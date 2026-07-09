"""Offline end-to-end check of the new W&B layer. No network, no API key.

    .venv/bin/python3 tests/wandb_offline_integration.py <phase>

Phases run as separate processes so `resume` is exercised the way it happens in
Colab (a fresh interpreter reattaching to an existing jsonl), not via leftover
in-process state.

wandb 0.28 offline does NOT write files/config.yaml or wandb-summary.json -- the
history lives in the binary .wandb transaction log. So identity and summary are
asserted on the live run object, the panel set is asserted by rebuilding it from
the real jsonl, and `files/media/` existing proves run.log(panels) serialized.
"""
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ["WANDB_SILENT"] = "true"

OUT = ".scratch/verify_out"
os.makedirs(".scratch", exist_ok=True)
BUDGET = 5000
# idx 620-639 of ms640 is a deliberate mix: most solve, several are still
# unsolved at 20k nodes. A trivial all-solve subset would leave the unsolved
# histogram and censored_fraction empty and prove nothing.
CFG = {
    "DATASET": "data/ms640_solved.txt",
    "SUBSET": (620, 640),
    "MAX_RELATOR_LENGTH": 24,
    "CYCLIC_REDUCE": True,
    "LOCAL_OUT_DIR": OUT,
    "MOUNT_DRIVE": False,
    "USE_WANDB": True,
    "WANDB_MODE": "offline",
    "WANDB_ENTITY": None,
    "WANDB_PROJECT": "acsolver",
    "PROGRESS_EVERY": 20,
    "WANDB_PATH_PROFILES": 4,
}

EXPECTED_PANELS = {
    "profile/solve_rate_vs_budget",
    "difficulty/solve_rate_by_initial_length",
    "difficulty/median_nodes_by_initial_length",
    "difficulty/initial_length_vs_nodes",
    "dist/nodes_explored_solved",
    "dist/nodes_explored_unsolved",
    "dist/path_length",
    "dist/time_seconds",
    "dist/nodes_per_s",
    "hump/overshoot_hist",
    "hump/path_overshoot_hist",
    "hump/path_peak_position_hist",
    "hump/peak_vs_initial",
    "hump/path_profile",
    "unsolved/closest_approach_hist",
    "perf/nodes_per_s_vs_initial_length",
    "rel/nodes_vs_path",
}


def _run(**over):
    from experiments.run_baseline import run_dataset
    return run_dataset({**CFG, **over}, node_budget=BUDGET)


def _latest_offline_dir():
    return sorted(glob.glob("wandb/offline-run-*"), key=os.path.getmtime)[-1]


def _paths_for(out):
    return out[: -len(".jsonl")] + "_paths.jsonl"


def phase_fresh():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.rmtree("wandb", ignore_errors=True)
    out = _run()
    rows = [json.loads(l) for l in open(out)]
    solved = [r for r in rows if r["solved"]]
    assert len(rows) == 20, f"expected 20 rows, got {len(rows)}"
    assert 0 < len(solved) < 20, (
        f"need a solved/unsolved mix to exercise every panel; got {len(solved)}/20")

    media = f"{_latest_offline_dir()}/files/media"
    assert os.path.isdir(media), "no media dir: run.log(panels) never serialized"
    n_media = sum(len(fs) for _, _, fs in os.walk(media))
    assert n_media > 0, "media dir is empty"
    print(f"FRESH ok: {len(rows)} rows, {len(solved)} solved, "
          f"{20 - len(solved)} unsolved | {n_media} media files written")
    open(".scratch/_out_path", "w").write(out)
    open(".scratch/_run_id", "w").write(_latest_offline_dir().split("-", 3)[-1])


