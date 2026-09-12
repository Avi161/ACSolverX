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

