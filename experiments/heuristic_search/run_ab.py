"""Run the tuned ordering against the length baseline on the same presentations, at Colab scale.

The local study capped every search at 1,000 nodes, so its central claim about large budgets is an
*extrapolation*: the tuned ordering's advantage over the baseline was still widening where the
ceiling cut the curve off. This runner is built to test that, not merely to score two arms.

The mechanism that makes it nearly free: **a search at budget B is exactly the first B pops of any
longer search.** So a single run to the full budget, recording the node count at which each
presentation solved, yields the entire solve-count-versus-budget curve for every checkpoint below
it. No re-running, no separate arms per budget.

What the run writes, per (arm, presentation), is one jsonl row carrying ``solved_at`` -- the node
count at the solve, or null. Everything else in the report is derived from that column.

Operational shape follows the rest of the repo: append-and-fsync per row so a disconnect loses at
most one search, a resume that skips rows already on disk, and a **time-based** heartbeat (a slow
machine must show as a falling rate, never as silence).

    from experiments.heuristic_search.run_ab import run_ab
    run_ab(cfg, out_dir="results/hsearch")
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import ROOT, bench66        # noqa: E402
from experiments.heuristic_search.hcompact import greedy_search_hcompact  # noqa: E402
from experiments.heuristic_search.hsolve import (                  # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED, greedy_search_h,
)

ARMS = {
    "baseline": None,                    # order by total length -- the control
    "recommended": RECOMMENDED,          # the tuned climb, no threshold
    "lean": LEAN_SMALL_BUDGET,           # the small-budget ordering, for contrast
}

UNSOLVED_CSV = os.path.join(ROOT, "results", "equivalence_classes", "ms1190_tables",
                            "unsolved_124_aca_classes.csv")


def load_rows(dataset, subset=None):
    """``[{name, r1, r2}]`` for the chosen dataset."""
    if dataset == "bench66":
        rows = [{"name": r["name"], "r1": r["r1"], "r2": r["r2"]} for r in bench66()]
    elif dataset == "unsolved124":
        with open(UNSOLVED_CSV) as f:
            rows = [{"name": r["aca_id"], "r1": r["r1"], "r2": r["r2"]}
                    for r in csv.DictReader(f)]
    else:
        raise ValueError(f"unknown DATASET {dataset!r}")
    return rows[:subset] if subset else rows


def _done(path):
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue                 # torn trailing line from a killed run
            seen.add((r["arm"], r["name"]))
    return seen


def run_ab(cfg, out_dir="results/hsearch", heartbeat_secs=60, progress_secs=300):
    rows = load_rows(cfg["DATASET"], cfg.get("SUBSET"))
    budget = cfg["NODE_BUDGET"]
    mrl = cfg["MAX_RELATOR_LENGTH"]
    arms = cfg["ARMS"]
    # KEEP_PATH=False runs each search without the parent map (1.53x less RAM -- 24 kB/node
    # instead of 36.5, measured worst-case on the unsolved 124 at cap 48) and, when a search
    # DOES solve, recovers its certificate by re-running just that presentation with the map on.
    # The search is deterministic, so the recovered path is exact and the written row is
    # identical either way -- which is why, like HIGH_SPEEDUP, the knob is result-neutral and
    # stays OUT of the filename identity: files resume across modes.
    keep_path = cfg.get("KEEP_PATH", True)
    # ENGINE="hcompact" runs the same search on the packed-arena solver: pop-identical to
    # greedy_search_h (880-search cross-check in verify_hcompact.py), ~78 B/state vs ~390,
    # so a 10^6 search reserves ~7 GB instead of holding ~24. Pathless like KEEP_PATH=False,
    # with the same automatic certificate recovery on a solve. Result-neutral, so it too
    # stays out of the filename identity and files resume across engines.
    engine = cfg.get("ENGINE", "hsolve")
    if engine not in ("hsolve", "hcompact"):
        raise ValueError(f"unknown ENGINE {engine!r}")
    os.makedirs(out_dir, exist_ok=True)
    # Identity: every knob that changes a result, and none that does not.
    stem = f"{cfg['OUT_STEM']}_{cfg['DATASET']}_b{budget}_mrl{mrl}"
    out = os.path.join(out_dir, stem + ".jsonl")

    seen = _done(out) if cfg.get("RESUME", True) else set()
    todo = [(a, r) for a in arms for r in rows if (a, r["name"]) not in seen]
    print(f"  {len(arms)} arms x {len(rows)} presentations, budget {budget:,}, cap {mrl}"
          + ("  [low-memory: KEEP_PATH=False]" if not keep_path else "")
          + ("  [engine: hcompact]" if engine == "hcompact" else ""))
    print(f"  {len(seen)} rows resumed; {len(todo)} to run")
    print(f"  -> {out}", flush=True)

    t0 = last_hb = last_pg = time.perf_counter()
    done = solved = 0

    with open(out, "a") as f:
        for arm, row in todo:
            # The heartbeat has to fire DURING a long search, not only between them: at 10^5+
            # nodes one presentation can run for many minutes and silence is indistinguishable
            # from a hang. progress() is called by the solver on every pop.
            state = {"nodes": 0, "last": time.perf_counter(), "prev_nodes": 0}

            def progress(n, _s=state, _arm=arm, _nm=row["name"]):
                _s["nodes"] = n
                now = time.perf_counter()
                if now - _s["last"] >= heartbeat_secs:
                    rate = (n - _s["prev_nodes"]) / (now - _s["last"])
                    print(f"      [{_arm}/{_nm}] {n:,}/{budget:,} nodes  "
                          f"{rate:,.0f} nodes/s", flush=True)
                    _s["last"], _s["prev_nodes"] = now, n

            t = time.perf_counter()
            if engine == "hcompact":
                res = greedy_search_hcompact(row["r1"], row["r2"], budget,
                                             max_relator_length=mrl,
                                             config=ARMS[arm], progress=progress)
            else:
                res = greedy_search_h(row["r1"], row["r2"], budget,
                                      max_relator_length=mrl, config=ARMS[arm],
                                      progress=progress, keep_path=keep_path)
            if res["solved"] and (engine == "hcompact" or not keep_path):
                # Deterministic recovery: same search with the parent map on stops at the same
                # pop, so its memory is bounded by the SOLVE's node count, not the budget --
                # and solved searches are the cheap ones. The full-budget burns, where the RAM
                # saving matters, never reach this branch.
                rec = greedy_search_h(row["r1"], row["r2"], budget,
                                      max_relator_length=mrl, config=ARMS[arm],
                                      progress=progress, keep_path=True)
                assert (rec["solved"], rec["nodes_explored"], rec["path_length"]) == \
                       (True, res["nodes_explored"], res["path_length"]), \
                    (row["name"], arm, "recovery diverged from the low-memory search")
                res = rec
            dt = time.perf_counter() - t

            f.write(json.dumps({
                "arm": arm, "name": row["name"], "dataset": cfg["DATASET"],
                "budget": budget, "mrl": mrl,
                "solved": res["solved"],
                # The whole budget curve comes from this one number.
                "solved_at": res["nodes_explored"] if res["solved"] else None,
                "nodes_explored": res["nodes_explored"],
                "path_length": res["path_length"],
                "min_relator_length": res["min_relator_length"],
                "max_relator_length_expanded": res["max_relator_length_expanded"],
                "path_moves": res["path_moves"],
                "secs": round(dt, 2),
            }) + "\n")
            f.flush()
            os.fsync(f.fileno())

            done += 1
            solved += bool(res["solved"])
            now = time.perf_counter()
            if now - last_pg >= progress_secs or done == len(todo):
                el = now - t0
                eta = el / done * (len(todo) - done)
                print(f"    {done}/{len(todo)} searches  {solved} solved  "
                      f"{el/60:.1f} min elapsed  ETA {eta/60:.1f} min", flush=True)
                last_pg = now

    report(out, cfg)


def report(out, cfg):
    """Solve counts per arm at every checkpoint -- and whether the gap is still widening."""
    data = [json.loads(l) for l in open(out)]
    arms = cfg["ARMS"]
    pts = [b for b in cfg["CHECKPOINTS"] if b <= cfg["NODE_BUDGET"]]
    n = len({r["name"] for r in data})

    def curve(arm):
        d = [r for r in data if r["arm"] == arm]
        return [sum(1 for r in d if r["solved_at"] is not None and r["solved_at"] <= b)
                for b in pts]

    lines = [f"# A/B — {cfg['DATASET']}, budget {cfg['NODE_BUDGET']:,}, cap "
             f"{cfg['MAX_RELATOR_LENGTH']}", "",
             f"{n} presentations. Each curve is read off ONE run per (arm, presentation): a "
             "search at budget B is the first B pops of any longer search, so the node count at "
             "the solve gives every checkpoint below it.", "",
             "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
             "|---" * (len(pts) + 1) + "|"]
    curves = {a: curve(a) for a in arms}
    for a in arms:
        lines.append(f"| {a} | " + " | ".join(f"{v}/{n}" for v in curves[a]) + " |")

    if "baseline" in curves and len(arms) > 1:
        base = curves["baseline"]
        lines += ["", "## The gap over the baseline — the thing worth watching", "",
                  "| arm | " + " | ".join(f"{b:,}" for b in pts) + " | verdict |",
                  "|---" * (len(pts) + 2) + "|"]
        for a in arms:
            if a == "baseline":
                continue
            g = [x - y for x, y in zip(curves[a], base)]
            # Compare the last third of the range against the middle: still widening means the
            # advantage grows with compute, which is what the local study predicted.
            mid = g[len(g) // 2]
            verdict = ("**still widening**" if g[-1] > mid + 1 else
                       "**turned over**" if g[-1] < mid - 1 else "flat")
            lines.append(f"| {a} | " + " | ".join(f"{v:+d}" for v in g) + f" | {verdict} |")
        lines += ["", "The local study (≤1,000 nodes) predicted **still widening** for "
                  "`recommended`. If this run shows it turning over, the extrapolation to large "
                  "budgets does not hold and the ordering is buying earliness rather than reach — "
                  "which is worth knowing and worth reporting either way.", ""]

    md = out.replace(".jsonl", ".md")
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print()
    print("\n".join(lines))
    print(f"\n  wrote {md}")
