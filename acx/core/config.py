"""``SearchConfig``, the one frozen dataclass every search takes, and the shared value checks ``parse_cap``,
``require_bool`` and ``parse_override``."""
import tomllib
from dataclasses import asdict, dataclass, fields, replace

from .priority import PRIORITIES

BACKENDS = ("spec", "fast")


@dataclass(frozen=True)
class SearchConfig:
    """The settings of ``acx.search.search``. Build it directly, or ``SearchConfig.load("configs/x.toml",
    ["budget=100000", "cap=none"])``: TOML keys are the field names (top level or under ``[search]``), an override
    is ``key=value`` with a TOML value or a bare word, and ``cap = "none"`` means uncapped. Unknown keys raise."""
    priority: str = "length"     # "length" | "s20_mk2"
    cap: int | None = 24         # per-relator length cap on generated children; None = uncapped
    budget: int = 10_000         # maximum pops
    backend: str = "spec"        # "spec" (pure Python reference) | "fast" (numba)
    capture_path: bool = True    # return the move path of a solve
    cyclic: bool = True          # cyclic reduction of children (the default)
    trace: bool = False          # return the popped states in order (parity tests)

    def __post_init__(self):
        object.__setattr__(self, "cap", parse_cap(self.cap))
        if self.priority not in PRIORITIES:
            raise ValueError(f"priority {self.priority!r} not in {sorted(PRIORITIES)}")
        if self.backend not in BACKENDS:
            raise ValueError(f"backend {self.backend!r} not in {BACKENDS}")
        if not (type(self.budget) is int and self.budget > 0):
            raise ValueError(f"budget must be a positive int, got {self.budget!r}")
        for name in ("capture_path", "cyclic", "trace"):
            require_bool(getattr(self, name), name)

    def replace(self, **changes):
        """A copy with fields changed."""
        return replace(self, **changes)

    def with_overrides(self, items=()):
        """A copy with ``key=value`` strings applied (``parse_override``)."""
        overrides = dict(parse_override(item) for item in items)
        return self.from_dict({**asdict(self), **overrides})

    @classmethod
    def from_dict(cls, values):
        """From a dict of field values; unknown keys raise ``ValueError``."""
        known = {field.name for field in fields(cls)}
        unknown = set(values) - known
        if unknown:
            raise ValueError(f"unknown SearchConfig keys {sorted(unknown)}")
        return cls(**values)

    @classmethod
    def load(cls, path=None, overrides=()):
        """From a TOML file (or the defaults for ``None``) plus ``key=value`` overrides."""
        values = {}
        if path is not None:
            with open(path, "rb") as file:
                values = tomllib.load(file)
            values = values.get("search", values)
        return cls.from_dict(values).with_overrides(overrides)


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


def require_bool(value, name):
    """``value`` if it is a bool. A string such as ``"False"`` (``--set key=False`` is not TOML) would read as true."""
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be true or false, got {value!r}")
    return value


def require_int(value, name, low=1):
    """``value`` if it is an int ``>= low``; a bool, a float or a string raises."""
    if type(value) is not int or value < low:
        raise ValueError(f"{name} must be an int >= {low}, got {value!r}")
    return value


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
