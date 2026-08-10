# Feature hunt on aut_min — advisor-gated notes

**Branch:** `cursor/heur-12h-anti-overfit-a42e`  
**ac-advisor:** REVISE (2026-07-30). No new arm shipped from this note.  
**Compute:** feature extraction + certificate replay only; **0 search nodes**.

## Methodology

Freeze rows are already `aut_min` (`phi` matches). Diagnosing on aut_min is fine for
*comparing presentations*; search still Booth-canonicalizes mid-climb (not full Aut).

Hard lesson from advisor: a hard-vs-easy **δ census is anti-correlated with ordering
value** here (largest δ features are the worst orderings; `S` has *negative* δ and
wins). Do not select features by hardness AUC. Select by Aut-disjoint transfer.

`xyimb` overfit was **out-of-sample transfer failure**, not “non-Aut-invariance”
(all 17 features including xyimb are invariant under the 8 signed permutations).

## Already in the 17-dim vector (don’t reinvent)

`L Lmin Lmax imbal K MK mK S Bmax B1 Bmin nb xyimb Bmaxrun Bspread ratio density`

Banned for hard transfer: `xyimb` / full `recommended`.  
Dead as primary (EXP-14/19): `Bmaxrun Bspread ratio density`; solo `B1 Bmin`.

## Rejected candidates

| idea | why dead |
|---|---|
| `thin_iso` / `thin_clump` | Spearman **−0.98** with `S` — reparameterization, not new |
| `col_imbal` / `max_exp` | abelianization degenerate on trivial group (`\|det\|=1`); IDEAS.md idea 8 |
| naive one-ply ΔL | ~250× cost per pop; node-matched compare unfair |
| stuffing more into primary | prefer new *family* or kill-first; portfolio +1/432 at best |

## Surviving next experiments (advisor)

1. ~~**`mobility / L²`**~~ — **BLOCKED + null-tested** (`results/heuristic_search/asym_scout/ASYM.md`).
   R²=0.922 vs the 17; `s20_mk2_Amob±8` = 54/120 = control on train. Dead.
2. **O(L) cross-relator cancellation / overlap** (suffix-automaton), *if* built —
   with **wall-clock-matched** arm, not only node-matched. (Needs positional
   info — bin-only features collapse to abel+generator counts.)
3. **`mK` add-on** — already defined, never swept in Aut-disjoint S×K×MK tune.
4. **Kill-first filter:** solution-child percentile rank across ≥2 independent
   certificate sources (baseline paths *and* S paths); never promote from it.

Also null-tested here: abelianization Gram / “sign asymmetry”
(`|⟨ab(r1),ab(r2)⟩|/T` = IDEAS.md idea 8). Train-selected `s20_Arawm3` overfits
(virgin +2 / fft −2 / spent −7). Do not promote.

## Anti-overfit protocol for any follow-up

- Fresh Aut-disjoint slice of `ac1m_hard_orbits.jsonl`, **disjoint** from spent
  120/60 *and* from `solved_1hop_autclean` (that set already evaluated the shipped arms).
- Controls always: `L`, `L+20S`, `L+20S+2MK`.
- Budget ≤ 1,000 locally. Report `(selected_on, evaluated_on)`.
- Do not re-use solved1hop as train/holdout.
