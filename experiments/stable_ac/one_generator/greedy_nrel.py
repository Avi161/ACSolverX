"""Phase 2 — n-relator GS-Sub greedy solver (int-encoded, generalizes the notebook).

Generalizes the 2-bool-relator search of ``greedy_search.ipynb`` /
``baseline_n2/greedy_ac.py`` from "2 relators of ``[bool,bool]`` letters" to "a tuple of
``n`` relators of **signed-int** letters" (x->1, y->2, z->3, inverses negative; one array
slot per letter). This is what runs the stabilized 3-generator ``z=w`` datasets.

Design (see PLAN.md "Phase 2"):
  * ``@njit`` stays at **single-relator** granularity (``rotate``/``reduce``/``inverse``/
    ``canonical`` each take ONE int array); the n-relator pairing loop is plain Python
    (numba falls to object mode on ragged tuples-of-arrays).
  * **Porting trap:** the notebook rolls by ``2*i`` because a letter is a 2-slot bool pair.
    Here one letter = one slot, so we roll by ``i`` (``np.roll(rel, i)``). Getting this wrong
    silently corrupts every neighbor/canonicalization — pre-flight test 1 pins it.
  * **Length cap = per-relator** (each relator < ``max_len``, same value every relator every
    arm), NOT a shared sum-cap: a sum-cap would let the long z-relator eat r1/r2's headroom, so
    the n=3 arm would search a strictly smaller (r1,r2) subspace than the n=2 baseline and any
    coverage delta would be a cap artifact. Per-relator makes the (r1,r2) subspace identical
    across baseline and arms by construction. Recorded per result line.
  * **Null-revert block:** ``blocked_states`` pre-seeds canonical keys that are never enqueued.
    For a ``z=w`` run pass the single state ``(r1, r2, [z])`` (z collapsed to z=1); every route
    that unwinds z lands on that one canonical key (canonical form is unique). A hit increments
    ``revert_hits`` (observable — the block does real work) instead of being silently dropped.
  * Every solve is **retraced, independently verified, and persisted** (n>=3 requirement): the
    step-by-step path (states + the move on each transition) is written to a sidecar so the
    solve is re-auditable/replayable/demonstrable offline, not just a run-time boolean.

Verification ladder: ``solved`` (reached trivial within budget) -> ``verify_path`` (independent
replay, recomputes neighbors from scratch — catches search bugs) -> [Phase 4] JAX ``check_paths``
gold gate (catches move-generation bugs; needs the generalized env ``s_move``, not available for
n=3 yet). A ``path_verified:false`` is never counted as a solve.
"""
import heapq
import json
import os
import time

import numpy as np
from numba import njit

L = 24  # per-relator length cap / padding (matches the env and ppo_ac_s.py)

INT_DTYPE = np.int64

# Canonical letter order = the ORIGINAL two-hump paper's (greedy_search.ipynb: find_minimal_rotation
# / lex_cmp_* docstrings state "Y < y < X < x"): group by generator with HIGHER generator-id first,
# and within a generator the inverse before the generator. Extended to the z generator this is
#     Z < z < Y < y < X < x   (ids: z=3 first, then y=2, then x=1; -g before +g).
# Any consistent order gives the same equivalence classes / solved set; this specific one matches the
# paper so node-counts / heap tie-breaks / canonical representatives reproduce the paper's search.
NGEN_MAX = 3


@njit(inline='always')
def _paper_lt(a, b):
    """True iff letter a < b in the paper's order Z<z<Y<y<X<x (see NGEN_MAX note)."""
    aa = a if a > 0 else -a
    bb = b if b > 0 else -b
    if aa != bb:
        return aa > bb          # higher |generator id| first  (z < y < x)
    return a < b                # same generator: inverse (-g) before generator (+g)


# ===================================================================================
# ==== single-relator primitives (njit; one int array in, one int array out)      ====
# ===================================================================================

@njit
def inverse_relator(rel):
    n = len(rel)
    out = np.empty(n, dtype=rel.dtype)
    for m in range(n):
        out[m] = -rel[n - 1 - m]
    return out


