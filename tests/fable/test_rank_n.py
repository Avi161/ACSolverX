"""Calibration suite for the rank-n Neuwirth stack (R1c: 3-connected planar supports).

Covers ``experiments/stable_ac/fable/neuwirth_rank_n.py`` (the decision procedure),
``witness_check_n.py`` (the independent rank-generic verifier) and
``rank3_stable_harvest.py`` (round 1 of the stable-move search).

Every number asserted here is either read from the committed fixture file
``results/stable_ac/theory/fable/rank3_census_fixtures.json`` or recomputed inside the
test.  Nothing depends on a scratch directory.

DOCUMENTED DEVIATION.  The task asked for "all 8 NO fixtures -> NOT_SPHERICAL".  One of
them, ``("ZY", "xzXZxYY")``, carries a relator of length 2, which the fail-closed
boundary of R1c (and of the rank-2 stack before it) turns into ``UNSUPPORTED`` -- the
gate is checked before any support analysis and outranks the verdict, exactly as
specified ("any relator < 3 letters => UNSUPPORTED (never NO)").  The test therefore
asserts ``UNSUPPORTED`` for that one and additionally reproduces its full recorded
census from scratch, so the NO it records is still confirmed, just not by the scheme
solver.  The other seven are ``NOT_SPHERICAL``.
"""

from __future__ import annotations

import itertools
import json
import os

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import neuwirth_core as NC
from experiments.stable_ac.fable import neuwirth_rank as NR
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable import rank3_stable_harvest as HV
from experiments.stable_ac.fable import witness_check_n as WCN

from helpers_fable import small_batch  # noqa: E402  (tests/fable is on sys.path)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE_PATH = os.path.join(
    REPO_ROOT, "results", "stable_ac", "theory", "fable", "rank3_census_fixtures.json"
)

RANK3_GENERATORS = ("x", "y", "z")
T3 = ("xyXY", "yzYZ", "zxZX")
SHORT_RELATOR_FIXTURE = ("ZY", "xzXZxYY")


def _fixtures():
    with open(FIXTURE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


FIXTURES = _fixtures()
NO_FIXTURES = [f for f in FIXTURES if f["n_accepting"] == 0]
YES_FIXTURES = [f for f in FIXTURES if f["n_accepting"] > 0]


def _recorded_histogram(fixture) -> dict:
    return {int(k): v for k, v in fixture["defect_histogram"].items()}


def _named_graph(edges):
    vertices = tuple(sorted({v for e in edges for v in e}))
    es = tuple(sorted(tuple(sorted(e)) for e in edges))
    adj = {v: [] for v in vertices}
    for u, v in es:
        adj[u].append(v)
        adj[v].append(u)
    adj = {v: tuple(sorted(ws)) for v, ws in adj.items()}
    return vertices, es, adj


K4_EDGES = list(itertools.combinations(range(4), 2))
OCTAHEDRON_EDGES = [(u, v) for u, v in itertools.combinations(range(6), 2)
                    if v - u != 3 or u >= 3]
CUBE_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
              (0, 4), (1, 5), (2, 6), (3, 7)]
PRISM_EDGES = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]
K5_EDGES = list(itertools.combinations(range(5), 2))
K33_EDGES = [(i, j) for i in range(3) for j in range(3, 6)]
PETERSEN_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (5, 7), (7, 9), (9, 6),
                  (6, 8), (8, 5), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]


# =====================================================================================
# 0. the rank-n dictionary specialises to the rank-2 one, bit for bit
# =====================================================================================


def test_build_link_n_reproduces_the_rank_2_dictionary_exactly():
    """At rank 2 the generalised builder must be the old builder, field for field."""
    sample = [p for i, p in enumerate(small_batch(7)) if i % 47 == 0]
    assert len(sample) >= 200
    for pair in sample:
        a = NC.build_link(pair)
        b = RN.build_link_n(pair)
        assert a == b, pair
    assert RN.germ_names(("x", "y")) == NC.GERM_NAMES


