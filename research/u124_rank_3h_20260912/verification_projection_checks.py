"""Read-only exact lineage, pivot coverage and projection-metric checks."""
from collections import Counter
import json
from pathlib import Path
import verify as v

HERE = Path(__file__).resolve().parent


def main():
    direct_path, neutral_path = HERE / 'theory_projection_panel.json', HERE / 'theory_projection_neutral_panel.json'
    direct, neutral = json.loads(direct_path.read_text()), json.loads(neutral_path.read_text())
    v.require(neutral['direct_snapshot_sha256'] == v.sha(direct_path), 'neutral projection snapshot changed')
    baseline = v.load_baseline()
    current = {r['name']: r for r in json.loads((HERE / 'CURRENT.json').read_text())['rows']}
    ids = {name for name, row in current.items() if row['phase_gain'] > 0}
    v.require(len(ids) == 18 and set(direct['selected_ids']) == set(neutral['selected_ids']) == ids, 'projection cohort differs')
    for source, expected in direct['source_hashes'].items():
        v.require(v.sha(HERE / source) == expected, 'projection seed source changed')
    counts, total_units, signed_returns = [], [], 0
    for report in (direct, neutral):
        v.require(v.sha(HERE / (report['module'] + '.py')) == report['script_sha256'], 'projection runner changed')
        count, units = 0, 0
        for row in report['projection_rows']:
            name = row['name']
            v.require(row['total_units'] == sum(row['costs'].values()) <= row['budget'] == 1000, 'projection budget differs')
            units += row['total_units']
            pairs = set()
            for projection in row['projections']:
                checked = v.verify_record(projection, baseline)
                endpoint = v.words(projection['endpoint'])
                v.require(checked['endpoint_length'] == projection['endpoint_length'] and checked['endpoint_rank'] == projection['endpoint_rank'], 'projection endpoint metric differs')
                v.require(projection['gain_vs_any_rank_incumbent'] == current[name]['best_length'] - v.size(endpoint) <= 0, 'projection falsely credits imported gain')
                expected_gain = baseline[name]['sources']['saved_rank2']
                v.require(projection['rank2_gain_vs_saved'] == (v.size(expected_gain) - v.size(endpoint) if len(endpoint) == 2 else None), 'projection rank-two comparison differs')
                v.require(projection['closure_complete'] is True and projection['rank2_aut_minimum_certified'] == (len(endpoint) == 2), 'projection completion flags differ')
                returned = projection['exact_saved_rank2_signed_permutation']
                if returned is not None:
                    mapping = {int(g): (letter,) for g, letter in returned.items()}
                    v.require(set(mapping) == {abs(x) for w in endpoint for x in w} and {abs(w[0]) for w in mapping.values()} == {abs(x) for w in expected_gain for x in w}, 'signed return is not a basis bijection')
                    v.require(v.normalized(tuple(v.image(w, mapping) for w in endpoint)) == v.normalized(expected_gain), 'saved signed return differs')
                    signed_returns += 1
                if report is direct:
                    cut = projection['seed_event_count']
                    seed = v.words(projection['events'][cut - 1]['after'] if cut else projection['initial'])
                    v.require(seed == v.words(current[name]['words']), 'projection starts from a different current tuple')
                    pivot = projection['pivot']
                    pairs.add((pivot['donor_index'], pivot['generator']))
                    removal = projection['events'][cut]
                    v.require(removal['kind'] == 'lemma11_removal' and v.words(removal['after']) == v.words(projection['raw_removed_words']), 'raw projection differs from removal')
                count += 1
            if report is direct:
                state = v.words(current[name]['words'])
                expected = {(i, g) for i, w in enumerate(state) for g, n in Counter(map(abs, w)).items() if n == 1}
                v.require(pairs == expected and len(row['projections']) == len(expected) == row['input_pivots'], 'direct projection omits or duplicates a pivot')
                v.verify_record(row, baseline)
            else:
                v.require(row['attempted_pivots'] == row['pivots_in_returned_neighbors'] and row['all_returned_neighbor_pivots_attempted'], 'returned neutral pivot coverage differs')
        v.require(count == report['summary']['projections'] and units == report['summary']['total_units'], 'projection summary differs')
        v.require(report['summary']['new_rank2_gain_ids'] == report['summary']['new_any_rank_gain_ids'] == report['summary']['solved_ids'] == [], 'unexpected projection gain claim')
        counts.append(count)
        total_units.append(units)
    v.require(counts == [61, 3] and total_units == [879, 1658], 'projection cohort totals differ')
    output = {'status': 'PASS', 'exact_current_winner_ids': sorted(ids), 'direct_projections': 61,
              'neutral_projections': 3, 'all_direct_singleton_pivots_present_once': True,
              'signed_returns_replayed': signed_returns, 'new_charged_units': total_units,
              'new_endpoint_gains': 0, 'census_reruns': 0,
              'source_hashes': {p.name: v.sha(p) for p in (direct_path, neutral_path)},
              'scope': 'Replays all64 saved projection paths and their exact current prefixes. Closure completion is checked against the frozen cleanup loop, which requires an unchanged tuple with complete Whitehead and peeling scans; scans were not rerun. Imported shorter prefixes are distinguished from longer projected endpoints. The neutral orbit is not exhausted.'}
    (HERE / 'verification_projection.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('status', 'direct_projections', 'neutral_projections', 'signed_returns_replayed', 'new_charged_units', 'new_endpoint_gains')}))


if __name__ == '__main__':
    main()
