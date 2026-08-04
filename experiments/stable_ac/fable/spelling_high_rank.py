"""S11 -- spelling space AT HIGH RANK: calibration ladder + the refutation of Conjecture SR.

HEADLINE, so it is not buried: ``sr_hunt_spelled`` found a **verified counterexample to
R7's Conjecture SR in its general form**.  ``("YyXYYyxY","XyX")`` has minimum defect 0 over
its full 4,320-system census while ``("XYYyxY","XyX")`` -- the same word with the leading
``Yy`` spike deleted -- has minimum defect 2 over its full 144-system census, and the fully
reduced ``("XYxY","XyX")`` is back at 0.  So along one reduction chain the defect goes
**0 -> 2 -> 0** and ``gamma_N(spike(P)) = 0 => gamma_N(P) = 0`` is FALSE.  Every prior SR
test spiked a *cyclically reduced* base once, i.e. tested only ``depth 1 -> depth 0``; this
breaks at ``depth 2 -> depth 1``.

**SCOPE, which decides what it is worth.**  Todd-Coxeter completes on that first family
with **index 4**: it presents Z/4, NOT the trivial group, and a counterexample outside the
trivial-group class does not transfer into it (CLAUDE.md, "distinguish the statements").
So the hunt was rerun with bases restricted by ``trivial_bases`` to Todd-Coxeter-verified
index-1 presentations, and it **also succeeded**:

    ("ABbbabAAaB","baB")   census 86,400   min defect 0   <- spike, u = "B"
    ("AbabAAaB","baB")     census  2,880   min defect 2
    ("AbabAB","baB")       census    144   min defect 0   (fully reduced)

balanced, rank 2, Todd-Coxeter **index 1 at every step**, the defect-0 witness accepted by
``check_witness_n`` with ``trivial_group=True`` and re-derived by
``rank_n_ac_search.independent_defect``.  So:

* **SR-general: REFUTED**;
* **SR-trivial: REFUTED** -- 12 counterexamples over 4 trivial-group bases,
  ``results/stable_ac/fable/s11_sr_trivial.json``.

CAVEAT that must travel with both: in all 28 counterexamples the FULLY REDUCED form already
had defect 0.  No spelling was found that beats its own reduced form, which is the thing
AK(3) would need.  What falls is the *proof* that it cannot happen, not the question.

Pinned in ``tests/fable/test_spelling_high_rank.py``
``::test_conjecture_SR_is_false_for_GENERAL_presentations`` and
``::test_conjecture_SR_is_false_for_TRIVIAL_GROUP_presentations``; written up in
``results/stable_ac/theory/fable/S11_SPELLING_AT_HIGH_RANK.md`` sections 4.3 and 4.3'.


Task A10 of the fable S-line.  Two things live here, in this order, because the second is
worthless without the first:

1.  **A calibration ladder for the exact-census instrument, indexed by (total length,
    rank).**  ``experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md``
    is mandatory reading: the project's earlier spelling hunt used a randomised defect-0
    climber whose measured detection fell from 100 % at total length 16 to 0 % at 21,
    which retired 1,312 of 1,909 swept states as uninformative.  The claim tested here is
    that the *exact census* -- a different instrument, which never guesses -- collapses in
    the same band at rank 2 but does **not** collapse at rank 6-8, because the census cost
    ``prod_g (deg(g+) - 1)!`` is driven by germ DEGREE, and at fixed total length degree
    falls as rank rises.

2.  **Spelling space, with the conjecture that used to close it now known false in
    general.**  A8 measured (``S6_MOVE_CLASSIFICATION.md`` section 1) that free/cyclic
    reduction created ``gamma_N = 0`` in 315 of 2,510 non-thickenable spellings and
    destroyed it in 0 of 997 thickenable ones -- but every base in those corpora was
    cyclically reduced, so they only ever measured the induction step at depth 1.  The
    headline above breaks it at depth 2.  ``sr_hunt`` (walk bases), ``sr_hunt_spelled``
    (unreduced bases, the one that found it) and ``ak3_depth2`` (AK(3)'s own frontier) are
    the three hunts; ``trivial_bases`` restricts any of them to the trivial-group class,
    which is the only class the AC programme can use.

Bound direction, recorded per the standing lesson
(``experiments/lessons/parallel-runs-and-bound-direction.md``):

* the exact census returns an **equality** for gamma_N when it completes inside the cap,
  and ``UNKNOWN_SIZE`` otherwise.  A skip is never a verdict (fail-closed);
* the randomised climber ``rank_n_ac_search.hunt_defect`` bounds gamma_N from **ABOVE**;
  it is used here only to CERTIFY ladder rungs (a defect-0 witness is a complete positive
  certificate) and never to conclude anything from silence;
* the ladder bounds the instrument's sensitivity from **ABOVE**: rungs are states some
  construction could certify, so real states of the same (length, rank) can only be
  harder.  A low cell is conclusive; a high cell is optimistic.

Nothing here is edited into another agent's files.  ``high_rank_refine`` and
``rank_n_ac_search`` are imported, never modified.
"""

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable.ac_words import (              # noqa: E402
    cyclic_reduce,
    free_reduce,
    inverse,
    inverse_letter,
    is_cyclically_reduced,
)
from experiments.stable_ac.fable.neuwirth_rank_n import (       # noqa: E402
    build_link_n,
    census_size,
    gamma_N_factorial_n,
    generators_of,
)
from experiments.stable_ac.fable import high_rank_refine as HR  # noqa: E402
from experiments.stable_ac.fable import rank_n_ac_search as RN  # noqa: E402
from experiments.stable_ac.fable.coset_enum import is_trivial_group  # noqa: E402

__all__ = [
    "DEFAULT_CAP",
    "AK3",
    "spelling_key",
    "spike",
    "spike_images",
    "peel_and_reduce",
    "stabilize_and_graft",
    "census_cost",
    "decide",
    "certify_zero",
    "build_ladder",
    "detection_table",
    "hunt",
]

#: modest per-state census cap (the user asked for modest node budgets).  A state whose
#: compatible family exceeds it is recorded ``SKIPPED``, never given a verdict.
DEFAULT_CAP = 200_000

AK3 = ("xxxYYYY", "xyxYXY")


# ======================================================================================
# 1.  spelling moves
# ======================================================================================


def _min_rot(w: str) -> str:
    return min(w[i:] + w[:i] for i in range(len(w))) if w else w


def spelling_key(words) -> tuple:
    """Dedup key for an EXACT word-realized complex.

    The complex sees each relator as a cyclic word only, and gamma_N is invariant under
    relator inversion (``GAMMA_N_SYMMETRY_LEMMA.md``, AUDITED) and relator permutation.
    It is deliberately **not** quotiented by free reduction -- that is the whole point of
    working in spelling space (``R1F_REDUCTION_AND_SPIKES.md``).
    """
    return tuple(sorted(min(_min_rot(w), _min_rot(inverse(w))) for w in words))


def spike(words, j: int, k: int, letter: str) -> tuple:
    """``SPIKE(P; j, k, u)``: insert ``u u^{-1}`` before position ``k`` of relator ``j``.

    ``letter`` is a signed letter (``'x'`` or ``'X'``).  Positions are taken cyclically,
    so ``k`` ranges over ``range(len(w))``; ``k = len(w)`` would give the same cyclic word
    as ``k = 0``.  This is the inverse of one step of Lackenby's move (0) (see the
    soundness section of ``S11_SPELLING_AT_HIGH_RANK.md`` for why insertion is legal).
    """
    w = words[j]
    k %= max(1, len(w))
    new = w[:k] + letter + inverse_letter(letter) + w[k:]
    return tuple(words[:j]) + (new,) + tuple(words[j + 1:])


