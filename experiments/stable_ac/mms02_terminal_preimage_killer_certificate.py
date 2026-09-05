"""Literal preimage-killer correction and stable terminal base pair."""

from dataclasses import dataclass

from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.mms02_terminal_base_pair_certificate import (
    R1, R2, from_xy, phi, to_xy,
)
from experiments.stable_ac.mms02_terminal_hnn_certificate import (
    canonical_cyclic_pair, canonical_cyclic_word, whitehead_minimum,
)
from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    apply_images, free_reduce, inverse,
)
from experiments.stable_ac.mms02_terminal_twisted_coboundary_certificate import (
    P_WORD, Q_WORD,
)

EXPECTED_BASE_PAIR = (
    "QpQQPQpQPQppqPqpQpQPPqpqPqpqqP",
    "QpQQPQpQPQppqPqpQPPqpqPqpqP",
)
EXPECTED_PRODUCT_MINIMUM = (
    "PPPqpqPqpQPQpQPQppq",
    "PPqpqPqpqPQpQQPQpQPQppqPqpQ",
)
PINNED_FACTOR_PREFIXES = (
    (2, -1, "Q"),
    (1, 1, "Q"),
    (2, -1, "QpQ"),
    (1, -1, "QpQP"),
    (1, -1, "QpQPP"),
    (2, 1, "QpQPP"),
    (1, 1, "QpQPPq"),
    (2, 1, "QpQPPqp"),
    (1, -1, "QpQPPqpqP"),
    (2, 1, "QpQPPqpqP"),
    (1, 1, "QpQPPqpqPq"),
    (2, 1, "QpQPPqpqPqp"),
    (2, 1, "QpQPPqpqPqpq"),
    (1, -1, "QpQPPqpqPqpqqP"),
    (2, 1, "QpQPPqpqPqpqqP"),
)


@dataclass(frozen=True)
class CyclicTransition:
    signs: tuple[int, int]
    rotations: tuple[int, int]
    retained_index: int
    product: str
    target_pair: tuple[str, str]
    floor: int
    ambient_descent: tuple[tuple[str, str], ...]


PINNED_TRANSITIONS = (
    CyclicTransition((1, 1), (0, 26), 0, "PPqpQPQpQPQppqPq",
                     ("PPQQPPQppqPPqppqqpQ", "PPQQPPQppqqPqpQ"), 34, (("x", "xy"),)),
    CyclicTransition((1, 1), (10, 9), 1, "PPQQPPQppqqqPqpQPQ",
                     ("PPQQPPQppqqPqpQ", "PPQQPPQppqqqPqpQPQ"), 33, ()),
    CyclicTransition((1, -1), (0, 0), 0, "PPQpqPqpQ",
                     ("PPQQPPQppqqPqpQ", "PPQpqPqpQ"), 24, ()),
    CyclicTransition((1, -1), (0, 0), 0, "PPQppqPQ",
                     ("PPQQPPQppqqPqpQ", "PPQppqPQ"), 23, ()),
    CyclicTransition((1, 1), (0, 5), 1, "PPPQQQPPQppqq",
                     ("PPPQQQPPQppqq", "PPQppqPQ"), 21, ()),
    CyclicTransition((1, -1), (5, 1), 0, "PPPQQpq",
                     ("PPPQQQPPQppqq", "PPPQQpq"), 20, ()),
    CyclicTransition((1, -1), (0, 0), 1, "PPQppqPQ",
                     ("PPPQQpq", "PPQppqPQ"), 15, ()),
)


