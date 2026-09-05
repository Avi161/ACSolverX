"""AK(3) universal-CoV sweep — can a re-coordinatisation open a door the raw
greedy provably cannot?

Base: AK(3) = ⟨x,y | xxxYYYY, xyxYXY⟩, total length 13. Benchmark facts
(results/benchmark/reach/reach_tier_1.csv): the baseline greedy from the raw
start never reaches a state with total length < 13 — at 1,000 nodes NOR at
1,000,000 — and the Aut(F₂)-minimal representative of the pair is ALSO 13, so
no chain of pure changes of variables can shorten it on its own. The open
lever is the interplay: re-coordinatise via the universal stable-AC move
(z = w(x,y); when w carries exactly one ±x [or ±y] the defining relator Z·w
isolates it — an elementary Nielsen automorphism, no occurrence needed — and
occurrence-based isolation covers the rest), then let the greedy search THAT
coordinate system's length landscape.

Stages (every search at the repo-capped 1,000-node budget):
  scan    transform-only, words 2..SCAN_MAX_LEN from AK(3): confirm no start
          beats total 13 by itself.
  control greedy on AK(3) raw and on the worked-example-C pair
          (z = xyy, x = zYY → yXXyXXyXXXXXX | yXyXYX, total 19).
  d1      greedy from every distinct depth-1 CoV start of AK(3)
          (words 2..GREEDY_MAX_LEN, both elimination targets).
  c       greedy from every depth-1 CoV start of the example-C pair — the
          w(z,y)-for-x / w(z,x)-for-y sweep, i.e. depth-2 chains through xyy.
  beam    the BEAM_K most promising presentations seen so far (ranked by min
          total reached; the shortest state reached replaces the start as the
          base when it improves on it) each get a CoV sweep of their own
          (words 2..BEAM_MAX_LEN) + greedy.

HIT = solved (a stable-AC trivialisation of AK(3) — THE result) or a state
with total length < 13 (beats what 10^6 raw-start nodes provably cannot).
Hits print immediately as '*** HIT'.

Run from the repo root:
    .venv/bin/python3 -m experiments.stable_ac.cov.ak_3_universal_test.sweep
Rows land in sweep_results.jsonl next to this file, keyed by the start pair's
canonical form (relators as unoriented cyclic words, pair unordered); a re-run
resumes by skipping starts already searched. min_pair tie-breaks follow
PYTHONHASHSEED (repo rule) — launch with PYTHONHASHSEED=0 so the beam-base
selection is reproducible across resumes.
"""

import argparse
import json
import os
import time

from experiments import run_baseline
from experiments.greedy_tests.spec.words import (
    canonical_word,
    reduce_word,
    str_to_word,
    word_to_str,
)
from experiments.stable_ac.cov import cov

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "sweep_results.jsonl")

AK3 = ("xxxYYYY", "xyxYXY")     # benchmark row order; total length 13
# Second Aut(F2)-orbit at the length-13 floor, found by this sweep (analyze.py):
# stably-AC-equivalent to AK(3), NOT a change of variables of it. As relations:
# yx = x²y², xy = y³x².
ORBIT2 = ("YYXXyx", "YYYxyXX")
BAR = 13                        # bar_to_beat: min total < 13 (reach_tier_1)
BUDGET = 1000                   # repo hard cap for local searches — never raise
GREEDY_MAX_LEN = 6              # universe z words 2..this get a greedy run
SCAN_MAX_LEN = 7                # transform-only scan goes one letter deeper
BEAM_K = 10
BEAM_MAX_LEN = 5

assert BUDGET <= 1000, "local node budget is hard-capped at 1000 (repo rule)"


def canon_key(r1s, r2s):
    """Start identity: relators as unoriented cyclic words, pair unordered."""
    ws = sorted(
        word_to_str(canonical_word(reduce_word(str_to_word(s), cyclic=True)))
        for s in (r1s, r2s))
    return "|".join(ws)


def example_c():
    res = cov.apply_cov_once(
        str_to_word(AK3[0]), str_to_word(AK3[1]), str_to_word("xyy"),
        allow_defining_iso=True, iso_gen="x")
    return word_to_str(res.r1), word_to_str(res.r2)


def cov_starts(base, max_len):
    """Every universal CoV of one base pair: (z_str, iso_gen, CoVResult)."""
    r1, r2 = str_to_word(base[0]), str_to_word(base[1])
    for z in cov.universe_candidates(2, max_len):
        for target in ("x", "y"):
            res = cov.apply_cov_once(r1, r2, z, allow_defining_iso=True,
                                     iso_gen=target)
            if res is not None:
                yield word_to_str(z), target, res


