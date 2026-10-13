"""compare.py / acx.report: the comparison table, --common, head-to-head and loading, on hand-made result folders."""
import itertools
import json
import math
import os
import re
import shutil
from typing import NamedTuple
from xml.etree import ElementTree

import pytest
from conftest import ROOT

import compare
from acx import report, runner
from acx.core import capcount


def rec(id, solved, cost, seconds, **extra):
    """One paths.jsonl record with the fields the report reads."""
    return {"id": id, "solved": solved, "kind": "ac_path" if solved else None, "cost": cost, "seconds": seconds,
            **extra}


# Run A, an older run (no cpu_seconds, no cost_unit): two rows solved, one burned its budget, one |det| error.
A_ROWS = [rec("0", True, 10, 1.0, sub_moves=2, elem_moves=9),
          rec("1", True, 30, 3.0, sub_moves=4, elem_moves=21),
          rec("2", False, 100, 10.0),
          rec("3", False, 0, 0.0, error="|det| = 2")]
# Run B, a hybrid run with cpu_seconds (``seconds`` is wall time and must be ignored): row 1 is bound by a cap,
# row 2 has no elementary path.
B_ROWS = [rec("0", True, 5, 9.9, cpu_seconds=0.5, sub_moves=3, elem_moves=12),
          rec("1", False, 50, 9.9, cpu_seconds=2.5, cap_would_pop=2, dyn_cap_would_pop=0),
          rec("2", True, 15, 9.9, cpu_seconds=1.0, sub_moves=5, elem_moves=None),
          rec("3", False, 0, 9.9, cpu_seconds=0.0, error="|det| = 2")]


