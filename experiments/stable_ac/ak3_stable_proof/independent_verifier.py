#!/usr/bin/env python3
"""
Independent, adversarial verifier for acx-cert-v1 Andrews-Curtis certificates.

Authored FROM THE SPEC ONLY (black-box). Imports nothing from the engine that
produced the certificates; the only external dependency is the Python stdlib
(numpy is available but not needed -- we use an exact integer determinant).

Public API:
    verify(cert) -> (ok: bool, errors: list[str])

CLI:
    python3 independent_verifier.py cert1.json cert2.json ...
    prints "OK <file>" / "FAIL <file>" (+ error detail), exit 0 iff all OK.

Math conventions (Andrews-Curtis, arXiv:2408.15332):
  * A word is a list of nonzero ints; letter g == generator x_g, -g == its inverse.
  * free_reduce cancels adjacent a,-a.  cyclic_reduce additionally cancels a...-a
    at the two ends.  inverse([a1..ak]) == [-ak..-a1].
  * Two STATES are EQUAL-UP-TO-CANONICALIZATION iff one becomes the other by
    (a) reordering relators, (b) cyclically rotating any relator (LENGTH-PRESERVING
    cyclic shift of the word list), and (c) inverting (word-inverse) any relator.
    This is a purely combinatorial equivalence on the stored (freely-reduced) word
    lists -- it does NOT itself perform free/cyclic reduction.  Each STEP's own
    reduction (free vs cyclic) is applied during replay, exactly as the step spec
    dictates, and the reduced result is then compared up to this equivalence.
"""

import json
import sys


# --------------------------------------------------------------------------- #
# Word primitives
# --------------------------------------------------------------------------- #
def free_reduce(w):
    out = []
    for x in w:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return out


def cyclic_reduce(w):
    w = free_reduce(w)
    i, j = 0, len(w) - 1
    while i < j and w[i] == -w[j]:
        i += 1
        j -= 1
    return w[i:j + 1]


def inverse(w):
    return [-x for x in reversed(w)]


def canonical_relator(w):
    """Length-preserving canonical form under cyclic-shift + inversion.

    Returns the lexicographically minimal tuple over all cyclic shifts of w and
    of inverse(w).  Two words in the same (cyclic-conjugacy up to inversion) class
    have the same length, so this is a faithful class representative."""
    if not w:
        return ()
    n = len(w)
    best = None
    for base in (w, inverse(w)):
        for i in range(n):
            cand = tuple(base[i:] + base[:i])
            if best is None or cand < best:
                best = cand
    return best


def canonical_state(state):
    n = state["n_gen"]
    rels = tuple(sorted(canonical_relator(r) for r in state["relators"]))
    return (n, rels)


def states_equal(a, b):
    return canonical_state(a) == canonical_state(b)


# --------------------------------------------------------------------------- #
# Exact integer determinant of the abelianization exponent matrix
# --------------------------------------------------------------------------- #
def abelian_matrix(state):
    """M[g][i] = signed count of generator (g+1) in relator i."""
    n = state["n_gen"]
    M = [[0] * n for _ in range(n)]
    for i, r in enumerate(state["relators"]):
        for x in r:
            g = abs(x) - 1
            M[g][i] += 1 if x > 0 else -1
    return M


def int_det(M):
    """Fraction-free (Bareiss) integer determinant. M is n x n list-of-lists."""
    n = len(M)
    if n == 0:
        return 1
    M = [row[:] for row in M]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if M[k][k] == 0:
            swap = None
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    swap = i
                    break
            if swap is None:
                return 0
            M[k], M[swap] = M[swap], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


