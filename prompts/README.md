# `prompts/` — agent prompts for attacking the Andrews–Curtis conjecture

Contract-style prompts that drive an AI coding agent (Claude Code, Cursor, Codex, …) to make real progress on the **Andrews–Curtis (AC) conjecture** inside this repo — either by *trivializing* hard balanced presentations of the trivial group, or by producing a rigorous *obstruction*. They are written in the "prompt-as-contract" style that has worked for AI-assisted attacks on named open problems (restate the problem precisely; spell out what a finished proof must establish; list what does **not** count so near-misses can't sneak through; front-load the known traps; prescribe an adversarial, counterexample-hunting search discipline; and demand independent verification). Every mathematical claim here is anchored to a file you can open, and the prompts instruct the agent to verify against source rather than trust a restatement.

## How to use

Point your agent at **one** problem prompt. It begins by reading the shared operating contract, then the problem-specific content. For a hard target, running it as a small fleet (one agent per prompt, plus adversarial verifiers) matches how this project's real results were found.

**Tooling note (Claude Code vs Cursor / Codex).** The prompts assume a Claude-Code-shaped harness — `.venv/bin/python3`, `pytest tests/...`, and launching `ac-advisor` as an Opus subagent for the plan gate. On an agent without a subagent mechanism (Cursor, Codex, a plain chat harness), fulfil the gate a different way: **read `.claude/agents/ac-advisor.md` and adopt it as a reviewer persona in a separate, dedicated pass** over your plan before implementing (or run it as a second model/session), reconciling every REVISE/BLOCK. The independent-replay verification (`verify_results.py`, `verify_proofs.py`) and the engineering constraints are harness-agnostic and apply unchanged.

| file | what it drives |
|---|---|
| [`00_operating_contract.md`](00_operating_contract.md) | **The spine — read by every problem prompt.** The trivialize-vs-counterexample asymmetry, the search discipline, what counts as a result, the ten red lines (ported from `.claude/agents/ac-advisor.md`), the verification protocol, and the CPU+numba / budget≤1000 / new-files-only engineering constraints. |
| [`01_ak3.md`](01_ak3.md) | **AK(3)** = ⟨x,y \| xyx=yxy, x³=y⁴⟩ — the unique minimal open case. Resolve it: (stably) AC-trivial, or a genuine counterexample. Highest-value single target. |
| [`02_miller_schupp_frontier.md`](02_miller_schupp_frontier.md) | **The 124 distinct unsolved Miller–Schupp classes** — trivialize as many as possible, or lower the count by a verified merge. (0 of 124 trivialized to date.) Folds in the knot/block search heuristic. |
| [`03_stable_ac.md`](03_stable_ac.md) | **Stable AC (AC4/AC5) searched directly** — the project's core mission. Targeted Lemma-11/CoV stabilization, the μ-ladder toward the μ≤12 criterion, and thickenability as a decidable milestone. |

## The non-negotiables (full detail in the operating contract)

- **The two directions are wildly asymmetric.** Trivialization is a verifiable search + certificate — that is where output happens. A *counterexample* requires a rigorous AC-**invariant obstruction** (the real 60-year problem), and this project has proved the usual invariant layers cannot supply one. **A stalled search is evidence of nothing** — Bridson/Lishak exhibit AC-trivializable presentations needing >10^10000 moves, and those bounds survive stabilization. "Unsolved at budget B" is never a counterexample.
- **Nothing is believed until it replays.** Every solved row goes through the independent pure-Python verifier (`experiments/stable_ac/verify_results.py`; merges through `experiments/equivalence_classes/verify/verify_proofs.py`). A solver cannot certify itself.
- **Gate the plan with `ac-advisor`** (`.claude/agents/ac-advisor.md`, Opus subagent, hostile-referee mode) before implementing.
- **Engineering:** CPU + numba only (no JAX/GPU/PPO on this branch); `.venv/bin/python3`; never run a search above `node_budget = 1000` yourself (production budgets are the user's, on Colab); new files only; run the test suites after any pipeline-adjacent change.

## Provenance

These prompts were synthesized from this repository's own research record — `.claude/agents/ac-advisor.md` (the domain-expert briefing), `literature/proofs/` (the project's proved theorems), `experiments/IDEAS.md` + `IMPLEMENTATION_IDEAS.md` (the ranked, `ac-advisor`-vetted idea backlog), `experiments/equivalence_classes/` and `experiments/stable_ac/` (the frontier and its certificates), and `experiments/clustering/` + `experiments/heuristic_search/` (the knot/block signal). Where a number appears here, its source file is named so the agent — and you — can check it.
