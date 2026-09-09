"""``mid_search`` plus a backward-ball terminal, and nothing else.

A copy of ``research/supermoves_20260908/mid_search.py`` -- the frozen module
is left untouched so it stays the comparison implementation -- with one
addition: a hash lookup of every newly created state in the exact backward ball
``B(cap)`` built by ``backward_table.build``.

The lookup is placed at the root and at EVERY state this search creates:

  * substitution children of a popped state,
  * ``aut_edges`` automorphism children,
  * commutator / full-splice children,
  * the partial states a macro contributes through ``admit_partial``,
  * and, transitively, everything the bounded BS-escape continuation creates
    (the recursive ``mixed_search`` call is handed the same table).

Nothing else moves.  The heap, the priorities, the ``parent`` de-duplication,
the terminal macros, and every ``nodes`` charge are the frozen code verbatim,
and a lookup neither charges a unit nor pushes, pops or reorders anything, so
the ball run and the frozen run are in lockstep until the first hit.  The
trivial pair ``('Y', 'X')`` is in the table at depth 0 and is the only
canonical state the frozen terminal test accepts, so every frozen solve is
matched here at a point no later in the same execution; ``nodes`` is
nondecreasing along an execution, hence ``nodes_ball <= nodes_frozen`` on every
row the frozen search solves, and hits at other states can only end the search
earlier still.  Every stored edge was forward-verified against this same kernel
at build time and re-checked by pure-Python replay, so a spliced tail is a real
path of engine moves down to ``('Y', 'X')``.

``nodes_explored`` therefore keeps its frozen meaning exactly.  Lookups are
free and are reported separately as ``ball_lookups``, with ``ball_hit`` and
``ball_depth``.
"""
import heapq
import numpy as np
from experiments.search.heuristic_1k import pack, score_key, adjust_scores, NIELSEN
from research.supermoves_20260908.packed_words import unpack_canonical_key as unpack
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair
from experiments.heuristic_search.core.hfast import _arrs, compile_config
from experiments.heuristic_search.core.hexpand import expand_and_score_h
from experiments.search.heuristics import BASELINE_CONFIG
from experiments.search.bs_collapse import bs_collapse
from research.supermoves_20260908.two_block import solve as solve_two_block, MoveBudgetExceeded
from research.supermoves_20260908.consecutive_bs import collapse as consecutive_collapse
from research.supermoves_20260908.cheap_gates import bs_gate, canonical_two_block_gate as two_block_gate
from research.supermoves_20260908.cheap_gates import one_occurrence_donor
from research.supermoves_20260908.primitive_completion import complete as primitive_complete
from research.supermoves_20260908.stable_square import collapse as stable_square_collapse, DONOR_TRANSFORMS
from research.supermoves_20260908.bs_preflight import preflight as bs_preflight
from research.supermoves_20260908.stable_power import collapse as stable_power_collapse, canonical_donor_gate
from research.supermoves_20260908.splice_power_family import collapse as splice_power_collapse, canonical_family_gate
from research.supermoves_20260908.christoffel_primitive_gate import is_christoffel_primitive_canonical
from research.residual_20260909.backward_table import tail as ball_tail

_UNSET = object()
_TABLE = None


def set_table(table):
    """Install the module-level backward ball used when no ``table=`` is passed."""
    global _TABLE
    _TABLE = table


def get_table():
    return _TABLE


def _resolve(table):
    return _TABLE if table is _UNSET else table


def bs_escape_feature(state):
    """Return donor-relative T=s-1 only for a recognized stalled BS pair."""
    if bs_gate(state, general=True) is None:
        return 0, {
            'status': 'reject', 'scans': 0, 'pinches': 0,
            'reason': 'cheap_gate_not_recognized', 'preflight_called': False,
        }
    check = bs_preflight(state)
    check = dict(check, preflight_called=True)
    if check['status'] != 'reject' or 'stable_letters' not in check:
        return 0, check
    return max(0, check['stable_letters'] - 1), check


