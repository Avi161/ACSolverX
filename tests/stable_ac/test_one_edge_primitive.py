import json

from experiments.stable_ac.rank3_compression.one_edge_primitive import (
    enumerate_one_edge_primitive_compressions,
    whitehead_graph_gate,
)
from experiments.stable_ac.rank3_compression.one_edge_primitive_certificate import (
    build_certificate,
    verify_certificate,
)
from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as PRIMITIVE_SINGLE_PATH,
)


def test_whitehead_graph_gate_accepts_every_certified_primitive_relator():
    with PRIMITIVE_SINGLE_PATH.open() as handle:
        data = json.load(handle)
    primitive_words = [
        row["word"] for row in data["word_records"] if row["primitive"]
    ]
    assert len(primitive_words) == 1016
    assert all(whitehead_graph_gate(word) for word in primitive_words)


def test_explicit_one_edge_primitive_census_reaches_standard_floor():
    census = enumerate_one_edge_primitive_compressions(
        sources=(("xz", "z", "t"),),
        upstream_trace="test",
    )
    assert census.source_count == 1
    assert census.literal_move_count > 0
    assert census.primitive_edge_count > 0
    assert census.minimum_output_floor == 2


def test_explicit_one_edge_primitive_certificate_replays():
    data = build_certificate(
        sources=(("xz", "z", "t"),),
        upstream_trace="test",
    )
    assert data["schema"] == "ak3-one-edge-primitive-v1"
    assert data["minimum_output_floor"] == 2
    assert data["candidate_lemma"] == "PROVED"
    verify_certificate(data, verify_upstream=False)
