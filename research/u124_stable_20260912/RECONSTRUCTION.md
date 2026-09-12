# Reconstruction log — verified 2026-09-12

Evidence-only. Summaries were not trusted without artifacts.

## Git and branches

- This campaign branch: `cursor/u124-stable-ac-1b54` cut from `origin/codex/proofs` @ `62b10c94` (2026-09-08, “Bind two-complement checkpoint log”).
- `codex/theory-patterns-3h` is **not on origin**. GitHub code search and `git ls-remote` both miss it.
- `fable/proofs` @ `7d8e999b` is a separate AK(3) algebraic lane (W2* checkpoints). Do not continue it as a U124 route.
- `claude/ac19-theorem-strength-8v1wp6` @ `dd06d784` holds supermoves + residual cascade + authoritative U124 CSVs.
- `claude/ac19-leftover-solver-notebook-6yan6d` @ `9f50ff3a` holds the 10M U124 ordinary search.

## U124 tables (hashes)

| file | sha256 | fact checked here |
|---|---|---|
| `aca_124_initial.csv` | `614bce2d3250a1acca81ec9de0fc0deb097eb74c4d56e6a9718985a150bb1d2c` | 124 rows, total length **2446** |
| `aca_124.csv` on proofs | same hash | **byte-identical** to initial |
| leftover `results/stable_ac/fable/aca_124.csv` | same hash | 10M search ran on **initial**, not best |
| `aca_124_best.csv` | `8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3` | 36 rows differ; total **2356** |
| `aca_124_reduced.csv` | `5be80a918b2b970e9bba7557a168908d8225ee8f781cc884cf0df6a845bbb72a` | `reduce_kind=mu_floor` on exactly those 36 |

36 changed IDs: aca_34, 36, 43, 44, 55, 58, 66, 67, 71, 72, 78, 80, 81, 85, 87, 88, 90, 95, 97, 98, 99, 100, 105–114, 120–123.

## What is already known, with strength

### Ordinary AC

- Leftover 10M-node `s20_mk2` on the **initial** 124: **0 solved**. 14 rows recorded a shorter total. Those records have **empty paths** (`track_path=False` from engine gen 4). Observed, **not certified**.
- Residual campaign 10k-unit cascade / supermove sweep on **best** 124: **0 solved, 0 shorter**, 122,842 BS-donor states all rejected by Britton preflight (`aca124_supermoves_10000.summary.json`).

### Stable CoV / μ-ladder

- `MU_CRITERION.md` Prop A: gated subword CoV is a Lemma-11 stable composite **if the presentation is of the trivial group**. Finish line μ ≤ 12.
- 8-rung ladder: 33 (later 35) classes descend; **none to μ ≤ 12**. Min non-AK3 floor 15. aca_115 is AK(3) at μ=13.
- `MS_TEMPLATE_PROPOSITION.md`: ten classes are `P_{n,δ}` and descend by `z=xy` then `z=x^n` to a one-parameter `Q_{n,δ}`. Sibling Family A: aca_43, aca_95.
- μ-ladder summary jsonl exists; companion `*_orbits.jsonl` needed by `verify_mu_ladder.py` is **not** on this branch. Chains are therefore **recorded, not re-replayed here** until identities or orbits are rebuilt.

### Ordinary completion rules (AC19 census, not U124 solves)

From `THEOREMS_PROOFS_AND_FREQUENCY.md` on theorem-strength (AC19 Aut-min 72,779 rows, all solved at 1k units):

| rule | AC19 closes | U124 10k supermove |
|---|---:|---|
| ordinary terminal | 43,406 | 0 |
| consecutive BS(m,m+1) | 24,983 | 0 (all preflight rejects) |
| primitive one-occurrence | 3,564 | not a U124 closer |
| two-block unimodular | 99 | 0 |

Cautions already measured there: BS(1,2) with companion exponent ±1 is ordinary-trivial; general BS(m,m+1) can stall on divisibility; reciprocal BS(3,2) is not free.

### Stable machinery on `codex/proofs` (AK3-oriented, reusable)

