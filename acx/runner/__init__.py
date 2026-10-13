"""The benchmark runner behind ``run.py``: one config, one method, every row verified before it is written.

- ``config``: read and check a config (``load_config``), build a method's settings (``method_config``).
- ``methods``: one function per method, turning a solve into a record.
- ``output``: the ``path`` and ``fields`` options: which record keys are written, and whether paths are kept.
- ``caps``: the cap counters of a record and their ``summary.json`` block.
- ``summary``: ``summary.json`` from a run's records.
- ``rundir``: the run folder: its ``config.json`` guard, the records of ``paths.jsonl``, what a resume keeps.
- ``execute``: solve the rows (picked by ``acx.data.select``), resume, write ``results/<name>/`` (``run``).
"""
from ..data import select
from .config import load_config, method_config
from .execute import run
from .summary import summarize

__all__ = ["load_config", "method_config", "run", "select", "summarize"]
