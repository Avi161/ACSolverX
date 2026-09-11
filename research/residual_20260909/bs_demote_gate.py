"""BS-DEMOTE / BS-NORMALISE packaged as a drop-in cascade gate.

The rule, its proof and its verification live in
``research/residual_20260909/theory/STALLED_BS_THEORY.md`` and
``theory/verify_stalled_bs_examples.py``; this module is the policy-facing
wrapper with an explicit work contract.

Contract
--------
``recognize(pair)``
    ``O(|W|)`` pure recognition.  Returns the class label ``(m, alpha, beta)``
    of a *stalled* consecutive-BS pair whose companion Britton-reduces to three
    stable letters, or ``None``.  It emits nothing and charges nothing.
    ``complete`` succeeds exactly on the labels with ``demotable(label)``.

``complete(pair, budget)``
    Same result contract as
    ``research/supermoves_20260908/primitive_completion.complete``:

    * success  -> ``dict(solved=True, work, states, steps, elementary_tail)``
    * failure  -> ``dict(solved=False, work, reason)``

    ``states[0] == list(canon_pair(*pair))``, ``len(states) == len(steps)+1``,
    every step is ``{'kind': 'substitution', 'move': 't_s_k1_k2'}`` replayable
    by ``experiments.equivalence_classes.lib.words.replay_move``, and
    ``elementary_tail`` is ``None`` (everything is expressed as engine
    substitutions, which ``certificate_decoder_compact_moves.decode_elementary``
    already handles).  The certificate decodes and replays to ``['x', 'y']``.

Recommended wiring
------------------
``recognize`` is free (it emits nothing and charges nothing), so a cascade
should use it as the admission test and only enter ``complete`` when the label
is demotable::

    label = recognize(state)
    if demotable(label):
        macro = complete(state, budget=budget - charged)
        charged += macro['work']

Wired that way the gate costs a row on which it does not fire exactly zero
charged units.  Calling ``complete`` unconditionally is also safe - it refuses
at 1 unit off the family and 2 units inside it - but that is 1-2 units of pure
overhead on every state.

Work charged
------------
1 for recognition; +1 for a failed applicability test (so every refusal costs
at most 2); then one unit per emitted engine substitution - the Britton pinch
carries, the normal-form transport carries, and every rewrite
``consecutive_bs.collapse`` emits.  ``complete`` never charges more than
``budget`` and never emits a move it cannot pay for: the whole cost
``2 + pinches + transport + 2**(m+1)`` is predicted before the first move.
"""
from __future__ import annotations

from experiments.equivalence_classes.lib.words import canon_pair, canon_rel, replay_move
from research.supermoves_20260908.bs_preflight import preflight
from research.supermoves_20260908.cheap_gates import bs_gate
from research.supermoves_20260908.consecutive_bs import collapse
from research.residual_20260909.theory.bs_normal_form import (
    britton_reduce, canonical_label, carry_solution, class_s3, core, reduce_plan,
    signs_gaps, transport_plan, unit_carry, word_from,
)

RECOGNITION_WORK = 1
REFUSAL_WORK = 2
DEMOTION_TARGETS = ((0, 1, -1), (0, -1, 1))


# ---------------------------------------------------------------------------
# recognition
# ---------------------------------------------------------------------------

def demotable(label):
    """True for the one stalled class per ``m`` that Rule BS-DEMOTE closes."""
    return label is not None and tuple(label[1:]) == (1, label[0] - 1)


def _oriented(pair):
    """Internal: (state, R, a, b, m, n, raw signs, raw gaps) or None."""
    state = tuple(canon_pair(*pair))
    found = core(state)
    if found is None:
        return None
    _index, a, b, m, n, R, W = found
    signs, gaps = signs_gaps(W, a, b)
    if abs(sum(signs)) != 1 or m < 2:
        return None
    return state, R, a, b, m, n, signs, gaps


