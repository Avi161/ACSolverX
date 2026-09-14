"""Literal root-only algebra checks; no search or imported research kernels."""
from pathlib import Path
import csv, json, hashlib, time
BASE=Path('/Users/avigyapaudel/Documents/surf/ACSolverX')
OUT=Path(__file__).parent

def inv(w):return w.swapcase()[::-1]
def red(w):
 s=[]
 for c in w:
  if s and s[-1]==c.swapcase():s.pop()
  else:s.append(c)
 return ''.join(s)
def power(w,n):return (w*n) if n>=0 else (inv(w)*(-n))
def exp(w,t):return w.count(t)-w.count(t.upper())
def ired(w):
 s=[]
 for i,e in w:
  if s and s[-1]==(i,-e):s.pop()
  else:s.append((i,e))
 return s
def collect(w,t):
 h=0;s=[]
 for c in w:
  if c==t:h+=1
  elif c==t.upper():h-=1
  else:s.append((h,1 if c.islower() else -1))
 return ired(s),h
def shift(w,q):return [(i+q,e) for i,e in w]
def iinv(w):return [(i,-e) for i,e in reversed(w)]
def expand(w,t):
 z='y' if t=='x' else 'x'
 return red(''.join(power(t,i)+power(z,e)+power(t,-i) for i,e in w))
def replay(pair,moves):
 p=list(pair)
 for kind,j,v in moves:
  if kind=='I':p[j]=inv(p[j])
  elif kind=='C':p[j]=red(inv(v)+p[j]+v)
  else:p[j]=red(p[j]+p[1-j])
 return p

def pass_boundary(r0,s0,t,side):
 e=exp(r0,t);r=power(r0,e);f,k=collect(r,t);g,l=collect(s0,t)
 assert k==1 and l==0
 a,b=min(i for i,e in f),max(i for i,e in f)
 c,d=min(i for i,e in g),max(i for i,e in g)
 assert b-a<d-c
 q=c+1-a;fq=shift(f,q);direction=1 if side=='lower' else -1
 boundary=c if direction==1 else d
 moves=[];ledgers=[];uses=0
 while any(i==boundary for i,e in g):
  pos=next(j for j,(i,e) in enumerate(g) if i==boundary)
  stop=pos+1
  while stop<len(g) and g[stop][0]==boundary:stop+=1
  h=g[pos:stop];post=g[stop:];H=expand(h,t);Q=expand(post,t)
  c1=red(power(t,-q)+H+Q);c2=red(power(t,-q)+Q)
  old=expand(g,t)
  if direction==1:newh=ired(fq+shift(h,1)+iinv(fq))
  else:
   fm=shift(fq,-1);newh=ired(iinv(fm)+shift(h,-1)+fm)
  g=ired(g[:pos]+newh+post);new=expand(g,t)
  factor=red(inv(c1)+power(r0,e*direction)+c1+inv(c2)+power(r0,-e*direction)+c2)
  assert red(inv(old)+new)==factor
  for sign,conj in [(e*direction,c1),(-e*direction,c2)]:
   if sign==-1:moves.append(('I',0,''))
   moves.extend(('C',0,ch) for ch in conj)
   moves.append(('M',1,''))
   moves.extend(('C',0,ch.swapcase()) for ch in reversed(conj))
   if sign==-1:moves.append(('I',0,''))
  ledgers.append({'H':H,'Q':Q,'c1':c1,'c2':c2,'sign1':e*direction})
  uses+=2
 result=expand(g,t);pair=replay((r0,s0),moves)
 assert pair==[r0,result]
 ns=(max(i for i,e in g)-min(i for i,e in g)) if g else None
 assert ns is None or ns<d-c
 return {'direction':side,'q':q,'result':result,'before_span':d-c,'after_span':ns,'before_length':len(s0),'after_length':len(result),'source_uses':uses,'elementary_moves':len(moves),'ledgers':ledgers,'moves':moves,'independent_replay':True}

def main():
 path=BASE/'data/ms_unsolved_reps/aca_124_best.csv';records=[];start=time.perf_counter()
 for row in csv.DictReader(path.open()):
  for j in range(2):
   r,s=row['r'+str(j+1)],row['r'+str(2-j)]
   for t in 'xy':
    e=exp(r,t)
    if abs(e)!=1 or exp(s,t):continue
    f,_=collect(power(r,e),t);g,_=collect(s,t)
    if not f or not g:continue
    fs=max(i for i,e in f)-min(i for i,e in f);gs=max(i for i,e in g)-min(i for i,e in g)
    if fs>=gs:continue
    records.append({'name':row['name'],'source_index':j,'source':r,'target':s,'stable':t,'source_sign':e,'source_span':fs,'target_span':gs,'passes':[pass_boundary(r,s,t,side) for side in ['lower','upper']]})
 report={'input':str(path),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'oriented_matches':len(records),'distinct_rows':len(set(r['name'] for r in records)),'verified_passes':2*len(records),'wall_seconds':time.perf_counter()-start,'records':records}
 (OUT/'astra_boundary_checks.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
 for rec in records:
  if rec['name'] in ['aca_1','aca_4','aca_118']:
   print(json.dumps({**{k:v for k,v in rec.items() if k!='passes'},'passes':[{k:v for k,v in p.items() if k not in ['moves','ledgers']} for p in rec['passes']]}))
if __name__=='__main__':main()
