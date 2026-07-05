/*
 * test_data.js — my own (non-independent) suite for the AC-SolverX website data layer.
 * Node-run against the real bundled sample data. Exits non-zero on any failure.
 *   node website/tools/test_data.js     (from repo root)
 *   node test_data.js                    (from website/tools)
 * A separate, independent black-box suite lives in test_data_independent.js.
 */
"use strict";
const fs = require("fs");
const path = require("path");

const HERE = __dirname;
const WEB = path.resolve(HERE, "..");
const SAMPLES = path.join(WEB, "sample-data");
const D = require(path.join(WEB, "js", "data.js"));

let pass = 0, fail = 0;
function ok(cond, msg) { if (cond) { pass++; } else { fail++; console.error("  FAIL: " + msg); } }
function eq(a, b, msg) { ok(a === b, msg + " (got " + a + ", want " + b + ")"); }

// ---- load ----
const manifest = JSON.parse(fs.readFileSync(path.join(SAMPLES, "manifest.json"), "utf8"));
let records = [];
for (const f of manifest.files) records = records.concat(D.parseJsonl(fs.readFileSync(path.join(SAMPLES, f), "utf8")));
const ds = D.buildDataset(records);
const grid = JSON.parse(fs.readFileSync(path.join(SAMPLES, "reps_grid.json"), "utf8"));

// ---- 1. dataset shape ----
console.log("[1] dataset shape");
ok(ds.datasets.indexOf("1190MS") !== -1 && ds.datasets.indexOf("ms_reps_unsolved") !== -1, "both datasets present");
// The pruned bundle keeps only the real arms: the four z=w words + the 2-gen baseline.
eq(ds.armsByDataset["1190MS"], 5, "1190MS has 5 arms");
eq(ds.armsByDataset["ms_reps_unsolved"], 4, "reps has 4 arms");
ok(ds.armSetsByDataset && ds.armSetsByDataset["ms_reps_unsolved"] instanceof Set &&
   ["r1", "r2", "x", "y"].every((a) => ds.armSetsByDataset["ms_reps_unsolved"].has(a)),
   "armSetsByDataset exposes the reps arm set");
let pres1190 = 0, presReps = 0;
for (const e of ds.byIdx.values()) { if (e.dataset === "1190MS") pres1190++; if (e.dataset === "ms_reps_unsolved") presReps++; }
eq(pres1190, 1190, "1190 MS presentations");
eq(presReps, 261, "261 rep presentations");

// ---- 2. groupStats v2: presentation-first buckets with rep coverage ----
console.log("[2] groupStats presentation counts");
const g = (sel) => D.groupStats(ds, sel);
// Oracle table (dataset · subset · arm → total/solved/unsolvedSearched/coveredViaReps/notAttempted).
// 544 = the 550 grid-nontrivial cells minus the 6 boundary idx 634-639 (attempted directly);
// 6 = the grid-trivial hard idx {668, 698, 717, 955, 1046, 1132} with no rep link.
const ORACLE = [
  ["1190MS", "all", "all", 1190, 634, 6, 544, 6],
  ["1190MS", "baseline", "all", 1190, 634, 6, 0, 550],
  ["1190MS", "r1", "all", 1190, 619, 21, 544, 6],
  ["1190MS", "r2", "all", 1190, 602, 38, 544, 6],
  ["1190MS", "x", "all", 1190, 540, 100, 544, 6],
  ["1190MS", "y", "all", 1190, 523, 117, 544, 6],
  ["1190MS", "all", "original", 640, 634, 6, 0, 0],
  ["1190MS", "r1", "original", 640, 619, 21, 0, 0],
  ["1190MS", "all", "hard", 550, 0, 0, 544, 6],
  ["1190MS", "r1", "hard", 550, 0, 0, 544, 6],
  ["ms_reps_unsolved", "all", "all", 261, 0, 261, 0, 0],
  ["ms_reps_unsolved", "r1", "all", 261, 0, 261, 0, 0],
  ["all", "all", "all", 1451, 634, 267, 544, 6],
];
for (const [dsName, arm, subset, total, solved, uns, rep, na] of ORACLE) {
  const s = g({ dataset: dsName, arm: arm, subset: subset });
  const tag = dsName + " " + subset + "/" + arm + " ";
  eq(s.total, total, tag + "total");
  eq(s.solved, solved, tag + "solved");
  eq(s.unsolvedSearched, uns, tag + "unsolvedSearched");
  eq(s.coveredViaReps, rep, tag + "coveredViaReps");
  eq(s.notAttempted, na, tag + "notAttempted");
}
eq(g({ dataset: "1190MS", arm: "all", subset: "all" }).unsolved,
   g({ dataset: "1190MS", arm: "all", subset: "all" }).unsolvedSearched, "unsolved aliases unsolvedSearched");
