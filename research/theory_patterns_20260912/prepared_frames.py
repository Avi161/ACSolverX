"""Finite ordinary-AC frame preparation for the alternating Magnus compiler.

The 16-frame portfolio uses x/y columns, literal/min-span cyclic cuts, right/left
signed products, and two deterministic choices for equal absolute column entries.
All framing and theorem attempts share one <=1000 algebraic work budget.
"""
from __future__ import annotations

from dataclasses import replace
from math import gcd
import time

try:
    from .ac_words import Trace, cyclic, exponent, inv, red, replay
    from .boundary_compiler import Limits, collect, compile_pair, span
except ImportError:
    from ac_words import Trace, cyclic, exponent, inv, red, replay
    from boundary_compiler import Limits, collect, compile_pair, span


class _Stop(Exception):
    pass


def _validate(pair):
    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
        raise ValueError('exactly two relators required')
    if any(not isinstance(w, str) or any(c not in 'xXyY' for c in w) for w in pair):
        raise ValueError('relators must be strings over xXyY')


def signed_product(trace, target, sign, side):
    """Replace target by target*donor^sign or donor^sign*target, restore donor."""
    if type(target) is not int or target not in (0, 1):
        raise ValueError('target must be integer 0 or 1')
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError('sign must be integer +/-1')
    if side not in ('left', 'right'):
        raise ValueError('side must be left or right')
    donor = 1 - target
    before = trace.pair[donor]
    if side == 'left':
        trace.invert(target)
        sign = -sign
    if sign == -1:
        trace.invert(donor)
    trace.multiply(target)
    if sign == -1:
        trace.invert(donor)
    if side == 'left':
        trace.invert(target)
    assert trace.pair[donor] == before


class _Prepare:
    def __init__(self, pair, stable, orientation, side, tie_target, limits):
        self.original = list(pair)
        self.trace = Trace(pair)
        self.stable, self.orientation = stable, orientation
        self.side, self.tie_target, self.limits = side, tie_target, limits
        self.charges, self.charge_kinds, self.steps, self.orientations = 0, {}, [], []
        self.best_pair, self.best_moves = list(self.trace.pair), []
        self.best_length = sum(map(len, self.best_pair))
        self.peak = max(map(len, self.trace.pair))
        self.source_index = None

    def charge(self, count, kind):
        if self.charges + count > self.limits.budget:
            raise _Stop('work_limit')
        self.charges += count
        self.charge_kinds[kind] = self.charge_kinds.get(kind, 0) + count

    def commit(self, staged, kind, count):
        self.charge(count, kind)
        peak = max(self.peak, *map(len, staged.pair))
        if peak > self.limits.max_word_length:
            raise _Stop('word_limit')
        if len(self.trace.moves) + len(staged.moves) > self.limits.max_moves:
            raise _Stop('certificate_limit')
        self.trace.pair = staged.pair
        self.trace.moves.extend(staged.moves)
        self.peak = peak
        length = sum(map(len, self.trace.pair))
        if length < self.best_length:
            self.best_pair, self.best_moves = list(self.trace.pair), list(self.trace.moves)
            self.best_length = length

    def cleanup(self, target):
        _, prefix = cyclic(self.trace.pair[target])
        if prefix:
            staged = Trace(self.trace.pair)
            staged.conjugate(target, prefix)
            self.commit(staged, 'cyclic_cleanup', 1)

    def orient(self, target):
        self.cleanup(target)
        if self.orientation == 'literal':
            self.orientations.append({'target': target, 'cut': 0, 'conjugator': ''})
            return
        word = self.trace.pair[target]
        winner = None
        for cut in range(max(1, len(word))):
            self.charge(1, 'orientation_candidate')
            candidate = word[cut:] + word[:cut]
            key = (span(collect(candidate, self.stable)[0]), candidate, cut)
            if winner is None or key < winner[0]:
                winner = key, cut
        cut = winner[1]
        prefix = word[:cut]
        if prefix:
            staged = Trace(self.trace.pair)
            staged.conjugate(target, prefix)
            self.commit(staged, 'orientation_conjugation', 1)
            assert staged.pair[target] == word[cut:] + word[:cut]
        self.orientations.append({'target': target, 'cut': cut, 'conjugator': prefix})

    def run(self):
        self.charge(1, 'column_recognition')
        if self.peak > self.limits.max_word_length:
            raise _Stop('word_limit')
        for target in (0, 1):
            self.orient(target)
        values = [exponent(w, self.stable) for w in self.trace.pair]
        initial_gcd = gcd(*values)
        while values[0] and values[1]:
            self.charge(1, 'euclidean_step_recognition')
            target = (self.tie_target if abs(values[0]) == abs(values[1])
                      else int(abs(values[1]) > abs(values[0])))
            before = list(values)
            sign = -1 if values[target] * values[1 - target] > 0 else 1
            staged = Trace(self.trace.pair)
            signed_product(staged, target, sign, self.side)
            self.commit(staged, 'row_elementary_operation', len(staged.moves))
            values = [exponent(w, self.stable) for w in self.trace.pair]
            assert sum(map(abs, values)) < sum(map(abs, before))
            assert gcd(*values) == initial_gcd
            self.steps.append({'target': target, 'sign': sign, 'side': self.side,
                               'before_column': before, 'after_column': values,
                               'move_end_before_cleanup': len(self.trace.moves)})
            self.cleanup(target)
        if initial_gcd != 1:
            raise _Stop('column_not_primitive')
        self.source_index = 0 if values[0] else 1
        assert abs(values[self.source_index]) == 1 and values[1 - self.source_index] == 0
        return 'frame_ready'

    def result(self, reason):
        assert replay(self.original, self.trace.moves) == self.trace.pair
        assert replay(self.original, self.best_moves) == self.best_pair
        return {'reason': reason, 'input': self.original, 'final_pair': list(self.trace.pair),
                'moves': self.trace.moves, 'elementary_moves': len(self.trace.moves),
                'best_pair': self.best_pair, 'best_moves': self.best_moves,
                'best_length': self.best_length, 'charges': self.charges,
                'charge_kinds': self.charge_kinds, 'steps': self.steps,
                'orientations': self.orientations, 'stable': self.stable,
                'source_index': self.source_index, 'orientation': self.orientation,
                'product_side': self.side, 'tie_target': self.tie_target,
                'final_column': [exponent(w, self.stable) for w in self.trace.pair],
                'final_spans': [span(collect(w, self.stable)[0]) for w in self.trace.pair],
                'peak_committed_relator_length': self.peak, 'verified': True,
                'limits': vars(self.limits)}


