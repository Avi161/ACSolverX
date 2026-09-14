"""Dynamic-rank AC search: ordinary products plus digram definitions and eliminations.

A *state* is a balanced presentation ``(R_1, ..., R_n)`` of the trivial group on
generators ``1..n``.  Letters are nonzero signed integers; each relator is a
cyclic word kept in canonical form (free + cyclic reduction, then the minimum
over all rotations of the word and its inverse); the tuple is sorted.

Three kinds of move are generated from a state:

``product``     ``R_i <- rot(R_i) . rot(R_j^s)``  (ordinary AC move, rank unchanged;
                the conjugator is a prefix of ``R_i`` times a prefix of ``R_j``).
``define``      choose a cyclic digram ``d = (a, b)`` that occurs at least twice
                (either sign) across the relators, add generator ``h = n + 1`` with
                defining relator ``h^-1 a b`` and replace occurrences of ``d`` by
                ``h`` and of ``d^-1`` by ``h^-1`` (shortest tokenisation per
                relator over its rotations).  Rank ``n -> n + 1``.  This is a
                stabilisation followed by the automorphism ``h -> h (ab)^-1``.
``eliminate``   choose a relator ``R_i`` and a generator ``g`` occurring exactly
                once in it; rotate so ``R_i = g^e u``; substitute ``g -> u^-1``
                (``e = +1``) or ``g -> u`` (``e = -1``) in every other relator,
                delete ``R_i`` and renumber generators above ``g``.  Rank
                ``n -> n - 1``.  A unit relator ``g`` is the special case ``u``
                empty, so reaching the *empty* presentation (rank 0) is the solved
                condition.

For presentations of the trivial group, ``define`` and ``eliminate`` are stable
AC composites (a stabilisation or destabilisation together with ordinary AC moves
whose existence follows from ``w in <<R>>``; Lemma 11 of Shehper et al.,
arXiv:2408.15332, as used in ``research/u124_rank_3h_20260912``).  They are NOT
expanded into elementary moves here.  ``product`` moves are elementary.  A path
to the empty presentation therefore witnesses *stable* AC-triviality of the root,
with the number of stabilisations bounded by the number of ``define`` events.

Optionally states are also canonicalised under permutations of the generators
(``relabel=True``); renaming is a pure symmetry of the move set and is recorded
in the certificate so a replayer can follow it exactly.

Two drivers are provided: a best-first search (``best_first``) with a pop budget,
and an exhaustive closure (``closure``) of everything reachable under a per-relator
length cap and a total-length ceiling, which either finds the empty presentation,
enumerates the whole finite component (``closed``) or hits the state budget.
"""
from __future__ import annotations

import heapq
import itertools
import time
from collections import Counter


# ----------------------------------------------------------------------------
# words
# ----------------------------------------------------------------------------

def inverse(word):
    return tuple(-x for x in reversed(word))


def reduce(word):
    out = []
    for x in word:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def cyclic_reduce(word):
    word = reduce(word)
    while len(word) > 1 and word[0] == -word[-1]:
        word = word[1:-1]
    return word


def canonical(word):
    word = cyclic_reduce(word)
    if not word:
        return ()
    best = None
    for w in (word, inverse(word)):
        for k in range(len(w)):
            r = w[k:] + w[:k]
            if best is None or r < best:
                best = r
    return best


def normalize(words):
    return tuple(sorted(canonical(w) for w in words))


def total_length(words):
    return sum(len(w) for w in words)


def parse(text, letters='xyzuvwabcdefghijklmnopqrst'):
    """'YXYxyx' -> (-2, -1, -2, 1, 2, 1): lowercase = generator, uppercase = inverse."""
    out = []
    for c in text:
        i = letters.index(c.lower()) + 1
        out.append(i if c.islower() else -i)
    return tuple(out)


def render(word, letters='xyzuvwabcdefghijklmnopqrst'):
    return ''.join(letters[abs(x) - 1] if x > 0 else letters[abs(x) - 1].upper() for x in word) or '1'


def render_state(words):
    return [render(w) for w in words]


# ----------------------------------------------------------------------------
# renaming symmetry
# ----------------------------------------------------------------------------

