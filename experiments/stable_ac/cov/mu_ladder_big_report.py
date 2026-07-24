"""Post-run report over the chunked ``mu_ladder_big`` dump (r256/b64, 124 classes).

Why this exists instead of ``mu_ladder_big.merge_chunks``: the sanctioned merge
holds every parsed orbit row in RAM to validate and concatenate them, and this
dump is 5.58M rows / 1.6 GB — an OOM on a 16 GB machine. This module runs the
SAME completeness validation as a streaming pass (all classes present, no
pres_id in two chunks, per-class orbit-row count == ``n_orbits_seen``), merges
only the 124 summary rows (small, belongs in git), and leaves the orbit chunks
where they are.

What it then measures — all of it only possible now that the ladder records
every intermediate orbit, not just the per-class floor:

1. **Seed-orbit collision scan.** Streams all 5.58M orbits against the
   canonicalized ``ms640_solved.txt`` orbits and AK(3)'s orbit. A hit is a
   stable-AC link (Prop A per hop + PROOFS.tex Thm 3), so an ms640 hit would
   certify the source class stably AC-trivial and an AK(3) hit would collapse
   it onto AK(3). Previous scans could only test the 35 floor reps.
2. **Cross-class orbit collision.** Two classes sharing one orbit anywhere in
   their ladders are stably AC-equivalent — a merge in the 124-class ledger.
   Two passes over the dump keyed on a 64-bit digest (pass 1 finds candidate
   digests, pass 2 re-reads only those and compares the exact reps), so peak
   RAM is a set of ints, never the rows.
3. Census diff against the r8/b12+b24 ladder, budget accounting (which rows
   the 4h backstop cut), rung saturation, and the z-chain template census.

Every collision is a LEAD, not a result: reps here were canonicalized by the
numba twin ``autcanon_fast``, so a hit must be re-derived through the pure
Python ``cov.py`` / ``aut_canon`` spec and replayed with ``verify_mu_ladder``
before it is written up (``results/stable_ac/theory/MU_CRITERION.md``).

Usage:
    .venv/bin/python3 -m experiments.stable_ac.cov.mu_ladder_big_report \
        --chunks-dir ~/ACSolverX-bigdata/mu_ladder_big_r256_b64
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict


def find_repo_root(start):
    d = start
    while True:
        if all(os.path.isdir(os.path.join(d, s)) for s in ("experiments", "data")):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise RuntimeError("repo root not found")
        d = up


ROOT = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.stable_ac.cov.mu_ladder_big import AK3  # noqa: E402

CLASS_CSV = os.path.join(ROOT, "data/ms_unsolved_reps/aca_124.csv")
MS640 = os.path.join(ROOT, "data/ms640_solved.txt")
OUT_DIR = os.path.join(ROOT, "results/stable_ac/mu_scan")
PRIOR_LADDERS = [
    os.path.join(OUT_DIR, "mu_ladder_aca124_r8_b12_mrl24.jsonl"),
    os.path.join(OUT_DIR, "mu_ladder_aca124_r8_b24_mrl24.jsonl"),
    os.path.join(OUT_DIR, "mu_ladder_mu_floors_r8_r10_b32_mrl24.jsonl"),
]
LOW_MU = 15   # the shell dumped verbatim: every orbit this short, any class
LETTER = {1: "x", -1: "X", 2: "y", -2: "Y"}


def digest(rep):
    """64-bit key for a canonical orbit rep. Pass 2 re-compares exact strings,
    so a digest collision costs a wasted candidate, never a false merge."""
    raw = (rep[0] + "\x00" + rep[1]).encode()
    return int.from_bytes(hashlib.blake2b(raw, digest_size=8).digest(), "big")


def load_summaries(chunk_dir):
    """{pres_id: row} plus the validation merge_chunks does, streaming."""
    paths = sorted(p for p in glob.glob(os.path.join(chunk_dir, "*.jsonl"))
                   if not p.endswith("_orbits.jsonl"))
    by_pid, owner = {}, {}
    for p in paths:
        for ln in open(p):
            if not ln.strip():
                continue
            row = json.loads(ln)
            pid = row["pres_id"]
            if pid in owner and owner[pid] != p:
                raise RuntimeError(f"{pid} appears in {owner[pid]} and {p}")
            owner[pid] = p
            by_pid[pid] = row
    with open(CLASS_CSV) as f:
        order = [r["name"] for r in csv.DictReader(f)]
    missing = [n for n in order if n not in by_pid]
    if missing:
        raise RuntimeError(f"{len(missing)} classes missing: {missing[:5]}")
    extra = set(by_pid) - set(order)
    if extra:
        raise RuntimeError(f"rows not in the CSV: {sorted(extra)[:5]}")
    return order, by_pid, len(paths)


def orbit_paths(chunk_dir):
    return sorted(glob.glob(os.path.join(chunk_dir, "*_orbits.jsonl")))


def stream_orbits(chunk_dir):
    for p in orbit_paths(chunk_dir):
        for ln in open(p):
            if ln.strip():
                yield json.loads(ln)


def ms640_orbits():
    """{orbit rep -> [line indices]} over data/ms640_solved.txt, canonicalized
    with the pure-Python spec (the ladder's numba twin is result-identical and
    test-pinned, so these keys are comparable to the dump's)."""
    orbits = defaultdict(list)
    with open(MS640) as f:
        for i, ln in enumerate(f):
            ints = [int(v) for v in ln.replace(",", " ").replace("[", " ")
                    .replace("]", " ").split()]
            half = len(ints) // 2
            r1 = "".join(LETTER[v] for v in ints[:half] if v)
            r2 = "".join(LETTER[v] for v in ints[half:] if v)
            orbits[tuple(aut_canon((r1, r2))[1])].append(i)
    return orbits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks-dir", required=True)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--tag", default="mu_ladder_big_aca124_r256_b64_mrl24")
    args = ap.parse_args()
    chunk_dir = os.path.expanduser(args.chunks_dir)

    order, by_pid, n_chunks = load_summaries(chunk_dir)
    print(f"summaries: {len(by_pid)} classes over {n_chunks} chunk files")

    # ---- pass 1: validate row counts, seed hits, candidate duplicate digests
    seeds = ms640_orbits()
    ak3_rep = tuple(aut_canon(AK3)[1])
    class_reps = {tuple(aut_canon((r["r1_orig"], r["r2_orig"]))[1]): pid
                  for pid, r in by_pid.items()}
    print(f"seed orbits: {len(seeds)} distinct over 640 solved rows; "
          f"AK(3) rep {ak3_rep}; {len(class_reps)} distinct class-rep orbits")
    seed_keys = {digest(k): k for k in seeds}
    ak3_key = digest(ak3_rep)

    mu_in = {pid: r["mu_in"] for pid, r in by_pid.items()}
    counts = Counter()
    seen, dup = set(), set()
    seed_hits, ak3_hits, low_shell = [], [], []
    mu_hist, below_start, low_by_class = Counter(), Counter(), defaultdict(Counter)
    for o in stream_orbits(chunk_dir):
        pid, rep = o["pres_id"], tuple(o["rep"])
        counts[pid] += 1
        mu_hist[o["mu"]] += 1
        if o["mu"] < mu_in[pid]:
            below_start[pid] += 1
        if o["mu"] <= mu_in[pid]:
            low_by_class[pid][o["mu"]] += 1
        if o["mu"] <= LOW_MU:
            low_shell.append({"mu": o["mu"], "pres_id": pid,
                              "rung": o["rung"], "rep": list(rep)})
        d = digest(rep)
        if d in seen:
            dup.add(d)
        else:
            seen.add(d)
        if d == ak3_key and rep == ak3_rep:
            ak3_hits.append((pid, o["rung"]))
        elif d in seed_keys and rep == seed_keys[d]:
            seed_hits.append((pid, o["rung"], list(rep)))
    bad = [(pid, counts.get(pid, 0), by_pid[pid]["n_orbits_seen"])
           for pid in order if counts.get(pid, 0) != by_pid[pid]["n_orbits_seen"]]
    if bad:
        raise RuntimeError(f"orbit-row count mismatch: {bad[:5]}")
    total = sum(counts.values())
    print(f"orbit rows: {total} validated against n_orbits_seen; "
          f"{len(seen)} distinct orbits, {len(dup)} shared by >1 class")

    # ---- pass 2: exact reps behind the duplicate digests
    shared = defaultdict(list)
    if dup:
        for o in stream_orbits(chunk_dir):
            if digest(tuple(o["rep"])) in dup:
                shared[tuple(o["rep"])].append((o["pres_id"], o["rung"], o["mu"]))
    merges = {rep: hits for rep, hits in shared.items()
              if len({h[0] for h in hits}) > 1}

    # ---- census / budget / template accounting
    prior = {}
    for p in PRIOR_LADDERS:
        if not os.path.exists(p):
            continue
        for ln in open(p):
            if not ln.strip():
                continue
            r = json.loads(ln)
            pid = r["pres_id"]
            if pid not in prior or r["best_mu"] < prior[pid]:
                prior[pid] = r["best_mu"]

    rows = [by_pid[pid] for pid in order]
    desc = [r for r in rows if r["best_mu"] < r["mu_in"]]
    # the rung at which each descender first touched its final floor: the only
    # honest measure of how deep the ladder had to go to buy what it bought
    first_hit = {r["pres_id"]: next(k["rung"] for k in r["rungs"]
                                    if k["best"] == r["best_mu"]) for r in desc}
    wasted = [(len(r["rungs"]) - first_hit[r["pres_id"]]) / max(len(r["rungs"]), 1)
              for r in desc]
    new_desc = [r["pres_id"] for r in desc
                if prior.get(r["pres_id"], r["mu_in"]) >= r["mu_in"]]
    regress = [(r["pres_id"], prior[r["pres_id"]], r["best_mu"]) for r in rows
               if r["pres_id"] in prior and r["best_mu"] > prior[r["pres_id"]]]
    improved = [(r["pres_id"], prior[r["pres_id"]], r["best_mu"]) for r in rows
                if r["pres_id"] in prior and r["best_mu"] < prior[r["pres_id"]]]

    report = {
        "tag": args.tag,
        "chunks_dir": chunk_dir,
        "cfg": rows[0]["cfg"],
        "git_commit": rows[0]["git_commit"],
        "n_classes": len(rows),
        "orbit_rows": total,
        "distinct_orbits": len(seen),
        "orbits_shared_across_classes": len(merges),
        "cross_class_merges": [
            {"rep": list(rep), "hits": hits} for rep, hits in
            sorted(merges.items(), key=lambda kv: kv[0])[:200]],
        "ms640_hits": seed_hits,
        "ak3_orbit_hits": ak3_hits,
        "ak3_orbit_rep": list(ak3_rep),
        "n_seed_orbits": len(seeds),
        "descenders": [r["pres_id"] for r in desc],
        "n_descenders": len(desc),
        "floor_first_hit_rung": first_hit,
        "max_floor_first_hit_rung": max(first_hit.values()),
        "mean_rung_fraction_after_last_gain": round(sum(wasted) / len(wasted), 4),
        "below_start_orbits": dict(below_start.most_common()),
        "below_start_total": sum(below_start.values()),
        "low_mu_shell": sorted(low_shell, key=lambda d: (d["mu"], d["pres_id"])),
        "shell_at_or_below_start": {p: dict(sorted(c.items()))
                                    for p, c in sorted(low_by_class.items())},
        "min_best_mu": min(r["best_mu"] for r in rows),
        "best_mu_hist": dict(sorted(Counter(r["best_mu"] for r in rows).items())),
        "orbit_mu_hist": dict(sorted(mu_hist.items())),
        "hits_stop": sum(r["hits_stop"] for r in rows),
        "timed_out": [r["pres_id"] for r in rows if r["timed_out"]],
        "orbit_capped": [r["pres_id"] for r in rows if r["orbit_capped"]],
        "rungs_completed_lt_max": {r["pres_id"]: len(r["rungs"]) for r in rows
                                   if len(r["rungs"]) < r["cfg"]["rungs"]},
        "prior_vs_now": {"new_descenders": new_desc,
                         "improved_floor": improved,
                         "regressed_floor": regress},
        "chain_templates": dict(Counter(
            " + ".join(r["best_chain"]) for r in desc).most_common()),
        "elapsed_h_total": round(sum(r["elapsed_s"] for r in rows) / 3600, 1),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    merged = os.path.join(args.out_dir, args.tag + ".jsonl")
    with open(merged, "w") as f:
        for pid in order:
            f.write(json.dumps(by_pid[pid]) + "\n")
    rep_path = os.path.join(args.out_dir, args.tag + "_report.json")
    with open(rep_path, "w") as f:
        json.dump(report, f, indent=1)
    print(f"wrote {merged}\nwrote {rep_path}")
    print(f"descenders {len(desc)}/{len(rows)}  min floor {report['min_best_mu']}  "
          f"hits_stop {report['hits_stop']}  timed_out {len(report['timed_out'])}")
    print(f"ms640 hits {len(seed_hits)}  AK(3)-orbit hits {ak3_hits}  "
          f"cross-class shared orbits {len(merges)}")
    print(f"every floor first touched by rung {report['max_floor_first_hit_rung']}; "
          f"{100 * report['mean_rung_fraction_after_last_gain']:.1f}% of rungs ran "
          f"after the last gain; below-start orbits "
          f"{report['below_start_total']}/{total} "
          f"({100 * report['below_start_total'] / total:.4f}%)")


if __name__ == "__main__":
    main()
