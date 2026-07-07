#!/usr/bin/env python3
"""Build sample-data/offline_bundle.js for file:// loading in the Path Explorer.

Browsers block fetch() on file:// URLs. This script merges manifest-listed JSONL
records plus reps_grid.json and ak3_test.json into one script-tag-loadable bundle.

Run from anywhere:
    python ACSolverX/website/tools/build_offline_bundle.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE = os.path.join(ROOT, "website", "sample-data")
MANIFEST = os.path.join(SAMPLE, "manifest.json")
OUT = os.path.join(SAMPLE, "offline_bundle.js")


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def read_json(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def main():
    if not os.path.exists(MANIFEST):
        raise SystemExit(f"missing {MANIFEST} — run build_reps_bundle.py then build_solved640_bundle.py first")

    with open(MANIFEST) as f:
        manifest = json.load(f)

    records = []
    for name in manifest.get("files") or []:
        path = os.path.join(SAMPLE, name)
        chunk = read_jsonl(path)
        records.extend(chunk)
        print(f"  {name}: {len(chunk)} records")

    reps_grid = read_json(os.path.join(SAMPLE, "reps_grid.json"))
    ak3 = read_json(os.path.join(SAMPLE, "ak3_test.json"))

    bundle = {
        "manifest": manifest,
        "records": records,
        "repsGrid": reps_grid,
        "ak3": ak3,
    }

    os.makedirs(SAMPLE, exist_ok=True)
    with open(OUT, "w") as f:
        f.write("window.__ACX_OFFLINE__=")
        json.dump(bundle, f, separators=(",", ":"))
        f.write(";\n")

    size_mb = os.path.getsize(OUT) / (1024 * 1024)
    print(f"wrote {os.path.relpath(OUT, ROOT)}  ({len(records)} records, {size_mb:.1f} MB)")


if __name__ == "__main__":
    print("build_offline_bundle ->", os.path.relpath(OUT, ROOT))
    main()
    print("OK")
