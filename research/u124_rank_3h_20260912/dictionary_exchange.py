"""Remove a defining generator, then recompress before judging the longer tuple."""
import rank_peeling
from rank_peeling import lemma11, search
import whitehead


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    used, removed, candidates, seen = 0, [], [], {words}
    for _, _, _, index, generator in rank_peeling.pivots(words):
        if used == remaining:
            return candidates, used
        used += 1
        after, event = lemma11.remove_one(words, index, generator)
        if after not in seen:
            seen.add(after)
            removed.append((after, [event]))
            candidates.append((after, [event]))
    removed.sort(key=lambda row: (search.length(row[0]), row[0]))
    for position, (expanded, prefix) in enumerate(removed[:3]):
        allowance = (remaining - used) // (min(3, len(removed)) - position)
        stop = used + allowance
        if not expanded or not allowance:
            continue
        definitions = search.definitions(expanded)
        for defining in definitions[:8]:
            if used == stop:
                break
            after, event = search.compress(expanded, defining)
            event['kind'] = 'defining_compression'
            used += 1
            events = prefix + [event]
            endpoint, suffix, charged, _ = whitehead.descend(after, min(32, stop - used))
            used += charged
            events += suffix
            endpoint, suffix, charged, _ = rank_peeling.descend(endpoint, min(24, stop - used))
            used += charged
            events += suffix
            if endpoint not in seen:
                seen.add(endpoint)
                candidates.append((endpoint, events))
    return candidates, used
