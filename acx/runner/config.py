"""Reading a run config (TOML plus overrides), checking it, and building the settings object of its method."""
import os
import tomllib
from dataclasses import fields

from ..core.config import SearchConfig, parse_cap, parse_override
from .output import check_output, keeps_path

# The config sections each method reads; any other section is an error.
SECTIONS = {"greedy": ("search",), "aut": ("search",), "cov": ("search", "cov"), "ngen": ("search", "ngen"),
            "hybrid": ("hybrid",), "rl": ("rl",), "rankn": ("search", "rankn")}
METHODS = tuple(SECTIONS)
TOP_LEVEL_KEYS = {"name", "method", "benchmark", "rows", "workers", "decode", "path", "fields"}
ALL_KEYS = TOP_LEVEL_KEYS | {section for sections in SECTIONS.values() for section in sections}
RL_KEYS = {"width", "steps", "alpha", "cap"}


def load_config(path, overrides=()):
    """The config TOML at ``path`` plus ``key=value`` overrides (dotted keys reach sections: ``search.budget=1000``).

    Top level: ``name`` (the results folder, default the file's stem), ``method``, ``benchmark`` (a name of
    ``acx.data.rows`` or a path), ``rows`` (optional: a slice ``"a:b[:c]"`` or ids ``"3,17"``), ``workers``
    (processes, an int >= 1, default 1) and ``decode`` (a bool, default true: elementary length of S-move paths).
    Two options shape the records (``acx.runner.output``): ``path`` (default true: store each solve's path and replay
    it on the row; false: search without the path, which is faster, with ``path`` and ``elementary`` null,
    ``verified`` false and ``elem_moves`` null where it needs the path; ``sub_moves`` is kept) and ``fields``
    (optional list: write only these record keys, besides ``id``, ``pres``, ``solved`` and ``error``).
    A method reads only its own sections (``SECTIONS``): ``[search]`` is ``SearchConfig``, ``[cov]`` ``CoVConfig``
    and ``[ngen]`` ``NGenConfig`` without their ``search``, ``[hybrid]`` ``HybridConfig``, ``[rl]`` the keywords of
    ``acx.rl.solve.solve``. Any other section, unknown key or invalid value raises ``ValueError`` here, before
    anything is written.
    """
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    cfg.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    for item in overrides:
        _apply_override(cfg, item)
    _check_keys(cfg)
    check_output(cfg)
    method_config(cfg)
    return cfg


def run_config(cfg):
    """``cfg`` as stored with a run (``config.json``, ``summary.json``): without ``rows`` and ``workers``, which may
    differ between the invocations that make up one run."""
    return {key: value for key, value in cfg.items() if key not in ("rows", "workers")}


def _apply_override(cfg, item):
    """Set one ``key=value`` override in ``cfg``; a dotted key creates the sections on its way."""
    key, value = parse_override(item)
    *sections, leaf = key.split(".")
    target = cfg
    for section in sections:
        target = target.setdefault(section, {})
    target[leaf] = value


def _check_keys(cfg):
    """Raise ``ValueError`` for an unknown top-level key, a ``name`` or ``benchmark`` that is not a string, a section
    that is not a table, an unknown method, or a section the method ignores."""
    unknown = set(cfg) - ALL_KEYS
    if unknown:
        raise ValueError(f"unknown config keys {sorted(unknown)}")
    for key in ("name", "benchmark"):
        if key in cfg and not isinstance(cfg[key], str):
            raise ValueError(f'{key} must be a string, got {cfg[key]!r} (quote it: {key}="...")')
    for section in set(cfg) - TOP_LEVEL_KEYS:
        if not isinstance(cfg[section], dict):
            raise ValueError(f"{section} is a section: set its keys ({section}.key=value), got {cfg[section]!r}")
    if cfg.get("method") not in METHODS:
        raise ValueError(f"method {cfg.get('method')!r} not in {METHODS}")
    ignored = set(cfg) - TOP_LEVEL_KEYS - set(SECTIONS[cfg["method"]])
    if ignored:
        raise ValueError(f"method {cfg['method']!r} does not read the sections {sorted(ignored)}")
    if "benchmark" not in cfg:
        raise ValueError("config needs a benchmark")


def method_config(cfg):
    """The method's settings object (a dict of keywords for ``rl``), built from its sections.

    ``ValueError`` on an unknown key or an invalid value. The search backend defaults to ``fast`` (``SearchConfig``
    keeps ``spec`` as its own default; the hybrid's is ``fast`` too). The path switches of the methods
    (``search.capture_path``, ``hybrid.certify``, ``ngen.lift``) are set from the top-level ``path``: a solve is
    replayed exactly when its path is kept.
    """
    method = cfg["method"]
    search_values = {"backend": "fast", **cfg.get("search", {})}     # a run's default backend is numba, not "spec"
    if method == "rankn":
        from ..ngen.sweep import SweepConfig
        return SweepConfig.from_cfg({**cfg, "search": search_values})
    if method == "rl":
        return _rl_keywords(cfg.get("rl", {}))
    if method == "hybrid":
        from ..hybrid import HybridConfig
        return _build(HybridConfig, {**cfg.get("hybrid", {}), "certify": keeps_path(cfg)})
    default_budget = {"budget": 1_000} if method == "cov" else {}
    search = SearchConfig.from_dict({**default_budget, **search_values, "capture_path": keeps_path(cfg)})
    if method == "cov":
        from ..cov import CoVConfig
        return _build(CoVConfig, cfg.get("cov", {}), search=search)
    if method == "ngen":
        return _ngen_config(cfg, search)
    return search                                    # greedy, aut


def _build(cls, values, **fixed):
    """``cls(**fixed, **values)`` for a config dataclass, with unknown keys of ``values`` named in the error."""
    allowed = {f.name for f in fields(cls)} - set(fixed)
    unknown = set(values) - allowed
    if unknown:
        raise ValueError(f"unknown {cls.__name__} keys {sorted(unknown)}")
    return cls(**fixed, **values)


def _ngen_config(cfg, search):
    """``NGenConfig`` from ``[ngen]`` and ``search``; the SAC phase has only the 'length' priority."""
    from ..ngen import NGenConfig
    config = _build(NGenConfig, {**cfg.get("ngen", {}), "lift": keeps_path(cfg)}, search=search)
    if config.sac and search.priority != "length":
        raise ValueError("ngen with sac=true searches past two generators, where only priority 'length' is defined")
    return config


def _rl_keywords(values):
    """The keywords for ``acx.rl.solve.solve``; ``cap`` defaults to, and may not exceed, the policy's width ``L``."""
    from ..rl import L
    unknown = set(values) - RL_KEYS
    if unknown:
        raise ValueError(f"unknown rl keys {sorted(unknown)}")
    keywords = dict(values)
    keywords["cap"] = parse_cap(keywords.get("cap", L), "rl.cap")
    if keywords["cap"] is None or keywords["cap"] > L:
        raise ValueError(f"rl.cap must be at most {L}, the policy's observation width")
    return keywords
