from dataclasses import replace

from experiments.stable_ac.mms02_boundary_automorphism_corridor_certificate import (
    PINNED_FACTORS, decide_boundary_automorphism_corridor, decide_boundary_donor_switch,
    decide_boundary_second_switch, verify_second_switch_factors,
    decide_second_switch_magnus_corridor,
    decide_second_switch_short_killer,
    shifted_h_factors,
    verify_shifted_h_factors,
)


def reduce_word(word):
    stack = []
    for letter in word:
        if stack and stack[-1].swapcase() == letter:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def invert(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def conjugate(word, prefix):
    return reduce_word(prefix + word + invert(prefix))


def substitute(word, images):
    full = images | {letter.upper(): invert(value) for letter, value in images.items()}
    return reduce_word("".join(full[letter] for letter in word))


def test_boundary_source_donors_and_basis_changes_are_literal():
    decision = decide_boundary_automorphism_corridor()
    words = dict(decision.stage_words)
    r1 = "taTB"
    assert reduce_word("tbTAA" + invert("ttaTTAA")) == conjugate(invert(r1), "t")
    assert reduce_word("AAbbAt" + invert("AAtaaTAt")) == reduce_word(
        conjugate(invert(r1), "AA") + conjugate(invert(r1), "AAtaT"))
    assert substitute("ttaTTAA", {"t": "caa", "a": "a"}) == words["Hc"] == "caacaCAACAA"
    assert substitute("AAtaaTAt", {"t": "caa", "a": "a"}) == words["Jc"] == "AAcaaCAcaa"
    assert conjugate(words["Jc"], "caa") == words["K"] == "ccaaCA"
    assert substitute(words["K"], {"c": "x", "a": "Xu"}) == words["Kimage"] == "xuXuXUx"
    assert conjugate(words["Kimage"], "x") == words["Kt"] == "xxuXuXU"
    assert substitute(words["Hc"], {"c": "x", "a": "Xu"}) == words["Himage"] == "uXuuXUxUUxUx"
    assert conjugate(words["Himage"], "xx") == words["shiftedH"] == "xxuXuuXUxUUxUX"
    assert reduce_word("xxuXuXU" + invert("xvXvU")) == reduce_word(
        conjugate("xuXV", "x") + conjugate("xuXV", "xvX"))


def test_shifted_h_factors_expand_independently_and_reject_corruption():
    factors = shifted_h_factors()
    assert factors == PINNED_FACTORS
    donors = {1: "xuXV", 2: "xvXvU"}
    product = reduce_word("".join(
        conjugate(donors[factor.row] if factor.sign == 1 else invert(donors[factor.row]),
                  factor.conjugator) for factor in factors))
    shifted = "xxuXuuXUxUUxUX"
    assert product == reduce_word(shifted + invert("uvUVUx"))
    verify_shifted_h_factors(shifted, factors)
    corrupted = (replace(factors[0], sign=-factors[0].sign),) + factors[1:]
    try:
        verify_shifted_h_factors(shifted, corrupted)
    except AssertionError as error:
        assert "factorization drifted" in str(error)
    else:
        raise AssertionError("the corrupted factor was accepted")


def test_boundary_automorphism_inverse_and_killer_orientation_are_pinned():
    decision = decide_boundary_automorphism_corridor()
    phi = {"u": "v", "v": "uV"}
    reverse = {"u": "vu", "v": "u"}
    for generator in "uv":
        assert substitute(substitute(generator, phi), reverse) == generator
        assert substitute(substitute(generator, reverse), phi) == generator
    assert substitute("uvUV", phi) == invert("uvUV")
    assert decision.final_tuple == ("xuXV", "xvXvU", "uvUVUx")
    assert decision.phi_images == ("v", "uV")
    assert decision.inverse_images == ("vu", "u")
    assert decision.magnus_positions == ((2, "u"), (1, "u"), (1, "u"), (0, "U"),
                                         (1, "U"), (1, "U"), (2, "U"))
    assert decision.final_height == 1


def test_boundary_donor_switch_defining_rows_and_elimination_are_literal():
    decision = decide_boundary_donor_switch()
    defining = reduce_word("c" + invert("uvUV"))
    assert decision.source == ("tuTV", "tvTvU", "uvUVUt")
    assert reduce_word("uvUVUt" + invert("cUt")) == invert(defining)
    assert decision.defining_row == defining
    assert decision.corrected_killer == "cUt"
    assert decision.source_defect == invert(defining)
    images = {"t": "uC", "v": "uCucU", "u": "u", "c": "c"}
    assert substitute("cUt", images) == ""
    assert substitute("tuTV", images) == ""
    assert substitute("tvTvU", images) == "uCuCuccUU"
    assert substitute(defining, images) == "cuCucuCUcUU"
    assert decision.eliminated_pair == ("uCuCuccUU", "cuCucuCUcUU")
    assert decision.t_word == "uC"
    assert decision.v_word == "uCucU"


def test_boundary_switch_uses_only_the_retained_r_donor():
    decision = decide_boundary_donor_switch()
    retained = "uCuCuccUU"
    recipient = conjugate("cuCucuCUcUU", "uC")
    v_word = "uCucU"
    commutator = reduce_word("u" + v_word + "U" + invert(v_word))
    g_word = conjugate("c", "uC")
    assert g_word == "ucU"
    assert reduce_word(g_word + commutator) == "ucuCucUCUcU"
    assert reduce_word(g_word + commutator + v_word) == "ucuCucUU"
    defect = reduce_word("ucuCucUCUcU" + invert(recipient))
    product = reduce_word(conjugate(retained, "ucuCucUU") + conjugate(invert(retained), "ucU"))
    assert defect == product
    assert tuple((factor.row, factor.sign, factor.conjugator) for factor in decision.factors) == (
        (1, 1, "ucuCucUU"), (1, -1, "ucU"),
    )
    assert decision.conjugated_recipient == recipient
    assert decision.commutator == commutator
    assert decision.switched_row == "ucuCucUCUcU"
    assert decision.switch_defect == decision.switch_product == defect
    assert decision.verdict == "TARGET_STABLE_BOUNDARY_LEGAL_DONOR_SWITCH"


def test_second_boundary_switch_has_independent_retained_row_factorization():
    decision = decide_boundary_second_switch()
    retained, first = "uCuCuccUU", "ucuCucUCUcU"
    t_word, v_word = "uC", "uCucU"
    commutator = reduce_word("u" + v_word + "U" + invert(v_word))
    g2 = conjugate("c", t_word + t_word)
    recipient = conjugate(first, t_word)
    switched = reduce_word(g2 + invert(commutator))
    assert switched == "uCuccuCUcUU"
    defect = reduce_word(switched + invert(recipient))
    product = reduce_word(conjugate(retained, switched) + conjugate(invert(retained), "uCuccU"))
    assert product == defect
    assert decision.retained_row == retained
    assert decision.conjugating_word == t_word
    assert decision.conjugated_recipient == recipient
    assert decision.switched_row == switched
    assert decision.defect == decision.product == defect
    assert tuple((factor.row, factor.sign, factor.conjugator) for factor in decision.factors) == (
        (1, 1, switched), (1, -1, "uCuccU"),
    )
    corrupted = (replace(decision.factors[0], sign=-1), decision.factors[1])
    try:
        verify_second_switch_factors(retained, recipient, switched, corrupted)
    except AssertionError as error:
        assert "factorization drifted" in str(error)
    else:
        raise AssertionError("the corrupted second-switch factor was accepted")


def test_second_switch_magnus_data_remain_descriptive():
    decision = decide_boundary_second_switch()
    scanned = []
    for word in ("uCuccuCUcUU", "uCuCuccUU"):
        height = 0
        positions = []
        for letter in word:
            if letter.lower() == "u":
                height += {"u": 1, "U": -1}[letter]
            else:
                positions.append((height, letter))
        scanned.append((tuple(positions), height))
    assert scanned == [
        (((1, "C"), (2, "c"), (2, "c"), (3, "C"), (2, "c")), 0),
        (((1, "C"), (2, "C"), (3, "c"), (3, "c")), 1),
    ]
    assert (decision.e_magnus, decision.e_final_height) == scanned[0]
    assert (decision.r_magnus, decision.r_final_height) == scanned[1]
    forward, reverse = {"a": "b", "b": "bAbb"}, {"a": "aaBa", "b": "a"}
    for generator in "ab":
        assert substitute(substitute(generator, forward), reverse) == generator
        assert substitute(substitute(generator, reverse), forward) == generator
    assert decision.descriptive_phi_images == ("b", "bAbb")
    assert decision.descriptive_inverse_images == ("aaBa", "a")
    assert decision.descriptive_remaining_coefficient == "AAbbbAbb"
    assert decision.magnus_stable_ac_realization_claimed is False


def test_second_switch_magnus_basis_and_inverse_conjugation_are_literal():
    decision = decide_second_switch_magnus_corridor()
    assert decision.source_pair == ("uCuCuccUU", "uCuccuCUcUU")
    images = {"c": "Uau", "u": "u"}
    assert substitute("uCuCuccUU", images) == "AuAuaaU"
    assert substitute("uCuccuCUcUU", images) == "AuaauAUaU"
    assert conjugate(invert("AbbuBUb"), "b") == "ubUBBaB"
    assert dict(decision.stage_words) == {
        "R0": "AuAuaaU", "E20": "AuaauAUaU", "D": "uaUB",
        "Ebar": "AbbuBUb", "F": "ubUBBaB", "Rtemp": "ABubb", "target": "AAbbbAbbu",
    }
    assert sum(1 if letter == "u" else -1 if letter == "U" else 0 for letter in "ABubb") == 1
    assert decision.final_tuple == ("uaUB", "ubUBBaB", "AAbbbAbbu")
    assert decision.remaining_coefficient == "AAbbbAbb"
    assert decision.phi_images == ("b", "bAbb")


def test_second_switch_magnus_three_donor_stages_expand_independently():
    decision = decide_second_switch_magnus_corridor()
    donors = {1: "uaUB", 2: "ubUBBaB"}
    pins = (
        ((1, 1, "A"), (1, 1, "Ab"), (1, -1, "AbbuB"), (1, 1, "AbbuBU")),
        ((1, -1, "AB"), (1, 1, "ABu"), (1, 1, "ABub")),
        ((2, 1, "AB"), (2, 1, "AAbb")),
    )
    defects = tuple(reduce_word(left + invert(right)) for left, right in (
        ("AuaauAUaU", "AbbuBUb"), ("AuAuaaU", "ABubb"), ("ABubb", "AAbbbAbbu"),
    ))
    products = tuple(reduce_word("".join(
        conjugate(donors[row] if sign == 1 else invert(donors[row]), prefix)
        for row, sign, prefix in factors
    )) for factors in pins)
    assert defects == products
    assert decision.donor_defects == defects
    assert decision.donor_products == products
    assert tuple(tuple((factor.row, factor.sign, factor.conjugator) for factor in factors)
                 for factors in decision.factor_stages) == pins
    assert decision.verdict == "TARGET_STABLE_SECOND_SWITCH_MAGNUS_CORRIDOR"


def test_second_switch_short_killer_has_independent_retained_f_identity():
    decision = decide_second_switch_short_killer()
    donor, old_killer, short = "ubUBBaB", "AAbbbAbbu", "bbABu"
    conjugated = conjugate(old_killer, "bb")
    defect = reduce_word(conjugated + invert(short))
    product = reduce_word(conjugate(invert(donor), "bbAAbb")
                          + conjugate(invert(donor), "bbAB"))
    assert defect == product
    assert decision.source_tuple == ("uaUB", donor, old_killer)
    assert decision.conjugated_killer == conjugated
    assert tuple((factor.row, factor.sign, factor.conjugator) for factor in decision.factors) == (
        (2, -1, "bbAAbb"), (2, -1, "bbAB"),
    )
    assert decision.defect == decision.product == defect
    assert decision.final_tuple == ("uaUB", "ubUBBaB", "bbABu")
    assert decision.verdict == "TARGET_STABLE_SECOND_SWITCH_SHORT_KILLER"


def _sl2_seven_evaluate(word, parameter=3):
    matrices = {"m": (1, 1, 0, 1), "M": (1, -1, 0, 1),
                "n": (1, 0, parameter, 1), "N": (1, 0, -parameter, 1)}
    result = (1, 0, 0, 1)
    for letter in word:
        a, b, c, d = result
        e, f, g, h = matrices[letter]
        result = ((a * e + b * g) % 7, (a * f + b * h) % 7,
                  (c * e + d * g) % 7, (c * f + d * h) % 7)
    return result


def test_short_killer_literature_map_and_retained_donors_are_literal():
    images = {"a": "Mn", "b": "NmnMMn", "u": "Nmn"}
    relator, killer = "mNmnMNmNMn", "NmnMnMNmm"
    w = "nMNm"
    standard = reduce_word(invert(w) + "m" + w + "N")
    assert standard == "MnmNmnMNmN"
    assert relator == standard[2:] + standard[:2]
    assert substitute("uaUB", images) == ""
    assert substitute("ubUBBaB", images) == conjugate(relator, "NmnM")
    assert substitute("bbABu", images) == killer
    assert substitute("aBu", images) == "m"
    assert substitute("aBua", images) == "n"
    assert _sl2_seven_evaluate(relator) == (1, 0, 0, 1)
    for donor in ("uaUB", "ubUBBaB"):
        assert _sl2_seven_evaluate(substitute(donor, images)) == (1, 0, 0, 1)
    assert _sl2_seven_evaluate(killer) == (3, 1, 6, 0)
    assert _sl2_seven_evaluate(w + "n") == (6, 3, 2, 0)


def test_short_killer_trace_controls_can_fail_and_reject_invalid_base():
    trace = lambda word: sum(_sl2_seven_evaluate(word)[i] for i in (0, 3)) % 7
    killer, simple = "NmnMnMNmm", "nMNmn"
    assert trace(killer) == 3
    assert tuple(trace(word) for word in ("m", "n", simple)) == (2, 2, 6)
    for word in (killer, "m", "n", simple):
        assert trace(invert(word)) == trace(word)
        assert trace(conjugate(word, "mnM")) == trace(word)
    assert trace(conjugate("m", "n")) == trace("m")
    assert _sl2_seven_evaluate("mNmnMNmNMn", parameter=1) != (1, 0, 0, 1)
