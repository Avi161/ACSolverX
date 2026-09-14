"""Tiny independent abelianization-preserving donor surgeries."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import donor_commutators as surgery
import verify


HERE = Path(__file__).resolve().parent


def main():
    initial = verify.normalized(((2, 5), (5,)))
    records = []
    for target, sign, c in product((0, 1), (-1, 1), ((2,), (-5,), (2, 5, -2))):
        donor = 1 - target
        endpoint, event = surgery.replacement(initial, target, donor, sign, c)
        verify.require(verify.verify_event(json.loads(json.dumps(event))) == verify.words(endpoint), 'commutator surgery exact replay differs')
        d = initial[donor] if sign == 1 else verify.invert(initial[donor])
        correction = verify.invert(d) + verify.invert(c) + d + c
        verify.require(verify.free(initial[target] + correction) == verify.word(event['raw_target_after']), 'commutator defining identity differs')
        verify.require(all(sum((1 if x > 0 else -1) for x in correction if abs(x) == g) == 0 for g in (2, 5)), 'commutator correction has nonzero exponent')
        records.append(event)
    candidates, spent = surgery.probe(initial, 40)
    verify.require(spent <= 40, 'commutator tiny probe exceeds budget')
    for endpoint, events in candidates:
        current = initial
        for event in events:
            verify.require(verify.words(event['before']) == current, 'commutator/Whitehead chain discontinuity')
            current = verify.verify_event(event, known_trivial=True)
        verify.require(current == verify.words(endpoint), 'commutator/Whitehead endpoint differs')
    corrupted = deepcopy(records[0])
    corrupted['commutator_sign'] = True
    try:
        verify.verify_event(corrupted)
    except AssertionError:
        pass
    else:
        raise AssertionError('invalid commutator metadata accepted')
    result = {'status': 'PASS', 'exact_signed_surgeries': len(records), 'tiny_probe_units': spent,
              'tiny_probe_endpoints': len(candidates), 'signed_events': records,
              'known_triviality_proof': 'The plant (ab,b) has b=1 and then a=1.', 'census_searches': 0,
              'source_sha256': verify.sha(HERE / 'donor_commutators.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_commutators.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'exact_signed_surgeries': len(records), 'tiny_probe_units': spent, 'tiny_probe_endpoints': len(candidates)}, indent=2))


if __name__ == '__main__':
    main()
