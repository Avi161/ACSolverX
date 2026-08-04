"""Tests for ``experiments/stable_ac/fable/rank_n_ac_search.py`` (task A7).

Scope, in the order the task asked for it:

* move legality -- every generated state is balanced, freely reduced, non-empty;
* the AC5 legality guard (single-generator relator, generator absent elsewhere);
* group preservation, by an abelianisation invariant on every move and by Todd-Coxeter
  on a couple of small cases;
* determinism under a fixed seed;
* the hunter finds a known ``gamma_N = 0`` state, and its output is re-verified by two
  independent routes;
* the triangulation helper reproduces ``S1_TRIANGULATION_LEMMA.md`` section 4.4 exactly.
"""

from __future__ import annotations

import random

import pytest

from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable.coset_enum import is_trivial_group
import experiments.stable_ac.fable.rank_n_ac_search as RNS
from experiments.stable_ac.fable.rank_n_ac_search import (
    AK3,
    DEFAULT_KIND_WEIGHTS,
    Limits,
    Pres,
    abelian_invariant,
    cyclically_reduce_pres,
    stabilizer_entangled,
    apply_move,
    canonical_key,
    cyclic_reduce,
    enumerate_moves,
    free_reduce,
    hunt_defect,
    independent_defect,
    inverse,
    is_freely_reduced,
    make,
    sample_moves,
    scramble,
    search,
    stabilize_k,
    standard_presentation,
    triangulate,
    triangulation_certificate,
    verify_defect_zero,
)

AK3_PRES = make(*AK3)

#: a rank-2 AC-trivial member of AK(2)'s class, verdict NOT_SPHERICAL in
#: ``results/stable_ac/fable/ak2_members.jsonl``
AK2_MEMBER = make(("x", "y"), ("YYxxx", "YxYxYxxx"))

#: a state with a genuine defect-0 compatible rotation (connected link), found by this
#: module's own search from ``AK2_MEMBER`` and confirmed by the exact census below
GAMMA_ZERO_FIXTURE = make(("x", "y"), ("yXYXyX", "Yxy"))


# --------------------------------------------------------------------------------------
# word algebra
# --------------------------------------------------------------------------------------


def test_word_algebra_round_trips():
    for w in ("xyxYXY", "xxxYYYY", "a", "aYX", "YxYxYxxx"):
        assert free_reduce(w) == w
        assert inverse(inverse(w)) == w
        assert free_reduce(w + inverse(w)) == ""
    assert free_reduce("xXy") == "y"
    assert cyclic_reduce("xyX") == "y"
    assert cyclic_reduce("xyxXYX") == ""
    assert is_freely_reduced("xyx")
    assert not is_freely_reduced("xXy")


# --------------------------------------------------------------------------------------
# move legality
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("start", [AK3_PRES, AK2_MEMBER, standard_presentation(3)])
def test_every_enumerated_move_yields_a_legal_state(start):
    limits = Limits(max_relator_length=30, max_total_length=200, min_rank=1, max_rank=12)
    produced = 0
    for move in enumerate_moves(start):
        child = apply_move(start, move, limits)
        if child is None:
            continue
        produced += 1
        child.validate()                       # balanced, reduced, non-empty, in-alphabet
        assert child.balanced()
        assert all(r for r in child.rels)
        assert all(is_freely_reduced(r) for r in child.rels)
        assert child.rank == len(child.rels)
    assert produced > 20


def test_moves_respect_the_length_and_rank_limits():
    """``max_relator_length`` caps the relator a move REWRITES (a growth cap, so a start
    that already exceeds it is not frozen); ``max_total_length`` and the rank window are
    global properties of the child."""
    limits = Limits(max_relator_length=6, max_total_length=13, min_rank=2, max_rank=2)
    for move in enumerate_moves(AK3_PRES):
        child = apply_move(AK3_PRES, move, limits)
        if child is None:
            continue
        changed = [r for r, s in zip(child.rels, AK3_PRES.rels) if r != s]
        assert all(len(r) <= 6 for r in changed), (move, changed)
        assert child.total_length <= 13
        assert 2 <= child.rank <= 2
    # the rank ceiling forbids AC4 outright
    assert apply_move(AK3_PRES, ("ac4",), limits) is None
    assert apply_move(AK3_PRES, ("ac4",), Limits(max_rank=3)) is not None


