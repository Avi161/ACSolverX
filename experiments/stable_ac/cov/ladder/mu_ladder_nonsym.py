"""Non-automorphic CoV best-first ladder (advisor-REVISE form).

Gates (PROOFS.tex Thm 1 + orbit check; Thm 3 Aut-min after every hop):
  * ``n_subs > 1`` pre-screen (Thm 1: n_subs=1 ⇒ automorphic under
    transformed-relator isolation; ``allow_defining_iso=False`` so Thm 1
    applies — the orbit check is what *proves* non-automorphy).
  * ``aut_canon(out) ≠ aut_canon(in)`` (orbit-moving).
  * Every accepted hop is replaced by its Aut-min immediately; expansion
    is only from Aut-min pairs; visited = Aut-min orbits.

Search over the open set is **global best-first by μ** (not a rung-local
beam — lesson: rung-local-beam-abandons-the-low-shell). Canonicalisation
uses ``autcanon_fast.aut_min`` for the climb; slow ``aut_canon`` stays in
the verifier for cross-check.

Cost is charged in ``n_aut_canon`` calls (deterministic), never wall-clock.

    from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import climb_nonsym
"""
from __future__ import annotations

import heapq

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min


def orbit_fast(pair):
    """``(mu, aut_min_pair)`` via numba twin — identical rows to ``aut_canon``[:2]."""
    mu, rep = aut_min((str(pair[0]), str(pair[1])))
    return int(mu), (str(rep[0]), str(rep[1]))


def hop_nonsym(r1s, r2s, cap, cost=None):
    """n_subs>1 + orbit-moving hops from an Aut-min parent.

    Returns list of hop dicts with full provenance:
    ``parent_pair, z, iso_gen, iso_index, n_subs, concrete_pair, mu, rep``.
    """
    parent = (str(r1s), str(r2s))
    res = cov.enumerate_cov(
        str_to_word(parent[0]), str_to_word(parent[1]),
        default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
        reject_len=cov.REJECT_LEN,
        allow_defining_iso=False,  # Thm 1 hypothesis; do not flip casually
    )
    if cost is not None:
        cost["n_enum"] = cost.get("n_enum", 0) + 1
    _, rep_in = orbit_fast(parent)
    if cost is not None:
        cost["n_aut_canon"] = cost.get("n_aut_canon", 0) + 1
    out = []
    seen_child = set()
    n_subs1 = 0
    for c in res:
        if int(c.n_subs) <= 1:
            n_subs1 += 1
            continue
        concrete = (word_to_str(c.r1), word_to_str(c.r2))
        mu, rep = orbit_fast(concrete)
        if cost is not None:
            cost["n_aut_canon"] = cost.get("n_aut_canon", 0) + 1
        if rep == rep_in or rep in seen_child:
            continue
        seen_child.add(rep)
        out.append({
            "parent_pair": list(parent),
            "z": word_to_str(c.z_word),
            "iso_gen": c.iso_gen,
            "iso_index": int(c.iso_index),
            "n_subs": int(c.n_subs),
            "concrete_pair": list(concrete),
            "mu": mu,
            "rep": list(rep),
        })
    if cost is not None:
        cost["n_subs1_skipped"] = cost.get("n_subs1_skipped", 0) + n_subs1
        cost["n_hops_kept"] = cost.get("n_hops_kept", 0) + len(out)
    return out


def climb_nonsym(r1, r2, *, max_expand=64, cap=24, stop_mu=12,
                 max_aut_canon=None):
    """Global best-first (by μ) over Aut-min orbits under the n_subs>1 gate.

    ``max_expand`` = max Aut-min states popped for expansion.
    ``max_aut_canon`` optional hard stop on canonicalisation count.
    """
    cost = {"n_aut_canon": 0, "n_enum": 0, "n_subs1_skipped": 0,
            "n_hops_kept": 0, "n_expanded": 0}
    mu_in, rep_in = orbit_fast((r1, r2))
    cost["n_aut_canon"] += 1
    start = list(rep_in)
    seen = {rep_in}
    # heap entries: (mu, tie_pair, rep, hop_from_root_index)
    # hop provenance stored in `hops` list; parent links via hop index.
    hops = []  # list of hop dicts (empty for root)
    parent_hop = {rep_in: None}  # rep -> hop index that produced it, or None
    heap = [(mu_in, rep_in, rep_in)]
    best_mu, best_rep = mu_in, rep_in
    stopped = "expand_exhausted"

    while heap and cost["n_expanded"] < max_expand:
        if max_aut_canon is not None and cost["n_aut_canon"] >= max_aut_canon:
            stopped = "max_aut_canon"
            break
        mu_b, _tie, rep_b = heapq.heappop(heap)
        if mu_b > best_mu:
            # heap may hold dominated entries; still expand for closure under
            # the popped-μ ball, but best_mu only updates on improvement.
            pass
        cost["n_expanded"] += 1
        if best_mu <= stop_mu:
            stopped = "stop_mu"
            break
        for h in hop_nonsym(rep_b[0], rep_b[1], cap, cost=cost):
            if max_aut_canon is not None and cost["n_aut_canon"] >= max_aut_canon:
                stopped = "max_aut_canon"
                break
            rep = tuple(h["rep"])
            if rep in seen:
                continue
            seen.add(rep)
            hops.append(h)
            parent_hop[rep] = len(hops) - 1
            heapq.heappush(heap, (h["mu"], rep, rep))
            if h["mu"] < best_mu:
                best_mu, best_rep = h["mu"], rep
        if stopped == "max_aut_canon":
            break
    else:
        if not heap:
            stopped = "closed" if cost["n_expanded"] > 0 else "no_candidates"

    # Reconstruct hop chain from start to best_rep.
    chain_hops = []
    cur = best_rep
    guard = 0
    while parent_hop.get(cur) is not None:
        hi = parent_hop[cur]
        chain_hops.append(hops[hi])
        cur = (str(hops[hi]["parent_pair"][0]),
               str(hops[hi]["parent_pair"][1]))
        guard += 1
        if guard > len(hops) + 2:
            raise RuntimeError("parent walk cycle in climb_nonsym")
    chain_hops.reverse()

    return {
        "r1_orig": r1, "r2_orig": r2,
        "mu_in": mu_in,
        "start_autmin": start,
        "best_mu": best_mu,
        "best_rep": list(best_rep),
        "best_chain_hops": chain_hops,  # full provenance per hop
        "best_chain": [h["z"] for h in chain_hops],
        "best_nsubs": [h["n_subs"] for h in chain_hops],
        "descended": best_mu < mu_in,
        "n_orbits_seen": len(seen),
        "stopped_reason": stopped,
        "cost": cost,
        "all_hops": hops,
    }


def remaining_budget_alpha(n_aut_canon, alpha, total_nodes=1000):
    """Nodes left after charging ``alpha`` nodes per ``aut_canon`` call."""
    spent = int(round(float(alpha) * int(n_aut_canon)))
    spent = max(0, min(int(total_nodes), spent))
    return max(0, int(total_nodes) - spent), spent


def solved_at_alpha(treat_solved, treat_nodes, n_aut_canon, alpha,
                    total_nodes=1000):
    """Rescore a full-budget-1000 run at charge α (zero extra search)."""
    b_rem, spent = remaining_budget_alpha(n_aut_canon, alpha, total_nodes)
    if not treat_solved:
        return False, b_rem, spent
    return int(treat_nodes) <= b_rem, b_rem, spent
