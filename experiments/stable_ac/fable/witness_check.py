"""Independent verifier for a claimed spherical Neuwirth rotation system.

This module shares **no scheme code** with ``neuwirth_rank``: it rebuilds the exact
``D, A, B`` dictionary from the words alone and then does nothing but permutation
arithmetic.  Its job is to be a second, structurally different opinion on any YES.

What it checks, in order:

1. ``C`` is a rotation system: exactly one cyclic order per germ, and that order is a
   permutation of exactly the darts sitting at that germ;
2. Neuwirth compatibility ``C_{tau v} = B C_v^{-1} B`` for every generator germ, both
   germ by germ and in the equivalent global form ``B C B = C^{-1}``;
3. the Lemma 1 numbers ``|C|``, ``|A|``, ``|AC|``, ``L = #Orb<A, C>`` and the defect
   ``|A| - |C| + 2L - |AC|``, asserting ``L == 1`` and defect ``0``;
4. transitivity of ``<AC, BC>`` with the right-to-left convention ``(PQ)(e) = P(Q(e))``.

Point 4 is *not* an extra thickenability condition.  By Corollary 3 of the Neuwirth
note, on a balanced **trivial-group** target the combination "Euler passes, ``BC``
transitivity fails" contradicts the proved topology, so it is raised as
``AuditContradiction`` -- an error in the dictionary, the composition convention or
the enumeration -- and never reported as a topological outcome.

The ``pi_1(K_P) = 1`` hypothesis of Corollary 3 is load-bearing and is exposed as the
``trivial_group`` flag (default ``True``, the setting for every target on this line).
It is not decoration: the exact pair ``("XXY", "XYxy")`` presents ``Z``, has a genuine
compatible spherical rotation, and its ``<AC, BC>`` has two orbits -- a legitimate
disconnected ``boundary N``, not a bug.  Callers verifying witnesses for presentations
that have not been certified trivial must pass ``trivial_group=False``; the report
still records ``ac_bc_orbits`` and ``ac_bc_transitive``.
"""

from __future__ import annotations

GERM_NAMES = ("x+", "x-", "y+", "y-")
_TAU = (1, 0, 3, 2)
_LETTER_GERMS = {
    "x": (0, 1),
    "X": (1, 0),
    "y": (2, 3),
    "Y": (3, 2),
}


class WitnessError(AssertionError):
    """The claimed witness is not a valid compatible spherical rotation system."""


class AuditContradiction(RuntimeError):
    """Euler passed but <AC, BC> is not transitive -- proved impossible, hence a bug."""


def _build(words):
    """Rebuild darts, A, B and the germ map from the exact words (no shared code)."""
    words = tuple(words)
    letters = []
    bounds = []
    for w in words:
        if not w:
            raise WitnessError("empty relator")
        bounds.append((len(letters), len(letters) + len(w)))
        for c in w:
            if c not in _LETTER_GERMS:
                raise WitnessError(f"bad letter {c!r}")
            letters.append(c)
    n = len(letters)
    size = 2 * n
    B = list(range(size))
    for i in range(n):
        B[2 * i], B[2 * i + 1] = 2 * i + 1, 2 * i
    A = [None] * size
    for lo, hi in bounds:
        span = hi - lo
        for k in range(span):
            i = lo + k
            j = lo + (k + 1) % span
            A[2 * i + 1] = 2 * j
            A[2 * j] = 2 * i + 1
    if any(a is None for a in A):
        raise WitnessError("corner involution incomplete")
    germ = [0] * size
    for i, c in enumerate(letters):
        gd, gh = _LETTER_GERMS[c]
        germ[2 * i], germ[2 * i + 1] = gd, gh
    return tuple(A), tuple(B), tuple(germ), size


def _cycles(perm):
    size = len(perm)
    seen = bytearray(size)
    count = 0
    for start in range(size):
        if seen[start]:
            continue
        count += 1
        cur = start
        while not seen[cur]:
            seen[cur] = 1
            cur = perm[cur]
    return count


def _orbits(perms, size):
    seen = bytearray(size)
    count = 0
    for start in range(size):
        if seen[start]:
            continue
        count += 1
        stack = [start]
        seen[start] = 1
        while stack:
            e = stack.pop()
            for p in perms:
                f = p[e]
                if not seen[f]:
                    seen[f] = 1
                    stack.append(f)
    return count


def _normalise_rotation(rotation):
    """Accept ``{germ name or index: dart sequence}`` and return an index-keyed dict."""
    out = {}
    for key, seq in rotation.items():
        if isinstance(key, str):
            if key not in GERM_NAMES:
                raise WitnessError(f"unknown germ {key!r}")
            idx = GERM_NAMES.index(key)
        else:
            idx = int(key)
            if not 0 <= idx < 4:
                raise WitnessError(f"germ index out of range: {idx}")
        if idx in out:
            raise WitnessError(f"germ {GERM_NAMES[idx]} listed twice")
        out[idx] = tuple(int(d) for d in seq)
    return out


