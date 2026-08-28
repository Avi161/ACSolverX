"""W3b phase 1: regenerate the AK(3) mu-ladder orbit set with provenance.

The committed AK(3) ladder rows (results/stable_ac/mu_scan/
mu_ladder_ak3_only_*.jsonl) are single summary rows; the per-orbit
representatives were never persisted. This driver calls
experiments/stable_ac/cov/mu_ladder_big.climb_one_big (imported,
unmodified) on AK(3)'s canonical rep and persists the returned orbit_rows
as a first-class artifact, so the thickenability dispatch (phase 2) and any
future scan need not re-derive them.

Deterministic per-class budgets only (rungs/beam/cap/stop_mu); the time
knob stays 0 (unlimited) so the run is machine-independent. stop_mu is
pinned to 12 (the repo rule: never 13). Requires Python >= 3.12 (PEP 701
f-strings in mu_ladder_big); run via uv with numba+numpy.

Usage: ak3_orbit_regen.py RUNGS BEAM [CAP]   (defaults CAP=24)
Output: fable/proofs/checkers/out/ak3_orbits_r{RUNGS}_b{BEAM}_c{CAP}.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.stable_ac.cov.mu_ladder_big import climb_one_big

AK3 = ("YXYxyx", "YYYYxxx")


def main():
    rungs = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    beam = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    task = {
        "pres_id": "aca_115",
        "r1": AK3[0],
        "r2": AK3[1],
        "rungs": rungs,
        "beam": beam,
        "cap": cap,
        "stop_mu": 12,
        "time_per_class_s": 0,
        "max_orbits": 0,
    }
    row, orbit_rows = climb_one_big(task)
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"ak3_orbits_r{rungs}_b{beam}_c{cap}.jsonl"
    with out.open("w") as f:
        for orbit in orbit_rows:
            f.write(json.dumps(orbit) + "\n")
    print(json.dumps({
        "summary": {k: row[k] for k in
                    ("pres_id", "mu_in", "best_mu", "hits_stop",
                     "n_orbits_seen") if k in row},
        "orbit_rows_written": len(orbit_rows),
        "out": str(out.relative_to(Path(__file__).resolve().parents[3])),
    }))
    if row.get("best_mu", 99) <= 12 or row.get("hits_stop"):
        print("TRIPWIRE: mu <= 12 for AK(3)'s class — presumed bug until "
              "independently reproduced (MU_CRITERION rule 6). Quarantine.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
