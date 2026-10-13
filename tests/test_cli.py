"""run.py on your own presentations: ``--pres`` (one presentation per flag) and ``--input`` (a file, see acx/data.py),
and how it ends on a bad config, row id or file."""
import gzip
import json
import os
import shutil
import re
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import ROOT

import run
from acx.runner import load_config

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


def test_other_presentations_into_records_without_config_json_leave_input_txt_alone(tmp_path):
    """The refusal comes before ``input.txt`` is rewritten, so the folder still names the presentations of its
    records."""
    run_cli(tmp_path, "--pres", AK2, *SPEC, "--set", "search.budget=50")
    (tmp_path / "smoke_pres" / "config.json").unlink()
    with pytest.raises(SystemExit, match="other presentations"):
        run_cli(tmp_path, "--pres", AK3, *SPEC, "--set", "search.budget=50")
    assert (tmp_path / "smoke_pres" / "input.txt").read_text() == AK2 + "\n"


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


def test_rows_help_names_every_form_select_takes(capsys):
    with pytest.raises(SystemExit):
        run.main(["--help"])
    text = " ".join(capsys.readouterr().out.split())                 # undo argparse's line wrapping
    assert all(form in text for form in ('"a:b"', '"a:b:c"', '"3,17"', '"ms:1"'))


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


# ---- decode later: --solved-from runs only the rows another run solved ---------------------------------------------

def write_run(run_dir, solved_by_id):
    """A run folder whose ``paths.jsonl`` holds one record per ``id: solved`` (the fields --solved-from reads)."""
    run_dir.mkdir(parents=True)
    lines = [json.dumps({"id": row_id, "solved": solved}) + "\n" for row_id, solved in solved_by_id.items()]
    (run_dir / "paths.jsonl").write_text("".join(lines))
    return str(run_dir)


def test_solved_ids_are_the_ids_marked_solved_in_file_order(tmp_path):
    fast = write_run(tmp_path / "fast", {"7": True, "2": False, "ms:1": True, "0": True})
    assert run.solved_ids(fast) == ["7", "ms:1", "0"]


def test_solved_from_reads_a_run_that_was_cut_off(tmp_path):
    """A run stopped mid-write leaves half a record last; the runner's resume drops it, and so does --solved-from."""
    (tmp_path / "paths.jsonl").write_text('{"id": "0", "solved": true}\n{"id": "1", "solved": false}\n{"id": "2", "so')
    assert run.solved_ids(tmp_path) == ["0"]


def test_solved_from_runs_exactly_the_solved_rows(tmp_path):
    fast = write_run(tmp_path / "fast", {"7": True, "2": False, "0": True, "5": True, "9": False})
    run_cli(tmp_path, "--solved-from", fast, "--set", "name=later", *SPEC, "--set", "search.budget=50")
    assert [r["id"] for r in records(tmp_path, "later")] == ["7", "0", "5"]


def test_solved_from_replaces_the_configs_own_rows(tmp_path):
    fast = write_run(tmp_path / "fast", {"25": True})                       # smoke.toml says rows = "0:20"
    run_cli(tmp_path, "--solved-from", fast, "--set", "name=later", *SPEC, "--set", "search.budget=50")
    assert [r["id"] for r in records(tmp_path, "later")] == ["25"]


def test_solved_from_works_on_your_own_file(tmp_path):
    mine = tmp_path / "mine.jsonl"
    mine.write_text('{"id": "AK2", "relators": ["xxYYY", "xyxYXY"]}\n{"id": "AK3", "relators": ["xyxYXY", "xxxYYYY"]}\n')
    options = ("--input", str(mine), *SPEC, "--set", "search.budget=50")
    run_cli(tmp_path, *options, "--set", "path=false")                     # smoke_mine: AK2 solved, AK3 not
    run_cli(tmp_path, *options, "--solved-from", str(tmp_path / "smoke_mine"), "--set", "name=later")
    assert [(r["id"], r["verified"]) for r in records(tmp_path, "later")] == [("AK2", True)]