def _search(r1, r2, cap):
    stats = run_baseline.greedy_search(r1, r2, BUDGET, max_relator_length=cap,
                                       cyclic_reduce=True, high_speedup=True)
    if stats["solved"]:
        # fast solver carries no path — re-solve slow for the certificate
        stats = run_baseline.greedy_search(r1, r2, BUDGET,
                                           max_relator_length=cap,
                                           cyclic_reduce=True,
                                           high_speedup=False)
    return stats


def run_one(out_f, seen, stage, base_name, base, z, target, info, r1t, r2t):
    key = canon_key(r1t, r2t)
    if key in seen:
        return None
    seen.add(key)
    t0 = time.perf_counter()
    stats = _search(r1t, r2t, info["cap"])
    elapsed = time.perf_counter() - t0
    row = {
        "stage": stage, "base_name": base_name,
        "base_r1": base[0], "base_r2": base[1],
        "z_word": z, "iso_gen": target,
        "iso_index": info.get("iso_index"),
        "n_subs": info.get("n_subs", 0),
        "r1": r1t, "r2": r2t,
        "start_total": len(r1t) + len(r2t),
        "cap": info["cap"], "node_budget": BUDGET, "canon": key,
        "solved": stats["solved"],
        "nodes_explored": stats["nodes_explored"],
        "min_total": stats["min_relator_length"],
        "min_pair": stats["min_relator"],
        "max_total": stats["max_relator_length"],
        "path_length": stats["path_length"],
        "time_seconds": round(elapsed, 4),
    }
    if stats["solved"]:
        row["path_moves"] = stats["path_moves"]
    out_f.write(json.dumps(row) + "\n")
    out_f.flush()
    os.fsync(out_f.fileno())
    if stats["solved"] or stats["min_relator_length"] < BAR:
        print(f"*** HIT [{stage}] base={base_name} z={z} iso={target} "
              f"start={r1t}|{r2t} ({row['start_total']}) "
              f"solved={stats['solved']} "
              f"min_total={stats['min_relator_length']} "
              f"min_pair={stats['min_relator']}", flush=True)
    return row


def control_row(out_f, seen, name, pair):
    r1, r2 = pair
    cap = max(cov.DEFAULT_CAP, max(len(r1), len(r2)) + cov.CAP_HEADROOM)
    row = run_one(out_f, seen, "control", name, pair, None, None,
                  {"cap": cap, "iso_index": None, "n_subs": 0}, r1, r2)
    if row is not None:
        print(f"[control] {name}: solved={row['solved']} "
              f"min_total={row['min_total']} nodes={row['nodes_explored']} "
              f"({row['time_seconds']}s)", flush=True)
    return row


def sweep(out_f, seen, stage, base_name, base, max_len):
    rows, n_starts, n_skip = [], 0, 0
    t0 = time.perf_counter()
    for z, target, res in cov_starts(base, max_len):
        n_starts += 1
        r1t, r2t = word_to_str(res.r1), word_to_str(res.r2)
        row = run_one(out_f, seen, stage, base_name, base, z, target,
                      {"cap": res.cap, "iso_index": res.iso_index,
                       "n_subs": res.n_subs}, r1t, r2t)
        if row is None:
            n_skip += 1
        else:
            rows.append(row)
    dt = time.perf_counter() - t0
    best = min((r["min_total"] for r in rows), default=None)
    print(f"[{stage}] base={base_name}: {n_starts} cov starts, "
          f"{len(rows)} searched, {n_skip} dup-skipped, "
          f"best min_total={best}, {dt:.1f}s", flush=True)
    return rows


def scan(base, max_len):
    best, best_info, n = None, None, 0
    for z, target, res in cov_starts(base, max_len):
        n += 1
        tot = len(res.r1) + len(res.r2)
        if best is None or tot < best:
            best = tot
            best_info = (z, target, word_to_str(res.r1), word_to_str(res.r2))
    print(f"[scan] {n} universal CoV starts from {base[0]}|{base[1]} "
          f"(words 2..{max_len}); shortest start total={best} via "
          f"z={best_info[0]} iso={best_info[1]} -> "
          f"{best_info[2]}|{best_info[3]}", flush=True)
    if best is not None and best < BAR:
        print(f"*** HIT [scan] pure CoV start below {BAR}: {best_info}",
              flush=True)
    return best


def load_rows():
    rows = []
    if not os.path.exists(OUT_PATH):
        return rows
    with open(OUT_PATH) as f:
        lines = f.read().splitlines()
    for i, ln in enumerate(lines):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except ValueError:
            if i == len(lines) - 1:
                continue    # torn final line; _repair_jsonl truncates it
            raise
    return rows


