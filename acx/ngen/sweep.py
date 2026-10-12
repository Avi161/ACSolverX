"""Rank-n brute force: stabilise each row with words, then search every stabilised start (``docs/RANK3.md``).

``python -m acx.ngen.sweep --config configs/rank3_bf.toml [--rows 0:40] [--set key=value] [--verify N]``. A start is
``<x, y, z1.. | r1, r2, Z1.w1, ..>`` for words ``w_i`` in ``x, y``, searched by ``acx.search.search``. Each row also
gets its 2-generator control and its null stabilisation (empty words), which must agree. Results go to
``<out>/<name>/``: ``config.json``, ``rows/<id>.npz`` (written atomically, so a killed run resumes) and ``summary.json``.
"""
import argparse
import hashlib
import itertools
import json
import os
import random
import shutil
import time
import tomllib
from contextlib import nullcontext
from dataclasses import asdict, dataclass, fields
from functools import lru_cache
from multiprocessing import Pool

import numpy as np

from .. import data
from ..core.capcount import FIELDS
from ..core.config import SearchConfig, parse_override
from ..core.moves import decode_path, encode_path
from ..core.words import Presentation, fmt, inverse as invert
from ..search import search
from ..verify.replay import replay

LETTERS = (1, 2, -1, -2)                    # x, y, X, Y
COUNTERS = FIELDS[1:]                       # the cap counters of acx.core.capcount (FIELDS[0] is the cap itself)
KEYS = {"name", "method", "benchmark", "rows", "workers", "search", "rankn"}


class SweepError(RuntimeError):
    """A row file from another run, or a control that disagrees with its null stabilisation."""


# ---------------------------------------------------------------------------------------- words and starts
@lru_cache(maxsize=None)
def reduced_words(n):
    """Freely reduced words of length ``n`` over x, y, X, Y, one of each pair ``{w, w^-1}`` (the larger), depth-first."""
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


@lru_cache(maxsize=None)
def pool(min_len, max_len, inverted):
    """The words of lengths ``min_len..max_len`` (each word's inverse when ``inverted``), in ``reduced_words`` order."""
    ws = tuple(w for n in range(min_len, max_len + 1) for w in reduced_words(n))
    return tuple(invert(w) for w in ws) if inverted else ws


@lru_cache(maxsize=None)
def combos(n_words, extra):
    """Index tuples of the starts: every multiset of ``extra`` words (one word each for ``extra = 1``)."""
    return tuple(itertools.combinations_with_replacement(range(n_words), extra))


def word_str(ws):
    """``"x"`` for one word, ``"x,yX"`` for several."""
    return ",".join(fmt(w) for w in ws)


