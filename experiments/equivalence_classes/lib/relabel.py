"""The relabel key: canonical form under the 8 signed permutations of {x, y}.

**Why this is an exact quotient, not a heuristic.** A signed permutation sigma is
length-preserving on words, so it commutes with rotation, with inversion, and with free /
cyclic reduction. Every Definition 2.1 move is built out of exactly those operations, hence

    children(sigma(P))  ==  sigma(children(P))        (set equality, exactly)

so the move relation descends to a well-defined graph on relabel classes. Deduplicating the
visited table by this key is therefore both **sound** and **complete within the cap** -- it is
not an approximation, it just makes the search 8x smaller.

(The same is NOT true of a general phi in Aut(F2), e.g. x -> xy: it changes word lengths, so it
changes which rotations exist and does not commute with the move set. That is why the full
Whitehead key is only ever used as a post-hoc *merge signal*, never as the dedup key.)

Letter encoding follows ``char_to_array``: row = (is_x_generator, is_positive), so
index ``2*a[0] + a[1]`` gives Y=0, y=1, X=2, x=3.
"""
import numpy as np
from numba import njit

from experiments.search.greedy_baseline import canonical_pair_nj

# index order: Y=0, y=1, X=2, x=3
_IDX_TO_CHAR = "YyXx"
_CHAR_TO_IDX = {c: i for i, c in enumerate(_IDX_TO_CHAR)}
# order-preserving codes (must match pack_key): X=1, Y=2, x=3, y=4
_IDX_TO_CODE = np.array([2, 4, 1, 3], dtype=np.uint8)
CODE_TO_CHAR = {1: "X", 2: "Y", 3: "x", 4: "y"}


def _build_perm_table():
    """(8, 4) int8: PERMS[s, idx] = image index of letter ``idx`` under signed perm ``s``.

    A signed permutation is any permutation of {Y, y, X, x} that commutes with inversion
    (the pairs Y<->y and X<->x). There are exactly 8, one per (image of x, image of y) with
    the two images on different generators.
    """
    rows, names = [], []
    for fx in ("x", "X", "y", "Y"):
        for fy in ("x", "X", "y", "Y"):
            if fx.lower() == fy.lower():
                continue
            img = {"x": fx, "y": fy}
            img["X"] = fx.swapcase()
            img["Y"] = fy.swapcase()
            rows.append([_CHAR_TO_IDX[img[_IDX_TO_CHAR[i]]] for i in range(4)])
            names.append(f"x->{fx},y->{fy}")
    assert len(rows) == 8
    return np.array(rows, dtype=np.int8), names


PERMS, PERM_NAMES = _build_perm_table()
# The identity is the perm mapping x->x, y->y.
IDENTITY_PERM = PERM_NAMES.index("x->x,y->y")


@njit(cache=True)
def apply_perm_nj(rel, perm):
    """Apply one signed permutation (length-preserving) to an (n, 2) bool relator."""
    n = len(rel)
    out = np.empty((n, 2), dtype=np.bool_)
    for i in range(n):
        idx = 2 * rel[i, 0] + rel[i, 1]
        img = perm[idx]
        out[i, 0] = img >= 2      # X, x are the x-generator
        out[i, 1] = (img & 1) == 1  # y, x are positive
    return out


@njit(cache=True)
def _encode(ca, cb, buf):
    la = len(ca)
    lb = len(cb)
    for t in range(la):
        v = 2 * ca[t, 0] + ca[t, 1]
        buf[t] = 2 if v == 0 else (4 if v == 1 else (1 if v == 2 else 3))
    for t in range(lb):
        v = 2 * cb[t, 0] + cb[t, 1]
        buf[la + t] = 2 if v == 0 else (4 if v == 1 else (1 if v == 2 else 3))
    return la, lb


@njit(cache=True)
def _lex_less(a, la, b, lb):
    """Compare packed code runs the way ``pack_key`` bytes compare (0x00 separator)."""
    n = la if la < lb else lb
    for i in range(n):
        if a[i] != b[i]:
            return a[i] < b[i]
    return la < lb


@njit(cache=True)
def relabel_key_nj(c1, c2, perms, out, work):
    """Min over the 8 signed permutations of the canonical packed codes of (c1, c2).

    ``c1, c2`` must already be a canonical pair. Writes the winning codes into ``out``
    (r1 then r2, back to back) and returns ``(la, lb, best_perm)``.
    """
    best_la = -1
    best_lb = -1
    best_s = 0
    for s in range(8):
        p = perms[s]
        a = apply_perm_nj(c1, p)
        b = apply_perm_nj(c2, p)
        ca, cb = canonical_pair_nj(a, b)
        la, lb = _encode(ca, cb, work)
        if best_la < 0:
            better = True
        else:
            # total length first (it is the search priority), then bytes
            ta = la + lb
            tb = best_la + best_lb
            if ta != tb:
                better = ta < tb
            elif la != best_la:
                better = _lex_less(work, la, out, best_la)
            else:
                better = _lex_less(work, la + lb, out, best_la + best_lb)
        if better:
            for t in range(la + lb):
                out[t] = work[t]
            best_la = la
            best_lb = lb
            best_s = s
    return best_la, best_lb, best_s
