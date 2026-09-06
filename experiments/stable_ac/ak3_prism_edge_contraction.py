"""A recorded deterministic pass of certified three-deformation blocks."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_collapse import face_closure, f_vector
from experiments.stable_ac.ak3_prism_shell_reduction import (
    proper_cofaces, shell_candidates, shell_trace, verify_trace,
)


def edge_condition(complex_faces, edge):
    edge = tuple(edge)
    if len(edge) != 2 or edge != tuple(sorted(set(edge))) or edge not in complex_faces:
        return False
    u, v = edge
    for face in complex_faces:
        if v not in face or u in face:
            continue
        sigma = set(face) - {v}
        if tuple(sorted(sigma | {u})) in complex_faces and tuple(sorted(sigma | {u, v})) not in complex_faces:
            return False
    return True


def contraction_trace(initial, edge):
    current = set(initial)
    if face_closure(current) != current or any(len(face) > 3 for face in current):
        raise AssertionError("contraction requires a closed two-complex")
    if not edge_condition(current, edge):
        raise AssertionError("edge contraction fails the full link condition")
    u, v = edge
    link_faces = {tuple(vertex for vertex in face if vertex != v)
                  for face in current if v in face and u not in face}
    trace = []
    for sigma in sorted(link_faces, key=lambda face: (len(face), face)):
        lower = tuple(sorted((u,) + sigma))
        if lower not in initial:
            trace.append(("expand", tuple(sorted((u, v) + sigma)), lower))
    for sigma in sorted(link_faces, key=lambda face: (-len(face), face)):
        trace.append(("collapse", tuple(sorted((u, v) + sigma)), tuple(sorted((v,) + sigma))))
    expected = {tuple(sorted({u if vertex == v else vertex for vertex in face})) for face in initial}
    endpoint = verify_trace(current, trace, expected)
    if sum(len(face) == 1 for face in endpoint) != sum(len(face) == 1 for face in initial) - 1:
        raise AssertionError("contraction did not remove exactly one vertex")
    if len(endpoint) > len(initial) - 2 or any(len(face) > 3 for face in endpoint):
        raise AssertionError("contraction did not strictly reduce the two-complex")
    return tuple(trace)


@dataclass(frozen=True)
class EdgeReduction:
    trace: tuple
    blocks: tuple
    ordinary_count: int
    shell_count: int
    contraction_count: int
    remaining_maximal_simplices: tuple
    remaining_f_vector: tuple
    success: bool


def reduce_core(initial):
    current = set(initial)
    if not current or face_closure(current) != current or any(len(face) > 3 for face in current):
        raise AssertionError("the input must be a nonempty closed two-complex")
    vertex_bound = sum(len(face) == 1 for face in current) - 1
    block_bound = (len(current) - 1) // 2
    trace, blocks = [], []
    counts = {"ordinary": 0, "shell": 0, "contraction": 0}
    while True:
        free = []
        for lower in current:
            cofaces = proper_cofaces(current, lower)
            if len(cofaces) == 1:
                upper = next(iter(cofaces))
                if len(upper) == len(lower) + 1:
                    free.append((upper, lower))
        edge = None
        if free:
            upper, lower = min(free, key=lambda pair: (-len(pair[0]), pair[0], pair[1]))
            kind, operations = "ordinary", (("collapse", upper, lower),)
        else:
            shells = shell_candidates(current)
            if shells:
                kind, edge = "shell", shells[0][3]
                operations = shell_trace(current, shells[0])
            else:
                edges = sorted(face for face in current if len(face) == 2 and edge_condition(current, face))
                if not edges:
                    break
                kind, edge = "contraction", edges[0]
                operations = contraction_trace(current, edge)
        before = len(current)
        current = verify_trace(current, operations)
        if len(current) > before - 2 or any(len(face) > 3 for face in current):
            raise AssertionError("a completed block failed strict two-complex reduction")
        start = len(trace)
        trace.extend(operations)
        metadata = {"kind": kind, "start": start, "end": len(trace)}
        if edge is not None:
            metadata["edge"] = edge
        blocks.append(metadata)
        if len(blocks) > block_bound:
            raise AssertionError("completed blocks exceeded the strict face-decrease bound")
        counts[kind] += 1
        if counts["contraction"] > vertex_bound:
            raise AssertionError("contractions exceeded the initial vertex bound")
    maximal = tuple(sorted(face for face in current if not proper_cofaces(current, face)))
    success = len(current) == 1 and len(next(iter(current))) == 1
    return EdgeReduction(tuple(trace), tuple(blocks), counts["ordinary"], counts["shell"],
                         counts["contraction"], maximal, f_vector(current), success)


def data():
    source = "results/stable_ac/theory/ak3_prism_shell_reduction_20260906.json"
    artifact = json.loads((Path(__file__).resolve().parents[2] / source).read_text(encoding="utf-8"))
    core = face_closure(artifact["reduction"]["remaining_maximal_simplices"])
    if f_vector(core) != (66, 222, 157):
        raise AssertionError("the saved shell endpoint counts drifted")
    result = reduce_core(core)
    verify_trace(core, result.trace, face_closure(result.remaining_maximal_simplices))
    return {"source_artifact": source, "input_f_vector": f_vector(core), "reduction": asdict(result),
            "status": "one_deterministic_edge_contraction_pass"}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
