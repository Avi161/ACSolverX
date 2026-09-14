"""Independent exchange/breakpoint checks and a shared-budget exact124 screen."""
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
from check_ac_words import independent_replay, inverse, legacy_replayer, reduce_word
import coupled_exchange as subject

HERE = Path(__file__).resolve().parent


def i_inverse(word):
    return tuple((i, -e) for i, e in reversed(word))


def i_reduce(word):
    word = list(word)
    while True:
        for pos in range(len(word) - 1):
            if word[pos] == (word[pos + 1][0], -word[pos + 1][1]):
                del word[pos:pos + 2]
                break
        else:
            return tuple(word)


def i_shift(word, amount):
    return tuple((i + amount, e) for i, e in word)


def i_span(word):
    return max(i for i, _ in word) - min(i for i, _ in word) if word else 0


def predicted_indexed(f, g, sign, q, k):
    dg = i_shift(g if sign == 1 else i_inverse(g), q)
    h = i_reduce(i_inverse(dg) + f)
    b = i_reduce(f + i_shift(i_inverse(h), -k))
    return h, b


def verify(pair, result, legacy, prefix=()):
    for key, endpoint in [('moves', 'final_pair'), ('best_moves', 'best_pair')]:
        moves = list(prefix) + result[key]
        assert frozen.replay(pair, moves) == result[endpoint]
        assert independent_replay(pair, moves) == result[endpoint]
        if legacy:
            assert legacy(pair, moves) == result[endpoint]
    for candidate in result.get('candidates', ()):
        if candidate['reason'] != 'evaluated':
            continue
        global_prefix = list(prefix) + result['moves'][:candidate['prefix_move_count']]
        assert independent_replay(pair, global_prefix) == candidate['input']
        moves = global_prefix + candidate['moves']
        assert independent_replay(pair, moves) == candidate['after']
        assert frozen.replay(pair, moves) == candidate['after']
        def core_length(word):
            while len(word) > 1 and inverse(word[0]) == word[-1]:
                word = word[1:-1]
            return len(word)
        current = list(candidate['input'])
        raw_minimum = sum(map(len, current))
        cyclic_minimum = sum(core_length(w) for w in current)
        for move in candidate['moves']:
            current = independent_replay(current, [move])
            raw_minimum = min(raw_minimum, sum(map(len, current)))
            cyclic_minimum = min(cyclic_minimum, sum(core_length(w) for w in current))
        assert raw_minimum == candidate['minimum_raw_length']
        assert cyclic_minimum == candidate['minimum_cyclic_length']
        if legacy:
            assert legacy(pair, moves) == candidate['after']
    assert result['charges'] <= result['limits']['budget'] <= 1000
    return True


def breakpoint_check():
    words = [((i, a), (j, b)) for i, j in itertools.product((-1, 0, 1), repeat=2) if i != j
             for a, b in itertools.product((-1, 1), repeat=2)]
    counts = Counter()
    for f, g in itertools.product(words, repeat=2):
        phi = i_span(f) + i_span(g)
        wide = {False: False, True: False}
        for sign, q, k in itertools.product((-1, 1), range(-3, 4), range(-5, 6)):
            h, b = predicted_indexed(f, g, sign, q, k)
            if i_span(h) + i_span(b) < phi:
                wide[False] = True
                if k:
                    wide[True] = True
            counts['wide_algebraic_candidates'] += 1
        for coupled_only in (False, True):
            candidates = subject.breakpoint_candidates(f, g, coupled_only)
            assert len(candidates) <= 12
            finite = False
            for c in candidates:
                h, b = predicted_indexed(f, g, c['donor_sign'], c['q'], c['k'])
                finite |= i_span(h) + i_span(b) < phi
                counts['breakpoint_algebraic_candidates'] += 1
            assert finite == wide[coupled_only], (f, g, coupled_only, finite, wide)
            counts['finite_wide_existence_agreement'] += 1
    return dict(counts)


