from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import chex
from flax import struct
import jax
from jax import lax
import jax.numpy as jnp
from gymnax.environments import spaces

from envs import int_box
from envs import environment
from envs.utils import change_max_relator_length_of_presentation
from envs.ac_moves import setup_s_actions
from ast import literal_eval


@struct.dataclass
class EnvState(environment.EnvState):
    x: jnp.array  # presentation
    sample: bool
    idx: int
    time: int
    # Per-episode visited-state hash buffer for cycle detection.
    # Sentinel-padded with int32.max; visited_hashes[t] is the hash of the
    # state at time t (visited_hashes[0] = hash of init).
    visited_hashes: jnp.ndarray


@struct.dataclass
class EnvParams(environment.EnvParams):
    n_gen: int = 2
    max_length: int = 64
    max_steps_in_episode: int = 200


class ACS(environment.Environment):

    def __init__(self, n_gen=2, max_length=64, max_steps_in_episode=200,
                 is_reward_sparse=False, initial_states_file="all_presentations",
                 cycle_penalty=0.0, noop_penalty=0.0):
        super().__init__()
        self.params = EnvParams(n_gen=n_gen, max_length=max_length, max_steps_in_episode=max_steps_in_episode)
        self.init_states = self.initiate_states(self.params, initial_states_file)
        # Initialize sampling probabilities over initial states (uniform by default)
        self.num_states = int(self.init_states.shape[0])
        self._actions = setup_s_actions(self.params)
        self.reward_fn = self.get_reward_fn(is_reward_sparse)
        # Reward shaping: penalties subtracted per step (only when non-terminal).
        self.cycle_penalty = float(cycle_penalty)
        self.noop_penalty = float(noop_penalty)
        # Fixed pseudo-random hash vector for state hashing (per-episode cycle
        # detection). Same hash for same state across all envs/episodes.
        obs_len = n_gen * max_length
        self.hash_vec = jax.random.randint(
            jax.random.PRNGKey(0xC0FFEE),
            (obs_len,),
            minval=-(2**31), maxval=2**31 - 1, dtype=jnp.int32,
        )
        self.HASH_SENTINEL = jnp.iinfo(jnp.int32).max
        self.visited_buf_size = max_steps_in_episode + 1
        print(f"Loading {len(self.init_states)} states.. cycle_penalty={cycle_penalty} noop_penalty={noop_penalty}")

    def _hash_state(self, x):
        return jnp.sum(x.astype(jnp.int32) * self.hash_vec)

    def initiate_states(self, params: EnvParams, initial_states_file: str):
        with open(f"data/{initial_states_file}.txt", "r") as file:
            initial_states = [literal_eval(line.strip()) for line in file]
        initial_states = [change_max_relator_length_of_presentation(state, params.max_length) for state in initial_states]
        return jnp.array(initial_states)

    def get_reward_fn(self, is_sparse: bool):
        if is_sparse:
            return lambda x, terminated: jnp.array(terminated, int)
        else:
            print(f"Using dense reward function. You may want to clip and normalize the reward.")
            return lambda x, terminated: -jnp.clip(jnp.count_nonzero(x), 0, 10) * (1-terminated) + 1000 * terminated

    @property
    def default_params(self) -> EnvParams:
        return self.params

    def step_env(
        self,
        key: chex.PRNGKey,
        state: EnvState,
        action: Union[int, float, chex.Array],
        params: EnvParams,
    ) -> Tuple[chex.Array, EnvState, jnp.ndarray, jnp.ndarray, Dict[Any, Any]]:
        """Performs step transitions in the environment.
        Action is expected to be [i, r, k1, k2].
        """
        # Call jit_s_move to get the new x
        new_x = jax.lax.switch(action[0], self._actions, state.x, action[1:])

        # Cycle / noop detection (only used if penalties are non-zero, but
        # always tracked so EnvState shape is consistent).
        new_hash = self._hash_state(new_x)
        already_visited = jnp.any(state.visited_hashes == new_hash)
        is_noop = jnp.all(new_x == state.x)
        new_visited = state.visited_hashes.at[state.time + 1].set(new_hash)

        # Update state
        state = EnvState(
            x=new_x,
            idx=state.idx,
            sample=state.sample,
            time=state.time + 1,
            visited_hashes=new_visited,
        )
        terminated = jnp.count_nonzero(state.x) == params.n_gen
        truncated = state.time >= params.max_steps_in_episode
        done = jnp.logical_or(terminated, truncated)
        base_reward = self.reward_fn(state.x, terminated)
        # Subtract penalties on non-terminal steps; terminal +1000 stays clean.
        non_term = (1 - terminated).astype(jnp.float32)
        penalty = (already_visited.astype(jnp.float32) * self.cycle_penalty
                   + is_noop.astype(jnp.float32) * self.noop_penalty) * non_term
        reward = base_reward - penalty

        return (
            lax.stop_gradient(self.get_obs(state)),
            lax.stop_gradient(state),
            jnp.array(reward),
            done,
            {
                "discount": self.discount(state, params),
                "terminated": terminated,
                "truncated": truncated,
                "idx": state.idx,
                "length": jnp.count_nonzero(state.x),
                "episode_length": state.time,
                "cycle_hit": already_visited,
                "noop_hit": is_noop,
            },
        )

    def is_terminal(self, state: EnvState, params: EnvParams) -> jnp.ndarray:
        """Check whether state transition is terminal."""
        terminated = jnp.count_nonzero(state.x) == params.n_gen
        truncated = state.time >= params.max_steps_in_episode
        done = jnp.logical_or(terminated, truncated)
        return done

    def reset_env(
        self, key: chex.PRNGKey, params: EnvParams, idx: Optional[int] = None, sample: bool = False, probs: Optional[jnp.ndarray] = None
    ) -> Tuple[chex.Array, EnvState]:
        """Performs resetting of environment.

        If sample is True, sample an initial state according to probs.
        If sample is False, reset deterministically to init_states[idx] (bounds are not checked).
        """
        if probs is None:
            probs = jnp.full((self.num_states,), 1.0 / max(self.num_states, 1), dtype=jnp.float32)

        def sample_state(_):
            return jax.random.choice(key, self.num_states, p=probs)

        def fixed_state(i):
            return i

        sample_idx = jax.lax.cond(sample, sample_state, fixed_state, idx)
        init_x = self.init_states[sample_idx]
        visited = jnp.full((self.visited_buf_size,), self.HASH_SENTINEL, dtype=jnp.int32)
        visited = visited.at[0].set(self._hash_state(init_x))
        state = EnvState(x=init_x, idx=sample_idx, sample=sample, time=0,
                         visited_hashes=visited)
        return self.get_obs(state), state

    def get_obs(self, state: EnvState, params=None, key=None) -> chex.Array:
        """Applies observation function to state."""
        return state.x

    @property
    def name(self) -> str:
        """Environment name."""
        return "ACS-v0"

    @property
    def num_actions(self) -> int:
        """Number of actions possible in environment."""
        # For S-moves: n_gen * 2 * max_length * max_length
        return self.params.n_gen * 2 * self.params.max_length * self.params.max_length

    def action_space(self, params: Optional[EnvParams] = None) -> spaces.Box:
        """Action space of the environment: [i, r, k1, k2]."""
        p = params if params is not None else self.params
        return spaces.Box(
            low=jnp.array([0, 0, 0, 0]),
            high=jnp.array([p.n_gen - 1, 1, p.max_length - 1, p.max_length - 1]),
            shape=(4,),
            dtype=jnp.int32
        )

    def observation_space(self, params: EnvParams) -> spaces.Box:
        """Observation space of the environment."""
        arr_len = params.max_length * params.n_gen
        low = jnp.ones(arr_len, dtype=jnp.int8) * (-params.n_gen)
        high = np.ones(arr_len, dtype=jnp.int8) * (params.n_gen)
        return int_box.IntBox(low, high, shape=(arr_len,), dtype=jnp.int8)
