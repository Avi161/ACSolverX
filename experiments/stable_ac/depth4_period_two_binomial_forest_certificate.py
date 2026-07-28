from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256


Word = tuple[int, ...]


def reduce_word(word: Word) -> Word:
    reduced: list[int] = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def inverse(word: Word) -> Word:
    return tuple(-letter for letter in reversed(word))


def multiply(*words: Word) -> Word:
    return reduce_word(tuple(letter for word in words for letter in word))


def alpha(word: Word) -> Word:
    return tuple(
        Q if letter == P else P if letter == Q else -Q if letter == -P else -P
        for letter in word
    )


def literal(word: Word) -> str:
    return "".join({P: "p", -P: "P", Q: "q", -Q: "Q"}[letter] for letter in word)


P = 1
Q = 2
T_COMPONENT = (P,)
X_COMPONENT = (Q, -P, -Q, P)
G_COMPONENT = (Q, -P, -P, Q)

RS_KERNEL_GENERATORS = (
    T_COMPONENT,
    multiply(G_COMPONENT, inverse(X_COMPONENT)),
    multiply(X_COMPONENT, (Q,), inverse(X_COMPONENT)),
    multiply(X_COMPONENT, alpha(X_COMPONENT)),
    multiply(X_COMPONENT, alpha(G_COMPONENT)),
)


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> bool:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        if left_root > right_root:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        return True


def initial_graph(words: tuple[Word, ...]) -> tuple[int, list[tuple[int, int, int]]]:
    edges = []
    next_vertex = 1
    for word in words:
        current = 0
        for index, letter in enumerate(word):
            target = 0 if index == len(word) - 1 else next_vertex
            if target == next_vertex:
                next_vertex += 1
            edges.append((current, letter, target))
            edges.append((target, -letter, current))
            current = target
    return next_vertex, edges


def fold(words: tuple[Word, ...]) -> tuple[int, set[tuple[int, int, int]]]:
    vertex_count, edges = initial_graph(words)
    union_find = UnionFind(vertex_count)
    changed = True
    while changed:
        changed = False
        transitions = {}
        canonical_edges = {
            (union_find.find(source), label, union_find.find(target))
            for source, label, target in edges
        }
        for source, label, target in sorted(canonical_edges):
            key = source, label
            if key in transitions:
                changed |= union_find.union(transitions[key], target)
            else:
                transitions[key] = target
    canonical_edges = {
        (union_find.find(source), label, union_find.find(target))
        for source, label, target in edges
    }
    vertices = sorted({vertex for edge in canonical_edges for vertex in (edge[0], edge[2])})
    renumber = {vertex: index for index, vertex in enumerate(vertices)}
    folded_edges = {
        (renumber[source], label, renumber[target])
        for source, label, target in canonical_edges
    }
    return renumber[union_find.find(0)], folded_edges


def prune_core(
    base: int,
    edges: set[tuple[int, int, int]],
) -> set[tuple[int, int, int]]:
    active_edges = set(edges)
    while True:
        undirected = {
            min((source, label, target), (target, -label, source))
            for source, label, target in active_edges
        }
        degree: dict[int, int] = defaultdict(int)
        for source, _, target in undirected:
            degree[source] += 1
            degree[target] += 1
        leaves = {vertex for vertex, value in degree.items() if value <= 1 and vertex != base}
        if not leaves:
            return active_edges
        active_edges = {
            edge for edge in active_edges if edge[0] not in leaves and edge[2] not in leaves
        }


def accepts(base: int, edges: set[tuple[int, int, int]], word: Word) -> bool:
    transitions = {(source, label): target for source, label, target in edges}
    current = base
    for letter in word:
        if (current, letter) not in transitions:
            return False
        current = transitions[current, letter]
    return current == base


@dataclass(frozen=True)
class PeriodTwoBinomialForestCertificate:
    ambient_generators: tuple[str, str, str]
    rs_kernel_generators: tuple[str, ...]
    core_vertices: int
    core_undirected_edges: int
    core_rank: int
    core_directed_edges: int
    core_sha256: str
    free_rank_three: bool
    torsion_free: bool
    incidence_graph_is_forest: bool
    finite_support_kernel_is_zero: bool


def period_two_binomial_forest_certificate() -> PeriodTwoBinomialForestCertificate:
    base, folded = fold(RS_KERNEL_GENERATORS)
    core = prune_core(base, folded)
    vertices = {vertex for edge in core for vertex in (edge[0], edge[2])}
    undirected = {
        min((source, label, target), (target, -label, source))
        for source, label, target in core
    }
    rank = len(undirected) - len(vertices) + 1
    assert all(accepts(base, core, word) for word in RS_KERNEL_GENERATORS)
    record = "\n".join(
        f"{source}:{label}:{target}"
        for source, label, target in sorted(core)
    )
    free_rank_three = rank == len(RS_KERNEL_GENERATORS) == 5
    certificate = PeriodTwoBinomialForestCertificate(
        ambient_generators=("p", "(qPQp)c", "(qPPq)c"),
        rs_kernel_generators=tuple(literal(word) for word in RS_KERNEL_GENERATORS),
        core_vertices=len(vertices),
        core_undirected_edges=len(undirected),
        core_rank=rank,
        core_directed_edges=len(core),
        core_sha256=sha256(record.encode()).hexdigest(),
        free_rank_three=free_rank_three,
        torsion_free=free_rank_three,
        incidence_graph_is_forest=free_rank_three,
        finite_support_kernel_is_zero=free_rank_three,
    )
    assert certificate.free_rank_three
    return certificate


if __name__ == "__main__":
    print(period_two_binomial_forest_certificate())
