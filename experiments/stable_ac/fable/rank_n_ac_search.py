"""Rank-N stable Andrews-Curtis search with a thickenability objective (task A7).

This is the first search on the fable line that moves in **rank-N AC space directly**
(FRAMING.md route R4: "no computational method has ever searched AC4/AC5 space
directly").  Everything else in the repo's environment stack is rank-2.

Why rank N and not rank 2
-------------------------
`S3_SUBDIVISION_INVARIANCE.md` proved that a *triangulation* (chord refinement) is a CW
subdivision, so it can never change the predicate ``gamma_N = 0``: the naive
"triangulate AK(3) to rank 9 and test thickenability" route is a provable no-op.  The
escape hatch identified there is exactly the hypothesis the theorem needs -- a
stabilized generator used **three or more times**.  That is what a genuine AC search at
rank N does and what a triangulation cannot do: the composite move
``r_i <- r_i * g r_j^eps g^-1`` copies letters of ``r_j`` (including stabilized letters)
into ``r_i``, raising occurrence multiplicities past 2 and leaving the subdivision
regime.  So the object of this module is: start at a rank-9 triangulation, then *walk*
with real AC moves, hunting for a member of the stable class with ``gamma_N = 0``.

Direction of every bound used here (filed trap
``experiments/lessons/parallel-runs-and-bound-direction.md``)
----------------------------------------------------------------------------------
* the randomized hill-climb (:func:`hunt_defect`) exhibits an explicit compatible
  rotation system, so it bounds ``gamma_N`` from **ABOVE**.  An upper bound of 0 is a
  *proof* of thickenability (after independent re-verification).  Silence -- "no
  defect-0 rotation found" -- bounds **nothing** and is never evidence that
  ``gamma_N > 0``;
* the exact census :func:`neuwirth_rank_n.gamma_N_factorial_n` gives **equality** when
  the family fits under the cap;
* the Euler sparsity certificate (``|E| > 3|V| - 6``) is the only *lower*-bound tool used
  and it is only ever used to prune.

Units: ``defect`` here is the UNHALVED Neuwirth defect ``|A| - |C| + 2L - |AC|``, the
same convention as ``gamma_N_factorial_n``'s ``minimum_defect``; ``gamma_N = defect / 2``.

Calibration is mandatory before any null is read
------------------------------------------------
``experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md``: a one-sided
hunt's silence is worth exactly its MEASURED detection rate.  Two ladders are built in
:func:`run_calibration`:

* **ladder A (realistic)** -- members of AK(2)'s AC class (``ak2_members.jsonl``, verdict
  ``NOT_SPHERICAL``, so ``gamma_N >= 1`` at rank 2).  AK(2) is AC-trivial, hence every
  member is AC-trivial, hence stably AC-trivial, hence its stable class *does* contain a
  thickenable member.  Triangulated to rank 8/9 and searched with the identical budget;
* **ladder B (distance-calibrated)** -- the standard rank-9 presentation scrambled by
  ``k`` random AC1-AC3 moves.  Here a ``gamma_N = 0`` state is known to sit within ``k``
  moves of the start, so the detection rate as a function of ``k`` measures the search's
  reach in AC-move distance directly.

Move set (project numbering, ``FRAMING.md`` section 1)
------------------------------------------------------
``AC1`` invert, ``AC2`` multiply, ``AC3`` conjugate by one generator, the composite
"conjugated multiply" ``AC3;AC2;AC3-back``, ``AC4`` stabilize, ``AC5`` destabilize
(legal only when the relator is a single generator occurring in no other relator).
Free reduction is applied always; the state key is on cyclically-reduced words
(``experiments/lessons/harvest-dedup-on-reduced-forms.md`` -- exact-word keys waste
~97% of pops on conjugacy churn).

File ownership: this module and ``tests/test_rank_n_ac_search.py`` only.  It shares no
code with ``high_rank_refine.py`` / ``high_rank_gamma_sweep.py`` (another agent's) --
the triangulation helper below is deliberately an independent implementation.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from dataclasses import dataclass
from math import factorial

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import neuwirth_rank_n as RN            # noqa: E402
from experiments.stable_ac.fable.witness_check_n import (                # noqa: E402
    AuditContradiction,
    WitnessError,
    check_witness_n,
)

__all__ = [
    "ALPHABET",
    "Pres",
    "make",
    "Limits",
    "inverse",
    "free_reduce",
    "cyclic_reduce",
    "is_freely_reduced",
    "canonical_key",
    "abelian_invariant",
    "enumerate_moves",
    "sample_moves",
    "apply_move",
    "triangulate",
    "triangulation_certificate",
    "standard_presentation",
    "scramble",
    "LinkCache",
    "hunt_defect",
    "independent_defect",
    "verify_defect_zero",
    "SearchResult",
    "search",
    "stabilize_k",
    "run_calibration",
    "load_ak2_ladder",
    "summarise",
    "AK3",
    "DEFAULT_CENSUS_CAP",
]

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

#: AK(3) in the repo's spelling (S1_TRIANGULATION_LEMMA.md section 4.4).
AK3 = (("x", "y"), ("xyxYXY", "xxxYYYY"))

#: Exact-census ceiling.  ``prod_g (deg(g) - 1)!`` above this is not re-run exactly.
DEFAULT_CENSUS_CAP = 200_000


# ======================================================================================
# 1.  word algebra (self-contained; rank-generic)
# ======================================================================================


def inverse(w: str) -> str:
    """``w^-1``: reverse and swap case."""
    return w[::-1].swapcase()


def free_reduce(w: str) -> str:
    out: list = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyclic_reduce(w: str) -> str:
    w = free_reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = free_reduce(w[1:-1])
    return w


def is_freely_reduced(w: str) -> bool:
    return all(a != b.swapcase() for a, b in zip(w, w[1:]))


def letters_of(w: str) -> set:
    return {c.lower() for c in w}


# ======================================================================================
# 2.  presentations
# ======================================================================================


@dataclass(frozen=True)
class Pres:
    """A balanced presentation: an ordered generator tuple and an ordered relator tuple.

    Relators are always kept **freely reduced** and non-empty.  Generators are single
    lowercase letters; the uppercase form of a letter denotes its inverse.
    """

    gens: tuple
    rels: tuple

    @property
    def rank(self) -> int:
        return len(self.gens)

    @property
    def total_length(self) -> int:
        return sum(len(r) for r in self.rels)

    def balanced(self) -> bool:
        return len(self.gens) == len(self.rels)

    def validate(self) -> None:
        if not self.balanced():
            raise ValueError(f"unbalanced: {len(self.gens)} gens, {len(self.rels)} rels")
        if len(set(self.gens)) != len(self.gens):
            raise ValueError("duplicate generator")
        for g in self.gens:
            if len(g) != 1 or g not in ALPHABET:
                raise ValueError(f"bad generator {g!r}")
        alphabet = set(self.gens) | {g.upper() for g in self.gens}
        for r in self.rels:
            if not r:
                raise ValueError("empty relator")
            if any(c not in alphabet for c in r):
                raise ValueError(f"relator {r!r} outside {self.gens}")
            if not is_freely_reduced(r):
                raise ValueError(f"relator {r!r} is not freely reduced")

    def occurrences(self, g: str) -> int:
        return sum(r.count(g) + r.count(g.upper()) for r in self.rels)

    def all_generators_occur(self) -> bool:
        return all(self.occurrences(g) > 0 for g in self.gens)

    def as_json(self) -> dict:
        return {"gens": list(self.gens), "rels": list(self.rels)}


def make(gens, rels) -> Pres:
    p = Pres(tuple(gens), tuple(free_reduce(r) for r in rels))
    p.validate()
    return p


def standard_presentation(rank: int, gens=None) -> Pres:
    """``<a_1..a_N | a_1,...,a_N>`` -- thickenable, ``gamma_N = 0``, the AC target."""
    if gens is None:
        gens = tuple(ALPHABET[:rank])
    gens = tuple(gens)
    return Pres(gens, tuple(gens))


# ======================================================================================
# 3.  canonical key (dedup on cyclically-reduced forms)
# ======================================================================================


def _necklace(w: str) -> str:
    """Lex-min over all rotations of ``w`` and of ``w^-1`` (both cyclically reduced)."""
    w = cyclic_reduce(w)
    if not w:
        return ""
    best = None
    for word in (w, inverse(w)):
        n = len(word)
        doubled = word + word
        for i in range(n):
            cand = doubled[i:i + n]
            if best is None or cand < best:
                best = cand
    return best


def _generator_signature(rels, g: str) -> tuple:
    """A relabel-invariant fingerprint of generator ``g`` inside ``rels``."""
    pos = sum(r.count(g) for r in rels)
    neg = sum(r.count(g.upper()) for r in rels)
    lens = tuple(sorted(len(r) for r in rels if g in r or g.upper() in r))
    # sign-symmetric part first so that g <-> g^-1 does not change the block
    return (pos + neg, tuple(sorted((pos, neg))), lens, len(lens))


def canonical_key(pres: Pres) -> tuple:
    """Key on the multiset of cyclically-reduced relators, up to inversion, generator
    renaming and per-generator sign flip.

    The renaming is derived from a relabel-invariant signature; generators whose
    signatures tie keep their incoming relative order.  That makes the key **sound but
    incomplete** -- two genuinely isomorphic states may receive different keys, which
    costs dedup efficiency and never merges distinct states.  (Full canonical labelling
    at rank 9 would be an N! search and is not worth it here.)
    """
    rels = [cyclic_reduce(r) for r in pres.rels]
    rels = [r for r in rels if r]
    gens = list(pres.gens)

    # per-generator sign normalisation: prefer the sign that occurs more often
    flip = set()
    for g in gens:
        pos = sum(r.count(g) for r in rels)
        neg = sum(r.count(g.upper()) for r in rels)
        if neg > pos:
            flip.add(g)
    if flip:
        table = {}
        for g in gens:
            if g in flip:
                table[g] = g.upper()
                table[g.upper()] = g
            else:
                table[g] = g
                table[g.upper()] = g.upper()
        rels = ["".join(table[c] for c in r) for r in rels]

    sig = {g: _generator_signature(rels, g) for g in gens}
    order = sorted(range(len(gens)), key=lambda i: (sig[gens[i]], i))
    relabel = {}
    for new_index, old_index in enumerate(order):
        old = gens[old_index]
        new = ALPHABET[new_index]
        relabel[old] = new
        relabel[old.upper()] = new.upper()
    rels = ["".join(relabel[c] for c in r) for r in rels]
    return (len(pres.gens), tuple(sorted(_necklace(r) for r in rels)))


# ======================================================================================
# 4.  abelianisation invariant (group-preservation proxy, used by the tests)
# ======================================================================================


def _bareiss_abs_det(matrix) -> int:
    """Integer-exact ``|det|`` by fraction-free Gaussian elimination."""
    m = [row[:] for row in matrix]
    n = len(m)
    if n == 0:
        return 1
    sign = 1
    prev = 1
    for k in range(n - 1):
        if m[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if m[i][k] != 0), None)
            if swap is None:
                return 0
            m[k], m[swap] = m[swap], m[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) // prev
            m[i][k] = 0
        prev = m[k][k]
    return abs(sign * m[n - 1][n - 1])


def abelian_invariant(pres: Pres) -> int:
    """``|det|`` of the exponent-sum matrix -- the order of ``H_1`` when finite.

    Invariant under AC1 (row negation), AC2 (row addition), AC3 (no change at all),
    AC4/AC5 (block extension by a unit row/column).  A presentation of the trivial group
    has invariant 1.  This is the group-preservation proxy the tests use where a full
    Todd-Coxeter enumeration would be too slow.
    """
    idx = {g: k for k, g in enumerate(pres.gens)}
    rows = []
    for r in pres.rels:
        row = [0] * len(pres.gens)
        for c in r:
            if c.islower():
                row[idx[c]] += 1
            else:
                row[idx[c.lower()]] -= 1
        rows.append(row)
    return _bareiss_abs_det(rows)


# ======================================================================================
# 5.  the rank-N move set
# ======================================================================================


@dataclass(frozen=True)
class Limits:
    """Search budget knobs.

    ``max_relator_length`` caps the relator a move *rewrites* (a growth cap, matching the
    AC-Solver convention in ``ac_words.apply_move``, so a start state that already
    exceeds it is not frozen); ``max_total_length`` and the rank window ``[min_rank,
    max_rank]`` are checked against the whole child.
    """

    max_relator_length: int = 12
    max_total_length: int = 40
    min_rank: int = 2
    max_rank: int = 11


def _signed(g: str, eps: int) -> str:
    return g if eps > 0 else g.upper()


def _fresh_generator(pres: Pres) -> str | None:
    used = set(pres.gens)
    for c in ALPHABET:
        if c not in used:
            return c
    return None


def apply_move(pres: Pres, move: tuple, limits: Limits = Limits()) -> Pres | None:
    """Apply one move.  Returns ``None`` when the move is illegal or violates a limit.

    Move encodings (all tuples, first entry the kind):

    ``("ac1", i)``                      r_i -> r_i^-1
    ``("ac2", i, j, eps)``              r_i -> freered(r_i * r_j^eps)   (eps = -1 is the
                                        composite AC1;AC2;AC1)
    ``("ac3", i, g, eps)``              r_i -> freered(g^eps r_i g^-eps)
    ``("cmul", i, j, eps, g, delta)``   r_i -> freered(r_i * u r_j^eps u^-1) with
                                        u = g^delta -- the composite AC3;AC2;AC3-back,
                                        the move that actually matters
    ``("ac4",)``                        stabilize: adjoin a fresh z and the relator z
    ``("ac5", i)``                      destabilize: legal only when r_i is a single
                                        generator occurring in no other relator
    """
    kind = move[0]
    rels = list(pres.rels)
    n = len(rels)

    if kind == "ac4":
        if pres.rank + 1 > limits.max_rank:
            return None
        z = _fresh_generator(pres)
        if z is None:
            return None
        if pres.total_length + 1 > limits.max_total_length:
            return None
        return Pres(pres.gens + (z,), pres.rels + (z,))

    if kind == "ac5":
        i = move[1]
        if not 0 <= i < n:
            return None
        if pres.rank - 1 < limits.min_rank:
            return None
        r = rels[i]
        if len(r) != 1:
            return None
        g = r.lower()
        for k, other in enumerate(rels):
            if k == i:
                continue
            if g in other or g.upper() in other:
                return None                       # generator occurs elsewhere: illegal
        if g not in pres.gens:
            return None
        gens = tuple(x for x in pres.gens if x != g)
        new_rels = tuple(r2 for k, r2 in enumerate(rels) if k != i)
        return Pres(gens, new_rels)

    if kind == "ac1":
        i = move[1]
        if not 0 <= i < n:
            return None
        new = inverse(rels[i])
    elif kind == "ac2":
        _, i, j, eps = move
        if not (0 <= i < n and 0 <= j < n) or i == j:
            return None
        piece = rels[j] if eps > 0 else inverse(rels[j])
        new = free_reduce(rels[i] + piece)
    elif kind == "ac3":
        _, i, g, eps = move
        if not 0 <= i < n or g not in pres.gens:
            return None
        u = _signed(g, eps)
        new = free_reduce(u + rels[i] + inverse(u))
    elif kind == "cmul":
        _, i, j, eps, g, delta = move
        if not (0 <= i < n and 0 <= j < n) or i == j:
            return None
        if g not in pres.gens:
            return None
        u = _signed(g, delta)
        piece = rels[j] if eps > 0 else inverse(rels[j])
        new = free_reduce(rels[i] + free_reduce(u + piece + inverse(u)))
    else:
        raise ValueError(f"unknown move kind {kind!r}")

    if not new:
        return None                               # an empty relator is not a legal state
    if len(new) > limits.max_relator_length:
        return None
    rels[i] = new
    total = sum(len(r) for r in rels)
    if total > limits.max_total_length:
        return None
    return Pres(pres.gens, tuple(rels))


def enumerate_moves(pres: Pres, include_composite: bool = True):
    """Every move encoding legal *in shape* at this rank (legality of the result is
    decided by :func:`apply_move`).  Deterministic order."""
    n = len(pres.rels)
    out = []
    for i in range(n):
        out.append(("ac1", i))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for eps in (1, -1):
                out.append(("ac2", i, j, eps))
    for i in range(n):
        for g in pres.gens:
            for eps in (1, -1):
                out.append(("ac3", i, g, eps))
    if include_composite:
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for eps in (1, -1):
                    for g in pres.gens:
                        for delta in (1, -1):
                            out.append(("cmul", i, j, eps, g, delta))
    out.append(("ac4",))
    for i in range(n):
        out.append(("ac5", i))
    return out


#: relative weights of the move kinds when sampling.  ``cmul`` dominates deliberately:
#: it is the only move that raises occurrence multiplicities of stabilized generators
#: past 2, i.e. the only one that leaves the subdivision regime of Theorem S3.
DEFAULT_KIND_WEIGHTS = {
    "ac1": 1.0,
    "ac2": 3.0,
    "ac3": 2.0,
    "cmul": 8.0,
    "ac4": 0.6,
    "ac5": 1.5,
}


def sample_moves(pres: Pres, count: int, rng: random.Random,
                 limits: Limits = Limits(), weights=None, oversample: int = 12):
    """Sample up to ``count`` distinct legal children as ``(move, child)`` pairs.

    Sampling (rather than enumerating) is a budget decision: the full move set at rank 9
    has ~2,900 entries, dominated by ``cmul``, and the objective is far more expensive
    than move generation.  Deterministic given ``rng``.
    """
    weights = dict(DEFAULT_KIND_WEIGHTS if weights is None else weights)
    n = len(pres.rels)
    if n < 2:
        weights.pop("ac2", None)
        weights.pop("cmul", None)
    kinds = sorted(weights)
    w = [weights[k] for k in kinds]
    seen = set()
    out = []
    tries = 0
    limit = max(count * oversample, 24)
    while len(out) < count and tries < limit:
        tries += 1
        kind = rng.choices(kinds, weights=w, k=1)[0]
        if kind == "ac1":
            move = ("ac1", rng.randrange(n))
        elif kind == "ac2":
            i = rng.randrange(n)
            j = rng.randrange(n - 1)
            j = j if j < i else j + 1
            move = ("ac2", i, j, rng.choice((1, -1)))
        elif kind == "ac3":
            move = ("ac3", rng.randrange(n), rng.choice(pres.gens), rng.choice((1, -1)))
        elif kind == "cmul":
            i = rng.randrange(n)
            j = rng.randrange(n - 1)
            j = j if j < i else j + 1
            move = ("cmul", i, j, rng.choice((1, -1)), rng.choice(pres.gens),
                    rng.choice((1, -1)))
        elif kind == "ac4":
            move = ("ac4",)
        else:
            move = ("ac5", rng.randrange(n))
        if move in seen:
            continue
        seen.add(move)
        child = apply_move(pres, move, limits)
        if child is None:
            continue
        if child.rels == pres.rels and child.gens == pres.gens:
            continue
        out.append((move, child))
    return out


# ======================================================================================
# 6.  triangulation helper (independent implementation; S1 section 4.2 left-prefix peel)
# ======================================================================================


def triangulate(pres: Pres, max_relator_length: int = 3):
    """Left-prefix chord peel until every relator has length <= ``max_relator_length``.

    One AC4 per peel; the new generator ``z`` is *defined* to be the peeled length-2
    prefix (Lemma S-a), giving the definition relator ``z (a_1 a_2)^-1`` and shortening
    the peeled relator to ``z a_3 ... a_m``.  Returns ``(triangulated, trace)`` where
    ``trace`` is the list of ``{"gen", "word", "definition", "shortened", "source"}``
    records, ``word`` being the closed-form value of the new generator in the ORIGINAL
    alphabet.

    This is a fresh implementation, deliberately not shared with any other module: an
    independent reimplementation is the point (both must agree with S1 section 4.4).
    """
    pres.validate()
    gens = list(pres.gens)
    rels = list(pres.rels)
    trace = []
    closed = {}                                    # new generator -> word over old gens
    used = set(gens)

    def expand(w: str) -> str:
        out = []
        for c in w:
            base = c.lower()
            if base in closed:
                piece = closed[base]
                out.append(piece if c.islower() else inverse(piece))
            else:
                out.append(c)
        return free_reduce("".join(out))

    changed = True
    while changed:
        changed = False
        for i in range(len(rels)):
            while len(rels[i]) > max_relator_length:
                z = next((c for c in ALPHABET if c not in used), None)
                if z is None:
                    raise ValueError("alphabet exhausted during triangulation")
                used.add(z)
                prefix = rels[i][:2]
                definition = z + inverse(prefix)
                shortened = z + rels[i][2:]
                if not is_freely_reduced(definition) or not is_freely_reduced(shortened):
                    raise ValueError("peel produced an unreduced word")
                closed[z] = expand(prefix)
                trace.append({
                    "gen": z,
                    "prefix": prefix,
                    "word": closed[z],
                    "definition": definition,
                    "shortened": shortened,
                    "source_index": i,
                })
                gens.append(z)
                rels[i] = shortened
                rels.append(definition)
                changed = True
    out = Pres(tuple(gens), tuple(rels))
    out.validate()
    return out, trace


def triangulation_certificate(original: Pres, triangulated: Pres, trace) -> dict:
    """Replay the peel: back-substitute every definition and check what comes out.

    A machine check (S1 section 4.4's "back-substitution check"), not an assertion by the
    generator that produced the triangulation.
    """
    closed = {rec["gen"]: rec["word"] for rec in trace}

    def expand(w: str) -> str:
        prev = None
        cur = w
        while prev != cur:
            prev = cur
            out = []
            for c in cur:
                base = c.lower()
                if base in closed:
                    piece = closed[base]
                    out.append(piece if c.islower() else inverse(piece))
                else:
                    out.append(c)
            cur = free_reduce("".join(out))
        return cur

    images = [expand(r) for r in triangulated.rels]
    definition_words = {rec["definition"] for rec in trace}
    survivors = []
    trivial = 0
    for r, img in zip(triangulated.rels, images):
        if r in definition_words:
            if img == "":
                trivial += 1
            else:
                survivors.append((r, img, "DEFINITION_DID_NOT_VANISH"))
            continue
        survivors.append((r, img, None))
    want = sorted(cyclic_reduce(r) for r in original.rels)
    got = sorted(cyclic_reduce(img) for _r, img, _f in survivors)
    ok = (
        triangulated.balanced()
        and triangulated.rank == original.rank + len(trace)
        and trivial == len(trace)
        and want == got
        and all(flag is None for _r, _i, flag in survivors)
        and abelian_invariant(triangulated) == abelian_invariant(original)
    )
    return {
        "ok": bool(ok),
        "rank_before": original.rank,
        "rank_after": triangulated.rank,
        "peels": len(trace),
        "definitions_vanished": trivial,
        "descendant_images": got,
        "original_relators": want,
        "abelian_invariant_before": abelian_invariant(original),
        "abelian_invariant_after": abelian_invariant(triangulated),
        "max_relator_length_after": max(len(r) for r in triangulated.rels),
    }


def scramble(pres: Pres, moves: int, rng: random.Random,
             limits: Limits = Limits()) -> tuple:
    """Apply ``moves`` random AC1-AC3 moves (no AC4/AC5).  Returns ``(pres, history)``."""
    cur = pres
    history = []
    weights = {"ac1": 1.0, "ac2": 3.0, "ac3": 2.0, "cmul": 4.0}
    guard = 0
    while len(history) < moves and guard < moves * 60:
        guard += 1
        got = sample_moves(cur, 1, rng, limits, weights=weights, oversample=6)
        if not got:
            continue
        move, child = got[0]
        cur = child
        history.append(list(move))
    return cur, history


# ======================================================================================
# 7.  the thickenability hunter (upper bound on gamma_N)
# ======================================================================================


class LinkCache:
    """Per-state link data plus the fast defect evaluator.

    The link dictionary itself is the audited ``neuwirth_rank_n.build_link_n``; only the
    *search* over compatible rotation systems is new here.  The compatible family is a
    product over positive germs of the orderings of that germ's darts with one dart
    pinned as head (``compatible_orders_n``'s convention -- pinning is WLOG because only
    the cyclic order matters); negative germs stay forced by B-reversal.
    """

    __slots__ = ("words", "generators", "data", "positive", "heads", "tails", "base",
                 "census_size", "link_components", "_C", "_seen", "n_darts")

    def __init__(self, pres: Pres):
        self.words = tuple(pres.rels)
        self.generators = tuple(pres.gens)
        self.data = RN.build_link_n(self.words, self.generators)
        data = self.data
        self.n_darts = data.n_darts
        self.positive = [2 * k for k in range(len(self.generators))
                         if data.vertex_darts[2 * k]]
        self.heads = [data.vertex_darts[g][0] for g in self.positive]
        self.tails = [list(data.vertex_darts[g][1:]) for g in self.positive]
        self.link_components = data.link_components
        self.base = (data.n_occurrences - len(data.present_germs)
                     + 2 * data.link_components)
        size = 1
        for g in self.positive:
            size *= factorial(data.degree(g) - 1)
        self.census_size = size
        self._C = [0] * self.n_darts
        self._seen = bytearray(self.n_darts)

    def defect(self, state) -> int:
        C = self._C
        B = self.data.B
        for idx, tail in enumerate(state):
            order = (self.heads[idx],) + tuple(tail)
            m = len(order)
            for k in range(m):
                C[order[k]] = order[(k + 1) % m]
            rev = tuple(B[d] for d in reversed(order))
            for k in range(m):
                C[rev[k]] = rev[(k + 1) % m]
        A = self.data.A
        seen = self._seen
        for i in range(self.n_darts):
            seen[i] = 0
        n_ac = 0
        for start in range(self.n_darts):
            if seen[start]:
                continue
            n_ac += 1
            cur = start
            while not seen[cur]:
                seen[cur] = 1
                cur = A[C[cur]]
        return self.base - n_ac

    def orders_of(self, state) -> dict:
        B = self.data.B
        out = {}
        for idx, germ in enumerate(self.positive):
            order = (self.heads[idx],) + tuple(state[idx])
            out[int(germ)] = [int(d) for d in order]
            out[int(germ ^ 1)] = [int(B[d]) for d in reversed(order)]
        return out


def hunt_defect(pres: Pres, evals: int, rng: random.Random,
                plateau_steps: int = 40, cache: LinkCache | None = None):
    """Randomised hill-climb for a low-defect compatible rotation system.

    Returns ``(best_defect, witness_orders, cache)``.  ``best_defect`` is an **UPPER**
    bound on the unhalved ``gamma_N`` potential: the returned rotation realises it.  A
    return of 0 is a thickenability witness (subject to independent re-verification by
    :func:`verify_defect_zero`); a positive return is **not** evidence of a positive
    lower bound.

    Two neighbourhood moves are used -- a transposition inside one germ's tail and a
    re-insertion (which the transposition alone cannot reach when a germ has degree > 3)
    -- with plateau walking and random restarts, the shape proven out in
    ``gateway_scan.sampled_min_defect``.
    """
    if cache is None:
        cache = LinkCache(pres)
    tails = cache.tails
    movable = [idx for idx, t in enumerate(tails) if len(t) >= 2]
    best = None
    best_state = None
    budget = max(1, evals)
    if not movable:
        state = [t[:] for t in tails]
        return cache.defect(state), cache.orders_of(state), cache
    while budget > 0:
        state = [rng.sample(t, len(t)) for t in tails]
        cur = cache.defect(state)
        budget -= 1
        if best is None or cur < best:
            best, best_state = cur, [t[:] for t in state]
            if best <= 0:
                return best, cache.orders_of(best_state), cache
        stale = 0
        while budget > 0 and stale < plateau_steps:
            idx = rng.choice(movable)
            tail = state[idx]
            m = len(tail)
            if rng.random() < 0.5:
                i, j = rng.randrange(m), rng.randrange(m)
                if i == j:
                    continue
                tail[i], tail[j] = tail[j], tail[i]
                undo = ("swap", i, j)
            else:
                i, j = rng.randrange(m), rng.randrange(m)
                if i == j:
                    continue
                item = tail.pop(i)
                tail.insert(j, item)
                undo = ("move", i, j)
            trial = cache.defect(state)
            budget -= 1
            if trial <= cur:
                stale = 0 if trial < cur else stale + 1
                cur = trial
                if cur < best:
                    best, best_state = cur, [t[:] for t in state]
                    if best <= 0:
                        return best, cache.orders_of(best_state), cache
            else:
                if undo[0] == "swap":
                    _k, i, j = undo
                    tail[i], tail[j] = tail[j], tail[i]
                else:
                    _k, i, j = undo
                    item = tail.pop(j)
                    tail.insert(i, item)
                stale += 1
    return best, (cache.orders_of(best_state) if best_state is not None else None), cache


def independent_defect(pres: Pres, orders: dict) -> dict:
    """Recompute a rotation system's Neuwirth numbers from scratch.

    Deliberately shares **no** code with ``neuwirth_rank_n`` or with :class:`LinkCache`:
    the dart dictionary is rebuilt here from the words.  This is the check that keeps a
    defect-0 hit honest when ``check_witness_n`` refuses the state because the link is
    disconnected (it requires ``L = 1``); ``gamma_N_factorial_n`` alone would share the
    link builder with the hunter and so would not be an independent opinion.
    """
    words = tuple(pres.rels)
    gens = tuple(pres.gens)
    table = {}
    for k, g in enumerate(gens):
        table[g] = (2 * k, 2 * k + 1)
        table[g.upper()] = (2 * k + 1, 2 * k)
    letters = []
    spans = []
    for w in words:
        spans.append((len(letters), len(letters) + len(w)))
        letters.extend(w)
    n = len(letters)
    size = 2 * n
    A = [None] * size
    for lo, hi in spans:
        span = hi - lo
        for k in range(span):
            i, j = lo + k, lo + (k + 1) % span
            A[2 * i + 1] = 2 * j
            A[2 * j] = 2 * i + 1
    B = list(range(size))
    for i in range(n):
        B[2 * i], B[2 * i + 1] = 2 * i + 1, 2 * i
    germ = [0] * size
    for i, c in enumerate(letters):
        germ[2 * i], germ[2 * i + 1] = table[c]

    C = [None] * size
    for v, seq in orders.items():
        v = int(v)
        seq = [int(d) for d in seq]
        if sorted(seq) != sorted(d for d in range(size) if germ[d] == v):
            raise ValueError(f"rotation at germ {v} is not a permutation of its darts")
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    if any(c is None for c in C):
        raise ValueError("rotation does not cover every dart")
    for e in range(size):                        # Neuwirth compatibility B C B = C^-1
        if C[B[C[B[e]]]] != e:
            raise ValueError("rotation is not Neuwirth-compatible")

    def cycles(perm):
        seen = bytearray(size)
        total = 0
        for start in range(size):
            if seen[start]:
                continue
            total += 1
            cur = start
            while not seen[cur]:
                seen[cur] = 1
                cur = perm[cur]
        return total

    AC = [A[C[e]] for e in range(size)]
    seen = bytearray(size)
    L = 0
    for start in range(size):
        if seen[start]:
            continue
        L += 1
        stack = [start]
        seen[start] = 1
        while stack:
            d = stack.pop()
            for nxt in (A[d], C[d]):
                if not seen[nxt]:
                    seen[nxt] = 1
                    stack.append(nxt)
    n_C, n_A, n_AC = cycles(C), cycles(A), cycles(AC)
    return {
        "cycles_C": n_C, "cycles_A": n_A, "cycles_AC": n_AC,
        "link_components": L,
        "defect": n_A - n_C + 2 * L - n_AC,
        "darts": size,
    }


def verify_defect_zero(pres: Pres, orders: dict,
                       census_cap: int = DEFAULT_CENSUS_CAP) -> dict:
    """Independently re-verify a claimed defect-0 rotation system.

    Two independent checks, both required before a hit is recorded:

    1. ``witness_check_n.check_witness_n`` -- a structurally different verifier that
       rebuilds ``D, A, B`` from the words alone and shares no scheme code with the
       hunter.  It requires a connected link (``L = 1``); a defect-0 rotation on a
       disconnected link is recorded as ``link_components > 1`` and left UNVERIFIED by
       this route (``R1E_DISCONNECTED_LINK.md`` Theorem D is the machinery for that case
       and is deliberately not re-implemented here);
    2. the exact census ``gamma_N_factorial_n`` when ``prod_g (deg-1)! <= census_cap``,
       which returns **equality** for ``gamma_N`` rather than a bound.
    """
    report = {
        "check_witness_n": None,
        "check_witness_n_error": None,
        "independent_defect": None,
        "independent_defect_error": None,
        "exact_census": None,
        "verified": False,
    }
    try:
        report["independent_defect"] = independent_defect(pres, orders)
    except Exception as exc:                                       # noqa: BLE001
        report["independent_defect_error"] = f"{type(exc).__name__}: {exc}"
    try:
        got = check_witness_n(pres.rels, {int(k): list(v) for k, v in orders.items()},
                              generators=pres.gens, trivial_group=True)
        report["check_witness_n"] = {
            "defect": got["defect"],
            "link_components": got["link_components"],
            "euler_line": got["euler_line"],
            "ac_bc_orbits": got["ac_bc_orbits"],
            "compatible": got["compatible"],
        }
    except AuditContradiction as exc:
        report["check_witness_n_error"] = f"AuditContradiction: {exc}"
    except WitnessError as exc:
        report["check_witness_n_error"] = f"WitnessError: {exc}"

    census = RN.gamma_N_factorial_n(pres.rels, generators=pres.gens,
                                    cap_rotations=census_cap, keep_accepting=False)
    report["exact_census"] = {
        "status": census["status"],
        "expected_cases": census["expected_cases"],
        "minimum_defect": census.get("minimum_defect"),
        "enumerated_cases": census.get("enumerated_cases"),
    }
    witness_ok = (report["check_witness_n"] is not None
                  and report["check_witness_n"]["defect"] == 0)
    independent_ok = (report["independent_defect"] is not None
                      and report["independent_defect"]["defect"] == 0)
    census_ok = (census["status"] == "OK" and census.get("minimum_defect") == 0)
    routes = []
    if witness_ok:
        routes.append("check_witness_n")
    if independent_ok:
        routes.append("independent_defect")
    if census_ok:
        routes.append("gamma_N_factorial_n")
    report["verified"] = bool(witness_ok or independent_ok or census_ok)
    report["verified_by"] = "+".join(routes) or None
    report["note"] = ("check_witness_n requires a connected link (L = 1); a defect-0 "
                      "rotation on a disconnected link is verified here by "
                      "independent_defect (a from-scratch dart dictionary) and, when "
                      "the family fits the cap, by the exact census.")
    return report


# ======================================================================================
# 8.  the search
# ======================================================================================


@dataclass
class SearchResult:
    label: str
    scheme: str
    start: dict
    start_rank: int
    start_total_length: int
    nodes_used: int
    generations: int
    best_defect: int | None
    best_state: dict | None
    best_rank: int | None
    best_total_length: int | None
    hit: bool
    verification: dict | None
    wall_seconds: float
    seed: int
    budget: dict
    stopped: str
    distinct_states: int
    rank_histogram: dict
    anomalies: list

    @property
    def best_gamma_N(self):
        """``gamma_N = minimum_defect // 2`` -- the project's halved convention."""
        return None if self.best_defect is None else self.best_defect // 2

    def as_json(self) -> dict:
        out = dict(self.__dict__)
        out["best_gamma_N_upper_bound"] = self.best_gamma_N
        return out


def _sparsity_prunes(cache: LinkCache) -> bool:
    """True when the Euler sparsity bound certifies the simple support non-planar.

    This is the only LOWER-bound tool in the module (``gamma_N >= 1``), and it is used
    only to prune -- never to report a verdict.
    """
    data = cache.data
    vertices = data.present_germs
    edges = [k for k in data.class_edges if k[0] != k[1]]
    v_count, e_count = len(vertices), len(edges)
    return v_count >= 3 and e_count > 3 * v_count - 6


def search(start: Pres, nodes: int = 1000, beam: int = 6, branch: int = 12,
           evals: int = 900, seed: int = 0, limits: Limits = Limits(),
           time_budget: float = 240.0, restart_after: int = 6,
           label: str = "", scheme: str = "", census_cap: int = DEFAULT_CENSUS_CAP,
           verbose: bool = False) -> SearchResult:
    """Beam search over rank-N AC space, scored by (defect upper bound, total length).

    ``nodes`` counts *objective evaluations* (hunter calls), which dominate the cost.
    The search stops at the first verified ``gamma_N = 0`` state, at the node budget, or
    at the wall-clock budget -- whichever comes first.  All three stop reasons are
    recorded; none of them is evidence about AC (PROCESS_GUARD.md).
    """
    t0 = time.time()
    rng = random.Random(seed)
    start.validate()

    seen = {canonical_key(start)}
    rank_hist: dict = {}
    anomalies: list = []

    def score(state: Pres):
        cache = LinkCache(state)
        if _sparsity_prunes(cache):
            return None, cache               # certified gamma_N >= 1: prune
        defect, orders, _ = hunt_defect(state, evals, rng, cache=cache)
        return (defect, orders), cache

    nodes_used = 0
    generations = 0
    stopped = "node_budget"
    best = None                              # (defect, total_length, Pres, orders)
    frontier = []

    scored, _cache = score(start)
    nodes_used += 1
    rank_hist[start.rank] = rank_hist.get(start.rank, 0) + 1
    if scored is not None:
        best = (scored[0], start.total_length, start, scored[1])
        frontier = [(scored[0], start.total_length, start)]
    else:
        frontier = [(10 ** 6, start.total_length, start)]

    hit = False
    verification = None
    if best is not None and best[0] == 0:
        verification = verify_defect_zero(start, best[3], census_cap)
        hit = bool(verification["verified"])

    stale_generations = 0
    exhausted = 0
    best_seen_defect = best[0] if best is not None else None

    while not hit and nodes_used < nodes and (time.time() - t0) < time_budget:
        generations += 1
        candidates = []
        local: set = set()
        for _d, _l, state in frontier:
            for _move, child in sample_moves(state, branch, rng, limits):
                if not child.all_generators_occur():
                    continue
                key = canonical_key(child)
                if key in seen or key in local:
                    continue
                local.add(key)
                candidates.append((key, child))
        if not candidates:
            # a beam can walk into a pocket whose whole move neighbourhood is already
            # scored; restart from a fresh scramble of the start rather than stop.
            exhausted += 1
            if exhausted > 12:
                stopped = "frontier_exhausted"
                break
            restart, _hist = scramble(start, rng.randrange(3, 13), rng, limits)
            frontier = [(10 ** 6, restart.total_length, restart)]
            continue
        exhausted = 0
        # Cheap prescreen: the objective is ~1000x the cost of generating a child, so
        # only a slice of the candidates can be scored.  Take most of the slice by total
        # length (shortening is the direction of the standard presentation) but reserve
        # a random share so the beam cannot collapse onto one shortening motif.
        width = max(beam * 3, beam + 4)
        candidates.sort(key=lambda kc: (kc[1].total_length, kc[1].rank))
        cut = (width * 3) // 5
        by_length = candidates[:cut]
        rest = candidates[cut:]
        rng.shuffle(rest)
        keep_pairs = by_length + rest[: max(0, width - len(by_length))]
        keep = []
        for key, child in keep_pairs:
            seen.add(key)                     # only SCORED states enter the seen set
            keep.append(child)
        scored_children = []
        for child in keep:
            if nodes_used >= nodes or (time.time() - t0) >= time_budget:
                break
            got, _c = score(child)
            nodes_used += 1
            rank_hist[child.rank] = rank_hist.get(child.rank, 0) + 1
            if got is None:
                continue
            defect, orders = got
            scored_children.append((defect, child.total_length, child))
            if best is None or (defect, child.total_length) < (best[0], best[1]):
                best = (defect, child.total_length, child, orders)
            if defect == 0:
                report = verify_defect_zero(child, orders, census_cap)
                if report["verified"]:
                    verification = report
                    hit = True
                    best = (0, child.total_length, child, orders)
                    stopped = "verified_hit"
                    break
                # a hunted defect 0 that no independent check confirms is an ANOMALY
                # (a bug in the hunter, not a mathematical outcome) and is recorded.
                anomalies.append({"state": child.as_json(), "verification": report})
        if hit:
            break
        if not scored_children:
            # everything in this slice was pruned by the sparsity certificate; restart
            # rather than stop, so a single non-planar pocket cannot end the search
            exhausted += 1
            if exhausted > 12 or nodes_used >= nodes:
                stopped = "no_scored_children"
                break
            restart, _hist = scramble(start, rng.randrange(3, 13), rng, limits)
            frontier = [(10 ** 6, restart.total_length, restart)]
            continue
        scored_children.sort(key=lambda t: (t[0], t[1], t[2].rank))
        frontier = scored_children[:beam]
        current_best = None if best is None else best[0]
        if (best_seen_defect is not None and current_best is not None
                and current_best >= best_seen_defect):
            stale_generations += 1
        else:
            stale_generations = 0
        best_seen_defect = current_best
        if restart_after and stale_generations >= restart_after:
            stale_generations = 0
            restart, _hist = scramble(start, rng.randrange(2, 6), rng, limits)
            key = canonical_key(restart)
            if key not in seen:
                seen.add(key)
                frontier = [(10 ** 6, restart.total_length, restart)] + frontier[:beam - 1]
        if verbose and best is not None:
            print(f"[search] gen {generations} nodes {nodes_used} "
                  f"best {best[0]} len {best[1]} rank {best[2].rank}", flush=True)

    if (time.time() - t0) >= time_budget and not hit:
        stopped = "time_budget"

    return SearchResult(
        label=label,
        scheme=scheme,
        start=start.as_json(),
        start_rank=start.rank,
        start_total_length=start.total_length,
        nodes_used=nodes_used,
        generations=generations,
        best_defect=None if best is None else best[0],
        best_state=None if best is None else best[2].as_json(),
        best_rank=None if best is None else best[2].rank,
        best_total_length=None if best is None else best[2].total_length,
        hit=hit,
        verification=verification,
        wall_seconds=round(time.time() - t0, 2),
        seed=seed,
        budget={"nodes": nodes, "beam": beam, "branch": branch, "evals": evals,
                "max_relator_length": limits.max_relator_length,
                "max_total_length": limits.max_total_length,
                "min_rank": limits.min_rank, "max_rank": limits.max_rank,
                "time_budget": time_budget},
        stopped=stopped,
        distinct_states=len(seen),
        rank_histogram={str(k): v for k, v in sorted(rank_hist.items())},
        anomalies=anomalies,
    )


# ======================================================================================
# 9.  ladders and the CLI
# ======================================================================================


AK2_MEMBERS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "ak2_members.jsonl")
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")