def write_run(root, name, rows, method="greedy", benchmark="bench4", **summary):
    """A results folder as run.py leaves it (``paths.jsonl`` and ``summary.json``); returns its path."""
    folder = root / name
    folder.mkdir()
    (folder / "paths.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
    summary = {"name": name, "method": method, "benchmark": benchmark, **summary}
    (folder / "summary.json").write_text(json.dumps(summary))
    return str(folder)


@pytest.fixture
def folders(tmp_path):
    """Run A and run B on one benchmark."""
    return write_run(tmp_path, "A", A_ROWS), write_run(tmp_path, "B", B_ROWS, "hybrid", cost_unit="units")


def load(*paths):
    return [report.load_run(p) for p in paths]


def page(*paths, **options):
    return report.html_page(load(*paths), **options)


class Drawn(NamedTuple):
    """A bar as its SVG draws it: visible name and label, where it ends, its color class and its tooltip."""
    name: str
    label: str
    tip: float
    color: str
    tooltip: str


class Panel(NamedTuple):
    """One SVG chart as plain data: height, lowest text, x of its axis and of its gridlines, tick labels, bars."""
    height: float
    lowest: float
    axes: list
    grid: list
    ticks: list
    bars: list


def line_xs(root, kind):
    """The x of the lines of one class ("axis" or "grid") in an SVG."""
    return [float(line.get("x1")) for line in root.iter("line") if line.get("class") == kind]


def panels(html, chart):
    """The panels of one chart of a page (0 solve rate, 1 mean cost, 2 CPU per pop/unit), read back from its SVG."""
    figure = re.findall(r"<figure>.*?</figure>", html, re.S)[chart]
    found = []
    for svg in re.findall(r"<svg.*?</svg>", figure, re.S):
        root = ElementTree.fromstring(svg)                                   # raises on a broken tag or attribute
        bars = []
        for group in root.iter("g"):
            name, label = group.findall("text")
            bars.append(Drawn(name.text, label.text, float(label.get("x")) - report.GAP, group.get("class"),
                              group.find("title").text))
        found.append(Panel(float(root.get("viewBox").split()[3]), max(float(t.get("y")) for t in root.iter("text")),
                           line_xs(root, "axis"), line_xs(root, "grid"), [t.text for t in root.findall("text")], bars))
    return found


MEAN, MEDIAN = "mean cost (solved)", "median cost (solved)"     # the cost columns average the solved rows only


def table(text):
    """The markdown table in ``text`` as one {header: cell} dict per run."""
    lines = [line for line in text.splitlines() if line.startswith("|")]
    cells = lambda line: [cell.strip() for cell in line.strip("|").split("|")]  # noqa: E731
    return [dict(zip(cells(lines[0]), cells(line), strict=True)) for line in lines[2:]]


def test_table_of_an_older_run_falls_back_to_seconds_and_the_method_unit(folders):
    text = report.markdown(load(folders[0]))
    (row,) = table(text)
    assert row == {
        "run": "A", "method": "greedy", "benchmark": "bench4", "rows": "4", "solved": "2 (50.0%)",
        MEAN: "20.0 pops", MEDIAN: "20.0 pops", "mean sub_moves": "3.0", "mean elem_moves": "15.0",
        "CPU s/row": "3.500*", "CPU µs per pop/unit": "100,000.0/pop*", "raise-cap rows": "0", "errors": "1"}
    assert text.splitlines()[1] == "| " + " | ".join(["---"] * 3 + ["---:"] * 10) + " |"   # names left, numbers right


def test_cpu_seconds_and_cost_unit_are_used_when_present(folders):
    (row,) = table(report.markdown(load(folders[1])))
    assert row == {
        "run": "B", "method": "hybrid", "benchmark": "bench4", "rows": "4", "solved": "2 (50.0%)",
        MEAN: "10.0 units", MEDIAN: "10.0 units", "mean sub_moves": "4.0",
        "mean elem_moves": "12.0 (n=1)", "CPU s/row": "1.000", "CPU µs per pop/unit": "57,142.9/unit",
        "raise-cap rows": "1", "errors": "1"}


@pytest.mark.parametrize("method,unit", [("greedy", "pops"), ("aut", "pops"), ("cov", "pops"), ("ngen", "pops"),
                                         ("rankn", "pops"), ("hybrid", "units"), ("rl", "evaluations")])
def test_the_unit_is_inferred_from_the_method(tmp_path, method, unit):
    assert report.load_run(write_run(tmp_path, "r", A_ROWS, method)).unit == unit


def test_a_summary_cost_unit_wins_over_the_method(tmp_path):
    assert report.load_run(write_run(tmp_path, "r", A_ROWS, cost_unit="evaluations")).unit == "evaluations"


def test_the_unit_names_the_cost_and_the_rate(tmp_path):
    folder = write_run(tmp_path, "r", A_ROWS, "rl")
    (row,) = table(report.markdown(load(folder)))
    assert (row[MEAN], row["CPU µs per pop/unit"]) == ("20.0 evaluations", "100,000.0/evaluation*")
    assert [bar.label for bar in panels(page(folder), 2)[0].bars] == ["100K µs/evaluation"]


def test_raise_cap_rows_count_a_row_once_whichever_counter_bound(tmp_path):
    rows = [rec("0", True, 5, 1.0, cap_would_pop=1, dyn_cap_would_pop=3),         # two counters bound: one row
            rec("1", True, 5, 1.0, slack_would_pop=1),
            rec("2", True, 5, 1.0, cap_would_pop=0, cap_dropped=7)]               # dropped, but nothing would pop
    (row,) = table(report.markdown(load(write_run(tmp_path, "r", rows))))
    assert row["raise-cap rows"] == "2"


def test_notes_appear_only_when_they_apply(folders):
    only_a, only_b, both = (report.markdown(load(*paths)) for paths in (folders[:1], folders[1:], folders))
    assert "Starred (*) CPU values are wall-clock seconds" in only_a            # A has no cpu_seconds
    assert "raise-cap rows:" not in only_a and "Units differ" not in only_a
    assert "Starred" not in only_b
    assert "raise-cap rows: rows where a relator cap dropped a state the search would have popped" in only_b
    assert all(note in both for note in ("Starred (*)", "raise-cap rows:", "a hybrid unit also counts"))


def test_head_to_head_of_two_runs_on_one_benchmark(folders):
    lines = report.markdown(load(*folders)).splitlines()
    assert ("- Head to head on bench4 (4 rows in common): solved by A only 1, by B only 1, by both 1, by neither 1."
            in lines)


def test_head_to_head_counts_only_the_rows_both_runs_ran(tmp_path, folders):
    short = write_run(tmp_path, "short", A_ROWS[:2])                               # ran rows 0 and 1 only
    lines = report.markdown(load(folders[1], short)).splitlines()
    assert ("- Head to head on bench4 (2 rows in common): solved by B only 0, by short only 1, by both 1, "
            "by neither 0." in lines)


def test_no_head_to_head_for_three_runs_or_two_benchmarks(tmp_path, folders):
    elsewhere = write_run(tmp_path, "C", A_ROWS, benchmark="elsewhere")
    third = write_run(tmp_path, "D", A_ROWS)
    assert "Head to head" not in report.markdown(load(*folders, third))
    assert "Head to head" not in report.markdown(load(folders[0], elsewhere))


COMMON_NOTE = "- --common: cost, move and CPU columns cover only the 1 row every run solved."


def test_common_restricts_the_means_to_the_rows_every_run_solved(folders):
    text = report.markdown(load(*folders), common=True)
    a, b = table(text)                                                            # only row "0" is solved by both
    assert (a[MEAN], a["mean sub_moves"], a["mean elem_moves"], a["CPU s/row"], a["CPU µs per pop/unit"]) == (
        "10.0 pops", "2.0", "9.0", "1.000*", "100,000.0/pop*")
    assert (b[MEAN], b["mean sub_moves"], b["mean elem_moves"], b["CPU s/row"], b["CPU µs per pop/unit"]) == (
        "5.0 units", "3.0", "12.0", "0.500", "100,000.0/unit")
    assert (a["rows"], a["solved"], a["errors"], b["raise-cap rows"]) == ("4", "2 (50.0%)", "1", "1")  # whole run
    assert COMMON_NOTE in text.splitlines()


def test_common_is_the_intersection_over_every_run(tmp_path, folders):
    only_row_1 = write_run(tmp_path, "C", [rec("1", True, 7, 1.0), rec("0", False, 9, 1.0)])
    cells = table(report.markdown(load(*folders, only_row_1), common=True))
    assert [c[MEAN] for c in cells] == ["-", "-", "-"]                              # no row is solved by all three


def test_common_needs_one_benchmark(tmp_path, folders):
    elsewhere = write_run(tmp_path, "C", A_ROWS, benchmark="elsewhere")
    with pytest.raises(SystemExit, match="one benchmark"):
        report.markdown(load(folders[0], elsewhere), common=True)


@pytest.mark.parametrize("part,whole,value", [(1, 3, 33.3), (2, 3, 66.7), (0, 5, 0), (5, 5, 100),
                                              (71281, 71283, 99.9), (1, 2500, 0.1)])
def test_a_percentage_is_never_rounded_to_all_or_none(part, whole, value):
    assert report.percent(part, whole) == value


def test_a_run_that_missed_one_row_in_two_thousand_does_not_read_100_percent(tmp_path):
    folder = write_run(tmp_path, "r", [rec(str(i), i > 0, 1, 0.1) for i in range(2000)])
    assert table(report.markdown(load(folder)))[0]["solved"] == "1999 (99.9%)"
    assert panels(page(folder), 0)[0].bars[0].label == "99.9%"


def test_a_run_with_no_rows_or_no_solves_shows_dashes(tmp_path):
    empty = write_run(tmp_path, "empty", [])
    unsolved = write_run(tmp_path, "unsolved", [rec("0", False, 100, 1.0)])
    e, u = table(report.markdown(load(empty, unsolved)))
    assert (e["rows"], e["solved"], e[MEAN], e["CPU s/row"], e["CPU µs per pop/unit"]) == ("0", "0 (-)", "-", "-", "-")
    assert (u["solved"], u[MEAN], u[MEDIAN], u["mean sub_moves"], u["CPU µs per pop/unit"]) == (
        "0 (0.0%)", "-", "-", "-", "10,000.0/pop*")


def test_a_run_without_cost_or_timing_fields_still_tabulates(tmp_path):
    """``fields`` in a config may drop everything but ``id`` and ``solved``; a rate needs both a cost and a time."""
    bare = write_run(tmp_path, "bare", [{"id": "0", "solved": True}])
    cost_only = write_run(tmp_path, "cost_only", [{"id": "0", "solved": True, "cost": 7}])
    time_only = write_run(tmp_path, "time_only", [{"id": "0", "solved": True, "seconds": 2.0}])
    text = report.markdown(load(bare, cost_only, time_only))
    assert [(r["solved"], r[MEAN], r["CPU s/row"], r["CPU µs per pop/unit"]) for r in table(text)] == [
        ("1 (100.0%)", "-", "-", "-"), ("1 (100.0%)", "7.0 pops", "-", "-"), ("1 (100.0%)", "-", "2.000*", "-")]
    assert "Starred" in text and "Starred" not in report.markdown(load(bare))     # nothing to star without a time


def test_zero_is_a_value_not_a_missing_value(tmp_path):
    rows = [rec("0", True, 0, 0.0, sub_moves=0, elem_moves=0), rec("1", True, 10, 0.0, sub_moves=2, elem_moves=4)]
    folder = write_run(tmp_path, "r", rows)
    (row,) = table(report.markdown(load(folder)))
    assert (row[MEAN], row["mean sub_moves"], row["mean elem_moves"], row["CPU s/row"],
            row["CPU µs per pop/unit"]) == ("5.0 pops", "1.0", "2.0", "0.000*", "0.0/pop*")
    assert panels(page(folder), 2)[0].bars[0].label == "0 µs/pop"                 # an empty bar, not an error
    free = write_run(tmp_path, "free", [rec("0", True, 0, 0.0, sub_moves=0, elem_moves=0)])
    assert table(report.markdown(load(free)))[0][MEAN] == "0.0 pops"
    assert panels(page(free), 1)[0].bars[0].label == "no data"                    # a log axis has no zero


def test_a_mean_over_no_rows_is_a_dash_not_a_count(tmp_path):
    """A CoV stable certificate is solved but has no elementary path, so it adds nothing to ``mean elem_moves``."""
    certificate = rec("0", True, 3, 1.0, sub_moves=1, elem_moves=None)
    (row,) = table(report.markdown(load(write_run(tmp_path, "r", [certificate]))))
    assert (row["mean sub_moves"], row["mean elem_moves"]) == ("1.0", "-")


def test_rows_with_and_without_cpu_seconds_each_use_what_they_have(tmp_path):
    """A run resumed by an older version: the wall-clock rows are starred, the CPU rows keep their own time."""
    rows = [rec("0", True, 10, 9.0, cpu_seconds=1.0), rec("1", True, 10, 3.0)]
    (row,) = table(report.markdown(load(write_run(tmp_path, "r", rows, "hybrid"))))
    assert row["CPU s/row"] == "2.000*"                           # (1.0 + 3.0) / 2: the 9.0 wall seconds are ignored


def test_loading_falls_back_to_config_json_then_to_question_marks(tmp_path, monkeypatch):
    live = tmp_path / "live"                                   # a run still going: paths.jsonl, no summary.json yet
    live.mkdir()
    first, second = (json.dumps(rec(id, True, 3, 0.1)) for id in "01")
    (live / "paths.jsonl").write_text(f"{first}\n\n{second}\n")                      # blank lines are ignored
    run = report.load_run(live)
    assert (run.name, run.method, run.benchmark, run.unit, len(run.records)) == ("live", "?", "?", "pops", 2)
    (live / "config.json").write_text(json.dumps({"method": "hybrid", "benchmark": "ladder60"}))
    run = report.load_run(str(live) + "/")                     # a trailing slash still names the folder
    assert (run.name, run.method, run.benchmark, run.unit) == ("live", "hybrid", "ladder60", "units")
    (live / "summary.json").write_text(json.dumps({"method": "rl", "benchmark": "ms640"}))      # the summary wins
    monkeypatch.chdir(live)
    run = report.load_run(".")                                 # "." is named by the folder it stands for
    assert (run.name, run.method, run.benchmark, run.unit) == ("live", "rl", "ms640", "evaluations")


def test_a_folder_with_neither_paths_jsonl_nor_a_run_summary_is_refused(tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(SystemExit, match="^empty has no paths.jsonl and no summary.json of run.py to compare$"):
        report.load_run(tmp_path / "empty")
    sweep = tmp_path / "rank3_bf"                                   # the rank-n sweep writes a summary of its own
    sweep.mkdir()
    (sweep / "summary.json").write_text(json.dumps({"rows": 40, "searches": 7}))
    with pytest.raises(SystemExit, match="^rank3_bf has no paths.jsonl and no summary.json of run.py to compare$"):
        report.load_run(sweep)
    with pytest.raises(SystemExit, match="nowhere: not a folder$"):
        report.load_run(tmp_path / "nowhere")


SHIPPED_NAMES = ("bench60_hybrid", "bench60_length", "ms640_cov")


@pytest.fixture
def shipped(tmp_path):
    """The tracked files of three shipped runs (summary.json, config.json), copied without any local paths.jsonl."""
    folders = []
    for name in SHIPPED_NAMES:
        (tmp_path / name).mkdir()
        for file in ("summary.json", "config.json"):
            shutil.copy(os.path.join(ROOT, "results", name, file), tmp_path / name / file)
        folders.append(str(tmp_path / name))
    return folders


def test_compare_py_tabulates_the_shipped_summary_only_folders(capsys, shipped):
    """The folders kept in results/ hold summary.json and config.json only: their table row comes from the summary,
    with a dash for the median and the CPU columns, which it lacks."""
    compare.main(shipped)
    hybrid, length, cov = table(capsys.readouterr().out)
    assert hybrid == {
        "run": "bench60_hybrid", "method": "hybrid", "benchmark": "bench60", "rows": "60", "solved": "60 (100.0%)",
        MEAN: "79.7 units", MEDIAN: "-", "mean sub_moves": "56.4", "mean elem_moves": "460.7", "CPU s/row": "-",
        "CPU µs per pop/unit": "-", "raise-cap rows": "0", "errors": "0"}
    assert (length["rows"], length["solved"], length[MEDIAN], length["CPU s/row"]) == ("60", "40 (66.7%)", "-", "-")
    assert (cov["mean sub_moves"], cov["mean elem_moves"]) == ("14.3", "99.2 (n=554)")       # 30 CoV certificates


def test_a_summary_only_run_reads_like_its_paths_jsonl(tmp_path):
    """The same run with and without paths.jsonl: equal numbers, but for the median (none in a summary)."""
    overrides = ['rows="7,500,620,639"', "search.cap=16", "search.budget=300", "search.backend=fast", "name=real"]
    config = runner.load_config(os.path.join(ROOT, "configs", "baseline_spec.toml"), overrides)
    runner.run(config, str(tmp_path), log=lambda *a: None)
    full = report.measure(report.load_run(tmp_path / "real"))
    os.remove(tmp_path / "real" / "paths.jsonl")
    only = report.measure(report.load_run(tmp_path / "real"))
    assert only.pop("median") is None and full.pop("median") is not None
    for key in ("cost", "sub", "elem", "us"):
        assert only.pop(key) == pytest.approx(full.pop(key), rel=1e-3)
    assert only.pop("cpu_row") == pytest.approx(full.pop("cpu_row"), abs=1e-3)
    assert only == full and full["raise_rows"] == 2


def binding_records(first, count, prefix="cap", would_pop=1):
    """``count`` records from id ``first`` on; the counter ``prefix`` dropped a child in each and ``would_pop`` of them
    would have been popped."""
    key = capcount.fields(prefix)
    return [{"id": str(i), key.cap: 24, key.dropped: 1, key.min_total: 30, key.would_pop: would_pop,
             key.first_bind: 2, key.needed: 25} for i in range(first, first + count)]


def summary_with_caps(**blocks):
    """A summary.json holding only what ``measure_summary`` reads, with one ``caps`` block per counter name."""
    return {"rows": 400, "solved": 0, "errors": 0, "cost": {"on_solved": 0}, "path_length": {}, "caps": blocks}


def test_summary_only_raise_rows_is_the_counted_rows_not_the_kept_ids():
    """ac19_hybrid's summary counts 344 rows that would pop but keeps only 100 ids of them."""
    with open(os.path.join(ROOT, "results", "ac19_hybrid", "summary.json")) as f:
        summary = json.load(f)
    assert summary["caps"]["dyn_cap"]["rows_would_pop"] == 344
    assert report.measure_summary(summary)["raise_rows"] == 344


def test_summary_only_raise_rows_with_one_counter_past_keep():
    block = capcount.summarize(binding_records(0, 150), "cap")
    assert len(block["raise_ids"]) == 100 and block["rows_would_pop"] == 150
    assert report.measure_summary(summary_with_caps(cap=block))["raise_rows"] == 150


def test_summary_only_raise_rows_with_no_binding_counter_is_zero():
    quiet = capcount.summarize(binding_records(0, 3, would_pop=0), "cap")
    assert report.measure_summary(summary_with_caps(cap=quiet))["raise_rows"] == 0
    assert report.measure_summary(summary_with_caps())["raise_rows"] == 0


def test_summary_only_raise_rows_counts_a_row_once_when_two_counters_bind_on_it():
    first = capcount.summarize(binding_records(0, 5), "cap")
    second = capcount.summarize(binding_records(3, 5, "dyn_cap"), "dyn_cap")              # rows 3 and 4 bind on both
    assert report.measure_summary(summary_with_caps(cap=first, dyn_cap=second))["raise_rows"] == 8


def test_summary_only_raise_rows_of_two_cut_lists_is_a_lower_bound():
    """Two counters cut at 100 ids each (150 and 120 binding rows, 270 in all): the union is unknowable, so the count is
    the larger of the pooled kept ids (200) and the biggest counter (150)."""
    first = capcount.summarize(binding_records(0, 150), "cap")
    second = capcount.summarize(binding_records(150, 120, "dyn_cap"), "dyn_cap")
    assert report.measure_summary(summary_with_caps(cap=first, dyn_cap=second))["raise_rows"] == 200


def test_summary_only_raise_rows_of_two_cut_lists_never_falls_below_the_biggest_counter():
    first = capcount.summarize(binding_records(0, 300), "cap")                 # 300 rows, 100 kept
    second = capcount.summarize(binding_records(0, 120, "dyn_cap"), "dyn_cap")   # 120 rows, the same 100 kept
    assert report.measure_summary(summary_with_caps(cap=first, dyn_cap=second))["raise_rows"] == 300


def test_common_and_head_to_head_need_paths_jsonl(capsys, shipped):
    with pytest.raises(SystemExit, match="^--common needs paths.jsonl: bench60_hybrid has only summary.json$"):
        compare.main([shipped[0], shipped[1], "--common"])
    compare.main(shipped[:2])
    printed = capsys.readouterr().out
    assert "Head to head" not in printed and "from summary.json" in printed


def test_loading_keeps_only_the_fields_the_report_reads(tmp_path):
    """The move lists are most of a big paths.jsonl (167 MB for the AC19 hybrid run), so they are not kept."""
    row = rec("0", True, 5, 1.0, sub_moves=2, elem_moves=9, cpu_seconds=0.5, cap_would_pop=1, path=[1, 2, 3],
              elementary=[[1, 0]] * 9, image="x")
    (kept,) = report.load_run(write_run(tmp_path, "r", [row])).records
    assert set(kept) == {"id", "solved", "cost", "seconds", "sub_moves", "elem_moves", "cpu_seconds", "cap_would_pop"}


def test_a_half_written_last_line_is_skipped_but_a_corrupt_middle_line_is_not(tmp_path):
    folder = write_run(tmp_path, "r", A_ROWS)
    lines = (tmp_path / "r" / "paths.jsonl").read_text().splitlines()
    (tmp_path / "r" / "paths.jsonl").write_text("\n".join(lines) + '\n{"id": "4", "sol')   # cut off mid-write
    assert len(report.load_run(folder).records) == 4
    (tmp_path / "r" / "paths.jsonl").write_text("\n".join([lines[0], "garbage", lines[1]]) + "\n")
    with pytest.raises(SystemExit, match="paths.jsonl: line 2 is not JSON$"):
        report.load_run(folder)


def test_a_pipe_in_a_name_does_not_break_the_table(tmp_path):
    (row,) = table(report.markdown(load(write_run(tmp_path, "a|b", A_ROWS))).replace("\\|", "/"))
    assert row["run"] == "a/b" and row["rows"] == "4"


# ---- the HTML page -------------------------------------------------------------------------------------------

EXTERNAL = re.compile(r"https?:|//|<script|<link|<img|<iframe|@import|@font-face|\bsrc=|\bhref=|url\(")
BLOCKS = {"main", "div", "figure", "table", "thead", "tbody", "tr", "svg", "g"}      # elements that hold only elements


def test_html_page_is_self_contained(folders):
    assert not EXTERNAL.search(page(*folders))


def test_html_page_has_the_table_and_the_three_charts(folders):
    html = page(*folders)
    assert html.startswith("<!doctype html>") and html.count("<figure") == 3 and html.count("<table") == 1
    assert re.findall(r"<figcaption><strong>(.*?)</strong> (\w+)", html) == [
        ("Solve rate (%)", "Solved"), ("Mean cost per solved row", "On"), ("CPU µs per pop/unit", "CPU")]
    assert 'name="viewport"' in html and html.count("viewBox") == html.count("<svg")  # the charts scale to the screen
    assert "overflow-x" in html                                                       # the wide table scrolls itself


def test_the_page_is_light_by_default_and_dark_by_the_browser_or_by_choice(folders):
    html, light, dark = page(*folders), report.LIGHT, report.DARK
    assert f":root {{ {light} }}" in html
    assert f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {dark} }} }}' in html
    assert f':root[data-theme="dark"] {{ {dark} }}' in html
    assert "background: var(--page)" in html                                  # the body paints its own background


