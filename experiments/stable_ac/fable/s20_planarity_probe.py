"""S20 -- exact planarity of the Neuwirth link graph, with machine-checkable certificates.

Question this instrument exists to answer (see
``results/stable_ac/theory/fable/S20_PLANARITY_OBSTRUCTION.md``):

    is the *simple support* ``S`` of the link multigraph ``G_A`` planar?

``S`` non-planar is a **LOWER** bound on ``gamma_N``: a defect-0 compatible rotation system
is a genus-0 embedding of ``G_A``, hence a planar embedding, hence ``S`` planar.  So
``S`` non-planar ==> ``gamma_N >= 1``.  Nothing here bounds ``gamma_N`` from above.

Why a new planarity implementation.  ``networkx`` is not installed in this clone
(``python3 -c "import networkx"`` -> ModuleNotFoundError), so ``check_planarity`` (LR) is
unavailable.  The repo's own exact test, ``neuwirth_rank_n.macro_rotations``, enumerates
*every* rotation system of ``S`` and keeps the genus-0 ones; it is exact but its family
size is ``prod_v (deg(v) - 1)!``, which blows past the 2e6 macro budget for the rank-12/13
supports this probe must sweep.  So this module implements the classical
Demoucron--Malgrange--Pertuiset path-addition test, and -- because a hand-rolled planarity
test must never be taken on trust -- **every verdict carries a certificate that is checked
independently of the algorithm that produced it**:

* PLANAR  -> an explicit face set per block, verified by ``verify_sphere_embedding``:
  every face is a closed walk in the block, every edge lies on exactly two faces, the
  corners at every vertex form a single cycle (so the polygonal complex is a surface), and
  ``|V| - |E| + |F| = 2`` (so that surface is a sphere).  Nothing about Demoucron is
  trusted; the checker would reject a wrong embedding.
* NONPLANAR -> an edge-minimal non-planar subgraph, verified to be a subdivision of ``K5``
  or ``K3,3`` after suppressing degree-2 vertices.  By Kuratowski's theorem a graph
  containing such a subdivision is non-planar, so the certificate stands on its own.

``selftest`` additionally cross-checks the whole test against ``macro_rotations`` (a
completely different algorithm: exhaustive rotation-system enumeration) on named graphs and
on random graphs small enough for the macro budget.

New file; nothing under ``experiments/`` or ``ac_solver/`` is modified.

CLI::

    python3 -m experiments.stable_ac.fable.s20_planarity_probe selftest
    python3 -m experiments.stable_ac.fable.s20_planarity_probe ak3
    python3 -m experiments.stable_ac.fable.s20_planarity_probe sweep --sample 3000
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import time
from collections import deque
from pathlib import Path

from experiments.stable_ac.fable.neuwirth_core import NeuwirthInputError
from experiments.stable_ac.fable.neuwirth_rank_n import (
    NONPLANAR as MACRO_NONPLANAR,
    PLANAR as MACRO_PLANAR,
    UNDETERMINED as MACRO_UNDETERMINED,
    build_link_n,
    generators_of,
    germ_names,
    macro_rotations,
    simple_support,
)

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "results" / "stable_ac" / "fable"


# ======================================================================================
# tiny graph utilities.  A graph is (vertices: tuple, edges: set of sorted 2-tuples).
# ======================================================================================


def ekey(u, v):
    return (u, v) if u <= v else (v, u)


def adjacency(vertices, edges):
    adj = {v: set() for v in vertices}
    for u, v in edges:
        if u == v:
            continue
        adj[u].add(v)
        adj[v].add(u)
    return {v: sorted(s) for v, s in adj.items()}


def components(vertices, adj, banned=()):
    banned = set(banned)
    seen = set()
    out = []
    for s in vertices:
        if s in banned or s in seen:
            continue
        comp = {s}
        seen.add(s)
        stack = [s]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w in banned or w in seen:
                    continue
                seen.add(w)
                comp.add(w)
                stack.append(w)
        out.append(comp)
    return out


class _DSU:
    def __init__(self, items):
        self.p = {x: x for x in items}

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb

    def classes(self):
        out = {}
        for x in self.p:
            out.setdefault(self.find(x), []).append(x)
        return list(out.values())


def blocks(vertices, edges):
    """Biconnected components as edge sets.

    Uses the definition directly rather than Hopcroft--Tarjan: two edges incident to a
    common vertex ``v`` lie in the same block iff their far endpoints lie in the same
    connected component of ``G - v``.  |V| here is at most a few dozen, so the O(V(V+E))
    cost is irrelevant and the correctness is immediate.
    """
    edges = sorted(edges)
    if not edges:
        return []
    adj = adjacency(vertices, edges)
    dsu = _DSU(edges)
    for v in vertices:
        inc = [e for e in edges if v in e]
        if len(inc) < 2:
            continue
        comps = components(vertices, adj, banned=(v,))
        where = {}
        for i, c in enumerate(comps):
            for w in c:
                where[w] = i
        buckets = {}
        for e in inc:
            far = e[0] if e[1] == v else e[1]
            buckets.setdefault(where[far], []).append(e)
        for grp in buckets.values():
            for e in grp[1:]:
                dsu.union(grp[0], e)
    return [set(c) for c in dsu.classes()]


def find_cycle(vertices, edges):
    """Any cycle of the graph, as a vertex list; ``None`` if the graph is a forest."""
    adj = adjacency(vertices, edges)
    parent = {}
    seen = set()
    for root in vertices:
        if root in seen:
            continue
        seen.add(root)
        parent[root] = None
        stack = [(root, iter(adj[root]))]
        while stack:
            v, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                stack.pop()
                continue
            w = nxt
            if w == parent[v]:
                continue
            if w in seen:
                cyc = [v]
                cur = v
                while cur != w:
                    cur = parent[cur]
                    cyc.append(cur)
                cyc.reverse()
                return cyc
            seen.add(w)
            parent[w] = v
            stack.append((w, iter(adj[w])))
    return None


# ======================================================================================
# Demoucron--Malgrange--Pertuiset path addition, on ONE 2-connected block
# ======================================================================================


class _Frag:
    __slots__ = ("att", "edges", "interior")

    def __init__(self, att, edges, interior):
        self.att = att
        self.edges = edges
        self.interior = interior


def _fragments(vertices, edges, Hv, He, adj):
    outside = [v for v in vertices if v not in Hv]
    frags = []
    seen = set()
    for s in outside:
        if s in seen:
            continue
        seen.add(s)
        K = {s}
        stack = [s]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w in Hv or w in seen:
                    continue
                seen.add(w)
                K.add(w)
                stack.append(w)
        att = set()
        fe = set()
        for v in K:
            for w in adj[v]:
                fe.add(ekey(v, w))
                if w in Hv:
                    att.add(w)
        frags.append(_Frag(att, fe, K))
    for e in edges:
        if e in He:
            continue
        u, v = e
        if u in Hv and v in Hv:
            frags.append(_Frag({u, v}, {e}, set()))
    return frags


def _fragment_path(frag, adj, Hv):
    """A path through the fragment joining two distinct attachment vertices."""
    if not frag.interior:
        u, v = sorted(frag.edges)[0]
        return [u, v]
    a1 = min(frag.att)
    prev = {}
    q = deque()
    for w in adj[a1]:
        if w in frag.interior and w not in prev:
            prev[w] = a1
            q.append(w)
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w in Hv:
                if w == a1:
                    continue
                path = [w, v]
                cur = v
                while prev[cur] != a1:
                    cur = prev[cur]
                    path.append(cur)
                path.append(a1)
                path.reverse()
                return path
            if w not in prev:
                prev[w] = v
                q.append(w)
    return None


def _split_face(cyc, path):
    a, b = path[0], path[-1]
    interior = path[1:-1]
    i, j = cyc.index(a), cyc.index(b)
    if i > j:
        i, j = j, i
        interior = list(reversed(interior))
    face_a = cyc[i:j + 1] + list(reversed(interior))
    face_b = cyc[j:] + cyc[:i + 1] + list(interior)
    return face_a, face_b


def demoucron_block(vertices, edges):
    """Return ``(True, faces)`` or ``(False, None)`` for a 2-connected block."""
    vertices = sorted(vertices)
    edges = set(edges)
    n, m = len(vertices), len(edges)
    if n <= 2 or m <= 2:
        return True, None                     # a single edge / a path: trivially planar
    if m > 3 * n - 6:
        return False, None                    # Euler sparsity: correct rejection
    adj = adjacency(vertices, edges)
    cyc = find_cycle(vertices, edges)
    if cyc is None:
        return True, None
    faces = [list(cyc), list(cyc)]
    Hv = set(cyc)
    He = {ekey(cyc[k], cyc[(k + 1) % len(cyc)]) for k in range(len(cyc))}
    guard = 0
    while He != edges:
        guard += 1
        if guard > 4 * m + 16:
            raise RuntimeError("demoucron did not terminate")
        frags = _fragments(vertices, edges, Hv, He, adj)
        if not frags:
            raise RuntimeError("no fragments but H != G")
        best = None
        for f in frags:
            adm = [k for k, face in enumerate(faces) if f.att <= set(face)]
            if not adm:
                return False, None
            if best is None or len(adm) < len(best[1]):
                best = (f, adm)
            if len(adm) == 1:
                break
        frag, adm = best
        path = _fragment_path(frag, adj, Hv)
        if path is None:
            raise RuntimeError("fragment with fewer than two attachments")
        fi = adm[0]
        fa, fb = _split_face(faces[fi], path)
        faces[fi] = fa
        faces.append(fb)
        for k in range(len(path) - 1):
            He.add(ekey(path[k], path[k + 1]))
        Hv.update(path)
    return True, faces


# ======================================================================================
# independent certificate checkers
# ======================================================================================


def verify_sphere_embedding(vertices, edges, faces):
    """Check that ``faces`` is a genuine genus-0 (sphere) embedding of the graph.

    This does not use Demoucron at all: it validates the combinatorial surface directly.
    Returns ``(ok, reason)``.
    """
    edges = set(edges)
    vertices = set(vertices)
    if not faces:
        return False, "no faces"
    count = {e: 0 for e in edges}
    corners = {v: [] for v in vertices}
    for face in faces:
        L = len(face)
        if L < 2:
            return False, "degenerate face"
        for k in range(L):
            u, v = face[k], face[(k + 1) % L]
            e = ekey(u, v)
            if e not in edges:
                return False, f"face uses non-edge {e}"
            count[e] += 1
        for k in range(L):
            prev, cur, nxt = face[k - 1], face[k], face[(k + 1) % L]
            corners[cur].append((ekey(prev, cur), ekey(cur, nxt)))
    bad = [e for e, c in count.items() if c != 2]
    if bad:
        return False, f"{len(bad)} edge(s) not on exactly two faces, e.g. {bad[0]}"
    for v in vertices:
        inc = [e for e in edges if v in e]
        if not inc:
            continue
        deg = {e: 0 for e in inc}
        dsu = _DSU(inc)
        for e1, e2 in corners[v]:
            if e1 not in deg or e2 not in deg:
                return False, f"corner at {v} uses a non-incident edge"
            deg[e1] += 1
            deg[e2] += 1
            dsu.union(e1, e2)
        if any(d != 2 for d in deg.values()):
            return False, f"corner multigraph at {v} is not 2-regular"
        if len(dsu.classes()) != 1:
            return False, f"link of {v} is disconnected (not a surface point)"
    chi = len(vertices) - len(edges) + len(faces)
    if chi != 2:
        return False, f"Euler characteristic {chi} != 2"
    return True, None


def _suppress_degree_two(vertices, edges):
    """Suppress degree-2 vertices; returns ``(branch_vertices, multiset_of_edges)``."""
    adj = {v: [] for v in vertices}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    live = {v for v in vertices if adj[v]}
    cur = [list(e) for e in edges]

    def deg(v, arcs):
        return sum((a[0] == v) + (a[-1] == v) for a in arcs)

    changed = True
    while changed:
        changed = False
        for v in sorted(live):
            touching = [a for a in cur if a[0] == v or a[-1] == v]
            if len(touching) != 2:
                continue
            a, b = touching
            if a is b:
                continue
            pa = a if a[-1] == v else list(reversed(a))
            pb = b if b[0] == v else list(reversed(b))
            merged = pa + pb[1:]
            if merged[0] == merged[-1]:
                continue                       # would create a self-loop; keep as is
            cur = [x for x in cur if x is not a and x is not b] + [merged]
            live.discard(v)
            changed = True
            break
    branch = sorted({a[0] for a in cur} | {a[-1] for a in cur})
    simple = [ekey(a[0], a[-1]) for a in cur]
    return branch, simple


def kuratowski_kind(vertices, edges):
    """``'K5'``, ``'K33'`` or ``None`` for a claimed Kuratowski subdivision."""
    used = sorted({v for e in edges for v in e})
    branch, arcs = _suppress_degree_two(used, sorted(edges))
    if len(arcs) != len(set(arcs)):
        return None                            # parallel arcs -> not K5/K3,3
    deg = {v: 0 for v in branch}
    for u, v in arcs:
        deg[u] += 1
        deg[v] += 1
    if len(branch) == 5 and len(arcs) == 10 and all(d == 4 for d in deg.values()):
        return "K5"
    if len(branch) == 6 and len(arcs) == 9 and all(d == 3 for d in deg.values()):
        colour = {}
        adj = adjacency(branch, arcs)
        ok = True
        for s in branch:
            if s in colour:
                continue
            colour[s] = 0
            st = [s]
            while st:
                v = st.pop()
                for w in adj[v]:
                    if w not in colour:
                        colour[w] = 1 - colour[v]
                        st.append(w)
                    elif colour[w] == colour[v]:
                        ok = False
        if ok:
            return "K33"
    return None


# ======================================================================================
# the public planarity entry point
# ======================================================================================


def is_planar(vertices, edges):
    """Exact planarity of a simple graph (loops/parallel edges must be pre-collapsed)."""
    edges = {ekey(*e) for e in edges if e[0] != e[1]}
    for blk in blocks(vertices, edges):
        bverts = sorted({v for e in blk for v in e})
        ok, _ = demoucron_block(bverts, blk)
        if not ok:
            return False
    return True


def planarity_certified(vertices, edges):
    """Planarity plus a certificate that is checked independently of Demoucron."""
    edges = {ekey(*e) for e in edges if e[0] != e[1]}
    vertices = tuple(sorted(vertices))
    blks = blocks(vertices, edges)
    per_block = []
    planar = True
    for blk in blks:
        bverts = sorted({v for e in blk for v in e})
        ok, faces = demoucron_block(bverts, blk)
        if not ok:
            planar = False
            break
        if faces is None:
            per_block.append({"n": len(bverts), "m": len(blk), "trivial": True})
            continue
        good, why = verify_sphere_embedding(bverts, blk, faces)
        per_block.append({"n": len(bverts), "m": len(blk), "faces": len(faces),
                          "verified": good, "reason": why})
        if not good:
            return {"planar": None, "certified": False,
                    "reason": f"embedding checker rejected a Demoucron embedding: {why}",
                    "blocks": per_block}
    if planar:
        return {"planar": True, "certified": True, "blocks": per_block,
                "n": len(vertices), "m": len(edges)}

    # non-planar: shrink to an edge-minimal non-planar subgraph and identify it
    cur = set(edges)
    for e in sorted(edges):
        trial = cur - {e}
        if not is_planar(vertices, trial):
            cur = trial
    kind = kuratowski_kind(vertices, cur)
    return {"planar": False, "certified": kind is not None, "kuratowski": kind,
            "witness_edges": sorted(cur), "n": len(vertices), "m": len(edges)}


# ======================================================================================
# link graph of a presentation
# ======================================================================================


def link_support(words, generators=None):
    """``(vertices, edges, names, stats)`` of the SIMPLE support of the link multigraph."""
    words = tuple(w for w in words if w)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(sorted(generators))
    data = build_link_n(words, generators)
    vertices, edges, adj = simple_support(data)
    names = germ_names(generators)
    stats = {
        "germs": len(vertices),
        "simple_edges": len(edges),
        "multigraph_edges": len(data.edge_darts),
        "link_components": data.link_components,
        "has_loop": data.has_loop,
        "degrees": sorted(len(adj[v]) for v in vertices),
    }
    return vertices, edges, names, stats


def probe_words(words, generators=None):
    try:
        vertices, edges, names, stats = link_support(words, generators)
    except NeuwirthInputError as exc:
        return {"status": "INPUT_ERROR", "reason": str(exc)}
    cert = planarity_certified(vertices, edges)
    out = {"status": "OK", "words": list(words)}
    out.update(stats)
    out["planar"] = cert["planar"]
    out["certified"] = cert["certified"]
    if cert.get("kuratowski"):
        out["kuratowski"] = cert["kuratowski"]
    if cert.get("reason"):
        out["reason"] = cert["reason"]
    return out


# ======================================================================================
# self-test: named graphs + cross-check against the repo's exhaustive rotation census
# ======================================================================================


def _complete(n):
    return [ekey(i, j) for i in range(n) for j in range(i + 1, n)]


def _complete_bipartite(a, b):
    return [ekey(i, a + j) for i in range(a) for j in range(b)]


NAMED = {
    "C5": ([ekey(i, (i + 1) % 5) for i in range(5)], True),
    "K4": (_complete(4), True),
    "K5": (_complete(5), False),
    "K5-e": ([e for e in _complete(5) if e != (0, 1)], True),
    "K6": (_complete(6), False),
    "K33": (_complete_bipartite(3, 3), False),
    "K33-e": ([e for e in _complete_bipartite(3, 3) if e != (0, 3)], True),
    "K33+sub": None,          # filled in below (subdivision of K3,3)
    "Q3": ([(0, 1), (1, 2), (2, 3), (0, 3), (4, 5), (5, 6), (6, 7), (4, 7),
            (0, 4), (1, 5), (2, 6), (3, 7)], True),
    "octahedron": ([e for e in _complete(6)
                    if e not in {(0, 1), (2, 3), (4, 5)}], True),
    "petersen": ([(0, 1), (1, 2), (2, 3), (3, 4), (0, 4),
                  (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),
                  (0, 5), (1, 6), (2, 7), (3, 8), (4, 9)], False),
    "wagner_V8": ([ekey(i, (i + 1) % 8) for i in range(8)]
                  + [(0, 4), (1, 5), (2, 6), (3, 7)], False),
    "prism": ([(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5),
               (0, 3), (1, 4), (2, 5)], True),
    "two_K5_blocks": (_complete(5)
                      + [ekey(4 + i, 4 + j) for i in range(1, 6)
                         for j in range(i + 1, 6)], False),
    "tree": ([(0, 1), (1, 2), (1, 3), (3, 4), (4, 5)], True),
}


def _build_named():
    sub = []
    nxt = 6
    for u, v in _complete_bipartite(3, 3):
        sub.append(ekey(u, nxt))
        sub.append(ekey(nxt, v))
        nxt += 1
    NAMED["K33+sub"] = (sub, False)


_build_named()


def _macro_verdict(vertices, edges, budget=2_000_000):
    adj = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    adj = {v: tuple(sorted(s)) for v, s in adj.items()}
    if len(components(vertices, adj)) != 1:
        return None                        # macro_rotations assumes a connected graph
    res = macro_rotations(tuple(sorted(vertices)), tuple(sorted(edges)), adj, budget=budget)
    if res.status == MACRO_PLANAR:
        return True
    if res.status == MACRO_NONPLANAR:
        return False
    return None


def cmd_selftest(args):
    rows = []
    fails = []
    for name, (edges, expect) in sorted(NAMED.items()):
        verts = sorted({v for e in edges for v in e})
        cert = planarity_certified(verts, edges)
        macro = _macro_verdict(verts, [ekey(*e) for e in edges])
        row = {"graph": name, "expected": expect, "demoucron": cert["planar"],
               "certified": cert["certified"], "kuratowski": cert.get("kuratowski"),
               "macro": macro}
        rows.append(row)
        if cert["planar"] is not expect or not cert["certified"]:
            fails.append(row)
        if macro is not None and macro is not cert["planar"]:
            fails.append(row)

    rng = random.Random(args.seed)
    disagree = 0
    checked = 0
    skipped = 0
    for _ in range(args.random):
        n = rng.randrange(5, 9)
        verts = list(range(n))
        alle = _complete(n)
        p = rng.uniform(0.3, 0.8)
        edges = sorted(e for e in alle if rng.random() < p)
        if not edges:
            continue
        deg = {v: 0 for v in verts}
        for u, v in edges:
            deg[u] += 1
            deg[v] += 1
        fam = 1
        for v in verts:
            fam *= max(1, _fact(max(deg[v] - 1, 0)))
        if fam > 2_000_000:
            skipped += 1
            continue
        cert = planarity_certified(verts, edges)
        macro = _macro_verdict(verts, edges)
        if macro is None:
            skipped += 1
            continue
        checked += 1
        if macro is not cert["planar"] or not cert["certified"]:
            disagree += 1
            fails.append({"graph": "random", "edges": edges, "macro": macro,
                          "demoucron": cert["planar"], "certified": cert["certified"]})
    report = {"record": "s20_selftest", "named": rows,
              "random_checked": checked, "random_skipped": skipped,
              "random_disagreements": disagree, "failures": fails}
    out = OUT_DIR / "s20_selftest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    for r in rows:
        print(f"  {r['graph']:14s} expect={str(r['expected']):5s} "
              f"demoucron={str(r['demoucron']):5s} macro={str(r['macro']):5s} "
              f"cert={r['certified']} {r['kuratowski'] or ''}")
    print(f"\nrandom cross-check vs macro_rotations: {checked} graphs, "
          f"{disagree} disagreements, {skipped} skipped (macro budget)")
    print(f"FAILURES: {len(fails)}")
    print(f"wrote {out}")
    return 1 if fails else 0


def _fact(k):
    out = 1
    for i in range(2, k + 1):
        out *= i
    return out


# ======================================================================================
# AK(3) and its roots
# ======================================================================================


AK3 = ("xyxYXY", "xxxYYYY")
T2 = ("x", "y")


def cmd_ak3(args):
    rows = []
    targets = [("AK(3) rank 2", AK3)]
    # the standard presentation needs length->=1 relators only; the link has degree-1 germs
    targets.append(("T_3 standard rank 3", ("x", "y", "z")))
    targets.append(("S16 control src0 (gamma_N=0)", ("XYXXY", "XXYXYXXY")))
    targets.append(("S16 ctrl2 src0", ("XyyXy", "YxYYYxxY")))
    targets.append(("S15 C1 rank-13 cubic form",
                    ("kAe", "Xgb", "aXH", "bxH", "cYY", "ydJ", "eid", "IfC", "gKF",
                     "hAe", "igb", "jfC", "kdJ")))
    for name, words in targets:
        row = probe_words(words)
        row["name"] = name
        rows.append(row)
        print(f"  {name:34s} germs={row.get('germs')} E={row.get('simple_edges')} "
              f"planar={row.get('planar')} certified={row.get('certified')} "
              f"{row.get('kuratowski') or ''}")
    # every cubic root of the s4b pools
    for tag, path in (("ak3", "s4b_pool.jsonl.gz"),
                      ("control0", "s4b_control_pool.jsonl.gz"),
                      ("control2", "s4b_ctrl2_pool.jsonl.gz")):
        p = OUT_DIR / path
        if not p.exists():
            continue
        seen = set()
        with gzip.open(p, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                root = tuple(r.get("root") or ())
                if not root or root in seen:
                    continue
                seen.add(root)
                row = probe_words(root)
                row["name"] = f"{tag} root {r.get('provenance', '')}"
                rows.append(row)
                print(f"  ROOT {tag:9s} germs={row.get('germs')} "
                      f"E={row.get('simple_edges')} planar={row.get('planar')} "
                      f"cert={row.get('certified')} {row.get('kuratowski') or ''}")
                if len(seen) >= args.max_roots:
                    break
    out = OUT_DIR / "s20_ak3_roots.json"
    out.write_text(json.dumps({"record": "s20_ak3_roots", "rows": rows}, indent=1))
    print(f"wrote {out}")
    return 0


# ======================================================================================
# the sweep over the persisted decided artifacts
# ======================================================================================


SOURCES = [
    ("ak3", "s4b_decided.jsonl.gz"),
    ("control0", "s4b_control_decided.jsonl.gz"),
    ("control2", "s4b_ctrl2_decided.jsonl.gz"),
]


def _reservoir(path, sample, rng, want_all_zero=True):
    """All ``minimum_defect == 0`` rows plus a uniform reservoir sample of the rest."""
    zeros = []
    keep = []
    n_rows = 0
    with gzip.open(path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            n_rows += 1
            if want_all_zero and r.get("minimum_defect") == 0:
                zeros.append(r)
                continue
            if len(keep) < sample:
                keep.append(r)
            else:
                j = rng.randrange(n_rows)
                if j < sample:
                    keep[j] = r
    return zeros, keep, n_rows


def cmd_sweep(args):
    rng = random.Random(args.seed)
    t0 = time.time()
    argd = {k: v for k, v in vars(args).items() if not callable(v)}
    report = {"record": "s20_planarity_sweep", "args": argd, "sources": {}}
    for tag, fname in SOURCES:
        path = OUT_DIR / fname
        if not path.exists():
            continue
        zeros, keep, n_rows = _reservoir(path, args.sample, rng)
        block = {"file": fname, "rows_total": n_rows, "gamma0_rows": len(zeros),
                 "sampled_rows": len(keep), "gamma0": {}, "sample": {}}
        for label, rows in (("gamma0", zeros), ("sample", keep)):
            stat = {"n": 0, "planar": 0, "nonplanar": 0, "uncertified": 0,
                    "errors": 0, "kuratowski": {}, "defect_by_planarity": {},
                    "nonplanar_examples": [], "violations": []}
            for r in rows:
                out = probe_words(tuple(r["words"]))
                if out["status"] != "OK":
                    stat["errors"] += 1
                    continue
                stat["n"] += 1
                d = r.get("minimum_defect")
                key = f"{'P' if out['planar'] else 'N'}|d{d}"
                stat["defect_by_planarity"][key] = \
                    stat["defect_by_planarity"].get(key, 0) + 1
                if not out["certified"]:
                    stat["uncertified"] += 1
                if out["planar"]:
                    stat["planar"] += 1
                else:
                    stat["nonplanar"] += 1
                    k = out.get("kuratowski") or "UNCERTIFIED"
                    stat["kuratowski"][k] = stat["kuratowski"].get(k, 0) + 1
                    if len(stat["nonplanar_examples"]) < 5:
                        stat["nonplanar_examples"].append(
                            {"words": r["words"], "minimum_defect": d,
                             "kuratowski": out.get("kuratowski"),
                             "provenance": r.get("provenance")})
                    # THE falsification test for step 1
                    if d == 0:
                        stat["violations"].append(
                            {"words": r["words"], "minimum_defect": d,
                             "kuratowski": out.get("kuratowski"),
                             "provenance": r.get("provenance")})
            block[label] = stat
            print(f"  {tag:9s} {label:7s} n={stat['n']:6d} planar={stat['planar']:6d} "
                  f"nonplanar={stat['nonplanar']:6d} uncert={stat['uncertified']} "
                  f"VIOLATIONS={len(stat['violations'])}")
        report["sources"][tag] = block
    report["elapsed_s"] = round(time.time() - t0, 1)
    out = OUT_DIR / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"wrote {out}  ({report['elapsed_s']}s)")
    return 0


# ======================================================================================
# step 2: does SPLIT ever DESTROY non-planarity?  (the minor claim, tested directly)
# ======================================================================================


def _split_mod():
    """Imported lazily: `cubic_split_search` pulls in numpy and is only needed here."""
    from experiments.stable_ac.fable import cubic_split_search as CSS
    return CSS


def cmd_chains(args):
    """Replay persisted SPLIT chains and record the planarity sequence along each.

    A single ``non-planar -> planar`` transition anywhere falsifies "non-planarity is
    absorbing under SPLIT", i.e. falsifies the minor claim for this move.
    """
    CSS = _split_mod()
    rng = random.Random(args.seed)
    report = {"record": "s20_chain_planarity", "sources": {}}
    for tag, fname in (("ak3", "s4b_pool.jsonl.gz"),
                       ("control0", "s4b_control_pool.jsonl.gz"),
                       ("control2", "s4b_ctrl2_pool.jsonl.gz")):
        path = OUT_DIR / fname
        if not path.exists():
            continue
        picked = []
        n = 0
        with gzip.open(path, "rt") as fh:
            for line in fh:
                n += 1
                r = json.loads(line)
                if len(picked) < args.chains:
                    picked.append(r)
                else:
                    j = rng.randrange(n)
                    if j < args.chains:
                        picked[j] = r
        stat = {"chains": 0, "replay_ok": 0, "replay_failed": 0,
                "transitions": {}, "sequences": {}, "N_to_P": []}
        for r in picked:
            root = tuple(r.get("root") or ())
            trace = r.get("trace") or []
            if not root or not trace:
                continue
            stat["chains"] += 1
            state = root
            seq = []
            ok = True
            probe = probe_words(state)
            seq.append("P" if probe.get("planar") else "N")
            for step in trace:
                got = CSS.split_apply(state, step["relator"], step["invert"],
                                      step["rot"],
                                      tuple(tuple(p) for p in step["positions"]),
                                      step["t"])
                if got is None:
                    ok = False
                    break
                state = got[0]
                probe = probe_words(state)
                seq.append("P" if probe.get("planar") else "N")
            if not ok or CSS.canon_state(state) != CSS.canon_state(tuple(r["words"])):
                stat["replay_failed"] += 1
                continue
            stat["replay_ok"] += 1
            s = "".join(seq)
            stat["sequences"][s] = stat["sequences"].get(s, 0) + 1
            for a, b in zip(s, s[1:]):
                stat["transitions"][a + "->" + b] = \
                    stat["transitions"].get(a + "->" + b, 0) + 1
            if "NP" in s and len(stat["N_to_P"]) < 10:
                stat["N_to_P"].append({"root": list(root), "seq": s,
                                       "words": r["words"]})
        report["sources"][tag] = stat
        print(f"  {tag:9s} chains={stat['chains']} replay_ok={stat['replay_ok']} "
              f"failed={stat['replay_failed']} transitions={stat['transitions']} "
              f"N->P chains={len(stat['N_to_P'])}")
    out = OUT_DIR / args.out
    out.write_text(json.dumps(report, indent=1))
    print(f"wrote {out}")
    return 0


def cmd_splitprobe(args):
    """Hunt directly for a SPLIT that takes a NON-planar link to a planar one."""
    CSS = _split_mod()
    rng = random.Random(args.seed)
    parents = []
    n = 0
    with gzip.open(OUT_DIR / "s4b_decided.jsonl.gz", "rt") as fh:
        for line in fh:
            n += 1
            r = json.loads(line)
            if len(parents) < args.parents:
                parents.append(r)
            else:
                j = rng.randrange(n)
                if j < args.parents:
                    parents[j] = r
    stat = {"parents_tried": 0, "nonplanar_parents": 0, "children": 0,
            "planar_children": 0, "escapes": []}
    for r in parents:
        st = tuple(r["words"])
        p = probe_words(st)
        stat["parents_tried"] += 1
        if p.get("planar") is not False:
            continue
        stat["nonplanar_parents"] += 1
        kids = CSS.split_children(st, rng, max_children=args.children)
        for child, _rec in kids:
            stat["children"] += 1
            q = probe_words(child)
            if q.get("planar"):
                stat["planar_children"] += 1
                if len(stat["escapes"]) < 10:
                    stat["escapes"].append({"parent": list(st),
                                            "child": list(child)})
        if stat["nonplanar_parents"] >= args.parents:
            break
    out = OUT_DIR / args.out
    out.write_text(json.dumps({"record": "s20_split_escape_probe", "stat": stat},
                              indent=1))
    print(f"  nonplanar parents={stat['nonplanar_parents']} "
          f"children={stat['children']} PLANAR children={stat['planar_children']}")
    print(f"wrote {out}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("chains")
    c.add_argument("--chains", type=int, default=200)
    c.add_argument("--seed", type=int, default=20260804)
    c.add_argument("--out", default="s20_chain_planarity.json")
    c.set_defaults(func=cmd_chains)

    sp = sub.add_parser("splitprobe")
    sp.add_argument("--parents", type=int, default=40)
    sp.add_argument("--children", type=int, default=120)
    sp.add_argument("--seed", type=int, default=20260804)
    sp.add_argument("--out", default="s20_split_escape.json")
    sp.set_defaults(func=cmd_splitprobe)

    s = sub.add_parser("selftest")
    s.add_argument("--random", type=int, default=200)
    s.add_argument("--seed", type=int, default=20260804)
    s.set_defaults(func=cmd_selftest)

    a = sub.add_parser("ak3")
    a.add_argument("--max-roots", type=int, default=40)
    a.set_defaults(func=cmd_ak3)

    w = sub.add_parser("sweep")
    w.add_argument("--sample", type=int, default=3000)
    w.add_argument("--seed", type=int, default=20260804)
    w.add_argument("--out", default="s20_planarity_sweep.json")
    w.set_defaults(func=cmd_sweep)

    args = ap.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
