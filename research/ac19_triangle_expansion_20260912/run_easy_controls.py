"""Run the same retained-rank triangular search on frozen easy AC19 controls."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import run_panel as base


HERE = Path(__file__).resolve().parent
PANEL = HERE / 'easy_control_panel.jsonl'
PANEL_SHA256 = 'd5c2ba68ff958ffff31a1233b282d83829aecf0b7612a47c55ecf55a5f7767ae'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing to overwrite output')
    if sha(PANEL) != PANEL_SHA256:
        raise AssertionError('easy-control panel changed')
    sources = [json.loads(line) for line in PANEL.read_text().splitlines()]
    if len(sources) != 12 or len({row['name'] for row in sources}) != 12:
        raise AssertionError('easy-control denominator changed')
    rows = []
    for source in sources:
        if not source['solved'] or not source['elementary_verified']:
            raise AssertionError('control lacks a verified saved solve')
        if source['states'][0] != source['pair'] or source['states'][-1] != ['Y', 'X']:
            raise AssertionError('control certificate endpoints changed')
        original = base.fixed_engine.search.normalize(
            tuple(base.parse_word(word) for word in source['pair']))
        cpu, wall = time.process_time(), time.perf_counter()
        expanded, events, units = base.triangulate(original)
        expansion_cpu = time.process_time() - cpu
        expansion_wall = time.perf_counter() - wall
        if base.excess(expanded) or base.replay_expansion(original, events) != expanded:
            raise AssertionError(source['name'] + ': expansion failed')
        result = base.phase(expanded, pops=100, cap=4, beam=128,
                            neighborhood='short_macros')
        compiled = base.terminal_compile(result['endpoint'])
        if result['solved_to_length_at_most_two'] != (compiled is not None):
            raise AssertionError(source['name'] + ': terminal status differs')
        rows.append({
            'name': source['name'],
            'rank2_policy_nodes': source['nodes_explored'],
            'original': original,
            'expanded': expanded,
            'expansion_events': events,
            'expansion_units': units,
            'expansion_cpu_seconds': expansion_cpu,
            'expansion_wall_seconds': expansion_wall,
            'retained_rank': len(expanded),
            'macro': result,
            'terminal_compiler': compiled,
            'solved_at_retained_rank': compiled is not None,
        })
    report = {
        'schema': 'ac19_easy_control_retained_triangle_search_v1',
        'panel_sha256': sha(PANEL),
        'source_sha256': {
            'run_easy_controls.py': sha(Path(__file__)),
            'run_panel.py': sha(HERE / 'run_panel.py'),
        },
        'summary': {
            'rows': len(rows),
            'solved_at_retained_rank': sum(row['solved_at_retained_rank'] for row in rows),
            'macro_pops': sum(row['macro']['heap_pops'] for row in rows),
            'rotation_products': sum(row['macro']['generated_rotation_products'] for row in rows),
            'search_cpu_seconds': sum(row['macro']['cpu_seconds'] for row in rows),
            'search_wall_seconds': sum(row['macro']['wall_seconds'] for row in rows),
        },
        'scope': 'Same fixed-rank macro search as the hard panel; no destabilization.',
        'rows': rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial = args.output.with_suffix(args.output.suffix + '.partial')
    partial.write_text(json.dumps(report, indent=2) + '\n')
    partial.replace(args.output)
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
