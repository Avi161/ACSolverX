"""run.py on your own presentations: ``--pres`` (one presentation per flag) and ``--input`` (a file, see acx/data.py)."""
import json
import os
import re

import pytest

import run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "configs", "smoke.toml")        # S20_MK2 greedy, fast backend, budget 1000, rows "0:20"
HYBRID = os.path.join(ROOT, "configs", "hybrid.toml")
AK2 = "xxYYY, xyxYXY"        # Akbulut-Kirby n = 2: solved in a few dozen pops
AK3 = "xxxYYYY, xyxYXY"      # n = 3 (relators in the other order): no AC path is known, so the budget runs out
SPEC = ("--set", "search.backend=spec")


def run_cli(out, *args, config=SMOKE):
    run.main(["--config", config, "--out", str(out), *args])


def records(out, name="smoke"):
    with open(out / name / "paths.jsonl") as f:
        return [json.loads(line) for line in f]


def summary(out, name="smoke"):
    with open(out / name / "summary.json") as f:
        return json.load(f)


def outcome(out, name):
    """What a run decided about each row: id, solved, cost."""
    return [(r["id"], r["solved"], r["cost"]) for r in records(out, name)]


def config(out, name):
    """The run's ``config.json`` without its name."""
    with open(out / name / "config.json") as f:
        return json.load(f) | {"name": None}


def printed(capsys):
    """The per-presentation lines run.py printed, as dicts: ``id``, ``relators``, ``status`` and the ``key=value`` fields."""
    lines = []
    for line in capsys.readouterr().out.splitlines():
        if re.match(r"\d+  ", line):                          # the lines that start with a row id
            row_id, relators, status, *fields = line.split("  ")
            lines.append({"id": row_id, "relators": relators, "status": status,
                          **dict(field.partition("=")[::2] for field in fields)})
    return lines


def test_pres_prints_a_line_per_presentation_on_the_smoke_config(tmp_path, capsys):
    run_cli(tmp_path, "--pres", AK2, "--pres", AK3)
    solved, unsolved = printed(capsys)
    recs = records(tmp_path)
    cost = summary(tmp_path).get("cost_unit") or "cost"                 # the cost is named by its unit: pops=22
    assert [r["solved"] for r in recs] == [True, False]
    assert solved == {"id": "0", "relators": AK2, "status": "solved", "kind": "ac_path", cost: str(recs[0]["cost"]),
                      "sub_moves": str(recs[0]["sub_moves"]), "elem_moves": str(recs[0]["elem_moves"])}
    assert unsolved == {"id": "1", "relators": AK3, "status": "unsolved", cost: "1000"}      # the whole budget, no path


def test_pres_writes_its_presentations_as_letters_lines_and_uses_them_as_the_benchmark(tmp_path):
    run_cli(tmp_path, "--pres", "xxYYY,xyxYXY", "--pres", "xy  yz z", "--set", "name=mine", "--set",
            "search.priority=length", *SPEC)
    assert (tmp_path / "mine" / "input.txt").read_text() == "xxYYY, xyxYXY\nxy, yz, z\n"
    with open(tmp_path / "mine" / "config.json") as f:
        assert json.load(f)["benchmark"] == os.path.join(str(tmp_path), "mine", "input.txt")
    assert [r["solved"] for r in records(tmp_path, "mine")] == [True, True]            # two and three generators


def test_pres_reports_the_error_of_a_presentation_no_ac_path_starts_from(tmp_path, capsys):
    run_cli(tmp_path, "--pres", "xyxYXY", "--pres", "xxx, yy", *SPEC)
    one_relator, det_zero = printed(capsys)
    assert one_relator["status"] == det_zero["status"] == "unsolved"
    assert "unbalanced" in one_relator["error"] and "det" in det_zero["error"]


def test_rows_still_selects_among_the_presentations(tmp_path, capsys):
    run_cli(tmp_path, "--pres", AK2, "--pres", AK3, "--rows", "1", "--set", "search.budget=50")
    assert [r["id"] for r in records(tmp_path)] == ["1"]
    assert [line["id"] for line in printed(capsys)] == ["1"]


def test_pres_runs_any_method(tmp_path, capsys):
    run_cli(tmp_path, "--pres", AK2, config=HYBRID)
    (line,) = printed(capsys)
    assert (line["status"], line["kind"]) == ("solved", "ac_path")
    assert (summary(tmp_path, "hybrid").get("cost_unit") or "cost") in line


@pytest.mark.parametrize("text", ["xy1", "", "x|y"])
def test_a_bad_pres_stops_before_anything_is_written(tmp_path, capsys, text):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path, "--pres", AK2, "--pres", text)
    assert e.value.code == 2 and not os.listdir(tmp_path)
    assert repr(text) in capsys.readouterr().err