def sampled(rid, wstr, frac):
    """Whether a solved start keeps its path: a fixed hash of ``id|word`` below ``frac``."""
    h = hashlib.md5(f"{rid}|{wstr}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64 < frac


# -------------------------------------------------------------------------------------------------- config
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
        """From a runner-style dict with sections ``search`` and ``rankn``; unknown keys are errors."""
        raw = dict(cfg.get("rankn", {}))
        bad = set(raw) - {f.name for f in fields(cls) if f.name != "search"}
        if bad:
            raise ValueError(f"unknown rankn keys {sorted(bad)}")
        return cls(search=SearchConfig.from_dict({**cfg.get("search", {}), "capture_path": True}), **raw)

    def key(self):
        """What a result directory holds; backend, capture and trace are left out (both backends give the same rows)."""
        d = asdict(self)
        d["search"] = {k: v for k, v in d["search"].items() if k not in ("backend", "capture_path", "trace")}
        return d


def words_of(sc):
    """The word pool of a config."""
    return pool(sc.min_len, sc.max_len, sc.inverse)


def ident_of(sc, rid, pres):
    """What a row file must say about itself: its row, the config and the word pool."""
    pool_hash = hashlib.md5(",".join(map(fmt, words_of(sc))).encode()).hexdigest()
    return json.dumps({"id": rid, "r1": fmt(pres.rels[0]), "r2": fmt(pres.rels[1]), "config": sc.key(),
                       "pool": pool_hash}, sort_keys=True, separators=(",", ":"))


# --------------------------------------------------------------------------------------------------- a row
def _record(res):
    """One search as a record: solved, pops, path length (None unsolved), smallest total and the cap counters."""
    return {"solved": res.solved, "pops": res.pops, "path_len": res.path_length,
            "min_total": res.stats["min_total"], **{k: res.stats[k] for k in COUNTERS}}


def _key(rec):
    """What the control and the null stabilisation must agree on."""
    return rec["solved"], rec["pops"], rec["path_len"]


def sweep_row(rid, pres, sc):
    """The arrays of one row file: the control, the null stabilisation and every start of the pool (by index)."""
    t0 = time.perf_counter()
    scfg, r1, r2 = sc.search, *pres.rels
    cres = search(Presentation(2, (r1, r2)), scfg)
    control, null = _record(cres), _record(search(start(r1, r2, [()] * sc.extra), scfg))
    if _key(control) != _key(null):
        raise SweepError(f"row {rid}: the control {_key(control)} and the null stabilisation {_key(null)} differ")
    if cres.solved:
        control["path"] = encode_path(cres.path)
    ws = words_of(sc)
    recs, paths = [], []
    for i, c in enumerate(combos(len(ws), sc.extra)):
        wd = [ws[j] for j in c]
        res = search(start(r1, r2, wd), scfg)
        recs.append(_record(res))
        if res.solved and sampled(rid, word_str(wd), sc.sample):
            paths.append({"index": i, "word": word_str(wd), "pops": res.pops, "path": encode_path(res.path)})

    def col(key, dtype=np.int32):
        return np.array([-1 if r[key] is None else r[key] for r in recs], dtype)

    return {"nodes": col("pops", np.uint16), "path_len": col("path_len", np.int16), "min_total": col("min_total"),
            **{k: col(k) for k in COUNTERS},
            "control": np.array(json.dumps(control)), "null": np.array(json.dumps(null)),
            "paths": np.array(json.dumps(paths)), "seconds": np.float32(time.perf_counter() - t0),
            "ident": np.array(ident_of(sc, rid, pres))}


def row_path(d, rid):
    """The row file of ``rid`` under the result directory ``d``."""
    return os.path.join(d, "rows", f"{rid}.npz")


def load_row(path):
    """A row file as a dict of arrays, with the JSON records parsed and ``ident`` as a string."""
    with np.load(path) as z:
        r = {k: z[k] for k in z.files}
    for k in ("control", "null", "paths"):
        r[k] = json.loads(str(r[k]))
    r["ident"] = str(r["ident"])
    return r


def _task(args):
    """Sweep one row into its file, unless the file is there (then it must belong to this run)."""
    d, rid, pres, sc = args
    path, ident = row_path(d, rid), ident_of(sc, rid, pres)
    if os.path.exists(path):
        got = load_row(path)["ident"]
        if got != ident:
            raise SweepError(f"{path} is not from this run: has {got}, expected {ident}")
        return
    out = sweep_row(rid, pres, sc)
    tmp = f"{path}.tmp{os.getpid()}.npz"
    np.savez_compressed(tmp, **out)
    os.replace(tmp, path)


# ------------------------------------------------------------------------------------------------- the run
def load_config(path, overrides=()):
    """The TOML at ``path`` (method ``rankn``) plus ``key=value`` overrides; the name defaults to the file name."""
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
    if set(cfg) - KEYS:
        raise ValueError(f"unknown config keys {sorted(set(cfg) - KEYS)}")
    if "benchmark" not in cfg:
        raise ValueError("config needs a benchmark")
    SweepConfig.from_cfg(cfg)
    return cfg


def run(cfg, out="results", fresh=False, log=print):
    """Sweep the selected rows of ``cfg`` into ``<out>/<name>/``; write and return the summary."""
    from ..runner import select
    sc = SweepConfig.from_cfg(cfg)
    rows = select(data.rows(cfg["benchmark"]), cfg.get("rows"))
    d = os.path.join(out, cfg["name"])
    if fresh:
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "rows"), exist_ok=True)
    key = {"benchmark": cfg["benchmark"], "method": "rankn", "sweep": sc.key()}
    cfg_file = os.path.join(d, "config.json")
    if os.path.exists(cfg_file):
        with open(cfg_file) as f:
            if json.load(f) != key:
                raise SystemExit(f"{d} holds a run with another config: pass --fresh or another name")
    with open(cfg_file, "w") as f:
        json.dump(key, f, indent=1)
    n_words = len(words_of(sc))
    done = sum(os.path.exists(row_path(d, r.id)) for r in rows)
    log(f"{cfg['name']}: rankn (extra {sc.extra}, lengths {sc.min_len}-{sc.max_len}, {n_words} words, "
        f"{len(combos(n_words, sc.extra))} starts per row) on {cfg['benchmark']}, {len(rows)} rows ({done} done)")
    t0 = time.perf_counter()
    workers = cfg.get("workers", 1)
    tasks = [(d, r.id, r.pres, sc) for r in rows]
    with (Pool(workers) if workers > 1 else nullcontext()) as pl:
        mapper = map if pl is None else pl.imap_unordered
        for n, _ in enumerate(mapper(_task, tasks), 1):
            if n % 50 == 0 or n == len(tasks):
                log(f"  {n}/{len(tasks)} rows")
    return summarize(d, wall=time.perf_counter() - t0, rows=[r.id for r in rows])


