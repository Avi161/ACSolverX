#!/usr/bin/env node
/*
 * test_data_independent.js — INDEPENDENT black-box test suite for the AC-SolverX
 * website data layer (website/js/data.js, exported as ACXData).
 *
 * Adversarial-independence rules followed (see task spec):
 *  - Only the PUBLIC API of data.js is called (D.parseJsonl, D.buildDataset,
 *    D.groupStats, D.buildSteps). The bodies of buildSteps/groupStats/reconstructMove/
 *    buildDataset/slot-signature logic were never read.
 *  - Every "expected" value below is re-derived from the raw files under
 *    website/sample-data/ and data/ms_unsolved_reps/, using math given in the task
 *    spec (Miller-Schupp relator formula, letter<->int map, AC-base-equality),
 *    re-implemented from scratch in this file (own JSONL/CSV parsing, own word
 *    algebra, own canonicalisation, own multiset-diff) — never by calling into or
 *    copying data.js's own computation.
 *
 * Run: node website/tools/test_data_independent.js   (from repo root, no deps)
 * Exits 1 on any failed assertion.
 */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const D = require(path.join(ROOT, "website", "js", "data.js"));

const SAMPLE_DIR = path.join(ROOT, "website", "sample-data");
const RAW_DIR = path.join(ROOT, "data", "ms_unsolved_reps");

// ---------------------------------------------------------------------------
// tiny test harness
// ---------------------------------------------------------------------------
let passCount = 0;
let failCount = 0;
const failures = [];
let currentSection = "";

function section(name) {
  currentSection = name;
  console.log("\n=== " + name + " ===");
}

function check(cond, label) {
  if (cond) {
    passCount++;
  } else {
    failCount++;
    const msg = "[" + currentSection + "] " + label;
    failures.push(msg);
    console.error("  FAIL: " + label);
  }
}

function checkEqual(actual, expected, label) {
  const ok = deepEqual(actual, expected);
  check(
    ok,
    label + "  (expected=" + JSON.stringify(expected) + ", actual=" + JSON.stringify(actual) + ")"
  );
}

function deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) if (!deepEqual(a[i], b[i])) return false;
    return true;
  }
  if (a && b && typeof a === "object") {
    const ka = Object.keys(a),
      kb = Object.keys(b);
    if (ka.length !== kb.length) return false;
    for (const k of ka) if (!deepEqual(a[k], b[k])) return false;
    return true;
  }
  return false;
}

// ---------------------------------------------------------------------------
// OWN raw-file parsers — independent of D.parseJsonl. Trivial by design: a
// bug in JSON.parse is not what we're hunting for, and staying off the SUT's
// own parser keeps this path fully independent.
// ---------------------------------------------------------------------------
function readOwnJsonl(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  const out = [];
  for (const raw of text.split("\n")) {
    const line = raw.replace(/\r$/, "").trim();
    if (!line) continue;
    out.push(JSON.parse(line));
  }
  return out;
}

function readOwnCsv(file) {
  const text = fs.readFileSync(file, "utf8").replace(/\r\n/g, "\n").trim();
  return text.split("\n").map((line) => line.split(","));
}

// ---------------------------------------------------------------------------
// OWN word algebra / canonicalisation — re-implemented from the task spec's
// math, NOT from data.js's canonicalRelator/minimalRotation/compareRelators
// (those were never read).
//   Letter -> int: x=1, X=-1, y=2, Y=-2  (task spec).
//   Two relators are AC-base-equal iff one is a cyclic rotation of the other,
//   or of the other's inverse. Two presentations are AC-base-equal iff their
//   relator-pairs coincide as an unordered pair of such classes.
// ---------------------------------------------------------------------------
const LETTER_TO_INT = { x: 1, X: -1, y: 2, Y: -2 };

function toIntsOwn(word) {
  const out = [];
  for (const ch of word) {
    if (!(ch in LETTER_TO_INT)) throw new Error("toIntsOwn: unknown letter " + ch);
    out.push(LETTER_TO_INT[ch]);
  }
  return out;
}

function invertOwn(w) {
  const out = [];
  for (let i = w.length - 1; i >= 0; i--) out.push(-w[i]);
  return out;
}

