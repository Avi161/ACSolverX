"""A drop-in ``greedy_search`` that orders by the tuned heuristic instead of by length.

The research harness (``hfast.search_fast``) proves the ordering works but returns only what an
experiment needs -- solved, nodes, path length, a couple of progress numbers. The production
pipeline (``run_baseline.py`` -> ``greedy_search``) needs more: the certificate path as Definition
2.1 moves, the shortest and longest presentations seen, the longest one actually expanded. Without
those a solve cannot be written to a results row, cannot be verified by ``verify_results.py``, and
cannot be resumed.

So this module exposes ``greedy_search_h``, which returns **exactly** the dict
``greedy_baseline.greedy_search`` returns, key for key, and takes one extra argument: the ordering
config. With ``config=None`` it orders by total length and is the baseline; with the tuned config
it is the heuristic. Nothing else about the search changes -- same move generator, same reduction,
same canonicalisation, same cap test, same ``(priority, depth, key)`` heap shape.

Two things this deliberately does not do. It does not modify ``greedy_baseline.py``, which is
read-only in this repo; it imports from it. And it does not recover the path by diffing consecutive
states -- a Definition 2.1 move inverts the *other* relator, so a diff misreads it, and the repo
has a lesson to that effect. The moves come out of the expansion kernel that generated them.

    from experiments.heuristic_search.hsolve import greedy_search_h, RECOMMENDED
    stats = greedy_search_h(r1, r2, node_budget=10**6, max_relator_length=48,
                            config=RECOMMENDED)
"""
import heapq
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.search.greedy_baseline import (                    # noqa: E402
    canonical_pair_nj, move_to_str, reduce_relator_nj, str_to_arr,
)
from experiments.heuristic_search.hfast import (                    # noqa: E402
    _CODE_TO_CHAR, _SEP, _arrs, _feats_nj, _pack, compile_config, expand_and_score_nj,
)
from experiments.heuristic_search.hlab import N_FEAT                # noqa: E402

