"""The same search as ``hlab.LabSolver``, with the per-child work moved inside numba.

``LabSolver`` calls four ``@njit`` functions per candidate child from a Python loop. That is fine
while the ordering keeps relators short -- the baseline pops states of total length ~18 and
generates a few hundred candidates -- but a *structural* ordering deliberately tolerates long
states, and the candidate count is ``4*(|r1|+1)*(|r2|+1)``. At cap 48 that is ~9,600 candidates,
each crossing the Python/numba boundary four times: ~38,000 crossings per pop, ~58 ms, ~29 s for a
single 500-node search. Measured across the EXP-02 sweep the average was 21 s/presentation, and
the whole cost was boundary crossings rather than arithmetic.

So this module makes **one** numba call per pop. ``expand_and_score_nj`` expands, reduces,
canonicalises, encodes each child's packed key, computes all thirteen features and evaluates the
segmented weight vector -- returning flat arrays. Python is left with a dict lookup and a heap
push per child, and only *new* children cost more than that.

Nothing about the search changes. The kernel calls ``expand_node_topk_nj(..., topk=0)``, which the
repo already pins as bit-identical to ``expand_node_nj``, in the same enumeration order (target ->
jsign -> k1 -> k2) that the heap's ``depth`` tie-break depends on. Keys are ``pack_key`` bytes,
which sort identically to the ``(r1_str, r2_str)`` tuples ``LabSolver`` uses.

**The gate is not the baseline config.** Ordering by length never lets a relator grow, so it never
enters the regime where these two implementations could differ -- a baseline-only check would be
vacuous for exactly this change. The gate is agreement with ``LabSolver`` on the *runaway*
configs, verified against the rows EXP-02 already computed with the slow solver
(``verify_fast.py``).
"""
import heapq
import os
import sys

import numpy as np
from numba import njit

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))

from experiments.search.greedy_baseline import (                    # noqa: E402
    expand_node_topk_nj, str_to_arr, reduce_relator_nj, canonical_pair_nj,
)
from experiments.heuristic_search.hlab import (                     # noqa: E402
    FEATURES, N_FEAT, _FIDX, INF,
)

_SEP = b"\x00"
_CODE_TO_CHAR = {1: 'X', 2: 'Y', 3: 'x', 4: 'y'}
_BIG = 1 << 30


@njit(inline='always')
def _runs_nj(codes, off, n, r_isx, r_len):
    """Cyclic block decomposition of one relator. Returns the run count after closing the seam.

    A run that wraps the ring is counted once at each end by a linear scan, so the first and last
    runs merge when they carry the same generator -- exactly ``word_stats``' seam close. A pure
    power produces a single run and is left alone, which is what makes its knot count zero.

    Generator bit: codes are X=1, Y=2, x=3, y=4, so ``c & 1`` is 1 for both x-letters and 0 for
    both y-letters. The sign is irrelevant to block structure and must not enter it.
    """
    if n == 0:
        return 0
    nr = 0
    i = 0
    while i < n:
        gi = (codes[off + i] & 1) == 1
        j = i
        while j + 1 < n and (((codes[off + j + 1] & 1) == 1) == gi):
            j += 1
        r_isx[nr] = gi
        r_len[nr] = j - i + 1
        nr += 1
        i = j + 1
    if nr > 1 and r_isx[0] == r_isx[nr - 1]:
        r_len[0] += r_len[nr - 1]
        nr -= 1
    return nr


