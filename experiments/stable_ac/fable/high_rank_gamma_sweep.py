"""Exact gamma_N over bounded families of high-rank refinements (task A4).

For each input presentation this enumerates a bounded family of refinements from
``high_rank_refine`` -- triangulations (plan section S-b) and generator splittings --
certifies each one by replay, and runs the exact rank-n census
``neuwirth_rank_n.gamma_N_factorial_n`` on it.  Every row records the input, the
refinement scheme and parameters, the output rank and words, the germ-degree multiset,
the census size, the status, the minimum defect and the full defect histogram, plus the
wall time.

Why the *input's own* census is measured first, and reported beside every row
-------------------------------------------------------------------------------
The interesting quantity is not gamma_N of a refinement in isolation but the DELTA
against the input.  Two structural facts (proved combinatorially in
``high_rank_refine``'s module docstring and checked here on every row) predict what the
delta must be:

* a triangulation puts a **degree-2** germ pair at each fresh generator, so the refined
  link is a *subdivision* of the input link and its compatible census is in canonical,
  defect-preserving bijection with the input's -- prediction: identical census size,
  identical defect histogram, identical gamma_N;
* a generator splitting is a **vertex split**, so the input link is a *minor* of the
  refined link -- prediction: the census gets cheaper, and gamma_N can only stay put or
  rise, never fall.

Both predictions are recorded per row as ``histogram_equal_to_input`` /
``min_defect_delta`` so a violation is visible rather than assumed.

Positive ladder (trap T-S2).  Nulls are worthless without a measured detection rate, so
the default input list leads with AC-trivial presentations whose rank-2 gamma_N is
**0**, each with the h-move sequence from ``("x", "y")`` that produced it.  If the
pipeline still reports gamma_N = 0 for their refinements, the machinery demonstrably
does find spherical rotation systems at rank 6-10; only then does AK(3)'s silence mean
anything.

Budget discipline (``PROCESS_GUARD.md``).  ``--limit`` defaults to 4 refinements per
scheme per input, a census larger than ``--cap-rotations`` is skipped as
``UNKNOWN_SIZE`` rather than run, each census is additionally wrapped in a SIGALRM
``--item-timeout``, and ``--max-seconds`` stops the whole sweep early and says so.  A
timeout is a process outcome and is never evidence about AC.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import high_rank_refine as HR      # noqa: E402
from experiments.stable_ac.fable.neuwirth_rank_n import (           # noqa: E402
    gamma_N_factorial_n,
)

DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "high_rank_gamma_sweep.json")
DEFAULT_SEED = 20260804
DEFAULT_CAP = 2_000_000

# Every input is cyclically reduced (the refinement builder requires it -- cyclic
# reduction is AC3 and costs nothing).  ``moves`` are 1-based h-moves of ``ac_words``
# replayed from ("x", "y") with cap 9, so the positive ladder's AC-triviality is
# provenance, not folklore; ``gamma_N`` is recomputed by this script, never assumed.
INPUTS = {
    # -- positive ladder: AC-trivial, rank-2 gamma_N = 0 ------------------------------
    "pos_a": {"words": ("xxxxY", "yXXX"), "moves": [7, 11, 3, 8, 3, 5, 3, 9, 2],
              "note": "AC-trivial from (x,y); rank-2 gamma_N = 0; total length 9"},
    "pos_b": {"words": ("xxxyx", "xxyx"), "moves": [7, 1, 12, 1, 9, 9, 12, 1, 4],
              "note": "AC-trivial from (x,y); rank-2 gamma_N = 0; total length 9"},
    "pos_c": {"words": ("xyxxxx", "yxxxx"), "moves": [1, 12, 1, 1, 12, 1, 4],
              "note": "AC-trivial from (x,y); rank-2 gamma_N = 0; total length 11"},
    "pos_d": {"words": ("xxyxy", "xyxxyxy"), "moves": [1, 10, 4, 4, 1, 6, 7],
              "note": "AC-trivial from (x,y); rank-2 gamma_N = 0; total length 12"},
    "pos_e": {"words": ("xyyxy", "yxyxyyxy"), "moves": [8, 11, 11, 4, 1, 4, 1],
              "note": "AC-trivial from (x,y); rank-2 gamma_N = 0; total length 13, "
                      "the same length band as AK(3)"},
    # -- one rung above zero ----------------------------------------------------------
    "orbit2": {"words": ("YYXXyx", "YYYxyXX"), "moves": None,
               "note": "AK(3) AC-class member with rank-2 gamma_N = 1"},
    # -- the target -------------------------------------------------------------------
    "ak3": {"words": ("xyxYXY", "xxxYYYY"), "moves": None,
            "note": "AK(3) = <x,y | xyx(yxy)^-1, x^3 y^-4>; rank-2 gamma_N = 2"},
}

DEFAULT_INPUTS = ("pos_a", "pos_b", "pos_c", "pos_d", "pos_e", "orbit2", "ak3")
SCHEMES = ("triangulate", "split")


class _ItemTimeout(Exception):
    pass


def _alarm(_signum, _frame):
    raise _ItemTimeout()


def census(words, generators, cap_rotations: int, item_timeout: int) -> dict:
    """``gamma_N_factorial_n`` behind a size gate and a SIGALRM watchdog."""
    t0 = time.time()
    size = HR.census_of(words, generators)
    if size > cap_rotations:
        return {"status": "UNKNOWN_SIZE", "expected_cases": size, "minimum_defect": None,
                "defect_histogram": {}, "link_components": None,
                "seconds": round(time.time() - t0, 3)}
    handler = None
    try:
        handler = signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(int(item_timeout))
    except (ValueError, AttributeError):            # not the main thread / no SIGALRM
        handler = None
    try:
        report = gamma_N_factorial_n(words, generators, cap_rotations=cap_rotations,
                                     keep_accepting=False)
    except _ItemTimeout:
        return {"status": "TIMEOUT", "expected_cases": size, "minimum_defect": None,
                "defect_histogram": {}, "link_components": None,
                "seconds": round(time.time() - t0, 3),
                "note": "process outcome only; never evidence about AC"}
    finally:
        if handler is not None:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, handler)
    return {"status": report["status"],
            "expected_cases": report["expected_cases"],
            "minimum_defect": report["minimum_defect"],
            "defect_histogram": {str(k): v for k, v in
                                 sorted(report["defect_histogram"].items())},
            "link_components": report["link_components"],
            "degrees": report["degrees"],
            "seconds": round(time.time() - t0, 3)}


def _structure(refinement: HR.Refinement) -> dict:
    """The subdivision / minor certificate appropriate to the refinement's scheme."""
    if refinement.scheme == "split-generator":
        cert = HR.split_minor_certificate(refinement)
        return {"kind": "vertex-split",
                "input_link_is_minor": bool(cert["is_contraction"]),
                "contracted_edges": cert["contracted_edges"],
                "expected_contracted_edges": cert["expected_contracted_edges"],
                "is_subdivision": False}
    cert = HR.link_smoothing_certificate(refinement.source, refinement.presentation)
    return {"kind": "subdivision",
            "is_subdivision": bool(cert["is_subdivision"]),
            "fresh_degrees": cert["fresh_degrees"],
            "reason": cert["reason"],
            "input_link_is_minor": bool(cert["is_subdivision"])}


