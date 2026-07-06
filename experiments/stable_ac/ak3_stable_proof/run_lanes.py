"""Colab driver for the AK(3) stable-proof lanes. One box per Colab runtime:

  D1  Lane D at scale, textbook form   (harvest 500k, solve top 12000 @50k)
  D2  Lane D at scale, rep form        (same)
  D3  Lane D, FULL ~95-word bank, both forms (harvest 200k, solve top 10000 @25k)
  B   StableSolver grid @800k (hero8 g3/g4, gen_penalty 1/2) + full bank @300k
  C   dumb baselines n=3/4/5 @0.8-2M + MITM outward AK3/P25 @2M with ball dumps

Usage (see nb_ak3_lanes.ipynb):
  python run_lanes.py --box D1 --out_dir /content/drive/MyDrive/ak3_stable_proof/D1
  --quick   divides budgets ~100x for a 2-minute end-to-end base-case first.

All boxes stream resumable JSONL into out_dir; re-running skips finished work.
Lane D certs land in out_dir/certs. Memory sized for a 50 GB Colab CPU runtime.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

LEAVES = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof", "catalog",
                      "catalog_leaves.jsonl")


def bank_word_names():
    import ak3_words as aw
    return [e["name"] for e in aw.build_word_bank()]


def _total_ram_gb():
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9
    except (ValueError, OSError, AttributeError):
        return 16.0


def auto_workers(budget):
    """Harvest is CPU-bound and each worker's peak is dominated by its visited set
    (~40x budget entries, ~200 B each ⇒ ~1.6 GB @200k, ~4 GB @500k). Use every core the
    box has, capped so the concurrent workers fit ~85% of RAM. The old hardcoded 4 left
    most of a 50 GB / many-core Colab box idle (the run was using ~4 GB)."""
    cores = os.cpu_count() or 4
    per_worker_gb = max(0.5, budget * 8e-6)
    ram_cap = max(1, int(0.85 * _total_ram_gb() / per_worker_gb))
    return max(1, min(cores, ram_cap))


def lane_d(box, out_dir, quick, workers):
    env = dict(os.environ)
    env["ACX_LANED_DIR"] = os.path.join(out_dir, "laneD")
    env["ACX_CERTS_DIR"] = os.path.join(out_dir, "certs")
    os.makedirs(env["ACX_LANED_DIR"], exist_ok=True)
    if box == "D1":
        cfg = dict(forms="textbook,p25", words=None, budget=500_000, budget2=50_000,
                   top=12_000, tl_cap=20, l_cap=24)
    elif box == "D2":
        cfg = dict(forms="rep,floorF", words=None, budget=500_000, budget2=50_000,
                   top=12_000, tl_cap=20, l_cap=24)
    else:  # D3
        cfg = dict(forms="textbook,rep", words=",".join(bank_word_names()),
                   budget=200_000, budget2=25_000, top=10_000, tl_cap=20, l_cap=24)
    if quick:
        cfg.update(budget=4_000, budget2=2_000, top=60)
        if box == "D3":
            cfg["words"] = ",".join(bank_word_names()[:3])
    hw = workers or auto_workers(cfg["budget"])          # harvest: RAM-bounded, memory-heavy
    sw = workers or (os.cpu_count() or 8)                 # solve: light per candidate
    print(f"box {box}: harvest_workers={hw} solve_workers={sw} "
          f"(cores={os.cpu_count()}, ram={_total_ram_gb():.0f} GB, budget={cfg['budget']})",
          flush=True)
    cmd = [sys.executable, os.path.join(HERE, "plateau_elim.py"), "--phase", "all",
           "--forms", cfg["forms"], "--budget", str(cfg["budget"]),
           "--budget2", str(cfg["budget2"]), "--top", str(cfg["top"]),
           "--tl_cap", str(cfg["tl_cap"]), "--l_cap", str(cfg["l_cap"]),
           "--harvest_tl_cap", str(cfg["tl_cap"]),        # solve ignores > tl_cap; don't harvest them
           "--workers", str(hw), "--solve_workers", str(sw)]
    if cfg["words"]:
        cmd += ["--words", cfg["words"]]
    print(" ".join(cmd), flush=True)
    subprocess.run(cmd, env=env, check=True)


GRID_B = [
    ("laneB", "AK3", 800_000, 24, 3, "hero8", 2),
    ("laneB", "P25", 800_000, 24, 3, "hero8", 2),
    ("laneB", "AK3", 800_000, 24, 4, "hero8", 2),
    ("laneB", "AK3", 800_000, 24, 3, "hero8", 1),
    ("laneB", "AK3", 300_000, 24, 3, "full", 2),
    ("laneB", "P25", 300_000, 24, 3, "full", 2),
]


def grid_c(out_dir):
    dumps = os.path.join(out_dir, "balls")
    os.makedirs(dumps, exist_ok=True)
    return [
        ("laneC", "textbook", 3, 2_000_000),
        ("laneC", "rep", 3, 1_500_000),
        ("laneC", "textbook", 4, 1_500_000),
        ("laneC", "rep", 4, 1_000_000),
        ("laneC", "textbook", 5, 1_000_000),
        ("laneC", "rep", 5, 800_000),
        ("mitm_out", "AK3", 2_000_000, 24, LEAVES,
         os.path.join(dumps, "ball_AK3_2M.gz")),
        ("mitm_out", "P25", 2_000_000, 24, LEAVES,
         os.path.join(dumps, "ball_P25_2M.gz")),
    ]


def probe_id(t):
    if t[0] == "laneB":
        return f"laneB_{t[1]}_{t[5]}_g{t[4]}_p{t[6]}@{t[2]}"
    if t[0] == "laneC":
        return f"laneC_{t[1]}_n{t[2]}@{t[3]}"
    return f"{t[0]}_{t[1]}@{t[2]}"


def shrink(t, factor=100):
    t = list(t)
    if t[0] == "laneB":
        t[2] = max(2_000, t[2] // factor)
    elif t[0] == "laneC":
        t[3] = max(2_000, t[3] // factor)
    else:
        t[2] = max(2_000, t[2] // factor)
    return tuple(t)


def probe_indexed(it):
    from lane_worker import probe
    i, t = it
    return i, probe(t)


def lane_grid(box, out_dir, quick, workers):
    from multiprocessing import Pool
    tasks = GRID_B if box == "B" else grid_c(out_dir)
    if quick:
        tasks = [shrink(t) for t in tasks]
    out = os.path.join(out_dir, f"box_{box}{'_quick' if quick else ''}.jsonl")
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                done.add(json.loads(line)["night_id"])
            except Exception:
                pass
    todo = [(probe_id(t), t) for t in tasks if probe_id(t) not in done]
    print(f"box {box}: {len(todo)} tasks pending ({len(done)} done)", flush=True)
    if not todo:
        return
    w = workers or 2
    indexed = list(enumerate([t for _, t in todo]))
    with Pool(processes=w, maxtasksperchild=1) as pool, open(out, "a") as f:
        for i, rec in pool.imap_unordered(probe_indexed, indexed):
            rec["night_id"] = todo[i][0]
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())
            print(json.dumps({k: rec.get(k) for k in
                              ("night_id", "solved", "nodes", "min_total_len",
                               "wall_s", "peak_rss_mb", "hit", "error")}), flush=True)
            if rec.get("solved") or rec.get("hit"):
                print(f"*** SOLVE/HIT *** {rec['night_id']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--box", required=True, choices=["D1", "D2", "D3", "B", "C"])
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    t0 = time.time()
    if args.box in ("D1", "D2", "D3"):
        lane_d(args.box, args.out_dir, args.quick, args.workers)
    else:
        lane_grid(args.box, args.out_dir, args.quick, args.workers)
    print(f"box {args.box} complete in {round(time.time() - t0)}s", flush=True)


if __name__ == "__main__":
    main()