def load_ak2_ladder(path: str = AK2_MEMBERS, lengths=(12, 13), per_length: int = 6,
                    seed: int = 0):
    """AK(2)-class members with the given total lengths and verdict NOT_SPHERICAL.

    AK(2) is AC-trivial (this repo records a trivialization path at
    ``results/stable_ac/fable/ak2_trivialization_path.json``), so every member of its AC
    class is AC-trivial, hence stably AC-trivial, hence its stable class contains a
    thickenable member.  ``NOT_SPHERICAL`` at rank 2 means the *member itself* is not
    thickenable, which is what makes it a non-trivial positive control.
    Total length ``L`` with both relators of length >= 3 triangulates to rank ``L - 4``.
    """
    buckets: dict = {L: [] for L in lengths}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("verdict") != "NOT_SPHERICAL":
                continue
            L = row.get("total_length")
            if L not in buckets:
                continue
            pair = row.get("canonical")
            if not (isinstance(pair, list) and len(pair) == 2):
                continue
            if min(len(pair[0]), len(pair[1])) < 3:
                continue
            buckets[L].append(tuple(pair))
    rng = random.Random(seed)
    out = []
    for L in lengths:
        pool = sorted(set(buckets[L]))
        rng.shuffle(pool)
        for pair in pool[:per_length]:
            out.append((L, pair))
    return out


