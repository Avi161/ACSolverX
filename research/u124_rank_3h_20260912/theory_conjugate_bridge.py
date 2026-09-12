"""Divisible conjugate-base definitions, followed by exact repacking and cleanup."""
from dataclasses import dataclass
from itertools import chain

import theory_corridor as corridor
import theory_stable_metric as stable_metric
import rank_peeling
import whitehead
from theory_corridor import lemma11
from search import inverse, length, reduced


@dataclass
class Conjugate:
    donor: int
    helper: int
    stable: int
    exponent: int
    replacement: tuple
    factors: list


def _add(words, root, signed_stable, exponent):
    helper = max(abs(x) for w in words for x in w) + 1
    defining = (signed_stable,) + corridor.shortest_power(exponent, root) + (-signed_stable,)
    raw = ((-helper,) + defining,) + words
    after, normalization = lemma11.normalize_witness(raw)
    positions = {row['input_index']: i for i, row in enumerate(normalization)}
    donor = positions[0]
    witness = normalization[donor]
    factors = [{'donor_index': donor, 'sign': witness['sign'],
                'conjugator': inverse(tuple(witness['conjugator']))}]
    if corridor.evaluate(after, factors) != raw[0]:
        raise AssertionError('conjugate-base defining identity failed')
    helper_data = Conjugate(donor, helper, signed_stable, exponent, defining, factors)
    event = {'kind': 'defining_compression', 'before': words, 'defining': defining,
             'helper': helper, 'cuts': [0] * len(words), 'templates': words,
             'raw_after': raw, 'after': after, 'uses': 0, 'literal_length': length(raw),
             'final_length': length(after), 'normalization': normalization}
    return after, helper_data, positions, event


def _tokens(word, root, helper):
    best = [()] * (len(word) + 1)
    for i in range(len(word) - 1, -1, -1):
        choices = [(word[i],) + best[i + 1]]
        if abs(word[i]) == root.base:
            j, exponent = i, 0
            while j < len(word) and abs(word[j]) == root.base:
                exponent += 1 if word[j] > 0 else -1
                j += 1
            choices.append(corridor.shortest_power(exponent, root) + best[j])
        if word[i] == helper.stable:
            j, exponent = i + 1, 0
            while j < len(word) and abs(word[j]) == root.base:
                exponent += 1 if word[j] > 0 else -1
                j += 1
            if j < len(word) and word[j] == -helper.stable and exponent % helper.exponent == 0:
                choices.append(corridor.power(helper.helper, exponent // helper.exponent) + best[j + 1])
        best[i] = min(choices, key=lambda w: (len(w), w))
    return best[0]


def _pack(words, target, root, helper, available):
    expanded, factors = stable_metric._expand(words[target], helper)
    expanded, more = corridor.expand_helper(expanded, root)
    factors += more
    core, witness = lemma11.canonical_witness(expanded)
    best, used = None, 0
    for cut in range(max(1, len(core))):
        if used == available:
            break
        used += 1
        rotated = core[cut:] + core[:cut]
        packed = _tokens(rotated, root, helper)
        option = (len(packed), packed, cut)
        if best is None or option < best:
            best = option
    if best is None:
        return words, None, used, False
    _, packed, cut = best
    frame = core[:cut]
    packed_core = reduced(frame + packed + inverse(frame))
    c, sign = tuple(witness['conjugator']), witness['sign']
    raw = reduced(c + (packed_core if sign > 0 else inverse(packed_core)) + inverse(c))
    unpacked, unpack = stable_metric._expand(raw, helper)
    unpacked, more = corridor.expand_helper(unpacked, root)
    unpack += more
    if unpacked != expanded:
        raise AssertionError('conjugate-base repacking changes expanded target')
    after, event = corridor._event(words, target, raw, factors + corridor.invert_factors(unpack),
        {'macro': 'divisible_conjugate_base_repacking', 'signed_stable': helper.stable,
         'conjugate_exponent': helper.exponent, 'cyclic_cuts_complete': used == max(1, len(core))})
    return after, event, used, used == max(1, len(core))


def compile_bridge(words, root, model, signed_stable, exponent, available):
    if available <= 0:
        return words, [], 0, False
    old_root_donor = root.donor
    current, helper, positions, event = _add(words, root, signed_stable, exponent)
    events, used, complete = [event], 1, True
    root = corridor.Root(positions[root.donor + 1], root.helper, root.base, root.exponent,
                        [dict(f, donor_index=positions[f['donor_index'] + 1]) for f in root.factors])
    pending = [positions[model['donor'] + 1]] + [positions[i + 1] for i in range(len(words))
                                                if i not in (old_root_donor, model['donor'])]
    pending = [i for i in pending if i not in (root.donor, helper.donor)]
    while pending:
        target = pending.pop(0)
        current, event, cost, done = _pack(current, target, root, helper, available - used)
        used += cost
        complete &= done
        if event is None:
            complete = False
            break
        events.append(event)
        positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
        pending = [positions[i] for i in pending]
        root = corridor.Root(positions[root.donor], root.helper, root.base, root.exponent,
                            [dict(f, donor_index=positions[f['donor_index']]) for f in root.factors])
        helper = Conjugate(positions[helper.donor], helper.helper, helper.stable, helper.exponent,
                           helper.replacement, [dict(f, donor_index=positions[f['donor_index']]) for f in helper.factors])
    return current, events, used, complete


def probe(words, remaining, *, audits=None):
    """Return bridge and cleanup candidates, including neutral or longer states."""
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
            for signed_stable, dividend in ((-model['stable'], model['m']), (model['stable'], model['n'])):
                tested = set()
                for exponent in chain((abs(root.exponent), abs(dividend), 1), range(2, abs(dividend) + 1)):
                    if exponent in tested:
                        continue
                    tested.add(exponent)
                    if used == remaining:
                        return candidates, used
                    used += 1
                    if dividend % exponent:
                        continue
                    allowance = min(128, remaining - used)
                    reserve = min(48, allowance // 3)
                    bridge, events, cost, complete = compile_bridge(current, root, model, signed_stable,
                                                                    exponent, allowance - reserve)
                    used += cost
                    if bridge not in seen:
                        seen.add(bridge)
                        candidates.append((bridge, prefix + events))
                    final, tail, cost, _ = whitehead.descend(bridge, min(32, remaining - used))
                    used += cost
                    final, removals, cost, _ = rank_peeling.descend(final, min(24, remaining - used))
                    used += cost
                    if final not in seen:
                        seen.add(final)
                        candidates.append((final, prefix + events + tail + removals))
                    if audits is not None:
                        audits.append({'root_donor': root.donor, 'bs_donor': donor,
                            'signed_stable': signed_stable, 'conjugate_exponent': exponent,
                            'dividend': dividend, 'repacking_complete': complete,
                            'bridge_length': length(bridge), 'cleanup_length': length(final)})
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, used
