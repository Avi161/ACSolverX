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
