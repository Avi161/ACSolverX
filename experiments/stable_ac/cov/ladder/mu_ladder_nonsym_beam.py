"""Rung-local non-automorphic CoV beam (user-specified algorithm).

Per presentation:
  1. Aut-min the current state (Whitehead / ``autcanon_fast``).
  2. Enumerate all non-automorphic CoVs (``n_subs > 1`` + orbit moved).
  3. Aut-min every child.
  4. Keep the ``beam_k`` lowest-μ Aut-min states.
  5. Repeat until ``best_mu <= stop_mu`` (default 12 = MU_CRITERION lead),
     no new orbits, rung cap, or ``max_aut_canon`` budget.

This is the rung-local beam (not global best-first). Imports hop gating from
``mu_ladder_nonsym``; does not edit that module.

    from experiments.stable_ac.cov.ladder.mu_ladder_nonsym_beam import climb_beam
"""
from __future__ import annotations

from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import (
    hop_nonsym,
    orbit_fast,
)


def climb_beam(r1, r2, *, beam_k=10, rungs=32, cap=24, stop_mu=12,
               max_aut_canon=None):
    """Rung-local beam over Aut-min orbits under the nonsym CoV gate.

    ``beam_k`` = how many lowest-μ Aut-min states to keep each rung.
    ``max_aut_canon`` = optional hard stop on Whitehead/Aut-min call count
    (the deterministic work budget).
    """
    if beam_k < 1:
        raise ValueError(f"beam_k must be >= 1, got {beam_k}")
    cost = {"n_aut_canon": 0, "n_enum": 0, "n_subs1_skipped": 0,
            "n_hops_kept": 0, "n_expanded": 0, "n_rungs": 0}
    mu_in, rep_in = orbit_fast((r1, r2))
    cost["n_aut_canon"] += 1
    start = list(rep_in)
    seen = {rep_in}
    # beam entries: (mu, rep, chain_hops)
    beam = [(mu_in, rep_in, [])]
    best_mu, best_rep, best_chain = mu_in, rep_in, []
    stopped = "rungs_exhausted"
    rung_log = []

    if best_mu <= stop_mu:
        return {
            "r1_orig": r1, "r2_orig": r2,
            "mu_in": mu_in, "start_autmin": start,
            "best_mu": best_mu, "best_rep": list(best_rep),
            "best_chain_hops": [], "best_chain": [], "best_nsubs": [],
            "descended": False, "hits_stop": True,
            "n_orbits_seen": 1, "stopped_reason": "stop_mu",
            "beam_k": beam_k, "rung_log": [], "cost": cost,
        }

    for rung in range(1, rungs + 1):
        if max_aut_canon is not None and cost["n_aut_canon"] >= max_aut_canon:
            stopped = "max_aut_canon"
            break
        cand = []
        for _mu_b, rep_b, chain in beam:
            if max_aut_canon is not None and cost["n_aut_canon"] >= max_aut_canon:
                stopped = "max_aut_canon"
                break
            cost["n_expanded"] += 1
            for h in hop_nonsym(rep_b[0], rep_b[1], cap, cost=cost):
                if max_aut_canon is not None and cost["n_aut_canon"] >= max_aut_canon:
                    stopped = "max_aut_canon"
                    break
                rep = tuple(h["rep"])
                if rep in seen:
                    continue
                seen.add(rep)
                new_chain = chain + [h]
                cand.append((h["mu"], rep, new_chain))
                if h["mu"] < best_mu:
                    best_mu, best_rep, best_chain = h["mu"], rep, new_chain
            if stopped == "max_aut_canon":
                break
        cost["n_rungs"] = rung
        rung_log.append({
            "rung": rung, "n_cand": len(cand), "best_mu": best_mu,
            "beam_kept": min(beam_k, len(cand)),
        })
        if not cand:
            stopped = "closed"
            break
        cand.sort(key=lambda t: (t[0], t[1]))
        beam = [(mu, rep, ch) for mu, rep, ch in cand[:beam_k]]
        if best_mu <= stop_mu:
            stopped = "stop_mu"
            break
        if stopped == "max_aut_canon":
            break

    return {
        "r1_orig": r1, "r2_orig": r2,
        "mu_in": mu_in,
        "start_autmin": start,
        "best_mu": best_mu,
        "best_rep": list(best_rep),
        "best_chain_hops": best_chain,
        "best_chain": [h["z"] for h in best_chain],
        "best_nsubs": [h["n_subs"] for h in best_chain],
        "descended": best_mu < mu_in,
        "hits_stop": best_mu <= stop_mu,
        "n_orbits_seen": len(seen),
        "stopped_reason": stopped,
        "beam_k": beam_k,
        "rung_log": rung_log,
        "cost": cost,
    }
