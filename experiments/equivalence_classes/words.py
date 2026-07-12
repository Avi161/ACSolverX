"""Pure-Python word algebra on F2, in the repo's ``xXyY`` alphabet.

Deliberately dependency-free and independent of ``experiments/search`` so that anything
built on it can serve as a cross-check of the numba solver rather than an echo of it.
Symbol order matches ``lex_cmp_array``: ``Y < y < X < x``.
"""

ORDER = {"Y": 0, "y": 1, "X": 2, "x": 3}
INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y"}
CHAR_TO_INT = {v: k for k, v in INT_TO_CHAR.items()}


def inv(w):
    """w^-1: reverse the word and invert every letter."""
    return w[::-1].swapcase()


def rev(w):
    """The anti-automorphism w -> reverse(w). NOT a homomorphism."""
    return w[::-1]


def free_reduce(w):
    out = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyc_reduce(w):
    w = free_reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = free_reduce(w[1:-1])
    return w


def _key(w):
    return [ORDER[c] for c in w]


# Recode the alphabet so that plain byte order IS the solver's Y < y < X < x order. That lets
# canon_rel use Booth's O(n) least-rotation instead of materialising all 2n rotations -- the
# difference between 25 us and 2 us per call, and canon_rel is the hot path of the whole sweep.
_TO_ORD = str.maketrans("YyXx", "\x00\x01\x02\x03")
_FROM_ORD = str.maketrans("\x00\x01\x02\x03", "YyXx")


def _least_rotation(s):
    """Booth's algorithm: the lexicographically least rotation of ``s``, in O(n)."""
    n = len(s)
    ss = s + s
    f = [-1] * (2 * n)
    k = 0
    for j in range(1, 2 * n):
        sj = ss[j]
        i = f[j - k - 1]
        while i != -1 and sj != ss[k + i + 1]:
            if sj < ss[k + i + 1]:
                k = j - i - 1
            i = f[i]
        if i == -1 and sj != ss[k]:
            if sj < ss[k]:
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    return ss[k:k + n]


def canon_rel(w):
    """Lex-min over all rotations of w and of w^-1 -- rotation+inversion invariant.

    Mirrors ``canonical_relator_nj`` (greedy_baseline.py:165) under the same Y<y<X<x order.
    """
    w = cyc_reduce(w)
    if not w:
        return ""
    a = _least_rotation(w.translate(_TO_ORD))
    b = _least_rotation(inv(w).translate(_TO_ORD))
    return (a if a <= b else b).translate(_FROM_ORD)


def canon_pair(r1, r2):
    """Canonical, order-normalised pair. Mirrors ``canonical_pair_nj`` (:175)."""
    a, b = canon_rel(r1), canon_rel(r2)
    if (len(a), a.translate(_TO_ORD)) > (len(b), b.translate(_TO_ORD)):
        a, b = b, a
    return (a, b)


def exp_sums(w):
    ex = sum(1 if c == "x" else -1 if c == "X" else 0 for c in w)
    ey = sum(1 if c == "y" else -1 if c == "Y" else 0 for c in w)
    return ex, ey


def abelian_det(r1, r2):
    a, b = exp_sums(r1)
    c, d = exp_sums(r2)
    return a * d - b * c


def apply_hom(w, img):
    """Apply the endomorphism determined by ``img`` (a dict 'x'->word, 'y'->word)."""
    out = []
    for c in w:
        out.append(img[c] if c.islower() else inv(img[c.lower()]))
    return free_reduce("".join(out))


def apply_pair(pair, img):
    return canon_pair(apply_hom(pair[0], img), apply_hom(pair[1], img))


# --- the 8 signed permutations of {x, y} (Whitehead automorphisms of the first kind) ---
SIGNED_PERMS = []
for _fx in ("x", "X", "y", "Y"):
    for _fy in ("x", "X", "y", "Y"):
        if _fx.lower() == _fy.lower():
            continue
        SIGNED_PERMS.append((f"x->{_fx},y->{_fy}", {"x": _fx, "y": _fy}))
assert len(SIGNED_PERMS) == 8


def relabel_key(pair):
    """Canonical form under the 8 signed permutations -- the cheap Aut(F2) key."""
    return min(apply_pair(pair, img) for _, img in SIGNED_PERMS)


def ms_presentation(n, w):
    """Miller-Schupp MS(n, w) = < x, y | x^-1 y^n x y^-(n+1),  x^-1 w >.

    ``w`` is one of the 170 zero-x-exponent words of ``ms_solved_grid.csv``; n in 1..7.
    Verified: the 170 x 7 canonical pairs this builds are exactly the 1190 of
    ``data/1190MS.txt`` (set equality, 1190/1190).
    """
    r1 = "X" + "y" * n + "x" + "Y" * (n + 1)
    return (r1, "X" + w)


def ints_to_word(ints):
    return "".join(INT_TO_CHAR[i] for i in ints if i != 0)


def rot(w, k):
    """Cyclic rotation matching numba's ``np.roll(rel, 2*k)`` -- rotate RIGHT by k."""
    if not w:
        return w
    k %= len(w)
    return w[-k:] + w[:-k] if k else w


def replay_move(pair, move):
    """Apply one Definition 2.1 move ``(target, jsign, k1, k2)``, then reduce + canonicalise.

    Pure Python, no numba: this is what the certificate verifier replays, so it must not share
    an implementation with the search it is checking.

        r_i  <-  rot_{k1}(r_i) . rot_{k2}(r_{3-i}^{jsign})
    """
    target, jsign, k1, k2 = move
    r1, r2 = pair
    ri, rj = (r1, r2) if target == 1 else (r2, r1)
    oj = rj if jsign == 1 else inv(rj)
    piece = rot(ri, k1) + rot(oj, k2)
    return canon_pair(piece, r2) if target == 1 else canon_pair(r1, piece)
