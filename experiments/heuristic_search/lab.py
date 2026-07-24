"""Score a list of configs against a benchmark slice, in parallel, resumably.

Every experiment in the hyperparameter program is the same shape -- take N configs, run each over
one frozen slice at one budget and one cap, write a row per (config, presentation) -- so it is
written once, here, and each experiment is a config generator plus a report.

**Resumability is not optional.** A long run in this environment gets reaped, and a sweep that
loses its work on a kill cannot be run at all. So: one jsonl per experiment, appended and fsynced
as results land, and a restart reads back what is already there and skips it. The row key is
``(config_id, name, budget, mrl)`` -- everything that changes the result and nothing that does
not, so re-running with more configs extends the file instead of invalidating it.

Work is chunked **by config**, not by presentation, for a reason that shows up in the clock: the
feature caches in ``hlab`` are per-process, and a worker handed one config over 40 presentations
re-scores far fewer novel words than one handed 40 configs over one presentation.

    python3 -m experiments.heuristic_search.lab --help
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (        # noqa: E402
    LOGS, cfg_name, load_split, make_priority, run_one,
)

# ONE core, one search at a time. This is not a tuning choice, it is a hard rule.
#
# A ProcessPoolExecutor here spawns children that outlive their parent: when the harness reaps a
# long-running sweep it kills only the parent, and the workers keep searching. Two such batches --
# eighteen processes -- survived unnoticed and drove this machine 22 GB into swap, at which point
# the editor the user was working in reported a 75 GB footprint and became unusable. Serial
# execution has no children to orphan, so the failure mode does not exist rather than being
# guarded against. Parallelism belongs on Colab, where the user runs it and can see it.
BUDGET_CEILING = 1_000         # the hard local cap; asserted, never merely documented


def _work(task):
    """One config over one slice, in this process."""
    cid, cfg, rows, budget, mrl = task
    p = make_priority(cfg)
    t0 = time.perf_counter()
    out = []
    for r in rows:
        res = run_one(r["r1"], r["r2"], budget, p, mrl)
        out.append({"config_id": cid, "name": r["name"], "budget": budget, "mrl": mrl,
                    "solved": res["solved"], "nodes": res["nodes"],
                    "path_length": res["path_length"], "min_total": res["min_total"],
                    "max_pop": res["max_pop"],
                    "bar": r.get("bar_to_beat"), "source": r["source"]})
    return out, time.perf_counter() - t0


def done_keys(path):
    """What a previous, possibly killed, run already computed. A torn final line is dropped."""
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue                       # torn trailing line from a kill mid-write
            seen.add((r["config_id"], r["name"], r["budget"], r["mrl"]))
    return seen


def evaluate(configs, slice_name, budget, mrl, out_path, label="", deadline=None):
    """Run every config over the slice, one at a time, skipping whatever the jsonl already holds.

    ``configs`` is a list of config dicts; ids come from ``cfg_name`` so the same ordering always
    gets the same id and a resumed run lines up with the file it is resuming.

    ``deadline`` (seconds) stops cleanly between configs. Every completed config is already on
    disk, so stopping early costs nothing and the next call resumes exactly where this one left
    off -- which is what makes a serial sweep survivable in a bounded-timeout environment.
    """
    assert budget <= BUDGET_CEILING, f"{budget} exceeds the {BUDGET_CEILING}-node local cap"
    rows = load_split(slice_name)
    seen = done_keys(out_path)

    tasks = []
    for cfg in configs:
        cid = cfg_name(cfg)
        todo = [r for r in rows if (cid, r["name"], budget, mrl) not in seen]
        if todo:
            tasks.append((cid, cfg, todo, budget, mrl))

    if not tasks:
        print(f"  [{label}] all {len(configs)} configs already done in "
              f"{os.path.basename(out_path)}", flush=True)
        return True

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    t0, n_done = time.perf_counter(), 0
    print(f"  [{label}] {len(tasks)} configs x {len(rows)} pres, budget {budget}, mrl {mrl}"
          f"  ({len(seen)} rows resumed)", flush=True)

    with open(out_path, "a") as f:
        last_beat = t0
        for task in tasks:
            out, dt = _work(task)
            for row in out:
                row["secs"] = round(dt, 3)
                f.write(json.dumps(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
            n_done += 1
            now = time.perf_counter()
            # Time-based heartbeat: a slow config must show as a falling rate, never as silence.
            if now - last_beat >= 60 or n_done == len(tasks):
                el = now - t0
                eta = el / n_done * (len(tasks) - n_done)
                print(f"    [{label}] {n_done}/{len(tasks)} configs  {el/60:.1f} min elapsed  "
                      f"ETA {eta/60:.1f} min  ({el/n_done:.1f} s/config)", flush=True)
                last_beat = now
            if deadline is not None and now - t0 >= deadline:
                print(f"    [{label}] deadline hit at {n_done}/{len(tasks)} — "
                      f"stopping cleanly, resume picks up here", flush=True)
                return False
    return True


# ------------------------------------------------------------------------------------ reporting

def read(path, by=("config_id",)):
    """jsonl -> {arm: {name: row}}, where ``arm`` is the tuple of ``by`` fields (joined if >1).

    ``by`` exists because an experiment that varies the cap or the budget writes rows whose
    ``config_id`` is identical across arms; grouping on the config alone would silently merge them
    and report whichever landed last.
    """
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            arm = r[by[0]] if len(by) == 1 else " | ".join(str(r[k]) for k in by)
            out.setdefault(arm, {})[r["name"]] = r
    return out


def sign_test(w, l):
    """Two-sided exact sign test on the discordant pairs. Solve counts here are PAIRED."""
    n = w + l
    if n == 0:
        return 1.0
    from math import comb
    k = max(w, l)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def score(res, ctrl):
    """One arm against the control on the same presentations.

    ``nodes_mean`` is over the presentations BOTH arms solved, never a raw sum: each arm's
    both-solved set has its own size, so a sum ranks an arm that solved one fewer as cheaper. That
    exact mistake pre-registered the wrong winner once already in this project.
    """
    common = [k for k in res if k in ctrl]
    both = [k for k in common if res[k]["solved"] and ctrl[k]["solved"]]
    won = sorted(k for k in common if res[k]["solved"] and not ctrl[k]["solved"])
    lost = sorted(k for k in common if ctrl[k]["solved"] and not res[k]["solved"])
    n = len(both)
    solved = sum(1 for k in common if res[k]["solved"])
    # Progress on the unsolved: how much shorter the best state reached is than the control's.
    prog = [ctrl[k]["min_total"] - res[k]["min_total"] for k in common if not res[k]["solved"]]
    return {
        "solved": solved, "n": len(common),
        "won": won, "lost": lost, "net": len(won) - len(lost),
        "sign_p": sign_test(len(won), len(lost)),
        "nodes_mean": (sum(res[k]["nodes"] for k in both) / n) if n else None,
        "nodes_ctrl_mean": (sum(ctrl[k]["nodes"] for k in both) / n) if n else None,
        "path_mean": (sum(res[k]["path_length"] for k in both) / n) if n else None,
        "path_ctrl_mean": (sum(ctrl[k]["path_length"] for k in both) / n) if n else None,
        "n_both": n,
        "min_total_gain": (sum(prog) / len(prog)) if prog else 0.0,
    }


def rank(results, ctrl_id, key="solved"):
    """Configs best-first: solves, then fewer nodes per commonly-solved search, then shorter paths."""
    ctrl = results[ctrl_id]
    rows = []
    for cid, res in results.items():
        s = score(res, ctrl)
        s["config_id"] = cid
        rows.append(s)
    rows.sort(key=lambda s: (-s["solved"], s["nodes_mean"] if s["nodes_mean"] is not None else 1e9,
                             s["path_mean"] if s["path_mean"] is not None else 1e9))
    return rows


def table(rows, ctrl_id, top=25, title=""):
    ctrl = next(r for r in rows if r["config_id"] == ctrl_id)
    out = [f"\n{'=' * 108}", f"{title}", f"{'=' * 108}",
           f"  {'config':52s} {'solved':>9s} {'net':>5s} {'p':>6s} {'nodes':>8s} {'path':>7s} "
           f"{'dmin':>6s}"]
    for r in rows[:top]:
        mark = "  <- control" if r["config_id"] == ctrl_id else ""
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "-"
        pm = f"{r['path_mean']:.1f}" if r["path_mean"] is not None else "-"
        out.append(f"  {r['config_id'][:52]:52s} {r['solved']:>4d}/{r['n']:<4d} "
                   f"{r['net']:>+5d} {r['sign_p']:>6.3f} {nm:>8s} {pm:>7s} "
                   f"{r['min_total_gain']:>+6.2f}{mark}")
    out.append(f"  control solved {ctrl['solved']}/{ctrl['n']}, "
               f"nodes {ctrl['nodes_mean']}, path {ctrl['path_mean']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True)
    ap.add_argument("--slice", default="train")
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--mrl", type=int, default=48)
    ap.add_argument("--configs", required=True, help="json file: list of config dicts")
    ap.add_argument("--deadline", type=float, default=None, help="seconds; stops between configs")
    a = ap.parse_args()

    with open(a.configs) as f:
        cfgs = json.load(f)
    out = os.path.join(LOGS, f"{a.exp}.jsonl")
    evaluate(cfgs, a.slice, a.budget, a.mrl, out, label=a.exp, deadline=a.deadline)


if __name__ == "__main__":
    main()
