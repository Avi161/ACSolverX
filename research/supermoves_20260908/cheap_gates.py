"""Low-overhead admission gates for already canonical two-relator states."""

from functools import lru_cache


LETTERS = "xXyY"


def inv(word):
    return word[::-1].swapcase()


@lru_cache(maxsize=None)
def _bs_patterns_for_length(length):
    """Map canonical donor strings to recognizer-order candidate tuples.

    The caller supplies canon_pair output, so the table intentionally keys the
    exact canonical representation used by consecutive_bs._recognize.
    """
    if length < 5 or length % 2 != 1:
        return {}
    from experiments.equivalence_classes.lib.words import canon_rel

    m = (length - 3) // 2
    n = m + 1
    table = {}
    for a in LETTERS:
        for b in LETTERS:
            if a.lower() == b.lower():
                continue
            relation = inv(b) + a * m + b + inv(a) * n
            table.setdefault(canon_rel(relation), []).append((a, b, relation, m, n))
    return table


def bs_gate(pair, general=False):
    """Return consecutive_bs._recognize's tuple, or None, for a canonical pair.

    With general=False only BS(1,2) is admitted. With general=True the donor
    length chooses the consecutive pair (m,m+1), exactly as the current
    consecutive_bs._recognize implementation does. The companion is scanned
    only after a cached donor-pattern lookup hits.
    """
    if len(pair) != 2:
        raise ValueError("expected a pair")
    for donor_index, donor in enumerate(pair):
        if not isinstance(donor, str):
            raise ValueError("expected words")
        if not general and len(donor) != 5:
            continue
        patterns = _bs_patterns_for_length(len(donor)).get(donor)
        if not patterns:
            continue
        companion = pair[1 - donor_index]
        if not isinstance(companion, str):
            raise ValueError("expected words")
        for a, b, relation, m, n in patterns:
            exponent = companion.count(b) - companion.count(inv(b))
            if abs(exponent) == 1:
                return a, b, relation, inv(companion) if exponent == 1 else companion, m, n
    return None


def _freely_and_cyclically_reduce(word):
    stack = []
    for letter in word:
        if letter not in LETTERS:
            raise ValueError("words must use xXyY")
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    start, stop = 0, len(stack)
    while stop - start >= 2 and stack[start] == stack[stop - 1].swapcase():
        start += 1
        stop -= 1
    return "".join(stack[start:stop])


def _is_rotation(word, candidate):
    """Linear KMP test for candidate as a rotation of word."""
    if len(word) != len(candidate):
        return False
    if not word:
        return True
    pattern = candidate
    failure = [0] * len(pattern)
    matched = 0
    for index in range(1, len(pattern)):
        while matched and pattern[index] != pattern[matched]:
            matched = failure[matched - 1]
        if pattern[index] == pattern[matched]:
            matched += 1
            failure[index] = matched
    matched = 0
    for index, letter in enumerate(word + word[:-1]):
        while matched and letter != pattern[matched]:
            matched = failure[matched - 1]
        if letter == pattern[matched]:
            matched += 1
            if matched == len(pattern):
                return index - len(pattern) + 1 < len(word)
    return False


def _two_block_row(word):
    reduced = _freely_and_cyclically_reduce(word)
    m = reduced.count("x") - reduced.count("X")
    n = reduced.count("y") - reduced.count("Y")
    candidate = ("x" if m >= 0 else "X") * abs(m) + ("y" if n >= 0 else "Y") * abs(n)
    return (m, n) if _is_rotation(reduced, candidate) else None


def two_block_gate(pair):
    """True exactly when two_block.recognize accepts both words with det +/-1.

    It does no certificate construction. Canonical callers already account for
    rotations/inverses; this also retains the recognizer's own cyclic handling
    so direct comparisons remain exact.
    """
    if len(pair) != 2:
        raise ValueError("expected a pair")
    first = _two_block_row(pair[0])
    second = _two_block_row(pair[1])
    if first is None or second is None:
        return False
    return abs(first[0] * second[1] - first[1] * second[0]) == 1


@lru_cache(maxsize=16384)
def _canonical_two_block_row(word):
    if not word:
        return 0, 0
    changes = 0
    previous = word[-1]
    for letter in word:
        if letter != previous:
            changes += 1
            if changes > 2:
                return None
        previous = letter
    m = word.count('x') - word.count('X')
    n = word.count('y') - word.count('Y')
    return (m, n) if abs(m) + abs(n) == len(word) else None


def canonical_two_block_gate(pair):
    """Exact two-block gate on validated freely/cyclically reduced words.

    A two-block cyclic word has zero or two letter changes. Three changes
    already disprove membership, so most search children need only a prefix.
    """
    first = _canonical_two_block_row(pair[0])
    if first is None:
        return False
    second = _canonical_two_block_row(pair[1])
    return second is not None and abs(first[0] * second[1] - first[1] * second[0]) == 1


@lru_cache(maxsize=16384)
def one_occurrence_donor(word):
    lower = word.lower()
    return lower.count('x') == 1 or lower.count('y') == 1
