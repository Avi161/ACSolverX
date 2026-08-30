from experiments.equivalence_classes.lib.autcanon import (
    aut_canon,
    aut_min_len,
    check,
)
from experiments.equivalence_classes.lib.words import (
    apply_hom as independent_apply_hom,
    free_reduce as independent_free_reduce,
    inv as independent_inverse,
)

from experiments.stable_ac.mms02_terminal_hnn_certificate import (
    AUTOMORPHISMS,
    C,
    D0,
    ORIGINAL_WORDS,
    TRANSFORMED_WORDS,
    W,
    decide_terminal_hnn_shortcut,
    transformed_words,
)


EXPECTED_ORIGINAL_WORDS = {
    "A": "xzYXyxZXYxyZ",
    "B": "XyxZXYXyxzXYxy",
    "u": "zYX",
    "v": "Xyz",
}
EXPECTED_AUTOMORPHISMS = (
    {"x": "x", "y": "y", "z": "zy"},
    {"x": "x", "y": "xyX", "z": "z"},
    {"x": "x", "y": "Zy", "z": "z"},
)
EXPECTED_TRANSFORMED_WORDS = {
    "A": "xyxYzXZY",
    "B": "ZyxYzXZYzXZyzxZyXYzxZyX",
    "u": "zX",
    "v": "ZyXzxZyX",
}


def test_terminal_hnn_words_and_four_pinches_are_literal():
    assert ORIGINAL_WORDS == EXPECTED_ORIGINAL_WORDS
    assert AUTOMORPHISMS == EXPECTED_AUTOMORPHISMS
    assert TRANSFORMED_WORDS == EXPECTED_TRANSFORMED_WORDS
    independent = {}
    for name, original in EXPECTED_ORIGINAL_WORDS.items():
        image = original
        for automorphism in EXPECTED_AUTOMORPHISMS:
            image = independent_apply_hom(image, automorphism)
        independent[name] = image
    assert independent == EXPECTED_TRANSFORMED_WORDS == transformed_words()

    assert TRANSFORMED_WORDS["B"] == (
        "Z" + "yxY" + "zXZ" + "Y" + "zXZ" + "y"
        + "zxZ" + "yXY" + "zxZ" + "yX"
    )
    assert independent_free_reduce(
        "yxY" + independent_inverse(W) + "Y" + independent_inverse(W) + "y"
        + W + "yXY" + W + "yX"
    ) == D0
    assert independent_free_reduce("yX" + W + "yX") == C
    assert independent_free_reduce(
        "X" + independent_inverse(EXPECTED_TRANSFORMED_WORDS["u"]) + "x"
    ) == "Zx"


def test_terminal_hnn_tail_floors_match_independent_whitehead_engine():
    decision = decide_terminal_hnn_shortcut()
    source_total, source_rep, source_phi = aut_canon(("x", D0))
    target_total, target_rep, target_phi = aut_canon((C, D0))

    assert decision.normalized_source == ("Zx", "Z" + D0)
    assert decision.normalized_target == ("Z" + C, "Z" + D0)
    assert decision.source_tail_minimum == ("X", "XYXyxYxyy")
    assert decision.target_tail_minimum == (
        "XXYYXyxxy",
        "XYxyy",
    )
    assert decision.source_descent == (("x", "xy"),)
    assert decision.target_descent == (("xy", "y"),)
    assert (decision.source_floor, decision.target_floor) == (10, 14)
    assert aut_min_len(("x", D0)) == source_total == 10
    assert aut_min_len((C, D0)) == target_total == 14
    assert check(("x", D0), source_rep, source_phi)
    assert check((C, D0), target_rep, target_phi)
    assert decision.whitehead_map_count == 12
    assert decision.verdict == "NO_SIMULTANEOUS_BASE_TAIL_AUTOMORPHISM"
