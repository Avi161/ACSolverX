"""Stage B of the ms640 CoV-top-3 experiment: search the frozen top-3 starts.

For each of the 640 ms640 presentations, run the greedy from its manifest picks
in rank order — rank 1, then rank 2, then rank 3 — **stopping at the first
solve**. Each search gets its own ``budget`` nodes, so a presentation costs at
most ``k * budget`` (3 x 100,000 = 300,000) and usually far less: on subset-60 at
budget 1,000 the median cumulative cost to first solve was 18 nodes. Early exit
is the rule, not an optimisation — "the top 3 until one solves" is the thing
being measured, so its cost is the cost of the ranks it actually ran.

The selection is Stage A's problem and is already frozen on disk
(``cov_top3_manifest``), so this module makes no ranking decisions at all. It
does assert the manifest's ``rule`` against its own, because with two manifests
on disk a stale path is a wrong experiment that nothing downstream could notice.

## The two arms

One rule per session, both over all 640 presentations, both writing every field
of every search they run:

- ``rule="abel"`` — top 3 by abelianized magnitude → ``abeltop3_*.jsonl``
- ``rule="len"``  — top 3 by shortest transformed pair → ``lentop3_*.jsonl``

The rule is in the filename, so the arms can never resume into each other.

## Row identity and resume

One jsonl row per *search*, keyed ``(pres_id, rank)``. A presentation is finished
when some row for it solved, or when all ``k`` ranks have a row — so a resumed
run re-derives the early exit from the file rather than storing a summary that
could disagree with it. ``_repair_jsonl`` runs before the first append (a torn
trailing line must be repaired, not merely tolerated at read time) and the output
is ``flock``-claimed against a superseded session's surviving workers.

Every row carries the full search result (``solved``, ``nodes_explored``,
``path_length``, the move ``path``, the relator extremes), the pick that produced
it (``rule``, ``rank``, ``z_word``, ``iso_gen``, ``iso_index``, ``abel``, the
caps and start lengths), the presentation's running ``cum_nodes``, **and** the
plain-greedy reference for the same presentation (``base_solved``,
``base_nodes_explored``, ``base_path_length``, read once from the frozen
1,000,000-node baseline). The comparison the run exists to make is therefore
answerable from this one file, with no join.

## Sharding

``chunk_index = i`` of ``chunks = N`` runs presentation ``j`` iff
``j % N == i - 1`` — a stride, never a block, because ms640 is difficulty-ordered
and a block split would hand one shard every hard presentation. Both shipped
notebooks run unsharded (``chunks = 1``); the split is kept for a session that
needs to divide one arm further, and ``merge_chunks`` folds the pieces back once
every one of them is complete.

## What the comparison is

Plain greedy on the untransformed presentation, which already exists on disk:
``results/greedy_baseline/greedy_1000000_640_*.jsonl``. Its truncation at any
budget is free — a search at budget B is exactly the first B pops of a longer one
— so the node-matched control (``k * budget``) and the single-search control
(``budget``) are both file reads. Do not re-run it. ``summarize`` prints the
solve counts *and* the paired nodes/path-length comparison over the
presentations where both arms solved.

    ACSOLVERX_ALLOW_BIG=1 .venv/bin/python3 -m \
        experiments.stable_ac.cov.run.cov_top3_run --rule len
"""

import argparse
import glob
import json
import os
import re
import time
from datetime import datetime

from experiments import run_baseline
from experiments.stable_ac.cov.run import cov_top3_manifest as manifest
from experiments.stable_ac.cov.run.run_cov import (
    _base_cfg, _claim_out_path, _git_commit, find_repo_root)

DEFAULTS = {
    "rule": manifest.DEFAULT_RULE,   # "abel" | "len" — one arm per session
    "budget": 100_000,               # per search; a presentation costs <= k * this
    "k": manifest.K,                 # ranks per presentation (manifest is built at 3)
    "manifest": None,                # None = derived from the rule (the safe default)
    "out_dir": manifest.OUT_DIR,
    "dataset_tag": "ms640",
    "cyclic_reduce": True,
    # Identity only. Every SEARCH runs at its manifest row's own ``cap``
    # (max(24, longest + 16)) — a CoV lengthens relators, and searching a
    # lengthened start under the untransformed 24-cap would cripple it.
    "max_relator_length": manifest.DEFAULT_CAP,
    # run_baseline.greedy_search(high_speedup=True): compact solver, same pop
    # order, same stats, no path; a SOLVED fast search is re-solved by the normal
    # solver to recover the path. Result-neutral -> never in the filename.
    "high_speedup": True,
    "resume": True,
    "chunks": 1,
    "chunk_index": None,             # 1..chunks; None = every presentation
}

