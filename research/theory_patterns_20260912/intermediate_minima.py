"""Audit every elementary multiplication in saved ordinary AC certificates."""
from __future__ import annotations

import argparse
from collections import Counter, deque
import csv
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
import time

sys.dont_write_bytecode = True
from ac_words import Trace, cyclic, red, replay
from check_ac_words import independent_replay

HERE = Path(__file__).resolve().parent
ENCODE = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}
DECODE = {v: k for k, v in ENCODE.items()}


class CpuLimit(Exception):
    pass


def cyclic_length(word):
    length = len(word)
    if length < 2:
        return length
    front, back = iter(word), reversed(word)
    for _ in range(length // 2):
        if next(front) != -next(back):
            break
        length -= 2
    return length


class Replay:
    def __init__(self, pair):
        self.words = [deque(ENCODE[c] for c in red(word)) for word in pair]
        self.lengths = [cyclic_length(word) for word in self.words]

    def pair(self):
        return [''.join(DECODE[c] for c in word) for word in self.words]

    def apply(self, move):
        target = move['target']
        if type(target) is not int or target not in (1, 2):
            raise ValueError('invalid target')
        i, op = target - 1, move['op']
        word = self.words[i]
        if op == 'invert':
            self.words[i] = deque(-c for c in reversed(word))
        elif op == 'conjugate':
            letter = ENCODE[move['by']]
            if word and word[0] == letter:
                word.popleft()
            else:
                word.appendleft(-letter)
            if word and word[-1] == -letter:
                word.pop()
            else:
                word.append(letter)
        elif op == 'multiply':
            if type(move['source']) is not int or move['source'] != 3 - target:
                raise ValueError('invalid source')
            for letter in self.words[1 - i]:
                if word and word[-1] == -letter:
                    word.pop()
                else:
                    word.append(letter)
            self.lengths[i] = cyclic_length(word)
        else:
            raise ValueError('invalid elementary operation')
        return op


def checks():
    rng = random.Random(12092026)
    count = 0
    for pair in (['xy', 'Y'], ['xxyXY', 'YxY'], ['xyX', 'Yxxxy'], ['', 'xyX']):
        engine = Replay(pair)
        moves = []
        for _ in range(80):
            target = rng.randrange(2) + 1
            op = rng.choice(('invert', 'multiply', 'conjugate'))
            move = {'op': op, 'target': target}
            if op == 'multiply':
                move['source'] = 3 - target
            elif op == 'conjugate':
                move['by'] = rng.choice('xXyY')
            moves.append(move)
            engine.apply(move)
            expected = independent_replay(pair, moves)
            assert engine.pair() == expected
            assert engine.lengths == [len(cyclic(word)[0]) for word in expected]
            count += 1
    pair = ['xy', 'Y']
    engine = Replay(pair)
    first = {'op': 'multiply', 'target': 1, 'source': 2}
    engine.apply(first)
    assert sum(engine.lengths) == 2
    engine.apply(first)
    assert sum(engine.lengths) == 3
    return {'step_differential_checks': count, 'temporary_minimum_regression': True}


class Audit:
    def __init__(self, inventory, cpu_cap, cooldown):
        self.start_wall, self.start_cpu = time.perf_counter(), time.process_time()
        self.cpu_cap, self.cooldown = cpu_cap, cooldown
        self.rows = {row['name']: {'name': row['name'],
            'input': [row['r1'], row['r2']], 'archival_initial_length': row['initial_total_length'],
            'starting_best_length': row['total_length'], 'best_length': row['total_length'],
            'best_pair': [row['r1'], row['r2']], 'best_moves': [], 'best_location': None,
            'certificates_checked': 0, 'elementary_steps': 0, 'multiplications': 0,
            'prepared_frames_complete': False, 'boundary_compiler_complete': False,
            'critical_pairs_complete': None} for row in inventory['rows']}
        self.ops = Counter()
        self.sources = {}
        self.cooldown_observed = 0.0
        self.last_location = None

    def check_time(self):
        if time.process_time() - self.start_cpu >= self.cpu_cap:
            raise CpuLimit

    def cool(self):
        before = time.perf_counter()
        if self.cooldown:
            time.sleep(self.cooldown)
        self.cooldown_observed += time.perf_counter() - before if self.cooldown else 0.0

    def candidate(self, row, engine, prefix, moves, index, location):
        length = sum(engine.lengths)
        if length >= row['best_length']:
            return
        raw = engine.pair()
        cleanup = Trace(raw)
        cleanup.canonicalize(0)
        cleanup.canonicalize(1)
        certificate = prefix + moves[:index + 1] + cleanup.moves
        assert sum(map(len, cleanup.pair)) == length
        assert replay(row['input'], certificate) == cleanup.pair
        assert independent_replay(row['input'], certificate) == cleanup.pair
        row.update({'best_length': length, 'best_pair': cleanup.pair,
                    'best_moves': certificate, 'best_location': {**location,
                        'elementary_index': index, 'raw_pair_before_cleanup': raw,
                        'cleanup_moves': cleanup.moves}})

    def branch(self, row, pair, moves, expected, prefix, location):
        self.check_time()
        engine = Replay(pair)
        self.last_location = location
        for index, move in enumerate(moves):
            op = engine.apply(move)
            self.ops[op] += 1
            row['elementary_steps'] += 1
            if op == 'multiply':
                row['multiplications'] += 1
                self.candidate(row, engine, prefix, moves, index, location)
            if index % 1024 == 0:
                self.check_time()
        assert engine.pair() == expected, location
        row['certificates_checked'] += 1

    def prepared(self, path):
        digest = hashlib.sha256()
        count, complete = 0, False
        try:
            opener = gzip.open if path.suffix == '.gz' else open
            with opener(path, 'rb') as stream:
                for raw in stream:
                    self.check_time()
                    digest.update(raw)
                    record = json.loads(raw)
                    row = self.rows[record['name']]
                    assert row['input'] == record['input']
                    for ai, attempt in enumerate(record['attempts']):
                        prep = attempt['preparation']
                        location = {'source': path.name, 'name': row['name'], 'attempt': ai,
                                    'stage': 'preparation'}
                        self.branch(row, row['input'], prep['moves'], prep['final_pair'], [], location)
                        for ti, theorem in enumerate(attempt['theorem_calls']):
                            location = {'source': path.name, 'name': row['name'], 'attempt': ai,
                                        'stage': 'theorem', 'theorem_call': ti}
                            self.branch(row, prep['final_pair'], theorem['moves'], theorem['final_pair'],
                                        prep['moves'], location)
                    row['prepared_frames_complete'] = True
                    count += 1
                    self.cool()
            complete = True
        finally:
            logical_name = path.name.removesuffix('.gz')
            self.sources[logical_name] = {'rows_complete': count, 'complete': complete,
                'sha256': digest.hexdigest() if complete else None}

    def boundary(self, path):
        self.check_time()
        raw = path.read_bytes()
        data = json.loads(raw)
        records = data['full_u124']['records']
        assert len(records) == 124
        count = 0
        try:
            for record in records:
                row = self.rows[record['name']]
                assert record['input'] == row['input']
                for index, attempt in enumerate(record['attempts']):
                    self.branch(row, row['input'], attempt['moves'], attempt['final_pair'], [],
                                {'source': path.name, 'name': row['name'], 'attempt': index})
                row['boundary_compiler_complete'] = True
                count += 1
                self.cool()
        finally:
            self.sources[path.name] = {'rows_complete': count, 'complete': count == 124,
                                      'sha256': hashlib.sha256(raw).hexdigest()}

    def critical(self, path):
        self.check_time()
        raw = path.read_bytes()
        records = json.loads(raw)['records']
        count = 0
        try:
            for record in records:
                row = self.rows[record['name']]
                row['critical_pairs_complete'] = False
                assert record['input'] == row['input']
                for index, attempt in enumerate(record['cases']):
                    self.branch(row, row['input'], attempt['moves'], attempt['pair'], [],
                                {'source': path.name, 'name': row['name'], 'case': index})
                row['critical_pairs_complete'] = True
                count += 1
                self.cool()
        finally:
            self.sources[path.name] = {'rows_complete': count, 'complete': count == len(records),
                                      'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu-cap', type=float, default=60)
    parser.add_argument('--cooldown-seconds', type=float, default=0.2)
    args = parser.parse_args()
    if not 0 < args.cpu_cap <= 60 or not 0 <= args.cooldown_seconds <= 60:
        parser.error('CPU cap must be in(0,60], cooldown in[0,60]')
    planted = checks()
    inventory_path = HERE / 'u124_inventory.json'
    inventory = json.loads(inventory_path.read_text())
    audit = Audit(inventory, args.cpu_cap, args.cooldown_seconds)
    status = 'complete'
    try:
        audit.prepared(HERE / 'prepared_frames_full124.jsonl.gz')
        audit.boundary(HERE / 'boundary_compiler_report.json')
        audit.critical(HERE / 'critical_pairs_panel.json')
    except CpuLimit:
        status = 'cpu_limit_incomplete'
    rows = list(audit.rows.values())
    for row in rows:
        row['strict_length_improvement'] = row['best_length'] < row['starting_best_length']
        row['best_elementary_moves'] = len(row['best_moves'])
        row['solved_at_intermediate'] = (row['best_length'] == 2 and all(len(w) == 1 for w in row['best_pair'])
                                         and {w.lower() for w in row['best_pair']} == {'x', 'y'})
    report = {'status': status, 'checks': planted, 'cpu_cap_seconds': args.cpu_cap,
        'sources': audit.sources, 'last_location': audit.last_location,
        'operation_counts': dict(audit.ops), 'certificates_checked': sum(r['certificates_checked'] for r in rows),
        'strict_length_improved_ids': [r['name'] for r in rows if r['strict_length_improvement']],
        'solved_ids': [r['name'] for r in rows if r['solved_at_intermediate']],
        'sum_starting_best_length': sum(r['starting_best_length'] for r in rows),
        'sum_best_length': sum(r['best_length'] for r in rows), 'rows': rows,
        'wall_seconds': time.perf_counter() - audit.start_wall,
        'cpu_seconds': time.process_time() - audit.start_cpu,
        'cooldown_seconds': audit.cooldown_observed,
        'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'inventory_sha256': hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
        'method': 'Stream each prepared record; replay preparation once per attempt, then theorem moves from that prepared input. Ignore redundant raw/composed/best copies. Check cyclic total length after every multiply, since invert and conjugate preserve it. Confirm every final state exactly. Materialize only strict improvements, append explicit ordinary canonicalization and independently replay the complete prefix from the original pair. No search or new theorem call.'}
    destination = HERE / 'intermediate_minima.json'
    temporary = HERE / 'intermediate_minima.partial.json'
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(destination)
    fields = ('name', 'solved_at_intermediate', 'archival_initial_length', 'starting_best_length', 'best_length',
              'strict_length_improvement', 'certificates_checked', 'elementary_steps', 'multiplications',
              'prepared_frames_complete', 'boundary_compiler_complete', 'critical_pairs_complete', 'best_elementary_moves')
    with (HERE / 'intermediate_minima.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    md = ['# Intermediate certificate minima', '',
          f"Status: **{status}**. Found **{len(report['solved_ids'])} intermediate solves and {len(report['strict_length_improved_ids'])} strict length improvements**; aggregate saved-best length {report['sum_starting_best_length']}→{report['sum_best_length']}.", '',
          report['method'], '',
          'Temporary donor states are ordinary legal pairs and are included. Only cyclic total length is used for admission; no canonical rotations are computed unless a strict new minimum occurs. The ledger always includes all124 original saved-best inputs, with per-source completeness flags. An unchanged row that was not fully audited is not a negative conclusion.', '',
          f"Checked {report['certificates_checked']} certificates and {sum(audit.ops.values())} elementary steps, including {audit.ops['multiply']} multiplications. Runtime {report['wall_seconds']:.6f}s wall / {report['cpu_seconds']:.6f}s CPU, including {audit.cooldown_observed:.6f}s measured cooldown; CPU cap {args.cpu_cap}s. The320-step differential check and temporary-minimum regression passed.", '',
          '| source | rows complete | complete |', '|---|---:|---|']
    md.extend(f"| {name} | {entry['rows_complete']} | {entry['complete']} |" for name, entry in audit.sources.items())
    md += ['', 'All124 results: `intermediate_minima.csv`. Exact best words, gain certificates, source hashes and coverage: `intermediate_minima.json`.', '']
    (HERE / 'intermediate_minima.md').write_text('\n'.join(md))
    print(json.dumps({k: v for k, v in report.items() if k not in ('rows', 'method')}))


if __name__ == '__main__':
    main()
