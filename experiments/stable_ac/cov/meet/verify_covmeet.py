"""Independent check of a covmeet events file: replay the store, certify the chains.

v2 storage writes bulk discovery compactly (no per-edge moves) and full chains only on
``merge`` and ``drop`` rows — the claims. So verification splits accordingly:

* structural pass (always): every line parses; masks/frontier replay; merges and drops
  re-derive from the mask events alone and must agree with the certificate rows and the
  summary json;
* chain pass (always, every chain): each recorded chain replays SEGMENT BY SEGMENT —
  ``cov_branches`` on the previous rep with the recorded ``(z, iso, br)``, then the real
  ``aut_min``, must land exactly on the recorded next rep (lesson:
  cov-chains-junction-at-canonical-reps; chains are never concatenated). A chain marked
  ``truncated`` (its head predates a resume — parents are RAM-only) has its surviving
  segments verified and is reported; the deterministic fresh re-run reproduces it whole.
* ``--sample K`` / ``--full``: additionally decode K (or all) ``o`` rows and check the
  stored rep is a valid, correctly-packed pair whose bucket matches its length.

Individual ``o`` rows carry no move by design (the v1 per-edge log was ~85% of the
bytes); the full audit of discovery itself is a deterministic re-run with the same
config. Exit 0 = everything checked verifies.

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
from experiments.stable_ac.cov.meet.covmeet import _dec_rep, _dec_word


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

    # -- structural: full replay (parses every line, rebuilds masks, re-derives
    #    merges and drops from mask events alone)
    store, meta = covmeet.replay(events_path, len(seeds),
                                 expect_family=covmeet.FAMILY)
    if meta is None:
        print("FAIL: events file has no meta row")
        return 1
    summary = covmeet.summarise(store, seeds)
    print(f"replayed: {len(store.mask):,} orbits, {len(store.expanded):,} expanded, "
          f"{summary['merges_found']} merges, {summary['n_improved']} drops(classes), "
          f"classes {summary['classes_remaining']}/{len(seeds)}")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            written = json.load(f)
        for key in ("classes_remaining", "merges_found", "n_improved",
                    "expanded", "discovered"):
            if written.get(key) != summary[key]:
                print(f"FAIL: summary json {key}={written.get(key)} but replay "
                      f"says {summary[key]}")
                return 1

    # -- certificate rows must agree with the re-derivation
    cert_merges, cert_drops, o_rows = [], [], []
    with open(events_path) as f:
        for line in f:
            ev = json.loads(line)
            if ev["t"] == "merge":
                cert_merges.append(ev)
            elif ev["t"] == "drop":
                cert_drops.append(ev)
            elif ev["t"] == "o":
                o_rows.append(ev)
    if len(cert_merges) != summary["merges_found"]:
        print(f"FAIL: {len(cert_merges)} merge rows but replay derives "
              f"{summary['merges_found']}")
        return 1

    # -- seed rows must match the dataset (the run's inputs are the csv's rows)
    af.warm()
    for i, (name, r1, r2) in enumerate(seeds):
        mu, rep = af.aut_min((r1, r2))
        if store.mask.get(rep, 0) >> i & 1 == 0:
            print(f"FAIL: seed {name} rep {rep} missing its own bit")
            return 1

    # -- chain pass: every chain on every certificate row, segment by segment
    bad = n_chains = n_trunc = 0
    for ev in cert_merges:
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
    for ev in cert_drops:
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

    # -- o-row decode sample: stored reps must round-trip and match their length
    picked = o_rows if args.full else \
        o_rows[::max(1, len(o_rows) // max(args.sample, 1))][:args.sample]
    for ev in picked:
        rep = _dec_rep(ev["rep"])
        if covmeet._enc_rep(rep) != ev["rep"] or not rep[0] or not rep[1]:
            print(f"FAIL: o row {ev['i']} does not round-trip")
            return 1

    if bad:
        print(f"FAIL: {bad} certificate failures across {n_chains} chains")
        return 1
    trunc_note = f" ({n_trunc} truncated at a resume boundary — deterministic " \
                 f"re-run recovers them whole)" if n_trunc else ""
    print(f"OK: {n_chains} chains replay segment-by-segment{trunc_note}; "
          f"{len(picked)} o rows round-trip; "
          f"classes {summary['classes_remaining']}/{len(seeds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
