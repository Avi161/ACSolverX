"""Full table at a larger budget: rows solved at the smaller budget are carried (deterministic search, nothing
pruned: the same result at any larger budget), unsolved rows are replaced by their rerun.
  python benchmark/ryan/merge.py results/ryan_1e5 results/ryan_1e6 results/ryan_full_1e6
"""
import json
import sys
from pathlib import Path

base, rerun, out = map(Path, sys.argv[1:4])
out.mkdir(parents=True, exist_ok=True)
for f in sorted(base.glob("*__*.jsonl")):
    re = {}
    if (rerun / f.name).exists():
        re = {r["id"]: r for r in map(json.loads, (rerun / f.name).read_text().splitlines())}
    lines = []
    for r in map(json.loads, f.read_text().splitlines()):
        if not r["solved"]:
            r = re[r["id"]]  # every unsolved row must have a rerun
        else:
            r["carried_from"] = base.name
        lines.append(json.dumps(r, separators=(",", ":")))
    (out / f.name).write_text("\n".join(lines) + "\n")
    print(f.name, len(lines))
