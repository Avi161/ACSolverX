#!/usr/bin/env python3
"""
Adversarial fact-check recompute for the NeurIPS AK(3)/stable-AC preprint.

Loads RAW data (JSONL / JSONL.gz / CSV / JSON) directly -- never the
figure_digest.json / tables_digest.json intermediates -- recomputes every
empirical numeric claim in paper/paper.md, and prints per-claim verdicts.

Exit 0 iff every recomputable claim matches (DOC-only claims are informational
and excluded from the pass/fail gate; they are printed and listed separately).

Usage:
    .venv/bin/python paper/fact_check/recompute.py
"""
import os, sys, json, gzip, csv, collections, statistics as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def R(*p):            return os.path.join(ROOT, *p)
def rows(p):          return [json.loads(l) for l in open(R(p)) if l.strip()]
def grows(p):         return [json.loads(l) for l in gzip.open(R(p), "rt") if l.strip()]
def csvrows(p):
    with open(R(p)) as f: return list(csv.DictReader(f))
def jload(p):         return json.load(open(R(p)))
def dec(rel):
    m = {1:"x",-1:"X",2:"y",-2:"Y",3:"z",-3:"Z"}
    return "".join(m[c] for c in rel)

# ---------------------------------------------------------------- raw sources
BASE   = "results/baseline_greedy/solved/calibration_baseline.jsonl"
ARM    = "results/stable_ac/3_generators_w_choices/ms640/runs/calibration_%s.jsonl"
AK3    = "results/stable_ac/3_generators_w_choices/ak_3_test/runs/ak3_%s_%d.jsonl"
HARD   = "results/stable_ac/3_generators_w_choices/hard_solved_test/runs/hard_ms%d_100000.jsonl"
WORDBK = "results/stable_ac/3_generators_w_choices/ak_3_test/word_bank.json"
TRIALS = "results/stable_ac/ak3_stable_proof/archive/campaign_trials.jsonl.gz"
CANDS  = "results/stable_ac/ak3_stable_proof/archive/campaign_candidates.jsonl.gz"
GRID   = "results/stable_ac/ak3_stable_proof/archive/campaign_grid_probes.jsonl.gz"
SUMM   = "results/stable_ac/ak3_stable_proof/collect_summary.json"
LIT    = "results/stable_ac/ak3_stable_proof/literature_checks.json"
CENSUS = "results/stable_ac/ak3_stable_proof/laneD/floor_census.jsonl"
SOLVE  = "results/stable_ac/ak3_stable_proof/laneD/solve.jsonl"
BEAM1  = "results/stable_ac/ak3_stable_proof/runs/beam_laneD_floor.csv"
BEAM2  = "results/stable_ac/ak3_stable_proof/runs/beam_laneD_floor_w2048.csv"
LEAFC  = "results/stable_ac/ak3_stable_proof/runs/leaf_class.jsonl"
CATL   = "results/stable_ac/ak3_stable_proof/catalog/catalog_leaves.jsonl"
CATCERTS = "results/stable_ac/ak3_stable_proof/catalog/certs"
CERTS  = "results/stable_ac/ak3_stable_proof/certs"
SS     = "experiments/test_cap/solve_stratified.jsonl"
SL     = "experiments/test_cap/search_L.jsonl"

# ---------------------------------------------------------------- claim table
claims = []
def add(cid, section, quoted, paper_value, source, expr, recomputed, match):
    claims.append(dict(claim_id=cid, section=section, quoted=quoted,
                       value=paper_value, source_file=source, recompute_expr=expr,
                       recomputed_value=recomputed, match=match))
def eq(a, b):
    return "YES" if a == b else "NO"

# ================================================================ load once
base   = rows(BASE)
bsolved= [r for r in base if r["solved"]]
bset   = set(r["idx"] for r in bsolved)
arms   = {a: rows(ARM % a) for a in ("r1","r2","x","y")}
armset = {a: set(r["idx"] for r in arms[a] if r["solved"]) for a in arms}
trials = grows(TRIALS)
cands  = grows(CANDS)
grid   = grows(GRID)
summ   = jload(SUMM)
lit    = jload(LIT)
census = rows(CENSUS)
solve  = rows(SOLVE)
beam1  = csvrows(BEAM1)
beam2  = csvrows(BEAM2)

# ================================================================ SECTION 4.2 / Table 3 (arms)
_bsolved=sum(1 for r in base if r["solved"])
add("arm_baseline_solved","4.2/T3","634 of the 640 known-solvable ... solve","634",BASE,
    "count solved in baseline stream", _bsolved, eq(_bsolved,634))
add("arm_baseline_exhausted","3.1/T3","remaining 6 (indices 634-639)","6",BASE,
    "count not solved", sum(1 for r in base if not r["solved"]), eq(sum(1 for r in base if not r['solved']),6))