def apply_relabel(words, perm, signs):
    """perm[g] = new label of generator g (1-based dict); signs[g] in {+1,-1}."""
    out = []
    for w in words:
        out.append(tuple((perm[abs(x)] * signs[abs(x)]) * (1 if x > 0 else -1) for x in w))
    return normalize(out)


def _refine(words, n, colour):
    """Canonical colour refinement on generators (adjacency in cyclic words, unsigned).

    ``colour`` maps generator -> int; returns a refined map with ints 0..k-1 such
    that the map depends only on the coloured presentation up to renaming.
    """
    while True:
        nbr = {g: [] for g in range(1, n + 1)}
        for w in words:
            m = len(w)
            if m < 2:
                continue
            for k in range(m):
                a, b = abs(w[k]), abs(w[(k + 1) % m])
                nbr[a].append(colour[b])
                nbr[b].append(colour[a])
        sig = {g: (colour[g], tuple(sorted(nbr[g]))) for g in range(1, n + 1)}
        order = sorted(set(sig.values()))
        index = {v: i for i, v in enumerate(order)}
        new = {g: index[sig[g]] for g in range(1, n + 1)}
        if len(order) == len(set(colour.values())):
            return new
        colour = new


def _initial_colour(words, n):
    base = {}
    for g in range(1, n + 1):
        rows = tuple(sorted((len(w), sum(abs(x) == g for x in w)) for w in words if any(abs(x) == g for x in w)))
        base[g] = (sum(abs(x) == g for w in words for x in w), rows)
    order = sorted(set(base.values()))
    index = {v: i for i, v in enumerate(order)}
    return {g: index[base[g]] for g in range(1, n + 1)}


def relabel_canonical(words, limit=20000):
    """Minimum of ``normalize`` over *permutations* of the generators.

    Individualisation-refinement: generators are coloured by an invariant
    refinement (sign-blind adjacency in the cyclic words); while some colour
    class has more than one member, each member of the first such class is
    individualised in turn and the search recurses.  At a discrete colouring the
    permutation is fixed by colour order.  The result is the minimum over all
    leaves, hence invariant under renaming the generators.  Inverting a
    generator is *not* quotiented (a relator's canonical form may be its own
    inverse, so no cheap sign rule is invariant); states that differ only by
    inverting some generators are therefore kept as distinct states, which is
    sound and merely repeats work.  ``limit`` bounds the leaves visited and
    raises ``RuntimeError`` if exceeded.
    """
    n = len(words)
    if n == 0:
        return (), {}, {}
    if any(abs(x) > n or x == 0 for w in words for x in w):
        raise ValueError('letters must lie in 1..rank')
    signs = {g: 1 for g in range(1, n + 1)}
    best = [None, None, 0]

    def leaf(colour):
        perm = {g: colour[g] + 1 for g in colour}
        cand = apply_relabel(words, perm, signs)
        best[2] += 1
        if best[2] > limit:
            raise RuntimeError('relabel_canonical leaf limit exceeded')
        if best[0] is None or cand < best[0]:
            best[0], best[1] = cand, perm

    def search(colour):
        colour = _refine(words, n, colour)
        classes = {}
        for g, c in colour.items():
            classes.setdefault(c, []).append(g)
        multi = [c for c in sorted(classes) if len(classes[c]) > 1]
        if not multi:
            leaf(colour)
            return
        c = multi[0]
        for g in classes[c]:
            new = {}
            for h, ch in colour.items():
                new[h] = 2 * ch + (1 if (ch == c and h != g) else 0)
            search(new)

    search(_initial_colour(words, n))
    return best[0], best[1], dict(signs)


# ----------------------------------------------------------------------------
# moves
# ----------------------------------------------------------------------------

def products(words, cap):
    """All ordinary rotation products; yields (child_raw_tuple, event)."""
    n = len(words)
    seen = {}
    for i in range(n):
        target = words[i]
        if not target:
            continue
        for j in range(n):
            if i == j or not words[j]:
                continue
            for sign in (1, -1):
                base = words[j] if sign == 1 else inverse(words[j])
                for k1 in range(len(target)):
                    left = target[k1:] + target[:k1]
                    for k2 in range(len(base)):
                        product = canonical(left + base[k2:] + base[:k2])
                        if not product or product == target or len(product) > cap:
                            continue
                        raw = words[:i] + (product,) + words[i + 1:]
                        key = normalize(raw)
                        if key not in seen:
                            seen[key] = {'kind': 'product', 'i': i, 'j': j, 'sign': sign,
                                         'k1': k1, 'k2': k2, 'result': product}
    return list(seen.items())


