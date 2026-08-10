"""Short ≤1k scouts on a frozen 20-row AC1M hard holdout slice.

Scout-then-scale (see experiments/lessons/scout-then-scale-budgets.md):
  B) cap 24 vs 48 for L+w·S at the holdout-peak weight (w=20) and at w=24
  C) pure S vs recommended vs S+MK add-on (one add-on only)

Dataset: first 20 odd-idx length-hard rows from screen_length_ac1m.jsonl
(holdout half of the S-grid convention). Budget 1000. Serial in-process.

    python3 -m experiments.heuristic_search.runners.scout_s_cap_addon
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hfast import search_fast  # noqa: E402
from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402

ROOT = _d
SCREEN = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "screen_length_ac1m.jsonl")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "scouts")
OUT = os.path.join(OUT_DIR, "s_cap_addon_b1k.jsonl")
REPORT = os.path.join(OUT_DIR, "S_CAP_ADDON.md")
BUDGET = 1000
N_HOLD = 20


def _cfg(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


ARMS = {
    "length_c24": (_cfg(L=1.0), 24),
    "length_c48": (_cfg(L=1.0), 48),
    "s20_c24": (_cfg(L=1.0, S=20.0), 24),
    "s20_c48": (_cfg(L=1.0, S=20.0), 48),
    "s24_c24": (_cfg(L=1.0, S=24.0), 24),
    "s24_c48": (_cfg(L=1.0, S=24.0), 48),
    "recommended_c48": (RECOMMENDED, 48),
    "s20_mk8_c48": (_cfg(L=1.0, S=20.0, MK=8.0), 48),
    "s24_mk8_c48": (_cfg(L=1.0, S=24.0, MK=8.0), 48),
}


def _load_holdout20():
    hard = []
    with open(SCREEN) as f:
        for line in f:
            r = json.loads(line)
            if not r["solved"] and int(r["idx"]) % 2 == 1:
                hard.append(r)
    hard.sort(key=lambda r: r["idx"])
    return hard[:N_HOLD]


def _done(path):
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            seen.add((r["arm"], r["idx"]))
    return seen


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = _load_holdout20()
    if len(rows) < N_HOLD:
        raise RuntimeError(f"need {N_HOLD} holdout hard, got {len(rows)}")
    done = _done(OUT)
    print(f"[scout] {len(rows)} hard holdout; {len(ARMS)} arms; "
          f"{len(done)} resumed; budget={BUDGET}", flush=True)
    # JIT warm
    search_fast("X", "Y", 20, ARMS["s24_c48"][0], 48)
    t0 = time.time()
    n_new = 0
    with open(OUT, "a") as f:
        for rec in rows:
            for arm, (cfg, cap) in ARMS.items():
                key = (arm, rec["idx"])
                if key in done:
                    continue
                res = search_fast(rec["r1"], rec["r2"], BUDGET, cfg, cap)
                if int(res["nodes"]) > BUDGET:
                    raise RuntimeError("budget overrun")
                row = {
                    "arm": arm,
                    "idx": rec["idx"],
                    "r1": rec["r1"],
                    "r2": rec["r2"],
                    "L": rec["L"],
                    "solved": bool(res["solved"]),
                    "nodes": int(res["nodes"]),
                    "path": res["path_length"],
                    "budget": BUDGET,
                    "cap": cap,
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
                f.write(json.dumps(row) + "\n")
                f.flush()
                os.fsync(f.fileno())
                done.add(key)
                n_new += 1
                if n_new % 20 == 0:
                    print(f"  +{n_new} {n_new/max(time.time()-t0,1e-9):.2f}/s",
                          flush=True)
    _write_report(rows)
    print(f"[scout] new={n_new} wrote {REPORT}", flush=True)


def _write_report(rows):
    data = [json.loads(l) for l in open(OUT)]
    idxs = [r["idx"] for r in rows]
    lines = [
        "# Scout: S-arm cap + add-on (budget 1,000)",
        "",
        f"Frozen holdout slice: first {N_HOLD} odd-idx AC1M length-hard rows "
        f"from `screen_length_ac1m.jsonl` (idxs {idxs}).",
        "",
        "Scout-then-scale: short ≤1k only; scale winner on Colab via "
        "`hsearch_s24_scale.ipynb`.",
        "",
        "## Solved / 20",
        "",
        "| arm | solved | mean nodes (solved) | cap |",
        "|---|---:|---:|---:|",
    ]
    for arm in ARMS:
        d = [r for r in data if r["arm"] == arm and r["idx"] in idxs]
        sol = [r for r in d if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else float("nan")
        cap = ARMS[arm][1]
        mean_s = f"{mean_n:.1f}" if sol else "—"
        lines.append(f"| `{arm}` | **{len(sol)}/{len(d)}** | {mean_s} | {cap} |")
    lines += [
        "",
        "## Readout (no fitting)",
        "",
        "- Cap: compare `s20_c24` vs `s20_c48` and `s24_c24` vs `s24_c48`.",
        "- Add-on: compare pure `s20_c48`/`s24_c48` vs `*_mk8_c48` and "
        "`recommended_c48`.",
        "- Scale the best pure-or-addon arm; do not raise agent budget above 1k.",
        "",
        f"Raw: [`s_cap_addon_b1k.jsonl`](s_cap_addon_b1k.jsonl).",
        "",
    ]
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
