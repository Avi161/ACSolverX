"""W3b phase 2: certified planarity dispatch over the AK(3) mu-ladder orbits.

Input: checkers/out/ak3_orbits_r20_b32_c24.jsonl (1,508 orbit rows with
provenance, regenerated bit-identically to the committed summary). Each
orbit pair is stably AC-equivalent to AK(3) (gated CoV ladder). For every
orbit we decide its 8 signed-permutation relabels (the greedy/Neuwirth
machinery reads strings, not orbits; full Aut-orbit coverage is NOT
achieved and is stated as a gap), through the PROVEN solver ladder of the
two-hop certificate: K4/K4-e/C4 -> P4 -> one-loop -> paw one-loop.

Verdicts per state: NOT_SPHERICAL (certificate), UNSUPPORTED (headline
count, never guessed), SPHERICAL_REQUIRES_REGINA (tripwire: quarantined as
a suspected bug per NEUWIRTH_FEASIBILITY doctrine — Pipeline B does not
exist; a validated positive would prove AK(3) STABLY AC-trivial).

Sliced and resumable: results append to out/ak3_orbit_thick_results.jsonl
keyed by (orbit_index, relabel_index); reruns skip done keys.

Usage: ak3_orbit_thickenability.py START END
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.stable_ac.thickenable.two_hop_cov_thickenability_certificate import (  # noqa: E501
    _dispatch,
)

HERE = Path(__file__).resolve().parent
ORBITS = HERE / "out" / "ak3_orbits_r20_b32_c24.jsonl"
RESULTS = HERE / "out" / "ak3_orbit_thick_results.jsonl"

SWAP = str.maketrans("xyXY", "yxYX")
INV_X = str.maketrans("xX", "Xx")
INV_Y = str.maketrans("yY", "Yy")


def relabels(pair):
    out = []
    for swap in (False, True):
        for ix in (False, True):
            for iy in (False, True):
                r1, r2 = pair
                if swap:
                    r1, r2 = r1.translate(SWAP), r2.translate(SWAP)
                if ix:
                    r1, r2 = r1.translate(INV_X), r2.translate(INV_X)
                if iy:
                    r1, r2 = r1.translate(INV_Y), r2.translate(INV_Y)
                out.append((r1, r2))
    return out


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    orbits = [json.loads(line) for line in ORBITS.read_text().splitlines()]
    done = set()
    cache = {}
    if RESULTS.exists():
        for line in RESULTS.read_text().splitlines():
            rec = json.loads(line)
            done.add((rec["orbit"], rec["relabel"]))
            cache[tuple(rec["pair"])] = rec["verdict"]
    counts = {"NOT_SPHERICAL": 0, "UNSUPPORTED": 0,
              "SPHERICAL_REQUIRES_REGINA": 0, "cached": 0, "skipped": 0}
    with RESULTS.open("a") as f:
        for idx in range(start, min(end, len(orbits))):
            pair = tuple(orbits[idx]["pair"])
            for rl_idx, rl_pair in enumerate(relabels(pair)):
                if (idx, rl_idx) in done:
                    counts["skipped"] += 1
                    continue
                if rl_pair in cache:
                    verdict = cache[rl_pair]
                    counts["cached"] += 1
                else:
                    decision = _dispatch(rl_pair)
                    if decision.spherical is None:
                        verdict = "UNSUPPORTED"
                    elif decision.spherical:
                        verdict = "SPHERICAL_REQUIRES_REGINA"
                    else:
                        verdict = "NOT_SPHERICAL"
                    cache[rl_pair] = verdict
                counts[verdict] = counts.get(verdict, 0) + 1
                f.write(json.dumps({
                    "orbit": idx, "relabel": rl_idx,
                    "pair": list(rl_pair), "mu": orbits[idx]["mu"],
                    "verdict": verdict}) + "\n")
                f.flush()
                if verdict == "SPHERICAL_REQUIRES_REGINA":
                    print(json.dumps({"TRIPWIRE": {
                        "orbit": idx, "relabel": rl_idx,
                        "pair": list(rl_pair)}}))
                    print("SPHERICAL verdict: quarantined as SUSPECTED BUG "
                          "pending independent rotation replay + Regina "
                          "(Pipeline B absent). Not a result claim.")
    print(json.dumps({"slice": [start, end], "counts": counts}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
