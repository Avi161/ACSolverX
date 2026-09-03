"""Lift the 1M residuals to a 5,000,000-node budget — stride-chunked for Colab.

THE ROW LISTS
-------------
What survived the 1,000,000-node pass (``run_leftovers_1m``, results in
``results/heuristic_search/leftovers_1m/RESULTS.md``), shipped beside the 100k
lists with the presentations inline:

    unsolved_1m_baseline.csv    88 rows   greedy / total-length ordering
    unsolved_1m_s20_mk2.csv     14 rows   L + 20*S + 2*MK   (subset of the 88)

Both are ``solved == false`` read off the 1M jsonl, with each orbit's membership
joined back from the 100k lists so the schema stays the one every wave has used.
``tests/test_leftovers_5m.py`` re-derives them rather than trusting them.

STRIDE CHUNKING
---------------
88 single-worker rows at 5M is several Colab-days, so the greedy arm splits
across four notebooks the way the u124 campaign did: ``CHUNKS=4``,
``CHUNK_INDEX=k`` takes rows ``[k-1::4]`` — interleaved, not contiguous, so the
name-ordered difficulty gradient spreads evenly and no chunk is "the hard one".
22 rows per chunk, disjoint by construction, union = all 88. The s20_mk2 arm is
14 rows and runs as one notebook.

WHY ONE WORKER
--------------
The engine's own arena formula gives ~35 GB reserved per search at 5M, and the
hard tail discovers ~100 states per pop (measured: a 6M-state grow by 60,000
pops on ``ac19_7284``), so a full-budget row can genuinely touch ~40 GB. On a
51 GB runtime that is one worker — parallelism comes from the chunking, not the
pool. The dedup is already the memory trick: FNV-hashed nibble rows in an
open-addressing int32 table at ~79 B/state (``greedy_compact``). Anything
leaner means fingerprint-only visited sets, which make the search probabilistic
— a hash collision silently skips a state — and nothing in this screen's chain
of results is probabilistic. Not done here.

    PYTHONPATH=. python3 -m experiments.search.run_leftovers_5m \
        --arm greedy --chunks 4 --chunk-index 1 --smoke

THE SELF-CHECK MOVES TO 1,000,000
---------------------------------
Same engine, same cap, same config: a search at budget B is the first B pops of
any longer search, so a row that failed at 1,000,000 cannot come back solved at
or below 1,000,000 now. A row that does means the wrong search ran.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import queue as _queue
import re
import time

from experiments.search.run_leftovers_1m import (
    ARMS, HAVE_HCOMPACT, MAX_RELATOR_LENGTH, SCREEN_DIR, _available_gb, _beat,
    _done, _ensure_trailing_newline, _in_search_heartbeat, _iter_results, _job,
    _mirror, _seed_from_mirror, est_gb, load_rows as _load_1m_rows, read_rows,
    resolve_arm, resolve_workers,
)

# Bumped whenever a change shifts the ENGINE'S MEMORY PROFILE (arena layout,
# reservation sizing, per-state arrays). Each finished row records the
# generation it ran under, and the governor seeds its learned peaks only from
# same-generation rows -- a peak measured under an old memory profile must
# never widen (or narrow) the gate for the profile running now.
#   gen 2: adaptive row width + reservations honored as-is + np.empty parent.
#   gen 3: the rate-floor RLIMIT cap in plan_memory. Under a rate floor a
#          row can no longer complete THROUGH a grow doubling, so its peak is
#          bounded by the width-repack transient. Gen-2 rows measured on a
#          big box before the cap carry doubling peaks (u124 aca_37: 286.4 GB
#          on 493 GiB) that no gen-3 row can produce; seeding them pinned
#          every box to one lane. Not evidence about this profile: skipped.
ENGINE_MEM_GEN = 3

# The 5M stage runs a WIDER corridor than the 1M wave did. Two caps therefore
# coexist and must never be conflated:
#   MAX_RELATOR_LENGTH (48) -- what the 1M baseline ran at. The "no row may
#       solve below 1M" floor is a statement about THAT search, so the check
#       below keys off this, not off whatever this stage is running.
#   MRL_5M (64)             -- what this stage runs at.
# At a wider cap an early solve is legitimate and is the interesting result:
# it is a row the wider corridor cracked cheaply.
MRL_5M = 64

# Every row records its solution path. `path_length` alone is not the result:
# the move sequence IS the certificate, and it is unrecoverable after the fact
# -- the arena is overwritten, so a finished run without it cannot be mined for
# paths later, only re-run. 8 B/state buys it.
TRACK_PATH = True

NODE_BUDGET_5M = 5_000_000
CHECKPOINTS_5M = (1_000_000, 2_000_000, 5_000_000)
FLOOR_5M = 1_000_000          # every input row failed at 1M; none may solve below

# arm -> (the 1M-unsolved CSV, its row count, default chunk count)
SPEC_5M = {
    "greedy": {"csv": "unsolved_1m_baseline.csv", "n_rows": 88, "chunks": 4},
    "s20_mk2": {"csv": "unsolved_1m_s20_mk2.csv", "n_rows": 14, "chunks": 1},
}


U124_CSV = os.path.join(os.path.dirname(os.path.dirname(SCREEN_DIR)),
                        "stable_ac", "fable", "aca_124.csv")

# A campaign is a row list plus the budget/cap it is run at and whether a prior
# run established a floor on it. Keeping these together is what stops the AC19
# floor claim -- "nothing on this list solves under 1M" -- from being applied to
# a set it says nothing about.
CAMPAIGNS = {
    "ac19": {
        "label": "AC19 1M residuals at 5M",
        "spec": None,                     # per-arm, from SPEC_5M
        "budget": NODE_BUDGET_5M,
        "mrl": MRL_5M,
        "floor": FLOOR_5M,                # every row here failed at 1M
        "floor_mrl": MAX_RELATOR_LENGTH,  # ... at cap 48
        "prefix": "leftovers_5m",
        "ids_stem": "5m",             # legacy names the live run already writes
        "checkpoints": CHECKPOINTS_5M,
        # None = the est_states-based reservation this campaign already runs
        # under; changed mid-flight it would alter the live boxes' sizing.
        "states_per_node": None,
    },
    "u124": {
        "label": "124 unsolved Miller-Schupp AC classes at 10M",
        "spec": {"csv": U124_CSV, "n_rows": 124, "chunks": 1},
        "budget": 10_000_000,
        "mrl": 64,
        # No prior run of THIS search established a floor on this set, so there
        # is no "impossible early solve" to alarm on -- an early solve here is
        # simply a result. The u124 sweep on the stable-ac branch was a
        # thickenability study, a different question entirely.
        "floor": None,
        "floor_mrl": None,
        "prefix": "u124_10m",
        "ids_stem": "u124_10m",       # never clobbers the AC19 ids files
        "checkpoints": (1_000_000, 5_000_000, 10_000_000),
        # Reservation floor, in discovered states per popped node. The
        # ladder of this number is the campaign's memory history: 110
        # (AC19's worst + 10%) was beaten by u124's own first two rows
        # (aca_0 ~111/node, aca_1 ~123/node -- both died in the grow
        # doubling, which cannot fit under the child's RLIMIT_AS however
        # much physical RAM is free); 150 covered those with 22% margin;
        # aca_4's live trajectory then sat AT that floor (~150-165 est).
        # 168 seated three lanes on the 493 GiB r6a.16xlarge and was then
        # beaten by aca_38: 186.42 and 186.36 states/node on two independent
        # deaths (identical to four figures -- the search is deterministic,
        # so an over-floor row dies at the same pop on every attempt). The
        # floor stays at 168 on purpose: raising it to cover one row in
        # twenty costs a lane on EVERY row (worst ~200 GB at 209 vs 161 at
        # 168), so over-floor rows die cleanly once, are deferred rather
        # than retried at the same sizing (see _deferred_exhausted), and
        # run in a second pass with STATES_PER_NODE raised -- 209 for the
        # aca_38 class -- which keeps the hash table at 16 GiB (it doubles
        # past 214/node). On any machine plan_memory's width-repack
        # transient clip has the last word, so this constant is safe
        # everywhere; the rate-floor RLIMIT cap keeps every over-floor
        # death clean on big boxes too.
        "states_per_node": 168,
    },
}


def resolve_campaign(name):
    key = str(name or "ac19").strip().lower()
    if key not in CAMPAIGNS:
        raise KeyError(f"unknown campaign {name!r}; known={sorted(CAMPAIGNS)}")
    return key, CAMPAIGNS[key]


def campaign_spec(campaign, arm):
    """``{csv, n_rows, chunks}`` for this arm under this campaign."""
    ckey, c = resolve_campaign(campaign)
    if c["spec"] is not None:
        return c["spec"]
    key, _ = resolve_arm(arm)
    spec = dict(SPEC_5M[key])
    spec["csv"] = os.path.join(SCREEN_DIR, spec["csv"])
    return spec


def load_rows_5m(arm, csv_path=None, campaign="ac19"):
    """``([{name, r1, r2, ...}], path)`` — this campaign's row list, in file order."""
    key, _ = resolve_arm(arm)
    spec = campaign_spec(campaign, key)
    path = csv_path or spec["csv"]
    rows, used = _load_1m_rows(key, csv_path=path)
    if csv_path is None and len(rows) != spec["n_rows"]:
        raise RuntimeError(
            f"{os.path.basename(path)} has {len(rows)} rows, expected "
            f"{spec['n_rows']} -- stale clone; pull the branch before running.")
    return rows, used


