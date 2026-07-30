"""Colab-scale runner for ``data/AC19_extended_aut_min.csv`` @ budget 1k.

Presentation-major A/B: length baseline vs best heuristic ``s20_mk2``
(L+20S+2MK). Reuses ``run_ab._run_parallel`` (Drive flock / heartbeat / resume).

    from experiments.heuristic_search.runners.run_ac19_autmin_scale import (
        run_ac19_autmin_scale, load_rows)
    run_ac19_autmin_scale(cfg, out_dir=...)
"""
from __future__ import annotations

import csv
import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners import run_ab  # noqa: E402

ROOT = _d
CSV_PATH = os.path.join(ROOT, "data", "AC19_extended_aut_min.csv")
DATASET_NAME = "ac19_extended_aut_min"


def _cfg(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


run_ab.ARMS.update({
    "baseline": None,
    "s20": _cfg(L=1.0, S=20.0),
    "s20_mk2": _cfg(L=1.0, S=20.0, MK=2.0),
    "s12": _cfg(L=1.0, S=12.0),
    "s28": _cfg(L=1.0, S=28.0),
})


def load_rows():
    """``[{name, r1, r2, n_members}]`` from the Aut-min CSV."""
    rows = []
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "name": r["name"],
                "r1": r["r1"],
                "r2": r["r2"],
                "n_members": int(r["n_members"]),
            })
    return rows


def _stride_chunk(rows, chunks, chunk_index):
    if not chunks or chunks <= 1 or chunk_index is None:
        return rows, ""
    if not (1 <= int(chunk_index) <= int(chunks)):
        raise ValueError(f"CHUNK_INDEX must be 1..{chunks}, got {chunk_index}")
    i = int(chunk_index) - 1
    n = int(chunks)
    picked = [r for k, r in enumerate(rows) if k % n == i]
    return picked, f"_c{chunk_index}of{chunks}"


def _report(out, cfg):
    data = [json.loads(l) for l in open(out) if l.strip()]
    arms = list(cfg["ARMS"])
    pts = [b for b in cfg["CHECKPOINTS"] if b <= cfg["NODE_BUDGET"]]
    by_name = {}
    for r in data:
        by_name.setdefault(r["name"], {})[r["arm"]] = r
    complete = [nm for nm, m in by_name.items() if all(a in m for a in arms)]
    n = len(complete)

    def curve(arm):
        return [sum(1 for nm in complete
                    if by_name[nm][arm].get("solved_at") is not None
                    and by_name[nm][arm]["solved_at"] <= b)
                for b in pts]

    lines = [
        f"# A/B — {cfg['DATASET']}, budget {cfg['NODE_BUDGET']:,}, "
        f"cap {cfg['MAX_RELATOR_LENGTH']}",
        "",
        f"{n} complete presentations (all {len(arms)} arms; "
        f"{len(by_name) - n} partial ignored).",
        "",
        "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
        "|---" * (len(pts) + 1) + "|",
    ]
    curves = {a: curve(a) for a in arms}
    for a in arms:
        lines.append(
            f"| {a} | " + " | ".join(f"{v}/{n}" for v in curves[a]) + " |")
    if "baseline" in curves and n and len(arms) > 1:
        base = curves["baseline"]
        lines += ["", "## Δ vs length baseline", "",
                  "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
                  "|---" * (len(pts) + 1) + "|"]
        for a in arms:
            if a == "baseline":
                continue
            g = [x - y for x, y in zip(curves[a], base)]
            lines.append(
                f"| {a} | " + " | ".join(f"{v:+d}" for v in g) + " |")
    md = out.replace(".jsonl", ".md")
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    print(f"  wrote {md}", flush=True)


def run_ac19_autmin_scale(cfg, out_dir="results/hsearch", heartbeat_secs=60,
                          progress_secs=300):
    rows = load_rows()
    chunks = cfg.get("CHUNKS") or 1
    chunk_index = cfg.get("CHUNK_INDEX")
    rows, tag = _stride_chunk(rows, chunks, chunk_index)

    subset = cfg.get("SUBSET")
    if subset is not None:
        rows = rows[: int(subset)]

    cfg = dict(cfg)
    cfg["DATASET"] = DATASET_NAME
    stem = cfg.get("OUT_STEM", "hsearch_ac19_autmin_1k")
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
        if out.startswith(run_ab._REMOTE_PREFIX) else out)
    seen = ((run_ab._done(out) | run_ab._done(stage_probe))
            if cfg.get("RESUME", True) else set())
    todo = [(a, {"name": r["name"], "r1": r["r1"], "r2": r["r2"]})
            for r in rows for a in arms
            if (a, r["name"]) not in seen]
    n_workers, per_gb = run_ab._resolve_workers(
        cfg, budget, mrl, engine, keep_path)
    print(f"  {len(arms)} arms x {len(rows)} presentations, budget {budget:,}, "
          f"cap {mrl}  [JOB_ORDER=presentation]"
          + ("  [low-memory: KEEP_PATH=False]" if not keep_path else "")
          + ("  [engine: hcompact]" if engine == "hcompact" else "")
          + (f"  [{n_workers} workers, ~{per_gb:.1f} GB/search]"
             if n_workers > 1 else ""), flush=True)
    print(f"  {len(seen)} rows resumed; {len(todo)} to run", flush=True)
    print(f"  -> {out}", flush=True)

    n_workers = max(int(n_workers), 1)
    run_ab._run_parallel(cfg, out, todo, n_workers, budget, mrl, engine,
                         keep_path, heartbeat_secs, progress_secs)
    _report(out, cfg)
    return out
