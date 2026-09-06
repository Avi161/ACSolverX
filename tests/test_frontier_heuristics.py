import pytest

from experiments.search.frontier_heuristics import search, verify
from experiments.search.heuristic_1k import run


@pytest.mark.parametrize('generators', [False, True])
def test_standard_priority_reproduces_existing_engine(generators):
    pair = ('YYXyx', 'Yx')
    old = run(pair, 'aut_edges' if generators else 's20', budget=30)
    new = search(pair, budget=30, generators=generators)
    for field in ('solved', 'nodes_explored', 'states', 'steps'):
        assert new[field] == old[field]
    assert verify(pair, new)


@pytest.mark.parametrize('normalization', ['none', 'root', 'pop', 'children'])
@pytest.mark.parametrize('beam', [0, 2])
def test_normalized_and_beam_budget_and_certificates(normalization, beam):
    pair = ('YYXyx', 'Yx')
    result = search(pair, budget=20, normalization=normalization, beam=beam, generators=True)
    assert 1 <= result['nodes_explored'] <= 20
    assert result['expanded_states'] <= result['nodes_explored']
    if result['solved']:
        assert verify(pair, result)
    terminal = search(('x', 'y'), budget=1, normalization=normalization, beam=beam)
    assert terminal['solved'] and verify(('x', 'y'), terminal)
