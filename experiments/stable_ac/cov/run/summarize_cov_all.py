"""Summarize a ``run_cov_all`` jsonl: every statistic per presentation first, then
aggregated across presentations (rows 531/532 alone hold ~a fifth of MS640's
starts, so pooled numbers would be theirs).

A search at budget B is exactly the first B pops of any longer search, so a row
solved in n nodes counts as solved at every budget >= n; one run at the file's
budget gives every smaller budget's column for free.

Arms (per presentation, at budget B):
  * control     — the untransformed pair, cap 24;
  * oracle_all  — the best CoV start of the whole ``suballpxyb8`` family (an
                  ORACLE: it presumes knowing which start to run);
  * oracle_one  — the best start the old single-pass substitution also reaches.
Oracle nodes are the minimum over solved starts; oracle path length is the
minimum path length over solved starts (a separate oracle, possibly another
start). CoV path lengths are in the TRANSFORMED coordinates: a solved CoV start
certifies stable AC-triviality of the original, and its path is not an AC path
of the original.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.cov.run.summarize_cov_all FILE.jsonl
"""

import argparse
import json
import os
import statistics as st
from collections import defaultdict


def _mm(xs):
    return (round(st.mean(xs), 2), st.median(xs)) if xs else (None, None)


def summarize(path):
    by = defaultdict(list)
    with open(path) as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                by[r["pres_id"]].append(r)
    budget = next(iter(by.values()))[0]["node_budget"]
    budgets = [b for b in (100, 1000, 10_000, 100_000) if b <= budget]
    out = {"file": os.path.basename(path), "node_budget": budget,
           "presentations": len(by),
           "cov_starts": sum(len(v) - 1 for v in by.values()),
           "cpu_hours": round(sum(r["time_seconds"] for v in by.values() for r in v) / 3600, 3),
           "per_budget": {}}
    nodes_spent = [sum(r["nodes_explored"] for r in v if not r["is_control"])
                   for v in by.values()]
    out["total_cov_nodes_per_presentation"] = {
        "mean": round(st.mean(nodes_spent), 1), "median": st.median(nodes_spent),
        "max": max(nodes_spent)}
    for B in budgets:
        arm = {k: {"solved": 0, "nodes": [], "path": []}
               for k in ("control", "oracle_all", "oracle_one")}
        shared_nodes = {k: [] for k in arm}
        shared_path = {k: [] for k in arm}
        frac = {"cheaper": [], "equal": [], "dearer": [], "fail": []}
        flips_non_one, all_beats_one = [], 0
        for pid, rows in sorted(by.items()):
            ok = lambda r: r["solved"] and r["nodes_explored"] <= B
            ctrl = next(r for r in rows if r["is_control"])
            cov = [r for r in rows if not r["is_control"]]
            groups = {"control": [ctrl] if ok(ctrl) else [],
                      "oracle_all": [r for r in cov if ok(r)],
                      "oracle_one": [r for r in cov if ok(r) and r["is_one_pattern"]]}
            best = {}
            for k, g in groups.items():
                if g:
                    best[k] = (min(r["nodes_explored"] for r in g),
                               min(r["path_length"] for r in g))
                    arm[k]["solved"] += 1
                    arm[k]["nodes"].append(best[k][0])
                    arm[k]["path"].append(best[k][1])
            if len(best) == 3:
                for k in arm:
                    shared_nodes[k].append(best[k][0])
                    shared_path[k].append(best[k][1])
            if "oracle_all" in best and "oracle_one" not in best and "control" not in best:
                flips_non_one.append(pid)
            if "oracle_all" in best and ("oracle_one" not in best
                                         or best["oracle_all"][0] < best["oracle_one"][0]):
                all_beats_one += 1
            if cov:
                c = best.get("control", (None,))[0]
                n = {"cheaper": 0, "equal": 0, "dearer": 0, "fail": 0}
                for r in cov:
                    if not ok(r):
                        n["fail"] += 1
                    elif c is None or r["nodes_explored"] < c:
                        n["cheaper"] += 1
                    elif r["nodes_explored"] == c:
                        n["equal"] += 1
                    else:
                        n["dearer"] += 1
                for k in frac:
                    frac[k].append(n[k] / len(cov))
        res = {}
        for k, a in arm.items():
            res[k] = {"solved": a["solved"],
                      "nodes_mean_median_on_own_solved": _mm(a["nodes"]),
                      "path_mean_median_on_own_solved": _mm(a["path"]),
                      "nodes_mean_median_on_shared": _mm(shared_nodes[k]),
                      "path_mean_median_on_shared": _mm(shared_path[k])}
        res["shared_solved_set"] = len(shared_nodes["control"])
        res["random_start_vs_control_mean_fraction"] = {
            k: round(st.mean(v), 4) for k, v in frac.items()}
        res["solved_only_via_non_one_pattern_start"] = {
            "count": len(flips_non_one), "pres_ids": flips_non_one}
        res["oracle_all_beats_oracle_one_in_nodes_or_solves"] = all_beats_one
        out["per_budget"][B] = res
    return out


