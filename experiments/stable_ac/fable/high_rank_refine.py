"""High-rank *refinements* of a balanced presentation, with a replay certifier.

This is task A3 of ``results/stable_ac/theory/fable/S0_HIGH_RANK_PLAN.md``: the
transform of plan section S-b (triangulation), a second family (generator splitting /
degree redistribution), and -- the part everything else leans on -- a **certifier that
replays the construction instead of trusting it**.

Vocabulary.  A *refinement* of a balanced presentation ``P = <g_1..g_n | r_1..r_n>``
is a balanced presentation ``P' = <g_1..g_n, z_1..z_t | D_1..D_t, R_1..R_n>`` in which

* each ``D_j`` is a **definition relator** ``z_j * w_j^{-1}`` with ``w_j`` a word in the
  strictly earlier generators (so ``D_j`` says ``z_j = w_j``), and
* substituting the definitions innermost-out into the **residual relators** ``R_i`` and
  freely reducing returns ``r_i`` up to cyclic rotation and inversion.

Plan section (S-a) is what makes this a *stable AC* statement: because ``P`` presents the
trivial group, AC4 may adjoin ``(z, z)`` and AC1-AC3 may then rewrite the relator ``z``
into ``z * w^{-1}`` for any ``w``.  **The triviality hypothesis is sharp** (FRAMING trap
2), and the chain is exponentially long in elementary moves (trap T-S5), so no move count
is ever quoted here.  This module manufactures and certifies the *combinatorics*; the
group-theoretic step is the plan's, not this file's.

Two refinement families
-----------------------

**(a) Triangulation** (S-b).  Peel a length-2 factor ``a1 a2`` off one end of a relator,
introduce ``z`` with the length-3 definition relator ``z a2^{-1} a1^{-1}``, and shorten
the relator to ``z a3...am``.  Iterate to relator length 3.  The choice family is
``bracket`` (``linear`` = the chain ``z1 = a1a2, z2 = z1a3, ...``; ``balanced`` = a
straight-line program that halves each block recursively), ``end`` (peel left or right),
``rot`` (which cyclic rotation of the relator is peeled), ``order`` (which relator is
worked first) and ``share`` (reuse an existing definition when the same 2-letter factor
comes up again -- this is the only option that leaves a fresh germ with degree > 2).

**(b) Generator splitting.**  Introduce ``u_1..u_t`` with length-2 definition relators
``u_i g^{-1}`` and redistribute the occurrences of ``g^{+-1}`` among ``g, u_1..u_t``.
This lowers the maximum germ degree, hence the size of the Neuwirth census.

Structural facts this module records (both verified in ``tests/fable/test_high_rank_refine.py``
and swept in ``high_rank_gamma_sweep.py``)
------------------------------------------------------------------------------------------

1. **Triangulation never changes a germ degree of an original generator.**  A peel moves
   ``a1 a2`` into the definition relator as ``a2^{-1} a1^{-1}``; occurrence counts of every
   original generator are therefore invariant, and every fresh germ has degree exactly 2
   (when ``share`` is off).  Since the compatible census has size
   ``prod_g (deg(g+) - 1)!`` and ``(2 - 1)! = 1``, **the census size is a triangulation
   invariant** -- plan section 2's hope that triangulation thins the link graph is false
   for the census.  What triangulation buys is short *relators*, not cheap *germs*.

2. **The link of ``P`` is a SUBDIVISION of the link of any triangulation of ``P`` with
   ``share`` off.**  Each fresh ``z`` puts a degree-2 germ ``z+`` in the middle of the
   original corner ``(a_m, a_1)`` and a degree-2 germ ``z-`` in the middle of the corner
   ``(a_2, a_3)``; every other corner is carried across unchanged.
   ``link_smoothing_certificate`` checks this on the labelled link multigraph, and returns
   ``is_subdivision = False`` for the ``share`` variant, whose reused definition leaves a
   fresh germ of degree 3 or more.  Subdividing an edge of a ribbon graph changes ``V``
   and ``E`` by one each and leaves the faces alone, and the rotation at a degree-2 germ
   is forced, so the whole compatible census -- histogram and all -- is carried across
   unchanged.  The ``share`` variant is the one member of the triangulation family that
   escapes this and is therefore the one worth pointing a search at.

3. **Generator splitting is a vertex split**, in the exact graph-theoretic sense: ``g+``
   is split into ``g+, u+`` and ``g-`` into ``g-, u-``, and the definition relator
   ``u g^{-1}`` contributes precisely the two edges ``{g+, u+}`` and ``{g-, u-}`` that make
   the original link a contraction of the refined one.  ``split_minor_certificate`` checks
   this.  Planarity is minor-closed, so a non-planar link can never be made planar by
   splitting.  (At rank 2 the link has only four germs and is therefore always planar, so
   this obstruction is vacuous for refinements of rank-2 inputs -- it bites only once a
   refinement has already produced a non-planar high-rank link.)

Nothing here decides thickenability; ``neuwirth_rank_n.gamma_N_factorial_n`` does that,
and ``high_rank_gamma_sweep.py`` drives it.
"""

