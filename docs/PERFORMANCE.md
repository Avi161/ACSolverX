# Performance

What a setting costs in CPU time and memory, measured with `run.py` on MS640: the relator cap, recording the path, and
(last section) the methods side by side.

**After the replay fix.** Commit `0712d76a` makes the runner replay each solve once instead of twice and warm up before
the timed rows, which changes CPU only: solved counts, pops, units and paths are identical. Only the two hybrid rows of
"Recording the path" (MS640, path on and off, one run each) and the LENGTH, S20_MK2 and hybrid runs of "Methods side by
side" were measured again; every other CPU number, ratio and microsecond in this file was measured before the fix.

**How it was measured.** A 4-vCPU VM (Intel Xeon, 2.8 GHz, 16 GB) that other jobs share; Python 3.12.3, numba 0.63.1,
numpy 2.1.3. Each run is one process (`workers = 1`, `NUMBA_NUM_THREADS=1`). The cost is **CPU time**, never wall time:
`cpu_seconds` of `summary.json` (every row, replay and decoding included) and `us_per_cost`, its microseconds per pop
(per unit for the hybrid). Memory is the peak resident size of the process, of which about 150 MB is Python and numba.
Each run started after a warm-up run (numba loads its compiled kernels). **Repetitions:** the LENGTH and S20_MK2 runs at
cap 24 and `none`, the `decode = false` run, the hybrid and CoV were run twice, alternating the settings between
repetitions, and the tables give the faster run (the two agreed within 3% for the fast backend and 9%
for the 15-second hybrid runs, so differences of a few percent there are noise). Everything else (caps 32 and 48, the
100,000-pop runs, the spec backend) is **one run**. The VM is shared, so each row also gives the **load**: the 1-minute
load average read when the run ended. A lone run reads 1.0; these read 1.1 to 2.0, because short jobs of
other sessions ran beside them.

To reproduce a row, run the config with the `--set` lines named above its table and read the summary:

```bash
python run.py --config configs/greedy_fast.toml --set search.cap=none --set name=len_nocap --fresh
python -c "import json; s = json.load(open('results/len_nocap/summary.json')); print(s['cpu_seconds'], s['us_per_cost'])"
/usr/bin/time -v python run.py --config configs/greedy_fast.toml --set search.cap=none --set name=len_nocap --fresh 2>&1 | grep Maximum   # peak memory
```

## Relator cap: cost of a larger or no cap

`cap = "none"` (`--set search.cap=none`) pushes every child whatever the length of its relators; the fast backend's state
arrays widen when a state needs it, so no relator is ever too long to enter. The price is that the search then stores,
hashes and queues the children a cap would have dropped. What each cap does on MS640 with the fast backend at 10,000 pops
(`greedy_fast.toml` for LENGTH, `s20_mk2_fast.toml` for S20_MK2, `--set search.cap=<24|32|48|none>`; an uncapped run has
no counter, so "dropped" is 0 and "would pop" is not defined):

| priority | cap | solved | pops | rows where a dropped state would pop | children dropped | states stored | largest total |
|---|---:|---:|---:|---:|---:|---:|---:|
| LENGTH | 24 | 606 | 576,053 | 0 | 12,195,104 | 30,168,922 | 46 |
| LENGTH | 32 | 606 | 576,053 | 0 | 0 | 40,260,920 | 52 |
| LENGTH | 48 | 606 | 576,053 | 0 | 0 | 40,260,920 | 52 |
| LENGTH | none | 606 | 576,053 | - | 0 | 40,260,920 | 52 |
| S20_MK2 | 24 | 626 | 382,718 | 20 | 10,128,166 | 19,912,492 | 47 |
| S20_MK2 | 32 | 626 | 382,838 | 0 | 9,560 | 28,389,551 | 56 |
| S20_MK2 | 48 | 626 | 382,838 | 0 | 0 | 28,399,089 | 58 |
| S20_MK2 | none | 626 | 382,838 | - | 0 | 28,399,089 | 58 |

What it costs, with the default `path = true` and with `--set path=false` (search only, no replay or decoding; see
"Recording the path"):

