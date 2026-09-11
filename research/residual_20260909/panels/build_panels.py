#!/usr/bin/env python3
"""Build disjoint, stratified evaluation panels over the AC19 census residual.

Inputs (read-only, never modified):
  results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv
      The 727 rows the frozen 1,000-unit policy left unsolved.
  results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl
      Per-row certificate/failure shards for all 72,779 census rows (74 files).
  data/AC19_extended_aut_min.csv
      Aut-minimal representatives with class size n_members.

Outputs (written under research/residual_20260909/panels/, this directory):
  features_727.csv               one row per residual presentation, full feature set
  clusters.csv                   name -> cluster_id (+ short description)
  dev.csv / val.csv / test.csv   three disjoint ~100-row stratified panels
  rest.csv                       the remaining unpaneled residual rows (~427)
  regression60.csv               ~60-row stratified sample of solved rows near budget
  regression_all_near_limit.csv  every solved row with nodes_explored >= 950
  panel_manifest.json            sha256 + row counts + seed + provenance
  PANELS.md                      method write-up (dev panel in full; val/test counts only)

Determinism: every random choice goes through one ``random.Random(SEED)`` instance,
consumed in a fixed order (sorted cluster ids, then dev/val/test, then a single
top-up pass). Re-running this script reproduces byte-identical CSVs.

Usage:
    PYTHONPATH=. python3 research/residual_20260909/panels/build_panels.py
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from experiments.equivalence_classes.lib.words import abelian_det, canon_pair, exp_sums
from experiments.search.heuristic_1k import pack, response
from experiments.heuristic_search.core.hfast import _feats_nj
from experiments.search.heuristics import N_FEAT
from research.supermoves_20260908.bs_preflight import preflight
from research.supermoves_20260908.cheap_gates import (
    _bs_patterns_for_length,
    bs_gate,
    inv as gate_inv,
    one_occurrence_donor,
    two_block_gate,
)
from research.supermoves_20260908.mid_search import bs_escape_feature

# --------------------------------------------------------------------------------- paths / seed

REPO = Path(__file__).resolve().parents[3]
CENSUS_DIR = REPO / "results" / "heuristic_search" / "ac19_final_policy_full_1k"
UNSOLVED_CSV = CENSUS_DIR / "unsolved.csv"
SHARD_GLOB = str(CENSUS_DIR / "rows_*.jsonl")
MEMBERS_CSV = REPO / "data" / "AC19_extended_aut_min.csv"
OUT_DIR = Path(__file__).resolve().parent
SCRIPT_REL_PATH = "research/residual_20260909/panels/build_panels.py"

SEED = 20260909
DEV_TARGET = 100
VAL_TARGET = 100
TEST_TARGET = 100
REGRESSION_TARGET = 60
REGRESSION_NODES_MIN_PANEL = 900     # regression60 pool: solved rows with nodes_explored >= this
REGRESSION_NODES_MIN_ALLROW = 950    # regression_all_near_limit.csv threshold

# ------------------------------------------------------------------------------- length buckets
#
# Chosen from the empirical quartiles of total_len over the 727 residual rows
# (10/25/50/75/90/95/99pct = 17/18/19/21/23/24/27, min 14, max 31): "short" is at or
# below the residual's own median-ish lower half, "long" is at or above its 75th
# percentile, "mid" is the middle third. This 3-way split keeps each length bucket
# in the low hundreds so it can still be usefully crossed with reduction status.

def length_bucket(total_len: int) -> str:
    if total_len <= 18:
        return "short"
    if total_len <= 21:
        return "mid"
    return "long"


# ------------------------------------------------------------------------------------ feature extraction

def _lsw_features(codes: np.ndarray) -> np.ndarray:
    """Replicate heuristic_1k.score_key's own feature call: split off the pack
    separator and hand the two words to hfast._feats_nj. f[0]=L, f[5]=MK, f[7]=S,
    in the ``FEATURES`` order documented in experiments/search/heuristics.py."""
    sep = 0
    for i in range(len(codes)):
        if codes[i] == 0:
            sep = i
            break
    word_codes = np.empty(len(codes) - 1, dtype=np.uint8)
    word_codes[:sep] = codes[:sep]
    word_codes[sep:] = codes[sep + 1:]
    f = np.empty(N_FEAT, dtype=np.float64)
    _feats_nj(word_codes, 0, sep, len(codes) - sep - 1,
              np.empty(len(codes), dtype=np.bool_), np.empty(len(codes), dtype=np.int64), f)
    return f


def _cyclic_blocks(word: str) -> tuple[int, int]:
    """Cyclic run-length block counts (n_x_blocks, n_y_blocks), sign-folded.

    Pure-Python mirror of hfast._runs_nj's block decomposition (merge the first
    and last run when they carry the same generator, i.e. treat the word as a
    ring), restricted to counting blocks per generator rather than run lengths.
    """
    if not word:
        return 0, 0
    is_x = [c in "xX" for c in word]
    runs = []  # list of (is_x, length)
    i = 0
    n = len(word)
    while i < n:
        j = i
        while j + 1 < n and is_x[j + 1] == is_x[i]:
            j += 1
        runs.append([is_x[i], j - i + 1])
        i = j + 1
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        runs[0][1] += runs[-1][1]
        runs.pop()
    n_x = sum(1 for isx, _ in runs if isx)
    n_y = len(runs) - n_x
    return n_x, n_y


def _bs_gate_with_index(pair: tuple[str, str]):
    """Same recognition as cheap_gates.bs_gate(pair, general=True), but also
    returns which relator was the donor. Deliberately re-walks bs_gate's own
    loop (same helper, same order) rather than approximating it separately."""
    for donor_index, donor in enumerate(pair):
        patterns = _bs_patterns_for_length(len(donor)).get(donor)
        if not patterns:
            continue
        companion = pair[1 - donor_index]
        for a, b, relation, m, n in patterns:
            exponent = companion.count(b) - companion.count(gate_inv(b))
            if abs(exponent) == 1:
                return donor_index, a, b, relation, m, n
    return None


def compute_features(name: str, r1: str, r2: str, n_members: int) -> dict:
    """One residual row's full feature record. r1/r2 are the raw unsolved.csv
    strings (kept verbatim for joining); every derived quantity is computed on
    canon_pair(r1, r2) so it is rotation/inversion/swap invariant, per spec."""
    cr1, cr2 = canon_pair(r1, r2)
    len1, len2 = len(cr1), len(cr2)
    total_len = len1 + len2
    max_len = max(len1, len2)

    codes = np.frombuffer(pack((cr1, cr2)), dtype=np.uint8)
    f = _lsw_features(codes)
    L, MK, S = f[0], f[5], f[7]
    assert int(L) == total_len, "hfast total length disagrees with len1+len2"
    W = int(min(response(codes)))

    det = abelian_det(cr1, cr2)
    ex1, ey1 = exp_sums(cr1)
    ex2, ey2 = exp_sums(cr2)
    xb1, yb1 = _cyclic_blocks(cr1)
    xb2, yb2 = _cyclic_blocks(cr2)

    gate = _bs_gate_with_index((cr1, cr2))
    bs_general = gate is not None
    bs_donor_index = gate[0] if gate else None
    bs_m = gate[4] if gate else None  # gate tuple: (donor_index, a, b, relation, m, n)

    pf = preflight((cr1, cr2))
    bs_preflight_status = pf["status"]
    stalled_stable_letters = pf.get("stable_letters")

    T, _check = bs_escape_feature((cr1, cr2))

    tb_gate = two_block_gate((cr1, cr2))
    one_occ_1 = one_occurrence_donor(cr1)
    one_occ_2 = one_occurrence_donor(cr2)

    return dict(
        name=name, r1=r1, r2=r2, canon_r1=cr1, canon_r2=cr2,
        len1=len1, len2=len2, total_len=total_len, max_len=max_len,
        n_members=n_members,
        S=S, MK=MK, W=W,
        abelian_det=det,
        ex1=ex1, ey1=ey1, ex2=ex2, ey2=ey2,
        x_blocks1=xb1, y_blocks1=yb1, x_blocks2=xb2, y_blocks2=yb2,
        bs_general=bs_general, bs_m=bs_m, bs_donor_index=bs_donor_index,
        bs_preflight_status=bs_preflight_status,
        stalled_stable_letters=stalled_stable_letters,
        T=T,
        two_block_gate=tb_gate,
        primitive_one_occurrence1=one_occ_1, primitive_one_occurrence2=one_occ_2,
        length_bucket=length_bucket(total_len),
    )


# ---------------------------------------------------------------------------------------- I/O

def load_unsolved() -> list[dict]:
    with open(UNSOLVED_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 727, f"expected 727 unsolved rows, found {len(rows)}"
    return rows


def load_members() -> dict[str, int]:
    with open(MEMBERS_CSV, newline="") as f:
        return {row["name"]: int(row["n_members"]) for row in csv.DictReader(f)}


def scan_shards(needed_names: set[str]):
    """One pass over all 74 shards. Returns:
      shard_rec: name -> jsonl record, for every name in needed_names (the 727)
      near_limit_900: solved records with nodes_explored >= REGRESSION_NODES_MIN_PANEL
      near_limit_950: solved records with nodes_explored >= REGRESSION_NODES_MIN_ALLROW
      route_counts_900: Counter of route -> count for the >=900 solved pool
    """
    shard_rec = {}
    near_limit_900 = []
    near_limit_950 = []
    route_counts_900 = Counter()
    for fp in sorted(glob.glob(SHARD_GLOB)):
        with open(fp) as f:
            for line in f:
                d = json.loads(line)
                if d["name"] in needed_names:
                    shard_rec[d["name"]] = d
                if d["solved"]:
                    if d["nodes_explored"] >= REGRESSION_NODES_MIN_PANEL:
                        near_limit_900.append(d)
                        route_counts_900[d["route"]] += 1
                    if d["nodes_explored"] >= REGRESSION_NODES_MIN_ALLROW:
                        near_limit_950.append(d)
    missing = needed_names - shard_rec.keys()
    assert not missing, f"{len(missing)} residual names not found in any shard: {sorted(missing)[:5]}..."
    return shard_rec, near_limit_900, near_limit_950, route_counts_900


# ------------------------------------------------------------------------------------- clustering
#
# Nine mutually exclusive, exhaustive clusters. Primary axis is the BS-donor /
# preflight status (the frozen policy's own T-feature obstruction structure);
# the remaining bulk (708 rows with no recognized BS donor at all -- the census
# route is 726/727 incumbent_restart vs 1 plain_s20, too degenerate to use as a
# crossing axis on its own, so the single plain_s20 row is folded into the BS
# axis where it structurally belongs instead: it is the one accept case) is
# split by total-length bucket x whether the failing search ever found a
# shorter state than its root (best_reduction > 0) at all.

CLUSTER_DEFS = [
    # (id, description)
    ("bs_accept_budget_starved",
     "BS donor recognized, preflight ACCEPTS (a certified reduction exists) but the "
     "1000-unit search never certified it -- budget-starved, not obstructed"),
    ("bs_stalled_lo",
     "BS donor recognized, preflight rejects with 3 stable letters left (T=2)"),
    ("bs_stalled_hi",
     "BS donor recognized, preflight rejects with 7 stable letters left (T=6)"),
    ("non_bs_short_reduced", "no BS donor; total_len<=18; search found a shorter state than root"),
    ("non_bs_short_stuck", "no BS donor; total_len<=18; search never beat the root length"),
    ("non_bs_mid_reduced", "no BS donor; 19<=total_len<=21; search found a shorter state than root"),
    ("non_bs_mid_stuck", "no BS donor; 19<=total_len<=21; search never beat the root length"),
    ("non_bs_long_reduced", "no BS donor; total_len>=22; search found a shorter state than root"),
    ("non_bs_long_stuck", "no BS donor; total_len>=22; search never beat the root length"),
]
CLUSTER_DESC = dict(CLUSTER_DEFS)


def assign_cluster(feat: dict, best_reduction: int) -> str:
    if feat["bs_general"]:
        if feat["bs_preflight_status"] == "accept":
            return "bs_accept_budget_starved"
        sl = feat["stalled_stable_letters"]
        if sl == 3:
            return "bs_stalled_lo"
        if sl == 7:
            return "bs_stalled_hi"
        # Defensive fallback: no bs_general row in this census failed to land in
        # one of the three buckets above, but keep the pipeline total in case a
        # rerun on different data surfaces a new stable_letters value.
        return "bs_stalled_hi" if (sl or 0) >= 5 else "bs_stalled_lo"
    reduced = "reduced" if best_reduction > 0 else "stuck"
    return f"non_bs_{feat['length_bucket']}_{reduced}"


# ------------------------------------------------------------------------------- extremes / sampling

def build_extremes(features: list[dict], reductions: dict[str, int]) -> list[str]:
    """Ordered, de-duplicated list of row names that MUST be force-placed into a
    panel (round-robin dev/val/test) before proportional stratified sampling
    fills the rest. Order matters: the plain_s20/accept row is listed first so
    it lands in dev, where PANELS.md and the final report show full detail."""
    by_name = {f["name"]: f for f in features}
    ordered: list[str] = []
    seen: set[str] = set()

    def add_many(names):
        for nm in names:
            if nm not in seen:
                seen.add(nm)
                ordered.append(nm)

    # 1) the single preflight-ACCEPT / plain_s20 residual row -- first priority.
    add_many(f["name"] for f in features if f["bs_preflight_status"] == "accept")

    # 2) largest-T rows (the bs_stalled_hi cluster, T=6 -- the largest T value present).
    add_many(sorted((f["name"] for f in features if f["T"] == max(f["T"] for f in features)),
                     key=lambda nm: by_name[nm]["name"]))

    # 3) the longest rows by total_len (ties broken by name for determinism).
    add_many(f["name"] for f in sorted(features, key=lambda f: (-f["total_len"], f["name"]))[:6])

    # 4) largest class size (n_members).
    add_many(f["name"] for f in sorted(features, key=lambda f: (-f["n_members"], f["name"]))[:6])

    # 5) rows where the search made zero length progress at all AND are long
    #    (non_bs_long_stuck is the rarest structural cell: 3 rows).
    add_many(f["name"] for f in features
             if f["length_bucket"] == "long" and reductions[f["name"]] == 0)

    # 6) any row carrying a primitive-one-occurrence or two-block gate flag (there
    #    happen to be none among the 727 -- Stage 1's terminal macros already
    #    consumed every such row -- but keep this future-proof rather than assume it).
    add_many(f["name"] for f in features
             if f["two_block_gate"] or f["primitive_one_occurrence1"] or f["primitive_one_occurrence2"])

    return ordered


def stratified_panels(features: list[dict], clusters: dict[str, str], extremes: list[str]):
    """Disjoint dev/val/test (~100 each) + rest, stratified over clusters,
    with `extremes` force-placed round-robin first. One random.Random(SEED)
    instance, consumed in a fixed order, makes this exactly reproducible."""
    rng = random.Random(SEED)
    panels = {"dev": [], "val": [], "test": []}
    panel_of: dict[str, str] = {}
    cycle = ["dev", "val", "test"]

    # Step 1: force-place extremes round robin, skipping a row already placed
    # by an earlier group (add_many above already de-duplicates names, but the
    # skip check is kept here too so the function is safe to reuse standalone).
    i = 0
    for name in extremes:
        if name in panel_of:
            continue
        p = cycle[i % 3]
        panel_of[name] = p
        panels[p].append(name)
        i += 1

    # Step 2: proportional per-cluster stratified draw for the remainder.
    by_cluster: dict[str, list[str]] = defaultdict(list)
    for f in features:
        by_cluster[clusters[f["name"]]].append(f["name"])

    total_n = len(features)
    target_each = DEV_TARGET  # 100, same for dev/val/test

    for cid in sorted(by_cluster):
        members = by_cluster[cid]
        cluster_size = len(members)
        # rows in this cluster not already spoken for by an extreme
        remaining = [nm for nm in members if nm not in panel_of]
        rng.shuffle(remaining)
        # proportional target per panel from the *whole* cluster (so extremes
        # already drawn from it count against the quota), floored at 1 when the
        # cluster is large enough to guarantee coverage in every panel.
        raw_quota = cluster_size * target_each / total_n
        quota = max(1, round(raw_quota)) if cluster_size >= 3 else round(raw_quota)
        cursor = 0
        for p in cycle:
            already = sum(1 for nm in members if panel_of.get(nm) == p)
            need = max(0, quota - already)
            take = remaining[cursor:cursor + need]
            cursor += len(take)
            for nm in take:
                panel_of[nm] = p
                panels[p].append(nm)

    # Step 3: top-up pass so each panel hits exactly target_each, pulling from
    # whatever is still unassigned, round robin, single fixed shuffle.
    unassigned = [f["name"] for f in features if f["name"] not in panel_of]
    rng.shuffle(unassigned)
    idx = 0
    targets = {"dev": DEV_TARGET, "val": VAL_TARGET, "test": TEST_TARGET}
    changed = True
    while changed and idx < len(unassigned):
        changed = False
        for p in cycle:
            if len(panels[p]) >= targets[p]:
                continue
            if idx >= len(unassigned):
                break
            nm = unassigned[idx]
            idx += 1
            panel_of[nm] = p
            panels[p].append(nm)
            changed = True

    rest = [f["name"] for f in features if f["name"] not in panel_of]
    for p in cycle:
        panels[p].sort(key=lambda nm: int(nm.split("_")[-1]))
    rest.sort(key=lambda nm: int(nm.split("_")[-1]))
    return panels, rest


def stratified_regression(near_limit_900: list[dict]):
    """~60-row stratified sample of the near-limit SOLVED pool (nodes_explored
    >= 900), stratified by route and by total_len bucket. In this census the
    pool turns out to be entirely route=incumbent_restart (see report), so the
    route stratum collapses to one value and length is the operative axis."""
    rng = random.Random(SEED)

    def total_len_of(d):
        return len(d["pair"][0]) + len(d["pair"][1])

    by_stratum: dict[tuple, list[dict]] = defaultdict(list)
    for d in near_limit_900:
        by_stratum[(d["route"], length_bucket(total_len_of(d)))].append(d)

    pool_size = len(near_limit_900)
    chosen: list[dict] = []
    for key in sorted(by_stratum):
        group = sorted(by_stratum[key], key=lambda d: d["name"])
        rng.shuffle(group)
        quota = max(1, round(len(group) * REGRESSION_TARGET / pool_size))
        chosen.extend(group[:quota])

    # Trim / top up to land close to REGRESSION_TARGET, deterministically.
    chosen_names = {d["name"] for d in chosen}
    if len(chosen) > REGRESSION_TARGET:
        rng.shuffle(chosen)
        chosen = chosen[:REGRESSION_TARGET]
    elif len(chosen) < REGRESSION_TARGET:
        leftover = [d for d in near_limit_900 if d["name"] not in chosen_names]
        rng.shuffle(leftover)
        chosen.extend(leftover[:REGRESSION_TARGET - len(chosen)])

    chosen.sort(key=lambda d: int(d["name"].split("_")[-1]))
    return chosen


# ---------------------------------------------------------------------------------- CSV writers

def write_features_csv(features: list[dict]):
    cols = [
        "name", "r1", "r2", "canon_r1", "canon_r2", "len1", "len2", "total_len", "max_len",
        "n_members", "S", "MK", "W", "abelian_det", "ex1", "ey1", "ex2", "ey2",
        "x_blocks1", "y_blocks1", "x_blocks2", "y_blocks2",
        "bs_general", "bs_m", "bs_donor_index", "bs_preflight_status", "stalled_stable_letters",
        "T", "route", "prepass_charges", "plain_charges", "best_state_r1", "best_state_r2",
        "best_total_len", "best_reduction", "two_block_gate",
        "primitive_one_occurrence1", "primitive_one_occurrence2", "cluster",
    ]
    with open(OUT_DIR / "features_727.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in features:
            w.writerow({c: row[c] for c in cols})


def write_clusters_csv(features: list[dict]):
    with open(OUT_DIR / "clusters.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "cluster", "description"])
        for row in features:
            w.writerow([row["name"], row["cluster"], CLUSTER_DESC[row["cluster"]]])


def write_panel_csv(path: Path, names: list[str], by_name: dict[str, dict], clusters: dict[str, str]):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "name", "r1", "r2", "cluster"])
        for nm in names:
            row = by_name[nm]
            w.writerow([row["index"], nm, row["r1"], row["r2"], clusters[nm]])


def write_regression_csv(path: Path, records: list[dict], with_elementary=True):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        header = ["index", "name", "r1", "r2", "nodes_explored", "route"]
        if with_elementary:
            header.append("elementary_count")
        w.writerow(header)
        for d in records:
            row = [d["index"], d["name"], d["pair"][0], d["pair"][1], d["nodes_explored"], d["route"]]
            if with_elementary:
                row.append(d.get("elementary_count", ""))
            w.writerow(row)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------------------- PANELS.md

def write_panels_md(features, clusters, panels, rest, near_limit_900, near_limit_950,
                     route_counts_900, regression60, manifest):
    by_name = {f["name"]: f for f in features}
    cluster_counts = Counter(clusters[f["name"]] for f in features)
    panel_cluster_counts = {p: Counter(clusters[nm] for nm in panels[p]) for p in ("dev", "val", "test")}

    lines = []
    lines.append("# Residual evaluation panels -- AC19 census, 2026-09-09\n")
    lines.append(
        "Panels built from the 727 unsolved rows of the frozen `final_policy.search(pair, "
        "budget=1000)` AC19 census (`results/heuristic_search/ac19_final_policy_full_1k/"
        "unsolved.csv`), plus a regression panel of solved rows near the 1,000-unit limit. "
        "Generated by `research/residual_20260909/panels/build_panels.py`, seed "
        f"`{SEED}`.\n"
    )

    lines.append("## Method\n")
    lines.append(
        "1. **Features** (`features_727.csv`): for every residual row, `canon_pair` first "
        "(rotation/inversion/swap invariant), then `L`/`S`/`MK` via "
        "`experiments.heuristic_search.core.hfast._feats_nj` exactly as "
        "`heuristic_1k.score_key` computes them (`f[0]`, `f[7]`, `f[5]`), `W` as "
        "`min(heuristic_1k.response(codes))` over the 4 ordered Nielsen maps, the abelian "
        "determinant and per-relator exponent sums/block counts from "
        "`experiments.equivalence_classes.lib.words`, the BS-donor recognition "
        "(`cheap_gates.bs_gate(pair, general=True)`) and preflight "
        "(`bs_preflight.preflight`) status/stable-letter count, the donor-relative `T` "
        "feature (`mid_search.bs_escape_feature`), the two-block and primitive "
        "one-occurrence gate flags, and `best_reduction = total_len - "
        "best_total_len` from each row's failing-search shard (`rows_*.jsonl`).\n"
    )
    lines.append(
        "2. **Clustering** (`clusters.csv`): 9 mutually exclusive, exhaustive clusters. "
        "Primary axis is the BS-donor / preflight structure (the frozen policy's own `T` "
        "obstruction, plus the one preflight-ACCEPT row -- see Surprising facts below); the "
        "route axis was tried but is degenerate on the residual (726/727 rows are "
        "`incumbent_restart`, 1 is `plain_s20`), so the lone `plain_s20` row is folded into "
        "the BS axis instead, where it structurally belongs. The remaining 708 non-BS rows "
        "are split by total-length bucket (`short<=18`, `19<=mid<=21`, `long>=22`, chosen "
        "from the residual's own quartiles) crossed with whether the failing search ever "
        "found a state shorter than its root (`best_reduction>0`) at all.\n"
    )
    lines.append(
        "3. **Panels** (`dev.csv`/`val.csv`/`test.csv`/`rest.csv`): `random.Random(20260909)`, "
        "one instance consumed in a fixed order (extremes round-robin, then clusters sorted "
        "by id, then a single top-up pass). Extremes -- the preflight-ACCEPT row, the "
        "largest-`T` rows, the longest rows, the largest-`n_members` rows, and the "
        "`non_bs_long_stuck` cell -- are force-placed round-robin across dev/val/test "
        "*before* proportional stratified sampling fills the rest, so they are distributed "
        "across all three panels rather than concentrated in dev. Every cluster with >=3 "
        "residual rows gets a floor of 1 row per panel. dev/val/test are exactly disjoint "
        "(each name assigned to at most one panel); everything else is `rest.csv`.\n"
    )
    lines.append(
        "4. **Regression panel** (`regression60.csv`, `regression_all_near_limit.csv`): from "
        "the 74 `rows_*.jsonl` shards, every **solved** row with `nodes_explored >= 900` "
        f"(the pool `regression60` stratifies from) and every solved row with "
        "`nodes_explored >= 950` (`regression_all_near_limit.csv`, for later full-regression "
        "checks). Same seed, stratified by (route, length bucket).\n"
    )

    lines.append("## Cluster table\n")
    lines.append("| cluster | description | n | dev | val | test | rest |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for cid, desc in CLUSTER_DEFS:
        n = cluster_counts.get(cid, 0)
        d = panel_cluster_counts["dev"].get(cid, 0)
        v = panel_cluster_counts["val"].get(cid, 0)
        t = panel_cluster_counts["test"].get(cid, 0)
        r = n - d - v - t
        lines.append(f"| `{cid}` | {desc} | {n} | {d} | {v} | {t} | {r} |")
    lines.append(f"| **total** |  | **{sum(cluster_counts.values())}** | "
                  f"**{len(panels['dev'])}** | **{len(panels['val'])}** | "
                  f"**{len(panels['test'])}** | **{len(rest)}** |\n")

    lines.append("## Near-limit regression pool\n")
    lines.append(
        f"Solved rows with `nodes_explored >= {REGRESSION_NODES_MIN_PANEL}`: "
        f"**{len(near_limit_900)}** total, by route: "
        + ", ".join(f"`{r}`: {c}" for r, c in sorted(route_counts_900.items())) + ". "
        f"Solved rows with `nodes_explored >= {REGRESSION_NODES_MIN_ALLROW}`: "
        f"**{len(near_limit_950)}** (all `incumbent_restart` -- see Surprising facts). "
        f"`regression60.csv` draws {len(regression60)} rows from the >=900 pool, stratified "
        "by (route, length bucket); since the pool is entirely `incumbent_restart`, length "
        "bucket is the operative stratum.\n"
    )

    lines.append("## Dev panel (full detail -- val/test are counts only, by design)\n")
    lines.append(
        "The dev panel is the only panel whose rows are listed here or in the final report. "
        "val.csv and test.csv exist on disk with the same schema but are deliberately not "
        "enumerated in this document so they stay unseen during rule development.\n"
    )
    lines.append("| index | name | cluster | total_len | S | MK | W | T | bs_general | "
                  "best_reduction | n_members |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---:|---|---:|---:|")
    for nm in panels["dev"]:
        row = by_name[nm]
        lines.append(
            f"| {row['index']} | {nm} | `{clusters[nm]}` | {row['total_len']} | "
            f"{row['S']:.3f} | {row['MK']:.0f} | {row['W']} | {row['T']} | "
            f"{row['bs_general']} | {row['best_reduction']} | {row['n_members']} |"
        )
    lines.append("")

    lines.append("## val / test panels -- counts only\n")
    for p in ("val", "test"):
        lines.append(f"**{p}.csv**: {len(panels[p])} rows. Cluster counts: "
                      + ", ".join(f"`{cid}`: {panel_cluster_counts[p].get(cid, 0)}"
                                   for cid, _ in CLUSTER_DEFS) + ".")
    lines.append("")

    lines.append("## Surprising structural facts about the 727 residual\n")
    n_bs = sum(1 for f in features if f["bs_general"])
    n_stalled = sum(1 for f in features if f["T"] > 0)
    n_accept = sum(1 for f in features if f["bs_preflight_status"] == "accept")
    n_reduced = sum(1 for f in features if f["best_reduction"] > 0)
    sl_counts = Counter(f["stalled_stable_letters"] for f in features if f["stalled_stable_letters"] is not None)
    bs_m_counts = Counter(f["bs_m"] for f in features if f["bs_m"] is not None)
    n_two_block = sum(1 for f in features if f["two_block_gate"])
    n_one_occ = sum(1 for f in features if f["primitive_one_occurrence1"] or f["primitive_one_occurrence2"])
    lines.append(f"- `{n_bs}`/727 rows ({n_bs/727:.1%}) have a recognized general consecutive-BS "
                 f"donor at all (`bs_general`); `{n_stalled}` of those are genuinely stalled "
                 "(`T>0`, preflight rejects with >1 stable letter left).")
    lines.append(f"- Exactly `{n_accept}` residual row has a preflight **ACCEPT** "
                 "(`bs_preflight_status=='accept'`) -- a certified reduction exists in principle "
                 "-- and it is the single `route=plain_s20` row in the whole residual "
                 "(`ac19_109`), with a base stable-letter exponent of 127. The frozen policy's "
                 "1000-unit budget is not enough to certify it even though it is structurally "
                 "solvable, which is a different failure mode from every other row here.")
    lines.append(f"- Stalled stable-letter counts split cleanly in two: `{sl_counts.get(3, 0)}` "
                 f"rows stall with 3 stable letters left (`T=2`), `{sl_counts.get(7, 0)}` "
                 "with 7 left (`T=6`) -- no residual row stalls anywhere in between.")
    lines.append("- `bs_m` (the recognized donor's BS(m,m+1) parameter) distribution among the "
                 f"{n_bs} bs_general rows: " + ", ".join(f"m={m}: {c}" for m, c in sorted(bs_m_counts.items())) + ".")
    lines.append(f"- `{n_reduced}`/727 rows ({n_reduced/727:.1%}) have `best_reduction>0` -- the "
                 "failing search did find a shorter state than its root at some point; "
                 f"`{727-n_reduced}` never beat the root length at all across the full 1000-unit "
                 "budget.")
    lines.append(f"- `{n_two_block}` residual rows carry the `two_block_gate` flag and "
                 f"`{n_one_occ}` carry a `primitive_one_occurrence` flag on either relator -- "
                 "zero, in this census. Stage 1's terminal macros for those gates are evidently "
                 "saturating: every row where they would fire is already solved.")
    lines.append(f"- Near-limit regression pool: all {len(near_limit_900)} solved rows with "
                 f"nodes_explored>={REGRESSION_NODES_MIN_PANEL} are route=`incumbent_restart`; "
                 "no `strict_donor` row gets anywhere near the limit (`strict_donor` caps at "
                 "250 units by construction) and no `plain_s20` solve exceeds 889 nodes, so the "
                 "`plain_s20` stratum of the regression pool is empty by construction, not by "
                 "sampling choice.")
    lines.append("")

    lines.append("## Manifest\n")
    lines.append("| file | sha256 | rows |")
    lines.append("|---|---|---:|")
    for fname, meta in manifest["files"].items():
        lines.append(f"| `{fname}` | `{meta['sha256']}` | {meta['rows']} |")
    lines.append(f"\nSeed: `{manifest['seed']}`. Script: `{manifest['script']}`.\n")

    (OUT_DIR / "PANELS.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------------------- main

def main():
    unsolved = load_unsolved()
    members = load_members()
    needed_names = {r["name"] for r in unsolved}

    shard_rec, near_limit_900, near_limit_950, route_counts_900 = scan_shards(needed_names)

    features = []
    reductions = {}
    for r in unsolved:
        name = r["name"]
        feat = compute_features(name, r["r1"], r["r2"], members[name])
        feat["index"] = r["index"]
        feat["route"] = r["route"]
        rec = shard_rec[name]
        assert rec["route"] == r["route"], f"{name}: route mismatch shard vs unsolved.csv"
        assert rec["nodes_explored"] == int(r["nodes_explored"]), f"{name}: nodes_explored mismatch"
        feat["prepass_charges"] = rec["prepass_charges"]
        feat["plain_charges"] = rec["plain_charges"]
        best_state = rec["best_state"]
        feat["best_state_r1"], feat["best_state_r2"] = best_state[0], best_state[1]
        best_total_len = sum(len(w) for w in best_state)
        feat["best_total_len"] = best_total_len
        best_reduction = feat["total_len"] - best_total_len
        feat["best_reduction"] = best_reduction
        reductions[name] = best_reduction
        features.append(feat)

    clusters = {}
    for f in features:
        cid = assign_cluster(f, reductions[f["name"]])
        f["cluster"] = cid
        clusters[f["name"]] = cid
    assert sum(Counter(clusters.values()).values()) == 727

    extremes = build_extremes(features, reductions)
    panels, rest = stratified_panels(features, clusters, extremes)

    # Disjointness / coverage sanity checks.
    all_paneled = panels["dev"] + panels["val"] + panels["test"]
    assert len(set(all_paneled)) == len(all_paneled), "a row landed in more than one panel"
    assert set(all_paneled) & set(rest) == set()
    assert set(all_paneled) | set(rest) == needed_names
    assert len(panels["dev"]) + len(panels["val"]) + len(panels["test"]) + len(rest) == 727

    regression60 = stratified_regression(near_limit_900)

    by_name = {f["name"]: f for f in features}

    write_features_csv(features)
    write_clusters_csv(features)
    write_panel_csv(OUT_DIR / "dev.csv", panels["dev"], by_name, clusters)
    write_panel_csv(OUT_DIR / "val.csv", panels["val"], by_name, clusters)
    write_panel_csv(OUT_DIR / "test.csv", panels["test"], by_name, clusters)
    write_panel_csv(OUT_DIR / "rest.csv", rest, by_name, clusters)
    write_regression_csv(OUT_DIR / "regression60.csv", regression60, with_elementary=True)
    write_regression_csv(OUT_DIR / "regression_all_near_limit.csv", near_limit_950, with_elementary=True)

    manifest_files = {}
    for fname in ("features_727.csv", "clusters.csv", "dev.csv", "val.csv", "test.csv",
                  "rest.csv", "regression60.csv", "regression_all_near_limit.csv"):
        path = OUT_DIR / fname
        with open(path, newline="") as f:
            rowcount = sum(1 for _ in csv.reader(f)) - 1
        manifest_files[fname] = {"sha256": sha256_of(path), "rows": rowcount}

    manifest = {
        "seed": SEED,
        "script": SCRIPT_REL_PATH,
        "inputs": {
            "unsolved_csv": str(UNSOLVED_CSV.relative_to(REPO)),
            "shards_glob": str(Path(SHARD_GLOB).relative_to(REPO)),
            "members_csv": str(MEMBERS_CSV.relative_to(REPO)),
        },
        "counts": {
            "residual_total": 727,
            "dev": len(panels["dev"]), "val": len(panels["val"]), "test": len(panels["test"]),
            "rest": len(rest),
            "near_limit_900_pool": len(near_limit_900),
            "near_limit_900_by_route": dict(route_counts_900),
            "near_limit_950_pool": len(near_limit_950),
            "regression60": len(regression60),
        },
        "files": manifest_files,
    }
    (OUT_DIR / "panel_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n")

    write_panels_md(features, clusters, panels, rest, near_limit_900, near_limit_950,
                     route_counts_900, regression60, manifest)

    # ------------------------------------------------------------------------------- console report
    print(f"residual rows:            727")
    print(f"clusters:                 {len(CLUSTER_DEFS)}")
    print(f"dev/val/test/rest:        {len(panels['dev'])}/{len(panels['val'])}/"
          f"{len(panels['test'])}/{len(rest)}")
    print(f"near-limit pool (>=900):  {len(near_limit_900)}  by route: {dict(route_counts_900)}")
    print(f"near-limit pool (>=950):  {len(near_limit_950)}")
    print(f"regression60:             {len(regression60)}")
    print("cluster sizes:", dict(Counter(clusters.values())))
    print(f"wrote files under {OUT_DIR}")


if __name__ == "__main__":
    main()
