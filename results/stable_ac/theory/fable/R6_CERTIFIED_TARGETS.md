# R6 — Searching toward thousands of certified targets instead of one

STATUS: INSTRUMENT + first results. Claims addressed: the STABLE claim, positive
direction. No AC-triviality claim is made here in either direction.

## The idea

Every AC search ever run — here and, as far as we can tell, in the literature — aims at
one target: the standard presentation. The fake-surface reformulation supplies
thousands more for free.

Fagan–Qiu–Wang, arXiv:2412.12293, abstract (VERBATIM, from a mirrored primary copy;
arXiv itself is proxy-blocked this session): *"The stable Andrews-Curtis conjecture is
equivalent to the conjecture that every contractible fake surface is 3-deformable to a
point. We prove that every contractible fake surface of complexity less than 6 is
3-deformable to a point by induction."*

Their census (github.com/lucasfagan/Fake-Surfaces) lists 5,389 contractible fake
surfaces of complexity 1–5. Collapsing a spanning tree of each singular graph gives a
balanced presentation with V+1 generators, V+1 relators and total length 3V+3 — and by
the theorem, **every one of those presentations is stably AC-trivial**. Hence

    AK(3) is stably AC-trivial   <==   AK(3) is stable-AC-equivalent to ANY of them.

Nothing in the target set is weaker than the standard presentation (all lie in the
trivial stable class). The gain is search geometry: thousands of short entry points,
each with 2–6 generators, i.e. natively inside the AC4/AC5 region that no published
search has explored — and a meet-in-the-middle that halves the depth a forward search
must cover.

## Validation before use

The census→presentation dictionary was derived from the definitions and checked, not
assumed: every singular edge carries exactly 3 face-germs and every row has the
V+1 / V+1 / 3V+3 profile (5,389/5,389); the abelianised relation matrix has |det| = 1
(5,389/5,389); and an INDEPENDENT Todd–Coxeter run certifies the trivial group, index 1,
on 457/457 tested (all of complexity 1–3 plus random samples at 4 and 5).

Flags, which every positive result routed through this set inherits — see
`LITERATURE_STATUS.md` for the full sourcing ledger. The body of arXiv:2412.12293 is
unreachable (proxy-blocked; no source mirror exists; only the abstract was recovered
verbatim, from mirrored arXiv RSS, in both v1 and v2 — identical text). So the exact form
of the equivalence is [UNVERIFIED], and there is a **live discrepancy on cellularity**:
the abstract's theorem is unqualified ("every contractible fake surface of complexity
less than 6"), while the census it rests on is, in the authors' own README, "the
classification of acyclic **cellular** fake surfaces of complexity 1-4 and a **partial**
classification of complexity 5: surfaces without small disks". Concretely, **the 514
complexity-5 targets come from a partial classification**, and whether the body's theorem
carries a cellularity hypothesis is unknown. Do not propagate the unqualified form.

**A second, sharper downgrade of the word "certified" (R8, from the primary README).**
The census is of **ACYCLIC** surfaces; FQW's theorem is about **CONTRACTIBLE** ones, and
acyclic ⇒ contractible is established only up to complexity 4. Combined with the partial
complexity-5 classification, the honest scope of "certified" is the **457 rows this
project verified by independent Todd–Coxeter**, not all 5,389. The remaining 4,932 are
CANDIDATES. `certified_trivial_targets.json`'s description as a "census of complexity
1–5" overstates coverage on both counts and should be read against this paragraph.

**And the targets were partly self-defeating.** R8's Theorem A2 shows a rank-2 census
match would itself be a proof that AK(3) is AC-trivial — so at rank 2 the detector was
searching for something logically equivalent to the answer, not a stepping stone to it.

Matching "up to generator relabelling" additionally leans on the stable ambient
automorphism theorem; exact matches are reported separately so the weaker,
dependency-free reading is always available.

The dictionary itself is in better shape than the theorem: it is a DERIVATION, re-checked
this session against all 5,389 upstream rows with zero failures (disks = V+1; total
attaching length = 6V; every edge label occurs exactly 3 times), from which
generators = 2V−(V−1) = V+1, relators = V+1, total length = 6V−3(V−1) = 3V+3 follows as
arithmetic. What is unverified is whether the paper states it this way, not whether it
holds of the data.

## Results so far

**Direct intersection** (targets vs every harvested member, no expansion):
AK(2) classical class 4 matches; AK(3) classical class (124,296 members) 0;
stable classes 0. Expected — the targets are short (length 3V+3) and the harvests live
at length 13–25.

**Meet-in-the-middle, depth 1** (backward closure of the 257 rank-≤4 targets under AC2
grafts with all rotations and both signs, cyclically reduced, length cap 26 → 31,982
states; intersected against every corpus):

| corpus | members | matches |
|---|---|---|
| AK(2) classical class (positive control) | 13,040 | **46** |
| AK(2)+z stable class (positive control) | 27,350 | **72** |
| AK(3) classical class | 124,296 | **0** |
| AK(3)+z stable class | 26,166 (partial, harvest running) | **0** |

Both controls fire, on the classical AND the stable side: the detector demonstrably
connects a trivializable class to the certified targets. AK(3)'s explored region does
not connect at this depth.

