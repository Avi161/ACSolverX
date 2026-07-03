"""GS-Sub greedy (n=2), lifted verbatim from ``greedy_search.ipynb``.

This is the paper's classical greedy baseline (substitution moves, best-first on
``len(r1)+len(r2)``). The njit helpers and ``ACRelatorSolver`` below are copied
CELL-for-CELL from the notebook with exactly TWO changes, both marked ``# CHANGED``:

  1. ``__init__`` gains a ``cap_mode`` argument (``'sum'`` | ``'per_relator'``).
  2. The single length-cap line in ``solve()`` branches on ``cap_mode``.

Everything else (bool-``[n,2]``-array state representation, Booth minimal rotation,
canonicalisation, ``get_neighbors_nj``) is unchanged — so the notebook's
``np.roll(r, 2*i)`` stride is CORRECT here (it is only wrong for a future int port).

Added below the verbatim block (new code, not from the notebook):
  ``flatlist_to_strs``  — env flat-int line -> the two ``xXyY`` strings the solver wants
  ``path_stats``        — (path_len, max_len_along_path) for a returned path
  ``verify_path``       — independent replay of a path (the ``path_verified`` gate)
  ``solve_one``         — run one presentation end-to-end -> a result dict
"""
import heapq
import time

import numpy as np
from numba import njit

# ===================================================================================
# ==== VERBATIM from greedy_search.ipynb (cells 1, 2, 4) — do not edit except the ====
# ==== two lines marked `# CHANGED`.                                              ====
# ===================================================================================

# cell 1 — known counterexamples (used by ACRelatorSolver.__init__)
counterexamples = {('xyxYXY', 'x' * n + 'Y' * (n + 1)): f'AK({n})' for n in range(3, 8)}
counterexamples[('XyyxYYY', 'XyxxyXX')] = 'Length 14 #1'
counterexamples[('XyyxYYY', 'XyxxYXX')] = 'Length 14 #2'

# cell 2 — encoding + njit helpers + solver
# We store the group elements as pairs of booleans.
# The first boolean represents the generator (x or y) and the second boolean represents inversion (x or X).
char_to_array = {'x': [True, True], 'X': [True, False], 'y': [False, True], 'Y': [False, False]}


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
    return (a[0] == b[0]) and (a[1] != b[1])


@njit(inline='always')
def is_equal_nj(a, b):
    return (a[0] == b[0]) and (a[1] == b[1])


@njit(inline='always')
def is_less_than(a, b):
    if a[0] != b[0]:
        return b[0]
    else:
        return a[1] < b[1]


@njit
def inverse_relator_nj(rel=np.array([[]])):
    res = rel.copy()
    res = np.flipud(res)
    res[:, 1] = np.logical_not(res[:, 1])
    return res


@njit
def reduce_relator_nj(rel):
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
    if is_inverse_nj(rel_list[0], rel_list[-1]):
        i = 1
        half_len = len(rel_list) / 2
        while i < half_len and is_inverse_nj(rel_list[i], rel_list[-1 - i]):
            i += 1
        rel_list = rel_list[i:-i]
    return rel_list


@njit
def find_minimal_rotation(rel):
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
    for x, y in zip(a, b):
        if x[0] == ~y[0]:
            return x[0]
        elif x[1] == ~y[1]:
            return x[1]
    return True


@njit
def lex_cmp_pair(a, b):
    if a[0] == ~b[0]:
        return a[0]
    elif a[1] == ~b[1]:
        return a[1]
    return False


@njit
def canonical_relator_nj(r):
    r_min = find_minimal_rotation(r)
    inv_min = find_minimal_rotation(inverse_relator_nj(r))
    if lex_cmp_array(r_min, inv_min):
        return inv_min
    return r_min


@njit
def canonical_pair_nj(r1, r2):
    cr1 = canonical_relator_nj(r1)
    cr2 = canonical_relator_nj(r2)
    if len(cr1) > len(cr2) or (len(cr1) == len(cr2) and lex_cmp_array(cr1, cr2)):
        (cr1, cr2) = (cr2, cr1)
    return cr1, cr2


@njit
def get_neighbors_nj(r1, r2):
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
    return np.array([char_to_array[c] for c in s], dtype=bool)


@njit(inline='always')
def arr_to_str(arr):
    chars = [array_to_char(c[0], c[1]) for c in arr]
    return ''.join(chars)


@njit(inline='always')
def state_to_key(state):
    return (arr_to_str(state[0]), arr_to_str(state[1]))


