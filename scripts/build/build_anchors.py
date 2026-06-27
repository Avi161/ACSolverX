"""Phase 1 of the d-o-t data-crafting pipeline -- anchors.

See ``experiments/eda+data_collection/4.DETAILED_STEPS_DATA_CRAFTING.md`` Phase 1. Supplies the
short-hard / hard presentations the raw data lacks:

  * emits the NAMED anchor rows -- AK(3)..AK(8) + Length-14 x2 -- as new (censored, hinge) training
    rows -> ``data/anchors.jsonl``;
  * emits the search-time TRAP-SET of 16 canonical keys ({8 named} u {8 in-data cousins}) ->
    ``data/ak_trap_set.json``.

The 8 cousins are NOT new rows -- they already exist in ``dot_archive.jsonl`` as censored rows with
``total_len <= 13``; Phase 1 only records their keys (Phase 2 tags them ``group=short_hard`` in
place; Phase 7 routes them to TRAIN, not the frozen eval).

Run from the repo root:
    python scripts/build_anchors.py

Reads ``data/dot_archive.jsonl`` (absent-check) and ``data/percentiles.json`` (B_hard, from Phase 0).
Originals never modified. Gate-style: prints diagnostics, exits non-zero with a message on any
failure (a named anchor already present in the archive aborts -- that would contaminate the eval).
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon          # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset    # noqa: E402  (reuse load_archive)

# Length-14 counterexamples from greedy_search.ipynb's `counterexamples` dict (named for their
# 14-letter size; unrelated to AK(3)). AK(n) is synthesized from the formula below.
LENGTH14 = [
    ("Length 14 #1", "XyyxYYY", "XyxxyXX"),
    ("Length 14 #2", "XyyxYYY", "XyxxYXX"),
]


def named_specs():
    """Raw (label, r1, r2) for every named anchor. AK(n) = <x,y | xyx=yxy, x^n=y^(n+1)> ->
    r1='xyxYXY' (len 6), r2='x'*n + 'Y'*(n+1) (len 2n+1). Cap AK_MAX keeps growth headroom (4-3a)."""
    specs = [(f"AK({n})", "xyxYXY", "x" * n + "Y" * (n + 1))
             for n in range(cfg.AK_MIN, cfg.AK_MAX + 1)]
    specs.extend(LENGTH14)
    return specs


def build_named_rows(b_hard):
    """8 anchor rows in the archive's censored schema + the 4 Phase-tag fields (no extra fields, so
    the Phase-2 merge stays clean). Returns (rows, label_to_key)."""
    rows, label_to_key = [], {}
    for label, r1, r2 in named_specs():
        c1, c2 = canon.canonical_pair_str(r1, r2)
        key, tlen = canon.canon_key(r1, r2)
        label_to_key[label] = key
        rows.append({
            "r1": c1, "r2": c2, "total_len": tlen,
            "min_dot": None, "n_obs": 0, "sources": [], "censored": True,
            "tier": "named", "loss_type": "hinge", "bound_B": b_hard, "group": "named",
        })
    return rows, label_to_key


def find_cousins(censored):
    """The in-data cousins: canonical keys of censored rows with total_len <= 13. The archive is
    stored canonical, so the stored 'r1|r2' is already the canonical key."""
    return sorted(f"{r['r1']}|{r['r2']}" for r in censored if r["total_len"] <= 13)


def _load_b_hard(percentiles_json):
    if not os.path.exists(percentiles_json):
        raise SystemExit(f"missing {percentiles_json} -- run scripts/phase0_baseline.py first")
    with open(percentiles_json) as f:
        return int(json.load(f)["B_hard"])


def _write_anchors(rows, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def _write_trap_set(named_label_to_key, cousin_keys, path):
    keys = sorted(set(named_label_to_key.values()) | set(cousin_keys))
    obj = {
        "version": 1,
        "n_keys": len(keys),
        "source": "build_anchors.py Phase 1",
        "keys": keys,
        "groups": {
            "named": dict(sorted(named_label_to_key.items())),
            "short_hard": sorted(cousin_keys),
        },
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
    return keys


def main(archive=None, percentiles_json=None, anchors_out=None, trap_out=None):
    archive = archive or cfg.ARCHIVE
    percentiles_json = percentiles_json or cfg.PERCENTILES_JSON
    anchors_out = anchors_out or cfg.ANCHORS_JSONL
    trap_out = trap_out or cfg.TRAP_SET_JSON

    b_hard = _load_b_hard(percentiles_json)
    rows, label_to_key = build_named_rows(b_hard)
    named_keys = set(label_to_key.values())

    labelled, censored = dot_dataset.load_archive(archive)
    arch_keys = set(f"{r['r1']}|{r['r2']}" for r in (labelled + censored))

    # load-bearing gate: a named anchor must NOT already be in the archive (eval contamination).
    present = sorted(label for label, k in label_to_key.items() if k in arch_keys)
    if present:
        for label in present:
            print(f"  PHASE1 1.3 FAIL: named anchor already in archive: {label} ({label_to_key[label]})")
        raise SystemExit("Phase 1 absent-check FAILED -- a named counterexample is in the training data")

    cousin_keys = find_cousins(censored)
    if len(cousin_keys) != 8:
        raise SystemExit(f"Phase 1 FAILED: expected 8 cousins (censored total_len<=13), got {len(cousin_keys)}")

    overlap = named_keys & set(cousin_keys)
    if overlap:
        raise SystemExit(f"Phase 1 FAILED: named/cousin key overlap: {sorted(overlap)}")

    _write_anchors(rows, anchors_out)
    trap_keys = _write_trap_set(label_to_key, cousin_keys, trap_out)
    if len(trap_keys) != 16:
        raise SystemExit(f"Phase 1 FAILED: trap-set has {len(trap_keys)} keys, expected 16")

    print("PHASE1 PASS")
    print(f"  named anchors: {len(rows)} (AK({cfg.AK_MIN})..AK({cfg.AK_MAX}) + Length-14 x2), bound_B={b_hard}")
    for label, k in sorted(label_to_key.items()):
        print(f"    {label:<13} {k}")
    print(f"  in-data cousins (group=short_hard, tagged in Phase 2): {len(cousin_keys)}")
    print(f"  trap-set: {len(trap_keys)} canonical keys")
    print(f"  wrote {anchors_out} and {trap_out}")


if __name__ == "__main__":
    main()