def replay_cyclic_continuation() -> tuple[CyclicTransition, ...]:
    pair = EXPECTED_PRODUCT_MINIMUM
    for transition in PINNED_TRANSITIONS:
        rotated = []
        for word, sign, index in zip(pair, transition.signs, transition.rotations, strict=True):
            oriented = word if sign == 1 else inverse(word)
            if not 0 <= index < len(oriented):
                raise AssertionError("the pinned cyclic rotation is out of range")
            rotated.append(oriented[index:] + oriented[:index])
        product = canonical_cyclic_word("".join(rotated))
        if product != transition.product:
            raise AssertionError("the pinned cyclic product drifted")
        xy_pair = canonical_cyclic_pair((to_xy(product), to_xy(pair[transition.retained_index])))
        for x_image, y_image in transition.ambient_descent:
            xy_pair = canonical_cyclic_pair(tuple(
                apply_images(word, {"x": x_image, "y": y_image}) for word in xy_pair
            ))
        pair = tuple(from_xy(word) for word in xy_pair)
        if pair != transition.target_pair or sum(map(len, pair)) != transition.floor:
            raise AssertionError("the pinned cyclic endpoint drifted")
        if aut_min_len(xy_pair) != transition.floor:
            raise AssertionError("the independent cyclic floor disagrees")
    return PINNED_TRANSITIONS


@dataclass(frozen=True)
class DonorFactor:
    row: int
    sign: int
    conjugator: str


def rho(word: str) -> str:
    return free_reduce("x" + word + "X" + inverse(phi(word)))


def rho_factors(word: str) -> tuple[DonorFactor, ...]:
    factors = []
    prefix = ""
    for letter in word:
        if letter not in "pPqQ":
            raise ValueError("rho factors require a base word")
        sign = 1 if letter.islower() else -1
        conjugator = phi(prefix + (letter if sign == -1 else ""))
        factors.append(DonorFactor(1 if letter.lower() == "p" else 2, sign, conjugator))
        prefix += letter
    return tuple(factors)


def expand_factors(factors: tuple[DonorFactor, ...]) -> str:
    words = []
    for factor in factors:
        if factor.row not in (1, 2) or factor.sign not in (-1, 1):
            raise ValueError("invalid signed donor factor")
        donor = (R1, R2)[factor.row - 1]
        body = donor if factor.sign == 1 else inverse(donor)
        words.append(factor.conjugator + body + inverse(factor.conjugator))
    return free_reduce("".join(words))


def verify_rho_factors(word: str, factors: tuple[DonorFactor, ...]) -> None:
    if expand_factors(factors) != rho(word):
        raise AssertionError("the rho donor factorization drifted")


@dataclass(frozen=True)
class PreimageKillerDecision:
    factors: tuple[DonorFactor, ...]
    conjugated_killer: str
    correction: str
    corrected_killer: str
    transformed_rows: tuple[str, ...]
    base_pair: tuple[str, ...]
    base_lengths: tuple[int, ...]
    base_floor: int
    product_pair: tuple[str, str]
    product_minimum: tuple[str, ...]
    product_floor: int
    transitions: tuple[CyclicTransition, ...]
    terminal_pair: tuple[str, str]
    terminal_floor: int
    verdict: str


