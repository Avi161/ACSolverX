"""Compare finished runs: load ``results/<run>/`` folders, tabulate them, draw them (``compare.py`` is the command)."""
import json
import math
import statistics
from html import escape
from pathlib import Path
from string import Template
from typing import NamedTuple

UNIT = {"hybrid": "units", "rl": "evaluations"}          # what ``cost`` counts; every other method counts pops
# The record fields the report reads, besides the ``*_would_pop`` cap flags; a record's other fields are dropped.
KEEP = {"id", "solved", "cost", "sub_moves", "elem_moves", "seconds", "cpu_seconds", "error"}
UNITS_NOTE = ("Units differ: a pop is one heap pop of a search; a hybrid unit also counts accepted automorphisms, "
              "image evaluations and substitution moves, so it is not a pop; an RL evaluation is one network "
              "evaluation. Compare cost and CPU per pop/unit only between runs counted in the same unit.")
HEADER = ("run", "method", "benchmark", "rows", "solved", "mean cost (solved)", "median cost (solved)",
          "mean sub_moves", "mean elem_moves", "CPU s/row", "CPU µs per pop/unit", "raise-cap rows", "errors")


class Run(NamedTuple):
    """One results folder: its name, method, benchmark, the unit its ``cost`` counts, and its records."""
    name: str
    method: str
    benchmark: str
    unit: str
    records: list


# ---- loading -------------------------------------------------------------------------------------------------

def read_json(path):
    """The object in a JSON file, ``{}`` when the file is missing."""
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}


def read_records(path):
    """The records of a ``paths.jsonl``, cut down to the fields the report reads: the move lists are most of a big
    file. A last line cut off by a run still writing is skipped; any other line that is not JSON stops the report."""
    records, bad = [], None
    with open(path, encoding="utf-8") as lines:
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            if bad:                                      # a bad line with more lines after it is not a cut-off
                raise SystemExit(f"{path}: line {bad} is not JSON")
            try:
                record = json.loads(line)
            except ValueError:
                bad = number
            else:
                records.append({k: v for k, v in record.items() if k in KEEP or k.endswith("_would_pop")})
    return records


def load_run(folder):
    """The ``Run`` in a results folder; ``summary.json``, else ``config.json``, names its method and benchmark."""
    folder = Path(folder).absolute()
    if not folder.is_dir():
        raise SystemExit(f"{folder}: not a folder")
    if not (folder / "paths.jsonl").exists():
        raise SystemExit(f"{folder.name}: no paths.jsonl (run.py writes one per run; a rankn sweep has none)")
    info = {**read_json(folder / "config.json"), **read_json(folder / "summary.json")}
    method = info.get("method", "?")
    unit = info.get("cost_unit") or UNIT.get(method, "pops")
    return Run(folder.name, method, info.get("benchmark", "?"), unit, read_records(folder / "paths.jsonl"))


# ---- numbers -------------------------------------------------------------------------------------------------

def mean(values):
    return sum(values) / len(values) if values else None


def percent(part, whole):
    """``part`` of ``whole`` in percent, to one decimal; never 0 or 100 unless it is exactly that."""
    value = round(100 * part / whole, 1)
    if part and not value:
        return 0.1
    return 99.9 if part < whole and value == 100 else value


def column(records, key):
    """The values of ``key`` that the records have (a missing or null value is skipped)."""
    return [r[key] for r in records if r.get(key) is not None]


def cpu_seconds(record):
    """A row's CPU seconds; a run older than ``cpu_seconds`` has only the wall-clock ``seconds``."""
    return record.get("cpu_seconds", record.get("seconds"))


def measure(run, ids=None):
    """The numbers of a run's table row. ``ids`` limits the cost, move and CPU means to those rows (``--common``)."""
    scope = [r for r in run.records if ids is None or r["id"] in ids]
    solved = [r for r in scope if r["solved"]]
    cost, sub, elem = (column(solved, key) for key in ("cost", "sub_moves", "elem_moves"))
    cpu = [seconds for seconds in map(cpu_seconds, scope) if seconds is not None]
    total_cost = sum(column(scope, "cost"))
    return {
        "rows": len(run.records),
        "solved": sum(1 for r in run.records if r["solved"]),
        "errors": sum(1 for r in run.records if r.get("error")),
        "raise_rows": sum(1 for r in run.records if any(v for k, v in r.items() if k.endswith("_would_pop"))),
        "n": len(solved), "cost": mean(cost), "median": statistics.median(cost) if cost else None,
        "sub": mean(sub), "sub_n": len(sub), "elem": mean(elem), "elem_n": len(elem),
        "cpu_row": mean(cpu), "us": 1e6 * sum(cpu) / total_cost if cpu and total_cost else None,
        "wall": any("cpu_seconds" not in r for r in scope),          # seconds stands in for cpu_seconds
    }


