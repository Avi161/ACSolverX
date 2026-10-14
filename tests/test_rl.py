"""Tests for the optional PyTorch RL extra (``acx.rl``); skipped when torch is missing."""
import json
import os
import subprocess
import sys

import pytest

torch = pytest.importorskip("torch")

from acx import data  # noqa: E402
from acx.core.words import Presentation  # noqa: E402
from acx.rl import beam, codec, convert, moves, policy, solve as rl_solve  # noqa: E402
from acx.rl.ppo import encode_rows, pinned_prefix, train  # noqa: E402
from acx.verify import replay  # noqa: E402

torch.set_num_threads(1)
REF = json.load(open(os.path.join(os.path.dirname(policy.CHECKPOINT), "jax_reference.json")))


@pytest.fixture(scope="module")
def model():
    return policy.pretrained()


def test_moves_match_jax():
    """123 transitions recorded from ``envs/ac_moves.py`` (random actions: no-ops, over-length, bad seams)."""
    x = torch.tensor([m[0] for m in REF["moves"]])
    a = torch.tensor([m[1] for m in REF["moves"]])
    out, over, _, _ = moves.s_move(x, *moves.decode_action(a, 24), 24)
    assert (out == torch.tensor([m[2] for m in REF["moves"]])).all()
    assert (out != x).any(-1).sum() > 20 and (out == x).all(-1).any()
    assert over.any() and (out[over] == x[over]).all()             # an over-length product is a no-op


def test_action_codec_roundtrip():
    """``decode_action`` is a bijection of ``[0, 4 L^2)`` onto ``(i, r, k1, k2)`` (its inverse is written out here)."""
    a = torch.arange(4 * 24 * 24)
    i, j, k1, k2 = moves.decode_action(a, 24)
    signed = torch.where(j == 0, k2, -(k2 + 1))
    assert (((k1 - 1) * 24 + signed) * 4 + (i * 2 + j) == a).all()
    assert (i.amax(), j.amax(), k1.min(), k1.max()) == (1, 1, 1, 24)


def test_policy_matches_jax(model):
    x = torch.tensor([p["obs"] for p in REF["policy"]])
    with torch.no_grad():
        logits, value = model(x)
    logp = torch.log_softmax(logits, -1)
    for k, p in enumerate(REF["policy"]):
        assert abs(float(value[k]) - p["value"]) < 1e-4
        assert int((logits[k] > -1e8).sum()) == p["legal"]
        for action, lp in p["top"]:
            assert abs(float(logp[k, action]) - lp) < 1e-4


def test_forward_in_chunks_equals_one_call(model):
    """``policy.forward``, which the beam search and the trainer share, gives the one-call result at any chunk size."""
    x = torch.tensor([p["obs"] for p in REF["policy"]])
    with torch.no_grad():
        logits, value = model(x)
        for chunk in (1, 2, len(x), 4096):
            chunked = policy.forward(model, x, chunk)
            assert torch.allclose(chunked[0], logits, atol=1e-5) and torch.allclose(chunked[1], value, atol=1e-5)


def test_checkpoint_conversion_is_exhaustive(model):
    """Every flax array maps to exactly one torch parameter (95 arrays, no silent skips)."""
    names = {n for n, _ in model.named_parameters()}
    assert set(torch.load(policy.CHECKPOINT, weights_only=True)) == names
    assert len(names) == 95
    with pytest.raises(KeyError):
        convert.to_state_dict({"Dense_9.kernel": torch.zeros(2, 2).numpy()})


def test_package_import_is_torch_free():
    """``acx.rl`` itself (the width ``L`` the config checks need) never imports torch; its modules do."""
    code = "import sys, acx.rl; assert 'torch' not in sys.modules and acx.rl.L == 24"
    subprocess.run([sys.executable, "-c", code], check=True)


def test_visited_table_is_sorted_fixed_size_and_ignores_dead_beams():
    visited = beam.Visited(torch.tensor(5), 4)
    hashes = torch.tensor([5, 7, 9])
    assert visited.contains(hashes).tolist() == [True, False, False]
    visited.add(hashes, torch.tensor([False, True, True]))              # 5 is dead this step: not added twice
    assert visited.contains(hashes).tolist() == [True, True, True]
    assert visited.table.tolist() == [5, 7, 9, beam.NEVER]


