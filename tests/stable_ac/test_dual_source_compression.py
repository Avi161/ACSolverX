from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.rank3_compression.two_stabilization import (
    cyclic_orientations,
    free_reduce,
    solve_isolator,
    substitute_generator,
    substitute_new,
)


def test_exact_dual_source_ak3_corridor():
    power = "xxxYYYY"
    braid = "xyxYXY"
    word_z = "X"
    word_t = "Xy"
    template_power = "TZxYYY"
    template_braid = "TZtxYX"

    assert substitute_new(template_power, word_z, word_t) in (
        cyclic_orientations(power)
    )
    assert substitute_new(template_braid, word_z, word_t) in (
        cyclic_orientations(braid)
    )

    expression_y = solve_isolator(template_braid, "y")
    assert expression_y == "XTZtx"
    isolator_x = substitute_generator(
        template_power,
        "y",
        expression_y,
    )
    assert isolator_x == "TZTzzztx"
    expression_x = solve_isolator(isolator_x, "x")
    assert expression_x == "TZZZtzt"

    defining_z = free_reduce("Z" + word_z)
    defining_t = free_reduce("T" + word_t)
    output = tuple(
        substitute_generator(
            substitute_generator(word, "y", expression_y),
            "x",
            expression_x,
        )
        for word in (defining_z, defining_t)
    )
    assert output == ("ZTZTzzzt", "TTZTzzTZtzt")

    relabeled = tuple(
        word.translate(str.maketrans("zZtT", "xXyY"))
        for word in output
    )
    minimum_total, representative, _ = aut_canon(relabeled)
    assert minimum_total == 16
    assert representative == ("YYXXXyx", "YYXXXYxyX")
