"""Lane D: plateau elimination — mine stabilized-AK(3) search balls for Lemma-11
eliminations, producing FRESH 2-generator presentations stably-AC-equivalent to AK(3)
by construction; greedy-trivializing ANY of them proves AK(3) stably AC-trivial.

Why this can work where the wormhole sweeps failed: the z=w sweeps ran plain greedy on
the 3-gen stabilization and plateaued at total length 13 — greedy has no destabilize
move. But every visited 3-gen state S with some generator occurring EXACTLY ONCE in a
relator admits a Lemma-11 elimination S -> E (a 2-gen presentation of the trivial
group). The chain AK3 -(stabilize z=w)-> S0 -(substitution path)-> S -(eliminate)-> E
is a stable-AC equivalence, so E ~stAC~ AK3. These E are 2-gen quotients nobody has
ever searched from. All 151 certified Wirtinger catalog leaves were plain-greedy
solvable, so 2-gen presentations of the trivial group are often greedy-easy even when
their 3-gen parents are stuck.

Phases (resumable, append-only JSONL under results/stable_ac/ak3_stable_proof/laneD/):
  harvest  one greedy run per (form, word) keeping the FULL visited set; every visited
           state x every eliminable (gen, ri) -> candidate E; per-run dedup; stream
           cands_<form>_<word>.jsonl
  merge    global dedup by signed-relabel symmetry key; drop candidates in the AK3/P25
           canonical classes; rank by total length -> merged.jsonl
  solve    shortest-first plain 2-gen greedy per candidate (Pool, fork,
           maxtasksperchild); stream solve.jsonl; on ANY solve, rebuild the full
           certificate chain (stabilize + substitution path + eliminate + greedy path
           + sign-fix inverts), verify with verify_certificate, save under certs/.

Run:  .venv/bin/python3 experiments/stable_ac/ak3_stable_proof/plateau_elim.py \
          --phase all --budget 150000 --budget2 25000 --workers 3 --solve_workers 8
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

import greedy_nrel as gn  # noqa: E402
import ak3_words as aw  # noqa: E402
from stable_moves import LengthCapExceeded, eliminate, find_eliminable, invert_move  # noqa: E402
from mitm import symmetry_keys  # noqa: E402

INT = gn.INT_DTYPE

# register P25 as a start form: P25 ~AC~ AK3 is certified (Appendix-F cert), so a
# Lane D chain from P25 composes into an AK(3) claim via concat_certificates.
import stabilize as _stab  # noqa: E402
from hmoves import P25 as _P25  # noqa: E402
aw.FORMS.setdefault("p25", _stab.relators_to_flat([list(r) for r in _P25], 2, gn.L))

# F: the dominant floor state of the quotient basin (712/1006 greedy flows), certified
# AC-equivalent to AK3 by 21 substitution moves (certs/laneF_F_to_AK3.json).
_FLOOR_F = [[-2, -2, 1, 2, -1, -1], [-2, -2, -2, -1, -1, 2, 1]]
aw.FORMS.setdefault("floorF", _stab.relators_to_flat(_FLOOR_F, 2, gn.L))

LANE_D = os.environ.get("ACX_LANED_DIR") or os.path.join(
    ROOT, "results", "stable_ac", "ak3_stable_proof", "laneD")
CERTS = os.environ.get("ACX_CERTS_DIR") or os.path.join(
    ROOT, "results", "stable_ac", "ak3_stable_proof", "certs")

HERO = ["xyx", "yxy", "xxx", "yyyy", "Xyxy", "YXyxy", "x", "y"]  # + r1, r2 per form


def word_ints(form, name):
    if name == "r1":
        return list(gn.flat_to_relators(aw.FORMS[form], 2)[0])
    if name == "r2":
        return list(gn.flat_to_relators(aw.FORMS[form], 2)[1])
    if not all(c in "xXyY" for c in name):
        for e in aw.build_word_bank():
            if e["name"] == name:
                return list(e["w_ints"])
        raise KeyError(f"unknown word name {name!r}")
    return aw.parse(name)


def run_stabilized(form, w, budget, block_null_revert=True):
    """Greedy on <x,y,z | r1,r2,z.w^-1>; returns the solver (visited kept) + path."""
    sflat = aw.stabilize_with_word(aw.FORMS[form], w)
    rels = gn.flat_to_relators(sflat, 3)
    blocked = [gn.null_revert_state(sflat, 3)] if block_null_revert else None
    solver = gn.NRelatorSolver(rels, 3, max_nodes=budget, max_len=gn.L,
                               blocked_states=blocked)
    path, nodes, _ = solver.solve()
    return solver, path, nodes


def harvest_one(task):
    """Worker: one (form, word_name) run -> stream unique candidates to its own file.
    Candidates longer than harvest_tl_cap (task[4], default 26) are counted, not
    written — bounds file size; they are unsolvable at L=24 in practice."""
    form, name, budget, l_cap = task[:4]
    harvest_tl_cap = task[4] if len(task) > 4 else 26
    out_path = os.path.join(LANE_D, f"cands_{form}_{name}.jsonl")
    done_marker = os.path.join(LANE_D, f"cands_{form}_{name}.done")
    if os.path.exists(done_marker):
        return {"form": form, "word": name, "skipped": True}
    w = word_ints(form, name)
    t0 = time.time()
    solver, path, nodes = run_stabilized(form, w, budget)
    seen = {}
    n_cap = n_elim = n_long = 0
    for key in solver.visited:
        state = gn.key_to_state(key)
        rels = [[int(a) for a in r] for r in state]
        for g, ri in find_eliminable(rels, 3):
            n_elim += 1
            try:
                e_state, _, _ = eliminate(rels, 3, g, ri, l_cap=l_cap)
            except (LengthCapExceeded, ValueError):
                n_cap += 1
                continue
            if any(len(r) == 0 for r in e_state):
                continue
            if sum(len(r) for r in e_state) > harvest_tl_cap:
                n_long += 1
                continue
            ck = gn.canonical_key(tuple(np.array(r, dtype=INT) for r in e_state))
            if ck in seen:
                continue
            seen[ck] = {"cand": ck.hex(),
                        "relators": [list(r) for r in e_state],
                        "total_len": sum(len(r) for r in e_state),
                        "form": form, "word": name,
                        "src": key.hex(), "gen": g, "ri": ri}
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f:
        for rec in seen.values():
            f.write(json.dumps(rec) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, out_path)
    with open(done_marker, "w") as f:
        f.write(json.dumps({"nodes": nodes, "visited": len(solver.visited),
                            "unique_cands": len(seen), "capped": n_cap,
                            "over_tl_cap": n_long, "eliminables": n_elim,
                            "solved_directly": path is not None,
                            "min_total_len": int(solver.min_total_len),
                            "wall_s": round(time.time() - t0, 1)}))
    return {"form": form, "word": name, "visited": len(solver.visited),
            "unique_cands": len(seen), "solved_directly": path is not None,
            "wall_s": round(time.time() - t0, 1)}


def phase_harvest(args):
    os.makedirs(LANE_D, exist_ok=True)
    words = args.words.split(",") if args.words else HERO + ["r1", "r2"]
    forms = args.forms.split(",")
    tasks = [(f, n, args.budget, args.l_cap, args.harvest_tl_cap)
             for f in forms for n in words]
    tasks = [t for t in tasks
             if not os.path.exists(os.path.join(LANE_D, f"cands_{t[0]}_{t[1]}.done"))]
    print(f"harvest: {len(tasks)} runs pending", flush=True)
    if not tasks:
        return
    gn.solve_one(aw.stabilize_with_word(aw.FORMS["textbook"], [1, 2, 1]),
                 n_gen=3, max_nodes=8)  # warm numba pre-fork
    from multiprocessing import Pool
    with Pool(processes=args.workers, maxtasksperchild=1) as pool:
        for res in pool.imap_unordered(harvest_one, tasks):
            print(f"  harvested {res}", flush=True)


def merge_one_file(task):
    """Worker: symmetry-dedup one candidate file -> (local_best, n_in, n_over)."""
    fn, merge_tl_cap = task
    from hmoves import AK3, P25
    known = set()
    for st in (AK3, P25):
        known |= symmetry_keys([list(r) for r in st])
    best = {}
    n_in = n_over = 0
    for line in open(os.path.join(LANE_D, fn)):
        rec = json.loads(line)
        n_in += 1
        if rec["total_len"] > merge_tl_cap:
            n_over += 1
            continue
        skeys = symmetry_keys(rec["relators"])
        if skeys & known:
            continue
        mkey = min(skeys).hex()
        cur = best.get(mkey)
        if cur is None or rec["total_len"] < cur["total_len"]:
            rec["mkey"] = mkey
            best[mkey] = rec
    return best, n_in, n_over


def phase_merge(args):
    """Global symmetry dedup + drop AK3/P25 classes + rank by total length. Records
    longer than --merge_tl_cap are only counted, not kept — bounds RAM. Per-file
    parallel (the symmetry keying dominates)."""
    from collections import Counter
    files = sorted(f for f in os.listdir(LANE_D)
                   if f.startswith("cands_") and f.endswith(".jsonl"))
    best = {}
    n_in = n_over = 0
    from multiprocessing import Pool
    with Pool(processes=max(1, args.merge_workers)) as pool:
        for local, ni, no in pool.imap_unordered(
                merge_one_file, [(fn, args.merge_tl_cap) for fn in files]):
            n_in += ni
            n_over += no
            for mkey, rec in local.items():
                cur = best.get(mkey)
                if cur is None or rec["total_len"] < cur["total_len"]:
                    best[mkey] = rec
            print(f"merge: +{len(local)} (global {len(best)})", flush=True)
    if n_over:
        print(f"merge: {n_over} raw candidates dropped as "
              f"total_len > {args.merge_tl_cap} (not deduped)", flush=True)
    ranked = sorted(best.values(), key=lambda r: (r["total_len"], r["mkey"]))
    out = os.path.join(LANE_D, "merged.jsonl")
    with open(out + ".tmp", "w") as f:
        for rec in ranked:
            f.write(json.dumps(rec) + "\n")
    os.replace(out + ".tmp", out)
    by_len = Counter(r["total_len"] for r in ranked)
    print(f"merge: {n_in} raw -> {len(ranked)} unique-mod-symmetry "
          f"(AK3/P25 classes dropped); shortest lens: "
          f"{sorted(by_len.items())[:12]}", flush=True)


def solve_candidate(task):
    """Worker: plain 2-gen greedy on one candidate."""
    rec, budget = task
    rels = [np.array(r, dtype=INT) for r in rec["relators"]]
    t0 = time.time()
    solver = gn.NRelatorSolver(rels, 2, max_nodes=budget, max_len=gn.L)
    path, nodes, _ = solver.solve()
    out = {"mkey": rec["mkey"], "total_len": rec["total_len"], "budget": budget,
           "solved": path is not None, "nodes": int(nodes),
           "min_total_len": int(solver.min_total_len),
           "wall_s": round(time.time() - t0, 1),
           "form": rec["form"], "word": rec["word"], "gen": rec["gen"],
           "ri": rec["ri"], "src": rec["src"], "relators": rec["relators"]}
    if path is not None:
        out["path_states"] = [[[int(a) for a in r] for r in st]
                              for st in path["states"]]
        out["path_verified"] = bool(gn.verify_path(path["states"], 2))
    return out


def build_chain_cert(solve_rec, budget):
    """Full certificate: AK3 -stabilize-> S0 -subst...-> S -eliminate-> E -subst...->
    trivial (+ inverts to make every single-letter relator positive)."""
    from certificate import make_certificate, save_certificate
    from verify_certificate import verify
    form, name = solve_rec["form"], solve_rec["word"]
    w = word_ints(form, name)
    solver, _, _ = run_stabilized(form, w, budget)   # deterministic re-run
    src_key = bytes.fromhex(solve_rec["src"])
    assert src_key in solver.visited, "cert rebuild: src state not re-found"
    sub_path = solver._retrace(src_key)

    ak3 = [list(r) for r in gn.flat_to_relators(aw.FORMS[form], 2)]
    states = [(ak3, 2)]
    steps = []
    # stabilize (recorded next = canonical(S0); verifier accepts canonical equality)
    s0_canon = [[int(a) for a in r] for r in sub_path["states"][0]]
    states.append((s0_canon, 3))
    steps.append({"type": "stabilize", "z": 3, "w": list(w)})
    # substitution path through canonical 3-gen states
    for st in sub_path["states"][1:]:
        states.append(([[int(a) for a in r] for r in st], 3))
        steps.append({"type": "substitution"})
    # eliminate at S = canonical src state
    s_rels = [[int(a) for a in r] for r in gn.key_to_state(src_key)]
    e_state, ng, e_step = eliminate(s_rels, 3, solve_rec["gen"], solve_rec["ri"],
                                    l_cap=64)
    e_rels = [list(r) for r in e_state]
    states.append((e_rels, 2))
    steps.append(e_step)
    # 2-gen greedy path (canonical states); path_states[0] == canonical(E)
    pstates = solve_rec["path_states"]
    for st in pstates[1:]:
        states.append(([list(r) for r in st], 2))
        steps.append({"type": "substitution"})
    # sign-fix: invert any negative single-letter relator
    cur = [list(r) for r in states[-1][0]]
    for i, r in enumerate(cur):
        if len(r) == 1 and r[0] < 0:
            cur, _step = invert_move(cur, i)
            cur = [list(x) for x in cur]
            states.append(([list(x) for x in cur], 2))
            steps.append(_step)
    cert = make_certificate(
        name=f"laneD_{form}_{name}_{solve_rec['mkey'][:12]}",
        claim="AK(3) is stably AC-trivial: stabilize z=w, substitution path, "
              "Lemma-11 elimination, then plain-AC trivialization of the quotient.",
        states_with_ngen=states, steps=steps, end_is_trivial=True,
        meta={"lane": "D", "form": form, "word": name,
              "harvest_budget": budget, "solve_budget": solve_rec["budget"]})
    ok, errs = verify(cert)
    os.makedirs(CERTS, exist_ok=True)
    path = os.path.join(CERTS, f"laneD_{form}_{name}_{solve_rec['mkey'][:12]}.json")
    save_certificate(cert, path)
    return ok, errs, path


def phase_solve(args):
    merged = os.path.join(LANE_D, "merged.jsonl")
    out_path = os.path.join(LANE_D, "solve.jsonl")
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            try:
                r = json.loads(line)
                if r["budget"] >= args.budget2:
                    done.add(r["mkey"])
            except Exception:
                pass
    cands = []
    for line in open(merged):
        rec = json.loads(line)
        if rec["total_len"] > args.tl_cap:
            continue
        if rec["mkey"] in done:
            continue
        if len(cands) >= args.top:
            break
        cands.append(rec)
    print(f"solve: {len(cands)} candidates (tl_cap={args.tl_cap}, top={args.top}, "
          f"{len(done)} already done at this budget)", flush=True)
    if not cands:
        return
    gn.solve_one(aw.FORMS["textbook"], n_gen=2, max_nodes=8)  # warm numba pre-fork
    from multiprocessing import Pool
    n_solved = 0
    t0 = time.time()
    with Pool(processes=args.solve_workers, maxtasksperchild=16) as pool, \
            open(out_path, "a") as f:
        tasks = [(rec, args.budget2) for rec in cands]
        for i, res in enumerate(pool.imap_unordered(solve_candidate, tasks)):
            if res["solved"]:
                n_solved += 1
                print(f"*** SOLVED *** cand {res['mkey'][:12]} tl={res['total_len']} "
                      f"({res['form']},{res['word']}) nodes={res['nodes']} "
                      f"path_verified={res['path_verified']}", flush=True)
                try:
                    ok, errs, cpath = build_chain_cert(res, args.budget)
                    res["cert_verified"] = ok
                    res["cert_path"] = cpath
                    res["cert_errors"] = errs[:5]
                    print(f"*** CERT {'VERIFIED' if ok else 'FAILED'} *** {cpath}",
                          flush=True)
                except Exception as e:
                    import traceback
                    res["cert_verified"] = False
                    res["cert_exc"] = repr(e)
                    print(f"cert build EXC: {e}\n{traceback.format_exc()[-1500:]}",
                          flush=True)
            f.write(json.dumps(res) + "\n")
            f.flush()
            os.fsync(f.fileno())
            if (i + 1) % 200 == 0:
                rate = (i + 1) / (time.time() - t0)
                print(f"  [{i + 1}/{len(cands)}] solved={n_solved} "
                      f"({rate:.1f} cands/s)", flush=True)
            if n_solved and args.stop_on_first:
                pool.terminate()
                break
    print(f"solve phase done: {n_solved} solved / {len(cands)} attempted", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["harvest", "merge", "solve", "all"],
                    default="all")
    ap.add_argument("--forms", default="textbook,rep")
    ap.add_argument("--words", default=None)
    ap.add_argument("--budget", type=int, default=150_000)
    ap.add_argument("--budget2", type=int, default=25_000)
    ap.add_argument("--l_cap", type=int, default=22)
    ap.add_argument("--harvest_tl_cap", type=int, default=26)
    ap.add_argument("--merge_tl_cap", type=int, default=24)
    ap.add_argument("--merge_workers", type=int, default=max(1, (os.cpu_count() or 4) // 2))
    ap.add_argument("--tl_cap", type=int, default=24)
    ap.add_argument("--top", type=int, default=6000)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--solve_workers", type=int, default=8)
    ap.add_argument("--stop_on_first", action="store_true")
    args = ap.parse_args()
    if args.phase in ("harvest", "all"):
        phase_harvest(args)
    if args.phase in ("merge", "all"):
        phase_merge(args)
    if args.phase in ("solve", "all"):
        phase_solve(args)


if __name__ == "__main__":
    main()
