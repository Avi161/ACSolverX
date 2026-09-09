# Census run summary

Range: rows **[0, 72779)** of `data/AC19_extended_aut_min.csv` (72779 rows) -- policy **`K3p_c12aut`**, budget **1000**.

Solved: **72738/72779** (verified certificates: **72738**). Unsolved: **41**. Errors: **0** (fail-closed on any error row). Maximum observed per-row charge: **1000** (limit 1000).

Total charged units: **2829457**. Search wall/CPU: **172.364624s / 170.953699s**. Certificate wall/CPU: **203.093027s / 201.828342s**. Total elementary moves: **39130184**.

## Outcomes by policy route

| Route | Rows | Solved | Unsolved |
|---|---:|---:|---:|
| `ball_root` | 24708 | 24708 | 0 |
| `bs_demote` | 43 | 43 | 0 |
| `incumbent_restart` | 189 | 148 | 41 |
| `plain_s20` | 23424 | 23424 | 0 |
| `strict_donor` | 24415 | 24415 | 0 |

## Provenance

Input: `data/AC19_extended_aut_min.csv`, SHA-256 `7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2`. Source hashes cover 41 files under `research/supermoves_20260908/` and `research/residual_20260909/`; table hashes cover 6 pickle file(s) under `research/residual_20260909/tables/`, all recorded in the interval `manifest_*.json` files: manifest_00000_72779.json.
