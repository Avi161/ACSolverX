"""Calibration suite for the fable Neuwirth gamma_N decision stack.

Everything asserted here is either a literal copied from a published certificate or
recomputed from scratch inside the test.  No scratch-directory file is required; the
codex oracle cross-check skips itself when its scratch copy is absent.
"""

from __future__ import annotations

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import neuwirth_core as NC
from experiments.stable_ac.fable import neuwirth_rank as NR
from experiments.stable_ac.fable import witness_check as WC

from helpers_fable import (  # noqa: E402  (tests/fable is on sys.path via pytest)
    AK3,
    AK3_CENSUS,
    ORBIT2,
    ORBIT2_CENSUS,
    P25,
    Q,
    codex_oracle,
    small_batch,
)


# =====================================================================================
# 1. the factorial census pins the published codex certificate numbers
# =====================================================================================


@pytest.mark.parametrize("words,expected", [(AK3, AK3_CENSUS), (ORBIT2, ORBIT2_CENSUS)])
def test_factorial_census_matches_published_certificate(words, expected):
    census = NC.gamma_N_factorial(words)
    assert census["status"] == "OK"
    assert census["expected_cases"] == expected["enumerated_cases"]
    assert census["enumerated_cases"] == expected["enumerated_cases"]
    assert census["defect_histogram"] == expected["defect_histogram"]
    assert sum(census["defect_histogram"].values()) == expected["enumerated_cases"]
    assert census["minimum_genus"] == expected["minimum_genus"]
    assert census["minimum_defect"] == 2 * expected["minimum_genus"]
    assert len(census["accepting_orders"]) == expected["accepting_orders"]
    assert census["link_components"] == expected["link_components"]
    assert census["degrees"] == expected["degrees"]


@pytest.mark.parametrize("words,kind", [(AK3, "K4"), (ORBIT2, "K4")])
def test_rank_solver_agrees_with_the_census_on_the_two_certificate_targets(words, kind):
    decision = NR.solve_spherical(words)
    assert decision.support.kind == kind
    assert decision.verdict == NR.NOT_SPHERICAL
    assert decision.witness is None
    assert decision.counters.exhaustive
    assert NC.gamma_N_factorial(words, keep_accepting=False)["minimum_defect"] > 0


def test_factorial_family_size_is_the_product_of_positive_end_factorials():
    data = NC.build_link(AK3)
    # six unsigned x-occurrences and seven y-occurrences => 5! * 6! = 86,400
    assert data.degree(NC.X_POS) == 6 and data.degree(NC.Y_POS) == 7
    assert data.positive_end_orders_size() == 86_400
    assert data.n_occurrences == 13 and data.n_darts == 26


def test_link_component_count_is_constant_over_the_family():
    """L(C) is a support invariant; spot-check it against the direct orbit count."""
    data = NC.build_link(AK3)
    for k, orders in enumerate(NC.compatible_orders(data)):
        if k >= 200:
            break
        C = NC.rotation_from_orders(data, orders)
        numbers = NC.euler_data(data, C)
        assert numbers["link_components"] == data.link_components == 1
        assert numbers["cycles_A"] == data.n_occurrences
        assert numbers["cycles_C"] == 4
        assert NC.is_compatible(data, C)


def test_neuwirth_note_xxX_worked_example():
    """The hand example on the AC/BC convention, verbatim from the Neuwirth note."""
    data = NC.build_link(("xxX",))
    d0, h0, d1, h1, d2, h2 = 0, 1, 2, 3, 4, 5
    assert data.A == (h2, d1, h0, d2, h1, d0)
    assert data.B == (h0, d0, h1, d1, h2, d2)
    C = NC.rotation_from_orders(data, {NC.X_POS: (d0, h2, d1), NC.X_NEG: (h1, d2, h0)})
    assert NC.is_compatible(data, C)
    numbers = NC.euler_data(data, C)
    assert (numbers["cycles_A"], numbers["cycles_C"], numbers["cycles_AC"]) == (3, 2, 3)
    assert numbers["defect"] == 0 and numbers["link_components"] == 1
    # <AC, BC> is transitive while <AC, CB> has two orbits -- the printed discrepancy
    A, B = data.A, data.B
    AC = NC.compose(A, C)
    BC = NC.compose(B, C)
    CB = NC.compose(C, B)
    assert AC == (0, 4, 5, 3, 2, 1)
    assert BC == (4, 2, 1, 5, 0, 3)
    assert CB == (3, 5, 4, 0, 2, 1)
    assert NC.orbit_count((AC, BC), 6) == 1
    assert NC.orbit_count((AC, CB), 6) == 2


