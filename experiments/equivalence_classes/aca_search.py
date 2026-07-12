"""Multi-source AC search with union-find merging.

One BFS, many roots. Every root is a source; the visited table is shared. The moment a
source reaches a state another source already owns, the two sources are **unioned** -- that
collision is a proof that their roots are AC-equivalent, because every move used is an AC
move and AC-equivalence is an equivalence relation (P ->* Z and Q ->* Z  =>  P ~AC Q,
regardless of direction).

Sharing the visited table costs nothing in completeness precisely *because* of that: a source
is never blocked from a region another source already explored -- reaching it merges them, and
merged sources search from a common frontier.

States are keyed by their **relabel-canonical** form (min over the 8 signed permutations), an
exact quotient (see ``relabel.py``), which makes the search 8x smaller at no cost in rigour.

  * two sources meeting at the same relabel key with the SAME raw canonical pair  -> ``ac``
  * two sources meeting at the same relabel key with different raw canonical pairs -> ``aca``
    (an AC path to a *relabeling* of the other's state: same problem, not the same AC class)

A length cap or a node budget removes edges, never adds them:
**every merge found is a proof; no merge found proves nothing.**
"""
import heapq
import numpy as np
from numba import njit

from experiments.equivalence_classes.acmoves import expand_nj
from experiments.equivalence_classes.relabel import (
    CODE_TO_CHAR, PERMS, _encode, apply_perm_nj, relabel_key_nj,
)
from experiments.search.greedy_baseline import (
    canonical_pair_nj, reduce_relator_nj, str_to_arr,
)


@njit(cache=True)
def _codes_to_arr_nj(buf, off, n):
    out = np.empty((n, 2), dtype=np.bool_)
    for i in range(n):
        c = buf[off + i]           # X=1, Y=2, x=3, y=4
        out[i, 0] = (c == 1) or (c == 3)
        out[i, 1] = c >= 3
    return out


@njit(cache=True)
def expand_relabel_nj(c1, c2, cap, cyclic, seam_only, perms, max_total):
    """Children of a canonical pair, each returned in relabel-canonical form.

    Returns ``(kbuf, klens, moves, sigmas, raw_same, count)``:
      ``kbuf[i, :klens[i,0]+klens[i,1]]`` = relabel-canonical codes (r1 then r2)
      ``moves[i]``    = the Definition 2.1 move (target, jsign, k1, k2) that produced the child
      ``sigmas[i]``   = index of the signed permutation that normalised it
      ``raw_same[i]`` = 1 if the raw canonical child already WAS the relabel-canonical form
                        (i.e. sigma acted trivially on it) -- this is what separates an
                        ``ac`` merge from an ``aca`` one.
    """
    codes, lens, moves, n = expand_nj(c1, c2, cap, cyclic, seam_only)
    W = 2 * cap
    kbuf = np.empty((n, W), dtype=np.uint8)
    klens = np.empty((n, 2), dtype=np.int32)
    sigmas = np.empty(n, dtype=np.int8)
    raw_same = np.empty(n, dtype=np.uint8)
    out = np.empty(W, dtype=np.uint8)
    work = np.empty(W, dtype=np.uint8)
    count = 0
    for i in range(n):
        la = lens[i, 0]
        lb = lens[i, 1]
        if la + lb > max_total:
            continue
        a = _codes_to_arr_nj(codes[i], 0, la)
        b = _codes_to_arr_nj(codes[i], la, lb)
        ra, rb, s = relabel_key_nj(a, b, perms, out, work)
        same = 1
        if ra != la or rb != lb:
            same = 0
        else:
            for t in range(la + lb):
                if out[t] != codes[i, t]:
                    same = 0
                    break
        for t in range(ra + rb):
            kbuf[count, t] = out[t]
        klens[count, 0] = ra
        klens[count, 1] = rb
        moves[count, 0] = moves[i, 0]
        moves[count, 1] = moves[i, 1]
        moves[count, 2] = moves[i, 2]
        moves[count, 3] = moves[i, 3]
        sigmas[count] = s
        raw_same[count] = same
        count += 1
    return kbuf, klens, moves, sigmas, raw_same, count


def relabel_canon(r1s, r2s, cap):
    """String pair -> (codes bytes, la, lb) in relabel-canonical form."""
    a = reduce_relator_nj(str_to_arr(r1s), True)
    b = reduce_relator_nj(str_to_arr(r2s), True)
    c1, c2 = canonical_pair_nj(a, b)
    out = np.empty(2 * cap, dtype=np.uint8)
    work = np.empty(2 * cap, dtype=np.uint8)
    la, lb, _ = relabel_key_nj(c1, c2, PERMS, out, work)
    return bytes(out[:la + lb]), la, lb


def decode(kb, la, lb):
    s = "".join(CODE_TO_CHAR[c] for c in kb)
    return s[:la], s[la:la + lb]


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return None
        self.p[rb] = ra
        return ra, rb


