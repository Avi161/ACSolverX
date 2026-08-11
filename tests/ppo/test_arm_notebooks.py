"""The two arm notebooks, executed for real with the runner stubbed after SETUP.

The experiment is a difference between two notebooks, so the thing most worth pinning is
that they are *the same notebook* apart from the reward. They are generated from one
template (`experiments/ppo/make_arm_notebooks.py`), and these tests fail if anyone edits
one `.ipynb` by hand: SETUP, RUN and TABLE must be byte-identical across the pair and
SETUP must still be the baseline notebook's, verbatim.

The rest is the same contract `test_notebook.py` holds the baseline to -- SETUP purges
`experiments.*` from `sys.modules`, so a stub installed before it is silently evicted and
the RUN cell calls the real pipeline. Everything here runs the real cell sources in order
and patches only once SETUP has finished.
"""

import json
import os
import subprocess
import sys

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, make_arm_notebooks                   # noqa: E402

NB_DIR = os.path.join(acs_data.ROOT, "experiments", "notebooks", "ppo")
ARMS = ("control", "s20mk2")


def _cells(name):
    with open(os.path.join(NB_DIR, f"ppo_arm_{name}.ipynb")) as fh:
        return ["".join(c["source"]) for c in json.load(fh)["cells"]]


def _knobs(config_src):
    """Every knob a CONFIG cell sets, flattened.

    A notebook splits them between bare module-level names (`BRANCH`, `SEED`, ...) and the
    `cfg` dict (`BEAM_WIDTH`, `WANDB_*`, ...). The two sets are disjoint, so one flat dict
    is unambiguous -- and reading them from the executed namespace rather than the source
    means a knob moved between the two halves does not read as a difference.
    """
    ns = {}
    exec(config_src, ns)
    flat = {k: v for k, v in ns.items() if k.isupper() and not k.startswith("_")}
    assert not (set(flat) & set(ns["cfg"])), "a knob is set in both halves; which wins?"
    flat.update(ns["cfg"])
    return flat


@pytest.fixture(scope="module")
def arms():
    return {name: _cells(name) for name in ARMS}


def test_both_are_the_four_cell_pattern_and_every_cell_compiles(arms):
    for name, cells in arms.items():
        assert len(cells) == 4, name
        assert cells[0].lstrip().startswith("# ===== PPO ARM"), name
        assert "edit ONLY this cell" in cells[0]
        for i, src in enumerate(cells):
            compile(src, f"{name}-cell{i}", "exec")


def test_the_arms_differ_in_the_reward_and_in_nothing_else(arms):
    """If SETUP, RUN or TABLE ever diverge, the comparison stops measuring the reward.

    CONFIG is compared by executed VALUE, not by source line: the two arms carry different
    explanatory comments on purpose, and a positional line diff would flag all of those.
    """
    a, b = arms["control"], arms["s20mk2"]
    assert a[1] == b[1] and a[2] == b[2] and a[3] == b[3]

    knobs_a, knobs_b = _knobs(a[0]), _knobs(b[0])
    assert set(knobs_a) == set(knobs_b), set(knobs_a) ^ set(knobs_b)
    differing = {k for k in knobs_a if knobs_a[k] != knobs_b[k]}
    assert differing == {"ARM", "SHAPING", "LAMBDA", "LOCAL_OUT_DIR", "DRIVE_OUT_DIR",
                         "WANDB_JOB_TYPE", "WANDB_TAGS"}, differing
    # named explicitly as well: these decide what is measured, and a future edit that
    # moved one into the allowed set above would still have to get past this line
    for k in ("DATASET", "EVAL_DATASET", "SEED", "MAX_UPDATES", "SAVE_EVERY", "BRANCH",
              "BEAM_WIDTH", "BEAM_MAX_STEPS", "BEAM_ALPHA", "BEAM_TEMPERATURE",
              "ALLOW_TF32", "WANDB_GROUP", "WANDB_PROJECT", "SMOKE_RUN", "SMOKE_SECONDS"):
        assert knobs_a[k] == knobs_b[k], k


def test_setup_is_the_baseline_notebook_s_setup_verbatim(arms):
    """Not a copy that can drift -- the generator lifts it, and this proves it did."""
    with open(os.path.join(NB_DIR, "ppo_baseline.ipynb")) as fh:
        baseline_setup = "".join(json.load(fh)["cells"][1]["source"])
    assert arms["control"][1] == baseline_setup


def test_regenerating_is_a_no_op(arms, tmp_path):
    """The committed notebooks are what the generator produces, so nobody has hand-edited."""
    for path in make_arm_notebooks.build(out_dir=str(tmp_path)):
        with open(path) as fh:
            fresh = ["".join(c["source"]) for c in json.load(fh)["cells"]]
        assert fresh == arms[os.path.basename(path)[len("ppo_arm_"):-len(".ipynb")]]


def test_the_branch_matches_the_branch_this_code_is_on(arms):
    try:
        head = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                              cwd=acs_data.ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pytest.skip("git unavailable")
    if head.returncode != 0:
        pytest.skip("not a git checkout")
    for name, cells in arms.items():
        assert f'BRANCH   = "{head.stdout.strip()}"' in cells[0], name


