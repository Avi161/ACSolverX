"""Exact CURRENT winner projections: one-occurrence removal, Aut descent, peeling."""
from itertools import permutations, product
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import rank_peeling
from rank_peeling import lemma11, search
import verify
import whitehead

HERE = Path(__file__).resolve().parent
EXPECTED = {'aca_' + str(i) for i in (5, 43, 44, 56, 67, 72, 75, 79, 80, 83, 84, 87, 88, 95, 99, 101, 106, 111)}


def seed(source, baseline, hashes):
    source_file = HERE / source['witness_file']
    hashes[source['witness_file']] = verify.sha(source_file)
    witness = json.loads(source_file.read_text())['rows'][int(source['witness_pointer'].split('/')[-1])]
    assert witness['name'] == source['name']
    events = witness['events'][:source['witness_prefix_events']]
    record = {'name': source['name'], 'baseline_sha256': baseline[source['name']]['baseline_sha256'],
              'source_key': witness['source_key'], 'initial': witness['initial'], 'events': events,
              'endpoint': events[-1]['after'] if events else witness['initial']}
    checked = verify.verify_record(record, baseline)
    state = verify.words(checked['endpoint'])
    assert state == verify.words(source['words']) and len(state) == 3
    assert search.length(state) == source['best_length']
    return state, record


def cleanup(words, remaining):
    current, events, cuts, pivots, complete = words, [], 0, 0, False
    while cuts + pivots < remaining:
        old = current
        current, tail, cost, aut_complete = whitehead.descend(current, remaining - cuts - pivots)
        cuts += cost
        events += tail
        current, tail, cost, peel_complete = rank_peeling.descend(current, remaining - cuts - pivots)
        pivots += cost
        events += tail
        if current == old and aut_complete and peel_complete:
            complete = True
            break
    return current, events, cuts, pivots, complete


