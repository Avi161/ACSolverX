import pytest

from experiments.stable_ac.supermoves.coordinate_endomorphism_census import (
    build_census,
)
from experiments.stable_ac.supermoves.quotient_isolator import (
    coordinate_endomorphism_move,
    exponent_sum,
    specialize_old_generators_to_identity,
)


PROPER_IMAGE = "xyyXY"


def test_coordinate_lift_builds_the_quotient_isolator():
    move = coordinate_endomorphism_move(("x", "y"), "y", PROPER_IMAGE)
    assert exponent_sum(PROPER_IMAGE, "y") == 1
    assert move.target == ("x", "xyyXY")
    assert move.quotient_isolator == "YxzzXZ"
    assert move.quotient_difference == "ZYxzzXZ"
    assert specialize_old_generators_to_identity(
        move.quotient_isolator, ("x", "y")
    ) == "z"
    assert specialize_old_generators_to_identity(
        move.quotient_difference, ("x", "y")
    ) == ""


def test_exact_aca0_target():
    source = ("YXXyxYx", "YYYYYYXyxyX")
    move = coordinate_endomorphism_move(source, "y", PROPER_IMAGE)
    assert move.target == (
        "xYYXXyyXYxyxY",
        "yxYYXyxYYXyxYYXyxYYXyxYYXyxYYXyyXYxxyyXYX",
    )


def test_negative_self_exponent_uses_inverse_stabilizer():
    move = coordinate_endomorphism_move(("x", "y"), "y", "yxYXY")
    assert move.exponent == -1
    assert specialize_old_generators_to_identity(
        move.quotient_isolator, ("x", "y")
    ) == "Z"
    assert specialize_old_generators_to_identity(
        move.quotient_difference, ("x", "y")
    ) == ""


def test_rejects_nonunimodular_coordinate_word():
    with pytest.raises(ValueError, match="self-exponent"):
        coordinate_endomorphism_move(("x", "y"), "y", "yy")


def test_census_does_not_promote_specialization_to_a_quotient_proof():
    rows = [{"name": "toy", "r1": "xy", "r2": "Yx"}]

    def separating_key(pair):
        return sum(map(len, pair)), pair

    payload = build_census(
        rows,
        separating_key,
        generator="y",
        image=PROPER_IMAGE,
    )
    assert payload["summary"]["quotient_specializations_verified"] == 1
    assert payload["summary"]["quotient_identities_conditionally_established"] == 0
    assert payload["records"][0]["quotient_identity_conditionally_established"] is False
    assert payload["summary"]["nonautomorphic_targets"] == 1
    assert payload["move"]["nonautomorphism_certificate"] == {
        "cyclically_reduced_commutator_image": "xyyXYXyxYY",
        "commutator_image_length": 10,
        "basis_commutator_length": 4,
        "verified": True,
    }
