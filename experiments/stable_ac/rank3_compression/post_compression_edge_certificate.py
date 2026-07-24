"""Build and replay the post-compression one-edge AK(3) certificate."""

import argparse
from collections import Counter
import json
from pathlib import Path

from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.equivalence_classes.lib.words import canon_pair
from experiments.stable_ac.rank3_compression.one_edge_certificate import (
    verify_certificate as verify_upstream_certificate,
)
from experiments.stable_ac.rank3_compression.post_compression_edge import (
    PostCompressionCensus,
    PostCompressionMove,
    UPSTREAM_PATH,
    enumerate_post_compression_edges,
    load_upstream_roots,
)


SCHEMA = "ak3-post-compression-edge-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT / "results/stable_ac/theory/ak3_post_compression_edge.json"
)


def build_certificate(
    roots: tuple[tuple[str, str], ...] | None = None,
    upstream_trace: str | None = None,
) -> dict[str, object]:
    census = enumerate_post_compression_edges(
        roots=roots,
        upstream_trace=upstream_trace,
    )
    return _certificate_from_census(census)


def verify_certificate(
    data: dict[str, object],
    verify_upstream: bool = True,
) -> None:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"wrong schema: {data.get('schema')!r}")

    roots_row = data.get("roots")
    if not isinstance(roots_row, list):
        errors.append("roots must be a list")
        roots_row = []
    roots: tuple[tuple[str, str], ...] = tuple(
        tuple(root) for root in roots_row if isinstance(root, list)
    )
    if len(roots) != len(roots_row) or any(len(root) != 2 for root in roots):
        errors.append("malformed roots")
    for index, root in enumerate(roots):
        if canon_pair(*root) != root:
            errors.append(f"roots[{index}] is not canonical")

    upstream_trace = data.get("upstream_trace")
    if not isinstance(upstream_trace, str):
        errors.append("upstream_trace must be a string")

    if verify_upstream:
        with UPSTREAM_PATH.open() as handle:
            upstream_data = json.load(handle)
        verify_upstream_certificate(upstream_data)
        expected_roots, expected_trace = load_upstream_roots()
        if roots != expected_roots:
            errors.append("roots differ from verified upstream certificate")
        if upstream_trace != expected_trace:
            errors.append("trace differs from verified upstream certificate")

    edges = data.get("edges")
    if not isinstance(edges, list):
        errors.append("edges must be a list")
        edges = []
    replayed_edge_keys: set[
        tuple[tuple[str, str], tuple[str, str]]
    ] = set()
    for index, row in enumerate(edges):
        if not isinstance(row, dict):
            errors.append(f"edges[{index}] is not an object")
            continue
        replayed = _verify_edge_row(row, index, errors)
        if replayed is not None:
            replayed_edge_keys.add(replayed)
    if len(replayed_edge_keys) != len(edges):
        errors.append("edge rows are not unique root-child pairs")

    aut_orbits = data.get("aut_orbits")
    if not isinstance(aut_orbits, list):
        errors.append("aut_orbits must be a list")
        aut_orbits = []
    for orbit_index, orbit in enumerate(aut_orbits):
        if not isinstance(orbit, dict):
            errors.append(f"aut_orbits[{orbit_index}] is not an object")
            continue
        representative = tuple(orbit.get("representative", ()))
        minimum_total = orbit.get("minimum_total")
        if minimum_total != sum(len(word) for word in representative):
            errors.append(f"aut_orbits[{orbit_index}] minimum mismatch")
        children = orbit.get("children")
        if not isinstance(children, list) or not children:
            errors.append(f"aut_orbits[{orbit_index}] has no children")
            continue
        for child_index, row in enumerate(children):
            if not isinstance(row, dict):
                errors.append(
                    f"aut_orbits[{orbit_index}].children[{child_index}] "
                    "is not an object"
                )
                continue
            child = tuple(row.get("child", ()))
            phi = row.get("phi")
            if (
                len(child) != 2
                or not isinstance(phi, dict)
                or not check(child, representative, phi)
            ):
                errors.append(
                    f"aut_orbits[{orbit_index}].children[{child_index}] "
                    "has an invalid Aut witness"
                )

    if errors:
        raise AssertionError("\n".join(errors))

    expected = build_certificate(
        roots=roots,
        upstream_trace=upstream_trace,
    )
    if data != expected:
        differing = sorted(
            key
            for key in set(data) | set(expected)
            if data.get(key) != expected.get(key)
        )
        raise AssertionError(
            "certificate differs from complete replay in keys: "
            + ", ".join(differing)
        )


