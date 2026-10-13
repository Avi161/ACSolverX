"""Compare finished runs (``compare.py`` is the command): load result folders, tabulate them, draw them.

* ``load``: ``Run`` and ``load_run``, a results folder read from its ``paths.jsonl`` or its ``summary.json``.
* ``table``: the numbers of each run, the notes and the markdown table.
* ``charts``: the bar charts as inline SVG.
* ``page``: the self-contained HTML page.
"""
from .charts import CHAR, GAP, Bar, W, by_unit, decade_ticks, linear_ticks, panel, place, short
from .load import load_run
from .page import DARK, LIGHT, html_page
from .table import markdown, measure, measure_summary, percent, raise_rows

__all__ = ["load_run", "markdown", "html_page", "measure", "measure_summary", "raise_rows", "percent", "Bar", "place",
           "decade_ticks", "linear_ticks", "short", "panel", "by_unit", "W", "GAP", "CHAR", "LIGHT", "DARK"]
