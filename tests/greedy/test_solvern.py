"""The general-n numba solver: spec trace-equality and n>3 seamlessness.

``solvern`` is a numba port of ``spec/search.py`` generalised to any ``n_gen``.
Wherever the spec can run (``n_gen <= 3``) it must reproduce the spec's pop order
*exactly* -- so these tests assert trace-equality against the spec on stats and
``path_moves``. Past ``n_gen = 3`` the spec cannot render, so the solver's own
``moves_to_states`` replay is the oracle.

All budgets are <= 1000 (the local hard ceiling); production runs live on Colab.
"""

import pytest

from experiments.search.greedy_baseline import greedy_search as baseline_search
from experiments.greedy_tests.fixtures.presentations import ak, ms640
from experiments.greedy_tests.spec import search as spec_search
from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.presentation import Presentation, trivial
from experiments.greedy_tests.spec.words import (
    ascii_order_key, word_to_str as spec_word_to_str,
)
from experiments.stable_ac import solvern

#: every stat field the solver must reproduce from the spec, exactly. Excludes
#: nothing: at n_gen<=3 solvern's pop order IS the spec's, min/max included.
TRACE_FIELDS = (
    "solved", "nodes_explored", "path_length",
    "min_relator_length", "max_relator_length", "max_relator_length_expanded",
    "min_relator", "max_relator", "max_relator_expanded",
)

#: Branch-A no-CoV target: <x,y,z | r1, r2, Z.xy> from ms640[0].
NOCOV = Presentation(3, ms640([0])[0].relators + ((-3, 1, 2),))
#: three genuinely-interacting relators, so the source index j is load-bearing.
THREE_REL = Presentation(3, ((1, 2), (-2, 3), (-3, -1)))


def _assert_trace_equal(pres, budget, cap):
    sp = spec_search.search(pres, budget, cap=cap, cyclic=True)
    me = solvern.search_n(pres, budget, cap=cap, cyclic=True)
    for f in TRACE_FIELDS:
        assert sp[f] == me[f], f"{f}: spec={sp[f]!r} solvern={me[f]!r}"
    sp_moves = [tuple(mv) for mv in sp["path_moves"]]
    me_moves = [solvern.str_to_move(m) for m in me["path_moves"]]
    assert sp_moves == me_moves


# -- basics ------------------------------------------------------------------


def test_trivial_3gen_solves_at_the_first_node():
    r = solvern.search_n(trivial(3), 10)
    assert r["solved"]
    assert r["nodes_explored"] == 1
    assert r["path_length"] == 0
    assert r["path_moves"] == []


def test_a_stabilized_solvable_presentation_solves_and_replays_like_the_spec():
    p = ms640([0])[0].stabilize()
    me = solvern.search_n(p, 1000, cap=64)
    assert me["solved"]
    final = me["path_words"][-1]
    assert Presentation(p.n_gen, final).is_trivial()

    spec = spec_search.search(p, 1000, cap=64)
    spec_states = [q.relators for q in spec_search.replay(p, spec["path_moves"])]
    my_states = solvern.moves_to_states(p.relators, me["path_moves"], True)
    assert my_states == spec_states


# -- spec trace-equality -----------------------------------------------------


@pytest.mark.parametrize("idx", range(10))
def test_trace_equality_vs_spec_at_two_generators(idx):
    _assert_trace_equal(ms640([idx])[0], 1000, cap=24)


@pytest.mark.parametrize("pres,name", [
    (ms640([0])[0].stabilize(), "ms640-0-stab"),
    (ak(3).stabilize(), "ak3-stab"),
    (THREE_REL, "three-rel"),
    (NOCOV, "nocov"),
], ids=lambda v: v if isinstance(v, str) else "p")
def test_trace_equality_vs_spec_at_three_generators(pres, name):
    _assert_trace_equal(pres, 1000, cap=64)


