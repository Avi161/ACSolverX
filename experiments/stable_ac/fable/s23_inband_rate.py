"""S23 -- is the IN-BAND certificate creation rate ever nonzero, and does extra rank help?

NEW FILE.  Nothing under ``experiments/`` or ``ac_solver/`` is modified.  Three existing
modules are imported READ-ONLY:

* ``s12_hunt``          -- the move family, ``decide``, and ``load_ladder`` (MS source);
* ``s21_audit_gen_replay`` -- ``hunt_tracked`` (parent-tracking clone of ``s12_hunt.hunt``,
  identical RNG call order) and ``ac_step`` (the fresh-AC-walk control generator);
* ``s18_s5_chain_audit`` -- ``defect_of`` (exact census, else the R1c-v2 verdict) and the
  two core reductions ``_elim_once`` / ``_tietze_kill_unit``.

WHY THIS FILE EXISTS.  Trap T-S20
(``experiments/lessons/control-escapes-through-a-region-the-target-cannot-enter.md``):
every control hit measured so far was obtained by walking DOWN in total length, from a
start of 13 to witnesses at length 3-11, i.e. into the Havas-Ramsay region that AK(3)
provably cannot enter without settling the open problem outright.  Endpoint-only counting
hid that for three iterations.  So this file counts hits only when the WHOLE CHAIN stays in
band, under two definitions:

  weak    : every state on the chain has total length >= 13 (AK(3)'s length);
  strong  : weak, AND the witness does not reduce to a short core -- total length is
            inflatable by inert AC4 discs, so a long witness can be a short core in
            costume.  Two core reductions, both from ``S18_S5_RECHECK.md``:
              ``elim``   delete every generator occurring EXACTLY ONCE
                         (AC3 + one ambient automorphism + AC5; stable-AC legal at rank 2,
                         [ASSERTED] at rank > 2 -- FRAMING.md trap 2);
              ``tietze`` delete every relator that is a bare generator and strike that
                         generator everywhere (group-legal, NOT an AC move: a structural
                         description only, hence the strictest reading).

UNITS.  ``defect`` is the UNHALVED Neuwirth defect; ``gamma_N = defect // 2``
(``experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md``).  AK(3) has
``minimum_defect`` 4, i.e. ``gamma_N = 2``.

BOUND DIRECTION.  Every hunt here is a ONE-SIDED, upper-bound-only instrument: a hit
certifies ``gamma_N = 0`` for that state (so bounds ``gamma_N`` from ABOVE), and a null
bounds NOTHING from below (``experiments/lessons/parallel-runs-and-bound-direction.md``).

RANK CEILING.  ``kstab`` fresh generators are adjoined as bare relators, so the rank
ceiling is ``2 + kstab``; the move family never introduces a letter, so no state can exceed
it.  The actual rank of each chain node is recorded separately (letters present), because a
slide can overwrite a bare stabilizer and drop the rank back.

PERSISTENCE.  ``hunt`` appends and flushes ONE JSONL row per (ceiling, trial) as it goes:
an interrupted run still leaves every completed trial on disk.  (``s12_hunt`` writes its
JSON only after the final depth; two runs died that way on 2026-08-04.)

Sub-commands
------------
    controls : build + exact-census-verify defect-4 rank-2 length-13 AC-trivial controls
               from two unrelated sources (solved Miller-Schupp ladder; fresh AC walks
               from the standard presentation)
    hunt     : run one root over rank ceilings 2..5, recording the FULL chain of each hit
    table    : aggregate the JSONL rows into the rank x in-band table
"""

from __future__ import annotations

import argparse
import glob as _glob
import json
import os
import random
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import s12_hunt as H              # noqa: E402
from experiments.stable_ac.fable import s21_audit_gen_replay as G   # noqa: E402
from experiments.stable_ac.fable import s18_s5_chain_audit as S18   # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")
BAND = 13                     # AK(3)'s total length; the Havas-Ramsay floor
AK3 = ("xyxYXY", "xxxYYYY")


# ------------------------------------------------------------------ helpers

def gens_of(words):
    return tuple(sorted(set("".join(words).lower())))


def total_len(words):
    return sum(len(w) for w in words)


def cores_of(words):
    """(elim core, tietze core) of a presentation, as (rank, length, rels)."""
    g = gens_of(words)
    eg, er, el = S18._elim_once(g, tuple(words))
    tg, tr, tl = S18._tietze_kill_unit(g, tuple(words))
    return ({"rank": len(eg), "length": el, "rels": list(er)},
            {"rank": len(tg), "length": tl, "rels": list(tr)})


