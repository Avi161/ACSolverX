"""Exhaustive CoV sweep: the baseline greedy from every ``cov_all`` class + control.

Per presentation of the dataset, one control row (the untransformed pair, cap
``DEFAULT_CAP``) and one row per class of ``cov_all.enumerate_classes`` (family
``suballpxyb8``), each searched exactly as returned at ``res.cap``. The greedy is
``run_baseline.greedy_search`` with its default (path-recording) solver, unchanged.

Every row carries the full provenance of its start, so the transform can be
re-applied from the row alone: the z word, the chosen occurrences in the
cyclically reduced r1/r2 (``pattern``), the substituted pair, the defining
relator ``Z·w⁻¹``, which generator was eliminated, which relator isolated it and
the expression it was solved to (``iso_expr``). ``verify_cov_all`` re-derives
each start from that provenance and replays the stored paths.

Paths are NOT stored by default (only ``path_length`` and ``nodes_explored``).
``--path-sample p`` keeps ``path_moves`` inline on a deterministic fraction p of
the solved rows (hash of the row key), so a sample can be certified.

One jsonl per (dataset, budget) under ``results/stable_ac/cov_all/``, resumable
on ``(pres_id, class_key)``; the control row's key is the input's own class,
which ``enumerate_classes`` never returns. Rows are appended by the parent only,
flushed and fsynced in batches; a torn final line is dropped on resume.

CLI (from the repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.cov.run.run_cov_all --budget 100 --workers 64
"""

import argparse
import ast
import hashlib
import json
import os
import subprocess
import time
from multiprocessing import get_context

from experiments import run_baseline
from experiments.greedy_tests.spec.words import reduce_word, word_to_str
from experiments.stable_ac.cov import cov, cov_all

OUT_DIR = "results/stable_ac/cov_all"


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


def load_ms640(path):
    """``[(pres_id, r1, r2)]`` int tuples; pres_id is the 0-based line index."""
    out = []
    with open(path) as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            v = ast.literal_eval(line)
            half = len(v) // 2
            out.append((i, tuple(g for g in v[:half] if g),
                        tuple(g for g in v[half:] if g)))
    return out


def _s(word):
    return word_to_str(tuple(word))


def _aut(r1s, r2s):
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    rep = aut_canon((r1s, r2s))[1]
    return f"{rep[0]},{rep[1]}"


def _sampled(pres_id, key, frac):
    if frac <= 0:
        return False
    if frac >= 1:
        return True
    h = hashlib.md5(f"{pres_id}|{key}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64 < frac


def enumerate_pres(args):
    """All search tasks for one presentation (control first)."""
    pres_id, r1, r2, source, tag = args
    r1s, r2s = _s(r1), _s(r2)
    own = cov_all.class_key(r1, r2)
    aut_orig = _aut(r1s, r2s)
    base = {
        "pres_id": pres_id, "source": source, "family_tag": tag,
        "r1_orig": r1s, "r2_orig": r2s,
        "start_total_length_orig": len(r1) + len(r2),
        "aut_canon_orig": aut_orig,
    }
    tasks = [dict(base, is_control=True, class_key=list(own), r1=r1s, r2=r2s,
                  max_relator_length_cap=cov.DEFAULT_CAP, z_word=None,
                  pattern=None, r1_substituted=None, r2_substituted=None,
                  defining_relator=None, iso_gen=None, iso_index=None,
                  iso_expr=None, n_subs=0, multiplicity=None,
                  is_one_pattern=None, start_total_length_cov=len(r1) + len(r2),
                  aut_canon_cov=aut_orig)]
    fam = cov_all.subwords(r1, r2)
    one = {cov_all.class_key(o.r1, o.r2)
           for o in cov.enumerate_cov(r1, r2, family=fam)}
    for res in cov_all.enumerate_classes(r1, r2):
        o1, o2 = _s(res.r1), _s(res.r2)
        ch1, ch2 = res.meta["pattern"]
        r1sub, r2sub, r_def = res.meta["intermediate"]
        tasks.append(dict(
            base, is_control=False, class_key=list(res.meta["class_key"]),
            r1=o1, r2=o2, max_relator_length_cap=res.cap,
            z_word=_s(res.z_word),
            pattern=[[list(o) for o in ch1], [list(o) for o in ch2]],
            r1_substituted=list(r1sub), r2_substituted=list(r2sub),
            defining_relator=list(r_def),
            iso_gen=res.iso_gen, iso_index=res.iso_index,
            iso_expr=list(res.expr), n_subs=res.n_subs,
            multiplicity=res.meta["multiplicity"],
            is_one_pattern=res.meta["class_key"] in one,
            start_total_length_cov=len(res.r1) + len(res.r2),
            aut_canon_cov=_aut(o1, o2)))
    return tasks


def search_task(args):
    """Run the greedy on one task; return the finished row."""
    task, budget, path_frac = args
    t0 = time.time()
    st = run_baseline.greedy_search(
        task["r1"], task["r2"], budget,
        max_relator_length=task["max_relator_length_cap"], cyclic_reduce=True)
    row = dict(task, node_budget=budget, cyclic_reduce=True,
               solved=bool(st["solved"]), nodes_explored=int(st["nodes_explored"]),
               path_length=st["path_length"] if st["solved"] else None,
               time_seconds=round(time.time() - t0, 4))
    if st["solved"] and _sampled(task["pres_id"], tuple(task["class_key"]), path_frac):
        row["path_moves"] = list(st["path_moves"])
    return row


def _done_keys(path, ident=None):
    """Keys already written; truncates a torn final line in place.

    ``ident`` (``node_budget``/``family_tag``/``source``) must match every row
    already in the file, so a reused ``--out`` can never mix two runs.
    """
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, "rb") as f:
        data = f.read()
    good = data.rfind(b"\n") + 1
    if good != len(data):
        with open(path, "r+b") as f:
            f.truncate(good)
    for line in data[:good].splitlines():
        if line.strip():
            r = json.loads(line)
            for k, v in (ident or {}).items():
                if r.get(k) != v:
                    raise SystemExit(f"{path}: row has {k}={r.get(k)!r}, run has {v!r}")
            done.add((r["pres_id"], tuple(r["class_key"])))
    return done


