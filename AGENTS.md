# Lessons Learned

### 2026-08-16 Universal versus computable AC bounds

[TRAP] When asked for the most powerful rigorous stable-AC supermove, do not silently require its move bound to be computable. Lemma 11 guarantees termination on every valid instance, so a machine-model-explicit Busy-Beaver bound is a universal rigorous bound even though it cannot be numerically evaluated. State computability as a separate property and optimize for the domain the user requested.

### 2026-08-16 Stable equivalence is not endpoint novelty

[TRAP] Do not call a stable-AC supermove useful merely because it has a universal equivalence bound. Require its accepted target family to contain states outside the source relator tuple's `Aut(F_n)` orbit. For same-rank endpoints, use an exact Whitehead orbit decision (including the repository's finite relator symmetries) as an admissibility filter; automorphic targets may occur but must not exhaust the action family.

### 2026-08-16 Patch context after substantive rewrites

[TRAP] An `apply_patch` failed with `Failed to find expected lines` after the same document had been substantively rewritten. Read the current local context before composing a follow-up multi-hunk patch; do not rely on an earlier readback.

### 2026-08-16 Markdown backticks in shell checks

[TRAP] A combined `rg` verification command failed with `zsh:1: unmatched "` because a literal Markdown backtick was embedded in a double-quoted shell pattern. Use single-quoted shell regexes for Markdown syntax, or split the checks so backticks never undergo shell command-substitution parsing.

### 2026-08-16 A filter is not a new supermove

[TRAP] Wrapping the existing Lemma 11/CoV action in a non-automorphic endpoint filter does not satisfy a request for a completely new stable-AC technique. A qualifying result must have a different mathematical transformation mechanism, an explicit source-to-target constructor, and its own soundness and move-bound proof. Use Lackenby's triangulation/Pachner machinery directly rather than repackaging CoV.

### 2026-08-16 Regina version API

[TRAP] Regina 7.4.1 imports from the project-local target but does not expose `regina.__version__`; direct access raised `AttributeError`. Use `regina.versionString()` for runtime identification and introspect dimension-specific classes such as `Triangulation3` for supported operations.

### 2026-08-16 Validate triangulation-derived presentations immediately

[TRAP] A prototype interpreted `Triangle3.edgeMapping()` values as triangle-local vertex indices on a self-identified triangulation and produced a singular exponent-sum matrix for an alleged presentation of the trivial group. For every `P(T,X,X')` constructor, validate balance and determinant `±1` before running orbit analysis, and confirm the exact Regina face-mapping convention from its documentation. Reject all examples generated before those gates pass.

### 2026-08-16 Compute macro bounds from certificates

[TRAP] The first witnessed-ACM test hard-coded an expected atomic cost of 14, while exact replay contained 13 moves. Derive macro costs directly from the certificate fields and assert equality with the independently expanded atomic path; never calculate a public bound through dummy presentations or hand-counted examples.

### 2026-08-16 Cross-worktree Python package masking

[TRAP] Adding a second worktree to `PYTHONPATH` caused its regular `experiments` package to mask the current workspace's namespace package, hiding a newly added module. For cross-worktree audits, import the current module first, then extend `experiments.__path__` only for the independent checker package; do not put both project roots on `PYTHONPATH` and assume left-to-right namespace merging.

### 2026-08-16 Beam deduplication is not bounded completeness

[TRAP] The first witnessed-ACM generator called `beam_size=None` exhaustive while still deduplicating intermediate prefixes by cyclic key; an independent advisor produced a width-two target lost by that pruning. Exhaustive bounded enumeration must iterate every factor tuple and deduplicate only final endpoints. Also cyclically reduce before computing cyclic keys, and state explicitly when source conjugators are represented only modulo final relator conjugacy.

### 2026-08-16 Final-audit grep repeated backtick expansion

[TRAP] A final `rg` readback repeated the already-recorded zsh backtick-expansion failure because the whole pattern was double-quoted. For every shell search of Markdown, use one single-quoted pattern per `rg -e` argument; treat this as a mechanical audit rule, not a reminder to remember case-by-case.

### 2026-08-16 A replayable AC batch is not Lemma-11-like

