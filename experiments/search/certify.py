"""Independent proof-carrying verifier for macro search certificates.

This module shares NO inference code with the search engine: everything here is
plain-Python string manipulation, written against the definition of the
Andrews–Curtis moves rather than against ``greedy_baseline``'s numba kernels.
The engine constructs a path of canonical states plus one typed certificate per
edge; this module expands each certificate into PRIMITIVE AC moves and replays
them, so a bug shared by the generator and its own replay cannot survive.

Primitive moves, on an ordered pair of freely reduced words ``[w1, w2]``:

    ("inv",  i)       w_i <- w_i^-1
    ("mul",  i, j)    w_i <- w_i . w_j            (i != j, j untouched)
    ("conj", i, g)    w_i <- g^-1 . w_i . g       (g a single letter)

Free reduction after each primitive is semantic normalisation (the words are
free-group elements), not a move.

An edge certificate is expanded from the STORED parent state, and the replayed
child words are then walked to the STORED child state by explicit "hop"
primitives — per-relator cyclic reduction and rotation are letter conjugations,
inversion is a primitive, and the pair swap is the classical six-move-plus-
conjugation AC composite materialised by ``swap_ops``. So a verified path is
one flat list of primitive AC moves from the input presentation to a trivial
one, with every stored state checked EXACTLY (ordered, letter for letter) along
the way. The final state must be two length-1 relators on DISTINCT generators —
a pair like ``(x, x)`` normally closes a proper subgroup and is not a trivial
presentation, so it is rejected even though it is two letters long.
"""

_INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
_ALPHABET = set("xXyY")


def inv_letter(g):
    return _INV[g]


def inv_word(w):
    return "".join(_INV[c] for c in reversed(w))


def free_reduce(w):
    out = []
    for c in w:
        if out and out[-1] == _INV[c]:
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyclic_core(w):
    """Cyclic reduction of a freely reduced word (strip cancelling end pairs)."""
    i, j = 0, len(w)
    while j - i >= 2 and w[i] == _INV[w[j - 1]]:
        i += 1
        j -= 1
    return w[i:j]


def rotations(w):
    return {w[k:] + w[:k] for k in range(max(len(w), 1))}


def cyclic_class(w):
    """Canonical key of the cyclic word up to rotation only (NOT inversion)."""
    core = cyclic_core(free_reduce(w))
    return min(rotations(core)) if core else ""


# --------------------------------------------------------------------------- replay

def apply_ops(words, ops):
    """Replay primitive ops on ``[w1, w2]``; returns the new pair. Raises on bad ops."""
    ws = [free_reduce(words[0]), free_reduce(words[1])]
    for op in ops:
        kind = op[0]
        if kind == "inv":
            _, i = op
            ws[i] = inv_word(ws[i])
        elif kind == "mul":
            _, i, j = op
            if i == j:
                raise ValueError("multiply requires distinct relator indices")
            ws[i] = free_reduce(ws[i] + ws[j])
        elif kind == "conj":
            _, i, g = op
            if g not in _ALPHABET:
                raise ValueError(f"conjugation letter {g!r} not in alphabet")
            ws[i] = free_reduce(_INV[g] + ws[i] + g)
        else:
            raise ValueError(f"unknown primitive {kind!r}")
    return ws


# ----------------------------------------------------------------- macro expansion

def _rot_ops(word, k, slot):
    """Primitives realising the engine's rot_k (np.roll: move the LAST k letters
    to the front), taking the shorter direction. Returns (ops, rotated word)."""
    n = len(word)
    if n == 0:
        return [], word
    k %= n
    ops = []
    w = word
    if k <= n - k:
        for _ in range(k):              # rotate right: conj by inv(last letter)
            g = _INV[w[-1]]
            ops.append(("conj", slot, g))
            w = w[-1] + w[:-1]
    else:
        for _ in range(n - k):          # rotate left: conj by the first letter
            ops.append(("conj", slot, w[0]))
            w = w[1:] + w[0]
    return ops, w


