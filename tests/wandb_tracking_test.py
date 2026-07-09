"""Offline checks for experiments/wandb_tracking.py.

No wandb, no network. Every expected value below is hand-computed, so a passing
run means the analytics are right, not merely self-consistent.

    .venv/bin/python3 tests/wandb_tracking_test.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.wandb_tracking import (  # noqa: E402
    _spread, anytime_profile, bucket_by_initial_length, canonical_initial_length,
    compute_analytics, compute_identity, derive_row, human_budget,
    path_analytics, summary_stats)

BASE_CFG = {
    "DATASET": "data/ms640_solved.txt",
    "SUBSET": None,
    "MAX_RELATOR_LENGTH": 24,
    "CYCLIC_REDUCE": True,
    "HIGH_SPEEDUP": False,
    "N_WORKERS": 0,
    "WANDB_PATH_PROFILES": 8,
}


def test_human_budget():
    assert human_budget(1_000) == "1k"
    assert human_budget(50_000) == "50k"
    assert human_budget(1_000_000) == "1M"
    assert human_budget(1234) == "1234"


def test_spread():
    assert _spread([], 5) == []
    assert _spread([1, 2, 3], 0) == []
    assert _spread([1, 2, 3], 5) == [1, 2, 3]
    assert _spread([1, 2, 3, 4, 5], 1) == [1]          # would divide by zero
    assert _spread([1, 2, 3, 4, 5], 3) == [1, 3, 5]    # endpoints included


def test_derive_row():
    row = {"r1": "xyx", "r2": "YXY", "nodes_explored": 900, "node_budget": 1000,
           "max_relator_length_expanded": 14, "time_seconds": 3.0, "solved": True}
    d = derive_row(row, canon_length=6)
    assert d["initial_length"] == 6            # len("xyx") + len("YXY")
    assert d["canonical_initial_length"] == 6
    assert d["nodes_per_s"] == 300.0           # 900 / 3.0
    assert d["hump_height"] == 8               # 14 - 6
    assert d["budget_frac"] == 0.9             # 900 / 1000
    assert d["path_recovered"] is False


def test_derive_row_tolerates_missing_keys():
    """use_time / use_max_relator_expanded may have been off when a row was written."""
    minimal = {"r1": "xy", "r2": "XY", "nodes_explored": 10, "node_budget": 10,
               "solved": False}
    d = derive_row(minimal)
    assert d["initial_length"] == 4
    assert d["canonical_initial_length"] == 4   # falls back to the raw length
    assert d["nodes_per_s"] is None
    assert d["hump_height"] is None
    assert d["budget_frac"] == 1.0


def test_anytime_profile_points():
    rows = [{"solved": True, "nodes_explored": n} for n in (10, 30, 30, 50)]
    rows.append({"solved": False, "nodes_explored": 50})
    points, _ = anytime_profile(rows, n_pres=5, node_budget=50)
    # b<10 -> 0.0 | b=10 -> 1/5 | b=30 -> 3/5 (the tie collapses) | b=50 -> 4/5
    assert points == [[0, 0.0], [10, 0.2], [30, 0.6], [50, 0.8]]


def test_anytime_profile_thresholds():
    rows = [{"solved": True, "nodes_explored": n} for n in (500, 6_000, 40_000)]
    rows.append({"solved": False, "nodes_explored": 50_000})
    _, at = anytime_profile(rows, n_pres=4, node_budget=50_000)
    assert at["solve_rate_at_1k"] == 0.25       # only the 500-node solve
    assert at["solve_rate_at_5k"] == 0.25
    assert at["solve_rate_at_10k"] == 0.5       # + the 6k solve
    assert at["solve_rate_at_50k"] == 0.75      # + the 40k solve; one never solves
    assert "solve_rate_at_100k" not in at       # above node_budget


def test_bucket_by_initial_length():
    rows = [derive_row(r) for r in (
        {"r1": "xyx", "r2": "XYX", "solved": True, "nodes_explored": 100},
        {"r1": "xyx", "r2": "XYX", "solved": False, "nodes_explored": 300},
        {"r1": "xyxy", "r2": "XYXY", "solved": True, "nodes_explored": 200},
    )]
    buckets = {b["initial_length"]: b for b in bucket_by_initial_length(rows)}
    assert buckets[6]["n"] == 2 and buckets[6]["solve_rate"] == 0.5
    assert buckets[6]["median_nodes"] == 200          # median of 100, 300
    assert buckets[6]["median_nodes_solved"] == 100
    assert buckets[8]["n"] == 1 and buckets[8]["solve_rate"] == 1.0


def test_summary_stats():
    rows = [derive_row(r) for r in (
        {"r1": "xy", "r2": "XY", "solved": True, "nodes_explored": 10,
         "path_length": 3, "time_seconds": 1.0, "max_relator_length_expanded": 6},
        {"r1": "xy", "r2": "XY", "solved": False, "nodes_explored": 90,
         "path_length": None, "time_seconds": 3.0, "max_relator_length_expanded": 10},
    )]
    s = summary_stats(rows, n_pres=2, n_solved=1, total_time=4.0)
    assert s["solve_rate"] == 0.5
    assert s["censored_fraction"] == 0.5
    assert s["nodes_explored_mean"] == 50.0
    assert s["path_length_median"] == 3
    assert s["nodes_per_s_mean"] == 20.0        # mean(10/1, 90/3) = mean(10, 30)
    assert s["hump_height_median"] == 4         # median(6-4, 10-4) = median(2, 6)


def test_path_analytics_replays_a_real_solution():
    """L(t) must start at the canonical start length and end at the trivial 2."""
    from experiments.run_baseline import load_dataset
    from experiments.search.greedy_baseline import greedy_search

    solved = []
    for pres_id, r1, r2 in load_dataset("data/ms640_solved.txt", (0, 4)):
        stats = greedy_search(r1, r2, 20_000, max_relator_length=24,
                              cyclic_reduce=True)
        if stats["solved"]:
            solved.append({"pres_id": pres_id, "r1": r1, "r2": r2,
                           "path_moves": stats["path_moves"],
                           "_path_length": stats["path_length"]})
    assert solved, "expected at least one of ms640 idx 0-3 to solve at 20k nodes"

    out = path_analytics(solved, cyclic_reduce=True, n_profiles=8)
    assert out["series"] is not None
    assert len(out["series"]["ys"]) == len(solved)

    for row, L in zip(solved, out["series"]["ys"]):
        assert len(L) == row["_path_length"] + 1
        assert L[0] == canonical_initial_length(row["r1"], row["r2"], True)
        assert L[-1] == 2, "the trivial presentation is |x| + |y| = 2"

    assert all(o >= 0 for o in out["overshoots"])
    assert all(0.0 <= p <= 1.0 for p in out["peak_positions"])


def test_path_analytics_disabled():
    assert path_analytics([{"pres_id": 0, "r1": "x", "r2": "y", "path_moves": []}],
                          n_profiles=0)["series"] is None


def test_compute_identity():
    ident = compute_identity(BASE_CFG, 50_000, 640, "greedy_50000_640_...", "all")
    assert ident["group"] == "ms640_solved-mrl24-cyc-all"
    assert ident["job_type"] == "greedy_baseline"     # family, not budget
    assert ident["name"] == "50k · ms640_solved · mrl24 · cyc"
    assert set(ident["tags"]) == {"ms640_solved", "mrl24", "cyc", "b50k",
                                  "normal", "subset:all"}
    assert ident["config"]["node_budget"] == 50_000   # numeric, so it sorts
    assert ident["config"]["solver"] == "normal"

    leaked = [k for k in ident["config"]
              if k.startswith(("WANDB_", "DRIVE_", "MOUNT_", "HEARTBEAT_", "MP_"))
              or k in ("GB_PER_PRES", "LOCAL_OUT_DIR", "RESUME", "PROGRESS_EVERY")]
    assert not leaked, f"plumbing leaked into wandb.config: {leaked}"


def test_compute_identity_heavy_and_subset():
    cfg = {**BASE_CFG, "HIGH_SPEEDUP": True, "SUBSET": (0, 20),
           "DATASET": "data/ms_unsolved_reps/ms_reps_unsolved.txt",
           "MAX_RELATOR_LENGTH": 48}
    ident = compute_identity(cfg, 1_000_000, 20, "prefix_", "0-20")
    assert ident["group"] == "ms_reps_unsolved-mrl48-cyc-0-20"
    assert ident["name"] == "1M · ms_reps_unsolved · mrl48 · cyc · 0-20"
    assert "heavy" in ident["tags"] and "b1M" in ident["tags"]


def test_compute_analytics_panels_and_summary():
    rows = [
        {"pres_id": 0, "r1": "xyx", "r2": "XYX", "node_budget": 1000, "solved": True,
         "nodes_explored": 400, "path_length": 5, "time_seconds": 2.0,
         "min_relator_length": 2, "max_relator_length_expanded": 10},
        {"pres_id": 1, "r1": "xyxy", "r2": "XYXY", "node_budget": 1000, "solved": False,
         "nodes_explored": 1000, "path_length": None, "time_seconds": 5.0,
         "min_relator_length": 4, "max_relator_length_expanded": 16},
    ]
    a = compute_analytics(rows, [], BASE_CFG, node_budget=1000, n_seen=2,
                          n_solved=1, total_time=7.0)

    assert a["summary"]["solve_rate"] == 0.5
    assert a["summary"]["solve_rate_at_1k"] == 0.5
    assert a["summary"]["timing_regime"] == "uniform"
    assert a["profile_points"] == [[0, 0.0], [400, 0.5], [1000, 0.5]]

    assert a["hists"]["dist/nodes_explored_solved"] == [400]
    assert a["hists"]["dist/nodes_explored_unsolved"] == [1000]
    assert a["hists"]["unsolved/closest_approach_hist"] == [4]   # unsolved rows only
    assert a["hists"]["hump/overshoot_hist"] == [4, 8]           # 10-6, 16-8
    assert a["hists"]["hump/path_overshoot_hist"] == []          # no paths supplied
    assert a["scatters"]["rel/nodes_vs_path"][1] == [[400, 5]]


def test_compute_analytics_flags_heavy_timing():
    rows = [{"pres_id": 0, "r1": "xy", "r2": "XY", "node_budget": 10, "solved": True,
             "nodes_explored": 5, "path_length": 1, "path_recovered": True}]
    a = compute_analytics(rows, [], BASE_CFG, 10, 1, 1, 1.0)
    assert a["mixed_timing"] is True
    assert a["summary"]["timing_regime"] == "mixed(heavy)"


def test_compute_analytics_on_minimal_rows():
    """A run with every use_* toggle off must still produce the core panels."""
    rows = [{"pres_id": 0, "r1": "xyx", "r2": "XYX", "node_budget": 1000,
             "solved": True, "nodes_explored": 400, "path_length": 5}]
    a = compute_analytics(rows, [], BASE_CFG, 1000, 1, 1, 1.0)
    assert a["profile_points"] == [[0, 0.0], [400, 1.0], [1000, 1.0]]
    assert a["buckets"][0]["solve_rate"] == 1.0
    assert a["hists"]["dist/nodes_explored_solved"] == [400]
    assert a["hists"]["dist/time_seconds"] == []        # skipped, not crashed
    assert a["hists"]["hump/overshoot_hist"] == []
    assert a["summary"]["nodes_per_s_mean"] is None


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ok   {t.__name__}")
        except Exception as e:                                  # noqa: BLE001
            failed += 1
            print(f"  FAIL {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