def test_ac2_and_ac1_semantics():
    p = make(("x", "y"), ("xy", "yx"))
    assert apply_move(p, ("ac1", 0), Limits()).rels == ("YX", "yx")
    assert apply_move(p, ("ac2", 0, 1, 1), Limits()).rels == ("xyyx", "yx")
    assert apply_move(p, ("ac2", 0, 1, -1), Limits()).rels == ("xyXY", "yx")
    assert apply_move(p, ("ac3", 0, "x", 1), Limits()).rels == ("xxyX", "yx")
    assert apply_move(p, ("ac3", 0, "x", -1), Limits()).rels == ("yx", "yx")
    # the composite conjugated multiply is AC3;AC2;AC3-back
    got = apply_move(p, ("cmul", 0, 1, 1, "x", 1), Limits())
    assert got.rels == (free_reduce("xy" + free_reduce("x" + "yx" + "X")), "yx")


def test_a_move_producing_an_empty_relator_is_refused():
    p = make(("x", "y"), ("xy", "YX"))          # r2 = r1^-1
    assert apply_move(p, ("ac2", 0, 1, 1), Limits()) is None
    assert apply_move(p, ("ac2", 1, 0, 1), Limits()) is None


# --------------------------------------------------------------------------------------
# AC5 legality guard
# --------------------------------------------------------------------------------------


def test_ac5_is_legal_only_for_an_isolated_single_generator_relator():
    limits = Limits(min_rank=1, max_rank=6)
    good = make(("x", "y", "z"), ("xyxYXY", "xxxYYYY", "z"))
    got = apply_move(good, ("ac5", 2), limits)
    assert got is not None
    assert got.gens == ("x", "y")
    assert got.rels == ("xyxYXY", "xxxYYYY")

    # z occurs in another relator -> illegal
    bad = make(("x", "y", "z"), ("xyxYXYz", "xxxYYYY", "z"))
    assert apply_move(bad, ("ac5", 2), limits) is None
    bad2 = make(("x", "y", "z"), ("xyxYXY", "xxxYYYYZ", "z"))
    assert apply_move(bad2, ("ac5", 2), limits) is None

    # the relator is not a single generator -> illegal
    bad3 = make(("x", "y", "z"), ("xyxYXY", "xxxYYYY", "zx"))
    assert apply_move(bad3, ("ac5", 2), limits) is None

    # an inverse single-generator relator IS legal (Z^-1 is still the generator z)
    ok = make(("x", "y", "z"), ("xyxYXY", "xxxYYYY", "Z"))
    assert apply_move(ok, ("ac5", 2), limits) is not None

    # the rank floor forbids it
    assert apply_move(good, ("ac5", 2), Limits(min_rank=3, max_rank=6)) is None


def test_ac4_then_ac5_is_the_identity():
    up = apply_move(AK3_PRES, ("ac4",), Limits(max_rank=3))
    assert up.rank == 3
    down = apply_move(up, ("ac5", 2), Limits(min_rank=2, max_rank=3))
    assert down == AK3_PRES


def test_stabilize_k_is_ac4_repeated():
    for k in range(4):
        got = stabilize_k(AK3_PRES, k)
        assert got.rank == 2 + k
        assert got.rels[:2] == AK3_PRES.rels
        assert all(len(r) == 1 for r in got.rels[2:])
        assert abelian_invariant(got) == 1


# --------------------------------------------------------------------------------------
# group preservation
# --------------------------------------------------------------------------------------


def test_abelian_invariant_matches_hand_values():
    assert abelian_invariant(AK3_PRES) == 1
    assert abelian_invariant(standard_presentation(5)) == 1
    # <x, y | x^2, y^3> presents Z/2 x Z/3, |H_1| = 6
    assert abelian_invariant(make(("x", "y"), ("xx", "yyy"))) == 6
    # <x, y | x^2 y^2, x y> -- exponent matrix [[2, 2], [1, 1]] is singular
    assert abelian_invariant(make(("x", "y"), ("xxyy", "xy"))) == 0


