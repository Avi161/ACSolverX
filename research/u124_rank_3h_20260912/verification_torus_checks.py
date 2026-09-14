"""Independent normal signatures, allocation minima and ordinary torus ledgers."""
import itertools
import json
from pathlib import Path

import verify as v
import theory_central_pinch as central
import theory_torus_collect as torus
from verification_central_checks import evaluate, power
from verification_consequence_checks import pilot

HERE = Path(__file__).resolve().parent


def signature(word, model):
    total, stack = 0, []
    h, z, d, n, k = (model[key] for key in ('base', 'stable', 'power', 'n', 'root_exponent'))
    for letter in word:
        axis = h if abs(letter) == abs(h) else z
        v.require(abs(letter) in (abs(h), abs(z)), 'unexpected signature generator')
        exponent = 1 if letter == axis else -1
        if stack and stack[-1][0] == axis:
            exponent += stack.pop()[1]
        q, r = divmod(exponent, d if axis == h else n)
        total += q * (1 if axis == h else k)
        if r:
            stack.append((axis, r))
    return total, tuple(stack)


def allocate_two(residues, modulus, total):
    v.require(len(residues) == 2, 'this independent oracle has exactly two residues')
    radius = abs(total) + 4
    return min(abs(residues[0] + modulus * a) + abs(residues[1] + modulus * b) + modulus * abs(total - a - b)
               for a in range(-radius, radius + 1) for b in range(-radius, radius + 1))


def prepared(rows, h, z):
    models, _ = central.models(rows, 160)
    raw = next(m for m in models if abs(m['base']) == abs(h) and abs(m['stable']) == abs(z) and m['power'] == 2)
    model = torus.prepare(rows, raw, torus.Budget(100))
    v.require(model is not None, 'torus preparation missing')
    expected = power((model['stable'],), -model['n']) + power((model['base'],), 2 * model['root_exponent'])
    v.require(evaluate(rows, model['power_factors']) == expected, 'torus power consequence differs')
    return model


def plant(h=3, z=2, k=2):
    x = 7
    w = (h, h, -z, -z)
    return v.normalized(((-z,) + w * k, (-h, -x, z, x), (x,) + (z,) * (1 + 2 * k), (19,)))


def main():
    rows = plant()
    model = prepared(rows, 3, 2)
    representatives, queries = {}, []
    for length in range(4):
        for raw in itertools.product((2, -2, 3, -3), repeat=length):
            sig = signature(raw, model)
            budget = torus.Budget(150)
            found, normal, factors = torus.normal_form(raw, model, budget)
            v.require(found == sig and v.free(raw + evaluate(rows, factors)) == normal, 'torus normal compiler differs')
            packed = torus.shortest(sig, model, budget)
            v.require(signature(packed, model) == sig and len(packed) <= len(raw), 'torus packed representative differs')
            representatives[sig] = min(representatives.get(sig, length), length)
            queries.append((sig, len(packed)))
    v.require(all(length == representatives[sig] for sig, length in queries), 'tiny exhaustive geodesic minimum differs')
    scalar = []
    for total in range(-4, 5):
        sig = total, ((model['base'], 1), (model['stable'], 2), (model['base'], 1), (model['stable'], 3))
        packed = torus.shortest(sig, model, torus.Budget(100))
        brute = min(allocate_two((1, 1), 2, total - 2 * b) + allocate_two((2, 3), 5, b) for b in range(-7, 8))
        v.require(len(packed) == brute, 'independent torus allocation minimum differs')
        scalar.append({'central_exponent': total, 'minimum': brute})
    chains = []
    for h, z, k in itertools.product((-10 ** 25, 10 ** 25), (-11, 11), (1, 2)):
        before = plant(h, z, k)
        prepared(before, h, z)
        candidates, used = torus.probe(before, 300)
        v.require(candidates and used <= 300, 'torus sparse candidate/budget differs')
        for after, events in candidates:
            cursor = before
            for event in json.loads(json.dumps(events)):
                v.require(v.words(event['before']) == cursor, 'torus chain discontinuity')
                cursor = v.verify_event(event, known_trivial=False)
            v.require(cursor == after and len(after) == 4 and v.size(after) <= v.size(before), 'torus ordinary endpoint differs')
            chains.append({'before': before, 'after': after, 'events': events})
    output = {'status': 'PASS', 'tiny_exact_word_queries': len(queries), 'distinct_normal_forms': len(representatives),
              'independent_scalar_allocation_controls': scalar, 'signed_sparse_rank4_chains': len(chains), 'chains': chains,
              'pilot': pilot('torus_exchange_all33.json'),
              'sources': {name: v.sha(HERE / name) for name in ('theory_torus_collect.py', 'theory_conjugate_exchange_torus.py')},
              'scope': 'Complete shortest spelling in the recognized two-generator retained-donor subgroup metric for each processed maximal block. Does not optimize arbitrary conjugacy frames, other donors, or the full stable orbit. Ordinary identities replay with known_trivial=False; composed stable paths retain source provenance.',
              'census_reruns': 0}
    (HERE / 'verification_torus.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('status', 'tiny_exact_word_queries', 'distinct_normal_forms', 'signed_sparse_rank4_chains')}))


if __name__ == '__main__':
    main()
