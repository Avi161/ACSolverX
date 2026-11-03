"""Compare the numba kernel (cov_gates_numba.py) with the verified pure-Python port (cov_gates_cpu.py).

Every field of the result and the whole path must be equal, for every row and gate given.
  python benchmark/ryan/check_numba.py --rows 0:640:7 --nodes 3000
"""
import argparse
import ast
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cov_gates_cpu as C  # noqa: E402
import cov_gates_numba as K  # noqa: E402

FIELDS = ["solved", "termination", "nodes_visited", "states_seen", "path_length", "path_sub_moves", "path_cov_moves",
          "max_relator_len", "max_total_len", "actions", "gate_checks", "gate_openings", "cov_actions_enumerated",
          "cov_changed_in_cap_actions", "cov_shortening_actions", "cov_shortening_unique_per_parent_sum",
          "gate_openings_with_shortening", "best_popped_length"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(HERE.parents[1] / "data/ms640_solved.txt"))
    ap.add_argument("--rows", default="0:640:7", help="start:end:step")
    ap.add_argument("--nodes", type=int, default=3000)
    ap.add_argument("--gates", default=",".join(C.GATES))
    ap.add_argument("--uncapped", action="store_true", help="compare with no length caps instead of Ryan's 24/48")
    a = ap.parse_args()
    lines = [l for l in Path(a.input).read_text().splitlines() if l.strip()]
    s, e, st = (list(map(int, a.rows.split(":"))) + [1])[:3]
    caps = (None, None) if a.uncapped else (24, 48)
    C.set_caps(*caps)
    K.search(C.start_key_from_row(ast.literal_eval(lines[0])), "periodic10", 50, *caps)  # compile
    n = bad = 0
    tp = tk = 0.0
    for idx in range(s, min(e, len(lines)), st):
        key = C.start_key_from_row(ast.literal_eval(lines[idx]))
        for gate in a.gates.split(","):
            t = time.monotonic(); r = C.search(key, gate, a.nodes, 1e9); tp += time.monotonic() - t
            t = time.monotonic(); m = K.search(key, gate, a.nodes, *caps); tk += time.monotonic() - t
            diff = {f: (r[f], m[f]) for f in FIELDS if r[f] != m[f]}
            if r["path"] != m["path"]:
                diff["path"] = "differs"
            n += 1
            if diff:
                bad += 1
                if bad <= 10:
                    print("DIFF", idx, gate, {k: v for k, v in diff.items() if k != "actions"}, flush=True)
    print(f"searches {n}, differing {bad}; python {tp:.1f}s, numba {tk:.1f}s, speedup {tp / max(tk, 1e-9):.0f}x")


if __name__ == "__main__":
    main()
