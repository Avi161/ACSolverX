"""Phase split of ``hcompact``'s per-pop cost by REPLAY, never by touching the engine.

The question this answers (the research memo's M0): of the ~hundreds of
microseconds one pop costs, how much is expansion arithmetic, how much is the
FNV hash chain, how much is the dependent table/arena probe, and how much is
the heap? Estimates from reading the code disagreed by 2x on this, and every
memory-side technique's expected gain scales with the answer.

METHOD
------
1. Record. A ``RecordingSolver`` runs the live engine's ``solve()`` unchanged
   except that ``_run_chunk_rec`` -- a verbatim copy of ``_run_chunk_h`` plus
   two stores per pop -- is swapped in for the module global while it runs.
   It writes ``popped[i]`` (the state id popped at pop ``i``) and
   ``nd_after[i]`` (``n_disc`` after pop ``i``'s children were processed).
   Because ids are assigned consecutively at discovery, ``[nd_after[i-1],
   nd_after[i])`` is exactly the set of states pop ``i`` pushed, in push order.
   The engine file is never edited; the two extra stores cost nothing
   measurable, and the recording run's final scalars are checked against a
   plain engine run at the same budget.

2. Replay, phase by phase, each in its own ``@njit`` kernel over batches of
   pops, timed with ``perf_counter`` around the kernel call (Python overhead is
   one call per batch of 64 pops, i.e. nil):

   (a) expand:  ``_decode_h`` + ``expand_and_score_nj`` over the popped
                sequence, exactly the engine's per-pop call.
   (b) hash:    ``_hash_codes`` over every candidate the expansion produced
                (candidates are materialised into a batch buffer first so
                this loop does nothing else).
   (c) probe:   ``_lookup_codes`` for every candidate against the FINAL
                table and arena, with the hash precomputed. Every candidate
                hits here (all were either found or inserted during the run),
                where in the live run the ~few percent that were new missed;
                the load factor is the run's final one. Both effects are
                reported alongside so the number can be read with them.
   (d) sift:    the heap replayed end to end -- pop/sift-down then push/
                sift-up for the recorded id ranges -- against the final
                score/seg/depth/arena. This is exact: those arrays are written
                once at discovery and never change, and the row order is
                width-invariant. The replay asserts ``heap[0] == popped[i]``
                at every pop, which is what proves the replay IS the run.
   (e) lascan:  the per-candidate zero-scan that finds ``la`` in the blob.
   (f) pack:    zero + pack a row (2 bits a symbol) for the candidates that were new.

   The residual is the plain engine's measured per-pop time minus the sum:
   ``_insert``, the min/max and heap bookkeeping, the pre-pop guards, the
   Python chunk loop, and -- importantly -- whatever out-of-order overlap the
   live loop enjoys between phases that isolation destroys (the residual can
   therefore be small or even negative; that is information, not error).

3. Diagnostics from the same replay, free: candidates per pop, mean symbol
   count per candidate, inserts per pop (the miss rate), the intra-pop
   duplicate fraction (a candidate resolving to an id inside this pop's own
   insert range but below the next-expected new id is a repeat of an earlier
   candidate of the same pop), mean probe length and mean rows compared per
   lookup. These are the memo's M2, M3, M5, M10.

USAGE
-----
    PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/phase_split.py \\
        --rows aca_0,aca_4,aca_5 --budget 50000 --reps 3 --cpu 2 --out /tmp/split.json
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

import numpy as np
from numba import njit

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
ROOT = _d
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from experiments.heuristic_search.core import hcompact as H            # noqa: E402
from experiments.heuristic_search.core.hcompact import (                # noqa: E402
    HCompactSolver, _hash_codes, _lookup_codes, _codes_equal_row,
    _sift_up_h, _sift_down_h, _NEED_WIDTH, greedy_search_hcompact,
    _decode_h, _set_sym2_at,
)
from experiments.search.greedy_compact import (                         # noqa: E402
    _OK, _SOLVED, _EMPTY, _NEED_CAPACITY, _insert, _slot0,
)
from experiments.heuristic_search.core.hfast import expand_and_score_nj  # noqa: E402
from experiments.heuristic_search.core.hlab import N_FEAT                # noqa: E402
from experiments.heuristic_search.core.perf_lab.bench import load_rows   # noqa: E402
from experiments.search.greedy_baseline import (                        # noqa: E402
    expand_node_topk_nj, inverse_relator_nj, reduce_relator_nj,
    canonical_relator_nj, lex_cmp_array, _ridx, _inv_at,
    _seam_reduced_len_nj, _reduce_into, _canon_into,
)


# ---------------------------------------------------------------------------
# 1. Recording: _run_chunk_h verbatim + two stores per pop.
# ---------------------------------------------------------------------------
@njit(cache=True)
def _run_chunk_rec(arena, len1, len2, depth, seg, score, heap, table, st,
                   cap, w, rw, cyclic, seg_upto, seg_w, seg_depth, use_depth,
                   max_pops, states_cap, parent, pmove, track, w_cap,
                   popped, nd_after):
    nodes = st[0]
    heap_len = st[1]
    n_disc = st[2]
    tmask = st[3]
    min_id, min_total = st[4], st[5]
    max_id, max_total = st[6], st[7]
    exp_id, exp_total = st[8], st[9]

    sym2 = 4 * w                 # symbol index where the r2 region starts
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
        if w < w_cap:
            nxt = heap[0]
            if np.int64(len1[nxt]) + np.int64(len2[nxt]) > sym2:
                status = _NEED_WIDTH
                break

        top = heap[0]
        heap_len -= 1
        if heap_len > 0:
            heap[0] = heap[heap_len]
            _sift_down_h(heap, heap_len, arena, len1, len2, seg, score, depth,
                         w, rw)
        nodes += 1
        pops += 1
        popped[nodes - 1] = top                       # <-- recording store 1

        l1 = len1[top]
        l2 = len2[top]
        total = l1 + l2
        if total > exp_total:
            exp_total = total
            exp_id = top
        if l1 == 1 and l2 == 1:
            st[10] = np.int64(depth[top])
            st[11] = np.int64(top)
            nd_after[nodes - 1] = n_disc              # <-- (solved: no children)
            status = _SOLVED
            break

        a1 = _decode_h(arena, top, 0, l1, rw)
        a2 = _decode_h(arena, top, sym2, l2, rw)
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

            h = _hash_codes(blob, o, la, lb)
            if _lookup_codes(table, tmask, arena, len1, len2, blob, o,
                             la, lb, sym2, rw, h) != -1:
                continue

            sid = n_disc
            off = sid * rw
            for t in range(rw):
                arena[off + t] = 0
            for t in range(la):
                _set_sym2_at(arena, off, t, np.int64(blob[o + t]))
            for t in range(lb):
                _set_sym2_at(arena, off, sym2 + t, np.int64(blob[o + la + 1 + t]))
            len1[sid] = la
            len2[sid] = lb
            depth[sid] = d1
            si = seg_idx[i]
            s_val = sc[i]
            if use_depth:
                s_val = s_val + seg_depth[si] * d1
            seg[sid] = np.uint8(si)
            score[sid] = s_val
            if track:
                parent[sid] = top
                for t in range(4):
                    pmove[sid, t] = np.int8(moves[i, t])
            _insert(table, tmask, h, sid)
            n_disc += 1

            nt = la + lb
            if nt < min_total:
                min_total = nt
                min_id = sid
            if nt > max_total:
                max_total = nt
                max_id = sid

            heap[heap_len] = sid
            heap_len += 1
            _sift_up_h(heap, heap_len - 1, arena, len1, len2, seg, score,
                       depth, w, rw)
        nd_after[nodes - 1] = n_disc                  # <-- recording store 2

    st[0] = nodes
    st[1] = heap_len
    st[2] = n_disc
    st[3] = tmask
    st[4], st[5] = min_id, min_total
    st[6], st[7] = max_id, max_total
    st[8], st[9] = exp_id, exp_total
    return status


class RecordingSolver(HCompactSolver):
    """The live engine's ``solve()``, with the recording chunk swapped in."""

    def solve(self, progress=None):
        self.popped = np.full(self.max_nodes, -1, dtype=np.int64)
        self.nd_after = np.full(self.max_nodes, -1, dtype=np.int64)
        popped, nd_after = self.popped, self.nd_after

        def chunk(*args):
            return _run_chunk_rec(*args, popped, nd_after)

        saved = H._run_chunk_h
        H._run_chunk_h = chunk
        try:
            return super().solve(progress)
        finally:
            H._run_chunk_h = saved


