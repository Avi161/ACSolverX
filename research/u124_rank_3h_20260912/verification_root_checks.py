"""Independent root identities and complete retained-row replay on tiny plants."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import exchange_root
import verify


HERE = Path(__file__).resolve().parent


def roots_oracle(value):
    value = verify.free(value)
    if not value:
        return []
    left, right = 0, len(value)
    while right - left > 1 and value[left] == -value[right - 1]:
        left += 1
        right -= 1
    core, frame = value[left:right], value[:left]
    result = []
    for power in range(2, len(core) + 1):
        if len(core) % power == 0:
            piece = core[:len(core) // power]
            if piece * power == core:
                result.append((frame + piece + verify.invert(frame), power))
    return result


def main():
    checked = 0
    values = {(), (2, 5, -2, -5)}
    for length in range(1, 4):
        for candidate in product((2, -2, 5, -5), repeat=length):
            if verify.free(candidate) != candidate:
                continue
            for power in (1, 2, 3, 4, 6):
                values.add(verify.free(candidate * power))
    for value in sorted(values):
        extracted = exchange_root.roots(value)
        verify.require(extracted == roots_oracle(value), 'root divisor or conjugation differs from independent literal-period oracle')
        for root, power in extracted:
            verify.require(verify.free(root * power) == value, 'extracted root does not multiply back')
        checked += 1
    initial = verify.normalized(((2, 5, 5, -2, -5), (2, 2, 5, -2, -5)))
    plans, discovery_charge = exchange_root.discover(initial, 333)
    plan = next(plan for plan in plans if plan['defining_word'] == (2, 5, -2, -5))
    after, event, charge = exchange_root.compile_plan(initial, plan, 150)
    verify.require(verify.verify_event(event, known_trivial=True) == verify.words(after), 'root event replay differs')
    verify.require(verify.verify_event(json.loads(json.dumps(event)), known_trivial=True) == verify.words(after), 'JSON root event replay differs')
    corruptions = []
    for key, value in [('root', (2,)), ('power', True), ('helper_sign', -event['root_template_witness']['helper_sign']), ('context_u', (5, 5)), ('isolatable_old_generators', [])]:
        altered = deepcopy(event)
        altered['root_template_witness'][key] = value
        if altered['root_template_witness'] != event['root_template_witness']:
            corruptions.append(altered)
    rejected = 0
    for altered in corruptions:
        try:
            verify.verify_event(altered, known_trivial=True)
        except AssertionError:
            rejected += 1
    verify.require(rejected == len(corruptions), 'corrupted root metadata accepted')
    high = verify.normalized(initial + tuple((10**20 + i,) for i in range(9)))
    high_plans, high_discovery_charge = exchange_root.discover(high, 333, contexts=((), (2,), (5,), (2, 5)))
    high_plan = next(plan for plan in high_plans if plan['defining_word'] == (2, 5, -2, -5))
    high_after, high_event, high_charge = exchange_root.compile_plan(high, high_plan, 200)
    verify.require(verify.verify_event(high_event, known_trivial=True) == verify.words(high_after), 'rank11 large-label root event differs')
    budgets = []
    for budget in (0, 1, 5, 17, 40):
        candidates, spent = exchange_root.probe(initial, budget)
        verify.require(spent <= budget, 'root probe exceeds small budget')
        for endpoint, events in candidates:
            current = initial
            for step in events:
                verify.require(verify.words(step['before']) == current, 'root probe discontinuity')
                current = verify.verify_event(step, known_trivial=True)
            verify.require(current == verify.words(endpoint), 'root probe endpoint differs')
        budgets.append({'budget': budget, 'spent': spent, 'endpoints': len(candidates)})
    result = {'status': 'PASS', 'word_power_cases': checked, 'rejected_corruptions': rejected,
              'known_triviality_proof': 'For (abbAB,aabAB), c=[a,b] gives cbc=1 and ac=1, whence c=a^-1, b=a^2 and c=[a,a^2]=1. Extra singleton generators do not change triviality.',
              'planted_event': event, 'planted_discovery_charge': discovery_charge, 'planted_compile_charge': charge,
              'high_rank_before': len(high), 'high_rank_after': len(high_after), 'high_helper': high_event['helpers'],
              'high_discovery_charge': high_discovery_charge, 'high_compile_charge': high_charge,
              'small_budgets': budgets, 'census_searches': 0,
              'root_source_sha256': verify.sha(HERE / 'exchange_root.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_root.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'word_power_cases', 'rejected_corruptions', 'high_rank_before', 'high_rank_after', 'small_budgets')}, indent=2))


if __name__ == '__main__':
    main()
