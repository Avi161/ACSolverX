"""Branch-A (No-CoV) sweep runner: combined benchmark x z-word families.

For each row ``<x,y | r1, r2>`` of the combined benchmark and each word ``w``
from the chosen family, solve ``<x,y,z | r1, r2, Z.w>`` (``nocov_presentation``)
with the general-n greedy solver and append one jsonl row per (row, word) job.

The harness discipline is ``run_baseline.py``'s, reused by import where it can
be: date-less filename identity + glob resume (lessons:
jsonl-filename-encodes-search-identity, date-in-filename-broke-resume),
``_repair_jsonl`` before any append, fsync every row, Drive staging with
whole-file mirroring, and a minimal inline W&B layer that only ever logs on a
monotone step (lesson: wandb-step-must-be-monotonic).

CPU + numba only. From the repo root::

    .venv/bin/python3 -m experiments.stable_ac.nocov.run_nocov
"""

import glob
import json
import os
import re
import time
from datetime import datetime

from experiments.analysis.combined_benchmark import load_combined
from experiments.run_baseline import (
    _copy_file, _is_remote, _persist, _repair_jsonl, _seed_stage,
)
from experiments.stable_ac.solvern import (
    nocov_presentation, search_n, word_to_str,
)
from experiments.stable_ac.word_families import build_family

DEFAULT_CONFIG = {
    "BENCHMARK": "combined_11",      # results/benchmark/combined/benchmark_{...}.json
    "FAMILIES": ["A1", "A2", "A3"],  # used by main()/the notebook loop only
    "MODE": "nocov",                 # row tag + part of the filename identity
    "MAX_RELATOR_LENGTH": 64,        # per-relator cap (no total-length budget)
    "CYCLIC_REDUCE": True,

    # z-word family knobs (see word_families.build_family)
    "A1_WORDS": None,                # None -> A1_DEFAULT_WORDS
    "A2_MAX_WORDS": None,            # cap the A2 prefix family (it dominates cost)
    "A2_DROP_LEN1": False,
    "A3_GRID": [0.25, 0.5, 0.75, 1.0],

    "RESUME": True,
    "PATH_IN_SEPARATE_FILE": True,   # solved paths (moves only) -> *_paths.jsonl

    # Job selection for smoke runs. These change WHICH jobs exist, not what any
    # one job computes, so they stay OUT of the filename identity: resume is
    # keyed per (name, z_word) row, so a partial file stays valid across them.
    "ROW_LIMIT": None,               # first N benchmark rows
    "WORD_LIMIT": None,              # first N words per row
    "NAMES": None,                   # filter benchmark rows by name

    # output
    "LOCAL_OUT_DIR": "results/stable_ac/nocov",
    "DRIVE_OUT_DIR": "/content/drive/MyDrive/acsolverx_results/stable_ac/nocov",
    "MOUNT_DRIVE": False,

    "PROGRESS_EVERY": 25,            # print a status line every N jobs

    # W&B. None of these change the search, so none enter the filename identity.
    "USE_WANDB": False,
    "WANDB_ENTITY": "avigyapaudel045-aisc",
    "WANDB_PROJECT": "acsolver",
    "WANDB_JOB_TYPE": "stable_ac_nocov",
    "WANDB_GROUP": None,             # None -> "{benchmark}-nocov-mrl{cap}-{cyc}"
    "WANDB_RUN_NAME": None,          # None -> "A1 · 50000 · combined_11 · nocov"
    "WANDB_TAGS": None,
    "WANDB_NOTES": None,
    "WANDB_MODE": "online",
}

# Whole-file mirror cadence when the output dir is a network mount.
# Result-neutral, so a constant rather than a config knob.
_MIRROR_EVERY_S = 60


def _require_budget_allowed(budgets):
    """Local-safety guard: a budget > 1000 needs ACSOLVERX_ALLOW_BIG=1.

    Production budgets belong on Colab (the notebook RUN cell sets the env
    var); a local invocation that forgot ROW_LIMIT would otherwise burn hours.
    """
    big = [b for b in budgets if b > 1000]
    if big and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(
            f"refusing node budget(s) {big} > 1000: local runs stay small; "
            f"set ACSOLVERX_ALLOW_BIG=1 to confirm a production (Colab) run")


