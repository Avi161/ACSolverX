"""CoV candidates ranked by total start length (ascending) — shortest transformed
presentation first. A blunt alternative prior to abel-magnitude: does 'just make the
start short' order the portfolio as well as the abelianized depth proxy?"""

from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_len"
KIND = "transform"


def candidates(r1, r2, cap):
    return ranked(cov_candidates(r1, r2, cap), key=lambda t: len(t[0]) + len(t[1]))