def canonical_pair_str(r1, r2):
    r1_arr = str_to_arr(r1)
    r2_arr = str_to_arr(r2)
    (canon_r1_arr, canon_r2_arr) = canonical_pair_nj(reduce_relator_nj(r1_arr), reduce_relator_nj(r2_arr))
    return arr_to_str(canon_r1_arr), arr_to_str(canon_r2_arr)


class ACRelatorSolver:
    def __init__(self, r1, r2, max_nodes=10000, max_len=100, visited=None,
                 verbose=True, stop_early=True, cap_mode='sum'):  # CHANGED: + cap_mode
        self.max_nodes = max_nodes
        self.verbose = verbose
        self.stop_early = stop_early
        self.cap_mode = cap_mode  # CHANGED: 'sum' (notebook native) | 'per_relator'
        if visited is None:
            self.visited = dict()
        else:
            self.visited = visited
        self.new_seen = set()
        self.max_len = max_len
        self.current_depth = 0
        self.max_depth = 0
        self.max_priority = len(r1) + len(r2)
        self.min_priority = len(r1) + len(r2)
        self.pq = []
        r1_arr = str_to_arr(r1)
        r2_arr = str_to_arr(r2)
        self.initial_state = canonical_pair_nj(reduce_relator_nj(r1_arr), reduce_relator_nj(r2_arr))
        self.counterexamples = {canonical_pair_str(k[0], k[1]): v for k, v in counterexamples.items()}

    def solve(self):
        heapq.heappush(self.pq, (len(self.initial_state[0]) + len(self.initial_state[1]), 0, state_to_key(self.initial_state)))
        self.visited[state_to_key(self.initial_state)] = None
        self.new_seen = set()
        self.new_seen.add(state_to_key(self.initial_state))
        nodes_visited = 0

        while self.pq and nodes_visited < self.max_nodes:
            _, depth, key = heapq.heappop(self.pq)
            nodes_visited += 1
            r1, r2 = self._key_to_state(key)

            if self.verbose:
                if len(r1) + len(r2) > self.max_priority:
                    print(f"First state of priority {len(r1) + len(r2)}, depth: {depth}, values: {len(r1)}, {len(r2)} ({arr_to_str(r1)},{arr_to_str(r2)}), nodes: {nodes_visited}")
                    self.max_priority = len(r1) + len(r2)
                if len(r1) + len(r2) < self.min_priority:
                    print(f"First state of priority {len(r1) + len(r2)}, depth: {depth}, values: {len(r1)}, {len(r2)} ({arr_to_str(r1)},{arr_to_str(r2)}), nodes: {nodes_visited}")
                    self.min_priority = len(r1) + len(r2)

            if len(r1) == 1 and len(r2) == 1:
                path = []
                state_key = key
                while state_key is not None:
                    path.append(self._key_to_state(state_key))
                    state_key = self.visited[state_key]
                path.reverse()
                return path, nodes_visited, self.new_seen
            elif self.stop_early and key in self.counterexamples:
                print(f"Found counterexample {self.counterexamples[key]} at depth {depth}, r1 = {arr_to_str(r1)}, r2 = {arr_to_str(r2)}, nodes = {nodes_visited}")
                path = []
                state_key = key
                while state_key is not None:
                    path.append(self._key_to_state(state_key))
                    state_key = self.visited[state_key]
                path.reverse()
                return path, nodes_visited, self.new_seen

            for nr1, nr2 in get_neighbors_nj(r1, r2):
                nr1r = reduce_relator_nj(nr1)
                nr2r = reduce_relator_nj(nr2)

                # CHANGED: length cap branches on cap_mode (was: len(nr1r)+len(nr2r) < self.max_len)
                if self.cap_mode == 'sum':
                    within_cap = (len(nr1r) + len(nr2r) < self.max_len)
                else:  # 'per_relator'
                    within_cap = (len(nr1r) < self.max_len and len(nr2r) < self.max_len)

                if within_cap:
                    canon_r1, canon_r2 = canonical_pair_nj(nr1r, nr2r)
                    key_new = state_to_key((canon_r1, canon_r2))
                    if key_new not in self.visited:
                        self.visited[key_new] = key
                        self.new_seen.add(key_new)
                        priority = len(canon_r1) + len(canon_r2)  # normal GS priority
                        heapq.heappush(self.pq, (priority, depth + 1, key_new))

        if self.verbose:
            print("No trivial relators found.")
            min_pres = min(self.new_seen, key=lambda k: len(k[0]) + len(k[1]))
            min_pres_r1 = min(self.new_seen, key=lambda k: (len(k[0]), len(k[1])))
            print(f"Minimal element found: r1 = {min_pres[0]}, r2 = {min_pres[1]}, Size: ({len(min_pres[0])}, {len(min_pres[1])})")
            print(f"Minimal element found: r1 = {min_pres_r1[0]}, r2 = {min_pres_r1[1]}, Size: ({len(min_pres_r1[0])}, {len(min_pres_r1[1])})")

        return None, nodes_visited, self.new_seen

    def _key_to_state(self, key):
        return (str_to_arr(key[0]), str_to_arr(key[1]))


