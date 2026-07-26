from __future__ import annotations

from collections.abc import Mapping


GENERATORS = ("x", "t", "z", "q")
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

A = "qxxxQTTTT"
C = "qxQtq"
W = A + "Z" + C
D = "TzxZ"

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


def inverse_word(word: str) -> str:
    return "".join(INVERSE_LETTER[letter] for letter in reversed(word))


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while (
        len(word) > 1
        and INVERSE_LETTER[word[0]] == word[-1]
    ):
        word = free_reduce(word[1:-1])
    return word


def canonical_relator(word: str) -> str:
    word = cyclic_reduce(word)
    if not word:
        return ""
    candidates: list[str] = []
    for orientation in (word, inverse_word(word)):
        candidates.extend(
            orientation[index:] + orientation[:index]
            for index in range(len(orientation))
        )
    return min(candidates)


def substitute(word: str, images: WordMap) -> str:
    result = ""
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse_word(image)
        result = free_reduce(result + image)
    return result


def second_kind_automorphisms() -> set[tuple[str, ...]]:
    signed = tuple(
        letter
        for generator in GENERATORS
        for letter in (generator, generator.upper())
    )
    identity = tuple(GENERATORS)
    maps: set[tuple[str, ...]] = set()
    for multiplier in signed:
        other_letters = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, INVERSE_LETTER[multiplier])
        )
        for mask in range(1 << len(other_letters)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(other_letters)
                if mask & (1 << index)
            )
            images: dict[str, str] = {}
            for generator in GENERATORS:
                if generator in (
                    multiplier,
                    INVERSE_LETTER[multiplier],
                ):
                    images[generator] = generator
                    continue
                positive = generator in subset
                negative = generator.upper() in subset
                if positive and not negative:
                    images[generator] = generator + multiplier
                elif negative and not positive:
                    images[generator] = (
                        INVERSE_LETTER[multiplier] + generator
                    )
                elif positive and negative:
                    images[generator] = (
                        INVERSE_LETTER[multiplier]
                        + generator
                        + multiplier
                    )
                else:
                    images[generator] = generator
            maps.add(tuple(images[generator] for generator in GENERATORS))
    maps.discard(identity)
    return maps


def word_map(x: str, t: str, z: str, q: str) -> dict[str, str]:
    return {"x": x, "t": t, "z": z, "q": q}


def source(eta: int, epsilon: int, delta: int) -> str:
    q_word = "q" if eta == 1 else "Q"
    w_word = W if epsilon == 1 else inverse_word(W)
    d_word = D if delta == 1 else inverse_word(D)
    return free_reduce(q_word + w_word + d_word)


PRIMITIVE_STEPS_POSITIVE_D = (
    word_map("Qxq", "t", "zq", "q"),
    word_map("Txt", "t", "Tzt", "Tq"),
    word_map("Txt", "t", "Tzt", "Tq"),
    word_map("Txt", "t", "Tzt", "Tq"),
    word_map("Txt", "t", "Tzt", "Tq"),
    word_map("x", "Xt", "z", "qx"),
    word_map("x", "t", "z", "Zq"),
    word_map("Txt", "t", "Tzt", "qt"),
    word_map("x", "t", "Xz", "Xqx"),
    word_map("Zxz", "tz", "z", "qz"),
    word_map("x", "t", "Xz", "Xqx"),
    word_map("Tx", "t", "Tz", "qt"),
)

PRIMITIVE_STEPS_NEGATIVE_D = (
    word_map("Qxq", "Qtq", "zq", "q"),
    word_map("txT", "t", "tzT", "qT"),
    word_map("txT", "t", "tzT", "qT"),
    word_map("txT", "t", "tzT", "qT"),
    word_map("Qxq", "Qt", "Qzq", "q"),
    word_map("x", "Xtx", "zx", "Xq"),
    word_map("x", "Xtx", "zx", "Xq"),
    word_map("x", "Xtx", "zx", "Xq"),
    word_map("Zx", "Zt", "z", "Zq"),
    word_map("Zxz", "Zt", "z", "Zq"),
    word_map("Txt", "t", "Tz", "Tq"),
    word_map("x", "Xt", "zx", "Xq"),
    word_map("x", "Xt", "zx", "Xq"),
)

ALPHA = word_map("Qxq", "t", "zq", "q")
MU = word_map("txT", "t", "tzT", "qT")
NU = word_map("x", "Xtx", "zx", "Xqx")


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


def test_all_eight_freely_reduced_source_words():
    expected = {
        (1, 1, 1): "qqxxxQTTTTZqxQtqTzxZ",
        (1, 1, -1): "qqxxxQTTTTZqxQtqzXZt",
        (1, -1, 1): "TqXQzttttqXXXQTzxZ",
        (1, -1, -1): "TqXQzttttqXXXQzXZt",
        (-1, 1, 1): "xxxQTTTTZqxQtqTzxZ",
        (-1, 1, -1): "xxxQTTTTZqxQtqzXZt",
        (-1, -1, 1): "QQTqXQzttttqXXXQTzxZ",
        (-1, -1, -1): "QQTqXQzttttqXXXQzXZt",
    }
    for signs, word in expected.items():
        assert source(*signs) == word
        assert free_reduce(word) == word


