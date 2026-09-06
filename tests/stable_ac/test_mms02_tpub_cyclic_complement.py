from itertools import combinations
import ast
import json
from pathlib import Path

from experiments.stable_ac.depth4_period_two_binomial_forest_certificate import (
    UnionFind, fold as reference_fold,
)

WORDS = ("xzYXyxZXYxyZ", "XyxZXYXyxzXYxy", "Xyz")
LABELS = (-3, -2, -1, 1, 2, 3)
FULL_ROSE = tuple((0, label, 0) for label in LABELS)


def integer_word(word):
    return tuple((1 if letter.islower() else -1) * ("xyz".index(letter.lower()) + 1) for letter in word)


def normalize(edges, root=0):
    names, queue = {root: 0}, [root]
    for source in queue:
        for label in LABELS:
            targets = {target for origin, edge_label, target in edges if (origin, edge_label) == (source, label)}
            assert len(targets) <= 1
            for target in targets:
                if target not in names:
                    names[target] = len(names)
                    queue.append(target)
    assert {vertex for s, _, t in edges for vertex in (s, t)} <= names.keys()
    return tuple(sorted((names[s], label, names[t]) for s, label, t in edges))


def set_fold(edges, pair=(0, 0)):
    vertices = {0} | {vertex for s, _, t in edges for vertex in (s, t)}
    classes = [{vertex} for vertex in sorted(vertices)]

    def identify(left, right):
        first = next(group for group in classes if left in group)
        second = next(group for group in classes if right in group)
        if first != second:
            classes.remove(first)
            classes.remove(second)
            classes.append(first | second)

    identify(*pair)
    while True:
        representatives = {vertex: min(group) for group in classes for vertex in group}
        quotient = {(representatives[s], label, representatives[t]) for s, label, t in edges}
        conflict = next(((t, other_t) for s, label, t in sorted(quotient)
                         for other_s, other_label, other_t in sorted(quotient)
                         if (s, label) == (other_s, other_label) and t != other_t), None)
        if conflict is None:
            return normalize(quotient, representatives[0])
        identify(*conflict)


def wedge(words):
    edges, fresh = [], 1
    for word in words:
        current = 0
        for index, letter in enumerate(word):
            target = 0 if index == len(word) - 1 else fresh
            if target:
                fresh += 1
            edges.extend(((current, letter, target), (target, -letter, current)))
            current = target
    return edges


def determinant_three(words):
    rows = [tuple(word.count(g) - word.count(-g) for g in (1, 2, 3)) for word in words]
    a, b, c = rows
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def data(words=WORDS):
    words = tuple(words)
    integer_words = tuple(map(integer_word, words))
    initial = set_fold(wedge(integer_words))
    vertices = sorted({0} | {vertex for s, _, t in initial for vertex in (s, t)})
    pairs = [{"pair": pair, "graph": set_fold(initial, pair)} for pair in combinations(vertices, 2)]
    hits = [record["pair"] for record in pairs if record["graph"] == FULL_ROSE]
    return {"words": words, "initial_graph": initial, "vertices": len(vertices),
            "undirected_edges": len(initial) // 2, "rank": len(initial) // 2 - len(vertices) + 1,
            "abelian_determinant": determinant_three(integer_words), "pairs": pairs,
            "full_rose_hits": hits, "initial_full_rose": initial == FULL_ROSE,
            "status": "one_step_vertex_pair_folds_only"}


def verify_result(result):
    words = tuple(map(integer_word, result["words"]))
    root, reference = reference_fold(words)
    initial = tuple(tuple(edge) for edge in result["initial_graph"])
    assert initial == normalize(reference, root)
    vertices = sorted({0} | {vertex for s, _, t in initial for vertex in (s, t)})
    assert result["vertices"] == len(vertices)
    assert result["undirected_edges"] == len(initial) // 2
    assert result["rank"] == len(initial) // 2 - len(vertices) + 1
    assert result["abelian_determinant"] == determinant_three(words)
    assert [tuple(record["pair"]) for record in result["pairs"]] == list(combinations(vertices, 2))
    hits = []
    for record in result["pairs"]:
        unions = UnionFind(len(vertices))
        unions.union(*record["pair"])
        while True:
            changed, transitions = False, {}
            for source, label, target in initial:
                key, target = (unions.find(source), label), unions.find(target)
                if key in transitions:
                    changed |= unions.union(transitions[key], target)
                else:
                    transitions[key] = target
            if not changed:
                break
        expected = normalize({(unions.find(s), label, unions.find(t)) for s, label, t in initial}, unions.find(0))
        graph = tuple(tuple(edge) for edge in record["graph"])
        assert graph == expected
        if graph == FULL_ROSE:
            hits.append(tuple(record["pair"]))
    for graph in [initial] + [tuple(tuple(edge) for edge in record["graph"]) for record in result["pairs"]]:
        assert set(graph) == {(t, -label, s) for s, label, t in graph}
        assert len({(s, label) for s, label, _ in graph}) == len(graph)
        assert normalize(set(graph)) == graph
        transitions = {(s, label): t for s, label, t in graph}
        for word in words:
            vertex = 0
            for letter in word:
                vertex = transitions[vertex, letter]
            assert vertex == 0
    assert [tuple(pair) for pair in result["full_rose_hits"]] == hits
    assert result["initial_full_rose"] == (initial == FULL_ROSE)


def test_small_cyclic_complement_controls():
    square_control = data(("x", "y", "zz"))
    verify_result(square_control)
    assert square_control["abelian_determinant"] == 2
    assert not square_control["initial_full_rose"] and square_control["full_rose_hits"]
    full = data(("x", "y", "z"))
    verify_result(full)
    assert full["initial_full_rose"] and full["abelian_determinant"] == 1


def test_saved_tpub_cyclic_complement_certificate():
    root = Path(__file__).resolve().parents[2]
    source = ast.parse((root / "experiments/stable_ac/thickenable/mms02_tpub_neuwirth_certificate.py").read_text())
    pinned = next(node.value for node in source.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "ORIGINAL_WORDS" for target in node.targets))
    assert tuple(ast.literal_eval(pinned)) == WORDS
    result = json.loads((root / "results/stable_ac/theory/mms02_tpub_cyclic_complement_20260906.json").read_text())
    assert tuple(result["words"]) == WORDS
    assert (result["vertices"], result["undirected_edges"], result["rank"], result["abelian_determinant"]) == (25, 27, 3, 1)
    assert len(result["pairs"]) == 300
    assert not result["initial_full_rose"] and result["full_rose_hits"] == []
    verify_result(result)


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
