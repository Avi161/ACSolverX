# Lessons Learned

### 2026-07-14 Equivalence tutorial verification environment

- [TRAP] This checkout has no `ACSolverX/.venv/bin/python3`; commands copied from the proof-book documentation fail here.
- [TRAP] The macOS system `python3` in this worktree also has no `pytest` module. Run focused Python tests through `uv run --with pytest python3 -m pytest ...` rather than calling the system interpreter directly.
- [TRAP] Sandboxed `uv` cannot initialize its default cache under `~/.cache/uv` (`Operation not permitted`). Set `UV_CACHE_DIR=.scratch/uv-cache` so dependency and interpreter state remains project-relative.
- [TRAP] Running the whole `tests/stable_ac` suite with only `--with pytest` leaves the unrelated CoV import path without JAX; `test_transformed_flat_repads_to_cap` then fails at import time with `ModuleNotFoundError: No module named 'jax'`. Include `--with numpy --with jax` when verifying that test or the full suite.
- [WORKS] The first JAX verification may require approved network access because the project-relative uv cache is initially empty. After downloading JAX, SciPy, and jaxlib once, the previously blocked CoV test passes in the isolated environment.
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
- [TRAP] The shared interpreter path contains `Obsidian Vault`; an unquoted absolute invocation is split at the space and fails with `zsh: no such file or directory: /Users/avigyapaudel/Documents/Obsidian`.
- [WORKS] Single-quote the complete interpreter path when replaying certificates from the isolated worktree.

### 2026-07-24 One-loop CoV thickenability

- [TRAP] The CoV implementation is `experiments/stable_ac/cov/cov.py`, not `experiments/stable_ac/cov.py`; resolve module paths with `rg --files` before reading.
- [WORKS] The complete AK(3) subword-CoV family has 34 distinct outputs: 24 have loopless `K4`/`K4-e` support and the other 10 have exactly one loop edge over such a core. Deleting the loop leaves a connected core after removal of its attachment vertex, so spherical rotations are completely parameterized by a core scheme, an insertion gap, and a loop-dart orientation.
- [TRAP] `("xx", "yy")` has no A-link loops: its repeated letters give parallel positive-to-negative edges. It cannot test a multi-loop fail-closed guard.
- [WORKS] Use `("xX", "yy")` for two distinct loop classes and `("xXy", "xXy")` for multiplicity two in one loop class; inspect the exact occurrence dictionary instead of inferring link loops from repeated letters.
- [TRAP] Exhaustively scanning all raw word pairs merely to find one support fixture grows as \(4^n\), ran past 40 seconds, and required interruption; dense `python3 -c` one-liners also produced avoidable syntax/name retries.
- [WORKS] Find small topology fixtures with a seeded random sampler, then pin the exact words and independent factorial trace in tests. The paw-loop fixtures `("yx", "yxXX")` and `("XYyyX", "X")` exercise spherical and non-spherical branches at only six and four factorial orders.
- [TRAP] “Every component of \(G-a\) occupies one rotation interval at a cut vertex” is false when there are three or more components: one connected component can surround separate components on opposite sides. The no-alternation argument does not imply one interval in a multi-symbol cyclic order.
- [WORKS] State and use the interval lemma only when \(G-a\) has exactly two components; then a split forces an alternating \(Q_1,Q_2,Q_1,Q_2\) pattern and the Jordan-curve contradiction is valid. This exact hypothesis holds for the paw articulation.
- [TRAP] The first direct 22-case paw batch exposed a 21-minute outlier at total length 39; a small scheme/phase count does not preclude expensive repeated propagation with large rank domains.
- [WORKS] Stop the batch at the first runtime outlier and optimize the exact constraint calculation before resuming; never let a bounded topology census silently consume the checkpoint interval.

### 2026-07-24 Focused CoV test dependencies

- [TRAP] `uv run --with pytest python3 -m pytest tests/stable_ac/test_cov.py` supplies the test runner but not JAX; `test_transformed_flat_repads_to_cap` then fails in `envs/utils.py` with `ModuleNotFoundError: No module named 'jax'` even though the proof-specific tests pass.
- [WORKS] `uv run --with pytest --with jax python3 -m pytest tests/stable_ac/test_cov.py::test_transformed_flat_repads_to_cap` supplies the missing optional runtime and passes. Treat that dependency separately from the exact CoV and thickenability certificate results.

### 2026-07-24 Cancelling-seam zero-incidence factor

- [TRAP] In `AK3_ONE_EDGE_COMPRESSION.md`, the claim that both cyclic factors must contain at least two \(x^{\pm1}\)-letters is false: \(P=z\), \(Q=xxzXZ\) have incidences zero and three, but \(\operatorname{cyc}(PQ)=xz\) has incidence one after a wrap cancellation cascade.
- [WORKS] The seam-normal-form conclusion needs only \(\nu_x(P)+\nu_x(Q)\ne1\), monotonicity of incidence under reduction, and the fact that the first cancellation of two cyclically reduced factors must occur at a factor seam. Pin the zero-incidence counterexample in `tests/stable_ac/test_one_edge.py`.

### 2026-07-24 Injected certificate inputs need theorem validation

- [TRAP] `two_hop_cov_thickenability_certificate.build_certificate` validated stable CoV hypotheses only while generating its default production paths. Explicit paths used by tests could set `n_cov=n_subs=0` and still receive `stable_move_hypotheses_verified=true`.
- [WORKS] Validate injected inputs against the exact upstream first-hop census, regenerate each parent's exact second-hop family, recheck every stable-move hypothesis, and require membership in the regenerated outputs. Bind direct codec dependencies such as `experiments/greedy_tests/spec/words.py` in the source manifest rather than relying only on complete payload replay.

### 2026-07-24 Stable ambient automorphism rank

- [TRAP] `PROOFS.tex` proves the stable ambient automorphism principle only for balanced rank-two presentations. Citing it directly for a primitive pair in \(F_4\) leaves an arity gap even though the generalization is natural.
- [WORKS] Before using an ambient automorphism in higher stable rank, prove the rank-\(n\) form from the substitution-and-removal exchange: fresh-letter renames realize swaps and inversions, and adjoining \(v^{-1}a_i a_j^{-1}\), removing \(a_i\), then renaming \(v\) realizes a Nielsen transvection.

### 2026-07-24 Triangular elimination is not pair primitivity

- [TRAP] Two relators that can be removed successively by unique-occurrence substitution need not form a primitive pair: the first relator may be used to clear the second by relator operations, while primitive-pair straightening permits only one ambient free-group automorphism plus independent conjugation/inversion.
- [WORKS] State triangular Lemma-11 elimination and \(F_n\) primitive-pair compression as complementary criteria unless a separate Whitehead certificate proves primitivity for the exact template pair.

### 2026-07-24 Survivor alphabet before Aut-canonicalization

- [TRAP] Passing an exact rank-two survivor pair over \(\{x,t\}\) directly to `aut_canon` fails with `KeyError: 't'`; the routine is intentionally written for the canonical \(\{x,y\}\) alphabet.
- [WORKS] Perform the theorem's final signed relabel \(t\mapsto y\), \(T\mapsto Y\) before calling the rank-two Whitehead code, and keep the pre-relabel words alongside the result for proof replay.

### 2026-07-24 Check conjugation orientation before promoting a symbolic family

- [TRAP] For \(u=z^{-1}xz\), one has \(u^{-1}=z^{-1}x^{-1}z\), not \(zx^{-1}z^{-1}\). Treating these as equal produced the wrong defining relator and survivor formula in a scratch derivation of the AK(3) twist family.
- [WORKS] Before writing a parametric compression theorem, replay both template expansions and the eliminated defining relator as literal free words. For the valid family use \(t=zxz^{-1}x^m\), whose inverse really compresses the blocks \(zx^{-1}z^{-1}\) in the power relator.

### 2026-07-24 Parametric free reduction versus cyclic conjugacy

- [TRAP] The unreduced survivor spelling \(TxtxTXx^m\) has reduced tail \(x^{m-1}\); writing it as a literal reduced expected word fails at \(m>0\). After the shear \(t\mapsto tx^m\), the second relator is generally a conjugate of the AK(3) relator, not the same linear spelling.
- [WORKS] State parametric formulas with group powers, reduce the complete expansion, and use cyclic reduction before comparing conjugacy classes. Test negative, zero, and positive parameter values because cancellation changes sides at \(m=0\).

### 2026-07-24 Ignored proof directory staging

- [TRAP] A single ordinary `git add` that includes any path under the ignored `literature/` tree exits nonzero and may leave the non-ignored paths partially staged, even when a proof file there is already tracked. Do not assume either an empty or a complete index after this error.
- [WORKS] Stage every exact intended `literature/proofs/...` path with a separate `git add -f`, including modifications to already tracked proof files; stage non-ignored report, test, and lesson files in another command, then inspect the cached diff before committing.

### 2026-07-24 Source-relator Bézout recovery

- [WORKS] After proving that free-basis recovery of \(v=zxz^{-1}\) is pure gauge, the first genuinely broader mechanism is to recover \(v\) modulo the source relation \(x^3=v^4\). For \(t=v^k\), aligned cyclic relator products implement the Euclidean algorithm on exponents \((-4,k)\) without an AC graph search.
- [WORKS] Split odd \(k\) by \(|k|\bmod4\): explicit shears collapse all endpoints to one floor-14 or one floor-15 orbit. For even \(k\), abelianization gives the parity obstruction \(3=4m+3kn\), so direct recovery is impossible before any word-level search.

### 2026-07-24 `cyclic_orientations` does not cyclically reduce

- [TRAP] `two_stabilization.cyclic_orientations(word)` freely reduces its input and enumerates rotations/inverses, but it does not cancel inverse letters across the cyclic boundary. A conjugated word such as \(x^3Wx^{-3}\) therefore does not expose the orientations of \(W\).
- [WORKS] Call `experiments.equivalence_classes.lib.words.cyc_reduce` before `cyclic_orientations` whenever the identity being tested is conjugacy rather than literal cyclic rotation of an already cyclically reduced spelling.

### 2026-07-24 Quotient recovery words are not unique

- [TRAP] From \(v=U(x,t)\) in the quotient by two relators, it does not follow that the canonical Euclidean word \(U\) is the only AC-realizable replacement in \(B=z^{-1}xv\). Multiplying \(U\) by a suitable consequence of the surviving relators preserves its quotient value but can change the post-removal endpoint orbit.
- [WORKS] Label the \(t=v^k\) residue-class theorem as a classification of the prescribed Euclidean normal-form recovery only. Pin the \(k=1\) counterexample \(U=t(t^{-4}x^3)=t^{-3}x^3\), whose endpoint has Aut-floor 23, and treat consequence-twisted recoveries as a separate live mechanism.

### 2026-07-24 Parametric Whitehead proofs from block counts

- [WORKS] For a one-parameter endpoint family, first apply a fixed signed basis permutation that exposes repeated cyclic blocks. Whitehead length changes then become affine functions of the parameter, so a twelve-row symbolic table proves complete Aut-minimality for all parameters without enumerating an Aut graph.
- [WORKS] In `AK3_CONSEQUENCE_TWIST_FAMILY.md`, the positive and negative \(t(t^{-4}x^3)^n\) branches have floors \(28n-5\) and \(28|n|+15\); zero is the separate floor-14 compression root.

### 2026-07-24 Cyclic coordinates in parametric replay tests

- [TRAP] `cyc_reduce()` removes boundary cancellation but does not choose a canonical cyclic rotation. An exact block-form assertion can therefore fail even when the computed word is the claimed cyclic conjugate; this occurred for `xxxyXXXXY` versus `yXXXXYxxx` in `test_conjugated_recovery_family.py`.
- [WORKS] Assert cyclic equivalence between the transformed endpoint and the displayed block form, then run all Whitehead length-change checks on that displayed representative. Cyclic conjugation preserves every cyclic-length calculation.
- [TRAP] Do not let a rotation-only assertion also accept inverse rotations. Relator inversion is AC-legal, but accepting it silently weakens a certificate whose proof claims the displayed words arise by cyclic rotation alone.

### 2026-07-24 Rank-two alphabet boundary

- [TRAP] `experiments.equivalence_classes.lib.autcanon` accepts only the `xXyY` alphabet. A mixed-consequence census that constructed endpoints over `xXtT` raised `KeyError: 't'` inside `apply_hom`.
- [WORKS] After eliminating \(z\), relabel `tT` to `yY` before calling `aut_min_len`, `peak_reduce`, or `aut_canon`.

### 2026-07-24 Mixed consequence corridors

- [WORKS] For \(U_{n,m}=t(t^{-4}x^3)^nK_m\) with \(nm\ne0\), isolate \(S_n=\operatorname{red}(t(t^{-4}x^3)^nt^{-1})\). It has exact length \(7|n|\), and the endpoint blocks in `AK3_MIXED_CONSEQUENCE_FAMILY.md` are already Whitehead-minimal.
- [WORKS] Split the twelve Whitehead deltas only by the three genuinely different sign regions \(n>0\), \(n<0<m\), and \(n,m<0\). The signs of \(m\) do not change the table when \(n>0\), and the complete mixed floor is \(28|n|+12|m|+15\).

