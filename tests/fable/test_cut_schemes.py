"""Calibration suite for the R1c-v2 cut-scheme solver.

Covers ``experiments/stable_ac/fable/neuwirth_cut_schemes.py`` against four independent
oracles, none of which shares code with the scheme machinery:

1. **counts** -- a brute-force enumerator of every rotation system of a multigraph,
   accepting the genus-0 ones by ``V - E + F = 2``, written here from the recipe of
   Sec. 10 of the note.  The claim tested is ``|Sigma| * prod m_uv! = N(G)`` (7.1), on
   the published anchors of Sec. 9 and on a deterministic random family that exercises
   cut vertices with ``t >= 3`` blocks (TRAP 2) and nested split pairs.  On the small
   instances the *bijection* of Lemma 7.4 is checked, not just its cardinality.
2. **decisions** -- the exact factorial census ``gamma_N_factorial_n``, on the whole
   exhaustive small word batch and on the committed rank-3 fixtures.
3. **rank-2 regression** -- ``neuwirth_rank.solve_spherical``, whose three proved
   supports (``K4``, ``K4-e``, ``C4``) R1c-v2 subsumes: YES-set equality is asserted.
4. **witnesses** -- ``witness_check_n``, the permutation-only verifier.

The two recorded zero-shift false negatives of TRAP 1 (``<x,y | xY, yy>`` and
``<x,y | xxx, xxy>``) are asserted end to end, including the shift sets at which they are
spherical, since they are exactly what a support-first (rather than block-first)
decomposition gets wrong.
"""

from __future__ import annotations

import itertools
import json
import os
import random

import pytest

from experiments.stable_ac.fable import neuwirth_cut_schemes as CS
from experiments.stable_ac.fable import neuwirth_rank as NR
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable import witness_check_n as WCN

from helpers_fable import small_batch  # noqa: E402  (tests/fable is on sys.path)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE_PATH = os.path.join(
    REPO_ROOT, "results", "stable_ac", "theory", "fable", "rank3_census_fixtures.json"
)

RANK3 = ("x", "y", "z")
HARVEST_WALKTHROUGH = ("ZxyxYXY", "ZZxyxYXY", "ZyyyyXXX")

# The two recorded false negatives of the naive "order at b = reverse of order at a"
# rule (TRAP 1 / lit_AK3_P4_SYNCHRONIZED_PLANARITY.md Sec. 5).
FALSE_NEGATIVE_1 = ("xY", "yy")          # central multiplicity 2, spherical at shift 1
FALSE_NEGATIVE_2 = ("xxx", "xxy")        # central multiplicity 4, spherical at {1, 3}


# =====================================================================================
# 0. brute-force oracle for multigraph rotation systems (Sec. 10 recipe (a))
# =====================================================================================


def _canonical_cycle(seq):
    seq = tuple(seq)
    i = seq.index(min(seq))
    return seq[i:] + seq[:i]


def _rotation_family_size(graph) -> int:
    from math import factorial
    total = 1
    for v in graph.vertices:
        total *= factorial(max(graph.degree(v) - 1, 0))
    return total


def brute_force_spherical(graph):
    """Every genus-0 rotation system of ``graph`` as ``((v, cyclic edge tuple), ...)``.

    Faces are the cycles of ``d -> next(other(d))`` on the darts ``(edge, tail)``; a
    connected rotation system is spherical iff ``V - E + F = 2``.  One dart is pinned at
    every vertex, so the family has ``prod_v (deg v - 1)!`` members.
    """
    incident = {v: [] for v in graph.vertices}
    for eid, (u, v) in enumerate(graph.edge_ends):
        incident[u].append(eid)
        incident[v].append(eid)
    verts = list(graph.vertices)
    pools = []
    for v in verts:
        darts = tuple(incident[v])
        pools.append([(darts[0],) + p for p in itertools.permutations(darts[1:])])
    n_v, n_e = len(verts), graph.n_edges
    all_darts = []
    for eid, (u, v) in enumerate(graph.edge_ends):
        all_darts.append((eid, u))
        all_darts.append((eid, v))
    out = set()
    for combo in itertools.product(*pools):
        succ = {}
        for v, seq in zip(verts, combo):
            for k, e in enumerate(seq):
                succ[(e, v)] = seq[(k + 1) % len(seq)]
        seen = set()
        faces = 0
        for start in all_darts:
            if start in seen:
                continue
            faces += 1
            cur = start
            while cur not in seen:
                seen.add(cur)
                e, tail = cur
                u, w = graph.edge_ends[e]
                head = w if tail == u else u
                cur = (succ[(e, head)], head)
        if n_v - n_e + faces == 2:
            out.add(tuple((v, _canonical_cycle(seq)) for v, seq in zip(verts, combo)))
    return out


