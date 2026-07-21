# [2026-07-20] Interrupting a notebook cell orphans the spawned workers — a re-run then double-computes every remaining row [TRAP]

On the 50k aca124 sweep (chunk c5of5), the heartbeat climbed past its own total — `2550/2276 rows | … | ~1m left` — while every beat still burned real nodes. Interrupting the RUN cell had killed only the parent join-loop; the 8 spawned fine-chunk workers survived as orphans and kept appending. Re-running the cell launched 8 new workers over the same files, and each fleet, having snapshotted its resume set at its own start, computed the same remaining rows: unique-key audit showed 2,129 unique rows under ~2,573 lines, i.e. ~444 rows written twice — about half that session's compute wasted. The ETA stayed pinned at "~1m" because `total - done` had gone negative.

Two defects, two fixes (both in `experiments/stable_ac/cov/run_cov.py`):

1. `_scan_rows` counted raw jsonl lines, so duplicate appends inflated the heartbeat past the chunk total. It now dedupes by the sweep row key `(pres_id, z_word, iso_gen, iso_index)` within each file — the heartbeat and ETA follow unique rows only.
2. Nothing arbitrated file ownership. `_claim_out_path` (called by both runners before `_repair_jsonl`) now takes an exclusive `flock` on `<out_path>.lock` for the process lifetime. The kernel releases a dead process's flock automatically, so a *live* holder is by construction a superseded run's worker: the claimant reads the holder's pid from the lock file and SIGKILLs it, then takes the file. A kill mid-append leaves at most a torn tail, which `_repair_jsonl` (run right after the claim) removes.

Data was never at risk — resume (`_read_done_pairs`) and the coarse fold-back (`_backfill_coarse`) already dedupe by key — the loss was throughput and a lying progress display. `nocov/run_nocov.py` has the same exposure and no claim yet.

**Rule:** a spawned worker fleet needs an ownership claim on its output file (flock: self-releasing on death, live holder ⇒ orphan ⇒ kill), and any progress counter derived from an append-only file must count unique row keys, never lines.
