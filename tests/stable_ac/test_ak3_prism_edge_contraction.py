import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_edge_contraction import (
    contraction_trace, edge_condition, reduce_core,
)


def closure(simplices):
    result = set()
    for simplex in simplices:
        vertices = sorted(set(simplex))
        for mask in range(1, 1 << len(vertices)):
            result.add(frozenset(vertex for index, vertex in enumerate(vertices) if mask & (1 << index)))
    return result


def tuples(faces):
    return {tuple(sorted(face)) for face in faces}


def replay(initial, trace):
    current = {frozenset(face) for face in initial}
    assert current == closure(current) and all(len(face) <= 4 for face in current)
    for kind, upper, lower in trace:
        upper, lower = frozenset(upper), frozenset(lower)
        assert lower and lower < upper and len(upper) == len(lower) + 1 and len(upper) <= 4
        if kind == "expand":
            assert upper not in current and lower not in current
            assert closure((upper,)) - {upper, lower} <= current
            current.update((upper, lower))
            assert {face for face in current if lower < face} == {upper}
        else:
            assert kind == "collapse" and upper in current and lower in current
            assert {face for face in current if lower < face} == {upper}
            current.difference_update((upper, lower))
        assert current == closure(current)
    return current


def test_edge_contraction_with_expansions_and_triangle_disk():
    for initial in (closure(((0, 1), (1, 2, 3))), closure(((0, 1, 2),))):
        source = tuples(initial)
        assert edge_condition(source, (0, 1))
        trace = contraction_trace(source, (0, 1))
        endpoint = replay(initial, trace)
        expected = {frozenset(0 if vertex == 1 else vertex for vertex in face) for face in initial}
        assert endpoint == expected == closure(expected)
        assert sum(len(face) == 1 for face in endpoint) == sum(len(face) == 1 for face in initial) - 1
        assert len(endpoint) <= len(initial) - 2
        assert trace[-1] == ("collapse", (0, 1), (1,))
        if frozenset((1, 2, 3)) in initial:
            assert any(kind == "expand" and len(upper) == 4 for kind, upper, _ in trace)
        result = reduce_core(source)
        point = replay(initial, result.trace)
        assert result.success and len(point) == 1 and len(next(iter(point))) == 1
        assert point == closure(result.remaining_maximal_simplices)
        assert result.remaining_f_vector == (1,)
        assert len(result.blocks) == result.ordinary_count + result.shell_count + result.contraction_count
        assert len(result.blocks) <= (len(initial) - 1) // 2
        cursor = 0
        for block in result.blocks:
            assert block["start"] == cursor < block["end"]
            cursor = block["end"]
        assert cursor == len(result.trace)


def test_full_link_condition_rejects_triangle_and_tetrahedron_boundaries():
    circle = closure(((0, 1), (0, 2), (1, 2)))
    sphere = closure(((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)))
    for initial, characteristic in ((circle, 0), (sphere, 2)):
        source = tuples(initial)
        for edge in (face for face in source if len(face) == 2):
            assert not edge_condition(source, edge)
            try:
                contraction_trace(source, edge)
            except AssertionError as error:
                assert "link condition" in str(error)
            else:
                raise AssertionError("a boundary edge without the full link condition was contracted")
        result = reduce_core(source)
        endpoint = replay(initial, result.trace)
        assert endpoint == initial == closure(result.remaining_maximal_simplices)
        assert not result.success and not result.trace and not result.blocks
        assert result.ordinary_count == result.shell_count == result.contraction_count == 0
        assert sum((-1) ** (len(face) - 1) for face in endpoint) == characteristic
    assert all(frozenset((0, 1, vertex)) in sphere for vertex in (2, 3))
    assert frozenset((0, 2, 3)) in sphere and frozenset((1, 2, 3)) in sphere
    assert frozenset((0, 1, 2, 3)) not in sphere


def independent_ec(faces, edge):
    u, v = edge
    edge = frozenset(edge)
    if edge not in faces:
        return False
    link_u = {face - {u} for face in faces if u in face}
    link_v = {face - {v} for face in faces if v in face}
    link_edge = {face - edge for face in faces if edge <= face}
    assert frozenset() in link_u & link_v & link_edge
    return link_u & link_v == link_edge


