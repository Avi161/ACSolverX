"""Independent proof checker for probe/overnight result files (`run_probe` / `run_overnight`).

`verify_certificates.py` checks the production sweep's output, whose sources are the 261 raw
reps named in `ms_reps_unsolved.csv`. The probe runners seed the **class reps** instead
(`C<id>` from the 126-manifest, plus TRIVIAL), so their files need this checker: same standard
of proof, different source universe.

What is checked, per file -- sharing the search's *inference* nowhere:

1. **Roots.** Every source's presentation is rebuilt from the ORIGINAL manifest (never from
   the file's own `roots` block), canonicalised through the repo's numba solver, and must
   match `raw`. The recorded `phi` must be a genuine automorphism of F2 -- decided by Nielsen
   reduction, fully independent of the Whitehead code that produced phi -- and must carry
   `raw` exactly onto `aut_rep`.
2. **Merges.** Both paths replay step by step: apply the Definition 2.1 move by string
   substitution, apply phi (Nielsen-checked), canonicalise, land exactly on the certified
   rep. Both paths must end on the same Aut-class, the one the merge names.
3. **The abelianisation invariant the search never computes.** |det| of the exponent-sum
   matrix is ACA-invariant, so it must be constant across every merged pair.
4. **The count.** The partition is rebuilt from scratch out of ONLY the merges that just
   verified, and must reproduce `n_classes` and `new_merges` exactly -- the number is the
   transitive closure of verified equivalences, not something the search printed.

Usage:
    verify_probe_merges.py <probe.json> [<probe.json> ...]

Exit code is non-zero if any claim in any file fails.
"""
import json
import os
import sys


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.words import abelian_det, apply_hom  # noqa: E402
from experiments.equivalence_classes.verify.verify_certificates import (  # noqa: E402
    canon, check_phi, legal_move, replay,
)

MANIFEST = os.path.join(ROOT, "results", "equivalence_classes",
                        "classes_126_from_greedy_1000000_261_mrl48.jsonl")


def manifest_sources():
    """name -> raw presentation, rebuilt from the manifest -- the non-circular ground truth."""
    reps = {}
    for line in open(MANIFEST):
        c = json.loads(line)
        reps[f"C{c['class_id']}"] = (c["r1"], c["r2"])
    reps["TRIVIAL"] = ("x", "y")
    return reps


def replay_path(start, path, where, errs):
    cur = start
    for i, step in enumerate(path):
        move, phi, rep = tuple(step[0]), step[1], tuple(step[2])
        if not legal_move(cur, move, f"{where}[{i}]", errs):
            return None
        child = replay(cur, move)
        if not check_phi(phi, f"{where}[{i}]", errs):
            return None
        got = canon(apply_hom(child[0], phi), apply_hom(child[1], phi))
        if got != rep:
            errs.append(f"{where}[{i}]: replay landed on {got}, certificate claims {rep}")
            return None
        cur = rep
    return cur


def verify_file(path, reps):
    data = json.load(open(path))
    errs = []
    roots = data["roots"]

    for name, r in roots.items():
        if name not in reps:
            errs.append(f"root {name}: not in the 126-manifest")
            continue
        raw = canon(*reps[name])
        if tuple(r["raw"]) != raw:
            errs.append(f"root {name}: canonical form {raw} != recorded {tuple(r['raw'])}")
            continue
        if not check_phi(r["phi"], f"root {name}", errs):
            continue
        got = canon(apply_hom(raw[0], r["phi"]), apply_hom(raw[1], r["phi"]))
        if got != tuple(r["aut_rep"]):
            errs.append(f"root {name}: phi lands on {got}, claims {tuple(r['aut_rep'])}")

    verified_pairs = []
    for m in data["merges"]:
        a, b, at = m["a"], m["b"], tuple(m["at"])
        w = f"{m['kind']} {a}={b}"
        if m["kind"] == "aut":
            if tuple(roots[a]["aut_rep"]) != tuple(roots[b]["aut_rep"]):
                errs.append(f"{w}: roots are NOT Aut-equivalent")
            else:
                verified_pairs.append((a, b))
            continue
        ea = replay_path(tuple(roots[a]["aut_rep"]), m["path_a"], f"{w}.a", errs)
        eb = replay_path(tuple(roots[b]["aut_rep"]), m["path_b"], f"{w}.b", errs)
        if ea is None or eb is None:
            continue
        if ea != eb:
            errs.append(f"{w}: paths end at different Aut-classes: {ea} vs {eb}")
        elif ea != at:
            errs.append(f"{w}: paths end at {ea}, certificate claims {at}")
        else:
            da = abs(abelian_det(*reps[a]))
            db = abs(abelian_det(*reps[b]))
            if da != db:
                errs.append(f"{w}: |det| not invariant across the merge: {da} vs {db}")
            else:
                verified_pairs.append((a, b))

    # the count itself: closure of ONLY the verified merges over the manifest reps
    rep_names = [n for n in roots if n != "TRIVIAL"]
    parent = {n: n for n in roots}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in verified_pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    rebuilt = {}
    for n in rep_names:
        rebuilt.setdefault(find(n), []).append(n)
    n_classes = len(rebuilt)
    multi = {frozenset(v) for v in rebuilt.values() if len(v) > 1}
    claimed = {frozenset(c) for c in data["new_merges"]}
    if n_classes != data["n_classes"]:
        errs.append(f"COUNT: {n_classes} classes rebuilt from verified merges, "
                    f"file claims {data['n_classes']}")
    if multi != claimed:
        errs.append(f"MERGE SETS: rebuilt {sorted(map(sorted, multi))} != "
                    f"claimed {sorted(map(sorted, claimed))}")
    solved_root = find("TRIVIAL")
    really_solved = sorted(n for n in rep_names if find(n) == solved_root)
    if really_solved != sorted(data["solved"]):
        errs.append(f"SOLVED claim {data['solved']} does not match the verified closure "
                    f"{really_solved}")

    tag = data.get("tag", os.path.basename(path))
    print(f"[{tag}] roots={len(roots)} merges verified={len(verified_pairs)}/"
          f"{len(data['merges'])} -> {n_classes} classes over the {len(rep_names)} reps"
          + (f"  FAILED({len(errs)})" if errs else "  OK"))
    for e in errs[:10]:
        print("   -", e)
    return errs


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    reps = manifest_sources()
    bad = 0
    for path in sys.argv[1:]:
        bad += len(verify_file(path, reps))
    if bad:
        print(f"\nFAILED: {bad} problems")
        sys.exit(1)
    print("\nALL PROBE CERTIFICATES VERIFY")


if __name__ == "__main__":
    main()
