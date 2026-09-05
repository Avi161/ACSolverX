"""Splice the two overnight edges into the cap-28 sweep artifact -> a 137-edge sweep JSON.

The proof book (`make_proof_book.py`) is generated from a sweep JSON: `roots` keyed by
presentation name + `merges` carrying (move, phi, rep) path certificates. The overnight ladder
(`run_overnight.py`, see EQUIVALENCE_FINDING.md 3b-3c) found its two merges over the
126-manifest class reps, named `C<id>` -- but each of the four presentations involved is a
SINGLETON class, and its class rep's Whitehead form coincides with the sweep root's `aut_rep`
(asserted below). So the probe paths splice directly onto the sweep's roots: same start state,
same step schema, no translation beyond the name.

Writes `sweep_seam_28_250_plus_overnight.json`. The original `sweep_seam_28_250.json` is left
byte-identical -- it is the historical cap-28 record, and `test_equivalence.py` pins its
126/135 numbers as exactly that.

Usage:  augment_sweep_overnight.py
Then:   make_proof_book.py results/equivalence_classes/sweep/sweep_seam_28_250_plus_overnight.json
Check:  verify_certificates.py on the new sweep, verify_proofs.py on the regenerated book.
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
OUT = os.path.join(ROOT, "results", "equivalence_classes")

SWEEP = os.path.join(OUT, "sweep", "sweep_seam_28_250.json")
PROBE = os.path.join(OUT, "probe", "probe_overnight_seam30.json")
MANIFEST = os.path.join(OUT, "sweep", "classes_126_from_greedy_1000000_261_mrl48.jsonl")


def main():
    sweep = json.load(open(SWEEP))
    probe = json.load(open(PROBE))
    members_of = {f"C{c['class_id']}": c["members"]
                  for c in map(json.loads, open(MANIFEST))}

    added = []
    for m in probe["merges"]:
        names = []
        for cid in (m["a"], m["b"]):
            mem = members_of[cid]
            assert len(mem) == 1, f"{cid} is not a singleton class: {mem}"
            names.append(mem[0])
        a, b = names
        # the splice condition: the probe path starts exactly where the sweep root ends up
        pa = tuple(probe["roots"][m["a"]]["aut_rep"])
        pb = tuple(probe["roots"][m["b"]]["aut_rep"])
        assert pa == tuple(sweep["roots"][a]["aut_rep"]), f"{a}: aut_rep mismatch"
        assert pb == tuple(sweep["roots"][b]["aut_rep"]), f"{b}: aut_rep mismatch"
        added.append({"kind": m["kind"], "a": a, "b": b, "at": m["at"],
                      "path_a": m["path_a"], "path_b": m["path_b"]})
        print(f"edge {135 + len(added)}: {a} == {b}  ({m['kind']}, "
              f"{len(m['path_a'])}+{len(m['path_b'])} steps)")

    sweep["merges"] += added

    # rebuild the class lists so the artifact stays internally consistent
    parent = {n: n for n in sweep["roots"]}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for m in sweep["merges"]:
        ra, rb = find(m["a"]), find(m["b"])
        assert ra != rb, f"merge {m['a']}={m['b']} closes a cycle"
        parent[rb] = ra
    comps = {}
    for n in sweep["roots"]:
        comps.setdefault(find(n), []).append(n)
    sweep["classes"] = sorted((sorted(v) for v in comps.values()), key=lambda c: c[0])
    sweep["n_classes_excl_trivial"] = sum(1 for c in comps.values()
                                          if c != ["TRIVIAL"] and "TRIVIAL" not in c) \
        + sum(1 for c in comps.values() if "TRIVIAL" in c and len(c) > 1)
    sweep["solved"] = sorted(n for c in comps.values() if "TRIVIAL" in c
                             for n in c if n != "TRIVIAL")
    sweep["config"] = {**sweep["config"],
                       "augmented_with": os.path.relpath(PROBE, ROOT)}

    path = os.path.join(OUT, "sweep", "sweep_seam_28_250_plus_overnight.json")
    json.dump(sweep, open(path, "w"), indent=1)
    print(f"{len(sweep['merges'])} merges, {sweep['n_classes_excl_trivial']} classes, "
          f"solved={sweep['solved']}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
