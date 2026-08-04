# [TRAP] A control built from inputs that already have the property measures SURVIVAL, not CREATION

**Filed:** 2026-08-04, fable S-line (`claude/stable-ac-conjecture-stabilization-rwo9as`).
**Cost:** retracted the section labelled "the strongest result of the session".
**Trap ID:** T-S19.

## The shape of the mistake

A one-sided search looks for states with property `Φ` (here: `γ_N = 0`, Neuwirth
thickenable). It finds none for the hard target. Is that because the target lacks a
certificate, or because the search cannot find one?

The standard fix is a calibration control: run the same pipeline on a source *known* to be
solvable and check the detection rate. We did that. The control scored 759/50,320 = 1.51 %
and the target scored 0/45,111, so "at the control's rate the target should have had ≈ 681"
became "the target's zero is a fact about the target".

**It was not.** The control source was chosen AC-trivial and length-matched — but it was
also, unnoticed, **already `γ_N = 0` itself**. Every one of its 759 hits was `Φ` at the root
and stayed `Φ`: replaying the chains gave the defect sequence `(0,0,0,0)` × 759, with zero
chains that left 0 and came back. The pipeline had never *created* a certificate. 1.51 % was
the rate at which it *failed to destroy* one.

Widening the control to sources that are AC-trivial, same rank, same total length, but **not**
already `Φ` gave 0 hits in 46,298 — the same score as the target. Across four independent
non-`Φ` roots the pipeline created `Φ` **0 times in 93,638 opportunities**, while remaining
demonstrably non-blind (759 exhibited certificates whenever the root already had one).

The target was never anomalous. The control was.

## Why it survived the obvious checks

- It was **length-matched**, so the two earlier length confounds
  (`contrast-length-confound.md`, the retracted S10) did not fire.
- It was **rank-matched and pipeline-matched** — same code, same kernel, same budgets.
- The write-up even *named* the real variable: *"only the source's rank-2 defect differs."*
  The one axis on which the control was not matched was the property being measured, and
  that sentence sat directly above the conclusion that attributed the gap to the target.

A control matched on every axis except the one that matters is worse than no control,
because it produces a number that licenses a false claim.

## The rule

> **Before comparing a hard instance's null to a control rate, replay the control's own
> chains and check whether the property was CREATED or merely CARRIED.**

Operationally, for any calibration control on a one-sided search:

1. **Ask the creation question explicitly.** Not "did the instrument find `Φ`?" but *"has
   this instrument ever produced `Φ` starting from a state that did not already have it?"*
   That is the only rate a null on a non-`Φ` target can be compared against.
2. **Compute `Φ` on the control source itself** and put it in the table, in its own column,
   next to the hit rate. If the source is already `Φ`, the control is a survival control and
   its rate is not transferable.
3. **Log `Φ` along the chain**, not just at the leaves. The sequence `(0,0,0,0)` is visible
   immediately and settles the question in one pass; leaf-only counting hides it forever.
4. **Use at least three independent sources.** One source cannot show you its own
   between-source variance. Here three non-`Φ` sources at 0 against one `Φ` source at 1.51 %
   made the confound unmissable — and that variance swamped the effect being claimed.
5. If an exactly-matched source **cannot be constructed**, say so and weaken the claim. Here
   AK(3)'s defect 4 never once appeared among 33 random AC-trivial length-13 rank-2
   presentations (distribution `{0: 20, 2: 13}`): the target sits at a value that is rare
   for its length, so no exact control exists and the nearest available is a different
   experiment.

## The consolation, which is the general point

The corrected reading is *more* useful than the retracted one. "The target resists" is a
statement about one instance and it was false. "This pipeline is `Φ`-preserving and
`Φ`-non-creating, 0 in 93,638" is a statement about the **instrument**, it is true, and it
retires the whole route with a mechanism instead of with silence — including for every
future target, not just this one.

A route closed by a mechanism is a result. A route closed by a null is a guess.

## See also

- `parallel-runs-and-bound-direction.md` — the parent trap. This is the bound-direction
  error wearing a control as a disguise: a null from an upper-bound-only instrument was
  read as a lower bound, and the control made that reading look validated.
- `calibrate-one-sided-hunts-on-a-positive-ladder.md` — calibration done right, on
  *detection*. Note the difference: that ladder calibrates whether the instrument can SEE
  `Φ` at a given size. It does **not** calibrate whether the instrument can MAKE `Φ`. A
  one-sided search aimed at a non-`Φ` target needs both, and the second is the one that
  killed this route.
- `contrast-length-confound.md` — the same failure mode with length as the hidden variable.
