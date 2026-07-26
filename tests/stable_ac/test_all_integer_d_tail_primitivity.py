from __future__ import annotations

from collections.abc import Mapping, Sequence


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
S = "qxxxQTTTTZqxQt"

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


def compose(outer: WordMap, inner: WordMap) -> dict[str, str]:
    return {
        generator: substitute(inner[generator], outer)
        for generator in GENERATORS
    }


def word_map(x: str, t: str, z: str, q: str) -> dict[str, str]:
    return {"x": x, "t": t, "z": z, "q": q}


def word_power(word: str, exponent: int) -> str:
    if exponent < 0:
        word = inverse_word(word)
        exponent = -exponent
    return free_reduce(word * exponent)


def source(eta: int, epsilon: int, exponent: int) -> str:
    q_power = "q" if eta == 1 else "Q"
    w_power = W if epsilon == 1 else inverse_word(W)
    return free_reduce(
        q_power + w_power + word_power(D, exponent)
    )


def whitehead_graph(word: str) -> Graph:
    word = cyclic_reduce(word)
    graph = {letter: set() for letter in LETTERS}
    for left, right in zip(word, word[1:] + word[:1]):
        first = INVERSE_LETTER[left]
        graph[first].add(right)
        graph[right].add(first)
    return graph


def assert_spanning_cycle(
    graph: Graph,
    cycle: tuple[str, ...],
) -> None:
    assert cycle[0] == cycle[-1]
    assert set(cycle[:-1]) == set(LETTERS)
    for left, right in zip(cycle, cycle[1:]):
        assert right in graph[left]


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


ALPHA = word_map("Qxq", "t", "zq", "q")
ALPHA_INVERSE = word_map("qxQ", "t", "zQ", "q")

BOUNDARY_BLOCKS = {
    (1, 1): "qxxxTTTTQZxtq",
    (-1, 1): "QxxxTTTTQZxtq",
    (-1, -1): "QQTXzqttttXXX",
}

SPANNING_CYCLES = {
    (1, 1, -1): (
        "x", "Q", "z", "t", "T", "q", "Z", "X", "x",
    ),
    (1, 1, 1): (
        "x", "Q", "T", "X", "t", "z", "q", "Z", "x",
    ),
    (-1, 1, -1): (
        "x", "X", "Z", "q", "T", "Q", "t", "z", "x",
    ),
    (-1, 1, 1): (
        "x", "X", "Z", "q", "T", "Q", "t", "z", "x",
    ),
    (-1, -1, -1): (
        "x", "X", "Z", "q", "Q", "T", "t", "z", "x",
    ),
    (-1, -1, 1): (
        "x", "T", "X", "Z", "q", "Q", "t", "z", "x",
    ),
}

BASED_PAIR_STEPS = (
    word_map("x", "t", "z", "qz"),
    word_map("x", "t", "xz", "q"),
    word_map("x", "t", "tzT", "qT"),
    word_map("x", "t", "zT", "q"),
    word_map("x", "t", "zT", "q"),
    word_map("x", "t", "zT", "q"),
    word_map("qxQ", "t", "zQ", "q"),
    word_map("x", "tx", "zx", "q"),
    word_map("x", "t", "z", "qX"),
    word_map("x", "t", "z", "qX"),
    word_map("Qx", "t", "zq", "q"),
)
THETA_INVERSE = word_map(
    "qxxxZt",
    "zXZt",
    "TqXQzttttqXXXQ",
    "qxxZt",
)


def theta() -> dict[str, str]:
    beta_inverse = word_map("Qxq", "t", "z", "q")
    combined = {generator: generator for generator in GENERATORS}
    for step in BASED_PAIR_STEPS:
        combined = compose(step, combined)
    return compose(combined, beta_inverse)


def unique_z_coordinate_maps(word: str) -> tuple[WordMap, WordMap]:
    positions = [
        index for index, letter in enumerate(word)
        if letter in "zZ"
    ]
    assert len(positions) == 1
    index = positions[0]
    left = word[:index]
    z_letter = word[index]
    right = word[index + 1:]
    assert not set(left + right) & set("zZ")
    coordinate = word_map("x", "t", word, "q")
    if z_letter == "z":
        inverse_z = free_reduce(
            inverse_word(left) + "z" + inverse_word(right)
        )
    else:
        inverse_z = free_reduce(right + "Z" + left)
    inverse = word_map("x", "t", inverse_z, "q")
    return coordinate, inverse


def is_primitive(eta: int, epsilon: int, exponent: int) -> bool:
    return exponent == 0 or (eta, epsilon) == (1, -1)