from __future__ import annotations

import itertools
import os
import random
import sys
from dataclasses import dataclass

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable.ac_words import (            # noqa: E402
    free_reduce,
    inverse,
    inverse_letter,
    is_cyclically_reduced,
    is_freely_reduced,
)
from experiments.stable_ac.fable.neuwirth_rank_n import (     # noqa: E402
    build_link_n,
    census_size,
    generators_of,
    germ_names,
)

__all__ = [
    "free_reduce",
    "inverse",
    "inverse_letter",
    "is_freely_reduced",
    "is_cyclically_reduced",
    "RefinementError",
    "CertificationError",
    "Presentation",
    "Definition",
    "Refinement",
    "Certificate",
    "as_presentation",
    "rotate",
    "canonical_form",
    "fresh_pool",
    "germ_degrees",
    "census_of",
    "triangulate",
    "enumerate_triangulations",
    "split_generator",
    "enumerate_splits",
    "certify_refinement",
    "link_edge_multiset",
    "smooth_vertices",
    "link_smoothing_certificate",
    "split_minor_certificate",
    "TRIANGULATION_SCHEMES",
]

TRIANGULATION_SCHEMES = ("linear", "balanced")
ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class RefinementError(ValueError):
    """The refinement could not be built (bad parameters or an exhausted alphabet)."""


class CertificationError(AssertionError):
    """A candidate refinement failed the independent replay certificate."""


# --------------------------------------------------------------------------------------
# containers
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Presentation:
    """A balanced presentation: ``words`` over ``generators`` (repo letter convention)."""

    words: tuple
    generators: tuple

    @property
    def rank(self) -> int:
        return len(self.generators)

    @property
    def total_length(self) -> int:
        return sum(len(w) for w in self.words)

    def is_balanced(self) -> bool:
        return len(self.words) == len(self.generators)


@dataclass(frozen=True)
class Definition:
    """``gen = word``, carried by the length ``1 + len(word)`` relator ``gen word^{-1}``."""

    gen: str
    word: str

    @property
    def relator(self) -> str:
        return self.gen + inverse(self.word)


@dataclass
class Refinement:
    """A built refinement plus the generator's own (untrusted) bookkeeping."""

    scheme: str
    params: dict
    source: Presentation
    words: tuple
    generators: tuple
    definitions: tuple                 # tuple[Definition], in introduction order
    residuals: tuple                   # residual image of source.words[i], in order
    trace: tuple = ()
    certificate: "Certificate | None" = None

    @property
    def presentation(self) -> Presentation:
        return Presentation(self.words, self.generators)

    @property
    def rank(self) -> int:
        return len(self.generators)

    def as_row(self) -> dict:
        return {
            "scheme": self.scheme,
            "params": dict(self.params),
            "input_words": list(self.source.words),
            "input_generators": list(self.source.generators),
            "output_words": list(self.words),
            "output_generators": list(self.generators),
            "output_rank": self.rank,
            "definitions": [{"gen": d.gen, "word": d.word, "relator": d.relator}
                            for d in self.definitions],
            "residuals": list(self.residuals),
        }


@dataclass(frozen=True)
class Certificate:
    """What the replay actually established.  Produced only by :func:`certify_refinement`."""

    balanced: bool
    generators_extended: bool
    all_cyclically_reduced: bool
    definition_order: tuple            # fresh generators, in a re-derived legal order
    definition_words: tuple            # ((gen, word), ...) as re-read from P'
    expansions: tuple                  # ((gen, word over the ORIGINAL alphabet), ...)
    residual_relators: tuple
    substituted: tuple                 # freely reduced substitution of each residual
    matching: tuple                    # ((residual index, original index, relation), ...)
    relations: tuple                   # the multiset of relations, sorted
    trace_consistent: bool | None      # None when no trace was supplied
    ambiguous_definitions: tuple = ()  # ((gen, n_candidate_relators), ...) with n > 1
    layerings_examined: int = 0

    def as_row(self) -> dict:
        return {
            "balanced": self.balanced,
            "generators_extended": self.generators_extended,
            "all_cyclically_reduced": self.all_cyclically_reduced,
            "definition_order": list(self.definition_order),
            "definition_words": [list(p) for p in self.definition_words],
            "expansions": [list(p) for p in self.expansions],
            "matching": [list(m) for m in self.matching],
            "relations": list(self.relations),
            "trace_consistent": self.trace_consistent,
            "ambiguous_definitions": [list(p) for p in self.ambiguous_definitions],
            "layerings_examined": self.layerings_examined,
        }


# --------------------------------------------------------------------------------------
# small word / presentation helpers
# --------------------------------------------------------------------------------------


def as_presentation(obj) -> Presentation:
    """Accept a :class:`Presentation`, a :class:`Refinement`, or a tuple of words."""
    if isinstance(obj, Presentation):
        return obj
    if isinstance(obj, Refinement):
        return obj.presentation
    words = tuple(obj)
    return Presentation(words, generators_of(words))


