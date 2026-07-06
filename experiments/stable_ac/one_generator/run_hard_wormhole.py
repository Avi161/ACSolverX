#!/usr/bin/env python3
"""Hard-but-solvable "wormhole" word-choice sweep — the driver.

Sibling of ``run_ak3_wormhole.py``. Throws ~97 candidate words ``w(x,y)`` (from ``hard_words``) at a
presentation the 2-gen greedy DID solve but only after many nodes + a long path, via the 3-generator
``z=w`` stabilization + greedy solver. Two-tier:

  * SCREEN  — every word x each target at a small budget (default 100k), parallel. Catches the
              r1/r2-class solves (they land <100k) and measures how close each word got
              (``min_total_len`` + ``min_total_state``, the actual closest presentation).
  * FULL    — every still-unsolved word escalated to the big budget (default 1,000,000), ONE worker
              (a 1M n=3 run peaks ~12 GB RSS on these targets), priority-ordered. Deferred: NOT run
              by default — the user picks the subset after seeing the screen.

Targets (locked): idx 625 (MS n=7, hardest) + idx 610 (MS n=6). Built-in controls already on disk:
2-gen and n=3 dumb-word (r1/r2/x/y @500k) baselines under results/.../ms640 and results/baseline_greedy.

Crash-safe & resumable (project convention): append-only JSONL, one line per ``(idx,word,budget)``,
append+flush+fsync; a re-run skips recorded ``(idx,word_name,budget)``; path row written before the
metric row (reuses ``run_baseline_greedy.persist``).

Output under ``--out_dir`` (default results/stable_ac/3_generators_w_choices/hard_solved_test/):
    runs/hard_ms<idx>_<budget>.jsonl   # one row per (idx,word): solved + unsolved together
    paths/hard_ms<idx>.jsonl           # one row per SOLVED (idx,word): replayable move+state path

Usage:
    python run_hard_wormhole.py --phase screen                       # all words x {625,610} @100k
    python run_hard_wormhole.py --phase screen --targets 625 --only r1   # base-case one word
    python run_hard_wormhole.py --phase full --only <w1>,<w2>,...     # escalate a chosen subset to 1M
"""
import os
# macOS fork-safety: numba/obj threads + fork crash without this (Lessons Learned). Set before mp.
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

import argparse
import json
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                     # importable hard_probe/hard_words/greedy_nrel (fork+spawn)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import greedy_nrel as gn
import stabilize as stab
import ak3_words as aw
import hard_words as hw
from hard_probe import probe
from run_baseline_greedy import persist        # reuse: path-first, append+flush+fsync

L = 24
DATASET = "1190MS"
DEFAULT_OUT = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "hard_solved_test")


def control_words(base_flat):
    """The two baseline words w=r1, w=r2 (family 'control'). x,y come from the brute family."""
    rels = stab.flat_to_relators(base_flat, 2, L)
    out = []
    for spec, ri in (("r1", 0), ("r2", 1)):
        w = list(rels[ri])
        out.append({"name": spec, "family": "control", "priority": 8,
                    "w_str": aw.to_str(w), "w_ints": w, "w_len": len(w)})
    return out


def words_for(idx):
    """Full candidate list for a target: bank (~97) + 2 controls. Deduped by word_name."""
    base_flat = hw.load_target(idx)
    bank = hw.build_word_bank_for(base_flat)
    ctrl = control_words(base_flat)
    seen = {e["name"] for e in bank}
    return bank + [c for c in ctrl if c["name"] not in seen]


def runs_path(out_dir, idx, budget):
    return os.path.join(out_dir, "runs", f"hard_ms{idx}_{budget}.jsonl")


def paths_path(out_dir, idx):
    return os.path.join(out_dir, "paths", f"hard_ms{idx}.jsonl")


def read_runs(path, idx, budget):
    """word_name -> record, for an (idx,budget) stream (tolerates a trailing corrupt line)."""
    recs = {}
    if not os.path.exists(path):
        return recs
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("idx") == idx and r.get("budget_nodes") == budget:
                recs[r.get("word_name")] = r
    return recs


