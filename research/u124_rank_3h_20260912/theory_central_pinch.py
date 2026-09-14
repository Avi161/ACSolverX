"""Strict central-power pinches from a retained root-of-product donor."""
import theory_corridor as corridor
from theory_corridor import lemma11
from search import inverse, length, reduced


def models(words, available):
    """Recognize D=z^-1(h^d z^a)^k and certify [z,h^d], retaining D."""
    found, seen, used = [], set(), 0
    for donor, word in enumerate(words):
        if used == available:
            break
        used += 1
        if len({abs(x) for x in word}) != 2 or len(word) < 3:
            continue
        size = len(word) - 1
        for sign, oriented in ((1, word), (-1, inverse(word))):
            for cut in range(len(word)):
                if used == available:
                    return found, used
                used += 1
                if abs(oriented[cut]) == abs(oriented[(cut + 1) % len(word)]):
                    continue
                raw = oriented[cut:] + oriented[:cut]
                stable = -raw[0]
                tail, base, d = raw[1:], raw[1], 0
                while d < size and tail[d] == base:
                    d += 1
                if d == size or abs(tail[d]) != abs(stable):
                    continue
                end = d + 1
                while end < size and tail[end] == tail[d]:
                    end += 1
                w = tail[:end]
                if size % end:
                    continue
                k = size // end
                if w * k != tail:
                    continue
                key = donor, abs(base), abs(stable), d
                if key in seen:
                    continue
                seen.add(key)
                defining = [{'donor_index': donor, 'sign': sign, 'conjugator': oriented[:cut]}]
                factors = defining + corridor.conjugate_factors(corridor.invert_factors(defining), inverse(w))
                relation = (-stable,) + corridor.power(base, d) + (stable,) + corridor.power(base, -d)
                if corridor.evaluate(words, factors) != relation:
                    raise AssertionError('central consequence identity failed')
                found.append({'donor': donor, 'base': base, 'stable': stable, 'power': d,
                    'root_exponent': k, 'root_word': w, 'factors': factors, 'relation': relation})
    return found, used


def pinch_once(words, target, model, available):
    word, used = words[target], 0
    for cut in range(len(word)):
        if used == available:
            break
        used += 1
        signed = word[cut]
        if abs(signed) != abs(model['stable']):
            continue
        rotated = word[cut:] + word[:cut]
        end, exponent = 1, 0
        while end < len(rotated) and abs(rotated[end]) == abs(model['base']):
            exponent += 1 if rotated[end] == model['base'] else -1
            end += 1
        if end == len(rotated) or rotated[end] != -signed or exponent % model['power']:
            continue
        image = corridor.power(model['base'], model['power'])
        primitive = (signed,) + image + (-signed,)
        if signed == -model['stable']:
            correction = corridor.conjugate_factors(corridor.invert_factors(model['factors']), image)
        else:
            correction = corridor.conjugate_factors(model['factors'], (-model['stable'],) + image)
        if corridor.evaluate(words, correction) != reduced(inverse(primitive) + image):
            raise AssertionError('central primitive correction failed')
        correction = corridor._power_correction(primitive, image, correction, exponent // model['power'])
        suffix, frame = rotated[end + 1:], word[:cut]
        factors = corridor.conjugate_factors(correction, suffix + inverse(frame))
        raw = reduced(frame + corridor.power(model['base'], exponent) + suffix + inverse(frame))
        after, event = corridor._event(words, target, raw, factors,
            {'macro': 'retained_donor_central_power_pinch', 'central_donor': model['donor'],
             'central_base': model['base'], 'central_stable': model['stable'],
             'central_power': model['power'], 'pinch_exponent': exponent})
        if length(after) >= length(words):
            raise AssertionError('central pinch did not shorten')
        return after, event, used
    return words, None, used


def descend(words, model, available):
    current, events, used = words, [], 0
    while used < available:
        accepted = False
        for target in range(len(current)):
            if target == model['donor']:
                continue
            after, event, cost = pinch_once(current, target, model, available - used)
            used += cost
            if event is None:
                continue
            positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
            model = dict(model, donor=positions[model['donor']],
                factors=[dict(f, donor_index=positions[f['donor_index']]) for f in model['factors']])
            current = after
            events.append(event)
            accepted = True
            break
        if not accepted:
            break
    return current, events, used


def probe(words, remaining, *, audits=None):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': normalization}]
    recognized, used = models(current, remaining // 2)
    candidates, seen = [], {current}
    for model in recognized:
        after, events, cost = descend(current, model, remaining - used)
        used += cost
        if after not in seen:
            seen.add(after)
            candidates.append((after, prefix + events))
        if audits is not None:
            audits.append({'donor': model['donor'], 'base': model['base'], 'stable': model['stable'],
                'power': model['power'], 'root_exponent': model['root_exponent'],
                'pinches': len(events), 'after_length': length(after)})
        if used == remaining:
            break
    return candidates, used
