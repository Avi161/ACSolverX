"""12 h anti-overfit heuristic campaign (advisor-rescoped evaluation-only).

Phases
------
A. Build MS exclusion set; stream-sample never-read AC1M rows.
B. Screen with length-only at budget 1000 / cap 48 (pre-registered denominator).
C. Go/no-go: if a hard/separating band exists, score pre-registered arms once.
D. Optional expected-null on Aut-class counts for ms640 clean band.
E. Keep expanding the screen until WALL_END.

No weight fitting. Unsolved ACA reps are never used for selection.

    python3 -m experiments.heuristic_search.runners.campaign_12h_anti_overfit
"""
from __future__ import annotations

import ast
import csv
import gzip
import json
import os
import random
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hfast import search_fast  # noqa: E402
from experiments.heuristic_search.core.hsolve import (  # noqa: E402
    RECOMMENDED, LENGTH_ONLY,
)
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results/heuristic_search/campaign_12h")
SCREEN_JSONL = os.path.join(OUT_DIR, "screen_length_ac1m.jsonl")
ARMS_JSONL = os.path.join(OUT_DIR, "arms_on_band.jsonl")
NULL_JSONL = os.path.join(OUT_DIR, "aut_disjoint_null.jsonl")
RESULTS_MD = os.path.join(OUT_DIR, "RESULTS.md")
STATE_JSON = os.path.join(OUT_DIR, "state.json")

BUDGET = 1_000
CAP = 48
WALL_END = datetime(2026, 7, 29, 14, 1, 44, tzinfo=timezone.utc)
SEED = 20260729

# subset-60 pinned means (reporting arm only; not re-fit on AC1M)
MU_K, MU_MK, MU_S = 4.533333333333333, 2.6, 1.09

_SYM = {1: "x", -1: "X", 2: "y", -2: "Y"}


def _now():
    return datetime.now(timezone.utc)


def _remaining_s():
    return (WALL_END - _now()).total_seconds()


def _to_words(flat):
    half = len(flat) // 2
    return ("".join(_SYM[v] for v in flat[:half] if v != 0),
            "".join(_SYM[v] for v in flat[half:] if v != 0))


def _parse_line(line):
    flat = ast.literal_eval(line.strip())
    if not isinstance(flat, (list, tuple)):
        raise ValueError("bad line")
    return [int(v) for v in flat]


def _pair_key(r1, r2):
    a, b = (r1, r2) if (r1, r2) <= (r2, r1) else (r2, r1)
    return a + "\0" + b


def make_priority_length():
    return LENGTH_ONLY


def make_priority_mk8():
    return {"segments": [{"upto": None, "w": {"L": 1.0, "MK": 8.0}}]}


def make_priority_k8():
    return {"segments": [{"upto": None, "w": {"L": 1.0, "K": 8.0}}]}


def make_priority_s24():
    return {"segments": [{"upto": None, "w": {"L": 1.0, "S": 24.0}}]}


def make_priority_kms5():
    # Encode equal-proportion as explicit weights w_f = α/μ_f with α=5
    return {"segments": [{"upto": None, "w": {
        "L": 1.0,
        "K": 5.0 / MU_K,
        "MK": 5.0 / MU_MK,
        "S": 5.0 / MU_S,
    }}]}


ARMS = {
    "length": make_priority_length(),
    "recommended": RECOMMENDED,
    "mk8": make_priority_mk8(),
    "k8": make_priority_k8(),
    "kms5": make_priority_kms5(),
    "s24": make_priority_s24(),
}


def _search(r1, r2, config):
    res = search_fast(r1, r2, BUDGET, config, CAP)
    # normalize to nodes_explored alias used below
    return {
        "solved": bool(res["solved"]),
        "nodes_explored": int(res["nodes"]),
        "path_length": res["path_length"],
        "min_total": res.get("min_total"),
    }


