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


@njit
def inverse_relator_nj(rel=np.array([[]])):
    """Invert a relator (reverse order, flip the inversion bit)."""
    res = rel.copy()
    res = np.flipud(res)
    res[:, 1] = np.logical_not(res[:, 1])
    return res


@njit
def reduce_relator_nj(rel, cyclic=True):
    """Free-reduce a relator (cancel adjacent inverse pairs).

    When ``cyclic`` is True also cancel inverse pairs across the wrap-around
    (cyclic reduction). ``cyclic=False`` performs only linear free reduction.
    Does not modify the input array.
    """
    n = len(rel)

    rel_list = np.zeros_like(rel)
    rel_list[0] = rel[0]

    current_index = 0
    add_index = 1

    while add_index < n:
        if is_inverse_nj(rel_list[current_index], rel[add_index]):
            if current_index == 0:
                rel_list[0] = rel[add_index + 1]
                add_index += 2
            else:
                add_index += 1
                current_index -= 1
        else:
            current_index += 1
            rel_list[current_index] = rel[add_index]
            add_index += 1

    rel_list = rel_list[:current_index + 1]

    if cyclic and is_inverse_nj(rel_list[0], rel_list[-1]):
        i = 1
        half_len = len(rel_list) / 2
        while i < half_len and is_inverse_nj(rel_list[i], rel_list[-1 - i]):
            i += 1
        rel_list = rel_list[i:-i]

    return rel_list


@njit
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


@njit
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


@njit
def lex_cmp_pair(a, b):
    """Compare two length-2 bool group elements; returns a > b."""
    if a[0] == ~b[0]:
        return a[0]
    elif a[1] == ~b[1]:
        return a[1]
    return False


@njit
def canonical_relator_nj(r):
    """Canonical form of a relator: min over its rotations and its inverse's."""
    r_min = find_minimal_rotation(r)
    inv_min = find_minimal_rotation(inverse_relator_nj(r))
    if lex_cmp_array(r_min, inv_min):
        return inv_min
    return r_min


@njit
def canonical_pair_nj(r1, r2):
    """Canonical, order-normalised pair (rotation/inversion invariant key)."""
    cr1 = canonical_relator_nj(r1)
    cr2 = canonical_relator_nj(r2)
    if len(cr1) > len(cr2) or (len(cr1) == len(cr2) and lex_cmp_array(cr1, cr2)):
        (cr1, cr2) = (cr2, cr1)
    return cr1, cr2


@njit
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


def str_to_arr(s):
    """'xXyY' string -> (n, 2) bool array."""
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
        self.new_seen = set()          # all states seen this search
        self.pq = []

        r1_arr = str_to_arr(r1)
        r2_arr = str_to_arr(r2)
        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(r1_arr, self.cyclic_reduce),
            reduce_relator_nj(r2_arr, self.cyclic_reduce),
        )

    def solve(self):
        """Return (path, nodes_visited, new_seen).

        ``path`` is a list of (r1_arr, r2_arr) from the initial state to a
        trivial one, or ``None`` if no trivial state was reached within budget.
        """
        init_key = state_to_key(self.initial_state)
        heapq.heappush(
            self.pq,
            (len(self.initial_state[0]) + len(self.initial_state[1]), 0, init_key),
        )
        self.visited[init_key] = None
        self.new_seen.add(init_key)
        nodes_visited = 0

        # Longest presentation actually POPPED/expanded (the states we run
        # get_neighbors_nj on), as opposed to merely discovered/enqueued.
        self.max_expanded_key = init_key

        while self.pq and nodes_visited < self.max_nodes:
            _, depth, key = heapq.heappop(self.pq)
            nodes_visited += 1
            if len(key[0]) + len(key[1]) > \
                    len(self.max_expanded_key[0]) + len(self.max_expanded_key[1]):
                self.max_expanded_key = key
            r1, r2 = self._key_to_state(key)

            if len(r1) == 1 and len(r2) == 1:
                path = []
                state_key = key
                while state_key is not None:
                    path.append(self._key_to_state(state_key))
                    state_key = self.visited[state_key]
                path.reverse()
                return path, nodes_visited, self.new_seen

            for nr1, nr2 in get_neighbors_nj(r1, r2):
                nr1r = reduce_relator_nj(nr1, self.cyclic_reduce)
                nr2r = reduce_relator_nj(nr2, self.cyclic_reduce)

                if len(nr1r) <= self.max_relator_length and \
                        len(nr2r) <= self.max_relator_length:
                    canon_r1, canon_r2 = canonical_pair_nj(nr1r, nr2r)
                    key_new = state_to_key((canon_r1, canon_r2))
                    if key_new not in self.visited:
                        self.visited[key_new] = key
                        self.new_seen.add(key_new)
                        priority = len(canon_r1) + len(canon_r2)
                        heapq.heappush(self.pq, (priority, depth + 1, key_new))

        return None, nodes_visited, self.new_seen

    def _key_to_state(self, key):
        return (str_to_arr(key[0]), str_to_arr(key[1]))


# ---------------------------------------------------------------------------
# Public entry for the jsonl pipeline
# ---------------------------------------------------------------------------
def greedy_search(r1_str, r2_str, node_budget, max_relator_length=24,
                  cyclic_reduce=True):
    """Run the baseline greedy on one presentation; return a stats dict.

    Keys: solved, nodes_explored, path_length, min_relator_length,
    min_relator, max_relator_length, max_relator, path.
    (``path_length`` and ``path`` are None / [] when unsolved; ``path`` is a
    list of [r1_str, r2_str] states from initial to trivial.)
    """
    solver = GreedyBaselineSolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
    )
    path, nodes_visited, new_seen = solver.solve()

    # Shortest / longest presentation (by total length) seen along the search.
    min_key = min(new_seen, key=lambda k: len(k[0]) + len(k[1]))
    max_key = max(new_seen, key=lambda k: len(k[0]) + len(k[1]))
    # Longest presentation actually popped/expanded (states we operated on).
    exp_key = solver.max_expanded_key

    solved = path is not None
    if solved:
        path_states = [[arr_to_str(a), arr_to_str(b)] for a, b in path]
        path_length = len(path_states) - 1
    else:
        path_states = []
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
    }
