# Ryan Zang's CoV-gate search with the full CoV image family, to 10^6 units

Ryan's best-first search (gate `no_short_sub`, no length cap) with its CoV move replaced by every CoV image of the
state: `acx.cov.states.cov_states`, family `suballpxyb8` (z := w for every cyclic subword w of length 2 to |r| - 1,
every set of non-overlapping occurrences substituted, x or y eliminated through either relator, one image per class up
to relator order, rotation, inversion and the 8 signed relabellings, no length limit). Ryan's one-letter windows are
not in the family and are not added.

- `../ryan_cov_full_1e5/`: all 740 rows (MS640 + ladder100) at 10^5 units (Python engine, `cov_full.py`).
- this folder: the 14 searches (21 rows) unsolved at 10^5, rerun at 10^6 units (numba engine, `cov_full_numba.py`,
  identical records to the Python by `check_full_numba.py`). All 21 solve, within 149,552 units.
- bench60 is read off MS640. `SUMMARY_TABLE.md` merges both folders, beside Ryan's row (`../ryan_full_1e6`).

```bash
python benchmark/ryan/run_full.py --out results/ryan_cov_full_1e5 --budget 100000
python benchmark/ryan/run_full.py --out results/ryan_cov_full_1e6 --budget 1000000 \
    --only-unsolved-from results/ryan_cov_full_1e5 --engine numba
python benchmark/ryan/verify_full.py results/ryan_cov_full_1e6 --out results/ryan_cov_full_1e6/VERIFY.json
python benchmark/ryan/summarize_full.py results/ryan_cov_full_1e5 results/ryan_cov_full_1e6 --md results/ryan_cov_full_1e6/SUMMARY_TABLE.md
```

**Units.** One per pop plus one per gate opening (building the CoV images of a state is a second expansion). Ryan's
code counts pops only; the table gives both counts for both searches, with Ryan's row recounted from its records. The
search never depends on the budget, so a row solves within B when its `units` is at most B.

## Result (units)

| benchmark | search | 10^3 | 10^4 | 10^5 | 10^6 | units to solve mean / median / max | path mean / median / max |
|---|---|---:|---:|---:|---:|---|---|
| MS640 | Ryan CoV | 590 | 612 | 626 | 640 | 5,580 / 11 / 212,418 | 25.7 / 9 / 462 |
| | full CoV | 596 | 612 | 626 | 640 | 4,104 / 10 / 149,552 | 20.5 / 8 / 375 |
| bench60 | Ryan CoV | 43 | 49 | 52 | 60 | 30,003 / 144 / 212,418 | 88.8 / 20 / 462 |
| | full CoV | 45 | 49 | 52 | 60 | 21,827 / 28 / 149,552 | 70.2 / 16 / 375 |
| ladder100 | Ryan CoV | 64 | 88 | 93 | 100 | 17,105 / 368 / 212,418 | 64.4 / 26 / 462 |
| | full CoV | 73 | 89 | 93 | 100 | 12,119 / 96 / 149,552 | 50.4 / 20 / 375 |

Counted in pops, as the paper's CoV gate row: full CoV 596/612/626/640, 45/49/52/60, 74/89/93/100 (Ryan
590/612/626/640, 43/49/52/60, 66/88/93/100). Paths count S-moves and CoV moves, one each.

## AC path or stable certificate

- **Orbit tag** (checked, and rechecked by `verify_full.py` with the Whitehead backend): a solve is an AC path when
  every CoV step's child lies in its parent's Aut(F2) orbit. MS640 297 AC / 343 stable, bench60 5 / 55, ladder100
  5 / 95.
- On the MS640 solve paths, every single-substitution CoV step is in the orbit (741 of 741) and every
  multi-substitution step is outside it (2,098 of 2,098: 685 with 2 substitutions, 1,065 with 3, 307 with 4, 41 with
  5 to 7).
- **One-z tag** (argued, not replayed): when the isolating relator holds exactly one z, eliminating g is the
  automorphism g -> s z^{+-1} t of F(other, z), and each substitution w -> z in the other relator multiplies it by a
  conjugate of the defining relator, an AC move; so the step is AC even outside the orbit. By this tag 423 MS640, 19
  bench60 and 19 ladder100 solves are AC paths.

## Verification

`VERIFY.json` (here and in `../ryan_cov_full_1e5`): every solve passes. Each substitution step is a reduced product of
rotations; each CoV step's certificate (define z = w, substitute, eliminate) replays on the parent with
`acx.cov.apply_steps` (Lemma 11 hypotheses, |det| = 1) and gives the child; the orbit tag and the path counts agree.

## Compute

AWS spot, account 205558941715, results in `s3://acsolver-u124-205558941715/cov_full/` (`ops/aws/ledger.md`): the 10^5
pass took 11 minutes on c8g.16xlarge (Python); the 10^6 rerun took 67 seconds per search, 1.1 GB each, on
r8g.8xlarge (numba, 14 searches in parallel).