def recognize(pair):
    """Class label of a stalled consecutive-BS pair with ``s_red == 3``.

    Returns ``(m, alpha, beta)`` or ``None``.  Cost is ``O(|W|)`` symbol work
    plus the integer Britton reduction; nothing is emitted and no AC move is
    constructed.  Recognition is invariant under rotation, inversion of either
    relator and relator swap because it consumes ``canon_pair`` output, and
    under the eight signed generator permutations because the label is the
    minimum over that orbit (STALLED_BS_THEORY.md Theorem 3.2).
    """
    oriented = _oriented(pair)
    if oriented is None:
        return None
    _state, _R, _a, _b, m, n, signs, gaps = oriented
    rsigns, rgaps = britton_reduce(signs, gaps, m, n)
    if len(rsigns) != 3:
        return None                      # pinchable (s=1) or a wider necklace
    return canonical_label(m, class_s3(rsigns, rgaps, m, n))


def predicted_work(pair):
    """Total units ``complete`` will charge, or ``None`` when it will refuse."""
    plan = _plan(pair)
    return None if plan is None else plan["predicted_work"]


# ---------------------------------------------------------------------------
# planning (no moves emitted, no units charged)
# ---------------------------------------------------------------------------

def _plan(pair):
    """Everything ``complete`` needs, computed without emitting a single move.

    ``None`` when the pair is not a stalled consecutive-BS pair with
    ``s_red == 3``; otherwise a dict whose ``transport`` is ``None`` when the
    class is outside ``(m, 1, m-1)``.
    """
    oriented = _oriented(pair)
    if oriented is None:
        return None
    state, R, a, b, m, n, signs, gaps = oriented
    pinches, rsigns, rgaps = reduce_plan(signs, gaps, m)
    if len(rsigns) != 3:
        return None
    eps = 1 if sum(rsigns) > 0 else -1
    start = next(i for i in range(3) if rsigns[i] == eps and rsigns[(i + 1) % 3] == eps)
    rsigns = rsigns[start:] + rsigns[:start]
    rgaps = rgaps[start:] + rgaps[:start]
    plan = {"state": state, "R": R, "a": a, "b": b, "m": m, "n": n,
            "signs": signs, "gaps": gaps, "pinches": pinches,
            "reduced_signs": rsigns, "reduced_gaps": tuple(rgaps), "eps": eps,
            "label": canonical_label(m, class_s3(rsigns, list(rgaps), m, n)),
            "target": None, "solution": None, "transport": None,
            "predicted_work": None}
    for target in DEMOTION_TARGETS:
        if carry_solution(m, eps, tuple(rgaps), target) is None:
            continue
        solution, transport = transport_plan(m, eps, tuple(rgaps), target)
        plan.update(target=target, solution=solution, transport=transport,
                    predicted_work=(REFUSAL_WORK + len(pinches) + len(transport)
                                    + (1 << (m + 1))))
        break
    return plan


# ---------------------------------------------------------------------------
# move emission
# ---------------------------------------------------------------------------

def _companion_move(state, donor, target_word):
    """The engine move on the companion of ``state`` giving ``target_word``.

    One unit carry is exactly one Definition 2.1 substitution on the companion
    (STALLED_BS_THEORY.md Lemma 2.1); this locates it and checks it with
    ``words.replay_move``, so an emitted step can never be wrong.
    """
    goal = canon_pair(target_word, donor)
    index = 0 if state[1] == donor else 1
    if state[index] == donor:                      # both relators equal donor
        index = 1 - index
    target = index + 1
    for jsign in (1, -1):
        for k1 in range(len(state[index])):
            for k2 in range(len(state[1 - index])):
                move = (target, jsign, k1, k2)
                if replay_move(state, move) == goal:
                    return move, goal
    return None, goal


def _shortest(value, modulus):
    """The representative of ``value`` mod ``modulus`` with least |.| (ties: +)."""
    low = value % modulus
    high = low - modulus
    return low if (abs(low), -low) <= (abs(high), -high) else high


class _Exhausted(Exception):
    pass