def _verify_edge_row(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> tuple[tuple[str, str], tuple[str, str]] | None:
    where = f"edges[{index}]"
    try:
        root = tuple(row["root"])
        move_row = row["move"]
        if not isinstance(move_row, dict):
            raise TypeError("move must be an object")
        move = PostCompressionMove(
            target=int(move_row["target"]),
            sign=int(move_row["sign"]),
            target_rotation=int(move_row["target_rotation"]),
            other_rotation=int(move_row["other_rotation"]),
            child_relator=str(move_row["child_relator"]),
            child=tuple(move_row["child"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return None
    try:
        got_relator, got_child = _independent_replay(root, move)
    except (IndexError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None
    if got_relator != move.child_relator:
        errors.append(f"{where} child relator mismatch")
    if got_child != move.child:
        errors.append(f"{where} canonical child mismatch")
    return root, got_child


def _independent_replay(
    root: tuple[str, str],
    move: PostCompressionMove,
) -> tuple[str, tuple[str, str]]:
    if len(root) != 2:
        raise ValueError("root must have two relators")
    if move.target not in (0, 1):
        raise ValueError("invalid target")
    if move.sign not in (1, -1):
        raise ValueError("invalid sign")
    other_index = 1 - move.target
    target_rotations = _left_rotations(root[move.target])
    other = (
        root[other_index]
        if move.sign == 1
        else _independent_inverse(root[other_index])
    )
    other_rotations = _left_rotations(other)
    target_word = target_rotations[move.target_rotation]
    other_word = other_rotations[move.other_rotation]
    child_relator = _independent_cyclic_reduce(target_word + other_word)
    child = (
        canon_pair(child_relator, root[other_index])
        if move.target == 0
        else canon_pair(root[other_index], child_relator)
    )
    return child_relator, child


def _independent_inverse(word: str) -> str:
    return "".join(letter.swapcase() for letter in reversed(word))


def _independent_cyclic_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    while len(stack) >= 2 and stack[0] == stack[-1].swapcase():
        stack = stack[1:-1]
    return "".join(stack)


def _left_rotations(word: str) -> tuple[str, ...]:
    reduced = _independent_cyclic_reduce(word)
    if not reduced:
        return ("",)
    return tuple(
        reduced[offset:] + reduced[:offset]
        for offset in range(len(reduced))
    )


def _certificate_from_census(
    census: PostCompressionCensus,
) -> dict[str, object]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    floor_by_child: dict[tuple[str, str], int] = {}
    for record in census.aut_records:
        floor_by_child[record.child] = record.minimum_total
        orbit = grouped.setdefault(
            record.representative,
            {
                "minimum_total": record.minimum_total,
                "representative": list(record.representative),
                "children": [],
            },
        )
        orbit["children"].append(
            {"child": list(record.child), "phi": record.phi}
        )
    aut_orbits = [grouped[key] for key in sorted(grouped)]

    root_records = [aut_canon(root) for root in census.roots]
    root_floor_distribution = Counter(record[0] for record in root_records)
    minimum_root = min(root_floor_distribution) if root_records else None
    minimum_child = census.minimum_child_floor
    minimum_edges = [
        edge.to_json()
        for edge in census.edges
        if floor_by_child[edge.move.child] == minimum_child
    ]
    return {
        "schema": SCHEMA,
        "claim": (
            "finite decision of one full classical AC multiplication "
            "after the certified one-edge compression"
        ),
        "upstream_trace": census.upstream_trace,
        "roots": [list(root) for root in census.roots],
        "root_count": census.root_count,
        "root_floor_distribution": {
            str(floor): count
            for floor, count in sorted(root_floor_distribution.items())
        },
        "minimum_root_floor": minimum_root,
        "literal_move_count": census.literal_move_count,
        "distinct_root_child_count": census.distinct_root_child_count,
        "distinct_child_count": census.distinct_child_count,
        "trace_sha256": census.trace_sha256,
        "floor_distribution": {
            str(floor): count
            for floor, count in sorted(census.floor_distribution.items())
        },
        "minimum_child_floor": minimum_child,
        "edges": [edge.to_json() for edge in census.edges],
        "aut_orbits": aut_orbits,
        "minimum_edges": minimum_edges,
        "strict_local_minimum": (
            minimum_root is not None
            and minimum_child is not None
            and minimum_child > minimum_root
        ),
        "candidate_lemma": (
            "PROVED"
            if minimum_child is not None and minimum_child <= 12
            else "REFUTED"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    args = parser.parse_args()
    if args.verify:
        with args.output.open() as handle:
            data = json.load(handle)
        verify_certificate(data)
        print(
            "CERTIFICATE VERIFIES: "
            f"{data['root_count']} roots, "
            f"{data['distinct_child_count']} children, "
            f"minimum {data['minimum_child_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['root_count']} roots, "
        f"{data['distinct_child_count']} children, "
        f"minimum {data['minimum_child_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
