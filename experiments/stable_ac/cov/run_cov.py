"""CoV runner: benchmark CSV rows → one-shot CoV → 2-gen numba greedy → jsonl.

Reuses ``run_baseline``'s seams by import (the ``greedy_search`` dispatcher,
``_repair_jsonl`` / ``_read_done`` resume machinery, ``_build_row`` schema) and
writes to its own namespace ``results/stable_ac/cov/``. One output file per
budget — when the budget changes, the file changes. jsonl schema = the greedy
schema + ``{mode, z_word, n_cov, cov_applicable, r1_orig, r2_orig,
start_total_length_orig, start_total_length_cov, iso_index, n_subs, source}``.

``mode: baseline`` runs the identity transform on the same rows/budgets so a
same-budget cov-vs-baseline comparison needs no other pipeline.

``experiment_length: true`` is the length-sweep experiment: per presentation,
run the greedy from EVERY valid subword-derived CoV (``cov.enumerate_cov``)
plus one no-CoV control row, so the jsonl directly answers whether post-CoV
start length predicts search outcome. Sweep rows are keyed ``(pres_id,
z_word)`` — the control row has ``z_word: null`` — and the file prefix is
``covsweep_..._sub{K}_`` where K = ``subword_max_len``.

CLI (from the repo root):
    .venv/bin/python3 -m experiments.stable_ac.cov.run_cov \
        --config experiments/stable_ac/cov/config_cov.yaml
"""

import argparse
import csv
import glob
import json
import os
import time
from datetime import datetime

import yaml

from experiments import run_baseline
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov

COV_DEFAULTS = {
    "datasets": [
        "results/benchmark/subsets/benchmark_subset_10.csv",
        "results/benchmark/reach/reach_tier_1.csv",
    ],
    "budgets": [100, 1000],
    "mode": "cov",                    # "cov" | "baseline"
    "z_family": cov.Z_FAMILY_TAG,
    "max_relator_length": cov.DEFAULT_CAP,
    "cap_headroom": cov.CAP_HEADROOM,
    "reject_len": cov.REJECT_LEN,
    "cyclic_reduce": True,
    "out_dir": "results/stable_ac/cov",
    "resume": True,
    "experiment_length": False,       # length sweep: all subword CoVs + control
    "subword_max_len": 4,             # sweep z = relator subwords of len 2..this
}


_GIT_COMMIT = False   # False = not yet resolved (None is a valid answer)


def _git_commit():
    """HEAD of the checkout this module runs from; None outside a git repo.

    Provenance only — which code produced a row. NOT part of `_run_prefix`
    (it is not a knob, and resume must survive a code update)."""
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


def find_repo_root(start):
    """Walk up until a dir holds both experiments/ and data/ (repo rule)."""
    d = os.path.abspath(start)
    while True:
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(f"no repo root (experiments/ + data/) above {start}")
        d = parent


def load_config(config_path=None, **overrides):
    c = dict(COV_DEFAULTS)
    if config_path:
        with open(config_path) as f:
            c.update(yaml.safe_load(f) or {})
    c.update({k: v for k, v in overrides.items() if v is not None})
    if c["mode"] not in ("cov", "baseline"):
        raise ValueError(f"mode must be 'cov' or 'baseline', got {c['mode']!r}")
    if c.get("experiment_length") and c["mode"] != "cov":
        raise ValueError("experiment_length requires mode 'cov' "
                         "(the sweep already contains its own control rows)")
    return c


def load_rows(dataset_paths, root):
    """(row_id, r1, r2, source) per benchmark row.

    Subset CSVs key rows by int ``pres_id``; reach CSVs by the ``name`` column
    (e.g. "AK(3)"). Both id kinds land in the jsonl ``pres_id`` field and in
    the resume set unchanged.
    """
    rows = []
    for p in dataset_paths:
        ap = p if os.path.isabs(p) else os.path.join(root, p)
        src = os.path.basename(p)
        with open(ap) as f:
            for rec in csv.DictReader(f):
                rid = int(rec["pres_id"]) if "pres_id" in rec else rec["name"]
                rows.append((rid, rec["r1"], rec["r2"], src))
    return rows