def replay_primitive_certificate(
    word: str,
    steps: tuple[dict[str, str], ...],
    lengths: tuple[int, ...],
    terminal: str,
) -> None:
    whitehead_maps = second_kind_automorphisms()
    current = canonical_relator(word)
    observed = [len(current)]
    for step in steps:
        assert tuple(step[generator] for generator in GENERATORS) in (
            whitehead_maps
        )
        current = canonical_relator(substitute(current, step))
        observed.append(len(current))
    assert tuple(observed) == lengths
    assert current == terminal


def test_two_primitive_rows_have_strict_whitehead_certificates():
    replay_primitive_certificate(
        source(1, -1, 1),
        PRIMITIVE_STEPS_POSITIVE_D,
        (18, 15, 14, 13, 12, 11, 10, 9, 8, 6, 4, 2, 1),
        "Q",
    )
    replay_primitive_certificate(
        source(1, -1, -1),
        PRIMITIVE_STEPS_NEGATIVE_D,
        (16, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
        "Z",
    )


def nonprimitive_certificates():
    return {
        (1, 1, 1): (
            (ALPHA,),
            "TTTTQZxtqTzxZqxxx",
            {
                "Q-T", "Q-t", "Q-x", "T-X", "T-q", "T-t",
                "X-Z", "X-t", "X-x", "Z-q", "Z-x", "q-z",
                "t-z", "x-z",
            },
            ("Q", "T", "X", "t", "z", "q", "Z", "x", "Q"),
        ),
        (1, 1, -1): (
            (ALPHA, MU),
            "TTTTQtZxqzXZqxxx",
            {
                "Q-t", "Q-x", "Q-z", "T-X", "T-Z", "T-t",
                "X-Z", "X-q", "X-x", "Z-x", "q-t", "q-z",
                "x-z",
            },
            ("Q", "t", "T", "Z", "X", "q", "z", "x", "Q"),
        ),
        (-1, 1, 1): (
            (ALPHA,),
            "TTTTQZxtqTzxZQxxx",
            {
                "Q-T", "Q-t", "Q-z", "T-X", "T-q", "T-t",
                "X-Z", "X-t", "X-x", "Z-q", "Z-x", "q-x",
                "t-z", "x-z",
            },
            ("Q", "T", "X", "Z", "q", "x", "z", "t", "Q"),
        ),
        (-1, 1, -1): (
            (ALPHA,),
            "TTTTQZxtqzXZtQxxx",
            {
                "Q-T", "Q-t", "Q-z", "T-X", "T-q", "T-t",
                "X-Z", "X-t", "X-x", "Z-q", "Z-x", "q-x",
                "t-z", "x-z",
            },
            ("Q", "T", "X", "Z", "q", "x", "z", "t", "Q"),
        ),
        (-1, -1, 1): (
            (ALPHA,),
            "TTTTQZxtqqzXZtxxx",
            {
                "Q-q", "Q-t", "Q-z", "T-X", "T-q", "T-t",
                "T-x", "X-Z", "X-t", "X-x", "Z-q", "Z-x",
                "t-z", "x-z",
            },
            ("Q", "q", "T", "X", "Z", "x", "z", "t", "Q"),
        ),
        (-1, -1, -1): (
            (ALPHA, NU),
            "TTTTQZtqqTxzxZxx",
            {
                "Q-T", "Q-q", "Q-t", "T-X", "T-q", "T-t",
                "X-Z", "X-x", "X-z", "Z-q", "Z-x", "t-x",
                "t-z", "x-z",
            },
            ("Q", "T", "X", "z", "t", "x", "Z", "q", "Q"),
        ),
    }


def parse_edges(edges: set[str]) -> set[frozenset[str]]:
    return {
        frozenset(edge.split("-"))
        for edge in edges
    }


def test_six_nonprimitive_rows_have_exact_spanning_cycle_graphs():
    for signs, (steps, terminal, edges, cycle) in (
        nonprimitive_certificates().items()
    ):
        current = canonical_relator(source(*signs))
        for step in steps:
            current = canonical_relator(substitute(current, step))
        assert current == canonical_relator(terminal)
        assert cyclic_reduce(terminal) == terminal
        assert len(terminal) in (16, 17)

        graph = whitehead_graph(terminal)
        assert edge_set(graph) == parse_edges(edges)
        assert_spanning_cycle(graph, cycle)
        assert graph_is_connected(graph)
        assert cut_vertices(graph) == set()


if __name__ == "__main__":
    test_all_eight_freely_reduced_source_words()
    test_two_primitive_rows_have_strict_whitehead_certificates()
    test_six_nonprimitive_rows_have_exact_spanning_cycle_graphs()
