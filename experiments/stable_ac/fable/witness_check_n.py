"""Rank-generic independent verifier for a claimed spherical Neuwirth rotation system.

This is the rank-n sibling of ``witness_check``.  It shares **no scheme code** with the
solver: it does not import ``neuwirth_rank_n`` (or ``neuwirth_core``), it rebuilds the
exact ``D, A, B`` dictionary from the words alone, and it then does nothing but
permutation arithmetic.  Its job is to be a second, structurally different opinion on
any YES the rank-n solver produces.

Why this file exists at all.  ``witness_check`` is **not** rank-generic: its
``_LETTER_GERMS`` table, its ``GERM_NAMES``, its ``_TAU`` and the ``0 <= idx < 4`` bound
in ``_normalise_rotation`` all hard-code the two-generator alphabet, so a rank-3 witness
cannot be passed to it.  What *is* rank-generic there -- the cycle counter, the orbit
counter and the two exception classes -- is imported and reused verbatim rather than
re-implemented, so the two verifiers agree by construction on the permutation
arithmetic and differ only in the alphabet layer.

Germ layout (the same convention as ``neuwirth_rank_n``, re-derived here from the words
so that the two modules can disagree if either is wrong): generator ``k`` owns germs
``2k`` (``g+``) and ``2k + 1`` (``g-``), ``tau(v) = v ^ 1``, and for occurrence ``i``,
``nu(d_i), nu(h_i)`` is ``(g+, g-)`` for the letter ``g`` and ``(g-, g+)`` for ``g^-1``.

What it checks, in order:

1. ``C`` is a rotation system: exactly one cyclic order per germ, and that order is a
   permutation of exactly the darts sitting at that germ;
2. Neuwirth compatibility ``C_{tau v} = B C_v^{-1} B`` per generator, germ by germ and
   in the equivalent global form ``B C B = C^{-1}``;
3. the Lemma 1 numbers ``|C|``, ``|A|``, ``|AC|``, ``L = #Orb<A, C>`` and the defect
   ``|A| - |C| + 2L - |AC|``, asserting ``L == 1`` and defect ``0``;
4. transitivity of ``<AC, BC>`` with the right-to-left convention ``(PQ)(e) = P(Q(e))``,
   gated on ``trivial_group``.

Point 4 is not an extra thickenability condition.  By Corollary 3 of the Neuwirth note
it is *forced* on a balanced trivial-group target once (3) passes, so a failure there is
raised as ``AuditContradiction`` -- an error in the dictionary, the composition
convention or the enumeration -- and never reported as a topological outcome.  The
``pi_1(K_P) = 1`` hypothesis is load-bearing (the rank-2 module records the exact pair
``("XXY", "XYxy")``, which presents ``Z``, has a genuine compatible spherical rotation
and two ``<AC, BC>`` orbits), so callers that have not certified triviality -- e.g. by
``coset_enum.is_trivial_group(words, generators=("x", "y", "z"))`` -- must pass
``trivial_group=False``.  The report always records ``ac_bc_orbits`` and
``ac_bc_transitive`` either way.
"""

from __future__ import annotations

from experiments.stable_ac.fable.witness_check import (  # rank-generic primitives only
    AuditContradiction,
    WitnessError,
    _cycles,
    _orbits,
)

__all__ = [
    "WitnessError",
    "AuditContradiction",
    "generators_of",
    "germ_names",
    "check_witness_n",
    "check_rank_n_witness",
    "ac_bc_orbit_count_n",
]


def generators_of(words) -> tuple:
    """The sorted unsigned alphabet implied by ``words`` (re-derived, not imported)."""
    gens = set()
    for w in words:
        for c in w:
            if len(c) != 1 or not c.isalpha():
                raise WitnessError(f"bad letter {c!r}")
            gens.add(c.lower())
    return tuple(sorted(gens))


def germ_names(generators) -> tuple:
    out = []
    for g in generators:
        out.append(f"{g}+")
        out.append(f"{g}-")
    return tuple(out)