function rotationsOwn(w) {
  const out = [];
  for (let i = 0; i < w.length; i++) out.push(w.slice(i).concat(w.slice(0, i)));
  return out;
}

function arrLess(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    if (a[i] !== b[i]) return a[i] < b[i];
  }
  return a.length < b.length;
}

function keyOfWord(arr) {
  return arr.join(",");
}

/** Minimal element (by plain lexicographic order) among all rotations of w and of invert(w). */
function relatorCanonKeyOwn(rel) {
  let best = null;
  for (const base of [rel, invertOwn(rel)]) {
    for (const rot of rotationsOwn(base)) {
      if (best === null || arrLess(rot, best)) best = rot;
    }
  }
  return keyOfWord(best);
}

/** Presentation key invariant under: rotating/inverting either relator, and swapping the two relators. */
function presentationKeyOwn(r1, r2) {
  const k1 = relatorCanonKeyOwn(r1);
  const k2 = relatorCanonKeyOwn(r2);
  return k1 <= k2 ? k1 + "||" + k2 : k2 + "||" + k1;
}

/** Miller-Schupp MS(n,w): r1 = X y^n x Y^(n+1), r2 = X.w (task spec formula). */
function msRelatorsOwn(n, w) {
  const r1 = [-1].concat(new Array(n).fill(2), [1], new Array(n + 1).fill(-2));
  const r2 = [-1].concat(toIntsOwn(w));
  return [r1, r2];
}

/** Multiset difference of two states (arrays of relators), own implementation for buildSteps checks. */
function multisetDiffOwn(prev, curr) {
  const cnt = new Map();
  const rep = new Map();
  for (const r of prev) {
    const k = keyOfWord(r);
    cnt.set(k, (cnt.get(k) || 0) + 1);
    rep.set(k, r);
  }
  for (const r of curr) {
    const k = keyOfWord(r);
    cnt.set(k, (cnt.get(k) || 0) - 1);
    rep.set(k, r);
  }
  const removed = [],
    added = [];
  for (const [k, c] of cnt) {
    for (let i = 0; i < c; i++) removed.push(rep.get(k));
    for (let i = 0; i < -c; i++) added.push(rep.get(k));
  }
  return { removed, added };
}

function multisetOfWords(words) {
  const m = new Map();
  for (const w of words) {
    const k = keyOfWord(w);
    m.set(k, (m.get(k) || 0) + 1);
  }
  return m;
}

function multisetsEqual(a, b) {
  if (a.size !== b.size) return false;
  for (const [k, c] of a) if (b.get(k) !== c) return false;
  return true;
}

// ===========================================================================
// Load raw sample data — twice, independently:
//   (1) rawRecords via OUR OWN jsonl reader -> our own oracle structures.
//   (2) sutRecords via D.parseJsonl -> D.buildDataset -> the object under test.
// ===========================================================================
const manifest = JSON.parse(fs.readFileSync(path.join(SAMPLE_DIR, "manifest.json"), "utf8"));

const rawRecords = [];
for (const f of manifest.files) {
  for (const r of readOwnJsonl(path.join(SAMPLE_DIR, f))) rawRecords.push(r);
}

// Classification per the top-of-file JSDoc's documented record shapes (PATH has
// states+moves; CALIBRATION has solved/nodes_explored; REGISTRY has kind==="registry").
const rawRegistry = [];
const rawCalibration = [];
const rawPath = [];
for (const r of rawRecords) {
  if (r && r.kind === "registry" && Array.isArray(r.relators)) rawRegistry.push(r);
  else if (r && Array.isArray(r.states) && Array.isArray(r.moves)) rawPath.push(r);
  else if (r && (typeof r.solved === "boolean" || typeof r.nodes_explored === "number")) rawCalibration.push(r);
}

let sutText = "";
for (const f of manifest.files) sutText += fs.readFileSync(path.join(SAMPLE_DIR, f), "utf8") + "\n";
const sutRecords = D.parseJsonl(sutText);
const ds = D.buildDataset(sutRecords);

