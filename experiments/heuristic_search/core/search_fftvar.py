"""``search_signlag`` twin that takes any ``fftvar_feats`` variant as the spectral term.

Identical search to ``search_signlag`` — same expansion, same visited set, same heap discipline
— with ``wF * pair_sign_lag(...)`` generalised to ``wF * fvar_pair(..., variant, agg_max)``.
Setting ``variant="lag345", agg_max=False`` reproduces ``search_signlag`` exactly, which is the
control that makes every other arm interpretable.

    score = (segment weights over the 17 features) + wF * F_variant
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
from experiments.heuristic_search.core.fftvar_feats import (  # noqa: E402
    VIDX, fvar_pair,
)


def search_fftvar(r1_str, r2_str, budget, cfg, mrl, wF=0.0,
                  variant="lag345", agg_max=False, cyclic=True):
    """Greedy best-first with a spectral term added to the heap priority.

    Returns the same field names as ``greedy_search_hcompact`` / ``search_signlag`` so scout
    accounting is shared: solved / nodes_explored / path_length / min_relator_length.
    """
    if cfg is None:
        cfg = {"segments": [{"upto": None, "w": {"L": 1.0}}]}
    v = VIDX[variant] if isinstance(variant, str) else int(variant)
    seg_upto, seg_w, seg_depth = compile_config(cfg)
    a1 = str_to_arr(r1_str)
    a2 = str_to_arr(r2_str)
    ca, cb = canonical_pair_nj(reduce_relator_nj(a1, cyclic),
                               reduce_relator_nj(a2, cyclic))
    key0 = _pack(ca, cb)

    # scratch: power spectrum buffer, sized for the largest relator the cap allows
    pw = np.empty(2 * mrl + 4, dtype=np.float64)
    f = np.empty(N_FEAT, dtype=np.float64)
    c0 = np.frombuffer(key0.replace(_SEP, b""), dtype=np.uint8)
    r_isx = np.empty(2 * mrl + 2, dtype=np.bool_)
    r_len = np.empty(2 * mrl + 2, dtype=np.int64)
    _feats_nj(c0, 0, len(ca), len(cb), r_isx, r_len, f)
    F0 = fvar_pair(c0, 0, len(ca), len(ca), len(cb), v, agg_max, pw)

    n_seg = len(seg_upto)
    p0 = None
    for s in range(n_seg):
        if f[0] <= seg_upto[s]:
            base = float(sum(seg_w[s, d] * f[d]
                             for d in range(N_FEAT) if seg_w[s, d] != 0.0))
            p0 = (s, base + float(wF) * float(F0))
            break
    if p0 is None:
        p0 = (n_seg, float(f[0]) + float(wF) * float(F0))

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
            F = fvar_pair(codes, 0, n1, n1, n2, v, agg_max, pw)
            sc = float(score[c]) + float(wF) * float(F)
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
        "wF": float(wF),
        "variant": variant,
        "agg_max": bool(agg_max),
    }
