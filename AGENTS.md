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
