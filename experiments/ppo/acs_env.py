"""Batched ACS environment in PyTorch, with the wrapper stack folded in.

Ports `envs/ac_s.py` (`ACS`) plus, in one class, the three wrappers
`ppo_ac_s.py` puts around it: `LogWrapper` -> `NormalizeVecReward(GAMMA)` ->
`LogPathsProbsS(NUM_ENVS)`. They are fused because their JAX composition is not
the composition it looks like, and splitting them would invite reintroducing the
bug they encode:

**`NormalizeVecReward` runs *inside* the vmap, so it is per-env, not per-batch.**
`LogPathsProbsS.__init__` vmaps `self._env.step`, and `self._env` is the
normalizer. Under that vmap, `obs.shape[0]` is 48 (the observation length), not
the number of envs -- so each env carries its own Welford `(mean, var, count)`,
each update contributes `batch_count = 48` with `batch_var = 0` (48 copies of
one scalar), and every reward is divided by that env's *own* running std. It is
not the batch-level normalizer the class name suggests. Reproduced exactly.

Ordering inside `step` matters and follows the JAX call graph:
  1. `ACS.step_env` -> new x, reward, done, and an `info` describing the episode
     that just ended (its `idx`, its `terminated`, its length);
  2. `Environment.step`'s auto-reset overwrites the state of every done env,
     sampling with the sampling distribution from *before* this step;
  3. the normalizer consumes the raw reward and `done`;
  4. the path/probability logger consumes the pre-reset `info` and only then
     updates the sampling distribution.

Two documented divergences from JAX, both inert for the baseline config:

- `hash_vec` cannot be reproduced without JAX (`jax.random.randint` under
  `PRNGKey(0xC0FFEE)`), so `cycle_hit` is computed against a torch-seeded vector
  instead. It feeds nothing but a logged rate while `cycle_penalty == 0.0`,
  which is the baseline. `noop_hit` is exact -- it is a plain state comparison.
- An env whose relator empties out divides by zero inside JAX's `rotate` and
  `rel_dist` modulo. `acs_moves.rotate_k` clamps, which lands on the same state;
  the network's relative-distance gather clamps too, which does not, so a
  presentation that empties a relator mid-episode is outside parity. Nothing
  bounds it away -- it is just rare.
"""

import numpy as np
import torch

from experiments.ppo import shaping
from experiments.ppo.acs_moves import decode_action, s_move

INT32_MAX = 2 ** 31 - 1


