"""Serial exact-word checks and fixed U124 prepared-frame screen; no search/JIT."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import prepared_frames as subject
from check_ac_words import independent_replay, inverse, legacy_replayer, reduce_word

HERE = Path(__file__).resolve().parent


def verify(pair, result, legacy=None):
    for path, expected in ((result['moves'], result['final_pair']),
                           (result['best_moves'], result['best_pair'])):
        assert independent_replay(pair, path) == expected
        assert subject.replay(pair, path) == expected
        if legacy:
            assert legacy(pair, path) == expected
    assert result['charges'] <= result['limits']['budget'] <= 1000
    assert len(result['moves']) <= result['limits']['max_moves']


def verify_portfolio(result, legacy=None):
    pair = result['input']
    assert independent_replay(pair, result['best_moves']) == result['best_pair']
    assert len(result['best_moves']) <= result['limits']['max_moves']
    total = 0
    for attempt in result['attempts']:
        prep = attempt['preparation']
        verify(pair, prep, legacy)
        total += prep['charges']
        for step in prep['steps']:
            assert gcd(*step['before_column']) == gcd(*step['after_column'])
            assert sum(map(abs, step['after_column'])) < sum(map(abs, step['before_column']))
        for theorem in attempt['theorem_calls']:
            verify(prep['final_pair'], theorem, legacy)
            total += theorem['charges']
            for moves, expected in ((theorem['composed_moves'], theorem['final_pair']),
                                    (theorem['composed_best_moves'], theorem['best_pair'])):
                assert independent_replay(pair, moves) == expected
                if legacy:
                    assert legacy(pair, moves) == expected
                assert len(moves) <= result['limits']['max_moves']
    assert total == result['charges'] == result['framing_charges'] + result['theorem_charges']
    assert 0 <= total <= result['limits']['budget'] <= 1000
    assert result['best_length'] == sum(map(len, result['best_pair']))
    assert result['strict_length_improvement'] == (result['best_length'] < result['input_length'])


def planted_checks(legacy=None):
    counts = Counter()
    for first, second, target, sign, side in itertools.product(
            ('x', 'xyX', 'xxYYx'), ('y', 'Yxy', 'yyXXy'), (0, 1), (-1, 1), ('right', 'left')):
        pair = [first, second]
        trace = subject.Trace(pair)
        donor = pair[1 - target] if sign == 1 else inverse(pair[1 - target])
        expected = list(pair)
        expected[target] = reduce_word(pair[target] + donor if side == 'right' else donor + pair[target])
        subject.signed_product(trace, target, sign, side)
        assert trace.pair == expected and independent_replay(pair, trace.moves) == expected
        if legacy:
            assert legacy(pair, trace.moves) == expected
        counts['signed_left_right_products'] += 1
    for a, b, side, tie in itertools.product(range(-6, 7), range(-6, 7), ('left', 'right'), (0, 1)):
        pair = [('x' * a if a >= 0 else 'X' * -a) + 'y',
                ('x' * b if b >= 0 else 'X' * -b) + 'yy']
        result = subject.prepare_frame(pair, side=side, tie_target=tie)
        assert result['reason'] == ('frame_ready' if gcd(a, b) == 1 else 'column_not_primitive')
        assert sorted(map(abs, result['final_column'])) == [0, gcd(a, b)]
        verify(pair, result, legacy)
        counts['euclidean_columns'] += 1
    for pair, stable in itertools.product((['xyX', 'Yxxxy'], ['xxy', 'xxxyy'], ['XY', 'yx']), 'xy'):
        result = subject.prepare_frame(pair, stable=stable, orientation='min_span')
        verify(pair, result, legacy)
        counts['explicit_cyclic_orientation_witnesses'] += 1
    solved_examples = []
    for pair in (['x', 'y'], ['xxy', 'xxxyy'], ['yx', 'xyy'], ['YXX', 'YYXXX']):
        exps = [[subject.exponent(w, g) for g in 'xy'] for w in pair]
        assert abs(exps[0][0] * exps[1][1] - exps[0][1] * exps[1][0]) == 1
        result = subject.compile_prepared(pair)
        verify_portfolio(result, legacy)
        assert result['solved'], (pair, result['best_pair'])
        solved_examples.append({'input': pair, 'best_pair': result['best_pair'],
                                'best_moves': result['best_moves'], 'charges': result['charges']})
        counts['prepared_solutions'] += 1
    for budget in range(26):
        for pair in (['xxy', 'xxxyy'], ['YXXyxYx', 'YYYYYYXyxyX']):
            result = subject.compile_prepared(pair, limits=subject.Limits(budget=budget))
            verify_portfolio(result, legacy)
            counts['every_small_shared_budget'] += 1
    for word_limit, move_limit in ((0, 12000), (1, 12000), (512, 0), (512, 1), (512, 2)):
        result = subject.compile_prepared(['xyX', 'Yxxxy'], limits=subject.Limits(
            budget=1000, max_word_length=word_limit, max_moves=move_limit))
        verify_portfolio(result, legacy)
        counts['word_certificate_resource_stops'] += 1
    for kwargs in ({'stable': 'z'}, {'orientation': 'all'}, {'tie_target': True}, {'tie_target': 1.0}, {'side': 'bad'}):
        try:
            subject.prepare_frame(['x', 'y'], **kwargs)
        except ValueError:
            counts['malformed_rejections'] += 1
        else:
            raise AssertionError(kwargs)
    for pair in (['z', 'y'], ['x', 'z'], ['x'], [None, 'y']):
        try:
            subject.compile_prepared(pair, limits=subject.Limits(budget=0))
        except ValueError:
            counts['malformed_rejections'] += 1
        else:
            raise AssertionError(pair)
    return {'counts': dict(counts), 'total': sum(counts.values()), 'solved_examples': solved_examples}


def summarize(records):
    calls = [c for r in records for a in r['attempts'] for c in a['theorem_calls']]
    return {'size': len(records), 'ids': [r['name'] for r in records],
            'solved_ids': [r['name'] for r in records if r['solved']],
            'strict_length_improved_ids': [r['name'] for r in records if r['strict_length_improvement']],
            'charges': sum(r['charges'] for r in records),
            'framing_charges': sum(r['framing_charges'] for r in records),
            'theorem_charges': sum(r['theorem_charges'] for r in records),
            'maximum_charges_per_input': max(r['charges'] for r in records),
            'theorem_calls': len(calls),
            'theorem_reasons': dict(Counter(c['reason'] for c in calls)),
            'preparation_reasons': dict(Counter(a['preparation']['reason'] for r in records for a in r['attempts'])),
            'completed_boundary_passes': sum(p['rule'] == 'stable_boundary' for c in calls for p in c['passes']),
            'completed_power_passes': sum(p['rule'] == 'extreme_power' for c in calls for p in c['passes']),
            'rows_with_completed_passes': [r['name'] for r in records if any(c['passes'] for a in r['attempts'] for c in a['theorem_calls'])],
            'sum_starting_best_length': sum(r['starting_best_length'] for r in records),
            'sum_new_best_length': sum(r['best_length'] for r in records),
            'max_composed_certificate_moves': max((c['composed_elementary_moves'] for c in calls), default=0),
            'cooldown_seconds': sum(r.get('cooldown_seconds', 0.0) for r in records),
            'algorithm_wall_seconds': sum(r['wall_seconds'] for r in records),
            'algorithm_cpu_seconds': sum(r['cpu_seconds'] for r in records)}


def save_jsonl(path, records):
    temporary = path.with_name(path.name + '.partial')
    data = ''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in records).encode()
    if path.suffix == '.gz':
        with temporary.open('wb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as stream:
                stream.write(data)
    else:
        temporary.write_bytes(data)
    temporary.replace(path)


def cohort(rows, source_rows, initial_rows, legacy=None, reuse=(), cooldown_seconds=0.2):
    previous = {r['name']: r for r in reuse}
    result = []
    for row in rows:
        name = row['name']
        pair = [row['r1'], row['r2']]
        assert [source_rows[name]['r1'], source_rows[name]['r2']] == pair
        if name in previous:
            record = previous[name]
            assert record['input'] == pair
        else:
            record = subject.compile_prepared(pair)
            record.update({'name': name, 'starting_best_length': sum(map(len, pair)),
                           'archival_initial_length': sum(len(initial_rows[name][k]) for k in ('r1', 'r2'))})
            verify_portfolio(record, legacy)
            cooldown_started = time.perf_counter()
            if cooldown_seconds:
                time.sleep(cooldown_seconds)
            record['cooldown_seconds'] = time.perf_counter() - cooldown_started if cooldown_seconds else 0.0
        result.append(record)
    assert len(result) == len({r['name'] for r in result})
    return result


def write_markdown(report, records):
    full = report['full_u124'] or report['panel']
    lines = ['# Prepared ordinary AC frames', '',
        f"The fixed {'124-row' if report['full_u124'] else '20-row'} screen found **{len(full['solved_ids'])} solves and {len(full['strict_length_improved_ids'])} strict total-length improvements** over the authoritative saved best inputs.", '',
        'The portfolio is finite: x/y columns, literal/minimum-span cyclic orientations, left/right signed row products, and target 0/1 tie resolution (16 preparation branches maximum). Each distinct prepared frame tries lower-first and upper-first boundary orders. It uses no ambient automorphism, stabilization, heap, JIT, or saved baseline rerun. Minimum-span orientation scores every literal cyclic rotation and emits its prefix conjugation explicitly. Both relators are cyclically reduced by explicit conjugations before preparation; each updated target is similarly reduced after a row product.', '',
        'For a column (a,b) with both entries nonzero, choose a target with larger absolute value (the fixed target breaks equality). Replace that relator by its signed product with the other, choosing the sign that subtracts the smaller absolute entry. The resulting absolute target entry is |a|-|b| (with roles exchanged if necessary), so |a|+|b| strictly decreases by the smaller positive absolute entry. Elementary row operations preserve gcd, hence primitive columns terminate at (±1,0) in one of the two relator orders. The compiler receives the actual source index; no relator swap or basis change is implicit. Left multiplication A←B^s A is emitted as A←A^-1, A←A B^-s, A←A^-1, with donor inversion restored inside the signed right multiplication.', '',
        'All branches start from the original saved-best pair. Framing recognizes a column for one charge, scores each orientation candidate for one, charges one per whole-word orientation/cleanup conjugation, and charges every inversion or multiplication used for signed row products. Each Euclidean step has a separate recognition charge. Preparation is capped at 128 charges per branch and each theorem call at 128, all deducted from one shared limit of 1,000 per input. Duplicates are detected only after paid preparation and avoid repeated theorem calls. Discarded resource-limited staged operations remain charged. Emitted generator-level certificate length is recorded separately. Validation, certificate emission/replay and output costs are outside algebraic charges and inside wall/CPU measurements.', '',
        'The preselected20 was run and verified first. Full124 reuses those records and evaluates only the remaining104. These retained bounded AC/Aut components are an upper bound, not124 proved distinct AC classes. The20-row structural panel is a development diagnostic, not a representative validation sample.', '',
        f"Checks: {report['planted']['total']} planted/edge cases; every preparation final/best path and every composed theorem final/best path independently replays. Sources are pinned by SHA-256 in `prepared_frames_report.json`.", '',
        '| cohort | solved | strict length gains | framing charges | theorem charges | total charges | algorithm wall s | algorithm CPU s |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for key in ('panel', 'full_u124'):
        value = report[key]
        if value:
            lines.append(f"| {key} ({value['size']}) | {len(value['solved_ids'])} | {len(value['strict_length_improved_ids'])} | {value['framing_charges']} | {value['theorem_charges']} | {value['charges']} | {value['algorithm_wall_seconds']:.6f} | {value['algorithm_cpu_seconds']:.6f} |")
    lines += ['', f"Maximum per-input work: {full['maximum_charges_per_input']}; theorem calls: {full['theorem_calls']}; completed stable-boundary passes: {full['completed_boundary_passes']}; completed extreme-power passes: {full['completed_power_passes']}; largest composed certificate: {full['max_composed_certificate_moves']} elementary moves.", '',
        'A completed span-decreasing pass is an algebraic rewrite result; it is not an ordinary total-length gain. Every branch records its exact final pair, best prefix pair, initial potential, final spans, failed checkpoint and composed ordinary certificate. Best-prefix total length is compared directly with the authoritative saved-best original, separately from the archival initial input.', '',
        'The theorem reason counts are `' + json.dumps(full['theorem_reasons'], sort_keys=True) + '`.', '',
        '| row | solved | archival initial | starting best | new best | charges | best elementary moves |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {r['name']} | {str(r['solved']).lower()} | {r['archival_initial_length']} | {r['starting_best_length']} | {r['best_length']} | {r['charges']} | {r['best_elementary_moves']} |")
    (HERE / 'prepared_frames_report.md').write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-u124', action='store_true')
    parser.add_argument('--cooldown-seconds', type=float, default=0.2)
    parser.add_argument('--legacy-replay-source', type=Path)
    args = parser.parse_args()
    if not 0 <= args.cooldown_seconds <= 60:
        parser.error('--cooldown-seconds must be from 0 through 60')
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    inventory_path = HERE / 'u124_inventory.json'
    inventory = json.loads(inventory_path.read_text())
    root = HERE.parents[1]
    paths = {key: root / inventory['sources'][key]['path'] for key in ('best', 'initial')}
    tables = {}
    for key, path in paths.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == inventory['sources'][key]['sha256']
        with path.open() as stream:
            tables[key] = {row['name']: row for row in csv.DictReader(stream)}
        assert len(tables[key]) == 124
    legacy, legacy_hash = legacy_replayer(args.legacy_replay_source) if args.legacy_replay_source else (None, None)
    planted = planted_checks(legacy)
    saved_panel = []
    if args.all_u124 and (HERE / 'prepared_frames_panel20.jsonl').exists():
        prior = json.loads((HERE / 'prepared_frames_report.json').read_text())
        assert prior['source_hashes']['prepared_frames.py'] == hashlib.sha256(Path(subject.__file__).read_bytes()).hexdigest()
        assert prior['source_hashes']['boundary_compiler.py'] == hashlib.sha256((HERE / 'boundary_compiler.py').read_bytes()).hexdigest()
        saved_panel = [json.loads(line) for line in (HERE / 'prepared_frames_panel20.jsonl').read_text().splitlines()]
    panel = cohort(inventory['panel']['rows'], tables['best'], tables['initial'], legacy, reuse=saved_panel, cooldown_seconds=args.cooldown_seconds)
    assert len(panel) == 20
    save_jsonl(HERE / 'prepared_frames_panel20.jsonl', panel)
    full = cohort(inventory['rows'], tables['best'], tables['initial'], legacy, reuse=panel, cooldown_seconds=args.cooldown_seconds) if args.all_u124 else None
    if full:
        assert len(full) == 124 and {r['name'] for r in full} == set(inventory['ids'])
        save_jsonl(HERE / 'prepared_frames_full124.jsonl.gz', full)
    report = {'status': 'pass', 'planted': planted, 'panel': summarize(panel),
              'full_u124': summarize(full) if full else None,
              'panel_records_reused_in_full': 20 if full else 0,
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                (Path(subject.__file__), Path(__file__), HERE / 'boundary_compiler.py',
                                 HERE / 'ac_words.py', inventory_path, *paths.values())},
              'legacy_replay_sha256': legacy_hash,
              'wall_seconds_including_independent_checks': time.perf_counter() - start_wall,
              'cpu_seconds_including_independent_checks': time.process_time() - start_cpu}
    (HERE / 'prepared_frames_report.json').write_text(json.dumps(report, indent=2) + '\n')
    write_markdown(report, full or panel)
    print(json.dumps({k: report[k] for k in ('status', 'panel', 'full_u124', 'wall_seconds_including_independent_checks', 'cpu_seconds_including_independent_checks')}))


if __name__ == '__main__':
    main()
