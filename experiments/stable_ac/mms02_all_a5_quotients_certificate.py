"""Complete A5 quotient census for the MMS02 signed terminal lift gate."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product

from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    A_WORD,
    B_WORD,
    IDENTITY,
    U_WORD,
    V_WORD,
    Permutation,
    compose,
    conjugate,
    generated_subgroup,
    inverse,
    parity,
)

RELATOR_STAR = "YZYzYzYZyzyZYzYzYZYzyZyZyz"
COLLAPSED_X = "zyZ"
COLLAPSED_Y = "y"
COLLAPSED_Z = "zYZYzYzYZyzyZ"

S5: tuple[Permutation, ...] = tuple(permutations(range(5)))
A5: tuple[Permutation, ...] = tuple(value for value in S5 if parity(value) == 0)


def evaluate(word: str, images: dict[str, Permutation]) -> Permutation:
    value = IDENTITY
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse(image)
        value = compose(value, image)
    return value


def commutator(left: Permutation, right: Permutation) -> Permutation:
    return compose(compose(compose(left, right), inverse(left)), inverse(right))


def canonical_epimorphism(
    triple: tuple[Permutation, Permutation, Permutation],
) -> tuple[Permutation, Permutation, Permutation]:
    return min(
        tuple(conjugate(conjugator, value) for value in triple)
        for conjugator in S5
    )


def three_generator_epimorphisms() -> frozenset[
    tuple[Permutation, Permutation, Permutation]
]:
    epimorphisms = set()
    for triple in product(A5, repeat=3):
        images = dict(zip("xyz", triple, strict=True))
        if evaluate(A_WORD, images) != IDENTITY:
            continue
        if evaluate(B_WORD, images) != IDENTITY:
            continue
        if len(generated_subgroup(triple)) == 60:
            epimorphisms.add(triple)
    return frozenset(epimorphisms)


def collapsed_epimorphisms() -> frozenset[
    tuple[Permutation, Permutation, Permutation]
]:
    epimorphisms = set()
    for y_image, z_image in product(A5, repeat=2):
        collapsed_images = {"y": y_image, "z": z_image}
        if evaluate(RELATOR_STAR, collapsed_images) != IDENTITY:
            continue
        if len(generated_subgroup((y_image, z_image))) != 60:
            continue
        original_images = {
            "x": evaluate(COLLAPSED_X, collapsed_images),
            "y": evaluate(COLLAPSED_Y, collapsed_images),
            "z": evaluate(COLLAPSED_Z, collapsed_images),
        }
        triple = tuple(original_images[letter] for letter in "xyz")
        if evaluate(A_WORD, original_images) != IDENTITY:
            raise AssertionError("the collapsed map stopped killing A")
        if evaluate(B_WORD, original_images) != IDENTITY:
            raise AssertionError("the collapsed map stopped killing B")
        if len(generated_subgroup(triple)) != 60:
            raise AssertionError("the recovered original images stopped generating A5")
        epimorphisms.add(triple)
    return frozenset(epimorphisms)


@dataclass(frozen=True)
class LiftWitness:
    source_commutator_conjugator: Permutation
    commutator_match_conjugator: Permutation
    target_commutator_conjugator: Permutation
    product_conjugator: Permutation
    endpoint_conjugator: Permutation
    commutator_value: Permutation


@dataclass(frozen=True)
class AllA5QuotientsDecision:
    three_generator_epimorphism_count: int
    collapsed_epimorphism_count: int
    automorphism_orbit_count: int
    automorphism_orbit_sizes: tuple[int, ...]
    source_image: Permutation
    target_image: Permutation
    source_commutator_value_count: int
    target_commutator_value_count: int
    compatible_commutator_count: int
    successful_commutator_product_count: int
    witness: LiftWitness
    verdict: str


def lift_predicate(
    triple: tuple[Permutation, Permutation, Permutation],
) -> tuple[int, int, int, int, LiftWitness]:
    images = dict(zip("xyz", triple, strict=True))
    source = inverse(evaluate(U_WORD, images))
    target = evaluate(V_WORD, images)

    source_commutators: dict[Permutation, Permutation] = {}
    target_commutators: dict[Permutation, Permutation] = {}
    for conjugator in A5:
        source_commutators.setdefault(
            commutator(source, conjugator), conjugator
        )
        target_commutators.setdefault(
            commutator(target, conjugator), conjugator
        )

    compatible: dict[
        Permutation,
        tuple[Permutation, Permutation, Permutation],
    ] = {}
    for value, source_conjugator in source_commutators.items():
        match = next(
            (
                (match_conjugator, target_conjugator)
                for target_value, target_conjugator in target_commutators.items()
                for match_conjugator in A5
                if conjugate(match_conjugator, target_value) == value
            ),
            None,
        )
        if match is not None:
            compatible[value] = (source_conjugator, match[0], match[1])

    target_class = frozenset(conjugate(g, target) for g in A5)
    successful_pairs = tuple(
        (value, product_conjugator)
        for value in compatible
        for product_conjugator in A5
        if compose(source, conjugate(product_conjugator, value)) in target_class
    )
    if not successful_pairs:
        raise AssertionError("the sole A5 lift predicate became obstructed")

    value, product_conjugator = successful_pairs[0]
    source_conjugator, match_conjugator, target_conjugator = compatible[value]
    endpoint = compose(source, conjugate(product_conjugator, value))
    endpoint_conjugator = next(
        candidate for candidate in A5 if conjugate(candidate, endpoint) == target
    )
    witness = LiftWitness(
        source_commutator_conjugator=source_conjugator,
        commutator_match_conjugator=match_conjugator,
        target_commutator_conjugator=target_conjugator,
        product_conjugator=product_conjugator,
        endpoint_conjugator=endpoint_conjugator,
        commutator_value=value,
    )

    if commutator(source, witness.source_commutator_conjugator) != value:
        raise AssertionError("the source commutator witness drifted")
    target_commutator = commutator(
        target, witness.target_commutator_conjugator
    )
    if conjugate(witness.commutator_match_conjugator, target_commutator) != value:
        raise AssertionError("the target commutator witness drifted")
    endpoint = compose(
        source,
        conjugate(witness.product_conjugator, value),
    )
    if conjugate(witness.endpoint_conjugator, endpoint) != target:
        raise AssertionError("the endpoint product witness drifted")

    return (
        len(source_commutators),
        len(target_commutators),
        len(compatible),
        len(successful_pairs),
        witness,
    )


def decide_all_a5_quotients() -> AllA5QuotientsDecision:
    if len(A5) != 60:
        raise AssertionError("the even-permutation model stopped being A5")

    direct = three_generator_epimorphisms()
    collapsed = collapsed_epimorphisms()
    if direct != collapsed:
        raise AssertionError("the independent presentation censuses disagree")
    if len(direct) != 120:
        raise AssertionError("the A5 epimorphism count drifted")

    orbit_partition: dict[
        tuple[Permutation, Permutation, Permutation],
        set[tuple[Permutation, Permutation, Permutation]],
    ] = {}
    for triple in direct:
        orbit_partition.setdefault(canonical_epimorphism(triple), set()).add(triple)
    orbit_sizes = tuple(
        sorted(len(orbit) for orbit in orbit_partition.values())
    )
    if orbit_sizes != (120,):
        raise AssertionError("the unique Aut(A5)-orbit classification drifted")

    representative = next(iter(orbit_partition))
    images = dict(zip("xyz", representative, strict=True))
    source = inverse(evaluate(U_WORD, images))
    target = evaluate(V_WORD, images)
    if source != (3, 4, 0, 1, 2):
        raise AssertionError("the canonical source image drifted")
    if target != (2, 0, 4, 1, 3):
        raise AssertionError("the canonical target image drifted")

    source_count, target_count, compatible_count, successful_count, witness = (
        lift_predicate(representative)
    )
    if (source_count, target_count, compatible_count, successful_count) != (
        12,
        12,
        12,
        105,
    ):
        raise AssertionError("the complete A5 lift-predicate census drifted")

    return AllA5QuotientsDecision(
        three_generator_epimorphism_count=len(direct),
        collapsed_epimorphism_count=len(collapsed),
        automorphism_orbit_count=len(orbit_partition),
        automorphism_orbit_sizes=orbit_sizes,
        source_image=source,
        target_image=target,
        source_commutator_value_count=source_count,
        target_commutator_value_count=target_count,
        compatible_commutator_count=compatible_count,
        successful_commutator_product_count=successful_count,
        witness=witness,
        verdict="EVERY_A5_QUOTIENT_SOLVES_THE_SIGNED_LIFT_GATE",
    )


if __name__ == "__main__":
    print(decide_all_a5_quotients())
