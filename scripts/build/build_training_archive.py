"""Phase 2 of the d-o-t data-crafting pipeline -- merge -> v2 archive (PART 1).

See ``experiments/eda+data_collection/data_crafting/4.0.DETAILED_STEPS_DATA_CRAFTING.md`` Phase 2.

The full design is ONE script that runs Phases 2->6 as internal stages and emits
``data/derived/labels/dot_archive_v2.jsonl`` exactly ONCE (at Phase 6). This file currently
implements ONLY **Phase 2 (part 1)**:

  * 2.1  load the original archive (reuse ``dot_dataset.load_archive``);
  * 2.2  merge the 8 named anchors (``anchors.jsonl``) into the 42,450-row archive, keyed by the
         canonical ``f"{r1}|{r2}"``; a named-anchor key colliding with an existing archive key is an
         eval-contamination alarm -> STOP;
  * 2.3  tag ``tier`` and ``group`` on every row.

Phase 2's deliverable is the IN-MEMORY tagged row set (42,458 rows), proven correct by the
acceptance gates below. **No file is written in this part.** Phases 3-6 (diversity/decorrelation,
loss-metadata, bands/weights, emit) land as parts 2-5; only Phase 6 writes ``dot_archive_v2.jsonl``.

Run from the repo root:
    python scripts/build/build_training_archive.py

Reads (read-only) ``dot_archive.jsonl``, ``anchors.jsonl``, ``ak_trap_set.json``,
``baseline_distribution.json``. Originals never modified. Gate-style: prints diagnostics, exits
non-zero with a message on any failure, prints ``PHASE2 PASS`` on success.
"""
import os
import sys
import json
import random
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon              # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset        # noqa: E402  (reuse load_archive)


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
    originals are never mutated, so the min-dot-unchanged snapshot stays valid).

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


def main(archive=None, anchors_jsonl=None, trap_set_json=None, baseline_json=None, canon_sample=0):
    archive = archive or cfg.ARCHIVE
    anchors_jsonl = anchors_jsonl or cfg.ANCHORS_JSONL
    trap_set_json = trap_set_json or cfg.TRAP_SET_JSON
    baseline_json = baseline_json or cfg.BASELINE_JSON

    # ---- load inputs (read-only) ----
    labelled, censored = dot_dataset.load_archive(archive)
    anchors = _load_jsonl(anchors_jsonl)
    trap = _load_json(trap_set_json)
    baseline = _load_json(baseline_json)
    short_hard_keys = trap["groups"]["short_hard"]
    named_keys = trap["groups"]["named"]  # {label: key}

    # ================= 2.1 Load originals =================
    n_lab, n_cen, n_tot = baseline["n_labelled"], baseline["n_censored"], baseline["n_total"]
    if len(labelled) != n_lab or len(censored) != n_cen:
        raise SystemExit(
            f"Phase 2.1 FAILED: archive counts {len(labelled)}/{len(censored)} != baseline "
            f"{n_lab}/{n_cen}")
    if n_lab + n_cen != n_tot or len(labelled) + len(censored) != n_tot:
        raise SystemExit(f"Phase 2.1 FAILED: counts do not reconcile to n_total={n_tot}")

    # 2.1 keying-canonicality gate (advisor #1, load-bearing).
    bad = check_keying_canonical(labelled + censored, sample=canon_sample)
    if bad:
        for raw, ck in bad:
            print(f"  Phase 2.1 canon-key mismatch: stored {raw!r} != canon {ck!r}")
        raise SystemExit(
            "Phase 2.1 FAILED: archive not stored canonical -- raw 'r1|r2' keying is unsafe; "
            "rebuild the 2.2 collision index on canon.canon_key (see plan 2.1).")

    total_orig = len(labelled) + len(censored)
    n_anchors = len(anchors)  # source of truth for the named-anchor count -- never a hardcoded literal

    # ================= 2.2 Merge + 2.3 Tag =================
    pre_min_dot = {_key(r): r["min_dot"] for r in labelled}  # snapshot BEFORE merge (advisor: copies)
    merged = stage2_merge_and_tag(labelled, censored, anchors, short_hard_keys)

    # ---- 2.2 acceptance ----
    if len(merged) != total_orig + n_anchors:
        raise SystemExit(
            f"Phase 2.2 FAILED: total_v2={len(merged)} != total_orig+anchors={total_orig + n_anchors}")
    post_min_dot = {_key(r): r["min_dot"] for r in merged if r["tier"] == "solved"}
    if post_min_dot != pre_min_dot:
        raise SystemExit("Phase 2.2 FAILED: a labelled row's min_dot changed during the merge")

    # ---- 2.3 acceptance ----
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

    # advisor #3a: short_hard keys == EXACTLY the censored & total_len<=13 set (no drift).
    le13 = {_key(r) for r in censored if r["total_len"] <= 13}
    if le13 != set(short_hard_keys):
        raise SystemExit(
            f"Phase 2.3 FAILED: short_hard set drift -- censored&len<=13={sorted(le13)} != "
            f"trap-set short_hard={sorted(short_hard_keys)}")
    if baseline.get("n_censored_le13") != 8:
        raise SystemExit(
            f"Phase 2.3 FAILED: baseline n_censored_le13={baseline.get('n_censored_le13')} != 8")

    # advisor #3b: the 8 anchor keys == ak_trap_set groups.named values (no anchors/trap-set desync).
    anchor_keys = {_key(a) for a in anchors}
    if anchor_keys != set(named_keys.values()):
        raise SystemExit(
            "Phase 2.3 FAILED: anchors.jsonl keys != ak_trap_set groups.named values")

    # ---- summary ----
    tiers = {}
    for r in merged:
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
    print("PHASE2 PASS")
    print(f"  2.1 loaded:  labelled={len(labelled)} censored={len(censored)} total={total_orig}")
    print(f"      keying-canonical gate: {'spot-sample ' + str(canon_sample) if canon_sample else 'full'} OK")
    print(f"  2.2 merged:  total_v2={len(merged)} (= total_orig + {n_anchors} anchors); labelled min_dot unchanged")
    print(f"  2.3 tiers:   " + " ".join(f"{k}={v}" for k, v in sorted(tiers.items()))
          + f"  | groups: named={n_named} short_hard={n_short}")
    print("  (in-memory only -- dot_archive_v2.jsonl is emitted at Phase 6 / part 5)")
    return merged


def parse_args():
    ap = argparse.ArgumentParser(description="Phase 2 (part 1): merge anchors + tag tier/group.")
    ap.add_argument("--archive", default=cfg.ARCHIVE)
    ap.add_argument("--anchors", default=cfg.ANCHORS_JSONL)
    ap.add_argument("--trap_set", default=cfg.TRAP_SET_JSON)
    ap.add_argument("--baseline", default=cfg.BASELINE_JSON)
    ap.add_argument("--canon_sample", type=int, default=0,
                    help="rows to spot-check in the 2.1 keying-canonical gate (0 = full archive)")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(archive=args.archive, anchors_jsonl=args.anchors, trap_set_json=args.trap_set,
         baseline_json=args.baseline, canon_sample=args.canon_sample)
