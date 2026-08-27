"""Benchmark-60 held out of the PPO training data, and the pin that survives it.

The standing rule is that every evaluation happens on `benchmark/subsets/benchmark_subset_60.csv`.
All 60 of those presentations are in `1190MS`, and **54 of them are in `AC19_extended`, every one
inside the first 634 lines** -- the block `ppo_ac_s.py:98` pins deterministically, one env per row,
for the whole run. So a model trained on the shipped file has seen 54/60 of its own test set as a
dedicated training target. This module removes them.

**The trap this exists to close.** `acs_data.ms_prefix_length` derives the pin count by walking the
*leading lines* of the training file against `1190MS` until they differ. Benchmark row `bin 0` is
line **0** of both files, so the first deletion stops that walk immediately and the derived pin
collapses 634 -> **0**: pinning silently switches off, in every arm, and the training recipe changes
far more than the reward under test. `tests/ppo/test_shaped_arms.py` asserts the naive walk really does
return 0 on the filtered file, so the trap stays visible rather than becoming folklore.

`ms_prefix_length` here is the fix, and it is a derivation rather than a constant: walk the training
file from the top counting rows that are *members* of `1190MS`, stop at the first that is not. On the
shipped file that reproduces the prefix walk exactly (634); on the filtered file it gives 580, which
is 634 - 54, without anything having been written down. It stays correct if the benchmark changes.

What this does **not** fix: rows elsewhere in the 156k that are Aut-equivalent to a benchmark row.
Exact-match removal cannot see them. That only touches a generalisation claim -- the arm-vs-arm
comparison is immune, since both arms train on the same file -- and it is stated as a limitation
rather than papered over.
"""

import csv
import os

from experiments.ppo import acs_data

BENCHMARK_CSV = os.path.join(acs_data.ROOT, "benchmark", "subsets", "benchmark_subset_60.csv")
HELDOUT_SUFFIX = "_ho60"
_SYM = {"x": 1, "X": -1, "y": 2, "Y": -2}


def _pad(word, max_length):
    v = [_SYM[c] for c in word]
    if len(v) > max_length:
        raise ValueError(f"relator of length {len(v)} does not fit in max_length={max_length}")
    return v + [0] * (max_length - len(v))


BENCH_STEM = "benchmark60"


def benchmark_rows():
    """The 60 evaluation rows, in CSV order. Row `i` is `presentation_idx` `i` in a beam."""
    with open(BENCHMARK_CSV) as fh:
        return list(csv.DictReader(fh))


def benchmark_states(max_length=24):
    """The 60 evaluation presentations, in the flat padded layout the data files use."""
    return {tuple(_pad(r["r1"], max_length) + _pad(r["r2"], max_length))
            for r in benchmark_rows()}


def build_benchmark_dataset(max_length=24, log=print):
    """Write `data/benchmark60.txt` so the ordinary beam stage can evaluate on it.

    Deliberately a *dataset*, not a new stage: `beam_eval` already resumes, verifies
    every solved row and reports, so pointing it at a 60-row file gets all of that for
    free. Row order is CSV order, which is what makes `presentation_idx` in the beam
    jsonl joinable back to `pres_id` / `bin` / `aut_class`.
    """
    path = os.path.join(acs_data.ROOT, "data", BENCH_STEM + ".txt")
    rows = benchmark_rows()
    want = "".join(str(_pad(r["r1"], max_length) + _pad(r["r2"], max_length)) + "\n"
                   for r in rows)
    if not (os.path.exists(path) and open(path).read() == want):   # CONTENT, not row count
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(want)
        os.replace(tmp, path)
    log(f"{BENCH_STEM}: {len(rows)} evaluation presentations "
        f"({len({r['aut_class'] for r in rows})} Aut orbits)")
    return path


def ms_prefix_length(stem, max_length=24, rows=None):
    """Envs to pin: the leading rows of `stem` that are `1190MS` presentations.

    Filter-aware where `acs_data.ms_prefix_length` is not. Comparison is on the padded
    layout at a single `max_length`, so it does not care what the two files were padded to.

    `rows` lets a caller that already holds the file in memory skip re-reading it --
    `acs_data.read_raw` is uncached and `literal_eval`s every line, so re-reading the
    156k-row training file is the expensive part of this function, not the walk.
    """
    ms = {tuple(acs_data.repad(p, max_length)) for p in acs_data.read_raw(acs_data.MS_STEM)}
    rows = acs_data.read_raw(stem) if rows is None else rows
    n = 0
    while n < len(rows) and tuple(acs_data.repad(rows[n], max_length)) in ms:
        n += 1
    return n


def heldout_stem(stem):
    return stem + HELDOUT_SUFFIX


def build(stem="AC19_extended", max_length=24, out_stem=None, log=print):
    """Write `data/<stem>_ho60.txt` -- `stem` with every benchmark-60 row removed.

    Idempotent: an existing file whose CONTENT already matches is left alone, so a Colab
    restart does not rewrite 156k lines. Comparing row *count* alone is not enough -- a
    stale file that happens to be the same length would survive as "already built", and
    the returned counts (computed in memory either way) would look right while the file a
    training run actually reads was wrong. Returns `(path, n_removed, n_pinned)`.
    """
    out_stem = out_stem or heldout_stem(stem)
    out_path = os.path.join(acs_data.ROOT, "data", out_stem + ".txt")
    drop = benchmark_states(max_length)
    rows = acs_data.read_raw(stem)
    keep = [r for r in rows if tuple(acs_data.repad(r, max_length)) not in drop]
    n_removed = len(rows) - len(keep)

    want = "".join(str(list(acs_data.repad(r, max_length))) + "\n" for r in keep)
    if not (os.path.exists(out_path) and open(out_path).read() == want):
        tmp = out_path + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(want)
        os.replace(tmp, out_path)

    # both walks reuse the lists already in memory: `acs_data.ms_prefix_length(stem)` here
    # would re-`literal_eval` the whole training file purely to print the "was" number,
    # and an f-string builds eagerly even when `log` is a no-op.
    n_pinned = ms_prefix_length(out_stem, max_length, rows=keep)
    was = ms_prefix_length(stem, max_length, rows=rows)
    log(f"{out_stem}: {len(rows)} -> {len(keep)} rows ({n_removed} benchmark-60 rows "
        f"removed); {n_pinned} envs pinned (was {was})")
    return out_path, n_removed, n_pinned
