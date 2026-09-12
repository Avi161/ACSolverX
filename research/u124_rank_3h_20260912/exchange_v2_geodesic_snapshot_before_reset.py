"""Finite weighted free-reduction saturation for exact dictionary geodesics.

Every finite returned path is checked by expansion. Completion proves shortest
token length for the fixed dictionary and exact reduced target; bounded partial
saturation/query gives only a valid candidate and makes no optimality claim.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import heapq
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rank_unbounded_20260912'))
import search


class Meter:
    def __init__(self, limit):
        if type(limit) is not int or limit < 0:
            raise ValueError('limit must be a nonnegative integer')
        self.limit = limit
        self.counts = Counter()

    @property
    def used(self):
        return sum(self.counts.values())

    def charge(self, kind):
        if self.used == self.limit:
            return False
        self.counts[kind] += 1
        return True


class DictionaryGeodesic:
    def __init__(self, basis, definitions, *, eliminate_generator=None):
        basis = tuple(sorted(basis))
        if not basis or any(type(g) is not int or g <= 0 for g in basis) or len(set(basis)) != len(basis):
            raise ValueError('basis must be distinct positive integers')
        definitions = {g: tuple(w) for g, w in definitions.items()}
        if any(type(g) is not int or g <= 0 or g in basis for g in definitions):
            raise ValueError('dictionary helpers must be fresh positive integers')
        if any(not w or search.reduced(w) != w or not {abs(x) for x in w} <= set(basis)
               for w in definitions.values()):
            raise ValueError('dictionary words must be nonempty reduced old-generator words')
        self.images = {g: (g,) for g in basis}
        self.images.update(definitions)
        self.basis = frozenset(basis)
        if eliminate_generator is not None and (type(eliminate_generator) is not int
                                                or eliminate_generator not in self.basis):
            raise ValueError('elimination objective must name an old generator')
        self.eliminate_generator = eliminate_generator
        self.edges = []
        self.outgoing = defaultdict(list)
        self.incoming = defaultdict(list)
        self.states = 1
        for token, word in sorted(self.images.items()):
            for signed, image in ((token, word), (-token, search.inverse(word))):
                state = 0
                for position, letter in enumerate(image):
                    target = 0 if position + 1 == len(image) else self.states
                    if target:
                        self.states += 1
                    edge = (state, letter, target, (signed,) if position == 0 else ())
                    index = len(self.edges)
                    self.edges.append(edge)
                    self.outgoing[state].append(index)
                    self.incoming[target].append(index)
                    state = target
        self.epsilon = {}
        self.saturation_complete = False

    def expand(self, template):
        return search.reduced(x for token in template for x in
                              (self.images[token] if token > 0 else search.inverse(self.images[-token])))

    def _tokens(self, edge_indices):
        return tuple(token for i in edge_indices for token in self.edges[i][3])

    def _path_cost(self, edge_indices):
        return self.token_cost(self._tokens(edge_indices))

    def token_cost(self, tokens):
        return (sum(abs(x) == self.eliminate_generator for x in tokens), len(tokens))

    @staticmethod
    def _plus(left, right):
        return left[0] + right[0], left[1] + right[1]

    def saturate(self, meter):
        pending = [((0, 0), i, i, ()) for i in range(self.states)]
        tentative = {(i, i): (0, 0) for i in range(self.states)}
        settled, starts, ends = {}, defaultdict(dict), defaultdict(dict)

        def offer(p, q, cost, witness):
            if (p, q) not in settled and cost < tentative.get((p, q), (float('inf'), float('inf'))):
                tentative[p, q] = cost
                heapq.heappush(pending, (cost, p, q, witness))

        while pending:
            cost, p, q, witness = heapq.heappop(pending)
            if (p, q) in settled or tentative[p, q] != cost:
                continue
            settled[p, q] = cost, witness
            starts[p][q] = cost, witness
            ends[q][p] = cost, witness
            for a, (left_cost, left) in list(ends[p].items()):
                if (a, q) in settled:
                    continue
                if not meter.charge('epsilon_concatenations'):
                    self.epsilon = settled
                    return False
                offer(a, q, self._plus(left_cost, cost), left + witness)
            for b, (right_cost, right) in list(starts[q].items()):
                if (p, b) in settled:
                    continue
                if not meter.charge('epsilon_concatenations'):
                    self.epsilon = settled
                    return False
                offer(p, b, self._plus(cost, right_cost), witness + right)
            for left in self.incoming[p]:
                a, letter, _, tokens_left = self.edges[left]
                for right in self.outgoing[q]:
                    _, other, b, tokens_right = self.edges[right]
                    if other != -letter or (a, b) in settled:
                        continue
                    if not meter.charge('epsilon_cancellation_pairs'):
                        self.epsilon = settled
                        return False
                    offer(a, b, self._plus(cost, self.token_cost(tokens_left + tokens_right)),
                          (left,) + witness + (right,))
        self.epsilon = settled
        self.saturation_complete = True
        for (p, q), (cost, path) in settled.items():
            if search.reduced(self.edges[i][1] for i in path) or self._path_cost(path) != cost:
                raise AssertionError('freely-trivial automaton path differs')
            if path and (self.edges[path[0]][0] != p or self.edges[path[-1]][2] != q):
                raise AssertionError('epsilon witness endpoints differ')
        return True

    def shortest(self, word, meter):
        word = tuple(word)
        if search.reduced(word) != word or not {abs(x) for x in word} <= self.basis:
            raise ValueError('target must be a reduced old-generator word')
        baseline = word
        frontier = {0: ((0, 0), ())}
        outgoing_eps = defaultdict(list)
        for (p, q), (cost, path) in self.epsilon.items():
            outgoing_eps[p].append((q, cost, path))

        def closure(states):
            closed = dict(states)
            for p, (cost, path) in states.items():
                for q, extra, epsilon in outgoing_eps[p]:
                    if not meter.charge('query_epsilon_paths'):
                        return closed, False
                    candidate = self._plus(cost, extra), path + epsilon
                    if q not in closed or candidate[0] < closed[q][0]:
                        closed[q] = candidate
            return closed, True

        complete = True
        for position, letter in enumerate(word):
            frontier, done = closure(frontier)
            if not done:
                complete = False
                break
            if 0 in frontier:
                tokens = self._tokens(frontier[0][1]) + word[position:]
                if self.token_cost(tokens) < self.token_cost(baseline):
                    baseline = tokens
            following = {}
            for p, (cost, path) in frontier.items():
                for edge in self.outgoing[p]:
                    _, label, q, tokens = self.edges[edge]
                    if label != letter:
                        continue
                    if not meter.charge('query_letter_edges'):
                        complete = False
                        break
                    candidate = self._plus(cost, self.token_cost(tokens)), path + (edge,)
                    if q not in following or candidate[0] < following[q][0]:
                        following[q] = candidate
                if not complete:
                    break
            if not complete:
                break
            frontier = following
        else:
            frontier, complete = closure(frontier)
            if 0 in frontier:
                tokens = self._tokens(frontier[0][1])
                if self.token_cost(tokens) < self.token_cost(baseline):
                    baseline = tokens
        if self.expand(baseline) != word:
            raise AssertionError('dictionary geodesic does not expand to target')
        return baseline, complete and self.saturation_complete


def solve(word, definitions, budget=1000, *, eliminate_generator=None):
    basis = {abs(x) for x in word}
    basis.update(abs(x) for w in definitions.values() for x in w)
    engine = DictionaryGeodesic(basis, definitions, eliminate_generator=eliminate_generator)
    meter = Meter(budget)
    engine.saturate(meter)
    template, complete = engine.shortest(tuple(word), meter)
    return {'target': tuple(word), 'definitions': definitions, 'template': template,
            'complete_geodesic': complete, 'saturation_complete': engine.saturation_complete,
            'objective': 'length' if eliminate_generator is None else 'old_generator_count_then_length',
            'eliminate_generator': eliminate_generator, 'template_cost': engine.token_cost(template),
            'charged_units': meter.used, 'work_counts': dict(meter.counts),
            'automaton_states': engine.states, 'automaton_edges': len(engine.edges)}