def stride_chunk(rows, chunks, chunk_index):
    """Rows ``[chunk_index-1::chunks]`` — the u124 campaign's interleaved split.

    Interleaved rather than contiguous so a difficulty gradient in file order
    spreads across every chunk instead of concentrating in one. The chunks are
    disjoint and their union is the full list, both pinned by tests.
    """
    chunks = int(chunks)
    chunk_index = int(chunk_index)
    if chunks < 1:
        raise ValueError(f"chunks must be >= 1, got {chunks}")
    if not 1 <= chunk_index <= chunks:
        raise ValueError(f"chunk_index must be in [1, {chunks}], got {chunk_index}")
    return rows[chunk_index - 1::chunks]


def unsolved_at_1m(arm):
    """The arm's 1M leftovers re-derived from the 1M jsonl, sorted by name.

    The unsolved_1m CSVs are supposed to be exactly this; deriving it again is
    what lets a test (and a notebook's SETUP) check them instead of trusting them.
    """
    key, _ = resolve_arm(arm)
    path = os.path.join(
        os.path.dirname(SCREEN_DIR), "leftovers_1m",
        f"leftovers_1m_{key}_b1000000_mrl48.jsonl")
    rows = read_rows(path)
    if not rows:
        raise FileNotFoundError(f"1M jsonl missing or empty: {path}")
    return sorted(r["name"] for r in rows if not r.get("solved"))


def out_path_5m(arm, out_dir, chunks, chunk_index,
                budget=NODE_BUDGET_5M, mrl=MRL_5M, campaign="ac19"):
    key, _ = resolve_arm(arm)
    _, c = resolve_campaign(campaign)
    tag = f"_c{int(chunk_index)}of{int(chunks)}" if int(chunks) > 1 else ""
    return os.path.join(
        out_dir, f"{c['prefix']}_{key}{tag}_b{budget}_mrl{mrl}.jsonl")