def node_record(words):
    """Full description of one chain node: length, rank, defect, both core lengths."""
    words = tuple(w for w in words if w)
    rec = S18.defect_of(words)
    e, t = cores_of(words)
    return {"rels": list(words), "total_length": rec["total_length"],
            "rank": rec["rank"], "defect": rec.get("defect"),
            "gamma_N": rec.get("gamma_N"), "verdict": rec.get("verdict"),
            "method": rec["method"],
            "elim_core_length": e["length"], "elim_core_rank": e["rank"],
            "elim_core": e["rels"],
            "tietze_core_length": t["length"], "tietze_core_rank": t["rank"],
            "tietze_core": t["rels"]}


def _write(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, default=str)
    print(f"[s23] wrote {path}", flush=True)


def _hist(it):
    out = {}
    for v in it:
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items()))


# ------------------------------------------------------------------ controls

def cmd_controls(args):
    """Build controls matched to AK(3) on rank (2), total length (13) and
    ``minimum_defect`` (4, i.e. gamma_N = 2), from two unrelated sources.

    Every root is verified NOT_SPHERICAL at defect 4 by EXACT census before use; a root
    whose census does not fit under the cap is rejected rather than accepted on a solver
    verdict, because the whole experiment is keyed to the exact defect.
    """
    t0 = time.time()
    rows, seen_rel = [], set()

    # ---- source A: solved Miller-Schupp ladder (AC-trivial: solved in ms640_solved.txt)
    ms = H.load_ladder(600, random.Random(args.seed), lo=BAND, hi=BAND)
    print(f"[controls] MS ladder length-{BAND} candidates: {len(ms)}", flush=True)
    for w in ms:
        if time.time() - t0 > args.time_budget:
            break
        rec = S18.defect_of(w)
        if rec.get("method") != "exact_census" or rec.get("defect") != args.defect:
            continue
        keys = {H.canon((r,))[0] for r in w}
        if keys & seen_rel:
            continue
        seen_rel |= keys
        rows.append({"label": f"msA{len([r for r in rows if r['source']=='ms'])}",
                     "source": "ms", "words": list(w), "defect": rec["defect"],
                     "gamma_N": rec["gamma_N"], "total_length": rec["total_length"],
                     "rank": rec["rank"], "census_enumerated": rec.get("enumerated"),
                     "verdict": rec["verdict"], "method": rec["method"],
                     "ac_trivial_evidence": "member of data/ms640_solved.txt "
                                            "(solved Miller-Schupp instance)"})
        print(f"[controls] MS  {w} defect={rec['defect']}", flush=True)
        if sum(1 for r in rows if r["source"] == "ms") >= args.want_ms:
            break

    # ---- source B: fresh AC walks from the standard presentation <x,y | x,y>
    rng = random.Random(args.seed + 1)
    keys_seen = set()
    walks_done = 0
    while (sum(1 for r in rows if r["source"] == "walk") < args.want_walk
           and time.time() - t0 < args.time_budget and walks_done < args.walks):
        walks_done += 1
        words = ("x", "y")
        chain = [words]
        for _ in range(args.steps):
            nxt, _d = G.ac_step(words, rng, args.max_rel)
            if nxt is None:
                continue
            words = nxt
            chain.append(words)
            if total_len(words) != BAND:
                continue
            k = H.canon(words)
            if k in keys_seen:
                continue
            keys_seen.add(k)
            rec = S18.defect_of(words)
            if rec.get("method") != "exact_census" or rec.get("defect") != args.defect:
                continue
            kk = {H.canon((r,))[0] for r in words}
            if kk & seen_rel:
                continue
            seen_rel |= kk
            rows.append({"label": f"walkB{sum(1 for r in rows if r['source']=='walk')}",
                         "source": "walk", "words": list(words),
                         "defect": rec["defect"], "gamma_N": rec["gamma_N"],
                         "total_length": rec["total_length"], "rank": rec["rank"],
                         "census_enumerated": rec.get("enumerated"),
                         "verdict": rec["verdict"], "method": rec["method"],
                         "ac_trivial_evidence": "explicit AC walk from <x,y|x,y>",
                         "walk_chain": [list(c) for c in chain]})
            print(f"[controls] WALK {words} defect={rec['defect']} "
                  f"steps={len(chain)-1}", flush=True)
            break

    tgt = S18.defect_of(AK3)
    payload = {"record": "s23_controls", "args": vars(args),
               "target": {"label": "ak3", "source": "target", "words": list(AK3),
                          "defect": tgt.get("defect"), "gamma_N": tgt.get("gamma_N"),
                          "total_length": tgt["total_length"], "rank": tgt["rank"],
                          "census_enumerated": tgt.get("enumerated"),
                          "verdict": tgt.get("verdict"), "method": tgt["method"]},
               "controls": rows, "walks_done": walks_done,
               "elapsed_s": round(time.time() - t0, 1)}
    _write(args.out, payload)
    print(f"[controls] {len(rows)} controls "
          f"({sum(1 for r in rows if r['source']=='ms')} ms / "
          f"{sum(1 for r in rows if r['source']=='walk')} walk) in "
          f"{payload['elapsed_s']}s", flush=True)
    return payload