- Rank-3 isolator corridor (`AK3_RANK3_COMPRESSION.md` Thm 3.1) **PROVEN**, with code in `experiments/stable_ac/rank3_compression/corridors.py`.
- Substitution of a displayed block by a defining generator is an AC1–AC3 composite (same note §2).
- Stable ambient automorphism principle: cited to missing `PROOFS.tex`; the lesson `ambient-principle-unstable-is-not-a-theorem.md` states the **stable** form and forbids the unstable pairwise form.
- Cyclic-complement criterion: unimodular pair plus a word c generating F₂ with the pair is stably trivial at rank 3 (`AK3_PARAFREE_STABLE_SELF_EMBEDDING.md`). AK(3) itself has join corank 2 (negative graph check). Failure of the criterion is **not** an AC obstruction (AK2 control).
- Power–Bézout corridors: mechanism is Euclidean relator reduction against a power defining word; currently written at the AK(3) compression root.

## Granola / meetings

SURF notes prioritized **algorithmic** progress and treated length ≤ 12 as a practical stable threshold, not a proofs campaign. This goal is the proofs campaign anyway; meeting notes do not override the certificate standard.

## First verified computations of this campaign

- Hashes and length totals: `tables/census_summary.json`. All 124 best pairs are unimodular. 10 match MS-floor shapes. 49 have a cheap BS(m,m+1)-shaped donor (companions still fail Britton at 10k on the residual sweep). 0 one-occurrence, 0 two-block-both on best.
- MS template identities: `tables/ms_template_identities.json`, **14/14 PASS** for `n=2..8`, both signs. Literal `Q_{n,δ}` after two CoVs; `aut_min_len` after `y↦x^{-2}y` equals `n+12`. Eleven U124 initial rows are exactly `P_{n,δ}`. **Not a solve.**
- Scripts: `python3 research/u124_stable_20260912/code/u124_census.py` and `.../ms_template_identities.py`. Direct tests in `tests/u124_stable_20260912/test_campaign.py` (pytest is not installed in this image; the same functions were executed directly).

## Wave 2 (guarded 60 s, 2026-09-12)

- Q common-suffix peel: 14/14 identities; 0 length drops; commutator factorization `g⁻¹ = v[y⁻¹,x⁻¹]`; second unconjugated peel is not a descent. Family A prefix identity holds and **raises** μ.
- After the displayed peel, some AC1/AC3 orientation peels drop raw length or `x`-run. On `Q_{2,±1}` the remainder `YXyxYYXyx` is ordinary-AC legal and **raises** `aut_min_len` 14→18; it is not primitive.
- Primitive-relator census: **0/248** best relators primitive, **0/248** cyclic products primitive. All 248 have abelian gcd 1. Whitehead-min histogram starts at 5 (13 words). Shared donors include `YXXyxYx` (11 rows) and `YXXXyxYx` (11 rows).
- Depth-1 AC2 on the best table: 44,016 children, 0 cyclic-length drops, 0 new one-occurrence, 0 new two-block–both.
- Still **0/124** stably trivialized. No certificate JSONL rows.

## Wave 3 (Sol C12 REVISE, guarded 60 s)

- `ingest/advisor_wave2.md`: C11 APPROVE; C12 REVISE. Catalogue C12 now applies C1 first, expands generator deletion into AC1+AC3 donor / AC2 / restore, and labels the Aut step non-effective.
- Step-4 replay: `tables/c12_generator_deletion.json`. Unimodular mixed companions finish at `y^{±1}`; commutator leftover is empty.
- Product aggregate: 0 primitive of 248 stored-orientation products (dedicated counter, not inferred from `primitive_hits`).
- Depth-1 unique new relators: 11,686 Whitehead tests, 0 primitive, minima starting at 5 (7.5 s). Bounded report only.

## Wave 4 (theory C16–C18, independent replay, 2026-09-12)

- Inventor draft: `ingest/theory_wave1.md`. Coordinator replay:
  `code/theory_wave1_replay.py` (guarded, 0.5 s),
  `tables/theory_wave1_replay.json`.
- `Q_{n,δ}` under `y ↦ x⁻² y` is freely equal to claimed `Q'` (14/14).
- C16 U124 instance and 1080-tuple parameter sweep: identities hold.
  C16.1 loop holds exactly on `δ=+1` and is absent on `δ=−1` (illegal
  `ρ` would drop `n=2` cyclic total 17→12).
- C17 shears are literal; U124 `S_{n,+1}` fails `3 ∤ 2`; orbit of
  `(c,2)` is `{(c,2),(c+1,3)}`; `S_{n,−1}` is not BS.
