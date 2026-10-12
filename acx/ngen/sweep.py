"""Rank-n brute-force sweep: stabilise each row with a word and search the stabilised start.

For a presentation ``<x, y | r1, r2>`` and a freely reduced word ``w`` in ``x, y`` the start is
``<x, y, z | r1, r2, Z.w>`` (one added generator, ``extra = 1``); ``extra = 2`` and ``3`` add
``Z1.w1, Z2.w2[, Z3.w3]`` and sweep every multiset of words (ranks 4 and 5). Each start is searched by
``acx.search.search`` (the same spec and fast backends as every other method) at the configured cap and budget.
Per row the 2-generator control and the null stabilisation (``extra`` relators ``Z_i`` with empty words) are
searched too, and must agree on (solved, pops, path length), or the row is refused.

The word pool is ``reduced_words(n)`` for ``n = min_len..max_len``: every freely reduced word of length ``n``
over ``x, y, X, Y``, one of each pair ``{w, w^-1}`` (``2 * 3**(n-1)`` words), in a fixed depth-first order over
``(x, y, X, Y)``. ``inverse = true`` searches ``w^-1`` instead (the two starts are the same up to renaming
``z``, so only heap ties can differ). The brute-force baseline this ports is
``origin/rank3/brute-force-baseline`` (``experiments/stable_ac/rank3/``); see ``docs/RANK3.md``.

A solve of a stabilised start is a statement about the start, not an AC path of the row: it certifies stable AC
triviality only after a lift that this sweep does not do, so it never writes an ``ac_path`` or a ``stable_cert``.

Results, under ``<out>/<name>/``:

* ``config.json``: the run's identity (a run with another config is refused);
* ``rows/<id>.npz``: one file per row, written atomically; a present file is skipped, so a killed run resumes
  (a file from another budget, cap, pool or counter set is an error, never merged). It holds, indexed by start
  (``combos`` into ``words``): ``nodes`` (pops, uint16), ``path_len`` (int16, -1 unsolved), ``min_total`` (uint8),
  the cap counters ``cap_*`` the search reports (``acx.core.capcount``; -1 = none), the control and null records
  and a deterministic sample of solved paths (md5 of ``id|word`` below ``sample``);
* ``summary.json`` and ``summary.md``: ``summarize``.

``verify(dir)`` re-checks the files (control against null, shapes, counter consistency, replay of the sampled
paths, a re-run of random cells on the other backend). The result files are large; keep them out of git.
"""
import argparse
import hashlib
import itertools
import json
import os
import random
import time
import tomllib
from dataclasses import asdict, dataclass, fields
from functools import lru_cache
from multiprocessing import Pool

import numpy as np

from .. import data
from ..core.config import SearchConfig, parse_override
from ..core.moves import decode_path, encode_path
from ..core.words import Presentation, fmt, inverse as invert
from ..search import search
from ..verify.replay import replay

LETTERS = (1, 2, -1, -2)                    # x, y, X, Y
COUNTERS = ("cap_dropped", "cap_dropped_min_total", "cap_would_pop", "cap_first_bind", "cap_needed")
HAS_COUNT = "cap_count" in {f.name for f in fields(SearchConfig)}
KEYS = {"name", "method", "benchmark", "rows", "workers", "search", "rankn"}


class SweepError(RuntimeError):
    pass


# ---------------------------------------------------------------------------------------- words and starts
@lru_cache(maxsize=None)
def reduced_words(n):
    """Every freely reduced word of length ``n`` over x, y, X, Y, one of each pair ``{w, w^-1}`` (the larger
    int tuple), in depth-first order over ``(x, y, X, Y)``: ``2 * 3**(n-1)`` words."""
    out = []

    def rec(prefix):
        if len(prefix) == n:
            if prefix > invert(prefix):
                out.append(prefix)
            return
        for g in LETTERS:
            if not prefix or prefix[-1] != -g:
                rec(prefix + (g,))

    rec(())
    return tuple(out)


def start(r1, r2, words):
    """``<x, y, z1..zk | r1, r2, Z1.w1, .., Zk.wk>``; empty words give the null stabilisation."""
    return Presentation(2 + len(words), (tuple(r1), tuple(r2))
                        + tuple((-(3 + i),) + tuple(w) for i, w in enumerate(words)))


