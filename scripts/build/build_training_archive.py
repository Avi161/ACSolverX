"""Build the d-o-t training archive v2 -- merge anchors, decorrelate, weight, emit.

See ``experiments/eda+data_collection/data_crafting/4.0.DETAILED_STEPS_DATA_CRAFTING.md`` Phases 2-6.

ONE script runs Phases 2->6 as internal stages and emits ``data/derived/labels/dot_archive_v2.jsonl``
exactly ONCE (at Phase 6):

  * Phase 2  (``stage2_merge_and_tag``)  merge the 8 named anchors into the 42,450-row archive keyed
             by the canonical ``f"{r1}|{r2}"`` (a named-anchor collision = eval contamination -> STOP);
             tag ``tier`` / ``group`` on every row.
  * Phase 3  (``stage3_diversity``)       re-walk ``merged_best_paths`` to reconstruct path->class
             sequences, thin the dense easy band (per-path d-o-t <= 10) by stride+cap with a cross-path
             union keep-set (valley/hard kept unconditionally; censored/named/short_hard/look-alike
             exempt), and attach ``n_paths`` + ``near_neighbour_count`` diagnostics.
  * Phase 4  (``stage4_loss_meta``)       ``loss_type`` (regression/hinge) + ``bound_B`` floors.
  * Phase 5  (``stage5_weights``)         per-row ``weight`` -- region rebalance to the target mixture,
             tail/short-hard multipliers, normalize-once-last to mean 1.
  * Phase 6  (``stage6_emit``)            validate the 14-field schema and write the JSONL.

Honesty guards baked in (Field Advisor warm-pre, Checkpoint 1):
  - Phase-3 thinning is a cross-path UNION, which preferentially drops *rare single-path* easy classes
    and keeps redundant hubs -- it is NOT a strong decorrelator. We REPORT ``n_dropped`` + the n_paths
    distribution of dropped classes rather than claim "decorrelation worked."
  - ``short_hard`` / ``named`` get x3 weight but are only 16 rows (~0.2% of loss mass): we REPORT that
    share so the hardness-recognition payoff is not oversold.
  - ``bound_B`` (B_soft=48 / B_hard=150) are HEURISTIC HINGE FLOORS derived from *solved* d-o-t
    percentiles -- NOT statistical lower bounds (the search found no path for censored rows). v1 keeps
    the schema frozen at 14 fields; per-row search-context enrichment is a deferred spec change.
  - ``near_neighbour_count`` is a CHEAP shared-relator / near-length clustering proxy, NOT an
    AC-neighbourhood density (an S-move changes length by an arbitrary amount).

Run from the repo root:
    python scripts/build/build_training_archive.py

Reads (read-only) ``dot_archive.jsonl``, ``anchors.jsonl``, ``ak_trap_set.json``,
``baseline_distribution.json``, ``percentiles.json``, ``merged_best_paths.jsonl``. Originals never
modified. Gate-style: prints per-phase diagnostics, exits non-zero with a message on any failure,
prints ``PHASE2-6 PASS`` and writes the v2 archive on success.
"""
import os
import sys
import json
import math
import bisect
import random
import argparse
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon              # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset        # noqa: E402  (reuse load_archive)

# v2 emit schema -- the EXACT 14 fields every row must carry (7 archive + 7 craft). The doc's 6.2
# says "13"; it is 7+7=14 (the doc miscounts). stage6 asserts the field SET equals this, so a missing
# diagnostic (e.g. n_paths on a non-path row) loud-fails instead of silently becoming null.
V2_FIELDS = [
    "r1", "r2", "total_len", "min_dot", "n_obs", "sources", "censored",
    "loss_type", "bound_B", "weight", "tier", "group", "n_paths", "near_neighbour_count",
]

LOOKALIKE_PAIR = ("YXyxYx", "xxxYYYY")  # the solved d-o-t-12 look-alike of AK(3) (Finding 2 probe)


def _key(row):
    """The canonical join key. The archive is stored canonical, so the raw stored 'r1|r2' is
    already the canonical key (this equality is *proven*, not assumed, by ``check_keying_canonical``)."""
    return f"{row['r1']}|{row['r2']}"


