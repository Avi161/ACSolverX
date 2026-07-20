"""CoV candidates ranked by max relator length (ascending) — shrink-the-longest-relator
first, rather than total length or abelianized magnitude. Rationale: the greedy stalls
when one relator is long; a CoV that shortens the longest relator may descend fastest."""

from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_min_maxrelator"
KIND = "transform"


def candidates(r1, r2, cap):
    return ranked(cov_candidates(r1, r2, cap), key=lambda t: max(len(t[0]), len(t[1])))
