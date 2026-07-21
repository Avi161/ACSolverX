"""Baseline substitution (S-move) greedy search — CPU + numba only.

The numba core (relators as (n, 2) bool arrays, substitution neighbours, Booth
canonicalisation, heapq by total length) is lifted verbatim from the repo's
`greedy_search.ipynb` prototype (`ACRelatorSolver`). We do NOT import or modify
that notebook or the JAX `envs/` code.

Adaptations over the prototype (all local to this new file):
  - per-relator length cap instead of the prototype's total-length `max_len`;
  - a `cyclic_reduce` toggle on the reduction step;
  - `stop_early`/counterexample logic dropped (we trivialise, not hunt);
  - a `greedy_search(...)` entry returning a stats dict for the jsonl pipeline.
"""

import heapq

import numpy as np
from numba import njit


# How often (in popped nodes) a solver calls its ``progress`` callback. The
# callback rate-limits itself by wall clock; this only bounds the granularity,
# so it must be small enough that a slow search still reports promptly
# (~0.6 s at the worst measured 1.6k nodes/s) and large enough to be free.
_HB_CHECK_EVERY = 1024


# ---------------------------------------------------------------------------
# Character <-> boolean-pair encoding (verbatim from greedy_search.ipynb)
# ---------------------------------------------------------------------------
# Each group element is a pair of bools: (generator: x/y, inverted: x/X).
char_to_array = {'x': [True, True], 'X': [True, False],
                 'y': [False, True], 'Y': [False, False]}


@njit(inline='always')
def array_to_char(bool1, bool2):
    if bool1:
        if bool2:
            return 'x'
        return 'X'
    elif bool2:
        return 'y'
    return 'Y'


@njit(inline='always')
def is_inverse_nj(a, b):
    """Whether two group elements are inverses of each other."""
    return (a[0] == b[0]) and (a[1] != b[1])


@njit(inline='always')
def is_equal_nj(a, b):
    """Whether two group elements are equal."""
    return (a[0] == b[0]) and (a[1] == b[1])


@njit(inline='always')
def is_less_than(a, b):
    """a < b under lexicographic order with True > False (Y < y < X < x)."""
    if a[0] != b[0]:
        return b[0]
    else:
        return a[1] < b[1]


@njit(cache=True)
def inverse_relator_nj(rel=np.array([[]])):
    """Invert a relator (reverse order, flip the inversion bit)."""
    res = rel.copy()
    res = np.flipud(res)
    res[:, 1] = np.logical_not(res[:, 1])
    return res


@njit(cache=True)
def reduce_relator_nj(rel, cyclic=True):
    """Free-reduce a relator (cancel adjacent inverse pairs).

    When ``cyclic`` is True also cancel inverse pairs across the wrap-around
    (cyclic reduction). ``cyclic=False`` performs only linear free reduction.
    Does not modify the input array. A word that cancels completely returns an
    empty (length-0) relator.

    Stack-based: the prototype's boundary branch did an out-of-bounds read
    (``rel[add_index + 1]``) when the cancelling partner was the last symbol,
    silently returning a garbage length-1 relator instead of the empty word.
    """
    n = len(rel)
    if n == 0:
        return rel

    rel_list = np.zeros_like(rel)
    length = 0                       # live symbols in rel_list (a stack)
    for idx in range(n):
        if length > 0 and is_inverse_nj(rel_list[length - 1], rel[idx]):
            length -= 1              # cancel against the top of the stack
        else:
            rel_list[length] = rel[idx]
            length += 1

    rel_list = rel_list[:length]

    if cyclic and length > 1 and is_inverse_nj(rel_list[0], rel_list[-1]):
        i = 1
        half_len = length / 2
        while i < half_len and is_inverse_nj(rel_list[i], rel_list[-1 - i]):
            i += 1
        rel_list = rel_list[i:-i]

    return rel_list


