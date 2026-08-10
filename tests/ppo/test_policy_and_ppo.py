"""The network port, the weight transplant, and the PPO arithmetic.

The cross-framework gate (same weights, same batch, JAX vs torch) lives in
`run_ppo.stage_parity` and can only close where JAX is installed. What is
checkable everywhere -- and checked here -- is that the transplant map is
complete and shape-exact against the *shipped* checkpoint's own metadata, that
the action mask is exactly the set of finite logits, and that GAE and the
gradient-accumulation split are the arithmetic they claim to be.
"""

import json
import os
import sys

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data                                 # noqa: E402
from experiments.ppo.acs_env import VecACS                           # noqa: E402
from experiments.ppo.policy import (                                 # noqa: E402
    RelativeDualRingActorCritic, action_stats)
from experiments.ppo.ppo import DEFAULT_CONFIG, PPOTrainer, make_config   # noqa: E402
from experiments.ppo.transplant import flat_to_state_dict            # noqa: E402

L = 24
CKPT_META = os.path.join(
    acs_data.ROOT, "ppo_checkpoints", "610model", "1000", "params",
    "array_metadatas", "process_0")


def test_hyperparameters_match_the_shipped_checkpoint():
    """`ppo_checkpoints/610model` saved its config as plain JSON. Use it."""
    saved = json.load(open(os.path.join(
        acs_data.ROOT, "ppo_checkpoints", "610model", "1000", "config", "metadata")))
    cfg = make_config()
    for k in ("LR", "NUM_ENVS", "NUM_STEPS", "UPDATE_EPOCHS", "NUM_MINIBATCHES",
              "GAMMA", "GAE_LAMBDA", "CLIP_EPS", "ENT_COEF", "VF_COEF",
              "MAX_GRAD_NORM", "ACTIVATION", "ANNEAL_LR", "CYCLE_PENALTY",
              "NOOP_PENALTY", "MINIBATCH_SIZE"):
        assert cfg[k] == saved[k], f"{k}: ours {cfg[k]!r} vs checkpoint {saved[k]!r}"
    assert cfg["NUM_UPDATES"] == int(saved["NUM_UPDATES"])
    assert DEFAULT_CONFIG["SEED"] == saved["SEED"] == 142


@pytest.mark.skipif(not os.path.exists(CKPT_META), reason="610model not present")
def test_transplant_covers_every_checkpoint_array():
    meta = json.load(open(CKPT_META))
    flat = {m["array_metadata"]["param_name"].removeprefix("params."):
            np.zeros(m["array_metadata"]["write_shape"], np.float32)
            for m in meta["array_metadatas"]}
    model = RelativeDualRingActorCritic(max_len=L)
    sd = flat_to_state_dict(flat, num_layers=len(model.blocks))
    report = model.load_state_dict(sd, strict=False)
    assert report.unexpected_keys == []
    assert [k for k in report.missing_keys if not k.endswith("base_rel_dist")] == []
    assert sum(int(np.prod(v.shape)) for v in flat.values()) == \
        sum(p.numel() for p in model.parameters())


def test_an_unmapped_parameter_is_an_error_not_a_silent_skip():
    with pytest.raises(KeyError):
        flat_to_state_dict({"Dense_9.kernel": np.zeros((4, 4), np.float32)})


def test_action_mask_is_exactly_the_finite_logits():
    pres = acs_data.load_presentations("1190MS", L)
    obs = torch.as_tensor(pres[:64], dtype=torch.int64)
    torch.manual_seed(0)
    model = RelativeDualRingActorCritic(max_len=L).eval()
    with torch.no_grad():
        logits, value = model(obs)
    mask = RelativeDualRingActorCritic.action_mask(obs, L)
    assert torch.equal(mask, logits > -1e8)
    assert value.shape == (64,)
    assert logits.shape == (64, 2 * 2 * L * L)
    assert bool((mask.sum(-1) > 0).all()), "every start state must have a legal move"


