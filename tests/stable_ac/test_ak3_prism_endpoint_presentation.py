import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_endpoint_presentation import (
    eliminate_defining_generators, extract_presentation,
)


def closure(simplices):
    faces = set()
    for simplex in simplices:
        vertices = sorted(simplex)
        for mask in range(1, 1 << len(vertices)):
            faces.add(tuple(vertex for index, vertex in enumerate(vertices) if mask & (1 << index)))
    return faces


def reduced(word):
    result = []
    for letter in word:
        if result and letter == -result[-1]:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def inverted(word):
    return tuple(-letter for letter in word[::-1])


def replay(rows, generators, result):
    current = {key: reduced(word) for key, word in rows.items()}
    live = set(generators)
    for step in result["steps"]:
        row_id, generator = step["row_id"], step["generator"]
        choices = [(key, value) for key in sorted(current)
                   for value in sorted(live) if sum(abs(letter) == value for letter in current[key]) == 1]
        assert (row_id, generator) == choices[0]
        word = current[row_id]
        assert word == tuple(step["before_pivot"])
        index = next(index for index, letter in enumerate(word) if abs(letter) == generator)
        assert tuple(step["prefix"]) == word[:index] and tuple(step["suffix"]) == word[index + 1:]
        sign = 1 if word[index] > 0 else -1
        assert step["sign"] == sign
        remainder = word[index + 1:] + word[:index]
        replacement = reduced(inverted(remainder) if sign == 1 else remainder)
        assert replacement == tuple(step["replacement"])
        after = {}
        for key, value in current.items():
            expanded = []
            for letter in value:
                expanded.extend(replacement if letter == generator else inverted(replacement) if letter == -generator else (letter,))
            if key == row_id:
                assert reduced(expanded) == ()
            else:
                after[key] = reduced(expanded)
        assert after == {key: tuple(value) for key, value in step["after_rows"].items()}
        assert all(abs(letter) != generator for value in after.values() for letter in value)
        current = after
        live.remove(generator)
    assert current == result["terminal_rows"] and sorted(live) == result["live_generators"]
    assert all(sum(abs(letter) == generator for letter in word) != 1 for word in current.values() for generator in live)
    return current, live


def test_disk_circle_and_sphere_presentation_controls():
    cases = ((closure(((0, 1, 2),)), 0, 0),
             (closure(((0, 1), (1, 2), (0, 2))), 1, 0),
             (closure(((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))), 0, 1))
    for faces, expected_generators, expected_empty_rows in cases:
        presentation = extract_presentation(faces)
        tree = presentation["tree"]
        assert len(tree) == sum(len(face) == 1 for face in faces) - 1
        components = [{face[0]} for face in faces if len(face) == 1]
        expected_tree = []
        for left, right in sorted(face for face in faces if len(face) == 2):
            first = next(component for component in components if left in component)
            second = next(component for component in components if right in component)
            if first != second:
                components.remove(first)
                components.remove(second)
                components.append(first | second)
                expected_tree.append((left, right))
        assert len(components) == 1 and tree == expected_tree
        cotree = sorted(face for face in faces if len(face) == 2 and face not in tree)
        assert presentation["generator_edges"] == dict(enumerate(cotree, 1))
        expected_rows = {}
        for index, (a, b, c) in enumerate(sorted(face for face in faces if len(face) == 3)):
            boundary = ((a, b), (b, c), (a, c))
            expected_rows[index] = tuple((1 if position < 2 else -1) * (cotree.index(edge) + 1)
                                         for position, edge in enumerate(boundary) if edge in cotree)
        assert presentation["initial_rows"] == expected_rows
        result = eliminate_defining_generators(expected_rows, presentation["generator_edges"])
        rows, live = replay(expected_rows, presentation["generator_edges"], result)
        assert len(live) == expected_generators
        assert len(rows) == expected_empty_rows and all(word == () for word in rows.values())


def test_pivot_signs_empty_rows_and_literal_defining_controls():
    for sign, replacement in ((1, (-2, -3)), (-1, (3, 2))):
        rows = {0: (2, sign, 3), 1: (2, 2), 2: (3, 3), 3: ()}
        result = eliminate_defining_generators(rows, (1, 2, 3))
        assert result["steps"][0]["generator"] == 1
        assert result["steps"][0]["replacement"] == replacement
        terminal, live = replay(rows, (1, 2, 3), result)
        assert terminal[3] == () and live == {2, 3}
    rows = {0: (-1, 2), 1: (2,)}
    result = eliminate_defining_generators(rows, (1, 2))
    assert replay(rows, (1, 2), result) == ({}, set())


def test_prospective_substitution_guard_can_fail_before_expansion():
    rows = {0: (1, 2, 2, 2), 1: (1, 1, 1, 1)}
    try:
        eliminate_defining_generators(rows, (1, 2), letter_limit=8)
    except AssertionError as error:
        assert "prospective substitutions" in str(error)
    else:
        raise AssertionError("a prospective total above the letter limit was accepted")


