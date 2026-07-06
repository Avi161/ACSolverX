"""High-L re-solve of the shortest Lane-D candidates — probe the per-relator cap gap.

The Lane-D solve phase caps each relator at L=24 (drops any child of length ≥ 24). That is a
COMPLETENESS limit: a trivialization of some quotient E that must pass through a relator > 23
letters is pruned and never found (measured: ~18% of children pruned by the cap in a 2-gen
solve). This script re-runs plain 2-gen greedy on just the SHORTEST candidates (the only ones
where a taller hump could plausibly still descend) at a raised per-relator cap and a bigger node
budget, to test exactly that: "is there a solution that only opens up when relators may grow?"

It reads one or more Lane-D `merged.jsonl` files (D1/D2/D3), unions their candidates with
`total_len ≤ --max_tl` (dedup by `mkey`, keep shortest), and solves each at `--L` (default 40)
with `--budget` nodes. Append-only, fsync'd, resumable JSONL under `--out_dir`. On ANY solve it
loudly flags it and best-effort rebuilds+verifies the full stabilize→subst→eliminate→trivial
certificate (the substitution-path re-run is done at L=24 for fidelity to how `src` was found;
the certificate itself has no length cap, so a longer-hump 2-gen tail is still valid).

Raising the cap only makes expand_fast's numba buffers bigger (sized from gn.L at import); the
≤23 emit/canonicalize logic is byte-for-byte gold-gated already, and ≥24 children are simply
kept now instead of pruned. We set gn.L BEFORE importing expand_fast so the buffers size to --L.

Run (Colab, after D1/D2 finish; D3 optional/whatever exists):
  python3 -u experiments/stable_ac/ak3_stable_proof/resolve_hi_l.py \
    --merged /content/drive/MyDrive/ak3_stable_proof/{D1,D2,D3}/laneD/merged.jsonl \
    --max_tl 16 --L 40 --budget 300000 \
    --out_dir /content/drive/MyDrive/ak3_stable_proof/resolve_hiL
  # --quick runs a ~1-minute self-test + base case first (do this once before the real run).
"""
import argparse
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402
import greedy_nrel as gn  # noqa: E402
# gn.L is raised in main() BEFORE the first solve() (which lazily imports expand_fast), so the
# njit buffers size to the raised cap. Keep the original for the L=24 certificate re-run.
_L24 = gn.L


def _util():
    try:
        import psutil
        p = psutil.Process()
        return psutil.cpu_percent(interval=None), p.memory_info().rss / 1e9, \
            psutil.virtual_memory().total / 1e9
    except Exception:
        try:
            load = os.getloadavg()[0]
            cores = os.cpu_count() or 1
            with open("/proc/meminfo") as f:
                m = {a.split(":")[0]: a.split()[1] for a in f}
            tot = int(m["MemTotal"]) / 1e6
            return 100 * load / cores, (tot - int(m["MemAvailable"]) / 1e6), tot
        except Exception:
            return 0.0, 0.0, 0.0


def load_short_candidates(merged_paths, max_tl):
    """Union candidates with total_len ≤ max_tl across all merged files, dedup by mkey (keep
    shortest), sorted shortest-first."""
    best = {}
    seen_files = 0
    for path in merged_paths:
        if not os.path.exists(path):
            print(f"  merged: MISSING {path} (skipped)", flush=True)
            continue
        seen_files += 1
        n = 0
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("total_len", 1 << 30) > max_tl:
                continue
            mk = r["mkey"]
            cur = best.get(mk)
            if cur is None or r["total_len"] < cur["total_len"]:
                best[mk] = r
            n += 1
        print(f"  merged: {path} -> {n} candidates ≤{max_tl}", flush=True)
    print(f"  merged: {seen_files} file(s), {len(best)} unique-by-mkey ≤{max_tl}", flush=True)
    return sorted(best.values(), key=lambda r: (r["total_len"], r["mkey"]))


