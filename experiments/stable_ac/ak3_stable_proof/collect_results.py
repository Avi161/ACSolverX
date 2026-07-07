"""Collect + consolidate the AK(3) stable-proof campaign results into ONE report.

Scans a Drive/results root that holds one subdir per box and aggregates every stream
into a single machine-readable summary + a human COLLECTED_RESULTS.md:

  <root>/D1/laneD/{merged.jsonl,solve.jsonl,certs/*.json}   Lane D, textbook+p25
  <root>/D2/laneD/{...}                                     Lane D, rep+floorF
  <root>/D3/laneD/{...}                                     Lane D, full word bank
  <root>/B/box_B*.jsonl   <root>/C/box_C*.jsonl             grid probes (solved/hit)
  <root>/resolve_hiL/resolve_L*.jsonl                       high-L cap-gap re-solve
  <root>/*/laneD/floor_census.jsonl                         two-floors census (optional)

Pure stdlib (json/os/argparse/collections) — runs on a bare Colab or locally, no numba.
Read-only + resumable-safe: tolerates a truncated trailing JSONL line, skips missing
files/boxes. The HEADLINE is the campaign verdict: any `solved:true` anywhere (with its
cert path) = the theorem; otherwise the certified negative + the length-13 floor.

It also writes a consolidated ARCHIVE under <root>/archive/ — the full per-record
datasets (every relator tested, its node budget, cap, and outcome) + a MANIFEST, so the
result is a reusable dataset, not just a headline. --no_archive skips it; --gzip zips it.

Usage:
  python collect_results.py --root /content/drive/MyDrive/ak3_stable_proof \
      --out /content/drive/MyDrive/ak3_stable_proof/COLLECTED_RESULTS.md
  python collect_results.py --selftest      # fabricate a fixture, assert the math
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

LANE_D_BOXES = ["D1", "D2", "D3"]
GRID_BOXES = ["B", "C"]


def read_jsonl(path):
    """Yield parsed records; silently drop a truncated/corrupt trailing line."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # a crash mid-write leaves at most one bad (last) line — ignore it
                continue


def count_lines(path):
    return sum(1 for _ in read_jsonl(path))


def hist(counter, top=None):
    """Sorted [(key, n)] by key; optionally only the `top` smallest keys."""
    items = sorted(counter.items())
    return items[:top] if top else items


def collect_lane_d(box_dir):
    """Aggregate one Lane-D box's laneD/ dir. Returns a stats dict (or None if absent)."""
    laneD = os.path.join(box_dir, "laneD")
    if not os.path.isdir(laneD):
        return None
    merged = os.path.join(laneD, "merged.jsonl")
    solve = os.path.join(laneD, "solve.jsonl")
    certs_dir = os.path.join(box_dir, "certs")

    combos = sorted(f for f in os.listdir(laneD)
                    if f.startswith("cands_") and f.endswith(".jsonl"))
    merged_mkeys = set()
    merged_tl = Counter()
    for rec in read_jsonl(merged):
        mk = rec.get("mkey") or rec.get("cand")
        if mk is not None:
            merged_mkeys.add(mk)
        if "total_len" in rec:
            merged_tl[int(rec["total_len"])] += 1

    attempted = 0
    solved = []
    floor = Counter()          # min_total_len histogram — the plateau
    attempted_mkeys = set()
    for rec in read_jsonl(solve):
        attempted += 1
        mk = rec.get("mkey")
        if mk is not None:
            attempted_mkeys.add(mk)
        if "min_total_len" in rec:
            floor[int(rec["min_total_len"])] += 1
        if rec.get("solved"):
            solved.append(rec)

    cert_files = []
    if os.path.isdir(certs_dir):
        cert_files = sorted(f for f in os.listdir(certs_dir)
                            if f.startswith("laneD_") and f.endswith(".json"))

    return {
        "kind": "laneD",
        "combos_done": len(combos),
        "merged_unique": len(merged_mkeys),
        "merged_mkeys": merged_mkeys,
        "merged_tl_hist": dict(merged_tl),
        "attempted": attempted,
        "attempted_mkeys": attempted_mkeys,
        "solved_count": len(solved),
        "solved_recs": solved,
        "floor_hist": dict(floor),
        "cert_files": cert_files,
    }


