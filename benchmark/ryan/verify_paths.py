"""Independent replay of the solved paths in run_all.py output (does not use Ryan's move code).

Per step:
  substitution: one relator unchanged (as a cyclic word up to inversion) and the other equal to the cyclic
                reduction of rot(a) * rot(b^{+-1}) for the parent relators a, b in some order and rotations;
  CoV:          the child is in the parent's Aut(F2) orbit (acx.aut.orbit_key), so it is an AC step via Aut.
Per row: the path starts at the row's canonical start, ends trivial, |det| = 1 throughout, and the logged
path_length / path_cov_moves / max_relator_len agree with the path.

  NUMBA_CACHE_DIR=/tmp/nc python -B benchmark/ryan/verify_paths.py results/ryan_1e5 [--out results/ryan_1e5/VERIFY.json]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from acx.aut import orbit_key  # noqa: E402
from acx.core.words import Presentation, canonical_rels, parse  # noqa: E402

LET = {1: "x", -1: "X", 2: "y", -2: "Y"}


def inv(w):
    return tuple(-c for c in reversed(w))


def cred(w):
    s = []
    for c in w:
        if s and s[-1] == -c:
            s.pop()
        else:
            s.append(c)
    while len(s) > 1 and s[0] == -s[-1]:
        s = s[1:-1]
    return tuple(s)


def cyc_class(w):
    """canonical cyclic word up to rotation and inversion"""
    w = cred(w)
    if not w:
        return ()
    cands = [w[i:] + w[:i] for i in range(len(w))] + [inv(w)[i:] + inv(w)[:i] for i in range(len(w))]
    return min(cands)


def is_substitution(parent, child):
    a, b = parent
    ca, cb = cyc_class(a), cyc_class(b)
    c0, c1 = cyc_class(child[0]), cyc_class(child[1])
    targets = []
    if c0 in (ca, cb):
        targets.append(c1)
    if c1 in (ca, cb):
        targets.append(c0)
    if not targets:
        return False
    for x, y in ((a, b), (b, a)):
        for s in (y, inv(y)):
            for i in range(len(x)):
                rx = x[i:] + x[:i]
                for j in range(len(s)):
                    ry = s[j:] + s[:j]
                    if rx[-1] != -ry[0]:
                        continue
                    if cyc_class(rx + ry) in targets:
                        return True
    return False


def det(pair):
    m = [[sum((1 if c > 0 else -1) for c in w if abs(c) == g) for g in (1, 2)] for w in pair]
    return abs(m[0][0] * m[1][1] - m[0][1] * m[1][0])


def okey(pair):
    rels = canonical_rels(tuple(parse("".join(LET[c] for c in w)) for w in pair))
    return orbit_key(Presentation(2, rels), "fast")


def check_record(r):
    fails = []
    path = [tuple(tuple(w) for w in p["relators"]) for p in r["path"]]
    acts = r["actions"]
    start = tuple(tuple(w) for w in r["start"]["relators"])
    if path[0] != start:
        fails.append("start")
    last = path[-1]
    if not (len(last[0]) == 1 and len(last[1]) == 1 and {abs(last[0][0]), abs(last[1][0])} == {1, 2}):
        fails.append("end")
    if len(acts) != len(path) - 1 or r["path_length"] != len(acts):
        fails.append("length")
    if r["path_cov_moves"] != sum(1 for x in acts if x[0] >= 2):
        fails.append("cov_count")
    if r["max_relator_len"] != max(max(len(w) for w in p) for p in path):
        fails.append("max_rel")
    n_sub = n_cov = 0
    for k, x in enumerate(acts):
        p, c = path[k], path[k + 1]
        if det(c) != 1:
            fails.append(f"det@{k}")
        if x[0] < 2:
            n_sub += 1
            if not is_substitution(p, c):
                fails.append(f"sub@{k}")
        else:
            n_cov += 1
            if okey(p) != okey(c):
                fails.append(f"cov_orbit@{k}")
    return fails, n_sub, n_cov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out")
    a = ap.parse_args()
    report = {}
    for f in sorted(Path(a.folder).glob("*__*.jsonl")):
        recs = [json.loads(l) for l in f.read_text().splitlines()]
        sol = [r for r in recs if r["solved"]]
        fails = {}
        ns = nc = 0
        for r in sol:
            fl, s_, c_ = check_record(r)
            ns += s_
            nc += c_
            if fl:
                fails[r["id"]] = fl[:5]
        report[f.stem] = {"rows": len(recs), "solved": len(sol), "sub_steps": ns, "cov_steps": nc,
                          "failures": fails}
        print(f.stem, report[f.stem]["solved"], "solved;", ns, "sub,", nc, "cov steps; failures", len(fails), flush=True)
    report["all_pass"] = all(not v["failures"] for k, v in report.items() if isinstance(v, dict))
    print("ALL PASS" if report["all_pass"] else "FAILURES")
    if a.out:
        Path(a.out).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
