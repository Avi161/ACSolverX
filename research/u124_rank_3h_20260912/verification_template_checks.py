"""Tiny independent controls for the cancellation-aware defining-template ledger."""
from copy import deepcopy
import json
from pathlib import Path

import verify
import exchange_templates
import lemma11


HERE = Path(__file__).resolve().parent


def main():
    initial = verify.normalized(((2, 5, 5, -2, -5), (2, 2, 5, -2, -5)))
    definition = (2, 5, -2, -5)
    after, event, charged = exchange_templates.compress_dictionary(initial, (definition,), 200)
    verify.require(event is not None, 'planted dictionary construction failed')
    verify.require(verify.verify_event(event, known_trivial=True) == verify.words(after), 'planted dictionary replay failed')
    path = [event]
    current = after
    for pivot in (2, 5, event['helpers'][0]):
        choices = [(len(w), i) for i, w in enumerate(current) if sum(abs(x) == pivot for x in w) == 1]
        verify.require(choices, 'planted elimination pivot missing')
        _, index = min(choices)
        current, removal = lemma11.remove_one(current, index, pivot)
        verify.require(verify.verify_event(removal, known_trivial=True) == verify.words(current), 'planted removal replay failed')
        path.append(removal)
    verify.require(current == (), 'planted exchange did not reach empty presentation')
    corruptions = []
    altered = deepcopy(event)
    altered['rows'][0]['expanded'] = (2,)
    corruptions.append(altered)
    altered = deepcopy(event)
    altered['rows'] = altered['rows'][1:]
    corruptions.append(altered)
    altered = deepcopy(event)
    altered['defining_relators'] = ()
    corruptions.append(altered)
    altered = deepcopy(event)
    altered['rows'][0]['sign'] = True
    corruptions.append(altered)
    rejected = 0
    for altered in corruptions:
        try:
            verify.verify_event(altered, known_trivial=True)
        except AssertionError:
            rejected += 1
    verify.require(rejected == len(corruptions), 'corrupted template accepted')
    two_seed = verify.normalized(((2,), (5,), (11, 2, 5, -2)))
    two_after, two_event, two_charge = exchange_templates.compress_dictionary(two_seed, ((2, 5), (5, -11)), 200)
    verify.require(verify.verify_event(two_event, known_trivial=True) == verify.words(two_after), 'two-definition high-label replay failed')
    verify.require(two_event['helpers'] == (12, 13), 'fresh nonconsecutive high helpers differ')
    result = {'status': 'PASS', 'known_triviality_proof': 'For P=(abbAB,aabAB), setting c=[a,b] gives cbc=1 and ac=1, hence c=a^-1, b=a^2, and c=[a,a^2]=1. The second plant has singleton2 and5, then generator11.',
              'planted_initial': initial, 'planted_solution_events': path,
              'solution_endpoint': current, 'first_dictionary_charged_units': charged,
              'two_definition_high_labels': two_event['helpers'], 'two_definition_charged_units': two_charge,
              'two_definition_event': two_event, 'rejected_corruptions': rejected,
              'ordinary_elementary_expansion_emitted': False, 'census_searches': 0,
              'source_sha256': verify.sha(HERE / 'exchange_templates.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_templates.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'planted_solution_endpoint': current,
                      'two_definition_helpers': two_event['helpers'], 'rejected_corruptions': rejected}, indent=2))


if __name__ == '__main__':
    main()
