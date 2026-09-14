"""Unified hash-free search over presentations of any rank.

One frontier, one budget, one comparison-sorted closed set.  Moves (all decided from
the current words; no pattern table):

  product     R_i <- rot(R_i) . rot(R_j^±1), result capped at `cap` letters
              (dynrank.products; an elementary AC move);
  define      a new generator for a cyclic digram occurring at least twice
              (dynrank.defines; rank + 1);
  eliminate   a generator occurring exactly once in some relator is substituted
              away (dynrank.eliminations; rank - 1);
  nielsen     the transvection x_i -> x_i x_j^±1 applied to every relator (an
              automorphism of the free group; at rank two these are the four
              Nielsen maps of hfcascade).

States are canonical up to cyclic rotation, inversion, relator order and (with
relabel=True) permutation of the generators (dynrank.relabel_canonical, an
individualisation-refinement canonical form, comparison-based).  The solve
condition is the empty presentation.  Certificate scope is that of
research/ac_dynamic_rank_20260913: products and Nielsen steps are elementary or
automorphism-transported AC moves; define/eliminate are stable AC composites
(Lemma 11 of arXiv:2408.15332) that are not expanded, so a certificate that uses
them proves stable AC-triviality of a trivial-group presentation.  A certificate
whose events are only products and Nielsen steps is an ordinary rank-two
certificate.
"""
from __future__ import annotations

import bisect
import heapq
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_dynamic_rank_20260913 import dynrank as D  # noqa: E402


def transvection(word, i, j, sign):
    """x_i -> x_i x_j^sign on one word, cyclically canonical."""
    out = []
    for x in word:
        if x == i:
            out.append(i)
            out.append(sign * j)
        elif x == -i:
            out.append(-sign * j)
            out.append(-i)
        else:
            out.append(x)
    return D.canonical(tuple(out))


def nielsen_children(words):
    n = len(words)
    out = []
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i == j:
                continue
            for sign in (1, -1):
                child = D.normalize(tuple(transvection(w, i, j, sign) for w in words))
                out.append((child, {'kind': 'nielsen', 'i': i, 'j': j, 'sign': sign}))
    return out


def search(root, *, pops, cap=8, slack=8, relabel=True, nielsen=True, allow_define=True,
           allow_eliminate=True, priority='length', closed_set='sorted', min_uses=2):
    """Best-first search from the rank-two root (a pair of int words); see the module doc."""
    t0 = time.process_time()
    root = D.normalize(root)
    ceiling = D.total_length(root) + slack
    key, relabel_event = D.make_key(root, relabel)
    prio = D.PRIORITIES[priority]
    records = [{'words': key, 'parent': None, 'event': None, 'relabel': relabel_event}]
    if closed_set == 'sorted':
        seen = [key]
    elif closed_set == 'hash':
        seen = {key}
    else:
        raise ValueError(closed_set)
    heap = [(prio(key), 0)]
    popped = generated = 0
    solved = 0 if len(key) == 0 else None
    max_rank = len(key)
    best_len, best_idx = D.total_length(key), 0
    while heap and popped < pops and solved is None:
        _, index = heapq.heappop(heap)
        words = records[index]['words']
        popped += 1
        edges = D.children(words, cap=cap, ceiling=ceiling, allow_define=allow_define,
                           allow_eliminate=allow_eliminate, min_uses=min_uses)
        if nielsen:
            edges = edges + [(c, e) for c, e in nielsen_children(words) if D.total_length(c) <= ceiling]
        for child_words, event in edges:
            generated += 1
            ckey, rl = D.make_key(child_words, relabel)
            if closed_set == 'sorted':
                pos = bisect.bisect_left(seen, ckey)
                if pos < len(seen) and seen[pos] == ckey:
                    continue
                seen.insert(pos, ckey)
            else:
                if ckey in seen:
                    continue
                seen.add(ckey)
            records.append({'words': ckey, 'parent': index, 'event': event, 'relabel': rl})
            child = len(records) - 1
            if D.total_length(ckey) < best_len:
                best_len, best_idx = D.total_length(ckey), child
            max_rank = max(max_rank, len(ckey))
            if len(ckey) == 0:
                solved = child
                break
            heapq.heappush(heap, (prio(ckey), child))
    path = None
    if solved is not None:
        path = []
        idx = solved
        while records[idx]['parent'] is not None:
            rec = records[idx]
            path.append({'event': rec['event'], 'relabel': rec['relabel'], 'after': rec['words']})
            idx = rec['parent']
        path.reverse()
    kinds = [s['event']['kind'] for s in path] if path else []
    return {'root': root, 'root_relabel': relabel_event, 'root_key': key, 'solved': solved is not None,
            'pops': popped, 'generated': generated, 'states': len(records), 'max_rank': max_rank,
            'min_total_length': best_len, 'path_length': len(path) if path else None, 'path': path,
            'defines': kinds.count('define'), 'eliminates': kinds.count('eliminate'),
            'products': kinds.count('product'), 'nielsens': kinds.count('nielsen'),
            'explicit_rank2': bool(path) and not any(k in ('define', 'eliminate') for k in kinds),
            'cpu_seconds': time.process_time() - t0,
            'params': {'cap': cap, 'slack': slack, 'pops': pops, 'relabel': relabel, 'nielsen': nielsen,
                       'allow_define': allow_define, 'allow_eliminate': allow_eliminate,
                       'priority': priority, 'closed_set': closed_set, 'min_uses': min_uses}}


def solve_pair(r1, r2, **kw):
    return search((D.parse(r1), D.parse(r2)), **kw)
