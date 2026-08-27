"""Exact presentation targets from Lackenby dual-tree exchanges.

The public constructor accepts a Regina ``Triangulation3`` recognised as S^3,
a primal maximal tree, and a dual maximal tree.  A dual-tree edge swap removes
one face relator and inserts the previously omitted face relator, with the
ordinary Andrews-Curtis bound from Lackenby Lemma 3.6.
"""

from dataclasses import dataclass
from fractions import Fraction


def free_reduce(word):
    out = []
    for letter in word:
        if out and out[-1] == -letter:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)


def cyclic_reduce(word):
    out = free_reduce(word)
    while len(out) >= 2 and out[0] == -out[-1]:
        out = free_reduce(out[1:-1])
    return out


class _UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left == right:
            return False
        self.parent[right] = left
        return True


def canonical_primal_tree(triangulation):
    union_find = _UnionFind(triangulation.countVertices())
    chosen = set()
    for edge in triangulation.edges():
        left = edge.vertex(0).index()
        right = edge.vertex(1).index()
        if left != right and union_find.union(left, right):
            chosen.add(edge.index())
    if len(chosen) != triangulation.countVertices() - 1:
        raise ValueError("the primal 1-skeleton is not connected")
    return frozenset(chosen)


def dual_endpoints(triangle):
    if triangle.degree() != 2:
        raise ValueError("a closed triangulation must give every triangle degree two")
    return (triangle.embedding(0).simplex().index(),
            triangle.embedding(1).simplex().index())


def _is_tree(vertex_count, edges):
    if len(edges) != vertex_count - 1:
        return False
    union_find = _UnionFind(vertex_count)
    return all(union_find.union(*edge) for edge in edges)


def is_primal_tree(triangulation, edge_indices):
    edges = []
    for index in edge_indices:
        edge = triangulation.edge(index)
        edges.append((edge.vertex(0).index(), edge.vertex(1).index()))
    return _is_tree(triangulation.countVertices(), edges)


def is_dual_tree(triangulation, face_indices):
    return _is_tree(
        triangulation.size(),
        [dual_endpoints(triangulation.triangle(index)) for index in face_indices],
    )


