"""acx.core.capcount: the plain counter's semantics, and the numba twin pinned to it on random streams."""
import ast
import random
from pathlib import Path

import pytest

import acx.core.capcount
from acx.core.capcount import FIELDS, CapArrays, CapCount, blank, combine, fields, summarize


def test_semantics_by_hand():
    c = CapCount(10, known=(b"start",))
    c.pop((5, 0, b"start"))                          # pop 1: nothing pending
    c.drop((6, 1, b"a"), total=21, longest=11, ident=b"a")
    c.drop((4, 1, b"b"), total=23, longest=13, ident=b"b")
    c.drop((4, 1, b"b"), total=22, longest=13, ident=b"b")        # same state again: per-move count only
    c.drop((9, 1, b"start"), total=20, longest=12, ident=b"start")  # equal to the start: no new state
    assert (c.dropped, c.would_pop, c.pending) == (4, 0, 2)          # nothing drains before a later pop
    c.pop((4, 1, b"b"))                              # an equal key is not "before" (cannot occur in a search)
    assert c.would_pop == 0
    c.pop((5, 1, b"x"))                              # pop 3: b sorts before it
    assert (c.would_pop, c.first_bind, c.needed) == (1, 3, 13)
    c.drop((3, 0, b"a"), total=21, longest=11, ident=b"a")          # a later, smaller duplicate: the first key holds
    c.pop((5, 2, b"y"))
    assert c.would_pop == 1
    c.pop((7, 2, b"z"))                              # the solving pop drains too
    c.end(ran_dry=False, left=5)
    assert c.record() == dict(zip(FIELDS, (10, 5, 20, 2, 3, 11)))


def test_dry_queue_counts_what_the_budget_would_pop():
    c = CapCount(8)
    c.pop((1, 0, b"s"))
    for k in range(5):
        c.drop((10 + k, 1, bytes([k + 1])), total=20, longest=12 - k, ident=bytes([k + 1]))
    c.end(ran_dry=True, left=3)
    assert c.record() == dict(zip(FIELDS, (8, 5, 20, 3, 2, 8)))      # cap_needed over every pending state
    d = CapCount(8)
    d.pop((1, 0, b"s"))
    d.drop((10, 1, b"q"), total=20, longest=12, ident=b"q")
    d.end(ran_dry=False, left=3)                     # budget spent or solved: pending entries never pop
    assert d.record() == dict(zip(FIELDS, (8, 1, 20, 0, None, None)))


@pytest.mark.parametrize("left", [0, 1, 3, 5, 9])
def test_dry_queue_counts_only_the_pops_the_budget_has_left(left):
    """Five states pending on a dry queue: ``min(left, 5)`` would pop, none at all once the budget is spent.
    The numba twin agrees, ``left == 0`` included (a random stream rarely ends there with states pending)."""
    plain, twin = CapCount(8), CapArrays(8)
    plain.pop((1, 0, b"s"))
    twin.pop(1, 0, b"s")
    for k in range(5):
        key = bytes([k + 1])
        plain.drop((10 + k, 1, key), total=20, longest=12 - k, ident=key)
        twin.drop(10 + k, 1, key, 20, 12 - k)
    plain.end(ran_dry=True, left=left)
    twin.end(True, left)
    want = (8, 5, 20, min(left, 5), 2, 8) if left else (8, 5, 20, 0, None, None)
    assert plain.record() == twin.record() == dict(zip(FIELDS, want))


def test_accept_and_drop_now():
    seen = set()
    c = CapCount(5, accept=lambda p: p not in seen and not seen.add(p))   # pop-time dedup
    c.pop(None)
    c.drop((2, 0), 9, 6, payload="u")
    c.drop((1, 0), 9, 7, payload="u")                # the same state twice: counted once when drained
    c.pop((3, 0))
    assert (c.would_pop, c.first_bind, c.needed) == (1, 2, 7)
    c.drop_now(8, 6)
    assert (c.dropped, c.would_pop, c.first_bind, c.needed, c.min_total) == (3, 2, 2, 6, 8)


def test_blank_fields_combine_summarize():
    assert blank() == dict(zip(FIELDS, (None, 0, None, 0, None, None)))
    assert fields("dyn_cap")[:2] == ("dyn_cap", "dyn_cap_dropped") and fields("slack")[5] == "slack_needed"
    a = dict(zip(FIELDS, (16, 10, 30, 0, None, None)))
    b = dict(zip(FIELDS, (20, 5, 25, 2, 7, 21)))
    assert combine([(a, 0), (b, 100)]) == dict(zip(FIELDS, (16, 15, 25, 2, 107, 21)))
    s = summarize([{"id": "1", **a}, {"id": "2", **b}, {"id": "3", **blank(cap=16)}, {"id": "4"}])
    assert s == {"cap": [16, 20], "rows": 3, "rows_dropped": 2, "rows_would_pop": 1, "raise_ids": ["2"],
                 "dropped": 15, "would_pop": 2, "dropped_min_total": 25, "first_bind_min": 7,
                 "needed_min": 21, "needed_max": 21}
    assert summarize([{"id": "1"}]) is None
    assert combine([]) == blank() and blank("slack", cap=8)["slack"] == 8


def _stream(rng, n_pops):
    """Random (pop bar | drop) events with ties on (prio, depth), duplicates and prefixes."""
    pool = [bytes(rng.randint(1, 4) for _ in range(rng.randint(1, 4))) for _ in range(40)]
    ev = []
    for _ in range(n_pops):
        ev.append(("pop", (float(rng.randint(0, 12)), rng.randint(0, 6), rng.choice(pool))))
        for _ in range(rng.randint(0, 8)):
            b = rng.choice(pool)
            ev.append(("drop", (float(rng.randint(0, 12)), rng.randint(0, 6), b), rng.randint(5, 40), len(b) + 9))
    return ev


@pytest.mark.parametrize("seed", range(40))
def test_numba_twin_matches_the_plain_counter(seed):
    rng = random.Random(seed)
    known = bytes([1, 2])
    plain, twin = CapCount(9, known=(known,)), CapArrays(9, entries=2, nbytes=4)   # growth from tiny arrays
    twin.known(known)
    for e in _stream(rng, rng.randint(1, 30)):
        if e[0] == "pop":
            plain.pop(e[1])
            twin.pop(*e[1])
        else:
            key, total, longest = e[1:]
            plain.drop(key, total, longest, ident=key[2])
            twin.drop(*key, total, longest)               # grows its arrays when they are full
    dry, left = rng.random() < 0.5, rng.randint(0, 6)
    plain.end(dry, left)
    twin.end(dry, left)
    assert twin.record() == plain.record()


def test_fields_address_a_record_by_short_name():
    assert fields().would_pop == "cap_would_pop"
    assert fields("dyn_cap").first_bind == "dyn_cap_first_bind"


def imports(source):
    """The modules a source file imports, as written: ``numpy``, ``heapq``, ``.records`` (a sibling), ``..words``."""
    names = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append("." * node.level + (node.module or ""))
    return names


def test_capcount_knows_no_heuristic():
    """The counter only compares the keys a search hands it: its modules import a few libraries and each other,
    never a search, a priority or the word code."""
    modules = list(Path(acx.core.capcount.__file__).parent.glob("*.py"))
    assert len(modules) >= 5
    for path in modules:
        for name in imports(path.read_text()):
            sibling = name.startswith(".") and not name.startswith("..")
            assert sibling or name.split(".")[0] in {"numpy", "numba", "heapq", "typing"}, (path.name, name)
