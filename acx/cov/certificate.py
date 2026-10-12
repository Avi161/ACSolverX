"""The certificate checker: replays a CoV transform from its typed steps, independent of the enumeration.

Each step checks the hypotheses of its part of Lemma 11, and ``|det| = 1`` must hold after every step.
"""
from ..core.words import Presentation, canonical_word, fmt, reduce, renumber, substitute_generator
from ..verify.replay import ReplayError, abs_det, replay
from .family import MIN_W_LEN
from .substitution import X, Y, Z


def _require_det_one(pres):
    """Raise ``ReplayError`` unless ``|det| = 1``."""
    if abs_det(pres) != 1:
        raise ReplayError(f"|det| != 1 at {pres}")


def _define(pres, step):
    """Step ``define``: add the generator ``z`` with the relator ``Z w``."""
    w = tuple(step["word"])
    bad_row = pres.n_gen != 2 or len(pres.rels) != 2
    bad_word = len(w) < MIN_W_LEN or reduce(w, False) != w or any(abs(a) > 2 for a in w)
    if bad_row or bad_word:
        raise ReplayError(f"cannot define z = {fmt(w)} on {pres}")
    return Presentation(3, pres.rels + ((-Z,) + w,))


def _substitute(pres, step):
    """Step ``substitute``: each relator is the old one with ``w`` put for ``z`` (up to rotation and inversion)."""
    new_rels = tuple(tuple(r) for r in step["rels"])
    if pres.n_gen != 3 or len(new_rels) != 2 or pres.rels[2][:1] != (-Z,):
        raise ReplayError("substitute needs the defined presentation")
    w = pres.rels[2][1:]
    for old, new in zip(pres.rels, new_rels):
        if canonical_word(reduce(substitute_generator(new, Z, w))) != canonical_word(reduce(old)):
            raise ReplayError(f"{fmt(new)} is not {fmt(old)} with w put for z")
    return Presentation(3, new_rels + pres.rels[2:])


def _eliminate(pres, step):
    """Step ``eliminate``: solve the isolating relator for ``g`` and put ``expr`` for ``g`` in the others."""
    g, target, expr = step["gen"], step["target"] - 1, tuple(step["expr"])
    if pres.n_gen != 3 or g not in (X, Y) or target not in (0, 1) or any(abs(a) == g for a in expr):
        raise ReplayError(f"bad elimination {step}")
    isolating = pres.rels[target]
    occurrences = sum(abs(a) == g for a in reduce(isolating))
    if occurrences != 1 or reduce(substitute_generator(isolating, g, expr)):
        raise ReplayError(f"{fmt(isolating)} is not of the form {'xy'[g - 1]}^-1 expr")
    survivors = tuple(renumber(substitute_generator(r, g, expr), g) for i, r in enumerate(pres.rels) if i != target)
    if not all(survivors):
        raise ReplayError("an empty relator remains")
    return Presentation(2, survivors)


STEPS = {"define": _define, "substitute": _substitute, "eliminate": _eliminate}


def apply_steps(pres, steps):
    """The image of ``pres`` under the certificate ``steps`` (``CoVImage.steps``), re-derived without the enumerator.

    Checks the hypotheses of each Lemma 11 step (the isolating relator has the form ``g^-1 expr`` with ``expr`` free of
    ``g``) and ``|det| = 1`` after each; raises ``ReplayError`` on any violated check.
    """
    _require_det_one(pres)
    for step in steps:
        if step.get("op") not in STEPS:
            raise ReplayError(f"unknown CoV step {step!r}")
        pres = STEPS[step["op"]](pres, step)
        _require_det_one(pres)
    return pres


def check_cert(pres, steps, path, cap=None, cyclic=True):
    """Replay a stable certificate: the CoV ``steps`` on ``pres``, then ``path`` on the image. Returns the image.

    That the group is trivial follows from the image replaying to the trivial presentation.
    """
    image = apply_steps(pres, steps)
    replay(image, path, cyclic=cyclic, cap=cap)
    return image