add("straggler_idx","3.1/4.2","the remaining 6 (indices 634-639)","634-639",BASE,
    "sorted idx of unsolved baseline rows",
    ",".join(map(str,sorted(r["idx"] for r in base if not r["solved"]))),
    eq(sorted(r["idx"] for r in base if not r["solved"]),[634,635,636,637,638,639]))

for a,exp_s,exp_e in (("r1",619,21),("r2",602,38),("x",540,100),("y",523,117)):
    s=sum(1 for r in arms[a] if r["solved"]); e=sum(1 for r in arms[a] if r.get("exhausted_budget"))
    add(f"arm_{a}_solved","4.2/T3",f"{a} solved {exp_s}",str(exp_s),ARM%a,"count solved",s,eq(s,exp_s))
    add(f"arm_{a}_exhausted","4.2/T3",f"{a} exhausted {exp_e}",str(exp_e),ARM%a,"count exhausted_budget",e,eq(e,exp_e))
    add(f"arm_{a}_subset","4.2/T3",f"|{a}\\baseline|=0","0",ARM%a,"len(armset-bset)",len(armset[a]-bset),eq(len(armset[a]-bset),0))

union=set().union(*armset.values()); inter=set.intersection(*armset.values())
add("arm_union","4.2/Fig2","union across arms is 620","620",ARM%"*","|r1|r2|x|y|",len(union),eq(len(union),620))
add("arm_inter","4.2/Fig2","intersection is 523","523",ARM%"*","|r1&r2&x&y|",len(inter),eq(len(inter),523))

# node/path stats (solved-only) — Table 3 + Appendix C extended table
def statline(stream_rows):
    sol=[r for r in stream_rows if r["solved"]]
    n=[r["nodes_explored"] for r in sol]; pl=[r["path_len"] for r in sol]
    return (min(n),max(n),round(st.mean(n),1),st.median(n),
            min(pl),max(pl),round(st.mean(pl),1),st.median(pl))
STAT={"baseline":statline(base),"r1":statline(arms["r1"]),"r2":statline(arms["r2"]),
      "x":statline(arms["x"]),"y":statline(arms["y"])}
EXP={  # min,max,mean,median nodes ; min,max,mean,median path  (Appendix C extended table)
 "baseline":(3,77385,1662.0,11,2,710,32.6,8),
 "r1":(5,239578,2802.6,13,4,714,33.8,12),
 "r2":(4,291479,3637.1,13,3,715,29.9,11),
 "x":(4,326326,14680.7,10,3,102,12.1,9),
 "y":(4,491437,21832.7,10,3,102,11.5,9)}
for a in ("baseline","r1","r2","x","y"):
    src = BASE if a=="baseline" else ARM%a
    got=STAT[a]; exp=EXP[a]
    add(f"stat_{a}_nodes","T3/AppC",f"{a} nodes min/max/mean/median {exp[:4]}",str(exp[:4]),src,
        "min/max/mean/median nodes over solved",str(got[:4]),eq(got[:4],exp[:4]))
    add(f"stat_{a}_path","AppC",f"{a} path min/max/mean/median {exp[4:]}",str(exp[4:]),src,
        "min/max/mean/median path_len over solved",str(got[4:]),eq(got[4:],exp[4:]))

# baseline idx625 / idx610 node+path  (Section 3.4)
for idx,en,ep in ((625,77385,663),(610,61066,307)):
    r=[x for x in base if x["idx"]==idx][0]
    add(f"base_idx{idx}_nodes","3.4",f"index {idx} ({en} nodes)",str(en),BASE,
        f"baseline idx {idx} nodes_explored",r["nodes_explored"],eq(r["nodes_explored"],en))
    add(f"base_idx{idx}_path","3.4",f"index {idx} ({ep} moves)",str(ep),BASE,
        f"baseline idx {idx} path_len",r["path_len"],eq(r["path_len"],ep))

# ================================================================ SECTION 4.3 / Table 1 / Fig 6 (AK3 word bank)
wb=jload(WORDBK)
bf=wb["by_family"]
fam_exp={"relhalf":17,"wk":17,"wstar":5,"conj":14,"comm":6,"ms":3,"brute":33}
for fam,c in fam_exp.items():
    got=len(bf[fam]) if isinstance(bf[fam],list) else bf[fam]
    add(f"wb_{fam}","T1",f"{fam} = {c}",str(c),WORDBK,f"len(by_family[{fam}])",got,eq(got,c))
tot95=sum((len(v) if isinstance(v,list) else v) for v in bf.values())
add("wb_families_total","T1","seven families (95 words)","95",WORDBK,"sum by_family",tot95,eq(tot95,95))
add("wb_total_97","T1","Total 97","97",WORDBK,"95 families + 2 control",tot95+2,eq(tot95+2,97))