# ---------------------------------------------------------------------------
# 2. Replay kernels. Each does ONE phase over pops [i0, i1) or over the
#    candidates of one materialised batch.
# ---------------------------------------------------------------------------
@njit(cache=True)
def replay_expand(arena, len1, len2, popped, i0, i1, cap, cyclic, seg_upto,
                  seg_w, rw, sym2):
    tot = 0
    for i in range(i0, i1):
        top = popped[i]
        l1 = len1[top]
        l2 = len2[top]
        if l1 == 1 and l2 == 1:
            continue
        a1 = _decode_h(arena, top, 0, l1, rw)
        a2 = _decode_h(arena, top, sym2, l2, rw)
        blob, offs, klens, seg_idx, sc, tots, knots, moves, count = \
            expand_and_score_nj(a1, a2, cap, cyclic, seg_upto, seg_w, 0)
        tot += count
    return tot


@njit(cache=True)
def materialize(arena, len1, len2, popped, i0, i1, cap, cyclic, seg_upto,
                seg_w, rw, sym2, bblob, boffs, bkl, bpop):
    """Expand pops [i0, i1) and copy every candidate's key bytes back to back
    into ``bblob``; per candidate its offset, key length and pop index."""
    pos = 0
    nc = 0
    for i in range(i0, i1):
        top = popped[i]
        l1 = len1[top]
        l2 = len2[top]
        if l1 == 1 and l2 == 1:
            continue
        a1 = _decode_h(arena, top, 0, l1, rw)
        a2 = _decode_h(arena, top, sym2, l2, rw)
        blob, offs, klens, seg_idx, sc, tots, knots, moves, count = \
            expand_and_score_nj(a1, a2, cap, cyclic, seg_upto, seg_w, 0)
        for j in range(count):
            o = offs[j]
            kl = klens[j]
            for t in range(kl):
                bblob[pos + t] = blob[o + t]
            boffs[nc] = pos
            bkl[nc] = kl
            bpop[nc] = i
            pos += kl
            nc += 1
    return nc, pos


@njit(cache=True)
def replay_lascan(bblob, boffs, bkl, nc, bla, blb):
    acc = 0
    for j in range(nc):
        o = boffs[j]
        kl = bkl[j]
        la = 0
        for t in range(kl):
            if bblob[o + t] == 0:
                la = t
                break
        lb = kl - la - 1
        bla[j] = la
        blb[j] = lb
        acc += la
    return acc


@njit(cache=True)
def replay_hash(bblob, boffs, bla, blb, nc, bh):
    acc = np.uint64(0)
    for j in range(nc):
        h = _hash_codes(bblob, boffs[j], bla[j], blb[j])
        bh[j] = h
        acc ^= h
    return acc


@njit(cache=True)
def replay_probe(table, tmask, arena, len1, len2, bblob, boffs, bla, blb, bh,
                 nc, sym2, rw, bsid):
    acc = 0
    for j in range(nc):
        sid = _lookup_codes(table, tmask, arena, len1, len2, bblob, boffs[j],
                            bla[j], blb[j], sym2, rw, bh[j])
        bsid[j] = sid
        acc += sid
    return acc


@njit(cache=True)
def probe_stats(table, tmask, arena, len1, len2, bblob, boffs, bla, blb, bh,
                nc, sym2, rw):
    """Untimed: total slots visited and total row compares (length-matched
    slots) over the batch -- the memo's M2/M5 numbers, from the same lookups."""
    slots = 0
    rowcmp = 0
    for j in range(nc):
        i = _slot0(bh[j], tmask)
        la = bla[j]
        lb = blb[j]
        o = boffs[j]
        while True:
            slot = table[i]
            slots += 1
            if slot == 0:
                break
            s = slot - 1
            if np.int64(len1[s]) == la and np.int64(len2[s]) == lb:
                rowcmp += 1
            if _codes_equal_row(arena, s, len1, len2, bblob, o, la, lb, sym2, rw):
                break
            i += 1
            if i > tmask:
                i = 0
    return slots, rowcmp


