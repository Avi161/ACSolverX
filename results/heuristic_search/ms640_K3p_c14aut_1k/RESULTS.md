# Census run summary

Range: rows **[0, 640)** of `research/residual_20260909/panels/ms640.csv` (640 rows) -- policy **`K3p_c14aut`**, budget **1000**.

Solved: **640/640** (verified certificates: **640**). Unsolved: **0**. Errors: **0** (fail-closed on any error row). Maximum observed per-row charge: **267** (limit 1000).

Total charged units: **13082**. Search wall/CPU: **1.578409s / 1.575768s**. Certificate wall/CPU: **2.008530s / 2.006020s**. Total elementary moves: **653656**.

## Outcomes by policy route

| Route | Rows | Solved | Unsolved |
|---|---:|---:|---:|
| `ball_root` | 550 | 550 | 0 |
| `bs_demote` | 24 | 24 | 0 |
| `plain_s20` | 62 | 62 | 0 |
| `strict_donor` | 4 | 4 | 0 |

## Provenance

Input: `research/residual_20260909/panels/ms640.csv`, SHA-256 `5ca1f7911cdfc76c643b0722369f51f61270f67e11633bd522c4bda21a907667`. Source hashes cover 44 files under `research/supermoves_20260908/` and `research/residual_20260909/`; table hashes cover 8 pickle file(s) under `research/residual_20260909/tables/`, all recorded in the interval `manifest_*.json` files: manifest_00000_00640.json.
