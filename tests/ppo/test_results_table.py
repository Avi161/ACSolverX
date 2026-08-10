"""The table is only as trustworthy as what it refuses to read.

`num_solved` from training and a beam over some other file both look like the
paper's number. The table must count neither, and it must get the seed spread
from separate files -- which only works if `beam_tag` and the parser agree.
"""

import json
import os

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data                                 # noqa: E402
from experiments.ppo.results_table import (                          # noqa: E402
    aggregate, format_table, parse_name, print_table, read_run, scan)
from experiments.ppo.run_ppo import beam_tag, checkpoint_tag         # noqa: E402

L = 24


def _cfg(**over):
    base = {"EVAL_DATASET": "1190MS", "BEAM_WIDTH": 1024, "BEAM_MAX_STEPS": 150,
            "MAX_RELATOR_LENGTH": L}
    base.update(over)
    return base


def _write(dir_, stem, solved, rows, plen=7):
    os.makedirs(dir_, exist_ok=True)
    with open(os.path.join(dir_, stem + ".jsonl"), "w") as fh:
        for i in range(rows):
            s = i < solved
            fh.write(json.dumps({"presentation_idx": i, "solved": s,
                                 "path_length": plen if s else -1}) + "\n")


def test_the_parser_and_the_namer_are_the_same_convention():
    """If these drift, the scan silently sees zero runs and prints an empty table."""
    cfg = _cfg()
    got = parse_name(beam_tag(cfg, checkpoint_tag(cfg, "r/ppo-drt-1190MS-s142.pt", 1000)))
    assert got["arm"] == "1190MS" and got["seed"] == 142 and got["update"] == 1000
    assert got["eval"] == "1190MS" and got["width"] == 1024 and got["steps"] == 150
    assert got["trained_here"] is True

    ext = parse_name(beam_tag(cfg, checkpoint_tag(cfg, "r/ppo-drt-AC19_extended-s7.pt", 500)))
    assert ext["arm"] == "AC19_extended" and ext["seed"] == 7 and ext["update"] == 500

    up = parse_name(beam_tag(_cfg(BEAM_ALPHA=0.5), "610model_params"))
    assert up["trained_here"] is False and up["arm"] == "upstream:610model_params"
    assert up["alpha"] == 0.5 and up["seed"] is None

    hot = parse_name(beam_tag(_cfg(BEAM_TEMPERATURE=0.3, SEED=4), "610model_params"))
    assert hot["temperature"] == 0.3 and hot["beam_seed"] == 4

    assert parse_name("ppo-drt-1190MS-s142") is None       # a training jsonl stem


def test_only_beam_runs_over_the_paper_denominator_are_counted(tmp_path):
    cfg = _cfg()
    d = str(tmp_path)
    total = len(acs_data.read_raw("1190MS"))
    _write(d, beam_tag(cfg, checkpoint_tag(cfg, "ppo-drt-1190MS-s142.pt", 1000)), 588, total)
    # same policy, decoded over the training file instead -- a different denominator
    _write(d, beam_tag(_cfg(EVAL_DATASET="AC19_extended"),
                       checkpoint_tag(cfg, "ppo-drt-1190MS-s142.pt", 1000)), 900, 1000)
    # and the training log, which carries `num_solved` over 156,762 rows
    with open(os.path.join(d, "ppo-drt-1190MS-s142.jsonl"), "w") as fh:
        fh.write(json.dumps({"update": 1, "num_solved": 12345}) + "\n")

    runs = scan(d)
    assert len(runs) == 1
    assert runs[0]["solved"] == 588 and runs[0]["complete"] and runs[0]["total"] == total
    assert runs[0]["mean_path_length"] == 7


def test_a_beam_named_file_that_is_not_beam_rows_is_an_error_not_a_zero(tmp_path):
    cfg = _cfg()
    bad = os.path.join(str(tmp_path), beam_tag(cfg, "610model_params") + ".jsonl")
    with open(bad, "w") as fh:
        fh.write(json.dumps({"update": 3, "num_solved": 99}) + "\n")
    with pytest.raises(ValueError):
        read_run(bad)


def test_the_seed_spread_comes_from_separate_files(tmp_path):
    cfg = _cfg()
    d = str(tmp_path)
    total = len(acs_data.read_raw("1190MS"))
    for seed, solved in [(142, 585), (7, 591), (3, 588)]:
        _write(d, beam_tag(cfg, checkpoint_tag(cfg, f"ppo-drt-1190MS-s{seed}.pt", 1000)),
               solved, total)
    _write(d, beam_tag(cfg, checkpoint_tag(cfg, "ppo-drt-AC19_extended-s142.pt", 1000)),
           607, total)

    rows = {a["arm"]: a for a in aggregate(scan(d))}
    ms = rows["1190MS"]
    assert ms["n_runs"] == 3 and ms["seeds"] == [3, 7, 142]
    assert ms["mean"] == pytest.approx((585 + 591 + 588) / 3)
    assert (ms["min"], ms["max"]) == (585, 591)
    assert rows["AC19_extended"]["label"] == "PPO-SUB-DRT + AC-19"

    text = format_table(scan(d))
    assert "588.0 (585-591)" in text
    assert f"SOLVED / {total}" in text
    assert "588.2 (585-591)" in text            # the paper reference row


def test_an_unfinished_decode_is_labelled_partial(tmp_path):
    cfg = _cfg()
    d = str(tmp_path)
    _write(d, beam_tag(cfg, checkpoint_tag(cfg, "ppo-drt-1190MS-s142.pt", 1000)), 300, 400)
    a = aggregate(scan(d))[0]
    assert not a["complete"] and a["partial_rows"] == [400]
    assert "PARTIAL" in format_table(scan(d))


def test_the_table_reads_back_what_earlier_sessions_left_on_the_mirror(tmp_path):
    cfg = _cfg()
    local, mirror = str(tmp_path / "local"), str(tmp_path / "drive")
    total = len(acs_data.read_raw("1190MS"))
    _write(mirror, beam_tag(cfg, checkpoint_tag(cfg, "ppo-drt-1190MS-s142.pt", 1000)), 585, total)
    _write(local, beam_tag(cfg, checkpoint_tag(cfg, "ppo-drt-1190MS-s7.pt", 1000)), 591, total)

    out = print_table(local, mirror_dir=mirror, log=lambda *_: None)
    assert out["summary"][0]["n_runs"] == 2
    assert out["summary"][0]["seeds"] == [7, 142]

    # a local file is the live one -- the mirror must never overwrite it
    _write(mirror, beam_tag(cfg, checkpoint_tag(cfg, "ppo-drt-1190MS-s7.pt", 1000)), 1, total)
    again = print_table(local, mirror_dir=mirror, log=lambda *_: None)
    assert sorted(r["solved"] for r in again["runs"]) == [585, 591]


def test_print_table_on_an_empty_directory_says_so(tmp_path, capsys):
    out = print_table(str(tmp_path))
    assert out["runs"] == [] and out["summary"] == []
    assert "no beam runs yet" in capsys.readouterr().out