def sweep(names, limit: int, seed: int, cap_rotations: int, item_timeout: int,
          max_seconds: float, schemes, out_path: str,
          planarity_budget: int = 50_000) -> dict:
    t0 = time.time()
    rows: list = []
    inputs_report: list = []
    stopped_early = None

    for name in names:
        if name in INPUTS:
            spec = dict(INPUTS[name])
        else:                                        # "w1,w2" literal
            spec = {"words": tuple(name.split(",")), "moves": None,
                    "note": "supplied on the command line"}
            name = "|".join(spec["words"])
        words = tuple(spec["words"])
        generators = HR.generators_of(words)
        base = census(words, generators, cap_rotations, item_timeout)
        entry = {"name": name, "words": list(words), "generators": list(generators),
                 "rank": len(generators), "note": spec.get("note"),
                 "moves_from_xy": spec.get("moves"), "census": base,
                 "support_planarity": HR.support_planarity(words, generators,
                                                           budget=planarity_budget)}
        inputs_report.append(entry)
        print(f"[sweep] input {name} {words} rank {len(generators)} "
              f"census {base['expected_cases']} status {base['status']} "
              f"min_defect {base['minimum_defect']}", flush=True)

        family: list = []
        if "triangulate" in schemes:
            family.extend(HR.enumerate_triangulations(words, limit=limit, seed=seed,
                                                      generators=generators))
        if "split" in schemes:
            family.extend(HR.enumerate_splits(words, limit=limit, seed=seed,
                                              generators=generators))

        for ref in family:
            if max_seconds and time.time() - t0 > max_seconds:
                stopped_early = f"max_seconds {max_seconds} reached"
                break
            item_t0 = time.time()
            report = census(ref.words, ref.generators, cap_rotations, item_timeout)
            cert = ref.certificate
            row = {
                "input_name": name,
                "input_words": list(words),
                "input_census": {"expected_cases": base["expected_cases"],
                                 "status": base["status"],
                                 "minimum_defect": base["minimum_defect"],
                                 "defect_histogram": base["defect_histogram"]},
                "scheme": ref.scheme,
                "params": ref.params,
                "output_rank": ref.rank,
                "output_generators": list(ref.generators),
                "output_words": list(ref.words),
                "output_total_length": sum(len(w) for w in ref.words),
                "max_relator_length": max(len(w) for w in ref.words),
                "germ_degrees": HR.germ_degrees(ref.words, ref.generators),
                "germ_degree_multiset": sorted(
                    HR.germ_degrees(ref.words, ref.generators).values()),
                "support_planarity": HR.support_planarity(ref.words, ref.generators,
                                                          budget=planarity_budget),
                "census_size": report["expected_cases"],
                "status": report["status"],
                "minimum_defect": report["minimum_defect"],
                "defect_histogram": report["defect_histogram"],
                "link_components": report["link_components"],
                "certificate": cert.as_row() if cert is not None else None,
                "structure": _structure(ref),
                "census_equal_to_input": report["expected_cases"] == base["expected_cases"],
                "histogram_equal_to_input": (report["defect_histogram"]
                                             == base["defect_histogram"]
                                             and report["status"] == base["status"]
                                             == "OK"),
                "min_defect_delta": (
                    None if report["minimum_defect"] is None
                    or base["minimum_defect"] is None
                    else report["minimum_defect"] - base["minimum_defect"]),
                "seconds": round(time.time() - item_t0, 3),
            }
            rows.append(row)
            print(f"[sweep]   {ref.scheme} {ref.params} rank {ref.rank} "
                  f"census {report['expected_cases']} status {report['status']} "
                  f"min_defect {report['minimum_defect']} "
                  f"delta {row['min_defect_delta']} ({row['seconds']}s)", flush=True)
        if stopped_early:
            break

    decided = [r for r in rows if r["status"] == "OK"]
    thickenable = [r for r in decided if r["minimum_defect"] == 0]
    deltas: dict = {}
    for r in decided:
        deltas[str(r["min_defect_delta"])] = deltas.get(str(r["min_defect_delta"]), 0) + 1
    subdivisions = [r for r in rows if r["structure"]["is_subdivision"]]
    summary = {
        "record": "high_rank_gamma_sweep",
        "seed": seed,
        "limit_per_scheme": limit,
        "schemes": list(schemes),
        "cap_rotations": cap_rotations,
        "item_timeout_s": item_timeout,
        "inputs": inputs_report,
        "rows": len(rows),
        "rows_decided": len(decided),
        "rows_unknown_size": sum(1 for r in rows if r["status"] == "UNKNOWN_SIZE"),
        "rows_timeout": sum(1 for r in rows if r["status"] == "TIMEOUT"),
        "thickenable_rows": len(thickenable),
        "thickenable": [{"input_name": r["input_name"], "scheme": r["scheme"],
                         "params": r["params"], "output_words": r["output_words"]}
                        for r in thickenable],
        "min_defect_delta_histogram": deltas,
        "histogram_preserved_rows": sum(1 for r in rows if r["histogram_equal_to_input"]),
        "subdivision_rows": len(subdivisions),
        "subdivision_rows_with_preserved_histogram": sum(
            1 for r in subdivisions if r["histogram_equal_to_input"]),
        "minor_certified_rows": sum(1 for r in rows
                                    if r["structure"]["input_link_is_minor"]),
        "support_planarity_by_scheme": _planarity_tally(rows),
        "positive_ladder_detection": _ladder(rows, inputs_report),
        "stopped_early": stopped_early,
        "elapsed_seconds": round(time.time() - t0, 1),
        "note": ("gamma_N here is EXACT (a full census), not a sample. "
                 "min_defect_delta > 0 means the refinement is strictly WORSE than its "
                 "input; delta = 0 means the refinement bought nothing. A TIMEOUT or "
                 "UNKNOWN_SIZE row is a process outcome and is never evidence about AC."),
    }
    payload = {"summary": summary, "rows": rows}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1)
    jsonl = os.path.splitext(out_path)[0] + ".jsonl"
    with open(jsonl, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(f"[sweep] wrote {out_path} and {jsonl}", flush=True)
    print(f"[sweep] {len(rows)} rows, {len(decided)} decided, "
          f"{len(thickenable)} thickenable, delta histogram {deltas}", flush=True)
    return summary


def _planarity_tally(rows) -> dict:
    """Simple-support planarity of the refinements, split by scheme.

    ``UNDETERMINED`` means the macro budget was too small for that support, not that the
    graph is hard: it is a process outcome, never a mathematical one.
    """
    out: dict = {}
    for row in rows:
        cell = out.setdefault(row["scheme"], {})
        key = row["support_planarity"]
        cell[key] = cell.get(key, 0) + 1
    return out


def _ladder(rows, inputs_report) -> dict:
    """Detection rate on the inputs whose own gamma_N is 0 (trap T-S2)."""
    zero = {e["name"] for e in inputs_report
            if e["census"].get("minimum_defect") == 0}
    hits = [r for r in rows if r["input_name"] in zero and r["status"] == "OK"]
    found = [r for r in hits if r["minimum_defect"] == 0]
    return {"inputs_with_gamma_N_zero": sorted(zero),
            "refinements_of_those_decided": len(hits),
            "refinements_still_gamma_N_zero": len(found),
            "detection_rate": (round(len(found) / len(hits), 4) if hits else None),
            "meaning": ("the fraction of refinements of a KNOWN-thickenable input that "
                        "the exact census still reports thickenable; a null on AK(3) is "
                        "readable only against this number")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inputs", nargs="*", default=list(DEFAULT_INPUTS),
                        help=f"names from {sorted(INPUTS)} or literal 'w1,w2' pairs")
    parser.add_argument("--limit", type=int, default=4,
                        help="refinements per scheme per input (keep small)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--schemes", nargs="*", default=list(SCHEMES), choices=SCHEMES)
    parser.add_argument("--cap-rotations", type=int, default=DEFAULT_CAP)
    parser.add_argument("--item-timeout", type=int, default=60)
    parser.add_argument("--max-seconds", type=float, default=480.0)
    parser.add_argument("--planarity-budget", type=int, default=50_000)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    sweep(args.inputs, args.limit, args.seed, args.cap_rotations, args.item_timeout,
          args.max_seconds, tuple(args.schemes), args.out, args.planarity_budget)


if __name__ == "__main__":
    main()
