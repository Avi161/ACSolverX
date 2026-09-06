"""Certified short-relator lookahead followed by a fixed search portfolio."""
from __future__ import annotations

from experiments.equivalence_classes.lib.words import canon_pair
from experiments.search.basis_moves import reduce_basis_key
from experiments.search.bs_collapse import bs_collapse
from experiments.search.heuristic_1k import NIELSEN, mixed_search, pack, unpack


def search(pair, *, budget=1000, cap=48, starter_budget=500, rewrite_budget=1000,
           intermediate_cap=256):
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= 100000:
        raise ValueError('Budget must be an integer in1..100000')
    if (cap is not None and (not isinstance(cap, int) or isinstance(cap, bool) or cap < 1)) \
            or not 0 <= starter_budget <= 10000 or not 1 <= rewrite_budget <= 10000:
        raise ValueError('Invalid search cap or component budget')
    if intermediate_cap is not None and (not isinstance(intermediate_cap, int)
            or isinstance(intermediate_cap, bool) or intermediate_cap < 1):
        raise ValueError('Invalid intermediate cap')
    pair = canon_pair(*pair)
    if cap is not None and max(map(len, pair)) > cap:
        raise ValueError('Reduced input exceeds search cap')
    attempts = []
    spent = 0
    best_state = list(pair)
    min_total = sum(map(len, pair))
    min_max = max(map(len, pair))
    max_seen = min_max

    def observe(states):
        nonlocal best_state, min_total, min_max, max_seen
        for state in states:
            total = sum(map(len, state))
            largest = max(map(len, state))
            max_seen = max(max_seen, largest)
            if (total, largest, tuple(state)) < (min_total, min_max, tuple(best_state)):
                best_state, min_total, min_max = list(state), total, largest

    def finish(record=None, winner=None):
        result = dict(solved=False, states=[], steps=[]) if record is None else dict(record)
        observe(result['states'])
        result.update(nodes_explored=spent, attempts=attempts, winner=winner,
                      max_certificate_relator_length=max((len(w) for state in result['states'] for w in state), default=0),
                      input_total_length=sum(map(len, pair)), best_state=best_state,
                      min_total_length_seen=min_total, min_max_relator_length_seen=min_max,
                      max_relator_length_seen=max_seen)
        assert 1 <= spent <= budget
        return result

    if all(len(word) == 1 for word in pair) and pair[0].lower() != pair[1].lower():
        spent = 1
        attempts.append(dict(component='terminal', nodes=1, solved=True))
        return finish(dict(solved=True, states=[list(pair)], steps=[]), 'terminal')

    # Each descent removes a letter; leave room for the final signed permutation and root.
    key, trace = reduce_basis_key(pack(pair)) if budget > sum(map(len, pair)) else (pack(pair), [])
    normalization_cost = len(trace)
    assert normalization_cost < budget
    spent += normalization_cost
    attempts.append(dict(component='normalization', nodes=normalization_cost,
                         image_applications=(8+sum(t['images'] in NIELSEN for t in trace))
                            if budget > sum(map(len, pair)) else 0, completed=True))
    normalized = unpack(key)
    observe([t['state'] for t in trace])
    if intermediate_cap is None or max((len(w) for t in trace for w in t['state']), default=0) <= intermediate_cap:
        allowance = min(rewrite_budget, budget-spent)
        macro = bs_collapse(normalized, budget=allowance, intermediate_cap=intermediate_cap)
        observe(macro['states'])
        spent += macro['nodes_explored']
        attempts.append(dict(component='rewrite', nodes=macro['nodes_explored'],
                             recognized=macro['recognized'], reason=macro['reason'],
                             max_intermediate_relator_length=macro['max_intermediate_relator_length']))
        if macro['solved']:
            states = [list(pair)] + [t['state'] for t in trace] + macro['states'][1:]
            steps = [{k:v for k,v in t.items() if k != 'state'} for t in trace] + macro['steps']
            assert len(steps)+1 == spent
            return finish(dict(solved=True, states=states, steps=steps), 'rewrite')
    for name, limit, kwargs in (
        ('s40_gen', starter_budget, dict(arm='aut_edges', s_weight=40.0, mk_weight=0.0, w_weight=0.0)),
        ('s20_mk2', budget, dict(arm='s20', s_weight=20.0, mk_weight=2.0, w_weight=0.0)),
    ):
        allowance = min(limit, budget-spent)
        if allowance <= 0:
            continue
        record = mixed_search(pair, budget=allowance, cap=cap, **kwargs)
        observe([record['best_state']])
        max_seen = max(max_seen, record['max_relator_length_seen'])
        spent += record['nodes_explored']
        attempts.append(dict(component=name, nodes=record['nodes_explored'], solved=record['solved'],
                             basis_evaluations=record['basis_evaluations']))
        if record['solved']:
            return finish(record, name)
    return finish()
