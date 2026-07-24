import pytest

from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    OccurrenceData,
    compose,
    cycle_count,
    enumerate_trace,
    orbit_count,
)


TARGETS = (
    ("xxxYYYY", "xyxYXY"),
    ("YYXXyx", "YYYxyXX"),
)


def test_products_act_right_to_left():
    p = (1, 0, 2)
    q = (0, 2, 1)
    assert compose(p, q) == (1, 2, 0)


def test_commutator_occurrence_dictionary():
    data = OccurrenceData.from_words(("xyXY",))
    assert len(data.A) == 8
    assert cycle_count(data.A) == 4
    assert cycle_count(data.B) == 4
    assert {g: len(es) for g, es in data.positive_ends.items()} == {"x": 2, "y": 2}


@pytest.mark.parametrize("words", [(), ("",), ("xy1",), ("x y",)])
def test_invalid_exact_words_are_rejected(words):
    with pytest.raises(ValueError):
        OccurrenceData.from_words(words)


def test_exact_words_are_not_reduced():
    data = OccurrenceData.from_words(("xX",))
    assert len(data.A) == 4
    assert cycle_count(data.A) == 2
    assert data.positive_ends == {"x": (0, 3)}


def test_hostile_xxX_fixture_distinguishes_BC_from_CB():
    data = OccurrenceData.from_words(("xxX",))
    assert data.A == (5, 2, 1, 4, 3, 0)
    assert data.B == (1, 0, 3, 2, 5, 4)

    C = (5, 3, 0, 4, 1, 2)
    AC = compose(data.A, C)
    BC = compose(data.B, C)
    CB = compose(C, data.B)

    L = orbit_count((data.A, C))
    defect = cycle_count(data.A) - cycle_count(C) + 2 * L - cycle_count(AC)
    assert defect == 0
    assert orbit_count((AC, BC)) == 1
    assert orbit_count((AC, CB)) == 2


def test_euler_acceptance_does_not_imply_BC_transitivity():
    census = enumerate_trace(("x", "xyXY"))
    assert any(
        trace[0] == 1 and trace[2] == 0 and trace[3] > 1
        for _, trace in census.accepting_orders
    )


@pytest.mark.parametrize(
    ("words", "has_euler_accepting_order"),
    [
        (("x", "y"), True),
        (("xyXY",), True),
        (("xyxYXY",), True),
        (("xx",), True),
        (("XXYXZYYZZ",), False),
    ],
)
def test_topology_calibration_exact_words(words, has_euler_accepting_order):
    census = enumerate_trace(words)
    assert bool(census.accepting_orders) is has_euler_accepting_order


@pytest.mark.parametrize("words", TARGETS)
def test_target_trace_is_complete(words):
    census = enumerate_trace(words)
    assert census.expected_cases == 86_400
    assert census.enumerated_cases == 86_400
    assert census.link_components == {1}
    assert sum(census.defect_histogram.values()) == 86_400


def test_census_json_is_replayable_data():
    census = enumerate_trace(("xyXY",))
    encoded = census.to_json()
    assert encoded["words"] == ["xyXY"]
    assert encoded["expected_cases"] == encoded["enumerated_cases"] == 1
    assert encoded["trace_sha256"] == census.trace_sha256
    assert encoded["accepting_orders"]