@njit(cache=True)
def _feats_nj(codes, off, la, lb, r_isx, r_len, out):
    """The thirteen features of one child, written into ``out`` in ``FEATURES`` order.

    Mirrors ``hlab.phi`` term for term, including the two places it is easy to get subtly wrong:
    a pure-power relator has zero knots (one generator is simply absent, so ``max`` over the block
    counts would be a lie), and when one generator is absent from the *pair* the smaller and
    larger mean block collapse to the same value rather than one of them being zero.
    """
    nr1 = _runs_nj(codes, off, la, r_isx, r_len)
    x1 = 0
    y1 = 0
    sx1 = 0
    nb1 = 0
    mn1 = _BIG
    mx1 = 0
    for t in range(nr1):
        if r_isx[t]:
            x1 += 1
            sx1 += r_len[t]
        else:
            y1 += 1
        if r_len[t] == 1:
            nb1 += 1
        if r_len[t] < mn1:
            mn1 = r_len[t]
        if r_len[t] > mx1:
            mx1 = r_len[t]

    nr2 = _runs_nj(codes, off + la, lb, r_isx, r_len)
    x2 = 0
    y2 = 0
    sx2 = 0
    nb2 = 0
    mn2 = _BIG
    mx2 = 0
    for t in range(nr2):
        if r_isx[t]:
            x2 += 1
            sx2 += r_len[t]
        else:
            y2 += 1
        if r_len[t] == 1:
            nb2 += 1
        if r_len[t] < mn2:
            mn2 = r_len[t]
        if r_len[t] > mx2:
            mx2 = r_len[t]

    k1 = 0 if (x1 == 0 or y1 == 0) else (x1 if x1 > y1 else y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else (x2 if x2 > y2 else y2)

    n_xs = x1 + x2                      # number of x-blocks in the pair
    n_ys = y1 + y2
    sum_x = sx1 + sx2                   # x-letters in the pair
    L = la + lb
    sum_y = L - sum_x

    mx = (sum_x / n_xs) if n_xs > 0 else 0.0
    my = (sum_y / n_ys) if n_ys > 0 else 0.0
    if n_xs == 0 or n_ys == 0:
        # One generator absent from the whole pair: there is only one mean, and it is both.
        only = my if mx == 0.0 else mx
        smb = only
        bmax = only
    else:
        smb = mx if mx < my else my
        bmax = mx if mx > my else my

    nb = n_xs + n_ys
    mnb = mn1 if mn1 < mn2 else mn2

    out[0] = float(L)
    out[1] = float(la if la < lb else lb)
    out[2] = float(la if la > lb else lb)
    out[3] = float(la - lb if la > lb else lb - la)
    out[4] = float(k1 + k2)
    out[5] = float(k1 if k1 > k2 else k2)
    out[6] = float(k1 if k1 < k2 else k2)
    out[7] = smb
    out[8] = bmax
    out[9] = float(nb1 + nb2)
    out[10] = float(mnb) if nb > 0 else 0.0
    out[11] = float(nb)
    out[12] = (abs(sum_x - sum_y) / L) if L > 0 else 0.0
    # Second family (index 13+). ``nb == 0`` only when the pair is empty, in which case the
    # min sentinel is still _BIG -- guard so it never leaks into a score.
    mxb = mx1 if mx1 > mx2 else mx2
    out[13] = float(mxb) if nb > 0 else 0.0
    out[14] = float(mxb - mnb) if nb > 0 else 0.0
    lo = la if la < lb else lb
    hi = la if la > lb else lb
    out[15] = (lo / hi) if hi > 0 else 0.0
    out[16] = (nb / L) if L > 0 else 0.0


@njit(cache=True)
def expand_and_score_nj(r1, r2, cap, cyclic, seg_upto, seg_w):
    """One pop's worth of work: children, packed keys, features, segmented priority.

    Returns ``(blob, offs, klens, seg_idx, score, tots, knots, moves, count)``. ``blob`` holds every
    child's packed key back to back -- ``pack_key``'s exact byte layout, r1 codes then a 0x00
    separator then r2 codes -- so the caller slices rather than encoding, and one ``tobytes()``
    serves the whole pop.

    ``moves[i]`` is child ``i``'s Definition 2.1 move ``(target, jsign, k1, k2)``, passed straight
    through from the expansion kernel. It costs nothing here -- the kernel already computed it --
    and it is what lets a production caller reconstruct a certificate path. Recovering the move by
    diffing two states instead would be wrong: the move inverts the *other* relator, so a diff
    misreads which one changed.
    """
    codes, lens, moves, count = expand_node_topk_nj(r1, r2, cap, cyclic, 1, 0)

    offs = np.empty(count + 1, dtype=np.int64)
    klens = np.empty(count, dtype=np.int64)
    tots = np.empty(count, dtype=np.int64)
    knots = np.empty(count, dtype=np.int64)
    pos = 0
    for i in range(count):
        offs[i] = pos
        k = lens[i, 0] + lens[i, 1] + 1          # +1 for the separator byte
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

    for i in range(count):
        _feats_nj(codes[i], 0, lens[i, 0], lens[i, 1], r_isx, r_len, f)
        L = f[0]
        placed = False
        for s in range(n_seg):
            if L <= seg_upto[s]:
                acc = 0.0
                for d in range(N_FEAT):
                    w = seg_w[s, d]
                    if w != 0.0:
                        acc += w * f[d]
                seg_idx[i] = s
                score[i] = acc
                placed = True
                break
        if not placed:
            seg_idx[i] = n_seg
            score[i] = L
        knots[i] = int(f[4])

    return blob, offs, klens, seg_idx, score, tots, knots, moves, count


def compile_config(cfg):
    """A config dict -> ``(seg_upto[n_seg], seg_w[n_seg, N_FEAT], seg_depth[n_seg])``.

    Weights are placed by ``FEATURES`` index, so a config naming a feature this module does not
    know raises here rather than silently scoring zero.

    ``depth`` is a per-segment scalar, kept OUT of the feature vector because it is not a property
    of the state -- see ``search_fast``.
    """
    segs = cfg["segments"]
    upto = np.empty(len(segs), dtype=np.float64)
    w = np.zeros((len(segs), N_FEAT), dtype=np.float64)
    dep = np.zeros(len(segs), dtype=np.float64)
    for i, s in enumerate(segs):
        upto[i] = INF if s.get("upto") is None else float(s["upto"])
        dep[i] = float(s.get("depth", 0.0))
        for k, v in s["w"].items():
            w[i, _FIDX[k]] = float(v)
    return upto, w, dep


def _pack(a1, a2):
    """Initial state -> packed key, matching ``pack_key`` without importing its numpy fancy-index."""
    tbl = (2, 4, 1, 3)
    b1 = bytes(tbl[2 * int(r[0]) + int(r[1])] for r in a1)
    b2 = bytes(tbl[2 * int(r[0]) + int(r[1])] for r in a2)
    return b1 + _SEP + b2


def _unpack(key):
    i = key.index(0)
    return (''.join(_CODE_TO_CHAR[c] for c in key[:i]),
            ''.join(_CODE_TO_CHAR[c] for c in key[i + 1:]))


def _arrs(key):
    i = key.index(0)
    c1 = np.frombuffer(key[:i], dtype=np.uint8)
    c2 = np.frombuffer(key[i + 1:], dtype=np.uint8)
    return (np.stack(((c1 & 1) == 1, c1 >= 3), axis=1),
            np.stack(((c2 & 1) == 1, c2 >= 3), axis=1))


def search_fast(r1_str, r2_str, budget, cfg, mrl, cyclic=True):
    """``hlab.run_one`` with the fast kernel. Same pops, same order, same numbers.

    The heap entry is ``(priority, depth, key)`` exactly as in ``LabSolver``; ``key`` is packed
    bytes rather than a string tuple, which sorts identically, so the tie-break is unchanged.

    **The optional ``depth`` weight.** A segment may carry ``"depth": w``, adding ``w * depth`` to
    that segment's score -- the ``g`` term of a weighted A*, with the structural features as ``h``.
    It is deliberately not a feature: ``depth`` is a property of the *path that found* a state, not
    of the state, and because the visited set keeps the first discovery with no decrease-key, a
    state reached later by a shorter route keeps its original key. The search stays perfectly
    deterministic -- it is the same inadmissible-search bargain weighted A* makes -- but "the
    priority of a state" stops being well defined, so the term is opt-in and named separately
    rather than hidden among the thirteen. With every ``depth`` absent or zero this function is
    bit-identical to the pure-state version (pinned in ``test_hfast.py``).
    """
    seg_upto, seg_w, seg_depth = compile_config(cfg)
    use_depth = bool(np.any(seg_depth != 0.0))
    a1 = str_to_arr(r1_str)
    a2 = str_to_arr(r2_str)
    ca, cb = canonical_pair_nj(reduce_relator_nj(a1, cyclic), reduce_relator_nj(a2, cyclic))
    key0 = _pack(ca, cb)

    f = np.empty(N_FEAT, dtype=np.float64)
    c0 = np.frombuffer(key0.replace(_SEP, b""), dtype=np.uint8)
    r_isx = np.empty(2 * mrl + 2, dtype=np.bool_)
    r_len = np.empty(2 * mrl + 2, dtype=np.int64)
    _feats_nj(c0, 0, len(ca), len(cb), r_isx, r_len, f)
    n_seg = len(seg_upto)
    p0 = None
    for s in range(n_seg):
        if f[0] <= seg_upto[s]:
            p0 = (s, float(sum(seg_w[s, d] * f[d] for d in range(N_FEAT) if seg_w[s, d] != 0.0)))
            break
    if p0 is None:
        p0 = (n_seg, float(f[0]))

    pq = [(p0, 0, key0)]
    visited = {key0: None}
    min_total = len(ca) + len(cb)
    max_pop = max(len(ca), len(cb))
    # The second hump's rows solve at no budget this program can run, so `solved` is constant-zero
    # there and ranks nothing. Knot count is the progress signal that still moves: a state with
    # fewer knots than the start is a structurally different presentation, and reaching one is the
    # opportunity the user is after even when the total length went UP to get there. Tracked over
    # discovered states, exactly like min_total, so the two are read on the same footing.
    start_K = int(f[4])
    min_K = start_K
    min_K_len = min_total
    nodes = 0

    while pq and nodes < budget:
        _, depth, key = heapq.heappop(pq)
        nodes += 1
        i = key.index(0)
        l1, l2 = i, len(key) - i - 1
        if l1 > max_pop:
            max_pop = l1
        if l2 > max_pop:
            max_pop = l2

        if l1 == 1 and l2 == 1:
            n = 0
            sk = key
            while sk is not None:
                n += 1
                sk = visited[sk]
            return {"solved": True, "nodes": nodes, "path_length": n - 1,
                    "min_total": min_total, "max_pop": max_pop,
                    "start_K": start_K, "min_K": min_K, "min_K_len": min_K_len}

        p1, p2 = _arrs(key)
        blob, offs, klens, seg_idx, score, tots, knots, _mv, count = expand_and_score_nj(
            p1, p2, mrl, cyclic, seg_upto, seg_w)
        if count == 0:
            continue
        raw = blob.tobytes()
        nd = depth + 1
        for c in range(count):
            o = int(offs[c])
            k = raw[o:o + int(klens[c])]
            if k not in visited:
                visited[k] = key
                t = int(tots[c])
                if t < min_total:
                    min_total = t
                if use_depth:
                    score[c] += seg_depth[int(seg_idx[c])] * nd
                kk = int(knots[c])
                # Strictly fewer knots wins; at equal knots prefer the shorter witness, so
                # min_K_len reports the cheapest state achieving the best knot count reached.
                if kk < min_K or (kk == min_K and t < min_K_len):
                    min_K = kk
                    min_K_len = t
                heapq.heappush(pq, ((int(seg_idx[c]), float(score[c])), nd, k))

    return {"solved": False, "nodes": nodes, "path_length": None,
            "min_total": min_total, "max_pop": max_pop,
            "start_K": start_K, "min_K": min_K, "min_K_len": min_K_len}
