"""R10 / Zeeman route: collapsibility certificates for K x I.

NEW FILE.  Pure CPU, standard library only (no numpy, no numba, no JAX).

Motivation
----------
Zeeman's conjecture: for every contractible finite 2-polyhedron ``K``, the product
``K x I`` is collapsible (after subdivision).  For a *single named* complex the
question "does this triangulation of ``K x I`` collapse?" is a finite combinatorial
search, and a successful collapse is a **complete positive certificate**: a finite
list of free-face collapses that any third party can replay.

The certificate we chase for a presentation ``P`` is a pair of explicit collapse
sequences on one fixed triangulation ``K'`` of the presentation 2-complex:

    (a)  K' x I  \\searrow  K' x {0}        (the expansion leg, reversed)
    (b)  K' x I  \\searrow  point           (the collapse leg)

Together, (a) reversed followed by (b) is a formal deformation of ``K'`` to a point
through complexes of dimension <= 3, i.e. a **3-deformation**.  See
``results/stable_ac/theory/fable/R10_ZEEMAN_ROUTE.md`` for exactly which links of the
chain "3-deformation ==> stably AC-trivial" are sourced and which are not.

Scope note (project rule): this module runs **no AC search** at all -- no
presentation-space node expansion, no move tree, no ``node_budget``.  The standing
"never run an AC search above node_budget 1,000" rule therefore does not bind
anything here.  What is searched is the free-face collapse tree of a *fixed finite
simplicial complex*, which is a different object entirely.

Everything in this file is deterministic given a seed.

Contents
--------
* simplicial-complex primitives (``closure``, ``Complex``)
* builders: ``presentation_complex`` (one vertex, |gens| loops, one 2-cell per
  relator, subdivided into an honest simplicial complex), ``prism`` (``K x I``),
  ``bing_house``, ``simplex_ball``, ``disc``
* the collapse engine (incremental free-face bookkeeping) and a restarted search
* ``verify_collapse_sequence``: an INDEPENDENT replay verifier that shares no
  bookkeeping with the search and recomputes every incidence by brute force
* integer simplicial homology (Smith normal form) for the sanity checks
* ``pi1_presentation`` + ``tietze_simplify``: an edge-path presentation of pi_1 of a
  simplicial complex, for complexes (Bing's house) that do not arrive as a
  presentation complex
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

Face = Tuple[int, ...]


# =====================================================================================
# simplicial complex primitives
# =====================================================================================


def _subfacets(face: Face) -> List[Face]:
    """The codimension-one faces of ``face`` (empty for a vertex)."""
    n = len(face)
    if n <= 1:
        return []
    return [face[:i] + face[i + 1:] for i in range(n)]


def closure(facets: Iterable[Iterable[int]]) -> Set[Face]:
    """Downward closure: every nonempty face of every listed simplex."""
    out: Set[Face] = set()
    stack: List[Face] = []
    for f in facets:
        t = tuple(sorted(set(f)))
        if t:
            stack.append(t)
    while stack:
        f = stack.pop()
        if f in out:
            continue
        out.add(f)
        stack.extend(_subfacets(f))
    return out


class Complex:
    """A finite abstract simplicial complex, stored as its full face set."""

    def __init__(self, faces: Iterable[Face], name: str = ""):
        self.faces: FrozenSet[Face] = frozenset(faces)
        self.name = name

    @classmethod
    def from_facets(cls, facets: Iterable[Iterable[int]], name: str = "") -> "Complex":
        return cls(closure(facets), name)

    # -- basic invariants ------------------------------------------------------------
    @property
    def dim(self) -> int:
        return max((len(f) for f in self.faces), default=0) - 1

    def f_vector(self) -> List[int]:
        counts: Dict[int, int] = {}
        for f in self.faces:
            counts[len(f) - 1] = counts.get(len(f) - 1, 0) + 1
        if not counts:
            return []
        return [counts.get(d, 0) for d in range(max(counts) + 1)]

    def n_faces(self) -> int:
        return len(self.faces)

    def euler_characteristic(self) -> int:
        return sum((-1) ** (len(f) - 1) for f in self.faces)

    def vertices(self) -> List[int]:
        return sorted(f[0] for f in self.faces if len(f) == 1)

    def faces_of_dim(self, d: int) -> List[Face]:
        return sorted(f for f in self.faces if len(f) == d + 1)

    def is_closed(self) -> bool:
        """Sanity: the face set really is downward closed."""
        return all(s in self.faces for f in self.faces for s in _subfacets(f))

    def free_faces(self) -> List[Tuple[Face, Face]]:
        """All free-face pairs ``(tau, sigma)`` of the complex (brute force)."""
        up: Dict[Face, List[Face]] = {f: [] for f in self.faces}
        for f in self.faces:
            for s in _subfacets(f):
                up[s].append(f)
        out = []
        for f in self.faces:
            if len(up[f]) == 1 and not up[up[f][0]]:
                out.append((f, up[f][0]))
        return sorted(out)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"Complex({self.name!r}, f={self.f_vector()}, chi={self.euler_characteristic()})"


# =====================================================================================
# builders
# =====================================================================================


def presentation_complex(
    words: Sequence[str],
    generators: Optional[Sequence[str]] = None,
    subdivision: int = 3,
    name: str = "",
) -> Tuple[Complex, Dict[str, object]]:
    """A simplicial model of the presentation 2-complex of ``<generators | words>``.

    Convention (the project's): a word is a string over single lowercase generator
    letters; an uppercase letter denotes the inverse of its generator.  Words are
    used **exactly as spelled** -- no free reduction -- because the 2-complex, and
    hence collapsibility, depends on the spelling (the dunce hat is the 2-complex of
    the *unreduced* word ``xxX``).

    Construction, chosen so the quotient is honestly simplicial:

    * one base vertex ``v``; each generator loop is subdivided into ``subdivision``
      (>= 3) edges, so the 1-skeleton is a simple graph -- a bouquet of
      ``subdivision``-cycles glued at ``v``;
    * each relator ``w`` gives a disc attached along the closed edge-walk of length
      ``m = subdivision * len(w)``.  The disc is triangulated as an **annular collar
      plus a cone**: an outer ring of ``m`` fresh vertices is *not* used; instead the
      outer boundary of the collar is the walk itself, the inner boundary is a fresh
      ``m``-cycle ``u_0..u_{m-1}``, and a fresh apex ``c`` cones off the inner cycle.

    The collar is what makes the quotient simplicial: every triangle contains at
    least one fresh vertex, and consecutive walk vertices are always distinct
    because each step of the walk is an edge of the 1-skeleton.

    Returns ``(complex, info)``.
    """
    if subdivision < 3:
        raise ValueError("subdivision must be >= 3 for the 1-skeleton to be simplicial")
    if generators is None:
        generators = sorted({c.lower() for w in words for c in w})
    generators = list(generators)
    for g in generators:
        if len(g) != 1 or not g.islower():
            raise ValueError(f"generator {g!r} must be a single lowercase character")

    labels: List[str] = []

    def new(label: str) -> int:
        labels.append(label)
        return len(labels) - 1

    base = new("v")
    chain: Dict[str, List[int]] = {}
    edge_facets: List[Tuple[int, int]] = []
    for g in generators:
        interior = [new(f"{g}{i + 1}") for i in range(subdivision - 1)]
        seq = [base] + interior + [base]
        chain[g] = seq
        for i in range(subdivision):
            a, b = seq[i], seq[i + 1]
            edge_facets.append((a, b) if a < b else (b, a))

    facets: List[Tuple[int, ...]] = list(edge_facets)
    walks: List[List[int]] = []
    for k, w in enumerate(words):
        walk = [base]
        for ch in w:
            g = ch.lower()
            if g not in chain:
                raise ValueError(f"letter {ch!r} is not over {tuple(generators)}")
            seq = chain[g] if ch.islower() else list(reversed(chain[g]))
            walk.extend(seq[1:])
        if walk[0] != walk[-1]:
            raise AssertionError("relator walk is not closed")
        p = walk[:-1]
        m = len(p)
        if m < 3:
            raise ValueError("relator walk too short; increase subdivision")
        for i in range(m):
            if p[i] == p[(i + 1) % m]:
                raise AssertionError("relator walk has a repeated consecutive vertex")
        u = [new(f"u{k}_{i}") for i in range(m)]
        c = new(f"c{k}")
        for i in range(m):
            j = (i + 1) % m
            facets.append(tuple(sorted((p[i], p[j], u[i]))))
            facets.append(tuple(sorted((p[j], u[i], u[j]))))
            facets.append(tuple(sorted((c, u[i], u[j]))))
        walks.append(p)

    cx = Complex.from_facets(facets, name or f"K<{','.join(generators)}|{','.join(words)}>")
    info = {
        "generators": generators,
        "words": list(words),
        "subdivision": subdivision,
        "labels": labels,
        "walks": walks,
        "base_vertex": base,
    }
    return cx, info


def prism(cx: Complex, layers: int = 1, name: str = "") -> Tuple[Complex, Set[Face]]:
    """The standard staircase triangulation of ``K x [0, layers]`` (~ ``K x I``).

    Vertex ``v`` at level ``j`` is ``v + j * n``.  For every face
    ``sigma = [v_0 < ... < v_d]`` of ``K`` and every level ``j`` the prism
    ``sigma x [j, j+1]`` is cut into the ``d+1`` simplices

        [ (v_0,j), ..., (v_i,j), (v_i,j+1), ..., (v_d,j+1) ],  i = 0..d,

    which is the classical simplicial product triangulation.  Returns the complex
    and the face set of the bottom copy ``K x {0}``.
    """
    verts = cx.vertices()
    if not verts:
        raise ValueError("empty complex")
    n = max(verts) + 1
    facets: List[Tuple[int, ...]] = []
    for f in cx.faces:
        d = len(f) - 1
        for j in range(layers):
            lo = tuple(v + j * n for v in f)
            hi = tuple(v + (j + 1) * n for v in f)
            for i in range(d + 1):
                facets.append(lo[: i + 1] + hi[i:])
    out = Complex.from_facets(facets, name or f"{cx.name} x I")
    bottom = frozenset(cx.faces)
    return out, set(bottom)


def simplex_ball(d: int) -> Complex:
    """The full ``d``-simplex (a collapsible ``d``-ball)."""
    return Complex.from_facets([tuple(range(d + 1))], name=f"simplex^{d}")


def disc(n: int = 6) -> Complex:
    """A triangulated ``n``-gon disc, coned from vertex 0 (collapsible)."""
    return Complex.from_facets(
        [(0, i, i + 1) for i in range(1, n)] + [(0, 1, n)], name=f"disc_{n}"
    )


def sphere2() -> Complex:
    """The boundary of the 3-simplex (not contractible, no free faces)."""
    return Complex.from_facets(
        [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)], name="S^2"
    )


def bing_house() -> Tuple[Complex, Dict[str, object]]:
    """Bing's house with two rooms, built as a grid cubical complex and triangulated.

    Box ``[0,3] x [0,5] x [0,2]``, unit cells.  The upper tunnel is the column over
    cell ``(1,1)`` between ``z = 1`` and ``z = 2``; the lower tunnel is the column
    over cell ``(1,3)`` between ``z = 0`` and ``z = 1``.  Both are interior cells and
    they are not adjacent.  Each tunnel is joined to the outer wall ``x = 0`` by a
    supporting membrane glued along all four of its edges (three-sided membranes
    would leave a free edge, and Bing's house famously has none -- the test suite
    asserts this).

    Returns ``(complex, info)`` where ``info['squares']`` is the cubical face list.
    """
    NX, NY = 3, 5  # cells in x and y
    UP_CELL = (1, 1)   # upper tunnel footprint (x in [1,2], y in [1,2])
    LOW_CELL = (1, 3)  # lower tunnel footprint (x in [1,2], y in [3,4])

    squares: List[Tuple[Tuple[int, int, int], ...]] = []

    def sq_z(i: int, j: int, k: int):
        return ((i, j, k), (i + 1, j, k), (i + 1, j + 1, k), (i, j + 1, k))

    def sq_x(i: int, j: int, k: int):
        return ((i, j, k), (i, j + 1, k), (i, j + 1, k + 1), (i, j, k + 1))

    def sq_y(i: int, j: int, k: int):
        return ((i, j, k), (i + 1, j, k), (i + 1, j, k + 1), (i, j, k + 1))

    # horizontal sheets
    for i in range(NX):
        for j in range(NY):
            if (i, j) != UP_CELL:
                squares.append(sq_z(i, j, 2))          # ceiling, hole over upper tunnel
            if (i, j) != LOW_CELL:
                squares.append(sq_z(i, j, 0))          # floor, hole under lower tunnel
            if (i, j) not in (UP_CELL, LOW_CELL):
                squares.append(sq_z(i, j, 1))          # middle wall, both holes
    # outer vertical walls
    for j in range(NY):
        for k in range(2):
            squares.append(sq_x(0, j, k))
            squares.append(sq_x(NX, j, k))
    for i in range(NX):
        for k in range(2):
            squares.append(sq_y(i, 0, k))
            squares.append(sq_y(i, NY, k))
    # tunnel walls
    ui, uj = UP_CELL
    for s in (sq_x(ui, uj, 1), sq_x(ui + 1, uj, 1), sq_y(ui, uj, 1), sq_y(ui, uj + 1, 1)):
        squares.append(s)
    li, lj = LOW_CELL
    for s in (sq_x(li, lj, 0), sq_x(li + 1, lj, 0), sq_y(li, lj, 0), sq_y(li, lj + 1, 0)):
        squares.append(s)
    # supporting membranes, joining each tunnel to the wall x = 0 inside its own room
    squares.append(sq_y(0, uj, 1))   # y = uj, x in [0,1], z in [1,2]
    squares.append(sq_y(0, lj, 0))   # y = lj, x in [0,1], z in [0,1]

    coords = sorted({p for s in squares for p in s})
    vid = {p: n for n, p in enumerate(coords)}
    facets = []
    for s in squares:
        a, b, c, d = (vid[p] for p in s)
        facets.append(tuple(sorted((a, b, c))))
        facets.append(tuple(sorted((a, c, d))))
    cx = Complex.from_facets(facets, name="bing_house")
    return cx, {"squares": squares, "coords": coords, "n_squares": len(squares)}


# =====================================================================================
# collapse engine
# =====================================================================================


class CollapseEngine:
    """Incremental free-face bookkeeping for elementary collapses.

    ``tau`` is a *free face* when it is a proper face of exactly one face of the
    complex.  In a simplicial complex that happens exactly when ``tau`` has a single
    immediate coface ``sigma`` and ``sigma`` is maximal, which is what is tracked.
    """

    __slots__ = ("present", "up", "buckets", "free_set", "protected", "maxdim")

    def __init__(self, faces: Iterable[Face], protected: Iterable[Face] = ()):
        self.present: Set[Face] = set(faces)
        self.protected: FrozenSet[Face] = frozenset(protected)
        self.up: Dict[Face, Set[Face]] = {f: set() for f in self.present}
        for f in self.present:
            for s in _subfacets(f):
                self.up[s].add(f)
        self.maxdim = max((len(f) for f in self.present), default=1) - 1
        self.buckets: Dict[int, List[Face]] = {d: [] for d in range(self.maxdim + 1)}
        self.free_set: Set[Face] = set()
        for f in self.present:
            self._refresh(f)

    # -- internals -------------------------------------------------------------------
    def _is_free(self, f: Face) -> bool:
        if f in self.protected:
            return False
        u = self.up.get(f)
        if u is None or len(u) != 1:
            return False
        for sigma in u:
            break
        if sigma in self.protected:
            return False
        return not self.up[sigma]

    def _refresh(self, f: Face) -> None:
        if self._is_free(f):
            if f not in self.free_set:
                self.free_set.add(f)
                self.buckets[len(f) - 1].append(f)
        else:
            self.free_set.discard(f)

    # -- public ----------------------------------------------------------------------
    def pick(self, rng: random.Random, strategy: str = "uniform") -> Optional[Face]:
        """Pop a free face, or ``None`` when the complex is stuck."""
        while True:
            sizes = [(d, len(b)) for d, b in self.buckets.items() if b]
            if not sizes:
                return None
            if strategy == "top":
                order = [max(d for d, _ in sizes)]
            elif strategy == "bottom":
                order = [min(d for d, _ in sizes)]
            elif strategy == "uniform":
                total = sum(n for _, n in sizes)
                r = rng.randrange(total)
                order = []
                for d, n in sizes:
                    if r < n:
                        order = [d]
                        break
                    r -= n
                if not order:
                    order = [sizes[-1][0]]
            else:
                raise ValueError(f"unknown strategy {strategy!r}")
            d = order[0]
            bucket = self.buckets[d]
            i = rng.randrange(len(bucket))
            f = bucket[i]
            bucket[i] = bucket[-1]
            bucket.pop()
            if f in self.free_set and self._is_free(f):
                self.free_set.discard(f)
                return f

    def collapse(self, tau: Face) -> Tuple[Face, Face]:
        """Perform the elementary collapse at the free face ``tau``."""
        for sigma in self.up[tau]:
            break
        for f in (sigma, tau):
            for s in _subfacets(f):
                if s in self.up:
                    self.up[s].discard(f)
            del self.up[f]
            self.present.discard(f)
            self.free_set.discard(f)
        dirty = {s for s in _subfacets(sigma) if s in self.present}
        dirty |= {s for s in _subfacets(tau) if s in self.present}
        recheck = set(dirty)
        for f in dirty:
            for s in _subfacets(f):
                if s in self.present:
                    recheck.add(s)
        for f in recheck:
            self._refresh(f)
        return (tau, sigma)


def run_collapse(
    faces: Iterable[Face],
    rng: random.Random,
    strategy: str = "uniform",
    protected: Iterable[Face] = (),
) -> Tuple[List[Tuple[Face, Face]], Set[Face]]:
    """Collapse greedily until stuck.  Returns ``(sequence, residual face set)``."""
    eng = CollapseEngine(faces, protected)
    seq: List[Tuple[Face, Face]] = []
    while True:
        tau = eng.pick(rng, strategy)
        if tau is None:
            break
        seq.append(eng.collapse(tau))
    return seq, eng.present


def _residual_ok(residual: Set[Face], target: str, protected: FrozenSet[Face]) -> bool:
    if target == "point":
        return len(residual) == 1 and len(next(iter(residual))) == 1
    if target == "subcomplex":
        return residual == set(protected)
    raise ValueError(f"unknown target {target!r}")


def search_collapse(
    cx: Complex,
    restarts: int = 200,
    seed: int = 0,
    strategies: Sequence[str] = ("uniform", "top", "bottom"),
    target: str = "point",
    protected: Iterable[Face] = (),
    time_budget: Optional[float] = None,
    verbose: bool = False,
) -> Dict[str, object]:
    """Restarted randomized free-face collapse search.

    A success is a genuine certificate; a failure is silence -- collapsibility is not
    a monotone property and this search is neither complete nor exhaustive.
    """
    protected = frozenset(protected)
    faces = cx.faces
    best = None
    best_left = len(faces) + 1
    t0 = time.time()
    used = 0
    for r in range(restarts):
        if time_budget is not None and time.time() - t0 > time_budget:
            break
        used = r + 1
        strategy = strategies[r % len(strategies)]
        rng = random.Random((seed * 1_000_003) ^ (r * 2_654_435_761))
        seq, residual = run_collapse(faces, rng, strategy, protected)
        if _residual_ok(residual, target, protected):
            return {
                "success": True,
                "sequence": seq,
                "restarts_used": used,
                "restart_index": r,
                "strategy": strategy,
                "seed": seed,
                "elapsed_s": time.time() - t0,
                "residual_f_vector": Complex(residual).f_vector(),
                "n_faces": len(faces),
                "n_steps": len(seq),
            }
        left = len(residual) - len(protected)
        if left < best_left:
            best_left = left
            best = (r, strategy, Complex(residual).f_vector())
            if verbose:
                print(f"  restart {r} [{strategy}] stuck with {left} faces left "
                      f"f={best[2]}", flush=True)
    return {
        "success": False,
        "restarts_used": used,
        "best_restart": None if best is None else best[0],
        "best_strategy": None if best is None else best[1],
        "best_residual_f_vector": None if best is None else best[2],
        "best_faces_left": None if best is None else best_left,
        "seed": seed,
        "elapsed_s": time.time() - t0,
        "n_faces": len(faces),
    }


# =====================================================================================
# INDEPENDENT replay verifier
# =====================================================================================


def verify_collapse_sequence(
    facets: Iterable[Iterable[int]],
    sequence: Sequence[Sequence[Sequence[int]]],
    target: str = "point",
    protected: Optional[Iterable[Iterable[int]]] = None,
) -> Dict[str, object]:
    """Replay a collapse sequence from scratch and check every step.

    Deliberately independent of :class:`CollapseEngine`: the complex is rebuilt from
    ``facets`` by downward closure and, at every step, the proper cofaces of the
    claimed free face are recomputed by brute-force scan of the surviving faces.  No
    incremental bookkeeping is shared with the search.

    Returns a report dict with ``ok`` True/False and, on failure, ``reason`` and the
    index of the offending step.
    """
    present: Set[Face] = closure(facets)
    n_start = len(present)
    prot: Set[Face] = set()
    if protected is not None:
        prot = {tuple(sorted(set(f))) for f in protected}
        missing = prot - present
        if missing:
            return {"ok": False, "reason": f"protected faces not in complex: {sorted(missing)[:3]}"}

    for step, pair in enumerate(sequence):
        if len(pair) != 2:
            return {"ok": False, "step": step, "reason": "step is not a pair"}
        tau = tuple(pair[0])
        sigma = tuple(pair[1])
        if tuple(sorted(set(tau))) != tau or tuple(sorted(set(sigma))) != sigma:
            return {"ok": False, "step": step, "reason": "faces must be sorted, repeat-free tuples"}
        if tau not in present:
            return {"ok": False, "step": step, "reason": f"free face {tau} not present"}
        if sigma not in present:
            return {"ok": False, "step": step, "reason": f"coface {sigma} not present"}
        if tau in prot or sigma in prot:
            return {"ok": False, "step": step, "reason": "step removes a protected face"}
        stau = set(tau)
        if not stau < set(sigma):
            return {"ok": False, "step": step, "reason": f"{tau} is not a proper face of {sigma}"}
        cofaces = [g for g in present if g != tau and stau.issubset(g)]
        if len(cofaces) != 1 or cofaces[0] != sigma:
            return {
                "ok": False,
                "step": step,
                "reason": (f"{tau} is not free: it has {len(cofaces)} proper cofaces "
                           f"{sorted(cofaces)[:4]}"),
            }
        present.discard(tau)
        present.discard(sigma)

    # the surviving set must still be a simplicial complex
    for f in present:
        for s in _subfacets(f):
            if s not in present:
                return {"ok": False, "reason": f"residual not closed: {s} missing under {f}"}

    residual = Complex(present)
    report = {
        "ok": True,
        "n_faces_start": n_start,
        "n_steps": len(sequence),
        "residual_f_vector": residual.f_vector(),
        "residual_euler": residual.euler_characteristic(),
    }
    if target == "point":
        report["ok"] = len(present) == 1 and len(next(iter(present))) == 1
        if not report["ok"]:
            report["reason"] = f"residual is not a single vertex: f={residual.f_vector()}"
        else:
            report["endpoint"] = sorted(present)[0]
    elif target == "subcomplex":
        report["ok"] = present == prot
        if not report["ok"]:
            report["reason"] = (f"residual != protected subcomplex "
                                f"(|residual|={len(present)}, |protected|={len(prot)})")
    elif target == "any":
        pass
    else:
        raise ValueError(f"unknown target {target!r}")
    return report


# =====================================================================================
# integer homology (Smith normal form)
# =====================================================================================


def _smith_normal_form(matrix: List[List[int]]) -> Tuple[int, List[int]]:
    """Rank and the list of elementary divisors > 1 of an integer matrix."""
    m = [row[:] for row in matrix]
    rows = len(m)
    cols = len(m[0]) if rows else 0
    divisors: List[int] = []
    t = 0
    while t < rows and t < cols:
        piv = None
        best = None
        for i in range(t, rows):
            for j in range(t, cols):
                v = abs(m[i][j])
                if v and (best is None or v < best):
                    best, piv = v, (i, j)
        if piv is None:
            break
        pi, pj = piv
        m[t], m[pi] = m[pi], m[t]
        if pj != t:
            for row in m:
                row[t], row[pj] = row[pj], row[t]
        again = True
        while again:
            again = False
            for i in range(t + 1, rows):
                if m[i][t]:
                    q = m[i][t] // m[t][t]
                    if q:
                        for j in range(t, cols):
                            m[i][j] -= q * m[t][j]
                    if m[i][t]:
                        m[t], m[i] = m[i], m[t]
                        again = True
            for j in range(t + 1, cols):
                if m[t][j]:
                    q = m[t][j] // m[t][t]
                    if q:
                        for i in range(t, rows):
                            m[i][j] -= q * m[i][t]
                    if m[t][j]:
                        for i in range(t, rows):
                            m[i][t], m[i][j] = m[i][j], m[i][t]
                        again = True
        # make the pivot divide the rest
        d = abs(m[t][t])
        bad = None
        for i in range(t + 1, rows):
            for j in range(t + 1, cols):
                if m[i][j] % d:
                    bad = i
                    break
            if bad is not None:
                break
        if bad is not None:
            for j in range(t, cols):
                m[t][j] += m[bad][j]
            continue
        divisors.append(d)
        t += 1
    rank = len(divisors)
    return rank, [d for d in divisors if d > 1]


def homology(cx: Complex, maxdim: Optional[int] = None) -> Dict[int, Dict[str, object]]:
    """Integer simplicial homology ``H_0 .. H_maxdim`` as betti numbers + torsion."""
    if maxdim is None:
        maxdim = cx.dim
    by_dim = {d: cx.faces_of_dim(d) for d in range(maxdim + 2)}
    index = {d: {f: i for i, f in enumerate(by_dim[d])} for d in by_dim}
    ranks: Dict[int, int] = {}
    tors: Dict[int, List[int]] = {}
    for d in range(1, maxdim + 2):
        rows = len(by_dim[d - 1])
        cols = len(by_dim[d])
        if rows == 0 or cols == 0:
            ranks[d] = 0
            tors[d] = []
            continue
        mat = [[0] * cols for _ in range(rows)]
        for f in by_dim[d]:
            j = index[d][f]
            for k in range(len(f)):
                s = f[:k] + f[k + 1:]
                mat[index[d - 1][s]][j] = (-1) ** k
        ranks[d], tors[d] = _smith_normal_form(mat)
    out: Dict[int, Dict[str, object]] = {}
    for d in range(maxdim + 1):
        n = len(by_dim[d])
        betti = n - ranks.get(d, 0) - ranks.get(d + 1, 0)
        out[d] = {"betti": betti, "torsion": tors.get(d + 1, [])}
    return out


# =====================================================================================
# pi_1 of a simplicial complex, for complexes not given as presentation complexes
# =====================================================================================


def pi1_presentation(cx: Complex) -> Tuple[List[Tuple[int, int]], List[List[Tuple[int, int]]]]:
    """Edge-path presentation of ``pi_1`` from a spanning tree of the 1-skeleton.

    Returns ``(generators, relators)``: generators are the non-tree edges (as sorted
    vertex pairs) and each relator is the boundary word of a triangle, written as a
    list of ``(generator_index, exponent)`` pairs with tree edges dropped.
    """
    verts = cx.vertices()
    edges = [tuple(f) for f in cx.faces_of_dim(1)]
    tris = [tuple(f) for f in cx.faces_of_dim(2)]
    adj: Dict[int, List[Tuple[int, int]]] = {v: [] for v in verts}
    for e in edges:
        adj[e[0]].append(e)
        adj[e[1]].append(e)
    tree: Set[Tuple[int, int]] = set()
    seen = {verts[0]}
    stack = [verts[0]]
    while stack:
        v = stack.pop()
        for e in adj[v]:
            w = e[0] if e[1] == v else e[1]
            if w not in seen:
                seen.add(w)
                tree.add(e)
                stack.append(w)
    gens = [e for e in edges if e not in tree]
    gidx = {e: i for i, e in enumerate(gens)}
    relators = []
    for (a, b, c) in tris:
        word: List[Tuple[int, int]] = []
        for (p, q, sign) in ((a, b, 1), (b, c, 1), (a, c, -1)):
            e = (p, q) if p < q else (q, p)
            if e in gidx:
                word.append((gidx[e], sign))
        relators.append(word)
    return gens, relators


def tietze_simplify(n_gens: int, relators: List[List[Tuple[int, int]]],
                    rounds: int = 200) -> Tuple[int, List[List[Tuple[int, int]]]]:
    """Eliminate generators that occur exactly once in some relator (Tietze)."""
    rel = [_freely_reduce(r) for r in relators]
    alive = set(range(n_gens))
    for _ in range(rounds):
        target = None
        for ri, r in enumerate(rel):
            counts: Dict[int, int] = {}
            for g, _s in r:
                counts[g] = counts.get(g, 0) + 1
            for g, c in counts.items():
                if c == 1:
                    target = (ri, g)
                    break
            if target:
                break
        if target is None:
            break
        ri, g = target
        r = rel[ri]
        pos = next(i for i, (gg, _s) in enumerate(r) if gg == g)
        sign = r[pos][1]
        rest = r[pos + 1:] + r[:pos]           # cyclic reading: g^sign * rest = 1
        # g^sign = rest^{-1}, hence g = rest^{-1} when sign = +1 and g = rest when -1
        sub = _invert(rest) if sign == 1 else rest
        new = []
        for rj, rr in enumerate(rel):
            if rj == ri:
                continue
            out: List[Tuple[int, int]] = []
            for (gg, ss) in rr:
                if gg == g:
                    out.extend(sub if ss == 1 else _invert(sub))
                else:
                    out.append((gg, ss))
            new.append(_freely_reduce(out))
        rel = [r for r in new if r]
        alive.discard(g)
    return len(alive), rel


def _invert(word: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    return [(g, -s) for (g, s) in reversed(word)]


def _freely_reduce(word: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for item in word:
        if out and out[-1][0] == item[0] and out[-1][1] == -item[1]:
            out.pop()
        else:
            out.append(item)
    return out


# =====================================================================================
# targets and CLI
# =====================================================================================

AK3_WORDS = ("xxxYYYY", "xyxYXY")
AK2_WORDS = ("xxYYY", "xyxYXY")
DUNCE_WORD = ("xxX",)
RP2_WORD = ("xx",)
TRIVIAL_WORD = ("x",)


def build_target(name: str, subdivision: int = 3) -> Tuple[Complex, Dict[str, object]]:
    """Build one of the named 2-complexes."""
    if name == "ak3":
        return presentation_complex(AK3_WORDS, ("x", "y"), subdivision, "AK(3)")
    if name == "ak2":
        return presentation_complex(AK2_WORDS, ("x", "y"), subdivision, "AK(2)")
    if name in ("dunce", "dunce_hat"):
        return presentation_complex(DUNCE_WORD, ("x",), subdivision, "dunce_hat")
    if name == "rp2":
        return presentation_complex(RP2_WORD, ("x",), subdivision, "RP^2")
    if name == "trivial":
        return presentation_complex(TRIVIAL_WORD, ("x",), subdivision, "<x|x>")
    if name == "bing":
        return bing_house()
    if name == "disc":
        return disc(6), {}
    if name == "ball3":
        return simplex_ball(3), {}
    if name == "s2":
        return sphere2(), {}
    raise ValueError(f"unknown target {name!r}")


def _jsonable(seq):
    return [[list(t), list(s)] for (t, s) in seq]


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Zeeman-route collapse search")
    ap.add_argument("--target", default="ak3")
    ap.add_argument("--words", nargs="*", default=None,
                    help="explicit relator words (overrides --target)")
    ap.add_argument("--generators", nargs="*", default=None)
    ap.add_argument("--subdivision", type=int, default=3)
    ap.add_argument("--layers", type=int, default=1,
                    help="number of I-layers in the prism triangulation of K x I")
    ap.add_argument("--mode", default="product",
                    choices=("base", "product", "onto-bottom"),
                    help="collapse K, collapse K x I to a point, or collapse K x I "
                         "onto K x {0}")
    ap.add_argument("--restarts", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--time-budget", type=float, default=None)
    ap.add_argument("--strategies", nargs="*",
                    default=["uniform", "top", "bottom"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    if args.words:
        cx, info = presentation_complex(args.words, args.generators, args.subdivision,
                                        "custom")
        label = "custom:" + ",".join(args.words)
    else:
        cx, info = build_target(args.target, args.subdivision)
        label = args.target

    print(f"[base] {label}  f={cx.f_vector()}  chi={cx.euler_characteristic()}  "
          f"faces={cx.n_faces()}  free_faces={len(cx.free_faces())}", flush=True)

    protected: Iterable[Face] = ()
    target = "point"
    if args.mode == "base":
        work = cx
    else:
        work, bottom = prism(cx, args.layers)
        print(f"[prism] layers={args.layers}  f={work.f_vector()}  "
              f"chi={work.euler_characteristic()}  faces={work.n_faces()}", flush=True)
        if args.mode == "onto-bottom":
            protected = bottom
            target = "subcomplex"

    t0 = time.time()
    res = search_collapse(work, restarts=args.restarts, seed=args.seed,
                          strategies=tuple(args.strategies), target=target,
                          protected=protected, time_budget=args.time_budget,
                          verbose=args.verbose)
    res["target"] = label
    res["mode"] = args.mode
    res["layers"] = args.layers
    res["subdivision"] = args.subdivision
    res["base_f_vector"] = cx.f_vector()
    res["work_f_vector"] = work.f_vector()
    res["wall_clock_s"] = time.time() - t0

    if res["success"]:
        print(f"[COLLAPSE FOUND] steps={res['n_steps']} restart={res['restart_index']} "
              f"strategy={res['strategy']} elapsed={res['elapsed_s']:.1f}s", flush=True)
        rep = verify_collapse_sequence(
            sorted(work.faces), res["sequence"], target=target,
            protected=protected if target == "subcomplex" else None)
        res["replay"] = rep
        print(f"[replay] {rep}", flush=True)
        if args.out:
            payload = dict(res)
            payload["sequence"] = _jsonable(res["sequence"])
            if target == "subcomplex":
                payload["protected"] = [list(f) for f in sorted(protected)]
            payload["facets"] = [list(f) for f in sorted(work.faces)]
            with open(args.out, "w") as fh:
                json.dump(payload, fh)
            print(f"[out] wrote {args.out}", flush=True)
    else:
        print(f"[no collapse] restarts={res['restarts_used']} "
              f"best_left={res['best_faces_left']} "
              f"best_f={res['best_residual_f_vector']} "
              f"elapsed={res['elapsed_s']:.1f}s", flush=True)
        if args.out:
            with open(args.out, "w") as fh:
                json.dump(res, fh)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
