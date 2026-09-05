"""Literal stable-equivalence corridor to a boundary automorphism killer."""

from dataclasses import dataclass

from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    apply_images, free_reduce, inverse,
)

SOURCE = ("taTB", "tbTAA", "AAbbAt")
D_ROW = "xuXV"
E_ROW = "xvXvU"
P5 = "uvUVU"
MAGNUS_POSITIONS = ((2, "u"), (1, "u"), (1, "u"), (0, "U"),
                    (1, "U"), (1, "U"), (2, "U"))


@dataclass(frozen=True)
class Factor:
    row: int
    sign: int
    conjugator: str


PINNED_FACTORS = (
    Factor(1, 1, "x"), Factor(2, 1, ""), Factor(1, 1, "uV"),
    Factor(1, 1, "u"), Factor(1, -1, "uvUV"), Factor(1, -1, "uvUVV"),
    Factor(2, -1, "uvUVU"), Factor(1, -1, "uvUVUx"),
)


def conjugate(word: str, conjugator: str) -> str:
    return free_reduce(conjugator + word + inverse(conjugator))


def phi(word: str) -> str:
    return apply_images(word, {"u": "v", "v": "uV"})


def phi_inverse(word: str) -> str:
    return apply_images(word, {"u": "vu", "v": "u"})


def transported_letter(height: int, letter: str) -> tuple[str, tuple[Factor, ...]]:
    if height not in (0, 1, 2) or letter not in "uU":
        raise ValueError("only the pinned height-zero-to-two u letters are supported")
    image = "u"
    for _ in range(height):
        image = phi(image)
    positive = ((), (Factor(1, 1, ""),),
                (Factor(1, 1, "x"), Factor(2, 1, "")))[height]
    if letter == "u":
        return image, positive
    return inverse(image), tuple(
        Factor(factor.row, -factor.sign, free_reduce(inverse(image) + factor.conjugator))
        for factor in reversed(positive)
    )


def shifted_h_factors() -> tuple[Factor, ...]:
    prefix = ""
    factors = []
    for height, letter in MAGNUS_POSITIONS:
        image, local = transported_letter(height, letter)
        factors.extend(Factor(factor.row, factor.sign,
                              free_reduce(prefix + factor.conjugator)) for factor in local)
        prefix = free_reduce(prefix + image)
    if prefix != P5 or tuple(factors) != PINNED_FACTORS:
        raise AssertionError("the pinned shifted-H factors drifted")
    return tuple(factors)


def expand_factors(factors: tuple[Factor, ...]) -> str:
    product = ""
    for factor in factors:
        if factor.row not in (1, 2) or factor.sign not in (-1, 1):
            raise ValueError("invalid signed donor factor")
        donor = (D_ROW, E_ROW)[factor.row - 1]
        product += conjugate(donor if factor.sign == 1 else inverse(donor), factor.conjugator)
    return free_reduce(product)


def verify_shifted_h_factors(shifted_h: str, factors: tuple[Factor, ...]) -> None:
    if expand_factors(factors) != free_reduce(shifted_h + inverse(P5 + "x")):
        raise AssertionError("the shifted-H donor factorization drifted")


@dataclass(frozen=True)
class BoundaryCorridorDecision:
    stage_words: tuple[tuple[str, str], ...]
    donor_defects: tuple[str, ...]
    donor_products: tuple[str, ...]
    magnus_positions: tuple[tuple[int, str], ...]
    final_height: int
    factors: tuple[Factor, ...]
    final_tuple: tuple[str, str, str]
    phi_images: tuple[str, str]
    inverse_images: tuple[str, str]
    verdict: str


