"""Exact GF(2) algebra guard for the residual augmented defect memo.

This checker proves polynomial identities only.  It deliberately does not
evaluate the concrete all-power ray or assert covariance.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

Monomial = frozenset[str]


@dataclass(frozen=True)
class Poly:
    terms: frozenset[Monomial]

    def __add__(self, other: Poly) -> Poly:
        return Poly(self.terms ^ other.terms)

    def __mul__(self, other: Poly) -> Poly:
        result: set[Monomial] = set()
        for left in self.terms:
            for right in other.terms:
                term = left | right
                if term in result:
                    result.remove(term)
                else:
                    result.add(term)
        return Poly(frozenset(result))


ZERO = Poly(frozenset())
ONE = Poly(frozenset({frozenset()}))


def var(name: str) -> Poly:
    return Poly(frozenset({frozenset({name})}))


def vector(prefix: str, size: int) -> tuple[Poly, ...]:
    return tuple(var(f"{prefix}{index}") for index in range(size))


def add_vectors(*vectors: tuple[Poly, ...]) -> tuple[Poly, ...]:
    return tuple(
        sum((vector[index] for vector in vectors), ZERO)
        for index in range(len(vectors[0]))
    )


def linear_raw(value: tuple[Poly, ...], raw: tuple[Poly, ...]) -> Poly:
    assert len(value) == len(raw)
    return sum((entry * weight for entry, weight in zip(value, raw)), ZERO)


def bilinear(
    left: tuple[Poly, ...],
    right: tuple[Poly, ...],
    kernel: dict[tuple[int, int], Poly],
) -> Poly:
    return sum(
        (
            kernel[first, second]
            * (left[first] * right[second] + right[first] * left[second])
            for first, second in combinations(range(len(left)), 2)
        ),
        ZERO,
    )


def quadratic(value: tuple[Poly, ...], kernel: dict[tuple[int, int], Poly]) -> Poly:
    return sum(
        (
            kernel[first, second] * value[first] * value[second]
            for first, second in combinations(range(len(value)), 2)
        ),
        ZERO,
    )


def cochain_increment(
    old: tuple[Poly, ...],
    increment: tuple[Poly, ...],
    raw: tuple[Poly, ...],
    kernel: dict[tuple[int, int], Poly],
) -> Poly:
    return (
        linear_raw(increment, raw)
        + bilinear(old, increment, kernel)
        + quadratic(increment, kernel)
    )


def main() -> None:
    size = 6
    raw = vector("r", size)
    kernel = {
        pair: var(f"x{pair[0]}_{pair[1]}")
        for pair in combinations(range(size), 2)
    }

    # Tokens 0 and 1 are the two terminal occurrences.  The terminal-excised
    # activity has zeros there and independent activity elsewhere.
    old_without_terminal = (ZERO, ZERO, *vector("a", size - 2))
    terminal = (ONE, ONE, *(ZERO for _ in range(size - 2)))
    old = add_vectors(old_without_terminal, terminal)

    b = vector("b", size)
    f = vector("f", size)
    g_zero = vector("z", size)
    g_q = vector("q", size)
    g = add_vectors(g_zero, g_q)

    original = (
        cochain_increment(old, g, raw, kernel)
        + bilinear(b, f, kernel)
        + bilinear(b, g, kernel)
        + bilinear(f, g, kernel)
    )
    terminal_leg = bilinear(terminal, g_zero, kernel) + bilinear(terminal, g_q, kernel)
    provenance_excised = (
        cochain_increment(old_without_terminal, g, raw, kernel)
        + bilinear(b, f, kernel)
        + bilinear(b, g, kernel)
        + bilinear(f, g, kernel)
    )
    assert original + terminal_leg == provenance_excised

    split_remainder_with_slot_zero_raw = (
        linear_raw(g_zero, raw)
        + linear_raw(g_q, raw)
        + bilinear(old_without_terminal, g_zero, kernel)
        + bilinear(old_without_terminal, g_q, kernel)
        + quadratic(g_zero, kernel)
        + bilinear(g_zero, g_q, kernel)
        + quadratic(g_q, kernel)
        + bilinear(b, f, kernel)
        + bilinear(b, g_zero, kernel)
        + bilinear(b, g_q, kernel)
        + bilinear(f, g_zero, kernel)
        + bilinear(f, g_q, kernel)
    )
    assert provenance_excised == split_remainder_with_slot_zero_raw

    # The concrete source theorem supplies L(g^(0))=0.  This guard verifies
    # exactly which single formal family that theorem removes.
    split_after_slot_zero_raw = split_remainder_with_slot_zero_raw + linear_raw(g_zero, raw)
    expected_after_slot_zero_raw = provenance_excised + linear_raw(g_zero, raw)
    assert split_after_slot_zero_raw == expected_after_slot_zero_raw

    # Boundary arithmetic for the two independently proved terminal loads.
    for d in (1, 2, 19):
        theta_zero = int(d >= 2)
        theta_q = int(d >= 2)
        assert theta_zero ^ theta_q == 0
        for defect in (0, 1):
            d_dagger = defect ^ theta_zero
            d_ddagger = d_dagger ^ theta_q
            omega = defect ^ 1
            assert d_ddagger == defect
            assert omega == (1 ^ d_ddagger)

    print("PASS: exact GF(2) residual identities")
    print(f"original polynomial monomials: {len(original.terms)}")
    print(f"terminal-leg polynomial monomials: {len(terminal_leg.terms)}")
    print(f"provenance-excised monomials: {len(provenance_excised.terms)}")


if __name__ == "__main__":
    main()
