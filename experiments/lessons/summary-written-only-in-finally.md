# [2026-08-16] A derived index file that a verifier hard-fails on must be written on the same cadence as the thing it indexes — never only at clean shutdown [TRAP]

`covmeet.run()` wrote its `*_summary.json` in exactly one place: the `finally:` block. Every other artifact was crash-hardened with real care — the certs jsonl fsyncs at each write and repairs a torn tail before appending, the snapshot is atomic (tmp → fsync → `os.replace`, previous kept) with a sha256 trailer and a `.prev` fallback, and resume was tested to be identical to an uninterrupted run. The summary was the one file left on a "we'll write it when we stop" cadence.

`finally` does not run on SIGKILL. A preempted spot instance is killed, not asked to exit — which is the deployment this engine was designed for, and the `.snap`/`.snap.prev` rotation exists precisely because of it.

What shipped: a ~25.6 h vast.ai session (2026-08-15 05:24:30 → 08-16 06:58+) expanded 9,336,325 orbits and discovered 14,627,414, then died. The `summary.json` next to that snapshot still read

```
"expanded": 28224,  "discovered": 59056,
"stopped": "time bound 180s reached (smoke)"
```

— the 3-minute smoke run from the previous day, **331× behind** the store it was supposed to describe.

The cost was not the wrong numbers. It was that `verify_covmeet` hard-fails when the summary and the snapshot disagree on any of `classes_remaining` / `merges_found` / `n_improved` / `expanded` / `discovered`, and `report_covmeet` refuses to write `COVMEET.md` unless the verifier passes. So a 14.6M-orbit store that passed **every** integrity, canonicalisation, abelianization-invariant and chain-replay check was unreportable, and the pipeline's own diagnosis pointed at the store rather than at the bookkeeping file. Writing the summary is milliseconds; the run it blocked was a day of 20-core compute.

Fix: `_write_summary()` is called immediately after **every** `save_snapshot()` — the fresh-run seed checkpoint, each periodic checkpoint, and the end-of-run write — plus a `regen_summary(out_dir, seed_set)` recovery path that rebuilds it from the snapshot alone for runs that already have a stale one.

Two details that are easy to get backwards:

* **Order.** Snapshot first, summary second. At this size the snapshot write is ~174 s and the summary is ~1 ms, so a kill in between leaves the summary behind by at most one checkpoint. Writing the summary first would leave it *ahead* by a whole snapshot write, which is the same failure with a wider window.
* **Do not bump the engine tag.** The reflex on "checkpoint format changed" is to bump `ENGINE_TAG`, and here that would have made `load()` reject the existing 14.6M-orbit snapshot — destroying the run while fixing it. The tag guards *event semantics and the expansion rule*; adding a write of a file that is not part of the store touches neither.

The test that pins it simulates the kill by patching `save_snapshot` to raise after N calls: the `finally` calls it again, raises again, and the end-of-run summary write is therefore never reached — leaving exactly what the periodic checkpoint wrote. Mutation-checked: deleting the checkpoint-site call fails it with `expanded: summary 0 vs snapshot 1`.

Third occurrence of the same family in this repo, after [`heavy-mode-defers-solved-rows`](heavy-mode-defers-solved-rows.md) and [`mem-abort-pending-row`](mem-abort-pending-row.md) — but with a new twist worth stating on its own: those two lost a *result*, this one lost nothing and still cost a day, because a downstream gate had quietly promoted a summary file into load-bearing state.

**Rule:** when a verifier or a report gate hard-fails on a derived file, that file is part of the state, not a convenience — write it on the same cadence as what it describes (immediately after, never before), and ship a regeneration path that rebuilds it from the real state. And before bumping a format/identity tag as part of a durability fix, ask whether the bump would orphan the artifact you are trying to rescue.
