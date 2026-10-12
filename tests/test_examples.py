"""The shipped examples (``examples/presentations.{txt,csv,jsonl}``) and the template (``configs/template.toml``).

The three files hold the same eight presentations in the same order: Akbulut-Kirby AK(2) and AK(3), the first four rows
of ``ms640``, one with three generators, and row 623 of ``ms640`` (the hybrid example). A ``.txt`` row has no id, so it
is numbered by its line; ``.csv`` and ``.jsonl`` rows carry the names in ``IDS``.
"""
import contextlib
import dataclasses
import io
import json
import re
import tomllib
from functools import lru_cache
from pathlib import Path

import pytest

import run
from acx import data
from acx.core.config import SearchConfig
from acx.cov import CoVConfig
from acx.hybrid import HybridConfig
from acx.ngen import NGenConfig
from acx.ngen.sweep.config import SweepConfig
from acx.runner import load_config, method_config
from acx.runner.config import RL_KEYS, TOP_LEVEL_KEYS
from acx.runner.output import PATH_SWITCHES

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
TEMPLATE = ROOT / "configs" / "template.toml"
HYBRID = ROOT / "configs" / "hybrid.toml"
IDS = ("ak2", "ak3", "ms0", "ms1", "ms2", "ms3", "gen3", "ms623")
TXT_IDS = {name: str(position) for position, name in enumerate(IDS)}     # the ids a .txt file gives its rows
RL_DEFAULTS = {"width": 1024, "steps": 150, "alpha": 0.0, "cap": 24}     # acx.rl.solve.solve (not imported: torch)
PATH_KEYS = {key for _, key in PATH_SWITCHES}                             # set by the top-level path, never written
BLOCK_CLASSES = {"cov": CoVConfig, "ngen": NGenConfig, "hybrid": HybridConfig, "rankn": SweepConfig}
BLOCK_METHODS = (*BLOCK_CLASSES, "rl")                                    # the methods with a commented-out block


def quietly(*argv):
    """``run.main`` with its progress and summary printed to nowhere: the tests read the files it writes."""
    with contextlib.redirect_stdout(io.StringIO()):
        run.main(list(argv))


def read_records(run_dir):
    """The records of a run's ``paths.jsonl``, in the order written."""
    with open(Path(run_dir) / "paths.jsonl") as f:
        return [json.loads(line) for line in f]


def by_id(records):
    return {rec["id"]: rec for rec in records}


def read_summary(run_dir):
    with open(Path(run_dir) / "summary.json") as f:
        return json.load(f)


def row_id(ext, name):
    """The id a row of the ``ext`` file gets: its name, or its line number for a ``.txt``."""
    return TXT_IDS[name] if ext == "txt" else name


def field_defaults(cls):
    """The default of every field of a dataclass that has one."""
    return {f.name: f.default for f in dataclasses.fields(cls) if f.default is not dataclasses.MISSING}


@lru_cache(maxsize=None)
def example(ext):
    """The rows of one example file, as ``data.rows`` reads them."""
    return data.rows(EXAMPLES / f"presentations.{ext}")


def presentations_by_name():
    return {row.id: row.pres for row in example("jsonl")}


@lru_cache(maxsize=None)
def ms640():
    return data.rows("ms640")


def assigned_keys(text):
    """Every key assigned on a line of ``text``, uncommented or commented out."""
    return set(re.findall(r"^#? ?([a-z_]+) = ", text, re.MULTILINE))


def block_span(lines, first_line):
    """``(start, end)`` of the block whose first line starts with ``first_line``, up to the next blank line."""
    start = next(k for k, line in enumerate(lines) if line.startswith(first_line))
    end = start
    while end < len(lines) and lines[end].strip():
        end += 1
    return start, end


def commented_block(text, section):
    """The commented-out ``# [section]`` block of the template, uncommented and parsed as TOML."""
    lines = text.splitlines()
    start, end = block_span(lines, f"# [{section}]")
    assert all(line.startswith("# ") for line in lines[start:end]), f"every line of [{section}] is a comment"
    body = [line[2:] for line in lines[start:end]]
    return tomllib.loads("\n".join(body))[section]


