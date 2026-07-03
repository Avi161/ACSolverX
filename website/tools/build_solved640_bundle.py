#!/usr/bin/env python3
"""Build the baseline + 640-solved z=w website bundles for the AC-SolverX Path Explorer.

READS the repo's results/ tree; WRITES only into website/sample-data/. Idempotent — safe to
re-run whenever a new local/cloud run lands.

Emits / updates in website/sample-data/:
  calibration_baseline.jsonl / paths_baseline.jsonl
      the 2-generator GS-Sub BASELINE over the 640 solved MS(1190) (arm "baseline", n_gen 2).
      Source: results/solved640/ if present (matched 500k budget), else results/baseline_greedy/ (1M).
  calibration_ms640.jsonl / paths_ms640.jsonl  (r1,r2 rows only)
      if results/solved640/ has the r1/r2 @500k run, REPLACE the stale 12k r1/r2 rows in the ms640
      bundle with it (leaving x,y,g at 12k untouched) — one budget per arm, so the viewer's byIdx
      arm map has no r1/r2 budget collision. Skipped (12k r1/r2 kept) until that run lands.
  manifest.json : append the two baseline files; refresh label.

Run from anywhere:  python website/tools/build_solved640_bundle.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "website", "sample-data")
R_640 = os.path.join(ROOT, "results", "solved640")
R_BASE = os.path.join(ROOT, "results", "baseline_greedy")

MS_SPLIT = 640
Z_ARMS = ["r1", "r2"]   # the arms this run replaces in ms640 (x,y,g stay at 12k)


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path):
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # tolerate a trailing truncated line
    return rows


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def clean(rec):
    rec = dict(rec)
    rec.pop("_source_file", None)   # provenance field the bundled files never carry
    return rec


def solved640_first(name):
    """Prefer the matched-budget solved640 file; fall back to the 1M baseline dir for baseline."""
    p640 = os.path.join(R_640, "solved" if name.startswith("calibration") else "paths", name)
    if os.path.exists(p640):
        return p640, "solved640"
    if name.endswith("baseline.jsonl"):
        sub = "solved" if name.startswith("calibration") else "paths"
        pbase = os.path.join(R_BASE, sub, name)
        if os.path.exists(pbase):
            return pbase, "baseline_greedy(1M)"
    return None, None


def build_baseline():
    calib_src, src_tag = solved640_first("calibration_baseline.jsonl")
    if not calib_src:
        print("  baseline: no source found (results/solved640 or results/baseline_greedy) — skipped")
        return 0
    paths_src, _ = solved640_first("paths_baseline.jsonl")
    calib = [clean(r) for r in read_jsonl(calib_src)
             if r.get("dataset") == "1190MS" and r.get("idx", 0) < MS_SPLIT]
    paths = [clean(r) for r in read_jsonl(paths_src or "")
             if r.get("dataset") == "1190MS" and r.get("idx", 0) < MS_SPLIT]
    write_jsonl(os.path.join(OUT, "calibration_baseline.jsonl"), calib)
    write_jsonl(os.path.join(OUT, "paths_baseline.jsonl"), paths)
    solved = sum(1 for r in calib if r.get("solved"))
    print(f"  baseline [{src_tag}]: {len(calib)} calib ({solved} solved), {len(paths)} paths")
    return len(calib)


def replace_arms_in_ms640(kind):
    """kind: 'calibration' or 'paths'. Replace r1/r2 rows in the ms640 bundle with the solved640
    @500k run, if present; leave x,y,g untouched. No-op if the run hasn't landed."""
    n_new = 0
    for arm in Z_ARMS:
        src = os.path.join(R_640, "solved" if kind == "calibration" else "paths",
                           f"{kind}_{arm}.jsonl")
        if os.path.exists(src):
            n_new += 1
    if n_new == 0:
        return None  # solved640 r1/r2 not available yet
    bundle = os.path.join(OUT, f"{kind}_ms640.jsonl")
    kept = [r for r in read_jsonl(bundle) if r.get("arm") not in Z_ARMS]
    added = 0
    for arm in Z_ARMS:
        src = os.path.join(R_640, "solved" if kind == "calibration" else "paths",
                           f"{kind}_{arm}.jsonl")
        for r in read_jsonl(src):
            if r.get("dataset") == "1190MS" and r.get("idx", 0) < MS_SPLIT:
                kept.append(clean(r))
                added += 1
    write_jsonl(bundle, kept)
    return added


def update_manifest():
    fp = os.path.join(OUT, "manifest.json")
    m = json.load(open(fp))
    for name in ["calibration_baseline.jsonl", "paths_baseline.jsonl"]:
        if name not in m["files"]:
            m["files"].append(name)
    m["label"] = ("MS(1190) original 640 + hard 550 · 2-gen baseline vs z ∈ {r₁,r₂,x,y,g,xY,yx,Xy} "
                  "on the 640 solved · 261 unsolved-class reps")
    with open(fp, "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")


def main():
    print("build_solved640_bundle ->", os.path.relpath(OUT, ROOT))
    build_baseline()
    for kind in ("calibration", "paths"):
        added = replace_arms_in_ms640(kind)
        if added is None:
            print(f"  ms640 {kind}: r1/r2 @500k not present yet — kept 12k rows")
        else:
            print(f"  ms640 {kind}: replaced r1/r2 with {added} @500k rows")
    update_manifest()
    print("OK — manifest updated")


if __name__ == "__main__":
    main()
