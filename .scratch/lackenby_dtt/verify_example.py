import random

import regina

from explore_dual_tree import (
    apply_automorphism,
    canonical_primal_tree,
    cyclic_reduce,
    dual_endpoints,
    exponent_determinant,
    presentation,
    type_two_automorphisms,
    whitehead_graph_min_delta,
    whitehead_reduce,
)


ISO_SIG = "fLLQcbcedeeajasdl"
SOURCE_TREE = frozenset((0, 1, 2, 5))
TARGET_TREE = frozenset((0, 2, 4, 5))


def graph_delta(relators, subset, multiplier):
    edges = []
    for word in relators:
        if word:
            edges.extend((x, -y) for x, y in zip(word, word[1:] + word[:1]))
    cut = sum((a in subset) != (b in subset) for a, b in edges)
    degree = sum((a == multiplier) + (b == multiplier) for a, b in edges)
    return cut - degree


def independent_delta_crosscheck():
    random.seed(0)
    checked = 0
    for rank in (2, 3):
        letters = tuple(range(1, rank + 1)) + tuple(range(-1, -rank - 1, -1))
        for _ in range(100):
            relators = tuple(
                cyclic_reduce(tuple(random.choice(letters)
                                    for _ in range(random.randint(1, 8))))
                for _ in range(rank)
            )
            for multiplier in letters:
                rest = [x for x in letters if x not in (multiplier, -multiplier)]
                for mask in range(1 << len(rest)):
                    subset = {multiplier}
                    subset.update(x for i, x in enumerate(rest) if mask & (1 << i))
                    images = {}
                    for x in range(1, rank + 1):
                        if x in (multiplier, -multiplier):
                            images[x] = (x,)
                        elif x in subset and -x in subset:
                            images[x] = (-multiplier, x, multiplier)
                        elif x in subset:
                            images[x] = (x, multiplier)
                        elif -x in subset:
                            images[x] = (-multiplier, x)
                        else:
                            images[x] = (x,)
                    encoded = tuple(sorted(images.items()))
                    substitution_delta = (
                        sum(len(apply_automorphism(word, encoded)) for word in relators)
                        - sum(map(len, relators))
                    )
                    assert substitution_delta == graph_delta(relators, subset, multiplier)
                    checked += 1
    return checked


def main():
    assert len(set(type_two_automorphisms(2))) - 1 == 12
    assert len(set(type_two_automorphisms(3))) - 1 == 90
    delta_checks = independent_delta_crosscheck()

    tri = regina.Triangulation3.fromIsoSig(ISO_SIG)
    assert tri.isSphere()
    primal = canonical_primal_tree(tri)
    assert primal == {0}

    source, generators, source_faces = presentation(tri, primal, SOURCE_TREE)
    target, target_generators, target_faces = presentation(tri, primal, TARGET_TREE)
    assert generators == target_generators == (1, 2, 3, 4, 5, 6)
    assert source_faces == (3, 4, 6, 7, 8, 9)
    assert target_faces == (1, 3, 6, 7, 8, 9)
    assert exponent_determinant(source) == -1
    assert exponent_determinant(target) == 1

    endpoints = {i: dual_endpoints(tri.triangle(i)) for i in range(tri.countTriangles())}
    assert SOURCE_TREE - TARGET_TREE == {1}
    assert TARGET_TREE - SOURCE_TREE == {4}
    assert endpoints[1] == (1, 0)
    assert endpoints[4] == (2, 1)

    source_minimum, source_reduced = whitehead_reduce(source)
    target_minimum, target_reduced = whitehead_reduce(target)
    assert source_minimum == 6
    assert target_minimum == 14
    assert whitehead_graph_min_delta(source_reduced) == 0
    assert whitehead_graph_min_delta(target_reduced) == 0

    print({
        "regina": regina.versionString(),
        "iso_sig": ISO_SIG,
        "sphere": tri.isSphere(),
        "f_vector": [tri.countVertices(), tri.countEdges(), tri.countTriangles(), tri.size()],
        "primal_tree": sorted(primal),
        "source_dual_tree": sorted(SOURCE_TREE),
        "target_dual_tree": sorted(TARGET_TREE),
        "source_presentation": source,
        "target_presentation": target,
        "source_determinant": exponent_determinant(source),
        "target_determinant": exponent_determinant(target),
        "source_whitehead_minimum": source_minimum,
        "target_whitehead_minimum": target_minimum,
        "ordinary_ac_bound": 4 * tri.size() ** 2 + 12 * tri.size() - 16,
        "independent_delta_checks": delta_checks,
    })


if __name__ == "__main__":
    main()
