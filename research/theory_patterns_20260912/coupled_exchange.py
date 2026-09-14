"""Exact coupled three-AC2 exchanges and finite literal support descent.

The candidate family uses at most twelve support breakpoints per normalized
frame. All candidate work is charged, including rejected candidates; certified
ordinary-length minima also inspect temporary donors inside each transaction.
"""
from __future__ import annotations

try:
    from . import boundary_compiler as frozen
    from .ac_words import cyclic, inv, red, replay
except ImportError:
    import boundary_compiler as frozen
    from ac_words import cyclic, inv, red, replay


def breakpoint_candidates(f, g, require_donor_change=True):
    if not f or not g:
        return []
    a, b = frozen.support(f)
    candidates = []
    for sign in (-1, 1):
        oriented = g if sign == 1 else frozen.iinv(g)
        if f[0][1] != oriented[0][1]:
            continue
        q = f[0][0] - oriented[0][0]
        h = frozen.ired(frozen.iinv(frozen.shift(oriented, q)) + f)
        if not h:
            ks = {1 if require_donor_change else 0}
        else:
            u, v = frozen.support(h)
            ks = {0, u - a, v - b, h[-1][0] - f[-1][0], -1, 1}
            if require_donor_change:
                ks.discard(0)
        candidates.extend({'donor_sign': sign, 'q': q, 'k': k} for k in sorted(ks))
    return candidates


class _TrackedTrace(frozen._BoundTrace):
    def __init__(self, pair, limit, remaining_moves):
        super().__init__(pair, limit, remaining_moves)
        self.raw_minimum = sum(map(len, pair))
        self.cyclic_minimum = sum(len(cyclic(w)[0]) for w in pair)
        self.best_snapshot = list(pair)
        self.best_snapshot_moves = []
        self.best_stage = 'start'
        self.stage = 'start'

    def _check(self):
        super()._check()
        self.raw_minimum = min(self.raw_minimum, sum(map(len, self.pair)))
        length = sum(len(cyclic(w)[0]) for w in self.pair)
        if length < self.cyclic_minimum:
            self.cyclic_minimum = length
            self.best_snapshot = list(self.pair)
            self.best_snapshot_moves = list(self.moves)
            self.best_stage = self.stage


