# Exhaustive CoV sweep (`suballpxyb8`) on MS640

The baseline greedy (`run_baseline.greedy_search`, unchanged; here it is `acx.search` with
`priority = "length"`) is run from the untransformed presentation (control, cap 24) and from every
distinct change-of-variables class of `cov/all-subsets-sweep:experiments/stable_ac/cov/cov_all.py`
(cap `res.cap`), one row per start, for all 640 rows of
`data/ms640_solved.txt` (`pres_id` = 0-based line; subset 60's `pres_id`s are the same rows as
`bench60`, `benchmark/subsets/benchmark_subset_60.csv`). Made on the branch `cov/all-subsets-sweep`
(tip `fb84a588`, 10 to 12 Oct 2026), at budgets 100, 10,000 and 100,000 nodes; 1,000 is read from the
100,000 file.

## In this checkout

- **Here**: the summaries of all three budgets, the per-presentation table, the control-versus-start
  tables and plots, the runner logs, and the 100,000 file `cov_all_suballpxyb8_ms640_b100000.jsonl.gz`
  (4.1 MB): every start of every row, with its transform. It is the only raw file kept: it holds
  the transform of every start, and the 100 and 10,000 files repeat its rows up to their budget (a
  search at a smaller budget is the first pops of a larger one, see the checks below).
- **Not here, listed in [`MANIFEST.json`](MANIFEST.json)** (size and sha256 of each, the source commit,
  the S3 prefix): the raw 100 and 10,000 files (`.jsonl.gz`, 4.4 and 4.1 MB) and the three uncompressed
  forms of the same files (`.jsonl`, 88 to 96 MB, kept in S3 only; each is the gunzip of the `.jsonl.gz`
  of its budget). Fetch a file of the source commit with
  `git show fb84a588:results/stable_ac/cov_all/<file> > <file>`. The raw files are in
  `s3://acsolver-u124-205558941715/cov_all/b<budget>/results/`; the prefix of the 100,000 run was
  confirmed, those of the 100 and 10,000 runs follow the same pattern and were not listed.
