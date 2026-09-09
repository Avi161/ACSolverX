"""Registry of search policies for the residual-campaign experiment harness.

Every policy is a callable ``policy(pair, budget) -> result`` returning the
same result contract as ``research.supermoves_20260908.final_policy.search``:
a ``dict`` carrying at least

    solved                  bool
    nodes_explored          int, charged work units spent (<= budget)
    states                  list[list[str, str]], the mixed certificate path
    steps                   list[dict], one entry per states transition
    elementary_tail         optional list, a packed terminal tail (two_block)
    best_state              list[str, str], best pair seen (whether solved or not)
    min_total_length_seen   int
    policy_route            str, which underlying route/arm actually ran

``harness.py`` only ever calls ``REGISTRY[name](pair, budget)`` and reads
this contract; it does not know anything about how a given policy is built.

Register new candidate policies with the ``@policy(name)`` decorator below --
nothing else in the harness needs to change to pick them up.
"""
import time

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, canon_rel
from research.supermoves_20260908 import final_policy
from research.supermoves_20260908 import mid_search
from research.supermoves_20260908 import plain_search_fast
from research.supermoves_20260908 import root_router
from research.supermoves_20260908.DONOR_NORMALIZED_BS import inspect as donor_inspect
from research.supermoves_20260908.strict_donor_route_fast import match as donor_match

REGISTRY = {}


def policy(name):
    """Decorator: register the wrapped callable in REGISTRY under ``name``.

    Raises if ``name`` is already taken, so two policies can never silently
    shadow each other.
    """
    def register(fn):
        if name in REGISTRY:
            raise ValueError(f'policy {name!r} is already registered')
        fn.policy_name = name
        REGISTRY[name] = fn
        return fn
    return register


def _total_length(state):
    return sum(len(word) for word in state)


# --------------------------------------------------------------------------
# 'frozen' -- the published census policy, unchanged.
# --------------------------------------------------------------------------
@policy('frozen')
def frozen(pair, budget):
    """``final_policy.search`` exactly as run for the AC19 census: strict
    donor prepass (<=250 units) -> plain S20 prefix (<=872 units) ->
    incumbent restart with whatever budget remains."""
    return dict(final_policy.search(pair, budget=budget))


# --------------------------------------------------------------------------
# 'donor_only' -- stage 1 of final_policy.search, alone.
# --------------------------------------------------------------------------
@policy('donor_only')
def donor_only(pair, budget):
    """Only the strict-donor route (final_policy.search's stage 1), with
    prepass_cap=budget instead of the frozen policy's 250.

    This is deliberately NOT the same thing as calling
    ``final_policy.search(pair, budget=budget, plain_prefix=0)``: that call
    still falls through unconditionally to the incumbent restart when the
    donor stage fails, because the incumbent call in final_policy.search is
    gated on ``result is None``, not on ``plain_prefix`` (see
    ``research/supermoves_20260908/final_policy.py`` lines 57-61 -- the
    ``if result is None and plain_prefix`` guard only skips the *plain*
    stage). So stage 1 is replicated here verbatim (same helper functions,
    same gates, same terminal mixed_search call) and simply stops -- no
    plain-S20 stage, no incumbent restart -- returning unsolved with the
    prepass charge as nodes_explored if the donor route never reaches an
    accepted terminal.

    Across failed donor attempts we still track the shortest total-length
    transported pair seen, and report it as ``best_state`` /
    ``min_total_length_seen``, so an unsolved result is still informative.
    """
    if type(budget) is not int or budget < 1:
        raise ValueError('budget must be positive integer')
    prepass_cap = budget
    root = list(canon_pair(*pair))
    limit = min(prepass_cap, max(0, budget - 1))
    charged = 0
    attempts = []
    result = None
    best_state = root
    best_total = _total_length(root)
    for index, donor in enumerate(root):
        if charged >= limit:
            break
        route = donor_match(donor, evaluation_cap=min(64, limit - charged))
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
        if limited:
            continue
        assert canon_rel(route['template_word']) in states[-1]
        if _total_length(states[-1]) < best_total:
            best_state, best_total = states[-1], _total_length(states[-1])
        gates, symbol_work = donor_inspect(states[-1])
        attempt.update(gates=gates, gate_symbol_work=symbol_work)
        if not (gates['two_block'] or gates['one_occurrence_relators']
                or (gates['bs_preflight'] or {}).get('status') == 'accept'):
            continue
        tail = mid_search.mixed_search(
            states[-1], 's20', budget=limit - charged, cap=None, use_bs=True,
            general_bs=True, use_two_block=True, use_primitive=True, use_bs_preflight=True)
        charged += tail['nodes_explored']
        attempt.update(terminal_solved=tail['solved'], terminal_charges=tail['nodes_explored'])
        if _total_length(tail['best_state']) < best_total:
            best_state, best_total = tail['best_state'], _total_length(tail['best_state'])
        if tail['solved']:
            result = dict(tail)
            result.update(states=states + tail['states'][1:], steps=steps + tail['steps'],
                          nodes_explored=charged, policy_route='strict_donor')
            break
    if result is None:
        result = dict(solved=False, nodes_explored=charged, states=[], steps=[],
                      best_state=list(best_state), min_total_length_seen=best_total,
                      policy_route='donor_only_unsolved')
    result.setdefault('prepass_attempts', attempts)
    result.setdefault('prepass_cap', limit)
    return result


