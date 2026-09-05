"""``expand_node_nj``: the fused neighbours+reduce+canonicalise used by the heavy solver.

It must agree with ``get_neighbors_with_moves_nj`` + reduce + canonicalise + cap
filter not just as a *set* but in **count, order, moves and codes**. The heavy
solver assigns ``depth`` by first-visit order, and the heap tie-breaks on
``depth``, so a reordering here would silently change ``nodes_explored``.
"""

import numpy as np
import pytest

from experiments.search.greedy_baseline import (
    _CODE_TO_CHAR, arr_to_str, canonical_pair_nj, expand_node_nj,
    get_neighbors_with_moves_nj, reduce_relator_nj, str_to_arr,
)
from experiments.greedy_tests.fixtures.presentations import (
    MMS02_LEN14, ak, ms640, ms_unsolved, random_presentations,
)

CASES = (ms640(range(0, 20)) + ms_unsolved(range(0, 3)) + [ak(3), MMS02_LEN14]
         + random_presentations(seed=99, count=8, max_len=6))
CAPS = [8, 24, 48]
CYCLIC = [True, False]


def _expanded(pres, cap, cyclic):
    r1, r2 = (str_to_arr(s) for s in pres.to_strs())
    codes, lens, moves, count = expand_node_nj(r1, r2, cap, cyclic)
    rows = []
    for i in range(count):
        la, lb = int(lens[i, 0]), int(lens[i, 1])
        row = codes[i]
        s1 = "".join(_CODE_TO_CHAR[c] for c in row[:la])
        s2 = "".join(_CODE_TO_CHAR[c] for c in row[la:la + lb])
        rows.append(((s1, s2), tuple(int(v) for v in moves[i])))
    return rows, codes, lens, moves, count


def _reference(pres, cap, cyclic):
    r1, r2 = (str_to_arr(s) for s in pres.to_strs())
    rows = []
    for nr1, nr2, t, js, k1, k2 in get_neighbors_with_moves_nj(r1, r2):
        a = reduce_relator_nj(nr1, cyclic)
        b = reduce_relator_nj(nr2, cyclic)
        if len(a) > cap or len(b) > cap:
            continue
        ca, cb = canonical_pair_nj(a, b)
        rows.append(((arr_to_str(ca), arr_to_str(cb)),
                     (int(t), int(js), int(k1), int(k2))))
    return rows


@pytest.mark.parametrize("cap", CAPS)
@pytest.mark.parametrize("cyclic", CYCLIC)
def test_matches_the_reference_in_count_order_moves_and_codes(cap, cyclic):
    for pres in CASES:
        got, *_ = _expanded(pres, cap, cyclic)
        assert got == _reference(pres, cap, cyclic), pres.to_strs()


def test_count_never_exceeds_the_allocated_upper_bound():
    for pres in CASES:
        r1, r2 = (str_to_arr(s) for s in pres.to_strs())
        _, _, _, count = expand_node_nj(r1, r2, 24, True)
        ub = 4 * (len(r1) + 1) * (len(r2) + 1)
        assert count <= ub


@pytest.mark.parametrize("cap", CAPS)
def test_every_emitted_relator_respects_the_cap(cap):
    for pres in CASES:
        _, _, lens, _, count = _expanded(pres, cap, True)
        for i in range(count):
            assert 0 <= lens[i, 0] <= cap
            assert 0 <= lens[i, 1] <= cap
            assert lens[i, 0] + lens[i, 1] <= 2 * cap  # the buffer width


def test_over_cap_children_are_dropped_not_raised():
    """The cap is a silent no-op filter, in both solvers."""
    pres = ms640([0])[0]
    _, _, _, _, wide = _expanded(pres, 48, True)
    _, _, _, _, narrow = _expanded(pres, 1, True)
    assert narrow <= wide


def test_emitted_codes_use_only_the_four_symbol_codes():
    """0x00 is reserved as the key separator, so it must never appear as a symbol."""
    for pres in CASES[:8]:
        _, codes, lens, _, count = _expanded(pres, 24, True)
        for i in range(count):
            la, lb = int(lens[i, 0]), int(lens[i, 1])
            used = codes[i][:la + lb]
            assert set(np.unique(used)).issubset({1, 2, 3, 4})


def test_only_the_first_count_rows_are_meaningful():
    """Rows are packed with no gaps, and the buffer beyond ``count`` is uninitialised.

    ``codes`` is ``np.empty``, so reading past ``count`` reads garbage by design.
    This pins that the caller only ever needs ``[:count]``.
    """
    pres = ms640([3])[0]
    r1, r2 = (str_to_arr(s) for s in pres.to_strs())
    codes, lens, moves, count = expand_node_nj(r1, r2, 24, True)
    assert count == len(_reference(pres, 24, True))
    for i in range(count):
        assert moves[i, 0] in (1, 2)
        assert moves[i, 1] in (1, -1)
