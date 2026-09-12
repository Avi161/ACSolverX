"""Use the verified neutral/shortening donor rules with imported frontier seeds."""
from plateau import rewrite_candidates


def probe(words, remaining):
    return rewrite_candidates(words, remaining, increase=0)
