"""CoV over a LONGER-subword z-family (contiguous length 3..6, vs the default
family's short length-2..3 favorites) — abel-ranked. A longer z is a bigger
coordinate jump per substitution; this tests whether that reaches an easier
basin a short z cannot, at the cost of trying fewer, more disruptive starts.

Family: every contiguous subword of length 3..6 of r1, r2 AND their cyclic
rotations (so wrap-around windows are covered too), freely reduced, deduped
by ``max(w, w**-1)``. Falls back to the full default family if the deep
family yields no valid CoV (e.g. relators shorter than 3 letters)."""

from experiments.greedy_tests.spec.words import inverse, is_freely_reduced, rotate, str_to_word
from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_deep_z"
KIND = "transform"

MIN_Z_LEN = 3
MAX_Z_LEN = 6


def _deep_subwords(word):
    """Contiguous length-``MIN_Z_LEN..MAX_Z_LEN`` subwords of every cyclic
    rotation of ``word`` (so every wrap-around window is included too),
    freely reduced, canonicalised to ``max(w, w**-1)``, deduped."""
    n = len(word)
    seen, out = set(), []
    for k in range(n):
        rot = rotate(word, k)
        for length in range(MIN_Z_LEN, MAX_Z_LEN + 1):
            if length > n:
                break
            sub = rot[:length]
            if not is_freely_reduced(sub):
                continue
            canon = max(sub, inverse(sub))
            if canon in seen:
                continue
            seen.add(canon)
            out.append(canon)
    return out


def candidates(r1, r2, cap):
    family, seen = [], set()
    for w in _deep_subwords(str_to_word(r1)) + _deep_subwords(str_to_word(r2)):
        if w not in seen:
            seen.add(w)
            family.append(w)

    cands = cov_candidates(r1, r2, cap, family=family)
    if not cands:                              # deep family found nothing valid
        cands = cov_candidates(r1, r2, cap)    # fall back to the full family
    return ranked(cands, key=lambda t: t[3])
