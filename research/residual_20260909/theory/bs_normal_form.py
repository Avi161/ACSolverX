"""Britton normal form for the companion of a consecutive-BS relator.

Conventions follow research/supermoves_20260908/bs_preflight.py exactly:
a recognized donor is  R = b^-1 a^m b a^-(m+1),  i.e.  b^-1 a^m b = a^(m+1)
in  G = <a, b | R> = BS(m, m+1).  Hence the two carry identities

    b a^(k(m+1)) = a^(km) b            (gap right of a  b^{+1}  reduces mod m+1)
    b^-1 a^(km)  = a^(k(m+1)) b^-1     (gap right of a  b^{-1}  reduces mod m)

The companion W is described cyclically by its stable-letter signs
``signs[i] in {+1,-1}`` and the a-exponents ``gaps[i]`` between stable letter i
and stable letter i+1 (cyclically) - the same data bs_preflight builds.
"""
from __future__ import annotations

from experiments.equivalence_classes.lib.words import canon_pair, canon_rel, inv
from research.supermoves_20260908.bs_preflight import donor_orientations


def core(pair):
    """(donor_index, a, b, m, n, donor, companion) for a consecutive-BS pair."""
    for index, donor in enumerate(pair):
        orientations = donor_orientations(donor)
        if orientations:
            a, b, m, n = orientations[0]
            return index, a, b, m, n, donor, pair[1 - index]
    return None


def signs_gaps(companion, a, b):
    positions = [i for i, c in enumerate(companion) if c.lower() == b.lower()]
    signs = [1 if companion[i] == b else -1 for i in positions]
    gaps = []
    for j, start in enumerate(positions):
        end = positions[(j + 1) % len(positions)]
        between = (companion[start + 1:end] if end > start
                   else companion[start + 1:] + companion[:end])
        gaps.append(between.count(a) - between.count(inv(a)))
    return signs, gaps


def britton_reduce(signs, gaps, m, n):
    """Cyclic Britton reduction; returns the reduced (signs, gaps)."""
    signs, gaps = list(signs), list(gaps)
    while len(signs) > 1:
        chosen = None
        for first in (1, -1):
            divisor, output = (n, m) if first == 1 else (m, n)
            for i, sign in enumerate(signs):
                if sign == first and signs[(i + 1) % len(signs)] == -first \
                        and gaps[i] % divisor == 0:
                    chosen = i, divisor, output
                    break
            if chosen is not None:
                break
        if chosen is None:
            return signs, gaps
        i, divisor, output = chosen
        signs, gaps = signs[i:] + signs[:i], gaps[i:] + gaps[:i]
        merged = gaps[-1] + gaps[0] // divisor * output + gaps[1]
        signs, gaps = signs[2:], gaps[2:-1] + [merged]
    return signs, gaps


def word_from(signs, gaps, a, b):
    """Rebuild a cyclic word from the stable-letter description."""
    out = []
    for sign, gap in zip(signs, gaps):
        out.append(b if sign == 1 else inv(b))
        out.append((a if gap >= 0 else inv(a)) * abs(gap))
    return "".join(out)


def class_s3(signs, gaps, m, n):
    """Invariants of a Britton-reduced 3-stable-letter companion.

    Returns dict(eps, u, v, w, alpha, beta) where, after rotating so the sign
    pattern reads (eps, eps, -eps), ``u`` is the gap at the (eps,eps) junction,
    ``v`` the gap at the (eps,-eps) junction and ``w`` the gap at the
    (-eps,eps) junction.  ``u`` is a free parameter (it lies in the carry
    lattice); the conjugacy class of W in G is fixed by

        alpha = v mod M_v ,   beta = w mod M_w
        M_v, M_w = (n, m) if eps == +1 else (m, n).
    """
    assert len(signs) == 3
    eps = 1 if sum(signs) > 0 else -1
    start = next(i for i in range(3)
                 if signs[i] == eps and signs[(i + 1) % 3] == eps)
    rot = lambda seq: seq[start:] + seq[:start]
    s, g = rot(list(signs)), rot(list(gaps))
    assert s == [eps, eps, -eps], (s, eps)
    u, v, w = g
    mv, mw = (n, m) if eps == 1 else (m, n)
    return {"eps": eps, "u": u, "v": v, "w": w,
            "alpha": v % mv, "beta": w % mw, "M_v": mv, "M_w": mw}


def normal_triple(info):
    """The carry-lattice normal form (u, v, w) = (0, alpha, beta)."""
    return 0, info["alpha"], info["beta"]


def canonical_label(m, info):
    """Class label invariant under W -> W^-1 and under a -> a^-1.

    Both symmetries are ordinary AC/relabelling symmetries of the pair, so the
    label is what actually classifies the AC problem.
    """
    n = m + 1
    eps, alpha, beta = info["eps"], info["alpha"], info["beta"]
    # normalise to eps = +1 by inverting W when needed:
    #   eps=-1 with (v mod m, w mod n) = (alpha, beta) becomes
    #   eps=+1 with (v mod n, w mod m) = (-beta mod n, -alpha mod m)
    if eps == 1:
        candidates = [(alpha % n, beta % m)]
    else:
        candidates = [((-beta) % n, (-alpha) % m)]
    # a -> a^-1 negates every gap
    first = candidates[0]
    candidates.append(((-first[0]) % n, (-first[1]) % m))
    return (m,) + min(candidates)


