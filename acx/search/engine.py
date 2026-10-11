"""One search API over two backends: ``search(presentation, cfg) -> Result``.

``cfg.backend = "spec"`` runs ``acx.search.spec`` (pure Python, the reference);
``"fast"`` runs ``acx.search.fast`` (numba; imported lazily). Both must return
the same ``Result`` for the same input and config: the same pop sequence, the
same path, the same ``PARITY_STATS``. The order that makes this possible is a
strict total order on heap entries::

    (priority(state), depth, state_key(state))

* ``priority``: ``acx.core.priority`` (int for ``length``, float for ``s20_mk2``).
* ``depth``: the root is 0; a child gets its first discoverer's depth + 1 and is
  never re-pushed (dedup on discovery, no decrease-key). Shallower first.
* ``state_key``: ``acx.core.words.state_key`` -- the relators' order-preserving
  codes (``X=1 < Y=2 < x=3 < y=4``) compared as tuples; at two generators this
  is main's ``(r1_str, r2_str)`` string order. States are unique, so no
  insertion counter is needed and the pop order is independent of the heap
  implementation.

Every solved path is replayed through ``acx.verify.replay`` before it is
returned; a backend that emits an invalid path raises here.
"""
import importlib
import time
from dataclasses import dataclass, field

from ..core.config import SearchConfig
from ..core.words import Presentation

# Stats every backend must report with identical values.
PARITY_STATS = ("discovered", "cap_rejected", "min_total", "max_total",
                "max_total_expanded", "max_expanded")


class BackendUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class Result:
    solved: bool
    pops: int                       # states popped, the solved one included (main's nodes_explored)
    path: tuple | None              # tuple of Move from ``start`` when solved and captured
    start: Presentation             # the reduced canonical start the path replays from
    end: Presentation | None        # the popped all-length-1 state, when solved
    stats: dict = field(default_factory=dict)
    trace: tuple | None = None      # popped states as tuples of relator strings (cfg.trace)

    @property
    def path_length(self):
        return None if self.path is None else len(self.path)


def as_presentation(pres):
    if isinstance(pres, Presentation):
        return pres
    return Presentation.parse(*pres)


def backend(name):
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
    """Best-first search from ``pres`` (a ``Presentation`` or relator strings)."""
    cfg = (cfg or SearchConfig()).replace(**overrides) if overrides else (cfg or SearchConfig())
    pres = as_presentation(pres)
    start = pres.reduced(cfg.cyclic).canonical()
    t0 = time.perf_counter()
    res = backend(cfg.backend).run(start, cfg)
    res.stats.update(backend=cfg.backend, seconds=time.perf_counter() - t0)
    if res.path is not None:
        from ..verify.replay import replay
        replay(pres, res.path, cyclic=cfg.cyclic, cap=cfg.cap)
    return res