def prepare_frame(pair, *, stable='x', orientation='literal', side='right',
                  tie_target=0, limits=None):
    _validate(pair)
    if stable not in ('x', 'y') or orientation not in ('literal', 'min_span'):
        raise ValueError('invalid stable column or orientation policy')
    if side not in ('right', 'left') or type(tie_target) is not int or tie_target not in (0, 1):
        raise ValueError('invalid product side or tie target')
    limits = Limits() if limits is None else limits
    if not isinstance(limits, Limits):
        raise ValueError('limits must be a Limits instance')
    worker = _Prepare(pair, stable, orientation, side, tie_target, limits)
    try:
        reason = worker.run()
    except _Stop as stop:
        reason = str(stop)
    return worker.result(reason)


def compile_prepared(pair, *, limits=None, theorem_slice=128):
    """Try <=16 frames and two boundary orders; each branch starts at the input.

    Repeated literal prepared frames are recognized after charging preparation;
    their theorem calls are cached. Framing caps at 128 charges per attempt and
    each theorem call at theorem_slice, all debited from the shared budget.
    """
    _validate(pair)
    limits = Limits(budget=1000, max_word_length=512, max_indexed_length=256,
                    max_moves=12000) if limits is None else limits
    if not isinstance(limits, Limits):
        raise ValueError('limits must be a Limits instance')
    if type(theorem_slice) is not int or not 1 <= theorem_slice <= 1000:
        raise ValueError('theorem_slice must be an integer from 1 through 1000')
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    remaining, attempts, seen = limits.budget, [], set()
    best_pair, best_moves = [red(w) for w in pair], []
    best_length = sum(map(len, best_pair))
    best_origin, solved = None, False
    framing_charges, theorem_charges = 0, 0
    for orientation in ('literal', 'min_span'):
        for side, tie_target in (('right', 0), ('left', 0), ('right', 1), ('left', 1)):
            for stable in 'xy':
                if not remaining or solved:
                    continue
                prepared = prepare_frame(pair, stable=stable, orientation=orientation,
                    side=side, tie_target=tie_target,
                    limits=replace(limits, budget=min(remaining, 128)))
                remaining -= prepared['charges']
                framing_charges += prepared['charges']
                attempt = {'preparation': prepared, 'theorem_calls': []}
                attempts.append(attempt)
                if prepared['best_length'] < best_length:
                    best_pair, best_moves = prepared['best_pair'], prepared['best_moves']
                    best_length, best_origin = prepared['best_length'], [len(attempts) - 1, 'preparation']
                if prepared['reason'] != 'frame_ready':
                    continue
                key = (tuple(prepared['final_pair']), stable, prepared['source_index'])
                if key in seen:
                    attempt['theorem_skipped'] = 'duplicate_prepared_frame'
                    continue
                seen.add(key)
                for side_first in ('lower', 'upper'):
                    if not remaining or solved:
                        break
                    result = compile_pair(prepared['final_pair'], stable=stable,
                        source_index=prepared['source_index'],
                        boundary_order=(side_first, 'upper' if side_first == 'lower' else 'lower'),
                        limits=replace(limits, budget=min(remaining, theorem_slice),
                            max_moves=limits.max_moves - prepared['elementary_moves']))
                    remaining -= result['charges']
                    theorem_charges += result['charges']
                    composed_moves = prepared['moves'] + result['moves']
                    composed_best = prepared['moves'] + result['best_moves']
                    assert replay(pair, composed_moves) == result['final_pair']
                    assert replay(pair, composed_best) == result['best_pair']
                    result['composed_moves'] = composed_moves
                    result['composed_best_moves'] = composed_best
                    result['composed_elementary_moves'] = len(composed_moves)
                    result['final_length_from_original'] = sum(map(len, result['final_pair']))
                    result['strict_length_improvement_from_original'] = result['best_length'] < sum(map(len, pair))
                    attempt['theorem_calls'].append(result)
                    if result['best_length'] < best_length:
                        best_pair, best_moves = result['best_pair'], composed_best
                        best_length = result['best_length']
                        best_origin = [len(attempts) - 1, side_first]
                    solved = result['status'] == 'solved'
    assert replay(pair, best_moves) == best_pair
    assert framing_charges + theorem_charges == limits.budget - remaining
    return {'input': list(pair), 'input_length': sum(map(len, pair)), 'solved': solved,
            'best_pair': best_pair, 'best_length': best_length, 'best_moves': best_moves,
            'best_elementary_moves': len(best_moves), 'best_origin': best_origin,
            'strict_length_improvement': best_length < sum(map(len, pair)),
            'charges': limits.budget - remaining, 'framing_charges': framing_charges,
            'theorem_charges': theorem_charges, 'attempts': attempts,
            'unique_ready_frames': len(seen), 'verified': True, 'limits': vars(limits),
            'wall_seconds': time.perf_counter() - start_wall,
            'cpu_seconds': time.process_time() - start_cpu}
