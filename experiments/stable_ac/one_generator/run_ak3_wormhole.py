#!/usr/bin/env python3
"""AK(3) "wormhole" word-choice sweep — the driver.

Throws ~100 candidate words ``w(x,y)`` (from ``ak3_words``) at AK(3) via the 3-generator
``z=w`` stabilization + the greedy substitution solver, two-tier:

  * SCREEN  — every word x both AK(3) forms at a small budget (default 100k), parallel: catches
              any easy solve fast + measures how close greedy got (``min_total_len``).
  * FULL    — every still-unsolved word escalated to the big budget (default 1,000,000), ONE
              worker (a 1M n=3 run peaks ~10 GB RSS; 2 would swap a 17 GB box), in PRIORITY order
              (family strength 1->8, then screen ``min_total_len`` asc, then screen nodes asc).

Crash-safe & resumable (project convention): append-only JSONL, one line per ``(form,word,budget)``,
append+flush+fsync; a re-run skips recorded ``(form,word_name,budget)``; the path row is written
before the metric row (reuses ``run_baseline_greedy.persist``). A verified solve of AK(3) is headline.

Output under ``--out_dir`` (default results/stable_ac/3_generators_w_choices/ak_3_test/):
    runs/ak3_<form>_<budget>.jsonl   # one row per (form,word): solved + unsolved together
    paths/ak3_<form>.jsonl           # one row per SOLVED (form,word): replayable move+state path

Usage:
    python run_ak3_wormhole.py --phase screen                 # fast screen, all words x both forms
    python run_ak3_wormhole.py --phase full                   # escalate unsolved to 1M, priority order
    python run_ak3_wormhole.py --phase both                   # screen then full
    python run_ak3_wormhole.py --phase full --time_budget_s 36000   # stop launching after 10h (resumable)
"""
import os
# macOS fork-safety: numba/obj threads + fork crash without this (Lessons Learned). Set before mp.
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

import argparse
import json
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                     # importable ak3_probe/ak3_words/greedy_nrel (fork+spawn)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import greedy_nrel as gn
import stabilize as stab
import ak3_words as aw
from ak3_probe import probe
from run_baseline_greedy import persist        # reuse: path-first, append+flush+fsync

L = 24
DEFAULT_OUT = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ak_3_test")


def control_words(base_flat):
    """The two form-dependent baseline words w=r1, w=r2 (family 'control')."""
    rels = stab.flat_to_relators(base_flat, 2, L)
    out = []
    for spec, ri in (("r1", 0), ("r2", 1)):
        w = list(rels[ri])
        out.append({"name": spec, "family": "control", "priority": 8,
                    "w_str": aw.to_str(w), "w_ints": w, "w_len": len(w)})
    return out


def words_for(form):
    """Full candidate list for a form: bank (~95) + 2 controls. Deduped by word_name."""
    bank = aw.build_word_bank()
    ctrl = control_words(aw.FORMS[form])
    seen = {e["name"] for e in bank}
    return bank + [c for c in ctrl if c["name"] not in seen]


def runs_path(out_dir, form, budget):
    return os.path.join(out_dir, "runs", f"ak3_{form}_{budget}.jsonl")


def paths_path(out_dir, form):
    return os.path.join(out_dir, "paths", f"ak3_{form}.jsonl")


def read_runs(path, form, budget):
    """word_name -> record, for a (form,budget) stream (tolerates a trailing corrupt line)."""
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
            if r.get("form") == form and r.get("budget_nodes") == budget:
                recs[r.get("word_name")] = r
    return recs


def build_tasks(form, words, budget, done, max_len):
    base_flat = aw.FORMS[form]
    return [(form, f"AK3_{form}", w["name"], w["family"], w["w_ints"], base_flat, budget, max_len)
            for w in words if w["name"] not in done]


