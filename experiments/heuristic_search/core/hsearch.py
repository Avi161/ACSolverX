"""Greedy substitution search with a pluggable heap priority.

The baseline orders its open set by total length alone (``greedy_baseline.py:397``). This module
changes **only that expression** and holds everything else fixed -- the move generator, the
reduction, the canonicalisation, the per-relator cap, the visited set, and the ``(priority, depth,
key)`` tie-break are the baseline's, reached by subclassing rather than by copying. So a difference
in solve rate between two runs here is attributable to the ordering and to nothing else.

The features come from the block analysis in ``experiments/clustering``: a relator is a cyclic word,
its **blocks** are the maximal runs of one generator read around the ring, and the two statistics
that separated solved from unsolved presentations were the **knot count** (how many blocks) and the
**smaller mean block** (how thick the thinner generator's runs are).

Two invariants this file is built around, both pinned in ``tests/heuristic_search/``:

  * ``PRIORITIES["length"]`` must reproduce the baseline **exactly** -- same solved set, same
    ``nodes_explored`` on every presentation. It is the control, and a control that merely scores
    the same is not the same; it has to be the same search. Nothing else here is interpretable
    until that holds.
  * A priority may return a tuple of any length, but the FIRST element must be an int wherever
    two differently-shaped tuples can meet, or Python compares an int against a tuple and raises
    mid-search. The endgame switch below is the case that matters.
"""
import heapq
import os
import sys


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.search.greedy_baseline import (                              # noqa: E402
    GreedyBaselineSolver, canonical_pair_nj, get_neighbors_with_moves_nj,
    reduce_relator_nj, state_to_key,
)

_HB = 1024


# ------------------------------------------------------------------------------- block features

_BLOCK_CACHE = {}


def blocks(word):
    """(x_run_lengths, y_run_lengths) read CYCLICALLY. Cached -- states recur constantly.

    Cyclic because the ring has no first letter: a word ending in the generator it starts with
    closes one block across the seam, and counting it as two would let the priority read the
    canonicaliser's rotation instead of the presentation.
    """
    hit = _BLOCK_CACHE.get(word)
    if hit is not None:
        return hit
    n = len(word)
    if n == 0:
        out = ((), ())
        _BLOCK_CACHE[word] = out
        return out
    g = [c in "xX" for c in word]
    runs, i = [], 0
    while i < n:
        j = i
        while j + 1 < n and g[j + 1] == g[i]:
            j += 1
        runs.append((g[i], j - i + 1))
        i = j + 1
    # Close the seam: a run that wraps was counted twice, once at each end.
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        runs[0] = (runs[0][0], runs[0][1] + runs[-1][1])
        runs.pop()
    out = (tuple(n_ for is_x, n_ in runs if is_x), tuple(n_ for is_x, n_ in runs if not is_x))
    _BLOCK_CACHE[word] = out
    return out


def feats(r1, r2):
    """(total_length, knot_sum, max_knots, smaller_mean_block) for a state."""
    x1, y1 = blocks(r1)
    x2, y2 = blocks(r2)
    k1 = 0 if not x1 or not y1 else max(len(x1), len(y1))
    k2 = 0 if not x2 or not y2 else max(len(x2), len(y2))
    xs, ys = x1 + x2, y1 + y2
    mx = sum(xs) / len(xs) if xs else 0.0
    my = sum(ys) / len(ys) if ys else 0.0
    if not xs or not ys:                      # one generator absent: no "thinner" one to compare
        smb = mx or my
    else:
        smb = min(mx, my)
    return len(r1) + len(r2), k1 + k2, max(k1, k2), smb


# ------------------------------------------------------------------------------------ priorities
#
# Each takes the two relator strings and returns a sortable key. Lower pops first.
#
# The ``*_first`` family is the user's "keep knots at the top of the queue": knot reduction is rare,
# so a state that achieved one should be expanded before any state that merely got shorter. Length
# stays as the second element, so within a knot level the search is exactly the baseline.
#
# The ``endgame`` family answers the objection that ordering by knots is wrong near the solution --
# the trivial state has 0 knots and length 2, and once a presentation is short the remaining work is
# cancellation, not restructuring. Below ``T`` it reverts to pure length. T is tuned, never guessed.

def p_length(r1, r2):
    return len(r1) + len(r2)


