"""n-generator search: best-first substitution search on any number of generators, with optional SAC.

The search itself is ``acx.search.search``: its spec and fast backends already
run any number of relators, step for step identical (``tests/test_ngen.py``
pins this for the triangle roots). They replace ``solvern`` / ``solvern_fast``
(``origin/worktree-hsearch-hyper:experiments/stable_ac/``: ``solvern.py`` blob
5d1dd1ee, commit eff4b4c7, identical on ``origin/cov/all-subsets-sweep``;
``solvern_fast.py`` blob e965386b, commit a4024828 (added in 848e673d): the numba twin, same pop
order, 4.6-5.9x faster) and ``greedy_nrel`` (``origin/test/stable-ac-moves:
experiments/stable_ac/one_generator/``, blob e12d2dd2, commit 658db0c0: 364 ->
3,300 nodes/s with ``expand_fast``). ``solvern`` is the newer, and the one whose
pop order equals the two-generator spec (its ``search_n`` is ``acx.search.spec``
with more relators); ``greedy_nrel`` adds nothing to it. Only the LENGTH
priority exists past two generators (``s20_mk2`` is two-generator).

``solve(pres, cfg)`` has two modes:

* ``cfg.sac = False``: search ``pres`` itself, whatever its rank. A solve is an
  ``ac_path``: S-moves that replay on ``pres`` (``normalize=True``).
* ``cfg.sac = True`` (default): triangulate first (``acx.ngen.sac``), search the
  root, and on a solve return the elementary stable path from ``acx.ngen.lift``
  (``cfg.lift``). That is a ``stable_cert``: it uses stabilisations, so it is
  stable AC triviality of ``pres``, never an AC path; ``replay(pres, moves,
  normalize=False)`` checks it. A presentation already of relator length <= 3
  needs no definition and yields an ``ac_path``.
"""
from dataclasses import dataclass, field

from ..core.config import SearchConfig
from ..search import search
from ..search.engine import Result, as_presentation
from ..verify.replay import replay
from .lift import lift
from .sac import Sac, triangulate


@dataclass(frozen=True)
class NGenConfig:
    search: SearchConfig = field(default_factory=SearchConfig)
    sac: bool = True      # triangulate (relators of length <= 3) before searching
    lift: bool = True     # expand a SAC solve into a replayable elementary path


@dataclass(frozen=True)
class NGenResult:
    solved: bool
    kind: str | None          # "ac_path" | "stable_cert" | None (unsolved)
    search: Result            # the search on ``root``
    sac: Sac | None
    moves: tuple | None       # replayable on the input (``verify``); None without a captured path or lift

    @property
    def rank(self):
        return self.search.start.n_gen


def solve(pres, cfg=None):
    cfg = cfg or NGenConfig()
    pres = as_presentation(pres)
    sac = triangulate(pres) if cfg.sac else None
    root = sac.root if sac else pres
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
    """Replay ``res.moves`` on ``pres`` (raises ``ReplayError``); an ``ac_path`` is replayed with the search's normal form."""
    return replay(as_presentation(pres), res.moves, cyclic=cyclic, normalize=res.kind == "ac_path")