// excludeArms: the Solutions view's "All z-words" must not count baseline-only solves —
// the union over r1/r2/x/y solves 620 of the 640 (baseline alone solves 634).
const gz = g({ dataset: "1190MS", arm: "all", subset: "all", excludeArms: new Set(["baseline"]) });
eq(gz.total, 1190, "z-only all total");
eq(gz.solved, 620, "z-only all solved (union of the four words)");
eq(gz.unsolvedSearched, 20, "z-only all unsolvedSearched");
eq(gz.coveredViaReps, 544, "z-only coveredViaReps");
eq(gz.notAttempted, 6, "z-only notAttempted");
eq(gz.solved + gz.unsolvedSearched + gz.coveredViaReps + gz.notAttempted, gz.total, "z-only partition sums");
eq(g({ dataset: "1190MS", arm: "all", subset: "all", excludeArms: ["baseline"] }).solved, 620,
   "excludeArms accepts an array too");
// invariant: the four buckets partition total, and total == presentations, for many selections
for (const sel of [
  { dataset: "1190MS", arm: "all", subset: "all" }, { dataset: "1190MS", arm: "r2", subset: "all" },
  { dataset: "1190MS", arm: "baseline", subset: "all" }, { dataset: "1190MS", arm: "y", subset: "hard" },
  { dataset: "ms_reps_unsolved", arm: "all", subset: "all" }, { dataset: "all", arm: "all", subset: "all" },
]) {
  const s = g(sel);
  eq(s.solved + s.unsolvedSearched + s.coveredViaReps + s.notAttempted, s.total,
     "partition sums to total " + JSON.stringify(sel));
  eq(s.total, s.presentations, "total==presentations " + JSON.stringify(sel));
}
// per-arm totals stay presentation counts
for (const arm of ds.arms) {
  const s = g({ dataset: "all", arm: arm, subset: "all" });
  eq(s.total, s.presentations, "single-arm " + arm + " total==presentations");
}

// ---- 2b. shared util exports (P2: single source for every view) ----
console.log("[2b] shared util exports");
ok(Array.isArray(D.ARM_ORDER) && D.ARM_ORDER.length === 5, "ARM_ORDER has the 5 real arms");
eq(D.ARM_ORDER[0], "baseline", "ARM_ORDER leads with baseline");
eq(D.ARM_ORDER.join(","), "baseline,r1,r2,x,y", "ARM_ORDER exact");
eq(typeof D.median, "function", "median exported");
eq(D.median([3, 1, 2]), 2, "median odd");
eq(D.median([4, 1, 2, 3]), 2.5, "median even");
eq(D.median([null, NaN, 7]), 7, "median drops null/NaN");
eq(D.median([]), null, "median of empty is null");
eq(typeof D.armSort, "function", "armSort exported");
eq(["y", "baseline", "r1"].sort(D.armSort).join(","), "baseline,r1,y", "armSort orders by ARM_ORDER");
eq(ds.arms.join(","), "baseline,r1,r2,x,y", "buildDataset arms use the shared order");
// counts is deliberately minimal — solved/unsolved item-row counts were removed
// (attractive nuisance: they read up to 5x the presentation truth).
eq(ds.counts.solved, undefined, "counts.solved removed");
eq(ds.counts.presentations, undefined, "counts.presentations removed");
ok(typeof ds.counts.total === "number" && typeof ds.counts.withPath === "number",
   "counts keeps total + withPath");

// ---- 2c. log-scale histogram bins (P5) ----
console.log("[2c] histogram {log:true}");
{
  const vals = [0, 1, 3, 9, 40, 700, 480000];
  const bins = D.histogram(vals, null, { log: true });
  ok(bins.length > 5, "log bins span the decades (" + bins.length + " bins)");
  let sum = 0, increasing = true;
  for (let i = 0; i < bins.length; i++) {
    sum += bins[i].count;
    if (bins[i].x1 <= bins[i].x0) increasing = false;
    if (i > 0 && bins[i].x0 !== bins[i - 1].x1) increasing = false; // contiguous
  }
  eq(sum, vals.length, "log bins conserve the count");
  ok(increasing, "log bin edges strictly increase and are contiguous");
  ok(bins[bins.length - 1].x1 > 480000, "last edge exceeds the max value");
  // 0 folds into the first bin together with 1 (first bin is [1,2))
  eq(bins[0].x0, 1, "first edge at the decade of the smallest positive value");
  eq(bins[0].count, 2, "zero folds into the first bin (0 and 1)");
  // sub-1 values get sub-1 decades (wall-time shape)
  const tbins = D.histogram([0.0009, 0.002, 0.5, 12], null, { log: true });
  ok(Math.abs(tbins[0].x0 - 0.0001) < 1e-12 || tbins[0].x0 <= 0.0009,
     "sub-1 values get a sub-1 first edge (" + tbins[0].x0 + ")");
  eq(tbins.reduce((a, b) => a + b.count, 0), 4, "time-shaped log bins conserve the count");
  // linear path unchanged
  const lin = D.histogram([1, 2, 3], 1);
  eq(lin.length, 3, "linear bins unchanged by the log extension");
}

