"""Bounded exact minimal Whitehead orbits for the two ambiguous projections."""
from collections import deque
from itertools import permutations, product
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import plateau
import theory_projection_panel as panel
from theory_projection_panel import search, verify, whitehead

HERE = Path(__file__).resolve().parent


def relabel(words, mapping):
    backward = {abs(v): (g if v > 0 else -g,) for g, v in mapping.items()}
    forward = {g: (v,) for g, v in mapping.items()}
    raw = tuple(tuple(mapping[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words)
    after = search.normalize(raw)
    event = {'kind': 'generator_relabeling', 'before': words, 'after': after,
             'images': forward, 'inverse_images': backward, 'raw_after': raw}
    assert verify.verify_event(event, known_trivial=True) == after
    return after, event


def basis_key(words):
    ids = sorted({abs(x) for w in words for x in w})
    assert len(ids) == 2
    choices = []
    for perm in permutations((1, 2)):
        for signs in product((-1, 1), repeat=2):
            mapping = {g: perm[i] * signs[i] for i, g in enumerate(ids)}
            after, event = relabel(words, mapping)
            choices.append((after, event))
    return min(choices, key=lambda p: p[0])


def run(row, baseline, budget=1000):
    source = min((p for p in row['projections'] if p['endpoint_length'] == row['saved_rank2_length']),
                 key=lambda p: (verify.words(p['endpoint']), len(p['events'])))
    verify.verify_record(source, baseline)
    original, saved = verify.words(source['endpoint']), verify.words(row['saved_rank2_words'])
    cpu, wall = time.process_time(), time.perf_counter()
    start, start_events, cuts1, complete1 = whitehead.descend(original, budget)
    target, target_events, cuts2, complete2 = whitehead.descend(saved, budget - cuts1)
    assert complete1 and complete2 and start == original and target == saved
    start_key, initial_map = basis_key(start)
    target_key, target_map = basis_key(target)
    cuts, comparisons = cuts1 + cuts2, 16
    states, parents, queue, indices = [start_key], [(None, [])], deque([0]), {start_key: 0}
    found = 0 if start_key == target_key else None
    complete, stop = False, 'budget'
    expanded = 0
    while queue and found is None:
        if budget - cuts - comparisons < 12:
            break
        index = queue.popleft()
        neighbors, cost = plateau.neutral_whitehead(states[index], 12)
        cuts += cost
        assert cost == 12
        exhausted = False
        for neighbor, events in neighbors:
            assert search.length(neighbor) == search.length(start)
            if budget - cuts - comparisons < 8:
                exhausted = True
                break
            canonical, event = basis_key(neighbor)
            comparisons += 8
            if canonical not in indices:
                child = len(states)
                indices[canonical] = child
                states.append(canonical)
                parents.append((index, events + [event]))
                queue.append(child)
            if canonical == target_key:
                found = indices[canonical]
                break
        expanded += not exhausted
        if exhausted:
            break
    if found is not None:
        stop = 'explicit_Aut_return'
        complete = True
        tail, index = [], found
        while parents[index][0] is not None:
            parent, events = parents[index]
            tail[0:0] = events
            index = parent
        mapping = {int(g): int(word[0]) for g, word in target_map['inverse_images'].items()}
        returned, event = relabel(target_key, mapping)
        assert returned == saved
        proof_events = source['events'] + start_events + [initial_map] + tail + [event]
        proof = {key: source[key] for key in ('name', 'baseline_sha256', 'source_key', 'initial')}
        proof.update(events=proof_events, endpoint=saved)
        proof['verification'] = verify.verify_record(proof, baseline)
    else:
        proof = None
        if not queue and expanded == len(states):
            stop, complete = 'complete_minimal_orbit_disjoint', True
    return {'name': row['name'], 'projection_source': source,
        'saved_rank2_words': saved, 'source_minimum_length': search.length(start),
        'target_minimum_length': search.length(target), 'both_minima_complete': complete1 and complete2,
        'Aut_equivalent': found is not None if complete else None, 'complete': complete, 'stop': stop,
        'neutral_orbit_states': states, 'orbit_tree': parents, 'expanded_states': expanded,
        'pending_states': len(queue), 'return_certificate': proof,
        'costs': {'minimum_and_neutral_cuts': cuts, 'signed_permutation_checks': comparisons},
        'total_units': cuts + comparisons, 'budget': budget,
        'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall}


def main():
    destination = Path(__file__).with_suffix('.json')
    if destination.exists():
        raise ValueError('refusing to overwrite orbit diagnostic')
    source_file = HERE / 'theory_projection_panel.json'
    source = json.loads(source_file.read_text())
    selected = [row for row in source['projection_rows'] if row['name'] in ('aca_79', 'aca_80')]
    assert {r['name'] for r in selected} == {'aca_79', 'aca_80'}
    baseline = verify.load_baseline()
    rows = [run(row, baseline) for row in selected]
    report = {'module': 'theory_projection_orbit_check', 'script_sha256': verify.sha(Path(__file__)),
        'projection_panel_sha256': verify.sha(source_file), 'orbit_rows': rows,
        'summary': {'rows': 2, 'equivalent_ids': [r['name'] for r in rows if r['Aut_equivalent'] is True],
            'proved_distinct_minimal_orbit_ids': [r['name'] for r in rows if r['Aut_equivalent'] is False],
            'inconclusive_ids': [r['name'] for r in rows if r['Aut_equivalent'] is None],
            'total_units': sum(r['total_units'] for r in rows),
            'cpu_seconds': sum(r['cpu_seconds'] for r in rows)},
        'scope': 'Finite neutral Whitehead traversal modulo all8signed permutations of rank2. '
                 'Negative conclusions require both minimum checks and complete orbit closure; no AC-orbit claim. '
                 'Cuts and signed-permutation checks share1k per row; prior projections are imported, not rerun.'}
    destination.write_text(json.dumps(report, indent=2) + '\n')
    assert json.loads(destination.read_text())['summary'] == report['summary']
    print(json.dumps(report['summary'], indent=2))
    for row in rows:
        print(row['name'],row['stop'],'states',len(row['neutral_orbit_states']),'expanded',row['expanded_states'],
              'work',row['costs'])


if __name__ == '__main__':
    main()