def signed_return(words, saved, remaining):
    source_ids = sorted({abs(x) for w in words for x in w})
    saved_ids = sorted({abs(x) for w in saved for x in w})
    if len(source_ids) != 2 or len(saved_ids) != 2:
        return None, 0
    used = 0
    for perm in permutations(saved_ids):
        for signs in product((-1, 1), repeat=2):
            if used == remaining:
                return None, used
            used += 1
            mapping = {g: perm[i] * signs[i] for i, g in enumerate(source_ids)}
            after = search.normalize(tuple(tuple(mapping[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words))
            if after == saved:
                return mapping, used
    return None, used


def project_row(source, baseline, hashes, budget=1000):
    state, imported = seed(source, baseline, hashes)
    name = source['name']
    saved = search.normalize(baseline[name]['sources']['saved_rank2'])
    assert search.length(saved) == source['saved_rank2_length']
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    cuts = pivots = comparisons = 0
    choices, projections, cache = rank_peeling.pivots(state), [], {}
    for bound, degree, donor_length, donor, generator in choices:
        used = cuts + pivots + comparisons
        if used == budget:
            break
        removed, event = lemma11.remove_one(state, donor, generator)
        pivots += 1
        reused = removed in cache
        if reused:
            endpoint, tail, complete = cache[removed]
            extra_cuts = extra_pivots = 0
        else:
            endpoint, tail, extra_cuts, extra_pivots, complete = cleanup(removed, budget - cuts - pivots - comparisons)
            cache[removed] = endpoint, tail, complete
            cuts += extra_cuts
            pivots += extra_pivots
        mapping, extra_comparisons = signed_return(endpoint, saved, budget - cuts - pivots - comparisons)
        comparisons += extra_comparisons
        path = imported['events'] + [event] + tail
        projection = {**imported, 'events': path, 'endpoint': endpoint,
            'endpoint_length': search.length(endpoint), 'endpoint_rank': len(endpoint),
            'pivot': {'donor_index': donor, 'generator': generator, 'degree': degree,
                      'donor_length': donor_length, 'literal_length_change_upper_bound': bound},
            'raw_removed_length': search.length(removed), 'raw_removed_words': removed,
            'closure_complete': complete, 'rank2_aut_minimum_certified': complete and len(endpoint) == 2,
            'saved_rank2_length': source['saved_rank2_length'], 'any_rank_incumbent_length': source['best_length'],
            'rank2_gain_vs_saved': source['saved_rank2_length'] - search.length(endpoint) if len(endpoint) == 2 else None,
            'gain_vs_any_rank_incumbent': source['best_length'] - search.length(endpoint),
            'exact_saved_rank2_signed_permutation': mapping, 'cleanup_reused_from_same_raw_tuple': reused,
            'new_work': {'pivot': 1, 'minimum_cuts': extra_cuts, 'cleanup_pivots': extra_pivots,
                         'signed_permutation_comparisons': extra_comparisons},
            'seed_event_count': len(imported['events'])}
        projection['verification'] = verify.verify_record(projection, baseline)
        projections.append(projection)
    if projections:
        best = min(projections, key=lambda r: (r['endpoint_length'], r['endpoint_rank'], verify.words(r['endpoint'])))
        output = {key: best[key] for key in ('name', 'baseline_sha256', 'source_key', 'initial', 'events', 'endpoint')}
    else:
        output = dict(imported)
    output.update({'input_length': baseline[name]['length'], 'seed_length': source['best_length'],
        'best_length': search.length(verify.words(output['endpoint'])), 'best_rank': len(output['endpoint']),
        'saved_rank2_length': source['saved_rank2_length'], 'saved_rank2_words': saved,
        'current_witness_file': source['witness_file'], 'current_witness_pointer': source['witness_pointer'],
        'current_witness_prefix_events': source['witness_prefix_events'],
        'input_pivots': len(choices), 'attempted_projections': len(projections),
        'all_input_pivots_attempted': len(projections) == len(choices),
        'all_projection_closures_complete': all(p['closure_complete'] for p in projections),
        'skip_reason': 'no one-occurrence donor in the exact current tuple' if not choices else None,
        'projections': projections, 'costs': {'minimum_cuts': cuts, 'pivot_attempts': pivots,
                                           'signed_permutation_comparisons': comparisons},
        'total_units': cuts + pivots + comparisons, 'budget': budget,
        'cpu_seconds': time.process_time() - start_cpu, 'wall_seconds': time.perf_counter() - start_wall,
        'certificate_kind': 'theorem_backed_stable_composite', 'fully_expanded_stable_certificate': False})
    assert output['total_units'] <= budget
    output['verification'] = verify.verify_record(output, baseline)
    return output


def main():
    destination = Path(__file__).with_suffix('.json')
    if destination.exists():
        raise ValueError('refusing to overwrite the projection panel')
    table_file = HERE / 'CURRENT.json'
    table_bytes = table_file.read_bytes()
    table = json.loads(table_bytes)
    selected = [r for r in table['rows'] if r['phase_gain'] > 0 and r['best_rank'] == 3]
    assert {r['name'] for r in selected} == EXPECTED and len(selected) == 18
    baseline, hashes, rows = verify.load_baseline(), {}, []
    for source in selected:
        row = project_row(source, baseline, hashes)
        rows.append(row)
        print(source['name'], 'projections', row['attempted_projections'], 'best rank/length',
              row['best_rank'], row['best_length'], 'saved', row['saved_rank2_length'],
              'units', row['total_units'], flush=True)
        time.sleep(0.05)
    report = {'module': 'theory_projection_panel', 'script_sha256': verify.sha(Path(__file__)),
        'current_sha256': __import__('hashlib').sha256(table_bytes).hexdigest(),
        'current_summary_at_snapshot': table['summary'], 'source_hashes': hashes,
        'selected_ids': [r['name'] for r in selected], 'projection_rows': rows,
        'summary': {'rows': len(rows), 'projections': sum(r['attempted_projections'] for r in rows),
            'all_input_pivots_attempted': all(r['all_input_pivots_attempted'] for r in rows),
            'all_closures_complete': all(r['all_projection_closures_complete'] for r in rows),
            'new_rank2_gain_ids': [r['name'] for r in rows if any(p['rank2_aut_minimum_certified'] and
                p['rank2_gain_vs_saved'] > 0 for p in r['projections'])],
            'new_any_rank_gain_ids': [r['name'] for r in rows if any(p['gain_vs_any_rank_incumbent'] > 0 for p in r['projections'])],
            'solved_ids': [r['name'] for r in rows if r['verification']['solved_at_certified_prefix']],
            'skipped_ids': [r['name'] for r in rows if r['skip_reason']],
            'total_units': sum(r['total_units'] for r in rows), 'cpu_seconds': sum(r['cpu_seconds'] for r in rows)},
        'scope': 'All affordable one-occurrence projections of 18 exact CURRENT winner endpoints; no heap search. '
                 'New cuts, pivots and comparison maps share 1k per row. Imported discovery/replay costs are historical. '
                 'Equal minimum lengths alone do not prove Aut-equivalence; explicit signed returns are separately recorded.'}
    destination.write_text(json.dumps(report, indent=2) + '\n')
    assert json.loads(destination.read_text())['summary'] == report['summary']
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
