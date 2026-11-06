"""Largest total relator length on every stored solution path (results/benchmark_rows/paths), the sum of the
cyclically reduced relator lengths of a state, maximized over the states of the path with the start included. The
states are those of benchmark/relen/verify_rows.py: the S-move path; for the hybrid both its search states
(``search``) and its AC path (``ac``); for the searches with CoV moves the two-generator states on the path.

    python benchmark/relen/total_len.py [results/benchmark_rows]   # writes max_total.jsonl there and prints the table
"""
import gzip
import json
import sys
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from acx.core.moves import Move  # noqa: E402
from acx.core.words import canonical_rels, parse, reduce  # noqa: E402
from acx.data import parse_presentation  # noqa: E402
from acx.hybrid.steps import aut_child, move_child  # noqa: E402
from acx.verify.pack import unpack  # noqa: E402
from acx.verify.replay import replay  # noqa: E402


def tot(rels):
    return sum(len(reduce(tuple(w))) for w in rels)


def search_states_total(pres, steps):
    cur = canonical_rels(tuple(reduce(r) for r in pres.rels))
    best = tot(cur)
    for st in steps:
        if isinstance(st, dict) and "aut" in st:
            cur = aut_child(cur, st["aut"])
        elif isinstance(st, dict):                       # a higher-rank step: its stored words
            after = [tuple(w) for w in st["after"]]
            best = max(best, tot(after))
            if len(after) == 2:
                cur = canonical_rels(tuple(after))
            continue
        else:
            cur = move_child(cur, Move(*st))
        best = max(best, tot(cur))
    return best


def max_total(pres, p):
    f = p["format"]
    if f == "smoves":
        return max(tot(s.rels) for s in replay(pres, [Move(*m) for m in p["path"]], cyclic=True, cap=p["cap"]))
    if f == "states" or f == "elliot":
        return max(tot([parse(w) for w in s]) for s in p["path"])
    if f == "cov_gate":
        return max(tot([parse(w) for w in s["state"]["relators_text"]]) for s in p["path"])
    raise ValueError(f)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "results/benchmark_rows")
    out = []
    for bench in ("ms640", "ladder100"):
        rows = {r["id"]: r for r in map(json.loads, (root / f"{bench}.jsonl").read_text().splitlines())}
        for line in gzip.open(root / "paths" / f"{bench}.jsonl.gz", "rt"):
            r = json.loads(line)
            row = rows[r["id"]]
            pres = parse_presentation(", ".join(row["pres"]))
            rec = dict(benchmark=bench, id=r["id"], bench60=row.get("bench60", False), start_total=tot(pres.rels))
            for m, p in r["paths"].items():
                if p["format"] == "hybrid":
                    states = replay(pres, unpack(p["elementary"]), cyclic=False, normalize=False)
                    rec["hybrid, search states"] = search_states_total(pres, p["certificate"])
                    rec["hybrid, AC path"] = max(tot(s.rels) for s in states)
                else:
                    rec[m] = max_total(pres, p)
            out.append(rec)
    with open(root / "max_total.jsonl", "w") as f:
        for rec in out:
            f.write(json.dumps(rec) + "\n")
    cols = ["start_total", "LENGTH", "S20_MK2", "hybrid, search states", "hybrid, AC path", "CoV gate",
            "dual, single CoV", "dual, auto CoV", "triple"]
    sets = {"MS640": [x for x in out if x["benchmark"] == "ms640"], "bench60": [x for x in out if x["bench60"]],
            "ladder100": [x for x in out if x["benchmark"] == "ladder100"]}
    for name, xs in sets.items():
        for c in cols:
            v = [x[c] for x in xs if c in x]
            print(f"{name}\t{c}\t{len(v)}\t{mean(v):.1f}\t{median(v):g}\t{min(v)}\t{max(v)}")


if __name__ == "__main__":
    main()