ak3hist={}
for form in ("rep","textbook"):
    for b in (100000,1000000):
        rr=rows(AK3%(form,b))
        ak3hist[(form,b)]=dict(collections.Counter(r["min_total_len"] for r in rr))
        add(f"ak3_{form}_{b}_rows","4.3",f"{form}@{b} 97-row",str(97),AK3%(form,b),"row count",len(rr),eq(len(rr),97))
        add(f"ak3_{form}_{b}_solved","4.3",f"{form}@{b} 0 solved","0",AK3%(form,b),"solved count",
            sum(1 for r in rr if r["solved"]),eq(sum(1 for r in rr if r['solved']),0))
def hcmp(cid,sec,q,exp,src,got):
    add(cid,sec,q,str(exp),src,"floor histogram",str(got),eq(got,exp))
hcmp("ak3_rep_1M_hist","4.3/J","rep@1M {13:88,14:2,15:7}",{13:88,14:2,15:7},AK3%("rep",1000000),ak3hist[("rep",1000000)])
hcmp("ak3_txt_1M_hist","4.3/J","textbook@1M {13:86,14:2,15:9}",{13:86,14:2,15:9},AK3%("textbook",1000000),ak3hist[("textbook",1000000)])
hcmp("ak3_rep_100k_hist","AppC-Fig6","rep@100k {13:79,14:11,15:7}",{13:79,14:11,15:7},AK3%("rep",100000),ak3hist[("rep",100000)])
hcmp("ak3_txt_100k_hist","AppC-Fig6","textbook@100k {13:77,14:11,15:9}",{13:77,14:11,15:9},AK3%("textbook",100000),ak3hist[("textbook",100000)])
add("ak3_total_388","4.3/Fig6","388 runs (97x2x2), 0 solved","388",AK3%("*",0),
    "4 files x 97 rows", 4*97, eq(4*97,388))

# ================================================================ SECTION 4.4 / Fig 7 (hard targets)
for idx,exp_solved,exp_lo,exp_hi,exp_peak,exp_peakN in ((625,4,17,25,19,41),(610,2,16,23,19,34)):
    rr=rows(HARD%idx)
    sol=[r for r in rr if r["solved"]]
    add(f"hard{idx}_solved","4.4",f"idx{idx}: {exp_solved} of {len(rr)} solve",str(exp_solved),HARD%idx,
        "solved count",len(sol),eq(len(sol),exp_solved))
    uns=[r for r in rr if not r["solved"]]
    floors=[r["min_total_len"] for r in uns]
    add(f"hard{idx}_floorlo","Fig7",f"idx{idx} floor range low {exp_lo}",str(exp_lo),HARD%idx,"min floor",min(floors),eq(min(floors),exp_lo))
    add(f"hard{idx}_floorhi","Fig7",f"idx{idx} floor range high {exp_hi}",str(exp_hi),HARD%idx,"max floor",max(floors),eq(max(floors),exp_hi))
    pk=collections.Counter(floors).most_common(1)[0]
    add(f"hard{idx}_peak","Fig7",f"idx{idx} peak {exp_peak} with {exp_peakN}",f"{exp_peak}/{exp_peakN}",HARD%idx,
        "mode floor + count",f"{pk[0]}/{pk[1]}",eq((pk[0],pk[1]),(exp_peak,exp_peakN)))
# tie node counts (special check B)
h625=rows(HARD%625); h610=rows(HARD%610)
def node_of(stream,word):
    m=[r for r in stream if r["word_name"]==word]
    return m[0]["nodes_explored"] if m else None
add("tie625_r1","4.4/B","z=r1 (77,395 nodes)","77395",HARD%625,"idx625 r1 nodes",node_of(h625,"r1"),eq(node_of(h625,"r1"),77395))
add("tie625_r2","4.4/B","z=r2 (80,111)","80111",HARD%625,"idx625 r2 nodes",node_of(h625,"r2"),eq(node_of(h625,"r2"),80111))
add("tie625_relhalf_r1","4.4/B","relhalf twin ties r1 77,395","77395",HARD%625,
    "relhalf word tying 77395 exists",str(77395 in [r['nodes_explored'] for r in h625 if r['solved'] and r['family']=='relhalf']),
    eq(77395 in [r['nodes_explored'] for r in h625 if r['solved'] and r['family']=='relhalf'],True))
add("tie625_xYXyxyy","4.4/B","xYXyxyy relhalf twin (80,111)","80111",HARD%625,"nodes of word xYXyxyy",
    node_of(h625,"xYXyxyy"),eq(node_of(h625,"xYXyxyy"),80111))
add("tie610_r1","4.4/B","idx610 z=r1 61,082","61082",HARD%610,"idx610 r1 nodes",node_of(h610,"r1"),eq(node_of(h610,"r1"),61082))
add("tie610_relhalf","4.4/B","relhalf twin 61,082","61082",HARD%610,
    "relhalf word tying 61082 exists",str(61082 in [r['nodes_explored'] for r in h610 if r['solved'] and r['family']=='relhalf']),
    eq(61082 in [r['nodes_explored'] for r in h610 if r['solved'] and r['family']=='relhalf'],True))