def rotate(word: str, k: int) -> str:
    """The ``k``-th cyclic rotation of ``word`` (``k`` taken mod ``len(word)``)."""
    if not word:
        return word
    k %= len(word)
    return word[k:] + word[:k]


def _min_rotation(word: str) -> str:
    if not word:
        return word
    return min(word[i:] + word[:i] for i in range(len(word)))


def canonical_form(words) -> tuple:
    """Dedup key: every relator at its lexicographically least rotation, then sorted.

    This collapses relator reordering and cyclic rotation but **not** a renaming of the
    fresh generators; ``enumerate_triangulations`` therefore only varies ``order`` when
    ``share`` is on, where the parameter has an effect beyond relabelling.
    """
    return tuple(sorted(_min_rotation(w) for w in words))


def fresh_pool(used, alphabet: str = ALPHABET) -> list:
    """Lowercase letters not already used, in alphabetical order."""
    taken = {c.lower() for c in used}
    return [c for c in alphabet if c not in taken]


def germ_degrees(words, generators=None) -> dict:
    """``generator -> deg(g+)`` = number of occurrences of ``g^{+-1}`` across ``words``."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    data = build_link_n(words, generators)
    return {g: data.degree(2 * k) for k, g in enumerate(generators)}


def census_of(words, generators=None) -> int:
    """``prod_g (deg(g+) - 1)!`` -- the size of the compatible-rotation family."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    return census_size(build_link_n(words, generators), generators)


def _check_input(words, generators):
    words = tuple(words)
    if not words:
        raise RefinementError("no relators")
    for w in words:
        if not w:
            raise RefinementError("empty relator")
        if not is_cyclically_reduced(w):
            raise RefinementError(f"relator {w!r} is not cyclically reduced")
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    for g in generators:
        if len(g) != 1 or not g.islower() or not g.isalpha():
            raise RefinementError(f"generator {g!r} must be a single lowercase letter")
    unknown = {c.lower() for w in words for c in w} - set(generators)
    if unknown:
        raise RefinementError(f"letters {sorted(unknown)} outside the alphabet")
    return words, generators


# --------------------------------------------------------------------------------------
# family (a): triangulation
# --------------------------------------------------------------------------------------


class _Definer:
    """Hands out fresh generators and records ``z = w`` definitions in creation order."""

    def __init__(self, used, share: bool):
        self._pool = fresh_pool(used)
        self._share = share
        self._by_word: dict = {}
        self.definitions: list = []

    def define(self, word: str) -> tuple:
        """Return ``(symbol, created)`` for the factor ``word``."""
        if self._share and word in self._by_word:
            return self._by_word[word], False
        if not self._pool:
            raise RefinementError("alphabet exhausted: no fresh generator available")
        z = self._pool.pop(0)
        self._by_word[word] = z
        self.definitions.append(Definition(z, word))
        return z, True


def _peel_linear(word: str, definer: _Definer, end: str, rot: int, steps: list) -> str:
    """The chain ``z1 = a1a2, z2 = z1a3, ...`` down to length 3."""
    if end not in ("left", "right"):
        raise RefinementError(f"end must be 'left' or 'right', not {end!r}")
    w = rotate(word, rot)
    while len(w) > 3:
        factor = w[:2] if end == "left" else w[-2:]
        rest = w[2:] if end == "left" else w[:-2]
        z, created = definer.define(factor)
        w = (z + rest) if end == "left" else (rest + z)
        steps.append({"kind": "peel", "end": end, "factor": factor, "gen": z,
                      "created": created, "word_after": w})
    return w


def _encode_balanced(sub: str, definer: _Definer, steps: list) -> str:
    """A single symbol standing for ``sub``, via a halving straight-line program."""
    if len(sub) == 1:
        return sub
    half = len(sub) // 2
    left = _encode_balanced(sub[:half], definer, steps)
    right = _encode_balanced(sub[half:], definer, steps)
    z, created = definer.define(left + right)
    steps.append({"kind": "bracket", "factor": left + right, "gen": z,
                  "created": created, "covers": sub})
    return z


def _peel_balanced(word: str, definer: _Definer, rot: int, steps: list) -> str:
    """Split the relator into three near-equal blocks and encode each one."""
    w = rotate(word, rot)
    if len(w) <= 3:
        return w
    m = len(w)
    base, rem = divmod(m, 3)
    sizes = [base + (1 if i < rem else 0) for i in range(3)]
    parts = []
    at = 0
    for size in sizes:
        parts.append(w[at:at + size])
        at += size
    return "".join(_encode_balanced(p, definer, steps) for p in parts)