def build_tasks(idx, words, budget, done, max_len):
    base_flat = hw.load_target(idx)
    return [(idx, DATASET, w["name"], w["family"], w["w_ints"], base_flat, budget, max_len)
            for w in words if w["name"] not in done]


def run_phase(tasks, n_workers, out_dir, idx, budget, run_tag, label, t0, time_budget_s=None):
    """Run a list of probe tasks at n_workers, persisting each result. Returns (#run, #solved,
    list-of-solved-word_names). Stops launching new tasks once time_budget_s elapses (resumable)."""
    if not tasks:
        return 0, 0, []
    rp, pp = runs_path(out_dir, idx, budget), paths_path(out_dir, idx)
    n_run = n_solved = 0
    solved_names = []
    if n_workers < 1:
        it = ((probe(t), t) for t in tasks)              # serial in-process (n_workers=0 only)
        pool = None
    else:
        # Always use a pool (even 1 worker) with maxtasksperchild=1: a fresh forked child per word
        # releases each word's visited set (~12 GB @1M) when its child exits, so the parent never
        # accumulates RSS across the long run. With 1 worker, order is preserved.
        import multiprocessing as mp
        ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
        pool = ctx.Pool(n_workers, maxtasksperchild=1)
        it = ((rec, None) for rec in pool.imap_unordered(probe, tasks))
    try:
        for rec, _ in it:
            n_run += 1
            solved = bool(rec["solved"])
            n_solved += int(solved)
            if solved:
                solved_names.append(rec["word_name"])
                print(f"  *** SOLVE  idx={rec['idx']} w={rec['word_name']} "
                      f"({rec['family']})  nodes={rec['nodes_explored']}  "
                      f"path_len={rec['path_len']}  verified={rec['path_verified']} ***", flush=True)
            persist(rec, rp, pp, run_tag, n_workers)
            if n_run % 10 == 0 or n_run == len(tasks):
                print(f"  [{label}] {n_run}/{len(tasks)}  solved={n_solved}  "
                      f"({time.time() - t0:.0f}s)", flush=True)
            if time_budget_s is not None and (time.time() - t0) > time_budget_s:
                print(f"  [{label}] time budget {time_budget_s}s reached — stopping "
                      f"(resumable). {n_run}/{len(tasks)} done this phase.", flush=True)
                break
    finally:
        if pool is not None:
            pool.terminate(); pool.join()
    return n_run, n_solved, solved_names


def _filter_only(words, only):
    if not only:
        return words
    keep = {s.strip() for s in only.split(",") if s.strip()}
    return [w for w in words if w["name"] in keep]


def do_screen(args, targets, t0):
    print(f"\n===== SCREEN @ {args.budget_screen:,} nodes  ({args.screen_workers} workers) =====")
    total_solved = []
    for idx in targets:
        words = _filter_only(words_for(idx), args.only)
        done = set(read_runs(runs_path(args.out_dir, idx, args.budget_screen), idx,
                             args.budget_screen).keys())
        tasks = build_tasks(idx, words, args.budget_screen, done, args.max_len)
        print(f"[screen] idx={idx}: {len(words)} words, {len(done)} done, {len(tasks)} to run")
        tag = f"hard_ms{idx}_screen_b{args.budget_screen // 1000}k"
        _, ns, solved = run_phase(tasks, args.screen_workers, args.out_dir, idx,
                                  args.budget_screen, tag, f"screen:{idx}", t0)
        total_solved += [(idx, s) for s in solved]
    return total_solved


