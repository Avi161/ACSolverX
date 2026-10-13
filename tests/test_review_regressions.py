"""Adversarial boundary cases found in the review of main at f4d5d21."""
import importlib
import json
from pathlib import Path

import numpy as np
import pytest

from acx import data
from acx.core.words import Presentation
from acx.ngen.sweep import SweepConfig, SweepError, run as sweep_run
from acx.ngen.sweep.rows import finished_rows, row_path, sweep_row_file
from acx.runner import load_config
from acx.runner.rundir import read_records


@pytest.mark.parametrize("name", ["", ".", "..", "../outside", "/tmp/outside", r"..\outside", "C:outside"])
def test_run_names_cannot_redirect_output(name):
    with pytest.raises(ValueError, match="name"):
        load_config("configs/rank3_bf.toml", [f"name={json.dumps(name)}"])


def test_fresh_cannot_delete_a_parent_directory(tmp_path):
    sentinel = tmp_path / "keep.txt"
    sentinel.write_text("keep")
    cfg = dict(name="..", method="rankn", benchmark="ms640", rows="0:0",
               search=dict(backend="spec"), rankn=dict(max_len=1))
    with pytest.raises(ValueError, match="name"):
        sweep_run(cfg, tmp_path / "out", fresh=True)
    assert sentinel.read_text() == "keep"


@pytest.mark.parametrize("row_id", ["../outside", "/tmp/outside", r"..\outside", "a/b", "a%2Fb", "a.npz.tmp1", "ms:1"])
def test_sweep_row_ids_roundtrip_inside_rows_directory(tmp_path, row_id):
    folder = tmp_path / "run"
    (folder / "rows").mkdir(parents=True)
    path = Path(row_path(folder, row_id))
    assert path.parent == folder / "rows"
    cfg = SweepConfig.from_cfg(dict(search=dict(backend="spec", budget=2), rankn=dict(max_len=1)))
    sweep_row_file((folder, row_id, Presentation.parse("x", "y"), cfg))
    assert finished_rows(folder) == [row_id]


def test_sweep_rejects_changed_unselected_rows_before_summarizing(tmp_path):
    mine = tmp_path / "mine.csv"
    mine.write_text("id,r1,r2\na,x,y\nb,xy,y\n")
    cfg = dict(name="sweep", method="rankn", benchmark=str(mine),
               search=dict(backend="spec", budget=2), rankn=dict(max_len=1))
    sweep_run(cfg, tmp_path, log=lambda *_: None)
    summary = tmp_path / "sweep" / "summary.json"
    before = summary.read_bytes()
    mine.write_text("id,r1,r2\na,x,y\nb,xx,yy\n")
    with pytest.raises(SweepError, match="b"):
        sweep_run({**cfg, "rows": "a"}, tmp_path, log=lambda *_: None)
    assert summary.read_bytes() == before


def test_sweep_path_lengths_fit_the_permitted_budget(monkeypatch):
    module = importlib.import_module("acx.ngen.sweep.rows")
    from acx.core.capcount import blank
    sc = SweepConfig.from_cfg(dict(search=dict(budget=65535), rankn=dict(max_len=1)))
    monkeypatch.setattr(module, "search_control_and_null", lambda *args: ({}, {}))
    record = dict(pops=40001, path_len=40000, min_total=3, **blank())
    monkeypatch.setattr(module, "search_starts", lambda *args: ([record], []))
    assert module.sweep_row("a", data.AK(2), sc)["path_len"].tolist() == [40000]


def test_reports_and_resume_agree_on_an_uncommitted_last_record(tmp_path):
    from acx.report.load import read_records as report_records
    path = tmp_path / "paths.jsonl"
    path.write_text('{"id":"a","solved":true}\n{"id":"b","solved":true}')
    assert report_records(path) == read_records(path) == [dict(id="a", solved=True)]


@pytest.mark.parametrize("value", [1.9, "1", True, np.float64(1.0)])
def test_presentation_does_not_coerce_invalid_symbols(value):
    with pytest.raises(ValueError, match="integer"):
        Presentation(2, ((value,), (2,)))


@pytest.mark.parametrize("rank", [-1, 2.0, True, "2"])
def test_presentation_requires_a_nonnegative_integer_rank(rank):
    with pytest.raises(ValueError, match="n_gen"):
        Presentation(rank, ())


@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_rl_config_rejects_nonfinite_scores(value):
    with pytest.raises(ValueError, match="rl.alpha"):
        load_config("configs/rl.toml", [f"rl.alpha={value}"])


def test_cov_high_speed_skips_certificate_work(monkeypatch):
    module = importlib.import_module("acx.cov.run")
    from acx.runner.methods import cov
    def forbidden(*args, **kwargs):
        pytest.fail("path=false must not construct or replay a certificate")
    monkeypatch.setattr(module, "verify", forbidden)
    monkeypatch.setattr(module, "transport", forbidden)
    monkeypatch.setattr(importlib.import_module("acx.search.engine"), "replay", forbidden)
    cfg = load_config("configs/cov.toml", ["path=false"])
    assert cov(data.AK(2), cfg)["solved"]


