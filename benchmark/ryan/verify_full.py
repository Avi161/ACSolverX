"""Independent replay of the solves in run_full.py output (does not use the search's move or image code).

Per step:
  sub:  checked as in verify_paths.py (one relator kept, the other a reduced product of rotations);
  cov:  Ryan's CoV move; the child is in the parent's Aut(F2) orbit (verify_paths.py);
  img:  the logged certificate (define z = w, substitute, eliminate) is replayed on the parent by
        acx.cov.apply_steps, which checks the hypotheses of Lemma 11 and |det| = 1, and its result must be the child
        up to relator order, rotation and inversion. The step's ``automorphic`` tag is recomputed with the Whitehead
        backend (acx.aut.are_automorphic), not the fast one the search used.
Per row: the path starts at the row's start and ends trivial, the counts and ``kind`` agree with the path.

  python benchmark/ryan/verify_full.py results/ryan_cov_full_1e6 [--out results/ryan_cov_full_1e6/VERIFY.json]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
from acx.aut import are_automorphic  # noqa: E402
from acx.core.words import Presentation, canonical_rels  # noqa: E402
from acx.cov import apply_steps  # noqa: E402
from verify_paths import cyc_class, det, is_substitution, okey  # noqa: E402


def same_state(a, b):
    """Two relator pairs are equal up to order, rotation and inversion of each relator."""
    return sorted(map(cyc_class, a)) == sorted(map(cyc_class, b))


def check_record(r):
    fails = []
    path = r["path"]
    states = [tuple(tuple(w) for w in s["state"]["relators"]) for s in path]
    if states[0] != tuple(tuple(w) for w in r["start"]["relators"]):
        fails.append("start")
    last = states[-1]
    if not (len(last[0]) == 1 and len(last[1]) == 1 and {abs(last[0][0]), abs(last[1][0])} == {1, 2}):
        fails.append("end")
    kinds = [s["kind"] for s in path[1:]]
    if r["path_length"] != len(kinds) or r["path_sub_moves"] != kinds.count("sub") \
            or r["path_cov_moves"] != kinds.count("cov") or r["path_img_moves"] != kinds.count("img"):
        fails.append("counts")
    if r["max_relator_len"] != max(max(len(w) for w in s) for s in states):
        fails.append("max_rel")
    non_aut = 0
    for k, step in enumerate(path[1:]):
        p, c = states[k], states[k + 1]
        if det(c) != 1:
            fails.append(f"det@{k}")
        if step["kind"] == "sub":
            if not is_substitution(p, c):
                fails.append(f"sub@{k}")
        elif step["kind"] == "cov":
            if okey(p) != okey(c):
                fails.append(f"cov_orbit@{k}")
        else:
            try:
                image = apply_steps(Presentation(2, p), step["cov"]["steps"])
            except Exception as e:  # noqa: BLE001  (any failed hypothesis is a failed step)
                fails.append(f"img_replay@{k}:{e}")
                continue
            if not same_state(image.rels, c):
                fails.append(f"img_state@{k}")
            aut = are_automorphic(Presentation(2, canonical_rels(p)), Presentation(2, canonical_rels(c)))
            if aut != step["cov"]["automorphic"]:
                fails.append(f"img_aut_tag@{k}")
            non_aut += not aut
    if r["kind"] != ("stable_cert" if non_aut else "ac_path") or r["path_img_non_aut"] != non_aut:
        fails.append("kind")
    return fails, kinds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out")
    a = ap.parse_args()
    report = {}
    for f in sorted(Path(a.folder).glob("*__*.jsonl")):
        recs = [json.loads(l) for l in f.read_text().splitlines()]
        sol = [r for r in recs if r["solved"]]
        fails, steps = {}, {"sub": 0, "cov": 0, "img": 0}
        for r in sol:
            fl, kinds = check_record(r)
            for k in steps:
                steps[k] += kinds.count(k)
            if fl:
                fails[r["id"]] = fl[:5]
        report[f.stem] = {"rows": len(recs), "solved": len(sol),
                          "ac_path": sum(r["kind"] == "ac_path" for r in sol),
                          "stable_cert": sum(r["kind"] == "stable_cert" for r in sol),
                          "steps": steps, "failures": fails}
        print(f.stem, json.dumps({k: v for k, v in report[f.stem].items() if k != "failures"}),
              "failures", len(fails), flush=True)
    report["all_pass"] = all(not v["failures"] for v in report.values() if isinstance(v, dict))
    print("ALL PASS" if report["all_pass"] else "FAILURES")
    if a.out:
        Path(a.out).write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
