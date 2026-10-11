"""Tests for the optional PyTorch RL extra (``acx.rl``); skipped when torch is missing."""
import json
import os

import pytest

torch = pytest.importorskip("torch")

from acx import data  # noqa: E402
from acx.core.words import Presentation  # noqa: E402
from acx.rl import convert, moves, policy, solve as rl_solve  # noqa: E402
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
    out, over = moves.s_move(x, *moves.decode_action(a, 24), 24)
    assert (out == torch.tensor([m[2] for m in REF["moves"]])).all()
    assert (out != x).any(-1).sum() > 20 and (out == x).all(-1).any()
    assert over.any() and (out[over] == x[over]).all()             # an over-length product is a no-op


def test_action_codec_roundtrip():
    a = torch.arange(0, 4 * 24 * 24, 7)
    i, j, k1, k2 = moves.decode_action(a, 24)
    assert (moves.encode_action(i, j, k1, k2, 24) == a).all()


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


def test_checkpoint_conversion_is_exhaustive(model):
    """Every flax array maps to exactly one torch parameter (95 arrays, no silent skips)."""
    names = {n for n, _ in model.named_parameters()}
    assert set(torch.load(policy.CHECKPOINT, weights_only=True)) == names
    assert len(names) == 95
    with pytest.raises(KeyError):
        convert.to_state_dict({"Dense_9.kernel": torch.zeros(2, 2).numpy()})


def test_beam_solves_easy_ms640_rows_and_replays(model):
    for row in data.load("ms640", ids=range(5)):
        res = rl_solve.solve(row.pres, model, width=64, steps=60)
        assert res.solved and res.path_length <= 6
        assert replay(row.pres, res.path, cap=24)[-1].is_trivial()
        assert res.stats["backend"] == "rl-beam" and res.pops == res.stats["evaluated"] > 0
    # width far above the legal-move count: illegal actions must never enter the beam
    res = rl_solve.solve(data.load("ms640", ids=[0])[0].pres, model, width=1024, steps=5)
    assert res.solved and res.pops < 50


def test_cap_is_applied_counted_and_bounded(model):
    pres = data.load("ms640", ids=[4])[0].pres
    res = rl_solve.solve(pres, model, width=64, steps=30, cap=6)
    assert res.solved and res.stats["cap_rejected"] > 0 and res.stats["cap"] == 6
    assert all(len(r) <= 6 for st in replay(pres, res.path, cap=6) for r in st.rels)
    assert rl_solve.solve(pres, model, width=64, steps=30).stats["cap_rejected"] == 0
    skipped = rl_solve.solve(pres, model, cap=4)                    # a start relator over the cap
    assert not skipped.solved and "skipped" in skipped.stats
    for bad in (None, 0, 25):
        with pytest.raises(ValueError):
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
        x, actions = rl_solve.encode(row.pres.reduced().rels), []
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
        path = rl_solve.to_acx_path(row.pres, actions)
        end = replay(row.pres, path, require_trivial=False)[-1]
        assert end == Presentation(2, rl_solve.decode(x)).reduced().canonical()


def test_bridge_rejects_a_no_op_action():
    x, action, _ = next(m for m in REF["moves"] if m[0] == m[2])
    with pytest.raises(ValueError):
        rl_solve.to_acx_path(Presentation(2, rl_solve.decode(torch.tensor(x))), [action])


def test_ppo_smoke():
    states = encode_rows(data.load("ms640", ids=range(12)))
    assert pinned_prefix(states, states[:3]) == 3
    before = policy.ActorCritic().state_dict()
    model = train(states, 2, n_pinned=3, envs=8, steps=6, minibatches=2, micro=16, log=lambda *_: None,
                  model=policy.ActorCritic())
    assert any(not torch.equal(v, before[k]) for k, v in model.state_dict().items())