def mixed_search(pair, arm, budget=1000, cap=48, w_weight=None,
                 s_weight=20.0, mk_weight=2.0, use_bs=True, general_bs=False,
                 use_two_block=False, probe_when='pop', use_primitive=False,
                 use_stable_square=False, use_partial_macros=False,
                 use_bs_preflight=False, use_stable_power=False, use_splice_power=False,
                 bs_escape_weight=0.0, use_christoffel=False, bs_escape_macro_budget=0,
                 bs_escape_macro_min_stable=3, use_commutator=False, commutator_admit=True,
                 use_full_splice=False, full_splice_admit=True, full_splice_every=0,
                 table=_UNSET):
    table = _resolve(table)
    if not isinstance(use_commutator, bool):
        raise ValueError('use_commutator must be boolean')
    if not isinstance(commutator_admit, bool):
        raise ValueError('commutator_admit must be boolean')
    if not isinstance(use_full_splice, bool):
        raise ValueError('use_full_splice must be boolean')
    if not isinstance(full_splice_admit, bool):
        raise ValueError('full_splice_admit must be boolean')
    if (isinstance(full_splice_every,bool) or not isinstance(full_splice_every,int)
            or full_splice_every<0 or full_splice_every==1):
        raise ValueError('full_splice_every must be0 or an integer>=2')
    if full_splice_every and (not use_full_splice or not full_splice_admit):
        raise ValueError('full-splice quota requires admitted full-splice children')
    if use_commutator and use_full_splice:
        raise ValueError('commutator and full-splice children are mutually exclusive')
    if probe_when not in ('pop','generated'):
        raise ValueError('probe_when must be pop or generated')
    if (isinstance(bs_escape_weight, bool) or not isinstance(bs_escape_weight, (int, float))
            or not np.isfinite(bs_escape_weight) or bs_escape_weight < 0):
        raise ValueError('bs_escape_weight must be finite and nonnegative')
    if (isinstance(bs_escape_macro_budget, bool) or not isinstance(bs_escape_macro_budget, int)
            or not 0 <= bs_escape_macro_budget <= 1000):
        raise ValueError('BS escape macro budget must be an integer in 0..1000')
    if (isinstance(bs_escape_macro_min_stable, bool)
            or not isinstance(bs_escape_macro_min_stable, int) or bs_escape_macro_min_stable < 3):
        raise ValueError('BS escape macro minimum stable count must be an integer at least3')
    collapse_bs = consecutive_collapse if general_bs else bs_collapse
    if w_weight is None:
        w_weight = 2.0 if arm == 'whitehead2' else 0.0
    whitehead = w_weight != 0.0
    escape_feature_checks = 0
    escape_preflight_calls = 0
    escape_preflight_scans = 0
    escape_hits = 0
    ball_lookups = 0

    def with_escape(_key, state, base):
        nonlocal escape_feature_checks
        nonlocal escape_preflight_calls, escape_preflight_scans
        nonlocal escape_hits
        if bs_escape_weight == 0:
            return float(base)
        escape_feature_checks += 1
        value, check = bs_escape_feature(state)
        if check['preflight_called']:
            escape_preflight_calls += 1
            escape_preflight_scans += check['scans']
        escape_hits += value > 0
        return float(base) + bs_escape_weight * value

    root = pack(canon_pair(*pair))
    root_state = unpack(root)
    base_priority = float(len(root)-1) if arm == 'greedy' else score_key(
        np.frombuffer(root,dtype=np.uint8),whitehead,w_weight,s_weight,mk_weight)
    priority = with_escape(root, root_state, base_priority)
    heap=[(priority,0,root)]
    parent={root:None}
    best=root
    best_total=len(root)-1
    best_max=max(map(len,unpack(root)))
    max_seen=best_max
    config={'segments':[{'upto':None,'w':{'L':1.0,'S':s_weight,'MK':mk_weight}}]}
    upto,weights,_=compile_config(BASELINE_CONFIG if arm=='greedy' else config)
    nodes=0
    basis_evaluations=0
    probe_calls=0
    probe_hits=0
    probe_rewrites=0
    completion_checks=0
    generated_unique=0
    stable_square_calls=0
    stable_square_rewrites=0
    partial_macro_states=0
    preflight_calls=preflight_rejects=preflight_scans=0
    stable_power_calls=stable_power_rewrites=0
    stable_power_matcher_tests=0
    splice_power_calls=splice_power_rewrites=0
    escape_macros=[]
    commutator_blocks=commutator_attempts=commutator_admitted=0
    commutator_wall=commutator_cpu=0.0
    heap_pops=commutator_cap_rejects=commutator_duplicates=commutator_processed=0
    full_splice_blocks=full_splice_attempts=full_splice_admitted=0
    full_splice_wall=full_splice_cpu=0.0
    full_splice_cap_rejects=full_splice_duplicates=full_splice_processed=0
    full_splice_potential_moves=0
    full_splice_direct_pops=0
    splice_heap=[]
    quota_closed=set()
    forced_splice_pops=quota_stale_discards=0

    def result(solved=False,key=None,winner=None,macro=None,tail=None,ball_depth=None):
        steps,states=[],[]
        ball_key=key
        if solved:
            while key is not None:
                states.append(list(unpack(key)))
                previous=parent[key]
                if previous is None:
                    break
                key,step=previous
                steps.append(step)
            states.reverse();steps.reverse()
            if macro is not None:
                states+=macro['states'][1:]
                steps+=macro['steps']
            if ball_depth is not None:
                tail_states,tail_steps=ball_tail(table,ball_key)
                states+=tail_states[1:]
                steps+=tail_steps
        out=dict(solved=solved,nodes_explored=nodes,states=states,steps=steps,
                 basis_evaluations=basis_evaluations,best_state=list(unpack(best)),
                 min_total_length_seen=best_total,min_max_relator_length_seen=best_max,
                 max_relator_length_seen=max_seen,probe_calls=probe_calls,
                 probe_hits=probe_hits,probe_rewrites=probe_rewrites,
                 completion_checks=completion_checks,generated_unique=generated_unique,
                 probe_when=probe_when,stable_square_calls=stable_square_calls,
                 stable_square_rewrites=stable_square_rewrites,
                 partial_macro_states=partial_macro_states,
                 preflight_calls=preflight_calls,preflight_rejects=preflight_rejects,
                 preflight_scans=preflight_scans,stable_power_calls=stable_power_calls,
                 stable_power_rewrites=stable_power_rewrites,
                 stable_power_matcher_tests=stable_power_matcher_tests,
                 splice_power_calls=splice_power_calls,splice_power_rewrites=splice_power_rewrites,
                 bs_escape_weight=float(bs_escape_weight),
                 bs_escape_feature_checks=escape_feature_checks,
                 bs_escape_preflight_calls=escape_preflight_calls,
                 bs_escape_preflight_scans=escape_preflight_scans,
                 bs_escape_hits=escape_hits,ball_lookups=ball_lookups,
                 ball_hit=ball_depth is not None,ball_depth=ball_depth or 0)
        if use_commutator:
            out.update(commutator_blocks=commutator_blocks,
                commutator_attempts=commutator_attempts,commutator_admitted=commutator_admitted,
                commutator_generation_wall=commutator_wall,commutator_generation_cpu=commutator_cpu,
                heap_pops=heap_pops,terminal_macro_charges=nodes-heap_pops-commutator_blocks,
                commutator_cap_rejects=commutator_cap_rejects,commutator_duplicates=commutator_duplicates,
                commutator_potential_elementary_moves=6*commutator_attempts,
                commutator_processed=commutator_processed,
                commutator_unprocessed=commutator_attempts-commutator_processed,
                commutator_suppressed_control_attempts=0 if commutator_admit else commutator_attempts,
                commutator_unprocessed_budget=commutator_attempts-commutator_processed if commutator_admit else 0,
                commutator_generation_enabled=True,commutator_edges_enabled=commutator_admit)
        if use_full_splice:
            out.update(full_splice_blocks=full_splice_blocks,
                full_splice_direct_pops=full_splice_direct_pops,
                full_splice_attempts=full_splice_attempts,
                full_splice_admitted=full_splice_admitted,
                full_splice_generation_wall=full_splice_wall,
                full_splice_generation_cpu=full_splice_cpu,
                heap_pops=heap_pops,
                terminal_macro_charges=nodes-heap_pops-full_splice_blocks,
                full_splice_cap_rejects=full_splice_cap_rejects,
                full_splice_duplicates=full_splice_duplicates,
                full_splice_potential_elementary_moves=full_splice_potential_moves,
                full_splice_processed=full_splice_processed,
                full_splice_unprocessed=full_splice_attempts-full_splice_processed,
                full_splice_suppressed_control_attempts=(
                    0 if full_splice_admit else full_splice_attempts),
                full_splice_unprocessed_budget=(
                    full_splice_attempts-full_splice_processed if full_splice_admit else 0),
                full_splice_generation_enabled=True,
                full_splice_edges_enabled=full_splice_admit)
        if full_splice_every:
            out.update(full_splice_every=full_splice_every,forced_splice_pops=forced_splice_pops,
                quota_stale_discards=quota_stale_discards,unique_expanded=len(quota_closed))
        if winner:out['winner']=winner
        if tail is not None:out['elementary_tail']=tail
        if bs_escape_macro_budget:
            out['escape_macros']=escape_macros
        return out

    def ball_probe(child):
        """One free hash lookup of a newly created state in the backward ball.

        Returns a finished solved result (search path + the stored substitution
        tail down to the trivial pair) on a hit, else ``None``.  Never charges a
        unit and never touches the heap.
        """
        nonlocal ball_lookups
        if table is None:
            return None
        ball_lookups+=1
        entry=table.get(child)
        if entry is None:
            return None
        return result(True,child,'ball',ball_depth=entry[0])

    def admit_partial(key, depth, macro):
        nonlocal partial_macro_states, generated_unique, max_seen, best, best_total, best_max
        if not use_partial_macros:
            return None
        previous = key
        for distance, (words, step) in enumerate(zip(macro['states'][1:], macro['steps']), 1):
            child = pack(words)
            if child not in parent:
                parent[child] = previous, step
                partial_macro_states += 1
                generated_unique += 1
                total, largest = sum(map(len, words)), max(map(len, words))
                max_seen = max(max_seen, largest)
                if (total, largest, child) < (best_total, best_max, best):
                    best, best_total, best_max = child, total, largest
                base_score = float(total) if arm == 'greedy' else score_key(
                    np.frombuffer(child, dtype=np.uint8), whitehead, w_weight, s_weight, mk_weight)
                score = with_escape(child, words, base_score)
                done = ball_probe(child)
                if done:
                    return done
                heapq.heappush(heap, (score, depth + distance, child))
            previous = child
        return None

    def complete(state,key,depth):
        nonlocal nodes,probe_calls,probe_hits,probe_rewrites,completion_checks
        nonlocal stable_square_calls,stable_square_rewrites
        nonlocal preflight_calls,preflight_rejects,preflight_scans
        nonlocal stable_power_calls,stable_power_rewrites
        nonlocal stable_power_matcher_tests
        nonlocal splice_power_calls,splice_power_rewrites
        nonlocal best,best_total,best_max,max_seen
        completion_checks+=1
        if len(state[0])==len(state[1])==1 and state[0].lower()!=state[1].lower():
            return result(True,key,'terminal')
        if nodes>=budget:
            return None
        if use_two_block and two_block_gate(state):
            try:
                tail=solve_two_block(state,max_moves=budget-nodes)
            except MoveBudgetExceeded:
                nodes=budget
                return None
            assert tail['solved']
            nodes+=tail['elementary_move_count']
            return result(True,key,'middle_two_block',tail=tail['elementary_moves'])
        if use_bs:
            probe_calls+=1
            if bs_gate(state,general=general_bs) is not None:
                probe_hits+=1
                rejected=False
                if use_bs_preflight:
                    check=bs_preflight(state)
                    preflight_calls+=1
                    preflight_scans+=check['scans']
                    rejected=check['status']=='reject'
                    preflight_rejects+=rejected
                    if (bs_escape_macro_budget and not escape_macros and rejected
                            and check.get('stable_letters', 0) >= bs_escape_macro_min_stable
                            and nodes < budget):
                        continuation = mixed_search(
                            state, 's20', budget=min(bs_escape_macro_budget, budget-nodes), cap=cap,
                            w_weight=1.5, s_weight=20., mk_weight=2., use_bs=True,
                            general_bs=True, use_two_block=True, probe_when='generated',
                            use_bs_preflight=True, bs_escape_weight=4., table=table,
                            use_stable_power=use_stable_power)
                        nodes += continuation['nodes_explored']
                        escape_macros.append({
                            'state': list(state), 'solved': continuation['solved'],
                            'nodes': continuation['nodes_explored'],
                            'generated_unique': continuation['generated_unique'],
                            'feature_checks': continuation['bs_escape_feature_checks'],
                            'preflight_calls': continuation['bs_escape_preflight_calls'],
                            'preflight_scans': continuation['bs_escape_preflight_scans'],
                            'completion_preflight_calls': continuation['preflight_calls'],
                            'completion_preflight_scans': continuation['preflight_scans'],
                            'probe_rewrites': continuation['probe_rewrites'],
                            'outer_nodes_before': nodes-continuation['nodes_explored'],
                            'outer_depth': depth,
                        })
                        candidate = pack(continuation['best_state'])
                        total = continuation['min_total_length_seen']
                        largest = continuation['min_max_relator_length_seen']
                        max_seen = max(max_seen, continuation['max_relator_length_seen'])
                        if (total, largest, candidate) < (best_total, best_max, best):
                            best, best_total, best_max = candidate, total, largest
                        if continuation['solved']:
                            return result(True, key, 'middle_bs_escape', macro=continuation,
                                          tail=continuation.get('elementary_tail'))
                if not rejected:
                    macro=collapse_bs(state,budget=min(10000,budget-nodes+1),intermediate_cap=None)
                    nodes+=macro['rewrites']
                    probe_rewrites+=macro['rewrites']
                    if macro['solved']:
                        return result(True,key,'middle_bs',macro=macro)
                    done=admit_partial(key,depth,macro)
                    if done:return done
        if use_splice_power and nodes < budget and canonical_family_gate(state):
            splice_power_calls += 1
            macro = splice_power_collapse(state,budget=min(1000,budget-nodes+1),intermediate_cap=None)
            nodes += macro['rewrites']
            splice_power_rewrites += macro['rewrites']
            if macro['solved']:
                return result(True,key,'middle_splice_power',macro=macro)
            done=admit_partial(key,depth,macro)
            if done:return done
        if use_stable_power and nodes < budget and canonical_donor_gate(state):
            stable_power_calls += 1
            macro = stable_power_collapse(state, budget=min(1000,budget-nodes+1),
                                          max_rewrites=16,intermediate_cap=None)
            nodes += macro['compute_units'] - 1
            stable_power_rewrites += macro['rewrites']
            stable_power_matcher_tests += macro['matcher_candidate_tests']
            if macro['solved']:
                return result(True,key,'middle_stable_power',macro=macro)
            done=admit_partial(key,depth,macro)
            if done:return done
        if use_stable_square and nodes < budget and any(word in DONOR_TRANSFORMS for word in state):
            stable_square_calls += 1
            macro = stable_square_collapse(state, budget=min(10000,budget-nodes+1))
            nodes += macro['rewrites']
            stable_square_rewrites += macro['rewrites']
            if macro['solved']:
                return result(True,key,'middle_stable_square',macro=macro)
            done=admit_partial(key,depth,macro)
            if done:return done
        if (use_primitive or use_christoffel) and nodes < budget:
            for donor in state:
                if ((use_primitive and one_occurrence_donor(donor)) or
                        (use_christoffel and is_christoffel_primitive_canonical(donor))):
                    macro = primitive_complete(state, budget=budget-nodes, donor_word=donor)
                    nodes += macro['work']
                    if macro['solved']:
                        return result(True,key,'middle_primitive',macro=macro,tail=macro['elementary_tail'])
                    break
        return None

    done=ball_probe(root)
    if done:return done
    while heap and nodes<budget:
        if full_splice_every:
            for queue in (heap,splice_heap):
                while queue and queue[0][2] in quota_closed:
                    heapq.heappop(queue);quota_stale_discards+=1
            if not heap:break
            force=bool(splice_heap) and (heap_pops+1)%full_splice_every==0
            _,depth,key=heapq.heappop(splice_heap if force else heap)
            forced_splice_pops+=force
            assert key not in quota_closed
            quota_closed.add(key)
        else:
            _,depth,key=heapq.heappop(heap)
        nodes+=1
        heap_pops+=1
        if use_full_splice and parent[key] is not None and parent[key][1]["kind"]=="elementary":
            full_splice_direct_pops+=1
        state=unpack(key)
        if probe_when=='pop' or key==root:
            done=complete(state,key,depth)
            if done:return done
            if nodes>=budget:break
        a,b=_arrs(key)
        expansion_cap=cap if cap is not None else sum(map(len,state))
        blob,offsets,lengths,segs,scores,_,_,moves,count=expand_and_score_h(
            a,b,expansion_cap,True,upto,weights,True,True)
        if whitehead:adjust_scores(blob,offsets[:count],lengths,scores,w_weight)
        raw=blob.tobytes()
        for i in range(count):
            o=int(offsets[i])
            child=raw[o:o+int(lengths[i])]
            if child in parent:continue
            parent[child]=key,{'kind':'substitution','move':'_'.join(str(int(v)) for v in moves[i])}
            generated_unique+=1
            child_state=unpack(child)
            total=sum(map(len,child_state));largest=max(map(len,child_state))
            max_seen=max(max_seen,largest)
            if (total,largest,child)<(best_total,best_max,best):
                best,best_total,best_max=child,total,largest
            done=ball_probe(child)
            if done:return done
            if probe_when=='generated':
                done=complete(child_state,child,depth+1)
                if done:return done
                if nodes>=budget:break
            score = with_escape(child, child_state, float(scores[i]))
            heapq.heappush(heap,(score,depth+1,child))
        if nodes>=budget:break
        if arm=='aut_edges':
            for transform in NIELSEN:
                basis_evaluations+=1
                nxt=apply_pair(state,transform)
                if cap is not None and max(map(len,nxt))>cap:continue
                child=pack(nxt)
                if child in parent:continue
                parent[child]=key,{'kind':'automorphism','images':transform}
                generated_unique+=1
                total=sum(map(len,nxt));largest=max(map(len,nxt))
                max_seen=max(max_seen,largest)
                if (total,largest,child)<(best_total,best_max,best):
                    best,best_total,best_max=child,total,largest
                done=ball_probe(child)
                if done:return done
                if probe_when=='generated':
                    done=complete(nxt,child,depth+1)
                    if done:return done
                    if nodes>=budget:break
                base_score=score_key(np.frombuffer(child,dtype=np.uint8),whitehead,w_weight,s_weight,mk_weight)
                score=with_escape(child,nxt,base_score)
                heapq.heappush(heap,(score,depth+1,child))
        if (use_commutator or use_full_splice) and nodes<budget:
            import time
            if use_commutator:
                from research.supermoves_20260908.commutator_edges import neighbors
            else:
                from research.supermoves_20260908.full_splice_screen import children
            nodes+=1
            started,cpu_started=time.perf_counter(),time.process_time()
            if use_commutator:
                candidates=list(neighbors(state))
            else:
                candidates=[(nxt,step) for nxt,step,_raw in children(state)]
            elapsed_wall=time.perf_counter()-started
            elapsed_cpu=time.process_time()-cpu_started
            if use_commutator:
                commutator_blocks+=1
                commutator_wall+=elapsed_wall
                commutator_cpu+=elapsed_cpu
                commutator_attempts+=len(candidates)
                admit_edges=commutator_admit
            else:
                full_splice_blocks+=1
                full_splice_wall+=elapsed_wall
                full_splice_cpu+=elapsed_cpu
                full_splice_attempts+=len(candidates)
                full_splice_potential_moves+=sum(len(step['moves']) for _,step in candidates)
                admit_edges=full_splice_admit
            if not admit_edges:
                continue
            for nxt,step in candidates:
                if use_commutator:
                    commutator_processed+=1
                else:
                    full_splice_processed+=1
                if cap is not None and max(map(len,nxt))>cap:
                    if use_commutator:
                        commutator_cap_rejects+=1
                    else:
                        full_splice_cap_rejects+=1
                    continue
                child=pack(nxt)
                if child in parent:
                    if use_commutator:
                        commutator_duplicates+=1
                    else:
                        full_splice_duplicates+=1
                    continue
                parent[child]=key,step
                generated_unique+=1
                if use_commutator:
                    commutator_admitted+=1
                else:
                    full_splice_admitted+=1
                total=sum(map(len,nxt));largest=max(map(len,nxt))
                max_seen=max(max_seen,largest)
                if (total,largest,child)<(best_total,best_max,best):
                    best,best_total,best_max=child,total,largest
                done=ball_probe(child)
                if done:return done
                if probe_when=='generated':
                    done=complete(nxt,child,depth+1)
                    if done:return done
                    if nodes>=budget:break
                base_score=score_key(np.frombuffer(child,dtype=np.uint8),whitehead,w_weight,s_weight,mk_weight)
                score=with_escape(child,nxt,base_score)
                heapq.heappush(heap,(score,depth+1,child))
                if full_splice_every:
                    heapq.heappush(splice_heap,(score,depth+1,child))
    return result()
