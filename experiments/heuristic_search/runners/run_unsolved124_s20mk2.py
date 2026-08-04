"""Colab-scale ``s20_mk2`` census on the Aut-min 124 unsolved class reps.

Non-comparative single-arm census (not an A/B vs baseline). Starts are the
Aut-min reps in ``unsolved_124_aca_classes.csv`` (unchanged — not μ-ladder
floors). Arm is only ``s20_mk2 = L+20S+2MK``. Heap depth tie-break is the
shipped ``+depth`` (``hcompact`` / ``run_ab`` default).

New-files only: registers the arm, stride-chunks, own parallel write loop
(reuses ``run_ab`` worker helpers) so every row carries start + minimizing
pair + length-floor fields. Agent-local budget ≤ 1000; production = Colab.

    from experiments.heuristic_search.runners.run_unsolved124_s20mk2 import (
        run_unsolved124_s20mk2)
    run_unsolved124_s20mk2(cfg, out_dir=...)
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
from statistics import mean, median

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners import run_ab  # noqa: E402
from experiments.heuristic_search.core.hcompact import (  # noqa: E402
    greedy_search_hcompact,
)
from experiments.heuristic_search.core.hsolve import greedy_search_h  # noqa: E402

ROOT = _d
DATASET_NAME = "unsolved124"
UNSOLVED_CSV = run_ab.UNSOLVED_CSV


def _cfg(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


run_ab.ARMS.update({
    "s20_mk2": _cfg(L=1.0, S=20.0, MK=2.0),
    "baseline": None,
})


def assert_autmin_freeze(path=UNSOLVED_CSV):
    """Advisor: load_rows uses r1/r2 — assert they equal Aut-min reps."""
    bad = []
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["r1"] != r["rep_r1"] or r["r2"] != r["rep_r2"]:
                bad.append(r["aca_id"])
    if bad:
        raise AssertionError(
            f"{len(bad)} rows have r1/r2 != rep_*: {bad[:8]}")
    return True


def load_rows(subset=None):
    assert_autmin_freeze()
    rows = run_ab.load_rows(DATASET_NAME, subset)
    for r in rows:
        r["start_total"] = len(r["r1"]) + len(r["r2"])
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


def _row_record(arm, name, dataset, budget, mrl, res, secs, start):
    """Full jsonl row: search fields + start + min pair + length-floor flags."""
    r1, r2 = start["r1"], start["r2"]
    start_total = int(start.get("start_total", len(r1) + len(r2)))
    min_len = res.get("min_relator_length")
    min_delta = (start_total - int(min_len)) if min_len is not None else None
    path_moves = res.get("path_moves") or []
    solved = bool(res.get("solved"))
    # path_pending: solved but certificate not yet recovered (persist-first).
    path_pending = bool(res.get("path_pending", False))
    return {
        "arm": arm,
        "name": name,
        "dataset": dataset,
        "budget": budget,
        "mrl": mrl,
        "engine": "hcompact",
        "depth_tie": "+depth",
        "r1": r1,
        "r2": r2,
        "start_total": start_total,
        "solved": solved,
        "solved_at": (int(res["nodes_explored"]) if solved else None),
        "nodes_explored": int(res["nodes_explored"]),
        "path_length": res.get("path_length"),
        "min_relator_length": min_len,
        "min_relator": res.get("min_relator"),
        "min_delta": min_delta,
        "improved": bool(min_delta is not None and min_delta > 0),
        "max_relator_length_expanded": res.get("max_relator_length_expanded"),
        "path_moves": path_moves,
        "path_pending": path_pending,
        "secs": secs,
    }


def _worker_u124(job):
    """``hcompact`` search only — never recover the path here.

    Parent writes the row first (persist-before-enrich). Certificate recovery
    is a separate parent-side step that in-place updates ``path_pending`` rows.
    """
    arm, cfg_arm, row, budget, mrl, engine, _keep_path, hb_secs = job
    state = {"last": 0.0, "prev": 0, "t_prev": time.perf_counter()}

    def progress(n):
        now = time.perf_counter()
        if now < state["last"]:
            return
        rate = (n - state["prev"]) / max(now - state["t_prev"], 1e-9)
        state["last"], state["prev"], state["t_prev"] = now + hb_secs, n, now
        if run_ab._HB_Q is not None:
            try:
                run_ab._HB_Q.put_nowait((arm, row["name"], n, budget, rate))
            except Exception:
                pass

    try:
        if engine != "hcompact":
            raise ValueError("u124 census requires ENGINE=hcompact")
        t = time.perf_counter()
        res = greedy_search_hcompact(
            row["r1"], row["r2"], budget,
            max_relator_length=mrl, config=cfg_arm, progress=progress)
        res = dict(res)
        # Solves land as path_pending until the parent recovers the certificate.
        if res["solved"]:
            res["path_pending"] = True
            res["path_moves"] = []
        else:
            res["path_pending"] = False
        dt = time.perf_counter() - t
        return {"arm": arm, "name": row["name"], "row": row,
                "res": res, "secs": round(dt, 2)}
    except Exception as e:  # noqa: BLE001
        return {"arm": arm, "name": row["name"], "row": row,
                "__error__": repr(e)}


def _update_jsonl_row(path, arm, name, updates):
    """In-place replace the (arm, name) row; raise if missing."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    rows = []
    found = False
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("arm") == arm and r.get("name") == name:
                r.update(updates)
                found = True
            rows.append(r)
    if not found:
        raise KeyError(f"no row ({arm}, {name}) in {path}")
    tmp = path + ".upd_tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _recover_pending(path, cfg, budget, mrl):
    """Finalize path_pending solves with keep_path=True recovery (parent-side)."""
    if not os.path.exists(path):
        return 0
    pending = []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("solved") and r.get("path_pending"):
                pending.append(r)
    n_ok = 0
    for r in pending:
        arm = r["arm"]
        try:
            rec = greedy_search_h(
                r["r1"], r["r2"], budget,
                max_relator_length=mrl, config=run_ab.ARMS[arm],
                keep_path=True)
            if ((rec["solved"], rec["nodes_explored"], rec["path_length"])
                    != (True, r["nodes_explored"], r.get("path_length"))):
                print(f"    recovery diverge [{arm}/{r['name']}] — "
                      "leaving path_pending", flush=True)
                continue
            moves = rec.get("path_moves") or []
            # path_moves may be tuples; jsonl wants lists/strings
            if moves and not isinstance(moves[0], str):
                from experiments.search.greedy_baseline import move_to_str
                moves = [move_to_str(m) for m in moves]
            _update_jsonl_row(path, arm, r["name"], {
                "path_moves": moves,
                "path_length": rec.get("path_length"),
                "path_pending": False,
                # keep already-persisted min_relator / min_delta from first pass
            })
            n_ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"    recovery failed [{arm}/{r['name']}]: {e!r} — "
                  "leaving path_pending", flush=True)
    return n_ok


