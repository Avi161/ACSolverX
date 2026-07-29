# Harvest search: key the seen-set on cyclically-reduced forms, not exact realizations

2026-07-29, fable line, R1d harvest round 1.

- [TRAP] With 8 of 12 h-moves being conjugations, a best-first harvest keyed on exact
  words (even quotienting rotation × inversion × swap) spends ~97% of its pops on
  conjugacy churn: 29,494 pops produced 45,466 exact states but only 1,009 distinct
  presentations up to cyclic reduction; one "top-E tier" of 267 states was 267 conjugate
  realizations of a single already-censused presentation. Contract-key novelty counts
  were inflated ~45×.
- [TRAP] Exact-word dedup also makes the search REALIZATION-SENSITIVE: three roots that
  are rotations of one another (identical canonical key) yielded 9 / 6 / 2,165 new
  states, because whichever rotation enters the seen-set first blocks the others, and
  only one realization admitted the length-collapsing concatenation.
- [WORKS] Key the seen-set on the cyclically-REDUCED canonical form (γ_N testing happens
  on reduced forms anyway — reduction is AC3 + free reduction, class-preserving), and
  record exact realizations only as provenance. Verify a sample of move chains replays
  exactly (305/305 here).
- [WORKS] Validate the E-yield implementation against two independent anchors before
  ranking anything by it (E(AK3) = 1/225 and a known cross-state ratio: 8.566 vs the
  recorded 8.6).
- Outcome for the record: 331 truly-novel ≤21 presentations in AK(3)'s classical class
  (35 of reduced length ≤ 17 — the stratum the codex ceiling-17 census cannot reach),
  100% K₄/K₄−e, all NOT_SPHERICAL by the oracle (ΣE ≈ 0.098, so zero hits is consistent);
  fable-solver confirmation pending.