| priority | cap | CPU s | x cap 24 | us/pop | CPU s, path off | x cap 24 | us/pop, path off | peak MB | load |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LENGTH | 24 | 83.0 | 1.00 | 144.1 | 60.0 | 1.00 | 104.1 | 330 | 1.5 |
| LENGTH | 32 | 104.3 | 1.26 | 181.1 | 82.9 | 1.38 | 144.0 | 345 | 1.2 |
| LENGTH | 48 | 110.9 | 1.34 | 192.5 | 91.4 | 1.52 | 158.7 | 393 | 1.9 |
| LENGTH | none | 107.5 | 1.30 | 186.6 | 80.2 | 1.34 | 139.2 | 395 | 1.2 |
| S20_MK2 | 24 | 62.7 | 1.00 | 163.9 | 34.8 | 1.00 | 91.0 | 260 | 1.5 |
| S20_MK2 | 32 | 82.3 | 1.31 | 215.0 | 52.2 | 1.50 | 136.4 | 346 | 1.3 |
| S20_MK2 | 48 | 88.1 | 1.40 | 230.1 | 58.5 | 1.68 | 152.7 | 394 | 1.6 |
| S20_MK2 | none | 91.3 | 1.46 | 238.4 | 62.6 | 1.80 | 163.5 | 447 | 1.8 |

- **LENGTH.** Without a cap the search is the same search: the same 606 rows in the same 576,053 pops, as
  [CAP.md](CAP.md) promises when no dropped state would pop. It stores 10.1M more states (+33%) and costs +30% CPU per
  run (+34% for the search alone), about 2 us per stored state at every cap. All of it comes from the 26 rows where cap 24
  drops children (12.2M of them, 38% of the pops): those cost 2.0x as much uncapped (up to 4.3x on row
  633); the other 614 rows cost 1.01x.
- **S20_MK2.** The same 626 rows are solved; six of them a few pops later (row 527: 7,458 pops at cap 24, 7,479 at cap
  25 or more), which is what the 20 rows with "would pop" at cap 24 predicted. It stores +43% states and costs +46% CPU
  (+80% for the search alone).
- **Caps 32 and 48 are no cheaper than `none`.** From 32 up almost nothing is dropped on MS640 (nothing with LENGTH, 9,560
  children with S20_MK2), so the search is the uncapped one. A fixed cap also fixes the width of every state array: cap 48
  makes them 48 letters wide, which costs more than `none` (91.4 against 80.2 s search-only with LENGTH), because uncapped
  arrays start at the width of the start presentation and widen only when a state could produce a longer child.

At 100,000 pops, on rows that cap 24 binds on (LENGTH rows 568, 610, 628, 636; S20_MK2 rows 616, 622, 638, all left
unsolved at 10,000 pops; `--set search.budget=100000 --set path=false --rows <ids>`; one run, rows sampled to stay within
the time limit):

| priority | rows | cap | solved | pops | rows where a dropped state would pop | states stored | CPU s | x cap 24 | us/pop | peak MB | load |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LENGTH | 4 | 24 | 3 | 203,954 | 0 | 5,199,754 | 17.1 | 1.00 | 83.6 | 565 | 1.8 |
| LENGTH | 4 | none | 3 | 203,954 | - | 18,320,992 | 57.9 | 3.39 | 283.9 | 2,070 | 1.5 |
| S20_MK2 | 3 | 24 | 3 | 102,208 | 3 | 5,262,751 | 11.4 | 1.00 | 111.3 | 374 | 1.5 |
| S20_MK2 | 3 | none | 3 | 102,526 | - | 8,261,516 | 29.5 | 2.60 | 288.2 | 919 | 1.3 |

Past the first thousands of pops the gap grows: where the cap binds, uncapped is 2.6x to 3.4x slower and uses 2.5x to
3.7x the memory (2.1 GB for four rows), with the same solved rows. The spec backend (`baseline_spec.toml`, `--set
workers=1`, 10,000 pops; rows 0:40 are the first 40 MS640 rows, at most 10 pops each, so the cap never binds; 628 and 636
are two of the rows it binds on most; one run):

| rows | cap | solved | pops | states stored | CPU s | x cap 24 | us/pop | peak MB | load |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0:40 | 24 | 40 / 40 | 231 | 1,747 | 0.24 | 1.00 | 1,025 | 104 | 1.2 |
| 0:40 | none | 40 / 40 | 231 | 1,747 | 0.22 | 0.91 | 934 | 104 | 1.3 |
| 628, 636 | 24 | 0 / 2 | 20,000 | 274,972 | 167.29 | 1.00 | 8,364 | 530 | 1.3 |
| 628, 636 | none | 0 / 2 | 20,000 | 1,871,906 | 169.30 | 1.01 | 8,465 | 1,172 | 1.6 |

