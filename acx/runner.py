"""The benchmark runner behind ``run.py``: one config, one method, every row verified before it is written.

A config is a TOML file::

    name = "s20_mk2_fast"        # results/<name>/ (default: the file's stem)
    method = "greedy"            # greedy | cov | aut | hybrid | ngen | rl
    benchmark = "ms640"          # a name of acx.data.rows, or a path
    rows = "0:40"                # optional: a slice "a:b[:c]" or ids "3,17,ms_335"
    workers = 1                  # processes
    decode = true                # elementary length of S-move paths (acx.verify.decode)
    [search]                     # acx.core.config.SearchConfig (greedy, cov, aut, ngen)
    [cov]                        # acx.cov.CoVConfig, without ``search``
    [hybrid]                     # acx.hybrid.HybridConfig
    [ngen]                       # acx.ngen.NGenConfig, without ``search``
    [rl]                         # acx.rl.solve.solve keywords: width, steps, alpha, cap

A method reads only its own sections (``SECTIONS``); any other section, any unknown key and any invalid value
(a cap through ``acx.core.config.parse_cap``) is an error when the config is loaded, before anything is written.

Each row gives one record in ``paths.jsonl``: ``kind`` (``ac_path``, ``stable_cert`` or None),
``aut_assisted`` (an ``ac_path`` whose certificate changed basis and was carried back to the row),
``cost`` (pops, hybrid units or network evaluations), ``sub_moves`` (substitution moves of the search)
and ``elem_moves`` (elementary AC moves on the row; None for a CoV ``stable_cert``, whose transform has no
AC path), and the certificate: ``path`` (S-moves, ``encode_path``), ``elementary`` (the elementary path on the
row, ``acx.verify.decode.pack``) and ``steps`` (a CoV transform or a hybrid certificate). A record is written only after its certificate replays on the row
(``acx.verify.replay``; a CoV ``stable_cert`` through ``acx.cov.verify``). Rows already in ``paths.jsonl``
are skipped, so an interrupted run resumes; ``summary.json`` covers the selected rows.
"""
import json
import os
import statistics
import time
import tomllib
from dataclasses import fields
from functools import lru_cache
from multiprocessing import Pool

from . import data
from .core.config import SearchConfig, parse_cap, parse_override
from .core.moves import encode_path
from .verify.decode import decode_and_replay, pack
from .verify.replay import replay

SECTIONS = {"greedy": ("search",), "aut": ("search",), "cov": ("search", "cov"), "ngen": ("search", "ngen"),
            "hybrid": ("hybrid",), "rl": ("rl",)}
METHODS = tuple(SECTIONS)
KEYS = {"name", "method", "benchmark", "rows", "workers", "decode"}
TOP = KEYS | {s for v in SECTIONS.values() for s in v}
RL_KEYS = {"width", "steps", "alpha", "cap"}
COST_UNIT = {"hybrid": "units", "rl": "evaluations"}


def load_config(path, overrides=()):
    """The TOML at ``path`` plus ``key=value`` overrides (dotted keys reach sections: ``search.budget=1000``)."""
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    cfg.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    for item in overrides:
        key, value = parse_override(item)
        *sections, leaf = key.split(".")
        d = cfg
        for s in sections:
            d = d.setdefault(s, {})
        d[leaf] = value
    bad = set(cfg) - TOP
    if bad:
        raise ValueError(f"unknown config keys {sorted(bad)}")
    if cfg.get("method") not in METHODS:
        raise ValueError(f"method {cfg.get('method')!r} not in {METHODS}")
    unused = set(cfg) - KEYS - set(SECTIONS[cfg["method"]])
    if unused:
        raise ValueError(f"method {cfg['method']!r} does not read the sections {sorted(unused)}")
    if "benchmark" not in cfg:
        raise ValueError("config needs a benchmark")
    method_config(cfg)
    return cfg


def select(rows, spec):
    """``rows`` sliced by ``"a:b[:c]"`` or picked by comma-separated ids."""
    if spec in (None, ""):
        return rows
    spec = str(spec)
    if ":" in spec:
        return rows[slice(*(int(t) if t else None for t in spec.split(":")))]
    ids = spec.split(",")
    by_id = {r.id: r for r in rows}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise KeyError(f"rows not in the benchmark: {missing}")
    return [by_id[i] for i in ids]


def _sub(cls, d, **fixed):
    names = {f.name for f in fields(cls)} - set(fixed)
    bad = set(d) - names
    if bad:
        raise ValueError(f"unknown {cls.__name__} keys {sorted(bad)}")
    return cls(**fixed, **d)


