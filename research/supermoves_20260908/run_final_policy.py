"""Serial, CPU-batched 1k research runner with elementary JSONL certificates."""
import argparse,csv,hashlib,json,math,os,time
from pathlib import Path
for variable in ('NUMBA_NUM_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[variable]='1'
from research.supermoves_20260908.final_policy import search
from research.supermoves_20260908.certificate_decoder_fast import decode_elementary,canon_rel
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary as decode_compact
from research.supermoves_20260908.certificate_decoder import replay_elementary
HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int,default=100000)
    p.add_argument('--budget',type=int,default=1000);p.add_argument('--cpu-seconds',type=float,default=2.)
    p.add_argument('--cooldown',type=float,default=.1)
    p.add_argument('--compact-certificates',action='store_true')
    a=p.parse_args()
    if not 1<=a.budget<=1000 or a.offset<0 or a.limit<1 or not math.isfinite(a.cpu_seconds) or not math.isfinite(a.cooldown) or a.cpu_seconds<=0 or a.cooldown<0:raise ValueError('invalid bounded-run parameters')
    if a.output.resolve()==a.input.resolve()or a.output.exists():raise ValueError('output must be new and distinct from input')
    rows=list(csv.DictReader(a.input.open()));seen=set()
    for row in rows:
        if row['name']in seen:raise ValueError('duplicate input ID')
        seen.add(row['name'])
        if any(c not in 'xXyY'for key in ('r1','r2')for c in row[key]):raise ValueError('invalid alphabet')
    source_sha=hashlib.sha256(a.input.read_bytes()).hexdigest()
    sources={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()for name in ('run_final_policy.py','final_policy.py','final_policy_measured.py','plain_search_fast.py','donor_s20_policy.py','strict_donor_route.py','strict_donor_route_fast.py','mid_search.py','root_router.py','certificate_decoder_fast.py','certificate_decoder_compact_moves.py','certificate_words_numba.py','certificate_decoder.py')}
    decoder=decode_compact if a.compact_certificates else decode_elementary
    started=time.perf_counter();search(('xyX','yyx'),budget=5);canon_rel('xy'*40);warmup=time.perf_counter()-started
    selected=rows[a.offset:a.offset+a.limit];counts=dict(rows=0,solves=0,search_wall=0.,search_cpu=0.,certificate_wall=0.,certificate_cpu=0.,charged=0,elementary_moves=0)
    partial=a.output.with_suffix(a.output.suffix+'.partial')
    with partial.open('x')as f:
        for row in selected:
            pair=[row['r1'],row['r2']];start=time.perf_counter();cpu=time.process_time();result=search(pair,budget=a.budget)
            record=dict(name=row['name'],pair=pair,result=result,search_wall=time.perf_counter()-start,search_cpu=time.process_time()-cpu,input_sha256=source_sha,source_sha256=sources,budget=a.budget,certificate_encoding='unary_compact'if a.compact_certificates else 'original')
            if result['solved']:
                start=time.perf_counter();cpu=time.process_time()
                moves=decoder(pair,result['states'],result['steps'],result.get('elementary_tail'))
                assert replay_elementary(pair,moves)==['x','y']
                record.update(elementary_moves=moves,elementary_verified=True,elementary_count=len(moves),certificate_wall=time.perf_counter()-start,certificate_cpu=time.process_time()-cpu)
            assert result['nodes_explored']<=a.budget
            f.write(json.dumps(record)+'\n');f.flush()
            counts['rows']+=1;counts['solves']+=bool(result['solved']);counts['charged']+=result['nodes_explored'];counts['elementary_moves']+=record.get('elementary_count',0)
            for key in ('search_wall','search_cpu','certificate_wall','certificate_cpu'):counts[key]+=record.get(key,0.)
            time.sleep(a.cooldown)
            if counts['search_cpu']+counts['certificate_cpu']>=a.cpu_seconds:break
    os.replace(partial,a.output)
    summary=dict(counts,offset=a.offset,next_offset=a.offset+counts['rows'],input_rows=len(rows),warmup_wall=warmup,source_sha256=sources,input_sha256=source_sha,scope='Fixed donor250/plainS20-prefix872/incumbent remainder; global mixed-unit budget, not equivalent CPU. No relator length cap. Serial CPU batching stops after completed row, not per-row timeout. Search and certificate clocks exclude warmup/cooldown and JSON writing.')
    a.output.with_suffix(a.output.suffix+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items()if k not in ('source_sha256',)}))


if __name__=='__main__':main()
