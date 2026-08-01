# Core workflow

Read the applicable routed instruction files before acting; do not assume linked Markdown is loaded automatically. Preserve user scope, make surgical changes, and read a file before editing it when its state is uncertain.

Implementation, documentation, and mechanical subagents use `gpt-5.6-terra`; Luna may replace Terra only if the surface exposes it. `gpt-5.6-sol` is a read-only advisor and never implements changes. Use Sol xhigh for every substantive proof or plan review. Reserve Sol ultra for final theorem claims, long-experiment authorization, or unresolved soundness after xhigh review. Subagents must not run proof, search, or test computation.

Before relying on an MCP or external integration, make a minimal health check. Keep temporary artifacts project-relative, never under `/tmp`. After any configuration edit, read the changed section back immediately. Verify work proportionately before claiming success; inspect only the intended scope before staging.

For a user correction, append the lesson to the current dated file in `.agents/instructions/lessons/`; never add dated lesson entries to root `AGENTS.md`. Find historical lessons only through the README protocol.