[TRAP] The witnessed ACM family was called a genuine Lemma-11-like supermove even though its certificate explicitly expands to a short, input-visible AC1--AC3 path. Multiple conjugated relator products are just sequential Two-Hump/S-moves bundled into one action. A qualifying Lemma-11-like mechanism must provide structural leverage not already priced by its naive local replay—such as generator elimination with a hidden normal-area step—and must demonstrate a length/search advantage beyond ordinary substitution moves.

### 2026-08-16 Coordinate images can vanish under cyclic reduction

[TRAP] The first coordinate-endomorphism test expected the proper word `yxyXY` to remain as a one-letter relator image, but it is conjugate to `y` and cyclically reduces back to `y`; a separate negative-exponent fixture was also miscounted. Distinguish the raw substituted word from its cyclic relator representative, compute exponent sums mechanically, and test non-automorphic effects only on relators where the coordinate word occurs in non-conjugacy-trivial context.

### 2026-08-16 Specialization is not a quotient certificate

[TRAP] The first quotient-isolator census called a syntactic specialization check a verified quotient identity even for a toy presentation of `C2`. Killing every old generator proves the quotient equality only when the old relators are separately certified to normally generate the old free group. Carry trusted trivial-presentation provenance or explicit normal-closure witnesses in every artifact, and call an unchecked erasure only a specialization. Describe hidden replay cost as witness-dependent with no effective bound supplied by the proof; do not claim literal unboundedness without a lower-bound family.

### 2026-08-16 Template bounds must reach source length

[TRAP] The first two-stabilization scan used defining words of length one and templates of length at most five against cyclically reduced source relators of length at least six. It therefore accepted no source identities and spent time proving only that the encoding bound was vacuous. Before launching a corridor census, check the minimum possible expanded-template length against every source relator; when exhaustive template growth is exponential, generate templates directly from certified source factorizations instead.

### 2026-08-16 Filter repeated-block corridors before replay

[TRAP] Enumerating every repeated two-block factorization of `aca_99` before fixing the source relator and one defining word repeatedly exceeded two minutes, even though the exact `z=yy` question on the relevant relator finishes in seconds. Repeated-block tokenizations grow exponentially on long powers. Constrain the source index, cyclic orientation, and known defining word first; only then derive rank-three tuples or run Whitehead minimization.

### 2026-08-16 New supermoves may compose Lemma 11 [SUPERSEDED]

[SUPERSEDED] The advisor gate was temporarily relaxed to permit a logical macro whose proof composes Lemma 11. The user subsequently rejected AMEC specifically because this admitted naive double CoV; follow the stricter later lesson instead.

### 2026-08-16 Run project tests through the selected Python

[TRAP] Invoking the temporary `pytest` console script under `uv run` omitted the repository root from `sys.path`, so namespace imports failed even though the code was present. [WORKS] Use `uv run ... python -m pytest`; the selected interpreter then places the working directory on the import path. For this workspace include the already-cached `pytest` and `numba` environments when the independent checker imports NumPy/Numba utilities.

### 2026-08-16 Inspect local word-algebra APIs before scripting

[TRAP] Two quick Whitehead-audit scripts failed because the module was mistyped as `autocon` and the inverse helper was guessed as `inverse` although `experiments/equivalence_classes/lib/words.py` exports `autcanon` and `inv`. Read the relevant module header or use `rg '^def '` before writing an ad-hoc verifier; do not guess repository-local import names.

### 2026-08-16 Sequential CoV is not an out-of-the-box supermove

[TRAP] AMEC was accepted under an overly relaxed reading even though its rank-two action is exactly two CoV/Lemma-11 corridors executed sequentially. The user's standard is stricter: reject double CoV, repeated Lemma 11, visible AC/substitution batching, and any macro whose claimed novelty vanishes when expanded. Require a direct theorem-level mechanism genuinely different from CoV/Lemma 11, then certify a non-automorphic endpoint on the 124 corpus and a non-obvious rigorous bound.

### 2026-08-16 Non-automorphic hit rate may be low

[WORKS] A genuinely new supermove family may yield mostly automorphic branches; even a one-percent non-automorphic hit rate is acceptable because exact orbit filtering can discard the rest. Do not require most outputs to escape `Aut(F_n)`. Require only that the mechanism is independently genuine and that at least one generated branch has a certified non-automorphic endpoint.

### 2026-08-16 Register ad-hoc importlib modules before dataclasses

