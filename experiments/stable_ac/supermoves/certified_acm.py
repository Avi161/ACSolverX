"""Finite, proof-carrying ACM supermoves.

An ACM move replaces one relator by a conjugate of itself in the quotient by
the other relators.  The certificate used here writes that quotient equality
as an explicit product of conjugates of the other relators.  This makes every
generated target replayable using ordinary AC1--AC3 moves and turns the
otherwise infinite ACM action family into a finite family at any chosen
width and conjugator-length bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product


def inverse(word: str) -> str:
    return "".join(letter.swapcase() for letter in reversed(word))


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if not letter.isalpha() or len(letter) != 1:
            raise ValueError(f"invalid generator letter: {letter!r}")
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while len(word) >= 2 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    return word


def cyclic_orientations(word: str) -> tuple[str, ...]:
    word = cyclic_reduce(word)
    if not word:
        return ("",)
    values: set[str] = set()
    for oriented in (word, inverse(word)):
        for offset in range(len(oriented)):
            values.add(oriented[offset:] + oriented[:offset])
    return tuple(sorted(values))


def cyclic_key(word: str) -> str:
    return min(cyclic_orientations(word))


@dataclass(frozen=True)
class NormalFactor:
    relator_index: int
    exponent: int
    conjugator: str = ""

    def __post_init__(self) -> None:
        if self.exponent not in (-1, 1):
            raise ValueError("factor exponent must be +1 or -1")
        free_reduce(self.conjugator)


@dataclass(frozen=True)
class ACMCertificate:
    target_index: int
    source_exponent: int = 1
    source_conjugator: str = ""
    factors: tuple[NormalFactor, ...] = ()

    def __post_init__(self) -> None:
        if self.source_exponent not in (-1, 1):
            raise ValueError("source exponent must be +1 or -1")
        free_reduce(self.source_conjugator)


@dataclass(frozen=True)
class AtomicACMove:
    kind: str
    target_index: int
    other_index: int | None = None
    letter: str | None = None


@dataclass(frozen=True)
class ACMSuccessor:
    relators: tuple[str, ...]
    certificate: ACMCertificate
    atomic_bound: int


def certified_target_word(
    relators: tuple[str, ...], certificate: ACMCertificate
) -> str:
    _validate_certificate(relators, certificate)
    source = relators[certificate.target_index]
    if certificate.source_exponent == -1:
        source = inverse(source)
    c = certificate.source_conjugator
    pieces = [inverse(c), source, c]
    for factor in certificate.factors:
        relator = relators[factor.relator_index]
        if factor.exponent == -1:
            relator = inverse(relator)
        h = factor.conjugator
        pieces.extend((inverse(h), relator, h))
    return free_reduce("".join(pieces))


def apply_certified_acm(
    relators: tuple[str, ...], certificate: ACMCertificate
) -> tuple[str, ...]:
    target = certified_target_word(relators, certificate)
    result = list(relators)
    result[certificate.target_index] = target
    return tuple(result)


def expand_atomic_moves(
    relators: tuple[str, ...], certificate: ACMCertificate
) -> tuple[AtomicACMove, ...]:
    _validate_certificate(relators, certificate)
    target = certificate.target_index
    moves: list[AtomicACMove] = []
    if certificate.source_exponent == -1:
        moves.append(AtomicACMove("invert", target))
    for letter in certificate.source_conjugator:
        moves.append(AtomicACMove("conjugate", target, letter=letter))
    for factor in certificate.factors:
        other = factor.relator_index
        if factor.exponent == -1:
            moves.append(AtomicACMove("invert", other))
        for letter in factor.conjugator:
            moves.append(AtomicACMove("conjugate", other, letter=letter))
        moves.append(AtomicACMove("multiply", target, other_index=other))
        for letter in inverse(factor.conjugator):
            moves.append(AtomicACMove("conjugate", other, letter=letter))
        if factor.exponent == -1:
            moves.append(AtomicACMove("invert", other))
    return tuple(moves)


def replay_atomic_moves(
    relators: tuple[str, ...], moves: tuple[AtomicACMove, ...]
) -> tuple[str, ...]:
    state = list(relators)
    for move in moves:
        target = move.target_index
        if not 0 <= target < len(state):
            raise ValueError("atomic move target index out of range")
        if move.kind == "invert":
            state[target] = inverse(state[target])
        elif move.kind == "conjugate":
            if move.letter is None or len(move.letter) != 1:
                raise ValueError("conjugation requires one generator letter")
            state[target] = free_reduce(
                move.letter.swapcase() + state[target] + move.letter
            )
        elif move.kind == "multiply":
            other = move.other_index
            if other is None or not 0 <= other < len(state) or other == target:
                raise ValueError("multiplication requires a distinct relator")
            state[target] = free_reduce(state[target] + state[other])
        else:
            raise ValueError(f"unknown atomic move: {move.kind!r}")
    return tuple(state)


def atomic_move_bound(certificate: ACMCertificate) -> int:
    return (
        int(certificate.source_exponent == -1)
        + len(certificate.source_conjugator)
        + sum(
            2 * len(factor.conjugator)
            + 1
            + 2 * int(factor.exponent == -1)
            for factor in certificate.factors
        )
    )


def commutator_wrap_certificate(
    relators: tuple[str, ...], target_index: int, other_index: int
) -> ACMCertificate:
    """Return the universal ``u -> u v u^-1 v^-1 u`` ACM certificate."""

    if target_index == other_index:
        raise ValueError("the wrapped relators must be distinct")
    if not 0 <= target_index < len(relators) or not 0 <= other_index < len(
        relators
    ):
        raise ValueError("wrapped relator index out of range")
    return ACMCertificate(
        target_index=target_index,
        factors=(
            NormalFactor(other_index, 1),
            NormalFactor(
                other_index,
                -1,
                relators[target_index],
            ),
        ),
    )


def bounded_acm_successors(
    relators: tuple[str, ...],
    *,
    target_index: int,
    max_width: int,
    max_conjugator_length: int,
    beam_size: int | None = 256,
    relator_cap: int | None = None,
    generators: tuple[str, ...] | None = None,
) -> tuple[ACMSuccessor, ...]:
    """Generate a finite witnessed-ACM action family.

    ``beam_size=None`` exhausts normalized certificates with the stated width
    and factor-conjugator bounds, modulo target conjugacy and relator inversion.
    The source conjugator is normalized to the empty word; over increasing
    factor-conjugator bounds this loses no target conjugacy classes. Exhaustive
    mode is exponential in width.
    Otherwise, the shortest cyclic target representatives survive at each
    width. Every returned action remains independently sound under pruning
    because it carries its full normal-factor certificate.
    """

    if len(relators) < 2:
        raise ValueError("an ACM move requires at least two relators")
    if not 0 <= target_index < len(relators):
        raise ValueError("target index out of range")
    if (
        max_width < 1
        or max_conjugator_length < 0
        or (beam_size is not None and beam_size < 1)
    ):
        raise ValueError("invalid finite-action bounds")
    for relator in relators:
        free_reduce(relator)

    used_generators = {letter.lower() for word in relators for letter in word}
    if generators is None:
        generator_list = sorted(used_generators)
    else:
        generator_list = list(generators)
        if (
            any(len(generator) != 1 or not generator.islower() for generator in generator_list)
            or len(set(generator_list)) != len(generator_list)
            or not used_generators.issubset(generator_list)
        ):
            raise ValueError("generators must be distinct lowercase letters covering the relators")
    conjugators = tuple(
        _reduced_words(generator_list, max_conjugator_length)
    )
    factor_choices = tuple(
        NormalFactor(index, exponent, conjugator)
        for index in range(len(relators))
        if index != target_index
        for exponent in (1, -1)
        for conjugator in conjugators
    )

    if beam_size is None:
        return _exhaustive_successors(
            relators,
            target_index,
            max_width,
            factor_choices,
            relator_cap,
        )

    frontier: list[ACMCertificate] = [
        ACMCertificate(target_index, source_exponent=exponent)
        for exponent in (1, -1)
    ]
    best_by_key: dict[str, ACMSuccessor] = {}
    source_key = cyclic_key(relators[target_index])
    for _width in range(1, max_width + 1):
        layer: dict[str, ACMSuccessor] = {}
        for prefix in frontier:
            for factor in factor_choices:
                certificate = ACMCertificate(
                    target_index=target_index,
                    source_exponent=prefix.source_exponent,
                    factors=prefix.factors + (factor,),
                )
                target = certified_target_word(relators, certificate)
                if relator_cap is not None and len(target) > relator_cap:
                    continue
                key = cyclic_key(target)
                if key == source_key:
                    continue
                successor = ACMSuccessor(
                    relators=apply_certified_acm(relators, certificate),
                    certificate=certificate,
                    atomic_bound=len(expand_atomic_moves(relators, certificate)),
                )
                previous = layer.get(key)
                if previous is None or _successor_score(
                    successor
                ) < _successor_score(previous):
                    layer[key] = successor
        ranked = sorted(layer.values(), key=_successor_score)
        if beam_size is not None:
            ranked = ranked[:beam_size]
        frontier = [successor.certificate for successor in ranked]
        for successor in ranked:
            key = cyclic_key(successor.relators[target_index])
            previous = best_by_key.get(key)
            if previous is None or _successor_score(
                successor
            ) < _successor_score(previous):
                best_by_key[key] = successor
        if not frontier:
            break
    return tuple(sorted(best_by_key.values(), key=_successor_score))


def _exhaustive_successors(
    relators: tuple[str, ...],
    target_index: int,
    max_width: int,
    factor_choices: tuple[NormalFactor, ...],
    relator_cap: int | None,
) -> tuple[ACMSuccessor, ...]:
    best_by_key: dict[str, ACMSuccessor] = {}
    source_key = cyclic_key(relators[target_index])
    for width in range(1, max_width + 1):
        for source_exponent in (1, -1):
            for factors in product(factor_choices, repeat=width):
                certificate = ACMCertificate(
                    target_index=target_index,
                    source_exponent=source_exponent,
                    factors=factors,
                )
                target = certified_target_word(relators, certificate)
                if relator_cap is not None and len(target) > relator_cap:
                    continue
                key = cyclic_key(target)
                if key == source_key:
                    continue
                successor = ACMSuccessor(
                    relators=apply_certified_acm(relators, certificate),
                    certificate=certificate,
                    atomic_bound=atomic_move_bound(certificate),
                )
                previous = best_by_key.get(key)
                if previous is None or _successor_score(
                    successor
                ) < _successor_score(previous):
                    best_by_key[key] = successor
    return tuple(sorted(best_by_key.values(), key=_successor_score))


def _successor_score(successor: ACMSuccessor) -> tuple[int, int, tuple[str, ...]]:
    return (
        sum(len(word) for word in successor.relators),
        successor.atomic_bound,
        successor.relators,
    )


def _validate_certificate(
    relators: tuple[str, ...], certificate: ACMCertificate
) -> None:
    if not 0 <= certificate.target_index < len(relators):
        raise ValueError("certificate target index out of range")
    for relator in relators:
        free_reduce(relator)
    for factor in certificate.factors:
        if not 0 <= factor.relator_index < len(relators):
            raise ValueError("factor relator index out of range")
        if factor.relator_index == certificate.target_index:
            raise ValueError("normal factors must use the other relators")


def _reduced_words(
    generators: list[str], maximum_length: int
):
    yield ""
    alphabet = tuple(
        letter
        for generator in generators
        for letter in (generator, generator.upper())
    )
    for length in range(1, maximum_length + 1):
        for letters in product(alphabet, repeat=length):
            if any(
                letters[index] == letters[index + 1].swapcase()
                for index in range(length - 1)
            ):
                continue
            yield "".join(letters)
