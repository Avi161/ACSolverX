# Extreme-power residues: exact finite prefixes and bounded negative screen

`extreme_residues.py` extends the exact power-replacement identity to nondivisible runs and supports an explicitly certified cyclic indexed donor cut. The frozen alternating compiler is unchanged. The extension uses only ordinary AC1 inversion, AC2 right multiplication, and AC3 conjugation by a single signed generator; it performs no heap search, JIT compilation, ambient basis change, or stabilization.

**459 checks pass.** Applying the extension to the saved failed checkpoints gives **0 strict ordinary-length improvements and 0 solves on the exact124 inputs**. Across the 460 side/checkpoint attempts, only two admit a strict residue step; both are the same `aca_9` state reached by the two saved boundary orders. Its selected extreme multiplicity drops from 2 to 1 while its span stays at 2. A single frozen-compiler retry after each positive prefix still ends `criterion_failed`.

The complete machine record, source hashes, input words, exact prefixes, extension streams, and replay evidence are in `extreme_residues_report.json`. The preceding certificates remain in the frozen `boundary_compiler_report.json`, which is pinned by SHA-256 and joined by row ID and attempt index.

## Exact identity with a remainder

Use the same literal Magnus convention `z_i=t^i z t^-i`. The current source `S` has stable exponent zero, and the recipient has normalized stable exponent one, `R=F t`. The source is not required to have base exponent ±1 for the local identity.

Assume the chosen extreme index of the reduced indexed source appears in one maximal run of signed exponent ±m, where `m>0`. Orient the source by `e=±1`, shift it to the selected extreme of `F`, and write

    D=t^q S^e t^-q=C A E,
    A=z_boundary^m,
    B=C^-1 E^-1.

Require `span(S)<=span(F)` so that alignment places every index of `D` inside the recipient's support interval. No letter in `B` has the selected boundary index. There is no commutativity hypothesis on `C` and `E`.

The exact free-group errors remain

    A^-1 B = E D^-1 E^-1,
    A B^-1 = C^-1 D C.

For a current boundary run `z_boundary^k`, let `eta=sign(k)` and `r=k-eta*m`. The free-group equality

    z_boundary^k = z_boundary^r A^eta

holds whether or not the literal input contains a full copy of `A^eta`. Consequently the current recipient

    R=U z_boundary^k V t

may be changed to

    R'=U z_boundary^r B^eta V t

with one source-restored multiplication. The exact factor relative to the current source `S` is

    eta=+1: sign -e, conjugator t^-q E^-1 V t;
    eta=-1: sign +e, conjugator t^-q C V t.

Indeed, cancellation of the common prefix leaves `z^-k z^r=A^-eta`, giving the same error as the full-block rule. This proof uses a freely equal factorization of the current word, not a claim that an absent literal block was observed. The implementation records `virtual_chunk=True` precisely when `|k|<m`, and its predicted output must agree with the independently replayed elementary stream before the transaction is committed.

Two supported policies are:

- `nearest=False`: a step requires `|k|>=m`, so ordinary full blocks are removed until each surviving run has absolute exponent less than `m`.
- `nearest=True`: a step requires `|k|>=m` or `2|k|>m`. For `0<|k|<m`, the latter condition is exactly `|k-eta*m|<|k|`. This leaves each surviving run with `2|k|<=m`. Exact half-modulus ties are not changed.

The replacement is placed after the remaining power in the current run. This fixes a deterministic policy in the noncommutative word, rather than treating all placements of the replacement as interchangeable.

## What decreases, and what does not follow

During one pass the source, alignment shift `q`, and selected recipient index are fixed. Let `N` be the total number of recipient letters at that index. A step replaces `|k|` such letters by at most `|r|`, because `B` contains none and later free cancellation can only remove more. Since `|r|<|k|`, every committed residue step strictly decreases the natural number `N`.

It follows that a pass uses at most its initial `N` source multiplications before no admissible run remains. This remains true if newly adjacent runs merge: the next step is selected from the actual freely reduced current indexed word and must again strictly reduce `N`. No divisibility invariant is needed.

All replacement indices remain in the pass's initial recipient support interval. This controls indexed support, but ordinary expanded word length can grow. The selected endpoint may survive as a nonzero remainder, so span need not decrease. The result records both multiplicity and span, and asserts `span_strictly_decreased` only when the checked endpoint words justify it.

This is a finite-prefix theorem, not a completion theorem, classification of AC-trivial presentations, or global terminating rewrite system for arbitrary alternation of endpoints. The screen applies one such prefix and one bounded retry of the already frozen alternating compiler.

## Cyclic indexed donor cut

A selected donor endpoint may appear in two linear maximal runs, one beginning the indexed word and the other ending it. If these are the only selected endpoint runs, they form a single circular run.

Write the exact indexed word `G=P Q`, where `P` is the first such run. Its free-word expansion gives the exact identity

    expand(P)^-1 S expand(P) = expand(ired(Q P)).

The compiler emits this conjugation explicitly and retains the conjugated donor as its new current source. It records the cut position, expanded conjugator, before/after donor words, and move boundary. It then recollects and rechecks the transformed donor; it never assumes that the old signed exponent or support survived.

If the two runs have the same sign, the cut joins them into a single run. Opposite signs can cancel partially or completely at the circular boundary. When the cut yields a span-zero donor, the procedure reports `span_zero_donor_after_cyclic_cut`; it does not label an arbitrary proper power as a terminal generator. Unimodularity would imply exponent ±1, but the local residue API does not assume it. A regression case explicitly checks the proper-power outcome.

