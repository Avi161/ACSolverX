"""`shaping.py`: the reward the treatment arm trains on.

Two things make this file the whole safety net for that arm. The features are a
**reimplementation** -- `hsearch.feats` walks a Python string and builds run lists,
this walks a batched int tensor and never enumerates a run -- so nothing but a
parity test against the original says they agree. And potential-based shaping is
only policy-invariant while `Phi` is zero at every episode end; break that and the
run still trains, still logs, and quietly optimises for sitting at the horizon.

The corpus is real rollout states, not synthetic words: the states an S-move
actually produces are the ones the agent will be rewarded on, and a hand-written
word list would have missed, for instance, that a relator can empty out mid-episode.
The hand-written cases are here as well, but only to force the branches a random
rollout reaches rarely -- the empty relator, the single-generator relator, and the
word whose first and last letters share a generator, which is the seam merge.
"""

import pytest

torch = pytest.importorskip("torch")

from experiments.search.heuristics import phi                              # noqa: E402
from experiments.ppo import acs_data, shaping                              # noqa: E402
from experiments.ppo.acs_env import VecACS                                 # noqa: E402


# `hsearch.feats` in this repo's vocabulary. `heuristics.phi` returns all seventeen
# features in FEATURES order; the four the potential uses are L, K, MK, S at indices
# 0, 4, 5, 7. The block decomposition underneath is the same algorithm (cyclic runs,
# seam merged, sign ignored), so this is a projection of the reference, not a second
# implementation of it.
def feats(r1, r2):
    v = phi(r1, r2)
    return int(v[0]), int(v[4]), int(v[5]), v[7]


# The vector withdrawn as overfit. Nothing defines it any more --
# `tests/test_greedy_heuristic.py` guards the package against it returning, and that
# guard scans module-level config dicts, not this test module -- so it is held here
# as a literal purely so the assertion below can still name the numbers it bans.
WITHDRAWN = {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}

L = 24
N_ACTIONS = 2 * 2 * L * L
SYM = {1: "x", -1: "X", 2: "y", -2: "Y"}


def _decode(row):
    """Flat int state -> the `(r1, r2)` strings `hsearch` works in."""
    return ("".join(SYM[int(c)] for c in row[:L] if c),
            "".join(SYM[int(c)] for c in row[L:] if c))


def _encode(r1, r2):
    inv = {v: k for k, v in SYM.items()}
    pad = lambda w: [inv[c] for c in w] + [0] * (L - len(w))
    return pad(r1) + pad(r2)


@pytest.fixture(scope="module")
def rollout():
    """Real states plus the `(x_old, x_new, done)` triples that produced them."""
    pres = acs_data.load_presentations("1190MS", L)
    env = VecACS(pres, num_envs=256, device="cpu", seed=0, track_paths=False)
    g = torch.Generator().manual_seed(0)
    states, steps = [], []
    for _ in range(24):
        x_old = env.x.clone()
        states.append(x_old)
        _, _, _, info = env.step(torch.randint(0, N_ACTIONS, (256,), generator=g))
        steps.append((x_old, env.x.clone(), info["terminated"] | info["truncated"]))
    return torch.cat(states, 0), steps


def test_features_match_the_search_heuristic_on_real_states(rollout):
    states, _ = rollout
    assert states.shape[0] >= 5000
    length, knots, max_knots, smaller = shaping.features(states)
    for i in range(states.shape[0]):
        r1, r2 = _decode(states[i].tolist())
        want = feats(r1, r2)
        got = (length[i].item(), knots[i].item(), max_knots[i].item(), smaller[i].item())
        assert want[0] == got[0] and want[1] == got[1] and want[2] == got[2], (r1, r2)
        assert abs(want[3] - got[3]) < 1e-5, (r1, r2, want, got)


