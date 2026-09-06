from collections import Counter
from itertools import combinations
import json
from pathlib import Path


def _closure(maximal_simplices):
    return {face for simplex in maximal_simplices
            for size in range(1, len(simplex) + 1)
            for face in combinations(sorted(set(simplex)), size)}


def _edge_incidence(faces):
    incidence = {edge: [] for edge in sorted(face for face in faces if len(face) == 2)}
    for triangle in sorted(face for face in faces if len(face) == 3):
        for edge in combinations(triangle, 2):
            incidence[edge].append(triangle)
    return incidence


def audit_saved_endpoint():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_prism_edge_contraction_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    faces = _closure(artifact["reduction"]["remaining_maximal_simplices"])
    incidence = _edge_incidence(faces)
    first_bad = next(({"edge": edge, "count": len(triangles),
                       "incident_triangles": tuple(triangles)}
                      for edge, triangles in incidence.items() if len(triangles) not in (2, 3)), None)
    return {"f_vector": tuple(sum(len(face) == size for face in faces)
                               for size in range(1, max(map(len, faces)) + 1)),
            "incidence_histogram": dict(sorted(Counter(map(len, incidence.values())).items())),
            "first_bad_edge": first_bad}


def test_saved_endpoint_incidence_audit_is_independently_reconstructed():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_prism_edge_contraction_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    maximal = artifact["reduction"]["remaining_maximal_simplices"]
    faces = set()
    for simplex in maximal:
        vertices = sorted(set(simplex))
        for mask in range(1, 1 << len(vertices)):
            faces.add(tuple(vertex for index, vertex in enumerate(vertices) if mask & (1 << index)))
    assert faces == _closure(maximal)
    for face in faces:
        for index in range(len(face)):
            if len(face) > 1:
                assert face[:index] + face[index + 1:] in faces
    assert tuple(sum(len(face) == size for face in faces) for size in (1, 2, 3)) == (19, 78, 60)
    assert max(map(len, faces)) == 3
    triangles = sorted(face for face in faces if len(face) == 3)
    expected = {edge: [triangle for triangle in triangles if set(edge) < set(triangle)]
                for edge in sorted(face for face in faces if len(face) == 2)}
    assert _edge_incidence(faces) == expected
    histogram = {}
    for incident in expected.values():
        histogram[len(incident)] = histogram.get(len(incident), 0) + 1
    bad_edges = [edge for edge, incident in expected.items() if len(incident) not in (2, 3)]
    first_bad = None
    if bad_edges:
        edge = bad_edges[0]
        first_bad = {"edge": edge, "count": len(expected[edge]),
                     "incident_triangles": tuple(expected[edge])}
    result = audit_saved_endpoint()
    assert result["f_vector"] == (19, 78, 60)
    assert result["incidence_histogram"] == histogram
    assert result["first_bad_edge"] == first_bad
    assert histogram == {2: 72, 3: 1, 5: 1, 6: 2, 7: 1, 9: 1}
    assert first_bad == {"edge": (0, 2), "count": 5,
                         "incident_triangles": ((0, 2, 8), (0, 2, 19), (0, 2, 24),
                                                (0, 2, 53), (0, 2, 91))}
    assert sum(histogram.values()) == 78
    assert sum(count * frequency for count, frequency in histogram.items()) == 3 * 60


def test_edge_incidence_positive_and_negative_local_controls():
    sphere = _closure(((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)))
    assert all(len(incident) == 2 for incident in _edge_incidence(sphere).values())
    three_sheets = _closure(((0, 1, 2), (0, 1, 3), (0, 1, 4)))
    assert _edge_incidence(three_sheets)[(0, 1)] == [(0, 1, 2), (0, 1, 3), (0, 1, 4)]
    assert len(_edge_incidence(three_sheets)[(0, 1)]) in (2, 3)
    four_sheets = _closure(((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 1, 5)))
    assert _edge_incidence(four_sheets)[(0, 1)] == [(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 1, 5)]
    assert len(_edge_incidence(four_sheets)[(0, 1)]) not in (2, 3)
