"""Certified UPPER bounds on gamma_N for the spiked spellings of a presentation.

R1f's tier-3 row claims that a single spike (inserting ``c c^-1`` into a relator) drops
AK(3)'s gamma_N from 2 to 1.  The first measurement of that row came from an exact
census, which is expensive at these lengths and timed out on re-run.  It is also more
than the claim needs: the claim is a STRICT DROP, i.e. ``gamma_N(spiked) <= 1``, and an
upper bound of that shape has a cheap certificate.

    One explicit compatible rotation system with defect 2d is a WITNESS that
    gamma_N <= d.  It is verifiable in isolation (``gateway_scan.verify_witness``
    re-derives the defect from the dart data and re-checks the B-reversal
    compatibility law), so it does not inherit the sampler's heuristics.

So this module hill-climbs for a witness on every spiked spelling and reports the
verified defect.  Absence of a witness is never evidence of anything -- an unwitnessed
spike is reported as ``>= (nothing proved)`` and simply carries no claim.  A witness of
defect 0 would be a THICKENABLE spelling and is flagged loudly.

Claims addressed: MACHINERY (gamma_N of exact word-realized complexes).  Nothing here
is an AC-triviality statement about AK(3) in either direction.

This is bounded enumeration plus local search over ROTATION SYSTEMS of fixed complexes;
it is not an AC search and consumes no search node budget.
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
from ac_words import cyclic_reduce                               # noqa: E402


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "spike_witness.json")

AK3 = ("xxxYYYY", "xyxYXY")


def spelling_key(words) -> tuple:
    """Canonical key that quotients ONLY by the gamma_N-invariant symmetries.

    Rotation, inversion and relator permutation are gamma_N-invariant (the AUDITED
    symmetry lemma), so collapsing on them cannot merge spellings of different gamma_N.
    Free reduction is deliberately NOT applied -- it is the very operation under study,
    and ``certified_targets.canon_multi`` reduces first, which would collapse every
    spiked spelling back onto its base.
    """
    keys = []
    for word in words:
        candidates = []
        for variant in (word, "".join(c.swapcase() for c in reversed(word))):
            candidates.extend(variant[i:] + variant[:i] for i in range(len(variant)))
        keys.append(min(candidates))
    return tuple(sorted(keys))


def single_spikes(words):
    """Every distinct one-spike spelling, up to the gamma_N-invariant symmetries."""
    seen = {}
    out = []
    letters = sorted({c.lower() for w in words for c in w}
                     | {c.upper() for w in words for c in w})
    for idx, word in enumerate(words):
        for pos in range(len(word) + 1):
            for letter in letters:
                spike = letter + letter.swapcase()
                spiked = word[:pos] + spike + word[pos:]
                image = list(words)
                image[idx] = spiked
                image = tuple(image)
                key = spelling_key(image)
                if key in seen:
                    continue
                seen[key] = image
                out.append({"words": list(image), "relator": idx, "position": pos,
                            "spike": spike})
    return out


def witness_bound(words, samples: int, rng: random.Random) -> dict:
    """Hill-climb for a low-defect rotation, then VERIFY it independently."""
    start = time.time()
    best, orders = GS.sampled_min_defect(tuple(words), samples, rng)
    row = {"words": list(words), "witness_defect": best,
           "seconds": round(time.time() - start, 2)}
    if orders:
        checked = GS.verify_witness(tuple(words), orders)
        row["verified_defect"] = checked
        if checked != best:
            row["ERROR"] = "sampler and verifier disagree"
        row["gamma_upper_bound"] = checked // 2
    else:
        row["gamma_upper_bound"] = None
    return row


def run(words=AK3, samples: int = 60_000, seed: int = 20260729,
        out_path: str = DEFAULT_OUT) -> dict:
    rng = random.Random(seed)
    base = witness_bound(words, samples, rng)
    print(f"[spike] base {tuple(words)}: verified defect {base.get('verified_defect')} "
          f"-> gamma_N <= {base.get('gamma_upper_bound')}", flush=True)

    spikes = single_spikes(tuple(words))
    print(f"[spike] {len(spikes)} distinct single spikes", flush=True)
    rows = []
    best_bound = None
    for n, spike in enumerate(spikes, 1):
        row = witness_bound(spike["words"], samples, rng)
        row.update({k: spike[k] for k in ("relator", "position", "spike")})
        rows.append(row)
        bound = row.get("gamma_upper_bound")
        if bound is not None and (best_bound is None or bound < best_bound):
            best_bound = bound
        print(f"[spike] {n}/{len(spikes)} {tuple(row['words'])}: "
              f"defect {row.get('verified_defect')} -> gamma_N <= {bound}", flush=True)

    report = {
        "record": "spike_witness",
        "base": base,
        "samples_per_state": samples,
        "seed": seed,
        "spikes_measured": len(rows),
        "best_spike_gamma_upper_bound": best_bound,
        "strict_drop_witnessed": (best_bound is not None
                                  and base.get("gamma_upper_bound") is not None
                                  and best_bound < base["gamma_upper_bound"]),
        "THICKENABLE_SPIKE_ALERT": any(r.get("gamma_upper_bound") == 0 for r in rows),
        "note": ("witness_defect is an UPPER bound certificate (an explicit compatible "
                 "rotation system, re-verified); no lower bound is claimed here, and a "
                 "state with no witness found carries no claim at all"),
        "rows": rows,
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"[spike] wrote {out_path}; best spike bound {best_bound}; "
          f"thickenable alert {report['THICKENABLE_SPIKE_ALERT']}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--words", nargs="+", default=list(AK3))
    parser.add_argument("--samples", type=int, default=60_000)
    parser.add_argument("--seed", type=int, default=20260729)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    words = tuple(cyclic_reduce(w) for w in args.words)
    run(words, args.samples, args.seed, args.out)


if __name__ == "__main__":
    main()