section("0: sanity — both parsers see the same raw record count");
checkEqual(sutRecords.length, rawRecords.length, "D.parseJsonl and our own jsonl reader parse the same total record count");
checkEqual(
  rawRegistry.length + rawCalibration.length + rawPath.length,
  rawRecords.length,
  "our classification (registry/calibration/path) accounts for every raw record"
);

// ===========================================================================
// TEST 1 — groupStats vs raw counting
// ===========================================================================
section("1: groupStats vs independent raw counting");

const registryByDataset = new Map(); // dataset -> [{idx, subset}]
for (const r of rawRegistry) {
  if (!registryByDataset.has(r.dataset)) registryByDataset.set(r.dataset, []);
  registryByDataset.get(r.dataset).push({ idx: r.idx, subset: r.subset });
}

const armsByDatasetOracle = new Map(); // dataset -> Set(arm)
const calibIndex = new Map(); // "dataset|idx|arm" -> calibration record
for (const c of rawCalibration) {
  if (!armsByDatasetOracle.has(c.dataset)) armsByDatasetOracle.set(c.dataset, new Set());
  armsByDatasetOracle.get(c.dataset).add(c.arm);
  calibIndex.set(c.dataset + "|" + c.idx + "|" + c.arm, c);
}

console.log(
  "  oracle: datasets=" +
    JSON.stringify(Array.from(registryByDataset.keys())) +
    " armsByDataset=" +
    JSON.stringify(
      Object.fromEntries(Array.from(armsByDatasetOracle.entries()).map(([k, v]) => [k, v.size]))
    )
);

/**
 * (presentation x z-word) cell counting, re-derived independently from the raw
 * registry + calibration records — mirrors the semantics documented in data.js's
 * own JSDoc for groupStats (which we read, per the task's allowed-reading rule):
 * unit = one (presentation, arm) cell; arm="all" multiplies each in-scope
 * presentation by that DATASET's own distinct-arm count; a single arm is 1
 * cell/presentation regardless of whether that arm was ever run for it.
 */
function expectedGroupStats(sel) {
  const datasetsInScope = sel.dataset === "all" ? Array.from(registryByDataset.keys()) : [sel.dataset];
  let total = 0,
    presentations = 0,
    attempted = 0,
    solved = 0;
  for (const dsName of datasetsInScope) {
    const entries = (registryByDataset.get(dsName) || []).filter(
      (e) => sel.subset === "all" || e.subset === sel.subset
    );
    presentations += entries.length;
    const armSet = armsByDatasetOracle.get(dsName) || new Set();
    for (const e of entries) {
      if (sel.arm === "all") {
        total += armSet.size;
        for (const a of armSet) {
          const rec = calibIndex.get(dsName + "|" + e.idx + "|" + a);
          if (rec) {
            attempted++;
            if (rec.solved) solved++;
          }
        }
      } else {
        total += 1;
        const rec = calibIndex.get(dsName + "|" + e.idx + "|" + sel.arm);
        if (rec) {
          attempted++;
          if (rec.solved) solved++;
        }
      }
    }
  }
  return { total, presentations, attempted, solved, notAttempted: total - attempted, unsolved: attempted - solved };
}

const selections = [
  { dataset: "1190MS", arm: "all", subset: "all" }, // required: 1190MS all/all
  { dataset: "1190MS", arm: "r1", subset: "all" }, // required: 1190MS single-arm
  { dataset: "1190MS", arm: "all", subset: "original" }, // required: 1190MS subset=original all-arms
  { dataset: "1190MS", arm: "all", subset: "hard" }, // extra: hard subset (never attempted)
  { dataset: "ms_reps_unsolved", arm: "all", subset: "all" }, // required: ms_reps_unsolved all/all
  { dataset: "ms_reps_unsolved", arm: "r2", subset: "all" }, // extra: reps single-arm
  { dataset: "all", arm: "all", subset: "all" }, // required: dataset="all" all/all
  { dataset: "all", arm: "r1", subset: "all" }, // extra: single arm shared by both datasets
  { dataset: "all", arm: "g", subset: "all" }, // extra: arm that exists in ONE dataset only
  { dataset: "all", arm: "all", subset: "hard" }, // extra: subset that exists in ONE dataset only
];