def _run_parallel_u124(cfg, out, todo, starts, n_workers, budget, mrl,
                       heartbeat_secs, progress_secs):
    """Parent-only writes with enriched keys; Drive stage+mirror like run_ab."""
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
            f"{stage} is flock-claimed by a live process — kill orphans before "
            "re-running.") from None

    ctx = mp.get_context("spawn")
    hb_q = ctx.Queue()
    engine = "hcompact"
    keep_path = False
    jobs = [(arm, run_ab.ARMS[arm], row, budget, mrl, engine, keep_path,
             heartbeat_secs)
            for arm, row in todo]
    t0 = time.perf_counter()
    done = solved = errors = 0
    last_pg = t0

    with ctx.Pool(n_workers, initializer=run_ab._init_worker_ab,
                  initargs=(hb_q,)) as pool, open(stage, "a") as f:
        pending = [pool.apply_async(_worker_u124, (j,)) for j in jobs]
        last_mirror = time.perf_counter()
        while pending:
            try:
                while True:
                    arm, name, n, b, rate = hb_q.get(
                        timeout=1.0 if not any(p.ready() for p in pending)
                        else 0.0)
                    print(f"      [{arm}/{name}] {n:,}/{b:,} nodes  "
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
                          f"{r['__error__']} — row NOT written; resume retries",
                          flush=True)
                    continue
                start = starts[r["name"]]
                rec = _row_record(
                    r["arm"], r["name"], cfg["DATASET"], budget, mrl,
                    r["res"], r["secs"], start)
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                done += 1
                solved += bool(rec["solved"])

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