def check_witness(words, rotation, trivial_group: bool = True) -> dict:
    """Verify a claimed compatible spherical rotation and return the audit report."""
    A, B, germ, size = _build(words)
    orders = _normalise_rotation(rotation)

    # (1) valid rotation system
    present = sorted({germ[d] for d in range(size)})
    if sorted(orders) != present:
        raise WitnessError(
            f"rotation covers germs {sorted(orders)}, expected {present}"
        )
    for v, seq in orders.items():
        want = sorted(d for d in range(size) if germ[d] == v)
        if sorted(seq) != want:
            raise WitnessError(f"germ {GERM_NAMES[v]}: dart set {sorted(seq)} != {want}")
        if len(set(seq)) != len(seq):
            raise WitnessError(f"germ {GERM_NAMES[v]}: repeated dart")

    C = [None] * size
    for v, seq in orders.items():
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    if any(c is None for c in C):
        raise WitnessError("rotation does not cover every dart")
    C = tuple(C)

    # (2) compatibility, germ by germ and globally
    Cinv = [0] * size
    for e in range(size):
        Cinv[C[e]] = e
    for v, seq in orders.items():
        tv = _TAU[v]
        if tv not in orders:
            raise WitnessError(f"germ {GERM_NAMES[tv]} missing while {GERM_NAMES[v]} present")
        for d in seq:
            if B[C[B[d]]] != Cinv[d]:
                raise WitnessError(
                    f"compatibility C_[{GERM_NAMES[tv]}] = B C_[{GERM_NAMES[v]}]^-1 B "
                    f"fails at dart {d}"
                )
    if any(B[C[B[e]]] != Cinv[e] for e in range(size)):
        raise WitnessError("global compatibility B C B = C^-1 fails")

    # (3) Lemma 1
    AC = tuple(A[C[e]] for e in range(size))
    BC = tuple(B[C[e]] for e in range(size))
    n_C, n_A, n_AC = _cycles(C), _cycles(A), _cycles(AC)
    L = _orbits((A, C), size)
    defect = n_A - n_C + 2 * L - n_AC
    euler = n_C - n_A + n_AC
    report = {
        "words": tuple(words),
        "darts": size,
        "cycles_C": n_C,
        "cycles_A": n_A,
        "cycles_AC": n_AC,
        "link_components": L,
        "euler_characteristic": euler,
        "defect": defect,
        "genus": defect // 2 if defect % 2 == 0 else None,
        "euler_line": f"|C| - |A| + |AC| = {n_C} - {n_A} + {n_AC} = {euler}",
        "ac_bc_orbits": _orbits((AC, BC), size),
        "compatible": True,
    }
    if defect < 0 or defect % 2:
        raise WitnessError(f"illegal defect {defect}")
    if L != 1:
        raise WitnessError(f"link has {L} components; Theorem 2 needs a connected link")
    if defect != 0:
        raise WitnessError(f"defect {defect} != 0; the rotation surface is not a sphere")

    # (4) Corollary 3 audit
    report["ac_bc_transitive"] = report["ac_bc_orbits"] == 1
    if trivial_group and not report["ac_bc_transitive"]:
        raise AuditContradiction(
            "Euler passes (defect 0, L = 1) but <AC, BC> has "
            f"{report['ac_bc_orbits']} orbits with the right-to-left convention; "
            "Corollary 3 proves this cannot happen, so it is an audit contradiction "
            f"(words={tuple(words)})"
        )
    return report


def check_rank_witness(decision, trivial_group: bool = True) -> dict:
    """Convenience wrapper for a ``neuwirth_rank.RankDecision`` carrying a witness."""
    if decision.witness is None:
        raise WitnessError("decision carries no witness")
    return check_witness(decision.words, decision.witness.rotation_map(),
                         trivial_group=trivial_group)


def ac_bc_orbit_count(words, rotation) -> int:
    """The number of ``<AC, BC>`` orbits, with no Euler precondition (audit helper)."""
    A, B, germ, size = _build(words)
    orders = _normalise_rotation(rotation)
    C = [None] * size
    for v, seq in orders.items():
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    if any(c is None for c in C):
        raise WitnessError("rotation does not cover every dart")
    AC = tuple(A[C[e]] for e in range(size))
    BC = tuple(B[C[e]] for e in range(size))
    return _orbits((AC, BC), size)


def audit_permutations(A, B, C, trivial_group: bool = True) -> dict:
    """Run checks (3) and (4) on hand-built permutations given as image tuples.

    Used by the unit tests to exercise the ``AuditContradiction`` path on a synthetic
    ``(A, B, C)`` triple that need not come from any word.
    """
    size = len(A)
    if not (len(B) == len(C) == size):
        raise WitnessError("permutations have different degrees")
    for p in (A, B, C):
        if sorted(p) != list(range(size)):
            raise WitnessError("not a permutation")
    AC = tuple(A[C[e]] for e in range(size))
    BC = tuple(B[C[e]] for e in range(size))
    n_C, n_A, n_AC = _cycles(C), _cycles(A), _cycles(AC)
    L = _orbits((A, C), size)
    defect = n_A - n_C + 2 * L - n_AC
    orbits = _orbits((AC, BC), size)
    report = {
        "cycles_C": n_C,
        "cycles_A": n_A,
        "cycles_AC": n_AC,
        "link_components": L,
        "defect": defect,
        "euler_characteristic": n_C - n_A + n_AC,
        "ac_bc_orbits": orbits,
        "ac_bc_transitive": orbits == 1,
    }
    if defect == 0 and L == 1 and orbits != 1 and trivial_group:
        raise AuditContradiction(
            f"Euler passes but <AC, BC> has {orbits} orbits -- audit contradiction"
        )
    return report