@njit(cache=True)
def classify(bsid, bpop, nc, nd_after, i0):
    """Per candidate: 0 = global duplicate, 1 = new (first occurrence),
    2 = intra-pop duplicate. Uses the recorded id ranges only."""
    n_dup = 0
    n_new = 0
    n_intra = 0
    cur_pop = -1
    nd_before = 0
    next_new = 0
    for j in range(nc):
        p = bpop[j]
        if p != cur_pop:
            cur_pop = p
            nd_before = nd_after[p - 1] if p > 0 else 1
            next_new = nd_before
        s = bsid[j]
        if s < nd_before:
            n_dup += 1
        elif s == next_new:
            n_new += 1
            next_new += 1
        else:
            n_intra += 1
    return n_dup, n_new, n_intra


@njit(cache=True)
def replay_pack(bblob, boffs, bla, blb, bsid, bpop, nc, nd_after, sym2, rw,
                scratch):
    """Zero + pack a 2-bit row for each NEW candidate (as the engine does),
    into a scratch row. Same classification walk as ``classify``."""
    acc = 0
    cur_pop = -1
    nd_before = 0
    next_new = 0
    for j in range(nc):
        p = bpop[j]
        if p != cur_pop:
            cur_pop = p
            nd_before = nd_after[p - 1] if p > 0 else 1
            next_new = nd_before
        s = bsid[j]
        if s >= nd_before and s == next_new:
            next_new += 1
            o = boffs[j]
            la = bla[j]
            lb = blb[j]
            for t in range(rw):
                scratch[t] = 0
            for t in range(la):
                _set_sym2_at(scratch, 0, t, np.int64(bblob[o + t]))
            for t in range(lb):
                _set_sym2_at(scratch, 0, sym2 + t, np.int64(bblob[o + la + 1 + t]))
            acc += np.int64(scratch[0])
    return acc


@njit(cache=True)
def replay_heap(arena, len1, len2, seg, score, depth, w, rw, popped, nd_after,
                npop, heap):
    heap[0] = 0
    heap_len = 1
    n_disc = 1
    mism = 0
    for i in range(npop):
        top = heap[0]
        if top != popped[i]:
            mism += 1
        heap_len -= 1
        if heap_len > 0:
            heap[0] = heap[heap_len]
            _sift_down_h(heap, heap_len, arena, len1, len2, seg, score, depth,
                         w, rw)
        for sid in range(n_disc, nd_after[i]):
            heap[heap_len] = sid
            heap_len += 1
            _sift_up_h(heap, heap_len - 1, arena, len1, len2, seg, score,
                       depth, w, rw)
        n_disc = nd_after[i]
    return mism


@njit(cache=True)
def sum_lens(len1, len2, popped, npop):
    s = 0
    for i in range(npop):
        s += np.int64(len1[popped[i]]) + np.int64(len2[popped[i]])
    return s


# ---------------------------------------------------------------------------
# 2b. Sub-split INSIDE the expansion kernel (--sub).
#
# The same differencing method one level down. ``expand_and_score_nj`` is
# ``expand_node_topk_nj`` (pass 1: the seam test and the seam-reduced length
# for every (k1, k2); pass 2: raw word, reduce, canonicalise, order-normalise,
# encode) followed by the blob assembly and the feature/score loop. Each
# kernel below is that pipeline cut off after one more stage, its code copied
# verbatim from the live kernels (the helpers are imported, not rewritten),
# and consumes its last stage's output in a checksum so nothing is dead. Each
# is replayed over the recorded pops exactly like ``replay_expand``; the
# stage costs are the successive differences and their sum is, by
# construction, the full kernel's time (the last cut IS ``replay_expand``).
#
#   x_pass1  pass 1 only                                  -> (c) pass-1 filter
#   x_gen    + raw child word + free/cyclic reduce        -> (a) generate+reduce
#   x_canon  + canonical form (two Booth passes, inverse, -> (b) canonicalise
#              lex pick; the per-pop hoisted canonicals)
#   x_child  = expand_node_topk_nj: + order-normalise,    -> (b') normalise+encode
#              encode to codes, the output arrays
#   x_blob   + blob assembly (offs/klens/tots, key bytes) -> (e) blob
#   x_full   = expand_and_score_nj: + features, segment   -> (d) features+score
#              pick, weighted sum
#
# A caveat that is inherent to differencing: every cut is compiled on its
# own, so a stage's figure carries whatever LLVM does differently with the
# truncated pipeline (register pressure, inlining) -- read the stages as
# shares, not as microsecond-exact costs.
# ---------------------------------------------------------------------------
@njit(inline='always')
def _p1(r1, r2, cap, cyclic, c_len, c_tot, c_mv, inv1, inv2):
    """Pass 1 of ``expand_node_topk_nj``, verbatim, into caller scratch."""
    cnt = 0
    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
            rj_inv = inv2
        else:
            ri = r2
            rj = r1
            rj_inv = inv1
        len_i = len(ri)
        if len_i == 0:
            continue
        oth = reduce_relator_nj(rj, cyclic)
        len_oth = len(oth)
        if len_oth > cap:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else rj_inv
            jsign = 1 if idx == 0 else -1
            len_o = len(oj)
            if len_o == 0:
                continue
            for k1 in range(len_i):
                li = _ridx(k1, len_i - 1, len_i)
                for k2 in range(len_o):
                    if not _inv_at(ri, li, oj, _ridx(k2, 0, len_o)):
                        continue
                    m = _seam_reduced_len_nj(ri, k1, oj, k2, cyclic)
                    if m > cap:
                        continue
                    c_len[cnt] = m
                    c_tot[cnt] = m + len_oth
                    c_mv[cnt, 0] = target
                    c_mv[cnt, 1] = jsign
                    c_mv[cnt, 2] = k1
                    c_mv[cnt, 3] = k2
                    cnt += 1
    return cnt


