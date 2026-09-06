import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_collapse import presentation_complex, staircase_prism
from experiments.stable_ac.ak3_prism_shell_reduction import (
    reduce_core, shell_candidates, shell_trace, verify_trace,
)


def closure(simplices):
    result = set()
    for simplex in simplices:
        vertices = tuple(sorted(set(simplex)))
        for mask in range(1, 1 << len(vertices)):
            result.add(tuple(vertex for index, vertex in enumerate(vertices) if mask & (1 << index)))
    return result


def replay(initial, trace):
    current = {frozenset(simplex) for simplex in initial}
    for kind, upper, lower in trace:
        upper, lower = frozenset(upper), frozenset(lower)
        assert 0 < len(lower) == len(upper) - 1 and lower < upper and len(upper) <= 4
        if kind == "expand":
            assert upper not in current and lower not in current
            all_faces = {frozenset(face) for face in closure((upper,))}
            assert all_faces - {upper, lower} <= current
            current.update((upper, lower))
            assert {face for face in current if lower < face} == {upper}
        else:
            assert kind == "collapse" and upper in current and lower in current
            assert {face for face in current if lower < face} == {upper}
            current.difference_update((upper, lower))
        assert current == {frozenset(face) for face in closure(current)}
    return {tuple(sorted(simplex)) for simplex in current}


def euler(complex_faces):
    return sum((-1) ** (len(face) - 1) for face in complex_faces)


def test_three_face_fan_has_an_exact_shell_and_standard_disk_reaches_a_point():
    fan = closure(((0, 1, 2), (0, 1, 3), (0, 2, 3)))
    candidate = ((0, 1, 2, 3), (1, 2, 3), (0, 1, 2), (0, 1))
    assert candidate in shell_candidates(fan)
    trace = shell_trace(fan, candidate)
    assert trace == (("expand", (0, 1, 2, 3), (1, 2, 3)),
                     ("collapse", (0, 1, 2, 3), (0, 1, 2)),
                     ("collapse", (0, 1, 3), (0, 1)))
    endpoint = replay(fan, trace)
    assert verify_trace(fan, trace, endpoint) == endpoint
    assert len(endpoint) == len(fan) - 2
    assert sum(len(face) == 2 for face in endpoint) == sum(len(face) == 2 for face in fan) - 1
    assert sum(len(face) == 3 for face in endpoint) == 2
    assert euler(endpoint) == euler(fan) == 1
    disk = closure(((0, 1, 2),))
    reduction = reduce_core(disk)
    point = replay(disk, reduction.trace)
    assert point == closure(reduction.remaining_maximal_simplices)
    assert reduction.success and len(point) == 1 and len(next(iter(point))) == 1
    assert reduction.remaining_f_vector == (1,)


def test_shell_shared_edge_degree_guard_and_missing_face_expansion_control():
    guarded = closure(((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 1, 4)))
    assert all(candidate[3] != (0, 1) for candidate in shell_candidates(guarded))
    bad_candidate = ((0, 1, 2, 3), (1, 2, 3), (0, 1, 2), (0, 1))
    try:
        shell_trace(guarded, bad_candidate)
    except AssertionError as error:
        assert "guards" in str(error)
    else:
        raise AssertionError("the degree-three shared edge was accepted")
    two_faces = closure(((0, 1, 2), (0, 1, 3)))
    try:
        verify_trace(two_faces, (("expand", (0, 1, 2, 3), (1, 2, 3)),))
    except AssertionError as error:
        assert "another missing face" in str(error)
    else:
        raise AssertionError("the expansion with two missing triangular faces was accepted")


def test_sphere_and_circle_controls_remain_nonpoint_with_their_euler_values():
    sphere = closure(((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)))
    circle = closure(((0, 1), (0, 2), (1, 2)))
    for initial, expected_euler in ((sphere, 2), (circle, 0)):
        result = reduce_core(initial)
        endpoint = replay(initial, result.trace)
        assert endpoint == closure(result.remaining_maximal_simplices)
        assert not result.success
        assert result.shell_count == result.ordinary_count == 0
        assert euler(initial) == euler(endpoint) == expected_euler
        assert verify_trace(initial, result.trace, endpoint) == endpoint


def test_saved_ak3_shell_pass_has_independent_replay_and_terminal_guards():
    directory = Path(__file__).resolve().parents[2] / "results/stable_ac/theory"
    original = json.loads((directory / "ak3_prism_collapse_20260906.json").read_text(encoding="utf-8"))
    artifact = json.loads((directory / "ak3_prism_shell_reduction_20260906.json").read_text(encoding="utf-8"))
    assert original["words"] == ["xxxYYYY", "xyxYXY"]
    prism = staircase_prism(presentation_complex(tuple(original["words"])).simplices)
    assert prism == closure(prism)
    old_pairs = original["attempt"]["pairs"]
    assert len(old_pairs) == 610
    core = replay(prism, (("collapse", upper, lower) for upper, lower in old_pairs))
    assert core == closure(original["attempt"]["remaining_maximal_simplices"])
    assert [sum(len(face) == size for face in core) for size in (1, 2, 3)] == artifact["input_f_vector"] == [78, 273, 196]
    result = artifact["reduction"]
    trace = result["trace"]
    assert len(trace) == 97
    expansion_count = sum(kind == "expand" for kind, _, _ in trace)
    assert expansion_count == result["shell_count"] == 23
    assert len(trace) - 3 * expansion_count == result["ordinary_count"] == 28
    endpoint = replay(core, trace)
    maximal = {tuple(face) for face in result["remaining_maximal_simplices"]}
    assert endpoint == closure(maximal) == closure(endpoint)
    frozen = {frozenset(face) for face in endpoint}
    assert maximal == {tuple(sorted(face)) for face in frozen if not any(face < other for other in frozen)}
    assert [sum(len(face) == size for face in endpoint) for size in (1, 2, 3)] == result["remaining_f_vector"] == [66, 222, 157]
    assert max(map(len, endpoint)) == 3
    assert euler(prism) == euler(core) == euler(endpoint) == 1
    is_point = len(endpoint) == 1 and len(next(iter(endpoint))) == 1
    assert result["success"] == is_point is False
    for face in frozen:
        cofaces = {other for other in frozen if face < other}
        assert not (len(cofaces) == 1 and len(next(iter(cofaces))) == len(face) + 1)
        if len(face) != 2 or len(cofaces) != 2 or any(len(other) != 3 for other in cofaces):
            continue
        first, second = tuple(cofaces)
        tetrahedron = first | second
        assert len(tetrahedron) == 4
        other_triangles = {tetrahedron - {vertex} for vertex in tetrahedron} - cofaces
        assert len(other_triangles) == 2
        assert sum(triangle in frozen for triangle in other_triangles) != 1
