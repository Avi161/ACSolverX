"""Independent commutator collection ledgers and dictionary-exchange controls."""
from copy import deepcopy
import json
from pathlib import Path

import verify
import exchange_collect as collect
import dictionary_exchange
from verification_consequence_checks import pilot, p

HERE = Path(__file__).resolve().parent
require = verify.require


def replay_collection(initial, events, *, allow_prefix=False):
    current = verify.words(initial)
    labels = [('original', i) for i in range(len(current))]
    definitions, rewrites, count, charged, forecast = None, None, 0, 0, 0
    for raw_event in events:
        event = json.loads(json.dumps(raw_event))
        require(verify.words(event['before']) == current, 'collection chain discontinuity')
        if event.get('method') == 'iterated_commutator_collection_stage':
            count += 1
            if definitions is None:
                definitions = [(g, verify.word(w)) for g, w in event['collection_definitions']]
                rewrites = event['collection_rewrites']
                forecast = event['work_counts'].get('collection_axis_forecasts', 0)
                first = event
            require(event['collection_stage'] == count and event['collection_stages'] == len(definitions), 'collection stage sequence differs')
            require((event['helpers'][0], verify.word(event['defining_words'][0])) == definitions[count - 1], 'collection planned definition differs')
            require([tuple(row['collection_row_label']) for row in event['rows']] == labels, 'collection labels lost through normalization')
            raw_labels = [('definition', event['helpers'][0])] + labels
            labels = [raw_labels[row['input_index']] for row in event['normalization']]
            charged += event['charged_units']
        current = verify.verify_event(event, known_trivial=True)
        if definitions is not None and count == len(definitions) and event.get('method') == 'iterated_commutator_collection_stage':
            for value, label in zip(current, labels):
                if label[0] == 'original':
                    require(value == verify.independent.representative(verify.word(rewrites[label[1]]['template'])), 'final collection template differs')
    require(definitions is not None and (allow_prefix or count == len(definitions)), 'collection stages incomplete')
    r, h = len(initial), count
    frames = 2 if first['collection_direction_policy'] == 'cheapest' else 1
    expected = 1 + 3 * verify.size(initial) * frames + sum(row['collection_swaps'] for row in rewrites) + r + h * (r + 1) + h * (h - 1) // 2 + forecast
    require(charged == expected, 'collection total construction work differs')
    return current, charged


def controls():
    saved_path = HERE / 'exchange_collect_control.json'
    saved = json.loads(saved_path.read_text())
    require(saved['source_sha256'] == verify.sha(HERE / 'exchange_collect.py'), 'collector saved source differs')
    saved_checks = []
    for row in saved['controls']:
        after, units = replay_collection(row['before'], row['events'])
        require(after == verify.words(row['after']), 'saved collector endpoint differs')
        saved_checks.append({'name': row['name'], 'status': 'PASS', 'endpoint_rank': len(after),
                             'endpoint_length': verify.size(after), 'dictionary_units_including_forecasts': units,
                             'full_probe_charged_units': row['charged_units'],
                             'maximum_certified_rank': max(len(e['after']) for e in row['events'])})
    high, axis = 10 ** 23 + 31, 101
    names, definitions, _ = collect.dictionary((axis, high), axis, {(1, high): 3, (-1, high): 3})
    images = {axis: (axis,), high: (high,)}
    for helper, definition in definitions:
        images[helper] = verify.image(definition, images)
    conjugate_checks = 0
    for height in range(-3, 4):
        for sign in (-1, 1):
            template = collect.conjugate_template(sign * high, height, names)
            require(verify.image(template, images) == verify.free(p(axis, height) + (sign * high,) + p(axis, -height)), 'signed commutator ladder identity differs')
            require(len(template) == 2 ** abs(height), 'collection silently truncates commutator depth')
            conjugate_checks += 1
    first_event = saved['controls'][0]['events'][0]
    bad = []
    altered = deepcopy(first_event)
    altered['collection_rewrites'][0]['letters_at_heights'][0][0] += 1
    bad.append(altered)
    altered = deepcopy(first_event)
    altered['collection_definitions'][0][1][0] *= -1
    bad.append(altered)
    altered = deepcopy(first_event)
    altered['collection_rewrites'][0]['conjugate_chunks'][0]['expanded'] = []
    bad.append(altered)
    altered = deepcopy(first_event)
    altered['collection_helper_names'][0][2] += 1
    bad.append(altered)
    rejected = 0
    for event in bad:
        try:
            verify.verify_event(event, known_trivial=True)
        except AssertionError:
            rejected += 1
    require(rejected == len(bad), 'corrupted collector metadata accepted')
    initial = verify.normalized(((2, 5, 5, -2, -5), (2, 2, 5, -2, -5)))
    framing = []
    for direction in ('left', 'right'):
        after, events, charged, _ = collect.build(initial, 2, 1000, direction=direction)
        require(replay_collection(initial, events)[0] == after, 'signed frame construction differs')
        framing.append({'direction': direction, 'rank': len(after), 'length': verify.size(after), 'charged': charged})
    high_depth = verify.normalized(((2, 5), (2,) * 100 + (5, 5) + (-2,) * 100 + (-5,)))
    denied = collect.build(high_depth, 2, 1000)
    require(denied[:3] == (None, [], 1), 'large-height collection lacks preflight')
    dictionary_initial = verify.normalized(((-11, 2, 5),) + initial)
    budget_checks = []
    for budget in (0, 1, 10, 100):
        candidates, used = dictionary_exchange.probe(dictionary_initial, budget)
        require(0 <= used <= budget, 'dictionary exchange budget exceeded')
        for after, events in candidates:
            current = dictionary_initial
            for event in json.loads(json.dumps(events)):
                require(verify.words(event['before']) == current, 'dictionary exchange discontinuity')
                current = verify.verify_event(event, known_trivial=True)
            require(current == after, 'dictionary exchange endpoint differs')
        budget_checks.append({'budget': budget, 'charged': used, 'candidates': len(candidates),
                              'best_length': min([verify.size(dictionary_initial)] + [verify.size(w) for w, _ in candidates])})
    return {'status': 'PASS', 'saved_control_replays': saved_checks,
            'signed_conjugate_checks': conjugate_checks, 'rejected_metadata_corruptions': rejected,
            'distinct_cyclic_frames': framing, 'high_depth_preflight_units': 1,
            'dictionary_exchange_budget_controls': budget_checks, 'census_searches': 0,
            'known_triviality': 'For the two-row plant put c=[x,y]; its rows give c y c=1 and x c=1, hence x=c^-1 and y=c^-2, so c=[x,y]=1. The dictionary plant additionally defines z=xy. The saved rank-four plant has x y=1 and [x^3,y]^2 y=1, forcing y=x=1 and then its other rows force the remaining generators to one.'}


def main():
    result = {'status': 'PASS', 'controls': controls(),
              'collector_pilot': pilot('collector_pilot.json'),
              'dictionary_exchange_pilot': pilot('dictionary_exchange_pilot.json'),
              'source_sha256': {n: verify.sha(HERE / n) for n in ('exchange_collect.py', 'dictionary_exchange.py')},
              'script_sha256': verify.sha(Path(__file__)), 'verifier_sha256': verify.sha(HERE / 'verify.py')}
    (HERE / 'verification_collection.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['controls'], indent=2))


if __name__ == '__main__':
    main()