@njit(cache=True)
def x_pass1(r1, r2, cap, cyclic):
    n1 = len(r1)
    n2 = len(r2)
    ub = 4 * (n1 + 1) * (n2 + 1)
    c_len = np.empty(ub, dtype=np.int64)
    c_tot = np.empty(ub, dtype=np.int64)
    c_mv = np.empty((ub, 4), dtype=np.int32)
    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)
    cnt = _p1(r1, r2, cap, cyclic, c_len, c_tot, c_mv, inv1, inv2)
    acc = 0
    for s in range(cnt):
        acc += c_len[s] + c_mv[s, 3]
    return cnt, acc


@njit(cache=True)
def x_gen(r1, r2, cap, cyclic):
    n1 = len(r1)
    n2 = len(r2)
    ub = 4 * (n1 + 1) * (n2 + 1)
    c_len = np.empty(ub, dtype=np.int64)
    c_tot = np.empty(ub, dtype=np.int64)
    c_mv = np.empty((ub, 4), dtype=np.int32)
    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)
    cnt = _p1(r1, r2, cap, cyclic, c_len, c_tot, c_mv, inv1, inv2)
    nn = n1 + n2
    pbuf = np.empty((nn, 2), dtype=np.bool_)
    rbuf = np.empty((nn, 2), dtype=np.bool_)
    acc = 0
    for s in range(cnt):
        target = c_mv[s, 0]
        k1 = c_mv[s, 2]
        k2 = c_mv[s, 3]
        if target == 1:
            ri = r1
            oj = r2 if c_mv[s, 1] == 1 else inv2
        else:
            ri = r2
            oj = r1 if c_mv[s, 1] == 1 else inv1
        ni = len(ri)
        no = len(oj)
        for t in range(ni):
            src = _ridx(k1, t, ni)
            pbuf[t, 0] = ri[src, 0]
            pbuf[t, 1] = ri[src, 1]
        for t in range(no):
            src = _ridx(k2, t, no)
            pbuf[ni + t, 0] = oj[src, 0]
            pbuf[ni + t, 1] = oj[src, 1]
        lo, m = _reduce_into(pbuf, ni + no, cyclic, rbuf)
        acc += m
        if m > 0:
            acc += rbuf[lo, 0]
    return cnt, acc


@njit(cache=True)
def x_canon(r1, r2, cap, cyclic):
    n1 = len(r1)
    n2 = len(r2)
    ub = 4 * (n1 + 1) * (n2 + 1)
    c_len = np.empty(ub, dtype=np.int64)
    c_tot = np.empty(ub, dtype=np.int64)
    c_mv = np.empty((ub, 4), dtype=np.int32)
    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)
    cnt = _p1(r1, r2, cap, cyclic, c_len, c_tot, c_mv, inv1, inv2)
    cro_t1 = canonical_relator_nj(reduce_relator_nj(r2, cyclic))
    cro_t2 = canonical_relator_nj(reduce_relator_nj(r1, cyclic))
    nn = n1 + n2
    pbuf = np.empty((nn, 2), dtype=np.bool_)
    rbuf = np.empty((nn, 2), dtype=np.bool_)
    ibuf = np.empty((nn, 2), dtype=np.bool_)
    cbuf1 = np.empty((nn, 2), dtype=np.bool_)
    cbuf2 = np.empty((nn, 2), dtype=np.bool_)
    fbuf = np.empty(2 * nn, dtype=np.int32)
    acc = len(cro_t1) + len(cro_t2)
    for s in range(cnt):
        target = c_mv[s, 0]
        k1 = c_mv[s, 2]
        k2 = c_mv[s, 3]
        if target == 1:
            ri = r1
            oj = r2 if c_mv[s, 1] == 1 else inv2
        else:
            ri = r2
            oj = r1 if c_mv[s, 1] == 1 else inv1
        ni = len(ri)
        no = len(oj)
        for t in range(ni):
            src = _ridx(k1, t, ni)
            pbuf[t, 0] = ri[src, 0]
            pbuf[t, 1] = ri[src, 1]
        for t in range(no):
            src = _ridx(k2, t, no)
            pbuf[ni + t, 0] = oj[src, 0]
            pbuf[ni + t, 1] = oj[src, 1]
        lo, m = _reduce_into(pbuf, ni + no, cyclic, rbuf)
        crp = _canon_into(rbuf[lo:lo + m], m, fbuf, ibuf, cbuf1, cbuf2)
        acc += len(crp)
        if m > 0:
            acc += crp[0, 1]
    return cnt, acc


@njit(cache=True)
def x_child(r1, r2, cap, cyclic):
    codes, lens, moves, count = expand_node_topk_nj(r1, r2, cap, cyclic, 1, 0)
    acc = 0
    for i in range(count):
        acc += lens[i, 0] + codes[i, 0]
    return count, acc


@njit(cache=True)
def x_blob(r1, r2, cap, cyclic, seg_upto, seg_w):
    """``expand_and_score_nj`` up to (not including) the feature loop."""
    codes, lens, moves, count = expand_node_topk_nj(r1, r2, cap, cyclic, 1, 0)
    offs = np.empty(count + 1, dtype=np.int64)
    klens = np.empty(count, dtype=np.int64)
    tots = np.empty(count, dtype=np.int64)
    knots = np.empty(count, dtype=np.int64)
    pos = 0
    for i in range(count):
        offs[i] = pos
        k = lens[i, 0] + lens[i, 1] + 1
        klens[i] = k
        tots[i] = lens[i, 0] + lens[i, 1]
        pos += k
    offs[count] = pos
    blob = np.empty(pos if pos > 0 else 1, dtype=np.uint8)
    for i in range(count):
        la = lens[i, 0]
        lb = lens[i, 1]
        o = offs[i]
        for t in range(la):
            blob[o + t] = codes[i, t]
        blob[o + la] = 0
        for t in range(lb):
            blob[o + la + 1 + t] = codes[i, la + t]
    n_seg = len(seg_upto)
    seg_idx = np.empty(count, dtype=np.int64)
    score = np.empty(count, dtype=np.float64)
    f = np.empty(N_FEAT, dtype=np.float64)
    r_isx = np.empty(2 * cap + 2, dtype=np.bool_)
    r_len = np.empty(2 * cap + 2, dtype=np.int64)
    acc = pos + n_seg + len(seg_idx) + len(score) + len(f) + len(r_isx) + len(r_len)
    for i in range(count):
        acc += blob[offs[i]] + tots[i]
    return count, acc