# The ordering this program recommends for a large run: a single weight vector, no phases.
# EXP-18 showed the endgame threshold is inert for a climb that already carries ``S`` and ``MK``;
# EXP-16 and EXP-06 independently showed this is the one still converting budget into solves at
# the top of the measurable range.
RECOMMENDED = {"segments": [
    {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]}

# The lean alternative, for small budgets (~500 nodes). Needs its endgame boundary: with only a
# knot term it would otherwise keep chasing knots where nothing structural is left to buy.
LEAN_SMALL_BUDGET = {"segments": [
    {"upto": 16, "w": {"L": 1.0}},
    {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]}

LENGTH_ONLY = {"segments": [{"upto": None, "w": {"L": 1.0}}]}


def _unpack(key):
    i = key.index(0)
    return (''.join(_CODE_TO_CHAR[c] for c in key[:i]),
            ''.join(_CODE_TO_CHAR[c] for c in key[i + 1:]))


def greedy_search_h(r1_str, r2_str, node_budget, max_relator_length=24,
                    cyclic_reduce=True, config=None, progress=None, keep_path=True):
    """``greedy_baseline.greedy_search`` with the heap ordering swapped. Same return dict.

    ``config=None`` means order by total length, which reproduces the baseline search.

    ``keep_path=False`` stores a visited **set** instead of the parent map, which is the same trade
    ``greedy_baseline``'s ``high_speedup`` mode makes: no certificate comes back (``path`` and
    ``path_moves`` are empty, ``path_length`` is still correct because depth is carried on the heap),
    and in exchange the search fits a much larger budget in the same RAM.

    Measured on the 124 unsolved classes at cap 48, where nothing solves so the full budget is
    consumed and state growth is worst-case: **36.5 kB per node with the path, 24 kB without**
    (1.53x), with the discovered-state count, pop count and solve outcome **identical** either way.
    That is the difference between a 10^6-node run needing 36.5 GB and needing 24 GB -- i.e. between
    not fitting and fitting on a 51 GB machine. Recover a certificate by re-running the one
    presentation that solved, with ``keep_path=True``; the search is deterministic, so the path is
    exact.
    """
    cfg = config or LENGTH_ONLY
    seg_upto, seg_w, seg_depth = compile_config(cfg)
    use_depth = bool(np.any(seg_depth != 0.0))
    n_seg = len(seg_upto)
    cap = max_relator_length

    a1 = str_to_arr(r1_str)
    a2 = str_to_arr(r2_str)
    ca, cb = canonical_pair_nj(reduce_relator_nj(a1, cyclic_reduce),
                               reduce_relator_nj(a2, cyclic_reduce))
    key0 = _pack(ca, cb)

    scratch = np.empty(N_FEAT, dtype=np.float64)
    r_isx = np.empty(2 * cap + 2, dtype=np.bool_)
    r_len = np.empty(2 * cap + 2, dtype=np.int64)
    c0 = np.frombuffer(key0.replace(_SEP, b""), dtype=np.uint8)
    _feats_nj(c0, 0, len(ca), len(cb), r_isx, r_len, scratch)
    p0 = None
    for s in range(n_seg):
        if scratch[0] <= seg_upto[s]:
            p0 = (s, float(sum(seg_w[s, d] * scratch[d]
                               for d in range(N_FEAT) if seg_w[s, d] != 0.0)))
            break
    if p0 is None:
        p0 = (n_seg, float(scratch[0]))

    pq = [(p0, 0, key0)]
    # One container or the other, never both: the dict is what costs the memory.
    parent = {key0: None} if keep_path else None   # key -> (parent_key, move), root -> None
    seen = None if keep_path else {key0}
    nodes = 0
    t0 = len(ca) + len(cb)
    min_key, min_tot = key0, t0    # shortest presentation DISCOVERED
    max_key, max_tot = key0, t0    # longest presentation DISCOVERED
    exp_key, exp_tot = key0, t0    # longest presentation actually POPPED

    while pq and nodes < node_budget:
        _, depth, key = heapq.heappop(pq)
        nodes += 1
        i = key.index(0)
        l1, l2 = i, len(key) - i - 1
        if l1 + l2 > exp_tot:
            exp_key, exp_tot = key, l1 + l2

        if l1 == 1 and l2 == 1:
            if not keep_path:
                # `depth` rides on the heap entry, so the path LENGTH survives even though the
                # path itself was never stored.
                return _stats(True, nodes, [], [], min_key, min_tot,
                              max_key, max_tot, exp_key, exp_tot, path_length=depth)
            states, moves = [], []
            k = key
            while k is not None:
                states.append(_unpack(k))
                pv = parent[k]
                if pv is None:
                    break
                k, mv = pv
                moves.append(mv)
            states.reverse()
            moves.reverse()
            return _stats(True, nodes, states, moves, min_key, min_tot,
                          max_key, max_tot, exp_key, exp_tot)

        p1, p2 = _arrs(key)
        blob, offs, klens, seg_idx, score, tots, knots, mvs, count = expand_and_score_nj(
            p1, p2, cap, cyclic_reduce, seg_upto, seg_w)
        if count == 0:
            continue
        raw = blob.tobytes()
        nd = depth + 1
        for c in range(count):
            o = int(offs[c])
            k = raw[o:o + int(klens[c])]
            if (k not in parent) if keep_path else (k not in seen):
                if keep_path:
                    parent[k] = (key, (int(mvs[c, 0]), int(mvs[c, 1]),
                                       int(mvs[c, 2]), int(mvs[c, 3])))
                else:
                    seen.add(k)
                t = int(tots[c])
                if t < min_tot:
                    min_key, min_tot = k, t
                if t > max_tot:
                    max_key, max_tot = k, t
                sc = float(score[c])
                if use_depth:
                    sc += seg_depth[int(seg_idx[c])] * nd
                heapq.heappush(pq, ((int(seg_idx[c]), sc), nd, k))
        if progress is not None:
            progress(nodes)

    return _stats(False, nodes, [], [], min_key, min_tot, max_key, max_tot, exp_key, exp_tot)


def _stats(solved, nodes, states, moves, min_key, min_tot, max_key, max_tot, exp_key, exp_tot,
           path_length=None):
    """Exactly ``greedy_search``'s dict -- same keys, same order, same types.

    Pinned against the real thing in ``tests/heuristic_search/test_hsolve.py``: a caller that
    switches orderings must not have to touch anything downstream, and a missing key would only
    surface when a results row was written, i.e. hours into a Colab run.
    """
    mn, mx, ex = _unpack(min_key), _unpack(max_key), _unpack(exp_key)
    return {
        "solved": solved,
        "nodes_explored": nodes,
        "path_length": (path_length if path_length is not None
                        else ((len(states) - 1) if solved else None)),
        "min_relator_length": min_tot,
        "min_relator": [mn[0], mn[1]],
        "max_relator_length": max_tot,
        "max_relator": [mx[0], mx[1]],
        "max_relator_length_expanded": exp_tot,
        "max_relator_expanded": [ex[0], ex[1]],
        "path": [[a, b] for a, b in states] if solved else [],
        "path_moves": [move_to_str(m) for m in moves] if solved else [],
    }
