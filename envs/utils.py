import numpy as np
import jax.numpy as jnp


def convert_relators_to_presentation(relator1, relator2, max_relator_length):
    """
    Converts two lists representing relators into a single numpy array, padding each relator with zeros
    to match the specified maximum length.

    Parameters:
    relator1 (list of int): The first relator, must not contain zeros.
    relator2 (list of int): The second relator, must not contain zeros.
    max_relator_length (int): The maximum allowed length for each relator.

    Returns:
    jnp.ndarray: A numpy array of dtype int8, containing the two relators concatenated and zero-padded to max_length.
    """

    # Ensure relators do not contain zeros and max_relator_length is sufficient
    assert (
        0 not in relator1 and 0 not in relator2
    ), "relator1 and relator2 must not be padded with zeros."
    assert max_relator_length >= max(
        len(relator1), len(relator2)
    ), "max_relator_length must be greater than or equal to the lengths of relator1 and rel2."
    assert isinstance(relator1, list) and isinstance(
        relator2, list
    ), f"got types {type(relator1)} for relator1 and {type(relator2)} for relator2"

    padded_relator1 = relator1 + [0] * (max_relator_length - len(relator1))
    padded_relator2 = relator2 + [0] * (max_relator_length - len(relator2))

    return np.array(padded_relator1 + padded_relator2, dtype=jnp.int8)


def change_max_relator_length_of_presentation(presentation, new_max_length):
    """
    Adjusts the maximum length of the relators in a given presentation by reformatting it
    with a new specified maximum length.

    Parameters:
    presentation (Numpy Array): The current presentation as a list, where relators are concatenated and padded with zeros.
    new_max_length (int): The new maximum length for each relator in the presentation.

    Returns:
    Numpy Array: The new presentation with relators adjusted to the specified maximum length.
    """

    old_max_length = len(presentation) // 2

    first_word_length = np.count_nonzero(presentation[:old_max_length])
    second_word_length = np.count_nonzero(presentation[old_max_length:])

    relator1 = presentation[:first_word_length]
    relator2 = presentation[old_max_length : old_max_length + second_word_length]

    new_presentation = convert_relators_to_presentation(
        relator1=relator1, relator2=relator2, max_relator_length=new_max_length
    )
    return new_presentation


# --- S-move action (un)packing ---------------------------------------------
# Paths are stored as a single packed integer per move (see
# wrappers.LogPathsProbsS.encode_action and the policy head in
# network.RelativeDualRingActorCritic), using L = max_length (24 in the
# training/beam scripts):
#
#     sample = (((k1 - 1) * L + (k2 + j) * (-1)**j) * 4) + (i * 2 + j)
#
# where the unpacked move is [i, j, k1, k2]:
#   i  : which relator is substituted (0 or 1)
#   j  : whether the other relator is inverted first (0 or 1)
#   k1 : cyclic rotation of relator 0 (>= 1)
#   k2 : cyclic rotation of relator 1
# The functions below are the exact inverse used in ppo_ac_s.py / beam_search.py.

def encode_action(action, max_length=24):
    """Pack a move [i, j, k1, k2] into its stored integer index."""
    i, j, k1, k2 = (int(action[0]), int(action[1]), int(action[2]), int(action[3]))
    L = max_length
    return (((k1 - 1) * L + (k2 + j) * (-1) ** j) * 4) + (i * 2 + j)


def decode_action(sample, max_length=24):
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


def decode_path(path, max_length=24, pad_value=-1):
    """Decode a stored path of packed S-move indices into a list of
    [i, j, k1, k2] moves.

    `path` is an iterable of packed integers (e.g. a row of
    env_state.best_paths). Padding entries equal to `pad_value` are dropped, so
    a fixed-width padded row decodes to just its real moves.
    """
    return [decode_action(a, max_length) for a in path if int(a) != pad_value]


# --- Path validation --------------------------------------------------------
def replay_packed_path(env, idx, packed_path, max_length=24):
    """Replay one stored (packed) path in an ACS env from initial state `idx`.

    `packed_path` is a sequence of packed action indices (e.g. a row of
    env_state.best_paths), -1-padded. Returns (terminated, n_steps, final_x):
      terminated : True iff a trivial presentation was reached
      n_steps    : number of moves applied before stopping
      final_x    : the final presentation as a numpy array
    """
    import jax
    import jax.numpy as jnp

    params = env.default_params
    key = jax.random.PRNGKey(0)
    _, state = env.reset_env(key, params,
                             idx=jnp.int32(int(idx)),
                             sample=jnp.bool_(False))
    terminated = False
    n_steps = 0
    for move in decode_path(packed_path, max_length=max_length):
        _, state, _, _, info = env.step_env(
            key, state, jnp.asarray(move, dtype=jnp.int32), params
        )
        n_steps += 1
        terminated = bool(info["terminated"])
        if terminated:
            break
    return terminated, n_steps, np.asarray(state.x)


def check_paths(solved_idx, path_lengths, best_paths, initial_states_file,
                max_length=24, max_paths=None, verbose=True):
    """Validate stored substitution paths by replaying them in the ACS env.

    For every index flagged in `solved_idx`, replays best_paths[idx] starting
    from init_states[idx] of `initial_states_file` and checks that it reaches
    the trivial presentation in exactly path_lengths[idx] moves.

    `solved_idx`, `path_lengths`, `best_paths` are the arrays held in
    env_state.solved_idx / .path_lengths / .best_paths (and saved in an Orbax
    checkpoint's solve_data). best_paths holds packed action indices padded
    with -1.

    `max_paths` (optional) caps how many solved paths are checked (the first
    `max_paths` solved indices); None checks all of them.

    Returns the list of indices that FAILED to validate (empty => all good).
    """
    # Lazy import: ac_s imports this module, so importing it at top level would
    # create a circular import.
    from envs.ac_s import ACS

    solved_idx = np.asarray(solved_idx)
    path_lengths = np.asarray(path_lengths)
    best_paths = np.asarray(best_paths)

    # Size max_steps to the stored path width so episodes never truncate before
    # a path finishes; truncation would not affect the terminal check anyway.
    max_steps = int(best_paths.shape[1])
    env = ACS(n_gen=2, max_length=max_length, max_steps_in_episode=max_steps,
              is_reward_sparse=False, initial_states_file=initial_states_file)

    failures = []
    solved_indices = np.nonzero(solved_idx)[0]
    if max_paths is not None:
        solved_indices = solved_indices[:max_paths]
    for idx in solved_indices:
        terminated, n_steps, _ = replay_packed_path(
            env, idx, best_paths[idx], max_length=max_length
        )
        expected = int(path_lengths[idx])
        if not (terminated and n_steps == expected):
            failures.append(int(idx))
            if verbose:
                print(f"[idx {idx}] INVALID: terminated={terminated}, "
                      f"replay_steps={n_steps}, stored_length={expected}")
    if verbose:
        n = len(solved_indices)
        print(f"checked {n} solved paths: {n - len(failures)} valid, "
              f"{len(failures)} invalid")
    return failures
