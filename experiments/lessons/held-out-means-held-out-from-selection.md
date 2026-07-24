# [2026-07-24] A split is only "held out" from the stage that actually chose the thing [TRAP]

The heuristic program built a deliberately clean split: `splits_aut.json` assigns whole automorphism classes to one side, so no presentation in the test half shares a change-of-variables twin with anything in the train half. That property was verified, and it is real — an independent audit recomputed it and found zero class overlap.

The headline claim built on it was still wrong:

> baseline 1/6 → tuned **6/6** on held-out automorphism classes

Because the recommended weight vector was never selected on `aut_train`. It came from EXP-04 (the joint weight search) and EXP-06 (the budget-1000 promotion), both of which ran on the **earlier stratified** slice in `splits.json`. That slice contains `ms544`, `ms602`, `ms628` and `ms633` — **4 of the 7 rows** in the supposedly held-out set, covering 3 of its 6 classes. For one class the tuning had seen *both* members.

So the split was disjoint from the wrong thing. It was held out from `aut_train`, and the config was not chosen on `aut_train`.

On the three classes no tuning stage ever contained, the honest figure is **1/3 → 3/3** at budget 1,000 (1/3 → 2/3 at 500). Same direction, a third of the evidence.

## Why it was invisible from inside

The program *did* worry about leakage, twice, and both defences aimed slightly off-target:

- The aut-disjoint split was introduced precisely to stop change-of-variables twins leaking across. It does that.
- A caveat was written admitting that the 25-candidate **shortlist** had been proposed using data overlapping the test rows.

Neither noticed that the *weights themselves* — not just the shortlist — were fitted on rows that later appeared in the held-out column. The shortlist caveat reads like the full admission, which is what made it comfortable to stop looking.

## Rule

**Trace every held-out claim back to the stage that produced the artifact being scored, and check disjointness against *that* stage's data — not against the slice the final evaluation happened to use.** Write it as a question with a file answer: *which experiment chose these numbers, what rows did it read, and is the evaluation set disjoint from those rows?* In a multi-stage program (screen → joint search → promote → validate) the answer is usually a different file at every stage, and the last one is the least informative.

Concretely, when more than one split exists in a project, every published number needs the *pair* stated — selected on X, evaluated on Y — because "held out" alone is ambiguous the moment X and Y are not the same partition. Related: [compare on the same denominator](compare-on-the-same-denominator.md), and [re-tune knobs when the winner changes](retune-knobs-when-the-winner-changes.md) — all three are the same underlying failure, an early decision silently outliving the conditions that justified it.

And the meta-rule this one earned: **an adversarial re-derivation of the headline from raw data, by someone told to refute it, is worth more than another experiment.** This program ran 25 experiments and 101,750 searches; the single most valuable check was the one that read the jsonl back and asked whether the lead number meant what it said.