for (const sel of selections) {
  const label = "dataset=" + sel.dataset + " arm=" + sel.arm + " subset=" + sel.subset;
  const exp = expectedGroupStats(sel);
  const act = D.groupStats(ds, sel);
  checkEqual(act.total, exp.total, label + " :: total");
  checkEqual(act.presentations, exp.presentations, label + " :: presentations");
  checkEqual(act.attempted, exp.attempted, label + " :: attempted");
  checkEqual(act.solved, exp.solved, label + " :: solved");
  checkEqual(act.notAttempted, exp.notAttempted, label + " :: notAttempted");
  check(act.solved + act.unsolved + act.notAttempted === act.total, label + " :: solved+unsolved+notAttempted === total");
  check(act.attempted === act.solved + act.unsolved, label + " :: attempted === solved+unsolved");
}

// ===========================================================================
// TEST 2 — stable-slot invariants over every path, via D.buildSteps
// ===========================================================================
section("2: buildSteps stable-slot invariants");

const pathItems = ds.items.filter((it) => it.path);
console.log("  paths to check: " + pathItems.length);

let stepsChecked = 0;
let transitionsChecked = 0;

for (const it of pathItems) {
  const built = D.buildSteps(it.path);
  const steps = built.steps;
  const label = it.dataset + "|" + it.idx + "|" + it.arm;

  for (let t = 0; t < steps.length; t++) {
    const st = steps[t];
    // (a) slots.length === nGen
    check(st.slots.length === built.nGen, label + " step " + t + " :: slots.length === nGen");
    // (b) multiset of slots[*].word === multiset of state
    const slotWords = st.slots.map((s) => s.word);
    check(
      multisetsEqual(multisetOfWords(slotWords), multisetOfWords(st.state)),
      label + " step " + t + " :: multiset(slots.word) === multiset(state)"
    );
    stepsChecked++;
  }

  for (let t = 1; t < steps.length; t++) {
    const prev = steps[t - 1];
    const curr = steps[t];
    const label2 = label + " step " + (t - 1) + "->" + t;

    // (c) exactly one slot's word changes between consecutive steps
    const changedIdxs = [];
    for (let i = 0; i < curr.slots.length; i++) {
      if (keyOfWord(curr.slots[i].word) !== keyOfWord(prev.slots[i].word)) changedIdxs.push(i);
    }
    check(changedIdxs.length === 1, label2 + " :: exactly one slot word changes (found " + changedIdxs.length + ")");

    if (changedIdxs.length === 1) {
      const changedIdx = changedIdxs[0];
      // (d) changed index equals step.changedSlot, and that slot has isChanged===true
      check(changedIdx === curr.changedSlot, label2 + " :: changed index === changedSlot");
      check(curr.slots[changedIdx].isChanged === true, label2 + " :: changed slot has isChanged===true");
      // all OTHER slots should be isChanged===false at this step
      let othersOk = true;
      for (let i = 0; i < curr.slots.length; i++) {
        if (i !== changedIdx && curr.slots[i].isChanged) othersOk = false;
      }
      check(othersOk, label2 + " :: non-changed slots have isChanged===false");

      // (e) changed slot's new/old word equals the multiset-diff added/removed relator
      // (multiset diff computed with OUR OWN multisetDiffOwn, independent of data.js)
      const diff = multisetDiffOwn(prev.state, curr.state);
      check(
        diff.removed.length === 1 && diff.added.length === 1,
        label2 + " :: raw-state multiset diff is exactly 1-removed/1-added"
      );
      if (diff.removed.length === 1 && diff.added.length === 1) {
        check(
          keyOfWord(curr.slots[changedIdx].word) === keyOfWord(diff.added[0]),
          label2 + " :: changed slot's new word === multiset-diff added relator"
        );
        check(
          keyOfWord(prev.slots[changedIdx].word) === keyOfWord(diff.removed[0]),
          label2 + " :: changed slot's previous word === multiset-diff removed relator"
        );
      }
    }
    transitionsChecked++;
  }
}
console.log("  steps checked: " + stepsChecked + ", transitions checked: " + transitionsChecked);

// ===========================================================================
// TEST 3 — reps_grid.json vs raw CSVs
// ===========================================================================
section("3: reps_grid.json vs raw CSVs (ms_solved_grid.csv, ms_reps_unsolved.csv)");

