"""W6: rank-three Neuwirth link graphs, exact genus, and the AC-ball census.

Rank-general reimplementation of the occurrence link graph of
`literature/proofs/AK3_NEUWIRTH.md` (the A/B/C dictionary), independent of
`experiments/stable_ac/thickenable/*`, plus:

  * an exact planarity oracle for <= 6 germ vertices (Wagner: no K5 and no
    K3,3 minor), cross-validated against brute-force rotation systems;
  * the exact Neuwirth genus potential gamma_N (Lemma 1 of AK3_NEUWIRTH.md)
    by complete enumeration of compatible orderings, when the factorial
    budget allows;
  * the three W5 bridge targets, classified;
  * a bounded rank-three AC-ball census under the 1,000-pop repo law.

DOCTRINE.  A planarity verdict is NOT a thickenability verdict.  Only
gamma_N > 0 is a certified negative (necessity direction of Theorem 2 of
AK3_NEUWIRTH.md, which does not use connectivity).  gamma_N == 0 is a
POSITIVE and is quarantined: Pipeline B (Regina) does not exist in this
repo, and for a disconnected link the sufficiency direction needs the
component lemma stated in W6_RANK3_FEASIBILITY.md, which is not certified
here.  No AK(3), AC, or stable-AC claim is made anywhere in this file.

Run (all modes are well under the guard's 60 s slice):

    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
        python3 fable/proofs/checkers/rank3_link_graph.py controls
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
        python3 fable/proofs/checkers/rank3_link_graph.py targets
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
        python3 fable/proofs/checkers/rank3_link_graph.py ball --ceiling 16
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
REPO = HERE.parents[2]

# ---------------------------------------------------------------------------
# words
# ---------------------------------------------------------------------------

FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> bool:
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)
    return bool(cond)


def inv(w: str) -> str:
    return "".join(c.swapcase() for c in reversed(w))


def free_reduce(w: str) -> str:
    out: list[str] = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyclic_reduce(w: str) -> str:
    w = free_reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = w[1:-1]
        w = free_reduce(w)
    return w


def canon_word(w: str) -> str:
    """Cyclic-rotation- and inversion-minimal spelling of a cyclic word.

    Cyclic rotation of a relator is AC3 conjugation by a prefix and inversion
    is AC1; neither changes the presentation 2-complex up to homeomorphism,
    so this is exactly the quotient the link graph already sees.
    """
    w = cyclic_reduce(w)
    if not w:
        return ""
    cands = []
    for u in (w, inv(w)):
        for k in range(len(u)):
            cands.append(u[k:] + u[:k])
    return min(cands)


def canon_state(rels: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(canon_word(r) for r in rels))


# ---------------------------------------------------------------------------
# the occurrence link graph (AK3_NEUWIRTH.md dictionary, rank-general)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Link:
    words: tuple[str, ...]
    gens: str
    A: tuple[int, ...]          # corner involution on darts
    B: tuple[int, ...]          # tube involution on darts
    germ: tuple[int, ...]       # dart -> germ vertex (2k = g+, 2k+1 = g-)
    pos_darts: tuple[tuple[int, ...], ...]   # per generator, darts at g+
    edges: tuple[tuple[int, int], ...]       # A-pairs as germ-vertex pairs
    n_germs: int


def letter_germs(letter: str, gens: str) -> tuple[int, int]:
    g = letter.lower()
    if g not in gens:
        raise ValueError(f"letter {letter!r} outside generators {gens!r}")
    k = gens.index(g)
    return (2 * k, 2 * k + 1) if letter.islower() else (2 * k + 1, 2 * k)


def build_link(words: tuple[str, ...], gens: str) -> Link:
    words = tuple(words)
    if not words or any(not w for w in words):
        raise ValueError("every relator must be a nonempty exact word")
    total = sum(map(len, words))
    n = 2 * total
    A = [-1] * n
    B = [-1] * n
    germ = [-1] * n
    off = 0
    for w in words:
        occ = tuple(range(off, off + len(w)))
        for i, o in enumerate(occ):
            d, h = 2 * o, 2 * o + 1
            gd, gh = letter_germs(w[i], gens)
            germ[d], germ[h] = gd, gh
            B[d], B[h] = h, d
            nxt = 2 * occ[(i + 1) % len(w)]
            A[h], A[nxt] = nxt, h
        off += len(w)
    if min(A) < 0 or min(B) < 0 or min(germ) < 0:
        raise AssertionError("incomplete dart dictionary")
    pos = tuple(
        tuple(d for d in range(n) if germ[d] == 2 * k) for k in range(len(gens))
    )
    edges = tuple(
        tuple(sorted((germ[d], germ[A[d]]))) for d in range(n) if d < A[d]
    )
    return Link(
        words=words,
        gens=gens,
        A=tuple(A),
        B=tuple(B),
        germ=tuple(germ),
        pos_darts=pos,
        edges=edges,  # type: ignore[arg-type]
        n_germs=2 * len(gens),
    )


def simple_support(link: Link) -> tuple[frozenset[tuple[int, int]], frozenset[int]]:
    """(simple edges u<v, germ vertices carrying a loop)."""
    simple = {e for e in link.edges if e[0] != e[1]}
    loops = {e[0] for e in link.edges if e[0] == e[1]}
    return frozenset(simple), frozenset(loops)


def active_germs(link: Link) -> frozenset[int]:
    return frozenset(link.germ)


def components(link: Link) -> tuple[frozenset[int], ...]:
    """Connected components of the link graph, on germ vertices that occur."""
    verts = sorted(active_germs(link))
    parent = {v: v for v in verts}

    def find(v: int) -> int:
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for u, v in link.edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    groups: dict[int, set[int]] = {}
    for v in verts:
        groups.setdefault(find(v), set()).add(v)
    return tuple(sorted((frozenset(s) for s in groups.values()), key=sorted))


# ---------------------------------------------------------------------------
# exact planarity for <= 6 vertices (Wagner: no K5 minor, no K3,3 minor)
# ---------------------------------------------------------------------------


def _connected_block(block: list[int], adj: dict[int, set[int]]) -> bool:
    if not block:
        return False
    inside = set(block)
    seen = {block[0]}
    stack = [block[0]]
    while stack:
        v = stack.pop()
        for u in adj[v] & inside:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return seen == inside


def _has_minor(
    verts: list[int],
    edges: frozenset[tuple[int, int]],
    k: int,
    required: list[tuple[int, int]],
) -> bool:
    """Brute-force minor test: k disjoint connected branch sets, all `required`
    pairs joined by at least one edge.  Exact for the tiny vertex counts here."""
    if len(verts) < k:
        return False
    adj: dict[int, set[int]] = {v: set() for v in verts}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for assign in itertools.product(range(k + 1), repeat=len(verts)):
        blocks: list[list[int]] = [[] for _ in range(k)]
        for v, a in zip(verts, assign):
            if a < k:
                blocks[a].append(v)
        if any(not _connected_block(b, adj) for b in blocks):
            continue
        ok = True
        for a, b in required:
            if not any(
                (min(u, v), max(u, v)) in edges
                for u in blocks[a]
                for v in blocks[b]
            ):
                ok = False
                break
        if ok:
            return True
    return False


K5_PAIRS = [(a, b) for a in range(5) for b in range(a + 1, 5)]
K33_PAIRS = [(a, b + 3) for a in range(3) for b in range(3)]


_PLANAR_CACHE: dict[tuple[int, frozenset[tuple[int, int]]], tuple[bool, str]] = {}


def is_planar(verts: list[int], edges: frozenset[tuple[int, int]]) -> tuple[bool, str]:
    """Exact planarity of a simple graph.  Only for <= 6 vertices."""
    if len(verts) > 6:
        raise ValueError("planarity oracle is only exact for <= 6 vertices")
    if len(verts) <= 4:
        return True, "at most four vertices"
    if len(edges) < 9:
        # Every non-planar simple graph has at least 9 edges (K3,3 is the
        # unique 9-edge minimal one; K5 has 10).  Exact, not a heuristic.
        return True, "fewer than nine simple edges"
    key = (len(verts), edges)
    if key in _PLANAR_CACHE:
        return _PLANAR_CACHE[key]
    got = _is_planar_slow(verts, edges)
    _PLANAR_CACHE[key] = got
    return got


def _is_planar_slow(
    verts: list[int], edges: frozenset[tuple[int, int]]
) -> tuple[bool, str]:
    if _has_minor(verts, edges, 5, K5_PAIRS):
        return False, "K5 minor"
    if _has_minor(verts, edges, 6, K33_PAIRS):
        return False, "K3,3 minor"
    return True, "no K5 and no K3,3 minor (Wagner)"


def rotation_genus0_exists(
    verts: list[int], edges: frozenset[tuple[int, int]], budget: int = 400_000
) -> bool | None:
    """Independent planarity oracle: brute force over rotation systems.

    A connected simple graph is planar iff some rotation system traces
    V - E + F = 2.  Returns None if the enumeration exceeds `budget`.
    """
    adj: dict[int, list[int]] = {v: [] for v in verts}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for v in verts:
        adj[v].sort()
    cases = 1
    for v in verts:
        cases *= max(1, math.factorial(max(0, len(adj[v]) - 1)))
    if cases > budget:
        return None
    choices = []
    for v in verts:
        nb = adj[v]
        if len(nb) <= 1:
            choices.append([tuple(nb)])
        else:
            head, *tail = nb
            choices.append([(head, *p) for p in itertools.permutations(tail)])
    E = len(edges)
    V = len(verts)
    for combo in itertools.product(*choices):
        rot = dict(zip(verts, combo))
        directed = {(u, v) for u, v in edges} | {(v, u) for u, v in edges}
        seen: set[tuple[int, int]] = set()
        faces = 0
        for start in sorted(directed):
            if start in seen:
                continue
            faces += 1
            d = start
            while d not in seen:
                seen.add(d)
                a, b = d
                order = rot[b]
                d = (b, order[(order.index(a) + 1) % len(order)])
        if V - E + faces == 2:
            return True
    return False


# ---------------------------------------------------------------------------
# exact Neuwirth genus potential (AK3_NEUWIRTH.md Lemma 1 / equation (E))
# ---------------------------------------------------------------------------


def support_analysis(
    verts: list[int], edges: frozenset[tuple[int, int]]
) -> dict[str, object]:
    """Rigidity data for a simple support: connectivity and #spherical rotations.

    Whitney: a 3-connected planar graph has exactly two spherical rotation
    systems (a reflection pair).  More than two means the support has embedding
    freedom -- the relative-shift phenomenon the P4 solver had to handle -- so
    the K6-E(P5) rigidity argument cannot be reused verbatim.
    """
    adj: dict[int, set[int]] = {v: set() for v in verts}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    def connected(sub: set[int]) -> bool:
        if not sub:
            return True
        s = next(iter(sub))
        seen, stack = {s}, [s]
        while stack:
            v = stack.pop()
            for u in adj[v] & sub - seen:
                seen.add(u)
                stack.append(u)
        return seen == sub

    kappa = len(verts) - 1
    for k in range(0, len(verts)):
        cut_found = False
        for cut in itertools.combinations(verts, k):
            rest = set(verts) - set(cut)
            if len(rest) >= 2 and not connected(rest):
                cut_found = True
                break
        if cut_found:
            kappa = k
            break
    n_rot = 0
    choices = []
    for v in verts:
        nb = sorted(adj[v])
        head, *tail = nb
        choices.append([(head, *p) for p in itertools.permutations(tail)])
    E, V = len(edges), len(verts)
    directed = {(u, v) for u, v in edges} | {(v, u) for u, v in edges}
    for combo in itertools.product(*choices):
        rot = dict(zip(verts, combo))
        seen: set[tuple[int, int]] = set()
        faces = 0
        for start in sorted(directed):
            if start in seen:
                continue
            faces += 1
            d = start
            while d not in seen:
                seen.add(d)
                a, b = d
                order = rot[b]
                d = (b, order[(order.index(a) + 1) % len(order)])
        if V - E + faces == 2:
            n_rot += 1
    return {
        "vertex_connectivity": kappa,
        "three_connected": kappa >= 3,
        "spherical_rotations_of_simple_support": n_rot,
        "rigid_whitney_pair": n_rot == 2,
    }


def compatible_case_count(link: Link) -> int:
    total = 1
    for darts in link.pos_darts:
        if not darts:
            raise ValueError("Neuwirth scope: every generator must occur")
        total *= math.factorial(len(darts) - 1)
    return total


def _cycle_count(perm: list[int]) -> int:
    n = len(perm)
    seen = [False] * n
    cycles = 0
    for i in range(n):
        if seen[i]:
            continue
        cycles += 1
        j = i
        while not seen[j]:
            seen[j] = True
            j = perm[j]
    return cycles


def neuwirth_min_genus(
    link: Link, budget: int = 2_000_000, stop_at_zero: bool = True
) -> dict[str, object]:
    """Exhaustive gamma_N = min over compatible orderings of the summed genus."""
    cases = compatible_case_count(link)
    if cases > budget:
        return {
            "decided": False,
            "reason": f"factorial budget exceeded ({cases} > {budget})",
            "cases": cases,
        }
    n = len(link.A)
    L = len(components(link))
    n_A = n // 2
    n_C = 2 * len(link.gens)
    per_gen = []
    for darts in link.pos_darts:
        head, *tail = list(darts)
        per_gen.append([(head, *p) for p in itertools.permutations(tail)])
    best = None
    scanned = 0
    for combo in itertools.product(*per_gen):
        C = [-1] * n
        for order in combo:
            m = len(order)
            for i, p in enumerate(order):
                C[p] = order[(i + 1) % m]
            rev = [link.B[p] for p in reversed(order)]
            for i, p in enumerate(rev):
                C[p] = rev[(i + 1) % m]
        AC = [link.A[C[d]] for d in range(n)]
        n_AC = _cycle_count(AC)
        genus2 = n_A - n_C + 2 * L - n_AC
        assert genus2 >= 0 and genus2 % 2 == 0, "genus defect must be even >= 0"
        g = genus2 // 2
        scanned += 1
        if best is None or g < best:
            best = g
            if stop_at_zero and best == 0:
                break
    return {
        "decided": True,
        "cases": cases,
        "scanned": scanned,
        "components": L,
        "gamma_N": best,
        "spherical_candidate": best == 0,
    }


# ---------------------------------------------------------------------------
# support classification (names used by the repo's certified solver ladder)
# ---------------------------------------------------------------------------

_NAMED = {
    "K4": (4, 6, [3, 3, 3, 3]),
    "K4-e": (4, 5, [2, 2, 3, 3]),
    "C4": (4, 4, [2, 2, 2, 2]),
    "P4": (4, 3, [1, 1, 2, 2]),
}


def _is_k6_minus_p5(verts: list[int], edges: frozenset[tuple[int, int]]) -> bool:
    if len(verts) != 6 or len(edges) != 11:
        return False
    allpairs = {
        (min(a, b), max(a, b)) for a in verts for b in verts if a != b
    }
    comp = allpairs - set(edges)
    if len(comp) != 4:
        return False
    adj: dict[int, set[int]] = {v: set() for v in verts}
    for u, v in comp:
        adj[u].add(v)
        adj[v].add(u)
    if sorted(map(len, adj.values())) != [0, 1, 1, 2, 2, 2]:
        return False
    non = {v for v in verts if adj[v]}
    seen = {min(non)}
    stack = list(seen)
    while stack:
        v = stack.pop()
        for u in adj[v] - seen:
            seen.add(u)
            stack.append(u)
    return seen == non


def classify(link: Link) -> dict[str, object]:
    simple, loops = simple_support(link)
    comps = components(link)
    verts = sorted(active_germs(link))
    deg: dict[int, int] = {v: 0 for v in verts}
    for u, v in simple:
        deg[u] += 1
        deg[v] += 1
    kind = "OTHER"
    if loops:
        kind = "HAS_LOOP"
    elif len(comps) > 1:
        kind = "DISCONNECTED"
    else:
        degs = sorted(deg.values())
        for name, (nv, ne, dd) in _NAMED.items():
            if len(verts) == nv and len(simple) == ne and degs == dd:
                kind = name
                break
        else:
            if _is_k6_minus_p5(verts, simple):
                kind = "K6-E(P5)"
    planar, why = is_planar(verts, simple)
    mult: dict[str, int] = {}
    for e in link.edges:
        mult[f"{e[0]}-{e[1]}"] = mult.get(f"{e[0]}-{e[1]}", 0) + 1
    return {
        "words": list(link.words),
        "gens": link.gens,
        "total_length": sum(map(len, link.words)),
        "germ_vertices": verts,
        "germ_labels": [
            (link.gens[v // 2] + ("+" if v % 2 == 0 else "-")) for v in verts
        ],
        "n_corner_edges": len(link.edges),
        "simple_edges": sorted(map(list, simple)),
        "loop_germs": sorted(loops),
        "degrees": [deg[v] for v in verts],
        "parallel_multiplicities": dict(sorted(mult.items())),
        "components": [sorted(c) for c in comps],
        "n_components": len(comps),
        "support_kind": kind,
        "simple_support_planar": planar,
        "planarity_reason": why,
        "certified_family": kind in ("K4", "K4-e", "C4", "P4", "K6-E(P5)"),
        "compatible_orderings": compatible_case_count(link),
    }


# ---------------------------------------------------------------------------
# targets
# ---------------------------------------------------------------------------

AK3 = ("xxxYYYY", "xyxYXY")
Q = ("xYxYXyyXYxyXy", "XyyXYXyxYYxy")
A_WORD = "xzYXyxZXYxyZ"
B_WORD = "XyxZXYXyxzXYxy"
K_PUB = "Xyz"
K_XY = "zYX"

TARGETS = (
    ("ak3_stabilized", (AK3[0], AK3[1], "z"), "xyz"),
    ("Q_stabilized", (Q[0], Q[1], "z"), "xyz"),
    ("Tpub", (A_WORD, B_WORD, K_PUB), "xyz"),
    ("Txy_certified_trivial", (A_WORD, B_WORD, K_XY), "xyz"),
    ("ak3_rank2_degenerate", AK3, "xy"),
    ("Q_rank2", Q, "xy"),
)


# ---------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------

# From experiments/stable_ac/thickenable/two_hop_cov_thickenability_certificate.
# CALIBRATIONS: independently pinned expected_cases and minimum_genus.
REPO_CALIBRATIONS = (
    (("yx", "yxXX"), 6, 0),
    (("XYyyX", "X"), 4, 1),
    (("x", "xxyxYy"), 12, 0),
)

GRAPH_CONTROLS = (
    ("K5", [0, 1, 2, 3, 4], [(a, b) for a in range(5) for b in range(a + 1, 5)], False),
    ("K3,3", list(range(6)), [(a, b + 3) for a in range(3) for b in range(3)], False),
    ("K4", [0, 1, 2, 3], [(a, b) for a in range(4) for b in range(a + 1, 4)], True),
    ("C4", [0, 1, 2, 3], [(0, 1), (1, 2), (2, 3), (0, 3)], True),
    ("P4", [0, 1, 2, 3], [(0, 1), (1, 2), (2, 3)], True),
    (
        "K6-E(P5)",
        list(range(6)),
        sorted(
            {(min(a, b), max(a, b)) for a in range(6) for b in range(6) if a != b}
            - {(0, 1), (1, 2), (2, 3), (3, 4)}
        ),
        True,
    ),
    ("K5-e", [0, 1, 2, 3, 4], [
        (a, b) for a in range(5) for b in range(a + 1, 5) if (a, b) != (3, 4)
    ], True),
)

# A word-level rank-three control whose link graph is non-planar (found by a
# bounded random scan over cyclically reduced length-6 triples; pinned here).
NONPLANAR_WORDS = ("YZyzzx", "zxxxZY", "YXyX")

# The standard rank-three presentation.  It is thickenable (Lackenby Lemma 3.1:
# three cancelling 1-/2-handle pairs collapse N(K) to a 3-ball), so it is the
# positive control for gamma_N -- and its link graph is DISCONNECTED, which is
# exactly the case the repo's certified ladder rejects as UNSUPPORTED.
STANDARD3 = ("x", "y", "z")


def run_controls() -> dict[str, object]:
    rec: dict[str, object] = {}

    # (1) graph-level planarity oracle vs independent rotation-system oracle
    graph_rows = []
    for name, verts, edges, expect in GRAPH_CONTROLS:
        es = frozenset((min(a, b), max(a, b)) for a, b in edges)
        got, why = is_planar(verts, es)
        alt = rotation_genus0_exists(verts, es)
        check(f"planarity oracle: {name} planar={expect}", got is expect, why)
        check(
            f"rotation-system oracle agrees: {name}",
            alt is None or alt is expect,
            f"rotation={alt}",
        )
        graph_rows.append(
            {"name": name, "expected_planar": expect, "minor_oracle": got,
             "rotation_oracle": alt, "reason": why}
        )
    rec["graph_controls"] = graph_rows

    # (2) my link-graph dictionary vs the repo's rank-two builder
    try:
        sys.path.insert(0, str(REPO))
        from experiments.stable_ac.thickenable import (  # noqa: E402
            neuwirth_rank_solver as base,
        )
        agree = []
        for words in (AK3, Q, ("yx", "yxXX"), ("XYyyX", "X"), ("x", "xxyxYy")):
            mine = build_link(words, "xy")
            theirs = base._build_link_data(tuple(words))
            same_edges = sorted(mine.edges) == sorted(theirs.edge_class)
            same_A = mine.A == theirs.A and mine.B == theirs.B
            same_germ = mine.germ == theirs.germ
            ok = same_edges and same_A and same_germ
            check(f"rank-2 dictionary matches repo builder: {words}", ok)
            agree.append(
                {"words": list(words), "edges": same_edges, "A_B": same_A,
                 "germ": same_germ}
            )
        rec["repo_builder_agreement"] = agree
    except Exception as exc:  # pragma: no cover - import guard
        check("import repo rank-2 builder", False, repr(exc))
        rec["repo_builder_agreement"] = f"import failed: {exc!r}"

    # (3) exact gamma_N vs the repo's pinned factorial calibrations
    calib = []
    for words, cases, genus in REPO_CALIBRATIONS:
        link = build_link(words, "xy")
        got_cases = compatible_case_count(link)
        res = neuwirth_min_genus(link, stop_at_zero=False)
        check(f"calibration case count {words}", got_cases == cases,
              f"{got_cases} vs {cases}")
        check(f"calibration min genus {words}", res.get("gamma_N") == genus,
              f"{res.get('gamma_N')} vs {genus}")
        calib.append(
            {"words": list(words), "expected_cases": cases, "cases": got_cases,
             "expected_min_genus": genus, "gamma_N": res.get("gamma_N")}
        )
    rec["repo_calibrations"] = calib

    # (4) a word-level rank-three non-planar control
    link = build_link(NONPLANAR_WORDS, "xyz")
    cls = classify(link)
    check(
        "rank-3 word control has non-planar simple support",
        cls["simple_support_planar"] is False,
        str(cls["planarity_reason"]),
    )
    rec["nonplanar_word_control"] = cls

    # (5) positive control: the standard rank-three presentation must be a
    # spherical candidate, and it must be DISCONNECTED (so the repo's ladder
    # cannot see a presentation that is provably thickenable).
    std = build_link(STANDARD3, "xyz")
    std_cls = classify(std)
    std_g = neuwirth_min_genus(std, stop_at_zero=False)
    check("standard rank-3 presentation has gamma_N = 0",
          std_g.get("gamma_N") == 0, str(std_g))
    check("standard rank-3 link graph is disconnected (3 components)",
          std_cls["n_components"] == 3, str(std_cls["components"]))
    rec["standard_positive_control"] = {"classification": std_cls,
                                        "gamma": std_g}

    # (6) the z-row splitting lemma, verified numerically on AK(3)
    g2 = neuwirth_min_genus(build_link(AK3, "xy"), stop_at_zero=False)
    g3 = neuwirth_min_genus(build_link((AK3[0], AK3[1], "z"), "xyz"),
                            stop_at_zero=False)
    check(
        "z-row splitting: gamma_N(r1,r2,z) == gamma_N(r1,r2)",
        g2.get("gamma_N") == g3.get("gamma_N") and g2.get("decided"),
        f"rank2={g2.get('gamma_N')} rank3={g3.get('gamma_N')}",
    )
    rec["z_row_splitting"] = {"rank2": g2, "rank3": g3}
    return rec


# ---------------------------------------------------------------------------
# targets mode
# ---------------------------------------------------------------------------


def run_targets(genus_budget: int) -> dict[str, object]:
    rows = []
    for name, words, gens in TARGETS:
        link = build_link(words, gens)
        cls = classify(link)
        cls["name"] = name
        if cls["n_components"] == 1 and not cls["loop_germs"]:
            cls["rigidity"] = support_analysis(
                list(cls["germ_vertices"]),  # type: ignore[arg-type]
                frozenset(tuple(e) for e in cls["simple_edges"]),  # type: ignore
            )
        gam = neuwirth_min_genus(link, budget=genus_budget, stop_at_zero=False)
        cls["gamma"] = gam
        if gam.get("decided"):
            g = gam["gamma_N"]
            cls["verdict"] = (
                "NOT_THICKENABLE (gamma_N > 0, necessity direction)"
                if g else "SPHERICAL_CANDIDATE_QUARANTINED"
            )
        else:
            cls["verdict"] = "UNDECIDED_HERE (factorial budget)"
        rows.append(cls)
        print(
            f"  {name:26s} kind={cls['support_kind']:14s} "
            f"planar={cls['simple_support_planar']} "
            f"comps={cls['n_components']} "
            f"orderings={cls['compatible_orderings']} "
            f"gamma_N={gam.get('gamma_N')} -> {cls['verdict']}"
        )
    return {"targets": rows}


def run_dispatch_crosscheck() -> dict[str, object]:
    """Run the repo's certified rank-2 ladder on the degenerate rank-2 targets."""
    out = []
    try:
        sys.path.insert(0, str(REPO))
        from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
            solve_spherical,
        )
        from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
            solve_four_germ_spherical,
        )
        from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
            solve_one_loop_spherical,
        )
        from experiments.stable_ac.thickenable.neuwirth_paw_one_loop_solver import (
            solve_paw_one_loop_spherical,
        )

        def dispatch(words):
            d = solve_spherical(words)
            if d.spherical is None:
                d = solve_four_germ_spherical(words)
            if d.spherical is None:
                d = solve_one_loop_spherical(words)
            if d.spherical is None:
                d = solve_paw_one_loop_spherical(words)
            return d

        for words in (AK3, Q):
            d = dispatch(words)
            verdict = (
                "UNSUPPORTED" if d.spherical is None
                else ("SPHERICAL_REQUIRES_REGINA" if d.spherical
                      else "NOT_SPHERICAL")
            )
            mine = neuwirth_min_genus(build_link(words, "xy"),
                                      stop_at_zero=False)
            row = {"words": list(words), "repo_support": d.support.kind,
                   "repo_verdict": verdict, "my_gamma_N": mine.get("gamma_N")}
            if d.spherical is not None and mine.get("decided"):
                agree = (d.spherical is False) == (mine["gamma_N"] > 0)
                check(f"repo ladder agrees with exact gamma_N on {words}", agree,
                      f"{verdict} vs gamma_N={mine['gamma_N']}")
                row["agrees"] = agree
            out.append(row)
            print(f"  repo ladder {words}: {d.support.kind} {verdict}; "
                  f"exact gamma_N={mine.get('gamma_N')}")

        # z-row splitting transport: for a triple (r1, r2, z) whose first two
        # rows are z-free, the compatible orderings factor over generators and
        # the link graph splits as (xy-part) u (the single z-edge, genus 0), so
        # gamma_N(r1, r2, z) = gamma_N(r1, r2) exactly.  The repo's CERTIFIED
        # rank-2 verdict therefore transports to the stabilized triple.
        for name, pair in (("ak3_stabilized", AK3), ("Q_stabilized", Q)):
            assert all("z" not in w.lower() for w in pair)
            d = dispatch(pair)
            v = ("UNSUPPORTED" if d.spherical is None
                 else ("SPHERICAL_REQUIRES_REGINA" if d.spherical
                       else "NOT_SPHERICAL"))
            transported = (
                "NOT_THICKENABLE (transported by z-row splitting)"
                if d.spherical is False
                else "NOT_TRANSPORTED"
            )
            check(f"z-row splitting transports a certified negative to {name}",
                  d.spherical is False, f"{d.support.kind} {v}")
            check(f"the transported rank-2 negative is exhaustive ({name})",
                  d.spherical is not False or d.counters.exhaustive,
                  f"exhaustive={d.counters.exhaustive}")
            out.append({"transport_target": name, "rank2_pair": list(pair),
                        "rank2_support": d.support.kind, "rank2_verdict": v,
                        "rank3_verdict": transported})
            print(f"  transport {name}: rank-2 {d.support.kind} {v} "
                  f"-> {transported}")

        # the only certified RANK-THREE family, run on the connected targets
        from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import (
            solve_rigid_spherical,
        )
        table = str.maketrans("xyzXYZ", "xztXZT")
        for name, words in (("Tpub", (A_WORD, B_WORD, K_PUB)),
                            ("Txy", (A_WORD, B_WORD, K_XY)),
                            ("ak3_stabilized", (AK3[0], AK3[1], "z")),
                            ("Q_stabilized", (Q[0], Q[1], "z"))):
            d = solve_rigid_spherical(tuple(w.translate(table) for w in words))
            v = ("UNSUPPORTED" if d.spherical is None
                 else ("SPHERICAL_REQUIRES_REGINA" if d.spherical
                       else "NOT_SPHERICAL"))
            out.append({"rigid_target": name, "support": d.support.kind,
                        "verdict": v, "reason": d.support.reason})
            print(f"  rigid solver {name}: {d.support.kind} {v} "
                  f"({d.support.reason})")
    except Exception as exc:  # pragma: no cover
        check("import repo certified ladder", False, repr(exc))
        out.append({"error": repr(exc)})
    return {"dispatch_crosscheck": out}


