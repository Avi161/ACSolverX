from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
    recoveries_up_to,
)


R = "xxxTTTT"
D = "TzxZ"


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def substitute_z(word: str, expression: str) -> str:
    pieces = []
    for letter in word:
        if letter == "z":
            pieces.append(expression)
        elif letter == "Z":
            pieces.append(inv(expression))
        else:
            pieces.append(letter)
    return free_reduce("".join(pieces))


ISOLATOR_GAUGES = (
    "",
    conjugate(R, "xT"),
    free_reduce(
        conjugate(inv(R), "ttX")
        + conjugate(R, "Xtx")
    ),
)

SURVIVOR_GAUGES = (
    "",
    conjugate(R, "zX"),
    free_reduce(
        conjugate(inv(R), "TzX")
        + conjugate(R, "xZt")
    ),
)


def test_post_catalyst_r_gauges_preserve_both_target_role_endpoints():
    recoveries = recoveries_up_to(9)
    assert len(recoveries) == 61

    for recovery in recoveries:
        w = free_reduce("x" + recovery)
        expressions = (
            free_reduce("T" + w + "x"),
            free_reduce("t" + w + "X"),
        )
        survivors = (
            D,
            free_reduce("Z" + w),
        )

        for baseline_expression in expressions:
            for baseline_survivor in survivors:
                baseline_endpoint = substitute_z(
                    baseline_survivor,
                    baseline_expression,
                )

                for isolator_gauge in ISOLATOR_GAUGES:
                    expression = free_reduce(
                        baseline_expression + isolator_gauge
                    )
                    assert normal_form(
                        free_reduce(
                            inv(baseline_expression) + expression
                        )
                    ) == (0, ())

                    for survivor_gauge in SURVIVOR_GAUGES:
                        survivor = free_reduce(
                            baseline_survivor + survivor_gauge
                        )
                        endpoint = substitute_z(survivor, expression)
                        assert normal_form(
                            free_reduce(inv(baseline_endpoint) + endpoint)
                        ) == (0, ())