def test_action_mask_is_the_seam_cancellation_rule():
    """`(k1-1, k2, j)` is legal iff the two seam letters cancel and neither is pad."""
    pres = acs_data.load_presentations("1190MS", L)
    obs = torch.as_tensor(pres[:16], dtype=torch.int64)
    mask = RelativeDualRingActorCritic.action_mask(obs, L).reshape(16, L, L, 2, 2)
    r1, r2 = obs[:, :L], obs[:, L:]
    for b in range(16):
        for a in range(0, L, 5):
            for c in range(0, L, 7):
                pad = bool(r1[b, a] != 0 and r2[b, c] != 0)
                assert bool(mask[b, a, c, 0, 0]) == (pad and int(r1[b, a]) == -int(r2[b, c]))
                assert bool(mask[b, a, c, 1, 1]) == (pad and int(r1[b, a]) == int(r2[b, c]))
                assert bool(mask[b, a, c, 0, 1]) == bool(mask[b, a, c, 1, 1])


def test_log_prob_and_entropy_ignore_masked_actions():
    torch.manual_seed(1)
    logits = torch.randn(4, 8)
    logits[:, 5:] = -1e9
    a = torch.tensor([0, 1, 2, 3])
    log_prob, entropy = action_stats(logits, a)
    ref = torch.log_softmax(logits[:, :5], -1)
    assert torch.allclose(log_prob, ref.gather(1, a.unsqueeze(1)).squeeze(1), atol=1e-6)
    assert torch.allclose(entropy, -(ref.exp() * ref).sum(-1), atol=1e-6)
    assert float(entropy.max()) <= np.log(5) + 1e-5


def _tiny_trainer(num_envs=8, num_steps=4, minibatches=2, micro=None):
    pres = acs_data.load_presentations("1190MS", L)[:64]
    cfg = make_config(NUM_ENVS=num_envs, NUM_STEPS=num_steps, NUM_MINIBATCHES=minibatches,
                      TOTAL_TIMESTEPS=num_envs * num_steps * 3, UPDATE_EPOCHS=1,
                      MICRO_BATCH=micro or num_envs * num_steps, SEED=0)
    env = VecACS(pres, num_envs, max_length=L, max_steps=num_steps,
                 gamma=cfg["GAMMA"], device="cpu", seed=0)
    return PPOTrainer(env, cfg, "cpu")


def test_gae_matches_the_recursion():
    tr = _tiny_trainer()
    torch.manual_seed(2)
    T, N = tr.cfg["NUM_STEPS"], tr.cfg["NUM_ENVS"]
    roll = {"rewards": torch.randn(T, N), "values": torch.randn(T, N),
            "dones": (torch.rand(T, N) < 0.3).float(), "last_value": torch.randn(N)}
    adv, targets = tr.gae(roll)

    g, lam = tr.cfg["GAMMA"], tr.cfg["GAE_LAMBDA"]
    ref = torch.zeros(T, N)
    for n in range(N):
        run, nxt = 0.0, float(roll["last_value"][n])
        for t in range(T - 1, -1, -1):
            d = float(roll["dones"][t, n])
            delta = float(roll["rewards"][t, n]) + g * nxt * (1 - d) - float(roll["values"][t, n])
            run = delta + g * lam * (1 - d) * run
            ref[t, n] = run
            nxt = float(roll["values"][t, n])
    assert torch.allclose(adv, ref, atol=1e-5)
    assert torch.allclose(targets, ref + roll["values"], atol=1e-5)


def test_gradient_accumulation_equals_one_big_minibatch():
    """`MICRO_BATCH` must be a memory knob, not a change to the objective."""
    grads = []
    for micro in (32, 8):
        tr = _tiny_trainer(num_envs=8, num_steps=4, minibatches=1, micro=micro)
        torch.manual_seed(3)
        roll = tr.collect()
        adv, targets = tr.gae(roll)
        tr.gen.manual_seed(99)
        tr.opt.zero_grad(set_to_none=True)
        tr.learn(roll, adv, targets)
        grads.append([p.grad.clone() for p in tr.model.parameters() if p.grad is not None])
    for a, b in zip(*grads):
        assert torch.allclose(a, b, atol=2e-5, rtol=2e-4)