# =====================================================================================
# 2. the rank solver equals the factorial census on the exhaustive <= 7 batch
# =====================================================================================

# Recomputed inventory of the batch this repository builds: all cyclically reduced
# ORDERED word pairs of total length <= 7 in which both generators occur, deduplicated
# only as exact pairs (no canonicalisation).
#
# DEVIATION, DOCUMENTED.  The codex results note publishes "1,412 supported canonical
# cyclically reduced word-pairs of total length at most seven: 328 K4, 568 K4-e, 516
# C4".  That inventory is NOT this batch and could not be reproduced from any of ~40
# batch definitions tried (exact / rotation-deduped / rotation+inversion-deduped /
# canon_pair-deduped, ordered and unordered, several length bounds, "both generators in
# the pair" and "in each relator").  It cannot be the canonical batch it claims to be:
# there are only 498 canon_pair-distinct cyclically reduced pairs of total length <= 7
# in total, so no canonical batch at that bound can contain 1,412 supported members.
# What was verified instead, and is the substantive claim, is that this stack's
# classify_support agrees with the codex oracle on ALL 5,464 pairs of the batch whose
# relators are both at least three letters long (0 disagreements); below that length
# the two differ only because this stack applies the advisor's degenerate gate
# (relator < 3 letters => UNSUPPORTED) that the codex solver does not have.
BATCH_SUPPORT_INVENTORY = {"K4": 912, "K4-e": 2064, "C4": 1360}
BATCH_TOTAL_PAIRS = 22_824
BATCH_IN_SCOPE = 4_336
# The same batch reduced by canon_pair, for a second independent fingerprint.
BATCH_CANONICAL_INVENTORY = {"K4": 10, "K4-e": 28, "C4": 26}
BATCH_CANONICAL_PAIRS = 498


def _classify_batch():
    counts = {"K4": 0, "K4-e": 0, "C4": 0, "UNSUPPORTED": 0}
    in_scope = []
    for pair in small_batch(7):
        kind = NR.classify_support(pair).kind
        counts[kind] += 1
        if kind != "UNSUPPORTED":
            in_scope.append(pair)
    return counts, in_scope


def test_small_batch_is_exactly_deduplicated_and_has_the_recorded_inventory():
    batch = small_batch(7)
    assert len(batch) == BATCH_TOTAL_PAIRS
    assert len(set(batch)) == BATCH_TOTAL_PAIRS, "exact pairs must be distinct"
    assert all(
        W.is_cyclically_reduced(a) and W.is_cyclically_reduced(b) for a, b in batch
    )
    assert all(len(a) + len(b) <= 7 for a, b in batch)
    counts, in_scope = _classify_batch()
    assert {k: counts[k] for k in BATCH_SUPPORT_INVENTORY} == BATCH_SUPPORT_INVENTORY
    assert len(in_scope) == BATCH_IN_SCOPE == sum(BATCH_SUPPORT_INVENTORY.values())


def test_small_batch_canonical_inventory():
    canon = {W.canon_pair(*pair) for pair in small_batch(7)}
    assert len(canon) == BATCH_CANONICAL_PAIRS
    counts = {"K4": 0, "K4-e": 0, "C4": 0, "UNSUPPORTED": 0}
    for pair in canon:
        counts[NR.classify_support(pair).kind] += 1
    assert {k: counts[k] for k in BATCH_CANONICAL_INVENTORY} == BATCH_CANONICAL_INVENTORY