# ------------------------------------------------------------------------------------------------ summary
def _frac(x):
    return round(float(x), 4)


def summarize(d, wall=None, rows=None):
    """Stream the row files of ``d`` into ``summary.json`` and ``summary.md``; return the summary.

    Fractions are per presentation, averaged over presentations. "Fewer" counts every solve when the control fails.
    The oracle counts a presentation as solved when some word of the bucket (up to that length) solves it.
    """
    with open(os.path.join(d, "config.json")) as f:
        key = json.load(f)["sweep"]
    sc = SweepConfig.from_cfg({"search": key["search"], "rankn": {k: v for k, v in key.items() if k != "search"}})
    ws = words_of(sc)
    wl = np.array([len(w) for w in ws])
    cs = combos(len(ws), sc.extra)
    if sc.extra == 1:
        buckets = [(f"L{n}", wl == n, wl <= n) for n in range(sc.min_len, sc.max_len + 1)]
    else:
        buckets = [("all", np.ones(len(cs), bool), np.ones(len(cs), bool))]
    ids = rows if rows is not None else sorted(f[:-4] for f in os.listdir(os.path.join(d, "rows")) if f.endswith(".npz"))
    acc = {name: dict(solved=0.0, solved_cs=0.0, solved_cu=0.0, fewer=0.0, same=0.0, more=0.0, unsolved=0.0,
                      some=0, gained=0, lost=0, faster=0) for name, _, _ in buckets}
    n_rows = ctl_solved = cap_searches = dropped = below = could = solved_could = 0
    per_word = np.zeros(len(cs), dtype=np.int64)
    secs = 0.0
    for rid in ids:
        r = load_row(row_path(d, rid))
        cn, c_ok = r["control"]["pops"], bool(r["control"]["solved"])
        S, nodes = r["path_len"] >= 0, r["nodes"].astype(np.int64)
        n_rows += 1
        ctl_solved += c_ok
        secs += float(r["seconds"])
        per_word += S
        for name, m, upto in buckets:
            a, s, nd = acc[name], S[m], nodes[m]
            a["solved"] += s.mean()
            a["solved_cs" if c_ok else "solved_cu"] += s.mean()
            a["fewer"] += (s & (nd < cn) if c_ok else s).mean()
            a["same"] += (s & (nd == cn)).mean() if c_ok else 0.0
            a["more"] += (s & (nd > cn)).mean() if c_ok else 0.0
            a["unsolved"] += (~s).mean()
            su = S[upto]
            some = bool(su.any())
            a["some"] += some
            a["gained"] += some and not c_ok
            a["lost"] += c_ok and not some
            a["faster"] += some and (not c_ok or int(nodes[upto][su].min()) < cn)
        cap_searches += len(S)
        dropped += int((r["cap_dropped"] > 0).sum())
        below += int((~S & (nodes < sc.search.budget)).sum())
        bind = r["cap_first_bind"] >= 0
        could += int(bind.sum())
        solved_could += int((bind & S).sum())
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
        rows=n_rows, extra=sc.extra, lengths=[sc.min_len, sc.max_len], budget=sc.search.budget, cap=sc.search.cap,
        starts_per_row=len(cs), searches=n_rows * len(cs), control_solved=ctl_solved, buckets=table,
        best_single=dict(word=word_str([ws[j] for j in cs[best]]), solved=int(per_word[best])),
        cap_counters=dict(fields=list(COUNTERS), searches=cap_searches, dropped=dropped, could_bind=could,
                          solved_could_bind=solved_could, below_budget=below),
        core_seconds=round(secs, 2), **({} if wall is None else {"wall_seconds": round(wall, 2)}))
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(d, "summary.md"), "w") as f:
        f.write(_markdown(summary))
    return summary


