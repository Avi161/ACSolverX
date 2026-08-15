"""Export a covmeet store as a dataset — the far-hump counterpart of AC-1M.

    PYTHONPATH=. python3 -m experiments.stable_ac.cov.meet.export_covmeet OUT_DIR \
        [--seed-set all124] [--dest DIR] [--max-length N] [--min-depth 0] \
        [--max-rows N] [--stem covmeet_hard]

AC-1M is ~1.1M canonical presentations populating the solvable hump and the valley.
A covmeet store is the other side: every row is a distinct Aut(F2)-orbit (exact,
canonical, deduped by construction), each a balanced presentation of the trivial
group (every CoV step is a Tietze transformation; the verifier enforces the
abelianization-det invariant), and each STABLY AC-equivalent to one of the unsolved
classes — hardness by pedigree, not by guess.

Outputs (dataset conventions of ``data/``):

* ``<stem>.txt`` — one presentation per line, the repo's flat-int layout: two
  relators of ``max_length`` ints each (x=1, X=-1, y=2, Y=-2, 0 = padding). Rows
  whose longer relator exceeds ``--max-length`` are SKIPPED AND COUNTED (a layout
  bound is a file-format necessity, not a length prior — pick a bigger N to keep
  more; the skip count is printed and stored in the manifest).
* ``<stem>_labels.csv`` — parallel rows: r1, r2 (letter strings), mu, depth (CoV
  steps from its seed, walked from the snapshot's parent pointers), classes (which
  seed classes reached it, ``|``-joined), n_classes.
* ``<stem>_manifest.json`` — provenance: engine/family, store counts, max_length,
  skipped, generation parameters. No dates in filenames (resume-key lesson).

Export is verification-gated like the report: a store the verifier rejects is not
a dataset. Deterministic given the store (discovery order).
"""

import argparse
import csv
import json
import os
import sys

from experiments.stable_ac.cov.meet import covmeet, verify_covmeet

_INT = {"x": 1, "X": -1, "y": 2, "Y": -2}


def _flat(rep, max_length):
    out = []
    for w in rep:
        out += [_INT[c] for c in w] + [0] * (max_length - len(w))
    return out


def _depths(store):
    """CoV steps from seed per orbit, via the snapshot's parent pointers."""
    depth = {}
    for rep in store.reps:
        chain, cur = [], rep
        while cur not in depth:
            hit = store.parent.get(cur)
            if hit is None:
                depth[cur] = 0 if store.index.get(cur, 0) < len(store.seed_mu) \
                    else -1                      # unknown lineage (defensive)
                break
            chain.append(cur)
            cur = hit[0]
        base = depth[cur]
        for i, c in enumerate(reversed(chain)):
            depth[c] = base + i + 1 if base >= 0 else -1
    return depth


def main(argv=None, seeds_override=None):
    """``seeds_override`` is the same TEST seam ``covmeet.run`` has."""
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed-set", default="all124")
    ap.add_argument("--dest", default=None)
    ap.add_argument("--stem", default="covmeet_hard")
    ap.add_argument("--max-length", type=int, default=None,
                    help="ints per relator slot; default = longest relator in store")
    ap.add_argument("--min-depth", type=int, default=0)
    ap.add_argument("--max-rows", type=int, default=None)
    ap.add_argument("--sample", type=int, default=500)
    args = ap.parse_args(argv)

    dest = args.dest or os.path.join(covmeet.repo_root(),
                                     "results", "stable_ac", "covmeet")
    rc = verify_covmeet.main([args.out_dir, "--seed-set", args.seed_set,
                              "--sample", str(args.sample)],
                             seeds_override=seeds_override)
    if rc != 0:
        print("REFUSING to export: verification failed")
        return rc

    seeds = seeds_override if seeds_override is not None \
        else covmeet.load_seeds(args.seed_set)
    store, header = covmeet.load(args.out_dir, args.seed_set, len(seeds),
                                 expect_family=covmeet.FAMILY)
    names = [s[0] for s in seeds]
    depth = _depths(store)
    max_len = args.max_length or max(
        max(len(r[0]), len(r[1])) for r in store.reps)

    os.makedirs(dest, exist_ok=True)
    n_written = n_skipped = 0
    txt_path = os.path.join(dest, args.stem + ".txt")
    csv_path = os.path.join(dest, args.stem + "_labels.csv")
    with open(txt_path, "w") as ft, open(csv_path, "w", newline="") as fc:
        w = csv.writer(fc)
        w.writerow(["r1", "r2", "mu", "depth", "classes", "n_classes"])
        for rep in store.reps:
            if max(len(rep[0]), len(rep[1])) > max_len:
                n_skipped += 1
                continue
            d = depth[rep]
            if d < args.min_depth:
                continue
            if args.max_rows is not None and n_written >= args.max_rows:
                break
            mask = store.mask[rep]
            cls = [names[i] for i in range(mask.bit_length()) if mask >> i & 1]
            ft.write(str(_flat(rep, max_len)) + "\n")
            w.writerow([rep[0], rep[1], store.mu[rep], d,
                        "|".join(cls), len(cls)])
            n_written += 1
    manifest = {
        "engine": covmeet.ENGINE_TAG, "family": covmeet.FAMILY,
        "seed_set": args.seed_set, "n_seeds": len(seeds),
        "store_orbits": len(store.reps), "rows": n_written,
        "skipped_over_max_length": n_skipped, "max_length": max_len,
        "min_depth": args.min_depth, "max_rows": args.max_rows,
        "layout": "flat ints, 2 relators x max_length, x=1 X=-1 y=2 Y=-2, 0 pad",
        "provenance": "every row is a distinct Aut(F2)-orbit, a balanced "
                      "presentation of the trivial group, stably AC-equivalent "
                      "to its listed unsolved classes",
    }
    with open(os.path.join(dest, args.stem + "_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"exported {n_written:,} rows (max_length {max_len}, "
          f"{n_skipped} skipped over-length) -> {txt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
