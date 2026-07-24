import pytest

from experiments.stable_ac.rank3_compression.one_edge_certificate import (
    build_certificate,
    verify_certificate,
)
from experiments.stable_ac.rank3_compression.one_edge import (
    OneEdgeMove,
    apply_one_edge,
    canonical_rank3,
    cyclic_reduce,
    enumerate_one_edge_compressions,
    enumerate_rank3_sources,
    enumerate_seam_moves,
    remove_one_edge_isolator,
    rotations,
)


FIXTURE_RANK3 = (
    "TTxxzx",
    "TXXzxTxzxTxzxTxzx",
    "TZxzx",
)


def test_cyclic_reduction_removes_wrap_cascade():
    assert cyclic_reduce("xztZX") == "t"


def test_rotations_use_left_offset_order():
    assert rotations("xzt") == ("xzt", "ztx", "txz")


def test_rank3_canonicalization_preserves_names_only():
    source = ("xzt", "ZZx", "tXX")
    equivalent = ("XXt", "ztx", "xZZ")
    assert canonical_rank3(source) == canonical_rank3(equivalent)
    assert canonical_rank3(source) != canonical_rank3(
        tuple(word.translate(str.maketrans("xXzZ", "zZxX")) for word in source)
    )


def test_exact_one_edge_fixture_replays():
    expected = OneEdgeMove(
        target=0,
        other=2,
        sign=-1,
        target_rotation=0,
        other_rotation=0,
        child_relator="Txz",
    )
    assert expected in tuple(enumerate_seam_moves(FIXTURE_RANK3))
    assert apply_one_edge(FIXTURE_RANK3, expected) == (
        "Txz",
        "TXXzxTxzxTxzxTxzx",
        "TZxzx",
    )
    expression, output = remove_one_edge_isolator(
        FIXTURE_RANK3,
        expected,
        isolator_index=0,
    )
    assert expression == "tZ"
    assert output == ("YxYxYxyXyXyXyX", "YXyyX")


def test_one_edge_replay_rejects_a_nonseam_move():
    move = OneEdgeMove(0, 2, 1, 0, 0, "")
    with pytest.raises(ValueError, match="seam"):
        apply_one_edge(FIXTURE_RANK3, move)


def test_small_source_census_excludes_immediate_isolators():
    census = enumerate_rank3_sources(
        ("xxxYYYY", "xyxYXY"),
        max_word_length=2,
        max_template_length=4,
    )
    assert census.defining_word_count == 16
    assert census.tested_cases == (
        census.defining_word_count**2
        * census.structural_template_count
    )
    assert census.accepted_source_identities > 0
    assert census.distinct_cyclic_rank3_count >= census.eligible_rank3_count
    assert all(
        all(sum(letter.lower() == "x" for letter in relator) != 1
            for relator in source.rank3)
        for source in census.eligible_sources
    )


def test_small_one_edge_census_is_deterministic():
    first = enumerate_one_edge_compressions(
        ("xxxYYYY", "xyxYXY"),
        max_word_length=2,
        max_template_length=5,
    )
    second = enumerate_one_edge_compressions(
        ("xxxYYYY", "xyxYXY"),
        max_word_length=2,
        max_template_length=5,
    )
    assert first == second
    assert first.source_census.eligible_rank3_count > 0
    assert first.seam_move_count > 0
    assert first.one_x_incidence_count > 0
    assert first.minimum_output_floor == 14
    assert first.trace_sha256


def test_small_one_edge_certificate_replays():
    data = build_certificate(
        max_word_length=2,
        max_template_length=5,
    )
    assert data["schema"] == "ak3-one-edge-v1"
    assert data["candidate_lemma"] == "REFUTED"
    assert data["minimum_output_floor"] == 14
    verify_certificate(data)
