import jax
import jax.lax as lax
import jax.numpy as jnp
from functools import partial
from envs.environment import EnvParams


def _invert(i: int, params: EnvParams, x: jnp.ndarray):
    """Inverts the ith relator."""
    max_length = params.max_length
    ith_relator = lax.dynamic_slice(x, (i*max_length,), (max_length,))
    ith_relator_inverted = jnp.where(ith_relator != 0, -_reverse_nonzero(ith_relator), jnp.int8(0))
    return jax.lax.dynamic_update_slice(x, ith_relator_inverted, (i*max_length,)) # type: ignore


# Note that if the result of a concatenation is longer than the maximum length,
# it is not stored in the relators. This is a limitation of the current implementation.
# If the result is longer than the maximum length, it is simply discarded. I don't know how to mask this action.
# Simplest thing to do is to add a negative reward if the result does not change.
# Probably also add a negative reward if there are zero simplifications.
def _concatenate(i: int, j: int, params: EnvParams, x: jnp.ndarray):
    """Concatenates the ith and jth relators."""
    max_length = params.max_length
    ith_relator = lax.dynamic_slice(x, (i*max_length,), (max_length,))
    jth_relator = lax.dynamic_slice(x, (j*max_length,), (max_length,))

    # r_i = a c, r_j = C b a #
    ith_relator_reversed = _reverse_nonzero(ith_relator) # r_i (reversed) = c a
    mask = (jth_relator == - ith_relator_reversed) # mask = (C b a == C a) = T F F

    num_cancel = jnp.argmin(mask) # 1 <-- = the number of elements that must cancel

    ith_len = jnp.count_nonzero(ith_relator)
    jth_len = jnp.count_nonzero(jth_relator)
    new_size = ith_len + jth_len - 2 * num_cancel

    def do_nothing(x, ith_relator, jth_relator, ith_len, num_cancel, new_size):
        return x

    def update_x(x, ith_relator, jth_relator, ith_len, num_cancel, new_size):

        # mask1 and mask2 specify indices of updated_ith_relator
        # where elements of ith_relator and jth_relator should be copied
        positions = jnp.arange(max_length, dtype=jnp.int8)
        mask1 = jnp.zeros_like(positions, dtype=jnp.bool_)
        mask2 = jnp.zeros_like(positions, dtype=jnp.bool_)

        # ith_len = 2, num_cancel = 1, so at position = 0, set mask1 = 1.
        # new_size = 2 + 3 - 2 = 3, ith_len = 2, num_cancel = 1
        # so for positions >= 1 and positions < 3, i.e. positions = [1, 2], set mask2=1.
        mask1 = jnp.where(positions < ith_len - num_cancel, 1, 0)
        mask2 = jnp.where(jnp.logical_and(positions >= ith_len - num_cancel, positions < new_size), 1, 0)

        # rotate jth_relator by ith_len - 2 * num_cancel = 2 - 2 = 0 elements.
        # where mask2=True, i.e. positions = [1, 2], place the first and the second element,
        # i.e. b a (skipping C as C is to be cancelled.)
        # where mask1=True, place
        updated_ith_relator = jnp.zeros_like(ith_relator)
        updated_ith_relator = jnp.where(
            mask2,
            jnp.roll(jth_relator, ith_len - 2 * num_cancel),
            jnp.where(mask1, ith_relator, 0) # type: ignore
        )

        out = jax.lax.dynamic_update_slice(x, updated_ith_relator, (i*max_length,))
        return out

    out = jax.lax.cond(
        new_size > max_length,
        do_nothing,
        update_x,
        x, ith_relator, jth_relator, ith_len, num_cancel, new_size,
    )

    out = cyclic_reduce(i, params, out)

    return out


def cyclic_reduce(i: int, params: EnvParams, x: jnp.ndarray):
    """only need to reduce one relator; the one that was just modified: labelled by i."""
    n_gen = params.n_gen
    max_length = params.max_length

    # C a b c
    ith_relator = lax.dynamic_slice(x, (i*max_length,), (max_length,)) # C a b c
    ith_relator_reversed = _reverse_nonzero(ith_relator) # c b a C

    ith_len = jnp.count_nonzero(ith_relator)

    #
    mask = (ith_relator == - ith_relator_reversed) # C a b c == C B A c --> T F F T

    # get index of the first F, eq. the total number of letters on each end to cancel
    indices = jnp.arange(max_length)
    num_cancel = jnp.min(jnp.where(~mask, indices, max_length))

    # We don't have to worry about length.
    # just copy [num_cancel: ith_len - num_cancel] = [1: 4-1] = [1: 3] = a b
    # at the beginning of the updated_ith_relator.
    rolled_indices = (indices + num_cancel) % max_length # [-1, 0, 1, 2]
    updated_ith_relator = jnp.where(
        indices >= ith_len - 2 * num_cancel, # 2, 3, ...
        jnp.zeros_like(ith_relator),
        ith_relator[rolled_indices]
    )

    out = jax.lax.dynamic_update_slice(x, updated_ith_relator, (i*max_length,))

    return out


def _reverse_nonzero(arr: jnp.ndarray):
    """Reverses the nonzero elements of the array."""
    nonzero_mask = arr != 0

    positions = jnp.arange(arr.shape[0])
    # Calculate new positions for non-zero elements
    # If the first 3 elements are non-zero in a length-5 array,
    # this maps [0,1,2,3,4] to [2,1,0,3,4]
    nonzero_count = jnp.sum(nonzero_mask)
    new_positions = jnp.where(
        nonzero_mask,
        nonzero_count - 1 - positions,
        positions
    )

    # Use the positions to create the reversed array
    reversed_arr = jnp.zeros_like(arr)
    reversed_arr = reversed_arr.at[new_positions].set(arr)

    return reversed_arr.astype(arr.dtype)


