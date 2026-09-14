"""Certified power collection and simultaneous flows in compressed BS corridors."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

PRIOR = Path(__file__).resolve().parent.parent / 'rank_unbounded_20260912'
if str(PRIOR) not in sys.path:
    sys.path.insert(0, str(PRIOR))

import lemma11
from search import inverse, length, normalize, reduced


def power(generator, exponent):
    return (generator if exponent >= 0 else -generator,) * abs(exponent)


def invert_factors(factors):
    return [dict(f, sign=-f['sign']) for f in reversed(factors)]


def conjugate_factors(factors, suffix):
    return [dict(f, conjugator=reduced(tuple(f['conjugator']) + tuple(suffix))) for f in factors]


def evaluate(words, factors):
    result = ()
    for f in factors:
        c = tuple(f['conjugator'])
        donor = words[f['donor_index']]
        result = reduced(result + inverse(c) + (donor if f['sign'] == 1 else inverse(donor)) + c)
    return result


@dataclass
class Root:
    donor: int
    helper: int
    base: int
    exponent: int
    factors: list


def roots(words):
    result = []
    for i, word in enumerate(words):
        for helper in lemma11.single_occurrences(word):
            p = next(j for j, letter in enumerate(word) if abs(letter) == helper)
            left, letter, right = word[:p], word[p], word[p + 1:]
            if letter < 0:
                replacement, sign, c = reduced(right + left), 1, left
            else:
                replacement, sign, c = reduced(inverse(left) + inverse(right)), -1, inverse(right)
            if not replacement or len({abs(x) for x in replacement}) != 1:
                continue
            base = abs(replacement[0])
            if base == helper:
                continue
            exponent = sum(1 if x > 0 else -1 for x in replacement)
            factors = [{'donor_index': i, 'sign': sign, 'conjugator': c}]
            if evaluate(words, factors) != (-helper,) + power(base, exponent):
                raise AssertionError('root isolation identity failed')
            result.append(Root(i, helper, base, exponent, factors))
    return result


def expand_helper(word, root):
    current, factors = reduced(word), []
    while any(abs(x) == root.helper for x in current):
        i = next(j for j, x in enumerate(current) if abs(x) == root.helper)
        letter, suffix = current[i], current[i + 1:]
        correction = root.factors if letter > 0 else conjugate_factors(
            invert_factors(root.factors), (-root.helper,))
        factors.extend(conjugate_factors(correction, suffix))
        replacement = power(root.base, root.exponent if letter > 0 else -root.exponent)
        current = reduced(current[:i] + replacement + suffix)
    return current, factors


def shortest_power(exponent, root):
    quotient = exponent // root.exponent
    choices = []
    for b in {0, quotient, quotient + 1, quotient - 1}:
        a = exponent - root.exponent * b
        left, right = power(root.base, a), power(root.helper, b)
        choices.extend((left + right, right + left))
    return min(choices, key=lambda word: (len(word), word))


def pack_powers(word, root):
    result, i = (), 0
    while i < len(word):
        if abs(word[i]) != root.base:
            result += word[i:i + 1]
            i += 1
            continue
        j, exponent = i, 0
        while j < len(word) and abs(word[j]) == root.base:
            exponent += 1 if word[j] > 0 else -1
            j += 1
        result += shortest_power(exponent, root)
        i = j
    return reduced(result)


def _event(words, target, raw, factors, details):
    raw = reduced(raw)
    if reduced(words[target] + evaluate(words, factors)) != raw:
        raise AssertionError('corridor normal product does not replay')
    replacement = words[:target] + (raw,) + words[target + 1:]
    after, witnesses = lemma11.normalize_witness(replacement)
    return after, {'kind': 'normal_product_substitution', 'before': words, 'target': target,
                   'factors': factors, 'raw_target_after': raw, 'raw_after': replacement,
                   'after': after, 'normalization': witnesses,
                   'length_change': length(after) - length(words),
                   'certificate_kind': 'explicit_ordinary_AC_normal_product', **details}


def collect_root(words, target, root):
    expanded, factors = expand_helper(words[target], root)
    packed = pack_powers(expanded, root)
    check, unpack = expand_helper(packed, root)
    if check != expanded:
        raise AssertionError('packed root exponent differs')
    return _event(words, target, packed, factors + invert_factors(unpack),
                  {'macro': 'relative_power_collection', 'root_donor': root.donor,
                   'root_helper': root.helper, 'root_base': root.base,
                   'root_exponent': root.exponent})


def bs_model(words, root, donor):
    expanded, root_factors = expand_helper(words[donor], root)
    stable = {abs(x) for x in expanded if abs(x) != root.base}
    if len(stable) != 1:
        return None
    stable = stable.pop()
    core, prefix = expanded, ()
    while len(core) > 1 and core[0] == -core[-1]:
        prefix += core[:1]
        core = core[1:-1]
    if sum(abs(x) == stable for x in core) != 2:
        return None
    expression = [{'donor_index': donor, 'sign': 1, 'conjugator': ()}] + root_factors
    for sign in (1, -1):
        signed = core if sign == 1 else inverse(core)
        for cut, letter in enumerate(signed):
            if letter != -stable:
                continue
            oriented = signed[cut:] + signed[:cut]
            pivot = next((i for i, x in enumerate(oriented[1:], 1) if abs(x) == stable), None)
            if pivot is None or oriented[pivot] != stable:
                continue
            first, second = oriented[1:pivot], oriented[pivot + 1:]
            m = sum(1 if x > 0 else -1 for x in first)
            n = -sum(1 if x > 0 else -1 for x in second)
            if m <= 0 or not n:
                continue
            c = reduced(prefix + signed[:cut])
            factors = conjugate_factors(expression if sign == 1 else invert_factors(expression), c)
            relation = (-stable,) + power(root.base, m) + (stable,) + power(root.base, -n)
            if evaluate(words, factors) != relation:
                raise AssertionError('derived Baumslag-Solitar donor does not replay')
            return {'donor': donor, 'stable': stable, 'm': m, 'n': n,
                    'relation': relation, 'factors': factors}
    return None


def _cyclic_corridor(word, root, stable):
    if any(abs(x) not in (root.base, stable) for x in word):
        return None
    cut = next((i for i, x in enumerate(word) if abs(x) == stable), None)
    if cut is None:
        return None
    rotated = word[cut:] + word[:cut]
    signs, exponents = [], []
    for x in rotated:
        if abs(x) == stable:
            signs.append(x)
            exponents.append(0)
        else:
            exponents[-1] += 1 if x > 0 else -1
    return signs, exponents, word[:cut]


def _flow(signs, exponents, root, model, bound, available):
    values = tuple(range(-bound, bound + 1))
    a = [model['m'] if s > 0 else model['n'] for s in signs]
    b = [model['n'] if s > 0 else model['m'] for s in signs]
    count, charged, best = len(signs), 0, None
    for first in values:
        states = {first: (0, (first,))}
        for i in range(count - 1):
            following = {}
            for previous, (cost, path) in states.items():
                for q in values:
                    if charged == available:
                        return None, charged
                    charged += 1
                    e = exponents[i] - b[i] * previous + a[i + 1] * q
                    option = (cost + len(shortest_power(e, root)), path + (q,))
                    if q not in following or (option[0], sum(map(abs, option[1])), option[1]) < (
                            following[q][0], sum(map(abs, following[q][1])), following[q][1]):
                        following[q] = option
            states = following
        for last, (cost, path) in states.items():
            if charged == available:
                return None, charged
            charged += 1
            e = exponents[-1] - b[-1] * last + a[0] * first
            option = (cost + len(shortest_power(e, root)), sum(map(abs, path)), path)
            if best is None or option < best:
                best = option
    return best[-1], charged


def _power_correction(a, b, correction, exponent):
    if exponent < 0:
        correction = conjugate_factors(invert_factors(correction), inverse(a))
        a, b, exponent = inverse(a), inverse(b), -exponent
    result = []
    for i in range(exponent):
        result.extend(conjugate_factors(correction, reduced(a * (exponent - i - 1))))
    return result


def _formal(signs, exponents, base):
    return tuple(x for s, e in zip(signs, exponents) for x in ((s,) + power(base, e)))


def compile_flow(words, target, root, model, choices):
    expanded, factors = expand_helper(words[target], root)
    signs, exponents, frame = _cyclic_corridor(expanded, root, model['stable'])
    initial_exponents = list(exponents)
    base, stable = root.base, model['stable']
    for i, q in enumerate(choices):
        if not q:
            continue
        sign = signs[i]
        a = model['m'] if sign > 0 else model['n']
        b = model['n'] if sign > 0 else model['m']
        primitive = (sign,) + power(base, b) + (-sign,)
        image = power(base, a)
        if sign < 0:
            correction = conjugate_factors(invert_factors(model['factors']), image)
        else:
            correction = conjugate_factors(model['factors'], (-stable,) + image)
        if reduced(inverse(primitive) + image) != evaluate(words, correction):
            raise AssertionError('primitive corridor correction differs')
        correction = _power_correction(primitive, image, correction, q)
        tail = (sign,) + power(base, exponents[i] - b * q) + _formal(
            signs[i + 1:], exponents[i + 1:], base)
        local = conjugate_factors(correction, tail)
        factors.extend(conjugate_factors(local, inverse(frame)))
        exponents[i] -= b * q
        if i:
            exponents[i - 1] += a * q
        else:
            exponents[-1] += a * q
            frame = reduced(frame + power(base, a * q))
    formal = reduced(_formal(signs, exponents, base))
    packed = pack_powers(formal, root)
    check, unpack = expand_helper(packed, root)
    if check != formal:
        raise AssertionError('flow endpoint root packing differs')
    factors.extend(conjugate_factors(invert_factors(unpack), inverse(frame)))
    raw = reduced(frame + packed + inverse(frame))
    return _event(words, target, raw, factors,
                  {'macro': 'compressed_bs_cyclic_flow', 'root_donor': root.donor,
                   'root_helper': root.helper, 'root_base': root.base,
                   'root_exponent': root.exponent, 'bs_donor': model['donor'],
                   'stable_generator': stable, 'bs_m': model['m'], 'bs_n': model['n'],
                   'stable_letters': signs, 'initial_exponents': initial_exponents,
                   'flow': choices, 'final_exponents': exponents})


def probe(words, remaining, *, flow_bound=2):
    """Return ``(candidates, charged)`` with all successful or failed work charged.

    A root collection or attempted second-donor model costs one. Each dynamic
    program transition costs one; incomplete programs yield no flow candidate.
    Costs cover all branches, not just returned paths. Known triviality is not
    needed for these ordinary donor operations. There is no group solve claim.
    """
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    if type(flow_bound) is not int or not 0 <= flow_bound <= 3:
        raise ValueError('flow_bound must be an integer in 0..3')
    before = tuple(tuple(w) for w in words)
    current, witnesses = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': witnesses}]
    candidates, charged = [], 0
    for root in roots(current):
        for target in range(len(current)):
            if target == root.donor:
                continue
            if charged == remaining:
                return candidates, charged
            charged += 1
            after, event = collect_root(current, target, root)
            if after != current:
                candidates.append((after, prefix + [event]))
        for donor in range(len(current)):
            if donor == root.donor:
                continue
            if charged == remaining:
                return candidates, charged
            charged += 1
            model = bs_model(current, root, donor)
            if model is None:
                continue
            for target, word in enumerate(current):
                if target in (root.donor, donor):
                    continue
                expanded, _ = expand_helper(word, root)
                corridor = _cyclic_corridor(expanded, root, model['stable'])
                if corridor is None:
                    continue
                choices, cost = _flow(*corridor[:2], root, model, flow_bound, remaining - charged)
                charged += cost
                if choices is None:
                    return candidates, charged
                after, event = compile_flow(current, target, root, model, choices)
                if after != current:
                    candidates.append((after, prefix + [event]))
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, charged
