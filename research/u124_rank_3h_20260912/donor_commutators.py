"""Abelianization-preserving donor surgery, with exact normal products."""
from __future__ import annotations

import completion
from completion import search
import whitehead


def contexts(words):
    letters = sorted({abs(x) for word in words for x in word})
    seen = set()
    for letter in letters:
        for word in ((letter,), (-letter,)):
            seen.add(word)
            yield word
    for source in sorted(words, key=lambda w: (len(w), w)):
        for signed in (source, search.inverse(source)):
            for cut in range(2, len(signed)):
                word = signed[:cut]
                if word not in seen:
                    seen.add(word)
                    yield word


def replacement(words, target, donor, sign, conjugator):
    factors = [{'donor_index': donor, 'sign': -sign, 'conjugator': ()},
               {'donor_index': donor, 'sign': sign, 'conjugator': conjugator}]
    raw = words[target]
    for factor in factors:
        signed = words[donor] if factor['sign'] == 1 else search.inverse(words[donor])
        c = factor['conjugator']
        raw = search.reduced(raw + search.inverse(c) + signed + c)
    after = search.normalize(words[:target] + (raw,) + words[target + 1:])
    event = {'kind': 'normal_product_substitution', 'before': words, 'target': target,
             'raw_target_after': raw, 'factors': factors, 'after': after,
             'macro': 'retained_donor_commutator', 'commutator_sign': sign,
             'commutator_conjugator': conjugator}
    return after, event


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    used, candidates, seen = 0, [], {words}
    construction_budget = min(remaining, max(12, remaining // 3))
    for conjugator in contexts(words):
        for target in range(len(words)):
            for donor in range(len(words)):
                if donor == target:
                    continue
                for sign in (1, -1):
                    if used == construction_budget:
                        break
                    used += 1
                    after, event = replacement(words, target, donor, sign, conjugator)
                    if after not in seen:
                        seen.add(after)
                        candidates.append((after, [event]))
                if used == construction_budget:
                    break
            if used == construction_budget:
                break
        if used == construction_budget:
            break
    candidates.sort(key=lambda row: (search.length(row[0]), row[0]))
    out = list(candidates)
    for after, events in candidates:
        if used == remaining:
            break
        endpoint, suffix, cost, _ = whitehead.descend(after, min(32, remaining - used))
        used += cost
        if suffix:
            out.append((endpoint, events + suffix))
    return out, used
