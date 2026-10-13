"""One-shot change of variables (CoV): the images of a presentation.

An image defines ``z = w(x, y)``, puts ``z`` for ``w`` in the relators, isolates a generator and eliminates it (Lemma 11
of the Two-Hump paper). Lemma 11 is stable AC and gives no path, so a solve of an image is a ``stable_cert`` for the row.
The word operations are in ``substitution``, the choice of ``w`` in ``family``, the checker in ``certificate``.
"""
from dataclasses import dataclass
from itertools import product

from ..aut.autos import SIGNED, apply_pres
from ..core.words import Presentation, fmt, renumber, substitute_generator
from .family import FAMILIES, MAX_LEN, proper_subwords, subwords
from .substitution import X, Y, Z, isolate, occurrences, patterns, substitute, substitute_pattern


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


def class_key(pres):
    """``pres`` up to relator order, rotation, inversion, cyclic reduction and the 8 signed permutations of x, y."""
    return min(apply_pres(pres, (k,)).reduced().canonical().rels for k in SIGNED)


def substitutions(r1, r2, w, exhaustive):
    """``(r1', r2', n_subs)`` for each way of putting ``z`` for ``w``: the one pass of ``substitute`` (rule s), or if
    ``exhaustive`` every pattern of non-overlapping occurrences with at least one taken (``suballpxyb8``)."""
    if not exhaustive:
        (r1_sub, n1), (r2_sub, n2) = substitute(r1, w), substitute(r2, w)
        if n1 + n2:
            yield r1_sub, r2_sub, n1 + n2
        return
    m = len(w)
    patterns1 = patterns(occurrences(r1, w), len(r1), m)
    patterns2 = patterns(occurrences(r2, w), len(r2), m)
    for c1, c2 in product(patterns1, patterns2):
        if c1 or c2:
            yield substitute_pattern(r1, c1, m), substitute_pattern(r2, c2, m), len(c1) + len(c2)


def branches(r1_sub, r2_sub, n_subs, w, gen, max_len=MAX_LEN):
    """Every valid CoV of one substituted pair, eliminating ``gen``: one per isolating relator (rule b)."""
    definition = (-Z,) + w                                   # the relator Z w
    for iso_index, (isolating, other) in enumerate(((r1_sub, r2_sub), (r2_sub, r1_sub))):
        expr = isolate(isolating, gen)
        if expr is None:
            continue
        image_rels = tuple(renumber(substitute_generator(r, gen, expr), gen) for r in (other, definition))
        if all(image_rels) and (max_len is None or max(map(len, image_rels)) <= max_len):
            yield CoVImage(Presentation(2, image_rels), w, gen, iso_index, expr, (r1_sub, r2_sub), n_subs)


def enumerate_images(pres, max_len=MAX_LEN, family="subnc2pxysb"):
    """All CoV images of the 2-generator, 2-relator ``pres`` in the ``family`` (``acx.cov.family``), without ranking:
    ``w`` by (length, word), then each substitution of ``w``, then eliminate x before y, then relator 1 before
    relator 2. Both families read the relators cyclically reduced. ``subnc2pxysb`` substitutes in one pass over each
    relator in its written rotation and drops repeated images; ``suballpxyb8`` keeps the first image of each
    ``class_key`` and drops the row's own class.

    Per image: **define** ``z = w`` (a relator ``Z w``), **substitute** ``z`` for ``w`` / ``w^-1`` in ``r1, r2``,
    **isolate** ``g^+-1`` in one relator (``g = expr(other, z)``), **destabilise** (put ``expr`` for ``g`` in the
    remaining two relators, drop ``g``) and **relabel** the survivors to ``x, y``.
    """
    if pres.n_gen != 2 or len(pres.rels) != 2:
        raise ValueError(f"CoV needs a 2-generator, 2-relator presentation, got {pres}")
    if family not in FAMILIES:
        raise ValueError(f"family {family!r} not in {FAMILIES}")
    exhaustive = family == "suballpxyb8"
    r1, r2 = pres.reduced().rels
    words = proper_subwords(r1, r2) if exhaustive else subwords(r1, r2)
    seen = {class_key(pres)} if exhaustive else set()
    images = []
    for w in words:
        for r1_sub, r2_sub, n_subs in substitutions(r1, r2, w, exhaustive):
            for gen in (X, Y):
                for image in branches(r1_sub, r2_sub, n_subs, w, gen, max_len):
                    key = class_key(image.pres) if exhaustive else image.pres.rels
                    if key not in seen:
                        seen.add(key)
                        images.append(image)
    return tuple(images)