@njit(cache=True)
def x_full(r1, r2, cap, cyclic, seg_upto, seg_w):
    blob, offs, klens, seg_idx, sc, tots, knots, moves, count = \
        expand_and_score_nj(r1, r2, cap, cyclic, seg_upto, seg_w, 0)
    acc = 0
    for i in range(count):
        acc += seg_idx[i] + knots[i]
    return count, acc


@njit(cache=True)
def replay_sub(which, arena, len1, len2, popped, i0, i1, cap, cyclic,
               seg_upto, seg_w, rw, sym2):
    tot = 0
    acc = 0
    for i in range(i0, i1):
        top = popped[i]
        l1 = len1[top]
        l2 = len2[top]
        if l1 == 1 and l2 == 1:
            continue
        a1 = _decode_h(arena, top, 0, l1, rw)
        a2 = _decode_h(arena, top, sym2, l2, rw)
        if which == 0:
            c, a = x_pass1(a1, a2, cap, cyclic)
        elif which == 1:
            c, a = x_gen(a1, a2, cap, cyclic)
        elif which == 2:
            c, a = x_canon(a1, a2, cap, cyclic)
        elif which == 3:
            c, a = x_child(a1, a2, cap, cyclic)
        elif which == 4:
            c, a = x_blob(a1, a2, cap, cyclic, seg_upto, seg_w)
        else:
            c, a = x_full(a1, a2, cap, cyclic, seg_upto, seg_w)
        tot += c
        acc += a
    return tot, acc


@njit(cache=True)
def x_diag(r1, r2, cap, cyclic):
    """Untimed pass-1 counts for one pop: (k1, k2) pairs enumerated, pairs
    whose seam cancels (the seam-reduced length is computed for these),
    survivors of the cap filter, and survivors flagged by the cut-shift
    criterion (k1 >= 1 and the child's back seam cancels: A[0] inverse to
    B[-1] for A = roll(ri, k1), B = roll(oj, k2)) -- the exact intra-pop
    duplicate criterion candidate change 4 proposes."""
    n_pairs = 0
    n_seam = 0
    n_surv = 0
    n_crit = 0
    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)
    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
            rj_inv = inv2
        else:
            ri = r2
            rj = r1
            rj_inv = inv1
        len_i = len(ri)
        if len_i == 0:
            continue
        oth = reduce_relator_nj(rj, cyclic)
        if len(oth) > cap:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else rj_inv
            len_o = len(oj)
            if len_o == 0:
                continue
            n_pairs += len_i * len_o
            for k1 in range(len_i):
                li = _ridx(k1, len_i - 1, len_i)
                for k2 in range(len_o):
                    if not _inv_at(ri, li, oj, _ridx(k2, 0, len_o)):
                        continue
                    n_seam += 1
                    m = _seam_reduced_len_nj(ri, k1, oj, k2, cyclic)
                    if m > cap:
                        continue
                    n_surv += 1
                    if cyclic and k1 >= 1 and _inv_at(
                            ri, _ridx(k1, 0, len_i), oj, _ridx(k2, len_o - 1, len_o)):
                        n_crit += 1
    return n_pairs, n_seam, n_surv, n_crit


@njit(cache=True)
def x_crit_check(r1, r2, cap, cyclic):
    """Untimed empirical check of the cut-shift criterion on one pop: for
    every flagged child (k1, k2) the child of (k1 - 1, (k2 + 1) mod no) in
    the same (target, sign) block must exist EARLIER in generation order
    with identical (la, lb, codes). Returns (flagged, violations)."""
    codes, lens, moves, count = expand_node_topk_nj(r1, r2, cap, cyclic, 1, 0)
    n1 = len(r1)
    n2 = len(r2)
    flagged = 0
    bad = 0
    for i in range(count):
        target = moves[i, 0]
        js = moves[i, 1]
        k1 = moves[i, 2]
        k2 = moves[i, 3]
        ni = n1 if target == 1 else n2
        no = n2 if target == 1 else n1
        if not (cyclic and k1 >= 1):
            continue
        if target == 1:
            ri = r1
            oj = r2 if js == 1 else inverse_relator_nj(r2)
        else:
            ri = r2
            oj = r1 if js == 1 else inverse_relator_nj(r1)
        if not _inv_at(ri, _ridx(k1, 0, ni), oj, _ridx(k2, no - 1, no)):
            continue
        flagged += 1
        pk1 = k1 - 1
        pk2 = k2 + 1
        if pk2 >= no:
            pk2 -= no
        found = False
        j = i - 1
        while j >= 0:
            if (moves[j, 0] == target and moves[j, 1] == js
                    and moves[j, 2] == pk1 and moves[j, 3] == pk2):
                found = True
                break
            j -= 1
        if not found:
            bad += 1
            continue
        if lens[j, 0] != lens[i, 0] or lens[j, 1] != lens[i, 1]:
            bad += 1
            continue
        k = lens[i, 0] + lens[i, 1]
        for t in range(k):
            if codes[j, t] != codes[i, t]:
                bad += 1
                break
    return flagged, bad


@njit(cache=True)
def replay_diag(arena, len1, len2, popped, i0, i1, cap, cyclic, rw, sym2):
    n_pairs = 0
    n_seam = 0
    n_surv = 0
    n_crit = 0
    flagged = 0
    bad = 0
    for i in range(i0, i1):
        top = popped[i]
        l1 = len1[top]
        l2 = len2[top]
        if l1 == 1 and l2 == 1:
            continue
        a1 = _decode_h(arena, top, 0, l1, rw)
        a2 = _decode_h(arena, top, sym2, l2, rw)
        p, s, v, c = x_diag(a1, a2, cap, cyclic)
        n_pairs += p
        n_seam += s
        n_surv += v
        n_crit += c
        f, b = x_crit_check(a1, a2, cap, cyclic)
        flagged += f
        bad += b
    return n_pairs, n_seam, n_surv, n_crit, flagged, bad


