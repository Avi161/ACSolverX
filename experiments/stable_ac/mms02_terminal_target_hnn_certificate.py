"""Exact source collapse and target HNN form for the terminal MMS02 pair."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from experiments.stable_ac.mms02_terminal_both_row_cleanup_certificate import (
    EXPECTED_WORDS,
)


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def apply_images(word: str, images: dict[str, str]) -> str:
    return free_reduce(
        "".join(
            images[letter]
            if letter.islower()
            else inverse(images[letter.lower()])
            for letter in word
        )
    )


@dataclass(frozen=True)
class Factor:
    conjugator: str
    sign: int


@dataclass(frozen=True)
class EqualityCertificate:
    left: str
    right: str
    factors: tuple[Factor, ...]


def factor_word(factor: Factor, relator: str) -> str:
    body = relator if factor.sign == 1 else inverse(relator)
    return free_reduce(
        factor.conjugator + body + inverse(factor.conjugator)
    )


def verify_equality(certificate: EqualityCertificate, relator: str) -> None:
    expanded = free_reduce(
        "".join(factor_word(factor, relator) for factor in certificate.factors)
    )
    defect = free_reduce(certificate.left + inverse(certificate.right))
    if expanded != defect:
        raise AssertionError("the normal-closure equality certificate drifted")


def reflexive(word: str) -> EqualityCertificate:
    return EqualityCertificate(word, word, ())


def free_equality(left: str, right: str) -> EqualityCertificate:
    if free_reduce(left) != free_reduce(right):
        raise AssertionError("the proposed free equality does not reduce")
    return EqualityCertificate(left, right, ())


def symmetric(certificate: EqualityCertificate) -> EqualityCertificate:
    return EqualityCertificate(
        certificate.right,
        certificate.left,
        tuple(
            Factor(factor.conjugator, -factor.sign)
            for factor in reversed(certificate.factors)
        ),
    )


def invert_equality(certificate: EqualityCertificate) -> EqualityCertificate:
    inverted = tuple(
        Factor(factor.conjugator, -factor.sign)
        for factor in reversed(certificate.factors)
    )
    shifted = tuple(
        Factor(inverse(certificate.left) + factor.conjugator, factor.sign)
        for factor in inverted
    )
    return EqualityCertificate(
        inverse(certificate.left), inverse(certificate.right), shifted
    )


def product(
    first: EqualityCertificate,
    second: EqualityCertificate,
) -> EqualityCertificate:
    shifted = tuple(
        Factor(first.right + factor.conjugator, factor.sign)
        for factor in second.factors
    )
    return EqualityCertificate(
        first.left + second.left,
        first.right + second.right,
        first.factors + shifted,
    )


def chain(*certificates: EqualityCertificate) -> EqualityCertificate:
    left = certificates[0].left
    right = certificates[0].right
    factors: tuple[Factor, ...] = ()
    for index, certificate in enumerate(certificates):
        if index and free_reduce(right) != free_reduce(certificate.left):
            raise AssertionError("the equality chain has mismatched endpoints")
        right = certificate.right
        factors += certificate.factors
    return EqualityCertificate(left, right, factors)


def context(
    prefix: str,
    certificate: EqualityCertificate,
    suffix: str,
) -> EqualityCertificate:
    return product(product(reflexive(prefix), certificate), reflexive(suffix))


def normalize(certificate: EqualityCertificate) -> EqualityCertificate:
    return chain(
        free_equality(free_reduce(certificate.left), certificate.left),
        certificate,
        free_equality(certificate.right, free_reduce(certificate.right)),
    )


def from_defect(
    certificate: EqualityCertificate,
    left: str,
    right: str,
) -> EqualityCertificate:
    if free_reduce(certificate.right):
        raise AssertionError("the source certificate is not a defect")
    return chain(
        free_equality(left, certificate.left + right),
        product(certificate, reflexive(right)),
    )


def braid_killer_certificate() -> EqualityCertificate:
    braid_relator = "yxyXYX"
    axiom = EqualityCertificate(braid_relator, "", (Factor("", 1),))
    braid = from_defect(axiom, "yxy", "xyx")

    xy_inverse_x_to_inverse_yxy = normalize(
        product(product(reflexive("Y"), braid), reflexive("X"))
    )
    inverse_xyx_to_yx_inverse_y = normalize(
        symmetric(
            product(
                product(reflexive("X"), symmetric(braid)),
                reflexive("Y"),
            )
        )
    )

    source_first = normalize(
        context("YXyXY", symmetric(braid), "Yxx")
    )
    source_second = normalize(
        context("Y", inverse_xyx_to_yx_inverse_y, "x")
    )
    source_to_core = chain(source_first, source_second)

    conjugate = "xyxyXyXYX"
    target_first = normalize(
        context("xy", xy_inverse_x_to_inverse_yxy, "yXYX")
    )
    inverse_braid = invert_equality(braid)
    target_second = normalize(
        context("xxyy", symmetric(inverse_braid), "")
    )
    target_third = normalize(
        context("x", xy_inverse_x_to_inverse_yxy, "Y")
    )
    target_to_core = chain(target_first, target_second, target_third)

    if free_reduce(source_to_core.right) != "xYx":
        raise AssertionError("the source braid reduction missed its core")
    if free_reduce(target_to_core.right) != "xYx":
        raise AssertionError("the conjugated mu2 reduction missed its core")
    certificate = chain(source_to_core, symmetric(target_to_core))
    if free_reduce(certificate.left) != EXPECTED_WORDS["e_source"]:
        raise AssertionError("the terminal source word drifted")
    if free_reduce(certificate.right) != conjugate:
        raise AssertionError("the conjugated trefoil killer drifted")
    verify_equality(certificate, braid_relator)
    return certificate


@dataclass(frozen=True)
class SourceCollapseDecision:
    braid_relator: str
    source_row: str
    mu2: str
    conjugator: str
    conjugated_mu2: str
    equality_factors: tuple[tuple[str, int], ...]
    transformed_relator: str
    transformed_mu2: str
    cleanup_factors: tuple[str, ...]
    verdict: str


def decide_source_collapse() -> SourceCollapseDecision:
    braid_relator = "yxyXYX"
    source_row = EXPECTED_WORDS["e_source"]
    mu2 = "xyXyX"
    conjugator = "xy"
    conjugated_mu2 = free_reduce(
        conjugator + mu2 + inverse(conjugator)
    )
    certificate = braid_killer_certificate()

    images = {"x": "x", "y": "yx"}
    transformed_relator = apply_images(braid_relator, images)
    transformed_mu2 = apply_images(mu2, images)
    if transformed_relator != "yxxyXYX":
        raise AssertionError("the braid relator Nielsen image drifted")
    if transformed_mu2 != "xyy":
        raise AssertionError("the trefoil killer Nielsen image drifted")

    cleanup_factors = (
        transformed_mu2,
        "Y" + transformed_mu2 + "y",
        "YY" + inverse(transformed_mu2) + "yy",
        inverse(transformed_mu2),
    )
    if free_reduce("".join(cleanup_factors)) != free_reduce(
        inverse(transformed_relator) + "y"
    ):
        raise AssertionError("the trefoil killer cleanup identity drifted")
    if free_reduce(transformed_mu2 + "YY") != "x":
        raise AssertionError("the final donor cleanup does not give x")

    return SourceCollapseDecision(
        braid_relator=braid_relator,
        source_row=source_row,
        mu2=mu2,
        conjugator=conjugator,
        conjugated_mu2=conjugated_mu2,
        equality_factors=tuple(
            (factor.conjugator, factor.sign)
            for factor in certificate.factors
        ),
        transformed_relator=transformed_relator,
        transformed_mu2=transformed_mu2,
        cleanup_factors=cleanup_factors,
        verdict="SOURCE_PAIR_AC_TRIVIAL",
    )


def magnus_rewrite(word: str) -> tuple[tuple[tuple[int, int], ...], int]:
    height = 0
    letters = []
    for letter in word:
        if letter == "x":
            height += 1
        elif letter == "X":
            height -= 1
        elif letter == "y":
            letters.append((height, 1))
        elif letter == "Y":
            letters.append((height, -1))
        else:
            raise AssertionError("the Magnus word uses an unknown letter")
    return tuple(letters), height


def phi(word: str) -> str:
    return apply_images(word, {"a": "b", "b": "abAb"})


@dataclass(frozen=True)
class TargetHNNDecision:
    target_relator: str
    target_row: str
    transformed_relator: str
    transformed_row: str
    relator_magnus: tuple[tuple[int, int], ...]
    row_magnus: tuple[tuple[int, int], ...]
    phi_a: str
    phi_b: str
    iterates: tuple[str, ...]
    shifted_base_word: str
    shifted_base_word_digest: str
    verdict: str


def decide_target_hnn() -> TargetHNNDecision:
    target_relator = EXPECTED_WORDS["T"]
    target_row = EXPECTED_WORDS["e_target"]
    images = {"x": "x", "y": "yx"}
    transformed_relator = apply_images(target_relator, images)
    transformed_row = apply_images(target_row, images)
    if transformed_relator != "yXYxyxYXXyx":
        raise AssertionError("the target relator Nielsen image drifted")
    if transformed_row != "XYXyXYxyxYxyXYxyx":
        raise AssertionError("the target killer Nielsen image drifted")

    relator_magnus, relator_height = magnus_rewrite(transformed_relator)
    row_magnus, row_height = magnus_rewrite(transformed_row)
    if relator_magnus != ((0, 1), (-1, -1), (0, 1), (1, -1), (-1, 1)):
        raise AssertionError("the target relator Magnus rewrite drifted")
    if relator_height != 0:
        raise AssertionError("the target relator has nonzero stable exponent")
    expected_row = (
        (-1, -1),
        (-2, 1),
        (-3, -1),
        (-2, 1),
        (-1, -1),
        (0, 1),
        (-1, -1),
        (0, 1),
    )
    if row_magnus != expected_row or row_height != 1:
        raise AssertionError("the target row Magnus rewrite drifted")

    iterates = ["b"]
    for _ in range(3):
        iterates.append(phi(iterates[-1]))
    expected_iterates = ("b", "abAb", "babbAb", "abAbbabAbabbAb")
    if tuple(iterates) != expected_iterates:
        raise AssertionError("the ascending-HNN iterates drifted")
    shifted_base_word = free_reduce(
        inverse(iterates[2])
        + iterates[1]
        + inverse(iterates[0])
        + iterates[1]
        + inverse(iterates[2])
        + iterates[3]
        + inverse(iterates[2])
        + iterates[3]
    )
    if shifted_base_word != "BaBBABBabAbbabbAbbabAbabbAb":
        raise AssertionError("the shifted target base word drifted")

    commutator = free_reduce(
        inverse("b")
        + inverse("abAb")
        + "b"
        + "abAb"
    )
    if not commutator:
        raise AssertionError("the two endomorphism images accidentally commute")

    return TargetHNNDecision(
        target_relator=target_relator,
        target_row=target_row,
        transformed_relator=transformed_relator,
        transformed_row=transformed_row,
        relator_magnus=relator_magnus,
        row_magnus=row_magnus,
        phi_a="b",
        phi_b="abAb",
        iterates=tuple(iterates),
        shifted_base_word=shifted_base_word,
        shifted_base_word_digest=sha256(
            shifted_base_word.encode()
        ).hexdigest(),
        verdict="TARGET_STRICT_ASCENDING_HNN_GATE",
    )


if __name__ == "__main__":
    print(decide_source_collapse())
    print(decide_target_hnn())