def test_solved_from_a_folder_without_paths_jsonl_exits_with_one_line(tmp_path):
    shipped = tmp_path / "ms640_hybrid"                                     # what git ships: no paths.jsonl
    shipped.mkdir()
    shutil.copy(os.path.join(ROOT, "results", "ms640_hybrid", "summary.json"), shipped)
    for folder in (str(shipped), str(tmp_path / "nowhere")):
        with pytest.raises(SystemExit) as e:
            run_cli(tmp_path / "out", "--solved-from", folder)
        assert e.value.code.startswith(os.path.join(folder, "paths.jsonl") + ": ") and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


def test_solved_from_a_run_that_solved_nothing_exits_with_one_line(tmp_path):
    fast = write_run(tmp_path / "fast", {"0": False, "1": False})
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--solved-from", fast)
    assert e.value.code == f"{os.path.join(fast, 'paths.jsonl')}: no solved rows"
    assert not (tmp_path / "out").exists()


def test_solved_from_and_rows_cannot_be_combined(tmp_path, capsys):
    fast = write_run(tmp_path / "fast", {"0": True})
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--solved-from", fast, "--rows", "0:3")
    assert e.value.code == 2 and "not allowed with" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("config,rows,options", [
    (SMOKE, "0:20", ("--set", "search.budget=5")),                          # greedy: some of the 20 rows unsolved
    (HYBRID, "0:6", ())])                                                   # hybrid: units, aut-assisted paths
def test_a_fast_run_then_a_decode_run_of_its_solved_rows(tmp_path, config, rows, options):
    """``path = false`` first, then ``path = true`` on its solved rows: the same solves, now each with a replayed path."""
    run_cli(tmp_path, "--rows", rows, *options, "--set", "path=false", "--set", "name=fast", config=config)
    run_cli(tmp_path, "--solved-from", str(tmp_path / "fast"), *options, "--set", "path=true", "--set", "name=paths",
            config=config)
    fast, paths = records(tmp_path, "fast"), records(tmp_path, "paths")
    solved = [r for r in fast if r["solved"]]
    assert 0 < len(solved) and (config == HYBRID or len(solved) < len(fast))
    assert [(r["id"], r["cost"], r["sub_moves"], r["kind"]) for r in solved] == \
        [(r["id"], r["cost"], r["sub_moves"], r["kind"]) for r in paths]
    assert all(r["verified"] and r["elem_moves"] for r in paths)
    assert not any(r["verified"] or r["path"] or r["elementary"] for r in fast)


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
    (("--set", "search"), "'search' is not key=value"),
    (("--set", "search.cyclic=False"), "cyclic must be true or false, got 'False'"),
    (("--set", "name.x=1"), "name.x: name is not a section")])
def test_a_bad_config_exits_with_one_line_naming_the_problem(tmp_path, args, message):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", *args)
    assert message in e.value.code and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


def test_set_cyclic_False_is_refused_at_load():
    """``--set search.cyclic=False`` (Python spelling) is the string 'False', which ran cyclic=True."""
    with pytest.raises(ValueError):
        load_config(SMOKE, ["search.cyclic=False"])


@pytest.mark.parametrize("item, message", [
    ("name=2026-10-13", "name must be a string"),                 # a TOML date
    ("name=123", "name must be a string"),
    ("name=true", "name must be a string"),
    ("benchmark=640", "benchmark must be a string"),
    ("search=5", "search is a section"),
    ("search=[1]", "search is a section")])
def test_a_wrongly_typed_top_level_value_is_a_valueerror_at_load(item, message):
    with pytest.raises(ValueError, match=f"^{message}"):
        load_config(SMOKE, [item])


@pytest.mark.parametrize("items, message", [
    (["name.x=1"], "name.x: name is not a section"),
    (["search=5", "search.budget=1"], "search.budget: search is not a section"),
    (["search.budget.x=1"], "search.budget.x: budget is not a section")])
def test_a_dotted_key_through_a_value_is_a_valueerror(items, message):
    with pytest.raises(ValueError) as error:
        load_config(SMOKE, items)
    assert str(error.value) == message


def test_run_py_exits_with_one_line_for_a_date_name(tmp_path):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--rows", "0:1", "--set", "name=2026-10-13")
    assert e.value.code.startswith("name must be a string") and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("method, override", [("rankn", "rankn.inverse=False"), ("greedy", "search.cyclic=False")])
def test_a_boolean_option_spelled_the_python_way_is_an_error_not_true(tmp_path, method, override):
    path = tmp_path / f"{method}.toml"
    path.write_text(f'method = "{method}"\nbenchmark = "bench60"\n')
    with pytest.raises(ValueError, match="true or false"):
        load_config(str(path), [override])