def _run_prefix(cfg, node_budget, family):
    """Date-less filename stem covering every knob that changes a job's result.

    Mode, benchmark id, family, budget, cap and cyclic_reduce all change what a
    search computes, so all are encoded. Deliberately absent: the date (it must
    never gate resume), W&B/PROGRESS/RESUME (result-neutral), and
    ROW_LIMIT/WORD_LIMIT/NAMES + the family knobs (A1_WORDS/A2_*/A3_GRID) —
    those change which jobs exist, not what any one job computes, and resume is
    row-keyed on (name, z_word), so a partial file stays valid across them.
    """
    cyc = "cyc" if cfg["CYCLIC_REDUCE"] else "noncyc"
    return (f"{cfg['MODE']}_{cfg['BENCHMARK']}_{family}_{node_budget}"
            f"_mrl{cfg['MAX_RELATOR_LENGTH']}_{cyc}_")


def _resolve_paths(cfg, node_budget, family):
    out_dir = cfg["DRIVE_OUT_DIR"] if cfg["MOUNT_DRIVE"] else cfg["LOCAL_OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(cfg, node_budget, family)
    stem = prefix + datetime.now().strftime("%m_%d_%y")

    # Resume is date-agnostic: reattach to the existing file with the MOST
    # rows, whatever day it was started; only create a fresh dated file when
    # none exists (lesson: date-in-filename-broke-resume).
    if cfg.get("RESUME", True):
        existing = [p for p in glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
                    if not p.endswith("_paths.jsonl")]
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]

    out_path = os.path.join(out_dir, stem + ".jsonl")
    paths_path = os.path.join(out_dir, stem + "_paths.jsonl")
    return out_path, paths_path, prefix


def _read_done(out_path):
    """({(name, z_word)}, n_seen, n_solved, cum_nodes) from an existing jsonl.

    Tolerates an unparseable FINAL line (an unrepaired torn write) so resume
    never crashes on it; a bad line anywhere else is real corruption and is
    raised rather than silently re-running that job (matches run_baseline).
    """
    done, n_seen, n_solved, cum_nodes = set(), 0, 0, 0
    if not os.path.exists(out_path):
        return done, n_seen, n_solved, cum_nodes
    with open(out_path) as f:
        lines = [ln.strip() for ln in f]
    for i, ln in enumerate(lines):
        if not ln:
            continue
        try:
            row = json.loads(ln)
        except ValueError:
            if i == len(lines) - 1:
                print(f"    WARNING: ignoring a truncated final line in "
                      f"{os.path.basename(out_path)}", flush=True)
                break
            raise
        done.add((row["name"], row["z_word"]))
        n_seen += 1
        n_solved += int(bool(row.get("solved")))
        cum_nodes += row.get("nodes_explored") or 0
    return done, n_seen, n_solved, cum_nodes


def _read_paths_done(paths_path):
    """(name, z_word) keys already in the paths file (keeps appends idempotent)."""
    keys = set()
    if os.path.exists(paths_path):
        with open(paths_path) as f:
            for ln in f:
                if ln.strip():
                    row = json.loads(ln)
                    keys.add((row["name"], row["z_word"]))
    return keys


def _benchmark_rows(cfg):
    """Combined-benchmark rows after the NAMES filter and the ROW_LIMIT slice."""
    combined_id = int(cfg["BENCHMARK"].rsplit("_", 1)[1])
    rows = load_combined(combined_id)["rows"]
    if cfg.get("NAMES"):
        wanted = set(cfg["NAMES"])
        rows = [r for r in rows if r["name"] in wanted]
    if cfg.get("ROW_LIMIT"):
        rows = rows[:cfg["ROW_LIMIT"]]
    return rows


def _build_jobs(cfg, family):
    """One job per (benchmark row, z-word), in deterministic order."""
    jobs = []
    for brow in _benchmark_rows(cfg):
        words = build_family(family, [brow["r1"], brow["r2"]], cfg)
        if cfg.get("WORD_LIMIT"):
            words = words[:cfg["WORD_LIMIT"]]
        jobs.extend((brow, w) for w in words)
    return jobs


