"""Batched Two-Hump environment (``ACS`` plus its wrapper stack) in PyTorch.

Port of ``envs/ac_s.py`` with ``LogWrapper -> NormalizeVecReward -> LogPathsProbsS``
(``origin/experiments/ppo:experiments/ppo/acs_env.py``, tip c73b11f2), reduced to what training needs.

* State: ``(num_envs, 2L)`` presentations; an episode ends when both relators have length 1
  (reward 1000) or after ``max_steps`` (96). Dense reward ``-min(#letters, 10)`` per step.
* The first ``n_pinned`` envs keep their initial state forever (one per Miller-Schupp target of the
  training set: 634 for ``AC19_extended``, which opens with the first 634 rows of ``1190MS``); the
  others re-sample on reset with probability ``~ (1 - success)/sqrt(1 + attempts)``.
* ``NormalizeVecReward`` runs inside the vmap upstream, so it is PER ENV with ``batch_count = 2L``
  and zero batch variance: each env divides by the running std of its own discounted return.
* Cycle and no-op penalties are off in the baseline and not ported; the cycle-hash RNG could not be
  reproduced outside JAX anyway.
"""
import torch

from .moves import decode_action, s_move


class VecEnv:
    def __init__(self, init_states, num_envs, *, L=24, max_steps=96, gamma=0.999, n_pinned=0, seed=0):
        self.L, self.max_steps, self.gamma, self.N = L, max_steps, gamma, num_envs
        self.init = torch.as_tensor(init_states, dtype=torch.int64)
        self.S = len(self.init)
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
        raw, bc = reward, float(2 * self.L)
        self.ret = self.ret * self.gamma * (~done) + raw
        delta, tot = self.ret - self.mean, self.count + bc
        self.mean = self.mean + delta * bc / tot
        self.var = (self.var * self.count + delta.square() * self.count * bc / tot) / tot
        self.count = tot
        return raw / torch.sqrt(self.var + 1e-8)

    def _reset(self, done, terminated):
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