def _ladder_a_states(lengths, per_length, seed):
    rows = []
    for L, pair in load_ak2_ladder(lengths=lengths, per_length=per_length, seed=seed):
        base = make(("x", "y"), pair)
        tri, trace = triangulate(base)
        cert = triangulation_certificate(base, tri, trace)
        rows.append({
            "label": f"ak2_L{L}_{'_'.join(pair)}",
            "scheme": "ladder_A:ak2_class_left_prefix_triangulation",
            "base": base,
            "state": tri,
            "certificate": cert,
        })
    return rows


def _ladder_b_states(rank, scramble_depths, per_depth, seed, screen_evals: int = 4000,
                     attempts: int = 40):
    """Standard rank-``rank`` presentation scrambled by ``k`` AC1-AC3 moves.

    Only scrambles whose OWN hunted defect is > 0 are kept.  A scramble that is already
    defect-0 would let the search "win" at node 1 without moving, which measures nothing;
    rejecting those makes the depth-``k`` cell a genuine test of reach: a ``gamma_N = 0``
    state (the standard presentation) is known to sit within ``k`` moves, and the search
    must travel to find one.
    """
    rows = []
    rng = random.Random(seed)
    limits = Limits(max_relator_length=8, max_total_length=4 * rank + 8,
                    min_rank=2, max_rank=rank + 2)
    for k in scramble_depths:
        kept = 0
        tried = 0
        while kept < per_depth and tried < attempts:
            tried += 1
            std = standard_presentation(rank)
            scrambled, history = scramble(std, k, rng, limits)
            if not scrambled.all_generators_occur():
                continue
            defect, _o, _c = hunt_defect(scrambled, screen_evals, rng)
            if defect is None or defect <= 0:
                continue                       # already thickenable: measures nothing
            rows.append({
                "label": f"std{rank}_scramble{k}_r{kept}",
                "scheme": f"ladder_B:scrambled_standard(k={k})",
                "base": std,
                "state": scrambled,
                "certificate": {"ok": True, "scramble_history": history,
                                "start_defect_upper_bound": defect,
                                "screen_evals": screen_evals,
                                "scrambles_rejected_as_already_thickenable": tried - kept - 1,
                                "abelian_invariant": abelian_invariant(scrambled)},
            })
            kept += 1
        if kept == 0:
            rows.append({
                "label": f"std{rank}_scramble{k}_EMPTY",
                "scheme": f"ladder_B:scrambled_standard(k={k})",
                "base": standard_presentation(rank),
                "state": None,
                "certificate": {"ok": False,
                                "reason": f"no scramble at depth {k} in {attempts} "
                                          "attempts had a positive start defect"},
            })
    return [r for r in rows if r["state"] is not None]


