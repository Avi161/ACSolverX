"""Independent tiny proof-transport controls and replay of saved macro pilots."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import verify
import completion
import theory_corridor as corridor


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
require, word, words = verify.require, verify.word, verify.words
free, invert, normalized, size = verify.free, verify.invert, verify.normalized, verify.size


def evaluate(relators, factors, excluded=None):
    output = ()
    basis = {abs(x) for w in relators for x in w}
    for factor in factors:
        i, sign, c = factor['donor_index'], factor['sign'], word(factor['conjugator'])
        require(type(i) is int and 0 <= i < len(relators) and i != excluded, 'factor uses target or absent donor')
        require(type(sign) is int and sign in (-1, 1), 'invalid factor sign')
        require(all(abs(x) in basis for x in c), 'conjugator uses foreign generator')
        d = relators[i] if sign == 1 else invert(relators[i])
        output += invert(c) + d + c
    return free(output)


def completion_controls():
    relators = normalized(((2, 5, 2), (5, 2), (9, 2, 5, 2, -5, 2)))
    target = next(i for i, w in enumerate(relators) if 9 in map(abs, w))
    donor_indices = [i for i in range(len(relators)) if i != target]
    proof = [{'donor_index': donor_indices[0], 'sign': 1, 'conjugator': (2, -5)},
             {'donor_index': donor_indices[1], 'sign': -1, 'conjugator': (-2,)}]
    original = evaluate(relators, proof, target)
    require(evaluate(relators, completion.inverted(proof), target) == invert(original), 'completion inversion transport fails')
    suffix = (-5, 2, 2)
    require(evaluate(relators, completion.conjugated(proof, suffix), target) == free(invert(suffix) + original + suffix), 'completion conjugation transport fails')
    canon, canon_proof = completion.canonical_consequence(original, proof)
    require(canon == verify.independent.representative(original) == evaluate(relators, canon_proof, target), 'completion cyclic transport fails')
    orientations = 0
    for value, factors in completion.orientations(canon, canon_proof):
        require(word(value) == evaluate(relators, factors, target), 'completion signed rotation transport fails')
        orientations += 1
    library, charge = completion.library(relators, target, 48)
    maximum_width = 0
    for consequence, factors in library.items():
        require(word(consequence) == evaluate(relators, factors, target), 'critical-overlap consequence proof fails')
        maximum_width = max(maximum_width, len(factors))
    require(maximum_width >= 3, 'tiny completion did not exercise repeated derived compositions')
    candidates, applied = completion.apply_library(relators, target, library, 32)
    require(candidates, 'tiny completion did not exercise application of derived consequences')
    for after, events in candidates:
        current = relators
        for event in events:
            require(words(event['before']) == current, 'derived-rule path discontinuity')
            current = verify.verify_event(event, known_trivial=True)
        require(current == words(after), 'derived-rule endpoint differs')
    return {'status': 'PASS', 'signed_orientations_checked': orientations,
            'critical_overlap_evaluations': charge, 'consequences_checked': len(library),
            'largest_normal_product_width': maximum_width, 'matched_target_rule_evaluations': applied,
            'derived_target_endpoints_checked': len(candidates), 'census_searches': 0}


def p(g, e):
    return (g if e >= 0 else -g,) * abs(e)


def independently_shortest_power(e, root):
    limit = abs(e) + 2
    return min(abs(e - root.exponent * b) + abs(b) for b in range(-limit, limit + 1))


def corridor_controls():
    total_models, compiled, dp_cases, power_cases, helper_cases = 0, 0, 0, 0, 0
    for root_exponent in (-2, 2):
        relators = ((-11,) + p(2, root_exponent), (-5, 2, 5, -2, -2),
                    free((2, 2, 5, 2, 2, -5, -2, -2, -2, 5, 2, -2, -2)))
        verify.independent.check_tuple(relators)
        root = next(r for r in corridor.roots(relators) if r.donor == 0 and r.helper == 11 and r.base == 2)
        require(evaluate(relators, root.factors) == (-11,) + p(2, root_exponent), 'root isolation does not replay')
        for test_word in ((11, 5, -11, -2), (-11, -11, 5, 11, 2), (2, 11, -5, -11)):
            expanded, factors = corridor.expand_helper(test_word, root)
            expected = verify.image(test_word, {2: (2,), 5: (5,), 11: p(2, root_exponent)})
            require(word(expanded) == expected == free(test_word + evaluate(relators, factors)), 'signed helper expansion ledger fails')
            helper_cases += 1
        for e in range(-12, 13):
            chosen = corridor.shortest_power(e, root)
            require(verify.image(chosen, {2: (2,), 11: p(2, root_exponent)}) == p(2, e), 'shortest-power exponent differs')
            require(len(chosen) == independently_shortest_power(e, root), 'shortest-power length not minimal')
            power_cases += 1
        model = corridor.bs_model(relators, root, 1)
        require(model is not None and evaluate(relators, model['factors']) == word(model['relation']), 'BS donor proof transport fails')
        total_models += 1
        expanded, _ = corridor.expand_helper(relators[2], root)
        signs, exponents, frame = corridor._cyclic_corridor(expanded, root, model['stable'])
        require(free(frame + tuple(x for s, e in zip(signs, exponents) for x in ((s,) + p(2, e))) + invert(frame)) == expanded, 'cyclic corridor frame differs')
        for choices in product((-1, 0, 1), repeat=len(signs)):
            after, event = corridor.compile_flow(relators, 2, root, model, choices)
            require(verify.verify_event(event, known_trivial=True) == words(after), 'compiled simultaneous flow ledger fails')
            expected_exponents = []
            for i, exponent in enumerate(exponents):
                j = (i + 1) % len(signs)
                outgoing = model['n'] if signs[i] > 0 else model['m']
                incoming = model['m'] if signs[j] > 0 else model['n']
                expected_exponents.append(exponent - outgoing * choices[i] + incoming * choices[j])
            require(list(event['final_exponents']) == expected_exponents, 'simultaneous cyclic exponent formula differs')
            compiled += 1
        selected, charged = corridor._flow(signs, exponents, root, model, 1, 200)
        scores = []
        for choices in product((-1, 0, 1), repeat=len(signs)):
            transformed = [e - (model['n'] if signs[i] > 0 else model['m']) * choices[i]
                           + (model['m'] if signs[(i + 1) % len(signs)] > 0 else model['n']) * choices[(i + 1) % len(signs)]
                           for i, e in enumerate(exponents)]
            scores.append((sum(independently_shortest_power(e, root) for e in transformed), sum(map(abs, choices)), choices))
        require(tuple(selected) == min(scores)[2] and charged <= 200, 'cyclic DP does not minimize its stated finite objective')
        for available in (0, 1, charged - 1):
            partial, spent = corridor._flow(signs, exponents, root, model, 1, available)
            require(partial is None and spent == available, 'incomplete DP falsely claims completion')
        dp_cases += 1
    return {'status': 'PASS', 'known_triviality_proof': 'After the helper definition, the BS(1,2) donor and target reduce to y=a; then a=a² forces a=1, y=1, and the helper dies. Root sign does not alter this quotient.',
            'root_exponents_tested': [-2, 2], 'signed_helper_expansion_cases': helper_cases,
            'power_lengths_compared_with_exhaustive_coefficients': power_cases,
            'derived_BS_models_checked': total_models, 'simultaneous_flows_compiled': compiled,
            'finite_cyclic_DP_exhaustive_comparisons': dp_cases, 'incomplete_DP_controls': 3 * dp_cases,
            'census_searches': 0}


def pilot(filename):
    report = json.loads((HERE / filename).read_text())
    historical_verifier = None
    for path, expected in report['hashes'].items():
        actual = verify.sha(HERE.parent / path)
        if path.endswith('/verify.py'):
            historical_verifier = {'executed_sha256': expected, 'current_sha256': actual,
                                   'matches_current': actual == expected,
                                   'scope': 'Historical verifier hash retained; every saved event is checked again with current independent verifier.'}
        else:
            require(actual == expected, 'pilot source changed: ' + path)
    seeds = []
    historical_work = 0
    for path, expected in report['seed_hashes'].items():
        source_path = ROOT / path
        require(verify.sha(source_path) == expected, 'pilot seed changed')
        data = json.loads(source_path.read_text())
        seeds.extend(data['rows'])
        historical_work += data['summary']['total_units']
    baseline = verify.load_baseline()
    checked = []
    for row in report['rows']:
        result = verify.verify_record(row, baseline)
        require(row['input_length'] == result['baseline_length'] and row['best_length'] == result['endpoint_length'] and row['best_rank'] == result['endpoint_rank'] and row['gain'] == result['endpoint_gain'], 'pilot endpoint metrics differ')
        require(sum(row['costs'].values()) == row['total_units'] <= row['budget'] == 1000, 'pilot budget differs')
        seeded = [r for r in seeds if r['name'] == row['name']]
        for seed in seeded:
            verify.verify_record(seed, baseline)
        initial_best = min([baseline[row['name']]['length']] + [size(e['after']) for seed in seeded for e in seed['events']])
        new_gain = initial_best - row['best_length']
        require(new_gain == 0, 'unexpected new strict gain beyond imported seed')
        checked.append({'name': row['name'], 'status': 'PASS', 'length': row['best_length'], 'rank': row['best_rank'],
                        'gain_vs2180_baseline': row['gain'], 'preprobe_best_length_including_seeds': initial_best,
                        'new_gain_beyond_seeds': new_gain, 'new_probe_units': row['total_units'],
                        'retained_path_identical_to_imported_seed': any(row['events'] == seed['events'] and row['endpoint'] == seed['endpoint'] for seed in seeded)})
    summary = report['summary']
    require(len(checked) == len({r['name'] for r in checked}) == summary['rows'], 'pilot denominator differs')
    require(summary['gains'] == [r['name'] for r in report['rows'] if r['gain'] > 0], 'pilot gain list differs')
    require(summary['input_total'] == sum(r['input_length'] for r in report['rows']) and summary['best_total'] == sum(r['best_length'] for r in report['rows']) and summary['total_units'] == sum(r['total_units'] for r in report['rows']), 'pilot summary sums differ')
    return {'status': 'PASS', 'file': filename, 'sha256': verify.sha(HERE / filename), 'rows': checked,
            'new_probe_work_units': summary['total_units'], 'full_seed_files_historical_discovery_units': historical_work,
            'seed_work_included_in_new_probe_budget': False, 'new_strict_gains_beyond_available_seeds': 0,
            'historical_verifier_provenance': historical_verifier}


def main():
    completion_result = {'status': 'PASS', 'controls': completion_controls(), 'pilot': pilot('completion_pilot.json'),
                         'proof_scope': 'Every retained consequence is an explicit product of conjugates of nontarget donors; inversion reverses factor order and sign, conjugation appends to each conjugator. Repeated critical compositions preserve this invariant.',
                         'source_sha256': verify.sha(HERE / 'completion.py'), 'audit_script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_completion.json').write_text(json.dumps(completion_result, indent=2) + '\n')
    corridor_result = {'status': 'PASS', 'controls': corridor_controls(), 'pilot': pilot('corridor_pilot.json'),
                       'proof_scope': 'Independent exact normal-product replay for helper expansion, derived BS relations and all tested cyclic-flow choices; DP checked only for its finite separable exponent-packing objective.',
                       'source_sha256': verify.sha(HERE / 'theory_corridor.py'), 'audit_script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_corridor.json').write_text(json.dumps(corridor_result, indent=2) + '\n')
    print(json.dumps({'completion': completion_result['controls'], 'completion_new_gains': 0,
                      'corridor': corridor_result['controls'], 'corridor_new_gains': 0}, indent=2))


if __name__ == '__main__':
    main()