@njit
def reduce_relator(rel):
    """Free reduction (adjacent a,-a cancellation) then cyclic reduction (trim inverse ends).

    Stack-based; computes the unique freely+cyclically reduced word. Correct on full
    cancellation (returns an empty array) rather than reading past the end like the notebook's
    ``reduce_relator_nj`` — the two agree on every non-degenerate search state (asserted by the
    n=2 differential oracle)."""
    n = len(rel)
    if n == 0:
        return rel.copy()
    stack = np.empty(n, dtype=rel.dtype)
    top = 0
    for k in range(n):
        a = rel[k]
        if top > 0 and stack[top - 1] == -a:
            top -= 1
        else:
            stack[top] = a
            top += 1
    i = 0
    j = top - 1
    while i < j and stack[i] == -stack[j]:
        i += 1
        j -= 1
    return stack[i:j + 1].copy()


@njit
def find_minimal_rotation(rel):
    """Booth's algorithm — minimal rotation under the paper's letter order (see _paper_lt)."""
    n = len(rel)
    if n == 0:
        return rel.copy()
    arr = np.concatenate((rel, rel))
    f = np.full(2 * n, -1, dtype=np.int64)
    k = 0
    for j in range(1, 2 * n):
        i = f[j - k - 1]
        while i != -1 and arr[j] != arr[k + i + 1]:
            if _paper_lt(arr[j], arr[k + i + 1]):
                k = j - i - 1
            i = f[i]
        if i == -1 and arr[j] != arr[k]:
            if _paper_lt(arr[j], arr[k]):
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    return arr[k:k + n].copy()


@njit
def _lex_less(a, b):
    """True iff equal-length int array a < b lexicographically under the paper's letter order."""
    for m in range(len(a)):
        if a[m] != b[m]:
            return _paper_lt(a[m], b[m])
    return False


@njit
def canonical_relator(rel):
    """Inversion-invariant canonical form: min (by rotation and inverse) under the fixed order.

    A relator and any of its cyclic rotations or its inverse all map to the SAME array, so a
    single canonical key identifies the whole equivalence class (this is why one blocked state
    suffices for the null-revert)."""
    if len(rel) == 0:
        return rel.copy()
    r_min = find_minimal_rotation(rel)
    inv_min = find_minimal_rotation(inverse_relator(rel))
    if _lex_less(inv_min, r_min):
        return inv_min
    return r_min


def rotate(rel, i):
    """np.roll(rel, i) — shift right by i letters (one slot per letter; NOT 2*i). Plain helper
    so tests can pin the porting trap directly."""
    return np.roll(rel, i)


def _roll(a, k):
    """Fast right-cyclic shift by k (0<=k<len): equals np.roll(a, k) without numpy.roll's
    per-call axis-normalization overhead (the hot loop calls this ~100x/node)."""
    if k == 0:
        return a
    return np.concatenate((a[-k:], a[:-k]))


# ===================================================================================
# ==== state layer (plain Python: tuple of int arrays)                            ====
# ===================================================================================

# Letter <-> byte, byte-order == the paper's letter order Z<z<Y<y<X<x (see _paper_lt). Letters map
# to 1..2*NGEN_MAX (never 0, so 0 stays the relator separator); reversible for key_to_state.
_INT_TO_RANK_BYTE = {v: (NGEN_MAX - (v if v > 0 else -v)) * 2 + (1 if v > 0 else 0) + 1
                     for g in range(1, NGEN_MAX + 1) for v in (-g, g)}
_RANK_BYTE_TO_INT = {b: v for v, b in _INT_TO_RANK_BYTE.items()}


def _relator_bytes(r):
    """Encode a relator as compact bytes whose byte-order == the paper's letter order
    (Z<z<Y<y<X<x), so a bytes-compare == a paper-order lex-compare. Reversible (key_to_state)."""
    return bytes(_INT_TO_RANK_BYTE[int(x)] for x in r)


def _bskey(bs):
    return (len(bs), bs)


