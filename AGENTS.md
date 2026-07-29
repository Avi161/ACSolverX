# AGENTS.md — ACSolverX

## Hard rules

### ⛔ MANDATORY before every `git push` (do not skip)

Every push on this branch must be logged. Same-day pushes are frequent (often 100s), so a
date alone is not enough — each push needs its own **UTC time** and **tip commit short SHA**.

1. Append a new section to `logs/DD-MM-YYYY.md` (create the day file if missing).
2. Heading format (required): `## HH:MM:SS UTC · \`<shortsha>\``.
3. Body: 1–3 sentences on what changed, with simple links to files added/changed.
4. Commit that log entry as the tip; fill `<shortsha>` with `git rev-parse --short HEAD`
   (amend once on your own unpushed HEAD if the SHA was unknown before commit).
5. Only then `git push`. Never push without a matching headed log section for that tip.

Same rule in [`CLAUDE.md`](CLAUDE.md). Example day file: [`logs/28-07-2026.md`](logs/28-07-2026.md).

# Lessons Learned

### 2026-07-14 Equivalence tutorial verification environment

- [TRAP] This checkout has no `ACSolverX/.venv/bin/python3`; commands copied from the proof-book documentation fail here.
- [WORKS] Run the independent certificate verifier without modifying the project environment via `uv run --with numba --with numpy python3 <absolute-path>/experiments/equivalence_classes/verify/verify_proofs.py`.
- [WORKS] Pass absolute input and output paths to Tectonic in this workspace; relative `--outdir` resolution was unreliable.

### 2026-07-14 CoV best-z: allow pure powers later

- [DEFERRED] Best-z / length-sweep should eventually allow pure-power `z` (`xx`, `yy`, …). First-z (`NAIVE_Z_FAMILY`) stays mixed-only so pure powers do not preempt the picker.
- Current pipeline: best-z candidates come from the presentation's own relator subwords (`subword_candidates` / `enumerate_cov`); that path still filters `len({abs(g)}) < 2`. Do not implement the pure-power change until asked.
