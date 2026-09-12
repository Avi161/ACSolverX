"""Independent replay and accounting checks for the AC19 expansion experiment."""
import hashlib
import json
from pathlib import Path

import run_panel as subject


HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_phase(initial, phase):
    endpoint = subject.replay_fixed(initial, phase['events'])
    assert endpoint == subject.tuple_words(phase['endpoint'])
    best = subject.replay_fixed(initial, phase['best_fixed_events'])
    assert best == subject.tuple_words(phase['best_fixed_endpoint'])
    assert all(event['kind'] == 'normal_product_substitution'
               for event in phase['events'] + phase['best_fixed_events'])


def check_hard(path):
    report = json.loads(path.read_text())
    assert report['panel_sha256'] == sha(HERE / 'hard_solved_panel.jsonl')
    assert report['source_sha256']['run_panel.py'] == sha(HERE / 'run_panel.py')
    sources = {row['name']: row for row in subject.load_panel()}
    assert len(report['rows']) == 4
    for row in report['rows']:
        source = sources[row['name']]
        original = subject.fixed_engine.search.normalize(
            (subject.parse_word(source['r1']), subject.parse_word(source['r2'])))
        expanded = subject.replay_expansion(original, row['expansion']['events'])
        assert expanded == subject.tuple_words(row['expansion']['endpoint'])
        assert len(expanded) == row['retained_rank']
        assert max(map(len, expanded)) == 3
        check_phase(expanded, row['macro'])
        seed = subject.tuple_words(row['macro']['best_fixed_endpoint'])
        check_phase(seed, row['deep'])
        assert subject.replay_fixed(expanded, row['combined_search_events']) == subject.tuple_words(row['endpoint'])
        assert not row['solved_at_retained_rank']
        assert row['terminal_compiler'] is None
        for phase in (row['macro'], row['deep']):
            assert phase['generated_states_with_unit'] == 0
            assert phase['generated_states_with_bigon'] == 0
            assert phase['generated_terminal_states'] == 0
    return report


def check_easy(path):
    report = json.loads(path.read_text())
    assert report['panel_sha256'] == sha(HERE / 'easy_control_panel.jsonl')
    assert report['source_sha256']['run_easy_controls.py'] == sha(HERE / 'run_easy_controls.py')
    assert report['source_sha256']['run_panel.py'] == sha(HERE / 'run_panel.py')
    assert len(report['rows']) == 12
    sources = {row['name']: row for row in (
        json.loads(line) for line in
        (HERE / 'easy_control_panel.jsonl').read_text().splitlines())}
    assert set(sources) == {row['name'] for row in report['rows']}
    solved = 0
    for row in report['rows']:
        source = sources[row['name']]
        assert all(step['kind'] == 'substitution' for step in source['steps'])
        moves = [subject.str_to_move(step['move']) for step in source['steps']]
        states = subject.moves_to_states(source['pair'][0], source['pair'][1], moves)
        assert states == source['states'] and states[-1] == ['Y', 'X']
        expected_original = subject.fixed_engine.search.normalize(
            tuple(subject.parse_word(word) for word in source['pair']))
        original = subject.tuple_words(row['original'])
        assert original == expected_original
        expanded = subject.replay_expansion(original, row['expansion_events'])
        assert expanded == subject.tuple_words(row['expanded'])
        check_phase(expanded, row['macro'])
        compiled = row['terminal_compiler']
        if compiled is not None:
            terminal = subject.tuple_words(row['macro']['endpoint'])
            replayed = subject.theory_short_relators.replay(terminal, compiled['moves'])
            assert replayed == subject.tuple_words(compiled['endpoint'])
            assert sorted(replayed) == [(g,) for g in range(1, len(expanded) + 1)]
            assert len(replayed) == len(expanded)
            solved += 1
        assert row['solved_at_retained_rank'] == (compiled is not None)
    assert solved == report['summary']['solved_at_retained_rank'] == 5
    return report


def main():
    s20_path = HERE / 's20_panel_records.jsonl'
    assert sha(s20_path) == 'ee99044b5f8fdd1edec996b4f6cdabcc39472ada7e96788a4db493a1e9b593e4'
    s20 = {row['name']: row for row in (
        json.loads(line) for line in s20_path.read_text().splitlines())}
    assert set(s20) == set(subject.S20_NODES)
    for name, nodes in subject.S20_NODES.items():
        assert s20[name]['solved'] and s20[name]['nodes_explored'] == nodes
        assert s20[name]['budget'] == 100000 and s20[name]['mrl'] == 48
    cap5 = check_hard(HERE / 'panel_macro100_cap5_p500_fast.json')
    cap6 = check_hard(HERE / 'panel_macro100_cap6_p1000_fast.json')
    audited = json.loads((HERE / 'panel_macro100_cap5_p500.json').read_text())
    for old, new in zip(audited['rows'], cap5['rows']):
        assert old['name'] == new['name']
        for key in ('endpoint', 'combined_search_events', 'solved_at_retained_rank',
                    'retained_rank', 'minimum_relator_length_reached',
                    'maximum_relator_length_at_endpoint'):
            assert old[key] == new[key]
        for phase_name in ('macro', 'deep'):
            for key in ('endpoint', 'events', 'best_fixed_endpoint',
                        'best_fixed_events', 'heap_pops', 'discovered_states',
                        'generated_rotation_products'):
                assert old[phase_name][key] == new[phase_name][key]
    assert cap5['summary']['solved_at_retained_rank'] == 0
    assert cap6['summary']['solved_at_retained_rank'] == 0
    easy = check_easy(HERE / 'easy_control_macro100.json')
    print('PASS: hard 0/4, easy controls 5/12; fast/audited cap-5 results match; every retained path replays and no destabilization occurs')


if __name__ == '__main__':
    main()