def to_markdown(s):
    L = [f"# CoV sweep summary: `{s['file']}`", "",
         f"Budget {s['node_budget']:,} nodes; {s['presentations']} presentations, "
         f"{s['cov_starts']:,} CoV starts + {s['presentations']} controls; "
         f"{s['cpu_hours']} CPU-hours of search (sum of `time_seconds`).", "",
         "Every statistic is computed per presentation, then aggregated across "
         "presentations. Oracle arms presume knowing the best start. CoV path "
         "lengths are in transformed coordinates (stable AC, not an AC path of the "
         "original).", ""]
    t = s["total_cov_nodes_per_presentation"]
    L += [f"Total nodes over all CoV starts per presentation (the oracle's real cost): "
          f"mean {t['mean']:,}, median {t['median']:,}, max {t['max']:,}.", ""]
    for B, r in s["per_budget"].items():
        L += [f"## Budget {int(B):,}", "",
              "| arm | solved | nodes mean / median (own) | path mean / median (own) "
              "| nodes mean / median (shared) | path mean / median (shared) |",
              "|---|---|---|---|---|---|"]
        for k in ("control", "oracle_all", "oracle_one"):
            a = r[k]
            f = lambda p: f"{p[0]} / {p[1]}"
            L.append(f"| {k} | {a['solved']} | {f(a['nodes_mean_median_on_own_solved'])} | "
                     f"{f(a['path_mean_median_on_own_solved'])} | "
                     f"{f(a['nodes_mean_median_on_shared'])} | "
                     f"{f(a['path_mean_median_on_shared'])} |")
        fr = r["random_start_vs_control_mean_fraction"]
        nn = r["solved_only_via_non_one_pattern_start"]
        L += ["", f"Shared solved set: {r['shared_solved_set']} presentations.",
              f"A single random CoV start vs the control (mean over presentations): "
              f"cheaper {fr['cheaper']:.1%}, equal {fr['equal']:.1%}, "
              f"dearer {fr['dearer']:.1%}, fails {fr['fail']:.1%}.",
              f"Solved only through a start that is NOT one-pattern (control and "
              f"one-pattern oracle both fail): {nn['count']}"
              + (f" (pres_ids {nn['pres_ids'][:40]})" if nn["count"] else "") + ".",
              f"Presentations where the full family's oracle beats the one-pattern "
              f"oracle (solves it or uses fewer nodes): "
              f"{r['oracle_all_beats_oracle_one_in_nodes_or_solves']}.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    a = ap.parse_args()
    s = summarize(a.file)
    base = os.path.splitext(a.file)[0]
    with open(base + "_summary.json", "w") as f:
        json.dump(s, f, indent=1)
    with open(base + "_summary.md", "w") as f:
        f.write(to_markdown(s) + "\n")
    print(to_markdown(s))


if __name__ == "__main__":
    main()
