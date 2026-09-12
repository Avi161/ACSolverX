"""Reserve simplification work for ordinary donor rewrites that first grow."""
import plateau
import rank_peeling
from plateau import search, whitehead


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    candidates, charged = plateau.rewrite_candidates(words, min(128, remaining),
                                                    increase=max(map(len, words), default=0))
    grown = [row for row in candidates if search.length(row[0]) > search.length(words)]
    grown.sort(key=lambda row: (search.length(row[0]), row[0]))
    out = []
    for after, prefix in grown:
        if charged == remaining:
            break
        endpoint, suffix, cost, _ = whitehead.descend(after, min(48, remaining - charged))
        charged += cost
        events = prefix + suffix
        endpoint, suffix, cost, _ = rank_peeling.descend(endpoint, min(16, remaining - charged))
        charged += cost
        events += suffix
        out.append((endpoint, events))
    return out, charged