[TRAP] Loading `.scratch/morse_search_port.py` with `module_from_spec` and `exec_module` under Python 3.14 failed inside `@dataclass` because the module had not been inserted into `sys.modules`. For ad-hoc filesystem imports of dataclass-bearing modules, assign `sys.modules[spec.name] = module` before `exec_module`, or import through a normal package path.

### 2026-08-16 Process inspection is sandbox-blocked

[TRAP] `ps -axo ...` failed with `operation not permitted` in the managed workspace sandbox. Do not use process-table inspection for progress checks here; inspect artifact modification times or use the agent-status tools instead.

### 2026-08-16 Bound Morse sampling before orbit canonicalization

[TRAP] A first 5,000-seed discrete-Morse scan combined full matching construction, Tietze simplification, and complete Whitehead canonicalization and overran the 30-second command window without yielding output. [WORKS] Preflight with 100--1,000 seeds, report rank/length histograms first, and use cheap Whitehead minimum-length screening before full minimal-level orbit enumeration.

### 2026-08-16 No bundled SymPy simplifier

[TRAP] The workspace Python 3.14 runtime does not include `sympy`; importing `sympy.combinatorics.fp_groups.simplify_presentation` raised `ModuleNotFoundError`. Do not plan the Morse/Tietze pipeline around SymPy without an explicit dependency installation; use the checked-in pure-Python port or the author's reference implementation for verification.

### 2026-08-16 Resolve search paths before multi-root rg

[TRAP] A broad `rg` search included a guessed root-level `ac_solver.py` path that does not exist, producing an avoidable path error alongside otherwise useful matches. Run `rg --files` first when a path is uncertain, and pass only verified directories/files to multi-root searches.

### 2026-08-16 Use the root uv cache for proof-worktree rank-three tools

[TRAP] Running the proof-worktree rank-three Whitehead module first under system Python failed because `numba` was absent; retrying from the proof worktree with a relative `.scratch/uv-cache` pointed at the wrong cache and also failed. [WORKS] Run from the project root with `PYTHONPATH=.claude/worktrees/codex-proofs UV_CACHE_DIR=.scratch/uv-cache uv run --offline --python 3.11 --with numba python ...` so both the proof package and cached dependency resolve.

### 2026-08-16 A new family needs one non-automorphic branch, not a majority

[TRAP] Do not reject a genuinely non-CoV/non-Lemma-11 theorem family merely because 90--99% of sampled outputs return to the source automorphism orbit. The user permits exact post-generation filtering and requires only that at least one rigorously certified branch is non-automorphic. Keep the two gates separate: mechanism novelty is family-level; orbit escape is witnessed by at least one exact output.

### 2026-08-16 Standalone scratch verifiers need the project root

[TRAP] Executing `.scratch/verify_aca115_morse_independent.py` directly put `.scratch/` rather than the project root on `sys.path`, so importing `experiments` failed. Standalone proof scripts under `.scratch/` must insert `Path(__file__).resolve().parents[1]` before project imports. Also keep using `UV_CACHE_DIR=.scratch/uv-cache uv run --offline --with pytest python -m pytest`; system Python still has no `pytest`.

### 2026-08-16 Time-box exploratory supermove benchmarks

[WORKS] When the user requests a mini run with a wall-clock cap, reduce scope before coding or launching: use deterministic seeds, tiny rank-three and rank-two node budgets, an explicit deadline check, and persist partial rows. Do not let a full 60/124 census, complete orbit canonicalization, or dependency setup consume a 15-minute exploratory budget.

### 2026-08-16 Bridge every split namespace package

[TRAP] The first mini Morse runner extended only `experiments.stable_ac.__path__`; importing the proof-worktree rank-three code then failed because `experiments.equivalence_classes.lib.acmoves` also lives only in that worktree. When mixing the main tree with a proof worktree, import the main modules first and explicitly extend every split namespace level required by transitive imports before the first dependent import.

### 2026-08-16 Filter Morse critical counts before endpoint replay

[TRAP] A random maximal acyclic matching can be valid yet have more than one critical 0-cell, so calling `replay` on every sampled matching raised Fernández Theorem 2.9's one-critical-vertex error mid-benchmark. Compute `critical_cells(poset, matching)` first and accept only the declared `(1,k,k)` stratum; replay is the constructor for accepted certificates, not the rejection predicate for arbitrary samples.
