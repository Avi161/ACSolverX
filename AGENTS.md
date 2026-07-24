# Lessons Learned

### 2026-07-14 Equivalence tutorial verification environment

- [TRAP] This checkout has no `ACSolverX/.venv/bin/python3`; commands copied from the proof-book documentation fail here.
- [WORKS] Run the independent certificate verifier without modifying the project environment via `uv run --with numba --with numpy python3 <absolute-path>/experiments/equivalence_classes/verify/verify_proofs.py`.
- [WORKS] Pass absolute input and output paths to Tectonic in this workspace; relative `--outdir` resolution was unreliable.

### 2026-07-14 CoV best-z: allow pure powers later

- [DEFERRED] Best-z / length-sweep should eventually allow pure-power `z` (`xx`, `yy`, …). First-z (`NAIVE_Z_FAMILY`) stays mixed-only so pure powers do not preempt the picker.
- Current pipeline: best-z candidates come from the presentation's own relator subwords (`subword_candidates` / `enumerate_cov`); that path still filters `len({abs(g)}) < 2`. Do not implement the pure-power change until asked.

### 2026-07-24 Research-loop terminal condition

- [TRAP] A rigorous bounded negative or an honest intermediate theorem is not completion when the user requested a proof-resolution loop.
- [WORKS] Treat each bounded result as one proof attempt: understand the remaining gap, formulate and adversarially check the next proof, and iterate. Mark the task done only when a correct proof resolves the requested AK(3) claim; otherwise continue or report a genuine external blocker without closing the research goal.

### 2026-07-24 Mathematical preflight timeboxing

- [TRAP] Two read-only mathematical preflights remained active through repeated waits without returning even after their scope was shortened, stalling the proof loop without producing an artifact.
- [WORKS] Ask for an early concise checkpoint; after two empty waits, interrupt the preflight and synthesize the theorem-program comparison locally rather than blocking further proof work.

### 2026-07-24 New literature proof files are ignored

- [TRAP] `git add literature/proofs/<new-file>` fails because the repository ignores new paths under `literature/`, even though existing proof files in that directory are tracked.
- [WORKS] For an intentional new proof note, inspect the exact path and use `git add -f literature/proofs/<exact-file>`; never force-add the directory broadly.

### 2026-07-24 Simultaneous-stabilizer factor order

- [TRAP] The tentative factorization `(xy)x(yx)^{-1}y^{-1}` was incorrectly identified with the AK(3) braid relator; literal reduction gives `xY`, so the resulting 9-move rank-3 solve was not connected to AK(3).
- [WORKS] Before running any search from a multi-stabilizer template, independently substitute every defining word and freely reduce to the exact named source orientation. Quarantine all downstream paths if that identity fails.

### 2026-07-24 Substitution boundary reduction

- [TRAP] Writing `x^3(XZt)^4` after substituting for `y^{-4}` missed the boundary cancellation between the final prefix `x` and the first `X`; the reduced word is `xxZtXZtXZtXZt`.
- [WORKS] Free-reduce the complete concatenated relator after every generator substitution, including the boundary between the unchanged prefix and the first substituted block. Pin reduced fixture words in tests.

### 2026-07-24 Cyclic seam completeness scope

- [TRAP] A finite product of cyclic rotations does not exhaust products of arbitrarily conjugated relators: modulo global conjugation, the latter contain an unrestricted relative conjugator \(U c V c^{-1}\).
- [WORKS] State seam-completeness only for the finite Definition-2.1 cyclic-rotation move class actually enumerated. If wrap-seam cancellation occurs, rotate both factors across the cancelled boundary to obtain an equivalent target-first product with a displayed cancelling seam; never broaden this to arbitrary relative conjugators.

### 2026-07-24 One-edge small-bound fixtures

- [TRAP] The bounds `max_word_length=1, max_template_length=4` contain no accepted AK(3) braid identity, so a deterministic certificate test at those bounds exercises only the empty census.
- [WORKS] Use word length two/template length four to test nonempty first-stage reconstruction, and template length five to exercise a genuine new one-edge isolator. Pin the latter's verified small-slice minimum at 14.

### 2026-07-24 Rank-three Whitehead pair census

- [WORKS] The 3,016-state primitive-pair decision contains 9,048 pair occurrences but only 6,928 distinct cyclic pairs. Cache `reduce_pair` by the canonical cyclic pair; the complete pure-Python rank-three Whitehead pass then finishes in roughly 90 seconds on CPU.
- [TRAP] No primitive-pair hit exists in this finite corridor: the observed complete pair minima start at total length 6, so do not spend time expanding a hypothetical positive elimination chain before the exact certificate confirms the null.

### 2026-07-24 Primitive-single quotient fixture

