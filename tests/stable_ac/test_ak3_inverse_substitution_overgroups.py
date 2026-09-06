from itertools import combinations
import json
from pathlib import Path

from experiments.stable_ac.ak3_inverse_substitution_overgroups import (
    AK3, analyze_graph, initial_graph,
)
from experiments.stable_ac.mms02_terminal_hnn_certificate import (
    apply_images, canonical_cyclic_word, rank_two_whitehead_automorphisms,
)


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def substitute(word, basis):
    return reduced(part for letter in word for part in
                   (basis[letter - 1] if letter > 0 else tuple(-part for part in reversed(basis[-letter - 1]))))


def independent_merge(graph, pair):
    vertices = {0} | {vertex for s, _, t in graph for vertex in (s, t)}
    classes = [{vertex} for vertex in sorted(vertices)]
    def identify(left, right):
        first = next(group for group in classes if left in group)
        second = next(group for group in classes if right in group)
        if first == second:
            return False
        classes.remove(first)
        classes.remove(second)
        classes.append(first | second)
        return True
    identify(*pair)
    while True:
        representative = {vertex: min(group) for group in classes for vertex in group}
        edges = {(representative[s], label, representative[t]) for s, label, t in graph}
        conflict = next(((t, other_t) for s, label, t in sorted(edges)
                         for other_s, other_label, other_t in sorted(edges)
                         if (s, label) == (other_s, other_label) and t != other_t), None)
        if conflict is None:
            break
        identify(*conflict)
    names = {representative[0]: 0}
    queue = [representative[0]]
    for source in queue:
        for _, label, target in sorted(edge for edge in edges if edge[0] == source):
            if target not in names:
                names[target] = len(names)
                queue.append(target)
    return tuple(sorted((names[s], label, names[t]) for s, label, t in edges))


def verify_full_record(data):
    """Explicit post-run replay entry point; never launches the enumeration."""
    records = data["records"]
    graphs = [tuple(tuple(edge) for edge in record["graph"]) for record in records]
    assert len(set(graphs)) == len(graphs) == data["counts"]["states"]
    words = tuple(tuple(word) for word in data["words"])
    wedge, fresh = [], 1
    for word in words:
        source = 0
        for position, letter in enumerate(word):
            target = 0 if position == len(word) - 1 else fresh
            if target:
                fresh += 1
            wedge.extend(((source, letter, target), (target, -letter, source)))
            source = target
    assert graphs[0] == independent_merge(wedge, (0, 0))
    vectors = [tuple(word.count(g) - word.count(-g) for g in (1, 2)) for word in words]
    determinant = vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]
    assert data["input_abelian_determinant"] == determinant
    assert len(graphs) <= data["max_states"]
    for index, (record, graph) in enumerate(zip(records, graphs)):
        vertices = {0} | {vertex for s, _, t in graph for vertex in (s, t)}
        assert set(graph) == {(t, -label, s) for s, label, t in graph}
        assert len({(s, label) for s, label, _ in graph}) == len(graph)
        assert record["rank"] == len(graph) // 2 - len(vertices) + 1
        if index:
            assert 0 <= record["parent"] < index
            assert independent_merge(graphs[record["parent"]], record["merged_pair"]) == graph
        else:
            assert record["parent"] is None and record["merged_pair"] is None
        transitions = {(s, label): t for s, label, t in graph}
        for word in words:
            vertex = 0
            for letter in word:
                vertex = transitions[vertex, letter]
            assert vertex == 0
        if record["rank"] == 2:
            basis = tuple(tuple(word) for word in record["basis"])
            tree = {tuple(edge) for edge in record["tree"]}
            assert len(tree) == len(vertices) - 1
            tree_edges = tree | {(t, -label, s) for s, label, t in tree}
            assert tree_edges <= set(graph)
            paths, queue = {0: ()}, [0]
            for source in queue:
                for _, letter, target in sorted(edge for edge in tree_edges if edge[0] == source):
                    if target not in paths:
                        paths[target] = paths[source] + (letter,)
                        queue.append(target)
            assert set(paths) == vertices
            chords = sorted({min((s, label, t), (t, -label, s)) for s, label, t in graph} - tree)
            assert len(chords) == 2 and [tuple(edge) for edge in record["chords"]] == chords
            expected_basis = tuple(reduced(paths[s] + (letter,) + tuple(-v for v in reversed(paths[t])))
                                   for s, letter, t in chords)
            assert basis == expected_basis
            assert tuple(substitute(word, basis) for word in record["preimages"]) == words
            for word, check in zip(basis + tuple(map(tuple, record["preimages"])),
                                   record["ambient_checks"] + record["preimage_checks"]):
                literal = "".join({1: "x", -1: "X", 2: "y", -2: "Y"}[letter] for letter in word)
                current = canonical_cyclic_word(literal)
                automorphisms = rank_two_whitehead_automorphisms()
                for step in check["steps"]:
                    images = dict(zip(("x", "y"), step))
                    assert images in automorphisms
                    following = canonical_cyclic_word(apply_images(current, images))
                    assert len(following) < len(current)
                    current = following
                assert current == check["minimum"] and len(current) == check["minimum_total"]
                assert all(len(canonical_cyclic_word(apply_images(current, images))) >= len(current)
                           for images in automorphisms)
                assert check["primitive"] == (check["minimum_total"] == 1)
            assert record["candidate"] == (abs(determinant) == 1
                    and any(item["primitive"] for item in record["ambient_checks"])
                    and any(item["primitive"] for item in record["preimage_checks"]))
        else:
            assert not record["candidate"]
        if data["complete"]:
            assert all(independent_merge(graph, pair) in set(graphs) for pair in combinations(sorted(vertices), 2))
    assert data["candidates"] == [index for index, record in enumerate(records) if record["candidate"]]
    assert data["counts"]["rank_two"] == sum(record["rank"] == 2 for record in records)
    assert data["counts"]["candidates"] == len(data["candidates"])


