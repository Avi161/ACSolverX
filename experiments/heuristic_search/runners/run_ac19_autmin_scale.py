"""Colab-scale runner for ``data/AC19_extended_aut_min.csv`` @ budget 1k.

Arms: length ``baseline``, ``s20_mk2`` (L+20S+2MK), ``s28`` (L+28S),
``s28_mk2_f8`` (L+28S+2MK+8Fsign). F arms go through ``search_signlag``;
others through hcompact HIGH_SPEEDUP. Drive flock / heartbeat / resume
match ``run_ab``.

    from experiments.heuristic_search.runners.run_ac19_autmin_scale import (
        run_ac19_autmin_scale, load_rows)
    run_ac19_autmin_scale(cfg, out_dir=...)
"""
from __future__ import annotations

import csv
import fcntl
import json
import multiprocessing as mp
import os
import queue as queue_mod
import shutil
import sys
import time

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners import run_ab  # noqa: E402

ROOT = _d
CSV_PATH = os.path.join(ROOT, "data", "AC19_extended_aut_min.csv")
DATASET_NAME = "ac19_extended_aut_min"

# arm -> (weight config or None, wF). wF>0 => search_signlag path.
DEFAULT_ARMS = ("baseline", "s20_mk2", "s28", "s28_mk2_f8")


def _cfg(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


ARM_SPECS = {
    "baseline": (None, 0.0),
    "s20": (_cfg(L=1.0, S=20.0), 0.0),
    "s20_mk2": (_cfg(L=1.0, S=20.0, MK=2.0), 0.0),
    "s28": (_cfg(L=1.0, S=28.0), 0.0),
    "s28_mk2": (_cfg(L=1.0, S=28.0, MK=2.0), 0.0),
    "s28_mk2_f8": (_cfg(L=1.0, S=28.0, MK=2.0), 8.0),
}

# Keep run_ab.ARMS in sync for non-F arms (resolve_workers / warm imports).
run_ab.ARMS.update({k: v[0] for k, v in ARM_SPECS.items()})

_HB_Q = None


def load_rows():
    """``[{name, r1, r2, n_members}]`` from the Aut-min CSV."""
    rows = []
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "name": r["name"],
                "r1": r["r1"],
                "r2": r["r2"],
                "n_members": int(r["n_members"]),
            })
    return rows


def _stride_chunk(rows, chunks, chunk_index):
    if not chunks or chunks <= 1 or chunk_index is None:
        return rows, ""
    if not (1 <= int(chunk_index) <= int(chunks)):
        raise ValueError(f"CHUNK_INDEX must be 1..{chunks}, got {chunk_index}")
    i = int(chunk_index) - 1
    n = int(chunks)
    picked = [r for k, r in enumerate(rows) if k % n == i]
    return picked, f"_c{chunk_index}of{chunks}"


def _report(out, cfg):
    data = [json.loads(l) for l in open(out) if l.strip()]
    arms = list(cfg["ARMS"])
    pts = [b for b in cfg["CHECKPOINTS"] if b <= cfg["NODE_BUDGET"]]
    by_name = {}
    for r in data:
        by_name.setdefault(r["name"], {})[r["arm"]] = r
    complete = [nm for nm, m in by_name.items() if all(a in m for a in arms)]
    n = len(complete)

    def curve(arm):
        return [sum(1 for nm in complete
                    if by_name[nm][arm].get("solved_at") is not None
                    and by_name[nm][arm]["solved_at"] <= b)
                for b in pts]

    lines = [
        f"# A/B — {cfg['DATASET']}, budget {cfg['NODE_BUDGET']:,}, "
        f"cap {cfg['MAX_RELATOR_LENGTH']}",
        "",
        f"{n} complete presentations (all {len(arms)} arms; "
        f"{len(by_name) - n} partial ignored).",
        "",
        "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
        "|---" * (len(pts) + 1) + "|",
    ]
    curves = {a: curve(a) for a in arms}
    for a in arms:
        lines.append(
            f"| {a} | " + " | ".join(f"{v}/{n}" for v in curves[a]) + " |")
    if "baseline" in curves and n and len(arms) > 1:
        base = curves["baseline"]
        lines += ["", "## Δ vs length baseline", "",
                  "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
                  "|---" * (len(pts) + 1) + "|"]
        for a in arms:
            if a == "baseline":
                continue
            g = [x - y for x, y in zip(curves[a], base)]
            lines.append(
                f"| {a} | " + " | ".join(f"{v:+d}" for v in g) + " |")
    md = out.replace(".jsonl", ".md")
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    print(f"  wrote {md}", flush=True)


def _init_worker(q):
    global _HB_Q
    _HB_Q = q