This optional preliminary conjugation is distinct from donor restoration during each product. Every residue multiplication restores the exact current donor after the preliminary cut. A resource stop preserves every already committed elementary step; it never reports that the preliminary cut was undone when it was retained.

The implementation does not enumerate arbitrary cyclic rotations or arbitrary donor cuts. It recognizes only a unique literal extreme run or the specified two end-runs forming a unique circular extreme run.

## API and bounds

The entry point is

    compile_residues(pair, stable='x', source_index=0, side='lower',
                     nearest=True, allow_cyclic_cut=True, limits=Limits())

The nominated stable-exponent relator is at `source_index`; the other relator supplies the power relation. Both literal generator axes, relator positions, source inversions, and recipient stable exponents ±1 are supported. A negative stable exponent is normalized with a recorded inversion. `Limits` is imported unchanged from the frozen compiler and requires an algebraic budget at most1,000.

The return format extends the frozen compiler's independently verified final/best certificates with `preparations` and `residue_summary`. Results are finite partial certificates, including when the reason is `residue_prefix_complete`. The extension itself makes no solve assertion. Important reasons include `residue_hypothesis_failed`, `no_strict_residue_step`, `span_zero_donor_after_cyclic_cut`, and the explicit word/indexed-word/certificate/work limits.

Recognition, candidate/block checks, conjugations, source uses, and optional best-prefix cleanup share the frozen accounting. Actual elementary conjugations and donor-restoration inversions remain separately counted. Each replacement uses the frozen bounded transaction core, compares the expected free word, restores the source, and checks every elementary intermediate word against the cap before commit.

## Independent checks

The 459 checks include:

| Check | Cases |
|---|---:|
| Arbitrary noncommuting `C,E`; `m=3,4,5`; positive/negative nondivisible runs; ordinary and virtual chunks; both endpoints, axes, roles, and input relator signs | 384 |
| Cyclic split extreme runs merged by explicit conjugation, all signs/roles/axes | 32 |
| Opposite-sign circular cancellation exposing a span-zero donor, all signs/roles/axes | 16 |
| Proper-power donor is not called a terminal generator | 1 |
| Ordinary residue policy, negative powers, and strict nearest threshold including an unchanged half-modulus tie | 4 |
| Budgets0 through14 preserve certified prefixes | 15 |
| Word, indexed-word, and certificate guards preserve the source during rejected products | 3 |
| Malformed API/input rejection | 4 |

The noncommuting-context tests assert that every nondivisible residue pass reduces multiplicity while preserving span. This directly guards against accidentally promoting multiplicity descent to span descent.

Each planted final/best stream and each screen stream concatenated with its saved prefix is checked by three implementations: the integer-stack replay, independent repeated-string cancellation, and the unchanged AST-extracted legacy `replay_elementary` body. The legacy module itself is not imported, so these checks do not trigger JIT compilation. The script verifies the frozen compiler's hash before using the saved checkpoints.

## Saved-checkpoint screen

The screen starts from all230 `criterion_failed` frame/order attempts in the existing exact124 archive and tries both endpoint sides, giving460 residue attempts. It does not rerun their preceding searches or compilers. It charges all2,929 saved prior work units against the same1,000-per-row budget before extending any checkpoint. A positive residue prefix or a committed cyclic cut receives one frozen-compiler retry using only the remaining row budget. No retry is made after a zero-change failed recognition.

The configured caps are expanded relator length512, indexed length256, and12,000 elementary moves per extension or retry. No cap is reached. The largest total per-row accounting is83, and total work including every saved prefix is4,289:1,360 additional units beyond the frozen archive.

| Result | Count |
|---|---:|
| Residue side/checkpoint attempts | 460 |
| Nonunique extreme-run hypothesis failures | 260 |
| Already within the strict nearest-residue threshold | 198 |
| Positive residue prefixes | 2 |
| Cyclic donor cuts admitted on these checkpoints | 0 |
| Frozen retries | 2 |
| Retries ending at a failed checkpoint | 2 |
| Inputs with strict ordinary-length improvement | 0/124 |
| Inputs solved | 0/124 |

The two positive prefixes are identical `aca_9` transformations from saved attempts6 and7:

    retained donor: YXXXyxx
    recipient:     xYYxxyyy  ->  xYYXyxxyy
    literal stable generator: y
    selected side: lower
    m=3, q=-1, boundary=-2
    multiplicity: 2 -> 1
    span: 2 -> 2
    elementary moves in the residue block: 5

The recipient's ordinary length increases from8 to9. This is not a new solved row or a new minimum. The frozen retry returns the same pair and an explicit failed checkpoint.

The final test-plus-screen run took approximately0.263 seconds wall and0.261 seconds CPU, including the independent replays and excluding the final JSON write. The saved-checkpoint extension alone took approximately0.15 seconds. These small implementation measurements do not establish a search speedup or a complexity bound. No cooldown was needed for this subsecond serial symbolic check.

Run from the outer checkout:

    .venv/bin/python .scratch/theory_3h_20260912/worktree/research/theory_patterns_20260912/extreme_residues_checks.py --legacy-replay-source .scratch/theory_3h_20260912/worktree/research/supermoves_20260908/certificate_decoder.py

Only the four assigned `extreme_residues*` source/check/report files were changed. The frozen boundary compiler, its report, the shared word kernel, census inputs, and existing results were not modified.
