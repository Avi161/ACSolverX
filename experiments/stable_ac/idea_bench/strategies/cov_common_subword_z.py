"""CoV restricted to the most FREQUENTLY OCCURRING short (length 2..3) cyclic
subwords shared across r1 and r2, rather than every subword (cov_abel) or the
full presentation-independent universe (cov_universe). A subword that recurs --
within a relator, across its rotations, or across both relators -- is the
natural thing to promote to a new variable z: naming a repeated pattern
concentrates the CoV portfolio on coordinate changes that target recurring
structure, instead of spreading budget over every one-off subword. w and w^-1
are counted together (they yield the same CoV up to inverting z, same
convention as cov.subword_candidates) and the top ~8 most frequent become the
z-family; CoV outputs over that family are abel-ranked, same depth-proxy prior
as cov_abel. Falls back to the full subword family when the targeted family
yields no valid CoV, so a low-repetition presentation still gets a portfolio."""

from collections import Counter

from experiments.greedy_tests.spec.words import inverse, reduce_word, str_to_word
from experiments.stable_ac.idea_bench.strategies._helpers import cov_candidates, ranked

NAME = "cov_common_subword_z"
KIND = "transform"

TOP_K = 8          # z-words kept after frequency ranking
LENGTHS = (2, 3)   # short recurring subwords only


def _cyclic_subwords(word, length):
    """All cyclic (wrap-around) contiguous subwords of `word` at exactly `length`,
    one per rotation start -- empty if `word` is shorter than `length`."""
    n = len(word)
    if n < length:
        return []
    doubled = word + word
    return [doubled[i:i + length] for i in range(n)]


def _top_subword_words(r1, r2, top_k=TOP_K, lengths=LENGTHS):
    """The `top_k` most frequent length-2..3 cyclic subwords across r1, r2,
    canonicalized w ~ w^-1 (max(w, inverse(w))) so a z and its inverse share one
    count. Deterministic order: frequency desc, then (length, tuple) for ties."""
    counts = Counter()
    for r in (r1, r2):
        cyc = reduce_word(str_to_word(r), cyclic=True)
        for length in lengths:
            for w in _cyclic_subwords(cyc, length):
                counts[max(w, inverse(w))] += 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
    return [w for w, _count in ordered[:top_k]]


def candidates(r1, r2, cap):
    family = _top_subword_words(r1, r2)
    cands = cov_candidates(r1, r2, cap, family=family) if family else []
    if not cands:
        cands = cov_candidates(r1, r2, cap)   # never return an empty portfolio
    return ranked(cands, key=lambda t: t[3])