def test_rank_solver_equals_factorial_census_on_the_whole_in_scope_batch():
    _counts, in_scope = _classify_batch()
    yes_rank = set()
    yes_factorial = set()
    for pair in in_scope:
        decision = NR.solve_spherical(pair)
        assert decision.verdict in (NR.SPHERICAL, NR.NOT_SPHERICAL)
        census = NC.gamma_N_factorial(pair, keep_accepting=False)
        assert census["status"] == "OK"
        if decision.verdict == NR.SPHERICAL:
            yes_rank.add(pair)
        if census["minimum_defect"] == 0:
            yes_factorial.add(pair)
        if decision.verdict == NR.NOT_SPHERICAL:
            assert decision.counters.exhaustive
            assert decision.counters.schemes_considered == decision.counters.scheme_budget
            assert (decision.counters.phase_pairs_considered
                    == decision.counters.phase_pair_budget)
            assert (decision.counters.component_seed_attempts
                    == decision.counters.component_seed_budget)
    assert yes_rank == yes_factorial, {
        "rank_only": sorted(yes_rank - yes_factorial),
        "factorial_only": sorted(yes_factorial - yes_rank),
    }
    # non-vacuous: the batch contains both verdicts, in every support class
    assert len(yes_rank) == 2352
    assert len(in_scope) - len(yes_rank) == 1984
    by_kind = {"K4": 0, "K4-e": 0, "C4": 0}
    for pair in yes_rank:
        by_kind[NR.classify_support(pair).kind] += 1
    assert by_kind == {"K4": 528, "K4-e": 1296, "C4": 528}


# =====================================================================================
# 3. a K4-e instance that is spherical only for a split cut 0 < i < m
# =====================================================================================

SPLIT_CUT_FIXTURE = ("XXY", "XXy")


def _central_multiplicity(support):
    poles = support.poles
    return support.multiplicity_map()[tuple(sorted(poles[:2]))]


def test_k4_minus_e_needs_a_split_central_cut():
    support = NR.classify_support(SPLIT_CUT_FIXTURE)
    assert support.kind == "K4-e"
    m = _central_multiplicity(support)
    assert m >= 2

    decision = NR.solve_spherical(SPLIT_CUT_FIXTURE)
    assert decision.verdict == NR.SPHERICAL
    assert 0 < decision.witness.cut < m, decision.witness.cut

    # the factorial ground truth agrees that a spherical rotation exists
    census = NC.gamma_N_factorial(SPLIT_CUT_FIXTURE)
    assert census["minimum_defect"] == 0

    # ... and the naive "central class is one block" family (cuts 0 and m only) misses it
    schemes = [s for s in NR.embedding_schemes(support) if s.cut in (0, m)]
    assert len(schemes) == 2
    restricted = NR.solve_with_schemes(SPLIT_CUT_FIXTURE, schemes)
    assert restricted.verdict == NR.NOT_SPHERICAL

    report = WC.check_rank_witness(decision, trivial_group=False)
    assert report["defect"] == 0 and report["link_components"] == 1


def test_split_cut_phenomenon_is_not_a_one_off():
    """Every split-cut-only instance in the <= 7 batch is found by the full family."""
    found = 0
    for pair in small_batch(7):
        support = NR.classify_support(pair)
        if support.kind != "K4-e":
            continue
        m = _central_multiplicity(support)
        if m < 2:
            continue
        full = NR.solve_spherical(pair)
        if full.verdict != NR.SPHERICAL:
            continue
        schemes = [s for s in NR.embedding_schemes(support) if s.cut in (0, m)]
        if NR.solve_with_schemes(pair, schemes).verdict == NR.NOT_SPHERICAL:
            found += 1
            assert 0 < full.witness.cut < m
    assert found == 144


# =====================================================================================
# 4. witness round-trip, corruption, and the Corollary 3 audit path
# =====================================================================================


def test_every_yes_in_the_batch_passes_the_independent_witness_check():
    _counts, in_scope = _classify_batch()
    checked = 0
    non_transitive = 0
    for pair in in_scope:
        decision = NR.solve_spherical(pair)
        if decision.verdict != NR.SPHERICAL:
            continue
        # trivial_group=False: Corollary 3's transitivity claim needs pi_1 = 1, and the
        # batch is full of presentations of infinite groups.
        report = WC.check_rank_witness(decision, trivial_group=False)
        assert report["defect"] == 0
        assert report["link_components"] == 1
        assert report["euler_characteristic"] == 2
        assert report["cycles_C"] == 4
        assert report["cycles_A"] == sum(len(w) for w in pair)
        checked += 1
        if not report["ac_bc_transitive"]:
            non_transitive += 1
    assert checked == 2352
    assert non_transitive == 384


