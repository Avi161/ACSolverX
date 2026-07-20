"""Output on a network mount is staged on local disk and mirrored whole-file.

Colab's Google Drive FUSE mount accepted flushed, appended rows from a long-idle
handle and dropped them: a 1M pooled run lost two presentations, and because the
ids never entered ``done`` every resume re-searched them and lost them again. The
same mount kept every row of the five serial ms640 runs, which append constantly,
and it keeps a whole-file copy without complaint.

So: append to local disk (never observed to lose a row), and give the mount a
whole-file copy. The mirror is the only thing that outlives the VM, so a resumed
run in a *new session* must seed its staging file from it.

``_is_remote`` is driven by ``_REMOTE_PREFIXES``, which these tests point at a
tmp_path so no real Drive mount is needed.
"""

import json
import os

import pytest

from experiments.run_baseline import DEFAULT_CONFIG, run_dataset
import experiments.run_baseline as rb
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

BUDGET = 500        # every fixture solves in <5 nodes; MAX_BUDGET = 1_000


@pytest.fixture
def tiny_dataset(tmp_path):
    lines = load_flat_lines(MS640)[:4]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


@pytest.fixture
def fake_drive(tmp_path, monkeypatch):
    """A directory that _is_remote() treats as a network mount."""
    d = tmp_path / "drive" / "out"
    d.mkdir(parents=True)
    monkeypatch.setattr(rb, "_REMOTE_PREFIXES", (str(tmp_path / "drive"),))
    return d


def _cfg(tmp_path, tiny_dataset, fake_drive, **over):
    return {**DEFAULT_CONFIG,
            "DATASET": tiny_dataset,
            "MOUNT_DRIVE": True,
            "DRIVE_OUT_DIR": str(fake_drive),
            "LOCAL_OUT_DIR": str(tmp_path / "local"),
            "STAGE_DIR": str(tmp_path / "stage"),
            "MIRROR_EVERY_S": 0,          # mirror on every row, for the test
            "USE_WANDB": False,
            "PROGRESS_EVERY": 100,
            "HIGH_SPEEDUP": True,
            "N_WORKERS": 1,
            "use_path": False,
            **over}


def _ids(path):
    with open(path) as f:
        return sorted(json.loads(ln)["pres_id"] for ln in f if ln.strip())


def test_is_remote_detects_the_colab_drive_mount():
    assert rb._is_remote("/content/drive/MyDrive/x/y.jsonl")
    assert not rb._is_remote("/content/results/y.jsonl")
    assert not rb._is_remote("results/y.jsonl")


def test_rows_land_on_local_disk_and_are_mirrored(tmp_path, tiny_dataset,
                                                  fake_drive):
    final = run_dataset(_cfg(tmp_path, tiny_dataset, fake_drive),
                        node_budget=BUDGET)

    stage = tmp_path / "stage" / os.path.basename(final)
    assert final.startswith(str(fake_drive)), "run_dataset must return the mirror"
    assert stage.exists(), "rows must be appended to local disk"
    assert _ids(str(stage)) == [0, 1, 2, 3]
    assert _ids(final) == [0, 1, 2, 3]
    assert open(str(stage)).read() == open(final).read()


def test_the_append_handle_never_touches_the_mount(tmp_path, tiny_dataset,
                                                   fake_drive, monkeypatch):
    """The mount only ever sees whole-file copies, never an incremental append."""
    real_open = open
    appended = []

    def spy(path, mode="r", *a, **kw):
        if "a" in mode and str(path).startswith(str(fake_drive)):
            appended.append(str(path))
        return real_open(path, mode, *a, **kw)

    monkeypatch.setattr("builtins.open", spy)
    run_dataset(_cfg(tmp_path, tiny_dataset, fake_drive), node_budget=BUDGET)
    assert appended == [], f"opened the mount for append: {appended}"