def _dataset_tag(dataset_paths):
    parts = []
    for p in dataset_paths:
        stem = os.path.splitext(os.path.basename(p))[0]
        digits = "".join(ch for ch in stem if ch.isdigit())
        lead = "s" if "subset" in stem else ("r" if "reach" in stem else stem[:3])
        parts.append(lead + digits)
    return "".join(parts)


def _run_prefix(c, node_budget, n_rows):
    """Date-less stem of every knob that changes the result (resume identity).

    The z-family tag is identity for cov mode (a different family = a different
    experiment); row caps are derived deterministically from the inputs, so
    they stay out of the name. mrl = the base cap / baseline cap. The length
    sweep is its own kind (covsweep) and its family tag is sub{K}: the family
    is derived from the presentation, so K is the only family knob.
    """
    kind = "cov" if c["mode"] == "cov" else "covbase"
    zfam = f"{c['z_family']}_" if c["mode"] == "cov" else ""
    if c.get("experiment_length"):
        kind = "covsweep"
        zfam = f"sub{c['subword_max_len']}_"
    cyc = "cyc" if c["cyclic_reduce"] else "noncyc"
    tag = _dataset_tag(c["datasets"])
    return (f"{kind}_{node_budget}_{n_rows}_{zfam}mrl{c['max_relator_length']}"
            f"_{cyc}_{tag}_")


def _resolve_out_path(c, node_budget, n_rows, root):
    out_dir = c["out_dir"]
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(root, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(c, node_budget, n_rows)
    stem = prefix + datetime.now().strftime("%m_%d_%y")
    if c.get("resume", True):
        existing = glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]
    return os.path.join(out_dir, stem + ".jsonl")


def _base_cfg(c):
    """run_baseline-compatible cfg for ``_build_row`` (paths inline)."""
    base = dict(run_baseline.DEFAULT_CONFIG)
    base["MAX_RELATOR_LENGTH"] = c["max_relator_length"]
    base["CYCLIC_REDUCE"] = c["cyclic_reduce"]
    base["PATH_IN_SEPARATE_FILE"] = False
    return base


def _transform(c, r1, r2):
    """(r1', r2', cap, n_cov, extra-fields) for one row under c["mode"]."""
    if c["mode"] == "baseline":
        return r1, r2, c["max_relator_length"], 0, {
            "cov_applicable": None, "z_word": None, "iso_index": None,
            "n_subs": 0,
            "start_total_length_orig": len(r1) + len(r2),
            "start_total_length_cov": len(r1) + len(r2),
        }
    r1t, r2t, cap, n_cov, meta = cov.cov_for_greedy(
        r1, r2,
        default_cap=c["max_relator_length"],
        cap_headroom=c["cap_headroom"],
        reject_len=c["reject_len"],
    )
    return r1t, r2t, cap, n_cov, meta


def run_budget(c, node_budget, rows, root):
    out_path = _resolve_out_path(c, node_budget, len(rows), root)
    run_baseline._repair_jsonl(out_path)
    done, n_seen, n_solved = run_baseline._read_done(out_path)
    print(f"[{c['mode']}] budget={node_budget} -> {os.path.basename(out_path)} "
          f"(resume: {n_seen} done, {n_solved} solved)", flush=True)

    bcfg = _base_cfg(c)
    with open(out_path, "a") as out_f:
        for rid, r1, r2, src in rows:
            if rid in done:
                continue
            r1t, r2t, cap, n_cov, extra = _transform(c, r1, r2)
            t0 = time.perf_counter()
            stats = run_baseline.greedy_search(
                r1t, r2t, node_budget, max_relator_length=cap,
                cyclic_reduce=c["cyclic_reduce"])
            elapsed = time.perf_counter() - t0

            row = run_baseline._build_row(bcfg, rid, r1t, r2t, node_budget,
                                          stats, elapsed)
            row["max_relator_length_cap"] = cap
            row["mode"] = c["mode"]
            row["n_cov"] = n_cov
            row["r1_orig"] = r1
            row["r2_orig"] = r2
            row["source"] = src
            row["git_commit"] = _git_commit()
            row.update(extra)
            out_f.write(json.dumps(row) + "\n")
            out_f.flush()
            os.fsync(out_f.fileno())

            n_seen += 1
            n_solved += int(bool(stats["solved"]))
            print(f"  {rid}: solved={stats['solved']} "
                  f"nodes={stats['nodes_explored']} "
                  f"path={stats['path_length']} cap={cap} "
                  f"z={extra.get('z_word')}", flush=True)
    print(f"[{c['mode']}] budget={node_budget} done: "
          f"{n_solved}/{n_seen} solved", flush=True)
    return out_path