class _Coupled(frozen._Compiler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.candidates = []
        self.exchanges = []
        self.candidate_elementary_moves = 0
        self.candidate_ac2_moves = 0
        self.best_origin = {'kind': 'input'}
        self.minimum_raw_candidate_length = sum(map(len, self.trace.pair))

    def _observe(self, staged, specification):
        self.candidate_elementary_moves += len(staged.moves)
        self.candidate_ac2_moves += sum(m['op'] == 'multiply' for m in staged.moves)
        self.minimum_raw_candidate_length = min(self.minimum_raw_candidate_length, staged.raw_minimum)
        if staged.cyclic_minimum >= self.best_length:
            return
        prefix_moves = list(self.trace.moves) + staged.best_snapshot_moves
        snapshot = frozen._BoundTrace(staged.best_snapshot, self.limits.max_word_length,
                                     self.limits.max_moves - len(prefix_moves))
        cores = [cyclic(w) for w in staged.best_snapshot]
        cleanup = sum(bool(p) for _, p in cores)
        if self.charges + cleanup > self.limits.budget:
            return
        try:
            for target, (_, prefix) in enumerate(cores):
                snapshot.conjugate(target, prefix)
        except frozen._Stop:
            return
        self.charge(cleanup, 'best_prefix_cleanup')
        self.best_pair = list(snapshot.pair)
        self.best_moves = prefix_moves + snapshot.moves
        self.best_length = staged.cyclic_minimum
        self.best_origin = {'kind': 'candidate_elementary_prefix', **specification,
                            'stage': staged.best_stage,
                            'candidate_prefix_elementary_moves': len(staged.best_snapshot_moves),
                            'cleanup_elementary_moves': len(snapshot.moves)}

    def candidate(self, specification):
        sign, q, k = (specification[name] for name in ('donor_sign', 'q', 'k'))
        self.charge(1, 'candidate')
        self.charge(3, 'candidate_relation_uses')
        self.charge(4 + (sign == -1) + (q != 0) + 2 * (k != 0), 'candidate_unary_operations')
        f, g = self.frame()
        dg = frozen.shift(g if sign == 1 else frozen.iinv(g), q)
        h = frozen.ired(frozen.iinv(dg) + f)
        b = frozen.ired(f + frozen.shift(frozen.iinv(h), -k))
        before_phi = frozen.span(f) + frozen.span(g)
        summary = {**specification, 'input': list(self.trace.pair),
                   'prefix_move_count': len(self.trace.moves), 'before_phi': before_phi,
                   'after_phi': frozen.span(h) + frozen.span(b),
                   'after_spans': [frozen.span(h), frozen.span(b)],
                   'empty_stable_fibre_after': not h,
                   'span_zero_zero_fibre_after': bool(b) and frozen.span(b) == 0,
                   'donor_changed_after_preorientation': b != dg,
                   'strict_phi_descent': frozen.span(h) + frozen.span(b) < before_phi}
        staged = _TrackedTrace(self.trace.pair, self.limits.max_word_length,
                               self.limits.max_moves - len(self.trace.moves))
        reason = 'evaluated'
        try:
            expected_move_count = 7 + 2 * abs(k) + abs(q) + (sign == -1)
            if expected_move_count > self.limits.max_moves - len(self.trace.moves):
                raise frozen._Stop('certificate_limit')
            expected = list(self.trace.pair)
            expected[self.ri] = red(self.checked_expand(h) + self.stable)
            expected[self.si] = self.checked_expand(b)
            staged.stage = 'orient_donor'
            if sign == -1:
                staged.invert(self.si)
            staged.conjugate(self.si, frozen.power(self.stable, -q))
            staged.stage = 'first_row_left_product'
            staged.invert(self.ri)
            staged.multiply(self.ri)
            staged.invert(self.ri)
            staged.stage = 'temporary_donor_is_original_source'
            staged.multiply(self.si)
            staged.stage = 'conjugated_inverse_changed_source'
            staged.invert(self.ri)
            staged.conjugate(self.ri, frozen.power(self.stable, k))
            staged.stage = 'final_donor_product'
            staged.multiply(self.si)
            staged.stage = 'restore_changed_source'
            staged.conjugate(self.ri, frozen.power(self.stable, -k))
            staged.invert(self.ri)
            if staged.pair != expected or replay(self.trace.pair, staged.moves) != expected:
                raise AssertionError('coupled exchange failed exact prediction/independent replay')
            expected_move_count = 7 + 2 * abs(k) + abs(q) + (sign == -1)
            if len(staged.moves) != expected_move_count:
                raise AssertionError('coupled elementary count does not match emitted stream')
        except frozen._Stop as stop:
            reason = stop.reason
        self._observe(staged, specification)
        summary.update({'reason': reason, 'elementary_moves': len(staged.moves),
                        'candidate_ac2_moves': sum(m['op'] == 'multiply' for m in staged.moves),
                        'minimum_raw_length': staged.raw_minimum,
                        'minimum_cyclic_length': staged.cyclic_minimum,
                        'minimum_stage': staged.best_stage})
        if reason == 'evaluated':
            summary.update({'after': list(staged.pair), 'moves': staged.moves,
                            'peak_relator_length': staged.peak})
        else:
            summary['strict_phi_descent'] = False
        self.candidates.append(summary)
        return staged if reason == 'evaluated' else None, summary

    def output(self, reason, require_donor_change):
        result = self.result(reason)
        result.update({'candidates': self.candidates, 'exchanges': self.exchanges,
                       'require_donor_change': require_donor_change,
                       'candidate_elementary_moves': self.candidate_elementary_moves,
                       'candidate_ac2_moves': self.candidate_ac2_moves,
                       'minimum_raw_candidate_length': self.minimum_raw_candidate_length,
                       'best_origin': self.best_origin})
        return result


def compile_coupled(pair, *, stable='x', source_index=0, require_donor_change=True,
                    max_exchanges=1, limits=None):
    """Accept strict support-potential exchanges from the complete breakpoint set.

    Temporary candidate words contribute certified best ordinary-length prefixes
    even if their exchange is not selected. The accepted path itself only takes
    strict Phi decreases. Terminal checkpoints are returned for a separate
    bounded frozen-compiler cleanup; this function does not assert a solve.
    """
    if type(require_donor_change) is not bool:
        raise ValueError('require_donor_change must be a boolean')
    if type(max_exchanges) is not int or not 1 <= max_exchanges <= 1000:
        raise ValueError('max_exchanges must be an integer in 1..1000')
    compiler = _Coupled(pair, stable, source_index, ('lower', 'upper'), frozen.Limits() if limits is None else limits)
    try:
        compiler.normalize(require_unimodular=True)
        for _ in range(max_exchanges):
            compiler.charge(1, 'checkpoint')
            f, g = compiler.frame()
            if not f or (g and frozen.span(g) == 0):
                raise frozen._Stop('terminal_checkpoint')
            compiler.charge(2, 'orientation_recognition')
            specifications = breakpoint_candidates(f, g, require_donor_change)
            if len(specifications) > 12:
                raise AssertionError('breakpoint family exceeded twelve candidates')
            accepted = []
            for specification in specifications:
                staged, summary = compiler.candidate(specification)
                if staged is not None and summary['strict_phi_descent']:
                    if require_donor_change and not summary['donor_changed_after_preorientation'] and not summary['empty_stable_fibre_after']:
                        raise AssertionError('nonterminal donor-changing filter failed')
                    accepted.append((staged, summary))
            if not accepted:
                rejected = sum(c['reason'] != 'evaluated' for c in compiler.candidates[-len(specifications):]) if specifications else 0
                compiler.failed_checkpoint = {'phi': frozen.span(f) + frozen.span(g),
                                              'tested_candidates': len(specifications),
                                              'resource_rejections': rejected}
                raise frozen._Stop('coupled_candidate_resource_limit' if rejected else 'no_strict_coupled_descent')
            staged, summary = min(accepted, key=lambda item: (item[1]['after_phi'],
                sum(map(len, item[0].pair)), len(item[0].moves), item[1]['donor_sign'], item[1]['q'], item[1]['k']))
            compiler.relation_uses += 3
            compiler.commit(staged)
            compiler.exchanges.append({k: v for k, v in summary.items() if k != 'moves'})
            newf, newg = compiler.frame()
            if not newf or (newg and frozen.span(newg) == 0):
                raise frozen._Stop('terminal_checkpoint')
        reason = 'exchange_limit_reached'
    except frozen._Stop as stop:
        reason = stop.reason
    return compiler.output(reason, require_donor_change)


def compile_exchange(pair, *, stable='x', source_index=0, donor_sign=1, q=0, k=1, limits=None):
    """Compile one specified exchange without a descent or unimodularity claim."""
    if type(donor_sign) is not int or donor_sign not in (-1, 1):
        raise ValueError('donor_sign must be integer ±1')
    if type(q) is not int or type(k) is not int:
        raise ValueError('q and k must be integers')
    compiler = _Coupled(pair, stable, source_index, ('lower', 'upper'), frozen.Limits() if limits is None else limits)
    try:
        compiler.normalize(require_unimodular=False)
        staged, summary = compiler.candidate({'donor_sign': donor_sign, 'q': q, 'k': k})
        if staged is None:
            raise frozen._Stop(summary['reason'])
        compiler.relation_uses += 3
        compiler.commit(staged)
        compiler.exchanges.append({key: value for key, value in summary.items() if key != 'moves'})
        reason = 'specified_exchange_complete'
    except frozen._Stop as stop:
        reason = stop.reason
    return compiler.output(reason, False)
