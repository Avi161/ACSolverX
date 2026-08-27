"""PPO in PyTorch, matching `ppo_ac_s.py` knob for knob.

The hyperparameters below are `ppo_ac_s.py:337-360` verbatim, and the loss is
its `_loss_fn`: clipped surrogate, PPO2 clipped value loss, entropy bonus, with
the advantage normalised **per minibatch** (not per batch), and the global grad
norm clipped **before** Adam because upstream chains
`optax.clip_by_global_norm` ahead of `optax.adam`.

The one implementation liberty is gradient accumulation. A 28,560-row minibatch
runs the actor head's `[B, 24, 24, 128]` grid through autograd, which is ~8 GB
before anything else; `MICRO_BATCH` splits the minibatch and scales each chunk's
loss by its share, which is exactly the same gradient. The advantage
normalisation still happens over the whole minibatch first -- normalising per
micro-batch would quietly change the objective.
"""

import math
import time

import numpy as np
import torch

from experiments.ppo.policy import RelativeDualRingActorCritic, action_stats

DEFAULT_CONFIG = {
    # --- upstream, do not drift ------------------------------------------
    "LR": 5 * 5e-4,
    "NUM_ENVS": 1190 * 2,
    "NUM_STEPS": 96,
    "TOTAL_TIMESTEPS": 1e9,
    "UPDATE_EPOCHS": 3,
    "NUM_MINIBATCHES": 8,
    "GAMMA": 0.999,
    "GAE_LAMBDA": 0.95,
    "CLIP_EPS": 0.2,
    "ENT_COEF": 0.01,
    "VF_COEF": 0.5,
    "MAX_GRAD_NORM": 0.5,
    "ACTIVATION": "gelu",
    "ANNEAL_LR": False,
    "CYCLE_PENALTY": 0.0,
    "NOOP_PENALTY": 0.0,
    "SEED": 142,
    # --- this port -------------------------------------------------------
    "DATASET": "AC19_extended",
    "MAX_RELATOR_LENGTH": 24,
    "MICRO_BATCH": 2048,
    "ROLLOUT_CHUNK": 4096,
    "ALLOW_TF32": False,
}


