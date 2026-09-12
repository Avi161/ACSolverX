"""One neutral Whitehead neighbor, then exact rank-two projection and cleanup."""
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import plateau
import theory_projection_panel as direct
from theory_projection_panel import lemma11, rank_peeling, search, verify

HERE = Path(__file__).resolve().parent


def run_row(row, baseline, budget=1000):
    count = row['current_witness_prefix_events']
    prefix = row['events'][:count]
    state = verify.words(prefix[-1]['after'] if prefix else row['initial'])
    seed = {key: row[key] for key in ('name', 'baseline_sha256', 'source_key', 'initial')}
    seed.update(events=prefix, endpoint=state)
    verify.verify_record(seed, baseline)
    assert len(state) == 3 and search.length(state) == row['seed_length']
    saved = verify.words(row['saved_rank2_words'])
    cpu, wall = time.process_time(), time.perf_counter()
    neighbors, neutral_checks = plateau.neutral_whitehead(state, min(96, budget))
    cuts = pivots = comparisons = 0
    candidates, cache, finished_neighbors = [], {}, 0
    total_pivots = sum(len(rank_peeling.pivots(s)) for s, _ in neighbors)
    attempted_pivots = 0
    for neighbor, ambient in neighbors:
        if search.length(neighbor) != search.length(state):
            raise AssertionError('CURRENT endpoint unexpectedly admits a strict Whitehead reduction')
        choices = rank_peeling.pivots(neighbor)
        finished = True
        for bound, degree, donor_length, donor, generator in choices:
            if neutral_checks + cuts + pivots + comparisons == budget:
                finished = False
                break
            removed, event = lemma11.remove_one(neighbor, donor, generator)
            pivots += 1
            attempted_pivots += 1
            reused = removed in cache
            if reused:
                endpoint, tail, complete = cache[removed]
                ecuts = epivots = 0
            else:
                endpoint, tail, ecuts, epivots, complete = direct.cleanup(
                    removed, budget - neutral_checks - cuts - pivots - comparisons)
                cache[removed] = endpoint, tail, complete
                cuts += ecuts
                pivots += epivots
            mapping, ec = direct.signed_return(endpoint, saved,
                budget - neutral_checks - cuts - pivots - comparisons)
            comparisons += ec
            projection = {**seed, 'events': prefix + ambient + [event] + tail, 'endpoint': endpoint,
                'endpoint_length': search.length(endpoint), 'endpoint_rank': len(endpoint),
                'neutral_neighbor': neighbor, 'pivot': {'donor': donor, 'generator': generator,
                    'literal_length_change_upper_bound': bound}, 'raw_removed_length': search.length(removed),
                'closure_complete': complete, 'rank2_aut_minimum_certified': complete and len(endpoint) == 2,
                'saved_rank2_length': row['saved_rank2_length'], 'any_rank_incumbent_length': row['seed_length'],
                'rank2_gain_vs_saved': row['saved_rank2_length'] - search.length(endpoint) if len(endpoint) == 2 else None,
                'gain_vs_any_rank_incumbent': row['seed_length'] - search.length(endpoint),
                'exact_saved_rank2_signed_permutation': mapping, 'cleanup_reused': reused,
                'new_projection_work': {'pivot': 1, 'minimum_cuts': ecuts, 'cleanup_pivots': epivots,
                                        'signed_permutation_comparisons': ec}}
            projection['verification'] = verify.verify_record(projection, baseline)
            candidates.append(projection)
        finished_neighbors += finished
        if not finished:
            break
    best = min(candidates, key=lambda p: (p['endpoint_length'], p['endpoint_rank'])) if candidates else None
    used = neutral_checks + cuts + pivots + comparisons
    assert used <= budget
    return {'name': row['name'], 'seed_length': row['seed_length'], 'saved_rank2_length': row['saved_rank2_length'],
        'neutral_neighbors_returned': len(neighbors), 'finished_neighbors': finished_neighbors,
        'pivots_in_returned_neighbors': total_pivots, 'attempted_pivots': attempted_pivots,
        'all_returned_neighbor_pivots_attempted': total_pivots == attempted_pivots,
        'all_projection_closures_complete': all(p['closure_complete'] for p in candidates),
        'best_projection_length': best['endpoint_length'] if best else None,
        'best_projection_rank': best['endpoint_rank'] if best else None,
        'projections': candidates, 'skip_reason': 'no returned neutral neighbor with a one-occurrence pivot' if not candidates else None,
        'costs': {'neutral_whitehead_checks': neutral_checks, 'minimum_cuts': cuts,
                  'pivot_attempts': pivots, 'signed_permutation_comparisons': comparisons},
        'total_units': used, 'budget': budget, 'cpu_seconds': time.process_time() - cpu,
        'wall_seconds': time.perf_counter() - wall}


def main():
    output = Path(__file__).with_suffix('.json')
    if output.exists():
        raise ValueError('refusing to overwrite the neutral projection panel')
    source_file = HERE / 'theory_projection_panel.json'
    source = json.loads(source_file.read_text())
    baseline, rows = verify.load_baseline(), []
    assert set(source['selected_ids']) == direct.EXPECTED
    for row in source['projection_rows']:
        result = run_row(row, baseline)
        rows.append(result)
        print(result['name'], 'neighbors', result['neutral_neighbors_returned'],
              'projections', result['attempted_pivots'], 'best', result['best_projection_length'],
              'units', result['total_units'], flush=True)
        time.sleep(0.05)
    summary = {'rows': len(rows), 'projections': sum(r['attempted_pivots'] for r in rows),
        'all_returned_neighbor_pivots_attempted': all(r['all_returned_neighbor_pivots_attempted'] for r in rows),
        'all_closures_complete': all(r['all_projection_closures_complete'] for r in rows),
        'new_rank2_gain_ids': [r['name'] for r in rows if any(p['rank2_aut_minimum_certified'] and
            p['rank2_gain_vs_saved'] > 0 for p in r['projections'])],
        'new_any_rank_gain_ids': [r['name'] for r in rows if any(p['gain_vs_any_rank_incumbent'] > 0 for p in r['projections'])],
        'solved_ids': [r['name'] for r in rows if any(p['verification']['solved_at_certified_prefix'] for p in r['projections'])],
        'total_units': sum(r['total_units'] for r in rows), 'cpu_seconds': sum(r['cpu_seconds'] for r in rows)}
    report = {'module': 'theory_projection_neutral_panel', 'script_sha256': verify.sha(Path(__file__)),
        'direct_snapshot_sha256': verify.sha(source_file), 'current_sha256': source['current_sha256'],
        'selected_ids': source['selected_ids'], 'projection_rows': rows, 'summary': summary,
        'scope': 'At most96 neutral whole-Whitehead checks before one-occurrence removal; all new work shares1k per row. '
                 'Exact imported CURRENT prefixes, no heap search, no exhaustive neutral Aut-orbit claim. '
                 'Diagnostic nested paths are not frontier records.'}
    output.write_text(json.dumps(report, indent=2) + '\n')
    assert json.loads(output.read_text())['summary'] == summary
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