def solved_ids(run):
    return {r["id"] for r in run.records if r["solved"]}


def common_ids(runs):
    """The ids of the rows every run solved; row ids only match across runs of one benchmark."""
    benchmarks = sorted({run.benchmark for run in runs})
    if len(benchmarks) > 1:
        raise SystemExit(f"--common needs runs on one benchmark, got {benchmarks}")
    return set.intersection(*(solved_ids(run) for run in runs))


def rows_of(n):
    return f"{n} row{'' if n == 1 else 's'}"


def head_to_head(a, b):
    """The rows two runs solved, by only a, only b, both or neither, over the rows both ran."""
    shared = {r["id"] for r in a.records} & {r["id"] for r in b.records}
    by_a, by_b = solved_ids(a) & shared, solved_ids(b) & shared
    return (f"Head to head on {a.benchmark} ({rows_of(len(shared))} in common): solved by {a.name} only "
            f"{len(by_a - by_b)}, by {b.name} only {len(by_b - by_a)}, by both {len(by_a & by_b)}, "
            f"by neither {len(shared - by_a - by_b)}.")


# ---- the table -----------------------------------------------------------------------------------------------

def fmt(value, digits=1, suffix=""):
    """``value`` with thousands separators and a suffix; ``-`` when there is none."""
    return "-" if value is None else f"{value:,.{digits}f}{suffix}"


def count_note(m, key):
    """`` (n=k)`` when a mean covers only k of the solved rows (a CoV stable certificate has no elementary path)."""
    return f" (n={m[key + '_n']})" if m[key + "_n"] not in (0, m["n"]) else ""


def cells(run, m):
    """The formatted cells of a run's table row, in the order of ``HEADER``."""
    unit, star = run.unit, "*" if m["wall"] else ""
    solved = f"{m['solved']} ({percent(m['solved'], m['rows']):.1f}%)" if m["rows"] else "0 (-)"
    return [run.name, run.method, run.benchmark, m["rows"], solved,
            fmt(m["cost"], suffix=f" {unit}"), fmt(m["median"], suffix=f" {unit}"),
            fmt(m["sub"]) + count_note(m, "sub"), fmt(m["elem"]) + count_note(m, "elem"),
            fmt(m["cpu_row"], 3, star), fmt(m["us"], 1, f"/{unit.removesuffix('s')}{star}"),
            m["raise_rows"], m["errors"]]


def notes(runs, measured, ids):
    """The lines that say what the table covers: its scope, wall-clock CPU, raise-cap rows, head to head."""
    if ids is None:
        lines = ["Cost and move columns average each run's solved rows; CPU columns cover all of its rows."]
    else:
        lines = [f"--common: cost, move and CPU columns cover only the {rows_of(len(ids))} every run solved."]
    if any(m["wall"] and m["cpu_row"] is not None for m in measured):
        lines.append("Starred (*) CPU values are wall-clock seconds, not CPU: the run has no cpu_seconds, and a "
                     "busy machine inflates them.")
    if any(m["raise_rows"] for m in measured):
        lines.append("raise-cap rows: rows where a relator cap dropped a state the search would have popped "
                     "(a larger cap changes that row's search).")
    if len(runs) == 2 and runs[0].benchmark == runs[1].benchmark:
        lines.append(head_to_head(*runs))
    return lines


def tabulate(runs, common):
    """Each run's table numbers and the notes on what they cover; the one step the markdown and the page share."""
    ids = common_ids(runs) if common else None
    measured = [measure(run, ids) for run in runs]
    return measured, notes(runs, measured, ids)


