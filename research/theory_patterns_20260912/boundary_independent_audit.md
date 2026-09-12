# Independent boundary theorem and compiler audit

Review status: **pass, with two interface/documentation precisions below**.
No incorrect free-group identity, termination inference, certificate endpoint,
transaction rollback, charge total, or saved-cohort metric was found.
The conditional theorem is valid. It does not prove that every unimodular pair
satisfies the online boundary tests, and the full124 record gives no solve or
ordinary-length gain.

The independent checker is `check_boundary_independent.py`; its exact results
and source hashes are in `boundary_independent_audit.json`. It passes **1,209
fresh finite checks** and independently replays and exactly regenerates all
**992 stored attempts on the 124 exact saved best-state inputs**. The final run
uses about 1.00 seconds wall / 0.93 seconds CPU, with no heap search, JIT import,
baseline execution, or frozen-data modification. Finite checks support the
compiler; the unbounded proof is assessed separately below.

## Unbounded proof assessment

For stable transport, let `R0^e=F t`, where `e=±1`, and let `S=G` have stable
exponent zero. If the nonempty supports are `[a,b]` and `[c,d]` and
`b-a<d-c`, the interval `[c+1-a,d-b]` contains exactly
`(d-c)-(b-a)` integers. Therefore an admissible translation always exists,
including when the entire interval is negative. For every such translation,
the support of `F_q` is contained in `[c+1,d]`; its translate by minus one is
contained in `[c,d-1]`. The shifted boundary block is also in the respective
interval. No monicity, sign, or boundary multiplicity restriction is needed.

Writing `D=t^q R0^e t^-q`, the exact errors for replacing a current subword
`H` in `P H Q` by `D^s H D^-s` are the two conjugates with signs `e*s,-e*s`
and conjugators `t^-q H Q,t^-q Q`. Multiplying these conjugates cancels the
middle `Q Q^-1` and leaves exactly `Q^-1 H^-1 D^s H D^-s Q`, the required
right multiplier. This derivation works for either direction, source sign,
ambient axis, relator position, and every nonzero signed power block.

Each replacement introduces no selected endpoint letter, and free reduction
only deletes letters. Thus endpoint occurrence count strictly decreases at
each block, proving that a whole-boundary pass finishes after finitely many
blocks. The target cannot gain an index outside its original interval and its
chosen endpoint disappears, so its span strictly decreases. If the target
becomes empty, its assigned span zero is also a strict decrease because the
input span was positive. This empty-target possibility is real for the
standalone nonunimodular identity and is explicitly checked; it is excluded
under the unimodular alternating theorem.

For the power rule, orient the unique extreme run positively and write the
aligned donor `D=C A E`, `A=z_boundary^m`, `m>0`. With `B=C^-1 E^-1`, direct
free multiplication verifies `A^-1 B=E D^-1 E^-1` and
`A B^-1=C^-1 D C`. Transport through the current suffix `V t` and undoing
the donor translation give exactly the implemented signed factors:
`(-e,t^-q E^-1 V t)` for a positive copy and
`(+e,t^-q C V t)` for a negative copy. Both `C` and `E` can be nonempty,
can have arbitrary signed interior letters, and need not form a BS tail.

The support-width hypothesis keeps the aligned donor interval inside the
recipient interval. Unique literal extremality makes `B` avoid the selected
endpoint. Removing one signed copy of size `m` reduces its occurrence count
by at least `m`; any other cancellation cannot add endpoint letters. Each
remaining endpoint run has exponent divisible by `m`: subtraction changes a
run by `±m`, while cancellation-driven mergers add or subtract divisible
exponents. An explicit middle-run identity check covers cancellation of an
interior bridge followed by merging opposite signed residual runs. The actual
compiler always selects the current leftmost endpoint run and recomputes its
run data after each replacement. There is no stale-run-divisibility argument.

For alternation, unimodularity and the exponent frame `(1,0)` force the base
exponent of `S` to be `±1`. Stable transport preserves that exponent because
it conjugates subwords, while a power pass keeps `S` literally unchanged.
Each completed nonterminal pass decreases the natural number
`span(F)+span(G)` by at least one. Endpoint occurrence count proves inner-loop
termination; the span sum proves outer-loop termination. These are distinct
measures. The number of completed passes is at most the initial span sum.
The early note's initial-sum-plus-one bound is a harmless weaker bound.

If `F` becomes empty, its normalized relator is exactly `t`, so generator
deletion turns the other relator into the signed base generator. If `G` has
span zero, free reduction and base exponent `±1` make it `z_i^±1`, so a
recorded conjugation exposes the base generator and deletes it from `F t`.
The final six ordinary relator operations correctly interchange `(y,x)`.
Empty `G` is incompatible with the unimodular hypothesis. The checker covers
initial terminal fibres, power-created empty `F`, standalone-created empty
`G`, both signs, and both relator positions.

