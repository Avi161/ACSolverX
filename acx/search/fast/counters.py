"""Slots of the fast engine's counters array ``st`` (int64), and the status codes of its pop loop."""

# Slots of ``st``. DROPPED is the cap's per-move count, DMIN_T the least dropped total (-1: none yet).
NODES, HEAP_LEN, N_DISC, MIN_T, MAX_T, EXP_T, EXP_ID, SOLVED_ID, DROPPED, DMIN_T = range(10)

# What ``_run`` returns: finished, solved, or stopped before a pop whose children might not fit.
OK, SOLVED, NEED_CAPACITY, NEED_WIDTH = range(4)