def spike_images(words, generators=None, *, letters=None, relators=None) -> list:
    """Every distinct single-spike image of ``words``, as ``(key, words, params)``."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    if letters is None:
        letters = [c for g in generators for c in (g, g.upper())]
    if relators is None:
        relators = range(len(words))
    seen: set = set()
    out = []
    for j in relators:
        for k in range(len(words[j])):
            for u in letters:
                img = spike(words, j, k, u)
                key = spelling_key(img)
                if key in seen:
                    continue
                seen.add(key)
                out.append((key, img, {"relator": j, "position": k, "letter": u}))
    return out


def peel_and_reduce(words, generators, j: int, rot: int, fresh: str = None) -> dict:
    """The `S3_AUDIT` section 3.2 mechanism: chord-refine a corner, THEN free-reduce.

    Peel the corner ``a1 a2`` off the ``rot``-th rotation of relator ``j``, introduce a
    fresh generator ``z`` with definition relator ``z (a1 a2)^{-1}``, shorten the relator
    to ``z a3 ... am``, and then apply the free/cyclic reduction that ``FRAMING.md`` trap 3
    mandates.  At a DEGENERATE corner (``a2 = a1^{-1}``) the definition relator reduces
    from length 3 to the single letter ``z`` and the complex genuinely changes -- that is
    the one measured mechanism in this project that moved a defect from 2 to 0.

    Returns a dict with the literal (unreduced) refinement and the reduced one, so the
    caller can see which of the two the value came from.
    """
    words = tuple(words)
    generators = tuple(generators)
    w = words[j]
    if len(w) < 2:
        raise ValueError(f"relator {w!r} is too short to peel")
    rot %= len(w)
    w = w[rot:] + w[:rot]
    if fresh is None:
        pool = HR.fresh_pool(generators)
        if not pool:
            raise ValueError("alphabet exhausted")
        fresh = pool[0]
    corner, rest = w[:2], w[2:]
    literal_def = fresh + inverse(corner)
    literal_res = fresh + rest
    literal = tuple(words[:j]) + (literal_res,) + tuple(words[j + 1:]) + (literal_def,)
    reduced = tuple(cyclic_reduce(free_reduce(x)) for x in literal)
    return {
        "fresh": fresh,
        "corner": corner,
        "degenerate": len(corner) == 2 and corner[1] == inverse_letter(corner[0]),
        "literal": literal,
        "reduced": tuple(x for x in reduced if x),
        "generators": tuple(sorted(set(generators) | {fresh})),
        "dropped_empty": any(x == "" for x in reduced),
    }


def stabilize_and_graft(words, generators, j: int, *, sign: int = 1,
                        fresh: str = None) -> dict:
    """``AC4`` then ``AC2``: adjoin ``(z | z)`` and replace ``r_j`` by ``r_j z^{sign}``.

    This is exactly what ``peel_and_reduce`` at a degenerate corner amounts to once the
    free reduction is done (``z (a1 a1^{-1})^{-1}`` reduces to ``z``, and the residual
    ``z a3...am`` is, as a CYCLIC word, ``a3...am z``).  Stating it this way removes every
    question about spelling legality: it is a bona-fide AC4 + AC2 composite on freely
    reduced words, valid because the presented group is trivial (FRAMING trap 2, the
    triviality hypothesis is sharp).
    """
    words = tuple(words)
    generators = tuple(generators)
    if fresh is None:
        pool = HR.fresh_pool(generators)
        if not pool:
            raise ValueError("alphabet exhausted")
        fresh = pool[0]
    z = fresh if sign > 0 else fresh.upper()
    grafted = free_reduce(words[j] + z)
    out = tuple(words[:j]) + (grafted,) + tuple(words[j + 1:]) + (fresh,)
    return {"fresh": fresh, "words": out,
            "generators": tuple(sorted(set(generators) | {fresh}))}


# ======================================================================================
# 2.  the instrument under test
# ======================================================================================


def census_cost(words, generators=None) -> int:
    """``prod_g (deg(g+) - 1)!`` -- the exact cost of deciding this complex."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    return census_size(build_link_n(words, generators), generators)


def decide(words, generators=None, cap: int = DEFAULT_CAP,
           keep_accepting: bool = False) -> dict:
    """THE PIPELINE.  Exact census, fail-closed above ``cap``.

    ``verdict`` is one of ``THICKENABLE`` (minimum defect 0 -- ORIENTABLY thickenable, see
    trap T-S9 and the Joint-A gap), ``NOT_THICKENABLE`` (decided, minimum defect > 0) or
    ``SKIPPED`` (census above the cap; **not** a mathematical verdict).
    """
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    res = gamma_N_factorial_n(words, generators, cap_rotations=cap,
                              keep_accepting=keep_accepting)
    if res["status"] != "OK":
        verdict = "SKIPPED"
    elif res["minimum_defect"] == 0:
        verdict = "THICKENABLE"
    else:
        verdict = "NOT_THICKENABLE"
    out = {
        "words": list(words),
        "generators": list(generators),
        "rank": len(generators),
        "total_length": sum(len(w) for w in words),
        "census": res["expected_cases"],
        "cap": cap,
        "status": res["status"],
        "verdict": verdict,
        "minimum_defect": res["minimum_defect"],
        "link_components": res["link_components"],
        "degrees": res["degrees"],
    }
    if keep_accepting and res.get("accepting_orders"):
        out["accepting_orders"] = res["accepting_orders"][:1]
    return out


def todd_coxeter_check(words, generators, cap: int = 200_000) -> dict:
    """Todd-Coxeter over the trivial subgroup: is the presented group still trivial?

    Required on any defect-0 hit before it is called a Lackenby certificate -- Thm 1.3's
    hypothesis is "thickenable AND presents the trivial group".  Returns ``trivial = None``
    when the enumeration hits the cap; that is undetermined, never guessed.  Spikes and
    chord refinements both preserve the group by construction, so this is a *check*, not a
    derivation -- which is exactly why it is worth running.
    """
    return is_trivial_group(tuple(words), tuple(generators), cap=cap)


def certify_zero(words, generators, *, evals: int = 60_000, seed: int = 0) -> dict:
    """Independent (non-census) certificate that ``gamma_N = 0``: a defect-0 witness.

    Uses the imported climber ``rank_n_ac_search.hunt_defect`` (bounds gamma_N from ABOVE)
    and re-verifies any hit with ``witness_check_n.check_witness_n`` through
    ``rank_n_ac_search.verify_defect_zero``, which shares no scheme code with the hunter.
    """
    pres = RN.Pres(tuple(generators), tuple(words))
    rng = random.Random(seed)
    best, orders, _cache = RN.hunt_defect(pres, evals, rng)
    row = {"climber_defect": best, "certified": False, "witness": None,
           "verify": None}
    if best == 0 and orders is not None:
        rep = RN.verify_defect_zero(pres, orders, census_cap=0)
        row["verify"] = {
            "check_witness_n": rep.get("check_witness_n"),
            "check_witness_n_error": rep.get("check_witness_n_error"),
            "independent_defect": rep.get("independent_defect"),
        }
        cw = rep.get("check_witness_n")
        ind = rep.get("independent_defect")
        ok_cw = bool(cw) and cw.get("defect") == 0
        ok_ind = bool(ind) and ind.get("defect") == 0
        row["certified"] = bool(ok_cw or ok_ind)
        row["witness"] = {str(k): list(v) for k, v in orders.items()}
    return row


# ======================================================================================
# 3.  the calibration ladder
# ======================================================================================


def _rank2_rungs(path: str) -> list:
    """Certified gamma_N = 0 rank-2 states from the earlier session's ladder."""
    with open(path) as fh:
        blob = json.load(fh)
    out = []
    for rung in blob.get("ladder", ()):
        words = tuple(rung["words"])
        out.append({
            "words": words,
            "generators": generators_of(words),
            "total_length": sum(len(w) for w in words),
            "rank": 2,
            "source": "witness_sensitivity ladder (census+witness)",
            "certified_by": rung.get("certified_by", "unknown"),
        })
    return out


