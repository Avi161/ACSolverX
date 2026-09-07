"""Literal data and interval controls for the fixed minimal conjugacy pair.

The ambient Whitehead normalization is an algebraic certificate, not an AC path.
"""

from collections import Counter
from pathlib import Path
from runpy import run_path


WORDS = ("XXYYXyxYxy", "XYXYXyxYxyy")


def free_reduce(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def canonical_pair(words):
    representatives = []
    for word in words:
        word = free_reduce(word)
        while len(word) > 1 and word[0] == word[-1].swapcase():
            word = word[1:-1]
        representatives.append(min(
            oriented[index:] + oriented[:index]
            for oriented in (word, word[::-1].swapcase())
            for index in range(len(oriented))
        ))
    return tuple(sorted(representatives))


def test_actual_quotient_has_saved_minimal_algebraic_normalization():
    source = ("xzYXyxZXYxyZ", "XyxZXYXyxzXYxy")
    quotient_images = {"x": "x", "y": "y", "z": "Yx"}
    quotient = tuple(free_reduce("".join(
        quotient_images[letter.lower()] if letter.islower()
        else quotient_images[letter.lower()][::-1].swapcase()
        for letter in word
    )) for word in source)
    assert quotient == ("xYxYXyyXYxyXy", "XyyXYXyxYYxy")
    current = canonical_pair(quotient)
    for images in ({"x": "xy", "y": "y"}, {"x": "x", "y": "xy"}):
        current = canonical_pair(tuple("".join(
            images[letter.lower()] if letter.islower()
            else images[letter.lower()][::-1].swapcase()
            for letter in word
        ) for word in current))
    assert current == WORDS
    assert sum(map(len, WORDS)) == 21
    saved = run_path(str(Path(__file__).with_name("test_ak3_mms02_relation_lift_certificate.py")))
    automorphisms = saved["rank_two_whitehead_automorphisms"]()
    assert len(automorphisms) == 12
    for images in automorphisms:
        transformed = canonical_pair(tuple("".join(
            images[letter.lower()] if letter.islower()
            else images[letter.lower()][::-1].swapcase()
            for letter in word
        ) for word in WORDS))
        assert sum(map(len, transformed)) >= 21


def test_occurrence_darts_independently_verify_seven_corner_cells():
    direct_corners = []
    direct_weights = Counter()
    for word in WORDS:
        for index, letter in enumerate(word):
            previous, following = word[index - 1], word[(index + 1) % len(word)]
            direct_weights[frozenset((letter.swapcase(), following))] += 1
            if letter == "y":
                direct_corners.append((previous.swapcase(), following))
            elif letter == "Y":
                direct_corners.append((following, previous.swapcase()))

    a_matching, b_matching, germs = {}, {}, {}
    offset = 0
    for word in WORDS:
        for index, letter in enumerate(word):
            departure = 2 * (offset + index)
            arrival = departure + 1
            germs[departure], germs[arrival] = letter, letter.swapcase()
            b_matching[departure], b_matching[arrival] = arrival, departure
            next_departure = 2 * (offset + (index + 1) % len(word))
            a_matching[arrival], a_matching[next_departure] = next_departure, arrival
        offset += len(word)
    assert len(germs) == 42
    assert all(a_matching[a_matching[dart]] == dart != a_matching[dart] for dart in germs)
    assert all(b_matching[b_matching[dart]] == dart != b_matching[dart] for dart in germs)
    dart_corners = [
        (germs[a_matching[dart]], germs[a_matching[b_matching[dart]]])
        for dart in sorted(germs) if germs[dart] == "y"
    ]
    assert dart_corners == direct_corners
    assert len(direct_corners) == 11
    counts = Counter(dart_corners)
    assert [[counts[row, column] for column in ("x", "X", "y")]
            for row in ("x", "X", "Y")] == [[2, 2, 0], [2, 1, 2], [1, 1, 0]]
    assert len(counts) == 7
    dart_weights = Counter(
        frozenset((germs[dart], germs[mate]))
        for dart, mate in a_matching.items() if dart < mate
    )
    assert dart_weights == direct_weights == Counter({
        frozenset("xX"): 1, frozenset("yY"): 2,
        frozenset("xy"): 4, frozenset("xY"): 5,
        frozenset("Xy"): 5, frozenset("XY"): 4,
    })
    assert Counter(germs.values()) == {"x": 10, "X": 10, "y": 11, "Y": 11}
    assert {vertex: sum(weight for edge, weight in dart_weights.items() if vertex in edge)
            for vertex in "xXyY"} == {"x": 10, "X": 10, "y": 11, "Y": 11}


def test_three_cyclic_blocks_have_six_cell_control_and_noninterval_negative():
    positive = "AAAABBBBCCCC"
    base_negative = "aaaabbbbcccc"
    for oriented in (base_negative, base_negative[::-1]):
        for cut in range(len(oriented)):
            negative = oriented[cut:] + oriented[:cut]
            assert sum(label != positive[index - 1] for index, label in enumerate(positive)) == 3
            assert sum(label != negative[index - 1] for index, label in enumerate(negative)) == 3
            assert len(set(zip(positive, negative))) <= 6
    artificial_positive = "AAAABBBBBCC"
    artificial_negative = "aabbaabccab"
    assert len(artificial_positive) == len(artificial_negative) == 11
    assert len(set(zip(artificial_positive, artificial_negative))) == 7
    assert sum(label != artificial_positive[index - 1]
               for index, label in enumerate(artificial_positive)) == 3
    assert sum(label != artificial_negative[index - 1]
               for index, label in enumerate(artificial_negative)) > 3


def test_shared_subword_multiplication_returns_to_ak3():
    """Replay the specified return to AK3, not a trivialization."""
    def inverse(word):
        return word[::-1].swapcase()

    def substitute(word, images):
        return free_reduce("".join(
            images[letter.lower()] if letter.islower() else inverse(images[letter.lower()])
            for letter in word
        ))

    def conjugate(word, prefix):
        return free_reduce(prefix + word + inverse(prefix))

    w1, w2 = WORDS
    second_prime = conjugate(w2, "y")
    s = free_reduce(second_prime + inverse(w1))
    assert s == "yXYXyxx"
    forward = {"x": "x", "y": "zX"}
    backward = {"x": "x", "z": "yx"}
    for generator in "xy":
        assert substitute(substitute(generator, forward), backward) == generator
    for generator in "xz":
        assert substitute(substitute(generator, backward), forward) == generator
    u = substitute(w1, forward)
    assert u == "XZxZXzxZxzX"
    donor = conjugate(inverse(substitute(s, forward)), "zx")
    assert donor == "xzxZXZ"
    d = "xzx"
    old = conjugate(u, d)
    assert old == "xxZXzxZxzXXZX"
    rows = (old, donor)
    for before, after, c, expected in (
        ("Xzx", "zxZ", "X", "xxxZZxzXXZX"),
        ("xzX", "Zxz", "Z", "xxxZZZxzXZX"),
        ("xzX", "Zxz", "Z", "xxxZZZZ"),
    ):
        assert free_reduce(before + inverse(after)) == conjugate(inverse(donor), c)
        index = rows[0].index(before)
        prefix = rows[0][:index]
        rewritten = free_reduce(prefix + after + rows[0][index + len(before):])
        assert rewritten == expected
        donation_prefix = free_reduce(prefix + c)
        donated = free_reduce(conjugate(rows[1], donation_prefix) + rows[0])
        assert donated == rewritten
        rows = (donated, rows[1])
        assert rows[1] == donor
    assert rows == ("xxxZZZZ", "xzxZXZ")