def _markdown(s):
    """The summary as a markdown page: the bucket table, the best single start and the cap counters."""
    pct = lambda x: "-" if x is None else f"{100 * x:.1f}%"
    out = [f"# rank {2 + s['extra']} brute force: {s['rows']} rows, budget {s['budget']}, cap {s['cap']}", "",
           f"Control solves {s['control_solved']} of {s['rows']}. {s['searches']:,} searches "
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
            f"Cap counters ({', '.join(c['fields'])}): the cap dropped a child in {c['dropped']:,} of "
            f"{c['searches']:,} searches; could bind in {c['could_bind']:,} ({c['solved_could_bind']:,} solved); "
            f"{c['below_budget']:,} unsolved searches stopped below the budget.", ""]
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ verifier
def verify(d, recheck=0, seed=0, log=print):
    """Check the result directory ``d``; return the failures (an empty list when it passes).

    Per row: ident and array shapes; control equals the null stabilisation, and the null's counters equal the
    control's (smallest score + ``extra``); pops in ``1..budget``; the cap-counter rules (``_check_counters``); every
    stored path (control and sampled) replays on its start through ``acx.verify.replay``. Then ``recheck`` random
    cells re-run on the other backend must agree on solved, pops, path length and the counters.
    """
    with open(os.path.join(d, "config.json")) as f:
        key = json.load(f)
    sc = SweepConfig.from_cfg({"search": key["sweep"]["search"],
                               "rankn": {k: v for k, v in key["sweep"].items() if k != "search"}})
    rows = {r.id: r for r in data.rows(key["benchmark"])}
    ws = words_of(sc)
    cs = combos(len(ws), sc.extra)
    bad = []
    files = sorted(f[:-4] for f in os.listdir(os.path.join(d, "rows")) if f.endswith(".npz"))
    for rid in files:
        r = load_row(row_path(d, rid))
        fail = lambda msg, rid=rid: bad.append(f"row {rid}: {msg}")
        if r["ident"] != ident_of(sc, rid, rows[rid].pres):
            fail("ident differs from the config")
            continue
        _check_row(r, rows[rid].pres, sc, ws, cs, fail)
    bad += _recheck(d, files, rows, sc, ws, cs, recheck, random.Random(seed))
    log(f"verify {d}: {len(files)} rows, {len(bad)} failures")
    return bad


