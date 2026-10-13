"""CoV-then-search: the row, then its CoV images in a fixed order, searched within one total budget.

Each image of ``acx.cov.enumerate_images`` is a plain ``acx.search`` (``cfg.search.backend``); there is no ranking.
``run`` documents the typed outcomes, the per-image cap and the cap counters.
"""
import time
from dataclasses import dataclass, field, replace

from ..aut import automorphism, transport
from ..core.capcount import blank, combine
from ..core.config import SearchConfig, parse_cap
from ..search import Result, search
from ..search.engine import as_presentation
from ..verify.replay import replay
from .certificate import check_cert
from .family import FAMILIES, MAX_LEN
from .images import CoVImage, enumerate_images

CAP_FIELDS = tuple(blank())


@dataclass(frozen=True)
class CoVConfig:
    """The settings of ``run``; ``search.budget`` is the pops per leg, ``total_budget`` the pops per row."""
    search: SearchConfig = SearchConfig(budget=1_000)   # per-search config; ``budget`` is the pops per image
    total_budget: int = 10_000          # pops over all searches of one row
    control: bool = True                # search the row itself first
    cap_headroom: int | None = 16       # see ``run``
    max_len: int | None = MAX_LEN       # CoV outputs longer than this are not images (family rule)
    until: str = "solve"                # "solve": stop at the first solve; "ac_path": go on past stable certs
    family: str = "subnc2pxysb"         # the z-family (``acx.cov.family``): "subnc2pxysb" or "suballpxyb8"

    def __post_init__(self):
        if self.until not in ("solve", "ac_path"):
            raise ValueError(f"until {self.until!r} not in ('solve', 'ac_path')")
        if self.family not in FAMILIES:
            raise ValueError(f"family {self.family!r} not in {FAMILIES}")
        if not (type(self.total_budget) is int and self.total_budget > 0):
            raise ValueError(f"total_budget must be a positive int, got {self.total_budget!r}")
        object.__setattr__(self, "cap_headroom", parse_cap(self.cap_headroom, "cap_headroom", low=0))
        object.__setattr__(self, "max_len", parse_cap(self.max_len, "max_len"))

    def replace(self, **kw):
        """A copy with the given fields changed."""
        return replace(self, **kw)


@dataclass(frozen=True)
class Outcome:
    """One solved leg, typed (``run`` explains ``ac_path`` and ``stable_cert``)."""
    kind: str                # "ac_path" | "stable_cert"
    image: CoVImage | None   # None: the row itself
    result: Result           # the search leg
    path: tuple              # ac_path: moves that replay on the row; stable_cert: the leg on ``image.pres``
    cap: int | None          # cap of the search leg
    cyclic: bool = True      # the search leg's reduction


@dataclass(frozen=True)
class CoVResult:
    """The outcomes found, the pops spent and ``stats`` (images, legs tried, cap counters, seconds)."""
    outcomes: tuple          # Outcome, in the order found
    pops: int
    stats: dict = field(default_factory=dict)

    def first(self, kind):
        """The first outcome of this ``kind``, or None."""
        return next((o for o in self.outcomes if o.kind == kind), None)

    @property
    def ac_path(self):
        """The first ``ac_path`` outcome, or None."""
        return self.first("ac_path")

    @property
    def stable_cert(self):
        """The first ``stable_cert`` outcome, or None."""
        return self.first("stable_cert")

    @property
    def solved(self):
        """Some leg solved."""
        return bool(self.outcomes)


def verify(pres, outcome):
    """Replay an outcome on the row it claims to solve; raises ``ReplayError`` if it does not hold."""
    if outcome.kind == "stable_cert":
        check_cert(pres, outcome.image.steps, outcome.path, outcome.cap, outcome.cyclic)
    else:
        replay(pres, outcome.path, outcome.cyclic, normalize=not (outcome.path and isinstance(outcome.path[0], dict)))


def _typed(pres, img, res, cap, cyclic):
    """The outcome of a solved search: the row's own ``ac_path``, a transported ``ac_path``, or a ``stable_cert``."""
    if img is None or res.start == pres.reduced(cyclic).canonical():     # the row itself, as written or as an image
        return Outcome("ac_path", img, res, res.path, cap, cyclic)
    try:
        phi = automorphism(pres, img.pres)
    except RuntimeError:                                                 # Aut level set over its cap: no orbit answer
        phi = None
    if phi is None:
        return Outcome("stable_cert", img, res, res.path, cap, cyclic)
    return Outcome("ac_path", img, res, tuple(transport(pres, phi, res.path, res.start, cyclic)), cap, cyclic)


