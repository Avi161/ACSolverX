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

    # Persisted because the gate is worth more than the cell that printed it: a
    # Colab session that scrolls away or dies still has to be able to answer
    # "did parity pass", and `stage_report` reads this rather than re-running it.
    out["device"] = str(device)
    if cfg.get("OUT_DIR"):
        os.makedirs(cfg["OUT_DIR"], exist_ok=True)
        parity_path = os.path.join(cfg["OUT_DIR"], "parity.json")
        with open(parity_path, "w") as fh:
            json.dump(out, fh, indent=2, default=float)
        _mirror(parity_path, cfg.get("MIRROR_DIR"))

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


def _ensure_distrax(log):
    """`network.py` imports distrax for exactly one thing: wrapping the logits.

    distrax pulls in tensorflow-probability, which is the dependency on this
    tree most likely to fail to install or to fight the jax already on a Colab
    image. Rather than let that take the gate down, stand in a shim for the one
    class used -- with the semantics *measured* off distrax 0.1.9 rather than
    assumed: `Categorical(logits=l).logits` returns `log_softmax(l)`, not `l`.
    """
    try:
        import distrax                                                  # noqa: F401
        return "installed"
    except ImportError:
        pass

    import types
    import jax.nn as jnn

    class Categorical:
        def __init__(self, logits=None, probs=None):
            if logits is None:
                raise TypeError("the distrax shim only supports logits=")
            self._logits = logits

        @property
        def logits(self):
            return jnn.log_softmax(self._logits, axis=-1)

    mod = types.ModuleType("distrax")
    mod.Categorical = Categorical
    sys.modules["distrax"] = mod
    log("distrax is not installed -- standing in a Categorical shim (log_softmax "
        "semantics, matching distrax 0.1.9) so the gate can still run")
    return "shim"


def _jax_parity(cfg, model, obs, device, log):
    """The real gate: same weights, same batch, two frameworks.

    **Diagnostic, never load-bearing.** Nothing downstream imports JAX -- the
    beam and the trainer are pure torch -- so every failure in here is reported
    and stepped over. A missing optional dependency must not cost a GPU session
    that was going to spend its time on `beam_upstream`.
    """
    try:
        return _jax_parity_inner(cfg, model, obs, log)
    except Exception as exc:                        # noqa: BLE001 - see docstring
        log(f"cross-framework gate NOT closed -- {type(exc).__name__}: {exc}")
        log("  the torch stack is unaffected; beam and training import no JAX. "
            "Continuing.")
        return {"jax_available": False, "jax_error": f"{type(exc).__name__}: {exc}"}


