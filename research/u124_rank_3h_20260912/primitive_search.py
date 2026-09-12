"""Tiny ordinary S20 continuations after certified primitive-relator projections."""
import json
from pathlib import Path
import sys
import time

import rank_peeling
from rank_peeling import lemma11, search
import verify
import whitehead

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[1]
sys.path.insert(0, str(WORKTREE))


def main():
    source = HERE / 'collector_remaining113.json'
    selected = {'aca_43', 'aca_79', 'aca_106'}
    seeds = [r for r in json.loads(source.read_text())['rows'] if r['name'] in selected]
    assert {r['name'] for r in seeds} == selected
    baseline = verify.load_baseline()
    rows, ready, warming = [], False, {}
    for seed in seeds:
        verify.verify_record(seed, baseline)
        current = tuple(map(tuple, seed['endpoint']))
        cpu, wall = time.process_time(), time.perf_counter()
        candidates, preparation = lemma11.generate_removals(current, 200, expose_primitives=True)
        candidates = [(after, events) for after, events in candidates if len(after) == 2 and
                      any(e.get('objective') == 'expose_lemma11_defining_relator' for e in events)]
        if not candidates:
            rows.append({'name': seed['name'], 'projected': False, 'preparation_units': preparation,
                         'reason': 'no rank2 projection using primitive exposure in the declared allowance'})
            continue
        projected, events = min(candidates, key=lambda row: (search.length(row[0]), row[0]))
        projected, suffix, cost, _ = whitehead.descend(projected, 40)
        preparation += cost
        events += suffix
        basis = sorted({abs(x) for w in projected for x in w})
        forward = {g: (i + 1,) for i, g in enumerate(basis)}
        backward = {i + 1: (g,) for i, g in enumerate(basis)}
        renamed = search.normalize(tuple(whitehead.apply(w, forward) for w in projected))
        events.append({'kind': 'generator_relabeling', 'before': projected, 'after': renamed,
                       'images': forward, 'inverse_images': backward})
        preparation += 1
        projection = {key: seed[key] for key in ('name', 'baseline_sha256', 'source_key', 'initial')}
        projection.update(events=seed['events'] + events, endpoint=renamed,
                          endpoint_length=search.length(renamed), endpoint_rank=len(renamed),
                          newly_charged_preparation_units=preparation)
        projection['verification'] = verify.verify_record(projection, baseline)
        prep_cpu, prep_wall = time.process_time() - cpu, time.perf_counter() - wall
        pair = tuple(''.join(('x' if abs(x) == 1 else 'y') if x > 0 else
                             ('X' if abs(x) == 1 else 'Y') for x in w) for w in renamed)
        if not ready:
            from research.theory_patterns_20260912.two_complement_search_continuation import original, captured, verify_prefix
            from research.theory_patterns_20260912.compile_search_prefix import compile_prefix
            assert search.sha(Path(original.__file__)) == captured.SOURCE_SHA256
            cpu, wall = time.process_time(), time.perf_counter()
            control = ('xyx', 'yxx')
            original_control = original.mixed_search(control, 's20', 1, cap=None)
            captured_control = captured.mixed_search(control, 's20', 1, cap=None)
            assert all(captured_control[k] == v for k, v in original_control.items())
            verify_prefix(control, captured_control)
            warming = {'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
                       'engine_sha256': search.sha(Path(original.__file__)),
                       'capture_sha256': search.sha(Path(captured.__file__))}
            ready = True
        allowance = 1000 - preparation
        cpu, wall = time.process_time(), time.perf_counter()
        outcome = captured.mixed_search(pair, 's20', budget=allowance, cap=None)
        search_cpu, search_wall = time.process_time() - cpu, time.perf_counter() - wall
        endpoint = verify_prefix(pair, outcome)
        states = outcome['states'] if outcome['solved'] else outcome['best_states']
        steps = outcome['steps'] if outcome['solved'] else outcome['best_steps']
        certificate = compile_prefix(pair, states, steps)
        assert certificate['endpoint'] == list(endpoint)
        row = {'name': seed['name'], 'projected': True, 'source_sha256': search.sha(source),
               'projection': projection, 'search_input': pair, 'search_input_length': sum(map(len, pair)),
               'preparation_units': preparation, 'heap_pop_budget': allowance,
               'heap_pops': outcome['nodes_explored'], 'combined_new_units': preparation + outcome['nodes_explored'],
               'historical_seed_work_excluded': True, 'solved': outcome['solved'],
               'best_search_pair': endpoint, 'best_search_length': sum(map(len, endpoint)),
               'phase_best_before': seed['best_length'],
               'additional_gain': seed['best_length'] - sum(map(len, endpoint)),
               'result': outcome, 'elementary_suffix': certificate,
               'preparation_cpu_seconds': prep_cpu, 'preparation_wall_seconds': prep_wall,
               'search_cpu_seconds': search_cpu, 'search_wall_seconds': search_wall,
               'relator_cap': None}
        assert row['combined_new_units'] <= 1000
        rows.append(row)
        print(row['name'], row['search_input_length'], '->', row['best_search_length'],
              'new gain', max(0, row['additional_gain']), 'solved', row['solved'], flush=True)
        time.sleep(0.2)
    output = HERE / 'primitive_search_results.json'
    assert not output.exists()
    output.write_text(json.dumps({'rows': rows, 'warmup': warming,
        'script_sha256': search.sha(Path(__file__)), 'source_sha256': search.sha(source),
        'scope': 'At most1000 newly charged preparation checks plus ordinary heap pops per row; heterogeneous units. Three selected new endpoints, no baseline rerun. Historical seed discovery and independent verification excluded.'}, indent=2) + '\n')
    print(json.dumps({'rows': len(rows), 'projected': sum(r['projected'] for r in rows),
                      'solved': sum(r.get('solved', False) for r in rows)}))


if __name__ == '__main__':
    main()