def _git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="data/ms640_solved.txt")
    ap.add_argument("--source", default="ms640")
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--path-sample", type=float, default=0.0)
    ap.add_argument("--pres", default=None,
                    help="comma list of pres_ids (default: all)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--batch", type=int, default=500)
    a = ap.parse_args()
    os.chdir(find_repo_root(os.path.dirname(__file__)))

    rows = load_ms640(a.dataset)
    if a.pres:
        keep = {int(x) for x in a.pres.split(",")}
        rows = [r for r in rows if r[0] in keep]
    out = a.out or os.path.join(
        OUT_DIR, f"cov_all_{cov_all.FAMILY_TAG}_{a.source}_b{a.budget}.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = _done_keys(out, {"node_budget": a.budget,
                            "family_tag": cov_all.FAMILY_TAG, "source": a.source})
    log = os.path.splitext(out)[0] + ".log"

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
        print(line, flush=True)
        with open(log, "a") as f:
            f.write(line + "\n")

    say(f"start budget={a.budget} workers={a.workers} pres={len(rows)} "
        f"done={len(done)} path_sample={a.path_sample} commit={_git_commit()}")
    # compile the greedy once before forking, so no row's time_seconds pays it
    run_baseline.greedy_search("xy", "xY", 10, max_relator_length=24, cyclic_reduce=True)
    ctx = get_context("fork")
    t0 = time.time()
    with ctx.Pool(a.workers) as pool:
        tasks = []
        for ts in pool.imap_unordered(
                enumerate_pres,
                [(p, r1, r2, a.source, cov_all.FAMILY_TAG) for p, r1, r2 in rows],
                chunksize=1):
            tasks.extend(ts)
        n_all = len(tasks)
        n_ctrl = sum(t["is_control"] for t in tasks)
        tasks = [t for t in tasks
                 if (t["pres_id"], tuple(t["class_key"])) not in done]
        say(f"enumerated {n_all} tasks ({n_ctrl} controls, {n_all - n_ctrl} cov) "
            f"in {time.time() - t0:.1f}s; {len(tasks)} to run")
        # long starts first spreads the heavy rows across workers
        tasks.sort(key=lambda t: -(t["max_relator_length_cap"]
                                   + t["start_total_length_cov"]))
        t1, n, solved, buf = time.time(), 0, 0, []
        with open(out, "a") as f:
            for row in pool.imap_unordered(
                    search_task, [(t, a.budget, a.path_sample) for t in tasks],
                    chunksize=4):
                buf.append(json.dumps(row, separators=(",", ":")))
                n += 1
                solved += row["solved"]
                if len(buf) >= a.batch:
                    f.write("\n".join(buf) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                    buf = []
                    say(f"progress {n}/{len(tasks)} solved={solved} "
                        f"elapsed={time.time() - t1:.0f}s")
            if buf:
                f.write("\n".join(buf) + "\n")
                f.flush()
                os.fsync(f.fileno())
    say(f"done {n} rows solved={solved} search_wall={time.time() - t1:.1f}s "
        f"total_wall={time.time() - t0:.1f}s out={out}")


if __name__ == "__main__":
    main()
