# Independent early-unit gate and stable suffix audit

PASS. No search was rerun. All 18 marked bases, both inverse compositions, literal original/projection joins, and fully elementary suffixes pass independent integer replay. There are no solves and no strict original-input length gains.

| Cohort | Marked rows | Prefix units | S20 pops | Combined | Elementary moves | Checkpoint boundaries |
|---|---:|---:|---:|---:|---:|---:|
| Fixed x,y² panel | 15 | 4224 | 10776 | 15000 | 4227 | 150 |
| Selected x,y³ follow-up | 2 | 141 | 1859 | 2000 | 1437 | 60 |
| Prepared-frame Euclidean x,y² | 1 | 28 | 972 | 1000 | 430 | 14 |

Every completed attempt consumes exactly 1000 declared heterogeneous units. The q³ and Euclidean attempts are separately authorized attempts; this is not a claim of cumulative 1000 work across earlier experiments. Independent proof replay and source verification are additional work.

## Cost and termination audit

The gate preserves the frozen candidate order, normalizes only by relator inversions and permutations, and checks unit lifts at a popped state and each normalized generated child before deduplication. Each candidate reserves two units before its multiplication image and inverse-comparison image are formed; four initial inverse comparisons are also charged. No saved searched row hit a word-length guard. All 17 successful searched gates occur at generated children; the Euclidean gate uses its explicit direct construction.

The compiler first makes its two selected lifts literal positive units. Every multiplication removes exactly one image letter, so there are L−2 multiplications, where L is the unit-gate input image length, plus at most two sign inversions. With the two kernel projections this gives an exact reservation before planning or completion. All 367 compiler updates and 36 projections replay with the declared costs. Four threshold controls confirm that a one-unit-short reservation neither invokes the compiler nor spends its reserved work. These controls do not run a candidate search.

The Euclidean attempt first inverts original relator 2 and swaps ambient x,y, with both whole relator images checked. It charges these three preparation operations and four initial image words, then the seven recorded updates s←s t⁻⁴ u³ expose the literal image Y because the prepared second relator is y⁻⁷x⁴ and f(u)=y². The exact saved left-clearing compiler marking, rather than a different theoretically possible basis, is replayed. Its twelve compiler updates and two projections give prefix charge 28, leaving 972 S20 pops. No Nielsen candidate search occurs in this prefix.

## Stable bridge and ordinary suffix

The original P is taken from the pinned known-trivial Miller–Schupp census. The Euclidean row first uses its explicit inversion and axis swap to obtain a prepared P. For each declared complement (x,y²) or (x,y³), replay verifies an F₄ basis B=(W₁,W₂,Vₓ,Vᵧ), its two-sided inverse, and f(B)=(1,1,x,y). Killing original r,s in W₁,W₂ gives the literal raw Q. Killing the first two new coordinates in the inverse basis recovers the literal P used by that gate. These are precisely the hypotheses of the separately audited two-complement bridge.

The balanced rank-four tuple (r,s,W₁,W₂) is known trivial by the quotient identification before the stable ambient-basis lemma is used. Unit elimination connects it to Q; the ambient basis change followed by kernel-unit elimination connects it to P. This certifies stable equivalence, potentially using a fifth helper generator. It does not certify ordinary equivalence from P or bound all internal stable word lengths. The generating image tuple (1,1,x,y) is not a balanced rank-two presentation and is never counted as a solve or length-two state.

From raw Q, each suffix uses only relator inversion, right multiplication by the other current relator, or conjugation by one signed generator. The independent checker evaluates all intermediate words and both-relator length sums, including temporary donors, initial canonicalization and swaps. Every saved search boundary is checked at its exact elementary move index. All elementary minima equal the corresponding saved endpoint length; no hidden temporary state improves an original input.

## Exact retained minima

| Input | Complement exponent | Original length | Raw Q length | Minimum ordinary suffix length | First minimum move |
|---|---:|---:|---:|---:|---:|
| aca_116 | 2 | 14 | 20 | 15 | 815 |
| aca_1 | 2 | 15 | 19 | 15 | 4 |
| aca_30 | 2 | 17 | 23 | 17 | 35 |
| aca_55 | 2 | 18 | 23 | 23 | 0 |
| aca_80 | 2 | 19 | 26 | 21 | 49 |
| aca_82 | 2 | 22 | 51 | 34 | 158 |
| aca_109 | 2 | 23 | 30 | 30 | 0 |
| aca_101 | 2 | 25 | 49 | 34 | 152 |
| aca_117 | 2 | 14 | 20 | 19 | 456 |
| aca_9 | 2 | 15 | 22 | 19 | 160 |
| aca_67 | 2 | 20 | 42 | 30 | 49 |
| aca_86 | 2 | 22 | 51 | 34 | 242 |
| aca_106 | 2 | 21 | 46 | 32 | 63 |
| aca_54 | 2 | 19 | 27 | 19 | 815 |
| aca_5 | 2 | 19 | 43 | 19 | 819 |
| aca_115 | 3 | 13 | 22 | 13 | 250 |
| aca_59 | 3 | 20 | 41 | 20 | 1165 |
| aca_59 | 2 | 20 | 60 | 21 | 413 |

## Admission API and provenance

`verify_prefix(gate_row, certificate, search_row=None)` returns the independently replayed minimum with `relators`, `rank`, `total_length`, `minimum_move_index`, endpoint, complete intermediate total-length ledger, `independently_verified`, and `stable_bridge_verified`. Supplying the search row additionally checks all captured boundaries, endpoint metadata and shared-budget arithmetic. Callers must pin the containing reports and join the original P to the known-trivial census. The JSON ledger supplies report/certificate hashes, row/line indices and the exact original input for that join.

The q³ and Euclidean certificates do not carry a source pointer individually. The audit supplies that missing provenance link by verifying raw Q against the same-name marked witness and hashing both whole artifacts. This is a metadata qualification, not a missing algebraic certificate. The Euclidean certificate is a single JSON object; all other certificates are JSONL. Each minimum declares its certificate format. The same verify_prefix API accepts all three cohorts and checks the explicit prepared-input bridge when present.

The integer bridge checker dependency is the frozen independent `two_complement_probe_checks.py`; the ordinary word stack is implemented directly in this audit. The current gate code is imported only for four reservation controls, with no heap or search execution. Negative claims remain bounded saved-prefix outcomes.

Auditor SHA-256: `eb6c3f98b530b1e85ad119277601de4f02efbe31ac19594802909fda0081d2b1`.
Audit CPU: 0.036460 seconds. Source hashes and the full intermediate length ledger are in the companion JSON.
