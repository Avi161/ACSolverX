"""The frozen AC19 cascade with a backward-ball terminal, plus two knobs.

This module is a copy of ``research/supermoves_20260908/final_policy.py`` with
``root_router.search``'s routing folded in; the frozen modules are left
untouched so they stay the comparison implementation.  Three things are added.

1. THE BALL TERMINAL (always on when a table is installed).
   Every state the cascade creates is looked up in the exact backward ball
   ``B(cap)`` (``backward_table.build``): the canonical root, every donor
   transport state, and -- through ``plain_search_ball`` and
   ``mid_search_ball`` -- every substitution child, automorphism child,
   macro-admitted partial state and escape-continuation state.  A hit ends the
   cascade with ``solved=True`` and the certificate
   ``forward mixed path + the stored substitution tail down to ('Y', 'X')``.

   DOMINANCE.  With ``force_arm=None`` and ``certified_overrun=False`` -- the
   settings the ``frozen_ball*`` policies use -- this cascade DOMINATES the
   frozen one: for every row the frozen policy solves at N units, this policy
   solves at <= N units.  The argument is a lockstep one.  Stage order, stage
   caps, every gate, every charge and every heap ordering are the frozen code
   verbatim; a ball lookup charges nothing and changes no ordering.  So the two
   runs agree instruction for instruction until the first hit.  A hit ends the
   run immediately with ``solved=True`` and with the ``charged``/``nodes``
   counter at its current value; because that counter never decreases along an
   execution and the frozen run can only return at the same point or later,
   the ball run's total is <= the frozen run's.  The trivial pair
   ``canon_pair('x', 'y') == ('Y', 'X')`` is itself in the table at depth 0 and
   is the only canonical state the frozen terminal test accepts, so every
   frozen solve has a matching hit at a point no later.  Finally, an earlier
   finish in an earlier stage only ever leaves a LARGER allowance to the later
   stages (``limit-charged``, ``budget-charged``, ``budget-charged-plain``),
   never a smaller one, so no later stage can be starved by the addition.

2. ``force_arm`` (default ``None``): which arm stage 3 runs.
   ``None`` keeps ``root_router``'s routing feature exactly -- ``'s20'`` with
   ``bs_escape_weight=4.`` when the stalled-BS feature fires, else
   ``'aut_edges'`` with the bounded high-core escape.  ``'s20'`` forces the
   ordinary route (T weight 4, no high-core escape, exactly as the router
   configures it) and ``'aut_edges'`` forces the generator route
   (``w_weight=1.5``, no T weight, high-core escape as the router configures
   it).  The routing feature is still computed and reported either way; it is
   uncharged in the frozen code and stays uncharged here.  Forcing an arm is
   NOT covered by the dominance argument -- it changes the ordering.

3. ``use_stable_power`` (default ``False``): pass ``use_stable_power=True``
   into every ``mid_search_ball.mixed_search`` the cascade runs -- the stage-1
   terminal subsearch, the stage-3 incumbent search, and the bounded escape
   continuation inside it.  ``stable_power.canonical_donor_gate`` fires on 11
   of the 102 dev rows; its compiler solves ``ac19_64188`` in 32 units and
   fails at 1 unit (``pinch_stalled``) on the other ten, so it is a cheap
   proved gate.  It charges units the frozen cascade does not charge, so it is
   off in every ``frozen_ball*`` policy and NOT covered by the dominance
   argument.

4. ``certified_overrun`` (default ``False``): let an accepted BS certificate
   finish even when it costs more than the stage-1 cap.
   When ``DONOR_NORMALIZED_BS.inspect`` reports ``bs_preflight`` status
   ``'accept'`` at a donor endpoint, ``consecutive_bs.collapse`` is a compiler
   that is guaranteed to terminate in a solve; only its rewrite count is
   unknown in advance, and that count is charged against the 250-unit stage-1
   cap through ``mid_search``'s macro accounting.  Row ``ac19_109``
   (``('YXXyx', 'YYYYYYYYXyyyyyyyx')``) is the worked example: preflight
   accepts with 7 pinches and base exponent 127, the collapse needs 256
   rewrites, stage 1 had 246 units left, so the frozen cascade drops the
   certificate on the floor and then spends its 750 plain units failing.
   With ``certified_overrun=True`` the collapse is run directly on the
   endpoint state with ``budget=min(10000, budget-charged)`` -- the whole
   remaining ROW allowance rather than the remaining STAGE allowance -- before
   the stage-1 terminal subsearch, and its ``rewrites`` are charged in full
   whether it succeeds or fails (the same unit ``mid_search`` charges for a
   ``collapse_bs`` macro).  A failure therefore burns budget the frozen policy
   would not have burned, so ``certified_overrun=True`` is NOT covered by the
   dominance argument either.  It is off in every ``frozen_ball*`` policy and
   on only in the explicitly named ``*_cc`` variants.
"""
import time

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, canon_rel
from experiments.search.heuristic_1k import pack
from research.residual_20260909.backward_table import tail as ball_tail
from research.residual_20260909.mid_search_ball import bs_escape_feature, mixed_search
from research.residual_20260909.plain_search_ball import mixed_search as plain_search
from research.supermoves_20260908.consecutive_bs import collapse as bs_collapse
from research.supermoves_20260908.DONOR_NORMALIZED_BS import inspect
from research.supermoves_20260908.strict_donor_route_fast import match

