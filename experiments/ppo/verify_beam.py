"""Certificate check for a beam jsonl: replay every solved row, prove it trivial.

`stable_ac/verify_results.py` exists because this repo does not believe a solve
count until something *other than the search* has re-derived it. The same
argument applies here, and more sharply: the number this branch exists to
produce is "how many of the 1190 does the policy solve", and it is produced by a
1024-wide beam whose bookkeeping (`seqs = seqs[parent]` gathered through 150
steps of dedup, no-op kills and visited-set pruning) is exactly the kind of code
that stays silent when it is wrong. A path that indexes the wrong parent still
looks like a path.

So this replays each solved row through `acs_spec` **only** -- the scalar
transliteration of `envs/ac_moves.py`, which shares no structure with the
batched `s_move` that produced the row -- starting from the presentation as read
off disk. The independence is the whole point: a bug in the batched move, or in
the beam's gather, cannot certify itself. Nothing here imports torch, so it runs
on a laptop over a jsonl mirrored back from Drive, with no GPU and no notebook.

Unsolved rows are checked too, for the opposite property: they must carry no
path. A `solved: false` row with moves in it means the terminal test and the
recorded sequence disagree, which would corrupt the mean path length even though
the solve count looked fine.

    .venv/bin/python3 -m experiments.ppo.verify_beam results/ppo/beam-*.jsonl
"""

import argparse
import glob
import json
import os
import sys

from experiments.ppo import acs_data, acs_spec
from experiments.ppo.results_table import parse_name


def dataset_and_length(path, dataset=None, max_length=None):
    """Which presentations the rows index, and the layout they were decoded in.

    Taken from the filename, because `beam_tag` puts it there precisely so a row
    can be traced back to its evaluation set. An explicit override exists for a
    file renamed through `BEAM_TAG`; guessing would be worse than refusing.
    """
    if dataset and max_length:
        return dataset, int(max_length)
    info = parse_name(os.path.splitext(os.path.basename(path))[0])
    if info is None:
        raise ValueError(
            f"{os.path.basename(path)} is not a beam jsonl name, so its evaluation "
            f"set is unknown -- pass --dataset and --max-length explicitly")
    return dataset or info["eval"], int(max_length or info["max_length"])


def verify_file(path, dataset=None, max_length=None, log=print):
    """Replay every row. Returns a summary; `failures` empty means certified."""
    stem, L = dataset_and_length(path, dataset, max_length)
    pres = acs_data.load_presentations(stem, L)

    rows, failures = [], []
    with open(path) as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((lineno, json.loads(line)))
            except ValueError:
                # `repair_jsonl` truncates a torn tail before the next append, so
                # a bad line here is real corruption, not a crash artefact.
                failures.append((lineno, None, "line is not valid json"))

    n_solved = n_verified = 0
    for lineno, row in rows:
        idx = row.get("presentation_idx")
        if not isinstance(idx, int) or not 0 <= idx < len(pres):
            failures.append((lineno, idx, f"presentation_idx outside {stem} (0..{len(pres) - 1})"))
            continue
        path_actions = row.get("path") or []
        if not row.get("solved"):
            if path_actions or row.get("path_length", -1) != -1:
                failures.append((lineno, idx, "unsolved row carries a path"))
            continue

        n_solved += 1
        if len(path_actions) != row.get("path_length"):
            failures.append((lineno, idx, f"path_length {row.get('path_length')} "
                                          f"!= {len(path_actions)} recorded moves"))
            continue
        # One pass, recording the FIRST step that terminates. Checking only the
        # last step would certify a path that solved early and wandered back to
        # trivial: it ends where it claims, but over-reports `path_length`, which
        # is the paper's second published column. The beam returns on its first
        # termination and so cannot emit one -- a mis-gathered `seqs[parent]`
        # could, and that is the failure this whole module exists to catch.
        state, first_term = [int(v) for v in pres[idx]], None
        for step, a in enumerate(path_actions, 1):
            state, _, term = acs_spec.step(state, int(a), L)
            if term and first_term is None:
                first_term = step
        if first_term is None:
            failures.append((lineno, idx, "replayed path does not reach a trivial presentation"))
        elif first_term != len(path_actions):
            failures.append((lineno, idx, f"a proper prefix of the path already solves "
                                          f"(at move {first_term} of {len(path_actions)})"))
        else:
            n_verified += 1

    log(f"{os.path.basename(path)}: {len(rows)} rows over {stem} (L={L}), "
        f"{n_solved} solved, {n_verified} certified by replay through acs_spec")
    for lineno, idx, why in failures[:20]:
        log(f"    FAIL line {lineno} idx {idx}: {why}")
    if len(failures) > 20:
        log(f"    ... and {len(failures) - 20} more")
    return {"file": path, "dataset": stem, "rows": len(rows), "solved": n_solved,
            "verified": n_verified, "failures": failures}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="beam jsonl files (globs allowed)")
    ap.add_argument("--dataset", help="override the evaluation set the filename names")
    ap.add_argument("--max-length", type=int, help="override the relator layout")
    args = ap.parse_args(argv)

    files = sorted({f for p in args.paths for f in (glob.glob(p) or [p])})
    if not files:
        print("no files matched")
        return 1
    bad = 0
    for f in files:
        result = verify_file(f, args.dataset, args.max_length)
        bad += len(result["failures"])
    print("ALL ROWS VERIFY" if not bad else f"{bad} FAILURES -- do not publish these numbers")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
