"""Pins ``hexpand`` (hcompact's expansion kernel) against the shared reference
kernels it replaces for that engine.

1. The packed canonical form equals ``canonical_relator_nj``: every word of
   up to 8 symbols (exhaustive, 87,380 words), random words up to 64 symbols
   including the 32/33 and 64 boundaries, and reduced words a real search
   produces.
2. ``expand_children_h`` with the skip off and the packed path off/on is
   child-for-child ``expand_node_topk_nj``; with the skip on it is that list
   with some children removed, and every removed child is an exact repeat of
   an EARLIER child of the same pop -- specifically of the move
   ``(k1 - 1, k2 + 1 mod n_o)`` in the same (target, sign) block, which is
   what the docstring's proof says. Real popped states at cap 64 (the
   campaign's cap), edge shapes, ``cyclic=False`` (no skipping), and a cap
   above 64 (the Booth fallback).
3. ``expand_and_score_h`` gives every surviving child the reference's blob
   bytes, segment, score (bit for bit), total, knot count and move.
"""
import itertools
import os
import sys

import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from experiments.search.greedy_baseline import (          # noqa: E402
    expand_node_topk_nj, str_to_arr, reduce_relator_nj, canonical_pair_nj,
    canonical_relator_nj,
)
from experiments.heuristic_search.core.hfast import expand_and_score_nj  # noqa: E402
from experiments.heuristic_search.core.hexpand import (   # noqa: E402
    canon_packed_codes, expand_children_h, expand_and_score_h,
)

_CODE = {(False, False): 2, (False, True): 4, (True, False): 1, (True, True): 3}


def _codes_of(arr):
    return np.array([_CODE[(bool(a), bool(b))] for a, b in arr], dtype=np.uint8)


def _bool_word(vals):
    """order values (0..3 = Y, y, X, x) -> (n, 2) bool array."""
    a = np.empty((len(vals), 2), dtype=np.bool_)
    for i, v in enumerate(vals):
        a[i, 0] = bool(v >> 1)
        a[i, 1] = bool(v & 1)
    return a


# ---------------------------------------------------------------------------
# 1. packed canonical form == canonical_relator_nj
# ---------------------------------------------------------------------------
def test_packed_canonical_form_is_booths_on_every_word_up_to_8_symbols():
    n_words = 0
    for n in range(0, 9):
        for vals in itertools.product(range(4), repeat=n):
            w = _bool_word(vals)
            want = _codes_of(canonical_relator_nj(w))
            got = canon_packed_codes(w)
            assert np.array_equal(got, want), vals
            n_words += 1
    assert n_words == sum(4 ** n for n in range(9))


@pytest.mark.parametrize("lo,hi,count", [(9, 31, 40000), (31, 34, 20000),
                                         (33, 64, 40000), (63, 65, 4000)])
