import json
from pathlib import Path

import pytest

from experiments.stable_ac.supermoves.amec import (
    AMECStage,
    aca120_replay,
    replay_amec,
)


def test_aca120_two_stage_corridor_replays_exactly():
    replay = aca120_replay()

    assert replay.stages[0].definition == "Zxy"
    assert replay.stages[0].displayed_substitution_count == 2
    assert replay.stages[0].isolator == "YYYZyyyx"
    assert replay.stages[0].expression == "YYYzyyy"
    assert replay.stages[0].output == (
        "ZYYYZZYzzyyy",
        "ZYYYzyyyy",
    )

    assert replay.stages[1].definition == "Tyyy"
    assert replay.stages[1].displayed_substitution_count == 4
    assert replay.stages[1].isolator == "ZTZZYzzt"
    assert replay.stages[1].expression == "zztZTZZ"
    assert replay.target_before_relabel == (
        "ZTztzztZTZZ",
        "TzztZZZTZZ",
    )
    assert replay.target == (
        "XYxyxxyXYXX",
        "YxxyXXXYXX",
    )
    assert replay.displayed_substitution_count == 6
    assert replay.final_generators == ("z", "t")


def test_aca120_certificate_matches_the_replay():
    root = Path(__file__).resolve().parents[2]
    certificate = json.loads(
        (root / "results/stable_ac/theory/aca120_amec_certificate.json").read_text()
    )
    replay = aca120_replay()

    assert tuple(certificate["source"]) == replay.source
    assert certificate["triviality_provenance"] == replay.triviality_provenance
    assert tuple(certificate["target"]) == replay.target
    assert [stage["output"] for stage in certificate["stages"]] == [
        list(stage.output) for stage in replay.stages
    ]
    assert certificate["bound"]["lemma11_uses"] == 4
    assert certificate["bound"]["normal_witnesses_materialized"] is False
    assert (
        certificate["displayed_substitution_count"]
        == replay.displayed_substitution_count
    )


def test_compression_must_expand_to_the_current_relator():
    with pytest.raises(ValueError, match="does not expand"):
        replay_amec(
            ("xy", "y"),
            (
                AMECStage(
                    fresh_generator="z",
                    defining_word="xy",
                    compressed_relators=("zz", "y"),
                    eliminated_generator="x",
                    isolator_index=2,
                ),
            ),
            generators=("x", "y"),
            triviality_provenance="trivial test fixture",
        )


def test_triviality_provenance_is_required_for_inverse_lemma11():
    with pytest.raises(ValueError, match="triviality provenance"):
        replay_amec(
            ("x", "y"),
            (),
            generators=("x", "y"),
            triviality_provenance="",
        )


def test_k1_inert_stage_contains_plain_lemma11():
    replay = replay_amec(
        ("x", "Yx"),
        (
            AMECStage(
                fresh_generator="z",
                defining_word="",
                compressed_relators=("x", "Yx"),
                eliminated_generator="y",
                isolator_index=1,
            ),
        ),
        generators=("x", "y"),
        triviality_provenance="standard trivial presentation",
    )

    assert replay.stages[0].expression == "x"
    assert replay.target == ("x", "Z")
    assert replay.final_generators == ("x", "z")


def test_defining_word_cannot_use_an_undeclared_generator():
    with pytest.raises(ValueError, match="defining word uses an undeclared"):
        replay_amec(
            ("x", "y"),
            (
                AMECStage(
                    fresh_generator="z",
                    defining_word="q",
                    compressed_relators=("x", "y"),
                    eliminated_generator="x",
                    isolator_index=2,
                ),
            ),
            generators=("x", "y"),
            triviality_provenance="standard trivial presentation",
        )


def test_eliminated_generator_must_be_currently_declared():
    with pytest.raises(ValueError, match="not currently declared"):
        replay_amec(
            ("x", "y"),
            (
                AMECStage(
                    fresh_generator="z",
                    defining_word="x",
                    compressed_relators=("z", "y"),
                    eliminated_generator="q",
                    isolator_index=0,
                ),
            ),
            generators=("x", "y"),
            triviality_provenance="standard trivial presentation",
        )


@pytest.mark.parametrize(
    "relabel",
    (
        {"x": "xx", "y": "y"},
        {"x": "z", "y": "Z"},
        {"x": "x"},
    ),
)
def test_relabel_must_be_a_bijective_signed_basis_permutation(relabel):
    with pytest.raises(ValueError, match="relabel"):
        replay_amec(
            ("x", "y"),
            (),
            generators=("x", "y"),
            triviality_provenance="standard trivial presentation",
            relabel=relabel,
        )


def test_isolator_is_checked_after_prior_stage_substitutions():
    with pytest.raises(ValueError, match="exactly one y"):
        replay_amec(
            ("x", "y"),
            (
                AMECStage(
                    fresh_generator="z",
                    defining_word="x",
                    compressed_relators=("z", "y"),
                    eliminated_generator="x",
                    isolator_index=2,
                ),
                AMECStage(
                    fresh_generator="t",
                    defining_word="y",
                    compressed_relators=("z", "t"),
                    eliminated_generator="y",
                    isolator_index=0,
                ),
            ),
            generators=("x", "y"),
            triviality_provenance="standard trivial presentation",
        )
