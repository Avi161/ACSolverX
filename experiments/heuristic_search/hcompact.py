"""The tuned ordering on the compact packed arena — ``hsolve`` results at ~1/4 the memory.

``greedy_search_h(keep_path=False)`` costs a measured **24 kB per node popped** on the unsolved
124 at cap 48, which caps a 51 GB machine at ~2M nodes. Almost none of that is data: it is CPython
object overhead on the packed ``bytes`` keys, the visited-set entries, and the heap tuples — the
exact overhead ``greedy_compact`` already eliminated for the length ordering with a nibble arena,
an int32 binary heap and an open-addressing table at ~75 B/state. This module is that layout with
the heap comparison swapped for the tuned heuristic's.

WHY THE POP ORDER IS IDENTICAL TO ``greedy_search_h``
=====================================================
``hsolve`` pushes ``((seg, score), depth, key)`` into ``heapq``; every state is pushed exactly
once (dedup before push), so no two entries share a ``key`` and the comparison is a strict total
order — the pop sequence follows from the ordering relation alone, not from the heap
implementation (the same argument ``greedy_compact``'s docstring makes for the length ordering).
Three things must therefore be preserved, and each is preserved by construction:

1. **The scores are bit-identical floats.** Children are generated and scored by importing and
   calling the exact ``expand_and_score_nj`` kernel ``hsolve`` calls — same accumulation, same
   order, no ``fastmath`` anywhere in the chain — and the root is scored by the same Python
   expression ``hsolve`` uses for its root. IEEE doubles from identical operation sequences are
   equal bit for bit, so ``score[a] != score[b]`` resolves exactly where ``hsolve``'s does.
2. **The tie-break sorts like the key.** The comparator is seg, then score, then depth, then
   ``memcmp`` on the arena row. The row memcmp-sorts exactly like the packed key
   ``c1 + b'\\x00' + c2`` (``greedy_compact``'s invariant, pinned by its sort-corpus test), and
   the code tables agree: ``hfast._pack``'s ``(2, 4, 1, 3)`` is ``greedy_compact._code_of``.
3. **Discovery order is the enumeration order** of the same kernel, so ``depth`` and the
   first-seen min/max statistics land on the same states. ``hsolve`` updates min and max with two
   INDEPENDENT ``if``s on discovery (not the heavy solver's ``elif``) and max-expanded on pop
   before the solved test — mirrored here line for line.

``verify_hcompact.py`` checks all of this against ``greedy_search_h`` on every benchmark row and
a slice of the unsolved 124, all three shipped configs, budgets 500 and 1,000 — every scalar
field plus the first-seen min/max/expanded relator *strings*, which pin discovery order.

WHAT IT BUYS
============
Per state: row (cap 48 → 48 B) + len1/len2 (2) + depth (4) + heap (4) + score (8) + seg (1)
+ table (~8–16 amortised) ≈ **76–84 B**, reserved once at the projected count (lazily faulted,
never grow-copied unless exceeded — then loudly). Against ``hsolve``'s ~390 B/state that is the
difference between 10⁶ nodes needing ~24 GB and needing ~7 GB, i.e. between 2M being the ceiling
on a 51 GB machine and ~5M fitting. No path is tracked (the ``keep_path=False`` trade); recover a
certificate by re-running the one presentation that solved through ``greedy_search_h`` — the
search is deterministic, so the path is exact.

    from experiments.heuristic_search.hcompact import greedy_search_hcompact
    stats = greedy_search_hcompact(r1, r2, node_budget=3 * 10**6,
                                   max_relator_length=48, config=RECOMMENDED)
"""
import os
import sys

import numpy as np
from numba import njit

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.search.greedy_baseline import (                    # noqa: E402
    canonical_pair_nj, reduce_relator_nj, str_to_arr,
)
from experiments.search.greedy_compact import (                     # noqa: E402
    _CODE_TO_CHAR, _HB_CHECK_EVERY, _EMPTY, _NEED_CAPACITY, _OK, _SOLVED,
    _decode, _fnv, _get_nib, _init_state, _insert, _lookup, _next_pow2,
    _rehash, _row_less, _set_nib_at, est_states, _RESERVE_SLACK,
)
from experiments.heuristic_search.hfast import (                    # noqa: E402
    _SEP, _feats_nj, _pack, compile_config, expand_and_score_nj,
)
from experiments.heuristic_search.hlab import N_FEAT                # noqa: E402
from experiments.heuristic_search.hsolve import LENGTH_ONLY         # noqa: E402