In pure Python the cap changes the CPU time by no more than 3% per row (building a child costs far more than storing it, and
the cap drops a child only after building it), but it still changes the memory 2.2x, as 1.87M states are kept instead of
275k. The hybrid on all of MS640 (`hybrid.toml`, `--set hybrid.r2_cap=24`, `--set hybrid.r2_cap=none`, `--set
hybrid.dyn_cap=none`; the third limit, `slack`, also takes an integer or `"none"`, not measured here) and CoV on
bench60 (`cov.toml`, `--set search.cap=none`):

| setting | solved | units | r2_cap drops | dyn_cap drops | CPU s | x default | us/unit | peak MB | load |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `r2_cap = "parent"` (default) | 640 | 25,064 | 0 | 766 | 15.0 | 1.00 | 597 | 176 | 1.2 |
| `r2_cap = 24` | 640 | 25,064 | 0 | 766 | 14.3 | 0.96 | 570 | 176 | 1.1 |
| `r2_cap = "none"` | 640 | 25,064 | - | 766 | 15.0 | 1.00 | 598 | 176 | 1.1 |
| `dyn_cap = "none"` | 640 | 25,064 | 0 | - | 14.5 | 0.97 | 577 | 176 | 1.4 |

| cap | solved | pops | CPU s | x cap 24 | us/pop | peak MB | load |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 24 | 39 / 60 | 246,744 | 33.8 | 1.00 | 137 | 216 | 1.4 |
| none | 39 / 60 | 246,744 | 35.0 | 1.04 | 142 | 240 | 1.2 |

The hybrid and CoV hardly feel the cap on MS640: the hybrid solves the same 640 rows in the same 25,064 units whichever
limit is set, and the CPU differences (-4% to +0%) are inside the noise of a 15-second run. CoV costs +4% for the same
39 rows.

**What it means.** A cap is not needed for correctness: `none` solves exactly what cap 24 solves with LENGTH on MS640, and
S20_MK2 changes by a few pops on six rows. It costs CPU and memory in proportion to the children the cap would have dropped:
+30% per run with LENGTH and +46% with S20_MK2 at 10,000 pops on MS640, 2.6x to 3.4x on the rows the cap binds on at
100,000 pops, nothing for the hybrid, about 4% for CoV, and nothing in CPU (but 2.2x the memory) for the spec backend. Prefer `none` to a
large fixed cap (it is no slower, at about the same memory), and keep 24 when a run is dominated by rows the cap binds on; the counters in
[CAP.md](CAP.md) (`rows_dropped`, `raise_ids`) show which rows those are.

## Recording the path

`path = true` (the default) keeps each solve's S-move path, replays it on the row, and (`decode = true`) decodes it to
elementary AC moves; the record is then `verified`. `path = false` skips all three: the search stores no parent and move
per state, nothing is replayed, and `path`, `elementary` and `verified` are empty. `--set decode=false` keeps the replay
and skips only the decoding. MS640, 10,000 pops (hybrid: 1,000 units per row; only the hybrid rows are after the fix):

| run | `path` | CPU s | x path on | us/cost | peak MB | load |
|---|---|---:|---:|---:|---:|---:|
| LENGTH, cap 24 | true | 83.0 | 1.00 | 144.1 | 330 | 1.5 |
| LENGTH, cap 24 | true, `decode = false` | 65.9 | 0.79 | 114.5 | 329 | 1.9 |
| LENGTH, cap 24 | false | 60.0 | 0.72 | 104.1 | 285 | 1.4 |
| LENGTH, no cap | true | 107.5 | 1.00 | 186.6 | 395 | 1.2 |
| LENGTH, no cap | false | 80.2 | 0.75 | 139.2 | 361 | 1.4 |
| S20_MK2, cap 24 | true | 62.7 | 1.00 | 163.9 | 260 | 1.5 |
| S20_MK2, cap 24 | false | 34.8 | 0.56 | 91.0 | 234 | 1.5 |
| S20_MK2, no cap | true | 91.3 | 1.00 | 238.4 | 447 | 1.8 |
| S20_MK2, no cap | false | 62.6 | 0.69 | 163.5 | 390 | 1.9 |
| hybrid | true | 10.5 | 1.00 | 420.8 | 175 | 1.0 |
| hybrid | false | 2.9 | 0.28 | 117.4 | 156 | 1.0 |