def _build(words, generators):
    """Rebuild darts, ``A``, ``B`` and the germ map from the exact words."""
    words = tuple(words)
    table = {}
    for k, g in enumerate(generators):
        if len(g) != 1 or not g.islower() or not g.isalpha():
            raise WitnessError(f"generator {g!r} must be a single lowercase letter")
        table[g] = (2 * k, 2 * k + 1)
        table[g.upper()] = (2 * k + 1, 2 * k)

    letters = []
    bounds = []
    for w in words:
        if not w:
            raise WitnessError("empty relator")
        bounds.append((len(letters), len(letters) + len(w)))
        for c in w:
            if c not in table:
                raise WitnessError(f"letter {c!r} is not over {tuple(generators)}")
            letters.append(c)
    n = len(letters)
    if n == 0:
        raise WitnessError("no occurrences")
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
        gd, gh = table[c]
        germ[2 * i], germ[2 * i + 1] = gd, gh
    return tuple(A), tuple(B), tuple(germ), size


def _normalise_rotation(rotation, names):
    """Accept ``{germ name or index: dart sequence}`` and return an index-keyed dict."""
    n_germs = len(names)
    out = {}
    for key, seq in rotation.items():
        if isinstance(key, str):
            if key not in names:
                raise WitnessError(f"unknown germ {key!r}; alphabet is {names}")
            idx = names.index(key)
        else:
            idx = int(key)
            if not 0 <= idx < n_germs:
                raise WitnessError(f"germ index out of range: {idx}")
        if idx in out:
            raise WitnessError(f"germ {names[idx]} listed twice")
        out[idx] = tuple(int(d) for d in seq)
    return out


def check_witness_n(words, rotation, generators=None, trivial_group: bool = True) -> dict:
    """Verify a claimed compatible spherical rotation at arbitrary rank."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    if len(set(generators)) != len(generators):
        raise WitnessError("duplicate generator")
    names = germ_names(generators)
    A, B, germ, size = _build(words, generators)
    orders = _normalise_rotation(rotation, names)

    # (1) valid rotation system
    present = sorted({germ[d] for d in range(size)})
    if sorted(orders) != present:
        raise WitnessError(
            f"rotation covers germs {[names[v] for v in sorted(orders)]}, "
            f"expected {[names[v] for v in present]}"
        )
    for v, seq in orders.items():
        want = sorted(d for d in range(size) if germ[d] == v)
        if sorted(seq) != want:
            raise WitnessError(f"germ {names[v]}: dart set {sorted(seq)} != {want}")
        if len(set(seq)) != len(seq):
            raise WitnessError(f"germ {names[v]}: repeated dart")

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
        tv = v ^ 1
        if tv not in orders:
            raise WitnessError(f"germ {names[tv]} missing while {names[v]} present")
        for d in seq:
            if B[C[B[d]]] != Cinv[d]:
                raise WitnessError(
                    f"compatibility C_[{names[tv]}] = B C_[{names[v]}]^-1 B "
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
        "words": words,
        "generators": generators,
        "germs": names,
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
    report["trivial_group_assumed"] = bool(trivial_group)
    if trivial_group and not report["ac_bc_transitive"]:
        raise AuditContradiction(
            "Euler passes (defect 0, L = 1) but <AC, BC> has "
            f"{report['ac_bc_orbits']} orbits with the right-to-left convention; "
            "Corollary 3 proves this cannot happen, so it is an audit contradiction "
            f"(words={words}, generators={generators})"
        )
    return report


def check_rank_n_witness(decision, trivial_group: bool = True) -> dict:
    """Convenience wrapper for a ``neuwirth_rank_n.RankNDecision`` carrying a witness.

    Only the witness's germ-name -> dart map and the decision's own words/generators are
    read; nothing about how the witness was found is trusted.
    """
    if decision.witness is None:
        raise WitnessError("decision carries no witness")
    return check_witness_n(decision.words, decision.witness.rotation_map(),
                           generators=decision.generators,
                           trivial_group=trivial_group)


def ac_bc_orbit_count_n(words, rotation, generators=None) -> int:
    """The number of ``<AC, BC>`` orbits, with no Euler precondition (audit helper)."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    names = germ_names(generators)
    A, B, germ, size = _build(words, generators)
    orders = _normalise_rotation(rotation, names)
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