def test_a_pin_wider_than_the_env_count_is_clamped_and_said_out_loud(tmp_path):
    """Shrinking NUM_ENVS for a smoke run must not silently pin more than exist."""
    from experiments.ppo.run_ppo import stage_train

    lines = []
    out = stage_train({"DEVICE": "cpu", "DATASET": "1190MS", "NUM_ENVS": 8,
                       "NUM_STEPS": 4, "MICRO_BATCH": 32, "MAX_UPDATES": 1,
                       "OUT_DIR": str(tmp_path), "SAVE_EVERY": 1, "USE_WANDB": False,
                       "MAX_RELATOR_LENGTH": L},
                      log=lines.append)
    assert out["updates"] == 1
    joined = "\n".join(str(l) for l in lines)
    assert "not a paper arm" in joined
    assert "8 envs pinned deterministically, 0 sampling" in joined


def test_one_update_runs_and_is_resumable(tmp_path):
    tr = _tiny_trainer()
    m = tr.step_update()
    assert m["update"] == 1
    assert m["global_step"] == tr.cfg["NUM_STEPS"] * tr.cfg["NUM_ENVS"]
    assert np.isfinite(m["loss_policy"]) and np.isfinite(m["loss_value"])

    blob = tr.state_dict()
    path = tmp_path / "ckpt.pt"
    torch.save(blob, path)

    tr2 = _tiny_trainer()
    tr2.load_state_dict(torch.load(path, map_location="cpu", weights_only=False))
    assert tr2.update == 1
    assert torch.equal(tr2.env.x, tr.env.x)
    assert torch.equal(tr2.env.idx, tr.env.idx)
    assert torch.allclose(tr2.env.probs, tr.env.probs)
    for a, b in zip(tr.model.parameters(), tr2.model.parameters()):
        assert torch.equal(a, b)


def test_the_metadata_tree_is_found_however_orbax_wraps_it():
    """`610model` was trained on ROCm, so a plain restore dies off-ROCm.

    The fix restores every leaf as numpy, which needs the parameter pytree out of
    `metadata()` -- and orbax has moved that twice. Getting the unwrap wrong does
    not raise here, it raises deep inside orbax with a pytree structure error, so
    pin the unwrap itself.
    """
    from experiments.ppo.transplant import _map_leaves, _metadata_tree

    tree = {"params": {"Dense_0": {"kernel": object()}}}

    class TreeMeta:
        def __init__(self, t):
            self.tree = t

    class StepMeta:                       # current orbax
        def __init__(self, t):
            self.item_metadata = TreeMeta(t)

    class OlderMeta:                      # item_metadata is the tree itself
        def __init__(self, t):
            self.item_metadata = t

    for md in (StepMeta(tree), OlderMeta(tree), tree):
        assert _metadata_tree(md) is tree

    with pytest.raises(TypeError):
        _metadata_tree(object())

    marked = _map_leaves(tree, lambda _: "LEAF")
    assert marked == {"params": {"Dense_0": {"kernel": "LEAF"}}}


@pytest.mark.skipif(not os.path.exists(CKPT_META), reason="610model not present")
def test_the_shipped_checkpoint_transplants_into_a_working_policy():
    """End to end on the real weights: 95 arrays in, finite masked logits out."""
    npz = os.path.join(acs_data.ROOT, "ppo_checkpoints", "610model_params.npz")
    if not os.path.exists(npz):
        pytest.skip("run `--stage convert` first (needs orbax)")
    from experiments.ppo.transplant import load_into

    model = RelativeDualRingActorCritic(max_len=L).eval()
    load_into(model, npz)
    obs = torch.as_tensor(acs_data.load_presentations("1190MS", L)[:64], dtype=torch.int64)
    with torch.no_grad():
        logits, value = model(obs)
    assert torch.equal(RelativeDualRingActorCritic.action_mask(obs, L), logits > -1e8)
    assert torch.isfinite(value).all()
    # a trained value head is not centred on zero the way an initialised one is
    assert abs(float(value.mean())) > 0.5


