"""Exact hybrid used for the three-row AC19 cloud campaign."""
from __future__ import annotations

from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
from experiments.search.cascade_heuristics import search as cascade_search
from experiments.search.heuristics import S20_MK2

PREFIX_BUDGET = 501
STARTER_BUDGET = 500
SEARCH_CAP = 255
MACRO_CAP = None


def run_hybrid_10m(r1, r2, budget, mrl, progress=None, reserve_states=None,
                   track_path=False):
    """Run the fixed 501-node cascade prefix, then restart with compact S20.

    Restarting the fallback from the input pair is part of the measured hybrid
    definition. Prefix work is charged to the same total budget. The three-row
    campaign pins the prefix to an unsolved normalization/rewrite/S40 attempt;
    an unexpected prefix solve is rejected so an Aut move is never serialized
    as an ordinary AC substitution certificate.
    """
    if mrl != SEARCH_CAP:
        raise ValueError(f"hybrid_10m requires cap {SEARCH_CAP}, got {mrl}")
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= PREFIX_BUDGET:
        raise ValueError(f"budget must be an integer greater than {PREFIX_BUDGET}")

    prefix = cascade_search(
        (r1, r2), budget=PREFIX_BUDGET, cap=SEARCH_CAP,
        starter_budget=STARTER_BUDGET, rewrite_budget=1000,
        intermediate_cap=MACRO_CAP)
    attempts = prefix["attempts"]
    signature = [(a["component"], a["nodes"], a.get("solved")) for a in attempts]
    expected = [("normalization", 0, None), ("rewrite", 1, None),
                ("s40_gen", STARTER_BUDGET, False)]
    if prefix["solved"] or prefix["nodes_explored"] != PREFIX_BUDGET or signature != expected:
        raise RuntimeError(
            "hybrid prefix drifted from the certified three-row campaign: "
            f"solved={prefix['solved']}, nodes={prefix['nodes_explored']}, "
            f"signature={signature}")

    def shifted_progress(nodes, *values):
        if progress is not None:
            progress(PREFIX_BUDGET + nodes, *values)

    fallback = greedy_search_hcompact(
        r1, r2, budget - PREFIX_BUDGET, max_relator_length=SEARCH_CAP,
        config=S20_MK2, progress=shifted_progress,
        reserve_states=reserve_states, track_path=track_path)

    prefix_best = list(prefix["best_state"])
    fallback_best = list(fallback["min_relator"])
    fallback_nodes = int(fallback["nodes_explored"])
    best = (prefix_best if sum(map(len, prefix_best))
            < sum(map(len, fallback_best)) else fallback_best)
    fallback.update(
        nodes_explored=PREFIX_BUDGET + fallback_nodes,
        min_relator_length=sum(map(len, best)),
        min_relator=best,
        hybrid_prefix_nodes=PREFIX_BUDGET,
        hybrid_fallback_nodes=fallback_nodes,
        hybrid_prefix_best=prefix_best,
        hybrid_prefix_max_relator_length_seen=prefix["max_relator_length_seen"],
        hybrid_prefix_attempts=attempts,
    )
    return fallback
