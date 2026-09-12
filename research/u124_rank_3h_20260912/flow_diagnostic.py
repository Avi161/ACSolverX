"""Record exactly which fixed-donor flow exclusions were completely checked."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import theory_flow_exact as flow
import verify

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to overwrite a diagnostic')
    baseline = verify.load_baseline()
    records = []
    for name, row in baseline.items():
        initial = verify.normalized(row['words'])
        cpu, wall = time.process_time(), time.perf_counter()
        audits = []
        candidates, charged = flow.probe(initial, 1000, audits=audits)
        cpu, wall = time.process_time() - cpu, time.perf_counter() - wall
        best, events = initial, []
        for endpoint, path in candidates:
            current = initial
            for event in path:
                if verify.words(event['before']) != current:
                    raise AssertionError('flow diagnostic path discontinuity')
                current = verify.verify_event(event, known_trivial=True)
            if current != endpoint:
                raise AssertionError('flow diagnostic endpoint differs')
            if (verify.size(endpoint), len(endpoint)) < (verify.size(best), len(best)):
                best, events = endpoint, path
        record = {'name': name, 'baseline_sha256': verify.BASELINE_SHA256, 'source_key': 'current_best',
                  'initial': initial, 'events': events, 'endpoint': best,
                  'input_length': row['length'], 'best_length': verify.size(best), 'best_rank': len(best),
                  'gain': row['length'] - verify.size(best), 'total_units': charged,
                  'cpu_seconds': cpu, 'wall_seconds': wall, 'flow_audits': audits,
                  'matched_root_definitions': len(flow.corridor.roots(initial)),
                  'verified_candidate_count': len(candidates)}
        record['verification'] = verify.verify_record(record, baseline)
        records.append(record)
        if audits:
            print(name, 'complete', sum(a.get('flow_complete', False) for a in audits),
                  'of', len(audits), 'flowcases', 'gain', record['gain'], flush=True)
        time.sleep(0.02)
    audits = [audit for record in records for audit in record['flow_audits']]
    summary = {'rows': len(records), 'root_bearing_rows': sum(r['matched_root_definitions'] > 0 for r in records),
               'flow_cases': len(audits), 'complete_flow_cases': sum(a.get('flow_complete', False) for a in audits),
               'incomplete_flow_cases': sum(not a.get('flow_complete', False) for a in audits),
               'found_flows': sum(a.get('found_flow') is not None for a in audits),
               'gain_ids': [r['name'] for r in records if r['gain'] > 0],
               'total_units': sum(r['total_units'] for r in records),
               'cpu_seconds': sum(r['cpu_seconds'] for r in records),
               'wall_seconds': sum(r['wall_seconds'] for r in records)}
    output.write_text(json.dumps({'baseline_sha256': verify.BASELINE_SHA256,
                                 'hashes': {p.name: verify.sha(p) for p in
                                            [Path(__file__), Path(flow.__file__), Path(flow.corridor.__file__)]},
                                 'rows': records, 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
