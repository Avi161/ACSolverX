"""Inside a knot bucket: does the exponent sign and the block size tell solved from unsolved?

``knot_number`` deliberately throws two things away -- it lowercases, so ``x`` and ``X`` count the
same, and it counts blocks without looking at how big they are. Both are recoverable, and both are
the natural next question once max_knots has split the population: among the states that share a
max_knots, what still differs?

A **signed block** keeps all of it: ``(generator, length, exponent sum)``. For a block of letters
drawn from {x, X}, the exponent sum is ``#x - #X``, so

    xxx   -> length 3, exp +3   (pure)
    XXX   -> length 3, exp -3   (pure)
    xXx   -> length 3, exp +1   (mixed -- the sign alternates inside the block)

``length == |exp|`` exactly when the block is a pure power, which is what makes ``frac_mixed`` a
clean scalar for "does the exponent alternate inside a block".

Two invariance constraints shape every feature here, and neither is optional:

  * **Rotation.** Blocks are read cyclically, so the block spanning the canonicaliser's cut is one
    block. Enforced by the same gate as the rest of the representations.
  * **Relator inversion flips every sign at once** (``xxy -> YXX``), and ``canon_pair`` already
    quotients inversion -- so a raw signed count like "number of negative blocks" is well defined
    on the representative but is *not* an invariant of the presentation. Every sign feature below
    is therefore built from inversion-stable combinations: ``min(#pos, #neg)``, ``|#pos - #neg|``,
    and absolute exponents. Likewise x<->y is folded by taking min/max over the two generators
    rather than naming them.
"""
import numpy as np

from experiments.clustering.features import gen_runs

INV_SIGN = {"x": 1, "X": -1, "y": 1, "Y": -1}


def signed_blocks(w):
    """[(generator, length, exponent sum), ...] read cyclically around the ring."""
    L = len(w)
    if L == 0:
        return []
    runs = gen_runs(w)
    out, pos = [], 0
    # gen_runs starts at the first generator change; recover the same offset to slice the letters.
    gen = [c.lower() for c in w]
    if len({g for g in gen}) == 1:
        start = 0
    else:
        start = next(i for i in range(L) if gen[i] != gen[(i - 1) % L])
    for g, n in runs:
        letters = [w[(start + pos + t) % L] for t in range(n)]
        out.append((g, n, sum(INV_SIGN[c] for c in letters)))
        pos += n
    return out


def signed_features(r1, r2):
    """(14,) inversion- and swap-stable description of the signed block structure of a pair."""
    blocks = signed_blocks(r1) + signed_blocks(r2)
    if not blocks:
        return np.zeros(14)
    lens = np.array([n for _, n, _ in blocks], dtype=float)
    exps = np.array([e for _, _, e in blocks], dtype=float)
    mixed = np.array([abs(e) != n for _, n, e in blocks], dtype=float)
    xl = np.array([n for g, n, _ in blocks if g == "x"], dtype=float)
    yl = np.array([n for g, n, _ in blocks if g == "y"], dtype=float)
    mx = xl.mean() if xl.size else 0.0
    my = yl.mean() if yl.size else 0.0
    lo, hi = min(mx, my), max(mx, my)                    # x<->y folded
    npos = int((exps > 0).sum())
    nneg = int((exps < 0).sum())
    return np.array([
        mixed.mean(),                                    # fraction of blocks with alternating sign
        float(mixed.sum()),
        (lens - np.abs(exps)).sum() / lens.sum(),        # how much cancellation sits inside blocks
        lens.mean(), lens.max(), lens.std(),
        lens.max() / lens.mean(),                        # block unevenness
        lo, hi, hi / (lo if lo else 1.0),                # generator asymmetry, swap-folded
        min(npos, nneg), abs(npos - nneg),               # sign spread, inversion-stable
        np.abs(exps).mean(), np.abs(exps).max(),
    ])


FEATURE_NAMES = [
    "frac mixed blocks", "n mixed blocks", "in-block cancellation", "mean block length",
    "max block length", "block length sd", "block unevenness", "smaller mean block",
    "larger mean block", "generator asymmetry", "min(#pos,#neg) blocks", "|#pos-#neg| blocks",
    "mean |exponent|", "max |exponent|",
]
assert len(FEATURE_NAMES) == 14


def block_signature(r1, r2):
    """A readable, rotation-invariant signature: block lengths in cyclic order, necklace-minimal.

    This is literally "how many x's and y's sit between each knot". Rotating the ring rotates the
    block sequence, so the lexicographically least rotation is taken to make it canonical; the two
    relators are then sorted so exchanging them cannot change the signature.
    """
    def one(w):
        b = signed_blocks(w)
        if not b:
            return ()
        seq = [(g, n) for g, n, _ in b]
        rots = [tuple(seq[i:] + seq[:i]) for i in range(len(seq))]
        return min(rots)
    return tuple(sorted([one(r1), one(r2)]))


def sig_str(sig):
    return " | ".join("".join(f"{g}{n}" for g, n in part) or "-" for part in sig)
