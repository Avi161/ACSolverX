"""Independent planted residue/cyclic-cut checks and saved-checkpoint extension."""
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
import boundary_compiler as frozen
from boundary_compiler_checks import make_pair
from check_ac_words import independent_replay, legacy_replayer
import extreme_residues as subject

HERE = Path(__file__).resolve().parent


def verify(pair, result, legacy, prefix=()):
    for key, endpoint in [('moves', 'final_pair'), ('best_moves', 'best_pair')]:
        stream = list(prefix) + result[key]
        assert frozen.replay(pair, stream) == result[endpoint]
        assert independent_replay(pair, stream) == result[endpoint]
        if legacy:
            assert legacy(pair, stream) == result[endpoint]
    assert result['charges'] <= result['limits']['budget'] <= 1000
    for ledger in result['ledgers']:
        assert ledger['after_boundary_letters'] < ledger['before_boundary_letters']
    return True


def planted_checks(legacy):
    counts = Counter()
    samples = []
    for m, recipient_sign, short, side, stable, role, rsign, ssign in itertools.product(
            (3, 4, 5), (-1, 1), (False, True), ('lower', 'upper'), 'xy', (0, 1), (-1, 1), (-1, 1)):
        k = recipient_sign * (m - 1 if short else m + 1)
        if side == 'upper':
            C = ((0, 1), (1, -1), (0, 1))
            E = ((1, 1), (0, -1), (1, 1))
            g = C + ((2, 1),) * m + E
            f = ((0, 1),) + ((4, recipient_sign),) * abs(k) + ((1, -1),)
        else:
            C = ((1, 1), (2, -1), (1, 1))
            E = ((2, 1), (1, -1), (2, 1))
            g = C + ((0, 1),) * m + E
            f = ((3, 1),) + ((-2, recipient_sign),) * abs(k) + ((1, -1),)
        assert frozen.ired(C + E) != frozen.ired(E + C)
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_residues(pair, stable=stable, source_index=role, side=side,
                                          nearest=True, allow_cyclic_cut=False)
        assert result['reason'] == 'residue_prefix_complete'
        assert result['residue_summary']['before_multiplicity'] == abs(k)
        assert result['residue_summary']['after_multiplicity'] == 1
        assert not result['residue_summary']['span_strictly_decreased']
        assert result['final_pair'][1 - role] == pair[1 - role]
        assert any(l['virtual_chunk'] for l in result['ledgers']) == short
        verify(pair, result, legacy)
        counts['noncommuting_context_all_signs_roles_axes'] += 1
        if len(samples) < 4:
            samples.append({'label': [m, k, side, stable, role, rsign, ssign], 'result': result})

    for side, stable, role, rsign, ssign in itertools.product(('lower', 'upper'), 'xy', (0, 1), (-1, 1), (-1, 1)):
        extreme = 0 if side == 'lower' else 3
        middle = ((1, 1), (2, -1))
        g = ((extreme, 1),) + middle + ((extreme, 1),) * 2
        f = ((extreme, 1),) * 2 + ((3 - extreme, -1),)
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_residues(pair, stable=stable, source_index=role, side=side)
        assert result['reason'] == 'residue_prefix_complete'
        assert len(result['preparations']) == 1
        assert result['residue_summary']['m'] == 3
        assert result['residue_summary']['after_multiplicity'] == 1
        assert result['final_pair'][1 - role] == result['preparations'][0]['after']
        verify(pair, result, legacy)
        counts['cyclic_split_run_merged_with_conjugation'] += 1

    for stable, role, rsign, ssign in itertools.product('xy', (0, 1), (-1, 1), (-1, 1)):
        pair = make_pair(((0, 1), (3, 1)), ((0, 1), (1, 1), (0, -1)), stable, role, rsign, ssign)
        result = subject.compile_residues(pair, stable=stable, source_index=role, side='lower')
        assert result['reason'] == 'span_zero_donor_after_cyclic_cut'
        assert len(result['preparations']) == 1
        verify(pair, result, legacy)
        counts['opposite_split_runs_cancel_to_terminal_donor'] += 1

    pair = make_pair(((0, 1), (3, 1)), ((0, 1), (1, 1), (1, 1), (0, -1)), 'x', 0, 1, 1)
    result = subject.compile_residues(pair)
    assert result['reason'] == 'span_zero_donor_after_cyclic_cut'
    assert result['status'] == 'partial' and abs(frozen.exponent(result['final_pair'][1], 'y')) == 2
    verify(pair, result, legacy)
    counts['proper_power_donor_is_not_claimed_terminal'] += 1

    for m, k, nearest, expected in [(3, 2, False, 'no_strict_residue_step'),
                                  (4, 2, True, 'no_strict_residue_step'),
                                  (3, 7, False, 'residue_prefix_complete'),
                                  (3, -7, False, 'residue_prefix_complete')]:
        f = ((0, 1 if k > 0 else -1),) * abs(k) + ((2, 1),)
        g = ((0, 1),) * m + ((1, -1),) * (m - 1)
        pair = make_pair(f, g, 'x', 0, 1, 1)
        result = subject.compile_residues(pair, nearest=nearest)
        assert result['reason'] == expected
        verify(pair, result, legacy)
        counts['floor_and_exact_half_threshold'] += 1

    pair = make_pair(((0, 1),) * 2 + ((2, 1),), ((0, 1),) * 3 + ((1, -1),) * 2, 'x', 0, 1, 1)
    for budget in range(15):
        result = subject.compile_residues(pair, limits=frozen.Limits(budget=budget))
        assert result['final_pair'][1] == pair[1]
        verify(pair, result, legacy)
        counts['small_shared_budget_prefixes'] += 1
    for field, value, expected in [('max_word_length', 8, 'word_limit'),
                                    ('max_moves', 4, 'certificate_limit'),
                                    ('max_indexed_length', 4, 'indexed_word_limit')]:
        result = subject.compile_residues(pair, limits=frozen.Limits(**{field: value}))
        assert result['reason'] == expected, (field, result['reason'])
        assert result['final_pair'][1] == pair[1]
        verify(pair, result, legacy)
        counts['resource_guards_preserve_donor'] += 1
    for call in [lambda: subject.compile_residues(['z', 'x']),
                 lambda: subject.compile_residues(pair, nearest=1),
                 lambda: subject.compile_residues(pair, allow_cyclic_cut=0),
                 lambda: subject.compile_residues(pair, source_index=False)]:
        try:
            call()
        except ValueError:
            counts['invalid_api'] += 1
        else:
            raise AssertionError('invalid API was accepted')
    return {'counts': dict(counts), 'total': sum(counts.values()), 'samples': samples}