_UNSET = object()
_TABLE = None

ARMS = (None, 's20', 'aut_edges')


def set_table(table):
    """Install the module-level backward ball for this module and both searches."""
    global _TABLE
    _TABLE = table
    return table


def get_table():
    return _TABLE


def _resolve(table):
    return _TABLE if table is _UNSET else table


def incumbent(pair, budget, table, force_arm=None, use_high_core_escape=True,
              use_stable_power=False):
    """``root_router.search`` with the ball-aware mid search and ``force_arm``.

    Identical to ``research/supermoves_20260908/root_router.py`` at
    ``force_arm=None``: the same routing feature, the same arm, the same
    weights, the same bounded high-core escape, the same reported keys.
    """
    if force_arm not in ARMS:
        raise ValueError(f'force_arm must be one of {ARMS}')
    started = time.perf_counter()
    cpu_started = time.process_time()
    root = canon_pair(*pair)
    value, check = bs_escape_feature(root)
    ordinary = value > 0 if force_arm is None else force_arm == 's20'
    routing_cpu = time.process_time() - cpu_started
    routing_wall = time.perf_counter() - started
    extra = dict(bs_escape_macro_budget=300, bs_escape_macro_min_stable=7) \
        if use_high_core_escape and not ordinary else {}
    result = mixed_search(
        pair, 's20' if ordinary else 'aut_edges', budget=budget, cap=None,
        w_weight=1.5, s_weight=20., mk_weight=2., use_bs=True,
        general_bs=True, use_two_block=True, probe_when='generated',
        use_bs_preflight=True, bs_escape_weight=4. if ordinary else 0.,
        table=table, use_stable_power=use_stable_power, **extra,
    )
    result.update(
        route='ordinary_bs_escape' if ordinary else 's20_generator',
        routing_feature=value, routing_check=check,
        routing_wall=routing_wall, routing_cpu=routing_cpu,
        forced_arm=force_arm,
    )
    if use_high_core_escape:
        result['high_core_escape_enabled'] = not ordinary
    return result