def stabilize_k(pres: Pres, k: int) -> Pres:
    """``AC4`` applied ``k`` times: adjoin ``k`` fresh generators and their relators."""
    cur = pres
    for _ in range(k):
        z = _fresh_generator(cur)
        if z is None:
            raise ValueError("alphabet exhausted")
        cur = Pres(cur.gens + (z,), cur.rels + (z,))
    cur.validate()
    return cur


#: The depth-ladder control: an AK(2)-class rank-2 base that is AC-trivial (AK(2) is
#: AC-trivial, so every member of its AC class is) and NOT_SPHERICAL at rank 2, taken
#: verbatim from ``results/stable_ac/fable/ak2_members.jsonl``.  Total length 13, the
#: same as AK(3), so the two ladders are length-matched
#: (``experiments/lessons/contrast-length-confound.md``: a raw gap between two families
#: can be a LENGTH gap in disguise).
DEPTH_LADDER_CONTROL = ("YYxxx", "YxYxYxxx")


def _depth_ladder_states(depths=(0, 1, 2, 3, 4), control=DEPTH_LADDER_CONTROL,
                         reps: int = 1):
    """The rank-filtration ladder: the SAME base searched under rank ceilings 2 + k.

    This is the S0 section 4 filtration ``~^{(k)}`` made operational: rung ``k`` starts
    from the base stabilized ``k`` times and the search may never exceed rank ``2 + k``
    (it may destabilize back down to rank 2 -- otherwise it would not be a stable
    search).  The mechanism under test is the S3 section 4 / S0 section 2 observation
    that at rank 2 four germs carry all 13 letter occurrences, and each extra generator
    adds two germs, i.e. room for the rotation system.

    Two families, identical move sets, identical budgets and identical per-rung seeds:
    AK(3), and a length-matched AC-trivial NOT_SPHERICAL control.  A FLAT ladder on the
    control means the instrument is blind and the AK(3) ladder says nothing.
    """
    families = [
        ("ak3", make(*AK3)),
        ("ak2ctl", make(("x", "y"), control)),
    ]
    rows = []
    for name, base in families:
        for k in depths:
            state = stabilize_k(base, k)
            for rep in range(reps):
                rows.append({
                    "label": f"depth_{name}_k{k}_r{rep}",
                    "scheme": f"ladder_D:rank_ceiling(k={k})",
                    "family": name,
                    "depth_k": k,
                    "rep": rep,
                    "base": base,
                    "state": state,
                    "rank_ceiling": 2 + k,
                    "certificate": {"ok": True,
                                    "abelian_invariant": abelian_invariant(state),
                                    "stabilizations": k},
                })
    return rows


