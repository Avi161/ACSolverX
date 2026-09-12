"""Conjugate dictionary exchange followed by full retained-torus collection."""
import theory_conjugate_exchange as exchange
import theory_torus_collect as torus
import whitehead
import rank_peeling
from search import length


def probe(words, remaining, *, audits=None):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    candidates, used = exchange.probe(words, remaining // 2)
    seen = {tuple(tuple(w) for w in words)} | {state for state, _ in candidates}
    seeds = [(state, path) for state, path in candidates if path and
             path[-1]['kind'] == 'lemma11_removal' and
             sum(e['kind'] == 'defining_compression' for e in path) == 1]
    seeds.sort(key=lambda item: (length(item[0]), item[0]))
    for state, path in seeds:
        if used == remaining:
            break
        allowance = min(320, remaining - used)
        local_audit = []
        results, cost = torus.probe(state, max(0, allowance - 48), audits=local_audit)
        used += cost
        for after, events in results:
            if after not in seen:
                seen.add(after)
                candidates.append((after, path + events))
            endpoint, tail, cost, _ = whitehead.descend(after, min(24, remaining - used))
            used += cost
            endpoint, removals, cost, _ = rank_peeling.descend(endpoint, min(24, remaining - used))
            used += cost
            if endpoint not in seen:
                seen.add(endpoint)
                candidates.append((endpoint, path + events + tail + removals))
        if audits is not None:
            audits.append({'seed_length': length(state), 'torus_models': local_audit,
                           'torus_candidates': len(results)})
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, used
