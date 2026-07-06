"""Variable-generator-count presentations (pure Python, no numpy/numba).

A *word/relator* is a list of nonzero signed ints (x1 -> 1, x1^-1 -> -1, ..., up to
GMAX generators). A *state* is a tuple of relators; ``n_gen`` is tracked explicitly
because stable AC moves grow (stabilize) and shrink (eliminate) it.

Canonical letter order extends the repo's paper order Z<z<Y<y<X<x to any number of
generators: HIGHER generator id first, and for the same generator the inverse before
the positive (paper_lt below == greedy_nrel._paper_lt for ids 1..3). The byte encoding
mirrors greedy_nrel's rank-byte scheme with a fixed GMAX so a bytes-compare equals a
paper-order lex-compare for every n_gen up to GMAX (14 needed for the Wirtinger W).

NOTE: keys produced here are NOT interchangeable with greedy_nrel.canonical_key
(different GMAX -> different byte values). Meet-in-the-middle target sets that must
match greedy_nrel's solver keys are built with greedy_nrel's own functions; this
module's keys are used by the stable-move engine and the descendant catalog only.
"""

GMAX = 16


# --------------------------------------------------------------------------- words

def inverse_word(w):
    return [-a for a in reversed(w)]


def free_reduce(w):
    out = []
    for a in w:
        if out and out[-1] == -a:
            out.pop()
        else:
            out.append(a)
    return out


def cyclic_reduce(w):
    w = free_reduce(w)
    i, j = 0, len(w) - 1
    while i < j and w[i] == -w[j]:
        i += 1
        j -= 1
    return w[i:j + 1]


def paper_lt(a, b):
    """True iff letter a < b in the paper's order (higher |id| first; -g before +g)."""
    aa, bb = abs(a), abs(b)
    if aa != bb:
        return aa > bb
    return a < b


def _byte(v):
    a = v if v > 0 else -v
    if not 1 <= a <= GMAX:
        raise ValueError(f"letter {v} out of range +-1..+-{GMAX}")
    return (GMAX - a) * 2 + (1 if v > 0 else 0) + 1


def word_bytes(w):
    """Bytes whose lexicographic order == paper-order lex order on words."""
    return bytes(_byte(a) for a in w)


def min_rotation(w):
    """Lexicographically (paper-order) minimal cyclic rotation. Brute force O(L^2) —
    relators here are short (<= l_cap) and this is not the greedy solver's hot path."""
    n = len(w)
    if n <= 1:
        return list(w)
    best, best_b = None, None
    for i in range(n):
        cand = w[i:] + w[:i]
        b = word_bytes(cand)
        if best_b is None or b < best_b:
            best, best_b = cand, b
    return best


def canonical_word(w):
    """Rotation- and inversion-invariant canonical form (same convention as
    greedy_nrel.canonical_relator)."""
    if not w:
        return []
    a = min_rotation(list(w))
    b = min_rotation(inverse_word(w))
    return a if word_bytes(a) <= word_bytes(b) else b


# --------------------------------------------------------------------------- states

def canonical_state_key(state):
    """Canonical bytes key: canonicalize each relator, sort by (len, bytes), join by 0.
    Generator labels are taken as-is (no relabeling)."""
    parts = sorted((word_bytes(canonical_word(r)) for r in state),
                   key=lambda bs: (len(bs), bs))
    return b"\x00".join(parts)


def used_generators(state):
    return sorted({abs(a) for r in state for a in r})


def total_length(state):
    return sum(len(r) for r in state)


def is_trivial_state(state, n_gen):
    """Trivial presentation: n_gen relators, each a single distinct generator letter."""
    if len(state) != n_gen:
        return False
    if any(len(r) != 1 for r in state):
        return False
    return sorted(abs(r[0]) for r in state) == list(range(1, n_gen + 1))


def relabel_state(state, perm, invert=frozenset()):
    """Apply the signed generator permutation: letter g -> perm[|g|] with sign kept,
    then flipped if |g| in invert. perm maps old id -> new id (both 1-based)."""
    out = []
    for r in state:
        nr = []
        for a in r:
            g = abs(a)
            v = perm[g] if a > 0 else -perm[g]
            if g in invert:
                v = -v
            nr.append(v)
        out.append(nr)
    return tuple(out)


def relabel_variants(state, n_gen):
    """All 2^k * k! signed relabelings of the k=n_gen generators (ids must be 1..n_gen).
    Only sane for small k (k<=3 -> 48). Yields states."""
    from itertools import permutations, product
    gens = list(range(1, n_gen + 1))
    for p in permutations(gens):
        perm = {g: p[i] for i, g in enumerate(gens)}
        for inv_mask in product((False, True), repeat=n_gen):
            invert = frozenset(g for g, m in zip(gens, inv_mask) if m)
            yield relabel_state(state, perm, invert)


def relabel_canonical_key(state, n_gen):
    """Min canonical_state_key over all signed relabelings — collapses presentations
    that differ only by renaming/inverting generators. k<=3 only (cost 2^k k!)."""
    if n_gen > 3:
        raise ValueError("relabel_canonical_key is limited to n_gen<=3 (cost 2^k k!)")
    return min(canonical_state_key(s) for s in relabel_variants(state, n_gen))


# --------------------------------------------------------------------- abelianization

def exponent_matrix(state, n_gen):
    """rows = relators, cols = generators 1..n_gen; entry = exponent sum."""
    rows = []
    for r in state:
        row = [0] * n_gen
        for a in r:
            row[abs(a) - 1] += 1 if a > 0 else -1
        rows.append(row)
    return rows


def det_bareiss(m):
    """Exact integer determinant (fraction-free Bareiss). m: square list-of-lists."""
    n = len(m)
    if n == 0:
        return 1
    a = [row[:] for row in m]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if a[k][k] == 0:
            for i in range(k + 1, n):
                if a[i][k] != 0:
                    a[k], a[i] = a[i], a[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def abelianization_det(state, n_gen):
    """det of the exponent matrix for a BALANCED state (len(state)==n_gen), else None.
    Every presentation of the trivial group has |det|=1, and every stable AC move
    preserves |det| — a cheap independent invariant checked along all our paths."""
    if len(state) != n_gen:
        return None
    return det_bareiss(exponent_matrix(state, n_gen))