# --------------------------------------------------------------------------- #
# State-level global invariants
# --------------------------------------------------------------------------- #
def check_state_invariants(state, label, errors):
    if not isinstance(state, dict) or "n_gen" not in state or "relators" not in state:
        errors.append(f"{label}: malformed STATE (missing n_gen/relators)")
        return False
    n = state["n_gen"]
    rels = state["relators"]
    ok = True
    if not isinstance(n, int) or n < 1:
        errors.append(f"{label}: n_gen must be a positive int, got {n!r}")
        return False
    if not isinstance(rels, list):
        errors.append(f"{label}: relators must be a list")
        return False
    # balanced
    if len(rels) != n:
        errors.append(f"{label}: unbalanced -- {len(rels)} relators but n_gen={n}")
        ok = False
    for ridx, r in enumerate(rels):
        if not isinstance(r, list) or len(r) == 0:
            errors.append(f"{label}: relator {ridx} is empty or not a list")
            ok = False
            continue
        for x in r:
            if not isinstance(x, int) or x == 0 or abs(x) > n:
                errors.append(
                    f"{label}: relator {ridx} letter {x!r} out of range 1..{n} (or zero)")
                ok = False
    # abelianization determinant must be +-1 (only meaningful if balanced & letters ok)
    if len(rels) == n and ok:
        d = int_det(abelian_matrix(state))
        if abs(d) != 1:
            errors.append(f"{label}: |det(abelianization)| = {abs(d)} != 1")
            ok = False
    return ok


def is_trivial_presentation(state):
    """Trivial <x1..xk | x1,...,xk> up to relator order; each generator g appears
    as a single-letter relator [g] or [-g] exactly once (sign-insensitive)."""
    n = state["n_gen"]
    rels = state["relators"]
    if len(rels) != n:
        return False
    seen = set()
    for r in rels:
        if len(r) != 1:
            return False
        g = abs(r[0])
        if not (1 <= g <= n) or g in seen:
            return False
        seen.add(g)
    return seen == set(range(1, n + 1))


# --------------------------------------------------------------------------- #
# Step semantics -> produce the exact next state (deterministic step types)
# --------------------------------------------------------------------------- #
class StepError(Exception):
    pass


def apply_concat(state, step):
    n = state["n_gen"]
    rels = [r[:] for r in state["relators"]]
    i, j, sign = step["i"], step["j"], step.get("sign", 1)
    if i == j:
        raise StepError("concat requires i != j")
    if not (0 <= i < len(rels) and 0 <= j < len(rels)):
        raise StepError("concat index out of range")
    if sign not in (1, -1):
        raise StepError("concat sign must be +-1")
    rj = rels[j] if sign == 1 else inverse(rels[j])
    rels[i] = free_reduce(rels[i] + rj)
    return {"n_gen": n, "relators": rels}


def apply_conjugation(state, step):
    n = state["n_gen"]
    rels = [r[:] for r in state["relators"]]
    i, g = step["i"], step["g"]
    if not (0 <= i < len(rels)):
        raise StepError("conjugation index out of range")
    if g == 0 or abs(g) > n:
        raise StepError("conjugation generator out of range")
    rels[i] = free_reduce([g] + rels[i] + [-g])
    return {"n_gen": n, "relators": rels}


def apply_invert(state, step):
    n = state["n_gen"]
    rels = [r[:] for r in state["relators"]]
    i = step["i"]
    if not (0 <= i < len(rels)):
        raise StepError("invert index out of range")
    rels[i] = inverse(rels[i])
    return {"n_gen": n, "relators": rels}


def apply_relabel(state, step):
    n = state["n_gen"]
    rels = [r[:] for r in state["relators"]]
    perm = {int(k): int(v) for k, v in step["perm"].items()}
    if sorted(perm.keys()) != list(range(1, n + 1)):
        raise StepError("relabel perm keys are not exactly 1..n_gen")
    if sorted(perm.values()) != list(range(1, n + 1)):
        raise StepError("relabel perm is not a bijection of 1..n_gen")
    invert_set = set(int(x) for x in step.get("invert", []))
    if any(not (1 <= x <= n) for x in invert_set):
        raise StepError("relabel invert list has generator out of range")

    def relab(w):
        out = []
        for x in w:
            g = abs(x)
            s = 1 if x > 0 else -1
            if g in invert_set:
                s = -s
            out.append(s * perm[g])
        return free_reduce(out)

    return {"n_gen": n, "relators": [relab(r) for r in rels]}