# ================================================================ SECTION 4.5 / Table 4 / Fig 3 (campaign, five lanes)
add("camp_candidates","4.5","180,645 distinct 2-generator quotients","180645",CANDS,
    "row count campaign_candidates.jsonl.gz",len(cands),eq(len(cands),180645))
add("camp_candidates_distinct","4.5","180,645 distinct quotients","180645",CANDS,
    "distinct mkey",len(set(r["mkey"] for r in cands)),eq(len(set(r["mkey"] for r in cands)),180645))
add("camp_trials","4.5/T4","16,870 solve attempts","16870",TRIALS,"row count campaign_trials",len(trials),eq(len(trials),16870))
add("camp_trials_solved","4.5/T4","0 of 16,870 attempts solved","0",TRIALS,"solved count",
    sum(1 for r in trials if r["solved"]),eq(sum(1 for r in trials if r['solved']),0))
add("camp_distinct_cand","4.5","6,058 distinct candidates","6058",TRIALS,"distinct mkey in trials",
    len(set(r["mkey"] for r in trials)),eq(len(set(r["mkey"] for r in trials)),6058))
thist=dict(collections.Counter(r["min_total_len"] for r in trials))
add("camp_floor_hist","4.5/Fig3/T4","campaign floor {13:16,844, 19:23, 20:3}",str({13:16844,19:23,20:3}),TRIALS,
    "trial-level floor histogram",str(thist),eq(thist,{13:16844,19:23,20:3}))
facet=dict(collections.Counter(r["source"] for r in trials))
add("camp_facets","4.5/AppC","D1=5866, D2=5350, D3=5497, resolve=157",
    str({"laneD:D1":5866,"laneD:D2":5350,"laneD:D3":5497,"resolve":157}),TRIALS,"trials by source",
    str(facet),eq(facet,{"laneD:D1":5866,"laneD:D2":5350,"laneD:D3":5497,"resolve":157}))
add("camp_facet_sum","AppC","four facets sum to 16,870","16870",TRIALS,"5866+5350+5497+157",
    5866+5350+5497+157,eq(5866+5350+5497+157,16870))

# grid probes (Table 4 A/B/C + Appendix C list)
add("grid_count","4.5/T4","14 grid probes","14",GRID,"row count campaign_grid_probes",len(grid),eq(len(grid),14))
mitm=[r for r in grid if r["kind"]=="mitm_out"]
laneB=[r for r in grid if r["kind"]=="laneB"]
laneC=[r for r in grid if r["kind"]=="laneC"]
add("laneA_count","T4","Lane A 2 probes","2",GRID,"mitm_out rows",len(mitm),eq(len(mitm),2))
add("laneA_targets","T4/AppC","targets = 1,177","1177",GRID,"mitm targets",
    list(set(r["targets"] for r in mitm)),eq(set(r["targets"] for r in mitm),{1177}))
add("laneA_nodes","T4/AppC","2 @ 2,000,000 nodes/side","2000000",GRID,"mitm nodes",
    list(set(r["nodes"] for r in mitm)),eq(set(r["nodes"] for r in mitm),{2000000}))
add("laneA_floor","T4","Lane A floor 13","13",GRID,"mitm min_total_len",
    list(set(r["min_total_len"] for r in mitm)),eq(set(r["min_total_len"] for r in mitm),{13}))
add("laneB_count","T4","Lane B 6 probes","6",GRID,"laneB rows",len(laneB),eq(len(laneB),6))
add("laneB_noderange","T4","6 @ 300k-800k nodes","300000-800000",GRID,"min/max laneB nodes",
    f"{min(r['nodes'] for r in laneB)}-{max(r['nodes'] for r in laneB)}",
    eq((min(r['nodes'] for r in laneB),max(r['nodes'] for r in laneB)),(300000,800000)))
# --- Appendix C grid-probe TABLE claims: Lane B hero-8 nodes 300,000 ; full-bank nodes 100,000
heroB=[r for r in laneB if r["bank_size"]==8]; fullB=[r for r in laneB if r["bank_size"]==95]
add("appC_laneB_hero_nodes","AppC-grid","hero-8 probe Nodes = 300,000 (Appendix C table)","300000",GRID,
    "actual hero-8 laneB node budgets",str(sorted(set(r["nodes"] for r in heroB))),
    eq(set(r["nodes"] for r in heroB),{300000}))
add("appC_laneB_full_nodes","AppC-grid","full 95-word probe Nodes = 100,000 (Appendix C table)","100000",GRID,
    "actual full-bank laneB node budgets",str(sorted(set(r["nodes"] for r in fullB))),
    eq(set(r["nodes"] for r in fullB),{100000}))