class VecACS:
    """`NUM_ENVS` copies of `ACS`, stepped together on one device."""

    def __init__(self, init_states, num_envs, *, n_gen=2, max_length=24,
                 max_steps=96, gamma=0.999, cycle_penalty=0.0, noop_penalty=0.0,
                 n_pinned=0, device="cpu", seed=0, track_paths=True,
                 shaping=None, lam=0.0):
        self.device = torch.device(device)
        self.n_gen = n_gen
        self.L = max_length
        self.obs_len = n_gen * max_length
        self.max_steps = max_steps
        self.num_envs = num_envs
        self.gamma = float(gamma)
        self.cycle_penalty = float(cycle_penalty)
        self.noop_penalty = float(noop_penalty)
        self.track_paths = track_paths
        self.n_actions = n_gen * 2 * max_length * max_length
        # Reward shaping is OFF unless both are set, and `lam = 0` is a hard zero
        # rather than a small number -- the control arm must be bit-identical to the
        # unshaped baseline, not merely close to it. See `shaping.py`.
        self.shaping = shaping
        self.lam = float(lam)

        self.init_states = torch.as_tensor(np.asarray(init_states), dtype=torch.int64, device=self.device)
        if self.init_states.shape[1] != self.obs_len:
            raise ValueError(f"init_states have width {self.init_states.shape[1]}, expected {self.obs_len}")
        self.num_states = int(self.init_states.shape[0])

        self.gen = torch.Generator(device=self.device)
        self.gen.manual_seed(int(seed))
        # See the module docstring: not the JAX vector, and inert at zero penalty.
        self.hash_vec = torch.randint(-(2 ** 31), 2 ** 31 - 1, (self.obs_len,),
                                      generator=self.gen, device=self.device, dtype=torch.int64).to(torch.int32)

        self.beta, self.alpha = 5, 1
        self.n_pinned = int(n_pinned)
        self.reset(n_pinned=self.n_pinned)

    # -- reset ---------------------------------------------------------------
    def reset(self, n_pinned=None):
        """`ppo_ac_s.py:93-99`: env e starts on `init_states[e % S]`, and the
        first `n_pinned` envs keep that assignment forever (`sample=False`)."""
        N, S, dev = self.num_envs, self.num_states, self.device
        if n_pinned is None:
            n_pinned = self.n_pinned
        self.idx = torch.arange(N, device=dev, dtype=torch.int64) % S
        self.sample = torch.ones(N, dtype=torch.bool, device=dev)
        self.sample[:n_pinned] = False

        self.x = self.init_states[self.idx].clone()
        self.time = torch.zeros(N, dtype=torch.int64, device=dev)
        self.visited = torch.full((N, self.max_steps + 1), INT32_MAX, dtype=torch.int32, device=dev)
        self.visited[:, 0] = self._hash(self.x)

        self.ret = torch.zeros(N, dtype=torch.float32, device=dev)
        self.norm_mean = torch.zeros(N, dtype=torch.float32, device=dev)
        self.norm_var = torch.ones(N, dtype=torch.float32, device=dev)
        self.norm_count = torch.full((N,), 1e-4, dtype=torch.float32, device=dev)

        self.solves = torch.zeros(S, dtype=torch.int64, device=dev)
        self.attempts = torch.zeros(S, dtype=torch.int64, device=dev)
        self.probs = torch.full((S,), 1.0 / S, dtype=torch.float32, device=dev)
        self.solved_idx = torch.zeros(S, dtype=torch.bool, device=dev)
        self.path_lengths = torch.full((S,), INT32_MAX, dtype=torch.int64, device=dev)
        if self.track_paths:
            self.best_paths = torch.full((S, self.max_steps), -1, dtype=torch.int32, device=dev)
            self.current_actions = torch.full((N, self.max_steps), -1, dtype=torch.int32, device=dev)
        return self.obs()

    def obs(self):
        return self.x

    def _hash(self, x):
        return (x.to(torch.int32) * self.hash_vec).sum(-1, dtype=torch.int32)

    def _draw(self, k):
        """`jax.random.choice(key, S, p=probs)`, by inverse CDF."""
        cdf = torch.cumsum(self.probs, 0)
        u = torch.rand(k, generator=self.gen, device=self.device) * cdf[-1]
        return torch.searchsorted(cdf, u).clamp(max=self.num_states - 1)

    # -- step ----------------------------------------------------------------
    def step(self, flat_action):
        """One vectorised transition. Returns `(obs, reward, done, info)`.

        `reward` is normalised, as PPO consumes it; `info["raw_reward"]` is the
        environment's own reward, which is what an env-parity check compares.
        """
        L = self.L
        i, r, k1, k2 = decode_action(flat_action, L)
        new_x = s_move(self.x, i, r, k1, k2, L)

        is_noop = (new_x == self.x).all(-1)
        new_hash = self._hash(new_x)
        already_visited = (self.visited == new_hash.unsqueeze(1)).any(-1)

        time = self.time + 1
        nnz = (new_x != 0).sum(-1)
        terminated = nnz == self.n_gen
        truncated = time >= self.max_steps
        done = terminated | truncated

        term_f = terminated.to(torch.float32)
        base_reward = -nnz.clamp(max=10).to(torch.float32) * (1.0 - term_f) + 1000.0 * term_f
        penalty = (already_visited.to(torch.float32) * self.cycle_penalty
                   + is_noop.to(torch.float32) * self.noop_penalty) * (1.0 - term_f)
        reward = base_reward - penalty
        if self.shaping is not None and self.lam:
            # `self.x` is still the state the action was taken FROM -- this must stay
            # above the assignment below. `done` carries truncation as well as
            # termination, which is what zeroes `Phi` at the horizon.
            reward = reward + shaping.shaping_term(
                self.x, new_x, done, self.lam, self.gamma, self.shaping, self.n_gen, L)

        self.x = new_x
        self.time = time
        self.visited = self.visited.scatter(1, time.clamp(max=self.max_steps).unsqueeze(1),
                                            new_hash.unsqueeze(1).to(torch.int32))

        info = {
            "idx": self.idx.clone(),
            "terminated": terminated,
            "truncated": truncated,
            "episode_length": time,
            "length": nnz,
            "noop_hit": is_noop,
            "cycle_hit": already_visited,
            "raw_reward": reward,
        }

        norm_reward = self._normalize(reward, done)
        if self.track_paths:
            self._log_paths(flat_action, info, done)
        self._auto_reset(done)
        return self.obs(), norm_reward, done, info

    def _normalize(self, reward, done):
        """`wrappers.py:319-363`, per env, with `batch_count = obs_len`."""
        bc = float(self.obs_len)
        self.ret = self.ret * self.gamma * (~done).to(torch.float32) + reward
        delta = self.ret - self.norm_mean
        tot = self.norm_count + bc
        self.norm_mean = self.norm_mean + delta * bc / tot
        m2 = self.norm_var * self.norm_count + delta.square() * self.norm_count * bc / tot
        self.norm_var = m2 / tot
        self.norm_count = tot
        return reward / torch.sqrt(self.norm_var + 1e-8)

    def _auto_reset(self, done):
        """`envs/environment.py:27-48` -- a done env immediately restarts."""
        if not bool(done.any()):
            return
        drawn = self._draw(self.num_envs)
        new_idx = torch.where(self.sample, drawn, self.idx)
        self.idx = torch.where(done, new_idx, self.idx)
        self.x = torch.where(done.unsqueeze(1), self.init_states[self.idx], self.x)
        self.time = torch.where(done, torch.zeros_like(self.time), self.time)
        fresh = torch.full_like(self.visited, INT32_MAX)
        fresh[:, 0] = self._hash(self.x)
        self.visited = torch.where(done.unsqueeze(1), fresh, self.visited)

    # -- path / sampling bookkeeping ----------------------------------------
    def _log_paths(self, flat_action, info, done):
        """`wrappers.LogPathsProbsS.step`."""
        cur = info["idx"]
        terminated = info["terminated"]
        ep_len = info["episode_length"]

        rows = torch.arange(self.num_envs, device=self.device)
        self.current_actions[rows, (ep_len - 1).clamp(min=0)] = flat_action.to(torch.int32)

        new_best = terminated & (ep_len < self.path_lengths[cur])
        if bool(new_best.any()):
            new_lengths = torch.where(new_best, ep_len, self.path_lengths[cur])
            new_paths = torch.where(new_best.unsqueeze(1), self.current_actions, self.best_paths[cur])
            new_terminated = terminated | self.solved_idx[cur]
            new_lengths, new_paths, new_terminated = self._propagate_min(
                cur, new_lengths, new_paths, new_terminated)
            self.current_actions = torch.where(
                done.unsqueeze(1), torch.full_like(self.current_actions, -1), self.current_actions)
            self._compute_probs(cur, terminated, done)
            self.solved_idx.index_copy_(0, cur, new_terminated)
            self.path_lengths.index_copy_(0, cur, new_lengths)
            self.best_paths.index_copy_(0, cur, new_paths)
        else:
            self.current_actions = torch.where(
                done.unsqueeze(1), torch.full_like(self.current_actions, -1), self.current_actions)
            self._compute_probs(cur, terminated, done)

    def _propagate_min(self, cur, lengths, paths, terminated):
        """`wrappers.py:_propagate_min_value`.

        Every env sharing an initial state takes that group's shortest entry --
        winner-takes-all across all three arrays, tie-broken by env index, which
        is what the stable `jnp.lexsort((lengths, idx))` does.
        """
        n = self.num_envs
        rows = torch.arange(n, device=self.device)
        key = lengths * n + rows
        best = torch.full((self.num_states,), torch.iinfo(torch.int64).max,
                          dtype=torch.int64, device=self.device)
        best.scatter_reduce_(0, cur, key, reduce="amin", include_self=True)
        winner = best[cur] % n
        return lengths[winner], paths[winner], terminated[winner]

    def _compute_probs(self, cur, terminated, done):
        """`wrappers.py:_compute_probs` -- harder and rarer states get sampled more."""
        self.solves.index_add_(0, cur, terminated.to(torch.int64))
        self.attempts.index_add_(0, cur, done.to(torch.int64))
        attempts = self.attempts.to(torch.float32)
        success_rate = self.solves.to(torch.float32) / (attempts + self.beta)
        raw = (1.0 - success_rate) ** self.alpha / (1.0 + attempts) ** 0.5
        self.probs = raw / raw.sum()

    # -- readout -------------------------------------------------------------
    def solve_data(self):
        out = {
            "solved_idx": self.solved_idx.cpu().numpy(),
            "path_lengths": self.path_lengths.cpu().numpy().astype(np.int32),
        }
        if self.track_paths:
            out["best_paths"] = self.best_paths.cpu().numpy()
        return out

    def load_solve_data(self, data):
        self.solved_idx.copy_(torch.as_tensor(data["solved_idx"], device=self.device))
        self.path_lengths.copy_(torch.as_tensor(np.asarray(data["path_lengths"], dtype=np.int64), device=self.device))
        if self.track_paths and "best_paths" in data:
            self.best_paths.copy_(torch.as_tensor(np.asarray(data["best_paths"], dtype=np.int32), device=self.device))
