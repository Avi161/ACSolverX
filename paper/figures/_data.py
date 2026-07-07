"""Data loaders for the NeurIPS stable-AC figures.

Every path is resolved relative to the worktree root (two levels above this
file: paper/figures/_data.py -> paper -> <root>). All data files are
git-tracked and present in the worktree.

Generic loaders:
    load_jsonl(path)      -> list[dict]
    load_jsonl_gz(path)   -> list[dict]   (gzip-compressed jsonl)
    load_csv(path)        -> list[dict]   (DictReader rows, all values str)

Per-source parsers return the parsed rows for one figure's data source.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# generic loaders
# --------------------------------------------------------------------------
def load_jsonl(path):
    """Read a plain JSONL file into a list of dicts (skips blank lines)."""
    path = Path(path)
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_jsonl_gz(path):
    """Read a gzip-compressed JSONL file into a list of dicts."""
    path = Path(path)
    rows = []
    with gzip.open(path, "rt") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path):
    """Read a CSV with header into a list of dicts (values are strings)."""
    path = Path(path)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
# per-source parsers
# --------------------------------------------------------------------------
def baseline_solved_rows():
    """2-gen greedy baseline over the MS(640) calibration slice (640 rows)."""
    return load_jsonl(ROOT / "results/baseline_greedy/solved/calibration_baseline.jsonl")


ARM_NAMES = ["r1", "r2", "x", "y"]


def arm_solved_rows(arm):
    """3-gen z=w stabilized calibration run for one arm (640 rows)."""
    assert arm in ARM_NAMES, arm
    return load_jsonl(
        ROOT
        / f"results/stable_ac/3_generators_w_choices/ms640/runs/calibration_{arm}.jsonl"
    )


AK3_FORMS = ["rep", "textbook"]
AK3_BUDGETS = ["100000", "1000000"]


def ak3_rows(form, budget):
    """AK(3) wormhole word sweep for one (form, budget) cell (97 rows)."""
    assert form in AK3_FORMS, form
    budget = str(budget)
    assert budget in AK3_BUDGETS, budget
    return load_jsonl(
        ROOT
        / f"results/stable_ac/3_generators_w_choices/ak_3_test/runs/ak3_{form}_{budget}.jsonl"
    )


def hard_rows(idx):
    """Hard-MS wormhole sweep for idx in {625, 610} at the 100k screen."""
    assert idx in (625, 610), idx
    return load_jsonl(
        ROOT
        / f"results/stable_ac/3_generators_w_choices/hard_solved_test/runs/hard_ms{idx}_100000.jsonl"
    )


def campaign_trials():
    """All 16,870 Lane-D stabilized-quotient greedy trials (gz)."""
    return load_jsonl_gz(
        ROOT / "results/stable_ac/ak3_stable_proof/archive/campaign_trials.jsonl.gz"
    )


def campaign_grid_probes():
    """Lane-B / Lane-C / MITM grid probes archive (gz)."""
    return load_jsonl_gz(
        ROOT / "results/stable_ac/ak3_stable_proof/archive/campaign_grid_probes.jsonl.gz"
    )


def lane_c_trivial_z():
    """Lane-C trivial-z 3-gen probes (2 rows @200k)."""
    return load_jsonl(
        ROOT / "results/stable_ac/ak3_stable_proof/runs/lane_c_trivial_z.jsonl"
    )


def beam_laneD_floor():
    """Beam-search RL agent on the Lane-D floor set (155 rows)."""
    return load_csv(
        ROOT / "results/stable_ac/ak3_stable_proof/runs/beam_laneD_floor.csv"
    )


def beam_laneD_floor_w2048():
    """Beam width=2048 escalation on the floor set (30 rows)."""
    return load_csv(
        ROOT / "results/stable_ac/ak3_stable_proof/runs/beam_laneD_floor_w2048.csv"
    )


def cap_solve_stratified():
    """Cap-test stratified solve sweep (1,800 rows)."""
    return load_jsonl(ROOT / "experiments/test_cap/solve_stratified.jsonl")


def floor_census():
    """Lane-D floor census: 1,006 elimination floors keyed by floor_mkey."""
    return load_jsonl(
        ROOT / "results/stable_ac/ak3_stable_proof/laneD/floor_census.jsonl"
    )


def cert_laneF():
    """The F -> AK(3) substitution-path certificate (single JSON object)."""
    with open(ROOT / "results/stable_ac/ak3_stable_proof/certs/laneF_F_to_AK3.json") as f:
        return json.load(f)