For LENGTH at cap 24 the default run spends 28% of its CPU beyond the search: 21% decoding to elementary moves (83.0 to
65.9 s) and 7% on replay and storing the path (to 60.0 s). With S20_MK2, whose paths are longer (168,702 elementary moves
against 114,828), recording the path is 44% of the run, and with the hybrid 72% (10.5 s to 2.9 s): its certificate is the
expensive part. `path = false` is for counting solves or comparing settings quickly; a result to quote needs `path = true`,
since only then is the solve replayed on its row.

## Methods side by side

`compare.py` puts finished runs side by side, and [`compare.html`](compare.html) (self-contained; open it in a browser)
draws the 16 runs below as bar charts. **How to read them.** *Cost* is in the run's own unit: pops for the greedy search
(LENGTH and S20_MK2), CoV and aut, work units for the hybrid, network evaluations for RL. **A hybrid unit is not a
pop** (it also counts accepted automorphisms, image evaluations and substitution moves), so compare speed by CPU, not by
units against pops. Cost and move columns **average the rows a run solved**, so a run that solves fewer, easier rows
looks cheaper. CPU **covers every row**, misses included (a greedy miss spends its whole 10,000 pops), plus decoding and
replaying each certificate; CPU µs per pop/unit is that total over the total cost. *raise-cap rows* counts the rows where
a larger relator cap would change the search ([CAP.md](CAP.md)). CPU is `time.process_time` of single-threaded runs,
one at a time, on a 4-core 2.8 GHz VM; identical runs differ by 4 to 11% in total CPU, so trust ratios more than
milliseconds. The LENGTH, S20_MK2 and hybrid runs are after the replay fix (one run each); **the CoV, aut and RL runs
were not repeated, so their CPU columns were measured before the replay fix** (their solved counts and costs do not
depend on it).

### bench60

60 MS640 rows picked evenly across ten difficulty bins (3 to about 575,000 pops of baseline greedy).

| run | method | benchmark | rows | solved | mean cost (solved) | median cost (solved) | mean sub_moves | mean elem_moves | CPU s/row | CPU µs per pop/unit | raise-cap rows | errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bench60_length | greedy | bench60 | 60 | 40 (66.7%) | 1,205.7 pops | 197.0 pops | 36.9 | 375.7 | 0.512 | 123.7/pop | 0 | 0 |
| bench60_s20_mk2 | greedy | bench60 | 60 | 52 (86.7%) | 1,187.3 pops | 190.0 pops | 62.2 | 657.2 | 0.338 | 143.0/pop | 10 | 0 |
| bench60_hybrid | hybrid | bench60 | 60 | 60 (100.0%) | 79.7 units | 43.0 units | 56.4 | 460.7 | 0.076 | 949.9/unit | 0 | 0 |
| bench60_cov | cov | bench60 | 60 | 39 (65.0%) | 942.2 pops | 121.0 pops | 26.7 | 171.4 (n=29) | 0.553 | 134.4/pop | 0 | 0 |
| bench60_aut | aut | bench60 | 60 | 52 (86.7%) | 1,303.2 pops | 180.5 pops | 61.8 | 3,401.1 | 0.498 | 202.2/pop | 10 | 0 |

CPU of `bench60_cov` and `bench60_aut`: measured before the replay fix.

### ladder200

188 rows on difficulty levels 1 to 10 (144 AC19 Aut-min orbits, 44 MS640 rows); plain greedy at 10,000 pops can reach
only levels 1 and 2.