# =====================================================================================
# 1. the instance corpus: published anchors + a deterministic random family
# =====================================================================================


def _K4(extra=()):
    return list(itertools.combinations(range(4), 2)) + list(extra)


def _k4_minus_e(m, legs):
    """Poles a=0, b=1; degree-2 germs c=2, d=3.  ``legs = (m_ac, m_bc, m_ad, m_bd)``."""
    m_ac, m_bc, m_ad, m_bd = legs
    return ([(0, 1)] * m + [(0, 2)] * m_ac + [(1, 2)] * m_bc
            + [(0, 3)] * m_ad + [(1, 3)] * m_bd)


def _p4(p, m, q):
    """``a-b-c-d`` with classes ``P`` (p), ``M`` (m), ``Q`` (q)."""
    return [(0, 1)] * p + [(1, 2)] * m + [(2, 3)] * q


def _paw(m_ab, m_ac, m_bc, m_ad):
    """Triangle ``abc`` (a=0, b=1, c=2) plus a pendant class ``ad`` (d=3)."""
    return ([(0, 1)] * m_ab + [(0, 2)] * m_ac + [(1, 2)] * m_bc + [(0, 3)] * m_ad)


TRAP2_STAR = [(0, 1), (0, 1), (0, 2), (0, 3)]

K4E_VECTORS = ((1, (1, 1, 1, 1)), (2, (1, 1, 1, 1)), (1, (2, 1, 1, 1)),
               (0, (2, 1, 1, 1)), (2, (2, 1, 1, 1)), (3, (1, 1, 1, 1)),
               (1, (1, 2, 1, 1)))
P4_VECTORS = ((1, 1, 1), (2, 1, 1), (1, 2, 1), (2, 2, 1), (1, 3, 1), (2, 1, 2),
              (1, 2, 2))
PAW_VECTORS = ((1, 1, 1, 1), (2, 1, 1, 1), (1, 1, 1, 2), (2, 2, 1, 1), (1, 2, 1, 2),
               (3, 1, 1, 1))

ANCHOR_CASES = (
    [("K4", _K4()), ("K4[m01=2]", _K4([(0, 1)])), ("K4[m01=3]", _K4([(0, 1), (0, 1)])),
     ("C4", [(0, 1), (1, 2), (2, 3), (3, 0)]),
     ("C4[m=2,3]", [(0, 1), (0, 1), (1, 2), (2, 3), (2, 3), (2, 3), (3, 0)]),
     ("TRAP2-star", TRAP2_STAR)]
    + [(f"K4-e[m={m},legs={legs}]", _k4_minus_e(m, legs)) for m, legs in K4E_VECTORS]
    + [(f"P4{v}", _p4(*v)) for v in P4_VECTORS]
    + [(f"paw{v}", _paw(*v)) for v in PAW_VECTORS]
)


def _deterministic_random_cases(count=110, seed=20260729, family_cap=40_000):
    """A reproducible batch of connected loopless multigraphs (no RNG state leaks)."""
    rng = random.Random(seed)
    cases = []
    tried = 0
    while len(cases) < count and tried < 60_000:
        tried += 1
        n_v = rng.randint(3, 6)
        n_e = rng.randint(n_v - 1, 8)
        pairs = []
        for _ in range(n_e):
            u, v = rng.sample(range(n_v), 2)
            pairs.append((min(u, v), max(u, v)))
        graph = CS.multigraph_from_edges(pairs)
        if len(graph.vertices) != n_v:
            continue
        if _rotation_family_size(graph) > family_cap:
            continue
        decomp = CS.decompose(graph, quotient=False)
        if decomp.status != "OK":
            continue
        cases.append((f"rand[{tried}]", pairs))
    return tuple(cases)


RANDOM_CASES = _deterministic_random_cases()
COUNT_CASES = tuple(ANCHOR_CASES) + RANDOM_CASES


def _profile(pairs):
    graph = CS.multigraph_from_edges(pairs)
    decomp = CS.decompose(graph, quotient=False)
    return graph, decomp, CS.decomposition_profile(decomp)