- C18 Euclid/radix identities hold; H1 census 1764/0 on `Q`/`Q'`/`S`.
- Extra: five **stored** best-table pairs already satisfy C16 H2+H3 on
  some AC1/AC3 orientation, with Gate 1/2 substitutions verified:
  aca_16, 43, 67, 87, 90. None admit the C16.1 `ρ`-rotation. Initial
  table: only aca_16. Not a solve (length rises; two C0 uses).
- `μ(P)=2n+10`, `μ(Q')=n+12`, `μ(S)=2n+13`; three distinct Aut orbits;
  Aut-canonical form of `S` matches the claimed tag family (10/10).
- Still **0/124** stably trivialized. No certificate JSONL rows.
- Inventor cyclic-complement / overgroup counts were **not** re-run.
- `ingest/advisor_wave3.md`: C16 and C16.1 APPROVE; C17/C18 REVISE applied
  (shear cost is `2 ∑ |e_j|/d_j` AC2, not `≤ 2|c|`; Euclid sufficiency
  only for the replayed `k=qm+1` chains). Still **0/124**.

## Wave 5 (C16-escape timeout recovery, C19, 2026-09-12)

- Theory agent on C16 escapes timed out with an empty transcript. Coordinator
  scan: `code/c16_escape_scan.py`.
- **C19**: on `S_{n,−1}`, one AC2 makes the companion consecutive BS(n,n+1)
  and drops cyclic total by 3 (`2n+13 → 2n+10`), `n=2..7`. C5 still
  fails: `D` has `u x^{-1} u^{-1}` boundaries, but the intervening
  exponent −1 is not a multiple of `n` or `n+1`. Not a best-table update
  (C16 to reach the endpoint is non-effective).
  `ingest/advisor_wave4.md` REVISE applied.
- Swapped-letter C16 does not fire on `S` or the five stored hits. Tag
  family is not depth-1 AC2 with the MS relator. Five stored endpoints
  are not BS donors.
- Still **0/124**.

## Wave 6 (C20 round-trip negative, 2026-09-12)

- `code/c19_continuation.py`: AC3 of `D` by `u^k`/`x^k` never leaves
  pinch exponent `{−1}`; depth-1 AC2 reports valid pinches that C20
  shows are not progress.
- **C20**: one associated-subgroup pinch after displayed `D·B^{±1}`
  returns cyclic `D` or `D⁻¹` (equality modulo `B`, not an AC move).
  For `n=2..7` every valid pinch on the `canon_pair`-unique depth-1
  AC2 neighbourhood rewrites to `D`/`D⁻¹` or empty on the `B` slot.
  Ten remaining children keep `D` and lengthen `B`. C12 does not fire
  (Whitehead minima 7 for `D` and `2n+3` for `B_n`).
  `ingest/advisor_wave5.md` REVISE applied.
- Still **0/124**. No certificate JSONL rows.

## Wave 7 (C21 depth-2 and Gate 2 AC5, 2026-09-12)

- C20’s ten no-pinch children are a uniform family: companion
  lengths `2n+6` (four) and `2n+8` (six).
- Depth-2 AC2 on those children, `n=2..7`: 0 cyclic totals below
  C19’s `2n+10`; Britton leftovers length ≥ 9. All-edge parent
  drops: ten returns to `⟨D,B⟩` per `n`; `n=2` has two extra edges
  into a length-16 class.
- C16 Gate 2 cannot destablize by bare AC5: `u² x^{nδ} y⁻¹` is never
  `y^{±1}`. `ingest/advisor_wave6.md` REVISE applied.
- Still **0/124**. No certificate JSONL rows.

## Wave 8 (C22 Gate 1/2 ncl, C6 ≠ C16, C15 bridge, 2026-09-12)

- Gate 1: `ξ ≡ R^δ` in abelianization, `S`-coefficient 0. No product of
  one or two conjugates of the Q' relators equals `ξ` (`|R|=7`, `|ξ|=3`).
  Depth-1 restore-preserving AC2 after AC4 cannot produce `D`.
- The C16 isolator template satisfies C6/Thm 3.1 on all 12 `Q'_{n,δ}`
  and produces a longer pair than C16 (letter substitution of `y` in the
  companion). C16 is not C6.
- C15 donor times `x⁻¹ y x` is `P_{m,+1}` row 1, but that conjugator is
  not an AC donor; 4160 raw depth-1 children yield 2440 local
  `canon_pair` classes, none of which is `P_{m,±1}`.
