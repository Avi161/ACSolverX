"""`VecACS`: the reward, the auto-reset, and the three fused wrappers.

The wrapper behaviour is the part most likely to be ported "sensibly" and
therefore wrongly -- especially the reward normaliser, which in JAX runs inside
the vmap and is per-env with a pseudo-batch of 48, not the batch-level
normaliser its name suggests.
"""

import math
import random

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, acs_spec                       # noqa: E402
from experiments.ppo.acs_env import INT32_MAX, VecACS                # noqa: E402
from experiments.ppo.policy import RelativeDualRingActorCritic       # noqa: E402

L = 24


@pytest.fixture(scope="module")
def presentations():
    return acs_data.load_presentations("AC19_extended", L)


def legal_actions(x, generator):
    mask = RelativeDualRingActorCritic.action_mask(x, L).to(torch.float32)
    mask = torch.where(mask.sum(-1, keepdim=True) > 0, mask, torch.ones_like(mask))
    return torch.multinomial(mask, 1, generator=generator).squeeze(1)


def test_ms_prefix_is_derived_not_hardcoded():
    """634 for the extended file, 0 for AC19 -- the pin must come from the data."""
    assert acs_data.ms_prefix_length("AC19_extended") == 634
    assert acs_data.ms_prefix_length("AC19") == 0
    assert acs_data.ms_prefix_length("1190MS") == 1190


def test_reward_and_termination_follow_ac_s(presentations):
    env = VecACS(presentations[:3000], 64, max_length=L, max_steps=12, device="cpu", seed=0)
    gen = torch.Generator()
    gen.manual_seed(1)
    for _ in range(30):
        _, _, _, info = env.step(legal_actions(env.obs(), gen))
        nnz, raw = info["length"], info["raw_reward"]
        expect = torch.where(info["terminated"], torch.full_like(raw, 1000.0),
                             -nnz.clamp(max=10).to(torch.float32))
        assert torch.equal(raw, expect)
        assert torch.equal(info["terminated"], nnz == 2)


def test_step_matches_the_scalar_spec(presentations):
    env = VecACS(presentations[:2000], 32, max_length=L, max_steps=64, device="cpu", seed=3)
    gen = torch.Generator()
    gen.manual_seed(2)
    shadow = [r.tolist() for r in env.x]
    for _ in range(20):
        a = torch.randint(0, 2 * 2 * L * L, (32,), generator=gen)
        pre_done = env.time + 1 >= env.max_steps
        _, _, done, info = env.step(a)
        for n in range(32):
            sx, sr, st = acs_spec.step(shadow[n], int(a[n]), L)
            assert float(info["raw_reward"][n]) == sr
            assert bool(info["terminated"][n]) == st
            shadow[n] = env.x[n].tolist() if bool(done[n]) else sx
            if bool(done[n]):
                assert st or bool(pre_done[n]), "done without termination or truncation"


def test_normalizer_is_per_env_with_a_48_row_pseudo_batch(presentations):
    """`wrappers.NormalizeVecReward` under vmap: obs.shape[0] is 48, batch_var 0."""
    env = VecACS(presentations[:500], 8, max_length=L, max_steps=6, gamma=0.9, device="cpu", seed=4)
    gen = torch.Generator()
    gen.manual_seed(5)
    mean = np.zeros(8, np.float64)
    var = np.ones(8, np.float64)
    count = np.full(8, 1e-4)
    ret = np.zeros(8, np.float64)
    for _ in range(15):
        _, norm_reward, done, info = env.step(legal_actions(env.obs(), gen))
        raw = info["raw_reward"].numpy().astype(np.float64)
        ret = ret * 0.9 * (~done.numpy()) + raw
        delta = ret - mean
        tot = count + 48.0
        mean = mean + delta * 48.0 / tot
        var = (var * count + delta ** 2 * count * 48.0 / tot) / tot
        count = tot
        assert np.allclose(norm_reward.numpy(), raw / np.sqrt(var + 1e-8), rtol=2e-4, atol=2e-4)
    assert not np.allclose(var, var[0]), "each env must carry its own variance"


