# Three-hour elementary AC pattern investigation

Research window: 2026-09-12 03:28:52–06:28:52 UTC. The final cutoff is before
02:30 America/New_York. Branch: `codex/theory-patterns-3h`.

Read [FINAL_REPORT.md](FINAL_REPORT.md) for the conclusions and limits,
[u124_final_table.md](u124_final_table.md) for every input's exact certified
minimum, and [THEORY_CATALOG.md](THEORY_CATALOG.md) for the general rules
and their proofs. The table's explicit status/timestamp identifies whether
the deadline snapshot has been exported. [final_table_validation.json](final_table_validation.json)
records the table checks; the final `ARTIFACT_MANIFEST.json` pins the local files.

The objective is to develop general constructive patterns beyond the existing
BS, primitive, torus and Magnus catalogue and try them on the 124 retained
Miller–Schupp components. Complete trivializations are the primary target;
certified strict reductions are recorded separately. The user subsequently
authorized stable AC as well as ordinary AC. Neither a solve nor a reduction
is promised.

## Protocol

1. Inventory exact inputs and prior results; select a small structurally diverse
   development panel before running candidate searches.
2. Generate distinct mathematical candidates, state their exact hypotheses, and
   separate known lemmas from proposed extensions.
3. Prove local identities in the free group and implement explicit inversion,
   multiplication and generator-conjugation certificates. Stable defining-word
   composites additionally require the explicit finite-realizability proof in
   `STABLE_CERTIFICATE_CONVENTIONS.md`; an unexpanded stable composite is labelled
   separately from a generator-level certificate.
4. Test small planted positive and negative examples, then the panel. Run only
   small serial local experiments (at most 1,000 search nodes per input).
5. Independently audit successful certificates and assess applicability to all
   U124 inputs using cheap structural scans. Record failed approaches too.
6. Stop new work at the deadline and report theorem status, exact coverage,
   certificate lengths, CPU/wall cost and remaining gaps honestly.

Four active agents are available including the coordinator. Specialist
assignments run in waves, with Astra for ideas and Sol/Terra for proof and
execution. Existing `codex/proofs` is read for context; its stable AK3 bridge
program is not being continued here. Frozen `data/` and `results/` are read-only.

This directory retains the research record, including failed attempts and
earlier author snapshots. A file's existence does not mean its theorem or
experiment passed review. The final report identifies the verified conclusions;
later independent audit files supersede a frozen author's pending-review label.
The work remains local and uncommitted; nothing was pushed.
