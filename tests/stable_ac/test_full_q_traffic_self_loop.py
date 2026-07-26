from __future__ import annotations

from collections.abc import Mapping


GENERATORS = "xtzq"
LETTERS = "xXtTzZqQ"
INVERSE_LETTER = {
    "x": "X",
    "X": "x",
    "t": "T",
    "T": "t",
    "z": "Z",
    "Z": "z",
    "q": "Q",
    "Q": "q",
}

R = "xxxTTTT"
P = "xt"
B = "Zxt"
D = "TzxZ"
U = R + B
W = "qxxxQTTTTZqxQtq"

WordMap = Mapping[str, str]
Graph = dict[str, set[str]]


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE_LETTER[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while (
        len(word) > 1
        and INVERSE_LETTER[word[0]] == word[-1]
    ):
        word = word[1:-1]
    return word


def inverse_word(word: str) -> str:
    return "".join(INVERSE_LETTER[letter] for letter in reversed(word))


def conjugate(conjugator: str, word: str) -> str:
    return free_reduce(conjugator + word + inverse_word(conjugator))


def substitute(word: str, images: WordMap) -> str:
    result = ""
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse_word(image)
        result = free_reduce(result + image)
    return result


def compose(outer: WordMap, inner: WordMap) -> dict[str, str]:
    return {
        generator: substitute(inner[generator], outer)
        for generator in GENERATORS
    }


def target(delta: int, epsilon: int) -> str:
    conjugator = "z" if delta == 1 else "Z"
    q_letter = "q" if epsilon == 1 else "Q"
    return free_reduce(
        W
        + conjugator
        + q_letter
        + inverse_word(conjugator)
    )


def whitehead_graph(word: str) -> Graph:
    graph = {letter: set() for letter in LETTERS}
    for left, right in zip(word, word[1:] + word[:1]):
        first = INVERSE_LETTER[left]
        graph[first].add(right)
        graph[right].add(first)
    return graph


def edge_set(graph: Graph) -> set[frozenset[str]]:
    return {
        frozenset((left, right))
        for left, neighbors in graph.items()
        for right in neighbors
    }


def graph_is_connected(
    graph: Graph,
    omitted: str | None = None,
) -> bool:
    vertices = [vertex for vertex in graph if vertex != omitted]
    seen = {vertices[0]}
    frontier = [vertices[0]]
    while frontier:
        vertex = frontier.pop()
        for neighbor in graph[vertex]:
            if neighbor != omitted and neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    return len(seen) == len(vertices)


def cut_vertices(graph: Graph) -> set[str]:
    assert graph_is_connected(graph)
    return {
        vertex
        for vertex in graph
        if not graph_is_connected(graph, omitted=vertex)
    }


def assert_spanning_cycle(graph: Graph, cycle: tuple[str, ...]) -> None:
    assert cycle[0] == cycle[-1]
    assert set(cycle[:-1]) == set(LETTERS)
    for left, right in zip(cycle, cycle[1:]):
        assert right in graph[left]


def automorphisms():
    identity = {generator: generator for generator in GENERATORS}
    alpha = {"x": "Qxq", "t": "t", "z": "z", "q": "q"}
    alpha_inverse = {
        "x": "qxQ",
        "t": "t",
        "z": "z",
        "q": "q",
    }
    sigma = {"x": "x", "t": "Xtx", "z": "zx", "q": "Xq"}
    sigma_inverse = {
        "x": "x",
        "t": "xtX",
        "z": "zX",
        "q": "xq",
    }

    assert compose(alpha_inverse, alpha) == identity
    assert compose(alpha, alpha_inverse) == identity
    assert compose(sigma_inverse, sigma) == identity
    assert compose(sigma, sigma_inverse) == identity
    return alpha, sigma


def test_full_q_normal_closure_traffic_disappears_on_source_first_deletion():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}
    beta_r = substitute(R, beta)
    multipliers = (
        "",
        conjugate("z", "q"),
        conjugate("z", "Q"),
        conjugate("Z", "q"),
        conjugate("Z", "Q"),
        free_reduce(
            conjugate("z", "q")
            + conjugate("x", "Q")
            + conjugate("Tzq", "q")
        ),
        free_reduce(
            conjugate("zqxQZ", "Q")
            + conjugate("qZt", "q")
            + conjugate("ZZxq", "Q")
        ),
    )

    assert beta_r == "qxxxQTTTT"
    assert substitute(beta_r, kill_q) == R
    assert substitute(D, kill_q) == D
    for multiplier in multipliers:
        assert substitute(multiplier, kill_q) == ""
        assert substitute(W + multiplier, kill_q) == U


