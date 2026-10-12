"""The benchmark runner behind ``run.py``: one config, one method, every row verified before it is written.

``load_config`` reads and checks a config; ``run`` solves the rows and writes ``results/<name>/``
``{config.json, paths.jsonl, summary.json}``. Methods: greedy, cov, aut, hybrid, ngen, rl; rankn writes its own
per-row files (``acx.ngen.sweep``, see docs/RANK3.md).
"""
import json
import os
import statistics
import time
import tomllib
from contextlib import nullcontext
from dataclasses import fields
from functools import lru_cache
from multiprocessing import Pool

from . import data
from .core.capcount import fields as cap_fields
from .core.capcount import summarize as cap_summary
from .core.config import SearchConfig, parse_cap, parse_override
from .core.moves import encode_path
from .verify.decode import decode_and_replay, pack
from .verify.replay import ReplayError, abs_det, replay

SECTIONS = {"greedy": ("search",), "aut": ("search",), "cov": ("search", "cov"), "ngen": ("search", "ngen"),
            "hybrid": ("hybrid",), "rl": ("rl",), "rankn": ("search", "rankn")}
METHODS = tuple(SECTIONS)
KEYS = {"name", "method", "benchmark", "rows", "workers", "decode"}
TOP = KEYS | {s for v in SECTIONS.values() for s in v}
RL_KEYS = {"width", "steps", "alpha", "cap"}
COST_UNIT = {"hybrid": "units", "rl": "evaluations"}
CAP_PREFIXES = ("cap", "dyn_cap", "slack")      # counter prefixes a method's stats may hold
CAP_EXTRA = ("cap_legs_bound",)                  # CoV: legs whose counter bound


def load_config(path, overrides=()):
    """The config TOML at ``path`` plus ``key=value`` overrides (dotted keys reach sections: ``search.budget=1000``).

    Top level: ``name`` (the results folder, default the file's stem), ``method``, ``benchmark`` (a name of
    ``acx.data.rows`` or a path), ``rows`` (optional: a slice ``"a:b[:c]"`` or ids ``"3,17"``), ``workers``
    (processes, default 1) and ``decode`` (default true: elementary length of S-move paths, ``acx.verify.decode``).
    A method reads only its own sections (``SECTIONS``): ``[search]`` is ``acx.core.config.SearchConfig``,
    ``[cov]`` ``CoVConfig`` and ``[ngen]`` ``NGenConfig`` without their ``search``, ``[hybrid]`` ``HybridConfig``,
    ``[rl]`` the keywords of ``acx.rl.solve.solve`` (width, steps, alpha, cap). Any other section, unknown key or
    invalid value (a cap goes through ``parse_cap``) raises ``ValueError`` here, before anything is written.
    """
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
    """``rows`` sliced by ``"a:b[:c]"`` or picked by comma-separated ids (a repeated id once, first place)."""
    if spec in (None, ""):
        return rows
    spec = str(spec)
    if ":" in spec:
        return rows[slice(*(int(t) if t else None for t in spec.split(":")))]
    ids = list(dict.fromkeys(spec.split(",")))
    by_id = {r.id: r for r in rows}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise KeyError(f"rows not in the benchmark: {missing}")
    return [by_id[i] for i in ids]


def _sub(cls, d, **fixed):
    """``cls(**fixed, **d)`` for a config dataclass, with unknown keys of ``d`` named in the error."""
    names = {f.name for f in fields(cls)} - set(fixed)
    bad = set(d) - names
    if bad:
        raise ValueError(f"unknown {cls.__name__} keys {sorted(bad)}")
    return cls(**fixed, **d)