def p_knots_first(r1, r2):
    L, K, _, _ = feats(r1, r2)
    return (K, L)


def p_maxknots_first(r1, r2):
    L, _, MK, _ = feats(r1, r2)
    return (MK, L)


def p_smb_first(r1, r2):
    L, _, _, S = feats(r1, r2)
    return (round(S, 3), L)


def _mk_linear(field, a):
    def p(r1, r2):
        f = feats(r1, r2)
        return f[0] + a * f[field]
    return p


def _mk_endgame(inner, T):
    """Below total length ``T``, order by length alone; above it, by ``inner``.

    The leading 0/1 is what makes the two branches comparable: every endgame key is ``(0, L)`` and
    every opening key is ``(1, ...)``, so heapq never has to compare an int against a tuple.
    """
    def p(r1, r2):
        L = len(r1) + len(r2)
        if L <= T:
            return (0, L)
        k = inner(r1, r2)
        return (1,) + (k if isinstance(k, tuple) else (k,))
    return p


PRIORITIES = {
    "length": p_length,                                    # the control -- baseline, exactly
    "knots_first": p_knots_first,
    "maxknots_first": p_maxknots_first,
    "smb_first": p_smb_first,
    "length+1.0*knots": _mk_linear(1, 1.0),
    "length+2.0*knots": _mk_linear(1, 2.0),
    "length+4.0*knots": _mk_linear(1, 4.0),
    "length+2.0*smb": _mk_linear(3, 2.0),
    "length+4.0*smb": _mk_linear(3, 4.0),
}
for _T in (4, 6, 8, 10, 12, 14, 16, 20):
    PRIORITIES[f"knots_first@endgame{_T}"] = _mk_endgame(p_knots_first, _T)
    PRIORITIES[f"smb_first@endgame{_T}"] = _mk_endgame(p_smb_first, _T)


# --------------------------------------------------------------------------------------- solver

class HeuristicSolver(GreedyBaselineSolver):
    """``GreedyBaselineSolver`` with the priority expression lifted out into ``self.priority``.

    ``solve`` is re-stated rather than patched because the priority is computed inline inside the
    base loop and the base file is read-only. Every other line is the parent's, deliberately --
    including the ``(priority, depth, key)`` push shape, whose depth tie-break is what keeps pops
    deterministic when two states share a priority.
    """

    def __init__(self, r1, r2, priority=p_length, **kw):
        super().__init__(r1, r2, **kw)
        self.priority = priority

    def solve(self, progress=None):
        init_key = state_to_key(self.initial_state)
        heapq.heappush(self.pq, (self.priority(*init_key), 0, init_key))
        self.visited[init_key] = None
        self.move_in[init_key] = None
        nodes = 0

        while self.pq and nodes < self.max_nodes:
            _, depth, key = heapq.heappop(self.pq)
            nodes += 1
            if progress is not None and nodes % _HB == 0:
                progress(nodes)
            r1, r2 = self._key_to_state(key)

            if len(r1) == 1 and len(r2) == 1:
                path, sk = [], key
                while sk is not None:
                    path.append(sk)
                    sk = self.visited[sk]
                return list(reversed(path)), None, nodes, self.new_seen

            for nr1, nr2, target, jsign, k1, k2 in get_neighbors_with_moves_nj(r1, r2):
                a = reduce_relator_nj(nr1, self.cyclic_reduce)
                b = reduce_relator_nj(nr2, self.cyclic_reduce)
                if len(a) <= self.max_relator_length and len(b) <= self.max_relator_length:
                    ca, cb = canonical_pair_nj(a, b)
                    key_new = state_to_key((ca, cb))
                    if key_new not in self.visited:
                        self.visited[key_new] = key
                        heapq.heappush(self.pq,
                                       (self.priority(*key_new), depth + 1, key_new))
        return None, None, nodes, self.new_seen


def hsearch(r1, r2, node_budget, priority=p_length, max_relator_length=24, cyclic_reduce=True):
    """One presentation, one priority. Returns solved / nodes_explored / path_length."""
    s = HeuristicSolver(r1, r2, priority=priority, max_nodes=node_budget,
                        max_relator_length=max_relator_length, cyclic_reduce=cyclic_reduce)
    path, _, nodes, _ = s.solve()
    return {"solved": path is not None, "nodes_explored": nodes,
            "path_length": (len(path) - 1) if path else None}
