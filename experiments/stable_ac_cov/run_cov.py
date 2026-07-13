"""CoV runner: benchmark CSV rows → one-shot CoV → 2-gen numba greedy → jsonl.

Reuses ``run_baseline``'s seams by import (the ``greedy_search`` dispatcher,
``_repair_jsonl`` / ``_read_done`` resume machinery, ``_build_row`` schema) and
writes to its own namespace ``results/stable_ac_cov/``. One output file per
budget — when the budget changes, the file changes. jsonl schema = the greedy
schema + ``{mode, z_word, n_cov, cov_applicable, r1_orig, r2_orig,
start_total_length_orig, start_total_length_cov, iso_index, n_subs, source}``.

``mode: baseline`` runs the identity transform on the same rows/budgets so a
same-budget cov-vs-baseline comparison needs no other pipeline.

CLI (from the repo root):
    .venv/bin/python3 -m experiments.stable_ac_cov.run_cov \
        --config experiments/stable_ac_cov/config_cov.yaml
"""

import argparse
import csv
import glob
import json
import os
import time
from datetime import datetime

import yaml

from experiments import run_baseline
from experiments.stable_ac_cov import cov

COV_DEFAULTS = {
    "datasets": [
        "results/benchmark/subsets/benchmark_subset_10.csv",
        "results/benchmark/reach/reach_tier_1.csv",
    ],
    "budgets": [100, 1000],
    "mode": "cov",                    # "cov" | "baseline"
    "z_family": cov.Z_FAMILY_TAG,
    "max_relator_length": cov.DEFAULT_CAP,
    "cap_headroom": cov.CAP_HEADROOM,
    "reject_len": cov.REJECT_LEN,
    "cyclic_reduce": True,
    "out_dir": "results/stable_ac_cov",
    "resume": True,
}


def find_repo_root(start):
    """Walk up until a dir holds both experiments/ and data/ (repo rule)."""
    d = os.path.abspath(start)
    while True:
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(f"no repo root (experiments/ + data/) above {start}")
        d = parent


def load_config(config_path=None, **overrides):
    c = dict(COV_DEFAULTS)
    if config_path:
        with open(config_path) as f:
            c.update(yaml.safe_load(f) or {})
    c.update({k: v for k, v in overrides.items() if v is not None})
    if c["mode"] not in ("cov", "baseline"):
        raise ValueError(f"mode must be 'cov' or 'baseline', got {c['mode']!r}")
    return c


def load_rows(dataset_paths, root):
    """(row_id, r1, r2, source) per benchmark row.

    Subset CSVs key rows by int ``pres_id``; reach CSVs by the ``name`` column
    (e.g. "AK(3)"). Both id kinds land in the jsonl ``pres_id`` field and in
    the resume set unchanged.
    """
    rows = []
    for p in dataset_paths:
        ap = p if os.path.isabs(p) else os.path.join(root, p)
        src = os.path.basename(p)
        with open(ap) as f:
            for rec in csv.DictReader(f):
                rid = int(rec["pres_id"]) if "pres_id" in rec else rec["name"]
                rows.append((rid, rec["r1"], rec["r2"], src))
    return rows


def _dataset_tag(dataset_paths):
    parts = []
    for p in dataset_paths:
        stem = os.path.splitext(os.path.basename(p))[0]
        digits = "".join(ch for ch in stem if ch.isdigit())
        lead = "s" if "subset" in stem else ("r" if "reach" in stem else stem[:3])
        parts.append(lead + digits)
    return "".join(parts)


def _run_prefix(c, node_budget, n_rows):
    """Date-less stem of every knob that changes the result (resume identity).

    The z-family tag is identity for cov mode (a different family = a different
    experiment); row caps are derived deterministically from the inputs, so
    they stay out of the name. mrl = the base cap / baseline cap.
    """
    kind = "cov" if c["mode"] == "cov" else "covbase"
    zfam = f"{c['z_family']}_" if c["mode"] == "cov" else ""
    cyc = "cyc" if c["cyclic_reduce"] else "noncyc"
    tag = _dataset_tag(c["datasets"])
    return (f"{kind}_{node_budget}_{n_rows}_{zfam}mrl{c['max_relator_length']}"
            f"_{cyc}_{tag}_")