def _load_jsonl(path):
    if not os.path.exists(path):
        raise SystemExit(f"missing {path} -- run scripts/build/build_anchors.py first")
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _load_json(path):
    if not os.path.exists(path):
        raise SystemExit(f"missing {path} -- run the prior phase first")
    with open(path) as f:
        return json.load(f)


def check_keying_canonical(rows, sample=0, seed=cfg.SEED):
    """advisor #1 (load-bearing): prove raw ``f"{r1}|{r2}"`` keying == ``canon.canon_key`` over the
    archive, so 2.2's collision check cannot miss a contamination via a non-canonical stored string.

    Returns a list of up to 5 (raw_key, canon_key) mismatches (empty == pass). ``sample`` > 0 checks
    a random subset; 0 == full (the numba-less ``canon`` shim does the full ~42.4k-row archive in
    ~2s, so keep the contamination tripwire at full in CI)."""
    if sample and sample < len(rows):
        rows = random.Random(seed).sample(rows, sample)
    bad = []
    for r in rows:
        ck, _ = canon.canon_key(r["r1"], r["r2"])
        if ck != _key(r):
            bad.append((_key(r), ck))
            if len(bad) >= 5:
                break
    return bad


def stage2_merge_and_tag(labelled, censored, anchors, short_hard_keys):
    """Phase 2.2 (merge) + 2.3 (tag). Returns the merged list of NEW dict copies (the loaded
    originals are never mutated, so the min-dot-unchanged snapshot stays valid). Row order is
    labelled, then censored, then anchors -- a stable, deterministic order carried through to emit.

    Collision policy (2.2): a named-anchor key colliding with an existing archive key is an
    eval-contamination alarm -> ``SystemExit``. This deviates ON PURPOSE from the plan's generic
    "existing-wins min-aggregate" branch: the named anchors are the frozen counterexample_eval, so a
    collision must HALT, not silently merge (assert-STOP *is* "existing-wins" in the limit -- we
    never reach a collision, so nothing is ever overwritten). The min-aggregate-existing-wins rule
    (min ``min_dot``, union ``sources``, sum ``n_obs``) would apply only if a later phase merged
    legitimately-overlapping sources -- not the case here, where anchors are the sole insert.
    """
    short_hard = set(short_hard_keys)
    index, merged = {}, []

    # archive rows: tag tier (solved/censored) + group (short_hard/"") in place on copies.
    for r in (labelled + censored):
        k = _key(r)
        if k in index:
            raise SystemExit(f"Phase 2.2 FAILED: duplicate key inside the archive: {k}")
        row = dict(r)
        row["tier"] = "censored" if row["censored"] else "solved"
        row["group"] = "short_hard" if k in short_hard else ""
        index[k] = row
        merged.append(row)

    # anchors: clean insert (must not collide); they already carry tier=named/group=named.
    for a in anchors:
        k = _key(a)
        if k in index:
            raise SystemExit(
                f"Phase 2.2 FAILED: named anchor collides with an existing archive key "
                f"(eval contamination) -> STOP: {k}")
        row = dict(a)
        if row.get("tier") != "named" or row.get("group") != "named":
            raise SystemExit(
                f"Phase 2.2 FAILED: anchor row not tagged tier/group=named: {k} -> "
                f"tier={row.get('tier')!r} group={row.get('group')!r}")
        index[k] = row
        merged.append(row)

    return merged


# ============================ Phase 3 -- diversity / decorrelation ============================