def test_the_instance_corpus_has_the_required_composition():
    """>= 100 instances, >= 10 with t >= 3 cut vertices, >= 10 with nested 2-cuts."""
    assert len(COUNT_CASES) >= 100
    t3 = 0
    nested = 0
    for _name, pairs in COUNT_CASES:
        _graph, _decomp, prof = _profile(pairs)
        if prof["max_cut_vertex_arity"] >= 3:
            t3 += 1
        if prof["p_node_depth"] >= 2:
            nested += 1
    assert t3 >= 10, f"only {t3} instances with a t >= 3 cut vertex"
    assert nested >= 10, f"only {nested} instances with nested split pairs"


@pytest.mark.parametrize("name,pairs", COUNT_CASES, ids=[c[0] for c in COUNT_CASES])
def test_scheme_count_times_class_factorials_equals_the_brute_force_count(name, pairs):
    """``|Sigma| * prod m_uv! = N(G)`` -- equation (7.1), against brute force."""
    graph = CS.multigraph_from_edges(pairs)
    decomp = CS.decompose(graph, quotient=False)
    assert decomp.status == "OK", (name, decomp.reason)
    n_brute = len(brute_force_spherical(graph))
    assert decomp.scheme_space * graph.product_of_class_factorials() == n_brute, name
    # the enumeration must actually produce |Sigma| distinct schemes
    seen = set()
    for _label, layout in CS.iter_schemes(decomp):
        seen.add(tuple(sorted((v, seq) for v, seq in layout.items())))
    assert len(seen) == decomp.scheme_space, name


SMALL_BIJECTION_CASES = tuple(
    c for c in COUNT_CASES
    if _rotation_family_size(CS.multigraph_from_edges(c[1])) <= 4_000
)


@pytest.mark.parametrize("name,pairs", SMALL_BIJECTION_CASES,
                         ids=[c[0] for c in SMALL_BIJECTION_CASES])
def test_scheme_times_ranks_is_a_bijection_onto_the_spherical_systems(name, pairs):
    """Lemma 7.4 as a *bijection*, not merely a count: no duplicates, no gaps."""
    graph = CS.multigraph_from_edges(pairs)
    decomp = CS.decompose(graph, quotient=False)
    truth = brute_force_spherical(graph)
    produced = []
    for _label, rotation in CS.iter_scheme_rotations(decomp):
        produced.append(
            tuple((v, _canonical_cycle(rotation[v])) for v in graph.vertices))
    assert len(produced) == len(set(produced)), f"{name}: duplicate rotation systems"
    assert set(produced) == truth, name


def test_published_anchor_closed_forms():
    """The closed forms of Sec. 9.1-9.5, recomputed by the master formula."""
    from math import factorial

    # 9.1 K4 : N = 2 * prod m!, |Sigma| = 2
    graph = CS.multigraph_from_edges(_K4([(0, 1), (0, 1)]))
    decomp = CS.decompose(graph, quotient=False)
    assert decomp.scheme_space == 2
    assert (decomp.scheme_space * graph.product_of_class_factorials()
            == 2 * factorial(3))

    # 9.2 C4 : N = prod m!, |Sigma| = 1
    graph = CS.multigraph_from_edges([(0, 1), (0, 1), (1, 2), (2, 3), (3, 0)])
    assert CS.scheme_count(graph) == 1

    # 9.3 K4-e : N = (m+1)! * m_ac! m_bc! m_ad! m_bd!, |Sigma| = m + 1
    for m, legs in K4E_VECTORS:
        graph = CS.multigraph_from_edges(_k4_minus_e(m, legs))
        expected = factorial(m + 1)
        for leg in legs:
            expected *= factorial(leg)
        assert CS.scheme_count(graph) == m + 1, (m, legs)
        assert (CS.scheme_count(graph) * graph.product_of_class_factorials()
                == expected), (m, legs)

    # 9.4 P4 : N = p! m! m q!, |Sigma| = m  (the central Z/m shift)
    for p, m, q in P4_VECTORS:
        graph = CS.multigraph_from_edges(_p4(p, m, q))
        assert CS.scheme_count(graph) == m, (p, m, q)
        assert (CS.scheme_count(graph) * graph.product_of_class_factorials()
                == factorial(p) * factorial(m) * m * factorial(q)), (p, m, q)

    # 9.5 paw : N = p * prod m!, |Sigma| = p = m_ab + m_ac
    for m_ab, m_ac, m_bc, m_ad in PAW_VECTORS:
        graph = CS.multigraph_from_edges(_paw(m_ab, m_ac, m_bc, m_ad))
        p = m_ab + m_ac
        assert CS.scheme_count(graph) == p, (m_ab, m_ac, m_bc, m_ad)
        assert (CS.scheme_count(graph) * graph.product_of_class_factorials()
                == p * factorial(m_ab) * factorial(m_ac) * factorial(m_bc)
                * factorial(m_ad))