def triangulate(words, generators=None, *, bracket: str = "linear", end: str = "left",
                rot=0, order=None, share: bool = False) -> Refinement:
    """Triangulate every relator of ``words`` down to length <= 3.

    ``rot`` is either one integer (used for every relator) or one integer per relator.
    ``order`` is a permutation of the relator indices giving the *processing* order; it
    determines which relator gets the earlier fresh letters and, when ``share`` is on,
    which relator gets to create a shared definition.  The output tuple is always
    assembled in input-relator order: the definitions created while processing relator
    ``i`` (in creation order), then the residual of relator ``i``.
    """
    words, generators = _check_input(words, generators)
    if bracket not in TRIANGULATION_SCHEMES:
        raise RefinementError(f"unknown bracket {bracket!r}")
    n = len(words)
    if isinstance(rot, int):
        rots = tuple(rot % len(w) for w in words)
    else:
        rots = tuple(int(r) for r in rot)
        if len(rots) != n:
            raise RefinementError("one rotation per relator is required")
        rots = tuple(r % len(words[i]) for i, r in enumerate(rots))
    if order is None:
        order = tuple(range(n))
    else:
        order = tuple(int(i) for i in order)
        if sorted(order) != list(range(n)):
            raise RefinementError("order must be a permutation of the relator indices")

    definer = _Definer(generators, share)
    residuals = [None] * n
    per_relator_defs = [[] for _ in range(n)]
    trace = []
    for i in order:
        before = len(definer.definitions)
        steps: list = []
        if bracket == "linear":
            residuals[i] = _peel_linear(words[i], definer, end, rots[i], steps)
        else:
            residuals[i] = _peel_balanced(words[i], definer, rots[i], steps)
        per_relator_defs[i] = definer.definitions[before:]
        trace.append({"relator_index": i, "input": words[i], "rot": rots[i],
                      "bracket": bracket, "end": end if bracket == "linear" else None,
                      "steps": steps, "residual": residuals[i]})

    out_words = []
    for i in range(n):
        out_words.extend(d.relator for d in per_relator_defs[i])
        out_words.append(residuals[i])
    out_words = tuple(out_words)
    new_gens = tuple(d.gen for d in definer.definitions)
    out_generators = tuple(sorted(set(generators) | set(new_gens)))
    params = {"bracket": bracket, "end": end if bracket == "linear" else None,
              "rot": list(rots), "order": list(order), "share": bool(share)}
    return Refinement(
        scheme=f"triangulate-{bracket}",
        params=params,
        source=Presentation(words, generators),
        words=out_words,
        generators=out_generators,
        definitions=tuple(definer.definitions),
        residuals=tuple(residuals),
        trace=tuple(trace),
    )


def _triangulation_grid(words, schemes, share_options):
    """Every parameter tuple of the bounded triangulation family, in a fixed order."""
    n = len(words)
    rot_ranges = [range(len(w)) for w in words]
    grid = []
    for share in share_options:
        orders = [tuple(range(n))]
        if share and n > 1:
            orders.append(tuple(reversed(range(n))))
        for order in orders:
            for bracket in schemes:
                ends = ("left", "right") if bracket == "linear" else ("left",)
                for end in ends:
                    for rots in itertools.product(*rot_ranges):
                        grid.append({"bracket": bracket, "end": end, "rot": rots,
                                     "order": order, "share": share})
    return grid


def _stratify(grid, key, seed: int):
    """Round-robin the grid across the cells of ``key`` so a small limit stays diverse."""
    cells: dict = {}
    for params in grid:
        cells.setdefault(key(params), []).append(params)
    if seed:
        rng = random.Random(seed)
        for bucket in cells.values():
            rng.shuffle(bucket)
    order = sorted(cells)
    out = []
    depth = 0
    while len(out) < len(grid):
        for name in order:
            bucket = cells[name]
            if depth < len(bucket):
                out.append(bucket[depth])
        depth += 1
    return out


def enumerate_triangulations(words, limit: int = 8, seed: int = 0, generators=None,
                             schemes=TRIANGULATION_SCHEMES, share_options=(False, True),
                             certify: bool = True) -> list:
    """Up to ``limit`` DISTINCT certified triangulations of ``words``.

    Distinctness is on :func:`canonical_form` of the output tuple.  The parameter grid is
    deterministic and is walked round-robin across the ``(bracket, end, share)`` cells,
    with ``seed`` (when non-zero) permuting *within* each cell, so a small ``limit`` still
    meets every scheme rather than one corner of one scheme.  The same
    ``(words, limit, seed)`` always yields the same list.
    """
    words, generators = _check_input(words, generators)
    grid = _triangulation_grid(words, tuple(schemes), tuple(share_options))
    grid = _stratify(grid, lambda p: (p["bracket"], p["end"], p["share"]), seed)
    out: list = []
    seen: set = set()
    for params in grid:
        if len(out) >= limit:
            break
        try:
            ref = triangulate(words, generators, **params)
        except RefinementError:
            continue
        key = canonical_form(ref.words)
        if key in seen:
            continue
        seen.add(key)
        if certify:
            ref.certificate = certify_refinement(ref.source, ref.presentation, ref.trace)
        out.append(ref)
    return out


# --------------------------------------------------------------------------------------
# family (b): generator splitting / degree redistribution
# --------------------------------------------------------------------------------------


def occurrences_of(words, gen: str) -> tuple:
    """``((relator index, position), ...)`` of every ``gen^{+-1}`` letter, in reading order."""
    out = []
    for i, w in enumerate(words):
        for j, c in enumerate(w):
            if c.lower() == gen:
                out.append((i, j))
    return tuple(out)


