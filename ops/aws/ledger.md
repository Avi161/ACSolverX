# AWS ledger (no secrets). Times UTC / ET. Spend estimate = hours x rate.

| instance | type | market | $/h | launched | purpose | max life | ended |
|---|---|---|---:|---|---|---|---|
| i-08ce3e49642b66e4b | m7i.16xlarge | spot (us-east-1a) | 1.202300 | 2026-11-03T05:10:32Z / 00:10 ET | Ryan CoV gates, 1e5 (done 05:15Z) then 1e6 on unsolved (OOM-killed 05:21Z; box idle until noticed) | 6 h | 2026-11-03T07:19:57Z (02:19 ET); 2.16 h x 1.20 = ~$2.60 |
| i-0ab47e420fe6669fe | r7a.16xlarge | spot (us-east-1a) | 1.903700 | 2026-11-03T07:23:39Z / 02:23 ET | Ryan CoV gates, 1e6 on the 171 searches unsolved at 1e5, 20 workers (success) | 4 h | 2026-11-03T07:43:36Z (02:43 ET); 0.33 h x 1.90 = ~$0.63 |

Total for the Ryan replication: about $3.25 (2.16 h + 0.33 h of spot).

## Elliot full-CoV rerun (5 Nov 2026)

| instance | type | market | $/h | launched | purpose | max life | ended |
|---|---|---|---:|---|---|---|---|
| i-0ad72d0b40767ec9c | c8g.48xlarge | spot persistent, stop on reclaim (us-east-1a, sir-akdfpi9j) | 2.193100 | 2026-11-05T20:55:22Z / 3:55 PM ET | Elliot's three searches with the full CoV family (benchmark/elliot/fullcov), MS640 / bench60 / ladder100, 10^3 to 10^7 | 12 h (request valid to 08:25Z, power-off 08:55Z 6 Nov) | not ended by this session: its key (claude-code-sair) may launch but not SendCommand, read the bucket, cancel the request or terminate; Truett asked to cancel sir-akdfpi9j and terminate (5 Nov 3:57 PM ET). Its results were never read (the rerun ran in the container instead). Spot-reclaimed to stopped at 2026-11-05T21:08:42Z (4:08 PM ET); Truett cancelled sir-akdfpi9j and terminated it in the console; terminated and no volume left at 2026-11-05T21:24Z (4:24 PM ET). Ran 0.22 h (20:55 to 21:08Z) x 2.19 = ~$0.48. |

## Full-CoV CoV-gate run (5 Nov 2026)

Key `claude-code-sair` (it can launch but not terminate, cancel spot requests or send SSM commands), instance profile
`acsolver-ec2`, results in `s3://acsolver-u124-205558941715/cov_full/run_5nov/`. The box runs
`ops/aws/userdata_cov_full.sh` at boot and powers itself off (shutdown terminates it) when the job ends, at once if S3
or pip fails, and at its 10 h timer at the latest. c8g.48xlarge and c8g.24xlarge spot had no capacity or would pass
the 300-vCPU spot quota (the Elliot thread's c8g.48xlarge holds 192).

| instance | type | market | $/h | launched | purpose | max life | ended |
|---|---|---|---:|---|---|---|---|
| i-04b5c27624d921fd7 | c8g.16xlarge | spot (us-east-1a, sir-i2vfm1wh) | 0.670400 | 2026-11-05T21:10:28Z / 4:10 PM ET | full-CoV CoV gate: all rows at 1e5 units, then unsolved at 1e6 | 10 h | job done 2026-11-05T21:52:36Z, powered itself off (terminated); about 0.7 h, ~$0.47. Its 1e6 records equal the numba rerun's on all 21 rows. |
| i-0b684365ee054b85b | r8g.8xlarge | spot (us-east-1b, sir-5asfn8ch) | 0.503300 | 2026-11-05T21:58:53.000Z / 4:58 PM ET | full-CoV CoV gate with the numba kernel (cov_full_numba.py): the 14 searches unsolved at 1e5, rerun at 1e6, 14 workers; run prefix cov_full/run_5nov_nb | 3 h || job done 2026-11-05T22:00:43Z, powered itself off (terminated); about 2 min, ~$0.02 |
