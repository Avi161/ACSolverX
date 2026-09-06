import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_collapse import (
    bottom_copy, canonical_prism_pairs, face_closure, f_vector, greedy_collapse,
    presentation_complex, staircase_prism, verify_collapse,
)


def independent_closure(simplices):
    faces = set()
    for simplex in simplices:
        vertices = sorted(set(simplex))
        for mask in range(1, 1 << len(vertices)):
            faces.add(tuple(vertex for index, vertex in enumerate(vertices) if mask & (1 << index)))
    return faces


def independent_replay(initial, pairs):
    remaining = {frozenset(simplex) for simplex in initial}
    for sigma, tau in pairs:
        upper, lower = frozenset(sigma), frozenset(tau)
        assert upper in remaining and lower in remaining
        assert len(upper) == len(lower) + 1 and lower < upper
        assert {face for face in remaining if lower < face} == {upper}
        remaining.difference_update((upper, lower))
    return {tuple(sorted(simplex)) for simplex in remaining}


def euler(simplices):
    return sum(1 if len(simplex) % 2 else -1 for simplex in simplices)


def test_ak3_rose_walks_and_simplicial_prism_counts_are_independent():
    construction = presentation_complex()
    assert construction.relators == ("xxxYYYY", "xyxYXY")
    base = set(construction.simplices)
    assert base == independent_closure(base)
    cycles = {"x": (0, 1, 2, 0), "X": (0, 2, 1, 0),
              "y": (0, 3, 4, 0), "Y": (0, 4, 3, 0)}
    all_domain_vertices = set()
    triangles = set()
    for word, walk, domain, apex in zip(construction.relators, construction.walks,
                                        construction.domain_cycles, construction.apices, strict=True):
        expected_walk = (0,) + tuple(vertex for letter in word for vertex in cycles[letter][1:])
        assert walk == expected_walk and walk[-1] == 0
        recovered = "".join(next(letter for letter, cycle in cycles.items() if tuple(walk[index:index + 4]) == cycle)
                            for index in range(0, len(walk) - 1, 3))
        assert recovered == word
        assert len(domain) == 3 * len(word) and len(set(domain)) == len(domain)
        assert not (set(domain) & (all_domain_vertices | set(range(5))))
        all_domain_vertices.update(domain)
        assert apex not in all_domain_vertices and apex > 4
        for index, domain_vertex in enumerate(domain):
            following = domain[(index + 1) % len(domain)]
            triangles.update(frozenset(triangle) for triangle in (
                (walk[index], walk[index + 1], following), (walk[index], domain_vertex, following),
                (apex, domain_vertex, following)))
    assert {frozenset(face) for face in base if len(face) == 3} == triangles
    assert tuple(sum(len(face) == size for face in base) for size in (1, 2, 3)) == (46, 162, 117)
    assert euler(base) == 1
    prism = staircase_prism(base)
    assert prism == independent_closure(prism)
    assert tuple(sum(len(face) == size for face in prism) for size in (1, 2, 3, 4)) == (92, 532, 792, 351)
    assert euler(prism) == 1
    bottom = {face for face in prism if all(vertex % 2 == 0 for vertex in face)}
    assert {tuple(vertex // 2 for vertex in face) for face in bottom} == base
    assert bottom_copy(base) == bottom
    pairs = canonical_prism_pairs(base)
    assert len(pairs) == 721
    assert independent_replay(prism, pairs) == bottom
    assert verify_collapse(prism, pairs, bottom) == bottom


def test_standard_presentation_prism_collapses_to_base_then_point():
    base = set(presentation_complex(("x", "y")).simplices)
    prism = staircase_prism(base)
    bottom = bottom_copy(base)
    assert independent_replay(prism, canonical_prism_pairs(base)) == bottom
    attempt = greedy_collapse(bottom)
    remaining = independent_replay(bottom, attempt.pairs)
    assert remaining == independent_closure(attempt.remaining_maximal_simplices)
    assert attempt.success and len(remaining) == 1
    assert len(next(iter(remaining))) == 1
    assert attempt.remaining_f_vector == (1,)
    assert euler(remaining) == 1
    direct_attempt = greedy_collapse(prism)
    direct_endpoint = independent_replay(prism, direct_attempt.pairs)
    assert direct_endpoint == independent_closure(direct_attempt.remaining_maximal_simplices)
    assert direct_attempt.success and len(direct_endpoint) == 1
    assert len(next(iter(direct_endpoint))) == 1
    assert direct_attempt.remaining_f_vector == (1,)


def test_nonfree_pair_is_rejected_and_circle_prism_does_not_collapse_to_point():
    filled_triangle = independent_closure(((0, 1, 2),))
    try:
        verify_collapse(filled_triangle, (((0, 1), (0,)),))
    except AssertionError as error:
        assert "proper coface" in str(error)
    else:
        raise AssertionError("a nonfree collapse pair was accepted")
    circle = independent_closure(((0, 1), (1, 2), (0, 2)))
    prism = staircase_prism(circle)
    assert independent_replay(prism, canonical_prism_pairs(circle)) == bottom_copy(circle)
    assert euler(prism) == 0
    attempt = greedy_collapse(prism)
    remaining = independent_replay(prism, attempt.pairs)
    assert not attempt.success
    assert euler(remaining) == 0
    assert remaining == independent_closure(attempt.remaining_maximal_simplices)
    assert f_vector(remaining) == attempt.remaining_f_vector
    assert face_closure(attempt.remaining_maximal_simplices) == remaining


def test_saved_ak3_prism_attempt_has_independent_complete_replay():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_prism_collapse_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["words"] == ["xxxYYYY", "xyxYXY"]
    base = set(presentation_complex(tuple(artifact["words"])).simplices)
    prism = staircase_prism(base)
    assert artifact["base_f_vector"] == [46, 162, 117]
    assert artifact["prism_f_vector"] == [92, 532, 792, 351]
    assert artifact["canonical_pair_count"] == 721
    attempt = artifact["attempt"]
    assert attempt["seed"] == 20260906
    assert len(attempt["pairs"]) == 610
    endpoint = independent_replay(prism, attempt["pairs"])
    maximal = {tuple(simplex) for simplex in attempt["remaining_maximal_simplices"]}
    assert endpoint == independent_closure(maximal)
    actual_maximal = {simplex for simplex in endpoint if not any(set(simplex) < set(other) for other in endpoint)}
    assert maximal == actual_maximal
    counts = [sum(len(simplex) == size for simplex in endpoint) for size in (1, 2, 3)]
    assert counts == attempt["remaining_f_vector"] == [78, 273, 196]
    assert euler(endpoint) == 1
    point = len(endpoint) == 1 and len(next(iter(endpoint))) == 1
    assert attempt["success"] is point is False
    for tau in endpoint:
        proper_cofaces = [sigma for sigma in endpoint if set(tau) < set(sigma)]
        assert not (len(proper_cofaces) == 1 and len(proper_cofaces[0]) == len(tau) + 1)
