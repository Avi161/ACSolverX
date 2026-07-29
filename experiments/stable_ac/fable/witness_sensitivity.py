"""Sensitivity of the R7 defect-0 witness hunt, calibrated on a known-gamma-0 ladder.

R7 (``spike_space_hunt``) hunts for a defect-0 compatible rotation system among
unreduced spellings in AK(3)'s class at total lengths 13-24, at a production budget of
40,000 hill-climb evaluations per state (``gateway_scan.sampled_min_defect``).  The
hunt is one-sided: a verified witness proves the exact complex is orientably
thickenable (gamma_N = 0), while finding none proves NOTHING.  But "proves nothing"
has two operationally different readings, and this module measures which one applies
at each total length:

* merely *uninformative* -- the instrument does recover defect 0 on comparable states
  at that length with useful probability, so silence at least means no easy witness
  was present;
* outright *vacuous* -- the instrument recovers defect 0 on KNOWN thickenable states
  at that length with probability ~0, so silence is what it emits regardless of the
  truth.

Method.  A LADDER of states with gamma_N = 0 is built at increasing total length,
starting from the census-confirmed fixture ``("xyXY", "xxy")`` (12 compatible rotation
systems, 2 of defect 0) and grown by spikes (insert ``c c^-1`` into a relator: exactly
the move R7's spike space is made of, total length +2) plus one AC2 graft image to
seed the even parity.  Each rung is certified gamma_N = 0 by

* an EXACT CENSUS (``neuwirth_rank_n.gamma_N_factorial_n``) while the compatible
  family ``prod_g (deg(g) - 1)!`` fits the cap, and
* a VERIFIED defect-0 witness (``gateway_scan.verify_witness``) always.

A verified witness is a complete proof of gamma_N = 0 at any length, so the ladder
stays rigorous past the census horizon; the artifact records which certification each
rung carries.  The production budgets are then replayed on every rung with independent
seeds, and the DETECTION RATE (fraction of runs that recover and re-verify a defect-0
witness) is tabulated by (total length, samples).

Bound directions (record which SIDE every tool bounds from -- the trap of
``experiments/lessons/parallel-runs-and-bound-direction.md``):

* ``sampled_min_defect`` bounds gamma_N from ABOVE, always.  It can certify
  ``gamma_N <= d``; it can never certify ``gamma_N >= 1``, and a failed run says
  nothing about the state it ran on.
* the detection rates measured here bound the instrument's sensitivity from ABOVE:
  every rung is, by construction, a state that a <= 2,000,000-evaluation climb could
  certify, so an arbitrary gamma_N = 0 state at the same length can only be harder to
  detect.  A low cell is therefore conclusive about insensitivity; a high cell is
  optimistic.

Claims addressed: MACHINERY only -- the sensitivity of one instrument on one
calibration ladder.  Nothing here is a statement about AK(3), about its class, or
about the AC / stable AC conjecture in either direction, and the absence of a witness
never proves gamma_N > 0.

This is bounded enumeration plus local search over ROTATION SYSTEMS of fixed
complexes; it is not an AC search and consumes no search node budget.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import gateway_scan as GS                                        # noqa: E402
import neuwirth_rank_n as RN                                     # noqa: E402
from gamma_floor import census_size as predicted_census_size     # noqa: E402
from spike_space_hunt import graft_images                        # noqa: E402
from spike_witness import single_spikes, spelling_key            # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "witness_sensitivity.json")

FIXTURE = ("xyXY", "xxy")            # gamma_N = 0 by exact census: 2 / 12 systems

PRODUCTION_SAMPLES = (10_000, 40_000, 200_000)
SEEDS_PER_CELL = 10
PROBE_TIERS = (6_000, 60_000, 600_000, 2_000_000)
TIER_POOL = {0: 48, 1: 10, 2: 3, 3: 2}   # children probed per escalation tier
CENSUS_CAP = 4_000_000                   # exact-census rung confirmation ceiling
MEASURE_FROM = 11
MAX_LENGTH = 24
MASTER_SEED = 20260729
DEADLINE_SECONDS = 1500.0

BOUND_DIRECTION = (
    "sampled_min_defect bounds gamma_N from ABOVE, always: a verified witness "
    "certifies gamma_N <= defect/2, and a run that finds no witness certifies "
    "nothing.  The detection rates in this artifact bound the instrument's "
    "sensitivity from ABOVE: rungs are states a <= 2,000,000-evaluation climb could "
    "certify, so arbitrary gamma_N = 0 states at the same length can only be harder."
)
NULL_READING = (
    "Absence of a witness never proves gamma_N > 0.  A near-zero cell at (length, "
    "samples) means an R7 null at that budget and length is VACUOUS -- it is what the "
    "instrument emits on known thickenable states too.  A high cell never converts an "
    "R7 null into evidence of non-thickenability; it only makes the null "
    "uninformative rather than vacuous."
)
SELECTION_BIAS = (
    "Rung selection is biased toward detectable states twice over: a rung enters the "
    "ladder only if some probe tier certified it, and the first certified child in a "
    "shuffled enumeration is kept.  Both biases push measured rates UP, never down."
)


# --------------------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------------------


def degree_profile(words) -> dict:
    """Occurrences of each generator (case-folded) -- the census cost driver."""
    return dict(Counter("".join(words).lower()))


def spike_children(words) -> list:
    """Every distinct single-spike image of ``words`` (total length + 2)."""
    return [tuple(s["words"]) for s in single_spikes(tuple(words))]


def witness_probe(words, budget: int, rng: random.Random):
    """``(best defect, verified defect-0 orders or None, anomaly or None)``.

    A defect-0 report from the sampler counts only after ``verify_witness``
    independently recomputes 0; a mismatch is returned as an anomaly, never as a hit.
    """
    words = tuple(words)
    best, orders = GS.sampled_min_defect(words, budget, rng)
    if best is None or best > 0:
        return best, None, None
    if best < 0:
        return best, None, {"kind": "NEGATIVE_DEFECT", "words": list(words),
                            "sampler_defect": best}
    checked = GS.verify_witness(words, orders)
    if checked != 0:
        return best, None, {"kind": "VERIFIER_MISMATCH", "words": list(words),
                            "sampler_defect": best, "verified_defect": checked}
    return 0, orders, None


def census_confirm(words, census_cap: int, deadline: float):
    """Exact-census record for ``words`` if affordable, else ``None``.

    Raises on a gamma-0 contradiction: callers only invoke this on states holding a
    verified defect-0 witness, so a census minimum above 0 would mean one of the two
    independent tools is broken -- that must halt the run, not be absorbed.
    """
    predicted = predicted_census_size(tuple(words))
    if predicted > census_cap:
        return None
    if time.time() + predicted * 2e-5 >= deadline:
        return None
    census = RN.gamma_N_factorial_n(tuple(words), cap_rotations=census_cap,
                                    keep_accepting=False)
    if census["status"] != "OK":
        return None
    if census["minimum_defect"] != 0:
        raise RuntimeError(
            f"census/witness CONTRADICTION on {words}: verified defect-0 witness "
            f"exists but census minimum defect is {census['minimum_defect']}"
        )
    zero = census["defect_histogram"].get(0, 0)
    family = census["enumerated_cases"]
    return {"family": family, "zero_systems": zero,
            "zero_density": zero / family if family else None}


def make_rung(words, orders, found_at_probe_evals, chain: str, parent,
              census_cap: int, deadline: float) -> dict:
    """Assemble one certified ladder rung (witness always, census when affordable)."""
    words = tuple(words)
    census = census_confirm(words, census_cap, deadline)
    return {
        "chain": chain,
        "total_length": sum(len(w) for w in words),
        "words": list(words),
        "parent": list(parent) if parent is not None else None,
        "degrees": degree_profile(words),
        "predicted_family": predicted_census_size(words),
        "certified_by": "census+witness" if census is not None else "witness",
        "census": census,
        "witness_verified_defect": 0,
        "witness_orders": {str(k): [int(d) for d in v] for k, v in orders.items()},
        "found_at_probe_evals": found_at_probe_evals,
    }


# --------------------------------------------------------------------------------------
# ladder construction
# --------------------------------------------------------------------------------------


def select_even_seed(master_seed: int, census_cap: int, deadline: float):
    """A census-certified gamma-0 AC2 graft image of the fixture at total length 10.

    Spikes change total length by exactly 2, so the fixture (length 7) reaches only
    odd lengths; a graft whose guest has length 3 seeds the even parity.  Every image
    is decided by EXACT census here (families are tiny at length 10), and one gamma-0
    image is chosen at random among all of them.
    """
    images = [img for img in graft_images(FIXTURE)
              if sum(len(w) for w in img) == 10]
    zeros = []
    for img in images:
        census = RN.gamma_N_factorial_n(tuple(img), cap_rotations=census_cap,
                                        keep_accepting=False)
        if census["status"] == "OK" and census["minimum_defect"] == 0:
            zeros.append(tuple(img))
    scan = {"length10_images": len(images), "gamma0_images": len(zeros)}
    if not zeros:
        return None, scan
    rng = random.Random(f"{master_seed}|even-seed")
    choice = rng.choice(sorted(zeros))
    best, orders, anomaly = witness_probe(choice, 20_000,
                                          random.Random(f"{master_seed}|even-witness"))
    if anomaly is not None or best != 0:
        # census says gamma 0; a modest climb failing to re-find it on a 720-strong
        # family would itself be an instrument bug worth halting on
        raise RuntimeError(f"even seed {choice}: census gamma 0 but probe best={best}, "
                           f"anomaly={anomaly}")
    rung = make_rung(choice, orders, 20_000, "even", FIXTURE, census_cap, deadline)
    rung["move"] = "AC2 graft (guest length 3)"
    return rung, scan


def grow_chain(tip_words, target_length: int, master_seed: int, deadline: float,
               probe_tiers=PROBE_TIERS, census_cap: int = CENSUS_CAP,
               tier_pool=None, anomalies=None):
    """One spike rung: ``(rung, None)`` on success, ``(None, stall record)`` otherwise.

    Children are probed in a seeded shuffled order through escalating budgets; higher
    tiers retry only the children whose best sampled defect so far is lowest.  A stall
    proves NOTHING about the children (they may include gamma-0 states the climb
    missed); it is recorded as an instrument limit, and the ladder simply ends.
    """
    tip_words = tuple(tip_words)
    if tier_pool is None:
        tier_pool = TIER_POOL
    children = spike_children(tip_words)
    rng = random.Random(f"{master_seed}|shuffle|{target_length}|"
                        f"{'&'.join(spelling_key(tip_words))}")
    rng.shuffle(children)
    best_by_child: dict = {}
    tiers_completed = 0
    for tier_idx, budget in enumerate(probe_tiers):
        if tier_idx == 0:
            pool = children[:tier_pool.get(0, len(children))]
        else:
            ranked = sorted(best_by_child, key=lambda c: (best_by_child[c], c))
            pool = ranked[:tier_pool.get(tier_idx, 2)]
        for child in pool:
            if time.time() >= deadline:
                return None, {"target_length": target_length,
                              "chain_tip": list(tip_words),
                              "reason": "deadline",
                              "children_enumerated": len(children),
                              "tiers_completed": tiers_completed,
                              "best_defect_seen": (min(best_by_child.values())
                                                   if best_by_child else None)}
            prng = random.Random(f"{master_seed}|grow|{budget}|{'&'.join(child)}")
            best, orders, anomaly = witness_probe(child, budget, prng)
            if anomaly is not None:
                if anomalies is not None:
                    anomalies.append(anomaly)
                continue
            if best == 0:
                rung = make_rung(child, orders, budget, None, tip_words,
                                 census_cap, deadline)
                rung["move"] = "spike"
                return rung, None
            cur = best_by_child.get(child)
            if cur is None or best < cur:
                best_by_child[child] = best
        tiers_completed += 1
    return None, {"target_length": target_length,
                  "chain_tip": list(tip_words),
                  "reason": "no child certified at any probe tier",
                  "children_enumerated": len(children),
                  "tiers_completed": tiers_completed,
                  "probe_tiers": list(probe_tiers),
                  "best_defect_seen": (min(best_by_child.values())
                                       if best_by_child else None),
                  "reading": ("proves nothing about the children's gamma_N -- the "
                              "instrument, not the states, is what failed here")}


# --------------------------------------------------------------------------------------
# detection-rate measurement
# --------------------------------------------------------------------------------------


def measure_rung(words, total_length: int, master_seed: int,
                 seeds_per_cell: int = SEEDS_PER_CELL,
                 production_samples=PRODUCTION_SAMPLES,
                 deadline: float = float("inf"), certified_by: str = "?",
                 anomalies=None, flush=None) -> dict:
    """Detection rate of each production budget on one certified gamma-0 rung."""
    words = tuple(words)
    record = {"words": list(words), "total_length": total_length,
              "certified_by": certified_by, "cells": {}}
    for samples in production_samples:
        hits = 0
        runs = 0
        best_defects = []
        seconds = []
        complete = True
        for k in range(seeds_per_cell):
            if time.time() >= deadline:
                complete = False
                break
            rng = random.Random(f"{master_seed}|measure|{total_length}|{samples}|{k}")
            t0 = time.time()
            best, orders, anomaly = witness_probe(words, samples, rng)
            seconds.append(round(time.time() - t0, 3))
            runs += 1
            best_defects.append(best)
            if anomaly is not None:
                if anomalies is not None:
                    anomalies.append(anomaly)
                continue
            if best == 0:
                hits += 1        # witness_probe returns 0 only after verify_witness
        record["cells"][str(samples)] = {
            "samples": samples,
            "runs": runs,
            "hits": hits,
            "rate": (hits / runs) if runs else None,
            "run_best_defects": best_defects,
            "mean_seconds": round(sum(seconds) / len(seconds), 3) if seconds else None,
            "complete": complete,
        }
        if flush is not None:
            flush()
        if not complete:
            break
    return record


# --------------------------------------------------------------------------------------
# summary
# --------------------------------------------------------------------------------------


def _rate_at(entry, samples: int):
    cell = entry.get("cells", {}).get(str(samples))
    if cell is None:
        return None
    return cell.get("rate")


def summarize(detection: dict, stalls, production_samples, max_length: int,
              ladder=()) -> dict:
    """Detection table plus the 40k adequacy crossings and the L=24 recommendation."""
    lengths = sorted(int(k) for k in detection)
    table = []
    for L in lengths:
        entry = detection[str(L)]
        table.append({
            "total_length": L,
            "certified_by": entry.get("certified_by"),
            "predicted_family": next((r.get("predicted_family") for r in ladder
                                      if r.get("total_length") == L), None),
            "rates": {str(s): _rate_at(entry, s) for s in production_samples},
        })

    mid = 40_000 if 40_000 in tuple(production_samples) else production_samples[
        len(production_samples) // 2]
    below_half = [L for L in lengths
                  if _rate_at(detection[str(L)], mid) is not None
                  and _rate_at(detection[str(L)], mid) < 0.5]
    first_below_half = min(below_half) if below_half else None
    zero_lengths = [L for L in lengths
                    if _rate_at(detection[str(L)], mid) == 0.0]
    first_zero = None
    for L in sorted(zero_lengths):
        tail = [x for x in lengths if x >= L]
        if all(_rate_at(detection[str(x)], mid) == 0.0 for x in tail
               if _rate_at(detection[str(x)], mid) is not None):
            first_zero = L
            break

    return {
        "reference_samples": mid,
        "table": table,
        "first_length_below_half_at_40k": first_below_half,
        "first_length_zero_at_40k": first_zero,
        "stalled_chains": list(stalls),
        "recommendation_at_max_length": _recommendation(
            detection, stalls, production_samples, max_length, ladder),
    }


def _recommendation(detection, stalls, production_samples, max_length: int,
                    ladder=()) -> dict:
    """A data-driven budget recommendation for R7 at ``max_length``."""
    entry = detection.get(str(max_length))
    if entry is None:
        stalled = [s for s in stalls if s.get("target_length", 0) <= max_length]
        return {
            "length": max_length,
            "status": "NO_CALIBRATION_STATE",
            "detail": (f"no gamma_N = 0 rung could be certified at length "
                       f"{max_length} (see stalled_chains); sensitivity there is "
                       f"UNMEASURED.  Even the top probe tier failed on every "
                       f"candidate, so R7 nulls at this length carry no information "
                       f"at any production budget"),
            "stalls": stalled,
        }
    rates = [(s, _rate_at(entry, s)) for s in sorted(production_samples)]
    adequate = [(s, r) for s, r in rates if r is not None and r >= 0.9]
    if adequate:
        s, r = adequate[0]
        return {"length": max_length, "status": "MEASURED",
                "recommended_samples": s,
                "detail": (f"{s} samples detected the known gamma-0 state at length "
                           f"{max_length} in {r:.0%} of runs on this ladder; remember "
                           f"the rate is an optimistic (upper) sensitivity estimate")}
    positive = [(s, r) for s, r in rates if r]
    if positive:
        s, r = max(positive)
        runs_needed = math.ceil(math.log(0.05) / math.log(1.0 - r)) if r < 1 else 1
        budget = s * runs_needed
        return {"length": max_length, "status": "MEASURED",
                "recommended_samples": budget,
                "detail": (f"best measured rate at length {max_length} was {r:.0%} at "
                           f"{s} samples; ~{budget} evaluations per state are needed "
                           f"for 95% detection of states no harder than this rung -- "
                           f"and the rung is a favourable case (see selection_bias)")}
    rung_tier = next((r.get("found_at_probe_evals") for r in ladder
                      if r.get("total_length") == max_length), None)
    return {"length": max_length, "status": "VACUOUS_AT_ALL_MEASURED_BUDGETS",
            "certifying_tier_evals": rung_tier,
            "detail": (f"every production budget up to {max(production_samples)} "
                       f"scored 0 hits at length {max_length} on a state KNOWN to "
                       f"have gamma_N = 0"
                       + (f"; certifying the rung itself required the "
                          f"{rung_tier}-evaluation tier" if rung_tier else "")
                       + ".  An R7 null at this length is vacuous at these budgets")}


# --------------------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------------------


def _flush(report: dict, out_path: str) -> None:
    report["elapsed_seconds"] = round(time.time() - report["_t0"], 1)
    payload = {k: v for k, v in report.items() if not k.startswith("_")}
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1)
    os.replace(tmp, out_path)


def run(out_path: str = DEFAULT_OUT, master_seed: int = MASTER_SEED,
        seeds_per_cell: int = SEEDS_PER_CELL,
        production_samples=PRODUCTION_SAMPLES, max_length: int = MAX_LENGTH,
        deadline_seconds: float = DEADLINE_SECONDS, probe_tiers=PROBE_TIERS,
        census_cap: int = CENSUS_CAP, measure_from: int = MEASURE_FROM) -> dict:
    t0 = time.time()
    deadline = t0 + deadline_seconds
    production_samples = tuple(sorted(production_samples))
    report = {
        "_t0": t0,
        "record": "witness_sensitivity",
        "claims": ("MACHINERY measurement: detection sensitivity of "
                   "gateway_scan.sampled_min_defect on a known-gamma-0 ladder.  No "
                   "statement about AK(3), its class, or the AC / stable AC "
                   "conjecture is made or implied in either direction."),
        "bound_direction": BOUND_DIRECTION,
        "null_reading": NULL_READING,
        "selection_bias": SELECTION_BIAS,
        "units": "defects are UNHALVED: gamma_N = defect / 2",
        "master_seed": master_seed,
        "seeds_per_cell": seeds_per_cell,
        "production_samples": list(production_samples),
        "probe_tiers": list(probe_tiers),
        "census_cap": census_cap,
        "deadline_seconds": deadline_seconds,
        "fixture": {"words": list(FIXTURE)},
        "even_seed_scan": None,
        "ladder": [],
        "stalls": [],
        "detection": {},
        "anomalies": [],
        "truncated": False,
        "summary": None,
    }
    _flush(report, out_path)
    if time.time() >= deadline:
        report["truncated"] = True
        _flush(report, out_path)
        return report

    # ---- fixture anchor: exact census, then a verified witness -----------------------
    census = RN.gamma_N_factorial_n(FIXTURE, cap_rotations=1_000,
                                    keep_accepting=False)
    if census["status"] != "OK" or census["minimum_defect"] != 0:
        raise RuntimeError(f"fixture census failed: {census['status']}, "
                           f"minimum_defect={census.get('minimum_defect')}")
    best, orders, anomaly = witness_probe(FIXTURE, 2_000,
                                          random.Random(f"{master_seed}|fixture"))
    if best != 0 or anomaly is not None:
        raise RuntimeError(f"fixture witness probe failed: best={best}, "
                           f"anomaly={anomaly}")
    fixture_rung = make_rung(FIXTURE, orders, 2_000, "odd", None, census_cap,
                             deadline)
    fixture_rung["move"] = "root fixture"
    report["fixture"].update(census=fixture_rung["census"],
                             certified_by=fixture_rung["certified_by"])
    report["ladder"].append(fixture_rung)
    print(f"[sens] fixture {FIXTURE}: census {fixture_rung['census']}", flush=True)
    _flush(report, out_path)

    # ---- even-parity seed ------------------------------------------------------------
    even_rung, scan = select_even_seed(master_seed, census_cap, deadline)
    report["even_seed_scan"] = scan
    tips = {}
    dead = set()
    tips["odd"] = (FIXTURE, 7)
    if even_rung is not None:
        report["ladder"].append(even_rung)
        tips["even"] = (tuple(even_rung["words"]), 10)
        print(f"[sens] even seed {tuple(even_rung['words'])} "
              f"census {even_rung['census']}", flush=True)
    else:
        dead.add("even")
        report["stalls"].append({"target_length": 10, "chain_tip": list(FIXTURE),
                                 "reason": "no gamma-0 graft image at length 10",
                                 **scan})
    _flush(report, out_path)

    # ---- grow and measure in ascending length ----------------------------------------
    for L in range(9, max_length + 1):
        chain = "odd" if L % 2 else "even"
        if chain in dead or chain not in tips:
            continue
        tip_words, tip_len = tips[chain]
        if L == tip_len:
            rung = next(r for r in report["ladder"]
                        if r["total_length"] == L and r["chain"] == chain)
        elif L == tip_len + 2:
            t_grow = time.time()
            rung, stall = grow_chain(tip_words, L, master_seed, deadline,
                                     probe_tiers=probe_tiers, census_cap=census_cap,
                                     anomalies=report["anomalies"])
            if rung is None:
                stall["chain"] = chain
                report["stalls"].append(stall)
                dead.add(chain)
                print(f"[sens] L={L} {chain}: STALL ({stall['reason']}); best defect "
                      f"seen {stall.get('best_defect_seen')}", flush=True)
                _flush(report, out_path)
                if time.time() >= deadline:
                    report["truncated"] = True
                    break
                continue
            rung["chain"] = chain
            rung["grow_seconds"] = round(time.time() - t_grow, 1)
            report["ladder"].append(rung)
            tips[chain] = (tuple(rung["words"]), L)
            print(f"[sens] L={L} {chain}: rung {tuple(rung['words'])} "
                  f"[{rung['certified_by']}, tier {rung['found_at_probe_evals']}, "
                  f"family {rung['predicted_family']}]", flush=True)
            _flush(report, out_path)
        else:
            continue
        if L >= measure_from:
            entry = measure_rung(
                tuple(rung["words"]), L, master_seed, seeds_per_cell,
                production_samples, deadline, rung["certified_by"],
                anomalies=report["anomalies"],
                flush=lambda: _flush(report, out_path))
            report["detection"][str(L)] = entry
            rates = {s: c.get("rate") for s, c in entry["cells"].items()}
            print(f"[sens] L={L} detection {rates}", flush=True)
            _flush(report, out_path)
        if time.time() >= deadline:
            report["truncated"] = True
            break

    report["summary"] = summarize(report["detection"], report["stalls"],
                                  production_samples, max_length, report["ladder"])
    _flush(report, out_path)
    print(f"[sens] wrote {out_path}; truncated={report['truncated']}", flush=True)
    print(f"[sens] 40k adequacy: below 50% first at "
          f"{report['summary']['first_length_below_half_at_40k']}, zero first at "
          f"{report['summary']['first_length_zero_at_40k']}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=MASTER_SEED)
    parser.add_argument("--seeds-per-cell", type=int, default=SEEDS_PER_CELL)
    parser.add_argument("--samples", type=int, nargs="+",
                        default=list(PRODUCTION_SAMPLES))
    parser.add_argument("--max-length", type=int, default=MAX_LENGTH)
    parser.add_argument("--deadline-seconds", type=float, default=DEADLINE_SECONDS)
    parser.add_argument("--probe-tiers", type=int, nargs="+",
                        default=list(PROBE_TIERS))
    parser.add_argument("--census-cap", type=int, default=CENSUS_CAP)
    parser.add_argument("--measure-from", type=int, default=MEASURE_FROM)
    args = parser.parse_args(argv)
    run(args.out, args.seed, args.seeds_per_cell, tuple(args.samples),
        args.max_length, args.deadline_seconds, tuple(args.probe_tiers),
        args.census_cap, args.measure_from)


if __name__ == "__main__":
    main()
