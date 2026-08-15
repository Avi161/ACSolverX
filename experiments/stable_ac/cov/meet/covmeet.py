"""CoV collision search ("covmeet"): merge the 124 unsolved Aut-classes by CoV moves only.

The idea (user's sketch, measured 2026-08-10): from each unsolved class representative,
enumerate EVERY valid change of variables (``cov.enumerate_cov`` — the (z, iso_gen,
iso_index) brute force over the pair's own subwords), take each output to its Aut-minimal
canonical orbit rep (``autcanon_fast.aut_min``), and pool everything into ONE store.
Every orbit row carries a bitmask of which seed classes have reached it; the moment an
orbit's mask holds bits from two different union-find classes, those classes are STABLY
AC-equivalent (a CoV chain from each side meets there) and 124 drops by one.

No substitution supermoves, no AC search anywhere in this pipeline — CoV edges and
Whitehead reduction only, zero search nodes.

STORAGE (v2, "covmeet2" — the user's policy). Disk stores results and resume state,
never bulk provenance:

* one ``o`` row per orbit at FIRST discovery (rep + mask), never again;
* an ``r`` row only when an orbit's mask GROWS (a cone overlap — the interesting case);
* an ``x`` row per expansion, by orbit index, carrying the census (raw CoVs → orbits);
* full chains are written ONLY for the events that are results: ``merge`` (two classes
  meet — both chains, seed to meeting orbit) and ``drop`` (a class reaches below its
  seeded aut-min — the chain to the new best rep). Parent pointers live in RAM only.

v1 logged every edge with its parent pair repeated per row; at 5.7 edges/expansion that
was ~85% of the bytes and grew superlinearly as cones overlap (a re-reach wrote a row
even when nothing changed). v2 writes nothing on a no-op re-reach. The cost of the
trade: individual ``o`` rows are not independently replayable (no move recorded), so
the full audit of a run is a deterministic re-run; merges and drops — the claims —
stay fully certified on disk. After a crash+resume, a later merge whose chain crosses
pre-resume territory is written truncated (``"truncated": true``) — the deterministic
fresh re-run reproduces it with the full chain.

Design decisions, each carrying a lesson or a measurement:

* **No relator-length cap.** ``REJECT_LEN`` in cov.py is the packed greedy solver's
  structural ceiling; this pipeline never calls that solver. Measured: ``aut_min`` is
  FLAT in input length (0.67 ms @ 10-19 letters -> 0.78 ms @ 90-99). A ceiling defines
  the space (lesson: ceiling-not-budget-was-binding) — here there deliberately is none.
  Relators longer than ``_PACK_THRESHOLD`` letters are stored 2-bit-packed+base64 on
  disk; measured shells (L 19-21, uncapped) top out at 59 letters, so this is insurance,
  not the common path.
* **Shortest-bucket-first.** The frontier is bucketed by total length and waves pop the
  shortest bucket. WAVE bounds a batch, never membership: what a wave doesn't pop stays
  queued, and the only stop is the frontier running dry (pinned by
  ``test_all_duplicate_children_do_not_stop_the_run``).
* **The jsonl IS the state.** Append-only events, parent-only writes, fsync per wave,
  torn trailing line repaired BEFORE the first append (lesson: run-baseline-two-known-
  bugs). Resume = replay.
* **Exact keys, no digests.** The store keys on the canonical rep pair itself. At 10^8+
  rows a 64-bit hash WILL collide, and a collision here is a false merge.
* **Expansion is once-per-orbit.** Mask growth keeps being recorded whenever any parent
  reaches a known orbit, so a first meeting is always detected; masks downstream of a
  late meeting are not back-propagated (the merge was already recorded at the meeting
  orbit).
* **Filename identity** = engine tag + seed set + family tag (single source of truth —
  lesson: identity-tag-shadowed-by-yaml). WAVE / CHUNK / WORKERS change wave boundaries
  and hence which orbit records a meeting first, but not the final masks, merges, or
  class count — they stay OUT of the filename. No dates in the filename either.
* **Heartbeat is TIME-based**, parent-only; first emission fires immediately (lessons:
  heartbeat-worker-cannot-print, heartbeat-first-emission-phase-bug).
* **Memory guard** trips on real system pressure (``MemAvailable``), never on a share.

A merge event proves the two classes STABLY AC-equivalent (CoV chains junction at
canonical reps and must be verified segment by segment — ``verify_covmeet.py`` replays
every recorded chain one step at a time; lesson: cov-chains-junction-at-canonical-reps).
Never claim unqualified AC-equivalence from this pipeline.
"""

