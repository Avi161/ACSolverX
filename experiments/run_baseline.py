"""Baseline greedy pipeline runner — data load, jsonl (resumable), W&B.

CPU + numba only. Run from the ACSolverX repo root (data paths are relative).
The heavy lifting is in ``experiments.search.greedy_baseline``; this module is
just the experiment harness around it.
"""

import ast
import hashlib
import json
import os
from datetime import datetime

from experiments.search.greedy_baseline import greedy_search


# Integer encoding of data/ms640_solved.txt: 1=x, -1=X, 2=y, -2=Y, 0=pad.
_INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


DEFAULT_CONFIG = {
    "DATASET": "data/ms640_solved.txt",
    "SUBSET": None,                  # None=all, list[int] of pres_id, or (start, end)
    "MAX_RELATOR_LENGTH": 24,        # per-relator cap
    "CYCLIC_REDUCE": True,

    # jsonl field toggles
    "use_min_relator_length": True,
    "use_min_relator": True,
    "use_max_relator_length": True,
    "use_max_relator": True,
    "use_max_relator_expanded": True,   # longest presentation actually popped/expanded (length + relator)
    "use_time": True,
    "use_path": True,
    "PATH_IN_SEPARATE_FILE": True,

    "RESUME": True,

    # output
    "MOUNT_DRIVE": False,
    "DRIVE_OUT_DIR": "/content/drive/MyDrive/acsolverx_results/greedy_baseline",
    "LOCAL_OUT_DIR": "results/greedy_baseline",

    # W&B
    "USE_WANDB": False,
    "WANDB_ENTITY": "avigyapaudel045-aisc",   # writable team entity (org-managed acct; None = account default)
    "WANDB_PROJECT": "acsolver",
    "WANDB_MODE": "online",
    "WANDB_GROUP": None,             # default set at runtime to greedy_baseline_{date}

    "PROGRESS_EVERY": 10,            # print a status line every N processed presentations
}


def int_line_to_relators(line_ints):
    """A 48-int ms640 line -> (r1_str, r2_str) in the xXyY alphabet."""
    half = len(line_ints) // 2
    r1 = ''.join(_INT_TO_CHAR[t] for t in line_ints[:half] if t != 0)
    r2 = ''.join(_INT_TO_CHAR[t] for t in line_ints[half:] if t != 0)
    return r1, r2


def load_dataset(path, subset=None):
    """Yield (pres_id, r1_str, r2_str) for the selected presentations.

    Parsing matches envs/ac_s.py:initiate_states (literal_eval per line).
    ``subset``: None=all, list[int] of pres_ids, or (start, end) half-open range.
    """
    with open(path, "r") as f:
        lines = [ast.literal_eval(ln.strip()) for ln in f if ln.strip()]

    if subset is None:
        ids = range(len(lines))
    elif isinstance(subset, tuple):
        ids = range(subset[0], subset[1])
    else:
        ids = subset

    for pres_id in ids:
        r1, r2 = int_line_to_relators(lines[pres_id])
        yield pres_id, r1, r2


def _subset_tag(subset):
    """A short, collision-safe tag identifying WHICH presentations ran.

    ``n_pres`` alone is ambiguous (e.g. SUBSET=(0,5) and SUBSET=[10,20,30,40,50]
    both have 5), so different subsets could otherwise share a filename. This
    encodes the actual selection: 'all' / a range / a hash of an explicit list.
    """
    if subset is None:
        return "all"
    if isinstance(subset, tuple):
        return f"{subset[0]}-{subset[1]}"
    # Explicit list: order-independent hash of its members.
    key = ",".join(str(i) for i in sorted(subset))
    return "ids" + hashlib.sha1(key.encode()).hexdigest()[:8]


def _run_tag(cfg, node_budget, n_pres, date):
    """Filename/run-id stem covering every knob that changes the search result.

    Two runs collide (share a file, and resume-merge) ONLY if they are truly
    the same experiment. Search-affecting knobs (cap, cyclic_reduce) and the
    subset selection are all encoded; jsonl field toggles are intentionally
    excluded (they change stored columns, not the computed result, and resume
    correctly reuses those rows).
    """
    cyc = "cyc" if cfg["CYCLIC_REDUCE"] else "noncyc"
    tag = _subset_tag(cfg["SUBSET"])
    return (f"greedy_{node_budget}_{n_pres}_mrl{cfg['MAX_RELATOR_LENGTH']}"
            f"_{cyc}_{tag}_{date}")