def _donor_factor_ops(tgt, oth, jsign, w):
    """Primitives appending ``w r_oth^jsign w⁻¹`` to slot ``tgt``, donor restored."""
    ops = []
    if jsign == -1:
        ops.append(("inv", oth))
    for g in inv_word(w):               # conj by word w^-1 => r_oth <- w r_oth w^-1
        ops.append(("conj", oth, g))
    ops.append(("mul", tgt, oth))
    for g in reversed(inv_word(w)):     # undo, letter by letter, in reverse
        ops.append(("conj", oth, _INV[g]))
    if jsign == -1:
        ops.append(("inv", oth))
    return ops


def expand_edge(parent, cert):
    """Primitive ops realising one certificate from the STORED parent pair.

    ``parent`` is the ordered pair of canonical words; slots are 0-based, while
    certificates carry 1-based targets.
    """
    kind = cert[0]
    tgt = cert[1] - 1
    oth = 1 - tgt
    ops = []
    if kind == "sub":
        _, _, jsign, k1, k2 = cert
        r_ops, _ = _rot_ops(parent[tgt], k1, tgt)
        ops.extend(r_ops)
        if jsign == -1:
            ops.append(("inv", oth))
        src = parent[oth] if jsign == 1 else inv_word(parent[oth])
        s_ops, _ = _rot_ops(src, k2, oth)
        ops.extend(s_ops)
        ops.append(("mul", tgt, oth))
        for op in reversed(s_ops):      # restore the source rotation
            ops.append(("conj", oth, _INV[op[2]]))
        if jsign == -1:
            ops.append(("inv", oth))
    elif kind == "donor":
        _, _, jsign, w = cert
        ops.extend(_donor_factor_ops(tgt, oth, jsign, w))
    elif kind == "ncrw":
        # multi-factor normal-closure rewrite: one donor expansion per factor,
        # in certificate order — the donor is restored between factors, so each
        # factor's primitives are exactly a donor edge's
        _, _, factors = cert
        for jsign, w in factors:
            ops.extend(_donor_factor_ops(tgt, oth, jsign, w))
    else:
        raise ValueError(f"unknown certificate kind {kind!r}")
    return ops


# ------------------------------------------------------------------------- hops

def swap_ops(a, b):
    """Primitives realising the transposition ``(a, b) -> (b, a)``.

        (a,b) -inv0-> (a^-1,b) -mul01-> (a^-1 b, b) -inv0-> (b^-1 a, b)
              -mul10-> (b^-1 a, a) -inv0-> (a^-1 b, a) -mul01-> (a^-1 b a, a)
              -conj0 by word a^-1-> (b, a)

    The final conjugation by the WORD ``a^-1`` is |a| letter conjugations.
    """
    ops = [("inv", 0), ("mul", 0, 1), ("inv", 0), ("mul", 1, 0),
           ("inv", 0), ("mul", 0, 1)]
    for g in inv_word(a):
        ops.append(("conj", 0, g))
    return ops


def _hop_one(word, target, slot):
    """Primitives taking ``word`` to the EXACT word ``target`` (same slot).

    ``target`` must be cyclically reduced (stored canonical states are) and in
    the same cyclic-word class as ``word`` up to inversion; raises otherwise.
    """
    w = free_reduce(word)
    t = target
    if cyclic_core(t) != t:
        raise ValueError("hop target is not cyclically reduced")
    ops = []
    if cyclic_class(w) != cyclic_class(t):
        if cyclic_class(inv_word(w)) != cyclic_class(t):
            raise ValueError("hop endpoints are not conjugate up to inversion")
        ops.append(("inv", slot))
        w = inv_word(w)
    while len(w) >= 2 and w[0] == _INV[w[-1]]:   # cyclic reduction = conjugation
        ops.append(("conj", slot, w[0]))
        w = w[1:-1]
    for k in range(max(len(w), 1)):              # rotate to the exact target
        if w[k:] + w[:k] == t:
            for _ in range(k):
                ops.append(("conj", slot, w[0]))
                w = w[1:] + w[0]
            break
    if w != t:
        raise ValueError("hop failed to reach its target word")
    return ops