@pytest.mark.parametrize("start", [AK3_PRES, AK2_MEMBER,
                                   make(("x", "y"), ("xx", "yyy"))])
def test_every_move_preserves_the_abelianisation(start):
    limits = Limits(max_relator_length=30, max_total_length=200, min_rank=1, max_rank=12)
    want = abelian_invariant(start)
    checked = 0
    for move in enumerate_moves(start):
        child = apply_move(start, move, limits)
        if child is None:
            continue
        assert abelian_invariant(child) == want, (move, child)
        checked += 1
    assert checked > 20


def test_todd_coxeter_confirms_group_preservation_on_small_cases():
    """A full Todd-Coxeter check on two presentations small enough to enumerate."""
    trivial = make(("x", "y"), ("x", "xyX"))         # trivial group
    assert is_trivial_group(trivial.rels, generators=trivial.gens)["trivial"] is True
    limits = Limits(max_relator_length=10, max_total_length=40, min_rank=1, max_rank=4)
    for move in enumerate_moves(trivial):
        child = apply_move(trivial, move, limits)
        if child is None:
            continue
        report = is_trivial_group(child.rels, generators=child.gens, cap=5_000)
        assert report["trivial"] is not False, (move, child, report)

    # AK(3) itself presents the trivial group; a random stable walk must keep it trivial
    rng = random.Random(4)
    cur = AK3_PRES
    for _ in range(12):
        got = sample_moves(cur, 1, rng, Limits(max_relator_length=14,
                                               max_total_length=40,
                                               min_rank=2, max_rank=5))
        if not got:
            continue
        cur = got[0][1]
        assert abelian_invariant(cur) == 1
    report = is_trivial_group(cur.rels, generators=cur.gens, cap=30_000)
    assert report["trivial"] is not False, (cur, report)


# --------------------------------------------------------------------------------------
# canonical key
# --------------------------------------------------------------------------------------


def test_canonical_key_is_invariant_under_rotation_inversion_and_renaming():
    a = make(("x", "y"), ("xyxYXY", "xxxYYYY"))
    rotated = make(("x", "y"), ("xYXYxy", "xYYYYxx"))
    inverted = make(("x", "y"), (inverse("xyxYXY"), "xxxYYYY"))
    swapped = make(("x", "y"), ("xxxYYYY", "xyxYXY"))
    renamed = make(("p", "q"), ("pqpQPQ", "pppQQQQ"))
    for other in (rotated, inverted, swapped, renamed):
        assert canonical_key(other) == canonical_key(a), other

    # conjugation is absorbed too (the key is on cyclically-reduced forms)
    conj = apply_move(a, ("ac3", 0, "x", 1), Limits())
    assert canonical_key(conj) == canonical_key(a)


def test_canonical_key_separates_genuinely_different_states():
    a = make(("x", "y"), ("xyxYXY", "xxxYYYY"))
    b = make(("x", "y"), ("xyxYXY", "xxYYYY"))
    assert canonical_key(a) != canonical_key(b)
    assert canonical_key(stabilize_k(a, 1)) != canonical_key(a)


# --------------------------------------------------------------------------------------
# triangulation helper
# --------------------------------------------------------------------------------------


def test_triangulation_reproduces_S1_section_4_4():
    tri, trace = triangulate(AK3_PRES)
    assert tri.rank == 9
    assert tri.balanced()
    assert set(tri.gens) == set("xyabcdefg")
    assert sorted(tri.rels) == sorted(
        ("cXY", "gYY", "aYX", "bXA", "cyB", "dXX", "eXD", "fyE", "gyF")
    )
    assert max(len(r) for r in tri.rels) == 3
    closed = {rec["gen"]: rec["word"] for rec in trace}
    assert closed == {"a": "xy", "b": "xyx", "c": "xyxY", "d": "xx", "e": "xxx",
                      "f": "xxxY", "g": "xxxYY"}
    cert = triangulation_certificate(AK3_PRES, tri, trace)
    assert cert["ok"] is True
    assert cert["peels"] == 7
    assert cert["definitions_vanished"] == 7
    assert cert["abelian_invariant_after"] == cert["abelian_invariant_before"] == 1


