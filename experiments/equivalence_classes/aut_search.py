"""The ACA search: BFS over **Aut(F2)-classes**, not over raw presentations.

Why not a raw AC search
-----------------------
A raw AC search is hopeless at any local budget. Measured on the one merge we already knew
(`19_52 = 18_9`, found by the 1M-node sweep): the *complete* AC-ball of both roots at total
length <= 28 is 8,923 states and they do not meet; ball size grows ~5x per +2 of the cap. So the
AC path between them climbs above total length 30 from roots of length 18 and 19, and a
length-ordered BFS must enumerate everything below the hump before it can cross.

But raw length is the wrong ruler. A state of raw length 34 can be one change of variables away
from a state of length 16. Measure the hump in **Aut-minimal** length and the same two roots
merge in **8 pops**.

The graph
---------
Node   = an Aut(F2)-class, keyed by its Whitehead canonical form (a *complete* invariant of the
         orbit, so the key is exact), which is itself an Aut-minimal presentation.
Edge   = [P] -> [Q] when an AC move carries the Aut-minimal representative of [P] into [Q].
Weight = Aut-minimal total length. This is the priority, and it is what keeps the ball small.

Soundness
---------
Each edge is "a change of variables, then an AC move". Both preserve AC-triviality
(`P` is AC-trivial <=> `phi(P)` is AC-trivial), so connectivity here is exactly **ACA**-
equivalence: the two roots are *the same problem* -- solving one settles the other. It is NOT a
claim that an AC path exists between them; that stronger claim is made only where a merge is
witnessed at identical raw states, and it is tagged ``ac``.

Incompleteness (stated, never hidden)
-------------------------------------
Only ONE representative per Aut-class is expanded. `children(phi(P))` is not `phi(children(P))`
for general `phi` -- the moves conjugate by rotations, and `phi` changes lengths, hence changes
which rotations exist -- so expanding one representative yields a SUBSET of the class's true
out-edges. Every edge found is real; some are missed.

**Every merge found is a proof. No merge found proves nothing.**
"""
import heapq

from experiments.equivalence_classes.acmoves import canon, children
from experiments.equivalence_classes.aca_search import DSU
from experiments.equivalence_classes.autcanon import ID, compose, level_min, peak_reduce
from experiments.equivalence_classes.words import canon_pair

# Two memos, because the two phases have very different costs and very different hit rates.
#   phase 1 (peak reduction)  ~0.18 ms, keyed by the raw pair
#   phase 2 (level-set BFS)   ~5 ms,    keyed by the PEAK-REDUCED pair
# Many distinct raw states peak-reduce to the same minimal pair, so phase 2 is hit far more
# often than phase 1 -- which is exactly what makes the sweep affordable.
#
# The peak-reduced key on its own is NOT a valid Aut key: on the 261 roots it yields 259
# classes where the true count is 168, i.e. peak reduction is not confluent. Phase 2 is what
# makes the invariant complete, and it cannot be skipped.
_MEMO1 = {}
_MEMO2 = {}


def memo_stats():
    return {"phase1": len(_MEMO1), "phase2": len(_MEMO2)}


def aut_key(pair, max_total=None):
    """(total, rep, phi) with canon(phi(pair)) == rep.

    ``max_total`` is the phase-1 pre-filter: peak reduction alone gives the Aut-minimal LENGTH
    cheaply, so children over the cap are dropped without ever paying for phase 2. They come
    back as ``(total, None, None)``.
    """
    v = _MEMO1.get(pair)
    if v is None:
        v = peak_reduce(pair)
        _MEMO1[pair] = v
    t, red, phi1 = v
    if max_total is not None and t > max_total:
        return (t, None, None)

    rkey = canon_pair(*red)
    w = _MEMO2.get(rkey)
    if w is None:
        w = level_min(red, dict(ID))
        _MEMO2[rkey] = w
    rep, psi = w
    return (t, rep, compose(psi, phi1))


