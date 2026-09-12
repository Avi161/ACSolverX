"""Short consequences of retained donors, with explicit normal products."""
from __future__ import annotations

from collections import deque
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rank_unbounded_20260912'))
import lemma11
import search


def inverted(factors):
    return [{'donor_index': f['donor_index'], 'sign': -f['sign'], 'conjugator': f['conjugator']}
            for f in reversed(factors)]


def conjugated(factors, word):
    return [{'donor_index': f['donor_index'], 'sign': f['sign'],
             'conjugator': search.reduced(tuple(f['conjugator']) + word)} for f in factors]


def canonical_consequence(word, factors):
    after, witness = lemma11.canonical_witness(word)
    factors = factors if witness['sign'] == 1 else inverted(factors)
    return after, conjugated(factors, witness['conjugator'])


def orientations(word, factors):
    for sign in (1, -1):
        base = word if sign == 1 else search.inverse(word)
        proof = factors if sign == 1 else inverted(factors)
        for cut in range(len(base)):
            yield base[cut:] + base[:cut], conjugated(proof, base[:cut])


def library(words, target, allowance):
    known, queue, seeds = {}, deque(), []
    for i, word in enumerate(words):
        if i == target or not word:
            continue
        factors = [{'donor_index': i, 'sign': 1, 'conjugator': ()}]
        known[word] = factors
        queue.append(word)
        seeds.extend(orientations(word, factors))
    used = 0
    while queue and used < allowance:
        word = queue.popleft()
        for left, left_factors in orientations(word, known[word]):
            for right, right_factors in seeds:
                if left == right or left[0] != right[0]:
                    continue
                if used == allowance:
                    return known, used
                used += 1
                consequence, factors = canonical_consequence(search.inverse(left) + right,
                                                             inverted(left_factors) + right_factors)
                if not consequence or consequence in known:
                    continue
                known[consequence] = factors
                queue.append(consequence)
    return known, used


def apply_library(words, target_index, consequences, allowance):
    target = words[target_index]
    rules = {}
    for word, factors in consequences.items():
        for oriented, proof in orientations(word, factors):
            for size in range((len(word) + 1) // 2, len(word) + 1):
                left, right = oriented[:size], search.inverse(oriented[size:])
                rules.setdefault(left[0], []).append((len(right) - len(left), left, right, proof))
    for first in rules:
        rules[first].sort(key=lambda r: (r[0], len(r[3]), r[1], r[2]))
    used, seen, candidates = 0, set(), []
    for cut in range(len(target)):
        prefix, oriented = target[:cut], target[cut:] + target[:cut]
        for _, left, right, proof in rules.get(oriented[0], ()):
            if oriented[:len(left)] != left:
                continue
            if used == allowance:
                return candidates, used
            used += 1
            suffix = oriented[len(left):]
            correction = conjugated(inverted(proof), search.reduced(left + suffix + search.inverse(prefix)))
            raw_target = search.reduced(prefix + right + suffix + search.inverse(prefix))
            replay = target
            for factor in correction:
                donor = words[factor['donor_index']]
                if factor['sign'] == -1:
                    donor = search.inverse(donor)
                c = factor['conjugator']
                replay = search.reduced(replay + search.inverse(c) + donor + c)
            if replay != raw_target:
                raise AssertionError('derived consequence correction failed')
            after = search.normalize(words[:target_index] + (raw_target,) + words[target_index + 1:])
            if after == words or after in seen:
                continue
            seen.add(after)
            event = {'kind': 'normal_product_substitution', 'before': words, 'target': target_index,
                     'raw_target_after': raw_target, 'factors': correction, 'after': after,
                     'derived_rule': {'left': left, 'right': right, 'normal_product_width': len(proof)}}
            candidates.append((after, [event]))
    return candidates, used


def probe(words, remaining):
    candidates, charged = [], 0
    order = sorted(range(len(words)), key=lambda i: (-len(words[i]), i))
    for position, target in enumerate(order):
        allowance = (remaining - charged) // (len(order) - position)
        consequences, cost = library(words, target, allowance // 2)
        charged += cost
        out, cost = apply_library(words, target, consequences, allowance - cost)
        charged += cost
        candidates.extend(out)
    return candidates, charged
