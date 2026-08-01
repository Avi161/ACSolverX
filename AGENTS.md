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

Configuration edits require immediate readback. Record user corrections only in the current dated lesson file under `.agents/instructions/lessons/`, never here. The AC final goal is a correct proof-resolution result; a bounded failure, null search, failed preflight, or intermediate theorem is not an AC/stable-AC nonclaim or final resolution. Follow the routed process and push rules exactly.