def _read_done_pairs(out_path):
    """({(pres_id, z_word)}, n_seen, n_solved) from an existing sweep jsonl.

    Sweep rows are keyed per (presentation, z) like run_nocov's (name, z_word);
    the control row's key is (pres_id, None). Same torn-final-line tolerance
    as ``run_baseline._read_done``: unparseable elsewhere is real corruption.
    """
    done, n_seen, n_solved = set(), 0, 0
    if not os.path.exists(out_path):
        return done, n_seen, n_solved
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
        done.add((row["pres_id"], row["z_word"]))
        n_seen += 1
        n_solved += int(bool(row.get("solved")))
    return done, n_seen, n_solved


def _sweep_entries(c, r1, r2):
    """[(z_str, r1t, r2t, cap, n_cov, extra)] — control first (z_str None,
    original pair, baseline cap), then every valid subword CoV in canonical
    family order."""
    orig_len = len(r1) + len(r2)
    entries = [(None, r1, r2, c["max_relator_length"], 0, {
        "cov_applicable": None, "z_word": None, "iso_index": None, "n_subs": 0,
        "start_total_length_orig": orig_len,
        "start_total_length_cov": orig_len,
    })]
    results = cov.enumerate_cov(
        str_to_word(r1), str_to_word(r2),
        default_cap=c["max_relator_length"], cap_headroom=c["cap_headroom"],
        reject_len=c["reject_len"], subword_max_len=c["subword_max_len"])
    for res in results:
        z = word_to_str(res.z_word)
        r1t, r2t = word_to_str(res.r1), word_to_str(res.r2)
        entries.append((z, r1t, r2t, res.cap, 1, {
            "cov_applicable": True, "z_word": z, "iso_index": res.iso_index,
            "n_subs": res.n_subs,
            "start_total_length_orig": orig_len,
            "start_total_length_cov": len(r1t) + len(r2t),
        }))
    return entries


def run_budget_sweep(c, node_budget, rows, root):
    """The length experiment: every start (control + all CoV variants) per
    presentation, one row per (pres_id, z_word), then the length-vs-outcome
    digest. Same write discipline as ``run_budget``."""
    out_path = _resolve_out_path(c, node_budget, len(rows), root)
    run_baseline._repair_jsonl(out_path)
    done, n_seen, n_solved = _read_done_pairs(out_path)
    print(f"[sweep] budget={node_budget} -> {os.path.basename(out_path)} "
          f"(resume: {n_seen} done, {n_solved} solved)", flush=True)

    bcfg = _base_cfg(c)
    with open(out_path, "a") as out_f:
        for rid, r1, r2, src in rows:
            entries = _sweep_entries(c, r1, r2)
            ran = solved_here = 0
            for z, r1t, r2t, cap, n_cov, extra in entries:
                if (rid, z) in done:
                    continue
                t0 = time.perf_counter()
                stats = run_baseline.greedy_search(
                    r1t, r2t, node_budget, max_relator_length=cap,
                    cyclic_reduce=c["cyclic_reduce"])
                elapsed = time.perf_counter() - t0

                row = run_baseline._build_row(bcfg, rid, r1t, r2t, node_budget,
                                              stats, elapsed)
                row["max_relator_length_cap"] = cap
                row["mode"] = "cov"
                row["n_cov"] = n_cov
                row["r1_orig"] = r1
                row["r2_orig"] = r2
                row["source"] = src
                row["git_commit"] = _git_commit()
                row.update(extra)
                out_f.write(json.dumps(row) + "\n")
                out_f.flush()
                os.fsync(out_f.fileno())

                ran += 1
                solved_here += int(bool(stats["solved"]))
            n_seen += ran
            n_solved += solved_here
            print(f"  {rid}: {len(entries)} starts (1 control + "
                  f"{len(entries) - 1} cov), ran {ran}, solved {solved_here}",
                  flush=True)
    print(f"[sweep] budget={node_budget} done: {n_solved}/{n_seen} solved",
          flush=True)
    _sweep_summary(out_path)
    return out_path


