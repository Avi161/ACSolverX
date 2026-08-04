"""A9 -- thickenability sweep of the 124 unsolved Miller-Schupp AC-equivalence classes.

WHY THIS COULD SETTLE AN OPEN CASE
----------------------------------
Lackenby (arXiv:2606.06122v1, abstract VERIFIED-FROM-SOURCE in
``results/stable_ac/theory/fable/S2_LITERATURE_HIGH_RANK.md`` Q1): *thickenable balanced
presentations of the trivial group satisfy the (unstable) Andrews-Curtis conjecture*.
Every one of the 124 minimal representatives in ``results/stable_ac/fable/aca_124.csv``
is balanced (2 generators, 2 relators) and presents the trivial group (Todd-Coxeter is
re-run here per row as a check, not as an assumption).  Therefore

    ANY of the 124 -- or any member of its AC class we reach -- with gamma_N = 0 is
    AC-trivial, and an open Miller-Schupp case is settled.

The project has censused AK(3)'s class (``ak3_matched_members.jsonl.gz``, 124,296
members, 0 spherical).  ``aca_115 = ("YXYxyx", "YYYYxxx")`` IS AK(3) and is the anchor
row of this sweep.  The other 123 classes had never been tested.

UNITS (fixed before anything else, per S3 section 0)
----------------------------------------------------
``neuwirth_rank_n.gamma_N_factorial_n`` returns ``minimum_defect``; this project's
``gamma_N`` is ``minimum_defect // 2``.  ``defect == 0`` <=> ``SPHERICAL`` <=>
thickenable.  Every raw number recorded here is the UNHALVED defect and is labelled
``defect``; every halved number is labelled ``gamma_N``.

TWO INSTRUMENTS, DELIBERATELY KEPT APART
----------------------------------------
**Instrument A -- the exact decision** (``disconnected_split.decide_pair``: the R1c-v2
cut-scheme solver first, exact factorial census second).  This is the entry point the
13,040-member AK(2) battery and the 124,296-member AK(3) matched control both used.  It
is a *decision procedure*, not a sampler: its ``NOT_SPHERICAL`` is exhaustive over
schemes x phases x seeds x cross-cycle combinations (or is a certified non-planarity),
and everything else fails closed to ``UNSUPPORTED`` / ``UNDECIDED_BUDGET``.  A
budget exhaustion is NEVER converted into a NO.  Instrument A answers the headline
question (is any row thickenable?) two-sidedly.

**Instrument B -- the sampled upper bound** (``gateway_scan.sampled_min_defect``, with
every witness re-verified by ``gateway_scan.verify_witness``).  This is a ONE-SIDED
hill-climb: it bounds ``gamma_N`` from ABOVE only.  It exists here solely to put a
*number* on rows whose exact census does not fit the cap, so that the 124 can be ranked
by how close to thickenable they are.  Per
``experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`` its silence is
worth exactly its measured detection rate, so stage ``calibration`` measures that rate
BY LENGTH on states known to be thickenable, and every row whose length sits above the
calibrated band is flagged ``sample_calibrated = False``.  Nothing on this line reads an
instrument-B null as evidence of non-thickenability.

**Length is a confound in every cross-row comparison** (filed lesson
``experiments/lessons/contrast-length-confound.md``).  The ranking produced here mixes
total lengths 13-25 and instrument B degrades with length, so the ranking is explicitly
reported with the length of every row and is NOT to be read as "row P is closer to
thickenable than row Q" across different lengths.

STAGES (each is a separate guarded run; see PROCESS_GUARD.md)
------------------------------------------------------------
``sweep``          -- all 124 representatives: exact decision (A), exact census where the
                      compatible family fits the cap, sampled upper bound (B),
                      Todd-Coxeter triviality check, cross-check of A against the
                      independent rank-n Theorem-R solver ``solve_spherical_n``.
``neighbourhood``  -- the bounded rank-2 AC neighbourhood: every one-move image (AC1
                      invert, AC2 multiply over all cyclic rotations and both signs, AC3
                      conjugation by a single generator), cyclically reduced and
                      deduplicated on ``ac_words.canon_pair`` (filed trap
                      ``harvest-dedup-on-reduced-forms.md``), each decided by
                      instrument A; then a bounded best-first canonical harvest from the
                      top-ranked rows using the validated
                      ``ak2_battery.canon_class_children`` operator.
``calibration``    -- the mandatory positive ladder.  gamma_N = 0 states from
                      ``ak2_members.jsonl`` (verdict SPHERICAL) plus the census-certified
                      rungs of ``witness_sensitivity.json``, run through BOTH instruments
                      at the sweep's own budgets, detection rate reported BY LENGTH.

New-files-only contract: this module imports the existing stack and modifies nothing.
Plain CPU python3.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import os
import random
import time
from collections import Counter, defaultdict
from math import factorial

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import gateway_scan as GS
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable.ak2_battery import canon_class_children
from experiments.stable_ac.fable.disconnected_split import decide_pair
from experiments.stable_ac.fable.rank3_round2 import (
    BRANCH_BUDGET,
    FALLBACK_CAP,
    SCHEME_BUDGET,
)

__all__ = [
    "GENERATORS",
    "CENSUS_CAP",
    "SAMPLE_BUDGET",
    "SAMPLE_SEEDS",
    "MASTER_SEED",
    "AK3_ROW",
    "SweepContradiction",
    "load_reps",
    "census_size",
    "exact_decision",
    "exact_census",
    "sampled_upper",
    "sweep_row",
    "rank_rows",
    "one_move_images",
    "positive_ladder",
    "run_sweep",
    "run_neighbourhood",
    "run_calibration",
]

GENERATORS = ("x", "y")

# per-row exact-census cap, pinned to the round-2 value the AK(2)/AK(3) batteries used
CENSUS_CAP = FALLBACK_CAP                     # 2,000,000 compatible rotation systems
SAMPLE_BUDGET = 40_000                        # instrument-B evaluations per seed
SAMPLE_SEEDS = 3                              # independent seeds per state
MASTER_SEED = 20260804
TC_CAP = 2_000_000                            # Todd-Coxeter coset cap per row
# (200,000 is not enough: aca_82 and aca_86 need ~2.4e5 and ~2.3e5 cosets before the
#  enumeration collapses to index 1.  A CAP_EXCEEDED is recorded as "unknown", never
#  as "not trivial".)

# neighbourhood budgets (bounded so no single stage can hang)
NEIGHBOUR_TOP_N = 10                          # rows given the deeper harvest
NEIGHBOUR_HARVEST_POPS = 60                   # best-first pops per top row
NEIGHBOUR_STATE_CAP = 42_000                  # hard cap on decided neighbourhood states
NEIGHBOUR_CENSUS_CAP = 50_000                 # census fallback size cap for a neighbour
NEIGHBOUR_CENSUS_BUDGET = 400                 # how many neighbours may get that fallback

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
RESULTS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")

DEFAULT_CSV = os.path.join(RESULTS, "aca_124.csv")
AK2_MEMBERS = os.path.join(RESULTS, "ak2_members.jsonl")
WITNESS_SENSITIVITY = os.path.join(RESULTS, "witness_sensitivity.json")

SWEEP_OUT = os.path.join(RESULTS, "u124_sweep.jsonl")
SWEEP_SUMMARY = os.path.join(RESULTS, "u124_sweep_summary.json")
NEIGHBOUR_OUT = os.path.join(RESULTS, "u124_neighbourhood.jsonl")
NEIGHBOUR_SUMMARY = os.path.join(RESULTS, "u124_neighbourhood_summary.json")
CALIBRATION_OUT = os.path.join(RESULTS, "u124_calibration.json")

SPHERICAL = "SPHERICAL"
NOT_SPHERICAL = "NOT_SPHERICAL"
UNSUPPORTED = "UNSUPPORTED"

AK3_ROW = "aca_115"
AK3_PAIR = ("YXYxyx", "YYYYxxx")
AK3_MINIMUM_DEFECT = 4        # pinned literal: exact 86,400-rotation census, S3 section 3

HIT_BANNER = (
    "gamma_N = 0 on a Miller-Schupp unsolved representative (or a member of its AC "
    "class).  By Lackenby arXiv:2606.06122v1 (thickenable + balanced + trivial group "
    "=> AC-trivializable) this SETTLES that open case -- but only after: (i) the "
    "rotation witness is re-verified independently, (ii) Todd-Coxeter certifies the "
    "group trivial, (iii) for a neighbourhood hit, the AC move chain back to the "
    "representative is replayed explicitly.  Report nothing before all three."
)


class SweepContradiction(RuntimeError):
    """Two instruments disagreed, or a pinned anchor moved.  Raised, never a verdict."""


# --------------------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------------------


def load_reps(path: str = DEFAULT_CSV) -> list:
    """The 124 rows of ``aca_124.csv`` as dicts with the pair and its total length."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pair = (row["r1"], row["r2"])
            out.append({
                "name": row["name"],
                "pair": pair,
                "canonical": list(W.canon_pair(*pair)),
                "total_length": len(pair[0]) + len(pair[1]),
                "n_members": int(row["n_members"]),
            })
    return out


