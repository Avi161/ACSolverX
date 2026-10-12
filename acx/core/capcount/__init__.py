"""Cap counters: what a relator cap dropped, and whether a dropped state would have been popped.

Heuristic-agnostic: a search passes the heap keys its own priority gives, and the counters only compare them.

* ``records``: the ``FIELDS`` of a counter and the helpers on its records (``blank``, ``combine``, ``summarize``).
* ``counter``: ``CapCount``, the plain Python counter.
* ``kernels`` and ``arrays``: ``CapArrays``, its numba twin for the fast engine.
"""
from .arrays import CapArrays
from .counter import CapCount
from .kernels import C_POOL, cc_drop, cc_free, cc_pop
from .records import FIELDS, blank, combine, fields, summarize

__all__ = ["FIELDS", "fields", "blank", "combine", "summarize", "CapCount", "CapArrays", "cc_drop", "cc_free",
           "cc_pop", "C_POOL"]
