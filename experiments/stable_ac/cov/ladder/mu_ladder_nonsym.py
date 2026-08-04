"""Non-automorphic (n_subs>1) CoV beam ladder with cost accounting.

Operationalisation of "only non-automorphic CoVs":
  1. Keep hops with ``n_subs > 1`` (PROOFS.tex Thm 1: every n_subs=1
     transformed-relator CoV is an automorphic image).
  2. Verify ``aut_canon(out) != aut_canon(in)`` (orbit-moving).

After every accepted CoV hop the concrete output is replaced **immediately**
by its Aut-min representative; the beam expands only from Aut-min pairs; the
visited set stores Aut-min orbits so the same orbit is never re-expanded.

    from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import (
        climb_nonsym, calibrate_node_eq_ms)
"""
from __future__ import annotations

import time

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov


def orbit(pair):
    """Return ``(mu, aut_min_pair)`` — always the Aut-min representative."""
    mu, rep, _ = aut_canon((str(pair[0]), str(pair[1])))
    return int(mu), (str(rep[0]), str(rep[1]))


def hop_nonsym(r1s, r2s, cap, cost=None):
    """CoV hops from an Aut-min pair: n_subs>1 and orbit-moving only.

    Parent ``(r1s, r2s)`` is assumed Aut-min (caller enforces). Each kept child
    is returned as its **Aut-min** ``rep`` (not the concrete CoV strings).

    Returns ``{orbit_rep: (mu, aut_min_pair, z, iso_gen, iso_index, n_subs)}``.
    """
    t0 = time.perf_counter()
    res = cov.enumerate_cov(
        str_to_word(r1s), str_to_word(r2s),
        default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
        reject_len=cov.REJECT_LEN)
    enum_ms = (time.perf_counter() - t0) * 1000.0
    t1 = time.perf_counter()
    _, rep_in = orbit((r1s, r2s))
    n_canon = 1
    out = {}
    n_subs1_skipped = 0
    for c in res:
        if int(c.n_subs) <= 1:
            n_subs1_skipped += 1
            continue
        # Concrete CoV output → Aut-min immediately.
        o1, o2 = word_to_str(c.r1), word_to_str(c.r2)
        mu, rep = orbit((o1, o2))
        n_canon += 1
        if rep == rep_in or rep in out:
            continue
        # Store Aut-min pair only — next rung expands from this.
        out[rep] = (mu, rep, word_to_str(c.z_word),
                    c.iso_gen, c.iso_index, int(c.n_subs))
    canon_ms = (time.perf_counter() - t1) * 1000.0
    if cost is not None:
        cost["enum_ms"] = cost.get("enum_ms", 0.0) + enum_ms
        cost["canon_ms"] = cost.get("canon_ms", 0.0) + canon_ms
        cost["n_aut_canon"] = cost.get("n_aut_canon", 0) + n_canon
        cost["n_subs1_skipped"] = cost.get("n_subs1_skipped", 0) + n_subs1_skipped
        cost["n_hops_kept"] = cost.get("n_hops_kept", 0) + len(out)
        cost["wall_ms"] = cost.get("wall_ms", 0.0) + enum_ms + canon_ms
    return out


def climb_nonsym(r1, r2, *, rungs=6, beam_k=10, cap=24, stop_mu=12,
                 cost_budget_ms=None):
    """Beam climb: n_subs>1, Aut-min after every hop, visited = Aut-min orbits.

    Start is Aut-min of the input. Beam entries are always Aut-min pairs.
    ``seen`` holds Aut-min orbit reps — never re-expand a visited orbit.
    """
    cost = {"enum_ms": 0.0, "canon_ms": 0.0, "wall_ms": 0.0,
            "n_aut_canon": 0, "n_subs1_skipped": 0, "n_hops_kept": 0}
    # Immediate Aut-min of the input.
    mu_in, rep_in = orbit((r1, r2))
    cost["n_aut_canon"] += 1
    seen = {rep_in}  # visited Aut-min orbits
    # Beam stores Aut-min pairs only.
    beam = [(mu_in, rep_in, [], [])]  # mu, aut_min_pair, z_chain, nsubs_chain
    best_mu, best_chain, best_rep = mu_in, [], rep_in
    best_nsubs = []
    rung_log = []
    stopped_reason = "rungs_exhausted"

    for rung in range(1, rungs + 1):
        if cost_budget_ms is not None and cost["wall_ms"] >= cost_budget_ms:
            stopped_reason = "cost_budget"
            break
        cand = []
        for _mu_b, pair, chain, nsubs_chain in beam:
            if cost_budget_ms is not None and cost["wall_ms"] >= cost_budget_ms:
                stopped_reason = "cost_budget"
                break
            # Expand CoV from Aut-min state only.
            hops = hop_nonsym(pair[0], pair[1], cap, cost=cost)
            for rep, (mu, aut_min_pair, z, _ig, _ii, ns) in hops.items():
                if rep in seen:
                    continue  # never revisit an Aut-min orbit
                seen.add(rep)  # mark visited immediately
                cand.append(
                    (mu, aut_min_pair, chain + [z], nsubs_chain + [ns], rep))
        if not cand:
            rung_log.append({"rung": rung, "new_orbits": 0, "best": best_mu})
            stopped_reason = "no_candidates"
            break
        cand.sort(key=lambda t: (t[0], t[1]))
        for mu, aut_min_pair, chain, nsubs_chain, rep in cand:
            if mu < best_mu:
                best_mu, best_chain, best_rep = mu, chain, rep
                best_nsubs = nsubs_chain
        # Beam = Aut-min pairs of this rung's top-K.
        beam = [(mu, p, c, ns) for mu, p, c, ns, _ in cand[:beam_k]]
        rung_log.append({"rung": rung, "new_orbits": len(cand),
                         "best": best_mu})
        if best_mu <= stop_mu:
            stopped_reason = "stop_mu"
            break

    return {
        "r1_orig": r1, "r2_orig": r2,
        "mu_in": mu_in,
        "start_autmin": list(rep_in),
        "best_mu": best_mu,
        "best_chain": best_chain,
        "best_nsubs": best_nsubs,
        "best_rep": list(best_rep),
        "descended": best_mu < mu_in,
        "n_orbits_seen": len(seen),
        "rungs": rung_log,
        "stopped_reason": stopped_reason,
        "cost": cost,
    }


def calibrate_node_eq_ms(pairs, budget=200, cap=24, n_warm=1):
    """Mean wall ms per length-greedy pop (calib only — not the shipped 1k baseline)."""
    from experiments.search.greedy_baseline import greedy_search

    for _ in range(n_warm):
        r1, r2 = pairs[0]
        greedy_search(r1, r2, max(50, budget // 4), max_relator_length=cap)

    samples = []
    for r1, r2 in pairs:
        t0 = time.perf_counter()
        res = greedy_search(r1, r2, budget, max_relator_length=cap)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        n = max(int(res["nodes_explored"]), 1)
        samples.append(dt_ms / n)
    return {
        "node_eq_ms": float(sum(samples) / len(samples)),
        "n_samples": len(samples),
        "per_row_ms_per_node": samples,
        "calib_budget": budget,
        "calib_cap": cap,
    }


def remaining_budget(cov_wall_ms, node_eq_ms, total_nodes=1000):
    """Nodes left for greedy after charging CoV wall time as node-equivalents."""
    if node_eq_ms <= 0:
        raise ValueError("node_eq_ms must be positive")
    spent = int(round(float(cov_wall_ms) / float(node_eq_ms)))
    spent = max(0, min(int(total_nodes), spent))
    return max(0, int(total_nodes) - spent), spent
