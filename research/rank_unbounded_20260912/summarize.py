"""Join the preserved baseline and verified any-rank shortening records."""
from collections import Counter
import csv
import json
from pathlib import Path

import search


def display(words):
    letters = 'xyzuvw'
    return '(' + ', '.join(''.join(letters[abs(x) - 1].upper() if x < 0 else letters[x - 1]
                                    for x in word) if all(abs(x) <= len(letters) for x in word)
                           else ' '.join(f'g{abs(x)}' + ('^-1' if x < 0 else '') for x in word)
                           for word in words) + ')'


def main():
    here = Path(__file__).resolve().parent
    old_file = here.parent / 'theory_patterns_20260912/u124_final_table.json'
    old = json.loads(old_file.read_text())
    observed = {}
    for filename in ('observed_pilot.json', 'observed_remainder.json'):
        report = json.loads((here / filename).read_text())
        for index, row in enumerate(report['rows']):
            if row['name'] in observed:
                raise AssertionError('duplicated observation')
            observed[row['name']] = row, f'{filename}#/rows/{index}/best_witness'
    if set(observed) != {r['name'] for r in old['rows']} or len(observed) != 124:
        raise AssertionError('observation IDs do not match all124')
    panel = json.loads((here / 'partial_panel.json').read_text())
    if panel['summary']['gain_ids']:
        raise AssertionError('merge the new partial-basis gains before publishing')
    audit = json.loads((here / 'audit.json').read_text())
    if audit['status'] != 'PASS':
        raise AssertionError('independent audit did not pass')
    rows, certificates = [], []
    for index, prior in enumerate(old['rows']):
        obs, pointer = observed[prior['name']]
        witness = obs['best_witness']
        words = witness['endpoint']
        if sum(map(len, words)) != obs['best_length'] or len(words) != witness['rank']:
            raise AssertionError('witness total/rank differs')
        gain = prior['best_any_rank_length'] - obs['best_length']
        if gain < 0:
            raise AssertionError('lost saved incumbent')
        rank_reduction = max(0, prior['best_rank'] - witness['rank'])
        new_witness = gain > 0 or rank_reduction > 0
        if not new_witness:
            words, _ = search.parse_words(prior['best_words'])
        rank2 = obs['inspected_rank_length_curve'].get('2', prior['best_rank2_length'])
        if rank2 < prior['best_rank2_length']:
            raise AssertionError('rank2 improvement needs a separate explicit witness')
        solved = (not words or all(len(w) == 1 for w in words)
                  and len({abs(w[0]) for w in words}) == len(words))
        row = {'name': prior['name'], 'archival_initial_length': prior['archival_initial_length'],
               'saved_rank2_length': prior['starting_best_length'],
               'previous_any_rank_length': prior['best_any_rank_length'],
               'best_any_rank_length': obs['best_length'], 'best_rank': len(words),
               'new_gain': gain, 'rank_reduction': rank_reduction, 'solved': solved, 'best_words': display(words),
               'certificate_kind': 'theorem_backed_stable_composite' if new_witness else prior['certificate_kind'],
               'witness_pointer': pointer if new_witness else '../theory_patterns_20260912/u124_final_table.json#/rows/' + str(index)}
        rows.append(row)
        if new_witness:
            source_pointer = (prior['source_certificate_pointer'] if witness['source'] == 'saved_best'
                              else prior['best_rank2_source_certificate_pointer'])
            certificates.append({'name': prior['name'], 'old_table_sha256': search.sha(old_file),
                                 'source_kind': witness['source'], 'source_pointer': source_pointer,
                                 'input_letter_map': search.parse_words(prior['best_words'] if witness['source'] == 'saved_best'
                                                                       else prior['starting_words'])[1],
                                 'previous_best_length': prior['best_any_rank_length'],
                                 'length_gain': gain, 'rank_reduction': rank_reduction,
                                 'endpoint_length': obs['best_length'], 'witness': witness,
                                 'certificate_kind': 'theorem_backed_stable_composite',
                                 'fully_expanded_elementary_path': False})
    summary = {'rows': len(rows), 'new_gain_ids': [r['name'] for r in rows if r['new_gain']],
               'same_length_rank_reduction_ids': [r['name'] for r in rows if not r['new_gain'] and r['rank_reduction']],
               'previous_total': sum(r['previous_any_rank_length'] for r in rows),
               'new_total': sum(r['best_any_rank_length'] for r in rows),
               'saved_rank2_total': sum(r['saved_rank2_length'] for r in rows),
               'shorter_than_saved_rank2': sum(r['best_any_rank_length'] < r['saved_rank2_length'] for r in rows),
               'solved': sum(r['solved'] for r in rows),
               'best_rank_counts': dict(Counter(str(r['best_rank']) for r in rows))}
    if summary['previous_total'] != 2191 or summary['new_total'] != 2180 or summary['solved']:
        raise AssertionError('final result differs from reviewed summary')
    (here / 'all124.json').write_text(json.dumps({'baseline_sha256': search.sha(old_file),
                                               'summary': summary, 'rows': rows}, indent=2) + '\n')
    with (here / 'all124.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    with (here / 'shortening_witnesses.jsonl').open('w') as handle:
        for certificate in certificates:
            handle.write(json.dumps(certificate) + '\n')
    lines = ['# U124 after arbitrary-rank research', '',
             'Total length counts all relators. No row is solved. The new witnesses use Lemma 11',
             'and exact word/basis operations; their elementary stable-AC expansions are not emitted.',
             'These are attained representatives, not global minima. The archival column predates',
             'the 36 historical rank2 reductions; the current investigation starts at the saved states.', '',
             '| Row | Archival | Saved rank2 | Previous any rank | New best | Rank | New gain |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        lines.append(f"| {row['name']} | {row['archival_initial_length']} | {row['saved_rank2_length']} | "
                     f"{row['previous_any_rank_length']} | {row['best_any_rank_length']} | {row['best_rank']} | {row['new_gain']} |")
    lines += ['', 'Exact endpoint words and witness pointers are in [CSV](all124.csv) and [JSON](all124.json).',
              'The eleven length gains and four same-length rank reductions have paths in',
              '[shortening_witnesses.jsonl](shortening_witnesses.jsonl).']
    (here / 'ALL124.md').write_text('\n'.join(lines) + '\n')
    reread = json.loads((here / 'all124.json').read_text())
    emitted = [json.loads(line) for line in (here / 'shortening_witnesses.jsonl').read_text().splitlines()]
    if reread['summary'] != summary or len(emitted) != len(summary['new_gain_ids']) + len(summary['same_length_rank_reduction_ids']):
        raise AssertionError('delivery read-back failed')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
