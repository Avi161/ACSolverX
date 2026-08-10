"""Colab-scale runner for solved_1hop_autclean (new wrapper; does not edit run_ab).

Loads the frozen Aut-orbit list, registers arms, stride-chunks, builds a
**presentation-major** todo (all arms of row i before row i+1), then reuses
``run_ab._run_parallel`` so Drive flock / heartbeat / resume stay identical.

    from experiments.heuristic_search.runners.run_solved1hop_scale import (
        run_solved1hop_scale, load_frozen)
    run_solved1hop_scale(cfg, out_dir=...)
"""
from __future__ import annotations

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
FREEZE = os.path.join(ROOT, "results", "heuristic_search", "splits",
                      "solved_1hop_autclean.json")
DATASET_NAME = "solved_1hop_autclean"


def _cfg(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


# Register arms without editing run_ab.py.
run_ab.ARMS.update({
    "s12": _cfg(L=1.0, S=12.0),
    "s20": _cfg(L=1.0, S=20.0),
    "s24": _cfg(L=1.0, S=24.0),
    "s28": _cfg(L=1.0, S=28.0),
    "s20_mk2": _cfg(L=1.0, S=20.0, MK=2.0),
    "s24_k1_mk2": _cfg(L=1.0, S=24.0, K=1.0, MK=2.0),
    "baseline": None,
})


def load_frozen():
    """``[{name, r1, r2, kind, ...}]`` from the write-once freeze."""
    with open(FREEZE) as f:
        data = json.load(f)
    return list(data["rows"])


def _stride_chunk(rows, chunks, chunk_index):
    if not chunks or chunks <= 1 or chunk_index is None:
        return rows, ""
    if not (1 <= int(chunk_index) <= int(chunks)):
        raise ValueError(f"CHUNK_INDEX must be 1..{chunks}, got {chunk_index}")
    i = int(chunk_index) - 1
    n = int(chunks)
    picked = [r for k, r in enumerate(rows) if k % n == i]
    return picked, f"_c{chunk_index}of{chunks}"


def _report_complete_rows(out, cfg):
    """Like ``run_ab.report``, but denominators are presentations with all arms present.

    Suppresses the gap 'still widening / turned over' line whenever any arm
    saturates the complete-row denominator (gap-metric trap).
    """
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
        f"{n} complete presentations (all {len(arms)} arms present; "
        f"{len(by_name) - n} partial rows ignored). "
        "Job order was presentation-major.",
        "",
        "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
        "|---" * (len(pts) + 1) + "|",
    ]
    curves = {a: curve(a) for a in arms}
    for a in arms:
        lines.append(f"| {a} | " + " | ".join(f"{v}/{n}" for v in curves[a]) + " |")

    if "baseline" in curves and n > 0 and len(arms) > 1:
        base = curves["baseline"]
        saturated = any(curves[a][-1] >= n for a in arms)
        lines += ["", "## Δ vs length baseline (complete rows only)", "",
                  "| arm | " + " | ".join(f"{b:,}" for b in pts)
                  + (" |" if saturated else " | verdict |"),
                  "|---" * (len(pts) + (1 if saturated else 2)) + "|"]
        for a in arms:
            if a == "baseline":
                continue
            g = [x - y for x, y in zip(curves[a], base)]
            if saturated:
                lines.append(
                    f"| {a} | " + " | ".join(f"{v:+d}" for v in g) + " |")
            else:
                mid = g[len(g) // 2]
                verdict = ("still widening" if g[-1] > mid + 1 else
                           "turned over" if g[-1] < mid - 1 else "flat")
                lines.append(
                    f"| {a} | " + " | ".join(f"{v:+d}" for v in g)
                    + f" | {verdict} |")
        if saturated:
            lines += ["",
                      "Gap verdict suppressed: at least one arm saturates the "
                      "complete-row denominator (gap-metric trap).", ""]

    md = out.replace(".jsonl", ".md")
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print()
    print("\n".join(lines))
    print(f"\n  wrote {md}")


def run_solved1hop_scale(cfg, out_dir="results/hsearch", heartbeat_secs=60,
                         progress_secs=300):
    """Presentation-major A/B on the frozen solved_1hop_autclean set."""
    rows = load_frozen()
    kind = cfg.get("KIND_FILTER")  # None | "seed" | "moved_cov"
    if kind:
        rows = [r for r in rows if r.get("kind") == kind]
    chunks = cfg.get("CHUNKS") or 1
    chunk_index = cfg.get("CHUNK_INDEX")
    rows, tag = _stride_chunk(rows, chunks, chunk_index)

    subset = cfg.get("SUBSET")
    if subset is not None:
        rows = rows[: int(subset)]

    cfg = dict(cfg)
    cfg["DATASET"] = DATASET_NAME
    stem = cfg.get("OUT_STEM", "hsearch_solved1hop")
    if kind:
        stem = f"{stem}_kind-{kind}"
    if tag:
        stem = f"{stem}{tag}"
    cfg["OUT_STEM"] = stem

    budget = cfg["NODE_BUDGET"]
    mrl = cfg["MAX_RELATOR_LENGTH"]
    arms = list(cfg["ARMS"])
    keep_path = cfg.get("KEEP_PATH", True)
    engine = cfg.get("ENGINE", "hsolve")
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
    # Presentation-major: finish every arm on row i before starting row i+1.
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
             if n_workers > 1 else ""))
    print(f"  {len(seen)} rows resumed; {len(todo)} to run")
    print(f"  -> {out}", flush=True)

    # Always use the pool path (n_workers>=1) so we do not re-implement serial.
    n_workers = max(int(n_workers), 1)
    run_ab._run_parallel(cfg, out, todo, n_workers, budget, mrl, engine,
                         keep_path, heartbeat_secs, progress_secs)
    _report_complete_rows(out, cfg)
    return out