@pytest.mark.parametrize("slice_text", ["0:5:0", "::0"])
def test_a_rows_slice_with_step_zero_exits_with_one_line_naming_it(tmp_path, slice_text):
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--rows", slice_text)
    assert e.value.code.startswith(f"bad rows slice {slice_text!r}") and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("spec", ["x:3", "1:y", "1:2:3:4", "0:1.5"])
def test_rows_that_are_not_integers_around_colons_are_ids(tmp_path, spec):
    """Only integers around colons make a slice, so ids such as ``ms:1`` can be picked; these name no row."""
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--rows", spec)
    assert e.value.code == f"rows not in the benchmark: [{spec!r}]"
    assert not (tmp_path / "out").exists()


def test_rows_ids_may_have_spaces_after_the_commas(tmp_path):
    run_cli(tmp_path, "--rows", "0, 2", *SPEC, "--set", "search.budget=50")
    assert [r["id"] for r in records(tmp_path)] == ["0", "2"]


def test_a_missing_config_or_input_file_exits_with_one_line_naming_it(tmp_path):
    missing = str(tmp_path / "nowhere.toml")
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", config=missing)
    assert e.value.code == f"{missing}: no such file"
    missing = str(tmp_path / "nowhere.txt")
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--input", missing)
    assert e.value.code == f"{missing}: no such file"
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


def test_an_input_file_that_is_not_gzip_exits_with_one_line_naming_the_file(tmp_path):
    fake = tmp_path / "fake.txt.gz"
    fake.write_text(AK2 + "\n")                                    # plain text under a .gz name
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--input", str(fake))
    assert e.value.code.startswith(f"{fake}: ") and "gzip" in e.value.code and "\n" not in e.value.code
    assert not (tmp_path / "out").exists()


def test_an_input_path_that_cannot_be_read_exits_with_one_line_naming_it(tmp_path):
    folder = tmp_path / "folder.txt"                               # a directory where a file was expected
    folder.mkdir()
    with pytest.raises(SystemExit) as e:
        run_cli(tmp_path / "out", "--input", str(folder))
    assert e.value.code.startswith(f"{folder}: ") and "\n" not in e.value.code


def test_the_same_input_file_spelled_another_way_resumes_the_run(tmp_path, monkeypatch):
    """``./mine.txt`` and ``mine.txt`` are one file: the second run resumes instead of being refused."""
    (tmp_path / "mine.txt").write_text(AK2 + "\n")
    monkeypatch.chdir(tmp_path)
    for spelling in ("mine.txt", "./mine.txt", "sub/../mine.txt"):
        run.main(["--config", SMOKE, "--input", spelling, *SPEC])
    assert [r["solved"] for r in records(tmp_path / "results", "smoke_mine")] == [True]
    assert json.loads((tmp_path / "results" / "smoke_mine" / "config.json").read_text())["benchmark"] == "mine.txt"


def test_the_template_examples_of_rows_name_rows_of_its_benchmark():
    """``configs/template.toml`` shows a slice and ids; both pick rows of the template's own benchmark."""
    from acx import data
    from acx.runner import load_config, select
    template = os.path.join(ROOT, "configs", "template.toml")
    slice_text, ids = re.search(r'a slice "([^"]+)" or ids "([^"]+)"', Path(template).read_text()).groups()
    rows = data.rows(load_config(template)["benchmark"])
    assert len(select(rows, slice_text)) == 3 and [r.id for r in select(rows, ids)] == ids.replace(" ", "").split(",")


def test_run_py_prints_the_message_and_no_traceback(tmp_path):
    done = subprocess.run([sys.executable, os.path.join(ROOT, "run.py"), "--config", SMOKE, "--out", str(tmp_path),
                           "--rows", "nope"], capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (1, "")
    assert "Traceback" not in done.stderr and done.stderr.splitlines()[-1] == "rows not in the benchmark: ['nope']"
    done = subprocess.run([sys.executable, os.path.join(ROOT, "run.py"), "--config", str(tmp_path / "no.toml")],
                          capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (1, "")
    assert "Traceback" not in done.stderr and done.stderr.splitlines()[-1] == f"{tmp_path / 'no.toml'}: no such file"
