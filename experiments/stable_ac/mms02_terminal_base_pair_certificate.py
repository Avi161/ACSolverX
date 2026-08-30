"""Exact stable base-pair reduction for the terminal MMS02 target."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.mms02_terminal_hnn_certificate import (
    whitehead_minimum,
)
from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    apply_images,
    decide_target_hnn,
    free_reduce,
    inverse,
)
from experiments.stable_ac.mms02_terminal_twisted_coboundary_certificate import (
    P_WORD,
    Q_WORD,
)

PHI_Q = "pqPq"
R1 = "xpXQ"
R2 = "xqX" + inverse(PHI_Q)
R3 = P_WORD + "x"
TARGET_T_PRIME = "qXQxqxQXXqx"
TARGET_E_PRIME = "XQXqXQxqxQxqXQxqx"
EXPECTED_T_REWRITE = (
    "qXQxqxQXXqx",
    "qPqxQXXqx",
    "qPqxQXp",
)
EXPECTED_E_REWRITE = (
    "xxQXqXQxqxQxqXQxqXX",
    "xxQXqXQxqxQxqXQpqPqX",
    "xxQXqXQxqxQpqqPqX",
    "xxQXqXQxpQPqpqPqpqqPq",
    "xQpQPqXQxpQPqpqPqpqqPq",
    "QpQQPQpqPxpQPqpqPqpqqPq",
    P_WORD + "x",
)

EXPECTED_U = "QpQQPQpQPQQpQQPQQpQPqqpqqPqpQpQQPQQpqPqqpqqPqqpqPqpqqP"
EXPECTED_V = "QpQQPQpQPQQpQQPQQpQPqqpqqPqpQQPQQpqPqqpqqPqqpqPqpqP"
EXPECTED_MINIMUM = (
    "PPQpQQPQQpqPqqpqqPqqpqPqpqqPqpQQPQpQPQQpQQPQQpQPqqpqq",
    "PQQpQPqqpqqPQpQQPQQpqPqqpqqPqqpqPqpqqPqpQPQpQPQQpQQ",
)
EXPECTED_D = "QpQQPQpQPQQpQQPQQpQPqqpqPPqpqPqpqqPq"
EXPECTED_D_MINIMUM = "PPQpQQPQQpQPqqpq"


def to_xy(word: str) -> str:
    return word.translate(str.maketrans({"p": "x", "P": "X", "q": "y", "Q": "Y"}))


def from_xy(word: str) -> str:
    return word.translate(str.maketrans({"x": "p", "X": "P", "y": "q", "Y": "Q"}))


def phi(word: str) -> str:
    return apply_images(word, {"p": "q", "q": PHI_Q})


def theta(word: str) -> str:
    return free_reduce(inverse(P_WORD) + word + P_WORD + inverse(phi(word)))


def replay_hnn_rows() -> tuple[tuple[str, ...], tuple[str, ...]]:
    target = decide_target_hnn()
    rename = {"x": "x", "y": "q"}
    if apply_images(target.transformed_relator, rename) != TARGET_T_PRIME:
        raise AssertionError("the renamed target relator drifted")
    if apply_images(target.transformed_row, rename) != TARGET_E_PRIME:
        raise AssertionError("the renamed target killer drifted")

    t_words = [TARGET_T_PRIME]
    position = t_words[-1].find("XQx")
    t_words.append(free_reduce(t_words[-1][:position] + "P" + t_words[-1][position + 3 :]))
    position = t_words[-1].rfind("Xqx")
    t_words.append(free_reduce(t_words[-1][:position] + "p" + t_words[-1][position + 3 :]))
    if tuple(t_words) != EXPECTED_T_REWRITE:
        raise AssertionError("the defining-row target rewrite drifted")
    if t_words[-1] != free_reduce("P" + inverse(R2) + "p"):
        raise AssertionError("the target relator did not become a conjugate of R2 inverse")

    e_words = [free_reduce("xxx" + TARGET_E_PRIME + "XXX")]
    for base in ("q", "q", "QpqqPq", "Q", "QpQPq"):
        pattern = "x" + base + "X"
        position = e_words[-1].rfind(pattern)
        if position < 0:
            raise AssertionError("the pinned HNN pinch disappeared")
        e_words.append(
            free_reduce(
                e_words[-1][:position]
                + phi(base)
                + e_words[-1][position + len(pattern) :]
            )
        )
    if e_words[-1].count("x") != 1 or "X" in e_words[-1]:
        raise AssertionError("the target killer did not reach one stable letter")
    left, right = e_words[-1].split("x")
    e_words.append(free_reduce(left + phi(right) + "x"))
    if tuple(e_words) != EXPECTED_E_REWRITE:
        raise AssertionError("the target killer HNN rewrite drifted")
    return tuple(t_words), tuple(e_words)


@dataclass(frozen=True)
class TerminalBasePairDecision:
    target_rewrite: tuple[str, ...]
    killer_rewrite: tuple[str, ...]
    expanded_rows: tuple[str, str, str]
    ambient_images: tuple[str, str, str]
    base_pair: tuple[str, str]
    base_lengths: tuple[int, int]
    base_minimum: tuple[str, str]
    base_floor: int
    base_descent: tuple[tuple[str, str], ...]
    consequence: str
    consequence_minimum: str
    consequence_floor: int
    verdict: str


def decide_terminal_base_pair() -> TerminalBasePairDecision:
    target_rewrite, killer_rewrite = replay_hnn_rows()
    ambient = {"p": "p", "q": "q", "x": inverse(P_WORD) + "x"}
    delete_x = {"p": "p", "q": "q", "x": ""}
    transformed = tuple(apply_images(row, ambient) for row in (R1, R2, R3))
    if transformed[2] != "x":
        raise AssertionError("the terminal killer did not become the stable letter")
    base_pair = tuple(apply_images(row, delete_x) for row in transformed[:2])
    if base_pair != (EXPECTED_U, EXPECTED_V):
        raise AssertionError("the terminal stable base pair drifted")

    xy_pair = tuple(to_xy(word) for word in base_pair)
    minimum_xy, descent = whitehead_minimum(xy_pair)
    minimum = tuple(from_xy(word) for word in minimum_xy)
    floor = sum(map(len, minimum))
    if minimum != EXPECTED_MINIMUM or floor != 104:
        raise AssertionError("the terminal base-pair Whitehead floor drifted")
    if aut_min_len(xy_pair) != floor:
        raise AssertionError("the independent base-pair floor disagrees")

    consequence = free_reduce(inverse(P_WORD) + Q_WORD)
    if consequence != EXPECTED_D:
        raise AssertionError("the terminal consequence word drifted")
    if theta(Q_WORD) != consequence:
        raise AssertionError("the terminal cocycle consequence drifted")
    duplicate = (to_xy(consequence), to_xy(consequence))
    consequence_minimum_xy, _ = whitehead_minimum(duplicate)
    consequence_minimum = from_xy(consequence_minimum_xy[0])
    consequence_floor = len(consequence_minimum)
    if consequence_minimum != EXPECTED_D_MINIMUM or consequence_floor != 16:
        raise AssertionError("the consequence primitivity floor drifted")
    if aut_min_len(duplicate) != 2 * consequence_floor:
        raise AssertionError("the independent consequence floor disagrees")

    return TerminalBasePairDecision(
        target_rewrite=target_rewrite,
        killer_rewrite=killer_rewrite,
        expanded_rows=(R1, R2, R3),
        ambient_images=(ambient["p"], ambient["q"], ambient["x"]),
        base_pair=base_pair,
        base_lengths=tuple(map(len, base_pair)),
        base_minimum=minimum,
        base_floor=floor,
        base_descent=descent,
        consequence=consequence,
        consequence_minimum=consequence_minimum,
        consequence_floor=consequence_floor,
        verdict="TARGET_STABLE_BASE_PAIR_FLOOR_104",
    )


if __name__ == "__main__":
    print(decide_terminal_base_pair())
