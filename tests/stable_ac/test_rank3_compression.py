import pytest

from experiments.stable_ac.rank3_compression.certificate import (
    build_certificate,
    verify_certificate,
)
from experiments.stable_ac.rank3_compression.corridors import (
    corridor_output,
    enumerate_short_corridors,
    free_reduce,
    inverse,
    solve_isolator,
    substitute_generator,
    substitute_z,
)


AK3 = ("xxxYYYY", "xyxYXY")


def test_inverse_reverses_and_inverts_letters():
    assert inverse("xyX") == "xYX"


def test_free_reduce_cancels_adjacent_inverse_pairs():
    assert free_reduce("xyYX") == ""


def test_substitute_z_exposes_hidden_braid_spelling():
    assert substitute_z("zxZY", "xy") == "xyxYXY"


def test_substitute_generator_respects_inverse_letters():
    assert substitute_generator("xYy", "y", "zxZ") == "x"


def test_solve_negative_isolator():
    assert solve_isolator("zxZY", "y") == "zxZ"


def test_rejects_nonunique_isolator_generator():
    with pytest.raises(ValueError, match="exactly one"):
        solve_isolator("zyY", "y")


def test_ak3_corridor_output():
    assert corridor_output(AK3, 1, "xy", "zxZY", "y") == (
        "xxxyXXXXY",
        "YxyxY",
    )


def test_corridor_rejects_wrong_template_identity():
    with pytest.raises(ValueError, match="source relator"):
        corridor_output(AK3, 1, "xy", "zY", "y")


def test_short_enumerator_contains_hidden_ak3_witness():
    census = enumerate_short_corridors(
        AK3, max_word_length=2, max_template_length=4
    )
    assert any(
        row.word == "xy"
        and row.template == "zxZY"
        and row.output == ("xxxyXXXXY", "YxyxY")
        for row in census.accepted
    )
    assert census.enumerated_templates > 0
    assert census.trace_sha256


def test_one_z_templates_are_excluded():
    census = enumerate_short_corridors(
        AK3, max_word_length=2, max_template_length=3
    )
    assert all(
        row.template.count("z") + row.template.count("Z") >= 2
        for row in census.accepted
    )


def test_certificate_replays():
    data = build_certificate(max_word_length=2, max_template_length=4)
    assert data["schema"] == "ak3-rank3-corridors-v1"
    assert data["pair"] == ["xxxYYYY", "xyxYXY"]
    assert data["bounds"] == {
        "max_word_length": 2,
        "max_template_length": 4,
        "minimum_z_occurrences": 2,
    }
    verify_certificate(data)