# ---------------------------------------------------------------------------
# bounded rank-three AC ball
# ---------------------------------------------------------------------------


def ac_neighbours(state: tuple[str, ...], gens: str) -> list[tuple[str, ...]]:
    """AC1/AC2/AC3 neighbours.  AC1 and cyclic AC3 are absorbed by canon_word."""
    out = []
    n = len(state)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for e in (1, -1):
                donor = state[j] if e == 1 else inv(state[j])
                new = list(state)
                new[i] = free_reduce(state[i] + donor)
                if new[i]:
                    out.append(tuple(new))
    for i in range(n):
        for g in gens:
            for letter in (g, g.upper()):
                new = list(state)
                new[i] = free_reduce(letter + state[i] + letter.swapcase())
                if new[i]:
                    out.append(tuple(new))
    return out


def run_ball(
    ceiling: int,
    pops: int,
    gens: str,
    start: tuple[str, ...],
    genus_budget: int = 0,
) -> dict:
    import heapq

    start_c = canon_state(start)
    seen = {start_c}
    heap = [(sum(map(len, start_c)), start_c)]
    popped = 0
    closed = True
    while heap:
        if popped >= pops:
            closed = False
            break
        _, st = heapq.heappop(heap)
        popped += 1
        for nb in ac_neighbours(st, gens):
            c = canon_state(nb)
            if any(not r for r in c):
                continue
            if sum(map(len, c)) > ceiling:
                continue
            if c in seen:
                continue
            seen.add(c)
            heapq.heappush(heap, (sum(map(len, c)), c))
    rigid = None
    try:
        sys.path.insert(0, str(REPO))
        from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import (
            solve_rigid_spherical,
        )
        rigid = solve_rigid_spherical
    except Exception as exc:  # pragma: no cover
        check("import repo rank-3 rigid solver", False, repr(exc))

    def to_rigid(words: tuple[str, ...]) -> tuple[str, ...]:
        """Relabel x,y,z -> x,z,t (the rigid solver's germ alphabet, same ids)."""
        table = str.maketrans("xyzXYZ", "xztXZT")
        return tuple(w.translate(table) for w in words)

    rows = []
    kinds: dict[str, int] = {}
    planar_n = 0
    decidable = 0
    rigid_verdicts: dict[str, int] = {}
    gamma_counts: dict[str, int] = {}
    for st in sorted(seen):
        try:
            link = build_link(st, gens)
            cls = classify(link)
        except ValueError as exc:
            kinds["GENERATOR_ABSENT"] = kinds.get("GENERATOR_ABSENT", 0) + 1
            rows.append({"state": list(st), "error": str(exc)})
            continue
        kinds[str(cls["support_kind"])] = kinds.get(str(cls["support_kind"]), 0) + 1
        planar_n += bool(cls["simple_support_planar"])
        decidable += bool(cls["certified_family"])
        row = {"state": list(st), "total_length": cls["total_length"],
               "support_kind": cls["support_kind"],
               "n_components": cls["n_components"],
               "planar": cls["simple_support_planar"],
               "certified_family": cls["certified_family"],
               "compatible_orderings": cls["compatible_orderings"]}
        if rigid is not None and cls["support_kind"] == "K6-E(P5)":
            d = rigid(to_rigid(st))
            v = ("UNSUPPORTED" if d.spherical is None
                 else ("SPHERICAL_REQUIRES_REGINA" if d.spherical
                       else "NOT_SPHERICAL"))
            if d.spherical is False and not d.counters.exhaustive:
                raise AssertionError(f"incomplete rigid negative on {st}")
            row["rigid_verdict"] = v
            row["rigid_support"] = d.support.kind
            rigid_verdicts[v] = rigid_verdicts.get(v, 0) + 1
        if genus_budget and cls["compatible_orderings"] <= genus_budget:
            g = neuwirth_min_genus(link, budget=genus_budget,
                                   stop_at_zero=False)
            row["gamma_N"] = g.get("gamma_N")
            if g.get("gamma_N") == 0:
                row["QUARANTINED_POSITIVE"] = True
            gamma_counts[str(g.get("gamma_N"))] = (
                gamma_counts.get(str(g.get("gamma_N")), 0) + 1
            )
        rows.append(row)
    return {
        "rigid_verdicts": dict(sorted(rigid_verdicts.items())),
        "gamma_N_counts": dict(sorted(gamma_counts.items())),
        "gamma_budget": genus_budget,
        "start": list(start_c),
        "gens": gens,
        "ceiling": ceiling,
        "pop_cap": pops,
        "pops_used": popped,
        "closed_under_cap": closed,
        "frontier_left": len(heap),
        "canonical_states": len(seen),
        "support_kind_counts": dict(sorted(kinds.items())),
        "planar_simple_support": planar_n,
        "in_certified_family": decidable,
        "states": rows,
    }


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("controls", "targets", "ball"))
    ap.add_argument("--ceiling", type=int, default=16)
    ap.add_argument("--pops", type=int, default=1000)
    ap.add_argument("--genus-budget", type=int, default=200_000)
    ap.add_argument("--ball-genus-budget", type=int, default=0)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    if args.pops > 1000:
        raise SystemExit("repo hard rule: node budget is capped at 1,000")

    OUT.mkdir(parents=True, exist_ok=True)
    if args.mode == "controls":
        data = run_controls()
        path = OUT / "w6_controls.json"
    elif args.mode == "targets":
        data = run_targets(args.genus_budget)
        data.update(run_dispatch_crosscheck())
        path = OUT / "w6_link_graphs.json"
    else:
        data = run_ball(
            args.ceiling, args.pops, "xyz", (AK3[0], AK3[1], "z"),
            genus_budget=args.ball_genus_budget,
        )
        print(
            f"  states={data['canonical_states']} pops={data['pops_used']} "
            f"closed={data['closed_under_cap']} "
            f"kinds={data['support_kind_counts']} rigid={data['rigid_verdicts']} "
            f"gamma={data['gamma_N_counts']} "
            f"certified={data['in_certified_family']}"
        )
        path = OUT / f"w6_ac_ball_c{args.ceiling}.json"
    if args.out:
        path = Path(args.out)
    data["_fails"] = FAILS
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"wrote {path}")
    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