@njit(cache=True)
def find_minimal_rotation(rel):
    """Index-min cyclic rotation of a relator via Booth's algorithm.

    Order used: Y < y < X < x.
    """
    n = len(rel)
    rel = np.concatenate((rel, rel))
    f = np.full(2 * n, -1, dtype=np.int32)
    k = 0
    for j in range(1, 2 * n):
        i = f[j - k - 1]
        while i != -1 and (not is_equal_nj(rel[j], rel[k + i + 1])):
            if is_less_than(rel[j], rel[k + i + 1]):
                k = j - i - 1
            i = f[i]
        if i == -1 and (not is_equal_nj(rel[j], rel[k])):
            if is_less_than(rel[j], rel[k]):
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    return rel[k:k + n]


@njit(cache=True)
def lex_cmp_array(a, b):
    """Compare (n, 2) bool relators lexicographically; returns a >= b.

    True > False, so the implied symbol order is Y < y < X < x.
    """
    for x, y in zip(a, b):
        if x[0] == ~y[0]:
            return x[0]
        elif x[1] == ~y[1]:
            return x[1]
    return True


@njit(cache=True)
def lex_cmp_pair(a, b):
    """Compare two length-2 bool group elements; returns a > b."""
    if a[0] == ~b[0]:
        return a[0]
    elif a[1] == ~b[1]:
        return a[1]
    return False


@njit(cache=True)
def canonical_relator_nj(r):
    """Canonical form of a relator: min over its rotations and its inverse's."""
    r_min = find_minimal_rotation(r)
    inv_min = find_minimal_rotation(inverse_relator_nj(r))
    if lex_cmp_array(r_min, inv_min):
        return inv_min
    return r_min


@njit(cache=True)
def canonical_pair_nj(r1, r2):
    """Canonical, order-normalised pair (rotation/inversion invariant key)."""
    cr1 = canonical_relator_nj(r1)
    cr2 = canonical_relator_nj(r2)
    if len(cr1) > len(cr2) or (len(cr1) == len(cr2) and lex_cmp_array(cr1, cr2)):
        (cr1, cr2) = (cr2, cr1)
    return cr1, cr2


@njit(cache=True)
def get_neighbors_nj(r1, r2):
    """All substitution neighbours of a pair (r1, r2).

    For an index i with r1[i] == (r2[i])^-1, splice r2 into r1 at that point.
    Considers both r2 and r2^-1, and yields (neighbour, r2) and (r1, neighbour).
    """
    results = []
    candidates = [r2, inverse_relator_nj(r2)]
    for idx_c in range(2):
        c = candidates[idx_c]
        len_r1 = len(r1)
        len_c = len(c)
        for i in range(len_r1):
            rot1 = np.roll(r1, 2 * i)
            for j in range(len_c):
                rot2 = np.roll(c, 2 * j)
                if len(rot1) > 0 and len(rot2) > 0 and is_inverse_nj(rot1[-1], rot2[0]):
                    neighbour = np.concatenate((rot1, rot2))
                    results.append((neighbour, r2))
                    results.append((r1, neighbour))
    return results


@njit(cache=True)
def get_neighbors_with_moves_nj(r1, r2):
    """Substitution neighbours tagged with their Definition 2.1 (i, j, k1, k2).

    Faithful to the paper: a move with target relator ``i`` replaces r_i by
        rot_{k1}(r_i) . rot_{k2}(r_{3-i}^{j}),
    i.e. it is the OTHER relator (r_{3-i}) that may be inverted, never the
    target. Each result carries:
      - ``target`` in {1, 2}: which relator is replaced (r_i);
      - ``jsign``  in {1, -1}: sign j on the OTHER relator r_{3-i}^{j};
      - ``k1``: cyclic rotation of the target r_i;
      - ``k2``: cyclic rotation of the other relator r_{3-i}^{j}.
    Only seams that cancel (last of rot_{k1}(r_i) inverts first of
    rot_{k2}(r_{3-i}^{j})) are emitted. Replaying (concat, then reduce +
    canonicalise) reproduces the child exactly — see ``replay_move_nj``.

    Note: this enumerates the SAME canonical neighbour set as the notebook's
    ``get_neighbors_nj`` (verified equal); only the raw word / (i,j,k1,k2)
    labelling differs, so it matches Definition 2.1 for interpretability.
    """
    results = []
    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
        else:
            ri = r2
            rj = r1
        len_i = len(ri)
        if len_i == 0:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else inverse_relator_nj(rj)
            jsign = 1 if idx == 0 else -1
            len_o = len(oj)
            if len_o == 0:
                continue
            # Rotations of oj are independent of k1 -> precompute once
            # (was O(len_i*len_o) rolls, now O(len_o)).
            rots_o = [np.roll(oj, 2 * k2) for k2 in range(len_o)]
            for k1 in range(len_i):
                rot_i = np.roll(ri, 2 * k1)
                for k2 in range(len_o):
                    rot_o = rots_o[k2]
                    if is_inverse_nj(rot_i[-1], rot_o[0]):
                        piece = np.concatenate((rot_i, rot_o))
                        if target == 1:
                            results.append((piece, r2, 1, jsign, k1, k2))
                        else:
                            results.append((r1, piece, 2, jsign, k1, k2))
    return results