// ---- 2d. armSolveSets (drives the Comparison verdict) ----
console.log("[2d] armSolveSets");
{
  const Z = D.armSolveSets(ds, { dataset: "1190MS", subset: "original", arms: ["r1", "r2", "x", "y"] });
  eq(Z.scopeTotal, 640, "verdict scope is the original 640");
  eq(Z.union.size, 620, "union of the four z-words solves 620");
  eq(Z.sets.r1.size, 619, "r1 solves 619");
  eq(Z.sets.r2.size, 602, "r2 solves 602");
  eq(Z.sets.x.size, 540, "x solves 540");
  eq(Z.sets.y.size, 523, "y solves 523");
  eq(Z.byK[0], 20, "20 solved by none of the four words");
  eq(Z.byK.reduce((a, b) => a + b, 0), 640, "byK partitions the scope");
  eq(Z.byK.slice(1).reduce((a, b) => a + b, 0), Z.union.size, "byK k>=1 sums to the union");
  let uniqueSum = 0;
  for (const a of Z.arms) uniqueSum += Z.unique[a];
  eq(uniqueSum, Z.byK[1], "per-arm unique counts sum to byK[1]");
  const B = D.armSolveSets(ds, { dataset: "1190MS", subset: "original", arms: ["baseline"] });
  eq(B.sets.baseline.size, 634, "baseline solves 634");
  let zOnly = 0, baseOnly = 0;
  Z.union.forEach((v) => { if (!B.sets.baseline.has(v)) zOnly++; });
  B.sets.baseline.forEach((v) => { if (!Z.union.has(v)) baseOnly++; });
  eq(Z.union.size - (620 - zOnly), zOnly, "set-algebra self-consistency");
  eq((620 - zOnly) + baseOnly, 634, "baseline = shared + baseline-only");
}

// ---- 2e. path-only records are gated by validatePath (P9) ----
console.log("[2e] path-only records gated by validatePath");
{
  const good = { dataset: "T", idx: 0, arm: "r1", budget_nodes: 1, n_gen: 3,
    states: [[[1], [2], [3]]], moves: [], path_len: 0 };
  const bad = { dataset: "T", idx: 1, arm: "r1", budget_nodes: 1, n_gen: 3,
    states: [[[1], [2], [3, 3]]], moves: [], path_len: 0 }; // final state NOT trivial
  // a 2-generator (baseline-style) path has no z-relator — must still count when
  // structurally valid (trivial final state), and not when truncated
  const good2g = { dataset: "T", idx: 2, arm: "baseline", budget_nodes: 1, n_gen: 2,
    states: [[[1], [2]]], moves: [], path_len: 0 };
  const bad2g = { dataset: "T", idx: 3, arm: "baseline", budget_nodes: 1, n_gen: 2,
    states: [[[1, 2], [2]]], moves: [], path_len: 0 };
  const tds = D.buildDataset([good, bad, good2g, bad2g]);
  eq(tds.byKey.get("T|0|r1|1").solved, true, "valid path-only record counts as solved");
  eq(tds.byKey.get("T|1|r1|1").solved, false, "invalid path-only record must NOT count as solved");
  eq(tds.byKey.get("T|2|baseline|1").solved, true, "valid 2-gen path-only record counts as solved");
  eq(tds.byKey.get("T|3|baseline|1").solved, false, "non-trivial 2-gen path-only record must NOT count");
}