def template_for(method):
    """The template as ``method`` runs it: its method line set, its block uncommented, and ``[search]`` commented out
    for the two methods that read no ``[search]``."""
    lines = TEMPLATE.read_text().replace('method = "greedy"', f'method = "{method}"', 1).splitlines()
    if method in BLOCK_METHODS:
        start, end = block_span(lines, f"# [{method}]")
        lines[start:end] = [line[2:] for line in lines[start:end]]
    if method in ("hybrid", "rl"):
        start, end = block_span(lines, "[search]")
        lines[start:end] = ["# " + line for line in lines[start:end]]
    return "\n".join(lines) + "\n"


# The example files

def test_the_three_files_hold_the_same_presentations_in_the_same_order():
    expected = [row.pres for row in example("jsonl")]
    assert len(expected) == len(IDS)
    assert [row.pres for row in example("csv")] == expected
    assert [row.pres for row in example("txt")] == expected


@pytest.mark.parametrize("ext", ["csv", "jsonl"])
def test_csv_and_jsonl_give_the_readable_ids(ext):
    assert [row.id for row in example(ext)] == list(IDS)


def test_txt_rows_are_numbered_by_their_line():
    assert [row.id for row in example("txt")] == [TXT_IDS[name] for name in IDS]


@pytest.mark.parametrize("name, n", [("ak2", 2), ("ak3", 3)])
def test_ak_examples_are_the_akbulut_kirby_presentations(name, n):
    pres = presentations_by_name()[name]
    assert pres.n_gen == 2 and sorted(pres.rels) == sorted(data.AK(n).rels)


@pytest.mark.parametrize("name, ms_row", [("ms0", 0), ("ms1", 1), ("ms2", 2), ("ms3", 3), ("ms623", 623)])
def test_ms_examples_are_rows_of_ms640(name, ms_row):
    assert presentations_by_name()[name] == ms640()[ms_row].pres


def test_the_three_generator_example_is_xy_yz_z():
    pres = presentations_by_name()["gen3"]
    assert pres.n_gen == 3 and pres.strs == ("xy", "yz", "z")


# The template config

def test_template_top_level_and_search_keys_hold_their_defaults():
    active = tomllib.loads(TEMPLATE.read_text())
    top = {key: active[key] for key in ("name", "method", "benchmark", "rows", "workers", "decode", "path")}
    assert top == {"name": "template", "method": "greedy", "benchmark": "examples/presentations.txt", "rows": "",
                   "workers": 1, "decode": True, "path": True}
    assert "fields" not in active                       # fields = [] would keep no record key but id, solved, error
    search = dict(active["search"])
    assert search.pop("backend") == "fast"              # the fast engine; the code default is "spec"
    assert set(search) == {"priority", "cap", "budget", "cyclic", "trace"}     # capture_path is set by path, not written
    defaults = field_defaults(SearchConfig)
    assert all(search[key] == defaults[key] for key in search)


def test_template_names_every_top_level_key_and_every_search_key():
    expected = TOP_LEVEL_KEYS | {f.name for f in dataclasses.fields(SearchConfig)}
    missing = expected - assigned_keys(TEMPLATE.read_text())
    assert not missing, missing


@pytest.mark.parametrize("section", sorted(BLOCK_CLASSES))
def test_each_commented_block_names_every_key_with_its_default(section):
    cls = BLOCK_CLASSES[section]
    block = commented_block(TEMPLATE.read_text(), section)
    assert set(block) == {f.name for f in dataclasses.fields(cls)} - {"search"} - PATH_KEYS
    defaults = field_defaults(cls)
    assert block == {key: defaults[key] for key in block}


def test_the_commented_rl_block_names_every_key_with_its_default():
    block = commented_block(TEMPLATE.read_text(), "rl")
    assert set(block) == RL_KEYS and block == RL_DEFAULTS


@pytest.mark.parametrize("method", ["aut", "cov", "ngen", "hybrid", "rl", "rankn"])
def test_each_method_loads_from_the_template_with_its_block_uncommented(tmp_path, method):
    path = tmp_path / f"{method}.toml"
    path.write_text(template_for(method))
    cfg = load_config(path)
    assert cfg["method"] == method
    method_config(cfg)