def method_config(cfg):
    """The method's settings, built from its sections; raises on an unknown key or an invalid value.

    ``[search]`` always captures paths, since every solve is replayed.
    """
    m = cfg["method"]
    search = SearchConfig.from_dict({**({"budget": 1_000} if m == "cov" else {}), **cfg.get("search", {}),
                                     "capture_path": True})
    if m in ("greedy", "aut"):
        return search
    if m == "cov":
        from .cov import CoVConfig
        return _sub(CoVConfig, cfg.get("cov", {}), search=search)
    if m == "ngen":
        from .ngen import NGenConfig
        return _sub(NGenConfig, {**cfg.get("ngen", {}), "lift": True}, search=search)
    if m == "hybrid":
        from .hybrid import HybridConfig
        return _sub(HybridConfig, {**cfg.get("hybrid", {}), "certify": True})
    from .rl import L
    kw = dict(cfg.get("rl", {}))
    bad = set(kw) - RL_KEYS
    if bad:
        raise ValueError(f"unknown rl keys {sorted(bad)}")
    kw["cap"] = parse_cap(kw.get("cap", L), "rl.cap")
    if kw["cap"] is None or kw["cap"] > L:
        raise ValueError(f"rl.cap must be at most {L}, the policy's observation width")
    return kw


def _elementary(pres, path, cfg):
    """Decoded elementary length of an S-move path (``decode = true`` and cyclic reduction on)."""
    if not cfg.get("decode", True) or not cfg.get("search", {}).get("cyclic", True):
        return None
    return len(decode_and_replay(pres.reduced(False), path)[0])


def _rec(solved, kind=None, aut=False, cost=0, sub=None, elem=None, path=None, elementary=None, **extra):
    return dict(solved=solved, kind=kind, aut_assisted=aut, cost=cost, sub_moves=sub, elem_moves=elem,
                path=None if path is None else encode_path(path),
                elementary=None if elementary is None else pack(elementary), **extra)


def greedy(pres, cfg):
    from .search import search
    s = method_config(cfg)
    res = search(pres, s)
    if not res.solved:
        return _rec(False, cost=res.pops)
    replay(pres, res.path, cyclic=s.cyclic, cap=s.cap)
    return _rec(True, "ac_path", False, res.pops, len(res.path), _elementary(pres, res.path, cfg), res.path)


def cov(pres, cfg):
    from .cov import run_cov, verify
    res = run_cov(pres, method_config(cfg))
    o = res.ac_path or res.stable_cert
    if o is None:
        return _rec(False, cost=res.pops)
    verify(pres, o)
    img = o.image and o.image.tag
    if o.kind == "stable_cert":
        return _rec(True, "stable_cert", False, res.pops, len(o.path), None, o.path, image=img,
                    steps=list(o.image.steps))
    if not (o.path and isinstance(o.path[0], dict)):          # S-moves on the row (the row, or an image equal to it)
        return _rec(True, "ac_path", False, res.pops, len(o.path), _elementary(pres, o.path, cfg), o.path, image=img)
    return _rec(True, "ac_path", True, res.pops, len(o.result.path), len(o.path), o.result.path, o.path, image=img)


def aut(pres, cfg):
    from .aut import solve_via_aut_min
    s = method_config(cfg)
    res, moves = solve_via_aut_min(pres, s)
    if moves is None:
        return _rec(False, cost=res.pops)
    replay(pres, moves, normalize=False)
    moved = res.start != pres.reduced(s.cyclic).canonical()   # False: the row is its own Aut-minimal form
    return _rec(True, "ac_path", moved, res.pops, len(res.path), len(moves), res.path, moves,
                rep=list(res.start.strs))


def hybrid(pres, cfg):
    from .core.moves import Move
    from .hybrid import encode_steps, solve
    from .hybrid.cascade import Aut
    res = solve(pres, method_config(cfg))
    if not res.solved:
        return _rec(False, cost=res.units)
    replay(pres, res.path, normalize=False)
    return _rec(True, res.kind, res.kind == "ac_path" and any(isinstance(s, Aut) for s in res.steps), res.units,
                sum(isinstance(s, Move) for s in res.steps), len(res.path), None, res.path, stage=res.stage,
                steps=encode_steps(res.steps))


def ngen(pres, cfg):
    from .ngen import solve, verify
    c = method_config(cfg)
    res = solve(pres, c)
    if not res.solved:
        return _rec(False, cost=res.search.pops, rank=res.rank)
    verify(pres, res, cyclic=c.search.cyclic)
    p = res.search.path
    if res.kind == "ac_path":
        return _rec(True, "ac_path", False, res.search.pops, len(p), _elementary(pres, p, cfg), p, rank=res.rank)
    return _rec(True, "stable_cert", False, res.search.pops, len(p), len(res.moves), p, res.moves, rank=res.rank)


