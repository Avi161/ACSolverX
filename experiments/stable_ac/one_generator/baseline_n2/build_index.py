"""Report-time — merge the Phase 0.5 streams into a minimum-path-length index.

For every idx solved (and path-verified) by ANY stream, record the MINIMUM path_len
found across the streams and which stream achieved it. Greedy is best-first on relator
length (not depth), so per-stream path_len is the found (not provably shortest) path;
the min across streams/budgets is the best known. Only verified solves are counted.

    python build_index.py                       # reads results/greedy_*.jsonl
    -> results/solved_path_len_index.json
"""
import argparse
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_RESULTS = os.path.join(ROOT, "results")
STREAMS = [
    "greedy_reprogate_100k.jsonl",
    "greedy_reprogate_1m.jsonl",
    "greedy_baseline_100k.jsonl",
    "greedy_baseline_1m.jsonl",
]


def build(results_dir):
    index = {}  # idx -> {min_path_len, from_stream, path_verified: True}
    per_stream_counts = {}
    for name in STREAMS:
        path = os.path.join(results_dir, name)
        if not os.path.exists(path):
            continue
        solved_here = 0
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not (obj.get("solved") and obj.get("path_verified")):
                    continue
                solved_here += 1
                idx = obj["idx"]
                plen = obj["path_len"]
                cur = index.get(idx)
                if cur is None or plen < cur["min_path_len"]:
                    index[idx] = {"min_path_len": plen, "from_stream": name, "path_verified": True}
        per_stream_counts[name] = solved_here
    return index, per_stream_counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=DEFAULT_RESULTS)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or os.path.join(args.results, "solved_path_len_index.json")

    index, counts = build(args.results)
    # stable, human-scannable ordering by idx
    ordered = {str(idx): index[idx] for idx in sorted(index)}
    with open(out, "w") as f:
        json.dump(ordered, f, indent=0)

    print(f"OK: {len(ordered)} distinct solved+verified idx -> {os.path.relpath(out, ROOT)}")
    for name, c in counts.items():
        print(f"    {name}: {c} solved+verified")


if __name__ == "__main__":
    main()
