"""Independent rational inverse, finite-box enumeration and pinch replay."""
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

import verify
import theory_corridor as corridor
import theory_flow_exact as exact
from verification_consequence_checks import pilot, p


HERE = Path(__file__).resolve().parent
require = verify.require


def inverse_matrix(matrix):
    n = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        factor = rows[col][col]
        rows[col] = [x / factor for x in rows[col]]
        for i in range(n):
            if i != col:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def exponent_flow(signs, exponents, model, choices):
    a = [model['m'] if s > 0 else model['n'] for s in signs]
    b = [model['n'] if s > 0 else model['m'] for s in signs]
    return [e - b[i] * choices[i] + a[(i + 1) % len(signs)] * choices[(i + 1) % len(signs)] for i, e in enumerate(exponents)]


def packing_cost(e, exponent):
    return min(abs(e - exponent * q) + abs(q) for q in range(-abs(e) - 2, abs(e) + 3))


def controls():
    cases = [([5], [3], 1, 2, 2, 2), ([5, 5], [1, -1], 1, 2, 2, 1),
             ([5, -5, 5], [1, 0, -1], 1, 2, -2, 1),
             ([5, -5, 5], [0, 1, 0], 1, -2, 2, 1),
             ([5, 5], [1, 1], 2, 3, -2, 1), ([5], [0], 1, 2, 2, 1)]
    results, residue_checks, partial_found = [], 0, 0
    for signs, exponents, m, n, root_exponent, ceiling in cases:
        model = {'m': m, 'n': n}
        root = corridor.Root(0, 11, 2, root_exponent, [])
        count = len(signs)
        a = [m if s > 0 else n for s in signs]
        b = [n if s > 0 else m for s in signs]
        matrix = [[0 for _ in signs] for _ in signs]
        for i in range(count):
            matrix[i][i] -= b[i]
            matrix[i][(i + 1) % count] += a[(i + 1) % count]
        inverse = inverse_matrix(matrix)
        require(exact.inverse_flow_matrix(signs, model) == inverse and inverse is not None, 'closed inverse differs from Gaussian elimination')
        bounds = exact.flow_bounds(signs, exponents, root, model, ceiling)
        expected = [int(abs(sum(c * e for c, e in zip(row, exponents))) + max(1, abs(root_exponent)) * ceiling * max(map(abs, row))) for row in inverse]
        require(bounds == expected, 'finite flow bound formula differs')
        feasible, enumerated = [], 0
        for choices in product(*(range(-bound, bound + 1) for bound in bounds)):
            transformed = exponent_flow(signs, exponents, model, choices)
            cost = sum(packing_cost(e, root_exponent) for e in transformed)
            require(all(packing_cost(e, root_exponent) >= 0 for e in transformed), 'negative block cost')
            if cost <= ceiling:
                feasible.append((cost, sum(map(abs, choices)), choices))
                require(sum(map(abs, transformed)) <= max(1, abs(root_exponent)) * ceiling, 'cost-to-exponent bound fails')
            for i, sign in enumerate(signs):
                if signs[(i + 1) % count] == -sign:
                    divisor = n if sign > 0 else m
                    require((transformed[i] - exponents[i]) % divisor == 0, 'opposite-neighbor Britton residue not preserved')
                    residue_checks += 1
            enumerated += 1
        selected, charged, complete, metadata = exact.exact_flow(signs, exponents, root, model, ceiling, 1000)
        require(complete and charged <= 1000, 'tiny finite-box program unexpectedly incomplete')
        require((None if selected is None else tuple(selected)) == (min(feasible)[2] if feasible else None), 'exact sparse DP differs from exhaustive box')
        for available in sorted({0, 1, charged // 2, max(0, charged - 1)}):
            partial, spent, done, _ = exact.exact_flow(signs, exponents, root, model, ceiling, available)
            require(spent <= available and not done, 'truncated flow falsely reports complete')
            if partial is not None:
                require(sum(packing_cost(e, root_exponent) for e in exponent_flow(signs, exponents, model, partial)) <= ceiling, 'partial flow violates cost ceiling')
                partial_found += 1
        results.append({'stable_signs': signs, 'm': m, 'n': n, 'root_exponent': root_exponent,
                        'ceiling': ceiling, 'bounds': bounds, 'box_points_enumerated': enumerated,
                        'feasible_points': len(feasible), 'DP_charged_units': charged, 'status': 'PASS'})
    singular = exact.exact_flow([5, -5], [1, 1], corridor.Root(0, 11, 2, 2, []), {'m': 1, 'n': 2}, 2, 1000)
    require(singular[:3] == (None, 0, False) and singular[3]['reason'] == 'singular_flow_matrix', 'singular flow incorrectly claims completion')
    require(partial_found > 0, 'did not exercise retention of a valid incomplete flow')
    initial = verify.normalized(((-11, 2, 2), (-5, 2, 5, -2, -2),
                                verify.free((2, 2, 5, 2, 2, -5, -2, -2, -2, 5, 2, -2, -2))))
    root = next(r for r in corridor.roots(initial) if r.helper == 11 and r.base == 2)
    donor = next(i for i, w in enumerate(initial) if sum(abs(x) == 5 for x in w) == 2)
    target = next(i for i, w in enumerate(initial) if sum(abs(x) == 5 for x in w) == 3)
    model = corridor.bs_model(initial, root, donor)
    after, new_root, new_model, new_target, events, charged, complete = exact.pinch_prefix(initial, root, model, target, 20)
    current = initial
    for event in events:
        require(verify.words(event['before']) == current, 'pinch prefix discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    require(current == verify.words(after) and complete and events, 'pinch prefix replay incomplete')
    require(sum(abs(x) == model['stable'] for x in corridor.expand_helper(after[new_target], new_root)[0]) == 1, 'pinch prefix did not reach stable lengthone')
    zero = exact.pinch_prefix(initial, root, model, target, 0)
    require(zero[-1] is False and zero[-2] == 0 and zero[-3] == [], 'zero-budget pinch claims completion')
    return {'status': 'PASS', 'finite_boxes': results, 'opposite_neighbor_residue_checks': residue_checks,
            'valid_partial_flows_retained': partial_found, 'singular_matrix_marked_incomplete': True,
            'normalized_Britton_prefix_events': events, 'pinch_charged_units': charged,
            'zero_budget_pinch_marked_incomplete': True, 'census_searches': 0,
            'scope': 'Negative BS exponent tested algebraically; known-triviality assertion used only for the explicit BS(1,2) planted certificate.'}


def main():
    result = {'status': 'PASS', 'controls': controls(), 'pilot': pilot('flow_exact_pilot.json'),
              'source_sha256': verify.sha(HERE / 'theory_flow_exact.py'),
              'script_sha256': verify.sha(Path(__file__)), 'verifier_sha256': verify.sha(HERE / 'verify.py'),
              'completeness_scope': 'Complete only for the nonsingular finite cyclic-flow system and declared root-cost ceiling after a completed Britton prefix; not a global stable-AC or group geodesic optimum.'}
    (HERE / 'verification_flow_exact.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'finite_boxes': len(result['controls']['finite_boxes']),
                      'residue_checks': result['controls']['opposite_neighbor_residue_checks'],
                      'valid_partial_flows_retained': result['controls']['valid_partial_flows_retained'],
                      'new_pilot_gains': 0}, indent=2))


if __name__ == '__main__':
    main()
