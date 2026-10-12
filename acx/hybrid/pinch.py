"""Syllable arithmetic of the pinch cascade (stage C): reading a cyclic word as syllables, the four rewriting rules and the
exponent-level dry run that decides for free whether the cascade can finish a companion relator."""
from functools import lru_cache


def syllables(w):
    """Cyclic syllables ``[(generator, signed exponent)]``, the seam merged."""
    out, run, n = [], 0, 0
    for g in w:
        if g == run:
            n += 1
            continue
        if run:
            out.append((abs(run), n if run > 0 else -n))
        run, n = g, 1
    if run:
        out.append((abs(run), n if run > 0 else -n))
    if len(out) > 1 and out[0][0] == out[-1][0]:
        out[0] = (out[0][0], out[0][1] + out.pop()[1])
    return out


def from_syllables(syl):
    """The word with the syllables ``[(generator, signed exponent)]``."""
    return sum((((g if e > 0 else -g),) * abs(e) for g, e in syl), ())


@lru_cache(maxsize=1 << 16)
def conjugation_forms(w):
    """Every reading of the cyclic word as ``g^a h^p g^-a h^q`` with ``a > 0`` and ``p, q != 0``."""
    syl = syllables(w)
    if len(syl) != 4:
        return ()
    forms = []
    for off in range(4):
        (g, a), (h, p), (g2, b), (h2, q) = (syl[(off + t) % 4] for t in range(4))
        if g == g2 and h == h2 and a > 0 and a + b == 0:
            forms.append((g, a, h, p, q))
    return tuple(forms)


def bracket(syl, g, a, p, q):
    """First cyclically adjacent pair of ``g``-syllables ``(e1, m, e2)`` of opposite sign, both of size at
    least ``a``, whose enclosed ``h``-exponent ``m`` is a multiple of ``p`` (``e1 > 0``) or ``q`` (``e1 < 0``)."""
    n = len(syl)
    for i in range(n):
        if syl[i][0] != g:
            continue
        j = (i + 2) % n
        if n < 4 or syl[j][0] != g or syl[(i + 1) % n][0] == g:
            continue
        e1, m, e2 = syl[i][1], syl[(i + 1) % n][1], syl[j][1]
        if e1 * e2 >= 0 or abs(e1) < a or abs(e2) < a:
            continue
        d = p if e1 > 0 else q
        if m % d == 0:
            return i, d
    return None


def merge_syllables(syl):
    """``syl`` with equal neighbouring generators joined (the seam too) and zero exponents dropped."""
    out = []
    for g, e in syl:
        if e == 0:
            continue
        if out and out[-1][0] == g:
            out[-1] = (g, out[-1][1] + e)
            if out[-1][1] == 0:
                out.pop()
        else:
            out.append((g, e))
    while len(out) > 1 and out[0][0] == out[-1][0]:
        out[0] = (out[0][0], out[0][1] + out.pop()[1])
        if out[0][1] == 0:
            out.pop(0)
    return out


def pinch_once(syl, i, g, a, h, p, q):
    """One rule use on the bracket at syllable ``i``: the new syllables and the replacement, as ``(position in the word read
    from syllable i, lhs, rhs)`` with lhs and rhs given as syllables."""
    n = len(syl)
    e1, m, e2 = syl[i][1], syl[(i + 1) % n][1], syl[(i + 2) % n][1]
    if e1 > 0:
        left = (m > 0) == (p > 0)
        if left:
            mid = [(g, e1 - a), (h, -q), (g, a), (h, m - p)]
            rw = e1 - a, [(g, a), (h, p)], [(h, -q), (g, a)]
        else:
            mid = [(g, e1), (h, m + p), (g, -a), (h, q), (g, e2 + a)]
            rw = e1 + abs(m) - abs(p), [(h, -p), (g, -a)], [(g, -a), (h, q)]
    else:
        left = (m > 0) == (q < 0)
        if left:
            mid = [(g, e1 + a), (h, p), (g, -a), (h, m + q)]
            rw = -e1 - a, [(g, -a), (h, -q)], [(h, p), (g, -a)]
        else:
            mid = [(g, e1), (h, m - q), (g, a), (h, -p), (g, e2 - a)]
            rw = -e1 + abs(m) - abs(q), [(h, q), (g, a)], [(g, a), (h, -p)]
    rest = [syl[(i + k) % n] for k in range(2 if left else 3, n)]
    return (merge_syllables(mid + rest),) + rw


@lru_cache(maxsize=1 << 16)
def pinch_preflight(form, companion, max_rules=400):
    """Dry run of the cascade on syllables: the number of rule uses when the companion ends primitive."""
    g, a, h, p, q = form
    syl = syllables(companion)
    rules = 0
    while sum(1 for s in syl if s[0] == g) > 1:
        b = bracket(syl, g, a, p, q)
        if b is None:
            return None
        syl = pinch_once(syl, b[0], g, a, h, p, q)[0]
        rules += 1
        if rules > max_rules:
            return None
    if len(syl) == 2 and (abs(syl[0][1]) == 1 or abs(syl[1][1]) == 1):
        return rules
    if len(syl) == 1 and abs(syl[0][1]) == 1:
        return rules
    return None