| run | method | benchmark | rows | solved | mean cost (solved) | median cost (solved) | mean sub_moves | mean elem_moves | CPU s/row | CPU µs per pop/unit | raise-cap rows | errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ladder200_length | greedy | ladder200 | 188 | 40 (21.3%) | 1,779.9 pops | 999.5 pops | 49.8 | 527.7 | 0.846 | 102.6/pop | 3 | 0 |
| ladder200_s20_mk2 | greedy | ladder200 | 188 | 116 (61.7%) | 2,962.9 pops | 2,372.5 pops | 66.4 | 742.9 | 0.597 | 105.5/pop | 77 | 0 |
| ladder200_hybrid | hybrid | ladder200 | 188 | 188 (100.0%) | 118.7 units | 65.5 units | 41.1 | 462.4 | 0.237 | 1,999.5/unit | 21 | 0 |
| ladder200_cov | cov | ladder200 | 188 | 92 (48.9%) | 4,315.5 pops | 4,819.0 pops | 35.8 | 1,370.9 (n=44) | 0.971 | 134.6/pop | 0 | 0 |
| ladder200_aut | aut | ladder200 | 188 | 116 (61.7%) | 3,025.7 pops | 2,376.0 pops | 67.7 | 2,214.9 | 0.684 | 120.1/pop | 77 | 0 |

CPU of `ladder200_cov` and `ladder200_aut`: measured before the replay fix.

### MS640

All 640 Miller-Schupp rows, each solved by the baseline within a million pops.

| run | method | benchmark | rows | solved | mean cost (solved) | median cost (solved) | mean sub_moves | mean elem_moves | CPU s/row | CPU µs per pop/unit | raise-cap rows | errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ms640_length | greedy | ms640 | 640 | 606 (94.7%) | 389.5 pops | 10.0 pops | 20.0 | 189.5 | 0.126 | 139.8/pop | 0 | 0 |
| ms640_s20_mk2 | greedy | ms640 | 640 | 626 (97.8%) | 387.7 pops | 10.5 pops | 27.0 | 269.5 | 0.094 | 158.0/pop | 20 | 0 |
| ms640_hybrid | hybrid | ms640 | 640 | 640 (100.0%) | 39.2 units | 29.0 units | 19.3 | 139.1 | 0.017 | 421.7/unit | 0 | 0 |
| ms640_cov | cov | ms640 | 640 | 584 (91.2%) | 228.0 pops | 9.0 pops | 14.3 | 99.2 (n=554) | 0.138 | 127.0/pop | 0 | 0 |
| ms640_aut | aut | ms640 | 640 | 626 (97.8%) | 428.4 pops | 10.0 pops | 27.2 | 1,258.4 | 0.161 | 252.1/pop | 20 | 0 |
| ms640_rl30 | rl | ms640 | 30 | 30 (100.0%) | 321.7 evaluations | 259.5 evaluations | 4.4 | 28.2 | 0.871 | 2,706.5/evaluation | 5 | 0 |

CPU of `ms640_cov`, `ms640_aut` and `ms640_rl30`: measured before the replay fix.

RL ran only the first 30 rows, so its line is not comparable with the others'. On those 30 rows (`--common` over all six
runs; every run solves them all) the five searches need 4.8 to 20.1 pops or units at 1 to 16 ms of CPU per row, RL
321.7 evaluations at 871 ms.

### Head to head: LENGTH, S20_MK2, hybrid

Rows solved, LENGTH / S20_MK2 / hybrid: bench60 40 / 52 / 60 of 60, ladder200 40 / 116 / 188 of 188, MS640 606 / 626 /
640 of 640. The sets are nested: S20_MK2 solves every row LENGTH solves and 12, 76 and 20 more (bench60, ladder200,
MS640), and the hybrid solves every row S20_MK2 solves and 8, 72 and 14 more. So the rows all three solved are exactly
the rows LENGTH solved, and the table averages those:

| run | rows all three solved | mean cost (solved) | median cost (solved) | CPU s/row | CPU µs per pop/unit |
| --- | ---: | ---: | ---: | ---: | ---: |
| bench60_length | 40 of 60 | 1,205.7 pops | 197.0 pops | 0.230 | 191.0/pop |
| bench60_s20_mk2 | 40 of 60 | 280.1 pops | 86.0 pops | 0.072 | 257.7/pop |
| bench60_hybrid | 40 of 60 | 38.8 units | 33.5 units | 0.021 | 531.4/unit |
| ladder200_length | 40 of 188 | 1,779.9 pops | 999.5 pops | 0.255 | 143.5/pop |
| ladder200_s20_mk2 | 40 of 188 | 594.4 pops | 256.5 pops | 0.137 | 231.3/pop |
| ladder200_hybrid | 40 of 188 | 46.6 units | 42.0 units | 0.019 | 405.7/unit |
| ms640_length | 606 of 640 | 389.5 pops | 10.0 pops | 0.066 | 169.9/pop |
| ms640_s20_mk2 | 606 of 640 | 237.2 pops | 9.5 pops | 0.050 | 212.2/pop |
| ms640_hybrid | 606 of 640 | 32.1 units | 28.0 units | 0.008 | 245.0/unit |

