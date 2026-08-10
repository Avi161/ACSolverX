"""The Colab notebook, executed for real with the runner stubbed AFTER SETUP.

SETUP purges `experiments.*` from `sys.modules`, so a stub installed before it is
silently evicted and the RUN cell calls the real pipeline (that has happened in
this repo). Everything here therefore runs the actual cell sources in order and
patches only once SETUP has finished.

Two things this pins that nothing else can: that `BRANCH` names the branch the
code is actually on -- a mismatch clones the wrong code and fails hours later on
Colab, not here -- and that the RUN cell issues one beam per trained checkpoint
with the checkpoint it just trained.
"""

import json
import os
import subprocess
import sys

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data                                 # noqa: E402

NB = os.path.join(acs_data.ROOT, "experiments", "notebooks", "ppo", "ppo_baseline.ipynb")


@pytest.fixture(scope="module")
def cells():
    with open(NB) as fh:
        nb = json.load(fh)
    return ["".join(c["source"]) for c in nb["cells"]]


def test_it_is_the_three_cell_pattern_plus_one_justified_extra(cells):
    assert len(cells) == 4
    assert cells[0].lstrip().startswith("# ===== PPO BASELINE")
    assert "edit ONLY this cell" in cells[0]
    for src, head in zip(cells[1:], ("SETUP", "RUN", "TABLE")):
        assert head in src.splitlines()[0], head
    for i, src in enumerate(cells):
        compile(src, f"cell{i}", "exec")


def test_setup_carries_the_contracts_that_make_a_restart_continue(cells):
    setup = cells[1]
    assert "del sys.modules[_m]" in setup                 # a pull is not a reload
    assert "invalidate_caches" in setup
    assert "reset --hard FETCH_HEAD" in setup
    assert 'os.chdir(BASE)' in setup                      # never nest the clone
    assert 'ACSOLVERX_ALLOW_BIG' in setup                 # production beam opt-in
    assert "relogin=True" in setup
    # torch/jax ship with the Colab GPU image; reinstalling breaks CUDA matching
    assert "pip -q install flax orbax-checkpoint wandb" in setup
    assert "pip -q install torch" not in setup


def test_the_branch_matches_the_branch_this_code_is_on(cells):
    try:
        head = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                              cwd=acs_data.ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pytest.skip("git unavailable")
    if head.returncode != 0:
        pytest.skip("not a git checkout")
    branch = head.stdout.strip()
    assert f'BRANCH   = "{branch}"' in cells[0], \
        f"notebook clones a different branch than {branch!r}"


def test_drive_output_lands_under_mydrive(cells):
    """The mount root itself is not writable."""
    assert '"/content/drive/MyDrive/' in cells[0]


def _exec_notebook(cells, tmp_path, monkeypatch):
    """CONFIG -> SETUP -> stub -> RUN, in one namespace, like Colab does."""
    ns = {"__name__": "__main__"}
    exec(cells[0], ns)

    # W&B auth is not what this test is about and it blocks on getpass.
    ns["cfg"]["USE_WANDB"] = False
    exec(cells[1], ns)                       # SETUP: purges experiments.* here

    import experiments.ppo.run_ppo as run_ppo    # re-imported fresh after the purge
    calls = []

    def fake_main(cfg, log=print):
        calls.append(dict(cfg))
        return {"stage": cfg["STAGE"]}

    monkeypatch.setattr(run_ppo, "main", fake_main)

    ns["STAGES"] = ["convert", "parity", "beam_upstream", "train", "beam_trained"]
    ns["ARMS"] = ["1190MS", "AC19_extended"]
    ns["SEEDS"] = [142, 7]
    ns["LOCAL_OUT_DIR"] = str(tmp_path)       # absolute -> join() keeps it
    exec(cells[2], ns)
    return ns, calls


def test_the_run_cell_walks_the_ladder_and_beams_what_it_trained(cells, tmp_path, monkeypatch):
    cwd = os.getcwd()
    saved = dict(sys.modules)
    try:
        # every arm/seed already has a checkpoint, so beam_trained is not skipped
        for name in ["ppo-drt-1190MS-s142", "ppo-drt-1190MS-s7",
                     "ppo-drt-AC19_extended-s142", "ppo-drt-AC19_extended-s7"]:
            (tmp_path / f"{name}.pt").write_bytes(b"")
        ns, calls = _exec_notebook(cells, tmp_path, monkeypatch)
    finally:
        os.chdir(cwd)
        sys.modules.clear()
        sys.modules.update(saved)

    stages = [c["STAGE"] for c in calls]
    assert stages == ["convert", "parity", "beam_eval",
                      "train", "beam_eval", "train", "beam_eval",
                      "train", "beam_eval", "train", "beam_eval"]

    # the upstream beam decodes the transplanted weights, not a .pt
    assert calls[2]["BEAM_CHECKPOINT"] is None
    trains = [c for c in calls if c["STAGE"] == "train"]
    assert [(c["DATASET"], c["SEED"]) for c in trains] == [
        ("1190MS", 142), ("1190MS", 7), ("AC19_extended", 142), ("AC19_extended", 7)]

    # each trained beam names the checkpoint of the train call right before it
    for train, beam in zip(trains, [c for c in calls if c["STAGE"] == "beam_eval"][1:]):
        assert beam["BEAM_CHECKPOINT"].endswith(
            f"ppo-drt-{train['DATASET']}-s{train['SEED']}.pt")
        assert beam["EVAL_DATASET"] == "1190MS", "the paper's denominator, always"

    # upstream hyperparameters reach the runner without the notebook restating them
    for c in calls:
        assert c["NUM_ENVS"] == 2380 and c["NUM_STEPS"] == 96 and c["SEED"] in (142, 7)
        assert c["MAX_UPDATES"] == ns["MAX_UPDATES"]
        assert c["OUT_DIR"] == str(tmp_path)
        assert c["MIRROR_DIR"] is None            # not Colab, so no Drive mirror


def test_a_missing_checkpoint_skips_its_beam_instead_of_crashing(cells, tmp_path, monkeypatch):
    cwd = os.getcwd()
    saved = dict(sys.modules)
    try:
        _, calls = _exec_notebook(cells, tmp_path, monkeypatch)
    finally:
        os.chdir(cwd)
        sys.modules.clear()
        sys.modules.update(saved)
    assert [c["STAGE"] for c in calls].count("beam_eval") == 1   # only the upstream one
