"""Crash-safe, resumable append-only JSONL helpers (project convention; see CLAUDE.md).

One JSON object per line, one line per item. A sweep appends + flushes + fsyncs per
line, and on restart skips items already recorded. A crash loses at most the single
in-flight line; a trailing truncated/corrupt line is ignored (its id is recomputed).
"""
import json
import os


def jsonl_done_ids(path, key="idx"):
    """Return the set of ``key`` values already recorded in ``path`` (empty if absent).

    A trailing truncated/corrupt line is skipped so a crashed sweep resumes cleanly.
    """
    done = set()
    if not os.path.exists(path):
        return done
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # trailing partial write from a crash — recompute this id
            if key in obj:
                done.add(obj[key])
    return done


def jsonl_append(path, obj):
    """Append one JSON object as a line, flushing to disk before returning."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")
        f.flush()
        os.fsync(f.fileno())
