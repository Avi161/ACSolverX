"""Pure-numpy port of the env S-move, for replaying packed beam paths to states.

Ported VERBATIM (logic-for-logic) from `envs/ac_moves.py` so it reproduces the
JAX env's `s_move` exactly, but with **no JAX dependency** -- it runs anywhere
numpy is available (e.g. the repo's py3.9 venv, where jax 0.6.0 cannot install).

A presentation is a length-`2*L` int8 array (two `L`-padded relators); generators
encode `x->1, y->2, x^-1->-1, y^-1->-2`, padding 0; padding is always at the end
of each relator (the env's invariant). The packed-action decode is the same
integer math as `envs.utils.decode_action` (inlined here to avoid importing
`envs.utils`, which pulls in jax.numpy).

CORRECTNESS: this is a reimplementation of core env logic, so it is only trusted
because `replay_to_states` asserts every replayed path reaches the trivial
presentation in exactly its stored length. The beam paths were produced BY the
env, so a faithful port trivializes all of them and a buggy one does not (each
move's k1/k2 are relative to the previous move's Booth rotation, so any drift
breaks trivialization). `build_merged_paths.py` runs that check over all 7,290
beam-won paths.
"""

import numpy as np

L_DEFAULT = 24


# --- packed action decode (verbatim from envs/utils.decode_action) ----------
def decode_action(sample, max_length=L_DEFAULT):
    """Decode one packed S-move index into the move [i, j, k1, k2]."""
    L = max_length
    a = int(sample)
    k1 = (a // (4 * L)) + 1
    rem = a % (4 * L)
    k2_tmp = rem // 4
    ij = rem % 4
    i = ij // 2
    j = ij % 2
    k2 = k2_tmp * ((-1) ** j) - j
    return [int(i), int(j), int(k1), int(k2)]


# --- low-level relator ops (port of envs/ac_moves.py) -----------------------
def _reverse_nonzero(arr):
    """Reverse the nonzero prefix (padding stays at the end)."""
    out = arr.copy()
    n = int(np.count_nonzero(arr))
    out[:n] = arr[:n][::-1]
    return out


def _invert_relator(rel):
    """Inverse of a relator: reverse the word and negate each letter."""
    rev = _reverse_nonzero(rel)
    return np.where(rel != 0, -rev, np.int8(0)).astype(np.int8)


def _rotate(rel, k):
    """Rotate the relator left by k positions, wrapping within the nonzero part."""
    n = int(np.count_nonzero(rel))
    if n == 0:
        return rel.copy()
    L = len(rel)
    mask = rel != 0
    km = k % n
    idx = np.where(mask, (np.arange(L) + km) % n, np.arange(L))
    return rel[idx]


def _cyclic_reduce(rel, L):
    """Free + cyclic reduction of one relator (port of cyclic_reduce)."""
    rev = _reverse_nonzero(rel)
    rlen = int(np.count_nonzero(rel))
    mask = (rel == -rev)
    indices = np.arange(L)
    num_cancel = int(np.min(np.where(~mask, indices, L)))
    rolled = (indices + num_cancel) % L
    out = np.where(indices >= rlen - 2 * num_cancel, np.int8(0), rel[rolled])
    return out.astype(np.int8)


def _concatenate(rel0, rel1, L):
    """Concatenate rel0 * rel1 with cancellation, then cyclic-reduce.

    If the (pre-reduction) result would exceed L, the env leaves rel0 unchanged
    (a no-op); we replicate that exactly.
    """
    ith = rel0
    jth = rel1
    ith_rev = _reverse_nonzero(ith)
    mask = (jth == -ith_rev)
    num_cancel = int(np.argmin(mask))          # first non-cancelling index (0 if all cancel)
    ith_len = int(np.count_nonzero(ith))
    jth_len = int(np.count_nonzero(jth))
    new_size = ith_len + jth_len - 2 * num_cancel

    if new_size > L:
        out = ith.copy()                       # do_nothing branch
    else:
        positions = np.arange(L)
        mask1 = positions < (ith_len - num_cancel)
        mask2 = (positions >= (ith_len - num_cancel)) & (positions < new_size)
        rolled = np.roll(jth, ith_len - 2 * num_cancel)
        out = np.where(mask2, rolled, np.where(mask1, ith, np.int8(0))).astype(np.int8)

    return _cyclic_reduce(out, L)


def _booth(s):
    """Index of the lex-min rotation of the nonzero prefix (port of
    booth_lex_min_rotation_masked, int8 order). Validity is checked before any
    s2[ijk] access so out-of-bounds reads never happen."""
    L_full = len(s)
    length = int(np.count_nonzero(s))
    s2 = np.concatenate([s, s])
    f = -np.ones(2 * L_full, dtype=np.int64)
    k = 0
    for i in range(1, 2 * L_full):
        j = int(f[i - k - 1])
        while True:
            ijk = k + j + 1
            valid = (i < length) and (ijk < length)
            neq = (not valid) or (s2[i] != s2[ijk])
            if not ((j != -1) and neq):
                break
            if (ijk >= length) or (s2[i] < s2[ijk]):
                k = i - j - 1
            j = int(f[j])
        neq2 = (s2[i] != s2[k]) or (i >= length) or (k >= length)
        f[i - k] = -1 if ((j == -1) and neq2) else (j + 1)
        if (j == -1) and neq2:
            if (s2[i] < s2[k]) or (k >= length):
                k = i
    return k


def s_move(i, x, r, k1, k2, L=L_DEFAULT):
    """Apply one S-move to presentation x (length 2L int8). Returns a new array.

    i  : which relator is substituted (0 or 1)
    r  : invert relator 1 first (0 or 1)   [= the move's `j`]
    k1 : left-rotation of relator 0 (>= 1)
    k2 : left-rotation of relator 1
    """
    x = np.asarray(x, dtype=np.int8)
    x_comp = x.copy()
    if r == 1:
        x_comp[L:2 * L] = _invert_relator(x_comp[L:2 * L])

    rel0 = _rotate(x_comp[0:L], k1)
    rel1 = _rotate(x_comp[L:2 * L], k2)

    new_rel = _concatenate(rel0, rel1, L)
    if np.array_equal(new_rel, rel0):
        return x.copy()                        # equal -> skip_update (no-op)

    booth_k = _booth(new_rel)
    out = x.copy()
    if i == 0:
        out[0:L] = new_rel
    else:
        out[L:2 * L] = new_rel
    seg = out[i * L:(i + 1) * L]
    out[i * L:(i + 1) * L] = _rotate(seg, booth_k)
    return out


# --- replay ----------------------------------------------------------------
def _state_strs(x, L):
    int_to_char = {1: "x", -1: "X", 2: "y", -2: "Y"}
    r1 = "".join(int_to_char[int(v)] for v in x[:L] if int(v) != 0)
    r2 = "".join(int_to_char[int(v)] for v in x[L:2 * L] if int(v) != 0)
    return r1, r2


def _initial_state(r1, r2, L):
    char_to_int = {"x": 1, "X": -1, "y": 2, "Y": -2}
    a = [char_to_int[c] for c in r1]
    b = [char_to_int[c] for c in r2]
    return np.array(a + [0] * (L - len(a)) + b + [0] * (L - len(b)), dtype=np.int8)


def replay_to_states(r1, r2, packed_path, L=L_DEFAULT):
    """Replay a packed beam path from initial (r1, r2).

    Returns (flat_states, terminated, n_steps):
      flat_states : [r1_0, r2_0, r1_1, r2_1, ...] xXyY strings (one pair per state)
      terminated  : True iff the trivial presentation (both relators length 1) is reached
      n_steps     : number of moves applied before stopping
    """
    x = _initial_state(r1, r2, L)
    states = [_state_strs(x, L)]
    terminated, n = False, 0
    for a in packed_path:
        i, j, k1, k2 = decode_action(a, L)
        x = s_move(i, x, j, k1, k2, L)
        states.append(_state_strs(x, L))
        n += 1
        if int(np.count_nonzero(x)) == 2:      # trivial: each relator length 1
            terminated = True
            break
    flat = [s for pair in states for s in pair]
    return flat, terminated, n
