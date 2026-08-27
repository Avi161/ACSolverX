"""Scalar pure-Python transliteration of `envs/ac_moves.py` and `envs/ac_s.py`.

Test support only. It exists so the batched torch env can be checked against the
JAX source **line by line, without installing JAX** -- which matters because the
cross-framework gate can only run on Colab, and a port should not go a whole
session unverified waiting for a GPU.

Written deliberately as a literal transcription: `jnp.where` becomes a list
comprehension, `jnp.roll` becomes an index rotation, the `argmin` over a boolean
mask keeps its "0 when nothing is False" behaviour. It is slow and it repeats
itself, and both are the point -- it must not share structure with
`acs_moves.py`, or agreement between them would prove nothing.
"""

from experiments.ppo.booth_spec import booth_lex_min_rotation_masked


def reverse_nonzero(arr):
    n = sum(1 for v in arr if v != 0)
    return list(arr[:n])[::-1] + list(arr[n:])


def cyclic_reduce(rel, max_length):
    rev = reverse_nonzero(rel)
    mask = [rel[p] == -rev[p] for p in range(max_length)]
    num_cancel = min([p for p in range(max_length) if not mask[p]] + [max_length])
    rlen = sum(1 for v in rel if v != 0)
    out = []
    for p in range(max_length):
        out.append(0 if p >= rlen - 2 * num_cancel else rel[(p + num_cancel) % max_length])
    return out


def concatenate(ri, rj, max_length):
    """`_concatenate(0, 1, ...)` on `[ri | rj]`, returning relator 0."""
    ri_rev = reverse_nonzero(ri)
    mask = [rj[p] == -ri_rev[p] for p in range(max_length)]
    falses = [p for p in range(max_length) if not mask[p]]
    num_cancel = falses[0] if falses else 0        # jnp.argmin over an all-True mask -> 0

    ith_len = sum(1 for v in ri if v != 0)
    jth_len = sum(1 for v in rj if v != 0)
    new_size = ith_len + jth_len - 2 * num_cancel

    if new_size > max_length:
        return cyclic_reduce(list(ri), max_length)

    shift = ith_len - 2 * num_cancel
    rolled = [rj[(p - shift) % max_length] for p in range(max_length)]
    out = []
    for p in range(max_length):
        if ith_len - num_cancel <= p < new_size:
            out.append(rolled[p])
        elif p < ith_len - num_cancel:
            out.append(ri[p])
        else:
            out.append(0)
    return cyclic_reduce(out, max_length)


def rotate_k(rel, k, max_length):
    length = sum(1 for v in rel if v != 0)
    if length == 0:
        return list(rel)
    km = k % length
    return [rel[(p + km) % length] if rel[p] != 0 else rel[p] for p in range(max_length)]


def s_move(x, i, r, k1, k2, max_length):
    L = max_length
    rel0, rel1 = list(x[:L]), list(x[L:])
    if r == 1:
        rel1 = [-v for v in reverse_nonzero(rel1)]

    a = rotate_k(rel0, k1, L)
    b = rotate_k(rel1, k2, L)
    new_rel = concatenate(a, b, L)
    if new_rel == a:
        return list(x)

    rotated = rotate_k(new_rel, booth_lex_min_rotation_masked(new_rel), L)
    if i == 0:
        return rotated + list(x[L:])
    return list(x[:L]) + rotated


def decode_action(flat, max_length):
    L = max_length
    k1 = flat // (4 * L) + 1
    rem = flat % (4 * L)
    k2_tmp = rem // 4
    ij = rem % 4
    i, j = ij // 2, ij % 2
    return i, j, k1, k2_tmp * (-1) ** j - j


def step(x, flat_action, max_length=24, n_gen=2):
    """`ACS.step_env` with the baseline (zero-penalty) reward."""
    i, r, k1, k2 = decode_action(flat_action, max_length)
    new_x = s_move(x, i, r, k1, k2, max_length)
    nnz = sum(1 for v in new_x if v != 0)
    terminated = nnz == n_gen
    reward = 1000.0 if terminated else -float(min(nnz, 10))
    return new_x, reward, terminated
