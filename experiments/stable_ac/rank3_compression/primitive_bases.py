"""Replayable Nielsen basis balls and signed corridor quotient classes."""

from dataclasses import dataclass
from itertools import product

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.stable_ac.rank3_compression.corridors import (
    free_reduce,
    inverse,
)


WORD_ALPHABET = "xXyY"


@dataclass(frozen=True)
class NielsenMove:
    target: int
    side: str
    sign: int

    def to_json(self) -> dict[str, object]:
        return {
            "target": self.target,
            "side": self.side,
            "sign": self.sign,
        }

    @classmethod
    def from_json(cls, data: dict[str, object]) -> "NielsenMove":
        return cls(
            target=int(data["target"]),
            side=str(data["side"]),
            sign=int(data["sign"]),
        )


@dataclass(frozen=True)
class BasisRecord:
    basis: tuple[str, str]
    moves: tuple[NielsenMove, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "basis": list(self.basis),
            "moves": [move.to_json() for move in self.moves],
        }


@dataclass(frozen=True)
class BasisMember:
    record: BasisRecord
    transformed_pair: tuple[str, str]

    def to_json(self, class_key: tuple[str, str]) -> dict[str, object]:
        data = self.record.to_json()
        data["transformed_pair"] = list(self.transformed_pair)
        data["class_key"] = list(class_key)
        return data


@dataclass(frozen=True)
class BasisClass:
    key: tuple[str, str]
    members: tuple[BasisMember, ...]


def apply_nielsen(
    pair: tuple[str, str],
    move: NielsenMove,
) -> tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("Nielsen moves require an ordered pair")
    _validate_rank_two_words(pair)
    if move.target not in (0, 1):
        raise ValueError(f"target must be 0 or 1: {move.target!r}")
    if move.side not in ("left", "right"):
        raise ValueError(f"side must be left or right: {move.side!r}")
    if move.sign not in (-1, 1):
        raise ValueError(f"sign must be -1 or 1: {move.sign!r}")
    current = tuple(free_reduce(word) for word in pair)
    other_index = 1 - move.target
    other = current[other_index]
    if move.sign == -1:
        other = inverse(other)
    target_word = current[move.target]
    replaced = (
        free_reduce(target_word + other)
        if move.side == "right"
        else free_reduce(other + target_word)
    )
    child = list(current)
    child[move.target] = replaced
    return tuple(child)


def nielsen_reduce(
    pair: tuple[str, str],
) -> tuple[NielsenMove, ...] | None:
    if len(pair) != 2:
        raise ValueError("Nielsen reduction requires an ordered pair")
    _validate_rank_two_words(pair)
    current = tuple(free_reduce(word) for word in pair)
    moves: list[NielsenMove] = []
    while not _is_signed_standard(current):
        current_total = sum(len(word) for word in current)
        candidates: list[
            tuple[int, tuple[str, str], int, str, int, NielsenMove]
        ] = []
        for target in (0, 1):
            for side in ("right", "left"):
                for sign in (1, -1):
                    move = NielsenMove(target, side, sign)
                    child = apply_nielsen(current, move)
                    child_total = sum(len(word) for word in child)
                    if child_total >= current_total:
                        continue
                    candidates.append(
                        (
                            child_total,
                            child,
                            target,
                            side,
                            sign,
                            move,
                        )
                    )
        if not candidates:
            return None
        _, current, _, _, _, move = min(candidates)
        moves.append(move)
    return tuple(moves)


def replay_nielsen(
    pair: tuple[str, str],
    moves: tuple[NielsenMove, ...],
) -> tuple[str, str]:
    _validate_rank_two_words(pair)
    current = tuple(free_reduce(word) for word in pair)
    for move in moves:
        current = apply_nielsen(current, move)
    return current


def enumerate_bases(max_total: int = 4) -> tuple[BasisRecord, ...]:
    if max_total < 2:
        raise ValueError("max_total must be at least two")
    words = tuple(_reduced_words(max_total - 1))
    records: list[BasisRecord] = []
    for left in words:
        for right in words:
            if len(left) + len(right) > max_total:
                continue
            basis = (left, right)
            moves = nielsen_reduce(basis)
            if moves is not None:
                records.append(BasisRecord(basis=basis, moves=moves))
    return tuple(records)


def apply_basis(
    pair: tuple[str, str],
    basis: tuple[str, str],
) -> tuple[str, str]:
    if len(pair) != 2 or len(basis) != 2:
        raise ValueError("basis application requires two relators and two images")
    _validate_rank_two_words(basis)
    left, right = (free_reduce(word) for word in basis)
    images = {
        "x": left,
        "X": inverse(left),
        "y": right,
        "Y": inverse(right),
    }
    outputs: list[str] = []
    for relator in pair:
        if any(letter not in WORD_ALPHABET for letter in relator):
            raise ValueError("relators must use only x and y")
        outputs.append(free_reduce("".join(images[letter] for letter in relator)))
    return tuple(outputs)


def signed_pair_key(pair: tuple[str, str]) -> tuple[str, str]:
    return min(canon(*apply_basis(pair, basis)) for basis in _signed_bases())


def primitive_basis_classes(
    pair: tuple[str, str],
    max_total: int = 4,
) -> tuple[BasisClass, ...]:
    grouped: dict[tuple[str, str], list[BasisMember]] = {}
    for record in enumerate_bases(max_total):
        transformed = apply_basis(pair, record.basis)
        key = signed_pair_key(transformed)
        grouped.setdefault(key, []).append(
            BasisMember(record=record, transformed_pair=transformed)
        )
    return tuple(
        BasisClass(
            key=key,
            members=tuple(
                sorted(grouped[key], key=lambda member: member.record.basis)
            ),
        )
        for key in sorted(grouped)
    )


def _is_signed_standard(pair: tuple[str, str]) -> bool:
    return (
        len(pair[0]) == len(pair[1]) == 1
        and pair[0].lower() != pair[1].lower()
    )


def _validate_rank_two_words(words: tuple[str, str]) -> None:
    if any(letter not in WORD_ALPHABET for word in words for letter in word):
        raise ValueError("words must use only x and y")


def _reduced_words(maximum_length: int):
    for length in range(1, maximum_length + 1):
        for letters in product(WORD_ALPHABET, repeat=length):
            if any(
                letters[index] == letters[index + 1].swapcase()
                for index in range(length - 1)
            ):
                continue
            yield "".join(letters)


def _signed_bases() -> tuple[tuple[str, str], ...]:
    bases: list[tuple[str, str]] = []
    for swap in (False, True):
        for x_sign in (1, -1):
            for y_sign in (1, -1):
                left = "x" if x_sign == 1 else "X"
                right = "y" if y_sign == 1 else "Y"
                if swap:
                    left, right = right, left
                bases.append((left, right))
    return tuple(bases)