def split_generator(words, generators=None, *, gen: str, buckets) -> Refinement:
    """Split ``gen`` into ``gen, u_1..u_t`` by redistributing its occurrences.

    ``buckets`` assigns a bucket index to each occurrence of ``gen^{+-1}`` in reading
    order; bucket ``0`` keeps ``gen`` and bucket ``i >= 1`` is carried by a fresh
    generator ``u_i`` with the length-2 definition relator ``u_i gen^{-1}``.  Every
    bucket ``i >= 1`` must be non-empty (an unused ``u_i`` would leave a degree-1 germ).
    """
    words, generators = _check_input(words, generators)
    if gen not in generators:
        raise RefinementError(f"{gen!r} is not a generator of the input")
    occ = occurrences_of(words, gen)
    buckets = tuple(int(b) for b in buckets)
    if len(buckets) != len(occ):
        raise RefinementError(
            f"buckets has {len(buckets)} entries but {gen!r} occurs {len(occ)} times"
        )
    if any(b < 0 for b in buckets):
        raise RefinementError("bucket indices must be non-negative")
    t = max(buckets) if buckets else 0
    for i in range(1, t + 1):
        if i not in buckets:
            raise RefinementError(f"bucket {i} is empty; every fresh generator must be used")
    if t == 0:
        raise RefinementError("splitting with no fresh generator is a no-op")

    pool = fresh_pool(generators)
    if len(pool) < t:
        raise RefinementError("alphabet exhausted: no fresh generator available")
    fresh = [pool[i] for i in range(t)]

    rows = [list(w) for w in words]
    for (i, j), b in zip(occ, buckets):
        if b == 0:
            continue
        u = fresh[b - 1]
        rows[i][j] = u if rows[i][j].islower() else u.upper()
    residuals = tuple("".join(r) for r in rows)

    definitions = tuple(Definition(u, gen) for u in fresh)
    out_words = tuple(d.relator for d in definitions) + residuals
    out_generators = tuple(sorted(set(generators) | set(fresh)))
    params = {"gen": gen, "buckets": list(buckets), "fresh": list(fresh),
              "n_occurrences": len(occ)}
    trace = ({"kind": "split", "gen": gen, "fresh": list(fresh),
              "occurrences": [list(o) for o in occ], "buckets": list(buckets)},)
    return Refinement(
        scheme="split-generator",
        params=params,
        source=Presentation(words, generators),
        words=out_words,
        generators=out_generators,
        definitions=definitions,
        residuals=residuals,
        trace=trace,
    )


def _bucket_patterns(k: int, rng: random.Random, extras: int = 4):
    """A bounded, deterministic family of bucket assignments for ``k`` occurrences."""
    seen = set()
    out = []

    def add(pattern):
        pattern = tuple(pattern)
        if len(set(pattern)) < 2:
            return
        # normalise so bucket labels appear in increasing order of first use
        remap: dict = {}
        for b in pattern:
            if b not in remap:
                remap[b] = len(remap)
        pattern = tuple(remap[b] for b in pattern)
        if pattern[0] != 0:
            return
        if pattern in seen:
            return
        seen.add(pattern)
        out.append(pattern)

    for j in range(1, k):                                  # contiguous 2-way splits
        add([0] * j + [1] * (k - j))
    add([i % 2 for i in range(k)])                         # alternating 2-way
    if k >= 3:                                             # contiguous 3-way, near-equal
        base, rem = divmod(k, 3)
        sizes = [base + (1 if i < rem else 0) for i in range(3)]
        pattern = []
        for b, size in enumerate(sizes):
            pattern.extend([b] * size)
        add(pattern)
        add([i % 3 for i in range(k)])                     # alternating 3-way
    for _ in range(extras):
        add([rng.randrange(2) for _ in range(k)])
    return out


def enumerate_splits(words, limit: int = 8, seed: int = 0, generators=None,
                     certify: bool = True) -> list:
    """Up to ``limit`` DISTINCT certified generator splittings of ``words``."""
    words, generators = _check_input(words, generators)
    rng = random.Random(seed or 1)
    grid = []
    for gen in generators:
        k = len(occurrences_of(words, gen))
        if k < 2:
            continue
        for pattern in _bucket_patterns(k, rng):
            grid.append({"gen": gen, "buckets": pattern})
    grid = _stratify(grid, lambda p: (p["gen"], max(p["buckets"])), seed)
    out: list = []
    seen: set = set()
    for params in grid:
        if len(out) >= limit:
            break
        try:
            ref = split_generator(words, generators, **params)
        except RefinementError:
            continue
        key = canonical_form(ref.words)
        if key in seen:
            continue
        seen.add(key)
        if certify:
            ref.certificate = certify_refinement(ref.source, ref.presentation, ref.trace)
        out.append(ref)
    return out


# --------------------------------------------------------------------------------------
# THE CERTIFIER -- reads P' back from scratch, never from the builder's bookkeeping
# --------------------------------------------------------------------------------------