def _worker_solve(job):
    """Spawn-safe worker. F arms use search_signlag; else hcompact (+ cert recovery)."""
    (arm, cfg_arm, wF, row, budget, mrl, engine, keep_path, hb_secs) = job
    from experiments.heuristic_search.core.hcompact import (  # noqa: WPS433
        greedy_search_hcompact,
    )
    from experiments.heuristic_search.core.hsolve import greedy_search_h  # noqa: WPS433
    from experiments.heuristic_search.core.search_signlag import (  # noqa: WPS433
        search_signlag,
    )

    state = {"last": time.time() + min(10.0, hb_secs), "prev": 0,
             "t_prev": time.time()}

    def progress(n):
        now = time.time()
        if now < state["last"]:
            return
        rate = (n - state["prev"]) / max(now - state["t_prev"], 1e-9)
        state["last"], state["prev"], state["t_prev"] = now + hb_secs, n, now
        if _HB_Q is not None:
            try:
                _HB_Q.put_nowait((arm, row["name"], n, budget, rate))
            except Exception:
                pass

    try:
        t = time.perf_counter()
        if float(wF) > 0.0:
            res = search_signlag(row["r1"], row["r2"], budget, cfg_arm, mrl,
                                 wF=float(wF))
            # search_signlag has no path_moves — pad fields for jsonl schema
            res = {
                "solved": res["solved"],
                "nodes_explored": res["nodes_explored"],
                "path_length": res.get("path_length"),
                "min_relator_length": res.get("min_relator_length"),
                "max_relator_length_expanded": res.get(
                    "max_relator_length_expanded"),
                "path_moves": res.get("path_moves"),
                "wF": float(wF),
            }
        elif engine == "hcompact":
            res = greedy_search_hcompact(
                row["r1"], row["r2"], budget, max_relator_length=mrl,
                config=cfg_arm, progress=progress)
            if res["solved"]:
                rec = greedy_search_h(
                    row["r1"], row["r2"], budget, max_relator_length=mrl,
                    config=cfg_arm, progress=progress, keep_path=True)
                assert (rec["solved"], rec["nodes_explored"],
                        rec["path_length"]) == (
                    True, res["nodes_explored"], res["path_length"]), \
                    (row["name"], arm, "recovery diverged")
                res = rec
        else:
            res = greedy_search_h(
                row["r1"], row["r2"], budget, max_relator_length=mrl,
                config=cfg_arm, progress=progress, keep_path=keep_path)
            if res["solved"] and not keep_path:
                rec = greedy_search_h(
                    row["r1"], row["r2"], budget, max_relator_length=mrl,
                    config=cfg_arm, progress=progress, keep_path=True)
                assert (rec["solved"], rec["nodes_explored"],
                        rec["path_length"]) == (
                    True, res["nodes_explored"], res["path_length"])
                res = rec
        dt = time.perf_counter() - t
        return {"arm": arm, "name": row["name"], "res": res, "secs": round(dt, 2)}
    except Exception as e:  # noqa: BLE001
        return {"arm": arm, "name": row["name"], "__error__": repr(e)}


