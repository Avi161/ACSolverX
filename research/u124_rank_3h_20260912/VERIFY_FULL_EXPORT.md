# Complete stable-composite export — PASS

[all124_stable_composite.jsonl](verification/export/all124_stable_composite.jsonl)
contains a continuous, explicit certificate for each of the 124 saved rank-two
starts in the pinned `aca_124_best.csv`. Their total length is 2356; the pinned
current endpoints total 2162, with 35 rank-two and 89 rank-three endpoints.
There are 265 saved/reconstructed composite or ordinary events, and no
unresolved lineage segment. All 124 initial and final word tuples have been
joined exactly to the CSV and the saved `CURRENT` snapshot.

`export_paths.py` reconstructs these certificates without running a presentation
search or invoking a subject compiler. It resolves the old literal, primitive,
recursive and rank-three ordinary-suffix records, checks their pinned source
and audit hashes, then connects them to the retained later witness prefix.
Explicit signed generator maps and relator equivalence witnesses preserve
coordinate changes and row sorting. The exported event list includes every
operation required from its own rank-two input; source pointers are provenance,
not deferred portions of the path.

The export is flat at the **stable composite** level. Definition/template
events retain the fresh defining row and every old relator; exact expansion
proves each replacement. Ambient basis events include forward and inverse
maps. The retained later events include their full defining, substitution,
normalization and removal ledgers. Relator equivalences give each old-row
index, inversion sign and conjugating word. The old ordinary suffix includes
its 21 elementary steps.

The stable composites use the known-trivial input hypothesis and the recorded
Lemma-11/defining-generator conventions. Their normal-closure products and
generator-level elementary stable expansions are not emitted. Thus 265 is
an event count for this export, not an elementary AC distance. Unimodularity
is not used to infer triviality. These paths start at the saved rank-two
states; they do not purport to reproduce the older moves from the archival
2446-total starts.

All stored event boundaries count every relator. The maximum rank in these
selected shortening certificates is five; higher-rank research detours are
separate witnesses and are not needed to certify these endpoints. Intermediate
steps inside an unexpanded stable composite are not included in the boundary
minimum or maximum statistics.

`verification_export_checks.json` records the independent readback: all 124
chains, all 118 lineage segments and exact endpoint words pass. Ten mutations
are rejected, including an omitted defining row, wrong template sign, wrong
rotation, duplicate old row, corrupted inverse, self-donor move, discontinuous
suffix, wrong endpoint, stale source pointer and determinant-only premise.

The immutable table snapshot, certificate SHA-256 and all source pins are in
[manifest.json](verification/export/manifest.json). Rebuild after a later
improvement with `export_paths.py`; replay the emitted file with
`export_paths.py --check`. Both commands require Python 3 and the preserved
independent audit modules in this workspace. Algebraic replay reads the
embedded event data; it does not recover missing moves from a search.

`verification_full_export.json` is the machine-readable delivery summary.
The exporter writes through a same-directory partial file and replaces the
JSONL only after every row and the complete written file have passed replay.