@njit(cache=True)
def replay_move_nj(r1, r2, target, jsign, k1, k2):
    """Re-apply one Definition 2.1 (i, j, k1, k2) move to a raw pair.

    Builds r_i <- rot_{k1}(r_i) . rot_{k2}(r_{3-i}^{j}) and returns the RAW
    (unreduced, non-canonical) child pair, exactly as
    ``get_neighbors_with_moves_nj`` constructed it. Callers apply
    ``reduce_relator_nj`` + ``canonical_pair_nj`` to land on the stored state.
    """
    if target == 1:
        ri = r1
        rj = r2
    else:
        ri = r2
        rj = r1
    oj = rj if jsign == 1 else inverse_relator_nj(rj)
    rot_i = np.roll(ri, 2 * k1)
    rot_o = np.roll(oj, 2 * k2)
    piece = np.concatenate((rot_i, rot_o))
    if target == 1:
        return piece, r2
    return r1, piece


def str_to_arr(s):
    """'xXyY' string -> (n, 2) bool array. Empty string -> well-formed (0, 2)."""
    if len(s) == 0:
        return np.zeros((0, 2), dtype=bool)
    return np.array([char_to_array[c] for c in s], dtype=bool)


@njit(inline='always')
def arr_to_str(arr):
    """(n, 2) bool array -> 'xXyY' string."""
    chars = [array_to_char(c[0], c[1]) for c in arr]
    return ''.join(chars)


@njit(inline='always')
def state_to_key(state):
    """(r1_arr, r2_arr) -> (r1_str, r2_str) for dict/set keys."""
    return (arr_to_str(state[0]), arr_to_str(state[1]))


# ---------------------------------------------------------------------------
# Solver (adapted from ACRelatorSolver)
# ---------------------------------------------------------------------------
class GreedyBaselineSolver:
    """Best-first (greedy) substitution search, ordered by total length.

    Differences from the prototype ``ACRelatorSolver``:
      - ``max_relator_length`` is a PER-RELATOR cap (prototype used a total cap);
      - ``cyclic_reduce`` toggles cyclic cancellation in the reduction step;
      - no counterexample / stop-early logic.
    """

    def __init__(self, r1, r2, max_nodes=10000, max_relator_length=24,
                 cyclic_reduce=True):
        self.max_nodes = max_nodes
        self.max_relator_length = max_relator_length
        self.cyclic_reduce = cyclic_reduce

        self.visited = dict()          # key -> parent key (for path reconstruction)
        self.move_in = dict()          # key -> (target, jsign, k1, k2) edge that reached it
        self.new_seen = set()          # all states seen this search
        self.pq = []

        r1_arr = str_to_arr(r1)
        r2_arr = str_to_arr(r2)
        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(r1_arr, self.cyclic_reduce),
            reduce_relator_nj(r2_arr, self.cyclic_reduce),
        )

    def solve(self, progress=None):
        """Return (path, moves, nodes_visited, new_seen).

        ``path`` is a list of (r1_arr, r2_arr) from the initial state to a
        trivial one, or ``None`` if no trivial state was reached within budget.
        ``moves`` is the parallel list of (target, jsign, k1, k2) tuples, one
        per edge (so ``len(moves) == len(path) - 1``), or ``None`` if unsolved.

        ``progress``: optional read-only callback invoked with the running node
        count every ``_HB_CHECK_EVERY`` pops. It must not touch solver state —
        results are bit-identical whether or not it is supplied.
        """
        init_key = state_to_key(self.initial_state)
        heapq.heappush(
            self.pq,
            (len(self.initial_state[0]) + len(self.initial_state[1]), 0, init_key),
        )
        self.visited[init_key] = None
        self.move_in[init_key] = None
        self.new_seen.add(init_key)
        nodes_visited = 0

        # Longest presentation actually POPPED/expanded (the states we run
        # get_neighbors_nj on), as opposed to merely discovered/enqueued.
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
                        priority = len(canon_r1) + len(canon_r2)
                        heapq.heappush(self.pq, (priority, depth + 1, key_new))

        return None, None, nodes_visited, self.new_seen

    def _key_to_state(self, key):
        return (str_to_arr(key[0]), str_to_arr(key[1]))