def canonical_tuple(state):
    """Canonicalize each relator, then sort by (len, lex) — order-independent. (Array form, used by
    verify_path / retrace / tests; the solver hot path keys via ``canonical_key`` instead.)"""
    canon = [canonical_relator(np.asarray(r, dtype=INT_DTYPE)) for r in state]
    canon.sort(key=lambda r: (len(r), _relator_bytes(r)))
    return tuple(canon)


def canonical_key(state):
    """Canonical bytes key in a single pass: canonicalize each relator, encode (+128), sort by
    (len, bytes), join by a 0 byte. Byte-for-byte equal to ``state_to_key(canonical_tuple(state))``
    but skips the array round-trip and the int-tuple sort key — this is what the solver keys on."""
    parts = [_relator_bytes(canonical_relator(np.asarray(r, dtype=INT_DTYPE))) for r in state]
    parts.sort(key=_bskey)
    return b"\x00".join(parts)


def state_to_key(state):
    """Reversible compact key. state must already be canonical. Letters +128 -> bytes
    (letters are +-1..+-n_gen, never 0), relators joined by a 0 byte."""
    return b"\x00".join(_relator_bytes(r) for r in state)


def key_to_state(key):
    return tuple(np.array([_RANK_BYTE_TO_INT[b] for b in part], dtype=INT_DTYPE)
                 for part in key.split(b"\x00"))


def is_trivial(state):
    return all(len(r) == 1 for r in state)


def flat_to_relators(flat, n_gen, half=L):
    """Env flat-int presentation (len n_gen*half, 0=pad) -> list of n_gen int arrays (zeros
    stripped; 0 is only ever padding)."""
    return [np.array([a for a in flat[g * half:(g + 1) * half] if a != 0], dtype=INT_DTYPE)
            for g in range(n_gen)]


def null_revert_state(flat, n_gen, half=L):
    """The single null-revert state for a z=w run: (r1, ..., r_{n-1}, [z]) — the original
    presentation with the z-relator collapsed to z=1. Pass to ``blocked_states``."""
    rels = flat_to_relators(flat, n_gen, half)
    z = n_gen
    return tuple(list(rels[:-1]) + [np.array([z], dtype=INT_DTYPE)])


# ===================================================================================
# ==== the substitution move (n-relator, plain Python)                            ====
# ===================================================================================

def get_neighbors(state, n_gen):
    """n-relator substitution neighbors — the exact generalization of the notebook's
    ``get_neighbors_nj``. For every UNORDERED pair {a,b} (a<b, leader = a), each candidate
    c in {r_b, r_b^-1}, and each cyclic rotation of r_a and c: if the boundary letters cancel,
    form the spliced word ``neighbour = reduce(concat(rot(r_a), rot(c)))`` and emit it into
    BOTH slot a (``r_a -> neighbour``) and slot b (``r_b -> neighbour``). At n=2 (single pair
    {0,1}, leader r1, both slots) this is byte-for-byte the notebook move set — the reference the
    differential oracle certifies against; the leader-only "ordered pair" reading does NOT match it.

    Boundary-letter fast-reject: read the last letter of rot(r_a,i) and the first of rot(c,j)
    by index arithmetic (no array materialization) and only build concat+reduce for the sparse
    cancelling pairs — the hot loop (n=3 has 3 pairs vs n=2's 1).

    Returns a list of (neighbor_state, move); move = (modified_index, ra_rot, c_rot, c_is_inverse)."""
    n = len(state)
    out = []
    for a in range(n):
        ra = state[a]
        la = len(ra)
        if la == 0:
            continue
        for b in range(a + 1, n):
            rb = state[b]
            for c_is_inv in (0, 1):
                c = rb if c_is_inv == 0 else inverse_relator(rb)
                lc = len(c)
                if lc == 0:
                    continue
                for i in range(la):
                    last = ra[(la - 1 - i) % la]          # last letter of np.roll(ra, i)
                    for j in range(lc):
                        first = c[(-j) % lc]               # first letter of np.roll(c, j)
                        if last == -first:                 # boundary cancels
                            neighbour = reduce_relator(np.concatenate((_roll(ra, i), _roll(c, j))))
                            if len(neighbour) == 0:
                                continue
                            sa = list(state)
                            sa[a] = neighbour
                            out.append((tuple(sa), (a, i, j, c_is_inv)))
                            sb = list(state)
                            sb[b] = neighbour
                            out.append((tuple(sb), (b, i, j, c_is_inv)))
    return out