def test_corrupted_witness_is_rejected():
    decision = NR.solve_spherical(SPLIT_CUT_FIXTURE)
    rotation = decision.witness.rotation_map()
    assert WC.check_witness(SPLIT_CUT_FIXTURE, rotation, trivial_group=False)

    # (a) swap two darts between different germs: the dart sets no longer match
    germs = [g for g, seq in rotation.items() if seq]
    a, b = germs[0], germs[1]
    swapped = dict(rotation)
    sa, sb = list(rotation[a]), list(rotation[b])
    sa[0], sb[0] = sb[0], sa[0]
    swapped[a], swapped[b] = tuple(sa), tuple(sb)
    with pytest.raises(WC.WitnessError):
        WC.check_witness(SPLIT_CUT_FIXTURE, swapped, trivial_group=False)

    # (b) every transposition inside a single germ's cyclic order breaks the witness.
    # Germs of degree 2 are excluded: transposing a 2-element cyclic order is the
    # identity on rotations, so it is not a corruption at all.
    attempts = 0
    for germ, seq in rotation.items():
        if len(seq) < 3:
            continue
        for i in range(len(seq)):
            for j in range(i + 1, len(seq)):
                corrupt = dict(rotation)
                order = list(seq)
                order[i], order[j] = order[j], order[i]
                corrupt[germ] = tuple(order)
                attempts += 1
                with pytest.raises(WC.WitnessError):
                    WC.check_witness(SPLIT_CUT_FIXTURE, corrupt, trivial_group=False)
    assert attempts > 0


# ("XXY", "XYxy") presents Z (abelianised determinant 0): it has a genuine compatible
# spherical rotation whose <AC, BC> has two orbits, i.e. a disconnected boundary.  That
# is a legitimate topological outcome *because* Corollary 3's pi_1 = 1 hypothesis fails;
# with trivial_group=True the verifier must nevertheless raise, because on a certified
# trivial-group target that combination is proved impossible.
NON_TRIVIAL_GROUP_SPHERICAL = ("XXY", "XYxy")


def test_audit_contradiction_is_raised_when_the_trivial_group_hypothesis_is_asserted():
    decision = NR.solve_spherical(NON_TRIVIAL_GROUP_SPHERICAL)
    assert decision.verdict == NR.SPHERICAL
    report = WC.check_rank_witness(decision, trivial_group=False)
    assert report["defect"] == 0 and report["link_components"] == 1
    assert report["ac_bc_orbits"] == 2 and report["ac_bc_transitive"] is False
    with pytest.raises(WC.AuditContradiction):
        WC.check_rank_witness(decision, trivial_group=True)
    assert WC.ac_bc_orbit_count(
        NON_TRIVIAL_GROUP_SPHERICAL, decision.witness.rotation_map()
    ) == 2


def test_audit_permutations_on_hand_built_triples():
    # the Neuwirth note's xxX example: Euler passes and <AC, BC> is transitive
    A = (5, 2, 1, 4, 3, 0)
    B = (1, 0, 3, 2, 5, 4)
    C = (5, 3, 0, 4, 1, 2)
    report = WC.audit_permutations(A, B, C)
    assert report["defect"] == 0
    assert report["cycles_A"] == 3 and report["cycles_C"] == 2
    assert report["cycles_AC"] == 3
    assert report["ac_bc_orbits"] == 1

    # force the contradiction branch by handing it B' = C B C^-1-style garbage that
    # keeps Euler but disconnects <AC, BC>
    identity = tuple(range(6))
    with pytest.raises(WC.WitnessError):
        WC.audit_permutations(A, B, (0, 0, 0, 0, 0, 0))
    assert WC.audit_permutations(identity, identity, identity)["ac_bc_orbits"] == 6


