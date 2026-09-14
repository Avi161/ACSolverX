"""Search-free elementary checks for the MS two-stable-letter identities."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def inv(w):
    return w.swapcase()[::-1]


def red(w):
    out = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return ''.join(out)


def power(c, n):
    return (c if n >= 0 else c.swapcase()) * abs(n)


def core(w):
    w = red(w)
    c = ''
    while len(w) > 1 and w[0] == w[-1].swapcase():
        c += w[0]
        w = w[1:-1]
    return c, w


def witness(source, target):
    """Return sign,c with target=c^-1 source^sign c, or None."""
    a, u = core(source)
    b, v = core(target)
    for sign in (1, -1):
        z = u if sign == 1 else inv(u)
        for cut in range(max(1, len(z))):
            if z[cut:] + z[:cut] == v:
                c = red(a + z[:cut] + inv(b))
                if red(inv(c) + (source if sign == 1 else inv(source)) + c) == red(target):
                    return sign, c
    return None


class Elementary:
    def __init__(self, pair):
        self.initial = list(map(red, pair))
        self.pair = self.initial[:]
        self.moves = []
        self.peak = max(map(len, self.pair))

    def emit(self, op, i, arg=None):
        if op == 'invert':
            self.pair[i] = inv(self.pair[i])
        elif op == 'conjugate':
            assert len(arg) == 1
            self.pair[i] = red(arg.swapcase() + self.pair[i] + arg)
        elif op == 'multiply':
            assert arg == 1-i
            self.pair[i] = red(self.pair[i] + self.pair[arg])
        else:
            raise ValueError(op)
        self.moves.append([op, i, arg])
        self.peak = max(self.peak, *(len(w) for w in self.pair))

    def orient(self, i, target):
        target = red(target)
        found = witness(self.pair[i], target)
        assert found is not None, (self.pair[i], target, 'unary mismatch')
        sign, c = found
        if sign < 0:
            self.emit('invert', i)
        for letter in c:
            self.emit('conjugate', i, letter)
        assert self.pair[i] == target

    def replace(self, i, target):
        target = red(target)
        delta = red(inv(self.pair[i]) + target)
        if not delta:
            return
        saved = self.pair[1-i]
        found = witness(saved, delta)
        assert found is not None, (self.pair, target, delta, 'donor mismatch')
        self.orient(1-i, delta)
        self.emit('multiply', i, 1-i)
        self.orient(1-i, saved)
        assert self.pair[i] == target

    def replay(self):
        state = self.initial[:]
        for op, i, arg in self.moves:
            if op == 'invert':
                state[i] = ''.join(c.swapcase() for c in state[i][::-1])
            elif op == 'conjugate':
                state[i] = freely_reduce_independent(arg.swapcase() + state[i] + arg)
            elif op == 'multiply':
                state[i] = freely_reduce_independent(state[i] + state[arg])
            else:
                raise AssertionError(op)
        assert state == self.pair
        return state


def freely_reduce_independent(w):
    while True:
        before = w
        for a in 'xXyY':
            w = w.replace(a + a.swapcase(), '')
        if before == w:
            return w


def R(n):
    return 'X' + power('y', n) + 'x' + power('y', -n-1)


def S(k, r, s):
    return red('X' + power('y', -k) + 'X' + power('y', r) + 'x' + power('y', s))


def shift(e, n, k, r, s):
    assert e.pair == [R(n), S(k,r,s)]
    e.orient(1, power('y',k)+'x'+power('y',-s)+'X'+power('y',-r)+'x')
    e.replace(1, power('y',k-n)+'x'+power('y',n+1-s)+'X'+power('y',-r)+'x')
    e.orient(1, power('y',r)+'x'+power('y',s-n-1)+'X'+power('y',n-k)+'X')
    e.replace(1, power('y',r-n)+'x'+power('y',s)+'X'+power('y',n-k)+'X')
    e.orient(1, power('y',n-k)+'X'+power('y',r-n)+'x'+power('y',s)+'X')
    e.replace(1, power('y',-k-1)+'X'+power('y',r)+'x'+power('y',s)+'X')
    e.orient(1, S(k+1,r,s))


def reverse_into(e, forward):
    assert e.pair == forward.pair
    for op,i,arg in reversed(forward.moves):
        if op == 'invert':
            e.emit('invert',i)
        elif op == 'conjugate':
            e.emit('conjugate',i,arg.swapcase())
        else:
            e.emit('invert',arg)
            e.emit('multiply',i,arg)
            e.emit('invert',arg)
    assert e.pair == forward.initial


def set_k(e,n,k,r,s,target):
    while k < target:
        shift(e,n,k,r,s)
        k += 1
    while k > target:
        forward = Elementary([R(n),S(k-1,r,s)])
        shift(forward,n,k-1,r,s)
        reverse_into(e,forward)
        k -= 1
    return k


def lower_s(e,n,k,r,s):
    e.orient(1, 'x'+power('y',s)+'X'+power('y',-k)+'X'+power('y',r))
    e.replace(1, 'x'+power('y',s-n-1)+'X'+power('y',n-k)+'X'+power('y',r))
    e.orient(1,S(k-n,r,s-n-1))
    return k-n,r,s-n-1


def lower_r(e,n,k,r,s):
    e.replace(1,S(k,r-n,s+n+1))
    return lower_s(e,n,k,r-n,s+n+1)


def normalize(e,n,k,r,s,rr,ss):
    assert (r-rr)%n == 0 and (s-ss)%(n+1) == 0
    while r > rr:
        k,r,s = lower_r(e,n,k,r,s)
    while r < rr:
        forward = Elementary([R(n),S(k+n,r+n,s)])
        lower_r(forward,n,k+n,r+n,s)
        reverse_into(e,forward)
        k,r = k+n,r+n
    while s > ss:
        k,r,s = lower_s(e,n,k,r,s)
    while s < ss:
        forward = Elementary([R(n),S(k+n,r,s+n+1)])
        lower_s(forward,n,k+n,r,s+n+1)
        reverse_into(e,forward)
        k,s = k+n,s+n+1
    set_k(e,n,k,r,s,0)
    return 0,r,s


def primitive_cleanup(e, i, a, b):
    e.orient(i,core(e.pair[i])[1])
    z=e.pair[i]
    assert z.count(b)+z.count(b.swapcase()) == 1
    if z.count(b.swapcase()):
        e.emit('invert',i)
        z=e.pair[i]
    cut=z.index(b)
    e.orient(i,z[cut:]+z[:cut])
    q=e.pair[i][1:].count(a)-e.pair[i][1:].count(a.swapcase())
    assert e.pair[i] == b+power(a,q)
    j=1-i
    while any(c.lower()==b.lower() for c in e.pair[j]):
        word=e.pair[j]
        pos=next(p for p,c in enumerate(word) if c.lower()==b.lower())
        replacement=power(a,-q if word[pos]==b else q)
        e.replace(j,word[:pos]+replacement+word[pos+1:])
    e.orient(j,a)
    while any(c.lower()==a.lower() for c in e.pair[i]):
        word=e.pair[i]
        pos=next(p for p,c in enumerate(word) if c.lower()==a.lower())
        e.replace(i,word[:pos]+word[pos+1:])
    assert e.pair[i]==b and e.pair[j]==a


def bs12_cleanup(e, donor, a, b):
    e.orient(donor,b.swapcase()+a+b+a.swapcase()*2)
    i=1-donor
    while e.pair[i].count(b)+e.pair[i].count(b.swapcase())>1:
        word=e.pair[i]
        found=None
        for cut in range(len(word)):
            z=word[cut:]+word[:cut]
            if not z.startswith(b.swapcase()):
                continue
            end=1
            while end<len(z) and z[end].lower()==a.lower():
                end+=1
            if end>1 and end<len(z) and z[end]==b:
                found=z
                break
        assert found is not None,(e.pair,'missing BS(1,2) pinch')
        e.orient(i,found)
        while True:
            z=e.pair[i]
            if b.swapcase() not in z:
                break
            pos=z.index(b.swapcase())
            if pos+1>=len(z) or z[pos+1].lower()!=a.lower():
                break
            letter=z[pos+1]
            e.replace(i,z[:pos]+letter*2+b.swapcase()+z[pos+2:])
    primitive_cleanup(e,i,a,b)


def swap_relators(e):
    e.emit('multiply',0,1)
    e.emit('invert',0)
    e.emit('multiply',1,0)
    e.emit('invert',0)
    e.emit('invert',0)
    e.emit('invert',1)
    e.emit('multiply',0,1)
    e.emit('invert',0)
    e.emit('invert',1)
    e.emit('invert',1)


def finish_xy(e):
    assert sorted(w.lower() for w in e.pair)==['x','y']
    for i in (0,1):
        if e.pair[i].isupper():
            e.emit('invert',i)
    if e.pair==['y','x']:
        swap_relators(e)
    assert e.pair==['x','y']


def terminal_residues(n,r,s):
    if r%n==0:
        return 0,s%(n+1)
    if s%(n+1)==0:
        return r%n,0
    for epsilon in (-1,1):
        if (r-epsilon)%n==0 and (s+epsilon)%(n+1)==0:
            return epsilon,-epsilon
    return None


def solve(n,k,r,s):
    residues=terminal_residues(n,r,s)
    assert residues is not None
    e=Elementary([R(n),S(k,r,s)])
    _,rr,ss=normalize(e,n,k,r,s,*residues)
    if rr==0 or ss==0:
        primitive_cleanup(e,1,'y','X')
    else:
        bs12_cleanup(e,1,'x',power('y',-rr))
    finish_xy(e)
    assert e.replay()==['x','y']
    return e


def cyclic_variants(w):
    w=core(w)[1]
    for z in (w,inv(w)):
        for k in range(max(1,len(z))):
            yield z[k:]+z[:k]


def canon(w):
    return min(cyclic_variants(w))


def scan_table(path):
    matches=[]
    rows=list(csv.DictReader(path.open()))
    for row in rows:
        for di in (0,1):
            for base in 'xXyY':
                for stable in 'xXyY':
                    if base.lower()==stable.lower():
                        continue
                    trans=str.maketrans({base:'y',base.swapcase():'Y',stable:'x',stable.swapcase():'X'})
                    donor=row[f'r{di+1}'].translate(trans)
                    companion=row[f'r{2-di}'].translate(trans)
                    n=(len(core(donor)[1])-3)//2
                    ns=[n] if n>=1 and canon(donor)==canon(R(n)) else []
                    for n in ns:
                        if companion.count('x')+companion.count('X')==1:
                            matches.append(dict(name=row['name'],n=n,terminal=True,kind='one_stable_letter',donor_index=di,base=base,stable=stable))
                            continue
                        for z in cyclic_variants(companion):
                            if z.count('x')+z.count('X') != 3 or z.count('X')!=2:
                                continue
                            if not z.startswith('X'):
                                continue
                            import re
                            m=re.fullmatch('X([yY]*)X([yY]*)x([yY]*)',z)
                            if m is None:
                                continue
                            a,b,c=(q.count('y')-q.count('Y') for q in m.groups())
                            k,r,s=-a,b,c
                            terminal = r%n == 0 or s%(n+1) == 0 or any((r-epsilon)%n==0 and (s+epsilon)%(n+1)==0 for epsilon in (-1,1))
                            item=dict(name=row['name'],n=n,k=k,r=r,s=s,residues=[r%n,s%(n+1)],terminal=terminal,donor_index=di,base=base,stable=stable)
                            if item not in matches:
                                matches.append(item)
    return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),row_count=len(rows),matches=matches,matched_ids=sorted({m['name'] for m in matches}),terminal_ids=sorted({m['name'] for m in matches if m['terminal']}))


def main():
    checks=[]
    for n,k,r,s in [(2,1,1,1),(2,-3,5,4),(2,3,-5,-4),(3,2,1,-1),(3,-2,-2,3),(5,4,6,5),(2,0,0,0),(1,3,-2,5)]:
        e=Elementary([R(n),S(k,r,s)])
        shift(e,n,k,r,s)
        assert e.replay()==[R(n),S(k+1,r,s)]
        f=Elementary([R(n),S(k,r,s)])
        rr=r%n
        ss=s%(n+1)
        normalize(f,n,k,r,s,rr,ss)
        assert f.replay()==[R(n),S(0,rr,ss)]
        checks.append(dict(parameters=[n,k,r,s],shift_moves=len(e.moves),normalization_moves=len(f.moves),peak=f.peak))
    completed=[]
    for n,k,r,s in [(2,1,1,1),(2,-3,5,4),(2,3,-5,-4),(3,2,1,-1),(3,-2,-2,3),(5,4,6,5),(2,0,0,0),(1,3,-2,5)]:
        e=solve(n,k,r,s)
        completed.append(dict(parameters=[n,k,r,s],initial=e.initial,moves=e.moves,move_count=len(e.moves),peak=e.peak,endpoint=e.pair))
    scans=[scan_table(ROOT/'data/ms_unsolved_reps'/f'aca_124_{name}.csv') for name in ('initial','best')]
    output=dict(identity_checks=checks,full_certificates=completed,u124_scans=scans,heap_nodes=0)
    (HERE/'ms_family_checks.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(checks=len(checks),completed=[dict(parameters=c['parameters'],moves=c['move_count'],peak=c['peak']) for c in completed],scans=[dict(input=x['path'],matches=x['matched_ids'],terminal=x['terminal_ids']) for x in scans]),indent=2))


if __name__=='__main__':
    main()