def census_size(pair, generators=GENERATORS) -> int:
    """``prod_g (deg(g+) - 1)!`` -- the size of the compatible-rotation family."""
    joined = "".join(pair).lower()
    total = 1
    for g in generators:
        deg = joined.count(g)
        if deg:
            total *= factorial(deg - 1)
    return total


# --------------------------------------------------------------------------------------
# instrument A -- the exact decision
# --------------------------------------------------------------------------------------


def _counters_of(verdict) -> dict | None:
    decision = getattr(verdict, "decision", None)
    if decision is None or getattr(decision, "counters", None) is None:
        return None
    counters = decision.counters
    raw = counters.as_dict() if hasattr(counters, "as_dict") else dict(counters.__dict__)
    keep = ("schemes_considered", "phase_tuples_considered", "exhaustive",
            "scheme_budget", "branch_budget", "macro_family_size")
    return {k: raw[k] for k in keep if k in raw}


def exact_decision(pair, census_cap: int = 0, cross_check: bool = True) -> dict:
    """Instrument A on one rank-2 pair, plus an independent Theorem-R cross-check.

    ``census_cap = 0`` keeps this purely the R1c-v2 solver (the census is run
    separately by :func:`exact_census` so its cost is accounted for on its own line).
    ``solve_spherical_n`` is the rank-n Theorem-R solver: it shares the slot arithmetic
    with R1c-v2 but reaches it through a completely different support decomposition, so
    a SPHERICAL/NOT_SPHERICAL disagreement between the two is a
    :class:`SweepContradiction`, never a verdict.
    """
    pair = tuple(pair)
    t0 = time.time()
    verdict, support = decide_pair(pair, scheme_budget=SCHEME_BUDGET,
                                   branch_budget=BRANCH_BUDGET, census_cap=census_cap)
    counters = _counters_of(verdict)
    out = {
        "verdict": verdict.verdict,
        "method": verdict.method,
        "reason": verdict.reason,
        "support_kind": support.kind if support is not None else None,
        "support_reason": support.reason if support is not None else None,
        "counters": counters,
        "exhaustive": bool(counters.get("exhaustive")) if counters else None,
        "seconds": round(time.time() - t0, 4),
    }
    if cross_check:
        try:
            other = RN.solve_spherical_n(pair, GENERATORS)
            out["theorem_r_verdict"] = other.verdict
            out["theorem_r_reason"] = other.reason
        except Exception as exc:                       # noqa: BLE001 -- audit surface
            out["theorem_r_verdict"] = "ERROR"
            out["theorem_r_reason"] = f"{type(exc).__name__}: {exc}"
        decisive = (SPHERICAL, NOT_SPHERICAL)
        if (out["verdict"] in decisive and out["theorem_r_verdict"] in decisive
                and out["verdict"] != out["theorem_r_verdict"]):
            raise SweepContradiction(
                f"R1c-v2 says {out['verdict']} but Theorem-R solve_spherical_n says "
                f"{out['theorem_r_verdict']} for {pair}"
            )
    return out


def exact_census(pair, cap: int = CENSUS_CAP) -> dict:
    """Exact ``minimum_defect`` over the whole compatible family, or a cap refusal."""
    pair = tuple(pair)
    size = census_size(pair)
    if size > cap:
        return {"ran": False, "expected_cases": size, "cap": cap,
                "reason": f"compatible family {size} exceeds the per-row cap {cap}"}
    t0 = time.time()
    census = RN.gamma_N_factorial_n(pair, GENERATORS, cap_rotations=cap,
                                    keep_accepting=True)
    if census["status"] != "OK":
        return {"ran": False, "expected_cases": size, "cap": cap,
                "reason": f"census status {census['status']}"}
    return {
        "ran": True,
        "expected_cases": census["expected_cases"],
        "enumerated_cases": census["enumerated_cases"],
        "minimum_defect": census["minimum_defect"],
        "gamma_N": census["minimum_genus"],
        "link_components": census["link_components"],
        "defect_histogram": {str(k): v
                             for k, v in sorted(census["defect_histogram"].items())},
        "accepting_orders": len(census["accepting_orders"]),
        "witness": ({str(k): list(v) for k, v in census["accepting_orders"][0].items()}
                    if census["accepting_orders"] else None),
        "seconds": round(time.time() - t0, 3),
    }


