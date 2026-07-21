"""CoV candidates ranked by the Aut-minimal length of their OUTPUT orbit —
mu-first, then abel magnitude, then total length.

Motivation (STABLE_AC_NEW.tex, orbit-floor section): the orbit floor is NOT
CoV-invariant — an n_subs>=2 subword CoV can land in an orbit with strictly
smaller Aut-minimal total length (AK(2): 11 -> 10; an ms640 row: 6 -> 2, the
standard orbit, in ONE hop). A mu-descending candidate is a candidate descent
toward a trivialization, so try those first; same-orbit re-seeds tie at the
input's mu and fall back to the abel/length order. Costs one ``aut_canon``
(~5 ms) per candidate at enumeration time — zero search nodes.
"""

from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_mu_lex"
KIND = "transform"


def candidates(r1, r2, cap):
    cands = cov_candidates(r1, r2, cap)
    mu = {(a, b): aut_min_len((a, b)) for a, b, _, _ in cands}
    return ranked(cands, key=lambda t: (mu[(t[0], t[1])], t[3],
                                        len(t[0]) + len(t[1])))