# -------------------------------------------------------------------------------------------------- config
@dataclass(frozen=True)
class SweepConfig:
    search: SearchConfig
    extra: int = 1           # added generators: rank 2 + extra (1: rank 3, 2: rank 4, 3: rank 5)
    min_len: int = 1
    max_len: int = 4
    inverse: bool = False    # search w^-1 instead of w
    sample: float = 0.002    # fraction of solved starts whose path is kept for replay

    def __post_init__(self):
        s = self.search
        if self.extra not in (1, 2, 3):
            raise ValueError(f"rankn.extra must be 1, 2 or 3, got {self.extra!r}")
        if not (type(self.min_len) is int and type(self.max_len) is int and 1 <= self.min_len <= self.max_len):
            raise ValueError(f"rankn needs 1 <= min_len <= max_len, got {self.min_len!r}, {self.max_len!r}")
        if s.priority != "length":
            raise ValueError("the sweep supports priority = 'length' only (s20_mk2 is defined for two generators)")
        if s.budget > 65_535:
            raise ValueError("the sweep stores pops as uint16: search.budget must be at most 65535")
        if s.cap is not None and 1 + self.max_len > s.cap:
            raise ValueError(f"search.cap {s.cap} is below the start relator Z.w of length {1 + self.max_len}")
        if not 0 <= self.sample <= 1:
            raise ValueError(f"rankn.sample must be in [0, 1], got {self.sample!r}")

    @classmethod
    def from_cfg(cls, cfg):
        """From a runner-style config dict (sections ``search`` and ``rankn``); unknown keys are errors."""
        raw = dict(cfg.get("rankn", {}))
        bad = set(raw) - {f.name for f in fields(cls)}
        if bad:
            raise ValueError(f"unknown rankn keys {sorted(bad)}")
        s = {**cfg.get("search", {}), "capture_path": True, **({"cap_count": True} if HAS_COUNT else {})}
        return cls(search=SearchConfig.from_dict(s), **raw)

    def key(self):
        """What a result directory holds (the backend is left out: both backends give the same rows)."""
        d = asdict(self)
        d["search"] = {k: v for k, v in d["search"].items() if k not in ("backend", "capture_path", "trace")}
        return d


@lru_cache(maxsize=None)
def pool(min_len, max_len, inverse):
    ws = tuple(w for n in range(min_len, max_len + 1) for w in reduced_words(n))
    return tuple(invert(w) for w in ws) if inverse else ws


@lru_cache(maxsize=None)
def combos(n_words, extra):
    """The index tuples of the starts: one word each (``extra = 1``) or every multiset of ``extra`` words."""
    if extra == 1:
        return tuple((i,) for i in range(n_words))
    return tuple(itertools.combinations_with_replacement(range(n_words), extra))


def words_of(sc):
    return pool(sc.min_len, sc.max_len, sc.inverse)


def word_str(ws):
    """``"x"`` for one word, ``"x,yX"`` for several (an empty word is ``""``)."""
    return ",".join(fmt(w) for w in ws)


def lengths(sc):
    return np.array([len(w) for w in pool(sc.min_len, sc.max_len, False)], dtype=np.int16)


@lru_cache(maxsize=None)
def counter_fields(scfg):
    """The cap counters this build of ``acx.search`` reports (a probe search; ``cap_rejected`` is ``cap_dropped``)."""
    stats = search(Presentation(2, ((1,), (2,))), scfg).stats
    got = {"cap_dropped" if k == "cap_rejected" else k for k in stats}
    return tuple(k for k in COUNTERS if k in got)


def cap_counters(stats, names):
    return {k: stats.get("cap_rejected") if k == "cap_dropped" and k not in stats else stats.get(k) for k in names}


