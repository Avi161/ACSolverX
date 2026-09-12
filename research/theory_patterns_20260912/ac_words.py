"""Small free-group identities and strict three-operation AC certificates."""

from __future__ import annotations

from dataclasses import dataclass


def inv(word: str) -> str:
    return word.swapcase()[::-1]


def red(word: str) -> str:
    stack = []
    for letter in word:
        if letter not in "xXyY":
            raise ValueError(f"invalid letter {letter!r}")
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic(word: str) -> tuple[str, str]:
    word = red(word)
    start, stop = 0, len(word)
    while stop - start > 1 and word[start] == word[stop - 1].swapcase():
        start += 1
        stop -= 1
    return word[start:stop], word[:start]


def canon(word: str) -> str:
    core, _ = cyclic(word)
    if not core:
        return ""
    return min(w[i:] + w[:i] for w in (core, inv(core)) for i in range(len(w)))


def exponent(word: str, generator: str) -> int:
    return word.count(generator) - word.count(generator.upper())


@dataclass(frozen=True)
class Factor:
    sign: int
    conjugator: str

    def __post_init__(self):
        if type(self.sign) is not int or self.sign not in (-1, 1):
            raise ValueError("factor sign must be an integer ±1")
        if not isinstance(self.conjugator, str) or any(c not in "xXyY" for c in self.conjugator):
            raise ValueError("invalid factor conjugator")


def inverse_factors(factors):
    return tuple(Factor(-f.sign, f.conjugator) for f in reversed(factors))


def conjugate_factors(factors, suffix):
    return tuple(Factor(f.sign, red(f.conjugator + suffix)) for f in factors)


def simplify_factors(factors):
    out = []
    for factor in factors:
        if factor.sign not in (-1, 1):
            raise ValueError("factor sign must be ±1")
        factor = Factor(factor.sign, red(factor.conjugator))
        if out and out[-1].conjugator == factor.conjugator and out[-1].sign == -factor.sign:
            out.pop()
        else:
            out.append(factor)
    return tuple(out)


def expand_factors(donor, factors):
    result = ""
    for factor in factors:
        word = donor if factor.sign == 1 else inv(donor)
        result = red(result + inv(factor.conjugator) + word + factor.conjugator)
    return result


class Trace:
    def __init__(self, pair):
        self.pair = [red(w) for w in pair]
        if len(self.pair) != 2:
            raise ValueError("exactly two relators required")
        self.moves = []

    @staticmethod
    def _target(target):
        if type(target) is not int or target not in (0, 1):
            raise ValueError("target must be integer 0 or 1")

    def invert(self, target):
        self._target(target)
        self.pair[target] = inv(self.pair[target])
        self.moves.append({"op": "invert", "target": target + 1})

    def multiply(self, target):
        self._target(target)
        self.pair[target] = red(self.pair[target] + self.pair[1 - target])
        self.moves.append({"op": "multiply", "target": target + 1, "source": 2 - target})

    def conjugate(self, target, word):
        self._target(target)
        word = red(word)
        self.pair[target] = red(inv(word) + self.pair[target] + word)
        self.moves.extend({"op": "conjugate", "target": target + 1, "by": c} for c in word)

    def append_factors(self, target, factors):
        self._target(target)
        donor = 1 - target
        before = self.pair[donor]
        for factor in factors:
            if factor.sign == -1:
                self.invert(donor)
            self.conjugate(donor, factor.conjugator)
            self.multiply(target)
            self.conjugate(donor, inv(factor.conjugator))
            if factor.sign == -1:
                self.invert(donor)
        assert self.pair[donor] == before

    def canonicalize(self, target):
        self._target(target)
        core, prefix = cyclic(self.pair[target])
        self.conjugate(target, prefix)
        assert self.pair[target] == core
        if not core:
            return
        best = canon(core)
        if not any(core[k:] + core[:k] == best for k in range(len(core))):
            self.invert(target)
            core = self.pair[target]
        k = next(k for k in range(len(core)) if core[k:] + core[:k] == best)
        self.conjugate(target, core[:k])
        assert self.pair[target] == best


def replay(pair, moves):
    """Independent integer-stack replay; accepts only AC1, AC2 and AC3."""
    encode = {"x": 1, "X": -1, "y": 2, "Y": -2}
    decode = {v: k for k, v in encode.items()}

    def reduce_int(word):
        stack = []
        for symbol in word:
            if stack and stack[-1] == -symbol:
                stack.pop()
            else:
                stack.append(symbol)
        return stack

    if len(pair) != 2:
        raise ValueError("exactly two relators required")
    current = [reduce_int([encode[c] for c in w]) for w in pair]
    for move in moves:
        target = move["target"]
        if type(target) is not int or target not in (1, 2):
            raise ValueError("invalid target")
        i = target - 1
        if move["op"] == "invert":
            current[i] = [-v for v in reversed(current[i])]
        elif move["op"] == "multiply":
            source = move["source"]
            if type(source) is not int or source != 3 - target:
                raise ValueError("invalid source")
            current[i] = reduce_int(current[i] + current[source - 1])
        elif move["op"] == "conjugate":
            by = move["by"]
            if by not in encode:
                raise ValueError("conjugator must be one generator letter")
            v = encode[by]
            current[i] = reduce_int([-v] + current[i] + [v])
        else:
            raise ValueError("not an elementary AC operation")
    return ["".join(decode[v] for v in w) for w in current]
