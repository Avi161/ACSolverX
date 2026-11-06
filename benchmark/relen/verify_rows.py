"""Replay the stored paths of results/benchmark_rows/paths and check each record's path_length and max_rel.

smoves: replayed from the cyclically reduced start at the stored cap; hybrid: the elementary AC moves replayed on the
original presentation, and the certificate's search states recomputed; states: the path ends trivial and its longest
relator matches. cov_gate and elliot paths are verified by their own runs (VERIFY.json on branch paper); here only
their longest relator is recomputed from the stored states.

    python benchmark/relen/verify_rows.py [results/benchmark_rows]
"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from acx.core.moves import Move  # noqa: E402
from acx.core.words import parse, reduce  # noqa: E402
from acx.data import parse_presentation  # noqa: E402
from acx.verify.pack import unpack  # noqa: E402
from acx.verify.replay import replay  # noqa: E402
from hybrid_relen import search_states_max  # noqa: E402


def cyc(w):
    return len(reduce(tuple(w)))


def check(pres, rec, p):
    f = p["format"]
    if f == "smoves":
        states = replay(pres, [Move(*m) for m in p["path"]], cyclic=True, cap=p["cap"])
        return len(p["path"]), max(max(map(len, s.rels)) for s in states)
    if f == "states":
        last = p["path"][-1]
        assert sorted(len(w) for w in last) == [1, 1], "does not end trivial"
        return len(p["path"]) - 1, max(max(len(w) for w in s) for s in p["path"])
    if f == "hybrid":
        states = replay(pres, unpack(p["elementary"]), cyclic=False, normalize=False)
        assert rec["max_rel_search"] == search_states_max(pres, p["certificate"])
        return len(p["certificate"]), max(cyc(w) for s in states for w in s.rels)
    if f == "elliot":
        return None, max(max(len(w) for w in s) for s in p["path"])
    if f == "cov_gate":
        return None, max(max(len(w) for w in s["state"]["relators_text"]) for s in p["path"])
    raise ValueError(f)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "results/benchmark_rows")
    bad = n = 0
    for bench in ("ms640", "ladder100"):
        rows = {r["id"]: r for r in map(json.loads, (root / f"{bench}.jsonl").read_text().splitlines())}
        for line in gzip.open(root / "paths" / f"{bench}.jsonl.gz", "rt"):
            r = json.loads(line)
            row = rows[r["id"]]
            pres = parse_presentation(", ".join(row["pres"]))
            for m, p in r["paths"].items():
                rec = row["methods"][m]
                n += 1
                try:
                    plen, mx = check(pres, rec, p)
                    ok = mx == rec["max_rel"] and (plen is None or plen == rec["path_length"])
                except Exception as e:  # a replay failure
                    ok, plen, mx = False, None, repr(e)[:100]
                if not ok:
                    bad += 1
                    print("MISMATCH", bench, r["id"], m, plen, mx, rec)
    print(f"{n} paths checked, {bad} mismatches")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