def make_config(**overrides):
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(overrides)
    cfg["NUM_UPDATES"] = int(cfg["TOTAL_TIMESTEPS"] // cfg["NUM_STEPS"] // cfg["NUM_ENVS"])
    cfg["MINIBATCH_SIZE"] = cfg["NUM_ENVS"] * cfg["NUM_STEPS"] // cfg["NUM_MINIBATCHES"]
    return cfg


def _cpu_rng(state):
    """An RNG state must be a CPU `ByteTensor`, whatever device the run is on.

    `run_ppo` resumes with `torch.load(..., map_location=device)`, which maps *every*
    tensor in the blob -- the three RNG states included -- so on a GPU they arrive on CUDA
    and `set_state` raises `TypeError: RNG state must be a torch.ByteTensor`. That is a
    crash on the resume path only, which is exactly the path a multi-hour run depends on
    and the one a CPU test never reaches: `map_location="cpu"` leaves the states where
    `set_state` already wants them, so the round-trip test passed for years of CPU runs.
    Route every RNG state through here rather than `.cpu()`-ing them one by one -- the
    original bug was two of the three call sites having been missed.
    """
    return state.cpu() if hasattr(state, "cpu") else state


class PPOTrainer:
    def __init__(self, env, config, device):
        self.env = env
        self.cfg = config
        self.device = torch.device(device)
        self.update = 0

        torch.manual_seed(int(config["SEED"]))
        self.gen = torch.Generator(device=self.device)
        self.gen.manual_seed(int(config["SEED"]) + 1)

        self.model = RelativeDualRingActorCritic(
            max_len=config["MAX_RELATOR_LENGTH"], activation=config["ACTIVATION"]).to(self.device)
        self.opt = torch.optim.Adam(self.model.parameters(), lr=config["LR"], eps=1e-5)

    # -- rollout -------------------------------------------------------------
    @torch.no_grad()
    def _policy_chunked(self, obs, need_logits=False):
        """Forward pass split into `ROLLOUT_CHUNK` rows so the actor grid fits."""
        chunk = self.cfg["ROLLOUT_CHUNK"]
        if obs.shape[0] <= chunk:
            return self.model(obs)
        logits, values = [], []
        for lo in range(0, obs.shape[0], chunk):
            lg, v = self.model(obs[lo:lo + chunk])
            logits.append(lg)
            values.append(v)
        return torch.cat(logits), torch.cat(values)

    @torch.no_grad()
    def collect(self):
        cfg, env = self.cfg, self.env
        T, N = cfg["NUM_STEPS"], cfg["NUM_ENVS"]
        dev = self.device

        obs_buf = torch.empty((T, N, env.obs_len), dtype=torch.int8, device=dev)
        act_buf = torch.empty((T, N), dtype=torch.int64, device=dev)
        logp_buf = torch.empty((T, N), dtype=torch.float32, device=dev)
        val_buf = torch.empty((T, N), dtype=torch.float32, device=dev)
        rew_buf = torch.empty((T, N), dtype=torch.float32, device=dev)
        done_buf = torch.empty((T, N), dtype=torch.float32, device=dev)

        stats = {"terminated": 0.0, "noop": 0.0, "cycle": 0.0, "length": 0.0,
                 "min_length": math.inf, "max_length": 0.0}

        for t in range(T):
            obs = env.obs()
            logits, value = self._policy_chunked(obs)
            probs = torch.softmax(logits, dim=-1)
            action = torch.multinomial(probs, 1, generator=self.gen).squeeze(1)
            logp, _ = action_stats(logits, action)

            obs_buf[t] = obs.to(torch.int8)
            act_buf[t] = action
            logp_buf[t] = logp
            val_buf[t] = value

            _, reward, done, info = env.step(action)
            rew_buf[t] = reward
            done_buf[t] = done.to(torch.float32)

            stats["terminated"] += float(info["terminated"].sum())
            stats["noop"] += float(info["noop_hit"].to(torch.float32).mean())
            stats["cycle"] += float(info["cycle_hit"].to(torch.float32).mean())
            lengths = info["length"].to(torch.float32)
            stats["length"] += float(lengths.mean())
            stats["min_length"] = min(stats["min_length"], float(lengths.min()))
            stats["max_length"] = max(stats["max_length"], float(lengths.max()))

        _, last_val = self._policy_chunked(env.obs())
        for k in ("noop", "cycle", "length"):
            stats[k] /= T
        return dict(obs=obs_buf, actions=act_buf, log_probs=logp_buf, values=val_buf,
                    rewards=rew_buf, dones=done_buf, last_value=last_val, stats=stats)

    def gae(self, roll):
        """`ppo_ac_s.py:_calculate_gae`, reversed over the time axis."""
        cfg = self.cfg
        gamma, lam = cfg["GAMMA"], cfg["GAE_LAMBDA"]
        adv = torch.zeros_like(roll["rewards"])
        run = torch.zeros_like(roll["last_value"])
        nxt = roll["last_value"]
        for t in range(cfg["NUM_STEPS"] - 1, -1, -1):
            done, value, reward = roll["dones"][t], roll["values"][t], roll["rewards"][t]
            delta = reward + gamma * nxt * (1.0 - done) - value
            run = delta + gamma * lam * (1.0 - done) * run
            adv[t] = run
            nxt = value
        return adv, adv + roll["values"]

    # -- update --------------------------------------------------------------
    def learn(self, roll, adv, targets):
        cfg = self.cfg
        B = cfg["NUM_ENVS"] * cfg["NUM_STEPS"]
        flat = dict(
            obs=roll["obs"].reshape(B, -1),
            actions=roll["actions"].reshape(B),
            log_probs=roll["log_probs"].reshape(B),
            values=roll["values"].reshape(B),
            adv=adv.reshape(B),
            targets=targets.reshape(B),
        )
        mb = cfg["MINIBATCH_SIZE"]
        micro = cfg["MICRO_BATCH"]
        totals = {"policy": 0.0, "value": 0.0, "entropy": 0.0, "clipfrac": 0.0, "approx_kl": 0.0}
        n_mb = 0

        for _ in range(cfg["UPDATE_EPOCHS"]):
            perm = torch.randperm(B, generator=self.gen, device=self.device)
            for start in range(0, B, mb):
                sel = perm[start:start + mb]
                gae = flat["adv"][sel]
                gae = (gae - gae.mean()) / (gae.std() + 1e-8)   # per MINIBATCH, before splitting
                self.opt.zero_grad(set_to_none=True)
                for lo in range(0, sel.numel(), micro):
                    idx = sel[lo:lo + micro]
                    share = idx.numel() / sel.numel()
                    stats = self._micro_loss(flat, idx, gae[lo:lo + micro])
                    (stats["loss"] * share).backward()
                    for k in totals:
                        totals[k] += float(stats[k].detach()) * share
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), cfg["MAX_GRAD_NORM"])
                self.opt.step()
                n_mb += 1

        return {k: v / max(n_mb, 1) for k, v in totals.items()}

    def _micro_loss(self, flat, idx, gae):
        cfg = self.cfg
        eps = cfg["CLIP_EPS"]
        logits, value = self.model(flat["obs"][idx])
        log_prob, entropy = action_stats(logits, flat["actions"][idx])

        old_value = flat["values"][idx]
        target = flat["targets"][idx]
        clipped = old_value + (value - old_value).clamp(-eps, eps)
        value_loss = 0.5 * torch.maximum((value - target) ** 2, (clipped - target) ** 2).mean()

        ratio = torch.exp(log_prob - flat["log_probs"][idx])
        policy_loss = -torch.minimum(ratio * gae, ratio.clamp(1 - eps, 1 + eps) * gae).mean()
        entropy = entropy.mean()

        loss = policy_loss + cfg["VF_COEF"] * value_loss - cfg["ENT_COEF"] * entropy
        with torch.no_grad():
            clipfrac = ((ratio - 1.0).abs() > eps).to(torch.float32).mean()
            approx_kl = (flat["log_probs"][idx] - log_prob).mean()
        return {"loss": loss, "policy": policy_loss, "value": value_loss,
                "entropy": entropy, "clipfrac": clipfrac, "approx_kl": approx_kl}

    # -- one update ----------------------------------------------------------
    def step_update(self):
        t0 = time.time()
        roll = self.collect()
        t_collect = time.time() - t0
        adv, targets = self.gae(roll)
        t1 = time.time()
        losses = self.learn(roll, adv, targets)
        t_learn = time.time() - t1

        values_flat, targets_flat = roll["values"].flatten(), targets.flatten()
        explained_var = float(1.0 - (values_flat - targets_flat).var() / targets_flat.var().clamp(min=1e-8))

        self.update += 1
        n_solved = int(self.env.solved_idx.sum())
        pinned = self.env.n_pinned or self.env.num_states
        n_solved_pinned = int(self.env.solved_idx[:pinned].sum())
        metrics = {
            "update": self.update,
            "global_step": self.update * self.cfg["NUM_STEPS"] * self.cfg["NUM_ENVS"],
            "num_solved": n_solved,
            "num_solved_pinned": n_solved_pinned,
            "explained_var": explained_var,
            "adv_mean": float(adv.mean()), "adv_std": float(adv.std()),
            "mean_length": roll["stats"]["length"],
            "min_length": roll["stats"]["min_length"],
            "max_length": roll["stats"]["max_length"],
            "noop_rate": roll["stats"]["noop"],
            "cycle_rate": roll["stats"]["cycle"],
            "terminations": roll["stats"]["terminated"],
            "collect_s": t_collect, "learn_s": t_learn,
            "sps": self.cfg["NUM_STEPS"] * self.cfg["NUM_ENVS"] / max(t_collect + t_learn, 1e-9),
        }
        metrics.update({f"loss_{k}": v for k, v in losses.items()})
        return metrics

    # -- persistence ---------------------------------------------------------
    def state_dict(self):
        env = self.env
        return {
            "update": self.update,
            "config": self.cfg,
            "model": self.model.state_dict(),
            "optimizer": self.opt.state_dict(),
            "torch_rng": torch.get_rng_state(),
            "gen_rng": self.gen.get_state(),
            "env": {
                "x": env.x.cpu(), "time": env.time.cpu(), "idx": env.idx.cpu(),
                "sample": env.sample.cpu(), "visited": env.visited.cpu(),
                "ret": env.ret.cpu(), "norm_mean": env.norm_mean.cpu(),
                "norm_var": env.norm_var.cpu(), "norm_count": env.norm_count.cpu(),
                "solves": env.solves.cpu(), "attempts": env.attempts.cpu(),
                "probs": env.probs.cpu(), "solved_idx": env.solved_idx.cpu(),
                "path_lengths": env.path_lengths.cpu(),
                "best_paths": env.best_paths.cpu() if env.track_paths else None,
                "current_actions": env.current_actions.cpu() if env.track_paths else None,
                "gen_rng": env.gen.get_state(),
            },
        }

    def load_state_dict(self, blob):
        self.update = int(blob["update"])
        self.model.load_state_dict(blob["model"])
        self.opt.load_state_dict(blob["optimizer"])
        torch.set_rng_state(_cpu_rng(blob["torch_rng"]))
        self.gen.set_state(_cpu_rng(blob["gen_rng"]))
        env, e = self.env, blob["env"]
        for name in ("x", "time", "idx", "sample", "visited", "ret", "norm_mean",
                     "norm_var", "norm_count", "solves", "attempts", "probs",
                     "solved_idx", "path_lengths"):
            getattr(env, name).copy_(e[name].to(env.device))
        if env.track_paths and e.get("best_paths") is not None:
            env.best_paths.copy_(e["best_paths"].to(env.device))
            env.current_actions.copy_(e["current_actions"].to(env.device))
        env.gen.set_state(_cpu_rng(e["gen_rng"]))


def solved_rows(env):
    """`(idx, path_length, packed_path)` for every initial state solved so far."""
    solved = env.solved_idx.cpu().numpy()
    lengths = env.path_lengths.cpu().numpy()
    paths = env.best_paths.cpu().numpy() if env.track_paths else None
    out = []
    for i in np.nonzero(solved)[0]:
        n = int(lengths[i])
        path = paths[i, :n].tolist() if paths is not None else []
        out.append({"idx": int(i), "path_length": n, "path": path})
    return out
