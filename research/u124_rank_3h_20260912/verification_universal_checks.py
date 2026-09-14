"""Small any-rank root-repacking and occurrence-prioritized peeling controls."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import rank_peeling
import theory_corridor as corridor
import universal_root_metric as universal
from verification_flow_exact_checks import packing_cost
from verification_preparer_checks import power
import verify


HERE = Path(__file__).resolve().parent


def replay(initial, endpoint, events):
    current = verify.words(initial)
    for event in json.loads(json.dumps(events)):
        verify.require(verify.words(event['before']) == current, 'universal/peeling path discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    verify.require(current == verify.words(endpoint), 'universal/peeling endpoint differs')


def packed_cost(core, base, exponent):
    total, i = 0, 0
    while i < len(core):
        if abs(core[i]) != base:
            total += 1
            i += 1
            continue
        count = 0
        while i < len(core) and abs(core[i]) == base:
            count += 1 if core[i] > 0 else -1
            i += 1
        total += packing_cost(count, exponent)
    return total


def main():
    compiled = []
    for old, new, rank in product((-4, 4), (-3, 3), (3, 11)):
        initial = verify.normalized(((-11,) + power(5, old), (2, 11), (5,)) + tuple((10**15 + i,) for i in range(rank - 3)))
        root = next(r for r in corridor.roots(initial) if r.helper == 11 and r.base == 5 and r.exponent == old)
        endpoint, events = universal.compile_metric(initial, root, new)
        replay(initial, endpoint, events)
        verify.require(len(events) == rank and len(endpoint) == rank, 'universal shear/repack omits a retained row')
        mapping = {abs(x): (abs(x),) for w in initial for x in w}
        mapping[root.helper] = power(root.base, old)
        predicted = abs(new) + 1 + sum(packed_cost(verify.independent.representative(verify.image(word, mapping)), root.base, new) for i, word in enumerate(initial) if i != root.donor)
        verify.require(verify.size(endpoint) == predicted, 'universal full-tuple prediction differs from independent packing cost')
        compiled.append({'rank': rank, 'old_exponent': old, 'new_exponent': new, 'length': predicted})
    initial = verify.normalized(((-3, 2, 2, 2, 2), (1, 3), (2,)))
    budgets = []
    for budget in (0, 1, 4, 100, 1000):
        audits = []
        candidates, charged = universal.probe(initial, budget, audits=audits)
        verify.require(charged <= budget, 'universal probe exceeds budget')
        for endpoint, events in candidates:
            replay(initial, endpoint, events)
            verify.require(verify.size(endpoint) <= verify.size(initial), 'universal candidate increases final length')
        for audit in audits:
            verify.require(audit['finite_denomination_ceiling'] == verify.size(initial) - audit['expanded_nonbase_letters'] - 1, 'universal finite denomination ceiling differs')
        budgets.append({'budget': budget, 'charged': charged, 'candidates': len(candidates)})
    saved = json.loads((HERE / 'rank_peeling_checks.json').read_text())
    verify.require(saved['source_sha256'] == verify.sha(HERE / 'rank_peeling.py'), 'saved peeling source changed')
    peeled = []
    for row in saved['rows']:
        events = row['events']
        initial = events[0]['before']
        replay(initial, (), events)
        verify.require(row['charged'] == row['rank'] == len(events) and row['final_length'] == 0, 'peeling terminal metrics differ')
        peeled.append({'rank': row['rank'], 'charged': row['charged'], 'status': 'PASS'})
    seed = verify.words(saved['rows'][-1]['events'][0]['before'])
    for budget in (0, 1, 3):
        endpoint, events, charged, complete = rank_peeling.descend(seed, budget)
        replay(seed, endpoint, events)
        verify.require(charged == budget and complete is False, 'truncated peeling completion or budget differs')
    endpoint, events, charged, complete = rank_peeling.descend((), 0)
    verify.require((endpoint, events, charged, complete) == ((), [], 0, True), 'empty peeling boundary differs')
    corrupted = deepcopy(saved['rows'][0]['events'][0])
    corrupted['occurrence_accounting']['generator_degree'] += 1
    try:
        verify.verify_event(corrupted, known_trivial=True)
    except AssertionError:
        pass
    else:
        raise AssertionError('incorrect peeling occurrence metadata accepted')
    result = {'status': 'PASS', 'known_triviality': 'All plants contain a base singleton, then helper/base definitions clear their partners; extra old generators are singletons. Peeling chains end in a singleton and clear backward.',
              'universal_signed_chains': compiled, 'universal_budget_controls': budgets,
              'saved_peeling_chains': peeled, 'peeling_truncated_controls': 3, 'empty_peeling_complete': True,
              'source_sha256': {name: verify.sha(HERE / name) for name in ('universal_root_metric.py', 'rank_peeling.py')},
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__)), 'census_searches': 0}
    (HERE / 'verification_universal_root_peeling.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'universal_signed_chains': len(compiled), 'universal_budgets': budgets, 'peeling_ranks': [row['rank'] for row in peeled]}, indent=2))


if __name__ == '__main__':
    main()
