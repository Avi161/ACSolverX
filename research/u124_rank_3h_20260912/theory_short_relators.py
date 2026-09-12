"""Exact fixed-rank ordinary-AC terminal compiler for balanced length <= 2."""
import json
from pathlib import Path


def reduce_word(word):
    out = []
    for x in word:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def inverse(word):
    return tuple(-x for x in reversed(word))


def replay(words, moves):
    state = [reduce_word(w) for w in words]
    for move in moves:
        i = move['target']
        if move['op'] == 'invert':
            state[i] = inverse(state[i])
        elif move['op'] == 'conjugate':
            c = move['letter']
            state[i] = reduce_word((-c,) + state[i] + (c,))
        elif move['op'] == 'right_multiply':
            assert i != move['donor']
            state[i] = reduce_word(state[i] + state[move['donor']])
        else:
            raise ValueError(move)
        assert len(state[i]) <= 2
    return tuple(state)


def trivialize(words, generators=None):
    initial = tuple(reduce_word(w) for w in words)
    ids = sorted(set(generators) if generators is not None else {abs(x) for w in initial for x in w})
    if len(initial) != len(ids) or any(len(w) > 2 for w in initial):
        raise ValueError('requires balanced tuple, declared positive generator labels, and reduced lengths <= 2')
    assert all(g > 0 for g in ids)
    assert {abs(x) for w in initial for x in w} <= set(ids)
    adjacency = {g: [] for g in ids}
    units = {g: [] for g in ids}
    for i, w in enumerate(initial):
        if len(w) == 1:
            units[abs(w[0])].append(i)
        elif len(w) == 2:
            a, b = map(abs, w)
            adjacency[a].append((b, i))
            adjacency[b].append((a, i))
    seen, components = set(), []
    for g in ids:
        if g in seen:
            continue
        component, todo = set(), [g]
        while todo:
            v = todo.pop()
            if v in component:
                continue
            component.add(v)
            todo.extend(w for w, _ in adjacency[v])
        seen.update(component)
        roots = [(v, i) for v in component for i in units[v]]
        if not roots:
            assignment = {str(v): int(v in component) for v in ids}
            assert any(assignment.values())
            assert all(sum(assignment[str(abs(x))] for x in w) % 2 == 0 for w in initial)
            return {'trivial': False, 'C2_quotient': assignment, 'moves': []}
        edge_ids = {i for v in component for _, i in adjacency[v]}
        components.append((component, roots, edge_ids))
    assert all(len(roots) == 1 and len(edges) == len(component) - 1
               for component, roots, edges in components)
    assert all(initial)
    state, moves = list(initial), []
    def apply(op, target, **kwargs):
        move = dict(op=op, target=target, **kwargs)
        state[:] = replay(state, [move])
        moves.append(move)
    singleton_index = {}
    for component, roots, _ in components:
        root, index = roots[0]
        if state[index] == (-root,):
            apply('invert', index)
        singleton_index[root] = index
        todo = [root]
        while todo:
            parent = todo.pop()
            for child, edge in adjacency[parent]:
                if child in singleton_index:
                    continue
                w = state[edge]
                child_letter = next(x for x in w if abs(x) == child)
                if child_letter < 0:
                    apply('invert', edge)
                if state[edge][0] != child:
                    apply('conjugate', edge, letter=state[edge][0])
                assert state[edge][0] == child and abs(state[edge][1]) == parent
                donor = singleton_index[parent]
                positive = state[edge][1] > 0
                if positive:
                    apply('invert', donor)
                apply('right_multiply', edge, donor=donor)
                if positive:
                    apply('invert', donor)
                assert state[edge] == (child,)
                singleton_index[child] = edge
                todo.append(child)
    assert replay(initial, moves) == tuple(state)
    assert sorted(state) == [(g,) for g in ids]
    return {'trivial': True, 'initial': initial, 'endpoint': state, 'moves': moves,
            'unit_relator_indices': singleton_index, 'rank_preserved': len(ids),
            'maximum_relator_length': max(map(len, initial), default=0),
            'terminal_scope': 'positive standard generators, up to relator permutation'}


def controls():
    from itertools import product
    solved = []
    for signs in product((-1, 1), repeat=5):
        a, b, c, d, e = signs
        words = ((a,), (b * 2, c), (d * 3, e * 2))
        result = trivialize(words)
        assert result['trivial'] and len(result['moves']) <= 11
        solved.append({'input': words, 'endpoint': result['endpoint'], 'moves': result['moves']})
    negatives = [((1, 1),), ((1, 2), (1, -2)), ((), (1, 2)), ((1,), (2, 2))]
    for words in negatives:
        assert not trivialize(words, (1,) if len(words) == 1 else (1, 2))['trivial']
    sparse = trivialize(((10**25,), (-7, 10**25)))
    assert sparse['trivial']
    return {'PASS': True, 'signed_tree_controls': solved, 'nontrivial_C2_controls': negatives,
            'sparse_labels': sparse, 'scope': '33 positive controls, four exact quotient negatives; no census search'}


if __name__ == '__main__':
    output = Path(__file__).with_suffix('.json')
    if output.exists():
        raise ValueError('refusing to overwrite frozen controls')
    result = controls()
    output.write_text(json.dumps(result, indent=2) + '\n')
    assert json.loads(output.read_text())['PASS']
    print('PASS: 33 signed/sparse positive controls, 4 exact C2 quotient negatives; rank preserved')