def test_saved_edge_pass_has_independent_provenance_blocks_and_terminal_guards():
    directory = Path(__file__).resolve().parents[2] / "results/stable_ac/theory"
    original = json.loads((directory / "ak3_prism_collapse_20260906.json").read_text(encoding="utf-8"))
    shell = json.loads((directory / "ak3_prism_shell_reduction_20260906.json").read_text(encoding="utf-8"))
    artifact = json.loads((directory / "ak3_prism_edge_contraction_20260906.json").read_text(encoding="utf-8"))
    assert original["words"] == ["xxxYYYY", "xyxYXY"]
    cycles = {"x": (1, 2, 0), "X": (2, 1, 0), "y": (3, 4, 0), "Y": (4, 3, 0)}
    cells = [(0, 1), (1, 2), (0, 2), (0, 3), (3, 4), (0, 4)]
    next_vertex = 5
    for word in original["words"]:
        walk = [0] + [vertex for letter in word for vertex in cycles[letter]]
        domain = list(range(next_vertex, next_vertex + 3 * len(word)))
        apex = next_vertex + len(domain)
        next_vertex = apex + 1
        for index, vertex in enumerate(domain):
            following = domain[(index + 1) % len(domain)]
            cells.extend(((walk[index], walk[index + 1], following),
                          (walk[index], vertex, following), (apex, vertex, following)))
    base = closure(cells)
    staircases = []
    for face in base:
        vertices = sorted(face)
        for pivot in range(len(vertices)):
            staircases.append([2 * vertex for vertex in vertices[:pivot + 1]]
                              + [2 * vertex + 1 for vertex in vertices[pivot:]])
    prism = closure(staircases)
    assert [sum(len(face) == size for face in prism) for size in (1, 2, 3, 4)] == [92, 532, 792, 351]
    old_pairs = original["attempt"]["pairs"]
    assert len(old_pairs) == 610
    current = replay(prism, (("collapse", upper, lower) for upper, lower in old_pairs))
    assert current == closure(original["attempt"]["remaining_maximal_simplices"])
    assert len(shell["reduction"]["trace"]) == 97
    current = replay(current, shell["reduction"]["trace"])
    assert current == closure(shell["reduction"]["remaining_maximal_simplices"])
    assert [sum(len(face) == size for face in current) for size in (1, 2, 3)] == artifact["input_f_vector"] == [66, 222, 157]
    initial = current
    result = artifact["reduction"]
    trace, blocks = result["trace"], result["blocks"]
    assert len(trace) == 592
    counts = {"contraction": 0, "shell": 0, "ordinary": 0}
    cursor = 0
    for block in blocks:
        assert block["start"] == cursor < block["end"] <= len(trace)
        operations = trace[cursor:block["end"]]
        before = current
        kind = block["kind"]
        counts[kind] += 1
        if kind == "contraction":
            u, v = block["edge"]
            assert u < v and independent_ec(before, (u, v))
            expected = {frozenset(u if vertex == v else vertex for vertex in face) for face in before}
        elif kind == "ordinary":
            assert len(operations) == 1 and operations[0][0] == "collapse"
        else:
            assert kind == "shell" and [operation[0] for operation in operations] == ["expand", "collapse", "collapse"]
        current = replay(before, operations)
        assert len(current) <= len(before) - 2 and max(map(len, current)) <= 3
        if kind == "contraction":
            assert current == expected
            assert sum(len(face) == 1 for face in current) == sum(len(face) == 1 for face in before) - 1
        cursor = block["end"]
    assert cursor == len(trace)
    assert counts == {"contraction": 46, "shell": 3, "ordinary": 3}
    assert all(result[kind + "_count"] == count for kind, count in counts.items())
    assert len(blocks) <= (len(initial) - 1) // 2 == 222
    maximal = {frozenset(face) for face in result["remaining_maximal_simplices"]}
    assert current == closure(maximal) == closure(current)
    assert maximal == {face for face in current if not any(face < other for other in current)}
    assert [sum(len(face) == size for face in current) for size in (1, 2, 3)] == result["remaining_f_vector"] == [19, 78, 60]
    assert sum((-1) ** (len(face) - 1) for face in current) == 1
    is_point = len(current) == 1 and len(next(iter(current))) == 1
    assert result["success"] == is_point is False
    for face in current:
        cofaces = {other for other in current if face < other}
        assert not (len(cofaces) == 1 and len(next(iter(cofaces))) == len(face) + 1)
        if len(face) != 2:
            continue
        assert not independent_ec(current, sorted(face))
        if len(cofaces) == 2 and all(len(other) == 3 for other in cofaces):
            first, second = tuple(cofaces)
            tetrahedron = first | second
            other_triangles = {tetrahedron - {vertex} for vertex in tetrahedron} - cofaces
            assert len(tetrahedron) == 4 and len(other_triangles) == 2
            assert sum(triangle in current for triangle in other_triangles) != 1
