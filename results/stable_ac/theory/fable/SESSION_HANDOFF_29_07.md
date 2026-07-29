# Fable line — session handoff (29-07-2026, updated ~15:36 UTC)

Entry point for the next session. Read CLAUDE.md first, then this. Branch:
`claude/ac-stable-ac-conjecture-ijfzgz` — PUSH ACCESS RESTORED at 13:21 UTC, everything
is on origin. Merge into `fable/proof` is the user's call; never `main`; no PRs.

## Where the line stands

Goal (stable ACC) OPEN. AK(3) sub-goal OPEN. Nothing anywhere on this branch is a
counterexample claim or a trivialisation claim.

**Machinery — complete and audited for ranks 2–3, connected and disconnected links.**
`experiments/stable_ac/fable/` decides orientable thickenability (γ_N = 0) for exact
word-realised complexes: the R1c rank-n theorem, the R1c-v2 cut schemes, and R1e's
Theorem D (which removes the connected-link hypothesis), each adversarially audited.
Run bare `pytest` before believing anything — 510 passed / 5 skipped at last full run,
plus tests added after.

**Negative corpus.** ~141,000 certified non-thickenable exact realisations across
AK(3)'s classical class (124,296), the rank-2/3 stable harvests, and the classical
corridor. Zero thickenable, ever. Statistically: the AK(3) contrast run sits at
ΣE = 5.03 with 0 observed (p 0.65% raw, 4.6% calibrated by the AK(2) control's 0.61
factor) — a real tension with the null model, not yet a phenomenon.

**Newest results (post-restart segment).**
* γ_N *landscape* (R1G): the class's bottom is fully measured — four of the six
  length-13 members are γ_N = 1 *gateways*, AK(3) itself is γ_N = 2; one more gateway
  certified at length 14. `gateway_scan.py` pins γ_N = 1 exactly without a census, by
  combining the solver's certified γ_N ≥ 1 with a hill-climbed defect-2 witness
  (~0.1 s at any length; calibrated on a 2-in-86,400 needle). CAUTION recorded in the
  doc: γ̂ is an UPPER bound and must never be fed to a distance corollary needing a
  lower one.
* Exhaustive one-move neighbourhoods of AK(3) and all four gateways: 420/420 reduced
  images NOT_SPHERICAL; the 150 undecided are exactly the loop-bearing unreduced
  images.
* R1F: **free reduction can create thickenability** — ("xyXY","xxy") is thickenable,
  its spelling ("xyXY","yYxxy") is not. Kills the "spike lemma", so the
  cancelling-graft gap in the graft calculus cannot be closed that way. The open
  question (spike monotonicity, i.e. is the reduced spelling always γ_N-minimal?) is
  worth real effort: if TRUE, reduced-form search is WLOG and every recorded negative
  extends to an infinite family of spellings.
* R5 (fake surfaces) BLOCKED tautologically — min-complexity(AK(3)) < 6 ⟺ AK(3) stably
  AC-trivial. This is Wall 5 instantiated in a second formalism, which is real evidence
  that Wall 5 is a feature of the problem rather than of our grading.
* R6 — the payload from that blocked route: **5,389 certified stably-AC-trivial
  targets** from the FQW census, validated in-session (profile + |det| = 1 on all rows,
  Todd–Coxeter index 1 on 457/457 tested). Meet-in-the-middle at depth 1: AK(2)
  classical 46 matches, AK(2)+z stable 72 — both positive controls fire — and AK(3)
  classical/stable 0. The detector is validated; AK(3)'s explored region does not
  connect.

## Next actions, in order of value

1. **USER / Colab: Run D and Run E.** Run D = the matched-operator contrast at 100k+
   pops (amendment 3 in `R1_COLAB_RUNNER_SPEC.md`); zero hits at ΣE ≳ 300 would be
   phenomenon-level. Run E (new) = R6's meet-in-the-middle at scale: expand the
   certified targets to rank ≤ 6 — which brings the 514 complexity-5 targets and their
   length-18 profile into range, exactly the profile AK(3) reaches after four
   stabilisations plus an AC1 — and drive the forward side by γ̂-ascending priority
   (R1g) instead of by length. Any AK(3)-side match is a CANDIDATE needing full replay.
2. **Settle spike monotonicity** (R1f). Cheap to test, high leverage either way; a
   three-tier experiment was running at session end and its result should be read
   first.
3. Calibrate the γ̂ hill-climber at lengths 14–15 against exact censuses — the missing
   control that separates "the class rises" from "my search degrades".
4. Verify from sources when network allows: Lackenby Thm 1.3 (flagged everywhere it is
   used), the FQW cellular-vs-general scope (flagged in R6), MMS02 Prop 1.2 / Q
   provenance.
5. Relay `NOTES_FOR_CODEX_LINE.md` (9 items; item 7 lets them lift their disconnected
   fail-closed gate, item 8 offers Δ̂ and the tight-ceiling witness).

## Session discipline notes

Budget rule (no search above 1,000 nodes) held throughout; the neighbourhood and
backward-closure enumerations are bounded exhaustive expansions, not best-first
searches, and say so in their reports. Two disclosed deviations remain from the earlier
segment. Lessons in `experiments/lessons/` + the CLAUDE.md index — including two new
ones this segment (duplicate writers corrupting an artifact; which side a tool bounds a
quantity from). Codex fetched throughout; their frontier is per-realisation
Fox-calculus/Hessian work and the Aut-frontier manifest — no collisions.
