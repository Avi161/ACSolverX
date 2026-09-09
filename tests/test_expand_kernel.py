"""Pins the expansion kernel ``expand_node_topk_nj`` (the one every engine
and the Python oracle share) against the independent ``np.roll``-based
``expand_node_nj``, child by child, on REAL states at cap 64.

Why this exists: ``hcompact_baseline`` and ``hsolve`` import the live
``greedy_baseline``, so a change to the kernel's values would move the
frozen baseline, the oracle and the candidate together and every
search-level gate would pass on a changed search. ``expand_node_nj`` builds
each child with ``np.roll`` + ``np.concatenate`` + the unmodified
``reduce_relator_nj`` / ``canonical_pair_nj`` and never touches ``_rot_at``,
``_seam_reduced_len_nj`` or the scratch-buffer path, so it is a reference
the kernel's edits cannot move. The existing unhoisted-formula test covers
four short seeds at cap 48; this one takes states a real S20_MK2 search
actually pops, including ones near the cap, where the seam cascade and the
cyclic trim are exercised at length.
"""
import os
import sys

import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from experiments.search.greedy_baseline import (          # noqa: E402
    expand_node_nj, expand_node_topk_nj, str_to_arr, reduce_relator_nj,
    canonical_pair_nj,
)


def _popped_states(r1, r2, budget, every):
    """States a real search pops, as (a1, a2) bool arrays."""
    from experiments.heuristic_search.core.perf_lab.phase_split import RecordingSolver
    from experiments.search.run_leftovers_1m import S20_MK2
    from experiments.heuristic_search.core.hcompact import _decode_h

    s = RecordingSolver(r1, r2, max_nodes=budget, max_relator_length=64,
                        config=S20_MK2, track_path=False)
    s.solve()
    out = []
    for i in range(0, budget, every):
        top = int(s.popped[i])
        # the engine's own 2-bit decoder; r2's region starts at symbol 4*w
        out.append((_decode_h(s.arena, top, 0, int(s.len1[top]), s.rw).copy(),
                    _decode_h(s.arena, top, 4 * s.w, int(s.len2[top]), s.rw).copy()))
    return out


def _assert_same_children(a1, a2, cap, cyclic):
    codes, lens, moves, count = expand_node_topk_nj(a1, a2, cap, cyclic, 1, 0)
    c, l, m, cnt = expand_node_nj(a1, a2, cap, cyclic)
    assert count == cnt
    assert np.array_equal(lens[:count], l[:cnt])
    assert np.array_equal(moves[:count], m[:cnt])
    for j in range(count):
        k = int(lens[j, 0] + lens[j, 1])
        assert np.array_equal(codes[j, :k], c[j, :k]), j


@pytest.mark.parametrize("row", [("YXXyxYx", "YYYYYYXyxyX"),        # aca_0
                                 ("YYXXXyx", "YYxyxyXyXYX")])       # aca_4
def test_topk_kernel_matches_the_roll_kernel_on_real_popped_states(row):
    r1, r2 = row
    states = _popped_states(r1, r2, 6000, 37)
    assert len(states) > 150
    assert max(len(a) + len(b) for a, b in states) > 30
    for a1, a2 in states:
        _assert_same_children(a1, a2, 64, True)


def test_topk_kernel_matches_the_roll_kernel_on_edge_shapes():
    """Length-1 relators, a relator that is a pure power, a pair whose
    children cancel to nothing, and cyclic=False -- the branches a real
    search visits rarely."""
    for s1, s2 in [("x", "y"), ("x", "xyxY"), ("xxxx", "yyy"), ("xyXY", "yxYX"),
                   ("xY", "Yx"), ("xxyy", "XXYY")]:
        a1 = reduce_relator_nj(str_to_arr(s1), True)
        a2 = reduce_relator_nj(str_to_arr(s2), True)
        a1, a2 = canonical_pair_nj(a1, a2)
        for cyclic in (True, False):
            _assert_same_children(a1, a2, 12, cyclic)