def test_the_page_body_is_well_formed_with_no_stray_text_between_its_blocks(folders):
    body = re.search(r"<main>.*</main>", page(*folders), re.S).group()
    for element in ElementTree.fromstring(body).iter():                   # raises on an unclosed or mismatched tag
        if element.tag in BLOCKS:
            assert not (element.text or "").strip() and not any((child.tail or "").strip() for child in element)


def test_the_page_table_has_the_cells_of_the_markdown_table(folders):
    html = page(*folders)
    head = re.findall(r"<th>(.*?)</th>", html)
    rows = [re.findall(r"<td>(.*?)</td>", tr) for tr in re.findall(r"<tr>(.*?)</tr>", html)[1:]]   # [0] is the head
    assert [dict(zip(head, row, strict=True)) for row in rows] == table(report.markdown(load(*folders)))


def test_runs_counted_in_different_units_get_their_own_panel_and_axis(tmp_path, folders):
    html = page(*folders)
    assert [len(panels(html, chart)) for chart in range(3)] == [1, 2, 2]             # a rate has no unit: one panel
    pops, units = panels(html, 1)                                                      # A counts 20 pops, B 10 units
    assert (pops.ticks, units.ticks) == (["1", "10", "100"], ["1", "10"])
    same_unit = page(write_run(tmp_path, "C", A_ROWS), write_run(tmp_path, "D", A_ROWS))
    assert [len(panels(same_unit, chart)) for chart in range(3)] == [1, 1, 1]


