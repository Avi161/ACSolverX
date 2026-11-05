"""cov_full_numba against cov_full (Python): the CoV children of many states, then whole searches, record by record.

  python benchmark/ryan/check_full_numba.py [--states 3000] [--budget 3000] [--rows 40]
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cov_full as F  # noqa: E402
import cov_full_numba as N  # noqa: E402
import cov_gates_cpu as C  # noqa: E402
from run_all import rows  # noqa: E402

ROOT = HERE.parents[1]
SKIP = {"elapsed_sec", "img_seconds"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", type=int, default=3000)
    ap.add_argument("--budget", type=int, default=3000)
    ap.add_argument("--rows", type=int, default=40)
    a = ap.parse_args()
    random.seed(0)
    states = set()
    for f in sorted((ROOT / "results/ryan_full_1e6").glob("*.jsonl")):
        for r in map(json.loads, f.read_text().splitlines()):
            for p in r["path"]:
                rels = tuple(tuple(w) for w in p["relators"])
                if rels[0] and rels[1]:
                    states.add(C.canonical_key(*rels))
    states = sorted(states)
    random.shuffle(states)
    bad = n_img = 0
    t_py = t_nb = 0.0
    for key in states[:a.states]:
        t = time.perf_counter()
        want = [k for k, _ in F.images(key)]
        t_py += time.perf_counter() - t
        t = time.perf_counter()
        got = N.children_of(key)
        t_nb += time.perf_counter() - t
        n_img += len(want)
        bad += got != want
    print(f"children: {min(a.states, len(states))} states, {n_img} images, {bad} mismatches; "
          f"python {t_py:.1f}s numba {t_nb:.1f}s", flush=True)
    picks = rows("ms640")[::max(1, 640 // a.rows)] + rows("ladder100")[::10]
    bad_s = 0
    t_py = t_nb = 0.0
    for rid, key, _ in picks:
        t = time.perf_counter()
        want = F.search(key, "no_short_sub", a.budget, "full")
        t_py += time.perf_counter() - t
        t = time.perf_counter()
        got = N.search(key, "no_short_sub", a.budget)
        t_nb += time.perf_counter() - t
        diff = [k for k in want if k not in SKIP and want[k] != got.get(k)]
        if diff:
            bad_s += 1
            print("MISMATCH", rid, diff, {k: (want[k], got.get(k)) for k in diff if k != "path"}, flush=True)
    print(f"searches: {len(picks)} at {a.budget} units, {bad_s} mismatches; python {t_py:.1f}s numba {t_nb:.1f}s")
    print("ALL SAME" if not bad and not bad_s else "DIFFERENT")


if __name__ == "__main__":
    main()