def _walk_rungs(rank: int, targets, *, per_cell: int, seed: int, evals: int,
                tries: int, band: int = 1) -> list:
    """Rungs at ``rank`` and each total length in ``targets``, certified by witness.

    Every state comes from a random AC1-AC3 walk out of the standard presentation, so it
    is **AC-trivial and presents the trivial group by construction** -- no triviality test
    needed and no bias toward hard instances (the S10 sampling design).  A state is kept
    only if the independent defect-0 witness certifies it, so the census plays no part in
    the ladder's construction.
    """
    rng = random.Random(seed)
    limits = RN.Limits(max_relator_length=14, max_total_length=max(targets) + 6,
                       min_rank=rank, max_rank=rank)
    want = {int(t): [] for t in targets}
    base = RN.standard_presentation(rank)
    for _ in range(tries):
        if all(len(v) >= per_cell for v in want.values()):
            break
        moves = rng.randrange(4, 34)
        cur, _hist = RN.scramble(base, moves, rng, limits)
        if len(cur.gens) != rank or not cur.all_generators_occur():
            continue
        L = cur.total_length
        hit = [t for t in want if abs(t - L) <= band and len(want[t]) < per_cell]
        if not hit:
            continue
        t = hit[0]
        key = RN.canonical_key(cur)
        if any(r["key"] == key for r in want[t]):
            continue
        cert = certify_zero(cur.rels, cur.gens, evals=evals, seed=rng.randrange(10 ** 9))
        if not cert["certified"]:
            continue
        want[t].append({
            "words": tuple(cur.rels),
            "generators": tuple(cur.gens),
            "total_length": L,
            "rank": rank,
            "key": key,
            "source": f"AC1-AC3 walk from standard rank {rank}",
            "certified_by": "defect-0 witness (check_witness_n)",
        })
    out = []
    for t in sorted(want):
        out.extend(want[t])
    for r in out:
        r.pop("key", None)
    return out


def _grow_rungs(seeds, lengths, *, per_cell: int, evals: int, seed: int,
                width: int = 1, deadline: float = 60.0, max_children: int = 40) -> list:
    """Grow certified rungs by SPIKES, certifying every child with the climber.

    This is the method the earlier session's ladder used, and it is the only one that
    reaches the long rank-2 cells at all: a random walk almost never lands on a
    climber-certifiable rank-2 state above total length ~18, whereas a spike of an
    already-certified state usually keeps ``gamma_N = 0`` (R1F: 821 of 821 bases with
    ``gamma_N = 0`` had a spike with ``gamma_N = 0``).  The bias this introduces is
    recorded: rungs are by construction states the climber COULD certify, so the cells
    are OPTIMISTIC upper bounds on sensitivity.
    """
    t0 = time.time()
    rng = random.Random(seed)
    want = {int(t): [] for t in lengths}
    frontier = [dict(r) for r in seeds]
    seen = {spelling_key(r["words"]) for r in frontier}
    for r in frontier:
        for t in want:
            if abs(r["total_length"] - t) <= width and len(want[t]) < per_cell:
                want[t].append(r)
                break
    while frontier and time.time() - t0 < deadline:
        if all(len(v) >= per_cell for v in want.values()):
            break
        nxt = []
        for parent in frontier:
            if time.time() - t0 > deadline:
                break
            imgs = spike_images(parent["words"], parent["generators"])
            rng.shuffle(imgs)
            for key, img, params in imgs[:max_children]:
                if time.time() - t0 > deadline:
                    break
                if key in seen:
                    continue
                L = sum(len(w) for w in img)
                if L > max(lengths) + width:
                    continue
                seen.add(key)
                cert = certify_zero(img, parent["generators"], evals=evals,
                                    seed=rng.randrange(10 ** 9))
                if not cert["certified"]:
                    continue
                child = {"words": img, "generators": parent["generators"],
                         "total_length": L, "rank": len(parent["generators"]),
                         "source": f"spike growth from {parent['source']}",
                         "certified_by": "defect-0 witness (check_witness_n)"}
                nxt.append(child)
                for t in want:
                    if abs(L - t) <= width and len(want[t]) < per_cell:
                        want[t].append(child)
                        break
        frontier = nxt
    out = []
    for t in sorted(want):
        out.extend(want[t])
    return out


def build_ladder(*, ranks=(2, 4, 6, 8), lengths=(13, 16, 19, 22, 25), per_cell: int = 8,
                 seed: int = 20260804, evals: int = 40_000, tries: int = 4000,
                 rank2_path: str = None, rank2_evals: int = 200_000,
                 deadline: float = None, grow_deadline: float = None) -> list:
    """Rungs = presentations KNOWN thickenable, certified without touching the census.

    Rank 2 gets a larger climber budget because R7b measured its detection collapsing
    above total length ~20; the existing ``witness_sensitivity`` ladder is folded in for
    the same reason (its top rungs cost 2,000,000 evaluations each).
    """
    t0 = time.time()
    rungs = []
    seeds2 = []
    if rank2_path and os.path.exists(rank2_path):
        seeds2 = _rank2_rungs(rank2_path)
    for k, rank in enumerate(ranks):
        if deadline is not None and time.time() - t0 > deadline:
            break
        budget = rank2_evals if rank == 2 else evals
        if rank == 2 and seeds2:
            # A random rank-2 walk almost never lands on a climber-certifiable state
            # above total length ~18 (R7b), so the rank-2 column is grown from the
            # already-certified rungs instead of searched for from scratch.
            walked = []
        else:
            walked = _walk_rungs(rank, lengths, per_cell=per_cell, seed=seed + 7 * k,
                                 evals=budget, tries=tries)
        grow_seeds = (seeds2 + walked) if rank == 2 else walked
        if grow_seeds:
            rungs.extend(_grow_rungs(grow_seeds, lengths, per_cell=per_cell,
                                     evals=budget, seed=seed + 101 * k,
                                     deadline=(grow_deadline or 45.0)))
        else:
            rungs.extend(walked)
    return rungs


