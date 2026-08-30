"""Exact endpoint cleanup of the terminal MMS02 rank-two gate."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.mms02_terminal_hnn_certificate import (
    C,
    D0,
    W,
    canonical_cyclic_word,
    free_reduce,
    inverse,
    whitehead_minimum,
)


EXPECTED_WORDS = {
    "R": "XyXYXyxYxyxYXyXYxyxYxyXYXy",
    "e_source": "YXyXYxyxYxx",
    "e_target": "YXyXYxyxYxyXYxy",
    "S": "xyXYXy",
    "T": "yXYxyxYXXy",
}
EXPECTED_MINIMA = {
    "S_singleton": ("XXyxy", "XXyxy"),
    "T_singleton": ("XXyyXYxyxY", "XXyyXYxyxY"),
    "source_pair": ("XXyXYXyxYxy", "XYXyxy"),
    "target_pair": ("XXYxyxYxy", "XXyyXYxyxY"),
}


@dataclass(frozen=True)
class TerminalBothRowCleanupDecision:
    source_pair: tuple[str, str]
    target_pair: tuple[str, str]
    cleaned_source_pair: tuple[str, str]
    cleaned_target_pair: tuple[str, str]
    source_donor_defect: str
    target_donor_defect: str
    source_singleton_minimum: tuple[str, str]
    target_singleton_minimum: tuple[str, str]
    source_pair_minimum: tuple[str, str]
    target_pair_minimum: tuple[str, str]
    singleton_floors: tuple[int, int]
    pair_floors: tuple[int, int]
    source_descent: tuple[tuple[str, str], ...]
    verdict: str


def decide_terminal_both_row_cleanup() -> TerminalBothRowCleanupDecision:
    rank_two_relator = free_reduce(D0 + "x" + inverse(D0) + inverse(W))
    source_row = free_reduce(inverse(D0) + "x")
    target_row = free_reduce(inverse(D0) + C)
    source_relator = free_reduce("x" + inverse(W))
    target_relator = free_reduce(C + "x" + inverse(C) + inverse(W))
    words = {
        "R": rank_two_relator,
        "e_source": source_row,
        "e_target": target_row,
        "S": source_relator,
        "T": target_relator,
    }
    if words != EXPECTED_WORDS:
        raise AssertionError("the endpoint cleanup words drifted")

    source_donor_defect = free_reduce(
        "x" + inverse(source_row) + "x" + source_row + "XX"
    )
    target_donor_defect = free_reduce(
        C
        + inverse(target_row)
        + "x"
        + target_row
        + "X"
        + inverse(C)
    )
    if source_donor_defect != free_reduce(rank_two_relator + inverse(source_relator)):
        raise AssertionError("the source donor cleanup identity drifted")
    if target_donor_defect != free_reduce(rank_two_relator + inverse(target_relator)):
        raise AssertionError("the target donor cleanup identity drifted")

    if canonical_cyclic_word(source_relator) != canonical_cyclic_word("yxyXYX"):
        raise AssertionError("the cleaned source row is not the braid relator")

    source_singleton_minimum, source_singleton_descent = whitehead_minimum(
        (source_relator, source_relator)
    )
    target_singleton_minimum, _ = whitehead_minimum(
        (target_relator, target_relator)
    )
    source_pair_minimum, _ = whitehead_minimum((source_relator, source_row))
    target_pair_minimum, _ = whitehead_minimum((target_relator, target_row))
    minima = {
        "S_singleton": source_singleton_minimum,
        "T_singleton": target_singleton_minimum,
        "source_pair": source_pair_minimum,
        "target_pair": target_pair_minimum,
    }
    if minima != EXPECTED_MINIMA:
        raise AssertionError("the endpoint cleanup Whitehead minima drifted")

    singleton_floors = (
        sum(map(len, source_singleton_minimum)) // 2,
        sum(map(len, target_singleton_minimum)) // 2,
    )
    pair_floors = (
        sum(map(len, source_pair_minimum)),
        sum(map(len, target_pair_minimum)),
    )
    if singleton_floors != (5, 10) or pair_floors != (17, 19):
        raise AssertionError("the endpoint cleanup floors drifted")

    return TerminalBothRowCleanupDecision(
        source_pair=(rank_two_relator, source_row),
        target_pair=(rank_two_relator, target_row),
        cleaned_source_pair=(source_relator, source_row),
        cleaned_target_pair=(target_relator, target_row),
        source_donor_defect=source_donor_defect,
        target_donor_defect=target_donor_defect,
        source_singleton_minimum=source_singleton_minimum,
        target_singleton_minimum=target_singleton_minimum,
        source_pair_minimum=source_pair_minimum,
        target_pair_minimum=target_pair_minimum,
        singleton_floors=singleton_floors,
        pair_floors=pair_floors,
        source_descent=source_singleton_descent,
        verdict="NO_CLEAN_THEN_AMBIENT_TRANSPORT",
    )


if __name__ == "__main__":
    print(decide_terminal_both_row_cleanup())
