"""After the 10h wall: write COLAB_RECOMMENDATION.md and stamp the 5×51GB notebooks.

Reads scale10k / extra_arms / ak3 / more_mini results; picks arms + budget for
five parallel Colab High-RAM (≈51 GB) sessions.

    python3 -m experiments.heuristic_search.runners.finalize_colab_handoff
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

ROOT = _d
OUT = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                   "COLAB_RECOMMENDATION.md")
SCALE = os.path.join(ROOT, "results", "heuristic_search", "scale10k")


def _load_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if "error" in r:
            continue
        rows.append(r)
    return rows


def _curve(rows, arm, checkpoints):
    rs = [r for r in rows if r.get("arm") == arm]
    n = len(rs)
    out = []
    for c in checkpoints:
        k = f"solved_le_{c}"
        if any(k in r for r in rs):
            out.append(sum(1 for r in rs if r.get(k)))
        else:
            out.append(sum(1 for r in rs if r.get("solved_at") is not None
                           and r["solved_at"] <= c))
    return n, out


def main():
    any_rows = _load_jsonl(os.path.join(SCALE, "anytime_b10k.jsonl"))
    extra = _load_jsonl(os.path.join(SCALE, "extra_arms_b10k.jsonl"))
    by_slice = defaultdict(list)
    for r in any_rows:
        by_slice[r.get("slice", "?")].append(r)

    # Decide arms from fresh_hard @10k (reach) + L-stratified (headline)
    hard = by_slice.get("fresh_hard", [])
    cps = (1000, 2000, 5000, 10000)
    hard_scores = {}
    for arm in ("length", "s12", "s20", "recommended"):
        n, c = _curve(hard, arm, cps)
        if n:
            hard_scores[arm] = (c[-1], c[0], n)

    # extra arms on L-stratified
    extra_scores = {}
    for arm in sorted({r["arm"] for r in extra}):
        n, c = _curve(extra, arm, (1000, 5000, 10000))
        if n:
            extra_scores[arm] = (c[-1], c[0], n)

    # Pick primary S weight: best @10k on fresh_hard among s12/s20; fallback s20
    primary = "s20"
    if hard_scores:
        cand = {a: hard_scores[a] for a in ("s12", "s20") if a in hard_scores}
        if cand:
            primary = max(cand, key=lambda a: (cand[a][0], cand[a][1]))
    # secondary from extra if clearly better on L-slice @10k
    secondary = None
    if extra_scores:
        best_extra = max(extra_scores, key=lambda a: extra_scores[a][0])
        if best_extra.startswith("s") and best_extra not in (primary,):
            secondary = best_extra

    arms = ["baseline", primary]
    if secondary:
        arms.append(secondary)
    # different family
    arms.append("recommended")

    # Budget for 10–20h × 5 sessions × ~6 workers @51GB
    # EXP-28 Colab: ~400–650 pops/s. Matched-wall rich arms slower.
    # budget ≈ wall_h * 3600 * workers * pops_s / (arms * rows_per_session)
    # 15h * 3600 * 6 * 450 / (3 * 25) ≈ 1.9e5 → recommend 200_000
    node_budget = 200_000
    checkpoints = [1000, 5000, 10000, 25000, 50000, 100000, 200000]

    lines = [
        "# COLAB_RECOMMENDATION — 5× High-RAM (≈51 GB) sessions",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}` after 10h mini-research wall.",
        "",
        "## What to run",
        "",
        "Open **five** notebooks (one Colab High-RAM runtime each):",
        "",
        "| session | notebook | `CHUNK_INDEX` |",
        "|---:|---|---:|",
    ]
    for i in range(1, 6):
        lines.append(
            f"| {i} | "
            f"`experiments/heuristic_search/hsearch_colab_5x51_c{i}.ipynb` "
            f"| **{i}** |")
    lines += [
        "",
        "All five share `CHUNKS=5`, same `ARMS` / `NODE_BUDGET`. Stride sharding "
        "is result-neutral; merge jsonls after (concat is fine — rows keyed by "
        "`(arm, name)`).",
        "",
        "## Frozen CONFIG (edit only `CHUNK_INDEX` per session — already set)",
        "",
        "```python",
        f"ARMS      = {arms!r}",
        "DATASET   = \"unsolved124\"   # primary target; also run bench66 if time",
        f"NODE_BUDGET = {node_budget:_}",
        f"CHECKPOINTS = {checkpoints}",
        "MAX_RELATOR_LENGTH = 64     # EXP-12 parity on the 124",
        "ENGINE    = \"hcompact\"      # REQUIRED for multi-worker @ this RAM",
        "KEEP_PATH = True",
        "N_WORKERS = \"auto\"          # memory-capped; expect ~6 on 51 GB @200k",
        "CHUNKS    = 5",
        "RESUME    = True",
        "```",
        "",
        "## Why these arms / budget",
        "",
        f"- Primary S-arm from fresh_hard @10k: **`{primary}`** "
        f"(scores={hard_scores}).",
        f"- Extra L-slice @10k: {extra_scores}.",
        f"- Secondary S (if any): `{secondary}`.",
        "- `recommended` kept as different-family control (not another S weight).",
        "- `baseline` = length-only control.",
        f"- Budget **{node_budget:_}**: sized for ~10–20 h wall × 5 sessions × "
        "~6 workers using EXP-28 Colab pops/s (~400–650), not this host's rates.",
        "- Per search RAM @200k hcompact ≪ 51 GB; workers are core/memory auto-capped.",
        "",
        "## High-speedup checklist (already in the notebooks)",
        "",
        "- `ENGINE=hcompact` (~78 B/state)",
        "- spawn workers + parent-only jsonl writes + local stage + Drive whole-file mirror",
        "- flock on stage (no double-compute on Restart)",
        "- time-based heartbeat",
        "- Drive path under `/content/drive/MyDrive/...` only",
        "",
        "## After all five finish",
        "",
        "Copy the five `*.jsonl` from Drive into one folder and:",
        "",
        "```bash",
        "python3 -m experiments.heuristic_search.runners.merge_colab_chunks \\",
        "  --glob 'hsearch_colab5_c*of5_*.jsonl' --out merged_colab5.jsonl",
        "```",
        "",
        "Hand the merged file (+ per-chunk files) back into the repo under "
        "`results/hsearch/`.",
        "",
        "## AK(3) note",
        "",
        "AK3 proofs-inspired mini-runs did **not** produce a solve or minL<13 at "
        "≤10k. Do **not** burn the 5×51GB fleet on AK3 until a scout shows "
        "dynamic range; keep this fleet on `unsolved124` / hard AC1M if extended.",
        "",
    ]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {OUT}", flush=True)
    # stamp notebooks' DRAFT banner removal if present
    _stamp_notebooks(arms, node_budget, checkpoints)


def _stamp_notebooks(arms, budget, checkpoints):
    import glob
    for path in sorted(glob.glob(os.path.join(
            ROOT, "experiments", "heuristic_search",
            "hsearch_colab_5x51_c*.ipynb"))):
        nb = json.load(open(path))
        src = "".join(nb["cells"][0]["source"])
        # replace DRAFT line and key assignments if markers exist
        lines = src.splitlines(keepends=True)
        out = []
        for line in lines:
            if line.startswith("# DRAFT"):
                out.append(
                    "# READY — see results/heuristic_search/scale10k/"
                    "COLAB_RECOMMENDATION.md\n")
                continue
            if line.strip().startswith("ARMS"):
                out.append(f"    ARMS      = {arms!r},\n")
                continue
            if line.strip().startswith("NODE_BUDGET"):
                out.append(f"    NODE_BUDGET = {budget:_},\n")
                continue
            if line.strip().startswith("CHECKPOINTS"):
                out.append(f"    CHECKPOINTS = {checkpoints},\n")
                continue
            if line.strip().startswith("MAX_RELATOR_LENGTH"):
                out.append("    MAX_RELATOR_LENGTH = 64,\n")
                continue
            out.append(line)
        nb["cells"][0]["source"] = out
        json.dump(nb, open(path, "w"), indent=1)
        print(f"stamped {path}", flush=True)


if __name__ == "__main__":
    main()
