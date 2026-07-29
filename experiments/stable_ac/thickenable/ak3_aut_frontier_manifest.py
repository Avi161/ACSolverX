"""Pure free-word infrastructure for the frozen AK(3) Aut(F2) frontier."""

from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path

WordMap = tuple[str, str]
IDENTITY_MAP: WordMap = ("x", "y")
SOURCE_RELATORS = ("xxxYYYY", "xyxYXY")


@dataclass(frozen=True)
class NielsenEdge:
    name: str
    x_image: str
    y_image: str
    inverse_id: int

    @property
    def images(self) -> WordMap:
        return (self.x_image, self.y_image)


@dataclass(frozen=True)
class MapRecord:
    id: int
    images: WordMap
    parent_id: int | None
    depth: int
    edge_word: tuple[int, ...]


EDGES = (
    NielsenEdge("swap", "y", "x", 0),
    NielsenEdge("inv_x", "X", "y", 1),
    NielsenEdge("inv_y", "x", "Y", 2),
    NielsenEdge("x_mul_y", "xy", "y", 4),
    NielsenEdge("x_mul_Y", "xY", "y", 3),
    NielsenEdge("y_mul_x", "x", "yx", 6),
    NielsenEdge("y_mul_X", "x", "yX", 5),
)


def formal_inverse(word: str) -> str:
    return "".join(letter.swapcase() for letter in reversed(word))


def free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def _image(letter: str, images: WordMap) -> str:
    if letter == "x":
        return images[0]
    if letter == "y":
        return images[1]
    if letter == "X":
        return formal_inverse(images[0])
    if letter == "Y":
        return formal_inverse(images[1])
    raise ValueError(f"not an F2 letter: {letter!r}")


def substitute_literal(word: str, images: WordMap) -> str:
    return "".join(_image(letter, images) for letter in word)


def substitute_free(word: str, images: WordMap) -> str:
    return free_reduce(substitute_literal(word, images))


def compose_maps(phi: WordMap, nu: WordMap) -> WordMap:
    """Return phi o nu, with phi substituted into each image of nu."""
    return (substitute_free(nu[0], phi), substitute_free(nu[1], phi))


