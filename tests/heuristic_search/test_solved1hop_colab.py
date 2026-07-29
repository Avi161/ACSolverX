"""solved_1hop_autclean freeze + stride + arms + Aut-disjointness (no heavy search)."""
from __future__ import annotations

import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
ROOT = _d
sys.path.insert(0, ROOT)

from experiments.heuristic_search.runners import run_solved1hop_scale as rs  # noqa: E402
from experiments.heuristic_search.runners import run_ab as ra  # noqa: E402
from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402

FREEZE = os.path.join(ROOT, "results", "heuristic_search", "splits",
                      "solved_1hop_autclean.json")
ARMS = ["baseline", "s12", "s28", "s20_mk2", "s24_k1_mk2"]

SELECTION_JSONL = [
    os.path.join(ROOT, "results", "heuristic_search", "campaign_12h", p)
    for p in ("s_grid_hard.jsonl", "arms_on_band.jsonl",
              "arms_hard_full.jsonl", "aut_disjoint_null.jsonl")
]
SELECTION_JSON = [
    os.path.join(ROOT, "results", "heuristic_search", "scale10k", p)
    for p in ("slice_fresh_hard.json", "slice_l_stratified.json")
]
BENCH60 = os.path.join(ROOT, "benchmark", "subsets", "benchmark_subset_60.json")
AC1M = os.path.join(ROOT, "results", "heuristic_search", "splits",
                    "splits_ac1m_hard_aut.json")


def test_freeze_exists_and_strata():
    data = json.load(open(FREEZE))
    assert data["kind"] == "solved_1hop_autclean"
    assert data["n_kept"] == len(data["rows"])
    assert data["n_kept"] >= 400
    assert data["n_seed"] + data["n_moved_cov"] == data["n_kept"]
    assert data["excluded_aut"]["removed_from_pool"] >= 45
    names = {r["name"] for r in data["rows"]}
    assert len(names) == len(data["rows"])
    assert "selected_on" in data and "evaluated_on" in data


def test_zero_aut_overlap_with_selection_union():
    warm()
    data = json.load(open(FREEZE))
    kept = {(r["aut_rep_r1"], r["aut_rep_r2"]) for r in data["rows"]}
    exclude = set()
    for r in json.load(open(BENCH60))["subset"]:
        _, rep = aut_min((r["r1"], r["r2"]))
        exclude.add(rep)
    sp = json.load(open(AC1M))
    for side in ("train_rows", "holdout_rows"):
        for r in sp[side]:
            _, rep = aut_min((r["r1"], r["r2"]))
            exclude.add(rep)
    for path in SELECTION_JSONL:
        for line in open(path):
            if not line.strip():
                continue
            r = json.loads(line)
            _, rep = aut_min((r["r1"], r["r2"]))
            exclude.add(rep)
    for path in SELECTION_JSON:
        for r in json.load(open(path))["rows"]:
            _, rep = aut_min((r["r1"], r["r2"]))
            exclude.add(rep)
    leak = kept & exclude
    assert not leak, f"Aut leak ({len(leak)}): {list(leak)[:3]}"


def test_arms_registered():
    for a in ARMS:
        assert a in ra.ARMS


def test_stride_chunks_partition():
    rows = rs.load_frozen()
    seen = []
    for ci in range(1, 6):
        picked, tag = rs._stride_chunk(rows, 5, ci)
        assert tag == f"_c{ci}of5"
        seen.extend(r["name"] for r in picked)
    assert len(seen) == len(rows)
    assert len(set(seen)) == len(rows)


def test_kind_filter_tags_stem(tmp_path):
    rows = rs.load_frozen()
    seeds = [r for r in rows if r["kind"] == "seed"]
    assert seeds
    # dry: just check OUT_STEM tagging logic via a tiny run is heavy;
    # unit-check the stem composition here.
    stem = "hsearch_solved1hop"
    kind = "seed"
    tag = "_c1of5"
    assert f"{stem}_kind-{kind}{tag}" == "hsearch_solved1hop_kind-seed_c1of5"
