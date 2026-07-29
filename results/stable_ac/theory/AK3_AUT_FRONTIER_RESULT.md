# Bounded AK(3) Aut(F2)-image exact-complex census

## Frozen bound

- Maps: 1000
- Exact cellular keys: 285
- Ordered memberships: 3000

## Spelling-mode membership histogram

| Value | Count |
| --- | ---: |
| `cyclic` | 1000 |
| `free` | 1000 |
| `literal` | 1000 |

## Exact support histogram

| Value | Count |
| --- | ---: |
| `C4` | 6 |
| `K4` | 6 |
| `K4-e` | 33 |
| `K4-e+1loop` | 6 |
| `P4` | 16 |
| `UNSUPPORTED` | 200 |
| `paw+1loop` | 18 |

## Verdict histogram

| Value | Count |
| --- | ---: |
| `NOT_SPHERICAL_EXACT` | 35 |
| `PRIOR_EXACT_DUPLICATE` | 50 |
| `SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION` | 0 |
| `UNSUPPORTED` | 200 |

## Exact source hashes

- `results/stable_ac/theory/ak3_aut_frontier_manifest.json`: `96b710a0fd53e56c53c42e8bcd203286d98a982a735ec2d42fa9b4b856fd816a`
- `experiments/stable_ac/thickenable/ak3_aut_frontier_certificate.py`: `58b5c2395125971179c68c4cfb37473b25fefa86234183aec08fb8c8a9a372b1`
- `results/stable_ac/theory/ak3_neuwirth_census.json`: `716019daf3f61a290fcec1608a5042cfa2da72f25f0719b115a463e8fea52710`
- `results/stable_ac/theory/ak3_component_thickenability.json`: `a64f8cdf396a7fcc0d5bdf0a49542078da69e5e43c05dd64b5d9b1251539d96f`
- `results/stable_ac/theory/ak3_cov_thickenability.json`: `db14ff6417610f212e847f7c3a2eda479ab49bac92fc2f1f9c242807bfbfb6cc`
- `results/stable_ac/theory/ak3_two_hop_cov_thickenability.json`: `06e113537ca6cae07763a94f8aae0bb1b91edc30710fccea814bb2a2c70f0400`
- `results/stable_ac/theory/ak3_primitive_quotient_thickenability.json`: `38a49708989e6a06542106f980885f5c3745093e5d87a73285d7fb2ae2902bab`
- `experiments/stable_ac/thickenable/neuwirth_rank_solver.py`: `5f5e0587e9f9b605c53412d9e5ab793d6823a9b67c87589a06d9ab36ada2c5cb`
- `experiments/stable_ac/thickenable/neuwirth_p4_solver.py`: `2c0b80038da936146264eccc3df31464bff1011fafbd1aa19c27569062ca421e`
- `experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py`: `5962751e54d3adc94da64ba6c3db1d4236f3999298ea27b39f7b992d36ac30fc`
- `experiments/stable_ac/thickenable/neuwirth_paw_one_loop_solver.py`: `20ed3de02d4b2d544af87b1d0a923c62060c1b5f76a62cb4782a300efb2644ee`
- `literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md`: `cd829d5899235a70441497a579c3c65647882376d61511e2af27a980c4a1fe9b`
- `literature/proofs/AK3_P4_SYNCHRONIZED_PLANARITY.md`: `04003737e20c6741ab867fd6822f6b9a56b8f266e83d57d0e9bd29ba6adfaf97`
- `literature/proofs/AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md`: `96952a15b3abf745d1553334a8790566b7dc9f71ca5907c05ac04a37b2b6aeaa`
- `literature/proofs/AK3_PAW_ONE_LOOP_PLANARITY.md`: `25443f6e87313872b3e0c0d9db8422107ce3dd91572887431d58c6b27ab58413`

## Quarantined spherical row IDs

- None

## Proof limits

- This is a finite census of the frozen 1,000-map BFS prefix, not an Aut(F2) orbit closure or saturation theorem.
- Each negative applies only to its exact stored spelling; unsupported rows are not negative results.
- This is not an AC search, and no row proves an AC or stable-AC counterexample.
- Every spherical row is quarantined pending an independent exact neighborhood and 3-ball validation; it is not a thickenability, Lackenby, AC, or stable-AC result.
