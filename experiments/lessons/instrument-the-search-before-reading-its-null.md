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

## Postscript, same session: a killed run that was not killed

`pkill -f "s12_hunt --nodes"` reported success and the shell moved on, but the loop it was
meant to stop was still alive 14 minutes later, three rungs further along, competing for the
same 4 cores as its replacement — and running the *pre-fix* code semantics, so its rungs
were not comparable with the new ones. The two runs wrote to different output paths, which
is the only reason this was a wasted-CPU incident and not a corrupted artifact (contrast
`parallel-runs-and-bound-direction.md`, where two writers shared one path).

> After killing a long run, **verify by PID**: `ps -eo pid,etime,args | grep '[p]attern'`.
> A pattern kill that matches the wrapper but not the child, or that races the shell, leaves
> the child orphaned and running. And check `etime` — a process older than your last edit is
> running code you no longer have.

## Second postscript: a null that was measuring the beam, not the target

The cubic-form search for AK(3) reported **0 hits in 48 roots** and was written up as
"no cubic form of AK(3) is reported", with a matched-ladder calibration of 33 % attached to
price the null. Re-run with one change — **30 % of each beam filled at random** instead of
purely by cost — it found **2 cubic forms in 28 roots**, and the calibration reversed
(AK(3) 2/28 against the matched ladder's 0/35).

The cause is structural, not statistical. The cost function `Σ|δ|` has a **parity plateau at
cost 2**, and leaving that plateau *provably requires a cost-increasing move*. A beam ordered
purely by cost can therefore never leave it, at any budget. More nodes would not have helped;
a hundred times more nodes would not have helped.

> When a search is guided by a cost function, ask whether the goal region is reachable by a
> monotone descent in that cost. If leaving a plateau requires a cost-increasing move, a
> greedy or purely cost-ranked beam has **probability zero** of success and its null carries
> no information at all — however large the budget and however carefully the detection rate
> was calibrated, because the calibration ladder may not sit on the plateau.

The tell is the same as in the main lesson: a null that does not move when the budget moves.
Here it was worse than flat — it was structurally impossible, and only a change to the
*search policy* revealed it.
