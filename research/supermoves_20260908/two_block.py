"""Deterministic elementary AC certificates for unimodular two-block pairs."""
from collections import deque


def inverse(word):
    return word[::-1].swapcase()


def reduce_word(word):
    stack = []
    for letter in word:
        if letter not in 'xXyY':
            raise ValueError('words must use xXyY')
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return ''.join(stack)


def power(letter, exponent):
    return (letter if exponent >= 0 else letter.swapcase()) * abs(exponent)


def block(m, n):
    return power('x', m) + power('y', n)


def replay(pair, moves):
    codes = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}
    letters = {v: k for k, v in codes.items()}
    current = []
    for raw in pair:
        word = deque()
        for c in raw:
            k = codes[c]
            if word and word[-1] == -k:
                word.pop()
            else:
                word.append(k)
        current.append(word)
    for move in moves:
        op = move[0]
        if op == 'S' and len(move) == 1:
            current.reverse()
            continue
        if len(move) < 2 or type(move[1]) is not int or move[1] not in (1, 2):
            raise ValueError('invalid target')
        i = move[1] - 1
        if op == 'I' and len(move) == 2:
            current[i] = deque(-k for k in reversed(current[i]))
        elif op == 'C' and len(move) == 3 and move[2] in codes:
            k = codes[move[2]]
            if current[i] and current[i][0] == k:
                current[i].popleft()
            else:
                current[i].appendleft(-k)
            if current[i] and current[i][-1] == -k:
                current[i].pop()
            else:
                current[i].append(k)
        elif op == 'M' and len(move) == 3 and type(move[2]) is int and move[2] == 3 - move[1]:
            for k in current[move[2] - 1]:
                if current[i] and current[i][-1] == -k:
                    current[i].pop()
                else:
                    current[i].append(k)
        else:
            raise ValueError('invalid elementary move')
    return [''.join(letters[k] for k in word) for word in current]


def recognize(word):
    reduced = reduce_word(word)
    prefix = ''
    while len(reduced) >= 2 and reduced[0] == reduced[-1].swapcase():
        prefix += reduced[0]
        reduced = reduced[1:-1]
    for cut in range(max(1, len(reduced))):
        rotated = reduced[cut:] + reduced[:cut]
        m = rotated.count('x') - rotated.count('X')
        n = rotated.count('y') - rotated.count('Y')
        if rotated == block(m, n):
            return (m, n), prefix + reduced[:cut]
    return None


class MoveBudgetExceeded(Exception):
    pass


def solve(pair, max_moves=None):
    if len(pair) != 2:
        raise ValueError('expected two relators')
    matches = [recognize(word) for word in pair]
    if any(match is None for match in matches):
        return {'solved': False, 'reason': 'not_two_block'}
    matrix = [list(match[0]) for match in matches]
    det = matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    if abs(det) != 1:
        return {'solved': False, 'reason': 'abelianization', 'determinant': det}
    moves = []
    current = [reduce_word(word) for word in pair]

    def emit(op):
        if max_moves is not None and len(moves) >= max_moves:
            raise MoveBudgetExceeded(max_moves)
        moves.append(op)
        if op[0] == 'S':
            current.reverse()
        elif op[0] == 'I':
            current[op[1]-1] = inverse(current[op[1]-1])
        elif op[0] == 'M':
            current[op[1]-1] = reduce_word(current[op[1]-1] + current[op[2]-1])
        else:
            c = op[2]
            current[op[1]-1] = reduce_word(inverse(c) + current[op[1]-1] + c)

    def conjugate(i, word):
        for c in word:
            emit(['C', i+1, c])

    def check():
        assert current == [block(*row) for row in matrix]

    for i, match in enumerate(matches):
        conjugate(i, match[1])
    check()

    def negate(i):
        n = matrix[i][1]
        emit(['I', i+1])
        conjugate(i, power('y', -n))
        matrix[i] = [-value for value in matrix[i]]
        check()

    def subtract(i, j):
        n = matrix[j][1]
        emit(['I', i+1])
        emit(['M', i+1, j+1])
        emit(['I', i+1])
        conjugate(i, power('y', -n))
        matrix[i] = [a-b for a, b in zip(matrix[i], matrix[j])]
        check()

    for i in range(2):
        if matrix[i][0] < 0:
            negate(i)
    while matrix[1][0]:
        if matrix[0][0] < matrix[1][0]:
            emit(['S'])
            matrix.reverse()
        subtract(0, 1)
    assert matrix[0][0] == 1 and abs(matrix[1][1]) == 1
    if matrix[1][1] < 0:
        negate(1)
    if matrix[0][1] < 0:
        negate(1)
        while matrix[0][1] < 0:
            subtract(0, 1)
        negate(1)
    else:
        while matrix[0][1] > 0:
            subtract(0, 1)
    assert current == ['x', 'y']
    assert replay(pair, moves) == ['x', 'y']
    return {'solved': True, 'reason': 'two_block_unimodular',
            'r1': pair[0], 'r2': pair[1], 'elementary_moves': moves,
            'elementary_move_count': len(moves), 'final_state': current,
            'replay_verified': True}
