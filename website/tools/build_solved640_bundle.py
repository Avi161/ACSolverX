#!/usr/bin/env python3
"""Build the baseline + 640-solved z=w website bundles for the AC-SolverX Path Explorer.

READS the repo's results/ tree; WRITES only into website/sample-data/. Idempotent — safe to
re-run whenever a new local/cloud run lands.

Emits / updates in website/sample-data/:
  calibration_baseline.jsonl / paths_baseline.jsonl
      the 2-generator GS-Sub BASELINE over the 640 solved MS(1190) (arm "baseline", n_gen 2).
      Source: results/solved640/ if present (matched 500k budget), else results/baseline_greedy/ (1M).
  calibration_ms640.jsonl / paths_ms640.jsonl  (r1,r2,x,y rows ONLY)
      REPLACE the ms640 bundle's r1/r2/x/y rows with the complete 500k run from the organized results
      tree (results/stable_ac/3_generators_w_choices/ms640/), and PRUNE every other arm (the leftover
      g@12k rows) — the four z=w words are the real results; anything else is a stale probe.
  (deletes) calibration_words.jsonl / paths_words.jsonl
      the xY/yx/Xy 12k probe arms — redundant; git history preserves them.
  manifest.json : append the two baseline files, drop the words files; refresh label.

BUILD ORDER: run build_reps_bundle.py FIRST (it annotates registry_1190MS.jsonl with
rep_idx/class_name), then this tool (prunes arms, writes the final manifest label).

Run from anywhere:  python website/tools/build_solved640_bundle.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "website", "sample-data")
R_640 = os.path.join(ROOT, "results", "solved640")
R_BASE = os.path.join(ROOT, "results", "baseline_greedy")
R_ORG = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ms640")

MS_SPLIT = 640
Z_ARMS = ["r1", "r2", "x", "y"]   # all four relator arms, now complete @500k from the organized results


def org_src(kind, arm):
    """Source path in the organized 3-gen results tree (runs/ = calibration, paths/ = paths)."""
    sub = "runs" if kind == "calibration" else "paths"
    return os.path.join(R_ORG, sub, f"{kind}_{arm}.jsonl")


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
    """kind: 'calibration' or 'paths'. Replace the r1/r2/x/y rows in the ms640 bundle with the
    complete 500k run from the organized results tree. Only those four arms are kept — every
    other arm is dropped by prune_bundle(). No-op if the organized tree is absent."""
    if not any(os.path.exists(org_src(kind, arm)) for arm in Z_ARMS):
        return None  # organized 500k arms not available yet
    bundle = os.path.join(OUT, f"{kind}_ms640.jsonl")
    kept = [r for r in read_jsonl(bundle) if r.get("arm") not in Z_ARMS]
    added = 0
    for arm in Z_ARMS:
        for r in read_jsonl(org_src(kind, arm)):
            if r.get("dataset") == "1190MS" and r.get("idx", 0) < MS_SPLIT:
                kept.append(clean(r))
                added += 1
    write_jsonl(bundle, kept)
    return added


def prune_bundle():
    """Drop the redundant probe arms from the bundle. Operates purely on sample-data (works
    even when results/ is absent): keeps only r1/r2/x/y rows in the ms640 files and removes
    the words files (xY/yx/Xy @12k) from disk entirely."""
    keep = set(Z_ARMS)
    for kind in ("calibration", "paths"):
        fp = os.path.join(OUT, f"{kind}_ms640.jsonl")
        rows = read_jsonl(fp)
        kept = [r for r in rows if r.get("arm") in keep]
        if len(kept) != len(rows):
            write_jsonl(fp, kept)
        print(f"  prune ms640 {kind}: {len(rows)} -> {len(kept)} rows (arms {sorted(keep)})")
    for name in ("calibration_words.jsonl", "paths_words.jsonl"):
        fp = os.path.join(OUT, name)
        if os.path.exists(fp):
            os.remove(fp)
            print(f"  removed {name}")


def update_manifest():
    fp = os.path.join(OUT, "manifest.json")
    m = json.load(open(fp))
    for name in ["calibration_baseline.jsonl", "paths_baseline.jsonl"]:
        if name not in m["files"]:
            m["files"].append(name)
    m["files"] = [n for n in m["files"] if n not in ("calibration_words.jsonl", "paths_words.jsonl")]
    m["label"] = ("MS(1190): original 640 (2-gen baseline + z ∈ {r₁,r₂,x,y} @500k) + "
                  "hard 550 via 261 unsolved-class reps (0 solved @500k)")
    with open(fp, "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")


def main():
    print("build_solved640_bundle ->", os.path.relpath(OUT, ROOT))
    build_baseline()
    for kind in ("calibration", "paths"):
        added = replace_arms_in_ms640(kind)
        if added is None:
            print(f"  ms640 {kind}: organized r1/r2/x/y not present — kept existing rows")
        else:
            print(f"  ms640 {kind}: replaced r1/r2/x/y with {added} @500k rows")
    prune_bundle()
    update_manifest()
    print("OK — manifest updated")


if __name__ == "__main__":
    main()