def collect_grid(box_dir, box):
    """Aggregate a B/C grid box (box_*.jsonl). Returns stats or None."""
    if not os.path.isdir(box_dir):
        return None
    files = sorted(f for f in os.listdir(box_dir)
                   if f.startswith(f"box_{box}") and f.endswith(".jsonl")
                   and "_quick" not in f)
    if not files:
        return None
    probes, solved_or_hit = 0, []
    for fn in files:
        for rec in read_jsonl(os.path.join(box_dir, fn)):
            probes += 1
            if rec.get("solved") or rec.get("hit"):
                solved_or_hit.append(rec)
    return {"kind": "grid", "files": files, "probes": probes,
            "solved_or_hit": solved_or_hit}


def collect_resolve(root):
    """Aggregate resolve_hiL/resolve_L*.jsonl (the high-L cap-gap probe)."""
    rdir = os.path.join(root, "resolve_hiL")
    if not os.path.isdir(rdir):
        return None
    files = sorted(f for f in os.listdir(rdir)
                   if f.startswith("resolve_L") and f.endswith(".jsonl"))
    arms = {}
    for fn in files:
        L = fn[len("resolve_L"):-len(".jsonl")]
        attempted, solved = 0, []
        maxrel = Counter()      # longest-relator-at-peak histogram: is the cap used?
        floor = Counter()
        for rec in read_jsonl(os.path.join(rdir, fn)):
            attempted += 1
            if "max_rel_len" in rec:
                maxrel[int(rec["max_rel_len"])] += 1
            if "min_total_len" in rec:
                floor[int(rec["min_total_len"])] += 1
            if rec.get("solved"):
                solved.append(rec)
        arms[L] = {"file": fn, "attempted": attempted, "solved_count": len(solved),
                   "solved_recs": solved, "maxrel_hist": dict(maxrel),
                   "floor_hist": dict(floor)}
    return arms or None


def collect_floor_census(root):
    """Union floor_census.jsonl across boxes -> {floor_mkey: count} (two-floors)."""
    tally = Counter()
    seen_mkeys = set()
    found = False
    for box in LANE_D_BOXES:
        path = os.path.join(root, box, "laneD", "floor_census.jsonl")
        for rec in read_jsonl(path):
            found = True
            mk = rec.get("mkey")
            fk = rec.get("floor_mkey") or rec.get("floor_key")
            if mk is not None and mk in seen_mkeys:
                continue          # dedup: same start quotient counted once
            if mk is not None:
                seen_mkeys.add(mk)
            if fk is not None:
                tally[fk] += 1
    return dict(tally) if found else None


# ---------------------------------------------------------------------------
# Consolidated ARCHIVE — the reusable per-record dataset (not just the summary).
# Two streams so a future attempt can look up "was this quotient already tested?"
# and skip it instead of burning compute:
#   campaign_candidates.jsonl  one row per DISTINCT reachable quotient (relators +
#                              provenance), attempted or not — the quotient pool.
#   campaign_trials.jsonl      one row per solve ATTEMPT (relators, budget, cap L,
#                              nodes, solved, min_total_len, max_rel_lens, and the
#                              full path on a solve) — the "we ran this" record.
# ---------------------------------------------------------------------------

CAND_FIELDS = ("mkey", "relators", "total_len", "form", "word", "gen", "ri", "src")
TRIAL_FIELDS = ("mkey", "relators", "total_len", "budget", "L", "solved", "nodes",
                "min_total_len", "max_rel_len", "max_rel_lens", "wall_s",
                "form", "word", "gen", "ri", "src", "path_verified")


def _open_out(path, gzip_out):
    if gzip_out:
        import gzip
        return gzip.open(path + ".gz", "wt"), path + ".gz"
    return open(path, "w"), path


