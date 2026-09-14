"""Early fixed-unit completion inside the frozen bounded Nielsen candidate policy."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import heapq
import importlib
import itertools
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import two_complement_probe as prototype
import two_complement_probe_checks as independent

COMPLETION_MODULE = 'two_complement_direct_completion'
FROZEN_COMPILER_SHA256 = 'f9ac216e709c886f6cd84d9eb441ba418d3eea7aeff2503c3a847a4545759603'
FROZEN_PROTOTYPE_SHA256 = '4ebb70fd05a098dbc43f3d308600ab40c3c453ad3ae2ad09f02b6be527e4cfbb'
FROZEN_CHECKER_SHA256 = '9045b8523f55886b61d0f76b701149fa16e2f77a60aed4c0c1a52c39c38002a1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def completion_module():
    return importlib.import_module(COMPLETION_MODULE)


def finish_if_possible(initial, state, budget, counters, location):
    images, basis, path = state
    compiler = completion_module()
    recognition = compiler.recognize_unit_lifts(images)
    counters['unit_goal_checks_' + location] += 1
    if recognition is None:
        return None
    counters['recognizable_unit_goals_' + location] += 1
    required = recognition['word_operations'] + 2
    if budget.limit - budget.used < required:
        counters['completion_budget_rejections'] += 1
        return None
    before_charge = budget.used
    if not budget.charge('unit_completion_word_images', recognition['word_operations']):
        raise AssertionError('reserved unit completion images missing')
    if not budget.charge('kernel_projection_word_images', 2):
        raise AssertionError('reserved kernel projection images missing')
    plan = compiler.plan_unit_completion(images)
    if plan['word_operations'] != recognition['word_operations']:
        raise ValueError('unit goal estimate differs from actual compiler operations')
    snapshot = prototype.verify_basis(initial, images, basis, path)
    completed = compiler.complete_snapshot(initial, snapshot, plan=plan)
    if completed['images'] != ['', '', 'x', 'y']:
        raise ValueError('unit compiler did not produce the exact terminal marking')
    completed.update(status='marked_kernel_basis_found', unit_goal_location=location,
                     unit_goal_image_tuple=list(images), unit_goal_recognition=recognition,
                     unit_completion_plan=plan, work_before_completion=before_charge,
                     reserved_completion_and_projection_units=required,
                     best_image_length=2)
    return completed


def nielsen(initial, budget, image_cap=128, domain_cap=2048):
    state = prototype.normalize(initial, tuple(prototype.DOMAIN), [], budget)
    if state is None:
        return {'status': 'image_budget_before_initial_normalization', 'best_image_length': sum(map(len, initial))}
    images, basis, path = state
    heap = [(sum(map(len, images)), images, 0, basis, path)]
    seen = {images}
    serial, popped, generated, best = 0, 0, 0, state
    guards, counters = Counter(), Counter()

    def statistics():
        return {'popped_states': popped, 'generated_candidates': generated,
                'seen_image_tuples': len(seen), 'guards': dict(guards), 'unit_gate_counts': dict(counters)}

    while heap:
        total, images, _, basis, path = heapq.heappop(heap)
        popped += 1
        if total < sum(map(len, best[0])):
            best = images, basis, path
        completed = finish_if_possible(initial, (images, basis, path), budget, counters, 'pop')
        if completed is not None:
            return {**completed, **statistics()}
        for i, j, sign, side in itertools.product(range(4), range(4), (1, -1), ('left', 'right')):
            if i == j or not images[j] or not images[i]:
                continue
            if budget.limit - budget.used < 2:
                return {'status': 'image_budget', **prototype.verify_basis(initial, *best),
                        **statistics(), 'best_image_length': sum(map(len, best[0]))}
            budget.charge('multiplication_candidate_images')
            move = {'op': 'multiply', 'target': i, 'donor': j, 'sign': sign, 'side': side}
            child_images = prototype.row_move(images, move)
            generated += 1
            if len(child_images[i]) > image_cap:
                guards['image_cap'] += 1
                continue
            child_basis = prototype.row_move(basis, move)
            if max(map(len, child_basis)) > domain_cap:
                guards['domain_basis_cap'] += 1
                continue
            child = prototype.normalize(child_images, child_basis, path + [move], budget, changed=i)
            if child is None:
                raise AssertionError('reserved normalization image missing')
            ci, cb, cp = child
            if sum(map(len, ci)) < sum(map(len, best[0])):
                best = child
            completed = finish_if_possible(initial, child, budget, counters, 'child')
            if completed is not None:
                return {**completed, **statistics()}
            if ci in seen:
                continue
            seen.add(ci)
            serial += 1
            heapq.heappush(heap, (sum(map(len, ci)), ci, serial, cb, cp))
    return {'status': 'finite_frontier_exhausted', **prototype.verify_basis(initial, *best),
            **statistics(), 'best_image_length': sum(map(len, best[0]))}


def project(search):
    projected = [prototype.red(''.join(c for c in w if c.lower() in 'tu')).translate(str.maketrans('tTuU', 'xXyY'))
                 for w in search['domain_basis'][:2]]
    return projected


def probe(pair, limit=1000, known_trivial=False):
    if len(pair) != 2 or any(set(w) - set('xXyY') or prototype.red(w) != w for w in pair):
        raise ValueError('two reduced old relators required')
    initial = [*pair, 'x', 'yy']
    budget = prototype.Budget(limit)
    folded = prototype.graph(initial, 'xy')
    result = {'input': list(pair), 'input_length': sum(map(len, pair)), 'complements': ['x', 'yy'],
              'initial_image_tuple': initial, 'full_fold_graph': folded,
              'join_is_full': folded == prototype.rose('xy'), 'image_limit': limit, 'projected': None}
    if not result['join_is_full']:
        result['status'] = 'join_not_full'
    else:
        search = nielsen(initial, budget)
        result['search'], result['status'] = search, search['status']
        if search['status'] == 'marked_kernel_basis_found':
            projected = project(search)
            determinant = prototype.determinant(projected)
            if abs(determinant) != 1:
                raise ValueError('projected kernel pair is not unimodular')
            result['projected'] = {'pair': projected, 'total_length': sum(map(len, projected)),
                'determinant': determinant, 'exact_pair_match': projected == list(pair),
                'cyclic_inverse_permutation_match': prototype.pair_key(projected) == prototype.pair_key(pair),
                'aut_comparison': 'not_searched', 'solve_implication_verified': False,
                'length_is_not_an_admissible_stable_minimum': not known_trivial}
            if known_trivial:
                result['stable_equivalence_witness'] = prototype.stable_equivalence_witness(pair, search)
                result['projected']['stable_equivalence_verified'] = True
    result['image_evaluations'], result['image_evaluation_counts'] = budget.used, dict(budget.counts)
    result['remaining_shared_budget'] = budget.limit - budget.used
    result['solved'] = False
    return result


def preflight():
    controls = []
    for pair, expected in ((['x', 'y'], 'marked_kernel_basis_found'),
                           (['xy', 'y'], 'marked_kernel_basis_found'),
                           (['xyx', 'xy'], 'marked_kernel_basis_found'),
                           (['xx', 'yy'], 'join_not_full')):
        record = probe(pair, known_trivial=expected != 'join_not_full')
        if record['status'] != expected:
            raise ValueError('planted unit-gate control failed')
        checked = independent.verify_record(record)
        controls.append({'input': pair, 'status': record['status'], 'units': record['image_evaluations'], 'independent_check': checked})
    tiny = []
    for limit in (0, 1, 2, 3, 4, 5, 7, 10, 11, 12, 13):
        record = probe(['x', 'y'], limit=limit)
        if record['image_evaluations'] > limit or record['remaining_shared_budget'] < 0:
            raise ValueError('tiny shared-budget overflow')
        if record['projected'] is not None:
            independent.verify_record(record)
        tiny.append({'limit': limit, 'used': record['image_evaluations'], 'status': record['status']})
    positive = probe(['xyx', 'xy'], known_trivial=True)
    corruptions = 0
    for field in ('domain_basis', 'inverse_domain_basis'):
        bad = deepcopy(positive); bad['search'][field][0] += 't'
        try:
            independent.verify_record(bad)
        except ValueError:
            corruptions += 1
        else:
            raise ValueError('corrupted marked basis accepted')
    return {'controls': controls, 'tiny_budgets': tiny, 'basis_corruptions_rejected': corruptions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel', action='store_true')
    args = parser.parse_args()
    if digest(HERE / 'two_complement_probe.py') != FROZEN_PROTOTYPE_SHA256:
        raise ValueError('frozen prototype changed')
    if digest(HERE / 'two_complement_probe_checks.py') != FROZEN_CHECKER_SHA256:
        raise ValueError('frozen independent checker changed')
    compiler = completion_module()
    compiler_path = Path(compiler.__file__)
    if digest(compiler_path) != FROZEN_COMPILER_SHA256:
        raise ValueError('verified direct compiler changed')
    started = time.process_time()
    checks = preflight()
    preflight_cpu = time.process_time() - started
    if not args.panel:
        print(json.dumps({'status': 'preflight_pass', 'checks': checks, 'cpu_seconds': preflight_cpu}, indent=2))
        return
    output = HERE / 'two_complement_unit_gate_report.json'
    if output.exists():
        raise ValueError('panel artifact already exists; do not rerun the exact20 screen')
    frozen = json.loads((HERE / 'two_complement_probe_report.json').read_text())
    inventory_path = prototype.ROOT.parent / 'u124_inventory.json'
    if digest(inventory_path) != frozen['source_inventory_sha256']:
        raise ValueError('fixed panel inventory hash changed')
    panel = json.loads(inventory_path.read_text())['panel']['rows']
    if [r['name'] for r in panel] != frozen['panel_ids'] or len(panel) != 20:
        raise ValueError('exact20 panel order changed')
    rows, cooling, algorithm_cpu, replay_cpu = [], 0.0, 0.0, 0.0
    wall = time.perf_counter()
    for original in panel:
        cpu = time.process_time()
        record = probe([original['r1'], original['r2']], known_trivial=True)
        record['search_cpu_seconds'] = time.process_time() - cpu
        algorithm_cpu += record['search_cpu_seconds']
        record['name'] = original['name']
        cpu = time.process_time()
        record['independent_check'] = independent.verify_record(record)
        replay_cpu += time.process_time() - cpu
        if record['image_evaluations'] > 1000:
            raise ValueError('shared per-input budget overflow')
        rows.append(record)
        pause = time.perf_counter(); time.sleep(.05); cooling += time.perf_counter() - pause
    report = {'status': 'exact20_unit_gate_screen_independently_replayed', 'rows': rows,
        'panel_ids': [r['name'] for r in rows], 'source_inventory_sha256': digest(inventory_path),
        'source_hashes': {name: digest(HERE / name) for name in ('two_complement_probe.py', 'two_complement_probe_checks.py', compiler_path.name, 'two_complement_probe_report.json')},
        'script_sha256': digest(Path(__file__)), 'preflight': checks,
        'counts': dict(Counter(r['status'] for r in rows)),
        'projected_pair_ids': [r['name'] for r in rows if r['projected']],
        'total_image_evaluations': sum(r['image_evaluations'] for r in rows),
        'maximum_image_evaluations': max(r['image_evaluations'] for r in rows),
        'remaining_budget_by_projected_input': {r['name']: r['remaining_shared_budget'] for r in rows if r['projected']},
        'new_solve_ids': [], 'certified_length_gain_ids': [], 'preflight_cpu_seconds': preflight_cpu,
        'search_cpu_seconds': algorithm_cpu, 'independent_replay_cpu_seconds': replay_cpu,
        'wall_seconds_including_cooling': time.perf_counter() - wall, 'cooldown_seconds': cooling,
        'candidate_policy': 'Same fixed complements x,y^2, join fold, normalized image tuple heap, signed left/right row products, deduplication, image128/domain2048 guards and candidate ordering as frozen prototype. Only added pop/generated-child goal checks and deterministic unit completion; no projected Aut search or S20 in this screen.',
        'budget': 'One unit per candidate multiplication image and inverse-normalization comparison; initial normalization4. Goal inspection scans and validates existing reduced words and constructs no candidate row image. Before compiling, reserve the exact non-permutation image-update count including sign fixes, lift prefix/suffix removal and every letter cleared from the two remaining images, plus2 kernel projections. Domain witness operations and inverse verification are bookkeeping outside candidate-image units, as in the frozen prototype. All remaining units are available for a separately captured rootS20 continuation; heterogeneous units are not equal-CPU units.',
        'scope': 'The exact marked basis and inverse give theorem-backed stable equivalence on these known-trivial inputs. No ordinary-equivalence or solve claim. All basis and projected pairs pass the existing independent integer replayer. The old prototype is preserved unchanged; this new screen stops earlier by a different sufficient goal gate.'}
    output.write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Two-complement early unit gate', '',
        f"Exact20 panel: {len(report['projected_pair_ids'])} independently replayed projected pairs; no solves claimed. Search CPU {algorithm_cpu:.6f}s; independent certificate replay {replay_cpu:.6f}s; cooling {cooling:.6f}s.", '',
        report['candidate_policy'], '', report['budget'], '', report['scope'], '',
        '| input | status | charged units | remaining units | projected length | exact projected pair |',
        '|---|---|---:|---:|---:|---|']
    for r in rows:
        projected = r['projected']
        words = ', '.join('`' + w + '`' for w in projected['pair']) if projected else '—'
        lines.append(f"| {r['name']} | {r['status']} | {r['image_evaluations']} | {r['remaining_shared_budget']} | {projected['total_length'] if projected else '—'} | {words} |")
    (HERE / 'two_complement_unit_gate_report.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('rows', 'preflight')}, indent=2))


if __name__ == '__main__':
    main()