def search(pair, budget=1000, prepass_cap=250, plain_prefix=872, force_arm=None,
           certified_overrun=False, use_stable_power=False, table=_UNSET):
    """Fixed donor prepass, plain S20 prefix, incumbent restart -- ball-aware."""
    if type(budget) is not int or budget < 1:
        raise ValueError('budget must be positive integer')
    if type(prepass_cap) is not int or prepass_cap < 0:
        raise ValueError('prepass_cap must be nonnegative integer')
    if type(plain_prefix) is not int or plain_prefix < 0:
        raise ValueError('plain_prefix must be nonnegative integer')
    if force_arm not in ARMS:
        raise ValueError(f'force_arm must be one of {ARMS}')
    if not isinstance(certified_overrun, bool):
        raise ValueError('certified_overrun must be boolean')
    if not isinstance(use_stable_power, bool):
        raise ValueError('use_stable_power must be boolean')
    table = _resolve(table)
    started, cpu = time.perf_counter(), time.process_time()
    root = list(canon_pair(*pair))
    limit = min(prepass_cap, max(0, budget - 1))
    charged = 0
    attempts = []
    result = None
    ball_lookups = 0
    ball_hit = False
    ball_depth = 0

    def ball_finish(states, steps, charges, route):
        """A hit on ``states[-1]``: splice the stored substitution tail."""
        key = pack(tuple(states[-1]))
        tail_states, tail_steps = ball_tail(table, key)
        return dict(solved=True, nodes_explored=charges,
                    states=[list(word) for word in states] + tail_states[1:],
                    steps=list(steps) + tail_steps,
                    best_state=['Y', 'X'], min_total_length_seen=2,
                    min_max_relator_length_seen=1, policy_route=route,
                    ball_hit=True, ball_depth=table[key][0])

    def probe(states, steps, charges, route):
        nonlocal ball_lookups, ball_hit, ball_depth
        if table is None:
            return None
        ball_lookups += 1
        key = pack(tuple(states[-1]))
        if key not in table:
            return None
        ball_hit = True
        ball_depth = table[key][0]
        return ball_finish(states, steps, charges, route)

    result = probe([root], [], 0, 'ball_root')
    if result is None:
        for index, donor in enumerate(root):
            if charged >= limit:
                break
            route = match(donor, evaluation_cap=min(64, limit - charged))
            charged += route['input_analysis']['evaluations']
            attempt = dict(donor_index=index, recognition=route)
            attempts.append(attempt)
            if route['status'] != 'match':
                continue
            if charged + len(route['maps']) >= limit:
                attempt['status'] = 'prepass_limit'
                continue
            states = [root]
            steps = []
            limited = False
            for image in route['maps']:
                if sum(len(image[c.lower()]) for word in states[-1] for c in word) > 100000:
                    limited = True
                    attempt['status'] = 'image_symbol_limit'
                    break
                states.append(list(apply_pair(states[-1], image)))
                steps.append(dict(kind='automorphism', images=image))
                charged += 1
                result = probe(states, steps, charged, 'strict_donor')
                if result is not None:
                    break
            if result is not None:
                break
            if limited:
                continue
            assert canon_rel(route['template_word']) in states[-1]
            gates, symbol_work = inspect(states[-1])
            attempt.update(gates=gates, gate_symbol_work=symbol_work)
            if not (gates['two_block'] or gates['one_occurrence_relators']
                    or (gates['bs_preflight'] or {}).get('status') == 'accept'):
                continue
            if (certified_overrun and (gates['bs_preflight'] or {}).get('status') == 'accept'
                    and budget - charged >= 1):
                macro = bs_collapse(states[-1], budget=min(10000, budget - charged),
                                    intermediate_cap=None)
                charged += macro['rewrites']
                attempt.update(certified_overrun_rewrites=macro['rewrites'],
                               certified_overrun_solved=macro['solved'],
                               certified_overrun_reason=macro['reason'])
                if macro['solved']:
                    result = dict(solved=True, nodes_explored=charged,
                                  states=states + macro['states'][1:],
                                  steps=steps + macro['steps'],
                                  best_state=['Y', 'X'], min_total_length_seen=2,
                                  min_max_relator_length_seen=1,
                                  policy_route='strict_donor', winner='certified_overrun')
                    break
            tail = mixed_search(states[-1], 's20', budget=limit - charged, cap=None,
                                use_bs=True, general_bs=True, use_two_block=True,
                                use_primitive=True, use_bs_preflight=True, table=table,
                                use_stable_power=use_stable_power)
            charged += tail['nodes_explored']
            ball_lookups += tail.get('ball_lookups', 0)
            attempt.update(terminal_solved=tail['solved'], terminal_charges=tail['nodes_explored'])
            if tail['solved']:
                ball_hit = ball_hit or bool(tail.get('ball_hit'))
                ball_depth = max(ball_depth, int(tail.get('ball_depth') or 0))
                result = dict(tail)
                result.update(states=states + tail['states'][1:], steps=steps + tail['steps'],
                              nodes_explored=charged, policy_route='strict_donor')
                break
    prepass_wall, prepass_cpu = time.perf_counter() - started, time.process_time() - cpu
    plain_charges = 0
    plain_wall, plain_cpu = 0., 0.
    if result is None and plain_prefix:
        t, c = time.perf_counter(), time.process_time()
        plain = plain_search(pair, 's20', budget=min(plain_prefix, budget - charged), cap=None,
                             s_weight=20., mk_weight=2., w_weight=0., table=table)
        plain_charges = plain['nodes_explored']
        ball_lookups += plain.get('ball_lookups', 0)
        plain_wall, plain_cpu = time.perf_counter() - t, time.process_time() - c
        if plain['solved'] or charged + plain_charges >= budget:
            ball_hit = ball_hit or bool(plain.get('ball_hit'))
            ball_depth = max(ball_depth, int(plain.get('ball_depth') or 0))
            result = dict(plain)
            result['nodes_explored'] += charged
            result['policy_route'] = 'plain_s20'
    if result is None:
        fallback = incumbent(pair, budget - charged - plain_charges, table,
                             force_arm=force_arm, use_high_core_escape=True,
                             use_stable_power=use_stable_power)
        ball_lookups += fallback.get('ball_lookups', 0)
        ball_hit = ball_hit or bool(fallback.get('ball_hit'))
        ball_depth = max(ball_depth, int(fallback.get('ball_depth') or 0))
        result = dict(fallback)
        result['fallback_nodes'] = result['nodes_explored']
        result['nodes_explored'] += charged + plain_charges
        result['policy_route'] = 'incumbent_restart'
    assert result['nodes_explored'] <= budget
    result.update(plain_prefix=plain_prefix, plain_charges=plain_charges, plain_wall=plain_wall,
                  plain_cpu=plain_cpu, prepass_charges=charged, prepass_cap=limit,
                  prepass_attempts=attempts, prepass_wall=prepass_wall, prepass_cpu=prepass_cpu,
                  policy_wall=time.perf_counter() - started,
                  policy_cpu=time.process_time() - cpu,
                  ball_lookups=ball_lookups, ball_hit=ball_hit, ball_depth=ball_depth,
                  ball_enabled=table is not None, ball_size=len(table) if table else 0,
                  force_arm=force_arm, certified_overrun=certified_overrun,
                  use_stable_power=use_stable_power,
                  work_unit_note='Image evaluations + accepted maps + terminal/fallback search '
                                 'charges; not calibrated equivalent pops. Gate symbol work '
                                 'separate. Backward-ball lookups are free and counted in '
                                 'ball_lookups.')
    return result
