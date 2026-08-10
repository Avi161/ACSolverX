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


def _exec_notebook(cells, tmp_path, monkeypatch, smoke=False, **over):
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

    ns["SMOKE_RUN"] = smoke
    ns["STAGES"] = ["convert", "parity", "beam_upstream", "train", "beam_trained"]
    ns["ARMS"] = ["1190MS", "AC19_extended"]
    ns["SEEDS"] = [142, 7]
    ns["LOCAL_OUT_DIR"] = str(tmp_path)       # absolute -> join() keeps it
    ns.update(over)
    exec(cells[2], ns)
    return ns, calls


def _run_isolated(cells, tmp_path, monkeypatch, **kw):
    cwd = os.getcwd()
    saved = dict(sys.modules)
    try:
        return _exec_notebook(cells, tmp_path, monkeypatch, **kw)
    finally:
        os.chdir(cwd)
        sys.modules.clear()
        sys.modules.update(saved)


def test_the_run_cell_walks_the_ladder_and_beams_what_it_trained(cells, tmp_path, monkeypatch):
    # every arm/seed already has a checkpoint, so beam_trained is not skipped
    for name in ["ppo-drt-1190MS-s142", "ppo-drt-1190MS-s7",
                 "ppo-drt-AC19_extended-s142", "ppo-drt-AC19_extended-s7"]:
        (tmp_path / f"{name}.pt").write_bytes(b"")
    ns, calls = _run_isolated(cells, tmp_path, monkeypatch)

    stages = [c["STAGE"] for c in calls]
    assert stages == ["convert", "parity", "beam_eval",
                      "train", "beam_eval", "train", "beam_eval",
                      "train", "beam_eval", "train", "beam_eval",
                      "report"]

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
    _, calls = _run_isolated(cells, tmp_path, monkeypatch)
    assert [c["STAGE"] for c in calls].count("beam_eval") == 1   # only the upstream one


def test_the_smoke_runs_the_gates_at_production_beam_settings(cells, tmp_path, monkeypatch):
    """A shrunken beam would measure a proxy. The smoke must not shrink it.

    Its whole value is that seconds/presentation extrapolates to all 1190 and
    its rows land in the SAME jsonl the full run resumes -- both of which fail
    the moment the width or step count differs from production.
    """
    ns, calls = _run_isolated(cells, tmp_path, monkeypatch, smoke=True)

    assert [c["STAGE"] for c in calls] == ["convert", "parity", "beam_eval", "report"]
    beam = calls[2]
    full = json.loads(json.dumps(ns["BASE"]))
    assert beam["BEAM_WIDTH"] == 1024 and beam["BEAM_MAX_STEPS"] == 150
    assert beam["BEAM_TIME_BUDGET_S"] == ns["SMOKE_SECONDS"]
    assert beam["EVAL_END"] is None, "the budget stops it, not a truncated slice"
    assert beam["EVAL_DATASET"] == "1190MS"
    assert full["USE_WANDB"] is False
    assert calls[-1]["SMOKE_RUN"] is True


def test_the_smoke_can_include_two_training_updates(cells, tmp_path, monkeypatch):
    _, calls = _run_isolated(cells, tmp_path, monkeypatch, smoke=True, SMOKE_TRAIN=True)
    stages = [c["STAGE"] for c in calls]
    assert stages == ["convert", "parity", "beam_eval", "train", "report"]
    train = next(c for c in calls if c["STAGE"] == "train")
    assert train["MAX_UPDATES"] == 2          # meaningless numbers, real code path
    assert train["SAVE_EVERY"] == 1           # so the checkpoint + mirror are exercised
    assert train["DATASET"] == "1190MS"


def test_the_smoke_boolean_is_on_by_default_and_documented(cells):
    """It ships on: the first thing to do with a fresh A100 is the 5-minute check."""
    assert "SMOKE_RUN     = True" in cells[0]
    assert "SMOKE_SECONDS = 300" in cells[0]
    assert "smoke_report.json" in cells[0]


def test_flipping_the_smoke_boolean_off_is_the_whole_full_run_edit(cells, tmp_path,
                                                                   monkeypatch):
    """The user's stated action: change one boolean, change nothing else.

    `STAGES += ["report"]` used to live inside the `if SMOKE_RUN:` branch, so
    the flag that turns the smoke into the real run also removed the only stage
    that prints a table -- the full eval would decode all 1190 presentations and
    end with nothing to read. The report touches no GPU and only reads disk, so
    it belongs to every ladder.
    """
    ns, calls = _run_isolated(cells, tmp_path, monkeypatch, smoke=False)
    stages = [c["STAGE"] for c in calls]

    assert stages[-1] == "report", "a full run must still print a table"
    assert stages.count("report") == 1
    assert calls[-1]["SMOKE_RUN"] is False

    beam = calls[2]
    assert beam["STAGE"] == "beam_eval"
    assert beam["BEAM_TIME_BUDGET_S"] is None, "no wall-clock stop on the real run"
    assert beam["EVAL_END"] is None, "all 1190, not a slice"
    assert beam["BEAM_WIDTH"] == 1024 and beam["BEAM_MAX_STEPS"] == 150
    assert beam["EVAL_DATASET"] == "1190MS"


def test_the_full_run_report_does_not_overwrite_the_smoke_report(tmp_path):
    """Two artefacts, two names -- they get read side by side when a number moves."""
    from experiments.ppo.run_ppo import stage_report

    base = {"OUT_DIR": str(tmp_path), "MIRROR_DIR": None, "EVAL_DATASET": "1190MS",
            "EVAL_DENOMINATOR": 1190}
    stage_report({**base, "SMOKE_RUN": True}, log=lambda *_: None)
    stage_report({**base, "SMOKE_RUN": False}, log=lambda *_: None)

    assert (tmp_path / "smoke_report.json").exists()
    assert (tmp_path / "report.json").exists()