SUB_CUTS = ("pass1", "gen", "canon", "child", "blob", "full")
SUB_STAGES = (
    ("pass1", "(c) pass-1 filter: seam test + seam-reduced length"),
    ("gen", "(a) raw child word + free/cyclic reduce"),
    ("canon", "(b) canonicalise: 2x Booth, inverse, lex pick"),
    ("encode", "(b') order-normalise + encode + output arrays"),
    ("blob", "(e) blob assembly (offs, klens, key bytes)"),
    ("feats", "(d) features + segment pick + weighted sum"),
)


def sub_split(arena, len1, len2, popped, npop, cap, cyclic, seg_upto, seg_w,
              rw, sym2, batch, reps):
    """Replay every cut over all pops; return per-cut medians (s) and the
    stage differences, plus the pass-1 diagnostics."""
    for which in range(len(SUB_CUTS)):
        replay_sub(which, arena, len1, len2, popped, 0, 1, cap, cyclic,
                   seg_upto, seg_w, rw, sym2)
    replay_diag(arena, len1, len2, popped, 0, 1, cap, cyclic, rw, sym2)

    cut_t = {c: [] for c in SUB_CUTS}
    cut_cnt = {}
    for rep in range(reps):
        for which, cname in enumerate(SUB_CUTS):
            t = 0.0
            tot = 0
            for i0 in range(0, npop, batch):
                i1 = min(npop, i0 + batch)
                a = time.perf_counter()
                c, _ = replay_sub(which, arena, len1, len2, popped, i0, i1,
                                  cap, cyclic, seg_upto, seg_w, rw, sym2)
                t += time.perf_counter() - a
                tot += c
            cut_t[cname].append(t)
            cut_cnt[cname] = tot
    # every cut must see the same candidate count: the pipeline is one
    assert len(set(cut_cnt.values())) == 1, cut_cnt

    d = {"n_pairs": 0, "n_seam": 0, "n_surv": 0, "n_crit": 0,
         "crit_flagged": 0, "crit_violations": 0}
    for i0 in range(0, npop, batch):
        i1 = min(npop, i0 + batch)
        p, s, v, c, f, b = replay_diag(arena, len1, len2, popped, i0, i1,
                                       cap, cyclic, rw, sym2)
        d["n_pairs"] += p
        d["n_seam"] += s
        d["n_surv"] += v
        d["n_crit"] += c
        d["crit_flagged"] += f
        d["crit_violations"] += b
    assert d["n_surv"] == cut_cnt["full"], (d["n_surv"], cut_cnt["full"])
    assert d["n_crit"] == d["crit_flagged"], (d["n_crit"], d["crit_flagged"])

    med = {c: statistics.median(cut_t[c]) for c in SUB_CUTS}
    stages = {
        "pass1": med["pass1"],
        "gen": med["gen"] - med["pass1"],
        "canon": med["canon"] - med["gen"],
        "encode": med["child"] - med["canon"],
        "blob": med["blob"] - med["child"],
        "feats": med["full"] - med["blob"],
    }
    return med, stages, d, cut_t


# ---------------------------------------------------------------------------
# 3. Driver
# ---------------------------------------------------------------------------
PHASES = ("expand", "lascan", "hash", "probe", "pack", "sift")