def test_best_of_each_hash_keeps_the_best_and_the_first_on_ties():
    hashes = torch.tensor([3, 1, 3, 1, 2])
    score = torch.tensor([0.5, 0.1, 0.9, 0.1, float("-inf")])
    assert beam.best_of_each_hash(hashes, score).tolist() == [False, True, True, False, True]


def test_beam_does_not_accumulate_the_value_bonus_as_log_probability(monkeypatch):
    # A probability-one path has log probability zero at every depth, even with a nonzero value heuristic.
    seen = []
    original = beam.top_children

    def forward(model, states, chunk):
        logits = torch.full((len(states), 16), -1e9)
        logits[:, 0] = 0
        return logits, torch.full((len(states),), 7.0)

    def top(*args):
        seen.append(args[3].tolist())
        return original(*args)

    def move(states, *args):
        new = states.clone()
        new[:, 0] += 1                 # distinct nonterminal states; action semantics are tested separately
        return (new, torch.zeros(len(states), dtype=torch.bool),
                torch.ones(len(states), dtype=torch.long), torch.ones(len(states), dtype=torch.long))

    monkeypatch.setattr(beam, "forward", forward)
    monkeypatch.setattr(beam, "top_children", top)
    monkeypatch.setattr(beam, "s_move", move)
    beam.beam_search(None, torch.ones(4, dtype=torch.int64), L=2, width=1, steps=3, alpha=1)
    assert seen == [[0.0], [0.0], [0.0]]


def test_nonzero_value_weight_retains_capture_parity(model):
    pres = data.load("ms640", ids=[0])[0].pres
    full = rl_solve.solve(pres, model, width=64, steps=30, alpha=0.5)
    fast = rl_solve.solve(pres, model, width=64, steps=30, alpha=0.5, capture_path=False)
    assert full.solved and (fast.solved, fast.pops, fast.path_length) == (full.solved, full.pops, full.path_length)
    assert replay(pres, full.path)[-1].is_trivial()


def test_beam_solves_easy_ms640_rows_and_replays(model):
    for row in data.load("ms640", ids=range(5)):
        res = rl_solve.solve(row.pres, model, width=64, steps=60)
        assert res.solved and res.path_length <= 6
        assert replay(row.pres, res.path, cap=24)[-1].is_trivial()
        assert res.stats["backend"] == "rl-beam" and res.pops == res.stats["evaluated"] > 0
    # width far above the legal-move count: illegal actions must never enter the beam
    res = rl_solve.solve(data.load("ms640", ids=[0])[0].pres, model, width=1024, steps=5)
    assert res.solved and res.pops < 50


class Uniform(torch.nn.Module):
    """The policy's legal-move mask with every legal action scored 0, so the beam alone decides what it keeps."""

    def __init__(self, inner):
        super().__init__()
        self.inner = inner

    def forward(self, x):
        logits, value = self.inner(x)
        return torch.where(logits < -1e8, logits, torch.zeros_like(logits)), value


@pytest.mark.parametrize("row, evaluated", [(0, 7), (2, 114), (4, 481)])
def test_beam_never_takes_an_illegal_action_under_a_uniform_model(model, row, evaluated):
    """These rows have 10 to 22 legal moves at the start and the beam holds 512, so an illegal action scoring above
    -inf would enter it. Every action of the path found is legal under the real policy and the path replays."""
    pres = data.load("ms640", ids=[row])[0].pres
    x = codec.encode(pres.reduced().rels)
    actions, stats = beam.beam_search(Uniform(model), x, cap=24, width=512, steps=12)
    assert actions and stats["evaluated"] == evaluated
    with torch.no_grad():
        for action in actions:
            assert model(x[None])[0][0, action] > -1e8
            x = moves.s_move(x[None], *moves.decode_action(torch.tensor([action]), 24), 24)[0][0]
    assert int((x != 0).sum()) == 2                                          # both relators of length 1
    assert replay(pres, codec.to_acx_path(pres, actions), cap=24)[-1].is_trivial()


