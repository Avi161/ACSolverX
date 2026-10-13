"""What a sweep run is: its config, the word pool it implies and the identity stamped into every row file."""
import hashlib
import json
from dataclasses import asdict, dataclass, fields

from ...core.capcount import FIELDS
from ...core.config import SearchConfig, is_number, reject_unknown, require_bool
from ...core.words import fmt
from .words import pool

COUNTERS = FIELDS[1:]                       # the cap counters of acx.core.capcount (FIELDS[0] is the cap itself)


class SweepError(RuntimeError):
    """A row file from another run, or a control that disagrees with its null stabilisation."""


@dataclass(frozen=True)
class SweepConfig:
    """``search`` (a SearchConfig, LENGTH only) and ``[rankn]``: ``extra`` added generators, words of length
    ``min_len..max_len``, ``inverse`` (search w^-1) and ``sample`` (fraction of solved paths kept)."""
    search: SearchConfig
    extra: int = 1
    min_len: int = 1
    max_len: int = 4
    inverse: bool = False
    sample: float = 0.002

    def __post_init__(self):
        """Refuse what the stored arrays or the start relators cannot hold, and anything but LENGTH."""
        search = self.search
        require_bool(self.inverse, "rankn.inverse")
        if type(self.extra) is not int or self.extra not in (1, 2, 3):
            raise ValueError(f"rankn.extra must be 1, 2 or 3, got {self.extra!r}")
        lengths_ok = type(self.min_len) is int and type(self.max_len) is int and 1 <= self.min_len <= self.max_len
        if not lengths_ok:
            raise ValueError(f"rankn needs 1 <= min_len <= max_len, got {self.min_len!r}, {self.max_len!r}")
        if search.priority != "length":
            raise ValueError("the sweep supports priority = 'length' only (s20_mk2 is defined for two generators)")
        if search.budget > 65_535:
            raise ValueError("the sweep stores pops as uint16: search.budget must be at most 65535")
        if search.cap is not None and 1 + self.max_len > search.cap:
            raise ValueError(f"search.cap {search.cap} is below the start relator Z.w of length {1 + self.max_len}")
        if not (is_number(self.sample) and 0 <= self.sample <= 1):
            raise ValueError(f"rankn.sample must be in [0, 1], got {self.sample!r}")

    @classmethod
    def from_cfg(cls, cfg):
        """From a runner-style dict with sections ``search`` and ``rankn``; unknown keys are errors.

        As for every method of the runner, the backend defaults to ``fast`` (``SearchConfig`` alone says ``spec``).
        """
        rankn = dict(cfg.get("rankn", {}))
        reject_unknown(rankn, {f.name for f in fields(cls) if f.name != "search"}, "rankn")
        search = SearchConfig.from_dict({"backend": "fast", **cfg.get("search", {}), "capture_path": True})
        return cls(search=search, **rankn)

    @classmethod
    def from_key(cls, key):
        """From ``key()``, the form stored in a result directory's ``config.json``."""
        rankn = {k: v for k, v in key.items() if k != "search"}
        return cls.from_cfg({"search": key["search"], "rankn": rankn})

    def key(self):
        """What a result directory holds; backend, capture and trace are left out (both backends give the same rows)."""
        key = asdict(self)
        key["search"] = {k: v for k, v in key["search"].items() if k not in ("backend", "capture_path", "trace")}
        return key


def words_of(sc):
    """The word pool of a config."""
    return pool(sc.min_len, sc.max_len, sc.inverse)


def ident_of(sc, row_id, pres):
    """What a row file must say about itself: its row, the config and the word pool."""
    pool_hash = hashlib.md5(",".join(map(fmt, words_of(sc))).encode()).hexdigest()
    ident = {"id": row_id, "r1": fmt(pres.rels[0]), "r2": fmt(pres.rels[1]), "config": sc.key(), "pool": pool_hash}
    return json.dumps(ident, sort_keys=True, separators=(",", ":"))