# ------------------------------------------------------------------ hunt

def cmd_hunt(args):
    """One root, rank ceilings ``2 + kstab``, ``trials`` seeds each; FULL chain per hit.

    Rows are appended and flushed one at a time.
    """
    base = tuple(args.root.split(","))
    ceilings = [int(c) for c in args.ceilings.split(",")]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    root_rec = S18.defect_of(base)
    hdr = {"kind": "header", "label": args.label, "source": args.source,
           "root": list(base), "root_defect": root_rec.get("defect"),
           "root_gamma_N": root_rec.get("gamma_N"),
           "root_verdict": root_rec.get("verdict"),
           "root_method": root_rec["method"], "root_length": root_rec["total_length"],
           "ceilings": ceilings, "trials": args.trials, "nodes": args.nodes,
           "seed": args.seed, "headroom": args.headroom,
           "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(hdr) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    print(f"[hunt] {args.label} root={base} defect={root_rec.get('defect')} "
          f"({root_rec['method']})", flush=True)

    t0 = time.time()
    for ceiling in ceilings:
        kstab = ceiling - root_rec["rank"]
        for trial in range(args.trials):
            if args.time_budget and time.time() - t0 > args.time_budget:
                print("[hunt] time budget reached; stopping", flush=True)
                return
            seed = args.seed + 7919 * trial + 104729 * kstab
            rng = random.Random(seed)
            ts = time.time()
            st, d, stats, parent = G.hunt_tracked(
                base, kstab, args.nodes, rng, headroom=args.headroom,
                census_cap=args.census_cap)
            row = {"kind": "run", "label": args.label, "source": args.source,
                   "rank_ceiling": ceiling, "kstab": kstab, "trial": trial,
                   "seed": seed, "nodes_budget": args.nodes, "hit": st is not None,
                   "stats": stats, "wall_s": round(time.time() - ts, 1)}
            if st is not None:
                chain = []
                node = st
                while node is not None:
                    chain.append(node)
                    node = parent.get(node)
                chain.reverse()
                nodes = [node_record(w) for w in chain]
                row["chain"] = nodes
                row["chain_len"] = len(nodes)
                row["chain_lengths"] = [n["total_length"] for n in nodes]
                row["chain_ranks"] = [n["rank"] for n in nodes]
                row["chain_defects"] = [n["defect"] for n in nodes]
                row["chain_elim_core_lengths"] = [n["elim_core_length"] for n in nodes]
                row["chain_tietze_core_lengths"] = [n["tietze_core_length"]
                                                    for n in nodes]
                row["created"] = (nodes[0]["defect"] not in (0, None)
                                  and nodes[-1]["defect"] == 0)
                row["min_chain_length"] = min(n["total_length"] for n in nodes)
                row["max_chain_rank"] = max(n["rank"] for n in nodes)
                row["witness"] = nodes[-1]["rels"]
                row["witness_length"] = nodes[-1]["total_length"]
                row["witness_rank"] = nodes[-1]["rank"]
                row["witness_elim_core_length"] = nodes[-1]["elim_core_length"]
                row["witness_tietze_core_length"] = nodes[-1]["tietze_core_length"]
                # --- the two in-band definitions
                row["weak_in_band"] = row["min_chain_length"] >= BAND
                row["strong_in_band_elim"] = (row["weak_in_band"]
                                              and nodes[-1]["elim_core_length"] >= BAND)
                row["strong_in_band_tietze"] = (row["weak_in_band"]
                                                and nodes[-1]["tietze_core_length"] >= BAND)
                # strictest: no node anywhere on the chain has a short core
                row["strong_in_band_elim_chainwide"] = (
                    row["weak_in_band"]
                    and min(n["elim_core_length"] for n in nodes) >= BAND)
                row["strong_in_band_tietze_chainwide"] = (
                    row["weak_in_band"]
                    and min(n["tietze_core_length"] for n in nodes) >= BAND)
                print(f"[hunt] {args.label} ceil={ceiling} t={trial} HIT "
                      f"lens={row['chain_lengths']} ranks={row['chain_ranks']} "
                      f"defects={row['chain_defects']} weak={row['weak_in_band']} "
                      f"strongE={row['strong_in_band_elim']} "
                      f"strongT={row['strong_in_band_tietze']}", flush=True)
            else:
                print(f"[hunt] {args.label} ceil={ceiling} t={trial} miss "
                      f"pops={stats['pops']}/{args.nodes} dec={stats['decided']} "
                      f"und={stats['undecided']} {row['wall_s']}s", flush=True)
            with open(args.out, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, default=str) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
    print(f"[hunt] {args.label} done in {round(time.time()-t0,1)}s", flush=True)


