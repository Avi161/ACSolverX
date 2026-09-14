# Direct completion of saved two-complement bases

**All 15 full-join snapshots now have verified marked kernel bases.** This directly completes the14 former image-budget failures and preserves the earlier aca_116 basis. No heap or candidate search was rerun. The deterministic completion uses **117 Nielsen word-image operations**, followed by30 projection images. Every basis path, inverse and raw projected endpoint passes the existing independent integer checker.

The resulting canonical projected lengths range from20 to51. Every projection is longer than its original U124 input, and none is an exact cyclic/inverse/permutation return. This run finds **zero original-input gains and zero solves**. It does not compare all full Aut orbits; the earlier independently certified Aut distinction for aca_116 remains recorded in the frozen prototype report.

| Input | Original total | Raw projected total | Canonical projected total | New Nielsen word operations |
|---|---:|---:|---:|---:|
| aca_116 | 14 | 21 | 21 | 0 |
| aca_1 | 15 | 29 | 29 | 5 |
| aca_30 | 17 | 29 | 27 | 4 |
| aca_55 | 18 | 33 | 33 | 6 |
| aca_80 | 19 | 39 | 39 | 8 |
| aca_82 | 22 | 51 | 49 | 12 |
| aca_109 | 23 | 30 | 30 | 11 |
| aca_101 | 25 | 49 | 49 | 11 |
| aca_117 | 14 | 20 | 20 | 4 |
| aca_9 | 15 | 22 | 22 | 4 |
| aca_67 | 20 | 35 | 33 | 11 |
| aca_86 | 22 | 51 | 51 | 12 |
| aca_106 | 21 | 39 | 37 | 11 |
| aca_54 | 19 | 26 | 26 | 9 |
| aca_5 | 19 | 38 | 38 | 9 |

## Unit-lift completion lemma

Let f:F_m->F_n be a marked homomorphism, and suppose the current image tuple of a verified domain basis contains n distinct rows whose images are the signed target basis generators. Invert those rows when necessary. Keep these n rows fixed. For any other row with image beginning in a letter `g^epsilon`, left-multiply its domain word by the corresponding fixed lift row to exponent `-epsilon`. The image loses exactly its first letter. Repetition makes all m-n other images empty while preserving a free domain basis at every step. Only elementary Nielsen row moves are used.

For the present m=4,n=2 case, a slightly broader structural condition is sufficient: one row has image `x^±1`, while a different row contains y or Y exactly once. Because its other letters are x/X, the latter image has the freely reduced form `x^p y^epsilon x^q`. Normalize the first unit's sign, remove the prefix using left multiplication and the suffix using right multiplication by that fixed x row, and normalize epsilon. This yields literal x,y lift rows. The same argument works with x,y interchanged. These are actual row operations; no independent ambient conjugation is hidden in the prefix/suffix stripping.

Every multiplication strictly lowers the natural number given by total noncyclic image length by exactly one. Sign normalizations and final row permutation preserve it and occur only finitely. Thus the compiler terminates with images `(1,1,x,y)`. If L is the initial image total, it uses exactly `L-2` multiplications plus at most two sign inversions. The implementation computes this exact cost before doing any word transformation beyond input validation, and checks the estimate against the emitted operations.

The domain basis is changed by exactly the same operations. Its inverse is recovered from the reversed inverse row-operation list, and both inverse compositions are checked. Projecting the two kernel rows by killing original coordinates r,s gives the new balanced tag pair. Unimodularity is checked independently on every resulting pair.

## Stable interpretation and costs

The marked kernel basis is a basis of F4 with images `(1,1,x,y)`. On these known trivial-group inputs, the independently reviewed bridge through `(r,s,W1,W2)` proves stable AC equivalence between the original pair and the projected pair. The displayed bridge has rank4; the established stable realization of its ambient basis change may need rank5 internally. No ordinary equivalence is claimed. Exact inverse markings, both full bases, raw projections and canonicalization witnesses are saved for all15 cases.

This continuation intentionally keeps the prior search and compiler costs separate. The largest prior-candidate plus direct-completion plus projection total is **1014**, so it is **not** a new shared1k search result. Ordinary generator-level canonicalization adds225 operations over the15 pairs; including those operations gives a maximum combined count1047 for one row. These totals describe the registered work and do not bound the unexpanded stable ambient/normal-product macro. Root's separate early-unit gate can use the exact estimate to stop candidate exploration before these compiler costs are incurred.

For aca_116 this direct pass adds no Nielsen moves; it simply validates the already complete basis and projects it again, counting those two projection images in this separate compiler record. Its earlier16-pop Q21->18 ordinary continuation belongs to the frozen prototype continuation and is not rerun here.

## Structural terminal observations

All30 cyclic projected words contain both signs of at least one generator. Hence none has the cyclic rank-two primitive-word form, and none is a two-block power word. There is one literal consecutive-BS donor, in aca_54:

`Q=(XXXXyxxYXXY, XXXXXXXYxxxxxxy)`.

The second relator is a rotation of `Y x^6 y X^7`, so it is BS(6,7) with base x and stable y. The companion's stable exponent is-1. Its two cyclic opposite-sign gaps are `y x^2 Y`, requiring divisibility by7, and `Y x^-4 y`, requiring divisibility by6. Both fail, so the companion already has cyclic Britton length3 and this recognition is not a terminal certificate. No rewrite or primitive search is performed.

## API and verification

`recognize_unit_lifts(images)` returns the selected rows and exact `word_operations` estimate, or None. Its `word_operations_including_projection` is that estimate plus2. `plan_unit_completion(images)` returns every row operation, every image boundary, the final marked images and the exact operation count. `complete_snapshot(initial_images,snapshot,plan=None)` applies the same plan to the saved domain basis and returns the full marked basis, inverse and concatenated Nielsen row path. Projection remains a separately charged operation. A caller can reserve the estimate before generating a plan, then reserve two more images for projection.

`finish_all_existing_verified_bases(source_report)` is the saved-record batch entry point. It invokes neither the old heap nor any terminal search. Four planted plans cover both axes, both signs, existing empty rows and a single-occurrence non-unit lift; an independent integer implementation replays every planned image state. Two negative structural recognizers and four canonicalization controls also pass. Full saved-record verification takes about 0.0138 CPU seconds.

Module SHA-256: `f9ac216e709c886f6cd84d9eb441ba418d3eea7aeff2503c3a847a4545759603`. Frozen source-report SHA-256: `2fcdcbc1368e508c6f85174488eb233b8740734cefee7e894935190833ade3f0`. The prototype and independent-checker hashes are separately pinned in the JSON report. Each canonical projected relator carries its explicit sign and conjugator, and each row retains its exact source snapshot and original candidate count.
