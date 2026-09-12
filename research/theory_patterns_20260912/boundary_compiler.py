"""Bounded ordinary-AC compiler for alternating literal Magnus boundaries.

No ambient automorphism or search is used. Charges count frame/checkpoint
recognition, proposed block rewrites, retained-source relation uses, and individual
terminal/normalization operations; emitted elementary moves are counted apart.
Resource stops return the last committed source-restored certificate prefix.
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    from .ac_words import Factor, Trace, cyclic, exponent, inv, red, replay
except ImportError:
    from ac_words import Factor, Trace, cyclic, exponent, inv, red, replay


def ired(word):
    stack = []
    for index, sign in word:
        if stack and stack[-1] == (index, -sign):
            stack.pop()
        else:
            stack.append((index, sign))
    return tuple(stack)


def iinv(word):
    return tuple((index, -sign) for index, sign in reversed(word))


def shift(word, amount):
    return tuple((index + amount, sign) for index, sign in word)


def collect(word, stable):
    height = 0
    out = []
    for letter in word:
        if letter == stable:
            height += 1
        elif letter == stable.upper():
            height -= 1
        else:
            out.append((height, 1 if letter.islower() else -1))
    return ired(out), height


def support(word):
    if not word:
        return None
    indices = [index for index, _ in word]
    return min(indices), max(indices)


def span(word):
    ends = support(word)
    return 0 if ends is None else ends[1] - ends[0]


def power(letter, number):
    return letter * number if number >= 0 else inv(letter) * -number


def expand(word, stable):
    base = 'y' if stable == 'x' else 'x'
    parts = []
    height = 0
    for index, sign in word:
        parts.extend((power(stable, index - height), power(base, sign)))
        height = index
    parts.append(power(stable, -height))
    return red(''.join(parts))


def runs(word, index):
    found = []
    start = 0
    while start < len(word):
        if word[start][0] != index:
            start += 1
            continue
        stop = start + 1
        while stop < len(word) and word[stop][0] == index:
            stop += 1
        found.append((start, stop, sum(sign for _, sign in word[start:stop])))
        start = stop
    return found


@dataclass(frozen=True)
class Limits:
    budget: int = 1000
    max_word_length: int = 4096
    max_indexed_length: int = 2048
    max_moves: int = 100000

    def __post_init__(self):
        for name in ('budget', 'max_word_length', 'max_indexed_length', 'max_moves'):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f'{name} must be a nonnegative integer')
        if self.budget > 1000:
            raise ValueError('budget must be at most 1000 algebraic charges')


class _Stop(Exception):
    def __init__(self, reason):
        self.reason = reason


class _BoundTrace(Trace):
    def __init__(self, pair, limit, remaining_moves):
        super().__init__(pair)
        self.limit = limit
        self.remaining_moves = remaining_moves
        self.peak = max(map(len, self.pair))

    def _check(self):
        self.peak = max(self.peak, *map(len, self.pair))
        if self.peak > self.limit:
            raise _Stop('word_limit')
        if len(self.moves) > self.remaining_moves:
            raise _Stop('certificate_limit')

    def invert(self, target):
        super().invert(target)
        self._check()

    def multiply(self, target):
        super().multiply(target)
        self._check()

    def conjugate(self, target, word):
        for letter in red(word):
            super().conjugate(target, letter)
            self._check()


class _Compiler:
    def __init__(self, pair, stable, source_index, boundary_order, limits):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError('exactly two relators required')
        if any(not isinstance(w, str) or any(c not in 'xXyY' for c in w) for w in pair):
            raise ValueError('relators must be strings over xXyY')
        if stable not in ('x', 'y'):
            raise ValueError('stable must be x or y')
        if type(source_index) is not int or source_index not in (0, 1):
            raise ValueError('source_index must be integer 0 or 1')
        if not isinstance(boundary_order, (list, tuple)) or not boundary_order:
            raise ValueError('at least one boundary is required')
        if any(side not in ('lower', 'upper') for side in boundary_order) or len(set(boundary_order)) != len(boundary_order):
            raise ValueError('boundary_order must contain distinct lower/upper choices')
        if not isinstance(limits, Limits):
            raise ValueError('limits must be a Limits instance')
        self.original = list(pair)
        self.trace = Trace(pair)
        self.stable, self.ri, self.si = stable, source_index, 1 - source_index
        self.boundary_order, self.limits = tuple(boundary_order), limits
        self.charges = 0
        self.charge_kinds = {}
        self.relation_uses = 0
        self.passes = []
        self.ledgers = []
        self.peak = max(map(len, self.trace.pair))
        self.best_pair = list(self.trace.pair)
        self.best_moves = []
        self.best_length = sum(map(len, self.best_pair))
        self.frame_sign = None
        self.virtual_source_sign = 1
        self.initial_potential = None
        self.failed_checkpoint = None

    def charge(self, count, kind):
        if self.charges + count > self.limits.budget:
            raise _Stop('work_limit')
        self.charges += count
        self.charge_kinds[kind] = self.charge_kinds.get(kind, 0) + count

    def checked_expand(self, word):
        if len(word) > self.limits.max_indexed_length:
            raise _Stop('indexed_word_limit')
        # This expansion is freely reduced when its indexed spelling is reduced.
        length = len(word)
        previous = 0
        for index, _ in word:
            length += abs(index - previous)
            previous = index
        length += abs(previous)
        if length > self.limits.max_word_length:
            raise _Stop('word_limit')
        return expand(word, self.stable)

    def _new_trace(self):
        return _BoundTrace(self.trace.pair, self.limits.max_word_length,
                           self.limits.max_moves - len(self.trace.moves))

    def commit(self, staged):
        self.trace.pair = staged.pair
        self.trace.moves.extend(staged.moves)
        self.peak = max(self.peak, staged.peak)
        self.record_best()

    def record_best(self):
        reduced = [cyclic(w) for w in self.trace.pair]
        length = sum(len(core) for core, _ in reduced)
        if length >= self.best_length:
            return
        cleanup_operations = sum(bool(prefix) for _, prefix in reduced)
        if self.charges + cleanup_operations > self.limits.budget:
            return
        staged = self._new_trace()
        try:
            for j, (_, prefix) in enumerate(reduced):
                staged.conjugate(j, prefix)
        except _Stop:
            return
        self.charge(cleanup_operations, 'best_prefix_cleanup')
        self.best_pair = list(staged.pair)
        self.best_moves = list(self.trace.moves) + staged.moves
        self.best_length = length

    def unary(self, kind, target, argument=None):
        self.charge(1, 'relation_use' if kind == 'multiply' else 'unary')
        staged = self._new_trace()
        if kind == 'invert':
            staged.invert(target)
        elif kind == 'conjugate':
            staged.conjugate(target, argument)
        else:
            staged.multiply(target)
            self.relation_uses += 1
        self.commit(staged)

    def factors(self, target, factors, expected, ledger):
        self.charge(len(factors), 'relation_use')
        staged = self._new_trace()
        donor_before = staged.pair[1 - target]
        staged.append_factors(target, factors)
        if staged.pair[target] != expected or staged.pair[1 - target] != donor_before:
            raise AssertionError('restored-source ledger does not match predicted word')
        self.relation_uses += len(factors)
        self.commit(staged)
        self.ledgers.append({**ledger, 'target': target, 'factors': [
            {'sign': f.sign, 'conjugator': f.conjugator} for f in factors],
            'after': expected, 'move_end': len(self.trace.moves)})

    def frame(self):
        source = self.trace.pair[self.ri]
        f, e = collect(source if self.virtual_source_sign == 1 else inv(source), self.stable)
        g, z = collect(self.trace.pair[self.si], self.stable)
        if e != 1 or z != 0:
            raise AssertionError('literal stable-exponent frame was not preserved')
        return f, g

    def normalize(self, require_unimodular, normalize_source=True):
        self.charge(1, 'frame_recognition')
        if self.peak > self.limits.max_word_length:
            raise _Stop('word_limit')
        r, s = self.trace.pair[self.ri], self.trace.pair[self.si]
        e = exponent(r, self.stable)
        if abs(e) != 1 or exponent(s, self.stable) != 0:
            raise _Stop('frame_not_recognized')
        base = 'y' if self.stable == 'x' else 'x'
        if require_unimodular and abs(exponent(s, base)) != 1:
            raise _Stop('not_unimodular')
        self.frame_sign = e
        if e == -1 and normalize_source:
            self.unary('invert', self.ri)
        elif e == -1:
            self.virtual_source_sign = -1
        f, g = self.frame()
        if max(len(f), len(g)) > self.limits.max_indexed_length:
            raise _Stop('indexed_word_limit')
        self.initial_potential = span(f) + span(g)
        self.record_best()

    def boundary_pass(self, side, q=None):
        f, g = self.frame()
        if not f or not g or span(f) >= span(g):
            raise _Stop('boundary_span_hypothesis_failed')
        a, b = support(f)
        c, d = support(g)
        lo, hi = c + 1 - a, d - b
        if q is None:
            q = lo
        if type(q) is not int or not lo <= q <= hi:
            raise ValueError('q must be an integer in [c+1-a,d-b]')
        boundary = c if side == 'lower' else d
        direction = 1 if side == 'lower' else -1
        fq = shift(f, q)
        old_span, start_moves = span(g), len(self.trace.moves)
        start_uses, start_charges = self.relation_uses, self.charges
        while runs(g, boundary):
            self.charge(1, 'block_recognition')
            start, stop, _ = runs(g, boundary)[0]
            h, post = g[start:stop], g[stop:]
            if direction == 1:
                replacement = ired(fq + shift(h, 1) + iinv(fq))
            else:
                fm = shift(fq, -1)
                replacement = ired(iinv(fm) + shift(h, -1) + fm)
            newg = ired(g[:start] + replacement + post)
            new_word = self.checked_expand(newg)
            H, Q = self.checked_expand(h), self.checked_expand(post)
            c1, c2 = red(power(self.stable, -q) + H + Q), red(power(self.stable, -q) + Q)
            self.factors(self.si, (Factor(self.virtual_source_sign * direction, c1),
                                   Factor(-self.virtual_source_sign * direction, c2)), new_word,
                         {'rule': 'stable_boundary', 'side': side, 'q': q,
                          'before_boundary_letters': sum(i == boundary for i, _ in g),
                          'after_boundary_letters': sum(i == boundary for i, _ in newg)})
            if sum(i == boundary for i, _ in newg) >= sum(i == boundary for i, _ in g):
                raise AssertionError('boundary occurrence count did not decrease')
            g = newg
        if g and span(g) >= old_span:
            raise AssertionError('completed boundary pass did not decrease span')
        self.passes.append({'rule': 'stable_boundary', 'side': side, 'q': q,
                            'changed_relator': self.si, 'before_span': old_span,
                            'after_span': span(g), 'empty_after': not g,
                            'relation_uses': self.relation_uses - start_uses,
                            'charges': self.charges - start_charges,
                            'elementary_moves': len(self.trace.moves) - start_moves})

    def power_candidate(self, side, f, g):
        a, b = support(g)
        c, d = support(f)
        donor_boundary, recipient_boundary = (a, c) if side == 'lower' else (b, d)
        source_runs = runs(g, donor_boundary)
        if len(source_runs) != 1:
            return None, {'side': side, 'reason': 'extreme_not_one_literal_run',
                          'source_boundary_runs': len(source_runs)}
        m = abs(source_runs[0][2])
        bad = [ex for _, _, ex in runs(f, recipient_boundary) if ex % m]
        if bad:
            return None, {'side': side, 'reason': 'extreme_run_not_divisible',
                          'm': m, 'recipient_exponents_not_divisible': bad}
        e = 1 if source_runs[0][2] > 0 else -1
        shifted = shift(g if e == 1 else iinv(g), recipient_boundary - donor_boundary)
        start, stop, _ = runs(shifted, recipient_boundary)[0]
        C, E = shifted[:start], shifted[stop:]
        return {'side': side, 'boundary': recipient_boundary, 'q': recipient_boundary - donor_boundary,
                'm': m, 'e': e, 'C': C, 'E': E, 'B': ired(iinv(C) + iinv(E))}, None

    def power_pass(self, candidate):
        f, g = self.frame()
        side, boundary, q = candidate['side'], candidate['boundary'], candidate['q']
        m, e, C, E, B = (candidate[k] for k in ('m', 'e', 'C', 'E', 'B'))
        old_span, start_moves = span(f), len(self.trace.moves)
        start_uses, start_charges = self.relation_uses, self.charges
        while runs(f, boundary):
            self.charge(1, 'block_recognition')
            start, _, run_exponent = runs(f, boundary)[0]
            if run_exponent % m:
                raise AssertionError('divisible boundary run invariant lost')
            eta = 1 if run_exponent > 0 else -1
            stop = start + m
            post = f[stop:]
            newf = ired(f[:start] + (B if eta == 1 else iinv(B)) + post)
            new_word = red(self.checked_expand(newf) + self.stable)
            suffix = red(self.checked_expand(post) + self.stable)
            if eta == 1:
                conj = red(power(self.stable, -q) + self.checked_expand(iinv(E)) + suffix)
                sign = -e
            else:
                conj = red(power(self.stable, -q) + self.checked_expand(C) + suffix)
                sign = e
            self.factors(self.ri, (Factor(sign, conj),), new_word,
                         {'rule': 'extreme_power', 'side': side, 'q': q, 'm': m, 'eta': eta,
                          'before_boundary_letters': sum(i == boundary for i, _ in f),
                          'after_boundary_letters': sum(i == boundary for i, _ in newf)})
            if sum(i == boundary for i, _ in newf) >= sum(i == boundary for i, _ in f):
                raise AssertionError('power boundary occurrence count did not decrease')
            f = newf
        if f and span(f) >= old_span:
            raise AssertionError('completed power pass did not decrease span')
        self.passes.append({'rule': 'extreme_power', 'side': side, 'q': q, 'm': m,
                            'changed_relator': self.ri, 'before_span': old_span,
                            'after_span': span(f), 'empty_after': not f,
                            'relation_uses': self.relation_uses - start_uses,
                            'charges': self.charges - start_charges,
                            'elementary_moves': len(self.trace.moves) - start_moves})

    def delete_generator(self, target, generator):
        if self.trace.pair[1 - target] != generator:
            raise AssertionError('terminal donor must be the positive generator')
        while any(c.lower() == generator for c in self.trace.pair[target]):
            self.charge(1, 'block_recognition')
            word = self.trace.pair[target]
            pos = next(i for i, c in enumerate(word) if c.lower() == generator)
            eta = 1 if word[pos].islower() else -1
            suffix = word[pos + 1:]
            expected = red(word[:pos] + suffix)
            self.factors(target, (Factor(-eta, suffix),), expected,
                         {'rule': 'terminal_generator_delete'})

    def finish(self):
        f, g = self.frame()
        t, z = self.stable, ('y' if self.stable == 'x' else 'x')
        if not g:
            raise _Stop('empty_zero_fibre')
        if not f:
            if self.trace.pair[self.ri] != t:
                raise AssertionError('empty stable fibre is not the stable generator')
            self.delete_generator(self.si, t)
            if self.trace.pair[self.si] == z.upper():
                self.unary('invert', self.si)
        elif span(g) == 0:
            index = g[0][0]
            self.unary('conjugate', self.si, power(t, index))
            if self.trace.pair[self.si] == z.upper():
                self.unary('invert', self.si)
            self.delete_generator(self.ri, z)
        else:
            raise AssertionError('finish called without a terminal condition')
        if self.trace.pair == ['y', 'x']:
            for kind, target in [('invert', 0), ('multiply', 1), ('invert', 1),
                                 ('multiply', 0), ('invert', 0), ('multiply', 1)]:
                self.unary(kind, target)
        if self.trace.pair != ['x', 'y']:
            raise AssertionError('unimodular terminal cleanup did not reach x,y')

    def result(self, reason):
        if replay(self.original, self.trace.moves) != self.trace.pair:
            raise AssertionError('independent certificate replay failed')
        if replay(self.original, self.best_moves) != self.best_pair:
            raise AssertionError('independent best-prefix replay failed')
        f, g = collect(self.trace.pair[self.ri], self.stable)[0], collect(self.trace.pair[self.si], self.stable)[0]
        return {'status': 'solved' if reason == 'solved' else 'partial', 'reason': reason,
                'input': self.original, 'final_pair': list(self.trace.pair),
                'stable': self.stable, 'source_index': self.ri,
                'source_sign_normalization': self.frame_sign,
                'boundary_order': list(self.boundary_order),
                'initial_potential': self.initial_potential,
                'final_spans': [span(f), span(g)], 'passes': self.passes,
                'failed_checkpoint': self.failed_checkpoint,
                'charges': self.charges, 'charge_kinds': self.charge_kinds,
                'relation_uses_committed': self.relation_uses,
                'elementary_moves': len(self.trace.moves), 'moves': self.trace.moves,
                'ledgers': self.ledgers, 'peak_committed_relator_length': self.peak,
                'best_pair': self.best_pair, 'best_length': self.best_length,
                'best_moves': self.best_moves,
                'strict_length_improvement': self.best_length < sum(map(len, self.original)),
                'verified': True, 'limits': vars(self.limits)}


def compile_pair(pair, *, stable='x', source_index=0,
                 boundary_order=('lower', 'upper'), limits=None):
    """Compile the conditional alternating-span algorithm in one literal frame.

    Recognition and failure concern this exact frame and boundary order only.
    Every result includes independently replayed strict ordinary-AC certificates
    for final_pair and best_pair, even on criterion/resource failure.
    """
    compiler = _Compiler(pair, stable, source_index, boundary_order, Limits() if limits is None else limits)
    try:
        compiler.normalize(require_unimodular=True)
        while True:
            compiler.charge(1, 'checkpoint')
            f, g = compiler.frame()
            if not g:
                raise _Stop('empty_zero_fibre')
            if not f or span(g) == 0:
                compiler.finish()
                reason = 'solved'
                break
            old_potential = span(f) + span(g)
            if span(g) > span(f):
                compiler.boundary_pass(compiler.boundary_order[0])
            else:
                failures = []
                for side in compiler.boundary_order:
                    compiler.charge(1, 'power_recognition')
                    candidate, failure = compiler.power_candidate(side, f, g)
                    if candidate is not None:
                        compiler.power_pass(candidate)
                        break
                    failures.append(failure)
                else:
                    compiler.failed_checkpoint = {'stable_fibre_span': span(f),
                                                  'zero_fibre_span': span(g),
                                                  'boundaries': failures}
                    raise _Stop('criterion_failed')
            newf, newg = compiler.frame()
            if newf and newg and span(newf) + span(newg) >= old_potential:
                raise AssertionError('completed nonterminal pass did not reduce potential')
    except _Stop as stop:
        reason = stop.reason
    return compiler.result(reason)


def compile_boundary_pass(pair, *, stable='x', source_index=0,
                          side='lower', q=None, limits=None):
    """Compile one new stable-source boundary pass, restoring that exact source.

    A negative stable source is normalized only in the indexed calculation;
    the supplied source word is restored literally even at a resource stop.
    Unimodularity is unnecessary for this standalone identity.
    """
    compiler = _Compiler(pair, stable, source_index, (side,), Limits() if limits is None else limits)
    try:
        compiler.normalize(require_unimodular=False, normalize_source=False)
        compiler.charge(1, 'checkpoint')
        compiler.boundary_pass(side, q=q)
        reason = 'boundary_pass_complete'
    except _Stop as stop:
        reason = stop.reason
    return compiler.result(reason)