def _walk_paths(merged_paths, labelled_keys):
    """Phase 3.1-3.2 path walk. Mirrors ``build_dot_archive``: ``best_path = [r1_0,r2_0,...]``, state
    m = (path[2m], path[2m+1]), per-path d-o-t = N-m. Memoizes canon like build_dot_archive.

    Returns (kept, key_paths, orphans):
      kept       -- set of canonical keys to keep (valley/hard unconditional; easy via stride+cap)
      key_paths  -- key -> set of source-path indices (for n_paths)
      orphans    -- count of on-path keys NOT in ``labelled_keys`` (must be 0; 1:1 join)
    """
    canon_cache = {}

    def ckey(a, b):
        kk = (a, b)
        if kk not in canon_cache:
            canon_cache[kk] = canon.canon_key(a, b)[0]
        return canon_cache[kk]

    kept = set()
    key_paths = defaultdict(set)
    orphans = 0
    with open(merged_paths) as f:
        for pidx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if not rec["solved"]:
                continue
            path, N = rec["best_path"], rec["best_path_length"]
            easy_idx = easy_kept = 0
            for m in range(N + 1):
                k = ckey(path[2 * m], path[2 * m + 1])
                if k not in labelled_keys:
                    orphans += 1
                key_paths[k].add(pidx)
                dot = N - m
                if dot >= 11:
                    kept.add(k)                 # valley/hard: kept unconditionally
                else:                           # easy occurrence: stride [::k], cap C per path
                    if easy_idx % cfg.DIVERSITY_STRIDE == 0 and easy_kept < cfg.PER_PATH_CAP:
                        kept.add(k)
                        easy_kept += 1
                    easy_idx += 1
    return kept, key_paths, orphans


def _near_neighbour_counts(labelled_rows):
    """Phase 3.4 proxy: per labelled class, #OTHER labelled survivors within +-1 total_len sharing a
    relator string. CHEAP shared-relator/near-length clustering -- NOT AC-neighbourhood density.

    bucket[relator] = sorted total_len of classes carrying that relator. A distinct class shares <=1
    relator with a given class (sharing both => same key => same class), so summing the two bucket
    counts cannot double-count -- only self must be removed (advisor A2: handle cr1==cr2 by appending
    the second relator only when distinct, then subtract 1 per consulted bucket)."""
    buckets = defaultdict(list)
    for r in labelled_rows:
        buckets[r["r1"]].append(r["total_len"])
        if r["r2"] != r["r1"]:
            buckets[r["r2"]].append(r["total_len"])
    for s in buckets:
        buckets[s].sort()

    def within(sorted_lens, t):
        return bisect.bisect_right(sorted_lens, t + 1) - bisect.bisect_left(sorted_lens, t - 1)

    out = {}
    for r in labelled_rows:
        t, a, b = r["total_len"], r["r1"], r["r2"]
        if a == b:                              # only one bucket entry was added for this row
            nn = within(buckets[a], t) - 1
        else:
            nn = (within(buckets[a], t) - 1) + (within(buckets[b], t) - 1)
        out[_key(r)] = nn
    return out


def stage3_diversity(merged, merged_paths, lookalike_key):
    """Phase 3. Returns (survivors, stats). Survivors are filtered from ``merged`` IN ORDER (never a
    set -> deterministic emit order). Mutates survivor dicts to add n_paths / near_neighbour_count.

    Drop rule: a labelled class is dropped iff it is NOT in the path keep-set AND not the look-alike
    probe. Non-labelled rows (censored/named) always survive and get n_paths=0 / near_neighbour_count=0
    explicitly (F1 forward-seam: never .get->null). Censored/named/short_hard are never in the labelled
    drop pool to begin with; the look-alike (d-o-t 12 = valley) is already kept unconditionally -- its
    exemption is belt-and-suspenders against a future shorter path dropping it to <=10.
    """
    labelled_keys = {_key(r) for r in merged if r["tier"] == "solved"}
    kept, key_paths, orphans = _walk_paths(merged_paths, labelled_keys)
    if orphans:
        raise SystemExit(f"Phase 3.1 FAILED: {orphans} on-path keys absent from the v2 archive (join broke)")

    survivors, dropped = [], []
    for r in merged:
        if r["tier"] != "solved":
            survivors.append(r)
        elif _key(r) in kept or _key(r) == lookalike_key:
            survivors.append(r)
        else:
            dropped.append(r)

    if len(survivors) >= len(merged):
        raise SystemExit("Phase 3.3 FAILED: nothing dropped -- the stride did not thin the easy band")

    lab_surv = [r for r in survivors if r["tier"] == "solved"]
    nn = _near_neighbour_counts(lab_surv)
    for r in survivors:
        if r["tier"] == "solved":
            r["n_paths"] = len(key_paths[_key(r)])
            r["near_neighbour_count"] = nn[_key(r)]
        else:
            r["n_paths"] = 0
            r["near_neighbour_count"] = 0

    # FA Finding 1: the union keep preferentially drops rare single-path easy classes -- report the
    # n_paths distribution of the dropped set so this is visible, not hidden behind "survivors < raw".
    drop_hist = Counter(min(len(key_paths[_key(r)]), 5) for r in dropped)
    nn_vals = [r["near_neighbour_count"] for r in lab_surv]
    stats = {
        "raw_labelled": len(labelled_keys),
        "survivors_labelled": len(lab_surv),
        "n_dropped": len(dropped),
        "drop_n_paths_hist": dict(sorted(drop_hist.items())),  # n_paths(>=5 bucketed) -> count
        "nn_mean": (sum(nn_vals) / len(nn_vals) if nn_vals else 0.0),
        "nn_max": (max(nn_vals) if nn_vals else 0),
    }
    return survivors, stats


