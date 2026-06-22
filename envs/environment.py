"""Abstract base class for all gymnax Environments."""

import functools
from typing import Any, Dict, Optional, Tuple, TypeVar, Union
import chex
import jax
import jax.numpy as jnp
from gymnax.environments import environment

TEnvState = TypeVar("TEnvState", bound="EnvState")
TEnvParams = TypeVar("TEnvParams", bound="EnvParams")

EnvState = environment.EnvState
EnvParams = environment.EnvParams

class Environment(environment.Environment):  # object):
    """Jittable abstract base class for all gymnax Environments.
    Essentially, the same as environment.Environment, the only differences
    are that reset and reset_env methods take idx as input, where 
    idx is the index of an initial state (possibly from some dataset specified by
    the user)."""

    @property
    def default_params(self) -> EnvParams:
        return EnvParams()

    @functools.partial(jax.jit, static_argnums=(0,))
    def step(
        self,
        key: chex.PRNGKey,
        state: TEnvState,
        action: Union[int, float, chex.Array],
        params: Optional[TEnvParams] = None,
        probs: Optional[jnp.ndarray] = None
    ) -> Tuple[chex.Array, TEnvState, jnp.ndarray, jnp.ndarray, Dict[Any, Any]]:
        """Performs step transitions in the environment."""
        # Use default env parameters if no others specified
        if params is None:
            params = self.default_params
        key, key_reset = jax.random.split(key)
        obs_st, state_st, reward, done, info = self.step_env(key, state, action, params)
        obs_re, state_re = self.reset_env(key_reset, params, state_st.idx, state_st.sample, probs) #This is a little bad, since state_st.sampel is not in the EnvState base class, but it is in the ac_s EnvState, so it should work for now. We can think about how to make it better later
        # Auto-reset environment based on termination
        state = jax.tree.map(
            lambda x, y: jax.lax.select(done, x, y), state_re, state_st
        )
        obs = jax.lax.select(done, obs_re, obs_st)
        return obs, state, reward, done, info

    @functools.partial(jax.jit, static_argnums=(0,))
    def reset(
        self, key: chex.PRNGKey, params: Optional[TEnvParams] = None, idx: int = 0, sample: bool = False ,probs: Optional[jnp.ndarray] = None
    ) -> Tuple[chex.Array, TEnvState]:
        """Performs resetting of environment."""
        # Use default env parameters if no others specified
        if params is None:
            params = self.default_params
        obs, state = self.reset_env(key, params, idx, sample, probs)
        return obs, state

    def reset_env(
        self, key: chex.PRNGKey, params: TEnvParams, idx: int = 0, sample: bool = False, probs: Optional[jnp.ndarray] = None
    ) -> Tuple[chex.Array, TEnvState]:
        """Environment-specific reset."""
        raise NotImplementedError