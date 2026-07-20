"""CoV candidates ranked by (abel_magnitude, total_length, max_relator_length) —
abel-magnitude stays the primary depth proxy, but its many ties are now broken by
preferring a shorter total start and then a shorter longest relator, instead of
whatever arbitrary order the single-key cov_abel ranker leaves them in."""

from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_abel_len_lex"
KIND = "transform"


def candidates(r1, r2, cap):
    return ranked(cov_candidates(r1, r2, cap),
                  key=lambda t: (t[3], len(t[0]) + len(t[1]), max(len(t[0]), len(t[1]))))