def _resolve_out_path(c, node_budget, n_rows, root):
    out_dir = c["out_dir"]
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(root, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(c, node_budget, n_rows)
    stem = prefix + datetime.now().strftime("%m_%d_%y")
    if c.get("resume", True):
        existing = glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]
    return os.path.join(out_dir, stem + ".jsonl")


def _base_cfg(c):
    """run_baseline-compatible cfg for ``_build_row`` (paths inline)."""
    base = dict(run_baseline.DEFAULT_CONFIG)
    base["MAX_RELATOR_LENGTH"] = c["max_relator_length"]
    base["CYCLIC_REDUCE"] = c["cyclic_reduce"]
    base["PATH_IN_SEPARATE_FILE"] = False
    return base


def _transform(c, r1, r2):
    """(r1', r2', cap, n_cov, extra-fields) for one row under c["mode"]."""
    if c["mode"] == "baseline":
        return r1, r2, c["max_relator_length"], 0, {
            "cov_applicable": None, "z_word": None, "iso_index": None,
            "n_subs": 0,
            "start_total_length_orig": len(r1) + len(r2),
            "start_total_length_cov": len(r1) + len(r2),
        }
    r1t, r2t, cap, n_cov, meta = cov.cov_for_greedy(
        r1, r2,
        default_cap=c["max_relator_length"],
        cap_headroom=c["cap_headroom"],
        reject_len=c["reject_len"],
    )
    return r1t, r2t, cap, n_cov, meta


def run_budget(c, node_budget, rows, root):
    out_path = _resolve_out_path(c, node_budget, len(rows), root)
    run_baseline._repair_jsonl(out_path)
    done, n_seen, n_solved = run_baseline._read_done(out_path)
    print(f"[{c['mode']}] budget={node_budget} -> {os.path.basename(out_path)} "
          f"(resume: {n_seen} done, {n_solved} solved)", flush=True)

    bcfg = _base_cfg(c)
    with open(out_path, "a") as out_f:
        for rid, r1, r2, src in rows:
            if rid in done:
                continue
            r1t, r2t, cap, n_cov, extra = _transform(c, r1, r2)
            t0 = time.perf_counter()
            stats = run_baseline.greedy_search(
                r1t, r2t, node_budget, max_relator_length=cap,
                cyclic_reduce=c["cyclic_reduce"])
            elapsed = time.perf_counter() - t0

            row = run_baseline._build_row(bcfg, rid, r1t, r2t, node_budget,
                                          stats, elapsed)
            row["max_relator_length_cap"] = cap
            row["mode"] = c["mode"]
            row["n_cov"] = n_cov
            row["r1_orig"] = r1
            row["r2_orig"] = r2
            row["source"] = src
            row.update(extra)
            out_f.write(json.dumps(row) + "\n")
            out_f.flush()
            os.fsync(out_f.fileno())

            n_seen += 1
            n_solved += int(bool(stats["solved"]))
            print(f"  {rid}: solved={stats['solved']} "
                  f"nodes={stats['nodes_explored']} "
                  f"path={stats['path_length']} cap={cap} "
                  f"z={extra.get('z_word')}", flush=True)
    print(f"[{c['mode']}] budget={node_budget} done: "
          f"{n_solved}/{n_seen} solved", flush=True)
    return out_path


def run(config_path=None, **overrides):
    c = load_config(config_path, **overrides)
    root = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
    rows = load_rows(c["datasets"], root)
    print(f"{len(rows)} presentations from {len(c['datasets'])} dataset(s); "
          f"budgets {c['budgets']}; mode {c['mode']}", flush=True)
    return [run_budget(c, b, rows, root) for b in c["budgets"]]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None, help="config_cov.yaml path")
    ap.add_argument("--mode", default=None, choices=["cov", "baseline"])
    ap.add_argument("--budget", type=int, nargs="*", default=None,
                    help="override budgets, e.g. --budget 100 1000")
    args = ap.parse_args()
    run(config_path=args.config, mode=args.mode, budgets=args.budget)


if __name__ == "__main__":
    main()