def _ak3_states():
    gens, rels = AK3
    base = make(gens, rels)
    rows = []
    tri, trace = triangulate(base)
    rows.append({
        "label": "ak3_left_prefix",
        "scheme": "AK(3) left-prefix triangulation (S1 section 4.4)",
        "base": base,
        "state": tri,
        "certificate": triangulation_certificate(base, tri, trace),
    })
    # a second, genuinely different triangulation: peel the cyclic rotations first
    rot = make(gens, (rels[0][2:] + rels[0][:2], rels[1][3:] + rels[1][:3]))
    tri2, trace2 = triangulate(rot)
    rows.append({
        "label": "ak3_rotated",
        "scheme": "AK(3) rotated-start left-prefix triangulation (S1 section 4.5 item 2)",
        "base": rot,
        "state": tri2,
        "certificate": triangulation_certificate(rot, tri2, trace2),
    })
    inv = make(gens, (inverse(rels[0]), rels[1]))
    tri3, trace3 = triangulate(inv)
    rows.append({
        "label": "ak3_inverted_r1",
        "scheme": "AK(3) inverted-r1 left-prefix triangulation (S1 section 4.5 item 4)",
        "base": inv,
        "state": tri3,
        "certificate": triangulation_certificate(inv, tri3, trace3),
    })
    return rows


