"""Independent virtual-donor deletion ledgers and saved pilot checks."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import donor_relative
import exchange_v2_geodesic as geodesic
import verification_consequence_checks as previous_checks
import verify


HERE = Path(__file__).resolve().parent


def main():
    a, b = 2, 5
    initial = verify.normalized(((a,), (b, a, b, a, -b, a)))
    target = next(i for i, w in enumerate(initial) if b in map(abs, w))
    donor = 1 - target
    engine = donor_relative.RelativeDictionary((a, b), {11: initial[donor]})
    meter = geodesic.Meter(1000)
    engine.saturate(meter)
    tokens, complete = engine.shortest(initial[target], meter)
    verify.require(complete and engine.token_cost(tokens)[0] == 3, 'relative geodesic control differs')
    images = {a: (a,), b: (b,), 11: initial[donor]}
    exhaustive = []
    choices = [tuple(token for token in (a, -a, b, -b, 11, -11) if verify.image((token,), images) == (letter,)) for letter in initial[target]]
    for candidate in product(*choices):
        exhaustive.append((sum(abs(x) in (a, b) for x in candidate), len(candidate)))
    verify.require(engine.token_cost(tokens) == min(exhaustive), 'relative objective differs from tiny exhaustive control')
    metadata = {'relative_objective': 'old_letter_token_count_then_total_token_count',
                'relative_template_cost': engine.token_cost(tokens), 'complete_fixed_dictionary_geodesic': complete,
                'saturation_complete': engine.saturation_complete, 'work_counts': dict(meter.counts), 'charged_units': meter.used}
    endpoint, event = donor_relative.compile_template(initial, target, engine, tokens, {11: donor}, metadata)
    verify.require(verify.verify_event(event) == verify.words(endpoint), 'relative ordinary event failed')
    verify.require(len(event['raw_target_after']) == 1, 'deletion did not expose additional free cancellation')
    verify.require(engine.token_cost(tokens)[0] > len(event['raw_target_after']), 'objective distinction was not exercised')
    c = 10**25
    high = verify.normalized(((a,), (b,), (c, a, -c, b, c)))
    target = next(i for i, w in enumerate(high) if c in map(abs, w))
    donors = {c + 1 + j: i for j, i in enumerate(i for i in range(3) if i != target)}
    engine = donor_relative.RelativeDictionary((a, b, c), {g: high[i] for g, i in donors.items()})
    signed_tokens = {high[i][0]: g for g, i in donors.items()}
    signed_tokens.update({-letter: -token for letter, token in list(signed_tokens.items())})
    tokens = tuple(signed_tokens.get(x, x) for x in high[target])
    metadata = {'relative_objective': 'old_letter_token_count_then_total_token_count',
                'relative_template_cost': engine.token_cost(tokens), 'complete_fixed_dictionary_geodesic': False,
                'saturation_complete': False, 'work_counts': {'manual_template_check': 1}, 'charged_units': 1}
    high_endpoint, high_event = donor_relative.compile_template(high, target, engine, tokens, donors, metadata)
    verify.require(verify.verify_event(json.loads(json.dumps(high_event))) == verify.words(high_endpoint), 'multiple retained donors/large IDs failed')
    corruptions = []
    altered = deepcopy(event)
    altered['factors'][0]['sign'] *= -1
    corruptions.append(altered)
    altered = deepcopy(event)
    altered['factors'][0]['conjugator'] = ()
    corruptions.append(altered)
    altered = deepcopy(event)
    altered['relative_template_cost'] = (0, 0)
    corruptions.append(altered)
    altered = deepcopy(event)
    altered['virtual_token_images'][11] = (b,)
    corruptions.append(altered)
    rejected = 0
    for altered in corruptions:
        try:
            verify.verify_event(altered)
        except AssertionError:
            rejected += 1
    verify.require(rejected == len(corruptions), 'corrupted relative ledger accepted')
    pilot = previous_checks.pilot('donor_relative_pilot.json')
    result = {'status': 'PASS', 'known_triviality_proof': 'The first plant has donor a=1, after which b a b a b^-1 a=b. The second has singleton a,b and then its companion reduces to c.',
              'objective_cost_before_deletion': event['relative_template_cost'], 'raw_target_length_after_deletion': len(event['raw_target_after']),
              'complete_fixed_dictionary': complete, 'tiny_geodesic_units': meter.used, 'exact_spelling_choices_checked': len(exhaustive),
              'global_control_optimality': 'Every token image is one letter, so exact expansion needs at least six tokens and at least the three surviving b letters. The returned (3,6) attains both lower bounds.',
              'ordinary_event': event, 'large_label_multiple_donor_event': high_event, 'rejected_corruptions': rejected,
              'pilot': pilot, 'census_searches': 0, 'source_sha256': verify.sha(HERE / 'donor_relative.py'),
              'geodesic_source_sha256': verify.sha(HERE / 'exchange_v2_geodesic.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_donor_relative.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'objective_cost': result['objective_cost_before_deletion'], 'target_after_deletion': 1,
                      'rejected_corruptions': rejected, 'pilot_rows': len(pilot['rows']), 'new_pilot_gains': 0}, indent=2))


if __name__ == '__main__':
    main()