const gridRows = readOwnCsv(path.join(RAW_DIR, "ms_solved_grid.csv"));
const gridHeader = gridRows[0];
const gridDataRows = gridRows.slice(1, gridRows.length - 1); // drop header + trailing count row
const gridCountRow = gridRows[gridRows.length - 1];
checkEqual(gridDataRows.length, 170, "ms_solved_grid.csv has 170 word data rows");

// gridCsv[word][n] = status string ('trivial' or '<len>_<id>')
const gridCsv = new Map();
const nCols = [1, 2, 3, 4, 5, 6, 7];
for (const row of gridDataRows) {
  const word = row[0];
  const byN = new Map();
  for (const n of nCols) byN.set(n, row[n].trim());
  gridCsv.set(word, byN);
}

const repsRows = readOwnCsv(path.join(RAW_DIR, "ms_reps_unsolved.csv"));
const repsHeader = repsRows[0];
const repsDataRows = repsRows.slice(1);
checkEqual(repsDataRows.length, 261, "ms_reps_unsolved.csv has 261 data rows");
const repsNames = repsDataRows.map((r) => r[2]);

const gridJson = JSON.parse(fs.readFileSync(path.join(SAMPLE_DIR, "reps_grid.json"), "utf8"));
const cells = gridJson.cells;

checkEqual(cells.length, 1190, "reps_grid.json has 1190 cells (170 words x 7 n-values)");

const nonTrivialLabels = cells.filter((c) => c.status !== "trivial").map((c) => c.status);
const trivialCells = cells.filter((c) => c.status === "trivial");
checkEqual(trivialCells.length, 640, "1190MS: 640 trivial cells");
checkEqual(nonTrivialLabels.length, 550, "1190MS: 550 labelled (non-trivial) cells");

const nonTrivialLabelSet = new Set(nonTrivialLabels);
const repsNameSet = new Set(repsNames);
checkEqual(repsNameSet.size, 261, "ms_reps_unsolved.csv names are 261 distinct labels");
check(
  nonTrivialLabelSet.size === repsNameSet.size &&
    Array.from(nonTrivialLabelSet).every((n) => repsNameSet.has(n)) &&
    Array.from(repsNameSet).every((n) => nonTrivialLabelSet.has(n)),
  "set of non-trivial grid labels === set of 261 ms_reps_unsolved.csv names"
);

// each grid cell's status matches the raw CSV cell at (word, n)
let statusMismatches = 0;
for (const c of cells) {
  const byN = gridCsv.get(c.w);
  if (!byN) {
    statusMismatches++;
    continue;
  }
  const csvVal = byN.get(c.n);
  if (csvVal !== c.status) statusMismatches++;
}
check(statusMismatches === 0, "every grid cell's status matches ms_solved_grid.csv (mismatches=" + statusMismatches + ")");

// ms_idx is a bijection onto 0..1189
const msIdxSet = new Set(cells.map((c) => c.ms_idx));
check(msIdxSet.size === 1190, "ms_idx values are all distinct (1190 distinct values)");
let idxBijectionOk = true;
for (let i = 0; i < 1190; i++) if (!msIdxSet.has(i)) idxBijectionOk = false;
check(idxBijectionOk, "ms_idx set is exactly {0,...,1189}");

// each labelled cell's rep_idx indexes the correct CSV row (name matches)
let repIdxMismatches = 0;
let repIdxMissing = 0;
for (const c of cells) {
  if (c.status === "trivial") continue;
  if (c.rep_idx == null || c.rep_idx < 0 || c.rep_idx >= repsDataRows.length) {
    repIdxMissing++;
    continue;
  }
  const rowName = repsDataRows[c.rep_idx][2];
  if (rowName !== c.status) repIdxMismatches++;
}
check(repIdxMissing === 0, "every labelled cell has a valid in-range rep_idx");
check(repIdxMismatches === 0, "every labelled cell's rep_idx row name matches its status (mismatches=" + repIdxMismatches + ")");

