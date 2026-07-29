"""Frozen pure-word contract for the AK(3) Aut(F2) frontier manifest."""

import json
import subprocess
import sys
from hashlib import sha256
from itertools import pairwise
from pathlib import Path

import pytest

from experiments.stable_ac.thickenable.ak3_aut_frontier_manifest import (
    DEFAULT_MANIFEST_PATH,
    EDGES,
    IDENTITY_MAP,
    SOURCE_RELATORS,
    build_bfs_prefix,
    build_manifest_payload,
    check_manifest,
    compose_maps,
    cyclic_peel,
    exact_cellular_key,
    formal_inverse,
    free_reduce,
    inverse_edge_word,
    map_from_edge_word,
    substitute_free,
    substitute_literal,
    verify_manifest_bytes,
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
_ORACLE_INVERSE_EDGE_IDS = (0, 1, 2, 4, 3, 6, 5)
_ORACLE_SIGNED_MAPS = (
    ("x", "y"),
    ("x", "Y"),
    ("X", "y"),
    ("X", "Y"),
    ("y", "x"),
    ("y", "X"),
    ("Y", "x"),
    ("Y", "X"),
)
_ORACLE_SOURCE_RELATORS = ("xxxYYYY", "xyxYXY")
_BFS_PREFIX_DIGEST = "0bca72e8cf793e5ccc4c982342b47d3deefb6a745cfb26c22322867bf742f669"
_MANIFEST_DRIVER = Path(__file__).parents[2] / "experiments/stable_ac/thickenable/ak3_aut_frontier_manifest.py"


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


def _oracle_substitute_literal(word: str, images: tuple[str, str]) -> str:
    blocks = {
        "x": images[0],
        "X": _oracle_inverse(images[0]),
        "y": images[1],
        "Y": _oracle_inverse(images[1]),
    }
    return "".join(blocks[letter] for letter in word)


def _oracle_substitute(word: str, images: tuple[str, str]) -> str:
    return _oracle_reduce(_oracle_substitute_literal(word, images))


def _oracle_replay(edge_word: tuple[int, ...]) -> tuple[str, str]:
    images = ("x", "y")
    for edge_id in edge_word:
        edge_images = _ORACLE_EDGE_IMAGES[edge_id]
        images = (
            _oracle_substitute(edge_images[0], images),
            _oracle_substitute(edge_images[1], images),
        )
    return images


def _oracle_cyclic_peel(word: str) -> tuple[str, str, str]:
    prefix = ""
    core = word
    while len(core) >= 2 and core[0] == _ORACLE_INVERSE[core[-1]]:
        prefix += core[0]
        core = core[1:-1]
    return (prefix, core, _oracle_inverse(prefix))


def _oracle_rotations(word: str) -> tuple[str, ...]:
    if not word:
        return ("",)
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def _oracle_cellular_key(relators: tuple[str, str]) -> tuple[str, str]:
    candidates: list[tuple[str, str]] = []
    for images in _ORACLE_SIGNED_MAPS:
        transformed = tuple(_oracle_substitute_literal(word, images) for word in relators)
        representatives = tuple(
            min(_oracle_rotations(word) + _oracle_rotations(_oracle_inverse(word)))
            for word in transformed
        )
        candidates.append(tuple(sorted(representatives)))
    return min(candidates)


def _oracle_spelling_tracks(images: tuple[str, str]) -> dict[str, object]:
    literal = tuple(_oracle_substitute_literal(word, images) for word in _ORACLE_SOURCE_RELATORS)
    free = tuple(_oracle_reduce(word) for word in literal)
    peeled = tuple(_oracle_cyclic_peel(word) for word in free)
    prefixes = tuple(item[0] for item in peeled)
    cyclic = tuple(item[1] for item in peeled)
    inverse_prefixes = tuple(item[2] for item in peeled)
    return {
        "literal": {"raw": list(literal), "cellular_key": list(_oracle_cellular_key(literal))},
        "free": {"raw": list(free), "cellular_key": list(_oracle_cellular_key(free))},
        "cyclic": {
            "raw": list(cyclic),
            "peeled_prefixes": list(prefixes),
            "peeled_inverse_prefixes": list(inverse_prefixes),
            "cellular_key": list(_oracle_cellular_key(cyclic)),
        },
    }


def _oracle_buckets(records: list[dict[str, object]]) -> list[dict[str, object]]:
    members_by_key: dict[tuple[str, str], list[dict[str, object]]] = {}
    for record in records:
        tracks = record["spellings"]
        for mode in ("literal", "free", "cyclic"):
            key = tuple(tracks[mode]["cellular_key"])
            members_by_key.setdefault(key, []).append({"map_id": record["id"], "mode": mode})
    return [
        {"cellular_key": list(key), "members": members_by_key[key]}
        for key in sorted(members_by_key)
    ]


def _has_no_adjacent_inverse(word: str) -> bool:
    return all(left != _ORACLE_INVERSE[right] for left, right in pairwise(word))


def _bfs_prefix_digest(records: tuple[object, ...]) -> str:
    payload = "\n".join(
        f"{record.id}|{'-' if record.parent_id is None else record.parent_id}|"
        f"{record.depth}|{','.join(map(str, record.edge_word))}|"
        f"{record.images[0]}|{record.images[1]}"
        for record in records
    )
    return sha256(payload.encode("ascii")).hexdigest()


def test_manifest_check_replays_the_frozen_artifact() -> None:
    """Catches a missing independent replay entry point."""
    result = subprocess.run(
        [sys.executable, str(_MANIFEST_DRIVER), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "manifest check: OK\n"


def test_manifest_carries_the_frozen_map_and_three_spelling_contracts() -> None:
    """Catches missing map provenance, inverse replays, or spelling tracks."""
    payload = json.loads(DEFAULT_MANIFEST_PATH.read_bytes())

    assert payload["schema"] == "ak3-aut-frontier-manifest-v1"
    assert payload["source_config"] == {
        "bfs_cap": 1_000,
        "source_relators": ["xxxYYYY", "xyxYXY"],
    }
    assert len(payload["records"]) == 1_000
    assert payload["records"][0] == {
        "depth": 0,
        "edge_word": [],
        "forward_then_inverse": ["x", "y"],
        "id": 0,
        "images": ["x", "y"],
        "inverse_edge_word": [],
        "inverse_images": ["x", "y"],
        "inverse_then_forward": ["x", "y"],
        "parent_id": None,
        "spellings": {
            "literal": {
                "raw": ["xxxYYYY", "xyxYXY"],
                "cellular_key": ["XXXXYYY", "XYxYXy"],
            },
            "free": {
                "raw": ["xxxYYYY", "xyxYXY"],
                "cellular_key": ["XXXXYYY", "XYxYXy"],
            },
            "cyclic": {
                "raw": ["xxxYYYY", "xyxYXY"],
                "peeled_prefixes": ["", ""],
                "peeled_inverse_prefixes": ["", ""],
                "cellular_key": ["XXXXYYY", "XYxYXy"],
            },
        },
        "terminal_edge": None,
    }
    later = payload["records"][731]
    assert later["parent_id"] < later["id"]
    assert later["edge_word"][-1] == later["terminal_edge"]
    assert later["inverse_edge_word"] == [
        _ORACLE_INVERSE_EDGE_IDS[edge] for edge in reversed(later["edge_word"])
    ]
    assert set(later["spellings"]) == {"literal", "free", "cyclic"}
    assert all(bucket["members"] for bucket in payload["buckets"])


def test_manifest_spellings_keys_and_buckets_match_independent_oracle() -> None:
    """Catches a shared systematic defect in spelling, peeling, keys, or buckets."""
    payload = build_manifest_payload()
    oracle_records: list[dict[str, object]] = []

    for record in payload["records"]:
        images = _oracle_replay(tuple(record["edge_word"]))
        tracks = _oracle_spelling_tracks(images)
        assert record["images"] == list(images)
        assert record["spellings"] == tracks
        for free_word, prefix, core in zip(
            tracks["free"]["raw"],
            tracks["cyclic"]["peeled_prefixes"],
            tracks["cyclic"]["raw"],
        ):
            assert free_word == prefix + core + _oracle_inverse(prefix)
        oracle_records.append({"id": record["id"], "spellings": tracks})

    assert payload["records"][0]["spellings"] == oracle_records[0]["spellings"]
    assert payload["records"][731]["spellings"] == oracle_records[731]["spellings"]
    assert payload["buckets"] == _oracle_buckets(oracle_records)
    assert sum(len(bucket["members"]) for bucket in payload["buckets"]) == 3_000


def test_manifest_replay_rejects_every_integrity_boundary_tamper() -> None:
    """Catches a verifier that trusts any stored record, digest, or bucket field."""
    original = json.loads(DEFAULT_MANIFEST_PATH.read_bytes())

    def tampered(mutator: object) -> bytes:
        payload = json.loads(json.dumps(original))
        mutator(payload)
        return (
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
        ).encode("utf-8")

    mutations = (
        lambda payload: payload["records"][731].__setitem__("parent_id", 0),
        lambda payload: payload["records"][731].__setitem__("terminal_edge", 0),
        lambda payload: payload["records"][731].__setitem__("inverse_images", ["x", "y"]),
        lambda payload: payload["records"][731]["spellings"]["cyclic"]["peeled_prefixes"].__setitem__(0, "x"),
        lambda payload: payload["records"][731]["spellings"]["free"]["cellular_key"].__setitem__(0, "x"),
        lambda payload: payload["buckets"][0]["members"].__setitem__(0, {"map_id": 999, "mode": "free"}),
        lambda payload: payload.__setitem__("ordered_record_digest", "0" * 64),
        lambda payload: payload["integrity"].__setitem__("source_config_sha256", "0" * 64),
    )
    for mutate in mutations:
        with pytest.raises(AssertionError):
            verify_manifest_bytes(tampered(mutate))
    with pytest.raises(AssertionError):
        verify_manifest_bytes(DEFAULT_MANIFEST_PATH.read_bytes() + b" ")


def test_driver_write_and_check_are_byte_for_byte_deterministic() -> None:
    """Catches nondeterministic serialization or a check path that rewrites bytes."""
    before = DEFAULT_MANIFEST_PATH.read_bytes()
    check_manifest()
    assert DEFAULT_MANIFEST_PATH.read_bytes() == before

    write = subprocess.run(
        [sys.executable, str(_MANIFEST_DRIVER), "--write"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert write.returncode == 0, write.stderr
    assert write.stdout == "manifest write: OK\n"
    assert DEFAULT_MANIFEST_PATH.read_bytes() == before


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
