"""Small algebraic controls for the retained two-sided stable spelling."""
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_stable_metric as metric
import theory_corridor as corridor
import verify
from search import length, normalize


def replay(words, after, events):
    cursor = words
    for event in json.loads(json.dumps(events)):
        assert verify.words(event['before']) == cursor
        cursor = verify.verify_event(event, known_trivial=True)
    assert cursor == after


def run():
    bit_checks = bit_patterns = compiled_checks = 0
    root = corridor.Root(-1, 3, 2, 2, [])
    for signs in ((1,), (-1,), (1, 1, -1), (-1, -1, 1),
                  (1, 1, 1, -1, -1), (-1, -1, -1, 1, 1)):
        exponents = [i % 3 - 1 for i in range(len(signs))]
        for left, right in ((-2, 4), (2, -4), (1, 3)):
            atom = metric.Atom(-1, 4, 1, left, right, (), [])
            brute = []
            for bits in product((0, 1), repeat=len(signs)):
                gaps = metric._adjust(signs, exponents, bits, left, right)
                brute.append((sum(len(corridor.shortest_power(e, root)) for e in gaps), bits))
                bit_patterns += 1
            assert metric._best_bits(signs, exponents, root, atom) == min(brute)
            bit_checks += 1
    for old in (-2, 2):
        words = normalize(((-3,) + corridor.power(2, old),
            (-1,) + corridor.power(2, 4) + (1,) + corridor.power(2, -5),
            (1,) + corridor.power(2, 11)))
        root = next(r for r in corridor.roots(words) if r.helper == 3)
        model = next(m for i in range(3) if i != root.donor
                     and (m := corridor.bs_model(words, root, i)))
        target = next(i for i in range(3) if i not in (root.donor, model['donor']))
        for left, right in ((0, -5), (-5, 0), (-2, 4), (2, -4), (3, 1), (-3, -1)):
            for q in (-1, 0, 1):
                after, events = metric.compile_metric(words, root, model, target, (q,), left, right)
                replay(words, after, events)
                compiled_checks += 1
    budgets = []
    for allowance in (0, 1, 2, 10, 100, 1000):
        candidates, used = metric.probe(words, allowance)
        assert 0 <= used <= allowance
        for after, events in candidates:
            replay(words, after, events)
            assert length(after) < length(words)
        budgets.append({'allowance': allowance, 'charged': used, 'strict_candidates': len(candidates)})
    zero_plant = normalize(((-3, 2, 2), (-1, 3, 2, 2, 1, -2, -2, -2, -2, -2), (1,)))
    audits = []
    candidates, used = metric.probe(zero_plant, 1000, audits=audits)
    for after, events in candidates:
        replay(zero_plant, after, events)
    zero = [a for a in audits if a.get('reason') == 'unique_rational_flow_solution']
    assert zero and any(a['found_flow'] is not None for a in zero)
    source = Path(metric.__file__)
    return {'status': 'PASS', 'module_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'independent_atom_patterns': bit_patterns, 'cycle_bit_optima': bit_checks,
        'compiled_signed_chains': compiled_checks, 'budget_controls': budgets,
        'zero_cost_controls': {'charged': used, 'rational_solves': len(zero),
                               'strict_candidates': len(candidates)},
        'known_triviality_proof': 'The first plant has x y^11; the second has x. Either forces BS(4,5) to give y=1, then the root donor gives z=1.',
        'scope': 'Mechanism and budget controls only, no census evaluation.'}


if __name__ == '__main__':
    result = run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