def emit_archive(root, archive_dir, gzip_out=False):
    """Write consolidated candidate + trial JSONL + a MANIFEST. Returns a counts dict."""
    os.makedirs(archive_dir, exist_ok=True)

    # ---- candidates: union all merged.jsonl, dedup by mkey (keep shortest form) ----
    cands = {}
    for box in LANE_D_BOXES:
        merged = os.path.join(root, box, "laneD", "merged.jsonl")
        for rec in read_jsonl(merged):
            mk = rec.get("mkey") or rec.get("cand")
            if mk is None:
                continue
            cur = cands.get(mk)
            if cur is None:
                row = {k: rec.get(k) for k in CAND_FIELDS}
                row["mkey"] = mk
                row["source_boxes"] = [box]
                cands[mk] = row
            else:
                if box not in cur["source_boxes"]:
                    cur["source_boxes"].append(box)
                tl = rec.get("total_len")
                if tl is not None and (cur.get("total_len") is None
                                       or tl < cur["total_len"]):
                    row = {k: rec.get(k) for k in CAND_FIELDS}
                    row["mkey"] = mk
                    row["source_boxes"] = cur["source_boxes"]
                    cands[mk] = row
    cpath = os.path.join(archive_dir, "campaign_candidates.jsonl")
    fh, cpath_w = _open_out(cpath, gzip_out)
    with fh as f:
        for mk in sorted(cands):
            f.write(json.dumps(cands[mk]) + "\n")

    # ---- trials: every solve attempt (Lane-D solve.jsonl + resolve_L*.jsonl) ----
    tpath = os.path.join(archive_dir, "campaign_trials.jsonl")
    fh, tpath_w = _open_out(tpath, gzip_out)
    n_trials, n_solved, seen = 0, 0, set()

    def _emit_trial(f, rec, source, default_L):
        nonlocal n_trials, n_solved
        key = (rec.get("mkey"), rec.get("budget"), rec.get("L", default_L), source)
        if key in seen:
            return
        seen.add(key)
        row = {k: rec.get(k) for k in TRIAL_FIELDS if k in rec}
        row["source"] = source
        row.setdefault("L", default_L)      # Lane-D solve ran at the gn.L=24 cap
        if rec.get("solved") and "path_states" in rec:
            row["path_states"] = rec["path_states"]
            n_solved += 1
        f.write(json.dumps(row) + "\n")
        n_trials += 1

    with fh as f:
        for box in LANE_D_BOXES:
            solve = os.path.join(root, box, "laneD", "solve.jsonl")
            for rec in read_jsonl(solve):
                _emit_trial(f, rec, "laneD:" + box, 24)
        rdir = os.path.join(root, "resolve_hiL")
        if os.path.isdir(rdir):
            for fn in sorted(os.listdir(rdir)):
                if fn.startswith("resolve_L") and fn.endswith(".jsonl"):
                    for rec in read_jsonl(os.path.join(rdir, fn)):
                        _emit_trial(f, rec, "resolve", rec.get("L"))

    counts = {"candidates": len(cands), "trials": n_trials, "trials_solved": n_solved,
              "candidates_file": cpath_w, "trials_file": tpath_w}
    _write_manifest(archive_dir, counts, gzip_out)
    return counts


