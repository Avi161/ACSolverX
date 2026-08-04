# [TRAP] The control solves the task through an exit the target provably cannot use

**Filed:** 2026-08-04, fable S-line (`claude/stable-ac-conjecture-stabilization-rwo9as`).
**Cost:** retracted a headline twice in one session — `S13` §3z-bis (T-S19) and then
`S21_MATCHED_NEGATIVE.md`, which was written *because of* T-S19 and still fell.
**Trap ID:** T-S20. **Companion:** `control-measures-survival-not-creation.md` (T-S19).

## The shape

A one-sided search looks for a state with property `Φ`. The hard target scores 0. To find
out whether that means anything, you build a control that is matched on every axis you can
think of, run the identical instrument, and compare rates.

We did this four times. Each control was matched on strictly more than the last, and each
failed on a variable that only became visible after the result was in hand:

| # | matched on | broke on |
|---|---|---|
| 1 | AC-triviality, rank, total length | it was **already `Φ`** — measured survival, not creation |
| 2 | + verified **not** `Φ` | it needed a **one-unit** descent; the target needs two |
| 3 | + the same **two-unit** descent | it can leave the length band; **the target cannot** |

The third failure is the one this file is about, and it is not a design error you can fix by
choosing a better control.

## What actually happened

Every control hit was a walk *downward in length*: from a start of 13, the witnesses came in
at 3, 3, 4, 4, 5, 7, 7, 8, 9, 9, 9, 10, 11, 11, 11, … The controls were not solving the hard
version of the task. They were shrinking until the task became easy.

The target cannot do that — **and the reason is the open problem itself.** Every balanced
2-generator presentation below the target's length has been exhaustively resolved
(Havas–Ramsay), so if the target's class contained such a member, the problem would already
be solved. The exit that produced essentially every control hit is closed to the target *by
the very fact that the target is open*.

Restricting to length-matched targets and requiring only the weak condition that the witness
end back in band took the rate from **19/24 = 0.79** to **8/24 = 0.33**. The strong version
is far worse: total length is inflatable by inert AC4 discs, so a long witness can be a short
core wearing a costume. Applying the core test to a sibling experiment's 39 witnesses, **39
of 39** reduced to a rank-2 core of length 8 or 11, and only **2** survived an AC-legal-only
reduction. A freshly built defect-matched control scored 8/40 — all genuinely created — with
**0 of 8 staying in band.**

So the honest in-band control rate is somewhere between 0 and 0.05, and the target's 0/34 is
exactly what that predicts. The comparison carried no information at all.

## The rule

> **Before comparing rates, ask how the control's hits were actually obtained — then check
> whether the target is permitted to obtain them the same way.** If the control's dominant
> route passes through a region the target cannot enter, the rates are not comparable, and no
> amount of matching on static attributes fixes it.

Operationally:

1. **Look at the witnesses, not the counts.** Print the full chain of every control hit — its
   length, rank and property value at each step — before quoting a rate. A rate is a summary
   of a mechanism; if you have not looked at the mechanism you do not know what you summarised.
2. **Ask what makes the target hard, and check the control is hard in the same way.** Here the
   target is hard *because* short members are excluded; a control with no such exclusion is
   not a control, it is a different experiment.
3. **Beware the axis defined by the problem being open.** Any control you can verify is
   solvable is, by that verification, close to a solution in a way the open target is not
   known to be. This is not removable: it is the price of having a control at all. State it
   as a limit, not a caveat, and do not build a headline on top of it.
4. **Watch for inert inflation.** If the framework has moves that change the matching
   attribute without changing anything real (here AC4 discs inflating length), then "in band"
   must be tested on a canonical core, not on the raw attribute.
5. **When a comparison fails repeatedly, suspect the method, not the control.** Three
   successive control redesigns each failing on a new variable is the signal that
   target-versus-control is the wrong instrument for the question — not that the fourth design
   will work.

## Why the earlier caveat did not save us

`S21` §5.2 already *said* AC-distance to a solution is unmatched and unmatchable. It was
written down, correctly, and then a headline was built anyway on the same page. A caveat that
is stated but not allowed to change the conclusion is decoration. **If a limitation would
void the result when taken seriously, take it seriously before publishing the number — or
report the result at the strength the limitation leaves it.**

## The independent audit made this stronger, not weaker

An adversarial auditor was set on the retracted file specifically to find a *structural*
fourth confound — a shared relator, a shape mismatch, an abelianisation difference. It found
four such differences, then **built controls without any of them** (fresh AC walks from the
trivial presentation: no shared relator, no unit abelianisation row, one matched even on the
target's relator-length shape) and the rate did **not** collapse: 8/8, 8/8, 8/8, pooled 59/64
across eight presentations from two unrelated sources.

So there is no structural fix hiding here. Matching was pushed to every axis the instrument
can see, and comparability still did not follow — because the incomparability is not an
attribute of the control, it is the *route* the control is allowed to take. The auditor also
replayed one hit end to end and produced the cleanest possible statement of the trap:

    length trace: 13,12,15,18,17,11,14,17,10,11,15,17,14,9,8,7
                  certificate created at length 7

Every step verified as a legal move, the certificate real and exactly checked. A perfect hit,
obtained by an exit the target cannot use.

## A separate lesson from the same audit: do not report a number before its artifact exists

The retracted file quoted the target's null as `0/34`, pooling three runs. Two of those runs
were **still executing** — the search writes its JSON only after its final depth — so 18 of
the 34 trials were console readings transcribed into a table whose status column said
*measured*. The artifact-backed figure was `0/16`.

Console output is a progress report, not an artifact. **A number is measured when a file on
disk contains it**; until then it is a preliminary reading and must be labelled one. Related:
the same audit found all five runs shared one `--seed`, so "40 independent restarts" was
really 8 streams reused 5 times — check the seeds before claiming independence.

## The consolation

The corrected reading is again more useful than the retracted one. "The target resists where
matched controls succeed" was false. "Target-versus-control cannot answer this question,
because every verifiable control has an exit the target is denied by the openness of the
problem" is true, and it retires an entire class of experiments rather than one.

What survived from the retracted file is the part that never depended on the comparison: a
direct measurement that stabilization is inert for the invariant at ranks 2–5. **Results that
stand alone survive retractions; results that live inside a comparison do not.**

## See also

- `control-measures-survival-not-creation.md` (T-S19) — the previous costume; read both, they
  are the same mistake at different depths.
- `contrast-length-confound.md` — length as a hidden variable, the first costume.
- `parallel-runs-and-bound-direction.md` — all of these are upper-bound instruments; a null
  from one bounds nothing from below, which is why a confounded control does so much damage.