def test_triangulation_certificate_on_other_bases():
    for base in (AK2_MEMBER, make(("x", "y"), ("YXX", "YYxYXXyXX"))):
        tri, trace = triangulate(base)
        cert = triangulation_certificate(base, tri, trace)
        assert cert["ok"] is True
        assert cert["max_relator_length_after"] <= 3
        assert tri.rank == base.rank + len(trace)


def test_triangulation_defect_is_a_subdivision_invariant():
    """Theorem S3: a chord refinement cannot change the predicate ``gamma_N = 0``.

    Checked here in its strong measured form on AK(3): the exact census of the rank-9
    triangulation returns the SAME ``minimum_defect`` as AK(3) itself.  (This is a
    theorem, not a finding -- it is asserted here so that a regression in the
    triangulation helper is caught.)
    """
    tri, _trace = triangulate(AK3_PRES)
    base = RN.gamma_N_factorial_n(AK3_PRES.rels, generators=AK3_PRES.gens,
                                  cap_rotations=200_000, keep_accepting=False)
    got = RN.gamma_N_factorial_n(tri.rels, generators=tri.gens,
                                 cap_rotations=200_000, keep_accepting=False)
    assert base["status"] == got["status"] == "OK"
    assert base["minimum_defect"] == 4                    # gamma_N = 2
    assert got["minimum_defect"] == base["minimum_defect"]


# --------------------------------------------------------------------------------------
# the hunter
# --------------------------------------------------------------------------------------


def test_hunter_finds_a_known_gamma_zero_state():
    census = RN.gamma_N_factorial_n(GAMMA_ZERO_FIXTURE.rels,
                                    generators=GAMMA_ZERO_FIXTURE.gens,
                                    cap_rotations=200_000, keep_accepting=False)
    assert census["status"] == "OK"
    assert census["minimum_defect"] == 0                  # the fixture really is gamma_0
    rng = random.Random(0)
    defect, orders, _cache = hunt_defect(GAMMA_ZERO_FIXTURE, 4_000, rng)
    assert defect == 0
    report = verify_defect_zero(GAMMA_ZERO_FIXTURE, orders)
    assert report["verified"] is True
    assert report["check_witness_n"]["defect"] == 0
    assert report["check_witness_n"]["link_components"] == 1
    assert report["independent_defect"]["defect"] == 0
    assert report["exact_census"]["minimum_defect"] == 0
    assert "check_witness_n" in report["verified_by"]


def test_hunter_never_undershoots_the_exact_minimum():
    """The hunter bounds gamma_N from ABOVE: it can never report below the census."""
    rng = random.Random(1)
    for pres in (AK3_PRES, AK2_MEMBER, triangulate(AK3_PRES)[0]):
        census = RN.gamma_N_factorial_n(pres.rels, generators=pres.gens,
                                        cap_rotations=300_000, keep_accepting=False)
        if census["status"] != "OK":
            continue
        defect, _orders, _c = hunt_defect(pres, 3_000, rng)
        assert defect >= census["minimum_defect"], pres


def test_independent_defect_agrees_with_check_witness_n():
    rng = random.Random(2)
    defect, orders, _c = hunt_defect(GAMMA_ZERO_FIXTURE, 4_000, rng)
    assert defect == 0
    got = independent_defect(GAMMA_ZERO_FIXTURE, orders)
    assert got["defect"] == 0
    assert got["link_components"] == 1
    with pytest.raises(ValueError):
        broken = {k: list(v) for k, v in orders.items()}
        key = sorted(broken)[0]
        broken[key] = list(reversed(broken[key])) + [999]
        independent_defect(GAMMA_ZERO_FIXTURE, broken)


def test_standard_presentation_is_defect_zero_with_a_disconnected_link():
    """The standard presentation is thickenable but has one link component per generator,
    which is exactly the case ``check_witness_n`` refuses (it needs ``L = 1``)."""
    std = standard_presentation(4)
    rng = random.Random(3)
    defect, orders, cache = hunt_defect(std, 50, rng)
    assert defect == 0
    assert cache.link_components == 4
    report = verify_defect_zero(std, orders)
    assert report["verified"] is True
    assert report["check_witness_n"] is None
    assert "link has 4 components" in report["check_witness_n_error"]
    assert report["independent_defect"]["defect"] == 0


