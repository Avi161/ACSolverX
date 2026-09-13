"""Lift the saved rank-2 AC certificates of the hard AC19 panel into triangle systems.

Outputs
-------
lift_hard.json   per-step tables for both saved arms of the four hard rows
lift_easy.json   the same for the three longest easy-control rows
gradient.json    fixed-rank cap-4 neighbourhood score statistics at the roots
tables/*.md      compact per-row markdown tables

Usage
-----
    python3 research/ac19_triangle_expansion_20260912/lift/run_lift.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import lift_common as L

HERE = Path(__file__).resolve().parent
TABLES = HERE / 'tables'


def markdown_table(report):
    head = ('| step | r1 | r2 | L | maxlen | rank_t | #defs | shared_prev | '
            'shared_init | enc_opt_max | enc_greedy_max |')
    rule = '|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|'
    lines = ['### %s (%s)' % (report['name'], report['arm']), '', head, rule]
    for record in report['steps']:
        lines.append('| %d | `%s` | `%s` | %d | %d | %d | %d | %d | %d | %d | %d |' % (
            record['step'], record['state'][0], record['state'][1],
            record['total_length'], record['max_relator_length'], record['rank'],
            record['definition_count'], record['shared_with_previous'],
            record['shared_with_initial'], record['encoded_optimal_max'],
            record['encoded_greedy_max']))
    lines.append('')
    return '\n'.join(lines)


def run(paths, label, output):
    reports = []
    for entry in paths:
        start = time.perf_counter()
        report = L.analyse_path(entry)
        report['wall_seconds'] = time.perf_counter() - start
        reports.append(report)
        print('%-14s %-8s states=%3d rank %d..%d drift=%.3f cap_min=%d cap_max=%d' % (
            report['name'], report['arm'], report['summary']['path_states'],
            report['summary']['min_rank'], report['summary']['max_rank'],
            report['summary']['dictionary_change_fraction'],
            report['summary']['min_over_path_encoded_optimal_max'],
            report['summary']['max_over_path_encoded_optimal_max']))
    payload = {
        'schema': 'ac19_triangle_lift_v1',
        'label': label,
        'inputs_sha256': {
            'hard_solved_panel.jsonl': L.sha(L.HARD_PANEL),
            's20_panel_records.jsonl': L.sha(L.S20_PANEL),
            'easy_control_panel.jsonl': L.sha(L.EASY_PANEL),
            'AC19_extended_aut_min.csv': L.sha(L.AC19),
            'high_rank_triangles.py': L.sha(L.U124 / 'high_rank_triangles.py'),
            'high_rank_ac_search.py': L.sha(L.HIGH_RANK / 'high_rank_ac_search.py'),
            'lift_common.py': L.sha(HERE / 'lift_common.py'),
        },
        'rows': reports,
    }
    output.write_text(json.dumps(payload, indent=1) + '\n')
    TABLES.mkdir(exist_ok=True)
    for report in reports:
        (TABLES / ('%s_%s.md' % (report['name'], report['arm']))).write_text(
            markdown_table(report) + '\n')
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--easy-rows', type=int, default=3)
    args = parser.parse_args()

    print('== hard panel ==')
    run(L.load_hard_paths(), 'hard_solved_panel', HERE / 'lift_hard.json')
    print('== easy controls ==')
    run(L.load_easy_paths(args.easy_rows), 'easy_control_panel',
        HERE / 'lift_easy.json')

    print('== gradient at the four hard roots + three easy roots ==')
    gradient = {'schema': 'ac19_triangle_gradient_v1', 'relator_cap': 4, 'rows': []}
    seeds = [(entry['name'], entry['states'][0], 'hard')
             for entry in L.load_hard_paths() if entry['arm'] == 'greedy']
    seeds += [(entry['name'], entry['states'][0], 'easy')
              for entry in L.load_easy_paths(args.easy_rows)]
    for name, pair, panel in seeds:
        record = L.gradient_report(pair, relator_cap=4)
        record.update({'name': name, 'panel': panel, 'state': list(pair)})
        gradient['rows'].append(record)
        print('%-14s %-5s rank=%2d neigh=%4d distinct=%3d best_ties=%3d (%.3f) '
              'better/equal/worse=%d/%d/%d' % (
                  name, panel, record['rank'], record['neighbours'],
                  record['distinct_scores'], record['best_score_multiplicity'],
                  record['best_score_tie_fraction'], record['strictly_better'],
                  record['equal_to_parent'], record['strictly_worse']))
    (HERE / 'gradient.json').write_text(json.dumps(gradient, indent=1) + '\n')


if __name__ == '__main__':
    main()