def method_config(cfg):
    """The method's settings object (a dict of keywords for ``rl``) built from its sections; ``ValueError`` on
    an unknown key or an invalid value. ``[search]`` always captures paths, since every solve is replayed."""
    m = cfg["method"]
    if m == "rankn":
        from .ngen.sweep import SweepConfig
        return SweepConfig.from_cfg(cfg)
    search = SearchConfig.from_dict({**({"budget": 1_000} if m == "cov" else {}), **cfg.get("search", {}),
                                     "capture_path": True})
    if m in ("greedy", "aut"):
        return search
    if m == "cov":
        from .cov import CoVConfig
        return _sub(CoVConfig, cfg.get("cov", {}), search=search)
    if m == "ngen":
        from .ngen import NGenConfig
        c = _sub(NGenConfig, {**cfg.get("ngen", {}), "lift": True}, search=search)
        if c.sac and search.priority != "length":
            raise ValueError("ngen with sac=true searches past two generators, where only priority 'length' is defined")
        return c
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
    """One record: the common fields (``run``), the S-move ``path`` and the ``elementary`` moves JSON-encoded,
    and ``extra`` fields."""
    return dict(solved=solved, kind=kind, aut_assisted=aut, cost=cost, sub_moves=sub, elem_moves=elem,
                path=None if path is None else encode_path(path),
                elementary=None if elementary is None else pack(elementary), **extra)


def _caps(stats):
    """The cap counter fields of a result's ``stats``: every prefix whose ``<prefix>_dropped`` is present."""
    stats = stats or {}
    out = {f: stats[f] for p in CAP_PREFIXES if f"{p}_dropped" in stats for f in cap_fields(p)}
    return {**out, **{k: stats[k] for k in CAP_EXTRA if k in stats}}


def greedy(pres, cfg):
    """Record of the plain best-first search (``acx.search``) on ``pres``; every method function takes the row's
    presentation and the config and returns a record (``run``)."""
    from .search import search
    s = method_config(cfg)
    res = search(pres, s)
    caps = _caps(res.stats)
    if not res.solved:
        return _rec(False, cost=res.pops, **caps)
    replay(pres, res.path, cyclic=s.cyclic, cap=s.cap)
    return _rec(True, "ac_path", False, res.pops, len(res.path), _elementary(pres, res.path, cfg), res.path, **caps)


def cov(pres, cfg):
    """Record of the change-of-variables search (``acx.cov``)."""
    from .cov import run_cov, verify
    res = run_cov(pres, method_config(cfg))
    caps = _caps(res.stats)
    o = res.ac_path or res.stable_cert
    if o is None:
        return _rec(False, cost=res.pops, **caps)
    verify(pres, o)
    img = o.image and o.image.tag
    if o.kind == "stable_cert":
        return _rec(True, "stable_cert", False, res.pops, len(o.path), None, o.path, image=img,
                    steps=list(o.image.steps), **caps)
    if not (o.path and isinstance(o.path[0], dict)):          # S-moves on the row (the row, or an image equal to it)
        return _rec(True, "ac_path", False, res.pops, len(o.path), _elementary(pres, o.path, cfg), o.path, image=img,
                    **caps)
    return _rec(True, "ac_path", True, res.pops, len(o.result.path), len(o.path), o.result.path, o.path, image=img,
                **caps)


def aut(pres, cfg):
    """Record of the search on the Aut-minimal representative, carried back to the row (``acx.aut``)."""
    from .aut import solve_via_aut_min
    s = method_config(cfg)
    res, moves = solve_via_aut_min(pres, s)
    caps = _caps(res.stats)
    if moves is None:
        return _rec(False, cost=res.pops, **caps)
    replay(pres, moves, normalize=False)
    moved = res.start != pres.normal(s.cyclic)      # False: the row is its own Aut-minimal form
    if not moved and s.cyclic:                      # then the S-moves replay on the row, and may decode shorter
        moves = min(moves, decode_and_replay(pres.reduced(False), res.path)[0], key=len)
    return _rec(True, "ac_path", moved, res.pops, len(res.path), len(moves), res.path, moves,
                rep=list(res.start.strs), **caps)


