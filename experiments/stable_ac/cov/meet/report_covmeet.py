"""Turn a covmeet OUT_DIR into the committed results artifacts.

    PYTHONPATH=. python3 -m experiments.stable_ac.cov.meet.report_covmeet OUT_DIR \
        [--seed-set all124] [--results-dir results/stable_ac/covmeet]

Reads the snapshot + certs (never the live run), refuses to write unless the
independent verifier passes, and emits into the results dir:

* ``COVMEET.md`` — classes remaining, merges and drops with their chains, the census
  headline, and provenance (sessions, engine/family, verification line);
* ``covmeet_classes.csv`` — one row per class: name, seed_mu, best_mu, improved,
  expanded, ncov (raw CoVs), norb (non-automorphic CoV census), orbits_reached;
* ``covmeet_census.csv`` — one row per EXPANDED orbit: mu, ncov, norb — the
  "how many non-automorphic CoVs does this presentation have" dataset.

The same run identity always writes the same filenames — a later, fuller ingestion of
the same run overwrites with more data (the "as of" line inside the files moves).
Results live here, never beside the code (repo rule). Certs chains are copied in
verbatim so the results dir is self-contained for the paper.
"""

import argparse
import csv
import json
import os
import sys

from experiments.stable_ac.cov.meet import covmeet, verify_covmeet


def _classes_rows(store, seeds):
    reached = {i: 0 for i in range(len(seeds))}
    for mask in store.mask.values():
        m = mask
        while m:
            b = m & -m
            reached[b.bit_length() - 1] += 1
            m ^= b
    rows = []
    for i, (name, r1, r2) in enumerate(seeds):
        rep = store.reps[i]
        nc, no = store.census.get(rep, (None, None))
        rows.append({
            "name": name, "seed_mu": store.seed_mu[i],
            "best_mu": store.best_mu[i],
            "improved": store.best_mu[i] < store.seed_mu[i],
            "expanded": rep in store.expanded,
            "ncov": nc, "norb": no,
            "orbits_reached": reached[i],
            "class_root": seeds[store.uf.find(i)][0],
        })
    return rows


def main(argv=None, seeds_override=None):
    """``seeds_override`` is the same TEST seam ``covmeet.run`` has."""
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed-set", default="all124")
    ap.add_argument("--results-dir", default=None)
    ap.add_argument("--sample", type=int, default=1000)
    args = ap.parse_args(argv)

    results_dir = args.results_dir or os.path.join(
        covmeet.repo_root(), "results", "stable_ac", "covmeet")

    # The gate: nothing lands in results/ that the independent verifier rejects.
    rc = verify_covmeet.main([args.out_dir, "--seed-set", args.seed_set,
                              "--sample", str(args.sample)],
                             seeds_override=seeds_override)
    if rc != 0:
        print("REFUSING to write results: verification failed")
        return rc

    seeds = seeds_override if seeds_override is not None \
        else covmeet.load_seeds(args.seed_set)
    store, header = covmeet.load(args.out_dir, args.seed_set, len(seeds),
                                 expect_family=covmeet.FAMILY)
    summary = covmeet.summarise(store, seeds)
    certs_path, _ = covmeet.run_paths(args.out_dir, args.seed_set)
    sessions, merges, drops = [], {}, {}
    with open(certs_path) as f:
        for line in f:
            ev = json.loads(line)
            if ev["t"] == "meta":
                sessions.append(ev["session_utc"])
            elif ev["t"] == "merge":
                merges[frozenset(ev["classes"])] = ev
            elif ev["t"] == "drop":
                drops[(ev["name"], ev["mu"])] = ev

    os.makedirs(results_dir, exist_ok=True)
    rows = _classes_rows(store, seeds)
    with open(os.path.join(results_dir, "covmeet_classes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(results_dir, "covmeet_census.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mu", "ncov", "norb"])
        for rep in store.reps:
            if rep in store.expanded:
                nc, no = store.census[rep]
                w.writerow([store.mu[rep], nc, no])

    ex = [store.census[r] for r in store.reps if r in store.expanded]
    ncs = sorted(v[0] for v in ex)
    nos = sorted(v[1] for v in ex)
    med = lambda v: v[len(v) // 2] if v else 0
    improved = [r for r in rows if r["improved"]]
    lines = [
        "# covmeet — CoV-only collision search over the unsolved classes",
        "",
        f"Engine `{covmeet.ENGINE_TAG}`, family `{covmeet.FAMILY}`, seed set "
        f"`{args.seed_set}` ({len(seeds)} classes). CoV moves only — no AC or "
        f"substitution search, zero search nodes. A merge certifies the two classes "
        f"**stably** AC-equivalent (never unqualified AC-equivalence); every chain "
        f"below replays segment-by-segment through `verify_covmeet` (exit 0 gated "
        f"this page).",
        "",
        f"**As of:** {summary['expanded']:,} orbits expanded, "
        f"{summary['discovered']:,} discovered, frontier {summary['frontier']:,} "
        f"(shortest open bucket L={summary['shortest_open_bucket']}), "
        f"{len(sessions)} session(s), last {sessions[-1] if sessions else '?'}Z.",
        "",
        f"## Classes remaining: **{summary['classes_remaining']} / {len(seeds)}**",
        "",
        f"Merges found: **{summary['merges_found']}**. Classes reaching below their "
        f"seeded Aut-min: **{len(improved)}**.",
        "",
    ]
    if merges:
        lines += ["### Merges (stable AC-equivalences)", ""]
        for key, ev in sorted(merges.items(), key=lambda kv: sorted(kv[0])):
            a, b = ev["classes"]
            lines.append(f"- **{a} ≡ {b}** at `{ev['rep']}` — chains of "
                         f"{len(ev['chains'][0]) - 1} and {len(ev['chains'][1]) - 1} "
                         f"CoV steps (full chains in the certs file)")
        lines.append("")
    if improved:
        lines += ["### New best representatives (below the seeded Aut-min)", ""]
        for r in improved:
            lines.append(f"- **{r['name']}**: mu {r['seed_mu']} → {r['best_mu']}")
        lines.append("")
    lines += [
        "## The census",
        "",
        f"Over {len(ex):,} expanded orbits: raw subword CoVs per state median "
        f"{med(ncs)} (min {ncs[0] if ncs else 0}, max {ncs[-1] if ncs else 0}); "
        f"**non-automorphic** CoVs per state (distinct Aut-orbits, the honest "
        f"branching) median {med(nos)} (min {nos[0] if nos else 0}, max "
        f"{nos[-1] if nos else 0}). Full table: `covmeet_census.csv`; per-class "
        f"rows incl. each class's own census: `covmeet_classes.csv`.",
        "",
        "## Reproduce / verify",
        "",
        "```bash",
        "PYTHONPATH=. python3 -m experiments.stable_ac.cov.meet.verify_covmeet "
        "<OUT_DIR> --full",
        "```",
        "",
        "Raw run state (snapshot + certs) is the user's `covmeet_out/` folder; the "
        "certs jsonl beside this page carries every merge/drop chain verbatim.",
    ]
    with open(os.path.join(results_dir, "COVMEET.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    # the certs file IS the certificate artifact — copy it in verbatim
    import shutil
    shutil.copy2(certs_path, os.path.join(results_dir,
                                          os.path.basename(certs_path)))
    print(f"results written to {results_dir}: COVMEET.md, covmeet_classes.csv "
          f"({len(rows)} rows), covmeet_census.csv ({len(ex)} rows), certs copy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
