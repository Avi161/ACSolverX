"""One-shot change of variables (CoV): the images of a presentation.

An image defines ``z = w(x, y)``, puts ``z`` for ``w`` in the relators, isolates a generator and eliminates it (Lemma 11
of the Two-Hump paper). Lemma 11 is stable AC and gives no path, so a solve of an image is a ``stable_cert`` for the row.
The word operations are in ``substitution``, the choice of ``w`` in ``family``, the checker in ``certificate``.
"""
from dataclasses import dataclass

from ..core.words import Presentation, fmt
from .certificate import ReplayError, apply_steps, check_cert                # noqa: F401  (kept importable from here)
from .family import FAMILY_TAG, MAX_LEN, MIN_TRANSFORMED, MIN_W_LEN, subwords   # noqa: F401
from .substitution import X, Y, Z, isolate, relabel, substitute, substitute_generator


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
    """Every valid CoV of ``(r1, r2)`` for one ``w`` and one eliminated ``gen``: one per isolating relator (rule b)."""
    r1_sub, n1 = substitute(r1, w)
    r2_sub, n2 = substitute(r2, w)
    if n1 + n2 == 0:
        return
    definition = (-Z,) + w                                   # the relator Z w
    for iso_index, (isolating, other) in enumerate(((r1_sub, r2_sub), (r2_sub, r1_sub))):
        expr = isolate(isolating, gen)
        if expr is None:
            continue
        image_rels = tuple(relabel(substitute_generator(r, gen, expr), gen) for r in (other, definition))
        if all(image_rels) and (max_len is None or max(map(len, image_rels)) <= max_len):
            yield CoVImage(Presentation(2, image_rels), w, gen, iso_index, expr, (r1_sub, r2_sub), n1 + n2)


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
    seen, images = set(), []
    for w in subwords(r1, r2):
        for gen in (X, Y):
            for image in branches(r1, r2, w, gen, max_len):
                if image.pres.rels not in seen:
                    seen.add(image.pres.rels)
                    images.append(image)
    return tuple(images)
