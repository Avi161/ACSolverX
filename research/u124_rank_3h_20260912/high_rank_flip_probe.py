"""Bounded triangle flips with rank retained and no automatic peeling."""
import heapq
import json
from pathlib import Path
import time

import exchange_triangle_flip as flip
import verify

HERE = Path(__file__).resolve().parent


def main():
    destination = HERE / 'HIGH_RANK_FLIPS.json'
    if destination.exists():
        raise ValueError('refusing to overwrite')
    source = json.loads((HERE / 'HIGH_RANK_TRIANGLES.json').read_text())
    baseline = verify.load_baseline()
    records = []
    for row in source['retained_rows']:
        initial = tuple(map(tuple, row['endpoint']))
        queue, seen = [(flip.score(initial), initial, [])], {initial}
        best, path, used, pops = initial, [], 0, 0
        cpu, wall = time.process_time(), time.perf_counter()
        while queue and used < 1000:
            _, current, prefix = heapq.heappop(queue)
            candidates, charge = flip.generate(current, 1000 - used)
            used += charge
            pops += 1
            if charge == 0:
                break
            for endpoint, events in candidates:
                if endpoint in seen:
                    continue
                seen.add(endpoint)
                full = prefix + events
                if flip.score(endpoint) < flip.score(best):
                    best, path = endpoint, full
                heapq.heappush(queue, (flip.score(endpoint), endpoint, full))
        record = {'name': row['name'], 'baseline_sha256': row['baseline_sha256'],
                  'source_key': row['source_key'], 'initial': row['initial'],
                  'events': row['events'] + path, 'endpoint': best,
                  'before_objective': flip.score(initial), 'after_objective': flip.score(best),
                  'rank': len(best), 'new_flip_events': len(path), 'new_charged_units': used,
                  'heap_pops': pops, 'discovered_states': len(seen),
                  'new_cpu_seconds': time.process_time() - cpu,
                  'new_wall_seconds': time.perf_counter() - wall,
                  'rank_preserved': len(best) == len(initial), 'automatic_destabilization': False}
        record['verification'] = verify.verify_record(record, baseline)
        records.append(record)
        time.sleep(0.05)
    summary = {'rows': len(records),
               'improved_rows': sum(r['after_objective'] < r['before_objective'] for r in records),
               'all_rank_preserved': all(r['rank_preserved'] for r in records),
               'total_length_sum': sum(r['after_objective'][2] for r in records),
               'units': sum(r['new_charged_units'] for r in records),
               'cpu_seconds': sum(r['new_cpu_seconds'] for r in records),
               'wall_seconds': sum(r['new_wall_seconds'] for r in records)}
    destination.write_text(json.dumps({'schema': 'retained_rank_triangle_flips_v1',
        'source_sha256': verify.sha(HERE / 'HIGH_RANK_TRIANGLES.json'),
        'script_sha256': verify.sha(Path(__file__)), 'summary': summary,
        'retained_rows': records}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
