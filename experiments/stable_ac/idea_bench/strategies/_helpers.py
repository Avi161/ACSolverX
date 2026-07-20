"""Shared building blocks for idea_bench transform-strategies.

Underscore prefix => the harness's ``load_strategies`` skips this file (it is not
itself a strategy). A transform-strategy is a pure ``candidates(r1, r2, cap) ->
[(r1', r2', cap'), ...]`` returning candidate STARTING presentations in the order
they should be tried; it runs NO search. These helpers build the common families
(change-of-variables outputs, signed-permutation relabels) already deduped and
ranked, so a strategy file stays a few lines. All coordinates stay 2-generator
(CoV destabilizes z away), so every candidate is searchable by the trusted 2-gen
greedy.
"""

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.restart_planner import abel_magnitude

MAX_CANDIDATES = 60   # portfolio cap: keep the sweep tractable; reported in RESULTS


def cov_candidates(r1, r2, cap, family=None, allow_defining_iso=False):
    """Every valid CoV output pair, deduped, as [(r1s, r2s, cap, abel)] (unranked)."""
    res = cov.enumerate_cov(
        str_to_word(r1), str_to_word(r2), family=family,
        default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
        reject_len=cov.REJECT_LEN, allow_defining_iso=allow_defining_iso)
    seen, out = set(), []
    for c in res:
        key = (tuple(c.r1), tuple(c.r2))
        if key in seen:
            continue
        seen.add(key)
        out.append((word_to_str(c.r1), word_to_str(c.r2), c.cap,
                    abel_magnitude(c.r1, c.r2)))
    return out


def ranked(cands, key, limit=MAX_CANDIDATES):
    """Sort (r1s, r2s, cap, abel) candidates by ``key`` and drop the abel field,
    capping at ``limit`` (portfolio bound). Returns [(r1s, r2s, cap)]."""
    ordered = sorted(cands, key=key)[:limit]
    return [(a, b, c) for a, b, c, _ in ordered]


def _inv(sym):
    return sym.swapcase()


def _signed_perms():
    """The 8 signed permutations of {x, y} as maps {'x': img, 'y': img}."""
    perms = []
    for ix, iy in (("x", "y"), ("y", "x")):
        for sx in (ix, ix.upper()):
            for sy in (iy, iy.upper()):
                perms.append({"x": sx, "y": sy})
    return perms


SIGNED_PERMS = _signed_perms()


def _apply_relabel(word, mp):
    out = []
    for ch in word:
        img = mp[ch.lower()]
        out.append(img if ch.islower() else _inv(img))
    return "".join(out)


def relabel_candidates(r1, r2, cap, skip_identity=True):
    """The (up to 8) signed-permutation relabels of (r1, r2) as [(r1s, r2s, cap, abel)].
    A relabel is a length-preserving coordinate change (a bijection on generators)."""
    out, seen = [], set()
    for mp in SIGNED_PERMS:
        a, b = _apply_relabel(r1, mp), _apply_relabel(r2, mp)
        if skip_identity and (a, b) == (r1, r2):
            continue
        if (a, b) in seen:
            continue
        seen.add((a, b))
        out.append((a, b, cap, abel_magnitude(str_to_word(a), str_to_word(b))))
    return out
