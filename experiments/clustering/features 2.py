"""Cyclic-invariant featurizations of a two-relator presentation.

Every representation here is a function of the pair ``(r1, r2)`` of **cyclic** words, and every
one of them is invariant under rotating either relator. That is the whole design constraint: a
relator is a ring, not a string, so any feature that can see where the canonicaliser happened to
cut the ring is measuring the tie-break rather than the presentation.

The headline representation is the **ring autocorrelation**, the training-free analogue of the
Dual-Ring Transformer's cyclic relative positional attention (Two-Hump paper Sec 4.1: "relators are
cyclic sequences, not linear ones"; tokens at positions i, j interact through the cyclic distance
``d(i,j) = (i-j) mod L``). Where the network *learns* attention weights over that cyclic distance,
we simply *tabulate* the empirical distribution over (letter a, letter b, cyclic distance d):

    A[a, b, d] = #{ i : w[i] = a  and  w[(i+d) mod L] = b }

Why it is rotation-invariant, stated in Fourier terms because that is where the constraint on the
cross-ring term comes from. Write ``s_a`` for the 0/1 indicator signal of letter ``a`` around the
ring and ``S_a`` for its DFT. Rotating the ring by tau multiplies **every** letter channel by the
same phase ``exp(-2*pi*i*k*tau/L)``, so:

  * ``|S_a[k]|``                  is rotation-invariant           -> ``ring_spectrum``
  * ``S_a[k] * conj(S_b[k])``     is rotation-invariant (phases cancel), and its inverse DFT is
    exactly the circular autocorrelation above                    -> ``ring_autocorr``
  * ``S1_a[k] * conj(S2_b[k])``   is **NOT** invariant: the two rings rotate independently, so
    their phases do not cancel. A cross-ring feature may therefore only combine per-ring
    invariants (magnitudes), never a phase-bearing product. ``ring_cross`` respects this.

Relators have different lengths, so a raw lag ``d`` is not comparable across presentations. Every
lag-indexed feature is binned by the **normalised** lag ``u = d / L`` on a fixed grid, which makes
the vector a fixed width and scale-free in the ring's circumference.

Ordering of the two rings is the canonical one from ``canon_pair`` (which already quotients the
relator swap), so ``(ring1 | ring2)`` concatenation is well-defined. ``*_sym`` variants additionally
fold the swap explicitly via (sum, |difference|), for representations where we want invariance
rather than mere well-definedness.
"""
import collections
import itertools

import numpy as np

ALPHA = ("x", "X", "y", "Y")
IDX = {c: i for i, c in enumerate(ALPHA)}
INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
# The 8 signed permutations of {x, y}, as letter->letter maps. A feature summed over this orbit is
# invariant under generator relabeling, not merely well-defined on a canonical representative.
SIGNED_PERMS = []
for _fx in ("x", "X", "y", "Y"):
    for _fy in ("x", "X", "y", "Y"):
        if _fx.lower() == _fy.lower():
            continue
        _m = {"x": _fx, "y": _fy}
        _m["X"], _m["Y"] = INV[_fx], INV[_fy]
        SIGNED_PERMS.append(_m)
assert len(SIGNED_PERMS) == 8

NLAG = 6      # normalised-lag bins for the autocorrelation
NFREQ = 6     # normalised-frequency bins for the spectrum
KMAX = 4      # longest cyclic k-mer


# --------------------------------------------------------------------------------------- rings

def _ring(w):
    return np.fromiter((IDX[c] for c in w), dtype=np.int64, count=len(w))


