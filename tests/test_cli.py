"""run.py on your own presentations: ``--pres`` (one presentation per flag) and ``--input`` (a file, see acx/data.py),
and how it ends on a bad config, row id or file."""
import gzip
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import ROOT

import run

SMOKE = os.path.join(ROOT, "configs", "smoke.toml")        # S20_MK2 greedy, fast backend, budget 1000, rows "0:20"
HYBRID = os.path.join(ROOT, "configs", "hybrid.toml")
RANK3 = os.path.join(ROOT, "configs", "rank3_bf.toml")     # the rank-n sweep, which has its own rows driver
AK2 = "xxYYY, xyxYXY"        # Akbulut-Kirby n = 2: solved in a few dozen pops
AK3 = "xxxYYYY, xyxYXY"      # n = 3 (relators in the other order): no AC path is known, so the budget runs out
SPEC = ("--set", "search.backend=spec")


def shipped_results():
    """Every file and folder of the repository's ``results/`` with its modification time."""
    return sorted((str(path), path.stat().st_mtime_ns) for path in Path(ROOT, "results").rglob("*"))


@pytest.fixture(autouse=True)
def shipped_results_stay_untouched():
    """``run_cli`` always passes ``--out``, so no test here may write into the shipped ``results/``."""
    before = shipped_results()
    yield
    assert shipped_results() == before


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
    recs = records(tmp_path, "smoke_pres")
    cost = summary(tmp_path, "smoke_pres").get("cost_unit") or "cost"   # the cost is named by its unit: pops=22
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
    assert [r["id"] for r in records(tmp_path, "smoke_pres")] == ["1"]
    assert [line["id"] for line in printed(capsys)] == ["1"]


def test_pres_runs_any_method(tmp_path, capsys):
    run_cli(tmp_path, "--pres", AK2, config=HYBRID)
    (line,) = printed(capsys)
    assert (line["status"], line["kind"]) == ("solved", "ac_path")
    assert (summary(tmp_path, "hybrid_pres").get("cost_unit") or "cost") in line


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
    assert len(records(tmp_path, "smoke_pres")) == 1                                   # the row was not searched again
    with pytest.raises(SystemExit, match="other presentations"):
        run_cli(tmp_path, "--pres", AK3, *options)
    assert (tmp_path / "smoke_pres" / "input.txt").read_text() == AK2 + "\n"
    run_cli(tmp_path, "--pres", AK3, "--fresh", *options)
    assert [r["solved"] for r in records(tmp_path, "smoke_pres")] == [False]
    assert (tmp_path / "smoke_pres" / "input.txt").read_text() == AK3 + "\n"


def test_pres_does_not_take_over_the_folder_of_a_regular_run(tmp_path):
    run_cli(tmp_path, "--rows", "0:2", *SPEC)                                          # smoke on its own benchmark
    run_cli(tmp_path, "--pres", AK2, *SPEC)                                            # smoke_pres, a folder of its own
    assert len(records(tmp_path, "smoke_pres")) == 1
    with pytest.raises(SystemExit, match="another name"):                              # the explicit name is the user's
        run_cli(tmp_path, "--pres", AK2, "--set", "name=smoke", *SPEC)
    assert not (tmp_path / "smoke" / "input.txt").exists() and len(records(tmp_path)) == 2


def test_input_runs_a_user_file_and_keeps_its_ids(tmp_path):
    mine = tmp_path / "mine.jsonl"
    mine.write_text('{"id": "AK2", "relators": ["xxYYY", "xyxYXY"]}\n{"id": "AK3", "relators": ["xyxYXY", "xxxYYYY"]}\n')
    run_cli(tmp_path, "--input", str(mine))
    assert [(r["id"], r["solved"]) for r in records(tmp_path, "smoke_mine")] == [("AK2", True), ("AK3", False)]


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
    assert len(records(tmp_path, "smoke_many")) == 25
    run_cli(tmp_path, "--input", str(many), "--rows", "0:3", "--set", "name=few", *SPEC)
    assert len(records(tmp_path, "few")) == 3


