"""Small release smoke test; three saved donor solves and no large searches."""
import argparse,csv,hashlib,json,os,time
from pathlib import Path
for variable in ('NUMBA_NUM_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[variable]='1'
from research.supermoves_20260908.final_policy import search
from research.supermoves_20260908.final_policy_measured import search as measured
from research.supermoves_20260908.certificate_decoder_fast import decode_elementary
from research.supermoves_20260908.certificate_decoder import replay_elementary
HERE=Path(__file__).resolve().parent


def strip_clocks(value):
    if isinstance(value,dict):return {k:strip_clocks(v)for k,v in value.items()if not k.endswith(('_wall','_cpu','_seconds'))}
    if isinstance(value,list):return [strip_clocks(v)for v in value]
    return value


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'FINAL_RELEASE_CHECK.json');a=p.parse_args()
    table=json.loads((HERE/'DONOR_FIRST_VALIDATION_200_RESULTS.json').read_text())
    names=[r['name']for r in table['rows']if r['solved']and r['route']=='strict_donor'][:3]
    inputs={r['name']:[r['r1'],r['r2']]for r in csv.DictReader((HERE/'donor_first_validation_200.csv').open())}
    rows=[]
    for name in names:
        original=measured(inputs[name],budget=1000);optimized=search(inputs[name],budget=1000)
        assert strip_clocks(original)==strip_clocks(optimized),name
        assert optimized['solved']and optimized['nodes_explored']<=1000
        moves=decode_elementary(inputs[name],optimized['states'],optimized['steps'],optimized.get('elementary_tail'))
        assert replay_elementary(inputs[name],moves)==['x','y']
        rows.append(dict(name=name,charged=optimized['nodes_explored'],elementary_moves=len(moves)))
        time.sleep(.1)
    terminal=search(('x','y'),budget=1);assert terminal['solved']and terminal['nodes_explored']==1
    output=dict(passed=True,rows=rows,measured_and_current_policy_equal=True,terminal_budget1=True,scope='Three known donor-route solves with exact non-clock output comparison and independent original-input elementary replay; no full performance suite.')
    a.output.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))


if __name__=='__main__':main()