### 2026-07-24 Zero commutator parameter

- [TRAP] The literal word \(K_m=t^{-1}x^{3m}tx^{-3m}\) freely reduces to the empty word at \(m=0\). A replay assertion that every constructed commutator word is nonempty incorrectly rejects the coordinate axis.
- [WORKS] Test `bool(K_m) == (m != 0)` and keep the \(m=0\) axis in every two-parameter signed grid.

### 2026-07-24 Reverse-order cancellation stratum

- [TRAP] For the reverse mixture \(tK_m(t^{-4}x^3)^n\), the chamber \(n<0,m<0\) has an additional boundary type at \(m=-1\): the middle \(x\)-block vanishes and two \(t\)-blocks merge. Extrapolating the \(m\le-2\) Whitehead delta formulas to \(m=-1\) gives the wrong constants.
- [WORKS] Isolate \(n<0,m=-1\) as its own symbolic Whitehead row. The complete reverse-order mixed floor still has the uniform chamber value \(28|n|+18|m|-13\), but the twelve local deltas have a five-region, not four-region, description.
- [TRAP] Closing the two collected orders \((R')^nK_m\) and \(K_m(R')^n\) does not imply that every remaining source-relator recovery must interleave their individual factors. Other rotations, conjugated or inverse whole blocks, and different conjugates of \(R\) remain unclassified too.

### 2026-07-24 System Python compatibility for proof tools

- [TRAP] The system `python3` in this worktree is Python 3.9.6, while `uv run --with pytest` currently selects Python 3.14. An unevaluated `str | None` annotation passed the pytest environment but raised `TypeError: unsupported operand type(s) for |` under the system interpreter.
- [WORKS] Add `from __future__ import annotations` to new proof modules that use PEP 604 unions or built-in generic annotations, and smoke-test imports under both system `python3` and the uv test runtime.

### 2026-07-24 Recovery word equations via amalgam normal form

- [WORKS] Replace bounded enumeration of chosen consequence products by the exact equation \(U=t\) in \(\langle x,t\mid x^3=t^4\rangle\). With central \(c=x^3=t^4\), alternating residues \(x,x^2\) and \(t,t^2,t^3\) give a unique amalgam normal form and a complete equality test.
- [SUPERSEDED] Exact abelianization prefix pruning first made the length-\(16\) census feasible, but the DFS still scaled poorly at length \(17\).
- [WORKS] Split each word into two freely reduced halves, index right halves by independent amalgam normal form, and join a left half \(L\) only to state \(\operatorname{NF}(L^{-1}t)\), excluding inverse seam cancellation. This exact meet-in-the-middle census covers all 258,280,324 raw words through length \(17\) in well under a second of enumeration time.
- [WORKS] There are exactly 40,503 recoveries through length \(17\). The unique floor-14 endpoint is \(U=t\); every floor-\(\le23\) word lies in a previously proved parametric family.
- [TRAP] State this as a bounded recovery-word theorem only. Normal-form completeness through a word-length cap does not rule out longer recoveries, changes to the retained source relator, or nontrivial use of the defining relator.
- [TRAP] Distinguish “shortest nonliteral recovery” from “smallest nonliteral endpoint floor”: nonliteral recoveries first occur at length \(6\), while the floor-\(15\) minimizer has length \(7\). Also do not call the word-equation model broader than every possible conjugate grammar; arbitrary products of arbitrary relator conjugates are extensionally complete.

### 2026-07-24 Dependency-free proof-test replay

- [TRAP] `/Library/Developer/CommandLineTools/usr/bin/python3` has no `pytest` module in this worktree, so `python3 -m pytest ...` fails before collecting any test.
- [WORKS] For proof tests whose imports are dependency-free, load the test file with `runpy.run_path` and call every `test_*` function directly under system Python. Use the managed test runtime only when pytest fixtures or third-party dependencies are actually required.

### 2026-07-24 Normal-closure diamonds close direct recovery

- [WORKS] If \(V^{-1}V'\in\langle\!\langle W\rangle\!\rangle\), then \((W,V)\) and \((W,V')\) are classically AC-equivalent: factor the quotient into conjugates of \(W^{\pm1}\), multiply them into the second relator one at a time, and restore \(W\) after each factor.
- [WORKS] For arbitrary \(U=t\) modulo \(R=x^3t^{-4}\), both the restored endpoint \(P(U)\) and the unrestored endpoint \(Q(U)\) return classically to AK(3). The restored-to-unrestored side has the exact four-factor identity \(A_U^{-1}R=\prod_{i=1}^4t^iS_Ut^{-i}\).
- [TRAP] Do not infer that arbitrary CoV transforms are classical self-loops. This diamond requires the exact fixed relator \(R\), final isolator \(z^{-1}xU\), and recovery equation \(U=t\bmod\langle\!\langle R\rangle\!\rangle\).
- [TRAP] Large combined `apply_patch` calls fail atomically when one late context hunk misses changed line wrapping. Add new files and patch an evolving report in separate calls, using a fresh read for the report context.

### 2026-07-24 Arbitrary-conjugator catalyst via axis bridges

- [WORKS] For one multiplication of \(B=z^{-1}xt\) by an arbitrary conjugate of \(D^{\pm1}=(t^{-1}zxz^{-1})^{\pm1}\), normalize the written conjugator to the shortest bridge between the two axes. A nonempty bridge gives a cyclically reduced word with at least three \(z^{\pm1}\)-letters, so every one-\(z\) isolator comes from intersecting axes and a finite signed-rotation residue.
- [WORKS] The 24 signed rotation products have four raw one-\(z\) witnesses and only two cyclic isolators, `ZTxtx` and `ZtxtX`; both substitutions return the surviving pair classically to AK(3).
- [TRAP] The literal-\(B\) one-\(D\) theorem does not cover first replacing \(B\) by an arbitrary recovery \(B_U=z^{-1}xU\) and then applying one \(D\)-factor. Preserve that mixed recovery-plus-catalyst mechanism as open.
- [TRAP] The system-Python scratch census once used a conditional expression inside a `from ... import ...` list and stopped with `SyntaxError: invalid syntax`. Keep scratch imports literal and separate; conditional selection belongs after import.

### 2026-07-24 Mixed recovery-plus-catalyst collapse

- [WORKS] For \(B_U=z^{-1}w\), \(w=xU\), an arbitrary-conjugator one-\(D\) multiplication can create a one-\(z\) target only by canceling \(B_U\)'s unique \(z^{-1}\) with \(D^{\pm1}\)'s unique \(z\). Moving that canceled pair to the displayed seam leaves exactly the templates \(z^{-1}t^{-1}wx\) and \(z^{-1}twx^{-1}\).
- [WORKS] If \(S_0=t^{-1}wxw^{-1}\) is the direct survivor, the two catalyst survivors reduce exactly to \(t^{-1}S_0t\) and \(tS_0t^{-1}\). Therefore arbitrary recovery followed by one \(D\)-factor is only a relator-conjugation self-loop.
- [TRAP] This theorem fixes the order “all \(R\)-recovery factors, then one \(D\)-factor.” It does not close other \(R/D\) interleavings or two \(D\)-factors.
- [TRAP] Cyclic factor-order symmetry does not exchange target/source roles after elimination. If \(D\) is targeted by \(B_U\), the modified \(D\) is removed and \(B_U\) survives; preserve that reverse-role endpoint as a distinct open mechanism.

### 2026-07-24 Reverse-target mixed recovery collapse

- [WORKS] When one \(B_U^{\pm1}\)-multiplication targets \(D\), the cyclic isolator classification transfers because \(V_DV_B\) and \(V_BV_D\) are conjugate, but the restored source \(B_U=z^{-1}w\) must be substituted separately. The exact survivors are \(C_+=w^{-1}S_0^{-1}w\) and \(C_-=(t^{-1}w)^{-1}S_0(t^{-1}w)\), so both return by AC1/AC3 to the direct endpoint \(Q(U)\).
- [TRAP] Closing both target/source roles after “all recovery, then one \(D\)-factor” closes only that order's one-\(z\)-elimination stratum. It does not close \(D\)-before-\(R\) or alternating \(R/D\) interleavings, two \(D\)-factors, or primitive eliminators with several \(z^{\pm1}\)-occurrences.

### 2026-07-24 Post-catalyst quotient shadows

- [WORKS] With \(R\in F(X)\) fixed, work in \((F(X)/\langle\!\langle R\rangle\!\rangle)*\langle z\rangle\). Equality of isolator shadows \(z^{-1}e=z^{-1}e_0\) forces \(e=e_0\) modulo \(R\); evaluation at \(z=e\) then sends quotient-equal survivor shadows to the same element modulo \(R\). The fixed-relator normal-closure lemma converts this into classical AC equivalence after deletion.
- [WORKS] This closes arbitrary fixed-\(R\) gauge suffixes after one classified \(B_U/D\) catalyst, including gauge factors on both the future isolator and survivor and conjugators containing \(z\). The \(D\)-then-\(R\) collected order is therefore a self-loop in both target roles.
- [TRAP] The quotient-shadow theorem requires the final chosen isolator spelling and survivor to retain their exact post-catalyst quotient shadows. It does not cover a net conjugation/inversion that is not restored, pre-catalyst \(R\)-twisting of \(D\), a second \(B_U/D\) cross multiplication, a changed \(R\), or a multi-\(z\) primitive eliminator.

### 2026-07-24 New-file EOF checks

- [TRAP] An added file with an explicit empty content line after its final paragraph triggers `git diff --check` with `new blank line at EOF`, even though the rendered Markdown or Python looks unchanged.
- [WORKS] Run `git diff --check` after staging new proof artifacts and remove the final empty content line while preserving the normal terminating newline.

### 2026-07-25 Bass--Serre vertex stabilizers

- [TRAP] In \(G*\langle z\rangle\), intersecting hyperbolic axes are not exhausted by literal signed syllable rotations. If the axes meet only at a vertex, its nontrivial stabilizer leaves a residual twist \(UhVh^{-1}\) with \(h\in G\) or \(h\in\langle z\rangle\). Importing the free-group Cayley-tree rotation lemma unchanged leaves an infinite gap.
- [TRAP] For disjoint Bass--Serre axes, do not assert a literal bridge spelling with exact \(z\)-incidence unless endpoint stabilizer twists have been normalized. Vertex stabilizers make that free-group argument unsafe.
- [WORKS] Exclude the disjoint case invariantly: \(\ell(B)=2\), \(\ell(D)=4\), and disjoint axes give product translation length \(6+2d\ge8\), while the cross-product weight \(7\pm1\) makes any one-\(z\) shadow nonelliptic of length \(2\).
- [WORKS] Split quotient axes into disjoint, shared-edge, and shared-vertex cases. For the AK(3) \(B/D\) pair, the \(G\)-vertex one-\(z\) condition forces one unique \(h\) in each signed \(2\times4\) cell; the \(z^k\)-vertex condition has four affine-exponent solutions per sign. Every cell returns `ZTxtx` or `ZtxtX`.
- [TRAP] In the \(z^k\)-vertex table, do not combine powers across a separating \(G\)-syllable. For \((B_0,D_1^+)\), the cyclic incidence is \(|k+1|+1+|-k-1|=2|k+1|+1\), not a two-factor boundary calculation.
- [WORKS] This corrected quotient classification closes arbitrary fixed-\(R\) gauge moves on either slot before and after exactly one \(B/D\) cross multiplication when the cross target becomes the final generator isolator.
- [TRAP] It does not cover preserving the cross target and eliminating the restored source instead, a second cross event, a changed \(R\)-normal closure, or a multi-\(z\) primitive eliminator.

### 2026-07-25 LaTeX line-end whitespace

- [TRAP] A display split across Markdown lines as `\ \text{or}\ ` left a literal trailing space and failed `git diff --check`.
- [WORKS] End the LaTeX command at the final backslash with no following space, and run `git diff --check` before staging.

### 2026-07-25 Proof-test import roots

- [TRAP] Running `python3 tests/stable_ac/test_*.py` directly sets the import root to `tests/stable_ac` and fails with `ModuleNotFoundError: No module named 'experiments'`.
- [WORKS] From the repository root, use `python3 -c 'import runpy; ... = runpy.run_path(...)'` so the current directory remains on `sys.path`, then invoke the dependency-free `test_*` functions.

### 2026-07-25 Passive-source normal-closure absorption

- [WORKS] If a final isolator \(I=z^{-1}e\) has quotient normal closure \(L\), evaluation at \(z=e\) kills all of \(L\). Any finite number of left or right survivor multiplications by conjugates of source spellings in \(L\) therefore disappears after elimination; target conjugation/inversion survives only as AC3/AC1.
- [TRAP] Restoring the source only at the end is insufficient. Every source spelling used at a cross event must lie in the final \(L\); a temporary source outside \(L\) can leave a permanent nontrivial factor in the survivor quotient.
- [WORKS] For the AK(3) rank-three root, this closes arbitrarily many passive \(B=z^{-1}xt\)-source events targeting \(D\). The opposite passive-\(D\) one-\(z\) elimination is impossible because \(D=t^{-1}zxz^{-1}\) has \(z\)-exponent zero.