def planted_checks(legacy):
    counts = Counter()
    samples = []
    f = ((-1, 1), (2, -1), (0, 1), (1, 1))
    g = ((1, -1), (0, 1), (2, 1))
    for stable, role, rsign, ssign, donor_sign, q, k in itertools.product(
            'xy', (0, 1), (-1, 1), (-1, 1), (-1, 1), (-2, 0, 3), (-2, 0, 1)):
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_exchange(pair, stable=stable, source_index=role,
                                          donor_sign=donor_sign, q=q, k=k)
        assert result['reason'] == 'specified_exchange_complete'
        source = pair[role] if rsign == 1 else inverse(pair[role])
        donor = pair[1 - role] if donor_sign == 1 else inverse(pair[1 - role])
        def pw(n):
            return stable * n if n >= 0 else inverse(stable) * -n
        donor = reduce_word(pw(q) + donor + pw(-q))
        a = reduce_word(inverse(donor) + source)
        b = reduce_word(source + pw(-k) + inverse(a) + pw(k))
        expected = [a, b] if role == 0 else [b, a]
        assert result['final_pair'] == expected
        assert result['elementary_moves'] == 7 + 2 * abs(k) + abs(q) + (donor_sign == -1) + (rsign == -1)
        assert result['candidate_ac2_moves'] == 3
        verify(pair, result, legacy)
        counts['general_exchange_sign_role_axis_shift_identity'] += 1

    for m, stable, role, rsign, ssign in itertools.product((2, 3, 5), 'xy', (0, 1), (-1, 1), (-1, 1)):
        h = ((0, 1), (1, 1), (0, -1), (1, -1))
        g = ((0, 1), (0, 1), (m, -1))
        f = g + h
        pair = make_pair(f, g, stable, role, rsign, ssign)
        result = subject.compile_exchange(pair, stable=stable, source_index=role,
                                          donor_sign=ssign, q=0, k=-1)
        assert result['candidates'][0]['before_phi'] == 2 * m
        assert result['candidates'][0]['after_phi'] == m + 1
        assert result['candidates'][0]['donor_changed_after_preorientation']
        verify(pair, result, legacy)
        selected = subject.compile_coupled(pair, stable=stable, source_index=role, max_exchanges=1000)
        assert selected['exchanges']
        assert all(e['strict_phi_descent'] for e in selected['exchanges'])
        assert len(selected['exchanges']) <= selected['initial_potential']
        verify(pair, selected, legacy)
        counts['arbitrary_width_nonterminal_descent_family'] += 1
        if len(samples) < 3:
            samples.append({'m': m, 'stable': stable, 'role': role, 'result': selected})

    for stable, role in itertools.product('xy', (0, 1)):
        g = ((0, 1), (2, -1), (1, 1))
        pair = make_pair(g, g, stable, role, 1, 1)
        result = subject.compile_coupled(pair, stable=stable, source_index=role)
        assert result['reason'] == 'terminal_checkpoint'
        assert result['exchanges'][-1]['empty_stable_fibre_after']
        assert not result['exchanges'][-1]['donor_changed_after_preorientation']
        verify(pair, result, legacy)
        counts['empty_h_terminal_not_called_donor_change'] += 1

    pair = make_pair(((0, 1), (2, -1)), ((1, 1), (0, 1)), 'x', 0, 1, 1)
    for budget in range(20):
        result = subject.compile_exchange(pair, q=1, k=-1, limits=frozen.Limits(budget=budget))
        verify(pair, result, legacy)
        counts['transactional_small_budget_prefix'] += 1
    for kwargs, reason in [({'max_moves': 5}, 'certificate_limit'),
                            ({'max_word_length': 5}, 'word_limit'),
                            ({'max_indexed_length': 1}, 'indexed_word_limit')]:
        result = subject.compile_exchange(pair, q=2, k=3, limits=frozen.Limits(**kwargs))
        assert result['reason'] == reason
        verify(pair, result, legacy)
        counts['explicit_resource_guards'] += 1
    h = ((0, 1), (1, 1), (0, -1), (1, -1))
    g = ((0, 1), (0, 1), (3, -1))
    pair = make_pair(g + h, g, 'x', 0, 1, 1)
    result = subject.compile_coupled(pair, limits=frozen.Limits(max_moves=3))
    assert result['reason'] == 'coupled_candidate_resource_limit'
    assert result['failed_checkpoint']['resource_rejections'] > 0
    verify(pair, result, legacy)
    counts['bounded_candidate_rejection_is_not_theorem_failure'] += 1
    result = subject.compile_exchange(['x', ''], k=10**100)
    assert result['reason'] == 'certificate_limit'
    verify(['x', ''], result, legacy)
    counts['huge_shift_rejected_before_word_allocation'] += 1
    for call in [lambda: subject.compile_coupled(['z', 'y']),
                 lambda: subject.compile_exchange(pair, donor_sign=True),
                 lambda: subject.compile_exchange(pair, q=1.0),
                 lambda: subject.compile_coupled(pair, max_exchanges=0),
                 lambda: subject.compile_coupled(pair, require_donor_change=1)]:
        try:
            call()
        except ValueError:
            counts['invalid_api'] += 1
        else:
            raise AssertionError('invalid API accepted')
    return {'counts': dict(counts), 'total': sum(counts.values()), 'samples': samples}


def normalized_key(pair, stable, role):
    sign = frozen.exponent(pair[role], stable)
    if abs(sign) != 1 or frozen.exponent(pair[1 - role], stable):
        return None
    normalized = list(pair)
    if sign == -1:
        normalized[role] = inverse(normalized[role])
    return stable, role, tuple(normalized)


