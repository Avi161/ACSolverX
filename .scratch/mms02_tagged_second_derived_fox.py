#!/usr/bin/env python3
"""Exact abelianized Fox calculation for the tagged second-derived word.

This is an intentionally standalone scratch calculation.  It does not read or
write any project data; running it only prints the canonical Laurent forms.
"""

from collections import defaultdict


# Laurent polynomials in the abelianization Z[A^+-1, B^+-1].
# A term is keyed by (a_exponent, b_exponent).
Poly = dict[tuple[int, int], int]
ZERO: Poly = {}


def tidy(terms: dict[tuple[int, int], int]) -> Poly:
    return {key: coefficient for key, coefficient in terms.items() if coefficient}


def add(*polynomials: Poly) -> Poly:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for polynomial in polynomials:
        for key, coefficient in polynomial.items():
            result[key] += coefficient
    return tidy(result)


def negate(polynomial: Poly) -> Poly:
    return {key: -coefficient for key, coefficient in polynomial.items()}


def multiply(left: Poly, right: Poly) -> Poly:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for (a_left, b_left), left_coefficient in left.items():
        for (a_right, b_right), right_coefficient in right.items():
            result[(a_left + a_right, b_left + b_right)] += left_coefficient * right_coefficient
    return tidy(result)


def monomial(a_exponent: int, b_exponent: int, coefficient: int = 1) -> Poly:
    return {} if coefficient == 0 else {(a_exponent, b_exponent): coefficient}


ONE = monomial(0, 0)
A = monomial(1, 0)
B = monomial(0, 1)
ONE_MINUS_B = add(ONE, negate(B))
A_MINUS_ONE = add(A, negate(ONE))


def show(polynomial: Poly) -> str:
    """Canonical, copyable sum ordered by the exponent pair."""
    if not polynomial:
        return "0"
    pieces = []
    for (a_exponent, b_exponent), coefficient in sorted(polynomial.items()):
        pieces.append(f"{coefficient}*A^{a_exponent}*B^{b_exponent}")
    return " + ".join(pieces)


def freely_reduce(word: str) -> str:
    inverse = {"a": "A", "A": "a", "b": "B", "B": "b"}
    stack: list[str] = []
    for letter in word:
        if letter not in inverse:
            raise ValueError(f"not a free-group letter: {letter!r}")
        if stack and inverse[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inverse(word: str) -> str:
    inverse_letter = {"a": "A", "A": "a", "b": "B", "B": "b"}
    return "".join(inverse_letter[letter] for letter in reversed(word))


def product(*words: str) -> str:
    return freely_reduce("".join(words))


def exponent_sum(word: str) -> tuple[int, int]:
    return (word.count("a") - word.count("A"), word.count("b") - word.count("B"))


def abelianized_fox(word: str) -> tuple[Poly, Poly]:
    """Return (d word/d a, d word/d b), using left Fox derivatives."""
    derivative_a: Poly = {}
    derivative_b: Poly = {}
    prefix_a = prefix_b = 0
    for letter in freely_reduce(word):
        prefix = monomial(prefix_a, prefix_b)
        if letter == "a":
            derivative_a = add(derivative_a, prefix)
            prefix_a += 1
        elif letter == "A":
            prefix_a -= 1
            derivative_a = add(derivative_a, negate(monomial(prefix_a, prefix_b)))
        elif letter == "b":
            derivative_b = add(derivative_b, prefix)
            prefix_b += 1
        elif letter == "B":
            prefix_b -= 1
            derivative_b = add(derivative_b, negate(monomial(prefix_a, prefix_b)))
    return derivative_a, derivative_b


# The abelianization induced by phi: alpha(A) = B and alpha(B) = B^2.
def alpha(polynomial: Poly) -> Poly:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for (a_exponent, b_exponent), coefficient in polynomial.items():
        result[(0, a_exponent + 2 * b_exponent)] += coefficient
    return tidy(result)


def quotient_by_one_minus_b(numerator: Poly) -> Poly:
    """Exact quotient of numerator by 1-B, or raise if it is not divisible."""
    by_a: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for (a_exponent, b_exponent), coefficient in numerator.items():
        by_a[a_exponent][b_exponent] += coefficient

    quotient: dict[tuple[int, int], int] = {}
    for a_exponent, coefficients in by_a.items():
        coefficients = tidy(coefficients)
        if not coefficients:
            continue
        if sum(coefficients.values()) != 0:
            raise AssertionError("not divisible by 1-B")
        running = 0
        for b_exponent in range(min(coefficients), max(coefficients) + 1):
            running += coefficients.get(b_exponent, 0)
            if running:
                quotient[(a_exponent, b_exponent)] = running
        if running:
            raise AssertionError("nonzero tail in division by 1-B")
    return tidy(quotient)


def main() -> None:
    d = "bbAbaB"
    delta = "bAbABaBB"
    phi_image = {"a": "b", "A": "B", "b": d, "B": inverse(d)}

    def phi(word: str) -> str:
        return product(*(phi_image[letter] for letter in word))

    epsilon = product(inverse(phi(delta)), d, delta, delta, inverse(d))
    # Equivalent spelling requested in the statement:
    assert epsilon == product(phi(product(inverse(delta), "b")), delta, delta, phi("B"))
    zeta = phi(epsilon)

    assert exponent_sum(epsilon) == (-2, 1)
    assert exponent_sum(zeta) == (0, 0)

    fox_a, fox_b = abelianized_fox(zeta)
    f = quotient_by_one_minus_b(fox_a)
    assert fox_a == multiply(f, ONE_MINUS_B)
    assert fox_b == multiply(f, A_MINUS_ONE)

    # Pin the canonical exact coefficient before inspecting its direct-limit image.
    print(f"f = {show(f)}")
    print(f"Fox(zeta) = ({show(fox_a)}, {show(fox_b)})")
    print("reconstruction = verified")

    alpha_f = alpha(f)
    print(f"alpha(f) = {show(alpha_f)}")
    if not alpha_f:
        print("direct-limit status: killed after one alpha application")
        return

    # Once alpha(f) is a nonzero Laurent polynomial in B alone, every further
    # iterate is nonzero: B -> B^2 is injective on Z[B^+-1].
    print(f"alpha^2(f) = {show(alpha(alpha_f))}")
    print("direct-limit status: not killed (alpha(f) is nonzero; B -> B^2 is injective)")


if __name__ == "__main__":
    main()