def aut_multi_search(sources, nodes_per_source, max_total, seam_only=False, move_cap=48,
                     max_states=1_500_000, progress=None, stop_when_merged=False,
                     time_limit=None, pre_union=()):
    """``sources``: list of (name, r1, r2). Returns (dsu, merges, stats).

    Each merge carries two paths, root -> shared Aut-class. A path step is
    ``(move, phi, rep)``: apply the Definition 2.1 ``move`` to the current representative,
    then the automorphism ``phi``, canonicalise, and you land on ``rep``. Both are replayable
    by ``verify_certificates.py`` with pure word substitution.
    """
    S = len(sources)
    dsu = DSU(S)

    key_of = {}
    st_rep, st_owner, st_parent, st_step = [], [], [], []
    heaps, budget = {}, {}
    merges = []

    def add(rep, owner, parent, step):
        sid = len(st_rep)
        st_rep.append(rep)
        st_owner.append(owner)
        st_parent.append(parent)
        st_step.append(step)
        key_of[rep] = sid
        return sid

    roots_of = {}
    for s, (name, r1, r2) in enumerate(sources):
        p = canon(r1, r2)
        t, rep, phi = aut_key(p)
        roots_of[s] = (p, rep, phi)
        if rep in key_of:
            other = st_owner[key_of[rep]]
            if dsu.union(other, s):
                merges.append({"kind": "aut", "a": sources[other][0], "b": name,
                               "at": rep, "path_a": [], "path_b": []})
            continue
        sid = add(rep, s, -1, None)
        heaps[s] = [(t, sid)]
        budget[s] = nodes_per_source

    def _merge_components(keep, gone):
        for it in heaps.get(gone, []):
            heapq.heappush(heaps.setdefault(keep, []), it)
        heaps[gone] = []
        budget[keep] = budget.get(keep, 0) + budget.get(gone, 0)
        budget[gone] = 0

    # Sources whose AC-equivalence is already established OUTSIDE this search (a state the
    # 1M-node sweep recorded is, by construction, reachable from its row's root by AC moves).
    # Unioning them up front is free reach, not an assumption.
    for a, b in pre_union:
        u = dsu.union(a, b)
        if u:
            _merge_components(*u)

    def path_to(sid):
        out = []
        while st_parent[sid] >= 0:
            out.append(st_step[sid])
            sid = st_parent[sid]
        out.reverse()
        return out, sid

    import time as _time
    t_start = _time.time()
    popped = 0
    capped = False
    timed_out = False
    while not capped and not timed_out:
        live = [r for r in list(heaps) if dsu.find(r) == r and heaps[r] and budget[r] > 0]
        if not live:
            break
        if stop_when_merged and len({dsu.find(i) for i in range(S)}) == 1:
            break
        for r in live:
            if time_limit and _time.time() - t_start > time_limit:
                timed_out = True
                break
            if len(st_rep) >= max_states:
                capped = True
                break
            if dsu.find(r) != r or not heaps[r] or budget[r] <= 0:
                continue
            _, sid = heapq.heappop(heaps[r])
            budget[r] -= 1
            popped += 1
            if progress and popped % 5000 == 0:
                progress(popped, len(st_rep), len({dsu.find(i) for i in range(S)}))

            rep = st_rep[sid]
            for child, mv in children(rep[0], rep[1], cap=move_cap,
                                      seam_only=seam_only).items():
                t, crep, phi = aut_key(child, max_total)
                if crep is None:          # over the Aut-minimal length cap
                    continue
                step = (mv, phi, crep)
                if crep in key_of:
                    osid = key_of[crep]
                    oroot = dsu.find(st_owner[osid])
                    if oroot != dsu.find(r):
                        pa, ra = path_to(sid)
                        pa = pa + [step]
                        pb, rb = path_to(osid)
                        merges.append({
                            "kind": "aca",
                            "a": sources[st_owner[ra]][0], "b": sources[st_owner[rb]][0],
                            "at": crep, "path_a": pa, "path_b": pb,
                        })
                        u = dsu.union(oroot, dsu.find(r))
                        if u:
                            _merge_components(*u)
                    continue
                nsid = add(crep, st_owner[sid], sid, step)
                heapq.heappush(heaps[dsu.find(r)], (t, nsid))

    stats = {"popped": popped, "states": len(st_rep), "capped": capped,
             "timed_out": timed_out, "seconds": round(_time.time() - t_start, 1),
             "components": len({dsu.find(i) for i in range(S)})}
    return dsu, merges, stats, roots_of
