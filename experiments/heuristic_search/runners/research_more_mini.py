"""More mini-experiments while scale10k/ak3 packs run (≤10k, shared wall).

1) Extra arms on fresh_hard slice (s28 won L-stratified extras).
2) AK3 height-18 frontier sample: BFS to total≈18, then s20/recommended @10k.
3) More CoV z-seeds on orbit-2 / dual_src (length≤4 mixed words).

    python3 -m experiments.heuristic_search.runners.research_more_mini
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import deque
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402
from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402
from experiments.search.greedy_baseline import (  # noqa: E402
    expand_node_nj, str_to_arr, reduce_relator_nj, canonical_pair_nj,
)
import numpy as np

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "more_mini")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
SCALE_STATE = os.path.join(ROOT, "results", "heuristic_search", "scale10k", "state.json")
SLICE_HARD = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                          "slice_fresh_hard.json")
BUDGET = 10_000
CAP = 48
RESERVE = 120 * BUDGET

ARMS = {
    "s20": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0}}]},
    "s28": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 28.0}}]},
    "s8": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 8.0}}]},
    "mk8": {"segments": [{"upto": None, "w": {"L": 1.0, "MK": 8.0}}]},
    "recommended": RECOMMENDED,
    "length": None,
}


def _iso():
    return datetime.now(timezone.utc).isoformat()


def _rem():
    if not os.path.exists(SCALE_STATE):
        return 99999.0
    end = datetime.fromisoformat(json.load(open(SCALE_STATE))["wall_end"])
    return (end - datetime.now(timezone.utc)).total_seconds()


def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done(keys):
    s = set()
    if not os.path.exists(JSONL):
        return s
    for line in open(JSONL):
        r = json.loads(line)
        s.add(tuple(r.get(k) for k in keys))
    return s


def _search(r1, r2, cfg, budget=BUDGET, cap=CAP):
    t0 = time.perf_counter()
    res = greedy_search_hcompact(
        r1, r2, budget, max_relator_length=cap, config=cfg,
        reserve_states=RESERVE)
    dt = time.perf_counter() - t0
    return {
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": int(res["nodes_explored"]) if res["solved"] else None,
        "min_relator_length": res["min_relator_length"],
        "max_expanded": res["max_relator_length_expanded"],
        "secs": round(dt, 3),
        "pops_s": round(res["nodes_explored"] / max(dt, 1e-9), 1),
        "budget": budget,
        "cap": cap,
    }


def phase_fresh_extra():
    rows = json.load(open(SLICE_HARD))["rows"]
    done = _done(("phase", "arm", "idx"))
    n = 0
    for rec in rows:
        for arm, cfg in ARMS.items():
            if _rem() < 120:
                return n
            key = ("fresh_extra", arm, rec["idx"])
            if key in done:
                continue
            res = _search(rec["r1"], rec["r2"], cfg)
            row = {"phase": "fresh_extra", "arm": arm, "idx": rec["idx"],
                   "L": rec["L"], "ts": _iso(), **res}
            for c in (1000, 5000, 10000):
                row[f"solved_le_{c}"] = bool(
                    row["solved_at"] is not None and row["solved_at"] <= c)
            _append(row)
            done.add(key)
            n += 1
            if n % 10 == 0:
                print(f"  [fresh+] {arm}/idx={rec['idx']} solved={res['solved']}",
                      flush=True)
    return n


def _pair_key(r1, r2):
    a, b = (r1, r2) if (r1, r2) <= (r2, r1) else (r2, r1)
    return a + "\0" + b


def _total(r1, r2):
    return len(r1) + len(r2)


def phase_h18_frontier():
    """Cheap BFS from orbit-2 until we collect up to 40 states with total==18."""
    done = _done(("phase", "arm", "seed"))
    if _rem() < 300:
        return 0
    # BFS with tiny node budget on expansion via baseline expand
    start = ("YYXXyx", "YYYxyXX")
    frontier = deque([start])
    seen = {_pair_key(*start)}
    at18 = []
    max_states = 5000
    visited = 0
    while frontier and len(at18) < 40 and visited < max_states:
        r1, r2 = frontier.popleft()
        visited += 1
        t = _total(r1, r2)
        if t == 18:
            at18.append((r1, r2))
            continue
        if t > 18:
            continue
        # expand children with cap 24 for the scout only
        a1 = str_to_arr(r1)
        a2 = str_to_arr(r2)
        # use expand via greedy one-step: borrow hcompact tiny search? too heavy.
        # Use expand_node_nj from baseline.
        from experiments.search import greedy_baseline as gb
        # expand_node_nj returns flat arrays — use Lab-style via apply moves
        # Simpler: one pop of length-only search recording states at depth
        pass
    # Fallback: run length-only searches that record max_expanded path via
    # multiple short searches is hard. Instead sample via random AC-ish:
    # use greedy_search_hcompact with length and take min/max relators? weak.
    # Practical approach: for each of 40 randomish Nielsen images of orbit2
    # at short words — use fixed list of conjugacy/Nielsen moves.
    seeds = []
    base_r1, base_r2 = start
    # cyclic rotations + inv + swap generate height variety
    def cyc(w, k):
        k %= len(w) if w else 1
        return w[k:] + w[:k] if w else w

    for i in range(len(base_r1)):
        for j in range(len(base_r2)):
            seeds.append((f"rot_{i}_{j}", cyc(base_r1, i), cyc(base_r2, j)))
    # inv variants
    inv = {"X": "x", "x": "X", "Y": "y", "y": "Y"}
    def invw(w):
        return "".join(inv[c] for c in w[::-1])
    seeds.append(("inv", invw(base_r1), invw(base_r2)))
    seeds.append(("swap", base_r2, base_r1))
    # dedupe
    uniq = []
    seen2 = set()
    for name, a, b in seeds:
        k = _pair_key(a, b)
        if k in seen2:
            continue
        seen2.add(k)
        uniq.append((name, a, b))
    n = 0
    for name, a, b in uniq[:40]:
        for arm in ("s20", "s28", "recommended", "length"):
            if _rem() < 120:
                return n
            key = ("h18_rot", arm, name)
            if key in done:
                continue
            res = _search(a, b, ARMS[arm])
            _append({"phase": "h18_rot", "arm": arm, "seed": name,
                     "r1": a, "r2": b, "start_total": _total(a, b),
                     "ts": _iso(), **res})
            done.add(key)
            n += 1
            if res["solved"] or (res["min_relator_length"] or 99) < 13:
                print(f"  *** TRIPWIRE {name}/{arm} minL="
                      f"{res['min_relator_length']}", flush=True)
            elif n % 8 == 0:
                print(f"  [h18] {name}/{arm} minL={res['min_relator_length']}",
                      flush=True)
    return n


def phase_more_z():
    """Apply short z substitutions for y on orbit2 / dual_src."""
    done = _done(("phase", "start", "z", "arm"))
    zs = ["Xy", "xY", "xy", "yx", "XXY", "XYX", "YXY", "xyx", "XXy", "xYY"]
    bases = [
        ("orbit2", "YYXXyx", "YYYxyXX"),
        ("dual_src_wh", "YYXXXyx", "YYXXXYxyX"),
        ("ak3", "YXYxyx", "YYYYxxx"),
    ]

    def apply_z(w, zp, zn):
        out = []
        for c in w:
            if c == "Y":
                out.append(zp)
            elif c == "y":
                out.append(zn)
            else:
                out.append(c)
        return "".join(out)

    def z_neg(zp):
        inv = {"X": "x", "x": "X", "Y": "y", "y": "Y"}
        return "".join(inv[c] for c in zp[::-1])

    n = 0
    for sname, r1, r2 in bases:
        for z in zs:
            zn = z_neg(z)
            a, b = apply_z(r1, z, zn), apply_z(r2, z, zn)
            for arm in ("s20", "s28", "recommended"):
                if _rem() < 120:
                    return n
                key = ("more_z", sname, z, arm)
                if key in done:
                    continue
                res = _search(a, b, ARMS[arm])
                _append({"phase": "more_z", "start": sname, "z": z, "arm": arm,
                         "r1": a, "r2": b, "ts": _iso(), **res})
                done.add(key)
                n += 1
                if res["solved"] or (res["min_relator_length"] or 99) < 13:
                    print(f"  *** TRIPWIRE z={z}/{sname}/{arm}", flush=True)
                elif n % 10 == 0:
                    print(f"  [z] {sname}/z={z}/{arm} minL="
                          f"{res['min_relator_length']}", flush=True)
    return n


def write_results():
    if not os.path.exists(JSONL):
        return
    rows = [json.loads(l) for l in open(JSONL)]
    lines = [f"# more_mini RESULTS\n\nUpdated `{_iso()}` rows={len(rows)} remain={_rem()/3600:.2f}h\n"]
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        by[r["phase"]].append(r)
    for ph, rs in by.items():
        sol = sum(1 for r in rs if r.get("solved"))
        bel = sum(1 for r in rs if (r.get("min_relator_length") or 99) < 13)
        lines.append(f"## {ph}: n={len(rs)} solved={sol} below13={bel}\n")
        if ph == "fresh_extra":
            arms = defaultdict(list)
            for r in rs:
                arms[r["arm"]].append(r)
            lines.append("| arm | @1k | @5k | @10k |\n|---|---:|---:|---:|\n")
            for a, ars in sorted(arms.items()):
                def c(k):
                    return sum(1 for r in ars if r.get(k))
                lines.append(
                    f"| `{a}` | {c('solved_le_1000')}/{len(ars)} | "
                    f"{c('solved_le_5000')}/{len(ars)} | "
                    f"{c('solved_le_10000')}/{len(ars)} |\n")
    open(RESULTS, "w").write("".join(lines) + "\n")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[more] remain={_rem()/3600:.2f}h", flush=True)
    greedy_search_hcompact("X", "Y", 50, max_relator_length=48,
                           config=ARMS["s20"], reserve_states=5000)
    while _rem() > 180:
        n1 = phase_fresh_extra()
        n2 = phase_h18_frontier()
        n3 = phase_more_z()
        write_results()
        print(f"[more] cycle new={n1+n2+n3}", flush=True)
        if n1 + n2 + n3 == 0:
            time.sleep(min(300, max(0, _rem() - 60)))
    write_results()
    print("[more] done", flush=True)


if __name__ == "__main__":
    main()
