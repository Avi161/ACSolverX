"""Build ``data/AC19_extended_aut_min.csv`` — one Aut(F₂)-minimal rep per orbit.

Reads ``data/AC19_extended.txt`` (flat 48-int lines), canonicalises each
presentation with ``aut_min`` (Whitehead / Aut(F₂) minimal form), and emits
one row per distinct Aut-orbit in the same schema as
``data/ms_unsolved_reps/aca_124.csv``:

    name,r1,r2,n_members,members

``members`` are 0-based line indices into ``AC19_extended.txt``.
``r1,r2`` are the Aut-minimal representative (not a raw member root).

    PYTHONPATH=. .venv/bin/python3 -m experiments.equivalence_classes.pipeline.make_ac19_extended_aut_min
"""
from __future__ import annotations

import ast
import csv
import os
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.run_baseline import int_line_to_relators  # noqa: E402
from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402

ROOT = _d
SRC = os.path.join(ROOT, "data", "AC19_extended.txt")
OUT = os.path.join(ROOT, "data", "AC19_extended_aut_min.csv")
# also mirror to the workspace-root data/ if this is a worktree with a
# separate copy (user path /workspace/data/...).
WORKSPACE_OUT = "/workspace/data/AC19_extended_aut_min.csv"


def _rep_key(rep):
    return rep[0] + "\0" + rep[1]


def main():
    warm()
    t0 = time.time()
    # key -> {r1, r2, mu, members: [idx, ...], first: idx}
    orbits = {}
    n_in = 0
    with open(SRC) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ints = ast.literal_eval(line)
            r1, r2 = int_line_to_relators(ints)
            mu, rep = aut_min((r1, r2))
            key = _rep_key(rep)
            row = orbits.get(key)
            if row is None:
                orbits[key] = {
                    "r1": rep[0], "r2": rep[1], "mu": mu,
                    "members": [n_in], "first": n_in,
                }
            else:
                row["members"].append(n_in)
            n_in += 1
            if n_in % 5000 == 0:
                rate = n_in / max(time.time() - t0, 1e-9)
                print(f"  {n_in} rows → {len(orbits)} orbits "
                      f"({rate:.0f}/s)", flush=True)

    ordered = sorted(orbits.values(), key=lambda r: r["first"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    def _write(path):
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "r1", "r2", "n_members", "members"])
            for i, row in enumerate(ordered):
                w.writerow([
                    f"ac19_{i}",
                    row["r1"],
                    row["r2"],
                    len(row["members"]),
                    " ".join(str(m) for m in row["members"]),
                ])

    _write(OUT)
    if os.path.isdir(os.path.dirname(WORKSPACE_OUT)):
        try:
            if os.path.abspath(OUT) != os.path.abspath(WORKSPACE_OUT):
                _write(WORKSPACE_OUT)
        except OSError as e:
            print(f"[warn] could not mirror to {WORKSPACE_OUT}: {e}", flush=True)

    dt = time.time() - t0
    print(
        f"[ac19-aut-min] input={n_in} unique_orbits={len(ordered)} "
        f"wrote={OUT} wall={dt:.1f}s "
        f"ts={datetime.now(timezone.utc).isoformat()}",
        flush=True,
    )
    # sanity: sum of members == n_in
    assert sum(len(r["members"]) for r in ordered) == n_in
    print(f"INITIAL: {n_in}", flush=True)
    print(f"AFTER Aut-min dedupe: {len(ordered)}", flush=True)


if __name__ == "__main__":
    main()
