"""The CoV steps the ported engines can use: ACSolverES's 24 auto-CoV maps, and the full CoV family.

An expander maps an engine state (a canonical pair over ``a b c d`` = ``Y y X x``) to
``(neighbors, n_generated, n_valid)``: ``neighbors`` are ``(canonical state, move)`` in a fixed order, first
occurrence kept.
"""
from acx.core.words import Presentation

from .engine import canonical_pair, from_xy, reduce_word

MAX_RIGHT_POWER = 6
_TO_INT = {"d": 1, "c": -1, "b": 2, "a": -2}
_TO_CHR = {v: k for k, v in _TO_INT.items()}


def _auto_maps():
    """ACSolverES's ``AUTO_COV_MAPS``: x -> x y^k, then y -> y x^k, k = -6..-1, 1..6, in that order."""
    maps = []
    for gen, pos, neg in (("x", "y", "Y"), ("y", "x", "X")):
        for k in range(-MAX_RIGHT_POWER, MAX_RIGHT_POWER + 1):
            if k:
                image = gen + (pos * k if k > 0 else neg * -k)
                inv_image = "".join({"x": "X", "X": "x", "y": "Y", "Y": "y"}[c] for c in reversed(image))
                table = {from_xy(gen): from_xy(image), from_xy(gen.upper()): from_xy(inv_image)}
                maps.append((f"{gen}_right_{k:+d}", table))
    return tuple(maps)


AUTO_MAPS = _auto_maps()


def auto_cov(max_total=None):
    """The 24 auto-CoV maps (``auto_cov_successors``); with ``max_total`` the original strict length bound."""
    def expander(state):
        out, batch = [], set()
        for name, table in AUTO_MAPS:
            r1, r2 = (reduce_word("".join(table.get(c, c) for c in w)) for w in state)
            if max_total is not None and len(r1) + len(r2) >= max_total:
                continue
            nxt = canonical_pair(r1, r2)
            if nxt in batch:
                continue
            batch.add(nxt)
            out.append((nxt, {"move_type": "auto_cov", "automorphism": name}))
        return out, len(AUTO_MAPS), len(out)
    return expander


def to_ints(w):
    return tuple(_TO_INT[c] for c in w)


def to_chars(w):
    return "".join(_TO_CHR[a] for a in w)


def isolating_z_count(image):
    """Letters ``z`` in the isolating relator after substitution; 1 means the step is an automorphism of F2."""
    from acx.core.words import reduce
    return sum(abs(a) == 3 for a in reduce(image.substituted[image.iso_index]))


def full_cov(images_fn):
    """Every CoV image of the state from ``images_fn(Presentation) -> iterable of acx.cov.CoVImage``.

    The engine's state is the presentation the images are taken of, so a move records the steps that replay it
    (``acx.cov.apply_steps``) from the logged ``from_state``. ``aut`` says whether the step is an automorphism (one
    ``z`` in the isolating relator), which decides AC path against stable certificate.
    """
    def expander(state):
        pres = Presentation(2, (to_ints(state[0]), to_ints(state[1])))
        out, batch, generated = [], set(), 0
        for im in images_fn(pres):
            generated += 1
            r1, r2 = (reduce_word(to_chars(r)) for r in im.pres.rels)
            if not r1 or not r2:
                continue
            nxt = canonical_pair(r1, r2)
            if nxt in batch:
                continue
            batch.add(nxt)
            out.append((nxt, {"move_type": "full_cov", "from_state": state, "w": to_chars(im.w), "gen": im.gen,
                              "iso_index": im.iso_index, "expr": list(im.expr),
                              "substituted": [list(r) for r in im.substituted], "n_subs": im.n_subs,
                              "aut": isolating_z_count(im) == 1}))
        return out, generated, len(out)
    return expander


def union(*expanders):
    """The neighbors of each expander in turn, a state kept at its first occurrence."""
    def expander(state):
        out, batch, generated = [], set(), 0
        for ex in expanders:
            nb, g, _ = ex(state)
            generated += g
            for nxt, move in nb:
                if nxt not in batch:
                    batch.add(nxt)
                    out.append((nxt, move))
        return out, generated, len(out)
    return expander
