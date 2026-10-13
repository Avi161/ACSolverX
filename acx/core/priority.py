"""Heap priorities, lower pops first: ``length`` (total relator length, an int) and ``s20_mk2`` (a float).

``PRIORITIES`` maps names to functions of the relators; ``get`` looks one up. ``acx.search.fast.kernels.score``
computes the same values, bit for bit.
"""


def _blocks(w):
    """Cyclic generator runs of ``w`` as ``[generator, length]`` pairs."""
    runs = []
    for symbol in w:
        generator = abs(symbol)
        if runs and runs[-1][0] == generator:
            runs[-1][1] += 1
        else:
            runs.append([generator, 1])
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:         # a run across the seam is one block
        runs[0][1] += runs.pop()[1]
    return runs


def length(rels):
    """The ``length`` priority: total relator length."""
    return sum(map(len, rels))


def features(rels):
    """``(L, MK, S)`` of a two-generator presentation, reading relators as rings of generator runs.

    ``L``: total length. Blocks are cyclic runs of one generator (``x`` and ``X`` count alike; a run across the
    seam is one block). ``knots(r)`` is 0 for a pure power, else max(#x-blocks, #y-blocks); ``MK`` is the largest
    knots. ``S`` is the smaller of the mean x-block and mean y-block lengths pooled over all relators (the one
    nonzero mean when a generator is absent). ``ValueError`` past two generators.
    """
    max_knots = 0
    x_blocks = y_blocks = 0              # block counts over all relators
    x_letters = y_letters = 0            # letters in those blocks
    for relator in rels:
        blocks = _blocks(relator)
        x_lengths = [length for generator, length in blocks if generator == 1]
        y_lengths = [length for generator, length in blocks if generator == 2]
        if len(x_lengths) + len(y_lengths) != len(blocks):
            raise ValueError("s20_mk2 is defined for two generators only")
        if x_lengths and y_lengths:
            max_knots = max(max_knots, len(x_lengths), len(y_lengths))
        x_blocks += len(x_lengths)
        y_blocks += len(y_lengths)
        x_letters += sum(x_lengths)
        y_letters += sum(y_lengths)
    mean_x = x_letters / x_blocks if x_blocks else 0.0
    mean_y = y_letters / y_blocks if y_blocks else 0.0
    if x_blocks == 0 or y_blocks == 0:
        smaller_mean = mean_y if mean_x == 0.0 else mean_x
    else:
        smaller_mean = mean_x if mean_x < mean_y else mean_y
    return x_letters + y_letters, max_knots, smaller_mean


def s20_mk2(rels):
    """The ``s20_mk2`` priority ``L + 20 S + 2 MK`` (``features``), summed in the order L, MK, S: the fast
    engine's order, so both backends give identical floats."""
    total_length, max_knots, smaller_mean = features(rels)
    score = 0.0
    score += 1.0 * total_length
    score += 2.0 * max_knots
    score += 20.0 * smaller_mean
    return score


PRIORITIES = {"length": length, "s20_mk2": s20_mk2}


def get(name):
    """The priority function called ``name``; ``ValueError`` for an unknown name."""
    try:
        return PRIORITIES[name]
    except KeyError:
        raise ValueError(f"unknown priority {name!r}; choose from {sorted(PRIORITIES)}") from None