def test_a_bad_line_in_the_input_file_stops_the_run_before_anything_is_written(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("xxYYY, xyxYXY\nxy1\n")
    with pytest.raises(SystemExit, match=r"bad\.txt:2: "):
        run_cli(tmp_path / "out", "--input", str(bad))
    assert not (tmp_path / "out").exists()


def test_a_missing_input_file_names_the_path(tmp_path):
    with pytest.raises(FileNotFoundError, match="nowhere.csv"):
        run_cli(tmp_path / "out", "--input", str(tmp_path / "nowhere.csv"))


def test_an_empty_input_path_is_an_error_and_not_the_configs_benchmark(tmp_path):
    with pytest.raises(SystemExit, match="unknown benchmark"):
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


# ---- the default run name of your own rows: never the shipped folder of the config ----------------------------------

def write_own(tmp_path, name):
    """A file called ``name`` that holds AK2 in the format its extension says (gzipped when it ends in .gz)."""
    kind = name.lower().removesuffix(".gz").rpartition(".")[2]
    text = {"txt": AK2 + "\n", "csv": "r1,r2\nxxYYY,xyxYXY\n", "jsonl": '{"relators": ["xxYYY", "xyxYXY"]}\n'}[kind]
    raw = text.encode()
    (tmp_path / name).write_bytes(gzip.compress(raw) if name.lower().endswith(".gz") else raw)
    return str(tmp_path / name)


@pytest.mark.parametrize("file,name", [
    ("mine.txt", "smoke_mine"), ("mine.csv", "smoke_mine"), ("mine.jsonl", "smoke_mine"),
    ("mine.csv.gz", "smoke_mine"), ("mine.txt.gz", "smoke_mine"), ("MINE.TXT", "smoke_MINE"),
    ("two.v2.jsonl", "smoke_two.v2")])
def test_input_without_a_name_writes_to_the_config_name_and_the_file_stem(tmp_path, file, name):
    """The stem is the file's name without .txt, .csv, .jsonl and .gz; the run never lands in ``smoke``."""
    run_cli(tmp_path / "out", "--input", write_own(tmp_path, file), *SPEC)
    assert os.listdir(tmp_path / "out") == [name]
    assert [r["solved"] for r in records(tmp_path / "out", name)] == [True]


def test_pres_without_a_name_writes_to_the_config_name_and_pres(tmp_path):
    run_cli(tmp_path, "--pres", AK2, *SPEC)
    assert os.listdir(tmp_path) == ["smoke_pres"]


def test_the_default_name_starts_from_the_configs_own_name(tmp_path):
    named = tmp_path / "named.toml"
    named.write_text('name = "base_run"\nmethod = "greedy"\nbenchmark = "ms640"\n[search]\nbudget = 50\n')
    run_cli(tmp_path / "out", "--pres", AK2, "--set", "search.backend=spec", config=str(named))
    assert os.listdir(tmp_path / "out") == ["base_run_pres"]


@pytest.mark.parametrize("override,name", [("name=mine", "mine"), ('name="mine"', "mine"), ("name = mine", "mine"),
                                           ("name=smoke", "smoke")])
@pytest.mark.parametrize("flag", ["--pres", "--input"])
def test_an_explicit_name_wins_even_when_it_is_the_configs_own(tmp_path, flag, override, name):
    mine = AK2 if flag == "--pres" else write_own(tmp_path, "mine.txt")
    run_cli(tmp_path / "out", flag, mine, "--set", override, *SPEC)
    assert os.listdir(tmp_path / "out") == [name]


# ---- a bad row id, config or input file ends the command with one line, not a traceback ----------------------------

@pytest.mark.parametrize("config", [SMOKE, RANK3])
def test_an_unknown_row_id_exits_with_one_line_naming_the_ids(tmp_path, config):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--rows", "3,nope,nada,5", config=config)
    assert e.value.code == "rows not in the benchmark: ['nope', 'nada']"
    assert not (tmp_path / "out").exists()


def test_an_unknown_row_id_among_your_presentations_exits_the_same_way(tmp_path):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path, "--pres", AK2, "--rows", "0,1", *SPEC)
    assert e.value.code == "rows not in the benchmark: ['1']"


@pytest.mark.parametrize("args,message", [
    (("--set", "bogus=1"), "unknown config keys ['bogus']"),
    (("--set", "search.bogus=1"), "unknown SearchConfig keys ['bogus']"),
    (("--set", "search.budget=0"), "budget must be a positive int, got 0"),
    (("--set", "search.cap=0"), "cap must be an int >= 1"),
    (("--set", "method=beam"), "method 'beam' not in"),
    (("--set", "path=1"), "path must be true or false"),
    (("--set", "search"), "'search' is not key=value")])
def test_a_bad_config_exits_with_one_line_naming_the_problem(tmp_path, args, message):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", *args)
    assert message in e.value.code and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


def test_a_config_file_that_is_not_toml_exits_with_one_line(tmp_path):
    broken = tmp_path / "broken.toml"
    broken.write_text('method = "greedy"\nbenchmark = ms640\n')
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", config=str(broken))
    assert "line 2" in e.value.code and "\n" not in e.value.code


def test_an_input_file_that_is_not_utf8_exits_with_one_line_naming_the_file(tmp_path):
    latin1 = tmp_path / "latin1.txt"
    latin1.write_bytes(b"xxYYY, xyxYXY  # caf\xe9\n")
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--input", str(latin1))
    assert e.value.code.startswith(f"{latin1}: ") and "UTF-8" in e.value.code and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


def test_run_py_prints_the_message_and_no_traceback(tmp_path):
    done = subprocess.run([sys.executable, os.path.join(ROOT, "run.py"), "--config", SMOKE, "--out", str(tmp_path),
                           "--rows", "nope"], capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (1, "")
    assert "Traceback" not in done.stderr and done.stderr.splitlines()[-1] == "rows not in the benchmark: ['nope']"
