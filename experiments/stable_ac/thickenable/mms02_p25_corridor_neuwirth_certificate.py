"""Exact Neuwirth decisions along the published P25-to-AK(3) corridor."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass

from experiments.stable_ac.thickenable.mms02_len25_neuwirth_certificate import (
    PUBLISHED_WORDS,
)
from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
    solve_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    RankDecision,
    solve_spherical,
)


AK3_WORDS = ("xxxYYYY", "xyxYXY")
PUBLISHED_H_MOVES = (
    9, 7, 4, 8, 11, 5, 11, 9, 3, 10, 12, 7, 7, 9, 11, 5, 3, 5,
    4, 3, 12, 5, 7, 7, 1, 9, 11, 8, 3, 5, 10, 2, 6, 12, 9, 7,
    5, 11, 10, 3, 8, 11, 9, 2, 10, 12, 5, 7, 9, 11, 1, 9, 8,
)
PUBLISHED_PATH_SHA256 = (
    "ee5fd9d8a38155d5774aca7f6bbc11ec55e00f1987209a69750977ffad7b23e8"
)


@dataclass(frozen=True)
class CorridorNeuwirthDecision:
    moves: tuple[int, ...]
    states: tuple[tuple[str, str], ...]
    path_sha256: str
    decisions: tuple[RankDecision, ...]
    support_histogram: tuple[tuple[str, int], ...]
    length_histogram: tuple[tuple[int, int], ...]
    total_scheme_budget: int
    total_phase_pair_budget: int
    total_component_seed_budget: int
    total_closed_component_assignments: int
    total_component_combination_budget: int
    total_component_combinations_considered: int
    verdict: str


def _inverse(word: str) -> str:
    return word[::-1].swapcase()


def _free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def _apply_h(state: tuple[str, str], move: int) -> tuple[str, str]:
    first, second = state
    if move == 1:
        second += first
    elif move == 2:
        first += _inverse(second)
    elif move == 3:
        second += _inverse(first)
    elif move == 4:
        first += second
    elif move == 5:
        second = "X" + second + "x"
    elif move == 6:
        first = "Y" + first + "y"
    elif move == 7:
        second = "Y" + second + "y"
    elif move == 8:
        first = "x" + first + "X"
    elif move == 9:
        second = "x" + second + "X"
    elif move == 10:
        first = "y" + first + "Y"
    elif move == 11:
        second = "y" + second + "Y"
    elif move == 12:
        first = "X" + first + "x"
    else:
        raise ValueError(f"unknown Appendix F move h{move}")
    return _free_reduce(first), _free_reduce(second)


def replay_published_corridor() -> tuple[tuple[str, str], ...]:
    states = [PUBLISHED_WORDS]
    for move in PUBLISHED_H_MOVES:
        states.append(_apply_h(states[-1], move))
    path = tuple(states)
    if len(path) != 54 or path[-1] != AK3_WORDS:
        raise AssertionError("the Appendix F path did not reach literal AK(3)")
    if len(set(path)) != len(path):
        raise AssertionError("the published corridor unexpectedly repeats a state")
    payload = json.dumps(
        path,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    if hashlib.sha256(payload).hexdigest() != PUBLISHED_PATH_SHA256:
        raise AssertionError("the published corridor trace drifted")
    return path


def decide_published_corridor_neuwirth() -> CorridorNeuwirthDecision:
    states = replay_published_corridor()
    decisions = []
    for state in states:
        decision = solve_spherical(state)
        if decision.spherical is None:
            decision = solve_one_loop_spherical(state)
        decisions.append(decision)
    decisions = tuple(decisions)
    if any(
        decision.support.kind not in {"K4", "K4-e", "K4+1loop"}
        for decision in decisions
    ):
        raise AssertionError("a corridor state left the proved support classes")
    if any(decision.spherical is not False for decision in decisions):
        raise AssertionError("a corridor state was not certified non-spherical")
    if any(not decision.counters.exhaustive for decision in decisions):
        raise AssertionError("a corridor negative has an incomplete budget")

    support_histogram = Counter(
        decision.support.kind for decision in decisions
    )
    length_histogram = Counter(sum(map(len, state)) for state in states)
    return CorridorNeuwirthDecision(
        moves=PUBLISHED_H_MOVES,
        states=states,
        path_sha256=PUBLISHED_PATH_SHA256,
        decisions=decisions,
        support_histogram=tuple(sorted(support_histogram.items())),
        length_histogram=tuple(sorted(length_histogram.items())),
        total_scheme_budget=sum(
            decision.counters.scheme_budget for decision in decisions
        ),
        total_phase_pair_budget=sum(
            decision.counters.phase_pair_budget for decision in decisions
        ),
        total_component_seed_budget=sum(
            decision.counters.component_seed_budget for decision in decisions
        ),
        total_closed_component_assignments=sum(
            decision.counters.closed_component_assignments
            for decision in decisions
        ),
        total_component_combination_budget=sum(
            decision.counters.component_combination_budget
            for decision in decisions
        ),
        total_component_combinations_considered=sum(
            decision.counters.component_combinations_considered
            for decision in decisions
        ),
        verdict="ALL_54_EXACT_COMPLEXES_NOT_SPHERICAL",
    )