- **How acx reproduces it**: `acx.cov` enumerates exactly this family's 114,042 MS640 starts
  (`enumerate_images(pres, family="suballpxyb8")`, or `--set cov.family=suballpxyb8` in
  `configs/cov.toml`; pinned by `tests/test_cov.py`). `acx.search` (`priority = "length"`, the row's
  own cap and budget) then reproduces a row's `nodes_explored` and `path_length`, and `acx.cov` and
  `acx.verify` check the stored certificates and paths ([Verify with acx](#reproduce-and-verify-with-acx)).
  `tests/test_cov_all_study.py` pins every number below that this folder holds.
- **No acx command**: the per-start sweep driver (`run_cov_all.py`), the `--counts` checks of
  `verify_cov_all.py`, and the summarize, table and plot scripts. Their output is the files here.
  They are on `cov/all-subsets-sweep` (listed under [The code](#the-code-on-the-source-branch)). The
  config `python run.py --config configs/cov.toml --set benchmark=ms640 --set cov.family=suballpxyb8`
  is a different experiment (the one-shot method: the first start that solves, 1,000 pops per start,
  10,000 per row), not this sweep.

| file | what | where |
|---|---|---|
| `cov_all_suballpxyb8_ms640_b100.jsonl.gz` | budget 100 smoke: 114,682 rows (640 controls + 114,042 CoV), every solved path stored as `path_moves` | manifest |
| `cov_all_suballpxyb8_ms640_b10000.jsonl.gz` | budget 10,000: the same 114,682 rows; `path_moves` kept on a 2% hash sample of solved rows (`--path-sample 0.02`), every other row keeps `path_length` and `nodes_explored` only | manifest |
| `cov_all_suballpxyb8_ms640_b100000.jsonl.gz` | budget 100,000: the same 114,682 rows, same 2% path sample | here |
| `*.jsonl` (three, uncompressed) | the three files above unpacked | manifest, S3 |
| `cov_all_suballpxyb8_ms640_b10000_subset60_summary.*` | the budget 10,000 statistics restricted to subset 60's 60 `pres_id`s (their rows are in the b10000 file) | here |
| `*_control_vs_cov.png` / `.md` | nodes from a random CoV start against nodes from the control, with y = x (`plot_cov_all_control_vs_cov`; budgets 10,000 and 100,000) | here |
| `cov_all_suballpxyb8_ms640_b100000_per_presentation.csv` | one row per presentation from the budget 100,000 file: the control's result, its number of starts, the best start and the substitution that made it, and the cheaper / equal / dearer / unsolved split (`table_cov_all_per_presentation`); its node counts answer every smaller budget too | here |
| `*_summary.md` / `*_summary.json` | per-presentation statistics aggregated across presentations (`summarize_cov_all`) | here |
| `*.log` | runner log: start, enumeration, progress, wall time | here |
| `MANIFEST.json` | the raw files above with size and sha256, the source commit, the S3 prefix | here |

Each row records how its start was made from the original: `z_word`, `pattern` (chosen
occurrences `[start, ±1]` of w / w⁻¹ in the cyclically reduced r1 and r2), the substituted pair
(`r1_substituted`, `r2_substituted`, generator 3 = z), `defining_relator` (Z·w), `iso_gen`
(eliminated generator), `iso_index` (0 = solved from r1′, 1 = from r2′) and `iso_expr`.
Path lengths of CoV rows are in transformed coordinates: a solve certifies stable AC-triviality.
`path_moves` are the baseline's `target_jsign_k1_k2` strings, which `acx.core.moves.decode_path` reads as they are.

## Reproduce and verify with acx

`acx.cov.check_cert` replays a row's transform (define `z`, substitute, eliminate) and then its stored
path on the start the transform made; `acx.verify.replay` replays a control's path on the row itself.
This checks every sampled row of the 100,000 file (2,251 CoV certificates and 12 control paths, a few
seconds; the test runs this block):

```python
import gzip
import json
from collections import Counter

from acx.core.moves import decode_path
from acx.core.words import Presentation, parse
from acx.cov import check_cert
from acx.verify import replay

FILE = "results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz"
checked = Counter()
with gzip.open(FILE, "rt") as rows:
    for line in rows:
        row = json.loads(line)
        if "path_moves" not in row:               # only a 2% sample of the solved rows keeps its path
            continue
        start = Presentation.parse(row["r1_orig"], row["r2_orig"])
        path = decode_path(row["path_moves"])
        if row["is_control"]:                     # the control searched the row itself
            replay(start, path, cyclic=row["cyclic_reduce"], cap=row["max_relator_length_cap"])
        else:                                     # a start: replay the transform, then the path on its image
            steps = ({"op": "define", "word": parse(row["z_word"])},
                     {"op": "substitute", "rels": (tuple(row["r1_substituted"]), tuple(row["r2_substituted"]))},
                     {"op": "eliminate", "gen": parse(row["iso_gen"])[0], "target": row["iso_index"] + 1,
                      "expr": tuple(row["iso_expr"])})
            check_cert(start, steps, path, cap=row["max_relator_length_cap"], cyclic=row["cyclic_reduce"])
        checked["control" if row["is_control"] else "cov"] += 1
print(dict(checked))                              # {'cov': 2251, 'control': 12}
```

The slow tests of `tests/test_cov_all_study.py` go further: `acx.cov.apply_steps` rebuilds `r1`, `r2` from the
transform of all 114,042 CoV rows, and `acx.search` (LENGTH, fast backend, the row's cap and budget) pops as many
states and finds as long a path as the sweep did on 100 random rows. The search path of the 98% of rows without
`path_moves` is regenerated that way.

| source branch | acx |
|---|---|
| `run_cov_all --budget B --workers N --path-sample P` | no command: enumerate with `acx.cov.enumerate_images(..., family="suballpxyb8")` and search each start with `acx.search` |
| `verify_cov_all FILE` | the snippet above for transforms and stored paths; no equivalent for the `--counts` class checks |
| `summarize_cov_all`, `table_cov_all_per_presentation`, `plot_cov_all_control_vs_cov` | none; their output is the summaries, the csv and the plots here |
| `aws_cov_all_box.sh` | none (size the workers by memory, see below) |

## The code (on the source branch)

Nothing below is in this checkout; the paths are on `cov/all-subsets-sweep` (`fb84a588`), for example
`git show cov/all-subsets-sweep:experiments/stable_ac/cov/cov_all.py`.

| file | what |
|---|---|
| `experiments/stable_ac/cov/cov_all.py` | the enumerator of the family |
| `experiments/stable_ac/cov/run/run_cov_all.py` | the sweep runner |
| `experiments/stable_ac/cov/verify/verify_cov_all.py` | the checker of a sweep file |
| `experiments/stable_ac/cov/run/summarize_cov_all.py`, `plot_cov_all_control_vs_cov.py`, `table_cov_all_per_presentation.py` | the summaries, plot and table |
| `experiments/stable_ac/cov/run/aws_cov_all_box.sh` | the box script of the 100,000 run |
| `tests/stable_ac/test_cov_all.py` | its tests |

Reproduce / check there (repo root, `PYTHONPATH=.`, gunzip first):

    python3 -m experiments.stable_ac.cov.run.run_cov_all --budget 100 --workers N --path-sample 1
    python3 -m experiments.stable_ac.cov.verify.verify_cov_all FILE.jsonl --counts --dataset data/ms640_solved.txt --path-sample 1
    python3 -m experiments.stable_ac.cov.run.summarize_cov_all FILE.jsonl
    python3 -m experiments.stable_ac.cov.run.plot_cov_all_control_vs_cov FILE.jsonl
    python3 -m experiments.stable_ac.cov.run.table_cov_all_per_presentation FILE.jsonl

The budget 100,000 run was one autonomous AWS box per attempt, started from
`experiments/stable_ac/cov/run/aws_cov_all_box.sh` as EC2 user-data (settings and the launch
command are at the top of that file).

Budget 100 check: 114,682 rows, 14,051 one-pattern, 90,234 solved, 90,234 paths replayed through
`greedy_tests/spec` to the trivial presentation, 0 failures.

Budget 10,000 check (64 workers on a c7a.16xlarge, code at `99968da`): 114,682 rows, 14,051
one-pattern, 106,843 solved, 2,147 sampled paths replayed to the trivial presentation, 0 failures,
on the box and again on the downloaded file (`--counts --dataset data/ms640_solved.txt
--path-sample 0.02`). Every row solved within 100 nodes has the same `nodes_explored` and
`path_length` as in the budget 100 file. Search wall time 47.5 min (19.0 for subset 60 first,
28.5 for the other 580 presentations), 49.8 CPU-hours.

Budget 100,000 check (code at `f2ffd98`): 114,682 rows, 14,051 one-pattern, 111,878 solved, 2,263
sampled paths replayed to the trivial presentation, 0 failures, on the box and again on the
downloaded file. Every row solved within 10,000 nodes has the same `nodes_explored` and
`path_length` as in the budget 10,000 file, and no other row solves within 10,000. 335.2
CPU-hours. Two boxes wrote the file: 192 workers on a c7a.48xlarge (384 GB) returned 113,040 rows
and then stalled with 1,642 rows never returned (more chunks of 4 than workers, so chunks were
lost, not slow). The cause is inferred, not observed (no
console access): the other 1,642 rows, resumed from the same file with 96 workers on an
r7i.24xlarge (768 GB), peaked at about 560 GB, so 5.8 GB per worker with the path-recording
greedy, which 192 workers cannot have in 384 GB; a `multiprocessing.Pool` never returns the chunk
of a worker the kernel kills. Size the worker count by memory at this budget.

## Results

Presentations solved (of 640; subset 60 in brackets), oracle = best start of the family:

| budget | control | oracle, all starts | oracle, one-pattern starts |
|---|---|---|---|
| 100 | 455 (17) | 555 (34) | 555 (34) |
| 1,000 | 554 (29) | 604 (45) | 604 (45) |
| 10,000 | 606 (40) | 626 (52) | 626 (52) |
| 100,000 | 634 (54) | 640 (60) | 640 (60) |

No presentation changes outcome because of a start outside the one-pattern set, at any budget; on
19 presentations the best such start is 1 or 2 nodes cheaper than the best one-pattern start. At
10,000 the 20 presentations solved only from a CoV start are `pres_id` 568, 570, 573, 575, 578,
583, 584, 588, 596, 603, 604, 605, 610, 613, 628, 629, 630, 633, 634, 635, and the 14 no start
solves are 616-625 and 636-639. At 100,000 every presentation is solved from some start, the
control fails on 6 (`pres_id` 634-639, each solved by 16 or 17 of its starts), and the best start
of the full family beats the best one-pattern start on 21 presentations, by at most 59 nodes.
2,804 rows in 140 presentations are still unsolved.

Searches solved (of 114,682): 90,234 at 100 (455 control + 89,779 CoV), 101,108 at 1,000, 106,843
at 10,000 (606 + 106,237), 111,878 at 100,000 (634 + 111,244). There are 178 starts per presentation
on average, 5 to 10,740. The oracle presumes knowing the best start; its real price is the sum over
all starts of a presentation, a mean of 5,328 nodes at the 100 run, 164,759 at 10,000 and 657,198
at 100,000 (the runs took 1.1, 49.8 and 335.2 CPU-hours of search), against 16 to 1,663 for the
control's own search.

A random start against the control (`*_control_vs_cov`, each presentation weighted equally, a
start counts as cheaper when it solves and the control does not): at 100,000 it needs fewer nodes
33.7% of the time, the same 9.6%, more 52.4%, and is unsolved 4.2%; at 10,000 the split is 33.0 /
9.6 / 48.2 / 9.2 (the source README printed 48.3; the stored value is 0.4825 and the summaries print
48.2). The share that is cheaper stays near a third whatever the control costs.

| budget | cheaper | equal | dearer | unsolved |
|---|---:|---:|---:|---:|
| 100 | 26.2% | 9.5% | 31.6% | 32.7% |
| 1,000 | 30.9% | 9.6% | 41.8% | 17.7% |
| 10,000 | 33.0% | 9.6% | 48.2% | 9.2% |
| 100,000 | 33.7% | 9.6% | 52.4% | 4.2% |

**AC path or stable AC.** The files do not type a solve. By acx's typing (see
[the main README](../../../README.md#ac-path-or-stable-ac)), a start whose Aut(F2)-canonical form
`aut_canon_cov` equals `aut_canon_orig` is in the row's orbit, and its solve carries back to an
`ac_path` of elementary moves (aut-assisted); a start outside the orbit gives a `stable_cert`. 7,206
starts are in the orbit; of the 111,244 solved starts at 100,000, 6,856 are and 104,388 are not. The
best start of a presentation (the cheapest search that solved it, ties to the control), by that typing:

| budget | control (`ac_path`) | in the orbit (`ac_path`, aut-assisted) | outside (`stable_cert`) | unsolved |
|---|---:|---:|---:|---:|
| 100 | 0 | 269 | 286 | 85 |
| 1,000 | 1 | 304 | 299 | 36 |
| 10,000 | 3 | 323 | 300 | 14 |
| 100,000 | 3 | 329 | 308 | 0 |

Every presentation the control fails but some start solves (100, 50, 20 and 6 of them at the four
budgets) also has a solving start in its orbit, so none of these gains over the control needs a
`stable_cert`. The six rows 634 to 639, which the control leaves unsolved at 100,000 pops and cap 24,
stay unsolved at cap 64 and with no cap, so they are not a cap artifact.

**Cap.** The sweep predates the cap counters ([docs/CAP.md](../../../docs/CAP.md)): a row records only
the cap it ran at, never whether the cap dropped a child, so these files cannot show that the cap did
not decide a pop. The control ran at cap 24 and a start at `max(24, its longer relator + 16)`, 24 to
91 (109,336 of the 114,042 starts above 24). The caps differ between control and start, as in the
10,000-node numbers of [docs/RESULTS.md](../../../docs/RESULTS.md) section 5, which compares this
sweep with the default family of `acx.cov`.

Subset 60 is `pres_id` 0, 43, 48, 77, 141, 155, 201, 203, 217,
228, 247, 265, 288, 323, 327, 331, 333, 367, 380, 455, 496, 505, 521, 533, 538, 543, 544, 546,
548, 549, 565, 568, 573, 575, 578-581, 583, 586, 589, 596, 602, 605, 606, 609, 610, 622-625, 628,
632-639.