def _relation(u: str, v: str):
    """How ``u`` is related to ``v``: identical / rotation / inversion / both / None."""
    if u == v:
        return "identical"
    if len(u) != len(v):
        return None
    if len(v) and any(u == rotate(v, i) for i in range(1, len(v))):
        return "rotation"
    vi = inverse(v)
    if u == vi:
        return "inversion"
    if len(vi) and any(u == rotate(vi, i) for i in range(1, len(vi))):
        return "rotation+inversion"
    return None


def _match_up_to_rotation_and_inversion(substituted, originals):
    """A bijection substituted -> originals, or ``None``.  Sizes are small; backtrack."""
    n = len(substituted)
    table = [[_relation(substituted[a], originals[b]) for b in range(n)]
             for a in range(n)]
    used = [False] * n
    choice = [None] * n

    def rec(a: int):
        if a == n:
            return True
        for b in range(n):
            if used[b] or table[a][b] is None:
                continue
            used[b] = True
            choice[a] = (a, b, table[a][b])
            if rec(a + 1):
                return True
            used[b] = False
            choice[a] = None
        return False

    if not rec(0):
        return None
    return tuple(choice)


def _expand(word: str, expansions: dict) -> str:
    """Substitute fully-expanded definitions into ``word`` and freely reduce."""
    out = []
    for c in word:
        g = c.lower()
        if g in expansions:
            piece = expansions[g]
            out.append(piece if c.islower() else inverse(piece))
        else:
            out.append(c)
    return free_reduce("".join(out))


def _topological_order(definition_of: dict):
    """A legal definition order for ``gen -> word``, or ``None`` if it is cyclic."""
    fresh = set(definition_of)
    deps = {z: {c.lower() for c in w if c.lower() in fresh} for z, w in definition_of.items()}
    order: list = []
    ready = sorted(z for z, d in deps.items() if not d)
    done: set = set()
    while ready:
        z = ready.pop(0)
        order.append(z)
        done.add(z)
        newly = []
        for y, d in deps.items():
            if y in done or y in ready:
                continue
            if d <= done:
                newly.append(y)
        ready = sorted(set(ready) | set(newly))
    if len(order) != len(fresh):
        return None
    return tuple(order)


def _declared_layering_ok(Pprime: Presentation, fresh: set, declared) -> bool:
    """Is the trace's own claimed set of definitions itself a legal layering of ``P'``?"""
    if not declared:
        return False
    seen: dict = {}
    for z, w in declared:
        if z in seen and seen[z] != w:
            return False
        seen[z] = w
    if set(seen) != fresh:
        return False
    relators = list(Pprime.words)
    for z, w in seen.items():
        relator = z + inverse(w)
        if relator not in relators:
            return False
        relators.remove(relator)
    return _topological_order(seen) is not None


