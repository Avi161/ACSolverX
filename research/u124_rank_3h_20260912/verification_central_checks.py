"""Independent exact consequence and circular correction controls."""
import copy
import json
from pathlib import Path

import verify as v
import theory_central_pinch as central
from verification_consequence_checks import pilot

HERE = Path(__file__).resolve().parent


def power(w, exponent):
    return (w if exponent >= 0 else v.invert(w)) * abs(exponent)


def evaluate(rows, factors):
    result = ()
    for factor in factors:
        donor = rows[factor['donor_index']]
        c = v.word(factor['conjugator'])
        result = v.free(result + v.invert(c) + (donor if factor['sign'] == 1 else v.invert(donor)) + c)
    return result


def main():
    chains, cyclic_frames, corrupted = [], 0, 0
    for h in (-10 ** 25, 10 ** 25):
        for z in (-11, 11):
            for exponent in (-2, 2):
                x = 7
                w = (h, h, -z, -z)
                rows = v.normalized(((-z,) + w * 2, (-h, -x, z, x),
                                     (x, z) + power((h,), 2 * exponent) + (-z,) + power((h,), -2 * exponent), (19,)))
                models, model_cost = central.models(rows, 160)
                model = next(m for m in models if abs(m['base']) == abs(h) and abs(m['stable']) == abs(z) and m['power'] == 2)
                consequence = evaluate(rows, model['factors'])
                expected = (-model['stable'],) + power((model['base'],), 2) + (model['stable'],) + power((model['base'],), -2)
                v.require(consequence == expected == v.word(model['relation']), 'central commutator consequence differs')
                target = next(i for i, row in enumerate(rows) if sum(abs(t) == x for t in row) == 1)
                after, event, pinch_cost = central.pinch_once(rows, target, model, 100)
                v.require(event is not None and len(after) == 4 and v.size(after) < v.size(rows), 'central pinch endpoint differs')
                v.require(v.verify_event(json.loads(json.dumps(event)), known_trivial=False) == after, 'ordinary central replay differs')
                v.require(all(f['donor_index'] != target for f in event['factors']), 'central pinch modifies its donor')
                cyclic_frames += len(event['raw_target_after']) != 1
                bad = copy.deepcopy(event)
                bad['factors'][0]['sign'] *= -1
                try:
                    v.verify_event(json.loads(json.dumps(bad)), known_trivial=False)
                except AssertionError:
                    corrupted += 1
                else:
                    raise AssertionError('wrong central donor sign was accepted')
                chains.append({'initial': rows, 'after': after, 'event': event, 'charged': model_cost + pinch_cost})
    budgets = []
    for allowance in (0, 1, 2, 10, 100):
        candidates, charged = central.probe(rows, allowance)
        v.require(0 <= charged <= allowance, 'central budget exceeded')
        for after, events in candidates:
            cursor = rows
            for event in json.loads(json.dumps(events)):
                v.require(v.words(event['before']) == cursor, 'central prefix discontinuity')
                cursor = v.verify_event(event, known_trivial=False)
            v.require(cursor == after, 'central endpoint differs')
        budgets.append({'allowance': allowance, 'charged': charged, 'candidates': len(candidates)})
    output = {'status': 'PASS', 'signed_sparse_rank4_chains': len(chains), 'nontrivial_cyclic_frames': cyclic_frames,
              'wrong_donor_sign_rejections': corrupted, 'chains': chains, 'budget_controls': budgets,
              'saved_pilot': pilot('central_exchange_all33.json'),
              'sources': {name: v.sha(HERE / name) for name in ('theory_central_pinch.py', 'theory_conjugate_exchange_central.py')},
              'scope': 'The central consequence and every emitted pinch are ordinary retained-donor products, checked with known_trivial=False. Stable steps in the saved composed pilot retain the inherited known-trivial lineage. No census rerun.'}
    (HERE / 'verification_central.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('status', 'signed_sparse_rank4_chains', 'nontrivial_cyclic_frames', 'wrong_donor_sign_rejections')}))


if __name__ == '__main__':
    main()