def analyse_pair(pair):
    """Full stalled/pinchable analysis of a canonical pair."""
    found = core(tuple(canon_pair(*pair)))
    if found is None:
        return None
    index, a, b, m, n, donor, companion = found
    signs, gaps = signs_gaps(companion, a, b)
    out = {"m": m, "n": n, "a": a, "b": b, "donor": donor, "companion": companion,
           "raw_signs": signs, "raw_gaps": gaps,
           "stable_exponent": sum(signs)}
    if abs(sum(signs)) != 1:
        out["status"] = "exponent"
        return out
    rsigns, rgaps = britton_reduce(signs, gaps, m, n)
    out["reduced_signs"], out["reduced_gaps"] = rsigns, rgaps
    out["s"] = len(rsigns)
    if len(rsigns) == 1:
        out["status"] = "accept"
        return out
    out["status"] = "stalled"
    if len(rsigns) == 3:
        info = class_s3(rsigns, rgaps, m, n)
        out.update(info)
        out["normal_triple"] = normal_triple(info)
        out["label"] = canonical_label(m, info)
    return out


# ---------------------------------------------------------------------------
# Constructive side: every rewrite below is ONE ordinary Definition 2.1 move
# ---------------------------------------------------------------------------
#
# A *unit carry at stable letter i* rewrites, inside the companion,
#
#     b     a^(m+1)  ->  a^m     b        (when signs[i] == +1)
#     b^-1  a^m      ->  a^(m+1) b^-1     (when signs[i] == -1)
#
# i.e. it multiplies the companion by one conjugate of R^(+/-1); on the gap
# vector it is  gaps[i] -= k*M, gaps[i-1] += k*M', with (M, M') = (m+1, m) for
# a positive stable letter and (m, m+1) for a negative one.  Britton pinches
# are the special case where a gap reaches 0 between opposite signs; the two
# stable letters then cancel freely.  So ONE primitive - the unit carry -
# expresses both the Britton reduction and the normal-form transport.

def modulus(sign, m):
    return (m + 1, m) if sign == 1 else (m, m + 1)


def cancel(signs, gaps):
    """Free cancellation of an opposite-sign stable pair separated by a^0."""
    signs, gaps = list(signs), list(gaps)
    changed = True
    while changed and len(signs) > 1:
        changed = False
        for j in range(len(signs)):
            k = (j + 1) % len(signs)
            if gaps[j] == 0 and signs[j] == -signs[k]:
                assert len(signs) >= 3, "stable exponent +/-1 forbids s == 2"
                s = signs[j:] + signs[:j]
                g = gaps[j:] + gaps[:j]
                signs, gaps = s[2:], g[2:-1] + [g[-1] + g[1]]
                changed = True
                break
    return signs, gaps


def unit_carry(signs, gaps, index, direction, m):
    """Apply one unit carry at ``index``; returns the new (signs, gaps)."""
    M, Mp = modulus(signs[index], m)
    gaps = list(gaps)
    gaps[index] -= direction * M
    gaps[index - 1] += direction * Mp
    return cancel(signs, gaps)


def reduce_plan(signs, gaps, m):
    """Unit carries realising bs_preflight's cyclic Britton reduction."""
    n = m + 1
    signs, gaps = cancel(signs, gaps)
    plan = []
    while len(signs) > 1:
        chosen = None
        for first in (1, -1):
            divisor = n if first == 1 else m
            for i, sign in enumerate(signs):
                if sign == first and signs[(i + 1) % len(signs)] == -first \
                        and gaps[i] % divisor == 0:
                    chosen = i, gaps[i] // divisor
                    break
            if chosen is not None:
                break
        if chosen is None:
            return plan, signs, gaps          # stalled: nothing more to pinch
        i, k = chosen
        step = 1 if k > 0 else -1
        for _ in range(abs(k)):
            plan.append((i, step))
            signs, gaps = unit_carry(signs, gaps, i, step, m)
            if len(signs) <= 1:
                break
    return plan, signs, gaps


def carry_generators(m, eps):
    """The three unit carries of a stalled s=3 companion, as gap vectors."""
    n = m + 1
    if eps == 1:
        return (-n, 0, m), (m, -n, 0), (0, n, -m)
    return (-m, 0, n), (n, -m, 0), (0, m, -n)


def carry_solution(m, eps, start, target):
    """Unique integer (c0, c1, c2) with sum ci*vi == target - start, or None.

    The generators span L = Z e_u + M_v Z e_v + M_w Z e_w, so a target is
    reachable exactly when it matches ``start`` in the two residues.
    """
    n = m + 1
    d = tuple(t - s for t, s in zip(target, start))
    if eps == 1:
        if d[1] % n or d[2] % m:
            return None
        A, B = d[1] // n, d[2] // m
        c1 = -(d[0] + n * (A + B))
    else:
        if d[1] % m or d[2] % n:
            return None
        A, B = d[1] // m, d[2] // n
        c1 = d[0] + m * (A + B)
    c2, c0 = c1 + A, c1 + A + B
    generators = carry_generators(m, eps)
    total = tuple(sum(c * g[i] for c, g in zip((c0, c1, c2), generators)) for i in range(3))
    return (c0, c1, c2) if total == d else None


