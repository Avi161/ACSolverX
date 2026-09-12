"""Independent conjugator cosets and opposite-sign template identities."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import exchange_conjugacy as conjugacy
import verify


HERE = Path(__file__).resolve().parent


def main():
    source = (11, 7, 7, -11)
    chosen = (13, 17, -13)
    target = verify.free(chosen + source + verify.invert(chosen))
    coset = conjugacy.conjugator_coset(source, target)
    verify.require(coset['centralizer_root'] == (11, 7, -11) and coset['centralizer_exponent'] == 2, 'noncyclic centralizer frame differs')
    signed_shifts = 0
    for shift in range(-3, 4):
        root = coset['centralizer_root']
        w = verify.free(coset['base_conjugator'] + (root if shift >= 0 else verify.invert(root)) * abs(shift))
        verify.require(verify.free(w + source + verify.invert(w)) == target, 'signed coset shift fails')
        signed_shifts += 1
    finite_conjugators = 0
    for source in ((2, 5), (2, 2), (2, 5, -2)):
        for length in range(3):
            for chosen in product((2, -2, 5, -5), repeat=length):
                if verify.free(chosen) != chosen:
                    continue
                target = verify.free(chosen + source + verify.invert(chosen))
                coset = conjugacy.conjugator_coset(source, target)
                verify.require(coset is not None, 'known conjugate rejected')
                base, root = coset['base_conjugator'], coset['centralizer_root']
                verify.require(verify.free(base + source + verify.invert(base)) == target, 'base does not conjugate source')
                difference = verify.free(verify.invert(base) + chosen)
                verify.require(any(difference == verify.free((root if k >= 0 else verify.invert(root)) * abs(k)) for k in range(-6, 7)), 'known conjugator is absent from stated coset')
                finite_conjugators += 1
    definition = (2, 5, -2, -5)
    verify.require(conjugacy.conjugator_coset(definition, verify.invert(definition)) is None, 'inverse commutator falsely conjugate')
    row = verify.free(definition + (2,) + verify.invert(definition) + (5,))
    initial = verify.normalized((row, (2,) + row))
    plans, discovery_charge = conjugacy.discover(initial, 500)
    plan = next(plan for plan in plans if plan['defining_word'] == definition)
    after, event, charge = conjugacy.compile_plan(initial, plan, 200)
    verify.require(verify.verify_event(event, known_trivial=True) == verify.words(after), 'opposite-sign complete tuple replay differs')
    verify.require(verify.verify_event(json.loads(json.dumps(event)), known_trivial=True) == verify.words(after), 'JSON conjugacy tuple replay differs')
    corruptions = []
    for key, value in [('base_conjugator', ()), ('centralizer_root', event['conjugacy_template_witness']['coset']['centralizer_root'] * 2), ('rotation_cut', True)]:
        altered = deepcopy(event)
        altered['conjugacy_template_witness']['coset'][key] = value
        corruptions.append(altered)
    for key, value in [('helper_sign', -event['conjugacy_template_witness']['helper_sign']), ('centralizer_shift', True), ('isolatable_old_generators', [])]:
        altered = deepcopy(event)
        altered['conjugacy_template_witness'][key] = value
        corruptions.append(altered)
    rejected = 0
    for altered in corruptions:
        try:
            verify.verify_event(altered, known_trivial=True)
        except AssertionError:
            rejected += 1
    verify.require(rejected == len(corruptions), 'corrupted conjugacy metadata accepted')
    result = {'status': 'PASS', 'known_triviality_proof': 'For R=[a,b] a [a,b]^-1 b, the pair (R,aR) first implies a=1, after which R=b; hence a=b=1.',
              'finite_known_conjugators_checked': finite_conjugators, 'noncyclic_signed_shifts_checked': signed_shifts,
              'rejected_corruptions': rejected, 'discovery_charge': discovery_charge, 'compile_charge': charge,
              'planted_event': event, 'endpoint': after, 'census_searches': 0,
              'source_sha256': verify.sha(HERE / 'exchange_conjugacy.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_conjugacy.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'finite_known_conjugators_checked', 'noncyclic_signed_shifts_checked', 'rejected_corruptions', 'discovery_charge', 'compile_charge')}, indent=2))


if __name__ == '__main__':
    main()