def classify_5m(rows, budget=NODE_BUDGET_5M, checkpoints=CHECKPOINTS_5M,
                floor=FLOOR_5M):
    """Split result rows; flag any solve at or below the 1M floor as impossible.

    A name can appear more than once when a crashed row was retried: keep one
    record per name, preferring any finished record over an error record.
    """
    best = {}
    for r in rows:
        n = r.get("name")
        if n is None:
            continue
        prev = best.get(n)
        if prev is None or (prev.get("error") and not r.get("error")):
            best[n] = r
    rows = list(best.values())
    solved, unsolved, suspicious = [], [], []
    errored = [r["name"] for r in rows if r.get("error")]
    for r in rows:
        if r.get("solved") and int(r["nodes_explored"]) <= budget:
            solved.append(r["name"])
            if int(r["nodes_explored"]) <= floor:
                suspicious.append(r["name"])
        else:
            unsolved.append(r["name"])
    return {
        "n": len(rows),
        "solved_at_5m": solved,
        "unsolved_at_5m": unsolved,
        "errored": errored,
        "solved_at_or_below_1m": suspicious,
        "anytime": {c: sum(1 for r in rows
                           if r.get("solved") and int(r["nodes_explored"]) <= c)
                    for c in checkpoints},
    }


# ------------------------------------------------------ Edge Compact crash guards
#
# The first 5M sessions crashed outright: a CPU-limit kill or a RAM overload
# took the whole kernel with it, because the search ran IN the driver process
# and hcompact's ``_grow`` doubles its arrays with a copy -- old and new coexist,
# and at 5M that transient is what the OOM killer shoots. The repo already has
# the two guards for this, and they are what is used here -- no new engine:
#
#   * ``run_ab``'s ``__error__``-row pattern: a failed row becomes a recorded
#     row the parent reports and skips, "resume retries it later". Here every
#     row runs in its OWN spawned process; if that child is OOM-killed, hits a
#     CPU/timeout kill, or raises, the parent writes an ``error`` row and moves
#     to the next presentation. The session never dies with a row.
#   * ``hcompact``'s own ``reserve_states`` knob: the reservation is clipped to
#     what this machine's free RAM actually holds, and the child's address
#     space is capped (RLIMIT_AS) just under free RAM -- so a ``_grow`` that
#     would have invoked the OOM killer instead raises MemoryError inside the
#     child, which is caught and recorded. A kill becomes a diagnosis.
#
# Error rows never satisfy resume (``_done_ok``), so a crashed row is retried
# on the next invocation -- on this machine or a bigger one.

ROW_TIMEOUT_DEFAULT = None       # seconds per row; None = no CPU-time kill

# Address-space headroom held back from the width-repack transient bound in
# plan_memory: interpreter + numba runtime + MemAvailable estimation noise.
_TRANSIENT_MARGIN_GB = 10.0

# What the child reports when the memory guard stops a row. The prefix is
# stable (status tools grep it); the engine appends the measurement.
_EXHAUSTION_TEXT = ("MemoryError: the memory guard stopped this row before "
                    "the OOM killer could -- it needs a bigger machine")
_EXHAUSTION_RE = re.compile(
    r"reservation exhausted at ([\d,]+) states after ([\d,]+) pops")


def _floor_for(camp, log=print):
    """The campaign's states-per-node floor, with ``STATES_PER_NODE`` in the
    environment overriding it. Honored only for a campaign that HAS a floor:
    AC19's est-based sizing must never pick up a u124 knob by accident."""
    base = camp.get("states_per_node")
    env = os.environ.get("STATES_PER_NODE")
    if base and env:
        try:
            v = int(env)
        except ValueError:
            raise SystemExit(f"STATES_PER_NODE={env!r} is not an integer")
        if v != base:
            log(f"  floor   : STATES_PER_NODE={v} overrides the campaign's "
                f"{base} states/node")
        return v
    return base


def _exhaustion_info(err):
    """``(states, pops)`` from a reservation-exhaustion message, or None."""
    m = _EXHAUSTION_RE.search(err or "")
    if not m:
        return None
    return (int(m.group(1).replace(",", "")),
            int(m.group(2).replace(",", "")))


def _error_record(row, arm, budget, mrl, err, seconds, reserve_states):
    """The row a crashed child leaves behind. An exhaustion death also
    records the sizing it died under and the rate it measured, so the next
    invocation can tell a retry that will succeed from one that will not."""
    rec = {"name": row["name"], "arm": arm, "r1": row["r1"], "r2": row["r2"],
           "budget": budget, "max_relator_length": mrl,
           "solved": False, "error": err, "seconds": round(seconds, 3)}
    if reserve_states:
        rec["reserve_states"] = int(reserve_states)
    info = _exhaustion_info(err)
    if info:
        states, pops = info
        rec["exhausted_states"] = states
        rec["exhausted_nodes"] = pops
        rec["states_per_node_measured"] = round(states / max(pops, 1), 2)
    return rec


def _deferred_exhausted(path, reserve_states, budget):
    """Rows whose LATEST record is a reservation-exhaustion death that this
    run's reservation would repeat.

    The search is deterministic, so such a retry dies at the same pop
    (aca_38: 186.42 then 186.36 states/node, ~2.5 h each time, first in the
    queue on every restart). A death that carries its measurement is
    retried only when the current reservation covers ``rate x budget`` --
    "bigger than last time" is not enough: aca_38 died at 1.67B, a 512 GB
    box reserves 1.68B, and it needs 1.86B. A death without the measurement
    (a record from before the field existed) is retried only when the
    recorded reservation is below the current one, and assumed same-sized
    when it records none. ``RETRY_EXHAUSTED=1`` forces every deferred row
    back into the queue (the second pass). Returns ``{name: reason}``."""
    if os.environ.get("RETRY_EXHAUSTED"):
        return {}
    latest = {}
    for r in read_rows(path):
        if "name" in r:
            latest[r["name"]] = r              # file order: later wins
    have = int(reserve_states or 0)
    out = {}
    for n, r in latest.items():
        err = r.get("error") or ""
        if not err.startswith(_EXHAUSTION_TEXT):
            continue
        states, pops = r.get("exhausted_states"), r.get("exhausted_nodes")
        if states and pops:
            rate = states / pops
            need = int(rate * (r.get("budget") or budget) * 1.01)
            if have >= need:
                continue                        # this sizing covers it
            out[n] = (f"measured {rate:.1f} states/node, needs "
                      f">= {need:,} states; this run reserves {have:,}")
            continue
        prior = r.get("reserve_states")
        if prior is not None and have and prior < have:
            continue                            # sizing grew: worth the retry
        out[n] = "rate unmeasured (legacy record); same sizing as its death"
    return out


