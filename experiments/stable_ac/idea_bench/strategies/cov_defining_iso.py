"""CoV restricted to the DEFINING-RELATOR isolation branch (``iso_index == 2``):
z solves directly to a Nielsen automorphism of a generator (``Z*w`` carries
exactly one +-x or +-y), so z need NOT occur in either relator at all -- unlike
the subword-derived branches (iso_index 0/1), which require z to already
appear inside r1' or r2'. Drawn from the universe z-family (every canonical
word of length 2..4), abel-ranked. Rationale: this Thm-2 sub-family reaches
coordinate systems the subword CoVs structurally cannot, since it never needs
a matching substring in the presentation -- distinct from ``cov_universe``,
which keeps every isolation branch (0, 1, and 2) unfiltered."""

from experiments.stable_ac.cov import cov
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov.restart_planner import abel_magnitude

NAME = "cov_defining_iso"
KIND = "transform"

MAX_CANDIDATES = 60  # portfolio cap, matches the other idea_bench strategies


def _enumerate(r1, r2, cap):
    return cov.enumerate_cov(
        str_to_word(r1), str_to_word(r2), family=cov.universe_candidates(2, 4),
        default_cap=cap, cap_headroom=cov.CAP_HEADROOM, reject_len=cov.REJECT_LEN,
        allow_defining_iso=True)


def _dedup_ranked(results, limit):
    seen, out = set(), []
    for c in results:
        key = (tuple(c.r1), tuple(c.r2))
        if key in seen:
            continue
        seen.add(key)
        out.append((word_to_str(c.r1), word_to_str(c.r2), c.cap,
                    abel_magnitude(c.r1, c.r2)))
    out.sort(key=lambda t: t[3])
    return [(a, b, cp) for a, b, cp, _ in out[:limit]]


def candidates(r1, r2, cap):
    res = _enumerate(r1, r2, cap)
    defining = [c for c in res if c.iso_index == 2]
    # Fallback: no defining-relator branch exists for this presentation --
    # never return an empty list, fall back to the (unfiltered) universe CoV.
    pool = defining if defining else res
    return _dedup_ranked(pool, MAX_CANDIDATES)