def test_primitive_u_deletion_and_two_r_factor_return_are_exact():
    identity = {generator: generator for generator in GENERATORS}
    nu = {"x": "x", "t": "t", "z": U, "q": "q"}
    nu_inverse = {
        "x": "x",
        "t": "t",
        "z": P + "Z" + R,
        "q": "q",
    }
    kill_z = {"x": "x", "t": "t", "z": "", "q": "q"}

    assert compose(nu_inverse, nu) == identity
    assert compose(nu, nu_inverse) == identity
    assert substitute(U, nu_inverse) == "z"
    assert substitute(R, nu_inverse) == R

    endpoint_r = substitute(substitute(D, nu_inverse), kill_z)
    expected_endpoint_r = free_reduce(
        "T" + P + R + "x" + inverse_word(P + R)
    )
    endpoint_0 = free_reduce("T" + P + "x" + inverse_word(P))
    first_factor = conjugate(P + "X", R)
    second_factor = conjugate(P, inverse_word(R))

    assert endpoint_r == expected_endpoint_r
    assert free_reduce(inverse_word(endpoint_0) + endpoint_r) == (
        free_reduce(first_factor + second_factor)
    )
    assert free_reduce(
        endpoint_r
        + inverse_word(second_factor)
        + inverse_word(first_factor)
    ) == endpoint_0


def test_four_literal_z_targets_are_reduced_length_eighteen():
    expected = {
        (1, 1): "qxxxQTTTTZqxQtqzqZ",
        (1, -1): "qxxxQTTTTZqxQtqzQZ",
        (-1, 1): "qxxxQTTTTZqxQtqZqz",
        (-1, -1): "qxxxQTTTTZqxQtqZQz",
    }

    for signs, word in expected.items():
        assert target(*signs) == word
        assert free_reduce(word) == word
        assert cyclic_reduce(word) == word
        assert len(word) == 18


def test_exact_whitehead_reductions_and_inverse_automorphisms():
    alpha, sigma = automorphisms()
    first_images = {
        (1, 1): "xxxTTTTZxtqzqZ",
        (1, -1): "xxxTTTTZxtqzQZ",
        (-1, 1): "xxxTTTTZxtqZqz",
        (-1, -1): "xxxTTTTZxtqZQz",
    }
    terminal_positive = {
        1: "xxTTTTZtqzqXZ",
        -1: "xxTTTTZtqzxQZ",
    }

    for signs, expected in first_images.items():
        image = substitute(target(*signs), alpha)
        assert image == expected
        assert len(image) == 14 < len(target(*signs))
        assert cyclic_reduce(image) == image

    for epsilon, expected in terminal_positive.items():
        image = substitute(first_images[(1, epsilon)], sigma)
        assert image == expected
        assert len(image) == 13 < len(first_images[(1, epsilon)])
        assert cyclic_reduce(image) == image


def test_positive_z_pair_has_common_no_cut_whitehead_graph():
    _, sigma = automorphisms()
    alpha, _ = automorphisms()
    words = tuple(
        substitute(substitute(target(1, epsilon), alpha), sigma)
        for epsilon in (1, -1)
    )
    expected_edges = {
        frozenset(edge)
        for edge in (
            ("Q", "X"),
            ("Q", "z"),
            ("T", "X"),
            ("T", "q"),
            ("T", "t"),
            ("X", "x"),
            ("Z", "q"),
            ("Z", "t"),
            ("Z", "x"),
            ("t", "z"),
            ("x", "z"),
        )
    }
    cycle = ("Q", "X", "x", "Z", "q", "T", "t", "z", "Q")

    graphs = tuple(whitehead_graph(word) for word in words)
    assert edge_set(graphs[0]) == expected_edges
    assert edge_set(graphs[1]) == expected_edges
    for graph in graphs:
        assert_spanning_cycle(graph, cycle)
        assert graph_is_connected(graph)
        assert cut_vertices(graph) == set()


def test_negative_z_pair_has_common_no_cut_whitehead_graph():
    alpha, _ = automorphisms()
    words = tuple(
        substitute(target(-1, epsilon), alpha)
        for epsilon in (1, -1)
    )
    expected_edges = {
        frozenset(edge)
        for edge in (
            ("Q", "Z"),
            ("Q", "z"),
            ("T", "X"),
            ("T", "q"),
            ("T", "t"),
            ("X", "t"),
            ("X", "x"),
            ("Z", "t"),
            ("Z", "x"),
            ("q", "z"),
            ("x", "z"),
        )
    }
    cycle = ("Q", "Z", "x", "X", "t", "T", "q", "z", "Q")

    graphs = tuple(whitehead_graph(word) for word in words)
    assert edge_set(graphs[0]) == expected_edges
    assert edge_set(graphs[1]) == expected_edges
    for graph in graphs:
        assert_spanning_cycle(graph, cycle)
        assert graph_is_connected(graph)
        assert cut_vertices(graph) == set()


if __name__ == "__main__":
    test_full_q_normal_closure_traffic_disappears_on_source_first_deletion()
    test_primitive_u_deletion_and_two_r_factor_return_are_exact()
    test_four_literal_z_targets_are_reduced_length_eighteen()
    test_exact_whitehead_reductions_and_inverse_automorphisms()
    test_positive_z_pair_has_common_no_cut_whitehead_graph()
    test_negative_z_pair_has_common_no_cut_whitehead_graph()
    test_positive_z_pair_has_common_no_cut_whitehead_graph()
    test_negative_z_pair_has_common_no_cut_whitehead_graph()