def hop_ops(words, target):
    """Primitives taking the ordered pair ``words`` EXACTLY onto ``target``.

    Each replayed relator is conjugate (up to inversion) to one stored relator;
    the assignment may be the identity or the swap. For the swap, each slot is
    first walked to its partner's stored word, then ``swap_ops`` transposes.
    """
    def feasible(w, t):
        return cyclic_class(w) == cyclic_class(t) or \
            cyclic_class(inv_word(w)) == cyclic_class(t)

    if feasible(words[0], target[0]) and feasible(words[1], target[1]):
        try:
            ops = _hop_one(words[0], target[0], 0) + _hop_one(words[1], target[1], 1)
            return ops
        except ValueError:
            pass
    if not (feasible(words[0], target[1]) and feasible(words[1], target[0])):
        raise ValueError("replayed pair does not match the stored state")
    ops = _hop_one(words[0], target[1], 0) + _hop_one(words[1], target[0], 1)
    ops.extend(swap_ops(target[1], target[0]))
    return ops


# ------------------------------------------------------------------ verification

def expand_path(r1, r2, states, certs):
    """One flat primitive trace: input presentation -> ... -> final stored state.

    ``states`` is the stored canonical path (len(certs) + 1 pairs). Boundary
    checks are the caller's (``verify_solution`` replays with assertions).
    """
    if len(states) != len(certs) + 1:
        raise ValueError("path/certificate length mismatch")
    trace = []
    words = [free_reduce(r1), free_reduce(r2)]
    hop = hop_ops(words, states[0])
    trace.extend(hop)
    words = apply_ops(words, hop)
    for cert, child in zip(certs, states[1:]):
        edge = expand_edge(words, tuple(cert))
        trace.extend(edge)
        words = apply_ops(words, edge)
        hop = hop_ops(words, child)
        trace.extend(hop)
        words = apply_ops(words, hop)
    return trace


def verify_solution(r1, r2, states, certs):
    """Independently verify a solved path. Returns a report dict; never raises.

    Checks, in order: the expansion exists (every certificate is well formed and
    lands where it claims), every stored state is reached EXACTLY (ordered,
    letter for letter) when its hop completes, and the final state is a trivial
    presentation — two length-1 relators on distinct generators.

    Report keys: ok, reason, n_primitives, n_macro_primitives (edge cores only,
    hops excluded), per-edge elementary costs.
    """
    fail = lambda reason: {"ok": False, "reason": reason, "n_primitives": None,
                           "n_macro_primitives": None, "edge_costs": None}
    try:
        if len(states) != len(certs) + 1:
            return fail("path/certificate length mismatch")
        words = [free_reduce(r1), free_reduce(r2)]
        n_prim = 0
        n_macro = 0
        edge_costs = []
        hop = hop_ops(words, states[0])
        words = apply_ops(words, hop)
        n_prim += len(hop)
        if words != list(states[0]):
            return fail("initial hop missed the stored start state")
        for k, (cert, child) in enumerate(zip(certs, states[1:])):
            edge = expand_edge(words, tuple(cert))
            words = apply_ops(words, edge)
            hop = hop_ops(words, child)
            words = apply_ops(words, hop)
            n_prim += len(edge) + len(hop)
            n_macro += len(edge)
            edge_costs.append(len(edge))
            if words != list(child):
                return fail(f"edge {k}: replay missed the stored child state")
        final = words
        if len(final[0]) != 1 or len(final[1]) != 1:
            return fail("final state is not two length-1 relators")
        if final[0].lower() == final[1].lower():
            return fail("final relators use the same generator — not a "
                        "presentation of the trivial group")
        return {"ok": True, "reason": None, "n_primitives": n_prim,
                "n_macro_primitives": n_macro, "edge_costs": edge_costs}
    except (ValueError, KeyError, IndexError) as e:
        return fail(f"expansion error: {e}")