def _sweep_summary(out_path):
    """The digest the experiment exists for: per 5-wide bin of post-CoV start
    length, n / solved / median nodes-to-solve; then control vs best CoV start
    per presentation. Read back from the file so a resumed run digests every
    row, not just this session's."""
    rows = []
    with open(out_path) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    variants = [r for r in rows if r["z_word"] is not None]
    controls = [r for r in rows if r["z_word"] is None]
    if not variants:
        print("[sweep] no cov variants recorded", flush=True)
        return
    print(f"[sweep] post-CoV start length vs outcome "
          f"({len(variants)} cov starts, {len(controls)} controls):", flush=True)
    bins = {}
    for r in variants:
        bins.setdefault(r["start_total_length_cov"] // 5 * 5, []).append(r)
    for lo in sorted(bins):
        rs = bins[lo]
        solved = sorted(r["nodes_explored"] for r in rs if r["solved"])
        med = solved[len(solved) // 2] if solved else "-"
        print(f"  len {lo:>2}-{lo + 4:<3} n={len(rs):>3}  "
              f"solved={len(solved):>3}/{len(rs):<3} median_nodes={med}",
              flush=True)
    print("[sweep] control vs best cov start per presentation:", flush=True)
    for ctrl in controls:
        rid = ctrl["pres_id"]
        sv = [r for r in variants if r["pres_id"] == rid and r["solved"]]
        best = min(sv, key=lambda r: r["nodes_explored"]) if sv else None
        n_tried = sum(r["pres_id"] == rid for r in variants)
        c_txt = (f"control nodes={ctrl['nodes_explored']}" if ctrl["solved"]
                 else "control UNSOLVED")
        b_txt = (f"best z={best['z_word']} len={best['start_total_length_cov']} "
                 f"nodes={best['nodes_explored']}" if best
                 else f"no cov start solved ({n_tried} tried)")
        print(f"  {rid}: {c_txt} | {b_txt}", flush=True)


def run(config_path=None, **overrides):
    c = load_config(config_path, **overrides)
    root = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
    rows = load_rows(c["datasets"], root)
    sweep = bool(c.get("experiment_length"))
    print(f"{len(rows)} presentations from {len(c['datasets'])} dataset(s); "
          f"budgets {c['budgets']}; mode {c['mode']}"
          f"{' (length sweep)' if sweep else ''}", flush=True)
    runner = run_budget_sweep if sweep else run_budget
    return [runner(c, b, rows, root) for b in c["budgets"]]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None, help="config_cov.yaml path")
    ap.add_argument("--mode", default=None, choices=["cov", "baseline"])
    ap.add_argument("--budget", type=int, nargs="*", default=None,
                    help="override budgets, e.g. --budget 100 1000")
    ap.add_argument("--experiment-length", action="store_true", default=None,
                    help="run the length sweep (all subword CoVs + control)")
    args = ap.parse_args()
    run(config_path=args.config, mode=args.mode, budgets=args.budget,
        experiment_length=args.experiment_length)


if __name__ == "__main__":
    main()