def digram_counts(words):
    counts = Counter()
    for w in words:
        m = len(w)
        if m < 2:
            continue
        for k in range(m):
            d = (w[k], w[(k + 1) % m])
            counts[min(d, inverse(d))] += 1
    return counts


def tokenize(word, d, h):
    """Shortest rewriting of a linear word replacing d by h and d^-1 by -h."""
    dinv = inverse(d)
    m = len(word)
    best = [None] * (m + 1)
    best[m] = ()
    for i in range(m - 1, -1, -1):
        cands = [(word[i],) + best[i + 1]]
        if i + 1 < m:
            block = word[i:i + 2]
            if block == d:
                cands.append((h,) + best[i + 2])
            if block == dinv:
                cands.append((-h,) + best[i + 2])
        best[i] = min(cands, key=lambda t: (len(t), t))
    return best[0]


def define(words, d):
    """Add generator h = n+1 with relator h^-1 d and rewrite every relator."""
    n = len(words)
    h = n + 1
    templates = []
    for w in words:
        if len(w) < 2:
            templates.append(w)
            continue
        choices = [tokenize(w[k:] + w[:k], d, h) for k in range(len(w))]
        templates.append(min(choices, key=lambda t: (len(t), t)))
    raw = ((-h,) + d,) + tuple(templates)
    uses = sum(abs(x) == h for t in templates for x in t)
    return raw, {'kind': 'define', 'digram': d, 'h': h, 'uses': uses, 'templates': templates}


def defines(words, min_uses=2):
    out = []
    for d, count in digram_counts(words).items():
        if count < min_uses:
            continue
        raw, event = define(words, d)
        if event['uses'] < min_uses:
            continue
        out.append((normalize(raw), event))
    return out


def triangulate(words, min_uses=2):
    """Greedy digram definitions until every relator has length <= 3.

    Returns (root, steps): ``steps`` are certificate steps (event, relabel=None,
    after) so a search from the triangulated root can be replayed from the
    rank-two root.  At each round the most frequent cyclic digram (ties: the
    smallest) among relators longer than three is defined; the triangle excess
    ``sum(max(0, |r| - 3))`` strictly decreases, so the loop terminates.
    """
    current = normalize(words)
    steps = []
    while any(len(w) > 3 for w in current):
        counts = Counter()
        for w in current:
            if len(w) <= 3:
                continue
            m = len(w)
            for k in range(m):
                d = (w[k], w[(k + 1) % m])
                counts[min(d, inverse(d))] += 1
        total = digram_counts(current)
        d = min(counts, key=lambda d: (-total[d], -counts[d], d))
        raw, event = define(current, d)
        after = normalize(raw)
        if sum(max(0, len(w) - 3) for w in after) >= sum(max(0, len(w) - 3) for w in current):
            raise AssertionError('triangle excess did not decrease')
        steps.append({'event': event, 'relabel': None, 'after': after})
        current = after
    return current, steps


def substitute(word, g, image):
    out = []
    inv_image = inverse(image)
    for x in word:
        if x == g:
            out.extend(image)
        elif x == -g:
            out.extend(inv_image)
        else:
            out.append(x)
    return reduce(tuple(out))


def renumber(word, g):
    return tuple((abs(x) - 1 if abs(x) > g else abs(x)) * (1 if x > 0 else -1) for x in word)


def eliminate(words, i, g):
    """Eliminate generator g using relator i, in which g occurs exactly once."""
    r = words[i]
    occ = [k for k, x in enumerate(r) if abs(x) == g]
    if len(occ) != 1:
        raise ValueError('generator must occur exactly once in the relator')
    k = occ[0]
    rot = r[k:] + r[:k]              # rot = g^e u
    e = 1 if rot[0] > 0 else -1
    u = rot[1:]
    image = inverse(u) if e == 1 else u   # g = image
    rest = [substitute(w, g, image) for idx, w in enumerate(words) if idx != i]
    raw = tuple(renumber(w, g) for w in rest)
    return raw, {'kind': 'eliminate', 'i': i, 'g': g, 'image': image}