def decide_boundary_automorphism_corridor() -> BoundaryCorridorDecision:
    r1, r2, j_row = SOURCE
    h_row, jp = "ttaTTAA", "AAtaaTAt"
    hc = apply_images(h_row, {"t": "caa", "a": "a"})
    jc = apply_images(jp, {"t": "caa", "a": "a"})
    k_row = conjugate(jc, "caa")
    k_image = apply_images(k_row, {"c": "x", "a": "Xu"})
    kt = conjugate(k_image, "x")
    h_image = apply_images(hc, {"c": "x", "a": "Xu"})
    shifted_h = conjugate(h_image, "xx")
    stages = (("H", h_row), ("Jp", jp), ("Hc", hc), ("Jc", jc),
              ("K", k_row), ("Kimage", k_image), ("Kt", kt),
              ("Himage", h_image), ("shiftedH", shifted_h))
    expected = ("ttaTTAA", "AAtaaTAt", "caacaCAACAA", "AAcaaCAcaa",
                "ccaaCA", "xuXuXUx", "xxuXuXU", "uXuuXUxUUxUx",
                "xxuXuuXUxUUxUX")
    if tuple(word for _, word in stages) != expected:
        raise AssertionError("the boundary corridor stage words drifted")
    defects = tuple(free_reduce(left + inverse(right)) for left, right in (
        (r2, h_row), (j_row, jp), (kt, E_ROW),
    ))
    products = (
        conjugate(inverse(r1), "t"),
        free_reduce(conjugate(inverse(r1), "AA") + conjugate(inverse(r1), "AAtaT")),
        free_reduce(conjugate(D_ROW, "x") + conjugate(D_ROW, "xvX")),
    )
    if defects != products:
        raise AssertionError("the boundary corridor donor identities drifted")
    height, positions = 0, []
    for letter in shifted_h:
        if letter in "xX":
            height += 1 if letter == "x" else -1
        else:
            positions.append((height, letter))
    if tuple(positions) != MAGNUS_POSITIONS or height != 1:
        raise AssertionError("the shifted-H Magnus positions drifted")
    factors = shifted_h_factors()
    verify_shifted_h_factors(shifted_h, factors)
    for generator in "uv":
        if phi(phi_inverse(generator)) != generator or phi_inverse(phi(generator)) != generator:
            raise AssertionError("the pinned inverse automorphism drifted")
    if phi("uvUV") != inverse("uvUV"):
        raise AssertionError("the boundary commutator orientation drifted")
    return BoundaryCorridorDecision(
        stages, defects, products, MAGNUS_POSITIONS, height, factors,
        (D_ROW, E_ROW, P5 + "x"), ("v", "uV"), ("vu", "u"),
        "TARGET_STABLE_BOUNDARY_AUTOMORPHISM_KILLER_GATE",
    )


SOURCE_BOUNDARY = ("tuTV", "tvTvU", "uvUVUt")
SWITCH_FACTORS = (Factor(1, 1, "ucuCucUU"), Factor(1, -1, "ucU"))


@dataclass(frozen=True)
class BoundaryDonorSwitchDecision:
    source: tuple[str, str, str]
    defining_row: str
    corrected_killer: str
    source_defect: str
    t_word: str
    v_word: str
    eliminated_pair: tuple[str, str]
    commutator: str
    conjugating_word: str
    conjugated_recipient: str
    switched_row: str
    factors: tuple[Factor, ...]
    switch_defect: str
    switch_product: str
    verdict: str


def decide_boundary_donor_switch() -> BoundaryDonorSwitchDecision:
    r1, r2, killer = SOURCE_BOUNDARY
    defining = free_reduce("c" + inverse("uvUV"))
    corrected = "cUt"
    source_defect = free_reduce(killer + inverse(corrected))
    if source_defect != inverse(defining):
        raise AssertionError("the boundary defining-row killer correction drifted")
    t_word, v_word = "uC", "uCucU"
    substitutions = {"t": t_word, "v": v_word, "u": "u", "c": "c"}
    if apply_images(r1, substitutions) or apply_images(corrected, substitutions):
        raise AssertionError("the boundary defining rows did not disappear")
    raw_pair = (apply_images(r2, substitutions), apply_images(defining, substitutions))
    if raw_pair != ("uCuCuccUU", "cuCucuCUcUU"):
        raise AssertionError("the boundary eliminated pair drifted")
    commutator = free_reduce("u" + v_word + "U" + inverse(v_word))
    g_word = conjugate("c", t_word)
    recipient = conjugate(raw_pair[1], t_word)
    switched = free_reduce(g_word + commutator)
    if g_word != "ucU" or switched != "ucuCucUCUcU":
        raise AssertionError("the boundary switched row drifted")
    if free_reduce(g_word + commutator + v_word) != SWITCH_FACTORS[0].conjugator:
        raise AssertionError("the positive boundary donor conjugator drifted")
    defect = free_reduce(switched + inverse(recipient))
    product = free_reduce("".join(
        conjugate(raw_pair[0] if factor.sign == 1 else inverse(raw_pair[0]), factor.conjugator)
        for factor in SWITCH_FACTORS
    ))
    if any(factor.row != 1 for factor in SWITCH_FACTORS) or defect != product:
        raise AssertionError("the retained-row boundary donor switch drifted")
    return BoundaryDonorSwitchDecision(
        SOURCE_BOUNDARY, defining, corrected, source_defect, t_word, v_word,
        raw_pair, commutator, g_word, recipient, switched, SWITCH_FACTORS,
        defect, product, "TARGET_STABLE_BOUNDARY_LEGAL_DONOR_SWITCH",
    )