# ---------------------------------------------------------------------------
# Move (Definition 2.1) codec + replay
# ---------------------------------------------------------------------------
def move_to_str(move):
    """(target, jsign, k1, k2) tuple -> compact 'target_jsign_k1_k2' string."""
    return "_".join(str(int(v)) for v in move)


def str_to_move(s):
    """'target_jsign_k1_k2' string -> (target, jsign, k1, k2) int tuple."""
    return tuple(int(v) for v in s.split("_"))


def moves_to_states(r1_str, r2_str, moves, cyclic_reduce=True):
    """Replay a move list from a start presentation into the state sequence.

    Reproduces the canonical states the search visited: for each move apply the
    raw substitution, then ``reduce_relator_nj`` + ``canonical_pair_nj`` (the
    exact per-step normalisation used during search). Returns the list of
    ``[r1_str, r2_str]`` states, length ``len(moves) + 1``. This is the
    authoritative decoder — moves + start fully determine the path.
    """
    r1 = reduce_relator_nj(str_to_arr(r1_str), cyclic_reduce)
    r2 = reduce_relator_nj(str_to_arr(r2_str), cyclic_reduce)
    r1, r2 = canonical_pair_nj(r1, r2)
    states = [[arr_to_str(r1), arr_to_str(r2)]]
    for target, jsign, k1, k2 in moves:
        nr1, nr2 = replay_move_nj(r1, r2, target, jsign, k1, k2)
        nr1 = reduce_relator_nj(nr1, cyclic_reduce)
        nr2 = reduce_relator_nj(nr2, cyclic_reduce)
        r1, r2 = canonical_pair_nj(nr1, nr2)
        states.append([arr_to_str(r1), arr_to_str(r2)])
    return states


# ===========================================================================
# HIGH_SPEEDUP mode — for heavy (e.g. 1M-node) runs only.
#
# Same search, cheaper bookkeeping. Three changes, all provably result-neutral:
#   1. `new_seen` dropped (it only fed a final min()/max() scan) -> min/max are
#      tracked incrementally at push time.
#   2. `visited` is a set and `move_in` is gone -> no path. A solved
#      presentation is re-solved by the normal solver to recover its path
#      (the search is deterministic, so the path is exact).
#   3. State keys are packed `bytes` instead of `(str, str)`.
#
# (3) is only safe because the packed key SORTS IDENTICALLY to the string
# tuple, which keeps the heap tie-break `(priority, depth, key)` -- and hence
# `nodes_explored` / `solved` -- unchanged. The alphabet below is ordered to
# match Python's str compare (ASCII: 'X'<'Y'<'x'<'y') and the 0x00 separator is
# below every symbol byte, reproducing str's shorter-prefix-is-smaller rule.
# ===========================================================================

# arr row -> index 2*b0 + b1 gives Y=0, y=1, X=2, x=3; map to order-preserving
# codes X=1 < Y=2 < x=3 < y=4 (0x00 reserved as the separator).
_CODE_TABLE = np.array([2, 4, 1, 3], dtype=np.uint8)
_CODE_TO_CHAR = {1: 'X', 2: 'Y', 3: 'x', 4: 'y'}
_KEY_SEP = b'\x00'


def pack_key(a1, a2):
    """(r1_arr, r2_arr) -> packed bytes key. Sorts exactly like (r1_str, r2_str)."""
    c1 = _CODE_TABLE[a1[:, 0].astype(np.uint8) * 2 + a1[:, 1]]
    c2 = _CODE_TABLE[a2[:, 0].astype(np.uint8) * 2 + a2[:, 1]]
    return c1.tobytes() + _KEY_SEP + c2.tobytes()