def test_factorial_census_n_reproduces_the_rank_2_census():
    sample = [p for i, p in enumerate(small_batch(7)) if i % 173 == 0]
    assert len(sample) >= 100
    for pair in sample:
        a = NC.gamma_N_factorial(pair, keep_accepting=False)
        b = RN.gamma_N_factorial_n(pair, keep_accepting=False)
        assert a["status"] == b["status"] == "OK"
        assert a["expected_cases"] == b["expected_cases"]
        assert a["defect_histogram"] == b["defect_histogram"]
        assert a["minimum_defect"] == b["minimum_defect"]
        assert a["link_components"] == b["link_components"]


# =====================================================================================
# 1. the T^3 YES fixture: octahedral support, exactly two Whitney reflections
# =====================================================================================


def test_octahedron_macro_enumeration_has_exactly_two_genus_zero_rotations():
    """The macro layer, exercised on the bare graph (no words involved)."""
    vertices, edges, adj = _named_graph(OCTAHEDRON_EDGES)
    assert len(vertices) == 6 and len(edges) == 12
    assert all(len(adj[v]) == 4 for v in vertices)
    assert RN.is_three_connected(vertices, adj) == (True, None)

    macro = RN.macro_rotations(vertices, edges, adj)
    assert macro.status == RN.PLANAR
    assert macro.family_size == 6 ** 6 == 46_656
    assert macro.enumerated == macro.family_size
    assert macro.genus0_count == 2, "Whitney: a 3-connected planar simple graph has 2"
    assert macro.reflections_verified
    # and the two really are vertex-wise reversals, recomputed here
    first, second = macro.rotations[0], macro.rotations[1]
    for v in vertices:
        rev = tuple(reversed(first[v]))
        assert any(rev[i:] + rev[:i] == second[v] for i in range(len(rev)))


@pytest.mark.parametrize("edges,name,expected", [
    (K4_EDGES, "K4", 2),
    (OCTAHEDRON_EDGES, "octahedron", 2),
    (CUBE_EDGES, "cube", 2),
    (PRISM_EDGES, "prism", 2),
])
def test_three_connected_planar_graphs_have_exactly_two_reflections(edges, name,
                                                                    expected):
    vertices, es, adj = _named_graph(edges)
    assert RN.is_three_connected(vertices, adj)[0], name
    macro = RN.macro_rotations(vertices, es, adj)
    assert macro.status == RN.PLANAR, name
    assert macro.genus0_count == expected, name
    assert macro.reflections_verified, name


def test_t3_is_spherical_and_the_witness_survives_the_independent_verifier():
    fixture = YES_FIXTURES[0]
    assert tuple(fixture["words"]) == T3
    support = RN.classify_support_n(T3, RANK3_GENERATORS)
    assert support.kind == "3CONN_PLANAR"
    assert support.three_connected is True and support.planar is True
    assert len(support.vertices) == 6 and len(support.edges) == 12
    assert dict(support.simple_degrees) == {g: 4 for g in RN.germ_names(RANK3_GENERATORS)}
    assert support.macro.genus0_count == 2 and support.macro.family_size == 46_656
    # every parallel class is a single edge, so Theorem R's count is 2 * prod m_uv! = 2
    assert all(m == 1 for _key, m in support.multiplicities)

    decision = RN.solve_spherical_n(T3, RANK3_GENERATORS)
    assert decision.verdict == RN.SPHERICAL
    assert decision.spherical is True
    assert decision.witness is not None
    assert decision.witness.defect == 0 and decision.witness.genus == 0
    assert decision.witness.link_components == 1
    assert decision.witness.euler_characteristic == 2
    assert decision.witness.compatibility_verified

    report = WCN.check_rank_n_witness(decision, trivial_group=False)
    assert report["defect"] == 0
    assert report["link_components"] == 1
    assert report["euler_characteristic"] == 2
    assert report["cycles_C"] == 6 and report["cycles_A"] == 12
    assert report["generators"] == RANK3_GENERATORS

    census = RN.gamma_N_factorial_n(T3, RANK3_GENERATORS)
    assert census["expected_cases"] == fixture["expected_cases"] == 216
    assert census["defect_histogram"] == _recorded_histogram(fixture)
    assert census["minimum_genus"] == fixture["minimum_genus"] == 0
    assert len(census["accepting_orders"]) == fixture["n_accepting"] == 2