add("laneC_count","T4","Lane C 6 probes","6",GRID,"laneC rows",len(laneC),eq(len(laneC),6))
# Lane C floors by n-gen and form
laneC_floor={}
for r in laneC:
    nid=r["id"].split("@")[0]  # e.g. rep_n3
    laneC_floor[nid]=r["min_total_len"]
expC={"rep_n3":14,"rep_n4":15,"rep_n5":16,"textbook_n3":14,"textbook_n4":15,"textbook_n5":16}
add("laneC_floors","T4/4.5/AppC","14/15/16 for n=3/4/5 (rep & textbook)",str(expC),GRID,
    "laneC floor by id",str(laneC_floor),eq(laneC_floor,expC))
add("grid_solved","T4","0 of 14 grid probes solve","0",GRID,"grid probes solved/hit",
    sum(1 for r in grid if r.get("solved") or r.get("hit")),eq(sum(1 for r in grid if r.get('solved') or r.get('hit')),0))
# Lane B validation cert step counts (3,1,1)
def cert_steps(name): return len(jload(f"{CERTS}/{name}.json")["steps"])
add("laneB_M3corr_steps","4.5/T6","corrected-family instance in 3 steps","3",CERTS,"steps",
    cert_steps("laneB_M3corr_hero8_500"),eq(cert_steps("laneB_M3corr_hero8_500"),3))
add("laneB_ms0_steps","4.5/T6","two MS instances in 1","1",CERTS,"steps",
    cert_steps("laneB_ms0"),eq(cert_steps("laneB_ms0"),1))
add("laneB_ms0stab_steps","4.5/T6","two MS instances in 1","1",CERTS,"steps",
    cert_steps("laneB_ms0_stab"),eq(cert_steps("laneB_ms0_stab"),1))

# local reproduction (kept separate from campaign scale)
add("local_census","4.5/4.8/T5","1,006-candidate floor census","1006",CENSUS,"row count",len(census),eq(len(census),1006))
add("local_solve","4.5","1,937 solve attempts","1937",SOLVE,"row count solve.jsonl",len(solve),eq(len(solve),1937))
add("local_solve_floor13","4.5","bottoms out at exactly 13 on every one","{13}",SOLVE,
    "distinct min_total_len",str(sorted(set(r["min_total_len"] for r in solve))),
    eq(set(r["min_total_len"] for r in solve),{13}))
add("local_solve_0","4.5","0 solved (local)","0",SOLVE,"solved count",
    sum(1 for r in solve if r["solved"]),eq(sum(1 for r in solve if r['solved']),0))

# ================================================================ SECTION 4.6 / Fig 8 (RL beam)
add("beam512_rows","4.6/T4","0 of 155 floor states","155",BEAM1,"beam512 data rows",len(beam1),eq(len(beam1),155))
add("beam512_solved","4.6","solves 0 of 155","0",BEAM1,"solved==True count",
    sum(1 for r in beam1 if r["solved"]=="True"),eq(sum(1 for r in beam1 if r['solved']=='True'),0))
add("beam512_train","4.6/Fig8","155/155 of training-distribution","155",BEAM1,"train_solved==True",
    sum(1 for r in beam1 if r["train_solved"]=="True"),eq(sum(1 for r in beam1 if r['train_solved']=='True'),155))
tp=[int(r["train_path_length"]) for r in beam1 if r["train_solved"]=="True"]
add("beam512_trainmean","4.6/Fig8","mean path length 6.1","6.1",BEAM1,"mean train_path_length",round(st.mean(tp),1),eq(round(st.mean(tp),1),6.1))
add("beam512_trainmax","4.6/Fig8","max 16","16",BEAM1,"max train_path_length",max(tp),eq(max(tp),16))
add("beam512_trainrange","Fig8","range 2-16","2-16",BEAM1,"min-max train_path_length",f"{min(tp)}-{max(tp)}",eq((min(tp),max(tp)),(2,16)))
add("beam512_mode4","Fig8","mode length 4: 31 of 155","31",BEAM1,"count train_path_length==4",
    sum(1 for x in tp if x==4),eq(sum(1 for x in tp if x==4),31))
add("beam2048_rows","4.6/T4","hardest 30-state core","30",BEAM2,"beam2048 data rows",len(beam2),eq(len(beam2),30))
add("beam2048_solved","4.6","still solves 0","0",BEAM2,"solved==True",
    sum(1 for r in beam2 if r["solved"]=="True"),eq(sum(1 for r in beam2 if r['solved']=='True'),0))
add("beamE_total","4.5/RESULTS","0/155 + 0/30 (185 total)","185",BEAM1,"155+30",len(beam1)+len(beam2),eq(len(beam1)+len(beam2),185))

# ================================================================ SECTION 4.7 / Appendix F (cap control)
ss=rows(SS); sL=rows(SL)
add("cap_strat_rows","4.7/AppF","1,800 solve attempts","1800",SS,"row count",len(ss),eq(len(ss),1800))
add("cap_strat_solved","4.7/AppF","0 of 1,800 attempts solved","0",SS,"solved count",
    sum(1 for r in ss if r["solved"]),eq(sum(1 for r in ss if r['solved']),0))
