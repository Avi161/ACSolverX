"""The word operations of a change of variables: put ``z`` for ``w``, isolate a generator."""
from ..core.words import inverse, reduce, rotate_left

X, Y, Z = 1, 2, 3       # letters (negative = inverse); Z is the new generator z = w(x, y)


def _inner_matches(word, w):
    """Non-overlapping occurrences of ``w`` / ``w^-1`` in the written ``word``, scanned left to right.

    Returns ``(hits, covered)``: ``hits[i]`` is ``Z`` or ``-Z`` for the match starting at ``i``, and
    ``covered[j]`` says position ``j`` lies inside a match.
    """
    n, m, w_inv = len(word), len(w), inverse(w)
    hits, covered, i = {}, [False] * n, 0
    while i + m <= n:
        window = word[i:i + m]
        if window == w or window == w_inv:
            hits[i] = Z if window == w else -Z
            covered[i:i + m] = [True] * m
            i += m
        else:
            i += 1
    return hits, covered


def _seam_match(word, w, covered):
    """The first match that wraps around the end of ``word`` and touches no inner match, as ``(k, +-Z)`` or None.

    ``k`` letters from the end of the word followed by the first ``len(w) - k`` letters spell ``w`` or ``w^-1``.
    """
    n, m, w_inv = len(word), len(w), inverse(w)
    for k in range(1, m):
        window = word[n - k:] + word[:m - k]
        free = not any(covered[:m - k]) and not any(covered[n - k:])
        if free and window in (w, w_inv):
            return k, Z if window == w else -Z
    return None


def substitute(word, w):
    """Replace non-overlapping ``w`` / ``w^-1`` in ``word`` by ``Z`` / ``-Z``; returns ``(word', n_subs)``.

    The rule ``s`` of the family: one left-to-right pass over the word as written, then at most one match that
    straddles the seam (the first suffix length that fits), then free reduction.
    """
    n, m = len(word), len(w)
    if m > n:
        return reduce(word, False), 0
    hits, covered = _inner_matches(word, w)
    seam = _seam_match(word, w, covered)
    if seam:
        k, letter = seam
        out, i, end = [letter], m - k, n - k      # the wrapping match comes first; skip the letters it used
    else:
        out, i, end = [], 0, n
    while i < end:
        if i in hits:
            out.append(hits[i])
            i += m
        else:
            out.append(word[i])
            i += 1
    return reduce(tuple(out), False), len(hits) + (seam is not None)


def occurrences(cyc, w):
    """``(start, +-Z)`` for every cyclic window of ``cyc`` spelling ``w`` / ``w^-1`` (the seam is an ordinary place)."""
    n, m, w_inv = len(cyc), len(w), inverse(w)
    if m > n:
        return ()
    doubled, found = cyc + cyc, []
    for i in range(n):
        window = doubled[i:i + m]
        if window == w:
            found.append((i, Z))
        elif window == w_inv:
            found.append((i, -Z))
    return tuple(found)


def patterns(occs, n, m):
    """Every set of pairwise non-overlapping occurrences of a length-``m`` word in a cyclic word of length ``n``.

    Each occurrence is left out before it is taken, so the empty set comes first (the sweep's order).
    """
    spans = [{(start + j) % n for j in range(m)} for start, _ in occs]
    out = []

    def extend(k, used, chosen):
        if k == len(occs):
            out.append(tuple(chosen))
            return
        extend(k + 1, used, chosen)
        if not used & spans[k]:
            extend(k + 1, used | spans[k], chosen + [occs[k]])

    extend(0, set(), [])
    return out


def substitute_pattern(cyc, chosen, m):
    """The cyclic word ``cyc`` with each chosen occurrence ``(start, +-Z)`` replaced by its letter, freely reduced.

    The word is rotated to begin at the first chosen occurrence, so no chosen window wraps around the end.
    """
    if not chosen:
        return cyc
    n, base = len(cyc), chosen[0][0]
    rotated = rotate_left(cyc, base)
    letters = {(start - base) % n: letter for start, letter in chosen}
    out, i = [], 0
    while i < n:
        if i in letters:
            out.append(letters[i])
            i += m
        else:
            out.append(rotated[i])
            i += 1
    return reduce(tuple(out), False)


def isolate(rel, g):
    """``expr`` with ``g = expr`` solved from ``rel``, or None.

    ``rel`` must hold exactly one ``g^+-1`` and at least one ``Z`` once cyclically reduced (a ``z``-free isolator
    would make ``z`` redundant). Rotated to ``g^e s`` with ``s`` free of ``g``: ``g s = 1`` gives ``g = s^-1`` and
    ``G s = 1`` gives ``g = s``.
    """
    cyc = reduce(rel)
    at = [i for i, a in enumerate(cyc) if abs(a) == g]
    if len(at) != 1 or not any(abs(a) == Z for a in cyc):
        return None
    rotated = cyc[at[0]:] + cyc[:at[0]]
    rest = rotated[1:]
    return inverse(rest) if rotated[0] == g else rest
