"""S18 -- adversarial re-audit of S5's depth ladder under trap T-S19.

NEW FILE.  Modifies nothing.  It only *reads* `rank_n_ac_search` and re-runs its own
ladder-D control runs with a parent-tracking wrapper around ``sample_moves`` so that
every hit's chain (root -> ... -> witness) can be replayed and its defect logged at
each node -- exactly the test that retracted the cubic control in S16.

Sub-commands
------------
roots   : exact/decided gamma_N of the ladder-D roots (both families, k = 0..4)
chains  : replay the 40 ladder-D CONTROL runs, reconstruct each hit's chain, log the
          defect and the total length at every node of every chain
scan4   : hunt for an AC-trivial rank-2 length-13 presentation with minimum_defect 4
          (a control matched to AK(3) on the quantity being measured, not just length)

Units: ``defect`` is the UNHALVED Neuwirth defect; ``gamma_N = defect // 2``
(``experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md``).
Every number this file prints is a MEASUREMENT at a bounded budget; a null bounds
nothing from below (``experiments/lessons/parallel-runs-and-bound-direction.md``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import rank_n_ac_search as R          # noqa: E402
from experiments.stable_ac.fable import s12_hunt                        # noqa: E402
from experiments.stable_ac.fable.neuwirth_rank_n import (               # noqa: E402
    build_link_n, census_size, gamma_N_factorial_n,
)

OUT_DIR = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")
CENSUS_CAP = 200_000


# ----------------------------------------------------------------------------------
# exact / decided defect
# ----------------------------------------------------------------------------------

def defect_of(rels, gens=None) -> dict:
    """Exact minimum_defect when the census fits, else the R1c-v2 verdict."""
    words = tuple(w for w in rels if w)
    if gens is None:
        gens = tuple(sorted(set("".join(words).lower())))
    out = {"words": list(words), "gens": list(gens),
           "total_length": sum(len(w) for w in words), "rank": len(gens)}
    try:
        size = census_size(build_link_n(words, gens), gens)
    except Exception as exc:                                   # pragma: no cover
        out["census_size"] = None
        out["method"] = f"link_exc:{type(exc).__name__}"
        size = None
    else:
        out["census_size"] = size
    if size is not None and size <= CENSUS_CAP:
        c = gamma_N_factorial_n(words, gens, cap_rotations=CENSUS_CAP,
                                keep_accepting=False)
        if c["status"] == "OK" and c["minimum_defect"] is not None:
            out["defect"] = c["minimum_defect"]
            out["gamma_N"] = c["minimum_defect"] // 2
            out["method"] = "exact_census"
            out["enumerated"] = c.get("enumerated_cases")
            out["verdict"] = "SPHERICAL" if c["minimum_defect"] == 0 else "NOT_SPHERICAL"
            return out
    d = s12_hunt.decide(words, 400_000)
    out["verdict"] = d.get("verdict")
    out["method"] = "decide:" + str(d.get("method"))
    out["defect"] = d.get("defect")
    if out["defect"] is not None:
        out["gamma_N"] = out["defect"] // 2
    elif out["verdict"] == "SPHERICAL":
        out["defect"], out["gamma_N"] = 0, 0
    return out


# ----------------------------------------------------------------------------------
# roots
# ----------------------------------------------------------------------------------

def cmd_roots(args) -> dict:
    fams = {"ak3": R.make(*R.AK3),
            "ak2ctl": R.make(("x", "y"), R.DEPTH_LADDER_CONTROL)}
    rows = []
    for name, base in fams.items():
        for k in range(5):
            st = R.stabilize_k(base, k)
            rec = defect_of(st.rels, st.gens)
            rec.update({"family": name, "depth_k": k})
            rows.append(rec)
            print(f"[roots] {name} k={k} rels={st.rels} len={rec['total_length']} "
                  f"verdict={rec.get('verdict')} defect={rec.get('defect')} "
                  f"gamma_N={rec.get('gamma_N')} method={rec['method']}", flush=True)
    payload = {"record": "s18_roots", "rows": rows}
    _write(args.out, payload)
    return payload


# ----------------------------------------------------------------------------------
# chain replay
# ----------------------------------------------------------------------------------

def _sig(pres) -> tuple:
    return (tuple(pres.gens), tuple(pres.rels))


class ParentTracker:
    """Wraps ``rank_n_ac_search.sample_moves`` and records first-seen parent edges.

    The wrapper forwards *every* argument to the original and touches the RNG in no
    other way, so the replayed run is bit-identical to the recorded one (verified
    against the persisted rows).
    """

    def __init__(self):
        self.orig = R.sample_moves
        self.edges: dict = {}

    def __enter__(self):
        tracker = self

        def wrapper(pres, count, rng, limits=R.Limits(), weights=None,
                    oversample: int = 12):
            got = tracker.orig(pres, count, rng, limits, weights=weights,
                               oversample=oversample)
            psig = _sig(pres)
            for move, child in got:
                for cand in (child, R.cyclically_reduce_pres(child)):
                    if cand is None:
                        continue
                    csig = _sig(cand)
                    if csig != psig and csig not in tracker.edges:
                        tracker.edges[csig] = (psig, list(move))
            return got

        R.sample_moves = wrapper
        return self

    def __exit__(self, *exc):
        R.sample_moves = self.orig
        return False

    def chain(self, leaf_sig, root_sig, max_steps: int = 400):
        """Walk back from ``leaf_sig``; returns (chain, ok) with chain[0] the earliest."""
        out = [leaf_sig]
        moves = []
        cur = leaf_sig
        for _ in range(max_steps):
            if cur == root_sig:
                return list(reversed(out)), list(reversed(moves)), True
            edge = self.edges.get(cur)
            if edge is None:
                return list(reversed(out)), list(reversed(moves)), False
            cur, mv = edge
            out.append(cur)
            moves.append(mv)
        return list(reversed(out)), list(reversed(moves)), False


def cmd_chains(args) -> dict:
    seed = 20260804
    control = (tuple(args.control.split(","))
               if getattr(args, "control", None) else R.DEPTH_LADDER_CONTROL)
    base = R.make(("x", "y"), control)
    recorded = {}
    src = os.path.join(OUT_DIR, "rank_n_ac_search_depth_ladder_rows.jsonl")
    if control == R.DEPTH_LADDER_CONTROL:
        with open(src, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                recorded[row["label"]] = row

    rows = []
    t0 = time.time()
    for k in range(5):
        state = R.stabilize_k(base, k)
        root_sig = _sig(state)
        for rep in range(args.reps):
            label = f"depth_ak2ctl_k{k}_r{rep}"
            run_seed = seed + 1009 * k + 7919 * rep
            limits = R.Limits(max_relator_length=12,
                              max_total_length=max(40, state.total_length + 6),
                              min_rank=2, max_rank=2 + k)
            with ParentTracker() as tracker:
                res = R.search(state, nodes=args.nodes, beam=6, branch=12, evals=800,
                               seed=run_seed, limits=limits, time_budget=40.0,
                               label=label, scheme=f"ladder_D:rank_ceiling(k={k})",
                               base_gens=base.gens, verbose=False)
                chain_sigs, chain_moves, ok = ([], [], False)
                if res.hit:
                    leaf = R.make(res.best_state["gens"], res.best_state["rels"])
                    chain_sigs, chain_moves, ok = tracker.chain(_sig(leaf), root_sig)
            ref = recorded.get(label)
            faithful = None if ref is None else (
                ref.get("hit") == res.hit
                and ref.get("nodes_used") == res.nodes_used
                and ref.get("best_state") == res.best_state)
            nodes = []
            for sig in chain_sigs:
                rec = defect_of(sig[1], sig[0])
                nodes.append({"rels": list(sig[1]), "gens": list(sig[0]),
                              "total_length": rec["total_length"],
                              "rank": rec["rank"], "defect": rec.get("defect"),
                              "gamma_N": rec.get("gamma_N"),
                              "verdict": rec.get("verdict"),
                              "method": rec["method"]})
            row = {
                "label": label, "depth_k": k, "rep": rep, "seed": run_seed,
                "hit": res.hit, "nodes_used": res.nodes_used,
                "generations": res.generations,
                "replay_faithful": faithful,
                "best_state": res.best_state,
                "best_rank": res.best_rank,
                "best_total_length": res.best_total_length,
                "chain_reconstructed": ok,
                "chain_len": len(nodes),
                "chain_moves": chain_moves,
                "chain": nodes,
                "chain_defects": [n["defect"] for n in nodes],
                "chain_lengths": [n["total_length"] for n in nodes],
                "chain_ranks": [n["rank"] for n in nodes],
            }
            if nodes:
                row["root_defect"] = nodes[0]["defect"]
                row["leaf_defect"] = nodes[-1]["defect"]
                row["created"] = (nodes[0]["defect"] not in (0, None)
                                  and nodes[-1]["defect"] == 0)
                row["min_chain_length"] = min(n["total_length"] for n in nodes)
                row["max_chain_rank"] = max(n["rank"] for n in nodes)
                row["in_band"] = row["min_chain_length"] >= 13
            rows.append(row)
            print(f"[chain] {label} hit={res.hit} faithful={faithful} "
                  f"chain={len(nodes)} defects={row.get('chain_defects')} "
                  f"lens={row.get('chain_lengths')} ranks={row.get('chain_ranks')}",
                  flush=True)

    hits = [r for r in rows if r["hit"]]
    created = [r for r in hits if r.get("created")]
    inherited = [r for r in hits if r.get("chain") and not r.get("created")]
    unreconstructed = [r for r in hits if not r.get("chain_reconstructed")]
    in_band = [r for r in created if r.get("in_band")]
    summary = {
        "runs": len(rows),
        "hits": len(hits),
        "replay_faithful": sum(1 for r in rows if r["replay_faithful"]),
        "chains_reconstructed": sum(1 for r in hits if r["chain_reconstructed"]),
        "chains_not_reconstructed": len(unreconstructed),
        "created": len(created),
        "inherited": len(inherited),
        "created_and_in_band(min chain total_length >= 13)": len(in_band),
        "in_band_rate_over_runs": round(len(in_band) / len(rows), 4) if rows else None,
        "rank_breakdown_all_created": _hist(r["best_rank"] for r in created),
        "rank_breakdown_created_in_band": _hist(r["best_rank"] for r in in_band),
        "max_chain_rank_created_in_band": _hist(r["max_chain_rank"] for r in in_band),
        "witness_length_hist_created": _hist(r["best_total_length"] for r in created),
        "min_chain_length_hist_created": _hist(r["min_chain_length"] for r in created),
        "distinct_chain_defect_sequences": _hist(
            tuple(r["chain_defects"]) for r in hits),
        "elapsed_s": round(time.time() - t0, 1),
    }
    print(json.dumps(summary, indent=1, default=str), flush=True)
    payload = {"record": "s18_chains", "summary": summary, "rows": rows}
    _write(args.out, payload)
    return payload


def _hist(it) -> dict:
    out: dict = {}
    for v in it:
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items()))


# ----------------------------------------------------------------------------------
# defect-4 control scan
# ----------------------------------------------------------------------------------

def cmd_scan4(args) -> dict:
    src = os.path.join(OUT_DIR, "ak2_members.jsonl")
    cands = []
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("verdict") != "NOT_SPHERICAL":
                continue
            if row.get("total_length") != args.length:
                continue
            cands.append(tuple(row["canonical"]))
    print(f"[scan4] {len(cands)} NOT_SPHERICAL AK(2)-class members of length "
          f"{args.length}", flush=True)
    found, rows = [], []
    t0 = time.time()
    for words in cands[: args.limit]:
        if time.time() - t0 > args.time_budget:
            print("[scan4] time budget reached", flush=True)
            break
        rec = defect_of(words)
        rows.append(rec)
        if rec.get("defect") == 4:
            found.append(rec)
            print(f"[scan4] DEFECT 4: {words}", flush=True)
    payload = {"record": "s18_scan4", "scanned": len(rows),
               "defect_hist": _hist(r.get("defect") for r in rows),
               "found_defect4": found, "elapsed_s": round(time.time() - t0, 1)}
    print(json.dumps(payload["defect_hist"], indent=1), flush=True)
    print(f"[scan4] scanned {len(rows)}, defect-4 found {len(found)}", flush=True)
    _write(args.out, payload)
    return payload


# ----------------------------------------------------------------------------------
# what is the certificate actually made of?
# ----------------------------------------------------------------------------------

def _elim_once(gens, rels):
    """Tietze-eliminate every generator that occurs EXACTLY ONCE in the whole thing.

    If ``g`` occurs once, in ``r_i = u g^e v`` and nowhere else, then an AC3
    conjugation makes ``r_i = g^e (vu)`` and the free-group automorphism
    ``g -> g (vu)^{-e}`` (which fixes every other relator, because ``g`` does not
    occur in them) makes it the bare letter ``g``; AC5 then removes it.  So the core is
    reachable by AC3 + one ambient automorphism + AC5.  The automorphism step leans on
    the STABLE ambient automorphism principle, which ``FRAMING.md`` trap 2 records as
    proved at rank 2 only -- so this reduction is flagged [ASSERTED at rank > 2], and
    the weaker verbatim-containment statement below needs no such assumption.
    """
    gens, rels = list(gens), list(rels)
    changed = True
    while changed:
        changed = False
        for g in list(gens):
            tot = sum(r.lower().count(g) for r in rels)
            if tot != 1:
                continue
            idx = [i for i, r in enumerate(rels) if g in r.lower()][0]
            rels.pop(idx)
            gens.remove(g)
            changed = True
            break
    return tuple(gens), tuple(rels), sum(len(r) for r in rels)


def _tietze_kill_unit(gens, rels):
    """Group-level (NOT necessarily AC-level) deletion of every ``r_i`` that is a bare
    generator: set that generator to 1 and strike it from all relators."""
    gens, rels = list(gens), list(rels)
    changed = True
    while changed:
        changed = False
        for i, r in enumerate(rels):
            if len(r) == 1:
                g = r.lower()
                rels.pop(i)
                gens = [x for x in gens if x != g]
                rels = [R.free_reduce("".join(ch for ch in w if ch.lower() != g))
                        for w in rels]
                if any(w == "" for w in rels):
                    return tuple(gens), tuple(rels), sum(len(w) for w in rels)
                changed = True
                break
    return tuple(gens), tuple(rels), sum(len(w) for w in rels)


def cmd_cores(args) -> dict:
    d = json.load(open(args.chains, encoding="utf-8"))
    rows = [r for r in d["rows"] if r["hit"]]
    base = set("xy")
    out = []
    for r in rows:
        gens = tuple(r["best_state"]["gens"])
        rels = tuple(r["best_state"]["rels"])
        eg, er, el = _elim_once(gens, rels)
        tg, tr, tl = _tietze_kill_unit(gens, rels)
        bo = [w for w in rels if set(w.lower()) <= base]
        rec = {
            "label": r["label"], "depth_k": r["depth_k"],
            "in_band(min chain len >= 13)": r["in_band"],
            "witness": list(rels), "witness_rank": r["best_rank"],
            "witness_length": r["best_total_length"],
            "elim_core_rank": len(eg), "elim_core_length": el,
            "elim_core": list(er),
            "tietze_core_rank": len(tg), "tietze_core_length": tl,
            "tietze_core": list(tr),
            "base_only_relators": bo,
            "base_only_count": len(bo),
            "base_only_length": sum(len(w) for w in bo),
            "carries_sub13_base_pair": len(bo) == 2 and sum(len(w) for w in bo) < 13,
        }
        # defect of the two cores, where affordable
        for tag, (g_, r_) in (("elim", (eg, er)), ("tietze", (tg, tr))):
            if r_ and all(r_):
                rec[tag + "_core_defect"] = defect_of(r_, g_).get("defect")
        out.append(rec)

    inb = [r for r in out if r["in_band(min chain len >= 13)"]]
    summary = {
        "hits": len(out),
        "in_band": len(inb),
        "carries_sub13_base_pair_all": sum(r["carries_sub13_base_pair"] for r in out),
        "carries_sub13_base_pair_in_band": sum(
            r["carries_sub13_base_pair"] for r in inb),
        "elim_core_rank_hist_in_band": _hist(r["elim_core_rank"] for r in inb),
        "elim_core_length_hist_in_band": _hist(r["elim_core_length"] for r in inb),
        "tietze_core_rank_hist_all": _hist(r["tietze_core_rank"] for r in out),
        "tietze_core_length_hist_all": _hist(r["tietze_core_length"] for r in out),
        "tietze_core_length_hist_in_band": _hist(r["tietze_core_length"] for r in inb),
        "in_band_with_tietze_core_length_ge_13": sum(
            1 for r in inb if r["tietze_core_length"] >= 13),
        "all_with_tietze_core_length_ge_13": sum(
            1 for r in out if r["tietze_core_length"] >= 13),
        "in_band_with_elim_core_length_ge_13": sum(
            1 for r in inb if r["elim_core_length"] >= 13),
    }
    print(json.dumps(summary, indent=1), flush=True)
    for r in out:
        if r["in_band(min chain len >= 13)"]:
            print(f"  IN {r['label']:22s} w={r['witness']} rk{r['witness_rank']}"
                  f" L{r['witness_length']} | elim rk{r['elim_core_rank']}"
                  f" L{r['elim_core_length']} {r['elim_core']}"
                  f" | tietze rk{r['tietze_core_rank']} L{r['tietze_core_length']}"
                  f" {r['tietze_core']}", flush=True)
    payload = {"record": "s18_cores", "summary": summary, "rows": out}
    _write(args.out, payload)
    return payload


def _write(path, payload) -> None:
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, default=str)
    print(f"[s18] wrote {path}", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("roots")
    p.add_argument("--out", default=os.path.join(OUT_DIR, "s18_roots.json"))
    p.set_defaults(func=cmd_roots)

    p = sub.add_parser("chains")
    p.add_argument("--out", default=os.path.join(OUT_DIR, "s18_control_chains.json"))
    p.add_argument("--reps", type=int, default=8)
    p.add_argument("--nodes", type=int, default=600)
    p.add_argument("--control", default=None,
                   help="comma-separated rank-2 root; default = S5's ladder-D control")
    p.set_defaults(func=cmd_chains)

    p = sub.add_parser("cores")
    p.add_argument("--chains",
                   default=os.path.join(OUT_DIR, "s18_control_chains.json"))
    p.add_argument("--out", default=os.path.join(OUT_DIR, "s18_witness_cores.json"))
    p.set_defaults(func=cmd_cores)

    p = sub.add_parser("scan4")
    p.add_argument("--out", default=os.path.join(OUT_DIR, "s18_defect4_scan.json"))
    p.add_argument("--length", type=int, default=13)
    p.add_argument("--limit", type=int, default=400)
    p.add_argument("--time-budget", type=float, default=150.0)
    p.set_defaults(func=cmd_scan4)

    args = ap.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
