"""Compressed cyclic Britton reduction before constructing an AC certificate."""
from functools import lru_cache
from experiments.equivalence_classes.lib.words import canon_rel, inv


@lru_cache(maxsize=16384)
def donor_orientations(donor):
    if len(donor) < 5 or len(donor) % 2 == 0:
        return ()
    m = (len(donor) - 3) // 2
    found = []
    for a in 'xXyY':
        for b in 'xXyY':
            if a.lower() != b.lower():
                relation = inv(b) + a * m + b + inv(a) * (m + 1)
                if canon_rel(relation) == donor:
                    found.append((a, b, m, m + 1))
    return tuple(found)


def preflight(pair, max_bits=63):
    """Inspect a canonical pair, returning accept/reject/unknown, never a solve.

    An accepted pair still needs the ordinary certificate compiler and replay.
    Integer growth beyond max_bits returns unknown rather than risking a
    large allocation or declaring an obstruction.
    """
    scans = pinches = 0
    for index, donor in enumerate(pair):
        for a, b, m, n in donor_orientations(donor):
            word = pair[1 - index]
            if abs(word.count(b) - word.count(inv(b))) != 1:
                continue
            positions = [i for i, letter in enumerate(word) if letter.lower() == b.lower()]
            signs = [1 if word[i] == b else -1 for i in positions]
            powers = []
            for j, start in enumerate(positions):
                end = positions[(j + 1) % len(positions)]
                between = word[start + 1:end] if end > start else word[start + 1:] + word[:end]
                powers.append(between.count(a) - between.count(inv(a)))
            if any(abs(power).bit_length() > max_bits for power in powers):
                return {'status': 'unknown', 'scans': scans, 'pinches': pinches}
            while len(signs) > 1:
                chosen = None
                for first in (1, -1):
                    divisor, output = (n, m) if first == 1 else (m, n)
                    for i, sign in enumerate(signs):
                        scans += 1
                        if sign == first and signs[(i + 1) % len(signs)] == -first and powers[i] % divisor == 0:
                            chosen = i, divisor, output
                            break
                    if chosen is not None:
                        break
                if chosen is None:
                    return {'status': 'reject', 'scans': scans, 'pinches': pinches,
                            'stable_letters': len(signs)}
                i, divisor, output = chosen
                signs = signs[i:] + signs[:i]
                powers = powers[i:] + powers[:i]
                replacement = powers[0] // divisor * output
                merged = powers[-1] + replacement + powers[1]
                if max(abs(replacement).bit_length(), abs(merged).bit_length()) > max_bits:
                    return {'status': 'unknown', 'scans': scans, 'pinches': pinches}
                signs = signs[2:]
                powers = powers[2:-1] + [merged]
                pinches += 1
            return {'status': 'accept', 'scans': scans, 'pinches': pinches,
                    'stable_letters': 1, 'base_exponent': powers[0]}
    return {'status': 'reject', 'scans': scans, 'pinches': pinches,
            'reason': 'not_recognized'}