def unpack_key(key):
    """Packed bytes key -> (r1_str, r2_str)."""
    b1, b2 = key.split(_KEY_SEP, 1)
    return (''.join(_CODE_TO_CHAR[c] for c in b1),
            ''.join(_CODE_TO_CHAR[c] for c in b2))


def key_lengths(key):
    """(len(r1), len(r2)) straight from the packed key — no decoding."""
    i = key.index(0)
    return i, len(key) - i - 1


def _codes_to_arr(buf):
    """order-preserving codes -> (n, 2) bool array (X=1,Y=2,x=3,y=4)."""
    c = np.frombuffer(buf, dtype=np.uint8)
    return np.stack(((c & 1) == 1, c >= 3), axis=1)


def unpack_arrays(key):
    """Packed key -> (r1_arr, r2_arr), skipping the string round-trip."""
    i = key.index(0)
    return _codes_to_arr(key[:i]), _codes_to_arr(key[i + 1:])


@njit(cache=True)
def expand_node_nj(r1, r2, max_relator_length, cyclic):
    """Neighbours + reduce + canonicalise, entirely inside numba.

    Returns ``(codes, lens, moves, count)`` where for child ``i``:
      ``codes[i, :lens[i,0]]``            = order-preserving codes of canon r1
      ``codes[i, 24+...]``                -- see below; r2 codes start at lens[i,0]
      ``moves[i] = (target, jsign, k1, k2)``
    Children are already length-pruned and canonicalised, so the caller only
    does dict/heap work. Enumeration order is IDENTICAL to
    ``get_neighbors_with_moves_nj`` (target -> jsign -> k1 -> k2), which the
    heap's ``depth`` tie-break depends on.

    ``codes`` is a fixed-width (n, 2*max_relator_length) uint8 buffer; the two
    relators are stored back-to-back starting at 0 and at ``lens[i,0]``.
    """
    cap = max_relator_length
    n1 = len(r1)
    n2 = len(r2)
    # upper bound: 2 targets x 2 signs x k1 x k2
    ub = 4 * (n1 + 1) * (n2 + 1)
    # np.empty (not zeros): only the [:la] / [la:la+lb] cells we write are read.
    codes = np.empty((ub, 2 * cap), dtype=np.uint8)
    lens = np.empty((ub, 2), dtype=np.int32)
    moves = np.empty((ub, 4), dtype=np.int32)
    count = 0

    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
        else:
            ri = r2
            rj = r1
        len_i = len(ri)
        if len_i == 0:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else inverse_relator_nj(rj)
            jsign = 1 if idx == 0 else -1
            len_o = len(oj)
            if len_o == 0:
                continue
            rots_o = [np.roll(oj, 2 * k2) for k2 in range(len_o)]
            for k1 in range(len_i):
                rot_i = np.roll(ri, 2 * k1)
                for k2 in range(len_o):
                    rot_o = rots_o[k2]
                    if not is_inverse_nj(rot_i[-1], rot_o[0]):
                        continue
                    piece = np.concatenate((rot_i, rot_o))
                    if target == 1:
                        nr1 = piece
                        nr2 = r2
                    else:
                        nr1 = r1
                        nr2 = piece
                    a = reduce_relator_nj(nr1, cyclic)
                    b = reduce_relator_nj(nr2, cyclic)
                    if len(a) > cap or len(b) > cap:
                        continue
                    ca, cb = canonical_pair_nj(a, b)
                    la = len(ca)
                    lb = len(cb)
                    for t in range(la):
                        v = 2 * ca[t, 0] + ca[t, 1]
                        # Y=0 -> 2, y=1 -> 4, X=2 -> 1, x=3 -> 3
                        if v == 0:
                            codes[count, t] = 2
                        elif v == 1:
                            codes[count, t] = 4
                        elif v == 2:
                            codes[count, t] = 1
                        else:
                            codes[count, t] = 3
                    for t in range(lb):
                        v = 2 * cb[t, 0] + cb[t, 1]
                        if v == 0:
                            codes[count, la + t] = 2
                        elif v == 1:
                            codes[count, la + t] = 4
                        elif v == 2:
                            codes[count, la + t] = 1
                        else:
                            codes[count, la + t] = 3
                    lens[count, 0] = la
                    lens[count, 1] = lb
                    moves[count, 0] = target
                    moves[count, 1] = jsign
                    moves[count, 2] = k1
                    moves[count, 3] = k2
                    count += 1
    return codes, lens, moves, count