### 2026-07-25 Checkpoint plan state

- [TRAP] Do not mark a plan's commit-and-push item complete before both Git commands have actually succeeded. Keep it unchecked through staging and verification, then update it in a follow-up checkpoint if necessary.

### 2026-07-25 Passive-source scope versus repeated targets

- [TRAP] Passive-source absorption closes repeated cross events only when the eventual eliminator is the source at every event. It does not close two or more source factors multiplied into a slot which is itself later used as the eliminator.
- [WORKS] Split the two-cross frontier into repeated hits on the eventual eliminator and alternating-target feedback. Do not describe feedback as the only remaining two-cross mechanism.

### 2026-07-25 Quotient by the passive source

- [WORKS] For repeated \(D\)-source hits on \(B\), quotient by \(D\) instead of analyzing three interacting axes. The quotient is the HNN extension \(\langle G,z\mid zxz^{-1}=t\rangle\); Britton--Collins conjugacy forces every final one-\(z\) tail to \(e_n=t^{-n}(xt)x^n\), and \(D(e_n)=t^{-n}D(xt)t^n\).
- [WORKS] For repeated \(B\)-source hits on \(D\), quotient by \(B\), set \(z=xt\), and read the surviving \(B\)-relator as the inverse of the final target class. This closes every one-way history that actually produces a one-\(z\) target; when each event source is a signed conjugate of \(B\), even event count is excluded by \(z\)-exponent parity.
- [TRAP] Per-event membership in the passive source normal closure erases cross factors, but it does not finish the endpoint argument. If the source survives, restore its final quotient shadow up to conjugation/inversion; if it is eliminated, require its final isolator to preserve the baseline source normal closure.

### 2026-07-25 Original-source quotient closes two-cross feedback

- [WORKS] In the alternating order “\(D^\epsilon\) targets \(B\), then the modified \(B_1^\eta\) targets \(D\),” quotient by the original \(D\), not by \(B_1\). This erases the first cross, makes the final target conjugate to \(B\), and reuses the HNN family with \(n=\epsilon+\eta\).
- [WORKS] Evaluation of the second target identity forces the actual \(B_1\)-survivor to be conjugate to \(D(e_n)^{-\eta}\), so arbitrary conjugators and either multiplication side introduce no new endpoint.
- [TRAP] In the reverse alternating order, the second target has \(z\)-exponent \(0\) or \(\pm2\); do not spend a cancellation census on a one-\(z\) isolator that exponent already forbids.

### 2026-07-25 Replay manifests must use tree paths

- [TRAP] A compacted checkpoint can abbreviate test filenames. Before a multi-file `runpy` replay, resolve every path with `rg --files tests/stable_ac`; otherwise the harness can fail before exercising any proof test.

### 2026-07-25 Three-cross bridge census fan-out

- [TRAP] Do not enumerate even one-letter relative bridges independently at all three cross events: signed rotations and cyclic classes already expand the second-stage pair set enough to make the third Cartesian product impractical. Derive the exponent/weight and quotient equations first, and use a finite census only on the resulting zero-bridge seam cases.

### 2026-07-25 Patch theorem ledgers by exact local anchors

- [TRAP] Before inserting a new numbered result into `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`, read the exact paragraph immediately before `## Live lead`; compacted summaries can omit a line and make a broad multi-file patch fail atomically.

### 2026-07-25 Three-cross routes reach the killer frontier

- [WORKS] In the strict order \(D\to B\to D\to B\), the third target has \(z\)-exponent \(0\) or \(\pm2\); eliminating its source erases the third event and reduces to the two-cross theorem.
- [WORKS] In the reverse strict order, exactly six sign triples have a one-\(z\) third target. Weight pins the tail to \(5,7,\) or \(9\) and the evaluated survivor to weight \(\pm1\), so the endpoint is a killer of \(\langle x,t\mid x^3=t^4\rangle\).
- [TRAP] Never infer “killer implies meridian” in a torus-knot group. Silver--Whitten--Williams, Theorem 1.2 and Corollary 1.3, give infinitely many inequivalent pseudo-meridians in every nontrivial torus-knot group.
- [WORKS] The literal untwisted three-seam grammar is finite: \(16\) first targets, \(416\) intermediate pairs, \(522\) one-\(z\) triples, \(69\) final target classes, and one evaluated survivor class \(D_p^{\pm1}\). Keep arbitrary bridges, vertex twists, and literal \(R\)-gauges outside this certificate's scope.

### 2026-07-25 Split ledger insertion from live-lead rewrites

- [TRAP] Even after reading the local anchor, a combined result insertion plus distant live-lead replacement can fail atomically on whitespace. Patch the new numbered result and the live-lead paragraph separately, then read both back.

### 2026-07-25 All exactly-three target words

- [WORKS] Record a three-event history by its target word in \(\{B,D\}^3\). The one-way theorem closes \(BBB,DDD\); quotient and exponent arguments close \(BBD,BDD,DDB\); the strict theorem closes \(BDB\).
- [WORKS] For \(BBD\), quotient by original \(D\): both earlier hits vanish, HNN weight gives \(n=\epsilon+\eta+\theta\), and evaluation identifies the survivor with \(D(e_n)^{-\theta}\). For \(DDB\), quotient by original \(B\): the two earlier hits vanish and final-target evaluation identifies the survivor with \(D_p^{\pm1}\).
- [TRAP] Exactly three cross events are not exhausted by strict alternation. The only two killer target words are \(DBB\) and \(DBD\); both have six feasible sign rows and the tail-weight set \(\{5,7,9\}\).
- [WORKS] The literal untwisted \(DBB\) grammar has the same \(16/416/522/69\) counts as \(DBD\) and the same unique survivor class \(D_p^{\pm1}\). Arbitrary bridge/twist geometry remains open in both.

### 2026-07-25 Keep hostile audit scripts readable

- [TRAP] Do not compress an independent matrix census into a nested one-line assertion; a parenthesis error can invalidate the audit while later shell checks continue. Build the result dictionary in a plain loop, print it, and assert it separately.

### 2026-07-25 Final-target switch duality

- [WORKS] A final target \(A\,uB^\theta u^{-1}\) is conjugate to \(B^\theta u^{-1}Au\), so the same final isolator can be realized with either slot designated as target.
- [WORKS] Evaluation of that target gives \(A_e=u_eB_e^{-\theta}u_e^{-1}\) in the fixed-\(R\) quotient. The two possible survivors are therefore classically AC-equivalent by the fixed-relator lemma, AC1, and AC3.
- [WORKS] Pair target words by their last letter. In particular \(DBB\leftrightarrow DBD\), so exactly-three traffic has one arbitrary bridge/twist killer mechanism with prefix \(DB\), not two.

### 2026-07-25 Central quotient plus weight lifts conjugacy

- [WORKS] In \(G=\langle x,t\mid x^3=t^4\rangle\), the central quotient by \(c=x^3=t^4\) is \(C_3*C_4\), with kernel exactly \(\langle c\rangle\).
- [WORKS] If two elements have conjugate images in \(C_3*C_4\), they differ after lifting the conjugator by \(c^k\); equal torus weight forces \(12k=0\), so quotient conjugacy plus weight exactly decides conjugacy in \(G\).
- [WORKS] Decide conjugacy in \(C_3*C_4\) by cyclically reducing the alternating normal form and comparing cyclic rotations. This gives an exact finish test for a weight-\(\pm1\) prefix-\(DB\) survivor against \(D_p^{\pm1}\).
- [TRAP] Failure of projected conjugacy rules out only the direct fixed-\(R\) conjugacy finish. It is not AC inequivalence, not a stable-AC obstruction, and not a counterexample certificate.

### 2026-07-25 Distinguish literal endpoints from AC3 endpoints

- [TRAP] If \(D_p=t^{-1}St\), then \((R,D_p)\) is AC3-equivalent to \((R,S)\), not literally equal to it. Write the conjugation step explicitly in displayed endpoint chains.
- [TRAP] Define every endpoint symbol locally before using it in a proof chain; importing the meaning of \(S\) from an earlier theorem makes a corrected equality formally incomplete.
- [TRAP] A finite replay over \(-12\le n\le12\) samples an infinite HNN family; describe the replay as representative even when a separate symbolic identity proves the formula for every \(n\).

### 2026-07-25 Zsh reserves `path`

- [TRAP] In zsh, assigning a loop variable named `path` mutates the special array tied to `PATH` and can make the next command fail with `command not found`. Use `proof_file` or another task-specific name in shell loops.

### 2026-07-25 Evaluated prefix-DB equations lose liftability

- [WORKS] The evaluated \(DBD\) system reduces to \(K=d\alpha b^\epsilon\alpha^{-1}\), \(C=b\beta K^\eta\beta^{-1}\), and \(1=K\gamma C^\theta\gamma^{-1}\). With \(\rho=\beta\gamma\) and \(m=\eta\theta\), this forces \(b=C\rho C^m\rho^{-1}\).
- [WORKS] The feasible \((+,+,-)\) row has an exact weight-one killer solution whose image in \(C_3*C_4\) has cyclic length \(2\), while \(D_p^{\pm1}\) have cyclic length \(6\). Thus the evaluated equations, weights, and killer property do not force the braid class.
- [WORKS] When lifting a projected solution by central powers, solve all central defects simultaneously and verify the resulting amalgam normal forms; independent equation-by-equation shifts need not be globally consistent.
- [WORKS] Quotienting a genuine \((+,+,-)\) \(DBD\) history by the original \(B=z^{-1}p\) turns its third target into \([D_p,h]\) up to conjugacy/inversion. The explicit countermodel would require a cyclic-length-\(4\) commutator, while the complete Bass--Serre edge/vertex reduction permits only \(0,8,10,12\), or at least \(14\); hence that countermodel is nonliftable.
- [TRAP] From \(T[z\mapsto e]=1\), conclude only \(T\in\langle\!\langle z^{-1}e\rangle\!\rangle\). A legal one-\(z\) deletion requires \(T\) to be a single conjugate of \(z^{-1}e\), a strictly stronger Bass--Serre liftability condition.
- [TRAP] Track the final orientation: in the \((+,+,-)\) row, \(\delta=-1\), so \(D_2^{-1}\), not \(D_2\), is conjugate to \(z^{-1}e\). An arbitrary conjugate can contain many literal \(z\)-letters; the invariant statement is that its conjugacy class has a cyclically reduced syllable-length-two representative.
- [TRAP] A non-braid killer solving the evaluated equations is not an AC obstruction, an AC-inequivalent endpoint, or a realized stable history.

### 2026-07-25 Replace complete prose sentences

- [TRAP] A line-level wording patch can preserve the old first line and insert the revised sentence beneath it, duplicating a clause. Replace the complete sentence or paragraph and read the local result immediately.

### 2026-07-25 Search LaTeX with fixed strings

- [TRAP] Combining escaped LaTeX delimiters and alternation in one `rg` regular expression can produce `regex parse error: unopened group`. Use separate fixed-string searches (`rg -F`) for proof-notation audits.

### 2026-07-25 Stage ignored proof directories separately

- [TRAP] An explicit `git add` path under ignored `literature/` can abort a mixed staging command even when some proof files are already tracked. Stage ordinary files first, then use `git add -f` with every exact intended proof-file path.

### 2026-07-25 Quotient-B length gap for all six rows

- [WORKS] Quotienting a prefix-\(DB\) \(DBD\) representative by the original \(B=z^{-1}p\) sends its third target to \(W_m(h)=D_phD_p^mh^{-1}\), where \(m=\eta\theta\), and literal liftability forces \(b=e^{-1}p\) to be conjugate to \(W_m(h)^{-\delta}\).
- [WORKS] The Bass--Serre spectra are unbounded but exact: for \(m=-1\), cyclic length is \(0,8,10,12\), or \(12+2d\ge14\); for \(m=1\), it is \(6,10,12\), or \(12+2d\ge14\).
- [WORKS] All four \(m=-1\) rows have \(\operatorname{wt}(b)=0\). Quotient length zero puts \(b\) in the central kernel, weight forces \(b=1\), and the survivor is a conjugate of \(D_p^\eta\). Thus every non-braid commutator-row lift has quotient length at least \(8\).
- [WORKS] The minimum \(m=1\) stratum has exactly two projected length-six classes. Their weight-two central lifts determine the tail up to conjugacy, but the previous non-braid killer solves the last two evaluated equations in both classes; the first-cross equation and free-kernel lift remain essential.
- [TRAP] The positive-length spectra are necessary liftability conditions, not sufficient constructions and not AC obstructions. The two \(m=1\) rows genuinely begin at length \(6\).

### 2026-07-25 Qualify zero-length self-loops

- [TRAP] Do not call every nonempty three-cross history “nontrivial” when its quotient shadow can have cyclic length zero. State the precise condition \(\bar b\ne1\), positive quotient length, or non-braid endpoint.
- [TRAP] In LaTeX spectrum tables, the `array` column declaration must count the label column plus every numeric heading; a five-value spectrum uses `c|rrrrr`.