# ============================ Phase 4 -- loss metadata ============================

def stage4_loss_meta(rows, b_soft, b_hard):
    """Phase 4.1/4.2. ``loss_type`` regression(labelled)/hinge(censored); ``bound_B`` = B_hard(named) /
    B_soft(other censored) / null(labelled). Anchors already carry hinge + B_hard from Phase 1; setting
    uniformly is idempotent for them iff percentiles' B_hard matches the anchors' stored bound_B
    (asserted in build_v2_rows). B_soft/B_hard are heuristic hinge floors, not lower bounds."""
    for r in rows:
        cen = r["censored"]
        r["loss_type"] = "hinge" if cen else "regression"
        if r["tier"] == "named":
            r["bound_B"] = b_hard
        elif cen:
            r["bound_B"] = b_soft
        else:
            r["bound_B"] = None


# ============================ Phase 5 -- bands & weights ============================

def _region(r):
    """5.1 region: labelled -> easy/valley/hard_solved by d-o-t band; censored+named -> hard_unsolved."""
    return "hard_unsolved" if r["censored"] else cfg.band_of(r["min_dot"])


def stage5_weights(rows):
    """Phase 5.1-5.5 (order load-bearing). Returns stats. Per-row ``weight``:
       base = clip(target_share/actual_share, *WEIGHT_CLIP); x0.5 if d-o-t>100 (loose tail);
       x3 (cap 5.0) if short_hard/named; then normalize ONCE (w *= n/sum) so mean(weight)==1."""
    regions = [_region(r) for r in rows]
    n = len(rows)
    counts = Counter(regions)
    actual = {reg: counts.get(reg, 0) / n for reg in cfg.TARGET_SHARES}

    # FA d.9 guard: easy must stay DOWN-weighted; if a future drop pushed easy below target the clip
    # floor would silently FLIP it to up-weighting. Fail loudly instead.
    if actual["easy"] <= cfg.TARGET_SHARES["easy"]:
        raise SystemExit(
            f"Phase 5 FAILED: easy share {actual['easy']:.4f} <= target {cfg.TARGET_SHARES['easy']} "
            f"-> base weight would up-weight easy (denominator inversion)")

    lo, hi = cfg.WEIGHT_CLIP
    ratios = {reg: (cfg.TARGET_SHARES[reg] / actual[reg] if actual[reg] else 0.0)
              for reg in cfg.TARGET_SHARES}
    clipped = [reg for reg, rt in ratios.items() if rt < lo or rt > hi]

    pre = []
    for r, reg in zip(rows, regions):
        w = min(max(ratios[reg], lo), hi)
        dot = r["min_dot"]
        if dot is not None and dot > cfg.TAIL_DOT_THRESHOLD:
            w *= cfg.TAIL_MULT
        if r["group"] == "short_hard" or r["tier"] == "named":
            w = min(w * cfg.SHORT_HARD_MULT, hi)
        pre.append(w)

    scale = n / sum(pre)
    for r, w in zip(rows, pre):
        r["weight"] = w * scale

    total_w = sum(r["weight"] for r in rows)
    band_mass = {reg: sum(r["weight"] for r, rg in zip(rows, regions) if rg == reg) / total_w
                 for reg in cfg.TARGET_SHARES}
    sh_mass = sum(r["weight"] for r in rows
                  if r["group"] == "short_hard" or r["tier"] == "named") / total_w
    return {
        "actual_shares": actual, "ratios": ratios, "clipped_regions": clipped,
        "mean_weight": total_w / n, "band_mass": band_mass,
        "short_hard_named_mass_share": sh_mass,
    }


