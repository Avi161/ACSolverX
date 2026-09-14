"""Independent coin, finite-flow, triangular certificate and shear controls."""
from itertools import product
import json
from pathlib import Path

import theory_multi_metric as multi
import theory_corridor as corridor
import verify


HERE = Path(__file__).resolve().parent


def power(g, n):
    return (g if n >= 0 else -g,) * abs(n)


def coin_distances(small, large, depth):
    costs = {0: 0}
    frontier = {0}
    for distance in range(1, depth + 1):
        following = {e + delta for e in frontier for delta in (1, -1, small, -small, large, -large)} - set(costs)
        costs.update({e: distance for e in following})
        frontier = following
    return costs


def replay(initial, endpoint, events):
    current = initial
    for event in json.loads(json.dumps(events)):
        verify.require(verify.words(event['before']) == current, 'triangular chain discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    verify.require(current == verify.words(endpoint), 'triangular endpoint differs')
    verify.require(len(current) == len(initial) + 1, 'triangular construction lost a relator')


def metric_controls():
    coin_checks, flow_checks, partial_checks = 0, [], 0
    for small, large in ((2, 5), (3, 7)):
        metric = multi.Metric(2, 11, 5, small, large)
        coins = coin_distances(small, large, 5)
        for exponent in range(-10, 11):
            spelling = metric.spell(exponent)
            require_exponent = sum((1 if x > 0 else -1) * {2: 1, 11: small, 5: large}[abs(x)] for x in spelling)
            verify.require(require_exponent == exponent and len(spelling) == coins[exponent], 'triangular coin spelling differs from integer BFS')
            coin_checks += 1
        for signs, exponents, model, ceiling in (([1], [2], {'m': 2, 'n': 3}, 1), ([1, 1], [1, -1], {'m': 1, 'n': 2}, 1)):
            chosen, spent, complete, audit = multi._flow(signs, exponents, metric, model, ceiling, 1000)
            verify.require(complete and spent <= 1000, 'tiny triangular flow incomplete')
            bounds = audit['mathematically_sufficient_flow_bounds']
            brute = []
            for q in product(*(range(-bound, bound + 1) for bound in bounds)):
                out = [e - (model['n'] if signs[i] > 0 else model['m']) * q[i] + (model['m'] if signs[(i + 1) % len(signs)] > 0 else model['n']) * q[(i + 1) % len(signs)] for i, e in enumerate(exponents)]
                total = sum(coins.get(e, 1000) for e in out)
                if total <= ceiling:
                    brute.append((total, sum(map(abs, q)), q))
            verify.require(chosen == (None if not brute else min(brute)[2]), 'triangular flow optimum differs from independent finite-box enumeration')
            for allowance in (0, max(0, spent // 2), max(0, spent - 1)):
                partial, used, done, _ = multi._flow(signs, exponents, metric, model, ceiling, allowance)
                verify.require(not done and used <= allowance, 'truncated triangular flow falsely complete')
                if partial is not None:
                    verify.require(any(item[2] == partial for item in brute), 'truncated triangular flow returns invalid candidate')
                partial_checks += 1
            flow_checks.append({'small': small, 'large': large, 'signs': signs, 'bounds': bounds, 'units': spent, 'chosen': chosen})
    chains = []
    for old, pair, q in product((-2, 2), ((2, 3), (3, 7)), (-1, 1)):
        a, x, h = 2, 5, 10**25
        initial = verify.normalized(((-h,) + power(a, old), (-x,) + power(a, 4) + (x,) + power(a, -5), (x,) + power(a, 11)))
        root = next(r for r in corridor.roots(initial) if r.helper == h and r.base == a)
        model = next(m for i in range(3) if i != root.donor and (m := corridor.bs_model(initial, root, i)))
        target = next(i for i in range(3) if i not in (root.donor, model['donor']))
        endpoint, events = multi.compile_metric(initial, root, model, target, (q,), *pair)
        replay(initial, endpoint, events)
        verify.require([e['kind'] for e in events] == ['normal_product_substitution', 'ambient_automorphism', 'defining_compression', 'normal_product_substitution', 'normal_product_substitution', 'normal_product_substitution'], 'triangular event order differs')
        addition = events[2]
        verify.require(addition['uses'] == 0 and verify.words(addition['templates']) == verify.words(addition['before']), 'triangular addition improperly substitutes old rows')
        defining_rows = events[3]['factors']
        verify.require(len(set(f['donor_index'] for f in defining_rows)) == 1, 'upper-definition compression uses more than the lower donor')
        chains.append({'old': old, 'denominations': pair, 'flow': q, 'rank': len(endpoint), 'lengths': [verify.size(initial)] + [verify.size(e['after']) for e in events], 'events': events})
    return {'status': 'PASS', 'coin_BFS_checks': coin_checks, 'finite_flow_checks': flow_checks,
            'truncated_flow_controls': partial_checks, 'signed_triangular_chains': chains,
            'known_triviality_proof': 'The companion x a^11 makes x=a^-11; BS(4,5) then forces a=1 and the retained/helper definitions force all remaining generators to1.'}


def shear_controls():
    a, x, h = 2, 5, 11
    controls = []
    for (m, n), signs, (p, q) in product(((4, 5), (5, 4)), ((1,), (-1,), (1, 1, -1), (-1, 1, -1)), ((2, 1), (-3, 1), (2, -2))):
        forward = {a: (a,), x: power(a, p) + (x,) + power(a, q), h: (h,)}
        inverse = {a: (a,), x: power(a, -p) + (x,) + power(a, -q), h: (h,)}
        verify.require(all(verify.image(forward[g], inverse) == (g,) and verify.image(inverse[g], forward) == (g,) for g in forward), 'stable shear inverse differs')
        donor = (-x,) + power(a, m) + (x,) + power(a, -n)
        verify.require(verify.image(donor, forward) == verify.free(power(a, -q) + donor + power(a, q)), 'stable shear donor conjugation differs')
        exponents = tuple(range(1, len(signs) + 1))
        original = tuple(t for s, e in zip(signs, exponents) for t in ((s * x,) + power(a, e)))
        vectors = [(s + signs[(i + 1) % len(signs)]) // 2 for i, s in enumerate(signs)]
        shifted = [e + (p + q) * v for e, v in zip(exponents, vectors)]
        predicted = tuple(t for s, e in zip(signs, shifted) for t in ((s * x,) + power(a, e)))
        frame = power(a, p if signs[0] > 0 else -q)
        verify.require(verify.image(original, forward) == verify.free(frame + predicted + verify.invert(frame)), 'cyclic stable-gap shear identity differs')
        constant = (p + q) // (m - n)
        flowed = [e - (n if signs[i] > 0 else m) * constant + (m if signs[(i + 1) % len(signs)] > 0 else n) * constant for i, e in enumerate(exponents)]
        verify.require(flowed == shifted, 'consecutive-BS constant flow differs from shear')
        controls.append({'m': m, 'n': n, 'signs': signs, 'p': p, 'q': q, 'constant_flow': constant})
    verify.require(1 % (2 - 5) != 0, 'nonconsecutive divisibility limitation not exercised')
    return {'status': 'PASS', 'signed_shear_controls': controls, 'nonconsecutive_countercondition': {'m': 2, 'n': 5, 'p_plus_q': 1, 'constant_integer_flow_exists': False}}


def main():
    for name, controls in [('multi_metric', metric_controls()), ('stable_shear', shear_controls())]:
        result = {'status': 'PASS', 'controls': controls, 'source_sha256': verify.sha(HERE / 'theory_multi_metric.py'),
                  'proof_note_sha256': verify.sha(HERE / 'theory_relators.md'), 'verifier_sha256': verify.sha(HERE / 'verify.py'),
                  'script_sha256': verify.sha(Path(__file__)), 'census_searches': 0}
        (HERE / ('verification_' + name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'module': name, 'controls': len(controls.get('signed_triangular_chains', controls.get('signed_shear_controls', [])))}, indent=2))


if __name__ == '__main__':
    main()
