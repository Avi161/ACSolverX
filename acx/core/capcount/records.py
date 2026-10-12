"""The cap counters as plain records: field names, an empty record, and combining records across searches or rows."""
from typing import NamedTuple

FIELDS = ("cap", "cap_dropped", "cap_dropped_min_total", "cap_would_pop", "cap_first_bind", "cap_needed")


class FieldNames(NamedTuple):
    """The record keys of one counter, by short name (``names.would_pop`` is ``"cap_would_pop"``)."""
    cap: str
    dropped: str
    min_total: str
    would_pop: str
    first_bind: str
    needed: str


def fields(prefix="cap"):
    """``FIELDS`` under another counter prefix (``"dyn_cap"`` -> ``dyn_cap``, ``dyn_cap_dropped``, ...), also by short
    name (``fields("dyn_cap").first_bind``)."""
    return FieldNames(*(name.replace("cap", prefix, 1) for name in FIELDS))


def blank(prefix="cap", cap=None):
    """The record of a search that kept no counter (uncapped): ``cap: None, dropped 0, ...``."""
    return dict(zip(fields(prefix), (cap, 0, None, 0, None, None)))


def combine(parts, prefix="cap"):
    """One record from several searches run one after another on a shared budget (e.g. CoV legs).

    ``parts``: ``(record, pops_before)`` pairs in run order, ``pops_before`` the pops spent before that
    search started. Sums ``dropped`` and ``would_pop``; ``first_bind`` is ``pops_before`` plus the first
    binding search's ``first_bind``; ``min_total`` and ``needed`` are minima; ``cap`` is the first
    record's.
    """
    key = fields(prefix)
    total = blank(prefix)
    for index, (record, pops_before) in enumerate(parts):
        if index == 0:
            total[key.cap] = record[key.cap]
        total[key.dropped] += record[key.dropped]
        total[key.would_pop] += record[key.would_pop]
        for name in (key.min_total, key.needed):
            if record[name] is not None and (total[name] is None or record[name] < total[name]):
                total[name] = record[name]
        if total[key.first_bind] is None and record[key.first_bind] is not None:
            total[key.first_bind] = pops_before + record[key.first_bind]
    return total


def summarize(records, prefix="cap", ids=None, keep=100):
    """The ``summary.json`` block of one counter over a run's row records (rows lacking it are skipped).

    It holds the cap(s), the rows seen, the rows that dropped, the rows with ``would_pop > 0`` (their ids, up
    to ``keep``), the sums, and the least ``dropped_min_total``, ``first_bind`` and least/greatest ``needed``.
    Returns None when no row has the counter.
    """
    key = fields(prefix)
    row_ids = ids or [record.get("id") for record in records]
    rows = [(row_id, record) for row_id, record in zip(row_ids, records) if key.dropped in record]
    if not rows:
        return None
    caps = sorted({record[key.cap] for _, record in rows}, key=lambda cap: (cap is None, cap))
    raise_ids = [row_id for row_id, record in rows if record[key.would_pop]]

    def extreme(name, pick=min):
        """``pick`` (min or max) of a field over the rows that set it, or None."""
        values = [record[name] for _, record in rows if record[name] is not None]
        return pick(values) if values else None

    return {
        key.cap: caps[0] if len(caps) == 1 else caps,
        "rows": len(rows),
        "rows_dropped": sum(1 for _, record in rows if record[key.dropped]),
        "rows_would_pop": len(raise_ids),
        "raise_ids": raise_ids[:keep],
        "dropped": sum(record[key.dropped] for _, record in rows),
        "would_pop": sum(record[key.would_pop] for _, record in rows),
        "dropped_min_total": extreme(key.min_total),
        "first_bind_min": extreme(key.first_bind),
        "needed_min": extreme(key.needed),
        "needed_max": extreme(key.needed, max),
    }