@pytest.mark.parametrize("r1,r2", [
    ("", ""),                       # both relators emptied out
    ("x", ""), ("", "y"),           # one empty: `smb` falls back to the other mean
    ("x", "y"), ("xx", "yy"),       # single-generator relators: k = 0, not k = 1
    ("XXX", "YY"),                  # ... and the sign must not matter
    ("xyx", "y"),                   # the seam merge: first and last share a generator
    ("xyxy", "xxyy"), ("xYxY", "XyXy"), ("xxxyyy", "xyxyxy"),
    ("x" * L, "y" * L),             # full width
    ("xy" * (L // 2), "x" * (L - 1) + "y"),
])
def test_features_match_on_the_branches_a_rollout_reaches_rarely(r1, r2):
    x = torch.tensor([_encode(r1, r2)], dtype=torch.int8)
    length, knots, max_knots, smaller = shaping.features(x)
    want = feats(r1, r2)
    assert (length[0].item(), knots[0].item(), max_knots[0].item()) == want[:3]
    assert abs(want[3] - smaller[0].item()) < 1e-6


def test_the_sign_of_a_letter_is_not_a_generator(rollout):
    """`blocks()` keys on `c in "xX"`. Inverting every letter must change nothing."""
    states, _ = rollout
    assert torch.allclose(shaping.heuristic(states), shaping.heuristic(-states))


def test_lambda_zero_is_exactly_the_unshaped_reward(rollout):
    """The control arm is this module returning a hard zero, not a small number."""
    _, steps = rollout
    for x_old, x_new, done in steps:
        f = shaping.shaping_term(x_old, x_new, done, lam=0.0, gamma=0.999)
        assert f.shape == (x_old.shape[0],)
        assert torch.count_nonzero(f) == 0


def test_the_lambda_zero_shortcut_agrees_with_the_general_formula(rollout):
    """The `if lam == 0.0: return zeros` branch is an optimisation, not a definition.

    Every other `lam = 0` test in this repo exercises only that one line, which makes them
    true by construction -- they would pass even if the general path disagreed. This is the
    test that has something to lose: it evaluates the formula the long way round, through
    `heuristic`, and requires the shortcut to be the same answer. Deleting the shortcut
    must be a no-op; if it ever is not, the control arm is not the unshaped baseline.
    """
    _, steps = rollout
    checked = 0
    for x_old, x_new, done in steps:
        # the general path, written out: Phi = -lam * h, F = gamma * Phi(s') - Phi(s)
        phi = -0.0 * shaping.heuristic(x_old, "s20mk2")
        phi_next = -0.0 * shaping.heuristic(x_new, "s20mk2")
        phi_next = torch.where(done, torch.zeros_like(phi_next), phi_next)
        general = 0.999 * phi_next - phi

        assert torch.equal(general, shaping.shaping_term(x_old, x_new, done, 0.0, 0.999))
        assert torch.equal(-0.0 * shaping.heuristic(x_old, "s20mk2"),
                           shaping.potential(x_old, 0.0))
        # the heuristic itself must be live on this data, or the equality is vacuous
        checked += int((shaping.heuristic(x_old, "s20mk2") > 0).sum())
    assert checked > 0, "heuristic was zero everywhere; the agreement proved nothing"


def test_the_potential_is_zero_at_every_episode_end(rollout):
    """Truncation as well as termination -- `acs_env` folds them into one `done`.

    Bootstrapping `Phi(s')` past the horizon would pay an agent for reaching step 96
    in a low-`h` state, which is the one thing shaping must not be able to buy.
    """
    _, steps = rollout
    x_old, x_new, _ = steps[0]
    n = x_old.shape[0]
    lam, gamma = 0.2, 0.999
    phi_old = shaping.potential(x_old, lam)
    for done in (torch.ones(n, dtype=torch.bool), torch.zeros(n, dtype=torch.bool)):
        f = shaping.shaping_term(x_old, x_new, done, lam=lam, gamma=gamma)
        if bool(done.all()):
            assert torch.allclose(f, -phi_old)
        else:
            assert torch.allclose(f, gamma * shaping.potential(x_new, lam) - phi_old)


def test_shaping_telescopes_over_a_whole_episode(rollout):
    """Sum of discounted `F` along any trajectory ending in `done` is `-Phi(s_0)`.

    This is the property that makes wandering unfarmable, and it is worth pinning
    directly: a per-step feature bonus would pass every other test in this file.
    """
    _, steps = rollout
    lam, gamma = 0.2, 0.999

    # A trajectory, not a scatter of transitions: pick an env that never reset inside
    # the rollout, so `x_new` of each step IS `x_old` of the next and the sum telescopes.
    # A random policy terminates almost never at this horizon, so rather than wait for a
    # natural ending (which made this test skip, and a skipped test pins nothing) the
    # last transition is declared done -- exactly what truncation does at step 96.
    ends = torch.stack([d for _, _, d in steps]).any(0)
    assert (~ends).any(), "every env reset; pick a shorter rollout"
    env_i = int((~ends).nonzero()[0])

    total = 0.0
    for t, (x_old, x_new, done) in enumerate(steps):
        last = t == len(steps) - 1
        d = torch.tensor([last])
        f = shaping.shaping_term(x_old[env_i:env_i + 1], x_new[env_i:env_i + 1],
                                 d, lam=lam, gamma=gamma)
        total += (gamma ** t) * f.item()
    x0 = steps[0][0][env_i:env_i + 1]
    assert abs(total + shaping.potential(x0, lam).item()) < 1e-3


def test_the_treatment_is_the_weights_the_70k_orbit_ab_selected():
    """`L + 20*S + 2*MK`, and nothing else on offer."""
    assert shaping.WEIGHTS["s20mk2"] == (1.0, 0.0, 2.0, 20.0)
    assert shaping.WEIGHTS["length"] == (1.0, 0.0, 0.0, 0.0)


def test_the_withdrawn_heuristic_is_not_an_arm_and_must_not_become_one():
    """User directive, standing: the withdrawn `RECOMMENDED` vector is never used here.

    It was tuned on ~60 presentations and its xyimb weight flips sign between the two
    configs it shipped with (see `experiments/search/HEURISTICS.md`). This asserts
    against the `WITHDRAWN` literal above -- and it fails loudly if anyone adds those
    weights back as a second arm.
    """
    banned = {w for k in ("L", "K", "MK", "S")
              for w in [WITHDRAWN[k]] if w != 1.0}
    assert not banned & {w for tup in shaping.WEIGHTS.values() for w in tup}
    assert "xyimb" not in str(shaping.WEIGHTS)
    assert set(shaping.WEIGHTS) == {"s20mk2", "length"}


def test_lambda_is_calibrated_against_the_base_reward(rollout):
    """The measurement that chose `lam = 0.2`, kept as a regression on the features.

    On transitions that actually change the state, median `|h' - h|` is ~11, so at
    `lam = 0.2` the median shaping term is ~2.2 -- about a fifth of the flat `-10`
    the base reward pays. Informative without swamping. If a change to the features
    moves this band, the chosen `lam` no longer means what it meant.
    """
    _, steps = rollout
    mags = []
    for x_old, x_new, done in steps:
        moved = (~done) & ~(x_new == x_old).all(-1)
        if moved.any():
            f = shaping.shaping_term(x_old, x_new, done, lam=1.0, gamma=0.999)
            mags.append(f[moved].abs())
    m = torch.cat(mags)
    assert m.numel() > 100
    assert 5.0 < m.median().item() < 20.0, m.median().item()
