#!/usr/bin/env python3
"""Exact supported-class Neuwirth rank scan of aca_124 source representatives."""
import csv,json,sys,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WT=ROOT/'.claude/worktrees/codex-proofs';sys.path.insert(0,str(WT))
from experiments.stable_ac.thickenable.neuwirth_rank_solver import solve_spherical

data=ROOT/'.claude/worktrees/codex-proofs/data/ms_unsolved_reps/aca_124.csv'
rows=[]
for row in csv.DictReader(data.open()):
 d=solve_spherical((row['r1'],row['r2']))
 rows.append({'name':row['name'],'words':[row['r1'],row['r2']], 'verdict':d.verdict,
   'spherical':d.spherical,'support':d.support.kind,'reason':d.reason,
   'exhaustive':d.counters.exhaustive,'witness':None if d.witness is None else {
     'scheme':d.witness.scheme,'genus':d.witness.genus,'euler_characteristic':d.witness.euler_characteristic}})
counts=Counter(r['verdict'] for r in rows);supports=Counter(r['support'] for r in rows)
payload={'schema':'aca124-neuwirth-rank-scan-v1','counts':dict(counts),'supports':dict(supports),'rows':rows}
out=ROOT/'.scratch/aca124_neuwirth_rank_scan.json';out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
print(json.dumps({'counts':dict(counts),'supports':dict(supports),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
