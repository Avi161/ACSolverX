from collections import Counter

from experiments.stable_ac.ak3_fagan_fake_surface_certificate import (
    SOURCE_FACES, decide_fagan_fake_surface, validate_source_complex,
)


LITERAL_FACES = (
    (1, 9, -3, -8), (3, 11, 13, -7, -12, -10),
    (7, 8, 10, -4, -9, -14), (4, 12, -6, -11),
    (6, 14, 2, -8, -13), (2, 10, 5, -11, -9),
    (5, 13, 1, -14, -12), (1, 2, 3, 4, 5, 6, 7),
)
LITERAL_ENDPOINTS = (
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 1),
    (1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 1), (7, 2),
)


def test_fagan_literal_endpoint_and_link_constraints_are_independent():
    assert SOURCE_FACES == LITERAL_FACES
    audit = validate_source_complex()
    occurrences = Counter()
    links = {vertex: [] for vertex in range(1, 8)}
    for face_index, face in enumerate(LITERAL_FACES):
        path = [LITERAL_ENDPOINTS[abs(edge) - 1][::1 if edge > 0 else -1] for edge in face]
        vertices = tuple(start for start, _ in path)
        assert len(set(vertices)) == len(face)
        assert audit.boundary_vertices[face_index] == vertices
        for index, edge in enumerate(face):
            following = (index + 1) % len(face)
            assert path[index][1] == path[following][0]
            occurrences[abs(edge)] += 1
            links[path[index][1]].append(tuple(sorted((-edge, face[following]))))
    assert occurrences == {edge: 3 for edge in range(1, 15)}
    for vertex, edges in links.items():
        germs = sorted(set(germ for edge in edges for germ in edge))
        assert len(germs) == 4 and len(edges) == 6
        assert len(set(edges)) == 6
        for left in germs:
            assert {right if first == left else first for first, right in edges if left in (first, right)} == set(germs) - {left}
        assert tuple(sorted(edges)) == audit.vertex_links[vertex - 1]
    assert audit.euler_characteristic == 7 - 14 + 8 == 1


def test_fagan_sheet_transport_has_independent_signed_triple_replay():
    decision = decide_fagan_fake_surface()
    assert tuple(t.monodromy for t in decision.sheet_transports) == (
        "identity", "identity", "identity", "identity", "swap", "identity", "swap", "identity",
    )
    triples = {}
    for face_index, face in enumerate(LITERAL_FACES):
        reverse = tuple(-edge for edge in face[::-1])
        for orientation in (face, reverse):
            for index, edge in enumerate(orientation):
                triples[(face_index, edge)] = (orientation[index - 1], edge,
                                               orientation[(index + 1) % len(orientation)])
    for transport in decision.sheet_transports:
        core_index = transport.core_face
        core = LITERAL_FACES[core_index]
        initial_sides = tuple(index for index, face in enumerate(LITERAL_FACES)
                              if index != core_index and abs(core[0]) in tuple(map(abs, face)))
        assert initial_sides == transport.starting_side_faces
        replayed = []
        for initial in initial_sides:
            side, trace = initial, [initial]
            for index, edge in enumerate(core):
                _, _, following_side_edge = triples[(side, edge)]
                next_core = core[(index + 1) % len(core)]
                candidates = [face_index for face_index in range(len(LITERAL_FACES))
                              if face_index != core_index and (face_index, next_core) in triples
                              and triples[(face_index, next_core)][0] == -following_side_edge]
                assert len(candidates) == 1
                side = candidates[0]
                trace.append(side)
            replayed.append(tuple(trace))
        assert tuple(replayed) == transport.traces
        endings = tuple(trace[-1] for trace in replayed)
        assert endings == transport.ending_side_faces
        assert transport.monodromy == ("identity" if endings == initial_sides else "swap")
    assert decision.contractibility_claimed is False
    assert decision.source_equivalence_checked is False


def test_fagan_validator_rejects_a_corrupted_edge_sign():
    corrupted = ((-1,) + LITERAL_FACES[0][1:],) + LITERAL_FACES[1:]
    try:
        validate_source_complex(corrupted)
    except AssertionError as error:
        assert "does not close" in str(error)
    else:
        raise AssertionError("the corrupted face orientation was accepted")