def _load_done(path, key_fields):
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            seen.add(tuple(r[k] for k in key_fields))
    return seen


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def build_ms_exclusion():
    """String-pair keys from MS solved/unsolved tables — exclude from AC1M 'never-read'."""
    keys = set()
    paths = [
        os.path.join(ROOT, "data/ms640_solved.txt"),
        os.path.join(ROOT, "data/1190MS.txt"),
    ]
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                flat = _parse_line(line) if line[0] in "[(" else None
                if flat is None:
                    continue
                r1, r2 = _to_words(flat)
                keys.add(_pair_key(r1, r2))
    # unsolved ACA string forms
    u = os.path.join(ROOT, "results/equivalence_classes/ms1190_tables/unsolved_124_aca_classes.csv")
    if os.path.exists(u):
        with open(u) as f:
            for r in csv.DictReader(f):
                keys.add(_pair_key(r["r1"], r["r2"]))
    # solved aut orbits
    s = os.path.join(ROOT, "results/equivalence_classes/ms1190_tables/solved_640_aut_orbits.csv")
    if os.path.exists(s):
        with open(s) as f:
            for r in csv.DictReader(f):
                keys.add(_pair_key(r["rep_r1"], r["rep_r2"]))
    return keys


def iter_ac1m(exclude, rng, max_yield=None):
    """Reservoir-ish random sample via stride from a seeded start."""
    path = os.path.join(ROOT, "data/AC1M.txt.gz")
    # deterministic subsample: take lines where hash matches
    n_out = 0
    with gzip.open(path, "rt") as f:
        for idx, line in enumerate(f):
            if _remaining_s() <= 0:
                break
            # ~1/50 of file ≈ 22k candidates before exclude; adjust with rng
            if (idx * 2654435761 + SEED) % 47 != 0:
                continue
            try:
                flat = _parse_line(line)
            except Exception:
                continue
            r1, r2 = _to_words(flat)
            if not r1 or not r2:
                continue
            if _pair_key(r1, r2) in exclude:
                continue
            L = len(r1) + len(r2)
            if L < 8 or L > 40:
                continue
            yield idx, r1, r2, L
            n_out += 1
            if max_yield is not None and n_out >= max_yield:
                return


def phase_screen(exclude, target_n=8000):
    done = _load_done(SCREEN_JSONL, ("src", "idx"))
    print(f"[screen] resume {len(done)} done; target {target_n}", flush=True)
    rng = random.Random(SEED)
    n_new = 0
    t0 = time.time()
    for idx, r1, r2, L in iter_ac1m(exclude, rng):
        if _remaining_s() <= 120:
            print("[screen] wall almost up — stop screen", flush=True)
            break
        key = ("ac1m", idx)
        if key in done:
            continue
        res = _search(r1, r2, ARMS["length"])
        row = {
            "src": "ac1m",
            "idx": idx,
            "r1": r1,
            "r2": r2,
            "L": L,
            "arm": "length",
            "solved": bool(res["solved"]),
            "nodes": int(res["nodes_explored"]),
            "path": int(res["path_length"]) if res["solved"] else None,
            "budget": BUDGET,
            "cap": CAP,
            "ts": _now().isoformat(),
        }
        if int(res["nodes_explored"]) > BUDGET:
            raise RuntimeError(f"budget exceeded idx={idx}")
        _append(SCREEN_JSONL, row)
        done.add(key)
        n_new += 1
        if n_new % 50 == 0:
            rate = n_new / max(time.time() - t0, 1e-6)
            print(f"  [screen] +{n_new} ({len(done)} total) {rate:.2f}/s "
                  f"remain={_remaining_s()/3600:.2f}h", flush=True)
        if len(done) >= target_n:
            break
    return len(done)


