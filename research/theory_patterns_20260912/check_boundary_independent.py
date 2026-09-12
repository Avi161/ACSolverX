"""Independent boundary audit: exact replay, algebra, caps, and frozen full124."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import ac_words
import boundary_compiler as bc

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def inverse(w):
    return w[::-1].swapcase()


def concatenate(u, v):
    n = 0
    while n < min(len(u), len(v)) and u[-1 - n] == v[n].swapcase():
        n += 1
    return u[:len(u) - n] + v[n:]


def normal(w):
    if len(w) < 2:
        return w
    mid = len(w) // 2
    return concatenate(normal(w[:mid]), normal(w[mid:]))


def replay_states(pair, moves):
    state = [normal(w) for w in pair]
    states = [state.copy()]
    for move in moves:
        assert type(move['target']) is int and move['target'] in (1, 2)
        j = move['target'] - 1
        if move['op'] == 'invert':
            state[j] = inverse(state[j])
        elif move['op'] == 'multiply':
            assert type(move['source']) is int and move['source'] == 2 - j
            state[j] = concatenate(state[j], state[1 - j])
        else:
            assert move['op'] == 'conjugate' and move['by'] in 'xXyY' and len(move['by']) == 1
            a = move['by']
            state[j] = concatenate(concatenate(inverse(a), state[j]), a)
        states.append(state.copy())
    return states


def audit_result(result):
    states = replay_states(result['input'], result['moves'])
    best_states = replay_states(result['input'], result['best_moves'])
    assert states[-1] == result['final_pair'] == ac_words.replay(result['input'], result['moves'])
    assert best_states[-1] == result['best_pair'] == ac_words.replay(result['input'], result['best_moves'])
    assert result['elementary_moves'] == len(result['moves'])
    assert result['relation_uses_committed'] == sum(m['op'] == 'multiply' for m in result['moves'])
    assert result['charges'] == sum(result['charge_kinds'].values()) <= result['limits']['budget']
    assert max(len(result['moves']), len(result['best_moves'])) <= result['limits']['max_moves']
    assert result['best_length'] == sum(map(len, result['best_pair']))
    assert result['strict_length_improvement'] == (result['best_length'] < sum(map(len, result['input'])))
    assert result['peak_committed_relator_length'] == max(len(w) for s in states for w in s)
    if max(map(len, states[0])) <= result['limits']['max_word_length']:
        assert max(len(w) for s in states + best_states for w in s) <= result['limits']['max_word_length']
    if result['status'] == 'solved':
        assert result['reason'] == 'solved' and states[-1] == ['x', 'y']
    for ledger in result['ledgers']:
        size = sum(1 + 2 * len(f['conjugator']) + 2 * (f['sign'] == -1) for f in ledger['factors'])
        end, j = ledger['move_end'], ledger['target']
        start = end - size
        assert start >= 0 and states[start][1 - j] == states[end][1 - j]
        word, donor = states[start][j], states[start][1 - j]
        for f in ledger['factors']:
            assert f['sign'] in (-1, 1) and normal(f['conjugator']) == f['conjugator']
            c = f['conjugator']
            factor = normal(inverse(c) + (donor if f['sign'] == 1 else inverse(donor)) + c)
            word = concatenate(word, factor)
        assert word == ledger['after'] == states[end][j]
        if 'before_boundary_letters' in ledger:
            assert ledger['after_boundary_letters'] < ledger['before_boundary_letters']
    assert all(p['empty_after'] or p['after_span'] < p['before_span'] for p in result['passes'])
    return states


def power(c, n):
    return (c if n >= 0 else inverse(c)) * abs(n)


def expanded(indexed, stable):
    z = 'y' if stable == 'x' else 'x'
    return normal(''.join(power(stable, i) + power(z, s) + power(stable, -i) for i, s in indexed))


def pair_for(f, g, stable, role, rs=1, ss=1):
    r, s = normal(expanded(f, stable) + stable), expanded(g, stable)
    r, s = r if rs == 1 else inverse(r), s if ss == 1 else inverse(s)
    return [r, s] if role == 0 else [s, r]


def fresh_checks():
    counts, reasons = Counter(), Counter()
    # Every legal q in both strictly negative and strictly positive intervals.
    for off, side, t, role, rs, ss in itertools.product((-5, 5), ('lower', 'upper'), 'xy', (0, 1), (-1, 1), (-1, 1)):
        f = ((off, 1), (off + 1, 1), (off, -1), (off + 1, -1))
        g = ((0, 1), (5, -1), (0, -1), (5, 1), (2, 1))
        pair = pair_for(f, g, t, role, rs, ss)
        low, high = 1 - off, 4 - off
        for q in range(low, high + 1):
            result = bc.compile_boundary_pass(pair, stable=t, source_index=role, side=side, q=q)
            audit_result(result)
            assert result['reason'] == 'boundary_pass_complete' and result['final_pair'][role] == pair[role]
            ends = bc.support(bc.collect(result['final_pair'][1 - role], t)[0])
            assert ends is None or (ends[0] >= (1 if side == 'lower' else 0) and ends[1] <= (5 if side == 'lower' else 4))
            counts['all_legal_q_signed_axes_roles'] += 1
        for q in (low - 1, high + 1, low + 0.5):
            try:
                bc.compile_boundary_pass(pair, stable=t, source_index=role, side=side, q=q)
            except ValueError:
                counts['out_of_interval_or_noninteger_q_rejected'] += 1
            else:
                raise AssertionError('invalid q accepted')

    # New moduli, translated indices, both signs, both literal axes and roles.
    for m, side, eta, t, role, rs, ss in itertools.product((4, 7), ('lower', 'upper'), (-1, 1), 'xy', (0, 1), (-1, 1), (-1, 1)):
        f = ((-2, eta),) * m + ((0, 1),) * (m + 1)
        g = ((-2, 1),) * m + ((-1, -1),) * (m + 1)
        if side == 'upper':
            f, g = tuple((-i, s) for i, s in f), tuple((-i, s) for i, s in g)
        pair = pair_for(f, g, t, role, rs, ss)
        result = bc.compile_pair(pair, stable=t, source_index=role, boundary_order=(side, 'upper' if side == 'lower' else 'lower'))
        audit_result(result)
        assert result['status'] == 'solved'
        assert len(result['passes']) <= result['initial_potential']
        assert any(p.get('m', 0) > 1 for p in result['passes'])
        counts['translated_nonmonic_alternating_solutions'] += 1

    # A conjugated pure-power donor makes B empty. Its middle-run replacement
    # cancels a whole interior bridge and merges opposite residual extreme runs.
    for m, t, eta, e in itertools.product((2, 3, 7), 'xy', (-1, 1), (-1, 1)):
        z = 'y' if t == 'x' else 'x'
        A = expanded(((2, 1),) * m, t)
        C, E = z, inverse(z)
        D = normal(C + A + E)
        B = normal(inverse(C) + inverse(E))
        assert not B
        U = normal(power(A, 2) + z)
        V = normal(inverse(z) + power(A, -3))
        old = normal(U + (A if eta == 1 else inverse(A)) + V + t)
        new = normal(U + (B if eta == 1 else inverse(B)) + V + t)
        donor = D if e == 1 else inverse(D)
        c = normal((inverse(E) if eta == 1 else C) + V + t)
        factor = normal(inverse(c) + (donor if e * -eta == 1 else inverse(donor)) + c)
        assert normal(old + factor) == new
        remaining, height = bc.collect(new, t)
        assert height == 1 and all(exp % m == 0 for _, _, exp in bc.runs(remaining, 2))
        counts['cancellation_merged_runs_signed_identity'] += 1

    for m, side, eta, t, role, rs, ss in itertools.product((2, 5), ('lower', 'upper'), (-1, 1), 'xy', (0, 1), (-1, 1), (-1, 1)):
        g = ((-1, 1), (0, -1)) + ((1, 1),) * m + ((0, 1), (-1, 1))
        f = ((-1, 1),) + ((3, eta),) * (2 * m) + ((2, -1),) + ((3, -eta),) * m + ((0, 1),)
        if side == 'lower':
            f, g = tuple((-i, s) for i, s in f), tuple((-i, s) for i, s in g)
        pair = pair_for(f, g, t, role, rs, ss)
        compiler = bc._Compiler(pair, t, role, (side,), bc.Limits())
        compiler.normalize(require_unimodular=False)
        current_f, current_g = compiler.frame()
        candidate, failure = compiler.power_candidate(side, current_f, current_g)
        assert failure is None and candidate['q'] == (-2 if side == 'lower' else 2)
        assert candidate['C'] and candidate['E'] and candidate['B']
        compiler.power_pass(candidate)
        result = compiler.result('audited_power_pass')
        audit_result(result)
        assert result['final_pair'][1 - role] == pair[1 - role]
        assert result['passes'][0]['after_span'] < result['passes'][0]['before_span']
        counts['general_C_E_power_compiler_signed_cases'] += 1

    for m, side, t, role, rs, ss in itertools.product((2, 5), ('lower', 'upper'), 'xy', (0, 1), (-1, 1), (-1, 1)):
        g = ((0, 1),) * m + ((1, -1),) * (m + 1)
        pair = pair_for(g, g, t, role, rs, ss)
        result = bc.compile_pair(pair, stable=t, source_index=role, boundary_order=(side,))
        audit_result(result)
        assert result['status'] == 'solved' and result['passes'][0]['empty_after']
        counts['power_pass_creates_empty_stable_fibre_terminal'] += 1
    for side, t, role, rs, ss in itertools.product(('lower', 'upper'), 'xy', (0, 1), (-1, 1), (-1, 1)):
        pair = pair_for(((0, 1),), ((0, 1), (1, -1)), t, role, rs, ss)
        result = bc.compile_boundary_pass(pair, stable=t, source_index=role, side=side)
        audit_result(result)
        assert result['reason'] == 'boundary_pass_complete' and result['final_pair'][1 - role] == ''
        assert result['final_pair'][role] == pair[role]
        counts['nonunimodular_transport_creates_empty_zero_fibre'] += 1

    # Sweep transaction boundaries using the full stream as a prefix oracle.
    f = ((0, 1), (1, 1), (0, -1), (1, 1))
    g = ((0, 1), (3, 1), (0, -1), (3, -1), (1, 1))
    for side, t, role in itertools.product(('lower', 'upper'), 'xy', (0, 1)):
        pair = pair_for(f, g, t, role, -1, -1)
        full = bc.compile_boundary_pass(pair, stable=t, source_index=role, side=side)
        states = audit_result(full)
        move_caps = sorted({max(0, n + delta) for n in [0, full['elementary_moves']] + [l['move_end'] for l in full['ledgers']] for delta in (-1, 0, 1)})
        caps = [('budget', n) for n in range(full['charges'] + 2)]
        caps += [('max_moves', n) for n in move_caps]
        caps += [('max_word_length', n) for n in sorted({max(map(len, s)) for s in states})]
        caps += [('max_indexed_length', n) for n in (0, 1, 4, 5, 10)]
        for field, n in caps:
            result = bc.compile_boundary_pass(pair, stable=t, source_index=role, side=side, limits=bc.Limits(**{field: n}))
            audit_result(result)
            assert result['final_pair'][role] == pair[role]
            assert result['moves'] == full['moves'][:len(result['moves'])]
            counts['negative_source_transaction_cap_sweeps'] += 1
            reasons[result['reason']] += 1

    for empty_f, index, t, role, rs, ss in itertools.product((False, True), (-4, 0, 3), 'xy', (0, 1), (-1, 1), (-1, 1)):
        f = () if empty_f else ((-3, 1), (2, -1), (0, 1))
        pair = pair_for(f, ((index, 1),), t, role, rs, ss)
        result = bc.compile_pair(pair, stable=t, source_index=role)
        audit_result(result)
        assert result['status'] == 'solved'
        counts['initial_terminal_fibres_all_signs_axes_roles'] += 1
    for budget in (0, 1, 2, 3):
        result = bc.compile_boundary_pass(['yxY', 'y'], limits=bc.Limits(budget=budget))
        audit_result(result)
        assert result['final_pair'][0] == 'yxY'
        assert result['charge_kinds'].get('best_prefix_cleanup', 0) == (1 if budget >= 2 else 0)
        assert result['best_pair'] == (['x', 'y'] if budget >= 2 else ['yxY', 'y'])
        counts['optional_best_cleanup_charged'] += 1
    for pair in (['x', ''], ['X', ''], ['', 'y'], ['x', 'yy']):
        result = bc.compile_pair(pair)
        audit_result(result)
        assert result['status'] != 'solved'
        counts['outside_unimodular_or_empty_frame_rejected'] += 1
    result = bc.compile_pair(['yxyxYXY', 'YxxYXXy'])
    audit_result(result)
    counts['arbitrary_outside_frame_certificate'] += 1
    return {'counts': dict(counts), 'total': sum(counts.values()), 'resource_outcomes': dict(reasons)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_checks(inventory_path):
    report_path = HERE / 'boundary_compiler_report.json'
    report = json.loads(report_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    assert report['compiler_sha256'] == sha(HERE / 'boundary_compiler.py')
    assert report['checks_sha256'] == sha(HERE / 'boundary_compiler_checks.py')
    assert report['inventory_sha256'] == sha(inventory_path)
    assert report['legacy_replay_sha256'] == sha(ROOT / 'research/supermoves_20260908/certificate_decoder.py')
    source = ROOT / inventory['sources']['best']['path']
    assert sha(source) == inventory['sources']['best']['sha256']
    rows = list(csv.DictReader(source.open()))
    exact = {r['name']: [r['r1'], r['r2']] for r in rows}
    full = report['full_u124']
    assert len(exact) == full['size'] == 124
    assert full['ids'] == [r['name'] for r in rows]
    assert set(exact) == {r['name'] for r in full['records']}
    counts, failures, stats = Counter(), Counter(), Counter()
    largest_moves = peak = largest_charge = 0
    for row in full['records']:
        assert row['input'] == exact[row['name']]
        assert len(row['attempts']) == 8
        orientations = [(a['stable'], a['source_index'], a['boundary_order'][0]) for a in row['attempts']]
        assert orientations == list(itertools.product('xy', (0, 1), ('lower', 'upper')))
        remaining = 1000
        for a in row['attempts']:
            assert a['input'] == row['input'] and a['limits']['budget'] == remaining
            audit_result(a)
            regenerated = bc.compile_pair(row['input'], stable=a['stable'], source_index=a['source_index'], boundary_order=a['boundary_order'], limits=bc.Limits(**a['limits']))
            assert regenerated == a
            remaining -= a['charges']
            counts[a['reason']] += 1
            stats['attempts'] += 1
            for p in a['passes']:
                stats[p['rule']] += 1
                if p['rule'] == 'extreme_power':
                    assert p['m'] == 1
            if a['failed_checkpoint']:
                failures.update(b['reason'] for b in a['failed_checkpoint']['boundaries'])
            largest_moves = max(largest_moves, a['elementary_moves'])
            peak = max(peak, a['peak_committed_relator_length'])
        assert row['charges'] == 1000 - remaining
        assert row['best_length'] == min(a['best_length'] for a in row['attempts'])
        assert not row['solved'] and not row['strict_length_improvement']
        stats['rows_with_passes'] += any(a['passes'] for a in row['attempts'])
        stats['charges'] += row['charges']
        largest_charge = max(largest_charge, row['charges'])
    assert stats == Counter(attempts=992, stable_boundary=149, extreme_power=48, rows_with_passes=62, charges=2929)
    assert counts == Counter(criterion_failed=230, frame_not_recognized=762)
    assert failures == Counter(extreme_not_one_literal_run=260, extreme_run_not_divisible=200)
    assert (largest_moves, peak, largest_charge) == (408, 141, 63)
    by_id = {r['name']: r for r in full['records']}
    assert len(report['panel']['records']) == 20
    assert all(r == by_id[r['name']] for r in report['panel']['records'])
    assert sum(r['charges'] for r in report['panel']['records']) == 394
    for sample in report['planted']['samples']:
        audit_result(sample['result'])
    return {'counts': dict(stats), 'outcomes': dict(counts), 'failed_boundary_conditions': dict(failures),
            'max_elementary_moves': largest_moves, 'max_committed_word_length': peak,
            'max_row_charges': largest_charge, 'solves': 0, 'strict_length_gains': 0,
            'stored_attempts_replayed_and_exactly_regenerated': 992,
            'source_best_sha256': sha(source), 'report_sha256': sha(report_path),
            'author_source_hashes_matched': True, 'panel_records_exactly_reused': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=ROOT.parent / 'u124_inventory.json')
    args = parser.parse_args()
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    fresh = fresh_checks()
    archive = archive_checks(args.inventory)
    report = {'status': 'pass', 'review': 'No correctness defect found in stated proofs or tested compiler paths.',
              'fresh': fresh, 'full_u124': archive,
              'hashes': {name: sha(HERE / name) for name in ('boundary_compiler.py', 'ac_words.py', 'astra_patterns.md', 'boundary_compiler_report.md', 'check_boundary_independent.py')},
              'wall_seconds': time.perf_counter() - start_wall, 'cpu_seconds': time.process_time() - start_cpu,
              'scope': 'Independent divide-and-conquer/free-boundary replay plus ac_words; tiny serial algebra only, no heap/JIT/baseline/frozen artifact writes.'}
    (HERE / 'boundary_independent_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
