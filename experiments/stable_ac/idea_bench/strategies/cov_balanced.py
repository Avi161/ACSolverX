"""CoV candidates ranked by relator-length balance (ascending |len(r1')-len(r2')|) —
most equal-length pairs first, rather than total length, max length, or abelianized
magnitude. Rationale: a balanced presentation gives each relator a same-length
cancellation partner, which may descend faster than one long + one short relator."""

from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_balanced"
KIND = "transform"


def candidates(r1, r2, cap):
    return ranked(cov_candidates(r1, r2, cap), key=lambda t: abs(len(t[0]) - len(t[1])))