# --------------------------------------------------------------------------
# 'plain_s20' -- plain relator-substitution search alone, ordinary S20_MK2.
# --------------------------------------------------------------------------
@policy('plain_s20')
def plain_s20(pair, budget):
    """``plain_search_fast.mixed_search`` alone: ordinary relator
    substitutions only, no ambient Nielsen neighbors, no BS/two-block/
    primitive terminal macros -- pure ``L + 20*S + 2*MK`` best-first search."""
    result = dict(plain_search_fast.mixed_search(
        pair, 's20', budget=budget, cap=None, s_weight=20., mk_weight=2., w_weight=0.))
    result.setdefault('policy_route', 'plain_s20')
    return result


# --------------------------------------------------------------------------
# 'incumbent' -- the routed incumbent search alone, from the original input.
# --------------------------------------------------------------------------
@policy('incumbent')
def incumbent(pair, budget):
    """``root_router.search`` alone, with the bounded high-core BS escape
    enabled -- the same call final_policy.search makes for its stage-3
    fallback, but run here directly from the original (uncharged) input."""
    result = dict(root_router.search(pair, budget=budget, use_high_core_escape=True))
    result.setdefault('policy_route', result.get('route', 'incumbent'))
    return result


# --------------------------------------------------------------------------
# 'aut_edges_s20' -- the generator-move (Nielsen-neighbor) arm, unrouted.
# --------------------------------------------------------------------------
@policy('aut_edges_s20')
def aut_edges_s20(pair, budget):
    """``mid_search.mixed_search`` on the ``aut_edges`` arm: ordinary S20_MK2
    substitutions plus the four ambient Nielsen neighbors, with BS/two-block/
    preflight terminals, generated-time probing and two-block admission --
    always this arm, regardless of what root_router's routing feature would
    have chosen."""
    result = dict(mid_search.mixed_search(
        pair, 'aut_edges', budget=budget, cap=None, w_weight=1.5, s_weight=20.,
        mk_weight=2., use_bs=True, general_bs=True, use_two_block=True,
        probe_when='generated', use_bs_preflight=True))
    result.setdefault('policy_route', 'aut_edges_s20')
    return result