def _resolve_paths(cfg, node_budget, n_pres):
    out_dir = cfg["DRIVE_OUT_DIR"] if cfg["MOUNT_DRIVE"] else cfg["LOCAL_OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    date = datetime.now().strftime("%m_%d_%y")
    stem = _run_tag(cfg, node_budget, n_pres, date)
    out_path = os.path.join(out_dir, stem + ".jsonl")
    paths_path = os.path.join(out_dir, stem + "_paths.jsonl")
    return out_path, paths_path, date, stem


def _read_done(out_path):
    """(done_ids, n_seen, n_solved) reconstructed from an existing jsonl."""
    done, n_seen, n_solved = set(), 0, 0
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                row = json.loads(ln)
                done.add(row["pres_id"])
                n_seen += 1
                n_solved += int(bool(row.get("solved")))
    return done, n_seen, n_solved


def _build_row(cfg, pres_id, r1, r2, node_budget, stats, elapsed):
    row = {
        "pres_id": pres_id,
        "r1": r1,
        "r2": r2,
        "node_budget": node_budget,
        "max_relator_length_cap": cfg["MAX_RELATOR_LENGTH"],
        "cyclic_reduce": cfg["CYCLIC_REDUCE"],
        "nodes_explored": stats["nodes_explored"],
        "solved": stats["solved"],
        "path_length": stats["path_length"],
    }
    if cfg["use_min_relator_length"]:
        row["min_relator_length"] = stats["min_relator_length"]
    if cfg["use_min_relator"]:
        row["min_relator"] = stats["min_relator"]
    if cfg["use_max_relator_length"]:
        row["max_relator_length"] = stats["max_relator_length"]
    if cfg["use_max_relator"]:
        row["max_relator"] = stats["max_relator"]
    if cfg["use_max_relator_expanded"]:
        row["max_relator_length_expanded"] = stats["max_relator_length_expanded"]
        row["max_relator_expanded"] = stats["max_relator_expanded"]
    if cfg["use_time"]:
        row["time_seconds"] = round(elapsed, 4)
    if cfg["use_path"] and not cfg["PATH_IN_SEPARATE_FILE"]:
        row["path"] = stats["path"]
    return row


def run_dataset(cfg, node_budget):
    """Run the baseline greedy over the dataset at one node budget.

    Writes one jsonl per budget (crash-safe: flush every row). Resumable via
    the pres_id set already present in the output file.
    """
    import time

    cfg = {**DEFAULT_CONFIG, **cfg}
    presentations = list(load_dataset(cfg["DATASET"], cfg["SUBSET"]))
    n_pres = len(presentations)
    out_path, paths_path, date, stem = _resolve_paths(cfg, node_budget, n_pres)

    if cfg["RESUME"]:
        done, n_seen, n_solved = _read_done(out_path)
    else:
        done, n_seen, n_solved = set(), 0, 0

    run = None
    table = None
    if cfg["USE_WANDB"]:
        import wandb
        group = cfg["WANDB_GROUP"] or f"greedy_baseline_{date}"
        # Same collision-safe identity as the jsonl file (W&B ids allow these chars).
        run_id = stem
        run = wandb.init(
            entity=cfg["WANDB_ENTITY"] or None, project=cfg["WANDB_PROJECT"],
            id=run_id, name=run_id, resume="allow",
            group=group, job_type="greedy_baseline", mode=cfg["WANDB_MODE"],
            config={
                "node_budget": node_budget,
                "max_relator_length": cfg["MAX_RELATOR_LENGTH"],
                "cyclic_reduce": cfg["CYCLIC_REDUCE"],
                "dataset": cfg["DATASET"], "n_pres": n_pres,
                "subset": str(cfg["SUBSET"]),
            },
        )
        table = wandb.Table(columns=[
            "pres_id", "r1", "r2", "node_budget", "max_relator_length_cap",
            "cyclic_reduce", "nodes_explored", "solved", "path_length",
            "min_relator_length", "max_relator_length",
        ])
        # Rebuild the Table from any already-written rows (resume).
        if os.path.exists(out_path):
            with open(out_path) as f:
                for ln in f:
                    ln = ln.strip()
                    if ln:
                        _add_table_row(table, json.loads(ln))

    todo = [(pid, r1, r2) for (pid, r1, r2) in presentations if pid not in done]
    n_todo = len(todo)
    every = max(1, int(cfg["PROGRESS_EVERY"]))
    print(f"=== budget={node_budget} | {n_pres} presentations | "
          f"{len(done)} already done, {n_todo} to run | -> {out_path}",
          flush=True)
    if n_todo == 0:
        print("    nothing to do (all done). ", flush=True)

    total_time = 0.0
    t_start = time.time()
    processed = 0
    out_f = open(out_path, "a")
    paths_f = open(paths_path, "a") if cfg["PATH_IN_SEPARATE_FILE"] else None
    try:
        for pres_id, r1, r2 in todo:
            t0 = time.time()
            stats = greedy_search(
                r1, r2, node_budget,
                max_relator_length=cfg["MAX_RELATOR_LENGTH"],
                cyclic_reduce=cfg["CYCLIC_REDUCE"],
            )
            elapsed = time.time() - t0
            total_time += elapsed

            row = _build_row(cfg, pres_id, r1, r2, node_budget, stats, elapsed)
            out_f.write(json.dumps(row) + "\n")
            out_f.flush()
            if cfg["PATH_IN_SEPARATE_FILE"] and cfg["use_path"] and stats["solved"]:
                paths_f.write(json.dumps({"pres_id": pres_id, "path": stats["path"]}) + "\n")
                paths_f.flush()

            n_seen += 1
            n_solved += int(stats["solved"])
            processed += 1
            if run is not None:
                run.log({"solve_rate": n_solved / max(n_seen, 1)}, step=pres_id)
                _add_table_row(table, row)

            if processed % every == 0 or processed == n_todo:
                wall = time.time() - t_start
                rate = processed / wall if wall > 0 else 0.0
                eta = (n_todo - processed) / rate if rate > 0 else 0.0
                print(f"    [{node_budget}] {processed}/{n_todo} | "
                      f"solved {n_solved}/{n_seen} ({n_solved / max(n_seen, 1):.1%}) | "
                      f"pres {pres_id}: {'ok' if stats['solved'] else 'unsolved'} "
                      f"nodes={stats['nodes_explored']} | "
                      f"{wall:.0f}s elapsed, ETA {eta:.0f}s ({rate:.1f}/s)",
                      flush=True)
    finally:
        out_f.close()
        if paths_f is not None:
            paths_f.close()

    if run is not None:
        _finish_wandb(run, table, out_path, paths_path, run_id,
                      n_seen, n_solved, total_time, cfg)

    print(f"[{out_path}] {n_seen} presentations, {n_solved} solved "
          f"({n_solved / max(n_seen, 1):.1%}).")
    return out_path


def _add_table_row(table, row):
    table.add_data(
        row["pres_id"], row["r1"], row["r2"], row["node_budget"],
        row.get("max_relator_length_cap"), row.get("cyclic_reduce"),
        row["nodes_explored"], row["solved"], row["path_length"],
        row.get("min_relator_length"), row.get("max_relator_length"),
    )


def _finish_wandb(run, table, out_path, paths_path, run_id,
                  n_seen, n_solved, total_time, cfg):
    import statistics
    import wandb

    # Recompute headline aggregates from the full jsonl (source of truth).
    nodes_all, nodes_solved, paths_solved = [], [], []
    scatter_pts = []  # (nodes_explored, path_length) for solved presentations
    with open(out_path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            row = json.loads(ln)
            nodes_all.append(row["nodes_explored"])
            if row["solved"]:
                nodes_solved.append(row["nodes_explored"])
                if row["path_length"] is not None:
                    paths_solved.append(row["path_length"])
                    scatter_pts.append([row["nodes_explored"], row["path_length"]])

    def _mean(xs):
        return statistics.fmean(xs) if xs else None

    def _median(xs):
        return statistics.median(xs) if xs else None

    run.summary["n_pres"] = n_seen
    run.summary["n_solved"] = n_solved
    run.summary["solve_rate"] = n_solved / max(n_seen, 1)
    run.summary["nodes_explored_mean"] = _mean(nodes_all)
    run.summary["nodes_explored_solved_mean"] = _mean(nodes_solved)
    run.summary["path_length_mean"] = _mean(paths_solved)
    run.summary["path_length_median"] = _median(paths_solved)
    run.summary["total_time_s"] = round(total_time, 2)

    run.log({"results": table})

    # Auto-rendered graphs (the two headline metrics as distributions).
    panels = {}
    if nodes_all:
        panels["nodes_explored_hist"] = wandb.Histogram(nodes_all)
    if paths_solved:
        panels["path_length_hist"] = wandb.Histogram(paths_solved)
    if scatter_pts:
        _sc = wandb.Table(data=scatter_pts, columns=["nodes_explored", "path_length"])
        panels["nodes_vs_path"] = wandb.plot.scatter(
            _sc, "nodes_explored", "path_length",
            title="nodes explored vs path length (solved)")
    if panels:
        run.log(panels)

    art = wandb.Artifact(run_id, type="results")
    art.add_file(out_path)
    if cfg["PATH_IN_SEPARATE_FILE"] and os.path.exists(paths_path):
        art.add_file(paths_path)
    run.log_artifact(art)
    run.finish()
