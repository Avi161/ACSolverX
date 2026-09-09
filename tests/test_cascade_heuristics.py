import pytest

from experiments.search.cascade_heuristics import search
from experiments.search.frontier_heuristics import verify


def test_rewrite_component_has_complete_certificate_and_charged_normalization():
    pair = ('YxyXX', 'YYYYXyyyx')
    result = search(pair, budget=1000)
    assert result['solved'] and result['winner'] == 'rewrite'
    assert result['nodes_explored'] == len(result['steps'])+1
    assert result['nodes_explored'] == sum(a['nodes'] for a in result['attempts'])
    assert verify(pair, result)


@pytest.mark.parametrize('budget', [1, 5, 30])
def test_components_share_budget(budget):
    pair = ('YYXyx', 'Yx')
    result = search(pair, budget=budget, starter_budget=3, rewrite_budget=3)
    assert 1 <= result['nodes_explored'] <= budget
    assert result['nodes_explored'] == sum(a['nodes'] for a in result['attempts'])
    if result['solved']:
        assert verify(pair, result)


def test_no_extra_terminal_charge():
    result = search(('x','y'), budget=1)
    assert result['solved'] and result['nodes_explored'] == 1
    assert verify(('x','y'), result)


def test_tiny_budget_with_an_empty_relator_does_not_overrun_normalization():
    result = search(('', 'y'), budget=1)
    assert not result['solved'] and result['nodes_explored'] == 1
    assert sum(a['nodes'] for a in result['attempts']) == 1


def test_none_disables_both_length_caps_and_reports_progress():
    pair = ('YYXyx', 'Yx')
    result = search(pair, budget=30, cap=None, intermediate_cap=None)
    assert result['solved'] and verify(pair, result)
    assert result['min_total_length_seen'] == 2
    assert result['best_state'] == ['Y', 'X']
    assert result['max_relator_length_seen'] >= result['max_certificate_relator_length']


def test_campaign_budget_accepts_100k_and_rejects_more():
    result = search(('x', 'y'), budget=100_000)
    assert result['solved'] and result['nodes_explored'] == 1
    with pytest.raises(ValueError, match='1..100000'):
        search(('x', 'y'), budget=100_001)