def run_calibration(out_path: str, nodes: int = 1000, beam: int = 6, branch: int = 12,
                    evals: int = 900, seed: int = 20260804, per_length: int = 4,
                    per_depth: int = 3, depth_reps: int = 3,
                    time_budget: float = 240.0,
                    ladders=("A", "B", "D", "AK3"), max_relator_length: int = 12,
                    max_total_length: int = 40, rank_slack: int = 2,
                    verbose: bool = True) -> dict:
    """Run the identical search on the positive ladders and then on AK(3)."""
    t0 = time.time()
    rows = []
    jobs = []
    if "A" in ladders:
        jobs.extend(_ladder_a_states((12, 13), per_length, seed))
    if "B" in ladders:
        jobs.extend(_ladder_b_states(9, (6, 10, 14, 18), per_depth, seed + 1))
    if "D" in ladders:
        jobs.extend(_depth_ladder_states(reps=depth_reps))
    if "AK3" in ladders:
        jobs.extend(_ak3_states())

    for k, job in enumerate(jobs):
        state: Pres = job["state"]
        # rung seed: the depth ladder pairs AK(3) with its control at identical seeds
        run_seed = (seed + 1009 * job["depth_k"] + 7919 * job.get("rep", 0)
                    if "depth_k" in job else seed + 1009 * k)
        max_rank = (job["rank_ceiling"] if "rank_ceiling" in job
                    else state.rank + rank_slack)
        limits = Limits(max_relator_length=max_relator_length,
                        max_total_length=max(max_total_length, state.total_length + 6),
                        min_rank=2, max_rank=max_rank)
        result = search(state, nodes=nodes, beam=beam, branch=branch, evals=evals,
                        seed=run_seed, limits=limits,
                        time_budget=time_budget, label=job["label"],
                        scheme=job["scheme"], verbose=False)
        row = result.as_json()
        row["certificate"] = job["certificate"]
        row["base"] = job["base"].as_json()
        row["ladder"] = job["scheme"].split(":")[0]
        if "depth_k" in job:
            row["depth_k"] = job["depth_k"]
            row["family"] = job["family"]
            row["rank_ceiling"] = job["rank_ceiling"]
        rows.append(row)
        if verbose:
            print(f"[calib] {k + 1}/{len(jobs)} {job['label']} rank {state.rank} "
                  f"len {state.total_length} -> best defect {result.best_defect} "
                  f"hit={result.hit} nodes={result.nodes_used} "
                  f"{result.wall_seconds}s", flush=True)
        if time.time() - t0 > 540:
            if verbose:
                print("[calib] wall-clock guard: stopping the job list early", flush=True)
            break

    summary = summarise(rows)
    payload = {
        "record": "rank_n_ac_search",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "budget": {"nodes": nodes, "beam": beam, "branch": branch, "evals": evals,
                   "seed": seed, "max_relator_length": max_relator_length,
                   "max_total_length": max_total_length, "rank_slack": rank_slack},
        "summary": summary,
        "note": ("defect is the UNHALVED Neuwirth defect; gamma_N = defect/2.  The "
                 "hunter bounds gamma_N from ABOVE only: a null says nothing about "
                 "gamma_N > 0 and must be read against the measured detection rate "
                 "on the ladders."),
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1)
    jsonl = out_path[:-5] + "_rows.jsonl" if out_path.endswith(".json") else out_path + "l"
    with open(jsonl, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    if verbose:
        print(json.dumps(summary, indent=1), flush=True)
        print(f"[calib] wrote {out_path} and {jsonl}", flush=True)
    return payload


def summarise(rows) -> dict:
    """Detection-rate table by ladder, by rank and by scheme."""
    by_ladder: dict = {}
    for row in rows:
        ladder = row.get("ladder", "?")
        scheme = row.get("scheme", "?")
        bucket = by_ladder.setdefault(ladder, {})
        cell = bucket.setdefault(scheme, {"runs": 0, "hits": 0, "best_defects": [],
                                          "start_ranks": set(), "nodes": []})
        cell["runs"] += 1
        cell["hits"] += int(bool(row.get("hit")))
        cell["best_defects"].append(row.get("best_defect"))
        cell["start_ranks"].add(row.get("start_rank"))
        cell["nodes"].append(row.get("nodes_used"))
    out: dict = {}
    for ladder, cells in sorted(by_ladder.items()):
        out[ladder] = {}
        for scheme, cell in sorted(cells.items()):
            defects = [d for d in cell["best_defects"] if d is not None]
            out[ladder][scheme] = {
                "runs": cell["runs"],
                "hits": cell["hits"],
                "detection_rate": round(cell["hits"] / cell["runs"], 3)
                if cell["runs"] else None,
                "start_ranks": sorted(cell["start_ranks"]),
                "min_best_defect": min(defects) if defects else None,
                "median_best_defect": sorted(defects)[len(defects) // 2]
                if defects else None,
                "mean_nodes": round(sum(cell["nodes"]) / len(cell["nodes"]), 1)
                if cell["nodes"] else None,
            }
    depth: dict = {}
    for row in rows:
        if "depth_k" not in row:
            continue
        fam = depth.setdefault(row["family"], {})
        cell = fam.setdefault(str(row["depth_k"]), {
            "rank_ceiling": row["rank_ceiling"], "runs": 0, "hits": 0,
            "best_defects": [], "nodes": [], "seeds": [], "best_states": [],
        })
        cell["runs"] += 1
        cell["hits"] += int(bool(row.get("hit")))
        cell["best_defects"].append(row.get("best_defect"))
        cell["nodes"].append(row.get("nodes_used"))
        cell["seeds"].append(row.get("seed"))
        if row.get("hit"):
            cell["best_states"].append(row.get("best_state"))
    for fam, cells in depth.items():
        for _k, cell in cells.items():
            vals = [d for d in cell["best_defects"] if d is not None]
            cell["min_best_defect"] = min(vals) if vals else None
            cell["min_best_gamma_N_upper_bound"] = (min(vals) // 2) if vals else None
            cell["detection_rate"] = round(cell["hits"] / cell["runs"], 3) if cell["runs"] else None
    if depth:
        out["_depth_ladder"] = depth
        flat = {}
        for fam, cells in depth.items():
            vals = [c["min_best_defect"] for c in cells.values()
                    if c["min_best_defect"] is not None]
            flat[fam] = {
                "distinct_min_best_defects_over_rungs": sorted(set(vals)),
                "flat": len(set(vals)) <= 1,
                "hits": sum(c["hits"] for c in cells.values()),
                "runs": sum(c["runs"] for c in cells.values()),
            }
        out["_depth_ladder_shape"] = flat
    total_runs = len(rows)
    total_hits = sum(1 for r in rows if r.get("hit"))
    out["_overall"] = {"runs": total_runs, "hits": total_hits,
                       "detection_rate": round(total_hits / total_runs, 3)
                       if total_runs else None}
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=os.path.join(DEFAULT_OUT_DIR,
                                                      "rank_n_ac_search.json"))
    parser.add_argument("--nodes", type=int, default=1000)
    parser.add_argument("--beam", type=int, default=6)
    parser.add_argument("--branch", type=int, default=12)
    parser.add_argument("--evals", type=int, default=900)
    parser.add_argument("--seed", type=int, default=20260804)
    parser.add_argument("--per-length", type=int, default=4)
    parser.add_argument("--per-depth", type=int, default=3)
    parser.add_argument("--depth-reps", type=int, default=3)
    parser.add_argument("--max-relator-length", type=int, default=12)
    parser.add_argument("--max-total-length", type=int, default=40)
    parser.add_argument("--rank-slack", type=int, default=2)
    parser.add_argument("--time-budget", type=float, default=240.0,
                        help="wall-clock seconds per individual search")
    parser.add_argument("--ladders", default="A,B,D,AK3")
    args = parser.parse_args(argv)
    run_calibration(args.out, nodes=args.nodes, beam=args.beam, branch=args.branch,
                    evals=args.evals, seed=args.seed, per_length=args.per_length,
                    per_depth=args.per_depth, depth_reps=args.depth_reps,
                    time_budget=args.time_budget,
                    ladders=tuple(x.strip() for x in args.ladders.split(",") if x.strip()),
                    max_relator_length=args.max_relator_length,
                    max_total_length=args.max_total_length,
                    rank_slack=args.rank_slack)


if __name__ == "__main__":
    main()