import base64
import csv
import datetime
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError as _FutTimeout

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.ladder import autcanon_fast as af

ENGINE_TAG = "covmeet2"      # bump on ANY change to event semantics or expansion rule
SEED_SETS = ("all124", "reduced39")

# The user's rule for this experiment: NO length ceiling anywhere. cov.REJECT_LEN=239
# is the packed greedy solver's structural ceiling and cov.py marks it part of the
# family rule ("changing it requires a tag bump") — so we pass an effectively infinite
# reject_len and bump the tag accordingly. FAMILY is this run's identity, one constant.
REJECT_LEN_UNCAPPED = 10 ** 9
FAMILY = cov.SUBWORD_FAMILY_TAG + "nolim"

HEARTBEAT_S = 60             # instantaneous beat
CUMULATIVE_S = 300           # cumulative done/frontier/merges line

_PACK_THRESHOLD = 120        # letters; longer relators are packed+b64 on disk
_PACK_BITS = {"x": 0, "X": 1, "y": 2, "Y": 3}
_PACK_CHARS = "xXyY"


# --------------------------------------------------------------------- word codec

def _enc_word(w):
    """Disk form of one relator: plain ascii, or ``~<len>:<b64>`` when long."""
    if len(w) <= _PACK_THRESHOLD:
        return w
    out = bytearray()
    for i in range(0, len(w), 4):
        b = 0
        for j, c in enumerate(w[i:i + 4]):
            b |= _PACK_BITS[c] << (2 * j)
        out.append(b)
    return f"~{len(w)}:" + base64.b64encode(bytes(out)).decode()


