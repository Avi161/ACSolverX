# W2b: at least six period-two baselines are live at layer 1

Date: 2026-08-28 · Checker: `checkers/period_two_baseline_liveness.py`
(imports the codex lift certificate unmodified; guarded runs, sliced).

## Method

For each of the 17 essential chains from `W2_PERIOD_TWO_BASELINE_CENSUS.md`:
recover quotient conjugators by complete bounded ball search (up to 4/2/3/3
gauge representatives per slot), lift verbatim to `F(c,t)`, recompute the
literal recurrence with the codex UNREDUCED source rows, form the defect
`D = Z (g t g^-1)^-1 ∈ N`, project to `M = Z[Q/⟨c⟩]`, build the five
lifting operators with the general-target calculus
(`L3 = U^-1 − w`, `L4 = w − 1`, `w = image(g t g^-1)`; the other three as
in the codex certificate), and test one-hop solvability of
`D + Σ L_i x_i = 0` over F2, F3, F5.

**Controls.**
- Fixed-h witness control: with the codex conjugators exactly, the witness
  reproduces the published defect data (21 terms, ℓ¹ 48, augmentation 0)
  and is live — the generalized calculus is validated.
- The sweep also (re)finds the witness live from scratch.
- The run additionally exposed and then absorbed a real subtlety: one-hop
  liveness depends on the gauge representative of the conjugators (the
  witness itself tests NOT-live at one arbitrary representative). Hence
  the sweep over representatives, and the verdict semantics below.

## Results (all 17 chains)

| verdict | count | meaning |
|---|---:|---|
| LIVE_AT_ONE_HOP_MOD_235 | **6** (witness + 5) | some tested lift admits a one-hop correction mod 2, 3, 5 — the same evidential bar the witness's known integral solution passes |
| NOT_LIVE_AT_TESTED_WINDOWS | 11 | no tested representative solvable — **inconclusive, not dead** (window is representative-dependent; support escape possible) |
| DEAD (augmentation) | 0 | every defect has coefficient sum zero |

The five live non-witness chains:

```text
(TTctcTctc, TTTcttcTctt, TTcTcttc)
(TTctcTctc, TTTcttcTctt, TTctcTcTctct)
(TTctcTctc, TTTcttcTctt, TcTTcttcTctc)
(TTctcTctc, TTTcttcTctt, TctcTcTctc)
(TTctcTctc, TcTcttc,     TTcttcTc)
```

Four share the witness's `(R, S)` and differ only in `U`; the fifth has a
shorter `S`. Every live chain's defect and correction data are in the run
records.

## Consequence

Combined with W2: the period-two quotient of the hardest depth-four
signature has **at least six essentially distinct baselines that are live
at the relation-module layer**. The anchored correction family (1.10) of
the codex universal-boundary document reduces to exactly one of them (the
witness). A completed noncancellation theorem over (1.10) therefore closes
one of at least six live lift families; the route to closing the signature
needs the same analysis (or a uniform argument) for the other five — whose
defects and operators this checker now computes mechanically.

## Nonclaims

- "Live at one hop mod 2/3/5" is necessary-condition evidence, not an
  integral solution; "not live at tested windows" is not death. No claim
  about the free-group class, AK(3), stable AC, or AC.
- The census caps (12,12,12,g5) bound the solution set from below only;
  more baselines may exist at larger caps.

---

## Post-hoc correction (same day, cycle 16): six is thirteen

`W2J_THETA_RESIDUAL.md` §1 found that `build_operators_general`'s `L0` column
omits a `q(h1)` factor — the exact variation of `S` conjugates `[δ_R]` by
`S·q(h1)`, not by `S` — so on the 59 of 67 census chains with `q(h1) ≠ 1` the
operator this note used in its `x_0` column is the wrong one. The codex
witness has `H1 = ()`, which is exactly why the fixed-h control passed and why
the generalisation silently did not. `W2K_CORRECTED_REVERIFY.md` re-runs the
sweep on the corrected operator (`checkers/corrected_operators.py`,
`build_operators_exact`), with the shipped arm recomputed as a control and
reproducing this note's numbers exactly.

**What changes.**

| | this note | corrected |
|---|---:|---:|
| `LIVE_AT_ONE_HOP_MOD_235` (17 cap-12 chains) | **6** | **13** |
| `NOT_LIVE_AT_TESTED_WINDOWS` | 11 | **4** |
| `DEAD (augmentation)` | 0 | 0 |

The witness and the five listed non-witness live chains are **all still live**
(5/5); seven of the eleven "not live" chains were live all along, including
three of the five `S = TcTcttc` members. No chain went the other way. So this
note's headline — "at least six essentially distinct baselines live at the
relation-module layer" — is **true but understated by more than a factor of
two**, and its consequence (a completed noncancellation theorem over (1.10)
closes one of *many* live lift families) is strengthened, not weakened.

**What does not change.** The method, the controls, the augmentation result
(0 dead by augmentation, now over 5,427 windows), the doctrine that
`NOT_LIVE_AT_TESTED_WINDOWS` is inconclusive, and every nonclaim. W2g/W2h
later prove `d = 1` for all 67 chains, so *no* window is genuinely dead — the
one-hop support truncation this note flags in its own nonclaim is the whole
story.

**One further caution this note could not have made.** "Live" here means the
one-hop system is solvable, verified by re-applying the same operators that
built it. `W2K` §2 re-tests solutions in `F(c,t)` itself (`n_r = σ(x_r)`,
replay the recurrence, assert the residual is in `[N,N]`): 24 of 46 solutions
built from the shipped operators are **not** layer-1 solutions at all. All 55
built from the corrected operators are.