#: nocov ms640[165] with w=xyy: start relator lengths 4/5/8, so caps 5/6/7 put
#: the start above/at/below the cap boundary. spec drops a child when ANY of
#: its relators exceeds cap -- inherited ones included -- which only bites when
#: the START carries an over-cap relator; this corpus is that regime.
OVER_CAP_START = Presentation.from_strs(
    *ms640([165])[0].to_strs(), "Z" + "xyy", n_gen=3)


@pytest.mark.parametrize("cap", [5, 6, 7])
def test_trace_equality_when_the_start_carries_an_over_cap_relator(cap):
    _assert_trace_equal(OVER_CAP_START, 800, cap=cap)


def test_an_over_cap_start_expands_to_nothing_below_the_boundary():
    """Pins the semantics explicitly (verified against spec, both == 1): at
    cap=5 the start (lengths 4/5/8) is popped, every child either inherits the
    over-cap relator or fails the new-relator filter, and the heap empties."""
    sp = spec_search.search(OVER_CAP_START, 800, cap=5, cyclic=True)
    me = solvern.search_n(OVER_CAP_START, 800, cap=5, cyclic=True)
    assert sp["nodes_explored"] == me["nodes_explored"] == 1
    assert not sp["solved"] and not me["solved"]


def test_length_stats_match_greedy_baseline_at_two_generators():
    """The two-generator baseline pops in the same order, so solved/nodes/path
    and the three length stats agree. Its min/max relator *strings* are excluded:
    it tie-breaks with min()/max() over a set, i.e. by PYTHONHASHSEED."""
    for p in ms640(range(6)):
        r1, r2 = p.to_strs()
        base = baseline_search(r1, r2, 1000, max_relator_length=24,
                               cyclic_reduce=True)
        me = solvern.search_n(p, 1000, cap=24, cyclic=True)
        for f in ("solved", "nodes_explored", "path_length",
                  "min_relator_length", "max_relator_length",
                  "max_relator_length_expanded"):
            assert base[f] == me[f], f"{f}: base={base[f]!r} solvern={me[f]!r}"


# -- n_gen = 4 seamlessness (solvern's own replay is the oracle) --------------


@pytest.mark.parametrize("pres,name", [
    (trivial(4), "trivial-4"),
    (ms640([0])[0].stabilize().stabilize(), "ms640-0-stab-stab"),
], ids=lambda v: v if isinstance(v, str) else "p")
def test_four_generator_search_runs_deterministically_and_replays(pres, name):
    a = solvern.search_n(pres, 500, cap=64)
    b = solvern.search_n(pres, 500, cap=64)
    assert a == b                                   # deterministic
    assert 1 <= a["nodes_explored"] <= 500          # budget respected
    if a["solved"]:
        replayed = solvern.moves_to_states(pres.relators, a["path_moves"], True)
        assert replayed == a["path_words"]          # replay is authoritative
        final = replayed[-1]
        assert all(len(r) == 1 for r in final)
        assert Presentation(pres.n_gen, final).is_trivial()
        d = abs_det(pres)
        for st in replayed:
            assert abs_det(Presentation(pres.n_gen, st)) == d == 1


# -- the two-symbol-order trap: tiebreak == rendered ASCII order --------------


def _ascii_state_key(state):
    return tuple(spec_word_to_str(r) for r in state)


@pytest.mark.parametrize("a,b", [
    (((1,),), ((1, 2),)),                              # prefix (single relator)
    (((1, 2), (1,)), ((1, 2), (1, 2))),                # shared first, prefix second
    (((1,), (2,)), ((1,), (-2,))),                     # X-vs-x in the second slot
    (((1, 2), (-3,)), ((1, 2), (3,))),                 # uppercase below lowercase
    (((-1, -2, 3),), ((-1, -2, -3),)),                 # deep tie then decide
])
def test_tiebreak_reproduces_ascii_string_order_on_known_pairs(a, b):
    ascii_cmp = (_ascii_state_key(a) > _ascii_state_key(b)) \
        - (_ascii_state_key(a) < _ascii_state_key(b))
    tb_cmp = (solvern._tiebreak(a) > solvern._tiebreak(b)) \
        - (solvern._tiebreak(a) < solvern._tiebreak(b))
    assert ascii_cmp == tb_cmp


