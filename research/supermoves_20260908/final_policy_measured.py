"""Fixed donor prepass, plain S20 prefix, then original-input incumbent restart."""
import time
from experiments.equivalence_classes.lib.words import apply_pair,canon_pair,canon_rel
from research.supermoves_20260908.plain_search_fast import mixed_search as plain_search
from research.supermoves_20260908.strict_donor_route import match
from research.supermoves_20260908.DONOR_NORMALIZED_BS import inspect
from research.supermoves_20260908.mid_search import mixed_search
from research.supermoves_20260908.root_router import search as incumbent


def search(pair,budget=1000,prepass_cap=250,plain_prefix=872):
    if type(budget) is not int or budget<1:
        raise ValueError('budget must be positive integer')
    if type(prepass_cap) is not int or prepass_cap<0:
        raise ValueError('prepass_cap must be nonnegative integer')
    if type(plain_prefix) is not int or plain_prefix<0:
        raise ValueError('plain_prefix must be nonnegative integer')
    started,cpu=time.perf_counter(),time.process_time()
    root=list(canon_pair(*pair));limit=min(prepass_cap,max(0,budget-1))
    charged=0;attempts=[];result=None
    for index,donor in enumerate(root):
        if charged>=limit:break
        route=match(donor,evaluation_cap=min(64,limit-charged))
        charged+=route['input_analysis']['evaluations']
        attempt=dict(donor_index=index,recognition=route);attempts.append(attempt)
        if route['status']!='match':continue
        if charged+len(route['maps'])>=limit:
            attempt['status']='prepass_limit';continue
        states=[root];steps=[];limited=False
        for image in route['maps']:
            if sum(len(image[c.lower()])for word in states[-1]for c in word)>100000:
                limited=True;attempt['status']='image_symbol_limit';break
            states.append(list(apply_pair(states[-1],image)))
            steps.append(dict(kind='automorphism',images=image));charged+=1
        if limited:continue
        assert canon_rel(route['template_word'])in states[-1]
        gates,symbol_work=inspect(states[-1]);attempt.update(gates=gates,gate_symbol_work=symbol_work)
        if not(gates['two_block']or gates['one_occurrence_relators']or(gates['bs_preflight']or{}).get('status')=='accept'):continue
        tail=mixed_search(states[-1],'s20',budget=limit-charged,cap=None,use_bs=True,general_bs=True,use_two_block=True,use_primitive=True,use_bs_preflight=True)
        charged+=tail['nodes_explored'];attempt.update(terminal_solved=tail['solved'],terminal_charges=tail['nodes_explored'])
        if tail['solved']:
            result=dict(tail)
            result.update(states=states+tail['states'][1:],steps=steps+tail['steps'],nodes_explored=charged,policy_route='strict_donor')
            break
    prepass_wall,prepass_cpu=time.perf_counter()-started,time.process_time()-cpu
    plain_charges=0
    plain_wall,plain_cpu=0.,0.
    if result is None and plain_prefix:
        t,c=time.perf_counter(),time.process_time()
        plain=plain_search(pair,'s20',budget=min(plain_prefix,budget-charged),cap=None,s_weight=20.,mk_weight=2.,w_weight=0.)
        plain_charges=plain['nodes_explored']
        plain_wall,plain_cpu=time.perf_counter()-t,time.process_time()-c
        if plain['solved'] or charged+plain_charges>=budget:
            result=dict(plain)
            result['nodes_explored']+=charged
            result['policy_route']='plain_s20'
    if result is None:
        result=dict(incumbent(pair,budget=budget-charged-plain_charges,use_high_core_escape=True))
        result['fallback_nodes']=result['nodes_explored']
        result['nodes_explored']+=charged+plain_charges
        result['policy_route']='incumbent_restart'
    assert result['nodes_explored']<=budget
    result.update(plain_prefix=plain_prefix,plain_charges=plain_charges,plain_wall=plain_wall,plain_cpu=plain_cpu,prepass_charges=charged,prepass_cap=limit,prepass_attempts=attempts,prepass_wall=prepass_wall,prepass_cpu=prepass_cpu,policy_wall=time.perf_counter()-started,policy_cpu=time.process_time()-cpu,work_unit_note='Image evaluations + accepted maps + terminal/fallback search charges; not calibrated equivalent pops. Gate symbol work separate.')
    return result
