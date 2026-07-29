# First-principles heuristic campaign (advisor-rescoped)

**Branch:** `cursor/heur-12h-anti-overfit-a42e`  
**Wall:** 2026-07-29 02:01–14:01 UTC (~12 h)  
**Budget:** 1000 nodes · **Cap:** 48 (matched to EXP-26/27)

## Advisor gate

`ac-advisor` **BLOCK**ed the original plan (fit weights on ~1100 automorphic / CoV rows):

1. EXP-27 / EXP-10 already returned **ties** on fresh `ms640` retunes — no reason a 12 h re-fit would differ.
2. `unique_aut_orbits_1hop` is **1566** rows with **1043 unsolved-descended** — forbidden as a fit set; solved side is only 113 seed problems + CoV images (non-independent).
3. Hard/unsolved presentations have **no dynamic range at budget 1000** (EXP-12: 0/3920).

**Approved re-scope (this campaign):**

- **(A) Evaluation-only** on never-read `AC1M` / clean pools: screen with **length-only** (pre-registered denominator), go/no-go on whether any band separates orderings, then score **pre-registered** arms once — no weight fitting.
- Optional **expected-null**: Aut-orbit-disjoint view of EXP-27-style comparison, reported at true class denominator.
- Never select on unsolved ACA reps or subset-60.
- Phrase negatives as “unsolved within budget 1000”.

## Pre-registered arms (frozen before scoring)

| id | priority |
|---|---|
| `length` | `L` |
| `recommended` | shipped RECOMMENDED |
| `mk8` | `L + 8·MK` |
| `k8` | `L + 8·K` |
| `kms5` | equal-proportion `L + 5·(K/μ_K + MK/μ_MK + S/μ_S)` with subset-60 μ’s (reporting only; not re-fit) |
| `s24` | `L + 24·S` |

μ constants pinned from subset-60 diagnostics (not re-estimated on AC1M): μ_K=4.5333, μ_MK=2.6, μ_S=1.09.

## Outputs

- `results/heuristic_search/campaign_12h/` — jsonl screens + arm scores (resume-safe)
- `results/heuristic_search/campaign_12h/RESULTS.md` — living report
- Runner: `experiments/heuristic_search/runners/campaign_12h_anti_overfit.py`