// ---- 3. stable-slot invariants over every stored path ----
console.log("[3] stable-slot invariants (all bundled paths)");
let paths = 0, stepChecks = 0, viol = 0;
const wkey = (w) => w.join(",");
const mkey = (arr) => arr.map(wkey).sort().join("|");
for (const it of ds.items) {
  if (!it.path) continue;
  paths++;
  const sol = D.buildSteps(it.path);
  const n = sol.nGen;
  for (let t = 0; t < sol.steps.length; t++) {
    const step = sol.steps[t];
    stepChecks++;
    if (step.slots.length !== n) { viol++; continue; }
    if (mkey(step.slots.map((s) => s.word)) !== mkey(step.state)) { viol++; continue; } // slots are a permutation of state
    if (t > 0 && step.change && step.change.wellFormed) {
      const prev = sol.steps[t - 1].slots;
      let diff = 0, at = -1;
      for (let s = 0; s < n; s++) if (wkey(prev[s].word) !== wkey(step.slots[s].word)) { diff++; at = s; }
      if (diff !== 1) { viol++; continue; }        // exactly one row changes
      if (at !== step.changedSlot) { viol++; continue; }
      if (!step.slots[at].isChanged) { viol++; continue; }
      // the changed slot's new word equals the diff's `added`, old equals `removed`
      if (wkey(step.slots[at].word) !== wkey(step.change.added[0])) { viol++; continue; }
      if (wkey(prev[at].word) !== wkey(step.change.removed[0])) { viol++; continue; }
    }
  }
}
ok(paths > 500, "checked many paths (" + paths + ")");
eq(viol, 0, "zero stable-slot violations over " + stepChecks + " step-checks");

// ---- 4. change.slots map (drives the in-place animation) ----
console.log("[4] change.slots operand map");
let reconSteps = 0, slotViol = 0;
for (const it of ds.items) {
  if (!it.path) continue;
  const sol = D.buildSteps(it.path);
  for (const step of sol.steps) {
    const c = step.change;
    if (!c || !c.recon || !c.recon.ok) continue;
    reconSteps++;
    if (!c.slots) { slotViol++; continue; }
    if (c.slots.a !== step.changedSlot) { slotViol++; continue; }   // A is the changing row
    if (c.slots.b < 0 || c.slots.b >= step.slots.length) { slotViol++; continue; }
    if (c.slots.a === c.slots.b) { slotViol++; continue; }          // partner distinct from A
  }
}
ok(reconSteps > 500, "many recon steps (" + reconSteps + ")");
eq(slotViol, 0, "zero change.slots violations");

// ---- 5. reps_grid.json integrity ----
console.log("[5] reps_grid.json integrity");
eq(grid.cells.length, 1190, "1190 grid cells");
eq(grid.words.length, 170, "170 words");
ok(grid.nvals.join(",") === "1,2,3,4,5,6,7", "nvals 1..7");
const triv = grid.cells.filter((c) => c.status === "trivial");
const rep = grid.cells.filter((c) => c.status !== "trivial");
eq(triv.length, 640, "640 trivial cells");
eq(rep.length, 550, "550 rep cells");
eq(new Set(rep.map((c) => c.rep_idx)).size, 261, "261 distinct rep_idx");
ok(grid.cells.every((c) => Number.isInteger(c.ms_idx) && c.ms_idx >= 0 && c.ms_idx < 1190), "every cell has a valid ms_idx");
ok(rep.every((c) => Number.isInteger(c.rep_idx) && c.rep_idx >= 0 && c.rep_idx < 261), "every rep cell has a valid rep_idx");
ok(new Set(grid.cells.map((c) => c.ms_idx)).size === 1190, "ms_idx is a bijection onto 0..1189");
// every rep cell's target presentation exists with attempted arms
ok(rep.every((c) => { const e = ds.byIdx.get("ms_reps_unsolved|" + c.rep_idx); return e && e.arms.size === 4; }),
  "every rep cell points at a rep with 4 attempted arms");
// every trivial cell's 1190MS presentation exists
ok(triv.every((c) => ds.byIdx.has("1190MS|" + c.ms_idx)), "every trivial cell points at an existing 1190MS idx");

// ---- 6. reps registry carries relators + name + nw_cells ----
console.log("[6] reps registry payload");
let regChecks = 0;
for (const e of ds.byIdx.values()) {
  if (e.dataset !== "ms_reps_unsolved") continue;
  regChecks++;
  ok(e.reg && Array.isArray(e.reg.relators) && e.reg.relators.length === 2, "rep " + e.idx + " has 2 relators");
  ok(e.reg.name && /^\d+_\d+$/.test(e.reg.name), "rep " + e.idx + " has a <len>_<id> name");
  ok(Array.isArray(e.reg.nw_cells) && e.reg.nw_cells.length >= 1, "rep " + e.idx + " has >=1 nw_cells");
}
eq(regChecks, 261, "261 reps registered");
// nw_cells across all reps == the 550 rep grid cells
let totalNwCells = 0;
for (const e of ds.byIdx.values()) if (e.dataset === "ms_reps_unsolved") totalNwCells += e.reg.nw_cells.length;
eq(totalNwCells, 550, "sum of nw_cells == 550 rep grid cells");

// ---- done ----
console.log("\n" + (fail === 0 ? "ALL PASS" : "FAILURES") + ": " + pass + " passed, " + fail + " failed.");
process.exit(fail === 0 ? 0 : 1);
