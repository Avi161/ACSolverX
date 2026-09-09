# Census run summary

Range: rows **[0, 72779)** of `data/AC19_extended_aut_min.csv` (72779 rows) -- policy **`K3p_c14aut`**, budget **1000**.

Solved: **72779/72779** (verified certificates: **72779**). Unsolved: **0**. Errors: **0** (fail-closed on any error row). Maximum observed per-row charge: **699** (limit 1000).

Total charged units: **949521**. Search wall/CPU: **46.717706s / 46.049150s**. Certificate wall/CPU: **186.177533s / 184.666068s**. Total elementary moves: **42304643**.

## Outcomes by policy route

| Route | Rows | Solved | Unsolved |
|---|---:|---:|---:|
| `ball_root` | 66151 | 66151 | 0 |
| `incumbent_restart` | 7 | 7 | 0 |
| `plain_s20` | 2113 | 2113 | 0 |
| `strict_donor` | 4508 | 4508 | 0 |

## Provenance

Input: `data/AC19_extended_aut_min.csv`, SHA-256 `7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2`. Source hashes cover 42 files under `research/supermoves_20260908/` and `research/residual_20260909/`; table hashes cover 8 pickle file(s) under `research/residual_20260909/tables/`, all recorded in the interval `manifest_*.json` files: manifest_00000_72779.json.
