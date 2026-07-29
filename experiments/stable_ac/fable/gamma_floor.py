"""gamma_N *floor* measurement: how close does a class get to thickenable?

Every decision so far has been binary -- ``SPHERICAL`` (gamma_N = 0) or not.  That
throws away the interesting number.  By the graft-calculus ceiling
(``R3PRIME_GRAFT_CALCULUS.md`` Theorem G6, AUDITED) a single non-cancelling AC2 graft
lowers gamma_N by at most 1, so a class whose members all sit at gamma_N >= 2 cannot
reach a thickenable member in one move from anywhere yet explored: the gamma_N = 1
states are the *gateway* every successful search must pass through.

This module measures, on a stratified sample of an already-harvested class, the exact
gamma_N of each member via the census (``neuwirth_rank_n.gamma_N_factorial_n``,
minimum_defect = 2 * gamma_N -- the UNHALVED convention), and reports the floor and the
full histogram per class and per total length.

Scope and honesty
-----------------
* Census-only: a member is measured iff its compatible family fits the per-member cap.
  Coverage is reported per length stratum; unmeasured members are counted, never
  guessed.  A floor reported here is a floor OVER THE MEASURED SAMPLE, which is an
  upper bound for the class floor (the class may contain lower members elsewhere).
* No search of any kind is run: the inputs are the committed harvest artifacts.
* Claims addressed: MACHINERY / measurement.  Nothing here is an AC-triviality claim
  about AK(3) in either direction.

Inputs (committed artifacts):
  results/stable_ac/fable/ak3_matched_members.jsonl.gz  -- AK(3) classical class
  results/stable_ac/fable/ak2_members.jsonl             -- AK(2) classical class
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import neuwirth_rank_n as RN                                    # noqa: E402
from disconnected_split import support_class_and_E              # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
AK3_MEMBERS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "ak3_matched_members.jsonl.gz")
AK2_MEMBERS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "ak2_members.jsonl")
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "gamma_floor_measurement.json")

CENSUS_CAP = 400_000          # per-member compatible-family cap
SAMPLE_PER_STRATUM = 260      # members sampled per (class, total length) stratum
SEED = 20260729


def _open_rows(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, encoding="utf-8")


def _pair_of(row) -> tuple | None:
    """The rank-2 pair a harvest row describes, or None if the row has no pair."""
    for field in ("canonical", "pair", "key"):
        value = row.get(field)
        if isinstance(value, list) and len(value) == 2 and all(isinstance(w, str)
                                                              for w in value):
            return tuple(value)
    return None


def census_size(pair) -> int:
    degrees = Counter("".join(pair).lower())
    size = 1
    for deg in degrees.values():
        size *= math.factorial(deg - 1)
    return size


def load_class(path: str) -> list:
    pairs = []
    with _open_rows(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            pair = _pair_of(row)
            if pair is None:
                continue
            pairs.append((pair, row.get("verdict")))
    return pairs


def stratified_sample(pairs, per_stratum: int = SAMPLE_PER_STRATUM, seed: int = SEED):
    """Group by total length, sample within each stratum, report the strata sizes."""
    strata = defaultdict(list)
    for pair, verdict in pairs:
        strata[sum(len(w) for w in pair)].append((pair, verdict))
    rng = random.Random(seed)
    sampled = {}
    for length, members in sorted(strata.items()):
        take = min(per_stratum, len(members))
        sampled[length] = (len(members), rng.sample(members, take))
    return sampled


def measure_class(name: str, path: str, census_cap: int = CENSUS_CAP,
                  per_stratum: int = SAMPLE_PER_STRATUM,
                  progress_every: int = 200) -> dict:
    t0 = time.time()
    pairs = load_class(path)
    sampled = stratified_sample(pairs, per_stratum)
    print(f"[{name}] {len(pairs)} rows, {len(sampled)} length strata", flush=True)

    gamma_hist: Counter = Counter()
    per_length: dict = {}
    measured = skipped = 0
    floor = None
    floor_witnesses: list = []
    verdict_cross_check = {"agree": 0, "disagree": []}
    done = 0

    for length, (stratum_size, members) in sorted(sampled.items()):
        length_hist: Counter = Counter()
        length_measured = length_skipped = 0
        for pair, verdict in members:
            size = census_size(pair)
            if size > census_cap:
                skipped += 1
                length_skipped += 1
                continue
            census = RN.gamma_N_factorial_n(pair, ("x", "y"), cap_rotations=census_cap,
                                            keep_accepting=False)
            done += 1
            if census["status"] != "OK":
                skipped += 1
                length_skipped += 1
                continue
            gamma = census["minimum_defect"] // 2       # UNHALVED -> gamma_N
            gamma_hist[gamma] += 1
            length_hist[gamma] += 1
            measured += 1
            length_measured += 1
            # cross-check the recorded harvest verdict against the census
            if verdict in ("SPHERICAL", "NOT_SPHERICAL"):
                census_says = "SPHERICAL" if gamma == 0 else "NOT_SPHERICAL"
                if census_says == verdict:
                    verdict_cross_check["agree"] += 1
                else:
                    verdict_cross_check["disagree"].append(
                        {"pair": list(pair), "recorded": verdict,
                         "census_gamma": gamma})
            if floor is None or gamma < floor:
                floor = gamma
                floor_witnesses = []
            if gamma == floor and len(floor_witnesses) < 12:
                cls, e = support_class_and_E(pair)
                floor_witnesses.append({"pair": list(pair), "gamma_N": gamma,
                                        "total_length": length, "support": cls,
                                        "E": float(e) if e is not None else None,
                                        "census_size": size})
            if done % progress_every == 0:
                print(f"[{name}]   measured {measured} (floor so far "
                      f"gamma_N={floor}) ...", flush=True)
        per_length[length] = {
            "stratum_size": stratum_size,
            "sampled": len(members),
            "measured": length_measured,
            "skipped_over_cap": length_skipped,
            "gamma_histogram": {str(k): v for k, v in sorted(length_hist.items())},
            "floor": min(length_hist) if length_hist else None,
        }

    return {
        "class": name,
        "source": os.path.relpath(path, REPO_ROOT),
        "rows_total": len(pairs),
        "census_cap": census_cap,
        "sample_per_stratum": per_stratum,
        "seed": SEED,
        "measured": measured,
        "skipped_over_cap": skipped,
        "gamma_floor_over_sample": floor,
        "gamma_histogram": {str(k): v for k, v in sorted(gamma_hist.items())},
        "floor_witnesses": floor_witnesses,
        "per_length": {str(k): v for k, v in sorted(per_length.items())},
        "verdict_cross_check": verdict_cross_check,
        "elapsed_seconds": round(time.time() - t0, 1),
    }


def run(out_path: str = DEFAULT_OUT, census_cap: int = CENSUS_CAP,
        per_stratum: int = SAMPLE_PER_STRATUM) -> dict:
    report = {
        "record": "gamma_floor_measurement",
        "theorem_context": ("R3PRIME_GRAFT_CALCULUS.md Theorem G6 (AUDITED): a "
                            "non-cancelling AC2 graft lowers gamma_N by at most 1, so "
                            "gamma_N = 1 members are the gateway to thickenability."),
        "units": "minimum_defect = 2 * gamma_N (unhalved); reported values are gamma_N",
        "classes": {},
    }
    for name, path in (("AK(3) classical class", AK3_MEMBERS),
                       ("AK(2) classical class", AK2_MEMBERS)):
        report["classes"][name] = measure_class(name, path, census_cap, per_stratum)
    ak3 = report["classes"]["AK(3) classical class"]
    ak2 = report["classes"]["AK(2) classical class"]
    report["contrast"] = {
        "ak3_floor": ak3["gamma_floor_over_sample"],
        "ak2_floor": ak2["gamma_floor_over_sample"],
        "ak3_histogram": ak3["gamma_histogram"],
        "ak2_histogram": ak2["gamma_histogram"],
        "reading": ("floors are over the MEASURED SAMPLE only (upper bounds for the "
                    "true class floors); unmeasured members are counted per stratum"),
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1, sort_keys=False)
    print(f"[floor] wrote {out_path}", flush=True)
    print(f"[floor] AK(3) floor {ak3['gamma_floor_over_sample']} "
          f"hist {ak3['gamma_histogram']}", flush=True)
    print(f"[floor] AK(2) floor {ak2['gamma_floor_over_sample']} "
          f"hist {ak2['gamma_histogram']}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--census-cap", type=int, default=CENSUS_CAP)
    parser.add_argument("--per-stratum", type=int, default=SAMPLE_PER_STRATUM)
    args = parser.parse_args(argv)
    run(args.out, args.census_cap, args.per_stratum)


if __name__ == "__main__":
    main()