def test_pres_and_input_cannot_be_combined(tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(tmp_path, "--pres", AK2, "--input", "mine.txt")
    assert "not allowed with" in capsys.readouterr().err


def test_rerunning_the_same_presentations_resumes_and_other_ones_need_fresh(tmp_path):
    options = (*SPEC, "--set", "search.budget=50")
    run_cli(tmp_path, "--pres", AK2, *options)
    run_cli(tmp_path, "--pres", AK2, *options)
    assert len(records(tmp_path)) == 1                                                 # the row was not searched again
    with pytest.raises(SystemExit, match="other presentations"):
        run_cli(tmp_path, "--pres", AK3, *options)
    assert (tmp_path / "smoke" / "input.txt").read_text() == AK2 + "\n"
    run_cli(tmp_path, "--pres", AK3, "--fresh", *options)
    assert [r["solved"] for r in records(tmp_path)] == [False]
    assert (tmp_path / "smoke" / "input.txt").read_text() == AK3 + "\n"


def test_pres_does_not_take_over_the_folder_of_a_regular_run(tmp_path):
    run_cli(tmp_path, "--rows", "0:2", *SPEC)                                          # smoke on its own benchmark
    with pytest.raises(SystemExit, match="another name"):
        run_cli(tmp_path, "--pres", AK2)
    assert not (tmp_path / "smoke" / "input.txt").exists() and len(records(tmp_path)) == 2


def test_input_runs_a_user_file_and_keeps_its_ids(tmp_path):
    mine = tmp_path / "mine.jsonl"
    mine.write_text('{"id": "AK2", "relators": ["xxYYY", "xyxYXY"]}\n{"id": "AK3", "relators": ["xyxYXY", "xxxYYYY"]}\n')
    run_cli(tmp_path, "--input", str(mine))
    assert [(r["id"], r["solved"]) for r in records(tmp_path)] == [("AK2", True), ("AK3", False)]


def test_input_is_the_same_as_setting_the_benchmark(tmp_path):
    mine = tmp_path / "mine.txt"
    mine.write_text(f"{AK2}\nxy, yz, z\n")
    options = ("--set", "search.priority=length", *SPEC)
    run_cli(tmp_path, "--input", str(mine), "--set", "name=a", *options)
    run_cli(tmp_path, "--set", f"benchmark={mine}", "--set", "rows=", "--set", "name=b", *options)
    assert outcome(tmp_path, "a") == outcome(tmp_path, "b") and len(outcome(tmp_path, "a")) == 2
    assert config(tmp_path, "a") == config(tmp_path, "b")


def test_input_runs_every_row_of_the_file_though_the_config_slices_rows(tmp_path):
    many = tmp_path / "many.txt"
    many.write_text("x, y\n" * 25)                                                     # smoke.toml says rows = "0:20"
    run_cli(tmp_path, "--input", str(many), *SPEC)
    assert len(records(tmp_path)) == 25
    run_cli(tmp_path, "--input", str(many), "--rows", "0:3", "--set", "name=few", *SPEC)
    assert len(records(tmp_path, "few")) == 3


def test_a_bad_line_in_the_input_file_stops_the_run_before_anything_is_written(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("xxYYY, xyxYXY\nxy1\n")
    with pytest.raises(ValueError, match=r"bad\.txt:2: "):
        run_cli(tmp_path / "out", "--input", str(bad))
    assert not (tmp_path / "out").exists()


def test_a_missing_input_file_names_the_path(tmp_path):
    with pytest.raises(FileNotFoundError, match="nowhere.csv"):
        run_cli(tmp_path / "out", "--input", str(tmp_path / "nowhere.csv"))


def test_an_empty_input_path_is_an_error_and_not_the_configs_benchmark(tmp_path):
    with pytest.raises(KeyError, match="unknown benchmark"):
        run_cli(tmp_path / "out", "--input", "")
    assert not (tmp_path / "out").exists()


def test_relative_paths_work_from_any_directory(tmp_path, monkeypatch):
    (tmp_path / "mine.txt").write_text(AK2 + "\n")
    monkeypatch.chdir(tmp_path)                                    # not the repository: mine.txt and results/ are here
    run.main(["--config", SMOKE, "--input", "mine.txt", "--set", "name=a", *SPEC])
    run.main(["--config", SMOKE, "--pres", AK2, "--set", "name=b", *SPEC])
    assert [r["solved"] for r in records(tmp_path / "results", "a")] == [True]
    assert [r["solved"] for r in records(tmp_path / "results", "b")] == [True]


def test_help_describes_both_flags(capsys):
    with pytest.raises(SystemExit):
        run.main(["--help"])
    out = capsys.readouterr().out
    assert "--input" in out and "--pres" in out
