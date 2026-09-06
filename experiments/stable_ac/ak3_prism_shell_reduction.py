"""One deterministic collapse and tetrahedral-shell reduction pass."""

from dataclasses import asdict, dataclass
from itertools import combinations
import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_collapse import (
    face_closure, f_vector, presentation_complex, staircase_prism, verify_collapse,
)


def proper_cofaces(complex_faces, face):
    vertices = set(face)
    return {simplex for simplex in complex_faces if vertices < set(simplex)}


def verify_trace(initial, trace, expected_final=None):
    current = set(initial)
    if face_closure(current) != current or any(len(face) > 4 for face in current):
        raise AssertionError("the initial complex must be closed and at most three-dimensional")
    for kind, upper, lower in trace:
        upper, lower = tuple(upper), tuple(lower)
        if upper != tuple(sorted(set(upper))) or lower != tuple(sorted(set(lower))):
            raise AssertionError("operation simplices must have distinct sorted vertices")
        if not lower or len(upper) > 4 or len(upper) != len(lower) + 1 or not set(lower) < set(upper):
            raise AssertionError("the operation is not an allowed codimension-one pair")
        if kind == "expand":
            if upper in current or lower in current:
                raise AssertionError("both expansion simplices must be new")
            required = face_closure((upper,)) - {upper, lower}
            if not required <= current:
                raise AssertionError("an expansion has another missing face")
            current.update((upper, lower))
            if proper_cofaces(current, lower) != {upper}:
                raise AssertionError("the new lower face has an unexpected proper coface")
        elif kind == "collapse":
            if upper not in current or lower not in current or proper_cofaces(current, lower) != {upper}:
                raise AssertionError("the collapse lower face is not globally free")
            current.difference_update((upper, lower))
        else:
            raise AssertionError("unknown elementary operation")
        if face_closure(current) != current:
            raise AssertionError("an elementary operation broke face closure")
    if expected_final is not None and current != set(expected_final):
        raise AssertionError("the elementary trace endpoint drifted")
    return current


def shell_candidates(complex_faces):
    if any(len(simplex) > 3 for simplex in complex_faces):
        raise ValueError("shell candidates require a two-dimensional complex")
    candidates = []
    for edge in sorted(simplex for simplex in complex_faces if len(simplex) == 2):
        triangles = sorted(proper_cofaces(complex_faces, edge))
        if len(triangles) != 2 or any(len(triangle) != 3 for triangle in triangles):
            continue
        first, second = triangles
        sigma = tuple(sorted(set(first) | set(second)))
        if len(sigma) != 4:
            continue
        other_faces = [face for face in combinations(sigma, 3) if face not in triangles]
        missing = [face for face in other_faces if face not in complex_faces]
        if len(missing) == 1:
            candidates.append((sigma, missing[0], first, edge))
    return tuple(sorted(candidates))


def shell_trace(complex_faces, candidate):
    if candidate not in shell_candidates(complex_faces):
        raise AssertionError("the proposed shell does not satisfy the exact degree and face guards")
    sigma, missing, first, edge = candidate
    second = next(triangle for triangle in proper_cofaces(complex_faces, edge) if triangle != first)
    return (("expand", sigma, missing), ("collapse", sigma, first), ("collapse", second, edge))


@dataclass(frozen=True)
class ShellReduction:
    trace: tuple[tuple[str, tuple[int, ...], tuple[int, ...]], ...]
    shell_count: int
    ordinary_count: int
    remaining_maximal_simplices: tuple[tuple[int, ...], ...]
    remaining_f_vector: tuple[int, ...]
    success: bool


def reduce_core(initial):
    current = set(initial)
    if face_closure(current) != current or any(len(simplex) > 3 for simplex in current):
        raise AssertionError("the core input must be a closed two-dimensional complex")
    triangle_bound = sum(len(simplex) == 3 for simplex in current)
    trace, ordinary_count, shell_count = [], 0, 0
    while True:
        free = []
        for lower in current:
            cofaces = proper_cofaces(current, lower)
            if len(cofaces) == 1:
                upper = next(iter(cofaces))
                if len(upper) == len(lower) + 1:
                    free.append((upper, lower))
        if free:
            upper, lower = min(free, key=lambda pair: (-len(pair[0]), pair[0], pair[1]))
            operation = ("collapse", upper, lower)
            current = verify_trace(current, (operation,))
            trace.append(operation)
            ordinary_count += 1
            continue
        candidates = shell_candidates(current)
        if not candidates:
            break
        before = {size: sum(len(face) == size for face in current) for size in (1, 2, 3)}
        before_count = len(current)
        block = shell_trace(current, candidates[0])
        current = verify_trace(current, block)
        after = {size: sum(len(face) == size for face in current) for size in (1, 2, 3)}
        if len(current) != before_count - 2 or after != {1: before[1], 2: before[2] - 1, 3: before[3] - 1}:
            raise AssertionError("the shell block did not give its strict face decrease")
        trace.extend(block)
        shell_count += 1
        if shell_count > triangle_bound:
            raise AssertionError("the shell count exceeded the initial triangle bound")
    maximal = tuple(sorted(face for face in current if not proper_cofaces(current, face)))
    success = len(current) == 1 and len(next(iter(current))) == 1
    return ShellReduction(tuple(trace), shell_count, ordinary_count, maximal, f_vector(current), success)


def data():
    artifact_path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_prism_collapse_20260906.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    base = presentation_complex(tuple(artifact["words"]))
    prism = staircase_prism(base.simplices)
    core = face_closure(artifact["attempt"]["remaining_maximal_simplices"])
    verify_collapse(prism, artifact["attempt"]["pairs"], core)
    if f_vector(core) != (78, 273, 196):
        raise AssertionError("the saved AK3 core counts drifted")
    result = reduce_core(core)
    verify_trace(core, result.trace, face_closure(result.remaining_maximal_simplices))
    return {"source_artifact": "results/stable_ac/theory/ak3_prism_collapse_20260906.json", "input_f_vector": f_vector(core),
            "reduction": asdict(result), "status": "one_deterministic_shell_reduction_pass"}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
