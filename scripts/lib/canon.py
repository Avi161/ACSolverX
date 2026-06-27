"""Canonical-form utilities for AC presentations (the lab's `canonical_pair_nj`).

The boolean-array canonicalizer (`reduce_relator_nj`, `canonical_pair_nj`,
`get_neighbors_nj`, `str_to_arr`, `arr_to_str`, ...) is ported VERBATIM from
`greedy_search.ipynb` cell 2 — the lab's implemented canonical form used for
state-keying/dedup in the Two-Hump paper. A relator is a numpy array of shape
(n, 2) of bools `[generator, inverted]`; the alphabet order is `Y < y < X < x`
(True > False). `canonical_pair_nj` = each relator lex-min over rotations + its
inverse, pair ordered length-then-lex. Validated 1:1 with the greedy CSV's
stored states in `experiments/eda.ipynb` P2-11.

numba is OPTIONAL: if installed, the `@njit` functions JIT-compile; if not, a
passthrough shim runs them as plain numpy (correct, just slower). This module
adds no JAX dependency.

Bridges to the env's int8 representation (`x->1, X->-1, y->2, Y->-2`, padding 0)
are at the bottom: `env_state_to_strs`, `strs_to_presentation_literal`,
`canonical_pair_str`, `canon_key`.
"""

import numpy as np

# --- numba shim: use real njit if available, else a no-op passthrough --------
try:  # pragma: no cover - depends on environment
    from numba import njit
    HAVE_NUMBA = True
except ImportError:  # pragma: no cover
    HAVE_NUMBA = False

    def njit(*args, **kwargs):
        # Support both @njit and @njit(inline='always') / @njit(cache=True).
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]

        def deco(fn):
            return fn

        return deco


# =====================================================================
# Verbatim port of greedy_search.ipynb cell 2 (canonicalization + neighbors).
# Only the solver class and `counterexamples` global are intentionally omitted.
# =====================================================================

# Map characters to integers and back.
# We store group elements as pairs of booleans: [generator (x/y), inverted].
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
    """Check if two group elements are inverses of each other."""
    return (a[0] == b[0]) and (a[1] != b[1])


@njit(inline='always')
def is_equal_nj(a, b):
    """Check if two group elements are equal."""
    return (a[0] == b[0]) and (a[1] == b[1])


@njit(inline='always')
def is_less_than(a, b):
    """Returns a < b with order defined as lexicographic order with True > False."""
    if a[0] != b[0]:
        return b[0]
    else:
        return a[1] < b[1]


@njit
def inverse_relator_nj(rel=np.array([[]])):
    """Invert a relator (reverse order, flip the inversion boolean)."""
    res = rel.copy()
    res = np.flipud(res)
    res[:, 1] = np.logical_not(res[:, 1])
    return res


@njit
def reduce_relator_nj(rel):
    """Free + cyclic reduction of a relator. Does not modify the input array."""
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
    """Minimal rotation via Booth's algorithm under the order `Y < y < X < x`."""
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
    """Compare two (n, 2) bool arrays lexicographically. Returns a >= b.

    True > False, so the implied symbol order is: Y < y < X < x.
    """
    for x, y in zip(a, b):
        if x[0] == ~y[0]:
            return x[0]
        elif x[1] == ~y[1]:
            return x[1]
    return True


@njit
def lex_cmp_pair(a, b):
    """Compare two length-2 bool arrays lexicographically. Returns a > b."""
    if a[0] == ~b[0]:
        return a[0]
    elif a[1] == ~b[1]:
        return a[1]
    return False


@njit
def canonical_relator_nj(r):
    """Canonical relator: lex-min over rotations of r and of r^{-1}."""
    r_min = find_minimal_rotation(r)
    inv_min = find_minimal_rotation(inverse_relator_nj(r))
    if lex_cmp_array(r_min, inv_min):
        return inv_min
    return r_min


@njit
def canonical_pair_nj(r1, r2):
    """Canonical pair: canonicalize each relator, then order length-then-lex."""
    cr1 = canonical_relator_nj(r1)
    cr2 = canonical_relator_nj(r2)
    if len(cr1) > len(cr2) or (len(cr1) == len(cr2) and lex_cmp_array(cr1, cr2)):
        (cr1, cr2) = (cr2, cr1)
    return cr1, cr2


@njit
def get_neighbors_nj(r1, r2):
    """All substitution neighbors of (r1, r2) and (r1, r2^{-1})."""
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
    """Convert an xXyY string to a numpy (n, 2) bool array."""
    return np.array([char_to_array[c] for c in s], dtype=bool)


@njit(inline='always')
def arr_to_str(arr):
    """Convert a numpy (n, 2) bool array to an xXyY string."""
    chars = [array_to_char(c[0], c[1]) for c in arr]
    return ''.join(chars)


@njit(inline='always')
def state_to_key(state):
    """Convert a (r1_arr, r2_arr) tuple to a (r1_str, r2_str) tuple."""
    return (arr_to_str(state[0]), arr_to_str(state[1]))


def canonical_pair_str(r1, r2):
    """Canonical (r1, r2) as xXyY strings (the lab's string-level wrapper)."""
    r1_arr = str_to_arr(r1)
    r2_arr = str_to_arr(r2)
    (canon_r1_arr, canon_r2_arr) = canonical_pair_nj(
        reduce_relator_nj(r1_arr), reduce_relator_nj(r2_arr))
    return arr_to_str(canon_r1_arr), arr_to_str(canon_r2_arr)


# =====================================================================
# Bridges to the env's int8 presentation and a joinable key.
# Env encoding: x->1, X->-1, y->2, Y->-2, padding 0.
# =====================================================================

INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}
CHAR_TO_INT = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}


def env_ints_to_str(ints):
    """A single relator's int8 slice (with padding zeros) -> xXyY string."""
    return ''.join(INT_TO_CHAR[int(v)] for v in ints if int(v) != 0)


def env_state_to_strs(x, max_length=24):
    """Flat env presentation array (2*max_length ints) -> (r1_str, r2_str)."""
    x = list(np.asarray(x).tolist())
    r1 = env_ints_to_str(x[:max_length])
    r2 = env_ints_to_str(x[max_length:2 * max_length])
    return r1, r2


def str_to_env_ints(s):
    """xXyY string -> list of env ints (no padding)."""
    return [CHAR_TO_INT[c] for c in s]


def strs_to_presentation_literal(r1, r2, max_length=24):
    """(r1_str, r2_str) -> flat zero-padded int list of length 2*max_length.

    Matches the literal format of data/<stem>.txt consumed by ACS.
    """
    a = str_to_env_ints(r1)
    b = str_to_env_ints(r2)
    if len(a) > max_length or len(b) > max_length:
        raise ValueError(
            f"relator longer than max_length={max_length}: "
            f"len(r1)={len(a)}, len(r2)={len(b)}")
    return a + [0] * (max_length - len(a)) + b + [0] * (max_length - len(b))


def canon_key(r1, r2, sep='|'):
    """Canonical join key for a pair of xXyY strings.

    Returns (key_str, total_len) where key_str = canon_r1 + sep + canon_r2.
    This is the cross-source dedup/merge key for greedy + beam labels.
    """
    c1, c2 = canonical_pair_str(r1, r2)
    return c1 + sep + c2, len(c1) + len(c2)
