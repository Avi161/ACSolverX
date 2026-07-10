# [2026-07-09] A hole in the jsonl is a lost *result*, never a raced *write* [TRAP]

## What happened

A 1M-budget `HIGH_SPEEDUP` run over `ms_reps_unsolved.txt` finished presentations 0-6 and
9-14, but the jsonl had **no rows for 7 and 8**. The natural reading — three workers running
concurrently, so the parallel dump must be racing — is wrong, and chasing it wastes the run.

## Why a write race is impossible here

`out_f.write(...)` lives at `run_baseline.py:946`, inside `_emit`, which is a **closure defined
in `run_dataset`** — i.e. the parent. `_solve_one` (the worker) computes stats and *returns*
them; the only file it ever opens is the optional `hb_stack_<pid>.txt` debug dump. Every row is
serialized through one parent-side handle, `write` + `flush` per row, opened `"a"` (`O_APPEND`).
There is exactly one writer.

Verified at budget 1,000 (never higher — see [local-run-budget-cap](local-run-budget-cap.md)):
3 forked workers, 12 presentations → `rows=12 order=[0,1,2,3,5,4,6,7,8,9,10,11] missing=[] dupes=0`.
Rows arrive out of order (that is `imap_unordered`, and it is normal); none are lost.

A second consequence: the file is **append-only**, so a Drive/FUSE sync lag can only ever
truncate the *tail*. A hole in the middle can never be a stale read.

Scope of that proof: it ran on **local disk**. It shows the *runner* never loses a row. If a
hole ever survives a `tail` taken from inside the Colab VM — with the `[budget] k/n | pres P`
completion lines present, which print *after* `_emit`'s flush — then the runner is exonerated
and the Drive FUSE layer is the only remaining suspect. Check the file before concluding.

## The two things that can produce a hole (mechanism: leading hypothesis, not established)

What is *proven* below is that the write path cannot lose a row, and that each mechanism here
would produce exactly this symptom. Which one fired in the original run was never confirmed —
its console was gone. Do not read this as a post-mortem; read it as the two places to look.
The recommendation (fewer workers) is robust either way, since both are memory-driven.

**1. A pool worker dies and its task is silently dropped.** `mp.Pool.imap_unordered` does not
detect worker death (unlike `concurrent.futures`, which raises `BrokenProcessPool`). The pool
*repopulates*, so later presentations keep completing at full throughput — and the dead worker's
result never arrives, so the iterator blocks forever once the last job is dispatched. Repro:

```python
pool = mp.get_context("fork").Pool(3)
it = pool.imap_unordered(work, range(6))   # work(1) SIGKILLs itself
# -> yields [0, 2, 3, 4, 5]; never raises StopIteration. HANG.
```

That is the exact signature: a hole at the killed ids, normal progress after, a hang at the end.

**2. The memory guard cannot prevent it at 1M.** `_MemGuard`'s soft threshold is
`avail * 0.90 / n_workers`. With the observed `53 GB usable / 3 workers` that is **15.9 GB**,
while one 1M/`mrl48` search peaks at **~14.4 GB** (`_est_gb_per_pres`). The guard therefore
*never fires* — and `3 x 14.4 = 43.2 GB` plus the parent (wandb, Drive FUSE) is close enough to
53 GB that the kernel OOM killer acts first. The guard protects against **one** worker
overshooting its share; nothing protects against **n** workers each sitting at their expected
peak. That is a sizing decision, not a guard decision.

## The diagnostic that settles it in one line

Compare what the runner reports against what is on disk:

```
=== budget=1000000 | 261 presentations | 12 already done, 249 to run
$ wc -l greedy_1000000_261_mrl48_cyc_all_*.jsonl     # -> 13 rows
```

`12 != 13` means `_repair_jsonl` dropped an un-newline-terminated final line — the fingerprint
of the previous run being **hard-killed mid-write** (OOM, disconnect). It re-runs that one
presentation, which is why `todo` began `[7, 8, 12]`. Reproduced exactly: 13 rows on disk,
final row complete JSON with no trailing `\n` → `_read_done` sees 12 → `missing = [7, 8, 12]`.

Note the corollary: the completion line `[budget] k/n | pres P: ...` is printed **after**
`_emit()` has written and flushed. If you see that line for a presentation, its row *is* on
disk. Do not diagnose from a jsonl snapshot taken before the run resumed.

## Rules

- **A missing row means the parent never received the result.** Look at the pool, the OOM
  killer, and `_repair_jsonl` — never at the write path. One process writes.
- **Out-of-order rows are `imap_unordered` working correctly**, not corruption.
- **Cross-check `N already done` against `wc -l`** before theorizing. A mismatch of one is a
  torn final line, i.e. the previous run was killed.
- **Size workers so `n_workers * _est_gb_per_pres` leaves real headroom**, because the guard's
  per-worker share is *above* a single search's peak and so can never fire. At 1M/`mrl48` on a
  53 GB runtime that means `N_WORKERS = 2` (~28.8 GB), not the auto-chosen 3 (~43.2 GB).

## Related

[`gb-per-pres-sized-from-measured-memory`](gb-per-pres-sized-from-measured-memory.md) sets the
estimate and explains why the guard is deliberately *not* share-based.
[`forked-workers-block-cause-unknown`](forked-workers-block-cause-unknown.md) is the other
failure with this symptom — workers **blocked alive** rather than killed. Distinguish them from
the console: count distinct pids in `[hb] pres N started (worker pid P)` (more than `n_workers`
→ replaced → died) and read `[hb] N solving` (`3` → full throughput → died; `1` → blocked).
