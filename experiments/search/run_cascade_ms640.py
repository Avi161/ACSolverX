"""Run the certified cascade on MS-640 and compare saved greedy costs."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time

import numba

from experiments.search.cascade_heuristics import search
from experiments.search.frontier_heuristics import verify
from experiments.search.time_cascade import verify_second


ROOT = Path(__file__).resolve().parents[2]
GREEDY_COMMIT = "525050dd9ed9b9e1ee06cde2d739ad05940c8172"
GREEDY_OBJECT = (
    "results/greedy_baseline/"
    "greedy_1000000_640_mrl24_cyc_all_07_11_26.jsonl"
)
SYMBOL = {1: "x", -1: "X", 2: "y", -2: "Y"}


def load_inputs():
    lines = [ast.literal_eval(line) for line in
             (ROOT / "data/ms640_solved.txt").read_text().splitlines() if line.strip()]
    if len(lines) != 640 or any(len(row) != 48 for row in lines):
        raise ValueError("expected 640 rows of 48 integers")
    pairs = []
    for row in lines:
        words = tuple("".join(SYMBOL[n] for n in half if n) for half in (row[:24], row[24:]))
        pairs.append(words)
    return pairs


def load_saved_greedy():
    raw = subprocess.run(
        ["git", "show", f"{GREEDY_COMMIT}:{GREEDY_OBJECT}"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    ).stdout
    records = [json.loads(line) for line in raw.splitlines()]
    rows = {int(row["pres_id"]): row for row in records}
    if len(records) != len(rows) or len(rows) != 640:
        raise ValueError("saved greedy run does not have 640 unique rows")
    if not all(row["solved"] and row["node_budget"] == 1_000_000
               and row["max_relator_length_cap"] == 24 and row["cyclic_reduce"]
               for row in rows.values()):
        raise ValueError("saved greedy run has unexpected settings or failures")
    return rows, hashlib.sha256(raw.encode()).hexdigest()


def describe(values):
    return dict(total=sum(values), mean=statistics.mean(values),
                median=statistics.median(values), minimum=min(values), maximum=max(values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=640)
    parser.add_argument("--budget", type=int, default=1000)
    parser.add_argument("--cooldown-every", type=int, default=50)
    parser.add_argument("--cooldown-seconds", type=float, default=0.25)
    args = parser.parse_args()
    if not 1 <= args.limit <= 640:
        raise ValueError("limit must be in 1..640")
    if args.out.exists():
        raise ValueError("use a fresh output directory")
    args.out.mkdir(parents=True)

    inputs = load_inputs()
    greedy, greedy_sha = load_saved_greedy()
    for i, pair in enumerate(inputs):
        row = greedy[i]
        if pair != (row["r1"], row["r2"]):
            raise AssertionError(f"input mismatch at pres_id {i}")
    input_file = ROOT / "data/ms640_solved.txt"
    source_files = [Path(__file__), ROOT / "experiments/search/cascade_heuristics.py",
                    ROOT / "experiments/search/bs_collapse.py",
                    ROOT / "experiments/search/basis_moves.py",
                    ROOT / "experiments/search/heuristic_1k.py"]
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in source_files}
    hashes[str(input_file.relative_to(ROOT))] = hashlib.sha256(input_file.read_bytes()).hexdigest()

    numba.set_num_threads(1)
    warmup_start = time.perf_counter()
    search(("YYXyx", "Yx"), budget=20)
    warmup_seconds = time.perf_counter() - warmup_start
    manifest = dict(
        rows=args.limit, budget=args.budget, threads=1,
        ordinary_search_cap=48, rewrite_intermediate_cap=256,
        greedy_source=dict(commit=GREEDY_COMMIT, object=GREEDY_OBJECT,
                           sha256=greedy_sha, budget=1_000_000, cap=24),
        search_timing="perf_counter/process_time around cascade search only",
        excluded_from_search_timing="warmup, verification, serialization, progress output, cooldown",
        cooldown=dict(every=args.cooldown_every, seconds=args.cooldown_seconds),
        warmup_seconds=warmup_seconds, platform=platform.platform(), source_sha256=hashes,
    )
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    records = []
    batch_start = time.perf_counter()
    for pres_id, pair in enumerate(inputs[:args.limit]):
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        result = search(pair, budget=args.budget)
        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start
        if result["solved"]:
            if not verify(pair, result) or not verify_second(pair, result):
                raise AssertionError(f"certificate verification failed for {pres_id}")
        saved = greedy[pres_id]
        record = dict(
            pres_id=pres_id, r1=pair[0], r2=pair[1], solved=result["solved"],
            charged_nodes=result["nodes_explored"],
            path_length=len(result["steps"]) if result["solved"] else None,
            winner=result["winner"], wall_seconds=wall_seconds, cpu_seconds=cpu_seconds,
            max_certificate_relator_length=result["max_certificate_relator_length"],
            certificate_verified=True if result["solved"] else None,
            second_decoder_verified=True if result["solved"] else None,
            greedy_nodes=int(saved["nodes_explored"]),
            greedy_path_length=int(saved["path_length"]),
            greedy_historical_time_seconds=float(saved["time_seconds"]),
            attempts=result["attempts"], states=result["states"], steps=result["steps"],
        )
        records.append(record)
        with (args.out / "runs.jsonl").open("a") as stream:
            stream.write(json.dumps(record) + "\n")
        if (pres_id + 1) % 50 == 0 or pres_id + 1 == args.limit:
            print(json.dumps(dict(rows=pres_id + 1,
                                  solved=sum(r["solved"] for r in records),
                                  search_wall_seconds=sum(r["wall_seconds"] for r in records))),
                  flush=True)
        if args.cooldown_every and (pres_id + 1) % args.cooldown_every == 0:
            time.sleep(args.cooldown_seconds)

    solved = [r for r in records if r["solved"]]
    summary = dict(
        rows=args.limit, solved=len(solved), failed=args.limit - len(solved),
        hybrid=dict(
            charged_nodes=describe([r["charged_nodes"] for r in records]),
            path_length=describe([r["path_length"] for r in solved]) if solved else None,
            search_wall_seconds=sum(r["wall_seconds"] for r in records),
            search_cpu_seconds=sum(r["cpu_seconds"] for r in records),
            winners={name: sum(r["winner"] == name for r in records)
                     for name in ("terminal", "rewrite", "s40_gen", "s20_mk2", None)},
        ),
        saved_greedy=dict(
            solved=args.limit,
            nodes=describe([int(greedy[i]["nodes_explored"]) for i in range(args.limit)]),
            path_length=describe([int(greedy[i]["path_length"]) for i in range(args.limit)]),
            historical_time_seconds=describe(
                [float(greedy[i]["time_seconds"]) for i in range(args.limit)]),
            timing_comparability="historical run; not same-machine matched timing",
        ),
        batch_elapsed_including_verification_output_and_cooldown_seconds=time.perf_counter() - batch_start,
    )
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