# Baseline passthrough per source, so analysis compares without a join back
# into the benchmark file.
_LADDER_PASSTHROUGH = ("baseline_nodes_at_50k", "baseline_path_at_50k",
                       "baseline_solved_at_50k")

_GIT_COMMIT = False   # False = not yet resolved (None is a valid answer)


def _git_commit():
    """HEAD of the checkout this module runs from; None outside a git repo.

    Provenance only — which code produced a row. Deliberately NOT part of the
    filename/resume identity: rows appended after a code update record the
    new commit in the same file, which is exactly the audit trail wanted.
    """
    global _GIT_COMMIT
    if _GIT_COMMIT is False:
        import subprocess
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True, text=True, timeout=10,
            )
            _GIT_COMMIT = out.stdout.strip() or None
        except Exception:
            _GIT_COMMIT = None
    return _GIT_COMMIT


def _build_row(cfg, node_budget, family, brow, z_word, z_relator, pres, stats,
               elapsed):
    row = {
        "name": brow["name"],
        "source": brow["source"],
        "pres_id": brow.get("pres_id"),      # null for reach rows
        "r1": brow["r1"],
        "r2": brow["r2"],
        "base_total_length": brow["base_total_length"],
        "z_word": z_word,
        "z_relator": z_relator,
        "w_family": family,
        "mode": cfg["MODE"],
        "n_gen": pres.n_gen,
        "n_rel": pres.n_rel,
        "benchmark": cfg["BENCHMARK"],
        "node_budget": node_budget,
        "max_relator_length_cap": cfg["MAX_RELATOR_LENGTH"],
        "cyclic_reduce": cfg["CYCLIC_REDUCE"],
        "nodes_explored": stats["nodes_explored"],
        "solved": stats["solved"],
        "path_length": stats["path_length"],
        "min_relator_length": stats["min_relator_length"],
        "min_relator": stats["min_relator"],
        "max_relator_length": stats["max_relator_length"],
        "max_relator": stats["max_relator"],
        "max_relator_length_expanded": stats["max_relator_length_expanded"],
        "max_relator_expanded": stats["max_relator_expanded"],
        "time_seconds": round(elapsed, 4),
        "git_commit": _git_commit(),
    }
    if "tier" in brow:                       # a future benchmark may carry one
        row["tier"] = brow["tier"]
    if brow["source"] == "ladder":
        for k in _LADDER_PASSTHROUGH:
            row[k] = brow.get(k)
    else:
        row["bar_to_beat"] = brow.get("bar_to_beat")
        row["start_length"] = brow.get("baseline_start_length")
        row["aut_min_rep_r1"] = brow.get("aut_min_rep_r1")
        row["aut_min_rep_r2"] = brow.get("aut_min_rep_r2")
    return row


def _wandb_start(cfg, node_budget, family, prefix):
    """Minimal inline W&B (deliberately NOT wandb_tracking.LiveLogger, whose
    pres_id step metric does not fit a presentation x word sweep).

    The run id derives from the date-less filename prefix, so a Colab
    disconnect reattaches to the same run (resume="allow"). run/* keys ride a
    monotone ``n_processed`` step metric and nothing ever passes ``step=``
    (lesson: wandb-step-must-be-monotonic).
    """
    import wandb

    run_id = re.sub(r"[^A-Za-z0-9_-]", "-", prefix.rstrip("_"))
    cap, cyc = cfg["MAX_RELATOR_LENGTH"], cfg["CYCLIC_REDUCE"]
    group = cfg["WANDB_GROUP"] or (
        f"{cfg['BENCHMARK']}-nocov-mrl{cap}-{'cyc' if cyc else 'noncyc'}")
    name = cfg["WANDB_RUN_NAME"] or (
        f"{family} · {node_budget} · {cfg['BENCHMARK']} · nocov")
    config = {
        "mode": cfg["MODE"], "benchmark": cfg["BENCHMARK"], "family": family,
        "node_budget": node_budget, "max_relator_length_cap": cap,
        "cyclic_reduce": cyc, "a1_words": cfg["A1_WORDS"],
        "a2_max_words": cfg["A2_MAX_WORDS"],
        "a2_drop_len1": cfg["A2_DROP_LEN1"], "a3_grid": cfg["A3_GRID"],
    }
    run = wandb.init(
        entity=cfg["WANDB_ENTITY"], project=cfg["WANDB_PROJECT"], id=run_id,
        name=name, group=group, job_type=cfg["WANDB_JOB_TYPE"],
        tags=cfg["WANDB_TAGS"], notes=cfg["WANDB_NOTES"],
        mode=cfg["WANDB_MODE"], resume="allow", config=config)
    run.define_metric("n_processed")
    run.define_metric("run/*", step_metric="n_processed")
    return run, run_id


