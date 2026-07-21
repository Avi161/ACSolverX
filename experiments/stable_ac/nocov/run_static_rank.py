"""Track T2 — static rank-4/5 stabilization sweep runner.

The mentor's "dumbest possible thing": adjoin 2-3 coupled relators ``z_i^-1 w_i``
up front and search the resulting rank-4 / rank-5 balanced presentation with the
shipped general-``n`` solver (``solvern.search_n`` / ``solvern_fast``). This is
STATIC stabilization — the extra generators are present at the start and never
adjoined/destabilized mid-search — so it sidesteps the length-sum-priority
inertness (the Miasnikov null) that kills dynamic adjoin.

For each benchmark row ``<x,y | r1, r2>`` and each word-set ``{w_1..w_k}`` drawn
from a pool (``A1``/``A2`` from ``word_families``), build::

    rank 4:  <x,y,z,a   | r1, r2, Z.w1, A.w2>
    rank 5:  <x,y,z,a,b | r1, r2, Z.w1, A.w2, B.w3>

by chaining ``solvern.add_generator_with_word`` (each call adjoins the NEXT
generator per ``GEN_CHARS`` = xyzab...), search it, and append one jsonl row per
(row, word-set) job.

The harness discipline is ``run_nocov.py``'s (itself ``run_baseline.py``'s),
reused by import where it can be: date-less filename identity + glob resume,
``_repair_jsonl`` before any append, fsync every row, Drive staging with
whole-file mirroring, and the ``ACSOLVERX_ALLOW_BIG`` local-safety guard.

Per-relator cap only, via ``search_n``'s ``cap=`` argument (NOT
``change_max_relator_length_of_presentation`` — that is a JAX-env artifact and
``solvern.Pres`` relators are unpadded tuples; the structural check + spec replay
in ``verify_static_rank.py`` is what validates a solve, not a re-pad).

CPU + numba only. From the repo root::

    .venv/bin/python3 -m experiments.stable_ac.nocov.run_static_rank
"""

import glob
import itertools
import json
import os
import re
import time
from datetime import datetime

from experiments.analysis.combined_benchmark import load_combined
from experiments.run_baseline import (
    _copy_file, _is_remote, _persist, _repair_jsonl, _seed_stage,
)
from experiments.stable_ac.solvern import (
    add_generator_with_word, search_n, word_to_str,
)
from experiments.stable_ac.solvern_fast import search_n_fast
from experiments.stable_ac.word_families import build_a1, build_a2

#: Filename stem for the T2 pipeline (a code constant, never read from yaml, so a
#: yaml copy can never shadow it — lesson: identity-tag-shadowed-by-yaml).
_FILE_STEM = "staticrank"

