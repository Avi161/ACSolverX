import jax
from typing import Any, Union
import jax.numpy as jnp
import chex
from gymnax.environments import spaces

class IntBox(spaces.Space):
    """Minimal jittable class for array-shaped gymnax spaces with integer elements."""

    def __init__(
        self,
        low: Union[jnp.ndarray, int],
        high: Union[jnp.ndarray, int],
        shape: Any, # Tuple[int],
        dtype: jnp.dtype = jnp.int_
    ):
        self.low = low # inclusive
        self.high = high # inclusive
        self.shape = shape
        self.dtype = dtype

    def sample(self, rng: chex.PRNGKey) -> chex.Array:
        """Sample random element uniformly from integers"""
        return jax.random.randint( # maxval has +1 as it expects exclusive
            rng, shape=self.shape, minval=self.low, maxval=self.high+1
        ).astype(self.dtype)
    
    def contains(self, x: chex.Array) -> jnp.ndarray:
        """Check whether specific object is within space."""
        # type_cond = isinstance(x, self.dtype)
        # shape_cond = (x.shape == self.shape)
        range_cond = jnp.logical_and(jnp.all(x >= self.low), jnp.all(x <= self.high))
        return range_cond