def _dec_word(s):
    if not s.startswith("~"):
        return s
    head, b64 = s[1:].split(":", 1)
    n = int(head)
    raw = base64.b64decode(b64)
    return "".join(_PACK_CHARS[raw[i // 4] >> (2 * (i % 4)) & 3] for i in range(n))


def _enc_rep(rep):
    return [_enc_word(rep[0]), _enc_word(rep[1])]


def _dec_rep(v):
    return (_dec_word(v[0]), _dec_word(v[1]))


# --------------------------------------------------------------------------- seeds

def repo_root():
    """Walk up until experiments/ + data/ are siblings (never dirname-count)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "experiments")) and \
                os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found (experiments/ + data/ siblings)")


def load_seeds(seed_set):
    """``[(name, r1, r2)]`` from aca_124_reduced.csv, in file order.

    ``all124``: every class at its best known representative — the 39 reduced rows
    start from their CoV-descended rep (``new_r1``/``new_r2``), the other 85 from the
    Aut-min rep the file carries. ``reduced39``: only the 39. all124 is the version
    whose answer is "124 - S"; reduced39 caps the result at 38 merges and cannot merge
    a reduced class with a non-reduced one.
    """
    if seed_set not in SEED_SETS:
        raise ValueError(f"seed_set must be one of {SEED_SETS}, got {seed_set!r}")
    path = os.path.join(repo_root(), "data", "ms_unsolved_reps", "aca_124_reduced.csv")
    out = []
    with open(path) as f:
        for row in csv.DictReader(f):
            reduced = row["reduced"] == "yes"
            if seed_set == "reduced39" and not reduced:
                continue
            r1, r2 = (row["new_r1"], row["new_r2"]) if reduced else (row["r1"], row["r2"])
            out.append((row["name"], r1, r2))
    want = 124 if seed_set == "all124" else 39
    if len(out) != want:
        raise RuntimeError(f"{seed_set}: expected {want} seeds, got {len(out)}")
    return out


def run_paths(out_dir, seed_set):
    """(events_jsonl, summary_json). Identity = engine + seed set + family tag."""
    stem = f"{ENGINE_TAG}_{seed_set}_{FAMILY}"
    return (os.path.join(out_dir, stem + ".jsonl"),
            os.path.join(out_dir, stem + "_summary.json"))


# --------------------------------------------------------------------------- worker

def _expand_chunk(pairs):
    """Expand canonical rep pairs: every CoV, Aut-min each output, aggregate per orbit.

    Returns ``[(rep, ncov, children)]`` with ``children`` sorted for determinism:
    ``[(child_rep, mu, z_str, iso_gen, iso_index, multiplicity)]``. The recorded move is
    the FIRST (family order) CoV landing on that orbit — enough to replay the edge —
    and ``multiplicity`` is the census: how many raw CoVs of this expansion land there.
    Self-loops (child orbit == parent) are counted into ``ncov`` but emit no edge.
    """
    out = []
    for a, b in pairs:
        wa, wb = str_to_word(a), str_to_word(b)
        results = cov.enumerate_cov(wa, wb, reject_len=REJECT_LEN_UNCAPPED)
        agg = {}
        for res in results:
            mu, rep = af.aut_min((word_to_str(res.r1), word_to_str(res.r2)))
            if rep == (a, b):
                continue
            hit = agg.get(rep)
            if hit is None:
                agg[rep] = [mu, word_to_str(res.z_word), res.iso_gen,
                            int(res.iso_index), 1]
            else:
                hit[4] += 1
        children = [(rep, v[0], v[1], v[2], v[3], v[4])
                    for rep, v in sorted(agg.items())]
        out.append(((a, b), len(results), children))
    return out


def _warm_worker():
    af.warm()


# --------------------------------------------------------------------------- store

class _UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, i, j):
        ri, rj = self.find(i), self.find(j)
        if ri != rj:
            self.p[max(ri, rj)] = min(ri, rj)
        return ri != rj

    def roots(self):
        return {self.find(i) for i in range(len(self.p))}


class Store:
    """In-memory mirror of the events file. Rebuilt exactly by replaying it.

    ``parent`` (rep -> (parent_rep, z, iso, br)) is RAM-ONLY provenance for chain
    extraction on merge/drop; it is deliberately NOT rebuilt by replay — see the
    module docstring on truncated post-resume chains.
    """

    def __init__(self, n_seeds):
        self.mask = {}                    # rep -> int bitmask of seed classes
        self.mu = {}                      # rep -> aut-min total length
        self.index = {}                   # rep -> orbit index (discovery order)
        self.reps = []                    # orbit index -> rep
        self.parent = {}                  # RAM only: rep -> (prep, z, iso, br)
        self.expanded = set()             # reps whose expansion completed (x row)
        self.frontier = {}                # L -> set of unexpanded reps
        self.uf = _UF(n_seeds)
        self.merges = []                  # (rep, seed_i, seed_j) as first detected
        self.best_mu = {}                 # seed i -> lowest mu its cone has reached
        self.seed_mu = {}                 # seed i -> mu of its starting rep
        self.drops = []                   # (seed_i, mu, rep): reached BELOW seed_mu[i]
        self.n_expansions_logged = 0
        self.n_cov_total = 0

    def _bucket_add(self, rep):
        L = len(rep[0]) + len(rep[1])
        self.frontier.setdefault(L, set()).add(rep)

    def reach(self, rep, mu, bits):
        """OR ``bits`` into ``rep``'s mask.

        Returns ``(kind, merged, drops)`` where kind is ``"new"`` (first discovery —
        an ``o``/``seed`` row is due), ``"grew"`` (mask gained bits — an ``r`` row is
        due), or ``None`` (no change — NOTHING is written, the v2 size fix). A drop is
        seed ``i``'s cone reaching an orbit with mu STRICTLY BELOW its seeded mu.
        """
        old = self.mask.get(rep, 0)
        new = old | bits
        if new == old:
            return None, None, ()
        if old == 0:
            self.index[rep] = len(self.reps)
            self.reps.append(rep)
            self.mu[rep] = mu
            if rep not in self.expanded:
                self._bucket_add(rep)
        self.mask[rep] = new
        drops = []
        added = new & ~old
        for i in range(added.bit_length()):
            if added >> i & 1:
                prev = self.best_mu.get(i)
                if prev is None:
                    self.best_mu[i] = mu
                    self.seed_mu[i] = mu          # first sight of this bit = its seed
                elif mu < prev:
                    self.best_mu[i] = mu
                    drops.append((i, mu, rep))
                    self.drops.append((i, mu, rep))
        merged = None
        seeds = [i for i in range(bits.bit_length()) if bits >> i & 1]
        base = seeds[0] if old == 0 else next(
            i for i in range(old.bit_length()) if old >> i & 1)
        for i in seeds:
            if self.uf.union(base, i):
                merged = (rep, self.uf.find(base), i)
                self.merges.append(merged)
        return ("new" if old == 0 else "grew"), merged, drops

    def mark_expanded(self, rep, ncov):
        self.expanded.add(rep)
        self.n_expansions_logged += 1
        self.n_cov_total += ncov
        L = len(rep[0]) + len(rep[1])
        b = self.frontier.get(L)
        if b is not None:
            b.discard(rep)
            if not b:
                del self.frontier[L]

    def take_wave(self, wave):
        """Up to ``wave`` reps from the shortest bucket, sorted — deterministic."""
        if not self.frontier:
            return []
        L = min(self.frontier)
        batch = sorted(self.frontier[L])[:wave]
        for rep in batch:
            self.frontier[L].discard(rep)
        if not self.frontier[L]:
            del self.frontier[L]
        return batch

    def frontier_size(self):
        return sum(len(v) for v in self.frontier.values())

    def chain(self, rep):
        """RAM lineage of ``rep``: ``[{"rep": ...}, {"z","iso","br","rep"}, ...]``.

        Walks ``parent`` back to a seed. If the walk hits an orbit with no parent
        entry that is not a seed (its discovery predates this session — parents are
        RAM-only), the chain is returned truncated with a leading marker; the
        deterministic fresh re-run reproduces the full chain.
        """
        steps = []
        cur = rep
        while True:
            hit = self.parent.get(cur)
            if hit is None:
                head = {"rep": _enc_rep(cur)}
                if self.index.get(cur, 0) >= len(self.seed_mu):
                    head["truncated"] = True
                return [head] + steps[::-1]
            prep, z, iso, br = hit
            steps.append({"z": z, "iso": iso, "br": br, "rep": _enc_rep(cur)})
            cur = prep


# --------------------------------------------------------------------------- events

def _repair_torn_tail(path):
    """Truncate a torn trailing line BEFORE the first append, never merely tolerate it."""
    if not os.path.exists(path):
        return 0
    size = os.path.getsize(path)
    if size == 0:
        return 0
    with open(path, "rb+") as f:
        f.seek(max(0, size - (1 << 20)))
        tail = f.read()
        if tail.endswith(b"\n"):
            last = tail[:-1].rsplit(b"\n", 1)[-1]
            try:
                json.loads(last)
                return 0
            except Exception:
                pass                      # complete but corrupt line: cut it too
            good = size - (len(last) + 1)
        else:
            last = tail.rsplit(b"\n", 1)[-1]
            good = size - len(last)
        f.truncate(good)
        return size - good


def replay(events_path, n_seeds, expect_family=None):
    """Rebuild the Store from the events file. Merges/drops are re-derived, not read."""
    store = Store(n_seeds)
    if not os.path.exists(events_path):
        return store, None
    meta = None
    with open(events_path) as f:
        for line in f:
            ev = json.loads(line)
            t = ev["t"]
            if t == "meta":
                if meta is None:
                    meta = ev
                    if expect_family and ev["family"] != expect_family:
                        raise RuntimeError(
                            f"resume file family {ev['family']!r} != current "
                            f"{expect_family!r} — a different family is a different "
                            f"experiment and must never share a resume file")
                    if ev.get("engine") != ENGINE_TAG:
                        raise RuntimeError(
                            f"resume file engine {ev.get('engine')!r} != "
                            f"{ENGINE_TAG!r} — event semantics differ; start fresh")
            elif t == "seed":
                store.reach(_dec_rep(ev["rep"]), ev["mu"], 1 << ev["i"])
            elif t == "o":
                rep = _dec_rep(ev["rep"])
                store.reach(rep, len(rep[0]) + len(rep[1]), int(ev["m"], 16))
            elif t == "r":
                rep = store.reps[ev["i"]]
                store.reach(rep, store.mu[rep], int(ev["m"], 16))
            elif t == "x":
                store.mark_expanded(store.reps[ev["i"]], ev["nc"])
            # "merge" and "drop" rows are certificates; replay re-derives both
    return store, meta


class _Writer:
    def __init__(self, path):
        self.f = open(path, "a", encoding="utf-8")

    def row(self, obj):
        self.f.write(json.dumps(obj, separators=(",", ":")) + "\n")

    def sync(self):
        self.f.flush()
        os.fsync(self.f.fileno())

    def close(self):
        self.sync()
        self.f.close()


# --------------------------------------------------------------------------- run

def _mem_available_gb():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1e6
    except Exception:
        pass
    return None


def summarise(store, seeds):
    names = [s[0] for s in seeds]
    roots = store.uf.roots()
    merged_pairs = [{"at": list(rep), "into": names[a], "joined": names[b]}
                    for rep, a, b in store.merges]
    improved = [{"name": names[i], "seed_mu": store.seed_mu[i],
                 "best_mu": store.best_mu[i]}
                for i in sorted(store.best_mu)
                if store.best_mu[i] < store.seed_mu.get(i, store.best_mu[i])]
    return {
        "engine": ENGINE_TAG, "family": FAMILY,
        "n_seeds": len(seeds), "classes_remaining": len(roots),
        "merges_found": len(store.merges), "merged": merged_pairs,
        "improved_below_seed": improved, "n_improved": len(improved),
        "expanded": len(store.expanded), "discovered": len(store.mask),
        "frontier": store.frontier_size(),
        "shortest_open_bucket": min(store.frontier) if store.frontier else None,
        "raw_cov_enumerated": store.n_cov_total,
    }


def run(out_dir, seed_set="all124", workers=None, wave=4096, chunk=8,
        max_expanded=None, max_seconds=None, mem_guard_gb=8.0, log=print,
        seeds_override=None):
    """Anytime, resumable CoV collision search. Returns the summary dict.

    Every knob except ``seed_set`` is throughput/stopping only and does not change the
    final masks, merges or class count. ``max_seconds`` is the smoke run's TIME bound
    (rows written under it are real rows the full run resumes from); ``max_expanded``
    is a test/backstop budget.
    """
    os.makedirs(out_dir, exist_ok=True)
    # seeds_override is the TEST seam (like run_baseline's SOLVER): a tiny controlled
    # seed list under a private seed_set label, so tests never touch the real datasets.
    seeds = seeds_override if seeds_override is not None else load_seeds(seed_set)
    events_path, summary_path = run_paths(out_dir, seed_set)

    cut = _repair_torn_tail(events_path)
    if cut:
        log(f"[covmeet] repaired torn tail: truncated {cut} bytes")
    store, meta = replay(events_path, len(seeds), expect_family=FAMILY)
    resumed = meta is not None
    w = _Writer(events_path)
    w.row({"t": "meta", "engine": ENGINE_TAG, "family": FAMILY,
           "seed_set": seed_set, "n_seeds": len(seeds),
           "session_utc": datetime.datetime.utcnow().isoformat(timespec="seconds")})
    if not resumed:
        af.warm()
        for i, (name, r1, r2) in enumerate(seeds):
            mu, rep = af.aut_min((r1, r2))
            w.row({"t": "seed", "i": i, "name": name,
                   "rep": _enc_rep(rep), "mu": mu})
            store.reach(rep, mu, 1 << i)
        w.sync()
        log(f"[covmeet] fresh run: {len(seeds)} seeds canonicalised")
    else:
        log(f"[covmeet] RESUMED: {len(store.expanded)} expanded, "
            f"{len(store.mask)} discovered, {len(store.merges)} merges, "
            f"frontier {store.frontier_size()}")

    if workers is None:
        workers = max(1, (os.cpu_count() or 2) - 1)
    pool = None
    if workers > 0:
        import multiprocessing as mp
        pool = ProcessPoolExecutor(max_workers=workers,
                                   mp_context=mp.get_context("spawn"),
                                   initializer=_warm_worker)
    else:
        af.warm()

    t0 = time.time()
    expanded0 = len(store.expanded)
    last_beat = [0.0]                 # 0 => first heartbeat fires immediately
    last_cum = [time.time()]
    beat_prev = [time.time(), expanded0]

    def heartbeat(force=False):
        now = time.time()
        if not force and now - last_beat[0] < HEARTBEAT_S:
            return
        dt = max(now - beat_prev[0], 1e-9)
        rate = (len(store.expanded) - beat_prev[1]) / dt
        L = min(store.frontier) if store.frontier else None
        log(f"[hb] +{now - t0:7.0f}s  expanded {len(store.expanded):>9,} "
            f"({rate:6.2f} st/s)  discovered {len(store.mask):>10,}  "
            f"frontier {store.frontier_size():>9,}  bucket L={L}  "
            f"merges {len(store.merges)}")
        last_beat[0] = now
        beat_prev[:] = [now, len(store.expanded)]
        if now - last_cum[0] >= CUMULATIVE_S:
            mem = _mem_available_gb()
            tot_rate = (len(store.expanded) - expanded0) / max(now - t0, 1e-9)
            try:
                mb = os.path.getsize(events_path) / 1e6
            except OSError:
                mb = 0.0
            log(f"[cum] {datetime.datetime.utcnow().isoformat(timespec='seconds')}Z  "
                f"session {(now - t0) / 3600:.2f} h  {tot_rate:.2f} st/s avg  "
                f"raw CoVs {store.n_cov_total:,}  classes "
                f"{len(store.uf.roots())}/{len(seeds)}  events {mb:,.0f} MB  "
                f"mem_avail {mem and f'{mem:.1f}'} GB")
            last_cum[0] = now

    def stop_reason():
        if max_expanded is not None and \
                len(store.expanded) - expanded0 >= max_expanded:
            return f"max_expanded {max_expanded} reached"
        if max_seconds is not None and time.time() - t0 >= max_seconds:
            return f"time bound {max_seconds:.0f}s reached (smoke)"
        if mem_guard_gb:
            mem = _mem_available_gb()
            if mem is not None and mem < mem_guard_gb:
                return f"memory guard: MemAvailable {mem:.1f} GB < {mem_guard_gb} GB"
        return None

    heartbeat(force=True)
    reason = None
    try:
        while True:
            reason = stop_reason()
            if reason:
                break
            batch = store.take_wave(wave)
            if not batch:
                reason = "frontier exhausted — the CoV graph is CLOSED for this seed set"
                break
            chunks = [batch[i:i + chunk] for i in range(0, len(batch), chunk)]
            if pool is not None:
                futs = [pool.submit(_expand_chunk, c) for c in chunks]
                results = []
                for fut in futs:              # submission order => deterministic
                    while True:
                        try:
                            results.append(fut.result(timeout=5))
                            break
                        except _FutTimeout:
                            heartbeat()
            else:
                results = [_expand_chunk(c) for c in chunks]
            for chunk_res in results:
                for rep, ncov, children in chunk_res:
                    pmask = store.mask[rep]
                    hexmask = format(pmask, "x")
                    for crep, mu, z, iso, br, n in children:
                        known = crep in store.mask
                        kind, merged, drops = store.reach(crep, mu, pmask)
                        if not known and kind == "new":
                            store.parent[crep] = (rep, z, iso, br)
                            w.row({"t": "o", "i": store.index[crep],
                                   "rep": _enc_rep(crep), "m": hexmask})
                        elif kind == "grew":
                            w.row({"t": "r", "i": store.index[crep],
                                   "m": hexmask})
                        for di, dmu, drep in drops:
                            w.row({"t": "drop", "i": di, "name": seeds[di][0],
                                   "mu": dmu, "from": store.seed_mu[di],
                                   "rep": _enc_rep(drep),
                                   "chain": store.chain(drep)})
                            log(f"[DROP] {seeds[di][0]}: mu {store.seed_mu[di]} "
                                f"-> {dmu} at {drep} — below its reduced aut-min "
                                f"start")
                        if merged:
                            mrep, a, b = merged
                            w.row({"t": "merge", "at": store.index[mrep],
                                   "rep": _enc_rep(mrep),
                                   "classes": [seeds[a][0], seeds[b][0]],
                                   "remaining": len(store.uf.roots()),
                                   "chains": [store.chain(mrep),
                                              store.chain(rep) +
                                              [{"z": z, "iso": iso, "br": br,
                                                "rep": _enc_rep(mrep)}]]})
                            log(f"[MERGE] {seeds[a][0]} ≡ {seeds[b][0]} at "
                                f"{mrep} — {len(store.uf.roots())} classes remain")
                    w.row({"t": "x", "i": store.index[rep], "nc": ncov,
                           "no": len(children)})
                    store.mark_expanded(rep, ncov)
            w.sync()                          # the wave reaches disk before the next
            heartbeat()
    finally:
        if pool is not None:
            pool.shutdown(wait=False, cancel_futures=True)
        w.close()
        summary = summarise(store, seeds)
        summary["stopped"] = reason or "interrupted"
        with open(summary_path + ".tmp", "w") as f:
            json.dump(summary, f, indent=1)
        os.replace(summary_path + ".tmp", summary_path)

    heartbeat(force=True)
    log(f"[covmeet] stopped: {reason}")
    log(f"[covmeet] classes remaining: {summary['classes_remaining']}"
        f"/{len(seeds)}  merges: {summary['merges_found']}  "
        f"classes below their seed mu: {summary['n_improved']}")
    return summary
