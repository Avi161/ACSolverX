"""Stall-triggered best-of-many CoV escape (IMPLEMENTATION_IDEAS.md idea 4).

The core mission mechanism: run the greedy until it stalls on a length plateau,
take the incumbent leader pair — the actual state the search is stuck on — fan
out its gated subword-CoV candidates (best-of-many, never one directed z),
rank them mu-first (the orbit-floor refutation: a CoV hop can strictly lower
the Aut-minimal length), and spend the remaining budget searching the top
candidates in their new coordinates.

The search loop is a plain-Python ``heapq`` over the imported ``@njit``
primitives (the sanctioned numba-the-math / Python-the-orchestration split) —
NOT the shipped solver, because the shipped solvers cannot pause at a plateau
or expose the incumbent. Same state model: canonical pair keys, priority =
total length, depth tie-break, budget charged per pop. Pop order is NOT
claimed identical to the shipped solver; the honest control is the shipped
``greedy_search`` at the same total budget and cap, run by the runner.

Certificate: SEGMENTED, never flat — seg1 = Definition-2.1 moves from the
start to the incumbent, junction = the CoV ``(z, iso_gen, iso_index)`` applied
to the incumbent (a stable-AC supermove of unbounded elementary cost), seg2 =
moves from the CoV output to trivial. ``verify_escape_row`` replays both
segments through ``experiments/greedy_tests/spec`` (never this module's own
search) and re-derives the junction with ``cov.apply_cov_once``. A verified
row certifies STABLE AC-triviality of the start (the CoV is a stable move);
it is never a flat 2-generator AC path and is never reported as one.

Budget accounting: pops(base) + sum pops(escape candidates) <= budget. Local
runs: budget <= 1000 (the runner refuses more without ACSOLVERX_ALLOW_BIG=1).

CLI:
    .venv/bin/python3 -m experiments.stable_ac.cov.stall_escape \
        --bench combined_22 --budget 1000 --cap 24
"""

import argparse
import heapq
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.search.greedy_baseline import (
    arr_to_str,
    canonical_pair_nj,
    get_neighbors_with_moves_nj,
    reduce_relator_nj,
    str_to_arr,
)
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.restart_planner import abel_magnitude

HERE = os.path.dirname(os.path.abspath(__file__))


def _canon_key(r1s, r2s):
    c1, c2 = canonical_pair_nj(reduce_relator_nj(str_to_arr(r1s), True),
                               reduce_relator_nj(str_to_arr(r2s), True))
    return (arr_to_str(c1), arr_to_str(c2)), (c1, c2)


def greedy_until(r1s, r2s, budget, cap, plateau_k=None):
    """Best-first search that can stop at a plateau.

    Returns a dict: status 'solved' | 'plateau' | 'budget' | 'exhausted',
    pops, moves (solved: full legacy move list; else None), incumbent (the
    min-total-length POPPED pair as strings), incumbent_moves (legacy moves
    start -> incumbent). A plateau = ``plateau_k`` pops without a new minimum
    popped total length (None disables).
    """
    key, arrs = _canon_key(r1s, r2s)
    pq = [(len(key[0]) + len(key[1]), 0, key)]
    visited = {key: None}
    move_in = {}
    arrays = {key: arrs}
    pops = 0
    best_total, best_key, since_best = 10 ** 9, key, 0
    max_popped = 0        # T9 envelope: the longest total actually POPPED

    def path_to(k):
        mv = []
        while visited[k] is not None:
            mv.append(move_in[k])
            k = visited[k]
        return mv[::-1], k

    while pq and pops < budget:
        _, d, k = heapq.heappop(pq)
        pops += 1
        a1, a2 = arrays[k]
        total = len(a1) + len(a2)
        max_popped = max(max_popped, total)
        if len(a1) == 1 and len(a2) == 1:
            moves, _ = path_to(k)
            return {"status": "solved", "pops": pops, "moves": moves,
                    "incumbent": k, "incumbent_moves": moves,
                    "max_popped_total": max_popped}
        if total < best_total:
            best_total, best_key, since_best = total, k, 0
        else:
            since_best += 1
            if plateau_k is not None and since_best >= plateau_k:
                mv, _ = path_to(best_key)
                return {"status": "plateau", "pops": pops, "moves": None,
                        "incumbent": best_key, "incumbent_moves": mv,
                        "max_popped_total": max_popped}
        for n1, n2, t, js, k1, k2 in get_neighbors_with_moves_nj(a1, a2):
            n1 = reduce_relator_nj(n1, True)
            n2 = reduce_relator_nj(n2, True)
            if len(n1) > cap or len(n2) > cap:
                continue
            c1, c2 = canonical_pair_nj(n1, n2)
            nk = (arr_to_str(c1), arr_to_str(c2))
            if nk in visited:
                continue
            visited[nk] = k
            move_in[nk] = (int(t), int(js), int(k1), int(k2))
            arrays[nk] = (c1, c2)
            heapq.heappush(pq, (len(c1) + len(c2), d + 1, nk))
    mv, _ = path_to(best_key)
    status = "budget" if pq else "exhausted"
    return {"status": status, "pops": pops, "moves": None,
            "incumbent": best_key, "incumbent_moves": mv,
            "max_popped_total": max_popped}