def test_a_unit_keeps_its_color_whatever_the_other_runs(tmp_path):
    kinds = {"pops": {}, "units": {"method": "hybrid"}, "evals": {"method": "rl"}, "other": {"cost_unit": "furlongs"}}
    runs = {name: write_run(tmp_path, name, A_ROWS, **kind) for name, kind in kinds.items()}

    def colors(*names):
        html = page(*(runs[name] for name in names))
        return {bar.name: bar.color for panel in panels(html, 1) for bar in panel.bars}

    assert colors("pops", "units", "evals", "other") == {"pops": "s1", "units": "s2", "evals": "s3", "other": "s0"}
    assert colors("units", "other") == {"units": "s2", "other": "s0"}              # the unit's color, not its rank
    swatches = re.findall(r'<i class="(s\d)"></i> (\w+)', page(*runs.values()))    # the legend wears the same colors
    assert swatches == [("s1", "pops"), ("s2", "units"), ("s3", "evaluations"), ("s0", "furlongs")]


def test_html_says_that_units_differ_and_shows_the_legend_only_for_mixed_units(tmp_path, folders):
    html = page(*folders)
    assert ('<p class="legend">Bar color is the unit the run counts its cost in: <span><i class="s1"></i> pops</span> '
            '<span><i class="s2"></i> units</span></p>') in html
    assert "not a pop" in html and "log scale" in html
    same_unit = page(write_run(tmp_path, "C", A_ROWS), write_run(tmp_path, "D", A_ROWS))
    assert 'class="legend"' not in same_unit and "None" not in same_unit
    assert "not a pop" in same_unit                                                  # the caption always stays