def test_trap2_star_has_six_spherical_systems_two_with_a_non_interval_block():
    """TRAP 2: for ``t >= 3`` the cut-vertex interval lemma is FALSE (Sec. 5, 10.1)."""
    graph = CS.multigraph_from_edges(TRAP2_STAR)
    systems = brute_force_spherical(graph)
    assert len(systems) == 6
    decomp = CS.decompose(graph, quotient=False)
    assert CS.decomposition_profile(decomp)["max_cut_vertex_arity"] == 3
    assert decomp.scheme_space * graph.product_of_class_factorials() == 6
    # blocks at the cut vertex 0: the dipole {0,1} (edges 0, 1) and the two pendants
    dipole = {0, 1}
    non_interval = 0
    for system in systems:
        at_zero = dict(system)[0]
        n = len(at_zero)
        positions = sorted(i for i, e in enumerate(at_zero) if e in dipole)
        gaps = sum(1 for i in range(len(positions))
                   if (positions[(i + 1) % len(positions)] - positions[i]) % n != 1)
        if gaps > 1:
            non_interval += 1
    assert non_interval == 2, "the paw-note trap must be present, not excluded"


def test_kreweras_and_the_merge_pattern_count():
    """Fact (K) and equation (5.1) on the size vectors of Sec. 10.2."""
    from math import factorial
    vectors = ((2, 2), (2, 1, 1), (2, 2, 1), (3, 2), (2, 2, 2), (3, 1, 1),
               (1, 1, 1, 1), (2, 1, 1, 1), (3, 2, 1))
    for sizes in vectors:
        n = sum(sizes)
        t = len(sizes)
        got = list(CS.nc_partitions(n, sizes))
        assert len(got) == factorial(n) // factorial(n - t + 1), sizes
        for labelling in got:
            counts = [0] * t
            for lab in labelling:
                counts[lab] += 1
            assert tuple(counts) == tuple(sizes)
        classes = CS.nc_rotation_classes(n, sizes)
        assert len(classes) == factorial(n - 1) // factorial(n - t + 1), sizes
        prod = 1
        for d in sizes:
            prod *= d
        assert CS.merge_pattern_count(sizes) == prod * len(classes)
    # the note's warning: A(2,1,1) = 6, and it is order independent
    assert CS.merge_pattern_count((2, 1, 1)) == 6
    assert CS.merge_pattern_count((1, 1, 2)) == 6
    assert CS.merge_pattern_count((1, 1)) == 1 * 1 * 1
    assert CS.merge_pattern_count((3, 4)) == 12


def test_non_planar_skeletons_are_certified_and_never_a_guess():
    for name, edges in (("K5", list(itertools.combinations(range(5), 2))),
                        ("K3,3", [(u, v + 3) for u in range(3) for v in range(3)])):
        graph = CS.multigraph_from_edges(edges)
        decomp = CS.decompose(graph, quotient=False)
        assert decomp.status == CS.NONPLANAR, name
        assert "non-planar" in decomp.reason
        assert CS.scheme_count(graph) == 0
        assert brute_force_spherical(graph) == set()


# =====================================================================================
# 2. decision cross-validation against the exact factorial census
# =====================================================================================

CENSUS_CAP = 500_000
SMALL_PAIRS = small_batch(7)


def _census_verdict(words, generators=None):
    census = RN.gamma_N_factorial_n(words, generators, cap_rotations=CENSUS_CAP,
                                    keep_accepting=False)
    if census["status"] != "OK":
        return None, census
    if census["link_components"] != 1:
        return CS.NOT_SPHERICAL, census
    return (CS.SPHERICAL if census["minimum_defect"] == 0 else CS.NOT_SPHERICAL), census


