"""`stage_report`: the one file that has to survive a Colab disconnect.

The smoke round trip is "run five minutes on a GPU, hand back one artefact", so
this stage is only as good as what that artefact contains. What it must carry,
and what is pinned here: the parity verdict (persisted, not scrolled away), the
measured cost per presentation and what it projects over the real denominator of
1190, and a certificate check of the rows the run actually produced.
"""

import json
import os

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, run_ppo                          # noqa: E402
from experiments.ppo.beam import run_beam                              # noqa: E402
from experiments.ppo.policy import RelativeDualRingActorCritic         # noqa: E402

L = 24
STEM = "AC19_extended"


@pytest.fixture(scope="module")
def presentations():
    return acs_data.load_presentations(STEM, L)


def _cfg(out_dir, **over):
    cfg = {"OUT_DIR": str(out_dir), "EVAL_DATASET": STEM, "MAX_RELATOR_LENGTH": L,
           "BEAM_WIDTH": 8, "BEAM_MAX_STEPS": 30, "SMOKE_RUN": True,
           "BEAM_TIME_BUDGET_S": 300, "MIRROR_DIR": None}
    cfg.update(over)
    return cfg


def _beam_file(out_dir, presentations, n=8):
    torch.manual_seed(0)
    model = RelativeDualRingActorCritic(max_len=L).eval()
    path = os.path.join(out_dir, f"beam-610model_params-{STEM}-w8-t30-L{L}.jsonl")
    run_beam(model, presentations, path, start=0, end=n, beam_width=8, max_steps=30,
             progress=lambda *_: None)
    return path


def test_the_report_measures_cost_and_projects_it_over_the_real_denominator(
        tmp_path, presentations):
    path = _beam_file(tmp_path, presentations)
    report = run_ppo.stage_report(_cfg(tmp_path), log=lambda *_: None)

    assert report["eval_denominator"] == len(acs_data.read_raw(STEM))
    run = report["beam_runs"][0]
    assert run["rows"] == 8
    assert run["verified"] == run["solved"], "every solved row must certify"
    assert run["verify_failures"] == []
    # the projection is this run's own mean, over the whole evaluation file.
    # Computed from the rows, not from the rounded field, so the rounding cannot
    # quietly become the thing under test.
    secs = [json.loads(l)["seconds"] for l in open(path) if l.strip()]
    expected = (sum(secs) / len(secs)) * report["eval_denominator"] / 3600
    assert run["projected_full_run_hours"] == pytest.approx(expected, rel=0.01)
    # the spread ships alongside it, because a head-of-file slice is not the mean
    assert run["seconds_per_row_min"] <= run["seconds_per_row_mean"] <= run["seconds_per_row_max"]


def test_the_report_is_written_and_mirrored(tmp_path, presentations):
    out, mirror = tmp_path / "out", tmp_path / "drive"
    out.mkdir()
    _beam_file(out, presentations, n=4)
    run_ppo.stage_report(_cfg(out, MIRROR_DIR=str(mirror)), log=lambda *_: None)
    for d in (out, mirror):
        with open(d / "smoke_report.json") as fh:
            assert json.load(fh)["beam_runs"][0]["rows"] == 4


def test_the_parity_verdict_survives_a_lost_scrollback(tmp_path, presentations):
    """`stage_parity` persists; the report reads that, never re-runs the gate."""
    with open(tmp_path / "parity.json", "w") as fh:
        json.dump({"parity_ok": True, "max_abs_logit_diff": 3e-6,
                   "jax_available": True}, fh)
    _beam_file(tmp_path, presentations, n=3)
    report = run_ppo.stage_report(_cfg(tmp_path), log=lambda *_: None)
    assert report["parity"]["parity_ok"] is True
    assert report["parity"]["max_abs_logit_diff"] == 3e-6


def test_a_missing_parity_file_is_reported_as_absent_not_as_a_pass(tmp_path, presentations):
    _beam_file(tmp_path, presentations, n=3)
    report = run_ppo.stage_report(_cfg(tmp_path), log=lambda *_: None)
    assert report["parity"] is None


def test_a_bad_certificate_reaches_the_report(tmp_path, presentations):
    """The report must not launder a failure into a clean solve count."""
    path = _beam_file(tmp_path, presentations, n=8)
    rows = [json.loads(l) for l in open(path) if l.strip()]
    solved = next(r for r in rows if r["solved"])
    solved["path"] = [(solved["path"][0] + 1) % (2 * 2 * L * L)] + solved["path"][1:]
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    run = run_ppo.stage_report(_cfg(tmp_path), log=lambda *_: None)["beam_runs"][0]
    assert run["verify_failures"], "a tampered path must show up in the report"
    assert run["verified"] < run["solved"]


def test_the_environment_block_names_the_machine(tmp_path, presentations):
    _beam_file(tmp_path, presentations, n=2)
    env = run_ppo.stage_report(_cfg(tmp_path), log=lambda *_: None)["environment"]
    assert env["torch"] and env["python"]
    assert "allow_tf32" in env and "cuda_available" in env
    if env["cuda_available"]:
        assert env["gpu"] and env["compute_capability"]


def test_a_training_jsonl_contributes_its_last_update(tmp_path, presentations):
    _beam_file(tmp_path, presentations, n=2)
    with open(tmp_path / "ppo-drt-1190MS-s142.jsonl", "w") as fh:
        for u in (1, 2):
            fh.write(json.dumps({"update": u, "sps": 1234.5, "num_solved": 10 * u,
                                 "num_solved_pinned": u, "collect_s": 1.0,
                                 "learn_s": 2.0}) + "\n")
    got = run_ppo.stage_report(_cfg(tmp_path), log=lambda *_: None)["training_runs"]
    assert len(got) == 1
    assert got[0]["update"] == 2 and got[0]["sps"] == 1234
    assert got[0]["seconds_per_update"] == 3.0


def test_report_is_a_registered_stage_reachable_through_main(tmp_path, presentations):
    _beam_file(tmp_path, presentations, n=2)
    cfg = _cfg(tmp_path, STAGE="report")
    assert run_ppo.main(cfg, log=lambda *_: None)["beam_runs"][0]["rows"] == 2