def _wandb_finish(run, run_id, out_path, paths_path, total_time):
    import wandb

    with open(out_path) as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    n_solved = sum(bool(r["solved"]) for r in rows)
    run.summary.update({
        "n_rows": len(rows),
        "n_solved": n_solved,
        "solve_rate": n_solved / max(len(rows), 1),
        # the headline reach signal: a reach row solved is a NEW solution
        "newly_solved_reach": sum(
            1 for r in rows if r["source"] == "reach" and r["solved"]),
        "cum_nodes": sum(r.get("nodes_explored") or 0 for r in rows),
        "total_time": total_time,
    })
    cols = ["name", "source", "z_word", "w_family", "solved", "nodes_explored",
            "path_length", "min_relator_length"]
    run.log({"tables/results": wandb.Table(
        columns=cols, data=[[r.get(c) for c in cols] for r in rows])})
    art = wandb.Artifact(run_id, type="stable_ac_nocov_results")
    art.add_file(out_path)
    if os.path.exists(paths_path):
        art.add_file(paths_path)
    run.log_artifact(art)
    run.finish()


def run_nocov(cfg, node_budget, family):
    """Run one (budget, family) sweep over the combined benchmark.

    One jsonl per (budget, family); crash-safe (fsync every row); resumable via
    the (name, z_word) keys already in the file. Returns the output jsonl path
    (the mirror path when the output lives on Drive).
    """
    cfg = {**DEFAULT_CONFIG, **cfg}
    _require_budget_allowed([node_budget])

    jobs = _build_jobs(cfg, family)
    out_path, paths_path, prefix = _resolve_paths(cfg, node_budget, family)

    # Drive staging (run_baseline's pattern, simplified): local disk is
    # authoritative; the mount only ever receives a whole-file copy, because
    # its long-idle append handles silently drop rows. A resumed run lands on a
    # FRESH VM whose staging file is gone, so seed it from the mirror before
    # anything reads `done`.
    mirror = []
    if _is_remote(out_path):
        stage_dir = os.path.join(cfg["LOCAL_OUT_DIR"], "_stage")
        os.makedirs(stage_dir, exist_ok=True)
        stage_out = os.path.join(stage_dir, os.path.basename(out_path))
        stage_paths = os.path.join(stage_dir, os.path.basename(paths_path))
        _seed_stage(stage_out, out_path)
        _seed_stage(stage_paths, paths_path)
        mirror = [(stage_out, out_path), (stage_paths, paths_path)]
        print(f"    durable output: appending to {stage_dir} (local disk), "
              f"mirroring to {os.path.dirname(out_path)} every "
              f"{_MIRROR_EVERY_S}s", flush=True)
        out_path, paths_path = stage_out, stage_paths

    last_mirror = [time.time()]

    def _mirror_all(force=False):
        """Copy the staging files onto the mount. No-op when output is local."""
        if not mirror:
            return
        now = time.time()
        if not force and now - last_mirror[0] < _MIRROR_EVERY_S:
            return
        last_mirror[0] = now
        for local, remote in mirror:
            if os.path.exists(local):
                _copy_file(local, remote)

    # Before ANY reader or the append handles below touch these files. Not
    # gated on RESUME: a non-resumed run still opens them "a" and would
    # concatenate its first row onto a leftover stub.
    _repair_jsonl(out_path)
    _repair_jsonl(paths_path)

    if cfg["RESUME"]:
        done, n_seen, n_solved, cum_nodes = _read_done(out_path)
        paths_done = _read_paths_done(paths_path)
    else:
        done, n_seen, n_solved, cum_nodes = set(), 0, 0, 0
        paths_done = set()

    todo = [(brow, w) for brow, w in jobs if (brow["name"], w) not in done]
    n_todo = len(todo)
    print(f"=== nocov | {family} | budget={node_budget} | {len(jobs)} jobs | "
          f"{len(done)} already done, {n_todo} to run | -> {out_path}",
          flush=True)
    if n_todo == 0:
        print("    nothing to do (all done).", flush=True)

    run, run_id = None, None
    if cfg["USE_WANDB"]:
        run, run_id = _wandb_start(cfg, node_budget, family, prefix)
    n_processed = n_seen         # monotone W&B step, seeded from prior rows

    every = max(1, int(cfg["PROGRESS_EVERY"]))
    total_time = 0.0
    t_start = time.time()
    processed = 0
    out_f = open(out_path, "a")
    paths_f = open(paths_path, "a") if cfg["PATH_IN_SEPARATE_FILE"] else None
    try:
        for brow, w in todo:
            pres = nocov_presentation(brow["r1"], brow["r2"], w)
            z_relator = word_to_str(pres.relators[-1])   # "Z"+w, as searched
            t0 = time.time()
            stats = search_n(pres, node_budget,
                             cap=cfg["MAX_RELATOR_LENGTH"],
                             cyclic=cfg["CYCLIC_REDUCE"])
            elapsed = time.time() - t0
            total_time += elapsed

            row = _build_row(cfg, node_budget, family, brow, w, z_relator,
                             pres, stats, elapsed)
            out_f.write(json.dumps(row) + "\n")
            _persist(out_f)

            key = (brow["name"], w)
            if paths_f is not None and stats["solved"] and key not in paths_done:
                # Moves only — replay (solvern.moves_to_states) is the decoder.
                paths_f.write(json.dumps({
                    "name": brow["name"], "z_word": w, "r1": brow["r1"],
                    "r2": brow["r2"], "z_relator": z_relator,
                    "path_moves": stats["path_moves"]}) + "\n")
                _persist(paths_f)
                paths_done.add(key)
            _mirror_all()

            processed += 1
            n_seen += 1
            n_solved += int(bool(stats["solved"]))
            cum_nodes += stats["nodes_explored"]
            n_processed += 1
            nps = stats["nodes_explored"] / elapsed if elapsed > 0 else 0.0
            if run is not None:
                run.log({"n_processed": n_processed,
                         "run/solve_rate": n_solved / max(n_seen, 1),
                         "run/n_solved": n_solved,
                         "run/cum_nodes": cum_nodes,
                         "run/nodes_per_s": nps})
            if processed % every == 0 or processed == n_todo:
                wall = time.time() - t_start
                print(f"    [{family}@{node_budget}] {processed}/{n_todo} | "
                      f"{brow['name']} · z={w!r} | solved {n_solved}/{n_seen} | "
                      f"{nps:,.0f} nodes/s | {wall:.0f}s elapsed", flush=True)
    finally:
        out_f.close()
        if paths_f is not None:
            paths_f.close()
        # A Ctrl-C must still push this session's rows onto the mount: the
        # staging disk dies with the VM.
        _mirror_all(force=True)

    if run is not None:
        _wandb_finish(run, run_id, out_path, paths_path, total_time)

    final_path = mirror[0][1] if mirror else out_path
    print(f"[{final_path}] {n_seen} jobs, {n_solved} solved "
          f"({n_solved / max(n_seen, 1):.1%}).", flush=True)
    return final_path


def main():
    """Read config_nocov.yaml (next to this file) and run every (budget, family)."""
    import yaml

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "config_nocov.yaml")) as f:
        cfg = yaml.safe_load(f)
    _require_budget_allowed(cfg["BUDGET"])   # fail fast, before any file I/O
    for budget in cfg["BUDGET"]:
        for family in cfg["FAMILIES"]:
            run_nocov(cfg, budget, family)


if __name__ == "__main__":
    main()
