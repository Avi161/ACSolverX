"""CoV over the UNIVERSE z-family (every reduced word of length 2..4, with
defining-relator isolation allowed) rather than only relator subwords — a much
broader set of coordinate systems, abel-ranked. Tests whether reaching beyond
subword-derived z buys coverage the subword family misses."""

from experiments.stable_ac.cov import cov
from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_universe"
KIND = "transform"


def candidates(r1, r2, cap):
    fam = cov.universe_candidates(2, 4)
    cands = cov_candidates(r1, r2, cap, family=fam, allow_defining_iso=True)
    return ranked(cands, key=lambda t: t[3])
