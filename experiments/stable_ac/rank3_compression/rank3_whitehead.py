"""Whitehead reduction for finite pairs of cyclic words in rank two or three."""

from dataclasses import dataclass
from functools import lru_cache

from experiments.stable_ac.rank3_compression.one_edge import (
    canonical_relator,
    cyclic_reduce,
)
from experiments.stable_ac.rank3_compression.two_stabilization import (
    free_reduce,
    inverse,
)


@lru_cache(maxsize=None)
def second_kind_automorphisms(
    generators: tuple[str, ...] = ("x", "z", "t"),
) -> tuple[dict[str, str], ...]:
    _validate_generators(generators)
    signed = tuple(
        letter
        for generator in generators
        for letter in (generator, generator.upper())
    )
    identity = {generator: generator for generator in generators}
    unique: dict[tuple[str, ...], dict[str, str]] = {}

    for multiplier in signed:
        other_letters = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, multiplier.swapcase())
        )
        for mask in range(1 << len(other_letters)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(other_letters)
                if mask & (1 << index)
            )
            phi: dict[str, str] = {}
            for generator in generators:
                if generator in (
                    multiplier,
                    multiplier.swapcase(),
                ):
                    phi[generator] = generator
                    continue
                positive = generator in subset
                negative = generator.upper() in subset
                if positive and not negative:
                    phi[generator] = generator + multiplier
                elif negative and not positive:
                    phi[generator] = multiplier.swapcase() + generator
                elif positive and negative:
                    phi[generator] = (
                        multiplier.swapcase()
                        + generator
                        + multiplier
                    )
                else:
                    phi[generator] = generator
            key = tuple(phi[generator] for generator in generators)
            unique.setdefault(key, phi)

    identity_key = tuple(identity[generator] for generator in generators)
    unique.pop(identity_key, None)
    return tuple(unique[key] for key in sorted(unique))


def apply_automorphism(
    word: str,
    phi: dict[str, str],
) -> str:
    images_inverse = {
        generator: inverse(image) for generator, image in phi.items()
    }
    pieces: list[str] = []
    for letter in word:
        generator = letter.lower()
        if generator not in phi:
            raise ValueError(f"automorphism has no image for {generator!r}")
        pieces.append(
            phi[generator]
            if letter.islower()
            else images_inverse[generator]
        )
    return free_reduce("".join(pieces))


def compose(
    after: dict[str, str],
    before: dict[str, str],
) -> dict[str, str]:
    if set(after) != set(before):
        raise ValueError("automorphisms use different bases")
    return {
        generator: apply_automorphism(before[generator], after)
        for generator in before
    }


def canonical_cyclic_pair(pair: tuple[str, str]) -> tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("Whitehead pair must contain two words")
    canonical = tuple(sorted(canonical_relator(word) for word in pair))
    if any(not word for word in canonical):
        raise ValueError("Whitehead pair words must be nontrivial")
    return canonical


@dataclass(frozen=True)
class WhiteheadReduction:
    minimum_total: int
    minimum: tuple[str, str]
    phi: dict[str, str]
    steps: tuple[dict[str, str], ...]
    generators: tuple[str, ...]


@dataclass(frozen=True)
class WhiteheadWordReduction:
    minimum_total: int
    minimum: str
    phi: dict[str, str]
    steps: tuple[dict[str, str], ...]
    generators: tuple[str, ...]


def reduce_word(
    word: str,
    generators: tuple[str, ...] = ("x", "z", "t"),
) -> WhiteheadWordReduction:
    _validate_generators(generators)
    current = canonical_relator(word)
    if not current:
        raise ValueError("Whitehead word must be nontrivial")
    total = len(current)
    phi = {generator: generator for generator in generators}
    steps: list[dict[str, str]] = []
    automorphisms = second_kind_automorphisms(generators)

    while True:
        candidates: list[
            tuple[int, str, tuple[str, ...], dict[str, str]]
        ] = []
        for automorphism in automorphisms:
            image = canonical_relator(
                apply_automorphism(current, automorphism)
            )
            image_total = len(image)
            if image_total >= total:
                continue
            candidates.append(
                (
                    image_total,
                    image,
                    tuple(
                        automorphism[generator]
                        for generator in generators
                    ),
                    automorphism,
                )
            )
        if not candidates:
            return WhiteheadWordReduction(
                minimum_total=total,
                minimum=current,
                phi=phi,
                steps=tuple(steps),
                generators=generators,
            )
        _, current, _, chosen = min(candidates)
        total = len(current)
        phi = compose(chosen, phi)
        steps.append(chosen)


def reduce_word_fast(
    word: str,
    generators: tuple[str, ...] = ("x", "z", "t"),
) -> WhiteheadWordReduction:
    """Length-only candidate scoring; canonicalize just the chosen descent."""
    _validate_generators(generators)
    current = canonical_relator(word)
    if not current:
        raise ValueError("Whitehead word must be nontrivial")
    total = len(current)
    phi = {generator: generator for generator in generators}
    steps: list[dict[str, str]] = []
    automorphisms = second_kind_automorphisms(generators)

    while True:
        best = None
        for automorphism in automorphisms:
            image = cyclic_reduce(
                apply_automorphism(current, automorphism)
            )
            image_total = len(image)
            if image_total >= total:
                continue
            key = (
                image_total,
                tuple(
                    automorphism[generator]
                    for generator in generators
                ),
            )
            if best is None or key < best[0]:
                best = (key, image, automorphism)
        if best is None:
            return WhiteheadWordReduction(
                minimum_total=total,
                minimum=current,
                phi=phi,
                steps=tuple(steps),
                generators=generators,
            )
        _, image, chosen = best
        current = canonical_relator(image)
        total = len(current)
        phi = compose(chosen, phi)
        steps.append(chosen)


