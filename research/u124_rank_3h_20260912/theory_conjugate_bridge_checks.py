"""Small signed and sparse controls for divisible conjugate-base bridges."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_conjugate_bridge as bridge
import theory_corridor as corridor
import verify
from search import normalize


def replay(words, after, events):
    cursor = words
    for event in json.loads(json.dumps(events)):
        assert verify.words(event['before']) == cursor
        cursor = verify.verify_event(event, known_trivial=True)
    assert cursor == after


def run():
    signed_checks = 0
    for old in (-2, 2):
        words = normalize(((-3,) + corridor.power(2, old),
            (-1,) + corridor.power(2, 4) + (1,) + corridor.power(2, -5),
            (1,) + corridor.power(2, 11)))
        root = next(r for r in corridor.roots(words) if r.helper == 3)
        model = next(m for i in range(3) if i != root.donor
                     and (m := corridor.bs_model(words, root, i)))
        for signed, dividend in ((-model['stable'], model['m']), (model['stable'], model['n'])):
            for exponent in range(1, abs(dividend) + 1):
                if dividend % exponent:
                    continue
                after, events, used, complete = bridge.compile_bridge(words, root, model, signed, exponent, 100)
                assert complete and used <= 100
                replay(words, after, events)
                signed_checks += 1
    budgets = []
    for allowance in (0, 1, 2, 10, 100, 1000):
        candidates, used = bridge.probe(words, allowance)
        assert 0 <= used <= allowance
        for after, events in candidates:
            replay(words, after, events)
        budgets.append({'allowance': allowance, 'charged': used, 'candidates': len(candidates)})
    ids = {1: 7, 2: 11, 3: 10 ** 25}
    sparse = normalize(tuple(tuple(ids[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words))
    candidates, used = bridge.probe(sparse, 200)
    for after, events in candidates:
        replay(sparse, after, events)
    source = Path(bridge.__file__)
    return {'status': 'PASS', 'module_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'signed_divisible_chains': signed_checks, 'budget_controls': budgets,
        'sparse_control': {'maximum_input_generator': 10 ** 25, 'charged': used, 'candidates': len(candidates)},
        'known_triviality_proof': 'The companion x y^11 turns BS(4,5) into y=1, forcing x=z=1.',
        'scope': 'Planted certificates and budgets only; no census evaluation.'}


if __name__ == '__main__':
    result = run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
