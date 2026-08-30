from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.equivalence_classes.lib.words import canon_rel, free_reduce, inv
from experiments.stable_ac.mms02_terminal_both_row_cleanup_certificate import (
    EXPECTED_MINIMA,
    EXPECTED_WORDS,
    decide_terminal_both_row_cleanup,
)


def test_terminal_both_row_donor_cleanup_is_literal():
    rank_two_relator = EXPECTED_WORDS["R"]
    source_row = EXPECTED_WORDS["e_source"]
    target_row = EXPECTED_WORDS["e_target"]
    source_relator = EXPECTED_WORDS["S"]
    target_relator = EXPECTED_WORDS["T"]

    source_defect = free_reduce(rank_two_relator + inv(source_relator))
    target_defect = free_reduce(rank_two_relator + inv(target_relator))
    assert source_defect == free_reduce(
        "x" + inv(source_row) + "x" + source_row + "XX"
    )
    assert target_defect == free_reduce(
        "yXYxy"
        + inv(target_row)
        + "x"
        + target_row
        + "X"
        + inv("yXYxy")
    )
    assert canon_rel(source_relator) == canon_rel("yxyXYX")


def test_terminal_both_row_floors_match_independent_autcanon():
    source_relator = EXPECTED_WORDS["S"]
    target_relator = EXPECTED_WORDS["T"]
    source_pair = (source_relator, EXPECTED_WORDS["e_source"])
    target_pair = (target_relator, EXPECTED_WORDS["e_target"])

    source_singleton = aut_canon((source_relator, source_relator))
    target_singleton = aut_canon((target_relator, target_relator))
    source = aut_canon(source_pair)
    target = aut_canon(target_pair)

    assert source_singleton[0] // 2 == 5
    assert target_singleton[0] // 2 == 10
    assert source[0] == 17
    assert target[0] == 19
    assert source_singleton[1] != target_singleton[1]
    assert source[1] != target[1]
    assert check((source_relator, source_relator), source_singleton[1], source_singleton[2])
    assert check((target_relator, target_relator), target_singleton[1], target_singleton[2])
    assert check(source_pair, source[1], source[2])
    assert check(target_pair, target[1], target[2])

    decision = decide_terminal_both_row_cleanup()
    assert decision.source_singleton_minimum == EXPECTED_MINIMA["S_singleton"]
    assert decision.target_singleton_minimum == EXPECTED_MINIMA["T_singleton"]
    assert decision.source_pair_minimum == EXPECTED_MINIMA["source_pair"]
    assert decision.target_pair_minimum == EXPECTED_MINIMA["target_pair"]
    assert decision.verdict == "NO_CLEAN_THEN_AMBIENT_TRANSPORT"
