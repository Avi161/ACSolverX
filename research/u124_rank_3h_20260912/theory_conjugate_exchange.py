"""Conjugate-base bridge, forced base removal, then a different dictionary."""
from itertools import chain

import theory_conjugate_bridge as bridge
import theory_corridor as corridor
import rank_peeling
import whitehead
from theory_corridor import lemma11
from search import compress, definitions, inverse, length


def _recompress(words, isolating, available):
    candidates, used = [], 0
    forbidden = {tuple(isolating), inverse(tuple(isolating))}
    selected = [word for word in definitions(words) if word not in forbidden][:6]
    for defining in chain(selected, (None,)):
        if used == available:
            break
        if defining is None:
            current, events = words, []
        else:
            current, event = compress(words, defining)
            event['kind'] = 'defining_compression'
            events = [event]
            used += 1
            candidates.append((current, events))
        current, tail, cost, _ = whitehead.descend(current, min(24, available - used))
        used += cost
        events = events + tail
        current, tail, cost, _ = rank_peeling.descend(current, min(16, available - used))
        used += cost
        candidates.append((current, events + tail))
    return candidates, used


def exchange_bridge(words, root, model, signed_stable, exponent, available):
    """Apply one divisor bridge and attempt every affordable base pivot."""
    bridged, prefix, used, complete = bridge.compile_bridge(
        words, root, model, signed_stable, exponent, min(96, available // 3))
    candidates = [(bridged, prefix)] if prefix else []
    audit = {'base': root.base, 'signed_stable': signed_stable,
             'conjugate_exponent': exponent, 'bridge_repacking_complete': complete,
             'bridge_length': length(bridged), 'base_pivots': []}
    if not prefix:
        return candidates, used, audit
    pivots = [row for row in rank_peeling.pivots(bridged) if row[-1] == root.base]
    for position, (_, _, _, donor, generator) in enumerate(pivots):
        if used == available:
            break
        after, removal = lemma11.remove_one(bridged, donor, generator)
        used += 1
        candidates.append((after, prefix + [removal]))
        allowance = (available - used) // (len(pivots) - position)
        packed, cost = _recompress(after, removal['isolating_word'], allowance)
        used += cost
        candidates.extend((endpoint, prefix + [removal] + tail) for endpoint, tail in packed)
        audit['base_pivots'].append({'donor': donor, 'isolating_word': removal['isolating_word'],
            'removed_length': length(after), 'length_change': removal['length_change'],
            'recompression_charged': cost, 'recompression_candidates': len(packed)})
    return candidates, used, audit


def probe(words, remaining, *, audits=None):
    """Return certified intermediate and endpoint candidates within 0..1000 units."""
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': normalization}]
    used, candidates, seen = 0, [], {current}
    for root in corridor.roots(current):
        for donor in range(len(current)):
            if donor == root.donor:
                continue
            if used == remaining:
                return candidates, used
            used += 1
            model = corridor.bs_model(current, root, donor)
            if model is None:
                continue
            for signed_stable, dividend in ((-model['stable'], model['m']),
                                             (model['stable'], model['n'])):
                tested = set()
                for exponent in chain((abs(root.exponent), abs(dividend), 1),
                                      range(2, abs(dividend) + 1)):
                    if exponent in tested:
                        continue
                    tested.add(exponent)
                    if used == remaining:
                        return candidates, used
                    used += 1
                    if dividend % exponent:
                        continue
                    results, cost, audit = exchange_bridge(current, root, model, signed_stable,
                                                           exponent, min(256, remaining - used))
                    used += cost
                    if audits is not None:
                        audits.append(dict(audit, root_donor=root.donor, bs_donor=donor))
                    for after, events in results:
                        if after not in seen:
                            seen.add(after)
                            candidates.append((after, prefix + events))
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, used
