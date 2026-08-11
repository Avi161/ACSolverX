# AGENTS.md — ACSolverX

## Hard rules

### ⛔ Smoke run before any long run

Anything that would take more than a few minutes — PPO training, a full beam decode, a multi-hour search, any Colab campaign — gets a short rehearsal first, and its report is read before the real run is launched.

1. **At production settings.** Same beam width, same batch, same data. Narrowing anything to make it fast measures a proxy.
2. **Bounded in wall-clock, between units.** Every row it writes is then a real row the full run resumes from — no work thrown away.
3. **It must measure the per-unit cost** the real run is sized from: `seconds_per_update`, seconds/presentation.
4. **It must exercise every side effect**, not just the maths: optimiser step, checkpoint write, Drive mirror, resume-from-disk.
5. **Read the report before launching.** A smoke nobody reads is a smoke that did not happen.

`SMOKE_RUN = True` in a Colab CONFIG is this rule's implementation. Same rule in [`CLAUDE.md`](CLAUDE.md).

### ⛔ Scout small, then scale only the winner (heuristic experiments)

Do **not** default to long wall-clock campaigns or huge node budgets.

1. **Scout** — short runs, small node budgets (agent local cap is still ≤1,000),
   small presentation subsets. Compare candidate arms / weights quickly.
2. **Pick the winner** on a pre-registered denominator (and check the control has
   dynamic range before reading a null).
3. **Scale only that winner** — raise budget or ship a Colab CONFIG/SETUP/RUN
   notebook so the user can run multi-CPU and hand jsonl results back.
4. Never burn hours at one huge `B` "to be sure": a search at budget `B` is the
   first `B` pops of any longer search, so the scout ranking is the prefix of the
   deep run.

Full note: [`experiments/lessons/scout-then-scale-budgets.md`](experiments/lessons/scout-then-scale-budgets.md).
Same rule in [`CLAUDE.md`](CLAUDE.md).

### ⛔ Live Colab hotfix = `.py` only (never edit the open notebook)

While the user has Colab sessions running: fix heartbeat / pops/s / ETA / mirror /
resume bugs only in importable `experiments/**/*.py` on the notebook's `BRANCH`.
Do **not** edit the `.ipynb`. User Restart → Run All pulls via `UPDATE_REPO` + module
purge; Drive jsonl resume continues. Touch the notebook only for a new CONFIG knob,
and say so. Full note: [`experiments/lessons/colab-live-hotfix-py-only.md`](experiments/lessons/colab-live-hotfix-py-only.md).

### ⛔ MANDATORY before every `git push` (do not skip)

Every push on this branch must be logged. Same-day pushes are frequent (often 100s), so a
date alone is not enough — each push needs its own **UTC time** and **tip commit short SHA**.

1. Append a new section to `logs/DD-MM-YYYY.md` (create the day file if missing).
2. Heading format (required): `## HH:MM:SS UTC · \`<shortsha>\``.
3. Body: 1–3 sentences on what changed, with simple links to files added/changed.
4. Commit the log section together with the work (or immediately after). Then set
   `<shortsha>` to that commit's `git rev-parse --short HEAD` in a **follow-up commit**
   (do not chase a self-hash with amend — a commit cannot contain its own SHA).
5. Push. Never push without a headed log section whose short SHA points at the commit
   that carries the log body for this push.

Same rule in [`CLAUDE.md`](CLAUDE.md). Example day file: [`logs/28-07-2026.md`](logs/28-07-2026.md).

# Lessons Learned

### 2026-07-14 Equivalence tutorial verification environment

- [TRAP] This checkout has no `ACSolverX/.venv/bin/python3`; commands copied from the proof-book documentation fail here.
- [WORKS] Run the independent certificate verifier without modifying the project environment via `uv run --with numba --with numpy python3 <absolute-path>/experiments/equivalence_classes/verify/verify_proofs.py`.
- [WORKS] Pass absolute input and output paths to Tectonic in this workspace; relative `--outdir` resolution was unreliable.

### 2026-07-14 CoV best-z: allow pure powers later

- [DEFERRED] Best-z / length-sweep should eventually allow pure-power `z` (`xx`, `yy`, …). First-z (`NAIVE_Z_FAMILY`) stays mixed-only so pure powers do not preempt the picker.
- Current pipeline: best-z candidates come from the presentation's own relator subwords (`subword_candidates` / `enumerate_cov`); that path still filters `len({abs(g)}) < 2`. Do not implement the pure-power change until asked.
