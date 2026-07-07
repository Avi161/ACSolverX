# AK(3) stable-proof campaign — data archive

Consolidated, deduplicated per-record datasets from the Lane-D plateau-elimination
campaign, so a future attempt can look up what was already tested instead of re-running
the same searches.

## Files

- `campaign_candidates.jsonl.gz` — 180,645 rows. One per DISTINCT reachable
  Lemma-11 quotient of the AK(3) stable class (deduped by symmetry key `mkey`; shortest
  form kept), whether or not it was solve-attempted. This is the quotient pool itself.
- `campaign_trials.jsonl.gz` — 16,841 rows (0 solved).
  One per solve ATTEMPT, with the full outcome.

## Schema — campaign_candidates.jsonl.gz

| field | meaning |
|---|---|
| `mkey` | symmetry-canonical id (min over 2^k·k! signed relabelings x per-relator rotate/invert/reorder); the dedup key |
| `relators` | the two relators as signed-int lists (x=1, y=2, x^-1=-1, y^-1=-2) |
| `total_len` | sum of relator lengths (trivial = 2) |
| `form`,`word`,`gen`,`ri`,`src` | provenance: which z=w stabilization + eliminated generator produced it |
| `source_boxes` | which box(es) harvested it (D1/D2/D3) |

## Schema — campaign_trials.jsonl.gz

| field | meaning |
|---|---|
| `mkey`,`relators`,`total_len` | the quotient tested (as above) |
| `source` | `laneD:D1/D2/D3` (cap L=24 greedy @ budget2) or `resolve` (high-L re-solve) |
| `budget` | node budget (max heap pops) the search was run to |
| `L` | per-relator length cap in effect (24 for Lane-D solve; 40+ for resolve) |
| `solved` | reached the trivial presentation |
| `nodes` | nodes actually expanded |
| `min_total_len` | shortest total length reached — the plateau floor if unsolved |
| `max_rel_lens`,`max_rel_len` | longest relator lengths at peak (resolve only) — cap-usage evidence |
| `path_states` | full solution state sequence (present only on `solved:true`) |

## Reuse

A quotient `mkey` with a `solved:false` trial at `budget >= B` and `L >= C` is a known
negative at that effort — attack it harder (bigger budget / cap / a different move set),
don't repeat it. Any `solved:true` row carries `path_states`: a machine-checkable
solution (verify with verify_certificate.py + independent_verifier.py).
