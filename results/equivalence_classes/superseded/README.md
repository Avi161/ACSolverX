# `superseded/` — the first pass, kept only for provenance

Unlike [`../convergence/`](../convergence/), this **is** an archive. Nothing in the repo reads either
file, nothing cites them, and the result they carry has been redone properly.

| file | what it was |
|---|---|
| `ms_reps_aut_dedup.csv` | the first `Aut(F₂)` dedup of the 261 reps → **168 classes** (168 rows + header) |
| `whitehead_classes.json` | the same partition as `{class_id: [total_len, r1, r2]}` |

Both were committed alongside `experiments/analysis/whitehead.py` in an early exploratory pass, and
they lived *inside that code package* until this reorg — data files in a source directory, produced by
a script that was never committed.

**Why they are superseded, not deleted:** the 261 → 168 `Aut(F₂)` partition is still true, and it is
still a step in the argument. But it is now produced by the verified pipeline
(`experiments/equivalence_classes/lib/autcanon.py`, cross-checked element-for-element against the
independently written `experiments/analysis/whitehead.py`, and re-proved by Nielsen reduction in
`verify/verify_proofs.py`). The 168 count is embedded in the canonical sweep's `roots` field, and the
result was then pushed further, to **126**, by adding AC moves.

So: same fact, no witness, no verifier, no provenance. Use the verified pipeline. These are here
because deleting a result is worse than shelving it.
