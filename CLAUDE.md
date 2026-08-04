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
- GitHub bounces files > 100 MB at push (commit big jsonl artifacts gzipped with a .gz
  test fallback); never compare hit rates across harvests with different operators —
  contrast experiments need member-by-member operator-identity verification and
  two-sided ΣE accounting against a trivializable positive control.
  [[TRAP]](experiments/lessons/large-artifact-commits-and-null-model-contrast.md)
- `literature/` is gitignored, so cloud clones have NO papers: a citation carried in from
  an earlier session looks identical to a read one and gets bolder each time it is copied.
  Re-verify in the session that USES it (`ls` the file before writing the sentence), and
  structure write-ups so an unsourceable theorem costs one inference, not the whole route.
  arXiv RSS feeds mirrored on GitHub still yield abstracts verbatim when bodies are blocked.
  [[TRAP]](experiments/lessons/literature-absent-in-cloud-clones.md)
- Contrast experiments: a raw hit-rate gap can be a LENGTH gap in disguise. A trivializable
  control's class shrinks and its short members are disproportionately thickenable, so
  compare only inside the length band the two harvests share — and never quote a p-value,
  because class members come from a move tree and are not independent draws.
  [[TRAP]](experiments/lessons/contrast-length-confound.md)
- A one-sided hunt's silence is worth exactly its MEASURED detection rate: calibrate on a
  ladder of states known to have the property before reading any null. Ours fell from 100%
  at length 16 to 0% at 21, retiring 1,312 of 1,909 swept states as uninformative.
  [[TRAP]](experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md)
- A resumed subagent can relaunch its job beside yours: two writers, one output path,
  corrupt artifact (check `ps` ELAPSED, kill both, rerun one with explicit --out). And
  record which SIDE each tool bounds a quantity from — a heuristic witness bounds γ_N
  from ABOVE and can never feed a distance corollary that needs a lower bound; a
  degrading search and a rising obstruction produce the same histogram shape.
  RECURRED in prose and cost a search plan: a theorem that CONSTRUCTS a rank-9 witness
  bounds from ABOVE, so "the class first meets the profile at rank 9" is backwards and
  retired the one band with a published theorem behind it. Any "first/minimum/at least"
  claim about something established by construction is suspect on sight; re-derive the
  direction before acting on "stop searching region X".
  [[TRAP]](experiments/lessons/parallel-runs-and-bound-direction.md)
- A control built from inputs that ALREADY have the property measures survival, not
  creation. Ours was length-, rank- and pipeline-matched — and already γ_N = 0, so all 759
  "hits" had chain `(0,0,0,0)` and the instrument had never once created a certificate
  (0 in 91,409 from four non-thickenable roots). Retracted "the strongest result of the
  session". Replay the control's own chains, put Φ(source) in its own column, and use ≥ 3
  sources — one source cannot show you its between-source variance.
  [[TRAP]](experiments/lessons/control-measures-survival-not-creation.md)
- The GERM COUNT is the criterion for whether extra generators can do anything; "it only
  re-describes the relators" is NOT, and stating it that way cost this line a wrong lesson.
  A new edge with exactly two 2-cell germs from two DISTINCT 2-cells is a chord: provably
  inert (whole defect histogram identical, census size unchanged). Three or more germs and
  the space genuinely changes — AK(3)'s rank-13 cubic form re-describes AK(3)'s relators and
  has γ_N = 1 < 2. Also: γ_N = `minimum_defect // 2`; comparing the two manufactures a
  factor-2 anomaly and a wrong theory to explain it.
  [[TRAP]](experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md)
- A search that silently starves yields exactly the null it was built to detect, on target
  AND control, so the contrast stays internally consistent to the write-up. Print
  `pops`/`decided` beside every verdict, check `pops` reached `nodes`, and treat "a 10×
  budget change did not move the detection rate" as a bug report. Reseed from a visited
  state not the root; make length caps relative to the root; and decide the START state, not
  only its children. SECOND POSTSCRIPT: if leaving a plateau in the search's cost function
  requires a cost-INCREASING move, a purely cost-ranked beam has probability zero of success
  at any budget — the cubic-form null went 0/48 → 2/28 on a 30 % random beam fill alone.
  [[TRAP]](experiments/lessons/instrument-the-search-before-reading-its-null.md)
- A corpus of "canonical base + ONE move" can never falsify an induction step. Conjecture SR
  carried ≈120,000 confirming instances from three tools, several exhaustive over a whole
  length class — and every one of them sampled depth 1. It is false at depth 2, on balanced
  presentations of the TRIVIAL group (defect 0 → 2 → 0 along one reduction chain, all rows
  Todd–Coxeter index 1). When a conjecture is an induction step `k → k−1`, the corpus must
  vary `k`, and the write-up must state which depths were actually sampled.
  [[TRAP]](experiments/lessons/conjectures-tested-only-at-depth-one.md)
