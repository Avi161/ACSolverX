"""Small exact controls for conjugate bridges followed by forced base exchange."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_conjugate_exchange as exchange
import theory_corridor as corridor
import verify
from search import normalize


def replay(words, after, events):
    cursor = words
    for event in json.loads(json.dumps(events)):
        assert verify.words(event['before']) == cursor
        cursor = verify.verify_event(event, known_trivial=True)
    assert cursor == after


def planted(k):
    return normalize(((-3,) + corridor.power(2, k),
        (-1,) + corridor.power(2, 2 * abs(k)) + (1,) + corridor.power(2, -2 * abs(k) - 1),
        (1,) + corridor.power(2, 11)))


def run():
    chains, forced, uphill, recompressed = 0, 0, 0, 0
    for k in (-4, -3, -2, 2, 3, 4):
        words = planted(k)
        root = next(r for r in corridor.roots(words) if r.helper == 3)
        model = next(m for i in range(3) if i != root.donor
                     and (m := corridor.bs_model(words, root, i)))
        candidates, used, audit = exchange.exchange_bridge(words, root, model,
            -model['stable'], abs(k), 300)
        assert used <= 300 and audit['base_pivots']
        for after, events in candidates:
            replay(words, after, events)
            chains += 1
            for i, event in enumerate(events):
                if event['kind'] == 'lemma11_removal' and event['generator'] == root.base:
                    forced += 1
                    uphill += event['length_change'] > 0
                    recompressed += any(tail['kind'] == 'defining_compression' for tail in events[i + 1:])
                    break
    assert forced and uphill and recompressed
    budgets = []
    words = planted(2)
    for allowance in (0, 1, 2, 10, 100, 1000):
        audits = []
        candidates, used = exchange.probe(words, allowance, audits=audits)
        assert 0 <= used <= allowance
        for after, events in candidates:
            replay(words, after, events)
        budgets.append({'allowance': allowance, 'charged': used, 'candidates': len(candidates)})
    ids = {1: 7, 2: 11, 3: 10 ** 25}
    sparse = normalize(tuple(tuple(ids[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words))
    candidates, used = exchange.probe(sparse, 250)
    for after, events in candidates:
        replay(sparse, after, events)
    original = tuple(tuple(w) for w in reversed(sparse))
    raw_candidates, raw_used = exchange.probe(original, 100)
    for after, events in raw_candidates:
        replay(original, after, events)
    assert raw_used <= 100
    source = Path(exchange.__file__)
    return {'status': 'PASS', 'module_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'signed_plants': 6, 'replayed_direct_chains': chains,
        'chains_with_forced_base_removal': forced, 'chains_with_uphill_base_removal': uphill,
        'chains_with_recompression_after_removal': recompressed, 'budget_controls': budgets,
        'sparse_control': {'maximum_input_generator': 10 ** 25, 'charged': used, 'candidates': len(candidates)},
        'unnormalized_input_control': {'charged': raw_used, 'candidates': len(raw_candidates)},
        'known_triviality_proof': 'x y^11=1 makes the consecutive BS donor imply y=1, then x=z=1.',
        'scope': 'Certificate and accounting controls only; no census evaluation.'}


if __name__ == '__main__':
    result = run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
