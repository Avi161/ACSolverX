"""Audit retained high-rank triangles and export complete saved-rank2 chains."""
from collections import Counter
from copy import deepcopy
import csv
import json
from pathlib import Path
import verify as v
import export_paths as ex

HERE = Path(__file__).resolve().parent


def excess(words):
    return sum(max(0, len(w) - 3) for w in words)


def main():
    source = HERE / 'HIGH_RANK_TRIANGLES.json'
    report = json.loads(source.read_text())
    v.require(report['script_sha256'] == v.sha(HERE / 'high_rank_triangles.py'), 'triangulation source changed')
    current = json.loads((HERE / 'CURRENT.json').read_text())
    v.require(report['current_sha256'] == v.sha(HERE / 'CURRENT.json'), 'triangulation current source changed')
    baseline = v.load_baseline()
    inputs = {r['name']: r for r in current['rows']}
    full = {r['name']: r for r in map(json.loads, (ex.OUT / 'all124_stable_composite.jsonl').read_text().splitlines())}
    records, checked, total_units = [], [], 0
    for index, row in enumerate(report['retained_rows']):
        name = row['name']
        v.verify_record(row, baseline)
        count = row['new_definitions']
        suffix = row['events'][-count:] if count else []
        cursor = v.normalized(v.words(inputs[name]['words']))
        v.require(len(cursor) == row['retained_source_rank'] and v.size(cursor) == row['retained_source_total'] and max(map(len, cursor)) == row['retained_source_max_relator'], 'retained source metric differs')
        charges = 0
        for event in suffix:
            v.require(event['kind'] == 'defining_compression' and v.words(event['before']) == cursor, 'retained suffix removes rank or is discontinuous')
            long_pairs, all_pairs = Counter(), Counter()
            for word in cursor:
                for k in range(len(word)):
                    pair = (word[k], word[(k + 1) % len(word)])
                    pair = min(pair, v.invert(pair))
                    all_pairs[pair] += 1
                    if len(word) > 3:
                        long_pairs[pair] += 1
            chosen = min(long_pairs, key=lambda pair: (-all_pairs[pair], -long_pairs[pair], pair))
            v.require(v.word(event['defining']) == chosen and len(chosen) == 2, 'selected two-letter definition differs')
            charges += len(long_pairs) + len(cursor) + 1
            after = v.verify_event(event, known_trivial=True)
            v.require(len(after) == len(cursor) + 1 and excess(after) < excess(cursor), 'triangularization progress/count fails')
            cursor = after
        v.require(cursor == v.words(row['endpoint']) and max(map(len, cursor)) <= 3 and len(cursor) == row['retained_rank'] and v.size(cursor) == row['retained_total'], 'retained endpoint differs')
        v.require(row['retained_max_relator'] == max(map(len, cursor)) and row['row_length_counts'] == {str(n): sum(len(w) == n for w in cursor) for n in (1, 2, 3)}, 'retained row lengths differ')
        v.require(row['automatic_destabilization'] is False and charges == row['new_charged_units'] <= row['budget'] == 1000, 'retained budget/removal policy differs')
        total_units += charges
        record = deepcopy(full[name])
        v.require(ex.replay_record(record) == v.words(inputs[name]['words']), 'full source chain differs from CURRENT')
        frame = ex.Chain(record['initial'])
        frame.current = v.words(record['endpoint'])
        frame.equivalent(v.normalized(frame.current))
        record['events'] += frame.events
        first = len(record['events'])
        record['events'] += suffix
        record.update(endpoint=cursor, endpoint_length=v.size(cursor), endpoint_rank=len(cursor), length_gain=record['initial_length'] - v.size(cursor))
        record['boundaries'] = [{'event_count': 0, 'rank': 2, 'length': record['initial_length']}] + [{'event_count': i + 1, 'rank': len(e['after']), 'length': v.size(e['after'])} for i, e in enumerate(record['events'])]
        record['retained_high_rank_suffix'] = {'source_file': str(source.relative_to(ex.ROOT)), 'source_sha256': v.sha(source), 'selector': '#/retained_rows/' + str(index), 'first_event': first, 'new_definitions': count, 'before': inputs[name]['words'], 'after': cursor, 'automatic_destabilization': False}
        record['objective'] = 'Retain rank while minimizing individual relator lengths; total length is separately reported.'
        v.require(ex.replay_record(record) == cursor, 'full retained chain replay differs')
        records.append(record)
        checked.append({'name': name, 'rank': len(cursor), 'total': v.size(cursor), 'maximum_relator': max(map(len, cursor)), 'new_definitions': count})
    v.require(len(records) == 124 and {r['name'] for r in records} == set(inputs), 'retained cohort differs')
    with (HERE / 'HIGH_RANK_TRIANGLES.csv').open(newline='') as handle:
        printed = list(csv.DictReader(handle))
    by_name = {r['name']: r for r in report['retained_rows']}
    v.require(len(printed) == 124 and all(all(value == str(by_name[r['name']][key]) for key, value in r.items()) for r in printed), 'retained CSV differs')
    total = sum(r['total'] for r in checked)
    rank_range = [min(r['rank'] for r in checked), max(r['rank'] for r in checked)]
    v.require(total == report['summary']['total_length_sum'] == 3444 and rank_range == report['summary']['rank_range'] == [7, 12] and total_units == report['summary']['units'] == 12234, 'retained aggregate differs')
    output = ex.OUT / 'all124_retained_high_rank.jsonl'
    partial = output.with_suffix('.jsonl.partial')
    partial.write_text(''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in records))
    for row in map(json.loads, partial.read_text().splitlines()):
        ex.replay_record(row)
    partial.replace(output)
    manifest = {'status': 'PASS', 'rows': 124, 'saved_rank2_total': 2356, 'retained_total': total,
                'maximum_individual_relator_length': 3, 'retained_rank_range': rank_range,
                'new_charged_units': total_units, 'full_composite_events': sum(len(r['events']) for r in records),
                'new_definitions': sum(r['new_definitions'] for r in checked), 'automatic_destabilization': False,
                'certificate_file': output.name, 'certificate_sha256': v.sha(output),
                'retained_source_sha256': v.sha(source), 'minimum_total_export_sha256': v.sha(ex.OUT / 'all124_stable_composite.jsonl'),
                'minimum_total_manifest_sha256': v.sha(ex.OUT / 'manifest.json'),
                'verifier_sha256': v.sha(HERE / 'verify.py'), 'script_sha256': v.sha(Path(__file__)),
                'fully_expanded_elementary_stable_AC': False, 'unresolved_lineage_segments': 0,
                'scope': 'All124 full saved-rank2 chains are embedded. The retained suffix consists only of exact definitions, with every original and defining row kept. This is a separate short-relator objective, not a solve or proximity claim. Earlier minimum-total prefix histories may contain removals; the new high-rank suffix does not.', 'searches_performed': 0}
    (ex.OUT / 'retained_high_rank_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (HERE / 'verification_highrank.json').write_text(json.dumps({**manifest, 'checked_rows': checked}, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