def split_one_row(name, r1, r2, budget, mrl, config, reps, batch, warm,
                  sub=False):
    from experiments.search.run_leftovers_1m import S20_MK2  # noqa: F401
    cfg = config

    # --- plain engine, timed: the total we split. Warm-up excludes compile.
    greedy_search_hcompact(r1, r2, warm, max_relator_length=mrl, config=cfg,
                           track_path=False)
    t0 = time.perf_counter()
    plain = greedy_search_hcompact(r1, r2, budget, max_relator_length=mrl,
                                   config=cfg, track_path=False)
    t_plain = time.perf_counter() - t0

    # --- recording run (warm-up first so its own compile is excluded too).
    rs = RecordingSolver(r1, r2, max_nodes=warm, max_relator_length=mrl,
                         config=cfg, track_path=False)
    rs.solve()
    rs = RecordingSolver(r1, r2, max_nodes=budget, max_relator_length=mrl,
                         config=cfg, track_path=False)
    t0 = time.perf_counter()
    solved, npop = rs.solve()
    t_rec = time.perf_counter() - t0
    assert npop == plain["nodes_explored"], (npop, plain["nodes_explored"])
    assert rs.min_total == plain["min_relator_length"]
    assert rs.max_total == plain["max_relator_length"]
    assert rs.max_expanded_total == plain["max_relator_length_expanded"]
    assert np.all(rs.popped[:npop] >= 0) and np.all(rs.nd_after[:npop] >= 0)

    arena, len1, len2 = rs.arena, rs.len1, rs.len2
    depth, seg, score, table = rs.depth, rs.seg, rs.score, rs.table
    rw, w, cap = rs.rw, rs.w, rs.cap
    sym2 = 4 * w                 # the r2 region's first symbol (4 a byte)
    tmask = rs.tcap - 1
    cyclic = rs.cyclic_reduce
    seg_upto, seg_w = rs.seg_upto, rs.seg_w
    popped, nd_after = rs.popped, rs.nd_after
    n_disc = rs.n_discovered

    maxc = 4 * (cap + 1) * (cap + 1)
    cb = batch * maxc                       # candidate bound per batch
    bblob = np.empty(cb * (2 * cap + 1), dtype=np.uint8)
    boffs = np.empty(cb, dtype=np.int64)
    bkl = np.empty(cb, dtype=np.int64)
    bpop = np.empty(cb, dtype=np.int64)
    bla = np.empty(cb, dtype=np.int64)
    blb = np.empty(cb, dtype=np.int64)
    bh = np.empty(cb, dtype=np.uint64)
    bsid = np.empty(cb, dtype=np.int64)
    scratch = np.zeros(rw, dtype=np.uint8)
    heap = np.empty(rs.heap.size, dtype=np.int32)

    # compile every replay kernel on a tiny batch before timing anything
    materialize(arena, len1, len2, popped, 0, 1, cap, cyclic, seg_upto, seg_w,
                rw, sym2, bblob, boffs, bkl, bpop)
    replay_expand(arena, len1, len2, popped, 0, 1, cap, cyclic, seg_upto,
                  seg_w, rw, sym2)
    nc0, _ = materialize(arena, len1, len2, popped, 0, 1, cap, cyclic,
                         seg_upto, seg_w, rw, sym2, bblob, boffs, bkl, bpop)
    replay_lascan(bblob, boffs, bkl, nc0, bla, blb)
    replay_hash(bblob, boffs, bla, blb, nc0, bh)
    replay_probe(table, tmask, arena, len1, len2, bblob, boffs, bla, blb, bh,
                 nc0, sym2, rw, bsid)
    probe_stats(table, tmask, arena, len1, len2, bblob, boffs, bla, blb, bh,
                nc0, sym2, rw)
    classify(bsid, bpop, nc0, nd_after, 0)
    replay_pack(bblob, boffs, bla, blb, bsid, bpop, nc0, nd_after, sym2, rw,
                scratch)
    replay_heap(arena, len1, len2, seg, score, depth, w, rw, popped, nd_after,
                1, heap)

    times = {p: [] for p in PHASES}
    diag = None
    for rep in range(reps):
        t = {p: 0.0 for p in PHASES}
        n_cand = 0
        n_sym = 0
        n_dup = n_new = n_intra = 0
        slots = rowcmp = 0
        for i0 in range(0, npop, batch):
            i1 = min(npop, i0 + batch)
            a = time.perf_counter()
            replay_expand(arena, len1, len2, popped, i0, i1, cap, cyclic,
                          seg_upto, seg_w, rw, sym2)
            t["expand"] += time.perf_counter() - a

            nc, pos = materialize(arena, len1, len2, popped, i0, i1, cap,
                                  cyclic, seg_upto, seg_w, rw, sym2, bblob,
                                  boffs, bkl, bpop)
            n_cand += nc
            n_sym += pos - nc                 # key bytes minus separators

            a = time.perf_counter()
            replay_lascan(bblob, boffs, bkl, nc, bla, blb)
            t["lascan"] += time.perf_counter() - a

            a = time.perf_counter()
            replay_hash(bblob, boffs, bla, blb, nc, bh)
            t["hash"] += time.perf_counter() - a

            a = time.perf_counter()
            replay_probe(table, tmask, arena, len1, len2, bblob, boffs, bla,
                         blb, bh, nc, sym2, rw, bsid)
            t["probe"] += time.perf_counter() - a

            a = time.perf_counter()
            replay_pack(bblob, boffs, bla, blb, bsid, bpop, nc, nd_after, sym2,
                        rw, scratch)
            t["pack"] += time.perf_counter() - a

            if rep == 0:
                d, nw, ni = classify(bsid, bpop, nc, nd_after, i0)
                n_dup += d
                n_new += nw
                n_intra += ni
                s_, r_ = probe_stats(table, tmask, arena, len1, len2, bblob,
                                     boffs, bla, blb, bh, nc, sym2, rw)
                slots += s_
                rowcmp += r_

        a = time.perf_counter()
        mism = replay_heap(arena, len1, len2, seg, score, depth, w, rw, popped,
                           nd_after, npop, heap)
        t["sift"] += time.perf_counter() - a
        assert mism == 0, f"heap replay diverged from the run at {mism} pops"

        for p in PHASES:
            times[p].append(t[p])
        if rep == 0:
            assert n_new == n_disc - 1, (n_new, n_disc)
            diag = {
                "n_cand": n_cand, "n_sym": n_sym, "n_dup": n_dup,
                "n_new": n_new, "n_intra": n_intra,
                "probe_slots": slots, "probe_rowcmp": rowcmp,
            }

    sub_res = None
    if sub:
        t0 = time.perf_counter()
        smed, stages, sdiag, sraw = sub_split(
            arena, len1, len2, popped, npop, cap, cyclic, seg_upto, seg_w, rw,
            sym2, batch, reps)
        t_sub = time.perf_counter() - t0
        sub_res = {
            "cut_us_per_pop": {c: 1e6 * smed[c] / npop for c in SUB_CUTS},
            "stage_us_per_pop": {k: 1e6 * v / npop for k, v in stages.items()},
            "diag": sdiag,
            "pairs_per_pop": sdiag["n_pairs"] / npop,
            "seam_per_pop": sdiag["n_seam"] / npop,
            "surv_per_pop": sdiag["n_surv"] / npop,
            "crit_per_pop": sdiag["n_crit"] / npop,
            "crit_frac_of_cand": sdiag["n_crit"] / max(1, sdiag["n_surv"]),
            "crit_violations": sdiag["crit_violations"],
            "t_sub_s": t_sub,
            "raw_times_s": sraw,
        }

    med = {p: statistics.median(times[p]) for p in PHASES}
    tot = t_plain
    us = {p: 1e6 * med[p] / npop for p in PHASES}
    us_total = 1e6 * tot / npop
    us_sum = sum(us.values())
    out = {
        "row": name, "budget": budget, "npop": int(npop), "solved": bool(solved),
        "n_discovered": int(n_disc), "rw": int(rw), "w": int(w),
        "tcap": int(rs.tcap), "load_factor": n_disc / rs.tcap,
        "widened": rs.widened, "grew": rs.grew,
        "t_plain_s": t_plain, "t_record_s": t_rec,
        "us_per_pop_total": us_total,
        "us_per_pop": us,
        "us_per_pop_sum": us_sum,
        "us_per_pop_residual": us_total - us_sum,
        "share": {p: us[p] / us_total for p in PHASES},
        "share_residual": (us_total - us_sum) / us_total,
        "cand_per_pop": diag["n_cand"] / npop,
        "sym_per_cand": diag["n_sym"] / max(1, diag["n_cand"]),
        "popped_total_mean": sum_lens(len1, len2, popped, npop) / npop,
        "inserts_per_pop": diag["n_new"] / npop,
        "miss_rate": diag["n_new"] / max(1, diag["n_cand"]),
        "intra_pop_dup_frac": diag["n_intra"] / max(1, diag["n_cand"]),
        "global_dup_frac": diag["n_dup"] / max(1, diag["n_cand"]),
        "probe_slots_per_lookup": diag["probe_slots"] / max(1, diag["n_cand"]),
        "probe_rowcmp_per_lookup": diag["probe_rowcmp"] / max(1, diag["n_cand"]),
        "reps": reps, "raw_times_s": times,
        "sub": sub_res,
    }
    return out