def test_literal_defining_donor_lifts_for_both_occurrence_signs():
    cases = (((), (), ()),
             ((2, -3, 2), (-2, 3), (-2, 1)),
             ((2, 3, -3, -2), (1, -1, 2), (-2, 3)),
             ((-3, 2, -3), (3, -2, 1), (-1, 3, -2)))
    for word, prefix, suffix in cases:
        assert all(abs(letter) != 1 for letter in word)
        donor = (1,) + word
        positive_recipient = prefix + (1,) + suffix
        conjugated_donor = prefix + donor + inverted(prefix)
        assert reduced(inverted(conjugated_donor) + positive_recipient) == reduced(prefix + inverted(word) + suffix)
        negative_recipient = prefix + (-1,) + suffix
        conjugator = prefix + word
        conjugated_donor = conjugator + donor + inverted(conjugator)
        assert reduced(conjugated_donor + negative_recipient) == reduced(prefix + word + suffix)


def test_saved_endpoint_presentation_has_independent_tree_and_58_pivot_replay():
    directory = Path(__file__).resolve().parents[2] / "results/stable_ac/theory"
    complex_artifact = json.loads((directory / "ak3_prism_edge_contraction_20260906.json").read_text(encoding="utf-8"))
    artifact = json.loads((directory / "ak3_prism_endpoint_presentation_20260906.json").read_text(encoding="utf-8"))
    faces = closure(complex_artifact["reduction"]["remaining_maximal_simplices"])
    vertices = sorted(face[0] for face in faces if len(face) == 1)
    edges = sorted(face for face in faces if len(face) == 2)
    triangles = sorted(face for face in faces if len(face) == 3)
    assert (len(vertices), len(edges), len(triangles)) == (19, 78, 60)
    components = [{vertex} for vertex in vertices]
    tree = []
    for left, right in edges:
        first = next(component for component in components if left in component)
        second = next(component for component in components if right in component)
        if first != second:
            components.remove(first)
            components.remove(second)
            components.append(first | second)
            tree.append((left, right))
    assert len(components) == 1 and len(tree) == 18
    cotree = [edge for edge in edges if edge not in tree]
    generator_edges = dict(enumerate(cotree, 1))
    rows = {}
    for index, (a, b, c) in enumerate(triangles):
        boundary = ((a, b), (b, c), (a, c))
        rows[index] = reduced((1 if position < 2 else -1) * (cotree.index(edge) + 1)
                              for position, edge in enumerate(boundary) if edge in cotree)
    recorded = artifact["presentation"]
    assert vertices == recorded["vertices"]
    assert triangles == [tuple(face) for face in recorded["triangles"]]
    assert tree == [tuple(edge) for edge in recorded["tree"]]
    assert generator_edges == {int(key): tuple(value) for key, value in recorded["generator_edges"].items()}
    assert rows == {int(key): tuple(value) for key, value in recorded["initial_rows"].items()}
    elimination = artifact["elimination"]
    normalized = dict(elimination)
    normalized["steps"] = [dict(step, after_rows={int(key): tuple(value) for key, value in step["after_rows"].items()})
                           for step in elimination["steps"]]
    normalized["terminal_rows"] = {int(key): tuple(value) for key, value in elimination["terminal_rows"].items()}
    assert len(normalized["steps"]) == 58
    assert normalized["letter_limit"] == 10000
    terminal, live = replay(rows, generator_edges, normalized)
    assert live == {53, 58} and normalized["live_generators"] == [53, 58]
    assert terminal == {
        57: (53, 53, -58, 53, 53, -58, 53, 53, -58, 53, 53, 53, 53),
        59: (58, 53, -58, 53, -58, 53),
    }
    assert len(terminal) == len(rows) - len(normalized["steps"]) == 2


def test_endpoint_two_generator_basis_change_returns_literally_to_ak3():
    def substitute(word, images):
        return reduced(letter for generator in word
                       for letter in (images[generator] if generator > 0 else inverted(images[-generator])))

    new_to_old = {1: (53, 53, -58), 2: (-53,)}
    old_to_new = {53: (-2,), 58: (-1, -2, -2)}
    for generator in (1, 2):
        assert substitute(new_to_old[generator], old_to_new) == (generator,)
    for generator in (53, 58):
        assert substitute(old_to_new[generator], new_to_old) == (generator,)
    first = (53, 53, -58) * 3 + (53,) * 4
    second = (58, 53, -58, 53, -58, 53)
    first_image = substitute(first, old_to_new)
    second_image = substitute(second, old_to_new)
    assert first_image == (1, 1, 1, -2, -2, -2, -2)
    assert second_image == (-1, -2, 1, 2, 1, -2)
    conjugator = (2, 1)
    returned_second = reduced(conjugator + second_image + inverted(conjugator))
    assert (first_image, returned_second) == ((1, 1, 1, -2, -2, -2, -2), (1, 2, 1, -2, -1, -2))
