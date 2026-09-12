"""Independent epsilon fixed-point oracle and bounded token enumeration."""
from itertools import product
import json
from pathlib import Path

import verify
import exchange_v2_geodesic as geodesic
import exchange_v2_probe
from verification_consequence_checks import pilot


HERE = Path(__file__).resolve().parent
require, free, words = verify.require, verify.free, verify.words


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def epsilon_oracle(engine):
    dist = {(i, i): (0, 0) for i in range(engine.states)}
    def improve(key, value):
        if value < dist.get(key, (float('inf'), float('inf'))):
            dist[key] = value
            return True
        return False
    for iteration in range(100):
        changed = False
        old = dict(dist)
        for (a, b), left in old.items():
            for (c, d), right in old.items():
                if b == c:
                    changed |= improve((a, d), plus(left, right))
        for a, letter, b, left_tokens in engine.edges:
            for c, other, d, right_tokens in engine.edges:
                if other == -letter and (b, c) in old:
                    tokens = left_tokens + right_tokens
                    weight = (sum(abs(x) == engine.eliminate_generator for x in tokens), len(tokens))
                    changed |= improve((a, d), plus(old[b, c], weight))
        if not changed:
            return dist, iteration + 1
    raise AssertionError('tiny epsilon fixed-point oracle did not converge')


def check_epsilon(engine):
    oracle, passes = epsilon_oracle(engine)
    meter = geodesic.Meter(1000)
    require(engine.saturate(meter), 'tiny engine failed to complete')
    require({key: value[0] for key, value in engine.epsilon.items()} == oracle, 'agenda settlement differs from independent global relaxation')
    for (start, end), (cost, indices) in engine.epsilon.items():
        current, letters, tokens = start, (), ()
        for index in indices:
            a, letter, b, emitted = engine.edges[index]
            require(current == a, 'epsilon reconstructed path is discontinuous')
            current = b
            letters += (letter,)
            tokens += emitted
        require(current == end and free(letters) == (), 'epsilon reconstructed path wrong')
        require(cost == (sum(abs(x) == engine.eliminate_generator for x in tokens), len(tokens)), 'epsilon path cost wrong')
    return {'epsilon_pairs': len(oracle), 'oracle_passes': passes, 'charged_units': meter.used}


def token_enumeration(images, maximum):
    alphabet = tuple(sorted(images)) + tuple(-x for x in sorted(images))
    represented = {}
    count = 0
    for length in range(maximum + 1):
        for tokens in product(alphabet, repeat=length):
            if free(tokens) != tokens:
                continue
            expanded = verify.image(tokens, images)
            represented.setdefault(expanded, []).append(tokens)
            count += 1
    return represented, count


def controls():
    engines, queried, enumerated = [], 0, 0
    for definitions in ({9: (2, 5)}, {9: (2, 5, -2)}):
        engine = geodesic.DictionaryGeodesic((2, 5), definitions)
        engines.append(check_epsilon(engine))
        images = {2: (2,), 5: (5,), **definitions}
        represented, count = token_enumeration(images, 3)
        enumerated += count
        for length in range(4):
            for target in product((2, 5, -2, -5), repeat=length):
                if free(target) != target:
                    continue
                template, complete = engine.shortest(target, geodesic.Meter(1000))
                require(complete and verify.image(template, images) == target, 'complete dictionary query expands incorrectly')
                require(len(template) == min(map(len, represented[target])), 'complete dictionary query is not token geodesic')
                queried += 1
    definition = {3: (1, 1, 1, 2, 2, 2)}
    lex = geodesic.DictionaryGeodesic((1, 2), definition, eliminate_generator=1)
    engines.append(check_epsilon(lex))
    target = (1, 1, 2)
    template, complete = lex.shortest(target, geodesic.Meter(1000))
    images = {1: (1,), 2: (2,), **definition}
    represented, count = token_enumeration(images, 4)
    enumerated += count
    cost = lambda tokens: (sum(abs(x) == 1 for x in tokens), len(tokens))
    require(complete and verify.image(template, images) == target and cost(template) == (1, 4), 'lexicographic optimum control differs')
    require(cost(template) == min(map(cost, represented[target])), 'lexicographic query differs from exhaustive length4 alternatives')
    require(sum(x == 1 for x in target) - sum(x == -1 for x in target) == 2, 'lexicographic lower-bound exponent wrong')
    # With zero old-generator1 tokens, only generator2 and helper3 remain;
    # their generator1 exponent is divisible by3, so cost first-coordinate0 is impossible.
    short = geodesic.DictionaryGeodesic((1, 2), definition)
    check_epsilon(short)
    length_template, length_complete = short.shortest(target, geodesic.Meter(1000))
    require(length_complete and len(length_template) == 3, 'length objective incorrectly replaced by elimination objective')
    repeated_return = lex.saturate(geodesic.Meter(0))
    repeated_template, repeated_complete = lex.shortest(target, geodesic.Meter(1000))
    require(repeated_return is False and lex.saturation_complete is False and repeated_complete is False, 'repeated saturation retains stale completeness')
    require(verify.image(repeated_template, images) == target, 'incomplete query returns invalid candidate')
    planted = verify.normalized(((2, 5, 5, -2, -5), (2, 2, 5, -2, -5)))
    after, event, charged = exchange_v2_probe.compress(planted, ((2, 5, -2, -5),), 1000, eliminate_generator=2)
    require(verify.verify_event(event, known_trivial=True) == words(after), 'v2 complete template ledger fails independent checker')
    return {'status': 'PASS', 'epsilon_oracles': engines, 'complete_queries_vs_exhaustive_tokens': queried,
            'freely_reduced_token_words_enumerated': enumerated, 'lexicographic_template': template,
            'lexicographic_cost': cost(template), 'length_objective_template': length_template,
            'lexicographic_zero_pivot_lower_bound': 'Without oldgenerator1, helper3 contributes exponent multiplesof3, incompatiblewith targetexponent2.',
            'repeated_saturation_regression_pass': True, 'v2_template_event': event,
            'v2_template_charged_units': charged, 'census_searches': 0}


def main():
    result = {'status': 'PASS', 'controls': controls(), 'pilot': pilot('templates_v2_pilot.json'),
              'source_sha256': {name: verify.sha(HERE / name) for name in ('exchange_v2_geodesic.py', 'exchange_v2_probe.py', 'exchange_v2_geodesic_snapshot_before_reset.py')},
              'independent_verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__)),
              'scope': 'Optimality concerns each selected exact reduced orientation and fixed dictionary/objective; orientation selection and whole-tuple search remain heuristic.'}
    (HERE / 'verification_v2_geodesic.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'complete_queries': result['controls']['complete_queries_vs_exhaustive_tokens'],
                      'lexicographic_cost': result['controls']['lexicographic_cost'], 'new_pilot_gains_beyond_seeds': 0}, indent=2))


if __name__ == '__main__':
    main()
