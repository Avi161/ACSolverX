# Residual campaign (2026-09-09): the 727 unsolved AC19 Aut-minimal rows

Starting point: commit 98f719e2 (verified 1k census, 72,052/72,779 solved,
727 unsolved, `results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv`).

Layout (filled in during the session):

- `panels/`   stratified disjoint panels drawn from the 727 residual (dev / val
              / test, ~100 each) and a ~60-row near-limit regression panel of
              already-solved rows; `PANELS.md` documents the method and hashes.
- `screens/`  bounded empirical screens (per-row JSONL, atomic writes,
              decode + independent replay for every claimed solve).
- `theory/`   proofs, path-mining reports, planted positive / adversarial
              negative tests for candidate completion rules.
- `harness.py`, `policies.py`  experiment runner and policy registry.

Rules of the campaign: the frozen census files are never modified; the val
panel is hidden while rules are invented; the test panel is inspected once,
after the candidate is frozen; every claimed solve is decoded to elementary
AC moves and independently replayed to `(x,y)`.
