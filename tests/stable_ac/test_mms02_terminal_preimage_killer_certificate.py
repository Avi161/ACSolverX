from dataclasses import replace

from experiments.stable_ac.mms02_terminal_preimage_killer_certificate import (
    EXPECTED_BASE_PAIR, EXPECTED_PRODUCT_MINIMUM, PINNED_FACTOR_PREFIXES,
    PINNED_TRANSITIONS, decide_preimage_killer, replay_cyclic_continuation,
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
