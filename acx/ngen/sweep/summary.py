"""Read the row files of a result directory into ``summary.json`` and ``summary.md``.

Fractions are per presentation, averaged over presentations; fewer, same, more and lost (pops against the control's)
are averaged over the control-solved presentations only, as in the baseline's tables. The oracle counts a presentation
as solved when some word of the bucket (up to that length) solves it; "some faster" counts control-solved ones only.
"""
import json
import os
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np

from .config import COUNTERS, SweepConfig, words_of
from .rows import finished_rows, load_row, row_path
from .words import combos, word_str


class Bucket(NamedTuple):
    """``members``: the starts reported in the bucket; ``upto``: the starts the oracle may pick from."""
    name: str
    members: np.ndarray
    upto: np.ndarray


def buckets_of(sc, words, starts):
    """One bucket per word length for ``extra = 1`` (the oracle takes the words up to that length), else one."""
    if sc.extra != 1:
        everything = np.ones(len(starts), bool)
        return [Bucket("all", everything, everything)]
    lengths = np.array([len(w) for w in words])
    return [Bucket(f"L{n}", lengths == n, lengths <= n) for n in range(sc.min_len, sc.max_len + 1)]


@dataclass
class BucketTally:
    """The sums over rows of one bucket's per-presentation fractions and oracle counts."""
    solved: float = 0.0
    solved_control_solved: float = 0.0
    solved_control_unsolved: float = 0.0
    fewer: float = 0.0
    same: float = 0.0
    more: float = 0.0
    lost: float = 0.0
    solved_by_some: int = 0
    gained: int = 0
    lost_by_every: int = 0
    faster: int = 0

    def add_row(self, bucket, solved, pops, control_solved, control_pops):
        """Add one row; ``solved`` and ``pops`` are the arrays over all starts of the row."""
        here, here_pops = solved[bucket.members], pops[bucket.members]
        self.solved += here.mean()
        if control_solved:
            self.solved_control_solved += here.mean()
            self.fewer += (here & (here_pops < control_pops)).mean()
            self.same += (here & (here_pops == control_pops)).mean()
            self.more += (here & (here_pops > control_pops)).mean()
            self.lost += (~here).mean()
        else:
            self.solved_control_unsolved += here.mean()

        oracle = solved[bucket.upto]
        some = bool(oracle.any())
        self.solved_by_some += some
        self.gained += some and not control_solved
        self.lost_by_every += control_solved and not some
        self.faster += some and control_solved and int(pops[bucket.upto][oracle].min()) < control_pops

    def table(self, bucket, n_rows, n_control_solved):
        """The bucket's entry of ``summary.json``."""
        n_control_unsolved = n_rows - n_control_solved

        def per_control_solved(total):
            return _fraction(total / n_control_solved) if n_control_solved else None

        return dict(
            starts=int(bucket.members.sum()), solved=_fraction(self.solved / n_rows),
            solved_on_control_solved=per_control_solved(self.solved_control_solved),
            solved_on_control_unsolved=_fraction(self.solved_control_unsolved / n_control_unsolved)
            if n_control_unsolved else None,
            fewer=per_control_solved(self.fewer), same=per_control_solved(self.same),
            more=per_control_solved(self.more), lost=per_control_solved(self.lost),
            oracle=dict(solved_by_some=self.solved_by_some, gained_over_control=self.gained,
                        control_solved_lost_by_every=self.lost_by_every, some_faster_than_control=self.faster))


@dataclass
class CapTally:
    """Counts of searches by what the relator cap did, over all rows."""
    searches: int = 0
    dropped: int = 0              # the cap dropped a child
    could_bind: int = 0           # a dropped child would have been popped
    solved_could_bind: int = 0
    below_budget: int = 0         # unsolved although the budget was not used up

    def add_row(self, row, solved, pops, budget):
        """Add one row file's arrays."""
        could_bind = row["cap_first_bind"] >= 0
        self.searches += len(solved)
        self.dropped += int((row["cap_dropped"] > 0).sum())
        self.below_budget += int((~solved & (pops < budget)).sum())
        self.could_bind += int(could_bind.sum())
        self.solved_could_bind += int((could_bind & solved).sum())


