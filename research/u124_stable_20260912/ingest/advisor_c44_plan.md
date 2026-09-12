# Wave plan audit (C44) — applied before census

Source: ac-advisor `bc-deb09c1d-46b1-537e-914e-4feb4bd573a1`, 2026-09-12.
Coordinator applied the REVISE below. Census has not been run.

**Numbering.** Committed C43 is the leftover aca_43 ncl scanner
(`code/c43_yyxxyxx_x_eq_cinv.py`). This cyclic pair-length descent is **C44**.

## BLOCKERS

None. Advisor verdict was REVISE, not BLOCK.

## WARNINGS / REVISE items applied

1. **Provenance split.** Hits and any ledger update distinguish:
   - `ordinary_displayed_initial`: BEST equals INITIAL (88-row type; 11 of
     the 13 shortest).
   - `mu_floor_best_relative`: BEST differs by a μ-floor CoV prefix (36
     rows). A drop here is a witness relative to the displayed BEST pair,
     not an ordinary archival certificate, and not a re-validated CoV
     prefix.
2. **Independent positive replay.** A length-drop witness is replayed with
   `experiments.greedy_tests.spec.moves.apply_move` + `reduce_word`
   (legacy `(target, jsign, k1, k2)`), **not** `children_fast`. Scanner
   self-replay is not a certificate. Bounded negatives keep
   `independent_checker=false`.
3. Depth counts **AC2 macro-steps**, not elementary moves. Each macro-step
   is one AC2 plus AC1/AC3 orientation, restoration, and cyclic reduction.
4. Corridor completeness is for **deduplicated exact-spelling states**:
   “All row-local exact-spelling depth-2 states of cyclic total equal to
   the input total were expanded once.” Flags `c44_1_complete` /
   `c44_2_complete`. Input SHA-256 of `aca_124_best.csv` is recorded.
   Not full depth-3; off-corridor (strictly longer unique d2) is excluded.
5. C43 identifier collision resolved by numbering this census C44. The
   aca_43 ncl draft remains C43 and is not this census.
6. C10 after an ordinary rank-2 AC1–AC3 chain to μ ≤ 12 is allowed
   (MM03 Thm 1.1). If the BEST pair was reached only by a stable CoV
   prefix, the archival conclusion is only stable. Order-120 is an
   integrity check, not a C10 exception. `aca_115` is included as AK(3)
   tripwire: μ ≤ 12 is recorded and not marked solved until independently
   reproduced. μ = 13 is never a removal.
7. `best_known_input_length` may update after independent replay from the
   exact displayed BEST pair. `best_certified_ordinary_ac_length` only for
   BEST=INITIAL. `best_certified_stable_ac_length` only after CoV-prefix
   validation under `MU_CRITERION.md` (not claimed by C44 itself).
8. New files only: `code/c44_best_length_descent.py`, JSON, and
   `tests/u124_stable_20260912/test_c44_best_length_descent.py`. Do not
   edit `test_campaign.py`. No pytest-coverage claim.

## ALLOWED CLAIMS

- Complete bounded negative for the specified exact-spelling
  equal-length-depth-2 corridor on the listed BEST inputs, once the
  completion flags are true.
- Verified strict cyclic-total decrease from displayed BEST pair X, if a
  drop is independently replayed.
- Score remains `0/124` unless a non-tripwire μ ≤ 12 endpoint is replayed.
- Not: “full depth-3 negative”, “ordinary certificate” for a CoV-floor
  row, “three-move path”, leftover 10M minima, or ncl product-word length
  11.

## VERDICT: REVISE (applied before census)
