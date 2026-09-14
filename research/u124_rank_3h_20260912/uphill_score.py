"""Rank growing donor rewrites by their exact best one-step Whitehead response."""
import plateau
import rank_peeling
from exchange_collect_aliases import score
from plateau import search, whitehead


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    candidates, charged = plateau.rewrite_candidates(words, min(128, remaining // 4),
                                                    increase=max(map(len, words), default=0))
    grown = [row for row in candidates if search.length(row[0]) > search.length(words)]
    grown.sort(key=lambda row: (search.length(row[0]), row[0]))
    reserve = min(256, (remaining - charged) // 2)
    selected, seen = [], set()
    for state, prefix in grown:
        vertices = {s for word in state for x in word for s in (x, -x)}
        if charged + len(vertices) > remaining - reserve:
            break
        after, events, used, _ = score(state)
        charged += used
        if after not in seen:
            seen.add(after)
            selected.append((after, prefix + events))
    selected.sort(key=lambda row: (search.length(row[0]), row[0]))
    out = list(selected)
    for state, prefix in selected:
        if charged == remaining:
            break
        after, events, used, _ = whitehead.descend(state, min(32, remaining - charged))
        charged += used
        after, tail, used, _ = rank_peeling.descend(after, min(24, remaining - charged))
        charged += used
        out.append((after, prefix + events + tail))
    return out, charged