def _leg_cap(cfg, img):
    """The cap of one leg: the row's own, or an image's written length plus ``cap_headroom`` if that is larger."""
    cap = cfg.search.cap
    if img is not None and cap is not None and cfg.cap_headroom is not None:
        cap = max(cap, max(map(len, img.pres.rels)) + cfg.cap_headroom)
    return cap


def _row_caps(legs, cap):
    """The cap counters of the whole row from the per-leg records (``run`` explains the fields)."""
    caps = combine(legs) if legs else blank()
    caps["cap"] = cap
    caps["cap_legs_bound"] = sum(1 for record, _ in legs if record["cap_would_pop"])
    return caps


def run(pres, cfg=None, **overrides):
    """Search ``pres`` (a 2-generator ``Presentation`` or relator strings) and its CoV images.

    Each leg (the row if ``cfg.control``, then every image) gets at most ``cfg.search.budget`` pops until
    ``cfg.total_budget`` are spent; legs with the same reduced canonical start run once. With ``until = "solve"`` the
    run stops at the first solve, with ``"ac_path"`` at the first ``ac_path``. Outcomes are typed:

    * ``ac_path``: moves that replay on the **row**. The row's own search gives S-moves; a solved image in the row's
      Aut(F2) orbit (a pure relabel, which most images are) gives elementary moves, its leg carried over by
      ``acx.aut.transport`` and counted only because they replay on the row.
    * ``stable_cert``: a solved image outside the orbit. It certifies that the row is **stably** AC-trivial, not
      that it has an AC path: ``Outcome.path`` is the leg on ``image.pres`` and ``image.steps`` the transform
      (``acx.cov.check_cert`` replays both).

    The cap of an image's leg is ``max(search.cap, longest image relator as written + cap_headroom)``, since a relator
    at the cap cannot grow over the hump; ``cap_headroom = None`` runs images at ``search.cap`` and the row always does.

    ``stats`` carry the cap counters of ``acx.core.capcount`` aggregated over the legs: ``cap`` is ``search.cap``,
    ``cap_dropped`` and ``cap_would_pop`` are sums, ``cap_dropped_min_total`` and ``cap_needed`` minima (``cap_needed``
    in letters of the binding leg's own cap), ``cap_first_bind`` is a pop number of the row (pops of earlier legs plus
    the first binding leg's) and ``cap_legs_bound`` counts the legs with ``cap_would_pop > 0``. When no leg binds,
    every larger cap gives the same run. ``max_len`` only decides which images exist (``stats["images"]``): no counter.
    """
    cfg = (cfg or CoVConfig()).replace(**overrides)
    pres = as_presentation(pres)
    search_cfg, started = cfg.search, time.perf_counter()
    images = enumerate_images(pres, cfg.max_len, cfg.family)
    legs_to_try = ([None] if cfg.control else []) + list(images)        # None: the row itself
    seen_starts, outcomes = set(), []
    pops = duplicates = tried = 0
    legs = []                           # (cap counter record, pops spent before the leg)
    for img in legs_to_try:
        pops_left = cfg.total_budget - pops
        if pops_left <= 0:
            break
        raw = pres if img is None else img.pres
        start = raw.reduced(search_cfg.cyclic).canonical()
        if start in seen_starts:
            duplicates += 1
            continue
        seen_starts.add(start)
        cap = _leg_cap(cfg, img)
        res = search(raw, search_cfg.replace(budget=min(search_cfg.budget, pops_left), cap=cap, capture_path=True))
        legs.append(({f: res.stats[f] for f in CAP_FIELDS}, pops))
        tried, pops = tried + 1, pops + res.pops
        if res.solved:
            outcomes.append(_typed(pres, img, res, cap, search_cfg.cyclic))
            verify(pres, outcomes[-1])
            if cfg.until == "solve" or outcomes[-1].kind == "ac_path":
                break
    stats = {"images": len(images), "tried": tried, "duplicates": duplicates, **_row_caps(legs, search_cfg.cap),
             "seconds": time.perf_counter() - started}
    return CoVResult(tuple(outcomes), pops, stats)