def extend_saved(saved, legacy):
    records = []
    wall, cpu = time.perf_counter(), time.process_time()
    for row in saved['full_u124']['records']:
        remaining = 1000 - row['charges']
        attempts = []
        prior_best = min(row['attempts'], key=lambda a: a['best_length'])
        best_length, best_pair, best_moves = prior_best['best_length'], prior_best['best_pair'], prior_best['best_moves']
        for prior_index, prior in enumerate(row['attempts']):
            if prior['reason'] != 'criterion_failed':
                continue
            for side in ('lower', 'upper'):
                if remaining <= 0:
                    break
                result = subject.compile_residues(prior['final_pair'], stable=prior['stable'],
                    source_index=prior['source_index'], side=side,
                    limits=frozen.Limits(budget=remaining, max_word_length=512,
                                         max_indexed_length=256, max_moves=12000))
                remaining -= result['charges']
                verify(row['input'], result, legacy, prefix=prior['moves'])
                attempt = {'preceding_attempt': prior_index, 'side': side, 'residue': result}
                if result['best_length'] < best_length:
                    best_length, best_pair = result['best_length'], result['best_pair']
                    best_moves = prior['moves'] + result['best_moves']
                if (result['relation_uses_committed'] or result['preparations']) and remaining:
                    retry = frozen.compile_pair(result['final_pair'], stable=prior['stable'],
                        source_index=prior['source_index'], boundary_order=tuple(prior['boundary_order']),
                        limits=frozen.Limits(budget=remaining, max_word_length=512,
                                             max_indexed_length=256, max_moves=12000))
                    remaining -= retry['charges']
                    verify(row['input'], retry, legacy, prefix=prior['moves'] + result['moves'])
                    attempt['retry'] = retry
                    if retry['best_length'] < best_length:
                        best_length, best_pair = retry['best_length'], retry['best_pair']
                        best_moves = prior['moves'] + result['moves'] + retry['best_moves']
                attempts.append(attempt)
        assert frozen.replay(row['input'], best_moves) == best_pair
        total_charges = 1000 - remaining
        assert total_charges <= 1000
        records.append({'name': row['name'], 'input': row['input'], 'initial_length': row['input_length'],
                        'prior_charges': row['charges'], 'total_charges': total_charges,
                        'best_length': best_length, 'best_pair': best_pair, 'best_moves': best_moves,
                        'strict_length_improvement': best_length < row['input_length'],
                        'solved': any(a.get('retry', {}).get('status') == 'solved' for a in attempts),
                        'attempts': attempts})
    attempts = [a for row in records for a in row['attempts']]
    return {'rows': len(records), 'ids': [r['name'] for r in records], 'records': records,
            'strict_length_improved': [r['name'] for r in records if r['strict_length_improvement']],
            'solved': [r['name'] for r in records if r['solved']],
            'total_charges_including_saved_prefixes': sum(r['total_charges'] for r in records),
            'saved_prefix_charges': sum(r['prior_charges'] for r in records),
            'max_per_row_charges': max(r['total_charges'] for r in records),
            'residue_reasons': dict(Counter(a['residue']['reason'] for a in attempts)),
            'cyclic_donor_cuts': sum(len(a['residue']['preparations']) for a in attempts),
            'retry_count': sum('retry' in a for a in attempts),
            'retry_reasons': dict(Counter(a['retry']['reason'] for a in attempts if 'retry' in a)),
            'wall_seconds': time.perf_counter() - wall, 'cpu_seconds': time.process_time() - cpu}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-replay-source', type=Path)
    args = parser.parse_args()
    legacy, legacy_hash = legacy_replayer(args.legacy_replay_source) if args.legacy_replay_source else (None, None)
    saved_path = HERE / 'boundary_compiler_report.json'
    saved = json.loads(saved_path.read_text())
    assert saved['compiler_sha256'] == hashlib.sha256(Path(frozen.__file__).read_bytes()).hexdigest()
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    planted = planted_checks(legacy)
    screen = extend_saved(saved, legacy)
    report = {'status': 'pass', 'module_sha256': hashlib.sha256(Path(subject.__file__).read_bytes()).hexdigest(),
              'checks_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'frozen_compiler_sha256': saved['compiler_sha256'],
              'saved_prefix_report_sha256': hashlib.sha256(saved_path.read_bytes()).hexdigest(),
              'legacy_sha256': legacy_hash, 'planted': planted, 'saved_checkpoint_extension': screen,
              'wall_seconds': time.perf_counter() - start_wall, 'cpu_seconds': time.process_time() - start_cpu,
              'scope': 'Only saved failed literal-frame checkpoints; no heap/JIT, basis changes, stabilizations, new census sampling, or baseline reruns.'}
    (HERE / 'extreme_residues_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'planted_checks': planted['total'],
                      'gains': screen['strict_length_improved'], 'solves': screen['solved'],
                      'charges': screen['total_charges_including_saved_prefixes'],
                      'reasons': screen['residue_reasons'], 'wall_seconds': report['wall_seconds'],
                      'cpu_seconds': report['cpu_seconds']}))


if __name__ == '__main__':
    main()
