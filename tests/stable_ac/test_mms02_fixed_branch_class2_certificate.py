from experiments.stable_ac.mms02_fixed_branch_class2_certificate import (
    EXPECTED_A_WEDGE,
    EXPECTED_B_WEDGE,
    EXPECTED_D_VECTOR,
    EXPECTED_D_WEDGE,
    EXPECTED_RESIDUAL,
    EXPECTED_T_VECTOR,
    construct_raw_fixed_branch_class_two_witness,
    decide_fixed_branch_class_two,
)


def reduce_word(word: str) -> str:
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def test_fixed_commutator_substitutions_solve_the_second_equation() -> None:
    commutator_u_v = "uvUV"
    commutator_v_u_inverse = "vUVu"
    conjugated = "U" + commutator_u_v + "u"
    assert reduce_word(commutator_v_u_inverse) == reduce_word(conjugated)


def test_canonical_branch_has_an_integral_class_two_obstruction() -> None:
    decision = decide_fixed_branch_class_two()
    assert decision.endpoint_wedges == (EXPECTED_A_WEDGE, EXPECTED_B_WEDGE)
    assert decision.twisted_source_vector == EXPECTED_D_VECTOR
    assert decision.twisted_source_wedge == EXPECTED_D_WEDGE
    assert decision.forced_conjugator_vector == EXPECTED_T_VECTOR
    assert decision.central_residual == EXPECTED_RESIDUAL
    assert decision.image_invariant_values == (0, 0, 0, 0, 0, 0)
    assert decision.residual_invariant == 8
    assert (
        decision.verdict
        == "CANONICAL_G_V_H_X_J_U_INVERSE_BRANCH_OBSTRUCTED_IN_BASE_CLASS_TWO"
    )


def test_raw_fixed_branch_arbitrary_h_has_a_class_two_solution() -> None:
    witness = construct_raw_fixed_branch_class_two_witness()
    assert witness.h_height == -1
    assert witness.transported_endpoint_coordinate == witness.target_coordinate
    assert witness.dropped_conjugation_invariant == 2
    assert witness.conjugator_word_length == 947
    assert witness.literal_endpoint_defect_length == 5806
    assert (
        witness.verdict
        == "RAW_FIXED_G_V_J_U_INVERSE_FAMILY_HAS_A_BASE_CLASS_TWO_SOLUTION"
    )


def test_literal_class_two_seed_strips_back_to_its_unsolved_source() -> None:
    from experiments.stable_ac import mms02_fixed_branch_class2_certificate as source

    def encode(word):
        return "".join("abcd"[index + 2] if sign == 1 else "ABCD"[index + 2]
                       for index, sign in word)

    invert = lambda word: word[::-1].swapcase()
    images = {"abcd"[index + 2]: encode(word) for index, word in source.PHI_IMAGES.items()}

    def phi(word):
        return reduce_word("".join(images[letter] if letter.islower()
                                   else invert(images[letter.lower()]) for letter in word))

    a, target = map(encode, source.EXPECTED_ENDPOINT_BASE_WORDS)
    sharp = phi(a)
    commutator = reduce_word(sharp + phi(target) + phi(invert(sharp)) + invert(target))
    s_word = "aa" + "B" * 5 + "c" * 8 + "D"
    original_source = reduce_word(sharp + phi(s_word) + commutator + invert(phi(s_word)))
    conjugator = encode(source.realize_class_two_coordinate(
        (source.EXPECTED_T_VECTOR, source.EXPECTED_RAW_FIXED_T_WEDGE)))
    endpoint = reduce_word(conjugator + original_source + invert(phi(conjugator)))
    assert (len(conjugator), len(endpoint), len(original_source), len(target)) == (947, 5796, 179, 10)
    for _ in range(947):
        letter = invert(conjugator[0])
        shorter = reduce_word(letter + endpoint + invert(phi(letter)))
        assert len(shorter) < len(endpoint)
        conjugator = reduce_word(letter + conjugator)
        endpoint = shorter
    assert conjugator == ""
    assert endpoint == original_source != target
    assert len(reduce_word(invert(target) + endpoint)) == 189
    assert all(len(reduce_word(letter + endpoint + invert(phi(letter)))) >= len(endpoint)
               for letter in "aAbBcCdD")
