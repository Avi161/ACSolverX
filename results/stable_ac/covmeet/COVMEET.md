# covmeet — CoV-only collision search over the unsolved classes

Engine `covmeet3`, family `subnc2pxysbnolim`, seed set `all124` (124 classes). CoV moves only — no AC or substitution search, zero search nodes. A merge certifies the two classes **stably** AC-equivalent (never unqualified AC-equivalence); every chain below replays segment-by-segment through `verify_covmeet` (exit 0 gated this page).

**As of:** 28,224 orbits expanded, 59,056 discovered, frontier 30,832 (shortest open bucket L=17), 1 session(s), last 2026-08-15T01:11:59Z.

## Classes remaining: **124 / 124**

Merges found: **0**. Classes reaching below their seeded Aut-min: **0**.

## The census

Over 28,224 expanded orbits: raw subword CoVs per state median 65 (min 34, max 162); **non-automorphic** CoVs per state (distinct Aut-orbits, the honest branching) median 6 (min 0, max 13). Full table: `covmeet_census.csv`; per-class rows incl. each class's own census: `covmeet_classes.csv`.

## Reproduce / verify

```bash
PYTHONPATH=. python3 -m experiments.stable_ac.cov.meet.verify_covmeet <OUT_DIR> --full
```

Raw run state (snapshot + certs) is the user's `covmeet_out/` folder; the certs jsonl beside this page carries every merge/drop chain verbatim.
