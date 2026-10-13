"""Slots of the fast engine's counters array ``st`` (int64), and the status codes of its pop loop."""

# Slots of ``st``. DROPPED is the cap's per-move count, DMIN_T the least dropped total (-1: none yet).
COUNTER_SIZE = 10
NODES, HEAP_LEN, N_DISC, MIN_T, MAX_T, EXP_T, EXP_ID, SOLVED_ID, DROPPED, DMIN_T = range(COUNTER_SIZE)

# What ``_run`` returns: finished, solved, or stopped before a pop that might not fit: its children (``NEED_CAPACITY``,
# ``NEED_WIDTH``) or its record in the cap counters' per-pop arrays (``NEED_POPS``).
OK, SOLVED, NEED_CAPACITY, NEED_WIDTH, NEED_POPS = range(5)