def test_ppo_normaliser_follows_the_trainer_of_the_checkpoint():
    torch = pytest.importorskip("torch")
    from acx.rl.env import VecEnv
    env = VecEnv(torch.tensor([[1, 0, 2, 0]]), 1, L=2, gamma=.5)
    observed = []
    for reward, done in [(1., False), (2., True), (3., False)]:
        env._normalise(torch.tensor([reward]), torch.tensor([done]))
        observed.append(float(env.mean[0]))
    # As the JAX NormalizeVecReward that trained the shipped weights: a step's own done clears the return before its
    # reward is added, so the moments observe 1, 2, 4 (each update weighted by the observation length, 4 here).
    assert observed == pytest.approx([1., 1.5, 7 / 3], abs=1e-4)
    assert env.ret.tolist() == [4.]


def test_rl_high_speed_skips_certificate_work(monkeypatch):
    pytest.importorskip("torch")
    from acx.runner.methods import rl
    def forbidden(*args, **kwargs):
        pytest.fail("path=false must not construct or replay a certificate")
    monkeypatch.setattr("acx.rl.solve.replay", forbidden)
    monkeypatch.setattr("acx.rl.solve.to_acx_path", forbidden)
    cfg = load_config("configs/rl.toml", ["path=false", "rl.width=64", "rl.steps=60"])
    result = rl(data.load("ms640", ids=[0])[0].pres, cfg)
    assert result["solved"] and result["path"] is None and result["sub_moves"] > 0


def test_decode_later_rejects_an_id_reused_for_different_words(tmp_path):
    import run
    old = tmp_path / "old"
    old.mkdir()
    (old / "paths.jsonl").write_text('{"id":"0","solved":true,"pres":"x, y"}\n')
    with pytest.raises(SystemExit, match="different presentation"):
        run.main(["--config", "configs/smoke.toml", "--pres", "xx, yy",
                  "--solved-from", str(old), "--out", str(tmp_path / "out")])
    assert not (tmp_path / "out").exists()


def test_common_reports_reject_changed_presentations():
    from acx.report.load import Run
    from acx.report.table import common_ids, head_to_head
    a = Run("a", "greedy", "mine.csv", "pops", [dict(id="0", solved=True, pres="x, y")])
    b = Run("b", "greedy", "mine.csv", "pops", [dict(id="0", solved=True, pres="xy, y")])
    with pytest.raises(SystemExit, match="different presentations"):
        common_ids((a, b))
    with pytest.raises(SystemExit, match="different presentations"):
        head_to_head(a, b)


def test_atomic_failure_preserves_old_config(tmp_path, monkeypatch):
    from acx.runner.storage import write_json
    path = tmp_path / "config.json"
    path.write_text('{"version":1}')
    def interrupted(*args):
        raise OSError("interrupted before replacement")
    monkeypatch.setattr("acx.runner.storage.os.replace", interrupted)
    with pytest.raises(OSError, match="interrupted"):
        write_json(path, dict(version=2))
    assert json.loads(path.read_text()) == dict(version=1)
    assert list(tmp_path.iterdir()) == [path]


def test_run_directory_symlink_is_not_followed(tmp_path):
    from acx.runner.storage import run_directory
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "out"
    root.mkdir()
    (root / "run").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        run_directory(root, "run")


def test_numpy_integer_words_remain_supported():
    assert Presentation(np.int64(2), ((np.int8(1),), (np.int32(2),))) == Presentation.parse("x", "y")


@pytest.mark.parametrize("symbol", [0, 3, -3, np.int64(3), np.int8(0)])
def test_presentation_rejects_symbols_outside_its_rank(symbol):
    with pytest.raises(ValueError, match="outside"):
        Presentation(2, ((1, symbol),))


def test_rankn_fresh_keeps_its_inline_input(tmp_path):
    import run
    args = ["--config", "configs/rank3_bf.toml", "--pres", "x, y", "--out", str(tmp_path),
            "--set", "rankn.max_len=1", "--set", "search.backend=spec", "--set", "search.budget=2"]
    run.main(args)
    run.main([*args, "--fresh"])
    folder = tmp_path / "rank3_bf_pres"
    assert (folder / "input.txt").read_text() == "x, y\n"
    run.main(args)  # the saved config still refers to a readable input on resume


@pytest.mark.parametrize("ratio", [float("inf"), float("nan")])
def test_hybrid_ratio_is_finite(ratio):
    from acx.hybrid import HybridConfig
    with pytest.raises(ValueError, match="dyn_ratio"):
        HybridConfig(dyn_ratio=ratio)
