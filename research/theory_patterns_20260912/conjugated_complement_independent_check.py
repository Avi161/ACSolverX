"""Small adversarial checks with an independent graph implementation."""

import itertools
import json
from pathlib import Path
from time import perf_counter


def inverse(w):
    return w.swapcase()[::-1]


def reduce_word(w):
    stack=[]
    for c in w:
        if stack and stack[-1] == c.swapcase(): stack.pop()
        else: stack.append(c)
    return ''.join(stack)


def fold(arcs, vertices, merge=None):
    classes=[{v} for v in range(vertices)]
    def owner(v):
        return next(i for i,s in enumerate(classes) if v in s)
    def combine(i,j):
        if i==j: return
        classes[min(i,j)] |= classes[max(i,j)]
        del classes[max(i,j)]
    if merge: combine(owner(merge[0]),owner(merge[1]))
    while True:
        mapped={(owner(u),c,owner(v)) for u,c,v in arcs}
        conflict=None
        lookup={}
        for u,c,v in sorted(mapped):
            if (u,c) in lookup and lookup[u,c] != v:
                conflict=(lookup[u,c],v); break
            lookup[u,c]=v
        if conflict is None: break
        combine(*conflict)
    root=owner(0)
    alive={root}|{v for u,c,w in mapped for v in (u,w)}
    while True:
        leaf=next((v for v in alive if v!=root and sum(u==v for u,c,w in mapped)<=1),None)
        if leaf is None: break
        mapped={a for a in mapped if leaf not in (a[0],a[2])}
        alive.remove(leaf)
    names={root:0}
    queue=[root]
    for u in queue:
        for a,c,v in sorted(mapped,key=lambda e:(e[1],e[2])):
            if a==u and v not in names:
                names[v]=len(names); queue.append(v)
    return tuple(sorted((names[u],c,names[v]) for u,c,v in mapped))


def graph(words):
    edges=[]; count=1
    for w in words:
        w=reduce_word(w); current=0
        for i,c in enumerate(w):
            target=0 if i==len(w)-1 else count
            if target: count+=1
            edges.extend(((current,c,target),(target,c.swapcase(),current)))
            current=target
    return fold(edges,count)


ROSE=tuple(sorted((0,c,0) for c in 'xXyY'))


def complement(g):
    n=1+max((max(u,v) for u,c,v in g),default=0)
    if n==1:
        return len(g)>=2,0
    tries=0
    for u,v in itertools.combinations(range(n),2):
        tries+=1
        if fold(g,n,(u,v))==ROSE: return True,tries
    return False,tries


def finite(pair):
    seen=set(); tries=0
    for i in range(len(pair[0])):
        for j in range(len(pair[1])):
            g=graph((pair[0][i:]+pair[0][:i],pair[1][j:]+pair[1][:j]))
            if g in seen: continue
            seen.add(g)
            answer,cost=complement(g); tries+=cost
            if answer: return True,tries
    return False,tries


def main():
    cases=[('xxyXY','yyxYX'),('xxyXY','xxYYY'),('xxyXY','xyyXY'),
           ('xx','yyy'),('xxyyy','xxxyy'),('xyXY','xxyXY'),('xxyy','xxxYYY'),
           ('xyXY','xxyy'),('x','y'),('xyXY','yxyxYX')]
    conjugators=['']
    for n in range(1,4):
        conjugators += [''.join(x) for x in itertools.product('xXyY',repeat=n)
                        if all(x[i]!=x[i+1].swapcase() for i in range(n-1))]
    start=perf_counter(); results=[]; attachment_checks=direct_checks=0
    for pair in cases:
        assert all(w==reduce_word(w) and w[0]!=w[-1].swapcase() for w in pair)
        attached,cost=finite(pair); attachment_checks+=cost
        direct=[]
        if not attached:
            for c in conjugators:
                answer,cost=complement(graph((pair[0],inverse(c)+pair[1]+c)))
                direct_checks+=cost
                direct.append({'c':c,'cyclic_complement':answer})
                assert not answer,('counterexample',pair,c)
        results.append({'pair':pair,'finite_attachment_positive':attached,
                        'direct_conjugator_checks':direct})
    # Explicit shortest-path sign tests, independent of the author's helper.
    signed_checks=0
    for r,s in cases:
        for i in range(len(r)):
            for j in range(len(s)):
                p=min((r[:i],inverse(r[i:])),key=lambda w:(len(w),w))
                q=min((s[:j],inverse(s[j:])),key=lambda w:(len(w),w))
                assert reduce_word(inverse(p)+r+p)==r[i:]+r[:i]
                assert reduce_word(inverse(q)+s+q)==s[j:]+s[:j]
                c=reduce_word(q+inverse(p))
                assert len(c)<=len(r)//2+len(s)//2
                assert graph((r,inverse(c)+s+c))==graph((r,p+inverse(q)+s+q+inverse(p)))
                signed_checks+=1
    report={'status':'PASS','scope':'small counterexample and sign checks; unbounded claim is proof-reviewed',
            'cases':results,'attachment_vertex_pair_checks':attachment_checks,
            'direct_vertex_pair_checks':direct_checks,'signed_attachment_checks':signed_checks,
            'wall_seconds':perf_counter()-start}
    output=Path(__file__).with_name('conjugated_complement_independent_audit.json')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'}))


if __name__=='__main__': main()
