/*
 * data.js — the data spine for the AC-SolverX Path Explorer.
 *
 * Pure, dependency-free, and Node-testable (exported at the bottom). Everything that
 * depends on the exact record schema and the AC-move semantics lives HERE so the view
 * layer never has to reconstruct it. Two record streams are consumed:
 *
 *   PATH record       (paths_*.jsonl):  has `states` + `moves`. The full solution path.
 *   CALIBRATION record (calibration_*.jsonl): has `solved`/`nodes_explored`/... . Metrics.
 *
 * Both carry (dataset, idx, arm, budget_nodes); they are merged on that 4-tuple.
 *
 * KEY SEMANTICS (get these wrong and the viewer lies):
 *  - n_gen = 3. The TRIVIAL presentation is THREE unit-length relators (total length 3),
 *    NOT length 2 like the 2-generator Miller-Schupp reference.
 *  - Every stored state is CANONICAL and SORTED (relators reordered by (len, bytes) each
 *    step). So relator array positions are NOT stable across steps. Identify a relator by
 *    CONTENT, never by slot. The per-step change is the multiset difference between the two
 *    states (exactly one relator leaves, one enters — a substitution supermove).
 *  - z (generator 3) MIGRATES. The "z = w" change-of-variables framing applies to state[0]
 *    ONLY. `decodeZWord` recovers w GENERICALLY from state[0] for ANY defining word w
 *    (r1, r2, x, y, or an arbitrary g) — this is what makes the viewer dynamic across arms.
 *  - The move tuple (emitted_slot, ra_rot, c_rot, c_is_inverse) does NOT uniquely pin the
 *    operand pair, so we NEVER fabricate a "B·C" reconstruction. We show old→new (from the
 *    diff) and expose the tuple as raw metadata.
 */
