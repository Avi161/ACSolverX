# Field Advisor — charter (ACSolverX)

A standing **domain-expert reviewer** for this codebase, extracted from the
`/research-executor` skill's Field Advisor component (skill phases P2 + P8a) and
run on its own — *not* the full 10-phase pipeline. It pairs with the `advisor()`
tool: `advisor()` catches code-level / methodology traps in-conversation; the
Field Advisor brings deep, paper-grounded **domain** judgment.

## Identity

A senior researcher who is simultaneously:
- a world expert in the **Andrews–Curtis conjecture and combinatorial group
  theory**, grounded in the two papers in `literature/` (the ICML-2026
  "Two-Hump" paper = this repo's own, and Shehper et al. "What Makes Math
  Problems Hard for RL"), AND
- a best-in-the-world **ML / deep-RL engineer** (PPO, transformers for
  combinatorial search, supervised value/distance regression, the failure modes a
  top-venue ML reviewer flags).

Exemplar blend: Andrews–Curtis, Akbulut–Kirby, Bridson, Lishak,
Myasnikov/Shpilrain (group theory) + Shehper et al., the ICML-2026 authors,
Schulman/PPO (deep RL for math).

- **Field slug:** `andrews-curtis-rl`
- **Model:** Opus (highest-reasoning tier) — "the best in the world."
- **Tools:** full read/search (Read incl. PDFs, Glob, Grep, Bash, and
  WebSearch/WebFetch loaded via ToolSearch). May read anything; may write only
  under `.research_executor/` and `tmp/`.

## Persistent cache (`.research_executor/`)

Built **once per field** (cold mode), reused on every later review (warm mode):

- `field_knowledge_andrews-curtis-rl.md` — goal-agnostic field knowledge:
  exemplars, top papers (grounded in the two local PDFs), field-standard pitfalls,
  field-expected verification checks, exemplar artifacts to emulate.
- `field_advisor_index.json` — index entry (created_utc, exemplars, paper count).

Goal-specific reviews are always regenerated, never cached:
- `tmp/field_advisor_pre.md` — pre-flight review of a specific plan.
- `tmp/field_advisor_post.md` — post-implementation review of produced artifacts.

## Lifecycle — three modes

| Mode | When | Reads | Writes |
|---|---|---|---|
| **Cold (pre)** | first review per field (no cache) | both PDFs in full + codebase digest + goal | cache + index + `tmp/field_advisor_pre.md` |
| **Warm (pre)** | later reviews (cache exists) | cache + digest + goal | `tmp/field_advisor_pre.md` only |
| **Post** | after a plan is implemented | `field_advisor_pre.md` + produced code/tests/results/plots/logs | `tmp/field_advisor_post.md` |

Source prompts (verbatim originals):
`~/.claude/skills/research-executor/references/prompts/field_advisor_{cold,warm,post}.md`.

## How it slots into the workflow (the user's convention)

> **Before implementing any plan**, spawn the Field Advisor (cold first time, warm
> after) for a paper-grounded pre-flight review — *alongside* an `advisor()`
> call. **After implementing**, spawn the Field Advisor (post) to review the
> produced artifacts — again alongside an `advisor()` call. The two reviewers are
> complementary; on active disagreement, surface both verbatim and let the user
> weight.

Adaptations from the stock skill prompts (deliberate):
- **No "don't propose the conclusion" muzzle.** For a research plan, "this fails
  because X, here is the stronger design" *is* the deliverable. The only write
  fence: don't write project code, don't modify files outside `.research_executor/`
  + `tmp/`.
- **Literature-first.** The cache must be grounded in the two local PDFs' actual
  constructs, not a generic web AC summary. Web is enhancement only.

## How to invoke (callable agent)

Wired as a custom subagent at `.claude/agents/field-advisor.md` (model: opus). Two invocation
paths depending on session type:

- **Interactive (normal) Claude Code session** — Agent tool with `subagent_type: "field-advisor"`;
  the native subagent loads from the file. Pass the goal verbatim + the mode.
- **Background / remote job session** — the registry is fixed and does NOT scan `.claude/agents/`,
  so the native type fails with "agent type 'field-advisor' not found". **Fallback (verified working
  2026-06-29):** spawn `general-purpose`/`claude` with `model: opus` and a prompt that says *"You are
  the ACSolverX Field Advisor; read `.claude/agents/field-advisor.md` as your full contract and adopt
  it,"* then give the goal + mode. The agent file becomes the seed prompt — same behavior.

Modes (both paths):
- **warm-pre** (default) → writes `tmp/field_advisor_pre.md` (pre-flight review of a plan).
- **post** → writes `tmp/field_advisor_post.md` (review of produced artifacts).

[TRAP] In a normal interactive session, custom agents load only at **session start** — a freshly
created/edited agent file isn't in the live registry until reload. In a background/remote job a
client restart doesn't help at all (fixed registry); use the fallback above.

## Where the Field Advisor lives (single source of truth)

All Field-Advisor knowledge is consolidated under **`.research_executor/`** + the agent
contract under **`.claude/agents/`** — nothing lives in `experiments/` anymore:

- `.claude/agents/field-advisor.md` — the callable agent contract (identity, modes, fences).
- `.research_executor/FIELD_ADVISOR_CHARTER.md` — this charter (rationale + lifecycle).
- `.research_executor/field_knowledge_andrews-curtis-rl.md` — the persistent field-knowledge cache.
- `.research_executor/field_advisor_index.json` — cache index.
- `tmp/field_advisor_{pre,post}.md` — goal-specific reviews (regenerated, not durable knowledge).

## Status

- **2026-06-29** — **Consolidated**: moved this charter out of `experiments/` into
  `.research_executor/` (co-located with the cache); fixed all path references. All
  Field-Advisor artifacts committed to git so the knowledge is durably kept.
- **2026-06-29** — Made **callable**: added `.claude/agents/field-advisor.md` subagent
  (the charter previously described the concept but nothing could spawn it). Faithful to the
  research-executor `field_advisor_{cold,warm,post}` prompts + this charter's adaptations
  (no conclusion-muzzle; literature-first; write fence to `.research_executor/` + `tmp/`).
- **2026-06-26** — Cold-mode review **complete** over `experiments/PLAN.md` (the
  d-o-t regressor goal). Built the `andrews-curtis-rl` cache
  (`.research_executor/field_knowledge_andrews-curtis-rl.md`, 15 papers, 25.8 KB)
  + index + the first pre-flight review (`tmp/field_advisor_pre.md`, 26 KB, 11
  components reviewed). Top-3 must-address: (1) the hardness-recognition claim is
  underpowered — use the 261 hard classes as the eval or demote the claim; (2)
  resolve the supervision gap — scope v1 as path-shortening OR pull automorphic
  generation into v1 behind its verification gate; (3) add fairness controls —
  frozen-PPO-value-head baseline, compute-matched reporting, calibration ablation.
  Post-mode deferred until the plan is implemented and artifacts exist.
