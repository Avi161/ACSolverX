"""The (up to 8) signed-permutation relabels of the presentation, abel-ranked.
A relabel is a length-preserving coordinate change — the cheapest possible restart:
no stabilization, no substitution. Measures how much of any CoV gain is just the
greedy reading different strings (Booth-seed / tie-break effects) vs a real basin
change. Baseline is same-orbit, so a relabel win is pure string-order sensitivity."""

from experiments.stable_ac.idea_bench.strategies._helpers import relabel_candidates, ranked

NAME = "relabel8"
KIND = "transform"


def candidates(r1, r2, cap):
    return ranked(relabel_candidates(r1, r2, cap), key=lambda t: t[3])
