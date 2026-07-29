from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass

try:
    from experiments.stable_ac import depth4_period_two_binomial_forest_certificate as forest
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
except ModuleNotFoundError:
    import depth4_period_two_binomial_forest_certificate as forest
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_phi4_escape_certificate as phi4


lift = escape.lift
HWord = tuple[int, ...]
Semidirect = tuple[HWord, int]


def free_reduce(word: tuple[int, ...]) -> tuple[int, ...]:
    result: list[int] = []
    for letter in word:
        if result and result[-1] == -letter:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def free_inverse(word: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(-letter for letter in reversed(word))


def substitute(
    word: tuple[int, ...],
    images: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    result: tuple[int, ...] = ()
    for letter in word:
        image = images[abs(letter) - 1]
        if letter < 0:
            image = free_inverse(image)
        result = free_reduce((*result, *image))
    return result


def q_normal_form(word: lift.Word) -> Semidirect:
    h: HWord = ()
    parity = 0
    for letter in lift.quotient_reduce(word):
        if abs(letter) == lift.C:
            parity ^= 1
            continue
        h_letter = forest.P if letter == lift.T else -forest.P
        if parity:
            h_letter = forest.alpha((h_letter,))[0]
        h = forest.multiply(h, (h_letter,))
    return h, parity


def q_inverse(value: Semidirect) -> Semidirect:
    h, parity = value
    inverse_h = forest.inverse(h)
    return (forest.alpha(inverse_h) if parity else inverse_h), parity


def q_multiply(left: Semidirect, right: Semidirect) -> Semidirect:
    left_h, left_parity = left
    right_h, right_parity = right
    if left_parity:
        right_h = forest.alpha(right_h)
    return forest.multiply(left_h, right_h), left_parity ^ right_parity


CORE_BASE, FOLDED = forest.fold(forest.RS_KERNEL_GENERATORS)
CORE = forest.prune_core(CORE_BASE, FOLDED)


def core_coordinates():
    undirected = sorted({
        min((source, label, target), (target, -label, source))
        for source, label, target in CORE
    })
    adjacency = defaultdict(list)
    for edge in undirected:
        source, _, target = edge
        adjacency[source].append((target, edge))
        adjacency[target].append((source, edge))
    seen = {CORE_BASE}
    queue = deque((CORE_BASE,))
    tree_edges = set()
    while queue:
        source = queue.popleft()
        for target, edge in sorted(adjacency[source]):
            if target in seen:
                continue
            seen.add(target)
            tree_edges.add(edge)
            queue.append(target)
    assert seen == {vertex for edge in CORE for vertex in (edge[0], edge[2])}
    non_tree = tuple(edge for edge in undirected if edge not in tree_edges)
    edge_index = {edge: index + 1 for index, edge in enumerate(non_tree)}
    transitions = {(source, label): target for source, label, target in CORE}

    def coordinates(word: HWord) -> tuple[int, ...]:
        current = CORE_BASE
        result: tuple[int, ...] = ()
        for label in word:
            target = transitions[current, label]
            oriented = current, label, target
            canonical = min(oriented, (target, -label, current))
            if canonical in edge_index:
                sign = 1 if oriented == canonical else -1
                result = free_reduce((*result, sign * edge_index[canonical]))
            current = target
        assert current == CORE_BASE
        return result

    return coordinates


COORDINATES = core_coordinates()


def nielsen_inverse(images: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    words = list(images)
    provenance = [(index + 1,) for index in range(len(images))]
    while sum(map(len, words)) > len(words):
        old_total = sum(map(len, words))
        best = None
        for target in range(len(words)):
            for source in range(len(words)):
                if target == source:
                    continue
                for source_sign in (1, -1):
                    source_word = words[source] if source_sign == 1 else free_inverse(words[source])
                    source_provenance = (
                        provenance[source]
                        if source_sign == 1
                        else free_inverse(provenance[source])
                    )
                    for side in (0, 1):
                        candidate_word = free_reduce(
                            (*source_word, *words[target])
                            if side == 0
                            else (*words[target], *source_word)
                        )
                        candidate_total = old_total - len(words[target]) + len(candidate_word)
                        if candidate_total >= old_total:
                            continue
                        candidate_provenance = free_reduce(
                            (*source_provenance, *provenance[target])
                            if side == 0
                            else (*provenance[target], *source_provenance)
                        )
                        record = (
                            candidate_total,
                            target,
                            source,
                            source_sign,
                            side,
                            candidate_word,
                            candidate_provenance,
                        )
                        if best is None or record < best:
                            best = record
        assert best is not None
        _, target, _, _, _, candidate_word, candidate_provenance = best
        words[target] = candidate_word
        provenance[target] = candidate_provenance
    inverse_images: list[tuple[int, ...] | None] = [None] * len(words)
    for word, value in zip(words, provenance):
        assert len(word) == 1
        inverse_images[abs(word[0]) - 1] = value if word[0] > 0 else free_inverse(value)
    assert all(value is not None for value in inverse_images)
    return tuple(value for value in inverse_images if value is not None)


RS_CORE_IMAGES = tuple(COORDINATES(word) for word in forest.RS_KERNEL_GENERATORS)
CORE_IN_RS = nielsen_inverse(RS_CORE_IMAGES)
RS_IN_K = (
    (1,),
    (3, -2),
    (2, 1, -2),
    (2, 2),
    (2, 3),
)
K_IMAGES: tuple[Semidirect, ...] = (
    ((forest.P,), 0),
    (forest.X_COMPONENT, 1),
    (forest.G_COMPONENT, 1),
)


def in_k(value: Semidirect) -> bool:
    h, parity = value
    if parity:
        h = forest.multiply(h, forest.inverse(forest.X_COMPONENT))
    return forest.accepts(CORE_BASE, CORE, h)


def evaluate_k_word(word: tuple[int, ...]) -> Semidirect:
    result: Semidirect = ((), 0)
    for letter in word:
        value = K_IMAGES[abs(letter) - 1]
        if letter < 0:
            value = q_inverse(value)
        result = q_multiply(result, value)
    return result


def rewrite_k(value: Semidirect) -> tuple[int, ...]:
    h, parity = value
    if parity:
        h = forest.multiply(h, forest.inverse(forest.X_COMPONENT))
    assert forest.accepts(CORE_BASE, CORE, h)
    core_word = COORDINATES(h)
    rs_word = substitute(core_word, CORE_IN_RS)
    k_word = substitute(rs_word, RS_IN_K)
    if parity:
        k_word = free_reduce((*k_word, 2))
    assert evaluate_k_word(k_word) == value
    return k_word


def path_between(start: lift.Word, end: lift.Word) -> str:
    start_inverse = q_inverse(q_normal_form(start))
    for epsilon in (0, 1):
        end_c = q_multiply(q_normal_form(end), ((), epsilon))
        ratio = q_multiply(end_c, start_inverse)
        if not in_k(ratio):
            continue
        k_word = rewrite_k(ratio)
        names = {1: "A", 2: "B", 3: "G", -1: "a", -2: "b", -3: "g"}
        path = "".join(names[letter] for letter in reversed(k_word))
        generators = phi4.forest_generators(escape.recurrence_data()[4])
        generators.update({
            name.lower(): lift.quotient_inverse(word)
            for name, word in tuple(generators.items())
        })
        current = start
        for name in path:
            current = escape.act(generators[name], current)
        assert current == end
        return path
    raise ValueError("vertices lie in different K-orbits")


def canonical_vertices_through_depth(depth: int) -> tuple[lift.Word, ...]:
    vertices = {lift.c_vertex(())}
    seen = {()}
    frontier = {()}
    for _ in range(depth):
        frontier = {
            lift.quotient_append(word, letter)
            for word in frontier
            for letter in (lift.C, lift.T, -lift.T)
        } - seen
        seen.update(frontier)
        vertices.update(lift.c_vertex(word) for word in frontier)
    return tuple(sorted(vertices, key=lambda word: (len(word), word)))


@dataclass(frozen=True)
class PeriodTwoSubgroupRewriteCertificate:
    core_vertices: int
    core_directed_edges: int
    core_free_rank: int
    fixed_paths: tuple[tuple[str, str, str], ...]
    depth_six_words_checked: int
    depth_six_k_elements: int
    depth_six_round_trips: int


def subgroup_rewrite_certificate() -> PeriodTwoSubgroupRewriteCertificate:
    forest_certificate = forest.period_two_binomial_forest_certificate()
    escape.period_two_degree_two_escape_certificate()
    phi4.period_two_phi4_escape_certificate()
    core_vertices = {vertex for edge in CORE for vertex in (edge[0], edge[2])}
    undirected_edges = {
        min((source, label, target), (target, -label, source))
        for source, label, target in CORE
    }
    transitions = {(source, label) for source, label, _ in CORE}
    assert all(
        (vertex, label) in transitions
        for vertex in core_vertices
        for label in (forest.P, -forest.P, forest.Q, -forest.Q)
    )
    assert len(core_vertices) == forest_certificate.core_vertices
    assert len(CORE) == forest_certificate.core_directed_edges
    assert len(undirected_edges) - len(core_vertices) + 1 == forest_certificate.core_rank

    fixed_paths = (
        ("ctcTcttct", "aGbaGaGbAA", "tt"),
        ("ttct", "aaBgA", "ctcTctt"),
        ("", "aaBgA", "ctcTctcTT"),
        ("ctcT", "aGaGbA", "tcTT"),
    )
    for start, expected, end in fixed_paths:
        assert path_between(lift.parse_quotient(start), lift.parse_quotient(end)) == expected

    depth_six_vertices = canonical_vertices_through_depth(6)
    depth_six_k_elements = 0
    for vertex in depth_six_vertices:
        value = q_normal_form(vertex)
        if not in_k(value):
            continue
        depth_six_k_elements += 1
        assert evaluate_k_word(rewrite_k(value)) == value
    certificate = PeriodTwoSubgroupRewriteCertificate(
        core_vertices=len(core_vertices),
        core_directed_edges=len(CORE),
        core_free_rank=len(undirected_edges) - len(core_vertices) + 1,
        fixed_paths=fixed_paths,
        depth_six_words_checked=len(depth_six_vertices),
        depth_six_k_elements=depth_six_k_elements,
        depth_six_round_trips=depth_six_k_elements,
    )
    assert certificate.depth_six_words_checked == 127
    assert certificate.depth_six_k_elements > 0
    return certificate


if __name__ == "__main__":
    print(subgroup_rewrite_certificate())