def screen(saved, legacy):
    records = []
    wall, cpu = time.perf_counter(), time.process_time()
    for row in saved['full_u124']['records']:
        remaining = 1000 - row['charges']
        prior_best = min(row['attempts'], key=lambda a: a['best_length'])
        best_length, best_pair, best_moves = prior_best['best_length'], prior_best['best_pair'], prior_best['best_moves']
        frames = [('literal', None, row['input'], t, j, []) for t, j in itertools.product('xy', (0, 1))]
        frames += [('saved_checkpoint', i, prior['final_pair'], prior['stable'], prior['source_index'], prior['moves'])
                   for i, prior in enumerate(row['attempts']) if prior['reason'] == 'criterion_failed']
        seen = set()
        attempts = []
        skipped_duplicates = 0
        for origin, index, pair, stable, role, prefix in frames:
            key = normalized_key(pair, stable, role)
            if key is not None and key in seen:
                skipped_duplicates += 1
                continue
            if key is not None:
                seen.add(key)
            if remaining <= 0:
                break
            result = subject.compile_coupled(pair, stable=stable, source_index=role,
                require_donor_change=True, max_exchanges=1,
                limits=frozen.Limits(budget=remaining, max_word_length=512,
                                     max_indexed_length=256, max_moves=12000))
            remaining -= result['charges']
            verify(row['input'], result, legacy, prefix=prefix)
            attempt = {'origin': origin, 'preceding_attempt': index, 'result': result}
            if result['best_length'] < best_length:
                best_length, best_pair = result['best_length'], result['best_pair']
                best_moves = prefix + result['best_moves']
            if result['exchanges'] and remaining:
                retry = frozen.compile_pair(result['final_pair'], stable=stable, source_index=role,
                    limits=frozen.Limits(budget=remaining, max_word_length=512,
                                         max_indexed_length=256, max_moves=12000))
                remaining -= retry['charges']
                verify(row['input'], retry, legacy, prefix=prefix + result['moves'])
                attempt['retry'] = retry
                if retry['best_length'] < best_length:
                    best_length, best_pair = retry['best_length'], retry['best_pair']
                    best_moves = prefix + result['moves'] + retry['best_moves']
            attempts.append(attempt)
        assert independent_replay(row['input'], best_moves) == best_pair
        assert 0 <= remaining <= 1000
        records.append({'name': row['name'], 'input': row['input'], 'input_length': row['input_length'],
                        'prior_charges': row['charges'], 'total_charges': 1000 - remaining,
                        'best_length': best_length, 'best_pair': best_pair, 'best_moves': best_moves,
                        'strict_length_improvement': best_length < row['input_length'],
                        'solved': any(a.get('retry', {}).get('status') == 'solved' for a in attempts),
                        'skipped_duplicate_frames': skipped_duplicates, 'attempts': attempts})
    attempts = [a for r in records for a in r['attempts']]
    return {'rows': len(records), 'records': records,
            'strict_length_improved': [r['name'] for r in records if r['strict_length_improvement']],
            'solved': [r['name'] for r in records if r['solved']],
            'prior_charges': sum(r['prior_charges'] for r in records),
            'total_charges': sum(r['total_charges'] for r in records),
            'max_per_row_charges': max(r['total_charges'] for r in records),
            'candidate_count': sum(len(a['result']['candidates']) for a in attempts),
            'accepted_exchanges': sum(len(a['result']['exchanges']) for a in attempts),
            'accepted_rows': [r['name'] for r in records if any(a['result']['exchanges'] for a in r['attempts'])],
            'attempt_origins': dict(Counter(a['origin'] for a in attempts)),
            'reasons': dict(Counter(a['result']['reason'] for a in attempts)),
            'retry_count': sum('retry' in a for a in attempts),
            'retry_reasons': dict(Counter(a['retry']['reason'] for a in attempts if 'retry' in a)),
            'skipped_duplicate_frames': sum(r['skipped_duplicate_frames'] for r in records),
            'wall_seconds': time.perf_counter() - wall, 'cpu_seconds': time.process_time() - cpu}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-replay-source', type=Path)
    args = parser.parse_args()
    legacy, legacy_hash = legacy_replayer(args.legacy_replay_source) if args.legacy_replay_source else (None, None)
    saved_path = HERE / 'boundary_compiler_report.json'
    saved = json.loads(saved_path.read_text())
    assert hashlib.sha256(Path(frozen.__file__).read_bytes()).hexdigest() == saved['compiler_sha256']
    wall, cpu = time.perf_counter(), time.process_time()
    breakpoints = breakpoint_check()
    planted = planted_checks(legacy)
    result = screen(saved, legacy)
    report = {'status': 'pass', 'module_sha256': hashlib.sha256(Path(subject.__file__).read_bytes()).hexdigest(),
              'checks_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'frozen_compiler_sha256': saved['compiler_sha256'],
              'saved_prefix_report_sha256': hashlib.sha256(saved_path.read_bytes()).hexdigest(),
              'legacy_sha256': legacy_hash, 'breakpoint_checks': breakpoints, 'planted': planted,
              'screen': result, 'wall_seconds': time.perf_counter() - wall,
              'cpu_seconds': time.process_time() - cpu,
              'scope': 'Literal frames and distinct saved normalized failed checkpoints; no heap/JIT, ambient Nielsen steps, stabilizations, or prepared-frame census rerun.'}
    (HERE / 'coupled_exchange_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'planted_checks': planted['total'],
                      'breakpoint_agreements': breakpoints['finite_wide_existence_agreement'],
                      'gains': result['strict_length_improved'], 'solves': result['solved'],
                      'accepted': result['accepted_exchanges'], 'charges': result['total_charges'],
                      'wall_seconds': report['wall_seconds'], 'cpu_seconds': report['cpu_seconds']}))


if __name__ == '__main__':
    main()