def eliminations(words, units_only=False):
    out = []
    for i, r in enumerate(words):
        if units_only and len(r) != 1:
            continue
        counts = Counter(abs(x) for x in r)
        for g, c in counts.items():
            if c == 1:
                raw, event = eliminate(words, i, g)
                out.append((normalize(raw), event))
    return out


def children(words, *, cap, ceiling, allow_define=True, allow_eliminate=True,
             elim_cap=None, min_uses=2, elim_units_only=False):
    """Every admissible child: (normalized_child, event).

    The per-relator ``cap`` bounds relators a move *creates*: the product result,
    and the substituted relators of an elimination (``elim_cap`` if given).  A
    definition never lengthens a relator, so it is bounded only by ``ceiling``
    (total length).  Relators inherited unchanged from the root may exceed ``cap``.
    """
    out = []
    for key, event in products(words, cap):
        if total_length(key) <= ceiling:
            out.append((key, event))
    if allow_define:
        for key, event in defines(words, min_uses):
            if total_length(key) <= ceiling:
                out.append((key, event))
    if allow_eliminate:
        ecap = cap if elim_cap is None else elim_cap
        for key, event in eliminations(words, elim_units_only):
            if total_length(key) <= ceiling and max(map(len, key), default=0) <= ecap:
                out.append((key, event))
    return out


# ----------------------------------------------------------------------------
# state keys
# ----------------------------------------------------------------------------

def make_key(words, relabel):
    if relabel:
        canon, perm, signs = relabel_canonical(words)
        return canon, {'perm': perm, 'signs': signs}
    return words, None


# ----------------------------------------------------------------------------
# drivers
# ----------------------------------------------------------------------------

def priority_length(words):
    return (total_length(words), max(map(len, words), default=0), len(words))


def priority_length_rank(words):
    return (total_length(words) + len(words), max(map(len, words), default=0))


PRIORITIES = {'length': priority_length, 'length_rank': priority_length_rank}


def best_first(root, *, cap, ceiling, pops, allow_define=True, allow_eliminate=True,
               priority='length', relabel=False, elim_cap=None, min_uses=2,
               max_states=2_000_000, elim_units_only=False, closed_set='hash'):
    """Best-first search from ``root``; solved when the empty presentation is reached.

    ``closed_set='sorted'`` keeps the visited states in a sorted list searched by
    bisection (comparison only, no hashing); the search is otherwise identical."""
    import bisect
    t0 = time.process_time()
    root = normalize(root)
    key, relabel_event = make_key(root, relabel)
    prio = PRIORITIES[priority]
    records = [{'words': key, 'parent': None, 'event': None, 'relabel': relabel_event}]
    if closed_set == 'sorted':
        seen_sorted = [key]
    elif closed_set == 'hash':
        seen = {key: 0}
    else:
        raise ValueError(closed_set)
    heap = [(prio(key), 0)]
    popped = generated = 0
    solved = None
    best_len = total_length(key)
    best_idx = 0
    max_rank = len(key)
    if len(key) == 0:
        solved = 0
    while heap and popped < pops and solved is None and len(records) < max_states:
        _, index = heapq.heappop(heap)
        words = records[index]['words']
        popped += 1
        for child_words, event in children(words, cap=cap, ceiling=ceiling,
                                           allow_define=allow_define,
                                           allow_eliminate=allow_eliminate,
                                           elim_cap=elim_cap, min_uses=min_uses,
                                           elim_units_only=elim_units_only):
            generated += 1
            ckey, rl = make_key(child_words, relabel)
            if closed_set == 'sorted':
                pos = bisect.bisect_left(seen_sorted, ckey)
                if pos < len(seen_sorted) and seen_sorted[pos] == ckey:
                    continue
                seen_sorted.insert(pos, ckey)
            else:
                if ckey in seen:
                    continue
                seen[ckey] = len(records)
            records.append({'words': ckey, 'parent': index, 'event': event, 'relabel': rl})
            child = len(records) - 1
            if total_length(ckey) < best_len:
                best_len, best_idx = total_length(ckey), child
            max_rank = max(max_rank, len(ckey))
            if len(ckey) == 0:
                solved = child
                break
            heapq.heappush(heap, (prio(ckey), child))

    def path_to(target):
        out = []
        idx = target
        while records[idx]['parent'] is not None:
            rec = records[idx]
            out.append({'event': rec['event'], 'relabel': rec['relabel'], 'after': rec['words']})
            idx = rec['parent']
        out.reverse()
        return out

    path = path_to(solved) if solved is not None else None
    return {'root': root, 'root_relabel': relabel_event, 'root_key': key,
            'solved': solved is not None, 'pops': popped, 'generated': generated,
            'states': len(records), 'min_total_length': best_len, 'max_rank': max_rank,
            'min_state': records[best_idx]['words'], 'min_path': path_to(best_idx),
            'path_length': len(path) if path is not None else None, 'path': path,
            'cpu_seconds': time.process_time() - t0,
            'params': {'cap': cap, 'ceiling': ceiling, 'pops': pops, 'allow_define': allow_define,
                       'allow_eliminate': allow_eliminate, 'priority': priority, 'relabel': relabel,
                       'elim_cap': elim_cap, 'min_uses': min_uses, 'elim_units_only': elim_units_only,
                       'closed_set': closed_set}}