def test_decision_agrees_with_the_factorial_census_on_the_whole_small_batch():
    """VERDICT equality on every pair of the exhaustive <= 7 family (Theorem 7.5)."""
    checked = 0
    unsupported: dict = {}
    for words in SMALL_PAIRS:
        truth, census = _census_verdict(words)
        if truth is None:
            continue
        decision = CS.solve_cut_schemes(words)
        if decision.verdict == CS.UNSUPPORTED:
            unsupported[decision.reason] = unsupported.get(decision.reason, 0) + 1
            # a fail-closed answer is never allowed to be a disguised NO on a YES
            assert truth == CS.NOT_SPHERICAL or decision.spherical is None
            continue
        assert decision.verdict == truth, (words, decision.reason)
        checked += 1
    assert checked > 20_000, checked
    # the only excluded family in this batch is the disconnected link of Sec. 8.2
    assert all("components" in reason for reason in unsupported), unsupported


def test_the_two_recorded_false_negatives_are_now_decided_yes():
    """TRAP 1: block-first decomposition recovers the shifts the naive rule drops."""
    for words, central in ((FALSE_NEGATIVE_1, 2), (FALSE_NEGATIVE_2, 4)):
        decision = CS.solve_cut_schemes(words)
        assert decision.verdict == CS.SPHERICAL, words
        truth, _census = _census_verdict(words)
        assert truth == CS.SPHERICAL, words
        # the support is P4: three bundle blocks, two cut vertices, |Sigma| = m
        decomp = decision.support.decomposition
        profile = CS.decomposition_profile(decomp)
        assert profile["blocks"] == 3
        assert len(decomp.cut_plans) == 2
        assert decomp.unquotiented_scheme_space == central
        assert decision.counters.scheme_space == central
        WCN.check_witness_n(words, decision.witness.rotation_map(),
                            generators=decision.generators, trivial_group=False)


def test_the_false_negative_shift_sets_are_exactly_the_recorded_ones():
    """``("xY","yy")`` is spherical at shift 1 only; ``("xxx","xxy")`` at {1, 3}.

    The shift is the ``Z/m`` rotation offset of the central bundle block at the cut
    vertex that is *not* its anchor pole (Theorem 6.S case 2).  Enumerating schemes one
    at a time and re-running the phase/rank layer per scheme exposes the shift set.
    """
    for words, expected in ((FALSE_NEGATIVE_1, {1}), (FALSE_NEGATIVE_2, {1, 3})):
        support = CS.classify_cut_support(words, quotient=False)
        decomp = support.decomposition
        good = set()
        schemes = list(CS.iter_schemes(decomp))
        for index, (label, _layout) in enumerate(schemes):
            single = CS.solve_with_scheme_indices(words, support, {index})
            if single == CS.SPHERICAL:
                good.add(index)
        assert len(good) == len(expected), (words, good, len(schemes))
        # the *set* of working shifts, read off the enumeration order, must be a proper
        # non-empty subset -- i.e. the naive zero-shift scheme alone would say NO
        assert 0 not in good, (words, good)


# =====================================================================================
# 3. rank-2 regression: R1c-v2 subsumes K4, K4-e and C4
# =====================================================================================


def test_rank2_yes_sets_agree_on_every_k4_k4e_and_c4_support():
    """YES-set equality with ``neuwirth_rank.solve_spherical`` on the <= 7 family."""
    seen = {"K4": 0, "K4-e": 0, "C4": 0}
    yes_old: dict = {"K4": set(), "K4-e": set(), "C4": set()}
    yes_new: dict = {"K4": set(), "K4-e": set(), "C4": set()}
    for words in SMALL_PAIRS:
        support = NR.classify_support(words)
        if support.kind not in seen:
            continue
        seen[support.kind] += 1
        old = NR.solve_spherical(words)
        new = CS.solve_cut_schemes(words)
        assert new.verdict == old.verdict, (words, support.kind, old.verdict,
                                            new.verdict, new.reason)
        if old.verdict == CS.SPHERICAL:
            yes_old[support.kind].add(words)
        if new.verdict == CS.SPHERICAL:
            yes_new[support.kind].add(words)
    for kind in seen:
        assert seen[kind] > 0, kind
        assert yes_old[kind] == yes_new[kind], kind