def inverse_edge_word(edge_word: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(EDGES[edge_id].inverse_id for edge_id in reversed(edge_word))


def map_from_edge_word(edge_word: tuple[int, ...]) -> WordMap:
    images = IDENTITY_MAP
    for edge_id in edge_word:
        images = compose_maps(images, EDGES[edge_id].images)
    return images


def build_bfs_prefix(cap: int) -> tuple[MapRecord, ...]:
    if cap <= 0:
        return ()
    records = [MapRecord(0, IDENTITY_MAP, None, 0, ())]
    seen = {IDENTITY_MAP}
    pending = deque([0])
    while pending and len(records) < cap:
        parent_id = pending.popleft()
        parent = records[parent_id]
        for edge_id, edge in enumerate(EDGES):
            images = compose_maps(parent.images, edge.images)
            if images in seen:
                continue
            child = MapRecord(
                len(records), images, parent_id, parent.depth + 1, parent.edge_word + (edge_id,)
            )
            records.append(child)
            seen.add(images)
            pending.append(child.id)
            if len(records) == cap:
                break
    return tuple(records)


def cyclic_peel(word: str) -> tuple[str, str, str]:
    prefix = ""
    core = word
    while len(core) >= 2 and core[0] == core[-1].swapcase():
        prefix += core[0]
        core = core[1:-1]
    return (prefix, core, formal_inverse(prefix))


def _rotations(word: str) -> tuple[str, ...]:
    if not word:
        return (word,)
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def _signed_generator_maps() -> tuple[WordMap, ...]:
    maps: list[WordMap] = []
    for x_image in ("x", "X", "y", "Y"):
        y_choices = ("y", "Y") if x_image.lower() == "x" else ("x", "X")
        maps.extend((x_image, y_image) for y_image in y_choices)
    return tuple(maps)


def exact_cellular_key(relators: tuple[str, str]) -> tuple[str, str]:
    candidates: list[tuple[str, str]] = []
    for images in _signed_generator_maps():
        transformed = tuple(substitute_literal(word, images) for word in relators)
        options = [
            tuple(_rotations(word)) + tuple(_rotations(formal_inverse(word)))
            for word in transformed
        ]
        for first, second in product(*options):
            candidates.append((first, second))
            candidates.append((second, first))
    return min(candidates)


MANIFEST_SCHEMA = "ak3-aut-frontier-manifest-v1"
BFS_CAP = 1_000
SPELLING_MODES = ("literal", "free", "cyclic")
_BFS_PREFIX_DIGEST = "0bca72e8cf793e5ccc4c982342b47d3deefb6a745cfb26c22322867bf742f669"
_ROOT = Path(__file__).resolve().parents[3]
_DESIGN_PATH = _ROOT / "docs/superpowers/specs/2026-07-29-ak3-aut-thickenability-frontier-design.md"
DEFAULT_MANIFEST_PATH = _ROOT / "results/stable_ac/theory/ak3_aut_frontier_manifest.json"


def _canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def _source_config() -> dict[str, object]:
    return {"bfs_cap": BFS_CAP, "source_relators": list(SOURCE_RELATORS)}


def _digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _bfs_prefix_digest(records: tuple[MapRecord, ...]) -> str:
    payload = "\n".join(
        f"{record.id}|{'-' if record.parent_id is None else record.parent_id}|"
        f"{record.depth}|{','.join(map(str, record.edge_word))}|"
        f"{record.images[0]}|{record.images[1]}"
        for record in records
    )
    return _digest_bytes(payload.encode("ascii"))


def _spelling_tracks(images: WordMap) -> dict[str, dict[str, list[str]]]:
    literal = tuple(substitute_literal(relator, images) for relator in SOURCE_RELATORS)
    free = tuple(free_reduce(word) for word in literal)
    peeled = tuple(cyclic_peel(word) for word in free)
    prefixes = tuple(item[0] for item in peeled)
    cyclic = tuple(item[1] for item in peeled)
    inverse_prefixes = tuple(item[2] for item in peeled)
    for free_word, prefix, core, inverse_prefix in zip(free, prefixes, cyclic, inverse_prefixes):
        if free_word != prefix + core + inverse_prefix:
            raise AssertionError("cyclic peel did not reconstruct the free word")
    return {
        "literal": {"raw": list(literal), "cellular_key": list(exact_cellular_key(literal))},
        "free": {"raw": list(free), "cellular_key": list(exact_cellular_key(free))},
        "cyclic": {
            "raw": list(cyclic),
            "peeled_prefixes": list(prefixes),
            "peeled_inverse_prefixes": list(inverse_prefixes),
            "cellular_key": list(exact_cellular_key(cyclic)),
        },
    }


def _record_payload(record: MapRecord) -> dict[str, object]:
    inverse_word = inverse_edge_word(record.edge_word)
    inverse_images = map_from_edge_word(inverse_word)
    forward_then_inverse = compose_maps(record.images, inverse_images)
    inverse_then_forward = compose_maps(inverse_images, record.images)
    if forward_then_inverse != IDENTITY_MAP or inverse_then_forward != IDENTITY_MAP:
        raise AssertionError("edge-word inverse did not replay to a two-sided inverse")
    return {
        "depth": record.depth,
        "edge_word": list(record.edge_word),
        "forward_then_inverse": list(forward_then_inverse),
        "id": record.id,
        "images": list(record.images),
        "inverse_edge_word": list(inverse_word),
        "inverse_images": list(inverse_images),
        "inverse_then_forward": list(inverse_then_forward),
        "parent_id": record.parent_id,
        "spellings": _spelling_tracks(record.images),
        "terminal_edge": None if record.parent_id is None else record.edge_word[-1],
    }


def _bucket_payload(records: list[dict[str, object]]) -> list[dict[str, object]]:
    members_by_key: dict[tuple[str, str], list[dict[str, object]]] = {}
    for record in records:
        for mode in SPELLING_MODES:
            track = record["spellings"][mode]  # type: ignore[index]
            key = tuple(track["cellular_key"])  # type: ignore[index]
            members_by_key.setdefault(key, []).append({"map_id": record["id"], "mode": mode})
    return [
        {"cellular_key": list(key), "members": members_by_key[key]}
        for key in sorted(members_by_key)
    ]


def build_manifest_payload() -> dict[str, object]:
    """Rebuild the complete frozen manifest from the map prefix and source tuple."""
    map_records = build_bfs_prefix(BFS_CAP)
    if len(map_records) != BFS_CAP or _bfs_prefix_digest(map_records) != _BFS_PREFIX_DIGEST:
        raise AssertionError("the frozen 1,000-map BFS prefix changed")
    records = [_record_payload(record) for record in map_records]
    source_config = _source_config()
    return {
        "buckets": _bucket_payload(records),
        "integrity": {
            "design_sha256": _digest_bytes(_DESIGN_PATH.read_bytes()),
            "manifest_module_sha256": _digest_bytes(Path(__file__).read_bytes()),
            "source_config_sha256": _digest_bytes(_canonical_json_bytes(source_config)),
        },
        "ordered_record_digest": _digest_bytes(_canonical_json_bytes(records)),
        "ordered_record_digest_definition": "sha256 of canonical UTF-8 JSON record-list bytes (sorted keys, compact separators, ASCII escaping, one trailing newline)",
        "records": records,
        "schema": MANIFEST_SCHEMA,
        "source_config": source_config,
    }


def build_manifest_bytes() -> bytes:
    return _canonical_json_bytes(build_manifest_payload())


def verify_manifest_bytes(manifest_bytes: bytes) -> None:
    """Independently rebuild every manifest field and require canonical byte identity."""
    try:
        parsed = json.loads(manifest_bytes)
    except json.JSONDecodeError as error:
        raise AssertionError("manifest is not valid JSON") from error
    expected = build_manifest_payload()
    if parsed != expected:
        raise AssertionError("manifest payload differs from its independent replay")
    if manifest_bytes != _canonical_json_bytes(expected):
        raise AssertionError("manifest bytes are not canonical or differ from the replay")


def check_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> None:
    verify_manifest_bytes(path.read_bytes())


def write_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> None:
    path.write_bytes(build_manifest_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description="build or replay the frozen AK(3) Aut(F2) manifest")
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--write", action="store_true")
    operation.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write_manifest()
            print("manifest write: OK")
        else:
            check_manifest()
            print("manifest check: OK")
    except (AssertionError, OSError) as error:
        print(f"manifest check: FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
