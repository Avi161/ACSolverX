# Independent audit: PASS for the saved stable-composite paths

`audit.py` independently replays the saved certificates. It does not import
the search implementation's reduction, expansion, canonicalization, inverse
checking or determinant helpers for that replay. Its free reduction repeatedly
deletes adjacent inverse pairs, independently of the implementation's stack.
Subject functions are called only for finite planted controls and minimum-cut
comparisons with exhaustive tiny partitions. The audit itself reruns no census
search; the separate observer validations below are explicitly charged reruns.

Run from the worktree with the parent checkout's interpreter:

```
/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python research/rank_unbounded_20260912/audit.py
```

The machine-readable results and input hashes are in `audit.json`.

## Final exported deliverables: PASS

The final `all124.json`, `all124.csv` and `ALL124.md` agree on every row.
All124 witness pointers resolve to the intended records, and the displayed
words, lengths and ranks match those records exactly. All15 paths in
`shortening_witnesses.jsonl` independently replay; their selected source
pointers resolve to the exact saved rank-two or saved stable relators. No stale
pointer was found.

The final retained endpoint counts are **35 rank2,87 rank3 and2 rank4**.
The eleven length gains give **2191 → 2180**, and89 rows are shorter than their
saved rank-two starts, whose total is2356. No row is solved. The four additional
same-length rank4-to-rank3 witnesses are `aca_108`, `aca_112`, `aca_113` and
`aca_114`. The final `aca_80` witness also removes a generator after its rank4
length17 boundary, retaining length17 at rank3. Thus the original screen table
below and the final table intentionally have different endpoint-rank counts.

The selected17-row partial-basis follow-up also passes: all158 retained
candidate chains replay, including185 Lemma11 removals,456 whole-presentation
Whitehead maps and90 relator normalizations. Selected-subtuple tracking and
length changes are checked independently. None of their stored intermediate
boundaries is shorter than the retained incumbent. Its5,380 work units produce
zero additional gains.

This final review reused the independent event checker and did not repeat the
exhaustive mincut/word controls or run a census search. It is reproducible with
`audit.py --delivery-only`; the full default audit also includes the final
deliverable checks. `audit.json` preserves the initial screen audit and adds
`final_delivery_validation` and `partial_panel_validation` with final hashes.

## Saved reports

| Report | Rows checked | Newly shorter rows | Total length before → after |
|---|---:|---:|---:|
| `basis_all124.json` | 124 | 5 | 2191 → 2186 |
| `mixed_all124.json` | 124 | 11 | 2191 → 2180 |
| `ladder_all124.json` | 124 | 1 | 2191 → 2190 |

These are separate screens against the same frozen 2191 baseline. Their gains
must not be added. Every input tuple, signed-integer map, actual selected source,
stored event, final tuple, complete relator length, gain and charged-work sum
passes. The rank-two starts agree exactly with
`data/ms_unsolved_reps/aca_124_best.csv`. The source table and executed scripts
are pinned by their SHA-256 hashes.

The basis screen contains six defining compressions and six Whitehead events.
The mixed winners contain fourteen defining compressions, seven Lemma 11
removals, four ordinary AC substitutions and five Whitehead events. The ladder's
saved winning path contains one defining compression and one Whitehead event.

| Mixed gain | Selected start | Every saved boundary, shown as rank:length |
|---|---|---|
| `aca_7` | saved best | 2:16 → 3:16 → 2:17 → 3:15 |
| `aca_30` | saved best | 2:17 → 3:17 → 3:16 |
| `aca_31` | saved best | 2:17 → 3:17 → 2:17 → 3:16 |
| `aca_36` | saved best | 2:16 → 3:16 → 3:15 |
| `aca_57` | saved rank two | 2:19 → 3:18 → 3:17 |
| `aca_80` | saved rank two | 2:19 → 3:19 → 4:19 → 4:17 |
| `aca_82` | saved best | 3:20 → 4:21 → 4:20 → 3:19 |
| `aca_86` | saved best | 3:20 → 4:21 → 4:20 → 3:19 |
| `aca_102` | saved best | 3:21 → 4:21 → 3:21 → 3:20 |
| `aca_103` | saved best | 3:21 → 4:21 → 3:21 → 3:20 |
| `aca_104` | saved best | 3:21 → 4:21 → 3:21 → 3:20 |

`aca_57` and `aca_80` improve saved stable length18 to17, even though their
selected paths start at rank-two length19. In particular, `aca_80` genuinely
uses two length-neutral definitions before a whole-tuple Whitehead gain of two.
None of the retained winning paths has an earlier boundary shorter than its
reported endpoint.

The later `observed_pilot.json` and `observed_remainder.json` contain disjoint
sets of two and122 rows, exactly covering U124. The audit independently replays
both the best and maximum-rank witness for each row, and both witnesses in the
separate `observed_rank16.json`: **250 chains,588 stored events** including
repeated shared prefixes. All pass. The observer's pinned implementation checks
that its endpoint, per-kind costs, total budget and accepted-rank maximum agree
with the original search. Its recorded boundary minima add no further gain;
the total remains2180. No retained chain contradicts those extrema.

The `aca_108` maximum-rank witness retains all16 relators at total length44:

```
rank:    4   5   6   7   8   9  10  11  12  13  14  15  16
length: 21  22  24  26  28  30  32  34  36  38  40  42  44
```

