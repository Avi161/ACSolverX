"""One recorded spanning-tree presentation and defining-generator pass."""

import json
from pathlib import Path

from experiments.stable_ac.ak3_prism_collapse import face_closure

LETTER_LIMIT = 10000


def freely_reduce(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def inverse(word):
    return tuple(-letter for letter in reversed(word))


def extract_presentation(complex_faces):
    faces = set(complex_faces)
    if not faces or face_closure(faces) != faces or any(len(face) > 3 for face in faces):
        raise AssertionError("presentation extraction requires a nonempty closed two-complex")
    vertices = sorted(face[0] for face in faces if len(face) == 1)
    edges = sorted(face for face in faces if len(face) == 2)
    triangles = sorted(face for face in faces if len(face) == 3)
    parent = {vertex: vertex for vertex in vertices}

    def find(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    tree = []
    for edge in edges:
        left, right = map(find, edge)
        if left != right:
            parent[right] = left
            tree.append(edge)
    if len(tree) != len(vertices) - 1 or len({find(vertex) for vertex in vertices}) != 1:
        raise AssertionError("the one-skeleton must be connected")
    tree_set = set(tree)
    generator_edges = {index: edge for index, edge in enumerate((edge for edge in edges if edge not in tree_set), 1)}
    edge_generators = {edge: generator for generator, edge in generator_edges.items()}
    rows = {}
    for row_id, (a, b, c) in enumerate(triangles):
        word = []
        for edge, sign in (((a, b), 1), ((b, c), 1), ((a, c), -1)):
            if edge in edge_generators:
                word.append(sign * edge_generators[edge])
        rows[row_id] = freely_reduce(word)
    return {"vertices": vertices, "triangles": triangles, "tree": tree,
            "generator_edges": generator_edges, "initial_rows": rows}


def eliminate_defining_generators(rows, generators, letter_limit=LETTER_LIMIT):
    if letter_limit < 0:
        raise ValueError("the letter limit must be nonnegative")
    if sum(len(word) for word in rows.values()) > letter_limit:
        raise AssertionError("initial rows exceed the total-letter guard")
    current = {row_id: freely_reduce(word) for row_id, word in rows.items()}
    live = set(generators)
    if any(generator <= 0 for generator in live) or any(abs(letter) not in live for word in current.values() for letter in word):
        raise AssertionError("rows contain an unknown generator")
    step_bound = len(live)
    steps = []
    while True:
        pivot = None
        for row_id in sorted(current):
            word = current[row_id]
            for generator in sorted({abs(letter) for letter in word}):
                if sum(abs(letter) == generator for letter in word) == 1:
                    pivot = row_id, generator
                    break
            if pivot is not None:
                break
        if pivot is None:
            break
        row_id, generator = pivot
        word = current[row_id]
        index = next(index for index, letter in enumerate(word) if abs(letter) == generator)
        sign = 1 if word[index] > 0 else -1
        prefix, suffix = word[:index], word[index + 1:]
        rotated_remainder = freely_reduce(suffix + prefix)
        replacement = inverse(rotated_remainder) if sign == 1 else rotated_remainder
        replacement_inverse = inverse(replacement)
        remaining = {key: value for key, value in current.items() if key != row_id}
        prospective_letters = sum(len(replacement) if abs(letter) == generator else 1
                                  for value in remaining.values() for letter in value)
        if prospective_letters > letter_limit:
            raise AssertionError("prospective substitutions exceed the total-letter guard")

        def substitute(value):
            return freely_reduce(part for letter in value
                                 for part in (replacement if letter == generator else
                                              replacement_inverse if letter == -generator else (letter,)))

        if substitute(word):
            raise AssertionError("the defining row did not vanish")
        after = {key: substitute(value) for key, value in remaining.items()}
        if any(abs(letter) == generator for value in after.values() for letter in value):
            raise AssertionError("the eliminated generator survived")
        steps.append({"row_id": row_id, "generator": generator, "sign": sign,
                      "prefix": prefix, "suffix": suffix, "before_pivot": word,
                      "replacement": replacement, "after_rows": after})
        current = after
        live.remove(generator)
        if len(steps) > step_bound:
            raise AssertionError("elimination exceeded the initial generator bound")
    return {"steps": steps, "terminal_rows": current, "live_generators": sorted(live),
            "letter_limit": letter_limit, "guard_scope": "total prospective letters before free reduction"}


def data():
    source = "results/stable_ac/theory/ak3_prism_edge_contraction_20260906.json"
    artifact = json.loads((Path(__file__).resolve().parents[2] / source).read_text(encoding="utf-8"))
    faces = face_closure(artifact["reduction"]["remaining_maximal_simplices"])
    if tuple(sum(len(face) == size for face in faces) for size in (1, 2, 3)) != (19, 78, 60):
        raise AssertionError("the saved endpoint counts drifted")
    presentation = extract_presentation(faces)
    if len(presentation["tree"]) != 18 or len(presentation["generator_edges"]) != 60:
        raise AssertionError("the endpoint spanning-tree counts drifted")
    elimination = eliminate_defining_generators(presentation["initial_rows"], presentation["generator_edges"])
    return {"source_artifact": source, "presentation": presentation, "elimination": elimination,
            "status": "one_defining_generator_elimination_pass"}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
