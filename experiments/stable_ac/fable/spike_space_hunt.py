"""R7 -- the spike-space witness hunt: look for a THICKENABLE spelling in AK(3)'s class.

Every gamma_N tool in this project so far produces LOWER bounds: the R1c-v2 solver
certifies NOT_SPHERICAL (gamma_N >= 1), exhaustively, on ~141,000 exact complexes.  A
lower bound can only ever produce a negative result.  This module is the mirror image:
it hunts for the one object that would settle the sub-goal outright.

    A compatible rotation system of defect 0, re-verified in isolation by
    gateway_scan.verify_witness, is a COMPLETE POSITIVE certificate that the exact
    word-realized complex is orientably thickenable.

Two properties make that certificate the right instrument here:

* it scales to ANY word length -- unlike the exact census, whose cost is
  prod_v (deg(v)-1)!, and unlike the R1c-v2 solver, which fails closed on the
  loop-bearing complexes that unreduced spellings always carry;
* it is one-sided in the useful direction.  Failure to find a witness is SILENCE and
  is reported as such -- never as evidence of non-thickenability, and never as evidence
  of anything about the conjecture (project Red line 3).

Where it searches, and why there.  gamma_N is a property of the exact word-realized
complex, not of the presentation as a tuple of free-group elements (R1F, machine-checked
by two independent tools).  Every search in this project -- and, as far as the project's
literature review found, every published AC search -- normalises to cyclically reduced
words, so the unreduced part of every AC class has never been entered.  R1F showed that
part is not cosmetic: AK(3)'s reduced spelling has gamma_N = 2, while eight of its 39
distinct single spikes have gamma_N = 1 exactly (exhaustive census, ~3.6-4.8M rotation
systems each, two defect-2 systems apiece).  By the AUDITED graft ceiling
(R3PRIME_GRAFT_CALCULUS Thm G6: one graft lowers gamma_N by at most 1) a thickenable
state is reachable only from a gamma_N = 1 state, so those eight spellings -- and the
gamma_N = 1 gateways of R1G -- are exactly the frontier this hunt starts from.

Claims addressed: the POSITIVE direction (AK(3) AC-trivial, hence stably AC-trivial).
A defect-0 hit is a CANDIDATE, not a claim: it requires (a) independent re-verification
of the rotation system, (b) an explicitly reconstructed AC move list from AK(3) to that
exact spelling, replayed through the pure-Python spec, and (c) confirmation that
Lackenby Thm 1.3 applies to an unreduced spelling.  All three are recorded as blockers
in the report so a hit can never be mistaken for a result.

This is bounded neighbourhood enumeration plus local search over ROTATION SYSTEMS of
fixed complexes.  It is not an AC search and consumes no search node budget.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import gateway_scan as GS                                        # noqa: E402
from ac_words import inverse                                     # noqa: E402
from spike_witness import single_spikes, spelling_key            # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "spike_space_hunt.json")

AK3 = ("xxxYYYY", "xyxYXY")

# the eight gamma_N = 1 spiked spellings of AK(3) (exhaustive census, R1F)
AK3_GATEWAY_SPIKES = (
    ("xyYxxYYYY", "xyxYXY"),
    ("xxYyxYYYY", "xyxYXY"),
    ("xxxYXxYYY", "xyxYXY"),
    ("xxxYxXYYY", "xyxYXY"),
    ("xxxYYYXxY", "xyxYXY"),
    ("xxxYYYxXY", "xyxYXY"),
    ("xxxYYYY", "xxXyxYXY"),
    ("xxxYYYY", "xyXxxYXY"),
)

# the gamma_N = 1 length-13 gateways of AK(3)'s class found in R1G
AK3_REDUCED_GATEWAYS = (
    ("YYXXyx", "YYYxyXX"),
    ("YYXXyx", "YYxyXXX"),
)


def rotations(word: str):
    return [word[i:] + word[:i] for i in range(len(word))]


def graft_images(words, reduce_result: bool = False):
    """Every AC2 graft image in EXACT (unreduced) realization.

    Both host choices, every rotation of host and guest, both signs of the guest.  The
    result is deliberately NOT freely reduced: reduction is a separate AC move whose
    effect on gamma_N is exactly what R1F showed is unpredictable, so the unreduced
    image is a state in its own right and is the one this hunt wants.
    """
    from ac_words import cyclic_reduce
    out = {}
    n = len(words)
    for host in range(n):
        for guest in range(n):
            if host == guest:
                continue
            for hw in rotations(words[host]):
                for gw in rotations(words[guest]):
                    for sign, word in (("+", gw), ("-", inverse(gw))):
                        merged = hw + word
                        if reduce_result:
                            merged = cyclic_reduce(merged)
                        if not merged:
                            continue
                        image = list(words)
                        image[host] = merged
                        image = tuple(image)
                        out.setdefault(spelling_key(image), image)
    return list(out.values())


def hunt(states, samples: int, rng: random.Random, label: str,
         report: dict) -> None:
    """Hill-climb each state for a defect-0 witness; verify every candidate."""
    for n, words in enumerate(states, 1):
        start = time.time()
        best, orders = GS.sampled_min_defect(tuple(words), samples, rng)
        row = {"group": label, "words": list(words),
               "total_length": sum(len(w) for w in words),
               "sampler_defect": best, "seconds": round(time.time() - start, 2)}
        if orders:
            checked = GS.verify_witness(tuple(words), orders)
            row["verified_defect"] = checked
            row["gamma_upper_bound"] = checked // 2
            if checked != best:
                row["ERROR"] = "sampler and verifier disagree"
            if checked == 0:
                row["THICKENABLE_WITNESS"] = {str(k): list(v)
                                              for k, v in orders.items()}
                report["HITS"].append(row)
                print(f"[hunt] *** DEFECT-0 WITNESS *** {tuple(words)}", flush=True)
        else:
            row["gamma_upper_bound"] = None
        report["rows"].append(row)
        best_seen = report["best_bound"].get(label)
        bound = row.get("gamma_upper_bound")
        if bound is not None and (best_seen is None or bound < best_seen):
            report["best_bound"][label] = bound
        if n % 50 == 0 or n == len(states):
            print(f"[hunt] {label}: {n}/{len(states)} best bound "
                  f"{report['best_bound'].get(label)}", flush=True)


def build_groups(double_spikes: bool = True) -> dict:
    """The states to hunt over, each group labelled by how it was reached."""
    groups = {}
    groups["ak3_single_spikes"] = [tuple(s["words"]) for s in single_spikes(AK3)]

    gateway_grafts = {}
    for base in AK3_GATEWAY_SPIKES:
        for image in graft_images(base):
            gateway_grafts.setdefault(spelling_key(image), image)
    groups["gateway_spike_grafts"] = list(gateway_grafts.values())

    reduced_gateway_spikes = {}
    for base in AK3_REDUCED_GATEWAYS:
        for spike in single_spikes(base):
            words = tuple(spike["words"])
            reduced_gateway_spikes.setdefault(spelling_key(words), words)
    groups["reduced_gateway_spikes"] = list(reduced_gateway_spikes.values())

    if double_spikes:
        doubles = {}
        for base in AK3_GATEWAY_SPIKES:
            for spike in single_spikes(base):
                words = tuple(spike["words"])
                doubles.setdefault(spelling_key(words), words)
        groups["ak3_double_spikes"] = list(doubles.values())
    return groups


def run(samples: int = 40_000, seed: int = 20260729, out_path: str = DEFAULT_OUT,
        double_spikes: bool = True, groups_only=None) -> dict:
    rng = random.Random(seed)
    groups = build_groups(double_spikes)
    if groups_only:
        groups = {k: v for k, v in groups.items() if k in groups_only}
    report = {
        "record": "spike_space_hunt",
        "root": list(AK3),
        "samples_per_state": samples,
        "seed": seed,
        "group_sizes": {k: len(v) for k, v in groups.items()},
        "one_sided": ("a defect-0 witness is a complete positive certificate; the "
                      "ABSENCE of one is silence and is evidence of nothing"),
        "hit_blockers": [
            "independently re-verify the rotation system",
            "reconstruct the explicit AC move list from AK(3) to this exact spelling "
            "and replay it through the pure-Python spec",
            "confirm Lackenby Thm 1.3 applies to an unreduced spelling",
        ],
        "best_bound": {}, "rows": [], "HITS": [],
    }
    print(f"[hunt] groups: {report['group_sizes']}", flush=True)
    for label, states in groups.items():
        hunt(states, samples, rng, label, report)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=1)

    report["states_hunted"] = len(report["rows"])
    report["THICKENABLE_FOUND"] = bool(report["HITS"])
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"[hunt] wrote {out_path}; {report['states_hunted']} states; "
          f"best bounds {report['best_bound']}; "
          f"THICKENABLE_FOUND {report['THICKENABLE_FOUND']}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--samples", type=int, default=40_000)
    parser.add_argument("--seed", type=int, default=20260729)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--no-double-spikes", action="store_true")
    parser.add_argument("--groups", nargs="*", default=None)
    args = parser.parse_args(argv)
    run(args.samples, args.seed, args.out, not args.no_double_spikes, args.groups)


if __name__ == "__main__":
    main()
