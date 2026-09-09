"""Fixed experimental routing from the initial canonical relators."""
import time

from experiments.equivalence_classes.lib.words import canon_pair
from research.supermoves_20260908.mid_search import bs_escape_feature, mixed_search


def search(pair, budget=1000, use_high_core_escape=False, use_commutator=False,
           commutator_admit=True, use_full_splice=False, full_splice_admit=True, full_splice_every=0):
    if (not isinstance(use_commutator,bool) or not isinstance(commutator_admit,bool)
            or not isinstance(use_full_splice,bool) or not isinstance(full_splice_admit,bool)):
        raise ValueError('commutator/full-splice options must be boolean')
    if (isinstance(full_splice_every,bool) or not isinstance(full_splice_every,int)
            or full_splice_every<0 or full_splice_every==1):
        raise ValueError('full_splice_every must be0 or an integer>=2')
    if full_splice_every and (not use_full_splice or not full_splice_admit):
        raise ValueError('full-splice quota requires admitted full-splice children')
    if use_commutator and use_full_splice:
        raise ValueError('commutator and full-splice children are mutually exclusive')
    started = time.perf_counter()
    cpu_started = time.process_time()
    root = canon_pair(*pair)
    value, check = bs_escape_feature(root)
    ordinary = value > 0
    routing_cpu = time.process_time() - cpu_started
    routing_wall = time.perf_counter() - started
    extra = dict(bs_escape_macro_budget=300, bs_escape_macro_min_stable=7) if use_high_core_escape and not ordinary else {}
    if use_commutator:
        extra['use_commutator']=True
        extra['commutator_admit']=commutator_admit
    if use_full_splice:
        extra['use_full_splice']=True
        extra['full_splice_admit']=full_splice_admit
        if full_splice_every:extra['full_splice_every']=full_splice_every
    result = mixed_search(
        pair, 's20' if ordinary else 'aut_edges', budget=budget, cap=None,
        w_weight=1.5, s_weight=20., mk_weight=2., use_bs=True,
        general_bs=True, use_two_block=True, probe_when='generated',
        use_bs_preflight=True, bs_escape_weight=4. if ordinary else 0., **extra,
    )
    result.update(
        route='ordinary_bs_escape' if ordinary else 's20_generator',
        routing_feature=value, routing_check=check,
        routing_wall=routing_wall, routing_cpu=routing_cpu,
    )
    if use_high_core_escape:
        result['high_core_escape_enabled'] = not ordinary
    return result
