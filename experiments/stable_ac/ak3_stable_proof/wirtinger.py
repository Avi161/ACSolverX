"""Corrected Wirtinger presentation W (Fig 24 of arXiv:2408.15332v2) + the Prop-12 /
Lemma-11 descendant generator — every leaf is stably AC-trivial BY CONSTRUCTION and
ships a mechanical certificate.

W transcription verified VISUALLY against the rendered PDF page 44 (the txt extraction
scrambles inverse superscripts; three relators differ from a naive txt reading. The
only difference vs MMS02's printed presentation is relator 13: x4 x12 x4^-1 here vs
the misprint x5 x12 x5^-1 there — confirmed against the MMS02 PDF).

Pipeline (all Lemma-11 mechanical, certificate-step granular):
  start  = <x1..x14 | r1..r14 minus r_k, w>   (Prop 12: stably AC-trivial for any word
                                               w with exponent sum +-1)
  cascade: eliminate generators one at a time (each via a relator containing it exactly
           once), until 3 (or 2) generators remain
  rename : relabel survivors to 1..n
The paper's own example (delete r6; eliminate x1..x5,x7..x9,x11..x13; rename
x10,x14,x6 -> x,y,z) is reproduced by ``paper_family()`` and cross-checked against the
printed relators (Section 9.2.2, lines 2641-2643 of the txt).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from certificate import make_certificate  # noqa: E402
from presentation import free_reduce  # noqa: E402
from stable_moves import LengthCapExceeded, eliminate, occurrences  # noqa: E402

# x_i = A x_j A^-1  encoded as the relator  x_i^-1 . A . x_j . A^-1
W_CORRECTED = (
    (-1, 10, 14, -10),      # x1  = x10 x14 x10^-1
    (-2, -10, 1, 10),       # x2  = x10^-1 x1 x10
    (-3, -1, 2, 1),         # x3  = x1^-1 x2 x1
    (-4, -6, 3, 6),         # x4  = x6^-1 x3 x6
    (-5, 12, 4, -12),       # x5  = x12 x4 x12^-1
    (-6, -7, 5, 7),         # x6  = x7^-1 x5 x7
    (-7, -4, 6, 4),         # x7  = x4^-1 x6 x4
    (-8, 1, 7, -1),         # x8  = x1 x7 x1^-1
    (-9, -11, 8, 11),       # x9  = x11^-1 x8 x11
    (-10, 14, 9, -14),      # x10 = x14 x9 x14^-1
    (-11, -2, 10, 2),       # x11 = x2^-1 x10 x2
    (-12, -1, 11, 1),       # x12 = x1^-1 x11 x1
    (-13, 4, 12, -4),       # x13 = x4 x12 x4^-1   <- the corrected relator
    (-14, 1, 13, -1),       # x14 = x1 x13 x1^-1
)
W_MISPRINT = tuple(
    (-13, 5, 12, -5) if r[0] == -13 else r for r in W_CORRECTED
)
N_W = 14


def exponent_sum(w):
    return sum(1 if a > 0 else -1 for a in w)


class Cascade:
    """Tracks a presentation through deletions/eliminations, keeping original generator
    labels and relator tags, emitting certificate steps, recording every state."""

    def __init__(self, relators=W_CORRECTED, delete_k=6, w=(-10, 14, 6), l_cap=64):
        if exponent_sum(w) not in (1, -1):
            raise ValueError(f"w must have exponent sum +-1, got {exponent_sum(w)}")
        self.l_cap = l_cap
        self.delete_k = delete_k
        self.w_original = list(w)
        # current state: list of (tag, relator-as-int-list) with CURRENT generator ids
        self.rels = [(f"r{i + 1}", list(r)) for i, r in enumerate(relators)
                     if i + 1 != delete_k] + [("w", free_reduce(list(w)))]
        # original generator label -> current id (1-based); None once eliminated
        self.cur = {g: g for g in range(1, N_W + 1)}
        self.n_gen = N_W
        self.steps = []
        self.states = [self._state()]

    def _state(self):
        return tuple(list(r) for _, r in self.rels)

    def current_id(self, orig_gen):
        return self.cur[orig_gen]

    def alive(self):
        return [g for g, c in self.cur.items() if c is not None]

    def eliminate_gen(self, orig_gen, prefer_tag=None):
        """Eliminate original generator `orig_gen` via a relator containing it exactly
        once (preferring `prefer_tag`, default its defining relator r<orig_gen>)."""
        g = self.cur[orig_gen]
        if g is None:
            raise ValueError(f"x{orig_gen} already eliminated")
        prefer = prefer_tag or f"r{orig_gen}"
        cand = [i for i, (tag, r) in enumerate(self.rels)
                if len(occurrences(r, g)) == 1]
        if not cand:
            raise LengthCapExceeded(f"no exactly-once relator for x{orig_gen}")
        ri = next((i for i in cand if self.rels[i][0] == prefer), cand[0])
        state = self._state()
        new_state, new_ngen, step = eliminate(state, self.n_gen, g, ri, l_cap=self.l_cap)
        step["orig_gen"] = orig_gen
        step["via_tag"] = self.rels[ri][0]
        tags = [tag for i, (tag, _) in enumerate(self.rels) if i != ri]
        self.rels = [(tag, list(r)) for tag, r in zip(tags, new_state)]
        self.n_gen = new_ngen
        for og, c in self.cur.items():
            if c is None:
                continue
            if og == orig_gen:
                self.cur[og] = None
            elif c > g:
                self.cur[og] = c - 1
        self.steps.append(step)
        self.states.append(self._state())

    def relabel_to(self, orig_order):
        """Final relabel: orig_order[i] (original label) becomes generator i+1."""
        from stable_moves import substitute_word  # noqa: F401  (unused; keep imports tight)
        perm = {}
        for new_id, og in enumerate(orig_order, start=1):
            c = self.cur[og]
            if c is None:
                raise ValueError(f"x{og} was eliminated")
            perm[c] = new_id
        if sorted(perm.keys()) != list(range(1, self.n_gen + 1)):
            raise ValueError("orig_order must cover exactly the surviving generators")
        state = self._state()
        new_state = []
        for r in state:
            new_state.append([(1 if a > 0 else -1) * perm[abs(a)] for a in r])
        self.rels = [(tag, r) for (tag, _), r in zip(self.rels, new_state)]
        inv_cur = {c: og for og, c in self.cur.items() if c is not None}
        self.cur = {og: (perm[c] if c is not None else None) for og, c in self.cur.items()}
        self.steps.append({"type": "relabel", "perm": {str(k): v for k, v in perm.items()},
                           "invert": []})
        self.states.append(self._state())

    def certificate(self, name, claim_suffix=""):
        w_str = self.w_original
        return make_certificate(
            name=name,
            claim=("Start = corrected unknot Wirtinger presentation W (Fig 24, "
                   f"arXiv:2408.15332v2) minus relator r{self.delete_k}, plus w={w_str} "
                   "(exponent sum +-1) — stably AC-trivial by Proposition 12; every step "
                   "is a Lemma-11 elimination (or final relabel), so the end presentation "
                   "is stably AC-trivial by construction. " + claim_suffix),
            states_with_ngen=list(zip(self.states,
                                      [N_W - i for i in range(len(self.states))]
                                      if False else self._ngen_seq())),
            steps=self.steps,
            end_is_trivial=False,
            meta={"source": "W corrected (PDF p.44, visually verified)",
                  "delete_k": self.delete_k, "w_original": w_str},
        )

    def _ngen_seq(self):
        seq = [N_W]
        for st in self.steps:
            seq.append(seq[-1] - 1 if st["type"] == "eliminate" else seq[-1])
        return seq


PAPER_ELIM_ORDER = [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13]
PAPER_RENAME = [10, 14, 6]          # x10 -> x(1), x14 -> y(2), x6 -> z(3)


def paper_family(w=(-10, 14, 6), relators=W_CORRECTED, delete_k=6):
    """Reproduce Section 9.2.2's 3-generator family derivation. Default w = x10^-1 x14 x6,
    which survives untouched and lands as x^-1 y z after the rename (the Appendix-F
    analog choice)."""
    c = Cascade(relators=relators, delete_k=delete_k, w=w)
    for og in PAPER_ELIM_ORDER:
        c.eliminate_gen(og)
    c.relabel_to(PAPER_RENAME)
    return c


def eliminate_final_via_w(cascade):
    """If the w-relator has a generator occurring exactly once, eliminate it -> 2 gens."""
    wi = next(i for i, (tag, _) in enumerate(cascade.rels) if tag == "w")
    tag, wrel = cascade.rels[wi]
    for g in range(1, cascade.n_gen + 1):
        if len(occurrences(wrel, g)) == 1:
            og = next(o for o, cc in cascade.cur.items() if cc == g)
            cascade.eliminate_gen(og, prefer_tag="w")
            return True
    return False
