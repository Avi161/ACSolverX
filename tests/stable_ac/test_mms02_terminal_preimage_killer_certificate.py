from dataclasses import replace

from experiments.stable_ac.mms02_terminal_preimage_killer_certificate import (
    EXPECTED_BASE_PAIR, EXPECTED_PRODUCT_MINIMUM, PINNED_FACTOR_PREFIXES,
    PINNED_TRANSITIONS, decide_preimage_killer, decide_squaring_hnn_target,
    decide_constructive_length_fourteen,
    replay_cyclic_continuation,
    rho_factors, verify_rho_factors,
)


def reduce_word(word):
    stack = []
    for letter in word:
        if stack and ord(stack[-1]) ^ ord(letter) == 32:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def invert(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def image(word):
    images = {"p": "q", "P": "Q", "q": "pqPq", "Q": "QpQP"}
    return reduce_word("".join(images[letter] for letter in word))


def expanded(factors):
    donors = {1: "xpXQ", 2: "xqXQpQP"}
    return reduce_word("".join(
        factor.conjugator
        + (donors[factor.row] if factor.sign == 1 else invert(donors[factor.row]))
        + invert(factor.conjugator)
        for factor in factors
    ))


def test_preimage_rho_factors_have_independent_literal_expansion():
    preimage = "QpQPPqpqPqpqqPq"
    killer = "QpQQPQQpqPqqpqqPqqpqPqpqqPq"
    factors = rho_factors(preimage)
    assert image(preimage) == killer
    assert tuple((factor.row, factor.sign, factor.conjugator) for factor in factors) == tuple(
        (row, sign, image(prefix)) for row, sign, prefix in PINNED_FACTOR_PREFIXES
    )
    assert expanded(factors) == reduce_word("x" + preimage + "X" + invert(killer))
    verify_rho_factors(preimage, factors)
    conjugated = "X" + killer + "xx"
    assert reduce_word("X" + expanded(factors) + "x" + conjugated) == preimage + "x"


def test_preimage_rho_verifier_rejects_corrupted_factor():
    preimage = "QpQPPqpqPqpqqPq"
    factors = rho_factors(preimage)
    corrupted = (replace(factors[0], sign=-factors[0].sign),) + factors[1:]
    try:
        verify_rho_factors(preimage, corrupted)
    except AssertionError as error:
        assert "factorization drifted" in str(error)
    else:
        raise AssertionError("the corrupted factor was accepted")


def test_preimage_killer_stable_elimination_and_product_are_pinned():
    decision = decide_preimage_killer()
    preimage = "QpQPPqpqPqpqqPq"
    raw = (
        reduce_word(invert(preimage) + "p" + preimage + "Q"),
        reduce_word(invert(preimage) + "q" + preimage + "QpQP"),
    )
    assert decision.corrected_killer == preimage + "x"
    assert decision.transformed_rows[2] == "x"
    assert decision.base_pair == raw == EXPECTED_BASE_PAIR
    assert decision.base_lengths == (30, 27)
    assert decision.base_floor == 57
    assert decision.product_pair == (reduce_word(invert(raw[0]) + raw[1]), raw[1])
    assert tuple(sorted(map(canonical_word, decision.product_pair))) == EXPECTED_PRODUCT_MINIMUM
    assert decision.product_minimum == EXPECTED_PRODUCT_MINIMUM
    assert decision.product_floor == 46
    assert decision.terminal_pair == ("PPPQQpq", "PPQppqPQ")
    assert decision.terminal_floor == 15
    assert decision.verdict == "TARGET_STABLE_PREIMAGE_KILLER_FLOOR_15"


def canonical_word(word):
    word = reduce_word(word)
    while len(word) > 1 and word[0].swapcase() == word[-1]:
        word = word[1:-1]
    return min(oriented[index:] + oriented[:index]
               for oriented in (word, invert(word)) for index in range(len(word)))


def test_pinned_cyclic_continuation_has_independent_literal_products():
    pair = EXPECTED_PRODUCT_MINIMUM
    for transition in PINNED_TRANSITIONS:
        factors = []
        for word, sign, index in zip(pair, transition.signs, transition.rotations, strict=True):
            signed = word if sign == 1 else invert(word)
            factors.append(signed[index:] + signed[:index])
        assert canonical_word("".join(factors)) == transition.product
        retained = pair[transition.retained_index]
        pair = tuple(sorted(map(canonical_word, (transition.product, retained))))
        for x_image, y_image in transition.ambient_descent:
            rename = str.maketrans("xXyY", "pPqQ")
            images = {"p": x_image.translate(rename), "q": y_image.translate(rename)}
            images.update({letter.upper(): invert(word) for letter, word in tuple(images.items())})
            pair = tuple(sorted(canonical_word("".join(images[letter] for letter in word)) for word in pair))
        assert pair == transition.target_pair
        assert sum(map(len, pair)) == transition.floor
    assert replay_cyclic_continuation() == PINNED_TRANSITIONS
    assert tuple(step.floor for step in PINNED_TRANSITIONS) == (34, 33, 24, 23, 21, 20, 15)


def test_squaring_hnn_has_four_independent_literal_donor_identities():
    a_row, b_row = "PPPQQpq", "PPQppqPQ"
    m_word, c_row = "qppp", "PPqpppqppQ"
    h_row, k1, d_row, h2, k2 = "pprPPRR", "prrPRpRR", "prPB", "pbPRR", "bbRpRR"
    y_row = reduce_word("pp" + "prPPPRpppR" + "PP")
    first, second = "PP" + m_word, "PP" + m_word + m_word
    assert reduce_word("PP" + m_word + m_word + "PQ") == c_row
    defects = tuple(reduce_word(left + invert(right)) for left, right in (
        (b_row, c_row), (y_row, k1), (h_row, h2), (k1, k2),
    ))
    products = tuple(map(reduce_word, (
        first + a_row + invert(first) + second + a_row + invert(second),
        "p" + h_row + "P" + k1 + invert(h_row) + invert(k1),
        "p" + d_row + "P", d_row + "b" + d_row + "B",
    )))
    assert defects == products
    decision = decide_squaring_hnn_target()
    assert decision.donor_defects == defects
    assert decision.donor_products == products


def test_squaring_hnn_basis_conjugations_and_killer_orientation_are_literal():
    decision = decide_squaring_hnn_target()
    words = dict(decision.stage_words)
    images = {"p": "p", "P": "P", "q": "rPPP", "Q": "pppR"}
    assert reduce_word("".join(images[letter] for letter in "PPPQQpq")) == "RpppRprPPP"
    assert reduce_word("".join(images[letter] for letter in "PPqpppqppQ")) == "PPrrppR"
    assert reduce_word("pp" + invert("PPrrppR") + "PP") == words["H"] == "pprPPRR"
    assert reduce_word(invert("RpppR") + "RpppRprPPP" + "RpppR") == words["K"] == "prPPPRpppR"
    assert reduce_word("pp" + words["K"] + "PP") == words["Y"]
    assert reduce_word("RR" + "bbRpRR" + "rr") == words["J"] == "RRbbRp"
    rename = str.maketrans("pPrRbB", "tTaAbB")
    assert tuple(row.translate(rename) for row in ("prPB", "pbPRR", "RRbbRp")) == decision.final_tuple
    assert decision.final_tuple == ("taTB", "tbTAA", "AAbbAt")
    assert decision.phi_images == ("b", "aa")
    assert decision.final_tuple[2] == decision.killer_prefix + "t"
    assert decision.killer_prefix == "AAbbA"
    assert decision.killer_prefix != invert("AAbbA")


def test_constructive_length_fourteen_has_independent_outer_donor_expansion():
    decision = decide_constructive_length_fourteen()
    h_word, q_word = "qqPq", "QpQPPqpqPqpqqPq"
    assert q_word.count("p") - q_word.count("P") == -1
    assert all(image(letter).count("p") == image(letter).count("P") for letter in "pq")
    assert image(h_word) == "pqPqpqqPq"
    w_word = reduce_word(h_word + q_word + invert(image(h_word)))
    assert w_word == "qPPq"
    assert dict(decision.inputs) == {"h": h_word, "Q": q_word, "phi_h": "pqPqpqqPq", "W": w_word}
    inverse_h = invert(h_word)
    prefix, pins = "", []
    for letter in inverse_h:
        sign = 1 if letter.islower() else -1
        pins.append((1 if letter.lower() == "p" else 2, sign,
                     image(prefix + (letter if sign == -1 else ""))))
        prefix += letter
    assert len(pins) == 4
    assert tuple(pins) == ((2, -1, "QpQP"), (1, 1, "QpQP"),
                           (2, -1, "QpQQP"), (2, -1, "QpQQPQpQP"))
    assert tuple((factor.row, factor.sign, factor.conjugator) for factor in decision.factors) == tuple(pins)
    outer = reduce_word(h_word + q_word)
    conjugated = reduce_word(h_word + q_word + "x" + invert(h_word))
    corrected = w_word + "x"
    defect = reduce_word(conjugated + invert(corrected))
    assert reduce_word(outer + expanded(decision.factors) + invert(outer)) == defect
    assert decision.outer_conjugator == outer
    assert decision.conjugated_killer == conjugated
    assert decision.corrected_killer == corrected
    assert decision.defect == decision.expanded_defect == defect
    corrupted = (replace(decision.factors[0], sign=-decision.factors[0].sign),) + decision.factors[1:]
    assert reduce_word(outer + expanded(corrupted) + invert(outer)) != defect


def test_constructive_length_fourteen_stable_elimination_and_moves_are_literal():
    decision = decide_constructive_length_fourteen()

    def substitute(word, images):
        signed = images | {letter.upper(): invert(value) for letter, value in images.items()}
        return reduce_word("".join(signed[letter] for letter in word))

    corrected = "qPPqx"
    images = {"p": "p", "q": "q", "x": invert("qPPq") + "x"}
    transformed = tuple(substitute(row, images) for row in ("xpXQ", "xqXQpQP", corrected))
    assert transformed == decision.transformed_rows
    assert transformed[2] == "x"
    base = tuple(substitute(row, {"p": "p", "q": "q", "x": ""}) for row in transformed[:2])
    assert base == decision.base_pair == ("QppQpqPP", "QppqPQP")
    b_inverse = invert(base[1])
    rotated = (base[0][6:] + base[0][:6], b_inverse[4:] + b_inverse[:4])
    assert rotated == decision.rotated_pair == ("PPQppQpq", "PPqpqpQ")
    a_row, b_row = rotated
    raw_product = a_row[1:] + a_row[:1] + b_row[4:] + b_row[:4]
    assert reduce_word(raw_product) == decision.product == "PQppQpqPqpQPPqp"
    conjugated = reduce_word("PPqp" + decision.product + invert("PPqp"))
    assert conjugated == decision.conjugated_product == "QpqPqpQ"
    negative = invert(conjugated)
    final = (b_row, negative[1:] + negative[:1])
    assert final == decision.final_pair == ("PPqpqpQ", "PQpQPqq")
    assert sum(map(len, final)) == 14
    assert decision.verdict == "CONSTRUCTIVE_LENGTH_FOURTEEN_TARGET_ONLY"


def test_squaring_norm_keeps_literal_cyclic_boundary_and_positive_control():
    def psi(word):
        images = {"a": "b", "A": "B", "b": "aa", "B": "AA"}
        return reduce_word("".join(images[letter] for letter in word))

    def norm(word):
        return reduce_word(word + psi(word))

    target = "AAbbA"
    assert norm(target) == "AAbbABBaaaaB"
    assert norm(target)[0] != norm(target)[-1].swapcase()
    assert {letter.lower() for letter in norm(target)} == {"a", "b"}
    for letter in "aAbB":
        assert psi(psi(letter)) == letter * 2
    conjugator = "ab"
    positive = reduce_word(conjugator + invert(psi(conjugator)))
    assert positive == "abAAB"
    assert reduce_word(invert(conjugator) + positive + psi(conjugator)) == ""
    assert norm(positive) == "aBAA"
    assert norm(positive)[0] == norm(positive)[-1].swapcase()
    assert norm(positive)[1:-1] == "BA"