# --------------------------------------------------------------------------
# 'ordinary_T' -- the ordinary-substitution-plus-T arm, unrouted.
# --------------------------------------------------------------------------
@policy('ordinary_T')
def ordinary_T(pair, budget):
    """``mid_search.mixed_search`` on the ``s20`` arm with the donor-relative
    ``T`` feature weighted in (``bs_escape_weight=4.``) -- the ordinary
    substitution-only arm augmented with the stalled-BS bonus, always run
    regardless of the routing feature that would normally pick between this
    and the generator-move arm."""
    result = dict(mid_search.mixed_search(
        pair, 's20', budget=budget, cap=None, w_weight=1.5, s_weight=20.,
        mk_weight=2., use_bs=True, general_bs=True, use_two_block=True,
        probe_when='generated', use_bs_preflight=True, bs_escape_weight=4.))
    result.setdefault('policy_route', 'ordinary_T')
    return result


# --------------------------------------------------------------------------
# 'frozen_reallocated' -- donor stage then incumbent gets the whole rest.
# --------------------------------------------------------------------------
@policy('frozen_reallocated')
def frozen_reallocated(pair, budget):
    """``final_policy.search`` with the plain-S20 stage skipped
    (``plain_prefix=0``) so the incumbent restart inherits the entire budget
    the plain stage would otherwise have used, keeping the 250-unit donor
    prepass. ``final_policy.search`` accepts ``plain_prefix=0`` directly (see
    ``if result is None and plain_prefix:`` in final_policy.py -- 0 is
    falsy, so the plain stage is skipped and the incumbent call, which is
    unconditional on ``result is None``, receives the freed-up budget)."""
    return dict(final_policy.search(pair, budget=budget, prepass_cap=250, plain_prefix=0))


# ==========================================================================
# Backward-ball policies (research/residual_20260909/backward_table.py).
#
# Each of these is the frozen cascade with one addition: every state the
# cascade creates is looked up in the exact backward ball B(cap), and a hit
# ends the row with the stored substitution (and, for an aut-closed table,
# automorphism) tail spliced onto the forward path.  Lookups are free; they
# are reported as ``ball_lookups`` and never counted in ``nodes_explored``.
# With force_arm=None and certified_overrun=False these DOMINATE 'frozen':
# same ordering, same charges, and the trivial pair is in the table, so any
# row 'frozen' solves at N units is solved here at <= N units.
#
# The table is an OFFLINE precomputation.  Its build cost is outside the
# per-row budget; see BACKWARD_TABLE.md.
# ==========================================================================
from pathlib import Path as _Path

from research.residual_20260909 import backward_table as _backward_table
from research.residual_20260909 import final_policy_ball as _final_policy_ball
from research.residual_20260909 import mid_search_ball as _mid_search_ball

TABLES = _Path(__file__).resolve().parent / 'tables'
_BALL_TABLES = {}


def ball_table(stem):
    """Load ``tables/<stem>.pkl`` once per process, sha256-checked against its
    manifest by ``backward_table.load``."""
    if stem not in _BALL_TABLES:
        _BALL_TABLES[stem] = _backward_table.load(TABLES / f'{stem}.pkl')
    return _BALL_TABLES[stem]


def make_policy(cap, prepass_cap=250, plain_prefix=872, force_arm=None,
                certified_overrun=False, use_stable_power=False, use_bs_demote=False,
                aut=False, name=None):
    """A complete ball cascade as a ``policy(pair, budget)`` callable.

    ``cap`` picks the table (``tables/ball_cap<NN>[_aut].pkl``, loaded lazily
    once); ``prepass_cap`` / ``plain_prefix`` / ``force_arm`` /
    ``certified_overrun`` are ``final_policy_ball.search``'s knobs.  Pass
    ``name`` to register the result in ``REGISTRY`` as well as return it.
    """
    stem = f'ball_cap{cap:02d}' + ('_aut' if aut else '')

    def run(pair, budget):
        result = dict(_final_policy_ball.search(
            pair, budget=budget, prepass_cap=prepass_cap, plain_prefix=plain_prefix,
            force_arm=force_arm, certified_overrun=certified_overrun,
            use_stable_power=use_stable_power, use_bs_demote=use_bs_demote,
            table=ball_table(stem)))
        result['ball_table'] = stem
        return result

    run.__doc__ = (f'final_policy_ball.search with the {stem} backward ball, '
                   f'prepass_cap={prepass_cap}, plain_prefix={plain_prefix}, '
                   f'force_arm={force_arm!r}, certified_overrun={certified_overrun}, '
                   f'use_stable_power={use_stable_power}, '
                   f'use_bs_demote={use_bs_demote}.')
    if name is not None:
        run.__name__ = name
        policy(name)(run)
    return run