def apply_stabilize(state, step):
    n = state["n_gen"]
    rels = [r[:] for r in state["relators"]]
    z = step["z"]
    w = list(step["w"])
    if z != n + 1:
        raise StepError(f"stabilize z must be n_gen+1={n+1}, got {z}")
    for a in w:
        if a == 0 or abs(a) > n:
            raise StepError("stabilize w has a letter out of range 1..n_gen")
    new_rel = cyclic_reduce([z] + inverse(free_reduce(w)))
    if not new_rel:
        raise StepError("stabilize produced empty relator")
    return {"n_gen": n + 1, "relators": rels + [new_rel]}


def apply_eliminate(state, step):
    n = state["n_gen"]
    rels = [r[:] for r in state["relators"]]
    gen = step["gen"]
    ri = step["ri"]
    if not (1 <= gen <= n):
        raise StepError(f"eliminate gen {gen} out of range 1..{n}")
    if not (0 <= ri < len(rels)):
        raise StepError("eliminate ri out of range")
    r = rels[ri]
    occ = [k for k, x in enumerate(r) if abs(x) == gen]
    if len(occ) != 1:
        raise StepError(
            f"eliminate: generator {gen} occurs {len(occ)} times in relator {ri}, "
            f"must be exactly once")
    idx = occ[0]
    if r[idx] == -gen:
        r = inverse(r)
        occ = [k for k, x in enumerate(r) if abs(x) == gen]
        idx = occ[0]
    if r[idx] != gen:
        raise StepError("eliminate: internal -- could not normalize occurrence to +gen")
    # rotate so +gen leads: r = [gen] + v, v has no +-gen
    r = r[idx:] + r[:idx]
    v = r[1:]
    if any(abs(x) == gen for x in v):
        raise StepError("eliminate: residual word still contains gen")
    inv_v = inverse(v)
    new_rels = []
    for k, rr in enumerate(rels):
        if k == ri:
            continue
        w = []
        for x in rr:
            if x == gen:
                w.extend(inv_v)
            elif x == -gen:
                w.extend(v)
            else:
                w.append(x)
        new_rels.append(cyclic_reduce(w))

    def renum(w):
        out = []
        for x in w:
            a = abs(x)
            s = 1 if x > 0 else -1
            if a > gen:
                a -= 1
            out.append(s * a)
        return out

    new_rels = [renum(w) for w in new_rels]
    return {"n_gen": n - 1, "relators": new_rels}


DETERMINISTIC = {
    "concat": apply_concat,
    "conjugation": apply_conjugation,
    "invert": apply_invert,
    "relabel": apply_relabel,
    "stabilize": apply_stabilize,
    "eliminate": apply_eliminate,
}


# --------------------------------------------------------------------------- #
# Substitution (membership check)
# --------------------------------------------------------------------------- #
def substitution_matches(state, target):
    """True iff `target` is equal-up-to-canonicalization to SOME state reachable
    from `state` by one substitution supermove:

        pick a != b; a cyclic rotation rot_a of r_a and a cyclic rotation rot_o of
        (r_b or r_b^{-1}) with last(rot_a) == -first(rot_o) (junction cancels);
        new relator = cyclic_reduce(free_reduce(rot_a + rot_o)); it replaces
        either slot a or slot b; all other relators unchanged.
    """
    if state["n_gen"] != target["n_gen"]:
        return False
    rels = state["relators"]
    m = len(rels)
    canon_orig = [canonical_relator(r) for r in rels]
    tgt_n, tgt_multiset = canonical_state(target)

    for a in range(m):
        ra = rels[a]
        la = len(ra)
        for b in range(m):
            if a == b:
                continue
            rb = rels[b]
            for rb_base in (rb, inverse(rb)):
                lb = len(rb_base)
                for ia in range(la):
                    rota = ra[ia:] + ra[:ia]
                    last = rota[-1]
                    for ib in range(lb):
                        if last != -rb_base[ib]:
                            continue
                        rotb = rb_base[ib:] + rb_base[:ib]
                        newrel = cyclic_reduce(free_reduce(rota + rotb))
                        if not newrel:
                            continue
                        cn = canonical_relator(newrel)
                        ms_a = sorted(
                            cn if k == a else canon_orig[k] for k in range(m))
                        if (tgt_n, tuple(ms_a)) == (tgt_n, tgt_multiset):
                            return True
                        ms_b = sorted(
                            cn if k == b else canon_orig[k] for k in range(m))
                        if (tgt_n, tuple(ms_b)) == (tgt_n, tgt_multiset):
                            return True
    return False