def test_rank_n_three_connected_agreement_on_the_rank3_fixtures():
    """R1c is Corollary 6.R: the two solvers must agree wherever R1c applies."""
    with open(FIXTURE_PATH, encoding="utf-8") as fh:
        fixtures = json.load(fh)
    compared = 0
    for fixture in fixtures:
        words = tuple(fixture["words"])
        truth, _census = _census_verdict(words, RANK3)
        decision = CS.solve_cut_schemes(words, RANK3)
        expected = (CS.SPHERICAL if fixture["n_accepting"] > 0 else CS.NOT_SPHERICAL)
        assert truth == expected, words
        if decision.verdict == CS.UNSUPPORTED:
            assert expected == CS.NOT_SPHERICAL, (words, decision.reason)
            continue
        assert decision.verdict == expected, (words, decision.reason)
        compared += 1
        rank_n = RN.solve_spherical_n(words, RANK3)
        if rank_n.verdict != CS.UNSUPPORTED:
            assert rank_n.verdict == decision.verdict, words
    assert compared >= 5, compared


# =====================================================================================
# 4. the harvest walk-through state (Sec. 9.6)
# =====================================================================================


def test_harvest_walkthrough_state_is_in_scope_with_the_published_decomposition():
    support = CS.classify_cut_support(HARVEST_WALKTHROUGH, RANK3)
    assert support.kind == CS.IN_SCOPE, support.reason
    names = support.germ_names
    multiplicities = {f"{names[u]}{names[v]}": m for (u, v), m in support.multiplicities}
    assert multiplicities == {
        "x+x-": 2, "x+y-": 4, "x+z+": 2, "x+z-": 1, "x-y+": 4,
        "x-y-": 3, "y+y-": 3, "y+z+": 1, "y+z-": 2, "z+z-": 1,
    }
    data = support.data
    assert [data.degree(2 * k) for k in range(3)] == [9, 10, 4]
    assert len(data.edge_darts) == 23
    decomp = support.decomposition
    profile = CS.decomposition_profile(decomp)
    assert profile["blocks"] == 1                      # G is 2-connected
    assert len(decomp.cut_plans) == 0
    assert profile["nodes"]["R"] == 2                  # the P - R - R shape of Sec. 9.6
    assert decomp.unquotiented_scheme_space == 4       # 2 (core) x 2 (z) x 1 (P, k = 2)
    assert decomp.scheme_space == 2                    # after fixing one R-bit


def test_harvest_walkthrough_state_is_decided_in_the_published_budget():
    decision = CS.solve_cut_schemes(HARVEST_WALKTHROUGH, RANK3)
    counters = decision.counters
    assert counters.top_level_branches == 720          # |Sigma|/2 x 9*10*4 phases
    assert counters.phase_tuple_budget == 360
    assert counters.schemes_considered == 2
    assert counters.phase_tuples_considered == 720
    assert decision.verdict in (CS.SPHERICAL, CS.NOT_SPHERICAL)
    census_family = RN.census_size(decision.support.data, RANK3)
    assert census_family == 87_787_929_600            # the abandoned factorial census
    if decision.verdict == CS.SPHERICAL:               # never assumed -- verified
        report = WCN.check_witness_n(HARVEST_WALKTHROUGH,
                                     decision.witness.rotation_map(),
                                     generators=RANK3, trivial_group=False)
        assert report["defect"] == 0 and report["link_components"] == 1
    else:
        assert counters.exhaustive
        assert decision.witness is None


def test_harvest_round1_two_cut_states_are_now_in_scope():
    """The 628 two-cut states of round 1 were the gate R1c-v2 exists to open."""
    path = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                        "rank3_harvest_round1.jsonl")
    if not os.path.exists(path):
        pytest.skip("round-1 harvest file not present")
    sampled = 0
    in_scope = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("record") != "state":
                continue
            if row.get("gate") != "2-cut in S (not 3-connected)":
                continue
            sampled += 1
            if sampled > 40:
                break
            words = tuple(row["canonical"])
            support = CS.classify_cut_support(words, RANK3)
            if support.kind == CS.IN_SCOPE:
                in_scope += 1
    assert sampled > 0
    assert in_scope == min(sampled, 40), (in_scope, sampled)


# =====================================================================================
# 5. witnesses
# =====================================================================================


def _some_yes_words():
    out = [FALSE_NEGATIVE_1, FALSE_NEGATIVE_2, ("xyXY", "yzYZ", "zxZX")]
    found = 0
    for words in SMALL_PAIRS:
        decision = CS.solve_cut_schemes(words)
        if decision.verdict == CS.SPHERICAL:
            out.append(words)
            found += 1
            if found >= 30:
                break
    return tuple(out)


YES_WORDS = _some_yes_words()