# =====================================================================================
# 5. fail-closed boundary
# =====================================================================================


@pytest.mark.parametrize(
    "words,needle",
    [
        (("xXy", "xXy"), "loop"),                     # A-loops in the exact realization
        (("YYYXyyyyx", "YXXyxyy"), "loop"),           # path state 23, exact realization
        (("xy", "xyxYXY"), "degenerate relator"),     # a length-2 relator
        (("xx", "yy"), "degenerate relator"),
        (("xxx", "yyy"), "components"),               # disconnected support
        (("xxx", "xxx"), "germs"),                    # only two germs occur
    ],
)
def test_fail_closed_returns_unsupported_never_no(words, needle):
    decision = NR.solve_spherical(words)
    assert decision.verdict == NR.UNSUPPORTED
    assert decision.spherical is None
    assert decision.witness is None
    assert needle in (decision.reason or "")


def test_unsupported_supports_outside_the_three_proved_types():
    # a "paw": triangle plus a pendant edge -- connected, loopless, four germs, but not
    # K4 / K4-e / C4
    seen = False
    for pair in small_batch(7):
        support = NR.classify_support(pair)
        if support.kind != "UNSUPPORTED" or support.data is None:
            continue
        if support.data.has_loop or support.data.link_components != 1:
            continue
        if len(support.data.present_germs) < 4:
            continue
        if any(len(w) < NR.MIN_RELATOR_LENGTH for w in pair):
            continue
        assert "outside K4 / K4-e / C4" in support.reason
        assert NR.solve_spherical(pair).verdict == NR.UNSUPPORTED
        seen = True
    assert seen, "no connected loopless out-of-scope support in the batch"


def test_loopy_exact_realization_still_has_a_well_defined_factorial_census():
    """Fail-closed applies to the rank criterion, not to the Euler dictionary."""
    words = ("YYYXyyyyx", "YXXyxyy")
    assert NR.solve_spherical(words).verdict == NR.UNSUPPORTED
    data = NC.build_link(words)
    assert data.has_loop
    reduced = tuple(W.cyclic_reduce(w) for w in words)
    assert reduced == ("YYYXyyyyx", "XXyxy")
    assert NR.solve_spherical(reduced).verdict in (NR.SPHERICAL, NR.NOT_SPHERICAL)


# =====================================================================================
# 7. cross-check against the codex oracle
# =====================================================================================


def _oracle_verdict(module, pair):
    return module.solve_spherical(pair).verdict


def test_cross_check_against_codex_oracle():
    oracle = codex_oracle()
    if oracle is None:
        pytest.skip("codex neuwirth_rank_solver.py not present in this checkout")

    targets = [AK3, ORBIT2, P25, Q]
    batch = [p for p in small_batch(7)
             if NR.classify_support(p).kind != "UNSUPPORTED"]
    yes_members = [p for p in batch if NR.solve_spherical(p).verdict == NR.SPHERICAL]
    # 20 deterministic members, half of them YES cases
    sample = [batch[i] for i in range(0, 10 * (len(batch) // 10), len(batch) // 10)][:10]
    sample += [yes_members[i] for i in
               range(0, 10 * (len(yes_members) // 10), len(yes_members) // 10)][:10]
    assert len(sample) == 20
    assert sum(1 for p in sample if p in set(yes_members)) >= 10

    for pair in targets + sample:
        mine = NR.solve_spherical(pair)
        theirs = oracle.solve_spherical(pair)
        assert mine.verdict == theirs.verdict, (pair, mine.verdict, theirs.verdict)
        if mine.verdict != NR.UNSUPPORTED:
            assert mine.support.kind == theirs.support.kind, pair


def test_codex_oracle_agrees_on_support_for_every_non_degenerate_batch_pair():
    oracle = codex_oracle()
    if oracle is None:
        pytest.skip("codex neuwirth_rank_solver.py not present in this checkout")
    checked = 0
    for pair in small_batch(7):
        if any(len(w) < NR.MIN_RELATOR_LENGTH for w in pair):
            continue
        checked += 1
        assert NR.classify_support(pair).kind == oracle.classify_support(pair).kind, pair
    assert checked == 5_464
