"""Chunked, provenance-complete mu-descent beam ladder (nb2, scaled up).

Per-class semantics are IDENTICAL to ``mu_ladder.climb_one`` — same candidate
generation (``hop_outputs`` over the gated subword-CoV family), same
``(mu, pair)`` sort, same top-K beam with uphill intermediates, same per-class
orbit dedup — pinned by a direct regression test
(``tests/stable_ac/test_mu_ladder_big.py::test_climb_matches_mu_ladder``).
On top of that, three things the original lacks for a long Colab run:

1. **Full provenance.** Every accepted orbit becomes one row in a per-chunk
   ``*_orbits.jsonl``: parent's CONCRETE pair, the z-word, the isolating
   branch ``(iso_gen, iso_index)``, ``n_subs``, the concrete output pair, and
   its ``aut_canon`` ``(mu, rep)``. Chains are representative-sensitive
   (lesson: cov-chains-junction-at-canonical-reps), so replay always starts
   from the recorded parent pair, never from a canonical rep. Any state's
   z-chain = walk parent pointers to the root. Verifier:
   ``experiments/stable_ac/cov/verify_mu_ladder.py``.

2. **Wall-clock + orbit budgets.** ``time_per_class_s`` bounds each class
   (checked between beam expansions and every 32 scored outputs inside a
   hop); ``max_orbits`` caps the per-class ``seen`` set. Both stop the climb
   gracefully and flag the row (``timed_out`` / ``orbit_capped``) — a row is
   always written, so resume never re-runs a finished class.

3. **Chunked parallelism** (run_cov.py pattern): stride partition
   (row j -> chunk (j % N) + 1), per-chunk resume identity ``_c{i}of{N}``,
   spawned chunk processes, flock claim on each chunk file (a live holder is
   a superseded run's orphan — killed), parent-side heartbeat, checked merge.

``stop_mu`` defaults to 12, NOT 13: a threshold on the input scale silently
skips whatever already satisfies it (lesson:
stop-threshold-at-the-boundary-skips-the-boundary-case) — mu=13 starters like
aca_115 must climb, not stop at rung 0. TRIPWIRE: a mu <= 12 hit on aca_115
(= AK(3)'s class) is presumed a BUG until independently reproduced.

Result-neutral speedups only: a per-class pair -> (mu, rep) memo avoids
re-scoring pairs ``aut_canon`` already saw (identical output, pinned by
``test_hop_outputs_full_matches_hop_outputs``). There is no greedy search
anywhere in this pipeline — zero search nodes — so the HIGH_SPEEDUP solver
knob does not apply.

CLI (local smoke runs only — production runs on Colab via
``mu_ladder_big.ipynb``):
    .venv/bin/python3 -m experiments.stable_ac.cov.mu_ladder_big \
        --rungs 2 --beam 4 --time-per-class 30 --chunks 2 --names aca_0 aca_1
"""

import fcntl
import glob
import json
import os
import re
import signal
import subprocess
import time

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.mu_descent_scan import find_repo_root

try:
    # result-identical numba twin of aut_canon (pinned by
    # tests/stable_ac/test_autcanon_fast.py); the verifier deliberately stays
    # on slow aut_canon, so every production row is a fast-vs-slow cross-check
    from experiments.stable_ac.cov.autcanon_fast import (
        aut_min as _aut_min,
        relabel_min as _relabel_min,
        warm as _warm_canon,
    )
    _FAST_AVAILABLE = True
except Exception:          # numba unavailable: same rows, just slower
    _FAST_AVAILABLE = False

# The live switch _orbit_memo reads. The HIGH_SPEEDUP knob (config key
# ``high_speedup``, default True) sets it per run via _apply_high_speedup —
# result-neutral like the greedy solver's HIGH_SPEEDUP, so it must never
# enter the filename identity.
FAST_CANON = _FAST_AVAILABLE


def _apply_high_speedup(c):
    global FAST_CANON
    FAST_CANON = _FAST_AVAILABLE and bool(c.get("high_speedup", True))

HERE = os.path.dirname(os.path.abspath(__file__))