def _write_manifest(archive_dir, counts, gzip_out):
    ext = ".jsonl.gz" if gzip_out else ".jsonl"
    txt = f"""# AK(3) stable-proof campaign — data archive

Consolidated, deduplicated per-record datasets from the Lane-D plateau-elimination
campaign, so a future attempt can look up what was already tested instead of re-running
the same searches.

## Files

- `campaign_candidates{ext}` — {counts['candidates']:,} rows. One per DISTINCT reachable
  Lemma-11 quotient of the AK(3) stable class (deduped by symmetry key `mkey`; shortest
  form kept), whether or not it was solve-attempted. This is the quotient pool itself.
- `campaign_trials{ext}` — {counts['trials']:,} rows ({counts['trials_solved']} solved).
  One per solve ATTEMPT, with the full outcome.

## Schema — campaign_candidates{ext}

| field | meaning |
|---|---|
| `mkey` | symmetry-canonical id (min over 2^k·k! signed relabelings x per-relator rotate/invert/reorder); the dedup key |
| `relators` | the two relators as signed-int lists (x=1, y=2, x^-1=-1, y^-1=-2) |
| `total_len` | sum of relator lengths (trivial = 2) |
| `form`,`word`,`gen`,`ri`,`src` | provenance: which z=w stabilization + eliminated generator produced it |
| `source_boxes` | which box(es) harvested it (D1/D2/D3) |

## Schema — campaign_trials{ext}

| field | meaning |
|---|---|
| `mkey`,`relators`,`total_len` | the quotient tested (as above) |
| `source` | `laneD:D1/D2/D3` (cap L=24 greedy @ budget2) or `resolve` (high-L re-solve) |
| `budget` | node budget (max heap pops) the search was run to |
| `L` | per-relator length cap in effect (24 for Lane-D solve; 40+ for resolve) |
| `solved` | reached the trivial presentation |
| `nodes` | nodes actually expanded |
| `min_total_len` | shortest total length reached — the plateau floor if unsolved |
| `max_rel_lens`,`max_rel_len` | longest relator lengths at peak (resolve only) — cap-usage evidence |
| `path_states` | full solution state sequence (present only on `solved:true`) |

## Reuse

A quotient `mkey` with a `solved:false` trial at `budget >= B` and `L >= C` is a known
negative at that effort — attack it harder (bigger budget / cap / a different move set),
don't repeat it. Any `solved:true` row carries `path_states`: a machine-checkable
solution (verify with verify_certificate.py + independent_verifier.py).
"""
    with open(os.path.join(archive_dir, "MANIFEST.md"), "w") as f:
        f.write(txt)


def merge_counters(dicts):
    out = Counter()
    for d in dicts:
        for k, v in d.items():
            out[int(k)] += v
    return dict(out)


def build_summary(root):
    boxes = {}
    for box in LANE_D_BOXES:
        s = collect_lane_d(os.path.join(root, box))
        if s is not None:
            boxes[box] = s
    grids = {}
    for box in GRID_BOXES:
        s = collect_grid(os.path.join(root, box), box)
        if s is not None:
            grids[box] = s
    resolve = collect_resolve(root)
    census = collect_floor_census(root)

    # ---- union across Lane-D boxes (mkey is symmetry-canonical -> valid dedup) ----
    all_merged, all_attempted = set(), set()
    all_solved = []
    for box, s in boxes.items():
        all_merged |= s["merged_mkeys"]
        all_attempted |= s["attempted_mkeys"]
        for r in s["solved_recs"]:
            all_solved.append({"box": box, **r})
    union_floor = merge_counters([s["floor_hist"] for s in boxes.values()])

    resolve_solved = []
    if resolve:
        for L, a in resolve.items():
            for r in a["solved_recs"]:
                resolve_solved.append({"L": L, **r})
    grid_hits = []
    for box, s in grids.items():
        for r in s["solved_or_hit"]:
            grid_hits.append({"box": box, **r})

    total_solved = len(all_solved) + len(resolve_solved) + len(grid_hits)
    return {
        "root": os.path.abspath(root),
        "boxes": boxes,
        "grids": grids,
        "resolve": resolve,
        "census": census,
        "union": {
            "distinct_quotients": len(all_merged),
            "distinct_attempted": len(all_attempted),
            "floor_hist": union_floor,
            "lane_d_solved": all_solved,
        },
        "resolve_solved": resolve_solved,
        "grid_hits": grid_hits,
        "total_solved": total_solved,
        "theorem": total_solved > 0,
    }


def fmt_hist(h, top=None):
    if not h:
        return "(none)"
    items = sorted((int(k), v) for k, v in h.items())
    if top:
        items = items[:top]
    return "  ".join(f"{k}:{v}" for k, v in items)