def test_preflight_initial_ak3_core_and_positive_candidate_controls():
    graph = initial_graph(AK3)
    assert len({vertex for s, _, t in graph for vertex in (s, t)}) == 10 and len(graph) == 22
    for words, eligible in ((((1,), (2,)), True), (((1, 1), (2,)), False),
                            (((1,), (2, 1, 2, -1, -2, 1, 2, -1, -2)), True)):
        graph = initial_graph(words)
        result = analyze_graph(graph, words)
        assert result["rank"] == 2 and result["candidate"] == eligible
        assert tuple(substitute(word, result["basis"]) for word in result["preimages"]) == words
        if words == ((1, 1), (2,)):
            assert abs(result["basis_abelian_determinant"]) == 2
        if len(words[1]) > 1:
            assert not result["full_group"]


def test_saved_complete_overgroup_certificate():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_inverse_substitution_overgroups_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["complete"] and artifact["counts"] == {"states": 82, "rank_two": 2, "candidates": 0}
    assert [index for index, record in enumerate(artifact["records"]) if record["rank"] == 2] == [0, 21]
    verify_full_record(artifact)


def test_saved_initial_graph_sign_restricted_cycles():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_inverse_substitution_overgroups_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    graph = {tuple(edge) for edge in artifact["records"][0]["graph"]}
    assert tuple(map(tuple, artifact["words"])) == AK3
    assert len(graph) == 22

    def cyclic_edges(source_graph, signs):
        edges = {edge for edge in source_graph if edge[1] in signs}
        vertices = {vertex for s, _, t in source_graph for vertex in (s, t)}
        reachable = {(vertex, vertex) for vertex in vertices} | {(s, t) for s, _, t in edges}
        for middle in sorted(vertices):
            reachable.update((source, target) for source in vertices for target in vertices
                             if (source, middle) in reachable and (middle, target) in reachable)
        return {edge for edge in edges if (edge[2], edge[0]) in reachable}

    def topological_remainder(source_graph, signs):
        edges = {edge for edge in source_graph if edge[1] in signs}
        remaining = {vertex for s, _, t in source_graph for vertex in (s, t)}
        while remaining:
            sources = {vertex for vertex in remaining
                       if not any(target == vertex and source in remaining for source, _, target in edges)}
            if not sources:
                break
            remaining.difference_update(sources)
        return remaining

    cycle = {(0, 1, 1), (1, 1, 3), (3, 1, 7), (7, -2, 9),
             (9, -2, 6), (6, -2, 2), (2, -2, 0)}
    assert topological_remainder(graph, (1, 2)) == set()
    assert cyclic_edges(graph, (1, 2)) == set()
    assert cyclic_edges(graph, (1, -2)) == cycle
    assert cyclic_edges(graph, (-1, -2)) == set()
    assert topological_remainder(graph, (-1, -2)) == set()
    assert cyclic_edges(graph, (-1, 2)) == {(target, -label, source) for source, label, target in cycle}
    wedge = {(0, label, 0) for label in (-2, -1, 1, 2)}
    assert cyclic_edges(wedge, (1, 2)) == {(0, 1, 0), (0, 2, 0)}
    assert topological_remainder(wedge, (1, 2)) == {0}


