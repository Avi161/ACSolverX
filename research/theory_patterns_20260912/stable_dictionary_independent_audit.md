# Independent stable dictionary audit

Status: **PASS.** All **84 saved strict prefixes** independently expand to their exact cyclically rotated inputs. The full 124-row starting total is **2,356**, and the certified minimum total including starts is **2,199**, a reduction of **157**. All three rank-three relators, including the definition, are counted. These records assert zero rank-two endpoint gains and zero solves.

## Exact certificate and length identity

For a reduced old word `w`, put `D = Z w`, where `Z = z^-1`. The stored target is exactly `(D,C1,C2)`. For each original relator, the audit checks its cut index and the **unreduced literal equality** obtained by replacing every `z` in its template by `w`, and every `Z` by `w^-1`. This proves that the signed occurrences are disjoint and fixes every sign and cyclic cut. It is stronger than equality only after free reduction. The auditor also checks that all three displayed words are freely reduced.

Writing `l = |w|`, `L` for the original total length and `M` for the total number of `z`/`Z` tokens in `C1,C2`, each replacement saves exactly `l-1` letters. Hence

`L' = L + l + 1 - M(l-1)`.

The audit checks this identity separately on all 84 prefixes. A strict gain is exactly `M(l-1) > l+1`; no claim of a rank-two gain follows.

Known triviality of the original Miller–Schupp input implies `w` lies in the normal closure of its relators. Starting from one ordinary stabilization `(z,z)`, invert the new relator and multiply it by a finite product of conjugates of old relators to produce `D = z^-1 w`, restoring every old donor. This is the established stable-definition lemma in `STABLE_CERTIFICATE_CONVENTIONS.md`; the normal-product expansion is not emitted here.

The subsequent literal compressions are exact ordinary AC operations with `D` restored. For a positive occurrence `P w Q = P z D Q`, right multiplication by `Q^-1 D^-1 Q` gives `P z Q`. For a negative occurrence `P w^-1 Q = P D^-1 Z Q`, right multiplication by `(ZQ)^-1 D (ZQ)` gives `P Z Q`. A cyclic cut after prefix `P` is conjugation by `P^-1` on the left and `P` on the right. Thus every displayed rank-three target is justified by a finite stable prefix, with the defining relator retained throughout compression.

## Audit scope and budget units

The checker imports neither the author verifier nor its enumerator. It validates exact input order and words against the hash-pinned 124-row best CSV, author/report hashes, every positive prefix, all aggregate lengths and the gain-ID list. Six corruptions are rejected: false length, omitted definition, wrong rank, boolean cut, altered template, and inverted defining word. Runtime was 0.0027 CPU seconds.

The source reports 15,814 defining-word candidates, at most 217 per input. One such unit includes two cyclic-compression optimizations; it is not one elementary AC operation, individual word image or dynamic-program transition. The finite normal-product realization of the stable definition is not emitted or included in this count. Rows without saved positives were checked for provenance and accounting only; the audit does not establish optimality under arbitrary stable AC or hidden-cancellation compression.

## Adapter API

`stable_dictionary_independent_audit.py` exposes `verify_prefix(input_pair, witness)`. It returns the complete verified boundary with `relators`, `rank`, `relator_lengths`, `total_length`, `independently_verified: true`, token counts, literal occurrence intervals and the checked formula length. It raises on malformed or incorrect data. The JSON ledger records all 124 rows, separates rank-two minima from rank-three witnesses, and provides exact source JSON pointers.

Source report SHA-256: `d40ef3d5b18237882a5515025a405c795b442ebf6c60376f7a86de29c808e7f3`. Auditor SHA-256: `a25f45a4335d921f2197f76821f5fda2226faa01fb05d790ea2aed842cc5f0d7`. Source CSV SHA-256: `8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3`. The author script and stable-certificate conventions are separately hash-pinned.