def do_full(args, targets, t0):
    print(f"\n===== FULL @ {args.budget_full:,} nodes  ({args.full_workers} worker) =====")
    total_solved = []
    for idx in targets:
        words = _filter_only(words_for(idx), args.only)
        screen = read_runs(runs_path(args.out_dir, idx, args.budget_screen), idx, args.budget_screen)
        full_done = set(read_runs(runs_path(args.out_dir, idx, args.budget_full), idx,
                                  args.budget_full).keys())
        # escalate words NOT solved in screen and NOT already run at full (unless --only overrides)
        if args.only:
            cand = [w for w in words if w["name"] not in full_done]
        else:
            cand = [w for w in words
                    if w["name"] not in full_done
                    and not (screen.get(w["name"], {}).get("solved", False))]
        # priority: known solvers first (controls), then family strength, then how close the screen
        # got (min_total_len asc), then screen nodes, then name.
        HERO = ["r1", "r2"]
        hero_rank = {name: i for i, name in enumerate(HERO)}

        def rank(w):
            sr = screen.get(w["name"], {})
            return (hero_rank.get(w["name"], len(HERO)), w["priority"],
                    sr.get("min_total_len", 10 ** 6), sr.get("nodes_explored", 10 ** 9), w["name"])
        cand.sort(key=rank)
        tasks = build_tasks(idx, cand, args.budget_full, set(), args.max_len)
        print(f"[full] idx={idx}: {len(tasks)} to escalate (priority-ordered), "
              f"{len(full_done)} already at 1M")
        tag = f"hard_ms{idx}_full_b{args.budget_full // 1000}k"
        _, ns, solved = run_phase(tasks, args.full_workers, args.out_dir, idx,
                                  args.budget_full, tag, f"full:{idx}", t0,
                                  time_budget_s=args.time_budget_s)
        total_solved += [(idx, s) for s in solved]
    return total_solved


def main():
    ap = argparse.ArgumentParser(description="Hard-but-solvable z=w word-choice sweep (two-tier, resumable).")
    ap.add_argument("--phase", choices=["screen", "full", "both"], default="screen",
                    help="default 'screen' — the 1M full tier is user-gated (run after seeing the screen)")
    ap.add_argument("--targets", default="625,610", help="comma list of 1190MS idx")
    ap.add_argument("--only", default=None, help="comma list of word_names to restrict to (base-case/escalation)")
    ap.add_argument("--budget_screen", type=int, default=100_000)
    ap.add_argument("--budget_full", type=int, default=1_000_000)
    ap.add_argument("--screen_workers", type=int, default=0, help="0 = auto min(6, cores-2)")
    ap.add_argument("--full_workers", type=int, default=1, help="keep 1: n=3 @1M ~12 GB RSS")
    ap.add_argument("--max_len", type=int, default=L)
    ap.add_argument("--time_budget_s", type=int, default=None,
                    help="full phase: stop launching new words after this many seconds (resumable)")
    ap.add_argument("--out_dir", default=DEFAULT_OUT)
    args = ap.parse_args()

    if args.screen_workers <= 0:
        args.screen_workers = max(1, min(6, (os.cpu_count() or 2) - 2))
    targets = [int(t.strip()) for t in args.targets.split(",") if t.strip()]
    os.makedirs(os.path.join(args.out_dir, "runs"), exist_ok=True)
    os.makedirs(os.path.join(args.out_dir, "paths"), exist_ok=True)

    print(f"[hard] targets={targets}  screen={args.budget_screen:,}({args.screen_workers}w)  "
          f"full={args.budget_full:,}({args.full_workers}w)  -> {os.path.relpath(args.out_dir, ROOT)}")
    n_words = len(words_for(targets[0]))
    print(f"[hard] {n_words} candidate words/target (bank + r1/r2 controls)"
          + (f"  [--only {args.only}]" if args.only else ""))

    gn.solve_one(aw.stabilize_with_word(hw.load_target(targets[0]), [1, 2, 1]),
                 n_gen=3, max_len=args.max_len, max_nodes=8)     # warm numba in parent
    t0 = time.time()

    solves = []
    if args.phase in ("screen", "both"):
        solves += do_screen(args, targets, t0)
    if args.phase in ("full", "both"):
        solves += do_full(args, targets, t0)

    print(f"\n[hard] DONE this run in {time.time() - t0:.0f}s.")
    if solves:
        print(f"[hard] *** {len(solves)} SOLVE(S): {solves} *** — verify with the reload->replay gate.")
    else:
        print("[hard] no solves this run (streams are resumable; escalate/continue).")


if __name__ == "__main__":
    main()