(function (global) {
  "use strict";

  // ---- alphabet -----------------------------------------------------------------
  const BASE = ["", "x", "y", "z", "u", "v", "w"]; // generator index -> lowercase letter
  const SUB = { 1: "₁", 2: "₂", 3: "₃", 4: "₄" }; // subscripts

  function letter(v) {
    if (v === 0) return "";
    const a = Math.abs(v);
    const ch = a < BASE.length ? BASE[a] : "g" + a;
    return v < 0 ? ch.toUpperCase() : ch;
  }

  /** Word (array of signed ints, 0=pad) -> string, e.g. [-2,1] -> "Yx". Padding dropped. */
  function wordToStr(word) {
    if (!word || word.length === 0) return "ε"; // epsilon for the empty word
    let s = "";
    for (const v of word) if (v !== 0) s += letter(v);
    return s === "" ? "ε" : s;
  }

  /** Rich tokens for colored rendering: [{v, ch, gen, inverse}] (padding dropped). */
  function wordToTokens(word) {
    const out = [];
    if (!word) return out;
    for (const v of word) {
      if (v === 0) continue;
      out.push({ v: v, ch: letter(v), gen: Math.abs(v), inverse: v < 0 });
    }
    return out;
  }

  // ---- word algebra (for the generic z=w decode) --------------------------------
  function invertWord(w) {
    const out = [];
    for (let i = w.length - 1; i >= 0; i--) out.push(-w[i]);
    return out;
  }
  function freeReduce(w) {
    const out = [];
    for (const a of w) {
      if (out.length && out[out.length - 1] === -a) out.pop();
      else out.push(a);
    }
    return out;
  }
  function cyclicReduce(w) {
    let r = freeReduce(w);
    let i = 0, j = r.length - 1;
    while (i < j && r[i] === -r[j]) { i++; j--; }
    return r.slice(i, j + 1);
  }

  /**
   * Recover the change-of-variables word w from a STABILIZED initial state (state[0]).
   * The z-relator is cyclic_reduce([z] ++ inverse(w)); z appears exactly once. Normalize
   * its orientation so +z is present, rotate +z to the front, strip it -> that suffix is
   * w^{-1}; return cyclic_reduce(inverse(suffix)) = w. Works for ANY w. Returns null if no
   * z-relator (e.g. a later, migrated state — only call this on state[0]).
   */
  function decodeZWord(state, zGen) {
    zGen = zGen || 3;
    for (const rel0 of state) {
      let hasZ = false;
      for (const v of rel0) if (Math.abs(v) === zGen) { hasZ = true; break; }
      if (!hasZ) continue;
      let r = rel0.slice();
      if (r.indexOf(zGen) === -1) r = invertWord(r); // was -z: flip so +z present
      const p = r.indexOf(zGen);
      r = r.slice(p).concat(r.slice(0, p)); // rotate +z to front
      return cyclicReduce(invertWord(r.slice(1)));
    }
    return null;
  }

  // ---- state helpers ------------------------------------------------------------
  function relKey(rel) { return rel.join(","); } // stored relators are canonical -> exact eq
  function stateTotalLen(state) { let n = 0; for (const r of state) n += r.length; return n; }
  function isTrivialState(state) {
    for (const r of state) if (r.length !== 1) return false;
    return true;
  }

  /**
   * Multiset difference of two states (arrays of relators). Returns {removed, added} — the
   * relators present in `prev` but not `curr`, and vice versa, by content. For a valid
   * substitution step this is exactly one removed + one added.
   */
  function multisetDiff(prev, curr) {
    const cnt = new Map(), rep = new Map();
    for (const r of prev) { const k = relKey(r); cnt.set(k, (cnt.get(k) || 0) + 1); rep.set(k, r); }
    for (const r of curr) { const k = relKey(r); cnt.set(k, (cnt.get(k) || 0) - 1); rep.set(k, r); }
    const removed = [], added = [];
    for (const [k, c] of cnt) {
      for (let i = 0; i < c; i++) removed.push(rep.get(k));
      for (let i = 0; i < -c; i++) added.push(rep.get(k));
    }
    return { removed: removed, added: added };
  }

  // ---- record classification + merge --------------------------------------------
  function classifyRecord(r) {
    if (r && r.kind === "registry" && Array.isArray(r.relators)) return "registry";
    if (r && Array.isArray(r.states) && Array.isArray(r.moves)) return "path";
    if (r && (typeof r.solved === "boolean" || typeof r.nodes_explored === "number")) return "calibration";
    return "unknown";
  }
  function mergeKey(r) {
    return r.dataset + "|" + r.idx + "|" + r.arm + "|" + r.budget_nodes;
  }
  function armSymbol(arm) {
    if (arm === "r1") return "r₁";
    if (arm === "r2") return "r₂";
    return arm;
  }

  // Canonical arm display order shared by every view (baseline first, then the four
  // z=w words). viewer.js keeps its own baseline-less order on purpose — the player
  // hides the baseline arm entirely.
  const ARM_ORDER = ["baseline", "r1", "r2", "x", "y"];
  function armSort(a, b) {
    let ia = ARM_ORDER.indexOf(a), ib = ARM_ORDER.indexOf(b);
    ia = ia === -1 ? 99 : ia; ib = ib === -1 ? 99 : ib;
    if (ia !== ib) return ia - ib;
    return a < b ? -1 : a > b ? 1 : 0;
  }

  /** Median of the finite values (nulls/NaN dropped). Shared by every view's tables. */
  function median(nums) {
    const vals = nums.filter((v) => v != null && !isNaN(v)).slice().sort((a, b) => a - b);
    const n = vals.length;
    if (n === 0) return null;
    const mid = Math.floor(n / 2);
    return n % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
  }

  /** HTML-escape for record-derived strings landing in innerHTML sinks (arm names,
   *  registry class names — all uploadable, so never trust them). */
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // ---- parsing ------------------------------------------------------------------
  /** Tolerant JSONL/JSON-array parser. Skips blank/corrupt lines (e.g. a truncated tail). */
  function parseJsonl(text) {
    const trimmed = (text || "").trim();
    if (!trimmed) return [];
    if (trimmed[0] === "[") {
      try { const arr = JSON.parse(trimmed); if (Array.isArray(arr)) return arr; } catch (e) { /* fall through */ }
    }
    const out = [];
    const lines = trimmed.split("\n");
    for (const line of lines) {
      const s = line.trim();
      if (!s) continue;
      try { out.push(JSON.parse(s)); } catch (e) { /* skip corrupt/partial line */ }
    }
    return out;
  }

  /**
   * Solvedness gate for a path record with no calibration row. Full validatePath,
   * except a 2-generator (baseline) path has no z-relator to decode — accept when the
   * z-word decode is the ONLY failure (final state must still be trivial and every
   * step a clean 1-out/1-in substitution).
   */
  function pathLooksSolved(p) {
    const v = validatePath(p);
    if (v.ok) return true;
    return v.errors.length > 0 && v.errors.every((e) => e.indexOf("z-word") !== -1);
  }

  // ---- dataset assembly ---------------------------------------------------------
  /**
   * Merge any number of mixed records (from any number of uploaded files) into a queryable
   * model. `items` is one entry per unique (dataset, idx, arm, budget); `byIdx` groups the
   * arms available for each (dataset, idx) — this is what powers the per-presentation arm
   * selector ("view this presentation under z=r1 / z=x / z=g / ...").
   */
  function buildDataset(records) {
    const calibrations = [], paths = [], registries = [];
    for (const r of records) {
      const t = classifyRecord(r);
      if (t === "path") paths.push(r);
      else if (t === "calibration") calibrations.push(r);
      else if (t === "registry") registries.push(r);
    }
    const pathByKey = new Map();
    for (const p of paths) pathByKey.set(mergeKey(p), p);

    const items = new Map();
    for (const c of calibrations) {
      const k = mergeKey(c);
      items.set(k, {
        key: k, dataset: c.dataset, idx: c.idx, arm: c.arm, budget: c.budget_nodes,
        solved: !!c.solved, calib: c, path: pathByKey.get(k) || null,
      });
    }
    for (const p of paths) { // a path with no calibration row (defensive)
      const k = mergeKey(p);
      // A bare path is only a solve if it actually replays to the trivial presentation —
      // a truncated/foreign upload must not be counted solved on faith.
      if (!items.has(k)) items.set(k, {
        key: k, dataset: p.dataset, idx: p.idx, arm: p.arm, budget: p.budget_nodes,
        solved: pathLooksSolved(p), calib: null, path: p,
      });
    }

    const itemList = Array.from(items.values());
    const byIdx = new Map();
    for (const it of itemList) {
      const gk = it.dataset + "|" + it.idx;
      if (!byIdx.has(gk)) byIdx.set(gk, { key: gk, dataset: it.dataset, idx: it.idx, arms: new Map(), reg: null });
      byIdx.get(gk).arms.set(it.arm, it);
    }
    // Registry records declare presentations that EXIST even if never attempted (e.g. the
    // hard 550 of MS(1190)). They create entries with an empty arms map, so totals can be
    // counted over the full dataset universe, not just what was run.
    for (const reg of registries) {
      const gk = reg.dataset + "|" + reg.idx;
      if (!byIdx.has(gk)) byIdx.set(gk, { key: gk, dataset: reg.dataset, idx: reg.idx, arms: new Map(), reg: reg });
      else byIdx.get(gk).reg = reg;
    }
    for (const entry of byIdx.values()) entry.subset = subsetOfEntry(entry);

    const arms = Array.from(new Set(itemList.map((i) => i.arm))).sort(armSort);
    const datasets = Array.from(new Set(itemList.map((i) => i.dataset).concat(registries.map((r) => r.dataset))));
    const budgets = Array.from(new Set(itemList.map((i) => i.budget))).sort((a, b) => a - b);
    const subsets = Array.from(new Set(Array.from(byIdx.values()).map((e) => e.subset).filter(Boolean)));

    // Which arms EXIST for each dataset (e.g. {baseline,r1,r2,x,y} for 1190MS, {r1,r2,x,y}
    // for ms_reps_unsolved). The sets feed rep-coverage lookups; the counts are informational.
    const armSets = {};
    for (const it of itemList) (armSets[it.dataset] || (armSets[it.dataset] = new Set())).add(it.arm);
    const armsByDataset = {};
    for (const k in armSets) armsByDataset[k] = armSets[k].size;

    return {
      calibrations: calibrations, paths: paths, registries: registries,
      items: itemList, byKey: items, byIdx: byIdx,
      arms: arms, datasets: datasets, budgets: budgets, subsets: subsets,
      armsByDataset: armsByDataset, armSetsByDataset: armSets,
      // Deliberately minimal: `total` (record rows) and `withPath` (stored solutions) are
      // the only item-level counts safe to headline. Anything solved/unsolved MUST go
      // through groupStats (presentation-first) — item-level solve counts read up to 5×
      // the presentation truth and were removed as an attractive nuisance.
      counts: {
        total: itemList.length,
        withPath: itemList.filter((i) => i.path).length,
      },
    };
  }

  // ---- provenance subsets ---------------------------------------------------------
  // MS(1190) splits into the ORIGINAL 640 we ran locally (idx 0–639) and the HARD
  // remaining 550 (idx 640–1189). Provenance comes from the registry record when
  // present, else from the idx threshold; other datasets get their own label.
  const SUBSET_LABELS = {
    original: "Original 640",
    hard: "Hard 550",
    reps: "Unsolved-class reps",
  };
  const MS_SPLIT = 640;
  const REPS_DATASET = "ms_reps_unsolved";

  const DATASET_LABELS = {
    "1190MS": "MS(1190) — full family",
    ms_reps_unsolved: "Unsolved-class reps (261)",
  };

  function datasetLabel(name) {
    return DATASET_LABELS[name] || name;
  }

  function subsetOfEntry(entry) {
    if (entry.reg && entry.reg.subset) return entry.reg.subset;
    if (entry.dataset === "1190MS") return entry.idx < MS_SPLIT ? "original" : "hard";
    if (entry.dataset === "ms_reps_unsolved") return "reps";
    return null;
  }

  function subsetLabel(subset) {
    return SUBSET_LABELS[subset] || subset || "—";
  }

  function itemPathLen(it) {
    if (!it) return null;
    if (it.calib && it.calib.path_len != null) return it.calib.path_len;
    if (it.path && it.path.path_len != null) return it.path.path_len;
    return null;
  }

  /**
   * PRESENTATION-first stats for a selection — the counting unit is always one presentation,
   * never a (presentation × z-word) cell, so 1190MS reads Total 1190 under any arm scope.
   * Buckets partition `total`:
   *   solved           — a run in scope solved it (best path length per presentation kept);
   *                      a rep-level solve would also land here
   *   unsolvedSearched — directly searched under the scope's arm(s), budget exhausted
   *   coveredViaReps   — never run directly, but its unsolved-class representative
   *                      (reg.rep_idx → the ms_reps_unsolved dataset) WAS searched under the
   *                      scope's arm(s) and stayed unsolved
   *   notAttempted     — nothing searched, directly or via a representative
   *   sel = { dataset: "all"|name, arm: "all"|arm, subset: "all"|subset,
   *           excludeArms: Set|array (optional) }
   * `excludeArms` drops those arms from the arm="all" union — the Solutions (z = w) view
   * passes its hidden baseline arm so "All z-words" never counts a baseline-only solve.
   * `attempted` counts directly-searched presentations only. `unsolved` is a back-compat
   * alias of `unsolvedSearched`. `avgPathLen` = mean over each solved presentation's best path.
   */
  function groupStats(ds, sel) {
    sel = sel || {};
    const wantDs = sel.dataset || "all", wantArm = sel.arm || "all", wantSub = sel.subset || "all";
    const excluded = sel.excludeArms
      ? (sel.excludeArms instanceof Set ? sel.excludeArms : new Set(sel.excludeArms))
      : null;
    const armInScope = (arm) => (wantArm === "all" ? !(excluded && excluded.has(arm)) : arm === wantArm);
    let total = 0, attempted = 0, solved = 0, unsolvedSearched = 0, coveredViaReps = 0, notAttempted = 0;
    const pathLens = [];

    // The rep's outcome under the arm scope: "solved" | "unsolved" | null (not covered).
    function repOutcome(entry) {
      const reg = entry.reg;
      if (!reg || reg.rep_idx == null || entry.dataset === REPS_DATASET) return null;
      const repEntry = ds.byIdx.get(REPS_DATASET + "|" + reg.rep_idx);
      if (!repEntry) return null;
      let anySearched = false;
      for (const it of repEntry.arms.values()) {
        if (!armInScope(it.arm)) continue;
        if (it.solved) return "solved";
        anySearched = true;
      }
      return anySearched ? "unsolved" : null;
    }

    for (const entry of ds.byIdx.values()) {
      if (wantDs !== "all" && entry.dataset !== wantDs) continue;
      if (wantSub !== "all" && entry.subset !== wantSub) continue;
      total++;
      let searched = false, won = false, best = null;
      for (const it of entry.arms.values()) {
        if (!armInScope(it.arm)) continue;
        searched = true;
        if (it.solved) {
          won = true;
          const len = itemPathLen(it);
          if (len != null && (best == null || len < best)) best = len;
        }
      }
      if (searched) {
        attempted++;
        if (won) {
          solved++;
          if (best != null) pathLens.push(best);
        } else {
          unsolvedSearched++;
        }
      } else {
        const rep = repOutcome(entry);
        if (rep === "solved") solved++;
        else if (rep === "unsolved") coveredViaReps++;
        else notAttempted++;
      }
    }
    const avg = pathLens.length ? pathLens.reduce((a, b) => a + b, 0) / pathLens.length : null;
    return {
      total: total, presentations: total, attempted: attempted, solved: solved,
      unsolvedSearched: unsolvedSearched, unsolved: unsolvedSearched,
      coveredViaReps: coveredViaReps, notAttempted: notAttempted,
      avgPathLen: avg, pathLens: pathLens,
    };
  }

  /**
   * Per-arm solved-idx set algebra over one dataset scope — the Comparison verdict's
   * numbers all come from here so none are ever hardcoded.
   *   sel = { dataset (default "1190MS"), subset ("all"), arms: [required] }
   * Returns { arms, sets: {arm -> Set(idx)}, union: Set, unique: {arm -> count solved
   * by that arm ONLY}, byK: [count solved by exactly k of the arms, k=0..arms.length
   * — byK[0] = in-scope presentations solved by none], scopeTotal }.
   */
  function armSolveSets(ds, sel) {
    sel = sel || {};
    const arms = sel.arms || [];
    const wantDs = sel.dataset || "1190MS";
    const wantSub = sel.subset || "all";
    const sets = {};
    for (const a of arms) sets[a] = new Set();
    let scopeTotal = 0, attempted = 0;
    for (const entry of ds.byIdx.values()) {
      if (entry.dataset !== wantDs) continue;
      if (wantSub !== "all" && entry.subset !== wantSub) continue;
      scopeTotal++;
      let ran = false;
      for (const a of arms) {
        const it = entry.arms.get(a);
        if (it) ran = true;
        if (it && it.solved) sets[a].add(entry.idx);
      }
      if (ran) attempted++;
    }
    const countByIdx = new Map();
    for (const a of arms) for (const v of sets[a]) countByIdx.set(v, (countByIdx.get(v) || 0) + 1);
    const union = new Set(countByIdx.keys());
    const byK = new Array(arms.length + 1).fill(0);
    // byK[0] = attempted-but-solved-by-none; never counts presentations no arm ran on
    // (a partial upload must not read never-attempted as "solved by none").
    byK[0] = attempted - union.size;
    for (const k of countByIdx.values()) byK[k]++;
    const unique = {};
    for (const a of arms) {
      unique[a] = 0;
      for (const v of sets[a]) if (countByIdx.get(v) === 1) unique[a]++;
    }
    return {
      arms: arms.slice(), sets: sets, union: union, unique: unique, byK: byK,
      scopeTotal: scopeTotal, attempted: attempted,
    };
  }

  // ---- move reconstruction --------------------------------------------------------
  // Faithful JS port of the solver's move semantics (greedy_nrel.py::get_neighbors):
  // a step replaces ONE relator by reduce( roll(r_a, i) · roll(c, j) ) where {a,b} is an
  // unordered pair (a<b, leader = a), c ∈ {r_b, r_b⁻¹}, and roll = np.roll (right shift).
  // The stored tuple (emitted_slot, i, j, c_inv) omits the partner index, but given the
  // full parent+child states we can RECOVER a valid factorization by replaying the rule —
  // reconstruction, not fabrication: it is only accepted if it reproduces the child exactly.

  /** np.roll(w, k): right-cyclic shift by k. */
  function rollWord(w, k) {
    const n = w.length;
    if (n === 0) return [];
    const kk = ((k % n) + n) % n;
    if (kk === 0) return w.slice();
    return w.slice(n - kk).concat(w.slice(0, n - kk));
  }

  function lexLessEq(a, b) { // equal-length int arrays, natural signed order
    for (let m = 0; m < a.length; m++) {
      if (a[m] !== b[m]) return a[m] < b[m];
    }
    return true;
  }

  function minimalRotation(w) {
    let best = w.slice();
    for (let k = 1; k < w.length; k++) {
      const r = rollWord(w, k);
      if (!lexLessEq(best, r)) best = r;
    }
    return best;
  }

  /** Inversion-invariant canonical form: min over rotations of w and of w⁻¹. */
  function canonicalRelator(w) {
    if (w.length === 0) return [];
    const a = minimalRotation(w);
    const b = minimalRotation(invertWord(w));
    return lexLessEq(a, b) ? a : b;
  }

  /** Solver relator order inside a state: by (length, lex-by-value). */
  function compareRelators(a, b) {
    if (a.length !== b.length) return a.length - b.length;
    for (let m = 0; m < a.length; m++) if (a[m] !== b[m]) return a[m] - b[m];
    return 0;
  }

  /**
   * The reduction as a sequence of HUMAN-VISIBLE events (this is what the animation plays):
   * free cancellations one adjacent inverse pair at a time (leftmost first — free reduction
   * is confluent, so the endpoint is the same as the solver's stack pass), then cyclic
   * end-trims exactly like reduce_relator's i<j loop. Each event snapshots the word AFTER it.
   */
  function spliceTrace(rotA, rotC) {
    const splice = rotA.concat(rotC);
    let w = splice.slice();
    const events = [];
    for (;;) {
      let k = -1;
      for (let m = 0; m + 1 < w.length; m++) {
        if (w[m] === -w[m + 1]) { k = m; break; }
      }
      if (k === -1) break;
      const letters = [w[k], w[k + 1]];
      w = w.slice(0, k).concat(w.slice(k + 2));
      events.push({ type: "free", pos: k, letters: letters, word: w.slice() });
    }
    while (w.length >= 2 && w[0] === -w[w.length - 1]) {
      const letters = [w[0], w[w.length - 1]];
      w = w.slice(1, w.length - 1);
      events.push({ type: "cyclic", letters: letters, word: w.slice() });
    }
    return { splice: splice, events: events, reduced: w };
  }

  /**
   * Recover a valid factorization of one step: which relator was the leader (A), which the
   * partner (B), whether B was inverted, and the two rotations — such that replaying
   * reduce(roll(A,i)·roll(B^±,j)) reproduces the child's new relator EXACTLY (canonical
   * compare). Uses the stored move tuple as a hint first, then falls back to a full search
   * (n=3: ≤ 2 pairs × 2 inversions × ≤24×24 rotations — sub-millisecond). Returns null when
   * nothing reproduces the child (the viewer then falls back to the plain old→new diff).
   */
  function reconstructMove(parent, child, moveTuple) {
    const d = multisetDiff(parent, child);
    if (d.removed.length !== 1 || d.added.length !== 1) return null;
    const removed = d.removed[0], added = d.added[0];
    const addedKey = relKey(added);

    // Emitted slot in the parent = the relator that disappears.
    let ci = -1;
    if (moveTuple && parent[moveTuple[0]] && relKey(parent[moveTuple[0]]) === relKey(removed)) {
      ci = moveTuple[0];
    } else {
      for (let s = 0; s < parent.length; s++) {
        if (relKey(parent[s]) === relKey(removed)) { ci = s; break; }
      }
    }
    if (ci === -1) return null;

    function attempt(other, cInv, i, j) {
      const a = Math.min(ci, other), b = Math.max(ci, other);
      const ra = parent[a];
      const cBase = parent[b];
      if (ra.length === 0 || cBase.length === 0) return null;
      const c = cInv ? invertWord(cBase) : cBase;
      if (i >= ra.length || j >= c.length) return null;
      const rotA = rollWord(ra, i), rotC = rollWord(c, j);
      if (rotA[rotA.length - 1] !== -rotC[0]) return null; // boundary must cancel
      const trace = spliceTrace(rotA, rotC);
      if (trace.reduced.length === 0) return null;
      const canon = canonicalRelator(trace.reduced);
      if (relKey(canon) !== addedKey) return null;
      return {
        ok: true,
        leaderSlot: a, partnerSlot: b, emittedSlot: ci,
        cInv: !!cInv, iRot: i, jRot: j,
        ra: ra.slice(), cBase: cBase.slice(), c: c.slice(),
        rotA: rotA, rotC: rotC,
        splice: trace.splice, events: trace.events, reduced: trace.reduced,
        canonical: canon,
        canonChanged: relKey(canon) !== relKey(trace.reduced),
      };
    }

    // 1) hinted: the stored (i, j, c_inv) with each possible partner slot
    if (moveTuple && moveTuple.length === 4) {
      const i = moveTuple[1], j = moveTuple[2], cInv = moveTuple[3];
      for (let other = 0; other < parent.length; other++) {
        if (other === ci) continue;
        const r = attempt(other, cInv, i, j);
        if (r) return r;
      }
    }
    // 2) full search
    for (let other = 0; other < parent.length; other++) {
      if (other === ci) continue;
      const a = Math.min(ci, other), b = Math.max(ci, other);
      const la = parent[a].length;
      for (let cInv = 0; cInv < 2; cInv++) {
        const lc = parent[b].length;
        for (let i = 0; i < la; i++) {
          for (let j = 0; j < lc; j++) {
            const r = attempt(other, cInv, i, j);
            if (r) return r;
          }
        }
      }
    }
    return null;
  }

  // ---- per-solution step model (the thing the player renders) -------------------
  function describeMoveTuple(m) {
    if (!m) return null;
    const [slot, raRot, cRot, cInv] = m;
    return "emitted slot " + slot + " · ra rot " + raRot + " · c rot " + cRot +
      " · c " + (cInv ? "inverted" : "as-is");
  }

  /**
   * Turn a PATH record into a render-ready structure: the stabilization framing (generic
   * z=w) + one Step per stored state. Each non-initial Step carries the multiset diff
   * (fromWord -> toWord) and the raw move tuple. This is the ground truth the player shows.
   */
  function buildSteps(rec) {
    const states = rec.states.map((st) => st.map((r) => r.slice()));
    const moves = rec.moves || [];
    const zGen = rec.n_gen || 3;
    const gWord = decodeZWord(states[0], zGen);
    const arm = rec.arm;
    const armSym = armSymbol(arm);
    const gStr = gWord ? wordToStr(gWord) : "?";
    const isNamedArm = arm === "r1" || arm === "r2";
    const stabilization = {
      generator: letter(zGen), // 'z'
      arm: arm,
      armSymbol: armSym,
      word: gWord,             // decoded defining word w (array), generic
      wordStr: gStr,
      // e.g. "z = r₁"  or  "z = xy"; for r1/r2 the actual word is in `wordStr`.
      text: letter(zGen) + " = " + (isNamedArm ? armSym : gStr),
      textFull: isNamedArm ? letter(zGen) + " = " + armSym + " = " + gStr
        : letter(zGen) + " = " + gStr,
    };

    // Stable slots: keep each relator in a FIXED row across steps. At step 0 the slot order
    // IS states[0]'s order; thereafter the ADDED relator takes the REMOVED relator's slot and
    // every other relator keeps its row — so unchanged relators never visually reorder (the
    // canonical `state` still gets sorted every step, but `slots` does not). `slotWords[s]` is
    // the word currently in slot s; it threads across the map (states.map runs in order).
    let slotWords = states[0].map((r) => r.slice());
    function slotOf(words, target) { // first slot whose content equals target
      const tk = relKey(target);
      for (let s = 0; s < words.length; s++) if (relKey(words[s]) === tk) return s;
      return -1;
    }

    const steps = states.map((st, t) => {
      const relatorStrings = st.map(wordToStr);
      const totalLen = stateTotalLen(st);
      let change = null, family, summary;
      let changedSlot = -1;
      if (t === 0) {
        family = "stabilization";
        summary = "Initial stabilized presentation (" + stabilization.text + ")";
      } else {
        const d = multisetDiff(states[t - 1], st);
        const fromStr = d.removed.map(wordToStr);
        const toStr = d.added.map(wordToStr);
        change = {
          removed: d.removed, added: d.added,
          fromWord: d.removed[0] || null, toWord: d.added[0] || null,
          fromStr: fromStr, toStr: toStr,
          moveTuple: moves[t] || null,
          moveTupleText: describeMoveTuple(moves[t]),
          movedSlotParent: moves[t] ? moves[t][0] : null,
          wellFormed: d.removed.length === 1 && d.added.length === 1,
          // Recovered factorization (leader/partner/rotations + cancellation trace) —
          // null when nothing replays to the child; the viewer then shows plain old→new.
          recon: reconstructMove(states[t - 1], st, moves[t] || null),
        };
        family = "substitution";
        summary = "Substitution supermove: " + (fromStr.join(", ") || "—") +
          " → " + (toStr.join(", ") || "—");

        // Thread the slots: the added relator lands in the removed relator's slot.
        const parentSlots = slotWords; // stable order of the parent (states[t-1])
        if (change.wellFormed) {
          const sRm = slotOf(parentSlots, change.removed[0]);
          if (sRm !== -1) {
            const next = parentSlots.map((r) => r.slice());
            next[sRm] = change.added[0].slice();
            changedSlot = sRm;
            slotWords = next;
            // Map the reconstruction's operand indices (into the canonical parent state) onto
            // stable rows: `a` = the row that changes (= emitted), `b` = the partner that stays.
            const recon = change.recon;
            if (recon && recon.ok) {
              const otherCanon = recon.emittedSlot === recon.leaderSlot ? recon.partnerSlot : recon.leaderSlot;
              change.slots = { a: changedSlot, b: slotOf(parentSlots, states[t - 1][otherCanon]) };
            }
          } else {
            slotWords = st.map((r) => r.slice()); // degenerate: fall back to canonical order
          }
        } else {
          slotWords = st.map((r) => r.slice());
        }
      }

      const slots = slotWords.map((w, s) => ({
        word: w, str: wordToStr(w),
        isChanged: s === changedSlot,
        fromStr: s === changedSlot && change ? (change.fromStr[0] || null) : null,
        toStr: s === changedSlot && change ? (change.toStr[0] || null) : null,
      }));

      return {
        index: t, isInitial: t === 0, isFinal: t === states.length - 1,
        state: st, relatorStrings: relatorStrings, totalLen: totalLen,
        slots: slots, changedSlot: changedSlot,
        change: change, family: family, summary: summary,
      };
    });

    return {
      arm: arm, armSymbol: armSym, dataset: rec.dataset, idx: rec.idx, name: rec.name || null,
      nGen: zGen, pathLen: rec.path_len != null ? rec.path_len : states.length - 1,
      stabilization: stabilization, steps: steps,
      finalTrivial: isTrivialState(states[states.length - 1]),
      pathVerified: !!rec.path_verified,
    };
  }

  // ---- validation (used by the test harness; also safe at runtime) --------------
  function validatePath(rec) {
    const errors = [];
    const states = rec.states;
    if (!Array.isArray(states) || states.length === 0) return { ok: false, errors: ["no states"] };
    for (let t = 1; t < states.length; t++) {
      const d = multisetDiff(states[t - 1], states[t]);
      if (d.removed.length !== 1 || d.added.length !== 1) {
        errors.push("step " + t + ": diff not 1-in/1-out (removed " + d.removed.length +
          ", added " + d.added.length + ")");
      }
    }
    if (!isTrivialState(states[states.length - 1])) errors.push("final state not trivial (n=3 => 3 unit relators)");
    if (rec.path_len != null && rec.path_len !== states.length - 1) {
      errors.push("path_len " + rec.path_len + " != states-1 " + (states.length - 1));
    }
    if (decodeZWord(states[0], rec.n_gen || 3) == null) errors.push("could not decode z-word from state[0]");
    return { ok: errors.length === 0, errors: errors };
  }

  // ---- aggregation helpers (dashboard consumes these) ---------------------------
  function countBy(items, keyFn) {
    const m = new Map();
    for (const it of items) { const k = keyFn(it); m.set(k, (m.get(k) || 0) + 1); }
    return m;
  }
  /**
   * Histogram of numeric values. Returns [{x0,x1,count}].
   * Default: fixed-width bins (binSize, or range/12). With opts.log: 1-2-5 log-scale
   * bins spanning the data's decades — the right shape for the heavily right-skewed
   * nodes-explored / wall-time distributions, where linear bins collapse ~all mass
   * into the first bar. Values ≤ 0 fold into the first bin.
   */
  function histogram(values, binSize, opts) {
    const vals = values.filter((v) => v != null && !isNaN(v));
    if (vals.length === 0) return [];
    if (opts && opts.log) return logHistogram(vals);
    const min = Math.min.apply(null, vals), max = Math.max.apply(null, vals);
    const bs = binSize || Math.max(1, Math.ceil((max - min) / 12));
    const start = Math.floor(min / bs) * bs;
    const bins = [];
    for (let x = start; x <= max; x += bs) bins.push({ x0: x, x1: x + bs, count: 0 });
    if (bins.length === 0) bins.push({ x0: start, x1: start + bs, count: 0 });
    for (const v of vals) {
      let i = Math.floor((v - start) / bs);
      if (i < 0) i = 0; if (i >= bins.length) i = bins.length - 1;
      bins[i].count++;
    }
    return bins;
  }

  function logHistogram(vals) {
    const pos = vals.filter((v) => v > 0);
    // no positive values: nothing to span decades with — one degenerate bin
    if (!pos.length) return [{ x0: 0, x1: 1, count: vals.length }];
    const min = Math.min.apply(null, pos), max = Math.max.apply(null, pos);
    // 1-2-5 edges from the decade at/below min until one edge exceeds max
    const edges = [];
    let b = Math.pow(10, Math.floor(Math.log10(min)));
    for (let guard = 0; guard < 40 && (edges.length === 0 || edges[edges.length - 1] <= max); guard++) {
      for (const m of [1, 2, 5]) {
        const e = m * b;
        if (edges.length === 0 || e > edges[edges.length - 1]) {
          edges.push(e);
          if (e > max) break;
        }
      }
      b *= 10;
    }
    if (edges.length < 2) edges.push(edges[0] * 2);
    const bins = [];
    for (let i = 0; i + 1 < edges.length; i++) bins.push({ x0: edges[i], x1: edges[i + 1], count: 0 });
    for (const v of vals) {
      let idx = 0; // ≤ first edge (incl. zeros) folds into the first bin
      for (let i = bins.length - 1; i >= 0; i--) {
        if (v >= bins[i].x0) { idx = i; break; }
      }
      bins[idx].count++;
    }
    while (bins.length > 1 && bins[0].count === 0) bins.shift(); // trim empty lead-in decades
    return bins;
  }

  const ACXData = {
    letter: letter, wordToStr: wordToStr, wordToTokens: wordToTokens,
    invertWord: invertWord, freeReduce: freeReduce, cyclicReduce: cyclicReduce,
    decodeZWord: decodeZWord, relKey: relKey, stateTotalLen: stateTotalLen,
    isTrivialState: isTrivialState, multisetDiff: multisetDiff,
    classifyRecord: classifyRecord, mergeKey: mergeKey, armSymbol: armSymbol,
    ARM_ORDER: ARM_ORDER, armSort: armSort, median: median, esc: esc,
    parseJsonl: parseJsonl, buildDataset: buildDataset, buildSteps: buildSteps,
    describeMoveTuple: describeMoveTuple, validatePath: validatePath,
    countBy: countBy, histogram: histogram,
    SUB: SUB,
    // provenance + non-redundant stats
    SUBSET_LABELS: SUBSET_LABELS, subsetLabel: subsetLabel, subsetOfEntry: subsetOfEntry,
    DATASET_LABELS: DATASET_LABELS, datasetLabel: datasetLabel,
    itemPathLen: itemPathLen, groupStats: groupStats, armSolveSets: armSolveSets,
    // move reconstruction
    rollWord: rollWord, minimalRotation: minimalRotation, canonicalRelator: canonicalRelator,
    compareRelators: compareRelators, spliceTrace: spliceTrace, reconstructMove: reconstructMove,
  };

  global.ACXData = ACXData;
  if (typeof module !== "undefined" && module.exports) module.exports = ACXData;
})(typeof window !== "undefined" ? window : globalThis);
