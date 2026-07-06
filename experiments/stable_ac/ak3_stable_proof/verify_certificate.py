"""Own-draft certificate verifier (engine author's). L1 replay / L2 preconditions /
L3 global invariants. A second, independently-authored verifier
(``independent_verifier.py``, written black-box from the schema + the math by an
adversarial subagent) must ALSO pass every certificate before any claim ships.

Checks:
  L1  every step's recorded post-state equals the recomputed post-state
  L2  every step's preconditions hold (exactly-once occurrence for eliminate, letter
      ranges, i!=j, perm bijectivity, ...)
  L3  states[0]==start, states[-1]==end; every state balanced (n_gen == #relators);
      no empty relator; |abelianization det| == 1 everywhere; if end_is_trivial, the
      end state is <x1..xk | x1,...,xk> up to relator order.

Returns (ok: bool, errors: list[str]) from verify(); raises nothing on bad certs.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from presentation import (  # noqa: E402
    abelianization_det, canonical_state_key, free_reduce, cyclic_reduce,
    inverse_word, is_trivial_state, relabel_state,
)
from stable_moves import occurrences, substitute_word  # noqa: E402


def _relators(state_o):
    return [list(r) for r in state_o["relators"]], int(state_o["n_gen"])


def _check_concat(prev, n_gen, step, errs, t):
    i, j, sign = step["i"], step["j"], step["sign"]
    if i == j:
        errs.append(f"step {t}: concat i==j")
        return None, n_gen
    if sign not in (1, -1):
        errs.append(f"step {t}: concat sign {sign}")
        return None, n_gen
    rj = prev[j] if sign == 1 else inverse_word(prev[j])
    out = [list(r) for r in prev]
    out[i] = free_reduce(prev[i] + rj)
    return out, n_gen


def _check_conjugation(prev, n_gen, step, errs, t):
    i, g = step["i"], step["g"]
    if not (1 <= abs(g) <= n_gen):
        errs.append(f"step {t}: conjugation letter {g} out of range")
        return None, n_gen
    out = [list(r) for r in prev]
    out[i] = free_reduce([g] + prev[i] + [-g])
    return out, n_gen


def _check_stabilize(prev, n_gen, step, errs, t):
    z, w = step["z"], list(step["w"])
    if z != n_gen + 1:
        errs.append(f"step {t}: stabilize z={z} != n_gen+1={n_gen + 1}")
        return None, n_gen
    if any(a == 0 or abs(a) > n_gen for a in w):
        errs.append(f"step {t}: stabilize w has letters outside 1..{n_gen}")
        return None, n_gen
    out = [list(r) for r in prev] + [cyclic_reduce([z] + inverse_word(free_reduce(w)))]
    return out, n_gen + 1


def _check_eliminate(prev, n_gen, step, errs, t):
    gen, ri = step["gen"], step["ri"]
    if not (1 <= gen <= n_gen) or not (0 <= ri < len(prev)):
        errs.append(f"step {t}: eliminate params out of range")
        return None, n_gen
    r = list(prev[ri])
    occ = occurrences(r, gen)
    if len(occ) != 1:
        errs.append(f"step {t}: eliminate gen {gen} occurs {len(occ)} times in relator {ri}")
        return None, n_gen
    if r[occ[0]] == -gen:
        r = inverse_word(r)
        occ = occurrences(r, gen)
    r = r[occ[0]:] + r[:occ[0]]
    v = r[1:]
    sub = inverse_word(v)

    def renum(word):
        return [(1 if a > 0 else -1) * (abs(a) - 1) if abs(a) > gen else a for a in word]

    out = []
    for jj, other in enumerate(prev):
        if jj == ri:
            continue
        out.append(renum(cyclic_reduce(substitute_word(list(other), gen, sub))))
    return out, n_gen - 1


def _check_invert(prev, n_gen, step, errs, t):
    i = step["i"]
    if not (0 <= i < len(prev)):
        errs.append(f"step {t}: invert index {i} out of range")
        return None, n_gen
    out = [list(r) for r in prev]
    out[i] = inverse_word(prev[i])
    return out, n_gen


def _check_relabel(prev, n_gen, step, errs, t):
    perm = {int(k): int(v) for k, v in step["perm"].items()}
    invert = frozenset(int(g) for g in step.get("invert", []))
    if sorted(perm.keys()) != list(range(1, n_gen + 1)) or \
       sorted(perm.values()) != list(range(1, n_gen + 1)):
        errs.append(f"step {t}: relabel perm not a bijection on 1..{n_gen}")
        return None, n_gen
    out = [list(r) for r in relabel_state(prev, perm, invert)]
    return out, n_gen


def _check_substitution(prev, n_gen, step, errs, t, next_state):
    """greedy_nrel composite move: states are canonical tuples, so we verify by
    membership — the recorded next state must be reachable in one substitution move,
    recomputed here from the math (rotate, splice, reduce), not via greedy_nrel."""
    target = canonical_state_key(next_state)
    n = len(prev)
    for a in range(n):
        ra = prev[a]
        for b in range(n):
            if b == a:
                continue
            for c_inv in (0, 1):
                c = list(prev[b]) if c_inv == 0 else inverse_word(prev[b])
                for i in range(len(ra)):
                    ra_rot = ra[-i:] + ra[:-i] if i else list(ra)
                    for j in range(len(c)):
                        c_rot = c[-j:] + c[:-j] if j else list(c)
                        if ra_rot[-1] != -c_rot[0]:
                            continue
                        nbr = cyclic_reduce(free_reduce(ra_rot + c_rot))
                        if not nbr:
                            continue
                        for slot in (a, b):
                            cand = [list(r) for r in prev]
                            cand[slot] = nbr
                            if canonical_state_key(cand) == target:
                                return [list(r) for r in next_state], n_gen
    errs.append(f"step {t}: substitution: next state not reachable in one move")
    return None, n_gen


CHECKERS = {
    "concat": _check_concat,
    "conjugation": _check_conjugation,
    "invert": _check_invert,
    "stabilize": _check_stabilize,
    "eliminate": _check_eliminate,
    "relabel": _check_relabel,
}


def verify(cert):
    errs = []
    states = cert["states"]
    steps = cert["steps"]
    if len(states) != len(steps) + 1:
        return False, ["len(states) != len(steps)+1"]
    if states[0] != cert["start"] or states[-1] != cert["end"]:
        errs.append("start/end do not match states[0]/states[-1]")

    for t, s in enumerate(states):
        rels, ng = _relators(s)
        if len(rels) != ng:
            errs.append(f"state {t}: not balanced ({len(rels)} relators, n_gen={ng})")
        if any(len(r) == 0 for r in rels):
            errs.append(f"state {t}: empty relator")
        if any(a == 0 or abs(a) > ng for r in rels for a in r):
            errs.append(f"state {t}: letter out of range 1..{ng}")
        d = abelianization_det(rels, ng)
        if d is None or abs(d) != 1:
            errs.append(f"state {t}: |abelianization det| = {d}, expected 1")
    if errs:
        return False, errs

    for t, step in enumerate(steps):
        prev, ng = _relators(states[t])
        nxt, ng_next = _relators(states[t + 1])
        typ = step["type"]
        if typ == "substitution":
            got, ng_new = _check_substitution(prev, ng, step, errs, t, nxt)
        elif typ in CHECKERS:
            got, ng_new = CHECKERS[typ](prev, ng, step, errs, t)
        else:
            errs.append(f"step {t}: unknown type {typ!r}")
            got, ng_new = None, ng
        if got is None:
            continue
        if ng_new != ng_next:
            errs.append(f"step {t}: n_gen {ng_new} != recorded {ng_next}")
            continue
        if typ == "substitution":
            continue  # membership check already done against recorded next state
        # exact replay for order-preserving step types; eliminate/relabel included
        if [list(r) for r in got] != nxt:
            # allow the recorded state to be a *canonically equal* form (e.g. relators
            # cyclically reduced or reordered by an external emitter)
            if canonical_state_key(got) != canonical_state_key(nxt):
                errs.append(f"step {t} ({typ}): replay mismatch")

    if cert.get("end_is_trivial"):
        rels, ng = _relators(states[-1])
        if not is_trivial_state(rels, ng):
            errs.append("end_is_trivial claimed but end state is not the trivial presentation")

    return (len(errs) == 0), errs


def main(paths):
    ok_all = True
    for p in paths:
        import json
        with open(p) as f:
            cert = json.load(f)
        ok, errs = verify(cert)
        ok_all &= ok
        print(f"{'OK  ' if ok else 'FAIL'} {cert.get('name')}  steps={len(cert['steps'])}  {p}")
        for e in errs[:10]:
            print(f"      {e}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
