# TRAP — a corpus of "canonical base + ONE move" can never falsify an induction step

## What happened

`R7_SPELLING_SPACE.md` §3.1 proposed **Conjecture SR**: `γ_N(spike(P)) = 0 ⇒ γ_N(P) = 0`
— i.e. inserting a spike (Lackenby's move (0), run backwards) never *creates*
thickenability. It carried an unusually strong evidence base:

| source | corpus | counterexamples |
|---|---|---|
| R1F tier 1 | 3,511 canonical bases, 81,942 distinct single spikes, exhaustive to total length 9 | 0 |
| R1F tier 2 | 28,786 double spikes | 0 |
| R7 §3.1 | 5,241 further spiked complexes + 12 certified AC-trivial states | 0 |
| A8 / `S6_MOVE_CLASSIFICATION.md` | 997 thickenable spellings, exact census | 0 |

≈120,000 confirming instances, several of them **exhaustive** over a whole length class,
by three different tools. Downstream, SR was used to prove `γ*(AK(3)) = 1`, "no spelling of
AK(3) is thickenable", "the entire spelling-space route is closed", and a retroactive
upgrade of ≈17,100 verdicts.

SR is **false**. It took under a second to break once the search was pointed at the right
place. Worked example, three spellings of one free-group element pair, each step a single
move (0), Todd–Coxeter **index 1 at every step** (the trivial group — the class that
matters):

```
("ABbbabAAaB","baB")   census 86,400   min defect 0     <- spike, u = "B"
("AbabAAaB","baB")     census  2,880   min defect 2
("AbabAB","baB")       census    144   min defect 0     (fully reduced)
```

`γ_N(spike(P)) = 0` while `γ_N(P) = 1`. The defect along one reduction chain runs
**0 → 2 → 0**: it is not monotone in the spelling in either direction.

## Why 120,000 measurements could not see it

SR is an **induction step**, `depth k → depth k−1`. Every corpus above was generated the
same way: *take a cyclically reduced (canonical) base, apply **one** spike, measure.* That
samples `k = 1` and nothing else. The counterexample needs `k = 2` — a base that is itself
already spiked — and no amount of growth in a `k = 1` corpus can produce one.

The corpus size was measuring the wrong dimension. 81,942 spikes over 3,511 bases is a
large sample **of depth 1**, and depth 1 is exactly where the conjecture is true.

The damage was not confined to the conjecture. The Corollary that SR was wanted for
iterates SR at *every* depth, so it inherited the gap silently; and the same blind spot sat
in `S6`'s neighbouring row, where AC3 conjugation was measured at **315 destroy / 0 create
in 3,507** and read as a law. Conjugation *is* a single spike up to rotation (`S6` Thm T2),
every base in that corpus was reduced too, and creation turns out to happen exactly when a
same-letter spike is already present — 16 of 16 counterexamples used the **same signed
letter** as the spike already in the base.

## The rules that follow

1. **Identify the induction variable and vary it.** If the conjecture has the shape "one
   move never does X", the corpus must contain states at move-depth 2 and 3, not only
   images of normal forms. Depth is a design parameter, not an accident of the generator.
2. **State which depths were sampled, in the write-up, next to the corpus size.** "0
   counterexamples in N complexes" is not interpretable without it. A reader must be able to
   ask *could this generator have produced the shape a counterexample would have?* and get
   an answer from the page.
3. **Normal-forming the generator is the smell.** Whenever a corpus is built from canonical
   / reduced / minimal representatives, ask what the conjecture says about the non-canonical
   ones — that is usually the whole content of the conjecture and usually the untested half.
4. **Exhaustive is not the same as complete.** R1F tier 1 was genuinely exhaustive *over
   total length ≤ 9 at depth 1*. Exhaustiveness inside a stratum reads as much stronger
   evidence than it is when the stratum is the one the conjecture is true in.
5. **Check the scope of a refutation before spending it.** The first counterexample found
   here had Todd–Coxeter index 4 — it presents ℤ/4, not the trivial group, and the AC
   programme only ever uses the trivial-group restriction. A counterexample outside the
   class does not transfer into it; the trivial-group version had to be hunted separately
   (`trivial_bases` + `sr_hunt_spelled`). Same discipline as `CLAUDE.md`'s "distinguish the
   statements", applied to conjectures rather than to AC-trivial / stably AC-trivial.
6. **And do not over-read the refutation either.** In all 28 counterexamples the *fully
   reduced* form already had defect 0 — no spelling beat its own reduction, which is the
   case AK(3) actually needs. Killing a conjecture removes a proof of impossibility; it does
   not supply a proof of possibility.

Code: `experiments/stable_ac/fable/spelling_high_rank.py` (`sr_hunt_spelled`,
`trivial_bases`). Data: `results/stable_ac/fable/s11_sr_trivial.json`,
`s11_sr_spelled.json`. Write-up: `results/stable_ac/theory/fable/S11_SPELLING_AT_HIGH_RANK.md`
§4.3–4.4. Pinned: `tests/fable/test_spelling_high_rank.py`.