- Still **0/124**. No certificate JSONL rows.

## Wave 9 (C23 three-factor Gate 1, 2026-09-12)

- Abelian 3-factor products equal to `ξ` are only shapes A (two `R^δ`,
  one `R^{-δ}`) and B (`R^δ` and opposite `S` pair).
- Complete prefix/one-letter enumeration, `n=2..7` both signs:
  1,529,400 products, min length 7, 0 equal to `ξ`.
- After AC4, F3 depth-2 (1,076,088 products, all 12 `Q'`): never `D`;
  non-generator length ≥ 8.
- Still **0/124**. No certificate JSONL rows.

## Wave 10 (C24 factor-parity, five-factor Gate 1, 2026-09-12)

- Gate 1: `ξ ≡ R^δ`, `L1=1`. Any conjugate product has odd `k`. Even
  `k` is impossible independently of conjugators. Closed count
  `N_1=1`, `N_3=9`, `N_5=100`.
- Five-factor prefix/one-letter MITM `2+3` over a globally
  deduplicated factor-word pool, all 12 `Q'_{n,δ}`:
  `103,765,444,800` tuples, no free equality with `ξ^{±1}`. Raw
  rotations of `ξ^{±1}` freely reduce to `{ξ, ξ^{-1}, x, x^{-1}}`.
- Gate 2 on `Q'`: closed form `L1=2n+2` (`δ=+1`) and
  `|n−2|+|n−4|` (`δ=−1`), always even. Odd `k` is impossible.
  Four-factor is legal only for `δ=−1`, `n=2..5`; `891,860,544`
  tuples, no hit. Stored C16 small-`k` searches on aca_16/43/90:
  no hit (`aca_43` `k=4` is next after C22.4).
- Advisor REVISE applied (`ingest/advisor_wave9.md`). Still **0/124**.
  No certificate JSONL rows.

## Wave 11 (C25 alternative defining words and C15 conjugator, 2026-09-12)

- On `Q'`, `x ≡ ξ` abelianly; 1,529,400 nine-config Cartesian
  three-factor products never equal `x` (min length 7). `X` is the
  inversion-closure of the same tuples, not a same-class free hit.
- `y` on `Q'` has closed `L1=|n+2δ|+1` for `n=2..20`. `k=1` is
  abelian-legal only at `(n,δ)=(2,-1)`, where `|S|=7>1` still blocks
  it; elsewhere `k=1` is abelian-impossible.
- On C15, `y` and `x^{-1}yx` both `≡ B^{-1}`, `L1=1`, `|B|=2m+3`.
  Ten-row three-factor census: 2,884,950 nine-config Cartesian
  tuples, min length 7, no hit on the positive one-letter class of
  `y`. A hit would have been a normal-closure candidate, not a C12
  primitive or a C22.6 AC donor. C22.6 is a row-1 identity; exactly
  five companions equal `P_{m,+1}` row 2.
- Advisor REVISE applied (`ingest/advisor_wave10.md`). Still **0/124**.
  No certificate JSONL rows.

## Wave 12 (C26 exact-L1 y on Q', 2026-09-12)

- Exact-L1 typed products for defining word `y`: `|a|` conjugates of
  `R^{\mathrm{sign}(a)}` and one `S^{-1}`. Prefix/one-letter, per-type
  unique conjugates, typed Cartesian counts (not `|F|^k`).
- Window `n=2..7`, `2≤L1≤7` (eight cells). Two Cartesian cells
  enumerate 38,940 products (observed minima 11 and 13). Six
  existence-MITM cells have typed search-space size 33,815,591,648
  and do not enumerate that many products. All-cell typed total
  33,815,630,588. No hit on `{y, Xyx, xyX}`.
- A hit would have been a normal-closure candidate, not a C12 path.
  `L1=1` remains C25.2; `L1≥8` is open. Advisor REVISE applied
  (`ingest/advisor_wave11.md`). Still **0/124**.
  No certificate JSONL rows.

## Wave 13 (C27 archival AC2 and k=4 extra pair, 2026-09-12)

- Depth-1 ordinary AC2 on `aca_124_initial.csv`: 124 rows, 36 μ-floor
  spellings different from best, 0 unique length drops, 0 new
  one-occurrence, 0 new two-block. Parametric `P`/`Q`/Family A
  (`n=2..7`): 36 pairs, 0 drops.