def decide_preimage_killer() -> PreimageKillerDecision:
    if phi(Q_WORD) != P_WORD:
        raise AssertionError("the pinned killer preimage drifted")
    factors = rho_factors(Q_WORD)
    pinned = tuple(DonorFactor(row, sign, phi(prefix)) for row, sign, prefix in PINNED_FACTOR_PREFIXES)
    if factors != pinned:
        raise AssertionError("the pinned rho factors drifted")
    verify_rho_factors(Q_WORD, factors)
    conjugated = free_reduce("X" + P_WORD + "xx")
    correction = free_reduce("X" + expand_factors(factors) + "x")
    corrected = free_reduce(correction + conjugated)
    if corrected != Q_WORD + "x":
        raise AssertionError("the preimage killer correction drifted")
    ambient = {"p": "p", "q": "q", "x": inverse(Q_WORD) + "x"}
    transformed = tuple(apply_images(row, ambient) for row in (R1, R2, corrected))
    if transformed[2] != "x":
        raise AssertionError("the corrected killer did not become x")
    base_pair = tuple(apply_images(row, {"p": "p", "q": "q", "x": ""}) for row in transformed[:2])
    if base_pair != EXPECTED_BASE_PAIR or tuple(map(len, base_pair)) != (30, 27):
        raise AssertionError("the preimage base pair drifted")
    xy_pair = tuple(to_xy(word) for word in base_pair)
    minimum, _ = whitehead_minimum(xy_pair)
    base_floor = sum(map(len, minimum))
    if base_floor != 57 or aut_min_len(xy_pair) != 57:
        raise AssertionError("the independent preimage base floors disagree")
    product_pair = (free_reduce(inverse(base_pair[0]) + base_pair[1]), base_pair[1])
    product_xy = tuple(to_xy(word) for word in product_pair)
    product_minimum_xy, product_descent = whitehead_minimum(product_xy)
    if product_descent != ():
        raise AssertionError("the initial product requires an unpinned ambient descent")
    product_minimum = tuple(from_xy(word) for word in product_minimum_xy)
    product_floor = sum(map(len, product_minimum))
    if product_minimum != EXPECTED_PRODUCT_MINIMUM or product_floor != 46:
        raise AssertionError("the pinned product minimum drifted")
    if aut_min_len(product_xy) != product_floor:
        raise AssertionError("the independent product floors disagree")
    transitions = replay_cyclic_continuation()
    return PreimageKillerDecision(
        factors, conjugated, correction, corrected, transformed, base_pair,
        tuple(map(len, base_pair)), base_floor, product_pair, product_minimum,
        product_floor, transitions, transitions[-1].target_pair, transitions[-1].floor,
        "TARGET_STABLE_PREIMAGE_KILLER_FLOOR_15",
    )


@dataclass(frozen=True)
class SquaringHNNDecision:
    stage_words: tuple[tuple[str, str], ...]
    donor_defects: tuple[str, ...]
    donor_products: tuple[str, ...]
    final_tuple: tuple[str, str, str]
    phi_images: tuple[str, str]
    killer_prefix: str
    verdict: str


def decide_squaring_hnn_target() -> SquaringHNNDecision:
    a_row, b_row = PINNED_TRANSITIONS[-1].target_pair
    m_word = "qppp"
    c_row = free_reduce("PP" + m_word + m_word + "PQ")
    a0 = apply_images(a_row, {"p": "p", "q": "rPPP"})
    c0 = apply_images(c_row, {"p": "p", "q": "rPPP"})
    h_row = free_reduce("pp" + inverse(c0) + "PP")
    prefix = "RpppR"
    k_row = free_reduce(inverse(prefix) + a0 + prefix)
    y_row = free_reduce("pp" + k_row + "PP")
    k1 = "prrPRpRR"
    d_row, h2, k2 = "prPB", "pbPRR", "bbRpRR"
    j_row = free_reduce("RR" + k2 + "rr")
    stage_words = (
        ("A", a_row), ("B", b_row), ("M", m_word), ("C", c_row),
        ("A0", a0), ("C0", c0), ("H", h_row), ("prefix", prefix),
        ("K", k_row), ("Y", y_row), ("K1", k1), ("D", d_row),
        ("H2", h2), ("K2", k2), ("J", j_row),
    )
    expected = {
        "C": "PPqpppqppQ", "A0": "RpppRprPPP", "C0": "PPrrppR",
        "H": "pprPPRR", "K": "prPPPRpppR", "J": "RRbbRp",
    }
    if any(dict(stage_words)[name] != word for name, word in expected.items()):
        raise AssertionError("the squaring-HNN stage words drifted")
    donor_defects = tuple(free_reduce(left + inverse(right)) for left, right in (
        (b_row, c_row), (y_row, k1), (h_row, h2), (k1, k2),
    ))
    first_conjugator, second_conjugator = "PP" + m_word, "PP" + m_word + m_word
    donor_products = tuple(map(free_reduce, (
        first_conjugator + a_row + inverse(first_conjugator)
        + second_conjugator + a_row + inverse(second_conjugator),
        "p" + h_row + "P" + k1 + inverse(h_row) + inverse(k1),
        "p" + d_row + "P",
        d_row + "b" + d_row + "B",
    )))
    if donor_defects != donor_products:
        raise AssertionError("the squaring-HNN donor identities drifted")
    final_tuple = tuple(apply_images(row, {"p": "t", "r": "a", "b": "b"})
                        for row in (d_row, h2, j_row))
    if final_tuple != ("taTB", "tbTAA", "AAbbAt"):
        raise AssertionError("the squaring-HNN target orientation drifted")
    return SquaringHNNDecision(
        stage_words, donor_defects, donor_products, final_tuple,
        ("b", "aa"), "AAbbA", "TARGET_STABLE_SQUARING_HNN_KILLER_GATE",
    )