# --------------------------------------------------------------------------- #
# Top-level verify
# --------------------------------------------------------------------------- #
def _same_state(a, b):
    """Exact structural equality (start==states[0], end==states[-1])."""
    try:
        return (a.get("n_gen") == b.get("n_gen")
                and [list(r) for r in a.get("relators", [])]
                == [list(r) for r in b.get("relators", [])])
    except AttributeError:
        return False


def verify(cert):
    errors = []
    if not isinstance(cert, dict):
        return False, ["certificate is not a JSON object"]

    # schema field: spec says "acx-cert-v1"; real engine files use certificate_version.
    schema = cert.get("schema")
    ver = cert.get("certificate_version")
    if schema is not None and schema != "acx-cert-v1":
        errors.append(f"unexpected schema {schema!r} (expected acx-cert-v1)")
    if schema is None and ver is None:
        errors.append("missing schema / certificate_version")

    states = cert.get("states")
    steps = cert.get("steps")
    if not isinstance(states, list) or not isinstance(steps, list):
        return False, errors + ["missing or malformed states/steps"]
    if len(states) != len(steps) + 1:
        errors.append(f"len(states)={len(states)} != len(steps)+1={len(steps)+1}")
        return False, errors

    if "start" in cert and not _same_state(cert["start"], states[0]):
        errors.append("start != states[0]")
    if "end" in cert and not _same_state(cert["end"], states[-1]):
        errors.append("end != states[-1]")

    states_ok = True
    for t, st in enumerate(states):
        if not check_state_invariants(st, f"state[{t}]", errors):
            states_ok = False

    for t, step in enumerate(steps):
        if not isinstance(step, dict) or "type" not in step:
            errors.append(f"step[{t}]: malformed (no type)")
            continue
        typ = step["type"]
        cur = states[t]
        nxt = states[t + 1]
        try:
            if typ == "substitution":
                if not substitution_matches(cur, nxt):
                    errors.append(
                        f"step[{t}] substitution: states[{t+1}] is not reachable "
                        f"from states[{t}] by any single substitution move")
            elif typ in DETERMINISTIC:
                produced = DETERMINISTIC[typ](cur, step)
                if not states_equal(produced, nxt):
                    errors.append(
                        f"step[{t}] {typ}: replay result != states[{t+1}] "
                        f"(up to reorder/rotation/inversion)")
            else:
                errors.append(f"step[{t}]: unknown step type {typ!r}")
        except StepError as e:
            errors.append(f"step[{t}] {typ}: precondition failed -- {e}")
        except (KeyError, IndexError, TypeError) as e:
            errors.append(f"step[{t}] {typ}: malformed step -- {e!r}")

    if cert.get("end_is_trivial") is True:
        if not states_ok:
            errors.append("end_is_trivial: cannot certify (state invariants failed)")
        elif not is_trivial_presentation(states[-1]):
            errors.append(
                "end_is_trivial=true but final state is not the trivial presentation")

    return (len(errors) == 0), errors


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv):
    if len(argv) < 2:
        print("usage: independent_verifier.py cert1.json [cert2.json ...]",
              file=sys.stderr)
        return 2
    all_ok = True
    for path in argv[1:]:
        try:
            with open(path) as f:
                cert = json.load(f)
        except Exception as e:  # noqa
            print(f"FAIL {path}\n    could not load: {e!r}")
            all_ok = False
            continue
        ok, errs = verify(cert)
        if ok:
            print(f"OK   {path}")
        else:
            all_ok = False
            print(f"FAIL {path}")
            for e in errs:
                print(f"    - {e}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
