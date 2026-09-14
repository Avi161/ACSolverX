"""Exact retained-donor collection for D=z^-1(h^d z^a)^k, a<0."""
import theory_central_pinch as central
import theory_corridor as corridor
from theory_corridor import lemma11
from search import inverse, length, reduced


class Exhausted(Exception):
    pass


class Budget:
    def __init__(self, available):
        self.available, self.used = available, 0

    def tick(self):
        if self.used == self.available:
            raise Exhausted
        self.used += 1


def _commute(prefix, exponent, model, budget):
    if not exponent:
        return []
    image = corridor.power(model['base'], model['power'])
    result = []
    for i in range(len(prefix) - 1, -1, -1):
        signed = prefix[i]
        if abs(signed) == abs(model['base']):
            continue
        if abs(signed) != abs(model['stable']):
            raise ValueError('central collection prefix contains another generator')
        budget.tick()
        primitive = (signed,) + image + (-signed,)
        if signed == -model['stable']:
            factors = corridor.conjugate_factors(corridor.invert_factors(model['factors']), image)
        else:
            factors = corridor.conjugate_factors(model['factors'], (-model['stable'],) + image)
        factors = corridor._power_correction(primitive, image, factors, exponent)
        result += corridor.conjugate_factors(factors, (signed,) + prefix[i + 1:])
    return result


def prepare(words, model, budget):
    """Derive z^-n h^(dk) as a product of the retained D, never replace D."""
    h, z, d, k, w = model['base'], model['stable'], model['power'], model['root_exponent'], model['root_word']
    tail = w[d:]
    if not tail or any(x != -z for x in tail):
        return None
    a, n = -len(tail), 1 + len(tail) * k
    defining = (-z,) + w * k
    canonical, witness = lemma11.canonical_witness(defining)
    if canonical != words[model['donor']]:
        raise AssertionError('torus defining orientation differs')
    factors = [{'donor_index': model['donor'], 'sign': witness['sign'],
                'conjugator': inverse(tuple(witness['conjugator']))}]
    if corridor.evaluate(words, factors) != defining:
        raise AssertionError('torus defining expression differs')
    for i in range(k):
        prefix = corridor.power(z, a * i - 1)
        suffix = corridor.power(z, a) + w * (k - i - 1)
        factors += corridor.conjugate_factors(_commute(prefix, 1, model, budget), suffix)
    cpower = corridor.power(h, d * k)
    expected = reduced(cpower + corridor.power(z, -n))
    if corridor.evaluate(words, factors) != expected:
        raise AssertionError('torus power consequence differs')
    factors = corridor.conjugate_factors(factors, cpower)
    if corridor.evaluate(words, factors) != corridor.power(z, -n) + cpower:
        raise AssertionError('torus power correction differs')
    return dict(model, n=n, a=a, power_factors=factors)


def _blocks(word, model):
    blocks = []
    for x in word:
        axis = model['base'] if abs(x) == abs(model['base']) else model['stable']
        if abs(x) not in (abs(model['base']), abs(model['stable'])):
            raise ValueError('torus block contains another generator')
        exponent = 1 if x == axis else -1
        if blocks and blocks[-1][0] == axis:
            blocks[-1] = axis, blocks[-1][1] + exponent
        else:
            blocks.append((axis, exponent))
    return blocks


def _spell(blocks):
    return tuple(x for axis, exponent in blocks for x in corridor.power(axis, exponent))


def normal_form(word, model, budget):
    h, z, d, n, k = model['base'], model['stable'], model['power'], model['n'], model['root_exponent']
    blocks, stack, total, factors = _blocks(word, model), [], 0, []
    for index, (axis, exponent) in enumerate(blocks):
        budget.tick()
        if stack and stack[-1][0] == axis:
            exponent += stack.pop()[1]
        modulus = d if axis == h else n
        quotient, residue = divmod(exponent, modulus)
        center = quotient if axis == h else k * quotient
        suffix = corridor.power(axis, residue) + _spell(blocks[index + 1:])
        if axis == z and quotient:
            budget.tick()
            correction = corridor._power_correction(corridor.power(z, n), corridor.power(h, d * k),
                                                     model['power_factors'], quotient)
            factors += corridor.conjugate_factors(correction, suffix)
        factors += corridor.conjugate_factors(_commute(_spell(stack), center, model, budget), suffix)
        total += center
        if residue:
            stack.append((axis, residue))
    normal = reduced(corridor.power(h, d * total) + _spell(stack))
    return (total, tuple(stack)), normal, factors


