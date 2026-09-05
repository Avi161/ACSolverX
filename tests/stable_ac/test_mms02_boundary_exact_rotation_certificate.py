from collections import Counter
from itertools import permutations, product

from experiments.stable_ac.mms02_boundary_exact_rotation_certificate import (
    decide_boundary_exact_rotations, enumerate_face_histogram, exact_link_data, verify_rotations,
)
from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import _build_link_data


def literal_darts(words=("txTZ", "tzTZZxZ", "zzXZt")):
    germs, a_pairing, b_pairing = [], {}, {}
    offset = 0
    for word in words:
        for index, letter in enumerate(word):
            departure, arrival = 2 * (offset + index), 2 * (offset + index) + 1
            pair = {"x": (0, 1), "z": (2, 3), "t": (4, 5)}[letter.lower()]
            germs.extend(pair if letter.islower() else pair[::-1])
            b_pairing[departure], b_pairing[arrival] = arrival, departure
            following = 2 * (offset + (index + 1) % len(word))
            a_pairing[arrival], a_pairing[following] = following, arrival
        offset += len(word)
    stars = tuple(tuple(dart for dart, germ in enumerate(germs) if germ == vertex) for vertex in range(6))
    return tuple(a_pairing[dart] for dart in range(len(germs))), tuple(b_pairing[dart] for dart in range(len(germs))), tuple(germs), stars


def test_exact_boundary_darts_pairings_and_adjacency_are_independent():
    from experiments.stable_ac.mms02_boundary_automorphism_corridor_certificate import decide_second_switch_short_killer
    source = decide_second_switch_short_killer().final_tuple
    renamed = tuple(word.translate(str.maketrans("aAbBuU", "xXzZtT")) for word in source)
    data = exact_link_data()
    a_pairing, b_pairing, germs, stars = literal_darts()
    assert data.words == ("txTZ", "tzTZZxZ", "zzXZt")
    assert data.words == renamed
    assert data.A == a_pairing
    assert data.B == b_pairing
    assert data.germ == germs
    assert tuple(data.vertex_darts[index] for index in range(6)) == stars
    assert a_pairing[:4] == (7, 2, 1, 4)
    assert tuple(map(len, stars)) == (3, 3, 8, 8, 5, 5)
    matrix = [[0] * 6 for _ in range(6)]
    for dart in range(32):
        assert a_pairing[a_pairing[dart]] == b_pairing[b_pairing[dart]] == dart
        assert a_pairing[dart] != dart and b_pairing[dart] != dart
        assert germs[b_pairing[dart]] == germs[dart] ^ 1
        matrix[germs[dart]][germs[a_pairing[dart]]] += 1
    assert all(matrix[i][i] == 0 for i in range(6))
    assert matrix == [list(column) for column in zip(*matrix)]
    assert tuple(map(sum, matrix)) == (3, 3, 8, 8, 5, 5)
    for i in range(6):
        for j in range(i + 1, 6):
            assert matrix[i][j] == len(data.class_edges.get((i, j), ()))
    reached = {0}
    for _ in range(6):
        reached |= {neighbor for vertex in reached for neighbor in range(6) if matrix[vertex][neighbor]}
    assert reached == set(range(6))


def test_exact_boundary_complete_histogram_has_independent_set_cycle_replay():
    a_pairing, b_pairing, _, stars = literal_darts()
    choices = [tuple((min(stars[vertex]),) + tail for tail in permutations(stars[vertex][1:]))
               for vertex in (0, 2, 4)]
    histogram = Counter()
    for positive_orders in product(*choices):
        successor = {}
        for positive in positive_orders:
            negative = tuple(b_pairing[dart] for dart in positive[::-1])
            for order in (positive, negative):
                successor.update(zip(order, order[1:] + order[:1]))
        seen, face_count = set(), 0
        for start in range(32):
            if start in seen:
                continue
            face_count += 1
            cursor = start
            while cursor not in seen:
                seen.add(cursor)
                cursor = successor[a_pairing[cursor]]
            assert cursor == start
        histogram[face_count] += 1
    expected = {2: 115836, 4: 109814, 6: 15840, 8: 424, 10: 6}
    assert dict(histogram) == expected
    assert sum(histogram.values()) == 241920
    decision = decide_boundary_exact_rotations()
    assert decision.face_histogram == expected
    assert decision.scheme_budget == decision.schemes_considered == 241920
    assert decision.spherical_face_count == 12
    assert decision.maximum_euler_characteristic == 0
    assert decision.exhaustive is True
    assert decision.ac_invariant_claimed is False


def test_exact_boundary_rotation_verifier_rejects_corrupted_negative_order():
    data = exact_link_data()
    _, b_pairing, _, stars = literal_darts()
    rotations = []
    for vertex in (0, 2, 4):
        positive = stars[vertex]
        rotations.extend((positive, tuple(b_pairing[dart] for dart in positive[::-1])))
    verify_rotations(data, tuple(rotations))
    negative = rotations[1]
    rotations[1] = (negative[1], negative[0]) + negative[2:]
    try:
        verify_rotations(data, tuple(rotations))
    except AssertionError as error:
        assert "B-reversed" in str(error)
    else:
        raise AssertionError("the corrupted negative order was accepted")


def test_connected_triangular_basis_is_a_spherical_positive_control():
    words = ("xzt", "zt", "t")
    a_pairing, b_pairing, germs, stars = literal_darts(words)
    data = _build_link_data(words)
    assert data.A == a_pairing and data.B == b_pairing and data.germ == germs
    assert tuple(map(len, stars)) == (1, 1, 2, 2, 3, 3)
    reached = {0}
    for _ in range(6):
        reached |= {germs[a_pairing[dart]] for dart in range(12) if germs[dart] in reached}
    assert reached == set(range(6))
    histogram = Counter()
    for positives in (((0,), (2, 6), (4, 8, 10)), ((0,), (2, 6), (4, 10, 8))):
        rotations = []
        successor = {}
        for positive in positives:
            negative = tuple(b_pairing[dart] for dart in positive[::-1])
            rotations.extend((positive, negative))
            for order in (positive, negative):
                successor.update(zip(order, order[1:] + order[:1]))
        verify_rotations(data, tuple(rotations))
        seen, faces = set(), 0
        for start in range(12):
            if start in seen:
                continue
            faces += 1
            cursor = start
            while cursor not in seen:
                seen.add(cursor)
                cursor = successor[a_pairing[cursor]]
            assert cursor == start
        assert 6 - 6 + faces == 2
        histogram[faces] += 1
    assert histogram == {2: 2}
    assert enumerate_face_histogram(data) == ({2: 2}, 2)
