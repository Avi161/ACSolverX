"""Block/knot heap ordering for the greedy substitution search.

The baseline (``greedy_baseline.greedy_search``) orders its open set by **total length alone**. This
module changes *only that expression* and holds everything else fixed — the move generator, the
reduction, the canonicalisation, the per-relator cap, the visited set and the ``(priority, depth,
key)`` tie-break are the baseline's, reached by subclassing rather than by copying. So a difference
between two runs is attributable to the ordering and to nothing else.

    from experiments.search.heuristics import greedy_search_h, RECOMMENDED

    stats = greedy_search_h(r1, r2, node_budget=10**5, max_relator_length=24,
                            config=RECOMMENDED)      # config=None => the baseline, exactly

``greedy_search_h`` returns **exactly** the dict ``greedy_baseline.greedy_search`` returns — same
keys, same order, same types — so a caller switches ordering by passing one argument and touches
nothing downstream. ``phi`` exposes the feature vector and ``make_priority`` compiles a config into
the callable the heap pushes with. ``HEURISTICS.md``, beside this file, documents every feature.

Two invariants, both pinned in ``tests/test_greedy_heuristic.py``:

  * ``config=None`` (equivalently ``BASELINE_CONFIG``) must reproduce the baseline **exactly** —
    same solved flag *and* same ``nodes_explored`` on every presentation. A control that merely
    scores the same is not the same; it has to be the same search.
  * **The priority must be a pure function of the state.** The visited set dedups on first discovery
    and there is no decrease-key, so a state's priority is fixed by whichever path reached it first.
    Any term reading ``depth`` — or the parent, e.g. "did this move drop a knot?" — would make pop
    order depend on discovery order and stop being reproducible. A knot *reduction* is already
    carried by the absolute knot count.
"""
import heapq

from experiments.search.greedy_baseline import (
    _HB_CHECK_EVERY, GreedyBaselineSolver, arr_to_str, canonical_pair_nj,
    get_neighbors_with_moves_nj, move_to_str, reduce_relator_nj, state_to_key,
)

INF = float("inf")

# ------------------------------------------------------------------------------------- features
#
# Every feature is rotation-invariant and reads the relator as a ring. A feature that could see
# where the canonicaliser cut the word would be measuring the tie-break, not the presentation.

FEATURES = (
    "L",        # total length -- the baseline's entire ordering
    "Lmin",     # length of the shorter relator
    "Lmax",     # length of the longer relator
    "imbal",    # Lmax - Lmin; a lopsided pair has one relator doing all the work
    "K",        # knot sum: knots(r1) + knots(r2)
    "MK",       # max knots over the two relators
    "mK",       # min knots -- nonzero means BOTH relators are mixed words
    "S",        # smaller mean block: mean run length of the thinner generator
    "Bmax",     # larger mean block
    "B1",       # number of length-1 blocks (isolated letters -- the thin spots)
    "Bmin",     # shortest block anywhere in the pair
    "nb",       # total number of blocks across both relators
    "xyimb",    # |#x letters - #y letters| / L; generator imbalance, scale-free
    "Bmaxrun",  # LONGEST single block anywhere -- Bmax is the larger *mean*, which hides a spike
    "Bspread",  # longest block - shortest block; how uneven the blocking is
    "ratio",    # Lmin / Lmax; imbalance as a ratio, where imbal is the raw difference
    "density",  # blocks per letter (nb / L); how finely the pair alternates, scale-free
)
_FIDX = {f: i for i, f in enumerate(FEATURES)}
N_FEAT = len(FEATURES)

_WORD_CACHE = {}
_STATE_CACHE = {}


def word_stats(word):
    """``(length, n_x_blocks, n_y_blocks, x_run_lengths, y_run_lengths, n_x_letters)`` — CYCLIC.

    Cyclic because the ring has no first letter: a word ending in the generator it starts with
    closes one block across the seam, and counting it as two would let the priority read the
    canonicaliser's rotation instead of the presentation. A letter and its inverse are the same
    generator here (``x`` and ``X`` do not start a new block) — a block is a run of one *generator*.

    Cached on the word: states recur constantly across a search, and the same relator string is
    re-scored every time it appears in any pair.
    """
    hit = _WORD_CACHE.get(word)
    if hit is not None:
        return hit
    n = len(word)
    if n == 0:
        out = (0, 0, 0, (), (), 0)
        _WORD_CACHE[word] = out
        return out
    g = [c in "xX" for c in word]
    runs, i = [], 0
    while i < n:
        j = i
        while j + 1 < n and g[j + 1] == g[i]:
            j += 1
        runs.append((g[i], j - i + 1))
        i = j + 1
    # Close the seam: a run wrapping the ring was counted twice, once at each end.
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        runs[0] = (runs[0][0], runs[0][1] + runs[-1][1])
        runs.pop()
    xr = tuple(k for is_x, k in runs if is_x)
    yr = tuple(k for is_x, k in runs if not is_x)
    out = (n, len(xr), len(yr), xr, yr, sum(xr))
    _WORD_CACHE[word] = out
    return out


