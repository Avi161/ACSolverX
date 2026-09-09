# AC19 final policy census

Verified coverage: **72052/72779** (verified certificates: **72052**).

Unsolved: **727**. Errors: **0**. Maximum observed per-row charge: **1000** (limit 1,000).

Policy budget: **1,000 heterogeneous charged units per row**; ordinary relator cap: **none**. These units are not calibrated as CPU-equivalent heap pops.

Total charged units: **6621411**. Search wall/CPU: **389.168448s / 385.598848s**. Certificate wall/CPU: **109.443121s / 108.547102s**.

Summed invocation elapsed time: **1976.135233s**, including **1471.091069s** recorded cooldown and excluding warmup. Warmup wall time: **9.115781s**; elapsed plus warmup: **1985.251014s**. Search and certificate clocks report compute phases separately.

## Outcomes by policy route

| Route | Rows | Solved | Unsolved |
|---|---:|---:|---:|
| `incumbent_restart` | 1338 | 612 | 726 |
| `plain_s20` | 43406 | 43405 | 1 |
| `strict_donor` | 28035 | 28035 | 0 |

## Provenance

Input: [`data/AC19_extended_aut_min.csv`](../../../data/AC19_extended_aut_min.csv), SHA-256 `7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2`. Runtime source hashes are recorded in the interval `manifest_*.json` files and checked against [`FINAL_PORTABILITY_CHECK.json`](../../../research/supermoves_20260908/FINAL_PORTABILITY_CHECK.json). The algorithm and reproduction commands are in [`AC19_FULL_CENSUS_ALGORITHM.md`](../../../research/supermoves_20260908/AC19_FULL_CENSUS_ALGORITHM.md).