def complete(pair, budget=1000):
    """Rule BS-DEMOTE: certify a stalled consecutive-BS pair of class (m,1,m-1).

    See the module docstring for the result contract and the work charged.
    """
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 1:
        raise ValueError("budget must be a positive integer")
    root = list(canon_pair(*pair))
    work = RECOGNITION_WORK
    if budget < RECOGNITION_WORK:
        return {"solved": False, "work": 0, "reason": "budget"}
    plan = _plan(pair)
    if plan is None:
        return {"solved": False, "work": work, "reason": "not_recognized"}
    work = REFUSAL_WORK
    label = plan["label"]
    if plan["transport"] is None or not demotable(label):
        return {"solved": False, "work": min(work, budget),
                "reason": "class_not_demotable", "label": label}
    if plan["predicted_work"] > budget:
        return {"solved": False, "work": min(work, budget), "reason": "budget",
                "label": label, "predicted_work": plan["predicted_work"]}

    state = plan["state"]
    R, a, b, m = plan["R"], plan["a"], plan["b"], plan["m"]
    states, steps = [list(state)], []
    signs, gaps = list(plan["signs"]), list(plan["gaps"])

    def emit(signs, gaps, index, direction):
        nonlocal state, work
        signs, gaps = unit_carry(signs, gaps, index, direction, m)
        if work + 1 > budget:
            raise _Exhausted
        move, goal = _companion_move(state, R, canon_rel(word_from(signs, gaps, a, b)))
        if move is None:
            raise AssertionError("unit carry is not a single Definition 2.1 move")
        work += 1
        state = goal
        steps.append({"kind": "substitution", "move": "_".join(map(str, move))})
        states.append(list(state))
        return signs, gaps

    try:
        for index, direction in plan["pinches"]:
            signs, gaps = emit(signs, gaps, index, direction)
        signs, gaps = list(plan["reduced_signs"]), list(plan["reduced_gaps"])
        for index, direction in plan["transport"]:
            signs, gaps = emit(signs, gaps, index, direction)
    except _Exhausted:
        return {"solved": False, "work": work, "reason": "budget", "label": label}

    remaining = budget - work
    if remaining < 1:
        return {"solved": False, "work": work, "reason": "budget", "label": label}
    macro = collapse(state, budget=min(10_000, remaining + 1), intermediate_cap=None)
    work += macro["rewrites"]
    if not macro["solved"]:
        return {"solved": False, "work": min(work, budget),
                "reason": "collapse_" + macro["reason"], "label": label}
    states += [list(w) for w in macro["states"][1:]]
    steps += macro["steps"]
    assert len(states) == len(steps) + 1
    assert states[0] == root
    return {"solved": True, "work": work, "states": states, "steps": steps,
            "elementary_tail": None, "label": label,
            "pinch_carries": len(plan["pinches"]),
            "transport_carries": len(plan["transport"]),
            "collapse_rewrites": macro["rewrites"]}


# ---------------------------------------------------------------------------
# Rule BS-NORMALISE
# ---------------------------------------------------------------------------

