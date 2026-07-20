"""Restart-tree driver: iterated-CoV restart points → greedy per point → jsonl.

Implements ``IMPLEMENTATION_IDEAS.md`` idea 1. ``restart_planner.build_restart_plan``
ranks a presentation's distinct-orbit change-of-variables restart points (deduped by
Aut(F₂)-orbit, cap-fit filtered); this driver *runs* them: per rep, search the base
presentation and then each restart point best-first at production budget, stopping the
rep on its first solve, with jsonl + resume so a Colab disconnect reattaches.

Reuses ``run_baseline``'s seams by import — ``greedy_search`` (the single monkeypatch
seam), ``_repair_jsonl`` / ``_build_row`` / ``DEFAULT_CONFIG``, ``load_dataset`` /
``int_line_to_relators`` for the flat-int reps in ``data/ms_unsolved_reps/`` — and
``run_cov``'s ``find_repo_root`` / ``_git_commit``. Writes to its own namespace
``results/stable_ac/restart/``. Row schema = the greedy schema +
``{restart_rep, restart_r1, restart_r2, hop, abel, rank, r1_orig, r2_orig, source}``.

Resume key is ``(pres_id, restart_rep)``; a rep whose jsonl already holds a solved row
is skipped whole. The plan is deterministic (``aut_canon`` + a total order), so resume
replays the identical restart sequence.

CERTIFICATE ACCOUNTING (read this): a restart point is reached from the original by a
sequence of change-of-variables moves, and CoV = stabilize + substitute + isolate +
destabilize + relabel is a *stable*-AC operation (``PROOFS.tex`` Thm 1–3). So a solved
restart row establishes **stable**-triviality of the original — which is the project's
actual question — but the row's ``path`` is the greedy path *from the restart point*,
not the full concatenated Definition-2.1 certificate from the original. The planner
currently records ``orbit_rep``/``hop``, not the CoV branch moves, so emitting the
fully concatenated path (base → restart CoV prefix + greedy suffix) for
``verify_results.py`` is a documented follow-up (thread the branch sequence through
``restart_planner``). Until then, verify the *suffix* against the restart pair, and
treat the CoV prefix as certified structurally by the CoV construction, not replayed.

Local runs are capped at ``node_budget`` 1000 — a bigger budget refuses without
``ACSOLVERX_ALLOW_BIG=1`` (the notebook sets it; local runs must not), mirroring
``run_nocov.py``. Production budgets are the user's, on Colab.

CLI (from the repo root):
    .venv/bin/python3 -m experiments.stable_ac.cov.run_restart_tree \
        --data data/ms_unsolved_reps/ms_reps_126.txt --budget 1000 \
        --depth 2 --subset 0 3
"""

import argparse
import glob
import json
import os
import time
from datetime import datetime

from experiments import run_baseline
from experiments.greedy_tests.spec.words import str_to_word
from experiments.stable_ac.cov.restart_planner import build_restart_plan, abel_magnitude
from experiments.stable_ac.cov.run_cov import find_repo_root, _git_commit

DEFAULTS = {
    "data": "data/ms_unsolved_reps/ms_reps_126.txt",
    "budget": 1000,
    "depth": 2,
    "cap": 24,
    "max_nodes": 400,       # planner tree bound (NOT a search budget)
    "cyclic_reduce": True,
    "out_dir": "results/stable_ac/restart",
    "resume": True,
}


def _aut_rep_str(pair):
    """Aut(F₂)-orbit canonical rep of a (r1, r2) string pair, JSON-able."""
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    rep = aut_canon((pair[0], pair[1]))[1]
    return f"{rep[0]},{rep[1]}"


def _rep_str(orbit_rep):
    """Planner records orbit_rep as a (r1, r2) tuple; normalize to the joined
    string used for both the jsonl field and the resume key."""
    if isinstance(orbit_rep, (tuple, list)):
        return f"{orbit_rep[0]},{orbit_rep[1]}"
    return orbit_rep


def load_reps(data_path, root, subset=None):
    """[(pres_id, r1, r2, source)] from a flat-int reps file (via
    ``run_baseline.load_dataset``: 1=x,-1=X,2=y,-2=Y,0=pad). ``subset`` is a
    half-open (start, end) index range or a list of pres_ids, passed through."""
    ap = data_path if os.path.isabs(data_path) else os.path.join(root, data_path)
    src = os.path.basename(data_path)
    return [(pid, r1, r2, src)
            for pid, r1, r2 in run_baseline.load_dataset(ap, subset=subset)]


def _run_prefix(c, n_reps):
    tag = os.path.splitext(os.path.basename(c["data"]))[0]
    cyc = "cyc" if c["cyclic_reduce"] else "noncyc"
    return (f"restart_{c['budget']}_{n_reps}_d{c['depth']}_"
            f"mrl{c['cap']}_{cyc}_{tag}_")


def _resolve_out_path(c, n_reps, root):
    out_dir = c["out_dir"]
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(root, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(c, n_reps)
    stem = prefix + datetime.now().strftime("%m_%d_%y")
    if c.get("resume", True):
        existing = glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]
    return os.path.join(out_dir, stem + ".jsonl")


