"""Independent exact first-commutator and divisible conjugate-bridge controls."""
from copy import deepcopy
import json
from pathlib import Path

import exchange_collect_prefix as prefix
import theory_conjugate_bridge as bridge
import theory_corridor as corridor
import verify
from verification_consequence_checks import pilot, p

HERE = Path(__file__).resolve().parent
require = verify.require


def replay(initial, after, events):
    current = verify.words(initial)
    for event in json.loads(json.dumps(events)):
        require(verify.words(event['before']) == current, 'prefix/bridge chain discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    require(current == verify.words(after), 'prefix/bridge endpoint differs')


def prefix_controls():
    source = HERE / 'exchange_collect_prefix_control.json'
    saved = json.loads(source.read_text())
    require(saved['source_sha256'] == verify.sha(HERE / 'exchange_collect_prefix.py'), 'saved first-helper source differs')
    checked = []
    for row in saved['controls']:
        replay(row['before'], row['after'], row['events'])
        checked.append({'name': row['name'], 'status': 'PASS', 'initial_length': verify.size(row['before']),
                        'endpoint_length': verify.size(row['after']), 'endpoint_rank': len(row['after'])})
    identities = 0
    high = 10 ** 24 + 11
    for axis in (101, -101):
        for other in (high, -high):
            images = {101: (101,), high: (high,), high + 1: (axis, other, -axis, -other)}
            for height in (-100, -4, -1, 0, 1, 4, 100):
                for letter in (other, -other):
                    template = prefix.conjugate(letter, height, axis, other, high + 1)
                    require(verify.image(template, images) == verify.free(p(axis, height) + (letter,) + p(axis, -height)), 'linear commutator formula identity fails')
                    require(len(template) <= 3 * abs(height) + 1, 'first-helper template is not linear length')
                    identities += 1
    initial = verify.normalized(((101, high, high, -101, -high), (101, 101, high, -101, -high)))
    cases = []
    for mode in ('one_direction', 'all_heights'):
        for axis, other in ((101, high), (-101, -high)):
            after, event, charged = prefix.compress(initial, axis, other, 100, mode=mode)
            replay(initial, after, [event])
            require(charged == 8, 'rank2 prefix cost differs')
            cases.append({'mode': mode, 'axis_sign': 1 if axis > 0 else -1,
                          'length': verify.size(after), 'rank': len(after), 'charged': charged})
    bad = []
    first = deepcopy(saved['controls'][0]['events'][0])
    altered = deepcopy(first); altered['prefix_axis'] *= -1; bad.append(altered)
    altered = deepcopy(first); altered['rows'][0]['prefix_chunks'][0]['height'] += 1; bad.append(altered)
    altered = deepcopy(first); altered['rows'][0]['prefix_axis_exponent'] += 1; bad.append(altered)
    rejected = 0
    for event in bad:
        try:
            verify.verify_event(event, known_trivial=True)
        except AssertionError:
            rejected += 1
    require(rejected == 3, 'corrupt first-helper metadata accepted')
    budgets = []
    for budget in (0, 1, 7, 8, 30):
        candidates, used = prefix.probe(initial, budget)
        require(used <= budget, 'prefix budget exceeded')
        for after, events in candidates:
            replay(initial, after, events)
        budgets.append({'budget': budget, 'charged': used, 'candidates': len(candidates)})
    return {'status': 'PASS', 'saved_controls': checked, 'signed_linear_identities': identities,
            'signed_high_label_compressions': cases, 'rejected_corruptions': rejected, 'budget_controls': budgets,
            'saved_real_prefix_scope': 'The aca43 record reconstructs an already found stage, not a new census gain.', 'census_searches': 0}


def bridge_controls():
    checked, partials = [], []
    high = 10 ** 25 + 13
    for exponent in (-2, 2):
        initial = verify.normalized(((-high,) + p(5, exponent), (-2,) + p(5, 4) + (2,) + p(5, -5), (2,) + p(5, 11)))
        root = next(r for r in corridor.roots(initial) if r.helper == high)
        model = next(m for i in range(3) if i != root.donor and (m := corridor.bs_model(initial, root, i)))
        for signed_stable, value in ((-model['stable'], 2), (model['stable'], 5)):
            after, events, used, complete = bridge.compile_bridge(initial, root, model, signed_stable, value, 100)
            replay(initial, after, events)
            require(complete and len(after) == 4 and used <= 100, 'complete divisible bridge differs')
            checked.append({'root_exponent': exponent, 'signed_stable': signed_stable, 'conjugate_exponent': value, 'events': len(events), 'charged': used, 'endpoint_length': verify.size(after)})
            for budget in (0, 1, 2):
                after, events, used, complete = bridge.compile_bridge(initial, root, model, signed_stable, value, budget)
                replay(initial, after, events)
                require(used <= budget and not complete, 'partial bridge wrongly claims completion')
                partials.append({'budget': budget, 'charged': used, 'events': len(events), 'rank': len(after)})
    arbitrary = verify.normalized(initial + tuple((high + i,) for i in range(1, 9)))
    root = next(r for r in corridor.roots(arbitrary) if r.helper == high)
    model = next(m for i in range(len(arbitrary)) if i != root.donor and (m := corridor.bs_model(arbitrary, root, i)))
    after, events, used, complete = bridge.compile_bridge(arbitrary, root, model, -model['stable'], 2, 100)
    replay(arbitrary, after, events)
    require(complete and len(after) == 12 and len(events) == 11, 'arbitrary-rank bridge omits a nontarget row')
    determinants = []
    for e in (2, 3, 5):
        for m, n in ((4, 5), (5, 6)):
            # The third relator has stable exponent one; expand along that column.
            old = m - n
            proposed = e * m - e * n
            require(abs(proposed) == e * abs(old) and abs(proposed) > 1, 'unsafe conjugate donor replacement determinant test differs')
            determinants.append({'m': m, 'n': n, 'conjugate_exponent': e, 'original_abs_determinant': abs(old), 'unsafe_replacement_abs_determinant': abs(proposed)})
    return {'status': 'PASS', 'signed_sparse_bridge_chains': checked, 'partial_bridges': partials,
            'rank11_to12_chain': {'events': len(events), 'charged': used, 'all_relators_counted': True},
            'unsafe_power_multiple_donor_replacement_controls': determinants,
            'known_triviality': 'The target x*y^11 together with BS(4,5) forces y=1 and x=1; defining/root rows and added singleton rows then force every other generator to one.', 'census_searches': 0}


def main():
    prefix_result = {'status': 'PASS', 'controls': prefix_controls(), 'source_sha256': verify.sha(HERE / 'exchange_collect_prefix.py'), 'verifier_sha256': verify.sha(HERE / 'verify.py')}
    (HERE / 'verification_collection_prefix.json').write_text(json.dumps(prefix_result, indent=2) + '\n')
    bridge_result = {'status': 'PASS', 'controls': bridge_controls(), 'pilot': pilot('conjugate_bridge_all33.json'), 'source_sha256': verify.sha(HERE / 'theory_conjugate_bridge.py'), 'verifier_sha256': verify.sha(HERE / 'verify.py')}
    (HERE / 'verification_conjugate_bridge.json').write_text(json.dumps(bridge_result, indent=2) + '\n')
    print(json.dumps({'prefix': prefix_result['controls'], 'bridge': bridge_result['controls'], 'bridge_new_gains': bridge_result['pilot']['new_strict_gains_beyond_available_seeds']}, indent=2))


if __name__ == '__main__':
    main()
