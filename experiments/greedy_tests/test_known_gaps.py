"""Real defects in ``run_baseline.py``, pinned rather than fixed.

Each test below asserts the **desired** behaviour and is marked
``xfail(strict=True)``. While the bug lives they xfail and the suite is green.
The moment someone fixes the underlying bug the test xpasses, strict mode turns
that into a failure, and whoever fixed it is told to delete the marker. That is
the intended lifecycle -- these are not permanent excuses.

Both defects break the same thing: resuming a run after a disconnect, which is
the entire reason the jsonl exists.

FIXED, marker removed: the ``todo[0]`` IndexError on a fully-resumed heavy run.
The warm-up is now guarded by ``and jobs``; the test below is a plain regression
test. One gap remains: ``_read_done``'s unguarded ``json.loads``.
"""

import json
import os

import pytest

from experiments.run_baseline import (
    DEFAULT_CONFIG, _read_done, _resolve_paths, _run_prefix, run_dataset,
)
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines


@pytest.fixture
def tiny_dataset(tmp_path):
    lines = load_flat_lines(MS640)[:4]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


@pytest.mark.xfail(strict=True, raises=json.JSONDecodeError,
                   reason="run_baseline.py:188 -- _read_done does not guard "
                          "json.loads; fix it and delete this marker")
def test_read_done_tolerates_a_truncated_trailing_line(tmp_path):
    """A Colab disconnect mid-write leaves exactly this: a half-written last line.

    ``_read_done`` calls ``json.loads`` unguarded, so the resume it exists to
    enable crashes instead. Blank lines are skipped, but a partial JSON object is
    not. The fix is to drop (or truncate) an unparseable final line.
    """
    p = tmp_path / "out.jsonl"
    p.write_text('{"pres_id": 0, "solved": true}\n'
                 '{"pres_id": 1, "solved": false}\n'
                 '{"pres_id": 2, "solv')          # power cut here
    done, seen, solved = _read_done(str(p))
    assert done == {0, 1}
    assert (seen, solved) == (2, 1)


def test_a_fully_resumed_heavy_run_does_not_crash(tmp_path, tiny_dataset):
    """``HIGH_SPEEDUP`` + multiple workers + nothing left to do must not raise.

    The numba warm-up used to read ``todo[0]`` unconditionally inside
    ``if high and n_workers > 1``, before the pool was created, so re-running a
    finished heavy sweep to confirm it is complete raised ``IndexError`` instead
    of printing "nothing to do". The guard is now ``if high and n_workers > 1
    and jobs``. No worker is ever spawned, so this is a fast test.
    """
    out_dir = str(tmp_path / "out")
    cfg = {**DEFAULT_CONFIG, "DATASET": tiny_dataset, "LOCAL_OUT_DIR": out_dir,
           "USE_WANDB": False, "HIGH_SPEEDUP": True, "N_WORKERS": 2}

    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(cfg, 500, 4)
    with open(os.path.join(out_dir, prefix + "01_01_20.jsonl"), "w") as f:
        for pid in range(4):
            f.write(json.dumps({"pres_id": pid, "solved": True}) + "\n")

    resolved, _, _, _ = _resolve_paths(cfg, 500, 4)
    assert _read_done(resolved)[1] == 4, "the fixture must leave nothing to do"

    assert run_dataset(cfg, 500) == resolved