def escape_candidates(r1s, r2s, cap, fanout):
    """Gated subword-CoV candidates of the incumbent, mu-then-abel ranked."""
    res = cov.enumerate_cov(str_to_word(r1s), str_to_word(r2s),
                            default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
                            reject_len=cov.REJECT_LEN)
    seen, out = set(), []
    for c in res:
        o = (word_to_str(c.r1), word_to_str(c.r2))
        if o in seen:
            continue
        seen.add(o)
        out.append((aut_min_len(o), abel_magnitude(c.r1, c.r2), o, c))
    out.sort(key=lambda t: (t[0], t[1], t[2]))
    return out[:fanout]


def stall_escape_search(r1s, r2s, budget, cap, plateau_k=200, fanout=6):
    """Base search -> plateau -> best-of-many CoV escape. One recursion level.

    Total pops across all phases <= budget. Returns the result row (dict).
    """
    base = greedy_until(r1s, r2s, budget, cap, plateau_k=plateau_k)
    row = {"solved": False, "phase": None, "nodes_base": base["pops"],
           "base_status": base["status"], "nodes_total": base["pops"],
           "incumbent": None, "escape": None,
           "max_popped_total": base.get("max_popped_total", 0)}
    if base["status"] == "solved":
        row.update({"solved": True, "phase": "base",
                    "seg1_moves": base["moves"]})
        return row
    if base["status"] == "exhausted" or base["pops"] >= budget:
        return row
    inc = base["incumbent"]
    row["incumbent"] = list(inc)
    cands = escape_candidates(*inc, cap, fanout)
    row["n_escape_cands"] = len(cands)
    remaining = budget - base["pops"]
    if not cands or remaining <= 0:
        return row
    per = max(1, remaining // len(cands))
    for mu, abel, (o1, o2), c in cands:
        r = greedy_until(o1, o2, per, max(cap, c.cap), plateau_k=None)
        row["nodes_total"] += r["pops"]
        if r["status"] == "solved":
            row.update({
                "solved": True, "phase": "escape",
                "seg1_moves": base["incumbent_moves"],
                "junction": {"z_word": word_to_str(c.z_word),
                             "iso_gen": c.iso_gen, "iso_index": c.iso_index,
                             "escape_start": [o1, o2], "mu": mu,
                             "escape_cap": max(cap, c.cap)},
                "seg2_moves": r["moves"],
            })
            return row
    return row


# ── independent verification (spec + cov only — never this module's search) ─

def verify_escape_row(r1s, r2s, row):
    """Replay a solved row through the spec. Returns (ok, why)."""
    from experiments.greedy_tests.spec.moves import legacy_to_move
    from experiments.greedy_tests.spec.presentation import Presentation
    from experiments.greedy_tests.spec.search import replay

    def _replay(start_strs, legacy_moves):
        pres = Presentation(2, tuple(str_to_word(s) for s in start_strs))
        mvs = [legacy_to_move(t, js, k1, k2) for t, js, k1, k2 in legacy_moves]
        return replay(pres, mvs, cyclic=True)[-1]     # final state

    if not row.get("solved"):
        return False, "row not solved"
    if row["phase"] == "base":
        end = _replay((r1s, r2s), row["seg1_moves"])
        ok = all(len(r) == 1 for r in end.relators)
        return ok, "base path replays to trivial" if ok else "seg1 not trivial"
    end1 = _replay((r1s, r2s), row["seg1_moves"])
    inc = tuple(word_to_str(r) for r in end1.relators)
    j = row["junction"]
    res = cov.apply_cov_once(str_to_word(inc[0]), str_to_word(inc[1]),
                             str_to_word(j["z_word"]), iso_gen=j["iso_gen"],
                             iso_index=j["iso_index"])
    if res is None:
        return False, "junction CoV not applicable at replayed incumbent"
    got = sorted([word_to_str(res.r1), word_to_str(res.r2)])
    if got != sorted(j["escape_start"]):
        return False, f"junction mismatch: {got} != {j['escape_start']}"
    end2 = _replay(tuple(j["escape_start"]), row["seg2_moves"])
    ok = all(len(r) == 1 for r in end2.relators)
    return ok, "stable-AC certificate verifies" if ok else "seg2 not trivial"


# ── runner ──────────────────────────────────────────────────────────────────

def _require_budget_allowed(budget):
    if budget > 1000 and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(f"budget {budget} > 1000 needs ACSOLVERX_ALLOW_BIG=1")


def main():
    from experiments import run_baseline
    from experiments.stable_ac.idea_bench import harness

    ap = argparse.ArgumentParser(description="Stall-triggered CoV escape.")
    ap.add_argument("--bench", default="combined_22")
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--cap", type=int, default=24)
    ap.add_argument("--plateau-k", type=int, default=200)
    ap.add_argument("--fanout", type=int, default=6)
    ap.add_argument("--row-limit", type=int, default=None)
    ap.add_argument("--names", nargs="*", default=None)
    args = ap.parse_args()
    _require_budget_allowed(args.budget)
    root = harness.find_repo_root(HERE)
    out = os.path.join(root, "results/stable_ac/stall_escape",
                       f"stallescape_{args.bench}_{args.budget}_mrl{args.cap}"
                       f"_pk{args.plateau_k}_f{args.fanout}.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            try:
                done.add(json.loads(ln)["pres_id"])
            except (ValueError, KeyError):
                pass
    rows = harness.load_bench(args.bench)
    if args.names:
        keep = set(args.names)
        rows = [p for p in rows if p["pres_id"] in keep]
    if args.row_limit:
        rows = rows[:args.row_limit]
    from experiments.stable_ac.cov.run_cov import _git_commit
    import time as _time
    commit = _git_commit()
    with open(out, "a") as f:
        for p in rows:
            if p["pres_id"] in done:
                continue
            t0 = _time.monotonic()
            control = run_baseline.greedy_search(
                p["r1"], p["r2"], args.budget, max_relator_length=args.cap,
                cyclic_reduce=True)
            row = stall_escape_search(p["r1"], p["r2"], args.budget, args.cap,
                                      plateau_k=args.plateau_k,
                                      fanout=args.fanout)
            verify_ok, why = (verify_escape_row(p["r1"], p["r2"], row)
                              if row["solved"] else (None, None))
            rec = {"pres_id": p["pres_id"], "r1_orig": p["r1"],
                   "r2_orig": p["r2"], "budget": args.budget,
                   "cap": args.cap, "plateau_k": args.plateau_k,
                   "fanout": args.fanout,
                   "control_solved": control["solved"],
                   "control_nodes": control["nodes_explored"],
                   "verify_ok": verify_ok, "verify_why": why,
                   "git_commit": commit,
                   "elapsed_s": round(_time.monotonic() - t0, 2), **row}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            tag = ("ESCAPE-SOLVED" if row["solved"] and row["phase"] == "escape"
                   else row.get("phase") or row["base_status"])
            print(f"  {p['pres_id']}: control={control['solved']} "
                  f"escape={row['solved']} ({tag}) verify={verify_ok}",
                  flush=True)
    print(f"written: {out}", flush=True)


if __name__ == "__main__":
    main()