# --------------------------------------------------------------------------------------
# instrument B -- the sampled upper bound (ONE-SIDED)
# --------------------------------------------------------------------------------------


def sampled_upper(pair, budget: int = SAMPLE_BUDGET, seeds: int = SAMPLE_SEEDS,
                  master_seed: int = MASTER_SEED) -> dict:
    """Best (lowest) defect found by ``seeds`` independent hill-climbs, each verified.

    BOUND DIRECTION (filed lesson ``parallel-runs-and-bound-direction.md``): every
    number here is an UPPER bound on ``gamma_N``.  A high value never shows the true
    gamma_N is high -- only that this budget did not find anything lower.
    """
    pair = tuple(pair)
    best = None
    best_orders = None
    per_seed = []
    t0 = time.time()
    for k in range(seeds):
        rng = random.Random((master_seed * 1_000_003 + k) % (2 ** 61))
        defect, orders = GS.sampled_min_defect(pair, budget, rng)
        per_seed.append(defect)
        if best is None or defect < best:
            best, best_orders = defect, orders
    verified = None
    if best_orders is not None:
        verified = GS.verify_witness(pair, best_orders)
        if verified != best:
            raise SweepContradiction(
                f"sampler reported defect {best} but the independent witness check "
                f"recomputed {verified} for {pair}"
            )
    return {
        "budget_per_seed": budget,
        "seeds": seeds,
        "per_seed_best_defect": per_seed,
        "best_defect": best,
        "verified_defect": verified,
        "gamma_N_upper": None if best is None else best // 2,
        "witness": ({str(k): list(v) for k, v in best_orders.items()}
                    if best_orders is not None else None),
        "seconds": round(time.time() - t0, 3),
        "bound_direction": "UPPER bound on gamma_N only; a null proves nothing",
    }


# --------------------------------------------------------------------------------------
# one row of the sweep
# --------------------------------------------------------------------------------------


def sweep_row(rec: dict, census_cap: int = CENSUS_CAP, budget: int = SAMPLE_BUDGET,
              seeds: int = SAMPLE_SEEDS, master_seed: int = MASTER_SEED,
              tc_cap: int = TC_CAP) -> dict:
    """Decision + exact census where affordable + sampled bound + triviality check."""
    pair = tuple(rec["pair"])
    row = dict(rec)
    row["pair"] = list(pair)
    row["record"] = "u124_row"
    row["census_family_size"] = census_size(pair)
    link = RN.build_link_n(pair, GENERATORS)
    row["structural_link_components"] = link.link_components
    row["has_A_loop"] = link.has_loop
    row["decision"] = exact_decision(pair)
    row["census"] = exact_census(pair, cap=census_cap)
    row["sample"] = sampled_upper(pair, budget=budget, seeds=seeds,
                                  master_seed=master_seed)

    tc = CE.is_trivial_group(pair, generators=GENERATORS, cap=tc_cap)
    row["todd_coxeter"] = {"status": tc["status"], "index": tc["index"],
                           "trivial": tc["trivial"],
                           "cosets_defined": tc["cosets_defined"], "cap": tc["cap"]}

    verdict = row["decision"]["verdict"]
    census = row["census"]
    if census["ran"]:
        # exact both ways
        row["gamma_N_lower"] = census["gamma_N"]
        row["gamma_N_upper"] = census["gamma_N"]
        row["gamma_N_exact"] = census["gamma_N"]
        row["gamma_source"] = "exact_census"
        census_verdict = SPHERICAL if census["minimum_defect"] == 0 else NOT_SPHERICAL
        if verdict in (SPHERICAL, NOT_SPHERICAL) and verdict != census_verdict:
            raise SweepContradiction(
                f"instrument A says {verdict} but the exact census minimum defect is "
                f"{census['minimum_defect']} for {pair}"
            )
    else:
        row["gamma_N_exact"] = None
        row["gamma_source"] = "sample_upper + decision_lower"
        if verdict == SPHERICAL:
            row["gamma_N_lower"] = 0
        elif verdict == NOT_SPHERICAL:
            row["gamma_N_lower"] = 1          # defect > 0 and defect is even => >= 2
        else:
            row["gamma_N_lower"] = None
        row["gamma_N_upper"] = row["sample"]["gamma_N_upper"]

    lower, upper = row["gamma_N_lower"], row["gamma_N_upper"]
    # A bracket that closes is an EXACT gamma_N even without a census: instrument A's
    # exhaustive NOT_SPHERICAL certifies gamma_N >= 1 and a re-verified defect-2 witness
    # certifies gamma_N <= 1, so gamma_N = 1 exactly (gateway_scan.py's two-sided
    # argument).  This is a certificate, not a sample: it does not depend on the
    # sampler's detection rate, only on the witness being valid.
    row["gamma_N_certified"] = (lower is not None and upper is not None
                                and lower == upper)
    row["gamma_N_certified_value"] = lower if row["gamma_N_certified"] else None
    row["thickenable"] = (verdict == SPHERICAL) or (
        census["ran"] and census["minimum_defect"] == 0)
    row["decision_is_two_sided"] = verdict in (SPHERICAL, NOT_SPHERICAL)
    # A row is INFORMATIVE about thickenability iff a two-sided instrument decided it:
    # the exact census, or instrument A with a certified-exhaustive negative / a
    # certified non-planar support.  Everything else is UNINFORMATIVE, never a NO.
    row["informative"] = bool(census["ran"] or row["decision_is_two_sided"])
    row["informative_reason"] = (
        "exact census over the whole compatible family" if census["ran"]
        else ("instrument A: " + str(row["decision"]["reason"]))
        if row["decision_is_two_sided"]
        else "UNINFORMATIVE: neither instrument returned a two-sided verdict")
    if row["thickenable"]:
        row["HIT"] = HIT_BANNER
    return row


# --------------------------------------------------------------------------------------
# ranking
# --------------------------------------------------------------------------------------


def rank_rows(rows: list) -> list:
    """Rank by the best KNOWN upper bound on gamma_N, shorter length breaking ties.

    LENGTH CONFOUND (``experiments/lessons/contrast-length-confound.md``): the ranking
    key is an upper bound produced by an instrument whose tightness degrades with total
    length, and the rows span lengths 13-25.  Two rows of different length are NOT
    comparable; the ranking is a search-order recommendation, not a measurement of
    relative distance to thickenability.  Rows with no upper bound sort last.
    """
    def key(row):
        upper = row.get("gamma_N_upper")
        return (upper if upper is not None else 10 ** 6,
                row["total_length"], row["name"])
    ordered = sorted(rows, key=key)
    for i, row in enumerate(ordered, 1):
        row["rank"] = i
    return ordered