DEFAULT_CONFIG = {
    "BENCHMARK": "combined_11",      # results/benchmark/combined/benchmark_{...}.json
    "FAMILIES": ["A1"],              # word POOL families (A1/A2); used by main()/the notebook loop
    "RANKS": [4, 5],                 # used by main()/the notebook loop only
    "MODE": "static_rank",           # row tag (the filename stem is _FILE_STEM)
    "MAX_RELATOR_LENGTH": 64,        # per-relator cap (search_n cap=; NO total-length budget)
    "CYCLIC_REDUCE": True,

    # search_n_fast: same search, fused numba bookkeeping, ~5x faster, every row
    # field bit-identical (test_solvern_fast.py pins whole-dict parity).
    # Result-neutral, so it stays OUT of the filename identity: files written in
    # either mode resume each other.
    "HIGH_SPEEDUP": False,

    # word-pool knobs (word_families.build_a1 / build_a2)
    "A1_WORDS": None,                # None -> A1_DEFAULT_WORDS (16 curated |w|<=4 words)
    "A2_MAX_WORDS": None,            # cap the A2 relator-prefix pool
    "A2_DROP_LEN1": False,

    # word-SET family: unordered pairs (rank 4) / triples (rank 5) from the pool,
    # each capped to a fixed count by deterministic even spacing. These change
    # WHICH jobs exist, not what any one job computes, so they are "limits" and
    # stay OUT of the filename identity (resume is row-keyed on (name, z_words)).
    "PAIR_LIMIT": 40,                # rank 4: cap C(pool,2) pairs to this many
    "TRIPLE_LIMIT": 20,              # rank 5: cap C(pool,3) triples to this many

    # When false (default) every w_i is a pool word in F(x,y); the structural
    # check then requires each adjoined generator to occur exactly once (in its
    # own coupled relator). When true the verifier permits w_i to reference
    # EARLIER adjoined generators (1..(2+i-1)). With the shipped A1/A2 pools —
    # which only ever produce F(x,y) words — this flag changes nothing the runner
    # builds, so it is genuinely result-neutral and stays OUT of the filename.
    "ALLOW_CHAINED_WORDS": False,

    "RESUME": True,
    "PATH_IN_SEPARATE_FILE": True,   # solved paths (moves only) -> *_paths.jsonl

    # Job selection for smoke runs — change WHICH jobs exist, not what any one
    # job computes, so OUT of the filename identity (resume stays valid).
    "ROW_LIMIT": None,               # first N benchmark rows
    "WORDSET_LIMIT": None,           # first N word-sets per row (after the pair/triple cap)
    "NAMES": None,                   # filter benchmark rows by name

    # output
    "LOCAL_OUT_DIR": "results/stable_ac/static_rank",
    "DRIVE_OUT_DIR": "/content/drive/MyDrive/acsolverx_results/stable_ac/static_rank",
    "MOUNT_DRIVE": False,

    "PROGRESS_EVERY": 25,            # print a status line every N jobs

    # W&B. None of these change the search, so none enter the filename identity.
    "USE_WANDB": False,
    "WANDB_ENTITY": "avigyapaudel045-aisc",
    "WANDB_PROJECT": "acsolver",
    "WANDB_JOB_TYPE": "stable_ac_static_rank",
    "WANDB_GROUP": None,             # None -> "{benchmark}-staticrank-r{rank}-mrl{cap}-{cyc}"
    "WANDB_RUN_NAME": None,          # None -> "A1 · r4 · 10000 · combined_11 · static_rank"
    "WANDB_TAGS": None,
    "WANDB_NOTES": None,
    "WANDB_MODE": "online",
}

# Whole-file mirror cadence when the output dir is a network mount.
# Result-neutral, so a constant rather than a config knob.
_MIRROR_EVERY_S = 60


def _require_budget_allowed(budgets):
    """Local-safety guard: a budget > 1000 needs ACSOLVERX_ALLOW_BIG=1.

    Production budgets belong on Colab (the notebook RUN cell sets the env var);
    a local invocation that forgot ROW_LIMIT would otherwise burn hours. Mirrors
    run_nocov._require_budget_allowed exactly.
    """
    big = [b for b in budgets if b > 1000]
    if big and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(
            f"refusing node budget(s) {big} > 1000: local runs stay small; "
            f"set ACSOLVERX_ALLOW_BIG=1 to confirm a production (Colab) run")


def _z_key(z_words):
    """Order-independent resume key for a word-SET: '+'-joined sorted words.

    Word-sets are unordered ({w1, w2} == {w2, w1}), so a canonical key must not
    depend on the tuple order the presentation was built in.
    """
    return "+".join(sorted(z_words))


def _run_prefix(cfg, node_budget, family, rank):
    """Date-less filename stem covering every knob that changes a job's result.

    Encoded: rank, benchmark id, pool family, budget, cap, cyclic_reduce.
    Deliberately absent: the date (never gates resume); W&B/PROGRESS/RESUME and
    HIGH_SPEEDUP (result-neutral); PAIR_LIMIT/TRIPLE_LIMIT/ROW_LIMIT/
    WORDSET_LIMIT/NAMES and ALLOW_CHAINED_WORDS (they change WHICH jobs exist or
    only how a solve is VALIDATED, not what any one job computes — resume is
    row-keyed on (name, z_words), so a partial file stays valid across them).
    """
    cyc = "cyc" if cfg["CYCLIC_REDUCE"] else "noncyc"
    return (f"{_FILE_STEM}_{cfg['BENCHMARK']}_{family}_r{rank}_{node_budget}"
            f"_mrl{cfg['MAX_RELATOR_LENGTH']}_{cyc}_")


def _resolve_paths(cfg, node_budget, family, rank):
    out_dir = cfg["DRIVE_OUT_DIR"] if cfg["MOUNT_DRIVE"] else cfg["LOCAL_OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(cfg, node_budget, family, rank)
    stem = prefix + datetime.now().strftime("%m_%d_%y")

    # Resume is date-agnostic: reattach to the existing file with the MOST rows,
    # whatever day it was started; only create a fresh dated file when none
    # exists (lesson: date-in-filename-broke-resume).
    if cfg.get("RESUME", True):
        existing = [p for p in glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
                    if not p.endswith("_paths.jsonl")]
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]

    out_path = os.path.join(out_dir, stem + ".jsonl")
    paths_path = os.path.join(out_dir, stem + "_paths.jsonl")
    return out_path, paths_path, prefix