def rotate_relator_k(i: int, k: int, params, x: jnp.ndarray) -> jnp.ndarray:
    """
    Rotates the i-th relator in x left by k positions (wraps around nonzero part).
    k can be any integer (rotation wraps around).
    """
    max_length = params.max_length
    start = i * max_length
    relator = lax.dynamic_slice(x, (start,), (max_length,))
    mask = relator != 0
    length = jnp.sum(mask).astype(jnp.int32)

    def rotate_nonzero(relator, mask, k):
        k_mod = k % length
        idx = (jnp.arange(max_length) + k_mod) % length
        idx = jnp.where(mask, idx, jnp.arange(max_length))
        rotated_relator = jnp.take(relator, idx)
        return rotated_relator

    rotated = rotate_nonzero(relator, mask, k)

    out = lax.dynamic_update_slice(x, rotated, (start,))
    return out


def booth_lex_min_rotation_masked(s):
    """
    JAX-compatible Booth's algorithm that only considers non-zero prefix of s.
    Assumes that padding (zeros) is at the end.
    Returns the index of the lex smallest rotation of the non-zero prefix.
    """

    L_full = s.shape[0]
    length = jnp.sum(s != 0)
    s2 = jnp.concatenate([s, s])  # doubled string

    f = -jnp.ones(2 * L_full, dtype=jnp.int32)
    k = 0

    def body(i, val):
        f, k = val
        j = f[i - k - 1]

        def cond_fun(loop_val):
            j, k = loop_val
            ijk = k + j + 1
            # Out-of-bound comparison is always "unequal"
            valid = (i < length) & (ijk < length)
            neq = jnp.logical_or(s2[i] != s2[ijk], ~valid)
            return (j != -1) & neq

        def body_fun(loop_val):
            j, k = loop_val
            ijk = k + j + 1
            k_new = jax.lax.select(
                (ijk >= length) | (s2[i] < s2[ijk]),
                i - j - 1,
                k
            )
            j = f[j]
            return j, k_new

        j, k = jax.lax.while_loop(cond_fun, body_fun, (j, k))

        def set_f(f, i, k, j):
            ijk = k + j + 1
            neq = (s2[i] != s2[k]) | (i >= length) | (k >= length)
            f_new = jax.lax.cond(
                (j == -1) & neq,
                lambda: f.at[i - k].set(-1),
                lambda: f.at[i - k].set(j + 1),
            )
            return f_new

        f = set_f(f, i, k, j)

        def new_k_fn():
            return jax.lax.select(
                (s2[i] < s2[k]) | (k >= length),
                i,
                k
            )

        k = jax.lax.cond(
            (j == -1) & ((s2[i] != s2[k]) | (i >= length) | (k >= length)),
            new_k_fn,
            lambda: k
        )

        return f, k

    f, k = jax.lax.fori_loop(1, 2 * L_full, body, (f, k))
    return k


def s_move(i: int, params, x: jnp.ndarray, rk1k2: jnp.ndarray) -> jnp.ndarray:
    """
    S-move:
    - Optionally inverts the second relator if r == 1 (for the computation only)
    - Rotates relator 1 by k1 and relator 2 by k2 (always left)
    - Multiplies (concatenates) the two relators
    - Substitutes the result into the i-th relator in x, leaving the other unchanged
    """
    max_length = params.max_length
    r, k1, k2 = rk1k2[0], rk1k2[1], rk1k2[2] # type: ignore

    # Step 1: Optionally invert the second relator for computation only
    def maybe_invert_for_comp(x):
        return _invert(1, params, x)
    x_comp = lax.cond(r == 1, maybe_invert_for_comp, lambda x: x, x)

    # Step 2: Rotate relator 1 and relator 2 (from possibly-inverted copy)
    x1_rot = rotate_relator_k(0, k1, params, x_comp)
    x2_rot = rotate_relator_k(1, k2, params, x_comp)

    # Step 3: Extract rotated relators
    rel1 = lax.dynamic_slice(x1_rot, (0,), (max_length,))
    rel2 = lax.dynamic_slice(x2_rot, (max_length,), (max_length,))

    # Step 4: Concatenate (multiply) relators
    x_concat = _concatenate(0, 1, params, jnp.concatenate([rel1, rel2]))

    # Step 5: Substitute result into i-th relator in the ORIGINAL x
    new_relator = lax.dynamic_slice(x_concat, (0,), (max_length,))
    equal = jnp.all(new_relator == rel1)
    booth_index = booth_lex_min_rotation_masked(new_relator)

    def skip_update(_):
        return x  # return original x unchanged

    def do_update(_):
        updated = lax.cond(
            i == 0,
            lambda _: lax.dynamic_update_slice(x, new_relator, (0,)),
            lambda _: lax.dynamic_update_slice(x, new_relator, (params.max_length,)),
            operand=None
        )
        return rotate_relator_k(i, booth_index, params, updated)

    out = lax.cond(equal, skip_update, do_update, operand=None)
    return out


def setup_s_actions(params: EnvParams):
    """A helper function to package the S-move action."""
    jit_s_move = jax.jit(s_move, static_argnames=("i", "params"))
    s_moves = [partial(jit_s_move, i, params) for i in range(params.n_gen)]
    return s_moves