def test_each_bar_ends_where_its_value_lies_on_the_axis(tmp_path):
    every = write_run(tmp_path, "every", [rec("0", True, 20, 1.0), rec("1", True, 20, 1.0)])   # 100%, 50,000 µs/pop
    older = write_run(tmp_path, "older", A_ROWS)                                               # 50%, 100,000 µs/pop
    html = page(every, older)                                                    # both: 20 pops, a log axis 1..100
    for chart, fractions in ((0, [1, 0.5]), (1, [math.log10(20) / 2] * 2), (2, [0.5, 1])):
        (panel,) = panels(html, chart)
        ticks = panel.axes + panel.grid                                          # the axis is the first tick
        expected = [ticks[0] + fraction * (ticks[-1] - ticks[0]) for fraction in fractions]
        assert [bar.tip for bar in panel.bars] == pytest.approx(expected, abs=0.2)
        gaps = [b - a for a, b in itertools.pairwise(ticks)]
        assert max(gaps) - min(gaps) < 0.2                      # evenly spaced: steps of 20, 20000, and powers of ten
    assert panels(html, 0)[0].ticks == ["0", "20", "40", "60", "80", "100"]


def test_every_label_and_tick_label_fits_inside_its_chart(tmp_path, folders):
    wide = write_run(tmp_path, "wide", A_ROWS, "rl")                       # the longest labels: evaluations
    done = write_run(tmp_path, "done", [rec("0", True, 5, 1.0)])           # 100% solved beside the 50% runs
    html = page(*folders, wide, done)
    for chart in range(3):
        for panel in panels(html, chart):
            assert panel.lowest < panel.height and all(panel.axes[0] <= bar.tip for bar in panel.bars)
            assert all(bar.tip + report.GAP + report.CHAR * len(bar.label) <= report.W for bar in panel.bars)


