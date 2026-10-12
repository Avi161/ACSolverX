"""CoV-then-search: try the CoV images of a row in a fixed order within a total budget.

For one row the images of ``acx.cov.enumerate_images`` (module ``cov`` explains the
transform and the family ``subnc2pxysb``) are searched one after another with
``acx.search`` on either backend (``cfg.search.backend``), each with at most
``cfg.search.budget`` pops, until ``cfg.total_budget`` pops are spent. There is
no ranking: the order is the enumeration order, optionally after the row itself.
Two images (or an image and the row) with the same reduced canonical start are
searched once.

Outcomes are typed, and kept apart:

* ``ac_path``: moves that replay on the **original row** and end trivial. The
  search of the row itself (``cfg.control``) gives one (S-moves). A solved image
  that lies in the row's Aut(F2) orbit (a pure relabel, which most images are)
  gives one too: the search leg is carried to the row by ``acx.aut.transport``
  (elementary AC moves), and counts only because that replays on the row.
* ``stable_cert``: a solved image outside the row's orbit. It certifies that the
  row is **stably** AC-trivial (Lemma 11 steps, then an AC path on the image),
  not that it has an AC path. ``Outcome.path`` is the search leg on the image
  and ``image.steps`` the transform; ``acx.cov.check_cert`` replays both.

**Cap counters.** Every leg is a plain ``acx.search`` with its own cap and its own counters
(``acx.core.capcount``); the row's ``stats`` hold their aggregate under the usual names: ``cap`` is
``search.cap`` (the row's leg; image legs follow from it and ``cap_headroom``), ``cap_dropped`` and
``cap_would_pop`` are sums over the legs tried, ``cap_dropped_min_total`` and ``cap_needed`` minima over
them (``cap_needed`` in absolute letters of the binding leg's own cap), ``cap_first_bind`` is a pop number
of the row (the pops spent on earlier legs plus the first binding leg's) and ``cap_legs_bound`` the
number of legs with ``cap_would_pop > 0``. When no leg binds every leg is the same at any larger cap, so
the row spends the same pops. ``max_len`` is a filter on which images exist, not a heap cap, so it has no
counter (``stats["images"]`` already reports it).

The cap of an image's search is ``max(search.cap, longest image relator (as
written) + cap_headroom)``: an image is usually longer than the row, and a relator
sitting at the cap cannot grow over the hump.  With this policy the 6,722 images of
bench60 + reach_tier_6 solve 890 (orbit) + 169 (moved) at 100 pops each, the
source's published numbers. ``cap_headroom=None`` runs every image at
``search.cap`` exactly (a cap-matched comparison with plain search); the row
itself always runs at ``search.cap``.

Source of the policy: ``origin/cov/all-subsets-sweep:experiments/stable_ac/cov/run/run_cov.py``
(per-image cap ``max(24, longest + 16)``). The selection key, abel top-3,
nonsymmetric beam and mu-ladder are not part of this module.
"""
import time
from dataclasses import dataclass, field, replace

from ..aut import automorphism, transport
from ..core.capcount import blank, combine
from ..core.config import SearchConfig, parse_cap
from ..search import Result, search
from ..search.engine import as_presentation
from ..verify.replay import replay
from .cov import MAX_LEN, CoVImage, check_cert, enumerate_images

CAP_FIELDS = tuple(blank())


@dataclass(frozen=True)
class CoVConfig:
    search: SearchConfig = SearchConfig(budget=1_000)   # per-search config; ``budget`` is the pops per image
    total_budget: int = 10_000          # pops over all searches of one row
    control: bool = True                # search the row itself first
    cap_headroom: int | None = 16       # see the module docstring
    max_len: int | None = MAX_LEN       # CoV outputs longer than this are not images (family rule)
    until: str = "solve"                # "solve": stop at the first solve; "ac_path": go on past stable certs

    def __post_init__(self):
        if self.until not in ("solve", "ac_path"):
            raise ValueError(f"until {self.until!r} not in ('solve', 'ac_path')")
        if not (type(self.total_budget) is int and self.total_budget > 0):
            raise ValueError(f"total_budget must be a positive int, got {self.total_budget!r}")
        object.__setattr__(self, "cap_headroom", parse_cap(self.cap_headroom, "cap_headroom", low=0))
        object.__setattr__(self, "max_len", parse_cap(self.max_len, "max_len"))

    def replace(self, **kw):
        return replace(self, **kw)

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        return cls(search=SearchConfig.from_dict({"budget": 1_000, **d.pop("search", {})}), **d)


@dataclass(frozen=True)
class Outcome:
    kind: str                # "ac_path" | "stable_cert"
    image: CoVImage | None   # None: the row itself
    result: Result           # the search leg
    path: tuple              # ac_path: moves that replay on the row; stable_cert: the leg on ``image.pres``
    cap: int | None          # cap of the search leg
    cyclic: bool = True      # the search leg's reduction


@dataclass(frozen=True)
class CoVResult:
    outcomes: tuple          # Outcome, in the order found
    pops: int
    stats: dict = field(default_factory=dict)

    def first(self, kind):
        return next((o for o in self.outcomes if o.kind == kind), None)

    @property
    def ac_path(self):
        return self.first("ac_path")

    @property
    def stable_cert(self):
        return self.first("stable_cert")

    @property
    def solved(self):
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


def run(pres, cfg=None, **overrides):
    """Search ``pres`` (a 2-generator ``Presentation`` or relator strings) and its CoV images."""
    cfg = (cfg or CoVConfig()).replace(**overrides)
    pres = as_presentation(pres)
    s, t0 = cfg.search, time.perf_counter()
    images = enumerate_images(pres, cfg.max_len)
    cands = ([None] if cfg.control else []) + list(images)
    seen, outcomes = set(), []
    pops = dups = tried = 0
    legs = []                           # (cap counter record, pops spent before the leg)
    for img in cands:
        left = cfg.total_budget - pops
        if left <= 0:
            break
        start = (pres if img is None else img.pres).reduced(s.cyclic).canonical()
        if start in seen:
            dups += 1
            continue
        seen.add(start)
        cap = s.cap
        if img is not None and cap is not None and cfg.cap_headroom is not None:
            cap = max(cap, max(map(len, img.pres.rels)) + cfg.cap_headroom)
        res = search(start, s.replace(budget=min(s.budget, left), cap=cap, capture_path=True))
        legs.append(({f: res.stats[f] for f in CAP_FIELDS}, pops))
        tried, pops = tried + 1, pops + res.pops
        if res.solved:
            outcomes.append(_typed(pres, img, res, cap, s.cyclic))
            verify(pres, outcomes[-1])
            if cfg.until == "solve" or outcomes[-1].kind == "ac_path":
                break
    caps = combine(legs) if legs else blank()
    caps["cap"] = s.cap
    stats = {"images": len(images), "tried": tried, "duplicates": dups, **caps,
             "cap_legs_bound": sum(1 for rec, _ in legs if rec["cap_would_pop"]), "seconds": time.perf_counter() - t0}
    return CoVResult(tuple(outcomes), pops, stats)
