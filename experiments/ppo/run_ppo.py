"""The runner every notebook cell and CLI invocation goes through.

Four stages, selected by `cfg["STAGE"]`:

| stage       | what it does                                                     |
|-------------|------------------------------------------------------------------|
| `convert`   | orbax -> `.npz`, once, so nothing later needs JAX                |
| `parity`    | transplant `610model` into the torch net and check it end to end |
| `train`     | PPO from scratch, resumable, checkpoint + jsonl + W&B            |
| `beam_eval` | beam-decode a checkpoint over a dataset, jsonl per presentation  |

Two contracts hold in every stage, both mandatory for this repo:

- **The heartbeat is time-based**, a ~60 s beat carrying an instantaneous rate,
  so a slow machine shows up as a falling number rather than as silence.
- **Restart -> Run All continues.** Every stage reads what is already on disk
  before doing anything: `train` resumes from its checkpoint, `beam_eval` skips
  presentations already in its jsonl.

Local runs are capped: `beam_width * max_steps <= 1000` expansions unless
`ACSOLVERX_ALLOW_BIG=1` is set, which only the notebook sets. See the repo
`CLAUDE.md` -- production budgets are the user's to run on Colab.
"""

import json
import os
import sys
import time

import numpy as np
import torch

from experiments.ppo import acs_data
from experiments.ppo.acs_env import VecACS
from experiments.ppo.beam import repair_jsonl, run_beam, summarise
from experiments.ppo.policy import RelativeDualRingActorCritic
from experiments.ppo.ppo import DEFAULT_CONFIG, PPOTrainer, make_config, solved_rows

ROOT = acs_data.ROOT
LOCAL_EXPANSION_CAP = 1000


def pick_device(requested="auto"):
    if requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_matmul_precision(allow_tf32):
    """Upstream pins `jax_default_matmul_precision=float32`; TF32 is off to match.

    An A100 silently uses TF32 for fp32 matmuls unless told not to, which costs
    ~1e-3 of relative accuracy -- fatal for a 1e-5 parity gate, invisible in
    training. The knob exists so training can buy the speed back deliberately.
    """
    torch.backends.cuda.matmul.allow_tf32 = bool(allow_tf32)
    torch.backends.cudnn.allow_tf32 = bool(allow_tf32)
    if hasattr(torch, "set_float32_matmul_precision"):
        torch.set_float32_matmul_precision("high" if allow_tf32 else "highest")


class Heartbeat:
    """Time-based progress line: fires on a period, never on an event count."""

    def __init__(self, every_s=60.0, sink=print):
        self.every_s = float(every_s)
        self.sink = sink
        self.t0 = self.last = time.time()

    def maybe(self, msg_fn, force=False):
        now = time.time()
        if force or now - self.last >= self.every_s:
            self.sink(msg_fn(now - self.t0))
            self.last = now
            return True
        return False


def _mirror(src, dst_dir):
    """Whole-file copy to a (possibly remote) mirror. Never append to a mount."""
    if not dst_dir:
        return
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, os.path.basename(src))
    tmp = dst + ".tmp"
    with open(src, "rb") as a, open(tmp, "wb") as b:
        b.write(a.read())
    os.replace(tmp, dst)


def _seed_from_mirror(local, mirror_dir):
    """Restart contract: rebuild a local artefact from the mirror on a fresh VM."""
    if not mirror_dir:
        return False
    remote = os.path.join(mirror_dir, os.path.basename(local))
    if os.path.exists(remote) and not os.path.exists(local):
        os.makedirs(os.path.dirname(os.path.abspath(local)) or ".", exist_ok=True)
        with open(remote, "rb") as a, open(local, "wb") as b:
            b.write(a.read())
        return True
    return False