AK3 = ("xxxYYYY", "xyxYXY")

_CHUNK_MARK = re.compile(r"_c\d+of\d+")
_HB_PERIOD = 60.0
_DETAIL_EVERY = 300.0
_SIDE_EVERY = 5.0

DEFAULTS = dict(
    data="data/ms_unsolved_reps/aca_124.csv",
    rungs=256,
    beam=64,
    cap=24,               # forwarded default_cap; the admissibility ceiling is cov.REJECT_LEN
    stop_mu=12,
    time_per_class_s=14400,   # 4h RUNAWAY BACKSTOP only — rungs/max_orbits are
                              # the budgets (deterministic, machine-independent)
    max_orbits=150_000,
    chunks=5,
    chunk_index=None,     # None = all chunks as parallel processes here
    out_dir="results/stable_ac/mu_scan",
    names=None,
    high_speedup=True,    # numba canon (autcanon_fast). False = force the
                          # pure-Python aut_canon path: identical rows, ~15x
                          # slower. Result-neutral => NOT in _run_prefix.
)


class _Deadline(Exception):
    pass


# --------------------------------------------------------------------------
# identity / io helpers (self-contained: a chunk worker must not drag in the
# numba solver stack just to append jsonl rows)

def _git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              timeout=10).stdout.strip() or None
    except Exception:
        return None


def _run_prefix(c, n_rows):
    """Every knob that changes a row's content is in the name; nothing else is
    (lesson: jsonl-filename-encodes-search-identity). ``cap`` stays out: it is
    forwarded as ``default_cap`` but nothing in the ladder path reads the
    resulting ``CoVResult.cap``, so it is result-inert here."""
    tag = os.path.splitext(os.path.basename(c["data"]))[0]
    tag = "aca124" if tag == "aca_124" else tag
    return (f"mu_ladder_big_{tag}_n{n_rows}_r{c['rungs']}_b{c['beam']}"
            f"_s{c['stop_mu']}_t{int(c['time_per_class_s'])}"
            f"_o{c['max_orbits']}")


def _chunk_paths(c, n_rows, root, chunk_index):
    base = os.path.join(root, c["out_dir"],
                        _run_prefix(c, n_rows) + f"_c{chunk_index}of{c['chunks']}")
    return base + ".jsonl", base + "_orbits.jsonl"


def _merged_paths(c, n_rows, root):
    base = os.path.join(root, c["out_dir"], _run_prefix(c, n_rows))
    return base + ".jsonl", base + "_orbits.jsonl"


def _repair_jsonl(path):
    """Drop a torn trailing line (kill mid-append). Rows are single writes of
    ``json.dumps(row) + "\\n"``, so only the tail can ever be damaged."""
    if not os.path.exists(path):
        return
    with open(path, "rb") as f:
        data = f.read()
    if not data or data.endswith(b"\n"):
        return
    with open(path, "r+b") as f:
        f.truncate(data.rfind(b"\n") + 1)


def _read_done(path):
    """pres_ids committed to a repaired summary jsonl. Strict: after
    ``_repair_jsonl`` any unparseable line is real corruption, so raise."""
    done = set()
    if not os.path.exists(path):
        return done
    for ln in open(path):
        ln = ln.strip()
        if ln:
            done.add(json.loads(ln)["pres_id"])
    return done


def _repair_orbits(orbits_path, done_ids):
    """Orbit rows are appended BEFORE the class's summary row commits, so a
    crash mid-class leaves orphan orbit rows for an uncommitted class — which
    would duplicate when the class re-runs. Drop them at claim time (single
    writer under flock; atomic replace)."""
    if not os.path.exists(orbits_path):
        return
    _repair_jsonl(orbits_path)
    keep, changed = [], False
    for ln in open(orbits_path):
        if not ln.strip():
            changed = True
            continue
        if json.loads(ln)["pres_id"] in done_ids:
            keep.append(ln)
        else:
            changed = True
    if changed:
        tmp = orbits_path + ".tmp"
        with open(tmp, "w") as f:
            f.writelines(keep)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, orbits_path)


