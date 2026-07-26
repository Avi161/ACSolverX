from __future__ import annotations

from collections.abc import Mapping


GENERATORS = "xtq"
LETTERS = "xXtTqQ"
INVERSE_LETTER = {
    "x": "X",
    "X": "x",
    "t": "T",
    "T": "t",
    "q": "Q",
    "Q": "q",
}
R = "xxxTTTT"

WordMap = Mapping[str, str]
GroupRing = dict[str, int]


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


def substitute(word: str, images: WordMap) -> str:
    result = ""
    for letter in word:
        generator = letter.lower()
        image = images[generator]
        if letter.isupper():
            image = inverse_word(image)
        result = free_reduce(result + image)
    return result


def compose(outer: WordMap, inner: WordMap) -> dict[str, str]:
    return {
        generator: substitute(inner[generator], outer)
        for generator in GENERATORS
    }


def v_word(k: int) -> str:
    return f"q{R[:k]}Q{R[k:]}q"


def whitehead_graph(word: str) -> dict[str, set[str]]:
    graph = {letter: set() for letter in LETTERS}
    for left, right in zip(word, word[1:] + word[:1]):
        first = INVERSE_LETTER[left]
        graph[first].add(right)
        graph[right].add(first)
    return graph


def graph_is_connected(
    graph: Mapping[str, set[str]],
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


def cut_vertices(graph: Mapping[str, set[str]]) -> set[str]:
    assert graph_is_connected(graph)
    return {
        vertex
        for vertex in graph
        if not graph_is_connected(graph, omitted=vertex)
    }


def ring_add_term(ring: GroupRing, word: str, coefficient: int) -> None:
    reduced = free_reduce(word)
    ring[reduced] = ring.get(reduced, 0) + coefficient
    if ring[reduced] == 0:
        del ring[reduced]


def fox_derivative(word: str, generator: str) -> GroupRing:
    derivative: GroupRing = {}
    prefix = ""
    for letter in word:
        if letter == generator:
            ring_add_term(derivative, prefix, 1)
        prefix = free_reduce(prefix + letter)
        if letter == generator.upper():
            ring_add_term(derivative, prefix, -1)
    return derivative


def specialize_ring(ring: GroupRing, images: WordMap) -> GroupRing:
    result: GroupRing = {}
    for word, coefficient in ring.items():
        ring_add_term(result, substitute(word, images), coefficient)
    return result


def test_six_three_q_words_specialize_to_the_retained_relator():
    kill_q = {"x": "x", "t": "t", "q": ""}
    for k in range(1, len(R)):
        word = v_word(k)
        assert free_reduce(word) == word
        assert substitute(word, kill_q) == R
        assert sum(letter == "q" for letter in word) == 2
        assert sum(letter == "Q" for letter in word) == 1


def test_whitehead_cut_vertex_gate_is_unique_at_the_relator_seam():
    for k in range(1, len(R)):
        graph = whitehead_graph(v_word(k))
        assert graph_is_connected(graph)
        expected = {"q", "Q"} if k == 3 else set()
        assert cut_vertices(graph) == expected


def test_explicit_automorphism_takes_q_to_v3():
    alpha = {"x": "x", "t": "t", "q": R + "q"}
    alpha_inverse = {
        "x": "x",
        "t": "t",
        "q": inverse_word(R) + "q",
    }
    beta = {"x": "qxQ", "t": "t", "q": "q"}
    beta_inverse = {"x": "Qxq", "t": "t", "q": "q"}

    phi = compose(beta, alpha)
    phi_inverse = compose(alpha_inverse, beta_inverse)
    identity = {"x": "x", "t": "t", "q": "q"}

    assert phi["q"] == v_word(3)
    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity


def test_exact_fox_rows_for_all_six_words():
    kill_q = {"x": "x", "t": "t", "q": ""}
    expected_x = fox_derivative(R, "x")
    expected_t = fox_derivative(R, "t")

    for k in range(1, len(R)):
        word = v_word(k)
        assert specialize_ring(fox_derivative(word, "x"), kill_q) == expected_x
        assert specialize_ring(fox_derivative(word, "t"), kill_q) == expected_t

        expected_q: GroupRing = {}
        ring_add_term(expected_q, "", 1)
        ring_add_term(expected_q, R[:k], -1)
        ring_add_term(expected_q, R, 1)
        assert specialize_ring(fox_derivative(word, "q"), kill_q) == expected_q
        assert sum(expected_q.values()) == 1


def test_straightening_quotient_is_coherent_only_on_transported_words():
    kill_q = {"x": "x", "t": "t", "q": ""}
    alpha = {"x": "x", "t": "t", "q": R + "q"}
    alpha_inverse = {
        "x": "x",
        "t": "t",
        "q": inverse_word(R) + "q",
    }
    beta = {"x": "qxQ", "t": "t", "q": "q"}
    beta_inverse = {"x": "Qxq", "t": "t", "q": "q"}
    phi = compose(beta, alpha)
    phi_inverse = compose(alpha_inverse, beta_inverse)

    def quotient(word: str) -> str:
        return substitute(substitute(word, phi_inverse), kill_q)

    assert quotient("x") == free_reduce(R + "x" + inverse_word(R))
    assert quotient("t") == "t"
    assert quotient("q") == inverse_word(R)

    for survivor in ("x", "t", "xtXTTx", R, "xTXXtt"):
        assert quotient(substitute(survivor, phi)) == free_reduce(survivor)


if __name__ == "__main__":
    test_six_three_q_words_specialize_to_the_retained_relator()
    test_whitehead_cut_vertex_gate_is_unique_at_the_relator_seam()
    test_explicit_automorphism_takes_q_to_v3()
    test_exact_fox_rows_for_all_six_words()
    test_straightening_quotient_is_coherent_only_on_transported_words()
