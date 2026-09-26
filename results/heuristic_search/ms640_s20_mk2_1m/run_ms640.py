import sys, csv, json, os, multiprocessing as mp
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","..")); sys.path.insert(0, ROOT)
from experiments.search.run_leftovers_1m import _run_greedy, _run_s20_mk2
D=sys.argv[1]; arm=sys.argv[2]; cap=int(sys.argv[3]); B=10**6
rows=list(csv.DictReader(open(D)))
f={"greedy":_run_greedy,"s20_mk2":_run_s20_mk2}[arm]
def job(r):
    o=f(r["r1"],r["r2"],B,cap)
    return {"pres_id":int(r["pres_id"]),"solved":bool(o["solved"]),"nodes":int(o["nodes_explored"]),"path":o["path_length"]}
if __name__=="__main__":
    out=os.path.join(os.path.dirname(__file__),f"ms640_{arm}_cap{cap}.jsonl")
    with mp.Pool(6) as p, open(out,"w") as fh:
        for res in p.imap_unordered(job, rows, chunksize=4):
            fh.write(json.dumps(res)+"\n"); fh.flush()
