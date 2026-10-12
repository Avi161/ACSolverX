"""One row of the sweep: search every start of the pool, and read or write the row's ``.npz`` file."""
import json
import os
import time

import numpy as np

from ...core.moves import encode_path
from ...core.words import Presentation
from ...search import search
from .config import COUNTERS, SweepError, ident_of, words_of
from .words import combos, sampled, start, word_str


def search_record(result):
    """One search as a record: solved, pops, path length (None unsolved), smallest total and the cap counters."""
    return {"solved": result.solved, "pops": result.pops, "path_len": result.path_length,
            "min_total": result.stats["min_total"], **{k: result.stats[k] for k in COUNTERS}}


def outcome(record):
    """What the control and the null stabilisation must agree on."""
    return record["solved"], record["pops"], record["path_len"]


def search_control_and_null(r1, r2, sc, row_id):
    """The 2-generator control and the null stabilisation of a row, as records; they must agree."""
    control_result = search(Presentation(2, (r1, r2)), sc.search)
    control = search_record(control_result)
    null = search_record(search(start(r1, r2, [()] * sc.extra), sc.search))
    if outcome(control) != outcome(null):
        raise SweepError(
            f"row {row_id}: the control {outcome(control)} and the null stabilisation {outcome(null)} differ")
    if control_result.solved:
        control["path"] = encode_path(control_result.path)
    return control, null


def search_starts(row_id, pres, sc):
    """Search every start of the pool; return the records (by start index) and the sampled solved paths."""
    words = words_of(sc)
    records, kept_paths = [], []
    for index, combo in enumerate(combos(len(words), sc.extra)):
        chosen = [words[j] for j in combo]
        result = search(start(*pres.rels, chosen), sc.search)
        records.append(search_record(result))
        if result.solved and sampled(row_id, word_str(chosen), sc.sample):
            kept_paths.append({"index": index, "word": word_str(chosen), "pops": result.pops,
                               "path": encode_path(result.path)})
    return records, kept_paths


def sweep_row(row_id, pres, sc):
    """The arrays of one row file: the control, the null stabilisation and every start of the pool (by index)."""
    began = time.perf_counter()
    control, null = search_control_and_null(*pres.rels, sc, row_id)
    records, kept_paths = search_starts(row_id, pres, sc)

    def column(key, dtype=np.int32):
        return np.array([-1 if r[key] is None else r[key] for r in records], dtype)

    return {"nodes": column("pops", np.uint16), "path_len": column("path_len", np.int16),
            "min_total": column("min_total"), **{k: column(k) for k in COUNTERS},
            "control": np.array(json.dumps(control)), "null": np.array(json.dumps(null)),
            "paths": np.array(json.dumps(kept_paths)), "seconds": np.float32(time.perf_counter() - began),
            "ident": np.array(ident_of(sc, row_id, pres))}


def row_path(result_dir, row_id):
    """The row file of ``row_id`` under the result directory ``result_dir``."""
    return os.path.join(result_dir, "rows", f"{row_id}.npz")


def finished_rows(result_dir):
    """The ids of the row files in ``result_dir``, sorted; a leftover ``<id>.npz.tmp<pid>.npz`` is not a row."""
    names = os.listdir(os.path.join(result_dir, "rows"))
    return sorted(name[:-4] for name in names if name.endswith(".npz") and ".npz.tmp" not in name)


def load_row(path):
    """A row file as a dict of arrays, with the JSON records parsed and ``ident`` as a string."""
    with np.load(path) as z:
        row = {k: z[k] for k in z.files}
    for key in ("control", "null", "paths"):
        row[key] = json.loads(str(row[key]))
    row["ident"] = str(row["ident"])
    return row


def sweep_row_file(task):
    """Sweep one row into its file, unless the file is there (then it must belong to this run).

    ``task`` is ``(result_dir, row_id, pres, sc)``. The file is written atomically, so a killed run resumes.
    """
    result_dir, row_id, pres, sc = task
    path, ident = row_path(result_dir, row_id), ident_of(sc, row_id, pres)
    if os.path.exists(path):
        found = load_row(path)["ident"]
        if found != ident:
            raise SweepError(f"{path} is not from this run: has {found}, expected {ident}")
        return
    arrays = sweep_row(row_id, pres, sc)
    tmp = f"{path}.tmp{os.getpid()}.npz"
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)