This is concrete reachability evidence beyond rank6, including ranks10 and11.
It gives no additional shortening and contains singleton relators, so the
singleton-free rank bounds do not apply to that chain.

Observation was real additional work:124,000 units for the all124 frontier
validation plus1,000 for the separate `aca_108` ladder validation, **125,000
extra physical units**. These are separate from the original screen budgets;
they are not cost-free reuse or part of the audit's small word checks.

## What each event check establishes

For a definition, the audit checks the fresh signed-integer label, each exact
rotation cut, every positive and negative template expansion without free
reduction, the occurrence count, and the literal gain formula. `raw_after` must
contain the untouched new defining relator and exactly one template for every
old relator, including older defining relators. It then independently checks
normalization and the sum of **all** lengths.

For a Whitehead change, the recorded images must match its signed multiplier
and partition. Both compositions with the recorded inverse are checked on every
current generator, including negative letters. The map is applied to every
relator, with independent free and cyclic reduction. The graph cut formula is
checked against the resulting whole-tuple length. Optional target-relator and
normalization witnesses are checked when present.

For Lemma 11, the defining relator must contain the removed generator exactly
once. Its recorded signed conjugation must give `g^-1 w`, with `w` free of `g`.
Every surviving relator must appear once; both signs of `g` are substituted
literally, then independently reduced and normalized. The removed generator
must disappear, all other labels must be preserved, and rank must decrease by
one. The normal-form and canonicalization conjugators are independently replayed.

For ordinary AC substitution, the target and donor are distinct, both rotation
cuts and the donor sign are checked, the product is independently reduced, and
every other relator is retained. Canonical inversion, rotation and tuple sorting
are standard finite relator operations. All saved boundaries also have balanced
generator/relator counts and unimodular exponent matrices; these checks do not
replace the known-triviality hypothesis.

## Finite controls and the corrected cut flag

The executable controls pass:

- 2,544 minimum-cut comparisons over every non-isolated rank-two signed graph
  with edge capacities in `{0,1,2}`, using exhaustive partitions as the oracle.
- 17,616 signed word/partition checks of the Whitehead length formula. These
  cover every cyclically reduced word through length4 at ranks1 and2 and through
  length3 at rank3.
- Known trivial triangular tuples at ranks7,8 and12, each grown by two signed
  definitions to ranks9,10 and14; forward and inverse Whitehead maps also pass.
- Positive and negative Lemma 11 isolations at ranks8 and13. Surviving generator
  labels have gaps, and the audit verifies these without assuming labels remain
  consecutive after removal.

The preserved `whitehead_first_screen.py` hash is exactly the executed hash in
the basis report. Removing assignments used solely for `complete`/`scanned`
metadata makes its AST identical to current `whitehead.py`. `basis_search.py`
only stores `aut_minimal`; it never reads that field to choose candidates,
paths, budgets or endpoints. Thus no saved outcome depends on the old flag.

The concrete control `((1,), (2,1))` at seven cuts reproduces the issue: the old
code returns `complete=True`, the fixed code returns `False`, and their endpoint,
path and charged cut count are identical. Budgets six and eight agree completely.

## Theory review and certificate scope

The two-step bypass proof in `THEOREM_NOTE.md` is sound for **freely and cyclically
reduced literal boundaries**, with no intervening operations beyond the stated
rotations. In the helper-free case, occurrences inside the fresh donor lift into
one original replaced block, disjoint from occurrences in the compressed old
relators. In the helper-containing case, an occurrence of length at least two
inside the donor expands with cancellation at a helper seam; such a word cannot
also occur in a compressed old relator, whose expansion is a reduced cyclic
substring of an original relator. Two disjoint occurrences cannot both use the
donor's single helper letter. Hence all profitable second-step occurrences lift
to disjoint copies of one reduced original word, giving the claimed gain bound.

This proves existence of a direct compression with at least the combined gain.
It does not prove equal endpoints, a bypass for arbitrary longer sequences,
necessity of an initial neutral/uphill definition, or an obstruction after a
Whitehead/AC operation. The note's fixed-input potential and singleton-free rank
bounds are valid under their explicit full-rank and operation hypotheses; they
are not a universal rank ceiling across arbitrarily long inputs.

Lemma 11 in the supplied local paper, lines2499 onward, explicitly assumes a
presentation of the trivial group. Applying it to a tuple with a retained
defining relator justifies removal; reversing it justifies adding a definition.
Known triviality ensures the required finite normal-product identity exists.
The conventions' signed Nielsen/basis changes have finite stable realizations
by the same defining-generator argument. Unimodular abelianization alone would
not suffice, and neither the lemma nor this audit supplies an elementary
expansion-size bound.

Accordingly, these are **theorem-backed stable-composite certificates**. They
are not fully expanded elementary streams, ordinary rank-two solves, or new
proofs of triviality. Where a new path starts from `saved_best`, its previously
certified upstream path is accepted from the pinned source table and is not
re-expanded here.

The original reports retain only winning paths. The observer adds best and
maximum-rank chains and verifies decision invariance during its instrumented
runs; the audit independently replays those retained chains. Statements about
other unretained intermediate states still rely on the pinned observer record.
The explicit `aca_108` chain establishes rank16 reachability, while neither the
screens nor observation establishes a global optimum or exhaustive failure.

No callable general `advisor()` tool is available in this session. This audit
therefore records its independent reasoning and executable evidence directly.
