"""Four exact roots plus the aca_9 saved stall; finite algebra, no heap."""
from pathlib import Path
import csv,json,time,importlib.util
P=Path(__file__).parent
spec=importlib.util.spec_from_file_location('astra_base',P/'astra_boundary_probe.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def bounds(f):
 return (min(i for i,e in f),max(i for i,e in f)) if f else None

def span(f):
 b=bounds(f);return b[1]-b[0] if b else 0

def exchange(r,s,t,q,k,donor_sign=1):
 e=w.exp(r,t);nr=w.power(r,e);ns=w.red(w.power(t,q)+w.power(s,donor_sign)+w.power(t,-q))
 f,_=w.collect(nr,t);g,_=w.collect(ns,t);h=w.ired(w.iinv(g)+f);b=w.ired(f+w.shift(w.iinv(h),-k))
 a=w.red(w.inv(ns)+nr);B=w.red(nr+w.power(t,-k)+w.inv(a)+w.power(t,k))
 assert a==w.red(w.expand(h,t)+t) and B==w.expand(b,t)
 moves=[]
 if e==-1:moves.append(('I',0,''))
 if donor_sign==-1:moves.append(('I',1,''))
 conj=w.power(t,-q)
 moves.extend(('C',1,ch) for ch in conj)
 moves.extend([('I',0,''),('M',0,''),('I',0,''),('M',1,''),('I',0,'')])
 conj=w.power(t,k)
 moves.extend(('C',0,ch) for ch in conj)
 moves.append(('M',1,''));moves.extend(('C',0,ch.swapcase()) for ch in reversed(conj));moves.append(('I',0,''))
 return {'donor_sign':donor_sign,'q':q,'k':k,'after':[a,B],'source_span':span(h),'donor_span':span(b),'Phi':span(h)+span(b),'elementary_count':len(moves),'moves':moves}

def frame(name,r,s,t):
 f,_=w.collect(w.power(r,w.exp(r,t)),t);g,_=w.collect(s,t);a,b=bounds(f);c,d=bounds(g);phi=span(f)+span(g)
 candidates=[];wide=[]
 for sign in [-1,1]:
  ge=g if sign==1 else w.iinv(g)
  if f[0][1]==ge[0][1]:
   q=f[0][0]-ge[0][0];h=w.ired(w.iinv(w.shift(ge,q))+f)
   if not h:ks={0}
   else:
    u,v=bounds(h);ks={0,u-a,v-b,h[-1][0]-f[-1][0],-1,1}
   for k in sorted(ks):candidates.append(exchange(r,s,t,q,k,sign))
  for q in range(a-d-phi,b-c+phi+1):
   h=w.ired(w.iinv(w.shift(ge,q))+f)
   if not h:
    wide.append(exchange(r,s,t,q,0,sign));continue
   if span(h)>=phi:continue
   u,v=bounds(h)
   for k in range(u-b-phi,v-a+phi+1):wide.append(exchange(r,s,t,q,k,sign))
 for coupled_only in [False,True]:
  assert any(x['Phi']<phi and (not coupled_only or x['k']!=0) for x in candidates)==any(x['Phi']<phi and (not coupled_only or x['k']!=0) for x in wide)
 for rec in candidates:assert w.replay((r,s),rec['moves'])==rec['after']
 best=min(candidates,key=lambda r:(r['Phi'],sum(map(len,r['after'])),r['elementary_count'])) if candidates else None
 return {'name':name,'before':[r,s],'stable':t,'Phi_before':phi,'breakpoint_candidates':len(candidates),'wide_candidates_checked':len(wide),'strict_descent_count':sum(x['Phi']<phi for x in candidates),'best':best}

def main():
 start=time.perf_counter();records=[]
 data=Path('/Users/avigyapaudel/Documents/surf/ACSolverX/data/ms_unsolved_reps/aca_124_best.csv')
 rows={x['name']:x for x in csv.DictReader(data.open())}
 for name in ['aca_1','aca_4','aca_9','aca_117']:
  row=rows[name]
  for r,s in [(row['r1'],row['r2']),(row['r2'],row['r1'])]:
   for t in 'xy':
    if abs(w.exp(r,t))==1 and w.exp(s,t)==0:records.append(frame(name,r,s,t))
 records.append(frame('aca_9_saved_residue_stall','xYYXyxxyy','YXXXyxx','y'))
 planted=[]
 for m in [2,3,5]:
  for t in 'xy':
   h=[(0,1),(1,1),(0,-1),(1,-1)];g=[(0,1),(0,1),(m,-1)];f=g+h
   r=w.red(w.expand(f,t)+t);s0=w.expand(g,t);rec=exchange(r,s0,t,0,-1)
   assert rec['Phi']==m+1 and rec['Phi']<2*m
   assert w.replay((r,s0),rec['moves'])==rec['after']
   planted.append({'m':m,'stable':t,'Phi_before':2*m,'Phi_after':rec['Phi'],'verified':True})
 out={'planted_checks':planted,'status':'finite_coupled_exchange_descent_probe','scope':'four roots and saved aca9 residue stall; no cohort search','records':records,'wall_seconds':time.perf_counter()-start}
 (P/'coupled_boundary_next_check.json').write_text(json.dumps(out,indent=2)+'\n')
 for r in records:
  print(json.dumps({k:v for k,v in r.items() if k!='best'}|{'best':None if r['best'] is None else {k:v for k,v in r['best'].items() if k!='moves'}}))
 print('wall',out['wall_seconds'])
if __name__=='__main__':main()
