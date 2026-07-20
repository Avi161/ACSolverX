"""CoV candidates deduped by Aut(F2)-orbit (one representative per orbit, first-seen kept),
then ordered by Aut-distance FROM THE ORIGINAL descending — the coordinate systems FARTHEST
from the input tried first (orbit-diversity idea, cov_orbit_spread). Distance measure:
``abs(aut_min_len(candidate) - aut_min_len(original))``, the difference between the
candidate's Aut-minimal total length and the original's (both via ``aut_canon``'s ``total``,
so no extra ``aut_min_len`` call is needed per candidate). Rationale: cov_abel's depth proxy
(abel magnitude) is weakest on the hard residual; maximizing basin diversity — landing in a
genuinely different orbit rather than a near-original relabel of the same one — may reach an
easy basin a near-original CoV misses. Differs from cov_abel (ranks by abel magnitude, no
orbit dedup) and from restart_tree/cov_restart_2hop (iterated-CoV via restart_planner, not
enumerate_cov's single-hop branches)."""

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.idea_bench.strategies._helpers import MAX_CANDIDATES, cov_candidates

NAME = "cov_orbit_spread"
KIND = "transform"


def candidates(r1, r2, cap):
    orig_total, _, _ = aut_canon((r1, r2))
    seen, deduped = set(), []
    for r1s, r2s, ccap, _abel in cov_candidates(r1, r2, cap):
        total, rep, _phi = aut_canon((r1s, r2s))
        if rep in seen:
            continue
        seen.add(rep)
        deduped.append((r1s, r2s, ccap, abs(total - orig_total)))
    deduped.sort(key=lambda t: t[3], reverse=True)
    return [(a, b, c) for a, b, c, _dist in deduped[:MAX_CANDIDATES]]
