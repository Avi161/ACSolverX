# U124 theory investigation — September12,2026

Research window:03:28:52–06:28:52UTC, ending before02:30America/New_York.
This report accompanies the final deadline snapshot of
[all124 presentations](u124_final_table.md). The table's timestamp and
`final_snapshot` status distinguish the final export from earlier snapshots.

**No U124 presentation was trivialized, by ordinary or stable AC.** No shorter
rank2 presentation was certified. Allowing stable representatives gives
**85 shorter presentations**, reducing the aggregate saved starting length
from2356 to2191, a total of165 letters. These are certified reached states,
not proven global minima or evidence that a solution is nearby.

| Quantity | Result |
|---|---:|
| Exact input rows |124|
| Ordinary trivializations |0|
| Stable trivializations |0|
| New rank2 length improvements |0|
| Rows with a shorter stable representative |85|
| Archival initial total length |2446|
| Saved starting-best total length |2356|
| Best certified rank2 total length |2356|
| Best certified any-rank total length |2191|
| Ranks of retained best states |39 rank2,79 rank3,6 rank4|

The36 historical reductions from2446 to2356 predate this investigation. The
124 rows are retained components of a bounded AC/Aut search, an upper bound
on unresolved equivalence classes. They are not124 proven distinct problems.

## The shortest representatives actually obtained

| Contribution, added in this order | Newly shortened rows | Further letters saved | Aggregate best length |
|---|---:|---:|---:|
| One verified defining-word compression |84|157|2199|
| Primitive-word stable intermediate: aca_13 |1|1|2198|
| Ordinary AC suffix after compression: aca_24 |0|1|2197|
| A second defining word on six rows |0|6|2191|

The accounting includes **every relator**, including each helper's defining
relator. For example, aca_59 starts at total20 and reaches
`(Zxx,YZYzyz,YYYYxzzz)`, whose lengths3+6+8 total17. The letters `X,Y,Z`
mean inverses of `x,y,z`. The original input is still unsolved.

For aca_24, the saved pair has total17. Compression gives a full rank3
tuple of length16, followed by an independently replayed21-move ordinary
suffix ending at `(XXZYY,XXyxZ,XYzYZ)`, total15. Its first15-letter boundary
occurs after17 moves. None of the defining relators has been discarded.

Six rows benefit from a second helper:
`aca_108,aca_109,aca_111,aca_112,aca_113,aca_114`.
Each saves one additional letter and ends at rank4. The exact words, source
pointer, proof kind, and separate rank2 minimum are in the
[CSV](u124_final_table.csv) and [JSON](u124_final_table.json).

## General mechanisms and what they achieved

The [constructive catalogue](THEORY_CATALOG.md) states the hypotheses,
identities, examples, and proof/checker locations for every retained shortcut.
“Developed here” means derived or implemented during this investigation;
it does not assert literature priority.

| Mechanism | Mathematical benefit | Observed U124 outcome |
|---|---|---|
| Miller–Schupp companion residues | Reduces an infinite parameter family to at most n(n+1) cases; several residue classes trivialize explicitly | No new U124 solve; all366 terminal matches among the1190 raw rows were already in solved640 |
| Magnus boundary transport | Removes an extreme indexed support when the donor span fits strictly inside | Applicable on62 starting rows; no ordinary length gain or solve |
| Nondivisible extreme-power reduction | Replaces a power by a strictly smaller signed remainder, with an exact conjugated-donor error | Valid aca_9 prefix reduces indexed multiplicity while increasing ordinary length |
| Coupled relator exchange | Changes the donor and strictly decreases the specified sum of indexed spans | Five accepted rows; no ordinary length gain or solve |
| Critical-pair substitutions | Combines certified overlapping rewrite identities | Planted positive trivialization; no gain on the20-row development panel |
| Stable defining-word compression | Shares repeated signed blocks, counting the defining relator | Main source of the85 shorter stable representatives |
| Primitive isolator and recursive compression | Uses a whole-tuple basis change or a second helper | One additional row and six additional letters respectively |
| Three-relator power-conjugacy corridor | Exposes a genuine BS donor in a rank3 tuple; special parameter families trivialize | aca_24 exposes BS(1,2), but the remaining independent generator prevents the rank2 terminal argument |
| Cyclic and conjugated subgroup complements | Gives sufficient stable-trivialization criteria and a finite family of conjugator placements | No witness; distinguish completed root tests from capped follow-ups |
| Rigid planar-support compatibility | Replaces a factorial embedding search with phase-count contradictions |92 exact presentation complexes excluded; no obstruction to other AC representatives |
| Marked free-kernel projection | Constructs another rank2 presentation by a verified stable bridge | New Aut frames exist, but bounded continuations give no solve or original-length improvement |
| Euclidean power-complement transfer | Computes the marked basis directly from a coprime exponent pair, avoiding Nielsen search | One different Aut-minimal frame for aca_59, minimum21 versus original20; unsolved |

Two infinite-family exclusions are also documented: the reciprocal proper-BS
corridor inequalities contradict one another, and a specified fixed torus
donor obstructs the proposed primitive lift. Their scopes are those exact
constructions. Neither is evidence of an AC counterexample.