- `k=4` typed extra-pair products for `y` on `Q'_{3,-1}`: 5,128,200
  Cartesian tuples, observed min length 11, no hit on `{y, Xyx, xyX}`.
  A hit would have been a normal-closure candidate, not a C12 path.
  Advisor APPROVE (`ingest/advisor_wave12.md`). Still **0/124**.
  No certificate JSONL rows.

## Wave 14 (C28 depth-2 archival AC2, 2026-09-12)

- Depth ≤ 2 ordinary AC2 (two successive C13/C27.1 neighbourhoods) on
  `aca_124_initial.csv`: 124 rows, 36 μ-floor spellings, 36,312 unique
  depth-1 children, 19,066,394 unique grandchildren, 0 length drops,
  0 new one-occurrence, 0 new two-block, 0 `canon_pair` matches to the
  stored best spelling. Parametric `P`/`Q`/Family A (`n=2..7`): 36
  pairs, 7,166,262 unique grandchildren, 0 drops. Bounded negative,
  not a solve. Advisor REVISE applied (`ingest/advisor_wave13.md`).
  Still **0/124**. No certificate JSONL rows.

## Wave 15 (C29 YXXyxYx family, 2026-09-12)

- Eleven best-table rows with donor `YXXyxYx`: `y ≡ D^{-1}`, `L1=1`,
  even `k` impossible, `k=1` blocked by `|D|=7`. k=3 nine-config census:
  `1,650,843` typed Cartesian products, equal to typed size, observed
  min length 7, no hit on `{y, Xyx, xyX}`. A hit would have been a
  normal-closure candidate, not a C12 primitive. Five companions are
  C7 Aut-minimal P floors; that Aut-orbit is not a solve. The free
  identity `D · Xyx = YXXyxx` is not an AC2. Defining word `x` is C30. Still **0/124**.
  No certificate JSONL rows. `independent_checker=false`.
  Advisor APPROVE (`ingest/advisor_wave15.md`).

## Wave 16 (C30 exact-L1 x on YXXyxYx, 2026-09-12)

- Defining word `x` on the eleven C29 rows: unique combo has `|b|=1`,
  `L1 ∈ {2,…,7}`. Exact-L1 typed products of `|a|` conjugates of
  `D^{sign(a)}` and one `C^{sign(b)}`. Prefix/one-letter, per-type
  unique conjugates, typed Cartesian counts (not `|F|^k`).
- Three Cartesian cells enumerate 107,212 products (observed minima
  15, 15, and 11). Eight MITM cells have typed search-space size
  43,999,380,138 and do not enumerate that many products. All-row
  typed total 43,999,487,350. No hit on `{x, Yxy, yxY}`.
- A hit would have been a normal-closure candidate, not a C12 path.
  Five companions are C7 Aut-minimal P floors; that is not a solve.
  `|b|=1` is unimodular; `L1 ∈ {2,…,7}` is the eleven listed rows.
  Equality is free-reduce literal against `{x, Yxy, yxY}`.
  Still **0/124**. No certificate JSONL rows.
  `independent_checker=false`. Advisor REVISE applied
  (`ingest/advisor_wave14.md`).

## Wave 17 (C31 YXXYxxyx family, 2026-09-12)

- Eight best-table rows with donor `YXXYxxyx`. Seven companions are
  consecutive `BS(m,m+1)` (`m=3..6`) with `y ≡ C^{-1}`, `L1=1`, even
  `k` impossible, `k=1` blocked by `|C|≥9`. k=3 nine-config census:
  `1,519,059` typed Cartesian products, equal to typed size, observed
  min length 9, no hit on `{y, Xyx, xyX}`. aca_32 is not BS: exact
  L1=2 two-factor Cartesian 1,104 products, min length 9, no hit.
  A hit would have been a normal-closure candidate, not a C12
  primitive. Parallel to C15, different donor. Observed min 9 is not a
  comparative control against C29. Still **0/124**.
  No certificate JSONL rows. `independent_checker=false`.
  Advisor APPROVE (`ingest/advisor_wave16.md`).

## Wave 18 (C32 exact-L1 x on YXXYxxyx, 2026-09-12)

