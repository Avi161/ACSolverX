"""search_fast twin that adds an abelianization-Gram term to the heap score.

New file only — does not edit hfast/hcompact. Uses ``expand_and_score_nj`` for
children, then adds ``wA * feat`` to each child's score.

    score = (L + … shipped weights…) + wA · feat

feat modes (advisor REVISE):
  * ``norm`` — asym = |⟨ab(r1),ab(r2)⟩| / T ∈ [0,1]
  * ``raw``  — |⟨ab(r1),ab(r2)⟩| / L
  * ``mob``  — Mob/L² (BLOCKED candidate; negative-control only)
"""
from __future__ import annotations

import heapq
import os
import sys

import numpy as np

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.search.greedy_baseline import (  # noqa: E402
    str_to_arr, reduce_relator_nj, canonical_pair_nj,
)
from experiments.heuristic_search.core.hfast import (  # noqa: E402
    compile_config, expand_and_score_nj, _feats_nj, _pack, _SEP, _arrs,
)
from experiments.heuristic_search.core.hlab import N_FEAT  # noqa: E402
from experiments.heuristic_search.core.abel_gram_feats import (  # noqa: E402
    pair_asym_norm, pair_asym_raw, pair_mob_over_L2,
)


def _feat_fn(mode: str):
    if mode == "norm":
        return pair_asym_norm
    if mode == "raw":
        return pair_asym_raw
    if mode == "mob":
        return pair_mob_over_L2
    raise ValueError(f"unknown asym mode {mode!r}")


def search_asym(r1_str, r2_str, budget, cfg, mrl, wA=0.0,
                mode="norm", cyclic=True):
    """Like ``search_fast``, plus optional abelianization-Gram term ``wA * feat``.

    Returns dict with solved / nodes_explored / path_length / min_relator_length
    plus ``goal_hidden`` (min_L==2 and not solved — trivial discovered, never popped).
    """
    if cfg is None:
        cfg = {"segments": [{"upto": None, "w": {"L": 1.0}}]}
    feat = _feat_fn(mode)
    seg_upto, seg_w, seg_depth = compile_config(cfg)
    a1 = str_to_arr(r1_str)
    a2 = str_to_arr(r2_str)
    ca, cb = canonical_pair_nj(reduce_relator_nj(a1, cyclic),
                               reduce_relator_nj(a2, cyclic))
    key0 = _pack(ca, cb)

    f = np.empty(N_FEAT, dtype=np.float64)
    c0 = np.frombuffer(key0.replace(_SEP, b""), dtype=np.uint8)
    r_isx = np.empty(2 * mrl + 2, dtype=np.bool_)
    r_len = np.empty(2 * mrl + 2, dtype=np.int64)
    _feats_nj(c0, 0, len(ca), len(cb), r_isx, r_len, f)
    F0 = feat(c0, 0, len(ca), len(ca), len(cb))
    n_seg = len(seg_upto)
    p0 = None
    for s in range(n_seg):
        if f[0] <= seg_upto[s]:
            base = float(sum(seg_w[s, d] * f[d]
                             for d in range(N_FEAT) if seg_w[s, d] != 0.0))
            p0 = (s, base + float(wA) * float(F0))
            break
    if p0 is None:
        p0 = (n_seg, float(f[0]) + float(wA) * float(F0))

    pq = [(p0, 0, key0)]
    visited = {key0: None}
    min_total = len(ca) + len(cb)
    n_pop = 0
    solved = False
    path_len = 0

    while pq and n_pop < budget:
        prio, depth, key = heapq.heappop(pq)
        n_pop += 1
        i = key.index(0)
        la, lb = i, len(key) - i - 1
        if la == 1 and lb == 1:
            solved = True
            path_len = depth
            break
        ra, rb = _arrs(key)
        blob, offs, klens, seg_idx, score, tots, knots, moves, count = \
            expand_and_score_nj(ra, rb, mrl, cyclic, seg_upto, seg_w, 0)
        for c in range(count):
            o = int(offs[c])
            klen = int(klens[c])
            child = bytes(blob[o:o + klen])
            if child in visited:
                continue
            sep = child.index(0)
            n1, n2 = sep, klen - sep - 1
            codes = np.frombuffer(child[:sep] + child[sep + 1:], dtype=np.uint8)
            F = feat(codes, 0, n1, n1, n2)
            sc = float(score[c]) + float(wA) * float(F)
            sidx = int(seg_idx[c])
            visited[child] = key
            heapq.heappush(pq, ((sidx, sc), depth + 1, child))
            tot = int(tots[c])
            if tot < min_total:
                min_total = tot

    return {
        "solved": solved,
        "nodes_explored": n_pop,
        "path_length": path_len if solved else None,
        "min_relator_length": min_total,
        "goal_hidden": (not solved) and (min_total == 2),
        "wA": float(wA),
        "mode": mode,
    }