# ===================================================================================
# ==== solver                                                                     ====
# ===================================================================================

class NRelatorSolver:
    """Best-first (GS default: total relator length) n-relator substitution search.

    ``blocked_states`` — states whose canonical key is pre-seeded as blocked (never enqueued);
    a generated neighbor matching one increments ``revert_hits`` (and, under ``track_reverts``,
    appends ``(parent_key, move)`` to ``revert_log``). ``track_seen`` gates the ``new_seen`` set
    (the minimal-element diagnostic) — off by default to save memory on the 1M runs.
    """

    def __init__(self, relators, n_gen, max_nodes=100_000, max_len=L,
                 blocked_states=None, track_reverts=False, track_seen=False):
        self.n_gen = n_gen
        self.max_nodes = max_nodes
        self.max_len = max_len
        self.track_reverts = track_reverts
        self.track_seen = track_seen
        self.blocked = set()
        if blocked_states:
            for st in blocked_states:
                self.blocked.add(canonical_key(st))
        self.initial_key = canonical_key(tuple(np.asarray(r, dtype=INT_DTYPE) for r in relators))
        self.visited = {}          # key -> parent_key (moves re-derived at retrace, to save memory)
        self.revert_hits = 0
        self.revert_log = []
        self.new_seen = set()
        self.min_total_len = None  # smallest total relator length reached (progress proxy; trivial=n_gen)
        self.min_total_state = None  # canonical key of the presentation achieving min_total_len

    def solve(self):
        pq = []
        init_key = self.initial_key
        init_len = sum(len(p) for p in init_key.split(b"\x00"))
        self.min_total_len = init_len
        self.min_total_state = init_key
        heapq.heappush(pq, (init_len, 0, init_key))
        self.visited[init_key] = None
        if self.track_seen:
            self.new_seen.add(init_key)
        visited, blocked, n_gen, max_len = self.visited, self.blocked, self.n_gen, self.max_len
        nodes = 0
        while pq and nodes < self.max_nodes:
            _, depth, key = heapq.heappop(pq)
            nodes += 1
            state = key_to_state(key)
            if all(len(r) == 1 for r in state):
                return self._retrace(key), nodes, self.new_seen
            byte_parts = key.split(b"\x00")            # parent's per-relator canonical bytes (sorted)
            for nbr_state, move in get_neighbors(state, n_gen):
                ci = move[0]                            # only relator ci changed; the rest stay canonical
                new_r = nbr_state[ci]
                if len(new_r) >= max_len:               # per-relator cap (only ci can have grown)
                    continue
                parts = list(byte_parts)                # incremental key: recompute only ci's bytes
                parts[ci] = _relator_bytes(canonical_relator(new_r))
                parts.sort(key=_bskey)
                nkey = b"\x00".join(parts)
                if nkey in blocked:
                    self.revert_hits += 1
                    if self.track_reverts:
                        self.revert_log.append((key, move))
                    continue
                if nkey not in visited:
                    visited[nkey] = key
                    if self.track_seen:
                        self.new_seen.add(nkey)
                    tl = sum(len(p) for p in parts)
                    if tl < self.min_total_len:
                        self.min_total_len = tl
                        self.min_total_state = nkey
                    heapq.heappush(pq, (tl, depth + 1, nkey))
        return None, nodes, self.new_seen

    def _retrace(self, key):
        """Walk the visited parent-dict back to the initial state, re-deriving each transition's
        move from get_neighbors(parent) (moves are not stored in visited, to save memory — retrace
        runs only on solved paths, which are short). Returns {states, moves, keys}: states[t] is the
        canonical state at step t; moves[t] is a move producing states[t] from states[t-1] (moves[0]
        is None, the root)."""
        keys = []
        k = key
        while k is not None:
            keys.append(k)
            k = self.visited[k]
        keys.reverse()
        states = [key_to_state(k) for k in keys]
        moves = [None]
        for t in range(1, len(states)):
            child = keys[t]
            mv = None
            for nbr, m in get_neighbors(states[t - 1], self.n_gen):
                if canonical_key(nbr) == child:
                    mv = m
                    break
            moves.append(mv)
        return {"states": states, "moves": moves, "keys": keys}