def render_md(S):
    L = []
    w = L.append
    w("# AK(3) stable-proof campaign — collected results")
    w("")
    w(f"Root: `{S['root']}`")
    w("")
    # ---------- HEADLINE ----------
    if S["theorem"]:
        w("## ✅ HEADLINE: A SOLVE WAS FOUND — candidate theorem")
        w("")
        w(f"**{S['total_solved']} solved record(s) across the campaign.** "
          "Each must be confirmed by BOTH verifiers (verify_certificate.py + "
          "independent_verifier.py) before it counts. Solved records:")
        for r in S["union"]["lane_d_solved"]:
            w(f"- Lane D `{r['box']}` mkey=`{r.get('mkey','?')}` "
              f"form={r.get('form')} word={r.get('word')} total_len={r.get('total_len')}")
        for r in S["resolve_solved"]:
            w(f"- resolve L={r['L']} mkey=`{r.get('mkey','?')}` "
              f"form={r.get('form')} word={r.get('word')} "
              f"max_rel_lens={r.get('max_rel_lens')} verified={r.get('path_verified')}")
        for r in S["grid_hits"]:
            w(f"- grid `{r['box']}` {r.get('night_id','?')} "
              f"solved={r.get('solved')} hit={r.get('hit')}")
    else:
        w("## ❌ HEADLINE: certified negative — 0 solved")
        w("")
        uf = S["union"]["floor_hist"]
        floor_min = min(uf) if uf else None
        w(f"**0 solves across the entire campaign.** "
          f"{S['union']['distinct_quotients']:,} distinct Lemma-11 quotients harvested, "
          f"{S['union']['distinct_attempted']:,} attempted by greedy substitution — "
          f"all floor at min total length **{floor_min}** (trivial = 2).")
    w("")
    # ---------- Lane D per box ----------
    w("## Lane D (plateau elimination) — per box")
    w("")
    w("| box | combos | unique candidates | attempted | solved | certs |")
    w("|---|---|---|---|---|---|")
    for box in LANE_D_BOXES:
        s = S["boxes"].get(box)
        if not s:
            w(f"| {box} | — (not present) | | | | |")
            continue
        w(f"| {box} | {s['combos_done']} | {s['merged_unique']:,} | "
          f"{s['attempted']:,} | {s['solved_count']} | {len(s['cert_files'])} |")
    w("")
    w(f"**Union across D1/D2/D3:** {S['union']['distinct_quotients']:,} distinct "
      f"quotients (dedup by symmetry mkey), {S['union']['distinct_attempted']:,} "
      f"attempted, {len(S['union']['lane_d_solved'])} solved.")
    w("")
    w("**Floor (min_total_len) histogram, union of all attempts:**")
    w(f"`{fmt_hist(S['union']['floor_hist'])}`")
    w("")
    # ---------- resolve high-L ----------
    if S["resolve"]:
        w("## High-L cap-gap re-solve (resolve_hiL)")
        w("")
        w("Re-solves the shortest candidates at a raised per-relator cap to test whether "
          "the L=24 limit causes false negatives. `max_rel_len` = longest single relator "
          "reached; if it stays < 24 the cap was never the binding constraint.")
        w("")
        w("| arm (L) | attempted | solved | max_rel_len hist | floor hist |")
        w("|---|---|---|---|---|")
        for Lk in sorted(S["resolve"]):
            a = S["resolve"][Lk]
            w(f"| L={Lk} | {a['attempted']:,} | {a['solved_count']} | "
              f"`{fmt_hist(a['maxrel_hist'])}` | `{fmt_hist(a['floor_hist'])}` |")
        w("")
        # cap-usage verdict
        for Lk in sorted(S["resolve"]):
            a = S["resolve"][Lk]
            if a["maxrel_hist"]:
                mx = max(int(k) for k in a["maxrel_hist"])
                verdict = ("cap NOT the blocker — search never reached the old 24 limit"
                           if mx < 24 else
                           f"cap WAS pressed (max_rel_len up to {mx}) — headroom is load-bearing")
                w(f"- L={Lk}: peak relator length **{mx}** → {verdict}")
        w("")
    # ---------- grid boxes ----------
    if S["grids"]:
        w("## Grid probes (B/C)")
        w("")
        for box in GRID_BOXES:
            s = S["grids"].get(box)
            if s:
                w(f"- **{box}**: {s['probes']} probes, "
                  f"{len(s['solved_or_hit'])} solved/hit")
        w("")
    # ---------- floor census ----------
    if S["census"]:
        w("## Floor census (two-floors structure)")
        w("")
        total = sum(S["census"].values())
        w(f"{len(S['census'])} distinct floor classes over {total:,} quotients:")
        for fk, n in sorted(S["census"].items(), key=lambda kv: -kv[1])[:10]:
            pct = 100.0 * n / total if total else 0
            w(f"- `{fk[:24]}…` — {n:,} ({pct:.0f}%)")
        w("")
    # ---------- data archive ----------
    if S.get("archive"):
        a = S["archive"]
        w("## Data archive (reusable per-record datasets)")
        w("")
        w(f"- `{os.path.basename(a['candidates_file'])}` — {a['candidates']:,} distinct "
          "quotients (relators + provenance)")
        w(f"- `{os.path.basename(a['trials_file'])}` — {a['trials']:,} solve trials "
          f"({a['trials_solved']} solved; each row = relators + budget + cap + outcome)")
        w("- `MANIFEST.md` — full schema + reuse notes")
        w("")
        w("Every relator tested and the budget/cap it ran to is preserved here, so a "
          "future attempt can skip known negatives instead of recomputing them.")
        w("")
    w("---")
    w("*Generated by collect_results.py — read-only aggregation of the Drive result tree.*")
    return "\n".join(L) + "\n"