def test_pinned_envs_never_move_and_the_rest_resample(presentations):
    env = VecACS(presentations[:400], 32, max_length=L, max_steps=4, device="cpu",
                 seed=6, n_pinned=8)
    pinned0 = env.idx[:8].clone()
    gen = torch.Generator()
    gen.manual_seed(7)
    moved = torch.zeros(32, dtype=torch.bool)
    for _ in range(25):
        before = env.idx.clone()
        env.step(legal_actions(env.obs(), gen))
        moved |= env.idx != before
    assert torch.equal(env.idx[:8], pinned0)
    assert not bool(moved[:8].any())
    assert bool(moved[8:].any()), "sampling envs should have drawn a new state"


def test_solved_paths_replay_to_the_trivial_presentation(presentations):
    """The recorded best path must actually solve, replayed through the spec."""
    env = VecACS(presentations[:4000], 128, max_length=L, max_steps=24, device="cpu", seed=8)
    gen = torch.Generator()
    gen.manual_seed(9)
    for _ in range(120):
        env.step(legal_actions(env.obs(), gen))
    solved = torch.nonzero(env.solved_idx).flatten().tolist()
    assert solved, "no presentation solved; the fixture stopped exercising this path"
    for idx in solved[:20]:
        n = int(env.path_lengths[idx])
        assert 0 < n <= 24
        x = presentations[idx].astype(int).tolist()
        for a in env.best_paths[idx, :n].tolist():
            assert a >= 0
            x, _, term = acs_spec.step(x, a, L)
        assert term, f"recorded path for {idx} does not end at a trivial presentation"


def test_sampling_probabilities_prefer_the_unsolved(presentations):
    env = VecACS(presentations[:600], 64, max_length=L, max_steps=8, device="cpu", seed=10)
    gen = torch.Generator()
    gen.manual_seed(11)
    for _ in range(60):
        env.step(legal_actions(env.obs(), gen))
    attempts = env.attempts.numpy()
    solves = env.solves.numpy()
    assert attempts.sum() > 0
    expect = (1 - solves / (attempts + env.beta)) / np.sqrt(1 + attempts)
    assert np.allclose(env.probs.numpy(), expect / expect.sum(), rtol=1e-5, atol=1e-8)
    assert math.isclose(float(env.probs.sum()), 1.0, rel_tol=1e-5)


def test_untouched_states_keep_the_placeholder(presentations):
    env = VecACS(presentations[:300], 16, max_length=L, max_steps=5, device="cpu", seed=12)
    assert int(env.path_lengths.min()) == INT32_MAX
    assert int(env.solved_idx.sum()) == 0
    gen = torch.Generator()
    gen.manual_seed(13)
    for _ in range(20):
        env.step(legal_actions(env.obs(), gen))
    unsolved = ~env.solved_idx
    assert torch.all(env.path_lengths[unsolved] == INT32_MAX)


def test_repad_round_trips_through_a_wider_layout():
    raw = acs_data.read_raw("1190MS")[:50]
    for row in raw:
        wide = acs_data.repad(row, 40)
        assert len(wide) == 80
        assert acs_data.repad(wide, 24) == acs_data.repad(row, 24)
    with pytest.raises(ValueError):
        acs_data.repad([1, 2, 1, 2, -1, -2, 0, 0], 2)


def test_random_and_masked_actions_agree_with_the_spec_over_many_steps(presentations):
    rng = random.Random(21)
    env = VecACS(presentations[:1500], 24, max_length=L, max_steps=96, device="cpu", seed=14)
    shadow = [r.tolist() for r in env.x]
    for _ in range(15):
        a = torch.tensor([rng.randrange(2 * 2 * L * L) for _ in range(24)])
        _, _, done, _ = env.step(a)
        for n in range(24):
            sx, _, _ = acs_spec.step(shadow[n], int(a[n]), L)
            shadow[n] = env.x[n].tolist() if bool(done[n]) else sx
        assert [r.tolist() for r in env.x] == shadow