@njit(inline='always')
def _rot_at(rel, k, t):
    """Element ``t`` of ``np.roll(rel, 2 * k)`` without building the rotation."""
    n = len(rel)
    return rel[(t - k) % n]


@njit(cache=True)
def _seam_reduced_len_nj(ri, k1, oj, k2, cyclic):
    """len(reduce_relator_nj(rot_i ++ rot_o, cyclic)) in O(cancelled), no concat.

    ``rot_i = np.roll(ri, 2*k1)``, ``rot_o = np.roll(oj, 2*k2)``. Both halves
    are freely reduced (rotations of a cyclically reduced relator are), so the
    only free cancellation is the cascade at the seam and the reduced word is
    the virtual ``rot_i[:n1-c] ++ rot_o[c:]`` — which is all the cyclic pass
    then needs to index. Exact only under that precondition; every state in a
    search satisfies it (children are reduced then canonicalised).
    """
    n1 = len(ri)
    n2 = len(oj)
    lim = n1 if n1 < n2 else n2
    c = 0
    while c < lim and is_inverse_nj(_rot_at(ri, k1, n1 - 1 - c),
                                    _rot_at(oj, k2, c)):
        c += 1
    m = n1 + n2 - 2 * c
    if (not cyclic) or m <= 1:
        return m
    # W[pos] = rot_i[pos] for pos < left, else rot_o[pos - left + c]
    left = n1 - c
    p_last = m - 1
    a = _rot_at(ri, k1, 0) if left > 0 else _rot_at(oj, k2, c)
    b = (_rot_at(ri, k1, p_last) if p_last < left
         else _rot_at(oj, k2, p_last - left + c))
    if not is_inverse_nj(a, b):
        return m
    i = 1
    half = m / 2
    while i < half:
        pl = i
        pr = m - 1 - i
        a = (_rot_at(ri, k1, pl) if pl < left
             else _rot_at(oj, k2, pl - left + c))
        b = (_rot_at(ri, k1, pr) if pr < left
             else _rot_at(oj, k2, pr - left + c))
        if not is_inverse_nj(a, b):
            break
        i += 1
    return m - 2 * i