def test_cap_is_applied_counted_and_bounded(model):
    pres = data.load("ms640", ids=[4])[0].pres
    res = rl_solve.solve(pres, model, width=64, steps=30, cap=6)
    assert res.solved and res.stats["cap_dropped"] > 0 and res.stats["cap"] == 6
    assert all(len(r) <= 6 for st in replay(pres, res.path, cap=6) for r in st.rels)
    assert rl_solve.solve(pres, model, width=64, steps=30).stats["cap_dropped"] == 0
    skipped = rl_solve.solve(pres, model, cap=4)                    # a start relator over the cap
    assert not skipped.solved and "skipped" in skipped.stats
    for bad in (None, 0, 25, True, "8", 8.0):          # True was a cap of 1; "8" a TypeError
        with pytest.raises(ValueError, match="cap"):
            rl_solve.solve(pres, model, cap=bad)


def test_unsolved_unsupported_and_trivial_rows(model):
    assert not rl_solve.solve(data.load("ms640", ids=[639])[0].pres, model, width=2, steps=2).solved
    res = rl_solve.solve(Presentation(3, ((1,), (2,), (3,))), model)
    assert res.solved and res.path == ()                            # already trivial
    res = rl_solve.solve(Presentation(3, ((1, 2, -1, -2), (2,), (3,))), model)
    assert not res.solved and "skipped" in res.stats


def test_bridge_follows_the_environment_on_random_walks(model):
    """Every non-no-op action is an acx S-move: the replayed state equals the environment state up to canonical form."""
    gen = torch.Generator().manual_seed(0)
    for row in data.load("ms640", ids=range(0, 640, 64)):
        x, actions = codec.encode(row.pres.reduced().rels), []
        for _ in range(8):
            with torch.no_grad():
                legal = (model(x[None])[0][0] > -1e8).nonzero().flatten()
            a = int(legal[torch.randint(len(legal), (1,), generator=gen)])
            y = moves.s_move(x[None], *moves.decode_action(torch.tensor([a]), 24), 24)[0][0]
            if (y == x).all():
                continue
            x, actions = y, actions + [a]
            if int((x != 0).sum()) == 2:
                break
        path = codec.to_acx_path(row.pres, actions)
        end = replay(row.pres, path, require_trivial=False)[-1]
        assert end == Presentation(2, codec.decode(x)).reduced().canonical()


def test_bridge_rejects_a_no_op_action():
    x, action, _ = next(m for m in REF["moves"] if m[0] == m[2])
    with pytest.raises(ValueError):
        codec.to_acx_path(Presentation(2, codec.decode(torch.tensor(x))), [action])


def test_ppo_smoke():
    states = encode_rows(data.load("ms640", ids=range(12)))
    assert pinned_prefix(states, states[:3]) == 3
    before = policy.ActorCritic().state_dict()
    model = train(states, 2, n_pinned=3, envs=8, steps=6, minibatches=2, micro=16, log=lambda *_: None,
                  model=policy.ActorCritic())
    assert any(not torch.equal(v, before[k]) for k, v in model.state_dict().items())


def test_ppo_singleton_minibatch_stays_finite():
    states = encode_rows(data.load("ms640", ids=[0]))
    model = train(states, 1, envs=1, steps=1, minibatches=1, epochs=1, log=lambda *_: None)
    assert all(torch.isfinite(p).all() for p in model.parameters())


