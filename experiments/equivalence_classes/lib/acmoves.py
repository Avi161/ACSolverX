"""AC move sets for the equivalence-class search.

Two move sets, both emitting Definition 2.1 moves ``(target, jsign, k1, k2)``:

  ``seam``  the baseline's set -- a child is emitted only when the seam cancels
            (``is_inverse_nj(rot_i[-1], rot_o[0])``). Identical to
            ``expand_node_nj`` (greedy_baseline.py:499); asserted in the tests.

  ``full``  every ``(k1, k2)``, cancelling seam or not. Still every move is a
            genuine AC move --
                rot_{k1}(r_i) . rot_{k2}(r_j^{+-1})  =  c1 r_i c1^-1 . c2 r_j^{+-1} c2^-1
            i.e. an AC move up to a global conjugation, which ``canonical_pair_nj``
            quotients away -- so any state collision it produces still proves
            AC-equivalence. Unlike ``seam`` it is *inverse-closed* (applying the
            move again with ``jsign`` flipped undoes it), which is what makes two
            balls of radius d/2 meet instead of needing one ball of radius d.

Why ``seam`` alone is not inverse-closed: the trivial pair ``(x, y)`` has ZERO
children under it (no rotation of ``x`` ends in the inverse of a rotation of
``y^{+-1}``), so it is a sink. Under ``full`` it is not.

Both are length-pruned by the per-relator cap. Nothing here modifies the baseline;
``reduce_relator_nj``, ``canonical_pair_nj``, ``inverse_relator_nj`` and
``is_inverse_nj`` are imported from it verbatim.
"""
import numpy as np
from numba import njit

from experiments.search.greedy_baseline import (  # noqa: F401  (re-exported for callers)
    canonical_pair_nj, inverse_relator_nj, is_inverse_nj, pack_key, reduce_relator_nj,
    str_to_arr, unpack_arrays, unpack_key,
)


@njit(cache=True)
def expand_nj(r1, r2, cap, cyclic, seam_only):
    """Definition 2.1 children of (r1, r2), reduced + canonicalised, length-pruned.

    Returns ``(codes, lens, moves, count)`` with the same layout as
    ``expand_node_nj``: for child i, ``codes[i, :lens[i,0]]`` are the canonical r1
    codes (X=1, Y=2, x=3, y=4) and ``codes[i, lens[i,0]:lens[i,0]+lens[i,1]]`` the
    canonical r2 codes; ``moves[i] = (target, jsign, k1, k2)``.

    ``seam_only=True`` reproduces the baseline move set exactly.
    """
    n1 = len(r1)
    n2 = len(r2)
    ub = 4 * (n1 + 1) * (n2 + 1)
    codes = np.empty((ub, 2 * cap), dtype=np.uint8)
    lens = np.empty((ub, 2), dtype=np.int32)
    moves = np.empty((ub, 4), dtype=np.int32)
    count = 0

    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
        else:
            ri = r2
            rj = r1
        len_i = len(ri)
        if len_i == 0:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else inverse_relator_nj(rj)
            jsign = 1 if idx == 0 else -1
            len_o = len(oj)
            if len_o == 0:
                continue
            rots_o = [np.roll(oj, 2 * k2) for k2 in range(len_o)]
            for k1 in range(len_i):
                rot_i = np.roll(ri, 2 * k1)
                for k2 in range(len_o):
                    rot_o = rots_o[k2]
                    if seam_only and not is_inverse_nj(rot_i[-1], rot_o[0]):
                        continue
                    piece = np.concatenate((rot_i, rot_o))
                    if target == 1:
                        nr1 = piece
                        nr2 = r2
                    else:
                        nr1 = r1
                        nr2 = piece
                    a = reduce_relator_nj(nr1, cyclic)
                    b = reduce_relator_nj(nr2, cyclic)
                    if len(a) > cap or len(b) > cap:
                        continue
                    if len(a) == 0 or len(b) == 0:
                        continue
                    ca, cb = canonical_pair_nj(a, b)
                    la = len(ca)
                    lb = len(cb)
                    for t in range(la):
                        v = 2 * ca[t, 0] + ca[t, 1]
                        if v == 0:
                            codes[count, t] = 2
                        elif v == 1:
                            codes[count, t] = 4
                        elif v == 2:
                            codes[count, t] = 1
                        else:
                            codes[count, t] = 3
                    for t in range(lb):
                        v = 2 * cb[t, 0] + cb[t, 1]
                        if v == 0:
                            codes[count, la + t] = 2
                        elif v == 1:
                            codes[count, la + t] = 4
                        elif v == 2:
                            codes[count, la + t] = 1
                        else:
                            codes[count, la + t] = 3
                    lens[count, 0] = la
                    lens[count, 1] = lb
                    moves[count, 0] = target
                    moves[count, 1] = jsign
                    moves[count, 2] = k1
                    moves[count, 3] = k2
                    count += 1

    return codes, lens, moves, count


_CHR = {1: "X", 2: "Y", 3: "x", 4: "y"}


def children(r1s, r2s, cap=48, cyclic=True, seam_only=False):
    """String-level wrapper: ('YXy...', 'YY...') -> {(r1, r2): (target, jsign, k1, k2)}.

    Deduplicated on the canonical child; the stored move is the FIRST that reached it,
    in the canonical ``target -> jsign -> k1 -> k2`` enumeration order.
    """
    a1 = reduce_relator_nj(str_to_arr(r1s), cyclic)
    a2 = reduce_relator_nj(str_to_arr(r2s), cyclic)
    c1, c2 = canonical_pair_nj(a1, a2)
    codes, lens, moves, n = expand_nj(c1, c2, cap, cyclic, seam_only)
    out = {}
    for i in range(n):
        la, lb = int(lens[i, 0]), int(lens[i, 1])
        k = ("".join(_CHR[c] for c in codes[i, :la]),
             "".join(_CHR[c] for c in codes[i, la:la + lb]))
        if k not in out:
            out[k] = (int(moves[i, 0]), int(moves[i, 1]), int(moves[i, 2]), int(moves[i, 3]))
    return out


def canon(r1s, r2s, cyclic=True):
    """String pair -> canonical string pair (rotation / inversion / swap invariant)."""
    a1 = reduce_relator_nj(str_to_arr(r1s), cyclic)
    a2 = reduce_relator_nj(str_to_arr(r2s), cyclic)
    c1, c2 = canonical_pair_nj(a1, a2)
    return unpack_key(pack_key(c1, c2))


def canon_key(r1s, r2s, cyclic=True):
    """String pair -> packed bytes key (the visited-table key)."""
    a1 = reduce_relator_nj(str_to_arr(r1s), cyclic)
    a2 = reduce_relator_nj(str_to_arr(r2s), cyclic)
    c1, c2 = canonical_pair_nj(a1, a2)
    return pack_key(c1, c2)