@pytest.mark.parametrize("length,shown", [(38, 38), (39, 38)])
def test_a_long_run_name_is_cut_above_its_bar_but_not_in_its_tooltip(tmp_path, length, shown):
    name = "r" * length
    (bar,) = panels(page(write_run(tmp_path, name, A_ROWS)), 0)[0].bars
    assert len(bar.name) == shown and bar.name.endswith("…") == (length > shown)
    assert bar.tooltip.startswith(name + ":")


def test_bars_are_grouped_by_unit_in_order_of_first_appearance():
    bars = [report.Bar(name, 1, unit, "", "") for name, unit in (("a", "pops"), ("b", "units"), ("c", "pops"))]
    assert [[bar.name for bar in group] for group in report.by_unit(bars)] == [["a", "c"], ["b"]]


def test_html_bar_labels_and_tooltips(folders):
    html = page(*folders)
    bars = [bar for chart in range(3) for panel in panels(html, chart) for bar in panel.bars]
    assert {bar.label for bar in bars} == {"50%", "20 pops", "10 units", "100K µs/pop", "57.1K µs/unit"}
    assert {bar.tooltip for bar in bars} == {
        "A: 2 of 4 rows solved", "B: 2 of 4 rows solved",
        "A: mean 20.0 pops per solved row (2 solved)", "B: mean 10.0 units per solved row (2 solved)",
        "A: 100,000.0 CPU µs per pop", "B: 57,142.9 CPU µs per unit"}