# ---------------------------------------------------------------------------
# heap ordered by (seg, score, depth, row) — hsolve's ((seg, sc), nd, key)
# ---------------------------------------------------------------------------
@njit(inline='always')
def _less_h(arena, seg, score, depth, a, b, rw):
    if seg[a] != seg[b]:
        return seg[a] < seg[b]
    if score[a] != score[b]:
        return score[a] < score[b]
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    return _row_less(arena, a, b, rw)


@njit(inline='always')
def _sift_up_h(heap, i, arena, seg, score, depth, rw):
    v = heap[i]
    while i > 0:
        parent = (i - 1) >> 1
        if _less_h(arena, seg, score, depth, v, heap[parent], rw):
            heap[i] = heap[parent]
            i = parent
        else:
            break
    heap[i] = v


@njit(inline='always')
def _sift_down_h(heap, n, arena, seg, score, depth, rw):
    i = 0
    v = heap[0]
    while True:
        c = 2 * i + 1
        if c >= n:
            break
        if c + 1 < n and _less_h(arena, seg, score, depth, heap[c + 1], heap[c], rw):
            c += 1
        if _less_h(arena, seg, score, depth, heap[c], v, rw):
            heap[i] = heap[c]
            i = c
        else:
            break
    heap[i] = v


@njit(cache=True)
def _run_chunk_h(arena, len1, len2, depth, seg, score, heap, table, st,
                 cap, w, rw, cyclic, seg_upto, seg_w, seg_depth, use_depth,
                 max_pops, states_cap):
    """Advance by at most ``max_pops`` pops; all state lives in the arrays and ``st``.

    The skeleton is ``greedy_compact._run_chunk``; the two deliberate differences are the
    comparator (via the ``_h`` sifts) and the min/max update, which uses hsolve's two
    independent ``if``s rather than the heavy solver's ``elif``.
    """
    nodes = st[0]
    heap_len = st[1]
    n_disc = st[2]
    tmask = st[3]
    min_id, min_total = st[4], st[5]
    max_id, max_total = st[6], st[7]
    exp_id, exp_total = st[8], st[9]

    nb2 = 2 * w
    maxc = 4 * (cap + 1) * (cap + 1)
    pops = 0
    status = _OK

    while pops < max_pops:
        if heap_len == 0:
            status = _EMPTY
            break
        if (n_disc + maxc > states_cap
                or (n_disc + maxc) * 2 > table.size
                or heap_len + maxc > heap.size):
            status = _NEED_CAPACITY
            break

        top = heap[0]
        heap_len -= 1
        if heap_len > 0:
            heap[0] = heap[heap_len]
            _sift_down_h(heap, heap_len, arena, seg, score, depth, rw)
        nodes += 1
        pops += 1

        l1 = len1[top]
        l2 = len2[top]
        total = l1 + l2
        if total > exp_total:
            exp_total = total
            exp_id = top
        if l1 == 1 and l2 == 1:
            st[10] = np.int64(depth[top])
            status = _SOLVED
            break

        a1 = _decode(arena, top, 0, l1, rw)
        a2 = _decode(arena, top, nb2, l2, rw)
        blob, offs, klens, seg_idx, sc, tots, knots, moves, count = \
            expand_and_score_nj(a1, a2, cap, cyclic, seg_upto, seg_w, 0)

        d1 = depth[top] + 1
        for i in range(count):
            o = offs[i]
            kl = klens[i]
            la = 0
            for t in range(kl):
                if blob[o + t] == 0:
                    la = t
                    break
            lb = kl - la - 1

            off = n_disc * rw
            for t in range(rw):
                arena[off + t] = 0
            for t in range(la):
                _set_nib_at(arena, off, t, np.int64(blob[o + t]))
            for t in range(lb):
                _set_nib_at(arena, off, nb2 + t, np.int64(blob[o + la + 1 + t]))

            h = _fnv(arena, off, rw)
            if _lookup(table, tmask, arena, n_disc, rw, h) != -1:
                continue

            sid = n_disc
            len1[sid] = la
            len2[sid] = lb
            depth[sid] = d1
            si = seg_idx[i]
            s_val = sc[i]
            if use_depth:
                # Mirrors hsolve: sc += seg_depth[seg] * nd, at the same point.
                s_val = s_val + seg_depth[si] * d1
            seg[sid] = np.uint8(si)
            score[sid] = s_val
            _insert(table, tmask, h, sid)
            n_disc += 1

            nt = la + lb
            # Two INDEPENDENT ifs — hsolve's semantics, not the heavy solver's elif.
            if nt < min_total:
                min_total = nt
                min_id = sid
            if nt > max_total:
                max_total = nt
                max_id = sid

            heap[heap_len] = sid
            heap_len += 1
            _sift_up_h(heap, heap_len - 1, arena, seg, score, depth, rw)

    st[0] = nodes
    st[1] = heap_len
    st[2] = n_disc
    st[3] = tmask
    st[4], st[5] = min_id, min_total
    st[6], st[7] = max_id, max_total
    st[8], st[9] = exp_id, exp_total
    return status


