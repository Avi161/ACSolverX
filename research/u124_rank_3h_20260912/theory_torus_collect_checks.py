"""Small independent word and optimization controls for full torus collection."""
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_central_pinch as central
import theory_torus_collect as torus
import theory_conjugate_exchange_torus as wrapper
import theory_conjugate_exchange_checks as exchange_checks
import verify
from search import normalize


def evaluate(words, factors):
    result = ()
    for f in factors:
        c, donor = tuple(f['conjugator']), words[f['donor_index']]
        result = verify.free(result + verify.invert(c) +
            (donor if f['sign'] > 0 else verify.invert(donor)) + c)
    return result


def replay(before, after, events):
    cursor = before
    for event in json.loads(json.dumps(events)):
        assert verify.words(event['before']) == cursor
        cursor = verify.verify_event(event, known_trivial=True)
    assert cursor == after


def planted(k=2, d=2, h=3, z=2):
    w = (h,) * d + (-z,) * d
    return normalize(((-z,) + w * k, (-h, -1, z, 1), (1,) + (z,) * (1 + d * k)))


def prepared(words, h=3, z=2, d=2):
    models, _ = central.models(words, 400)
    model = next(m for m in models if abs(m['base']) == abs(h) and abs(m['stable']) == abs(z)
                 and m['power'] == d)
    return torus.prepare(words, model, torus.Budget(1000))


def run():
    words = planted()
    model = prepared(words)
    enumeration, representatives = 0, {}
    for size in range(5):
        for letters in product((2, -2, 3, -3), repeat=size):
            budget = torus.Budget(1000)
            signature, normal, factors = torus.normal_form(letters, model, budget)
            assert verify.free(letters + evaluate(words, factors)) == normal
            packed = torus.shortest(signature, model, budget)
            again, endpoint, outgoing = torus.normal_form(packed, model, budget)
            assert again == signature and endpoint == normal
            assert verify.free(packed + evaluate(words, outgoing)) == normal
            assert len(packed) <= size
            if signature not in representatives or size < representatives[signature][0]:
                representatives[signature] = size, packed
            enumeration += 1
    for signature, (minimum, packed) in representatives.items():
        assert len(packed) == minimum
    convex_checks = 0
    for total in range(-5, 6):
        signature = total, ((model['base'], 1), (model['stable'], 2),
                            (model['base'], 1), (model['stable'], 3))
        packed = torus.shortest(signature, model, torus.Budget(1000))
        brute = min(torus._allocate([1, 1], 2, total - 2 * b)[0] +
                    torus._allocate([2, 3], 5, b)[0] for b in range(-20, 21))
        assert len(packed) == brute
        convex_checks += 1
    signed_chains = 0
    for k, d, h, z in product((1, 2), (2, 3), (-3, 3), (-2, 2)):
        source = planted(k, d, h, z)
        choices, used = torus.probe(source, 500)
        assert choices and used <= 500
        for after, events in choices:
            replay(source, after, events)
            assert verify.size(after) <= verify.size(source)
            for event in events:
                assert verify.verify_event(json.loads(json.dumps(event)), known_trivial=False) == verify.words(event['after'])
            signed_chains += 1
    budgets = []
    for allowance in (0, 1, 2, 10, 100, 1000):
        choices, used = torus.probe(words, allowance)
        assert 0 <= used <= allowance
        for after, events in choices:
            replay(words, after, events)
        budgets.append({'allowance': allowance, 'charged': used, 'candidates': len(choices)})
    ids = {1: 7, 2: 11, 3: 10 ** 25}
    sparse = normalize(tuple(tuple(ids[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words) + ((19,),))
    choices, used = torus.probe(sparse, 300)
    assert choices
    for after, events in choices:
        replay(sparse, after, events)
        assert len(after) == 4 and (-19,) in after
    sparse_control = {'rank': 4, 'maximum_generator': 10 ** 25, 'charged': used, 'candidates': len(choices)}
    wrapper_budgets = []
    original = exchange_checks.planted(2)
    for allowance in (0, 1, 2, 10, 100, 1000):
        choices, used = wrapper.probe(original, allowance)
        assert 0 <= used <= allowance
        for after, events in choices:
            replay(original, after, events)
        wrapper_budgets.append({'allowance': allowance, 'charged': used, 'candidates': len(choices)})
    return {'status': 'PASS', 'module_sha256': hashlib.sha256(Path(torus.__file__).read_bytes()).hexdigest(),
        'wrapper_sha256': hashlib.sha256(Path(wrapper.__file__).read_bytes()).hexdigest(),
        'exhaustive_words_through_length4': enumeration, 'distinct_normal_forms': len(representatives),
        'convex_minimum_checks': convex_checks, 'signed_replayed_chains': signed_chains,
        'budget_controls': budgets, 'sparse_control': sparse_control, 'wrapper_budget_controls': wrapper_budgets,
        'known_triviality_proof': 'With x z^n=1, the conjugate-root row gives h=z and D then gives z=1.',
        'scope': 'Exact retained-donor words and finite normal-form optimization controls; no census run.'}


if __name__ == '__main__':
    result = run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
