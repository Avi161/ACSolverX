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

- [TRAP] A single ordinary `git add` that includes any path under the ignored `literature/` tree aborts the whole staging command, even when another proof file there is already tracked.
- [WORKS] Stage the exact intended `literature/proofs/...` paths with `git add -f`; stage non-ignored report, test, and lesson files separately, then inspect the cached diff before committing.

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
