"""Single source of truth for the d-o-t data-crafting pipeline.

See ``experiments/eda+data_collection/4.DETAILED_STEPS_DATA_CRAFTING.md`` §A. This is a
*pure* module: agreed constants plus one band helper, no file IO. Every build script
(``phase0_baseline``, future ``build_anchors`` / ``build_training_archive`` /
``dot_dataset.make_splits_v2``) imports its knobs from here so there is no copy-paste drift.

Data-derived values (``B_soft`` / ``B_hard``) are deliberately NOT stored here: Phase 0
derives them live from the archive and writes them to ``PERCENTILES_JSON``. The
``*_EXPECTED`` constants below are the documented targets Phase 0 asserts the live
derivation against.
"""

# ---- env / reproducibility ----
L = 24                     # per-relator max_length (env invariant)
SEED = 0                   # frozen splits

# ---- target loss-mass mixture (4-§2) ----
TARGET_SHARES = {"easy": 0.25, "valley": 0.35, "hard_solved": 0.15, "hard_unsolved": 0.25}

# ---- difficulty bands by d-o-t; inclusive int ranges, hard_solved open-ended (4-§2) ----
BAND_EDGES = {"easy": (0, 10), "valley": (11, 50), "hard_solved": (51, None)}

# ---- weighting (4-§2) ----
WEIGHT_CLIP = (0.25, 5.0)
TAIL_DOT_THRESHOLD = 100   # d-o-t above this is treated as a loose upper-bound label
TAIL_MULT = 0.5
SHORT_HARD_MULT = 3.0      # applied to short_hard / named rows, then capped at WEIGHT_CLIP[1]

# ---- anchors (4-§3a) ----
AK_MIN, AK_MAX = 3, 8      # AK(n) series; cap=8 keeps growth headroom (2*8+1 = 17 <= L)

# ---- diversity / decorrelation (4-§2) ----
DIVERSITY_STRIDE = 2       # keep every k-th easy-band state along a path
PER_PATH_CAP = 40          # max easy-band states kept per source path

# ---- censored hinge bounds (4-§4): derived live in Phase 0, asserted against these ----
B_SOFT_EXPECTED = 48       # round(p90) of solved d-o-t
B_HARD_EXPECTED = 150      # round(p99) of solved d-o-t
B_TOL = 2                  # tolerance for the Phase 0 assertion

# ---- paths (relative to repo root; run entry points from there) ----
# Raw/env-loaded datasets live at data/ root (the env hardcodes data/<stem>.txt); all
# pipeline-generated files live under data/derived/. See data/README.md.
ARCHIVE = "data/derived/labels/dot_archive.jsonl"                   # mirrors dot_dataset.ARCHIVE
MERGED_PATHS = "data/derived/paths/merged_best_paths.jsonl"
GREEDY_CSV = "data/all_presentations_len_8_to_19_GS_solved_copy2.csv"   # raw source (root)
PERCENTILES_JSON = "data/derived/dot/percentiles.json"
BASELINE_JSON = "data/derived/dot/baseline_distribution.json"
ANCHORS_JSONL = "data/derived/dot/anchors.jsonl"          # Phase 1: named anchor rows
TRAP_SET_JSON = "data/derived/dot/ak_trap_set.json"       # Phase 1: search-time known-basin keys
ARCHIVE_V2 = "data/derived/labels/dot_archive_v2.jsonl"   # Phase 6: emitted v2 training archive


def band_of(dot):
    """Map a numeric d-o-t to its difficulty band name.

    Canonical band definition shared by Phase 0.3 (baseline snapshot) and Phase 5.1
    (weighting). Censored rows carry no d-o-t and are assigned ``hard_unsolved`` by the
    caller, not here.
    """
    for name, (lo, hi) in BAND_EDGES.items():
        if dot >= lo and (hi is None or dot <= hi):
            return name
    raise ValueError(f"d-o-t {dot!r} fell outside all bands")