# --------------------------------------------------------------------------------------
# determinism
# --------------------------------------------------------------------------------------


def test_sample_moves_is_deterministic_under_a_fixed_seed():
    a = sample_moves(AK3_PRES, 10, random.Random(7), Limits())
    b = sample_moves(AK3_PRES, 10, random.Random(7), Limits())
    assert [m for m, _ in a] == [m for m, _ in b]
    c = sample_moves(AK3_PRES, 10, random.Random(8), Limits())
    assert [m for m, _ in a] != [m for m, _ in c]


def test_scramble_is_deterministic_under_a_fixed_seed():
    p1, h1 = scramble(standard_presentation(5), 8, random.Random(11))
    p2, h2 = scramble(standard_presentation(5), 8, random.Random(11))
    assert p1 == p2 and h1 == h2
    assert abelian_invariant(p1) == 1


def test_search_is_deterministic_under_a_fixed_seed():
    limits = Limits(max_relator_length=10, max_total_length=30, min_rank=2, max_rank=4)
    kwargs = dict(nodes=40, beam=3, branch=6, evals=200, seed=5, limits=limits,
                  time_budget=60.0)
    a = search(AK3_PRES, **kwargs)
    b = search(AK3_PRES, **kwargs)
    assert a.best_defect == b.best_defect
    assert a.best_state == b.best_state
    assert a.nodes_used == b.nodes_used
    assert a.rank_histogram == b.rank_histogram
    assert a.hit == b.hit


# --------------------------------------------------------------------------------------
# the search end to end
# --------------------------------------------------------------------------------------


def test_search_only_ever_reports_a_verified_hit():
    limits = Limits(max_relator_length=10, max_total_length=30, min_rank=2, max_rank=3)
    result = search(AK2_MEMBER, nodes=120, beam=4, branch=8, evals=400, seed=1,
                    limits=limits, time_budget=90.0)
    assert result.nodes_used <= 120
    assert result.best_defect is not None and result.best_defect >= 0
    if result.hit:
        assert result.verification is not None
        assert result.verification["verified"] is True
        assert result.best_defect == 0
    assert result.anomalies == []


def test_search_states_stay_in_the_stable_class():
    """Every state the search visits must remain balanced with the same abelianisation."""
    limits = Limits(max_relator_length=10, max_total_length=30, min_rank=2, max_rank=4)
    result = search(AK3_PRES, nodes=60, beam=3, branch=6, evals=200, seed=2,
                    limits=limits, time_budget=60.0)
    best = Pres(tuple(result.best_state["gens"]), tuple(result.best_state["rels"]))
    best.validate()
    assert abelian_invariant(best) == 1
    assert limits.min_rank <= best.rank <= limits.max_rank


def test_search_on_ak3_at_rank_two_cannot_report_a_hit_it_has_not_verified():
    """AK(3) is the open case; the search must come back honest, whatever it finds."""
    limits = Limits(max_relator_length=9, max_total_length=20, min_rank=2, max_rank=2)
    result = search(AK3_PRES, nodes=60, beam=3, branch=6, evals=300, seed=3,
                    limits=limits, time_budget=60.0)
    assert result.stopped in {"node_budget", "time_budget", "frontier_exhausted",
                              "no_scored_children", "verified_hit"}
    if result.hit:                                      # would be a headline result
        assert result.verification["verified"] is True
    else:
        assert result.best_defect is None or result.best_defect > 0


# --------------------------------------------------------------------------------------
# the S6 measured move table (S6_MOVE_CLASSIFICATION.md section 1) drives these
# --------------------------------------------------------------------------------------