def sampled(rid, wstr, frac):
    if frac <= 0:
        return False
    if frac >= 1:
        return True
    h = hashlib.md5(f"{rid}|{wstr}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64 < frac


def ident_of(sc, rid, pres):
    ws = words_of(sc)
    return json.dumps({"id": rid, "r1": fmt(pres.rels[0]), "r2": fmt(pres.rels[1]), "config": sc.key(),
                       "pool": hashlib.md5(",".join(map(fmt, ws)).encode()).hexdigest(),
                       "counters": list(counter_fields(sc.search))}, sort_keys=True, separators=(",", ":"))


# --------------------------------------------------------------------------------------------------- a row
def _one(pres, scfg, names):
    res = search(pres, scfg)
    return res, {"solved": res.solved, "pops": res.pops, "path_len": res.path_length,
                 "min_total": res.stats["min_total"], "counters": cap_counters(res.stats, names)}


def sweep_row(rid, pres, sc):
    """Control, null stabilisation and every start of the pool for one row; returns the arrays of the row file."""
    t0 = time.perf_counter()
    scfg, names = sc.search, counter_fields(sc.search)
    r1, r2 = pres.rels
    cres, control = _one(Presentation(2, (r1, r2)), scfg, names)
    _, null = _one(start(r1, r2, [()] * sc.extra), scfg, names)
    if tuple(control[k] for k in ("solved", "pops", "path_len")) != tuple(null[k] for k in ("solved", "pops", "path_len")):
        raise SweepError(f"row {rid}: the control {control} and the null stabilisation {null} differ")
    if control["solved"]:
        control["path"] = encode_path(cres.path)
    ws = words_of(sc)
    cs = combos(len(ws), sc.extra)
    nodes = np.zeros(len(cs), dtype=np.uint16)
    plen = np.full(len(cs), -1, dtype=np.int16)
    mint = np.zeros(len(cs), dtype=np.uint8)
    caps = {k: np.full(len(cs), -1, dtype=np.int64) for k in names}
    paths = []
    for i, c in enumerate(cs):
        res = search(start(r1, r2, [ws[j] for j in c]), scfg)
        nodes[i], mint[i] = res.pops, min(res.stats["min_total"], 255)
        for k, v in cap_counters(res.stats, names).items():
            caps[k][i] = -1 if v is None else v
        if res.solved:
            plen[i] = res.path_length
            wstr = word_str([ws[j] for j in c])
            if sampled(rid, wstr, sc.sample):
                paths.append({"index": i, "word": wstr, "pops": res.pops, "path": encode_path(res.path)})
    out = {"nodes": nodes, "path_len": plen, "min_total": mint, **{k: caps[k].astype(np.uint32 if k == "cap_dropped" else np.int32) for k in names},
           "control": np.array(json.dumps(control)), "null": np.array(json.dumps(null)),
           "paths": np.array(json.dumps(paths)), "seconds": np.float32(time.perf_counter() - t0),
           "ident": np.array(ident_of(sc, rid, pres))}
    return out


def row_path(d, rid):
    return os.path.join(d, "rows", f"{rid}.npz")


def load_row(path):
    with np.load(path) as z:
        r = {k: z[k] for k in z.files}
    for k in ("control", "null", "paths"):
        r[k] = json.loads(str(r[k]))
    r["ident"] = str(r["ident"])
    return r


def _task(args):
    d, rid, pres, sc = args
    path = row_path(d, rid)
    ident = ident_of(sc, rid, pres)
    if os.path.exists(path):
        got = load_row(path)["ident"]
        if got != ident:
            raise SweepError(f"{path} is not from this run: has {got}, expected {ident}")
        return rid, 0.0, None
    out = sweep_row(rid, pres, sc)
    tmp = f"{path}.tmp{os.getpid()}.npz"
    np.savez_compressed(tmp, **out)
    os.replace(tmp, path)
    return rid, float(out["seconds"]), int((out["path_len"] >= 0).sum())


# ------------------------------------------------------------------------------------------------- the run
def load_config(path, overrides=()):
    """The TOML at ``path`` plus ``key=value`` overrides (dotted keys reach sections), for ``python -m acx.ngen.sweep``."""
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    cfg.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    for item in overrides:
        key, value = parse_override(item)
        *sections, leaf = key.split(".")
        node = cfg
        for s in sections:
            node = node.setdefault(s, {})
        node[leaf] = value
    if cfg.get("method") != "rankn":
        raise ValueError(f"method {cfg.get('method')!r} is not 'rankn'")
    bad = set(cfg) - KEYS
    if bad:
        raise ValueError(f"unknown config keys {sorted(bad)}")
    if "benchmark" not in cfg:
        raise ValueError("config needs a benchmark")
    SweepConfig.from_cfg(cfg)
    return cfg


def run(cfg, out="results", fresh=False, log=print):
    """Sweep every selected row of ``cfg`` into ``<out>/<name>/rows``; write and return the summary."""
    from ..runner import select
    sc = SweepConfig.from_cfg(cfg)
    rows = select(data.rows(cfg["benchmark"]), cfg.get("rows"))
    d = os.path.join(out, cfg["name"])
    os.makedirs(os.path.join(d, "rows"), exist_ok=True)
    cfg_file = os.path.join(d, "config.json")
    key = {"benchmark": cfg["benchmark"], "method": "rankn", "sweep": sc.key()}
    if fresh:
        for f in [os.path.join(d, "rows", x) for x in os.listdir(os.path.join(d, "rows"))] + [
                cfg_file, os.path.join(d, "summary.json"), os.path.join(d, "summary.md")]:
            if os.path.exists(f):
                os.remove(f)
    if os.path.exists(cfg_file):
        with open(cfg_file) as f:
            if json.load(f) != key:
                raise SystemExit(f"{d} holds a run with another config: pass --fresh or another name")
    with open(cfg_file, "w") as f:
        json.dump(key, f, indent=1)
    names = counter_fields(sc.search)
    todo = [r for r in rows if not os.path.exists(row_path(d, r.id))]
    log(f"{cfg['name']}: rankn (extra {sc.extra}, lengths {sc.min_len}-{sc.max_len}, {len(words_of(sc))} words, "
        f"{len(combos(len(words_of(sc)), sc.extra))} starts per row) on {cfg['benchmark']}, {len(rows)} rows "
        f"({len(rows) - len(todo)} done), counters {list(names)}")
    t0 = time.perf_counter()
    workers = cfg.get("workers", 1)
    tasks = [(d, r.id, r.pres, sc) for r in rows]
    with (Pool(workers) if workers > 1 else _Serial()) as pl:
        for n, (rid, secs, solved) in enumerate(pl.imap_unordered(_task, tasks), 1):
            if n % 50 == 0 or n == len(tasks):
                log(f"  {n}/{len(tasks)} rows")
    summary = summarize(d, wall=time.perf_counter() - t0, rows=[r.id for r in rows])
    return summary


class _Serial:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def imap_unordered(self, fn, items):
        return map(fn, items)


# ------------------------------------------------------------------------------------------------ summary
def _frac(x):
    return round(float(x), 4)


def summarize(d, wall=None, rows=None):
    """Stream the row files of ``d`` into ``summary.json`` and ``summary.md``; return the summary.

    Per-presentation fractions are averaged over presentations (every presentation weighs the same). "Fewer" counts
    a solve where the control fails. The oracle row is an existence statement: a presentation counts if some word
    of the pool (up to that length, for ``extra = 1``) solves it.
    """
    with open(os.path.join(d, "config.json")) as f:
        key = json.load(f)["sweep"]
    sc = SweepConfig.from_cfg({"search": key["search"], "rankn": {k: v for k, v in key.items() if k != "search"}})
    ws = words_of(sc)
    wl = lengths(sc)
    cs = combos(len(ws), sc.extra)
    if sc.extra == 1:
        buckets = [(f"L{n}", wl == n, wl <= n) for n in range(sc.min_len, sc.max_len + 1)]
    else:
        buckets = [("all", np.ones(len(cs), bool), np.ones(len(cs), bool))]
    ids = rows if rows is not None else sorted(f[:-4] for f in os.listdir(os.path.join(d, "rows")) if f.endswith(".npz"))
    zero = lambda: dict(solved=0.0, solved_cs=0.0, solved_cu=0.0, fewer=0.0, same=0.0, more=0.0, lost_cs=0.0, unsolved=0.0,
                        some=0, gained=0, lost=0, faster=0, searches=0)
    acc = {b[0]: zero() for b in buckets}
    n_rows = ctl_solved = 0
    per_word = np.zeros(len(cs), dtype=np.int64)
    cap = dict(searches=0, dropped=0, could_bind=None, solved_could_bind=None, below_budget=0)
    budget = sc.search.budget
    secs = 0.0
    names = None
    for rid in ids:
        r = load_row(row_path(d, rid))
        names = [k for k in COUNTERS if k in r]
        c = r["control"]
        cn, c_ok = c["pops"], bool(c["solved"])
        S, nodes = r["path_len"] >= 0, r["nodes"].astype(np.int64)
        n_rows += 1
        ctl_solved += c_ok
        secs += float(r["seconds"])
        per_word += S
        for name, m, upto in buckets:
            a, s, nd = acc[name], S[m], nodes[m]
            a["solved"] += s.mean()
            if c_ok:
                a["solved_cs"] += s.mean()
                a["lost_cs"] += (~s).mean()
            else:
                a["solved_cu"] += s.mean()
            fewer = s & (nd < cn) if c_ok else s
            a["fewer"] += fewer.mean()
            a["same"] += (s & (nd == cn)).mean() if c_ok else 0.0
            a["more"] += (s & (nd > cn)).mean() if c_ok else 0.0
            a["unsolved"] += (~s).mean()
            a["searches"] += int(m.sum())
            su = S[upto]
            some = bool(su.any())
            a["some"] += some
            a["gained"] += some and not c_ok
            a["lost"] += c_ok and not some
            a["faster"] += some and (not c_ok or int(nodes[upto][su].min()) < cn)
        if "cap_dropped" in r:
            dr = r["cap_dropped"] > 0
            cap["searches"] += len(S)
            cap["dropped"] += int(dr.sum())
            cap["below_budget"] += int((~S & (nodes < budget)).sum())
            if "cap_first_bind" in r:
                cb = r["cap_first_bind"] >= 0
                cap["could_bind"] = (cap["could_bind"] or 0) + int(cb.sum())
                cap["solved_could_bind"] = (cap["solved_could_bind"] or 0) + int((cb & S).sum())
    n_ctl_unsolved = n_rows - ctl_solved
    table = {}
    for name, m, _ in buckets:
        a = acc[name]
        table[name] = dict(
            starts=int(m.sum()), solved=_frac(a["solved"] / n_rows),
            solved_on_control_solved=_frac(a["solved_cs"] / ctl_solved) if ctl_solved else None,
            solved_on_control_unsolved=_frac(a["solved_cu"] / n_ctl_unsolved) if n_ctl_unsolved else None,
            fewer=_frac(a["fewer"] / n_rows), same=_frac(a["same"] / n_rows), more=_frac(a["more"] / n_rows),
            unsolved=_frac(a["unsolved"] / n_rows),
            oracle=dict(solved_by_some=a["some"], gained_over_control=a["gained"],
                        control_solved_lost_by_every=a["lost"], some_faster_than_control=a["faster"]))
    best = int(per_word.argmax())
    summary = dict(
        rows=n_rows, extra=sc.extra, lengths=[sc.min_len, sc.max_len], budget=budget, cap=sc.search.cap,
        starts_per_row=len(cs), searches=n_rows * len(cs), control_solved=ctl_solved, buckets=table,
        best_single=dict(word=word_str([ws[j] for j in cs[best]]), solved=int(per_word[best])),
        cap_counters=dict(fields=names, **cap), core_seconds=round(secs, 2),
        **({} if wall is None else {"wall_seconds": round(wall, 2)}))
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(d, "summary.md"), "w") as f:
        f.write(_markdown(summary))
    return summary