def phase_panels():
    """Rebuild exactly what finish_run logs, from the real jsonl."""
    from experiments.wandb_tracking import (
        build_panels, canonical_initial_length, compute_analytics, read_jsonl)

    out = open(".scratch/_out_path").read()
    rows = read_jsonl(out)
    path_rows = read_jsonl(_paths_for(out))
    n_solved = sum(r["solved"] for r in rows)
    a = compute_analytics(rows, path_rows, CFG, BUDGET, len(rows), n_solved, 1.0,
                          canon_len_fn=canonical_initial_length)
    panels = build_panels(a)

    missing = EXPECTED_PANELS - set(panels)
    extra = set(panels) - EXPECTED_PANELS
    assert not missing, f"panels missing: {sorted(missing)}"
    assert not extra, f"unexpected panels: {sorted(extra)}"

    s = a["summary"]
    assert s["solve_rate"] == n_solved / len(rows)
    assert s["censored_fraction"] == 1 - s["solve_rate"]
    assert s["timing_regime"] == "uniform"
    assert s["solve_rate_at_1k"] <= s["solve_rate_at_5k"] == s["solve_rate"]
    assert "solve_rate_at_10k" not in s, "reported a solve rate above node_budget"

    pts = a["profile_points"]
    assert pts[0] == [0, 0.0] and pts[-1][0] == BUDGET
    assert all(b[1] >= x[1] for x, b in zip(pts, pts[1:])), "profile not monotone"
    assert pts[-1][1] == s["solve_rate"], "profile plateau != final solve rate"

    # Every unsolved run must have spent exactly the budget (right-censoring).
    assert all(v == BUDGET for v in a["hists"]["dist/nodes_explored_unsolved"])
    assert a["hists"]["unsolved/closest_approach_hist"], "no unsolved closest-approach"
    n_profiles = len(a["path_series"]["ys"])
    assert n_profiles == min(4, len(path_rows)), (
        f"WANDB_PATH_PROFILES=4 not honoured: {n_profiles} vs {len(path_rows)} paths")
    assert all(L[-1] == 2 for L in a["path_series"]["ys"]), "path must end trivial"

    print(f"PANELS ok: {len(panels)} panels, all expected keys present")
    print(f"  path profiles drawn: {n_profiles} (from {len(path_rows)} solved paths)")
    print(f"  solve_rate={s['solve_rate']:.2f} at_1k={s['solve_rate_at_1k']:.2f} "
          f"p90_nodes={s['nodes_explored_p90']} hump_median={s['hump_height_median']}")
    print(f"  profile steps={len(pts)} plateau={pts[-1][1]:.2f}")


def phase_identity():
    import wandb
    from experiments.wandb_tracking import init_run
    os.environ["WANDB_DIR"] = ".scratch"
    run = init_run({**CFG, "WANDB_MODE": "offline"}, 50_000, 640,
                   "greedy_50000_640_mrl24_cyc_all_07_09_26",
                   "greedy_50000_640_mrl24_cyc_all_", "all")
    assert run.group == "ms640_solved-mrl24-cyc-all", run.group
    assert run.job_type == "greedy_baseline", run.job_type
    assert run.name == "50k · ms640_solved · mrl24 · cyc", run.name
    assert set(run.tags) >= {"ms640_solved", "mrl24", "cyc", "b50k", "normal"}
    cfg = dict(run.config)
    assert cfg["node_budget"] == 50_000 and isinstance(cfg["node_budget"], int)
    assert cfg["solver"] == "normal" and cfg["git_commit"]
    leaked = sorted(k for k in cfg if k.startswith(
        ("WANDB_", "DRIVE_", "MOUNT_", "HEARTBEAT_", "MP_", "use_", "PATH_"))
        or k in ("GB_PER_PRES", "LOCAL_OUT_DIR", "RESUME", "PROGRESS_EVERY"))
    assert not leaked, f"plumbing leaked into wandb.config: {leaked}"
    run.finish()
    print(f"IDENTITY ok: group={run.group!r} job_type={run.job_type!r}")
    print(f"  name={run.name!r}")
    print(f"  tags={sorted(run.tags)}")
    print(f"  config={sorted(cfg)}")


def phase_resume_full():
    """Re-running a finished sweep must reattach, not restart, and not duplicate."""
    before = set(glob.glob(f"{OUT}/*.jsonl"))
    out = _run()
    after = set(glob.glob(f"{OUT}/*.jsonl"))
    assert before == after, f"resume created a new file: {after - before}"
    assert len(list(open(out))) == 20, "resume appended duplicate rows"
    run_id = _latest_offline_dir().split("-", 3)[-1]
    expect = open(".scratch/_run_id").read()
    assert run_id == expect, f"run id changed on resume: {expect} -> {run_id}"
    print(f"RESUME-FULL ok: same file, still 20 rows, run_id stable ({run_id})")