def transport_plan(m, eps, start, target):
    """Unit carries from gap triple ``start`` to ``target``, shortest-word order."""
    solution = carry_solution(m, eps, start, target)
    if solution is None:
        return None
    generators = carry_generators(m, eps)
    pending = [(i, 1 if solution[i] > 0 else -1)
               for i in range(3) for _ in range(abs(solution[i]))]
    current, plan = list(start), []
    while pending:
        best = None
        for j, (i, direction) in enumerate(pending):
            candidate = [current[k] + direction * generators[i][k] for k in range(3)]
            cost = sum(map(abs, candidate))
            if best is None or cost < best[0]:
                best = (cost, j, candidate, i, direction)
        _, j, candidate, i, direction = best
        pending.pop(j)
        current = candidate
        plan.append((i, direction))
    return solution, plan


def find_move(state, target_pair):
    """The Definition 2.1 move taking ``state`` to ``target_pair``, verified."""
    from experiments.equivalence_classes.lib.words import replay_move
    for target in (1, 2):
        for jsign in (1, -1):
            for k1 in range(len(state[target - 1])):
                for k2 in range(len(state[2 - target])):
                    move = (target, jsign, k1, k2)
                    if replay_move(state, move) == target_pair:
                        return move
    return None


def run_plan(state, R, a, b, signs, gaps, plan, m):
    """Apply a unit-carry plan, emitting one verified AC move per carry."""
    states, steps = [list(state)], []
    signs, gaps = list(signs), list(gaps)
    for index, direction in plan:
        signs, gaps = unit_carry(signs, gaps, index, direction, m)
        word = canon_rel(word_from(signs, gaps, a, b))
        nxt = canon_pair(word, R)
        move = find_move(state, nxt)
        if move is None:
            return None
        steps.append({"kind": "substitution", "move": "_".join(map(str, move))})
        states.append(list(nxt))
        state = nxt
    return state, states, steps, signs, gaps


def orient(pair):
    """(state, R, a, b, m, n, companion signs/gaps) for a consecutive-BS pair."""
    state = tuple(canon_pair(*pair))
    found = core(state)
    if found is None:
        return None
    index, a, b, m, n, R, W = found
    signs, gaps = signs_gaps(W, a, b)
    if abs(sum(signs)) != 1:
        return None
    return state, R, a, b, m, n, signs, gaps


DEMOTION_TARGETS = ((0, 1, -1), (0, -1, 1))


def demotion_certificate(pair):
    """Rule BS-DEMOTE.

    Britton-reduce the companion, then transport it onto the BS(1,2) relator
    b^(2eps) a b^(-eps) a^(-1).  Every emitted step is one ordinary AC
    substitution, verified against words.replay_move.  The caller finishes
    with consecutive_bs.collapse on the returned pair.
    """
    oriented = orient(pair)
    if oriented is None:
        return {"applicable": False, "reason": "not_a_consecutive_bs_pair"}
    state, R, a, b, m, n, signs, gaps = oriented
    plan, rsigns, rgaps = reduce_plan(signs, gaps, m)
    if len(rsigns) == 1:
        return {"applicable": False, "reason": "already_pinchable"}
    if len(rsigns) != 3:
        return {"applicable": False, "reason": f"reduced_stable_letters_{len(rsigns)}"}
    ran = run_plan(state, R, a, b, signs, gaps, plan, m)
    if ran is None:
        return {"applicable": False, "reason": "reduction_path_failed"}
    state, states, steps, rsigns, rgaps = ran
    eps = 1 if sum(rsigns) > 0 else -1
    start = next(i for i in range(3) if rsigns[i] == eps and rsigns[(i + 1) % 3] == eps)
    rsigns = rsigns[start:] + rsigns[:start]
    rgaps = rgaps[start:] + rgaps[:start]
    for target in DEMOTION_TARGETS:
        found = transport_plan(m, eps, tuple(rgaps), target)
        if found is None:
            continue
        solution, plan2 = found
        ran = run_plan(state, R, a, b, rsigns, rgaps, plan2, m)
        if ran is None:
            return {"applicable": False, "reason": "transport_path_failed"}
        state, states2, steps2, _s, _g = ran
        states, steps = states + states2[1:], steps + steps2
        return {"applicable": True, "reason": "demotion", "target": target,
                "m": m, "eps": eps, "reduced_gaps": tuple(rgaps),
                "pinch_carries": len(plan), "transport_carries": len(plan2),
                "solution": solution, "carries": len(steps),
                "states": states, "steps": steps, "final": list(state),
                "max_total_length": max(sum(map(len, s)) for s in states)}
    return {"applicable": False, "reason": "class_not_demotable"}
