STANDARD_A = "xxxYYYY"
STANDARD_B = "xyxYXY"


def inverse(word):
    return word[::-1].swapcase()


def cyclic_starts(word):
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def periodic_prefix(word, length):
    return "".join(word[index % len(word)] for index in range(length))


def common_prefix_length(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right))


def test_periodic_axis_overlap_and_alternating_triple_controls():
    a_starts = cyclic_starts(STANDARD_A) + cyclic_starts(inverse(STANDARD_A))
    b_starts = cyclic_starts(STANDARD_B) + cyclic_starts(inverse(STANDARD_B))
    overlaps = [common_prefix_length(periodic_prefix(a, 14), periodic_prefix(b, 14))
                for a in a_starts for b in b_starts]
    assert max(overlaps) == 2
    for start in a_starts:
        names = periodic_prefix(start, 3).lower()
        assert not (names[0] != names[1] and names[1] != names[2])
    for start in b_starts:
        names = periodic_prefix(start, 3).lower()
        assert names[0] != names[1] and names[1] != names[2]
    assert common_prefix_length(periodic_prefix(STANDARD_A, 14), periodic_prefix(STANDARD_A, 14)) == 14


def test_short_contiguous_cyclic_deletions_leave_both_a_generator_types():
    for oriented, required in ((STANDARD_A, {"x", "Y"}), (inverse(STANDARD_A), {"X", "y"})):
        for start in cyclic_starts(oriented):
            for length in (0, 1, 2):
                remainder = start[length:]
                assert required <= set(remainder)
                assert set(remainder) <= required
    assert set(STANDARD_A) <= {"x", "Y"}
    assert not (set(STANDARD_A) & {"X", "y"})


def test_short_contiguous_cyclic_deletions_cannot_make_b_sign_coherent():
    for oriented in (STANDARD_B, inverse(STANDARD_B)):
        for start in cyclic_starts(oriented):
            for length in (0, 1, 2):
                remainder = start[length:]
                assert not set(remainder) <= {"x", "Y"}
                assert not set(remainder) <= {"X", "y"}
