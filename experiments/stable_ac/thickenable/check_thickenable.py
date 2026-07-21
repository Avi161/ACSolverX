"""Neuwirth thickenability checker -- PROTOTYPE (track T7).  [unverified]

===============================================================================
DO NOT TRUST THE VERDICTS.  This is Pipeline A of the plan in
``NEUWIRTH_FEASIBILITY.md`` only -- the pure-python thickenability *certificate
filter*.  Its verdicts are NOT to be believed until each accepted case is
independently confirmed by the mandatory validator (Regina ``isBall`` on a
separately-constructed thickening N(K)), which is Pipeline B and is NOT built
here.  The single load-bearing correctness risk is the rotation-consistency
rule below: a wrong sign silently manufactures a FALSE POSITIVE, and a false
positive here does not fail loudly -- it prints a "proof" that an open problem
(AK(3), the 124 aca targets) is Andrews-Curtis-trivial.  Because of that, any
THICKENABLE verdict on an open-problem presentation is reported as a SUSPECTED
BUG, never as a result claim (see ``verdict``).  A NEGATIVE verdict settles
nothing either way (the payoff is one-sided: Lackenby Thm 1.3 fires only on a
*positive*), so a "NOT_THICKENABLE" is informative-but-inconclusive.
===============================================================================

What it decides (target problem)
--------------------------------
Given a balanced 2-generator presentation ``P = <x, y | r1, r2>`` of (usually)
the trivial group, is its presentation 2-complex ``K`` -- one 0-cell v, one
loop 1-cell per generator, one 2-cell per relator glued along the relator word
-- *thickenable*, i.e. does ``K`` embed in some orientable 3-manifold?  For a
trivial-group presentation a "yes" makes N(K) a contractible compact 3-manifold
= a 3-ball (Perelman), and by Lackenby Thm 1.3 the presentation is then
AC-trivial.  See ``NEUWIRTH_FEASIBILITY.md`` (a)-(f).

The criterion implemented (rotation system on the link graph)
-------------------------------------------------------------
Following Carmesin II (arXiv:1709.04643, Thm 1.1) and Lackenby 2606.06122 as
reconstructed in the memo: ``K`` embeds in a 3-manifold iff the *link of the
vertex v* can be realised as (a subgraph of) the 2-sphere S^2 that is the link
of a point in a 3-manifold, compatibly along the edges.  Concretely we build
the **link graph L** (= Whitehead graph of {r1, r2}) and search for an
edge-consistent genus-0 (planar) **rotation system** on it.

Link graph L (derived from first principles; this is THE convention)
--------------------------------------------------------------------
Vertices of L = the *germs* (directed edge-ends) at v.  For each generator g
there are two germs: ``+g`` = the direction you head off in when you start
reading the letter g (the tail of the oriented loop g), and ``-g`` = the
direction for reading G = g^{-1} (the head of loop g).  So for 2 generators L
has exactly four vertices {+x, -x, +y, -y}; n generators give 2n vertices.

Reading a letter ``a`` at v you DEPART along germ ``a`` and ARRIVE along germ
``-a`` (to retrace your step you would leave along a^{-1}, so the point where
you land is the germ of a^{-1}).  Edges of L = the *corners* of the discs: read
each relator cyclically; every consecutive letter pair ``(a_i, a_{i+1})`` is
one corner of that disc at v, and on the link sphere it is an arc joining the
germ where a_i arrives to the germ where a_{i+1} departs, i.e. an edge

        corner(a_i, a_{i+1})  =  edge{ germ(-a_i) , germ(a_{i+1}) } .

There are exactly |r1|+|r2| corners.  (Cross-check with the memo's wording:
this joins "a_i-head-side" (= germ -a_i, the head end of loop |a_i|) to
"a_{i+1}-tail-side" (= germ +a_{i+1}, the tail end of loop |a_{i+1}|).)  This L
is the Whitehead graph of {r1, r2}.  A worked tiny example (the commutator
r = xyXY, giving the 4-cycle +x -- -y -- -x -- +y -- +x) is pinned in the
tests.

Cyclic reduction removes any corner ``{-a_i, a_{i+1}}`` with a_{i+1} = -a_i
(consecutive inverse letters), which would be a self-loop; so after cyclic
reduction L has no self-loops (only parallel edges).

Rotation system, the reversal COUPLING, and genus (the load-bearing part)
-------------------------------------------------------------------------
A rotation system is a cyclic order of the incident corner-darts at each germ
vertex -- a combinatorial embedding (ribbon/fat-graph structure) of L into an
oriented surface.  Tracing the resulting boundary walks gives a closed oriented
surface of Euler characteristic chi = V - E + F (F = number of walks); the
system is *genus 0 / planar* iff chi = 2*(#components of L).

The rotations at the two germ ends of a single generator are NOT independent.
Loop g is a solid tube; its strands (one per occurrence of g or G in the
relators) run the length of the tube, so the cyclic (angular) order of strands
seen at the +g end equals the *reverse* of the order seen at the -g end (the
two boundary circles of an oriented cylinder carry opposite induced
orientations).  Each occurrence of the generator gives one strand pairing a
dart at +g with a dart at -g (its DEPART dart, on the corner before it, at germ
= its own letter; and its ARRIVE dart, on the corner after it, at germ = the
inverse letter).  deg(+g) = deg(-g) = (#g)+(#G) always, so the pairing is a
bijection.  The coupling forces:

    rotation at -g  =  reverse( pairing-image of rotation at +g ).

  >>> [unverified -- reconstructed]  The *reversal* direction of this coupling
  >>> is the single riskiest convention in the whole module.  It is what makes
  >>> the checker discriminating (without it every 4-vertex link is trivially
  >>> planar, so every 2-generator presentation would read THICKENABLE, which
  >>> would be a catastrophic all-false-positive).  It is topologically
  >>> justified (opposite boundary orientations of a tube) but has NOT been
  >>> validated against Regina.  Treat every THICKENABLE as suspect until it is.

Search: only the positive germs +g are free (each (deg-1)! cyclic orders); the
negative germs are then forced.  For 2 generators that is a product of two
factorials -- 86,400 for AK(3) (deg 6 and 7) -- brute-forceable.  For larger
total length the product blows up; above ``max_rotations`` the search returns
the honest third verdict UNKNOWN (a size limit), NEVER a false NOT_THICKENABLE.

Size limit
----------
Tractable (sub-second) whenever prod_g (deg(g)-1)! <= max_rotations (default
2,000,000).  AK(3) at total length 13 fits comfortably; several length-25 floor
reps do not and come back UNKNOWN.  This is a prototype limit, not a theorem.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# word encoding: x=1 X=-1  y=2 Y=-2  z=3 Z=-3   (matches data/ layout)
# ---------------------------------------------------------------------------
_POS = {"x": 1, "y": 2, "z": 3}
_INT_TO_CH = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}


def parse_word(s: str) -> list[int]:
    """'YXXyxYx' -> [-2,-1,-1,2,1,-2,1].  Lowercase = generator, upper = inverse."""
    out: list[int] = []
    for ch in s.strip():
        if ch in " ,":
            continue
        low = ch.lower()
        if low not in _POS:
            raise ValueError(f"unknown letter {ch!r} in word {s!r}")
        out.append(_POS[low] if ch.islower() else -_POS[low])
    return out


def word_to_str(w: list[int]) -> str:
    return "".join(_INT_TO_CH[c] for c in w)


def free_reduce(w: list[int]) -> list[int]:
    """Cancel adjacent inverse pairs (stack based; safe on empty word)."""
    st: list[int] = []
    for c in w:
        if st and st[-1] == -c:
            st.pop()
        else:
            st.append(c)
    return st


def cyclic_reduce(w: list[int]) -> list[int]:
    """Freely reduce, then remove cyclically-inverse ends (no self-loops left)."""
    w = free_reduce(w)
    i, j = 0, len(w) - 1
    while i < j and w[i] == -w[j]:
        i += 1
        j -= 1
    return w[i : j + 1]


# ---------------------------------------------------------------------------
# pre-collapse: Lackenby Lemma 3.1.  Relators of length 1 or 2 are degenerate
# for the raw rotation checker (they make ill-posed corners); each lets us
# eliminate a generator by a handle cancellation, exactly as Lemma 3.1 does.
# We collapse until every remaining relator has length >= 3, or the whole
# presentation collapses (=> trivial group => thickenable, N(K)=B^3).
# ---------------------------------------------------------------------------
@dataclass
class Presentation:
    relators: list[list[int]]  # each a list[int], cyclically reduced
    n_gen: int = 2
    name: str = ""

    @classmethod
    def from_strings(cls, r1: str, r2: str | None = None, name: str = "",
                     n_gen: int = 2) -> "Presentation":
        rels = [parse_word(r1)]
        if r2 is not None:
            rels.append(parse_word(r2))
        return cls([cyclic_reduce(r) for r in rels], n_gen=n_gen, name=name)


def _subst_generator(relators: list[list[int]], g: int, repl: list[int]) -> list[list[int]]:
    """Replace generator |g|: every +|g| -> repl, every -|g| -> repl^{-1}."""
    tg = abs(g)
    inv = [-c for c in reversed(repl)]
    out = []
    for r in relators:
        nr: list[int] = []
        for c in r:
            if abs(c) == tg:
                nr.extend(repl if c > 0 else inv)
            else:
                nr.append(c)
        out.append(cyclic_reduce(nr))
    return out


def precollapse(pres: Presentation) -> tuple[Presentation, str, str]:
    """Apply Lemma-3.1 handle cancellations for length-1/2 relators.

    Returns (new_pres, note, outcome).  ``outcome`` is one of:
      * "trivial"     -- balance held and every generator+relator cancelled
                         (n_gen eliminations of a starting n_gen-balanced
                         presentation) -> trivial group, K collapses to a point,
                         thickenable with N(K)=B^3 (Lemma 3.1 / memo hand-check).
      * "reduced"     -- collapse done; some relators of length >= 3 remain, hand
                         them to the rotation checker.
      * "degenerate"  -- a relator vanished to the empty word by REDUNDANCY (not
                         the clean final cancellation), so the presentation has a
                         free factor / is not the balanced trivial-group object
                         the checker is for (Lackenby: an empty relation forces an
                         infinite group).  Out of scope -> undecided.
    """
    relators = [cyclic_reduce(r) for r in pres.relators]
    # balance is judged against the generators actually appearing, not a
    # caller-supplied n_gen (undeclared/unused generators are out of scope).
    orig_ngen = len({abs(c) for r in relators for c in r})
    notes: list[str] = []
    elims = 0
    degenerate = False
    changed = True
    while changed:
        changed = False
        n_before = len(relators)
        relators = [r for r in relators if len(r) > 0]  # drop empty relators
        if len(relators) < n_before and (n_before - len(relators)) > 0 and elims > 0:
            # a relator became empty via substitution before the final collapse
            # step -> redundancy (only benign at the very end, handled below)
            pass
        # length-1 relator g^{+-1}: sets g = 1, delete generator.
        for idx, r in enumerate(relators):
            if len(r) == 1:
                g = r[0]
                rest = relators[:idx] + relators[idx + 1 :]
                before = len(rest)
                relators = [x for x in _subst_generator(rest, g, []) if len(x) > 0]
                if len(relators) < before:
                    degenerate = True   # some other relator vanished => redundant
                notes.append(f"len1 relator {word_to_str(r)} -> kill gen {_INT_TO_CH[abs(g)]}")
                elims += 1
                changed = True
                break
        if changed:
            continue
        # length-2 relator g^{a} h^{b}, g != h: sets g = h^{-b*a}, delete generator g.
        for idx, r in enumerate(relators):
            if len(r) == 2 and abs(r[0]) != abs(r[1]):
                g, h = r[0], r[1]
                repl = [-h] if g > 0 else [h]   # g == (h^{b})^{-1} rearranged
                rest = relators[:idx] + relators[idx + 1 :]
                before = len(rest)
                relators = [x for x in _subst_generator(rest, g, repl) if len(x) > 0]
                if len(relators) < before:
                    degenerate = True
                notes.append(
                    f"len2 relator {word_to_str(r)} -> gen {_INT_TO_CH[abs(g)]}="
                    f"{word_to_str(repl)}"
                )
                elims += 1
                changed = True
                break
    relators = [r for r in relators if len(r) > 0]
    note = "; ".join(notes) if notes else "no pre-collapse needed"
    if degenerate:
        outcome = "degenerate"
    elif len(relators) == 0 and elims == orig_ngen:
        outcome = "trivial"
    elif len(relators) == 0:
        outcome = "degenerate"   # relators gone but balance broke -> free factor
    else:
        outcome = "reduced"
    # renumber generators to a contiguous block for the link graph
    present = sorted({abs(c) for r in relators for c in r})
    remap = {g: i + 1 for i, g in enumerate(present)}
    relators = [[(1 if c > 0 else -1) * remap[abs(c)] for c in r] for r in relators]
    new = Presentation(relators, n_gen=len(present), name=pres.name)
    return new, note, outcome


# ---------------------------------------------------------------------------
# link graph  +  rotation-system genus search
# ---------------------------------------------------------------------------
@dataclass
class LinkGraph:
    """Whitehead graph of the relators, as a combinatorial-map skeleton.

    darts: 0..2E-1.  Each corner k contributes two darts (2k = arrive-side at
    germ -a_i, 2k+1 = depart-side at germ a_{i+1}).  alpha swaps the two darts
    of a corner.  ``dart_vertex[d]`` = germ (signed int).  ``vert_darts[v]`` =
    darts at germ v.  ``pairing[d]`` = the strand partner (other tube-end of
    the same letter occurrence) used by the reversal coupling.
    """
    n_corners: int
    dart_vertex: list[int]
    vert_darts: dict[int, list[int]]
    pairing: dict[int, int]
    vertices: list[int] = field(default_factory=list)


def build_link_graph(pres: Presentation) -> LinkGraph:
    relators = [cyclic_reduce(r) for r in pres.relators if len(r) > 0]
    # global occurrence table so strands (letter occurrences) get stable ids
    # occ id -> (relator idx, position)
    occ_of: list[tuple[int, int]] = []
    occ_id: list[list[int]] = []
    for ri, r in enumerate(relators):
        ids = []
        for pos in range(len(r)):
            ids.append(len(occ_of))
            occ_of.append((ri, pos))
        occ_id.append(ids)

    dart_vertex: list[int] = []
    vert_darts: dict[int, list[int]] = {}
    # per occurrence, remember its two darts (depart dart, arrive dart)
    occ_depart: dict[int, int] = {}
    occ_arrive: dict[int, int] = {}

    def add_dart(vertex: int) -> int:
        d = len(dart_vertex)
        dart_vertex.append(vertex)
        vert_darts.setdefault(vertex, []).append(d)
        return d

    corner = 0
    for ri, r in enumerate(relators):
        m = len(r)
        for pos in range(m):
            a = r[pos]
            b = r[(pos + 1) % m]
            i_occ = occ_id[ri][pos]
            j_occ = occ_id[ri][(pos + 1) % m]
            # corner(a,b) = edge{ -a , b }; darts numbered 2*corner, 2*corner+1
            dA = add_dart(-a)   # arrive-side of occurrence i_occ (tube |a|)
            dB = add_dart(b)    # depart-side of occurrence j_occ (tube |b|)
            occ_arrive[i_occ] = dA
            occ_depart[j_occ] = dB
            corner += 1

    # strand pairing: each occurrence pairs its depart dart with its arrive dart
    pairing: dict[int, int] = {}
    for occ in range(len(occ_of)):
        dd, da = occ_depart[occ], occ_arrive[occ]
        pairing[dd] = da
        pairing[da] = dd

    verts = sorted(vert_darts.keys(), key=lambda v: (abs(v), v < 0))
    return LinkGraph(corner, dart_vertex, vert_darts, pairing, verts)


def _alpha(d: int) -> int:
    """Involution swapping the two darts of a corner (2k <-> 2k+1)."""
    return d ^ 1


def _components(lg: LinkGraph) -> int:
    """Connected components of L (germ vertices joined by corners)."""
    parent = {v: v for v in lg.vertices}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for k in range(lg.n_corners):
        u, v = lg.dart_vertex[2 * k], lg.dart_vertex[2 * k + 1]
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    return len({find(v) for v in lg.vertices})


def _genus_of_rotation(lg: LinkGraph, rot: dict[int, list[int]], ncomp: int) -> int | None:
    """Euler genus of the surface for this rotation.  None if orientation-
    inconsistent (should not happen for our oriented construction).

    Faces = orbits of phi = sigma . alpha, where sigma sends a dart to the next
    dart (cyclically) at its own vertex.
    """
    succ: dict[int, int] = {}
    for v, order in rot.items():
        k = len(order)
        for i in range(k):
            succ[order[i]] = order[(i + 1) % k]
    n_darts = len(lg.dart_vertex)
    seen = [False] * n_darts
    faces = 0
    for start in range(n_darts):
        if seen[start]:
            continue
        faces += 1
        d = start
        while not seen[d]:
            seen[d] = True
            d = succ[_alpha(d)]   # phi = sigma . alpha
    V = len(lg.vertices)
    E = lg.n_corners
    F = faces
    chi = V - E + F
    # genus counted against the number of spherical components (planar => 0)
    return (2 * ncomp - chi) // 2


def _rotation_cost(lg: LinkGraph) -> float:
    """Product over free (positive) germs of (deg-1)! -- the search size."""
    cost = 1.0
    for v in lg.vertices:
        if v > 0:
            cost *= math.factorial(max(len(lg.vert_darts[v]) - 1, 0))
    return cost


def _coupled_negative_order(lg: LinkGraph, pos_v: int, pos_order: list[int]) -> list[int]:
    """Forced cyclic order at germ -pos_v = reverse of pairing-image of the
    positive order.  (The tube reversal convention -- the [unverified] rule.)"""
    imaged = [lg.pairing[d] for d in pos_order]
    # reverse: keep first fixed, reverse the rest (cyclic-order reversal)
    return [imaged[0]] + imaged[1:][::-1] if imaged else []


@dataclass
class Verdict:
    presentation: str
    status: str          # THICKENABLE | NOT_THICKENABLE | UNKNOWN_SIZE | TRIVIAL_COLLAPSE
    thickenable: bool | None
    reason: str
    precollapse_note: str
    n_gen: int
    total_length: int
    link_degrees: dict[str, int]
    rotation_cost: float
    open_problem: bool = False
    warnings: list[str] = field(default_factory=list)

    def one_line(self) -> str:
        tag = self.status
        if self.thickenable and self.open_problem:
            tag += "  << SUSPECTED BUG"
        return f"{self.presentation:<24} {tag:<28} {self.reason}"


# canonical open-problem presentations that a THICKENABLE would (falsely?) settle
def _canon_key(pres: Presentation) -> frozenset:
    """Cheap identity: multiset of (cyclically reduced) relator strings up to
    rotation/inversion.  Only used to flag open-problem inputs for the guard."""
    keys = set()
    for r in pres.relators:
        r = cyclic_reduce(r)
        variants = []
        for w in (r, [-c for c in reversed(r)]):
            for i in range(len(w) or 1):
                variants.append(tuple(w[i:] + w[:i]))
        keys.add(min(variants) if variants else tuple())
    return frozenset(keys)


_OPEN_KEYS: set[frozenset] = set()


def _register_open(*strings: str) -> None:
    for s in strings:
        r1, r2 = s.split("|")
        _OPEN_KEYS.add(_canon_key(Presentation.from_strings(r1, r2)))


# AK(3) and its orbit-2 rep are the marquee open cases.
_register_open("xxxYYYY|xyxYXY", "YYXXyx|YYYxyXX")


def is_open_problem(pres: Presentation) -> bool:
    return _canon_key(pres) in _OPEN_KEYS


def check(pres: Presentation, max_rotations: int = 2_000_000,
          mark_open: bool | None = None) -> Verdict:
    """Decide thickenability of ``pres``.  See module docstring; [unverified]."""
    name = pres.name or (
        "|".join(word_to_str(cyclic_reduce(r)) for r in pres.relators)
    )
    open_flag = is_open_problem(pres) if mark_open is None else mark_open
    total_len = sum(len(cyclic_reduce(r)) for r in pres.relators)

    collapsed, note, outcome = precollapse(pres)
    if outcome == "trivial":
        return Verdict(
            presentation=name, status="TRIVIAL_COLLAPSE", thickenable=True,
            reason="pre-collapse eliminated all generators+relators => trivial "
                   "group, K collapses to a point, N(K)=B^3 (Lemma 3.1)",
            precollapse_note=note, n_gen=0, total_length=total_len,
            link_degrees={}, rotation_cost=1.0, open_problem=open_flag,
            warnings=(["THICKENABLE on an open-problem presentation -- "
                       "SUSPECTED BUG, do NOT claim a result"] if open_flag else []),
        )
    if outcome == "degenerate":
        return Verdict(
            presentation=name, status="DEGENERATE", thickenable=None,
            reason="pre-collapse hit an empty (redundant) relator / broken "
                   "balance => a free factor, not the balanced trivial-group "
                   "object this checker decides (out of scope)",
            precollapse_note=note, n_gen=collapsed.n_gen, total_length=total_len,
            link_degrees={}, rotation_cost=1.0, open_problem=open_flag,
        )

    lg = build_link_graph(collapsed)
    degs = {_INT_TO_CH[v]: len(lg.vert_darts[v]) for v in lg.vertices}
    cost = _rotation_cost(lg)
    ncomp = _components(lg)

    if cost > max_rotations:
        return Verdict(
            presentation=name, status="UNKNOWN_SIZE", thickenable=None,
            reason=f"rotation search space {cost:.3g} > max_rotations "
                   f"{max_rotations:g}; prototype size limit (NOT a NO)",
            precollapse_note=note, n_gen=collapsed.n_gen, total_length=total_len,
            link_degrees=degs, rotation_cost=cost, open_problem=open_flag,
        )

    pos_verts = [v for v in lg.vertices if v > 0]
    # enumerate cyclic orders at each positive germ (fix first dart, permute rest)
    per_vertex_orders: list[list[list[int]]] = []
    for v in pos_verts:
        darts = lg.vert_darts[v]
        if len(darts) <= 1:
            per_vertex_orders.append([list(darts)])
        else:
            head = darts[0]
            tail = darts[1:]
            per_vertex_orders.append([[head, *p] for p in itertools.permutations(tail)])

    found = None
    for combo in itertools.product(*per_vertex_orders):
        rot: dict[int, list[int]] = {}
        for v, order in zip(pos_verts, combo):
            rot[v] = list(order)
            neg = -v
            if neg in lg.vert_darts:
                rot[neg] = _coupled_negative_order(lg, v, list(order))
        # any germ with no positive partner (should not occur) gets identity
        for v in lg.vertices:
            rot.setdefault(v, list(lg.vert_darts[v]))
        g = _genus_of_rotation(lg, rot, ncomp)
        if g == 0:
            found = rot
            break

    if found is not None:
        warns = []
        if open_flag:
            warns.append(
                "THICKENABLE on an OPEN-PROBLEM presentation. A genuine positive "
                "would settle it via Lackenby Thm 1.3 -- extraordinary. This is a "
                "SUSPECTED BUG in the [unverified] rotation-consistency rule until "
                "Regina isBall independently confirms N(K)=B^3. DO NOT claim a result."
            )
        return Verdict(
            presentation=name, status="THICKENABLE", thickenable=True,
            reason="found an edge-consistent genus-0 rotation system [unverified]",
            precollapse_note=note, n_gen=collapsed.n_gen, total_length=total_len,
            link_degrees=degs, rotation_cost=cost, open_problem=open_flag,
            warnings=warns,
        )
    return Verdict(
        presentation=name, status="NOT_THICKENABLE", thickenable=False,
        reason="no edge-consistent genus-0 rotation exists over the full search "
               "[unverified]; a negative settles nothing (one-sided payoff)",
        precollapse_note=note, n_gen=collapsed.n_gen, total_length=total_len,
        link_degrees=degs, rotation_cost=cost, open_problem=open_flag,
    )


def check_strings(r1: str, r2: str | None = None, name: str = "", **kw) -> Verdict:
    return check(Presentation.from_strings(r1, r2, name=name), **kw)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and "|" in sys.argv[1]:
        r1, r2 = sys.argv[1].split("|")
        v = check_strings(r1, r2 if r2 else None)
        print(v.one_line())
        for w in v.warnings:
            print("  !!", w)
    else:
        print("usage: python -m ...check_thickenable 'r1|r2'")
