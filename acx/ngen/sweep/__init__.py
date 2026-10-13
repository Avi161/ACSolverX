"""Rank-n brute force: stabilise each row with words, then search every stabilised start (``docs/RANK3.md``).

``python -m acx.ngen.sweep --config configs/rank3_bf.toml [--rows 0:40] [--set key=value] [--verify N]``. Each row also
gets its 2-generator control and its null stabilisation (empty words), which must agree. Results go to
``<out>/<name>/``: ``config.json``, ``rows/<id>.npz`` and ``summary.json``, ``summary.md``.

Modules: ``words`` (word pool, starts), ``config``, ``rows`` (one row's searches and file), ``driver`` (``run``),
``summary``, ``check`` (``verify``) and ``cli``.
"""
from .check import check_counters, verify
from .cli import main
from .config import COUNTERS, SweepConfig, SweepError, words_of
from .driver import run
from .rows import load_row, row_path, sweep_row, sweep_row_file
from .summary import summarize
from .words import combos, pool, reduced_words, sampled, start

__all__ = ["COUNTERS", "SweepConfig", "SweepError", "check_counters", "combos", "load_row", "main", "pool",
           "reduced_words", "row_path", "run", "sampled", "start", "summarize", "sweep_row", "sweep_row_file", "verify",
           "words_of"]
