"""Exact one-word subgroup-complement test using folded finite graphs."""

from collections import deque
from itertools import combinations

from .ac_words import inv, red


def folded(edges, count, identify=None):
    parent = list(range(count))

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(a, b):
        a, b = find(a), find(b)
        if a == b:
            return False
        parent[max(a, b)] = min(a, b)
        return True

    if identify is not None:
        union(*identify)
    while True:
        lookup = {}
        changed = False
        for u, letter, v in edges:
            key, v = (find(u), letter), find(v)
            if key in lookup:
                changed |= union(lookup[key], v)
            else:
                lookup[key] = v
        if not changed:
            break
    edges = {(find(u), letter, find(v)) for u, letter, v in edges}
    root = find(0)
    transition = {(u, letter): v for u, letter, v in edges}
    names, queue = {root: 0}, deque([root])
    while queue:
        u = queue.popleft()
        for letter in 'xXyY':
            v = transition.get((u, letter))
            if v is not None and v not in names:
                names[v] = len(names)
                queue.append(v)
    return tuple(sorted((names[u], letter, names[v]) for u, letter, v in edges))


def graph(words):
    edges, count = [], 1
    for word in map(red, words):
        u = 0
        for i, letter in enumerate(word):
            v = 0 if i + 1 == len(word) else count
            if v:
                count += 1
            edges.extend(((u, letter, v), (v, letter.swapcase(), u)))
            u = v
    return folded(edges, count)


def vertices(g):
    return {0} | {v for u, _, w in g for v in (u, w)}


def full_rose(g):
    return g == tuple(sorted((0, letter, 0) for letter in 'xXyY'))


def paths(g):
    transition = {(u, letter): v for u, letter, v in g}
    words, queue = {0: ''}, deque([0])
    while queue:
        u = queue.popleft()
        for letter in 'xXyY':
            v = transition.get((u, letter))
            if v is not None and v not in words:
                words[v] = words[u] + letter
                queue.append(v)
    return words


def analyze(words, *, max_pairs=1000):
    g = graph(words)
    if full_rose(g):
        return {'status': 'already_generates', 'complement': '', 'graph': g,
                'pairs_checked': 0, 'complete': True}
    verts = vertices(g)
    if len(verts) == 1:
        missing = [c for c in 'xy' if (0, c, 0) not in g]
        if len(missing) == 1:
            return {'status': 'cyclic_complement', 'complement': missing[0], 'graph': g,
                    'pairs_checked': 0, 'complete': True}
        return {'status': 'no_cyclic_complement', 'graph': g, 'pairs_checked': 0, 'complete': True}
    root_paths = paths(g)
    checked = 0
    for pair in combinations(sorted(verts), 2):
        if checked == max_pairs:
            return {'status': 'unknown_pair_cap', 'graph': g, 'pairs_checked': checked, 'complete': False}
        child = folded(g, len(verts), pair)
        checked += 1
        if full_rose(child):
            u, v = pair
            complement = red(root_paths[u] + inv(root_paths[v]))
            if not full_rose(graph([*words, complement])):
                raise AssertionError('independent appended-loop witness failed')
            return {'status': 'cyclic_complement', 'complement': complement, 'identified': pair,
                    'graph': g, 'pairs_checked': checked, 'complete': True}
    return {'status': 'no_cyclic_complement', 'graph': g,
            'pairs_checked': checked, 'complete': True}
