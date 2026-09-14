"""Bounded greedy dictionary compression of already audited stable tuples."""
from __future__ import annotations

from functools import lru_cache
import time

ALPHABET = 'xXyYzZuUvVwW'
HELPERS = ('u', 'v', 'w', 'z', 'x', 'y')


def inv(word):
    return word.swapcase()[::-1]


def red(word):
    stack = []
    for letter in word:
        if letter not in ALPHABET:
            raise ValueError('word outside supported six-generator alphabet')
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return ''.join(stack)


def cyclic(word):
    word = red(word)
    start, stop = 0, len(word)
    while stop - start > 1 and word[start] == word[stop - 1].swapcase():
        start += 1
        stop -= 1
    return word[start:stop], word[:start]


def tokenize(word, defining, helper):
    blocks = ((defining, helper), (inv(defining), helper.upper()))
    best = [''] * (len(word) + 1)
    for position in range(len(word) - 1, -1, -1):
        options = [word[position] + best[position + 1]]
        for block, token in blocks:
            if word.startswith(block, position):
                options.append(token + best[position + len(block)])
        best[position] = min(options, key=lambda value: (len(value), value))
    return best[0]


@lru_cache(maxsize=65536)
def cyclic_compression(word, defining, helper):
    return min((len(compressed), compressed, cut)
               for cut in range(max(1, len(word)))
               for compressed in (tokenize(word[cut:] + word[:cut], defining, helper),))[1:]


def boundary(label, words, basis):
    return {'label': label, 'basis': list(basis), 'rank': len(basis), 'relators': list(words),
            'relator_lengths': list(map(len, words)), 'total_length': sum(map(len, words))}


def validate(words, basis):
    if not isinstance(words, (list, tuple)) or not isinstance(basis, (list, tuple)):
        raise ValueError('words and basis must be sequences')
    if not 2 <= len(words) == len(basis) <= 6 or len(set(basis)) != len(basis):
        raise ValueError('balanced rank from two through six is required')
    if any(g not in 'xyzuvw' for g in basis):
        raise ValueError('invalid basis')
    if any(not isinstance(w, str) or any(c.lower() not in basis for c in w) or red(w) != w for w in words):
        raise ValueError('relators must be reduced words in the active basis')