def _report(out, cfg):
    data = [json.loads(l) for l in open(out) if l.strip()]
    arms = list(cfg["ARMS"])
    pts = [b for b in cfg.get("CHECKPOINTS", []) if b <= cfg["NODE_BUDGET"]]
    n = len(data)
    improved = [r for r in data if r.get("improved")]
    deltas = [int(r["min_delta"]) for r in improved
              if r.get("min_delta") is not None]
    solved = [r for r in data if r.get("solved")]
    pending = [r for r in data if r.get("path_pending")]

    lines = [
        f"# unsolved124 × s20_mk2 census — budget {cfg['NODE_BUDGET']:,}, "
        f"cap {cfg['MAX_RELATOR_LENGTH']}",
        "",
        "**Non-comparative** single-arm census (no baseline A/B). "
        f"Rows: {n}. Arm(s): {arms}. depth_tie=`+depth`. "
        "Starts = Aut-min class reps (asserted `r1/r2 == rep_*`).",
        "",
        "Cap 64 is per-relator ⇒ search is incomplete at the length ceiling. "
        "Unsolved means unsolved within 1M / cap 64 — never a counterexample.",
        "",
        "## Length-floor progress (primary)",
        "",
        f"- improved (`min_relator_length` < `start_total`): "
        f"**{len(improved)}/{n}**",
        f"- solved: **{len(solved)}/{n}**"
        + (f" ({len(pending)} path_pending)" if pending else ""),
    ]
    if deltas:
        lines += [
            f"- min_delta among improvers: median {median(deltas):.0f}, "
            f"mean {mean(deltas):.1f}, max {max(deltas)}",
            "",
            "### Top drops",
            "",
            "| name | start | min_len | min_delta | min_relator | nodes |",
            "|---|---:|---:|---:|---|---:|",
        ]
        top = sorted(improved, key=lambda r: (-int(r["min_delta"]),
                                              r.get("nodes_explored") or 0))
        for r in top[:20]:
            mr = r.get("min_relator")
            mr_s = (f"`{mr[0]}` / `{mr[1]}`" if isinstance(mr, (list, tuple))
                    and len(mr) == 2 else "—")
            lines.append(
                f"| {r['name']} | {r.get('start_total')} | "
                f"{r.get('min_relator_length')} | {r.get('min_delta')} | "
                f"{mr_s} | {r.get('nodes_explored')} |"
            )
    else:
        lines += ["", "No presentation reduced its pair-total below start."]

    if pts and data:
        lines += [
            "",
            "## Anytime solves (secondary)",
            "",
            "| arm | " + " | ".join(f"{b:,}" for b in pts) + " |",
            "|---" * (len(pts) + 1) + "|",
        ]
        for a in arms:
            arm_rows = [r for r in data if r.get("arm") == a]
            denom = len(arm_rows) or n
            counts = [
                sum(1 for r in arm_rows
                    if r.get("solved_at") is not None
                    and int(r["solved_at"]) <= b)
                for b in pts
            ]
            lines.append(
                f"| {a} | " + " | ".join(f"{c}/{denom}" for c in counts) + " |"
            )

    lines += [
        "",
        "Note: μ-ladder “36/124 descenders” uses Aut-orbit floor μ — a different "
        "ruler from greedy `min_relator_length`. Compare like with like.",
        "",
    ]
    md = out.replace(".jsonl", ".md")
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print()
    print("\n".join(lines))
    print(f"  wrote {md}")
    return md