@lru_cache(maxsize=1)
def _policy():
    from .rl.policy import pretrained
    return pretrained()


def rl(pres, cfg):
    from .rl.solve import solve
    res = solve(pres, _policy(), **method_config(cfg))
    if not res.solved:
        return _rec(False, cost=res.pops, **({"skipped": res.stats["skipped"]} if "skipped" in res.stats else {}))
    replay(pres, res.path, cap=res.stats["cap"])
    return _rec(True, "ac_path", False, res.pops, len(res.path), _elementary(pres, res.path, cfg), res.path)


def _solve_row(args):
    cfg, row = args
    t0 = time.perf_counter()
    rec = globals()[cfg["method"]](row.pres, cfg)
    return {"id": row.id, **rec, "seconds": round(time.perf_counter() - t0, 4)}


def check_method(cfg):
    """Fail early with a clear message when an optional dependency is missing."""
    if cfg["method"] == "rl":
        try:
            import torch  # noqa: F401
        except ModuleNotFoundError:
            raise SystemExit("method 'rl' needs PyTorch: pip install -e .[rl]") from None


def _stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return dict(n=len(xs), sum=sum(xs), mean=round(statistics.fmean(xs), 2), median=statistics.median(xs), max=max(xs))


def summarize(cfg, recs, wall):
    solved = [r for r in recs if r["solved"]]
    groups = {"ac_path": [r for r in solved if r["kind"] == "ac_path" and not r["aut_assisted"]],
              "aut_assisted": [r for r in solved if r["aut_assisted"]],
              "stable_cert": [r for r in solved if r["kind"] == "stable_cert"]}
    return dict(
        name=cfg["name"], method=cfg["method"], benchmark=cfg["benchmark"], rows=len(recs), solved=len(solved),
        **{k: len(v) for k, v in groups.items()}, skipped=sum(1 for r in recs if r.get("skipped")),
        cost=dict(unit=COST_UNIT.get(cfg["method"], "pops"), total=sum(r["cost"] for r in recs),
                  on_solved=sum(r["cost"] for r in solved)),
        path_length={k: dict(sub_moves=_stats(r["sub_moves"] for r in v), elem_moves=_stats(r["elem_moves"] for r in v))
                     for k, v in groups.items() if v},
        wall_seconds=round(wall, 2), row_seconds=round(sum(r["seconds"] for r in recs), 2), config=cfg)


def run(cfg, out="results", fresh=False, log=print):
    """Run ``cfg`` over its rows; write ``results/<name>/{paths.jsonl, summary.json}``; return the summary."""
    check_method(cfg)
    rows = select(data.rows(cfg["benchmark"]), cfg.get("rows"))
    d = os.path.join(out, cfg["name"])
    os.makedirs(d, exist_ok=True)
    paths, cfg_file = os.path.join(d, "paths.jsonl"), os.path.join(d, "config.json")
    key = {k: v for k, v in cfg.items() if k not in ("rows", "workers")}
    for f in (paths, cfg_file, os.path.join(d, "summary.json")) if fresh else ():
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists(cfg_file):
        with open(cfg_file) as f:
            if json.load(f) != key:
                raise SystemExit(f"{d} holds a run with another config: pass --fresh or another name")
    with open(cfg_file, "w") as f:
        json.dump(key, f, indent=1)
    done = {}
    if os.path.exists(paths):
        with open(paths) as f:
            done = {r["id"]: r for r in map(json.loads, f)}
    todo = [r for r in rows if r.id not in done]
    log(f"{cfg['name']}: {cfg['method']} on {cfg['benchmark']}, {len(rows)} rows ({len(rows) - len(todo)} done)")
    t0 = time.perf_counter()
    workers = cfg.get("workers", 1)
    with open(paths, "a") as f, Pool(workers) if workers > 1 else _Serial() as pool:
        for n, rec in enumerate(pool.imap(_solve_row, [(cfg, r) for r in todo]), 1):
            done[rec["id"]] = rec
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if n % 50 == 0 or n == len(todo):
                log(f"  {n}/{len(todo)} rows, {sum(done[r.id]['solved'] for r in todo[:n])} solved")
    summary = summarize(cfg, [done[r.id] for r in rows], time.perf_counter() - t0)
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary


class _Serial:
    """``Pool``'s ``imap`` in this process (one worker)."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def imap(self, fn, items):
        return map(fn, items)
