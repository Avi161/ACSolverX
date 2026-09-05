from experiments.stable_ac.mms02_depth_five_lift_equations_certificate import (
    EXPECTED_COLLAPSED_ENDPOINTS,
    R_STAR,
)


def inverse(word):
    return word[::-1].swapcase()


def reduce_word(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def substitute(word, images):
    signed = images | {letter.upper(): inverse(value) for letter, value in images.items()}
    return reduce_word("".join(signed[letter] for letter in word))


def test_six_three_schubert_relator_and_inverse_basis_are_literal():
    assert R_STAR == "YZYzYzYZyzyZYzYzYZYzyZyZyz"
    forward, backward = {"y": "A", "z": "AAB"}, {"a": "Y", "b": "Zyy"}
    for generator in "yz":
        assert substitute(substitute(generator, forward), backward) == generator
    for generator in "ab":
        assert substitute(substitute(generator, backward), forward) == generator
    p, q = 5, 13
    epsilon = tuple(1 if (index * p // q) % 2 == 0 else -1 for index in range(1, q))
    assert epsilon == (1, 1, -1, -1, -1, 1, 1, -1, -1, -1, 1, 1)
    w_word = "".join(("b" if index % 2 == 0 else "a") if sign == 1
                     else ("B" if index % 2 == 0 else "A")
                     for index, sign in enumerate(epsilon))
    assert w_word == "baBABabABAba"
    relator = reduce_word("a" + w_word + "B" + inverse(w_word))
    assert relator == "abaBABabABAbaBABabaBAbabAB"
    assert substitute(R_STAR, forward) == relator
    assert substitute(relator, backward) == R_STAR
    corrupted_w = w_word[0].swapcase() + w_word[1:]
    assert reduce_word("a" + corrupted_w + "B" + inverse(corrupted_w)) != relator
    assert substitute(R_STAR, {"y": "A", "z": "AB"}) != relator


def test_six_three_endpoint_images_and_trefoil_control_are_literal():
    raw_endpoints = ("zyZyzYZYzyZyZyzyZ", "zYZyzYZYzYzYZyzyZ")
    mapped_endpoints = ("AABAbABabaBAbabABAbaa", "AABabABabaBABabABAbaa")
    assert EXPECTED_COLLAPSED_ENDPOINTS == raw_endpoints
    forward, backward = {"y": "A", "z": "AAB"}, {"a": "Y", "b": "Zyy"}
    assert tuple(substitute(word, forward) for word in raw_endpoints) == mapped_endpoints
    assert tuple(substitute(word, backward) for word in mapped_endpoints) == raw_endpoints
    p, q = 1, 3
    epsilon = tuple(1 if (index * p // q) % 2 == 0 else -1 for index in range(1, q))
    assert epsilon == (1, 1)
    w_word = "".join(("b" if index % 2 == 0 else "a") if sign == 1
                     else ("B" if index % 2 == 0 else "A")
                     for index, sign in enumerate(epsilon))
    assert reduce_word("a" + w_word + "B" + inverse(w_word)) == "abaBAB"