_CHUNK_MARK = re.compile(r"_c\d+of\d+_")
_BIG_BUDGET = 1_000
_ALLOW_BIG_ENV = "ACSOLVERX_ALLOW_BIG"

ROOT = find_repo_root(os.path.dirname(os.path.abspath(__file__)))


def load_config(**overrides):
    c = dict(DEFAULTS)
    c.update({k: v for k, v in overrides.items() if v is not None})
    manifest.check_rule(c["rule"])
    if c["manifest"] is None:
        c["manifest"] = manifest.manifest_path(c["rule"], c["out_dir"])
    n = c["chunks"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError(f"chunks must be an int >= 1, got {n!r}")
    ci = c["chunk_index"]
    if ci is not None and not (isinstance(ci, int) and not isinstance(ci, bool)
                               and 1 <= ci <= n):
        raise ValueError(f"chunk_index must be 1..{n} or None, got {ci!r}")
    if c["budget"] > _BIG_BUDGET and os.environ.get(_ALLOW_BIG_ENV) != "1":
        raise RuntimeError(
            f"budget {c['budget']:,} exceeds the local cap of {_BIG_BUDGET:,}. "
            f"Production budgets run on Colab: set {_ALLOW_BIG_ENV}=1 there. "
            f"A search at budget B is the first B pops of any longer search, so "
            f"a bigger budget locally buys a slower repro, never new behaviour.")
    return c


# ------------------------------------------------------------------- identity

def _run_prefix(c, n_pres):
    """Date-less stem of every knob that changes the result (resume identity).

    In: the RULE (two rules are two experiments and must never share a file),
    budget, k, the manifest's family tag, base cap, cyclic reduction, the
    dataset, and the chunk (a different row subset is a different experiment).
    Out: ``high_speedup`` and ``resume``, which are result-neutral — files must
    resume across those.
    """
    cyc = "cyc" if c["cyclic_reduce"] else "noncyc"
    chunk = (f"c{c['chunk_index']}of{c['chunks']}_"
             if c["chunk_index"] is not None else "")
    return (f"{c['rule']}top{c['k']}_{c['budget']}_{n_pres}_{manifest.FAMILY_TAG}"
            f"_mrl{c['max_relator_length']}_{cyc}_{c['dataset_tag']}_{chunk}")


def _resolve_out_path(c, n_pres, root=ROOT):
    out_dir = c["out_dir"]
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(root, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(c, n_pres)
    stem = prefix + datetime.now().strftime("%m_%d_%y")
    if c["resume"]:
        existing = glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
        if not _CHUNK_MARK.search(prefix):
            # the unchunked prefix is a proper prefix of every chunk filename,
            # so an unchunked resume would otherwise silently adopt a chunk file
            existing = [p for p in existing
                        if not _CHUNK_MARK.search(os.path.basename(p))]
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]
    return os.path.join(out_dir, stem + ".jsonl")


def _read_done(out_path):
    """{(pres_id, rank): row} from a results jsonl, plus (n_seen, n_solved).

    The whole row, not a flag: resume must re-derive the early exit AND the
    running cumulative node count from the file, because a summary written
    beside them could disagree with them after a crash. Same torn-final-line
    tolerance as ``run_baseline._read_done`` — unparseable anywhere else is real
    corruption and must raise.
    """
    done, n_solved = {}, 0
    if not os.path.exists(out_path):
        return done, 0, 0
    with open(out_path) as f:
        lines = [ln.strip() for ln in f]
    for i, ln in enumerate(lines):
        if not ln:
            continue
        try:
            row = json.loads(ln)
        except ValueError:
            if i == len(lines) - 1:
                continue
            raise
        done[(row["pres_id"], row["rank"])] = row
        n_solved += int(bool(row.get("solved")))
    return done, len(done), n_solved


def shard(pres_list, chunks, chunk_index):
    """Presentation ``j`` belongs to chunk ``(j % chunks) + 1`` (run_cov's rule).

    Sharded on the PRESENTATION, never on the manifest row: ranks 1-3 of one
    presentation are a sequential early-exit chain, so splitting them across
    sessions would make each session search ranks the other had already made
    unnecessary.
    """
    if chunk_index is None:
        return list(pres_list)
    return [p for j, p in enumerate(pres_list) if j % chunks == chunk_index - 1]


# ------------------------------------------------------------------ heartbeat

class _Top3Heartbeat:
    """The standard notebook pulse, TIME-based on both phases.

    ``beat`` (60 s) rides the solver's own ``progress`` callback, so it fires
    *inside* a long search: a slow CPU shows up as a falling instantaneous
    nodes/s, never as silence. ``summary`` (5 min) is the cumulative
    done/solved/ETA line. Progress is counted in PRESENTATIONS, not searches —
    early exit makes a presentation 1, 2 or 3 searches, so a search-denominated
    ETA would be wrong by up to 3x. Everything prints from the main thread (the
    callback runs inside ``solve``); a background thread must never print, and a
    pool worker's print is dropped outright in Colab.
    """

    BEAT = 60.0
    SUMMARY = 300.0

    def __init__(self, total_pres, done_pres, label="", now=None):
        self.total = total_pres
        self.done0 = self.done = done_pres    # resumed: outside rate and ETA
        self.solved = self.nodes = self.searches = 0
        self.label = f" {label}" if label else ""
        t = time.monotonic() if now is None else now
        self.t0 = self.t_beat = self.t_sum = t
        self.n_beat = 0                       # nodes at the last beat
        self._live = 0                        # nodes of the search in flight

    # -- the solver's callback -------------------------------------------------
    def progress(self, nodes_in_search):
        self._live = nodes_in_search
        self.maybe_beat()

    def _seen(self):
        return self.nodes + self._live

    def maybe_beat(self, now=None):
        now = time.monotonic() if now is None else now
        if now - self.t_beat >= self.BEAT:
            seen = self._seen()
            rate = (seen - self.n_beat) / (now - self.t_beat)
            self.t_beat, self.n_beat = now, seen
            print(f"  [hb{self.label}] search {self.searches + 1} in flight | "
                  f"{self._live:,} nodes this search | {rate:,.0f} nodes/s",
                  flush=True)
        if now - self.t_sum >= self.SUMMARY:
            self.t_sum = now
            print(self.summary(now), flush=True)

    # -- accounting ------------------------------------------------------------
    def note_search(self, stats):
        self.searches += 1
        self.nodes += int(stats["nodes_explored"])
        self._live = 0

    def note_pres(self, solved):
        self.done += 1
        self.solved += int(bool(solved))

    def summary(self, now=None):
        now = time.monotonic() if now is None else now
        elapsed = now - self.t0
        ran = self.done - self.done0
        if ran:
            left = (self.total - self.done) * (elapsed / ran)
            eta = (f"~{left / 3600:.1f}h left" if left >= 3600
                   else f"~{max(left / 60, 1):.0f}m left")
        else:
            eta = "eta n/a"
        rate = self._seen() / elapsed if elapsed > 0 else 0.0
        return (f"  [sum{self.label}] {self.done}/{self.total} presentations | "
                f"{self.solved} solved this session | {self.searches} searches | "
                f"{self._seen():,} nodes @ {rate:,.0f} nodes/s mean | {eta}")


# ------------------------------------------------------- the plain-greedy ref

BASELINE_GLOB = "results/greedy_baseline/greedy_1000000_640_mrl24_cyc_all_*.jsonl"


def baseline_rows(root=ROOT, pattern=BASELINE_GLOB):
    """{pres_id: {solved, nodes_explored, path_length}} for plain greedy.

    The frozen 1,000,000-node ms640 run — the untransformed route's own cost and
    own certificate length, which is what every comparison here is against.
    Returns ``{}`` if the file is absent rather than raising: a missing reference
    must degrade the summary, never kill a finished search run.
    """
    paths = sorted(glob.glob(os.path.join(root, pattern)))
    if not paths:
        return {}
    out = {}
    with open(paths[-1]) as fh:
        for line in fh:
            d = json.loads(line)
            out[d["pres_id"]] = {"solved": bool(d["solved"]),
                                 "nodes_explored": d["nodes_explored"],
                                 "path_length": d["path_length"],
                                 "node_budget": d["node_budget"]}
    return out


def baseline_at(budget, root=ROOT, pattern=BASELINE_GLOB):
    """{pres_id: solved} for plain greedy at ``budget``, by TRUNCATION.

    Zero new search. A greedy search at budget B is exactly the first B pops of
    any longer search, so the node-matched control at k x budget is the frozen
    1,000,000-node run read with ``solved and nodes_explored <= budget``.
    Re-running it would burn days to reproduce a file that already exists.
    """
    rows = baseline_rows(root, pattern)
    if not rows:
        raise FileNotFoundError(f"no plain-greedy baseline matching {pattern}")
    return {p: d["solved"] and d["nodes_explored"] <= budget
            for p, d in rows.items()}


# --------------------------------------------------------------------- search

def _search(c, r1, r2, cap, progress=None):
    """One start's search through the ``run_baseline.greedy_search`` seam.

    ``run_cov._search`` with a ``progress`` callback added — the in-search
    heartbeat needs it, and at budget 100,000 a between-search beat would leave
    the notebook silent for a whole search. The two-phase high_speedup pattern is
    ``run_cov``'s verbatim: the compact solver returns no path, so a SOLVED fast
    search is re-solved by the normal solver (deterministic — the identical
    search, stopping at the identical node), which is what makes every written
    row identical to a slow-mode row, paths included. The re-solve gets no
    callback: its nodes are the same nodes, and counting them twice would
    inflate the rate.
    """
    hs = bool(c["high_speedup"])
    stats = run_baseline.greedy_search(
        r1, r2, c["budget"], max_relator_length=cap,
        cyclic_reduce=c["cyclic_reduce"], high_speedup=hs, progress=progress)
    if hs and stats["solved"]:
        stats = run_baseline.greedy_search(
            r1, r2, c["budget"], max_relator_length=cap,
            cyclic_reduce=c["cyclic_reduce"], high_speedup=False)
    return stats


def run(root=ROOT, **overrides):
    """Search this arm's presentations, appending one row per search."""
    c = load_config(**overrides)
    groups = manifest.load_manifest(c["manifest"], root=root, rule=c["rule"])
    n_pres = len(groups)
    mine = shard(groups, c["chunks"], c["chunk_index"])
    base = baseline_rows(root)

    out_path = _resolve_out_path(c, n_pres, root)
    _claim_out_path(out_path)
    run_baseline._repair_jsonl(out_path)
    done, n_seen, n_solved = _read_done(out_path)
    label = (f"c{c['chunk_index']}of{c['chunks']}"
             if c["chunk_index"] is not None else c["rule"])
    done_pres = sum(1 for _, picks in mine if _finished(done, picks, c["k"]))
    print(f"[{c['rule']}-top{c['k']}] budget={c['budget']:,} "
          f"{len(mine)}/{n_pres} presentations -> "
          f"{os.path.basename(out_path)} (resume: {done_pres} presentations, "
          f"{n_seen} searches, {n_solved} solved)", flush=True)
    if not base:
        print("  ! plain-greedy reference not found: rows will carry no "
              "base_* fields and summarize() will skip the comparison",
              flush=True)

    bcfg = _base_cfg(c)
    hb = _Top3Heartbeat(len(mine), done_pres, label=label)
    with open(out_path, "a") as out_f:
        for pres_id, picks in mine:
            if _finished(done, picks, c["k"]):
                continue
            cum = ranks = 0
            solved_here = False
            ref = base.get(pres_id, {})
            for pick in picks[:c["k"]]:
                ranks += 1
                prev = done.get((pres_id, pick["rank"]))
                if prev is not None:
                    cum += int(prev["nodes_explored"])
                    if prev["solved"]:
                        solved_here = True
                        break
                    continue
                t0 = time.perf_counter()
                stats = _search(c, pick["r1"], pick["r2"], pick["cap"],
                                progress=hb.progress)
                elapsed = time.perf_counter() - t0
                cum += int(stats["nodes_explored"])

                row = run_baseline._build_row(bcfg, pres_id, pick["r1"],
                                              pick["r2"], c["budget"], stats,
                                              elapsed)
                row.update({
                    "mode": f"{c['rule']}_top{c['k']}", "rule": c["rule"],
                    "rank": pick["rank"], "k": c["k"],
                    "n_cand": pick["n_cand"], "abel": pick["abel"],
                    "z_word": pick["z_word"], "iso_gen": pick["iso_gen"],
                    "iso_index": pick["iso_index"], "n_subs": pick["n_subs"],
                    "max_relator_length_cap": pick["cap"],
                    "r1_orig": pick["r1_orig"], "r2_orig": pick["r2_orig"],
                    "start_total_length_orig": (len(pick["r1_orig"])
                                                + len(pick["r2_orig"])),
                    "start_total_length_cov": pick["start_total_length_cov"],
                    "cum_nodes": cum, "family_tag": pick["family_tag"],
                    "source": pick["dataset"], "git_commit": _git_commit(),
                    # the untransformed route on the SAME presentation, from the
                    # frozen 1M baseline — carried so this file answers the
                    # nodes/path comparison with no join
                    "base_solved": ref.get("solved"),
                    "base_nodes_explored": ref.get("nodes_explored"),
                    "base_path_length": ref.get("path_length"),
                    "base_node_budget": ref.get("node_budget"),
                })
                out_f.write(json.dumps(row) + "\n")
                out_f.flush()
                os.fsync(out_f.fileno())
                done[(pres_id, pick["rank"])] = row

                n_seen += 1
                n_solved += int(bool(stats["solved"]))
                hb.note_search(stats)
                if stats["solved"]:
                    solved_here = True
                    break
            hb.note_pres(solved_here)
            print(f"  {pres_id}: solved={solved_here} cum_nodes={cum:,} "
                  f"ranks={ranks}/{min(c['k'], len(picks))}", flush=True)
    print(hb.summary(), flush=True)
    print(f"[{c['rule']}-top{c['k']}] done: {n_solved} solving searches over "
          f"{n_seen} searches", flush=True)
    return out_path


def _finished(done, picks, k):
    """A presentation is done when some rank solved, or all k ranks have a row.

    Re-derived from the rows themselves on every resume — never cached, because
    a cached verdict that survives a crash the rows did not is exactly how a
    resumed run reports work it never did.
    """
    rows = [done.get((p["pres_id"], p["rank"])) for p in picks[:k]]
    if any(r is not None and r["solved"] for r in rows):
        return True
    return bool(rows) and all(r is not None for r in rows)


# ---------------------------------------------------------------------- merge

def merge_chunks(root=ROOT, force=False, **overrides):
    """Fold the COMPLETE chunk files into the canonical unchunked filename.

    Only rows are merged, deduplicated on ``(pres_id, rank)`` — the unchunked
    file is then a normal resumable run of the same experiment, which is what
    ``_run_prefix`` keeping ``n_pres`` at the FULL dataset size buys.

    It refuses to merge while a chunk file is absent or any presentation is
    unfinished, because the file it writes becomes the canonical one: merging
    early would leave a short file under the name every later unchunked run
    resumes from, and that run would report the missing presentations as done.
    ``force=True`` overrides for a deliberate partial snapshot.
    """
    c = load_config(**overrides)
    groups = manifest.load_manifest(c["manifest"], root=root, rule=c["rule"])
    n_pres = len(groups)
    rows, sources, absent = {}, [], []
    for i in range(1, c["chunks"] + 1):
        path = _resolve_out_path(dict(c, chunk_index=i), n_pres, root)
        if not os.path.exists(path):
            absent.append(os.path.basename(path))
            print(f"  chunk {i}/{c['chunks']}: MISSING ({os.path.basename(path)})",
                  flush=True)
            continue
        run_baseline._repair_jsonl(path)
        d, n_seen, _ = _read_done(path)
        rows.update(d)
        sources.append(os.path.basename(path))
        print(f"  chunk {i}/{c['chunks']}: {n_seen} searches", flush=True)
    unfinished = [p for p, picks in groups if not _finished(rows, picks, c["k"])]
    if not force and (absent or unfinished):
        raise RuntimeError(
            f"refusing to merge: {len(absent)} chunk file(s) absent "
            f"{absent[:3]}, {len(unfinished)} presentation(s) unfinished "
            f"{unfinished[:5]}. Let every shard finish (or pass force=True for "
            f"a deliberate partial snapshot — it will claim the canonical "
            f"filename that later unchunked runs resume from).")
    out_path = _resolve_out_path(dict(c, chunk_index=None), n_pres, root)
    _claim_out_path(out_path)
    with open(out_path, "w") as fh:
        for key in sorted(rows, key=lambda k: (k[0], k[1])):
            fh.write(json.dumps(rows[key]) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    print(f"merged {len(sources)} chunks ({len(rows)} searches, "
          f"{n_pres - len(unfinished)}/{n_pres} presentations) -> "
          f"{os.path.basename(out_path)}", flush=True)
    return out_path


# ------------------------------------------------------------------ overlap

OVERLAP_SWEEP = ("results/stable_ac/cov/"
                 "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")


def verify_overlap(out_path, root=ROOT, budget=None, sweep=OVERLAP_SWEEP):
    """Gate this run against the frozen 10,000-node sweep. Zero new search.

    60 of the 640 presentations are subset-60, and that sweep already searched
    their whole CoV families — so both arms' picks on those rows have a known
    answer before the run starts. Greedy search is deterministic and a search at
    budget B is the first B pops of a longer one, so on every overlapping row:
    a start that solved at 10,000 must solve here with the SAME
    ``nodes_explored`` and ``path_length``, and a start that solves here in
    <= 10,000 nodes must have solved there. This is the budget-agnostic proof
    the repo asks for in place of brute-forcing one budget, and it costs a file
    read. Returns (n_overlap, violations).
    """
    path = sweep if os.path.isabs(sweep) else os.path.join(root, sweep)
    if not os.path.exists(path):
        return 0, [f"frozen sweep not found: {sweep}"]
    ref = {}
    with open(path) as fh:
        for line in fh:
            d = json.loads(line)
            if d.get("n_cov", 0):
                ref[(d["pres_id"], d["z_word"], d["iso_gen"],
                     d["iso_index"])] = d
    done, _, _ = _read_done(out_path)
    n, bad = 0, []
    for row in done.values():
        key = (row["pres_id"], row["z_word"], row["iso_gen"], row["iso_index"])
        r = ref.get(key)
        if r is None:
            continue
        n += 1
        b_ref = r["node_budget"]
        b_run = budget or row["node_budget"]
        if row["max_relator_length_cap"] != r["max_relator_length_cap"]:
            bad.append(f"{key}: cap {row['max_relator_length_cap']} != "
                       f"{r['max_relator_length_cap']} — a different search")
        if r["solved"] and r["nodes_explored"] <= b_run:
            if not row["solved"]:
                bad.append(f"{key}: solved at {b_ref} in "
                           f"{r['nodes_explored']} nodes but UNSOLVED here")
            elif (row["nodes_explored"] != r["nodes_explored"]
                  or row["path_length"] != r["path_length"]):
                bad.append(f"{key}: {row['nodes_explored']}/{row['path_length']}"
                           f" != frozen {r['nodes_explored']}/{r['path_length']}")
        elif row["solved"] and row["nodes_explored"] <= b_ref and not r["solved"]:
            bad.append(f"{key}: solved here in {row['nodes_explored']} nodes, "
                       f"unsolved in the frozen {b_ref} sweep")
    return n, bad


# ------------------------------------------------------------------ summarize

def _stats(vals):
    s = sorted(vals)
    n = len(s)
    return {"n": n, "median": s[n // 2], "mean": sum(s) / n, "max": max(s),
            "total": sum(s)}


def per_presentation(out_path, k, root=ROOT):
    """{pres_id: {solved, rank, cum_nodes, path_length, base_*}} — the arm's row.

    One record per presentation the file searched: what the rule actually
    delivered (did it solve, at which rank, for how many nodes in total, with
    what path length) beside the untransformed route's own numbers. This is the
    unit every comparison below is computed on.
    """
    done, _, _ = _read_done(out_path)
    base = baseline_rows(root)
    by_pres = {}
    for (pres_id, rank), row in done.items():
        by_pres.setdefault(pres_id, []).append(row)
    out = {}
    for pres_id, rows in by_pres.items():
        rows.sort(key=lambda r: r["rank"])
        rows = rows[:k]
        hit = next((r for r in rows if r["solved"]), None)
        ref = base.get(pres_id, {})
        out[pres_id] = {
            "solved": hit is not None,
            "rank": hit["rank"] if hit else None,
            "n_searches": len(rows),
            "cum_nodes": sum(r["nodes_explored"] for r in rows),
            "path_length": hit["path_length"] if hit else None,
            "base_solved": ref.get("solved"),
            "base_nodes_explored": ref.get("nodes_explored"),
            "base_path_length": ref.get("path_length"),
        }
    return out


def summarize(out_path, root=ROOT, **overrides):
    """Solve counts and the paired nodes/path comparison against plain greedy.

    Every count is over the set this file actually searched, never over all 640 —
    a partial run scored against a complete control reads as a catastrophic loss
    that is really just unfinished work, and one run's arm must never be scored
    against another run's denominator. The paired statistics go further and use
    only the presentations where BOTH arms solved: a mean over rows one arm never
    finished is a mean over two different questions.
    """
    c = load_config(**overrides)
    groups = manifest.load_manifest(c["manifest"], root=root, rule=c["rule"])
    per = per_presentation(out_path, c["k"], root)
    matched = c["k"] * c["budget"]

    searched = set(per)
    hit = {p for p, d in per.items() if d["solved"]}
    missing = [p for p, _ in groups if p not in searched]
    # started but not finished: ranks left to try. Counted separately because
    # such a row is an unsolved row in every statistic below while the arm has
    # not actually given up on it — mid-run, that reads as a loss it never took.
    partial = sorted(p for p, d in per.items()
                     if not d["solved"] and d["n_searches"] < c["k"])
    n, m = len(groups), len(searched)
    print(f"[summary {c['rule']} top-{c['k']} @ {c['budget']:,}] {m}/{n} "
          f"presentations searched"
          + (f" — {len(missing)} NOT STARTED, every number below is over the "
             f"{m} searched" if missing else "")
          + (f"; {len(partial)} still have ranks to try {partial[:10]} and "
             f"count as unsolved below" if partial else ""), flush=True)
    if not m:
        return {"searched": searched, "solved": hit, "per": per}

    g_m = {p for p, s in baseline_at(matched, root).items() if s} & searched
    g_1 = {p for p, s in baseline_at(c["budget"], root).items() if s} & searched
    print(f"  {c['rule']} top-{c['k']} @ {c['budget']:,}   : {len(hit)}/{m}",
          flush=True)
    print(f"  plain greedy @ {c['budget']:,} (1 search): {len(g_1)}/{m}",
          flush=True)
    print(f"  plain greedy @ {matched:,} (node-matched): {len(g_m)}/{m}",
          flush=True)
    only_a, only_g = sorted(hit - g_m), sorted(g_m - hit)
    print(f"  discordant vs node-matched: {len(only_a)} only {c['rule']} "
          f"{only_a[:20] or ''} | {len(only_g)} only greedy {only_g[:20] or ''}",
          flush=True)
    ranks = [per[p]["rank"] for p in hit]
    print(f"  solving rank: "
          + " ".join(f"r{i}={ranks.count(i)}" for i in range(1, c["k"] + 1))
          + f" | unsolved={m - len(hit)}", flush=True)

    # -- the paired comparison, on rows BOTH arms solved -----------------------
    pair = sorted(p for p in hit if per[p]["base_solved"]
                  and per[p]["base_nodes_explored"] is not None)
    if pair:
        cn = _stats([per[p]["cum_nodes"] for p in pair])
        bn = _stats([per[p]["base_nodes_explored"] for p in pair])
        cp = _stats([per[p]["path_length"] for p in pair])
        bp = _stats([per[p]["base_path_length"] for p in pair])
        w_n = sum(1 for p in pair
                  if per[p]["cum_nodes"] < per[p]["base_nodes_explored"])
        t_n = sum(1 for p in pair
                  if per[p]["cum_nodes"] == per[p]["base_nodes_explored"])
        w_p = sum(1 for p in pair
                  if per[p]["path_length"] < per[p]["base_path_length"])
        t_p = sum(1 for p in pair
                  if per[p]["path_length"] == per[p]["base_path_length"])
        print(f"  paired on {len(pair)} presentations both arms solved "
              f"(plain greedy's own cost at its 1,000,000-node budget):",
              flush=True)
        print(f"    nodes  {c['rule']}: median {cn['median']:,} mean "
              f"{cn['mean']:,.0f} max {cn['max']:,} total {cn['total']:,}",
              flush=True)
        print(f"    nodes  greedy: median {bn['median']:,} mean "
              f"{bn['mean']:,.0f} max {bn['max']:,} total {bn['total']:,}"
              f"  ->  {c['rule']} cheaper on {w_n}, tied {t_n}, dearer on "
              f"{len(pair) - w_n - t_n}", flush=True)
        print(f"    path   {c['rule']}: median {cp['median']} mean "
              f"{cp['mean']:.1f} max {cp['max']}", flush=True)
        print(f"    path   greedy: median {bp['median']} mean "
              f"{bp['mean']:.1f} max {bp['max']}"
              f"  ->  {c['rule']} shorter on {w_p}, tied {t_p}, longer on "
              f"{len(pair) - w_p - t_p}", flush=True)
        print("    (a CoV path certifies the TRANSFORMED pair — the original is "
              "stably AC-trivial, and this path length is not its certificate)",
              flush=True)

    n_ov, bad = verify_overlap(out_path, root, budget=c["budget"])
    print(f"  [gate] {n_ov} searches overlap the frozen 10,000-node sweep: "
          + ("all agree" if not bad else f"{len(bad)} DISAGREE"), flush=True)
    for b in bad[:10]:
        print(f"    ! {b}", flush=True)
    return {"solved": hit, "searched": searched, "greedy_matched": g_m,
            "greedy_one": g_1, "per": per, "paired": pair, "missing": missing,
            "partial": partial, "overlap": n_ov, "overlap_violations": bad}


def compare_rules(path_a, path_b, root=ROOT, k=manifest.K, label_a="abel",
                  label_b="len"):
    """Head-to-head between the two arms' result files, on their COMMON rows.

    Neither arm is scored on a presentation the other has not searched: with two
    sessions finishing at different times, an intersection is the only
    denominator both arms have actually earned.
    """
    a, b = (per_presentation(path_a, k, root), per_presentation(path_b, k, root))
    common = sorted(set(a) & set(b))
    ha = {p for p in common if a[p]["solved"]}
    hb_ = {p for p in common if b[p]["solved"]}
    print(f"[compare] {len(common)} presentations searched by both arms",
          flush=True)
    print(f"  {label_a}: {len(ha)}/{len(common)} | "
          f"{label_b}: {len(hb_)}/{len(common)} | both {len(ha & hb_)} | "
          f"only {label_a} {sorted(ha - hb_)[:20]} | "
          f"only {label_b} {sorted(hb_ - ha)[:20]}", flush=True)
    both = sorted(ha & hb_)
    if both:
        an = _stats([a[p]["cum_nodes"] for p in both])
        bn = _stats([b[p]["cum_nodes"] for p in both])
        ap_ = _stats([a[p]["path_length"] for p in both])
        bp = _stats([b[p]["path_length"] for p in both])
        print(f"  on the {len(both)} both solved — nodes {label_a} median "
              f"{an['median']:,} mean {an['mean']:,.0f} | {label_b} median "
              f"{bn['median']:,} mean {bn['mean']:,.0f}", flush=True)
        print(f"  on the {len(both)} both solved — path  {label_a} median "
              f"{ap_['median']} mean {ap_['mean']:.1f} | {label_b} median "
              f"{bp['median']} mean {bp['mean']:.1f}", flush=True)
    return {"common": common, label_a: ha, label_b: hb_}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rule", choices=sorted(manifest.RULES))
    ap.add_argument("--budget", type=int)
    ap.add_argument("--k", type=int)
    ap.add_argument("--chunks", type=int)
    ap.add_argument("--chunk-index", type=int, dest="chunk_index")
    ap.add_argument("--no-high-speedup", action="store_const", const=False,
                    dest="high_speedup")
    ap.add_argument("--merge", action="store_true",
                    help="fold completed chunk files into the unchunked file")
    ap.add_argument("--summarize", metavar="JSONL",
                    help="print the arm's scoreboard from an existing jsonl")
    a = ap.parse_args()
    kw = {k: v for k, v in vars(a).items()
          if k not in ("merge", "summarize") and v is not None}
    if a.summarize:
        summarize(a.summarize, **kw)
    elif a.merge:
        merge_chunks(**kw)
    else:
        summarize(run(**kw), **kw)


if __name__ == "__main__":
    main()