- [TRAP] Straightening a primitive relator changes the other relators too. For `<x,z,t | xz,z,t>`, removing the straightened `xz` relator yields canonical pair `X | Yx`, not the literal standard pair, although its Aut-floor is two.
- [WORKS] Replay the ambient automorphism on the full rank-three tuple before quotienting, and assert the exact induced pair or its independently certified Aut-floor; never assume untouched survivor relators.

### 2026-07-24 GitHub transient push rejection

- [TRAP] A completed local commit can still fail to reach `origin/codex/proofs` with GitHub `remote: Internal Server Error`; do not mistake local commit success for the requested remote checkpoint.
- [WORKS] Preserve the commit, verify the exact ahead state, and retry the same branch push without rewriting history or broadening staged scope.

### 2026-07-24 Primitive-product Whitehead preflight

- [TRAP] Canonicalizing all 90 automorphic images for every one-edge product made even a 100-source preflight exceed 90 seconds and required interruption.
- [WORKS] Gate product words first by primitive abelianization and the Whitehead disconnected/cut-vertex condition. Score Whitehead candidates by cyclic length only and canonicalize just the chosen strict descent; the same 100-source slice then finishes in about 25 seconds.

### 2026-07-24 Full one-edge primitive-product census

- [WORKS] The complete 3,016-source pass closes in under twenty minutes with progress every 100 sources: 2,916,576 literal moves, 1,895,680 deduplicated source-target words, 735,368 global product words, 230,412 graph-gated words, 94,090 primitive words, and 237,680 primitive edges.
- [TRAP] The abelian gcd gate rejects nothing in this corridor (`2,916,576 / 2,916,576` literal moves pass), so the Whitehead disconnected/cut-vertex gate and global word cache carry the optimization. The exact minimum remains 13 in AK(3)'s own orbit.

### 2026-07-24 Shared checkout branch switch

- [TRAP] Another process switched the shared checkout from `codex/proofs` to a dirty `research/w5/stable-ac-escape` branch during a long verifier; continuing there would mix unrelated `.gitignore` work and hide the committed certificate from the filesystem.
- [WORKS] Never stash or overwrite the foreign dirty branch. Confirm `codex/proofs` and `origin/codex/proofs` contain the checkpoint, then create a project-local `.claude/worktrees/codex-proofs` worktree and continue commits/pushes from that isolated branch.

### 2026-07-24 Isolated-worktree test runner

- [TRAP] `/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.venv/bin/python3 -m pytest` fails with `No module named pytest`; sharing the main checkout's interpreter does not imply that the pytest runner is installed.
- [TRAP] Sandboxed `uv run --with pytest ...` cannot initialize `/Users/avigyapaudel/.cache/uv` and fails with `Operation not permitted`.
- [WORKS] Keep using the shared interpreter for certificate replay. For focused tests, run `uv run --with pytest python3 -m pytest ...` with the narrowly scoped approved uv cache access; the one-edge primitive and rank-three Whitehead suite then reports `10 passed`.
- [TRAP] Git writes from the isolated worktree update `.git/worktrees/codex-proofs/index.lock` in the protected main checkout and fail sandboxed with `Operation not permitted`.
- [WORKS] Stage, commit, and push from this worktree only with narrowly scoped Git approval; never move the work back onto the foreign dirty main branch.

### 2026-07-24 Four-germ path rotations

- [TRAP] The project venv does not contain `networkx`; use a narrowly scoped `uv run --with networkx` only for exploratory support-graph inventories, and keep the proof implementation dependency-free.
- [TRAP] For a \(P_4\) link with middle-bundle multiplicity \(m\), exact reversal of one linear middle order represents only one relative gap. The two outer components may occupy independently chosen faces of the middle dipole, so a one-scheme solver creates false negatives.
- [WORKS] Enumerate all \(m\) central shifts \(z\mapsto m-1-z+s\pmod m\). The resulting \(P_4\) rank solver agrees with the factorial Neuwirth census on all 476 canonical cyclically reduced pairs of total length at most seven.
- [TRAP] A misspelling of `AK3_P4_SYNCHRONIZED_PLANARITY.md` produced a failed empty patch. Resolve long theorem filenames from `rg --files literature/proofs` before patching them.

### 2026-07-24 Rigid six-germ census runner

- [TRAP] Plain `python3` in the isolated `codex-proofs` worktree fails while importing the rank-three certificate chain with `ModuleNotFoundError: No module named 'numba'`.
- [WORKS] Run rank-three certificate and rigid-support census code under `uv run --with pytest python3 ...`; the exact 64-state rigid census then exhausts 118,976 phase triples and 1,741,883 component seeds in under five seconds.
