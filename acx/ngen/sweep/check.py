"""The independent verifier of a result directory (``python -m acx.ngen.sweep --verify N`` runs it)."""
import json
import os
import random

import numpy as np

from ... import data
from ...core.moves import decode_path
from ...search import search
from ...verify.replay import replay
from .config import COUNTERS, SweepConfig, ident_of, words_of
from .rows import finished_rows, load_row, outcome, row_path
from .words import combos, start, word_str


def verify(result_dir, recheck=0, seed=0, log=print):
    """Check the result directory ``result_dir``; return the failures (an empty list when it passes).

    Per row: ident and array shapes; control equals the null stabilisation, and the null's counters equal the
    control's (smallest score + ``extra``); pops in ``1..budget``; the cap-counter rules (``check_counters``); every
    stored path (control and sampled) replays on its start through ``acx.verify.replay``. Then ``recheck`` random
    cells re-run on the other backend must agree on solved, pops, path length and the counters.
    """
    with open(os.path.join(result_dir, "config.json")) as f:
        key = json.load(f)
    sc = SweepConfig.from_key(key["sweep"])
    rows = {r.id: r for r in data.rows(key["benchmark"])}
    words = words_of(sc)
    starts = combos(len(words), sc.extra)

    failures = []
    row_ids = finished_rows(result_dir)
    for row_id in row_ids:
        row = load_row(row_path(result_dir, row_id))

        def fail(message, row_id=row_id):
            failures.append(f"row {row_id}: {message}")

        if row["ident"] != ident_of(sc, row_id, rows[row_id].pres):
            fail("ident differs from the config")
            continue
        check_row(row, rows[row_id].pres, sc, words, starts, fail)
    failures += recheck_on_other_backend(result_dir, row_ids, rows, sc, words, starts, recheck, random.Random(seed))
    log(f"verify {result_dir}: {len(row_ids)} rows, {len(failures)} failures")
    return failures


def check_row(row, pres, sc, words, starts, fail):
    """The row-level checks of ``verify`` for one row file; each failure is passed to ``fail``."""
    control, null, budget = row["control"], row["null"], sc.search.budget
    if outcome(control) != outcome(null):
        fail("control != null stabilisation")
    for key in COUNTERS:
        # The Z_i never take part in a move: the same drops, with every score shifted by ``extra``.
        shifted = key == "cap_dropped_min_total" and control[key] is not None
        want = control[key] + sc.extra if shifted else control[key]
        if null[key] != want:
            fail(f"{key} differs between the control ({control[key]}) and the null stabilisation ({null[key]})")
    wrong_shape = [k for k in ("nodes", "path_len", "min_total", *COUNTERS) if row[k].shape != (len(starts),)]
    if wrong_shape:
        fail(f"arrays {wrong_shape} have the wrong shape")
        return
    solved, pops = row["path_len"] >= 0, row["nodes"].astype(np.int64)
    if (pops > budget).any() or (pops < 1).any():
        fail("pops outside 1..budget")
    # The relators Z.w are within the cap (SweepConfig), so only a relator of the row itself can put the start over it.
    cap = sc.search.cap
    over_cap = cap is not None and max(map(len, pres.normal(sc.search.cyclic).rels)) > cap
    check_counters(row, solved, pops, budget, sc, fail, start_over_cap=over_cap)
    try:
        check_paths(row, pres, sc, words, starts, solved, pops, fail)
    except ValueError as e:
        fail(f"replay: {e}")


def check_paths(row, pres, sc, words, starts, solved, pops, fail):
    """Replay the control's path and every sampled path on its start (``ValueError`` when one does not replay)."""
    cyclic, cap = sc.search.cyclic, sc.search.cap
    if row["control"]["solved"]:
        replay(pres, decode_path(row["control"]["path"]), cyclic=cyclic, cap=cap)
    for kept in row["paths"]:
        index = kept["index"]
        chosen = [words[j] for j in starts[index]]
        if kept["word"] != word_str(chosen) or not solved[index] or int(pops[index]) != kept["pops"]:
            fail(f"sampled path {index} does not match the arrays")
            continue
        replay(start(*pres.rels, chosen), decode_path(kept["path"]), cyclic=cyclic, cap=cap)


def recheck_on_other_backend(result_dir, row_ids, rows, sc, words, starts, n, rng):
    """``n`` random cells re-run on the other backend; the failures (solved, pops, path length, counters)."""
    other = "spec" if sc.search.backend == "fast" else "fast"
    failures = []
    for _ in range(n if row_ids else 0):
        row_id, index = rng.choice(row_ids), rng.randrange(len(starts))
        row = load_row(row_path(result_dir, row_id))
        result = search(start(*rows[row_id].pres.rels, [words[j] for j in starts[index]]),
                        sc.search.replace(backend=other))
        got = (bool(result.solved), result.pops, -1 if result.path_length is None else result.path_length)
        want = (bool(row["path_len"][index] >= 0), int(row["nodes"][index]), int(row["path_len"][index]))
        counters = {k: -1 if result.stats[k] is None else result.stats[k] for k in COUNTERS}
        if got != want or any(counters[k] != int(row[k][index]) for k in COUNTERS):
            failures.append(f"row {row_id} start {index}: {other} backend gives {got} {counters}, file has {want}")
    return failures


def check_counters(row, solved, pops, budget, sc, fail, start_over_cap=False):
    """The relations the cap counters must satisfy.

    Per search: ``dropped`` children were not pushed; ``bind`` is the first pop (1 = the start) at which a dropped
    child would have been popped, or -1; ``would`` counts the dropped children that would have been popped; ``need``
    is the cap needed to keep them, or -1; ``smallest`` is the smallest total length of a dropped child, or -1.
    ``start_over_cap``: a relator of the start is over the cap. The start can then be the only child the cap drops,
    and the counters leave it out (it is no new state), so a dry search may have drops and no bind.
    """
    dropped = row["cap_dropped"].astype(np.int64)
    smallest, bind, would, need = (row[k].astype(np.int64) for k in
                                   ("cap_dropped_min_total", "cap_first_bind", "cap_would_pop", "cap_needed"))
    cap, has_bind = sc.search.cap, bind >= 0
    frontier_emptied = has_bind & (bind == pops + 1)
    rules = [
        (((smallest >= 0) != (dropped > 0)).any(), "a smallest dropped score iff something was dropped"),
        (cap is not None and ((smallest >= 0) & (smallest <= cap)).any(),
         "a dropped child whose total is within the cap"),
        ((has_bind & (dropped == 0)).any(), "a bind without a drop"),
        ((has_bind & ((bind < 2) | (bind > pops + 1))).any(), "a bind outside 2..pops+1"),
        ((frontier_emptied & (pops >= budget)).any(), "a frontier-empty bind at the full budget"),
        ((frontier_emptied & solved).any(), "a frontier-empty bind on a solved search"),
        (not start_over_cap and (~solved & (pops < budget) & (dropped > 0) & ~has_bind).any(),
         "an unsolved search below the budget with drops and no bind"),
        ((would > dropped).any(), "cap_would_pop above cap_dropped"),
        (((would > 0) != has_bind).any(), "cap_would_pop > 0 must hold exactly when there is a bind"),
        (((would > 0) != (need >= 0)).any(), "cap_needed must be set exactly when cap_would_pop > 0"),
        (cap is not None and ((need >= 0) & (need <= cap)).any(), "cap_needed within the cap"),
    ]
    for violated, message in rules:
        if violated:
            fail(message)