def markdown(runs, common=False):
    """``runs`` as one markdown table followed by the notes on what its numbers cover."""
    measured, lines = tabulate(runs, common)
    if len({run.unit for run in runs}) > 1:
        lines.append(UNITS_NOTE)
    rule = ["---"] * 3 + ["---:"] * (len(HEADER) - 3)
    table = [HEADER, rule] + [cells(run, m) for run, m in zip(runs, measured, strict=True)]
    rows = ["| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in table]
    return "\n".join(rows + [""] + [f"- {line}" for line in lines])


# ---- the HTML page -------------------------------------------------------------------------------------------

SLOT = {"pops": 1, "units": 2, "evaluations": 3}         # a unit's categorical color slot; any other unit is gray (0)
# Chart geometry in SVG pixels: width, left margin, pitch of one bar, its thickness, the gap before its label, and the
# width of one label character (an estimate that keeps the longest label inside the chart).
W, LEFT, ROW, BAR, GAP, CHAR = 280, 8, 42, 14, 6, 7
LIGHT = ("color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e1e0d9;"
         "--axis:#c3c2b7;--c1:#2a78d6;--c2:#eb6834;--c3:#1baf7a")
DARK = ("color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#2c2c2a;"
        "--axis:#383835;--c1:#3987e5;--c2:#d95926;--c3:#199e70")
# One stylesheet: the three theme rules take the color tokens at $light and $dark, the rest only reads them.
STYLE = Template("""
:root { $light }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { $dark } }
:root[data-theme="dark"] { $dark }
body { margin: 0; background: var(--page); color: var(--ink);
       font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1280px; margin: 0 auto; padding: 8px 16px 24px; }
h1 { font-size: 20px; margin: 16px 0 8px; }
.note, .legend { color: var(--ink2); font-size: 13px; margin: 8px 0; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin: 16px 0; }
figure, .scroll { margin: 0; padding: 12px 16px; background: var(--surface); border: 1px solid var(--grid);
                  border-radius: 8px; }
figcaption { font-size: 13px; color: var(--ink2); margin-bottom: 8px; }
figcaption strong { display: block; color: var(--ink); font-size: 14px; }
svg { display: block; width: 100%; max-width: 420px; margin: 0 auto; }
svg text { fill: var(--ink); font-size: 13px; }
svg .tick { fill: var(--ink2); font-size: 12px; }
svg .val { font-weight: 600; }
.grid { stroke: var(--grid); }
.axis { stroke: var(--axis); }
.hit { fill: transparent; }
.bar { fill: currentColor; }
g:hover .bar { opacity: .75; }
.s0 { color: var(--ink2); } .s1 { color: var(--c1); } .s2 { color: var(--c2); } .s3 { color: var(--c3); }
.legend span { margin-right: 12px; white-space: nowrap; }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; background: currentColor; }
.scroll { overflow-x: auto; padding: 0; }
table { border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; }
th, td { padding: 6px 10px; text-align: right; border-bottom: 1px solid var(--grid); }
th { color: var(--ink2); font-weight: 600; vertical-align: bottom; }
td { white-space: nowrap; }
th:nth-child(-n+3), td:nth-child(-n+3) { text-align: left; }
""").substitute(light=LIGHT, dark=DARK)
PAGE = Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AC run comparison</title>
<style>$style</style>
</head>
<body>
<main>
<h1>AC run comparison</h1>
$legend
<div class="charts">$charts</div>
<p class="note">$units</p>
<div class="scroll">$table</div>
$notes
</main>
</body>
</html>
""")


class Bar(NamedTuple):
    """One run's bar: its ``value`` (None: no data), the ``unit`` that colors it, the ``suffix`` of its label and its
    ``tooltip``."""
    name: str
    value: float
    unit: str
    suffix: str
    tooltip: str


def short(value):
    """``value`` in three significant digits, compact from a thousand: 118, 57.1K, 2.5M, 0.1."""
    value = float(f"{value:.3g}")                          # round first, so that 999999 reads 1M
    for size, mark in ((1e9, "G"), (1e6, "M"), (1e3, "K")):
        if value >= size:
            return f"{value / size:g}{mark}"
    return f"{value:g}"


def linear_ticks(top):
    """Round tick values from 0 up to the first at or above ``top``, in at most five steps."""
    exponent = math.floor(math.log10(top))
    steps = (m * 10 ** (exponent + k) for k in (-1, 0) for m in (1, 2, 5))
    step = next(s for s in steps if top / s <= 5)
    return [i * step for i in range(math.ceil(top / step) + 1)]


def decade_ticks(values):
    """Powers of ten from one decade below the smallest value up to the first at or above the largest."""
    low = math.floor(math.log10(min(values, default=1))) - 1
    high = math.ceil(math.log10(max(values, default=1)))
    return [10.0 ** exponent for exponent in range(low, high + 1)]


def place(value, ticks, log):
    """Where ``value`` lies along the axis of ``ticks``: 0 at the first tick, 1 at the last."""
    low, high = ticks[0], ticks[-1]
    if log:
        low, high, value = math.log10(low), math.log10(high), math.log10(value)
    return (value - low) / (high - low)


def bar_path(x, y, width, height, radius=4):
    """A horizontal bar growing from the baseline at ``x``: square there, rounded at the tip."""
    r = min(radius, width, height / 2)
    return (f"M{x:g},{y:g}h{width - r:g}a{r:g},{r:g} 0 0 1 {r:g},{r:g}v{height - 2 * r:g}"
            f"a{r:g},{r:g} 0 0 1 {-r:g},{r:g}h{r - width:g}z")


def by_unit(bars):
    """The bars in groups of one unit each, in order of first appearance; a group shares an axis, others do not."""
    groups = {}
    for bar in bars:
        groups.setdefault(bar.unit, []).append(bar)
    return list(groups.values())


def panel(title, bars, ticks, log):
    """One horizontal bar chart as inline SVG: a name above each bar, its value at the tip."""
    labels = ["no data" if bar.value is None else short(bar.value) + bar.suffix for bar in bars]
    plot = W - LEFT - CHAR * max(map(len, labels)) - 2 * GAP    # the room left of the longest label and a margin
    room = (W - LEFT) // CHAR                                   # the characters of a name that fit above its bar
    base = ROW * len(bars)
    svg = []
    for k, tick in enumerate(ticks):
        x = LEFT + plot * place(tick, ticks, log)
        svg.append(f'<line class="{"axis" if k == 0 else "grid"}" x1="{x:.1f}" x2="{x:.1f}" y2="{base}"/>'
                   f'<text class="tick" x="{x:.1f}" y="{base + 14}" text-anchor="middle">{short(tick)}</text>')
    for row, (bar, label) in enumerate(zip(bars, labels, strict=True)):
        top = row * ROW
        width = 0 if bar.value is None else plot * place(bar.value, ticks, log)
        name = bar.name if len(bar.name) <= room else bar.name[:room - 1] + "…"
        svg.append(f'<g class="s{SLOT.get(bar.unit, 0)}"><title>{escape(bar.tooltip)}</title>'
                   f'<rect class="hit" y="{top}" width="{W}" height="{ROW}"/>'
                   f'<text x="{LEFT}" y="{top + 14}">{escape(name)}</text>'
                   f'<path class="bar" d="{bar_path(LEFT, top + 20, width, BAR)}"/>'
                   f'<text class="val" x="{LEFT + width + GAP:.1f}" y="{top + 32}">{escape(label)}</text></g>')
    return f'<svg viewBox="0 0 {W} {base + 22}" role="img" aria-label="{escape(title)}">{"".join(svg)}</svg>'


def figure(title, caption, groups, ticks_of, log=False):
    """A titled chart with one panel per group of bars. ``ticks_of`` makes a panel's ticks from its positive values."""
    panels = "".join(panel(title, group, ticks_of([bar.value for bar in group if bar.value]), log)
                     for group in groups)
    return f'<figure><figcaption><strong>{escape(title)}</strong> {escape(caption)}</figcaption>{panels}</figure>'


def charts(runs, measured):
    """The three charts, one bar per run: solve rate, mean cost per solved row (log scale), CPU µs per pop/unit."""
    rate, cost, speed = [], [], []
    for run, m in zip(runs, measured, strict=True):
        one = run.unit.removesuffix("s")
        rate.append(Bar(run.name, percent(m["solved"], m["rows"]) if m["rows"] else None, run.unit, "%",
                        f"{run.name}: {m['solved']} of {m['rows']} rows solved"))
        cost.append(Bar(run.name, m["cost"] or None, run.unit, f" {run.unit}",          # a log axis has no zero
                        f"{run.name}: mean {fmt(m['cost'])} {run.unit} per solved row ({m['n']} solved)"))
        speed.append(Bar(run.name, m["us"], run.unit, f" µs/{one}", f"{run.name}: {fmt(m['us'])} CPU µs per {one}"))
    own_panel = "Runs counted in different units get a panel and an axis each."
    return [
        figure("Solve rate (%)", "Solved rows as a share of all rows of the run; error rows count as unsolved.",
               [rate], lambda values: linear_ticks(100)),             # one panel: a rate has no unit; always 0 to 100
        figure("Mean cost per solved row", f"On a log scale (gridlines 10x apart) lengths show ratios. {own_panel}",
               by_unit(cost), decade_ticks, log=True),
        figure("CPU µs per pop/unit",
               f"CPU time of all rows, verification included, over their total cost. {own_panel}",
               by_unit(speed), lambda values: linear_ticks(max(values, default=1)))]


def legend(runs):
    """What the bar colors mean; only needed when the runs count their cost in more than one unit."""
    units = list(dict.fromkeys(run.unit for run in runs))        # in the order the charts show them
    if len(units) < 2:
        return ""
    keys = " ".join(f'<span><i class="s{SLOT.get(unit, 0)}"></i> {escape(unit)}</span>' for unit in units)
    return f'<p class="legend">Bar color is the unit the run counts its cost in: {keys}</p>'


def html_table(runs, measured):
    """The table behind the charts (every number a chart shows is here)."""
    head = "".join(f"<th>{escape(name)}</th>" for name in HEADER)
    rows = ["<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in cells(run, m)) + "</tr>"
            for run, m in zip(runs, measured, strict=True)]
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def html_page(runs, common=False):
    """``runs`` as one self-contained HTML page: three bar charts and the table behind them, light and dark."""
    measured, lines = tabulate(runs, common)
    return PAGE.substitute(
        style=STYLE, legend=legend(runs), charts="".join(charts(runs, measured)), units=escape(UNITS_NOTE),
        table=html_table(runs, measured), notes="".join(f'<p class="note">{escape(line)}</p>' for line in lines))
