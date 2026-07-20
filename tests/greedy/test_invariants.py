"""Abelianization: the one oracle the solver shares no code with.

Every other test in this suite compares the solver to a spec that was written
from the same description. These compare it to a quantity it never computes.
An exponent-sum matrix cannot be made to agree with a broken expander by having
made the same mistake twice.

The move ``r_i <- rot(r_i) . rot(r_j ** s)`` is an elementary row operation on
that matrix, so ``det`` is preserved exactly; canonicalisation may negate or
permute rows, so ``abs(det)`` is preserved. The trivial presentation has
``M = I``. Hence every state reachable from an AC-trivial presentation has
``abs(det) == 1``, and any state the search invents with a different value came
from an unsound move.
"""

import random

import pytest

from experiments.search.greedy_baseline import (
    arr_to_str, canonical_pair_nj, get_neighbors_with_moves_nj, greedy_search,
    moves_to_states, reduce_relator_nj, str_to_arr,
)
from experiments.greedy_tests.fixtures.presentations import (
    MMS02_LEN14, ak, load_dataset, MS640, MS_UNSOLVED, ms640, ms_unsolved,
)
from experiments.greedy_tests.spec.invariants import (
    abs_det, det_int, exponent_sum_matrix, is_perfect_abelianization,
    smith_normal_form,
)
from experiments.greedy_tests.spec.moves import neighbours
from experiments.greedy_tests.spec.presentation import Presentation, trivial
from experiments.greedy_tests.spec.words import str_to_word


def test_det_int_agrees_with_numpy_on_random_matrices():
    np = pytest.importorskip("numpy")
    rng = random.Random(7)
    for n in (1, 2, 3, 4):
        for _ in range(60):
            m = [[rng.randint(-6, 6) for _ in range(n)] for _ in range(n)]
            assert det_int(m) == round(float(np.linalg.det(np.array(m, dtype=float))))


def test_exponent_sum_matrix_of_the_trivial_presentation_is_the_identity():
    for n in (2, 3, 4):
        m = exponent_sum_matrix(trivial(n))
        assert m == [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        assert abs_det(trivial(n)) == 1


def test_rotation_and_inversion_only_change_the_sign_of_det():
    from experiments.greedy_tests.spec.words import inverse, rotate

    p = MMS02_LEN14
    d = det_int(exponent_sum_matrix(p))
    rot = Presentation(2, (rotate(p.relators[0], 3), p.relators[1]))
    assert det_int(exponent_sum_matrix(rot)) == d
    inv = Presentation(2, (inverse(p.relators[0]), p.relators[1]))
    assert det_int(exponent_sum_matrix(inv)) == -d


def test_every_ms640_presentation_has_unit_determinant():
    """A necessary condition for AC-triviality, and a check that the loader is right."""
    pres = load_dataset(MS640)
    assert len(pres) == 640
    assert all(abs_det(p) == 1 for p in pres)


def test_every_ms640_presentation_has_trivial_abelianization():
    assert all(is_perfect_abelianization(p) for p in load_dataset(MS640))


def test_every_unsolved_representative_has_unit_determinant():
    """They resist the search, but they are still balanced presentations of a perfect group."""
    pres = load_dataset(MS_UNSOLVED)
    assert pres and all(abs_det(p) == 1 for p in pres)


@pytest.mark.parametrize("pres", [ak(2), ak(3), MMS02_LEN14],
                         ids=["AK(2)", "AK(3)", "MMS02_len14"])
def test_literature_fixtures_have_unit_determinant(pres):
    """Transcription check: a mistyped relator almost always breaks abs(det) == 1.

    Note this asserts nothing about AC-triviality, which is open for AK(3) and
    for the MMS02 instance.
    """
    assert abs_det(pres) == 1


def test_smith_normal_form_detects_a_nontrivial_abelianization():
    # <x, y | x^2, y> abelianises to Z/2.
    p = Presentation(2, ((1, 1), (2,)))
    assert smith_normal_form(exponent_sum_matrix(p)) == [1, 2]
    assert not is_perfect_abelianization(p)
    assert abs_det(p) == 2


# -- the invariant applied to the real solver -------------------------------


def _numba_children(pres, cap=24, cyclic=True):
    r1, r2 = (str_to_arr(s) for s in pres.to_strs())
    out = []
    for nr1, nr2, *_ in get_neighbors_with_moves_nj(r1, r2):
        a = reduce_relator_nj(nr1, cyclic)
        b = reduce_relator_nj(nr2, cyclic)
        if len(a) > cap or len(b) > cap:
            continue
        ca, cb = canonical_pair_nj(a, b)
        out.append(Presentation(2, (str_to_word(arr_to_str(ca)),
                                    str_to_word(arr_to_str(cb)))))
    return out


def test_the_numba_expander_preserves_abs_det():
    """If ``get_neighbors_with_moves_nj`` invented an unsound move, this fails."""
    for pres in ms640(range(0, 30)) + ms_unsolved(range(0, 3)) + [ak(3)]:
        d = abs_det(pres)
        for child in _numba_children(pres):
            assert abs_det(child) == d, pres.to_strs()


def test_the_spec_expander_preserves_abs_det_at_three_relators():
    p = Presentation(3, ((1, 2, -1, -2), (2, 3, -2, -3), (3,)))
    d = abs_det(p)
    for child, _ in neighbours(p, cap=24, cyclic=True):
        assert abs_det(child) == d


def test_every_step_of_a_recovered_solution_path_preserves_abs_det():
    for idx in (0, 3, 7, 11):
        pres = ms640([idx])[0]
        stats = greedy_search(*pres.to_strs(), 1000)
        assert stats["solved"]
        states = moves_to_states(*pres.to_strs(),
                                 [tuple(int(v) for v in m.split("_"))
                                  for m in stats["path_moves"]])
        for r1, r2 in states:
            step = Presentation(2, (str_to_word(r1), str_to_word(r2)))
            assert abs_det(step) == 1
        assert Presentation(2, (str_to_word(states[-1][0]),
                                str_to_word(states[-1][1]))).is_trivial()


@pytest.mark.stable
def test_stabilization_preserves_abs_det_and_abelianization():
    for pres in [ms640([0])[0], ak(3), MMS02_LEN14]:
        s = pres.stabilize()
        assert s.n_gen == 3 and s.n_rel == 3
        assert abs_det(s) == abs_det(pres)
        assert is_perfect_abelianization(s) == is_perfect_abelianization(pres)
