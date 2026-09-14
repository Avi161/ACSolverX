# Intermediate certificate minima

Status: **complete**. Found **0 intermediate solves and 0 strict length improvements**; aggregate saved-best length 2356→2356.

Stream each prepared record; replay preparation once per attempt, then theorem moves from that prepared input. Ignore redundant raw/composed/best copies. Check cyclic total length after every multiply, since invert and conjugate preserve it. Confirm every final state exactly. Materialize only strict improvements, append explicit ordinary canonicalization and independently replay the complete prefix from the original pair. No search or new theorem call.

Temporary donor states are ordinary legal pairs and are included. Only cyclic total length is used for admission; no canonical rotations are computed unless a strict new minimum occurs. The ledger always includes all124 original saved-best inputs, with per-source completeness flags. An unchanged row that was not fully audited is not a negative conclusion.

Checked 5374 certificates and 3042053 elementary steps, including 36147 multiplications. Runtime 59.585246s wall / 4.815976s CPU, including 54.670987s measured cooldown; CPU cap 60s. The320-step differential check and temporary-minimum regression passed.

| source | rows complete | complete |
|---|---:|---|
| prepared_frames_full124.jsonl | 124 | True |
| boundary_compiler_report.json | 124 | True |
| critical_pairs_panel.json | 20 | True |

All124 results: `intermediate_minima.csv`. Exact best words, gain certificates, source hashes and coverage: `intermediate_minima.json`.
