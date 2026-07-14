"""z-word family builders for the Branch-A (No-CoV) sweep.

Pure Python: no numba, no import from ``solvern``. Words and relators are plain
strings over a generator alphabet like ``"xXyY"`` -- lowercase = generator,
uppercase = its inverse (same convention as the rest of the repo). Every
builder derives its alphabet from the input relators, so the same code runs
unchanged on a 2-, 3- or n-generator presentation.

Words here are NOT cyclically reduced -- they are words appended as a new
generator's defining relator (``z^-1 w``), not relators themselves, so only
free reduction applies.
"""

import math

A1_DEFAULT_WORDS = ("x", "y", "X", "Y", "xy", "xY", "Xy", "XY", "yx", "yX",
                     "xyx", "yxy", "xyX", "yxY", "xxy", "xyy")


def free_reduce_str(s):
    """Cancel adjacent inverse pairs to a fixpoint. A stack pass does this in one go."""
    stack = []
    for c in s:
        if stack and stack[-1] == c.swapcase():
            stack.pop()
        else:
            stack.append(c)
    return "".join(stack)


def _alphabet(relators):
    return {c.lower() for r in relators for c in r}


def _rotate(s, k):
    return s[k:] + s[:k]


def _dedup(words):
    out = []
    for w in words:
        if w not in out:
            out.append(w)
    return out


def _evenly_spaced(items, k):
    """k items evenly spaced over the range, endpoints included. Assumes len(items) > k."""
    n = len(items)
    if k <= 0:
        return []
    if k == 1:
        return [items[(n - 1) // 2]]
    idxs = []
    for i in range(k):
        j = round(i * (n - 1) / (k - 1))
        while j in idxs:            # only reachable when n is barely above k
            j += 1
        idxs.append(j)
    return [items[j] for j in sorted(idxs)]


def build_a1(relators, words=None):
    alphabet = _alphabet(relators)
    src = A1_DEFAULT_WORDS if words is None else words
    reduced = []
    for w in src:
        r = free_reduce_str(w)
        if not r:
            continue
        assert all(c.lower() in alphabet for c in r), \
            f"A1 word {r!r} uses a generator outside {sorted(alphabet)}"
        reduced.append(r)
    return _dedup(reduced)


def a2_raw_count(relators):
    """sum(len(r)**2) -- the candidate count build_a2 generates before reduction/dedup."""
    return sum(len(r) ** 2 for r in relators)


def build_a2(relators, max_words=None, drop_len1=False):
    out = []
    for r in relators:
        L = len(r)
        for k in range(L):
            rot = _rotate(r, k)
            for m in range(1, L + 1):
                w = free_reduce_str(rot[:m])
                if not w:
                    continue
                if drop_len1 and len(w) == 1:
                    continue
                out.append(w)
    out = _dedup(out)
    if max_words is not None and len(out) > max_words:
        out = _evenly_spaced(out, max_words)
    return out


def build_a3(relators, grid=(0.25, 0.5, 0.75, 1.0)):
    """Pairwise over the first two relators. Documented extension point for n > 2."""
    r1, r2 = relators[0], relators[1]
    out = []
    for p in grid:
        for q in grid:
            cut1 = math.ceil(p * len(r1))
            cut2 = math.ceil(q * len(r2))
            w = free_reduce_str(r1[:cut1] + r2[:cut2])
            if w:
                out.append(w)
    return _dedup(out)


def build_family(family, relators, cfg):
    if family == "A1":
        return build_a1(relators, cfg.get("A1_WORDS"))
    if family == "A2":
        return build_a2(relators, max_words=cfg.get("A2_MAX_WORDS"),
                         drop_len1=cfg.get("A2_DROP_LEN1", False))
    if family == "A3":
        return build_a3(relators, grid=cfg.get("A3_GRID", (0.25, 0.5, 0.75, 1.0)))
    raise ValueError(f"unknown word family: {family!r}")
