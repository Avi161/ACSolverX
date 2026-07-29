"""Frozen pure-word contract for the AK(3) Aut(F2) frontier manifest."""

from hashlib import sha256

from experiments.stable_ac.thickenable.ak3_aut_frontier_manifest import (
    EDGES,
    IDENTITY_MAP,
    SOURCE_RELATORS,
    build_bfs_prefix,
    compose_maps,
    cyclic_peel,
    exact_cellular_key,
    formal_inverse,
    free_reduce,
    inverse_edge_word,
    map_from_edge_word,
    substitute_free,
    substitute_literal,
)


_ORACLE_INVERSE = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
_ORACLE_EDGE_IMAGES = (
    ("y", "x"),
    ("X", "y"),
    ("x", "Y"),
    ("xy", "y"),
    ("xY", "y"),
    ("x", "yx"),
    ("x", "yX"),
)
_BFS_PREFIX_DIGEST = "0bca72e8cf793e5ccc4c982342b47d3deefb6a745cfb26c22322867bf742f669"


def _oracle_inverse(word: str) -> str:
    return "".join(_ORACLE_INVERSE[letter] for letter in reversed(word))


def _oracle_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == _ORACLE_INVERSE[letter]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def _oracle_substitute(word: str, images: tuple[str, str]) -> str:
    blocks = {
        "x": images[0],
        "X": _oracle_inverse(images[0]),
        "y": images[1],
        "Y": _oracle_inverse(images[1]),
    }
    return _oracle_reduce("".join(blocks[letter] for letter in word))


def _oracle_replay(edge_word: tuple[int, ...]) -> tuple[str, str]:
    images = ("x", "y")
    for edge_id in edge_word:
        edge_images = _ORACLE_EDGE_IMAGES[edge_id]
        images = (
            _oracle_substitute(edge_images[0], images),
            _oracle_substitute(edge_images[1], images),
        )
    return images


def _has_no_adjacent_inverse(word: str) -> bool:
    return all(left != _ORACLE_INVERSE[right] for left, right in zip(word, word[1:]))


def _bfs_prefix_digest(records: tuple[object, ...]) -> str:
    payload = "\n".join(
        f"{record.id}|{'-' if record.parent_id is None else record.parent_id}|"
        f"{record.depth}|{','.join(map(str, record.edge_word))}|"
        f"{record.images[0]}|{record.images[1]}"
        for record in records
    )
    return sha256(payload.encode("ascii")).hexdigest()


def test_frozen_nielsen_edges_inverse_ids_and_composition_convention() -> None:
    """Catches reordered edges, wrong inverses, or reversed composition."""
    assert [
        (edge.name, edge.x_image, edge.y_image, edge.inverse_id)
        for edge in EDGES
    ] == [
        ("swap", "y", "x", 0),
        ("inv_x", "X", "y", 1),
        ("inv_y", "x", "Y", 2),
        ("x_mul_y", "xy", "y", 4),
        ("x_mul_Y", "xY", "y", 3),
        ("y_mul_x", "x", "yx", 6),
        ("y_mul_X", "x", "yX", 5),
    ]
    assert compose_maps(EDGES[0].images, EDGES[3].images) == ("yx", "x")


def test_bfs_prefix_is_fifo_first_discovery_with_consistent_records_and_exact_cap() -> None:
    """Catches non-FIFO discovery, duplicate keys, bad lineage, and off-by-one caps."""
    records = build_bfs_prefix(1_000)

    assert len(records) == 1_000
    # Literal digest derived by a standalone reference BFS with its own edge
    # table, substitution, reduction, queue, and seen set; it imported no
    # project module and used the serialization reproduced in this test.
    assert _bfs_prefix_digest(records) == _BFS_PREFIX_DIGEST
    assert records[0].id == 0
    assert records[0].images == IDENTITY_MAP
    assert records[0].edge_word == ()
    assert [(record.edge_word, record.parent_id, record.depth) for record in records[:8]] == [
        ((), None, 0),
        ((0,), 0, 1),
        ((1,), 0, 1),
        ((2,), 0, 1),
        ((3,), 0, 1),
        ((4,), 0, 1),
        ((5,), 0, 1),
        ((6,), 0, 1),
    ]
    assert len({record.images for record in records}) == len(records)
    for expected_id, record in enumerate(records):
        assert record.id == expected_id
        assert record.images == _oracle_replay(record.edge_word)
        assert all(_has_no_adjacent_inverse(word) for word in record.images)
        assert record.depth == len(record.edge_word)
        if record.id == 0:
            continue
        assert record.parent_id is not None
        assert record.parent_id < record.id
        parent = records[record.parent_id]
        stored_edge = record.edge_word[-1]
        assert record.edge_word == parent.edge_word + (stored_edge,)
        assert record.depth == parent.depth + 1


def test_inverse_edge_words_rebuild_two_sided_inverse_maps() -> None:
    """Catches incorrect reverse/inverse derivation or one-sided inverse maps."""
    forward = (3, 0, 6)
    inverse_word = inverse_edge_word(forward)
    assert inverse_word == (5, 0, 4)

    forward_map = map_from_edge_word(forward)
    backward_map = map_from_edge_word(inverse_word)
    assert compose_maps(forward_map, backward_map) == IDENTITY_MAP
    assert compose_maps(backward_map, forward_map) == IDENTITY_MAP


def test_literal_free_and_cyclic_outputs_keep_their_distinct_meanings() -> None:
    """Catches premature reduction or failure to reduce inverse substitutions."""
    images = ("xy", "y")
    assert SOURCE_RELATORS == ("xxxYYYY", "xyxYXY")
    assert substitute_literal(SOURCE_RELATORS[0], images) == "xyxyxyYYYY"
    assert substitute_literal("xY", images) == "xyY"
    assert substitute_free("xY", images) == "x"
    assert free_reduce("xYxyyX") == "xYxyyX"
    assert cyclic_peel("xYxyyX") == ("xY", "xy", "yX")


def test_cyclic_peel_reconstructs_and_handles_empty_words() -> None:
    """Catches incorrect peeled conjugators and empty-word indexing."""
    prefix, core, suffix = cyclic_peel("xYxyyX")
    assert suffix == formal_inverse(prefix)
    assert "xYxyyX" == prefix + core + suffix
    assert cyclic_peel("") == ("", "", "")


def test_exact_cellular_key_identifies_only_the_frozen_orbit_operations() -> None:
    """Catches missing cellular symmetries or accidental free-group quotients."""
    relators = ("xyX", "yYX")
    assert exact_cellular_key(relators) == exact_cellular_key(("Yxy", "xXy"))
    assert exact_cellular_key(relators) == exact_cellular_key(("yXx", "YXy"))
    assert exact_cellular_key(relators) == exact_cellular_key(("yYX", "xyX"))
    assert exact_cellular_key(relators) == exact_cellular_key(("xyX", "xyY"))

    assert exact_cellular_key(relators) != exact_cellular_key(("y", "yYX"))
    assert exact_cellular_key(relators) != exact_cellular_key(("xyyYX", "yYYX"))
    assert exact_cellular_key(relators) != exact_cellular_key(("YxyXy", "yYX"))


def test_exact_cellular_key_uses_raw_ascii_order_without_reduction() -> None:
    """Catches locale ordering, relator-order loss, and comparison-time reduction."""
    assert exact_cellular_key(("xX", "y")) == ("X", "Yy")
