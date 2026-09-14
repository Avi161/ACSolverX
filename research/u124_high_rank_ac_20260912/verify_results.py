"""Independent fixed-rank and path-continuity checks for this experiment."""
from pathlib import Path
import hashlib
import json
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
U124 = ROOT / 'research/u124_rank_3h_20260912'
PRIOR = ROOT / 'research/rank_unbounded_20260912'
sys.path[:0] = [str(U124), str(PRIOR)]

import verify


def words(value):
    return tuple(tuple(word) for word in value)


def generator_set(value):
    return {abs(letter) for word in words(value) for letter in word}


def replay_suffix(initial, events):
    current = words(initial)
    rank = len(current)
    generators = generator_set(current)
    for event in events:
        assert event['kind'] == 'normal_product_substitution'
        assert words(event['before']) == current
        current = verify.verify_event(event, known_trivial=True)
        assert len(current) == rank
        assert generator_set(current) == generators
    return current


def check_report(path, expected_ids, *, instrumented=False):
    report = json.loads(path.read_text())
    rows = report['rows']
    assert len(rows) == len({row['name'] for row in rows})
    assert {row['name'] for row in rows} == set(expected_ids)
    for row in rows:
        initial = row.get('search_initial', row['source_endpoint'])
        assert len(words(initial)) == len(words(row['endpoint']))
        assert replay_suffix(initial, row['events']) == words(row['endpoint'])
        terminal = all(len(word) <= 2 for word in words(row['endpoint']))
        assert row['solved_to_length_at_most_two'] == terminal
        if instrumented:
            for key in ('generated_states_with_unit',
                        'generated_states_with_bigon',
                        'generated_terminal_states'):
                assert key in row
    return report


def main():
    source = json.loads((U124 / 'HIGH_RANK_TRIANGLES.json').read_text())
    ids = [row['name'] for row in source['retained_rows']]
    panels = sorted(HERE.glob('panel_*_p100.json'))
    panel_rows = []
    for panel in panels:
        report = json.loads(panel.read_text())
        panel_rows.extend(report['rows'])
    assert len(panels) == 7
    assert len(panel_rows) == len({row['name'] for row in panel_rows}) == 124
    assert {row['name'] for row in panel_rows} == set(ids)
    for row in panel_rows:
        assert len(words(row['source_endpoint'])) == len(words(row['endpoint']))
        assert replay_suffix(row['source_endpoint'], row['events']) == words(row['endpoint'])
        assert not row['solved_to_length_at_most_two']
    macro_path = HERE / 'all124_macro_v2_p100.json'
    macro = check_report(macro_path, ids, instrumented=True)
    wrapper = HERE / 'high_rank_ac_search_v2.py'
    engine = HERE / 'high_rank_ac_search.py'
    assert macro['script_sha256'] == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    assert hashlib.sha256(engine.read_bytes()).hexdigest() == (
        'd3e9ec72620ab15ab0253209f917ed8c6d03e941714360c8909811699fa453b9')
    assert max(row['heap_pops'] for row in macro['rows']) == 72
    assert not [row for row in macro['rows'] if row['heap_pops'] == row['pop_budget']]
    for key in ('generated_states_with_unit', 'generated_states_with_bigon',
                'generated_terminal_states'):
        assert sum(row[key] for row in macro['rows']) == 0
    for name, instrumented in (
            ('focused_78_80_quartic_p500.json', False),
            ('focused_78_80_cap5_p500_v2.json', True)):
        report = check_report(HERE / name, {'aca_78', 'aca_80'},
                              instrumented=instrumented)
        seeds = {row['name']: row for row in macro['rows']}
        for row in report['rows']:
            seed = seeds[row['name']]
            assert words(row['search_initial']) == words(seed['best_fixed_endpoint'])
            assert replay_suffix(row['source_endpoint'], row['seed_events']) == words(row['search_initial'])
        if instrumented:
            assert report['script_sha256'] == macro['script_sha256']
            for key in ('generated_states_with_unit',
                        'generated_states_with_bigon',
                        'generated_terminal_states'):
                assert sum(row[key] for row in report['rows']) == 0
    print('PASS: fixed-rank paths replay; ranks and generators stay fixed; instrumented searches generated no unit, bigon, or terminal')


if __name__ == '__main__':
    main()
