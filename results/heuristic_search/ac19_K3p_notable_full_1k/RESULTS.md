# Census run summary

Range: rows **[0, 72779)** of `data/AC19_extended_aut_min.csv` (72779 rows) -- policy **`K3p_notable`**, budget **1000**.

Solved: **72562/72779** (verified certificates: **72562**). Unsolved: **217**. Errors: **0** (fail-closed on any error row). Maximum observed per-row charge: **1000** (limit 1000).

Total charged units: **5871522**. Search wall/CPU: **840.065828s / 815.307006s**. Certificate wall/CPU: **213.326186s / 206.466162s**. Total elementary moves: **39976689**.

## Outcomes by policy route

| Route | Rows | Solved | Unsolved |
|---|---:|---:|---:|
| `bs_demote` | 427 | 427 | 0 |
| `incumbent_restart` | 2672 | 2455 | 217 |
| `plain_s20` | 41644 | 41644 | 0 |
| `strict_donor` | 28036 | 28036 | 0 |

## Provenance

Input: `data/AC19_extended_aut_min.csv`, SHA-256 `7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2`. Source hashes cover 44 files under `research/supermoves_20260908/` and `research/residual_20260909/`; table hashes cover 8 pickle file(s) under `research/residual_20260909/tables/`, all recorded in the interval `manifest_*.json` files: manifest_00000_72779.json.
