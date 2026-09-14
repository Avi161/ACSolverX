"""Signed, cyclic and budget controls for retained-donor central pinches."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_central_pinch as central
import theory_conjugate_exchange_central as wrapper
import theory_conjugate_exchange_checks as exchange_checks
import theory_corridor as corridor
import verify
from search import normalize


def replay(words, after, events):
    cursor = words
    for event in json.loads(json.dumps(events)):
        assert verify.words(event['before']) == cursor
        cursor = verify.verify_event(event, known_trivial=True)
    assert cursor == after


def evaluate(words, factors):
    result = ()
    for factor in factors:
        c = tuple(factor['conjugator'])
        donor = words[factor['donor_index']]
        result = verify.free(result + verify.invert(c) +
            (donor if factor['sign'] > 0 else verify.invert(donor)) + c)
    return result


def planted(k, h, z, j):
    w = (h, h, -z, -z)
    return normalize(((-z,) + w * k, (-h, -1, z, 1),
                      (1, z) + corridor.power(h, 2 * j) + (-z,) + corridor.power(h, -2 * j)))


def run():
    chains, consequences, cyclic = 0, 0, 0
    for k in (1, 2, 3):
        for h in (-3, 3):
            for z in (-2, 2):
                for j in (-2, -1, 1, 2):
                    words = planted(k, h, z, j)
                    models, used = central.models(words, 200)
                    selected = next(m for m in models if m['donor'] == next(
                        i for i, word in enumerate(words) if {abs(x) for x in word} == {2, 3})
                        and abs(m['base']) == 3 and abs(m['stable']) == 2 and m['power'] == 2)
                    assert evaluate(words, selected['factors']) == tuple(selected['relation'])
                    consequences += 1
                    target = next(i for i, word in enumerate(words) if sum(abs(x) == 1 for x in word) == 1)
                    after, event, cost = central.pinch_once(words, target, selected, 100)
                    assert event and cost <= 100 and verify.size(after) < verify.size(words)
                    replay(words, after, [event])
                    assert verify.verify_event(json.loads(json.dumps(event)), known_trivial=False) == after
                    assert (1,) in after or (-1,) in after
                    chains += 1
                    cyclic += tuple(event['raw_target_after']) not in ((1,), (-1,))
    budgets = []
    words = planted(2, 3, 2, -2)
    for allowance in (0, 1, 2, 10, 100, 1000):
        candidates, used = central.probe(words, allowance)
        assert 0 <= used <= allowance
        for after, events in candidates:
            replay(words, after, events)
        budgets.append({'allowance': allowance, 'charged': used, 'candidates': len(candidates)})
    ids = {1: 7, 2: 11, 3: 10 ** 25}
    sparse = normalize(tuple(tuple(ids[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words) + ((19,),))
    candidates, used = central.probe(sparse, 250)
    assert candidates and len(sparse) == 4
    for after, events in candidates:
        replay(sparse, after, events)
        assert len(after) == 4 and (-19,) in after
    sparse_count = len(candidates)
    wrapper_budgets = []
    original = exchange_checks.planted(2)
    for allowance in (0, 1, 2, 10, 100, 1000):
        candidates, charged = wrapper.probe(original, allowance)
        assert 0 <= charged <= allowance
        for after, events in candidates:
            replay(original, after, events)
        wrapper_budgets.append({'allowance': allowance, 'charged': charged, 'candidates': len(candidates)})
    original = normalize(((-3, 2, 2), (-1, 2, 2, 2, 2, 1, -2, -2, -2, -2, -2),
        (1, 3, -1, 3, 3, 1, -3, -1, -3, -3, 1)))
    candidates, charged = wrapper.probe(original, 1000)
    composed = []
    for after, events in candidates:
        replay(original, after, events)
        if any(event.get('macro') == 'retained_donor_central_power_pinch' for event in events):
            composed.append((after, events))
    assert composed
    return {'status': 'PASS', 'module_sha256': hashlib.sha256(Path(central.__file__).read_bytes()).hexdigest(),
        'wrapper_sha256': hashlib.sha256(Path(wrapper.__file__).read_bytes()).hexdigest(),
        'signed_consequences': consequences, 'signed_pinch_chains': chains,
        'nontrivial_cyclic_frames': cyclic, 'budget_controls': budgets,
        'arbitrary_rank_sparse_control': {'input_rank': 4, 'maximum_input_generator': 10 ** 25,
            'charged': used, 'candidates': sparse_count}, 'wrapper_budget_controls': wrapper_budgets,
        'positive_composition_control': {'charged': charged, 'central_chains': len(composed),
            'initial_length': verify.size(original), 'shortest_endpoint_length': min(verify.size(state) for state, _ in composed)},
        'known_triviality_proof': 'After the certified central pinch the companion is x; h=Xzx then gives h=z, and D gives z=1.',
        'scope': 'Exact certificate and bounded accounting controls, with no census evaluation.'}


if __name__ == '__main__':
    result = run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
