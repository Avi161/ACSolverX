"""Exact gamma_N by full census for the spiked spellings, written incrementally.

``spike_witness.py`` certifies UPPER bounds (an explicit verified rotation system).
It cannot certify a lower bound, so it can never rule out that one of AK(3)'s spiked
spellings is THICKENABLE (gamma_N = 0) -- the single outcome that would decide the
session's sub-goal via Lackenby Thm 1.3 [flagged unverified].  Only an exhaustive
census over the compatible family settles that.

The census is prod_v (deg(v)-1)! rotation systems per state, which at these lengths is
3.6-4.8 million each: affordable one state at a time, not affordable as one blocking
run over all 39 (that is what timed out).  So this driver processes states in ASCENDING
census size and flushes the report after every state, making the artifact resumable and
honest about how far it got.

Claims addressed: MACHINERY.  A gamma_N value is a statement about one exact
word-realized complex, never about the AC class it sits in.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import gamma_floor as GF                                         # noqa: E402
import neuwirth_rank_n as RN                                     # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
WITNESS_JSON = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "spike_witness.json")
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "spike_census.json")


def census(words, cap: int) -> dict:
    start = time.time()
    result = RN.gamma_N_factorial_n(tuple(words), None, cap_rotations=cap,
                                    keep_accepting=False)
    row = {"words": list(words), "status": result["status"],
           "expected_cases": result.get("expected_cases"),
           "seconds": round(time.time() - start, 1)}
    if result["status"] == "OK":
        row["minimum_defect"] = result["minimum_defect"]
        row["gamma_N"] = result["minimum_defect"] // 2
        row["defect_histogram"] = {str(k): v
                                   for k, v in sorted(result["histogram"].items())}
    return row


def run(witness_path: str = WITNESS_JSON, out_path: str = DEFAULT_OUT,
        cap: int = 6_000_000, limit: int | None = None,
        only_gateways: bool = False) -> dict:
    with open(witness_path, encoding="utf-8") as handle:
        witness = json.load(handle)
    states = [tuple(r["words"]) for r in witness["rows"]]
    if only_gateways:
        states = [tuple(r["words"]) for r in witness["rows"]
                  if r.get("gamma_upper_bound") == 1]
    states.sort(key=GF.census_size)
    if limit is not None:
        states = states[:limit]

    report = {"record": "spike_census", "base": witness["base"]["words"],
              "cap_rotations": cap, "requested": len(states),
              "note": ("exact minimum over the full compatible family; gamma_N = "
                       "minimum_defect / 2 (defects are UNHALVED)"),
              "rows": []}
    for n, words in enumerate(states, 1):
        row = census(words, cap)
        report["rows"].append(row)
        report["completed"] = n
        report["THICKENABLE_ALERT"] = any(r.get("gamma_N") == 0
                                          for r in report["rows"])
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=1)
        print(f"[census] {n}/{len(states)} {words}: {row['status']} "
              f"gamma_N={row.get('gamma_N')} ({row['seconds']}s)", flush=True)
    decided = [r for r in report["rows"] if r["status"] == "OK"]
    report["decided"] = len(decided)
    report["gamma_histogram"] = {}
    for row in decided:
        key = str(row["gamma_N"])
        report["gamma_histogram"][key] = report["gamma_histogram"].get(key, 0) + 1
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"[census] wrote {out_path}; decided {len(decided)}/{len(states)}; "
          f"gamma histogram {report['gamma_histogram']}; "
          f"thickenable alert {report.get('THICKENABLE_ALERT')}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--witness", default=WITNESS_JSON)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--cap", type=int, default=6_000_000)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-gateways", action="store_true")
    args = parser.parse_args(argv)
    run(args.witness, args.out, args.cap, args.limit, args.only_gateways)


if __name__ == "__main__":
    main()