# --------------------------------------------------------------------------------------
# the bounded rank-2 AC neighbourhood
# --------------------------------------------------------------------------------------


def _rotations(w: str) -> list:
    return sorted({w[i:] + w[:i] for i in range(len(w))})


def one_move_images(pair, cap: int) -> dict:
    """Every one-move AC image of ``pair``, keyed on the reduced canonical form.

    * **AC1** (invert): ``r_i -> r_i^{-1}``.
    * **AC2** (multiply): ``r_i -> r_i r_j^{+-1}``, ``j != i``, over EVERY pair of cyclic
      rotations of the two relators.  Rotating a relator is AC3 by single generators
      (Lemma P of ``R1E_DISCONNECTED_LINK.md``), so every image listed is reachable by a
      genuine AC1-AC3 composite.
    * **AC3** (conjugate): ``r_i -> g r_i g^{-1}`` for ``g`` a single generator or its
      inverse.

    The seen-set is keyed on ``ac_words.canon_pair`` -- the cyclically REDUCED canonical
    form -- per ``experiments/lessons/harvest-dedup-on-reduced-forms.md``; exact-word
    keys waste ~97% of pops on conjugacy churn.  A relator that free-reduces to empty or
    exceeds ``cap`` is dropped (the ``ac_words.apply_move`` no-op rule).  Returns
    ``{canonical pair: (exact image, move label)}``; the parent's own class is excluded.
    """
    pair = tuple(W.cyclic_reduce(w) for w in pair)
    parent_key = W.canon_pair(*pair)
    out = {}

    def offer(state, label):
        if any(not w for w in state):
            return
        if any(len(w) > cap for w in state):
            return
        key = W.canon_pair(*state)
        if key == parent_key or key in out:
            return
        out[key] = (tuple(state), label)

    for i in (0, 1):
        state = list(pair)
        state[i] = W.free_reduce(W.inverse(state[i]))
        offer(state, f"AC1(r{i + 1})")

    for i in (0, 1):
        for g in ("x", "X", "y", "Y"):
            state = list(pair)
            state[i] = W.free_reduce(g + state[i] + W.inverse_letter(g))
            offer(state, f"AC3(r{i + 1},{g})")

    for i, j in ((0, 1), (1, 0)):
        for a in _rotations(pair[i]):
            for b in _rotations(pair[j]):
                for sign in (1, -1):
                    new = W.free_reduce(a + (b if sign > 0 else W.inverse(b)))
                    state = [None, None]
                    state[i] = new
                    state[j] = pair[j]
                    offer(state, f"AC2(r{i + 1}<-r{i + 1}r{j + 1}^{sign:+d})")
    return out


def _harvest_canonical(root_key, pops: int, cap: int, state_cap: int) -> dict:
    """Best-first canonical harvest with the validated ``canon_class_children`` operator.

    Same operator, seen-set and priority as the AK(2) battery and the AK(3) matched
    control (``ak2_battery.canon_class_children``, imported): a popped canonical class is
    expanded through every concatenation move applied to every pair of cyclic rotations
    of its two cyclically reduced relators.  Unlike ``ak2_battery.harvest_members`` this
    wrapper does not assert the pop contract -- a small class legitimately exhausts its
    queue early -- and it stops at ``state_cap`` distinct members.
    """
    found = {root_key: 0}
    heap = [(len(root_key[0]) + len(root_key[1]), 0, root_key)]
    tie = 1
    popped = 0
    while heap and popped < pops and len(found) < state_cap:
        _p, _t, key = heapq.heappop(heap)
        popped += 1
        for child in sorted(canon_class_children(key, cap)):
            if child in found:
                continue
            found[child] = len(found)
            heapq.heappush(heap, (len(child[0]) + len(child[1]), tie, child))
            tie += 1
            if len(found) >= state_cap:
                break
    return {"pops": popped, "pop_budget": pops, "relator_cap": cap,
            "distinct_members": len(found), "queue_remaining": len(heap),
            "members": found}


# --------------------------------------------------------------------------------------
# the positive ladder (mandatory calibration)
# --------------------------------------------------------------------------------------


def _min_degree(pair) -> int:
    joined = "".join(pair).lower()
    return min(joined.count("x"), joined.count("y"))


