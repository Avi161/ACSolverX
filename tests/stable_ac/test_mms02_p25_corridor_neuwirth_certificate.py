from collections import Counter

from experiments.stable_ac.thickenable.mms02_len25_neuwirth_certificate import (
    PUBLISHED_WORDS,
)
from experiments.stable_ac.thickenable.mms02_p25_corridor_neuwirth_certificate import (
    AK3_WORDS,
    PUBLISHED_H_MOVES,
    PUBLISHED_PATH_SHA256,
    decide_published_corridor_neuwirth,
    replay_published_corridor,
)


GERMS = {
    "x": (0, 1),
    "X": (1, 0),
    "y": (2, 3),
    "Y": (3, 2),
}
EXPECTED_H_MOVES = (
    9, 7, 4, 8, 11, 5, 11, 9, 3, 10, 12, 7, 7, 9, 11, 5, 3, 5,
    4, 3, 12, 5, 7, 7, 1, 9, 11, 8, 3, 5, 10, 2, 6, 12, 9, 7,
    5, 11, 10, 3, 8, 11, 9, 2, 10, 12, 5, 7, 9, 11, 1, 9, 8,
)


def _inverse(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def _reduce(pieces):
    stack = []
    for piece in pieces:
        for letter in piece:
            if stack and stack[-1].swapcase() == letter:
                stack.pop()
            else:
                stack.append(letter)
    return "".join(stack)


def _independent_h(state, move):
    first, second = state
    if move in (1, 3):
        donor = first if move == 1 else _inverse(first)
        return first, _reduce((second, donor))
    if move in (2, 4):
        donor = _inverse(second) if move == 2 else second
        return _reduce((first, donor)), second
    conjugations = {
        5: (1, "X"),
        6: (0, "Y"),
        7: (1, "Y"),
        8: (0, "x"),
        9: (1, "x"),
        10: (0, "y"),
        11: (1, "y"),
        12: (0, "X"),
    }
    target, conjugator = conjugations[move]
    rows = [first, second]
    rows[target] = _reduce(
        (conjugator, rows[target], conjugator.swapcase())
    )
    return tuple(rows)


def _independent_support_inventory(state):
    multiplicities = Counter()
    for word in state:
        for index, letter in enumerate(word):
            following = word[(index + 1) % len(word)]
            edge = tuple(
                sorted((GERMS[letter][1], GERMS[following][0]))
            )
            multiplicities[edge] += 1
    loops = {edge for edge in multiplicities if edge[0] == edge[1]}
    core = set(multiplicities) - loops
    adjacency = {vertex: set() for vertex in range(4)}
    for left, right in core:
        adjacency[left].add(right)
        adjacency[right].add(left)
    degrees = sorted(map(len, adjacency.values()))
    loop_edge_count = sum(multiplicities[edge] for edge in loops)
    if len(loops) == loop_edge_count == 1 and len(core) == 6:
        kind = "K4+1loop"
    elif not loops and len(core) == 6:
        kind = "K4"
    elif not loops and len(core) == 5 and degrees == [2, 2, 3, 3]:
        kind = "K4-e"
    else:
        kind = "UNSUPPORTED"
    return kind, loop_edge_count, tuple(sorted(multiplicities.items()))


def test_appendix_f_path_replays_every_literal_h_move():
    assert PUBLISHED_H_MOVES == EXPECTED_H_MOVES
    assert len(EXPECTED_H_MOVES) == 53
    states = replay_published_corridor()
    assert states[0] == PUBLISHED_WORDS
    assert states[-1] == AK3_WORDS
    assert len(states) == len(set(states)) == 54
    assert PUBLISHED_PATH_SHA256 == (
        "ee5fd9d8a38155d5774aca7f6bbc11ec55e00f1987209a69750977ffad7b23e8"
    )
    for before, move, after in zip(states, PUBLISHED_H_MOVES, states[1:]):
        assert _independent_h(before, move) == after


def test_every_appendix_f_corridor_complex_is_exactly_non_spherical():
    result = decide_published_corridor_neuwirth()
    assert result.verdict == "ALL_54_EXACT_COMPLEXES_NOT_SPHERICAL"
    assert len(result.decisions) == 54
    inventory = tuple(
        _independent_support_inventory(state) for state in result.states
    )
    independent_kinds = tuple(row[0] for row in inventory)
    assert Counter(independent_kinds) == {
        "K4": 37,
        "K4-e": 15,
        "K4+1loop": 2,
    }
    assert independent_kinds == tuple(
        decision.support.kind for decision in result.decisions
    )
    assert tuple(
        index for index, kind in enumerate(independent_kinds)
        if kind == "K4+1loop"
    ) == (23, 24)
    assert result.states[23] == ("YYYXyyyyx", "YXXyxyy")
    assert result.states[24] == ("YYYXyyyyx", "YYXXyxyyy")
    assert tuple(row[1] for row in inventory) == (
        *((0,) * 23),
        1,
        1,
        *((0,) * 29),
    )
    assert result.support_histogram == (
        ("K4", 37),
        ("K4+1loop", 2),
        ("K4-e", 15),
    )
    assert result.length_histogram == (
        (13, 3),
        (14, 3),
        (15, 14),
        (16, 16),
        (17, 6),
        (18, 4),
        (19, 5),
        (25, 3),
    )
    assert result.total_scheme_budget == 158
    assert result.total_phase_pair_budget == 10_701
    assert result.total_component_seed_budget == 66_823
    assert result.total_closed_component_assignments == 60
    assert result.total_component_combination_budget == 0
    assert result.total_component_combinations_considered == 0
    assert all(decision.spherical is False for decision in result.decisions)
    assert all(decision.witness is None for decision in result.decisions)
    assert all(decision.counters.exhaustive for decision in result.decisions)