def _selftest():
    """Fabricate a tiny fixture tree, run collection, assert the aggregation math."""
    import tempfile
    import shutil
    d = tempfile.mkdtemp(prefix="collect_selftest_")
    try:
        # D1: 3 unique candidates, 2 attempted (1 shared mkey with D2), 0 solved
        laneD1 = os.path.join(d, "D1", "laneD")
        os.makedirs(laneD1)
        with open(os.path.join(laneD1, "cands_textbook_x.jsonl"), "w") as f:
            f.write('{"cand":"aa"}\n')
        with open(os.path.join(laneD1, "merged.jsonl"), "w") as f:
            for mk, tl in [("m1", 13), ("m2", 14), ("shared", 15)]:
                f.write(json.dumps({"mkey": mk, "total_len": tl}) + "\n")
        with open(os.path.join(laneD1, "solve.jsonl"), "w") as f:
            f.write(json.dumps({"mkey": "m1", "min_total_len": 13, "solved": False}) + "\n")
            f.write(json.dumps({"mkey": "m2", "min_total_len": 13, "solved": False}) + "\n")
            f.write('{"mkey": "m2", "trunc')  # corrupt trailing line -> must be skipped
        # D2: 2 unique (one shared mkey with D1), 1 attempted, 0 solved
        laneD2 = os.path.join(d, "D2", "laneD")
        os.makedirs(laneD2)
        with open(os.path.join(laneD2, "merged.jsonl"), "w") as f:
            for mk, tl in [("shared", 15), ("m3", 16)]:
                f.write(json.dumps({"mkey": mk, "total_len": tl}) + "\n")
        with open(os.path.join(laneD2, "solve.jsonl"), "w") as f:
            f.write(json.dumps({"mkey": "m3", "min_total_len": 13, "solved": False}) + "\n")
        # resolve_hiL: 2 attempted at L40, 0 solved, max_rel_len maxes at 21 (< 24)
        rdir = os.path.join(d, "resolve_hiL")
        os.makedirs(rdir)
        with open(os.path.join(rdir, "resolve_L40.jsonl"), "w") as f:
            f.write(json.dumps({"mkey": "m1", "min_total_len": 13, "max_rel_len": 21,
                                "max_rel_lens": [12, 21], "solved": False}) + "\n")
            f.write(json.dumps({"mkey": "m2", "min_total_len": 13, "max_rel_len": 20,
                                "max_rel_lens": [13, 20], "solved": False}) + "\n")

        S = build_summary(d)
        assert S["union"]["distinct_quotients"] == 4, S["union"]["distinct_quotients"]  # m1,m2,shared,m3
        assert S["union"]["distinct_attempted"] == 3, S["union"]["distinct_attempted"]  # m1,m2,m3
        assert S["union"]["floor_hist"] == {13: 3}, S["union"]["floor_hist"]
        assert S["boxes"]["D1"]["merged_unique"] == 3
        assert S["boxes"]["D1"]["attempted"] == 2   # corrupt line dropped
        assert S["total_solved"] == 0
        assert S["theorem"] is False
        r = S["resolve"]["40"]
        assert r["attempted"] == 2 and r["solved_count"] == 0
        assert max(int(k) for k in r["maxrel_hist"]) == 21
        # archive: 4 distinct candidates, 3 Lane-D + 2 resolve = 5 trials, 0 solved
        arch = emit_archive(d, os.path.join(d, "archive"))
        S["archive"] = arch
        assert arch["candidates"] == 4, arch["candidates"]
        assert arch["trials"] == 5, arch["trials"]
        assert arch["trials_solved"] == 0, arch["trials_solved"]
        cand_lines = list(read_jsonl(os.path.join(d, "archive", "campaign_candidates.jsonl")))
        assert len(cand_lines) == 4
        shared = next(c for c in cand_lines if c["mkey"] == "shared")
        assert sorted(shared["source_boxes"]) == ["D1", "D2"], shared["source_boxes"]
        trial_lines = list(read_jsonl(os.path.join(d, "archive", "campaign_trials.jsonl")))
        assert len(trial_lines) == 5
        assert all("source" in t and "L" in t for t in trial_lines)
        assert os.path.exists(os.path.join(d, "archive", "MANIFEST.md"))
        md = render_md(S)
        assert "certified negative" in md and "13:3" in md.replace(" ", "")
        assert "Data archive" in md
        print("SELFTEST PASS: union dedup, floor hist, corrupt-line skip, resolve "
              "cap-gap, archive (candidates/trials/source_boxes/manifest), md render")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", help="dir holding D1/D2/D3/B/C/resolve_hiL subdirs")
    ap.add_argument("--out", help="markdown report path (default <root>/COLLECTED_RESULTS.md)")
    ap.add_argument("--json_out", help="machine-readable summary path "
                    "(default <root>/collect_summary.json)")
    ap.add_argument("--archive_dir", help="consolidated per-record archive dir "
                    "(default <root>/archive)")
    ap.add_argument("--no_archive", action="store_true",
                    help="skip the consolidated archive (summary only)")
    ap.add_argument("--gzip", action="store_true",
                    help="gzip the archive JSONL (smaller, commit/share-friendly)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    if not args.root:
        ap.error("--root is required (or use --selftest)")
    S = build_summary(args.root)
    if not args.no_archive:
        adir = args.archive_dir or os.path.join(args.root, "archive")
        S["archive"] = emit_archive(args.root, adir, args.gzip)
    out = args.out or os.path.join(args.root, "COLLECTED_RESULTS.md")
    md = render_md(S)
    with open(out, "w") as f:
        f.write(md)
    # JSON summary: drop the big mkey sets (not JSON-serializable, huge)
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if not isinstance(v, set)}
        if isinstance(o, list):
            return [strip(x) for x in o]
        return o
    jout = args.json_out or os.path.join(args.root, "collect_summary.json")
    with open(jout, "w") as f:
        json.dump(strip(S), f, indent=2)
    print(md)
    print(f"\n[written] {out}\n[written] {jout}")
    if S.get("archive"):
        a = S["archive"]
        print(f"[written] {a['candidates_file']}  ({a['candidates']:,} quotients)")
        print(f"[written] {a['trials_file']}  ({a['trials']:,} trials)")


if __name__ == "__main__":
    main()
