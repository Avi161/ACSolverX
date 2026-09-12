"""Tiny strict AC replay for the rank-three power-conjugacy corridor; no search."""
from itertools import product
import json


def inv(w):
    return w.swapcase()[::-1]


def red(w):
    out = []
    for a in w:
        assert a in 'xXyYzZ'
        if out and out[-1] == a.swapcase():
            out.pop()
        else:
            out.append(a)
    return ''.join(out)


def pw(w, n):
    return red((w if n >= 0 else inv(w)) * abs(n))


def image(w, images):
    return red(''.join(images[a] if a in images else inv(images[a.swapcase()]) for a in w))


class Trace:
    def __init__(self, words):
        self.start = list(words)
        self.words = [red(w) for w in words]
        self.moves = []
        self.peak = sum(map(len, self.words))

    def step(self, op, i, arg=None):
        if op == 'inv':
            self.words[i] = inv(self.words[i])
        elif op == 'mul':
            assert i != arg
            self.words[i] = red(self.words[i] + self.words[arg])
        else:
            assert op == 'conj' and len(arg) == 1
            self.words[i] = red(inv(arg) + self.words[i] + arg)
        self.moves.append((op, i, arg))
        self.peak = max(self.peak, sum(map(len, self.words)))

    def conj(self, i, w):
        for a in red(w):
            self.step('conj', i, a)

    def append(self, i, j, sign, w):
        donor = self.words[j]
        if sign == -1:
            self.step('inv', j)
        self.conj(j, w)
        self.step('mul', i, j)
        self.conj(j, inv(w))
        if sign == -1:
            self.step('inv', j)
        assert self.words[j] == donor

    def verify(self):
        current = [list(w) for w in self.start]
        def reduce_letters(letters):
            stack = []
            for c in letters:
                if stack and ord(stack[-1]) ^ ord(c) == 32:
                    stack.pop()
                else:
                    stack.append(c)
            return stack
        for op, i, arg in self.moves:
            if op == 'inv':
                current[i] = [c.swapcase() for c in reversed(current[i])]
            elif op == 'mul':
                current[i] = reduce_letters(current[i] + current[arg])
            else:
                current[i] = reduce_letters([arg.swapcase()] + current[i] + [arg])
        assert [''.join(w) for w in current] == self.words


def corridor(m, k, n, seed=False):
    standard = [red('z' + pw('x', m) + pw('y', n)),
                red('Z' + pw('x', -m) + 'yx'),
                red('z' + pw('y', k) + 'Zyx')]
    tr = Trace(['XXZYY', 'XXyxZ', 'XYzYZ'] if seed else standard)
    if seed:
        assert (m, k, n) == (2, 1, 2)
        tr.step('inv', 0)
        tr.conj(0, 'yy')
        tr.conj(1, 'XXyx')
        tr.step('inv', 2)
        assert tr.words == standard
    tr.append(0, 1, 1, pw('x', m) + pw('y', n))
    tr.step('inv', 0)
    tr.conj(0, pw('y', -n))
    assert tr.words[0] == red(pw('x', -m-1) + 'Y' + pw('x', m) + pw('y', -n))
    tr.append(0, 2, 1, 'z' + pw('y', k) + 'Z' + pw('x', m) + pw('y', -n))
    expected = red(pw('x', -m) + 'z' + pw('y', k) + 'Z' + pw('x', m) + pw('y', -n))
    assert tr.words == [expected, *standard[1:]]
    tr.verify()
    forward = {'x':'x', 'y':'y', 'z':pw('x',m)+'z'}
    backward = {'x':'x', 'y':'y', 'z':pw('x',-m)+'z'}
    for a in 'xyz':
        assert image(image(a, forward), backward) == a
        assert image(image(a, backward), forward) == a
    transformed = [image(w, forward) for w in tr.words]
    assert transformed == [red('z'+pw('y',k)+'Z'+pw('y',-n)),
                           red('Z'+pw('x',-2*m)+'yx'),
                           red(pw('x',m)+'z'+pw('y',k)+'Z'+pw('x',-m)+'yx')]
    after = Trace(transformed)
    after.append(2, 0, -1, pw('y', n)+pw('x', -m)+'yx')
    assert after.words[2] == red(pw('x',m)+pw('y',n)+pw('x',-m)+'yx')
    # Replace the third relator by C I^-1 using temporary inversion of I.
    after.append(2, 1, -1, '')
    assert after.words[2] == red(pw('x',m)+pw('y',n)+pw('x',m)+'z')
    after.verify()
    out = {'parameters':[m,k,n], 'initial':tr.start, 'ordinary_endpoint':tr.words,
           'ordinary_moves':len(tr.moves), 'ordinary_peak_all_relator_length':tr.peak,
           'coordinate_endpoint':transformed,
           'final_endpoint':after.words, 'final_total':sum(map(len,after.words)),
           'post_coordinate_moves':len(after.moves),
           'post_coordinate_peak_all_relator_length':after.peak,
           'stable_coordinate_elementary_expansion':'not emitted or peak-bounded'}
    if seed:
        out['ordinary_move_stream'] = tr.moves
        out['post_coordinate_move_stream'] = after.moves
    return out


if __name__ == '__main__':
    cases = [corridor(m,k,n) for m,k,n in product(range(-2,4),range(-2,4),range(-2,4))]
    seed = corridor(2,1,2,True)
    print(json.dumps({'signed_identity_replays':len(cases), 'aca_24':seed},indent=2))
