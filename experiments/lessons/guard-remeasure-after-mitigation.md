# [2026-07-14] A guard that mitigates must re-measure before it escalates [TRAP]

The overnight ladder's memory guard (`run_overnight.py`) reads rss once per checkpoint tick,
then runs two checks against that single reading:

```python
rss = _rss_gb()                      # measured BEFORE any mitigation
if rss > soft: _MEMO1.clear()        # drops the actual memory hog
if rss > hard: raise _MemAbort(...)  # judged on the STALE reading
```

On the seam32 arm the first soft trip measured **3.00 GB**, dropped a **5,256,254-entry**
phase-1 memo — the bulk of that memory — and then the hard check fired *in the same tick* on
the 3.00 GB it had just mitigated. The arm stopped gracefully (results kept, by design) but
**6 hours early**: at 62,000 pops / 1.45M states its live data was ~1 GB, nowhere near the
2.8 GB hard limit the abort claimed.

The sibling failure shapes are already in the index — `ru_maxrss` never comes down
([gb-per-pres-sized-from-measured-memory](gb-per-pres-sized-from-measured-memory.md)), and a
guard must trip on real pressure, not a stale proxy. This one is subtler: the reading was
*current* when taken; it went stale because the guard's own first branch changed the world.

**Rule:** when one reading feeds an escalation ladder (log → mitigate → abort), every rung
after a mitigation must re-measure (`gc.collect()` first, so freed arenas actually return).
Otherwise the guard escalates a condition it has already fixed.