def _done_ok(path):
    """Names of rows that FINISHED -- error rows do not count as done."""
    return {r["name"] for r in read_rows(path)
            if "name" in r and not r.get("error")}


def _sibling_results(out, prefix, key):
    """Populated result files for the SAME campaign+arm under a DIFFERENT
    name -- the signature of the worst silent failure this pipeline has: a
    drifted name component (budget, mrl, chunk tag) makes resume see an
    empty history and re-run every finished row while looking perfectly
    healthy. Smoke-scale files (budget < 100k) are expected siblings and
    ignored."""
    import glob
    got = []
    for p in glob.glob(os.path.join(os.path.dirname(out) or ".",
                                    f"{prefix}_{key}*_b*_mrl*.jsonl")):
        if os.path.abspath(p) == os.path.abspath(out):
            continue
        m = re.search(r"_b(\d+)_mrl", os.path.basename(p))
        if m and int(m.group(1)) < 100_000:
            continue
        if _done_ok(p):
            got.append(p)
    return sorted(got)


def plan_memory(budget=NODE_BUDGET_5M, mrl=MRL_5M,
                available_gb=None, states_per_node=None, log=print):
    """``(mem_limit_bytes, reserve_states)`` sized to THIS machine.

    Uses the engine's own sizing pieces (``est_states``/``row_width``/slack) --
    the reservation is the engine default when it fits, and clipped to free RAM
    when it does not, with a note that clipped rows fail cleanly on MemoryError
    rather than by OOM kill. Returns ``(None, None)`` without the engine.
    """
    if not HAVE_HCOMPACT:
        return None, None
    from experiments.search.greedy_compact import (
        _RESERVE_SLACK, est_states, row_width)
    avail = available_gb if available_gb is not None else _available_gb()
    limit_gb = max(avail - 2.0, 3.0)
    per_state = row_width(mrl) + 31 + (8 if TRACK_PATH else 0)
    default_n = int(est_states(budget) * _RESERVE_SLACK) + 4 * (mrl + 1) ** 2
    if states_per_node:
        # A measured discovery-rate floor beats the est_states curve: AC19's
        # fattest rows hit the est-based reservation before their budget and
        # each paid a grow transient that DOUBLED their peak. Reserving for
        # the measured worst rate means grow never fires and a row's peak is
        # its honest steady state.
        default_n = max(default_n,
                        int(states_per_node * budget) + 4 * (mrl + 1) ** 2)
    cap_n = int(max(limit_gb - 2.5, 1.0) * 0.95 * 2 ** 30 / per_state)
    # The width ladder's LAST repack (previous rung -> full width) holds BOTH
    # arenas at once, so a widening row's address-space peak is the repack,
    # not the steady worst -- aca_1 measured it at 158.0 GB VmHWM on a 1.50B
    # reserve. A reservation whose repack cannot fit under this box's
    # RLIMIT_AS turns every widening row into a death at ~90% of budget;
    # clipping the reservation instead keeps width-legal rows completable
    # and only shortens the runway of over-rate rows, which fail cleanly at
    # reservation exhaustion either way.
    w_cap = (mrl + 1) // 2
    if w_cap > 12:
        w_prev = w = 12
        while w < w_cap:
            w_prev, w = w, min(2 * w, w_cap)
        per_tr = 2 * w_prev + 2 * w_cap + 19 + (8 if TRACK_PATH else 0)
        cand = max(1024, min(default_n, cap_n))
        table_gb = (1 << max(1, 2 * cand - 1).bit_length()) * 4 / 2 ** 30
        tr_gb = max(limit_gb - _TRANSIENT_MARGIN_GB - table_gb, 1.0)
        cap_n = min(cap_n, int(tr_gb * 2 ** 30 / per_tr))
    reserve = max(1024, min(default_n, cap_n))
    if reserve < default_n:
        log(f"  memory  : reservation clipped to {reserve:,} states "
            f"(engine default {default_n:,} does not fit {avail:.0f} GB free, "
            f"width-repack transient included); a row that outgrows it fails "
            f"with a clean MemoryError row, never an OOM kill")
    if states_per_node and w_cap > 12:
        # Under a rate floor the reservation IS the sizing model, so the
        # per-child RLIMIT doubles as the poisoning vaccine: on a box big
        # enough that a grow-doubling FITS in address space, a row past the
        # floor balloons to ~2x its reservation and completes -- and its
        # recorded peak then throttles admission for the whole campaign (a
        # ~260 GB peak would pin a 512 GB box to one lane, permanently,
        # via governor seeding). Cap the child just above its widest
        # legitimate allocation -- the width-repack transient -- and a row
        # that outgrows a rate-floored reservation dies the same clean,
        # recorded, retried MemoryError on every box size. The est-based
        # path (states_per_node=None) is deliberately ungated: THERE the
        # reservation is a guess and the grow is load-bearing (AC19's
        # 72.9 GB rows completed through it).
        table_gb = (1 << max(1, 2 * reserve - 1).bit_length()) * 4 / 2 ** 30
        repack_gb = reserve * per_tr / 2 ** 30 + table_gb
        limit_gb = min(limit_gb, repack_gb + _TRANSIENT_MARGIN_GB)
    return int(limit_gb * 2 ** 30), reserve


def _reserved_worst_gb(reserve_states, mrl):
    """What the reservation itself costs if every reserved state materializes
    at worst-case width -- the allocation-backed worst case. A governor whose
    worst case sits below its own allocation admits rows the box cannot hold."""
    if not reserve_states or not HAVE_HCOMPACT:
        return None
    from experiments.search.greedy_compact import row_width
    per = row_width(mrl) + 31 + (8 if TRACK_PATH else 0)
    return reserve_states * per / 2 ** 30


def _rss_gb(pid="self"):
    """Resident GB for a pid, or None. The arena is ``np.empty``: address space
    is reserved up front but physical pages commit only on first touch, so RSS
    -- not the reservation -- is what actually competes for the machine."""
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / (1024.0 * 1024.0)
    except (OSError, ValueError, IndexError):
        pass
    return None


