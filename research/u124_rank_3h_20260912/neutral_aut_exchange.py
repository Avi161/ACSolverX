"""Cross a whole-Aut plateau before adding and simplifying a defining helper."""
import plateau
import rank_peeling
from plateau import search, whitehead


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    neighbors, charged = plateau.neutral_whitehead(words, min(192, remaining // 4))
    planning_limit = min(remaining, charged + remaining // 5)
    proposals = []
    seen = {words}
    for state, prefix in neighbors:
        for defining in search.definitions(state)[:4]:
            if charged == planning_limit:
                break
            after, event = search.compress(state, defining)
            event['kind'] = 'defining_compression'
            charged += 1
            if after not in seen:
                seen.add(after)
                proposals.append((after, prefix + [event]))
        if charged == planning_limit:
            break
    proposals.sort(key=lambda row: (search.length(row[0]), row[0]))
    out = list(neighbors)
    for state, prefix in proposals:
        if charged == remaining:
            break
        after, tail, cost, _ = whitehead.descend(state, min(48, remaining - charged))
        charged += cost
        after, peel, cost, _ = rank_peeling.descend(after, min(24, remaining - charged))
        charged += cost
        out.append((after, prefix + tail + peel))
    return out, charged