# ============================ Phase 6 -- emit ============================

def stage6_emit(rows, out):
    """Phase 6.1/6.2. Validate the EXACT 14-field schema + invariants, then write one JSON/line.
    Building each obj from V2_FIELDS via the strict field-set check guarantees no diagnostic was
    silently dropped to null and no temp key leaked."""
    expected = set(V2_FIELDS)
    for i, r in enumerate(rows):
        got = set(r.keys())
        if got != expected:
            raise SystemExit(
                f"Phase 6.2(a) FAILED: row {i} field-set mismatch -- missing={expected - got} "
                f"extra={got - expected}")
        if r["censored"] and (r["min_dot"] is not None or r["n_obs"] != 0):
            raise SystemExit(
                f"Phase 6.2(b) FAILED: censored row with min_dot/n_obs set: {_key(r)} "
                f"min_dot={r['min_dot']!r} n_obs={r['n_obs']!r}")
        w = r["weight"]
        if not (isinstance(w, (int, float)) and math.isfinite(w) and w > 0):
            raise SystemExit(f"Phase 6.2(d) FAILED: non-finite/non-positive weight {w!r} at {_key(r)}")

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps({k: r[k] for k in V2_FIELDS}, sort_keys=True) + "\n")


# ============================ orchestration ============================