def run_phase(tasks, n_workers, out_dir, form, budget, run_tag, label, t0, time_budget_s=None):
    """Run a list of probe tasks at n_workers, persisting each result. Returns (#run, #solved,
    list-of-solved-word_names). Stops launching new tasks once time_budget_s elapses (resumable)."""
    if not tasks:
        return 0, 0, []
    rp, pp = runs_path(out_dir, form, budget), paths_path(out_dir, form)
    n_run = n_solved = 0
    solved_names = []
    if n_workers < 1:
        it = ((probe(t), t) for t in tasks)              # serial in-process (n_workers=0 only)
        pool = None
    else:
        # Always use a pool (even 1 worker) with maxtasksperchild=1: a fresh forked child per word
        # means each word's ~10 GB (1M-node) visited set is released when its child exits, so the
        # parent never accumulates RSS across the long full run. With 1 worker, order is preserved.
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
                print(f"  *** SOLVE  form={rec['form']} w={rec['word_name']} "
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


def do_screen(args, forms, t0):
    print(f"\n===== SCREEN @ {args.budget_screen:,} nodes  ({args.screen_workers} workers) =====")
    total_solved = []
    for form in forms:
        words = words_for(form)
        done = set(read_runs(runs_path(args.out_dir, form, args.budget_screen), form,
                             args.budget_screen).keys())
        tasks = build_tasks(form, words, args.budget_screen, done, args.max_len)
        print(f"[screen] form={form}: {len(words)} words, {len(done)} done, {len(tasks)} to run")
        tag = f"ak3_{form}_screen_b{args.budget_screen // 1000}k"
        _, ns, solved = run_phase(tasks, args.screen_workers, args.out_dir, form,
                                  args.budget_screen, tag, f"screen:{form}", t0)
        total_solved += [(form, s) for s in solved]
    return total_solved


def do_full(args, forms, t0):
    print(f"\n===== FULL @ {args.budget_full:,} nodes  ({args.full_workers} worker) =====")
    total_solved = []
    for form in forms:
        words = words_for(form)
        screen = read_runs(runs_path(args.out_dir, form, args.budget_screen), form,
                           args.budget_screen)
        full_done = set(read_runs(runs_path(args.out_dir, form, args.budget_full), form,
                                  args.budget_full).keys())
        # escalate words NOT solved in screen and NOT already run at full
        cand = [w for w in words
                if w["name"] not in full_done
                and not (screen.get(w["name"], {}).get("solved", False))]

        # HERO order: the theory's flagship words get their 1M budget FIRST (Fagan's z=xyx & alts,
        # the wk core k=0, the MS w1, w*). Everything else falls back to family priority then how
        # close the 100k screen got (min_total_len) then screen nodes, then name.
        HERO = ["xyx", "yxy", "xxx", "yyyy", "Xyxy", "YXyxy", "YxyX", "xyxY", "x", "y", "r1", "r2"]
        hero_rank = {name: i for i, name in enumerate(HERO)}

        def rank(w):
            sr = screen.get(w["name"], {})
            return (hero_rank.get(w["name"], len(HERO)),
                    w["priority"],
                    sr.get("min_total_len", 10 ** 6),      # closer to trivial first
                    sr.get("nodes_explored", 10 ** 9),
                    w["name"])
        cand.sort(key=rank)
        tasks = build_tasks(form, cand, args.budget_full, set(), args.max_len)
        print(f"[full] form={form}: {len(tasks)} to escalate (priority-ordered), "
              f"{len(full_done)} already at 1M")
        tag = f"ak3_{form}_full_b{args.budget_full // 1000}k"
        _, ns, solved = run_phase(tasks, args.full_workers, args.out_dir, form,
                                  args.budget_full, tag, f"full:{form}", t0,
                                  time_budget_s=args.time_budget_s)
        total_solved += [(form, s) for s in solved]
    return total_solved


def main():
    ap = argparse.ArgumentParser(description="AK(3) z=w word-choice sweep (two-tier, resumable).")
    ap.add_argument("--phase", choices=["screen", "full", "both"], default="both")
    ap.add_argument("--forms", default="textbook,rep", help="comma list; textbook first (primary)")
    ap.add_argument("--budget_screen", type=int, default=100_000)
    ap.add_argument("--budget_full", type=int, default=1_000_000)
    ap.add_argument("--screen_workers", type=int, default=0, help="0 = auto min(6, cores-2)")
    ap.add_argument("--full_workers", type=int, default=1, help="keep 1: n=3 @1M ~10 GB RSS")
    ap.add_argument("--max_len", type=int, default=L)
    ap.add_argument("--time_budget_s", type=int, default=None,
                    help="full phase: stop launching new words after this many seconds (resumable)")
    ap.add_argument("--out_dir", default=DEFAULT_OUT)
    args = ap.parse_args()

    if args.screen_workers <= 0:
        args.screen_workers = max(1, min(6, (os.cpu_count() or 2) - 2))
    forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    os.makedirs(os.path.join(args.out_dir, "runs"), exist_ok=True)
    os.makedirs(os.path.join(args.out_dir, "paths"), exist_ok=True)

    print(f"[ak3] forms={forms}  screen={args.budget_screen:,}({args.screen_workers}w)  "
          f"full={args.budget_full:,}({args.full_workers}w)  -> {os.path.relpath(args.out_dir, ROOT)}")
    n_words = len(words_for(forms[0]))
    print(f"[ak3] {n_words} candidate words/form (bank + r1/r2 controls)")

    gn.solve_one(aw.stabilize_with_word(aw.FORMS[forms[0]], [1, 2, 1]),
                 n_gen=3, max_len=args.max_len, max_nodes=8)     # warm numba in parent
    t0 = time.time()

    solves = []
    if args.phase in ("screen", "both"):
        solves += do_screen(args, forms, t0)
    if args.phase in ("full", "both"):
        solves += do_full(args, forms, t0)

    print(f"\n[ak3] DONE this run in {time.time() - t0:.0f}s.")
    if solves:
        print(f"[ak3] *** {len(solves)} SOLVE(S): {solves} *** — verify with the reload->replay gate.")
    else:
        print("[ak3] no solves this run (expected for AK(3); escalate/continue — streams are resumable).")


if __name__ == "__main__":
    main()