def test_tiebreak_reproduces_ascii_string_order_on_a_fuzz_corpus():
    import random
    rng = random.Random(1)

    def rand_word(n_gen, length):
        alpha = [g for g in range(-n_gen, n_gen + 1) if g != 0]
        return tuple(rng.choice(alpha) for _ in range(length))

    for _ in range(3000):
        n_gen = rng.choice([1, 2, 3])
        n_rel = rng.choice([2, 3])
        a = tuple(rand_word(n_gen, rng.randint(0, 5)) for _ in range(n_rel))
        b = tuple(rand_word(n_gen, rng.randint(0, 5)) for _ in range(n_rel))
        ac = (_ascii_state_key(a) > _ascii_state_key(b)) \
            - (_ascii_state_key(a) < _ascii_state_key(b))
        tc = (solvern._tiebreak(a) > solvern._tiebreak(b)) \
            - (solvern._tiebreak(a) < solvern._tiebreak(b))
        assert ac == tc, (a, b)
    # the packed order must also agree with ascii_order_key symbol-wise
    for g in range(-3, 4):
        if g == 0:
            continue
        assert ascii_order_key(g) == (g > 0, abs(g))


# -- misc contract-ish properties --------------------------------------------


def test_budget_is_respected_when_the_search_is_capped():
    r = solvern.search_n(ak(3).stabilize(), 300, cap=64)
    assert 1 <= r["nodes_explored"] <= 300


def test_the_progress_callback_is_result_neutral():
    # The callback fires every 1024 pops; under the <=1000 budget ceiling it
    # never fires, so ``seen`` stays empty -- the point is that supplying it
    # changes nothing (and any firing would land on a 1024-multiple).
    p = ak(3).stabilize()
    quiet = solvern.search_n(p, 1000, cap=64)
    seen = []
    loud = solvern.search_n(p, 1000, cap=64, progress=seen.append)
    for f in TRACE_FIELDS:
        assert quiet[f] == loud[f]
    assert all(n % 1024 == 0 for n in seen)


def test_no_path_state_exceeds_the_per_relator_cap():
    cap = 24
    me = solvern.search_n(ms640([0])[0], 500, cap=cap)
    assert me["solved"]
    for st in me["path_words"]:
        for r in st:
            assert len(r) <= cap


def test_the_move_codec_round_trips():
    for mv in [(0, 1, 1, 0, 0), (2, 0, -1, 3, 5), (1, 2, 1, 7, 11)]:
        assert solvern.str_to_move(solvern.move_to_str(mv)) == mv
    me = solvern.search_n(NOCOV, 500, cap=64)
    assert me["solved"]
    for s in me["path_moves"]:
        assert solvern.move_to_str(solvern.str_to_move(s)) == s


# -- the Tietze step add_generator_with_word ---------------------------------


def test_add_generator_with_word_shapes_and_preserves_abs_det_at_k2():
    base = ms640([0])[0]
    r1, r2 = base.to_strs()
    p = solvern.add_generator_with_word([r1, r2], "xy")
    assert (p.n_gen, p.n_rel) == (base.n_gen + 1, base.n_rel + 1)
    assert p.relators[:2] == base.relators
    assert p.relators[-1] == (-3,) + solvern.str_to_word("xy")
    assert abs_det(p) == abs_det(base) == 1


def test_add_generator_with_word_shapes_and_preserves_abs_det_at_k3():
    base3 = solvern.nocov_presentation(*ms640([0])[0].to_strs(), "xy")
    assert (base3.n_gen, base3.n_rel) == (3, 3)
    strs3 = [solvern.word_to_str(r) for r in base3.relators]
    p = solvern.add_generator_with_word(strs3, "xyz", n_gen=3)
    assert (p.n_gen, p.n_rel) == (4, 4)
    assert p.relators[:3] == base3.relators
    assert p.relators[-1] == (-4,) + solvern.str_to_word("xyz")
    assert abs_det(p) == abs_det(base3) == 1
