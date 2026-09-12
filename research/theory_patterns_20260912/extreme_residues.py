"""Finite extreme-power residue prefixes, with strict ordinary-AC certificates.

Depends on the frozen boundary compiler's bounded transaction/certificate core.
A pass decreases extreme-letter multiplicity; no completion theorem is asserted.
"""
from __future__ import annotations

try:
    from . import boundary_compiler as frozen
    from .ac_words import Factor, red
except ImportError:
    import boundary_compiler as frozen
    from ac_words import Factor, red


class _Residues(frozen._Compiler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.preparations = []
        self.residue_summary = None

    def prepare(self, side, allow_cyclic_cut):
        self.charge(1, 'residue_recognition')
        f, g = self.frame()
        if not f or not g:
            raise frozen._Stop('empty_fibre')
        a, b = frozen.support(g)
        boundary = a if side == 'lower' else b
        source_runs = frozen.runs(g, boundary)
        if len(source_runs) == 2 and source_runs[0][0] == 0 and source_runs[-1][1] == len(g) and allow_cyclic_cut:
            cut = source_runs[0][1]
            prefix = self.checked_expand(g[:cut])
            rotated = frozen.ired(g[cut:] + g[:cut])
            expected = self.checked_expand(rotated)
            before = self.trace.pair[self.si]
            self.unary('conjugate', self.si, prefix)
            if self.trace.pair[self.si] != expected:
                raise AssertionError('cyclic indexed cut did not match explicit conjugation')
            self.preparations.append({'rule': 'cyclic_indexed_cut', 'donor_index': self.si,
                                      'indexed_cut': cut, 'conjugator': prefix,
                                      'before': before, 'after': expected,
                                      'move_end': len(self.trace.moves)})
            g = rotated
            if not g:
                raise frozen._Stop('empty_fibre')
            if frozen.span(g) == 0:
                raise frozen._Stop('span_zero_donor_after_cyclic_cut')
            a, b = frozen.support(g)
            boundary = a if side == 'lower' else b
            source_runs = frozen.runs(g, boundary)
        if len(source_runs) != 1:
            self.failed_checkpoint = {'side': side, 'reason': 'extreme_not_one_circular_or_literal_run',
                                      'source_boundary_runs': len(source_runs)}
            raise frozen._Stop('residue_hypothesis_failed')
        if frozen.span(g) > frozen.span(f):
            self.failed_checkpoint = {'side': side, 'reason': 'source_span_exceeds_recipient_span',
                                      'source_span': frozen.span(g), 'recipient_span': frozen.span(f)}
            raise frozen._Stop('residue_hypothesis_failed')
        c, d = frozen.support(f)
        recipient_boundary = c if side == 'lower' else d
        m = abs(source_runs[0][2])
        e = 1 if source_runs[0][2] > 0 else -1
        q = recipient_boundary - boundary
        shifted = frozen.shift(g if e == 1 else frozen.iinv(g), q)
        start, stop, _ = frozen.runs(shifted, recipient_boundary)[0]
        C, E = shifted[:start], shifted[stop:]
        return {'side': side, 'boundary': recipient_boundary, 'q': q, 'm': m, 'e': e,
                'C': C, 'E': E, 'B': frozen.ired(frozen.iinv(C) + frozen.iinv(E))}

    def descend(self, candidate, nearest):
        f, _ = self.frame()
        boundary, m, q, e = (candidate[k] for k in ('boundary', 'm', 'q', 'e'))
        C, E, B = (candidate[k] for k in ('C', 'E', 'B'))
        initial_f = f
        initial_count = sum(i == boundary for i, _ in f)
        start_moves, start_uses, start_charges = len(self.trace.moves), self.relation_uses, self.charges
        while True:
            self.charge(1, 'residue_block_recognition')
            eligible = [(start, stop, k) for start, stop, k in frozen.runs(f, boundary)
                        if abs(k) >= m or (nearest and 2 * abs(k) > m)]
            if not eligible:
                break
            start, stop, k = eligible[0]
            eta = 1 if k > 0 else -1
            remainder = k - eta * m
            rem = ((boundary, 1 if remainder > 0 else -1),) * abs(remainder)
            post = f[stop:]
            replacement = B if eta == 1 else frozen.iinv(B)
            newf = frozen.ired(f[:start] + rem + replacement + post)
            if abs(remainder) >= abs(k):
                raise AssertionError('selected residue step does not decrease multiplicity')
            expected = red(self.checked_expand(newf) + self.stable)
            suffix = red(self.checked_expand(post) + self.stable)
            if eta == 1:
                conjugator = red(frozen.power(self.stable, -q) + self.checked_expand(frozen.iinv(E)) + suffix)
                sign = -e
            else:
                conjugator = red(frozen.power(self.stable, -q) + self.checked_expand(C) + suffix)
                sign = e
            before_count = sum(i == boundary for i, _ in f)
            after_count = sum(i == boundary for i, _ in newf)
            if after_count >= before_count:
                raise AssertionError('extreme multiplicity did not strictly decrease')
            self.factors(self.ri, (Factor(sign, conjugator),), expected,
                         {'rule': 'extreme_residue', 'side': candidate['side'], 'q': q, 'm': m,
                          'run_exponent': k, 'remainder': remainder,
                          'virtual_chunk': abs(k) < m,
                          'before_boundary_letters': before_count,
                          'after_boundary_letters': after_count})
            f = newf
        self.residue_summary = {'side': candidate['side'], 'm': m, 'q': q, 'nearest': nearest,
                                'boundary': boundary, 'before_multiplicity': initial_count,
                                'after_multiplicity': sum(i == boundary for i, _ in f),
                                'before_span': frozen.span(initial_f), 'after_span': frozen.span(f),
                                'empty_after': not f,
                                'span_strictly_decreased': not f or frozen.span(f) < frozen.span(initial_f),
                                'relation_uses': self.relation_uses - start_uses,
                                'charges': self.charges - start_charges,
                                'elementary_moves': len(self.trace.moves) - start_moves,
                                'remaining_boundary_runs': [k for _, _, k in frozen.runs(f, boundary)]}
        if self.relation_uses == start_uses:
            raise frozen._Stop('no_strict_residue_step')


def compile_residues(pair, *, stable='x', source_index=0, side='lower',
                     nearest=True, allow_cyclic_cut=True, limits=None):
    """Return one finite source-restored residue prefix in the literal frame.

    Optional donor conjugation merges an extreme run split across the indexed
    word boundary, and is explicitly retained in the output certificate. The
    nominated stable-exponent relator is normalized by a recorded inversion.
    These preliminary unary moves are separate from source-restored products.
    """
    if type(nearest) is not bool or type(allow_cyclic_cut) is not bool:
        raise ValueError('nearest and allow_cyclic_cut must be booleans')
    compiler = _Residues(pair, stable, source_index, (side,), frozen.Limits() if limits is None else limits)
    try:
        compiler.normalize(require_unimodular=False)
        candidate = compiler.prepare(side, allow_cyclic_cut)
        compiler.descend(candidate, nearest)
        reason = 'residue_prefix_complete'
    except frozen._Stop as stop:
        reason = stop.reason
    result = compiler.result(reason)
    result.update({'preparations': compiler.preparations, 'residue_summary': compiler.residue_summary,
                   'nearest': nearest, 'allow_cyclic_cut': allow_cyclic_cut})
    return result
