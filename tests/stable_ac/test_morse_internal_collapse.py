from experiments.stable_ac.supermoves.morse_aca115_certificate import (
    ENDPOINT,
    EXPECTED_CRITICAL,
    MATCHING,
    SOURCE,
    STABILIZED_SOURCE,
    TOPOLOGICAL_ORDER_SHA256,
    WHITEHEAD_STATES,
    build_certificate,
    exponent_determinant,
    topological_order_digest,
    verify_certificate,
    whitehead_cut_minimum_delta,
)
from experiments.stable_ac.supermoves.morse_internal_collapse import (
    presentation_poset,
    replay,
    sample_greedy_matching,
    sample_target_rank_matching,
)


def test_aca115_matching_replays_exact_morse_endpoint():
    result = replay(SOURCE, MATCHING)
    poset = presentation_poset(("x", "y"), SOURCE)

    assert len(poset.cells) == 61
    assert len(poset.covers) == 138
    assert len(MATCHING) == 27
    assert len(result.topological_order) == 61
    assert result.critical_cells == EXPECTED_CRITICAL
    assert result.endpoint_words == ENDPOINT
    assert topological_order_digest(result.topological_order) == (
        TOPOLOGICAL_ORDER_SHA256
    )
    assert exponent_determinant(ENDPOINT) == 1


def test_aca115_endpoint_is_not_automorphic_to_trivial_stabilization():
    assert sum(map(len, STABILIZED_SOURCE)) == 14
    assert whitehead_cut_minimum_delta(STABILIZED_SOURCE) == 0

    reduced_endpoint = WHITEHEAD_STATES[-1]
    assert sum(map(len, reduced_endpoint)) == 15
    assert whitehead_cut_minimum_delta(reduced_endpoint) == 0

    # Whitehead minima are complete Aut(F_3)-invariants for total length.
    assert 14 != 15


def test_certificate_recomputes_all_structural_and_orbit_checks():
    certificate = build_certificate()
    assert certificate["source_id"] == "aca_115"
    assert certificate["endpoint"] == list(ENDPOINT)
    assert certificate["matching_pair_count"] == 27
    assert certificate["whitehead_minimum_delta_source"] == 0
    assert certificate["whitehead_minimum_delta_endpoint_reduced"] == 0
    assert certificate["limitations"]["primitive_relator_indices_zero_based"] == [1, 2]
    assert certificate["limitations"]["claim"] == (
        "mechanism and raw-orbit escape witness, not a solve"
    )
    assert verify_certificate()


def test_matching_rejects_a_duplicate_matched_cell():
    bad_matching = MATCHING + ((0, "x2"),)
    try:
        replay(SOURCE, bad_matching)
    except ValueError as error:
        assert "more than one matching pair" in str(error)
    else:
        raise AssertionError("invalid matching was accepted")


def test_sampled_matching_is_deterministic_and_replayable():
    poset = presentation_poset(("x", "y"), SOURCE)
    first = sample_greedy_matching(poset, 364)
    second = sample_greedy_matching(poset, 364)

    assert first == second
    result = replay(SOURCE, first)
    assert len(result.critical_cells[0]) == 1
    assert len(result.critical_cells[1]) == len(result.critical_cells[2])


def test_target_rank_sampler_constructs_one_three_three_matching():
    poset = presentation_poset(("x", "y"), SOURCE)
    matching = next(
        candidate
        for seed in range(100)
        if (candidate := sample_target_rank_matching(poset, seed, 3)) is not None
    )
    result = replay(SOURCE, matching)

    assert tuple(map(len, result.critical_cells)) == (1, 3, 3)