def hybrid(pres, cfg):
    """Record of the hybrid solver (``acx.hybrid``)."""
    from .core.moves import Move
    from .hybrid import encode_steps, solve
    from .hybrid.cascade import Aut
    res = solve(pres, method_config(cfg))
    caps = _caps(res.stats)
    if not res.solved:
        return _rec(False, cost=res.units, **caps)
    replay(pres, res.path, normalize=False)
    return _rec(True, res.kind, res.kind == "ac_path" and any(isinstance(s, Aut) for s in res.steps), res.units,
                sum(isinstance(s, Move) for s in res.steps), len(res.path), None, res.path, stage=res.stage,
                steps=encode_steps(res.steps), **caps)


def ngen(pres, cfg):
    """Record of the n-generator search, SAC then lift (``acx.ngen``)."""
    from .ngen import solve, verify
    c = method_config(cfg)
    res = solve(pres, c)
    caps = _caps(res.search.stats)
    if not res.solved:
        return _rec(False, cost=res.search.pops, rank=res.rank, **caps)
    verify(pres, res, cyclic=c.search.cyclic)
    p = res.search.path
    if res.kind == "ac_path":
        return _rec(True, "ac_path", False, res.search.pops, len(p), _elementary(pres, p, cfg), p, rank=res.rank,
                    **caps)
    return _rec(True, "stable_cert", False, res.search.pops, len(p), len(res.moves), p, res.moves, rank=res.rank,
                **caps)


@lru_cache(maxsize=1)
def _policy():
    """The pretrained policy, loaded once per process."""
    from .rl.policy import pretrained
    return pretrained()


def rl(pres, cfg):
    """Record of the network-guided beam search (``acx.rl``, needs PyTorch)."""
    from .rl.solve import solve
    res = solve(pres, _policy(), **method_config(cfg))
    caps = _caps(res.stats)
    if not res.solved:
        return _rec(False, cost=res.pops, **({"skipped": res.stats["skipped"]} if "skipped" in res.stats else {}),
                    **caps)
    replay(pres, res.path, cap=res.stats["cap"])
    return _rec(True, "ac_path", False, res.pops, len(res.path), _elementary(pres, res.path, cfg), res.path, **caps)


def _unsolvable(pres):
    """Why no AC path starts from ``pres`` (``|det| != 1``, or not balanced), None when one may exist."""
    try:
        d = abs_det(pres)
    except ReplayError as e:
        return str(e)
    return None if d == 1 else f"|det| = {d}, not AC-trivial"


def _solve_row(args):
    """``(cfg, row)`` -> the row's record; a row no AC path can start from is an unsolved record with an ``error``."""
    cfg, row = args
    t0 = time.perf_counter()
    why = _unsolvable(row.pres)
    rec = _rec(False, error=why) if why else globals()[cfg["method"]](row.pres, cfg)
    return {"id": row.id, **rec, "seconds": round(time.perf_counter() - t0, 4)}


def check_method(cfg):
    """Fail early with a clear message when an optional dependency is missing."""
    if cfg["method"] == "rl":
        try:
            import torch  # noqa: F401
        except ModuleNotFoundError:
            raise SystemExit("method 'rl' needs PyTorch: pip install -e .[rl]") from None


def _stats(xs):
    """``n``, ``sum``, ``mean``, ``median`` and ``max`` of the values that are not None (None if there are none)."""
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return dict(n=len(xs), sum=sum(xs), mean=round(statistics.fmean(xs), 2), median=statistics.median(xs), max=max(xs))