def _check_row(r, pres, sc, ws, cs, fail):
    """The row-level checks of ``verify`` for one row file; each failure is passed to ``fail``."""
    c, nl, budget = r["control"], r["null"], sc.search.budget
    if _key(c) != _key(nl):
        fail("control != null stabilisation")
    for k in COUNTERS:      # the Z_i never take part in a move: the same drops, scores shifted by extra
        want = c[k] + sc.extra if k == "cap_dropped_min_total" and c[k] is not None else c[k]
        if nl[k] != want:
            fail(f"{k} differs between the control ({c[k]}) and the null stabilisation ({nl[k]})")
    shapes = [k for k in ("nodes", "path_len", "min_total", *COUNTERS) if r[k].shape != (len(cs),)]
    if shapes:
        fail(f"arrays {shapes} have the wrong shape")
        return
    S, nodes = r["path_len"] >= 0, r["nodes"].astype(np.int64)
    if (nodes > budget).any() or (nodes < 1).any():
        fail("pops outside 1..budget")
    _check_counters(r, S, nodes, budget, sc, fail)
    try:
        if c["solved"]:
            replay(pres, decode_path(c["path"]), cyclic=sc.search.cyclic, cap=sc.search.cap)
        for p in r["paths"]:
            wd = [ws[j] for j in cs[p["index"]]]
            if p["word"] != word_str(wd) or not S[p["index"]] or int(nodes[p["index"]]) != p["pops"]:
                fail(f"sampled path {p['index']} does not match the arrays")
                continue
            replay(start(*pres.rels, wd), decode_path(p["path"]), cyclic=sc.search.cyclic, cap=sc.search.cap)
    except ValueError as e:
        fail(f"replay: {e}")


def _recheck(d, files, rows, sc, ws, cs, n, rng):
    """``n`` random cells re-run on the other backend; the failures (solved, pops, path length, counters)."""
    other = "spec" if sc.search.backend == "fast" else "fast"
    bad = []
    for _ in range(n if files else 0):
        rid, i = rng.choice(files), rng.randrange(len(cs))
        r = load_row(row_path(d, rid))
        res = search(start(*rows[rid].pres.rels, [ws[j] for j in cs[i]]), sc.search.replace(backend=other))
        got = (bool(res.solved), res.pops, -1 if res.path_length is None else res.path_length)
        want = (bool(r["path_len"][i] >= 0), int(r["nodes"][i]), int(r["path_len"][i]))
        cc = {k: -1 if res.stats[k] is None else res.stats[k] for k in COUNTERS}
        if got != want or any(cc[k] != int(r[k][i]) for k in COUNTERS):
            bad.append(f"row {rid} start {i}: {other} backend gives {got} {cc}, file has {want}")
    return bad


def _check_counters(r, S, nodes, budget, sc, fail):
    """The relations the cap counters must satisfy (ported from the baseline's ``cap_violations``)."""
    dropped = r["cap_dropped"].astype(np.int64)
    mn, bind, would, need = (r[k].astype(np.int64) for k in
                             ("cap_dropped_min_total", "cap_first_bind", "cap_would_pop", "cap_needed"))
    cap, has = sc.search.cap, bind >= 0
    rules = [
        (((mn >= 0) != (dropped > 0)).any(), "a smallest dropped score iff something was dropped"),
        (cap is not None and ((mn >= 0) & (mn <= cap)).any(), "a dropped child whose total is within the cap"),
        ((has & (dropped == 0)).any(), "a bind without a drop"),
        ((has & ((bind < 2) | (bind > nodes + 1))).any(), "a bind outside 2..pops+1"),
        ((has & (bind == nodes + 1) & (nodes >= budget)).any(), "a frontier-empty bind at the full budget"),
        ((has & (bind == nodes + 1) & S).any(), "a frontier-empty bind on a solved search"),
        (((~S) & (nodes < budget) & (dropped > 0) & ~has).any(), "an unsolved search below the budget with drops and no bind"),
        ((would > dropped).any(), "cap_would_pop above cap_dropped"),
        (((would > 0) != has).any(), "cap_would_pop > 0 must hold exactly when there is a bind"),
        (((would > 0) != (need >= 0)).any(), "cap_needed must be set exactly when cap_would_pop > 0"),
        (cap is not None and ((need >= 0) & (need <= cap)).any(), "cap_needed within the cap"),
    ]
    for bad, msg in rules:
        if bad:
            fail(msg)


# ---------------------------------------------------------------------------------------------------- CLI
def main(argv=None):
    """``python -m acx.ngen.sweep``: run a rank-n config (the runner's TOML), print the summary, optionally verify."""
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