def closure(root, *, cap, ceiling, max_states, allow_define=True, allow_eliminate=True,
            relabel=True, elim_cap=None, min_uses=2, stop_when_solved=True, elim_units_only=False):
    """Exhaustive BFS of the component under the cap and ceiling."""
    t0 = time.process_time()
    root = normalize(root)
    key, relabel_event = make_key(root, relabel)
    records = [{'words': key, 'parent': None, 'event': None, 'relabel': relabel_event}]
    seen = {key: 0}
    queue = [0]
    head = 0
    solved = 0 if len(key) == 0 else None
    generated = 0
    budget_hit = False
    max_rank = len(key)
    while head < len(queue) and (solved is None or not stop_when_solved):
        index = queue[head]
        head += 1
        words = records[index]['words']
        for child_words, event in children(words, cap=cap, ceiling=ceiling,
                                           allow_define=allow_define,
                                           allow_eliminate=allow_eliminate,
                                           elim_cap=elim_cap, min_uses=min_uses,
                                           elim_units_only=elim_units_only):
            generated += 1
            ckey, rl = make_key(child_words, relabel)
            if ckey in seen:
                continue
            if len(records) >= max_states:
                budget_hit = True
                break
            seen[ckey] = len(records)
            records.append({'words': ckey, 'parent': index, 'event': event, 'relabel': rl})
            max_rank = max(max_rank, len(ckey))
            if len(ckey) == 0 and solved is None:
                solved = len(records) - 1
                if stop_when_solved:
                    break
            queue.append(len(records) - 1)
        if budget_hit:
            break
    closed = (not budget_hit) and head >= len(queue) and solved is None
    path = None
    if solved is not None:
        path = []
        idx = solved
        while records[idx]['parent'] is not None:
            rec = records[idx]
            path.append({'event': rec['event'], 'relabel': rec['relabel'], 'after': rec['words']})
            idx = rec['parent']
        path.reverse()
    return {'root': root, 'root_relabel': relabel_event, 'root_key': key,
            'solved': solved is not None, 'closed': closed, 'budget_hit': budget_hit,
            'states': len(records), 'popped': head, 'generated': generated, 'max_rank': max_rank,
            'path_length': len(path) if path is not None else None, 'path': path,
            'cpu_seconds': time.process_time() - t0,
            'params': {'cap': cap, 'ceiling': ceiling, 'max_states': max_states,
                       'allow_define': allow_define, 'allow_eliminate': allow_eliminate,
                       'relabel': relabel, 'elim_cap': elim_cap, 'min_uses': min_uses,
                       'elim_units_only': elim_units_only}}


def json_relabel(rl):
    if rl is None:
        return None
    return {'perm': {str(k): v for k, v in rl['perm'].items()},
            'signs': {str(k): v for k, v in rl['signs'].items()}}


def json_path(path):
    """Make a path JSON-serialisable (tuples -> lists, dict keys -> str)."""
    if path is None:
        return None
    out = []
    for step in path:
        ev = dict(step['event'])
        for k, v in list(ev.items()):
            if isinstance(v, tuple):
                ev[k] = list(v)
            elif isinstance(v, list):
                ev[k] = [list(t) if isinstance(t, tuple) else t for t in v]
        rl = json_relabel(step['relabel'])
        out.append({'event': ev, 'relabel': rl, 'after': [list(w) for w in step['after']]})
    return out