def certify_refinement(P, Pprime, trace=None, max_layerings: int = 20_000) -> Certificate:
    """Independently verify that ``Pprime`` is a refinement of ``P``.

    The check is a *replay*: the definition layering is re-derived from ``Pprime``'s
    relators alone, the definitions are expanded innermost-out into the residual relators,
    and the freely reduced results are matched against ``P``'s relators up to cyclic
    rotation and inversion.  None of the builder's bookkeeping (``Refinement.definitions``,
    ``Refinement.residuals``, ``Refinement.params``) is consulted; ``trace``, when given,
    is only cross-checked at the end and its verdict is reported, never relied on.

    Reading the layering back out of ``P'`` is genuinely ambiguous -- for the AK(3) linear
    triangulation, ``cyB`` and ``cXY`` are both syntactically ``c * (earlier word)^{-1}``
    -- so every injective, acyclic assignment of fresh generators to candidate definition
    relators is tried (bounded by ``max_layerings``) and the certificate reports how many
    generators were ambiguous.  The claim established is existential: *some* legal
    definition layering of ``P'`` replays to ``P``.

    Raises :class:`CertificationError` on any failure.  Returns a :class:`Certificate`
    recording, among other things, which relation (identical / rotation / inversion /
    rotation+inversion) each residual bore to its original.
    """
    P = as_presentation(P)
    Pprime = as_presentation(Pprime)

    # ---- (0) shape ------------------------------------------------------------------
    if not P.is_balanced():
        raise CertificationError(
            f"input is not balanced: {len(P.generators)} generators, {len(P.words)} relators"
        )
    if not Pprime.is_balanced():
        raise CertificationError(
            f"refinement is not balanced: {len(Pprime.generators)} generators, "
            f"{len(Pprime.words)} relators"
        )
    old = set(P.generators)
    new = set(Pprime.generators)
    if not old <= new:
        raise CertificationError(
            f"refinement drops generator(s) {sorted(old - new)} of the input"
        )
    fresh = new - old
    if len(Pprime.words) != len(P.words) + len(fresh):
        raise CertificationError(
            f"{len(fresh)} fresh generators but {len(Pprime.words) - len(P.words)} "
            "extra relators"
        )

    # ---- (1) every relator freely and cyclically reduced, over the alphabet ---------
    for w in Pprime.words:
        if not w:
            raise CertificationError("refinement has an empty relator")
        bad = {c.lower() for c in w} - new
        if bad:
            raise CertificationError(f"relator {w!r} uses letters {sorted(bad)} "
                                     "outside the refined alphabet")
        if not is_freely_reduced(w):
            raise CertificationError(f"relator {w!r} is not freely reduced")
        if not is_cyclically_reduced(w):
            raise CertificationError(f"relator {w!r} is not cyclically reduced")

    # ---- (2) candidate definition relators, read off P' alone -----------------------
    candidates: dict = {z: [] for z in sorted(fresh)}
    for idx, w in enumerate(Pprime.words):
        z = w[0]
        if not z.islower() or z not in fresh:
            continue
        if any(c.lower() == z for c in w[1:]):        # a definition may not use itself
            continue
        candidates[z].append(idx)
    empty = [z for z, idxs in candidates.items() if not idxs]
    if empty:
        raise CertificationError(
            f"generator(s) {empty} have no relator of the form z * (word)^{{-1}}; "
            "they are not defined by the refinement"
        )
    ambiguous = tuple((z, len(idxs)) for z, idxs in sorted(candidates.items())
                      if len(idxs) > 1)
    budget = 1
    for idxs in candidates.values():
        budget *= len(idxs)
    if budget > max_layerings:
        raise CertificationError(
            f"{budget} candidate definition layerings exceed the search budget "
            f"{max_layerings}; the refinement is not certified"
        )

    # ---- (3) search the layerings; expand innermost-out and replay ------------------
    keys = sorted(candidates)
    examined = 0
    failure = "no injective, acyclic definition layering exists"
    for combo in itertools.product(*(candidates[z] for z in keys)):
        examined += 1
        if len(set(combo)) != len(combo):             # two generators, one relator
            continue
        definition_of = {z: inverse(Pprime.words[idx][1:]) for z, idx in zip(keys, combo)}
        order = _topological_order(definition_of)
        if order is None:
            continue
        expansions: dict = {}
        broken = None
        for z in order:
            expansions[z] = _expand(definition_of[z], expansions)
            leftover = {c.lower() for c in expansions[z]} - old
            if leftover:
                broken = (f"definition of {z!r} does not expand into the input alphabet "
                          f"(leftover {sorted(leftover)})")
                break
        if broken:
            failure = broken
            continue
        residual_idx = tuple(i for i in range(len(Pprime.words)) if i not in set(combo))
        if len(residual_idx) != len(P.words):
            raise CertificationError(
                f"{len(residual_idx)} residual relators but the input has {len(P.words)}"
            )
        residuals = tuple(Pprime.words[i] for i in residual_idx)
        substituted = tuple(_expand(w, expansions) for w in residuals)
        matching = _match_up_to_rotation_and_inversion(substituted, P.words)
        if matching is None:
            failure = ("substitution does not reproduce the input relators up to cyclic "
                       f"rotation and inversion: got {list(substituted)}, "
                       f"expected {list(P.words)}")
            continue

        # ---- (4) optional, non-load-bearing cross-check of the supplied trace -------
        trace_consistent = None
        if trace is not None:
            declared = []
            for step in trace:
                if step.get("kind") == "split":
                    declared.extend((u, step["gen"]) for u in step.get("fresh", ()))
                for sub in step.get("steps", ()):
                    if sub.get("created"):
                        declared.append((sub["gen"], sub["factor"]))
            trace_consistent = _declared_layering_ok(Pprime, fresh, declared)

        return Certificate(
            balanced=True,
            generators_extended=True,
            all_cyclically_reduced=True,
            definition_order=order,
            definition_words=tuple((z, definition_of[z]) for z in order),
            expansions=tuple((z, expansions[z]) for z in order),
            residual_relators=residuals,
            substituted=substituted,
            matching=matching,
            relations=tuple(sorted(rel for _, _, rel in matching)),
            trace_consistent=trace_consistent,
            ambiguous_definitions=ambiguous,
            layerings_examined=examined,
        )

    raise CertificationError(
        f"no legal definition layering of {list(Pprime.words)} replays to "
        f"{list(P.words)} after {examined} attempt(s): {failure}"
    )


# --------------------------------------------------------------------------------------
# link-graph structure: subdivision (triangulation) and vertex split (generator split)
# --------------------------------------------------------------------------------------


def link_edge_multiset(words, generators=None) -> list:
    """The labelled edge list of the link multigraph: one edge per corner of a relator.

    Vertices are germ *names* (``'x+'``, ``'x-'``, ...), so links of different
    presentations over overlapping alphabets are directly comparable.
    """
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    data = build_link_n(words, generators)
    names = germ_names(generators)
    return sorted(tuple(sorted((names[data.germ[a]], names[data.germ[b]])))
                  for a, b in data.edge_darts)