def test_html_escapes_names_and_notes(tmp_path):
    html = page(write_run(tmp_path, "<i>x&y", A_ROWS))
    assert "<i>x" not in html and "&lt;i&gt;x&amp;y" in html


def test_html_page_carries_the_common_scope_note(folders):
    assert f'<p class="note">{COMMON_NOTE[2:]}</p>' in page(*folders, common=True)


def test_html_page_without_data_to_plot(tmp_path):
    empty = write_run(tmp_path, "empty", [])                                  # no rows at all
    unsolved = write_run(tmp_path, "u", [rec("0", False, 100, 1.0)])           # no solved row: no cost bar
    bare = write_run(tmp_path, "n", [{"id": "0", "solved": False}])            # neither cost nor timing
    html = page(empty, unsolved, bare)
    labels = [[bar.label for panel in panels(html, chart) for bar in panel.bars] for chart in range(3)]
    assert labels == [["no data", "0%", "0%"], ["no data"] * 3, ["no data", "10K µs/pop", "no data"]]
    assert panels(html, 1)[0].ticks == ["0.1", "1"]                            # nothing to plot: a bare axis
    assert "None" not in html and "nan" not in html


# ---- the axes and the bars -----------------------------------------------------------------------------------

def test_linear_ticks_are_round_and_cover_the_top():
    assert report.linear_ticks(100) == [0, 20, 40, 60, 80, 100]
    assert report.linear_ticks(1421) == [0, 500, 1000, 1500]
    assert report.linear_ticks(118) == [0, 50, 100, 150]
    assert report.linear_ticks(5) == [0, 1, 2, 3, 4, 5]


def test_decade_ticks_start_a_decade_below_the_smallest_value():
    assert report.decade_ticks([39, 1205]) == [1, 10, 100, 1000, 10000]
    assert report.decade_ticks([10, 20]) == [1, 10, 100]
    assert report.decade_ticks([10, 10]) == [1, 10]
    assert report.decade_ticks([3]) == [0.1, 1, 10]
    assert report.decade_ticks([]) == [0.1, 1]                          # nothing to plot: a bare axis


