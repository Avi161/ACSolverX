import csv,hashlib,json,tempfile
from pathlib import Path
from research.supermoves_20260908.summarize_full_ac19_final1k import summarize

HERE=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(dir=HERE) as temporary:
    root=Path(temporary);input_path=root/'input.csv';result=root/'results';result.mkdir()
    input_path.write_text('name,r1,r2\nac19_0,x,y\nac19_1,xx,y\nac19_2,xy,y\n')
    digest=hashlib.sha256(input_path.read_bytes()).hexdigest();source={'f.py':'abc'}
    manifest=dict(input_sha256=digest,population=3,budget=1000,cap=None,threads=1,
                  source_sha256=source,offset=0,end=3)
    (result/'manifest_00000_00003.json').write_text(json.dumps(manifest))
    rows=[dict(index=0,name='ac19_0',pair=['x','y'],budget=1000,solved=True,
               nodes_explored=1,route='plain_s20',elementary_verified=True,elementary_count=0,
               search_wall=.1,search_cpu=.09,certificate_wall=.01,certificate_cpu=.01),
          dict(index=1,name='ac19_1',pair=['xx','y'],budget=1000,solved=False,
               nodes_explored=1000,route='incumbent_restart'),
          dict(index=2,name='ac19_2',pair=['xy','y'],budget=1000,solved=True,
               nodes_explored=2,route='strict_donor',elementary_verified=True,elementary_count=4)]
    with (result/'rows_00000_00003.jsonl').open('w') as stream:
        for row in rows:stream.write(json.dumps(row)+'\n')
    (result/'rows_00000_00003.summary.json').write_text(json.dumps(
        dict(manifest='manifest_00000_00003.json',next_offset=3,elapsed=2.,warmup_wall=.2,cooldown_wall=1.,
             rows=3,solved=2,verified=2,errors=0,nodes=1003,elementary_moves=4,
             search_wall=.1,search_cpu=.09,certificate_wall=.01,certificate_cpu=.01)))
    summary=summarize(input_path,result,expected_count=3,expected_sha=digest)
    assert (summary['solved'],summary['unsolved'],summary['nodes'])==(2,1,1003)
    assert summary['verified']==2
    assert summary['routes']=={
        'plain_s20':{'rows':1,'solved':1,'unsolved':0},
        'strict_donor':{'rows':1,'solved':1,'unsolved':0},
        'incumbent_restart':{'rows':1,'solved':0,'unsolved':1}}
    assert (result/'SUMMARY.json').exists() and (result/'RESULTS.md').exists() and (result/'unsolved.csv').exists()
    report=(result/'RESULTS.md').read_text()
    assert 'including **1.000000s** recorded cooldown and excluding warmup' in report
    assert 'elapsed plus warmup: **2.200000s**' in report
    assert '| `plain_s20` | 1 | 1 | 0 |' in report
    assert 'verified certificates: **2**' in report
    assert '../../../data/AC19_extended_aut_min.csv' in report
    assert summary['invocation_runtime']['execution_plus_warmup_wall']==2.2

with tempfile.TemporaryDirectory(dir=HERE) as temporary:
    root=Path(temporary);input_path=root/'input.csv';result=root/'results';result.mkdir()
    input_path.write_text('name,r1,r2\nac19_0,x,y\nac19_1,xx,y\n')
    digest=hashlib.sha256(input_path.read_bytes()).hexdigest()
    (result/'manifest_00000_00002.json').write_text(json.dumps(dict(
        input_sha256=digest,population=2,budget=1000,cap=None,threads=1,
        source_sha256={'f':'a'},offset=0,end=2)))
    (result/'rows_00000_00001.jsonl').write_text(json.dumps(dict(
        index=0,name='ac19_0',pair=['x','y'],budget=1000,solved=False,
        nodes_explored=1,route='plain'))+'\n')
    progress=summarize(input_path,result,expected_count=2,expected_sha=digest,allow_incomplete=True)
    assert progress['provisional'] and progress['rows']==1 and progress['next_missing']==1
    assert not (result/'SUMMARY.json').exists() and not (result/'RESULTS.md').exists()

print(json.dumps({'complete_fixture':True,'incomplete_writes_no_final_files':True}))