def _jax_parity_inner(cfg, model, obs, log):
    """Compared as log-probabilities over *legal* actions. Both parts matter.

    `distrax.Categorical(logits=l).logits` is `log_softmax(l)`, so comparing it
    against raw torch logits differs by the per-row logsumexp -- 5.98 on the
    shipped checkpoint, which reads as a broken port and is not one. The
    signature of that mistake is a large maximum with near-zero spread *within*
    each row (2.6e-06 here), and log-probs are what the beam ranks on anyway.

    The masked entries are excluded because they are a -1e9 sentinel, not a
    prediction: log_softmax leaves them around -1e9, where a float32 ulp is 64,
    so their difference measures rounding on a constant. The two masks are
    compared directly instead, which is the stronger check -- if they disagreed
    the beam would be exploring different actions in the two frameworks.

    Expected magnitude: **~4e-05** on the shipped checkpoint, measured identical
    on CPU and MPS, so it is float32 accumulation through the flax net and not
    an accelerator artefact. The 1e-4 threshold is a sanity bound with ~2.5x
    headroom; the checks that actually decide anything -- the two masks and the
    argmax -- are exact, and `parity_ok` requires them too.
    """
    import jax
    import jax.numpy as jnp

    sys.path.insert(0, ROOT)
    jax.config.update("jax_default_matmul_precision", "float32")
    distrax_source = _ensure_distrax(log)
    from network import RelativeDualRingActorCritic as FlaxNet          # noqa: E402
    from experiments.ppo.transplant import read_orbax_params            # noqa: E402

    ckpt_dir = os.path.join(ROOT, cfg["CKPT_DIR"])
    flat, step = read_orbax_params(ckpt_dir, cfg.get("CKPT_STEP"))
    params = {"params": _unflatten(flat)}
    net = FlaxNet(activation=cfg["ACTIVATION"])
    pi, value = net.apply(params, jnp.asarray(obs.cpu().numpy(), dtype=jnp.int8))
    with torch.no_grad():
        t_logits, t_value = model(obs)

    j_logprob = np.asarray(pi.logits, dtype=np.float64)
    # Normalised in numpy/float64, not `torch.log_softmax(...).double()`: MPS has
    # no float64 at all, and doing it on-device would make the gate's own
    # arithmetic vary by accelerator. The beam ranks raw logits, so this
    # log_softmax exists only to cancel distrax's.
    t_raw = t_logits.cpu().numpy().astype(np.float64)
    _m = t_raw.max(axis=-1, keepdims=True)
    t_logprob = t_raw - _m - np.log(np.exp(t_raw - _m).sum(axis=-1, keepdims=True))

    legal = RelativeDualRingActorCritic.action_mask(
        obs, cfg["MAX_RELATOR_LENGTH"]).cpu().numpy()
    j_legal = j_logprob > -1e6                     # the -1e9 sentinel, post-softmax
    masks_agree = bool((legal == j_legal).all())

    d_logprob = float(np.abs(j_logprob - t_logprob)[legal].max()) if legal.any() else 0.0
    d_value = float(np.abs(np.asarray(value, dtype=np.float64)
                           - t_value.cpu().numpy().astype(np.float64)).max())

    # What actually reaches the beam: the ranking, not the numbers.
    t_rank = np.where(legal, t_logprob, -np.inf)
    j_rank = np.where(legal, j_logprob, -np.inf)
    argmax_agree = int((t_rank.argmax(-1) == j_rank.argmax(-1)).sum())
    k = int(min(16, legal.sum(-1).min()))
    topk_agree = None
    if k > 0:
        t_top = np.argsort(-t_rank, axis=-1)[:, :k]
        j_top = np.argsort(-j_rank, axis=-1)[:, :k]
        topk_agree = int(sum(set(a) == set(b) for a, b in zip(t_top, j_top)))

    n = len(t_logprob)
    log(f"JAX vs torch on step {step} ({distrax_source} distrax): "
        f"max|dlogprob|={d_logprob:.3e} max|dvalue|={d_value:.3e} "
        f"masks_agree={masks_agree} argmax {argmax_agree}/{n}"
        + (f" top{k} {topk_agree}/{n}" if topk_agree is not None else ""))
    return {"jax_available": True, "jax_step": step, "distrax": distrax_source,
            "max_abs_logprob_diff_legal": d_logprob, "max_abs_value_diff": d_value,
            "action_masks_agree": masks_agree,
            "argmax_agreement": f"{argmax_agree}/{n}",
            "topk_agreement": None if topk_agree is None else f"{topk_agree}/{n} (k={k})",
            "parity_ok": bool(d_logprob < 1e-4 and d_value < 1e-4
                              and masks_agree and argmax_agree == n)}


def _unflatten(flat):
    tree = {}
    for k, v in flat.items():
        node = tree
        parts = k.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = v
    return tree


def train_tag(stem, seed):
    """Checkpoint / jsonl / W&B identity of one training arm.

    The update count is deliberately absent: this names a *continuing* run, and
    the update it has reached lives inside the checkpoint. Anything that reads
    the weights and reports a number (`beam_tag`) must add it back.
    """
    return f"ppo-drt-{stem}-s{int(seed)}"