@njit(cache=True)
def expand_node_topk_nj(r1, r2, max_relator_length, cyclic, sgn, topk):
    """``expand_node_nj``'s children, materialising only the ``topk`` kept ones.

    Pass 1 prices every child by its reduced length alone (``_seam_reduced_len_nj``,
    O(cancelled)) and drops the over-cap ones there. At a saturated climb that
    is ~every child — the old kernel paid a full concatenate + two reduces
    (O(L) each, ~90k children at L=300) before discarding them on the same
    test, which is the whole reason a tier-300 climb ran at ~1 pop/s.
    Pass 2 concatenates, reduces, canonicalises and encodes only the survivors
    the caller would have kept.

    ``sgn`` = +1 keep shortest (descend) | -1 keep longest (climb).
    ``topk <= 0`` keeps everything. Output order reproduces the caller's old
    ``np.argsort(sgn * totals, kind='stable')[:child_cap]`` exactly, and
    generation order when the survivor count is <= ``topk``.
    """
    cap = max_relator_length
    n1 = len(r1)
    n2 = len(r2)
    ub = 4 * (n1 + 1) * (n2 + 1)
    c_len = np.empty(ub, dtype=np.int64)
    c_tot = np.empty(ub, dtype=np.int64)
    c_mv = np.empty((ub, 4), dtype=np.int32)
    cnt = 0

    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
        else:
            ri = r2
            rj = r1
        len_i = len(ri)
        if len_i == 0:
            continue
        # the untouched relator is reduced once per target, not per child
        oth = reduce_relator_nj(rj, cyclic)
        len_oth = len(oth)
        if len_oth > cap:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else inverse_relator_nj(rj)
            jsign = 1 if idx == 0 else -1
            len_o = len(oj)
            if len_o == 0:
                continue
            for k1 in range(len_i):
                last_i = _rot_at(ri, k1, len_i - 1)
                for k2 in range(len_o):
                    if not is_inverse_nj(last_i, _rot_at(oj, k2, 0)):
                        continue
                    m = _seam_reduced_len_nj(ri, k1, oj, k2, cyclic)
                    if m > cap:
                        continue
                    c_len[cnt] = m
                    c_tot[cnt] = m + len_oth
                    c_mv[cnt, 0] = target
                    c_mv[cnt, 1] = jsign
                    c_mv[cnt, 2] = k1
                    c_mv[cnt, 3] = k2
                    cnt += 1

    if topk > 0 and cnt > topk:
        order = np.argsort(sgn * c_tot[:cnt], kind='mergesort')[:topk]
    else:
        order = np.arange(cnt)

    count = len(order)
    codes = np.empty((count if count > 0 else 1, 2 * cap), dtype=np.uint8)
    lens = np.empty((count if count > 0 else 1, 2), dtype=np.int32)
    moves = np.empty((count if count > 0 else 1, 4), dtype=np.int32)

    for out in range(count):
        s = order[out]
        target = c_mv[s, 0]
        k1 = c_mv[s, 2]
        k2 = c_mv[s, 3]
        if target == 1:
            ri = r1
            rj = r2
        else:
            ri = r2
            rj = r1
        oj = rj if c_mv[s, 1] == 1 else inverse_relator_nj(rj)
        piece = np.concatenate((np.roll(ri, 2 * k1), np.roll(oj, 2 * k2)))
        if target == 1:
            a = reduce_relator_nj(piece, cyclic)
            b = reduce_relator_nj(r2, cyclic)
        else:
            a = reduce_relator_nj(r1, cyclic)
            b = reduce_relator_nj(piece, cyclic)
        ca, cb = canonical_pair_nj(a, b)
        la = len(ca)
        lb = len(cb)
        for t in range(la):
            v = 2 * ca[t, 0] + ca[t, 1]
            if v == 0:
                codes[out, t] = 2
            elif v == 1:
                codes[out, t] = 4
            elif v == 2:
                codes[out, t] = 1
            else:
                codes[out, t] = 3
        for t in range(lb):
            v = 2 * cb[t, 0] + cb[t, 1]
            if v == 0:
                codes[out, la + t] = 2
            elif v == 1:
                codes[out, la + t] = 4
            elif v == 2:
                codes[out, la + t] = 1
            else:
                codes[out, la + t] = 3
        lens[out, 0] = la
        lens[out, 1] = lb
        moves[out, 0] = target
        moves[out, 1] = c_mv[s, 1]
        moves[out, 2] = k1
        moves[out, 3] = k2

    return codes, lens, moves, count


