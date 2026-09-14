# AC word kernel independent audit

Status: **pass**.

Subject SHA-256: `2ebb847b2e2d8cdf997ae2256255857bce8ed4106a228f3caa22a093e56a07aa`.

86,109 deterministic checks; 161 freely reduced words through length four, all 25,921 short-word products, and 512 seeded factor products.

The independent oracle removes inverse adjacent pairs by repeated string replacement; it does not call the subject's word helpers. Emitted moves are replayed independently and must use only inversion, right multiplication by the other relator, and single-generator conjugation.

## Ledger derivations

u=wA; v=wB; U=uC=wAC; V=vD=wBD. Thus U^-1 V=C^-1 A^-1 B D.

For U=U' s and V=V' s, U'^-1 V'=s(U^-1 V)s^-1. Each c^-1 R^e c becomes (c s^-1)^-1 R^e(c s^-1).

## Coverage

| Check | Count |
|---|---:|
| all_raw_short_canonicalizations | 341 |
| all_raw_short_reductions | 341 |
| all_short_products | 25921 |
| canonical_word | 161 |
| common_suffix_ledger | 512 |
| critical_pair_ledger | 512 |
| cyclic_witness | 161 |
| emitted_operation_alphabet | 12294 |
| factor_context_conjugation | 512 |
| factor_inverse | 512 |
| factor_inverse_cancellation | 512 |
| factor_simplification | 512 |
| free_reduced_word | 161 |
| independent_replay | 12294 |
| invalid_elementary_operation | 29 |
| invalid_factor_conjugator | 7 |
| invalid_factor_sign | 9 |
| invalid_replay_pair | 4 |
| invalid_trace_target | 35 |
| inverse | 161 |
| legacy_replay | 32 |
| random_factor_product | 512 |
| single_factor_expansion | 5474 |
| strict_replay | 12294 |
| suffix_factor_transport | 512 |
| trace_state | 12294 |

Legacy cross-check: 32 emitted streams, using the unchanged AST-extracted `replay_elementary` body and an independent reducer for initial normalization. No legacy module imports or JIT.

Measured audit wall/CPU: 0.339249/0.338813 seconds.

## Findings

No failures in the declared checks.

Audit findings corrected by the implementation owner before this final run:

- Factor(0, '') expanded as donor inverse but appended as donor; strict constructor validation now rejects it, booleans, and noninteger signs.
- Trace methods accepted some negative or boolean targets; every operation now checks integer target 0 or 1.
- replay([], []) accepted zero relators; replay now requires exactly two.

Finite bounded verification and elementary free-group derivations; no presentation search, census experiment, or performance conclusion.
