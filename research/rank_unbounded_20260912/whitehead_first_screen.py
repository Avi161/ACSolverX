"""Whole-tuple Whitehead descent using minimum cuts on signed-letter graphs."""
from collections import Counter, deque

from search import canonical, inverse, length, normalize, reduced


def graph(words):
    edges = Counter()
    for word in words:
        for i, x in enumerate(word):
            y = -word[(i + 1) % len(word)]
            if x == y:
                raise ValueError('input must be cyclically reduced')
            edges[tuple(sorted((x, y)))] += 1
    return edges


def cut_value(edges, side):
    return sum(n for (x, y), n in edges.items() if (x in side) != (y in side))


def minimum_cut(edges, source):
    vertices = sorted({v for edge in edges for v in edge})
    sink = -source
    residual = {v: {} for v in vertices}
    for (x, y), n in edges.items():
        residual[x][y] = residual[y][x] = n
    while True:
        parents = {source: None}
        queue = deque([source])
        while queue and sink not in parents:
            x = queue.popleft()
            for y, n in residual[x].items():
                if n > 0 and y not in parents:
                    parents[y] = x
                    queue.append(y)
        if sink not in parents:
            side = set(parents)
            return cut_value(edges, side), side
        x, capacity = sink, float('inf')
        while parents[x] is not None:
            capacity = min(capacity, residual[parents[x]][x])
            x = parents[x]
        x = sink
        while parents[x] is not None:
            y = parents[x]
            residual[y][x] -= capacity
            residual[x][y] = residual[x].get(y, 0) + capacity
            x = y


def images(basis, multiplier, side):
    if multiplier not in side or -multiplier in side:
        raise ValueError('invalid Whitehead partition')
    out = {}
    for x in basis:
        if x == abs(multiplier):
            out[x] = (x,)
        else:
            out[x] = ((-multiplier,) if -x in side else ()) + (x,) + ((multiplier,) if x in side else ())
    return out


def apply(word, mapping):
    return reduced(tuple(y for x in word for y in (mapping[x] if x > 0 else inverse(mapping[-x]))))


def transform(words, multiplier, side):
    basis = sorted({abs(x) for w in words for x in w})
    forward = images(basis, multiplier, side)
    backward = images(basis, -multiplier, (set(side) - {multiplier}) | {-multiplier})
    for x in basis:
        if apply(forward[x], backward) != (x,) or apply(backward[x], forward) != (x,):
            raise AssertionError('Whitehead inverse does not replay')
    raw = tuple(apply(w, forward) for w in words)
    after = normalize(raw)
    return after, {'kind': 'ambient_whitehead', 'before': words, 'multiplier': multiplier,
                   'side': sorted(side), 'images': forward, 'inverse_images': backward,
                   'raw_after': raw, 'after': after}


def descend(words, available):
    current, path, cuts = normalize(words), [], 0
    complete = False
    while cuts < available:
        edges = graph(current)
        vertices = sorted({v for edge in edges for v in edge})
        candidates = []
        if not vertices:
            complete = True
            break
        for a in vertices:
            if cuts == available:
                break
            capacity, side = minimum_cut(edges, a)
            cuts += 1
            degree = sum(n for edge, n in edges.items() if a in edge)
            if capacity < degree:
                candidates.append((capacity - degree, a, side))
        if not candidates:
            complete = cuts < available or len(vertices) <= cuts and a == vertices[-1]
            break
        delta, a, side = min(candidates, key=lambda x: (x[0], x[1], sorted(x[2])))
        after, event = transform(current, a, side)
        if length(after) - length(current) != delta:
            raise AssertionError('Whitehead cut formula differs from word replay')
        event['length_change'] = delta
        path.append(event)
        current = after
    return current, path, cuts, complete