def test_saved_initial_graph_needs_two_pair_merges_to_reach_full_rose():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_inverse_substitution_overgroups_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    records = artifact["records"]
    initial = tuple(tuple(edge) for edge in records[0]["graph"])
    full_rose = ((0, -2, 0), (0, -1, 0), (0, 1, 0), (0, 2, 0))
    vertices = sorted({vertex for source, _, target in initial for vertex in (source, target)})
    pairs = tuple(combinations(vertices, 2))
    assert len(vertices) == 10 and len(pairs) == 45
    assert all(independent_merge(initial, pair) != full_rose for pair in pairs)
    first = records[1]
    final = records[21]
    first_graph = tuple(tuple(edge) for edge in first["graph"])
    assert first["parent"] == 0
    assert independent_merge(initial, first["merged_pair"]) == first_graph
    assert final["parent"] == 1 and final["full_group"]
    assert tuple(tuple(edge) for edge in final["graph"]) == full_rose
    assert independent_merge(first_graph, final["merged_pair"]) == full_rose
    control = initial_graph(((1,), (2, 2)))
    control_vertices = sorted({vertex for source, _, target in control for vertex in (source, target)})
    assert any(independent_merge(control, pair) == full_rose for pair in combinations(control_vertices, 2))


def ak2_cyclic_complement_control_data():
    words = ((1, 1, -2, -2, -2), (1, 2, 1, -2, -1, -2))
    graph = initial_graph(words)
    vertices = sorted({0} | {vertex for source, _, target in graph for vertex in (source, target)})
    pairs = tuple(combinations(vertices, 2))
    full_rose = ((0, -2, 0), (0, -1, 0), (0, 1, 0), (0, 2, 0))
    hits = [pair for pair in pairs if independent_merge(graph, pair) == full_rose]
    return {"words": words, "vertices": len(vertices), "edges": len(graph) // 2,
            "rank": len(graph) // 2 - len(vertices) + 1, "pair_count": len(pairs),
            "hits_full_rose": hits}


def test_ordinary_ac_trivial_ak2_has_no_cyclic_complement():
    import runpy

    result = ak2_cyclic_complement_control_data()
    assert (result["vertices"], result["edges"], result["rank"], result["pair_count"]) == (8, 9, 2, 28)
    assert result["hits_full_rose"] == []
    wedge, fresh = [], 1
    for word in result["words"]:
        source = 0
        for position, letter in enumerate(word):
            target = 0 if position == len(word) - 1 else fresh
            if target:
                fresh += 1
            wedge.extend(((source, letter, target), (target, -letter, source)))
            source = target
    assert initial_graph(result["words"]) == independent_merge(wedge, (0, 0))
    transcript = runpy.run_path(str(Path(__file__).with_name("test_ak2_primitive_donor_transcript.py")))
    transcript["test_five_left_donor_factors_have_the_prescribed_family_transcript"]()
    transcript["test_ak2_primitive_donor_basis_and_defining_deletion_are_literal"]()
    transcript["test_ak2_cleanup_is_an_ordinary_ac_transcript_in_original_generators"]()
