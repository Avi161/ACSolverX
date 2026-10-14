"""PPO trainer (optional; the shipped policy is step 1000): Adam ``lr 2.5e-3``, 96-step rollouts, 3 epochs x 8
minibatches, ``gamma 0.999``, GAE ``0.95``, clip ``0.2``, entropy ``0.01``, value coefficient ``0.5``, clipped value
loss, advantages normalised per minibatch, grad-norm clip ``0.5``. ``micro`` splits a minibatch into chunks with the
same gradient. The reward is the plain dense one.

    states = encode_rows(data.load("ac19_extended"))
    model = train(states, updates=100, n_pinned=pinned_prefix(states, encode_rows(data.load("1190ms"))))
"""
import math

import torch

from ..core.config import is_finite_number, reject_unknown, require_int
from .env import VecEnv
from .policy import ActorCritic, forward, log_prob_entropy
from .codec import encode

DEFAULTS = dict(lr=2.5e-3, envs=2380, steps=96, epochs=3, minibatches=8, gamma=0.999, lam=0.95,
                clip=0.2, ent=0.01, vf=0.5, max_grad_norm=0.5, micro=2048, chunk=4096, seed=142)


def training_config(overrides):
    """Validate PPO settings before constructing the model or starting an experiment."""
    reject_unknown(overrides, DEFAULTS, "PPO")
    cfg = {**DEFAULTS, **overrides}
    for key in ("envs", "steps", "epochs", "minibatches", "micro", "chunk"):
        require_int(cfg[key], key)
    require_int(cfg["seed"], "seed", low=0)
    if cfg["minibatches"] > cfg["envs"] * cfg["steps"]:
        raise ValueError("minibatches must not exceed envs * steps")
    for key in ("lr", "gamma", "lam", "clip", "ent", "vf", "max_grad_norm"):
        value = cfg[key]
        if not is_finite_number(value) or value < 0:
            raise ValueError(f"{key} must be a finite nonnegative number, got {value!r}")
    for key in ("gamma", "lam"):
        if cfg[key] > 1:
            raise ValueError(f"{key} must be in [0, 1]")
    for key in ("lr", "max_grad_norm"):
        if cfg[key] == 0:
            raise ValueError(f"{key} must be positive")
    return cfg


def encode_rows(rows, L=24):
    """``acx.data`` rows -> ``(S, 2L)`` int tensor (``encode`` raises on a relator longer than ``L``)."""
    return torch.stack([encode(r.pres.rels, L) for r in rows])


def pinned_prefix(states, ms_states):
    """Leading rows of ``states`` equal to the leading rows of ``ms_states`` (the pinned envs)."""
    n = 0
    while n < min(len(states), len(ms_states)) and bool((states[n] == ms_states[n]).all()):
        n += 1
    return n


def rollout(model, env, cfg, gen):
    """``steps`` environment steps under the sampled policy: the batch tensors, the last value and the solve count."""
    T, N = cfg["steps"], env.N
    obs = torch.empty((T, N, 2 * env.L), dtype=torch.int64)
    act = torch.empty((T, N), dtype=torch.int64)
    logp, val, rew, done = (torch.empty((T, N), dtype=torch.float32) for _ in range(4))
    terminated = 0
    with torch.no_grad():
        for t in range(T):
            logits, v = forward(model, env.x, cfg["chunk"])
            a = torch.multinomial(torch.softmax(logits, -1), 1, generator=gen).squeeze(1)
            obs[t], act[t], val[t], logp[t] = env.x, a, v, log_prob_entropy(logits, a)[0]
            _, rew[t], d, term = env.step(a)
            done[t] = d.float()
            terminated += int(term.sum())
        last = forward(model, env.x, cfg["chunk"])[1]
    return obs, act, logp, val, rew, done, last, terminated


def gae(val, rew, done, last, gamma, lam):
    """Generalised advantage estimate and the value targets ``(advantage, advantage + value)``."""
    adv, run, nxt = torch.zeros_like(rew), torch.zeros_like(last), last
    for t in reversed(range(len(rew))):
        delta = rew[t] + gamma * nxt * (1 - done[t]) - val[t]
        run = delta + gamma * lam * (1 - done[t]) * run
        adv[t], nxt = run, val[t]
    return adv, adv + val


def update(model, opt, batch, cfg, gen):
    """Epochs x minibatches of the clipped PPO loss. Returns the mean policy / value / entropy terms."""
    obs, act, logp, val, adv, target = batch
    B = len(act)
    eps, totals, n = cfg["clip"], torch.zeros(3), 0
    for _ in range(cfg["epochs"]):
        perm = torch.randperm(B, generator=gen)
        for sel in torch.tensor_split(perm, cfg["minibatches"]):
            a = adv[sel]
            if len(a) > 1:                                     # sample std is undefined for a singleton
                a = (a - a.mean()) / (a.std() + 1e-8)           # per minibatch, before microbatching
            opt.zero_grad(set_to_none=True)
            for c in range(0, len(sel), cfg["micro"]):
                idx, ac = sel[c:c + cfg["micro"]], a[c:c + cfg["micro"]]
                logits, v = model(obs[idx])
                lp, ent = log_prob_entropy(logits, act[idx])
                clipped = val[idx] + (v - val[idx]).clamp(-eps, eps)
                vloss = 0.5 * torch.maximum((v - target[idx]) ** 2, (clipped - target[idx]) ** 2).mean()
                ratio = torch.exp(lp - logp[idx])
                ploss = -torch.minimum(ratio * ac, ratio.clamp(1 - eps, 1 + eps) * ac).mean()
                loss = ploss + cfg["vf"] * vloss - cfg["ent"] * ent.mean()
                (loss * len(idx) / len(sel)).backward()
                totals += torch.stack([ploss, vloss, ent.mean()]).detach() * len(idx) / len(sel)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["max_grad_norm"])
            opt.step()
            n += 1
    return dict(zip(("policy", "value", "entropy"), (totals / n).tolist()))


def train(states, updates, n_pinned=0, model=None, log=print, **overrides):
    """Run ``updates`` PPO updates over the initial ``states``; returns the model."""
    cfg = training_config(overrides)
    require_int(updates, "updates", low=0)
    env = VecEnv(states, cfg["envs"], n_pinned=n_pinned, gamma=cfg["gamma"], max_steps=cfg["steps"], seed=cfg["seed"])
    torch.manual_seed(cfg["seed"])
    gen = torch.Generator().manual_seed(cfg["seed"] + 1)
    model = model or ActorCritic()
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"], eps=1e-5)
    for u in range(1, updates + 1):
        obs, act, logp, val, rew, done, last, terminated = rollout(model, env, cfg, gen)
        adv, target = gae(val, rew, done, last, cfg["gamma"], cfg["lam"])
        batch = tuple(t.reshape(-1, *t.shape[2:]) for t in (obs, act, logp, val, adv, target))   # merge steps and envs
        stats = update(model, opt, batch, cfg, gen)
        if not all(map(math.isfinite, stats.values())):
            raise FloatingPointError(f"update {u}: non-finite loss {stats}")
        log(f"update {u}: solved {int(env.solved.sum())}/{env.S}, terminations {terminated}, {stats}")
    return model
