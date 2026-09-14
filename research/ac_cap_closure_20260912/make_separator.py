"""Summarise minimal-cap ladders (run_min_cap.py output) as a separator table.

    python make_separator.py --u124 records/separator/u124_caps*.jsonl \
        --solved records/separator/solved60_caps*.jsonl --out records/separator/summary.json

Prints markdown tables and writes a JSON summary.  For every row the ladder
is reduced to: the largest cap at which the component was CLOSED and unsolved
(``closed_through``), the minimal solving cap if a SOLVED run exists
(``min_cap``), and whether the ladder ended on a budget-exhausted run.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json


def load(patterns):
    rows = collections.defaultdict(list)
    for pat in patterns:
        for path in sorted(glob.glob(pat)):
            with open(path) as fh:
                for line in fh:
                    if line.strip():
                        rec = json.loads(line)
                        rows[rec["name"]].append(rec)
    out = {}
    for name, recs in rows.items():
        recs.sort(key=lambda r: r["cap"])
        closed = [r["cap"] for r in recs if r["closed"] and not r["solved"]]
        solved = [r for r in recs if r["solved"]]
        budget = [r["cap"] for r in recs if r["budget_exhausted"]]
        states_at = {r["cap"]: r["states"] for r in recs}
        out[name] = {
            "r1": recs[0]["r1"], "r2": recs[0]["r2"],
            "floor": max(len(recs[0]["r1"]), len(recs[0]["r2"])),
            "total_length": len(recs[0]["r1"]) + len(recs[0]["r2"]),
            "bin": recs[0].get("bin"),
            "closed_through": max(closed) if closed else None,
            "min_cap": min(r["cap"] for r in solved) if solved else None,
            "path_length": min((len(r["path"]) for r in solved), default=None),
            "budget_at": min(budget) if budget else None,
            "states_at": states_at,
            "seconds": sum(r["seconds"] for r in recs),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--u124", nargs="+", required=True)
    ap.add_argument("--solved", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    u = load(args.u124)
    s = load(args.solved)

    print("## U124 rows (%d)\n" % len(u))
    ct = collections.Counter(v["closed_through"] for v in u.values())
    print("closed-through cap histogram:", dict(sorted(ct.items(), key=lambda kv: (kv[0] is None, kv[0]))))
    print("solved:", [n for n, v in u.items() if v["min_cap"] is not None])
    print("budget-exhausted:", [(n, v["budget_at"]) for n, v in u.items() if v["budget_at"]])
    top = sorted(u.items(), key=lambda kv: -max(kv[1]["states_at"].values()))[:10]
    print("\n| row | r1, r2 | total | closed through | states at top cap | CPU s |")
    print("|---|---|---:|---:|---:|---:|")
    for n, v in top:
        c = v["closed_through"]
        print("| %s | `%s`, `%s` | %d | %s | %s | %.1f |" % (
            n, v["r1"], v["r2"], v["total_length"], c,
            "{:,}".format(v["states_at"][c]) if c else "-", v["seconds"]))

    print("\n## Solved ladder rows (%d), by difficulty bin\n" % len(s))
    print("| bin | rows | min cap: distribution | unsolved at top cap | budget |")
    print("|---:|---:|---|---:|---:|")
    by_bin = collections.defaultdict(list)
    for n, v in s.items():
        by_bin[int(v["bin"]) if v["bin"] is not None else -1].append(v)
    for b in sorted(by_bin):
        vs = by_bin[b]
        caps = collections.Counter(v["min_cap"] for v in vs if v["min_cap"] is not None)
        uns = sum(1 for v in vs if v["min_cap"] is None and v["budget_at"] is None)
        bud = sum(1 for v in vs if v["budget_at"] is not None)
        print("| %d | %d | %s | %d | %d |" % (
            b, len(vs), ", ".join("%d:%d" % kv for kv in sorted(caps.items())), uns, bud))
    print("\n| row | bin | r1, r2 | min cap | path | closed below | CPU s |")
    print("|---|---:|---|---:|---:|---:|---:|")
    for n, v in sorted(s.items(), key=lambda kv: (int(kv[1]["bin"]), kv[0])):
        print("| %s | %s | `%s`, `%s` | %s | %s | %s | %.1f |" % (
            n, v["bin"], v["r1"], v["r2"],
            v["min_cap"] if v["min_cap"] is not None else ("budget@%d" % v["budget_at"] if v["budget_at"] else "> %s" % v["closed_through"]),
            v["path_length"] if v["path_length"] is not None else "-",
            v["closed_through"] if v["closed_through"] is not None else "-",
            v["seconds"]))
    with open(args.out, "w") as fh:
        json.dump({"u124": u, "solved": s}, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