def phase_resume_partial():
    """A jsonl written on an earlier DATE must still be picked up (no restart)."""
    import io
    from contextlib import redirect_stdout

    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    old = f"{OUT}/greedy_{BUDGET}_20_mrl24_cyc_620-640_01_01_25.jsonl"
    with open(old, "w") as f:
        for pid in (620, 621):
            # Deliberately minimal: no time_seconds, no max_relator_length_expanded.
            f.write(json.dumps({
                "pres_id": pid, "r1": "xyx", "r2": "XYX", "node_budget": BUDGET,
                "max_relator_length_cap": 24, "cyclic_reduce": True,
                "nodes_explored": 7, "solved": True, "path_length": 1}) + "\n")

    buf = io.StringIO()
    with redirect_stdout(buf):
        out = _run()
    log = buf.getvalue()
    assert "2 already done, 18 to run" in log, f"resume did not reattach:\n{log}"
    assert os.path.abspath(out) == os.path.abspath(old), f"new file created: {out}"
    print("RESUME-PARTIAL ok: old-dated jsonl reattached, 2 already done, 18 to run")
    print("  seed rows lack time_seconds/max_relator_length_expanded -> the"
          " missing-key tolerance held on the real finish path")


def phase_heavy():
    shutil.rmtree(OUT, ignore_errors=True)
    out = _run(SUBSET=(630, 634), HIGH_SPEEDUP=True, N_WORKERS=2, GB_PER_PRES=0.1)
    rows = [json.loads(l) for l in open(out)]
    ids = [r["pres_id"] for r in rows]
    assert len(ids) == len(set(ids)) == 4, f"one row per pres_id broken: {ids}"
    solved = [r for r in rows if r["solved"]]
    assert solved, "expected at least one solve in 630-633"
    assert all(r.get("path_recovered") for r in solved), "solved rows lost recovery flag"
    assert all(r["path_length"] is not None for r in solved), "recovery lost the path"
    print(f"HEAVY ok: 4 unique rows, {len(solved)} solved+recovered "
          f"(no duplicate rows from the deferred/recovery loop)")


def phase_cum_nodes():
    """run/* must accumulate once per worker result, never again at recovery."""
    from experiments.wandb_tracking import LiveLogger

    class FakeRun:
        def __init__(self):
            self.logs = []

        def log(self, d):
            self.logs.append(d)

    run = FakeRun()
    lg = LiveLogger(run, {**CFG, "WANDB_LOG_PRES_SCALARS": True}, BUDGET,
                    n_todo=2, n_seen=0, n_solved=0, cum_nodes=0)
    stats = [{"solved": True, "nodes_explored": 100},
             {"solved": False, "nodes_explored": 5000}]
    for s in stats:
        lg.on_result(s)
    # The heavy path then re-solves the solved one and emits its row LATER.
    lg.on_row({"pres_id": 630, "r1": "xyx", "r2": "XYX", "node_budget": BUDGET,
               "nodes_explored": 100, "solved": True, "path_length": 3,
               "path_recovered": True})

    assert lg.cum_nodes == 5100, f"cum_nodes double-counted: {lg.cum_nodes}"
    assert lg.n_processed == 2 and lg.n_solved == 1
    run_logs = [d for d in run.logs if "run/cum_nodes" in d]
    pres_logs = [d for d in run.logs if "pres_id" in d]
    assert [d["run/cum_nodes"] for d in run_logs] == [100, 5100]
    assert len(pres_logs) == 1 and pres_logs[0]["pres_id"] == 630
    assert "run/cum_nodes" not in pres_logs[0], "on_row must not touch run/* counters"

    # Resume must seed the counters, and throughput must stay session-scoped.
    lg2 = LiveLogger(FakeRun(), CFG, BUDGET, n_todo=1, n_seen=10, n_solved=4,
                     cum_nodes=999)
    lg2.on_result({"solved": True, "nodes_explored": 1})
    assert (lg2.n_processed, lg2.n_solved, lg2.cum_nodes) == (11, 5, 1000)
    assert lg2._session_nodes == 1, "session throughput contaminated by resume seed"
    print("CUM-NODES ok: accumulates once per result; on_row is pres/* only; "
          "resume seeds totals without inflating session nodes/s")


if __name__ == "__main__":
    globals()[f"phase_{sys.argv[1]}"]()