def build_v2_rows(archive=None, anchors_jsonl=None, trap_set_json=None, baseline_json=None,
                  percentiles_json=None, merged_paths=None, canon_sample=0):
    """Run Phases 2->5 in-memory and return (survivors, stats). Pure: reads inputs, writes nothing
    (Phase 6 emit is separate). All acceptance gates raise SystemExit on failure."""
    archive = archive or cfg.ARCHIVE
    anchors_jsonl = anchors_jsonl or cfg.ANCHORS_JSONL
    trap_set_json = trap_set_json or cfg.TRAP_SET_JSON
    baseline_json = baseline_json or cfg.BASELINE_JSON
    percentiles_json = percentiles_json or cfg.PERCENTILES_JSON
    merged_paths = merged_paths or cfg.MERGED_PATHS

    # ---- load inputs (read-only) ----
    labelled, censored = dot_dataset.load_archive(archive)
    anchors = _load_jsonl(anchors_jsonl)
    trap = _load_json(trap_set_json)
    baseline = _load_json(baseline_json)
    percentiles = _load_json(percentiles_json)
    short_hard_keys = trap["groups"]["short_hard"]
    named_keys = trap["groups"]["named"]  # {label: key}
    b_soft, b_hard = int(percentiles["B_soft"]), int(percentiles["B_hard"])
    lookalike_key = canon.canon_key(*LOOKALIKE_PAIR)[0]

    # ================= Phase 2.1 Load originals =================
    n_lab, n_cen, n_tot = baseline["n_labelled"], baseline["n_censored"], baseline["n_total"]
    if len(labelled) != n_lab or len(censored) != n_cen:
        raise SystemExit(
            f"Phase 2.1 FAILED: archive counts {len(labelled)}/{len(censored)} != baseline "
            f"{n_lab}/{n_cen}")
    if n_lab + n_cen != n_tot or len(labelled) + len(censored) != n_tot:
        raise SystemExit(f"Phase 2.1 FAILED: counts do not reconcile to n_total={n_tot}")

    bad = check_keying_canonical(labelled + censored, sample=canon_sample)
    if bad:
        for raw, ck in bad:
            print(f"  Phase 2.1 canon-key mismatch: stored {raw!r} != canon {ck!r}")
        raise SystemExit(
            "Phase 2.1 FAILED: archive not stored canonical -- raw 'r1|r2' keying is unsafe; "
            "rebuild the 2.2 collision index on canon.canon_key (see plan 2.1).")

    total_orig = len(labelled) + len(censored)
    n_anchors = len(anchors)

    # ================= Phase 2.2 Merge + 2.3 Tag =================
    pre_min_dot = {_key(r): r["min_dot"] for r in labelled}
    merged = stage2_merge_and_tag(labelled, censored, anchors, short_hard_keys)

    if len(merged) != total_orig + n_anchors:
        raise SystemExit(
            f"Phase 2.2 FAILED: total_v2={len(merged)} != total_orig+anchors={total_orig + n_anchors}")
    post_min_dot = {_key(r): r["min_dot"] for r in merged if r["tier"] == "solved"}
    if post_min_dot != pre_min_dot:
        raise SystemExit("Phase 2.2 FAILED: a labelled row's min_dot changed during the merge")

    missing_tier = sum(1 for r in merged if not r.get("tier"))
    if missing_tier:
        raise SystemExit(f"Phase 2.3 FAILED: {missing_tier} rows have no tier")
    n_named = sum(1 for r in merged if r["group"] == "named")
    n_short = sum(1 for r in merged if r["group"] == "short_hard")
    if n_named != n_anchors:
        raise SystemExit(f"Phase 2.3 FAILED: group=='named' count {n_named} != n_anchors {n_anchors}")
    if n_short != len(short_hard_keys):
        raise SystemExit(
            f"Phase 2.3 FAILED: group=='short_hard' count {n_short} != trap-set short_hard "
            f"{len(short_hard_keys)}")
    le13 = {_key(r) for r in censored if r["total_len"] <= 13}
    if le13 != set(short_hard_keys):
        raise SystemExit(
            f"Phase 2.3 FAILED: short_hard set drift -- censored&len<=13={sorted(le13)} != "
            f"trap-set short_hard={sorted(short_hard_keys)}")
    if baseline.get("n_censored_le13") != 8:
        raise SystemExit(
            f"Phase 2.3 FAILED: baseline n_censored_le13={baseline.get('n_censored_le13')} != 8")
    anchor_keys = {_key(a) for a in anchors}
    if anchor_keys != set(named_keys.values()):
        raise SystemExit("Phase 2.3 FAILED: anchors.jsonl keys != ak_trap_set groups.named values")
    if lookalike_key not in post_min_dot:
        raise SystemExit(f"Phase 2 FAILED: look-alike probe {lookalike_key} not a labelled archive row")

    p2 = {"labelled": len(labelled), "censored": len(censored), "total": total_orig,
          "total_v2": len(merged), "n_anchors": n_anchors,
          "tiers": dict(Counter(r["tier"] for r in merged)),
          "n_named": n_named, "n_short": n_short, "canon_sample": canon_sample}

    # ================= Phase 3 Diversity =================
    survivors, p3 = stage3_diversity(merged, merged_paths, lookalike_key)

    # ================= Phase 4 Loss metadata =================
    anchor_pre = {_key(r): (r["loss_type"], r["bound_B"]) for r in survivors if r["tier"] == "named"}
    stage4_loss_meta(survivors, b_soft, b_hard)
    # FA d.7: Phase 4 must leave the Phase-1 anchor (loss_type, bound_B) byte-identical.
    for r in survivors:
        if r["tier"] == "named" and (r["loss_type"], r["bound_B"]) != anchor_pre[_key(r)]:
            raise SystemExit(
                f"Phase 4 FAILED: anchor {_key(r)} loss-meta changed "
                f"{anchor_pre[_key(r)]} -> {(r['loss_type'], r['bound_B'])} (percentiles desync?)")
    bad_hinge = [_key(r) for r in survivors if (r["loss_type"] == "hinge") != bool(r["censored"])]
    if bad_hinge:
        raise SystemExit(f"Phase 4.1 FAILED: hinge<->censored mismatch on {bad_hinge[:3]}")
    p4 = {"loss_type": dict(Counter(r["loss_type"] for r in survivors)),
          "b_soft": b_soft, "b_hard": b_hard,
          "bound_B_null": sum(1 for r in survivors if r["bound_B"] is None)}

    # ================= Phase 5 Bands & weights =================
    p5 = stage5_weights(survivors)
    if abs(p5["mean_weight"] - 1.0) > 0.01:
        raise SystemExit(f"Phase 5.5 FAILED: mean(weight)={p5['mean_weight']:.5f} != 1.0 +-0.01")
    if p5["clipped_regions"]:
        # not fatal, but surface it -- the band-mass acceptance distorts under clipping.
        print(f"  Phase 5 NOTE: regions hit WEIGHT_CLIP: {p5['clipped_regions']}")

    # ================= presence gate (6.2e, computed pre-emit) =================
    surv_keys = {_key(r) for r in survivors}
    must_have = anchor_keys | set(short_hard_keys) | {lookalike_key}
    missing = must_have - surv_keys
    if missing:
        raise SystemExit(f"Phase 6.2(e) FAILED: required keys absent from survivors: {sorted(missing)}")

    stats = {"p2": p2, "p3": p3, "p4": p4, "p5": p5,
             "lookalike_key": lookalike_key, "n_v2": len(survivors)}
    return survivors, stats