### 2026-07-25 Follow the operating-contract AC numbering

- [TRAP] The project prompt defines AC1 as relator multiplication, AC2 as relator inversion, and AC3 as conjugation. Some legacy proof prose uses a different numbering. When removing a survivor sign, name AC2 or say AC1--AC3; never say AC1 removes the sign.
- [TRAP] A \(6\times6\times6\) rotation/twist list is an overcomplete template census. Call \(k=1\) the template slice covering shared-edge cases and the other \(180\) nonidentity-twist templates; they are not counts of geometrically distinct axis configurations.
- [TRAP] Once whole-slot inversions have been absorbed into canonical signs \(\epsilon,\eta,\theta,\delta\), do not leave a residual “up to inversion” ambiguity in the quotient equation. Multiplication-side changes leave only conjugacy, which is needed for exact oriented class statements such as \(b^{-\delta}\sim\lambda_j\).

### 2026-07-25 Distinguish lifts from lifted conjugacy classes

- [TRAP] A projected conjugacy class has many literal lifts and representatives. Weight plus projected conjugacy determines a unique \(G\)-conjugacy class, not a unique word or element.
- [TRAP] State an “if and only if” length classification only inside the necessary quotient equation it classifies; arbitrary elements of the same weight and length need not occur as \(AhA^mh^{-1}\).

### 2026-07-25 Superpowers plan location and scratch-length replay

- [TRAP] This worktree stores design and execution artifacts under `docs/superpowers/specs/` and `docs/superpowers/plans/`; probing nonexistent `docs/specs/` or `docs/plans/` wastes a retry.
- [TRAP] An informal scratch note recorded quotient cyclic length \(26\) for one dual first-cross product, while the independent normal-form replay gives \(24\). Never promote scratch numerics into a theorem.
- [WORKS] Derive every stated projected length from `projected_conjugacy_key` in `tests/stable_ac/test_prefix_db_evaluated_countermodel.py`; do not infer a uniform lower bound from the two factor lengths.

### 2026-07-25 Translation length has no reverse triangle inequality

- [TRAP] Tree translation length is conjugacy invariant but is not a norm. For arbitrary relative conjugation, \(\ell(g^{-1}uhu^{-1})\ge|\ell(g)-\ell(h)|\) is false: the four minimum-template probes reach \(12,14,16,14\), below the proposed \(16/20\) bounds.
- [WORKS] Before using an axis inequality uniformly over a free conjugator, enumerate reduced conjugators far enough to attack it. Then replace the false inequality by the complete relative-axis product formula or an exact cyclic-word overlap argument.
- [TRAP] Do not cite a two-axis product formula without checking which overlap regime applies. A conjugated short cyclic word can acquire a long handle whose cancellation with the other factor changes the product length even though its own translation length stays short.

### 2026-07-25 Repositioned minimum tails and the exact free-kernel frontier

- [TRAP] Failure of the first-cross equation for fixed \(C,\rho,b\) representatives need not survive simultaneous conjugation: \(e=pb^{-1}\) keeps \(p=xt\) fixed, so \(d=t^{-1}exe^{-1}\) changes non-equivariantly.
- [WORKS] A repositioned row-\((+,-,-)\) length-six tail satisfies all three evaluated equations with a non-braid killer. The first evaluated cross equation is therefore not a general minimum-stratum barrier.
- [WORKS] For \(\Phi=(r_e,r_p):G*\langle z\rangle\to G\times G\), \(\operatorname{im}\Phi=\{(g,gn):n\in\langle\!\langle e^{-1}p\rangle\!\rangle_G\}\). Use this image subgroup, not separate evaluations, to test bridge synchronization.
- [WORKS] With \(q=ze^{-1}\), the true remaining target condition is a three-variable equation in the free kernel \(N=F\{q_g:g\in G\}\): the resulting \(n_3(U,V,W)\) must be conjugate to one negative distinguished basis letter.
- [TRAP] Kernel length seven for the literal \(G\)-valued bridges proves only that \(U=V=W=1\) fails. It is not evidence that arbitrary kernel-decorated lifts fail.
- [TRAP] Scalar augmentation \(-1\) checks only the augmentation of \(N_{\rm ab}\cong\mathbb Z[G]\). It does not solve the full Fox group-ring equation and must not be reported as “the abelian obstruction vanishes.”
- [WORKS] Project the explicit Fox equation to \(\mathbb F_p[Q]\) for finite quotients \(G\to Q\). Linear failure is a rigorous nonlift certificate; linear success remains only necessary.

### 2026-07-25 Target-word replay filename

- [TRAP] The three-cross target-word replay is `tests/stable_ac/test_three_cross_target_words.py`, not a filename copied from the proof title such as `test_three_cross_target_word_classification.py`.
- [WORKS] Resolve verification manifests with `rg --files tests/stable_ac` before running them; a missing test must not silently reduce the claimed replay total.

### 2026-07-25 Patch audited claims by exact local paragraph

- [TRAP] A multi-file `apply_patch` aborts atomically when one wrapped prose paragraph differs from the assumed context, even if every other hunk is correct.
- [WORKS] After a hostile wording audit, locate every exact phrase with `rg`, read the local paragraphs, and patch those verified contexts together.

### 2026-07-25 Bound finite-quotient Fox scans before symmetric degree six

- [TRAP] Enumerating every exact-order generator pair in \(S_6\) repeats many conjugate representations and spends most time rebuilding the same subgroups and linear spans.
- [WORKS] The complete raw scans through \(S_4\) and \(S_5\) found no Fox obstruction. Treat that only as bounded negative evidence, stop before an uncached \(S_6\) fan-out, and prefer the exact \(\mathbb Z[P\backslash G]\) coset-module reduction or conjugacy-class representatives.
- [WORKS] For any longer finite-quotient scan, run Python unbuffered and print/cache quotient signatures so progress is visible and duplicate representations are removed.

### 2026-07-25 Fox bridge ideal and infinite-index subgroup

- [WORKS] In the repositioned minimum-tail Fox equation, the \(V,W\) coefficients generate exactly \(I_P=\sum_{p\in P}(p-1)\mathbb Z[G]\) for \(P=\langle K,\gamma b\gamma^{-1}\rangle\). Quotient them first; the remaining equation lives in \(\mathbb Z[P\backslash G]\).
- [WORKS] The projected generators of \(P\) are two length-two hyperbolics with disjoint axes at distance one. Tree ping-pong gives \(P\cong F_2\), the central projection is injective on \(P\), and Euler characteristic proves infinite index.
- [WORKS] The exact \(S_4\) quotient maps \(P\) to a point stabilizer. Its four-coset Fox module restricts the target residue to that stabilizer.
- [TRAP] A finite Fox quotient which leaves even one target residue is not a nonlift certificate. Here the identity residue survives, so the \(S_4\) restriction is progress but not closure.

### 2026-07-25 Retry a timed-out exact force-add once

- [TRAP] Automatic approval review can time out while force-adding one exact ignored proof file; a timeout is not a safety rejection and does not imply the path is wrong.
- [WORKS] Retry the identical exact `git add -f literature/proofs/<file>` once, then stop for guidance if the retry also fails.

### 2026-07-25 Compile folded-graph scratch helpers before running

- [TRAP] A missing parenthesis in an inline folded-coset prototype can abort before any mathematical check and waste a full retry.
- [WORKS] Keep the prototype short, run its syntax/initialization path first, and only then add the subgroup and coset-module workload. Treat an aborted prototype as producing no evidence.

### 2026-07-25 System `py_compile` cache outside the worktree