def _markdown(s):
    pct = lambda x: "-" if x is None else f"{100 * x:.1f}%"
    out = [f"# rank {2 + s['extra']} brute force: {s['rows']} rows, budget {s['budget']}, cap {s['cap']}",
           "", f"Control solves {s['control_solved']} of {s['rows']}. {s['searches']:,} searches "
           f"({s['starts_per_row']:,} starts per row), words of length {s['lengths'][0]} to {s['lengths'][1]}.", "",
           "| bucket | starts | solved | on control-solved | on control-unsolved | fewer | same | more | unsolved "
           "| solved by some | gained | lost | some faster |", "|" + "---|" * 13]
    for name, t in s["buckets"].items():
        o = t["oracle"]
        out.append(f"| {name} | {t['starts']:,} | {pct(t['solved'])} | {pct(t['solved_on_control_solved'])} | "
                   f"{pct(t['solved_on_control_unsolved'])} | {pct(t['fewer'])} | {pct(t['same'])} | {pct(t['more'])} | "
                   f"{pct(t['unsolved'])} | {o['solved_by_some']} | {o['gained_over_control']} | "
                   f"{o['control_solved_lost_by_every']} | {o['some_faster_than_control']} |")
    c = s["cap_counters"]
    out += ["", f"Best single start: `{s['best_single']['word']}` solves {s['best_single']['solved']} rows.", "",
            f"Cap counters ({', '.join(c['fields'] or []) or 'none'}): the cap dropped a child in {c['dropped']:,} of "
            f"{c['searches']:,} searches; "
            + ("no bind counter reported" if c["could_bind"] is None else
               f"could bind in {c['could_bind']:,} ({c['solved_could_bind']:,} solved)")
            + f"; {c['below_budget']:,} unsolved searches stopped below the budget.", ""]
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ verifier
def _cell(sc, pres, index, backend):
    ws = words_of(sc)
    c = combos(len(ws), sc.extra)[index]
    res = search(start(*pres.rels, [ws[j] for j in c]), sc.search.replace(backend=backend))
    return res


