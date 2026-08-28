from dataclasses import dataclass
from typing import Iterable, Tuple


R = "xxxYYYY"
S = "xyxYXY"
RELATORS = {"R": R, "S": S}


def inverse(word: str) -> str:
    return "".join(letter.swapcase() for letter in reversed(word))


def reduce_word(word: str) -> str:
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def defect(left: str, right: str) -> str:
    return reduce_word(left + inverse(right))


@dataclass(frozen=True)
class Factor:
    conjugator: str
    relator: str
    sign: int


@dataclass(frozen=True)
class EqCert:
    left: str
    right: str
    factors: Tuple[Factor, ...]


def factor_defect(factor: Factor) -> str:
    relator = RELATORS[factor.relator]
    if factor.sign == -1:
        relator = inverse(relator)
    return reduce_word(factor.conjugator + relator + inverse(factor.conjugator))


def expanded_factors(factors: Iterable[Factor]) -> str:
    return reduce_word("".join(factor_defect(factor) for factor in factors))


def verify(cert: EqCert) -> None:
    assert expanded_factors(cert.factors) == defect(cert.left, cert.right)


def refl(word: str) -> EqCert:
    return EqCert(word, word, ())


def axiom(name: str) -> EqCert:
    return EqCert(RELATORS[name], "", (Factor("", name, 1),))


def symmetric(cert: EqCert) -> EqCert:
    return EqCert(
        cert.right,
        cert.left,
        tuple(Factor(f.conjugator, f.relator, -f.sign) for f in reversed(cert.factors)),
    )


def invert_equality(cert: EqCert) -> EqCert:
    inverted = tuple(
        Factor(f.conjugator, f.relator, -f.sign) for f in reversed(cert.factors)
    )
    shifted = tuple(
        Factor(inverse(cert.left) + f.conjugator, f.relator, f.sign)
        for f in inverted
    )
    return EqCert(inverse(cert.left), inverse(cert.right), shifted)


def transitive(first: EqCert, second: EqCert) -> EqCert:
    assert reduce_word(first.right) == reduce_word(second.left)
    return EqCert(first.left, second.right, first.factors + second.factors)


def product(first: EqCert, second: EqCert) -> EqCert:
    shifted = tuple(
        Factor(first.right + factor.conjugator, factor.relator, factor.sign)
        for factor in second.factors
    )
    return EqCert(
        first.left + second.left,
        first.right + second.right,
        first.factors + shifted,
    )


def conjugate(cert: EqCert, word: str) -> EqCert:
    return EqCert(
        word + cert.left + inverse(word),
        word + cert.right + inverse(word),
        tuple(Factor(word + f.conjugator, f.relator, f.sign) for f in cert.factors),
    )


def power(cert: EqCert, exponent: int) -> EqCert:
    assert exponent >= 0
    result = refl("")
    for _ in range(exponent):
        result = product(result, cert)
    return result


def free_equality(left: str, right: str) -> EqCert:
    assert reduce_word(left) == reduce_word(right)
    return EqCert(left, right, ())


def from_defect(cert: EqCert, left: str, right: str) -> EqCert:
    assert reduce_word(cert.right) == ""
    return chain(
        free_equality(left, cert.left + right),
        product(cert, refl(right)),
    )


def chain(*certificates: EqCert) -> EqCert:
    result = certificates[0]
    for certificate in certificates[1:]:
        result = transitive(result, certificate)
    return result


def certificate() -> dict[str, EqCert]:
    delta = "xyx"
    r_defect = axiom("R")
    r = from_defect(r_defect, "xxx", "yyyy")
    s = axiom("S")
    braid = from_defect(s, "xyx", "yxy")

    delta_x_delta_y = free_equality(delta + "x" + inverse(delta) + "Y", S)
    swap_x = from_defect(
        chain(delta_x_delta_y, s), delta + "x" + inverse(delta), "y"
    )
    delta_y_delta_x = free_equality(
        delta + "y" + inverse(delta) + "X", "x" + inverse(S) + "X"
    )
    x_s_inverse_x = conjugate(invert_equality(s), "x")
    swap_y = from_defect(
        chain(delta_y_delta_x, x_s_inverse_x), delta + "y" + inverse(delta), "x"
    )

    y3_x4 = chain(
        symmetric(power(swap_x, 3)),
        from_defect(
            conjugate(r_defect, delta),
            delta + "xxx" + inverse(delta),
            delta + "yyyy" + inverse(delta),
        ),
        power(swap_y, 4),
    )

    x9_y12 = power(r, 3)
    y12_x16 = power(y3_x4, 4)
    x9_x16 = transitive(x9_y12, y12_x16)
    one_x7 = product(x9_x16, refl("X" * 9))
    x7_one = symmetric(one_x7)

    y9_x12 = power(y3_x4, 3)
    x12_y16 = power(r, 4)
    y9_y16 = transitive(y9_x12, x12_y16)
    one_y7 = product(y9_y16, refl("Y" * 9))
    y7_one = symmetric(one_y7)

    x4_xminus3 = product(x7_one, refl("XXX"))
    y3_xminus3 = transitive(y3_x4, x4_xminus3)
    y15_xminus15 = power(y3_xminus3, 5)
    y15_y = product(power(y7_one, 2), refl("y"))
    xminus7_one = invert_equality(x7_one)
    xminus15_xminus1 = product(power(xminus7_one, 2), refl("X"))
    y_xminus1 = chain(symmetric(y15_y), y15_xminus15, xminus15_xminus1)

    x_y_x = product(product(refl("x"), y_xminus1), refl("x"))
    y_x_y = product(product(y_xminus1, refl("x")), y_xminus1)
    braid_after_y = chain(symmetric(x_y_x), braid, y_x_y)
    x2_one = product(refl("x"), braid_after_y)

    x6_one = power(x2_one, 3)
    x7_x = product(x6_one, refl("x"))
    x_one_raw = symmetric(chain(symmetric(x7_one), x7_x))
    x_one = chain(
        free_equality("x", x_one_raw.left),
        x_one_raw,
        free_equality(x_one_raw.right, ""),
    )
    y_one_raw = transitive(y_xminus1, invert_equality(x_one))
    y_one = chain(
        free_equality("y", y_one_raw.left),
        y_one_raw,
        free_equality(y_one_raw.right, ""),
    )

    return {
        "swap_x": swap_x,
        "swap_y": swap_y,
        "y3_x4": y3_x4,
        "x7_one": x7_one,
        "y7_one": y7_one,
        "y_xminus1": y_xminus1,
        "x2_one": x2_one,
        "x_one": x_one,
        "y_one": y_one,
    }


def test_every_factor_expands_to_its_claimed_conjugate_relator() -> None:
    for cert in certificate().values():
        for factor in cert.factors:
            relator = RELATORS[factor.relator]
            signed = relator if factor.sign == 1 else inverse(relator)
            claimed = reduce_word(factor.conjugator + signed + inverse(factor.conjugator))
            assert factor_defect(factor) == claimed


def test_all_certificates_reduce_to_their_claimed_defects() -> None:
    for cert in certificate().values():
        verify(cert)


def test_final_normal_closure_certificates_are_literal_generators() -> None:
    final = certificate()
    assert final["x_one"].left == "x"
    assert final["x_one"].right == ""
    assert final["y_one"].left == "y"
    assert final["y_one"].right == ""
    verify(final["x_one"])
    verify(final["y_one"])
