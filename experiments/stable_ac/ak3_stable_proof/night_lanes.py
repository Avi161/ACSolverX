"""Overnight sequential lane runner (16 GB local box).

Waits for the Lane D pipeline (plateau_elim.py) to exit, then runs, one subprocess at
a time (fresh forked child per item, so each run's peak RSS is released):
  1. Lane D escalation: re-solve the shortest merged candidates at a 200k budget
  2. Lane B grid: StableSolver AK3/P25 at 300k (hero8 g3/g4) and 100k (full bank)
  3. Lane C grid: trivial-z stabilization baselines n=3/4/5 at 0.4-1M
  4. Lane B escalation: AK3/P25 hero8 at 500k (~12 GB each — run last, alone)

Everything streams to results/stable_ac/ak3_stable_proof/runs/night_lanes.jsonl
(append+flush+fsync, resume by id). Safe to re-run; finished ids are skipped.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

RUNS = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof", "runs")
OUT = os.path.join(RUNS, "night_lanes.jsonl")
PY = os.path.join(ROOT, ".venv", "bin", "python3")

LANE_B = [
    ("laneB", "AK3", 300_000, 24, 3, "hero8", 2),
    ("laneB", "P25", 300_000, 24, 3, "hero8", 2),
    ("laneB", "AK3", 300_000, 24, 4, "hero8", 2),
    ("laneB", "AK3", 300_000, 24, 3, "hero8", 1),
    ("laneB", "AK3", 100_000, 24, 3, "full", 2),
    ("laneB", "P25", 100_000, 24, 3, "full", 2),
]
LANE_C = [
    ("laneC", "textbook", 3, 1_000_000),
    ("laneC", "rep", 3, 700_000),
    ("laneC", "textbook", 4, 700_000),
    ("laneC", "rep", 4, 500_000),
    ("laneC", "textbook", 5, 500_000),
    ("laneC", "rep", 5, 400_000),
]
LANE_B_BIG = [
    ("laneB", "AK3", 500_000, 24, 3, "hero8", 2),
    ("laneB", "P25", 500_000, 24, 3, "hero8", 2),
]


def wait_for_no_process(pattern, poll_s=60):
    while True:
        r = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
        pids = [p for p in r.stdout.split() if p and int(p) != os.getpid()]
        if not pids:
            return
        print(f"waiting: {pattern} still running ({len(pids)} procs)", flush=True)
        time.sleep(poll_s)


def task_id(t):
    if t[0] == "laneB":
        return f"laneB_{t[1]}_{t[5]}_g{t[4]}_p{t[6]}@{t[2]}"
    return f"laneC_{t[1]}_n{t[2]}@{t[3]}"


def done_ids():
    ids = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                ids.add(json.loads(line)["night_id"])
            except Exception:
                pass
    return ids


def run_probe_task(t):
    """One lane_worker.probe task in a fresh child (multiprocessing, fork)."""
    from multiprocessing import Pool
    from lane_worker import probe
    with Pool(processes=1, maxtasksperchild=1) as pool:
        return pool.apply(probe, (t,))


def append(rec):
    os.makedirs(RUNS, exist_ok=True)
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()
        os.fsync(f.fileno())


def main():
    print(f"night_lanes start {time.strftime('%H:%M:%S')}", flush=True)
    wait_for_no_process("plateau_elim.py")
    print("Lane D pipeline finished; starting escalation + lanes", flush=True)

    # 1. Lane D escalation (its own resume logic; skip if merged.jsonl missing)
    merged = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof",
                          "laneD", "merged.jsonl")
    esc_id = "laneD_escalation_200k_top400"
    if os.path.exists(merged) and esc_id not in done_ids():
        t0 = time.time()
        r = subprocess.run(
            [PY, os.path.join(HERE, "plateau_elim.py"), "--phase", "solve",
             "--budget2", "200000", "--top", "400", "--tl_cap", "16",
             "--solve_workers", "6"],
            capture_output=True, text=True)
        append({"night_id": esc_id, "rc": r.returncode,
                "wall_s": round(time.time() - t0, 1),
                "tail": r.stdout[-3000:] + r.stderr[-1000:]})
        print(f"laneD escalation done rc={r.returncode}", flush=True)

    # 2-4. lane_worker grids
    for t in LANE_B + LANE_C + LANE_B_BIG:
        nid = task_id(t)
        if nid in done_ids():
            print(f"skip {nid} (done)", flush=True)
            continue
        print(f"run {nid} ...", flush=True)
        try:
            rec = run_probe_task(t)
        except Exception as e:
            rec = {"error": repr(e)}
        rec["night_id"] = nid
        append(rec)
        print(f"  -> {json.dumps({k: rec.get(k) for k in ('solved', 'nodes', 'min_total_len', 'wall_s', 'peak_rss_mb', 'error')})}",
              flush=True)
        if rec.get("solved"):
            print(f"*** NIGHT SOLVE *** {nid}", flush=True)
    print(f"night_lanes done {time.strftime('%H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
