"""Stable AC moves as certificate-emitting transforms (Lemma 11 of arXiv:2408.15332).

Two supermoves on (state, n_gen):

* ``stabilize``  — add generator z=n_gen+1 with relator z.w^-1 (w a word in the existing
  generators). Justified as a stable-AC equivalence by Lemma 11 applied in reverse (the
  new relator isolates z, and substituting z:=w in the other relators changes nothing
  because they do not contain z).
* ``eliminate``  — Lemma 11 forward: pick a relator in which some generator g occurs
  EXACTLY once (as a cyclic word); rotating it to  g.v  gives g = v^-1; substitute v^-1
  for g in every other relator, then drop g and that relator. Valid whenever the
  presentation presents the trivial group (all our chains start from one).

Both return ``(new_state, new_n_gen, step)`` where ``step`` is a JSON-ready certificate
step; nothing is mutated in place. States are tuples of int-list relators (see
presentation.py). The certificate verifier re-checks every precondition independently —
these functions are the *engine*, not the *proof*.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from presentation import (  # noqa: E402
    cyclic_reduce, free_reduce, inverse_word,
)


class LengthCapExceeded(Exception):
    pass


def occurrences(rel, gen):
    """Indices of letters +-gen in rel."""
    return [i for i, a in enumerate(rel) if abs(a) == gen]


def substitute_word(word, gen, sub):
    """Replace every +gen by sub and every -gen by inverse(sub); free reduction NOT applied."""
    inv = inverse_word(sub)
    out = []
    for a in word:
        if a == gen:
            out.extend(sub)
        elif a == -gen:
            out.extend(inv)
        else:
            out.append(a)
    return out


def stabilize(state, n_gen, w):
    """<gens | rels>  ->  <gens+z | rels, z.w^-1>.  w: word in generators 1..n_gen."""
    if any(abs(a) > n_gen or a == 0 for a in w):
        raise ValueError(f"w uses letters outside 1..{n_gen}: {w}")
    z = n_gen + 1
    w = free_reduce(list(w))
    z_rel = cyclic_reduce([z] + inverse_word(w))
    new_state = tuple(list(r) for r in state) + (z_rel,)
    step = {"type": "stabilize", "z": z, "w": list(w)}
    return new_state, n_gen + 1, step


def find_eliminable(state, n_gen):
    """All (gen, ri) with exactly one occurrence of +-gen in relator ri (cyclic word)."""
    out = []
    for ri, r in enumerate(state):
        for gen in range(1, n_gen + 1):
            if len(occurrences(r, gen)) == 1:
                out.append((gen, ri))
    return out


def eliminate(state, n_gen, gen, ri, l_cap=64):
    """Lemma-11 elimination of ``gen`` via relator ``ri`` (must contain +-gen exactly once).

    Renumbering: generators > gen shift down by one so the result uses ids 1..n_gen-1.
    Raises LengthCapExceeded if any substituted relator exceeds l_cap after reduction.
    """
    r = list(state[ri])
    occ = occurrences(r, gen)
    if len(occ) != 1:
        raise ValueError(f"generator {gen} occurs {len(occ)} times in relator {ri}, need exactly 1")
    inverted = r[occ[0]] == -gen
    if inverted:
        r = inverse_word(r)
        occ = occurrences(r, gen)
    rot = occ[0]
    r = r[rot:] + r[:rot]              # now r = [gen] + v
    v = r[1:]                          # gen = v^-1 in the group
    assert all(abs(a) != gen for a in v)
    sub = inverse_word(v)

    def renum(word):
        return [(1 if a > 0 else -1) * (abs(a) - 1) if abs(a) > gen else a for a in word]

    new_rels = []
    for j, other in enumerate(state):
        if j == ri:
            continue
        nr = cyclic_reduce(substitute_word(list(other), gen, sub))
        if len(nr) > l_cap:
            raise LengthCapExceeded(
                f"relator {j} grew to {len(nr)} > l_cap={l_cap} eliminating gen {gen}")
        new_rels.append(renum(nr))
    step = {"type": "eliminate", "gen": gen, "ri": ri,
            "inverted": bool(inverted), "rot": int(rot), "sub": list(sub)}
    return tuple(new_rels), n_gen - 1, step


# ----------------------------------------------------------------- classic AC moves
# (needed by the h-move replayer and by certificates for plain AC sequences)

def concat_move(state, i, j, sign):
    """AC'1:  r_i -> free_reduce(r_i . r_j^sign),  i != j, sign in {+1,-1}."""
    if i == j:
        raise ValueError("concat needs i != j")
    rj = list(state[j]) if sign == 1 else inverse_word(state[j])
    new = free_reduce(list(state[i]) + rj)
    out = [list(r) for r in state]
    out[i] = new
    step = {"type": "concat", "i": i, "j": j, "sign": int(sign)}
    return tuple(out), step


def conjugation_move(state, i, g):
    """AC'2:  r_i -> free_reduce(g . r_i . g^-1),  g a single signed generator letter.
    Free reduction ONLY (cyclic reduction would undo the conjugation)."""
    new = free_reduce([g] + list(state[i]) + [-g])
    out = [list(r) for r in state]
    out[i] = new
    step = {"type": "conjugation", "i": i, "g": int(g)}
    return tuple(out), step


def invert_move(state, i):
    """AC2:  r_i -> r_i^-1."""
    out = [list(r) for r in state]
    out[i] = inverse_word(state[i])
    step = {"type": "invert", "i": i}
    return tuple(out), step