class GreedyHeavySolver:
    """Memory-lean twin of ``GreedyBaselineSolver`` for very large budgets.

    Pops in exactly the same order (identical heap keys), so ``nodes_explored``
    and ``solved`` match the normal solver. Reports ``path_length`` (the solved
    node's depth) but does not reconstruct the path itself.
    """

    def __init__(self, r1, r2, max_nodes=10000, max_relator_length=24,
                 cyclic_reduce=True):
        self.max_nodes = max_nodes
        self.max_relator_length = max_relator_length
        self.cyclic_reduce = cyclic_reduce

        r1_arr = str_to_arr(r1)
        r2_arr = str_to_arr(r2)
        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(r1_arr, self.cyclic_reduce),
            reduce_relator_nj(r2_arr, self.cyclic_reduce),
        )
        self.visited = set()
        self.pq = []
        self.n_discovered = 0
        self.solved_depth = None       # depth of the solved node == path_length

    def solve(self, progress=None):
        """Return (solved, nodes_visited). Stats live on ``self``.

        ``progress``: see ``GreedyBaselineSolver.solve`` — read-only, result-neutral.
        """
        cap = self.max_relator_length
        init_key = pack_key(self.initial_state[0], self.initial_state[1])
        init_total = len(self.initial_state[0]) + len(self.initial_state[1])
        heapq.heappush(self.pq, (init_total, 0, init_key))
        self.visited.add(init_key)
        self.n_discovered = 1

        # incremental replacements for the old min()/max() scan over new_seen
        self.min_key, self.min_total = init_key, init_total
        self.max_key, self.max_total = init_key, init_total
        self.max_expanded_key, self.max_expanded_total = init_key, init_total

        nodes_visited = 0
        pq = self.pq
        visited = self.visited
        while pq and nodes_visited < self.max_nodes:
            total, depth, key = heapq.heappop(pq)
            nodes_visited += 1
            if progress is not None and nodes_visited % _HB_CHECK_EVERY == 0:
                progress(nodes_visited)
            if total > self.max_expanded_total:
                self.max_expanded_key, self.max_expanded_total = key, total

            l1, l2 = key_lengths(key)
            if l1 == 1 and l2 == 1:
                self.solved_depth = depth
                return True, nodes_visited

            a1, a2 = unpack_arrays(key)
            codes, lens, moves, count = expand_node_nj(
                a1, a2, cap, self.cyclic_reduce)

            depth1 = depth + 1
            for i in range(count):
                la = lens[i, 0]
                lb = lens[i, 1]
                row = codes[i]
                key_new = row[:la].tobytes() + _KEY_SEP + row[la:la + lb].tobytes()
                if key_new not in visited:
                    visited.add(key_new)
                    self.n_discovered += 1
                    new_total = int(la) + int(lb)
                    if new_total < self.min_total:
                        self.min_key, self.min_total = key_new, new_total
                    elif new_total > self.max_total:
                        self.max_key, self.max_total = key_new, new_total
                    heapq.heappush(pq, (new_total, depth1, key_new))

        return False, nodes_visited


# ---------------------------------------------------------------------------
# Public entry for the jsonl pipeline
# ---------------------------------------------------------------------------
def _greedy_search_heavy(r1_str, r2_str, node_budget, max_relator_length,
                         cyclic_reduce, progress=None):
    """HIGH_SPEEDUP path: same stats dict (path_length included), no path/path_moves."""
    solver = GreedyHeavySolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
    )
    solved, nodes_visited = solver.solve(progress)
    min_r = unpack_key(solver.min_key)
    max_r = unpack_key(solver.max_key)
    exp_r = unpack_key(solver.max_expanded_key)
    return {
        "solved": solved,
        "nodes_explored": nodes_visited,
        "path_length": solver.solved_depth,
        "min_relator_length": solver.min_total,
        "min_relator": [min_r[0], min_r[1]],
        "max_relator_length": solver.max_total,
        "max_relator": [max_r[0], max_r[1]],
        "max_relator_length_expanded": solver.max_expanded_total,
        "max_relator_expanded": [exp_r[0], exp_r[1]],
        "path": [],
        "path_moves": [],
    }


def greedy_search(r1_str, r2_str, node_budget, max_relator_length=24,
                  cyclic_reduce=True, high_speedup=False, progress=None):
    """Run the baseline greedy on one presentation; return a stats dict.

    Keys: solved, nodes_explored, path_length, min_relator_length,
    min_relator, max_relator_length, max_relator, path, path_moves.
    (``path_length``/``path``/``path_moves`` are None/[] when unsolved.)
    ``path`` is the list of [r1_str, r2_str] states; ``path_moves`` is the
    parallel list of 'target_jsign_k1_k2' move strings (Definition 2.1) that
    reproduces ``path`` via ``moves_to_states`` — the compact storage form.

    ``high_speedup=True`` uses the memory-lean solver (for 1M-node runs): the
    same ``solved``/``nodes_explored``/``path_length``/min/max stats, but
    ``path``/``path_moves`` come back empty — recover the path (not the length,
    which is already reported) by re-running with ``high_speedup=False``.

    ``progress``: optional callback for live nodes/s reporting; result-neutral.
    """
    if high_speedup:
        return _greedy_search_heavy(r1_str, r2_str, node_budget,
                                    max_relator_length, cyclic_reduce, progress)

    solver = GreedyBaselineSolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
    )
    path, moves, nodes_visited, new_seen = solver.solve(progress)

    # Shortest / longest presentation (by total length) seen along the search.
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