// bonus: internal cross-check against the CSV's own per-column trivial-count row
let countRowOk = true;
for (const n of nCols) {
  const expectedTrivialForN = cells.filter((c) => c.n === n && c.status === "trivial").length;
  if (String(expectedTrivialForN) !== gridCountRow[n].trim()) countRowOk = false;
}
check(countRowOk, "per-n trivial counts (from cells) match ms_solved_grid.csv's own count row");

// bonus: reps_grid.json's own declared totals agree with what we counted
if (typeof gridJson.n_trivial === "number") checkEqual(gridJson.n_trivial, 640, "reps_grid.json n_trivial === 640");
if (typeof gridJson.n_rep_cells === "number") checkEqual(gridJson.n_rep_cells, 550, "reps_grid.json n_rep_cells === 550");

// ===========================================================================
// TEST 4 — (n, w) -> ms_idx bijection: synthesize MS(n,w), canonicalise
// independently, and confirm registry_1190MS[ms_idx] shares that key.
// ===========================================================================
section("4: (n,w) -> ms_idx bijection spot-check");

const regByIdx1190 = new Map();
for (const r of rawRegistry) {
  if (r.dataset === "1190MS") regByIdx1190.set(r.idx, r.relators);
}
checkEqual(regByIdx1190.size, 1190, "registry_1190MS.jsonl has 1190 distinct idx entries");

// hand-picked: first cell, last cell, one per n=1..7 (mix of trivial + labelled)
const handPicked = [cells[0], cells[cells.length - 1]];
for (let n = 1; n <= 7; n++) {
  const c = cells.find((cc) => cc.n === n);
  if (c) handPicked.push(c);
}
// a couple of explicit interesting picks: a trivial one and a labelled one, deep in the grid
const explicitLabelled = cells.find((c) => c.status !== "trivial");
const explicitTrivialDeep = cells.slice().reverse().find((c) => c.status === "trivial");
if (explicitLabelled) handPicked.push(explicitLabelled);
if (explicitTrivialDeep) handPicked.push(explicitTrivialDeep);

// deterministic pseudo-random spread across the 1190 cells (fixed stride, reproducible)
const strideSample = [];
const STRIDE = 37;
for (let i = 0; i < 30; i++) strideSample.push(cells[(i * STRIDE) % cells.length]);

const seen = new Set();
const sample = [];
for (const c of handPicked.concat(strideSample)) {
  const key = c.w + "|" + c.n;
  if (seen.has(key)) continue;
  seen.add(key);
  sample.push(c);
}
console.log("  sampled cells: " + sample.length + " (>= 30 required)");
check(sample.length >= 30, "sampled at least 30 distinct (w,n) cells");

let bijectionMismatches = 0;
for (const c of sample) {
  const [r1, r2] = msRelatorsOwn(c.n, c.w);
  const expectedKey = presentationKeyOwn(r1, r2);
  const regRel = regByIdx1190.get(c.ms_idx);
  const label = "w=" + c.w + " n=" + c.n + " ms_idx=" + c.ms_idx;
  if (!regRel) {
    bijectionMismatches++;
    check(false, label + " :: registry_1190MS has an entry at ms_idx");
    continue;
  }
  const actualKey = presentationKeyOwn(regRel[0], regRel[1]);
  const ok = actualKey === expectedKey;
  if (!ok) bijectionMismatches++;
  check(
    ok,
    label +
      " :: synthesized MS(" +
      c.n +
      "," +
      c.w +
      ") AC-base-equals registry_1190MS[" +
      c.ms_idx +
      "]"
  );
}
check(bijectionMismatches === 0, "no (n,w)->ms_idx bijection mismatches across " + sample.length + " sampled cells");

// ===========================================================================
// SUMMARY
// ===========================================================================
console.log("\n=== SUMMARY ===");
console.log("assertions passed: " + passCount);
console.log("assertions failed: " + failCount);
console.log("total assertions:  " + (passCount + failCount));

if (failCount > 0) {
  console.log("\nFAILED ASSERTIONS:");
  for (const f of failures) console.log("  - " + f);
  console.log("\nRESULT: FAIL");
  process.exit(1);
} else {
  console.log("\nRESULT: PASS — all assertions passed, no discrepancies found.");
  process.exit(0);
}