def _read_done_restart(out_path):
    """({(pres_id, restart_rep)}, {solved pres_ids}, n_seen, n_solved) from a
    restart jsonl. A rep with any solved row is skipped whole; within a rep,
    a done (pres_id, restart_rep) is not re-searched. Same torn-final-line
    tolerance as ``run_baseline._read_done`` — unparseable elsewhere is real
    corruption."""
    done, solved_reps, n_seen, n_solved = set(), set(), 0, 0
    if not os.path.exists(out_path):
        return done, solved_reps, n_seen, n_solved
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
        done.add((row["pres_id"], row["restart_rep"]))
        n_seen += 1
        if row.get("solved"):
            n_solved += 1
            solved_reps.add(row["pres_id"])
    return done, solved_reps, n_seen, n_solved


def _base_cfg(c):
    base = dict(run_baseline.DEFAULT_CONFIG)
    base["MAX_RELATOR_LENGTH"] = c["cap"]
    base["CYCLIC_REDUCE"] = c["cyclic_reduce"]
    base["PATH_IN_SEPARATE_FILE"] = False
    return base


def _restart_points(rid, r1, r2, c):
    """[(rank, restart_rep, restart_r1, restart_r2, hop, abel)] — the base
    presentation (rank 0, hop 0) first, then the planner's ranked restart tree.
    The base is included so 'search from the original coordinates' is always a
    tried, logged option, not an implicit assumption."""
    base_rep = _aut_rep_str((r1, r2))
    base_abel = abel_magnitude(str_to_word(r1), str_to_word(r2))
    pts = [(0, base_rep, r1, r2, 0, base_abel)]
    plan = build_restart_plan(r1, r2, depth=c["depth"], cap=c["cap"],
                              max_nodes=c["max_nodes"])
    for rank, rec in enumerate(plan, start=1):
        pts.append((rank, _rep_str(rec["orbit_rep"]), rec["r1"], rec["r2"],
                    rec["hop"], rec["abel"]))
    return pts


def run(config=None, **overrides):
    c = dict(DEFAULTS)
    if config:
        c.update(config)
    c.update({k: v for k, v in overrides.items() if v is not None})

    if c["budget"] > 1000 and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise RuntimeError(
            f"node_budget {c['budget']} > 1000 refused locally; set "
            f"ACSOLVERX_ALLOW_BIG=1 (the notebook does; local runs must not).")

    root = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
    reps = load_reps(c["data"], root, subset=c.get("subset"))
    out_path = _resolve_out_path(c, len(reps), root)
    run_baseline._repair_jsonl(out_path)
    done, solved_reps, n_seen, n_solved = _read_done_restart(out_path)
    print(f"[restart] budget={c['budget']} depth={c['depth']} "
          f"{len(reps)} reps -> {os.path.basename(out_path)} "
          f"(resume: {n_seen} rows, {len(solved_reps)} reps solved)", flush=True)

    bcfg = _base_cfg(c)
    with open(out_path, "a") as out_f:
        for rid, r1, r2, src in reps:
            if rid in solved_reps:
                continue
            for rank, rep, rr1, rr2, hop, abel in _restart_points(rid, r1, r2, c):
                if (rid, rep) in done:
                    continue
                t0 = time.perf_counter()
                stats = run_baseline.greedy_search(
                    rr1, rr2, c["budget"], max_relator_length=c["cap"],
                    cyclic_reduce=c["cyclic_reduce"])
                elapsed = time.perf_counter() - t0

                row = run_baseline._build_row(bcfg, rid, rr1, rr2, c["budget"],
                                              stats, elapsed)
                row["max_relator_length_cap"] = c["cap"]
                row["restart_rep"] = rep
                row["restart_r1"] = rr1
                row["restart_r2"] = rr2
                row["hop"] = hop
                row["abel"] = abel
                row["rank"] = rank
                row["r1_orig"] = r1
                row["r2_orig"] = r2
                row["source"] = src
                row["git_commit"] = _git_commit()
                out_f.write(json.dumps(row) + "\n")
                out_f.flush()
                os.fsync(out_f.fileno())

                n_seen += 1
                print(f"  {rid} rank={rank} hop={hop} abel={abel} "
                      f"solved={stats['solved']} nodes={stats['nodes_explored']}",
                      flush=True)
                if stats["solved"]:
                    n_solved += 1
                    solved_reps.add(rid)
                    break
    print(f"[restart] done: {len(solved_reps)}/{len(reps)} reps solved "
          f"({n_seen} restart points searched)", flush=True)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Run the iterated-CoV restart tree.")
    ap.add_argument("--data", default=None)
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--depth", type=int, default=None)
    ap.add_argument("--cap", type=int, default=None)
    ap.add_argument("--max-nodes", type=int, default=None,
                    help="planner tree bound (not a search budget)")
    ap.add_argument("--subset", type=int, nargs=2, default=None,
                    metavar=("START", "END"), help="half-open pres index range")
    args = ap.parse_args()
    subset = tuple(args.subset) if args.subset else None
    run(data=args.data, budget=args.budget, depth=args.depth, cap=args.cap,
        max_nodes=args.max_nodes, subset=subset)


if __name__ == "__main__":
    main()
