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

Flags, which every positive result routed through this set inherits: the full text of
arXiv:2412.12293 is unreachable this session, so whether the complexity < 6 theorem is
stated for all or only *cellular* fake surfaces, and the exact form of the equivalence,
are [UNVERIFIED]. Matching "up to generator relabelling" additionally leans on the
stable ambient automorphism theorem; exact matches are reported separately so the
weaker, dependency-free reading is always available.

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

## How to read this, and how not to

What it is: a *validated* detector — the strongest form of negative evidence this
project has produced, because the instrument is shown to work on classes where the
answer is known, in both the classical and the stable setting, at the same depth and
budget.

What it is not: any kind of proof. The backward closure is depth-bounded and
length-capped, the forward corpora are one budgeted corridor of an infinite class, and
a single AC path may leave both windows and return. A non-match is silence, not
refutation.

The honest statement is: *no member of AK(3)'s explored class lies within one AC2 graft
of a certified stably-trivial presentation of rank ≤ 4, while AK(2)'s does at 46 and 72
points respectively under the identical procedure.*

## Next

Depth 2 backward closure (running); then the natural scaling for the Colab tier —
expand to rank ≤ 6 (which brings the 514 complexity-5 targets and their length-18
profile into range, the profile AK(3) reaches after four stabilisations plus an AC1),
raise the state cap, and drive the forward side with the gamma_hat-ascending priority
of R1g rather than by length. Any AK(3)-side match is a CANDIDATE only: it requires an
explicitly reconstructed AC1–AC5 move list and a full replay before it is a claim.

## Artifacts

`results/stable_ac/fable/certified_trivial_targets.json` (5,389 targets with
provenance and flags), `certified_target_intersection.json`, `target_meet.json`.
Instruments: `experiments/stable_ac/fable/certified_targets.py`, `target_meet.py`.