def verify(d, recheck=0, seed=0, log=print):
    """Check a result directory; return the list of failures (empty when it passes).

    1. control == null stabilisation; the null's dropped count equals the control's;
    2. each row file: ident, shapes, ``nodes <= budget``, solved iff ``path_len >= 0``;
    3. cap-counter consistency (when the search reports them);
    4. every stored path (control, sampled) replays on its start through ``acx.verify.replay``;
    5. ``recheck`` random cells re-run on the other backend agree on solved, pops, path length and the counters.
    """
    with open(os.path.join(d, "config.json")) as f:
        key = json.load(f)
    sc = SweepConfig.from_cfg({"search": key["sweep"]["search"],
                               "rankn": {k: v for k, v in key["sweep"].items() if k != "search"}})
    rows = {r.id: r for r in data.rows(key["benchmark"])}
    ws = words_of(sc)
    cs = combos(len(ws), sc.extra)
    budget, bad = sc.search.budget, []
    rng = random.Random(seed)
    files = sorted(f[:-4] for f in os.listdir(os.path.join(d, "rows")) if f.endswith(".npz"))
    for rid in files:
        r = load_row(row_path(d, rid))
        pres = rows[rid].pres
        fail = lambda msg, rid=rid: bad.append(f"row {rid}: {msg}")
        if r["ident"] != ident_of(sc, rid, pres):
            fail("ident differs from the config")
            continue
        c, nl = r["control"], r["null"]
        if tuple(c[k] for k in ("solved", "pops", "path_len")) != tuple(nl[k] for k in ("solved", "pops", "path_len")):
            fail("control != null stabilisation")
        for k, v in c["counters"].items():          # the Z_i never take part in a move: same drops, scores shifted by extra
            want = v + sc.extra if k == "cap_dropped_min_total" and v is not None else v
            if nl["counters"].get(k) != want:
                fail(f"{k} differs between the control ({v}) and the null stabilisation ({nl['counters'].get(k)})")
        shapes = [k for k in ("nodes", "path_len", "min_total", *COUNTERS) if k in r and r[k].shape != (len(cs),)]
        if shapes:
            fail(f"arrays {shapes} have the wrong shape")
            continue
        S, nodes = r["path_len"] >= 0, r["nodes"].astype(np.int64)
        if (nodes > budget).any() or (nodes < 1).any():
            fail("pops outside 1..budget")
        if (S & (nodes > budget)).any():
            fail("solved after the budget")
        _check_counters(r, S, nodes, budget, sc, fail)
        try:
            if c["solved"]:
                replay(pres, decode_path(c["path"]), cyclic=sc.search.cyclic, cap=sc.search.cap)
            for p in r["paths"]:
                combo = cs[p["index"]]
                if p["word"] != word_str([ws[j] for j in combo]) or not S[p["index"]] or int(nodes[p["index"]]) != p["pops"]:
                    fail(f"sampled path {p['index']} does not match the arrays")
                    continue
                replay(start(*pres.rels, [ws[j] for j in combo]), decode_path(p["path"]),
                       cyclic=sc.search.cyclic, cap=sc.search.cap)
        except ValueError as e:
            fail(f"replay: {e}")
    other = "spec" if sc.search.backend == "fast" else "fast"
    names = counter_fields(sc.search)
    for _ in range(recheck if files else 0):
        rid, i = rng.choice(files), rng.randrange(len(cs))
        r = load_row(row_path(d, rid))
        res = _cell(sc, rows[rid].pres, i, other)
        got = (bool(res.solved), res.pops, -1 if res.path_length is None else res.path_length)
        want = (bool(r["path_len"][i] >= 0), int(r["nodes"][i]), int(r["path_len"][i]))
        cc = cap_counters(res.stats, names)
        if got != want or any((-1 if cc[k] is None else cc[k]) != int(r[k][i]) for k in names):
            bad.append(f"row {rid} start {i}: {other} backend gives {got} {cc}, file has {want}")
    log(f"verify {d}: {len(files)} rows, {len(bad)} failures")
    return bad


