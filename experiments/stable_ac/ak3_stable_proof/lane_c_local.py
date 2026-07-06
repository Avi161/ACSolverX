"""Lane C (mentor baseline #2): trivial-z stabilization <x,y,z | r1, r2, z> on both
AK(3) forms, solved with the verified n-relator greedy. The empty word w (z-relator =
[z]) was NOT in any previously swept bank. 4/5-generator variants are handled by the
Colab notebook (they need the NGEN_MAX byte-table bump).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    sys.path.insert(0, p)

import numpy as np  # noqa: E402
import greedy_nrel as gn  # noqa: E402

RUNS = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof", "runs")

FORMS = {
    "textbook": ([1, 2, 1, -2, -1, -2], [1, 1, 1, -2, -2, -2, -2]),
    "rep": ([-2, -1, 2, -1, -2, 1], [-2, -2, -2, -1, -1, -1, -1]),
}


def main():
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    os.makedirs(RUNS, exist_ok=True)
    out = os.path.join(RUNS, "lane_c_trivial_z.jsonl")
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                r = json.loads(line)
                done.add((r["form"], r["budget"]))
            except Exception:
                pass
    with open(out, "a") as f:
        for form, (r1, r2) in FORMS.items():
            if (form, budget) in done:
                print(f"skip {form}@{budget} (done)")
                continue
            relators = [np.array(r1, dtype=gn.INT_DTYPE),
                        np.array(r2, dtype=gn.INT_DTYPE),
                        np.array([3], dtype=gn.INT_DTYPE)]
            solver = gn.NRelatorSolver(relators, 3, max_nodes=budget, max_len=gn.L)
            t0 = time.time()
            path, nodes, _ = solver.solve()
            dt = time.time() - t0
            rec = {"form": form, "arm": "trivial_z_3gen", "budget": budget,
                   "solved": path is not None, "nodes": nodes,
                   "min_total_len": solver.min_total_len,
                   "wall_s": round(dt, 1)}
            if path is not None:
                rec["path_verified"] = bool(gn.verify_path(path["states"], 3))
                rec["path_len"] = len(path["states"]) - 1
                sidecar = os.path.join(RUNS, f"lane_c_path_{form}.jsonl")
                gn.write_path_sidecar(sidecar, gn.serialize_path(path, 0, name=form))
                rec["path_file"] = sidecar
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())
            print(rec)


if __name__ == "__main__":
    main()