The checkpoint condition is a sufficient online condition, not a static
classification of all unimodular presentations. It is nonvacuous: the stated
family for arbitrary `m>=2` has successive stable fibres
`z_0^(eta*m) z_2^(m+1)`,
`z_1^(eta*(m+1)) z_2^(m+1)`, and
`z_1^(eta*(m+1)+m)`. The last exponent is `2m+1` or `-1`, hence never zero.
A subsequent stable-transport pass makes the other fibre span zero. The
new checker tests translated/reflected cases at moduli 4 and 7, beyond the
author's 2, 3, 5 grid. No total-length, polynomial-time, or search-speed bound
follows from this proof.

## Independent implementation evidence

The checker does not import the author's check helpers or legacy AST replay.
It uses a separate divide-and-conquer free reduction with maximal cancellation
at the boundary between two already reduced strings. Its elementary replay
is compared with `ac_words.replay`. It retains every elementary state and
checks the word cap at those states, actual move counts, actual committed
AC2 counts, best-prefix endpoints, total charges, and claimed peak length.
For every saved factor ledger it derives the block's start from its emitted
conjugator/sign costs, independently expands the free-group factors, and
checks that the donor is identical before and after the block.

| Fresh independent checks | Count |
|---|---:|
| Every legal q in strictly positive and negative intervals, both directions/axes/roles/signs | 256 |
| Rejection below/above that interval and noninteger q | 192 |
| Translated nonmonic alternating solutions at m=4,7 | 128 |
| Signed cancellation and merged-run identities | 24 |
| General nonempty C/E power compiler cases, both q signs/axes/roles/signs | 128 |
| Power pass creates empty F and completes terminal cleanup | 64 |
| Standalone nonunimodular transport creates empty G | 32 |
| Negative-source transaction sweeps over work/move/word/indexed caps | 280 |
| Initial empty-F/span-zero-G terminals, signed indices/axes/roles | 96 |
| Optional best-prefix cleanup is charged or suppressed at the budget boundary | 4 |
| Empty/unimodularity/frame rejection cases | 5 |

The 280 cap sweeps produce 64 work stops, 48 certificate stops, 88 word stops,
40 indexed-word stops, and 40 completed passes. Every returned main
certificate is a prefix of the uncapped test stream; every retained source
is identical to its input free word. The staging transaction correctly
discards a partially conjugated or inverted donor. Proposed relation uses
can remain charged when the staged block is rejected, while committed
relation uses equal the number of actual AC2 moves. Best-prefix conjugation
cost shares the same budget and is not silently free.

Two precise qualifications should accompany the API:

1. Source preservation applies to `final_pair` and the main block-boundary
   certificate. `best_pair` may apply an explicitly certified cyclic cleanup
   to either relator. For input `['yxY','y']` at budget 2, `final_pair` is
   unchanged, `best_pair=['x','y']`, and one `best_prefix_cleanup` charge is
   recorded. This is consistent with the stated best-prefix semantics; do
   not describe every returned endpoint as preserving the donor. Input words
   with free cancellation are initially freely reduced, as documented.
2. The report says the target is "recollected after every committed block."
   The implementation actually carries exact reduced `newf/newg` inside a
   pass and recollects at pass/checkpoint boundaries. Its equality check
   against the emitted ambient word establishes the required invariant.
   A more literal description is: "The exact current indexed spelling is
   updated after every committed block." This is a wording correction only.

## Full124 archive verification

The best-state CSV hash is
`8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3`.
Its ordered IDs and exact free words agree with all archived rows. All eight
literal orientations per row are present in the specified order: both axes,
both source roles, and both boundary orders. There are no omitted rows or
orientation attempts. The twenty development records are identical to their
copies in the full archive. Compiler, author-check, inventory, and legacy
replay source hashes match those stored in the author report.

| Independently recomputed full124 quantity | Value |
|---|---:|
| Exact rows / attempts | 124 / 992 |
| Solves / strict ordinary-length gains | 0 / 0 |
| Stable-source / extreme-power completed passes | 149 / 48 |
| Rows with at least one completed pass | 62 |
| Total charges / largest per-row charge | 2,929 / 63 |
| Criterion failures / outside-frame attempts | 230 / 762 |
| Nonunique boundary conditions / nondivisible boundary conditions | 260 / 200 |
| Largest certificate / largest committed elementary-state word | 408 / 141 |
| Resource-stopped attempts | 0 |

All 48 saved power passes have modulus one. Thus this cohort supplies evidence
for alternating monic span reductions; nonmonic compiler evidence comes from
the planted and independent algebra cases. The 124 rows remain retained
components of a bounded AC/Aut computation, not 124 proved distinct AC classes.

The author archive itself was read, replayed, and compared against fresh
in-memory compiler results; it was not rewritten. This auditor changed only
the three assigned independent-audit files. No advisor tool was available in
the exposed tool inventory.

Run from this worktree using the outer checkout's Python environment:

    /Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python research/theory_patterns_20260912/check_boundary_independent.py