def test_move_weights_follow_the_measured_flip_table():
    """S6 row M2: bare AC3 conjugation is 315 destroys / 0 creates of 3,507; rows M3
    (AC2) are the only slides measured to CREATE gamma_N = 0.  The sampler must not be
    spending its budget on the counterproductive move."""
    w = DEFAULT_KIND_WEIGHTS
    assert w["ac3"] < w["ac2"]
    assert w["ac3"] < w["cmul"]
    assert w["ac3"] <= 0.5
    assert w["ac2"] + w["cmul"] > 3 * sum(v for k, v in w.items()
                                          if k not in ("ac2", "cmul"))


def test_ac3_sampler_prefers_a_cancelling_conjugation():
    """S6 row M2c: conjugation WITH cancellation is inert (0 flips of 3,413)."""
    p = make(("x", "y"), ("Xyyx", "xyxYXY"))       # r1 starts with X and ends with x
    rng = random.Random(0)
    for _ in range(20):
        move = RNS._cancelling_ac3(p, 0, rng)
        child = apply_move(p, move, Limits())
        assert child is not None
        assert len(child.rels[0]) < len(p.rels[0]) + 2, move
    # a cyclically reduced relator with no repeated end letters has no cancelling option
    q = make(("x", "y"), ("xy", "yx"))
    move = RNS._cancelling_ac3(q, 0, rng)
    assert move[0] == "ac3"


def test_cyclically_reduce_pres_is_move_zero():
    """S6 row M0: reduction creates gamma_N = 0 in 315 of 2,510 and destroys it in 0 of
    997, so the search applies it to every child."""
    p = Pres(("x", "y"), ("xyxYXYX", "xxxYYYY"))   # r1 = x . (xyxYXY) . x^-1
    got = cyclically_reduce_pres(p)
    assert got.rels == ("xyxYXY", "xxxYYYY")
    assert got.gens == p.gens
    # a relator that reduces away entirely makes the state illegal
    assert cyclically_reduce_pres(Pres(("x", "y"), ("xX" and "xyXY", "xY"))) is not None
    assert cyclically_reduce_pres(Pres(("x", "y"), ("xyxXYX", "xy"))) is None


def test_stabilizer_entanglement_gate_matches_theorem_T4_prime():
    """T4': a fresh stabilizer's first slide is a subdivision, so gamma_N cannot move
    while the new generator is still a chord."""
    base = ("x", "y")
    # z occurs twice, in two relators: still a chord
    chordal = make(("x", "y", "z"), ("xyxYXYz", "xxxYYYY", "Z"))
    assert stabilizer_entangled(chordal, base) is False
    # z occurs three times but only in one relator plus its own: not yet entangled
    one_relator = make(("x", "y", "z"), ("xyzxzYXY", "xxxYYYY", "Z"))
    assert stabilizer_entangled(one_relator, base) is False
    # three occurrences spread over two relators: entangled
    entangled = make(("x", "y", "z"), ("xyzxzYXY", "xxxYYYYz", "xxyyz"))
    assert stabilizer_entangled(entangled, base) is True
    # a state with no stabilizers at all is never entangled
    assert stabilizer_entangled(AK3_PRES, base) is False


def test_search_scores_only_cyclically_reduced_states_by_default():
    limits = Limits(max_relator_length=10, max_total_length=30, min_rank=2, max_rank=4)
    result = search(AK2_MEMBER, nodes=60, beam=3, branch=8, evals=300, seed=9,
                    limits=limits, time_budget=60.0)
    best = Pres(tuple(result.best_state["gens"]), tuple(result.best_state["rels"]))
    for r in best.rels:
        assert cyclic_reduce(r) == r, best
    assert result.budget["reduce_children"] is True
    assert result.budget["entangle_first"] is True
    assert result.entangled_scored >= 0


def test_entangle_first_never_starves_the_search():
    """The T4' priority is a priority, not a gate: a start with no entangled child at
    all must still get its full node budget."""
    limits = Limits(max_relator_length=10, max_total_length=30, min_rank=2, max_rank=3)
    a = search(AK3_PRES, nodes=50, beam=3, branch=8, evals=200, seed=13, limits=limits,
               time_budget=60.0, entangle_first=True)
    b = search(AK3_PRES, nodes=50, beam=3, branch=8, evals=200, seed=13, limits=limits,
               time_budget=60.0, entangle_first=False)
    assert a.nodes_used >= 40 and b.nodes_used >= 40
