# TRAP — a deeper plateau is not closer to a hit (and the residual's SHAPE is the real diagnostic)

Discovered 2026-07-29 while finishing the R10 Zeeman collapse instrument
(`experiments/stable_ac/fable/zeeman_collapse.py`). Cost: about an hour of chasing the
wrong picker, and one written-down conclusion ("score biasing hurts") that was exactly
backwards.

## The setting

A restarted randomized search for a collapse of `K x I` down to a point. The natural
progress metric is the one the search already tracks: `best_faces_left`, the size of the
smallest residual any restart got stuck at. Smaller looks better. It is the metric you
print while tuning.

## What happened

Two pickers, on AK(3)'s `K x I` (1,767 faces):

| picker | best residual reached | hit rate on the GUARANTEED positive (dunce hat x I) |
|---|---|---|
| unbiased LIFO | **325 faces** | **0 / 400** |
| level-score-partitioned LIFO | ~550 faces | **13 / 400** |

The unbiased picker looks dramatically better on `best_faces_left` and *never* succeeds.
The picker that looks 70% worse is the only one that works. Tuning on `best_faces_left`
would have discarded the only picker with any power, and the write-up would have said
"biasing hurts" while measuring the opposite of what it claimed.

Why: `best_faces_left` measures how far one greedy run got before dying, but the runs
that die deepest are the ones that took the *dominant attractor* all the way down.
Depth of plateau and probability of escape are different quantities, and here they are
anti-correlated.

## The thing that actually diagnosed the problem

Not the residual's SIZE — the residual's **f-vector**. Every unbiased restart got stuck
with residual `f = [46, 162, 117]`, which is *exactly* the f-vector of `K` itself. That
one printed number identified the attractor immediately: the search was collapsing
`K x I` vertically onto the copy `K x {0}`, and `K` has no free face at all, so that
residual is terminal. No amount of tail-rollback can repair it, because reaching it
requires having *preserved* every 2-face of that copy — the decisive choices are spread
over the whole sequence, not concentrated in its last few dozen steps.

## Rules

1. **Never tune a one-sided search on how far it got. Tune it on hit rate against a
   state where the answer is known to be YES.** Build the positive rung first, even if
   it is a smaller/different object; the guaranteed positive is the only honest
   objective function. (Same family as
   `calibrate-one-sided-hunts-on-a-positive-ladder.md`, one level earlier: that lesson
   is about reading a null, this one is about choosing the search that produces it.)
2. **Log the residual's full shape, not its size.** An f-vector, a homology, a
   canonical form — something with enough structure to be recognised. "Stuck with 325
   faces left" is noise; "stuck with `f = [46,162,117]`, which is `K`" is a diagnosis
   and a proof that a bounded rollback cannot help.
3. **When two metrics disagree, say which one is the objective before looking.** Here
   "success rate" was the objective and "plateau depth" was a convenience readout that
   happened to be printed more often. The one that is printed more often quietly
   becomes the objective unless you name it.

## Bonus: the same run produced a free sanity check worth copying

The negative controls were cheap and decisive. `S^2 x I` and `RP^2 x I` are not
contractible, so they cannot be collapsible; running the identical search on them gave
0 hits in 40,000 restarts. That is what makes a positive on the real target believable:
it shows the hit detector cannot manufacture a certificate. Always include a target
where a hit is *impossible*, not only targets where a hit is expected.
