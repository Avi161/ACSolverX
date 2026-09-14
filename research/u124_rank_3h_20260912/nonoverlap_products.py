"""Noncancelling AC products followed by exact whole-tuple Whitehead scoring."""
from collections import deque
from itertools import product

from exchange_collect_aliases import score
import rank_peeling
from rank_peeling import search
import whitehead


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    families = deque()
    for donor in sorted(range(len(words)), key=lambda j: (len(words[j]), j)):
        for target in range(len(words)):
            if target != donor:
                for sign in (1, -1):
                    families.append((target, donor, sign,
                                     iter(product(range(len(words[target])), range(len(words[donor]))))))
    charged, seen, selected = 0, {words}, []
    reserve = min(256, remaining // 3)
    while families and charged < remaining - reserve:
        target, donor, sign, cuts = families.popleft()
        cut = next(cuts, None)
        if cut is None:
            continue
        families.append((target, donor, sign, cuts))
        charged += 1
        left, right = words[target], words[donor] if sign == 1 else search.inverse(words[donor])
        k, l = cut
        product_word = search.reduced(left[k:] + left[:k] + right[l:] + right[:l])
        if len(search.canonical(product_word)) != len(left) + len(right):
            continue
        conjugator = search.reduced(right[:l] + search.inverse(left[:k]))
        raw_target = search.reduced(left + search.inverse(conjugator) + right + conjugator)
        if search.canonical(raw_target) != search.canonical(product_word):
            raise AssertionError('transported product differs from its rotation pair')
        raw = words[:target] + (raw_target,) + words[target + 1:]
        after = search.normalize(raw)
        if after in seen:
            continue
        seen.add(after)
        event = {'kind': 'normal_product_substitution', 'before': words, 'target': target,
                 'raw_target_after': raw_target,
                 'factors': [{'donor_index': donor, 'sign': sign, 'conjugator': conjugator}],
                 'after': after}
        cuts_needed = 2 * len({abs(x) for word in after for x in word})
        if charged + cuts_needed > remaining - reserve:
            break
        endpoint, tail, used, _ = score(after)
        charged += used
        selected.append((endpoint, [event] + tail))
    selected.sort(key=lambda row: (search.length(row[0]), row[0]))
    out = list(selected)
    for state, prefix in selected:
        if charged == remaining:
            break
        after, tail, used, _ = whitehead.descend(state, min(32, remaining - charged))
        charged += used
        after, peel, used, _ = rank_peeling.descend(after, min(24, remaining - charged))
        charged += used
        out.append((after, prefix + tail + peel))
    return out, charged