def exponent_determinant(relators):
    rank = len(relators)
    matrix = [[Fraction(sum(
        1 if letter == generator else -1 if letter == -generator else 0
        for letter in relator
    )) for generator in range(1, rank + 1)] for relator in relators]
    determinant = Fraction(1)
    for column in range(rank):
        pivot = next((row for row in range(column, rank)
                      if matrix[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            determinant = -determinant
        value = matrix[column][column]
        determinant *= value
        for j in range(column, rank):
            matrix[column][j] /= value
        for row in range(column + 1, rank):
            value = matrix[row][column]
            for j in range(column, rank):
                matrix[row][j] -= value * matrix[column][j]
    if determinant.denominator != 1:
        raise AssertionError(determinant)
    return int(determinant)


@dataclass(frozen=True)
class TreePresentation:
    relators: tuple
    generator_edges: tuple
    kept_faces: tuple
    exponent_determinant: int


@dataclass(frozen=True)
class DualTreeSwap:
    source: TreePresentation
    target: TreePresentation
    source_dual_tree: frozenset
    target_dual_tree: frozenset
    face_removed_from_presentation: int
    face_added_to_presentation: int
    ordinary_ac_bound: int


@dataclass(frozen=True)
class DualTreeTeleport:
    source: TreePresentation
    target: TreePresentation
    source_dual_tree: frozenset
    target_dual_tree: frozenset
    ordinary_ac_bound: int


def presentation_from_trees(triangulation, primal_tree, dual_tree):
    primal_tree = frozenset(primal_tree)
    dual_tree = frozenset(dual_tree)
    if not triangulation.isSphere():
        raise ValueError("the triangulation is not certified as S^3")
    if not is_primal_tree(triangulation, primal_tree):
        raise ValueError("primal_tree is not a maximal tree")
    if not is_dual_tree(triangulation, dual_tree):
        raise ValueError("dual_tree is not a maximal tree")

    generator_edges = tuple(
        edge.index() for edge in triangulation.edges()
        if edge.index() not in primal_tree
    )
    generator = {edge: index + 1 for index, edge in enumerate(generator_edges)}
    relators = []
    kept_faces = []
    for face in triangulation.triangles():
        if face.index() in dual_tree:
            continue
        word = []
        for edge_in_face, start, end in ((2, 0, 1), (0, 1, 2), (1, 2, 0)):
            edge = face.edge(edge_in_face).index()
            if edge not in generator:
                continue
            mapping = face.edgeMapping(edge_in_face)
            if (mapping[0], mapping[1]) == (start, end):
                sign = 1
            elif (mapping[0], mapping[1]) == (end, start):
                sign = -1
            else:
                raise AssertionError((face.index(), edge_in_face, mapping, start, end))
            word.append(sign * generator[edge])
        relators.append(cyclic_reduce(word))
        kept_faces.append(face.index())

    if len(relators) != len(generator_edges):
        raise AssertionError("P(T,X,X') is not balanced")
    determinant = exponent_determinant(relators)
    if abs(determinant) != 1:
        raise AssertionError("P(T,X,X') failed the trivial-abelianisation gate")
    return TreePresentation(
        relators=tuple(relators),
        generator_edges=generator_edges,
        kept_faces=tuple(kept_faces),
        exponent_determinant=determinant,
    )


def swap_ac_bound(tetrahedra):
    return 4 * tetrahedra * tetrahedra + 12 * tetrahedra - 16


def teleport_ac_bound(tetrahedra):
    return max(0, tetrahedra - 1) * swap_ac_bound(tetrahedra)


def dual_tree_swap(triangulation, primal_tree, source_dual_tree,
                   add_face_to_tree, remove_face_from_tree):
    source_dual_tree = frozenset(source_dual_tree)
    if add_face_to_tree in source_dual_tree:
        raise ValueError("add_face_to_tree is already in the source tree")
    if remove_face_from_tree not in source_dual_tree:
        raise ValueError("remove_face_from_tree is not in the source tree")
    target_dual_tree = frozenset(
        (source_dual_tree - {remove_face_from_tree}) | {add_face_to_tree}
    )
    if not is_dual_tree(triangulation, target_dual_tree):
        raise ValueError("the requested exchange does not produce a dual maximal tree")

    source = presentation_from_trees(triangulation, primal_tree, source_dual_tree)
    target = presentation_from_trees(triangulation, primal_tree, target_dual_tree)
    source_faces = set(source.kept_faces)
    target_faces = set(target.kept_faces)
    if source_faces - target_faces != {add_face_to_tree}:
        raise AssertionError("the exchanged-in tree face was not removed as a relator")
    if target_faces - source_faces != {remove_face_from_tree}:
        raise AssertionError("the exchanged-out tree face was not added as a relator")

    return DualTreeSwap(
        source=source,
        target=target,
        source_dual_tree=source_dual_tree,
        target_dual_tree=target_dual_tree,
        face_removed_from_presentation=add_face_to_tree,
        face_added_to_presentation=remove_face_from_tree,
        ordinary_ac_bound=swap_ac_bound(triangulation.size()),
    )


def dual_tree_swap_successors(triangulation, primal_tree, source_dual_tree):
    source_dual_tree = frozenset(source_dual_tree)
    for add_face in range(triangulation.countTriangles()):
        if add_face in source_dual_tree:
            continue
        for remove_face in sorted(source_dual_tree):
            target = (source_dual_tree - {remove_face}) | {add_face}
            if is_dual_tree(triangulation, target):
                yield dual_tree_swap(
                    triangulation,
                    primal_tree,
                    source_dual_tree,
                    add_face,
                    remove_face,
                )


def dual_tree_teleport(triangulation, primal_tree, source_dual_tree,
                       target_dual_tree):
    source_dual_tree = frozenset(source_dual_tree)
    target_dual_tree = frozenset(target_dual_tree)
    if not is_dual_tree(triangulation, source_dual_tree):
        raise ValueError("source_dual_tree is not a maximal tree")
    if not is_dual_tree(triangulation, target_dual_tree):
        raise ValueError("target_dual_tree is not a maximal tree")
    return DualTreeTeleport(
        source=presentation_from_trees(triangulation, primal_tree, source_dual_tree),
        target=presentation_from_trees(triangulation, primal_tree, target_dual_tree),
        source_dual_tree=source_dual_tree,
        target_dual_tree=target_dual_tree,
        ordinary_ac_bound=teleport_ac_bound(triangulation.size()),
    )
