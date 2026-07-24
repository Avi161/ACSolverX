import pytest

from experiments.stable_ac.rank3_compression.two_stabilization_certificate import (
    build_certificate,
    verify_certificate,
)
from experiments.stable_ac.rank3_compression.two_stabilization import (
    derive_rank3,
    enumerate_immediate_two_stabilizations,
    remove_second,
    solve_isolator,
    substitute_new,
)


AK3 = ("xxxYYYY", "xyxYXY")


def test_valid_two_word_braid_factorization():
    assert substitute_new("zxYT", "xy", "yx") == "xyxYXY"


def test_invalid_factor_order_is_quarantined():
    assert substitute_new("zxTY", "xy", "yx") == "xY"
    with pytest.raises(ValueError, match="source relator"):
        derive_rank3(AK3, 1, "xy", "yx", "zxTY")


def test_valid_factor_derives_exact_reduced_rank3_tuple():
    assert solve_isolator("zxYT", "y") == "Tzx"
    assert derive_rank3(AK3, 1, "xy", "yx", "zxYT") == (
        "xxZtXZtXZtXZt",
        "ZxTzx",
        "TTzxx",
    )


def test_known_triangular_certificate_returns_to_ak3_floor():
    rank3 = derive_rank3(AK3, 1, "x", "xy", "ytZT")
    assert rank3[2] == "TxtzT"
    assert solve_isolator(rank3[2], "x") == "ttZT"
    assert remove_second(rank3, 2) == (
        "yyXyXyXXXXXY",
        "XyyXY",
    )


def test_second_removal_rejects_multiple_old_generator_occurrences():
    rank3 = derive_rank3(AK3, 1, "xy", "yx", "zxYT")
    with pytest.raises(ValueError, match="exactly one"):
        remove_second(rank3, 1)


def test_length_two_length_four_census_contains_fixture():
    census = enumerate_immediate_two_stabilizations(
        AK3,
        max_word_length=2,
        max_template_length=4,
    )
    assert any(
        row.word_z == "x"
        and row.word_t == "xy"
        and row.template == "ytZT"
        and row.second_isolator_index == 2
        for row in census.certificates
    )
    assert census.minimum_output_floor == 13
    assert census.trace_sha256


def test_small_two_stabilization_certificate_replays():
    data = build_certificate(max_word_length=1, max_template_length=4)
    assert data["schema"] == "ak3-two-stabilization-v1"
    assert data["defining_word_count"] == 4
    verify_certificate(data)