def _peak_rss_gb():
    """This process's high-water RSS (VmHWM) in GB, or None."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return round(int(line.split()[1]) / (1024.0 * 1024.0), 3)
    except (OSError, ValueError, IndexError):
        pass
    return None


def _set_worker_name(name):
    """Row name into the kernel's comm field (prctl PR_SET_NAME, 15 bytes).

    A spawned child carries the parent's argv, so ps shows five identical
    pythons and a per-worker RSS reading can only be paired to its row by
    rank -- an assumption, not a measurement. With the comm set,
    ``ps -o pid,comm,rss`` (or ``/proc/<pid>/comm``) binds pid to row
    exactly. Best-effort and Linux-only; a worker that cannot be named
    still runs."""
    try:
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        libc.prctl(15, name.encode()[:15], 0, 0, 0)     # 15 = PR_SET_NAME
    except Exception:
        pass


def _child_run_row(q, arm, row, budget, mrl, heartbeat_secs, mem_limit_bytes,
                   reserve_states):
    """Runs in a spawned process. Everything that can go wrong is a message."""
    _set_worker_name(row["name"])     # named first, so even a crash is named
    try:
        if mem_limit_bytes:
            import resource
            resource.setrlimit(resource.RLIMIT_AS,
                               (int(mem_limit_bytes), int(mem_limit_bytes)))
    except (ImportError, ValueError, OSError):
        pass                                   # no rlimit support: guard degrades
    try:
        _, spec = resolve_arm(arm)
        hb = _in_search_heartbeat(row["name"], budget, heartbeat_secs,
                                  log=lambda m: q.put(("log", m)),
                                  init_total=len(row["r1"]) + len(row["r2"]))
        t = time.time()
        st = spec["run"](row["r1"], row["r2"], budget, mrl, progress=hb,
                         reserve_states=reserve_states, track_path=TRACK_PATH)
        q.put(("done", {
            "name": row["name"], "arm": arm, "r1": row["r1"], "r2": row["r2"],
            "budget": budget, "max_relator_length": mrl,
            "solved": bool(st["solved"]),
            "nodes_explored": int(st["nodes_explored"]),
            "path_length": st["path_length"],
            "min_relator_length": st["min_relator_length"],
            # the actual presentation at the best point, not just its length:
            # for an unsolved row, HOW FAR the pair got is the result
            "min_relator": st.get("min_relator"),
            "max_relator_length_expanded": st["max_relator_length_expanded"],
            "max_relator_expanded": st.get("max_relator_expanded"),
            "path": st.get("path", []),
            "path_moves": st.get("path_moves", []),
            "seconds": round(time.time() - t, 3),
            "peak_rss_gb": _peak_rss_gb(),
            "engine_mem_gen": ENGINE_MEM_GEN,
        }))
    except MemoryError as e:
        detail = f" [{e}]" if str(e) else ""
        q.put(("err", _EXHAUSTION_TEXT + detail))
    except BaseException as e:  # noqa: BLE001 -- repr crosses the queue safely
        q.put(("err", repr(e)))


class RamGovernor:
    """Admission control: may one MORE row start right now?

    ``resolve_workers`` answers once, at startup, from the worst-case reserve
    for a full-budget row. On a big box that is far too conservative twice
    over: most rows solve long before the budget and never approach the
    reserve, and the arena is ``np.empty`` -- address space up front, physical
    pages only on first touch. A fixed N sized off the worst case therefore
    leaves most of a 512 GB machine idle.

    This re-decides before every launch from free RAM as it is NOW, and from
    what finished rows actually peaked at. The trap it must avoid is the
    overcommit one: a row that just started has touched almost nothing, so free
    RAM looks enormous and a naive controller admits a crowd that then grows
    into each other. So the memory a live row has NOT yet claimed
    (``predict - its RSS``) is subtracted before deciding. Admission is
    therefore honest about the future, not just the present.
    """

    def __init__(self, budget, mrl, cpu_cap=None, max_workers=None,
                 headroom_gb=None, safety=1.25, min_samples=3, worst_gb=None):
        # sized for what this stage actually runs -- path capture included,
        # or the governor admits rows the machine cannot hold. worst_gb lets
        # the caller floor this with the ALLOCATION-backed worst (what the
        # actual reservation costs if every reserved state materializes) --
        # a rate-based reservation is bigger than the est curve, and a worst
        # case below one's own allocation admits rows the box cannot hold.
        self.worst = max(est_gb(budget, mrl, track_path=TRACK_PATH),
                         worst_gb or 0.0)
        self.cpus = cpu_cap or os.cpu_count() or 1
        self.max_workers = max_workers
        # never hand out the last of the machine: the parent, the numba runtime
        # and page cache all need room, and MemAvailable is an estimate
        self.headroom = headroom_gb if headroom_gb is not None else 4.0
        self.safety = safety
        self.min_samples = min_samples
        self.peaks = []

    def note(self, peak_gb):
        """Record what a finished row actually cost."""
        if peak_gb and peak_gb > 0:
            self.peaks.append(float(peak_gb))

    def predict_gb(self):
        """GB to assume for the NEXT row. The worst case until rows have
        spoken; after that their measured peak with safety margin, capped at
        the worst case -- UNLESS a row has already demonstrated more than the
        model's worst case, in which case the demonstration wins. The old
        unconditional cap silently discarded AC19's measured 72.9 GB grow
        transients in favour of the model's 45.1: a clamp that prefers the
        model over the measurement is a clamp installed backwards."""
        if len(self.peaks) < self.min_samples:
            return self.worst
        cap = max(self.worst, max(self.peaks))
        return max(0.25, min(max(self.peaks) * self.safety, cap))

    def capacity(self, live_rss_gb=(), free_gb=None):
        """How many more rows may start now, given the live rows' RSS."""
        free = _available_gb() if free_gb is None else float(free_gb)
        live = tuple(live_rss_gb)
        # Never predict below what a row in flight has ALREADY demonstrated.
        # Every row on these lists failed at 1M, so plenty will run the full
        # budget and peak near the reserve; without this, three cheap early
        # rows widen the gate just before the expensive ones arrive.
        per = max(self.predict_gb(), max(live) if live else 0.0)
        # what live rows have reserved but not yet touched -- they WILL claim it
        unclaimed = sum(max(0.0, per - r) for r in live)
        room = int((free - self.headroom - unclaimed) // per)
        ceiling = min(self.cpus, self.max_workers or self.cpus)
        allowed = max(0, min(ceiling - len(live), room))
        # one row always runs, even when the estimate says there is no space:
        # the estimate is linear and a real row is usually far cheaper. Stalling
        # forever on an estimate is worse than trying and recording an error.
        if not live:
            allowed = max(allowed, 1)
        return allowed


def _seed_governor(governor, path, log=print):
    """Re-teach the governor the peaks already paid for and sitting on disk.

    The learned peaks live in process memory, so every restart -- a planned
    upgrade or a Spot preemption -- re-zeroed the sample counter and sent the
    campaign back to worst-case admission for another ``min_samples`` rows.
    Finished rows already carry ``peak_rss_gb``; feeding the CURRENT
    generation's back in makes the widening survive restarts. Rows from an
    older memory profile (or before tagging existed) are skipped: their peaks
    describe an engine that is no longer running.
    """
    seeded = 0
    for r in read_rows(path):
        if (not r.get("error") and r.get("engine_mem_gen") == ENGINE_MEM_GEN
                and r.get("peak_rss_gb")):
            governor.note(r["peak_rss_gb"])
            seeded += 1
    if seeded:
        log(f"  governor: seeded {seeded} peak(s) from finished rows; "
            f"next-row prediction {governor.predict_gb():.1f} GB")
    return seeded


class _RowProc:
    """One row's isolated process, polled instead of waited on -- so the parent
    can hold several at once and still record an error for any that dies."""

    def __init__(self, arm, row, budget, mrl, heartbeat_secs, mem_limit_bytes,
                 reserve_states, timeout_secs, log):
        self.arm, self.row, self.budget, self.mrl = arm, row, budget, mrl
        self.timeout_secs, self.log = timeout_secs, log
        ctx = mp.get_context("spawn")
        self.q = ctx.Queue()
        self.proc = ctx.Process(
            target=_child_run_row,
            args=(self.q, arm, row, budget, mrl, heartbeat_secs,
                  mem_limit_bytes, reserve_states))
        self.reserve_states = reserve_states
        self.t0 = time.time()
        self.proc.start()
        self.rec = self.err = None

    def rss_gb(self):
        return _rss_gb(self.proc.pid) or 0.0

    def poll(self, timeout=0.1):
        """Drain messages; return the record once this row is settled."""
        while self.rec is None and self.err is None:
            try:
                kind, payload = self.q.get(timeout=timeout)
            except _queue.Empty:
                if not self.proc.is_alive():
                    self.err = (f"worker died (exit={self.proc.exitcode}) -- an "
                                f"external kill (OOM/CPU limit); the row is "
                                f"retried next run")
                elif self.timeout_secs and time.time() > self.t0 + self.timeout_secs:
                    self.proc.terminate()
                    self.err = (f"row timeout after {self.timeout_secs:,.0f}s -- "
                                f"terminated; the row is retried next run")
                break
            if kind == "log":
                self.log(payload)
            elif kind == "done":
                self.rec = payload
            else:
                self.err = payload
        if self.rec is None and self.err is None:
            return None
        return self._settle()

    def _settle(self):
        self.proc.join(timeout=10)
        if self.proc.is_alive():
            self.proc.kill()
            self.proc.join(timeout=5)
        self.q.close()
        if self.rec is None:
            self.rec = _error_record(self.row, self.arm, self.budget, self.mrl,
                                     self.err, time.time() - self.t0,
                                     self.reserve_states)
            self.log(f"    !! {self.row['name']}: {self.err}")
        return self.rec


def run_rows_dynamic(arm, todo, budget, mrl, heartbeat_secs, mem_limit_bytes,
                     reserve_states, timeout_secs, governor, log=print):
    """Yield records as rows finish, holding as many in flight as RAM allows.

    This replaces both of the old paths. The fixed-size pool had no per-row
    isolation -- on a 14-worker box a single OOM took every row with it -- and
    the isolated path ran strictly one at a time. Here every row is isolated
    AND the width floats with the machine.
    """
    pending, live = list(todo), []
    while pending or live:
        n = governor.capacity([p.rss_gb() for p in live])
        while n > 0 and pending:
            r = pending.pop(0)
            live.append(_RowProc(arm, r, budget, mrl, heartbeat_secs,
                                 mem_limit_bytes, reserve_states,
                                 timeout_secs, log))
            n -= 1
        settled = []
        for p in live:
            rec = p.poll(timeout=0.1 if len(live) > 1 else 0.5)
            if rec is not None:
                settled.append((p, rec))
        for p, rec in settled:
            live.remove(p)
            governor.note(rec.get("peak_rss_gb"))
            yield rec
        if not settled and not (pending and governor.capacity(
                [p.rss_gb() for p in live])):
            time.sleep(0.05)      # nothing settled and no room: do not spin


def _run_row_isolated(arm, row, budget, mrl, heartbeat_secs, mem_limit_bytes,
                      reserve_states, timeout_secs, log):
    """One row, one process. Whatever kills the child, the run continues."""
    p = _RowProc(arm, row, budget, mrl, heartbeat_secs, mem_limit_bytes,
                 reserve_states, timeout_secs, log)
    while True:
        rec = p.poll(timeout=0.5)
        if rec is not None:
            return rec


def absorb_shard_rows(out, shard_paths, valid_names, log=print):
    """Fold finished rows from earlier per-chunk jsonl into the combined jsonl.

    The 5M stage first shipped as four greedy stride-shard notebooks; the
    combined single-CPU notebook replaces them, and any rows those shards
    already paid for must not be re-run. A shard jsonl only ever contains
    finished rows, so every one whose name is in ``valid_names`` and not yet in
    ``out`` is appended verbatim. Names outside ``valid_names`` (another arm, a
    smoke row) are skipped, and duplicates across shards collapse to the first
    seen. Returns how many rows were absorbed.
    """
    have = _done(out)
    added = 0
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    _ensure_trailing_newline(out)
    with open(out, "a") as fh:
        for p in shard_paths:
            for r in read_rows(p):
                n = r.get("name")
                if r.get("error"):
                    continue                     # a failed row is not paid-for work
                if n in valid_names and n not in have:
                    fh.write(json.dumps(r) + "\n")
                    have.add(n)
                    added += 1
    if added:
        log(f"  absorbed {added} finished row(s) from "
            f"{len(shard_paths)} earlier shard file(s)")
    return added


def run_arm_5m(arm, out_dir, chunks=None, chunk_index=1, budget=NODE_BUDGET_5M,
               mrl=MRL_5M, n_workers="auto", resume=True, campaign="ac19",
               csv_path=None, mirror_dir=None, limit=None, heartbeat_secs=60,
               row_timeout_secs=ROW_TIMEOUT_DEFAULT, mem_limit_bytes=None,
               reserve_states=None, log=print):
    """Run one arm's chunk to a chunk-tagged jsonl; append + whole-file mirror.

    With one worker (which is what this budget resolves on any ordinary
    machine) every row runs crash-isolated in its own process -- see the Edge
    Compact guards above. ``mem_limit_bytes``/``reserve_states`` default to
    ``plan_memory()`` for this machine; pass them only to test the guards.
    With more than one worker the pool path is used (no per-row isolation).
    """
    key, spec1m = resolve_arm(arm)
    ckey, camp = resolve_campaign(campaign)
    cspec = campaign_spec(ckey, key)
    if chunks is None:
        chunks = cspec["chunks"]
    rows, used = load_rows_5m(key, csv_path=csv_path, campaign=ckey)
    rows = stride_chunk(rows, chunks, chunk_index)
    if limit:
        rows = rows[:int(limit)]

    os.makedirs(out_dir, exist_ok=True)
    out = out_path_5m(key, out_dir, chunks, chunk_index, budget, mrl,
                      campaign=ckey)
    if resume:
        _seed_from_mirror(out, mirror_dir, log)
    seen = _done_ok(out) if resume else set()
    if resume and not seen and not os.environ.get("RESUME_FRESH_OK"):
        sib = _sibling_results(out, camp["prefix"], key)
        if sib:
            raise SystemExit(
                "CRITICAL: the expected output file has no finished rows, but "
                "this campaign+arm already has results under a DIFFERENT "
                "name:\n" + "".join(f"    {p}\n" for p in sib)
                + f"    expected: {out}\n"
                "A drifted name component (budget/mrl/chunk tag) would "
                "silently re-run every finished row of a multi-day campaign. "
                "If a fresh pass at these settings is REALLY wanted, set "
                "RESUME_FRESH_OK=1 (or pass resume=False).")
    auto = n_workers in (None, "auto")
    n_workers, per_gb = resolve_workers(key, n_workers, budget=budget, mrl=mrl,
                                        track_path=TRACK_PATH)
    if mem_limit_bytes is None and reserve_states is None:
        mem_limit_bytes, reserve_states = plan_memory(
            budget, mrl, states_per_node=_floor_for(camp, log), log=log)
    # a row that died at reservation exhaustion under this sizing would die
    # again at the same pop; it waits for a bigger reservation or box
    deferred = _deferred_exhausted(out, reserve_states, budget) if resume else {}
    todo = [r for r in rows if r["name"] not in seen and r["name"] not in deferred]
    # "auto" lets the governor float up to the core count; an explicit number
    # is a ceiling, never a target -- RAM still has the last word.
    governor = RamGovernor(budget, mrl,
                           max_workers=None if auto else n_workers,
                           worst_gb=_reserved_worst_gb(reserve_states, mrl))
    log(f"  campaign: {camp['label']}")
    log(f"  arm     : {key} -- {spec1m['label']}")
    log(f"  rows    : {len(rows)} (chunk {chunk_index} of {chunks}, "
        f"stride split of {cspec['n_rows']}) from {used}")
    log(f"  budget  : {budget:,} nodes, cap {mrl}")
    # the number the governor ADMITS against is the allocation-backed worst;
    # the est curve is printed for scale only -- quoting it as the worst case
    # misread a 246 GB box as a 2-lane box twice in one day
    log(f"  workers : dynamic ({'auto' if auto else f'cap {n_workers}'}, "
        f"{governor.cpus} cores); the governor admits against "
        f"{governor.worst:.1f} GB/row (allocation-backed worst) -- the est "
        f"curve's {per_gb:.1f} GB is NOT the admission figure")
    log(f"  resume  : {len(seen)} row(s) already on disk, {len(todo)} to run")
    if deferred:
        names = ", ".join(f"{n} ({why})" for n, why in sorted(deferred.items())[:8])
        log(f"  deferred: {len(deferred)} row(s) died at reservation exhaustion "
            f"under this sizing and would die again (deterministic): {names}"
            f"{' ...' if len(deferred) > 8 else ''} -- raise STATES_PER_NODE or "
            f"use a bigger box; RETRY_EXHAUSTED=1 forces the retry")
    if resume:
        _seed_governor(governor, out, log)
    log(f"  -> {out}")

    t0 = time.time()
    last = t0
    done = 0
    if todo:
        _ensure_trailing_newline(out)
        with open(out, "a") as fh:
            # Every row is crash-isolated AND the width floats with the
            # machine: the old fixed pool had no per-row isolation, so on a
            # wide box one OOM took every row in flight with it.
            for rec in run_rows_dynamic(key, todo, budget, mrl, heartbeat_secs,
                                        mem_limit_bytes, reserve_states,
                                        row_timeout_secs, governor, log):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                done += 1
                last = _beat(rec, done, len(todo), t0, last,
                             heartbeat_secs, out, mirror_dir, log)
    _mirror(out, mirror_dir)
    log(f"  {done} row(s) run in {time.time() - t0:,.0f}s; jsonl at {out}")
    return out


def report_5m(arm, out_dir, chunks=None, chunk_index=None, budget=NODE_BUDGET_5M,
              mrl=MRL_5M, write_ids=True, campaign="ac19", log=print):
    """Report one chunk, or — with ``chunk_index=None`` — every chunk merged.

    The merged view is what the experiment answers; a single chunk's numbers are
    progress, not a result, and are labelled as such.
    """
    key, spec1m = resolve_arm(arm)
    ckey, camp = resolve_campaign(campaign)
    cspec = campaign_spec(ckey, key)
    if chunks is None:
        chunks = cspec["chunks"]
    idxs = [chunk_index] if chunk_index is not None else range(1, int(chunks) + 1)
    rows, missing = [], []
    for i in idxs:
        p = out_path_5m(key, out_dir, chunks, i, budget, mrl, campaign=ckey)
        got = read_rows(p)
        rows.extend(got)
        if not got:
            missing.append(i)
    if not rows:
        log(f"no rows yet for {key} in {out_dir}")
        return None
    c = classify_5m(rows, budget=budget, checkpoints=camp["checkpoints"],
                    floor=camp["floor"] or 0)
    expected = (cspec["n_rows"] if chunk_index is None
                else len(stride_chunk(load_rows_5m(key, campaign=ckey)[0],
                                      chunks, chunk_index)))
    scope = ("all chunks merged" if chunk_index is None
             else f"chunk {chunk_index} of {chunks} ONLY -- progress, not a result")

    log("")
    log(f"=== {key} @ {budget/1e6:g}M -- {spec1m['label']}  [{scope}]")
    log(f"    rows complete        : {len(rows)}/{expected}"
        + ("" if len(rows) == expected else
           "   (PARTIAL -- these numbers are not final)")
        + (f"   [chunks with no rows yet: {missing}]" if missing and
           chunk_index is None else ""))
    n_solved = len(c["solved_at_5m"])
    pct = f"   ({100.0 * n_solved / len(rows):.1f}%)" if rows else ""
    log(f"    solved at {budget:>9,}  : {n_solved}{pct}")
    log(f"    still unsolved       : {len(c['unsolved_at_5m'])}")
    if c["errored"]:
        log(f"    errored (crash-guarded, retried on the next run): "
            f"{len(c['errored'])}  {sorted(c['errored'])[:5]}")
    log("    anytime (free -- one search answers every budget below it):")
    for cp in sorted(c["anytime"]):
        log(f"      <= {cp:>9,} : {c['anytime'][cp]}")
    if c["solved_at_or_below_1m"] and camp["floor"]:
        if mrl == camp["floor_mrl"]:
            # same cap as the 1M run, so the prefix property applies exactly
            log(f"    !! {len(c['solved_at_or_below_1m'])} row(s) solved at or "
                f"below 1,000,000 nodes, which the 1M run says is impossible: "
                f"{c['solved_at_or_below_1m'][:5]}")
            log("       -> the search being run is not the one that built this "
                "list; stop and check the arm, the cap and the row list before "
                "reading anything above.")
        else:
            # a different cap is a different search space: the 1M floor was
            # established at cap 48, so an early solve here is legitimate --
            # and it is the interesting outcome, not an error
            log(f"    note: {len(c['solved_at_or_below_1m'])} row(s) solved at "
                f"or below 1,000,000 nodes. Legitimate at cap {mrl} (the 1M "
                f"floor holds only at cap {MAX_RELATOR_LENGTH}); these are "
                f"rows the wider corridor cracked cheaply.")

    if write_ids and chunk_index is None and len(rows) == expected:
        tag = camp["ids_stem"]
        for stem, ids in ((f"solved_at_{tag}", c["solved_at_5m"]),
                          (f"still_unsolved_{tag}", c["unsolved_at_5m"])):
            p = os.path.join(out_dir, f"{stem}_{key}.txt")
            with open(p, "w") as f:
                f.write("".join(n + "\n" for n in sorted(ids)))
            log(f"    {stem} ids -> {p}")
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", required=True, choices=sorted(SPEC_5M))
    ap.add_argument("--campaign", default="ac19", choices=sorted(CAMPAIGNS),
                    help="row list + its budget/cap defaults")
    ap.add_argument("--out-dir", default=os.path.join(
        os.path.dirname(SCREEN_DIR), "leftovers_5m"))
    ap.add_argument("--chunks", type=int, default=None)
    ap.add_argument("--chunk-index", type=int, default=1)
    ap.add_argument("--budget", type=int, default=None)
    # One flag feeds BOTH the run and the report. The cap is in the jsonl
    # filename, so a run at one cap and a report at another silently read a
    # file that does not exist ("no rows yet" on a finished run) -- that bug
    # has bitten this campaign twice. Passing one value to both closes it.
    ap.add_argument("--mrl", type=int, default=None,
                    help="max relator length (per relator); tags the jsonl name")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--smoke", action="store_true",
                    help="2 rows at a 2,000-node budget -- proves the pipeline, "
                         "measures nothing")
    a = ap.parse_args(argv)
    ckey, camp = resolve_campaign(a.campaign)
    # a campaign carries its own budget/cap; an explicit flag still wins
    budget = a.budget if a.budget is not None else camp["budget"]
    mrl = a.mrl if a.mrl is not None else camp["mrl"]
    limit, out_dir = a.limit, a.out_dir
    if a.smoke:
        budget, limit = 2_000, 2
        out_dir = out_dir + "_smoke"
    run_arm_5m(a.arm, out_dir, chunks=a.chunks, chunk_index=a.chunk_index,
               budget=budget, mrl=mrl, n_workers=a.workers, limit=limit,
               campaign=ckey)
    report_5m(a.arm, out_dir, chunks=a.chunks, chunk_index=a.chunk_index,
              budget=budget, mrl=mrl, campaign=ckey)


if __name__ == "__main__":
    main()