def test_ppo_uneven_minibatches_use_every_sample_once_and_microbatch_gradients_agree():
    from copy import deepcopy
    from acx.rl.ppo import DEFAULTS, update

    class SmallPolicy(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(3, 3)
            self.seen = []

        def forward(self, x):
            self.seen.extend(x[:, 0].tolist())
            y = self.linear(x)
            return y[:, :2], y[:, 2]

    base = SmallPolicy()
    obs = torch.arange(21, dtype=torch.float32).reshape(7, 3) / 20
    act = torch.arange(7) % 2
    with torch.no_grad():
        logits, val = base(obs)
        logp = policy.log_prob_entropy(logits, act)[0]
    base.seen.clear()
    batch = obs, act, logp, val, torch.arange(7).float(), val + 0.5
    outcomes = []
    for micro in (1, 2, 100):
        model = deepcopy(base)
        opt = torch.optim.SGD(model.parameters(), lr=0.001)
        updates = []
        opt.register_step_post_hook(lambda *args: updates.append(1))
        stats = update(model, opt, batch, {**DEFAULTS, "minibatches": 3, "epochs": 2, "micro": micro},
                       torch.Generator().manual_seed(7))
        assert len(updates) == 6
        assert sorted(model.seen) == sorted(obs[:, 0].tolist() * 2)
        assert all(torch.isfinite(torch.tensor(v)) for v in stats.values())
        outcomes.append(model.state_dict())
    for other in outcomes[1:]:
        for key in other:
            torch.testing.assert_close(other[key], outcomes[0][key], atol=1e-6, rtol=1e-6)


@pytest.mark.parametrize("overrides", [
    {"step": 6}, {"envs": 0}, {"steps": True}, {"micro": 0}, {"chunk": 0}, {"epochs": 0},
    {"minibatches": 0}, {"envs": 1, "steps": 1, "minibatches": 2},
    {"gamma": float("nan")}, {"lam": 1.01}, {"lr": 0}, {"vf": -1}, {"clip": float("inf")},
])
def test_ppo_rejects_bad_experiment_settings(overrides):
    from acx.rl.ppo import training_config

    with pytest.raises(ValueError):
        training_config(overrides)


@pytest.mark.parametrize("states, envs, pinned", [
    (torch.empty((0, 48), dtype=torch.int64), 1, 0),
    (torch.zeros((1, 47), dtype=torch.int64), 1, 0),
    (torch.zeros((1, 48)), 1, 0),
    (torch.full((1, 48), 3, dtype=torch.int64), 1, 0),
    (torch.zeros((1, 48), dtype=torch.int64), 1, 2),
    (torch.zeros((1, 48), dtype=torch.int64), 0, 0),
])
def test_training_environment_rejects_invalid_initialization(states, envs, pinned):
    from acx.rl.env import VecEnv

    with pytest.raises(ValueError):
        VecEnv(states, envs, n_pinned=pinned)


def test_s_move_sizes_describe_the_dropped_product():
    """``s_move`` returns the seam-reduced product length and the child's total beside the new state and ``over``."""
    x = torch.tensor([m[0] for m in REF["moves"]])
    a = torch.tensor([m[1] for m in REF["moves"]])
    args = moves.decode_action(a, 24)
    for cap in (None, 10):
        new, over, size, total = moves.s_move(x, *args, 24, cap)
        assert (new[over] == x[over]).all()
        limit = 24 if cap is None else cap
        assert (size[over] > limit).all() and (size[~over] <= limit).all()
        other = torch.where(args[0] == 0, (x[:, 24:] != 0).sum(-1), (x[:, :24] != 0).sum(-1))
        assert (total == size + other).all()
    assert over.any()


def test_beam_cap_counters(model):
    """The beam selects before it applies a move, so a selected over-cap child always took a beam slot."""
    pres = data.load("ms640", ids=[4])[0].pres
    s = rl_solve.solve(pres, model, width=64, steps=30, cap=6).stats
    assert s["cap"] == 6 and s["cap_dropped"] > 0 and s["cap_would_pop"] == s["cap_dropped"]
    assert 1 <= s["cap_first_bind"] <= 30 and s["cap_needed"] > 6 and s["cap_dropped_min_total"] > 6
    assert s["cap_dropped_min_total"] >= s["cap_needed"]
    clean = rl_solve.solve(pres, model, width=64, steps=30).stats                 # the default cap is 24
    assert clean["cap"] == 24 and clean["cap_dropped"] == 0 and clean["cap_would_pop"] == 0
    assert clean["cap_first_bind"] is None and clean["cap_needed"] is None and clean["cap_dropped_min_total"] is None


def test_beam_zero_dropped_means_the_same_run_at_every_larger_cap(model):
    zero = nonzero = 0
    for row in data.load("ms640", ids=range(10)):
        big = rl_solve.solve(row.pres, model, width=64, steps=40, cap=24)
        assert big.stats["cap_dropped"] == 0                                         # nothing over 24 here
        for cap in (8, 12, 16):
            res = rl_solve.solve(row.pres, model, width=64, steps=40, cap=cap)
            if res.stats["cap_dropped"] == 0:
                zero += 1
                assert (res.path, res.pops) == (big.path, big.pops)
            else:
                nonzero += 1
    assert zero > 5 and nonzero > 5


def test_beam_counters_on_skipped_and_trivial_rows(model):
    pres = data.load("ms640", ids=[4])[0].pres
    for res in (rl_solve.solve(pres, model, cap=4), rl_solve.solve(Presentation(2, ((1,), (2,))), model, cap=7)):
        assert res.stats["cap_dropped"] == res.stats["cap_would_pop"] == 0
        assert res.stats["cap_first_bind"] is None and res.stats["cap_needed"] is None
    assert res.stats["cap"] == 7