def _allocate(residues, modulus, total):
    values = [0] * (len(residues) + 1)
    if total >= 0:
        values[0] = total
    else:
        order = sorted(range(len(residues)), key=lambda i: (-residues[i], i))
        count = min(-total, len(order))
        for i in order[:count]:
            values[i] = -1
        values[0] -= -total - count
    exponents = [r + modulus * q for r, q in zip(residues + [0], values)]
    return sum(map(abs, exponents)), exponents


def shortest(signature, model, budget):
    total, blocks = signature
    h, z, d, n, k = model['base'], model['stable'], model['power'], model['n'], model['root_exponent']
    hs = [r for axis, r in blocks if axis == h]
    zs = [r for axis, r in blocks if axis == z]
    choices = {-j for j in range(len(zs) + 1)}
    for j in range(len(hs) + 1):
        q = (total + j) // k
        choices.update((q, q + 1))
    best = None
    for b in sorted(choices):
        budget.tick()
        hcost, hexps = _allocate(hs, d, total - k * b)
        zcost, zexps = _allocate(zs, n, b)
        hi, zi = iter(hexps[:-1]), iter(zexps[:-1])
        word = corridor.power(h, hexps[-1]) + corridor.power(z, zexps[-1])
        word += tuple(x for axis, _ in blocks for x in corridor.power(axis, next(hi) if axis == h else next(zi)))
        word = reduced(word)
        if len(word) != hcost + zcost:
            raise AssertionError('torus allocation contains unaccounted cancellation')
        candidate = len(word), word
        if best is None or candidate < best:
            best = candidate
    return best[1]


def collect(words, target, model, budget):
    source = words[target]
    allowed = {abs(model['base']), abs(model['stable'])}
    cut = next((i for i, x in enumerate(source) if abs(x) not in allowed), 0)
    frame, rotated = source[:cut], source[cut:] + source[:cut]
    output, factors, i = (), [], 0
    while i < len(rotated):
        if abs(rotated[i]) not in allowed:
            output += (rotated[i],)
            i += 1
            continue
        end = i + 1
        while end < len(rotated) and abs(rotated[end]) in allowed:
            end += 1
        block = rotated[i:end]
        signature, normal, incoming = normal_form(block, model, budget)
        packed = shortest(signature, model, budget)
        if len(packed) > len(block):
            raise AssertionError('torus optimizer increased block length')
        if packed != block:
            outgoing_signature, outgoing_normal, outgoing = normal_form(packed, model, budget)
            if outgoing_signature != signature or outgoing_normal != normal:
                raise AssertionError('torus packed normal form differs')
            factors += corridor.conjugate_factors(incoming + corridor.invert_factors(outgoing), rotated[end:])
        output += packed
        i = end
    raw = reduced(frame + output + inverse(frame))
    factors = corridor.conjugate_factors(factors, inverse(frame))
    return corridor._event(words, target, raw, factors,
        {'macro': 'retained_donor_torus_normal_collection', 'torus_donor': model['donor'],
         'torus_base': model['base'], 'torus_root': model['stable'],
         'torus_d': model['power'], 'torus_k': model['root_exponent'], 'torus_n': model['n']})


def probe(words, remaining, *, audits=None):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if current == before else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': normalization}]
    recognized, used = central.models(current, remaining // 4)
    budget, candidates, seen = Budget(remaining - used), [], {current}
    for raw_model in recognized:
        try:
            model = prepare(current, raw_model, budget)
            if model is None:
                continue
            for target in range(len(current)):
                if target == model['donor']:
                    continue
                budget.tick()
                after, event = collect(current, target, model, budget)
                if after not in seen:
                    seen.add(after)
                    candidates.append((after, prefix + [event]))
                if audits is not None:
                    audits.append({'donor': model['donor'], 'target': target,
                        'd': model['power'], 'k': model['root_exponent'], 'n': model['n'],
                        'length_change': length(after) - length(current)})
        except Exhausted:
            break
    return candidates, used + budget.used