def test_all_zero_power_rows_are_exact_unique_z_coordinates():
    identity = {generator: generator for generator in GENERATORS}
    for eta in (1, -1):
        for epsilon in (1, -1):
            word = source(eta, epsilon, 0)
            coordinate, inverse = unique_z_coordinate_maps(word)
            assert coordinate["z"] == word
            assert compose(inverse, coordinate) == identity
            assert compose(coordinate, inverse) == identity


def test_positive_inverse_w_row_is_primitive_for_every_integer_power():
    identity = {generator: generator for generator in GENERATORS}
    theta_map = theta()
    assert compose(theta_map, THETA_INVERSE) == identity
    assert compose(THETA_INVERSE, theta_map) == identity
    assert free_reduce(W + "Q") == S
    assert substitute(S, theta_map) == "Z"
    assert substitute(D, theta_map) == "T"

    for exponent in (-11, -3, -1, 0, 2, 7, 12):
        word = source(1, -1, exponent)
        assert word == free_reduce(
            inverse_word(S) + word_power(D, exponent)
        )
        shear = word_map(
            "x",
            "t",
            free_reduce("z" + word_power("t", exponent)),
            "q",
        )
        shear_inverse = word_map(
            "x",
            "t",
            free_reduce("z" + word_power("t", -exponent)),
            "q",
        )
        assert compose(shear, shear_inverse) == identity
        assert compose(shear_inverse, shear) == identity
        assert substitute(substitute(word, theta_map), shear) == "z"


def test_common_whitehead_map_has_the_three_exact_boundary_blocks():
    identity = {generator: generator for generator in GENERATORS}
    assert compose(ALPHA, ALPHA_INVERSE) == identity
    assert compose(ALPHA_INVERSE, ALPHA) == identity

    for signs, boundary in BOUNDARY_BLOCKS.items():
        for sign in (-1, 1):
            for magnitude in (1, 2, 5):
                exponent = sign * magnitude
                transformed = canonical_relator(
                    substitute(source(*signs, exponent), ALPHA)
                )
                expected = canonical_relator(
                    boundary + word_power(D, exponent)
                )
                assert transformed == expected


def test_five_symbolic_cycles_obstruct_every_nonzero_other_row():
    for signs, boundary in BOUNDARY_BLOCKS.items():
        for sign in (-1, 1):
            base_word = boundary + word_power(D, sign)
            assert free_reduce(base_word) == base_word
            assert cyclic_reduce(base_word) == base_word
            assert len(base_word) == 17

            graph = whitehead_graph(base_word)
            cycle = SPANNING_CYCLES[(*signs, sign)]
            assert_spanning_cycle(graph, cycle)
            assert graph_is_connected(graph)
            assert cut_vertices(graph) == set()

            base_edges = {
                frozenset((left, right))
                for left, neighbors in graph.items()
                for right in neighbors
            }
            for magnitude in (1, 2, 3, 7, 12):
                word = boundary + word_power(D, sign * magnitude)
                assert free_reduce(word) == word
                assert cyclic_reduce(word) == word
                assert len(word) == 4 * magnitude + 13
                power_graph = whitehead_graph(word)
                power_edges = {
                    frozenset((left, right))
                    for left, neighbors in power_graph.items()
                    for right in neighbors
                }
                assert base_edges <= power_edges
                assert_spanning_cycle(power_graph, cycle)
                assert cut_vertices(power_graph) == set()


def test_every_left_right_d_split_reduces_to_the_total_power():
    for eta in (1, -1):
        for epsilon in (1, -1):
            q_power = "q" if eta == 1 else "Q"
            w_power = W if epsilon == 1 else inverse_word(W)
            for left, right in (
                (-5, 2),
                (-1, -1),
                (0, 0),
                (2, -5),
                (3, 4),
            ):
                split = free_reduce(
                    word_power(D, left)
                    + q_power
                    + w_power
                    + word_power(D, right)
                )
                conjugated = free_reduce(
                    word_power(D, -left)
                    + split
                    + word_power(D, left)
                )
                assert conjugated == source(
                    eta,
                    epsilon,
                    left + right,
                )
                assert is_primitive(
                    eta,
                    epsilon,
                    left + right,
                ) is (
                    left + right == 0
                    or (eta, epsilon) == (1, -1)
                )


def test_all_integer_d_tail_primitivity_criterion():
    for eta in (1, -1):
        for epsilon in (1, -1):
            for exponent in (-12, -3, -1, 0, 1, 4, 11):
                expected = (
                    exponent == 0
                    or (eta, epsilon) == (1, -1)
                )
                assert is_primitive(eta, epsilon, exponent) is expected
