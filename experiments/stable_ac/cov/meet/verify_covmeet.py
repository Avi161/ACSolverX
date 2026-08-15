"""Independent check of a covmeet run: load the snapshot, certify the chains.

v3 storage keeps two artifacts: the binary snapshot (the whole store — integrity-hashed,
loaded and cross-checked here) and the certs jsonl (results only — seeds, merges,
drops, with full chains). Verification layers:

* **snapshot pass**: loads and hash-verifies the snapshot; the loader independently
  re-derives union-find classes from the MASKS alone and refuses a snapshot whose
  recorded merges disagree with them;
* **chain pass** (always, every chain): each recorded chain replays SEGMENT BY SEGMENT
  — ``cov_branches`` on the previous rep with the recorded ``(z, iso, br)``, then the
  real ``aut_min``, must land exactly on the recorded next rep (lesson:
  cov-chains-junction-at-canonical-reps; chains are never concatenated). Duplicate
  certificate rows (a re-done crash interval re-firing a merge) are deduped;
* **self-canonical sample**: ``--sample K`` (default 1000; ``--full`` = all) snapshot
  orbits are checked to be genuine Aut-minimal fixed points — ``aut_min(rep) == rep``
  — a real property, not a round-trip;
* seed reps must carry their own bit; the summary json must agree with the store.

Exit 0 = everything checked verifies.

    PYTHONPATH=. python3 -m experiments.stable_ac.cov.meet.verify_covmeet OUT_DIR \
        [--seed-set all124] [--sample 1000 | --full]
"""

import argparse
import json
import os
import sys

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.ladder import autcanon_fast as af
from experiments.stable_ac.cov.meet import covmeet
from experiments.stable_ac.cov.meet.covmeet import _dec_rep


def replay_step(prev_rep, z, iso, br):
    """All aut-min orbits the recorded move can produce from ``prev_rep``."""
    wa, wb = str_to_word(prev_rep[0]), str_to_word(prev_rep[1])
    outs = []
    for res in cov.cov_branches(wa, wb, str_to_word(z),
                                reject_len=covmeet.REJECT_LEN_UNCAPPED, iso_gen=iso):
        if int(res.iso_index) == br:
            outs.append(af.aut_min((word_to_str(res.r1), word_to_str(res.r2)))[1])
    return outs


def verify_chain(chain):
    """(ok, n_segments, truncated). Replays every consecutive step of one chain."""
    head = chain[0]
    truncated = bool(head.get("truncated"))
    prev = _dec_rep(head["rep"])
    n = 0
    for step in chain[1:]:
        want = _dec_rep(step["rep"])
        if want not in replay_step(prev, step["z"], step["iso"], step["br"]):
            return False, n, truncated
        prev = want
        n += 1
    return True, n, truncated


def main(argv=None, seeds_override=None):
    """``seeds_override`` is the same TEST seam ``covmeet.run`` has."""
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed-set", default="all124")
    ap.add_argument("--sample", type=int, default=1000)
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args(argv)

    certs_path, summary_path = covmeet.run_paths(args.out_dir, args.seed_set)
    seeds = seeds_override if seeds_override is not None \
        else covmeet.load_seeds(args.seed_set)

    # -- snapshot pass: load() hash-verifies and cross-checks merges against masks
    store, header = covmeet.load(args.out_dir, args.seed_set, len(seeds),
                                 expect_family=covmeet.FAMILY)
    if header is None:
        print(f"FAIL: no readable snapshot in {args.out_dir}")
        return 1
    summary = covmeet.summarise(store, seeds)
    print(f"snapshot: {len(store.mask):,} orbits, {len(store.expanded):,} expanded, "
          f"{summary['merges_found']} merges, {summary['n_improved']} improved, "
          f"classes {summary['classes_remaining']}/{len(seeds)}")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            written = json.load(f)
        for key in ("classes_remaining", "merges_found", "n_improved",
                    "expanded", "discovered"):
            if written.get(key) != summary[key]:
                print(f"FAIL: summary json {key}={written.get(key)} but the "
                      f"snapshot says {summary[key]}")
                return 1

    # -- certificate rows: dedupe (a re-done crash interval may re-fire a merge)
    cert_merges, cert_drops = {}, {}
    if os.path.exists(certs_path):
        with open(certs_path) as f:
            for line in f:
                ev = json.loads(line)
                if ev["t"] == "merge":
                    cert_merges[frozenset(ev["classes"])] = ev
                elif ev["t"] == "drop":
                    cert_drops[(ev["name"], ev["mu"])] = ev
    if len(cert_merges) != summary["merges_found"]:
        print(f"FAIL: {len(cert_merges)} distinct merge certificates but the "
              f"snapshot masks derive {summary['merges_found']}")
        return 1

    # -- seed reps must carry their own bit
    af.warm()
    for i, (name, r1, r2) in enumerate(seeds):
        mu, rep = af.aut_min((r1, r2))
        if store.mask.get(rep, 0) >> i & 1 == 0:
            print(f"FAIL: seed {name} rep {rep} missing its own bit")
            return 1

    # -- chain pass
    bad = n_chains = n_trunc = 0
    for ev in cert_merges.values():
        ends = []
        for chain in ev["chains"]:
            ok, nseg, trunc = verify_chain(chain)
            n_chains += 1
            n_trunc += trunc
            if not ok:
                bad += 1
                print(f"FAIL chain (merge {ev['classes']}): a segment does not replay")
            ends.append(_dec_rep(chain[-1]["rep"]))
        if ends[0] != ends[1] or ends[0] != _dec_rep(ev["rep"]):
            bad += 1
            print(f"FAIL merge {ev['classes']}: chains do not meet at the "
                  f"recorded orbit")
    for ev in cert_drops.values():
        ok, nseg, trunc = verify_chain(ev["chain"])
        n_chains += 1
        n_trunc += trunc
        if not ok:
            bad += 1
            print(f"FAIL chain (drop {ev['name']}): a segment does not replay")
        drep = _dec_rep(ev["rep"])
        if _dec_rep(ev["chain"][-1]["rep"]) != drep or \
                len(drep[0]) + len(drep[1]) != ev["mu"]:
            bad += 1
            print(f"FAIL drop {ev['name']}: chain end or mu mismatch")

    # -- self-canonical sample: stored orbits must be aut_min fixed points
    picked = store.reps if args.full else \
        store.reps[::max(1, len(store.reps) // max(args.sample, 1))][:args.sample]
    for rep in picked:
        mu, canon = af.aut_min(rep)
        if canon != rep or mu != len(rep[0]) + len(rep[1]):
            print(f"FAIL: stored orbit {rep} is not aut-min canonical")
            return 1

    if bad:
        print(f"FAIL: {bad} certificate failures across {n_chains} chains")
        return 1
    trunc_note = f" ({n_trunc} truncated — deterministic re-run recovers them)" \
        if n_trunc else ""
    print(f"OK: {n_chains} chains replay segment-by-segment{trunc_note}; "
          f"{len(picked)} orbits are aut-min fixed points; "
          f"classes {summary['classes_remaining']}/{len(seeds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