def reduce_pair(
    pair: tuple[str, str],
    generators: tuple[str, ...] = ("x", "z", "t"),
) -> WhiteheadReduction:
    _validate_generators(generators)
    current = canonical_cyclic_pair(pair)
    total = sum(len(word) for word in current)
    phi = {generator: generator for generator in generators}
    steps: list[dict[str, str]] = []
    automorphisms = second_kind_automorphisms(generators)

    while True:
        candidates: list[
            tuple[
                int,
                tuple[str, str],
                tuple[str, ...],
                dict[str, str],
            ]
        ] = []
        for automorphism in automorphisms:
            image = canonical_cyclic_pair(
                tuple(
                    apply_automorphism(word, automorphism)
                    for word in current
                )
            )
            image_total = sum(len(word) for word in image)
            if image_total >= total:
                continue
            candidates.append(
                (
                    image_total,
                    image,
                    tuple(
                        automorphism[generator]
                        for generator in generators
                    ),
                    automorphism,
                )
            )
        if not candidates:
            return WhiteheadReduction(
                minimum_total=total,
                minimum=current,
                phi=phi,
                steps=tuple(steps),
                generators=generators,
            )
        _, current, _, chosen = min(candidates)
        total = sum(len(word) for word in current)
        phi = compose(chosen, phi)
        steps.append(chosen)


def is_primitive_pair(result: WhiteheadReduction) -> bool:
    if result.minimum_total != 2:
        return False
    if any(len(word) != 1 for word in result.minimum):
        return False
    return (
        result.minimum[0].lower()
        != result.minimum[1].lower()
    )


def is_primitive_word(result: WhiteheadWordReduction) -> bool:
    return result.minimum_total == 1 and len(result.minimum) == 1


def check_word_reduction(
    word: str,
    result: WhiteheadWordReduction,
) -> None:
    current = canonical_relator(word)
    if not current:
        raise AssertionError("source word is trivial")
    previous_total = len(current)
    composed = {
        generator: generator for generator in result.generators
    }
    for index, step in enumerate(result.steps):
        current = canonical_relator(apply_automorphism(current, step))
        total = len(current)
        if total >= previous_total:
            raise AssertionError(
                f"step {index} does not strictly reduce length"
            )
        previous_total = total
        composed = compose(step, composed)
    if composed != result.phi:
        raise AssertionError("composed automorphism mismatch")

    direct = canonical_relator(apply_automorphism(word, result.phi))
    if direct != result.minimum or current != result.minimum:
        raise AssertionError("minimum witness does not replay")
    if result.minimum_total != len(result.minimum):
        raise AssertionError("minimum total mismatch")

    for automorphism in second_kind_automorphisms(result.generators):
        image = canonical_relator(
            apply_automorphism(result.minimum, automorphism)
        )
        if len(image) < result.minimum_total:
            raise AssertionError("stored endpoint admits a Whitehead descent")


def check_reduction(
    pair: tuple[str, str],
    result: WhiteheadReduction,
) -> None:
    current = canonical_cyclic_pair(pair)
    previous_total = sum(len(word) for word in current)
    composed = {
        generator: generator for generator in result.generators
    }
    for index, step in enumerate(result.steps):
        current = canonical_cyclic_pair(
            tuple(apply_automorphism(word, step) for word in current)
        )
        total = sum(len(word) for word in current)
        if total >= previous_total:
            raise AssertionError(
                f"step {index} does not strictly reduce length"
            )
        previous_total = total
        composed = compose(step, composed)
    if composed != result.phi:
        raise AssertionError("composed automorphism mismatch")

    direct = canonical_cyclic_pair(
        tuple(apply_automorphism(word, result.phi) for word in pair)
    )
    if direct != result.minimum or current != result.minimum:
        raise AssertionError("minimum witness does not replay")
    if result.minimum_total != sum(len(word) for word in result.minimum):
        raise AssertionError("minimum total mismatch")

    for automorphism in second_kind_automorphisms(result.generators):
        image = canonical_cyclic_pair(
            tuple(
                apply_automorphism(word, automorphism)
                for word in result.minimum
            )
        )
        if sum(len(word) for word in image) < result.minimum_total:
            raise AssertionError("stored endpoint admits a Whitehead descent")


def _validate_generators(generators: tuple[str, ...]) -> None:
    if not generators:
        raise ValueError("basis must be nonempty")
    if any(
        len(generator) != 1 or not generator.islower()
        for generator in generators
    ):
        raise ValueError("generators must be distinct lowercase letters")
    if len(set(generators)) != len(generators):
        raise ValueError("generators must be distinct")
