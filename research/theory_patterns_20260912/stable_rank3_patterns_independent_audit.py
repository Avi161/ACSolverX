"""Independent integer-word checks for the three-relator corridor."""
import hashlib
import itertools
import json
from pathlib import Path
import time

from . import stable_rank3_patterns_check as author

HERE = Path(__file__).resolve().parent
ALPHABET = {"x": 1, "X": -1, "y": 2, "Y": -2, "z": 3, "Z": -3}


def require(value, message):
    if not value:
        raise ValueError(message)


def inv(word):
    return tuple(-letter for letter in reversed(word))


def red(word):
    stack = []
    for letter in word:
        require(type(letter) is int and 1 <= abs(letter) <= 3, "invalid integer letter")
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def pw(generator, exponent):
    return (generator if exponent >= 0 else -generator,) * abs(exponent)


def parse(word):
    return red(tuple(ALPHABET[c] for c in word))


def append(target, donor, sign, conjugator):
    require(type(sign) is int and sign in (-1, 1), "invalid donor sign")
    return red(target + inv(conjugator) + (donor if sign == 1 else inv(donor)) + conjugator)


def replay(words, moves):
    current = [parse(w) for w in words]
    peak = sum(map(len, current))
    for operation, target, argument in moves:
        require(type(target) is int and 0 <= target < 3, "target index")
        if operation == "inv":
            require(argument is None, "inversion argument")
            current[target] = inv(current[target])
        elif operation == "mul":
            require(type(argument) is int and 0 <= argument < 3 and argument != target, "distinct donor")
            current[target] = red(current[target] + current[argument])
        elif operation == "conj":
            require(isinstance(argument, str) and len(argument) == 1 and argument in ALPHABET, "single generator conjugation")
            letter = ALPHABET[argument]
            current[target] = red((-letter,) + current[target] + (letter,))
        else:
            raise ValueError("unknown elementary operation")
        peak = max(peak, sum(map(len, current)))
    return current, peak


def main():
    cpu = time.process_time()
    checks = 0
    for m, k, n in itertools.product(range(-2, 4), repeat=3):
        x, y, z = (1,), (2,), (3,)
        D = red(z + pw(1, m) + pw(2, n))
        I = red(inv(z) + pw(1, -m) + y + x)
        A = red(z + pw(2, k) + inv(z))
        C = red(A + y + x)
        first = append(D, I, 1, red(pw(1, m) + pw(2, n)))
        K = red(pw(2, n) + inv(first) + pw(2, -n))
        second = append(K, C, 1, red(A + pw(1, m) + pw(2, -n)))
        expected = red(pw(1, -m) + z + pw(2, k) + inv(z) + pw(1, m) + pw(2, -n))
        require(second == expected, "signed corridor identity")
        B = red(z + pw(2, k) + inv(z) + pw(2, -n))
        J = red(inv(z) + pw(1, -2*m) + y + x)
        E = red(pw(1, m) + z + pw(2, k) + inv(z) + pw(1, -m) + y + x)
        after = append(E, B, -1, red(pw(2, n) + pw(1, -m) + y + x))
        require(red(after + inv(J)) == red(pw(1, m) + pw(2, n) + pw(1, m) + z), "terminal form identity")
        matrix = ((m,n,1),(1-m,1,-1),(1,k+1,0))
        a,b,c = matrix
        determinant = a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
        require(determinant == k-n, "determinant")
        checks += 1
    seed = author.corridor(2, 1, 2, True)
    first, peak1 = replay(seed["initial"], seed["ordinary_move_stream"])
    require(first == [parse(w) for w in seed["ordinary_endpoint"]], "seed first endpoint")
    second, peak2 = replay(seed["coordinate_endpoint"], seed["post_coordinate_move_stream"])
    require(second == [parse(w) for w in seed["final_endpoint"]], "seed second endpoint")
    require((peak1, peak2) == (27, 29), "all-relator peaks")
    output = {"status": "pass", "signed_identity_cases": checks,
              "seed_ordinary_moves": len(seed["ordinary_move_stream"]),
              "seed_post_coordinate_moves": len(seed["post_coordinate_move_stream"]),
              "ordinary_segment_peaks": [peak1, peak2], "seed_final_total": sum(map(len, second)),
              "solved_ids": [], "new_length_gain_ids": [], "cpu_seconds": time.process_time()-cpu,
              "hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), HERE / "stable_rank3_patterns_check.py", HERE / "stable_rank3_patterns.md")},
              "proof_review": "General signed identities, necessary determinant, three unconditional ordinary soluble subfamilies, invertible stable coordinate, and extra-generator obstruction reviewed independently. The stable-coordinate elementary expansion is not emitted."}
    (HERE / "stable_rank3_patterns_independent_audit.json").write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
