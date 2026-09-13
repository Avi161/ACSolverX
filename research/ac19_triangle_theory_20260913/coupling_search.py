"""Rank-preserving best-first search that climbs toward the bigon gate.

Every edge is an ordinary AC normal-product substitution
``R_i <- rot(R_i) . rot(R_j^eps)`` emitted as a ``normal_product_substitution``
event, so the resulting paths replay under the frozen research verifier.  Rank,
the declared generator set and every relator are retained: no generator is
added or removed, and no destabilization is performed.

Two orderings are provided so the campaign can compare like with like:

``COUPLING``
    the ordering developed here.  Theory Lemma 2 says a shared cyclic digram
    (modulo ``inv2``) is *necessary* before any single substitution can produce
    a length-two relator, and Lemma 1 says a unit needs a relator of length
    other than three.  The score therefore ranks by
    ``(no unit, no bigon, -shared digram pairs, -shared digrams, length, ...)``
    which is a strictly monotone climb toward that gate rather than toward
    short total length.

``STRUCTURAL``
    the incumbent ordering from ``high_rank_ac_search.structural_score``, used
    unchanged as the control arm.
"""
from __future__ import annotations

import heapq
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(ROOT / 'research/rank_unbounded_20260912'),
                str(ROOT / 'research/u124_high_rank_ac_20260912'),
                str(ROOT / 'research/u124_rank_3h_20260912')]

import search                                  # noqa: E402
import high_rank_ac_search as engine           # noqa: E402
import theory                                  # noqa: E402


def coupling_score(state):
    pairs, total = theory.coupling(state)
    return (0 if theory.has_unit(state) else 1,
            0 if theory.has_bigon(state) else 1,
            -pairs, -total,
            search.length(state),
            max(map(len, state), default=0),
            state)


def structural_score(state):
    return engine.structural_score(state)


ORDERINGS = {'coupling': coupling_score, 'structural': structural_score}


def search_row(initial, *, ordering='coupling', pop_budget=400, relator_cap=5,
               beam=64, stop_on_bigon=True):
    """Best-first search retaining rank; returns the record and its work."""
    initial = search.normalize(initial)
    rank = len(initial)
    declared = {abs(x) for w in initial for x in w}
    key = ORDERINGS[ordering]

    records = [{'words': initial, 'parent': None, 'event': None}]
    seen = {initial}
    heap = [(key(initial), 0)]
    pops = 0
    rotation_products = 0
    first_bigon = first_unit = None
    first_coupled = None
    best_coupling = theory.coupling(initial)

    while heap and pops < pop_budget:
        _, index = heapq.heappop(heap)
        current = records[index]['words']
        pops += 1
        children, attempted = theory.one_step_products(current, relator_cap)
        rotation_products += attempted
        ranked = []
        for i, j, sign, k1, k2, product in children:
            endpoint = search.normalize(current[:i] + (product,) + current[i + 1:])
            if endpoint in seen:
                continue
            if len(endpoint) != rank or {abs(x) for w in endpoint for x in w} - declared:
                continue            # never change rank or leave the declared basis
            seen.add(endpoint)
            rebuilt, event = engine.normal_product_event(current, i, j, sign, k1, k2)
            if rebuilt != endpoint:
                raise AssertionError('endpoint changed while building its witness')
            records.append({'words': endpoint, 'parent': index, 'event': event})
            child = len(records) - 1
            pairs, total = theory.coupling(endpoint)
            if first_coupled is None and pairs:
                first_coupled = child
            if pairs > best_coupling[0] or (pairs == best_coupling[0] and total > best_coupling[1]):
                best_coupling = (pairs, total)
            if first_bigon is None and theory.has_bigon(endpoint):
                first_bigon = child
            if first_unit is None and theory.has_unit(endpoint):
                first_unit = child
            ranked.append((key(endpoint), child))
        if stop_on_bigon and first_bigon is not None:
            break
        ranked.sort()
        for item in ranked[:beam]:
            heapq.heappush(heap, item)

    def path_to(index):
        events = []
        while index is not None and records[index]['parent'] is not None:
            events.append(records[index]['event'])
            index = records[index]['parent']
        return list(reversed(events))

    target = first_unit if first_unit is not None else first_bigon
    return {
        'ordering': ordering,
        'initial': initial,
        'rank': rank,
        'relator_cap': relator_cap,
        'pop_budget': pop_budget,
        'beam': beam,
        'heap_pops': pops,
        'discovered_states': len(seen),
        'rotation_products': rotation_products,
        'initial_digram_disjoint': theory.is_digram_disjoint(initial),
        'best_coupling_pairs': best_coupling[0],
        'best_coupling_digrams': best_coupling[1],
        'first_coupled_state': records[first_coupled]['words'] if first_coupled is not None else None,
        'bigon_found': first_bigon is not None,
        'unit_found': first_unit is not None,
        'endpoint': records[target]['words'] if target is not None else None,
        'events': path_to(target) if target is not None else [],
        'shortest_relator_seen': min(min(map(len, r['words'])) for r in records),
    }
