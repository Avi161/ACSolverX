"""n-generator search: ``acx.search.search`` on a presentation of any rank, with optional stable-AC triangulation.

``solve(pres, NGenConfig)``: with ``sac = True`` (default) the presentation is triangulated (``acx.ngen.sac``), the
root is searched and a solve is lifted to elementary stable AC moves (``acx.ngen.lift``), a ``stable_cert``. With
``sac = False`` the presentation itself is searched and a solve is an ``ac_path``. See ``docs/RANK3.md``.
"""
from dataclasses import dataclass, field

from ..core.config import SearchConfig
from ..search import search
from ..search.engine import Result, as_presentation
from ..verify.replay import replay
from .lift import lift
from .sac import Sac, triangulate

MAX_GENERATORS = 127     # a letter code is one byte in the fast backend and in the cap counters' state keys


@dataclass(frozen=True)
class NGenConfig:
    """``search``; ``sac``: triangulate before searching; ``lift``: expand a SAC solve into replayable moves."""
    search: SearchConfig = field(default_factory=SearchConfig)
    sac: bool = True
    lift: bool = True

    def __post_init__(self):
        """SAC always raises the rank past two, and only LENGTH is defined there: refused here, before any run."""
        if self.sac and self.search.priority != "length":
            raise ValueError("ngen with sac = true needs search.priority = 'length': the SAC root has more than two "
                             "generators, and s20_mk2 is defined for two (use sac = false to search as it is)")


@dataclass(frozen=True)
class NGenResult:
    """The outcome of ``solve``: ``kind`` is ``ac_path``, ``stable_cert`` or None; ``moves`` replays on the input."""
    solved: bool
    kind: str | None          # "ac_path" | "stable_cert" | None (unsolved)
    search: Result            # the search on ``root``
    sac: Sac | None
    moves: tuple | None       # replayable on the input (``verify``); None without a captured path or lift

    @property
    def rank(self):
        """Generators of the searched root."""
        return self.search.start.n_gen


def solve(pres, cfg=None):
    """Search ``pres`` (or its SAC root) under ``cfg`` (default ``NGenConfig()``); return an ``NGenResult``."""
    cfg = cfg or NGenConfig()
    pres = as_presentation(pres)
    sac = triangulate(pres) if cfg.sac else None
    root = sac.root if sac and sac.digrams else pres     # no definition: search the input itself (B1, cyclic = false)
    if root.n_gen > MAX_GENERATORS:
        raise ValueError(f"ngen searches at most {MAX_GENERATORS} generators; the root has {root.n_gen}")
    if root.n_gen > 2 and cfg.search.priority != "length":
        raise ValueError("only the length priority is defined past two generators")
    res = search(root, cfg.search)
    if not res.solved:
        return NGenResult(False, None, res, sac, None)
    if not (sac and sac.digrams):
        return NGenResult(True, "ac_path", res, sac, res.path)
    lifted = cfg.lift and res.path is not None
    moves = tuple(lift(pres, sac, res.path, res.start, cfg.search.cyclic)) if lifted else None
    return NGenResult(True, "stable_cert", res, sac, moves)


def verify(pres, res, cyclic=True):
    """Replay ``res.moves`` on ``pres`` (raises ``ReplayError``); an ``ac_path`` uses the search's normal form."""
    return replay(as_presentation(pres), res.moves, cyclic=cyclic, normalize=res.kind == "ac_path")