def phi(r1, r2):
    """The feature vector for a state, as a plain tuple ordered like ``FEATURES``.

    Computed in one pass over the two words and cached on the pair — a 17-feature weighted config
    runs within noise of pure length, so the ordering layer is free and the search trajectory is the
    only thing that moves the clock.
    """
    hit = _STATE_CACHE.get((r1, r2))
    if hit is not None:
        return hit
    n1, x1, y1, xr1, yr1, nx1 = word_stats(r1)
    n2, x2, y2, xr2, yr2, nx2 = word_stats(r2)

    # A pure power has no knots: one generator simply does not appear.
    k1 = 0 if (x1 == 0 or y1 == 0) else max(x1, y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else max(x2, y2)

    xs, ys = xr1 + xr2, yr1 + yr2
    mx = sum(xs) / len(xs) if xs else 0.0
    my = sum(ys) / len(ys) if ys else 0.0
    if not xs or not ys:              # one generator absent: no "thinner" one to compare against
        smb, bmax = (mx or my), (mx or my)
    else:
        smb, bmax = min(mx, my), max(mx, my)

    allb = xs + ys
    L = n1 + n2
    out = (
        float(L),
        float(min(n1, n2)),
        float(max(n1, n2)),
        float(abs(n1 - n2)),
        float(k1 + k2),
        float(max(k1, k2)),
        float(min(k1, k2)),
        smb,
        bmax,
        float(sum(1 for b in allb if b == 1)),
        float(min(allb)) if allb else 0.0,
        float(len(allb)),
        (abs((nx1 + nx2) - (L - nx1 - nx2)) / L) if L else 0.0,
        float(max(allb)) if allb else 0.0,
        float(max(allb) - min(allb)) if allb else 0.0,
        (min(n1, n2) / max(n1, n2)) if max(n1, n2) else 0.0,
        (len(allb) / L) if L else 0.0,
    )
    _STATE_CACHE[(r1, r2)] = out
    return out


# -------------------------------------------------------------------------------------- configs
#
# A config is {"segments": [{"upto": <total length ceiling>, "w": {feature: weight}}, ...]}.
# Segments are tried in order and the FIRST whose ``upto`` covers the state's total length wins; the
# last one should carry ``"upto": None`` (read as +inf) or nothing will match a long state.
#
# ONE segment is a single linear ordering, which is what both configs below use. Two or more switch
# weight vectors at a length boundary — the "endgame" shape — and the schema keeps that door open
# because the research harness this was ported from speaks the same format.

BASELINE_CONFIG = {"segments": [{"upto": None, "w": {"L": 1.0}}]}

# The shipped ordering. One segment, no boundary, five of the seventeen features:
#
#     priority(r1, r2) = L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb
#
# i.e. total length, plus penalties for knot sum, worst-relator knots, smaller mean block and
# generator imbalance. Lower pops first, so every term above pushes a state DOWN the queue: a state
# is preferred for being short, for being less tangled, and for using its two generators evenly.
# The weights were tuned jointly, not one at a time — S is the weakest single ordering of the five
# and carries the largest weight here, so a one-at-a-time search would have discarded it.
RECOMMENDED = {"segments": [
    {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]}

# The research branch's block-ordering arm ``s20_mk2`` (L + 20*S + 2*MK), ported verbatim from
# cursor/heur-u124-s20mk2-a42e `runners/run_ac19_autmin_scale.py` so the benchmark in
# ``bench_new_moves.py`` can score the exact arm those campaigns named. Same feature definitions
# (``S`` smaller mean block, ``MK`` max knots); only the weight vector differs from RECOMMENDED.
S20_MK2 = {"segments": [
    {"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]}


def make_priority(config=None):
    """Compile a config into the ``(r1, r2) -> key`` callable the solver pushes with.

    ``config=None`` compiles the baseline, i.e. order by total length. The key is
    ``(segment_index, score)``: the leading index makes every state in an earlier (shorter) segment
    outrank every state in a later one — which is the whole point of an endgame boundary — and it
    keeps two segments' scores from ever being compared against each other, so their weight vectors
    need not be on a common scale.
    """
    cfg = config or BASELINE_CONFIG
    segs = []
    for s in cfg["segments"]:
        upto = INF if s.get("upto") is None else float(s["upto"])
        pairs = tuple((_FIDX[k], float(v)) for k, v in s["w"].items() if v)
        segs.append((upto, pairs))
    segs = tuple(segs)
    n_seg = len(segs)

    def priority(r1, r2):
        f = phi(r1, r2)
        L = f[0]
        for i in range(n_seg):
            upto, pairs = segs[i]
            if L <= upto:
                sc = 0.0
                for idx, wt in pairs:
                    sc += wt * f[idx]
                return (i, sc)
        # No segment covered it: fall through to pure length, in a bucket of its own.
        return (n_seg, L)
    return priority


# --------------------------------------------------------------------------------------- solver

class HeuristicSolver(GreedyBaselineSolver):
    """``GreedyBaselineSolver`` with the priority expression lifted out into ``self.priority``.

    ``solve`` is re-stated rather than patched because the priority is computed inline inside the
    base loop and ``greedy_baseline.py`` is read-only. Every other line is the parent's,
    deliberately — including the ``(priority, depth, key)`` push shape, whose depth tie-break is
    what keeps pops deterministic when two states share a priority, and the ``max_expanded_key``
    update, which happens on POP (before the trivial check), not on discovery.
    """

    def __init__(self, r1, r2, config=None, **kw):
        super().__init__(r1, r2, **kw)
        self.priority = make_priority(config)

    def solve(self, progress=None):
        init_key = state_to_key(self.initial_state)
        heapq.heappush(self.pq, (self.priority(*init_key), 0, init_key))
        self.visited[init_key] = None
        self.move_in[init_key] = None
        self.new_seen.add(init_key)
        nodes_visited = 0
        self.max_expanded_key = init_key

        while self.pq and nodes_visited < self.max_nodes:
            _, depth, key = heapq.heappop(self.pq)
            nodes_visited += 1
            if progress is not None and nodes_visited % _HB_CHECK_EVERY == 0:
                progress(nodes_visited)
            if len(key[0]) + len(key[1]) > \
                    len(self.max_expanded_key[0]) + len(self.max_expanded_key[1]):
                self.max_expanded_key = key
            r1, r2 = self._key_to_state(key)

            if len(r1) == 1 and len(r2) == 1:
                path, moves = [], []
                state_key = key
                while state_key is not None:
                    path.append(self._key_to_state(state_key))
                    mv = self.move_in[state_key]
                    if mv is not None:
                        moves.append(mv)
                    state_key = self.visited[state_key]
                path.reverse()
                moves.reverse()
                return path, moves, nodes_visited, self.new_seen

            for nr1, nr2, target, jsign, k1, k2 in get_neighbors_with_moves_nj(r1, r2):
                nr1r = reduce_relator_nj(nr1, self.cyclic_reduce)
                nr2r = reduce_relator_nj(nr2, self.cyclic_reduce)

                if len(nr1r) <= self.max_relator_length and \
                        len(nr2r) <= self.max_relator_length:
                    canon_r1, canon_r2 = canonical_pair_nj(nr1r, nr2r)
                    key_new = state_to_key((canon_r1, canon_r2))
                    if key_new not in self.visited:
                        self.visited[key_new] = key
                        self.move_in[key_new] = (int(target), int(jsign),
                                                 int(k1), int(k2))
                        self.new_seen.add(key_new)
                        heapq.heappush(self.pq,
                                       (self.priority(*key_new), depth + 1, key_new))

        return None, None, nodes_visited, self.new_seen


def greedy_search_h(r1_str, r2_str, node_budget, max_relator_length=24,
                    cyclic_reduce=True, config=None, progress=None):
    """``greedy_baseline.greedy_search`` with the heap ordering swapped. Same return dict.

    ``config=None`` orders by total length and IS the baseline search, pop for pop. Pass
    ``RECOMMENDED``, or any config of your own, to order by the heuristic.

    Returns the same eleven keys ``greedy_search`` returns — ``solved``, ``nodes_explored``,
    ``path_length``, ``min_relator_length``, ``min_relator``, ``max_relator_length``,
    ``max_relator``, ``max_relator_length_expanded``, ``max_relator_expanded``, ``path``,
    ``path_moves`` — so a caller switches orderings without touching anything downstream. ``path``
    is the list of ``[r1, r2]`` states and ``path_moves`` the parallel list of Definition 2.1 move
    strings that replays it via ``greedy_baseline.moves_to_states``; a certificate is stored as
    moves, never recovered by diffing consecutive states, because the move inverts the *other*
    relator.
    """
    solver = HeuristicSolver(
        r1_str, r2_str,
        config=config,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
    )
    path, moves, nodes_visited, new_seen = solver.solve(progress)

    # Shortest / longest presentation (by total length) DISCOVERED anywhere in the search.
    min_key = min(new_seen, key=lambda k: len(k[0]) + len(k[1]))
    max_key = max(new_seen, key=lambda k: len(k[0]) + len(k[1]))
    # Longest presentation actually popped/expanded (states we operated on).
    exp_key = solver.max_expanded_key

    solved = path is not None
    if solved:
        path_states = [[arr_to_str(a), arr_to_str(b)] for a, b in path]
        path_moves = [move_to_str(m) for m in moves]
        path_length = len(path_states) - 1
    else:
        path_states = []
        path_moves = []
        path_length = None

    return {
        "solved": solved,
        "nodes_explored": nodes_visited,
        "path_length": path_length,
        "min_relator_length": len(min_key[0]) + len(min_key[1]),
        "min_relator": [min_key[0], min_key[1]],
        "max_relator_length": len(max_key[0]) + len(max_key[1]),
        "max_relator": [max_key[0], max_key[1]],
        "max_relator_length_expanded": len(exp_key[0]) + len(exp_key[1]),
        "max_relator_expanded": [exp_key[0], exp_key[1]],
        "path": path_states,
        "path_moves": path_moves,
    }