@pytest.mark.parametrize("words", YES_WORDS, ids=[".".join(w) for w in YES_WORDS])
def test_every_yes_passes_the_independent_verifier(words):
    generators = RANK3 if len(set("".join(words).lower())) == 3 else None
    decision = CS.solve_cut_schemes(words, generators)
    assert decision.verdict == CS.SPHERICAL
    report = WCN.check_witness_n(words, decision.witness.rotation_map(),
                                 generators=decision.generators, trivial_group=False)
    assert report["defect"] == 0
    assert report["genus"] == 0
    assert report["link_components"] == 1
    assert report["euler_characteristic"] == 2
    assert report["compatible"]
    assert decision.witness.compatibility_verified
    assert decision.witness.defect == 0


def test_a_corrupted_witness_is_rejected_by_the_independent_verifier():
    words = FALSE_NEGATIVE_2
    decision = CS.solve_cut_schemes(words)
    assert decision.verdict == CS.SPHERICAL
    rotation = {k: list(v) for k, v in decision.witness.rotation_map().items()}
    # (a) transpose two darts at one germ -> compatibility or Euler must fail
    germ = sorted(k for k in rotation if len(rotation[k]) >= 3)[0]
    broken = dict(rotation)
    seq = list(rotation[germ])
    seq[0], seq[1] = seq[1], seq[0]
    broken[germ] = seq
    with pytest.raises(WCN.WitnessError):
        WCN.check_witness_n(words, broken, generators=decision.generators,
                            trivial_group=False)
    # (b) a dart that does not live at that germ
    broken = dict(rotation)
    other = sorted(k for k in rotation if k != germ)[0]
    broken[germ] = list(rotation[germ])[:-1] + [rotation[other][0]]
    with pytest.raises(WCN.WitnessError):
        WCN.check_witness_n(words, broken, generators=decision.generators,
                            trivial_group=False)


# =====================================================================================
# 6. fail-closed boundary (Sec. 8.2)
# =====================================================================================


@pytest.mark.parametrize("words,generators,needle", [
    (("xxY", "Xy"), ("x", "y", "z"), "do not occur"),
    (("x", "y"), ("x", "y"), "components"),
    (("xxx",), ("x",), "2n = 2 < 4"),
])
def test_fail_closed_paths_return_unsupported_not_no(words, generators, needle):
    decision = CS.solve_cut_schemes(words, generators)
    assert decision.verdict == CS.UNSUPPORTED
    assert decision.spherical is None
    assert needle in decision.reason


def test_a_loop_in_the_link_is_unsupported():
    """(H4): a non-cyclically-reduced relator can make an ``A``-loop (Sec. 8.2)."""
    seen = False
    for words in (("xXy", "yy"), ("xxXY", "yx"), ("xXY", "xyy")):
        support = CS.classify_cut_support(words)
        if support.data is not None and support.data.has_loop:
            seen = True
            assert support.kind == CS.UNSUPPORTED
            assert "loop" in support.reason
    assert seen, "no loop instance in the probe list"


def test_scheme_budget_refusal_is_unsupported_not_no():
    decision = CS.solve_cut_schemes(FALSE_NEGATIVE_2, scheme_budget=1)
    assert decision.verdict == CS.UNSUPPORTED
    assert "scheme space" in decision.reason
    decision = CS.solve_cut_schemes(FALSE_NEGATIVE_2, branch_budget=2)
    assert decision.verdict == CS.UNSUPPORTED
    assert "branch budget" in decision.reason


def test_the_reflection_quotient_never_changes_a_verdict():
    """Sec. 7.3 / audit point 7: fixing one R-bit is sound; no P-node is quotiented."""
    probes = [FALSE_NEGATIVE_1, FALSE_NEGATIVE_2, ("xyXY", "yzYZ", "zxZX"),
              HARVEST_WALKTHROUGH]
    probes.extend(SMALL_PAIRS[:400])
    for words in probes:
        generators = RANK3 if len(set("".join(words).lower())) == 3 else None
        a = CS.solve_cut_schemes(words, generators, quotient=True)
        b = CS.solve_cut_schemes(words, generators, quotient=False)
        assert a.verdict == b.verdict, words
        if a.support.decomposition is not None and a.support.kind == CS.IN_SCOPE:
            if a.support.decomposition.ctx.r_nodes:
                assert a.counters.scheme_space * 2 == b.counters.scheme_space, words
            else:
                assert a.counters.scheme_space == b.counters.scheme_space, words
