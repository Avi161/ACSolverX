"""One csv row per presentation from a ``run_cov_all`` jsonl.

For each presentation: the control's result, how many CoV starts it has and how
many solve, the best (fewest nodes) CoV start with the substitution that made it,
and the split of its starts into cheaper / equal / dearer / unsolved against the
control (a start counts as cheaper when it solves and the control does not).

A search at budget B is the first B pops of a longer one, so the node counts in
a budget 100,000 file also answer every smaller budget.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.cov.run.table_cov_all_per_presentation FILE.jsonl
writes FILE_per_presentation.csv next to it.
"""

import argparse
import csv
import json
import os
from collections import defaultdict

FIELDS = ["pres_id", "r1_orig", "r2_orig", "start_total_length_orig", "node_budget",
          "control_solved", "control_nodes", "control_path_length",
          "cov_starts", "cov_one_pattern_starts", "cov_solved_starts",
          "best_cov_nodes", "best_cov_path_length", "best_cov_is_one_pattern",
          "best_cov_z_word", "best_cov_pattern", "best_cov_iso_gen", "best_cov_iso_index",
          "best_cov_r1", "best_cov_r2",
          "frac_cheaper", "frac_equal", "frac_dearer", "frac_unsolved"]


def table(path):
    by = defaultdict(list)
    with open(path) as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                by[r["pres_id"]].append(r)
    out = []
    for pid in sorted(by):
        rows = by[pid]
        ctrl = next(r for r in rows if r["is_control"])
        cov = [r for r in rows if not r["is_control"]]
        solved = [r for r in cov if r["solved"]]
        # file order varies between runs, so ties are broken on the start itself
        best = min(solved, default=None, key=lambda r: (
            r["nodes_explored"], r["path_length"], r["z_word"],
            json.dumps(r["pattern"]), r["iso_gen"], r["iso_index"]))
        n = {"cheaper": 0, "equal": 0, "dearer": 0, "unsolved": 0}
        for r in cov:
            if not r["solved"]:
                n["unsolved"] += 1
            elif not ctrl["solved"] or r["nodes_explored"] < ctrl["nodes_explored"]:
                n["cheaper"] += 1
            elif r["nodes_explored"] == ctrl["nodes_explored"]:
                n["equal"] += 1
            else:
                n["dearer"] += 1
        out.append({
            "pres_id": pid, "r1_orig": ctrl["r1_orig"], "r2_orig": ctrl["r2_orig"],
            "start_total_length_orig": ctrl["start_total_length_orig"],
            "node_budget": ctrl["node_budget"],
            "control_solved": int(ctrl["solved"]),
            "control_nodes": ctrl["nodes_explored"],
            "control_path_length": ctrl["path_length"] if ctrl["solved"] else "",
            "cov_starts": len(cov),
            "cov_one_pattern_starts": sum(bool(r["is_one_pattern"]) for r in cov),
            "cov_solved_starts": len(solved),
            "best_cov_nodes": best["nodes_explored"] if best else "",
            "best_cov_path_length": best["path_length"] if best else "",
            "best_cov_is_one_pattern": int(bool(best["is_one_pattern"])) if best else "",
            "best_cov_z_word": best["z_word"] if best else "",
            "best_cov_pattern": json.dumps(best["pattern"], separators=(",", ":")) if best else "",
            "best_cov_iso_gen": best["iso_gen"] if best else "",
            "best_cov_iso_index": best["iso_index"] if best else "",
            "best_cov_r1": best["r1"] if best else "",
            "best_cov_r2": best["r2"] if best else "",
            **{f"frac_{k}": round(v / len(cov), 6) if cov else "" for k, v in n.items()},
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    a = ap.parse_args()
    out = os.path.splitext(a.file)[0] + "_per_presentation.csv"
    rows = table(a.file)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} presentations")


if __name__ == "__main__":
    main()