# --------------------------------------------------------------------------
# stages
# --------------------------------------------------------------------------
def stage_convert(cfg, log=print):
    from experiments.ppo.transplant import export_npz, read_config

    ckpt_dir = os.path.join(ROOT, cfg["CKPT_DIR"])
    out = os.path.join(ROOT, cfg["PARAMS_NPZ"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    step = cfg.get("CKPT_STEP")
    if step is None:
        step = max(int(d) for d in os.listdir(ckpt_dir) if d.isdigit())
    export_npz(ckpt_dir, out, step)
    saved = read_config(ckpt_dir, step)
    log(f"checkpoint config: seed={saved.get('SEED')} envs={saved.get('NUM_ENVS')} "
        f"steps={saved.get('NUM_STEPS')} of {saved.get('NUM_UPDATES')} updates; "
        f"this artefact is step {step}")
    return {"npz": out, "step": step, "checkpoint_config": saved}


def stage_parity(cfg, log=print):
    """Load the shipped weights, then check the torch stack agrees with JAX.

    Runs the JAX side too when JAX is importable (Colab); when it is not, it
    still checks everything that does not need it -- that the transplant is
    complete, that masked logits are finite exactly on legal actions, and that
    the env's own invariants hold over random rollouts.
    """
    from experiments.ppo.transplant import load_into

    device = pick_device(cfg.get("DEVICE", "auto"))
    set_matmul_precision(False)
    L = cfg["MAX_RELATOR_LENGTH"]
    log(f"parity on {device} (TF32 off)")

    model = RelativeDualRingActorCritic(max_len=L, activation=cfg["ACTIVATION"]).to(device).eval()
    src = os.path.join(ROOT, cfg["PARAMS_NPZ"])
    if not os.path.exists(src):
        src = os.path.join(ROOT, cfg["CKPT_DIR"])
    load_into(model, src, cfg.get("CKPT_STEP"))
    log(f"transplanted {sum(p.numel() for p in model.parameters())} parameters from {src}")

    pres = acs_data.load_presentations(cfg["DATASET"], L)
    n = int(cfg.get("PARITY_BATCH", 256))
    obs = torch.as_tensor(pres[:n], dtype=torch.int64, device=device)
    with torch.no_grad():
        logits, value = model(obs)

    legal = RelativeDualRingActorCritic.action_mask(obs, L)
    finite = logits > -1e8
    out = {"batch": n, "mask_matches_logits": bool(torch.equal(legal, finite)),
           "legal_per_state_mean": float(legal.sum(-1).to(torch.float32).mean()),
           "value_mean": float(value.mean()), "value_std": float(value.std())}

    env_report = _env_selfcheck(cfg, device, log)
    out.update(env_report)

    jax_report = _jax_parity(cfg, model, obs, device, log)
    out.update(jax_report)

    log(json.dumps(out, indent=2, default=float))
    return out


def _env_selfcheck(cfg, device, log, steps=32, n_envs=64):
    """Invariants the JAX env also satisfies, checkable without JAX."""
    L = cfg["MAX_RELATOR_LENGTH"]
    pres = acs_data.load_presentations(cfg["DATASET"], L)
    env = VecACS(pres[:2048], n_envs, max_length=L, max_steps=cfg["NUM_STEPS"],
                 gamma=cfg["GAMMA"], device=device, seed=0,
                 n_pinned=min(8, n_envs))
    gen = torch.Generator(device=device)
    gen.manual_seed(7)
    bad_reward = bad_reduce = 0
    for _ in range(steps):
        legal = RelativeDualRingActorCritic.action_mask(env.obs(), L).to(torch.float32)
        legal = torch.where(legal.sum(-1, keepdim=True) > 0, legal, torch.ones_like(legal))
        action = torch.multinomial(legal, 1, generator=gen).squeeze(1)
        _, _, _, info = env.step(action)
        nnz = info["length"]
        raw = info["raw_reward"]
        expect = torch.where(info["terminated"], torch.full_like(raw, 1000.0),
                             -nnz.clamp(max=10).to(torch.float32))
        bad_reward += int((raw != expect).sum())
        # every relator must be freely and cyclically reduced
        x = env.x.reshape(n_envs, 2, L)
        for g in range(2):
            r = x[:, g, :]
            nz = (r != 0).sum(-1)
            adj = (r[:, :-1] == -r[:, 1:]) & (r[:, 1:] != 0)
            bad_reduce += int(adj.any(-1).sum())
            first = r[:, 0]
            last = torch.gather(r, 1, (nz - 1).clamp(min=0).unsqueeze(1)).squeeze(1)
            bad_reduce += int(((first == -last) & (nz > 1)).sum())
    log(f"env self-check over {steps} steps x {n_envs} envs: "
        f"reward mismatches={bad_reward} unreduced relators={bad_reduce}")
    return {"env_reward_mismatches": bad_reward, "env_unreduced_relators": bad_reduce,
            "env_solved_after_selfcheck": int(env.solved_idx.sum())}


def _jax_parity(cfg, model, obs, device, log):
    """The real gate: same weights, same batch, two frameworks."""
    try:
        import jax
        import jax.numpy as jnp
    except ImportError:
        log("jax not importable -- skipping the cross-framework gate "
            "(run this stage on Colab to close it)")
        return {"jax_available": False}

    sys.path.insert(0, ROOT)
    jax.config.update("jax_default_matmul_precision", "float32")
    from network import RelativeDualRingActorCritic as FlaxNet          # noqa: E402
    from experiments.ppo.transplant import read_orbax_params            # noqa: E402

    ckpt_dir = os.path.join(ROOT, cfg["CKPT_DIR"])
    flat, step = read_orbax_params(ckpt_dir, cfg.get("CKPT_STEP"))
    params = {"params": _unflatten(flat)}
    net = FlaxNet(activation=cfg["ACTIVATION"])
    pi, value = net.apply(params, jnp.asarray(obs.cpu().numpy(), dtype=jnp.int8))
    with torch.no_grad():
        t_logits, t_value = model(obs)

    j_logits = np.asarray(pi.logits)
    d_logits = float(np.abs(j_logits - t_logits.cpu().numpy()).max())
    d_value = float(np.abs(np.asarray(value) - t_value.cpu().numpy()).max())
    log(f"JAX vs torch on step {step}: max|dlogits|={d_logits:.3e} max|dvalue|={d_value:.3e}")
    return {"jax_available": True, "jax_step": step,
            "max_abs_logit_diff": d_logits, "max_abs_value_diff": d_value,
            "parity_ok": d_logits < 1e-4 and d_value < 1e-4}


def _unflatten(flat):
    tree = {}
    for k, v in flat.items():
        node = tree
        parts = k.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = v
    return tree


def stage_train(cfg, log=print):
    device = pick_device(cfg.get("DEVICE", "auto"))
    set_matmul_precision(cfg.get("ALLOW_TF32", False))
    config = make_config(**{k: v for k, v in cfg.items() if k in DEFAULT_CONFIG})

    L = config["MAX_RELATOR_LENGTH"]
    stem = config["DATASET"]
    pres = acs_data.load_presentations(stem, L)
    n_pinned = acs_data.ms_prefix_length(stem)
    log(f"{stem}: {len(pres)} presentations, MS prefix {n_pinned} "
        f"-> {n_pinned} envs pinned deterministically, {config['NUM_ENVS'] - n_pinned} sampling")

    env = VecACS(pres, config["NUM_ENVS"], max_length=L, max_steps=config["NUM_STEPS"],
                 gamma=config["GAMMA"], cycle_penalty=config["CYCLE_PENALTY"],
                 noop_penalty=config["NOOP_PENALTY"], n_pinned=n_pinned,
                 device=device, seed=config["SEED"])
    trainer = PPOTrainer(env, config, device)

    out_dir = cfg["OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    tag = cfg.get("RUN_TAG") or f"ppo-drt-{stem}-s{config['SEED']}"
    ckpt_path = os.path.join(out_dir, f"{tag}.pt")
    jsonl_path = os.path.join(out_dir, f"{tag}.jsonl")
    mirror = cfg.get("MIRROR_DIR")
    _seed_from_mirror(ckpt_path, mirror)
    _seed_from_mirror(jsonl_path, mirror)

    if os.path.exists(ckpt_path):
        trainer.load_state_dict(torch.load(ckpt_path, map_location=device, weights_only=False))
        log(f"resumed from {ckpt_path} at update {trainer.update}")

    run = _wandb_init(cfg, config, tag, log)
    target = int(cfg.get("MAX_UPDATES") or config["NUM_UPDATES"])
    save_every = int(cfg.get("SAVE_EVERY", 25))
    hb = Heartbeat(cfg.get("HEARTBEAT_EVERY_S", 60.0), log)
    log(f"training updates {trainer.update} -> {target} "
        f"({config['NUM_STEPS'] * config['NUM_ENVS']:,} timesteps each) on {device}")

    repair_jsonl(jsonl_path, log)      # a killed VM can only tear the last line
    with open(jsonl_path, "a") as fh:
        while trainer.update < target:
            m = trainer.step_update()
            fh.write(json.dumps(m) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            if run is not None:
                run.log(m, step=m["update"])
            hb.maybe(lambda el, m=m, t=target: (
                f"  update {m['update']}/{t}  solved={m['num_solved']} "
                f"(pinned {m['num_solved_pinned']})  {m['sps'] / 1000:.1f}k sps  "
                f"elapsed {el / 60:.1f} min  "
                f"ETA {((t - m['update']) * (m['collect_s'] + m['learn_s'])) / 60:.1f} min"),
                force=trainer.update % 10 == 0)
            if trainer.update % save_every == 0 or trainer.update >= target:
                _save(trainer, ckpt_path, mirror)
                _mirror(jsonl_path, mirror)
                log(f"  checkpoint at update {trainer.update} -> {ckpt_path}")

    _save(trainer, ckpt_path, mirror)
    _mirror(jsonl_path, mirror)
    summary = {"updates": trainer.update, "solved": int(env.solved_idx.sum()),
               "solved_pinned": int(env.solved_idx[:n_pinned].sum()) if n_pinned else 0,
               "checkpoint": ckpt_path, "jsonl": jsonl_path}
    solved_path = os.path.join(out_dir, f"{tag}_solved.jsonl")
    with open(solved_path, "w") as fh:
        for row in solved_rows(env):
            fh.write(json.dumps(row) + "\n")
    _mirror(solved_path, mirror)
    if run is not None:
        run.summary.update(summary)
        run.finish()
    log(json.dumps(summary, indent=2))
    return summary


def _save(trainer, path, mirror):
    tmp = path + ".tmp"
    torch.save(trainer.state_dict(), tmp)
    os.replace(tmp, path)
    _mirror(path, mirror)


def _wandb_init(cfg, config, tag, log):
    if not cfg.get("USE_WANDB"):
        return None
    try:
        import wandb
    except ImportError:
        log("wandb not installed -- continuing without it")
        return None
    return wandb.init(
        entity=cfg.get("WANDB_ENTITY") or None,
        project=cfg.get("WANDB_PROJECT") or None,
        group=cfg.get("WANDB_GROUP") or None,
        job_type=cfg.get("WANDB_JOB_TYPE") or "ppo-train",
        name=tag, id=tag, resume="allow",
        tags=cfg.get("WANDB_TAGS") or None,
        notes=cfg.get("WANDB_NOTES") or None,
        config=config,
    )


def stage_beam(cfg, log=print):
    from experiments.ppo.transplant import load_into

    device = pick_device(cfg.get("DEVICE", "auto"))
    set_matmul_precision(cfg.get("ALLOW_TF32", False))
    L = cfg["MAX_RELATOR_LENGTH"]
    width, steps = int(cfg["BEAM_WIDTH"]), int(cfg["BEAM_MAX_STEPS"])
    if width * steps > LOCAL_EXPANSION_CAP and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(
            f"beam_width * max_steps = {width * steps} exceeds the local cap of "
            f"{LOCAL_EXPANSION_CAP}. Production budgets run on Colab, where the "
            f"notebook sets ACSOLVERX_ALLOW_BIG=1.")

    model = RelativeDualRingActorCritic(max_len=L, activation=cfg["ACTIVATION"]).to(device).eval()
    src = cfg.get("BEAM_CHECKPOINT")
    if src and src.endswith(".pt"):
        blob = torch.load(src, map_location=device, weights_only=False)
        model.load_state_dict(blob["model"])
        log(f"loaded torch checkpoint {src} (update {blob.get('update')})")
    else:
        src = os.path.join(ROOT, cfg["PARAMS_NPZ"])
        if not os.path.exists(src):
            src = os.path.join(ROOT, cfg["CKPT_DIR"])
        load_into(model, src, cfg.get("CKPT_STEP"))
        log(f"loaded upstream checkpoint {src}")

    stem = cfg["EVAL_DATASET"]
    pres = acs_data.load_presentations(stem, L)
    out_dir = cfg["OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    tag = cfg.get("BEAM_TAG") or f"beam-{stem}-w{width}-t{steps}"
    out_path = os.path.join(out_dir, f"{tag}.jsonl")
    mirror = cfg.get("MIRROR_DIR")
    _seed_from_mirror(out_path, mirror)

    end = cfg.get("EVAL_END")
    result = run_beam(
        model, pres, out_path, start=int(cfg.get("EVAL_START", 0)),
        end=None if end is None else int(end), device=device, beam_width=width,
        max_steps=steps, alpha=float(cfg.get("BEAM_ALPHA", 0.0)),
        temperature=float(cfg.get("BEAM_TEMPERATURE", 0.0)),
        temp_end=float(cfg.get("BEAM_TEMP_END", 0.0)), max_length=L,
        seed=int(cfg.get("SEED", 0)), heartbeat_s=cfg.get("HEARTBEAT_EVERY_S", 60.0),
        progress=log)
    _mirror(out_path, mirror)
    result.update(summarise(out_path))
    log(json.dumps(result, indent=2))
    return result


STAGES = {"convert": stage_convert, "parity": stage_parity,
          "train": stage_train, "beam_eval": stage_beam}


def main(cfg, log=print):
    stage = cfg.get("STAGE", "parity")
    if stage not in STAGES:
        raise SystemExit(f"unknown STAGE {stage!r}; expected one of {sorted(STAGES)}")
    log(f"=== stage {stage} ===")
    return STAGES[stage](cfg, log=log)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", default="parity", choices=sorted(STAGES))
    p.add_argument("--config", default=None, help="json file of CONFIG overrides")
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = p.parse_args()

    conf = dict(make_config())
    conf.update({
        "STAGE": a.stage, "DEVICE": "auto",
        "CKPT_DIR": "ppo_checkpoints/610model", "CKPT_STEP": None,
        "PARAMS_NPZ": "ppo_checkpoints/610model_params.npz",
        "OUT_DIR": os.path.join(ROOT, "results", "ppo"),
        "EVAL_DATASET": "1190MS", "EVAL_START": 0, "EVAL_END": None,
        "BEAM_WIDTH": 8, "BEAM_MAX_STEPS": 100, "BEAM_ALPHA": 0.0,
        "USE_WANDB": False, "HEARTBEAT_EVERY_S": 60.0, "SAVE_EVERY": 25,
    })
    if a.config:
        with open(a.config) as fh:
            conf.update(json.load(fh))
    for kv in a.set:
        k, _, v = kv.partition("=")
        try:
            conf[k] = json.loads(v)
        except ValueError:
            conf[k] = v
    conf["STAGE"] = a.stage
    main(conf)