def find_compression(words, basis, remaining):
    total = sum(map(len, words))
    helper = next(letter for letter in HELPERS if letter not in basis)
    definitions = set()
    for word in words:
        doubled = word + word
        for length in range(2, min(len(word), total // 2) + 1):
            for cut in range(len(word)):
                candidate = doubled[cut:cut + length]
                if red(candidate) == candidate:
                    definitions.add(min(candidate, inv(candidate)))
    best, processed = None, 0
    for defining in sorted(definitions, key=lambda value: (len(value), value)):
        if processed == remaining:
            break
        processed += 1
        compressed, cuts = zip(*(cyclic_compression(word, defining, helper) for word in words))
        after = [helper.upper() + defining, *compressed]
        length = sum(map(len, after))
        if length >= total or best is not None and length >= best['total_length']:
            continue
        tokens = [word.count(helper) + word.count(helper.upper()) for word in compressed]
        formula = total + len(defining) + 1 - sum(tokens) * (len(defining) - 1)
        if formula != length or any(red(word) != word for word in after):
            raise AssertionError('literal token count or free-reduction invariant failed')
        best = {'helper': helper, 'defining_word': defining, 'cuts': list(cuts),
                'rotation_conjugators': [word[:cut] for word, cut in zip(words, cuts)],
                'compressed_relators': list(compressed), 'relators': after,
                'basis_before': list(basis), 'basis_after': [*basis, helper],
                'rank': len(after), 'input_total_length': total, 'total_length': length,
                'token_counts': tokens, 'formula_length': formula,
                'certificate_kind': 'theorem_backed_stable_literal_prefix'}
    return {'definitions_generated': len(definitions), 'defining_word_candidates': processed,
            'definition_screen_complete': processed == len(definitions), 'best': best}


class Trace:
    def __init__(self, words):
        self.words = list(words)
        self.moves = []

    def invert(self, target):
        self.words[target] = inv(self.words[target])
        self.moves.append({'op': 'invert', 'target': target + 1})

    def multiply(self, target, source):
        self.words[target] = red(self.words[target] + self.words[source])
        self.moves.append({'op': 'multiply', 'target': target + 1, 'source': source + 1})

    def conjugate(self, target, word):
        for letter in word:
            self.words[target] = red(letter.swapcase() + self.words[target] + letter)
            self.moves.append({'op': 'conjugate', 'target': target + 1, 'by': letter})


def delete_singleton(words, basis):
    source = next((i for i, word in enumerate(words) if len(word) == 1), None)
    if source is None or len(basis) <= 2:
        return None
    before, old_basis = list(words), list(basis)
    axis = words[source].lower()
    trace = Trace(words)
    if trace.words[source].isupper():
        trace.invert(source)
    for target in range(len(words)):
        if target == source:
            continue
        while axis in trace.words[target].lower():
            word = trace.words[target]
            position = next(i for i, letter in enumerate(word) if letter.lower() == axis)
            letter, suffix = word[position], word[position + 1:]
            if letter.islower():
                trace.invert(source)
            trace.conjugate(source, suffix)
            trace.multiply(target, source)
            trace.conjugate(source, inv(suffix))
            if letter.islower():
                trace.invert(source)
            if trace.words[source] != axis:
                raise AssertionError('singleton donor was not restored')
    after_substitutions = list(trace.words)
    if any(axis in word.lower() for i, word in enumerate(trace.words) if i != source):
        raise AssertionError('deleted generator remains in another relator')
    trace.words.pop(source)
    new_basis = [g for g in basis if g != axis]
    after_deletion = list(trace.words)
    cleanup = Trace(trace.words)
    for target in range(len(cleanup.words)):
        _, prefix = cyclic(cleanup.words[target])
        cleanup.conjugate(target, prefix)
    return {'kind': 'strict_singleton_deletion', 'before': before, 'basis_before': old_basis,
            'source_index': source, 'generator': axis, 'ordinary_moves': trace.moves,
            'after_substitutions': after_substitutions,
            'destabilization': {'generator': axis, 'relator_index': source},
            'after_deletion': after_deletion, 'basis_after': new_basis,
            'cyclic_cleanup_moves': cleanup.moves, 'after': cleanup.words}


def run(words, *, basis=('x', 'y', 'z'), candidate_limit=1000, rank_limit=6):
    validate(words, basis)
    if type(candidate_limit) is not int or not 0 <= candidate_limit <= 1000:
        raise ValueError('candidate_limit must be an integer from zero through1000')
    if type(rank_limit) is not int or not len(basis) <= rank_limit <= 6:
        raise ValueError('rank_limit must be an integer between initial rank and six')
    if any(cyclic(word)[0] != word for word in words):
        raise ValueError('seed must be cyclically reduced')
    wall, cpu = time.perf_counter(), time.process_time()
    initial, current, active = list(words), list(words), list(basis)
    boundaries = [boundary('audited_seed', current, active)]
    rounds, deletions, events, used = [], [], [], 0
    while True:
        deletion = delete_singleton(current, active)
        if deletion is not None:
            deletions.append(deletion)
            events.append({'kind': 'singleton_deletion', 'index': len(deletions) - 1})
            boundaries.extend((boundary('singleton_substitutions', deletion['after_substitutions'], active),
                               boundary('strict_destabilization', deletion['after_deletion'], deletion['basis_after']),
                               boundary('cyclic_cleanup', deletion['after'], deletion['basis_after'])))
            current, active = deletion['after'], deletion['basis_after']
        else:
            if len(active) >= rank_limit:
                stop = 'rank_limit'
                break
            if used >= candidate_limit:
                stop = 'candidate_limit'
                break
            result = find_compression(current, active, candidate_limit - used)
            used += result['defining_word_candidates']
            rounds.append({'before': list(current), 'basis_before': list(active), **result})
            events.append({'kind': 'compression_round', 'index': len(rounds) - 1})
            witness = result['best']
            if witness is None:
                stop = 'no_strict_literal_gain' if result['definition_screen_complete'] else 'candidate_limit'
                break
            oriented = [word[cut:] + word[:cut] for word, cut in zip(current, witness['cuts'])]
            definition = witness['helper'].upper() + witness['defining_word']
            boundaries.extend((boundary('cyclic_orientations', oriented, active),
                               boundary('defining_relator_added', [definition, *oriented], witness['basis_after']),
                               boundary('literal_compression', witness['relators'], witness['basis_after'])))
            current, active = witness['relators'], witness['basis_after']
    return {'input': initial, 'input_basis': list(basis), 'input_rank': len(basis),
            'input_length': sum(map(len, initial)), 'final_relators': current,
            'final_basis': active, 'final_rank': len(active), 'final_length': sum(map(len, current)),
            'strict_gain_from_audited_seed': sum(map(len, current)) < sum(map(len, initial)),
            'additional_length_gain': sum(map(len, initial)) - sum(map(len, current)),
            'defining_word_candidates': used, 'candidate_limit': candidate_limit, 'rank_limit': rank_limit,
            'rounds': rounds, 'singleton_deletions': deletions, 'events': events, 'boundaries': boundaries,
            'stop_reason': stop, 'solved': False,
            'terminal_basis_candidate': len({word.lower() for word in current if len(word) == 1}) == len(active),
            'ordinary_suffix_moves': sum(len(d['ordinary_moves']) + len(d['cyclic_cleanup_moves']) for d in deletions),
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'certificate_kind': 'theorem_backed_recursive_stable_prefix_pending_independent_audit'}
