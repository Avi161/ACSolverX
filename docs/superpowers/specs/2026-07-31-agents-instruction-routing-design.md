# ACSolverX Agent Instruction Routing Design

## Problem

The repository-root `AGENTS.md` is 206,912 bytes and 1,816 lines. Codex's
documented default `project_doc_max_bytes` limit is 32 KiB for the combined
project-instruction chain, so the current lesson corpus can truncate later
instructions and wastes context on unrelated history.

Official discovery guidance: [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md).

## Design

Keep root `AGENTS.md` below 8 KiB. It contains only critical invariants and a
mandatory routing table. Arbitrary referenced Markdown is not automatically
discovered, so the root explicitly requires agents to read
`.agents/instructions/core.md` and then only the task-specific files.

Use these locations:

- `.agents/instructions/core.md` — universal workflow, model routing, readback,
  verification, and context rules.
- `.agents/instructions/ac-theory.md` — theory-first AC/stable-AC proof rules,
  advisor protocol, and mathematical nonclaim boundaries.
- `.agents/instructions/process-safety.md` — guarded computation, stale-process
  audit, thermal, preflight, and cleanup rules.
- `.agents/instructions/git-checkpoints.md` — commit cadence and mandatory push
  log protocol.
- `.agents/instructions/experiments.md` — scout/scale and certificate workflow.
- `.agents/instructions/lessons/README.md` — lesson search/read protocol.
- `.agents/instructions/lessons/YYYY-MM-DD.md` — every historical lesson,
  partitioned by its heading date and preserved exactly once.

Model ownership is explicit: implementation, documentation, and mechanical
subagents use `gpt-5.6-terra` (or Luna only if the surface later exposes it).
`gpt-5.6-sol` is a dedicated read-only advisor for proof/substantive-plan
verification and never implements changes.

## Verification

- Root `AGENTS.md` is nonempty and below 8,192 bytes.
- Every original `### YYYY-MM-DD ...` lesson heading occurs exactly once across
  the dated lesson files and never in root.
- Concatenated lesson blocks, in original source order, match the original
  lesson corpus byte-for-byte apart from the single top-level heading.
- All routed files exist, are nonempty, and are linked from root.
- A fresh Codex instruction-summary command is attempted; if unavailable, the
  documented discovery rules plus local size/routing audits are recorded.

## Nonchanges

Do not raise `project_doc_max_bytes`, change proof code, change theorem claims,
or modify experiment behavior during this reorganization.