def test_t3_verdict_does_not_depend_on_which_reflection_is_fixed():
    """Theorem P: fixing either macro reflection loses no compatible solution."""
    for index in (0, 1):
        decision = RN.solve_spherical_n(T3, RANK3_GENERATORS, macro_index=index)
        assert decision.verdict == RN.SPHERICAL, index
        assert decision.witness.macro_index == index
        WCN.check_rank_n_witness(decision, trivial_group=False)


def test_t3_witness_is_one_of_the_two_accepting_census_orders():
    """The scheme solver's YES must be an element of the factorial ground truth."""
    census = RN.gamma_N_factorial_n(T3, RANK3_GENERATORS)
    accepting = {
        tuple(sorted((name, tuple(seq)) for name, seq in order.items()))
        for order in census["accepting_orders"]
    }
    assert len(accepting) == 2
    for index in (0, 1):
        witness = RN.solve_spherical_n(T3, RANK3_GENERATORS,
                                       macro_index=index).witness
        # rotations are cyclic orders; normalise each by rotating its minimum to front
        found = False
        for order in accepting:
            if all(_same_cycle(dict(order)[name], seq)
                   for name, seq in witness.rotations):
                found = True
                break
        assert found, (index, witness.rotations, accepting)


def _same_cycle(a, b) -> bool:
    a, b = tuple(a), tuple(b)
    if len(a) != len(b):
        return False
    return any(a[i:] + a[:i] == b for i in range(len(a)))


# =====================================================================================
# 2. the eight NO fixtures
# =====================================================================================


@pytest.mark.parametrize("fixture", NO_FIXTURES,
                         ids=[".".join(f["words"]) for f in NO_FIXTURES])
def test_no_fixtures_are_never_spherical(fixture):
    words = tuple(fixture["words"])
    decision = RN.solve_spherical_n(words, RANK3_GENERATORS)
    assert decision.verdict != RN.SPHERICAL
    assert decision.witness is None
    if words == SHORT_RELATOR_FIXTURE:
        # documented deviation: the degenerate-relator gate fires before any support
        # analysis and must fail closed, never NO.
        assert decision.verdict == RN.UNSUPPORTED
        assert "length 2" in decision.reason
        return
    assert decision.verdict == RN.NOT_SPHERICAL
    assert decision.spherical is False
    assert decision.support.kind in ("3CONN_PLANAR", "NONPLANAR")
    if decision.support.kind == "3CONN_PLANAR":
        assert decision.counters.exhaustive
        assert (decision.counters.phase_tuples_considered
                == decision.counters.phase_tuple_budget)
        assert (decision.counters.component_seed_attempts
                == decision.counters.component_seed_budget)
        assert decision.counters.phase_tuple_budget > 0
        assert decision.support.macro.genus0_count == 2


@pytest.mark.parametrize("fixture", FIXTURES,
                         ids=[".".join(f["words"]) for f in FIXTURES])
def test_own_factorial_census_reproduces_every_recorded_histogram(fixture):
    """Independent re-run of the census for all nine fixtures (>= 2 was required)."""
    words = tuple(fixture["words"])
    census = RN.gamma_N_factorial_n(words, RANK3_GENERATORS)
    assert census["status"] == "OK"
    assert census["expected_cases"] == fixture["expected_cases"]
    assert census["enumerated_cases"] == fixture["expected_cases"]
    assert census["defect_histogram"] == _recorded_histogram(fixture)
    assert sum(census["defect_histogram"].values()) == fixture["expected_cases"]
    assert census["minimum_genus"] == fixture["minimum_genus"]
    assert len(census["accepting_orders"]) == fixture["n_accepting"]
    assert [census["link_components"]] == fixture["link_components"]
    if "degrees" in fixture:
        assert census["degrees"] == fixture["degrees"]


@pytest.mark.parametrize("fixture", NO_FIXTURES,
                         ids=[".".join(f["words"]) for f in NO_FIXTURES])
def test_no_fixture_census_agrees_with_the_solver_verdict(fixture):
    words = tuple(fixture["words"])
    census = RN.gamma_N_factorial_n(words, RANK3_GENERATORS, keep_accepting=False)
    assert census["minimum_defect"] > 0
    assert fixture["minimum_genus"] >= 1


# =====================================================================================
# 3. rank-2 regression: on K_4 supports the two solvers must decide identically
# =====================================================================================

