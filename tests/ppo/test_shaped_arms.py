"""The seam: shaping wired into the env, the arms wired into the runner.

`test_shaping.py` proves the potential is right in isolation. This file proves the two
things that can still be wrong once it is plugged in, and that no unit test can see:

  * **the control arm is bit-identical to the unshaped baseline.** `lam = 0` has to be a
    hard zero all the way through `VecACS.step`, not a small number. If it is not, the
    control is itself a treatment and the comparison measures nothing.
  * **the two arms cannot collide on disk.** They share a dataset, a seed and an output
    directory, so if `train_tag` did not carry the reward variant they would share a
    checkpoint file -- and each would silently resume from the other's weights. That
    failure produces plausible numbers, which is what makes it worth a test.

Plus the trap `heldout.py` exists for: filtering the benchmark out of the training file
makes the shipped prefix walk return 0, and pinning would switch off in both arms at once.
"""

import json
import os

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, bench60, heldout, run_ppo, shaping   # noqa: E402
from experiments.ppo.acs_env import VecACS                                 # noqa: E402

L = 24
N_ACTIONS = 2 * 2 * L * L


def _pair(shaped, n=64, seed=3):
    pres = acs_data.load_presentations("1190MS", L)
    kw = dict(num_envs=n, max_length=L, max_steps=8, device="cpu", seed=seed,
              track_paths=False)
    return VecACS(pres, **kw), VecACS(pres, shaping=shaped, lam=0.0, **kw)


def test_lambda_zero_leaves_the_env_reward_bit_identical():
    """The control arm, end to end. Same seed, same actions, byte-for-byte same reward."""
    plain, zeroed = _pair("s20mk2")
    g = torch.Generator().manual_seed(11)
    for _ in range(24):
        a = torch.randint(0, N_ACTIONS, (64,), generator=g)
        (_, r_plain, _, i_plain), (_, r_zero, _, i_zero) = plain.step(a), zeroed.step(a)
        assert torch.equal(i_plain["raw_reward"], i_zero["raw_reward"])
        assert torch.equal(r_plain, r_zero)
        assert torch.equal(plain.x, zeroed.x)


def test_the_shaped_env_adds_exactly_the_shaping_term_and_nothing_else():
    """A treatment that changed anything besides the reward would not be a treatment."""
    pres = acs_data.load_presentations("1190MS", L)
    kw = dict(num_envs=64, max_length=L, max_steps=8, device="cpu", seed=5,
              track_paths=False)
    plain = VecACS(pres, **kw)
    shaped = VecACS(pres, shaping="s20mk2", lam=0.2, **kw)
    g = torch.Generator().manual_seed(7)
    moved = 0
    for _ in range(24):
        a = torch.randint(0, N_ACTIONS, (64,), generator=g)
        x_old = shaped.x.clone()
        (_, _, _, i_plain), (_, _, _, i_shaped) = plain.step(a), shaped.step(a)
        done = i_shaped["terminated"] | i_shaped["truncated"]
        want = shaping.shaping_term(x_old, shaped.x, done, 0.2, shaped.gamma, "s20mk2")
        assert torch.allclose(i_shaped["raw_reward"] - i_plain["raw_reward"], want,
                              atol=1e-4)
        # the state trajectory must be untouched -- only the reward may differ
        assert torch.equal(plain.x, shaped.x)
        moved += int((want.abs() > 1e-6).sum())
    assert moved > 0, "shaping never fired; the assertion above proved nothing"


def test_the_two_arms_cannot_share_a_checkpoint():
    control = run_ppo.train_tag("AC19_extended_ho60", 142)
    shaped = run_ppo.train_tag("AC19_extended_ho60", 142, "s20mk2", 0.2)
    assert control != shaped
    assert "s20mk2" in shaped and "lam0.2" in shaped
    # an unshaped run keeps the ORIGINAL tag, so existing checkpoints stay readable
    assert control == "ppo-drt-AC19_extended_ho60-s142"
    assert run_ppo.train_tag("1190MS", 142, None, 0.0) == "ppo-drt-1190MS-s142"
    assert run_ppo.train_tag("1190MS", 142, "s20mk2", 0.0) == "ppo-drt-1190MS-s142"


def test_an_unknown_shaping_variant_fails_loudly():
    """A typo in the CONFIG must not quietly train a control and call it a treatment.

    Asserted through the REAL call path, not by indexing `WEIGHTS` directly: a dict raising
    `KeyError` is a fact about Python, and a lookup changed to `WEIGHTS.get(name, default)`
    would silently fall back to an arm while that weaker assertion stayed green.
    """
    x = torch.zeros(4, 2 * L, dtype=torch.int64)
    typo = "s20_mk2"                        # the results-file spelling, not the arm name
    for call in (lambda: shaping.heuristic(x, weights=typo),
                 lambda: shaping.potential(x, 0.2, weights=typo),
                 lambda: shaping.shaping_term(x, x, torch.zeros(4, dtype=torch.bool),
                                              0.2, 0.99, typo)):
        with pytest.raises(KeyError):
            call()
    # and the env carries the typo all the way to the same failure, not past it
    pres = acs_data.load_presentations("1190MS", L)
    env = VecACS(pres, num_envs=8, max_length=L, max_steps=4, device="cpu", seed=1,
                 track_paths=False, shaping=typo, lam=0.2)
    with pytest.raises(KeyError):
        env.step(torch.zeros(8, dtype=torch.int64))


