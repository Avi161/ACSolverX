"""Round-2 candidate cascades: a bounded 'pocket' stage in front of the ball cascade.

The pocket stage is the ordinary S20 search (plain_search_ball.mixed_search) with a
relator-length cap equal to the root's longest relator plus ``pocket_delta`` and a small
budget, with the backward-table terminal.  Under a tight cap the move graph around many
hard roots is a small pocket (tens to a few thousand states), so a breadth-limited search
either meets the table quickly or exhausts the pocket and stops; its charges are added to
the shared 1,000-unit allowance and the remainder goes to the ball cascade unchanged.
"""
import time
from experiments.equivalence_classes.lib.words import canon_pair
from research.residual_20260909 import plain_search_ball, final_policy_ball
from research.residual_20260909.policies import ball_table, policy, REGISTRY


def make_pocket_policy(stem, pocket_budget=200, pocket_delta=2, name=None, **cascade):
    def run(pair, budget):
        table = ball_table(stem)
        root = canon_pair(*pair)
        cap = max(map(len, root)) + pocket_delta
        t0, c0 = time.perf_counter(), time.process_time()
        pocket = plain_search_ball.mixed_search(
            pair, 's20', budget=min(pocket_budget, budget - 1), cap=cap,
            s_weight=20., mk_weight=2., w_weight=0., table=table)
        charged = pocket['nodes_explored']
        if pocket['solved']:
            result = dict(pocket)
            result.update(policy_route='pocket', pocket_charges=charged, pocket_cap=cap,
                          nodes_explored=charged, ball_table=stem,
                          policy_wall=time.perf_counter() - t0, policy_cpu=time.process_time() - c0)
            return result
        result = dict(final_policy_ball.search(pair, budget=budget - charged, table=table, **cascade))
        result['nodes_explored'] += charged
        result.update(pocket_charges=charged, pocket_cap=cap, pocket_solved=False, ball_table=stem)
        return result
    run.__doc__ = f'pocket stage ({pocket_budget} units, cap = max root relator + {pocket_delta}) then final_policy_ball.search({cascade}) on {stem}'
    if name is not None:
        run.__name__ = name
        policy(name)(run)
    return run


K3 = dict(prepass_cap=250, plain_prefix=300, certified_overrun=True, use_bs_demote=True)
for stem, suffix in (('ball_cap12_aut', 'c12aut'), ('ball_cap14_aut', 'c14aut')):
    make_pocket_policy(stem, 200, 2, name=f'P200d2_K3p_{suffix}', **K3)
    make_pocket_policy(stem, 300, 2, name=f'P300d2_K3p_{suffix}', **K3)
    make_pocket_policy(stem, 200, 1, name=f'P200d1_K3p_{suffix}', **K3)
    make_pocket_policy(stem, 300, 3, name=f'P300d3_K3p_{suffix}', **K3)