K4_PAIRS = tuple(p for p in small_batch(7) if NR.classify_support(p).kind == "K4")


def test_rank_n_solver_agrees_with_the_rank_2_solver_on_every_k4_pair():
    """K_4 is 3-connected planar, so both theorems apply and must agree."""
    assert len(K4_PAIRS) >= 200
    yes_2, yes_n, disagreements = set(), set(), []
    for pair in K4_PAIRS:
        two = NR.solve_spherical(pair)
        many = RN.solve_spherical_n(pair)
        assert many.support.kind == "3CONN_PLANAR", pair
        assert many.support.macro.genus0_count == 2, pair
        assert many.verdict in (RN.SPHERICAL, RN.NOT_SPHERICAL), pair
        if two.verdict == NR.SPHERICAL:
            yes_2.add(pair)
        if many.verdict == RN.SPHERICAL:
            yes_n.add(pair)
            WCN.check_rank_n_witness(many, trivial_group=False)
        if two.verdict != many.verdict:
            disagreements.append((pair, two.verdict, many.verdict))
    assert disagreements == []
    assert yes_2 == yes_n
    assert len(yes_n) == 528, "the sample must contain YES cases"
    assert len(K4_PAIRS) - len(yes_n) == 384
    assert len(K4_PAIRS) == 912


def test_rank_n_solver_fails_closed_on_the_rank_2_supports_the_theorem_excludes():
    """``K_4 - e`` and ``C_4`` are not 3-connected, so R1c must decline them."""
    seen = {"K4-e": 0, "C4": 0}
    for pair in small_batch(7):
        kind = NR.classify_support(pair).kind
        if kind not in seen or seen[kind] >= 40:
            continue
        seen[kind] += 1
        decision = RN.solve_spherical_n(pair)
        assert decision.verdict == RN.UNSUPPORTED, (pair, kind)
        assert decision.witness is None
        assert decision.support.three_connected is False
    assert seen == {"K4-e": 40, "C4": 40}


# =====================================================================================
# 4. the fail-closed boundary
# =====================================================================================

FAIL_CLOSED = [
    (("XXY", "XXy"), None, "2-cut", "K4-e support (2-cut)"),
    (("xxxYYYY", "xyxYXY", "z"), RANK3_GENERATORS, "length 1",
     "plain stabilisation: the z relator is one letter"),
    (("xxxYYYY", "xyxYXY", "zxxxYYYY"), RANK3_GENERATORS, "simple degree < 3",
     "stabilised state whose z germs have simple degree 1"),
    (("xyXY", "yzYZ", "zxZXxX"), RANK3_GENERATORS, "loop",
     "loopy exact realisation (the corner Xx)"),
    (("xyXY", "yzYZ", "zxZXXx"), RANK3_GENERATORS, "loop",
     "loopy exact realisation (the corner Xx, single loop edge)"),
    (("xyXY", "yxYX", "zzz"), RANK3_GENERATORS, "2 components",
     "z isolated in its own link component"),
]


@pytest.mark.parametrize("words,generators,needle,label", FAIL_CLOSED,
                         ids=[c[3] for c in FAIL_CLOSED])
def test_fail_closed_cases_return_unsupported(words, generators, needle, label):
    decision = RN.solve_spherical_n(words, generators)
    assert decision.verdict == RN.UNSUPPORTED, label
    assert decision.spherical is None
    assert decision.witness is None
    assert needle in decision.reason, (label, decision.reason)


def test_absent_generator_is_unsupported_not_no():
    """A stabilising generator that has been moved out of every relator."""
    decision = RN.solve_spherical_n(("xyXY", "yxYX", "xyxYXY"), RANK3_GENERATORS)
    assert decision.verdict == RN.UNSUPPORTED
    assert "z+" in decision.reason and "do not occur" in decision.reason


def test_certified_non_planar_support_is_a_real_no_at_rank_3():
    """S non-planar kills every rotation system; the certificate is exhaustive here."""
    words = ("xyXY", "yzYZ", "zxxZYY")
    decision = RN.solve_spherical_n(words, RANK3_GENERATORS)
    assert decision.verdict == RN.NOT_SPHERICAL
    assert decision.support.kind == "NONPLANAR"
    assert decision.support.planar is False
    assert decision.counters.exhaustive
    certificate = decision.support.macro.certificate
    assert "found none of genus 0" in certificate
    census = RN.gamma_N_factorial_n(words, RANK3_GENERATORS, keep_accepting=False)
    assert census["minimum_defect"] > 0


