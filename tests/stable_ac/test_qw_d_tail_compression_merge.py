from __future__ import annotations

from collections.abc import Mapping, Sequence


INVERSE_LETTER = {
    "x": "X",
    "X": "x",
    "t": "T",
    "T": "t",
    "z": "Z",
    "Z": "z",
    "q": "Q",
    "Q": "q",
    "y": "Y",
    "Y": "y",
}
GENERATORS4 = ("x", "t", "z", "q")
GENERATORS3 = ("x", "t", "z")
GENERATORS2 = ("x", "y")

R = "xxxTTTT"
A = "qxxxQTTTT"
C = "qxQtq"
W = A + "Z" + C
D = "TzxZ"

WordMap = Mapping[str, str]


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE_LETTER[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inverse_word(word: str) -> str:
    return "".join(INVERSE_LETTER[letter] for letter in reversed(word))


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while (
        len(word) > 1
        and INVERSE_LETTER[word[0]] == word[-1]
    ):
        word = free_reduce(word[1:-1])
    return word


def canonical_relator(word: str) -> str:
    word = cyclic_reduce(word)
    if not word:
        return ""
    candidates: list[str] = []
    for orientation in (word, inverse_word(word)):
        candidates.extend(
            orientation[index:] + orientation[:index]
            for index in range(len(orientation))
        )
    return min(candidates)


def substitute(word: str, images: WordMap) -> str:
    result = ""
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse_word(image)
        result = free_reduce(result + image)
    return result


def compose(
    outer: WordMap,
    inner: WordMap,
    generators: Sequence[str],
) -> dict[str, str]:
    return {
        generator: substitute(inner[generator], outer)
        for generator in generators
    }


def word_map(
    generators: Sequence[str],
    *images: str,
) -> dict[str, str]:
    return dict(zip(generators, images, strict=True))


def identity_map(generators: Sequence[str]) -> dict[str, str]:
    return {generator: generator for generator in generators}


def assert_inverse_maps(
    images: WordMap,
    inverse: WordMap,
    generators: Sequence[str],
) -> None:
    identity = identity_map(generators)
    assert compose(inverse, images, generators) == identity
    assert compose(images, inverse, generators) == identity


def apply_maps(word: str, maps: Sequence[WordMap]) -> str:
    for images in maps:
        word = substitute(word, images)
    return word


def word_power(word: str, exponent: int) -> str:
    if exponent < 0:
        word = inverse_word(word)
        exponent = -exponent
    return free_reduce(word * exponent)


def second_kind_automorphisms(
    generators: Sequence[str],
) -> set[tuple[str, ...]]:
    signed = tuple(
        letter
        for generator in generators
        for letter in (generator, generator.upper())
    )
    identity = tuple(generators)
    maps: set[tuple[str, ...]] = set()
    for multiplier in signed:
        other_letters = tuple(
            letter
            for letter in signed
            if letter not in (
                multiplier,
                INVERSE_LETTER[multiplier],
            )
        )
        for mask in range(1 << len(other_letters)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(other_letters)
                if mask & (1 << index)
            )
            images: dict[str, str] = {}
            for generator in generators:
                if generator in (
                    multiplier,
                    INVERSE_LETTER[multiplier],
                ):
                    images[generator] = generator
                    continue
                positive = generator in subset
                negative = generator.upper() in subset
                if positive and not negative:
                    images[generator] = generator + multiplier
                elif negative and not positive:
                    images[generator] = (
                        INVERSE_LETTER[multiplier] + generator
                    )
                elif positive and negative:
                    images[generator] = (
                        INVERSE_LETTER[multiplier]
                        + generator
                        + multiplier
                    )
                else:
                    images[generator] = generator
            maps.add(tuple(images[generator] for generator in generators))
    maps.discard(identity)
    return maps


def assert_complete_minimum(
    word: str,
    steps: Sequence[WordMap],
    lengths: Sequence[int],
    terminal: str,
) -> None:
    whitehead_maps = second_kind_automorphisms(GENERATORS3)
    assert len(whitehead_maps) == 90
    current = canonical_relator(word)
    observed = [len(current)]
    for step in steps:
        assert tuple(
            step[generator] for generator in GENERATORS3
        ) in whitehead_maps
        current = canonical_relator(substitute(current, step))
        observed.append(len(current))
    assert tuple(observed) == tuple(lengths)
    assert current == canonical_relator(terminal)
    assert all(
        len(canonical_relator(substitute(current, word_map(
            GENERATORS3,
            *images,
        ))))
        >= len(current)
        for images in whitehead_maps
    )


def source(delta: int) -> str:
    d_power = D if delta == 1 else inverse_word(D)
    return free_reduce("q" + inverse_word(W) + d_power)


PLUS_BLOCKS = (
    word_map(GENERATORS4, "Qxq", "t", "zq", "q"),
    word_map(
        GENERATORS4,
        "TTTTxtttt",
        "t",
        "TTTTztttt",
        "TTTTq",
    ),
    word_map(GENERATORS4, "x", "Xt", "z", "qxxx"),
    word_map(
        GENERATORS4,
        "XttZxZxtXzTTx",
        "XttZx",
        "XttXzTTx",
        "XttZxZqXz",
    ),
)
PLUS_BLOCK_INVERSES = (
    word_map(GENERATORS4, "qxQ", "t", "zQ", "q"),
    word_map(
        GENERATORS4,
        "ttttxTTTT",
        "t",
        "ttttzTTTT",
        "ttttq",
    ),
    word_map(GENERATORS4, "x", "xt", "z", "qXXX"),
    word_map(
        GENERATORS4,
        "TzxzxZ",
        "Tzxt",
        "TzxzxZTzt",
        "TzxzxZTzqTZt",
    ),
)
PLUS_SOURCE_CONJUGATOR = (
    "ZxtXzTTxZxtXzTTxZxtXzTTxZxtXzTT"
)

MINUS_BLOCKS = (
    word_map(GENERATORS4, "Qxq", "Qtq", "zq", "q"),
    word_map(
        GENERATORS4,
        "x",
        "XXXtxxx",
        "zxxx",
        "XXXqxxx",
    ),
    word_map(
        GENERATORS4,
        "ZZxz",
        "ZZxZZxtXzzXzz",
        "Xzz",
        "ZZxZZxqx",
    ),
    word_map(
        GENERATORS4,
        "TTTTx",
        "t",
        "TTTTz",
        "TTTTq",
    ),
)
MINUS_BLOCK_INVERSES = (
    word_map(GENERATORS4, "qxQ", "qtQ", "zQ", "q"),
    word_map(
        GENERATORS4,
        "x",
        "xxxtXXX",
        "zXXX",
        "xxxqXXX",
    ),
    word_map(
        GENERATORS4,
        "zxzxZ",
        "zztZZ",
        "zx",
        "zzqzXZXZ",
    ),
    word_map(
        GENERATORS4,
        "ttttx",
        "t",
        "ttttz",
        "ttttq",
    ),
)
MINUS_SOURCE_CONJUGATOR = (
    "ZttttXzXzXzTTTTzXttttQTqTTTTxZttttZxZxZx"
)


def source_blocks(delta: int) -> tuple[WordMap, ...]:
    return PLUS_BLOCKS if delta == 1 else MINUS_BLOCKS


def first_deletion_survivors(delta: int) -> tuple[str, str, str]:
    kill_q = word_map(GENERATORS4, "x", "t", "z", "")
    return tuple(
        substitute(apply_maps(relator, source_blocks(delta)), kill_q)
        for relator in (A, W, D)
    )


PLUS_A_STEPS = (
    word_map(GENERATORS3, "x", "Xtx", "zx"),
    word_map(GENERATORS3, "tx", "t", "tz"),
    word_map(GENERATORS3, "xz", "t", "z"),
    word_map(GENERATORS3, "txT", "t", "z"),
    word_map(GENERATORS3, "Zx", "Zt", "z"),
    word_map(GENERATORS3, "Txt", "t", "z"),
)
PLUS_W_STEPS = (
    word_map(GENERATORS3, "x", "Xtx", "zx"),
    word_map(GENERATORS3, "tx", "t", "tz"),
    word_map(GENERATORS3, "tx", "t", "z"),
    word_map(GENERATORS3, "Zxz", "t", "z"),
    word_map(GENERATORS3, "Tx", "t", "z"),
    word_map(GENERATORS3, "Zxz", "Zt", "z"),
)
PLUS_D_STEPS = (
    word_map(GENERATORS3, "x", "Xt", "zx"),
    word_map(GENERATORS3, "xz", "Zt", "z"),
)

MINUS_A_STEPS = (
    word_map(GENERATORS3, "xz", "t", "z"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "x", "t", "Xzx"),
    word_map(GENERATORS3, "x", "Ztz", "z"),
)
MINUS_W_STEPS = (
    word_map(GENERATORS3, "tx", "t", "tz"),
    word_map(GENERATORS3, "tx", "t", "tz"),
    word_map(GENERATORS3, "tx", "t", "tz"),
    word_map(GENERATORS3, "xz", "tz", "z"),
    word_map(GENERATORS3, "txT", "t", "zT"),
    word_map(GENERATORS3, "x", "Xt", "z"),
    word_map(GENERATORS3, "Txt", "t", "z"),
    word_map(GENERATORS3, "x", "tx", "z"),
    word_map(GENERATORS3, "x", "tx", "z"),
    word_map(GENERATORS3, "x", "tx", "z"),
)
MINUS_D_STEPS = (
    word_map(GENERATORS3, "xz", "t", "z"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "txT", "t", "tz"),
    word_map(GENERATORS3, "x", "t", "Xzx"),
    word_map(GENERATORS3, "x", "Ztz", "z"),
    word_map(GENERATORS3, "x", "t", "Xz"),
    word_map(GENERATORS3, "x", "t", "Xz"),
    word_map(GENERATORS3, "x", "t", "Xz"),
    word_map(GENERATORS3, "Zxz", "t", "z"),
    word_map(GENERATORS3, "x", "tx", "Xz"),
)


def d_steps(delta: int) -> tuple[WordMap, ...]:
    return PLUS_D_STEPS if delta == 1 else MINUS_D_STEPS


def second_deletion_pair(delta: int) -> tuple[str, str]:
    first_a, first_w, first_d = first_deletion_survivors(delta)
    transformed = tuple(
        apply_maps(relator, d_steps(delta))
        for relator in (first_a, first_w, first_d)
    )
    if delta == 1:
        kill_coordinate = word_map(GENERATORS3, "", "x", "y")
    else:
        kill_coordinate = word_map(GENERATORS3, "x", "", "y")
    pair = tuple(
        substitute(relator, kill_coordinate)
        for relator in transformed[:2]
    )
    assert substitute(transformed[2], kill_coordinate) == ""
    return pair


PLUS_POST_PAIR = (
    "XYxYYYxYYYxyXyyyXyyyXyyy",
    "XYYxYYxYYYYxYYYxYYYxyXyyyXyyyXyyy",
)
MINUS_POST_PAIR = (
    "XXXXYxxxy",
    "XXXXYxxYxyxYxxxy",
)
COMMON_R = "YXXXXyxxx"
COMMON_S = "YYXXXXyxxxYxyx"
COMMON_B = "YYxyx"
KNOWN_COMPRESSION_PAIR = ("xxxyXXXXY", "YxyxY")
KNOWN_FLOOR_PAIR = ("YXXYx", "YYYYXyyyx")

U = "xxxTTTTZxt"
E = "TzQxqZ"
S = free_reduce(W + "Q")
BASED_PAIR_STEPS = (
    word_map(GENERATORS4, "x", "t", "z", "qz"),
    word_map(GENERATORS4, "x", "t", "xz", "q"),
    word_map(GENERATORS4, "x", "t", "tzT", "qT"),
    word_map(GENERATORS4, "x", "t", "zT", "q"),
    word_map(GENERATORS4, "x", "t", "zT", "q"),
    word_map(GENERATORS4, "x", "t", "zT", "q"),
    word_map(GENERATORS4, "qxQ", "t", "zQ", "q"),
    word_map(GENERATORS4, "x", "tx", "zx", "q"),
    word_map(GENERATORS4, "x", "t", "z", "qX"),
    word_map(GENERATORS4, "x", "t", "z", "qX"),
    word_map(GENERATORS4, "Qx", "t", "zq", "q"),
)
BASED_PAIR_ROWS = (
    ("xxxTTTTZxt", "TzQxqZ"),
    ("xxxTTTTZxt", "TQxq"),
    ("xxxTTTTZt", "TQxq"),
    ("xxxTTTZ", "QxqT"),
    ("xxxTTZ", "QxqT"),
    ("xxxTZ", "QxqT"),
    ("xxxZ", "QxqT"),
    ("qxxxZ", "xT"),
    ("qxxZ", "T"),
    ("qxZ", "T"),
    ("qZ", "T"),
    ("Z", "T"),
)
BASED_PAIR_AUTOMORPHISM = word_map(
    GENERATORS4,
    "xQ",
    "tQx",
    "xQtQxzxQxQxQXqTXqTXqTXqT",
    "qXqXqXqTxQtQxzxQxQxQXqTXqTXqTXqT",
)
BASED_PAIR_AUTOMORPHISM_INVERSE = word_map(
    GENERATORS4,
    "xxxqZt",
    "zQXqZt",
    "TXzttttXXX",
    "xxqZt",
)
ALL_K_RAW_ENDPOINT = (
    "xYxYxYXyXyXyXy",
    "yXyXyXyxYYxxYxYxYXyXyXyXy",
)
FLOOR_23_COORDINATE = word_map(GENERATORS2, "XyXXX", "yXXX")
FLOOR_23_COORDINATE_INVERSE = word_map(
    GENERATORS2,
    "yX",
    "yyXyXyX",
)


def normalize_pair(
    pair: Sequence[str],
    images: WordMap,
) -> tuple[str, str]:
    return tuple(
        canonical_relator(substitute(relator, images))
        for relator in pair
    )


def theta_image(word: str) -> str:
    beta_inverse = word_map(GENERATORS4, "Qxq", "t", "z", "q")
    return apply_maps(substitute(word, beta_inverse), BASED_PAIR_STEPS)


def all_k_pair_quotient(exponent: int) -> tuple[str, str]:
    lambda_k = word_map(
        GENERATORS4,
        "x",
        "t",
        free_reduce("z" + word_power("t", exponent)),
        "q",
    )
    kill_t_z_and_rename_q = word_map(
        GENERATORS4,
        "x",
        "",
        "",
        "y",
    )
    q_k = free_reduce(
        inverse_word(S) + word_power(D, exponent)
    )
    transformed_q = substitute(theta_image(q_k), lambda_k)
    transformed_d = substitute(theta_image(D), lambda_k)
    assert transformed_q == "z"
    assert transformed_d == "T"
    assert substitute(transformed_q, kill_t_z_and_rename_q) == ""
    assert substitute(transformed_d, kill_t_z_and_rename_q) == ""
    return tuple(
        substitute(
            substitute(theta_image(relator), lambda_k),
            kill_t_z_and_rename_q,
        )
        for relator in (A, W)
    )


def test_based_pair_certificate_gives_an_all_integer_power_coordinate():
    whitehead_maps = second_kind_automorphisms(GENERATORS4)
    assert len(whitehead_maps) == 504
    current = (U, E)
    assert current == BASED_PAIR_ROWS[0]
    for step, expected in zip(
        BASED_PAIR_STEPS,
        BASED_PAIR_ROWS[1:],
        strict=True,
    ):
        assert tuple(
            step[generator] for generator in GENERATORS4
        ) in whitehead_maps
        current = tuple(substitute(word, step) for word in current)
        assert current == expected
    assert current == ("Z", "T")

    combined = identity_map(GENERATORS4)
    for step in BASED_PAIR_STEPS:
        combined = compose(step, combined, GENERATORS4)
    assert combined == BASED_PAIR_AUTOMORPHISM
    assert_inverse_maps(
        BASED_PAIR_AUTOMORPHISM,
        BASED_PAIR_AUTOMORPHISM_INVERSE,
        GENERATORS4,
    )

    beta = word_map(GENERATORS4, "qxQ", "t", "z", "q")
    beta_inverse = word_map(GENERATORS4, "Qxq", "t", "z", "q")
    assert S == substitute(U, beta)
    assert theta_image(S) == "Z"
    assert theta_image(D) == "T"
    theta = compose(
        BASED_PAIR_AUTOMORPHISM,
        beta_inverse,
        GENERATORS4,
    )
    theta_inverse = word_map(
        GENERATORS4,
        "qxxxZt",
        "zXZt",
        "TqXQzttttqXXXQ",
        "qxxZt",
    )
    assert theta_inverse["t"] == inverse_word(D)
    assert theta_inverse["z"] == inverse_word(S)
    assert_inverse_maps(theta, theta_inverse, GENERATORS4)

    for exponent in (-7, -2, -1, 0, 1, 3, 8):
        q_k = free_reduce(
            inverse_word(S) + word_power(D, exponent)
        )
        lambda_k = word_map(
            GENERATORS4,
            "x",
            "t",
            free_reduce("z" + word_power("t", exponent)),
            "q",
        )
        lambda_k_inverse = word_map(
            GENERATORS4,
            "x",
            "t",
            free_reduce("z" + word_power("t", -exponent)),
            "q",
        )
        assert_inverse_maps(
            lambda_k,
            lambda_k_inverse,
            GENERATORS4,
        )
        assert substitute(theta_image(q_k), lambda_k) == "z"
        assert substitute(theta_image(D), lambda_k) == "T"


def test_all_integer_power_pair_quotients_are_the_same():
    assert_inverse_maps(
        FLOOR_23_COORDINATE,
        FLOOR_23_COORDINATE_INVERSE,
        GENERATORS2,
    )
    common = tuple(map(canonical_relator, (COMMON_R, COMMON_S)))
    assert sum(map(len, common)) == 23
    for images in second_kind_automorphisms(GENERATORS2):
        automorphism = word_map(GENERATORS2, *images)
        assert sum(
            len(canonical_relator(substitute(relator, automorphism)))
            for relator in common
        ) >= 23
    for exponent in (-7, -2, -1, 0, 1, 3, 8):
        endpoint = all_k_pair_quotient(exponent)
        assert endpoint == ALL_K_RAW_ENDPOINT
        assert normalize_pair(
            endpoint,
            FLOOR_23_COORDINATE,
        ) == common


def test_every_split_d_tail_reduces_to_the_total_power():
    for left, right in (
        (-5, 2),
        (-1, -1),
        (0, 0),
        (2, -5),
        (3, 4),
    ):
        split_tail = free_reduce(
            word_power(D, left)
            + inverse_word(S)
            + word_power(D, right)
        )
        conjugated = free_reduce(
            word_power(D, -left)
            + split_tail
            + word_power(D, left)
        )
        total_power = free_reduce(
            inverse_word(S)
            + word_power(D, left + right)
        )
        assert conjugated == total_power
        assert all_k_pair_quotient(left + right) == ALL_K_RAW_ENDPOINT


def test_four_block_source_straighteners_are_exact_automorphisms():
    for blocks, inverses in (
        (PLUS_BLOCKS, PLUS_BLOCK_INVERSES),
        (MINUS_BLOCKS, MINUS_BLOCK_INVERSES),
    ):
        for images, inverse in zip(blocks, inverses, strict=True):
            assert_inverse_maps(images, inverse, GENERATORS4)

    expected = {
        1: (
            (18, 15, 11, 8, 1),
            PLUS_SOURCE_CONJUGATOR,
        ),
        -1: (
            (16, 13, 10, 5, 1),
            MINUS_SOURCE_CONJUGATOR,
        ),
    }
    for delta, (lengths, conjugator) in expected.items():
        current = source(delta)
        observed = [len(canonical_relator(current))]
        for images in source_blocks(delta):
            current = substitute(current, images)
            observed.append(len(canonical_relator(current)))
        assert tuple(observed) == lengths
        assert current == free_reduce(
            conjugator + "q" + inverse_word(conjugator)
        )


def test_first_deletion_has_exact_three_survivors():
    expected = {
        1: (
            "TTxZxtXzTTxZxtXzTTxZxtXzTTxZxtZxtZxtZxtXz",
            "TTXzXttZxTXzXttZxTXzXttZxTXzXttZxTXzXttZxTXzTXzTXzXzTTxZxzXz",
            "XXz",
        ),
        -1: (
            "TTTTxZttttZxZxZxTTTTzX",
            "TTTTTTTTxZttttZxZxZxTTTTzXttttXzXzXzTTTTzXtxZttttZxZttttZx",
            "TTTTxZttttXzXzXzTTTTzXTxZttttZxZxZx",
        ),
    }
    for delta, displayed in expected.items():
        actual = first_deletion_survivors(delta)
        assert tuple(map(canonical_relator, actual)) == tuple(
            map(canonical_relator, displayed)
        )


def test_d_is_the_unique_primitive_survivor_after_first_deletion():
    plus_a, plus_w, plus_d = first_deletion_survivors(1)
    assert_complete_minimum(
        plus_a,
        PLUS_A_STEPS,
        (41, 30, 23, 19, 13, 9, 7),
        "XXXXzzz",
    )
    assert_complete_minimum(
        plus_w,
        PLUS_W_STEPS,
        (60, 45, 39, 34, 24, 19, 18),
        "TTZXtzTXZZZxxxxxtZ",
    )
    assert_complete_minimum(
        plus_d,
        PLUS_D_STEPS,
        (3, 2, 1),
        "X",
    )

    minus_a, minus_w, minus_d = first_deletion_survivors(-1)
    assert_complete_minimum(
        minus_a,
        MINUS_A_STEPS,
        (22, 19, 17, 15, 13, 11, 9, 7),
        "TTTTxxx",
    )
    assert_complete_minimum(
        minus_w,
        MINUS_W_STEPS,
        (58, 51, 44, 37, 29, 24, 21, 19, 18, 17, 16),
        "TXtXTZTxtzzzzXXX",
    )
    assert_complete_minimum(
        minus_d,
        MINUS_D_STEPS,
        (35, 30, 26, 22, 18, 14, 12, 10, 8, 6, 4, 2, 1),
        "T",
    )


def test_both_second_deletions_give_one_common_rank_two_pair():
    plus_pair = second_deletion_pair(1)
    minus_pair = second_deletion_pair(-1)
    assert tuple(map(canonical_relator, plus_pair)) == tuple(
        map(canonical_relator, PLUS_POST_PAIR)
    )
    assert tuple(map(canonical_relator, minus_pair)) == tuple(
        map(canonical_relator, MINUS_POST_PAIR)
    )

    plus_coordinate = word_map(GENERATORS2, "XYYY", "Y")
    plus_coordinate_inverse = word_map(GENERATORS2, "yyyX", "Y")
    minus_coordinate = word_map(GENERATORS2, "X", "YXX")
    minus_coordinate_inverse = word_map(GENERATORS2, "X", "xxY")
    assert_inverse_maps(
        plus_coordinate,
        plus_coordinate_inverse,
        GENERATORS2,
    )
    assert_inverse_maps(
        minus_coordinate,
        minus_coordinate_inverse,
        GENERATORS2,
    )

    common = tuple(map(canonical_relator, (COMMON_R, COMMON_S)))
    assert normalize_pair(plus_pair, plus_coordinate) == common
    assert normalize_pair(minus_pair, minus_coordinate) == common


def test_one_retained_source_factor_reaches_the_known_floor_14_corridor():
    assert COMMON_S == free_reduce("Y" + COMMON_R + "Yxyx")
    conjugate_r_inverse = free_reduce(
        "Y" + inverse_word(COMMON_R) + "y"
    )
    factor = free_reduce(
        inverse_word(COMMON_S)
        + conjugate_r_inverse
        + COMMON_S
    )
    assert free_reduce(COMMON_S + factor) == COMMON_B

    signed_relabel = word_map(GENERATORS2, "y", "X")
    signed_relabel_inverse = word_map(GENERATORS2, "Y", "x")
    assert_inverse_maps(
        signed_relabel,
        signed_relabel_inverse,
        GENERATORS2,
    )
    assert sorted(normalize_pair(
        (COMMON_R, COMMON_B),
        signed_relabel,
    )) == sorted(map(canonical_relator, KNOWN_FLOOR_PAIR))

    known_coordinate = word_map(GENERATORS2, "Y", "x")
    known_coordinate_inverse = word_map(GENERATORS2, "y", "X")
    assert_inverse_maps(
        known_coordinate,
        known_coordinate_inverse,
        GENERATORS2,
    )
    assert sorted(normalize_pair(
        KNOWN_COMPRESSION_PAIR,
        known_coordinate,
    )) == sorted(map(canonical_relator, KNOWN_FLOOR_PAIR))

    whitehead_maps = second_kind_automorphisms(GENERATORS2)
    floor_pair = tuple(map(canonical_relator, KNOWN_FLOOR_PAIR))
    assert sum(map(len, floor_pair)) == 14
    for images in whitehead_maps:
        automorphism = word_map(GENERATORS2, *images)
        transformed_length = sum(
            len(canonical_relator(substitute(relator, automorphism)))
            for relator in floor_pair
        )
        assert transformed_length >= 14


def compression_endpoint(delta: int) -> tuple[str, str]:
    pair = second_deletion_pair(delta)
    coordinate = (
        word_map(GENERATORS2, "XYYY", "Y")
        if delta == 1
        else word_map(GENERATORS2, "X", "YXX")
    )
    common = normalize_pair(pair, coordinate)
    assert common == tuple(map(canonical_relator, (COMMON_R, COMMON_S)))
    signed_relabel = word_map(GENERATORS2, "y", "X")
    return tuple(sorted(normalize_pair(
        (COMMON_R, COMMON_B),
        signed_relabel,
    )))


def test_both_d_tail_signs_merge_into_the_known_compression_pair():
    expected = tuple(sorted(map(canonical_relator, KNOWN_FLOOR_PAIR)))
    assert compression_endpoint(1) == expected
    assert compression_endpoint(-1) == expected
