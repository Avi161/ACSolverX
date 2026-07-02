# Convention: PLAN lifecycle (authoring & feedback)

> Referenced from the root `CLAUDE.md` ("PLAN conventions" pointer). Kept out of `CLAUDE.md`
> so that index stays lean. Two parts: **authoring** a plan (before writing code) and giving
> **feedback** on someone's plan. Open this file before doing either.

---

## PLAN authoring (writing an implementation plan)

Write an implementation plan to `PLAN.md` (or `<FEATURE>_PLAN.md`) in the experiment/feature
directory before writing code. Keep it verifiable and readable by a fresh agent with none of your
context.

- **Advisor before and after.** Call `advisor()` before implementing (to check the approach) and
  after finishing (to check the result). Save the file first so it persists if the call times out.
- **Base case first.** Before any full sweep, run one small unit (one presentation/line) end-to-end
  and confirm it works. State the base case, its expected result, and the assertion that gates the
  sweep. Don't start the sweep until the base case passes.
- **TODO checklist in the plan file, updated as you go.** Markers:
  - `[ ]` — to-do.
  - `[X]` — done as planned.
  - `[X][-]` — done but deviated; follow it with a one-line reason and both versions, e.g.
    `[X][-] Used per-relator cap. Reason: sum-cap confounded arm coverage. Planned: sum-cap. Actual: per-relator L=24.`
  Mirror the phases 1:1 and check boxes off as they complete.
- **Ground every claim in the repo.** Verify numbers, paths, signatures, and data shapes by opening
  the file; mark anything you can't verify `[unverified]`. No invented names, flags, or APIs.
- **Reuse map.** List the existing files/functions the plan leans on.
- **Deliverable layout.** Name each file the plan creates, one line each.
- **Phase gates.** End each phase with a checkable validation (assertion, count, replay); mark HARD
  (must pass) vs SOFT (log deviations).
- **Scope.** State what's out of scope / deferred. No speculative refactors.
- **Resumability & cost.** For a long sweep, state the crash-safe/resumable design (see the JSONL
  section of `CLAUDE.md`) and a rough runtime/memory estimate.
- **Simple beats clever.** Use the simplest baseline that works; defer cleverness to a later phase.

---

## PLAN feedback (critical review of a plan)

Every code implementation starts from an implementation plan (`*_PLAN.md` or `PLAN.md`). When the
user asks for feedback on a plan, produce a **critical review** — not a summary and not
encouragement. Write it to a sibling file named `<PLAN_STEM>_FEEDBACK.md` (e.g. `PLAN.md` →
`PLAN_FEEDBACK.md`) in the same directory as the plan, unless the user says otherwise.

**Format: every item is (WHAT → WHY → HOW).**

- **WHAT** — the specific problem, in one sentence. Point at the exact phase / function / line /
  claim in the plan. No vague "consider improving X".
- **WHY** — the concrete consequence if left unfixed: a bug, a wasted-compute estimate, a
  confounded metric, an OOM, a wrong conclusion. Show the reasoning or the number. This is the
  part that earns the fix; a WHAT without a WHY is just an opinion.
- **HOW** — the concrete fix or addition, specific enough to act on (the data structure, the cap
  rule, the file split, the one-line guard). If the fix is "no code change, just pre-register this
  expectation," say that.

**Rules for good feedback.**

- **Ground it in the actual code, not the plan's prose.** Before writing, read the files the plan
  reuses (the notebook, `envs/`, the datasets) and verify the plan's factual claims yourself
  (lengths, counts, budgets, API shapes). Cite what you checked. A plan's stated fact being wrong
  is itself a high-value WHAT.
- **Order by severity** — correctness/compute-blocking issues first, cosmetic last. Group true
  one-liners under a final "Minor" heading.
- **Quantify WHY whenever possible** — extrapolate runtime from a measured node/sec, estimate
  memory from state count × key size, name the specific metric a confound distorts. Numbers beat
  adjectives.
- **Hunt for these classes specifically** (they recur here): redundant work the plan's own logic
  already rules out; resumability/keying bugs in the crash-safe JSONL streams; metric confounds
  (unequal caps/budgets across arms); silent runtime/memory blowups; porting traps (e.g. the
  bool-array `np.roll(...,2*i)` stride when moving to int encoding); and gates that conflate a bug
  with a genuine finding.
- **Be terse and strict.** Short items, backticked identifiers, no filler. Don't pad the count — a
  real 5-item review beats a padded 12.
- **Say what's right too, briefly.** Call out the one or two design choices that are sound (so they
  aren't "fixed" later), but keep this to a line, not a section.
- **Don't rewrite the plan.** Feedback proposes; it doesn't edit `PLAN.md` or implement the changes
  unless the user asks.
