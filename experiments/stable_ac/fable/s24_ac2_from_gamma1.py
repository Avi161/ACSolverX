"""S24 -- AC2-driven search launched from AK(3)-class states already at ``gamma_N = 1``.

NEW FILE.  Nothing under ``experiments/`` is modified.  Four existing modules are imported
READ-ONLY:

* ``s12_hunt``            -- ``slides`` (the conjugated AC2 move family), ``canon``,
                             ``cyclered``, ``decide`` (cut-scheme solver then exact census);
* ``s20_planarity_probe`` -- ``probe_words`` (certified Demoucron planarity of the link);
* ``s18_s5_chain_audit``  -- ``defect_of`` (exact census where it fits, else the verdict);
* ``neuwirth_rank_n``     -- only through the two above.

WHY THIS FILE EXISTS.  ``S17_TRANSITION_TABLE.md`` measured that the cubic pipeline's
length-3 SPLIT move takes ``gamma_N = 1 -> 0`` **zero times in 56,388 opportunities** from
1,958 distinct ``gamma_N = 1`` parents, while on *identical* rank-5 parents plain **AC2**
made that step **14 times in 1,470**.  Every high-rank search on this line used SPLIT, i.e.
the move that provably never takes the last step in this corpus.  AK(3)'s own persisted pool
contains **527 states at ``gamma_N = 1``** (``minimum_defect = 2``) at rank 12.  This file
launches an AC2-rich, SPLIT-free search from those states.

UNITS, stated once.  ``gamma_N = minimum_defect // 2``.  Every artifact on disk stores
``minimum_defect``.  The launch set is ``minimum_defect == 2``, i.e. ``gamma_N == 1``.
(``experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md``.)

BOUND DIRECTION.  This is a ONE-SIDED, upper-bound-only instrument.  A hit certifies
``gamma_N = 0`` for that state, i.e. bounds ``Gamma`` from ABOVE.  A null bounds NOTHING
from below (``experiments/lessons/parallel-runs-and-bound-direction.md``).

MOVE SET (AC2-rich, no SPLIT).  ``s12_hunt.slides`` proposes
``r_i <- cyclered(r_i * u r_j^{eps} u^{-1})`` with a random rotation of ``r_j``.  That one
generator realises AC2 (the multiply), AC1 on ``r_j`` (``eps = -1``, probability 1/2), AC3
(conjugation by a generator, probability 1/2) and move (0) (``cyclered``).  Bare AC1 on
``r_i`` and bare AC3 on ``r_i`` are *inert modulo* ``canon``: ``canon`` keys on the
lexicographically least rotation of the word or its inverse, so inverting or conjugating
``r_i`` alone cannot produce a state the seen-set regards as new.  No SPLIT, no AC4, no AC5:
the rank never changes and no new generator is ever introduced.

GOAL TEST, cheap first (this is the point of the design):
  (a) linear-time planarity reject -- non-planar link => ``gamma_N >= 1`` (Theorem S20.1,
      proved in ``S20_PLANARITY_OBSTRUCTION.md``), so a non-planar child cannot be a
      certificate and is discarded WITHOUT a census;
  (b) exact census only for planar survivors, through ``s12_hunt.decide``.

INSTRUMENTATION (``experiments/lessons/instrument-the-search-before-reading-its-null.md``):
every trial row carries ``pops``, ``decided``, ``undecided``, ``planar_rejects``,
``planar_pass``, ``restarts``, ``budget`` and ``pops_reached_budget``.  A run whose ``pops``
did not reach the node budget is starved and its null is not readable.

PERSISTENCE.  One JSONL row per trial, appended, flushed and ``fsync``-ed as it goes.

BAND ACCOUNTING (T-S20, ``experiments/lessons/
control-escapes-through-a-region-the-target-cannot-enter.md``).  Every hit records the FULL
chain, and every chain node records ``gamma_N``, ``total_length`` and ``min_relator_length``.
Hits are reported three ways: raw; in band by total length >= 13; in band by minimum relator
length >= 6.  NOTE, stated here because it is a real limitation of this corpus: the launch
states are *cubic* rank-12 refinements, whose own minimum relator length is 3, so the third
criterion is vacuous on BOTH arms -- it excludes the start state itself.  A fourth,
corpus-appropriate criterion is therefore also reported: ``no_escape``, meaning the chain
never drops below the START state's own total length and minimum relator length.

Sub-commands
------------
    launch : extract + verify the gamma_N = 1 launch set from the persisted pools
    hunt   : run AC2 searches from a launch set, one fsync'd JSONL row per trial
    table  : aggregate JSONL rows into the raw / in-band tables
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import s12_hunt as H            # noqa: E402
from experiments.stable_ac.fable import s20_planarity_probe as P  # noqa: E402
from experiments.stable_ac.fable import s18_s5_chain_audit as S18  # noqa: E402
from experiments.stable_ac.fable.neuwirth_rank_n import (          # noqa: E402
    build_link_n, census_size)

OUT_DIR = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")
BAND_TOTAL = 13      # AK(3)'s total length -- the Havas-Ramsay floor
BAND_MINREL = 6      # AK(3)'s minimum relator length

POOLS = {
    "ak3": "s4b_decided.jsonl.gz",
    "control0": "s4b_control_decided.jsonl.gz",
    "control2": "s4b_ctrl2_decided.jsonl.gz",
}


# ------------------------------------------------------------------ helpers

def total_len(words):
    return sum(len(w) for w in words)


def min_rel(words):
    return min(len(w) for w in words if w) if any(words) else 0


def gens_of(words):
    return tuple(sorted(set("".join(words).lower())))


def _append_jsonl(path, row):
    """Append ONE row, flush and fsync.  Two runs on 2026-08-04 died writing only at end."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


