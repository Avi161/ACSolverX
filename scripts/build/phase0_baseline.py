"""Phase 0 of the d-o-t data-crafting pipeline.

See ``experiments/eda+data_collection/4.DETAILED_STEPS_DATA_CRAFTING.md`` Phase 0:
  0.1 preconditions fail-fast gate (inputs present + canon importable),
  0.2 re-derive censored bounds B_soft/B_hard from live data, assert vs documented 48/150,
  0.3 snapshot the current distribution (the immutable "before" the Phase-8 report diffs).

Run from the repo root:
    python scripts/phase0_baseline.py

Read-only on all inputs (originals never modified). Writes ``data/percentiles.json`` and
``data/baseline_distribution.json``. Gate-style: prints diagnostics, exits non-zero with a
message on any failure, else prints ``PHASE0 PASS``.
"""
import os
import sys
import json
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset        # noqa: E402  (reuse load_archive; do not re-parse the archive)


def check_inputs():
    """0.1 -- pipeline-wide fail-fast gate. Returns a list of problems ([] means ok).

    Checks the three pipeline inputs exist and are non-empty (merged-paths and the greedy
    CSV are not consumed by Phase 0 itself, but 0.1 is a *pipeline-wide* gate), plus the
    canon smoke-test the doc requires -- if canon is broken, surface it now, not at Phase 1.
    """
    problems = []
    for path in (cfg.ARCHIVE, cfg.MERGED_PATHS, cfg.GREEDY_CSV):
        if not os.path.exists(path):
            problems.append(f"missing input: {path}")
        elif os.path.getsize(path) == 0:
            problems.append(f"empty input: {path}")
    try:
        from scripts.lib import canon  # noqa: E402
        key = canon.canon_key("xyxYXY", "xxxYYYY")
        ok = (isinstance(key, tuple) and len(key) == 2
              and isinstance(key[0], str) and isinstance(key[1], int))
        if not ok:
            problems.append(f"canon.canon_key returned unexpected shape: {key!r}")
    except Exception as e:  # noqa: BLE001 - any failure here is a real precondition failure
        problems.append(f"canon import/smoke-test failed: {e}")
    return problems


def compute_percentiles(dots):
    """0.2 -- solved d-o-t percentiles (numpy linear). Native floats (JSON-safe)."""
    arr = np.asarray(list(dots), dtype=float)
    pcts = {f"p{p}": float(np.percentile(arr, p)) for p in (50, 75, 90, 95, 99)}
    pcts["max"] = float(arr.max())
    pcts["min"] = float(arr.min())
    return pcts


def derive_bounds(pcts):
    """0.2 -- B_soft = round(p90), B_hard = round(p99). Native ints."""
    return int(round(pcts["p90"])), int(round(pcts["p99"]))


def baseline_distribution(labelled, censored):
    """0.3 -- per-band counts (both denominators) + length x hardness table.

    Records band fractions against BOTH the total and the labelled-only denominator,
    because the source §2 "current" percentages were taken relative to labelled-only while
    the hard/unsolved share is relative to the total -- storing both removes the ambiguity.
    """
    dots = [int(r["min_dot"]) for r in labelled]
    band_counts = Counter(cfg.band_of(d) for d in dots)
    n_lab, n_cen = len(labelled), len(censored)
    total = n_lab + n_cen

    bands = {
        "easy": int(band_counts.get("easy", 0)),
        "valley": int(band_counts.get("valley", 0)),
        "hard_solved": int(band_counts.get("hard_solved", 0)),
        "hard_unsolved": n_cen,
    }
    frac_total = {k: (v / total if total else 0.0) for k, v in bands.items()}
    frac_labelled = {k: (bands[k] / n_lab if n_lab else 0.0)
                     for k in ("easy", "valley", "hard_solved")}

    by_len = {}
    for r in labelled:
        by_len.setdefault(int(r["total_len"]), {"solved": [], "cen": 0})["solved"].append(int(r["min_dot"]))
    for r in censored:
        by_len.setdefault(int(r["total_len"]), {"solved": [], "cen": 0})["cen"] += 1
    table = []
    for tl in sorted(by_len):
        s, c = by_len[tl]["solved"], by_len[tl]["cen"]
        n = len(s) + c
        table.append({
            "total_len": tl,
            "n_solved": len(s),
            "solved_median_dot": (float(np.median(s)) if s else None),
            "n_censored": c,
            "censored_frac": (c / n if n else 0.0),
        })

    cen_len_dist = {int(k): int(v)
                    for k, v in sorted(Counter(int(r["total_len"]) for r in censored).items())}
    n_cen_le13 = sum(v for k, v in cen_len_dist.items() if k <= 13)

    return {
        "n_labelled": n_lab,
        "n_censored": n_cen,
        "n_total": total,
        "band_counts": bands,
        "band_frac_total": frac_total,
        "band_frac_labelled": frac_labelled,
        "length_hardness": table,
        "censored_len_dist": cen_len_dist,
        "n_censored_le13": n_cen_le13,
    }


def _write_json(obj, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def main(archive=None, percentiles_json=None, baseline_json=None):
    archive = archive or cfg.ARCHIVE
    percentiles_json = percentiles_json or cfg.PERCENTILES_JSON
    baseline_json = baseline_json or cfg.BASELINE_JSON

    problems = check_inputs()
    if problems:
        for p in problems:
            print("  PHASE0 0.1 FAIL:", p)
        raise SystemExit("Phase 0 preconditions FAILED")

    labelled, censored = dot_dataset.load_archive(archive)
    pcts = compute_percentiles(r["min_dot"] for r in labelled)
    b_soft, b_hard = derive_bounds(pcts)

    if abs(b_soft - cfg.B_SOFT_EXPECTED) > cfg.B_TOL or abs(b_hard - cfg.B_HARD_EXPECTED) > cfg.B_TOL:
        print(f"  PHASE0 0.2 FAIL: derived B_soft={b_soft} B_hard={b_hard} vs expected "
              f"{cfg.B_SOFT_EXPECTED}/{cfg.B_HARD_EXPECTED} (tol {cfg.B_TOL})")
        raise SystemExit("Phase 0 bound derivation FAILED -- archive distribution moved; review 4-§4")

    percentiles_obj = {
        **pcts,
        "B_soft": b_soft,
        "B_hard": b_hard,
        "n_labelled": len(labelled),
        "method": "linear",
        "archive": archive,
    }
    baseline_obj = {"schema_version": 1, "archive": archive,
                    **baseline_distribution(labelled, censored)}

    _write_json(percentiles_obj, percentiles_json)
    _write_json(baseline_obj, baseline_json)

    print("PHASE0 PASS")
    print(f"  rows: {len(labelled)} labelled + {len(censored)} censored = {len(labelled) + len(censored)}")
    print(f"  percentiles: p50={pcts['p50']:.0f} p75={pcts['p75']:.0f} p90={pcts['p90']:.0f} "
          f"p95={pcts['p95']:.0f} p99={pcts['p99']:.0f} max={pcts['max']:.0f}")
    print(f"  bounds: B_soft={b_soft} B_hard={b_hard}")
    bf = baseline_obj["band_frac_total"]
    print(f"  bands(total): easy={bf['easy']:.3f} valley={bf['valley']:.3f} "
          f"hard_solved={bf['hard_solved']:.3f} hard_unsolved={bf['hard_unsolved']:.3f}")
    print(f"  wrote {percentiles_json} and {baseline_json}")


if __name__ == "__main__":
    main()