def test_the_fields_example_line_loads_as_a_list_of_record_keys(tmp_path):
    text = TEMPLATE.read_text()
    line = next(line for line in text.splitlines() if line.startswith("# fields"))
    path = tmp_path / "fields.toml"
    path.write_text(text.replace(line, line[2:]))
    assert load_config(path)["fields"] == ["solved", "cost", "sub_moves"]


# Runs on the examples

@pytest.fixture(scope="module")
def template_runs(tmp_path_factory):
    """The run folder of ``configs/template.toml`` on each example file, by extension."""
    runs = {}
    for ext in ("txt", "csv", "jsonl"):
        out = tmp_path_factory.mktemp(f"template_{ext}")
        quietly("--config", str(TEMPLATE), "--input", str(EXAMPLES / f"presentations.{ext}"), "--out", str(out))
        runs[ext] = out / "template"
    return runs


@pytest.fixture(scope="module")
def hybrid_run(tmp_path_factory):
    """The run folder of ``configs/hybrid.toml`` on ``presentations.jsonl``."""
    out = tmp_path_factory.mktemp("hybrid")
    quietly("--config", str(HYBRID), "--input", str(EXAMPLES / "presentations.jsonl"), "--out", str(out))
    return out / "hybrid"


@pytest.mark.parametrize("ext", ["txt", "csv", "jsonl"])
def test_template_writes_one_record_per_example(template_runs, ext):
    records = read_records(template_runs[ext])
    assert sorted(rec["id"] for rec in records) == sorted(row_id(ext, name) for name in IDS)


@pytest.mark.parametrize("ext", ["txt", "csv", "jsonl"])
def test_template_solves_ak2_and_gives_the_three_generator_row_no_error(template_runs, ext):
    records = by_id(read_records(template_runs[ext]))
    assert records[row_id(ext, "ak2")]["solved"]
    assert records[row_id(ext, "gen3")].get("error") is None
    assert read_summary(template_runs[ext])["errors"] == 0


@pytest.mark.parametrize("ext", ["txt", "csv", "jsonl"])
def test_every_solve_of_the_template_is_replay_verified(template_runs, ext):
    assert all(rec["verified"] for rec in read_records(template_runs[ext]) if rec["solved"])


def test_the_template_leaves_the_hybrid_example_unsolved(template_runs):
    assert not by_id(read_records(template_runs["jsonl"]))["ms623"]["solved"]


def test_path_false_keeps_no_path_and_greedy_keeps_no_length(tmp_path):
    """The template's ``path`` comment: without the path the greedy record has no ``sub_moves`` (the search does not
    count the length when it does not capture the path)."""
    quietly("--config", str(TEMPLATE), "--input", str(EXAMPLES / "presentations.jsonl"), "--rows", "ak2",
            "--set", "path=false", "--set", "name=nopath", "--out", str(tmp_path))
    (rec,) = read_records(tmp_path / "nopath")
    assert rec["solved"] and rec["path"] is None and rec["verified"] is False and rec["sub_moves"] is None


def test_the_hybrid_config_solves_the_hybrid_example(hybrid_run):
    records = by_id(read_records(hybrid_run))
    assert len(records) == len(IDS)
    assert records["ms623"]["solved"] and records["ms623"]["verified"]


def test_the_three_generator_row_is_an_error_for_the_methods_that_cannot_take_it(tmp_path):
    jsonl = str(EXAMPLES / "presentations.jsonl")
    quietly("--config", str(TEMPLATE), "--input", jsonl, "--rows", "gen3", "--set", "search.priority=s20_mk2",
            "--set", "name=s20", "--out", str(tmp_path))
    quietly("--config", str(HYBRID), "--input", jsonl, "--rows", "gen3", "--set", "name=hybrid", "--out", str(tmp_path))
    (s20,) = read_records(tmp_path / "s20")
    (hybrid,) = read_records(tmp_path / "hybrid")
    assert not s20["solved"] and "two generators" in s20["error"]
    assert not hybrid["solved"] and "two-generator" in hybrid["error"]
