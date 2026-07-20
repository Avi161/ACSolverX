"""Depth-2 iterated-CoV restart tree (restart_planner.build_restart_plan): a CoV of a
CoV, cap-fit filtered, deduped by Aut-orbit, and abel-ranked. Differs from restart_tree
(depth=1) by taking a second hop -- single-hop CoV under-explores the stable class, and
the second hop reaches an order of magnitude more coordinate systems (AK(3): 2 -> 12
orbits at hop 1 -> 2), all ranked by the same abelianized-magnitude proxy and orbit-deduped
by the planner."""

from experiments.stable_ac.cov.restart_planner import build_restart_plan

NAME = "cov_restart_2hop"
KIND = "transform"


def candidates(r1, r2, cap):
    plan = build_restart_plan(r1, r2, depth=2, cap=cap, max_nodes=60)
    return [(rec["r1"], rec["r2"], cap) for rec in plan]
