"""Cap counters in records and in ``summary.json``: which fields a record copies, and how a run sums them."""
from ..core.capcount import PREFIXES
from ..core.capcount import fields as counter_fields
from ..core.capcount import summarize as summarize_counter

CAP_EXTRA = ("cap_legs_bound",)                # CoV: legs whose counter bound
CAP_KEYS = tuple(field for prefix in PREFIXES for field in counter_fields(prefix)) + CAP_EXTRA


def record_caps(stats):
    """The cap counter fields of a result's ``stats``: every prefix whose ``<prefix>_dropped`` is present."""
    stats = stats or {}
    caps = {}
    for prefix in PREFIXES:
        if f"{prefix}_dropped" in stats:
            caps.update({field: stats[field] for field in counter_fields(prefix)})
    caps.update({key: stats[key] for key in CAP_EXTRA if key in stats})
    return caps


def caps_block(records):
    """``summary.json``'s ``caps``: one ``acx.core.capcount.summarize`` entry per counter prefix the rows carry."""
    block = {}
    for prefix in PREFIXES:
        entry = summarize_counter(records, prefix)
        if entry is None:
            continue
        if prefix == "cap":
            for key in CAP_EXTRA:
                values = [r[key] for r in records if key in r]
                if values:
                    entry[key] = sum(values)
        block[prefix] = entry
    return block