def fmt_table(results):
    lines = []
    hdr = f"{'phase':10s}" + "".join(f"{r['row']:>18s}" for r in results)
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for p in PHASES + ("residual",):
        cells = []
        for r in results:
            if p == "residual":
                u, s = r["us_per_pop_residual"], r["share_residual"]
            else:
                u, s = r["us_per_pop"][p], r["share"][p]
            cells.append(f"{u:9.1f} us {100*s:5.1f}%")
        lines.append(f"{p:10s}" + "".join(f"{c:>18s}" for c in cells))
    lines.append(f"{'total':10s}" + "".join(
        f"{r['us_per_pop_total']:9.1f} us 100.0%".rjust(18) for r in results))
    lines.append("")
    for k, label in (
            ("npop", "pops"), ("n_discovered", "states discovered"),
            ("cand_per_pop", "candidates / pop"), ("sym_per_cand", "symbols / candidate"),
            ("popped_total_mean", "mean |r1|+|r2| popped"),
            ("inserts_per_pop", "inserts / pop"), ("miss_rate", "miss rate (new / cand)"),
            ("intra_pop_dup_frac", "intra-pop dup fraction"),
            ("probe_slots_per_lookup", "slots / lookup (final table)"),
            ("probe_rowcmp_per_lookup", "row compares / lookup"),
            ("load_factor", "final load factor"), ("rw", "row bytes"),
            ("widened", "widens"), ("grew", "grows")):
        cells = []
        for r in results:
            v = r[k]
            cells.append(f"{v:.3f}" if isinstance(v, float) else f"{v}")
        lines.append(f"{label:30s}" + "".join(f"{c:>18s}" for c in cells))
    return "\n".join(lines)


def fmt_sub_table(results):
    lines = []
    rs = [r for r in results if r.get("sub")]
    if not rs:
        return ""
    hdr = f"{'expand stage':52s}" + "".join(f"{r['row']:>24s}" for r in rs)
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for key, label in SUB_STAGES:
        cells = []
        for r in rs:
            u = r["sub"]["stage_us_per_pop"][key]
            ex = r["us_per_pop"]["expand"]
            tot = r["us_per_pop_total"]
            cells.append(f"{u:8.1f} us {100*u/ex:5.1f}%e {100*u/tot:5.1f}%p")
        lines.append(f"{label:52s}" + "".join(f"{c:>24s}" for c in cells))
    cells = []
    for r in rs:
        u = r["sub"]["cut_us_per_pop"]["full"]
        ex = r["us_per_pop"]["expand"]
        tot = r["us_per_pop_total"]
        cells.append(f"{u:8.1f} us {100*u/ex:5.1f}%e {100*u/tot:5.1f}%p")
    lines.append(f"{'sum = full kernel (x_full cut)':52s}"
                 + "".join(f"{c:>24s}" for c in cells))
    cells = []
    for r in rs:
        u = r["us_per_pop"]["expand"]
        tot = r["us_per_pop_total"]
        cells.append(f"{u:8.1f} us {100.0:5.1f}%e {100*u/tot:5.1f}%p")
    lines.append(f"{'expand phase (replay_expand, outer split)':52s}"
                 + "".join(f"{c:>24s}" for c in cells))
    lines.append("")
    lines.append("(%e = share of the expand phase, %p = share of the pop)")
    lines.append("")
    for k, label in (
            ("pairs_per_pop", "(k1, k2) pairs enumerated / pop"),
            ("seam_per_pop", "seam-matching pairs / pop (before cap filter)"),
            ("surv_per_pop", "candidates after pass 1 / pop"),
            ("crit_per_pop", "cut-shift-flagged candidates / pop"),
            ("crit_frac_of_cand", "cut-shift-flagged fraction of candidates"),
            ("crit_violations", "cut-shift criterion violations (must be 0)"),
            ("t_sub_s", "sub-split wall (s)")):
        cells = []
        for r in rs:
            v = r["sub"][k]
            cells.append(f"{v:.3f}" if isinstance(v, float) else f"{v}")
        lines.append(f"{label:52s}" + "".join(f"{c:>24s}" for c in cells))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", default="aca_0,aca_4,aca_5")
    ap.add_argument("--budget", type=int, default=50_000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--batch", type=int, default=64, help="pops per replay batch")
    ap.add_argument("--mrl", type=int, default=64)
    ap.add_argument("--cpu", type=int, default=2)
    ap.add_argument("--warm", type=int, default=2000)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sub", action="store_true",
                    help="also split the expansion kernel into its stages")
    args = ap.parse_args(argv)

    try:
        os.sched_setaffinity(0, {args.cpu})
    except (AttributeError, OSError) as e:
        print(f"WARN: could not pin to cpu {args.cpu}: {e}", file=sys.stderr)

    from experiments.search.run_leftovers_1m import S20_MK2
    rows = load_rows([s.strip() for s in args.rows.split(",") if s.strip()])
    results = []
    for name, r1, r2 in rows:
        t0 = time.time()
        res = split_one_row(name, r1, r2, args.budget, args.mrl, S20_MK2,
                            args.reps, args.batch, args.warm, sub=args.sub)
        results.append(res)
        print(f"[{name}] done in {time.time() - t0:.0f}s: total "
              f"{res['us_per_pop_total']:.1f} us/pop, sum of phases "
              f"{res['us_per_pop_sum']:.1f}, residual {res['us_per_pop_residual']:.1f}",
              flush=True)
    print()
    print(fmt_table(results))
    if args.sub:
        print()
        print(fmt_sub_table(results))
    if args.out:
        with open(args.out, "w") as f:
            json.dump({"args": vars(args), "results": results}, f, indent=1)
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