@pytest.mark.parametrize("edges,name", [(K5_EDGES, "K5"), (K33_EDGES, "K3,3"),
                                        (PETERSEN_EDGES, "Petersen")])
def test_non_planar_graphs_are_certified_non_planar(edges, name):
    vertices, es, adj = _named_graph(edges)
    macro = RN.macro_rotations(vertices, es, adj)
    assert macro.status == RN.NONPLANAR, name
    assert macro.genus0_count == 0, name
    assert macro.certificate


def test_macro_budget_refusal_is_unsupported_not_no():
    """A macro family over budget must fail closed, never become a verdict."""
    vertices, edges, adj = _named_graph(OCTAHEDRON_EDGES)
    macro = RN.macro_rotations(vertices, edges, adj, budget=100)
    assert macro.status == RN.UNDETERMINED
    assert macro.enumerated == 0
    decision = RN.solve_spherical_n(T3, RANK3_GENERATORS, macro_budget=100)
    assert decision.verdict == RN.UNSUPPORTED
    assert "undetermined" in decision.reason


def test_two_cut_control_confirms_h2_is_load_bearing():
    """C_4 has a single genus-0 rotation system, so the Whitney count 2 needs (H2)."""
    vertices, edges, adj = _named_graph([(0, 1), (1, 2), (2, 3), (3, 0)])
    assert RN.is_three_connected(vertices, adj)[0] is False
    macro = RN.macro_rotations(vertices, edges, adj)
    assert macro.status == RN.PLANAR
    assert macro.genus0_count == 1
    assert macro.reflections_verified is False


# =====================================================================================
# 5. Todd-Coxeter controls at rank 3 (coset_enum was already alphabet-generic)
# =====================================================================================


def test_tc_trivial_presentation_at_rank_three():
    result = CE.is_trivial_group(("x", "y", "z"), generators=RANK3_GENERATORS)
    assert result["status"] == CE.COMPLETE
    assert result["index"] == 1
    assert result["trivial"] is True


def test_tc_infinite_presentation_at_rank_three_hits_the_cap():
    result = CE.is_trivial_group(("xyz",), generators=RANK3_GENERATORS, cap=400)
    assert result["status"] == CE.CAP_EXCEEDED
    assert result["index"] is None
    assert result["trivial"] is None


def test_tc_finite_nontrivial_control_at_rank_three():
    result = CE.is_trivial_group(("xx", "y", "z"), generators=RANK3_GENERATORS)
    assert result["status"] == CE.COMPLETE
    assert result["index"] == 2
    assert result["trivial"] is False


def test_t3_is_not_the_trivial_group():
    """Z^3 must not be certified trivial (the YES fixture is not an AC certificate)."""
    result = CE.is_trivial_group(T3, generators=RANK3_GENERATORS, cap=3_000)
    assert result["trivial"] is not True


# =====================================================================================
# 6. witness_check_n
# =====================================================================================


def test_witness_check_n_rejects_a_corrupted_rank_3_witness():
    decision = RN.solve_spherical_n(T3, RANK3_GENERATORS)
    rotation = {name: list(seq) for name, seq in decision.witness.rotations}
    victim = sorted(rotation)[0]
    rotation[victim] = rotation[victim][:2][::-1] + rotation[victim][2:]
    with pytest.raises((WCN.WitnessError, WCN.AuditContradiction)):
        WCN.check_witness_n(T3, rotation, generators=RANK3_GENERATORS,
                            trivial_group=False)


def test_witness_check_n_rejects_a_dart_set_that_is_not_the_germ():
    decision = RN.solve_spherical_n(T3, RANK3_GENERATORS)
    rotation = {name: list(seq) for name, seq in decision.witness.rotations}
    a, b = sorted(rotation)[0], sorted(rotation)[1]
    rotation[a][0], rotation[b][0] = rotation[b][0], rotation[a][0]
    with pytest.raises(WCN.WitnessError):
        WCN.check_witness_n(T3, rotation, generators=RANK3_GENERATORS,
                            trivial_group=False)