The last proof check extends the rank3 terminal family to m=-1 and
|k-n|=1. Fourteen signed examples replay through1263 ordinary elementary
moves to exactly(x,y,z), using three independent replay implementations.
This is a coordinate extension of the same unit-elimination mechanism,
not new U124 coverage; the actual aca_24 corridor has m=2.

## Why the stable records count

An ambient automorphism is admitted through its finite stable AC realization
on these known trivial-group inputs. This investigation also uses exact
defining-generator additions and deletions. Their proof is in
[Stable certificate conventions](STABLE_CERTIFICATE_CONVENTIONS.md).

There are two distinct certificate formats:

* **Elementary ordinary streams:** explicit relator inversions, products, and
  single-generator conjugations, replayed independently at every recorded step.
* **Theorem-backed stable composites:** exact word expansions, basis maps and
  inverse maps, plus the finite-realizability proof. The potentially enormous
  normal products needed to expand these into strict stable elementary moves
  have not been generated.

Consequently the stable length gains are mathematically certified under the
authorized convention, but their macro timings do not measure the time or
number of moves needed to emit the full stable elementary expansion. The
current two-generator search engine also cannot directly search the new
rank3/rank4 states; it would require an explicit higher-rank implementation.

## The last bounded search experiments

The early unit-lift gate stops as soon as enough marked rows exist to complete
the free basis by direct Nielsen operations. A20-row panel gives15 completed
projections using4224 image/compiler units. S20 then uses10776 heap pops on
those15 targets. Each completed attempt has exactly1000 combined units.
The five proper joins are not searched again from the original inputs.

All15 fail to solve or beat their saved starting lengths. Their ordinary
suffixes contain4227 elementary moves and pass independent replay. Two
additional, separately budgeted q3 attempts on aca_115 and aca_59 also fail;
their projections turn out to be literal ambient images of the original
pairs, explaining that lack of a new frame.

One final aca_59 experiment in swapped coordinates uses a direct Euclidean
construction with exponents7 and2. It spends28 preparation/compiler units
and972 S20 pops. The raw projected total60 reaches21, with a430-move replayed
ordinary suffix. A separate post-search16-image Whitehead check proves this
endpoint Aut-minimal at21. Those16 extra image evaluations are outside the
1000-unit search experiment. The original20 remains shorter.

These are **separate exploratory attempts**, not a portfolio that spent only
1000 units cumulatively per presentation. Candidate word images, compiler
operations, folding identifications and heap pops are different kinds of
work. Their counts are not claims of equal CPU cost, and this work establishes
no improvement over the existing AC19/MS640 search baselines.

## Measured costs

Representative clocks below come from saved reports. They exclude LLM work,
and exclude unexpanded stable normal products. No whole-session timing is
inferred by summing incomparable or overlapping reports.

| Component | CPU seconds | Wall seconds | Included work |
|---|---:|---:|---|
| Literal stable compression, all124 |0.923|8.065| Symbolic scan and author checks; wall includes per-row cooling |
| Primitive compression,19-row panel |2.207| — | Panel computation; separate planted checks excluded |
| Full rank3 Whitehead scan,84 tuples |0.429|5.311|90 maps/tuple; wall includes cooling |
| Ordinary rank3 substitution descent,84 tuples |1.173|6.027| Bounded candidate scan; wall includes cooling |
| Recursive compression of85 seeds |0.625|0.630| Algorithm only; seed replay and cooling separately recorded |
| Independent geometric audit,92 tuples |0.081|0.233| Witness reconstruction and controls; wall includes cooling |
| Early marked-basis gate,20 rows |0.039|1.168| Gate CPU; wall additionally includes replay/cooling |
| Residual S20,15 projected rows |6.478|6.487| Search only; compilation/replay adds0.012 seconds |
| Two q3 S20 continuations |0.496|0.515| Search only |
| Direct Euclidean target S20 |0.444|0.446| Search only |

The longer prepared-frame scan cost62.289 CPU seconds including validation
and output, and was not repeated. No million-node local campaign or parallel
CPU-heavy batch was launched. Tiny search continuations ran serially, with
one-thread numerical settings and verified warmed engine sources.

One recorded execution mistake concerns the earlier cyclic-complement
follow-up: its aca_0 preflight was repeated. That row used2000 physical
checks for1000 distinct identifications; the batch therefore used124055
physical checks rather than123055 distinct checks. The saved audit retains
both counts. This exception is not hidden by the per-attempt budget language.

## Files and remaining work

Start with [the full table](u124_final_table.md), then
[the theory catalogue](THEORY_CATALOG.md). Independent audits and machine
records remain alongside them. Some frozen author reports still say
“pending independent audit”; their later audit files record the actual review
result without rewriting the original experiment. The final artifact manifest
pins both versions and the final table snapshot.

The strongest demonstrated result is stable length compression. It does not
yet provide a useful terminal shortcut on U124. The marked-kernel construction
offers mathematically different rank2 targets, but its few bounded searches
have not shown a practical gain. The next meaningful experiment would need
either a new terminal theorem for the rank3 power corridor, or a justified
choice of kernel marking that improves search; simply enlarging the same
local runs is not supported by this evidence.

Work is saved in the separate `codex/theory-patterns-3h` worktree based on
`98f719e2ad9ce98cac1525c0984555f4711e412b`. Frozen census files, the parent
checkout's changes, PR#23 and main were not edited. These research files are
local and uncommitted; nothing was pushed during this investigation.