def _check_counters(r, S, nodes, budget, sc, fail):
    """The relations every cap-counter set must satisfy (ported from the baseline's ``cap_violations``)."""
    if "cap_dropped" not in r:
        return
    dropped = r["cap_dropped"].astype(np.int64)
    cap = sc.search.cap
    if "cap_dropped_min_total" in r:
        mn = r["cap_dropped_min_total"].astype(np.int64)
        if ((mn >= 0) != (dropped > 0)).any():
            fail("a smallest dropped score iff something was dropped")
        if cap is not None and ((mn >= 0) & (mn <= cap)).any():
            fail("a dropped child whose total is within the cap")
    if "cap_first_bind" in r:
        b = r["cap_first_bind"].astype(np.int64)
        has = b >= 0
        if (has & (dropped == 0)).any():
            fail("a bind without a drop")
        if (has & ((b < 2) | (b > nodes + 1))).any():
            fail("a bind outside 2..pops+1")
        if (has & (b == nodes + 1) & (nodes >= budget)).any():
            fail("a frontier-empty bind at the full budget")
        if (has & (b == nodes + 1) & S).any():
            fail("a frontier-empty bind on a solved search")
        if "cap_would_pop" not in r and ((~S) & (nodes < budget) & (dropped > 0) & ~has).any():
            fail("an unsolved search below the budget with drops and no bind")
    if "cap_would_pop" in r:
        w = r["cap_would_pop"].astype(np.int64)
        if (w > dropped).any():
            fail("cap_would_pop above cap_dropped")
        if "cap_first_bind" in r and ((w > 0) != (r["cap_first_bind"] >= 0)).any():
            fail("cap_would_pop > 0 must hold exactly when there is a bind")
        if "cap_needed" in r:
            nd = r["cap_needed"].astype(np.int64)
            if ((w > 0) != (nd >= 0)).any():
                fail("cap_needed must be set exactly when cap_would_pop > 0")
            if cap is not None and ((nd >= 0) & (nd <= cap)).any():
                fail("cap_needed within the cap")


# ---------------------------------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="rank-n brute-force sweep (the config is the runner's TOML, method 'rankn')")
    ap.add_argument("--config", required=True)
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--rows")
    ap.add_argument("--out", default="results")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--verify", type=int, metavar="N", help="after the run, re-run N random cells on the other backend")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, args.set + ([f'rows="{args.rows}"'] if args.rows else []))
    summary = run(cfg, args.out, args.fresh)
    print(json.dumps({k: v for k, v in summary.items() if k != "buckets"}, indent=1))
    if args.verify is not None:
        bad = verify(os.path.join(args.out, cfg["name"]), recheck=args.verify)
        if bad:
            raise SystemExit("\n".join(bad[:20]))


if __name__ == "__main__":
    main()