def test_witness_check_n_accepts_germ_indices_as_well_as_names():
    decision = RN.solve_spherical_n(T3, RANK3_GENERATORS)
    by_index = decision.witness.rotation_index_map()
    report = WCN.check_witness_n(T3, by_index, generators=RANK3_GENERATORS,
                                 trivial_group=False)
    assert report["defect"] == 0


def test_witness_check_n_audit_contradiction_is_gated_on_triviality():
    """The Corollary 3 subtlety, at rank 3: a non-trivial group may have L(AC,BC) > 1."""
    census = RN.gamma_N_factorial_n(T3, RANK3_GENERATORS)
    order = census["accepting_orders"][0]
    orbits = WCN.ac_bc_orbit_count_n(T3, order, generators=RANK3_GENERATORS)
    assert orbits >= 1
    report = WCN.check_witness_n(T3, order, generators=RANK3_GENERATORS,
                                 trivial_group=False)
    assert report["ac_bc_orbits"] == orbits
    assert report["trivial_group_assumed"] is False


def test_witness_check_n_shares_no_solver_code():
    """The verifier must not be able to inherit a scheme bug from the solver."""
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(WCN))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not any("neuwirth" in name for name in imported), imported
    assert imported == {"experiments.stable_ac.fable.witness_check", "__future__"}


def test_witness_check_n_verifies_every_rank_2_yes_in_the_k4_family():
    """Rank-3 coverage is the point, but rank-2 witnesses must still pass."""
    checked = 0
    for pair in K4_PAIRS[::4]:
        decision = RN.solve_spherical_n(pair)
        if decision.verdict != RN.SPHERICAL:
            continue
        report = WCN.check_rank_n_witness(decision, trivial_group=False)
        assert report["defect"] == 0 and report["link_components"] == 1
        checked += 1
    assert checked >= 50


# =====================================================================================
# 7. the rank-3 stable harvest
# =====================================================================================


def test_harvest_letter_order_specialises_to_the_rank_2_solver_order():
    assert HV.letter_order(("x", "y")) == {"Y": 0, "y": 1, "X": 2, "x": 3}
    assert HV.letter_order(("x", "y", "z")) == {
        "Z": 0, "z": 1, "Y": 2, "y": 3, "X": 4, "x": 5,
    }


def test_harvest_canonical_forms_specialise_to_ac_words():
    order = HV.letter_order(("x", "y"))
    sample = [p for i, p in enumerate(small_batch(7)) if i % 31 == 0]
    assert len(sample) >= 200
    for a, b in sample:
        assert HV.canon_relator(a, order) == W.canon_rel(a)
        assert HV.canon_relator(b, order) == W.canon_rel(b)
        assert HV.canon_state((a, b), order) == W.canon_pair(a, b)


def test_harvest_canonical_key_is_a_conjugacy_and_permutation_invariant():
    order = HV.letter_order(HV.GENERATORS)
    state = ("xxxYYYY", "xyxYXY", "z")
    key = HV.canon_state(state, order)
    assert HV.canon_state(state[::-1], order) == key
    conj = (W.free_reduce("x" + state[0] + "X"), state[1], state[2])
    assert HV.canon_state(conj, order) == key
    inv = (W.inverse(state[0]), state[1], state[2])
    assert HV.canon_state(inv, order) == key


def test_harvest_move_generator_respects_the_cap_and_stays_reduced():
    state = ("xxxYYYY", "xyxYXY", "z")
    children = list(HV.moves(state))
    assert children
    labels = {label for label, _ in children}
    assert any(label.startswith("AC1") for label in labels)
    assert any(label.startswith("AC3") for label in labels)
    for _label, child in children:
        assert len(child) == 3
        for word in child:
            assert word
            assert len(word) <= HV.RELATOR_CAP
            assert W.is_freely_reduced(word)
        assert sum(a != b for a, b in zip(child, state)) == 1


def test_ac3_conjugation_children_are_canonical_duplicates():
    """Recorded finding: under reduced keying every AC3 child is already seen."""
    order = HV.letter_order(HV.GENERATORS)
    state = ("xxxYYYY", "xyxYXY", "z")
    parent = HV.canon_state(state, order)
    conjugations = [c for label, c in HV.moves(state) if label.startswith("AC3")]
    assert conjugations
    assert all(HV.canon_state(c, order) == parent for c in conjugations)


