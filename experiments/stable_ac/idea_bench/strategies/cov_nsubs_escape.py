"""CoV candidates split into two escape tiers by n_subs, orbit-escaping tier first.

An n_subs>=2 change of variables performs two or more genuine substitutions across
the two relators -- it leaves the input's Aut(F2)-orbit and lands in a genuinely new
coordinate system. An n_subs<=1 CoV merely re-seeds the SAME orbit (see
experiments/lessons/cited-theorem-hypothesis-never-fires.md: the n_subs=1 case is a
pure relabel because the isolating map is an isomorphism regardless of |w|). Try the
orbit-escaping group first -- a stuck search escapes only by changing orbit -- then
the reseed group; within each group, rank by abelianized magnitude ascending (the
depth-proxy prior)."""

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.restart_planner import abel_magnitude

NAME = "cov_nsubs_escape"
KIND = "transform"

MAX_CANDIDATES = 60   # portfolio cap, matches the other cov_* strategies


def candidates(r1, r2, cap):
    res = cov.enumerate_cov(
        str_to_word(r1), str_to_word(r2), default_cap=cap,
        cap_headroom=cov.CAP_HEADROOM, reject_len=cov.REJECT_LEN)
    seen, escaping, reseed = set(), [], []
    for c in res:
        key = (tuple(c.r1), tuple(c.r2))
        if key in seen:
            continue
        seen.add(key)
        item = (word_to_str(c.r1), word_to_str(c.r2), c.cap, abel_magnitude(c.r1, c.r2))
        (escaping if c.n_subs >= 2 else reseed).append(item)
    escaping.sort(key=lambda t: t[3])
    reseed.sort(key=lambda t: t[3])
    ordered = (escaping + reseed)[:MAX_CANDIDATES]
    return [(a, b, cp) for a, b, cp, _ in ordered]
