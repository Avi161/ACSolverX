"""The output options of a run config: ``path`` (keep and verify each solve's path), ``fields`` (the keys written)."""
from .caps import CAP_KEYS

# Every key a record can hold: the common ones (``methods.record``, plus the ``error`` and timings ``execute`` adds),
# what single methods add, and the cap counters.
COMMON_KEYS = ("id", "solved", "kind", "aut_assisted", "cost", "sub_moves", "elem_moves", "path", "elementary",
               "verified", "error", "seconds", "cpu_seconds")
EXTRA_KEYS = ("rep", "image", "steps", "stage", "rank", "skipped")
RECORD_KEYS = frozenset(COMMON_KEYS + EXTRA_KEYS + CAP_KEYS)
ALWAYS_KEPT = ("id", "solved", "error")        # whatever ``fields`` says: a failed row must say so
PATH_SWITCHES = (("search", "capture_path"), ("hybrid", "certify"), ("ngen", "lift"))      # set from ``path``


def keeps_path(cfg):
    """``path`` (default true): store each solve's path and replay it on the row."""
    return cfg.get("path", True)


def check_output(cfg):
    """``ValueError`` unless ``path`` is a bool, ``fields`` a list of record keys, the methods' own path switches are
    left to ``path``, and the method honours both options."""
    if not isinstance(cfg.get("path", True), bool):
        raise ValueError(f"path must be true or false, got {cfg['path']!r}")
    fields = cfg.get("fields", [])
    if not (isinstance(fields, list) and all(isinstance(key, str) for key in fields)):
        raise ValueError(f"fields must be a list of record keys, got {fields!r}")
    unknown = set(fields) - RECORD_KEYS
    if unknown:
        raise ValueError(f"unknown record keys in fields: {sorted(unknown)}")
    for section, key in PATH_SWITCHES:
        if key in cfg.get(section, {}):
            raise ValueError(f"{section}.{key} follows the top-level path: set path instead")
    if cfg["method"] == "rankn" and ("fields" in cfg or not keeps_path(cfg)):
        raise ValueError("rankn writes its own row files (acx.ngen.sweep): path and fields do not apply to it")


def shape(rec, cfg):
    """``rec`` as the options ask: ``verified`` only for a solve whose path was kept (the methods replay it), no
    certificate without ``path``, and only the keys of ``fields`` when it is set."""
    keep_path = keeps_path(cfg)
    rec["verified"] = rec["solved"] and keep_path
    if not keep_path:
        rec.update(path=None, elementary=None)
        rec.pop("steps", None)
    if "fields" in cfg:
        rec = {key: value for key, value in rec.items() if key in ALWAYS_KEPT or key in cfg["fields"]}
    return rec
