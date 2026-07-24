"""A parameterized heap ordering, and the harness that scores one against the baseline.

``hsearch.py`` shipped nine hand-written orderings plus an endgame family. This module replaces
the hand-writing with a **config**: a list of length-keyed segments, each carrying a weight vector
over state features. Everything ``hsearch.py`` shipped is a point in this space -- ``length`` is
one segment with ``{"L": 1}``, ``knots_first`` is ``{"K": 1e6, "L": 1}``, and
``knots_first@endgame16`` is two segments -- so a tuner searching here can always return an
ordering already known to work, and can always return the baseline.

Three design constraints, each of which cost something to learn:

**The priority must be a pure function of the state.** The visited set dedups canonical states on
first discovery and there is no decrease-key, so a state's priority is fixed by whichever path
reached it first. Under a non-length ordering that path is not the shortest one, so any term
reading ``depth`` -- or reading the parent, e.g. "did this move drop a knot?" -- makes the pop
order depend on discovery order and stop being reproducible. The user's knot insight is already
carried by the *absolute* knot count: a state that bought a knot reduction sorts above one that
did not, without anything path-dependent entering the key.

**"Dynamic by depth and length" therefore means length.** A segment boundary switches the entire
weight vector when the state crosses a total-length threshold, which is how a search can climb
aggressively while the presentation is long and revert to pure length once it is short. The
leading segment index in the key makes every short state outrank every long one, and also keeps
the key heap-comparable when segments return different shapes.

**Features are computed once per state, in one pass.** ``feats()`` in ``hsearch.py`` returns four;
this returns thirteen from a single traversal, cached on the word. Measured cost: a 13-feature
weighted config runs within noise of pure length (515 vs 529 ms/presentation at budget 1,000), so
the ordering layer is free and the search trajectory is the only thing that moves the clock.
"""
import heapq
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _repo_root():
    d = _HERE
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

BENCH66 = os.path.join(ROOT, "results", "benchmark", "combined",
                       "benchmark_combined_66.json")
LOGS = os.path.join(ROOT, "tests", "heuristic_search", "logs")

INF = float("inf")

# ---------------------------------------------------------------------------------- features
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
)
_FIDX = {f: i for i, f in enumerate(FEATURES)}
N_FEAT = len(FEATURES)

_WORD_CACHE = {}