def test_packed_canonical_form_is_booths_on_random_words(lo, hi, count):
    rng = np.random.default_rng(lo * 1000 + hi)
    for _ in range(count):
        n = int(rng.integers(lo, hi))
        n = min(n, 64)
        w = rng.integers(0, 2, size=(n, 2)).astype(np.bool_)
        # periodic words and words with long equal runs are where a least
        # rotation is decided late; mix some in
        r = rng.random()
        if r < 0.15 and n >= 2:
            p = int(rng.integers(1, max(2, n // 2 + 1)))
            w = np.concatenate([w[:p]] * (n // p + 1))[:n]
        elif r < 0.3:
            w[: n // 2, 0] = w[0, 0]
        want = _codes_of(canonical_relator_nj(w))
        got = canon_packed_codes(w)
        assert np.array_equal(got, want), (n, w.tolist())


def test_packed_canonical_form_on_reduced_words_a_search_makes():
    for r1, r2 in [("YXXyxYx", "YYYYYYXyxyX"), ("YXXYxxyX", "YYYYYxyyyyX")]:
        a1 = reduce_relator_nj(str_to_arr(r1), True)
        a2 = reduce_relator_nj(str_to_arr(r2), True)
        a1, a2 = canonical_pair_nj(a1, a2)
        codes, lens, moves, count = expand_node_topk_nj(a1, a2, 64, True, 1, 0)
        for i in range(count):
            la, lb = int(lens[i, 0]), int(lens[i, 1])
            for word in (codes[i, :la], codes[i, la:la + lb]):
                w = np.stack(((word & 1) == 1, word >= 3), axis=1)
                assert np.array_equal(canon_packed_codes(w),
                                      _codes_of(canonical_relator_nj(w)))


# ---------------------------------------------------------------------------
# 2. the children
# ---------------------------------------------------------------------------
def _popped_states(r1, r2, budget, every):
    from experiments.heuristic_search.core.perf_lab.phase_split import RecordingSolver
    from experiments.search.run_leftovers_1m import S20_MK2
    from experiments.heuristic_search.core.hcompact import _decode_h

    s = RecordingSolver(r1, r2, max_nodes=budget, max_relator_length=64,
                        config=S20_MK2, track_path=False)
    s.solve()
    out = []
    for i in range(0, budget, every):
        top = int(s.popped[i])
        out.append((_decode_h(s.arena, top, 0, int(s.len1[top]), s.rw).copy(),
                    _decode_h(s.arena, top, 4 * s.w, int(s.len2[top]), s.rw).copy()))
    return out


def _child(codes, lens, moves, j):
    k = int(lens[j, 0] + lens[j, 1])
    return (int(lens[j, 0]), int(lens[j, 1]), codes[j, :k].tobytes(),
            tuple(int(v) for v in moves[j]))


def _child_h(cbuf, offs, lens, moves, j):
    k = int(lens[j, 0] + lens[j, 1])
    o = int(offs[j])
    return (int(lens[j, 0]), int(lens[j, 1]), cbuf[o:o + k].tobytes(),
            tuple(int(v) for v in moves[j]))


def _first_occurrences(stream):
    """The stream with every exact repeat (same la, lb, codes) of an earlier
    element removed; the move is not part of identity."""
    seen = set()
    out = []
    for c in stream:
        if c[:3] not in seen:
            seen.add(c[:3])
            out.append(c[:3])
    return out


def _check_children(a1, a2, cap, cyclic, skip, packed):
    """Returns (reference count, removed count)."""
    rc, rl, rm, rcount = expand_node_topk_nj(a1, a2, cap, cyclic, 1, 0)
    hb, ho, hl, hm, hcount = expand_children_h(a1, a2, cap, cyclic, skip, packed)
    assert int(ho[hcount]) == int(np.sum(hl[:hcount]))
    ref = [_child(rc, rl, rm, j) for j in range(rcount)]
    got = [_child_h(hb, ho, hl, hm, j) for j in range(hcount)]
    if not (skip and cyclic):
        assert got == ref
        return rcount, 0
    # the two streams are the same stream once exact repeats of earlier
    # candidates are removed from each, order preserved (this is the
    # property the engine's table makes the search blind to)
    assert _first_occurrences(got) == _first_occurrences(ref)
    n1, n2 = len(a1), len(a2)
    i = 0
    removed = 0
    for j, rj in enumerate(ref):
        if i < len(got) and got[i] == rj:
            i += 1
            continue
        # removed: must repeat an earlier reference child, and precisely the
        # predecessor move (target, sign, k1 - 1, k2 + 1 mod n_o)
        removed += 1
        target, js, k1, k2 = rj[3]
        no = n2 if target == 1 else n1
        assert k1 >= 1, rj
        pred = (target, js, k1 - 1, (k2 + 1) % no)
        earlier = [r for r in ref[:j] if r[3] == pred]
        assert len(earlier) == 1, (rj, pred)
        assert earlier[0][:3] == rj[:3], (rj, earlier[0])
    assert i == len(got), (i, len(got))
    return rcount, removed


@pytest.mark.parametrize("row", [("YXXyxYx", "YYYYYYXyxyX"),        # aca_0
                                 ("YXXYxxyX", "YYYYYxyyyyX")])      # aca_47
@pytest.mark.parametrize("skip,packed", [(False, False), (False, True),
                                         (True, False), (True, True)])
def test_children_on_real_popped_states(row, skip, packed):
    """2,000 real popped states per row (every third pop of 6,000)."""
    r1, r2 = row
    states = _popped_states(r1, r2, 6000, 3)
    assert len(states) == 2000
    assert max(len(a) + len(b) for a, b in states) > 30
    n_ref = n_rem = 0
    for a1, a2 in states:
        r, d = _check_children(a1, a2, 64, True, skip, packed)
        n_ref += r
        n_rem += d
    if skip:
        assert n_rem > 0.2 * n_ref, (n_rem, n_ref)     # the skip does work
    else:
        assert n_rem == 0


def test_children_on_edge_shapes_both_cyclic_settings_and_a_cap_past_64():
    shapes = [("x", "y"), ("x", "xyxY"), ("xxxx", "yyy"), ("xyXY", "yxYX"),
              ("xY", "Yx"), ("xxyy", "XXYY"), ("xyxyxyxy", "xxxxxxxxxxxxxxxxx"),
              ("YXXYxxyX", "YYYYYxyyyyX")]
    for s1, s2 in shapes:
        a1 = reduce_relator_nj(str_to_arr(s1), True)
        a2 = reduce_relator_nj(str_to_arr(s2), True)
        a1, a2 = canonical_pair_nj(a1, a2)
        for cyclic in (True, False):
            for cap in (12, 64, 80):
                for skip in (False, True):
                    for packed in (False, True):
                        _check_children(a1, a2, cap, cyclic, skip, packed)


def test_children_past_32_symbols_use_the_two_word_path():
    """States whose children exceed 32 symbols per relator, at cap 64: the
    (hi, lo) rotation path, pinned against the reference."""
    rng = np.random.default_rng(7)
    n_long = 0
    for _ in range(40):
        s1 = "".join(rng.choice(list("xyXY"), size=int(rng.integers(20, 30))))
        s2 = "".join(rng.choice(list("xyXY"), size=int(rng.integers(20, 30))))
        a1 = reduce_relator_nj(str_to_arr(s1), True)
        a2 = reduce_relator_nj(str_to_arr(s2), True)
        if len(a1) == 0 or len(a2) == 0:
            continue
        a1, a2 = canonical_pair_nj(a1, a2)
        rc, rl, rm, rcount = expand_node_topk_nj(a1, a2, 64, True, 1, 0)
        n_long += int(np.sum(rl[:rcount] > 32))
        for skip in (False, True):
            _check_children(a1, a2, 64, True, skip, True)
    assert n_long > 100, n_long


# ---------------------------------------------------------------------------
# 3. the fused wrapper
# ---------------------------------------------------------------------------
def _scored(t, i):
    blob, offs, klens, seg_idx, score, tots, knots, moves, count = t
    o, k = int(offs[i]), int(klens[i])
    return (blob[o:o + k].tobytes(), int(seg_idx[i]), np.float64(score[i]).tobytes(),
            int(tots[i]), int(knots[i]), tuple(int(v) for v in moves[i]))


def test_fused_wrapper_gives_survivors_the_reference_values_bit_for_bit():
    from experiments.search.run_leftovers_1m import S20_MK2
    from experiments.heuristic_search.core.hfast import compile_config

    seg_upto, seg_w, _ = compile_config(S20_MK2)
    states = _popped_states("YXXYxxyX", "YYYYYxyyyyX", 4000, 41)
    for a1, a2 in states:
        ref = expand_and_score_nj(a1, a2, 64, True, seg_upto, seg_w, 0)
        for skip, packed in [(False, False), (True, True)]:
            got = expand_and_score_h(a1, a2, 64, True, seg_upto, seg_w, skip, packed)
            r = [_scored(ref, i) for i in range(ref[8])]
            g = [_scored(got, i) for i in range(got[8])]
            if not skip:
                assert g == r
                continue
            i = 0
            for j, rj in enumerate(r):
                if i < len(g) and g[i] == rj:
                    i += 1
                elif rj[:5] not in [x[:5] for x in r[:j]]:
                    raise AssertionError(("removed child is not a repeat", rj))
            assert i == len(g)