# ------------------------------------------------------------------ launch set

def cmd_launch(args):
    """All states at ``minimum_defect == 2`` (gamma_N == 1) in the persisted pools.

    A sample is re-decided here with the repo's own decider, so the set is not taken on the
    persisted number's word alone.
    """
    t0 = time.time()
    out = {"record": "s24_launch_set", "args": vars(args), "families": {}}
    rng = random.Random(args.seed)
    for fam, fname in POOLS.items():
        path = os.path.join(OUT_DIR, fname)
        rows, ranks, lens, mrs = [], {}, {}, {}
        with gzip.open(path, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("minimum_defect") != 2:
                    continue
                w = tuple(r["words"])
                rows.append({"words": list(w), "rank": r["rank"],
                             "minimum_defect": r["minimum_defect"],
                             "census": r.get("census"),
                             "provenance": r.get("provenance"),
                             "total_length": total_len(w), "min_rel": min_rel(w)})
                ranks[r["rank"]] = ranks.get(r["rank"], 0) + 1
                lens[total_len(w)] = lens.get(total_len(w), 0) + 1
                mrs[min_rel(w)] = mrs.get(min_rel(w), 0) + 1
        distinct = {tuple(r["words"]) for r in rows}
        # verification sample: recompute the defect with the repo's own exact census
        sample = rng.sample(rows, min(args.verify, len(rows))) if rows else []
        ver = []
        for r in sample:
            d = S18.defect_of(tuple(r["words"]))
            ver.append({"words": r["words"], "persisted_defect": 2,
                        "recomputed_defect": d.get("defect"),
                        "recomputed_gamma_N": d.get("gamma_N"),
                        "method": d.get("method"), "verdict": d.get("verdict"),
                        "agree": d.get("defect") == 2})
        agree = sum(1 for v in ver if v["agree"])
        out["families"][fam] = {
            "pool_file": fname, "rows_at_defect2": len(rows),
            "distinct_states": len(distinct), "by_rank": ranks,
            "total_length_hist": dict(sorted(lens.items())),
            "min_relator_length_hist": dict(sorted(mrs.items())),
            "verify_sample": len(ver), "verify_agree": agree, "verify_rows": ver,
        }
        print(f"[s24] {fam:9s} defect-2 rows={len(rows):5d} distinct={len(distinct):5d} "
              f"ranks={ranks} verify {agree}/{len(ver)}", flush=True)
        # persist the launch states themselves
        lp = os.path.join(OUT_DIR, f"s24_launch_{fam}.jsonl")
        if os.path.exists(lp):
            os.remove(lp)
        for r in rows:
            _append_jsonl(lp, r)
    out["elapsed_s"] = round(time.time() - t0, 1)
    p = os.path.join(OUT_DIR, "s24_launch_set.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"[s24] wrote {p}  ({out['elapsed_s']}s)", flush=True)


# ------------------------------------------------------------------ the search

def screen(words, cache_p, cache_d, stats, census_cap):
    """(a) certified planarity reject, then (b) exact decision.  Returns a verdict dict."""
    k = H.canon(words)
    if k in cache_d:
        return cache_d[k]
    pr = cache_p.get(k)
    if pr is None:
        try:
            pr = P.probe_words(tuple(w for w in words if w))
        except Exception as exc:                       # fail OPEN: never reject on a crash
            pr = {"status": "PROBE_EXC", "planar": None, "certified": False,
                  "reason": type(exc).__name__}
        cache_p[k] = pr
    # S20.1: non-planar link => gamma_N >= 1, so the state cannot be a certificate.
    # Only a CERTIFIED non-planar verdict is allowed to reject (Kuratowski witness).
    if pr.get("planar") is False and pr.get("certified"):
        stats["planar_rejects"] += 1
        res = {"verdict": "NOT_SPHERICAL", "method": "s20_planarity_reject"}
        cache_d[k] = res
        return res
    stats["planar_pass"] += 1
    # Exact census FIRST when it fits (cheap: a cubic rank-12 state has census 9,216); the
    # cut-scheme solver is the fallback.  Measured 2026-08-04: ``H.decide`` alone spends
    # ~10 s per state inside the SPQR decomposition, which would have made this search
    # unrunnable inside the node budget.  ``S18.defect_of`` is exactly this ordering and is
    # the same exact census that wrote the persisted ``minimum_defect`` rows.
    ws = tuple(w for w in words if w)
    try:
        size = census_size(build_link_n(ws, gens_of(ws)), gens_of(ws))
    except Exception:
        size = None
    if size is None or size > census_cap:
        # MEASURED 2026-08-04: EVERY planar survivor of an AC2 move from these rank-12
        # cubic states has census > 200,000, so the exact-census arm alone is blind here.
        # Fall back to the repo's certified cut-scheme solver (~10 s/state), under a
        # per-trial budget so one trial cannot eat the wall clock.
        if stats["solver_calls"] < stats["solver_budget"]:
            stats["solver_calls"] += 1
            d = H.decide(ws, census_cap)
            if d["verdict"] == H.UNDECIDED:
                stats["undecided"] += 1
            else:
                stats["decided"] += 1
                stats["decided_by_solver"] += 1
            cache_d[k] = d
            return d
        stats["undecided"] += 1
        stats["undecided_solver_budget"] += 1
        res = {"verdict": H.UNDECIDED, "method": "census_over_cap", "census": size}
        cache_d[k] = res
        return res
    rec = S18.defect_of(ws)
    if rec.get("defect") is not None:
        d = {"verdict": "SPHERICAL" if rec["defect"] == 0 else "NOT_SPHERICAL",
             "method": rec.get("method"), "defect": rec["defect"]}
    elif rec.get("verdict") in ("SPHERICAL", "NOT_SPHERICAL"):
        d = {"verdict": rec["verdict"], "method": rec.get("method")}
    else:
        d = {"verdict": H.UNDECIDED, "method": rec.get("method")}
    if d["verdict"] == H.UNDECIDED:
        stats["undecided"] += 1
    else:
        stats["decided"] += 1
    cache_d[k] = d
    return d


def hunt_ac2(start, nodes, rng, *, beam=6, branch=8, max_rel=None, max_tot=None,
             rel_headroom=4, tot_headroom=8, census_cap=200_000, solver_budget=12):
    """AC2-rich beam search from ``start`` with the S20 planarity screen in front.

    Length caps are RELATIVE TO THE ROOT (filed lesson: absolute caps starve long roots):
    per-relator cap = ``max relator length of the root + rel_headroom``;
    total cap        = ``total length of the root + tot_headroom``.
    """
    start = tuple(w for w in start if w)
    gens = gens_of(start)
    if max_rel is None:
        max_rel = max(len(w) for w in start) + rel_headroom
    if max_tot is None:
        max_tot = total_len(start) + tot_headroom
    seen = {H.canon(start)}
    frontier = [start]
    parent = {start: None}
    stats = {"pops": 0, "decided": 0, "undecided": 0, "spherical": 0, "restarts": 0,
             "planar_rejects": 0, "planar_pass": 0, "generated": 0,
             "solver_calls": 0, "solver_budget": solver_budget, "decided_by_solver": 0,
             "undecided_solver_budget": 0}
    cache_p, cache_d = {}, {}
    d0 = screen(start, cache_p, cache_d, stats, census_cap)
    if d0["verdict"] == "SPHERICAL":
        stats["spherical"] += 1
        return start, d0, stats, parent
    pool_cap = 4000
    visited = [start]
    while stats["pops"] < nodes:
        if not frontier:
            stats["restarts"] += 1
            frontier = [visited[rng.randrange(len(visited))] for _ in range(4)]
        frontier.sort(key=lambda w: total_len(w))
        del frontier[pool_cap:]
        idx = (rng.randrange(len(frontier)) if rng.random() < 0.25
               else rng.randrange(min(beam, len(frontier))))
        cur = frontier.pop(idx)
        stats["pops"] += 1
        for nb in H.slides(cur, gens, rng, max_rel, max_tot, branch):
            k = H.canon(nb)
            if k in seen:
                continue
            seen.add(k)
            stats["generated"] += 1
            parent.setdefault(nb, cur)
            d = screen(nb, cache_p, cache_d, stats, census_cap)
            if d["verdict"] == "SPHERICAL":
                stats["spherical"] += 1
                return nb, d, stats, parent
            frontier.append(nb)
            if len(visited) < 20_000:
                visited.append(nb)
    return None, None, stats, parent


def chain_of(node, parent):
    ch = []
    while node is not None:
        ch.append(node)
        node = parent.get(node)
    ch.reverse()
    return ch


def chain_record(chain):
    """Full per-node record: gamma_N, total length, minimum relator length."""
    out = []
    for w in chain:
        rec = S18.defect_of(tuple(w))
        out.append({"rels": list(w), "total_length": total_len(w),
                    "min_relator_length": min_rel(w), "rank": rec["rank"],
                    "defect": rec.get("defect"), "gamma_N": rec.get("gamma_N"),
                    "verdict": rec.get("verdict"), "method": rec.get("method")})
    return out


def band_flags(nodes_rec, start_rec):
    tl = [n["total_length"] for n in nodes_rec]
    mr = [n["min_relator_length"] for n in nodes_rec]
    return {
        "inband_total_length": min(tl) >= BAND_TOTAL,
        "inband_min_relator": min(mr) >= BAND_MINREL,
        "no_escape": (min(tl) >= start_rec["total_length"]
                      and min(mr) >= start_rec["min_relator_length"]),
        "chain_min_total_length": min(tl),
        "chain_min_relator_length": min(mr),
    }


def cmd_hunt(args):
    launch_path = os.path.join(OUT_DIR, f"s24_launch_{args.family}.jsonl")
    states = []
    with open(launch_path, encoding="utf-8") as fh:
        for line in fh:
            states.append(json.loads(line))
    rng0 = random.Random(args.seed)
    rng0.shuffle(states)
    states = states[:args.states]
    out_path = os.path.join(REPO_ROOT, args.out)
    t0 = time.time()
    n_hit = 0
    print(f"[s24] {args.family}: {len(states)} launch states x {args.trials} trials, "
          f"nodes={args.nodes}", flush=True)
    for si, s in enumerate(states):
        start = tuple(s["words"])
        start_rec = {"total_length": total_len(start), "min_relator_length": min_rel(start),
                     "rank": s["rank"], "provenance": s.get("provenance"),
                     "persisted_defect": s.get("minimum_defect")}
        for t in range(args.trials):
            if time.time() - t0 > args.wall:
                print(f"[s24] wall budget {args.wall}s reached at state {si} trial {t}",
                      flush=True)
                return
            rng = random.Random(args.seed + 7919 * t + 104729 * si)
            st, d, stats, parent = hunt_ac2(
                start, args.nodes, rng, beam=args.beam, branch=args.branch,
                rel_headroom=args.rel_headroom, tot_headroom=args.tot_headroom,
                census_cap=args.census_cap, solver_budget=args.solver_budget)
            row = {"record": "s24_trial", "family": args.family, "state_index": si,
                   "trial": t, "seed": args.seed, "nodes_budget": args.nodes,
                   "start": list(start), "start_rec": start_rec,
                   "hit": st is not None, "stats": stats,
                   "pops_reached_budget": stats["pops"] >= args.nodes,
                   "elapsed_s": round(time.time() - t0, 1)}
            if st is not None:
                chain = chain_of(st, parent)
                rec = chain_record(chain)
                row["hit_state"] = list(st)
                row["hit_method"] = d.get("method")
                row["chain"] = rec
                row["chain_len"] = len(rec)
                row["bands"] = band_flags(rec, start_rec)
                n_hit += 1
                print(f"[s24] *** HIT state {si} trial {t}: {st}  bands={row['bands']}",
                      flush=True)
            _append_jsonl(out_path, row)
            print(f"[s24]   s{si:3d} t{t} hit={st is not None} pops={stats['pops']} "
                  f"dec={stats['decided']} und={stats['undecided']} "
                  f"prej={stats['planar_rejects']} ppass={stats['planar_pass']} "
                  f"gen={stats['generated']} rst={stats['restarts']} "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    print(f"[s24] {args.family} done: {n_hit} hits, {time.time()-t0:.0f}s", flush=True)


# ------------------------------------------------------------------ table

def cmd_table(args):
    rows = []
    for p in args.inputs:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    fams = {}
    for r in rows:
        f = fams.setdefault(r["family"], {
            "trials": 0, "hits_raw": 0, "hits_inband_total": 0, "hits_inband_minrel": 0,
            "hits_no_escape": 0, "pops": 0, "decided": 0, "undecided": 0,
            "planar_rejects": 0, "planar_pass": 0, "generated": 0, "restarts": 0,
            "solver_calls": 0, "decided_by_solver": 0, "undecided_solver_budget": 0,
            "trials_reached_budget": 0, "distinct_states": set(), "hit_rows": []})
        f["trials"] += 1
        s = r["stats"]
        for k in ("pops", "decided", "undecided", "planar_rejects", "planar_pass",
                  "generated", "restarts", "solver_calls", "decided_by_solver",
                  "undecided_solver_budget"):
            f[k] += s.get(k, 0)
        f["trials_reached_budget"] += bool(r.get("pops_reached_budget"))
        f["distinct_states"].add(tuple(r["start"]))
        if r["hit"]:
            f["hits_raw"] += 1
            b = r.get("bands", {})
            f["hits_inband_total"] += bool(b.get("inband_total_length"))
            f["hits_inband_minrel"] += bool(b.get("inband_min_relator"))
            f["hits_no_escape"] += bool(b.get("no_escape"))
            f["hit_rows"].append({"state_index": r["state_index"], "trial": r["trial"],
                                 "hit_state": r.get("hit_state"), "bands": b,
                                  "chain": r.get("chain")})
    for f in fams.values():
        f["distinct_states"] = len(f["distinct_states"])
    out = {"record": "s24_table", "inputs": args.inputs, "families": fams}
    p = os.path.join(REPO_ROOT, args.out)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    for name, f in fams.items():
        print(f"[s24] {name:9s} trials={f['trials']} states={f['distinct_states']} "
              f"pops={f['pops']} decided={f['decided']} und={f['undecided']} "
              f"prej={f['planar_rejects']} ppass={f['planar_pass']} "
              f"budget_reached={f['trials_reached_budget']}/{f['trials']}", flush=True)
        print(f"[s24] {name:9s} HITS raw={f['hits_raw']} "
              f"inband_total>=13={f['hits_inband_total']} "
              f"inband_minrel>=6={f['hits_inband_minrel']} "
              f"no_escape={f['hits_no_escape']}", flush=True)
    print(f"[s24] wrote {p}", flush=True)


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("launch")
    a.add_argument("--verify", type=int, default=20)
    a.add_argument("--seed", type=int, default=20260804)
    a.set_defaults(func=cmd_launch)

    b = sub.add_parser("hunt")
    b.add_argument("--family", default="ak3", choices=sorted(POOLS))
    b.add_argument("--states", type=int, default=8)
    b.add_argument("--trials", type=int, default=2)
    b.add_argument("--nodes", type=int, default=250)
    b.add_argument("--beam", type=int, default=6)
    b.add_argument("--branch", type=int, default=8)
    b.add_argument("--rel-headroom", type=int, default=4)
    b.add_argument("--tot-headroom", type=int, default=8)
    b.add_argument("--census-cap", type=int, default=200_000)
    b.add_argument("--solver-budget", type=int, default=12,
                   help="max cut-scheme-solver calls per trial (planar survivors whose "
                        "exact census does not fit under the cap)")
    b.add_argument("--wall", type=float, default=600.0)
    b.add_argument("--seed", type=int, default=20260804)
    b.add_argument("--out", default="results/stable_ac/fable/s24_ak3.jsonl")
    b.set_defaults(func=cmd_hunt)

    c = sub.add_parser("table")
    c.add_argument("inputs", nargs="+")
    c.add_argument("--out", default="results/stable_ac/fable/s24_table.json")
    c.set_defaults(func=cmd_table)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
