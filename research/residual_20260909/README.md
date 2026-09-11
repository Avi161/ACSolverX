# Residual campaign (2026-09-09): the 727 unsolved AC19 Aut-minimal rows

Starting point: commit 98f719e2 (verified 1k census, 72,052/72,779 solved,
727 unsolved, `results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv`).

Outcome: **72,779 / 72,779 solved and independently verified at 1,000 charged
units per presentation**, 0 lost, 949,521 charged units in total (published:
6,621,411), 46.7 s search wall for the whole census (published: 389.2 s),
census wall 70 s on 4 workers. Bundle:
`results/heuristic_search/ac19_ball14_cascade_full_1k/`. The full account is
[`CAMPAIGN_REPORT.md`](CAMPAIGN_REPORT.md); the chronological record with every
intermediate measurement is [`NOTES.md`](NOTES.md).

Layout:

- `panels/`   stratified disjoint panels drawn from the 727 residual (dev / val
              / test, ~100 each), a 60-row near-limit regression panel of
              already-solved rows, a 12-row smoke panel and the 41-row
              round-1 residual; `PANELS.md` documents the method and hashes.
- `screens/`  bounded empirical screens (per-row JSONL, atomic writes,
              decode + independent replay for every claimed solve).
- `theory/`   proofs, path-mining reports, planted positive / adversarial
              negative tests for candidate completion rules (stalled BS,
              four-block, family theory for the round-1 residual).
- `tables/`   backward balls (exact sets of pairs with a bounded-length
              elementary path to (x, y)); manifests with hashes are committed,
              the cap-12/14 tables are rebuilt with the documented command.
- `harness.py`, `policies.py`, `policies_round2.py`  experiment runner and
              policy registry (`--policy` names).
- `backward_table.py`, `plain_search_ball.py`, `mid_search_ball.py`,
  `final_policy_ball.py`, `bs_demote_gate.py`  the table builder and the
              cascade with the table terminal; `BACKWARD_TABLE.md` is the spec.
- `census_run.py`, `census_summarize.py`, `verify_bundle.py`,
  `replay_census.py`  full-census runner (sharded, resumable, provenance
              manifest), summariser, and the two independent checks of a bundle.
- `THEOREMS_PROOFS_AND_FREQUENCY.md`  audit of every completion rule inherited
              from `research/supermoves_20260908` (hypotheses, proofs, census
              frequency, strength ranking).
- `tests/`    341 tests (`PYTHONPATH=. python3 -m pytest research/residual_20260909/tests`).

Rules of the campaign: the frozen census files are never modified; the val
panel is hidden while rules are invented; the test panel is inspected once,
after the candidate is frozen; every claimed solve is decoded to elementary
AC moves and independently replayed to `(x,y)`.
