# ACSolverX Agent Instruction Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task.

**Goal:** Replace the oversized root lesson corpus with a compact, lossless,
task-routed instruction hierarchy.

**Architecture:** Root `AGENTS.md` retains critical rules and explicit read
routes. Universal and task-specific rules live under `.agents/instructions/`;
historical lessons are partitioned by date and loaded only when relevant.

**Tech Stack:** Markdown, shell text audits, Git.

## Global Constraints

- Root `AGENTS.md` must stay below 8,192 bytes.
- Preserve every existing lesson block exactly once.
- Do not change mathematical claims, proof code, or Codex byte-limit config.
- Terra/Luna implement; Sol is advisor-only.

---

### Task 1: Inventory and lossless lesson split

**Files:**
- Modify: `AGENTS.md`
- Create: `.agents/instructions/lessons/README.md`
- Create: `.agents/instructions/lessons/2026-07-14.md`
- Create: `.agents/instructions/lessons/2026-07-24.md`
- Create: `.agents/instructions/lessons/2026-07-25.md`
- Create: `.agents/instructions/lessons/2026-07-26.md`
- Create: `.agents/instructions/lessons/2026-07-27.md`
- Create: `.agents/instructions/lessons/2026-07-28.md`
- Create: `.agents/instructions/lessons/2026-07-29.md`
- Create: `.agents/instructions/lessons/2026-07-30.md`
- Create: `.agents/instructions/lessons/2026-07-31.md`

- [ ] Snapshot the original file and inventory all dated headings.
- [ ] Partition complete heading blocks by their literal date without rewriting.
- [ ] Verify exact heading count, uniqueness, and lossless block content.

### Task 2: Create routed instruction files

**Files:**
- Create: `.agents/instructions/core.md`
- Create: `.agents/instructions/ac-theory.md`
- Create: `.agents/instructions/process-safety.md`
- Create: `.agents/instructions/git-checkpoints.md`
- Create: `.agents/instructions/experiments.md`
- Modify: `AGENTS.md`

- [ ] Put universal rules and the Terra/Sol ownership boundary in `core.md`.
- [ ] Put theory, process, Git, and experiment rules in their named files.
- [ ] Replace root with critical invariants and explicit task-routing commands.

### Task 3: Verify discovery and checkpoint

- [ ] Read back every changed instruction file.
- [ ] Prove root is below 8,192 bytes and every linked path exists.
- [ ] Prove every original lesson heading/block is preserved exactly once.
- [ ] Run `git diff --check` and inspect only instruction/document changes.
- [ ] Commit, add the mandatory UTC push log entry, bind its SHA, and push.
