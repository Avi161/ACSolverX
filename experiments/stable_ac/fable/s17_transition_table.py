"""S17 -- empirical ``gamma_N`` transition table for a SINGLE SPLIT step.

Read-and-tabulate only.  Nothing here searches the move tree: every parent/child pair is
*reconstructed* from a trace that is already on disk, and every defect is either *read*
from an already-persisted decided row or *measured* by the repo's exact census decider
(``cubic_split_search.fast_min_defect``, the same function ``cmd_decide`` used to write
those rows).

Why reconstruction is possible at all
-------------------------------------
``cubic_split_search.beam_search`` persists, for every pooled state, the ``root`` it came
from and the full ``trace`` of SPLIT records that produced it.  ``split_apply`` is
deterministic given a record, so the whole chain

    root = s_0 -> s_1 -> ... -> s_L = words

is replayable, and each consecutive pair is exactly ONE SPLIT step.  ``verify_split`` is
the repo's own machine check that a pair really is a SPLIT; a sample of reconstructed
chains is put through it, and every reconstructed terminal state is compared letter for
letter against the persisted ``words``.

Selection effects that the caller must be told about (they are reported in the JSON):
  * the pool only persists states with ``sum|delta| <= 4``, so a pair whose CHILD sits at
    depth 3 or 4 is conditioned on the child being near-cubic;
  * the beam keeps <= 40 children per level (70 % cost-ranked, 30 % random), so the edge
    set is a biased sample of all SPLIT children, not an exhaustive one;
  * intermediate states (depths 1, 2) are reconstructible only when they are ancestors of
    a pooled state.

Units: ``gamma_N = minimum_defect // 2``.  Everything internal is kept in
``minimum_defect`` and converted exactly once, at report time.

Usage
-----
    python3 -m experiments.stable_ac.fable.s17_transition_table \
        --out results/stable_ac/fable/s17_transition_table.json --budget 210
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from experiments.stable_ac.fable.cubic_split_search import (  # noqa: E402
    canon_state, census_size, fast_min_defect, split_apply, verify_split,
)

RES = "results/stable_ac/fable"

# (pool artifact, decided artifact, family tag)
FAMILIES = [
    (f"{RES}/s4b_pool.jsonl.gz", f"{RES}/s4b_decided.jsonl.gz", "ak3"),
    (f"{RES}/s4b_control_pool.jsonl.gz", f"{RES}/s4b_control_decided.jsonl.gz",
     "control0_thickenable"),
    (f"{RES}/s4b_ctrl2_pool.jsonl.gz", f"{RES}/s4b_ctrl2_decided.jsonl.gz",
     "control2_nonthickenable"),
]

CHAIN_FILES = [f"{RES}/s4b_ak3.jsonl", f"{RES}/s4b_ak3_run2.jsonl",
               f"{RES}/s4b_control.jsonl", f"{RES}/s4b_ctrl2.jsonl",
               f"{RES}/s4b_ladder.jsonl"]


def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def step_key(step):
    """A hashable, order-independent identity for one persisted SPLIT record."""
    return (step["relator"], bool(step["invert"]), step["rot"], step["t"],
            tuple(tuple(p) for p in step["positions"]))


def apply_step(state, step):
    got = split_apply(state, step["relator"], bool(step["invert"]), step["rot"],
                      [tuple(p) for p in step["positions"]], step["t"])
    return got  # (child, record) or None


def load_decided(paths):
    """canon_state(words) -> minimum_defect, read from persisted decided rows."""
    table = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        with _open(p) as fh:
            for line in fh:
                if not line.strip():
                    continue
                d = json.loads(line)
                if d.get("kind") or "minimum_defect" not in d:
                    continue
                table[canon_state(tuple(d["words"]))] = d["minimum_defect"]
    return table


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=f"{RES}/s17_transition_table.json")
    ap.add_argument("--edges-out", default=f"{RES}/s17_transition_edges.jsonl.gz")
    ap.add_argument("--budget", type=float, default=210.0,
                    help="hard wall-clock ceiling for the NEW decide work, seconds")
    ap.add_argument("--deep-cap", type=int, default=400_000,
                    help="census cap, matched to the deep_cap of the persisted runs")
    ap.add_argument("--verify-sample", type=int, default=400)
    ap.add_argument("--max-rows", type=int, default=0,
                    help="smoke-test only: cap pool rows read per family (0 = all)")
    ap.add_argument("--extra-decided", default="",
                    help="comma-separated extra decided artifacts to fold in (read-only)")
    ap.add_argument("--decided-cache", default=f"{RES}/s17_extra_decided.jsonl.gz",
                    help="where THIS run persists the defects it measures, so a rerun "
                         "can fold them back in via --extra-decided and spend its whole "
                         "budget on states nobody has decided yet")
    args = ap.parse_args(argv)

    t_start = time.time()
    report = {"kind": "s17_transition_table", "deep_cap": args.deep_cap}

    # ------------------------------------------------------------------ decided rows
    decided_paths = [d for _p, d, _f in FAMILIES]
    decided_paths += [p for p in args.extra_decided.split(",") if p.strip()]
    defect = load_decided(decided_paths)
    report["decided_rows_loaded"] = len(defect)
    report["decided_sources"] = decided_paths
    print(f"[s17] persisted decided states: {len(defect)}", flush=True)

    # ------------------------------------------------------------------ pool -> chains
    # edge identity: (canon parent, canon child); value: metadata of first sighting
    edges = {}
    state_words = {}            # canon -> words tuple (for later deciding)
    reconstruct_fail = 0
    terminal_mismatch = 0
    verified_chains = 0
    rows_seen = Counter()
    canon_cache = {}

    def canon(st):
        c = canon_cache.get(st)
        if c is None:
            c = canon_state(st)
            canon_cache[st] = c
        return c

    for pool_path, _dec, family in FAMILIES:
        if not os.path.exists(pool_path):
            continue
        memo = {}               # (root, prefix step_keys) -> state tuple
        with _open(pool_path) as fh:
            for lineno, line in enumerate(fh):
                if args.max_rows and lineno >= args.max_rows:
                    break
                if not line.strip():
                    continue
                r = json.loads(line)
                root = tuple(r["root"])
                trace = r["trace"]
                words = tuple(r["words"])
                rows_seen[family] += 1
                keys = tuple(step_key(s) for s in trace)
                memo[(root, ())] = root
                chain = [root]
                ok = True
                for i, step in enumerate(trace):
                    pk = (root, keys[:i + 1])
                    if pk in memo:
                        chain.append(memo[pk])
                        continue
                    got = apply_step(chain[-1], step)
                    if got is None:
                        ok = False
                        break
                    memo[pk] = got[0]
                    chain.append(got[0])
                if not ok:
                    reconstruct_fail += 1
                    continue
                if chain[-1] != words:
                    terminal_mismatch += 1
                    continue
                # sampled machine check that each pair really is a SPLIT
                if verified_chains < args.verify_sample and lineno % 97 == 0:
                    good = True
                    st = root
                    for step in trace:
                        got = apply_step(st, step)
                        if got is None or not verify_split(st, got[0], got[1]):
                            good = False
                            break
                        st = got[0]
                    if not good:
                        terminal_mismatch += 1
                        continue
                    verified_chains += 1
                for i in range(len(chain) - 1):
                    par, kid = chain[i], chain[i + 1]
                    cp, ck = canon(par), canon(kid)
                    if (cp, ck) in edges:
                        continue
                    edges[(cp, ck)] = {"family": family, "depth_parent": i,
                                       "rank_parent": len(par), "rank_child": len(kid),
                                       "parent": list(par), "child": list(kid)}
                    state_words.setdefault(cp, par)
                    state_words.setdefault(ck, kid)

    report["pool_rows_read"] = dict(rows_seen)
    report["chains_reconstruct_failed"] = reconstruct_fail
    report["chains_terminal_mismatch"] = terminal_mismatch
    report["chains_machine_verified_by_verify_split"] = verified_chains
    report["distinct_split_edges"] = len(edges)
    print(f"[s17] distinct SPLIT edges reconstructed: {len(edges)} "
          f"(fail {reconstruct_fail}, mismatch {terminal_mismatch}, "
          f"verify_split-checked chains {verified_chains})", flush=True)

    # ------------------------------------------------------- decide the missing states
    need = [c for c in state_words if c not in defect]
    # Priority: LOW RANK FIRST.  The rank-9 roots and the depth-1/2 states are few, are the
    # only source of the early layers of the chain, and are irreplaceable; the leftover
    # rank-12/13 states are numerous and interchangeable.  A pure census sort buries the
    # roots (their census is the largest) and loses the root -> d1 layer entirely.
    need.sort(key=lambda c: (len(state_words[c]), census_size(state_words[c])))
    over_cap = 0
    newly = 0
    t_dec = time.time()
    deadline = t_start + args.budget
    ran_out = False
    cache_fh = gzip.open(args.decided_cache, "wt") if args.decided_cache else None
    for c in need:
        if time.time() > deadline:
            ran_out = True
            break
        st = state_words[c]
        if census_size(st) > args.deep_cap:
            over_cap += 1
            continue
        defect[c] = fast_min_defect(st)
        newly += 1
        if cache_fh is not None:
            cache_fh.write(json.dumps({"words": list(st), "rank": len(st),
                                       "minimum_defect": defect[c],
                                       "provenance": "s17_reconstructed"}) + "\n")
        if newly % 1000 == 0:
            if cache_fh is not None:
                cache_fh.flush()
            print(f"[s17]   decided {newly}/{len(need)} new states "
                  f"{time.time() - t_dec:.0f}s", flush=True)
    if cache_fh is not None:
        cache_fh.close()
    report["states_needing_decision"] = len(need)
    report["states_needing_decision_by_rank"] = dict(sorted(
        Counter(len(state_words[c]) for c in need).items()))
    report["states_left_undecided_by_rank"] = dict(sorted(
        Counter(len(state_words[c]) for c in need if c not in defect).items()))
    report["states_newly_decided_here"] = newly
    report["states_over_census_cap"] = over_cap
    report["states_left_undecided_budget"] = len(need) - newly - over_cap
    report["decide_seconds"] = round(time.time() - t_dec, 1)
    report["decide_budget_exhausted"] = ran_out
    print(f"[s17] newly decided {newly}, over cap {over_cap}, "
          f"left undecided {len(need) - newly - over_cap}", flush=True)

    # ------------------------------------------------------------------ the table
    def cells():
        return defaultdict(Counter)

    overall = cells()
    by_family = defaultdict(cells)
    by_layer = defaultdict(cells)
    by_family_layer = defaultdict(cells)
    dropped = Counter()
    one_to_zero_examples = []
    creations = []              # positive -> 0, any row
    destructions = []           # 0 -> positive

    ekeys = list(edges.items())
    for (cp, ck), meta in ekeys:
        dp, dc = defect.get(cp), defect.get(ck)
        if dp is None or dc is None:
            dropped["parent_unknown" if dp is None else "child_unknown"] += 1
            meta["gamma_parent"] = None if dp is None else dp // 2
            meta["gamma_child"] = None if dc is None else dc // 2
            continue
        gp, gc = dp // 2, dc // 2
        meta["gamma_parent"], meta["gamma_child"] = gp, gc
        overall[gp][gc] += 1
        by_family[meta["family"]][gp][gc] += 1
        lay = f"rank{meta['rank_parent']}->rank{meta['rank_child']}"
        by_layer[lay][gp][gc] += 1
        by_family_layer[f"{meta['family']}|{lay}"][gp][gc] += 1
        if gc == 0 and gp > 0:
            creations.append(meta)
            if gp == 1:
                one_to_zero_examples.append(meta)
        if gp == 0 and gc > 0:
            destructions.append(meta)

    def dump(tbl):
        return {str(a): {str(b): n for b, n in sorted(row.items())}
                for a, row in sorted(tbl.items())}

    report["transition_matrix_gamma_N"] = dump(overall)
    report["transition_matrix_by_family"] = {k: dump(v) for k, v in sorted(by_family.items())}
    report["transition_matrix_by_layer"] = {k: dump(v) for k, v in sorted(by_layer.items())}
    report["transition_matrix_by_family_layer"] = {
        k: dump(v) for k, v in sorted(by_family_layer.items())}
    report["edges_dropped_unknown_defect"] = dict(dropped)
    report["pairs_in_matrix"] = sum(sum(r.values()) for r in overall.values())

    # ------------------------------------------------------------- the 1 -> 0 question
    opp1 = sum(overall[1].values())
    report["cell_1_to_0"] = {
        "count": overall[1].get(0, 0),
        "opportunities_pairs_with_parent_gamma1": opp1,
        "distinct_parent_states_at_gamma1_with_an_outgoing_split": len(
            {cp for (cp, _ck), m in ekeys
             if m.get("gamma_parent") == 1}),
        "row": {str(b): n for b, n in sorted(overall[1].items())},
        "by_family": {f: {str(b): n for b, n in sorted(by_family[f][1].items())}
                      for f in sorted(by_family)},
    }
    report["creations_positive_to_zero"] = [
        {k: v for k, v in m.items() if k != "parent" and k != "child"}
        for m in creations[:50]]
    report["n_creations_positive_to_zero"] = len(creations)

    # ------------------------------------------------- control certificate destruction
    ctrl = by_family.get("control0_thickenable", cells())
    row0 = ctrl.get(0, Counter())
    tot0 = sum(row0.values())
    report["control0_certificate_fate"] = {
        "pairs_with_parent_gamma0": tot0,
        "row": {str(b): n for b, n in sorted(row0.items())},
        "preserved_0_to_0": row0.get(0, 0),
        "destroyed_0_to_positive": tot0 - row0.get(0, 0),
        "destruction_rate": (round((tot0 - row0.get(0, 0)) / tot0, 4) if tot0 else None),
    }
    # same quantity pooled over every family that has any gamma0 parent at all
    orow0 = overall.get(0, Counter())
    otot0 = sum(orow0.values())
    report["pooled_certificate_fate"] = {
        "pairs_with_parent_gamma0": otot0,
        "row": {str(b): n for b, n in sorted(orow0.items())},
        "destroyed_0_to_positive": otot0 - orow0.get(0, 0),
        "destruction_rate": (round((otot0 - orow0.get(0, 0)) / otot0, 4) if otot0 else None),
    }

    # ------------------------------------------------ already-persisted depth-1 census
    flips = None
    fp = f"{RES}/s4b_flips.jsonl"
    if os.path.exists(fp):
        for line in open(fp):
            d = json.loads(line)
            if d.get("kind") == "flip_summary":
                flips = d
    if flips is not None:
        def conv(dp):
            out = defaultdict(Counter)
            for k, v in dp.items():
                a, b = k.split("->")
                out[int(a) // 2][int(b) // 2] += v
            return dump(out)
        report["depth1_flip_census_rank5"] = {
            "note": "already on disk (s4b_flips.jsonl); one SPLIT from a triangulated "
                    "rank-2 source of total length 9; DEPTH 1 ONLY",
            "sources": flips["sources"], "parents_measured": flips["parents_measured"],
            "split_matrix_gamma_N": conv(flips["split"]["defect_pairs"]),
            "ac2_control_matrix_gamma_N": conv(flips["ac2_control"]["defect_pairs"]),
            "split_pairs": flips["split"]["pairs"],
            "ac2_pairs": flips["ac2_control"]["pairs"],
        }

    # ------------------------------------------------------------------ traced chains
    tr = []
    for p in CHAIN_FILES:
        if not os.path.exists(p):
            continue
        for line in open(p):
            d = json.loads(line)
            if d.get("status") in ("CUBIC", "GAMMA0") and d.get("trace"):
                tr.append({"file": os.path.basename(p), "depth": len(d["trace"]),
                           "provenance": d.get("provenance"),
                           "final_minimum_defect": (d.get("gamma") or {}).get(
                               "minimum_defect")})
    report["traced_terminal_chains"] = tr

    report["elapsed_s"] = round(time.time() - t_start, 1)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    with gzip.open(args.edges_out, "wt") as fh:
        for (cp, ck), m in ekeys:
            fh.write(json.dumps({"parent": m["parent"], "child": m["child"],
                                 "family": m["family"],
                                 "depth_parent": m["depth_parent"],
                                 "rank_parent": m["rank_parent"],
                                 "gamma_parent": m.get("gamma_parent"),
                                 "gamma_child": m.get("gamma_child")}) + "\n")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("creations_positive_to_zero", "decided_sources",
                                   "traced_terminal_chains")}, indent=1), flush=True)
    return report


if __name__ == "__main__":
    main()
