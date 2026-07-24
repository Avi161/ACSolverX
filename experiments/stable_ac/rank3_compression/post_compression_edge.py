"""Complete one-edge image of the certified AK(3) compression endpoints."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.rank3_compression.one_edge import (
    cyclic_reduce,
    rotations,
)
from experiments.stable_ac.rank3_compression.two_stabilization import inverse


ROOT = Path(__file__).resolve().parents[3]
UPSTREAM_PATH = ROOT / "results/stable_ac/theory/ak3_one_edge.json"
UPSTREAM_SCHEMA = "ak3-one-edge-v1"


@dataclass(frozen=True)
class PostCompressionMove:
    target: int
    sign: int
    target_rotation: int
    other_rotation: int
    child_relator: str
    child: tuple[str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "target": self.target,
            "sign": self.sign,
            "target_rotation": self.target_rotation,
            "other_rotation": self.other_rotation,
            "child_relator": self.child_relator,
            "child": list(self.child),
        }


@dataclass(frozen=True)
class PostCompressionEdge:
    root: tuple[str, str]
    move: PostCompressionMove

    def to_json(self) -> dict[str, object]:
        return {
            "root": list(self.root),
            "move": self.move.to_json(),
        }


@dataclass(frozen=True)
class PostCompressionAutRecord:
    child: tuple[str, str]
    minimum_total: int
    representative: tuple[str, str]
    phi: dict[str, str]


@dataclass(frozen=True)
class PostCompressionCensus:
    roots: tuple[tuple[str, str], ...]
    upstream_trace: str
    literal_move_count: int
    edges: tuple[PostCompressionEdge, ...]
    aut_records: tuple[PostCompressionAutRecord, ...]
    floor_distribution: dict[int, int]
    trace_sha256: str

    @property
    def root_count(self) -> int:
        return len(self.roots)

    @property
    def distinct_root_child_count(self) -> int:
        return len(self.edges)

    @property
    def distinct_child_count(self) -> int:
        return len(self.aut_records)

    @property
    def minimum_child_floor(self) -> int | None:
        if not self.aut_records:
            return None
        return min(record.minimum_total for record in self.aut_records)


def load_upstream_roots(
    path: Path = UPSTREAM_PATH,
) -> tuple[tuple[tuple[str, str], ...], str]:
    with path.open() as handle:
        data = json.load(handle)
    if data.get("schema") != UPSTREAM_SCHEMA:
        raise ValueError("upstream one-edge certificate has wrong schema")
    trace = data.get("trace_sha256")
    if not isinstance(trace, str) or len(trace) != 64:
        raise ValueError("upstream one-edge certificate has invalid trace")
    aut_orbits = data.get("aut_orbits")
    if not isinstance(aut_orbits, list):
        raise ValueError("upstream one-edge certificate has no Aut records")
    roots: set[tuple[str, str]] = set()
    for orbit in aut_orbits:
        if not isinstance(orbit, dict):
            raise ValueError("malformed upstream Aut orbit")
        outputs = orbit.get("outputs")
        if not isinstance(outputs, list):
            raise ValueError("malformed upstream Aut outputs")
        for row in outputs:
            if not isinstance(row, dict):
                raise ValueError("malformed upstream output")
            output = tuple(row.get("output", ()))
            if len(output) != 2 or canon(*output) != output:
                raise ValueError("upstream output is not a canonical pair")
            roots.add(output)
    return tuple(sorted(roots)), trace


def literal_children(root: tuple[str, str]):
    if len(root) != 2 or any(not relator for relator in root):
        raise ValueError("root must contain two nonempty relators")
    for target in (0, 1):
        other = 1 - target
        target_rotations = rotations(root[target])
        for sign in (1, -1):
            other_word = (
                root[other] if sign == 1 else inverse(root[other])
            )
            other_rotations = rotations(other_word)
            for target_offset, target_word in enumerate(target_rotations):
                for other_offset, rotated_other in enumerate(
                    other_rotations
                ):
                    child_relator = cyclic_reduce(
                        target_word + rotated_other
                    )
                    child = (
                        canon(child_relator, root[other])
                        if target == 0
                        else canon(root[other], child_relator)
                    )
                    yield PostCompressionMove(
                        target=target,
                        sign=sign,
                        target_rotation=target_offset,
                        other_rotation=other_offset,
                        child_relator=child_relator,
                        child=child,
                    )


def apply_post_compression_move(
    root: tuple[str, str],
    move: PostCompressionMove,
) -> tuple[str, str]:
    if move.target not in (0, 1):
        raise ValueError("target must be 0 or 1")
    if move.sign not in (1, -1):
        raise ValueError("sign must be +1 or -1")
    other = 1 - move.target
    target_rotations = rotations(root[move.target])
    signed_other = (
        root[other] if move.sign == 1 else inverse(root[other])
    )
    other_rotations = rotations(signed_other)
    try:
        target_word = target_rotations[move.target_rotation]
        other_word = other_rotations[move.other_rotation]
    except IndexError as exc:
        raise ValueError("rotation offset out of range") from exc
    child_relator = cyclic_reduce(target_word + other_word)
    child = (
        canon(child_relator, root[other])
        if move.target == 0
        else canon(root[other], child_relator)
    )
    if child_relator != move.child_relator:
        raise ValueError("stored child relator does not replay")
    if child != move.child:
        raise ValueError("stored canonical child does not replay")
    return child


def enumerate_post_compression_edges(
    roots: tuple[tuple[str, str], ...] | None = None,
    upstream_trace: str | None = None,
) -> PostCompressionCensus:
    if roots is None:
        roots, loaded_trace = load_upstream_roots()
        upstream_trace = loaded_trace
    roots = tuple(sorted(set(roots)))
    if upstream_trace is None:
        raise ValueError("upstream_trace is required for explicit roots")

    trace = sha256()
    trace.update(b"UPSTREAM\0" + upstream_trace.encode("ascii") + b"\n")
    literal_move_count = 0
    first_by_edge: dict[
        tuple[tuple[str, str], tuple[str, str]],
        PostCompressionEdge,
    ] = {}
    for root in roots:
        for move in literal_children(root):
            literal_move_count += 1
            edge_key = (root, move.child)
            is_new = edge_key not in first_by_edge
            trace.update(
                b"E\0"
                + "\0".join(
                    (
                        *root,
                        str(move.target),
                        str(move.sign),
                        str(move.target_rotation),
                        str(move.other_rotation),
                        move.child_relator,
                        *move.child,
                        "1" if is_new else "0",
                    )
                ).encode("ascii")
                + b"\n"
            )
            first_by_edge.setdefault(
                edge_key,
                PostCompressionEdge(root=root, move=move),
            )

    children = sorted({child for _, child in first_by_edge})
    aut_records: list[PostCompressionAutRecord] = []
    for child in children:
        minimum_total, representative, phi = aut_canon(child)
        aut_records.append(
            PostCompressionAutRecord(
                child=child,
                minimum_total=minimum_total,
                representative=representative,
                phi=phi,
            )
        )
    floor_distribution = Counter(
        record.minimum_total for record in aut_records
    )
    return PostCompressionCensus(
        roots=roots,
        upstream_trace=upstream_trace,
        literal_move_count=literal_move_count,
        edges=tuple(first_by_edge[key] for key in sorted(first_by_edge)),
        aut_records=tuple(aut_records),
        floor_distribution=dict(sorted(floor_distribution.items())),
        trace_sha256=trace.hexdigest(),
    )