def test_drive_output_lands_under_mydrive_and_the_arms_do_not_share_a_folder(arms):
    """Both mirror two FIXED-name report files; one folder and two live sessions race."""
    dirs = set()
    for cells in arms.values():
        ns = {}
        exec(compile(cells[0], "config", "exec"), ns)
        assert ns["DRIVE_OUT_DIR"].startswith("/content/drive/MyDrive/")
        dirs.add(ns["DRIVE_OUT_DIR"])
    assert len(dirs) == 2


def _run_isolated(cells, tmp_path, monkeypatch, ckpt=None, **over):
    cwd, saved = os.getcwd(), dict(sys.modules)
    try:
        ns = {"__name__": "__main__"}
        exec(cells[0], ns)
        ns["cfg"]["USE_WANDB"] = False           # getpass would block
        exec(cells[1], ns)                       # SETUP: purges experiments.* here

        import experiments.ppo.run_ppo as run_ppo   # re-imported fresh after the purge
        calls = []
        monkeypatch.setattr(run_ppo, "main",
                            lambda cfg, log=print: (calls.append(dict(cfg)),
                                                    {"stage": cfg["STAGE"]})[1])
        ns["LOCAL_OUT_DIR"] = str(tmp_path)      # absolute -> join() keeps it
        ns.update(over)
        if ckpt:
            (tmp_path / ckpt).write_bytes(b"")
        exec(cells[2], ns)
        return ns, calls
    finally:
        os.chdir(cwd)
        sys.modules.clear()
        sys.modules.update(saved)


@pytest.mark.parametrize("name,variant,lam", [("control", None, 0.0), ("s20mk2", "s20mk2", 0.2)])
def test_the_run_cell_carries_the_reward_into_every_stage(arms, tmp_path, monkeypatch,
                                                          name, variant, lam):
    tag = f"ppo-drt-AC19_extended_ho60{f'-{variant}-lam{lam:g}' if variant else ''}-s142"
    ns, calls = _run_isolated(arms[name], tmp_path, monkeypatch, ckpt=f"{tag}.pt")

    assert [c["STAGE"] for c in calls] == ["convert", "parity", "train", "beam_eval", "report"]
    assert ns["TAG"] == tag
    for c in calls:
        assert c["SHAPING"] == variant and c["LAMBDA"] == lam
        assert c["DATASET"] == "AC19_extended_ho60"
        assert c["SEED"] == 142
    # the benchmark-60 beam decodes the checkpoint this arm just trained
    beam = next(c for c in calls if c["STAGE"] == "beam_eval")
    assert beam["BEAM_CHECKPOINT"].endswith(f"{tag}.pt")
    assert beam["EVAL_DATASET"] == "benchmark60", "the standing evaluation rule"
    assert beam["BEAM_WIDTH"] == 1024 and beam["BEAM_MAX_STEPS"] == 150


def test_a_missing_checkpoint_skips_the_eval_instead_of_crashing(arms, tmp_path, monkeypatch):
    _, calls = _run_isolated(arms["control"], tmp_path, monkeypatch)
    assert [c["STAGE"] for c in calls] == ["convert", "parity", "train", "report"]


def test_the_smoke_shrinks_the_updates_and_nothing_that_would_make_it_a_proxy(arms, tmp_path,
                                                                              monkeypatch):
    """Two updates, but production beam width -- a narrowed beam measures nothing.

    No override: both notebooks must SHIP with the smoke armed, so the user cannot launch
    17 A100-hours without a rehearsal first. That is the standing rule, asserted here.
    """
    ns, calls = _run_isolated(arms["s20mk2"], tmp_path, monkeypatch)
    assert ns["SMOKE_RUN"] is True, "the shipped default must be smoke-on"
    train = next(c for c in calls if c["STAGE"] == "train")
    assert train["MAX_UPDATES"] == 2 and train["SAVE_EVERY"] == 1
    assert train["BEAM_WIDTH"] == 1024 and train["BEAM_MAX_STEPS"] == 150
    assert train["BEAM_TIME_BUDGET_S"] == ns["SMOKE_SECONDS"]
    assert calls[-1]["SMOKE_RUN"] is True


def test_flipping_the_smoke_off_is_the_whole_full_run_edit(arms, tmp_path, monkeypatch):
    tag = "ppo-drt-AC19_extended_ho60-s142"
    ns, calls = _run_isolated(arms["control"], tmp_path, monkeypatch, ckpt=f"{tag}.pt",
                              SMOKE_RUN=False)
    train = next(c for c in calls if c["STAGE"] == "train")
    assert train["MAX_UPDATES"] == ns["MAX_UPDATES"] == 1000
    assert train["SAVE_EVERY"] == 25
    assert train["BEAM_TIME_BUDGET_S"] is None, "no wall-clock stop on the real run"
    assert calls[-1]["SMOKE_RUN"] is False
    assert [c["STAGE"] for c in calls].count("report") == 1
