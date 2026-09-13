# AC-SolverX — what a session needs to know before touching the search

Four settled facts. The code on this branch reflects the first two; the third
is about modules that live on other branches. Read this file before trusting a
docstring found elsewhere.

## 1. The best heuristic is `S20_MK2`

```
priority(r1, r2) = L + 20*S + 2*MK
```

`S` = smaller mean block (mean run length of the thinner generator), `MK` = max
knots over the two relators, `L` = total length. Lower pops first. `S20_MK2` is
the **recommended** heap ordering — where a default is needed, this is it.

Provenance, stated as a pair — a number without both halves is not readable:
*selected on* the ac1m_hard_aut train 120 (54/120, against the length control's
0/120); *evaluated on* an automorphism-disjoint fresh holdout (27/60, against
the length control's 0/60). On the 60-row ladder at budget 10,000 it solves
52/60 against the plain greedy's 40/60 — McNemar 12-0, a strict superset, gains
concentrated in bins 6-9. Cap caveat: those runs used `mrl=48` while the frozen
greedy column is `mrl=24`, so read the delta in solves as primary and the node
ratios as indicative.

Note the tuning grid's own top scorer, `S28_MK2_F8` (57/120), is **not** the
keeper: it falls to 22/60 on that fresh holdout. Taking the training-set maximum
would repeat the mistake described next.

## 2. `RECOMMENDED` is overfit and is NOT production

```
L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb        <- do not use as default
```

It was selected on a slice containing fourteen of the twenty rows it was then
validated against, and its 60-row campaign used subset-60 as its own row list.
So every margin ever published for it -- 10/20 -> 15/20, the 60-row cost tables
-- is largely in-sample: a statement about the tuner, not about the ordering.

This branch ships `S20_MK2` instead. Both the name `RECOMMENDED` and the
withdrawn weight map are guarded against returning by
`tests/test_greedy_heuristic.py::test_module_ships_no_overfit_weight_vector`.

The runs `RECOMMENDED` produced are real and should be kept as the record of
what that campaign cost (the `heur_*` columns of the arms tables); it is the
recommendation that is withdrawn, not the data.

## 3. The μ-ladder is NOT production

It does not appear on this branch at all. On the research branches
(`research/w5/*`, `cursor/*`, `experiments/ppo`) `AGENTS.md` describes it as the
active line — that framing is stale. Its modules and results stay as records.

## 4. The census

| step | count |
|---|---|
| Miller–Schupp presentations | **1,190** |
| solved | **640** |
| unsolved | **550** |
| A-equivalent reps among the 550 | **261** |
| after automorphisms and AC moves | **124** |

State it once, from here. Two precisions worth carrying: 124 is an **upper
bound** from a bounded AC-move search (caps 30–36, unanimous across five arms,
not proven converged), and the exact `Aut(F₂)` step between 261 and 124 is
**168** — no change of variables does better than 168. Derivation and the
machine-checked merges are in `results/equivalence_classes/EQUIVALENCE_FINDING.md`
on the research branches; `docs/BRANCH_MAP.md` says which branch holds what.

## Lessons Learned

### [2026-09-12] AC19 ladder stages contain only the preceding stage's survivors
[TRAP] Building a hard-solved certificate panel from the 5M greedy JSONL omitted
rows solved between 100k and 1M (`ac19_3303`, `ac19_69456`): those rows live in
the 1M stage and never enter the 5M survivor input. Join solved records across
the 1M, 5M, and 10M stage files, then assert the exact requested ID set before
writing a frozen panel.

### [2026-09-12] A solved compact row may omit path capture
[TRAP] The AC19 1M greedy records for `ac19_3303` and `ac19_69456` say solved
but contain neither `path` nor `path_moves`; capture-free solve metadata is not
a replay certificate. Before freezing a known-solved experimental panel, require
and replay both fields, or anchor the row to a separate verified certificate.
[TRAP] Saved `path_moves` are underscore-delimited strings, while
`greedy_baseline.moves_to_states` expects integer 4-tuples. Decode each entry
with `greedy_baseline.str_to_move` before replay.

### [2026-09-12] Research scripts must add the repository root to `sys.path`
[TRAP] `run_panel.py` imported `experiments.search` successfully under unittest
because the repository root was injected by the test runner, then failed when
executed directly because `sys.path[0]` was the script directory. Add the
resolved repository root explicitly before importing project packages, and
preflight the actual CLI rather than relying only on module tests.

### [2026-09-12] Verify retained high-rank certificates, not every generated child
[TRAP] A four-row cap-6 screen spent more than five minutes inside
`high_rank_ac_search.normal_product_event -> verify_event -> Fraction`
determinants because every emitted child was independently audited. The move
constructor already checks its exact packed/canonical identity. For exploratory
search, keep generation lightweight and independently replay only retained best
and solution paths afterward; regression-check that fast and audited generation
produce identical child endpoints on planted states.

### [2026-09-12] Keep inspection commands literal after long-running searches
[TRAP] Two post-run inspection calls picked up stray generated text in a tool
argument and a JSON key (`generated_states_with_unit grac`), causing zero-work
retries. Use short literal commands copied from the schema and inspect filenames
with `ls` before composing the summary query.

### [2026-09-12] Detect terminals at the final generated frontier
[TRAP] `search_row` originally set its solved flag only when a state was popped.
A terminal generated by the last permitted pop became the selected endpoint but
was labeled unsolved. Derive the flag from the retained endpoint or detect the
child immediately, and instrument all generated unit/bigon states before making
a claim about what a bounded search encountered.

### [2026-09-12] Preserve the executed runner beside every search report
[TRAP] The first high-rank generic and macro reports recorded their runner hash,
but later edits replaced the only source file. Exact paths still replay, yet the
old search ordering cannot be reproduced from its pinned hash alone. Freeze a
same-directory source snapshot before execution. The authoritative macro report
was rerun as `all124_macro_current_p100.json` against the final source.

### [2026-09-12] Validate literal tool source before dispatch
[TRAP] Several continuation calls contained stray placeholder tokens and failed
before doing work. Keep each orchestration wrapper minimal, inspect every field,
and dispatch only the literal command already validated by the preceding call.

### [2026-09-12] Keep the retained-triangle search fixed-rank when requested
[TRAP] The first broader AC screen used Lemma11 removals as a scoring projection,
even though the user's target was to search among the short high-rank relators.
When the user says not to destabilize, generate and score only fixed-rank AC
substitutions and stop at the length-at-most-two terminal boundary without
removing a generator. Preserve any later destabilization as a separate step.

### [2026-09-12] Exercise result serialization in high-rank search preflights
[TRAP] The first retained-triangle AC preflight verified its generated moves but
then failed in summary construction because `sum(r, generator)` referenced an
undefined variable. A search preflight must reach atomic JSON serialization and
read-back, not merely complete the search loop, before an all-row run.

### [2026-09-12] Scratch worktrees share the repository virtual environment
[TRAP] `.scratch/theory_3h_20260912/worktree` has no local `.venv`, so invoking
`.venv/bin/python` there fails before a probe starts. Use
`/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python -B` for research
scripts launched from this worktree.

### [2026-09-12] Validate certificate signs at construction
[TRAP] The first `research/theory_patterns_20260912/ac_words.py` draft let
`Factor(0, '')` mean inverse to the algebra evaluator but positive to the AC
emitter. Require an exact integer sign in {-1,1} at `Factor` construction,
validate relator indices and pair cardinality, and independently replay every
accepted witness. Boolean signs are not accepted as integer signs.

### [2026-09-12] Use all available research slots without exceeding capacity
[WORKS] The user requests roughly ten parallel specialists; this session permits
four active agents including the coordinator. Keep three specialist assignments
active when independent useful work exists and rotate through focused waves.
Validate one artifact-producing preflight before the first wider fanout.

### [2026-09-12] Exercise every terminal disjunct after cyclic reduction
[TRAP] `ms_family_verify.solve(2,0,1,0)` reached `XXyx`, a cyclic conjugate
of a one-occurrence primitive, but `primitive_cleanup` counted occurrences in
the raw word and rejected it. Explicitly emit the cyclic conjugation before
checking that terminal condition. Test zero residues separately from opposite
unit residues; eight positive examples had missed this distinct proof branch.

### [2026-09-12] Stable scope and final U124 accounting
[WORKS] The user explicitly extended this investigation to stable AC and
requires an all124 table before02:30 America/New_York. Preserve archival initial
length, the best known starting length, and the newly reached best length as
separate columns. Count all relators in stable-rank states and distinguish
theorem-backed stable composites from fully expanded elementary certificates.

### [2026-09-12] Derive research metrics from exact records
[TRAP] A manually counted corridor length was14 but its verified word has15
letters. A planted frame test also used determinant-4 input as a required solve.
Compute lengths and determinants from the words before asserting them; every
required solved positive control must first satisfy the theorem's hypotheses.

### [2026-09-12] Reuse preflight work and enumerate paths before reading
[TRAP] The complement follow-up repeated its completed aca_0 pilot, doubling
physical work on that row even though the distinct tested set stayed unchanged.
Reuse the pilot record in the main pass and count duplicate work explicitly.
[TRAP] An unquoted speculative `stallings*` path and a table file not yet written
aborted under zsh. Use `rg --files` to locate existing paths and wait for the
worker's artifact-ready message before reading a newly assigned deliverable.

### [2026-09-12] Keep finalization edits and agent slots explicit
[TRAP] A worker's artifact-ready message can precede its final inactive status;
dispatching the next worker then returns `agent thread limit reached`. Wait for
the final-status notification before reusing its concurrency slot.
[TRAP] A multi-file patch carried an unrelated trailing context hunk and failed
verification. Read the affected files after a failed patch and retry only the
intended hunks; never infer which files changed from the attempted patch text.

### [2026-09-12] Validate the Miller–Schupp grid footer
[TRAP] `ms_solved_grid.csv` ends with a blank-word numeric totals row, causing
`KeyError: '170'` when treated as a presentation. Keep only nonempty word rows,
validate their alphabet, and assert the expected170 words before cell traversal.

### [2026-09-12] Stable intermediate minima are different from rank-two endpoints
[TRAP] Comparing only the rank2 endpoints missed real shorter rank3 tuples:
aca_59 reaches `(Zxx,YZYzyz,YYYYxzzz)`, total17 versus starting20. Score every
certified stable boundary, including nonprimitive and budget-stopped attempts,
and sum all current relators. Keep rank2 and any-rank minima separate. A stable
definition/compression prefix with an independently checked finite-realizability
proof is admissible under the user's scope even if its normal-product expansion
is not emitted; label that certificate kind explicitly and do not call it a solve.

### [2026-09-12] Distinguish a terminal local minimum from a failed descent
[TRAP] A descent report labelled all84 locally minimal endpoints as negative
rows even though aca_24 had improved before reaching its endpoint. Name that
count `locally_minimal_endpoint_rows`; count successful prefixes separately.
When correcting metadata without rerunning, retain the executed script hash
and state precisely which reporting field changed.

### [2026-09-12] Inspect a research report's schema before joining it
[TRAP] `recursive_stable_compression_report.json` uses `records`, while nearby
reports use `rows`; assuming the shared key raised `KeyError: 'rows'` in an
inspection snippet. Read the top-level keys and one record before writing a
cross-report adapter, and join by explicit presentation ID rather than position.

### [2026-09-12] Locate the cached runtime by a verified ancestor marker
[TRAP] A hard-coded parent index in the nested worktree continuation selected
`surf` instead of `ACSolverX`, causing `ModuleNotFoundError: experiments` before
any search ran. Locate the ancestor containing `.venv/bin/python` and verify
the imported source hash before using its warmed Numba cache.

### [2026-09-12] Complete a marked basis as soon as unit lifts are available
[WORKS] `two_complement_unit_gate.py` replaces a capped Nielsen tail with
deterministic relator-basis operations: fix rows whose images are x and y,
then clear each remaining image letter with the corresponding signed lift.
Reserve the exact compiler image count plus two kernel projections before
accepting the gate. The20-row screen produces15 marked projections using4224
units; all15 subsequent elementary S20 prefixes independently replay. These
image/compiler units and heap pops are heterogeneous, not equal compute.

### [2026-09-12] A changed complement can still return the same Aut orbit
[TRAP] For an input with second relator `y^-d*x^n`, choosing the complement
`y^(d-1)` passes the join test but the natural projected marking is just the
ambient image `x->x, y->x^n*Y`. Both q3 follow-ups returned old Aut frames.
Check an exact inverse map before calling a projected presentation a new
search problem. Other Euclidean markings require their own proof and tests.

### [2026-09-12] Keep final-table validation outside its input manifest
[WORKS] `final_table_validation.json` verifies the generated table, so including
it among the table builder's input components creates a circular or stale hash
dependency. Exclude that validator output from inputs; pin it only in the final
artifact manifest after rebuilding and validating the table.
[TRAP] Validation lives inside `u124_final_table.py`; no separate
`validate_final_table.py` exists. Inspect the builder's actual entry points
before inventing a validation command.

### [2026-09-12] Preserve the quantifier in a boundary-descent statement
[TRAP] The draft theory catalogue described one extreme-run replacement as
strict span descent. A single replacement can leave other occurrences of the
same extreme. The proof in `astra_patterns.md` removes every such run using
one suitable shifted donor before claiming the span decreased. Keep the
per-block identity and the complete-pass conclusion separate in documentation.

### [2026-09-12] Rank-independent compression and bounded-cut completeness
[WORKS] `research/rank_unbounded_20260912/search.py` represents generators by
signed integers, so additional definitions are constrained by measured work and
total length rather than a six-letter alphabet. Count every defining relator.
Two length-neutral definitions followed by a whole-tuple Whitehead change can
improve a rank4 endpoint even when literal compression alone has stopped.
[TRAP] A capped minimum-cut loop cannot infer completeness from the last loop
variable: a break can occur before that last candidate is evaluated. Record the
actual number of cuts in the current pass. Preserve the executed source when
correcting reporting metadata after a saved screen.
[TRAP] The isolated worktree lacks the parent checkout's untracked literature.
Locate references in the parent without assuming the worktree includes them;
read an agent artifact only after its explicit artifact-ready notification.

### [2026-09-12] Preserve JSON round-trip types in generated summaries
[TRAP] `rank_unbounded_20260912/summarize.py` initially compared integer-keyed
rank counts to their JSON read-back, whose object keys are strings. Use explicit
string keys for JSON mappings before writing, so strict read-back comparison
checks the data instead of failing on a predictable serialization conversion.

### [2026-09-12] Resolve exact generator IDs from certificate pointers
[TRAP] After Lemma11 removal, an endpoint may use nonconsecutive generator IDs
(aca7 uses2,3,4). The display-word parser compacts the alphabet, so parsing a
summary silently changes the basis. Continue from the exact integer endpoint
at its witness pointer, or record an explicit signed relabeling event. The
continuation loader is `research/u124_rank_3h_20260912/verify.py::load_baseline`.

### [2026-09-12] Read each row before reporting a grouped gain
[TRAP] Three one-letter gains were incorrectly described with one shared
starting length: aca75 is19→18, but aca83/84 are20→19. Extract each displayed
before/after pair directly from the result records; equal gains do not imply
equal initial lengths.

### [2026-09-12] Audit every retained template in a generator exchange
[TRAP] A proposed pruning rule treated a pivot with one old-generator occurrence
and one helper occurrence as a pure ambient automorphism. The other compressed
relators still undergo substitutions using the retained defining donor, so the
complete exchange may shorten an Aut-minimal tuple. Do not discard this case.
For pivot `a b z`, the exact isolated word is `a=Z B`, not `B Z`; generate the
substitution trace before writing a worked example.
[WORKS] Continuing from previously proved endpoints is cheap, but a new1000-unit
probe excludes historical seed-discovery work. Compare new gains against the
best imported endpoint, and label those incremental costs explicitly.

### [2026-09-12] Reuse observed runner paths in independent audits
[TRAP] Guessing `macro_probe.py` and a new interpreter location caused avoidable
read/launch failures; report metadata already identified `frontier.py`, and the
working interpreter was `/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python`.
Inspect recorded source paths and retain the verified interpreter command.

### [2026-09-12] Use machine IDs and explicit research imports
[TRAP] A continuation command used display IDs such as `aca7`, but the frozen
loader keys are `aca_7`. Inspect the loader keys before constructing a panel.
The new verifier does not add the old search directory at import time; import
only what the inspection needs or insert both explicit research paths before
importing `search`. Neither failed command performed presentation searches.

### [2026-09-12] Keep generator labels sparse throughout certificate auditing
[TRAP] The frozen `rank_unbounded_20260912/audit.py::defining_event` expanded
`range(1, helper)` into a dictionary. A new10^25-label control stalled on that
allocation even though the presentation had only three generators. Current
`u124_rank_3h_20260912/verify.py::sparse_defining_event` maps only occurring basis
IDs and checks every definition/template letter against that set. Preserve the
frozen auditor; never infer basis size from the largest integer label.
[WORKS] The repaired checker replayed the same signed rank3→4 chains with large
IDs. Always retain the full `exec_command` result, including a possible session
ID, instead of printing only stdout; a stalled audit must be stopped by its
exact process/session without affecting another worker's search.

### [2026-09-12] Keep experimental records and control summaries distinct
[TRAP] A scoreboard discovery loop treated every JSON `rows` field as a list;
control reports also use an integer count. Require a nonempty list of records
with the certificate fields before handing a file to `scoreboard.py`.
[TRAP] Extending a saved seed by copying its whole record retained stale
`best_length` and `best_rank` metadata in `primitive_search_results.json`.
The exact path replay was correct. Preserve the executed snapshot, write a
separate reporting-only correction, and construct extension metadata afresh.
The authoritative result is `primitive_search_results_corrected.json`.

### [2026-09-12] Distinguish raw exported chains from normalized search records
[TRAP] `endpoint_closure.py` initially passed a full exported rank-two chain
to `verify_record`, which expects its source in canonical row order. The raw
export preserves the input CSV row order and has its own export event kinds.
The check rejected it with `candidate starts from wrong source or silently
relabels generators` before any batch ran. Continue a search record through
the exact CURRENT witness pointer and recorded normalized source; replay a
flat export through `export_paths.replay_event`. Do not silently reorder a
certificate boundary or mix the two schemas.

### [2026-09-12] Retain high rank for the individual-relator objective
[WORKS] The user explicitly values shorter individual relators even when rank
and total length increase. Keep retained high-rank states separate from the
minimum-total scoreboard; do not automatically destabilize them. All-relator
length at most three is universally attainable by defining generators, so it
is a representation change rather than evidence of a solve. At most two is a
constructive terminal condition for balanced trivial presentations; exactly two
for every row instead admits a nontrivial C2 quotient.

### [2026-09-12] Archive generated records below GitHub's file-size limit
[TRAP] `research/theory_patterns_20260912/prepared_frames_full124.jsonl` was
252 MB, so committing it directly would exceed GitHub's 100 MB per-file limit.
[WORKS] Store it as deterministic gzip (`gzip -n -9`), make consumers stream
the archive, and record the SHA-256 of the decompressed JSONL. Before staging a
research batch, scan every intended file for the remote's size limit.

### [2026-09-13] At an all-triangle root a unit is parity-forbidden and a bigon needs a shared digram
[MECHANISM] Products of two length-3 cyclic words have even length, so a fixed-rank
search from a triangulated root cannot make a unit in one move; a length-2 relator
needs two relators sharing a cyclic digram modulo (u,v)->(v^-1,u^-1); every one of
the 255 all-triangle roots in a 400-row AC19 sample is digram-disjoint, as are all four
hard rows (the other 145 roots already carry a length<=2 relator from preprocessing).
Score by digram coupling, not total length (constant 3r), and never read an empty
cap-3/cap-4 neighbourhood as a budget problem. See
`research/ac19_triangle_theory_20260913/THEORY.md`.
