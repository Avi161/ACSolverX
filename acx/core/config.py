"""``SearchConfig``: one frozen dataclass for every search, loadable from TOML.

    cfg = SearchConfig.load("configs/x.toml", ["budget=100000", "cap=none"])

TOML keys are the field names, at the top level or under ``[search]``. An
override is ``key=value`` with a TOML value (``48``, ``true``, ``"s20_mk2"``)
or a bare word (``s20_mk2``). ``cap = "none"`` means uncapped (TOML has no null);
every relator cap of every config goes through ``parse_cap``. Unknown keys are an
error, never ignored.
"""
import tomllib
from dataclasses import asdict, dataclass, fields, replace

from .priority import PRIORITIES

BACKENDS = ("spec", "fast")


@dataclass(frozen=True)
class SearchConfig:
    priority: str = "length"     # "length" | "s20_mk2"
    cap: int | None = 24         # per-relator length cap on generated children; None = uncapped
    budget: int = 10_000         # maximum pops
    backend: str = "spec"        # "spec" (pure Python reference) | "fast" (numba)
    capture_path: bool = True    # return the move path of a solve
    cyclic: bool = True          # cyclic reduction of children (main's default)
    trace: bool = False          # return the popped states in order (parity tests)

    def __post_init__(self):
        object.__setattr__(self, "cap", parse_cap(self.cap))
        if self.priority not in PRIORITIES:
            raise ValueError(f"priority {self.priority!r} not in {sorted(PRIORITIES)}")
        if self.backend not in BACKENDS:
            raise ValueError(f"backend {self.backend!r} not in {BACKENDS}")
        if not (type(self.budget) is int and self.budget > 0):
            raise ValueError(f"budget must be a positive int, got {self.budget!r}")

    def replace(self, **kw):
        return replace(self, **kw)

    def with_overrides(self, items=()):
        return self.from_dict({**asdict(self), **dict(parse_override(s) for s in items)})

    @classmethod
    def from_dict(cls, d):
        names = {f.name for f in fields(cls)}
        bad = set(d) - names
        if bad:
            raise ValueError(f"unknown SearchConfig keys {sorted(bad)}")
        return cls(**d)

    @classmethod
    def load(cls, path=None, overrides=()):
        d = {}
        if path is not None:
            with open(path, "rb") as f:
                d = tomllib.load(f)
            d = d.get("search", d)
        cfg = cls.from_dict(d)
        return cfg.with_overrides(overrides)


def parse_cap(value, name="cap", low=1, keep=()):
    """A length limit: an int ``>= low``, or ``None`` / ``"none"`` (no limit); strings in ``keep`` pass as they are.

    The one reading of a cap for every config (``SearchConfig.cap``, ``HybridConfig.r2_cap`` and ``dyn_cap``,
    ``CoVConfig.max_len`` and ``cap_headroom``, the RL beam's ``cap``). Bools and ``0`` (for a cap) raise.
    """
    if value is None or (isinstance(value, str) and value.lower() == "none"):
        return None
    if isinstance(value, str) and value in keep:
        return value
    if type(value) is int and value >= low:
        return value
    allowed = " or ".join([f"an int >= {low}", "'none'", *map(repr, keep)])
    raise ValueError(f"{name} must be {allowed}, got {value!r}")


def parse_override(item):
    """``'key=value'`` -> ``(key, value)``, the value read as TOML, else as a bare string."""
    key, sep, raw = item.partition("=")
    if not sep:
        raise ValueError(f"override {item!r} is not key=value")
    key, raw = key.strip(), raw.strip()
    try:
        value = tomllib.loads(f"v = {raw}")["v"]
    except tomllib.TOMLDecodeError:
        value = raw
    return key, value