def solve_worker(task):
    """Plain 2-gen greedy at the raised cap. gn.L is inherited (fork) from the parent, which
    set it before this pool was created."""
    rec, budget, hi_l = task
    rels = [np.array(x, dtype=gn.INT_DTYPE) for x in rec["relators"]]
    t0 = time.time()
    solver = gn.NRelatorSolver(rels, 2, max_nodes=budget, max_len=hi_l)
    path, nodes, _ = solver.solve()
    out = {k: rec[k] for k in ("mkey", "total_len", "form", "word", "gen", "ri", "src")
           if k in rec}
    out.update(relators=rec["relators"], budget=budget, L=hi_l,
               solved=path is not None, nodes=int(nodes),
               min_total_len=int(solver.min_total_len),
               # per-relator lengths at the peak state (sorted asc; last = longest single relator).
               # last == L-1 => the per-relator cap was binding even at this raised L.
               max_rel_lens=[int(x) for x in solver.max_rel_lens],
               max_rel_len=int(solver.max_rel_len),
               wall_s=round(time.time() - t0, 1))
    if path is not None:
        out["path_states"] = [[[int(a) for a in r] for r in st] for st in path["states"]]
        out["path_verified"] = bool(gn.verify_path(path["states"], 2))
        # per-relator lengths at the longest-total state on the winning path (did the SOLUTION need > 23?)
        peak = max(path["states"], key=lambda st: sum(len(r) for r in st))
        out["path_max_rel_lens"] = sorted(int(len(r)) for r in peak)
    return out


def try_certificate(rec, cert_budget, out_dir):
    """Best-effort full-chain certificate for a solve. The substitution-path re-run is done at
    the ORIGINAL L=24 (that is how `src` was harvested), while expand_fast's larger buffers
    happily hold the ≤23 children. Never raises — returns a status dict."""
    import plateau_elim as pe
    pe.CERTS = os.path.join(out_dir, "certs")   # build_chain_cert writes into pe.CERTS
    old = gn.L
    gn.L = _L24
    try:
        ok, errs, path = pe.build_chain_cert(rec, cert_budget)
        return {"cert_verified": bool(ok), "cert_path": path, "cert_errors": errs[:5]}
    except Exception as e:
        return {"cert_verified": False, "cert_exc": repr(e)}
    finally:
        gn.L = old


