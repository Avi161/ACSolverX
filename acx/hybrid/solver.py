"""``solve``: the cascade (stages A-C), then the best-first search, then the replayed elementary path.

A solve is a ``HybridResult`` whose ``steps`` are typed: an ``ac_path`` has AC moves and automorphisms of F2 only,
a ``stable_cert`` also has higher-rank steps. ``certify`` writes either as elementary moves and ``acx.verify`` replays them.
"""
import time
from dataclasses import dataclass, field, replace

from ..core.config import parse_cap
from ..core.moves import Move
from ..core.words import Presentation
from ..verify.replay import abs_det
from .capwatch import blank_records
from .cascade import Aut, Budget, Run, cascade
from .certify import certify
from .frontier import BACKENDS
from .search import search


@dataclass(frozen=True)
class HybridConfig:
    """The hybrid's settings; ``r2_cap``, ``dyn_cap`` and ``slack`` are the three limits the cap counters watch."""

    budget: int = 1000                # work units
    penalty: int = 5                  # priority letters per generator above two
    dyn_ratio: float = 0.5            # higher-rank pops <= dyn_ratio * rank-two pops + 20
    dyn_cap: int | None = 8           # longest relator a higher-rank product or elimination may create; None = uncapped
    slack: int | None = 8             # higher-rank total-length ceiling above the search root; None = no ceiling
    min_uses: int = 2                 # a defined digram must occur this often
    r2_cap: int | str | None = "parent"   # rank-two relator cap: "parent" (the parent's total length), an int, or None (uncapped)
    backend: str = "fast"             # rank-two expansion: "spec" (pure Python) | "fast" (numba)
    certify: bool = True              # write out and replay the elementary path

    def __post_init__(self):
        if self.backend not in BACKENDS:
            raise ValueError(f"backend {self.backend!r} not in {BACKENDS}")
        if isinstance(self.dyn_ratio, bool) or not isinstance(self.dyn_ratio, (int, float)) or not self.dyn_ratio >= 0:
            raise ValueError(f"dyn_ratio must be a number >= 0, got {self.dyn_ratio!r}")
        object.__setattr__(self, "r2_cap", parse_cap(self.r2_cap, "r2_cap", keep=("parent",)))
        object.__setattr__(self, "dyn_cap", parse_cap(self.dyn_cap, "dyn_cap"))
        object.__setattr__(self, "slack", parse_cap(self.slack, "slack", low=0))

    def replace(self, **kw):
        """A copy with the given fields changed."""
        return replace(self, **kw)


@dataclass(frozen=True)
class HybridResult:
    """What ``solve`` returns. ``stats``: ``pops``, ``dyn_pops``, ``max_rank``, ``dyn_rejected``, ``seconds`` and the
    18 cap-counter fields of ``capwatch``."""

    solved: bool
    stage: str | None                 # "terminal", "B", "C" (cascade) or "H" (search)
    units: int
    steps: tuple                      # the certificate from the canonical start: Move / Aut / dyn dicts
    kind: str | None                  # "ac_path" or "stable_cert"
    path: tuple | None = None         # elementary moves on the presentation, replayed (cfg.certify)
    stats: dict = field(default_factory=dict)


def solve(pres, cfg=None, **overrides):
    """Solve ``pres`` (a ``Presentation`` or two relator strings), with ``cfg`` and ``overrides`` of its fields."""
    cfg = (cfg or HybridConfig()).replace(**overrides)
    if not isinstance(pres, Presentation):
        pres = Presentation.parse(*pres)
    if pres.n_gen != 2 or len(pres.rels) != 2:
        raise ValueError("the hybrid solves balanced two-generator presentations")
    start = time.perf_counter()
    stats = blank_records(cfg)                  # the cascade has no caps; a search replaces these
    if abs_det(pres) != 1:                      # |det| is an AC invariant: no path starts here, the cascade needs 1
        stats["seconds"] = time.perf_counter() - start
        return HybridResult(False, None, 0, (), None, stats=stats)
    run = Run(pres.rels, cfg.budget)
    try:
        stage = cascade(run)
    except Budget:                              # the cascade spent the whole budget
        stats["seconds"] = time.perf_counter() - start
        return HybridResult(False, None, cfg.budget, (), None, stats=stats)
    if stage is not None:
        solved, steps, units = True, tuple(run.steps), 1 if stage == "terminal" else run.units
    else:
        solved, steps, stats = search(run, cfg, cfg.budget - run.units)
        steps, units, stage = tuple(run.steps) + steps, min(run.units + stats["pops"], cfg.budget), "H"
    stats["seconds"] = time.perf_counter() - start
    if not solved:
        return HybridResult(False, None, units, (), None, stats=stats)
    kind = "stable_cert" if any(isinstance(s, dict) for s in steps) else "ac_path"
    path = tuple(certify(pres, steps)) if cfg.certify else None
    return HybridResult(True, stage, units, steps, kind, path, stats)


def encode_steps(steps):
    """JSON form of a certificate: ``[i, j, s, k1, k2]``, ``{"aut": k}`` or the dyn dict (lists for tuples)."""
    def js(x):
        if isinstance(x, dict):
            return {str(k): js(v) for k, v in x.items()}
        return [js(v) for v in x] if isinstance(x, (tuple, list)) else x
    return [{"aut": s.k} if isinstance(s, Aut) else js(s) if isinstance(s, dict) else list(s) for s in steps]


def decode_steps(items):
    """Inverse of ``encode_steps``."""
    def tup(x):
        return tuple(map(tup, x)) if isinstance(x, list) else x

    def dyn(d):
        ev = {k: tup(v) for k, v in d["event"].items()}
        rl = d["relabel"] and {k: {int(g): v for g, v in m.items()} for k, m in d["relabel"].items()}
        return {"op": "dyn", "event": ev, "relabel": rl, "after": tup(d["after"])}
    return tuple(Move(*s) if isinstance(s, list) else Aut(s["aut"]) if "aut" in s else dyn(s) for s in items)