def _fraction(x):
    """Six places, so the markdown's one-decimal percent is the exact value's rounding (0.806458 prints 80.6%)."""
    return round(float(x), 6)


def summarize(result_dir, wall=None):
    """Stream every row file of ``result_dir`` into ``summary.json`` and ``summary.md``; return the summary.

    The summary covers the whole directory, whichever rows the latest run selected; ``wall`` is that run's seconds.
    """
    with open(os.path.join(result_dir, "config.json")) as f:
        sc = SweepConfig.from_key(json.load(f)["sweep"])
    words = words_of(sc)
    starts = combos(len(words), sc.extra)
    buckets = buckets_of(sc, words, starts)

    tallies = {b.name: BucketTally() for b in buckets}
    cap = CapTally()
    solved_per_start = np.zeros(len(starts), dtype=np.int64)
    n_rows = n_control_solved = 0
    core_seconds = 0.0
    for row_id in finished_rows(result_dir):
        row = load_row(row_path(result_dir, row_id))
        control_solved, control_pops = bool(row["control"]["solved"]), row["control"]["pops"]
        solved, pops = row["path_len"] >= 0, row["nodes"].astype(np.int64)
        n_rows += 1
        n_control_solved += control_solved
        core_seconds += float(row["seconds"])
        solved_per_start += solved
        for bucket in buckets:
            tallies[bucket.name].add_row(bucket, solved, pops, control_solved, control_pops)
        cap.add_row(row, solved, pops, sc.search.budget)

    best = int(solved_per_start.argmax())
    summary = dict(
        rows=n_rows, extra=sc.extra, lengths=[sc.min_len, sc.max_len], budget=sc.search.budget, cap=sc.search.cap,
        starts_per_row=len(starts), searches=n_rows * len(starts), control_solved=n_control_solved,
        buckets={b.name: tallies[b.name].table(b, n_rows, n_control_solved) for b in buckets},
        best_single=dict(word=word_str([words[j] for j in starts[best]]), solved=int(solved_per_start[best])),
        cap_counters=dict(fields=list(COUNTERS), searches=cap.searches, dropped=cap.dropped,
                          could_bind=cap.could_bind, solved_could_bind=cap.solved_could_bind,
                          below_budget=cap.below_budget),
        core_seconds=round(core_seconds, 2), **({} if wall is None else {"wall_seconds": round(wall, 2)}))
    with open(os.path.join(result_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(result_dir, "summary.md"), "w") as f:
        f.write(markdown(summary))
    return summary


def _percent(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def markdown(summary):
    """The summary as a markdown page: the bucket table, the best single start and the cap counters."""
    s = summary
    lines = [f"# rank {2 + s['extra']} brute force: {s['rows']} rows, budget {s['budget']}, cap {s['cap']}", "",
             f"Control solves {s['control_solved']} of {s['rows']}. {s['searches']:,} searches "
             f"({s['starts_per_row']:,} starts per row), words of length {s['lengths'][0]} to {s['lengths'][1]}.", "",
             "| bucket | starts | solved | on control-solved | on control-unsolved | fewer | same | more | lost "
             "| solved by some | gained | lost by every | some faster |", "|" + "---|" * 13]
    for name, t in s["buckets"].items():
        o = t["oracle"]
        lines.append(
            f"| {name} | {t['starts']:,} | {_percent(t['solved'])} | {_percent(t['solved_on_control_solved'])} | "
            f"{_percent(t['solved_on_control_unsolved'])} | {_percent(t['fewer'])} | {_percent(t['same'])} | "
            f"{_percent(t['more'])} | {_percent(t['lost'])} | {o['solved_by_some']} | {o['gained_over_control']} | "
            f"{o['control_solved_lost_by_every']} | {o['some_faster_than_control']} |")
    c = s["cap_counters"]
    lines += ["", f"Best single start: `{s['best_single']['word']}` solves {s['best_single']['solved']} rows.", "",
              f"Cap counters ({', '.join(c['fields'])}): the cap dropped a child in {c['dropped']:,} of "
              f"{c['searches']:,} searches; could bind in {c['could_bind']:,} ({c['solved_could_bind']:,} solved); "
              f"{c['below_budget']:,} unsolved searches stopped below the budget.", ""]
    return "\n".join(lines)