def support_planarity(words, generators=None, budget: int = 2_000_000) -> str:
    """``PLANAR`` / ``NONPLANAR`` / ``UNDETERMINED`` for the SIMPLE support of the link.

    This calls ``neuwirth_rank_n.macro_rotations`` directly rather than
    ``classify_support_n``, because the latter is fail-closed on relators shorter than
    three letters and a generator splitting always produces length-2 definition relators.
    Planarity of the simple support is a *necessary* condition for ``gamma_N = 0``, and it
    is the quantity the minor argument controls.
    """
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    from experiments.stable_ac.fable.neuwirth_rank_n import (   # local: avoids a cycle
        macro_rotations,
        simple_support,
    )
    data = build_link_n(words, generators)
    vertices, edges, adj = simple_support(data)
    return macro_rotations(vertices, edges, adj, budget=budget).status


def smooth_vertices(edges, targets) -> list:
    """Suppress each degree-2 vertex in ``targets``: its two edges become one.

    ``edges`` is a list of unordered pairs (as 2-tuples); the result is the edge list of
    the graph in which each target has been smoothed away.  A target whose two ends lie
    on the same edge (a loop) has that loop removed.  Raises if a target does not have
    exactly two ends.
    """
    edges = [tuple(e) for e in edges]
    for t in targets:
        ends = []
        for i, (u, v) in enumerate(edges):
            if u == t:
                ends.append(i)
            if v == t:
                ends.append(i)
        if len(ends) != 2:
            raise RefinementError(
                f"vertex {t!r} has {len(ends)} ends, not 2; it cannot be smoothed"
            )
        i, j = ends
        if i == j:                                    # a loop at t: drop it
            edges = [e for k, e in enumerate(edges) if k != i]
            continue
        a = edges[i][0] if edges[i][1] == t else edges[i][1]
        b = edges[j][0] if edges[j][1] == t else edges[j][1]
        keep = [e for k, e in enumerate(edges) if k not in (i, j)]
        keep.append(tuple(sorted((a, b))))
        edges = keep
    return sorted(edges)


def link_smoothing_certificate(P, Pprime) -> dict:
    """Is the link of ``Pprime`` a subdivision of the link of ``P`` at its fresh germs?

    Returns a dict with ``is_subdivision`` plus the evidence.  A ``True`` means every
    fresh germ has degree exactly 2 and suppressing all of them returns the labelled link
    multigraph of ``P`` edge for edge.  Because a subdivision has the same faces as the
    original for the induced rotation, this is the structural reason the whole compatible
    census -- and hence gamma_N -- is a triangulation invariant.
    """
    P = as_presentation(P)
    Pprime = as_presentation(Pprime)
    fresh = tuple(sorted(set(Pprime.generators) - set(P.generators)))
    degrees = germ_degrees(Pprime.words, Pprime.generators)
    fresh_germs = [n for g in fresh for n in (f"{g}+", f"{g}-")]
    bad = [g for g in fresh if degrees.get(g) != 2]
    before = link_edge_multiset(Pprime.words, Pprime.generators)
    target = link_edge_multiset(P.words, P.generators)
    if bad:
        return {"is_subdivision": False, "fresh_generators": list(fresh),
                "fresh_degrees": {g: degrees.get(g) for g in fresh},
                "reason": f"fresh generator(s) {bad} do not have germ degree 2",
                "edges_after": None, "edges_target": target}
    try:
        after = smooth_vertices(before, fresh_germs)
    except RefinementError as exc:
        return {"is_subdivision": False, "fresh_generators": list(fresh),
                "fresh_degrees": {g: degrees.get(g) for g in fresh},
                "reason": str(exc), "edges_after": None, "edges_target": target}
    return {"is_subdivision": after == target,
            "fresh_generators": list(fresh),
            "fresh_degrees": {g: degrees.get(g) for g in fresh},
            "reason": None if after == target else "smoothed link differs from the input link",
            "edges_after": after, "edges_target": target}


def split_minor_certificate(refinement: Refinement) -> dict:
    """Is the link of the input a CONTRACTION of the link of a generator splitting?

    For a splitting of ``g`` into ``g, u_1..u_t`` the definition relator ``u_i g^{-1}``
    contributes exactly the two edges ``{g+, u_i+}`` and ``{g-, u_i-}``.  Contracting all
    of them -- i.e. relabelling every ``u_i+`` to ``g+`` and every ``u_i-`` to ``g-`` and
    deleting the resulting loops -- must return the input's labelled link multigraph.
    That makes the input link a MINOR of the refined link, and planarity is minor-closed.
    """
    if refinement.scheme != "split-generator":
        raise RefinementError("split_minor_certificate applies to split-generator only")
    gen = refinement.params["gen"]
    fresh = tuple(refinement.params["fresh"])
    rename = {}
    for u in fresh:
        rename[f"{u}+"] = f"{gen}+"
        rename[f"{u}-"] = f"{gen}-"
    before = link_edge_multiset(refinement.words, refinement.generators)
    contracted = []
    dropped = 0
    for u, v in before:
        a, b = rename.get(u, u), rename.get(v, v)
        if a == b:
            dropped += 1
            continue
        contracted.append(tuple(sorted((a, b))))
    contracted.sort()
    target = link_edge_multiset(refinement.source.words, refinement.source.generators)
    return {"is_contraction": contracted == target,
            "contracted_edges": dropped,
            "expected_contracted_edges": 2 * len(fresh),
            "edges_after": contracted,
            "edges_target": target}
