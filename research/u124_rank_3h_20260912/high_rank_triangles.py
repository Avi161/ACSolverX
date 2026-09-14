"""Retain high rank while shortening every individual relator to length at most3."""
from collections import Counter
import csv
import io
import json
from pathlib import Path
import time

import rank_peeling
from rank_peeling import search
import verify

HERE = Path(__file__).resolve().parent


def excess(words):
    return sum(max(0, len(word) - 3) for word in words)


def triangulate(words, budget=1000):
    current, events, used = search.normalize(words), [], 0
    while excess(current):
        long_counts, all_counts = Counter(), Counter()
        for word in current:
            for k in range(len(word)):
                pair = (word[k], word[(k + 1) % len(word)])
                pair = min(pair, search.inverse(pair))
                all_counts[pair] += 1
                if len(word) > 3:
                    long_counts[pair] += 1
        charge = len(long_counts) + len(current) + 1
        if used + charge > budget:
            break
        defining = min(long_counts, key=lambda pair: (-all_counts[pair], -long_counts[pair], pair))
        after, event = search.compress(current, defining)
        event['kind'] = 'defining_compression'
        if excess(after) >= excess(current):
            raise AssertionError('triangle excess did not decrease')
        events.append(event)
        current = after
        used += charge
    return current, events, used


def main():
    output = HERE / 'HIGH_RANK_TRIANGLES.json'
    if output.exists():
        raise ValueError('refusing to overwrite retained high-rank states')
    table = json.loads((HERE / 'CURRENT.json').read_text())
    baseline = verify.load_baseline()
    rows = []
    for source in table['rows']:
        name = source['name']
        source_key, prefix = 'current_best', []
        initial = search.normalize(baseline[name]['sources'][source_key])
        if not source['witness_file'].startswith('../'):
            parent = json.loads((HERE / source['witness_file']).read_text())['rows'][int(source['witness_pointer'].split('/')[-1])]
            source_key, initial = parent['source_key'], parent['initial']
            prefix = parent['events'][:source['witness_prefix_events']]
        words = search.normalize(source['words'])
        cpu, wall = time.process_time(), time.perf_counter()
        after, events, used = triangulate(words)
        row = {'name': name, 'baseline_sha256': baseline[name]['baseline_sha256'],
               'source_key': source_key, 'initial': initial, 'events': prefix + events, 'endpoint': after,
               'retained_source_rank': len(words), 'retained_source_total': search.length(words),
               'retained_source_max_relator': max(map(len, words), default=0),
               'retained_rank': len(after), 'retained_total': search.length(after),
               'retained_max_relator': max(map(len, after), default=0),
               'row_length_counts': {str(n): sum(len(w) == n for w in after) for n in (1, 2, 3)},
               'new_definitions': len(events), 'new_charged_units': used, 'budget': 1000,
               'new_cpu_seconds': time.process_time() - cpu, 'new_wall_seconds': time.perf_counter() - wall,
               'all_relators_at_most_three': not excess(after),
               'automatic_destabilization': False, 'fully_expanded_elementary_stable_path': False}
        row['verification'] = verify.verify_record(row, baseline)
        rows.append(row)
        time.sleep(0.05)
    summary = {'rows': len(rows), 'all_max_length_at_most_three': all(r['all_relators_at_most_three'] for r in rows),
               'rank_range': [min(r['retained_rank'] for r in rows), max(r['retained_rank'] for r in rows)],
               'total_length_sum': sum(r['retained_total'] for r in rows),
               'units': sum(r['new_charged_units'] for r in rows),
               'cpu_seconds': sum(r['new_cpu_seconds'] for r in rows),
               'wall_seconds': sum(r['new_wall_seconds'] for r in rows)}
    report = {'schema': 'retained_high_rank_short_relators_v1', 'current_sha256': verify.sha(HERE / 'CURRENT.json'),
              'script_sha256': verify.sha(Path(__file__)), 'summary': summary, 'retained_rows': rows,
              'scope': 'Separate individual-relator-length objective. Universal triangularization is not a solve or proof of easier search.'}
    output.write_text(json.dumps(report, indent=2) + '\n')
    columns = ['name', 'retained_source_rank', 'retained_source_total', 'retained_source_max_relator',
               'retained_rank', 'retained_total', 'retained_max_relator', 'new_definitions']
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    (HERE / 'HIGH_RANK_TRIANGLES.csv').write_text(stream.getvalue())
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