# ---------------------------------------------------------------- the held-out dataset
@pytest.fixture(scope="module")
def heldout_stem():
    stem = heldout.heldout_stem("AC19_extended")
    path = os.path.join(acs_data.ROOT, "data", stem + ".txt")
    existed = os.path.exists(path)
    run_ppo._ensure_dataset(stem, L, log=lambda *_: None)
    yield stem
    if not existed:
        os.remove(path)


def test_the_benchmark_is_gone_from_the_training_file(heldout_stem):
    drop = heldout.benchmark_states(L)
    rows = acs_data.read_raw(heldout_stem)
    assert len(rows) == len(acs_data.read_raw("AC19_extended")) - 54
    assert not any(tuple(acs_data.repad(r, L)) in drop for r in rows)


def test_the_naive_prefix_walk_really_does_collapse_to_zero(heldout_stem):
    """The trap, asserted rather than described.

    Benchmark row `bin 0` is line 0 of both files, so removing it stops the shipped
    walk immediately. If this test ever starts failing, the trap has moved -- it has
    not gone away, and `run_ppo` must still not use that function.
    """
    assert acs_data.ms_prefix_length(heldout_stem) == 0
    assert heldout.ms_prefix_length(heldout_stem, L) == 580     # 634 - 54


def test_the_filter_aware_pin_agrees_with_the_shipped_one_everywhere_else():
    for stem in ("1190MS", "AC19_extended", "AC19"):
        assert heldout.ms_prefix_length(stem, L) == acs_data.ms_prefix_length(stem), stem


def test_building_the_datasets_twice_changes_nothing(heldout_stem):
    path = os.path.join(acs_data.ROOT, "data", heldout_stem + ".txt")
    before = open(path).read()
    heldout.build("AC19_extended", L, log=lambda *_: None)
    assert open(path).read() == before


def test_a_stale_file_of_the_right_LENGTH_is_still_rebuilt(tmp_path):
    """The training file is what a run actually reads; the row count is not a checksum.

    A resume that trusted `len(file) == len(keep)` would keep a wrong file and still return
    the right counts, because those are recomputed in memory either way -- so the mistake
    would be invisible in the log and visible only in what the policy trained on. Here the
    row count is preserved exactly and only the CONTENT is corrupted.

    Corrupts a stem of its OWN, never the canonical `AC19_extended_ho60`: a test that
    damages a shared data file leaves it damaged for every later test if the process dies
    between the corruption and the repair, which is exactly how this test first failed.
    """
    stem = "AC19_extended_ho60_stalecheck"
    path = os.path.join(acs_data.ROOT, "data", stem + ".txt")
    try:
        heldout.build("AC19_extended", L, out_stem=stem, log=lambda *_: None)
        good = open(path).read()
        lines = good.splitlines(keepends=True)
        lines[7] = str([0] * (2 * L)) + "\n"        # same line count, wrong row
        open(path, "w").write("".join(lines))
        assert open(path).read() != good

        heldout.build("AC19_extended", L, out_stem=stem, log=lambda *_: None)
        assert open(path).read() == good
    finally:
        for p in (path, path + ".tmp"):
            if os.path.exists(p):
                os.remove(p)


def test_ensure_dataset_does_not_skip_the_content_check_on_an_existing_file(heldout_stem):
    """The seam that made the check above dead code on the real path.

    `_ensure_dataset` used to return early on `os.path.exists`, so `build`'s comparison
    never ran for the file a training run reads -- the guarantee existed only where nobody
    needed it. Corrupt the canonical file and require the ordinary entry point to heal it.
    """
    path = os.path.join(acs_data.ROOT, "data", heldout_stem + ".txt")
    good = open(path).read()
    try:
        lines = good.splitlines(keepends=True)
        lines[3] = str([0] * (2 * L)) + "\n"
        open(path, "w").write("".join(lines))

        run_ppo._ensure_dataset(heldout_stem, L, log=lambda *_: None)
        assert open(path).read() == good
    finally:
        open(path, "w").write(good)     # never leave the shared file damaged


# ---------------------------------------------------------------- benchmark-60 scoring
def test_benchmark60_is_scored_at_orbit_level_as_well_as_row_level(tmp_path):
    """60 rows are 45 orbits; a bare `n/60` overstates a method that suits a duplicate."""
    bench = heldout.benchmark_rows()
    assert len(bench) == 60 and len({b["aut_class"] for b in bench}) == 45

    # solve every row of the single most duplicated orbit and nothing else
    dup = max({b["aut_class"] for b in bench}, key=lambda c: sum(b["aut_class"] == c for b in bench))
    path = tmp_path / f"beam-arm-{heldout.BENCH_STEM}-w1024-t150-L24.jsonl"
    with open(path, "w") as fh:
        for i, b in enumerate(bench):
            hit = b["aut_class"] == dup
            fh.write(json.dumps({"presentation_idx": i, "solved": hit,
                                 "path_length": 7 if hit else 0}) + "\n")
    s = bench60.score(str(path), bench)
    assert s["rows"] == 60 and s["orbits"] == 45
    assert s["solved"] == 8 and s["orbits_solved"] == 1     # 8 rows, ONE orbit
    assert sum(int(v.split("/")[1]) for v in s["by_bin"].values()) == 60
    assert s["discriminating_rows"] == 18                   # bins 7, 8 and 9


def test_a_torn_trailing_row_does_not_take_the_score_with_it(tmp_path):
    path = tmp_path / f"beam-arm-{heldout.BENCH_STEM}-w1024-t150-L24.jsonl"
    path.write_text('{"presentation_idx": 0, "solved": true, "path_length": 4}\n'
                    '{"presentation_idx": 1, "solv')
    s = bench60.score(str(path))
    assert s["rows"] == 1 and s["solved"] == 1