def _run_parallel(cfg, out, todo, n_workers, budget, mrl, engine, keep_path,
                  heartbeat_secs, progress_secs):
    remote = out.startswith(run_ab._REMOTE_PREFIX)
    if remote:
        stage_dir = cfg.get("STAGE_DIR") or os.path.join(
            os.path.expanduser("~"), ".hsearch_stage")
        os.makedirs(stage_dir, exist_ok=True)
        stage = os.path.join(stage_dir, os.path.basename(out))
        if run_ab._n_lines(out) > run_ab._n_lines(stage):
            shutil.copyfile(out, stage)
            print(f"  seeded stage from the mirror ({run_ab._n_lines(stage)} rows)",
                  flush=True)
    else:
        stage = out

    lock_fd = os.open(stage + ".lock", os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(lock_fd)
        raise RuntimeError(
            f"{stage} is flock-claimed by a live process — kill orphans "
            "before re-running.") from None

    ctx = mp.get_context("spawn")
    hb_q = ctx.Queue()
    jobs = []
    for arm, row in todo:
        if arm not in ARM_SPECS:
            raise KeyError(f"unknown arm {arm!r}; known={sorted(ARM_SPECS)}")
        cfg_arm, wF = ARM_SPECS[arm]
        jobs.append((arm, cfg_arm, wF, row, budget, mrl, engine, keep_path,
                     heartbeat_secs))

    t0 = time.perf_counter()
    done = solved = errors = 0
    last_pg = t0

    with ctx.Pool(n_workers, initializer=_init_worker, initargs=(hb_q,)) as pool, \
            open(stage, "a") as f:
        pending = [pool.apply_async(_worker_solve, (j,)) for j in jobs]
        last_mirror = time.perf_counter()
        while pending:
            try:
                while True:
                    a, name, n, b, rate = hb_q.get(
                        timeout=1.0 if not any(p.ready() for p in pending)
                        else 0.0)
                    print(f"      [{a}/{name}] {n:,}/{b:,} nodes  "
                          f"{rate:,.0f} nodes/s", flush=True)
            except queue_mod.Empty:
                pass

            ready = [p for p in pending if p.ready()]
            if not ready:
                continue
            pending = [p for p in pending if not p.ready()]
            for p in ready:
                r = p.get()
                if "__error__" in r:
                    errors += 1
                    print(f"    WORKER ERROR [{r['arm']}/{r['name']}]: "
                          f"{r['__error__']} — not written; resume retries",
                          flush=True)
                    continue
                res = r["res"]
                f.write(json.dumps({
                    "arm": r["arm"], "name": r["name"],
                    "dataset": cfg["DATASET"],
                    "budget": budget, "mrl": mrl,
                    "solved": res["solved"],
                    "solved_at": (res["nodes_explored"] if res["solved"]
                                  else None),
                    "nodes_explored": res["nodes_explored"],
                    "path_length": res.get("path_length"),
                    "min_relator_length": res.get("min_relator_length"),
                    "max_relator_length_expanded": res.get(
                        "max_relator_length_expanded"),
                    "path_moves": res.get("path_moves"),
                    "wF": res.get("wF", 0.0),
                    "secs": r["secs"],
                }) + "\n")
                f.flush()
                os.fsync(f.fileno())
                done += 1
                solved += bool(res["solved"])

            now = time.perf_counter()
            if remote and now - last_mirror >= 60:
                run_ab._mirror(stage, out)
                last_mirror = now
            if now - last_pg >= progress_secs or not pending:
                el = now - t0
                eta = el / max(done, 1) * len(pending)
                print(f"    {done}/{len(jobs)} searches  {solved} solved  "
                      f"{errors} errors  {el/60:.1f} min elapsed  "
                      f"ETA {eta/60:.1f} min  [{n_workers} workers]",
                      flush=True)
                last_pg = now

    if remote:
        run_ab._mirror(stage, out)
    os.close(lock_fd)
    return stage


def run_ac19_autmin_scale(cfg, out_dir="results/hsearch", heartbeat_secs=60,
                          progress_secs=300):
    rows = load_rows()
    chunks = cfg.get("CHUNKS") or 1
    chunk_index = cfg.get("CHUNK_INDEX")
    rows, tag = _stride_chunk(rows, chunks, chunk_index)

    subset = cfg.get("SUBSET")
    if subset is not None:
        rows = rows[: int(subset)]

    cfg = dict(cfg)
    cfg["DATASET"] = DATASET_NAME
    if not cfg.get("ARMS"):
        cfg["ARMS"] = list(DEFAULT_ARMS)
    for a in cfg["ARMS"]:
        if a not in ARM_SPECS:
            raise KeyError(f"unknown arm {a!r}; known={sorted(ARM_SPECS)}")

    stem = cfg.get("OUT_STEM", "hsearch_ac19_autmin_1k")
    if tag:
        stem = f"{stem}{tag}"
    cfg["OUT_STEM"] = stem

    budget = cfg["NODE_BUDGET"]
    mrl = cfg["MAX_RELATOR_LENGTH"]
    arms = list(cfg["ARMS"])
    keep_path = cfg.get("KEEP_PATH", False)
    engine = cfg.get("ENGINE", "hcompact")
    if engine not in ("hsolve", "hcompact"):
        raise ValueError(f"unknown ENGINE {engine!r}")

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(
        out_dir, f"{stem}_{DATASET_NAME}_b{budget}_mrl{mrl}.jsonl")

    stage_probe = (os.path.join(
        cfg.get("STAGE_DIR") or os.path.join(os.path.expanduser("~"),
                                             ".hsearch_stage"),
        os.path.basename(out))
        if out.startswith(run_ab._REMOTE_PREFIX) else out)
    seen = ((run_ab._done(out) | run_ab._done(stage_probe))
            if cfg.get("RESUME", True) else set())
    todo = [(a, {"name": r["name"], "r1": r["r1"], "r2": r["r2"]})
            for r in rows for a in arms
            if (a, r["name"]) not in seen]
    n_workers, per_gb = run_ab._resolve_workers(
        cfg, budget, mrl, engine, keep_path)
    print(f"  {len(arms)} arms x {len(rows)} presentations, budget {budget:,}, "
          f"cap {mrl}  [JOB_ORDER=presentation] arms={arms}"
          + ("  [engine: hcompact; F arms via search_signlag]"
             if engine == "hcompact" else "")
          + (f"  [{n_workers} workers, ~{per_gb:.1f} GB/search]"
             if n_workers > 1 else ""), flush=True)
    print(f"  {len(seen)} rows resumed; {len(todo)} to run", flush=True)
    print(f"  -> {out}", flush=True)

    n_workers = max(int(n_workers), 1)
    _run_parallel(cfg, out, todo, n_workers, budget, mrl, engine,
                  keep_path, heartbeat_secs, progress_secs)
    _report(out, cfg)
    return out
