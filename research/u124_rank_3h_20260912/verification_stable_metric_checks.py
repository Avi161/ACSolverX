"""Independent two-sided spelling identities, finite costs and certificate replay."""
from itertools import product
import json
from pathlib import Path

import verify
import theory_corridor as corridor
import theory_stable_metric as first
import theory_stable_metric_v2 as second
from verification_flow_exact_checks import inverse_matrix, exponent_flow, packing_cost
from verification_consequence_checks import p

HERE = Path(__file__).resolve().parent
require = verify.require


def adjusted(signs, gaps, bits, left, right):
    prefixes = [0 if not bit else (left if sign > 0 else -right) for sign, bit in zip(signs, bits)]
    suffixes = [0 if not bit else (right if sign > 0 else -left) for sign, bit in zip(signs, bits)]
    return [gap - suffixes[i] - prefixes[(i + 1) % len(signs)] for i, gap in enumerate(gaps)], prefixes[0]


def replay(before, after, events):
    current = before
    for event in json.loads(json.dumps(events)):
        require(verify.words(event['before']) == current, 'stable spelling chain discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    require(current == after, 'stable spelling endpoint differs')
    return len(events)


def controls():
    patterns = optima = bad_uncompensated = 0
    for exponent in (-3, 2):
        root = corridor.Root(-1, 11, 5, exponent, [])
        for signs in ((2,), (-2,), (2, -2, 2), (-2, 2, -2)):
            gaps = tuple(i - 1 for i in range(len(signs)))
            original = verify.free(tuple(x for sign, gap in zip(signs, gaps) for x in (sign,) + p(5, gap)))
            for left, right in ((-2, 3), (2, -3), (0, 2), (1, 0)):
                expected = []
                for bits in product((0, 1), repeat=len(signs)):
                    shifted, prefix = adjusted(signs, gaps, bits, left, right)
                    expected.append((sum(packing_cost(e, exponent) for e in shifted), bits))
                    packed = tuple(x for sign, bit, gap in zip(signs, bits, shifted)
                                   for x in ((17 if sign > 0 else -17,) if bit else (sign,)) + p(5, gap))
                    expanded = verify.image(packed, {2: (2,), 5: (5,), 17: p(5, left) + (2,) + p(5, right)})
                    require(verify.free(p(5, -prefix) + expanded + p(5, prefix)) == original, 'first-prefix frame identity fails')
                    bad_uncompensated += expanded != original
                    require(first._adjust(signs, gaps, bits, left, right) == shifted == second._adjust(signs, gaps, bits, left, right), 'bit shift differs')
                    patterns += 1
                for module in (first, second):
                    atom = module.Atom(-1, 17, 2, left, right, (), [])
                    require(module._best_bits(signs, gaps, root, atom) == min(expected), 'cyclic two-state optimum differs from exhaustive bits')
                optima += 1
    require(bad_uncompensated > 0, 'control did not detect missing prefix compensation')
    chains = events_checked = 0
    high = 10 ** 24 + 19
    for exponent in (-2, 2):
        initial = verify.normalized(((-high,) + p(5, exponent), (-2,) + p(5, 4) + (2,) + p(5, -5), (2,) + p(5, 11)))
        root = next(r for r in corridor.roots(initial) if r.helper == high)
        model = next(m for i in range(3) if i != root.donor and (m := corridor.bs_model(initial, root, i)))
        target = next(i for i in range(3) if i not in (root.donor, model['donor']))
        for left, right, flow in ((-2, 4, -1), (2, -4, 0), (0, -5, 1), (-5, 0, -1)):
            for module in (first, second):
                after, events = module.compile_metric(initial, root, model, target, (flow,), left, right)
                events_checked += replay(initial, after, events)
                require(len(after) == 4 and all(after), 'stable spelling omitted relators')
                require(events[1]['helper'] == high + 1 and events[1]['uses'] == 0, 'new definition was not retained separately')
                chains += 1
    balls = pairs = partials = 0
    for exponent in (-3, 2, 5):
        root = corridor.Root(-1, 11, 5, exponent, [])
        for ceiling in range(4):
            values, used, complete = second._coin_ball(root, ceiling, 1000)
            expected = {e: packing_cost(e, exponent) for e in range(-abs(exponent) * ceiling, abs(exponent) * ceiling + 1)
                        if packing_cost(e, exponent) <= ceiling}
            require(complete and values == expected and used == 2 * ceiling * ceiling + 2 * ceiling + 1, 'signed coin ball or accounting differs')
            generated = list(second._parameters(root, {'m': 4, 'n': 5}, values, ceiling))
            oracle = {(a, b) for a, b in product(expected, repeat=2) if (a, b) != (0, 0) and expected[a] + expected[b] <= ceiling}
            require(set(generated) == oracle and len(generated) == len(oracle), 'parameter family omission or duplicate')
            for allowance in sorted({0, used - 1}):
                subset, charged, done = second._coin_ball(root, ceiling, allowance)
                require(charged == allowance and not done and set(subset) <= set(expected), 'partial ball claims complete')
                partials += 1
            balls += 1
            pairs += len(generated)
    zero_plant = verify.normalized(((-11, 5, 5), (-2, 11, 5, 5, 2, -5, -5, -5, -5, -5), (2,)))
    probe_rows = []
    for module in (first, second):
        audits = []
        candidates, charged = module.probe(zero_plant, 1000, audits=audits)
        require(charged <= 1000 and candidates, 'zero-cost planted probe failed')
        rational_checks = 0
        for audit in audits:
            if audit.get('reason') != 'unique_rational_flow_solution':
                continue
            root = next(r for r in corridor.roots(zero_plant) if r.donor == audit['root_donor'])
            model = corridor.bs_model(zero_plant, root, audit['bs_donor'])
            target = next(i for i in range(3) if i not in (root.donor, model['donor']))
            expanded = verify.image(zero_plant[target], {g: (g,) for g in {abs(x) for w in zero_plant for x in w} - {root.helper}} | {root.helper: p(root.base, root.exponent)})
            require(expanded == (-model['stable'],) or expanded == (model['stable'],), 'zero plant changed')
            signs, gaps = [expanded[0]], [0]
            shifted, _ = adjusted(signs, gaps, audit['atom_bits'], audit['atom_left'], audit['atom_right'])
            a = [model['m'] if s > 0 else model['n'] for s in signs]
            b = [model['n'] if s > 0 else model['m'] for s in signs]
            inv = inverse_matrix([[a[0] - b[0]]])
            rational = [-sum(c * e for c, e in zip(row, shifted)) for row in inv]
            require(audit['rational_flow'] == list(map(str, rational)), 'rational solve differs from Gaussian elimination')
            found = audit['found_flow']
            require((found is None) == any(x.denominator != 1 for x in rational), 'rational integrality decision wrong')
            if found is not None:
                require(exponent_flow(signs, shifted, model, found) == [0], 'zero flow has nonzero residual')
            rational_checks += 1
        for after, events in candidates:
            replay(zero_plant, after, events)
            require(verify.size(after) < verify.size(zero_plant), 'credited non-strict candidate')
        if module is second:
            phases = [a for a in audits if a.get('phase') == 'exact_parameter_cost_ball']
            require(phases and all(not a['parameter_family_complete'] or (a['parameter_pairs_enumerated'] and a['all_tested_flows_complete']) for a in phases), 'family completeness flags inconsistent')
        probe_rows.append({'module': module.__name__, 'charged': charged, 'strict_candidates_replayed': len(candidates), 'Gaussian_rational_solutions_checked': rational_checks})
    return {'status': 'PASS', 'cyclic_bit_patterns': patterns, 'exhaustive_bit_optima': optima,
            'missing_prefix_compensation_counterexamples': bad_uncompensated,
            'signed_high_label_chains': chains, 'chain_events': events_checked,
            'exact_cost_balls': balls, 'exact_parameter_pairs': pairs, 'truncated_cost_balls': partials,
            'zero_cost_planted_probes': probe_rows, 'census_searches': 0,
            'known_triviality': 'The target x*y^11 (or x) and the BS(4,5) donor imply y=1, x=1; the root and stable helper definitions then imply all helpers are trivial.'}


def main():
    result = {'status': 'PASS', 'controls': controls(),
              'source_sha256': {n: verify.sha(HERE / n) for n in ('theory_stable_metric.py', 'theory_stable_metric_v2.py')},
              'script_sha256': verify.sha(Path(__file__)), 'verifier_sha256': verify.sha(HERE / 'verify.py'),
              'scope': 'Exact two-sided retained-spelling family for normalized rank-3 root/BS inputs without a cyclic Britton pinch; completed finite parameters and flows do not prove global AC minimality.'}
    (HERE / 'verification_stable_metric.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['controls'], indent=2))


if __name__ == '__main__':
    main()
