"""Independent check of a covmeet events file: replay edges, re-derive the classes.

Two layers, per the CoV-chain lesson (cov-chains-junction-at-canonical-reps): a chain
is only as good as its segments, so verification is EDGE-local — recompute each
recorded (parent, z, iso_gen, iso_index) move with the real ``cov_branches``, Aut-min
the output with the real ``aut_min``, and require the recorded child rep and mu. No
chain concatenation anywhere.

    PYTHONPATH=. python3 -m experiments.stable_ac.cov.meet.verify_covmeet OUT_DIR \
        [--seed-set all124] [--sample 1000 | --full]

* structural pass (always): every line parses; masks replay; merges re-derive; the
  summary json (if present) agrees with the replayed classes_remaining count.
* edge pass: ``--sample K`` replays K deterministically-spaced edges (default 1000);
  ``--full`` replays every edge — the full pass costs about what the run cost.

Exit 0 = everything checked verifies. Any failure prints and exits 1.
"""

import argparse
import json
import os
import sys

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.ladder import autcanon_fast as af
from experiments.stable_ac.cov.meet import covmeet


def replay_edge(par, z, iso, br):
    """All aut-min orbits the recorded move can produce (branch ``br`` of (z, iso))."""
    wa, wb = str_to_word(par[0]), str_to_word(par[1])
    outs = []
    for res in cov.cov_branches(wa, wb, str_to_word(z),
                                reject_len=covmeet.REJECT_LEN_UNCAPPED, iso_gen=iso):
        if int(res.iso_index) == br:
            outs.append(af.aut_min((word_to_str(res.r1), word_to_str(res.r2))))
    return outs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed-set", default="all124", choices=covmeet.SEED_SETS)
    ap.add_argument("--sample", type=int, default=1000)
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args(argv)

    events_path, summary_path = covmeet.run_paths(args.out_dir, args.seed_set)
    if not os.path.exists(events_path):
        print(f"FAIL: no events file at {events_path}")
        return 1
    seeds = covmeet.load_seeds(args.seed_set)

    # -- structural: full replay (parses every line, rebuilds masks, re-derives merges)
    store, meta = covmeet.replay(events_path, len(seeds),
                                 expect_family=covmeet.FAMILY)
    if meta is None:
        print("FAIL: events file has no meta row")
        return 1
    summary = covmeet.summarise(store, seeds)
    print(f"replayed: {store.n_edges:,} edges, {len(store.mask):,} orbits, "
          f"{len(store.expanded):,} expanded, {summary['merges_found']} merges, "
          f"classes {summary['classes_remaining']}/{len(seeds)}")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            written = json.load(f)
        for key in ("classes_remaining", "merges_found"):
            if written.get(key) != summary[key]:
                print(f"FAIL: summary json {key}={written.get(key)} but replay "
                      f"says {summary[key]}")
                return 1

    # -- seed rows must match the dataset (the run's inputs are the csv's rows)
    af.warm()
    for i, (name, r1, r2) in enumerate(seeds):
        mu, rep = af.aut_min((r1, r2))
        if store.mask.get(rep, 0) >> i & 1 == 0:
            print(f"FAIL: seed {name} rep {rep} missing its own bit")
            return 1

    # -- edge replay: every recorded move must reproduce its recorded (rep, mu)
    edges = []
    with open(events_path) as f:
        for line in f:
            ev = json.loads(line)
            if ev["t"] == "edge":
                edges.append(ev)
    if args.full:
        picked = edges
    else:
        step = max(1, len(edges) // max(args.sample, 1))
        picked = edges[::step][:args.sample]
    bad = 0
    for ev in picked:
        want = (ev["mu"], tuple(ev["rep"]))
        got = replay_edge(ev["par"], ev["z"], ev["iso"], ev["br"])
        if want not in got:
            bad += 1
            print(f"FAIL edge: parent {ev['par']} z={ev['z']} iso={ev['iso']} "
                  f"br={ev['br']} recorded {want} but replay gives {got}")
    mode = "full" if args.full else f"sample {len(picked)}"
    if bad:
        print(f"FAIL: {bad}/{len(picked)} edges do not replay ({mode})")
        return 1
    print(f"OK: {len(picked)} edges replay exactly ({mode}); "
          f"classes {summary['classes_remaining']}/{len(seeds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
