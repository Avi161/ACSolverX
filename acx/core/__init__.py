"""Core types shared by every acx module: words, moves, priorities, config."""
from .config import SearchConfig
from .moves import Move, decode_path, encode_path, enumerate_moves, step
from .priority import PRIORITIES
from .words import Presentation, canonical_rels, canonical_word, fmt, inverse, parse, reduce, rotate
