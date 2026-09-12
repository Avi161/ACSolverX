# Observation: common tail of Q_{n,δ}

Both relators of the verified normal form

```
R1 = XYxyxxy xd YXX
R2 = Yxxy (xd)^n YXX
```

end with the same length-3 word `YXX` = `y^{-1}x^{-2}`. They also share the
contiguous block `xxy` / `Yxxy` / `XYXX` (see `tables/q_residue_scan.json`).

This is the “word represented in both relators” direction from the campaign
brief. A defining generator `t^{-1} YXX` would let AC1–AC3 replace that tail
in both rows, then Lemma 11-delete `t` after isolation. It is **not** yet a
theorem: one must prove an isolator exists and a well-founded measure drops.

Bounded rank-3 isolator census with `|w|≤2`, `|I|≤5` accepted 0 templates on
`Q_{2,-1}` (62,464 enumerated). Longer defining words, or a template that
retains the other relator, remain open.

Do not treat the common tail as a Tietze deletion of a generator.