_HELD_LOCKS = []


def _claim_out_path(out_path):
    """Exclusive-writer claim, held until this process dies (run_cov.py
    pattern; lesson: orphaned-workers-double-compute). A live holder is by
    construction a superseded run's worker — kill it and take the file."""
    lock_fd = os.open(out_path + ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    for _ in range(40):
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.lseek(lock_fd, 0, os.SEEK_SET)
            try:
                pid = int(os.read(lock_fd, 32) or b"0")
            except ValueError:
                pid = 0
            if pid == os.getpid():
                os.close(lock_fd)
                return
            if pid:
                try:
                    os.kill(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
            time.sleep(0.25)
            continue
        os.ftruncate(lock_fd, 0)
        os.lseek(lock_fd, 0, os.SEEK_SET)
        os.write(lock_fd, str(os.getpid()).encode())
        _HELD_LOCKS.append(lock_fd)
        return
    raise RuntimeError(f"could not claim {os.path.basename(out_path)}: a "
                       f"previous run's worker survived SIGKILL — restart "
                       f"the runtime")


def _chunk_rows(rows, chunks, chunk_index):
    """Stride, not blocks: the class CSVs are ordered, so a block split would
    hand one chunk a correlated (all-hard) slice and finish last by hours."""
    return [r for j, r in enumerate(rows) if j % chunks == chunk_index - 1]


def _load_rows(c, root):
    import csv
    rows = list(csv.DictReader(open(os.path.join(root, c["data"]))))
    if c.get("names"):
        keep = set(c["names"])
        rows = [r for r in rows if r["name"] in keep]
    return rows


# --------------------------------------------------------------------------
# the climb

def _orbit_memo(pair, memo):
    """(mu, rep) of the pair's orbit. On the fast path the memo key is the
    8-signed-perm relabel canonical — coarser than the raw pair but still
    exact (equal keys => same Aut-orbit => same result), so the cache also
    hits across relabeled duplicates. Result-identical either way: aut_min
    == aut_canon[:2] is test-pinned, and aut_canon's rep is an orbit
    invariant."""
    if memo is None:
        if FAST_CANON:
            return _aut_min(pair)
        t, rep, _ = aut_canon(pair)
        return t, rep
    key = _relabel_min(pair) if FAST_CANON else pair
    hit = memo.get(key)
    if hit is None:
        if FAST_CANON:
            hit = memo[key] = _aut_min(pair)
        else:
            t, rep, _ = aut_canon(pair)
            hit = memo[key] = (t, rep)
    return hit


def hop_outputs_full(r1s, r2s, cap, memo=None, deadline=None):
    """``mu_descent_scan.hop_outputs`` with full branch provenance kept:
    {orbit_rep: (mu, out_pair, z, iso_gen, iso_index, n_subs)}. Identical
    selection (first CoV result per new orbit, input orbit excluded, same
    enumeration order) — its projection to (mu, out_pair, z) IS hop_outputs'
    return value, and a test pins that. A partial result is never returned:
    on deadline it raises, and the caller discards the whole hop."""
    res = cov.enumerate_cov(str_to_word(r1s), str_to_word(r2s),
                            default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
                            reject_len=cov.REJECT_LEN)
    _, rep_in = _orbit_memo((r1s, r2s), memo)
    out = {}
    for k, c in enumerate(res):
        if deadline is not None and (k & 31) == 0 \
                and time.monotonic() > deadline:
            raise _Deadline
        o1, o2 = word_to_str(c.r1), word_to_str(c.r2)
        mu, rep = _orbit_memo((o1, o2), memo)
        if rep == rep_in or rep in out:
            continue
        out[rep] = (mu, (o1, o2), word_to_str(c.z_word),
                    c.iso_gen, c.iso_index, c.n_subs)
    return out


def climb_one_big(task, progress=None):
    """One class's ladder. Returns (summary_row, orbit_rows). With
    ``time_per_class_s=0`` and ``max_orbits=0`` (both unlimited) the summary
    fields shared with ``mu_ladder.climb_one`` are bit-identical to its
    output — the regression test relies on exactly that."""
    pres_id, r1, r2 = task["pres_id"], task["r1"], task["r2"]
    rungs, beam_k, cap = task["rungs"], task["beam"], task["cap"]
    stop_mu = task["stop_mu"]
    time_s, max_orbits = task["time_per_class_s"], task["max_orbits"]
    t0 = time.monotonic()
    deadline = t0 + time_s if time_s else None

    memo = {}
    mu_in, rep_in = _orbit_memo((r1, r2), memo)
    seen = {rep_in}
    orbit_rows = [{"pres_id": pres_id, "rung": 0, "mu": mu_in,
                   "rep": list(rep_in), "pair": [r1, r2], "parent_rep": None,
                   "z": None, "iso_gen": None, "iso_index": None,
                   "n_subs": None}]
    beam = [(mu_in, (r1, r2), [], rep_in)]
    best_mu, best_chain, best_rep = mu_in, [], rep_in
    rung_log = []
    timed_out = orbit_capped = False

    for rung in range(1, rungs + 1):
        cand = []
        partial = False
        for mu_b, pair, chain, rep_b in beam:
            if deadline is not None and time.monotonic() > deadline:
                timed_out = partial = True
                break
            if max_orbits and len(seen) >= max_orbits:
                orbit_capped = partial = True
                break
            try:
                hops = hop_outputs_full(*pair, cap, memo=memo,
                                        deadline=deadline)
            except _Deadline:
                timed_out = partial = True
                break
            for rep, (mu, out_pair, z, iso_gen, iso_index, n_subs) \
                    in hops.items():
                if rep in seen:
                    continue
                seen.add(rep)
                cand.append((mu, out_pair, chain + [z], rep))
                orbit_rows.append({"pres_id": pres_id, "rung": rung,
                                   "mu": mu, "rep": list(rep),
                                   "pair": list(out_pair),
                                   "parent_rep": list(rep_b), "z": z,
                                   "iso_gen": iso_gen,
                                   "iso_index": iso_index,
                                   "n_subs": n_subs})
            if progress is not None:
                progress(rung, len(seen), best_mu)
        if not cand:
            rung_log.append({"rung": rung, "new_orbits": 0, "best": best_mu,
                             **({"partial": True} if partial else {})})
            break
        cand.sort(key=lambda t: (t[0], t[1]))
        for mu, out_pair, chain, rep in cand:
            if mu < best_mu:
                best_mu, best_chain, best_rep = mu, chain, rep
        beam = [(mu, p, c, rep) for mu, p, c, rep in cand[:beam_k]]
        rung_log.append({"rung": rung, "new_orbits": len(cand),
                         "best": best_mu,
                         **({"partial": True} if partial else {})})
        if best_mu <= stop_mu or partial:
            break

    _, ak3_rep = _orbit_memo(AK3, memo)
    row = {"pres_id": pres_id, "r1_orig": r1, "r2_orig": r2,
           "mu_in": mu_in, "best_mu": best_mu,
           "best_chain": best_chain, "best_rep": best_rep,
           "hits_stop": best_mu <= stop_mu,
           "is_ak3_orbit": best_rep == ak3_rep,
           "n_orbits_seen": len(seen), "rungs": rung_log,
           "timed_out": timed_out, "orbit_capped": orbit_capped,
           "elapsed_s": round(time.monotonic() - t0, 1),
           "cfg": {"rungs": rungs, "beam": beam_k, "cap": cap,
                   "stop_mu": stop_mu, "time_per_class_s": time_s,
                   "max_orbits": max_orbits}}
    return row, orbit_rows


def _lead_tag(row):
    if row["hits_stop"]:
        bug = (" [aca_115 = AK(3)-class: PRESUMED BUG until reproduced]"
               if row["pres_id"] == "aca_115" or row.get("is_ak3_orbit")
               else "")
        return (f" *** LEAD mu<={row['best_mu']} — verification bar applies "
                f"(MU_CRITERION.md){bug}")
    if row["best_mu"] < row["mu_in"]:
        return f" *** DESC {row['mu_in']}->{row['best_mu']}"
    return ""


# --------------------------------------------------------------------------
# chunk worker

class _Sidecar:
    """Intra-class progress for the parent's heartbeat: a spawned child's
    print() never reaches a Colab cell (lesson: heartbeat-worker-cannot-
    print), so the worker overwrites one tiny json (atomic replace) that the
    parent polls."""

    def __init__(self, path, n_done, n_total):
        self.path, self.n_done, self.n_total = path, n_done, n_total
        self.pres_id = self.mu_in = None
        self.last = 0.0

    def start_class(self, pres_id, mu_in):
        self.pres_id, self.mu_in = pres_id, mu_in
        self.write(0, 1, mu_in, force=True)

    def __call__(self, rung, n_orbits, best_mu):
        self.write(rung, n_orbits, best_mu)

    def write(self, rung, n_orbits, best_mu, force=False):
        now = time.monotonic()
        if not force and now - self.last < _SIDE_EVERY:
            return
        self.last = now
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump({"pres_id": self.pres_id, "mu_in": self.mu_in,
                           "rung": rung, "n_orbits": n_orbits,
                           "best_mu": best_mu, "done": self.n_done,
                           "total": self.n_total, "ts": time.time()}, f)
            os.replace(tmp, self.path)
        except OSError:
            pass


def run_chunk(c, chunk_index):
    """One chunk's classes, serially, into its own pair of jsonls. Claims
    both files, repairs a torn tail, drops orphan orbit rows of uncommitted
    classes, then runs every class not already in the summary. Per class:
    orbit rows land first, the summary row second — a summary row present
    means its provenance block is complete."""
    _apply_high_speedup(c)
    root = find_repo_root(HERE)
    rows_all = _load_rows(c, root)
    rows = _chunk_rows(rows_all, c["chunks"], chunk_index) \
        if c.get("use_chunks") else rows_all
    out_path, orbits_path = (
        _chunk_paths(c, len(rows_all), root, chunk_index)
        if c.get("use_chunks") else _merged_paths(c, len(rows_all), root))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    _claim_out_path(out_path)
    _repair_jsonl(out_path)
    done = _read_done(out_path)
    _repair_orbits(orbits_path, done)
    todo = [r for r in rows if r["name"] not in done]
    print(f"[c{chunk_index}of{c['chunks']}] {len(todo)} classes to climb "
          f"({len(done)} resumed) -> {os.path.basename(out_path)}", flush=True)
    if FAST_CANON and todo:
        t_w = time.monotonic()
        _warm_canon()
        print(f"[c{chunk_index}of{c['chunks']}] HIGH_SPEEDUP on: numba canon "
              f"warm in {time.monotonic() - t_w:.1f}s", flush=True)
    elif todo:
        why = ("knob off" if _FAST_AVAILABLE else "numba unavailable")
        print(f"[c{chunk_index}of{c['chunks']}] HIGH_SPEEDUP off ({why}): "
              f"pure-Python aut_canon — identical rows, ~15x slower",
              flush=True)
    commit = _git_commit()
    side = _Sidecar(out_path + ".hb", len(done), len(rows))
    with open(out_path, "a") as out_f, open(orbits_path, "a") as orb_f:
        for r in todo:
            task = {"pres_id": r["name"], "r1": r["r1"], "r2": r["r2"],
                    "rungs": c["rungs"], "beam": c["beam"], "cap": c["cap"],
                    "stop_mu": c["stop_mu"],
                    "time_per_class_s": c["time_per_class_s"],
                    "max_orbits": c["max_orbits"]}
            # mu_in up front (sub-ms on the fast path) so every heartbeat can
            # show best vs the starting Aut-floor, not just a bare number
            side.start_class(r["name"], _orbit_memo((r["r1"], r["r2"]),
                                                    None)[0])
            row, orbit_rows = climb_one_big(task, progress=side)
            row["git_commit"] = commit
            orb_f.write("".join(json.dumps(o) + "\n" for o in orbit_rows))
            orb_f.flush()
            os.fsync(orb_f.fileno())
            out_f.write(json.dumps(row) + "\n")
            out_f.flush()
            os.fsync(out_f.fileno())
            side.n_done += 1
            side.write(0, row["n_orbits_seen"], row["best_mu"], force=True)
            print(f"  [c{chunk_index}] {row['pres_id']} best {row['best_mu']} "
                  f"(in {row['mu_in']}, {row['n_orbits_seen']} orbits, "
                  f"{row['elapsed_s']}s"
                  f"{', timed_out' if row['timed_out'] else ''}"
                  f"{', orbit_capped' if row['orbit_capped'] else ''})"
                  f"{_lead_tag(row)}", flush=True)
    return out_path, orbits_path


def _spawn_entry(c):
    """Module-level so multiprocessing spawn can import it in the child."""
    run_chunk(c, c["chunk_index"])


# --------------------------------------------------------------------------
# parent orchestration + heartbeat

def _scan_summary(paths):
    """Deduped rows across chunk summaries other processes are appending to
    right now — torn tails skipped, never repaired (only the owner truncates),
    and dedup by pres_id so a superseded worker can't inflate done."""
    rows = {}
    for path in paths:
        try:
            with open(path) as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        row = json.loads(ln)
                    except ValueError:
                        continue
                    rows.setdefault(row["pres_id"], row)
        except OSError:
            continue
    return rows


class _LadderHeartbeat:
    """Time-based, printed by the parent only: a 60s beat with each chunk's
    live class (from the sidecars) + a ~5min cumulative done/descents/ETA
    line, plus loud one-off lines for every DESC / LEAD row as it commits."""

    def __init__(self, sum_paths, total, now=None):
        self.sum_paths = list(sum_paths)
        self.total = total
        self.t0 = self.last = self.last_detail = \
            time.monotonic() if now is None else now
        self.announced = set(_scan_summary(self.sum_paths))
        self.done0 = len(self.announced)
        self.prev_hb = {}     # path -> (pres_id, n_orbits, ts) of the last beat

    def _news(self, rows):
        out = []
        for pid, row in rows.items():
            if pid in self.announced:
                continue
            self.announced.add(pid)
            tag = _lead_tag(row)
            if tag:
                out.append(f"{tag.strip()} [{pid}] chain "
                           f"{'+'.join(row['best_chain'])}")
        return out

    def maybe_beat(self, now=None):
        now = time.monotonic() if now is None else now
        if now - self.last < _HB_PERIOD:
            return None
        self.last = now
        rows = _scan_summary(self.sum_paths)
        lines = self._news(rows)
        for path in self.sum_paths:
            try:
                hb = json.load(open(path + ".hb"))
            except (OSError, ValueError):
                continue
            m = _CHUNK_MARK.search(os.path.basename(path))
            cid = m.group(0)[1:] if m else "all"
            # instantaneous orbits/s since the LAST beat (the rule: a slowing
            # CPU must show as a falling rate, never as silence). The sidecar
            # count is per-class, so the delta is only valid within one class.
            prev = self.prev_hb.get(path)
            self.prev_hb[path] = (hb["pres_id"], hb["n_orbits"], hb["ts"])
            if prev and prev[0] == hb["pres_id"] and hb["ts"] > prev[2] \
                    and hb["n_orbits"] >= prev[1]:
                rate = f"{(hb['n_orbits'] - prev[1]) / (hb['ts'] - prev[2]):.1f} orb/s"
            elif prev and prev[0] == hb["pres_id"] and hb["ts"] == prev[2]:
                # sidecar frozen: the worker is inside one very long hop, or
                # stalled — either way the age must be visible, not silent
                rate = f"no update for {int(time.time() - hb['ts'])}s"
            else:
                rate = "orb/s n/a"    # first sample of this class
            mu_in = hb.get("mu_in")
            if mu_in is None:
                vs = f"best {hb['best_mu']}"
            elif hb["best_mu"] is not None and hb["best_mu"] < mu_in:
                vs = (f"best {hb['best_mu']} (in {mu_in}, REDUCED "
                      f"-{mu_in - hb['best_mu']})")
            else:
                vs = f"best {hb['best_mu']} (in {mu_in})"
            lines.append(
                f"  [hb {cid}] {hb['done']}/{hb['total']} classes | now "
                f"{hb['pres_id']} rung {hb['rung']}, {hb['n_orbits']} orbits"
                f" @ {rate}, {vs}")
        done = len(rows)
        desc = sum(1 for r in rows.values() if r["best_mu"] < r["mu_in"])
        floor = min((r["best_mu"] for r in rows.values()), default=None)
        # every beat carries the headline: how many finished classes came out
        # BELOW their starting Aut-floor (live in-progress reductions show as
        # REDUCED on their chunk's own line above)
        total_line = (f"  [hb total] {done}/{self.total} classes done | "
                      f"{desc} reduced | floor {floor}")
        elapsed = now - self.t0
        if now - self.last_detail >= _DETAIL_EVERY:
            self.last_detail = now
            ran = done - self.done0
            eta = (f"~{(self.total - done) * (elapsed / ran) / 3600:.1f}h left"
                   if ran else "eta n/a")
            total_line += f" | {elapsed / 3600:.1f}h elapsed | {eta}"
        lines.append(total_line)
        return "\n".join(lines) if lines else None


def run(**overrides):
    """Entry point for the notebook and CLI. chunk_index: None = every chunk
    as its own spawned process here; an int = only that chunk, in-process
    (one per parallel Colab session); a list = those chunks as processes."""
    c = {**DEFAULTS, **{k: v for k, v in overrides.items() if v is not None
                        or k in ("chunk_index", "names")}}
    c["use_chunks"] = c["chunks"] > 1
    root = find_repo_root(HERE)
    n_rows = len(_load_rows(c, root))
    if not c["use_chunks"] or isinstance(c["chunk_index"], int):
        idx = c["chunk_index"] if c["use_chunks"] else 1
        return [run_chunk(c, idx)]

    import multiprocessing as mp
    indices = (list(range(1, c["chunks"] + 1)) if c["chunk_index"] is None
               else list(c["chunk_index"]))
    sum_paths = [_chunk_paths(c, n_rows, root, i)[0] for i in indices]
    hb = _LadderHeartbeat(sum_paths,
                          sum(len(_chunk_rows(range(n_rows), c["chunks"], i))
                              for i in indices))
    ctx = mp.get_context("spawn")
    procs = []
    for i in indices:
        ci = dict(c)
        ci["chunk_index"] = i
        p = ctx.Process(target=_spawn_entry, args=(ci,),
                        name=f"mu-ladder-chunk{i}")
        p.start()
        procs.append(p)
    print(f"[chunks] {len(procs)} chunk processes launched "
          f"({', '.join(f'c{i}of{c['chunks']}' for i in indices)}); "
          f"resume is per chunk", flush=True)
    while True:
        alive = [p for p in procs if p.is_alive()]
        if not alive:
            break
        alive[0].join(timeout=max(_HB_PERIOD / 4, 1.0))
        beat = hb.maybe_beat()
        if beat:
            print(beat, flush=True)
    failed = []
    for p in procs:
        p.join()
        if p.exitcode != 0:
            failed.append(p.name)
    if failed:
        raise RuntimeError(f"chunk process(es) failed: {failed} — rerun the "
                           f"same command; finished rows resume, only the "
                           f"failed chunk's remainder re-runs")
    final = hb.maybe_beat(now=time.monotonic() + _HB_PERIOD)
    if final:
        print(final, flush=True)
    return [_chunk_paths(c, n_rows, root, i) for i in indices]


# --------------------------------------------------------------------------
# merge

def merge_chunks(**overrides):
    """Concatenate COMPLETED chunk files into the canonical unchunked pair.
    Refuses (run_cov.py pattern): a missing/incomplete chunk (row sets are
    re-derived from the CSV stride, never trusted from the files), a pres_id
    repeated across chunks, orbit rows whose class is not committed, or an
    already-existing target. Merged output is in CSV row order, so it reads
    like a serial run's file."""
    c = {**DEFAULTS, **{k: v for k, v in overrides.items() if v is not None
                        or k in ("chunk_index", "names")}}
    c["use_chunks"] = True
    root = find_repo_root(HERE)
    rows_all = _load_rows(c, root)
    out_path, orbits_path = _merged_paths(c, len(rows_all), root)
    for p in (out_path, orbits_path):
        if os.path.exists(p):
            raise RuntimeError(f"merge target exists: {p}")

    by_pid, orb_by_pid, owner = {}, {}, {}
    for i in range(1, c["chunks"] + 1):
        cp, op = _chunk_paths(c, len(rows_all), root, i)
        expect = {r["name"] for r in _chunk_rows(rows_all, c["chunks"], i)}
        got = {}
        if os.path.exists(cp):
            for ln in open(cp):
                if ln.strip():
                    row = json.loads(ln)
                    got.setdefault(row["pres_id"], row)
        missing = expect - set(got)
        if missing:
            raise RuntimeError(
                f"chunk {i}/{c['chunks']} incomplete: {len(missing)} of "
                f"{len(expect)} classes missing (e.g. {sorted(missing)[:3]})")
        for pid, row in got.items():
            if pid in owner:
                raise RuntimeError(f"pres_id {pid} appears in chunks "
                                   f"{owner[pid]} and {i}")
            owner[pid] = i
            by_pid[pid] = row
        if os.path.exists(op):
            for ln in open(op):
                if ln.strip():
                    o = json.loads(ln)
                    orb_by_pid.setdefault(o["pres_id"], []).append(o)
    for pid, row in by_pid.items():
        n_orb = len(orb_by_pid.get(pid, []))
        if n_orb != row["n_orbits_seen"]:
            raise RuntimeError(f"{pid}: {n_orb} orbit rows on disk but "
                               f"n_orbits_seen={row['n_orbits_seen']}")

    order = [r["name"] for r in rows_all if r["name"] in by_pid]
    for path, per_pid in ((out_path, {p: [by_pid[p]] for p in by_pid}),
                          (orbits_path, orb_by_pid)):
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            for pid in order:
                for row in per_pid.get(pid, []):
                    f.write(json.dumps(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    print(f"merged {len(order)} classes -> {os.path.basename(out_path)} "
          f"+ {os.path.basename(orbits_path)}", flush=True)
    return out_path, orbits_path


# --------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=DEFAULTS["data"])
    ap.add_argument("--rungs", type=int, default=DEFAULTS["rungs"])
    ap.add_argument("--beam", type=int, default=DEFAULTS["beam"])
    ap.add_argument("--cap", type=int, default=DEFAULTS["cap"])
    ap.add_argument("--stop-mu", type=int, default=DEFAULTS["stop_mu"])
    ap.add_argument("--time-per-class", type=int,
                    default=DEFAULTS["time_per_class_s"])
    ap.add_argument("--max-orbits", type=int, default=DEFAULTS["max_orbits"])
    ap.add_argument("--chunks", type=int, default=DEFAULTS["chunks"])
    ap.add_argument("--chunk-index", type=int, default=None)
    ap.add_argument("--out-dir", default=DEFAULTS["out_dir"])
    ap.add_argument("--names", nargs="*", default=None)
    ap.add_argument("--no-high-speedup", action="store_true",
                    help="force the pure-Python aut_canon path "
                         "(identical rows, ~15x slower)")
    ap.add_argument("--merge", action="store_true",
                    help="merge completed chunk files instead of running")
    a = ap.parse_args()
    kw = dict(data=a.data, rungs=a.rungs, beam=a.beam, cap=a.cap,
              stop_mu=a.stop_mu, time_per_class_s=a.time_per_class,
              max_orbits=a.max_orbits, chunks=a.chunks,
              chunk_index=a.chunk_index, out_dir=a.out_dir, names=a.names,
              high_speedup=not a.no_high_speedup)
    if a.merge:
        merge_chunks(**kw)
    else:
        run(**kw)


if __name__ == "__main__":
    main()