def _read_done(out_path):
    """({(name, z_key)}, n_seen, n_solved, cum_nodes) from an existing jsonl.

    Tolerates an unparseable FINAL line (an unrepaired torn write) so resume
    never crashes on it; a bad line anywhere else is real corruption and is
    raised (matches run_baseline / run_nocov).
    """
    done, n_seen, n_solved, cum_nodes = set(), 0, 0, 0
    if not os.path.exists(out_path):
        return done, n_seen, n_solved, cum_nodes
    with open(out_path) as f:
        lines = [ln.strip() for ln in f]
    for i, ln in enumerate(lines):
        if not ln:
            continue
        try:
            row = json.loads(ln)
        except ValueError:
            if i == len(lines) - 1:
                print(f"    WARNING: ignoring a truncated final line in "
                      f"{os.path.basename(out_path)}", flush=True)
                break
            raise
        done.add((row["name"], _z_key(row["z_words"])))
        n_seen += 1
        n_solved += int(bool(row.get("solved")))
        cum_nodes += row.get("nodes_explored") or 0
    return done, n_seen, n_solved, cum_nodes


def _read_paths_done(paths_path):
    """(name, z_key) keys already in the paths file (keeps appends idempotent)."""
    keys = set()
    if os.path.exists(paths_path):
        with open(paths_path) as f:
            for ln in f:
                if ln.strip():
                    row = json.loads(ln)
                    keys.add((row["name"], _z_key(row["z_words"])))
    return keys


def _benchmark_rows(cfg):
    """Combined-benchmark rows after the NAMES filter and the ROW_LIMIT slice."""
    combined_id = int(cfg["BENCHMARK"].rsplit("_", 1)[1])
    rows = load_combined(combined_id)["rows"]
    if cfg.get("NAMES"):
        wanted = set(cfg["NAMES"])
        rows = [r for r in rows if r["name"] in wanted]
    if cfg.get("ROW_LIMIT"):
        rows = rows[:cfg["ROW_LIMIT"]]
    return rows


