"""The self-contained HTML page: its theme and stylesheet, the table behind the charts, and ``html_page``."""
from html import escape
from string import Template

from .charts import charts, legend
from .table import HEADER, UNITS_NOTE, cells, tabulate

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