add("cap_strat_floor13","4.7/AppF","every one flooring at exactly total length 13","{13}",SS,
    "distinct min_total_len",str(sorted(set(r["min_total_len"] for r in ss))),
    eq(set(r["min_total_len"] for r in ss),{13}))
nctrl=sum(1 for r in ss if r["total_len"]<=24); nlong=sum(1 for r in ss if r["total_len"]>=25)
add("cap_strat_controls","AppF","plus 200 short controls","200",SS,"rows total_len<=24",nctrl,eq(nctrl,200))
add("cap_strat_long","AppF","100 per bucket 25-40 (16 buckets = 1600)","1600",SS,"rows total_len>=25",nlong,eq(nlong,1600))
add("cap_search_rows","AppF","0 of 32 runs solve","32",SL,"row count search_L",len(sL),eq(len(sL),32))
add("cap_search_solved","AppF","0 of 32 runs solve","0",SL,"solved count",
    sum(1 for r in sL if r["solved"]),eq(sum(1 for r in sL if r['solved']),0))
add("cap_search_floors","AppF","Floors are 13 or 15","{13,15}",SL,"distinct min_total_len",
    str(sorted(set(r["min_total_len"] for r in sL))),eq(set(r["min_total_len"] for r in sL),{13,15}))
byfw=collections.defaultdict(dict)
for r in sL: byfw[(r["form"],r["word"])][r["max_len"]]=r
ident=sum(1 for d in byfw.values() if 24 in d and 48 in d and d[24]["visited"]==d[48]["visited"]
          and d[24]["min_total_len"]==d[48]["min_total_len"])
npairs=sum(1 for d in byfw.values() if 24 in d and 48 in d)
add("cap_search_identical","4.7/AppF","byte-identical in 16 of 16 (visited-count proxy)","16/16",SL,
    "pairs with identical visited-count AND floor across L24/L48",f"{ident}/{npairs}",eq((ident,npairs),(16,16)))

# ================================================================ SECTION 4.8 / Table 5 (floor census / two representatives)
byfloor=collections.Counter(r["floor_mkey"] for r in census)
top2=byfloor.most_common()
add("census_all13","4.8/T5","all 1,006 bottom out at 13","{13}",CENSUS,"distinct min_total_len",
    str(sorted(set(r["min_total_len"] for r in census))),eq(set(r["min_total_len"] for r in census),{13}))
add("census_two_classes","4.8/T5","exactly two canonical representatives","2",CENSUS,"distinct floor_mkey",
    len(byfloor),eq(len(byfloor),2))
add("census_class1","4.8/T5","F hit 712 times","712",CENSUS,"count of majority floor class",top2[0][1],eq(top2[0][1],712))
add("census_class2","4.8/T5","AK(3) reduced form hit 294","294",CENSUS,"count of minority floor class",top2[1][1],eq(top2[1][1],294))
p1=round(100*712/1006,1); p2=round(100*294/1006,1)
add("census_pct1_1dp","4.8/T5/G","712/1006 = 70.8%","70.8",CENSUS,"round(712/1006*100,1)",p1,eq(p1,70.8))
add("census_pct2_1dp","4.8/T5/G","294/1006 = 29.2%","29.2",CENSUS,"round(294/1006*100,1)",p2,eq(p2,29.2))
add("census_pct1_int","contrib/G","712/1006 = 71%","71",CENSUS,"round(712/1006*100)",round(100*712/1006),eq(round(100*712/1006),71))
add("census_pct2_int","contrib/G","294/1006 = 29%","29",CENSUS,"round(294/1006*100)",round(100*294/1006),eq(round(100*294/1006),29))
add("census_ratio","4.8/Fig5/G","reached 2.4x more often than AK(3)","2.4",CENSUS,"round(712/294,1)",round(712/294,1),eq(round(712/294,1),2.4))
# floor class relator words (raw) — Table5 vs AppendixC internal consistency
seen={}
for r in census:
    seen.setdefault(r["floor_mkey"], r["floor_state"])
class1_words=[dec(x) for x in seen[top2[0][0]]]
class2_words=[dec(x) for x in seen[top2[1][0]]]
add("census_F_relators","T5/AppC","F = YYxyXX, YYYXXyx","YYxyXX,YYYXXyx",CENSUS,
    "decoded majority floor_state",",".join(class1_words),eq(class1_words,["YYxyXX","YYYXXyx"]))
add("census_AK3_relators_T5","T5","Class2 = YXYxyx, YYYxxxx (Table 5)","YXYxyx,YYYxxxx",CENSUS,
    "decoded minority floor_state",",".join(class2_words),eq(class2_words,["YXYxyx","YYYxxxx"]))