**Meet-in-the-middle, depth 2** (same procedure, backward closure truncated at the
400,000-state cap — so this row is a lower bound on what depth 2 can detect):

| corpus | members | depth-1 matches | depth-2 matches |
|---|---|---|---|
| AK(2) classical class (positive control) | 13,040 | 46 | **276** |
| AK(2)+z stable class (positive control) | 27,350 | 72 | **1,543** |
| AK(3) classical class | 124,296 | 0 | **0** |
| AK(3)+z stable class | 54,422 (partial) | 0 | **0** |

One extra move of backward expansion multiplies the detector's sensitivity by 6× on the
classical control and 21× on the stable control, and leaves AK(3) at exactly zero on
both sides.

## The rank constraint — why most of the target set is currently unreachable

AC1, AC2 and AC3 preserve the number of generators; only AC4/AC5 change it. So a
backward-expanded target of rank r can only ever coincide with a forward state of rank
r. That makes the targets' rank distribution decisive:

| complexity | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| generators (= rank) | 2 | 3 | 4 | 5 | 6 |
| targets | 2 | 17 | 238 | 4,618 | 514 |

and a check of all 5,389 targets finds that **none of them is destabilisable** — no
target has a relator equal to a lone generator absent from the others, so AC5 cannot
lower any target's rank (0 of 5,389 admit even one destabilisation). Their ranks are
intrinsic.

Consequence: our corpora are rank 2 (AK(3) classical) and rank 3 (AK(3)+z), so only
**19 of the 5,389 targets** — the two rank-2 and the seventeen rank-3 ones — were ever
eligible to match. The 5,370 targets of rank 4-6 are not far from AK(3); they are simply
at ranks where we have never searched. This is the single most actionable finding of the
route: the forward side must be stabilised to rank 4, 5 and 6, where 99.6% of the
certified targets live and where no published search has gone. AK(3) plus four
stabilisations has 6 generators and total length 17; the 514 complexity-5 targets have 6
generators and total length 18 — the profiles nearly coincide.

## Searching at the right rank (first attempt)

`stabilized_meet.py` acts on that finding: it starts from AK(3) plus k plain
stabilisations and runs the same rotation-expanded operator, testing every state
against the certified targets **of its own rank**. At the session budget of 1,000 pops
per rank:

| rank | root | targets at rank | states reached | matches |
|---|---|---|---|---|
| 4 | AK(3) + 2 stabilisations | 238 | 30,906 | 0 |
| 5 | AK(3) + 3 stabilisations | 4,618 | 58,849 | 0 |
| 6 | AK(3) + 4 stabilisations | 514 | 84,009 | 0 |

These are, as far as we know, the first searches ever run at ranks 4-6 against certified
stably-trivial targets. 1,000 pops is a demonstration, not an attempt — the point is that
the pipeline runs end-to-end and the scaling is now a matter of budget, which is Run E.

**How little the rank-6 window actually opened, stated honestly.** The 514 rank-6 targets
all have total length 3V+3 = 18. The rank-6 harvest's length histogram is
{18: 128, 19: 8,534, 20: 59,349, 21: 15,997} — so of 84,009 states reached, exactly **128
were at the targets' own length**. A non-match against 514 targets from 128 same-length
states is not a measurement of anything; it is the window barely opening. The rank-6 row
belongs in this table as a pipeline demonstration and nothing more, and any future run
should drive the forward search by length-18 states specifically rather than by pops.

## How to read this, and how not to

What it is: a *validated* detector — the strongest form of negative evidence this
project has produced, because the instrument is shown to work on classes where the
answer is known, in both the classical and the stable setting, at the same depth and
budget.

What it is not: any kind of proof. The backward closure is depth-bounded and
length-capped, the forward corpora are one budgeted corridor of an infinite class, and
a single AC path may leave both windows and return. A non-match is silence, not
refutation.

The honest statement is: *no member of AK(3)'s explored class lies within two AC2 grafts
of a certified stably-trivial presentation of rank ≤ 4, while AK(2)'s does at 276 points
(classical) and 1,543 points (stable) under the identical procedure* — and, per the rank
analysis above, only 19 of the 5,389 targets were eligible to be found at all.

## Next — Run E

1. **Stabilise the forward side.** Harvest from AK(3) plus 2, 3 and 4 stabilisations
   (ranks 4, 5, 6). That is where 5,370 of the 5,389 certified targets live, and where no
   published search has gone. This is the concrete, novel experiment this route exists
   to enable.
2. Raise the backward state cap (depth 2 truncated at 400,000) and expand the rank-5/6
   targets, whose length-18 profile nearly coincides with stabilised AK(3)'s length 17.
3. Drive the forward priority by gamma_hat ascending (R1g) rather than by length.
4. Any AK(3)-side match is a CANDIDATE only: it requires an explicitly reconstructed
   AC1–AC5 move list and a full replay before it is a claim.

## Artifacts

`results/stable_ac/fable/certified_trivial_targets.json` (5,389 targets with
provenance and flags), `certified_target_intersection.json`, `target_meet.json`.
Instruments: `experiments/stable_ac/fable/certified_targets.py`, `target_meet.py`.
