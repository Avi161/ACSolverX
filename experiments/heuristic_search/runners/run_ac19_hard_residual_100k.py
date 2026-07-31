"""Run the 4-arm hard residual @ budget 100k (new file — does not edit scale runner).

Dataset = ``results/heuristic_search/ac19_autmin_screen/hard_residual_10k_union.csv``
(the union of every presentation any of baseline / s20_mk2 / s20_mk2_mK2 / s20_f4
failed on at budget 10k). All 4 arms run on the **same** list.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.run_ac19_hard_residual_100k
"""
from __future__ import annotations

import csv
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners import run_ac19_autmin_scale as base  # noqa: E402

ROOT = _d
DEFAULT_CSV = os.path.join(
    ROOT, "results", "heuristic_search", "ac19_autmin_screen",
    "hard_residual_10k_union.csv",
)
DATASET_NAME = "ac19_hard_residual_10k"
DEFAULT_ARMS = ("baseline", "s20_mk2", "s20_mk2_mK2", "s20_f4")


def load_hard_rows(csv_path: str | None = None):
    path = csv_path or DEFAULT_CSV
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"hard residual CSV missing: {path}\n"
            "Regenerate via the ac19_autmin_screen analysis / HARD_RESIDUAL_100k.md")
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "name": r["name"],
                "r1": r["r1"],
                "r2": r["r2"],
                "n_members": int(r["n_members"]) if r.get("n_members") else 0,
            })
    if not rows:
        raise RuntimeError(f"empty hard residual CSV: {path}")
    return rows, path


def run_hard_residual_100k(cfg, out_dir="results/hsearch", heartbeat_secs=60,
                           progress_secs=300):
    """Same schedule as ``run_ac19_autmin_scale``, but rows come from the union CSV."""
    csv_path = cfg.get("HARD_CSV") or DEFAULT_CSV
    rows, used = load_hard_rows(csv_path)
    print(f"  hard residual CSV: {used}  ({len(rows)} presentations)", flush=True)

    # coverage: every name unique
    names = [r["name"] for r in rows]
    if len(names) != len(set(names)):
        raise RuntimeError("duplicate names in hard residual CSV")

    chunks = cfg.get("CHUNKS") or 1
    chunk_index = cfg.get("CHUNK_INDEX")
    rows, tag = base._stride_chunk(rows, chunks, chunk_index)

    cfg = dict(cfg)
    cfg["DATASET"] = DATASET_NAME
    if not cfg.get("ARMS"):
        cfg["ARMS"] = list(DEFAULT_ARMS)
    for a in cfg["ARMS"]:
        if a not in base.ARM_SPECS:
            raise KeyError(f"unknown arm {a!r}; known={sorted(base.ARM_SPECS)}")

    # force the four 10k arms unless user overrides carefully
    missing = [a for a in DEFAULT_ARMS if a not in cfg["ARMS"]]
    if missing:
        print(f"  [warn] ARMS omit {missing} — hard-tail compare will be incomplete",
              flush=True)

    stem = cfg.get("OUT_STEM", "hsearch_ac19_hard100k")
    if tag:
        stem = f"{stem}{tag}"
    cfg["OUT_STEM"] = stem

    budget = cfg["NODE_BUDGET"]
    mrl = cfg["MAX_RELATOR_LENGTH"]
    arms = list(cfg["ARMS"])
    keep_path = cfg.get("KEEP_PATH", False)
    engine = cfg.get("ENGINE", "hcompact")
    if engine not in ("hsolve", "hcompact"):
        raise ValueError(f"unknown ENGINE {engine!r}")

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(
        out_dir, f"{stem}_{DATASET_NAME}_b{budget}_mrl{mrl}.jsonl")

    stage_probe = (os.path.join(
        cfg.get("STAGE_DIR") or os.path.join(os.path.expanduser("~"),
                                             ".hsearch_stage"),
        os.path.basename(out))
        if out.startswith(base.run_ab._REMOTE_PREFIX) else out)
    seen = ((base.run_ab._done(out) | base.run_ab._done(stage_probe))
            if cfg.get("RESUME", True) else set())
    todo = [(a, {"name": r["name"], "r1": r["r1"], "r2": r["r2"]})
            for r in rows for a in arms
            if (a, r["name"]) not in seen]

    # assert no arm×name from the CSV is silently dropped except via resume
    expected = {(a, r["name"]) for r in rows for a in arms}
    covered = seen | {(a, j["name"]) for a, j in todo}
    if covered != expected:
        missing_jobs = expected - covered
        raise RuntimeError(
            f"job coverage hole: {len(missing_jobs)} arm×name pairs not scheduled")

    n_workers, per_gb = base.run_ab._resolve_workers(
        cfg, budget, mrl, engine, keep_path)
    print(f"  {len(arms)} arms x {len(rows)} presentations, budget {budget:,}, "
          f"cap {mrl}  [HARD residual union] arms={arms}"
          + (f"  [{n_workers} workers, ~{per_gb:.1f} GB/search]"
             if n_workers > 1 else ""), flush=True)
    print(f"  {len(seen)} rows resumed; {len(todo)} to run; "
          f"expected {len(expected)} arm×name", flush=True)
    print(f"  -> {out}", flush=True)

    n_workers = max(int(n_workers), 1)
    base._run_parallel(cfg, out, todo, n_workers, budget, mrl, engine,
                       keep_path, heartbeat_secs, progress_secs)
    base._report(out, cfg)
    return out


def main():
    cfg = {
        "ARMS": list(DEFAULT_ARMS),
        "ENGINE": "hcompact",
        "N_WORKERS": "auto",
        "KEEP_PATH": False,
        "NODE_BUDGET": 100_000,
        "CHECKPOINTS": [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
        "MAX_RELATOR_LENGTH": 48,
        "RESUME": True,
        "OUT_STEM": "hsearch_ac19_hard100k",
        "CHUNKS": 1,
        "CHUNK_INDEX": 1,
        "HARD_CSV": DEFAULT_CSV,
    }
    out_dir = os.path.join(ROOT, "results", "heuristic_search",
                           "hsearch_ac19_hard100k")
    run_hard_residual_100k(cfg, out_dir=out_dir)


if __name__ == "__main__":
    main()