- Defining word `x` on the eight C31 rows: unique combo has `|b|=1`
  from unimodularity with `D_ab=(1,-1)`. L1=2 on seven BS companions
  and L1=3 on aca_32 (those eight rows, not every conceivable
  companion). Exact-L1 typed Cartesian products: 51,412, equal to
  typed size, observed min length 11, no hit on `{x, Yxy, yxY}`.
  Equality was tested after free reduction only against `{x, Yxy, yxY}`.
  No cyclic-reduction or conjugacy quotient, ambient `Aut(F_2)`, or
  Tietze identification was used; freely reduced longer conjugates of
  `x` not among these three targets remain untested. A hit would have
  been a normal-closure candidate, not a C12 path. Still **0/124**.
  No certificate JSONL rows. `independent_checker=false`.
  Advisor REVISE applied (`ingest/advisor_wave17.md`).

## Wave 19 (C33 remaining length-7 D_ab=(0,-1) donors, 2026-09-12)

- Unused compact donors `YXyXYxx` (six rows) and `YYXXyxx` (six rows)
  have the same abelian type as C29: exponent `(0,-1)`, cyclic length
  7, `y ≡ D^{-1}`, `L1=1`. Not a re-run of C29. k=3 nine-config:
  `1,737,522` typed Cartesian products, equal to typed size, observed
  min length 7, no hit on `{y, Xyx, xyX}`. Disjoint donor/row pool from
  C29; same C29/C25 machinery. A hit would have been a
  normal-closure candidate, not a C12 primitive. Still **0/124**.
  No certificate JSONL rows. `independent_checker=false`.
  Advisor APPROVE (`ingest/advisor_wave18.md`).

## Wave 20 (C34 exact-L1 x on C33 rows, 2026-09-12)

- Defining word `x` on C33 donors, window `2≤L1≤7` (eight listed
  rows, not every unimodular companion). C30's combo `(a,b)=(pq,p)`
  applies, so `|b|=1`. Four Cartesian cells enumerate 59,884 typed
  tuples (observed minima 9, 11, 17, 15). Four MITM cells have typed
  search-space 69,587,713,197 (not enumerated products). No hit on
  `{x, Yxy, yxY}`. Equality was tested after free reduction only
  against those three words. Skipped aca_43 (`L1=1`, `x ≡ C^{-1}`) and
  three `L1≥8` rows. Still **0/124**. No certificate JSONL rows.
  `independent_checker=false`. Advisor APPROVE (`ingest/advisor_wave19.md`).

## Wave 21 (C35 YXXXyxx family, 2026-09-12)

- Last unused length-7 donor in the listed shared-donor inventory:
  `D = YXXXyxx`, exponent `(-1,0)`. Pair matrix unimodular ⇒ unique
  x-combo `(-1,0)`, `L1=1`, `R^+ = D^{-1}`. Six rows. The spelling
  already appears in C22.6; that free identity is not an AC2.
- k=3 nine-config: `579,870` typed Cartesian products, equal to typed
  size, observed min length 7, no hit on `{x, Yxy, yxY}`. Hit witness
  schema records signed types, factors, conjugators, and a free-reduce
  replay; unused because there was no hit. Observed min 7 is a C35
  census statistic, not a comparison with C29/C33/C34. Still **0/124**.
  No certificate JSONL rows. `independent_checker=false`. Plan advisor
  REVISE applied (`ingest/advisor_c35_plan.md`). Advisor APPROVE
  (`ingest/advisor_wave20.md`).

## Wave 22 (C36 YXXYxxyX BS family, 2026-09-12)

- Seven best-table rows with donor `YXXYxxyX`. All companions are
  consecutive `BS(m,m+1)` with `C_ab=(0,-1)`, so on those listed rows
  `y ≡ C^{-1}`, `L1=1`. Not every unimodular companion. No exceptional
  row. C31 orientation `R^+ = C^{-1}`. Disjoint donor/row presentation
  pairs from C31, not a disjoint companion-word pool.
- k=3 nine-config: `1,549,596` typed Cartesian products, equal to typed
  size, observed min length 9, no hit on `{y, Xyx, xyX}`. Hit witnesses
  would be replayed outside the scanner; unused because there was no
  hit. Observed min 9 is a C36 census statistic, not a comparison with
  C31. Still **0/124**. No certificate JSONL rows.
  `independent_checker=false`. Plan advisor REVISE applied
  (`ingest/advisor_c36_plan.md`). Advisor APPROVE (`ingest/advisor_wave21.md`).




