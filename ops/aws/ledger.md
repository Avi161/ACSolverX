# AWS ledger (no secrets). Times UTC / ET. Spend estimate = hours x rate.

| instance | type | market | $/h | launched | purpose | max life | ended |
|---|---|---|---:|---|---|---|---|
| i-08ce3e49642b66e4b | m7i.16xlarge | spot (us-east-1a) | 1.202300 | 2026-11-03T05:10:32Z / 00:10 ET | Ryan CoV gates, 1e5 (done 05:15Z) then 1e6 on unsolved (OOM-killed 05:21Z; box idle until noticed) | 6 h | 2026-11-03T07:19:57Z (02:19 ET); 2.16 h x 1.20 = ~$2.60 |
| i-0ab47e420fe6669fe | r7a.16xlarge | spot (us-east-1a) | 1.903700 | 2026-11-03T07:23:39Z / 02:23 ET | Ryan CoV gates, 1e6 on the 171 searches unsolved at 1e5, 20 workers (success) | 4 h | 2026-11-03T07:43:36Z (02:43 ET); 0.33 h x 1.90 = ~$0.63 |

Total for the Ryan replication: about $3.25 (2.16 h + 0.33 h of spot).