def summarize(cfg, recs, wall):
    """The ``summary.json`` dict of ``recs`` (the run's records, one per row)."""
    solved = [r for r in recs if r["solved"]]
    groups = {"ac_path": [r for r in solved if r["kind"] == "ac_path" and not r["aut_assisted"]],
              "aut_assisted": [r for r in solved if r["aut_assisted"]],
              "stable_cert": [r for r in solved if r["kind"] == "stable_cert"]}
    return dict(
        name=cfg["name"], method=cfg["method"], benchmark=cfg["benchmark"], rows=len(recs), solved=len(solved),
        **{k: len(v) for k, v in groups.items()}, skipped=sum(1 for r in recs if r.get("skipped")),
        errors=sum(1 for r in recs if r.get("error")),
        cost=dict(unit=COST_UNIT.get(cfg["method"], "pops"), total=sum(r["cost"] for r in recs),
                  on_solved=sum(r["cost"] for r in solved)),
        path_length={k: dict(sub_moves=_stats(r["sub_moves"] for r in v), elem_moves=_stats(r["elem_moves"] for r in v))
                     for k, v in groups.items() if v},
        caps=caps_block(recs),
        wall_seconds=round(wall, 2), row_seconds=round(sum(r["seconds"] for r in recs), 2), config=cfg)


def caps_block(recs):
    """``summary.json``'s ``caps``: one ``acx.core.capcount.summarize`` entry per counter prefix the rows carry."""
    out = {}
    for p in CAP_PREFIXES:
        block = cap_summary(recs, p)
        if block is not None:
            if p == "cap":
                for k in CAP_EXTRA:
                    xs = [r[k] for r in recs if k in r]
                    if xs:
                        block[k] = sum(xs)
            out[p] = block
    return out


def _load_done(paths):
    """The records in ``paths`` by id. A last line that is cut off (an interrupted write) is dropped from the file."""
    done, good = {}, 0
    with open(paths, "rb") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                break
            if not line.endswith(b"\n"):
                break
            done[rec["id"]] = rec
            good += len(line)
    with open(paths, "r+b") as f:
        f.truncate(good)
    return done


def run(cfg, out="results", fresh=False, log=print):
    """Run ``cfg`` over its rows and return the summary.

    Writes ``<out>/<name>/``: ``config.json``, ``paths.jsonl`` (one record per row, flushed as it is solved) and
    ``summary.json``. Rows already in ``paths.jsonl`` are skipped, so an interrupted run resumes and a run under
    another config needs ``fresh`` or another name; the summary covers every record in ``paths.jsonl``.

    A record: ``solved``, ``kind`` (``ac_path``, ``stable_cert`` or None), ``aut_assisted`` (an ``ac_path`` carried
    back to the row from another basis), ``cost`` (pops, hybrid units or network evaluations), ``sub_moves``
    (substitution moves) and ``elem_moves`` (elementary AC moves on the row; None for a CoV ``stable_cert``), the
    certificate (``path``: S-moves, ``acx.core.moves.encode_path``; ``elementary``: ``acx.verify.decode.pack``;
    ``steps``: a CoV transform or hybrid certificate), the cap counters of its search (``CAP_PREFIXES``, fields
    ``acx.core.capcount.FIELDS``; ``caps`` in the summary) and ``seconds``. A record is written only after its
    certificate is verified on the row (``acx.verify.replay``; a CoV ``stable_cert`` by ``acx.cov.verify``); a
    row with ``|det| != 1`` gets ``solved: false`` and an ``error``.
    """
    check_method(cfg)
    if cfg["method"] == "rankn":
        from .ngen.sweep import run as run_rankn
        return run_rankn(cfg, out, fresh, log)
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
    done = _load_done(paths) if os.path.exists(paths) else {}
    todo = [r for r in rows if r.id not in done]
    log(f"{cfg['name']}: {cfg['method']} on {cfg['benchmark']}, {len(rows)} rows ({len(rows) - len(todo)} done)")
    t0 = time.perf_counter()
    workers = cfg.get("workers", 1)
    with open(paths, "a") as f, (Pool(workers) if workers > 1 else nullcontext()) as pool:
        for n, rec in enumerate((pool.imap if pool else map)(_solve_row, [(cfg, r) for r in todo]), 1):
            done[rec["id"]] = rec
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if n % 50 == 0 or n == len(todo):
                log(f"  {n}/{len(todo)} rows, {sum(done[r.id]['solved'] for r in todo[:n])} solved")
    summary = summarize(cfg, list(done.values()), time.perf_counter() - t0)
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary
