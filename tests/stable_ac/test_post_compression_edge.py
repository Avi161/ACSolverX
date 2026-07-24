from experiments.stable_ac.rank3_compression.post_compression_edge import (
    PostCompressionMove,
    apply_post_compression_move,
    enumerate_post_compression_edges,
    literal_children,
    load_upstream_roots,
)
from experiments.stable_ac.rank3_compression.post_compression_edge_certificate import (
    build_certificate,
    verify_certificate,
)


ROOT = ("YXXYx", "YXYXYXYXyxyxyx")


def test_exact_post_compression_edge_replays():
    move = PostCompressionMove(
        target=0,
        sign=1,
        target_rotation=0,
        other_rotation=7,
        child_relator="YXyxyxYXYXYXY",
        child=("YYXyxyxYXYXYX", "YXYXYXYXyxyxyx"),
    )
    assert move in tuple(literal_children(ROOT))
    assert apply_post_compression_move(ROOT, move) == move.child


def test_single_root_complete_image_has_observed_floor():
    census = enumerate_post_compression_edges((ROOT,), upstream_trace="test")
    assert census.root_count == 1
    assert census.literal_move_count == 280
    assert census.distinct_root_child_count > 0
    assert census.distinct_child_count > 0
    assert census.minimum_child_floor == 15
    assert census.trace_sha256


def test_upstream_certificate_exposes_twenty_roots():
    roots, trace = load_upstream_roots()
    assert len(roots) == 20
    assert trace == (
        "418393174833c114c4cc53f0fe323437"
        "b471c9d02227b748b9da3db482b398a8"
    )


def test_single_root_certificate_replays_independently():
    data = build_certificate((ROOT,), upstream_trace="test")
    assert data["schema"] == "ak3-post-compression-edge-v1"
    assert data["minimum_child_floor"] == 15
    assert data["candidate_lemma"] == "REFUTED"
    verify_certificate(data, verify_upstream=False)