def pick_beam(rows, skip_keys, k, stages=("control", "d1", "c")):
    """Most promising presentations from the given stages, one per canon key.

    Base = the shortest state the search reached when that improves on the
    start, else the start itself — sweeping the min state is the case-(ii)
    flavour: CoV applied mid-descent rather than at the root.
    """
    cands = {}
    for r in rows:
        if r["stage"] not in stages:
            continue
        if r["min_total"] < r["start_total"]:
            b = (r["min_pair"][0], r["min_pair"][1])
        else:
            b = (r["r1"], r["r2"])
        if not b[0] or not b[1]:
            continue
        bkey = canon_key(*b)
        if bkey in skip_keys:
            continue
        score = (r["min_total"], r["start_total"], r["r1"], r["r2"])
        if bkey not in cands or score < cands[bkey][0]:
            cands[bkey] = (score, b)
    ranked = sorted(cands.items(), key=lambda kv: kv[1][0])[:k]
    return [(bkey, b) for bkey, (_, b) in ranked]


def main():
    ap = argparse.ArgumentParser(
        description="AK(3) universal-CoV sweep (1000-node greedy per start)")
    ap.add_argument("--stages", default="scan,control,d1,c,beam")
    ap.add_argument("--greedy-max-len", type=int, default=GREEDY_MAX_LEN)
    ap.add_argument("--scan-max-len", type=int, default=SCAN_MAX_LEN)
    ap.add_argument("--beam-k", type=int, default=BEAM_K)
    ap.add_argument("--beam-max-len", type=int, default=BEAM_MAX_LEN)
    args = ap.parse_args()
    stages = set(args.stages.split(","))

    c_pair = example_c()
    print(f"AK(3) = {AK3[0]}|{AK3[1]} (13); example C pair = "
          f"{c_pair[0]}|{c_pair[1]} ({len(c_pair[0]) + len(c_pair[1])})",
          flush=True)

    run_baseline._repair_jsonl(OUT_PATH)
    prior = load_rows()
    seen = {r["canon"] for r in prior}
    prior_hits = [r for r in prior if r["solved"] or r["min_total"] < BAR]
    print(f"resume: {len(prior)} rows already done, "
          f"{len(prior_hits)} prior hits", flush=True)

    with open(OUT_PATH, "a") as out_f:
        if "scan" in stages:
            scan(AK3, args.scan_max_len)
        if "control" in stages:
            control_row(out_f, seen, "AK3-raw", AK3)
            control_row(out_f, seen, "exampleC-xyy", c_pair)
        if "d1" in stages:
            sweep(out_f, seen, "d1", "AK3-raw", AK3, args.greedy_max_len)
        if "c" in stages:
            sweep(out_f, seen, "c", "exampleC-xyy", c_pair,
                  args.greedy_max_len)
        if "beam" in stages:
            rows = load_rows()
            skip = {canon_key(*AK3), canon_key(*c_pair)}
            beams = pick_beam(rows, skip, args.beam_k)
            print(f"[beam] {len(beams)} bases picked", flush=True)
            for _, b in beams:
                sweep(out_f, seen, "beam", f"beam:{b[0]}|{b[1]}", b,
                      args.beam_max_len)
        if "o2" in stages:
            control_row(out_f, seen, "orbit2-rep", ORBIT2)
            sweep(out_f, seen, "o2", "orbit2-rep", ORBIT2,
                  args.greedy_max_len)
        if "o2beam" in stages:
            rows = load_rows()
            skip = {canon_key(*AK3), canon_key(*c_pair), canon_key(*ORBIT2)}
            beams = pick_beam(rows, skip, args.beam_k, stages=("o2",))
            print(f"[o2beam] {len(beams)} bases picked", flush=True)
            for _, b in beams:
                sweep(out_f, seen, "o2beam", f"o2beam:{b[0]}|{b[1]}", b,
                      args.beam_max_len)

    rows = load_rows()
    hits = [r for r in rows if r["solved"] or r["min_total"] < BAR]
    print("\n=== SUMMARY ===", flush=True)
    print(f"{len(rows)} searches at budget {BUDGET}; "
          f"hits (solved or min_total < {BAR}): {len(hits)}", flush=True)
    for r in sorted(rows, key=lambda r: (r["min_total"],
                                         r["start_total"]))[:15]:
        print(f"  min_total={r['min_total']:>3} start={r['start_total']:>3} "
              f"[{r['stage']}] z={r['z_word']} iso={r['iso_gen']} "
              f"base={r['base_name']}", flush=True)


if __name__ == "__main__":
    main()
