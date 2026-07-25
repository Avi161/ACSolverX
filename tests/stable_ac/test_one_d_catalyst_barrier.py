from experiments.equivalence_classes.lib.words import cyc_reduce, free_reduce, inv
from experiments.equivalence_classes.lib.autcanon import aut_min_len


B = "Zxt"
D = "TzxZ"
BRAID = "xtxTXT"


def rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def isolator_rotation(word: str) -> str:
    word = cyc_reduce(word)
    candidates = tuple(
        rotation
        for orientation in (word, inv(word))
        for rotation in rotations(orientation)
        if rotation.startswith("Z")
    )
    return min(candidates)


def substitute_z(word: str, expression: str) -> str:
    return free_reduce(
        "".join(
            expression
            if letter == "z"
            else inv(expression)
            if letter == "Z"
            else letter
            for letter in word
        )
    )


def test_complete_signed_rotation_residue_has_two_isolator_classes():
    witnesses = []
    for sign in (1, -1):
        source = D if sign == 1 else inv(D)
        for target_rotation in rotations(B):
            for source_rotation in rotations(source):
                product = cyc_reduce(target_rotation + source_rotation)
                if sum(letter in "zZ" for letter in product) == 1:
                    witnesses.append(
                        (
                            sign,
                            target_rotation,
                            source_rotation,
                            product,
                            isolator_rotation(product),
                        )
                    )

    assert 3 * (4 + 4) == 24
    assert witnesses == [
        (1, "Zxt", "xZTz", "xtxZT", "ZTxtx"),
        (1, "xtZ", "zxZT", "xtxZT", "ZTxtx"),
        (-1, "Zxt", "XZtz", "xtXZt", "ZtxtX"),
        (-1, "xtZ", "zXZt", "xtXZt", "ZtxtX"),
    ]


def test_both_isolators_return_the_surviving_relator_to_ak3():
    first_expression = "Txtx"
    first_survivor = substitute_z(D, first_expression)
    assert first_survivor == "TTxtxTXt"
    assert cyc_reduce(first_survivor) == "TxtxTX"
    assert free_reduce("T" + BRAID + "t") == "TxtxTX"

    second_expression = "txtX"
    second_survivor = substitute_z(D, second_expression)
    assert second_survivor == BRAID

    relabel = str.maketrans("tT", "yY")
    rank_two_power = "xxxTTTT".translate(relabel)
    assert aut_min_len((rank_two_power, first_survivor.translate(relabel))) == 13
    assert aut_min_len((rank_two_power, second_survivor.translate(relabel))) == 13
