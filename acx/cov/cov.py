"""One-shot change of variables (CoV): the images of a presentation and the checker of their certificates.

An image defines ``z = w(x, y)``, puts ``z`` for ``w`` in the relators, isolates a generator and eliminates it (Lemma 11
of the Two-Hump paper). Lemma 11 is stable AC and gives no path, so a solve of an image is a ``stable_cert`` for the row.
"""
from dataclasses import dataclass

from ..core.words import Presentation, canonical_word, fmt, inverse, reduce
from ..verify.replay import ReplayError, abs_det, replay

X, Y, Z = 1, 2, 3
FAMILY_TAG = "subnc2pxysb"
MIN_W_LEN = 2          # |w| < 2 is a rename
MIN_TRANSFORMED = 3    # the no-collapse gate (nc2)
MAX_LEN = 239          # an image with a longer relator is not in the family; None = no limit


def substitute(word, w):
    """Replace non-overlapping ``w`` / ``w^-1`` in ``word`` by ``Z`` / ``-Z``; ``(word', n_subs)``.

    One left-to-right pass over the written word, then at most one match that
    straddles the seam (the first suffix length that fits), then free reduction.
    """
    n, L, wi = len(word), len(w), inverse(w)
    if L > n:
        return reduce(word, False), 0
    used, hits, i = [False] * n, {}, 0
    while i + L <= n:
        c = word[i:i + L]
        if c in (w, wi):
            hits[i] = Z if c == w else -Z
            used[i:i + L] = [True] * L
            i += L
        else:
            i += 1
    seam = None
    for k in range(1, L):
        c = word[n - k:] + word[:L - k]
        if c in (w, wi) and not any(used[:L - k]) and not any(used[n - k:]):
            seam = (k, Z if c == w else -Z)
            break
    out, i, end = ([seam[1]], L - seam[0], n - seam[0]) if seam else ([], 0, n)
    while i < end:
        if i in hits:
            out.append(hits[i])
            i += L
        else:
            out.append(word[i])
            i += 1
    return reduce(tuple(out), False), len(hits) + (seam is not None)


def isolate(rel, g):
    """``expr`` with ``g = expr`` solved from ``rel``, or None.

    ``rel`` must hold exactly one ``g^+-1`` and at least one ``Z`` once cyclically
    reduced (a ``z``-free isolator would make ``z`` redundant). Rotated to
    ``g^e s`` with ``s`` free of ``g``: ``g s = 1`` gives ``g = s^-1``, ``G s = 1`` gives ``g = s``.
    """
    cyc = reduce(rel)
    at = [i for i, a in enumerate(cyc) if abs(a) == g]
    if len(at) != 1 or not any(abs(a) == Z for a in cyc):
        return None
    r = cyc[at[0]:] + cyc[:at[0]]
    return inverse(r[1:]) if r[0] == g else r[1:]


def substitute_generator(word, g, expr):
    """``word`` with every ``g`` replaced by ``expr`` (``g^-1`` by its inverse), freely reduced."""
    inv = inverse(expr)
    return reduce(tuple(b for a in word for b in (expr if a == g else inv if a == -g else (a,))), False)


def relabel(word, g):
    """Rename the generators that remain after ``g`` is gone to ``1, 2``: ``(y, z) -> (x, y)`` or ``(x, z) -> (x, y)``."""
    new = {h: i + 1 for i, h in enumerate(sorted({X, Y, Z} - {g}))}
    return tuple(new[abs(a)] * (1 if a > 0 else -1) for a in word)


def subwords(r1, r2):
    """The ``w`` family ``subnc2pxysb``: its tag names the rules, and changing one is a different experiment.

    ``sub``: ``w`` is a cyclic subword (the seam included) of ``r1`` or ``r2`` of length >= 2; ``w`` and ``w^-1`` are
    one member, ``max(w, w^-1)``. ``nc2``: ``w`` is dropped when substituting it brings a relator it occurs in below 3
    letters (a two-letter isolator is a rank-two substitution plus a rename). ``p``: pure powers such as ``xx`` count.
    Order is (length, word). The other letters of the tag are in ``branches`` (``s``: seam matches in ``substitute``;
    ``xy``: both targets; ``b``: every isolating relator is its own image).
    """
    found = set()
    for rel in (r1, r2):
        cyc = reduce(rel)
        dbl = cyc + cyc
        windows = (dbl[i:i + m] for m in range(MIN_W_LEN, len(cyc) + 1) for i in range(len(cyc)))
        found |= {max(w, inverse(w)) for w in windows}
    keep = [w for w in found
            if all(not k or len(s) >= MIN_TRANSFORMED for s, k in (substitute(rel, w) for rel in (r1, r2)))]
    return sorted(keep, key=lambda w: (len(w), w))


@dataclass(frozen=True)
class CoVImage:
    """One CoV image of a presentation, with the data of its certificate."""
    pres: Presentation       # the image, relabelled to <x, y | .., ..>
    w: tuple                 # z = w(x, y)
    gen: int                 # the generator eliminated: 1 (x) or 2 (y)
    iso_index: int           # 0 / 1: which substituted relator isolates ``gen``
    expr: tuple              # gen = expr, over the other generator and z
    substituted: tuple       # (r1', r2') over x, y, z after step 2
    n_subs: int

    @property
    def steps(self):
        """The transform as typed steps, replayed by ``apply_steps``."""
        return ({"op": "define", "word": self.w},
                {"op": "substitute", "rels": self.substituted},
                {"op": "eliminate", "gen": self.gen, "target": self.iso_index + 1, "expr": self.expr})

    @property
    def tag(self):
        """``w/target generator/isolating relator``, e.g. ``xyx/x/0``."""
        return f"{fmt(self.w)}/{'xy'[self.gen - 1]}/{self.iso_index}"


