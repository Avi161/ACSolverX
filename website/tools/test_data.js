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
// 9 arms since the 2-gen baseline was added (r1,r2,x,y,g,xY,yx,Xy + baseline).
eq(ds.armsByDataset["1190MS"], 9, "1190MS has 9 arms");
eq(ds.armsByDataset["ms_reps_unsolved"], 4, "reps has 4 arms");
let pres1190 = 0, presReps = 0;
for (const e of ds.byIdx.values()) { if (e.dataset === "1190MS") pres1190++; if (e.dataset === "ms_reps_unsolved") presReps++; }
eq(pres1190, 1190, "1190 MS presentations");
eq(presReps, 261, "261 rep presentations");

// ---- 2. groupStats cell-count targets ----
console.log("[2] groupStats cell counts");
const g = (sel) => D.groupStats(ds, sel);
eq(g({ dataset: "1190MS", arm: "all", subset: "all" }).total, 10710, "1190MS all/all total");   // 1190 × 9 arms
eq(g({ dataset: "1190MS", arm: "all", subset: "all" }).notAttempted, 5056, "1190MS all/all notAttempted");   // 10710 − attempted(640×7 + r1 595 + r2 579)
eq(g({ dataset: "1190MS", arm: "r1", subset: "all" }).total, 1190, "1190MS r1 total == presentations");
eq(g({ dataset: "1190MS", arm: "all", subset: "original" }).total, 5760, "1190MS original all total");   // 640 × 9 arms
const hard = g({ dataset: "1190MS", arm: "all", subset: "hard" });
eq(hard.total, 4950, "1190MS hard all total");   // 550 × 9 arms
eq(hard.attempted, 0, "1190MS hard has no attempts");
eq(g({ dataset: "ms_reps_unsolved", arm: "all", subset: "all" }).total, 1044, "reps all/all total");
eq(g({ dataset: "ms_reps_unsolved", arm: "all", subset: "all" }).solved, 0, "reps solved == 0");
eq(g({ dataset: "ms_reps_unsolved", arm: "x", subset: "all" }).total, 261, "reps x total == presentations");
eq(g({ dataset: "all", arm: "all", subset: "all" }).total, 11754, "ALL all/all total");   // 1190MS 10710 + reps 1044
// invariant: solved + unsolved + notAttempted == total, for many selections
for (const sel of [
  { dataset: "1190MS", arm: "all", subset: "all" }, { dataset: "1190MS", arm: "r2", subset: "all" },
  { dataset: "ms_reps_unsolved", arm: "all", subset: "all" }, { dataset: "all", arm: "all", subset: "all" },
]) { const s = g(sel); eq(s.solved + s.unsolved + s.notAttempted, s.total, "partition sums to total " + JSON.stringify(sel)); }
// single-arm cells == presentation counts (per arm)
for (const arm of ds.arms) {
  const s = g({ dataset: "all", arm: arm, subset: "all" });
  eq(s.total, s.presentations, "single-arm " + arm + " total==presentations");
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