def _read_screen():
    rows = []
    if not os.path.exists(SCREEN_JSONL):
        return rows
    with open(SCREEN_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def pick_band(screen_rows):
    """Pre-registered band definition (length-only only):

    - hard: unsolved at budget 1000
    - mid: solved with nodes in [100, 1000)
    Separating interest = mid (both arms can move) ∪ a capped sample of hard for reporting.
    """
    mid = [r for r in screen_rows if r["solved"] and 100 <= r["nodes"] < BUDGET]
    hard = [r for r in screen_rows if not r["solved"]]
    easy = [r for r in screen_rows if r["solved"] and r["nodes"] < 100]
    # deterministic order
    mid.sort(key=lambda r: (r["nodes"], r["idx"]))
    hard.sort(key=lambda r: r["idx"])
    return {"easy": easy, "mid": mid, "hard": hard}


def phase_arms(band, max_mid=400, max_hard_report=50):
    """Score all pre-registered arms once on mid band (+ small hard report set)."""
    done = _load_done(ARMS_JSONL, ("arm", "src", "idx"))
    targets = band["mid"][:max_mid] + band["hard"][:max_hard_report]
    print(f"[arms] {len(targets)} targets; {len(done)} cells done", flush=True)
    n_new = 0
    t0 = time.time()
    for rec in targets:
        if _remaining_s() <= 180:
            print("[arms] wall almost up", flush=True)
            break
        for arm_name, cfg in ARMS.items():
            key = (arm_name, rec["src"], rec["idx"])
            if key in done:
                continue
            res = _search(rec["r1"], rec["r2"], cfg)
            row = {
                "arm": arm_name,
                "src": rec["src"],
                "idx": rec["idx"],
                "r1": rec["r1"],
                "r2": rec["r2"],
                "L": rec["L"],
                "band": "mid" if rec["solved"] else "hard",
                "length_nodes": rec["nodes"],
                "length_solved": rec["solved"],
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "path": int(res["path_length"]) if res["solved"] else None,
                "budget": BUDGET,
                "cap": CAP,
                "ts": _now().isoformat(),
            }
            if int(res["nodes_explored"]) > BUDGET:
                raise RuntimeError("budget exceeded")
            _append(ARMS_JSONL, row)
            done.add(key)
            n_new += 1
            if n_new % 20 == 0:
                print(f"  [arms] +{n_new} remain={_remaining_s()/3600:.2f}h "
                      f"{n_new/max(time.time()-t0,1e-6):.2f}/s", flush=True)
    return len(done)


def phase_aut_null():
    """Expected-null: on ms640 clean bins 4-7 never-seen, count distinct Aut proxies
    via aut_class from difficulty if present; score length vs recommended only.
    """
    from experiments.heuristic_search.exp.exp26_clean_holdout import clean_rows
    rows = clean_rows()
    done = _load_done(NULL_JSONL, ("arm", "name"))
    print(f"[null] {len(rows)} clean ms640 rows; {len(done)} done", flush=True)
    for rec in rows:
        if _remaining_s() <= 300:
            break
        for arm_name in ("length", "recommended", "mk8", "kms5"):
            key = (arm_name, rec["name"])
            if key in done:
                continue
            res = _search(rec["r1"], rec["r2"], ARMS[arm_name])
            row = {
                "arm": arm_name,
                "name": rec["name"],
                "pres_id": rec["pres_id"],
                "bin": rec["bin"],
                "r1": rec["r1"],
                "r2": rec["r2"],
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "path": int(res["path_length"]) if res["solved"] else None,
                "budget": BUDGET,
                "cap": CAP,
                "ts": _now().isoformat(),
            }
            _append(NULL_JSONL, row)
            done.add(key)
    return len(done)


def write_results_md():
    screen = _read_screen()
    band = pick_band(screen)
    arms = []
    if os.path.exists(ARMS_JSONL):
        with open(ARMS_JSONL) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    arms.append(json.loads(line))
                except ValueError:
                    continue

    lines = [
        "# Campaign 12h — anti-overfit heuristic evaluation",
        "",
        f"Updated: `{_now().isoformat()}` · wall end `{WALL_END.isoformat()}` · "
        f"remaining `{max(_remaining_s(),0)/3600:.2f} h`",
        "",
        "Advisor **BLOCK**ed fitting on the CoV/automorphic unsolved-descended pool; "
        "this run is **evaluation-only** on never-read AC1M (+ ms640 clean null), "
        "budget 1000, cap 48. Negatives mean unsolved within budget 1000.",
        "",
        "## Screen (length-only denominator)",
        "",
        f"- Screened rows: **{len(screen)}**",
        f"- Easy (solved <100 nodes): {len(band['easy'])}",
        f"- Mid (solved 100–999 nodes): {len(band['mid'])}",
        f"- Hard (unsolved at 1000): {len(band['hard'])}",
        "",
    ]
    if screen:
        sol = sum(1 for r in screen if r["solved"])
        lines.append(f"- Solve rate @1000: **{sol}/{len(screen)}** "
                     f"({100*sol/len(screen):.1f}%)")
        lines.append("")

    # go/no-go
    sep = band["mid"]
    lines.extend([
        "## Go / no-go (dynamic range)",
        "",
        f"Mid-band size (length-only solved in [100,1000)): **{len(sep)}**.",
        "",
    ])
    if len(sep) < 20:
        lines.append(
            "**NO-GO for fitting** — mid-band too thin to select weights. "
            "Continue evaluation-only reporting only.")
    else:
        lines.append(
            "**GO for evaluation** — mid-band large enough to compare "
            "pre-registered arms (still no fitting).")
    lines.append("")

    # arm table on mid
    mid_idx = {r["idx"] for r in band["mid"]}
    lines.extend(["## Pre-registered arms on mid-band", ""])
    lines.append("| arm | solved | n | mean nodes (solved) |")
    lines.append("|---|---:|---:|---:|")
    for arm_name in ARMS:
        cells = [a for a in arms if a["arm"] == arm_name and a["idx"] in mid_idx
                 and a.get("band") == "mid"]
        # also accept band inferred
        if not cells:
            cells = [a for a in arms if a["arm"] == arm_name and a["idx"] in mid_idx]
        if not cells:
            lines.append(f"| `{arm_name}` | — | 0 | — |")
            continue
        sol = [a for a in cells if a["solved"]]
        mean_n = (sum(a["nodes"] for a in sol) / len(sol)) if sol else None
        mean_s = f"{mean_n:.1f}" if mean_n is not None else "—"
        lines.append(f"| `{arm_name}` | **{len(sol)}/{len(cells)}** | "
                     f"{len(cells)} | {mean_s} |")
    lines.append("")

    # pairwise vs length on same mid rows
    length_by = {(a["src"], a["idx"]): a for a in arms if a["arm"] == "length"}
    lines.extend(["## Matched mid-band: vs length-only", ""])
    for arm_name in ARMS:
        if arm_name == "length":
            continue
        better = worse = same = 0
        for a in arms:
            if a["arm"] != arm_name or a["idx"] not in mid_idx:
                continue
            b = length_by.get((a["src"], a["idx"]))
            if not b:
                continue
            # compare solve first, then nodes if both solved
            if a["solved"] and not b["solved"]:
                better += 1
            elif b["solved"] and not a["solved"]:
                worse += 1
            elif a["solved"] and b["solved"]:
                if a["nodes"] < b["nodes"]:
                    better += 1
                elif a["nodes"] > b["nodes"]:
                    worse += 1
                else:
                    same += 1
            else:
                same += 1
        lines.append(
            f"- `{arm_name}` vs length: better {better} / worse {worse} / "
            f"same {same}")
    lines.append("")

    lines.extend([
        "## Method notes",
        "",
        "- Denominator fixed by length-only screen before any other arm.",
        "- AC1M rows excluding exact string pairs from ms640 / 1190MS / "
        "solved-aut / unsolved-124 tables.",
        "- No unsolved ACA reps used for selection (there is no selection).",
        "- See [`PLAN.md`](PLAN.md).",
        "",
    ])
    with open(RESULTS_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {RESULTS_MD}", flush=True)


def save_state(**kw):
    st = {}
    if os.path.exists(STATE_JSON):
        with open(STATE_JSON) as f:
            st = json.load(f)
    st.update(kw)
    st["updated"] = _now().isoformat()
    st["remaining_h"] = max(_remaining_s(), 0) / 3600
    with open(STATE_JSON, "w") as f:
        json.dump(st, f, indent=2)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"WALL_END={WALL_END.isoformat()} remaining_h={_remaining_s()/3600:.2f}",
          flush=True)
    # control: length config present
    assert "length" in ARMS

    print("[init] building MS exclusion set…", flush=True)
    exclude = build_ms_exclusion()
    print(f"[init] exclusion keys={len(exclude)}", flush=True)
    save_state(phase="screen", exclude_n=len(exclude))

    # Warm JIT
    _search("X", "Y", ARMS["length"])

    # Phase loop until wall
    round_i = 0
    while _remaining_s() > 600:
        round_i += 1
        print(f"\n=== round {round_i} remain={_remaining_s()/3600:.2f}h ===",
              flush=True)
        # expand screen
        target = 2000 + round_i * 1500
        n = phase_screen(exclude, target_n=target)
        save_state(phase="screen_done", screen_n=n, round=round_i)
        write_results_md()

        band = pick_band(_read_screen())
        print(f"[band] easy={len(band['easy'])} mid={len(band['mid'])} "
              f"hard={len(band['hard'])}", flush=True)

        if band["mid"] or band["hard"]:
            phase_arms(band, max_mid=min(500, max(50, len(band["mid"]))),
                       max_hard_report=min(80, len(band["hard"])))
            save_state(phase="arms", round=round_i)
            write_results_md()

        # periodic null on clean ms640 (cheap relative)
        if round_i == 1 or _remaining_s() > 3600:
            phase_aut_null()
            save_state(phase="null", round=round_i)
            write_results_md()

        if _remaining_s() < 900:
            break

    write_results_md()
    save_state(phase="done")
    print("campaign loop exit", flush=True)


if __name__ == "__main__":
    main()
