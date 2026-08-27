import argparse
import functools
from fractions import Fraction
import itertools
import json
import sys

import regina


def free_reduce(word):
    out = []
    for x in word:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def cyclic_reduce(word):
    out = free_reduce(word)
    while len(out) >= 2 and out[0] == -out[-1]:
        out = free_reduce(out[1:-1])
    return out


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.parent[b] = a
        return True


def canonical_primal_tree(tri):
    uf = UnionFind(tri.countVertices())
    chosen = set()
    for edge in tri.edges():
        a, b = edge.vertex(0).index(), edge.vertex(1).index()
        if a != b and uf.union(a, b):
            chosen.add(edge.index())
    if len(chosen) != tri.countVertices() - 1:
        raise ValueError("primal 1-skeleton is not connected")
    return chosen


def dual_endpoints(triangle):
    if triangle.degree() != 2:
        raise ValueError("closed triangulation triangle does not have degree two")
    return (triangle.embedding(0).simplex().index(),
            triangle.embedding(1).simplex().index())


def dual_spanning_trees(tri, limit=None):
    need = tri.size() - 1
    count = 0
    for faces in itertools.combinations(range(tri.countTriangles()), need):
        uf = UnionFind(tri.size())
        if all(uf.union(*dual_endpoints(tri.triangle(f))) for f in faces):
            yield frozenset(faces)
            count += 1
            if limit is not None and count >= limit:
                return


def presentation(tri, primal_tree, dual_tree):
    generator_edges = [e.index() for e in tri.edges() if e.index() not in primal_tree]
    generator = {e: i + 1 for i, e in enumerate(generator_edges)}

    relators = []
    kept_faces = []
    for face in tri.triangles():
        if face.index() in dual_tree:
            continue
        word = []
        for edge_in_face, start, end in ((2, 0, 1), (0, 1, 2), (1, 2, 0)):
            edge = face.edge(edge_in_face).index()
            if edge in generator:
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
        raise AssertionError((len(generator_edges), len(relators)))
    return tuple(relators), tuple(generator_edges), tuple(kept_faces)


@functools.lru_cache(maxsize=None)
def type_two_automorphisms(rank):
    letters = tuple(range(1, rank + 1)) + tuple(range(-1, -rank - 1, -1))
    result = []
    for multiplier in letters:
        rest = [x for x in letters if x not in (multiplier, -multiplier)]
        for mask in range(1 << len(rest)):
            subset = {multiplier}
            subset.update(x for i, x in enumerate(rest) if mask & (1 << i))
            images = {}
            for x in range(1, rank + 1):
                if x == multiplier or -x == multiplier:
                    images[x] = (x,)
                elif x in subset and -x in subset:
                    images[x] = (-multiplier, x, multiplier)
                elif x in subset:
                    images[x] = (x, multiplier)
                elif -x in subset:
                    images[x] = (-multiplier, x)
                else:
                    images[x] = (x,)
            result.append(tuple(sorted(images.items())))
    return tuple(result)


def apply_automorphism(word, images):
    images = dict(images)
    out = []
    for x in word:
        image = images[abs(x)]
        if x < 0:
            image = tuple(-y for y in reversed(image))
        out.extend(image)
    return cyclic_reduce(out)


def whitehead_reduce(relators):
    current = tuple(cyclic_reduce(r) for r in relators)
    rank = max((abs(x) for r in current for x in r), default=len(current))
    autos = tuple(type_two_automorphisms(rank))
    while True:
        current_length = sum(map(len, current))
        best = current
        best_length = current_length
        for auto in autos:
            candidate = tuple(apply_automorphism(r, auto) for r in current)
            candidate_length = sum(map(len, candidate))
            if candidate_length < best_length:
                best, best_length = candidate, candidate_length
        if best_length == current_length:
            return current_length, current
        current = best


def whitehead_minimum(relators):
    return whitehead_reduce(relators)[0]