def _print_report(stats):
    p2, p3, p4, p5 = stats["p2"], stats["p3"], stats["p4"], stats["p5"]
    print("PHASE2-6 PASS")
    print(f"  P2 merge:  labelled={p2['labelled']} censored={p2['censored']} "
          f"+{p2['n_anchors']} anchors -> {p2['total_v2']}  "
          f"(keying-canonical: {'sample ' + str(p2['canon_sample']) if p2['canon_sample'] else 'full'} OK)")
    print(f"  P3 thin:   raw_labelled={p3['raw_labelled']} survivors={p3['survivors_labelled']} "
          f"dropped={p3['n_dropped']}  drop n_paths hist(>=5 bucketed)={p3['drop_n_paths_hist']}")
    print(f"             near_neighbour: mean={p3['nn_mean']:.2f} max={p3['nn_max']}  "
          f"(shared-relator/near-length proxy, NOT AC-distance)")
    print(f"  P4 loss:   {p4['loss_type']}  bound_B: B_soft={p4['b_soft']} B_hard={p4['b_hard']} "
          f"null(labelled)={p4['bound_B_null']}")
    bm = "  ".join(f"{k}={v:.3f}" for k, v in p5["band_mass"].items())
    rr = "  ".join(f"{k}={v:.2f}" for k, v in p5["ratios"].items())
    print(f"  P5 weight: mean={p5['mean_weight']:.4f}  band_mass[{bm}]")
    print(f"             target/actual ratios[{rr}]  clipped={p5['clipped_regions'] or 'none'}")
    print(f"             short_hard+named loss-mass share={p5['short_hard_named_mass_share']*100:.2f}% "
          f"(16 rows -- intentionally small; do NOT oversell hardness funding)")
    print(f"  total v2 rows = {stats['n_v2']}")


def main(archive=None, anchors_jsonl=None, trap_set_json=None, baseline_json=None,
         percentiles_json=None, merged_paths=None, out=None, canon_sample=0, write=True):
    out = out or cfg.ARCHIVE_V2
    survivors, stats = build_v2_rows(
        archive=archive, anchors_jsonl=anchors_jsonl, trap_set_json=trap_set_json,
        baseline_json=baseline_json, percentiles_json=percentiles_json, merged_paths=merged_paths,
        canon_sample=canon_sample)
    if write:
        stage6_emit(survivors, out)
    _print_report(stats)
    print(f"  {'wrote ' + out if write else '(no write: --no_write)'}")
    return survivors, stats


def parse_args():
    ap = argparse.ArgumentParser(description="Phases 2-6: build dot_archive_v2.jsonl.")
    ap.add_argument("--archive", default=cfg.ARCHIVE)
    ap.add_argument("--anchors", default=cfg.ANCHORS_JSONL)
    ap.add_argument("--trap_set", default=cfg.TRAP_SET_JSON)
    ap.add_argument("--baseline", default=cfg.BASELINE_JSON)
    ap.add_argument("--percentiles", default=cfg.PERCENTILES_JSON)
    ap.add_argument("--merged_paths", default=cfg.MERGED_PATHS)
    ap.add_argument("--out", default=cfg.ARCHIVE_V2)
    ap.add_argument("--no_write", action="store_true", help="run all gates but do not write the v2 file")
    ap.add_argument("--canon_sample", type=int, default=0,
                    help="rows to spot-check in the 2.1 keying-canonical gate (0 = full archive)")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(archive=args.archive, anchors_jsonl=args.anchors, trap_set_json=args.trap_set,
         baseline_json=args.baseline, percentiles_json=args.percentiles, merged_paths=args.merged_paths,
         out=args.out, canon_sample=args.canon_sample, write=not args.no_write)