def word_stats(word):
    """(length, n_x_blocks, n_y_blocks, x_run_lengths, y_run_lengths, n_x_letters) -- CYCLIC.

    Cached on the word: states recur constantly across a search and across configs, and the same
    relator string is re-scored every time it appears in any pair.
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


_STATE_CACHE = {}


def phi(r1, r2):
    """The feature vector, as a plain tuple ordered like ``FEATURES``."""
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
    if not xs or not ys:
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
    )
    _STATE_CACHE[(r1, r2)] = out
    return out


# ------------------------------------------------------------------------------------- configs
#
# A config is {"segments": [{"upto": <total length ceiling>, "w": {feature: weight}}, ...]}.
# Segments are tried in order and the FIRST whose ``upto`` covers the state's total length wins;
# the last segment should have ``upto: null`` (read as +inf) or nothing will match a long state.
#
# The key is ``(segment_index, score)``. The leading index is load-bearing twice over: it makes
# every state in an earlier (shorter) segment outrank every state in a later one -- which is the
# whole point of an endgame threshold -- and it keeps two segments' scores from ever being
# compared against each other, so their weight vectors need not be on a common scale.

BASELINE_CONFIG = {"segments": [{"upto": None, "w": {"L": 1.0}}]}


def make_priority(cfg):
    """Compile a config into the ``(r1, r2) -> key`` callable the solver pushes with."""
    segs = []
    for s in cfg["segments"]:
        upto = INF if s.get("upto") is None else float(s["upto"])
        pairs = tuple((_FIDX[k], float(v)) for k, v in s["w"].items() if v)
        segs.append((upto, pairs))
    segs = tuple(segs)
    n_seg = len(segs)

    def p(r1, r2):
        f = phi(r1, r2)
        L = f[0]
        for i in range(n_seg):
            upto, pairs = segs[i]
            if L <= upto:
                sc = 0.0
                for idx, wt in pairs:
                    sc += wt * f[idx]
                return (i, sc)
        # No segment covered it: fall through to pure length in a final bucket of its own.
        return (n_seg, L)
    return p


def cfg_name(cfg):
    """A short stable label. Used as the config id in logs, so it must not depend on dict order."""
    parts = []
    for s in cfg["segments"]:
        w = "+".join(f"{k}{v:g}" for k, v in sorted(s["w"].items()) if v)
        parts.append(f"[<={'inf' if s.get('upto') is None else s['upto']:}]{w or '0'}")
    return "".join(parts)


# -------------------------------------------------------------------------------------- solver

class LabSolver(GreedyBaselineSolver):
    """The baseline search with the heap key swapped for ``self.priority``, plus min-total tracking.

    ``solve`` is re-stated rather than patched because the priority is computed inline in the base
    loop and the base file is read-only. Every other line is the parent's -- the move generator,
    the reduction, the canonicalisation, the cap test and the ``(key, depth, state)`` push shape
    with its depth tie-break. So a difference between two runs here is the ordering and nothing
    else.

    ``min_total`` is the shortest total length discovered anywhere in the search. That is this
    repo's ``min_relator_length`` (``greedy_baseline.py:931`` sums the pair), and it is the only
    progress signal the genuinely-unsolved presentations can produce at a budget where nothing
    solves.

    ``max_pop_relator`` is the longest single relator ever **popped**. It exists to make the cap
    question answerable rather than inferential: ``max_relator_length`` can only matter if some
    state actually reaches it, so an ordering whose ``max_pop_relator`` sits far below the cap is
    one for which the cap provably cannot bind, at any cap above that value.
    """

    def __init__(self, r1, r2, priority, **kw):
        super().__init__(r1, r2, **kw)
        self.priority = priority
        self.min_total = None
        self.max_pop_relator = 0

    def solve(self, progress=None):
        init_key = state_to_key(self.initial_state)
        heapq.heappush(self.pq, (self.priority(*init_key), 0, init_key))
        self.visited[init_key] = None
        self.move_in[init_key] = None
        self.min_total = len(init_key[0]) + len(init_key[1])
        nodes = 0

        while self.pq and nodes < self.max_nodes:
            _, depth, key = heapq.heappop(self.pq)
            nodes += 1
            r1, r2 = self._key_to_state(key)
            lr = len(r1) if len(r1) > len(r2) else len(r2)
            if lr > self.max_pop_relator:
                self.max_pop_relator = lr

            if len(r1) == 1 and len(r2) == 1:
                path, sk = [], key
                while sk is not None:
                    path.append(sk)
                    sk = self.visited[sk]
                return list(reversed(path)), nodes

            for nr1, nr2, target, jsign, k1, k2 in get_neighbors_with_moves_nj(r1, r2):
                a = reduce_relator_nj(nr1, self.cyclic_reduce)
                b = reduce_relator_nj(nr2, self.cyclic_reduce)
                if len(a) <= self.max_relator_length and len(b) <= self.max_relator_length:
                    ca, cb = canonical_pair_nj(a, b)
                    key_new = state_to_key((ca, cb))
                    if key_new not in self.visited:
                        self.visited[key_new] = key
                        t = len(key_new[0]) + len(key_new[1])
                        if t < self.min_total:
                            self.min_total = t
                        heapq.heappush(self.pq, (self.priority(*key_new), depth + 1, key_new))
        return None, nodes


def run_one(r1, r2, budget, priority, mrl):
    s = LabSolver(r1, r2, priority, max_nodes=budget, max_relator_length=mrl,
                  cyclic_reduce=True)
    path, nodes = s.solve()
    return {"solved": path is not None, "nodes": nodes,
            "path_length": (len(path) - 1) if path else None,
            "min_total": s.min_total, "max_pop": s.max_pop_relator}


# ------------------------------------------------------------------------------------ benchmark

def bench66():
    """The 66-row combined benchmark: 60 solved ladder rows + 6 genuinely-unsolved reach rows."""
    with open(BENCH66) as f:
        return json.load(f)["rows"]


def load_split(name):
    """One frozen slice by name. The split file is written once and never regenerated."""
    with open(os.path.join(LOGS, "splits.json")) as f:
        sp = json.load(f)
    by = {r["name"]: r for r in bench66()}
    return [by[n] for n in sp[name]]