def selftest(hi_l):
    """Prove the raised-cap fast path solves what it should (a few known-trivial 2-gen
    presentations) — a plumbing smoke test before trusting a negative."""
    # all genuinely the trivial group (|det|=1 AND collapses to x=y=1), needing real moves
    cases = [
        [[1, 2], [2]],           # xy, y        -> y=1, x=1
        [[1], [1, 2]],           # x, xy        -> x=1, y=1
        [[1, 2], [1, 2, 2]],     # xy, xy²      -> y=1, x=1
        [[2, 1], [1, 1, 2]],     # yx, x²y      -> x=1, y=1
    ]
    allok = True
    for i, rels in enumerate(cases):
        r = solve_worker((({"relators": rels, "total_len": sum(len(x) for x in rels),
                            "mkey": f"self{i}", "form": "self", "word": "-",
                            "gen": 0, "ri": 0, "src": ""}), 50_000, hi_l))
        ok = r["solved"] and r.get("path_verified", False)
        allok &= ok
        print(f"  selftest[{i}] rels={rels} solved={r['solved']} "
              f"verified={r.get('path_verified')} nodes={r['nodes']}",
              flush=True)
    print(f"selftest: {'PASS' if allok else 'FAIL'} (raised cap L={hi_l})", flush=True)
    return allok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--merged", nargs="+", required=True,
                    help="one or more Lane-D merged.jsonl paths (missing ones skipped)")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--max_tl", type=int, default=16, help="only re-solve candidates ≤ this total_len")
    ap.add_argument("--L", type=int, default=40, help="raised per-relator cap (children ≥ L dropped)")
    ap.add_argument("--budget", type=int, default=300_000, help="node budget per candidate")
    ap.add_argument("--cert_budget", type=int, default=500_000,
                    help="budget for the L=24 substitution-path re-run when a solve certifies")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 8)
    ap.add_argument("--quick", action="store_true", help="self-test + tiny base case, then exit")
    ap.add_argument("--selftest", action="store_true", help="run only the plumbing smoke test")
    args = ap.parse_args()

    # raise the per-relator cap BEFORE the first solve()/expand_fast import
    gn.L = args.L
    print(f"resolve_hi_l: L(cap)={gn.L} budget={args.budget} max_tl={args.max_tl} "
          f"workers={args.workers}", flush=True)

    # warm the raised-cap numba fast path in the parent so forked workers inherit it
    gn.NRelatorSolver([np.array([1, 2], gn.INT_DTYPE), np.array([1, -2], gn.INT_DTYPE)],
                      2, max_nodes=8, max_len=gn.L).solve()

    if args.selftest or args.quick:
        ok = selftest(gn.L)
        if args.selftest:
            sys.exit(0 if ok else 1)

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"resolve_L{args.L}.jsonl")

    cands = load_short_candidates(args.merged, args.max_tl)
    if args.quick:
        cands = cands[:5]
        args.budget = min(args.budget, 20_000)
        print(f"quick: base case on {len(cands)} candidates @ {args.budget}", flush=True)
    if not cands:
        print("no candidates to solve (are the merged.jsonl paths correct / done?)", flush=True)
        return

    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            try:
                r = json.loads(line)
                if r.get("budget", 0) >= args.budget and r.get("L", 0) >= args.L:
                    done.add(r["mkey"])
            except Exception:
                pass
    todo = [c for c in cands if c["mkey"] not in done]
    print(f"resolve: {len(todo)} to solve ({len(done)} already done at L≥{args.L}, "
          f"budget≥{args.budget})", flush=True)
    if not todo:
        print("nothing to do — all short candidates already re-solved at this L/budget.", flush=True)
        return

    from multiprocessing import Pool
    n_solved = [0]
    done_ct = [0]
    t0 = time.time()
    stop = threading.Event()

    def heartbeat():
        while not stop.wait(60):
            k, el = done_ct[0], time.time() - t0
            rate = k / el if el and k else 0
            eta = (len(todo) - k) / rate if rate else 0
            cpu, ram, rt = _util()
            print(f"  … {k}/{len(todo)} solved={n_solved[0]} "
                  f"({rate:.2f}/s, ETA {eta / 60:.0f}m) | CPU {cpu:.0f}% RAM {ram:.0f}/{rt:.0f}GB",
                  flush=True)

    hb = threading.Thread(target=heartbeat, daemon=True)
    hb.start()
    fout = open(out_path, "a")
    try:
        with Pool(processes=args.workers, maxtasksperchild=16) as pool:
            for res in pool.imap_unordered(
                    solve_worker, [(rec, args.budget, args.L) for rec in todo]):
                done_ct[0] += 1
                if res["solved"]:
                    n_solved[0] += 1
                    print(f"*** SOLVED @ L={args.L} *** mkey={res['mkey']} tl={res['total_len']} "
                          f"form={res['form']} word={res['word']} nodes={res['nodes']} "
                          f"path_verified={res.get('path_verified')}", flush=True)
                    res.update(try_certificate(res, args.cert_budget, args.out_dir))
                    print(f"    certificate: verified={res.get('cert_verified')} "
                          f"{res.get('cert_path') or res.get('cert_exc')}", flush=True)
                fout.write(json.dumps(res) + "\n")
                fout.flush()
                os.fsync(fout.fileno())
                if done_ct[0] % 100 == 0:
                    cpu, ram, rt = _util()
                    el = time.time() - t0
                    rate = done_ct[0] / el if el else 0
                    print(f"  [{done_ct[0]}/{len(todo)}] solved={n_solved[0]} "
                          f"({rate:.2f}/s, ETA {(len(todo)-done_ct[0])/rate/60 if rate else 0:.0f}m) "
                          f"| CPU {cpu:.0f}% RAM {ram:.0f}/{rt:.0f}GB", flush=True)
    finally:
        stop.set()
        fout.close()
    print(f"resolve_hi_l done: {n_solved[0]} solved / {len(todo)} attempted "
          f"(L={args.L}, budget={args.budget}) in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