def branches(r1, r2, w, gen, max_len=MAX_LEN):
    """Every valid CoV of ``(r1, r2)`` for one ``w`` and one eliminated ``gen``: one per isolating relator."""
    r1s, n1 = substitute(r1, w)
    r2s, n2 = substitute(r2, w)
    if n1 + n2 == 0:
        return
    r_def = (-Z,) + w
    for idx, (iso, keep) in enumerate(((r1s, r2s), (r2s, r1s))):
        expr = isolate(iso, gen)
        if expr is None:
            continue
        out = tuple(relabel(substitute_generator(r, gen, expr), gen) for r in (keep, r_def))
        if all(out) and (max_len is None or max(map(len, out)) <= max_len):
            yield CoVImage(Presentation(2, out), w, gen, idx, expr, (r1s, r2s), n1 + n2)


def enumerate_images(pres, max_len=MAX_LEN):
    """All CoV images of the 2-generator, 2-relator ``pres`` as it is written (the order of the relators and their
    rotation matter), without repeats and without ranking: ``w`` by (length, word), then eliminate x before y,
    then relator 1 before relator 2.

    Per image: **define** ``z = w`` (a relator ``Z w``), **substitute** ``z`` for ``w`` / ``w^-1`` in ``r1, r2``,
    **isolate** ``g^+-1`` in one relator (``g = expr(other, z)``), **destabilise** (put ``expr`` for ``g`` in the
    remaining two relators, drop ``g``) and **relabel** the survivors to ``x, y``.
    """
    if pres.n_gen != 2 or len(pres.rels) != 2:
        raise ValueError(f"CoV needs a 2-generator, 2-relator presentation, got {pres}")
    r1, r2 = pres.rels
    seen, out = set(), []
    for w in subwords(r1, r2):
        for gen in (X, Y):
            for img in branches(r1, r2, w, gen, max_len):
                if img.pres.rels not in seen:
                    seen.add(img.pres.rels)
                    out.append(img)
    return tuple(out)


# ---- the certificate checker: independent of the enumeration above ----

def _det1(pres):
    """Raise ``ReplayError`` unless ``|det| = 1``."""
    if abs_det(pres) != 1:
        raise ReplayError(f"|det| != 1 at {pres}")


def _define(pres, st):
    """Step ``define``: add the generator ``z`` with the relator ``Z w``."""
    w = tuple(st["word"])
    if pres.n_gen != 2 or len(pres.rels) != 2 or len(w) < MIN_W_LEN or reduce(w, False) != w or any(abs(a) > 2 for a in w):
        raise ReplayError(f"cannot define z = {fmt(w)} on {pres}")
    return Presentation(3, pres.rels + ((-Z,) + w,))


def _substitute(pres, st):
    """Step ``substitute``: each relator is the old one with ``w`` put for ``z`` (up to rotation and inversion)."""
    new = tuple(tuple(r) for r in st["rels"])
    if pres.n_gen != 3 or len(new) != 2 or pres.rels[2][:1] != (-Z,):
        raise ReplayError("substitute needs the defined presentation")
    for old, r in zip(pres.rels, new):
        if canonical_word(reduce(substitute_generator(r, Z, pres.rels[2][1:]))) != canonical_word(reduce(old)):
            raise ReplayError(f"{fmt(r)} is not {fmt(old)} with w put for z")
    return Presentation(3, new + pres.rels[2:])


def _eliminate(pres, st):
    """Step ``eliminate``: solve the isolating relator for ``g`` and put ``expr`` for ``g`` in the others."""
    g, t, expr = st["gen"], st["target"] - 1, tuple(st["expr"])
    if pres.n_gen != 3 or g not in (X, Y) or t not in (0, 1) or any(abs(a) == g for a in expr):
        raise ReplayError(f"bad elimination {st}")
    rel = pres.rels[t]
    if sum(abs(a) == g for a in reduce(rel)) != 1 or reduce(substitute_generator(rel, g, expr)):
        raise ReplayError(f"{fmt(rel)} is not of the form {'xy'[g - 1]}^-1 expr")
    out = tuple(relabel(substitute_generator(r, g, expr), g) for i, r in enumerate(pres.rels) if i != t)
    if not all(out):
        raise ReplayError("an empty relator remains")
    return Presentation(2, out)


STEPS = {"define": _define, "substitute": _substitute, "eliminate": _eliminate}


def apply_steps(pres, steps):
    """The image of ``pres`` under the certificate ``steps`` (``CoVImage.steps``), re-derived without the enumerator.

    Checks the hypotheses of each Lemma 11 step (the isolating relator has the form ``g^-1 expr`` with ``expr`` free of
    ``g``) and ``|det| = 1`` after each; raises ``ReplayError`` on any violated check.
    """
    _det1(pres)
    for st in steps:
        if st.get("op") not in STEPS:
            raise ReplayError(f"unknown CoV step {st!r}")
        pres = STEPS[st["op"]](pres, st)
        _det1(pres)
    return pres


def check_cert(pres, steps, path, cap=None, cyclic=True):
    """Replay a stable certificate: the CoV ``steps`` on ``pres``, then ``path`` on the image. Returns the image.

    That the group is trivial follows from the image replaying to the trivial presentation.
    """
    image = apply_steps(pres, steps)
    replay(image, path, cyclic=cyclic, cap=cap)
    return image
