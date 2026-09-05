from dataclasses import replace

from experiments.stable_ac.mms02_boundary_automorphism_corridor_certificate import (
    PINNED_FACTORS, decide_boundary_automorphism_corridor, shifted_h_factors,
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
