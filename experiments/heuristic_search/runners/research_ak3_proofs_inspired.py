"""AK(3)-aimed mini-experiments inspired by ``codex/proofs`` (READ-ONLY).

Do NOT modify ``codex/proofs``. Ideas transferred from that branch's theory
handoffs + local ``results/stable_ac/ak3/RESULTS.md``:

  A) Alternate starts: orbit-2 (degree-22 crossroads), 5 aut_min-14 orbits,
     dual-source stable endpoint (Result 1 on proofs branch).
  B) Ordering arms at those starts (length / S-plateau / recommended / MK / K).
  C) Floor CoV hop (φ: y↦xy, z=Xy) then climb — height-17 bridge shortcut.
  D) Relabel portfolio at FULL depth (not split) on orbit-2.
  E) Height-climb readout: did search ever expand ≥18? (trivialization lower bound)
  F) Budget ladder 1k → 5k → 10k (prefix property; ≤1h/search).

Success metrics (pre-registered):
  - solved (tripwire if true on aca_115 class — certify before celebrating)
  - ever_min_total < 13 (same tripwire)
  - ever_expanded >= 18 (necessary for classical escape of ≤17 component)
  - min_relator_length / first-seen floor strings (orbit proxy, not aut_canon)

    python3 -m experiments.heuristic_search.runners.research_ak3_proofs_inspired
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402
from experiments.heuristic_search.core.hsolve import RECOMMENDED, greedy_search_h  # noqa: E402

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "ak3_proofs_inspired")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
STATE = os.path.join(OUT_DIR, "state.json")
PLAN = os.path.join(OUT_DIR, "PLAN.md")

# Share wall with scale10k if present; else 10h from now.
SCALE_STATE = os.path.join(ROOT, "results", "heuristic_search", "scale10k", "state.json")
BUDGETS = (1000, 5000, 10_000)
MAX_SECS = 3600.0
RESERVE_MULT = 120
CAP = 48

# From results/stable_ac/ak3/RESULTS.md + proofs dual-source endpoint.
STARTS = [
    ("ak3_classic", "xxxYYYY", "xyxYXY"),
    ("ak3_canon", "YXYxyx", "YYYYxxx"),
    ("orbit2", "YYXXyx", "YYYxyXX"),
    ("aut14_a", "YYXyXyx", "YXYXyxx"),
    ("aut14_b", "YYXYxyx", "YXyXyxx"),
    ("aut14_c", "YYXyXyx", "YXyxxyX"),
    ("aut14_d", "YYXXXyx", "YYxyxyX"),
    ("aut14_e", "YXXYx", "YYYYXyyyx"),
    # proofs Result 1 dual-source compression stable endpoint / Whitehead
    ("dual_src_ep", "XYXYxxxy", "YYXYxxYXyxy"),
    ("dual_src_wh", "YYXXXyx", "YYXXXYxyX"),
]

ARMS = {
    "length": None,
    "s12": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 12.0}}]},
    "s20": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0}}]},
    "mk8": {"segments": [{"upto": None, "w": {"L": 1.0, "MK": 8.0}}]},
    "k8": {"segments": [{"upto": None, "w": {"L": 1.0, "K": 8.0}}]},
    "recommended": RECOMMENDED,
}

# Full-depth relabels (EXP-17: do not split budget).
RELABELS = [
    ("id", lambda a, b: (a, b)),
    ("swap", lambda a, b: (b, a)),
    ("inv", lambda a, b: (a.swapcase()[::-1] if False else _inv(a), _inv(b))),
    ("x2y", lambda a, b: (_mapxy(a, "Y", "X", "y", "x"), _mapxy(b, "Y", "X", "y", "x"))),
]


def _inv(w):
    return "".join({"X": "x", "x": "X", "Y": "y", "y": "Y"}[c] for c in w[::-1])


def _mapxy(w, X, Y, x, y):
    return w.translate(str.maketrans({"X": X, "Y": Y, "x": x, "y": y}))


def _now():
    return datetime.now(timezone.utc)


def _iso():
    return _now().isoformat()


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done(keys):
    seen = set()
    if not os.path.exists(JSONL):
        return seen
    with open(JSONL) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            seen.add(tuple(r.get(k) for k in keys))
    return seen


def _wall_end():
    if os.path.exists(SCALE_STATE):
        return datetime.fromisoformat(json.load(open(SCALE_STATE))["wall_end"])
    return datetime.fromtimestamp(_now().timestamp() + 10 * 3600, tz=timezone.utc)


def _remaining():
    return (_wall_end() - _now()).total_seconds()


def _search(r1, r2, budget, cfg, cap=CAP):
    t0 = time.perf_counter()
    t_dead = t0 + min(MAX_SECS, max(30.0, _remaining() - 60))

    def progress(n):
        if time.perf_counter() > t_dead:
            raise TimeoutError("wall/search deadline")

    res = greedy_search_hcompact(
        r1, r2, budget, max_relator_length=cap, config=cfg,
        progress=progress, reserve_states=RESERVE_MULT * budget)
    dt = time.perf_counter() - t0
    out = {
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": int(res["nodes_explored"]) if res["solved"] else None,
        "min_relator_length": res["min_relator_length"],
        "min_relator": res["min_relator"],
        "max_relator_length": res["max_relator_length"],
        "max_relator": res["max_relator"],
        "max_expanded": res["max_relator_length_expanded"],
        "climbed_ge18": bool(res["max_relator_length_expanded"] >= 18),
        "below13": bool(res["min_relator_length"] is not None
                        and res["min_relator_length"] < 13),
        "secs": round(dt, 3),
        "pops_s": round(res["nodes_explored"] / max(dt, 1e-9), 1),
        "budget": budget,
        "cap": cap,
    }
    if res["solved"] or out["below13"]:
        rec = greedy_search_h(r1, r2, budget, max_relator_length=cap,
                              config=cfg, keep_path=True)
        out["path_moves"] = rec.get("path_moves")
        out["cert_nodes"] = rec["nodes_explored"]
        out["cert_minL"] = rec["min_relator_length"]
    return out


def write_plan():
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(PLAN):
        return
    open(PLAN, "w").write(
        "# AK(3) proofs-inspired mini-experiments\n\n"
        "Source of ideas: remote `codex/proofs` (READ-ONLY — not modified) + "
        "`results/stable_ac/ak3/RESULTS.md`.\n\n"
        "Wall shared with scale10k. Budgets ≤10k. New files only.\n"
    )


def write_results():
    if not os.path.exists(JSONL):
        return
    rows = [json.loads(l) for l in open(JSONL) if "error" not in json.loads(l)]
    # re-read safely
    rows = []
    for l in open(JSONL):
        r = json.loads(l)
        if "error" in r:
            continue
        rows.append(r)
    lines = [
        "# AK(3) proofs-inspired — RESULTS",
        "",
        f"Updated: `{_iso()}` · remaining `{_remaining()/3600:.2f}h` · "
        f"rows `{len(rows)}`",
        "",
        "Tripwire: any `solved` or `below13` on AK(3) class must be "
        "independently certified before any claim.",
        "",
    ]
    # Phase A/B summary
    ab = [r for r in rows if r.get("phase") == "starts_x_arms"]
    if ab:
        lines += ["## A/B — starts × arms (best minL / climbed≥18 / solved)", "",
                  "| start | arm | budget | n | minL_best | climbed≥18 | solved |",
                  "|---|---|---:|---:|---:|---:|---:|"]
        from collections import defaultdict
        g = defaultdict(list)
        for r in ab:
            g[(r["start"], r["arm"], r["budget"])].append(r)
        for k in sorted(g):
            rs = g[k]
            minL = min(r["min_relator_length"] for r in rs)
            climb = sum(1 for r in rs if r["climbed_ge18"])
            sol = sum(1 for r in rs if r["solved"])
            lines.append(
                f"| `{k[0]}` | `{k[1]}` | {k[2]} | {len(rs)} | {minL} | "
                f"{climb}/{len(rs)} | {sol} |")
        lines.append("")
    for phase in ("cov_hop", "relabel_full", "dual_focus"):
        ps = [r for r in rows if r.get("phase") == phase]
        if not ps:
            continue
        lines += [f"## Phase `{phase}` ({len(ps)} rows)", ""]
        sol = sum(1 for r in ps if r.get("solved"))
        bel = sum(1 for r in ps if r.get("below13"))
        climb = sum(1 for r in ps if r.get("climbed_ge18"))
        best = min((r["min_relator_length"] for r in ps), default=None)
        lines += [
            f"- solved: **{sol}** · below13: **{bel}** · climbed≥18: "
            f"**{climb}/{len(ps)}** · best minL: **{best}**",
            "",
        ]
    lines += [
        "## Inspiration map (proofs → experiment)",
        "",
        "- orbit-2 / aut_min-14 starts ← AK3 census + proofs floor structure",
        "- dual_src_* ← `AK3_DUAL_SOURCE_COMPRESSION` endpoint on `codex/proofs`",
        "- cov_hop z=Xy ← height-17 bridge certificate (ORBIT2_CERTIFICATE)",
        "- climbed≥18 metric ← closed ≤17 component lower bound",
        "- relabels at full depth ← EXP-17 / diversity lesson",
        "",
        "Proofs branch untouched.",
        "",
    ]
    open(RESULTS, "w").write("\n".join(lines) + "\n")


def phase_starts_arms():
    done = _done(("phase", "start", "arm", "budget"))
    n_new = 0
    # Priority: orbit2/aut14/dual at all budgets; ak3 at 10k only first pass
    order = []
    for b in BUDGETS:
        for s, r1, r2 in STARTS:
            for arm in ("s20", "recommended", "length", "s12", "mk8", "k8"):
                order.append((s, r1, r2, arm, b))
    for s, r1, r2, arm, b in order:
        if _remaining() < 120:
            return n_new
        key = ("starts_x_arms", s, arm, b)
        if key in done:
            continue
        try:
            res = _search(r1, r2, b, ARMS[arm])
        except TimeoutError as e:
            _append(JSONL, {"phase": "starts_x_arms", "start": s, "arm": arm,
                            "budget": b, "error": str(e), "ts": _iso()})
            return n_new
        row = {"phase": "starts_x_arms", "start": s, "arm": arm,
               "r1": r1, "r2": r2, "ts": _iso(), **res}
        _append(JSONL, row)
        done.add(key)
        n_new += 1
        flag = ""
        if res["solved"] or res["below13"]:
            flag = " *** TRIPWIRE"
        elif res["climbed_ge18"]:
            flag = " [climbed≥18]"
        if n_new % 3 == 0 or flag:
            print(f"  [A] {s}/{arm}/b{b} minL={res['min_relator_length']} "
                  f"exp={res['max_expanded']}{flag}", flush=True)
    return n_new


def _apply_cov_y_to_xy(r1, r2):
    """φ: y ↦ xy  (elementary Nielsen; ORBIT2 certificate seed)."""
    def sub(w):
        out = []
        for c in w:
            if c == "Y":
                out.append("XY")
            elif c == "y":
                out.append("yx")  # (xy)^{-1} = y^{-1} x^{-1}
            else:
                out.append(c)
        return "".join(out)
    return sub(r1), sub(r2)


def phase_cov_hop():
    done = _done(("phase", "start", "arm", "budget", "hop"))
    n_new = 0
    bases = [s for s in STARTS if s[0] in ("ak3_classic", "ak3_canon", "orbit2")]
    for s, r1, r2 in bases:
        h1, h2 = _apply_cov_y_to_xy(r1, r2)
        for arm in ("s20", "recommended", "length"):
            for b in BUDGETS:
                if _remaining() < 120:
                    return n_new
                key = ("cov_hop", s, arm, b, "y_to_xy")
                if key in done:
                    continue
                try:
                    res = _search(h1, h2, b, ARMS[arm])
                except TimeoutError as e:
                    _append(JSONL, {"phase": "cov_hop", "error": str(e),
                                    "ts": _iso()})
                    return n_new
                row = {"phase": "cov_hop", "start": s, "hop": "y_to_xy",
                       "arm": arm, "r1": h1, "r2": h2, "ts": _iso(), **res}
                _append(JSONL, row)
                done.add(key)
                n_new += 1
                print(f"  [C] hop {s}/{arm}/b{b} minL={res['min_relator_length']} "
                      f"exp={res['max_expanded']} climbed={res['climbed_ge18']}",
                      flush=True)
    return n_new


def phase_relabel_full():
    """8-ish relabels × s20 @10k on orbit2 — full budget each (no split)."""
    done = _done(("phase", "start", "relabel", "arm", "budget"))
    n_new = 0
    r1, r2 = "YYXXyx", "YYYxyXX"
    # expand RELABELS with a few more Aut generators
    more = RELABELS + [
        ("inv_swap", lambda a, b: (_inv(b), _inv(a))),
        ("x2Y", lambda a, b: (_mapxy(a, "x", "Y", "X", "y"),
                              _mapxy(b, "x", "Y", "X", "y"))),
        ("y2X", lambda a, b: (_mapxy(a, "Y", "x", "y", "X"),
                              _mapxy(b, "Y", "x", "y", "X"))),
        ("rev", lambda a, b: (a[::-1], b[::-1])),
    ]
    for name, fn in more:
        a, b = fn(r1, r2)
        for arm in ("s20", "recommended"):
            for budget in (10_000,):
                if _remaining() < 120:
                    return n_new
                key = ("relabel_full", "orbit2", name, arm, budget)
                if key in done:
                    continue
                try:
                    res = _search(a, b, budget, ARMS[arm])
                except TimeoutError as e:
                    _append(JSONL, {"phase": "relabel_full", "error": str(e),
                                    "ts": _iso()})
                    return n_new
                row = {"phase": "relabel_full", "start": "orbit2",
                       "relabel": name, "arm": arm, "r1": a, "r2": b,
                       "ts": _iso(), **res}
                _append(JSONL, row)
                done.add(key)
                n_new += 1
                print(f"  [D] relabel {name}/{arm} minL={res['min_relator_length']} "
                      f"climbed={res['climbed_ge18']}", flush=True)
    return n_new


def phase_extra_hops():
    """More CoV seeds at the floor (z in {Xy, xy, yX, xY})."""
    done = _done(("phase", "start", "arm", "budget", "hop"))
    n_new = 0

    def sub_gen(z_pos, z_neg):
        def sub(w):
            out = []
            for c in w:
                if c == "Y":
                    out.append(z_pos)
                elif c == "y":
                    out.append(z_neg)
                else:
                    out.append(c)
            return "".join(out)
        return sub

    hops = {
        "y_to_xy": sub_gen("XY", "yx"),
        "y_to_yx": sub_gen("YX", "xy"),
        "y_to_xY": sub_gen("Xy", "Yx"),
        "y_to_Xy": sub_gen("xY", "yX"),
    }
    for s, r1, r2 in STARTS[:3]:
        for hop, fn in hops.items():
            h1, h2 = fn(r1), fn(r2)
            for arm in ("s20", "recommended"):
                for b in (5000, 10_000):
                    if _remaining() < 120:
                        return n_new
                    key = ("cov_hop", s, arm, b, hop)
                    if key in done:
                        continue
                    try:
                        res = _search(h1, h2, b, ARMS[arm])
                    except TimeoutError as e:
                        _append(JSONL, {"phase": "cov_hop", "error": str(e),
                                        "ts": _iso()})
                        return n_new
                    row = {"phase": "cov_hop", "start": s, "hop": hop,
                           "arm": arm, "r1": h1, "r2": h2, "ts": _iso(), **res}
                    _append(JSONL, row)
                    done.add(key)
                    n_new += 1
                    if res["climbed_ge18"] or res["below13"] or res["solved"]:
                        print(f"  [C+] {s}/{hop}/{arm}/b{b} minL="
                              f"{res['min_relator_length']} exp="
                              f"{res['max_expanded']}", flush=True)
    return n_new


def phase_cap64_focus():
    """Cap 64 on the most promising starts (EXP-12 parity for hard class)."""
    done = _done(("phase", "start", "arm", "budget", "cap"))
    n_new = 0
    focus = [s for s in STARTS if s[0] in
             ("orbit2", "aut14_a", "dual_src_wh", "ak3_canon")]
    for s, r1, r2 in focus:
        for arm in ("s20", "recommended", "length"):
            for b in (10_000,):
                if _remaining() < 120:
                    return n_new
                key = ("cap64", s, arm, b, 64)
                if key in done:
                    continue
                try:
                    res = _search(r1, r2, b, ARMS[arm], cap=64)
                except TimeoutError as e:
                    _append(JSONL, {"phase": "cap64", "error": str(e),
                                    "ts": _iso()})
                    return n_new
                row = {"phase": "cap64", "start": s, "arm": arm,
                       "r1": r1, "r2": r2, "ts": _iso(), **res}
                # also key field for done
                row["cap_key"] = 64
                _append(JSONL, row)
                done.add(key)
                n_new += 1
                print(f"  [cap64] {s}/{arm} minL={res['min_relator_length']} "
                      f"climbed={res['climbed_ge18']}", flush=True)
    return n_new


def main():
    write_plan()
    greedy_search_hcompact("X", "Y", 50, max_relator_length=48,
                           config=ARMS["s20"], reserve_states=5000)
    print(f"[ak3-insp] remain={_remaining()/3600:.2f}h out={OUT_DIR}", flush=True)
    phases = [
        ("starts_x_arms", phase_starts_arms),
        ("cov_hop", phase_cov_hop),
        ("relabel_full", phase_relabel_full),
        ("extra_hops", phase_extra_hops),
        ("cap64", phase_cap64_focus),
    ]
    round_i = 0
    while _remaining() > 180:
        round_i += 1
        total_new = 0
        for name, fn in phases:
            if _remaining() < 180:
                break
            print(f"\n=== ak3 round {round_i} phase={name} "
                  f"remain={_remaining()/3600:.2f}h ===", flush=True)
            n = fn()
            total_new += n
            write_results()
            open(STATE, "w").write(json.dumps({
                "phase": name, "round": round_i,
                "remaining_h": _remaining() / 3600,
                "updated": _iso(),
            }, indent=2) + "\n")
            print(f"  phase {name} new={n}", flush=True)
        if total_new == 0:
            print("[ak3-insp] matrix complete; holding", flush=True)
            write_results()
            time.sleep(min(300, max(0, _remaining() - 60)))
    write_results()
    print("[ak3-insp] wall shared end", flush=True)


if __name__ == "__main__":
    main()
