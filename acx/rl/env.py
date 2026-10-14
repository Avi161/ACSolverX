"""Batched Two-Hump environment (the PPO stack's ``ACS`` plus its reward wrappers) in PyTorch, reduced to training.

* State: ``(num_envs, 2L)`` presentations; an episode ends when both relators have length 1 (reward 1000) or after
  ``max_steps`` (96). Dense reward ``-min(#letters, 10)`` per step.
* The first ``n_pinned`` envs keep their initial state forever (one per Miller-Schupp target of the training set);
  the others re-sample on reset with probability ``~ (1 - success)/sqrt(1 + attempts)``.
* The reward is normalised PER ENV by the running std of its own discounted return. Cycle and no-op penalties are off.
"""
import torch

from ..core.config import is_finite_number, require_int
from .moves import decode_action, s_move


class VecEnv:
    """``num_envs`` environments over the initial states ``init_states``, stepped together."""

    def __init__(self, init_states, num_envs, *, L=24, max_steps=96, gamma=0.999, n_pinned=0, seed=0):
        for key, value in (("num_envs", num_envs), ("L", L), ("max_steps", max_steps)):
            require_int(value, key)
        require_int(n_pinned, "n_pinned", low=0)
        if not is_finite_number(gamma) or not 0 <= gamma <= 1:
            raise ValueError("gamma must be a finite number in [0, 1]")
        self.L, self.max_steps, self.gamma, self.N = L, max_steps, gamma, num_envs
        states = torch.as_tensor(init_states)
        if states.ndim != 2 or states.shape[1] != 2 * L or len(states) == 0:
            raise ValueError(f"init_states must be a nonempty (S, {2 * L}) array")
        if states.dtype == torch.bool or states.is_floating_point() or states.is_complex():
            raise ValueError("init_states must contain integer generator symbols")
        # abs(minimum_signed_integer) overflows back to a negative number; compare bounds directly.
        if (states > 2).any() or (states.is_signed() and (states < -2).any()):
            raise ValueError("init_states must contain only -2, -1, 0, 1, 2")
        self.init = states.to(dtype=torch.int64)
        self.S = len(self.init)
        if n_pinned > min(num_envs, self.S):
            raise ValueError("n_pinned must not exceed num_envs or the number of initial states")
        self.gen = torch.Generator().manual_seed(seed)
        self.pinned = torch.arange(num_envs) < n_pinned
        self.idx = torch.arange(num_envs) % self.S
        self.x, self.time = self.init[self.idx].clone(), torch.zeros(num_envs, dtype=torch.int64)
        self.ret, self.mean = torch.zeros(num_envs), torch.zeros(num_envs)
        self.var, self.count = torch.ones(num_envs), torch.full((num_envs,), 1e-4)
        self.solves, self.attempts = torch.zeros(self.S), torch.zeros(self.S)
        self.solved = torch.zeros(self.S, dtype=torch.bool)

    def step(self, action):
        """Returns ``(obs, normalised reward, done, terminated)``; done envs are already reset."""
        self.x = s_move(self.x, *decode_action(action, self.L), self.L)[0]
        self.time += 1
        nnz = (self.x != 0).sum(-1)
        terminated, done = nnz == 2, (nnz == 2) | (self.time >= self.max_steps)
        reward = torch.where(terminated, 1000.0, -nnz.clamp(max=10).float())
        reward = self._normalise(reward, done)
        self._reset(done, terminated)
        return self.x, reward, done, terminated

    def _normalise(self, reward, done):
        """Divide each env's reward by the running std of its discounted return.

        Exactly the JAX ``NormalizeVecReward`` that trained the shipped weights, quirks kept: a step's own ``done``
        clears the return before its reward is added, and each update weighs ``2L`` (the observation length)."""
        raw, bc = reward, float(2 * self.L)
        self.ret = self.ret * self.gamma * (~done) + raw
        delta, tot = self.ret - self.mean, self.count + bc
        self.mean = self.mean + delta * bc / tot
        self.var = (self.var * self.count + delta.square() * self.count * bc / tot) / tot
        self.count = tot
        return raw / torch.sqrt(self.var + 1e-8)

    def _reset(self, done, terminated):
        """Re-sample the unpinned envs that finished (harder rows more often) and restart their clocks."""
        if not done.any():
            return
        self.solves.index_add_(0, self.idx, terminated.float())
        self.attempts.index_add_(0, self.idx, done.float())
        self.solved[self.idx[terminated]] = True
        p = (1 - self.solves / (self.attempts + 5)) / (1 + self.attempts).sqrt()
        draw = torch.searchsorted(p.cumsum(0), torch.rand(self.N, generator=self.gen) * p.sum()).clamp(max=self.S - 1)
        self.idx = torch.where(done & ~self.pinned, draw, self.idx)
        self.x = torch.where(done[:, None], self.init[self.idx], self.x)
        self.time = torch.where(done, torch.zeros_like(self.time), self.time)