class HCompactSolver:
    """Pops in exactly the order ``greedy_search_h`` does. Tracks no paths."""

    def __init__(self, r1, r2, max_nodes=10000, max_relator_length=24,
                 cyclic_reduce=True, config=None, reserve_states=None):
        if not 1 <= max_relator_length <= 255:
            raise ValueError(
                f"max_relator_length must be in 1..255, got {max_relator_length}")
        self.max_nodes = max_nodes
        self.cap = max_relator_length
        self.cyclic_reduce = cyclic_reduce
        self.w = (self.cap + 1) // 2
        self.rw = 2 * self.w
        self.grew = 0

        cfg = config or LENGTH_ONLY
        self.seg_upto, self.seg_w, self.seg_depth = compile_config(cfg)
        self.use_depth = bool(np.any(self.seg_depth != 0.0))
        self.n_seg = len(self.seg_upto)
        if self.n_seg >= 255:
            raise ValueError("seg is uint8; configs are 1-3 segments in practice")

        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(str_to_arr(r1), cyclic_reduce),
            reduce_relator_nj(str_to_arr(r2), cyclic_reduce),
        )

        want = reserve_states or est_states(max_nodes)
        n = max(1024, int(want * _RESERVE_SLACK)) + 4 * (self.cap + 1) ** 2
        self._alloc(n)

    def _alloc(self, n, old=None):
        self.states_cap = n
        self.arena = np.empty(n * self.rw, dtype=np.uint8)
        self.len1 = np.empty(n, dtype=np.uint8)
        self.len2 = np.empty(n, dtype=np.uint8)
        self.depth = np.empty(n, dtype=np.int32)
        self.seg = np.empty(n, dtype=np.uint8)
        self.score = np.empty(n, dtype=np.float64)
        self.heap = np.empty(n, dtype=np.int32)
        self.tcap = _next_pow2(2 * n)
        self.table = np.zeros(self.tcap, dtype=np.int32)
        if old is not None:
            k = old["n"]
            self.arena[:k * self.rw] = old["arena"][:k * self.rw]
            self.len1[:k] = old["len1"][:k]
            self.len2[:k] = old["len2"][:k]
            self.depth[:k] = old["depth"][:k]
            self.seg[:k] = old["seg"][:k]
            self.score[:k] = old["score"][:k]
            self.heap[:old["heap_len"]] = old["heap"][:old["heap_len"]]
            _rehash(self.table, self.tcap - 1, self.arena, k, self.rw)

    def _grow(self, st):
        self.grew += 1
        old = {"n": int(st[2]), "heap_len": int(st[1]), "arena": self.arena,
               "len1": self.len1, "len2": self.len2, "depth": self.depth,
               "seg": self.seg, "score": self.score, "heap": self.heap}
        print(f"    [hcompact] reservation exceeded at {old['n']:,} states; "
              f"growing to {2 * self.states_cap:,} (this copies)", flush=True)
        self._alloc(2 * self.states_cap, old)
        st[3] = self.tcap - 1

    def bytes_reserved(self):
        return (self.arena.nbytes + self.len1.nbytes + self.len2.nbytes
                + self.depth.nbytes + self.seg.nbytes + self.score.nbytes
                + self.heap.nbytes + self.table.nbytes)

    def bytes_per_state(self):
        return self.bytes_reserved() / self.states_cap

    def solve(self, progress=None):
        a1, a2 = self.initial_state
        _init_state(self.arena, self.len1, self.len2, self.depth, self.table,
                    self.tcap - 1, a1, a2, self.w, self.rw)
        init_total = int(self.len1[0]) + int(self.len2[0])

        # Root score: hsolve's exact Python expression (its p0 block), so the root's stored
        # (seg, score) is bit-identical too. It is popped first regardless (heap of one), but
        # a child can rediscover the root and dedup against it — the stored value must be the
        # one hsolve stored.
        key0 = _pack(a1, a2)
        scratch = np.empty(N_FEAT, dtype=np.float64)
        r_isx = np.empty(2 * self.cap + 2, dtype=np.bool_)
        r_len = np.empty(2 * self.cap + 2, dtype=np.int64)
        c0 = np.frombuffer(key0.replace(_SEP, b""), dtype=np.uint8)
        _feats_nj(c0, 0, len(a1), len(a2), r_isx, r_len, scratch)
        p0 = None
        for s in range(self.n_seg):
            if scratch[0] <= self.seg_upto[s]:
                p0 = (s, float(sum(self.seg_w[s, d] * scratch[d]
                                   for d in range(N_FEAT) if self.seg_w[s, d] != 0.0)))
                break
        if p0 is None:
            p0 = (self.n_seg, float(scratch[0]))
        self.seg[0] = p0[0]
        self.score[0] = p0[1]

        st = np.zeros(11, dtype=np.int64)
        st[10] = -1
        st[1] = 1
        st[2] = 1
        st[3] = self.tcap - 1
        st[5] = init_total
        st[7] = init_total
        st[9] = init_total
        self.heap[0] = 0

        solved = False
        next_tick = _HB_CHECK_EVERY
        while True:
            remaining = self.max_nodes - int(st[0])
            if remaining <= 0:
                break
            status = _run_chunk_h(
                self.arena, self.len1, self.len2, self.depth, self.seg,
                self.score, self.heap, self.table, st, self.cap, self.w,
                self.rw, self.cyclic_reduce, self.seg_upto, self.seg_w,
                self.seg_depth, self.use_depth,
                min(_HB_CHECK_EVERY, remaining), self.states_cap)

            if progress is not None and int(st[0]) >= next_tick:
                progress(int(st[0]))
                next_tick = (int(st[0]) // _HB_CHECK_EVERY + 1) * _HB_CHECK_EVERY

            if status == _SOLVED:
                solved = True
                break
            if status == _EMPTY:
                break
            if status == _NEED_CAPACITY:
                self._grow(st)

        self.n_discovered = int(st[2])
        self.min_id, self.min_total = int(st[4]), int(st[5])
        self.max_id, self.max_total = int(st[6]), int(st[7])
        self.max_expanded_id, self.max_expanded_total = int(st[8]), int(st[9])
        self.solved_depth = int(st[10]) if solved else None
        return solved, int(st[0])

    def relators(self, sid):
        off = sid * self.rw
        row = self.arena[off:off + self.rw]
        nb2 = 2 * self.w

        def word(base, n):
            return ''.join(_CODE_TO_CHAR[int(_get_nib(row, base + t))]
                           for t in range(n))
        return word(0, int(self.len1[sid])), word(nb2, int(self.len2[sid]))


def greedy_search_hcompact(r1_str, r2_str, node_budget, max_relator_length=24,
                           cyclic_reduce=True, config=None, progress=None,
                           reserve_states=None):
    """``greedy_search_h(keep_path=False)``'s exact dict, from the compact layout."""
    solver = HCompactSolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
        config=config,
        reserve_states=reserve_states,
    )
    solved, nodes_visited = solver.solve(progress)
    min_r = solver.relators(solver.min_id)
    max_r = solver.relators(solver.max_id)
    exp_r = solver.relators(solver.max_expanded_id)
    return {
        "solved": solved,
        "nodes_explored": nodes_visited,
        "path_length": solver.solved_depth,
        "min_relator_length": solver.min_total,
        "min_relator": [min_r[0], min_r[1]],
        "max_relator_length": solver.max_total,
        "max_relator": [max_r[0], max_r[1]],
        "max_relator_length_expanded": solver.max_expanded_total,
        "max_relator_expanded": [exp_r[0], exp_r[1]],
        "path": [],
        "path_moves": [],
    }
