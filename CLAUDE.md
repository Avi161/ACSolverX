# CLAUDE.md — standing instructions for AC / stable-AC proof sessions

This file is the permanent memory for autonomous proof sessions in this repo.
Re-read it at the start of every session and after every context compaction.

## Mission

Prove or disprove the Andrews–Curtis (AC) conjecture or the stable AC
conjecture. Do not stop until one of these goals is reached.

- Showing AK(3) is trivial or stably AC-trivial is by itself a huge new
  result: commit it and notify the user immediately.
- Work fully autonomously. Never ask the user questions.

## Branch discipline

- The `codex/proof` branch is a separate, independent solver. Do NOT work on
  it or duplicate it.
- All results from these sessions belong on `fable/proof` — this branch.
- Cloud sessions can only push to their own designated `claude/*` branch. If
  you cannot push to `fable/proof` directly, work on your designated branch
  (started FROM `fable/proof` so this file is loaded), commit everything
  there, and state clearly in every report that the branch must be merged
  back into `fable/proof` by the user.
- Every 30 minutes, fetch and read `codex/proof`'s new commits so the two
  efforts stay complementary, never redundant. Take a DIFFERENT theoretical
  direction from whatever `codex/proof` is pursuing.
- Commit and push to the fable branch at least every 15 minutes so no work is
  ever lost.

## Workflow (adapted from https://github.com/ShouqiaoW/erdos)

Model the process on Shouqiao Wang's Codex workflow, which solved 6 open
Erdős problems in 5 days with GPT-5.6 Sol (problems 390, 486, 536, 788, 1002,
1038; ~46% success over ~13 attempts). Fetch that repo via the web (yourself
or with a subagent) to learn the exact workflow, and tweak it freely — AC is
much harder than those Erdős problems. Its three keys:

1. **Problem framing** (inspired by OpenAI's cycle-double-cover prompt):
   restate the problem precisely; specify what a complete proof or disproof
   must establish; list weaker results that do NOT count; identify
   problem-specific traps and edge cases; require independent adversarial
   agents to challenge every candidate proof.
2. **Search management**: start with many independent approaches; keep
   several incompatible routes alive; search aggressively for counterexamples
   to proposed lemmas; mark a route as blocked if it only reduces the problem
   to another open problem.
3. **Patience and persistence**: expect long uninterrupted runs (6–32 hours
   on the Erdős problems; likely longer here). The loop is:
   attempt → failure → diagnosis → new approach → proof draft →
   adversarial audit → repair. Repeatedly abandon broken ideas, attack your
   own arguments, and strengthen the proof until no substantive gaps remain.

## Operating rules

- Act as a mentor/orchestrator. ALWAYS deploy Opus and Fable subagents;
  delegate as much as possible and work solo as little as possible. Your own
  job is theory direction and verification.
- Run computations/experiments when needed (this repo's greedy/PPO solvers
  can serve as experimental tools), but keep your work from colliding with
  the `codex/proof` branch.
- Be creative and rigorous. Independently verify each proof you write with
  separate adversarial subagents before treating it as established. Think out
  of the box if necessary — the way Fermat's Last Theorem was proved through
  an unexpected route.

## Advice that must survive every session

- **Rigor over optimism.** A "proof" that has not survived an independent
  adversarial audit is a draft, not a result. Never report a draft as a
  result.
- **Verify the literature.** Before relying on any "known" theorem about AC,
  AK(n), or stable AC-triviality, have a subagent confirm it against actual
  sources. Misremembered background facts are the fastest way to a broken
  proof.
- **Distinguish the statements.** AC-trivial, stably AC-trivial, and trivial
  group are different claims; a result about one does not transfer to the
  others without proof. State which one every lemma addresses.
- **Negative results are results.** A route shown to be blocked, or a lemma
  with a counterexample, should be written up and committed — it steers
  future sessions away from dead ends.
- **Everything on the branch.** Proof drafts, audits, counterexample
  searches, and route status live in files on the fable branch, committed at
  the 15-minute cadence, so a fresh session can resume from the repo alone.

## Repo quick facts

- Pure Python (numpy/numba for the greedy solver; JAX/flax for PPO training).
- Tests: `pip install pytest numpy==2.1.3 numba==0.63.1` then `pytest`
  (matches `.github/workflows/tests.yml`).
- Full training stack: `pip install -r requirements.txt` plus CPU
  `jax==0.6.0` (cloud containers have no GPU; ignore the CUDA/ROCm files).

## Lessons index (fable line)

- Cloud sessions: scholarly hosts are proxy-blocked (WebFetch dead; GitHub clones work —
  check for paper-source mirrors); a 403 push needs user notification + local commit
  cadence; measure log timestamps with `date -u`, never estimate.
  [[TRAP]](experiments/lessons/cloud-session-network-and-push-constraints.md)
- Harvest searches with conjugation moves: key the seen-set on cyclically-REDUCED
  canonical forms (exact-word keys waste ~97% of pops on conjugacy churn, inflate novelty
  ~45×, and make the search realization-sensitive); validate E-yield code against two
  independent anchors first.
  [[TRAP]](experiments/lessons/harvest-dedup-on-reduced-forms.md)