# ------------------------------------------------------------------ table

DEFS = ["raw", "weak_in_band", "strong_in_band_elim", "strong_in_band_tietze",
        "strong_in_band_elim_chainwide", "strong_in_band_tietze_chainwide"]


def cmd_table(args):
    files = sorted(_glob.glob(args.rows))
    runs, headers = [], {}
    for p in files:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r.get("kind") == "header":
                    headers[r["label"]] = r
                elif r.get("kind") == "run":
                    r["_file"] = os.path.basename(p)
                    runs.append(r)
    if not runs:
        print("[table] no rows found", flush=True)
        return

    def agg(sel):
        out = {}
        for r in sel:
            c = r["rank_ceiling"]
            b = out.setdefault(c, {k: 0 for k in DEFS})
            b["trials"] = b.get("trials", 0) + 1
            if r["hit"]:
                b["raw"] += 1
                for k in DEFS[1:]:
                    b[k] += 1 if r.get(k) else 0
                if not r.get("created", True):
                    b["inherited"] = b.get("inherited", 0) + 1
        return {str(k): out[k] for k in sorted(out)}

    labels = sorted({r["label"] for r in runs})
    per_label = {lab: agg([r for r in runs if r["label"] == lab]) for lab in labels}
    controls = [r for r in runs if r["source"] != "target"]
    target = [r for r in runs if r["source"] == "target"]
    payload = {"record": "s23_table", "files": [os.path.basename(f) for f in files],
               "headers": headers, "n_runs": len(runs),
               "pooled_controls": agg(controls), "target": agg(target),
               "by_source": {s: agg([r for r in runs if r["source"] == s])
                             for s in sorted({r["source"] for r in runs})},
               "per_label": per_label,
               "hit_witness_length_hist": _hist(
                   r["witness_length"] for r in runs if r["hit"]),
               "hit_min_chain_length_hist": _hist(
                   r["min_chain_length"] for r in runs if r["hit"]),
               "hit_witness_elim_core_length_hist": _hist(
                   r["witness_elim_core_length"] for r in runs if r["hit"]),
               "hit_witness_tietze_core_length_hist": _hist(
                   r["witness_tietze_core_length"] for r in runs if r["hit"]),
               "starved_runs(pops<budget and no hit)": sum(
                   1 for r in runs if not r["hit"]
                   and r["stats"]["pops"] < r["nodes_budget"]),
               }
    print(json.dumps({k: payload[k] for k in
                      ("n_runs", "pooled_controls", "target", "by_source",
                       "hit_witness_length_hist", "hit_min_chain_length_hist",
                       "hit_witness_elim_core_length_hist",
                       "hit_witness_tietze_core_length_hist",
                       "starved_runs(pops<budget and no hit)")},
                     indent=1), flush=True)
    print("\nper label:", flush=True)
    for lab in labels:
        print(f"  {lab}: {json.dumps(per_label[lab])}", flush=True)
    _write(args.out, payload)
    return payload


# ------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("controls")
    p.add_argument("--out", default=os.path.join(OUT_DIR, "s23_controls.json"))
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--defect", type=int, default=4)
    p.add_argument("--want-ms", type=int, default=3)
    p.add_argument("--want-walk", type=int, default=3)
    p.add_argument("--walks", type=int, default=4000)
    p.add_argument("--steps", type=int, default=400)
    p.add_argument("--max-rel", type=int, default=9)
    p.add_argument("--time-budget", type=float, default=420.0)
    p.set_defaults(func=cmd_controls)

    p = sub.add_parser("hunt")
    p.add_argument("--root", required=True, help="comma-separated relators")
    p.add_argument("--label", required=True)
    p.add_argument("--source", default="control")
    p.add_argument("--ceilings", default="2,3,4,5")
    p.add_argument("--trials", type=int, default=4)
    p.add_argument("--nodes", type=int, default=500)
    p.add_argument("--seed", type=int, default=20260804)
    p.add_argument("--headroom", type=int, default=4)
    p.add_argument("--census-cap", type=int, default=200_000)
    p.add_argument("--time-budget", type=float, default=0.0)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_hunt)

    p = sub.add_parser("table")
    p.add_argument("--rows", default=os.path.join(OUT_DIR, "s23_rows_*.jsonl"))
    p.add_argument("--out", default=os.path.join(OUT_DIR, "s23_table.json"))
    p.set_defaults(func=cmd_table)

    args = ap.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
