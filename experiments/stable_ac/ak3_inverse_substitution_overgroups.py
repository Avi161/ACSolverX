"""Bounded folded-overgroup enumeration; positives remain uncertified candidates."""

from collections import deque
from functools import lru_cache
from itertools import combinations
import json

from experiments.stable_ac.depth4_period_two_binomial_forest_certificate import (
    UnionFind, fold, inverse, reduce_word,
)
from experiments.stable_ac.mms02_terminal_hnn_certificate import whitehead_minimum

AK3 = ((1, 1, 1, -2, -2, -2, -2), (1, 2, 1, -2, -1, -2))


def canonicalize(edges, root=0):
    transitions = {}
    for source, label, target in edges:
        assert (source, label) not in transitions or transitions[source, label] == target
        transitions[source, label] = target
    names, queue = {root: 0}, deque([root])
    while queue:
        source = queue.popleft()
        for label in (-2, -1, 1, 2):
            if (source, label) in transitions:
                target = transitions[source, label]
                if target not in names:
                    names[target] = len(names)
                    queue.append(target)
    assert {vertex for s, _, t in edges for vertex in (s, t)} <= names.keys()
    return tuple(sorted((names[s], label, names[t]) for s, label, t in edges))


def merge_vertices(graph, pair):
    count = 1 + max((vertex for s, _, t in graph for vertex in (s, t)), default=0)
    unions = UnionFind(count)
    unions.union(*pair)
    while True:
        changed, transitions = False, {}
        for source, label, target in sorted(graph):
            key, target = (unions.find(source), label), unions.find(target)
            if key in transitions:
                changed |= unions.union(transitions[key], target)
            else:
                transitions[key] = target
        if not changed:
            break
    return canonicalize({(unions.find(s), label, unions.find(t)) for s, label, t in graph}, unions.find(0))


def initial_graph(words):
    root, edges = fold(tuple(map(reduce_word, words)))
    return canonicalize(edges, root)


def graph_rank(graph):
    vertices = {0} | {vertex for s, _, t in graph for vertex in (s, t)}
    return len(graph) // 2 - len(vertices) + 1


def determinant(words):
    vectors = [tuple(word.count(g) - word.count(-g) for g in (1, 2)) for word in words]
    return vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]


@lru_cache(maxsize=None)
def word_analysis(word):
    literal = "".join({1: "x", -1: "X", 2: "y", -2: "Y"}[letter] for letter in word)
    minimum, steps = whitehead_minimum((literal,))
    return {"minimum": minimum[0], "minimum_total": len(minimum[0]),
            "steps": steps, "primitive": len(minimum[0]) == 1}


def analyze_graph(graph, words):
    rank = graph_rank(graph)
    result = {"rank": rank, "full_group": graph == ((0, -2, 0), (0, -1, 0), (0, 1, 0), (0, 2, 0)),
              "candidate": False}
    if rank != 2:
        return result
    paths, queue, tree = {0: ()}, deque([0]), set()
    transitions = {(s, label): t for s, label, t in graph}
    while queue:
        source = queue.popleft()
        for label in (-2, -1, 1, 2):
            if (source, label) not in transitions:
                continue
            target = transitions[source, label]
            if target not in paths:
                paths[target] = paths[source] + (label,)
                tree.add(min((source, label, target), (target, -label, source)))
                queue.append(target)
    undirected = {min((s, label, t), (t, -label, s)) for s, label, t in graph}
    chords = sorted(undirected - tree)
    assert len(chords) == 2
    basis = tuple(reduce_word(paths[s] + (label,) + inverse(paths[t])) for s, label, t in chords)
    chord_letters = {}
    for generator, (source, label, target) in enumerate(chords, 1):
        chord_letters[source, label, target] = generator
        chord_letters[target, -label, source] = -generator
    preimages = []
    for word in words:
        source, output = 0, []
        for label in word:
            target = transitions[source, label]
            if (source, label, target) in chord_letters:
                output.append(chord_letters[source, label, target])
            source = target
        assert source == 0
        preimage = reduce_word(tuple(output))
        expanded = tuple(part for letter in preimage for part in
                         (basis[letter - 1] if letter > 0 else inverse(basis[-letter - 1])))
        assert reduce_word(expanded) == reduce_word(word)
        preimages.append(preimage)
    ambient_checks = tuple(word_analysis(word) for word in basis)
    preimage_checks = tuple(word_analysis(word) for word in preimages)
    result.update({"tree": sorted(tree), "chords": chords, "basis": basis, "preimages": preimages,
                   "basis_abelian_determinant": determinant(basis), "ambient_checks": ambient_checks,
                   "preimage_checks": preimage_checks,
                   "candidate": abs(determinant(words)) == 1 and any(item["primitive"] for item in ambient_checks)
                   and any(item["primitive"] for item in preimage_checks)})
    return result


def enumerate_overgroups(words=AK3, max_states=5000):
    if max_states < 1:
        raise ValueError("at least one state is required")
    words = tuple(map(reduce_word, words))
    graph = initial_graph(words)
    records = [{"graph": graph, "parent": None, "merged_pair": None, **analyze_graph(graph, words)}]
    known, cursor, complete = {graph: 0}, 0, True
    while cursor < len(records) and complete:
        graph = records[cursor]["graph"]
        vertices = sorted({0} | {vertex for s, _, t in graph for vertex in (s, t)})
        for pair in combinations(vertices, 2):
            child = merge_vertices(graph, pair)
            if child in known:
                continue
            if len(records) == max_states:
                complete = False
                break
            known[child] = len(records)
            records.append({"graph": child, "parent": cursor, "merged_pair": pair, **analyze_graph(child, words)})
        cursor += 1
    candidates = [index for index, record in enumerate(records) if record["candidate"]]
    return {"words": words, "input_abelian_determinant": determinant(words), "max_states": max_states,
            "complete": complete, "records": records, "candidates": candidates,
            "counts": {"states": len(records), "rank_two": sum(record["rank"] == 2 for record in records),
                       "candidates": len(candidates)}, "status": "candidates_pending_independent_root_certificate"}


def data():
    return enumerate_overgroups()


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
