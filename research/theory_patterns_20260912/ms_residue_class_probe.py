"""Compare residue-normalized original MS cells with saved U124 class lengths."""

import csv
import json
from pathlib import Path
import time

from .ac_words import canon
from .check_complement import sha256
from .endpoint_gates import ms_matches
from .endpoint_nielsen import descend
from .ms_family_verify import R, S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def balanced(value, modulus):
    remainder = value % modulus
    choices = {remainder, remainder - modulus}
    best = min(abs(x) for x in choices)
    return sorted(x for x in choices if abs(x) == best)


def main():
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    grid_path = ROOT / "data/ms_unsolved_reps/ms_solved_grid.csv"
    best_path = ROOT / "data/ms_unsolved_reps/aca_124_best.csv"
    classes = list(csv.DictReader(best_path.open()))
    members = {member: row for row in classes for member in row["members"].split()}
    cache, outcomes = {}, []
    grid_rows = [row for row in csv.DictReader(grid_path.open()) if row["w"]]
    assert len(grid_rows) == 170 and all(set(row["w"]) <= set("xXyY") for row in grid_rows)
    for grid in grid_rows:
        for n in range(1, 8):
            member = grid[str(n)]
            if member == "trivial":
                continue
            parent = members[member]
            raw = (R(n), "X" + grid["w"])
            pair = tuple(canon(word) for word in raw)
            matches = ms_matches(pair)
            attempts = []
            for match in matches:
                m, r, s = match["n"], match["r"], match["s"]
                for rr in balanced(r, m):
                    for ss in balanced(s, m + 1):
                        key = (m, rr, ss)
                        if key not in cache:
                            endpoint, trace, charges, complete = descend((R(m), S(0, rr, ss)), 1000)
                            cache[key] = {"residue_pair": [R(m), S(0, rr, ss)], "endpoint": endpoint,
                                          "endpoint_length": sum(map(len, endpoint)), "trace": trace,
                                          "image_evaluations": charges, "complete": complete}
                        attempts.append({"match": match, "residues": [rr, ss], "normalization": cache[key]})
            if attempts:
                winner = min(attempts, key=lambda a: a["normalization"]["endpoint_length"])
                starting = len(parent["r1"]) + len(parent["r2"])
                outcomes.append({"aca_id": parent["name"], "member_name": member,
                                 "ms_cell": {"n": n, "w": grid["w"]}, "original_ms_pair": raw,
                                 "u124_starting_length": starting, "winner": winner,
                                 "potential_gain": starting - winner["normalization"]["endpoint_length"]})
    result = {"status": "original_cell_theorem_scope_probe", "grid_sha256": sha256(grid_path),
              "best_input_sha256": sha256(best_path), "script_sha256": sha256(Path(__file__)),
              "matched_unsolved_cells": len(outcomes), "distinct_u124_components": len({r["aca_id"] for r in outcomes}),
              "unique_residue_targets": len(cache), "image_evaluations": sum(v["image_evaluations"] for v in cache.values()),
              "potential_gain_ids": sorted({r["aca_id"] for r in outcomes if r["potential_gain"] > 0}),
              "rows": outcomes, "cpu_seconds": time.process_time() - start_cpu,
              "wall_seconds": time.perf_counter() - start_wall,
              "scope": "Original MS cells joined to U124 through the frozen grid/member labels. Any shorter result is a candidate pending explicit source-to-current-U124 bridge verification and parameter certificate; this diagnostic alone does not alter the certified table."}
    (HERE / "ms_residue_class_probe.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
