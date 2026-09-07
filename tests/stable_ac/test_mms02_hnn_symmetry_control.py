"""Literal HNN symmetry and defining-elimination controls, without a search."""


def reduce_word(*words):
    stack = []
    for word in words:
        for letter in word:
            if stack and stack[-1] == letter.swapcase():
                stack.pop()
            else:
                stack.append(letter)
    return "".join(stack)


def inverse(word):
    return word[::-1].swapcase()


def substitute(word, images):
    return reduce_word(*(images[letter.lower()] if letter.islower()
                         else inverse(images[letter.lower()]) for letter in word))


def conjugate(word, prefix):
    return reduce_word(prefix, word, inverse(prefix))


SIGMA = {"a": "Ab", "b": "b", "x": "baBx"}
SIGMA_INVERSE = {"a": "bA", "b": "b", "x": "baBBx"}
PHI = {"a": "b", "b": "bbAbaB"}
ALPHA = {"a": "Ab", "b": "b"}
Z = "baB"
R1 = "xaXB"
R2 = reduce_word("xbX", inverse(PHI["b"]))
S = "XbAB"


def test_literal_hnn_symmetry_has_inverse_and_intertwines_monodromy():
    assert substitute("X", SIGMA) == S
    for generator in "abx":
        assert substitute(substitute(generator, SIGMA), SIGMA_INVERSE) == generator
        assert substitute(substitute(generator, SIGMA_INVERSE), SIGMA) == generator
    for generator in "ab":
        assert substitute(PHI[generator], ALPHA) == conjugate(substitute(ALPHA[generator], PHI), Z)
    assert substitute(R1, SIGMA) == conjugate(reduce_word(inverse(R1), R2), reduce_word(Z, "B"))
    assert substitute(R2, SIGMA) == conjugate(R2, Z)


def test_symmetry_relators_restore_with_unchanged_killer_donor():
    rows = (substitute(R1, SIGMA), substitute(R2, SIGMA), S)
    rows = (rows[0], conjugate(rows[1], inverse(Z)), rows[2])
    assert rows[1:] == (R2, S)
    rows = (conjugate(rows[0], inverse(reduce_word(Z, "B"))), rows[1], rows[2])
    assert rows == (reduce_word(inverse(R1), R2), R2, S)
    rows = (reduce_word(rows[0], inverse(rows[1])), rows[1], rows[2])
    assert rows == (inverse(R1), R2, S)
    rows = (inverse(rows[0]), rows[1], rows[2])
    assert rows == (R1, R2, S)


def test_defining_elimination_and_literal_wrong_target_control():
    """Check substitutions; do not present variable elimination as an AC replay."""
    elimination = {"a": "a", "b": "b", "x": "bAB"}
    assert substitute(S, elimination) == ""
    assert substitute(R2, elimination) == "B"
    assert substitute(substitute(R1, elimination), {"a": "a", "b": ""}) == "a"
    target = "abX"
    assert substitute(target, elimination) != ""