add("census_AK3_relators_AppC","AppC","AK(3) reduced = YXYxyx, YYYYxxx (Appendix C)","YXYxyx,YYYYxxx",CENSUS,
    "decoded minority floor_state (raw)",",".join(class2_words),eq(class2_words,["YXYxyx","YYYYxxx"]))

# ================================================================ Certificates / Table 6 / Appendix B
def cert(name): return jload(f"{CERTS}/{name}.json")
def cinfo(name):
    d=cert(name); return len(d["steps"]), len(d["states"])
for name,es,st_ in (("appendixF_P25_to_AK3",53,54),("laneF_F_to_AK3",21,22),
                    ("laneB_M3corr_hero8_500",3,4),("laneB_ms0",1,2),("laneB_ms0_stab",1,2)):
    s,ns=cinfo(name)
    add(f"cert_{name}_steps","T6/AppB",f"{name} steps {es}",str(es),f"{CERTS}/{name}.json","len(steps)",s,eq(s,es))
    add(f"cert_{name}_states","T6/AppB",f"{name} states {st_}",str(st_),f"{CERTS}/{name}.json","len(states)",ns,eq(ns,st_))
# peak total length
def peak_tl(name):
    d=cert(name); return max(sum(len(r) for r in s["relators"]) for s in d["states"])
add("appF_peak25","4.1/4.8/AppE","Appendix-F path peaks at total length 25","25",
    f"{CERTS}/appendixF_P25_to_AK3.json","max total relator length over states",
    peak_tl("appendixF_P25_to_AK3"),eq(peak_tl("appendixF_P25_to_AK3"),25))
add("fig5_laneF_peak25","Fig5","21-move F->AK(3) path peaks at total length 25 (Fig 5 caption)","25",
    f"{CERTS}/laneF_F_to_AK3.json","max total relator length over laneF states",
    peak_tl("laneF_F_to_AK3"),eq(peak_tl("laneF_F_to_AK3"),25))
add("appF_above_floor","4.8/AppE","25, i.e. 12 above the floor","12",
    f"{CERTS}/appendixF_P25_to_AK3.json","25-13",peak_tl("appendixF_P25_to_AK3")-13,
    eq(peak_tl("appendixF_P25_to_AK3")-13,12))

# ================================================================ Section 4.1 / Table 2 / Appendix E (literature checks)
litkeys=["self_test_hom_counter","check1_correctedW_all_deletions_Z","check2_misprintW_broken",
         "check3_AK3_trivial","check4_M3_to_P25","check5_correctedW_3gen","check6_remark17_conjugation"]
npass=sum(1 for k in litkeys if lit[k]["pass"])
add("lit_7of7","4.1/T2/A","7 of 7 independent checks agree","7",LIT,"count pass:true",npass,eq(npass,7))
selftest=lit["self_test_hom_counter"]["details"]
add("lit_selftest_4of4","T2","4/4 match (hom-counter self-test)","4",LIT,"count match:true",
    sum(1 for d in selftest if d["match"]),eq(sum(1 for d in selftest if d['match']),4))
ndel=len(lit["check1_correctedW_all_deletions_Z"]["details"])
add("lit_14deletions","4.1/T2/AppE","all 14 deletions leave Z","14",LIT,"count deletion entries",ndel,eq(ndel,14))
allZ=all(v["is_Z"] for v in lit["check1_correctedW_all_deletions_Z"]["details"].values())
add("lit_14allZ","4.1/T2","14/14 present Z","True",LIT,"all is_Z",str(allZ),eq(allZ,True))
c2=lit["check2_misprintW_broken"]["details"]
add("lit_r7_homs","4.1/AppE","12 homomorphisms to S3","12",LIT,"misprint del_r7 s3_homs",
    c2["misprint_delete_r7"]["s3_homs"],eq(c2["misprint_delete_r7"]["s3_homs"],12))
add("lit_r7_nonab","4.1/AppE","6 of them non-abelian","6",LIT,"misprint del_r7 s3_nonabelian",
    c2["misprint_delete_r7"]["s3_nonabelian"],eq(c2["misprint_delete_r7"]["s3_nonabelian"],6))
add("lit_ak3_order1","4.1/T2","AK(3) presents the trivial group (order 1)","1",LIT,"check3 order",
    lit["check3_AK3_trivial"]["details"]["order_via_trivial_subgroup_cosets"],
    eq(lit["check3_AK3_trivial"]["details"]["order_via_trivial_subgroup_cosets"],1))
add("lit_conv_B","4.1/T2","convention B matches","B",LIT,"check4 matched_convention",
    lit["check4_M3_to_P25"]["details"]["matched_convention"],eq(lit["check4_M3_to_P25"]["details"]["matched_convention"],"B"))