def test_harvest_root_search_is_deterministic_and_canonically_deduplicated():
    order = HV.letter_order(HV.GENERATORS)
    first = HV.harvest_root("AK3+z", HV.ROOTS[0][1], pops=25)
    second = HV.harvest_root("AK3+z", HV.ROOTS[0][1], pops=25)
    assert set(first["states"]) == set(second["states"])
    assert first["pops"] == 25
    for key, record in first["states"].items():
        assert key == HV.canon_state(key, order)
        assert HV.canon_state(record.exact, order) == key


def test_harvest_p25_component_is_frozen_by_the_relator_cap():
    """Recorded finding: P25's 13/12-letter relators barely move under cap 15."""
    result = HV.harvest_root("P25+z", HV.ROOTS[1][1], pops=HV.POPS_PER_ROOT)
    assert result["queue_exhausted"]
    assert result["pops"] < HV.POPS_PER_ROOT
    assert result["distinct_states"] == 93


def test_harvest_round_smoke(tmp_path):
    out = str(tmp_path / "round.jsonl")
    result = HV.run_round(pops=12, output=out, fallback_cap=200_000,
                          fallback_total_budget=400_000, verbose=False)
    summary = result["summary"]
    assert summary["distinct_states"] == len(result["rows"])
    assert summary["distinct_states"] > 0
    assert summary["spherical_states"] == []
    assert sum(summary["verdict_histogram"].values()) == summary["distinct_states"]
    assert sum(summary["gate_histogram"].values()) == summary["distinct_states"]
    assert summary["fallback_spent"] <= 400_000
    with open(out, encoding="utf-8") as fh:
        lines = [json.loads(line) for line in fh]
    assert lines[0]["record"] == "summary"
    assert len(lines) == summary["distinct_states"] + 1
    for row in lines[1:]:
        assert row["record"] == "state"
        assert row["verdict"] in (RN.SPHERICAL, RN.NOT_SPHERICAL, RN.UNSUPPORTED,
                                  HV.UNDECIDED_BUDGET)
        assert row["gate"] in HV.GATE_ORDER
        assert row["verdict"] != RN.SPHERICAL


def test_plain_stabilisation_has_a_disconnected_link():
    """``(r1, r2, "z")`` puts the z germs in their own component: never a YES."""
    words = tuple(HV.AK3) + ("z",)
    support = HV.classify_only(words)
    assert support.kind == "UNSUPPORTED"
    assert support.data.link_components == 2
    assert HV.census_family_size(words) == 86_400
    verdict = HV.decide_by_census(words, support)
    assert verdict.verdict == RN.UNSUPPORTED
    assert verdict.method == "factorial_census"
    assert verdict.census["link_components"] == 2
    assert "2 components" in verdict.support_reason


def test_harvest_census_fallback_decides_a_connected_out_of_scope_state():
    """A harvested state out of scope for R1c is still settled by the exact census."""
    words = ("Z", "YXYxyx", "ZxxxYYYY")     # reached from AK3+z by r3 <- r3 . r1^-1
    support = HV.classify_only(words)
    assert support.kind == "UNSUPPORTED"
    assert support.data.link_components == 1
    assert HV.census_family_size(words) == 86_400
    verdict = HV.decide_by_census(words, support)
    assert verdict.verdict == RN.NOT_SPHERICAL
    assert verdict.method == "factorial_census"
    assert verdict.census["minimum_defect"] > 0
    assert verdict.census["link_components"] == 1


def test_harvest_gate_categories_cover_the_fail_closed_boundary():
    cases = {
        ("xxxYYYY", "xyxYXY", "z"): "relator shorter than 3",
        ("xxxYYYY", "xyxYXY", "zxxxYYYY"): "simple degree < 3",
        ("xyXY", "yzYZ", "zxZXxX"): "A-loop",
        ("xyXY", "yzYZ", "zxxZYY"): "certified non-planar S",
        T3: "IN SCOPE (3-connected planar)",
        ("xyXY", "yxYX", "xyxYXY"): "generator absent from every relator",
    }
    for words, expected in cases.items():
        support = HV.classify_only(words)
        assert HV.gate_category(words, support) == expected, words