def ring_autocorr(w, nlag=NLAG):
    """(16*nlag,) circular autocorrelation of one ring, binned by normalised lag d/L.

    ``A[a,b,d]`` counts positions where letter a is followed, d steps around the ring, by letter b.
    Lags run 1..floor(L/2): beyond half the circumference the information repeats, since
    ``A[a,b,d] == A[b,a,L-d]``. Counts are divided by L so the vector is a rate, not a size.
    """
    r = _ring(w)
    L = len(r)
    out = np.zeros((4, 4, nlag))
    if L < 2:
        return out.ravel()
    for d in range(1, L // 2 + 1):
        b = int(min(nlag - 1, (d / L) * 2 * nlag))  # u = d/L in (0, 0.5] -> nlag bins
        rolled = np.roll(r, -d)
        for a, c in zip(r, rolled):
            out[a, c, b] += 1.0
    return (out / L).ravel()


def ring_spectrum(w, nfreq=NFREQ):
    """(4*nfreq,) rotation-invariant DFT magnitude of each letter channel, binned by k/L."""
    r = _ring(w)
    L = len(r)
    out = np.zeros((4, nfreq))
    if L < 2:
        return out.ravel()
    for a in range(4):
        mag = np.abs(np.fft.rfft((r == a).astype(float)))
        for k in range(1, len(mag)):           # k=0 is the letter count, already in `letters`
            b = int(min(nfreq - 1, (k / L) * 2 * nfreq))
            out[a, b] += mag[k]
    return (out / L).ravel()


def kmer(w, k):
    """(4**k,) cyclic k-mer frequency. Wraps around the ring, so no seam is privileged."""
    out = np.zeros(4 ** k)
    L = len(w)
    if L == 0:
        return out
    for i in range(L):
        code = 0
        for j in range(k):
            code = code * 4 + IDX[w[(i + j) % L]]
        out[code] += 1.0
    return out / L


def whitehead(w):
    """(6,) Whitehead-graph edge rates: the subword ``ab`` contributes an edge {a^-1, b}."""
    pairs = [tuple(sorted(p)) for p in itertools.combinations(ALPHA, 2)]
    c = collections.Counter()
    L = len(w)
    for i in range(L):
        c[tuple(sorted((INV[w[i]], w[(i + 1) % L])))] += 1
    return np.array([c[p] / max(L, 1) for p in pairs])


def gen_runs(w):
    """Maximal same-generator runs, read **cyclically**. Returns [(generator, length), ...].

    A run is a block of consecutive letters on the same generator, so ``x`` and ``X`` belong to the
    same run. Reading cyclically means the block spanning the canonicaliser's cut is one run, not
    two -- that is exactly what makes the count rotation-invariant.
    """
    L = len(w)
    if L == 0:
        return []
    gen = [c.lower() for c in w]
    if len(set(gen)) == 1:
        return [(gen[0], L)]
    start = next(i for i in range(L) if gen[i] != gen[(i - 1) % L])
    runs, cur = [], 1
    for t in range(1, L):
        i, j = (start + t) % L, (start + t - 1) % L
        if gen[i] == gen[j]:
            cur += 1
        else:
            runs.append((gen[j], cur))
            cur = 1
    runs.append((gen[(start - 1) % L], cur))
    return runs


def block_counts(w):
    """(number of maximal x-blocks, number of maximal y-blocks), read cyclically."""
    runs = gen_runs(w)
    return (sum(1 for g, _ in runs if g == "x"), sum(1 for g, _ in runs if g == "y"))


def knot_number(w):
    """Knots: how many blocks of one generator sit squashed inside the other, counted cyclically.

    **Theorem.** If a cyclic word contains at least one x-type letter *and* at least one y-type
    letter, then #x-blocks == #y-blocks.

    *Proof.* Maximal blocks partition the cycle Z_L into arcs A_1..A_m in cyclic order, and by
    maximality consecutive arcs carry different generators, so the labels alternate: l_j = l_1 for
    odd j and l_j = l_2 != l_1 for even j. Cyclicity requires l_m != l_1. Were m odd we would have
    l_m = l_1, a contradiction; so m is even and exactly m/2 arcs carry each generator. QED

    So "counting on either index" is not a convention -- it is *forced* to agree, and the shared
    value is what this returns.

    **The pure-power case is 0, not 1.** A word on a single generator (``X``, ``yyy``) falls
    outside the hypothesis: it has one block of its own generator and none of the other. Reading
    the definition literally -- how many blocks of one generator are squashed *inside the other* --
    the answer is none, because the other generator does not occur. A ``max(#x, #y)`` tie-break
    would say 1, but that rule only exists to reconcile the two counts when they disagree, and
    here the disagreement is not a tie to break: there is genuinely nothing squashed.

    0 is also the more informative value. A relator that is a pure power kills a generator
    outright -- ``sol_001`` is <x, y | x, YYXyx>, i.e. x = 1 -- so a 0 marks a degenerate,
    trivially-collapsing presentation rather than a merely quiet one.

    Choosing 0 over 1 moves NOTHING measurable: it changes no presentation's ``max_knots`` at all,
    and only shifts ``min_knots`` from 1 to 0 for the 7 presentations built on ``X``
    (``sol_001``..``sol_007``). ``test_knots.py`` pins the theorem, this case, and that invariance.

        yyyxxxyyyxxx  ->  yyy|xxx|yyy|xxx  ->  (2 x-blocks, 2 y-blocks)  ->  2 knots
        yxxyxyxx      ->  y|xx|y|x|y|xx    ->  (3 x-blocks, 3 y-blocks)  ->  3 knots
        X             ->  x                ->  (1 x-block,  0 y-blocks) ->  0 knots
    """
    nx, ny = block_counts(w)
    return 0 if min(nx, ny) == 0 else max(nx, ny)


def knots(w):
    """(8,) knot structure of one ring, in the user's sense. Raw count AND density, because they
    answer different questions: the count is confounded with length, the density is not."""
    L = len(w)
    if L == 0:
        return np.zeros(8)
    runs = gen_runs(w)
    k = knot_number(w)
    xs = np.array([n for g, n in runs if g == "x"], dtype=float)
    ys = np.array([n for g, n in runs if g == "y"], dtype=float)
    lens = np.array([n for _, n in runs], dtype=float)
    flips = sum(1 for i in range(L) if w[i].lower() == w[(i + 1) % L].lower() and w[i] != w[(i + 1) % L])
    return np.array([
        float(k),                       # knot number
        k / L,                          # knot density -- the length-free version
        lens.mean(), lens.max(), lens.std(),
        xs.mean() if xs.size else 0.0,  # how deep the x-blocks are
        ys.mean() if ys.size else 0.0,  # how deep the y-blocks are
        flips / L,                      # sign alternation inside a block (x X x vs x x x)
    ])


def syllable(w):
    """(6,) cyclic syllable structure -- run counts and run lengths, all normalised by L."""
    L = len(w)
    if L == 0:
        return np.zeros(6)
    runs = np.array([n for _, n in gen_runs(w)], dtype=float)
    gen = [c.lower() for c in w]
    flips = sum(1 for i in range(L) if gen[i] == gen[(i + 1) % L] and w[i] != w[(i + 1) % L])
    return np.array([len(runs) / L, runs.mean() / L, runs.max() / L,
                     runs.std(), float(len(runs)), flips / L])


def letters(w):
    """(4,) letter frequency -- trivially rotation-invariant."""
    L = max(len(w), 1)
    return np.array([w.count(c) / L for c in ALPHA])


# ------------------------------------------------------------------------------- presentations

_RING_FEATS = {
    "letters": letters,
    "whitehead": whitehead,
    "syllable": syllable,
    "knots": knots,
    "autocorr": ring_autocorr,
    "spectrum": ring_spectrum,
    "kmer2": lambda w: kmer(w, 2),
    "kmer3": lambda w: kmer(w, 3),
    "kmer4": lambda w: kmer(w, 4),
}


def _both(name, r1, r2):
    f = _RING_FEATS[name]
    return np.concatenate([f(r1), f(r2)])


def _sym(name, r1, r2):
    """Swap-symmetrised: (sum, |difference|) is invariant under exchanging the two rings."""
    f = _RING_FEATS[name]
    a, b = f(r1), f(r2)
    return np.concatenate([a + b, np.abs(a - b)])


def _relabel(w, m):
    return "".join(m[c] for c in w)


def _perm_sym(name, r1, r2):
    """Summed over the 8 signed permutations: invariant under generator relabeling."""
    f = _RING_FEATS[name]
    acc = None
    for m in SIGNED_PERMS:
        v = np.concatenate([f(_relabel(r1, m)), f(_relabel(r2, m))])
        acc = v if acc is None else acc + v
    return acc / 8.0


def shape(r1, r2):
    """(5,) pure size. The CONTROL representation: if this separates as well as the rich ones,
    the separation is length, not structure."""
    l1, l2 = len(r1), len(r2)
    return np.array([l1 + l2, min(l1, l2), max(l1, l2),
                     min(l1, l2) / max(l1, l2), abs(l1 - l2)], dtype=float)


# name -> callable(r1, r2) -> 1-D vector. Every entry is rotation-invariant in both rings.
REPRESENTATIONS = {
    "shape (control)":      shape,
    "letters":              lambda a, b: _both("letters", a, b),
    "whitehead":            lambda a, b: _both("whitehead", a, b),
    "syllable":             lambda a, b: _both("syllable", a, b),
    "knots":                lambda a, b: _both("knots", a, b),
    "knots+ring":           lambda a, b: np.concatenate([_both("knots", a, b),
                                                         _both("autocorr", a, b),
                                                         _both("spectrum", a, b)]),
    "kmer2":                lambda a, b: _both("kmer2", a, b),
    "kmer3":                lambda a, b: _both("kmer3", a, b),
    "kmer4":                lambda a, b: _both("kmer4", a, b),
    "kmer23":               lambda a, b: np.concatenate([_both("kmer2", a, b), _both("kmer3", a, b)]),
    "ring_autocorr":        lambda a, b: _both("autocorr", a, b),
    "ring_spectrum":        lambda a, b: _both("spectrum", a, b),
    "ring_dual":            lambda a, b: np.concatenate([_both("autocorr", a, b),
                                                         _both("spectrum", a, b),
                                                         _both("letters", a, b)]),
    "ring_dual_sym":        lambda a, b: np.concatenate([_sym("autocorr", a, b),
                                                         _sym("spectrum", a, b),
                                                         _sym("letters", a, b)]),
    "ring_dual_permsym":    lambda a, b: np.concatenate([_perm_sym("autocorr", a, b),
                                                         _perm_sym("spectrum", a, b),
                                                         _perm_sym("letters", a, b)]),
    "ring+whitehead+syll":  lambda a, b: np.concatenate([_both("autocorr", a, b),
                                                         _both("spectrum", a, b),
                                                         _both("whitehead", a, b),
                                                         _both("syllable", a, b),
                                                         _both("letters", a, b)]),
    "all":                  lambda a, b: np.concatenate([_both("autocorr", a, b),
                                                         _both("spectrum", a, b),
                                                         _both("whitehead", a, b),
                                                         _both("syllable", a, b),
                                                         _both("kmer2", a, b),
                                                         _both("kmer3", a, b),
                                                         _both("letters", a, b),
                                                         shape(a, b)]),
}


def build(pairs, name):
    """(n, d) matrix for the named representation over ``pairs`` = [(r1, r2), ...]."""
    f = REPRESENTATIONS[name]
    return np.vstack([f(r1, r2) for r1, r2 in pairs])


def rotation_invariance_report(pairs, rng):
    """Every representation must be numerically unchanged when a ring is rotated. This is a test,
    not a formality: a feature that reads the canonicaliser's cut point would silently cluster on
    the tie-break. Returns {name: max abs deviation over random rotations}."""
    out = {}
    for name in REPRESENTATIONS:
        worst = 0.0
        for r1, r2 in pairs:
            base = REPRESENTATIONS[name](r1, r2)
            for _ in range(3):
                k1 = int(rng.integers(len(r1))) if r1 else 0
                k2 = int(rng.integers(len(r2))) if r2 else 0
                rot = REPRESENTATIONS[name](r1[k1:] + r1[:k1], r2[k2:] + r2[:k2])
                worst = max(worst, float(np.abs(base - rot).max()))
        out[name] = worst
    return out