# ===================================================================================
# ==== independent verification + persistence                                     ====
# ===================================================================================

def verify_path(states, n_gen):
    """Replay a path independently of the search bookkeeping: for each consecutive pair recompute
    get_neighbors(states[t]) from scratch and require canonical(states[t+1]) is among them; require
    the final state trivial. Shares get_neighbors with the solver, so it catches search bugs but
    NOT a move-generation bug (that's the deferred JAX gold gate). ``path_verified:false`` is never
    counted as a solve."""
    if not states:
        return False
    for t in range(len(states) - 1):
        target = state_to_key(canonical_tuple(states[t + 1]))
        ok = False
        for nbr, _ in get_neighbors(states[t], n_gen):
            if any(len(r) == 0 for r in nbr):
                continue
            if state_to_key(canonical_tuple(nbr)) == target:
                ok = True
                break
        if not ok:
            return False
    return is_trivial(states[-1])


def serialize_path(path_obj, idx, name=None):
    """path object -> a JSON-serializable record whose ``states`` deserialize back into exactly
    the representation ``verify_path`` accepts (persist-loop closure)."""
    states = [[[int(x) for x in r] for r in st] for st in path_obj["states"]]
    moves = [list(m) if m is not None else None for m in path_obj["moves"]]
    return {"idx": idx, "name": name, "moves": moves, "states": states,
            "path_len": len(states) - 1}


def deserialize_states(record):
    return [tuple(np.array(r, dtype=INT_DTYPE) for r in st) for st in record["states"]]


def write_path_sidecar(path, record):
    """Append one path record to a JSONL sidecar (crash-safe: append + flush + fsync)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())


def path_max_len(states):
    return max(sum(len(r) for r in st) for st in states)


def solve_one(flat, n_gen, max_len=L, max_nodes=100_000, blocked_states=None,
              track_reverts=False, track_seen=False):
    """Run one flat-int presentation end-to-end. Returns (result_dict, path_obj); path_obj is None
    if unsolved. The caller persists path_obj via serialize_path + write_path_sidecar."""
    relators = flat_to_relators(flat, n_gen, half=L)
    solver = NRelatorSolver(relators, n_gen, max_nodes=max_nodes, max_len=max_len,
                            blocked_states=blocked_states, track_reverts=track_reverts,
                            track_seen=track_seen)
    t0 = time.time()
    path, nodes, _ = solver.solve()
    dt = time.time() - t0
    if path is not None:
        pv = verify_path(path["states"], n_gen)
        plen = len(path["states"]) - 1
        mlen = path_max_len(path["states"])
    else:
        pv, plen, mlen = False, None, None
    _CH = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}
    mts = key_to_state(solver.min_total_state) if solver.min_total_state is not None else None
    result = {
        "solved": path is not None,
        "path_verified": bool(pv),
        "nodes_explored": int(nodes),
        "path_len": plen,
        "max_len_along_path": mlen,
        "revert_hits": int(solver.revert_hits),
        "min_total_len": int(solver.min_total_len),
        # the actual presentation achieving min_total_len (relators as int-lists + decoded strings)
        "min_total_state": None if mts is None else [[int(x) for x in r] for r in mts],
        "min_total_state_str": None if mts is None else ["".join(_CH.get(int(x), "?") for x in r) for r in mts],
        "wall_time_s": round(dt, 4),
        "cap": "per_relator",
        "max_len": max_len,
    }
    return result, path