def run_unsolved124_s20mk2(cfg, out_dir="results/hsearch", heartbeat_secs=60,
                           progress_secs=300):
    rows = load_rows(cfg.get("SUBSET"))
    chunks = cfg.get("CHUNKS") or 1
    chunk_index = cfg.get("CHUNK_INDEX")
    rows, tag = _stride_chunk(rows, chunks, chunk_index)
    starts = {r["name"]: r for r in rows}

    cfg = dict(cfg)
    cfg["DATASET"] = DATASET_NAME
    arms = list(cfg.get("ARMS") or ["s20_mk2"])
    if arms != ["s20_mk2"]:
        raise ValueError(
            f"this census is pre-registered as s20_mk2-only; got {arms}")
    for a in arms:
        if a not in run_ab.ARMS:
            raise ValueError(f"unknown arm {a!r}")
    cfg["ARMS"] = arms

    stem = cfg.get("OUT_STEM", "hsearch_u124_s20mk2")
    if tag:
        stem = f"{stem}{tag}"
    # Filename encodes result-changing identity (depth tie is fixed +depth here).
    if "dpos" not in stem:
        stem = f"{stem}_dpos"
    cfg["OUT_STEM"] = stem

    budget = int(cfg["NODE_BUDGET"])
    mrl = int(cfg["MAX_RELATOR_LENGTH"])
    engine = cfg.get("ENGINE", "hcompact")
    if engine != "hcompact":
        raise ValueError("ENGINE must be hcompact for this census")

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{stem}_{DATASET_NAME}_b{budget}_mrl{mrl}.jsonl")

    stage_probe = (
        os.path.join(
            cfg.get("STAGE_DIR") or os.path.join(os.path.expanduser("~"),
                                                 ".hsearch_stage"),
            os.path.basename(out))
        if out.startswith(run_ab._REMOTE_PREFIX) else out)

    # Finalize any leftover path_pending from a prior crash before counting done.
    for p in (out, stage_probe):
        if os.path.exists(p):
            n_rec = _recover_pending(p, cfg, budget, mrl)
            if n_rec:
                print(f"  recovered {n_rec} path_pending rows in {p}", flush=True)

    seen = ((run_ab._done(out) | run_ab._done(stage_probe))
            if cfg.get("RESUME", True) else set())
    todo = [(a, {"name": r["name"], "r1": r["r1"], "r2": r["r2"],
                 "start_total": r["start_total"]})
            for r in rows for a in arms
            if (a, r["name"]) not in seen]

    n_workers, per_gb = run_ab._resolve_workers(
        cfg, budget, mrl, engine, keep_path=False)
    print(f"  {len(arms)} arm(s) x {len(rows)} presentations, budget {budget:,}, "
          f"cap {mrl}  [engine: hcompact]  [depth_tie: +depth]"
          + (f"  [{n_workers} workers, ~{per_gb:.1f} GB/search]"
             if n_workers > 1 else ""))
    print(f"  {len(seen)} rows resumed; {len(todo)} to run")
    print(f"  -> {out}", flush=True)

    n_workers = max(int(n_workers), 1)
    stage = stage_probe
    if todo:
        stage = _run_parallel_u124(
            cfg, out, todo, starts, n_workers, budget, mrl,
            heartbeat_secs, progress_secs)
    for p in {out, stage}:
        if os.path.exists(p):
            n_rec = _recover_pending(p, cfg, budget, mrl)
            if n_rec:
                print(f"  recovered {n_rec} certificates in {p}", flush=True)
    if (out.startswith(run_ab._REMOTE_PREFIX)
            and os.path.exists(stage) and stage != out):
        run_ab._mirror(stage, out)

    report_path = out if os.path.exists(out) else stage_probe
    if os.path.exists(report_path):
        _report(report_path, cfg)
    return out
