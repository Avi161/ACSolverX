"""One search API, ``search(presentation, cfg) -> Result``, over the ``spec`` (Python) and ``fast`` (numba) backends.

Both backends pop the same states in the same order, a strict total order on ``(priority, depth, state_key)``
(``acx.core.priority``, the first discoverer's depth, ``acx.core.words.state_key``), so a ``Result`` and its
``PARITY_STATS`` do not depend on the backend. A solved path is always replayed by ``acx.verify.replay``.
"""
import importlib
import time
from dataclasses import dataclass, field, replace

from ..core.capcount import FIELDS as CAP_FIELDS
from ..core.config import SearchConfig
from ..core.words import Presentation

# Stats every backend reports with identical values (the cap counters are ``acx.core.capcount.FIELDS``).
PARITY_STATS = ("discovered", *CAP_FIELDS, "min_total", "max_total",
                "max_total_expanded", "max_expanded")


class BackendUnavailable(RuntimeError):
    """The ``fast`` backend needs numba."""


@dataclass(frozen=True)
class Result:
    """A search outcome. ``start`` is the normal form (``Presentation.normal``) the search began from; a path
    replays on it and on the raw presentation. ``stats`` holds ``PARITY_STATS`` plus ``backend`` and ``seconds``;
    the cap counters only observe (``cap_would_pop == 0``: no larger cap changes the search; otherwise
    ``cap_needed`` is the smallest cap that does)."""
    solved: bool
    pops: int                       # states popped, the solved one included
    path: tuple | None              # tuple of Move from ``start`` when solved and captured
    start: Presentation             # the normal form the search started from
    end: Presentation | None        # the popped all-length-1 state, when solved
    stats: dict = field(default_factory=dict)
    trace: tuple | None = None      # popped states as tuples of relator strings (cfg.trace)
    depth: int | None = None        # depth of the solved state: the moves of its path, kept without the path

    @property
    def path_length(self):
        """Number of moves of a solve, None when unsolved; the same whether or not the path was captured."""
        return self.depth if self.path is None else len(self.path)


def as_presentation(pres):
    """``pres`` as a ``Presentation``: relator strings (``("xxYXY", "xyyXY")``) are parsed."""
    if isinstance(pres, Presentation):
        return pres
    return Presentation.parse(*pres)


def backend(name):
    """The module of backend ``name``, each with ``run(start, cfg)``; ``fast`` is imported on demand."""
    if name == "spec":
        from . import spec
        return spec
    try:
        return importlib.import_module("acx.search.fast")
    except ModuleNotFoundError as e:
        if e.name not in ("acx.search.fast", "numba"):
            raise
        raise BackendUnavailable(f"backend 'fast' needs acx.search.fast and numba ({e})") from e


def search(pres, cfg=None, **overrides):
    """Best-first search from ``pres`` (a ``Presentation`` or relator strings) under ``cfg`` (with ``overrides``).

    A start with ``|det| != 1`` is never AC-trivial, so a search that ends on a state of length-1 relators that is
    not the trivial presentation (``(X, X)``) reports unsolved.
    """
    cfg = (cfg or SearchConfig()).replace(**overrides)
    pres = as_presentation(pres)
    t0 = time.perf_counter()
    res = backend(cfg.backend).run(pres.normal(cfg.cyclic), cfg)
    res.stats.update(backend=cfg.backend, seconds=time.perf_counter() - t0)
    if res.solved and not res.end.is_trivial():
        return replace(res, solved=False, path=None, end=None, depth=None)
    if res.path is not None:
        from ..verify.replay import replay
        replay(pres, res.path, cyclic=cfg.cyclic, cap=cfg.cap)
    return res