- [TRAP] `python3 -m py_compile .scratch/<file>.py` tries to create its mirrored bytecode cache under `~/Library/Caches/com.apple.python/...` and fails in the isolated worktree with `PermissionError: [Errno 1] Operation not permitted`.
- [SUPERSEDED] `python3 -m ast < .scratch/<file>.py` does parse the file, but dumps the entire AST and creates unusably noisy logs.
- [WORKS] Syntax-check scratch proof helpers with `PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONPATH=. python3 -m py_compile .scratch/<file>.py`, then run them with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.`. The explicit `PYTHONPATH` is required because launching a script under `.scratch/` otherwise omits the project root and breaks imports such as `experiments`.

### 2026-07-25 Folded-core homology orientation

- [TRAP] A folded coset core can accept both subgroup generators while a guessed fundamental-cycle coordinate still assigns the wrong second basis vector; graph acceptance alone does not validate the homology transducer.
- [WORKS] Replay the complete state path and raw oriented edge chain for each named subgroup generator, derive the coordinate change from those two actual chains, and only then use central weight to decide membership in \(P<G\).

### 2026-07-25 Canonicalize cosets before linear algebra

- [TRAP] Pairwise `same_left_coset` clustering is quadratic in all support points; the exact target solve reached 1,016 rows at multiplier radius five but spent over two minutes constructing radius six and required interruption.
- [WORKS] Use the folded core to assign a canonical left-coset key (core transversal, first unreadable tail, and central defect) once per word. Build sparse module rows by hashing that key rather than comparing every pair by subgroup membership.

### 2026-07-25 Test finite-module targets by coset, not element

- [TRAP] Recomputing a full augmented RREF for every element of an 8,064-element combined quotient repeats the same target vector once per element of each left \(P\)-coset and required interruption.
- [WORKS] Row-reduce the orbit-column span once, test one basis target for each left coset, and then lift the allowed coset indices back to group elements only if needed.

### 2026-07-25 Left multiplication is not a coset-module action

- [TRAP] In the right module \(\mathbb Z[P\backslash G]\), \((1+L)z\) maps to \([Pz]+[PLz]\), not \([Pz]+[PzL]\). Left multiplication by \(L\) is not a well-defined action on left cosets unless \(L\) normalizes \(P\); the folded core proves \(L\notin P\) here.
- [WORKS] Evaluate every coefficient monomial before taking its left coset, or use a row representation \(F([Pg])=\ell\rho(g)\) with \(\ell\rho(P)=\ell\). Never turn a left group-ring factor into a right Schreier orbit.

### 2026-07-25 Do not mix LaTeX backslashes into audit alternation

- [TRAP] An `rg` alternation containing the shell spelling `L\\notin P` was parsed as a forbidden literal newline escape and aborted the entire final claim audit.
- [WORKS] Run prose alternatives and each LaTeX command as separate fixed-string searches with `rg -F`; never place LaTeX backslashes inside a shared regular-expression audit.

### 2026-07-25 Layer BFS must expand the current frontier

- [TRAP] A scratch basis-word BFS compared `len(word) >= depth` while starting at depth zero, consumed the only frontier state, and then reported empty frontiers at every later depth.
- [WORKS] Advance one complete frontier layer per outer iteration and build the next layer unconditionally from those states; test that depth one has the expected signed-generator count before trusting a null word search.

### 2026-07-25 Fold two-generator subgroups before word BFS

- [TRAP] Literal \(G\)-normal-form BFS in the signed generators \(K,d\) reached 118,097 words at depth ten and spent over a minute rebuilding long representatives before interruption.
- [WORKS] Fold the two projected generator loops first. Use the finite precover for subgroup membership and central voltage, then search only the few support-word differences required by the module equation.

### 2026-07-25 Distinguish the central element from the candidate relator

- [TRAP] In the minimum-tail replay, `candidate_c` denotes the repositioned candidate relator, while theorem notation \(c\) denotes the central element \(x^3=t^4\); substituting the former into \(t^{-1}c=t^3\) makes the exact identity fail.
- [WORKS] Implement the central-extension element with an explicit name such as `central_word = "xxx"`.

### 2026-07-25 Keep LaTeX commands out of regex claim audits

- [TRAP] Repeating an `rg` alternation with `\notin` again triggered the literal-newline parser error and aborted every later audit pattern in that command.
- [WORKS] Audit each LaTeX-bearing claim with a separate `rg -F '<literal>'` invocation; use regex alternation only for plain prose.

### 2026-07-25 Agent waits have a ten-second minimum

- [TRAP] `wait_agent` rejects `timeout_ms` below 10000; a one-second poll produces only a parameter error.
- [WORKS] Use `timeout_ms: 10000` for the shortest agent-status wait.

### 2026-07-25 Do not generate mixed LaTeX regex alternations

- [TRAP] Dynamically joining search terms into one `rg` regex reintroduced invalid escapes such as `\Xi`, even after the literal-search rule was recorded.
- [WORKS] For mathematical symbols, issue separate `rg -F` calls or search only their plain identifier fragments; never programmatically assemble them into one regex.

### 2026-07-25 Carry structural hypotheses into theorem headlines

- [TRAP] The signed Fox factorization is universal, but its HNN-incidence kernel conclusion requires \(J=\langle K,L\rangle\cong F(K,L)\); stating the conclusion before that hypothesis made the opening broader than the proof.
- [WORKS] When a theorem has an unconditional algebraic half and a conditional geometric half, put the geometric hypothesis in the status paragraph as well as in the proof body.

### 2026-07-25 Claim audits must use the file's actual delimiter spelling

- [TRAP] A fixed-string audit searched for `$J=` although the manuscript used `\(J=`, so the check failed despite the required sentence being present.
- [WORKS] Copy the exact phrase from a readback into `rg -F`; do not guess whether the file uses dollar or parenthesized LaTeX delimiters.

### 2026-07-25 Rank-three Whitehead imports require numba transitively

- [TRAP] Importing `one_edge_primitive.whitehead_graph_gate` under system Python reaches `acmoves.py` and fails with `ModuleNotFoundError: No module named 'numba'`.
- [WORKS] Replay rank-three Whitehead certificates with `uv run --with numba --with numpy python3 ...` in this worktree.

### 2026-07-25 Sandbox uv cannot open the global cache

- [TRAP] A sandboxed `uv run` fails at `~/.cache/uv/sdists-v9/.git` with `Operation not permitted` before dependency resolution begins.
- [WORKS] Run the exact approved `uv run --with numba --with numpy` verifier with escalation so it can reuse the existing global dependency cache.

### 2026-07-25 Keep macOS Python bytecode inside the worktree

- [TRAP] `python3 -m py_compile` tries to create a mirrored cache below `~/Library/Caches/com.apple.python/` and fails under the workspace sandbox even when the source file is writable.
- [WORKS] Set `PYTHONPYCACHEPREFIX=.scratch/pycache` for syntax checks so generated bytecode remains project-relative.

### 2026-07-25 Patch theorem sections by exact local anchors

- [TRAP] One large theorem-generalization patch assumed that `Choose` immediately followed the section lead, but an intervening displayed map made the context fail and rejected the whole patch.
- [WORKS] Read the exact section first, then patch one locally anchored theorem block at a time when notation and equation numbers are changing together.

### 2026-07-25 Do not mix Markdown backticks into shell regex quoting

- [TRAP] An `rg` audit embedded Markdown backticks and escaped LaTeX inside one double-quoted shell pattern, causing zsh to report `unmatched "`.
- [WORKS] Use separate single-quoted fixed-string searches for prose fragments; never combine Markdown backticks and LaTeX into one shell regex.

### 2026-07-25 Mathematical claim audits are fixed-string only

- [TRAP] A follow-up audit removed the backticks but still combined escaped LaTeX fragments in one regex, producing `regex parse error: unclosed group`.
- [WORKS] Enforce the existing rule literally: every mathematical claim audit uses its own `rg -F` command, with no regex alternation at all.

### 2026-07-25 Compare automorphism images as reduced group words

- [TRAP] The nontrivial-\(U\) replay compared `phi["q"]` with the raw concatenation `beta_u + "q"`; when `beta_u` ended in `Q`, the implementation correctly canceled the terminal `Qq` and the assertion failed.
- [WORKS] Every literal expected image assembled from word pieces must pass through `free_reduce` before comparison.

### 2026-07-25 Split ledger insertions from live-lead rewrites

- [TRAP] A single patch combined a new numbered result with two distant live-lead replacements; one stale line wrap in the final hunk rejected the entire otherwise-correct insertion.
- [WORKS] Insert a numbered result in one patch, read the current live-lead text, then patch each live-lead paragraph separately.

### 2026-07-25 Rank-three Whitehead reducer is alphabet-hardcoded

- [TRAP] Passing generators `("x","t","z","q")` to `rank3_whitehead.reduce_word_fast` still fails before reduction because `two_stabilization._validate_word` rejects `q`; the downstream `generators` parameter does not make the word utilities rank-generic.
- [WORKS] Use a dependency-free rank-four Whitehead implementation for \(F(x,t,z,q)\); do not treat the rank-three validator failure as evidence about primitivity.

### 2026-07-25 Build focused test manifests from repository paths

- [TRAP] A combined replay named `test_relation_split_primitive_self_loop.py` from the theorem title, but the repository file is `tests/stable_ac/test_relation_split_primitive_loop.py`; pytest stopped before running any test.
- [WORKS] Before assembling a multi-file replay command, derive the exact manifest with `rg --files tests/stable_ac` rather than translating proof titles into guessed filenames.

### 2026-07-25 Run diff-check before staging new Markdown

- [TRAP] A newly added design spec retained a blank line after its final paragraph; `git diff --check` correctly stopped the combined stage-and-commit command before any files were staged.
- [WORKS] Keep the pre-stage `git diff --check` gate, remove trailing blank lines with `apply_patch`, and rerun the full gate before committing.

### 2026-07-25 Separate file moves from theorem-wide rewrites

- [TRAP] One patch tried to rename a new proof and simultaneously replace many LaTeX-aligned blocks; a single mismatch around `&=` rejected the whole proof update.
- [WORKS] Move the file first, then rewrite one exact section at a time using anchors copied from a fresh readback.

### 2026-07-25 Apply-patch moves require a content hunk

- [TRAP] An `apply_patch` update containing only `*** Move to:` is rejected as an empty hunk.
- [WORKS] Pair every file move with one minimal verified content change, such as updating the document title.

### 2026-07-25 Re-read the exact small block after partial rewrites

- [TRAP] After several successful local theorem patches, a later hunk still used the pre-rewrite quotient symbols and an assumed duplicate line, so its context failed.
- [WORKS] After each cluster of local patches, read the next 80-line block fresh and use only its current literal symbols as patch anchors.

### 2026-07-25 Treat overlapping sed output as presentation, not file content

- [TRAP] Two overlapping `sed` ranges made a boundary line appear twice in combined output; a later patch included that apparent duplicate and missed the actual single-copy paragraph.
- [WORKS] When auditing a suspicious duplicate, read one non-overlapping range around it before constructing the patch.

### 2026-07-26 Do not regress a recorded split-patch rule

- [TRAP] The Result 41 insertion was again bundled with two distant live-lead rewrites even though the project already records that this pattern rejects the whole patch on one stale line wrap.
- [WORKS] Treat a matching project lesson as an executable constraint: insert a numbered result alone, read back the exact live-lead paragraphs, and only then patch those paragraphs.

### 2026-07-26 Resolve proof filenames before parallel reads

- [TRAP] A theory read guessed `AK3_SOURCE_SLOT_PRIMITIVE_EXCHANGE.md`; the tracked file includes the `_SELF_LOOP.md` suffix, so that arm of the combined read failed.
- [WORKS] Resolve proof paths with `rg --files literature/proofs | rg '<stem>'` before issuing a multi-file read, just as for focused test manifests.

### 2026-07-26 Expand named words inside letter-level replay inputs

- [TRAP] `test_changed_q_source_gauge.py` put the mathematical name `D` inside a literal conjugator string, but the free-word alphabet contains only `xXtTzZqQ`; inversion failed with `KeyError: 'D'`.
- [WORKS] Build mixed conjugators by concatenating the defined word constant, such as `"Z" + D + "q"`, and freely reduce before passing them to letter-level helpers.

### 2026-07-26 Apply audit-driven scope changes one artifact at a time

- [TRAP] One patch tried to broaden the passive-slot theorem across proof, spec, and test; a stale equation block rejected every hunk. A follow-up typo then guessed a nonexistent context line.
- [WORKS] For a scope generalization, read and patch the theorem statement/proof first, then patch the concrete specialization, boundary, spec, and replay in separate verified hunks.

### 2026-07-26 Treat the live-lead tail as a separate patch target

- [TRAP] The Result 43 live-lead rewrite again combined the main source paragraph with the distant final paragraph; a line-wrap mismatch in the tail rejected both changes.
- [WORKS] After inserting a numbered result, patch the first live-lead paragraph alone, then read `tail` and patch the final frontier paragraph separately.

### 2026-07-26 Replay ambient straightening on the inner payload letter

- [TRAP] The first qW-tail derivation tracked the second straightening on the outer conjugator but implicitly fixed the inner `x`; since `beta^{-1}(x)=q^{-1}xq`, the exact replay contradicted the claimed V=R endpoints.
- [WORKS] For an endpoint `t^{-1} E x E^{-1}`, compute and replay both `theta^{-1}(E)` and `theta^{-1}(x)`. Here the missing image is `x -> V^eta x V^{-eta}`, which changes the conjugator to `p V^{-eta} R V^eta`.

### 2026-07-26 Resolve Whitehead verifier names before importing

- [TRAP] The rank-four translated Whitehead probe guessed `verify_word_reduction`, but `rank3_whitehead.py` exports `check_word_reduction`; the import failed before any mathematical computation.
- [WORKS] Resolve verifier entry points with `rg '^def (check|verify)'` before an inline proof probe, then import the exact symbol.

### 2026-07-26 Do not BFS the full strict Whitehead descent DAG

- [TRAP] A shortest-certificate BFS over every strict rank-four Whitehead reduction from the length-18 qWD words fanned out without a clean result, despite the already verified greedy certificates.
- [WORKS] Once a complete strict descent and endpoint minimality replay exists, keep its 12/13 small steps. Improve presentation only with bounded beam search or structural algebra, never an unrestricted all-state BFS.

### 2026-07-26 Compare cyclic Whitehead witnesses canonically

- [TRAP] The D-tail replay compared a canonical per-step word with a deliberately chosen human-readable cyclic orientation of the same terminal word, so the literal assertion failed although all six pairs were cyclically equivalent.
- [WORKS] Compare descent outputs with `canonical_relator(displayed_terminal)`; compute the undirected Whitehead graph on the displayed orientation, which is invariant under cyclic rotation and inversion.

### 2026-07-26 Replay advisory endpoint coordinates literally

- [TRAP] A read-only endpoint derivation reported the negative rank-two coordinate as `x -> X, y -> Y` and identified the post-factor pair literally with the old compression pair. Full-tuple replay found the exact coordinate is `x -> X, y -> YXX`, and the post-factor pair meets the old corridor only after both are mapped to the same floor-14 Aut representative.
- [WORKS] Treat agent/advisor word formulas as hypotheses: substitute them into every survivor, verify explicit inverses, and compare exact canonical outputs before writing a theorem.

### 2026-07-26 Use the uv Python for modern test syntax

- [TRAP] Importing a replay under the macOS system Python failed on `zip(..., strict=True)` because that interpreter predates the argument, even though the pytest environment uses Python 3.14.
- [WORKS] Run inline probes for new test modules through `UV_CACHE_DIR=.scratch/uv-cache uv run --with pytest python3`, matching the focused test interpreter.

### 2026-07-26 Display changed-source manufacture before deletion

- [TRAP] The first D-power-tail draft proved the primitive pair and its quotient but began from `(A,W,D,Q_k)` without displaying how the literal checkpoint reaches that tuple while restoring the carrier rows.
- [WORKS] Before every changed-source deletion theorem, give the exact AC1--AC3 manufacture from the prior checkpoint, including inversions and restoration of every source carrier; only then invoke stable ambient straightening.

### 2026-07-26 Propagate individual nonprimitivity to pair gates

- [TRAP] The live lead proposed an 18-case primitive-pair census using six source rows already proved nonprimitive. This is logically redundant: every component of a primitive pair is individually primitive.
- [WORKS] As soon as a relator is proved nonprimitive, exclude every direct primitive pair containing that unchanged row. The next genuine pair gate must first change a row by AC2 multiplication, with AC1/AC3 used only for normalization.

### 2026-07-26 Keep new ignored proofs out of normal multi-file staging

- [TRAP] A normal multi-file `git add` included a new file under ignored `literature/`; Git staged the other paths but exited 1 on the ignored proof, leaving a misleading partially successful command.
- [WORKS] Stage normal and already tracked files first, then force-add each new ignored proof in its own command and inspect `git status --short` before committing.

### 2026-07-26 Separate literal orientation counts from symmetry quotients

- [TRAP] The one-edge census expected 25,984 literal moves while its stated enumeration had already quotiented target inversion, so the first replay correctly produced only 12,992 representatives. An advisory unchanged-pair floor of 18 also failed complete Whitehead descent, which independently gives 16.
- [WORKS] Report the full oriented count and the symmetry-reduced count separately, prove the factor-two target-inversion symmetry, and replay every advisory Whitehead minimum with an independent reducer before putting it in a theorem.

### 2026-07-26 Do not identify cyclic rotation with arbitrary AC3 traffic

- [TRAP] The first Result 49 draft called a finite signed-rotation census all AC1--AC3 realizations and called its changed-row-first sequential branches every primitive deletion. An arbitrary relative conjugator gives \(TuSu^{-1}\), an infinite family, and an unchanged primitive survivor may be deleted first.
- [WORKS] Name finite cyclic-representative strata literally. Put arbitrary relative conjugators, alternate deletion orders, and changed-nonprimitive-first histories in the boundary unless the replay transports those cases explicitly.

### 2026-07-26 Summarize large positive word families before printing

- [TRAP] An exploratory carrier-edge probe printed all 186 primitive A--W child words and their per-direction multiplicities, producing thousands of noisy tokens when only the four exceptional W--D words were needed.
- [WORKS] Print counts and short exceptional families first; for a large symbolic family such as the unique-z A--W class, suppress the member list and verify its structural criterion separately.

### 2026-07-26 Cache exhaustive theorem classifiers across tests

- [SUPERSEDED] The initial diagnosis attributed the 80-second carrier replay to three uncached calls. The inner Whitehead cache already made later calls cheap; a fresh cached full replay still takes about 78 seconds for its first exhaustive pass.
- [WORKS] Keep `@lru_cache(maxsize=1)` so separate assertions do not repeat enumeration, but budget about three minutes for the strengthened carrier subset and more than three minutes for combined Results 46--50. Optimize the first pass only with a separately verified structural gate, never by assuming the decorator removes its cost.

### 2026-07-26 Split structural proof upgrades from footer renumbering

- [TRAP] A patch that replaced the carrier-cancellation proof and simultaneously renumbered its distant verifier bullet was rejected as one large context match.
- [WORKS] Upgrade the algebraic block in short equation-local hunks first, then patch references and verifier bullets separately after reading the new numbering.

### 2026-07-26 Anchor repeated classifier blocks by function

- [TRAP] A patch anchored only on `primitive_children = {` matched the earlier Result 49 classifier and inserted Result 50 histogram variables after an unreachable return. Syntax compilation passed, but the carrier classifier would have raised `NameError`.
- [WORKS] When one test module contains parallel classifiers, include the target function signature or a unique nearby variable in every patch context, then read the definition site and run the exact new assertion before staging.

### 2026-07-26 Distinguish multiplication from multiplication by a conjugate

- [TRAP] The first unchanged-primitive-first proof called \(T\mapsto TcS^\epsilon c^{-1}\) one ordinary relator multiplication. It is classically AC-equivalent but generally needs source inversion, source conjugation, multiplication, and restoration.
- [WORKS] Describe a relative product as a multiplication by a conjugate and display the finite classical AC sequence; reserve “one relator multiplication” for the literal \(T\mapsto TS^{\pm1}\) move.

### 2026-07-26 Derive reverse-target straighteners independently

- [TRAP] The first z-free A--W design reused the W-target normal form \(Az^{-1}CV\) for the reverse A-target word. The two directions share only their post-deletion shadow; before deletion, A-target needs sign-dependent coordinates and \(u\mapsto u^{-1}\).
- [WORKS] For a claimed target-direction duality, substitute both literal changed rows through separate full-tuple straighteners and compare every survivor after deletion. Do not infer a common pre-deletion coordinate from a common quotient formula.

### 2026-07-26 Normalize axes after the chosen basis change

- [TRAP] In a relative product \(UcVc^{-1}\), the written c is not generally the shortest bridge between factor axes, and an ambient automorphism need not preserve axis intersection in the original Cayley metric.
- [WORKS] Apply the row-specific automorphism first, cyclically reduce both factors, absorb their reduction prefixes into the transformed conjugator, and then take shortest-axis-bridge normal form in that transformed basis. State separately whether the normalized bridge is empty.

### 2026-07-26 Do not lift quotient primitivity to a based pair

- [TRAP] The first D-then-Q draft treated a Q-row that becomes primitive only after D deletion as a based primitive pair with D. Complete rank-four pair descent disproves that lift.
- [WORKS] For sequential deletion, prove equality of the relevant normal closures and reuse a valid fixed quotient coordinate; never infer simultaneous based-pair primitivity from primitivity in the first quotient.

### 2026-07-26 Quotient bridge automata before exhaustive expansion

- [TRAP] A direct W--D bridge-edge automaton expanded more than 230,000 states for one exceptional cut because it retained every accumulated Whitehead edge set, even though the goal was only to decide whether accepting cycles exist.
- [WORKS] First test for pumpable accepting states on a symmetry-reduced exceptional cut and derive a symbolic cycle witness. Only build a full automaton after minimizing states by the cut partition or other proof-relevant invariant.

### 2026-07-26 Count every generator in hand-written exponent fixtures

- [TRAP] The first Fox-sieve fixture labeled `qzxTZQ` abelianization-zero even though its x- and t-exponent sums are \(+1\) and \(-1\).
- [WORKS] Construct zero-abelianization fixtures from an explicit word and its balancing letters, then assert all four computed coordinates rather than trusting a visual cancellation.

### 2026-07-26 Close both signs in exponential Diophantine bounds

- [TRAP] The first A--D Fox proof asserted \(\lvert4^{k-1}-3^k\rvert>1\) after ruling out only the value \(+1\); the value \(-1\) needed a separate congruence/factorization argument.
- [WORKS] Whenever a prime-divisor proof uses an absolute lower bound, audit both exceptional equations \(M=+1\) and \(M=-1\). If the obstruction is stated for arbitrary quotient rings, prove the relevant small integers are units rather than discussing only fields of exceptional characteristic.

### 2026-07-26 Split distant theory-index patches

- [TRAP] A single patch tried to insert a new result section and update a distant live-lead paragraph; one context mismatch rejected both otherwise independent edits.
- [WORKS] Patch a theory index one local section at a time, then update plan checkboxes separately so a distant wording change cannot discard completed content.

### 2026-07-26 Cap exploratory automorphism images

- [TRAP] An unconstrained random Nielsen walk made basis images grow until even free reduction stalled; a bounded residual-conjugator scan likewise spent minutes repeating exact Whitehead descent on thousands of graph-positive words.
- [WORKS] Reset random automorphism walks at a fixed image-length cap. For residual-language discovery, canonicalize and deduplicate children before exact descent, print each completed length with flushing, and never treat a bounded scan as a theorem.

### 2026-07-26 Zero winding does not preserve primitive retractions

- [TRAP] A proposed shortcut claimed that a primitive word with zero z-exponent must retract to a primitive or trivial word after \(z\mapsto1\). A bounded Nielsen construction produced a primitive counterexample whose rank-two retraction is nonprimitive.
- [WORKS] Zero winding makes a primitive word primitive in the infinite cyclic-cover kernel, but says nothing this strong about the base retraction. Use Schreier/Fox data in the cover rather than collapsing every z-level.

### 2026-07-27 Keep escalated Git checkpoints atomic

- [TRAP] Chaining `git add`, `git commit`, and `git push` in one escalated command caused the approval review to time out and obscured which permission prefix applied.
- [WORKS] Run staging, commit, and push as separate escalated calls with the matching narrow prefix and inspect staged state before the commit.

### 2026-07-27 Replay Fox rows before applying module relations

- [TRAP] The first \(BS(3,4)\) four-state verifier wrote down already-cancelled module residuals without constructing \(\nabla A+\sigma g\nabla D\), so changes to the Fox row, coordinate order, or left \(g\)-factor could not make the test fail.
- [WORKS] Build every tested residual from the independently computed Fox rows, then apply the proposed module rewrite rules. A proof replay must fail when its upstream algebra changes.

### 2026-07-27 Finite \(BS(3,4)\) quotients erase the index gap

- [TRAP] A planned finite-quotient module scan could not expose the \(3\)-versus-\(4\) HNN asymmetry: in every finite quotient, conjugacy of \(x^3\) and \(x^4\) forces \(\gcd(|x|,12)=1\), so \(vt^4=v\) already implies \(vt=v\).
- [WORKS] Prove order-spectrum compatibility before scanning finite HNN quotients. Any residual A--D obstruction that uses the Baumslag--Solitar index gap must use an infinite quotient or infinite-dimensional module.

### 2026-07-27 Check ignored proof whitespace after force-add

- [TRAP] `git diff --check` did not inspect a new ignored proof file before it was force-added, so a trailing space survived the first verification pass.
- [WORKS] Force-add each requested ignored proof before the final audit, then run both `git diff --check` and `git diff --cached --check`.

### 2026-07-27 Relative endpoint multiplication can hide torsion

- [TRAP] For \(u\in A*C\), infinite order of \(u\) does not imply that \(A\) and \(u\) generate \(A*\langle u\rangle\). In \(C_2*C_2=\langle a,c\mid a^2,c^2\rangle\), the element \(u=ac\) has infinite order but \(aua=u^{-1}\), so a nontrivial relative word dies.
- [WORKS] Remove the optional initial and final \(A\)-syllables by the relative Nielsen map \(s\mapsto a_0sa_1\). The correct rank-one criterion is infinite order of the resulting \(C\)-ended core, not infinite order of the original element. Only specialize this to \(u\notin A\) after proving the whole ambient free product torsion-free.

### 2026-07-27 Checkpoint global tree recurrences before editing

- [TRAP] The first noncanonical \(BS(3,4)\) flow subtask stayed active through repeated waits without returning the requested early checkpoint or producing an edit. A global double-coset recurrence can absorb an unbounded amount of silent analysis.
- [WORKS] Split this attack at the exact component reduction: first return and review the subgroup \(K_b=\langle H,b^{-1}Cb\rangle\) and the induced scalar equations, then launch a separate task for existence or collapse. Interrupt after two empty post-checkpoint waits and preserve the already reviewed local-flow theorem.

### 2026-07-27 Audit sibling contributors in tree leaf arguments

- [TRAP] The first leaf-elimination proof treated an outward incoming predecessor \(p\) as visible only to the leaf relation \(A_v\). The unique interior predecessor \(w_0\) can also reach one such \(p\) through its fixed-turn relation \(B_{w_0}\), using \(v\) as their common successor.
- [WORKS] In a directed Bass--Serre leaf argument, classify center, parent, and every sibling-turn contributor separately. Here at least three incoming predecessors point outward, and excluding the single target \(\rho_v^{-r}(w_0)\) leaves at least two genuinely unique witnesses.

### 2026-07-27 Normalize both endpoints of HNN double cosets

- [TRAP] Reducing the initial exponent modulo the left subgroup and deleting the final base coefficient does not make a unique double-coset code. Right-end carries can change internal turns; for example \(Cy^2H=CyxyH\).
- [WORKS] Parameterize \(C\backslash B/H\) by fixed-transversal Britton codes modulo the deterministic endpoint-carry maps \(T_m\). Audit carry-induced turn changes before claiming an individual code is canonical.

### 2026-07-27 Replace colliding leaf markers by macro ports

- [TRAP] In the general scalar system, every (37) target is also the \(i=0\) target of (36) at an adjacent center, and dually for (36). A target outside a lifted coefficient hull therefore need not have a unique coefficient.
- [WORKS] When the internal stencil is a nonzero turn in an amalgam fiber, prove two local interpolation lemmas (prescribed vertex value and prescribed block sum), then glue fibers across the second HNN tree. One macro edge imposes one port datum, so tree recursion avoids the cross-collision without claiming coordinate uniqueness.

### 2026-07-27 Preserve LaTeX escapes in scripted patches

- [TRAP] Passing a LaTeX-heavy patch through an ordinary JavaScript template string converted backslash escapes and inserted NUL bytes before commands such as \(\sigma\); the first read-back exposed corrupted inline math.
- [WORKS] Use a raw JavaScript string for every LaTeX-heavy apply-patch payload, then immediately read back the edited section and scan the diff before mathematical review.

### 2026-07-27 Saturate cyclic fold labels before counting ports

- [TRAP] Reading \(K_b=\langle x,z^3\rangle\) directly from \(b^{-1}Cb\) initially missed the additional relation \(z^4=x^4\in H\); together \(z^3,z^4\in K_b\) force \(z\in K_b\), changing a three-port stencil into a one-port stencil.
- [WORKS] Before declaring a stencil fold index, collect every available power of its cyclic endpoint generator and replace the exponent set by its gcd saturation. Only count ports after this subgroup closure.

### 2026-07-27 Keep small proof-graph checks dependency-free

- [TRAP] A one-line Whitehead-graph audit imported NetworkX, which is not installed in this proof worktree, and failed before producing any evidence.
- [WORKS] For finite proof graphs, compute adjacency, connectivity, and articulation vertices with the Python standard library; reserve optional graph packages for project code that declares them.

### 2026-07-27 Keep diagnostic scripts readable

- [TRAP] Compressing the dependency-free articulation check into a side-effect-heavy Python comprehension produced a NameError and no evidence.
- [WORKS] Put even small graph traversals in a readable multiline standard-library script with named adjacency and connectivity functions; proof diagnostics should optimize for auditability, not one-line brevity.
- [TRAP] The readable retry still printed a hardcoded connected-true guard even though its adjacency list visibly had two components.
- [WORKS] Compute the baseline component count explicitly and define an articulation vertex by an increase from that count; never infer articulation points from a graph that was not first verified connected.

### 2026-07-27 Keep multi-file patches syntactically independent

- [TRAP] A two-file LaTeX patch failed as a whole because one line in the second file lacked its diff prefix, discarding a valid first-file section.
- [WORKS] Apply and read back each proof-file insertion separately; only combine files after each hunk has independently passed patch parsing.

### 2026-07-27 Reuse live reviewers before opening another task

- [TRAP] A follow-up review request hit the agent-thread limit while two long aggregate attacks and their inherited review threads were still live.
- [WORKS] Check the live-agent tree before dispatching another review; finish or interrupt a redundant live attack, then reuse an existing reviewer instead of adding a sibling thread.

### 2026-07-27 Use fixed-string searches for LaTeX fragments

- [TRAP] A combined ripgrep regex for LaTeX fragments with braces treated them as repetition syntax and failed before searching.
- [WORKS] Search LaTeX literals with separate fixed-string queries, or escape every regex metacharacter and test one term before combining patterns.

### 2026-07-27 Avoid literal backticks inside raw patch templates

- [TRAP] A JavaScript raw-template patch contained Markdown backticks, which terminated the template and caused a syntax error before the patch ran.
- [WORKS] Omit Markdown backticks from raw patch payload text or use a safely quoted construction that cannot terminate on documentation punctuation.

### 2026-07-27 Run Whitehead diagnostics with the proof dependencies

- [TRAP] Importing rank3_whitehead.py with the system Python failed at acmoves.py because numba is absent from this proof worktree.
- [WORKS] Run isolated Whitehead diagnostics with uv and explicit numba and numpy dependencies, matching the established verifier environment.
- [TRAP] The reducer accepts an arbitrary generators tuple at its public boundary, but its imported free-reduction and cyclic-canonicalization helpers validate only x, y, z, and t; adding q therefore fails before Whitehead reduction. The primitivity predicate also accepts the completed reduction object, not the source word and basis.
- [WORKS] For rank-four diagnostics, use an independently checked alphabet-generic reducer or first generalize and test the shared helpers; do not infer rank-four support from the public tuple alone.

### 2026-07-27 Resolve truncated paths from commit statistics

- [TRAP] A truncated git-show statistics line was read as experiments/stable_ac/theory, but the committed ledger actually lives at results/stable_ac/theory; the subsequent read failed.
- [WORKS] Before opening a path shown with an ellipsis in commit statistics, recover the exact name with git show --name-only or rg --files.

### 2026-07-27 Separate theorem insertion from frontier rewrites

- [TRAP] A large one-file patch combined a new theorem insertion with a distant live-frontier replacement; changed line wrapping in the frontier made the entire patch fail atomically.
- [WORKS] Apply a self-contained theorem insertion first and read it back, then patch distant status prose in a separate hunk using freshly read context.

### 2026-07-27 Force-add proof-archive updates explicitly

- [TRAP] Staging a mixed checkpoint failed because literature is ignored, even though the edited proof ledger is already part of this proof branch.
- [WORKS] Stage ordinary tracked files normally and force-add only the exact edited literature/proofs file; never force-add the literature tree broadly.

### 2026-07-27 Read the exact summary block before replacing prose

- [TRAP] A theory-summary rewrite used remembered sentence wrapping and failed to match, even though the mathematical proof file had already been corrected.
- [WORKS] Read the exact local summary paragraph immediately before applying a prose replacement; do not reuse context copied from the longer proof ledger.

### 2026-07-27 Append theorem sections from a single terminal line

- [TRAP] Appending Section 49 with a multi-line end-of-file anchor failed even after the visible tail appeared to match exactly.
- [WORKS] When extending a rapidly growing proof ledger, anchor the append on its unique final content line; read back the new tail before making any distant summary edit.

### 2026-07-27 Avoid all-add append hunks in proof ledgers

- [TRAP] An all-add hunk for Section 51 duplicated the ledger's terminal sentence, and a LaTeX turn label beginning with a plus sign lost that sign to the unified-diff marker.
- [WORKS] Append by replacing one exact terminal line with itself plus the new section; avoid content lines that begin with a literal plus sign, or include a second plus after the diff marker and verify the rendered tail immediately.

### 2026-07-27 Use the uv Python for repository verifiers

- [TRAP] The macOS system Python 3.9.6 failed inside the Whitehead verifier at `zip(..., strict=True)` before evaluating the candidate.
- [WORKS] Run repository proof diagnostics through `UV_CACHE_DIR=.scratch/uv-cache uv run python3`; this workspace resolves Python 3.14.3 and supports the verifier's language features.

### 2026-07-27 Pass real newlines to multiline Python diagnostics

- [TRAP] Escaped `\\n` sequences inside a shell `python3 -c` argument reached Python as literal line-continuation characters and caused a SyntaxError before the cancellation audit.
- [WORKS] Put actual newline characters inside the quoted `-c` program, or reduce the diagnostic to one expression; do not double-escape program structure through both JavaScript and the shell.

### 2026-07-27 Factor primitive eliminators before solving them

- [TRAP] A diagnostic retyped the left factor of the one-q relator with the wrong y-orientation, so its computed q-substitution was unrelated to the displayed relator.
- [SUPERSEDED] The former rule incorrectly said that `L q M=1` gives `q=M^{-1}L^{-1}`; that reverses the two factors in the wrong order.

### 2026-07-27 Preserve side order when solving a unique-letter relator

- [TRAP] Solving `L q M=1` as `q=M^{-1}L^{-1}` manufactured a false AK(3) endpoint that appeared stably trivial.
- [WORKS] The exact solution is `q=L^{-1}M^{-1}`. Assert both the factorization and `free_reduce(L + q_solution + M) == ""`, then replay the solution in every survivor before analyzing later moves.

### 2026-07-27 Apply deletion to whole conjugated source factors

- [TRAP] A survivor table wrote \(H_R\) unchanged after q-deletion even though the conjugator defining \(H_R\) may contain q; the core gauge argument survived, but the displayed word was too strong.
- [WORKS] Write the survivor as \(\phi(H_R)\), observe that it is still a conjugate of the retained source, and restate explicitly which fixed words are q-free. For occurrence sieves, use parity: conjugator letters enter in inverse pairs, so a Q-bearing source makes the total q-letter count even but not necessarily only zero or two.

### 2026-07-27 State the stable-deletion hypothesis at each theorem boundary

- [TRAP] The changed-source exchange algebra used a valid unique-r substitution but initially omitted that the checkpoint must be a balanced trivial-group presentation, making the step readable as an unauthorized bare generator-relator deletion.
- [WORKS] Every primitive or unique-letter deletion theorem must state the balanced trivial-group hypothesis and name the stable substitution-and-removal composite. Use its explicit triangular substitution when claiming that unaffected generators or relators remain fixed.

### 2026-07-27 Distinguish exact basis pairs from relator conjugacy-class pairs

- [TRAP] The rank-three Whitehead pair reducer cyclically canonicalizes each word independently. Its positive result certifies a primitive pair of relator conjugacy classes, which is correct after AC3, but it cannot test whether the two displayed based elements themselves extend to one ambient basis.
- [WORKS] Before using a primitive-pair diagnostic, state whether independent conjugation is allowed. Use the cyclic Whitehead reducer for AC relator slots; use an exact Nielsen or Stallings based-subgroup test for an endomorphism or exact basis-pair claim.

### 2026-07-27 Bound exploratory Whitehead diagnostics incrementally

- [TRAP] An all-at-once rank-three conjugator census through length eight ran long enough to require interruption and produced no checkpointed partial counts.
- [WORKS] Sweep one word length at a time, print the completed level, and apply algebraic occurrence and abelianization filters before Whitehead reduction. Treat every bounded absence as diagnostic evidence only.

### 2026-07-27 Separate cyclic normalization from the Whitehead automorphism

- [TRAP] A primitive word reduced to a one-letter cyclic representative while the stored Whitehead automorphism stayed the identity; reading this as an inconsistent witness initially obscured that the source was already a conjugate of that letter.
- [WORKS] The word reducer cyclically canonicalizes before recording Whitehead descents. Recover and verify the peeled conjugating prefix separately whenever the minimum changes under free or cyclic normalization with no recorded automorphism step.

### 2026-07-27 Relabel auxiliary generators before rank-three Whitehead diagnostics

- [TRAP] `rank3_whitehead.reduce_word_fast` accepts a caller-supplied generator tuple, but its shared word validator still rejects `r/R`; a positive-bridge diagnostic failed before performing any Whitehead step.
- [WORKS] Relabel the auxiliary generator `r/R` to the repository's supported `z/Z` alphabet before calling the rank-three reducer, and pass `("x", "y", "z")`. Treat the relabeling as notation only and replay any witness after translating back.

### 2026-07-27 Do not rechoose a Cohen--Lyndon transversal

- [TRAP] Cohen--Lyndon asphericity supplies a particular transversal whose conjugates of the relator freely generate its normal closure. Replacing those representatives by convenient elements of a subgroup in the same normal-closure cosets need not preserve a free basis; independently conjugated basis elements can generate a proper subgroup.
- [WORKS] Keep the existential Cohen--Lyndon transversal fixed unless a separate Nielsen or Bass--Serre argument proves the replacement is basis-preserving. The implication `Q = K <<v>>` and `v` root-free therefore does not by itself prove `Q = K`.

### 2026-07-27 Preserve LaTeX backslashes in patch scripts

- [TRAP] A JavaScript string interpreted a LaTeX backslash sequence while adding a proof file, split a content line, and made `apply_patch` reject it as an invalid hunk.
- [WORKS] Pass LaTeX-heavy patches with a raw string so every backslash reaches `apply_patch` literally, and avoid unescaped backticks inside the raw template. Read the rendered equations back from disk.

### 2026-07-27 Match verifier helpers to the word alphabet

- [TRAP] A regression test reused the compression-root abelianization helper, which counts x and z, on the original AK words in x and y; every y-exponent was silently reported as zero.
- [TRAP] The first repair changed the earlier x-z test because the patch matched the first identical assertion, while leaving the new x-y test unchanged.
- [WORKS] Name basis-specific word invariants explicitly and add a separate helper when a proof changes alphabets. Pin the expected exponent vector before trusting a cyclic-length comparison.
- [WORKS] When two tests contain the same assertion spelling, anchor each replacement on its function name and verify both call sites before rerunning.

### 2026-07-27 Re-read theorem endpoints before ledger insertion

- [TRAP] A Result 117 insertion used a remembered terminal sentence from Result 116 and failed because the actual ledger ended with a more specific r-slot sentence.
- [WORKS] Read the exact final paragraph and anchor a new numbered result on the following heading, not on remembered prose from an earlier draft.

### 2026-07-27 Stress-test rigidity with conjugating endomorphisms

- [TRAP] Two simultaneous proper torus-quotient embeddings, first-homology isomorphisms, normal generation, and even a primitive syllable-six realization looked close to forcing the old free factor onto, but the proper map x -> x, y -> y[x,y] satisfies all of them.
- [WORKS] Before promoting a package of relative one-relator conditions to rigidity, test x -> x, y -> gyg^-1. Klyachko injects every root-free coefficient quotient because the defining relative equation has y-exponent one; the exact marked AC source factorization may be the only remaining information.

### 2026-07-27 Resolve focused regression paths from the checkout

- [TRAP] A focused proof-regression command used remembered descriptive filenames for Results 114--117; several results share older verifier files instead of having one test module per theorem, so collection stopped at the first nonexistent path.
- [WORKS] Build focused test commands from `rg --files tests/stable_ac` and the committed file lists, never from theorem titles or remembered names.

### 2026-07-27 Keep word diagnostics dependency-free

- [TRAP] Importing `experiments.stable_ac.rank3_compression.one_edge` solely for cyclic reduction also imports `numba`; the system Python failed before the intended word calculation.
- [WORKS] For disposable theory diagnostics, implement the few-line free/cyclic reduction locally or use the verified `uv` environment. Do not import a broad experiment module for a basic word operation.

### 2026-07-27 Do not use a reverse triangle inequality for cyclic length

- [TRAP] The proposed family-wide corridor barrier used `min_h ||P hQh^-1|| >= ||P|-|Q||`. This is false: after the shorter factor cancels, cyclic reduction can expose and cancel more of the longer factor. For example, cyclically reduced `P=abaB`, `Q=A` have lengths 4 and 1, but a suitable rotated product cyclically reduces to `b` of length 1.
- [WORKS] Bound products of conjugacy classes through the exact two-seam rotation/common-factor calculation or a proved Stallings bounded-cancellation lemma specific to the words. Raw cyclic lengths alone supply no reverse triangle inequality.

### 2026-07-27 Use raw patch strings for every LaTeX insertion

- [TRAP] A regular JavaScript patch string dropped the backslash from `\\quad` in equation (9.5), repeating the already documented LaTeX-escape class of failure.
- [TRAP] A subsequent raw template failed to parse because the lesson text itself contained unescaped backticks.
- [WORKS] Use `String.raw` for LaTeX-only patch payloads and a separate regular string for prose containing backticks. Search the edited region for bare command names before verification.

### 2026-07-27 Patch audited proof corrections in small anchors

- [TRAP] A multi-file audit correction failed atomically because its final hunk matched a remembered line break instead of the committed Section 14 wording; a second combined raw patch failed because lesson prose contained backticks.
- [WORKS] After an audit, reread the exact theorem region and split structural lemma insertion, theorem wording, and lesson updates into separately anchored patch payloads.

### 2026-07-27 Adjacent axis overlaps do not control long products

- [TRAP] The proposed Result 129 summed pairwise adjacent overlap bounds through an arbitrary cyclic product. The four leaves `u`, `v`, `u^-1`, `u v^-1 u^-1` can have distinct adjacent K-tags and still multiply to 1: cancellation passes through a conjugator bridge and exposes a new seam.
- [SUPERSEDED] The initial response incorrectly retained a three-axis version of the seam lemma; a legal two-AC2 history refutes it too.
- [TRAP] With `u=a` and `v=yby^-1`, a legal two-AC2 history produces `uv^-1uvu^-1`, cyclically conjugate to `v^-1uv`, even though its three inherited source tags are pairwise distinct and their axes have overlap at most two.
- [WORKS] Axis-overlap bounds are safe for the two-factor product estimates used through Result 127. For three or more history-derived leaves, fold the whole based history word including conjugator bridges; never sum source-axis seam bounds in isolation.
- [WORKS] Replay a cancellation counterexample as an exact AC history before discarding the branch. Here the failure exposed the universal row-braid self-loop `(u,v) -> (v^-1uv,uvu^-1)`, whose formal map is proper but whose evaluated rows remain individually conjugate.
- [WORKS] A proper injective row-symbol map can produce strict descending displayed-relator subgroups inside one classical AC class. Never use subgroup descent alone as evidence of progress; also track the evaluated relator conjugacy classes.

### 2026-07-27 Replace long-product geometry by source-leaf quotients

- [WORKS] Under AC1--AC3, track each row as a product of conjugates of signed source leaves. At fixed AC2 depth this gives finitely many signed multisets even though every conjugator is arbitrary.
- [WORKS] In rank two, primitivity fixes the signed Christoffel conjugacy class from the exponent vector. A finite quotient can then exclude all conjugators at once by separating that class from the required product of source conjugacy classes; the depth-two AK and first-image certificates reduce to cycle types in `S4` and `S5`.
- [TRAP] Quotients through degree five closed all six signed cases for the fixed first image but only two cases uniformly over every conjugating embedding. Do not extrapolate the fixed-image theorem to all `phi_g` or all corridor depths.
- [TRAP] A disposable quotient diagnostic used a mutable `set` as a dictionary key and failed with `TypeError: unhashable type: 'set'`. Keep subgroup-dependent caches local to the subgroup or key them by a `frozenset`.

### 2026-07-27 Kill the majority provenance source

- [WORKS] At fixed AC2 depth, quotient by the majority source relator before testing a primitive Christoffel candidate. For AK depth three, the central quotients `A=1 -> C3*C4` and `B=1 -> C2*C3` leave only one or two minority conjugates and close all eighteen new provenance multisets.
- [WORKS] In a free product Bass--Serre tree, normalize a product of two hyperbolic conjugacy classes to syllable rotations joined by a connector. Intersecting axes need connector length at most one; disjoint axes at vertex distance `D` need at most `D+1`, and the product translation length determines `D`.
- [TRAP] Full symmetric-group class products saturated at depth three, and a subgroup-sensitive exhaustive `S5` pass ran too long and had to be interrupted. Prefer the infinite virtually free quotient and its finite axis-connector normal form before broadening a finite-group loop.
- [TRAP] A large `String.raw` proof patch again contained a Markdown backtick and failed with `SyntaxError: Unexpected identifier 'tests'`. Before sending any raw template patch, search the payload itself for backticks; write code paths as LaTeX `texttt` or patch that prose separately.

### 2026-07-27 Preserve dependent provenance in the last quotient residue

- [TRAP] To lift `C3*C4` through the first stable image, an unnecessary diagnostic searched for `phi(y)=Y`. The needed fact is only that `phi(y)` is conjugate to `y`, so the torsion relation `y^4=1` already kills `phi(A)`.
- [WORKS] The same quotients give `phi(A)=1, |phi(B)|_syl=18` in `C3*C4` and `phi(B)=1, |phi(A)|_syl=2` in `C2*C3`. Combined with one `S5` certificate, they close seventeen of eighteen first-image depth-three provenance classes.
- [WORKS] Do not flatten the last class beyond its shared subexpressions. Its exact normal form is `X=u^s h0 v^t h0^-1`, `Y=v^-1 h1 X h1^-1`, `Z=X^-1 h2 Y h2^-1`; the identical `X` and `Y` occurrences are the remaining structure to exploit.
- [TRAP] Symmetric quotients through degree six, small `SL(2,p)` quotients through `p=7`, and conjugators of free length at most three did not resolve the final equation. These bounded failures are lead diagnostics only, never proof evidence.

### 2026-07-27 Nilpotent quotients erase braid separation

- [WORKS] In any nilpotent group, `rsr=srs` implies `r=s`: abelianization gives the base case, and centrality of `gamma_n/gamma_{n+1}` advances `rs^-1` through the lower central series.
- [WORKS] For the last first-image depth-three residue, `b=1` makes `x=phi(y)` in every nilpotent quotient. Since `phi(y)=(yx)y(yx)^-1`, this makes `a=x^-1` and explicitly writes `yx^-1` as a conjugate of `a^-1 (yx) a (yx)^-1`.
- [TRAP] Do not spend more searches on nilpotent or finite p-group quotients for this residue. They uniformly realize the projected commutator; the next invariant must retain non-nilpotent braid information.

### 2026-07-27 Rewrite exponent-zero residues in the cyclic cover

- [WORKS] For `G_b`, use `t=x` and `z_i=t^i y t^(-i-1)`. The Magnus rewrite of `b` contains its bottom `z_0` and top `z_4` once, giving an explicit rank-four free-by-cyclic presentation and converting the last residue into a free-group twisted-conjugacy equation.
- [WORKS] Check both directions of the monodromy by solving the shifted relator for `z_-1`; a monic top letter alone proves only an ascending presentation until the explicit inverse is verified.
- [TRAP] The ordinary Alexander module is blind here because `det(Phi_ab-I)=1`, and the full braid quotient is also blind via the half-twist that swaps the two braid generators. Do not retry invariants factoring through either quotient.
- [TRAP] The first class-two kernel diagnostic built a 10-dimensional action from only four generator columns and failed with `IndexError`. Include the six exterior-square commutator columns. The corrected mod-3 semidirect quotient admits a solution, so that bounded class-two result is diagnostic only.
- [TRAP] The first mapping-torus statement dropped the surviving sign of the fixed a-entry. The exact target is `Phi^j(z_0^eta)` with `eta=+/-1`; carry source orientation through every quotient and twisted-conjugacy reduction.
- [TRAP] A split LaTeX quantifier line left a trailing space after the comma and failed `git diff --check`. Break display lines after punctuation without padding before the newline.
- [TRAP] Explicitly generating each diagonal image subgroup attached to all 72 `S3` representation orbits stalled even though the representation-orbit classification was cheap. Do not enumerate the whole diagonal subgroup; saturate only the equation's reachable states, work one orbit at a time, and impose a hard state cap with progress output.
- [TRAP] The compact Magnus diagnostic encoded a positive `z_i` by the integer `i` and a negative `z_i^-1` by `-i-1`; the value `-1` can therefore be misread if the sign channel is discarded. A positive `y` encountered at height `-1` is `z_-1`, not `z_0^-1`. For new rewrites, store `(index, sign)` pairs or verify the final kernel word by direct semidirect multiplication.
- [TRAP] A three-file proof patch anchored the main ledger on prose whose line wrapping differed from the expected context, so the whole patch was rejected. Read the exact insertion neighborhood and patch each proof file separately when their surrounding formats differ.
- [TRAP] The first displayed expansion of `Delta x Delta^-1` retained one extra `x` after cancelling the middle `x x^-1`. Verify braid identities as freely reduced words before typesetting the intermediate equality; the correct line is `x u x u^-1 x^-1 = u x u u^-1 x^-1 = u`.

### 2026-07-27 Separate fixed commutators with compact Lie geometry

- [WORKS] After reducing a fixed-entry commutator equation to `Cl(a) intersect a Cl(c^+/-1)`, allow representations into compact Lie groups, not only finite quotients. In `SU(2)`, conjugacy fixes quaternion scalar part, and Cauchy--Schwarz can separate an entire translated conjugacy class at once.
- [WORKS] For the last first-image depth-three AK residue, choose equal-angle quaternion images of `x,y` with axis dot product an algebraic root. The braid relation becomes one scalar dot-product equation, while `scal(a)^2>1/2` and `scal(c)<0` create a strict trace gap for both orientations.
- [WORKS] The exact `SU(2)` obstruction closes the eighteenth first-image depth-three provenance class. The complete statement is in `literature/proofs/AK3_SU2_FIXED_COMMUTATOR_OBSTRUCTION.md`; keep finite and nilpotent blindness results as motivation, not as evidence for solvability.

### 2026-07-28 Disable external Python bytecode caches in scratch verification

- [TRAP] `python3 -m py_compile .scratch/depth4_provenance_check.py` tried to create a mirrored cache below `/Users/avigyapaudel/Library/Caches/com.apple.python/` and failed with `PermissionError: [Errno 1] Operation not permitted` even though the source file is project-local.
- [WORKS] Run disposable project diagnostics with `PYTHONDONTWRITEBYTECODE=1 python3 ...` in this macOS workspace, or set an explicitly project-local cache prefix before using `py_compile`.
- [TRAP] `.scratch/depth4_provenance_check.py` eagerly materializes every free-product connector up to the largest per-case bound and did not finish the 24 one/two-minority census before handoff. Stream connectors per case, prune by target length during generation, and emit progress before treating those cases as closed.
- [TRAP] An inline SU(3) Horn diagnostic wrote `else0` without whitespace in a conditional expression and failed at parse time. Run disposable research snippets through a syntax-only check or keep ternaries on separate assignments before launching a long randomized scan.
- [TRAP] The same `else999` parse error recurred in the next compact heredoc, proving the prior wording was insufficient. Do not use inline conditional expressions in disposable mathematical scans; assign the default in an explicit `if/else` block and keep one statement per line.
- [TRAP] The first depth-four checker refactor patch mixed a real comment anchor with a not-yet-present `typing` import and was rejected atomically. Introduce new imports and replace existing regions in separate exact-anchor patches.
- [TRAP] Grouping depth-four connectors by quotient and sign removed duplicate traversals but still exceeded 69 seconds because every candidate was fully cyclically reduced. While scanning a raw product, track monotone syllable loss and abandon it as soon as its maximum possible final length is below every active target length.
- [TRAP] A depth-four metric experiment treated signature entries `(c_A,c_B)` as the primitive target exponent vector. They are signed source coefficients; always derive the actual vector as `(p,q)=(3*c_A+c_B,-4*c_A-c_B)` and assert it against the handoff table before evaluating a Christoffel target.
- [TRAP] A large corrective patch to `literature/proofs/AK3_DEPTH4_BIINVARIANT_METRIC_OBSTRUCTION.md` failed atomically because one prose anchor differed (`Four choices suffice`). For proof rewrites after a conceptual correction, inspect the complete current file and apply small section-local patches so no stale claim survives unnoticed.
- [TRAP] A JavaScript `String.raw` wrapper for a Markdown proof failed before `apply_patch` because Markdown backticks terminated the template literal. When using a raw template for LaTeX-heavy patches, omit Markdown backticks/code fences or escape the JavaScript delimiter before the tool call.
- [TRAP] `experiments/stable_ac/depth4_three_class_certificates.py` passed when imported by pytest but failed when replayed as a file because `from experiments...` cannot resolve from the script directory. Replayable certificate scripts must not depend on repository-root package imports; keep their small exact word helper local or explicitly support both invocation modes.
- [TRAP] The same certificate passed under `uv` Python 3.14 but direct workspace `python3` eagerly evaluated `int | Fraction` and failed. Start standalone certificate modules with `from __future__ import annotations` and verify both the pytest runtime and the documented direct replay command.
- [TRAP] A second large LaTeX-heavy handoff replacement failed because JavaScript string escaping stripped backslashes from patch anchors. Update proof handoffs in small prose/hash/list patches; reserve `String.raw` for additions without Markdown backtick delimiters.
- [TRAP] Naively nesting all four free conjugators through length three in the final depth-four dependency equation required (53^4) word reductions and was interrupted after several minutes. Search the last conjugator by conjugacy/centralizer normal form or use meet-in-the-middle state sets; the exact length-two census (83,521 states) is the largest acceptable direct fourfold loop.
- [TRAP] Simulated annealing on the four dependency conjugators spent minutes improving cyclic output length only from 39 to 17 and supplied no certificate. Do not extend heuristic search budgets after a plateau; switch to the target-basis cancellation theorem or an exact free-group equation algorithm.
- [WORKS] For the 24 depth-four one/two-minority certificates, a connector product of raw length `R` reaching target length `T` must retain an unchanged connector block of length at least `k-(R-T)`. Pruning DFS prefixes that cannot extend such a cyclic target subword reduced the exact focused test to seconds; where the prune is nonvacuous, check `R-T<L` so a source word cannot vanish and expose an unmodeled internal seam.
- [TRAP] Staging the tracked `.scratch/depth4_provenance_check.py` together with ordinary files returned exit 1 and an ignored-path warning even though `git status --short` showed all three requested files staged. Inspect the index after this warning before retrying; use `git add -f` only if the exact scratch path is still unstaged.
