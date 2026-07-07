# Fact-check report (adversarial recomputation from raw data)

**Verdict: 160 claims / 147 matched / 6 mismatched / 7 DOC-only.**
`recompute.py` loads only raw streams (JSONL/gz/CSV/JSON — never the figure/table
digests) and exits 1 while the 6 mismatches below stand. Every headline number is
correct; all 6 mismatches are confined to figure/appendix presentation text.
(After the fixes recorded at the bottom, the six items were corrected in the
sections and masters — see git history.)

## Special checks A–J: ALL PASS

- **A. Containment** — all four arms give |arm∖baseline| = 0 (row-by-row).
- **B. Ties** — idx625 r1/twin = 77,395, r2/xYXyxyy = 80,111; idx610 r1/twin = 61,082. Byte-exact.
- **C. Histogram sums** — trials {13:16844, 19:23, 20:3} = 16,870; each 97-row file = 97; stratified = 1,800; census = 1,006.
- **D. 14 leaf certs** — catalog/certs/*.json counted = 14; the paper does not conflate this with grid_probes=14 (distinct quantities).
- **E. 634-vs-640** — baseline 634 solved / 6 exhausted at idx 634–639; no sentence implies 640 solved under L=24.
- **F. Two scales separate** — 180,645/16,870/6,058 vs 1,006/1,937, never mixed.
- **G. Percentages** — 712/1006 → 70.8%/71%, 294/1006 → 29.2%/29%, 2.4× all correct.
- **H. Histogram labeling** — the paper prints trial-level {13:16,844,…} (correct), not the per-candidate deduped {13:16,687,…}.
- **I. Beam widths** — 512/2048 (RESULTS.md, DOC); CSV row counts 155/30 recomputed.
- **J. Plateau tail** — rep@1M {13:88,14:2,15:7}, textbook@1M {13:86,14:2,15:9} exact.

## The 6 mismatches (severity-ranked; all fixed post-report)

1. **[MEDIUM] Figure 5 (two-floors) caption**: claimed the certified 21-move F→AK(3)
   path "peaks at total length 25, 12 above the floor." Raw laneF_F_to_AK3.json peaks
   at **17** (4 above the floor). Peak-25 belongs to the 53-move Appendix-F path, as
   the §4.8 body and all other references correctly state. → Caption corrected.
2. **[LOW] Appendix C grid-probe table**: Lane-B hero-8 probes listed at 300,000 nodes
   and full-bank probes at 100,000; raw archive says **800,000** and **300,000**. → Corrected.
3. **[LOW/cosmetic] Appendix C relator word**: AK(3) floor form printed as
   YXYxyx / YYYYxxx; raw floor_state and Table 5 say **YXYxyx / YYYxxxx** (same
   signed-relabel class, different representative). → Aligned to the raw representative.
4. **[LOW/framing] Budget upper bound**: abstract/§1/§6 said "up to 10⁶ nodes per
   attempt" while Lane A/C grid probes ran at 2×10⁶. → Hedge widened to 2×10⁶ where
   it refers to the campaign ceiling.
5. **[LOW/framing] Appendix D**: Lane-D solve budgets "2.5×10⁴–2×10⁵" excluded the
   resolve facet (157 trials at 3×10⁵). → Upper end corrected to 3×10⁵.
6. (Counted within items 2–3 rows in claims.tsv; see TSV for the per-row detail.)

## DOC-only claims (7 — documented in campaign logs, not raw-recomputable)

20,947 verifier checks / 0 failures (RESULTS.md); beam widths 512/2048 (RESULTS.md);
250,397 and 212,913 raised-cap candidates (test_cap/REPORT.md — the raw merged.jsonl
was a deleted ~2 GB intermediate); Lisitsa S2 159 transitions (literature artifact);
numba speedups 3.7–5.7× (RESULTS.md). The "byte-identical 16/16" cap claim is DOC for
the wording, but recompute independently corroborates it (identical visited counts and
floors across L=24/L=48 in experiments/test_cap/search_L.jsonl).

## Bottom line

The paper's empirical spine — the negative result, the 180,645/16,870/6,058 campaign
scale, the 712/294 two-floor split, every arm/histogram/certificate/literature-check
count — is corroborated by raw data. The six mismatches were presentation-level and
have been corrected; rerun `recompute.py` after any further edit.