### What it shows

1. The hybrid solves 60 of 60, 188 of 188 and 640 of 640 rows (bench60, ladder200, MS640); S20_MK2 solves 52, 116 and
   626 and LENGTH 40, 40 and 606, and each stronger method solves every row the weaker one does.
2. It explores far less. On the rows all three solve, the hybrid explores a mean of 38.8, 46.6 and 32.1 units where
   S20_MK2 explores 280, 594 and 237 pops and LENGTH 1,206, 1,780 and 390. Over all rows the totals are 4,783, 22,319
   and 25,064 units against 141,740, 1,063,702 and 382,718 pops for S20_MK2: each greedy miss alone costs 10,000 pops,
   and no hybrid row needs more than 742 of its 1,000 units.
3. It is also quicker in CPU, although a unit costs more than a pop (0.42 to 2.0 ms against 0.10 to 0.16 ms for a
   greedy pop): the hybrid takes 76, 237 and 17 ms per row against 338, 597 and 94 ms for S20_MK2 and 512, 846 and
   126 ms for LENGTH, while solving more rows.
4. The gain is in the hard rows, not the typical one: on MS640, where most rows are easy, the median hybrid row costs 29
   units against 10 pops for greedy, and the hybrid's mean is lower because greedy's hard rows run to thousands of pops.
5. Of the other kinds, aut solves exactly the rows S20_MK2 solves at 1.1 to 1.7 times its CPU per row, CoV solves fewer
   rows than S20_MK2 (39, 92 and 584) at 1.5 to 1.6 times its CPU, and RL solves the 30 rows it ran at 871 ms of CPU per
   row against 1 to 16 ms for the searches (CPU of aut, CoV and RL from before the replay fix).

### Reproduce

```bash
export NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1      # one thread, so the CPU time is the run's own
OUT=/tmp/compare                                  # any folder; run.py makes one subfolder per run
for b in bench60 ladder200 ms640; do
  python run.py --config configs/greedy_fast.toml  --set benchmark=$b --set name=${b}_length  --out $OUT
  python run.py --config configs/s20_mk2_fast.toml --set benchmark=$b --set name=${b}_s20_mk2 --out $OUT
  python run.py --config configs/hybrid.toml       --set benchmark=$b --set name=${b}_hybrid  --out $OUT
  python run.py --config configs/cov.toml          --set benchmark=$b --set name=${b}_cov     --out $OUT
  python run.py --config configs/aut.toml          --set benchmark=$b --set name=${b}_aut     --out $OUT
done
python run.py --config configs/rl.toml --set name=ms640_rl30 --out $OUT    # 30 MS640 rows; needs PyTorch (the [rl] extra)

for b in bench60 ladder200 ms640; do
  python compare.py $OUT/${b}_{length,s20_mk2,hybrid,cov,aut}      # the plain table (MS640: add $OUT/ms640_rl30)
  python compare.py $OUT/${b}_{length,s20_mk2,hybrid} --common     # head to head: the rows all three solved
done
python compare.py $OUT/ms640_{length,s20_mk2,hybrid,cov,aut,rl30} --common    # the 30 rows RL ran
python compare.py $OUT/{bench60,ladder200,ms640}_{length,s20_mk2,hybrid,cov,aut} $OUT/ms640_rl30 --html docs/compare.html
```

The shipped budgets apply (10,000 pops for LENGTH, S20_MK2 and aut, 10,000 in total for CoV, 1,000 units for the
hybrid), and the 16 runs take about 19 CPU minutes (bench60 2, ladder200 10, MS640 6). With exactly two runs,
`compare.py` also prints their head-to-head line of solved rows. Your own presentations: replace `--set benchmark=$b`
by `--input mine.txt` (formats in `acx/data.py`). The LENGTH, S20_MK2 and hybrid runs were measured at `0712d76a`, the CoV, aut and RL runs at `b745f0f8` (Python 3.12.3,
numba 0.63.1, numpy 2.1.3).