def stage_train(cfg, log=print):
    device = pick_device(cfg.get("DEVICE", "auto"))
    set_matmul_precision(cfg.get("ALLOW_TF32", False))
    config = make_config(**{k: v for k, v in cfg.items() if k in DEFAULT_CONFIG})

    L = config["MAX_RELATOR_LENGTH"]
    stem = config["DATASET"]
    pres = acs_data.load_presentations(stem, L)
    n_pinned = acs_data.ms_prefix_length(stem)
    if n_pinned > config["NUM_ENVS"]:
        # Only reachable by shrinking NUM_ENVS for a smoke run. Clamping keeps it
        # runnable; saying so keeps its solve count from being read as an arm.
        log(f"NOTE: {stem} pins {n_pinned} presentations but NUM_ENVS is "
            f"{config['NUM_ENVS']} -- clamping the pin. Every env is pinned and none "
            f"resample, so this is a smoke configuration, not a paper arm.")
        n_pinned = config["NUM_ENVS"]
    log(f"{stem}: {len(pres)} presentations, MS prefix {n_pinned} "
        f"-> {n_pinned} envs pinned deterministically, {config['NUM_ENVS'] - n_pinned} sampling")

    env = VecACS(pres, config["NUM_ENVS"], max_length=L, max_steps=config["NUM_STEPS"],
                 gamma=config["GAMMA"], cycle_penalty=config["CYCLE_PENALTY"],
                 noop_penalty=config["NOOP_PENALTY"], n_pinned=n_pinned,
                 device=device, seed=config["SEED"])
    trainer = PPOTrainer(env, config, device)

    out_dir = cfg["OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    tag = cfg.get("RUN_TAG") or train_tag(stem, config["SEED"])
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
    """Tracking mirrors the jsonl; it is never the source of truth.

    So nothing in here may end a training run. `wandb.init` goes to the network,
    resolves an entity and a project and can fail for reasons that have nothing
    to do with this machine -- an outage, a quota, a permission on the team
    entity. Losing hours of training to that would repeat the distrax mistake
    exactly: a stage that only *describes* the work taking down the work.

    Catching only ImportError was not enough, and the smoke could not have found
    it -- SMOKE_RUN forces USE_WANDB off, so the first init ever executed would
    have been the real multi-hour run.
    """
    if not cfg.get("USE_WANDB"):
        return None
    try:
        import wandb
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
    except Exception as exc:                        # noqa: BLE001 - see docstring
        log(f"W&B unavailable -- {type(exc).__name__}: {exc}")
        log("  training continues; per-update metrics still go to the jsonl, "
            "which is what the report reads.")
        return None


def checkpoint_tag(cfg, src, update=None):
    """Filename-safe identity of the *weights* a beam run decoded.

    A `.pt` from `stage_train` is a moving target -- the same path holds update
    500 in the morning and update 1000 at night -- so the update count is part
    of the identity, not metadata. For the upstream artefact the step is only
    known when `CKPT_STEP` pins it; the `.npz` stem names the export otherwise.
    """
    stem = os.path.splitext(os.path.basename(str(src).rstrip("/")))[0]
    if update is None:
        update = cfg.get("CKPT_STEP")
    return f"{stem}-u{update}" if update is not None else stem


def beam_tag(cfg, ckpt_tag):
    """The beam jsonl is a resume key, so its name must carry every knob.

    `run_beam` skips presentations already in the file. Two seeds, two training
    arms, or one arm at two update counts sharing a name means the second eval
    writes nothing and reports the first one's solve count as its own -- a
    silent wrong number, not an error. Result-neutral knobs (`EVAL_START/END`,
    heartbeat, mirror) stay out: a slice is a subset of the same run's rows and
    merges into the same file correctly.
    """
    tag = (f"beam-{ckpt_tag}-{cfg['EVAL_DATASET']}"
           f"-w{int(cfg['BEAM_WIDTH'])}-t{int(cfg['BEAM_MAX_STEPS'])}"
           f"-L{cfg['MAX_RELATOR_LENGTH']}")
    alpha = float(cfg.get("BEAM_ALPHA", 0.0))
    if alpha:
        tag += f"-a{alpha:g}"
    t0, t1 = float(cfg.get("BEAM_TEMPERATURE", 0.0)), float(cfg.get("BEAM_TEMP_END", 0.0))
    if t0 or t1:                                  # sampling: the seed now matters
        tag += f"-T{t0:g}_{t1:g}-s{int(cfg.get('SEED', 0))}"
    return tag


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
        ckpt_tag = checkpoint_tag(cfg, src, blob.get("update"))
    else:
        src = os.path.join(ROOT, cfg["PARAMS_NPZ"])
        if not os.path.exists(src):
            src = os.path.join(ROOT, cfg["CKPT_DIR"])
        load_into(model, src, cfg.get("CKPT_STEP"))
        log(f"loaded upstream checkpoint {src}")
        ckpt_tag = checkpoint_tag(cfg, src)

    stem = cfg["EVAL_DATASET"]
    pres = acs_data.load_presentations(stem, L)
    out_dir = cfg["OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    tag = cfg.get("BEAM_TAG") or beam_tag(cfg, ckpt_tag)
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
        time_budget_s=cfg.get("BEAM_TIME_BUDGET_S"), progress=log,
        # Mirror on the heartbeat, not only at the end: the full eval runs for
        # hours and the VM's local disk does not survive a disconnect.
        checkpoint=(lambda p: _mirror(p, mirror)) if mirror else None)
    _mirror(out_path, mirror)
    result.update(summarise(out_path))
    log(json.dumps(result, indent=2))
    return result


def _environment():
    """What the numbers were produced on. A timing is meaningless without it."""
    env = {"torch": torch.__version__, "python": sys.version.split()[0],
           "cuda_available": torch.cuda.is_available(),
           "allow_tf32": bool(torch.backends.cuda.matmul.allow_tf32)}
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        env.update(gpu=props.name, gpu_memory_gb=round(props.total_memory / 2 ** 30, 1),
                   compute_capability=f"{props.major}.{props.minor}",
                   cuda=torch.version.cuda)
    try:
        import subprocess
        env["git_commit"] = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:                                  # not a clone, or no git
        env["git_commit"] = None
    return env


def stage_report(cfg, log=print):
    """Everything needed to judge a run from its artefacts alone.

    Built for the smoke round trip: run a few presentations at *production*
    beam settings, then hand this one file back. It answers the three questions
    a partial run has to answer before the full one is worth starting -- did the
    cross-framework gate pass, do the rows it wrote certify, and what does the
    measured per-presentation cost imply for all 1190 -- without needing the
    Colab scrollback, which is the first thing a disconnect destroys.

    Extrapolation is deliberately from *this* run's own mean seconds/row. It is
    an over-estimate whenever the slice is the easy head of the file (fast
    solves) and an under-estimate whenever it is the hard tail (150 full steps),
    so `seconds_per_row_min/max` ship alongside it rather than a bare ETA.
    """
    from experiments.ppo import verify_beam

    out_dir = cfg["OUT_DIR"]
    mirror = cfg.get("MIRROR_DIR")
    eval_stem = cfg.get("EVAL_DATASET", "1190MS")
    denom = len(acs_data.read_raw(eval_stem))

    report = {"environment": _environment(),
              "config": {k: cfg.get(k) for k in (
                  "SMOKE_RUN", "EVAL_DATASET", "EVAL_START", "EVAL_END", "BEAM_WIDTH",
                  "BEAM_MAX_STEPS", "BEAM_ALPHA", "BEAM_TIME_BUDGET_S", "ALLOW_TF32",
                  "MAX_RELATOR_LENGTH", "DATASET", "SEED", "MAX_UPDATES")},
              "eval_denominator": denom, "beam_runs": [], "training_runs": []}

    parity_path = os.path.join(out_dir, "parity.json")
    _seed_from_mirror(parity_path, mirror)
    if os.path.exists(parity_path):
        with open(parity_path) as fh:
            report["parity"] = json.load(fh)
    else:
        report["parity"] = None

    import glob
    for path in sorted(glob.glob(os.path.join(out_dir, "beam-*.jsonl"))):
        rows = []
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except ValueError:
                        pass
        if not rows:
            continue
        secs = [r["seconds"] for r in rows if "seconds" in r]
        solved = [r for r in rows if r.get("solved")]
        entry = {
            "file": os.path.basename(path), "rows": len(rows), "solved": len(solved),
            "solve_rate": round(len(solved) / len(rows), 4),
            "mean_path_length": round(float(np.mean([r["path_length"] for r in solved])), 2)
            if solved else None,
            "max_path_length": max((r["path_length"] for r in solved), default=None),
        }
        if secs:
            mean_s = float(np.mean(secs))
            entry.update(seconds_per_row_mean=round(mean_s, 3),
                         seconds_per_row_min=round(float(np.min(secs)), 3),
                         seconds_per_row_max=round(float(np.max(secs)), 3),
                         measured_wall_s=round(float(np.sum(secs)), 1),
                         projected_full_run_hours=round(mean_s * denom / 3600, 2))
        # The certificate check, on the rows this run actually produced.
        try:
            v = verify_beam.verify_file(path, log=lambda *_: None)
            entry["verified"] = v["verified"]
            entry["verify_failures"] = [f"line {ln} idx {i}: {why}"
                                        for ln, i, why in v["failures"][:10]]
        except ValueError as exc:                      # non-standard filename
            entry["verify_failures"] = [str(exc)]
        report["beam_runs"].append(entry)

    for path in sorted(glob.glob(os.path.join(out_dir, "ppo-drt-*.jsonl"))):
        if path.endswith("_solved.jsonl"):
            continue
        last = None
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        last = json.loads(line)
                    except ValueError:
                        pass
        if last:
            report["training_runs"].append({
                "file": os.path.basename(path), "update": last.get("update"),
                "sps": round(last.get("sps", 0)), "num_solved": last.get("num_solved"),
                "num_solved_pinned": last.get("num_solved_pinned"),
                "seconds_per_update": round(last.get("collect_s", 0) + last.get("learn_s", 0), 2)})

    os.makedirs(out_dir, exist_ok=True)
    # Distinct names so the full run does not overwrite the smoke report that
    # justified starting it -- the two are read side by side when a number moves.
    report_path = os.path.join(
        out_dir, "smoke_report.json" if cfg.get("SMOKE_RUN") else "report.json")
    with open(report_path, "w") as fh:
        json.dump(report, fh, indent=2, default=float)
    _mirror(report_path, mirror)

    log("=" * 72)
    log(json.dumps(report, indent=2, default=float))
    log("=" * 72)
    log(f"written to {report_path}" + (f" and mirrored to {mirror}" if mirror else ""))
    log("Paste the block between the ==== lines back into the chat.")
    return report


STAGES = {"convert": stage_convert, "parity": stage_parity,
          "train": stage_train, "beam_eval": stage_beam, "report": stage_report}


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
