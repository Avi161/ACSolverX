"""Composes CoV with relabel: for each of the top ~8 abel-ranked change-of-variables
outputs (best abelianized magnitude first), emit the CoV itself then its (up to 8)
signed-permutation relabels, before moving to the next CoV. Rationale: a relabel is a
free string-order change on top of a CoV basin; the greedy reads strings, so different
relabels of the same basin can flip solve/unsolve via Booth-seed / tie-break effects,
multiplying the diversity of each CoV cheaply. Differs from cov_abel (CoV alone) and
relabel8 (relabels of the ORIGINAL alone) by composing both — the novelty is the cross
product, not either family on its own."""

from experiments.stable_ac.idea_bench.strategies._helpers import (
    cov_candidates, ranked, relabel_candidates, MAX_CANDIDATES,
)

NAME = "cov_plus_relabel"
KIND = "transform"

N_COV = 8


def candidates(r1, r2, cap):
    covs = ranked(cov_candidates(r1, r2, cap), key=lambda t: t[3], limit=N_COV)
    out, seen = [], set()

    def add(a, b, c):
        key = (a, b)
        if key in seen:
            return
        seen.add(key)
        out.append((a, b, c))

    for cr1, cr2, ccap in covs:
        add(cr1, cr2, ccap)
        for rr1, rr2, rcap, _ in relabel_candidates(cr1, cr2, ccap):
            add(rr1, rr2, rcap)

    return out[:MAX_CANDIDATES]
