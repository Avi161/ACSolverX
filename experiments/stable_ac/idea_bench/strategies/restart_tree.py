"""Iterated-CoV restart tree (restart_planner.build_restart_plan): distinct-orbit
restart points reached in one hop, cap-fit filtered, deduped by Aut-orbit, and
abel-ranked (IMPLEMENTATION_IDEAS.md idea 1). Differs from cov_abel in the z-family
(build_a2 rotations vs enumerate_cov branches) and in the hard orbit dedup — so it
races genuinely distinct coordinate systems, not every branch."""

from experiments.stable_ac.cov.restart_planner import build_restart_plan

NAME = "restart_tree"
KIND = "transform"


def candidates(r1, r2, cap):
    plan = build_restart_plan(r1, r2, depth=1, cap=cap, max_nodes=60)
    return [(rec["r1"], rec["r2"], cap) for rec in plan]
