# Independent cyclic-complement audit

PASS. Explicit set partitions reproduce every saved root graph and all 14,864 identified-vertex quotients across 124 inputs. None folds to the full x/y rose.

298 small controls match the author implementation; 270 positive control words independently generate the rose when adjoined. Controls cover the empty subgroup, one-loop and full bouquets, proper power subgroups, conjugated generators, and free cancellation.

The independent folder explicitly merges sets of vertices and restarts after each collision; the author folder uses union-find. Both canonically label the resulting rooted graph.

The exact negative conclusion applies to these literal subgroups only. It excludes neither a complement after ordinary AC changes nor stable AC-triviality by another route, and says nothing about nontriviality of the presented groups.

Criterion: [Delgado–Silva, Lemma 5.3 and Theorem 5.4](https://gcc.episciences.org/6059/pdf). Detailed counts, source hashes, controls and timings are in `complement_audit.json`.

## Certified endpoint follow-up

The streamed follow-up considered 3,746 exact new endpoint pairs from `boundary_compiler_report.json` and `prepared_frames_full124.jsonl`, tested 951, and found no cyclic-complement witness. Every selected endpoint has a composed ordinary prefix from its original input, replayed by two word-level checkers. Exact rooted-graph reuse accounts for 285 selected endpoints.

The main pass performed 123,055 vertex-pair checks. Its 1,000-check cap is shared across endpoints for each input. Only aca_117 exhausts its saved endpoint portfolio (5 endpoints, 55 checks); the other 123 inputs are **unknown at the cap**. A completed negative graph test excludes a complement for that literal subgroup; a capped test has no such conclusion.

**Execution-budget exception:** the one-row preflight for `aca_0` was inadvertently repeated in the full pass. It performed 2,000 physical checks of 1,000 distinct identifications, violating the requested physical 1,000-check cap on that one input. The extra 1,000 checks add no coverage. All other inputs remain within the cap; total physical follow-up checks including the repeat are 124,055. This exception is recorded both per-row and in the summary JSON.

The main pass took 3.599157 s of row screening wall time / 3.551183 s CPU; elapsed time including streaming, source hashing and 0.1 s cooldown per row was 18.536567 s. The repeated preflight adds approximately 0.033743 s of row screening wall time and 0.295732 s elapsed.

`complement_followup.json` contains per-input counts and source hashes; `complement_followup.jsonl` contains each chosen pair, source array indices/line index, prefix digest and size, replay status, graph digest, graph-completeness flag and merge count. No compiler was rerun, and the 252 MB source was streamed one row at a time. A positive would only be a stable criterion witness pending full proof review, never an automatic ordinary solve.
