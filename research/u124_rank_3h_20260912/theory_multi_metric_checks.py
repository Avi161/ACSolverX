"""Tiny planted controls; this file performs no census evaluation."""
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_multi_metric as multi
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
    metric_checks = flow_checks = compiled_checks = 0
    for small, large in ((2, 3), (3, 7)):
        metric = multi.Metric(2, 4, 3, small, large)
        brute = {}
        for a, b, c in itertools.product(range(-3, 4), repeat=3):
            exponent, cost = a + small * b + large * c, abs(a) + abs(b) + abs(c)
            brute[exponent] = min(cost, brute.get(exponent, cost))
        for exponent in range(-6, 7):
            result = metric.spell(exponent)
            assert len(result) == brute[exponent]
            assert sum((1 if x > 0 else -1) * {2: 1, 4: small, 3: large}[abs(x)]
                       for x in result) == exponent
            metric_checks += 1
        for sign, m, n, exponent in ((1, 4, 5, 1), (-1, 4, 5, -2), (1, 4, -5, 3)):
            model = {'m': m, 'n': n}
            choices, used, complete, audit = multi._flow([sign], [exponent], metric, model, 3, 1000)
            assert complete and used <= 1000
            a, b = (m, n) if sign > 0 else (n, m)
            bound = audit['mathematically_sufficient_flow_bounds'][0]
            brute_cost = min(len(metric.spell(exponent + (a - b) * q))
                             for q in range(-bound, bound + 1))
            assert choices is not None
            assert len(metric.spell(exponent + (a - b) * choices[0])) == brute_cost
            flow_checks += 1
    for old in (-2, 2):
        words = normalize(((-3,) + corridor.power(2, old),
            (-1,) + corridor.power(2, 4) + (1,) + corridor.power(2, -5),
            (1,) + corridor.power(2, 11)))
        root = next(r for r in corridor.roots(words) if r.helper == 3)
        model = next(m for i in range(3) if i != root.donor
                     and (m := corridor.bs_model(words, root, i)))
        target = next(i for i in range(3) if i not in (root.donor, model['donor']))
        for small, large in ((2, 3), (2, 4), (3, 7)):
            for q in (-1, 0, 1):
                after, events = multi.compile_metric(words, root, model, target, (q,), small, large)
                replay(words, after, events)
                compiled_checks += 1
    budgets = []
    for allowance in (0, 1, 2, 10, 100, 1000):
        candidates, used = multi.probe(words, allowance)
        assert 0 <= used <= allowance
        for after, events in candidates:
            replay(words, after, events)
            assert length(after) < length(words)
        budgets.append({'allowance': allowance, 'charged': used, 'strict_candidates': len(candidates)})
    path = Path(multi.__file__)
    return {'status': 'PASS', 'module_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'independent_coin_coefficients_tested': 686, 'metric_checks': metric_checks,
        'flow_optima_checks': flow_checks, 'compiled_signed_chains': compiled_checks,
        'budget_controls': budgets,
        'known_triviality_proof': 'The companion x y^11 forces x=y^-11; BS(4,5) then forces y=1, hence x=z=1.',
        'scope': 'Planted mechanism and budget controls only; no census campaign.'}


if __name__ == '__main__':
    result = run()
    path = Path(__file__).with_suffix('.json')
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