def normalise(pair, budget=1000):
    """Carry a stalled ``s_red == 3`` companion onto its class normal form.

    Returns ``dict(applicable, work, states, steps, label, normal_state)``.
    The path is an ordinary AC prefix - concatenating it with a certificate for
    ``normal_state`` gives a certificate for ``pair`` - and the companion never
    gets longer, so this is a safe deduplicating preprocessing step: two rows
    with the same label reach the same ``normal_state`` up to one signed
    permutation of the generators (STALLED_BS_THEORY.md Theorem 3.2).
    """
    oriented = _oriented(pair)
    if oriented is None:
        return {"applicable": False, "work": RECOGNITION_WORK,
                "reason": "not_recognized"}
    state, R, a, b, m, n, signs, gaps = oriented
    pinches, rsigns, rgaps = reduce_plan(signs, gaps, m)
    if len(rsigns) != 3:
        return {"applicable": False, "work": REFUSAL_WORK,
                "reason": f"reduced_stable_letters_{len(rsigns)}"}
    eps = 1 if sum(rsigns) > 0 else -1
    start = next(i for i in range(3) if rsigns[i] == eps and rsigns[(i + 1) % 3] == eps)
    rsigns = rsigns[start:] + rsigns[:start]
    rgaps = rgaps[start:] + rgaps[:start]
    Mv, Mw = (m + 1, m) if eps == 1 else (m, m + 1)
    goal = (0, _shortest(rgaps[1], Mv), _shortest(rgaps[2], Mw))
    found = transport_plan(m, eps, tuple(rgaps), goal)
    if found is None:
        return {"applicable": False, "work": REFUSAL_WORK, "reason": "no_transport"}
    _solution, transport = found
    work = REFUSAL_WORK
    if work + len(pinches) + len(transport) > budget:
        return {"applicable": False, "work": min(work, budget), "reason": "budget"}
    states, steps = [list(state)], []
    cursor = state

    def step_through(signs, gaps, plan):
        nonlocal cursor, work
        for index, direction in plan:
            signs, gaps = unit_carry(signs, gaps, index, direction, m)
            move, target = _companion_move(cursor, R, canon_rel(word_from(signs, gaps, a, b)))
            if move is None:
                raise AssertionError("unit carry is not a single Definition 2.1 move")
            work += 1
            cursor = target
            steps.append({"kind": "substitution", "move": "_".join(map(str, move))})
            states.append(list(cursor))
        return signs, gaps

    step_through(list(signs), list(gaps), pinches)
    step_through(list(rsigns), list(rgaps), transport)
    return {"applicable": True, "work": work, "states": states, "steps": steps,
            "label": canonical_label(m, class_s3(rsigns, list(rgaps), m, n)),
            "normal_state": list(cursor)}


# ---------------------------------------------------------------------------
# recommendation 2: skip provably doomed BS recognition
# ---------------------------------------------------------------------------

def is_doomed_bs_state(root_pair, state, w_only=True):
    """True when ``bs_preflight`` on ``state`` provably cannot accept.

    Hypothesis (the caller must guarantee ``w_only``): ``state`` was reached
    from ``root_pair`` by moves that never changed the root's consecutive-BS
    relator ``R0`` - i.e. every substitution targeted the companion and no
    ambient automorphism was applied.  Engines can carry that as one inherited
    boolean per node, cleared whenever a move targets the relator equal to
    ``R0`` or an automorphism is applied.  With ``w_only=False`` the function
    makes no claim and returns ``False``.

    Proof sketch.  Under the hypothesis the companion of ``state`` is
    ``g^-1 W_0 g . (product of conjugates of R0^{+/-1})``, so its image in
    ``G = <a,b | R0> = BS(m, m+1)`` is a conjugate of the image of ``W_0``.
    ``G`` is an HNN extension of ``<a> = Z`` with associated subgroups
    ``<a^m>``, ``<a^(m+1)>`` and stable letter ``b``; by Britton's lemma and the
    HNN conjugacy criterion, the number of stable letters in a cyclically
    Britton-reduced representative is a conjugacy invariant.  ``bs_preflight``
    is exactly that reduction, and it accepts only at one stable letter.  So if
    it rejects at the root with ``s_red > 1`` it rejects here.  Without the
    hypothesis the claim is false: a path may modify ``R0`` and later recreate
    it beside a pinchable companion.  (STALLED_BS_THEORY.md Theorem 2.2.)
    """
    if not w_only:
        return False
    root = tuple(canon_pair(*root_pair))
    gate = bs_gate(root, general=True)
    if gate is None:
        return False
    check = preflight(root)
    if check.get("status") != "reject" or check.get("stable_letters", 0) <= 1:
        return False
    R0 = canon_rel(gate[2])
    state = tuple(state)
    if R0 not in state:
        return False
    here = bs_gate(state, general=True)
    return here is not None and canon_rel(here[2]) == R0
