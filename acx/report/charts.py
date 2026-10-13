"""The three bar charts of the page as inline SVG, and the legend for runs counted in different units."""
import math
from html import escape
from typing import NamedTuple

from .table import fmt, percent

SLOT = {"pops": 1, "units": 2, "evaluations": 3}         # a unit's categorical color slot; any other unit is gray (0)
# Chart geometry in SVG pixels: width, left margin, pitch of one bar, its thickness, the gap before its label, and the
# width of one label character (an estimate that keeps the longest label inside the chart).
W, LEFT, ROW, BAR, GAP, CHAR = 280, 8, 42, 14, 6, 7


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
                   f'<rect class="bar" x="{LEFT}" y="{top + 20}" width="{width:g}" height="{BAR}" rx="4"/>'
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

