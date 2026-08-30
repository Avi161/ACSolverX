"""Complete S4 homomorphism census for the MMS02 terminal quotient."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product

from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    A_WORD,
    B_WORD,
)

Permutation = tuple[int, int, int, int]

IDENTITY: Permutation = (0, 1, 2, 3)
S4: tuple[Permutation, ...] = tuple(permutations(range(4)))
RELATOR_STAR = "YZYzYzYZyzyZYzYzYZYzyZyZyz"
COLLAPSED_X = "zyZ"
COLLAPSED_Y = "y"
COLLAPSED_Z = "zYZYzYzYZyzyZ"


def compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(4))


def inverse(value: Permutation) -> Permutation:
    result = [0] * 4
    for index, image in enumerate(value):
        result[image] = index
    return tuple(result)


def evaluate(word: str, images: dict[str, Permutation]) -> Permutation:
    value = IDENTITY
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse(image)
        value = compose(value, image)
    return value


def generated_subgroup(generators: tuple[Permutation, ...]) -> frozenset[Permutation]:
    subgroup = {IDENTITY}
    frontier = [IDENTITY]
    steps = generators + tuple(inverse(value) for value in generators)
    while frontier:
        current = frontier.pop()
        for step in steps:
            candidate = compose(current, step)
            if candidate not in subgroup:
                subgroup.add(candidate)
                frontier.append(candidate)
    return frozenset(subgroup)


def power(value: Permutation, exponent: int) -> Permutation:
    result = IDENTITY
    for _ in range(exponent):
        result = compose(result, value)
    return result


def collapsed_pairs() -> frozenset[tuple[Permutation, Permutation]]:
    pairs = set()
    for y_image, z_image in product(S4, repeat=2):
        collapsed_images = {"y": y_image, "z": z_image}
        if evaluate(RELATOR_STAR, collapsed_images) != IDENTITY:
            continue
        pairs.add((y_image, z_image))
    return frozenset(pairs)


def collapsed_homomorphisms() -> frozenset[
    tuple[Permutation, Permutation, Permutation]
]:
    homomorphisms = set()
    for y_image, z_image in collapsed_pairs():
        collapsed_images = {"y": y_image, "z": z_image}
        original_images = {
            "x": evaluate(COLLAPSED_X, collapsed_images),
            "y": evaluate(COLLAPSED_Y, collapsed_images),
            "z": evaluate(COLLAPSED_Z, collapsed_images),
        }
        if evaluate(A_WORD, original_images) != IDENTITY:
            raise AssertionError("the collapsed S4 map stopped killing A")
        if evaluate(B_WORD, original_images) != IDENTITY:
            raise AssertionError("the collapsed S4 map stopped killing B")
        homomorphisms.add(tuple(original_images[letter] for letter in "xyz"))
    return frozenset(homomorphisms)


def original_homomorphisms() -> frozenset[
    tuple[Permutation, Permutation, Permutation]
]:
    homomorphisms = set()
    for triple in product(S4, repeat=3):
        images = dict(zip("xyz", triple, strict=True))
        if evaluate(A_WORD, images) != IDENTITY:
            continue
        if evaluate(B_WORD, images) == IDENTITY:
            homomorphisms.add(triple)
    return frozenset(homomorphisms)


@dataclass(frozen=True)
class S4HomomorphismDecision:
    collapsed_candidate_count: int
    original_candidate_count: int
    collapsed_homomorphism_count: int
    original_homomorphism_count: int
    image_order_histogram: tuple[tuple[int, int], ...]
    cyclic_specialization_count: int
    noncyclic_specialization_count: int
    epimorphism_count: int
    verdict: str


def decide_s4_homomorphisms() -> S4HomomorphismDecision:
    pairs = collapsed_pairs()
    if len(pairs) != 24:
        raise AssertionError("the raw collapsed S4 homomorphism count drifted")
    noncyclic_specializations = sum(
        z_image != power(y_image, 3) for y_image, z_image in pairs
    )
    if noncyclic_specializations:
        raise AssertionError("a collapsed S4 map stopped satisfying Z=Y^3")

    collapsed = collapsed_homomorphisms()
    original = original_homomorphisms()
    if collapsed != original:
        raise AssertionError("the original and collapsed S4 censuses disagree")
    if len(original) != 24:
        raise AssertionError("the complete S4 homomorphism count drifted")

    expected = frozenset((value, value, value) for value in S4)
    if original != expected:
        raise AssertionError("an S4 homomorphism stopped factoring through abelianization")
    if len(collapsed) != len(pairs):
        raise AssertionError("the collapsed Tietze reconstruction stopped being injective")

    histogram: dict[int, int] = {}
    epimorphisms = 0
    for triple in original:
        image_order = len(generated_subgroup(triple))
        histogram[image_order] = histogram.get(image_order, 0) + 1
        if image_order == 24:
            epimorphisms += 1
    image_order_histogram = tuple(sorted(histogram.items()))
    if image_order_histogram != ((1, 1), (2, 9), (3, 8), (4, 6)):
        raise AssertionError("the complete S4 image-order histogram drifted")
    if epimorphisms:
        raise AssertionError("an unexpected S4 quotient appeared")

    cyclic_specializations = len(pairs) - noncyclic_specializations
    return S4HomomorphismDecision(
        collapsed_candidate_count=24**2,
        original_candidate_count=24**3,
        collapsed_homomorphism_count=len(collapsed),
        original_homomorphism_count=len(original),
        image_order_histogram=image_order_histogram,
        cyclic_specialization_count=cyclic_specializations,
        noncyclic_specialization_count=noncyclic_specializations,
        epimorphism_count=epimorphisms,
        verdict="EVERY_G_MINUS_TO_S4_HOMOMORPHISM_FACTORS_THROUGH_ABELIANIZATION",
    )


if __name__ == "__main__":
    print(decide_s4_homomorphisms())