# Lane A leaf classifications + catalog counts
lc=rows(LEAFC)
add("laneA_151_leaves","3.5/4.5","all 151 in-cap catalog leaves","151",LEAFC,"row count",len(lc),eq(len(lc),151))
add("laneA_all_trivial","3.5/4.5","proved plain-AC-trivial (all)","ac_trivial(151)",LEAFC,
    "count class==ac_trivial",sum(1 for r in lc if r["class"]=="ac_trivial"),
    eq(sum(1 for r in lc if r['class']=='ac_trivial'),151))
add("catalog_334","3.5","catalog of 334 presentations","334",CATL,"row count catalog_leaves",len(rows(CATL)),eq(len(rows(CATL)),334))
ncat=len([f for f in os.listdir(R(CATCERTS)) if f.endswith(".json")])
add("leaf_certs_14","AppB/T4/D","14 exported leaf certificates (count files)","14",CATCERTS,
    "count catalog/certs/*.json files",ncat,eq(ncat,14))
add("leaf_certs_137","AppB/lim5","remaining 137 leaf classifications","137",LEAFC,"151-14",len(lc)-ncat,eq(len(lc)-ncat,137))

# ================================================================ budget-framing cross-check (special: scale/budget bounds)
max_grid=max(r["nodes"] for r in grid)
add("budget_table4_upper","5-lim1/6/abstract","reached within ... up to 10^6 nodes per attempt","1000000",
    GRID,"max node budget among Table-4 grid probes (Lane A/C run at 2e6)",max_grid,eq(max_grid,1000000))
# informational: max budget among the 16,870 Lane D 'solve attempts' and the word-bank attempts
add("budget_laneD_max","AppD","Lane D solve budgets 2.5e4-2e5","200000",TRIALS,
    "max Lane D trial budget (resolve pass runs at 3e5)",max(r["budget"] for r in trials),
    eq(max(r["budget"] for r in trials),200000))

# ================================================================ DOC-only claims (documented, not raw-recomputed)
DOC=[
 ("doc_verifier_checks","3.6/AppB","20,947 checks with 0 failures","20947","RESULTS.md",
  "RESULTS.md P6: '20,947 checks passed, 0 failed'"),
 ("doc_beam_w512","4.6/E/I","beam width 512","512","RESULTS.md","RESULTS.md Lane E: 'beam width 512, 200 steps: 0/155'"),
 ("doc_beam_w2048","4.6/E/I","beam width 2048","2048","RESULTS.md","RESULTS.md Lane E: 'Escalation @width 2048 ... 0/30'"),
 ("doc_capA3_unique","4.7/AppF","250,397 unique candidates","250397","REPORT.md","test_cap REPORT.md Arm 3"),
 ("doc_capA3_over24","4.7/AppF","212,913 in the >24 region","212913","REPORT.md","test_cap REPORT.md Arm 3"),
 ("doc_lisitsa_159","4.1/AppE","159-transition AC path","159","RESULTS.md","RESULTS.md / Lisitsa Zenodo (literature count)"),
 ("doc_numba_speedup","3.7/AppD","3.7-5.7x speedup","3.7-5.7","RESULTS.md","lessons/RESULTS numba differential"),
]
for cid,sec,q,val,src,expr in DOC:
    add(cid,sec,q,val,src,expr,"(documented in "+src+")","DOC")

# ================================================================ output
def short(s,n=48):
    s=str(s); return s if len(s)<=n else s[:n-1]+"…"
print(f"{'claim_id':30s} {'match':5s} {'paper':>16s}  recomputed")
print("-"*100)
n_yes=n_no=n_doc=0
mism=[]
for c in claims:
    m=c["match"]
    if m=="YES": n_yes+=1
    elif m=="NO": n_no+=1; mism.append(c)
    else: n_doc+=1
    print(f"{c['claim_id']:30s} {m:5s} {short(c['value'],16):>16s}  {short(c['recomputed_value'])}")
print("-"*100)
print(f"TOTAL {len(claims)}  |  YES {n_yes}  NO {n_no}  DOC {n_doc}")
if mism:
    print("\nMISMATCHES:")
    for c in mism:
        print(f"  [{c['claim_id']}] ({c['section']}) paper={c['value']!r} recomputed={c['recomputed_value']!r}")
        print(f"      quoted: {c['quoted']}")
        print(f"      source: {c['source_file']}  expr: {c['recompute_expr']}")

# write TSV
tsv=R("paper/fact_check/claims.tsv")
with open(tsv,"w") as f:
    f.write("claim_id\tsection\tquoted_text\tvalue\tsource_file\trecompute_expr\trecomputed_value\tmatch\n")
    for c in claims:
        f.write("\t".join(str(c[k]).replace("\t"," ").replace("\n"," ") for k in
                 ("claim_id","section","quoted","value","source_file","recompute_expr","recomputed_value","match"))+"\n")
print(f"\nWrote {tsv} ({len(claims)} rows)")

sys.exit(1 if n_no else 0)
