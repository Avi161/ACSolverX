# ACSolverX agent instructions

Read `.agents/instructions/core.md` before any work. Then read every route that applies below; referenced Markdown is not discovered automatically.

| Task | Also read |
| --- | --- |
| AC/stable-AC proof, theorem, claim, or substantive plan | `.agents/instructions/ac-theory.md`, `.agents/instructions/process-safety.md` |
| Any computational proof, checker, census, search, test, process cleanup, or long run | `.agents/instructions/process-safety.md` |
| Experiment, benchmark, CoV, notebook, certificate, or result | `.agents/instructions/experiments.md` |
| Commit, staging, branch, checkpoint, or push | `.agents/instructions/git-checkpoints.md` |
| A prior lesson, failure mode, or topic | `.agents/instructions/lessons/README.md` |

Implementation, documentation, and mechanical subagents use `gpt-5.6-terra` (or Luna only if it is available). `gpt-5.6-sol` is read-only: use xhigh for every substantive proof or plan review; reserve ultra for final theorem claims, long-experiment authorization, or unresolved soundness. No subagent may run proof, search, or test computation.

Configuration edits require immediate readback. Record user corrections only in the current dated lesson file under `.agents/instructions/lessons/`, never here. The AC final goal is a correct proof-resolution result; a bounded failure, null search, failed preflight, or intermediate theorem is neither evidence against AC/stable AC nor a final resolution. Follow the routed process and push rules exactly.

## Latest user-directed role boundary

### [2026-09-05] First-principles ownership

[TRAP] Delegating the first-principles choice of AK3 strategy to Sol conflicts
with the user's current allocation of roles. Astra owns mathematical ideas,
strategy, and synthesis. Sol and Terra execute explicitly specified checks,
certificate inspection, or implementation; do not ask them to originate the
research direction. This latest user instruction supersedes earlier strategic
delegation defaults. This lesson is recorded here under the user's replacement
AGENTS.md protocol.

### [2026-09-05] Stable ambient hypotheses

[TRAP] The draft preimage-shift lemma generalized a stable ambient
substitution beyond the trivial-group hypothesis of the cited theorem.
Before promoting a word identity to stable AC, explicitly carry the
balanced trivial-presentation hypothesis through every ambient substitution
and generator-removal step. Free-word replay alone does not check this gate.

### [2026-09-05] Multi-hunk proof-note patches

[TRAP] A proof-note patch failed because its final context omitted text on
the same line. After a context-mismatch error, recheck the literal context
and retry only the intended hunks; do not assume earlier hunks were applied.