def positive_ladder(ak2_path: str = AK2_MEMBERS,
                    sensitivity_path: str = WITNESS_SENSITIVITY,
                    min_length: int = 13, max_length: int = 25,
                    min_degree: int = 3) -> list:
    """States KNOWN to have gamma_N = 0, with the provenance of that knowledge.

    Two independent sources:

    * ``ak2_members.jsonl`` rows with ``verdict == SPHERICAL`` -- members of AK(2)'s
      provably AC-trivial class, decided by the very stack this sweep uses.  This is the
      source the task specifies and it is the primary ladder.
    * the census-certified rungs of ``witness_sensitivity.json`` -- grown by spikes and
      grafts from a census-confirmed fixture and certified either by exact census or by
      an independently re-verified defect-0 witness.  These extend the ladder above the
      AK(2) corpus's longest positive.

    SELECTION BIAS, recorded because it decides how the numbers may be read: both
    sources are biased toward detectable states (an AK(2) row is SPHERICAL because the
    stack said so; a sensitivity rung entered the ladder only because a climb certified
    it).  Both biases push measured detection rates UP.  A LOW cell is therefore
    conclusive -- the instrument is blind there -- while a HIGH cell is optimistic and
    never licenses reading a null as absence.

    COMPOSITION MISMATCH, recorded for the same reason.  ``min_degree`` filters out the
    degenerate tail (a ladder state whose alphabet is essentially one generator), but no
    filter can fix the deeper mismatch: the 124 targets all have ``min_degree >= 6``
    while AK(2)'s thickenable members top out far below that.  A ladder state with a
    small germ degree has a much smaller compatible family in that direction, which makes
    it EASIER for the sampler than a target of the same total length.  This bias also
    points UP, so it can only make a null look better than it is.
    """
    ladder = []
    seen = set()
    if os.path.exists(ak2_path):
        with open(ak2_path, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if row.get("verdict") != SPHERICAL:
                    continue
                pair = tuple(row["canonical"])
                length = len(pair[0]) + len(pair[1])
                if not (min_length <= length <= max_length):
                    continue
                if _min_degree(pair) < min_degree:
                    continue
                key = W.canon_pair(*pair)
                if key in seen:
                    continue
                seen.add(key)
                ladder.append({"pair": list(pair), "total_length": length,
                               "min_degree": _min_degree(pair),
                               "census_family_size": census_size(pair),
                               "source": "ak2_members.jsonl",
                               "certified_by": row.get("method")})
    if os.path.exists(sensitivity_path):
        with open(sensitivity_path, encoding="utf-8") as fh:
            doc = json.load(fh)
        for rung in doc.get("ladder", ()):
            pair = tuple(rung["words"])
            length = len(pair[0]) + len(pair[1])
            if not (min_length <= length <= max_length):
                continue
            if _min_degree(pair) < min_degree:
                continue
            key = W.canon_pair(*pair)
            if key in seen:
                continue
            seen.add(key)
            ladder.append({"pair": list(pair), "total_length": length,
                           "min_degree": _min_degree(pair),
                           "census_family_size": census_size(pair),
                           "source": "witness_sensitivity.json ladder",
                           "certified_by": rung.get("certified_by")})
    ladder.sort(key=lambda r: (r["total_length"], r["pair"]))
    return ladder


# --------------------------------------------------------------------------------------
# stage runners
# --------------------------------------------------------------------------------------


def _write_jsonl(path: str, rows) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def _write_json(path: str, doc) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")


def _calibration_bands(calibration_path: str = CALIBRATION_OUT) -> dict:
    """``{length: instrument-B detection rate}`` plus the blind threshold, if measured.

    Read BEFORE any null is reported, per
    ``experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md``: a sampled
    upper bound at a length where the instrument's measured detection rate is 0 (or
    where no positive control exists at all) is not a measurement and is marked so.
    """
    if not os.path.exists(calibration_path):
        return {"available": False}
    with open(calibration_path, encoding="utf-8") as fh:
        doc = json.load(fh)
    cells = doc.get("cells_by_total_length", {})
    return {
        "available": True,
        "path": os.path.relpath(calibration_path, REPO_ROOT),
        "rate_by_length": {int(k): v["instrument_B_detection_rate"]
                           for k, v in cells.items()},
        "a_rate_by_length": {int(k): v["instrument_A_detection_rate"]
                             for k, v in cells.items()},
        "blind_from_length": doc.get("instrument_B", {}).get("blind_from_length"),
        "lengths_with_no_positive_control":
            doc.get("lengths_with_no_positive_control", []),
    }


def run_sweep(csv_path: str = DEFAULT_CSV, out_path: str = SWEEP_OUT,
              summary_path: str = SWEEP_SUMMARY, census_cap: int = CENSUS_CAP,
              budget: int = SAMPLE_BUDGET, seeds: int = SAMPLE_SEEDS,
              limit: int | None = None, calibration_path: str = CALIBRATION_OUT,
              verbose: bool = True) -> dict:
    """Stage 1: decide and measure all 124 representatives."""
    started = time.time()
    reps = load_reps(csv_path)
    if limit is not None:
        reps = reps[:limit]
    bands = _calibration_bands(calibration_path)
    rows = []
    for i, rec in enumerate(reps, 1):
        row = sweep_row(rec, census_cap=census_cap, budget=budget, seeds=seeds)
        length = row["total_length"]
        if row["census"]["ran"]:
            row["sample_calibrated"] = None       # irrelevant: the value is exact
        elif not bands.get("available"):
            row["sample_calibrated"] = None
        else:
            rate = bands["rate_by_length"].get(length)
            blind = bands.get("blind_from_length")
            row["sample_calibrated"] = bool(
                rate is not None and rate > 0.0
                and (blind is None or length < blind))
            row["sample_detection_rate_at_this_length"] = rate
        rows.append(row)
        if verbose and (i % 20 == 0 or i == len(reps)):
            print(f"  [sweep] {i}/{len(reps)} rows ({time.time() - started:.0f}s)",
                  flush=True)

    # anchor: AK(3) must reproduce its pinned exact census
    anchor = next((r for r in rows if r["name"] == AK3_ROW), None)
    anchor_ok = None
    if anchor is not None:
        if tuple(anchor["pair"]) != AK3_PAIR:
            raise SweepContradiction(
                f"{AK3_ROW} is {tuple(anchor['pair'])}, expected AK(3) {AK3_PAIR}")
        if anchor["census"]["ran"]:
            if anchor["census"]["minimum_defect"] != AK3_MINIMUM_DEFECT:
                raise SweepContradiction(
                    f"AK(3) exact census minimum defect "
                    f"{anchor['census']['minimum_defect']} != pinned "
                    f"{AK3_MINIMUM_DEFECT}")
            anchor_ok = True

    ranked = rank_rows(rows)
    hits = [r for r in ranked if r["thickenable"]]
    verdicts = Counter(r["decision"]["verdict"] for r in ranked)
    methods = Counter(r["decision"]["method"] for r in ranked)
    upper_by_length = defaultdict(list)
    for r in ranked:
        if r["gamma_N_upper"] is not None:
            upper_by_length[r["total_length"]].append(r["gamma_N_upper"])

    summary = {
        "record": "u124_sweep_summary",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": (
            "MACHINERY + a decidable test of Lackenby's thickenability hypothesis on "
            "the 124 unsolved Miller-Schupp AC classes.  A SPHERICAL row would settle "
            "that open case; a NOT_SPHERICAL row says only that this presentation is "
            "not thickenable, which is NOT a statement about its AC class."),
        "units": "defects are UNHALVED; gamma_N = defect // 2; defect 0 == SPHERICAL",
        "source_csv": os.path.relpath(csv_path, REPO_ROOT),
        "rows": len(ranked),
        "budgets": {"census_cap": census_cap, "sample_budget_per_seed": budget,
                    "sample_seeds": seeds, "scheme_budget": SCHEME_BUDGET,
                    "branch_budget": BRANCH_BUDGET, "tc_cap": TC_CAP,
                    "master_seed": MASTER_SEED},
        "LOUD_THICKENABLE_ALERT": bool(hits),
        "thickenable_rows": [r["name"] for r in hits],
        "decision_verdict_histogram": dict(sorted(verdicts.items())),
        "decision_method_histogram": dict(sorted(methods.items())),
        "two_sided_rows": sum(1 for r in ranked if r["decision_is_two_sided"]),
        "informative_rows": sum(1 for r in ranked if r["informative"]),
        "uninformative_rows": [
            {"name": r["name"], "total_length": r["total_length"],
             "reason": r["informative_reason"]}
            for r in ranked if not r["informative"]],
        "sample_calibration": bands,
        "rows_with_uncalibrated_sampled_bound": [
            r["name"] for r in ranked if r.get("sample_calibrated") is False],
        "sample_calibrated_meaning": (
            "sample_calibrated = False means the ABSENCE of a lower witness at this "
            "length is uninformative -- the sampler's measured detection rate there is "
            "0 or was never measured, so gamma_N_upper may be far above the truth.  It "
            "does NOT weaken a witness that WAS found: every recorded witness was "
            "re-verified by an independent recomputation of the defect, so "
            "gamma_N <= gamma_N_upper is a certificate at every length."),
        "certified_gamma_N_rows": [
            {"name": r["name"], "pair": r["pair"], "total_length": r["total_length"],
             "gamma_N": r["gamma_N_certified_value"], "source": r["gamma_source"]}
            for r in ranked if r["gamma_N_certified"]],
        "gateways_gamma_N_1": [
            r["name"] for r in ranked
            if r["gamma_N_certified"] and r["gamma_N_certified_value"] == 1],
        "fail_closed_rows": [
            {"name": r["name"], "verdict": r["decision"]["verdict"],
             "reason": r["decision"]["reason"]}
            for r in ranked if not r["decision_is_two_sided"]],
        "exact_census_rows": [
            {"name": r["name"], "expected_cases": r["census"]["expected_cases"],
             "minimum_defect": r["census"]["minimum_defect"],
             "gamma_N": r["census"]["gamma_N"]}
            for r in ranked if r["census"]["ran"]],
        "ak3_anchor": {
            "row": AK3_ROW, "pair": list(AK3_PAIR),
            "pinned_minimum_defect": AK3_MINIMUM_DEFECT,
            "reproduced": anchor_ok,
            "decision": anchor["decision"]["verdict"] if anchor else None,
            "rank": anchor["rank"] if anchor else None,
        },
        "todd_coxeter": {
            "trivial": sum(1 for r in ranked if r["todd_coxeter"]["trivial"] is True),
            "not_trivial": sum(1 for r in ranked
                               if r["todd_coxeter"]["trivial"] is False),
            "incomplete": sum(1 for r in ranked
                              if r["todd_coxeter"]["trivial"] is None),
        },
        "gamma_upper_histogram": dict(sorted(Counter(
            r["gamma_N_upper"] for r in ranked
            if r["gamma_N_upper"] is not None).items())),
        "gamma_upper_by_length": {
            str(k): {"n": len(v), "min": min(v), "median": sorted(v)[len(v) // 2],
                     "max": max(v)}
            for k, v in sorted(upper_by_length.items())},
        "length_histogram": dict(sorted(Counter(
            r["total_length"] for r in ranked).items())),
        "ranking": [
            {"rank": r["rank"], "name": r["name"], "pair": r["pair"],
             "total_length": r["total_length"],
             "census_family_size": r["census_family_size"],
             "gamma_N_lower": r["gamma_N_lower"], "gamma_N_upper": r["gamma_N_upper"],
             "gamma_N_exact": r["gamma_N_exact"], "source": r["gamma_source"],
             "verdict": r["decision"]["verdict"],
             "gamma_N_certified": r["gamma_N_certified"],
             "sample_calibrated": r.get("sample_calibrated")}
            for r in ranked],
        "length_confound_warning": (
            "The ranking key is an upper bound from a one-sided instrument whose "
            "tightness degrades with total length, and the rows span lengths 13-25.  "
            "Rows of different length are NOT comparable "
            "(experiments/lessons/contrast-length-confound.md).  Read stage "
            "'calibration' before using any row's upper bound as a measurement."),
        "elapsed_seconds": round(time.time() - started, 1),
        "outputs": {"rows": os.path.relpath(out_path, REPO_ROOT),
                    "summary": os.path.relpath(summary_path, REPO_ROOT)},
    }
    if hits:
        summary["HIT_BANNER"] = HIT_BANNER
    _write_jsonl(out_path, ranked)
    _write_json(summary_path, summary)
    if verbose:
        print(f"[sweep] {len(ranked)} rows, verdicts {summary['decision_verdict_histogram']}",
              flush=True)
        if hits:
            print("!" * 78)
            print(f"!!! THICKENABLE ROW(S): {summary['thickenable_rows']} !!!")
            print("!" * 78, flush=True)
        else:
            print("[sweep] no thickenable representative.", flush=True)
    return summary


def run_neighbourhood(sweep_path: str = SWEEP_OUT, out_path: str = NEIGHBOUR_OUT,
                      summary_path: str = NEIGHBOUR_SUMMARY,
                      top_n: int = NEIGHBOUR_TOP_N,
                      harvest_pops: int = NEIGHBOUR_HARVEST_POPS,
                      state_cap: int = NEIGHBOUR_STATE_CAP,
                      depth1_all: bool = True, verbose: bool = True) -> dict:
    """Stage 2: decide the bounded rank-2 AC neighbourhood with instrument A."""
    started = time.time()
    with open(sweep_path, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh]
    rows.sort(key=lambda r: r.get("rank", 10 ** 6))

    decided: dict = {}
    out_rows = []
    hits = []
    per_root = []
    census_used = [0]

    def decide(key, exact, origin, move, depth):
        if key in decided or len(decided) >= state_cap:
            return None
        result = exact_decision(tuple(key), cross_check=False)
        # bounded census fallback: a fail-closed neighbour whose compatible family is
        # small is still decided exactly, never silently folded into the negatives.
        if (result["verdict"] not in (SPHERICAL, NOT_SPHERICAL)
                and census_used[0] < NEIGHBOUR_CENSUS_BUDGET
                and census_size(tuple(key)) <= NEIGHBOUR_CENSUS_CAP):
            census = exact_census(tuple(key), cap=NEIGHBOUR_CENSUS_CAP)
            census_used[0] += 1
            if census["ran"]:
                result = dict(result)
                result["verdict"] = (SPHERICAL if census["minimum_defect"] == 0
                                     else NOT_SPHERICAL)
                result["method"] = "factorial_census"
                result["reason"] = (f"R1c-v2 fail-closed; exact census minimum defect "
                                    f"{census['minimum_defect']}")
                result["exhaustive"] = True
        decided[key] = result["verdict"]
        record = {"record": "u124_neighbour", "canonical": list(key),
                  "exact": list(exact), "origin": origin, "move": move,
                  "depth": depth, "total_length": len(key[0]) + len(key[1]),
                  "verdict": result["verdict"], "method": result["method"],
                  "support_kind": result["support_kind"],
                  "exhaustive": result["exhaustive"], "reason": result["reason"]}
        if result["verdict"] == SPHERICAL:
            record["HIT"] = HIT_BANNER
            tc = CE.is_trivial_group(tuple(key), generators=GENERATORS, cap=TC_CAP)
            record["todd_coxeter"] = {"status": tc["status"], "index": tc["index"],
                                      "trivial": tc["trivial"]}
            hits.append(record)
        out_rows.append(record)
        return record

    # -- depth 1: every one-move image of every representative -------------------------
    targets = rows if depth1_all else rows[:top_n]
    for i, row in enumerate(targets, 1):
        pair = tuple(row["pair"])
        cap = row["total_length"] + 4          # the batteries' relative-headroom rule
        images = one_move_images(pair, cap)
        n_new = 0
        for key, (exact, move) in sorted(images.items()):
            if decide(key, exact, row["name"], move, 1) is not None:
                n_new += 1
        per_root.append({"name": row["name"], "rank": row.get("rank"),
                         "total_length": row["total_length"], "relator_cap": cap,
                         "one_move_images": len(images), "newly_decided": n_new})
        if verbose and (i % 20 == 0 or i == len(targets)):
            print(f"  [nbhd d1] {i}/{len(targets)} roots, {len(decided)} states "
                  f"({time.time() - started:.0f}s)", flush=True)
        if len(decided) >= state_cap:
            break

    # -- deeper: bounded best-first canonical harvest from the top-ranked rows ----------
    harvests = []
    share = max(200, (state_cap - len(decided)) // max(1, top_n))
    for row in rows[:top_n]:
        if len(decided) >= state_cap:
            break
        root_key = tuple(W.canon_pair(*row["pair"]))
        cap = row["total_length"] + 4          # the batteries' relative-headroom rule
        harvest = _harvest_canonical(root_key, harvest_pops, cap,
                                     min(share, max(1, state_cap - len(decided))))
        n_new = 0
        for member in sorted(harvest["members"]):
            if decide(member, member, row["name"], "harvest", None) is not None:
                n_new += 1
        harvests.append({"name": row["name"], "rank": row.get("rank"),
                         "root": list(root_key), "relator_cap": cap,
                         "pops": harvest["pops"], "pop_budget": harvest["pop_budget"],
                         "distinct_members": harvest["distinct_members"],
                         "queue_remaining": harvest["queue_remaining"],
                         "newly_decided": n_new})
        if verbose:
            print(f"  [nbhd deep] {row['name']}: {harvest['distinct_members']} members, "
                  f"{n_new} new ({time.time() - started:.0f}s)", flush=True)

    verdicts = Counter(r["verdict"] for r in out_rows)
    by_length = defaultdict(Counter)
    for r in out_rows:
        by_length[r["total_length"]][r["verdict"]] += 1
    summary = {
        "record": "u124_neighbourhood_summary",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": ("MACHINERY: bounded AC-neighbourhood test of the same Lackenby "
                   "hypothesis.  A SPHERICAL neighbour settles the class it belongs "
                   "to (after an explicit move-chain replay); nothing else here is a "
                   "statement about the AC conjecture."),
        "operator": (
            "depth 1 = every one-move AC image (AC1 invert; AC2 multiply over all "
            "cyclic rotations of both relators, both signs; AC3 conjugation by a single "
            "generator), dropped if a relator empties or exceeds the per-root cap.  "
            "Deeper = best-first canonical harvest with ak2_battery.canon_class_children "
            "(the operator the 13,040-member AK(2) battery and the 124,296-member AK(3) "
            "matched control used).  Seen-set on ac_words.canon_pair, the cyclically "
            "REDUCED canonical form (harvest-dedup-on-reduced-forms.md)."),
        "budgets": {"top_n": top_n, "harvest_pops": harvest_pops,
                    "state_cap": state_cap, "depth1_all": depth1_all,
                    "scheme_budget": SCHEME_BUDGET, "branch_budget": BRANCH_BUDGET,
                    "census_fallback_size_cap": NEIGHBOUR_CENSUS_CAP,
                    "census_fallback_budget": NEIGHBOUR_CENSUS_BUDGET},
        "states_decided": len(decided),
        "census_fallbacks_used": census_used[0],
        "state_cap_reached": len(decided) >= state_cap,
        "uninformative_states": sum(1 for r in out_rows
                                    if r["verdict"] not in (SPHERICAL, NOT_SPHERICAL)),
        "verdict_histogram": dict(sorted(verdicts.items())),
        "verdict_by_total_length": {str(k): dict(sorted(v.items()))
                                    for k, v in sorted(by_length.items())},
        "LOUD_THICKENABLE_ALERT": bool(hits),
        "thickenable_neighbours": [
            {"canonical": h["canonical"], "origin": h["origin"], "move": h["move"],
             "todd_coxeter": h.get("todd_coxeter")} for h in hits],
        "per_root_depth1": per_root,
        "harvests": harvests,
        "elapsed_seconds": round(time.time() - started, 1),
        "outputs": {"rows": os.path.relpath(out_path, REPO_ROOT),
                    "summary": os.path.relpath(summary_path, REPO_ROOT)},
    }
    if hits:
        summary["HIT_BANNER"] = HIT_BANNER
    _write_jsonl(out_path, out_rows)
    _write_json(summary_path, summary)
    if verbose:
        print(f"[nbhd] {len(decided)} states, verdicts {summary['verdict_histogram']}",
              flush=True)
        if hits:
            print("!" * 78)
            print(f"!!! THICKENABLE NEIGHBOUR(S): "
                  f"{[h['canonical'] for h in hits]} !!!")
            print("!" * 78, flush=True)
    return summary


def run_calibration(out_path: str = CALIBRATION_OUT, budget: int = SAMPLE_BUDGET,
                    seeds: int = SAMPLE_SEEDS, per_length_cap: int = 12,
                    min_length: int = 13, max_length: int = 25,
                    min_degree: int = 3, verbose: bool = True) -> dict:
    """Stage 3: the mandatory positive ladder, BOTH instruments, rates BY LENGTH."""
    started = time.time()
    ladder = positive_ladder(min_length=min_length, max_length=max_length,
                             min_degree=min_degree)
    by_length = defaultdict(list)
    for entry in ladder:
        by_length[entry["total_length"]].append(entry)

    rng = random.Random(MASTER_SEED)
    cells = {}
    rows = []
    for length in sorted(by_length):
        pool = by_length[length]
        chosen = (pool if len(pool) <= per_length_cap
                  else sorted(rng.sample(range(len(pool)), per_length_cap)))
        if chosen is not pool:
            chosen = [pool[i] for i in chosen]
        a_hits = 0
        a_fail_closed = 0
        a_fail_reasons = []
        b_hits = 0
        b_best = []
        for entry in chosen:
            pair = tuple(entry["pair"])
            decision = exact_decision(pair, cross_check=False)
            sample = sampled_upper(pair, budget=budget, seeds=seeds)
            if decision["verdict"] == SPHERICAL:
                a_hits += 1
            elif decision["verdict"] != NOT_SPHERICAL:
                a_fail_closed += 1
                a_fail_reasons.append(decision["reason"])
            if sample["best_defect"] == 0:
                b_hits += 1
            b_best.append(sample["best_defect"])
            rows.append({"pair": entry["pair"], "total_length": length,
                         "min_degree": entry["min_degree"],
                         "census_family_size": entry["census_family_size"],
                         "source": entry["source"],
                         "instrument_A_verdict": decision["verdict"],
                         "instrument_A_method": decision["method"],
                         "instrument_B_best_defect": sample["best_defect"],
                         "instrument_B_per_seed": sample["per_seed_best_defect"]})
            if decision["verdict"] == NOT_SPHERICAL:
                raise SweepContradiction(
                    f"instrument A returned NOT_SPHERICAL on a state certified "
                    f"gamma_N = 0: {pair} (source {entry['source']})")
        cells[str(length)] = {
            "ladder_states_available": len(pool),
            "states_measured": len(chosen),
            "min_degree_range": [min(e["min_degree"] for e in chosen),
                                 max(e["min_degree"] for e in chosen)],
            "sources": dict(sorted(Counter(e["source"] for e in chosen).items())),
            "instrument_A_detection_rate": round(a_hits / len(chosen), 4),
            "instrument_A_hits": a_hits,
            "instrument_A_fail_closed": a_fail_closed,
            "instrument_A_fail_closed_reasons": a_fail_reasons[:4],
            "instrument_B_detection_rate": round(b_hits / len(chosen), 4),
            "instrument_B_hits": b_hits,
            "instrument_B_best_defects": b_best,
        }
        if verbose:
            print(f"  [calib] L{length}: A {a_hits}/{len(chosen)}  "
                  f"B {b_hits}/{len(chosen)}  ({time.time() - started:.0f}s)",
                  flush=True)

    measured = sorted(int(k) for k in cells)
    b_blind_from = None
    for length in measured:
        if cells[str(length)]["instrument_B_detection_rate"] == 0.0:
            b_blind_from = length
            break
    uncovered = [L for L in range(min_length, max_length + 1) if L not in measured]

    doc = {
        "record": "u124_calibration",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": ("MACHINERY measurement: detection rate BY LENGTH of the two "
                   "instruments used by the u124 sweep, on states independently known "
                   "to have gamma_N = 0.  No statement about any AC class."),
        "units": "defects are UNHALVED; gamma_N = defect // 2",
        "budgets": {"sample_budget_per_seed": budget, "sample_seeds": seeds,
                    "per_length_cap": per_length_cap, "master_seed": MASTER_SEED,
                    "min_degree_filter": min_degree,
                    "scheme_budget": SCHEME_BUDGET, "branch_budget": BRANCH_BUDGET},
        "ladder_sources": ["results/stable_ac/fable/ak2_members.jsonl (verdict "
                           "SPHERICAL)",
                           "results/stable_ac/fable/witness_sensitivity.json "
                           "(census-certified rungs)"],
        "ladder_size": len(ladder),
        "cells_by_total_length": cells,
        "lengths_measured": measured,
        "lengths_with_no_positive_control": uncovered,
        "instrument_A": {
            "kind": "exact decision procedure (R1c-v2 + exact census fallback)",
            "one_sided": False,
            "reading": ("A NOT_SPHERICAL carrying exhaustive = true is a certified "
                        "negative, not a null: the whole product schemes x phases x "
                        "seeds x cross-cycle combinations was enumerated, or the "
                        "support was certified non-planar.  Its detection rate on the "
                        "ladder is reported so the certificate is checked empirically "
                        "as well as read off the code."),
        },
        "instrument_B": {
            "kind": "one-sided sampled hill-climb (upper bound on gamma_N only)",
            "one_sided": True,
            "blind_from_length": b_blind_from,
            "reading": ("Above the first length with detection rate 0 the instrument is "
                        "blind: a sampled bound there is worth nothing as evidence of "
                        "non-thickenability and the corresponding gamma_N_upper values "
                        "are UNINFORMATIVE as measurements of distance."),
        },
        "selection_bias": (
            "Both ladder sources are biased toward detectable states, which pushes "
            "measured rates UP.  A low cell is conclusive (the instrument is blind); a "
            "high cell is optimistic and never licenses reading a null as absence."),
        "composition_mismatch": (
            "Every one of the 124 targets has min generator degree >= 6; the ladder's "
            "thickenable states are much sparser in one generator (see min_degree_range "
            "per cell).  A sparse state has a smaller compatible family in that "
            "direction and is therefore EASIER for instrument B than a target of the "
            "same total length.  This bias also points UP: the measured rates bound the "
            "instrument's sensitivity on the actual targets from ABOVE."),
        "rows": rows,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    _write_json(out_path, doc)
    if verbose:
        print(f"[calib] {len(rows)} ladder states over lengths {measured}; "
              f"instrument B blind from length {b_blind_from}; "
              f"no positive control at lengths {uncovered}", flush=True)
    return doc


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stage", default="sweep",
                        choices=("sweep", "neighbourhood", "calibration"))
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--sweep-out", default=SWEEP_OUT)
    parser.add_argument("--sweep-summary", default=SWEEP_SUMMARY)
    parser.add_argument("--neighbour-out", default=NEIGHBOUR_OUT)
    parser.add_argument("--neighbour-summary", default=NEIGHBOUR_SUMMARY)
    parser.add_argument("--calibration-out", default=CALIBRATION_OUT)
    parser.add_argument("--census-cap", type=int, default=CENSUS_CAP)
    parser.add_argument("--samples", type=int, default=SAMPLE_BUDGET)
    parser.add_argument("--seeds", type=int, default=SAMPLE_SEEDS)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--top-n", type=int, default=NEIGHBOUR_TOP_N)
    parser.add_argument("--harvest-pops", type=int, default=NEIGHBOUR_HARVEST_POPS)
    parser.add_argument("--state-cap", type=int, default=NEIGHBOUR_STATE_CAP)
    parser.add_argument("--depth1-top-only", action="store_true")
    parser.add_argument("--per-length-cap", type=int, default=12)
    parser.add_argument("--min-degree", type=int, default=3)
    args = parser.parse_args(argv)

    if args.stage == "sweep":
        run_sweep(args.csv, args.sweep_out, args.sweep_summary,
                  census_cap=args.census_cap, budget=args.samples, seeds=args.seeds,
                  limit=args.limit, calibration_path=args.calibration_out)
    elif args.stage == "neighbourhood":
        run_neighbourhood(args.sweep_out, args.neighbour_out, args.neighbour_summary,
                          top_n=args.top_n, harvest_pops=args.harvest_pops,
                          state_cap=args.state_cap,
                          depth1_all=not args.depth1_top_only)
    else:
        run_calibration(args.calibration_out, budget=args.samples, seeds=args.seeds,
                        per_length_cap=args.per_length_cap,
                        min_degree=args.min_degree)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