def test_place_is_proportional_on_a_linear_axis_and_logarithmic_on_a_log_axis():
    assert report.place(50, [0, 100], log=False) == 0.5
    assert report.place(15, [10, 20], log=False) == 0.5                   # an axis need not start at zero
    assert report.place(100, [1, 10, 100, 1000], log=True) == pytest.approx(2 / 3)
    assert report.place(1, [0.1, 1, 10], log=True) == pytest.approx(0.5)  # nor a log axis at one
    assert report.place(10, [1, 10, 100, 1000], True) < report.place(20, [1, 10, 100, 1000], True)


@pytest.mark.parametrize("value,text", [(0, "0"), (5.0, "5"), (66.67, "66.7"), (118.3, "118"), (1000, "1K"),
                                        (1234, "1.23K"), (57142.857, "57.1K"), (100000, "100K"), (999999, "1M"),
                                        (2.5e6, "2.5M"), (3e9, "3G"), (0.1, "0.1")])
def test_short_numbers_keep_three_significant_digits(value, text):
    assert report.short(value) == text


def test_a_panel_is_a_row_per_bar_under_a_baseline_and_gridlines():
    """The markup of a small panel: a name over each bar, its label at the tip, a tooltip; no data draws no bar."""
    bars = [report.Bar("run <1>", 50, "pops", "%", 'run <1>: "half"'), report.Bar("gap", None, "units", "%", "no data")]
    assert report.panel("Solve", bars, [0, 100], log=False) == "".join([
        '<svg viewBox="0 0 280 106" role="img" aria-label="Solve">',
        '<line class="axis" x1="8.0" x2="8.0" y2="84"/>',
        '<text class="tick" x="8.0" y="98" text-anchor="middle">0</text>',
        '<line class="grid" x1="219.0" x2="219.0" y2="84"/>',
        '<text class="tick" x="219.0" y="98" text-anchor="middle">100</text>',
        '<g class="s1"><title>run &lt;1&gt;: &quot;half&quot;</title>',
        '<rect class="hit" y="0" width="280" height="42"/>',
        '<text x="8" y="14">run &lt;1&gt;</text>',
        '<rect class="bar" x="8" y="20" width="105.5" height="14" rx="4"/>',
        '<text class="val" x="119.5" y="32">50%</text></g>',
        '<g class="s2"><title>no data</title>',
        '<rect class="hit" y="42" width="280" height="42"/>',
        '<text x="8" y="56">gap</text>',
        '<rect class="bar" x="8" y="62" width="0" height="14" rx="4"/>',
        '<text class="val" x="14.0" y="74">no data</text></g></svg>'])


# ---- the runner's own output ---------------------------------------------------------------------------------

def test_the_numbers_agree_with_the_summary_the_runner_writes(tmp_path):
    """Four MS640 rows through the pure-Python search with a small cap, two of them bound by it."""
    overrides = ['rows="7,500,620,639"', "search.cap=16", "search.budget=300", "workers=1", "name=real"]
    config = runner.load_config(os.path.join(ROOT, "configs", "baseline_spec.toml"), overrides)
    summary = runner.run(config, str(tmp_path), log=lambda *a: None)
    run = report.load_run(tmp_path / "real")
    m = report.measure(run)
    assert (run.name, run.method, run.benchmark, run.unit) == ("real", "greedy", "ms640", summary["cost"]["unit"])
    assert (m["rows"], m["solved"], m["errors"]) == (summary["rows"], summary["solved"], summary["errors"]) == (4, 2, 0)
    assert m["cost"] == pytest.approx(summary["cost"]["on_solved"] / summary["solved"])
    assert m["sub"] == pytest.approx(summary["path_length"]["ac_path"]["sub_moves"]["mean"])
    assert m["elem"] == pytest.approx(summary["path_length"]["ac_path"]["elem_moves"]["mean"])
    assert m["raise_rows"] == summary["caps"]["cap"]["rows_would_pop"] == 2
    if "us_per_cost" in summary:                            # a runner that records cpu_seconds
        assert not m["wall"] and m["us"] == pytest.approx(summary["us_per_cost"], rel=0.01)


# ---- the command ---------------------------------------------------------------------------------------------

def test_cli_prints_the_table_and_writes_the_page(folders, tmp_path, capsys):
    out = tmp_path / "page.html"
    compare.main([*folders, "--html", str(out), "--common"])
    printed = capsys.readouterr().out
    assert [row["run"] for row in table(printed)] == ["A", "B"] and COMMON_NOTE in printed.splitlines()
    html = out.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>") and COMMON_NOTE[2:] in html


def test_cli_without_runs_is_an_error():
    with pytest.raises(SystemExit) as error:
        compare.main([])
    assert error.value.code == 2
