"""Small serial planted and exact-panel checks; no search, imports of JIT, or baselines."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import boundary_compiler as subject
from check_ac_words import independent_replay, inverse, legacy_replayer, reduce_word


HERE = Path(__file__).resolve().parent


def indexed_word(letters, stable):
    base = 'y' if stable == 'x' else 'x'
    def pw(letter, exponent):
        return letter * exponent if exponent >= 0 else inverse(letter) * -exponent
    return reduce_word(''.join(pw(stable, index) + pw(base, sign) + pw(stable, -index)
                               for index, sign in letters))


def make_pair(f, g, stable, role, rsign, ssign):
    r = reduce_word(indexed_word(f, stable) + stable)
    s = indexed_word(g, stable)
    r = r if rsign == 1 else inverse(r)
    s = s if ssign == 1 else inverse(s)
    pair = [r, s] if role == 0 else [s, r]
    return pair


def inspect_certificate(pair, result, legacy=None):
    for prefix in ('final', 'best'):
        moves = result['moves' if prefix == 'final' else 'best_moves']
        expected = result['final_pair' if prefix == 'final' else 'best_pair']
        assert independent_replay(pair, moves) == expected
        assert subject.replay(pair, moves) == expected
        if legacy:
            assert legacy(pair, moves) == expected
    assert result['charges'] <= result['limits']['budget'] <= 1000
    assert len(result['moves']) <= result['limits']['max_moves']
    assert all(p['empty_after'] or p['after_span'] < p['before_span'] for p in result['passes'])
    assert all(l.get('after_boundary_letters', -1) < l.get('before_boundary_letters', 0)
               for l in result['ledgers'])
    return True


def compact_result(result, include_moves=True):
    omitted = set() if include_moves else {'moves', 'best_moves', 'ledgers'}
    return {k: v for k, v in result.items() if k not in omitted}


def planted_checks(legacy):
    counts = Counter()
    samples = []
    for m, side, eta, stable, role, rsign, ssign in itertools.product(
            (2, 3, 5), ('lower', 'upper'), (-1, 1), 'xy', (0, 1), (-1, 1), (-1, 1)):
        if side == 'lower':
            f = ((0, eta),) * m + ((2, 1),) * (m + 1)
            g = ((0, 1),) * m + ((1, -1),) * (m + 1)
        else:
            f = ((0, 1),) * (m + 1) + ((2, eta),) * m
            g = ((0, -1),) * (m + 1) + ((1, 1),) * m
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_pair(pair, stable=stable, source_index=role,
                                      boundary_order=(side, 'upper' if side == 'lower' else 'lower'))
        assert result['reason'] == 'solved', (m, side, eta, stable, role, rsign, ssign, result['reason'])
        assert result['final_pair'] == ['x', 'y']
        assert any(p['rule'] == 'extreme_power' and p['m'] > 1 for p in result['passes'])
        assert any(p['rule'] == 'stable_boundary' for p in result['passes'])
        inspect_certificate(pair, result, legacy)
        counts['nonmonic_alternating_solutions'] += 1
        if len(samples) < 4:
            samples.append({'label': [m, side, eta, stable, role, rsign, ssign], 'result': result})

    f = ((0, 1), (1, 1), (0, -1), (1, 1))
    g = ((0, 1), (3, 1), (0, -1), (3, -1), (1, 1))
    for side, stable, role, rsign, ssign in itertools.product(('lower', 'upper'), 'xy', (0, 1), (-1, 1), (-1, 1)):
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_boundary_pass(pair, stable=stable, source_index=role, side=side)
        assert result['reason'] == 'boundary_pass_complete'
        assert result['final_pair'][role] == pair[role]
        inspect_certificate(pair, result, legacy)
        counts['repeated_extreme_source_transport'] += 1

    for stable, role, rsign, ssign, index, empty_f in itertools.product('xy', (0, 1), (-1, 1), (-1, 1), (-3, 0, 2), (False, True)):
        f = () if empty_f else ((-2, 1), (3, -1), (0, 1))
        g = ((index, 1),)
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_pair(pair, stable=stable, source_index=role)
        assert result['reason'] == 'solved'
        inspect_certificate(pair, result, legacy)
        counts['empty_or_span_zero_terminal'] += 1

    failures = [
        ('divisibility', ((0, 1), (2, 1)), ((0, 1),) * 2 + ((1, -1),) * 3,
         'extreme_run_not_divisible'),
        ('nonunique', ((0, 1), (2, 1)), ((0, 1), (1, 1), (0, -1), (1, 1), (0, -1)),
         'extreme_not_one_literal_run'),
    ]
    for label, f, g, expected_failure in failures:
        pair = make_pair(f, g, 'x', 0, 1, 1)
        result = subject.compile_pair(pair)
        assert result['reason'] == 'criterion_failed', (label, result['reason'])
        assert all(b['reason'] == expected_failure for b in result['failed_checkpoint']['boundaries'])
        inspect_certificate(pair, result, legacy)
        counts['explicit_failed_hypothesis'] += 1

    pair = ['YYYxyXyX', 'YYXXyxx']
    for budget in range(14):
        result = subject.compile_boundary_pass(pair, limits=subject.Limits(budget=budget))
        assert result['final_pair'][0] == pair[0]
        inspect_certificate(pair, result, legacy)
        counts['every_small_budget_preserves_source'] += 1
    for field, value in [('max_word_length', 8), ('max_indexed_length', 3), ('max_moves', 10)]:
        kwargs = {field: value}
        result = subject.compile_boundary_pass(pair, limits=subject.Limits(**kwargs))
        expected = {'max_word_length': 'word_limit', 'max_indexed_length': 'indexed_word_limit',
                    'max_moves': 'certificate_limit'}[field]
        assert result['reason'] == expected, (field, result['reason'])
        assert result['final_pair'][0] == pair[0]
        inspect_certificate(pair, result, legacy)
        counts['resource_reason_and_atomic_rollback'] += 1

    result = subject.compile_pair(['x', ''])
    assert result['reason'] == 'not_unimodular'
    inspect_certificate(['x', ''], result, legacy)
    counts['empty_zero_fibre_rejected_before_theorem'] += 1
    invalid_calls = [lambda: subject.compile_pair(['z', 'y'], limits=subject.Limits(budget=0)),
                     lambda: subject.compile_pair(['x' * 5000, 'z']),
                     lambda: subject.compile_pair(['x', 'y'], source_index=True),
                     lambda: subject.compile_pair(['x', 'y'], source_index=0.0),
                     lambda: subject.compile_pair(['x', 'y'], stable='X'),
                     lambda: subject.compile_pair(['x', 'y'], limits=0),
                     lambda: subject.Limits(budget=1001), lambda: subject.Limits(budget=True),
                     lambda: subject.Limits(max_moves=1.0),
                     lambda: subject.compile_boundary_pass(pair, q=100),
                     lambda: subject.compile_boundary_pass(pair, q=True)]
    for call in invalid_calls:
        try:
            call()
        except ValueError:
            counts['invalid_api_rejected'] += 1
        else:
            raise AssertionError('invalid API call was accepted')
    return {'counts': dict(counts), 'total': sum(counts.values()), 'samples': samples}


def cohort_checks(inventory_path, legacy, all_rows=False, reuse=()):
    inventory = json.loads(inventory_path.read_text())
    rows = inventory['rows'] if all_rows else inventory['panel']['rows']
    expected_count = 124 if all_rows else 20
    assert len(rows) == expected_count and len({r['name'] for r in rows}) == expected_count
    previous = {r['name']: r for r in reuse}
    records = []
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    for row in rows:
        pair = [row['r1'], row['r2']]
        if row['name'] in previous:
            saved = previous[row['name']]
            assert saved['input'] == pair
            records.append(saved)
            continue
        remaining = 1000
        attempts = []
        wall, cpu = time.perf_counter(), time.process_time()
        for stable, role, side in itertools.product('xy', (0, 1), ('lower', 'upper')):
            if remaining <= 0:
                break
            result = subject.compile_pair(pair, stable=stable, source_index=role,
                boundary_order=(side, 'upper' if side == 'lower' else 'lower'),
                limits=subject.Limits(budget=remaining, max_word_length=512,
                                      max_indexed_length=256, max_moves=12000))
            inspect_certificate(pair, result, legacy)
            remaining -= result['charges']
            attempts.append(result)
            if result['status'] == 'solved':
                break
        best = min(attempts, key=lambda a: a['best_length'])
        records.append({'name': row['name'], 'input': pair, 'input_length': sum(map(len, pair)),
                        'charges': 1000 - remaining, 'solved': any(a['status'] == 'solved' for a in attempts),
                        'best_pair': best['best_pair'], 'best_length': best['best_length'],
                        'strict_length_improvement': best['best_length'] < sum(map(len, pair)),
                        'wall_seconds': time.perf_counter() - wall, 'cpu_seconds': time.process_time() - cpu,
                        'attempts': attempts})
    return {'ids': [r['name'] for r in records], 'size': len(records),
            'selection': 'All 124 exact saved best-state inputs; retained bounded AC/Aut components, not 124 proved distinct classes.' if all_rows else inventory['panel']['selection'],
            'reused_records': len(previous), 'fresh_records': len(rows) - len(previous), 'records': records,
            'solved': [r['name'] for r in records if r['solved']],
            'strict_length_improved': [r['name'] for r in records if r['strict_length_improvement']],
            'charges': sum(r['charges'] for r in records),
            'completed_boundary_passes': sum(sum(p['rule'] == 'stable_boundary' for p in a['passes'])
                                              for r in records for a in r['attempts']),
            'completed_power_passes': sum(sum(p['rule'] == 'extreme_power' for p in a['passes'])
                                           for r in records for a in r['attempts']),
            'wall_seconds': time.perf_counter() - started_wall,
            'cpu_seconds': time.process_time() - started_cpu}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--legacy-replay-source', type=Path)
    parser.add_argument('--all-u124', action='store_true')
    args = parser.parse_args()
    legacy, legacy_hash = legacy_replayer(args.legacy_replay_source) if args.legacy_replay_source else (None, None)
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    planted = planted_checks(legacy)
    panel = cohort_checks(args.inventory, legacy)
    full = cohort_checks(args.inventory, legacy, all_rows=True, reuse=panel['records']) if args.all_u124 else None
    report = {'status': 'pass', 'compiler_sha256': hashlib.sha256(Path(subject.__file__).read_bytes()).hexdigest(),
              'checks_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'inventory_sha256': hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
              'legacy_replay_sha256': legacy_hash, 'planted': planted, 'panel': panel, 'full_u124': full,
              'wall_seconds': time.perf_counter() - start_wall,
              'cpu_seconds': time.process_time() - start_cpu,
              'scope': 'Literal raw xXyY axes and relator roles, deterministic boundary orders; no heap, JIT, baseline rerun or frozen-data modification.'}
    (HERE / 'boundary_compiler_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'planted_checks': planted['total'],
                      'panel_solved': panel['solved'], 'panel_strict_length_improved': panel['strict_length_improved'],
                      'panel_charges': panel['charges'], 'full_u124_gains': full['strict_length_improved'] if full else None,
                      'full_u124_charges': full['charges'] if full else None, 'wall_seconds': report['wall_seconds'],
                      'cpu_seconds': report['cpu_seconds']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
