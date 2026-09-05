from collections import Counter

from experiments.stable_ac.ak3_fagan_fake_surface_certificate import (
    SOURCE_FACES, decide_fagan_fake_surface, validate_source_complex,
    decide_first_fourgon_endpoint, validate_endpoint_tree,
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


def test_first_fourgon_target_endpoints_and_links_are_independent():
    decision = decide_first_fourgon_endpoint()
    target = (
        (3, 15, 17, -16), (3, 11, 13, -16, 18, -12, -10),
        (-18, 10, -4, -14), (4, 12, -6, -11, 15),
        (6, 14, -15, 19, -13), (19, -16, 10, 5, -11),
        (5, 13, -17, -14, -12), (3, 19, -17, 4, 5, 6, -18),
    )
    edges = sorted(set(abs(edge) for face in target for edge in face))
    groups = [{(edge, end)} for edge in edges for end in (0, 1)]
    for face in target:
        for incoming, outgoing in zip(face, face[1:] + face[:1]):
            head, tail = (abs(incoming), int(incoming > 0)), (abs(outgoing), int(outgoing < 0))
            left = next(group for group in groups if head in group)
            right = next(group for group in groups if tail in group)
            if left is not right:
                merged = left | right
                groups = [group for group in groups if group is not left and group is not right] + [merged]
    assert len(groups) == 7 and len(edges) == 14
    counts = Counter(abs(edge) for face in target for edge in face)
    assert set(counts.values()) == {3}
    assert tuple(sorted(counts.items())) == decision.target_audit.edge_occurrences
    vertex_of = {endpoint: index for index, group in enumerate(groups) for endpoint in group}
    endpoints = {edge: (vertex_of[(edge, 0)], vertex_of[(edge, 1)]) for edge in edges}
    production = {edge: (start, end) for edge, start, end in decision.target_audit.endpoints}
    for edge in edges:
        for other in edges:
            for side in (0, 1):
                for other_side in (0, 1):
                    assert (endpoints[edge][side] == endpoints[other][other_side]) == (
                        production[edge][side] == production[other][other_side])
    links = {vertex: [] for vertex in range(7)}
    for face in target:
        for incoming, outgoing in zip(face, face[1:] + face[:1]):
            vertex = vertex_of[(abs(incoming), int(incoming > 0))]
            assert vertex == vertex_of[(abs(outgoing), int(outgoing < 0))]
            links[vertex].append(tuple(sorted((-incoming, outgoing))))
    for corners in links.values():
        germs = sorted(set(germ for corner in corners for germ in corner))
        assert len(germs) == 4
        assert Counter(corners) == Counter((left, right) for left in germs for right in germs if left < right)
    assert decision.source_tree == (2, 4, 7, 8, 9, 11)
    assert decision.target_tree == (4, 11, 15, 16, 18, 19)
    for audit, tree in ((decision.source_audit, decision.source_tree),
                        (decision.target_audit, decision.target_tree)):
        ends = {edge: (start, end) for edge, start, end in audit.endpoints}
        assert len(set(tree)) == 6
        reached = {0}
        for _ in range(7):
            reached |= {other for edge in tree for at, other in (ends[edge], ends[edge][::-1]) if at in reached}
        assert reached == set(range(7))
    try:
        validate_endpoint_tree(decision.target_audit, decision.target_tree[:-1])
    except AssertionError as error:
        assert "six distinct" in str(error)
    else:
        raise AssertionError("the incomplete endpoint tree was accepted")


def test_first_fourgon_collapsed_words_and_donor_identity_are_independent():
    decision = decide_first_fourgon_endpoint()
    source = ((1, -3), (3, 13, -12, -10), (10, -14), (12, -6),
              (6, 14, -13), (10, 5), (5, 13, 1, -14, -12), (1, 3, 5, 6))
    target_faces = (
        (3, 15, 17, -16), (3, 11, 13, -16, 18, -12, -10),
        (-18, 10, -4, -14), (4, 12, -6, -11, 15),
        (6, 14, -15, 19, -13), (19, -16, 10, 5, -11),
        (5, 13, -17, -14, -12), (3, 19, -17, 4, 5, 6, -18),
    )

    def reduced(word):
        result = []
        for letter in word:
            if result and result[-1] + letter == 0:
                result.pop()
            else:
                result.append(letter)
        return tuple(result)

    def inverse(word):
        return tuple(-letter for letter in word[::-1])

    collapsed_source = tuple(reduced(tuple(edge for edge in face if abs(edge) not in (2, 4, 7, 8, 9, 11)))
                             for face in LITERAL_FACES)
    collapsed_target = tuple(reduced(tuple({17: -1, -17: 1}.get(edge, edge) for edge in face
                                          if abs(edge) not in (4, 11, 15, 16, 18, 19))) for face in target_faces)
    assert collapsed_source == decision.source_collapsed == source
    assert collapsed_target == decision.target_collapsed == (inverse(source[0]),) + source[1:-1] + ((3, 1, 5, 6),)
    defect = reduced(source[-1] + inverse(collapsed_target[-1]))
    product = reduced(source[0] + (3,) + inverse(source[0]) + (-3,))
    assert defect == product == (1, 3, -1, -3)
    assert decision.defect == decision.product == defect
    assert reduced(source[0] + (1,) + inverse(source[0]) + (-1,)) != defect
    assert decision.geometric_local_rewrite_certified is False
    assert decision.complexity_reduction_claimed is False
    assert decision.verdict == "FIRST_FOURGON_ENDPOINT_PRESENTATION_EQUIVALENCE_ONLY"
