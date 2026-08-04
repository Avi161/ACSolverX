# A search that silently starves produces a null that looks exactly like a real one

**Filed 2026-08-04, S-line (`claude/stable-ac-conjecture-stabilization-rwo9as`).**
Companion to `calibrate-one-sided-hunts-on-a-positive-ladder.md`: that lesson says a null is
worth its measured detection rate. This one says **the detection rate itself is worthless
until you have checked the search consumed its budget.**

## What happened

The S12 certificate hunt reported a detection rate of 0.25–0.30 on a positive ladder and
0 hits on 124 target presentations. Both numbers were stable across a 10× change in the node
budget (250 → 2,500 nodes), and 148 hunts at 2,500 nodes finished in **12 seconds**. That
last fact is the only thing that gave it away.

Three independent defects, each of which starves the search while leaving every printed
number looking plausible:

1. **Reseeding from the root.** On an empty frontier the search restarted from the start
   state — whose children are all already in the seen-set — so the frontier emptied again
   immediately and a restart counter tripped a `break`. Actual work done: **14 to 145 pops
   against a 1,500-node budget.**
2. **Pure length descent.** Always popping one of the shortest `beam` states parks the
   search in a local length minimum and it never climbs out.
3. **Absolute length caps.** A cap of "total ≤ 34" gives a length-13 base 21 letters of room
   and a length-21 base only 13, so long bases have their child generation mechanically
   suppressed. (The project's own `stable_matched_contrast` design already makes this point
   as the *relative-headroom rule*; it had not been carried into the new instrument.)

After the three fixes — reseed from a random **visited** state, take a uniformly random
state a quarter of the time, and make the caps **relative to the root** — the detection rate
on the identical ladder went **0.30 → 0.46 → 0.54**, and pops finally reached the budget.

## The rule

> Every search must report `pops`, `decided` and `undecided` next to its verdict, and the
> first thing to check is whether `pops` reached `nodes`. If a 10× budget increase does not
> move the detection rate, the search is not budget-limited — it is broken. Wall-clock that
> is implausibly short for the claimed budget is the loudest single symptom.

Corollary, from the same session: **decide the start state, not only its children.** The
first revision scored only the children of each popped node, so a root that already carried
the certificate was reported as a miss — a silent false negative at every depth, and at
depth 0 the root *is* the input presentation. A unit test asserting that a known-positive
root is returned at `pops == 0` catches this in one line; nothing else does.

## Why this matters more than a normal bug

A starved search does not crash and does not produce a suspicious number. It produces
*exactly the null the experiment was designed to detect*, on both the target and the
control, which makes the control look like it is doing its job. The comparison stays
internally consistent all the way to the write-up.