def whitehead_graph_min_delta(relators):
    rank = len(relators)
    letters = tuple(range(1, rank + 1)) + tuple(range(-1, -rank - 1, -1))
    edges = []
    for word in relators:
        if word:
            edges.extend((x, -y) for x, y in zip(word, word[1:] + word[:1]))
    minimum = None
    for multiplier in letters:
        rest = [x for x in letters if x not in (multiplier, -multiplier)]
        for mask in range(1 << len(rest)):
            subset = {multiplier}
            subset.update(x for i, x in enumerate(rest) if mask & (1 << i))
            cut = sum((a in subset) != (b in subset) for a, b in edges)
            degree = sum((a == multiplier) + (b == multiplier) for a, b in edges)
            delta = cut - degree
            minimum = delta if minimum is None else min(minimum, delta)
    return minimum


def exponent_determinant(relators):
    rank = len(relators)
    matrix = [[Fraction(sum(1 if x == j else -1 if x == -j else 0 for x in word))
               for j in range(1, rank + 1)] for word in relators]
    determinant = Fraction(1)
    for col in range(rank):
        pivot = next((row for row in range(col, rank) if matrix[row][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
            determinant = -determinant
        value = matrix[col][col]
        determinant *= value
        for j in range(col, rank):
            matrix[col][j] /= value
        for row in range(col + 1, rank):
            value = matrix[row][col]
            for j in range(col, rank):
                matrix[row][j] -= value * matrix[col][j]
    if determinant.denominator != 1:
        raise AssertionError(determinant)
    return int(determinant)


def make_triangulation(kind, grow, two_three):
    if kind == "simplicial":
        tri = regina.Example3.simplicialSphere()
    elif kind == "sphere":
        tri = regina.Example3.sphere()
    elif kind == "bings":
        tri = regina.Example3.bingsHouse()
    elif kind == "three":
        tri = regina.Example3.threeSphere()
    else:
        raise ValueError(kind)
    for _ in range(grow):
        next_tri = None
        for tetrahedron in tri.simplices():
            next_tri = tri.withPachner(tetrahedron)
            if next_tri is not None:
                break
        if next_tri is None:
            raise RuntimeError("no legal 1-4 move")
        tri = next_tri
    for _ in range(two_three):
        next_tri = None
        for triangle in tri.triangles():
            next_tri = tri.withPachner(triangle)
            if next_tri is not None:
                break
        if next_tri is None:
            raise RuntimeError("no legal 2-3 move")
        tri = next_tri
    return tri


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("simplicial", "sphere", "bings", "three"),
                        default="simplicial")
    parser.add_argument("--grow", type=int, default=0)
    parser.add_argument("--two-three", type=int, default=0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    tri = make_triangulation(args.kind, args.grow, args.two_three)
    if not tri.isSphere():
        raise AssertionError("Regina does not recognise the triangulation as S^3")
    primal = canonical_primal_tree(tri)
    rows = []
    for dual in dual_spanning_trees(tri, args.limit):
        relators, generators, kept_faces = presentation(tri, primal, dual)
        determinant = exponent_determinant(relators)
        if abs(determinant) != 1:
            raise AssertionError((dual, relators, determinant))
        rows.append({
            "dual_tree": sorted(dual),
            "kept_faces": kept_faces,
            "relators": relators,
            "exponent_determinant": determinant,
            "whitehead_minimum": whitehead_minimum(relators),
        })
    print(json.dumps({
        "regina": regina.versionString(),
        "iso_sig": tri.isoSig(),
        "f_vector": [tri.countVertices(), tri.countEdges(), tri.countTriangles(), tri.size()],
        "primal_tree": sorted(primal),
        "generator_edges": presentation(tri, primal, next(dual_spanning_trees(tri, 1)))[1],
        "n_dual_trees": len(rows),
        "minimum_lengths": sorted({r["whitehead_minimum"] for r in rows}),
        "rows": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