def decidability_scan(*, ranks=(2, 3, 4, 6, 8), lengths=(13, 16, 19, 22, 25),
                      per_cell: int = 50, seed: int = 20260804, tries: int = 20_000,
                      cap: int = DEFAULT_CAP, width: int = 1) -> dict:
    """The bias-free companion to the ladder.

    The pipeline is an EXACT census, so on a state that really is thickenable it returns
    defect 0 **iff** its compatible family fits inside the cap.  Detection rate is
    therefore a function of the DEGREE PROFILE alone, and can be estimated on an
    unconditional sample -- no ``gamma_N = 0`` filter, hence no selection by the climber
    whose own sensitivity varies with rank.  States are AC1-AC3 walks out of the standard
    presentation, so every one is AC-trivial and presents the trivial group.
    """
    rng = random.Random(seed)
    cells: dict = {}
    for rank in ranks:
        limits = RN.Limits(max_relator_length=16, max_total_length=max(lengths) + 6,
                           min_rank=rank, max_rank=rank)
        base = RN.standard_presentation(rank)
        want = {int(t): [] for t in lengths}
        for _ in range(tries):
            if all(len(v) >= per_cell for v in want.values()):
                break
            cur, _h = RN.scramble(base, rng.randrange(4, 40), rng, limits)
            if len(cur.gens) != rank or not cur.all_generators_occur():
                continue
            L = cur.total_length
            hit = [t for t in want if abs(t - L) <= width and len(want[t]) < per_cell]
            if not hit:
                continue
            want[hit[0]].append(census_cost(cur.rels, cur.gens))
        for t, costs in want.items():
            if not costs:
                continue
            costs.sort()
            cells[f"{t}|{rank}"] = {
                "band": t, "rank": rank, "n": len(costs),
                "decidable": sum(1 for c in costs if c <= cap),
                "decidable_rate": sum(1 for c in costs if c <= cap) / len(costs),
                "median_census": costs[len(costs) // 2],
                "max_census": costs[-1],
            }
    return cells


# --------------------------------------------------------------------------------------
# the one open spelling question: can free/cyclic REDUCTION destroy thickenability?
# --------------------------------------------------------------------------------------


#: R1F's eight single spikes of AK(3) with gamma_N exactly 1 (exhaustive census, 3.6M/4.8M
#: systems each; `R1F_REDUCTION_AND_SPIKES.md`).  These are the only depth-1 spellings that
#: Corollary S5's ceiling leaves as possible ancestors of a thickenable depth-2 spelling.
AK3_GATEWAYS = (
    ("xyYxxYYYY", "xyxYXY"),
    ("xxYyxYYYY", "xyxYXY"),
    ("xxxYXxYYY", "xyxYXY"),
    ("xxxYxXYYY", "xyxYXY"),
    ("xxxYYYXxY", "xyxYXY"),
    ("xxxYYYxXY", "xyxYXY"),
    ("xxxYYYY", "xxXyxYXY"),
    ("xxxYYYY", "xyXxxYXY"),
)


def climb(words, generators, *, evals: int, seed: int = 0):
    """Upper bound on ``gamma_N`` by the imported hill-climber.  0 is a complete positive."""
    pres = RN.Pres(tuple(generators), tuple(words))
    best, orders, _c = RN.hunt_defect(pres, evals, random.Random(seed))
    return best, orders


def calibrate_climber(states, *, evals: int, seeds: int = 5, seed: int = 0) -> dict:
    """Detection rate of the climber on states KNOWN to have ``gamma_N = 0``.

    The states must be certified positives; the fraction of (state, seed) cells in which
    the climber returns defect 0 is the number any null from the same budget is worth.
    """
    hits = 0
    cells = 0
    rows = []
    for w in states:
        gens = generators_of(w)
        got = 0
        for s in range(seeds):
            best, _o = climb(w, gens, evals=evals, seed=seed + 997 * s)
            cells += 1
            if best == 0:
                hits += 1
                got += 1
        rows.append({"words": list(w), "total_length": sum(len(x) for x in w),
                     "detected": got, "seeds": seeds})
    return {"evals": evals, "cells": cells, "detected": hits,
            "detection_rate": hits / cells if cells else None, "rows": rows}


def ak3_depth2(*, evals: int = 300_000, seed: int = 20260804, cap: int = 6_000_000,
               deadline: float = 600.0, same_letter_first: bool = True,
               gateways=AK3_GATEWAYS) -> dict:
    """The AK(3) depth-2 spelling hunt, re-opened after Conjecture SR fell.

    Corollary S6 (a *proof*, from the spike ceiling S5) says a thickenable spelling of
    AK(3) has spike-depth >= 2, and depth 1 is exhaustively decided.  So depth 2 is the
    frontier.  Bases are R1F's eight gateway spellings (the only depth-1 spellings with
    ``gamma_N = 1``); every distinct single spike of each is scored.

    Ordering: the 16 SR counterexamples found by ``sr_hunt_spelled`` all used the **same
    signed letter** as the spike already present, so those candidates are scored first.
    The instrument is the climber (an UPPER bound -- a 0 is conclusive, a positive is not),
    with the exact census used to confirm any hit; ``calibrate_climber`` supplies the
    detection rate that the null is worth.
    """
    t0 = time.time()
    rows = []
    hits = []
    seen: set = set()
    for gi, gw in enumerate(gateways):
        gens = generators_of(gw)
        base_letter = None
        for j, w in enumerate(gw):
            for i in range(len(w) - 1):
                if w[i + 1] == inverse_letter(w[i]):
                    base_letter = w[i]
                    break
            if base_letter:
                break
        imgs = spike_images(gw, gens)
        if same_letter_first and base_letter:
            imgs.sort(key=lambda t: 0 if t[2]["letter"] == base_letter else 1)
        for key, img, params in imgs:
            if time.time() - t0 > deadline:
                break
            if key in seen:
                continue
            seen.add(key)
            best, orders = climb(img, gens, evals=evals, seed=seed + 31 * gi)
            row = {"gateway": gi, "words": list(img), "spike": params,
                   "same_letter": params["letter"] == base_letter,
                   "climber_defect": best,
                   "total_length": sum(len(w) for w in img)}
            if best == 0 and orders is not None:
                exact = decide(img, gens, cap=cap, keep_accepting=True)
                row["exact"] = {k: exact[k] for k in
                                ("census", "status", "minimum_defect", "verdict")}
                row["todd_coxeter"] = todd_coxeter_check(img, gens, cap=200_000)
                row["verify"] = RN.verify_defect_zero(RN.Pres(gens, img), orders,
                                                      census_cap=0).get("check_witness_n")
                hits.append(row)
            rows.append(row)
        if time.time() - t0 > deadline:
            break
    by_defect: dict = {}
    for r in rows:
        by_defect[r["climber_defect"]] = by_defect.get(r["climber_defect"], 0) + 1
    return {
        "record": "AK(3) depth-2 spelling hunt (re-opened after Conjecture SR fell)",
        "bound_direction": "the climber bounds gamma_N from ABOVE; a 0 is conclusive, "
                           "silence is worth exactly the measured detection rate",
        "gateways": [list(g) for g in gateways],
        "evals_per_state": evals,
        "states_scored": len(rows),
        "same_letter_states": sum(1 for r in rows if r["same_letter"]),
        "climber_defect_histogram": {str(k): v for k, v in sorted(by_defect.items())},
        "n_hits": len(hits),
        "hits": hits,
        "seconds": round(time.time() - t0, 2),
        "rows": rows,
    }


def trivial_bases(rank: int = 2, *, count: int = 60, max_length: int = 10,
                  seed: int = 20260804, tries: int = 6000, coset_cap: int = 200_000):
    """Cyclically reduced balanced presentations of the **trivial group**, with the index.

    AC1-AC3 walks out of the standard presentation are trivial *by construction*; every one
    is nevertheless re-checked by Todd-Coxeter and the index is recorded, because the
    trivial-group restriction is the only version of Conjecture SR the AC programme can use
    (a general-presentation counterexample does not transfer -- CLAUDE.md, "distinguish the
    statements").
    """
    rng = random.Random(seed)
    limits = RN.Limits(max_relator_length=max_length, max_total_length=max_length,
                       min_rank=rank, max_rank=rank)
    base = RN.standard_presentation(rank)
    out = []
    seen: set = set()
    for _ in range(tries):
        if len(out) >= count:
            break
        cur, _h = RN.scramble(base, rng.randrange(3, 24), rng, limits)
        if len(cur.gens) != rank or not cur.all_generators_occur():
            continue
        if any(len(w) < 2 for w in cur.rels):
            continue
        key = spelling_key(cur.rels)
        if key in seen:
            continue
        seen.add(key)
        tc = todd_coxeter_check(cur.rels, cur.gens, cap=coset_cap)
        if tc.get("trivial") is not True:
            continue                       # never guessed: a capped enumeration is dropped
        out.append({"words": tuple(cur.rels), "generators": tuple(cur.gens),
                    "coset_index": tc.get("index"), "trivial": True})
    return out


def _jsonl_append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _jsonl_keys(path, field="key"):
    done = {}
    if not os.path.exists(path):
        return done
    with open(path) as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except Exception:                                        # noqa: BLE001
                continue
            if field in row:
                done[row[field]] = row
    return done


def deep_climb_pass(states, *, evals: int, seeds: int, checkpoint: str, tag: str,
                    deadline: float, seed: int = 20260804, log=None) -> dict:
    """Climb every state at ``evals`` x ``seeds``, appending each result to ``checkpoint``.

    Crash-safe and resumable: a state already present in the checkpoint with the same
    ``tag`` is skipped.  The climber bounds ``gamma_N`` from ABOVE, so a 0 is a complete
    positive certificate and a positive return is worth exactly the calibrated detection
    rate at this ``evals`` -- never a lower bound.
    """
    t0 = time.time()
    done = {k: r for k, r in _jsonl_keys(checkpoint).items()
            if r.get("tag") == tag}
    hits = []
    scored = 0
    for st in states:
        words = tuple(st["words"]) if isinstance(st, dict) else tuple(st)
        gens = generators_of(words)
        key = f"{tag}|" + "|".join(words)
        if key in done:
            if done[key].get("best") == 0:
                hits.append(done[key])
            continue
        if time.time() - t0 > deadline:
            break
        best = None
        witness = None
        for s in range(seeds):
            b, orders = climb(words, gens, evals=evals, seed=seed + 7919 * s)
            if best is None or b < best:
                best, witness = b, orders
            if best == 0:
                break
        row = {"key": key, "tag": tag, "words": list(words), "evals": evals,
               "seeds_used": seeds, "best": best,
               "census": census_cost(words, gens),
               "total_length": sum(len(w) for w in words),
               "seconds": round(time.time() - t0, 1)}
        if best == 0 and witness is not None:
            row["witness"] = {str(k): list(v) for k, v in witness.items()}
        _jsonl_append(checkpoint, row)
        scored += 1
        if best == 0:
            hits.append(row)
            if log:
                log(f"  *** DEFECT-0 HIT {words} tag={tag}")
        done[key] = row
    hist: dict = {}
    for r in done.values():
        hist[str(r["best"])] = hist.get(str(r["best"]), 0) + 1
    return {"tag": tag, "evals": evals, "seeds": seeds, "scored_now": scored,
            "in_checkpoint": len(done), "histogram": hist, "hits": hits,
            "survivors": [r["words"] for r in done.values() if r["best"] == 2],
            "seconds": round(time.time() - t0, 2)}


def verify_hit(words, generators=None, *, base=AK3, witness=None,
               census_cap: int = 10 ** 9, coset_cap: int = 500_000) -> dict:
    """Four-way verification of a claimed defect-0 spelling, per the standing rule.

    1. ``check_witness_n`` with ``trivial_group=True`` -- rebuilds ``D, A, B`` from the
       words and shares no code with the climber; it also cross-checks Corollary 3's
       transitivity, which only holds for the trivial group;
    2. the exact census (expensive at these degrees -- 2-4 x 10^8 systems, ~30 min each --
       so it is attempted only under ``census_cap`` and reported as SKIPPED otherwise);
    3. Todd-Coxeter over the trivial subgroup: the presented group must still be trivial;
    4. **replay**: free-reduce back to ``base`` and exhibit the explicit chain of spike
       insertions, so the claim "this is a spelling of AK(3)" is checked rather than
       asserted.
    """
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    out = {"words": list(words), "generators": list(generators)}

    # (4) replay first: cheapest, and it decides whether the rest is even relevant
    reduced = tuple(cyclic_reduce(free_reduce(w)) for w in words)
    out["free_reduction"] = list(reduced)
    out["replays_to_base"] = spelling_key(reduced) == spelling_key(
        tuple(cyclic_reduce(w) for w in base))
    out["base"] = list(base)
    out["spikes_removed"] = sum(len(w) for w in words) - sum(len(w) for w in reduced)

    # (3) Todd-Coxeter
    out["todd_coxeter"] = todd_coxeter_check(words, generators, cap=coset_cap)

    # (1) independent witness verification
    if witness is not None:
        pres = RN.Pres(generators, words)
        orders = {int(k): list(v) for k, v in witness.items()}
        rep = RN.verify_defect_zero(pres, orders, census_cap=0)
        out["check_witness_n"] = rep.get("check_witness_n")
        out["check_witness_n_error"] = rep.get("check_witness_n_error")
        out["independent_defect"] = rep.get("independent_defect")

    # (2) exact census, only if it is remotely affordable
    cost = census_cost(words, generators)
    out["census_size"] = cost
    if cost <= census_cap:
        out["exact_census"] = decide(words, generators, cap=census_cap)
    else:
        out["exact_census"] = {"verdict": "SKIPPED", "census": cost,
                               "note": "above census_cap; not a mathematical verdict"}
    return out


def matched_positive_ladder(*, target_length: int = 17, min_census: int = 10 ** 8,
                            want: int = 5, certify_evals: int = 3_000_000,
                            seed: int = 20260804, deadline: float = 600.0,
                            seeds_from=None, log=None) -> list:
    """Certified ``gamma_N = 0`` rank-2 states MATCHED on length AND census size.

    Calibrating the AK(3) depth-2 hunt on generic length-17 rungs would be too kind: the
    targets have compatible families of 2-4 x 10^8, while a generic length-17 ladder rung
    has 10^4-10^6.  A climber's difficulty tracks the search space, not the word length, so
    the calibration states are grown until their census is at least ``min_census``.
    """
    t0 = time.time()
    rng = random.Random(seed)
    if seeds_from is None:
        seeds_from = [("xyXY", "xxy"), ("xyXY", "Yyxxy"), ("xxy", "xyXY")]
    frontier = [tuple(w) for w in seeds_from]
    found = []
    seen = {spelling_key(w) for w in frontier}
    while frontier and time.time() - t0 < deadline and len(found) < want:
        nxt = []
        for parent in frontier:
            gens = generators_of(parent)
            imgs = spike_images(parent, gens)
            rng.shuffle(imgs)
            for key, img, _p in imgs[:24]:
                if time.time() - t0 > deadline or len(found) >= want:
                    break
                if key in seen:
                    continue
                L = sum(len(w) for w in img)
                if L > target_length:
                    continue
                seen.add(key)
                cost = census_cost(img, gens)
                # cheap gate first: only climb states that are still on a useful trajectory
                if L == target_length and cost < min_census:
                    continue
                cert = certify_zero(img, gens,
                                    evals=certify_evals if L == target_length else 200_000,
                                    seed=rng.randrange(10 ** 9))
                if not cert["certified"]:
                    continue
                row = {"words": img, "generators": gens, "total_length": L,
                       "census": cost, "certified_by": "defect-0 witness",
                       "certify_evals": certify_evals if L == target_length else 200_000}
                if L == target_length and cost >= min_census:
                    found.append(row)
                    if log:
                        log(f"  matched rung {img} census={cost:,}")
                else:
                    nxt.append(img)
        frontier = nxt[:40]
    return found


def calibrate_at(states, budgets, *, seeds: int = 5, seed: int = 0,
                 checkpoint: str = None, deadline: float = 900.0) -> dict:
    """Detection rate of the climber at each budget in ``budgets``, on certified positives."""
    t0 = time.time()
    out = {}
    for evals in budgets:
        hits = 0
        cells = 0
        rows = []
        for st in states:
            words = tuple(st["words"]) if isinstance(st, dict) else tuple(st)
            gens = generators_of(words)
            got = 0
            for s in range(seeds):
                if time.time() - t0 > deadline:
                    break
                b, _o = climb(words, gens, evals=evals, seed=seed + 104729 * s)
                cells += 1
                if b == 0:
                    hits += 1
                    got += 1
            rows.append({"words": list(words), "census": census_cost(words, gens),
                         "total_length": sum(len(w) for w in words),
                         "detected": got, "seeds": seeds})
            if checkpoint:
                _jsonl_append(checkpoint, {"key": f"cal{evals}|" + "|".join(words),
                                           "tag": f"cal{evals}", "detected": got,
                                           "seeds": seeds, "words": list(words)})
        out[str(evals)] = {"evals": evals, "cells": cells, "detected": hits,
                           "detection_rate": hits / cells if cells else None,
                           "rows": rows}
    return out


def sr_hunt_spelled(*, bases=None, max_base_length: int = 8, cap: int = DEFAULT_CAP,
                    deadline: float = 180.0, seed: int = 20260804,
                    max_bases: int = 400) -> dict:
    """Counterexample hunt for Conjecture SR **at spike depth 1 -> 2**.

    This is the gap in every previous SR test.  R1F/R7's 110,917 complexes and A8's 997 all
    take a **cyclically reduced** base and apply ONE spike, so they test the induction step
    ``depth 1 -> depth 0`` only.  The Corollary that SR is wanted for
    (``gamma*(P) = 0 <=> gamma_N(P_red) = 0``, hence ``gamma*(AK(3)) = 1`` and the closure of
    the spelling route) iterates SR at EVERY depth.  So the step to attack is
    ``depth 2 -> depth 1``: a spelling two spikes out that is thickenable, sitting over a
    spelling one spike out that is not.

    For each hit the report also records whether the **existential** repair survives, i.e.
    whether SOME one-step reduction of the hit is still thickenable.  That distinction is
    the whole difference between "SR is false" and "the Corollary is false".
    """
    t0 = time.time()
    rng = random.Random(seed)
    if bases is None:
        bases = []
        gens = ("x", "y")
        letters = "xXyY"
        for total in range(4, max_base_length + 1):
            for l1 in range(2, total - 1):
                l2 = total - l1
                if l2 < 2:
                    continue
                for w1 in itertools.product(letters, repeat=l1):
                    s1 = "".join(w1)
                    if not is_cyclically_reduced(s1) or len({c.lower() for c in s1}) < 2:
                        continue
                    for w2 in itertools.product(letters, repeat=l2):
                        s2 = "".join(w2)
                        if (not is_cyclically_reduced(s2)
                                or len({c.lower() for c in s2}) < 2):
                            continue
                        bases.append((s1, s2))
            if len(bases) > 40_000:
                break
        seen = set()
        uniq = []
        for b in bases:
            k = spelling_key(b)
            if k in seen:
                continue
            seen.add(k)
            uniq.append(b)
        bases = uniq
        rng.shuffle(bases)
    bases = list(bases)[:max_bases]

    hits = []
    n_bases = 0
    n_depth1 = 0
    n_depth2 = 0
    skipped = 0
    for base in bases:
        if time.time() - t0 > deadline:
            break
        gens = generators_of(base)
        n_bases += 1
        for _k1, p1, prm1 in spike_images(base, gens):
            if time.time() - t0 > deadline:
                break
            r1 = decide(p1, gens, cap=cap)
            if r1["verdict"] != "NOT_THICKENABLE":
                continue                        # only a POSITIVE-defect depth-1 can break SR
            n_depth1 += 1
            for _k2, p2, prm2 in spike_images(p1, gens):
                if time.time() - t0 > deadline:
                    break
                r2 = decide(p2, gens, cap=cap)
                if r2["verdict"] == "SKIPPED":
                    skipped += 1
                    continue
                n_depth2 += 1
                if r2["minimum_defect"] != 0:
                    continue
                # a hit: gamma_N(p2) = 0 while gamma_N(p1) > 0 and p2 = spike(p1)
                sibs = []
                for j, w in enumerate(p2):
                    for i in range(len(w)):
                        if w[(i + 1) % len(w)] != inverse_letter(w[i]):
                            continue
                        red = w[:i] + w[i + 2:] if i + 2 <= len(w) else w[1:-1]
                        red = free_reduce(red)
                        if not red:
                            continue
                        sib = tuple(p2[:j]) + (red,) + tuple(p2[j + 1:])
                        rs = decide(sib, gens, cap=cap)
                        sibs.append({"words": list(sib), "verdict": rs["verdict"],
                                     "minimum_defect": rs["minimum_defect"]})
                hits.append({
                    "base_reduced": list(base),
                    "depth1": list(p1), "depth1_defect": r1["minimum_defect"],
                    "depth2": list(p2), "depth2_defect": 0,
                    "spike1": prm1, "spike2": prm2,
                    "generators": list(gens),
                    "total_length": sum(len(w) for w in p2),
                    "census_depth2": r2["census"],
                    "one_step_reductions": sibs,
                    "existential_SR_survives": any(
                        s["minimum_defect"] == 0 for s in sibs),
                    "group_of_reduced_base": todd_coxeter_check(base, gens, cap=20_000),
                })
    hits.sort(key=lambda h: (h["total_length"], h["depth2"]))
    return {
        "record": "Conjecture SR counterexample hunt at spike depth 1 -> 2",
        "conjecture": "SR: gamma_N(spike(P)) = 0 => gamma_N(P) = 0, for EVERY P and spike",
        "gap_attacked": ("all prior SR evidence takes a cyclically reduced base and one "
                         "spike, i.e. it tests depth 1 -> 0 only"),
        "bases_examined": n_bases,
        "depth1_spellings_with_positive_defect": n_depth1,
        "depth2_spellings_decided": n_depth2,
        "depth2_skipped_over_cap": skipped,
        "n_counterexamples": len(hits),
        "counterexamples": hits[:200],
        "cap": cap,
        "seconds": round(time.time() - t0, 2),
    }


def sr_hunt(*, ranks=(2, 3, 4), max_base_length: int = 12, spike_depth: int = 2,
            per_rank: int = 400, seed: int = 20260804, cap: int = DEFAULT_CAP,
            deadline: float = 120.0) -> dict:
    """Counterexample hunt for R7's **Conjecture SR**.

    SR says ``gamma_N(spike(P)) = 0  =>  gamma_N(P) = 0``.  A counterexample is a spelling
    ``K`` with ``gamma_N(K) = 0`` whose free/cyclic reduction has ``gamma_N > 0``.  Both
    sides are decided by EXACT census inside ``cap``; a pair where either side is skipped
    is counted and discarded, never converted into a verdict.

    Bases are AC1-AC3 walks out of the standard presentation (AC-trivial by construction);
    the interesting bases are the NON-thickenable ones, since a counterexample needs
    ``gamma_N(reduced) > 0``, and the spikes are then piled on those.
    """
    t0 = time.time()
    rng = random.Random(seed)
    tested = 0
    skipped = 0
    zero_spellings = 0
    counterexamples = []
    per_rank_stats = {}
    slice_s = deadline / max(1, len(ranks))
    for r_i, rank in enumerate(ranks):
        stop_at = min(deadline, slice_s * (r_i + 1))
        limits = RN.Limits(max_relator_length=12, max_total_length=max_base_length + 4,
                           min_rank=rank, max_rank=rank)
        base = RN.standard_presentation(rank)
        n_bases = 0
        n_bad = 0
        while n_bases < per_rank and time.time() - t0 < stop_at:
            cur, _h = RN.scramble(base, rng.randrange(3, 26), rng, limits)
            if len(cur.gens) != rank or not cur.all_generators_occur():
                continue
            if cur.total_length > max_base_length:
                continue
            red = decide(cur.rels, cur.gens, cap=cap)
            n_bases += 1
            if red["verdict"] != "NOT_THICKENABLE":
                continue                       # only non-thickenable reductions can break SR
            n_bad += 1
            frontier = [tuple(cur.rels)]
            for _d in range(spike_depth):
                nxt = []
                for words in frontier:
                    for _k, img, _p in spike_images(words, cur.gens):
                        if time.time() - t0 > stop_at:
                            break
                        row = decide(img, cur.gens, cap=cap)
                        if row["verdict"] == "SKIPPED":
                            skipped += 1
                            continue
                        tested += 1
                        nxt.append(img)
                        if row["verdict"] == "THICKENABLE":
                            zero_spellings += 1
                            counterexamples.append({
                                "spelling": list(img),
                                "reduced": list(cur.rels),
                                "generators": list(cur.gens),
                                "spelling_defect": row["minimum_defect"],
                                "reduced_defect": red["minimum_defect"],
                            })
                    if time.time() - t0 > stop_at:
                        break
                frontier = nxt[:60]
                if time.time() - t0 > stop_at:
                    break
        per_rank_stats[str(rank)] = {"bases": n_bases, "non_thickenable_bases": n_bad,
                                     "tested_so_far": tested, "skipped_so_far": skipped}
    return {
        "record": "SR counterexample hunt (does free/cyclic reduction ever DESTROY "
                  "gamma_N = 0?)",
        "conjecture": "SR: gamma_N(spike(P)) = 0  =>  gamma_N(P) = 0",
        "counterexample_shape": "a spelling with defect 0 whose reduction has defect > 0",
        "spellings_tested": tested,
        "skipped_over_cap": skipped,
        "counterexamples": counterexamples,
        "n_counterexamples": len(counterexamples),
        "per_rank": per_rank_stats,
        "cap": cap,
        "seconds": round(time.time() - t0, 2),
    }


def _band(L: int, edges=(13, 16, 19, 22, 25), width: int = 1):
    for e in edges:
        if abs(L - e) <= width:
            return e
    return None


def detection_table(rows, edges=(13, 16, 19, 22, 25), width: int = 1) -> dict:
    """``{(band, rank): {...}}`` -- the headline table."""
    cells: dict = {}
    for r in rows:
        b = _band(r["total_length"], edges, width)
        if b is None:
            continue
        cell = cells.setdefault((b, r["rank"]), {"n": 0, "detected": 0, "skipped": 0,
                                                 "missed": 0, "census": []})
        cell["n"] += 1
        cell["census"].append(r["census"])
        if r["verdict"] == "THICKENABLE":
            cell["detected"] += 1
        elif r["verdict"] == "SKIPPED":
            cell["skipped"] += 1
        else:
            cell["missed"] += 1
    out = {}
    for (b, rank), c in sorted(cells.items()):
        cen = sorted(c["census"])
        out[f"{b}|{rank}"] = {
            "band": b, "rank": rank, "n": c["n"],
            "detected": c["detected"], "skipped": c["skipped"], "missed": c["missed"],
            "detection_rate": c["detected"] / c["n"] if c["n"] else None,
            "median_census": cen[len(cen) // 2] if cen else None,
        }
    return out


# ======================================================================================
# 4.  the hunt
# ======================================================================================


def high_rank_forms(words, generators=None, *, limit: int = 4, seed: int = 0) -> list:
    """Certified chord refinements of ``words`` (rank up, relators down to length 3).

    Uses ``high_rank_refine.enumerate_triangulations`` unmodified, so every form carries
    the module's own replay certificate.  Theorem S3 / Lemma S3' say the whole defect
    histogram is preserved by these, which is exactly why they are used here as a
    COST-REDUCING change of cell structure and never as a mechanism.
    """
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    out = []
    for ref in HR.enumerate_triangulations(words, limit=limit, seed=seed,
                                           generators=tuple(generators), certify=True):
        out.append({
            "words": tuple(ref.words),
            "generators": tuple(ref.generators),
            "scheme": ref.scheme,
            "params": ref.params,
            "certified": ref.certificate is not None,
            "share": bool(ref.params.get("share")),
        })
    return out


def hunt(base_words, base_generators=None, *, depth: int = 2, cap: int = DEFAULT_CAP,
         max_states: int = 4000, refine_limit: int = 3, seed: int = 0,
         include_peel: bool = True, deadline: float = None, log=None) -> dict:
    """Spike-space hunt at high rank.  Exhaustive by depth, capped by ``max_states``."""
    t0 = time.time()
    base_words = tuple(base_words)
    if base_generators is None:
        base_generators = generators_of(base_words)
    base_generators = tuple(base_generators)

    forms = [{"words": base_words, "generators": base_generators, "scheme": "base",
              "params": {}, "certified": True, "share": False}]
    if refine_limit:
        try:
            forms.extend(high_rank_forms(base_words, base_generators,
                                         limit=refine_limit, seed=seed))
        except Exception as exc:                                    # noqa: BLE001
            forms[0]["refine_error"] = f"{type(exc).__name__}: {exc}"

    rows = []
    hits = []
    seen: set = set()
    skipped = 0
    scored = 0
    stopped = None

    def score(words, gens, prov):
        nonlocal skipped, scored, stopped
        if stopped:
            return None
        if deadline is not None and time.time() - t0 > deadline:
            stopped = "deadline"
            return None
        if len(rows) >= max_states:
            stopped = "max_states"
            return None
        key = (spelling_key(words), tuple(gens))
        if key in seen:
            return None
        seen.add(key)
        cost = census_cost(words, gens)
        if cost > cap:
            skipped += 1
            row = {"verdict": "SKIPPED", "census": cost, "words": list(words),
                   "generators": list(gens), "rank": len(gens),
                   "total_length": sum(len(w) for w in words), "provenance": prov,
                   "minimum_defect": None}
            rows.append(row)
            return row
        row = decide(words, gens, cap=cap)
        row["provenance"] = prov
        scored += 1
        rows.append(row)
        if row["verdict"] == "THICKENABLE":
            hits.append(row)
            if log:
                log(f"  !! HIT {row['words']} rank {row['rank']} prov={prov}")
        return row

    for form in forms:
        fw, fg = form["words"], form["generators"]
        prov0 = {"form": form["scheme"], "spikes": [], "peel": None}
        score(fw, fg, dict(prov0))
        # depth-1 .. depth-`depth` spike frontier over this form
        frontier = [(fw, [])]
        for d in range(depth):
            nxt = []
            for words, hist in frontier:
                for _key, img, params in spike_images(words, fg):
                    prov = {"form": form["scheme"], "spikes": hist + [params],
                            "peel": None}
                    r = score(img, fg, prov)
                    if stopped:
                        break
                    if r is not None:
                        nxt.append((img, hist + [params]))
                    if include_peel:
                        for j in range(len(img)):
                            for rot in range(len(img[j])):
                                if len(img[j]) < 2:
                                    continue
                                a1, a2 = img[j][rot], img[j][(rot + 1) % len(img[j])]
                                if a2 != inverse_letter(a1):
                                    continue
                                try:
                                    pr = peel_and_reduce(img, fg, j, rot)
                                except ValueError:
                                    continue
                                if pr["dropped_empty"]:
                                    continue
                                score(pr["reduced"], pr["generators"],
                                      {"form": form["scheme"],
                                       "spikes": hist + [params],
                                       "peel": {"relator": j, "rot": rot,
                                                "corner": pr["corner"],
                                                "fresh": pr["fresh"]}})
                                if stopped:
                                    break
                            if stopped:
                                break
                    if stopped:
                        break
                if stopped:
                    break
            if stopped:
                break
            frontier = nxt
        if stopped:
            break

    return {
        "base_words": list(base_words),
        "base_generators": list(base_generators),
        "depth": depth,
        "cap": cap,
        "forms": [{k: (list(v) if isinstance(v, tuple) else v)
                   for k, v in f.items()} for f in forms],
        "n_states": len(rows),
        "scored": scored,
        "skipped": skipped,
        "hits": hits,
        "stopped": stopped,
        "seconds": round(time.time() - t0, 2),
        "rows": rows,
    }


# ======================================================================================
# 5.  CLI
# ======================================================================================


def _emit(path, blob):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(blob, fh, indent=1, sort_keys=False)
    return path


def cmd_ladder(args):
    t0 = time.time()
    rungs = build_ladder(ranks=tuple(int(r) for r in args.ranks.split(",")),
                         lengths=tuple(int(x) for x in args.lengths.split(",")),
                         per_cell=args.per_cell, seed=args.seed, evals=args.evals,
                         tries=args.tries, rank2_path=args.rank2,
                         rank2_evals=args.rank2_evals, deadline=args.deadline,
                         grow_deadline=args.grow_deadline)
    rows = []
    for r in rungs:
        row = decide(r["words"], r["generators"], cap=args.cap)
        row["source"] = r["source"]
        row["certified_by"] = r["certified_by"]
        rows.append(row)
    table = detection_table(rows, edges=tuple(int(x) for x in args.lengths.split(",")),
                            width=args.width)
    blob = {
        "record": "S11 calibration ladder: exact-census detection by (length, rank)",
        "bound_direction": ("census returns EQUALITY inside the cap and SKIPPED above it; "
                            "the ladder bounds sensitivity from ABOVE"),
        "cap": args.cap,
        "n_rungs": len(rows),
        "table": table,
        "rows": rows,
        "seconds": round(time.time() - t0, 2),
    }
    print(json.dumps(table, indent=1))
    print("wrote", _emit(args.out, blob), blob["seconds"], "s")
    return blob


def cmd_scan(args):
    t0 = time.time()
    cells = decidability_scan(ranks=tuple(int(r) for r in args.ranks.split(",")),
                              lengths=tuple(int(x) for x in args.lengths.split(",")),
                              per_cell=args.per_cell, seed=args.seed, tries=args.tries,
                              cap=args.cap, width=args.width)
    blob = {"record": "S11 decidability of the exact census by (length, rank)",
            "note": ("on a state that IS thickenable the exact census returns defect 0 "
                     "iff its family fits inside the cap, so this is the bias-free "
                     "estimator of the detection rate"),
            "cap": args.cap, "cells": cells, "seconds": round(time.time() - t0, 2)}
    print(json.dumps(cells, indent=1))
    print("wrote", _emit(args.out, blob), blob["seconds"], "s")
    return blob


def cmd_ak3(args):
    t0 = time.time()
    cal = None
    if args.calibrate:
        ladder = json.load(open(args.ladder))["rows"] if os.path.exists(args.ladder) else []
        # every ladder rung is a CERTIFIED gamma_N = 0 state (defect-0 witness,
        # re-verified by check_witness_n); the census verdict must NOT be used as the
        # filter, since the cells being calibrated are exactly the ones the census SKIPS.
        pos = [tuple(r["words"]) for r in ladder
               if abs(r["total_length"] - args.calibrate_length) <= 1
               and r["rank"] == 2]
        pos = pos[:args.calibrate_states]
        if pos:
            cal = calibrate_climber(pos, evals=args.evals, seeds=args.calibrate_seeds,
                                    seed=args.seed)
            print("climber calibration at %d evals, length ~%d, rank 2: %d/%d = %.2f"
                  % (args.evals, args.calibrate_length, cal["detected"], cal["cells"],
                     cal["detection_rate"]))
        else:
            print("no rank-2 positive ladder rungs near length", args.calibrate_length)
    blob = ak3_depth2(evals=args.evals, seed=args.seed, cap=args.cap,
                      deadline=args.deadline)
    blob["climber_calibration"] = cal
    blob["total_seconds"] = round(time.time() - t0, 2)
    print(json.dumps({k: v for k, v in blob.items()
                      if k not in ("rows", "hits", "gateways")}, indent=1))
    if blob["hits"]:
        print("HITS:", json.dumps(blob["hits"][:3], indent=1))
    print("wrote", _emit(args.out, blob))
    return blob


def cmd_sr_spelled(args):
    bases = None
    index_of = {}
    if getattr(args, "trivial_only", False):
        rows = trivial_bases(2, count=args.max_bases, max_length=args.max_base_length,
                             seed=args.seed)
        bases = [r["words"] for r in rows]
        index_of = {r["words"]: r["coset_index"] for r in rows}
        print("trivial-group bases:", len(bases),
              "(all Todd-Coxeter index 1)" if all(v == 1 for v in index_of.values())
              else "(INDEX MISMATCH)")
    blob = sr_hunt_spelled(bases=bases, max_base_length=args.max_base_length, cap=args.cap,
                           deadline=args.deadline, seed=args.seed,
                           max_bases=args.max_bases)
    blob["bases_restricted_to_trivial_group"] = bool(getattr(args, "trivial_only", False))
    print(json.dumps({k: v for k, v in blob.items() if k != "counterexamples"}, indent=1))
    for h in blob["counterexamples"][:6]:
        print(" CE:", h["depth2"], "d=0  <-  spike of", h["depth1"],
              "d=%s" % h["depth1_defect"], "| L=%d" % h["total_length"],
              "| existential SR survives:", h["existential_SR_survives"])
    print("wrote", _emit(args.out, blob))
    return blob


def cmd_sr(args):
    blob = sr_hunt(ranks=tuple(int(r) for r in args.ranks.split(",")),
                   max_base_length=args.max_base_length,
                   spike_depth=args.spike_depth, per_rank=args.per_rank,
                   seed=args.seed, cap=args.cap, deadline=args.deadline)
    print(json.dumps({k: v for k, v in blob.items() if k != "counterexamples"}, indent=1))
    if blob["counterexamples"]:
        print("COUNTEREXAMPLES:", json.dumps(blob["counterexamples"][:5], indent=1))
    print("wrote", _emit(args.out, blob))
    return blob


def cmd_hunt(args):
    words = tuple(args.words.split(",")) if args.words else AK3
    gens = tuple(args.generators.split(",")) if args.generators else None
    res = hunt(words, gens, depth=args.depth, cap=args.cap, max_states=args.max_states,
               refine_limit=args.refine_limit, seed=args.seed,
               include_peel=not args.no_peel, deadline=args.deadline,
               log=print if args.verbose else None)
    summary = {k: v for k, v in res.items() if k != "rows"}
    print(json.dumps(summary, indent=1)[:4000])
    _emit(args.out, res)
    print("wrote", args.out)
    return res


def cmd_harvest(args):
    """Sample long members of AK(3)'s rank-3 stable harvest, refine, spike, decide."""
    t0 = time.time()
    rng = random.Random(args.seed)
    members = []
    opener = gzip.open if args.path.endswith(".gz") else open
    with opener(args.path, "rt") as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except Exception:                                        # noqa: BLE001
                continue
            w = row.get("words") or row.get("relators") or row.get("state")
            if not w:
                continue
            w = tuple(w)
            L = sum(len(x) for x in w)
            if not (args.min_length <= L <= args.max_length):
                continue
            if rng.random() < args.sample_rate:
                members.append(w)
            if len(members) >= args.limit:
                break
    out_rows = []
    hits = []
    for w in members:
        if time.time() - t0 > args.deadline:
            break
        gens = generators_of(w)
        res = hunt(w, gens, depth=args.depth, cap=args.cap,
                   max_states=args.max_states, refine_limit=args.refine_limit,
                   seed=args.seed, include_peel=False,
                   deadline=max(1.0, args.per_member))
        out_rows.append({k: v for k, v in res.items() if k != "rows"})
        hits.extend(res["hits"])
    blob = {"record": "S11 harvest sample hunt", "n_members": len(members),
            "hits": hits, "members": out_rows,
            "seconds": round(time.time() - t0, 2)}
    print(json.dumps({"n_members": len(members), "n_hits": len(hits),
                      "seconds": blob["seconds"]}, indent=1))
    _emit(args.out, blob)
    print("wrote", args.out)
    return blob


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ladder")
    p.add_argument("--ranks", default="2,4,6,8")
    p.add_argument("--lengths", default="13,16,19,22,25")
    p.add_argument("--per-cell", type=int, default=8)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--evals", type=int, default=40_000)
    p.add_argument("--rank2-evals", type=int, default=200_000)
    p.add_argument("--tries", type=int, default=4000)
    p.add_argument("--width", type=int, default=1)
    p.add_argument("--cap", type=int, default=DEFAULT_CAP)
    p.add_argument("--deadline", type=float, default=None)
    p.add_argument("--grow-deadline", type=float, default=45.0)
    p.add_argument("--rank2", default="results/stable_ac/fable/witness_sensitivity.json")
    p.add_argument("--out", default="results/stable_ac/fable/s11_ladder.json")
    p.set_defaults(func=cmd_ladder)

    p = sub.add_parser("scan")
    p.add_argument("--ranks", default="2,3,4,6,8")
    p.add_argument("--lengths", default="13,16,19,22,25")
    p.add_argument("--per-cell", type=int, default=50)
    p.add_argument("--tries", type=int, default=20_000)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--cap", type=int, default=DEFAULT_CAP)
    p.add_argument("--width", type=int, default=1)
    p.add_argument("--out", default="results/stable_ac/fable/s11_decidability.json")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("sr")
    p.add_argument("--ranks", default="2,3,4")
    p.add_argument("--max-base-length", type=int, default=12)
    p.add_argument("--spike-depth", type=int, default=2)
    p.add_argument("--per-rank", type=int, default=400)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--cap", type=int, default=DEFAULT_CAP)
    p.add_argument("--deadline", type=float, default=120.0)
    p.add_argument("--out", default="results/stable_ac/fable/s11_sr_hunt.json")
    p.set_defaults(func=cmd_sr)

    p = sub.add_parser("sr-spelled")
    p.add_argument("--trivial-only", action="store_true",
                   help="bases = Todd-Coxeter-verified trivial-group presentations")
    p.add_argument("--max-base-length", type=int, default=8)
    p.add_argument("--max-bases", type=int, default=400)
    p.add_argument("--cap", type=int, default=DEFAULT_CAP)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--deadline", type=float, default=180.0)
    p.add_argument("--out", default="results/stable_ac/fable/s11_sr_spelled.json")
    p.set_defaults(func=cmd_sr_spelled)

    p = sub.add_parser("ak3")
    p.add_argument("--evals", type=int, default=300_000)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--cap", type=int, default=6_000_000)
    p.add_argument("--deadline", type=float, default=600.0)
    p.add_argument("--calibrate", action="store_true")
    p.add_argument("--calibrate-length", type=int, default=17)
    p.add_argument("--calibrate-states", type=int, default=4)
    p.add_argument("--calibrate-seeds", type=int, default=5)
    p.add_argument("--ladder", default="results/stable_ac/fable/s11_ladder.json")
    p.add_argument("--out", default="results/stable_ac/fable/s11_ak3_depth2.json")
    p.set_defaults(func=cmd_ak3)

    p = sub.add_parser("hunt")
    p.add_argument("--words", default=None, help="comma-separated relators")
    p.add_argument("--generators", default=None)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--cap", type=int, default=DEFAULT_CAP)
    p.add_argument("--max-states", type=int, default=4000)
    p.add_argument("--refine-limit", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-peel", action="store_true")
    p.add_argument("--deadline", type=float, default=None)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--out", default="results/stable_ac/fable/s11_hunt.json")
    p.set_defaults(func=cmd_hunt)

    p = sub.add_parser("harvest")
    p.add_argument("--path",
                   default="results/stable_ac/fable/stable_contrast_ak3z_members.jsonl.gz")
    p.add_argument("--min-length", type=int, default=21)
    p.add_argument("--max-length", type=int, default=27)
    p.add_argument("--limit", type=int, default=60)
    p.add_argument("--sample-rate", type=float, default=0.02)
    p.add_argument("--depth", type=int, default=1)
    p.add_argument("--cap", type=int, default=DEFAULT_CAP)
    p.add_argument("--max-states", type=int, default=400)
    p.add_argument("--refine-limit", type=int, default=2)
    p.add_argument("--per-member", type=float, default=6.0)
    p.add_argument("--deadline", type=float, default=240.0)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--out", default="results/stable_ac/fable/s11_harvest.json")
    p.set_defaults(func=cmd_harvest)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":                                          # pragma: no cover
    main()