# cell 4 — Miller--Schupp generator (used by the base-case check)
def MS(n, w):
    return 'X' + 'y' * n + 'x' + 'Y' * (n + 1), 'X' + w


# ===================================================================================
# ==== NEW (not from the notebook): flat-int loading, path stats, verification,   ====
# ==== and a single-presentation runner.                                          ====
# ===================================================================================

INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}  # env signed-int -> xXyY (matches scripts/build_ms_reps.py)


def flatlist_to_strs(flat, half=24):
    """Env flat-int presentation (len 2*half, first half = r1, second = r2, 0=pad)
    -> the two ``xXyY`` strings ``ACRelatorSolver`` expects."""
    r1 = ''.join(INT_TO_CHAR[i] for i in flat[:half] if i != 0)
    r2 = ''.join(INT_TO_CHAR[i] for i in flat[half:] if i != 0)
    return r1, r2


def path_stats(path):
    """(path_len, max_len_along_path) for a returned solve path.

    path_len = number of moves = len(path)-1.
    max_len_along_path = peak |r1|+|r2| across the path (the temporary length 'hump').
    """
    path_len = len(path) - 1
    max_len_along_path = max(len(a) + len(b) for a, b in path)
    return path_len, max_len_along_path


def verify_path(path):
    """Replay a returned path independently of the search's visited/heap bookkeeping.

    For each consecutive (s_k, s_{k+1}) recompute get_neighbors_nj(s_k) from scratch,
    reduce+canonicalise each candidate, and require that canonical(s_{k+1}) is among
    them; then require the final state be trivial (both relators length 1). Returns
    False on any illegal step, a non-trivial endpoint, or an empty/None path.

    Scope: this shares get_neighbors_nj/canonicalisation with the solver, so it catches
    search bugs (bad parent pointers, wrong ordering) but NOT a move-generation bug. The
    move-logic gold check is the real-env check_paths (JAX), deferred to the n=3 env.
    """
    if not path:
        return False
    for k in range(len(path) - 1):
        cur_r1, cur_r2 = path[k]
        target = state_to_key(path[k + 1])
        found = False
        for nr1, nr2 in get_neighbors_nj(cur_r1, cur_r2):
            cand = canonical_pair_nj(reduce_relator_nj(nr1), reduce_relator_nj(nr2))
            if state_to_key(cand) == target:
                found = True
                break
        if not found:
            return False
    last_r1, last_r2 = path[-1]
    return len(last_r1) == 1 and len(last_r2) == 1


def solve_one(flat, cap_mode='sum', max_len=100, max_nodes=100_000):
    """Run one flat-int presentation to a result dict.

    ``solved`` is the RAW 'greedy reached the trivial presentation within budget'
    flag; ``path_verified`` is the independent replay. A solve is only counted
    downstream when BOTH are true, so a ``solved:true, path_verified:false`` line
    is a loud solver-bug signal, not silently dropped.
    """
    r1, r2 = flatlist_to_strs(flat)
    solver = ACRelatorSolver(r1, r2, max_nodes=max_nodes, max_len=max_len,
                             verbose=False, stop_early=False, cap_mode=cap_mode)
    t0 = time.time()
    path, nodes, _ = solver.solve()
    dt = time.time() - t0

    reached = path is not None and len(path[-1][0]) == 1 and len(path[-1][1]) == 1
    if reached:
        pv = verify_path(path)
        plen, mlen = path_stats(path)
    else:
        pv, plen, mlen = False, None, None

    return {
        'solved': bool(reached),
        'path_verified': bool(pv),
        'nodes_explored': int(nodes),
        'path_len': plen,
        'max_len_along_path': mlen,
        'wall_time_s': round(dt, 4),
    }