def test_the_distrax_shim_matches_the_real_packages_semantics():
    """`Categorical(logits=l).logits` is `log_softmax(l)`, NOT `l`.

    Measured off distrax 0.1.9, not assumed -- and the distinction is the whole
    reason the parity gate compares log-probabilities. A shim that returned the
    raw array would silently make the gate compare two different quantities and
    report a per-row logsumexp offset as a broken port.
    """
    jax = pytest.importorskip("jax")
    import jax.numpy as jnp
    from experiments.ppo.run_ppo import _ensure_distrax

    saved = sys.modules.pop("distrax", None)
    blocker = _DistraxBlocker()
    sys.meta_path.insert(0, blocker)
    try:
        assert _ensure_distrax(lambda *_: None) == "shim"
        import distrax
        raw = jnp.asarray([[1.0, 2.0, -3.0, 0.5]])
        got = np.asarray(distrax.Categorical(logits=raw).logits)
        expect = np.asarray(jax.nn.log_softmax(raw, axis=-1))
        assert np.allclose(got, expect, atol=1e-6)
        assert not np.allclose(got, np.asarray(raw)), "the shim must normalise"
        # the property is what `network.py` reads; probs= is not supported
        with pytest.raises(TypeError):
            distrax.Categorical(probs=raw)
    finally:
        sys.meta_path.remove(blocker)
        sys.modules.pop("distrax", None)
        if saved is not None:
            sys.modules["distrax"] = saved


class _DistraxBlocker:
    """Make `import distrax` fail the way a Colab without it would."""

    def find_spec(self, name, path, target=None):
        if name == "distrax" or name.startswith("distrax."):
            raise ImportError("blocked by the test")
        return None


def test_the_parity_gate_is_diagnostic_and_cannot_stop_the_ladder():
    """Whatever goes wrong under JAX, `beam_upstream` must still get to run.

    A real A100 session was lost to `ModuleNotFoundError: No module named
    'distrax'` raised out of `network.py` -- an optional dependency of a stage
    that only *reports*, killing the stage that produces the number. Nothing
    downstream imports JAX, so the gate reports and steps aside.
    """
    from experiments.ppo import run_ppo

    for boom in (ImportError("no distrax"), RuntimeError("jax died"),
                 ValueError("sharding")):
        def explode(*a, **k):
            raise boom

        saved = run_ppo._jax_parity_inner
        run_ppo._jax_parity_inner = explode
        try:
            lines = []
            got = run_ppo._jax_parity({}, None, None, "cpu", lines.append)
        finally:
            run_ppo._jax_parity_inner = saved

        assert got["jax_available"] is False
        assert type(boom).__name__ in got["jax_error"]
        assert "parity_ok" not in got, "a gate that did not run is not a pass"
        assert any("NOT closed" in ln for ln in lines), "the failure must be loud"


def test_a_wandb_failure_cannot_end_a_training_run(monkeypatch, tmp_path):
    """Tracking describes the work; it must never be able to destroy it.

    `wandb.init` reaches the network and can fail on things unrelated to this
    machine -- an outage, a quota, a permission on the team entity. Only
    ImportError was caught, so any of those would have propagated out of
    stage_train and ended hours of training. The smoke could not have caught it
    either: SMOKE_RUN forces USE_WANDB off, so the first init ever executed
    would have been the real run.
    """
    import types
    from experiments.ppo import run_ppo

    for exc in (RuntimeError("entity 'x' not found"),
                OSError("connection reset"),
                ValueError("quota exceeded")):
        fake = types.ModuleType("wandb")

        def _boom(*_a, _e=exc, **_k):
            raise _e

        fake.init = _boom
        monkeypatch.setitem(sys.modules, "wandb", fake)

        lines = []
        got = run_ppo._wandb_init({"USE_WANDB": True}, {}, "tag", lines.append)
        assert got is None, f"{type(exc).__name__} must degrade, not propagate"
        assert any("W&B unavailable" in ln for ln in lines)
        assert any("training continues" in ln for ln in lines)


def test_wandb_off_does_not_even_import_it(monkeypatch):
    """The smoke path sets USE_WANDB False; that must stay a zero-cost path."""
    from experiments.ppo import run_ppo

    # None in sys.modules makes `import wandb` raise -- so if the guard ever
    # stops short-circuiting, this test fails instead of silently passing.
    monkeypatch.setitem(sys.modules, "wandb", None)
    assert run_ppo._wandb_init({"USE_WANDB": False}, {}, "tag", print) is None
