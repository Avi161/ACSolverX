"""Quotient-isolator elimination and coordinate-endomorphism targets.

The atomic stable-AC path is intentionally not part of the move certificate.
Its existence uses normal generation by the whole source presentation, so its
cost is witness-dependent and this proof supplies no effective input-visible
bound.  That distinguishes the action from a bounded substitution or
witnessed-ACM batch.
"""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.supermoves.certified_acm import (
    cyclic_reduce,
    inverse,
)


@dataclass(frozen=True)
class CoordinateEndomorphismMove:
    source: tuple[str, ...]
    target: tuple[str, ...]
    generator: str
    image: str
    exponent: int
    fresh_generator: str
    quotient_isolator: str
    quotient_difference: str


def exponent_sum(word: str, generator: str) -> int:
    _validate_generator(generator)
    return sum(
        1 if letter == generator else -1 if letter == generator.upper() else 0
        for letter in word
    )


def substitute_generator(word: str, generator: str, image: str) -> str:
    _validate_generator(generator)
    image_inverse = inverse(image)
    return cyclic_reduce(
        "".join(
            image
            if letter == generator
            else image_inverse
            if letter == generator.upper()
            else letter
            for letter in word
        )
    )


def coordinate_endomorphism_move(
    relators: tuple[str, ...],
    generator: str,
    image: str,
    *,
    fresh_generator: str = "z",
) -> CoordinateEndomorphismMove:
    """Apply ``generator -> image`` when its self-exponent is ``+/-1``.

    Soundness requires that ``relators`` normally generate the ambient free
    group.  In the intended use this is guaranteed by the presentation's
    trusted trivial-group provenance.
    """

    _validate_generator(generator)
    _validate_generator(fresh_generator)
    if fresh_generator == generator:
        raise ValueError("fresh generator must differ from the replaced generator")
    alphabet = {letter.lower() for relator in relators for letter in relator}
    if generator not in alphabet:
        raise ValueError("replaced generator is absent from the presentation")
    if fresh_generator in alphabet:
        raise ValueError("fresh generator already occurs in the presentation")
    if any(letter.lower() not in alphabet for letter in image):
        raise ValueError("coordinate image uses a generator outside the presentation")
    exponent = exponent_sum(image, generator)
    if exponent not in (-1, 1):
        raise ValueError("coordinate image must have self-exponent +1 or -1")

    fresh_image = _rename_letter(image, generator, fresh_generator)
    quotient_isolator = generator.upper() + fresh_image
    stabilizer = fresh_generator if exponent == 1 else fresh_generator.upper()
    quotient_difference = inverse(stabilizer) + quotient_isolator
    target = tuple(
        substitute_generator(relator, generator, image) for relator in relators
    )
    return CoordinateEndomorphismMove(
        source=tuple(relators),
        target=target,
        generator=generator,
        image=image,
        exponent=exponent,
        fresh_generator=fresh_generator,
        quotient_isolator=quotient_isolator,
        quotient_difference=quotient_difference,
    )


def specialize_old_generators_to_identity(
    word: str, old_generators: tuple[str, ...]
) -> str:
    old = set(old_generators)
    return cyclic_reduce(
        "".join(letter for letter in word if letter.lower() not in old)
    )


def _rename_letter(word: str, old: str, new: str) -> str:
    return "".join(
        new
        if letter == old
        else new.upper()
        if letter == old.upper()
        else letter
        for letter in word
    )


def _validate_generator(generator: str) -> None:
    if len(generator) != 1 or not generator.islower() or not generator.isalpha():
        raise ValueError("generator must be one lowercase letter")
