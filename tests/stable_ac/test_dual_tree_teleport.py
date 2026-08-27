import functools
import random

import pytest

regina = pytest.importorskip("regina")

from experiments.stable_ac.lackenby.dual_tree_teleport import (  # noqa: E402
    cyclic_reduce,
    dual_tree_swap_successors,
    dual_tree_teleport,
    dual_tree_swap,
)


ISO_SIG = "fLLQcbcedeeajasdl"
SOURCE_TREE = frozenset((0, 1, 2, 5))


@functools.lru_cache(maxsize=None)
def type_two_automorphisms(rank):
    letters = tuple(range(1, rank + 1)) + tuple(range(-1, -rank - 1, -1))
    result = []
    for multiplier in letters:
        rest = [letter for letter in letters if letter not in (multiplier, -multiplier)]
        for mask in range(1 << len(rest)):
            subset = {multiplier}
            subset.update(letter for i, letter in enumerate(rest) if mask & (1 << i))
            images = {}
            for generator in range(1, rank + 1):
                if generator in (multiplier, -multiplier):
                    images[generator] = (generator,)
                elif generator in subset and -generator in subset:
                    images[generator] = (-multiplier, generator, multiplier)
                elif generator in subset:
                    images[generator] = (generator, multiplier)
                elif -generator in subset:
                    images[generator] = (-multiplier, generator)
                else:
                    images[generator] = (generator,)
            result.append(tuple(sorted(images.items())))
    return tuple(result)


def apply_automorphism(word, encoded_images):
    images = dict(encoded_images)
    out = []
    for letter in word:
        image = images[abs(letter)]
        if letter < 0:
            image = tuple(-x for x in reversed(image))
        out.extend(image)
    return cyclic_reduce(out)


def whitehead_reduce(relators):
    current = tuple(cyclic_reduce(relator) for relator in relators)
    rank = len(relators)
    while True:
        length = sum(map(len, current))
        best = current
        best_length = length
        for automorphism in type_two_automorphisms(rank):
            candidate = tuple(apply_automorphism(relator, automorphism)
                              for relator in current)
            candidate_length = sum(map(len, candidate))
            if candidate_length < best_length:
                best, best_length = candidate, candidate_length
        if best_length == length:
            return length, current
        current = best


def whitehead_graph_min_delta(relators):
    rank = len(relators)
    letters = tuple(range(1, rank + 1)) + tuple(range(-1, -rank - 1, -1))
    edges = []
    for word in relators:
        edges.extend((left, -right) for left, right in zip(word, word[1:] + word[:1]))
    minimum = 0
    for multiplier in letters:
        rest = [letter for letter in letters if letter not in (multiplier, -multiplier)]
        for mask in range(1 << len(rest)):
            subset = {multiplier}
            subset.update(letter for i, letter in enumerate(rest) if mask & (1 << i))
            cut = sum((left in subset) != (right in subset) for left, right in edges)
            degree = sum((left == multiplier) + (right == multiplier)
                         for left, right in edges)
            minimum = min(minimum, cut - degree)
    return minimum


def whitehead_graph_delta(relators, subset, multiplier):
    edges = []
    for word in relators:
        edges.extend((left, -right) for left, right in zip(word, word[1:] + word[:1]))
    cut = sum((left in subset) != (right in subset) for left, right in edges)
    degree = sum((left == multiplier) + (right == multiplier)
                 for left, right in edges)
    return cut - degree


def test_whitehead_generators_match_known_rank_counts():
    assert len(set(type_two_automorphisms(2))) - 1 == 12
    assert len(set(type_two_automorphisms(3))) - 1 == 90


def test_dual_tree_swap_has_exact_nonautomorphic_target():
    triangulation = regina.Triangulation3.fromIsoSig(ISO_SIG)
    move = dual_tree_swap(
        triangulation,
        primal_tree={0},
        source_dual_tree=SOURCE_TREE,
        add_face_to_tree=4,
        remove_face_from_tree=1,
    )
    assert triangulation.isSphere()
    assert move.target_dual_tree == frozenset((0, 2, 4, 5))
    assert move.source.kept_faces == (3, 4, 6, 7, 8, 9)
    assert move.target.kept_faces == (1, 3, 6, 7, 8, 9)
    assert move.source.exponent_determinant == -1
    assert move.target.exponent_determinant == 1
    assert move.face_removed_from_presentation == 4
    assert move.face_added_to_presentation == 1
    assert move.ordinary_ac_bound == 144

    source_minimum, source_reduced = whitehead_reduce(move.source.relators)
    target_minimum, target_reduced = whitehead_reduce(move.target.relators)
    assert source_minimum == 6
    assert target_minimum == 14
    assert whitehead_graph_min_delta(source_reduced) == 0
    assert whitehead_graph_min_delta(target_reduced) == 0

    successors = list(dual_tree_swap_successors(
        triangulation, primal_tree={0}, source_dual_tree=SOURCE_TREE))
    assert any(successor.target_dual_tree == move.target_dual_tree
               for successor in successors)

    teleport = dual_tree_teleport(
        triangulation,
        primal_tree={0},
        source_dual_tree=SOURCE_TREE,
        target_dual_tree=move.target_dual_tree,
    )
    assert teleport.source == move.source
    assert teleport.target == move.target
    assert teleport.ordinary_ac_bound == 576


def test_substitution_and_whitehead_graph_deltas_agree():
    random.seed(0)
    for rank in (2, 3):
        letters = tuple(range(1, rank + 1)) + tuple(range(-1, -rank - 1, -1))
        for _ in range(100):
            relators = tuple(cyclic_reduce(tuple(
                random.choice(letters) for _ in range(random.randint(1, 8))
            )) for _ in range(rank))
            initial_length = sum(map(len, relators))
            for multiplier in letters:
                rest = [letter for letter in letters
                        if letter not in (multiplier, -multiplier)]
                for mask in range(1 << len(rest)):
                    subset = {multiplier}
                    subset.update(letter for i, letter in enumerate(rest)
                                  if mask & (1 << i))
                    images = {}
                    for generator in range(1, rank + 1):
                        if generator in (multiplier, -multiplier):
                            images[generator] = (generator,)
                        elif generator in subset and -generator in subset:
                            images[generator] = (-multiplier, generator, multiplier)
                        elif generator in subset:
                            images[generator] = (generator, multiplier)
                        elif -generator in subset:
                            images[generator] = (-multiplier, generator)
                        else:
                            images[generator] = (generator,)
                    encoded = tuple(sorted(images.items()))
                    substitution_delta = (
                        sum(len(apply_automorphism(relator, encoded))
                            for relator in relators) - initial_length
                    )
                    assert substitution_delta == whitehead_graph_delta(
                        relators, subset, multiplier)