def test_a_new_session_seeds_the_stage_from_the_mirror(tmp_path, tiny_dataset,
                                                       fake_drive, capsys):
    """The VM (and its staging disk) is gone; only the mirror survives."""
    cfg = _cfg(tmp_path, tiny_dataset, fake_drive, SUBSET=(0, 2))
    final = run_dataset(cfg, node_budget=BUDGET)
    assert _ids(final) == [0, 1]

    stage = tmp_path / "stage" / os.path.basename(final)
    os.remove(stage)                                   # the VM died
    assert not stage.exists()

    cfg2 = _cfg(tmp_path, tiny_dataset, fake_drive, SUBSET=(0, 2))
    run_dataset(cfg2, node_budget=BUDGET)              # same run, new session

    out = capsys.readouterr().out
    assert "seeded" in out, "the stage must be rebuilt from the mirror"
    assert "2 already done, 0 to run" in out, \
        "a resumed run must not re-search what the mirror already has"
    assert _ids(final) == [0, 1]


def test_a_mirror_that_lost_rows_is_simply_re_run(tmp_path, tiny_dataset,
                                                  fake_drive, capsys):
    """The self-healing property: an id absent from the jsonl is just searched again."""
    cfg = _cfg(tmp_path, tiny_dataset, fake_drive)
    final = run_dataset(cfg, node_budget=BUDGET)
    assert _ids(final) == [0, 1, 2, 3]

    # the mount drops two rows, exactly as Drive did to presentations 7 and 8
    rows = [ln for ln in open(final) if ln.strip()]
    with open(final, "w") as f:
        f.writelines(r for r in rows if json.loads(r)["pres_id"] not in (1, 2))
    os.remove(tmp_path / "stage" / os.path.basename(final))

    run_dataset(_cfg(tmp_path, tiny_dataset, fake_drive), node_budget=BUDGET)

    assert "2 already done, 2 to run" in capsys.readouterr().out
    assert _ids(final) == [0, 1, 2, 3], "the lost rows must come back"


def test_an_interrupted_run_still_mirrors_what_it_earned(tmp_path, tiny_dataset,
                                                         fake_drive, monkeypatch):
    """A KeyboardInterrupt must not strand rows on a staging disk about to vanish."""
    real = rb.greedy_search
    n = [0]

    def boom(r1, r2, budget, **kw):
        n[0] += 1
        if n[0] > 2:
            raise KeyboardInterrupt("simulated Colab disconnect")
        return real(r1, r2, budget, **kw)

    monkeypatch.setattr(rb, "greedy_search", boom)
    cfg = _cfg(tmp_path, tiny_dataset, fake_drive, MIRROR_EVERY_S=10_000)

    with pytest.raises(KeyboardInterrupt):
        run_dataset(cfg, node_budget=BUDGET)

    remote = fake_drive / f"greedy_{BUDGET}_4_mrl24_cyc_all_" \
                          f"{__import__('datetime').datetime.now():%m_%d_%y}.jsonl"
    assert remote.exists(), "the finally-block mirror never ran"
    assert _ids(str(remote)) == [0, 1], "rows earned before the interrupt are safe"


def test_local_output_is_untouched_by_the_mirror_layer(tmp_path, tiny_dataset):
    """MOUNT_DRIVE=False: no staging, no mirroring, no behaviour change."""
    cfg = {**DEFAULT_CONFIG, "DATASET": tiny_dataset, "MOUNT_DRIVE": False,
           "LOCAL_OUT_DIR": str(tmp_path / "out"), "USE_WANDB": False,
           "PROGRESS_EVERY": 100, "HIGH_SPEEDUP": True, "N_WORKERS": 1,
           "use_path": False}
    final = run_dataset(cfg, node_budget=BUDGET)

    assert final.startswith(str(tmp_path / "out"))
    assert not (tmp_path / "out" / "_stage").exists()
    assert _ids(final) == [0, 1, 2, 3]