def multi_source_search(sources, nodes_per_source, max_total, seam_only=False,
                        cap=None, progress=None, max_states=6_000_000, stop_when_merged=False):
    """``sources``: list of (name, r1, r2). Returns (dsu, merges, states, stats).

    ``merges``: list of dicts, each a *proof obligation* carrying everything the independent
    verifier needs -- the two source names, the shared relabel key, and both paths as lists of
    ``(target, jsign, k1, k2, sigma)`` steps from the respective roots.
    """
    cap = cap or max_total
    S = len(sources)
    dsu = DSU(S)

    # state store
    key_of = {}                  # relabel-key bytes -> state id
    st_key, st_la, st_lb = [], [], []
    st_owner, st_parent, st_move, st_sigma, st_total = [], [], [], [], []

    heaps = {}                   # dsu root -> heap of (total, state_id)
    budget = {}                  # dsu root -> remaining node budget
    merges = []

    def add_state(kb, la, lb, owner, parent, move, sigma):
        sid = len(st_key)
        st_key.append(kb)
        st_la.append(la)
        st_lb.append(lb)
        st_owner.append(owner)
        st_parent.append(parent)
        st_move.append(move)
        st_sigma.append(sigma)
        st_total.append(la + lb)
        key_of[kb] = sid
        return sid

    for s, (name, r1, r2) in enumerate(sources):
        kb, la, lb = relabel_canon(r1, r2, cap)
        if kb in key_of:                       # two roots identical after relabeling
            other = st_owner[key_of[kb]]
            u = dsu.union(other, s)
            if u:
                merges.append({"kind": "aca", "a": sources[other][0], "b": name,
                               "at": decode(*_kv(st_key, st_la, st_lb, key_of[kb])),
                               "path_a": [], "path_b": [], "note": "roots coincide"})
            continue
        sid = add_state(kb, la, lb, s, -1, None, None)
        heaps[s] = [(la + lb, sid)]
        budget[s] = nodes_per_source

    def path_to(sid):
        out = []
        while st_parent[sid] >= 0:
            out.append(tuple(st_move[sid]) + (int(st_sigma[sid]),))
            sid = st_parent[sid]
        out.reverse()
        return out, sid

    popped = 0
    capped = False
    while True:
        if capped:
            break
        roots = [r for r in list(heaps) if dsu.find(r) == r and heaps[r] and budget[r] > 0]
        if not roots:
            break
        if stop_when_merged and len({dsu.find(i) for i in range(S)}) == 1:
            break
        for r in roots:
            if len(st_key) >= max_states:
                capped = True
                break
            if dsu.find(r) != r or not heaps[r] or budget[r] <= 0:
                continue
            _, sid = heapq.heappop(heaps[r])
            budget[r] -= 1
            popped += 1
            if progress and popped % 20000 == 0:
                progress(popped, len(st_key), sum(1 for i in range(S) if dsu.find(i) == i))

            r1s, r2s = decode(st_key[sid], st_la[sid], st_lb[sid])
            a = str_to_arr(r1s)
            b = str_to_arr(r2s)
            kbuf, klens, moves, sigmas, raw_same, n = expand_relabel_nj(
                a, b, cap, True, seam_only, PERMS, max_total)

            for i in range(n):
                la, lb = int(klens[i, 0]), int(klens[i, 1])
                kb = bytes(kbuf[i, :la + lb])
                mv = (int(moves[i, 0]), int(moves[i, 1]), int(moves[i, 2]), int(moves[i, 3]))
                if kb in key_of:
                    osid = key_of[kb]
                    oroot = dsu.find(st_owner[osid])
                    if oroot != dsu.find(r):
                        pa, ra = path_to(sid)
                        pa.append(mv + (int(sigmas[i]),))
                        pb, rb = path_to(osid)
                        kind = "ac" if (int(raw_same[i]) == 1 and _pure(pa) and _pure(pb)) \
                            else "aca"
                        merges.append({
                            "kind": kind,
                            "a": sources[st_owner[ra]][0], "b": sources[st_owner[rb]][0],
                            "at": decode(kb, la, lb),
                            "path_a": pa, "path_b": pb,
                        })
                        u = dsu.union(oroot, dsu.find(r))
                        if u:
                            keep, gone = u
                            if heaps.get(gone):
                                for it in heaps[gone]:
                                    heapq.heappush(heaps.setdefault(keep, []), it)
                                heaps[gone] = []
                            budget[keep] = budget.get(keep, 0) + budget.get(gone, 0)
                            budget[gone] = 0
                    continue
                nsid = add_state(kb, la, lb, st_owner[sid], sid, mv, int(sigmas[i]))
                heapq.heappush(heaps[dsu.find(r)], (la + lb, nsid))

    comps = len({dsu.find(i) for i in range(S)})
    stats = {"popped": popped, "states": len(st_key), "components": comps, "capped": capped}
    states = (st_key, st_la, st_lb, st_owner)
    return dsu, merges, states, stats


def _kv(st_key, st_la, st_lb, sid):
    return st_key[sid], st_la[sid], st_lb[sid]


def _pure(path):
    """True if no step needed a non-identity relabeling -- i.e. the path is a raw AC path."""
    from experiments.equivalence_classes.relabel import IDENTITY_PERM
    return all(step[4] == IDENTITY_PERM for step in path)