def _evenly_spaced(items, k):
    """k items evenly spaced over the range, endpoints included (deterministic).

    Matches word_families._evenly_spaced. Returns items unchanged when k>=len.
    """
    n = len(items)
    if k is None or k >= n:
        return list(items)
    if k <= 0:
        return []
    if k == 1:
        return [items[(n - 1) // 2]]
    idxs = []
    for i in range(k):
        j = round(i * (n - 1) / (k - 1))
        while j in idxs:                 # only reachable when n is barely above k
            j += 1
        idxs.append(j)
    return [items[j] for j in sorted(idxs)]


def _build_pool(family, relators, cfg):
    """The word POOL for one benchmark row, seeded from its relators."""
    if family == "A1":
        return build_a1(relators, cfg.get("A1_WORDS"))
    if family == "A2":
        return build_a2(relators, max_words=cfg.get("A2_MAX_WORDS"),
                        drop_len1=cfg.get("A2_DROP_LEN1", False))
    raise ValueError(
        f"unsupported word-pool family {family!r}: use A1 or A2 (A3 is a "
        f"2-relator pairwise builder, not a valid adjoined-word pool)")


def _word_sets(cfg, family, rank, relators):
    """Deterministic list of word-SETS (tuples of ``rank-2`` pool words).

    Unordered combinations of the pool, capped to PAIR_LIMIT (rank 4) or
    TRIPLE_LIMIT (rank 5) by even spacing. WORDSET_LIMIT (a smoke first-N slice)
    is applied by the caller.
    """
    k = rank - 2
    if k < 1:
        raise ValueError(f"rank {rank} adjoins {k} words; rank must be >= 3")
    pool = _build_pool(family, relators, cfg)
    combos = list(itertools.combinations(pool, k))
    limit = cfg["PAIR_LIMIT"] if k == 2 else (
        cfg["TRIPLE_LIMIT"] if k == 3 else None)
    if limit is not None:
        combos = _evenly_spaced(combos, limit)
    return combos


def build_static_rank_pres(r1, r2, z_words):
    """``<x,y | r1,r2>`` stabilized once per ``w`` in ``z_words``.

    Each step adjoins the NEXT generator (per GEN_CHARS) with defining relator
    ``G^-1 . w`` via ``add_generator_with_word``. ``z_words`` is a tuple of word
    strings; the k-th adjoins generator ``2 + k`` (z, a, b, ...).
    """
    strs = [r1, r2]
    n_gen = 2
    pres = None
    for w in z_words:
        pres = add_generator_with_word(strs, w, n_gen=n_gen)
        strs = [word_to_str(r) for r in pres.relators]
        n_gen = pres.n_gen
    return pres


def _build_jobs(cfg, family, rank):
    """One job per (benchmark row, word-set), in deterministic order."""
    jobs = []
    for brow in _benchmark_rows(cfg):
        sets = _word_sets(cfg, family, rank, [brow["r1"], brow["r2"]])
        if cfg.get("WORDSET_LIMIT"):
            sets = sets[:cfg["WORDSET_LIMIT"]]
        jobs.extend((brow, zw) for zw in sets)
    return jobs


# Baseline passthrough per source, so analysis compares without a join back into
# the benchmark file (mirrors run_nocov).
_LADDER_PASSTHROUGH = ("baseline_nodes_at_50k", "baseline_path_at_50k",
                       "baseline_solved_at_50k", "nodes_1M", "path_1M")

_GIT_COMMIT = False   # False = not yet resolved (None is a valid answer)


def _git_commit():
    """HEAD of the checkout this module runs from; None outside a git repo.

    Provenance only — which code produced a row. Deliberately NOT part of the
    filename/resume identity.
    """
    global _GIT_COMMIT
    if _GIT_COMMIT is False:
        import subprocess
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True, text=True, timeout=10,
            )
            _GIT_COMMIT = out.stdout.strip() or None
        except Exception:
            _GIT_COMMIT = None
    return _GIT_COMMIT


def _build_row(cfg, node_budget, family, rank, brow, z_words, z_relators, pres,
               stats, elapsed):
    row = {
        "name": brow["name"],
        "source": brow["source"],
        "pres_id": brow.get("pres_id"),      # null for reach rows
        "r1": brow["r1"],
        "r2": brow["r2"],
        "base_total_length": brow["base_total_length"],
        "z_words": list(z_words),
        "z_relators": list(z_relators),
        "rank": rank,
        "w_family": family,
        "allow_chained": bool(cfg["ALLOW_CHAINED_WORDS"]),
        "mode": cfg["MODE"],
        "n_gen": pres.n_gen,
        "n_rel": pres.n_rel,
        "benchmark": cfg["BENCHMARK"],
        "node_budget": node_budget,
        "max_relator_length_cap": cfg["MAX_RELATOR_LENGTH"],
        "cyclic_reduce": cfg["CYCLIC_REDUCE"],
        "nodes_explored": stats["nodes_explored"],
        "solved": stats["solved"],
        "path_length": stats["path_length"],
        "min_relator_length": stats["min_relator_length"],
        "min_relator": stats["min_relator"],
        "max_relator_length": stats["max_relator_length"],
        "max_relator": stats["max_relator"],
        "max_relator_length_expanded": stats["max_relator_length_expanded"],
        "max_relator_expanded": stats["max_relator_expanded"],
        "time_seconds": round(elapsed, 4),
        "git_commit": _git_commit(),
    }
    if "tier" in brow:                       # a future benchmark may carry one
        row["tier"] = brow["tier"]
    if brow["source"] == "ladder":
        for k in _LADDER_PASSTHROUGH:
            row[k] = brow.get(k)
    else:
        row["bar_to_beat"] = brow.get("bar_to_beat")
        row["start_length"] = brow.get("baseline_start_length")
        row["aut_min_rep_r1"] = brow.get("aut_min_rep_r1")
        row["aut_min_rep_r2"] = brow.get("aut_min_rep_r2")
    return row


def _wandb_start(cfg, node_budget, family, rank, prefix):
    """Minimal inline W&B (same shape as run_nocov's): the run id derives from
    the date-less filename prefix so a Colab disconnect reattaches to the same
    run; run/* keys ride a monotone ``n_processed`` step and nothing passes
    ``step=`` (lesson: wandb-step-must-be-monotonic)."""
    import wandb

    run_id = re.sub(r"[^A-Za-z0-9_-]", "-", prefix.rstrip("_"))
    cap, cyc = cfg["MAX_RELATOR_LENGTH"], cfg["CYCLIC_REDUCE"]
    group = cfg["WANDB_GROUP"] or (
        f"{cfg['BENCHMARK']}-staticrank-r{rank}-mrl{cap}"
        f"-{'cyc' if cyc else 'noncyc'}")
    name = cfg["WANDB_RUN_NAME"] or (
        f"{family} · r{rank} · {node_budget} · {cfg['BENCHMARK']} · static_rank")
    config = {
        "mode": cfg["MODE"], "benchmark": cfg["BENCHMARK"], "family": family,
        "rank": rank, "node_budget": node_budget, "max_relator_length_cap": cap,
        "cyclic_reduce": cyc, "pair_limit": cfg["PAIR_LIMIT"],
        "triple_limit": cfg["TRIPLE_LIMIT"],
        "allow_chained": cfg["ALLOW_CHAINED_WORDS"],
    }
    run = wandb.init(
        entity=cfg["WANDB_ENTITY"], project=cfg["WANDB_PROJECT"], id=run_id,
        name=name, group=group, job_type=cfg["WANDB_JOB_TYPE"],
        tags=cfg["WANDB_TAGS"], notes=cfg["WANDB_NOTES"],
        mode=cfg["WANDB_MODE"], resume="allow", config=config)
    run.define_metric("n_processed")
    run.define_metric("run/*", step_metric="n_processed")
    return run, run_id


def _wandb_finish(run, run_id, out_path, paths_path, total_time):
    import wandb

    with open(out_path) as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    n_solved = sum(bool(r["solved"]) for r in rows)
    run.summary.update({
        "n_rows": len(rows),
        "n_solved": n_solved,
        "solve_rate": n_solved / max(len(rows), 1),
        "newly_solved_reach": sum(
            1 for r in rows if r["source"] == "reach" and r["solved"]),
        "cum_nodes": sum(r.get("nodes_explored") or 0 for r in rows),
        "total_time": total_time,
    })
    cols = ["name", "source", "rank", "z_words", "w_family", "solved",
            "nodes_explored", "path_length", "min_relator_length"]
    run.log({"tables/results": wandb.Table(
        columns=cols, data=[[r.get(c) for c in cols] for r in rows])})
    art = wandb.Artifact(run_id, type="stable_ac_static_rank_results")
    art.add_file(out_path)
    if os.path.exists(paths_path):
        art.add_file(paths_path)
    run.log_artifact(art)
    run.finish()


def run_static_rank(cfg, node_budget, family, rank):
    """Run one (budget, family, rank) sweep over the combined benchmark.

    One jsonl per (budget, family, rank); crash-safe (fsync every row);
    resumable via the (name, z_words) keys already in the file. Returns the
    output jsonl path (the mirror path when the output lives on Drive).
    """
    cfg = {**DEFAULT_CONFIG, **cfg}
    _require_budget_allowed([node_budget])

    jobs = _build_jobs(cfg, family, rank)
    out_path, paths_path, prefix = _resolve_paths(cfg, node_budget, family, rank)

    # Drive staging (run_nocov's pattern): local disk is authoritative; the mount
    # only ever receives a whole-file copy. A resumed run lands on a FRESH VM
    # whose staging file is gone, so seed it from the mirror before reading done.
    mirror = []
    if _is_remote(out_path):
        stage_dir = os.path.join(cfg["LOCAL_OUT_DIR"], "_stage")
        os.makedirs(stage_dir, exist_ok=True)
        stage_out = os.path.join(stage_dir, os.path.basename(out_path))
        stage_paths = os.path.join(stage_dir, os.path.basename(paths_path))
        _seed_stage(stage_out, out_path)
        _seed_stage(stage_paths, paths_path)
        mirror = [(stage_out, out_path), (stage_paths, paths_path)]
        print(f"    durable output: appending to {stage_dir} (local disk), "
              f"mirroring to {os.path.dirname(out_path)} every "
              f"{_MIRROR_EVERY_S}s", flush=True)
        out_path, paths_path = stage_out, stage_paths

    last_mirror = [time.time()]

    def _mirror_all(force=False):
        """Copy the staging files onto the mount. No-op when output is local."""
        if not mirror:
            return
        now = time.time()
        if not force and now - last_mirror[0] < _MIRROR_EVERY_S:
            return
        last_mirror[0] = now
        for local, remote in mirror:
            if os.path.exists(local):
                _copy_file(local, remote)

    # Before ANY reader or the append handles below touch these files. Not gated
    # on RESUME: a non-resumed run still opens them "a" and would concatenate its
    # first row onto a leftover stub.
    _repair_jsonl(out_path)
    _repair_jsonl(paths_path)

    if cfg["RESUME"]:
        done, n_seen, n_solved, cum_nodes = _read_done(out_path)
        paths_done = _read_paths_done(paths_path)
    else:
        done, n_seen, n_solved, cum_nodes = set(), 0, 0, 0
        paths_done = set()

    todo = [(brow, zw) for brow, zw in jobs
            if (brow["name"], _z_key(zw)) not in done]
    n_todo = len(todo)
    print(f"=== static_rank | {family} r{rank} | budget={node_budget} | "
          f"{len(jobs)} jobs | {len(done)} already done, {n_todo} to run | "
          f"-> {out_path}", flush=True)
    if n_todo == 0:
        print("    nothing to do (all done).", flush=True)

    run, run_id = None, None
    if cfg["USE_WANDB"]:
        run, run_id = _wandb_start(cfg, node_budget, family, rank, prefix)
    n_processed = n_seen         # monotone W&B step, seeded from prior rows

    every = max(1, int(cfg["PROGRESS_EVERY"]))
    total_time = 0.0
    t_start = time.time()
    processed = 0
    out_f = open(out_path, "a")
    paths_f = open(paths_path, "a") if cfg["PATH_IN_SEPARATE_FILE"] else None
    try:
        searcher = search_n_fast if cfg["HIGH_SPEEDUP"] else search_n
        for brow, zw in todo:
            pres = build_static_rank_pres(brow["r1"], brow["r2"], zw)
            # The adjoined coupled relators, as searched ("Z"+w1, "A"+w2, ...).
            z_relators = [word_to_str(r) for r in pres.relators[2:]]
            t0 = time.time()
            stats = searcher(pres, node_budget,
                             cap=cfg["MAX_RELATOR_LENGTH"],
                             cyclic=cfg["CYCLIC_REDUCE"])
            elapsed = time.time() - t0
            total_time += elapsed

            row = _build_row(cfg, node_budget, family, rank, brow, zw,
                             z_relators, pres, stats, elapsed)
            out_f.write(json.dumps(row) + "\n")
            _persist(out_f)

            key = (brow["name"], _z_key(zw))
            if paths_f is not None and stats["solved"] and key not in paths_done:
                # Moves only — replay (verify_static_rank / spec) is the decoder.
                paths_f.write(json.dumps({
                    "name": brow["name"], "z_words": list(zw),
                    "r1": brow["r1"], "r2": brow["r2"],
                    "z_relators": z_relators,
                    "path_moves": stats["path_moves"]}) + "\n")
                _persist(paths_f)
                paths_done.add(key)
            _mirror_all()

            processed += 1
            n_seen += 1
            n_solved += int(bool(stats["solved"]))
            cum_nodes += stats["nodes_explored"]
            n_processed += 1
            nps = stats["nodes_explored"] / elapsed if elapsed > 0 else 0.0
            if run is not None:
                run.log({"n_processed": n_processed,
                         "run/solve_rate": n_solved / max(n_seen, 1),
                         "run/n_solved": n_solved,
                         "run/cum_nodes": cum_nodes,
                         "run/nodes_per_s": nps})
            if processed % every == 0 or processed == n_todo:
                wall = time.time() - t_start
                print(f"    [{family} r{rank}@{node_budget}] {processed}/{n_todo}"
                      f" | {brow['name']} · z={list(zw)} | solved "
                      f"{n_solved}/{n_seen} | {nps:,.0f} nodes/s | {wall:.0f}s "
                      f"elapsed", flush=True)
    finally:
        out_f.close()
        if paths_f is not None:
            paths_f.close()
        # A Ctrl-C must still push this session's rows onto the mount: the
        # staging disk dies with the VM.
        _mirror_all(force=True)

    if run is not None:
        _wandb_finish(run, run_id, out_path, paths_path, total_time)

    final_path = mirror[0][1] if mirror else out_path
    print(f"[{final_path}] {n_seen} jobs, {n_solved} solved "
          f"({n_solved / max(n_seen, 1):.1%}).", flush=True)
    return final_path


def main():
    """Read config_static_rank.yaml (next to this file) and run every
    (budget, family, rank)."""
    import yaml

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "config_static_rank.yaml")) as f:
        cfg = yaml.safe_load(f)
    _require_budget_allowed(cfg["BUDGET"])   # fail fast, before any file I/O
    for budget in cfg["BUDGET"]:
        for family in cfg["FAMILIES"]:
            for rank in cfg["RANKS"]:
                run_static_rank(cfg, budget, family, rank)


if __name__ == "__main__":
    main()