make_policy(8, name='frozen_ball08')
make_policy(10, name='frozen_ball10')
make_policy(12, name='frozen_ball12')
make_policy(10, aut=True, name='frozen_ball10aut')
make_policy(10, certified_overrun=True, name='frozen_ball10_cc')


@policy('aut_edges_ball10')
def aut_edges_ball10(pair, budget):
    """``mid_search_ball.mixed_search`` on the ``aut_edges`` arm with the
    cap-10 backward ball: the 'aut_edges_s20' policy's exact configuration
    plus ``w_weight=1.5`` and the ball terminal at every generated state."""
    result = dict(_mid_search_ball.mixed_search(
        pair, 'aut_edges', budget=budget, cap=None, w_weight=1.5, s_weight=20.,
        mk_weight=2., use_bs=True, general_bs=True, use_two_block=True,
        probe_when='generated', use_bs_preflight=True, table=ball_table('ball_cap10')))
    result.setdefault('policy_route', 'aut_edges_ball10')
    result['ball_table'] = 'ball_cap10'
    return result


# --------------------------------------------------------------------------
# K1..K5 -- the pre-registered candidate cascades of NOTES.md, on the
# automorphism-closed cap-10 table.  K0 is 'frozen'.  Only K1 is covered by
# the dominance argument; K2..K5 charge units the frozen cascade does not
# (certified overrun, stable-power gate) or reorder stage 3 (forced arm).
# --------------------------------------------------------------------------
make_policy(10, aut=True, name='K1')
make_policy(10, aut=True, certified_overrun=True, use_stable_power=True, name='K2')
make_policy(10, aut=True, plain_prefix=300, certified_overrun=True, use_stable_power=True,
            name='K3')
make_policy(10, aut=True, plain_prefix=0, certified_overrun=True, use_stable_power=True,
            name='K4')
make_policy(10, aut=True, plain_prefix=0, certified_overrun=True, use_stable_power=True,
            force_arm='aut_edges', name='K5')
make_policy(12, aut=True, name='frozen_ball12aut')


# --------------------------------------------------------------------------
# The revised candidate set.  The stable-power gate is dropped: on
# regression60 it lost ac19_28267, which 'frozen' and K1 both solve at exactly
# 973 units, because its charged failed attempts pushed the row past 1,000.
# K1 stays the zero-loss reference (ball terminal only, frozen allocation, no
# charged addition at all).  K2'..K5' add the certified consecutive-BS overrun
# and the free BS-DEMOTE root macro, and reallocate stages.  Each is offered
# on both automorphism-closed tables.
# --------------------------------------------------------------------------
def _register_candidates(cap, suffix):
    make_policy(cap, aut=True, name=f'K1{suffix}')
    make_policy(cap, aut=True, certified_overrun=True, use_bs_demote=True,
                name=f'K2p{suffix}')
    make_policy(cap, aut=True, plain_prefix=300, certified_overrun=True,
                use_bs_demote=True, name=f'K3p{suffix}')
    make_policy(cap, aut=True, plain_prefix=0, certified_overrun=True,
                use_bs_demote=True, name=f'K4p{suffix}')
    make_policy(cap, aut=True, plain_prefix=0, certified_overrun=True,
                use_bs_demote=True, force_arm='aut_edges', name=f'K5p{suffix}')


_register_candidates(10, '_c10aut')
_register_candidates(12, '_c12aut')