@dataclass(frozen=True)
class ConstructiveLengthFourteenDecision:
    inputs: tuple[tuple[str, str], ...]
    factors: tuple[DonorFactor, ...]
    outer_conjugator: str
    conjugated_killer: str
    corrected_killer: str
    defect: str
    expanded_defect: str
    transformed_rows: tuple[str, ...]
    base_pair: tuple[str, str]
    rotated_pair: tuple[str, str]
    product: str
    conjugated_product: str
    final_pair: tuple[str, str]
    verdict: str


def decide_constructive_length_fourteen() -> ConstructiveLengthFourteenDecision:
    h_word = "qqPq"
    phi_h = phi(h_word)
    w_word = free_reduce(h_word + Q_WORD + inverse(phi_h))
    if phi_h != "pqPqpqqPq" or w_word != "qPPq":
        raise AssertionError("the length-fourteen killer inputs drifted")
    conjugated = free_reduce(h_word + Q_WORD + "x" + inverse(h_word))
    corrected = w_word + "x"
    outer = free_reduce(h_word + Q_WORD)
    factors = rho_factors(inverse(h_word))
    if len(factors) != 4:
        raise AssertionError("the length-fourteen correction must have four donor factors")
    verify_rho_factors(inverse(h_word), factors)
    expanded = free_reduce(outer + expand_factors(factors) + inverse(outer))
    defect = free_reduce(conjugated + inverse(corrected))
    if defect != expanded:
        raise AssertionError("the length-fourteen killer donor correction drifted")
    ambient = {"p": "p", "q": "q", "x": inverse(w_word) + "x"}
    transformed = tuple(apply_images(row, ambient) for row in (R1, R2, corrected))
    if transformed[2] != "x":
        raise AssertionError("the length-fourteen killer did not become x")
    base = tuple(apply_images(row, {"p": "p", "q": "q", "x": ""}) for row in transformed[:2])
    if base != ("QppQpqPP", "QppqPQP"):
        raise AssertionError("the length-fourteen stable base pair drifted")
    inverted_second = inverse(base[1])
    rotated = (base[0][6:] + base[0][:6], inverted_second[4:] + inverted_second[:4])
    if rotated != ("PPQppQpq", "PPqpqpQ"):
        raise AssertionError("the length-fourteen pinned base rotations drifted")
    a_row, b_row = rotated
    product = free_reduce(a_row[1:] + a_row[:1] + b_row[4:] + b_row[:4])
    if product != "PQppQpqPqpQPPqp":
        raise AssertionError("the length-fourteen literal row product drifted")
    conjugated_product = free_reduce("PPqp" + product + inverse("PPqp"))
    if conjugated_product != "QpqPqpQ":
        raise AssertionError("the length-fourteen product conjugation drifted")
    inverted_product = inverse(conjugated_product)
    final = (b_row, inverted_product[1:] + inverted_product[:1])
    if final != ("PPqpqpQ", "PQpQPqq") or sum(map(len, final)) != 14:
        raise AssertionError("the constructive length-fourteen endpoint drifted")
    return ConstructiveLengthFourteenDecision(
        (("h", h_word), ("Q", Q_WORD), ("phi_h", phi_h), ("W", w_word)),
        factors, outer, conjugated, corrected, defect, expanded, transformed,
        base, rotated, product, conjugated_product, final,
        "CONSTRUCTIVE_LENGTH_FOURTEEN_TARGET_ONLY",
    )
