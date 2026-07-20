"""CoV candidates ranked by abelianized magnitude (ascending) — the depth-proxy
try-order (IDEAS.md idea 3). Lowest |Σx|+|Σy| first: on shallow instances this
tracks distance-to-trivial; on the hard residual it is a weak prior (measured here)."""

from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_abel"
KIND = "transform"


def candidates(r1, r2, cap):
    return ranked(cov_candidates(r1, r2, cap), key=lambda t: t[3])
