"""Read-only predicates for the short-companion fixed-donor corollary."""
from collections import Counter
import json
from pathlib import Path

from verification_flow_exact_checks import inverse_matrix, packing_cost
from verification_preparer_checks import isolate, power
import verify


HERE = Path(__file__).resolve().parent


def main():
    source = HERE / 'flow_exact_diagnostic.json'
    report = json.loads(source.read_text())
    verify.require(report['baseline_sha256'] == verify.BASELINE_SHA256, 'fixed-donor diagnostic baseline differs')
    for path, expected in report['hashes'].items():
        verify.require(verify.sha(HERE / path) == expected, 'fixed-donor diagnostic source changed')
    baseline = verify.load_baseline()
    checked, ids = [], set()
    for row in report['rows']:
        verify.verify_record(row, baseline)
        ids.add(row['name'])
        words = verify.words(row['initial'])
        for audit in row['flow_audits']:
            verify.require(len(words) == 3 and audit['flow_complete'] is True and audit['found_flow'] is None and audit['britton_prefix_events'] == 0, 'short-companion completion hypotheses missing')
            root_donor, bs_donor, target = (audit[k] for k in ('root_donor', 'bs_donor', 'target'))
            verify.require({root_donor, bs_donor, target} == {0, 1, 2}, 'fixed-donor indices overlap or omit row')
            signs, exponents = audit['stable_letters'], audit['initial_exponents']
            stable = abs(signs[0])
            matches = []
            for helper in {abs(x) for x in words[root_donor]}:
                if sum(abs(x) == helper for x in words[root_donor]) != 1:
                    continue
                defining = isolate(words[root_donor], helper)
                if not defining or len({abs(x) for x in defining}) != 1:
                    continue
                base, k = abs(defining[0]), len(defining) * (1 if defining[0] > 0 else -1)
                if stable in (base, helper):
                    continue
                mapping = {g: (g,) for g in {abs(x) for w in words for x in w}}
                mapping[helper] = power(base, k)
                expected_bs = (-stable,) + power(base, audit['bs_m']) + (stable,) + power(base, -audit['bs_n'])
                if verify.independent.representative(verify.image(words[bs_donor], mapping)) != verify.independent.representative(expected_bs):
                    continue
                expanded = verify.image(words[target], mapping)
                first = next(i for i, x in enumerate(expanded) if abs(x) == stable)
                reconstructed = tuple(x for sign, exponent in zip(signs, exponents) for x in ((sign,) + power(base, exponent)))
                if verify.free(reconstructed) != verify.free(expanded[first:] + expanded[:first]):
                    continue
                matches.append((helper, base, k))
            verify.require(len(matches) == 1, 'fixed-donor root/BS/companion reconstruction ambiguous or invalid')
            helper, base, k = matches[0]
            t, stable_sum = len(signs), sum(1 if x > 0 else -1 for x in signs)
            cost = sum(packing_cost(e, k) for e in exponents)
            verify.require(t >= 3 and abs(stable_sum) == 1 and cost <= 3, 'short-companion geometric hypotheses absent')
            verify.require(len(words[target]) == t + cost and audit['cost_ceiling'] == cost - 1, 'packed companion or searched ceiling differs')
            m, n = audit['bs_m'], audit['bs_n']
            verify.require(abs(m - n) == 1, 'recognized root/BS pair is not consecutive')
            for i, sign in enumerate(signs):
                if signs[(i + 1) % t] == -sign:
                    verify.require(exponents[i] % (n if sign > 0 else m) != 0, 'recorded companion has a cyclic Britton pinch')
            a = [m if s > 0 else n for s in signs]
            b = [n if s > 0 else m for s in signs]
            matrix = [[0] * t for _ in range(t)]
            for i in range(t):
                matrix[i][i] -= b[i]
                matrix[i][(i + 1) % t] += a[(i + 1) % t]
            inverse = inverse_matrix(matrix)
            verify.require(inverse is not None, 'saved fixed-donor flow matrix singular')
            bounds = [int(abs(sum(value * e for value, e in zip(line, exponents))) + max(1, abs(k)) * (cost - 1) * max(map(abs, line))) for line in inverse]
            verify.require(bounds == audit['mathematically_sufficient_flow_bounds'], 'saved fixed-donor sufficient box differs')
            checked.append({'name': row['name'], 'helper': helper, 'base': base, 'root_exponent': k, 'stable_generator': stable,
                            'bs_m': m, 'bs_n': n, 'stable_length': t, 'stable_exponent': stable_sum,
                            'power_cost': cost, 'companion_length': len(words[target]), 'searched_ceiling': cost - 1,
                            'flow_complete': True, 'no_cheaper_flow_recorded': True, 'status': 'PASS'})
    verify.require(ids == set(baseline) and len(report['rows']) == 124, 'diagnostic does not cover exact124 source IDs')
    verify.require(len(checked) == len({r['name'] for r in checked}) == 33, 'recognized companion count differs')
    verify.require(Counter(r['power_cost'] for r in checked) == {2: 2, 3: 31} and all(r['stable_length'] == 5 for r in checked), 'recorded short-companion distribution differs')
    result = {'status': 'PASS', 'source_rows': 124, 'fixed_donor_cases': checked,
              'read_only_validation': True, 'census_searches': 0, 'source_sha256': verify.sha(source),
              'proof_source': 'https://eprints.maths.manchester.ac.uk/991/1/OmskVestnik.pdf',
              'proof_source_scope': 'Section2.2 stable-length invariance and Theorem3.9 Collins conjugacy criterion; short-cost corollary is a separately audited deduction.',
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_fixed_donor.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'saved_rows': 124, 'recognized_companions': 33, 'power_cost_distribution': {2: 2, 3: 31}, 'census_searches': 0}, indent=2))


if __name__ == '__main__':
    main()
