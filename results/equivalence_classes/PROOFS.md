# Proof book — how the 261 unsolved Miller–Schupp reps collapse to 126 classes

Generated from `results/equivalence_classes/sweep_seam_28_250.json` by `experiments/equivalence_classes/make_proof_book.py`.

**Re-check every line of this file:**

```bash
.venv/bin/python3 experiments/equivalence_classes/verify_proofs.py
```

That reads `certificates.json` and the raw presentation CSV and *nothing else* — it replays every AC move by string substitution, re-proves every change of variables is an automorphism by Nielsen reduction, and rebuilds the partition from the verified edges alone. It shares no inference with the search that produced them.

## What is proved

| | count |
|---|---|
| presentations | 261 |
| **distinct problems (classes)** | **126** |
| edges proving them equivalent | 135 |
| — change of variables only (`cv`) | 93 |
| — needed AC moves (`ac`) | 42 |
| singleton classes | 13 |
| largest class | 8 |

Every class below is a tree of edges: each member is joined to the rest by a chain of the edges listed under it. Two kinds, and they prove different things.

---

## How to read a proof, by hand, with no computer

**Read this section once and every derivation below becomes checkable with a pencil.**

### The alphabet

A relator is a word in two generators. `x` and `y` are the generators; **a capital letter is an inverse** — `X` = `x⁻¹`, `Y` = `y⁻¹`. So `YYYxxyyX` means `y⁻¹y⁻¹y⁻¹xxyy x⁻¹`.

### What a substitution means — and what happens to the capitals

A substitution `psi: x -> …, y -> …` lists only where the **generators** go. It is a *homomorphism*, so the capitals are not free to choose — they follow automatically. Since `X` is just notation for `x⁻¹`:

```
psi(X) = psi(x^-1) = psi(x)^-1 = reverse psi(x), then swap the case of every letter
```

So **yes, `y -> Y` also means `Y -> y`** — but only because the image is a single letter, where inverting is just a case swap. When the image is longer the inverse is a *reversed* word, and reading it as a case swap gives the wrong answer:

| `psi` says | so the capital must go | because |
|---|---|---|
| `y -> Y` | `Y -> y` | `(y⁻¹)⁻¹ = y` — here it *is* just a case swap |
| `x -> xY` | `X -> yX` | reverse `xY` → `Yx`, swap case → `yX` |
| `x -> xy` | `X -> YX` | reverse `xy` → `yx`, swap case → `YX` |
| `x -> yx` | `X -> XY` | reverse `yx` → `xy`, swap case → `XY` |

88 of the 93 change-of-variables edges have single-letter images, where substituting really is just swapping cases. **5 do not** — for those, reverse first.

### The one thing that trips everyone up

Every presentation below is printed in **canonical form**, and canonicalisation quietly rewrites the relators. So when you substitute `y → Y` into a relator, **the string you get is almost never the target string you see printed** — you must still invert it and rotate it. That is not a gap in the proof; it is bookkeeping. But it is invisible unless it is written down, so **every derivation below writes it down**, step by step.

Canonical form does exactly three things, and each is free:

| | what it does | why it changes nothing |
|---|---|---|
| **freely reduce** | delete any `xX`, `Xx`, `yY`, `Yy` | `x x⁻¹` is the empty word |
| **invert** a relator | `r ↦ r⁻¹` (reverse the word, swap every letter's case) | a relator is a *relation* `r = 1`; `r⁻¹ = 1` says the same thing. It is also one of the four AC moves. |
| **rotate** a relator | move letters from the end to the front | a rotation is a conjugate: if `r = uv` then the rotation `vu = u⁻¹(uv)u = u⁻¹ r u`. Conjugating a relator is an AC move, and it does not change the group. |

(It also sorts the two relators, since which one you write first is not data.) Among all the rotations of `r` and of `r⁻¹`, canonical form keeps the alphabetically least — a fingerprint, so two presentations that differ only by this bookkeeping get the same string.

So a derivation line like

```
  r1 = YYYxxyyX
       substitute y -> Y   ->  yyyxxYYX
       invert             ->  xyyXXYYY
       rotate by 3        ->  YYYxyyXX     = r1 of 19_50   [MATCH]
```

is checked with a pencil: swap the case of every `y`; then reverse the word and swap every letter's case; then move the last 3 letters to the front. The result is the printed target. **The substitution is the only mathematical content — the invert and the rotate are notation.**

### The two kinds of edge

#### `cv` — change of variables only

A single substitution `psi` with `canon(psi(A)) == canon(B)`. **B is A with new words substituted for the generators** — no AC move at all. Every one is derived below, relator by relator, in the form just shown.

#### `ac` — AC moves were needed

Both presentations are driven to a common form by **Definition 2.1 moves**:

```
r_i  <-  rot_k1(r_i) . rot_k2(r_j^±1)          (note: the move inverts the OTHER relator)
```

In words: rotate relator `i` by `k1`, rotate the *other* relator by `k2` (inverting it first if the exponent is `-1`), and **concatenate them** — the product replaces relator `i`. The other relator is untouched. Every move below shows the two rotated pieces and their product, so you can concatenate the strings yourself.

This proves **A and B are the same problem** — A is AC-trivial ⟺ B is. It does **not** exhibit an AC path from A to B, because a change of variables is applied between the moves.

On **6 of the 42** the change of variables at every step is the identity, so the path is Definition 2.1 moves and nothing else. Those are flagged `pure AC path` and do give an AC path — from `A` to `psi(B)`, where `psi` is the relabelling that carried the two roots to their `Aut`-minimal forms. **Not** from A to B; no edge here proves that.

---

## Index

| class | size | members |
|---|---|---|
| [001](#class-001) | 8 | 4(21_1) 179(22_13) 180(22_14) 182(23_21) 186(21_36) 191(23_24) 196(18_6) 197(18_7) |
| [002](#class-002) | 6 | 181(21_34) 188(21_37) 195(15_12) 204(15_13) 225(15_14) 237(15_15) |
| [003](#class-003) | 5 | 183(19_37) 187(19_38) 198(17_41) 203(17_42) 212(20_12) |
| [004](#class-004) | 4 | 3(17_1) 123(20_8) 124(20_9) 129(17_35) |
| [005](#class-005) | 4 | 184(23_22) 190(23_23) 231(19_43) 238(19_48) |
| [006](#class-006) | 4 | 201(19_40) 211(19_42) 236(19_47) 259(19_51) |
| [007](#class-007) | 4 | 202(18_9) 210(18_11) 235(19_46) 260(19_52) |
| [008](#class-008) | 3 | 127(16_6) 133(16_9) 161(16_10) |
| [009](#class-009) | 2 | 7(15_2) 11(15_6) |
| [010](#class-010) | 2 | 8(15_3) 14(15_9) |
| [011](#class-011) | 2 | 9(15_4) 12(15_7) |
| [012](#class-012) | 2 | 10(15_5) 13(15_8) |
| [013](#class-013) | 2 | 17(17_2) 36(17_21) |
| [014](#class-014) | 2 | 18(17_3) 42(17_27) |
| [015](#class-015) | 2 | 19(17_4) 44(17_29) |
| [016](#class-016) | 2 | 20(17_5) 32(17_17) |
| [017](#class-017) | 2 | 21(17_6) 34(17_19) |
| [018](#class-018) | 2 | 22(17_7) 41(17_26) |
| [019](#class-019) | 2 | 23(17_8) 43(17_28) |
| [020](#class-020) | 2 | 24(17_9) 31(17_16) |
| [021](#class-021) | 2 | 25(17_10) 33(17_18) |
| [022](#class-022) | 2 | 26(17_11) 35(17_20) |
| [023](#class-023) | 2 | 27(17_12) 40(17_25) |
| [024](#class-024) | 2 | 28(17_13) 39(17_24) |
| [025](#class-025) | 2 | 29(17_14) 38(17_23) |
| [026](#class-026) | 2 | 30(17_15) 37(17_22) |
| [027](#class-027) | 2 | 45(15_10) 46(15_11) |
| [028](#class-028) | 2 | 47(18_1) 49(18_3) |
| [029](#class-029) | 2 | 50(19_1) 71(19_22) |
| [030](#class-030) | 2 | 51(19_2) 79(19_30) |
| [031](#class-031) | 2 | 52(19_3) 81(19_32) |
| [032](#class-032) | 2 | 53(19_4) 69(19_20) |
| [033](#class-033) | 2 | 54(19_5) 67(19_18) |
| [034](#class-034) | 2 | 55(19_6) 78(19_29) |
| [035](#class-035) | 2 | 56(19_7) 80(19_31) |
| [036](#class-036) | 2 | 57(19_8) 68(19_19) |
| [037](#class-037) | 2 | 58(19_9) 66(19_17) |
| [038](#class-038) | 2 | 59(19_10) 70(19_21) |
| [039](#class-039) | 2 | 60(19_11) 75(19_26) |
| [040](#class-040) | 2 | 61(19_12) 74(19_25) |
| [041](#class-041) | 2 | 62(19_13) 73(19_24) |
| [042](#class-042) | 2 | 63(19_14) 72(19_23) |
| [043](#class-043) | 2 | 64(19_15) 77(19_28) |
| [044](#class-044) | 2 | 65(19_16) 76(19_27) |
| [045](#class-045) | 2 | 82(17_30) 85(17_33) |
| [046](#class-046) | 2 | 83(17_31) 84(17_32) |
| [047](#class-047) | 2 | 86(20_1) 89(20_3) |
| [048](#class-048) | 2 | 88(16_4) 90(16_5) |
| [049](#class-049) | 2 | 91(21_2) 112(21_20) |
| [050](#class-050) | 2 | 92(20_4) 120(20_7) |
| [051](#class-051) | 2 | 94(21_4) 110(21_18) |
| [052](#class-052) | 2 | 95(21_5) 108(21_16) |
| [053](#class-053) | 2 | 96(21_6) 119(21_27) |
| [054](#class-054) | 2 | 98(21_8) 109(21_17) |
| [055](#class-055) | 2 | 99(20_5) 107(20_6) |
| [056](#class-056) | 2 | 100(21_9) 111(21_19) |
| [057](#class-057) | 2 | 101(21_10) 116(21_24) |
| [058](#class-058) | 2 | 102(21_11) 115(21_23) |
| [059](#class-059) | 2 | 103(21_12) 114(21_22) |
| [060](#class-060) | 2 | 104(21_13) 113(21_21) |
| [061](#class-061) | 2 | 105(21_14) 118(21_26) |
| [062](#class-062) | 2 | 106(21_15) 117(21_25) |
| [063](#class-063) | 2 | 125(17_34) 131(17_36) |
| [064](#class-064) | 2 | 126(19_33) 130(19_34) |
| [065](#class-065) | 2 | 128(16_7) 132(16_8) |
| [066](#class-066) | 2 | 134(22_1) 140(22_4) |
| [067](#class-067) | 2 | 135(22_2) 139(22_3) |
| [068](#class-068) | 2 | 136(17_37) 142(17_40) |
| [069](#class-069) | 2 | 137(17_38) 141(17_39) |
| [070](#class-070) | 2 | 138(19_35) 143(19_36) |
| [071](#class-071) | 2 | 144(23_1) 167(23_13) |
| [072](#class-072) | 2 | 145(21_30) 175(21_33) |
| [073](#class-073) | 2 | 146(22_5) 177(22_12) |
| [074](#class-074) | 2 | 147(22_6) 165(22_10) |
| [075](#class-075) | 2 | 148(23_2) 163(23_11) |
| [076](#class-076) | 2 | 149(23_3) 174(23_20) |
| [077](#class-077) | 2 | 150(22_7) 176(22_11) |
| [078](#class-078) | 2 | 151(22_8) 164(22_9) |
| [079](#class-079) | 2 | 152(21_31) 162(21_32) |
| [080](#class-080) | 2 | 153(23_4) 166(23_12) |
| [081](#class-081) | 2 | 154(23_5) 171(23_17) |
| [082](#class-082) | 2 | 155(23_6) 170(23_16) |
| [083](#class-083) | 2 | 156(23_7) 169(23_15) |
| [084](#class-084) | 2 | 157(23_8) 168(23_14) |
| [085](#class-085) | 2 | 158(23_9) 173(23_19) |
| [086](#class-086) | 2 | 159(23_10) 172(23_18) |
| [087](#class-087) | 2 | 160(18_4) 178(18_5) |
| [088](#class-088) | 2 | 185(21_35) 189(21_38) |
| [089](#class-089) | 2 | 192(24_1) 206(24_4) |
| [090](#class-090) | 2 | 193(24_2) 205(24_3) |
| [091](#class-091) | 2 | 194(19_39) 208(19_41) |
| [092](#class-092) | 2 | 199(18_8) 207(18_10) |
| [093](#class-093) | 2 | 200(20_10) 209(20_11) |
| [094](#class-094) | 2 | 213(25_1) 244(25_22) |
| [095](#class-095) | 2 | 214(25_2) 252(25_30) |
| [096](#class-096) | 2 | 215(25_3) 254(25_32) |
| [097](#class-097) | 2 | 216(25_4) 242(25_20) |
| [098](#class-098) | 2 | 217(25_5) 240(25_18) |
| [099](#class-099) | 2 | 218(25_6) 251(25_29) |
| [100](#class-100) | 2 | 219(25_7) 253(25_31) |
| [101](#class-101) | 2 | 220(25_8) 241(25_19) |
| [102](#class-102) | 2 | 221(25_9) 239(25_17) |
| [103](#class-103) | 2 | 222(25_10) 243(25_21) |
| [104](#class-104) | 2 | 223(25_11) 248(25_26) |
| [105](#class-105) | 2 | 224(25_12) 247(25_25) |
| [106](#class-106) | 2 | 226(25_13) 246(25_24) |
| [107](#class-107) | 2 | 227(25_14) 245(25_23) |
| [108](#class-108) | 2 | 228(25_15) 250(25_28) |
| [109](#class-109) | 2 | 229(25_16) 249(25_27) |
| [110](#class-110) | 2 | 230(21_39) 256(21_41) |
| [111](#class-111) | 2 | 232(19_44) 255(19_49) |
| [112](#class-112) | 2 | 233(21_40) 258(21_42) |
| [113](#class-113) | 2 | 234(19_45) 257(19_50) |
| [114](#class-114) | 1 | 0(13_1) |
| [115](#class-115) | 1 | 1(15_1) |
| [116](#class-116) | 1 | 2(16_1) |
| [117](#class-117) | 1 | 5(14_1) |
| [118](#class-118) | 1 | 6(14_2) |
| [119](#class-119) | 1 | 15(16_2) |
| [120](#class-120) | 1 | 16(16_3) |
| [121](#class-121) | 1 | 48(18_2) |
| [122](#class-122) | 1 | 87(20_2) |
| [123](#class-123) | 1 | 93(21_3) |
| [124](#class-124) | 1 | 97(21_7) |
| [125](#class-125) | 1 | 121(21_28) |
| [126](#class-126) | 1 | 122(21_29) |

---

## Class 001

**8 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 4 | 21_1 | `YXYxyx` | `YYYYYYYYxxxxxxx` |
| 179 | 22_13 | `YXYxx` | `YYYYYYYYxyyyyyyyX` |
| 180 | 22_14 | `YXXYx` | `YYYYYYYYXyyyyyyyx` |
| 182 | 23_21 | `YXYxYx` | `YYYYYYYYxyyyyyyyX` |
| 186 | 21_36 | `YXyXYx` | `YYYYYYYXXXXXXXX` |
| 191 | 23_24 | `YXYXYx` | `YYYYYYYYXyyyyyyyx` |
| 196 | 18_6 | `YXYXyxx` | `YYYYYYxyXyx` |
| 197 | 18_7 | `YXYXyxx` | `YYYYYYYXXyx` |

### Why they are the same problem — 7 edges

**179 (22_13)  ≡  180 (22_14)** — *change of variables only*

Substitute `x -> X, y -> y` into **22_13** (`YXYxx`, `YYYYYYYYxyyyyyyyX`), then normalise:

```
  r1 = YXYxx
       substitute      ->  YxYXX
       rotate by 3     ->  YXXYx
                           = r1 of 22_14   [MATCH]
  r2 = YYYYYYYYxyyyyyyyX
       substitute      ->  YYYYYYYYXyyyyyyyx
                           = r2 of 22_14   [MATCH]
```

which is exactly **22_14** = (`YXXYx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

**179 (22_13)  ≡  182 (23_21)** — *change of variables only*

Substitute `x -> xY, y -> y` into **22_13** (`YXYxx`, `YYYYYYYYxyyyyyyyX`), then normalise:

```
  r1 = YXYxx
       substitute      ->  XYxYxY
       rotate by 1     ->  YXYxYx
                           = r1 of 23_21   [MATCH]
  r2 = YYYYYYYYxyyyyyyyX
       substitute      ->  YYYYYYYYxyyyyyyyX
                           = r2 of 23_21   [MATCH]
```

which is exactly **23_21** = (`YXYxYx`, `YYYYYYYYxyyyyyyyX`). No AC move was used.

**4 (21_1)  ≡  186 (21_36)** — *change of variables only*

Substitute `x -> Y, y -> x` into **21_1** (`YXYxyx`, `YYYYYYYYxxxxxxx`), then normalise:

```
  r1 = YXYxyx
       substitute      ->  XyXYxY
       rotate by 1     ->  YXyXYx
                           = r1 of 21_36   [MATCH]
  r2 = YYYYYYYYxxxxxxx
       substitute      ->  XXXXXXXXYYYYYYY
       rotate by 7     ->  YYYYYYYXXXXXXXX
                           = r2 of 21_36   [MATCH]
```

which is exactly **21_36** = (`YXyXYx`, `YYYYYYYXXXXXXXX`). No AC move was used.

**179 (22_13)  ≡  191 (23_24)** — *change of variables only*

Substitute `x -> XY, y -> y` into **22_13** (`YXYxx`, `YYYYYYYYxyyyyyyyX`), then normalise:

```
  r1 = YXYxx
       substitute      ->  xYXYXY
       rotate by 5     ->  YXYXYx
                           = r1 of 23_24   [MATCH]
  r2 = YYYYYYYYxyyyyyyyX
       substitute      ->  YYYYYYYYXyyyyyyyx
                           = r2 of 23_24   [MATCH]
```

which is exactly **23_24** = (`YXYXYx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

**196 (18_6)  ≡  179 (22_13)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 18_6
    start: (YXYXyxx, YYYYYYxyXyx)
    change of variables: x -> x, y -> Y
      r1 = YXYXyxx
           substitute      ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYYxyXyx
           substitute      ->  yyyyyyxYXYx
           invert          ->  XyxyXYYYYYY
           rotate by 6     ->  YYYYYYXyxyX
                               = r2
    => (YXXyxYx, YYYYYYXyxyX)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YXXyxYx
        rot_1(r2)        =  XYYYYYYXyxy
        concatenate      =  YXXyxYxXYYYYYYXyxy
        cancel inverses  =  YXXyxYYYYYYYXyxy
        reduce cyclically=  XyxYYYYYYYXy
        rotate by 9      =  YYYYYYYXyXyx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYYYXyxyX, YYYYYYYXyXyx)
    change of variables: x -> yyyyyyx, y -> Y
      r1 = YYYYYYXyxyX
           substitute      ->  yyyyyyXYxYXYYYYYY
           reduce          ->  XYxYX
           rotate by 2     ->  YXXYx
                               = r1
      r2 = YYYYYYYXyXyx
           substitute      ->  yyyyyyyXYYYYYYYXYx
           rotate by 10    ->  YYYYYYYXYxyyyyyyyX
                               = r2
    => (YXXYx, YYYYYYYXYxyyyyyyyX)
  right — 22_13
    start: (YXYxx, YYYYYYYYxyyyyyyyX)
    change of variables: x -> X, y -> y
      r1 = YXYxx
           substitute      ->  YxYXX
           rotate by 3     ->  YXXYx
                               = r1
      r2 = YYYYYYYYxyyyyyyyX
           substitute      ->  YYYYYYYYXyyyyyyyx
                               = r2
    => (YXXYx, YYYYYYYYXyyyyyyyx)

    AC move:  r2 <- rot_8(r2) . rot_2(r1^-1)
        rot_8(r2)        =  yyyyyyyxYYYYYYYYX
        rot_2(r1^-1)     =  xyXyx
        concatenate      =  yyyyyyyxYYYYYYYYXxyXyx
        cancel inverses  =  yyyyyyyxYYYYYYYXyx
        invert           =  XYxyyyyyyyXYYYYYYY
        rotate by 7      =  YYYYYYYXYxyyyyyyyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYx, YYYYYYYXYxyyyyyyyX)
    both meet at (YXXYx, YYYYYYYXYxyyyyyyyX)
```

**196 (18_6)  ≡  197 (18_7)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 18_6
    start: (YXYXyxx, YYYYYYxyXyx)
    change of variables: x -> x, y -> Y
      r1 = YXYXyxx
           substitute      ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYYxyXyx
           substitute      ->  yyyyyyxYXYx
           invert          ->  XyxyXYYYYYY
           rotate by 6     ->  YYYYYYXyxyX
                               = r2
    => (YXXyxYx, YYYYYYXyxyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYYYYXyxyX
        rot_1(r1)        =  xYXXyxY
        concatenate      =  YYYYYYXyxyXxYXXyxY
        cancel inverses  =  YYYYYYXyXyxY
        rotate by 1      =  YYYYYYYXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyxYx, YYYYYYYXyXyx)
    change of variables: x -> xY, y -> Y
      r1 = YXXyxYx
           substitute      ->  yyXyXYxxY
           reduce          ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYYYXyXyx
           substitute      ->  yyyyyyyyXXYxY
           reduce          ->  yyyyyyyXXYx
           invert          ->  XyxxYYYYYYY
           rotate by 7     ->  YYYYYYYXyxx
                               = r2
    => (YXXyxYx, YYYYYYYXyxx)
  right — 18_7
    start: (YXYXyxx, YYYYYYYXXyx)
    change of variables: x -> x, y -> Y
      r1 = YXYXyxx
           substitute      ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYYYXXyx
           substitute      ->  yyyyyyyXXYx
           invert          ->  XyxxYYYYYYY
           rotate by 7     ->  YYYYYYYXyxx
                               = r2
    => (YXXyxYx, YYYYYYYXyxx)
    both meet at (YXXyxYx, YYYYYYYXyxx)
```

**4 (21_1)  ≡  196 (18_6)** — *AC moves + change of variables*, 6 + 1 AC moves

```
  left  — 21_1
    start: (YXYxyx, YYYYYYYYxxxxxxx)
    => (YXYxyx, YYYYYYYYxxxxxxx)   [already Aut-minimal]

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYYYYYYxxxxxxx
        rot_0(r1^-1)     =  XYXyxy
        concatenate      =  YYYYYYYYxxxxxxxXYXyxy
        cancel inverses  =  YYYYYYYYxxxxxxYXyxy
        reduce cyclically=  YYYYYYYxxxxxxYXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYxyx, YYYYYYYxxxxxxYXyx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYYYYYxxxxxxYXyx
        rot_0(r1^-1)     =  XYXyxy
        concatenate      =  YYYYYYYxxxxxxYXyxXYXyxy
        cancel inverses  =  YYYYYYYxxxxxxYXXyxy
        reduce cyclically=  YYYYYYxxxxxxYXXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYxyx, YYYYYYxxxxxxYXXyx)

    AC move:  r2 <- rot_3(r2) . rot_2(r1^-1)
        rot_3(r2)        =  XyxYYYYYYxxxxxxYX
        rot_2(r1^-1)     =  xyXYXy
        concatenate      =  XyxYYYYYYxxxxxxYXxyXYXy
        cancel inverses  =  XyxYYYYYYxxxxxYXy
        rotate by 14     =  YYYYYYxxxxxYXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYxyx, YYYYYYxxxxxYXyXyx)

    AC move:  r2 <- rot_4(r2) . rot_2(r1^-1)
        rot_4(r2)        =  yXyxYYYYYYxxxxxYX
        rot_2(r1^-1)     =  xyXYXy
        concatenate      =  yXyxYYYYYYxxxxxYXxyXYXy
        cancel inverses  =  yXyxYYYYYYxxxxYXy
        rotate by 13     =  YYYYYYxxxxYXyyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYxyx, YYYYYYxxxxYXyyXyx)

    AC move:  r2 <- rot_5(r2) . rot_2(r1^-1)
        rot_5(r2)        =  yyXyxYYYYYYxxxxYX
        rot_2(r1^-1)     =  xyXYXy
        concatenate      =  yyXyxYYYYYYxxxxYXxyXYXy
        cancel inverses  =  yyXyxYYYYYYxxxYXy
        rotate by 12     =  YYYYYYxxxYXyyyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYxyx, YYYYYYxxxYXyyyXyx)

    AC move:  r2 <- rot_6(r2) . rot_2(r1^-1)
        rot_6(r2)        =  yyyXyxYYYYYYxxxYX
        rot_2(r1^-1)     =  xyXYXy
        concatenate      =  yyyXyxYYYYYYxxxYXxyXYXy
        cancel inverses  =  yyyXyxYYYYYYxxYXy
        rotate by 11     =  YYYYYYxxYXyyyyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYxyx, YYYYYYxxYXyyyyXyx)
  right — 18_6
    start: (YXYXyxx, YYYYYYxyXyx)
    change of variables: x -> x, y -> Y
      r1 = YXYXyxx
           substitute      ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYYxyXyx
           substitute      ->  yyyyyyxYXYx
           invert          ->  XyxyXYYYYYY
           rotate by 6     ->  YYYYYYXyxyX
                               = r2
    => (YXXyxYx, YYYYYYXyxyX)

    AC move:  r1 <- rot_5(r1) . rot_7(r2^-1)
        rot_5(r1)        =  XyxYxYX
        rot_7(r2^-1)     =  xyyyyyyxYXY
        concatenate      =  XyxYxYXxyyyyyyxYXY
        cancel inverses  =  XyxYxyyyyyxYXY
        invert           =  yxyXYYYYYXyXYx
        rotate by 10     =  YYYYYXyXYxyxyX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYYYXyxyX, YYYYYXyXYxyxyX)
    change of variables: x -> YYYYYx, y -> y
      r1 = YYYYYYXyxyX
           substitute      ->  YYYYYYXyxyXyyyyy
           reduce          ->  YXyxyX
           invert          ->  xYXYxy
           rotate by 5     ->  YXYxyx
                               = r1
      r2 = YYYYYXyXYxyxyX
           substitute      ->  YYYYYXyyyyyyXYxYYYYxyXyyyyy
           reduce          ->  XyyyyyyXYxYYYYxyX
           invert          ->  xYXyyyyXyxYYYYYYx
           rotate by 7     ->  YYYYYYxxYXyyyyXyx
                               = r2
    => (YXYxyx, YYYYYYxxYXyyyyXyx)
    both meet at (YXYxyx, YYYYYYxxYXyyyyXyx)
```

---

## Class 002

**6 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 181 | 21_34 | `YYXYxx` | `YYYYYYxYxYxYXyx` |
| 188 | 21_37 | `YYXXYx` | `YYxYxyxyXYXYXYX` |
| 195 | 15_12 | `YYXyyxx` | `YXXXyxYx` |
| 204 | 15_13 | `YYXXyyx` | `YXYXyxxx` |
| 225 | 15_14 | `YYXXyxx` | `YYYxyXyX` |
| 237 | 15_15 | `YYXXyxx` | `YYYxyxyX` |

### Why they are the same problem — 5 edges

**195 (15_12)  ≡  204 (15_13)** — *change of variables only*

Substitute `x -> x, y -> Y` into **15_12** (`YYXyyxx`, `YXXXyxYx`), then normalise:

```
  r1 = YYXyyxx
       substitute      ->  yyXYYxx
       invert          ->  XXyyxYY
       rotate by 2     ->  YYXXyyx
                           = r1 of 15_13   [MATCH]
  r2 = YXXXyxYx
       substitute      ->  yXXXYxyx
       invert          ->  XYXyxxxY
       rotate by 1     ->  YXYXyxxx
                           = r2 of 15_13   [MATCH]
```

which is exactly **15_13** = (`YYXXyyx`, `YXYXyxxx`). No AC move was used.

**195 (15_12)  ≡  225 (15_14)** — *change of variables only*

Substitute `x -> y, y -> x` into **15_12** (`YYXyyxx`, `YXXXyxYx`), then normalise:

```
  r1 = YYXyyxx
       substitute      ->  XXYxxyy
       invert          ->  YYXXyxx
                           = r1 of 15_14   [MATCH]
  r2 = YXXXyxYx
       substitute      ->  XYYYxyXy
       rotate by 7     ->  YYYxyXyX
                           = r2 of 15_14   [MATCH]
```

which is exactly **15_14** = (`YYXXyxx`, `YYYxyXyX`). No AC move was used.

**195 (15_12)  ≡  237 (15_15)** — *change of variables only*

Substitute `x -> Y, y -> x` into **15_12** (`YYXyyxx`, `YXXXyxYx`), then normalise:

```
  r1 = YYXyyxx
       substitute      ->  XXyxxYY
       rotate by 2     ->  YYXXyxx
                           = r1 of 15_15   [MATCH]
  r2 = YXXXyxYx
       substitute      ->  XyyyxYXY
       invert          ->  yxyXYYYx
       rotate by 4     ->  YYYxyxyX
                           = r2 of 15_15   [MATCH]
```

which is exactly **15_15** = (`YYXXyxx`, `YYYxyxyX`). No AC move was used.

**181 (21_34)  ≡  188 (21_37)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 21_34
    start: (YYXYxx, YYYYYYxYxYxYXyx)
    change of variables: x -> Yx, y -> x
      r1 = YYXYxx
           substitute      ->  XXXyXYxYx
           reduce          ->  XXyXYxY
           rotate by 1     ->  YXXyXYx
                               = r1
      r2 = YYYYYYxYxYxYXyx
           substitute      ->  XXXXXXYYYXyxYx
           reduce          ->  XXXXXYYYXyxY
           rotate by 7     ->  YYYXyxYXXXXX
                               = r2
    => (YXXyXYx, YYYXyxYXXXXX)

    AC move:  r2 <- rot_3(r2) . rot_3(r1^-1)
        rot_3(r2)        =  XXXYYYXyxYXX
        rot_3(r1^-1)     =  xxyXyxY
        concatenate      =  XXXYYYXyxYXXxxyXyxY
        cancel inverses  =  XXXYYYXyyxY
        rotate by 8      =  YYYXyyxYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYXyyxYXXX)

    AC move:  r2 <- rot_0(r2) . rot_2(r1^-1)
        rot_0(r2)        =  YYYXyyxYXXX
        rot_2(r1^-1)     =  xyXyxYx
        concatenate      =  YYYXyyxYXXXxyXyxYx
        cancel inverses  =  YYYXyyxYXXyXyxYx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYXyyxYXXyXyxYx)
    change of variables: x -> xy, y -> y
      r1 = YXXyXYx
           substitute      ->  YYXYXXYxy
           reduce          ->  YXYXXYx
                               = r1
      r2 = YYYXyyxYXXyXyxYx
           substitute      ->  YYYYXyyxYXYXXyxxy
           reduce          ->  YYYXyyxYXYXXyxx
                               = r2
    => (YXYXXYx, YYYXyyxYXYXXyxx)
  right — 21_37
    start: (YYXXYx, YYxYxyxyXYXYXYX)
    change of variables: x -> xY, y -> X
      r1 = YYXXYx
           substitute      ->  xxyXyxY
           invert          ->  yXYxYXX
           rotate by 3     ->  YXXyXYx
                               = r1
      r2 = YYxYxyxyXYXYXYX
           substitute      ->  xxxYxxYYXyyyyX
           reduce          ->  xxYxxYYXyyyy
           invert          ->  YYYYxyyXXyXX
                               = r2
    => (YXXyXYx, YYYYxyyXXyXX)

    AC move:  r2 <- rot_1(r2) . rot_5(r1^-1)
        rot_1(r2)        =  XYYYYxyyXXyX
        rot_5(r1^-1)     =  xYxxyXy
        concatenate      =  XYYYYxyyXXyXxYxxyXy
        cancel inverses  =  XYYYYxyyyXy
        rotate by 10     =  YYYYxyyyXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYYxyyyXyX)
    change of variables: x -> xy, y -> y
      r1 = YXXyXYx
           substitute      ->  YYXYXXYxy
           reduce          ->  YXYXXYx
                               = r1
      r2 = YYYYxyyyXyX
           substitute      ->  YYYYxyyyXX
                               = r2
    => (YXYXXYx, YYYYxyyyXX)

    AC move:  r2 <- rot_8(r2) . rot_6(r1^-1)
        rot_8(r2)        =  YYxyyyXXYY
        rot_6(r1^-1)     =  yxxyxyX
        concatenate      =  YYxyyyXXYYyxxyxyX
        cancel inverses  =  YYxyyyXXYxxyxyX
        invert           =  xYXYXXyxxYYYXyy
        rotate by 6      =  YYYXyyxYXYXXyxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYXyyxYXYXXyxx)
    both meet at (YXYXXYx, YYYXyyxYXYXXyxx)
```

**188 (21_37)  ≡  195 (15_12)** — *AC moves + change of variables*, 3 + 1 AC moves

```
  left  — 21_37
    start: (YYXXYx, YYxYxyxyXYXYXYX)
    change of variables: x -> xY, y -> X
      r1 = YYXXYx
           substitute      ->  xxyXyxY
           invert          ->  yXYxYXX
           rotate by 3     ->  YXXyXYx
                               = r1
      r2 = YYxYxyxyXYXYXYX
           substitute      ->  xxxYxxYYXyyyyX
           reduce          ->  xxYxxYYXyyyy
           invert          ->  YYYYxyyXXyXX
                               = r2
    => (YXXyXYx, YYYYxyyXXyXX)

    AC move:  r2 <- rot_1(r2) . rot_5(r1^-1)
        rot_1(r2)        =  XYYYYxyyXXyX
        rot_5(r1^-1)     =  xYxxyXy
        concatenate      =  XYYYYxyyXXyXxYxxyXy
        cancel inverses  =  XYYYYxyyyXy
        rotate by 10     =  YYYYxyyyXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYYxyyyXyX)
    change of variables: x -> xy, y -> y
      r1 = YXXyXYx
           substitute      ->  YYXYXXYxy
           reduce          ->  YXYXXYx
                               = r1
      r2 = YYYYxyyyXyX
           substitute      ->  YYYYxyyyXX
                               = r2
    => (YXYXXYx, YYYYxyyyXX)

    AC move:  r2 <- rot_0(r2) . rot_5(r1^-1)
        rot_0(r2)        =  YYYYxyyyXX
        rot_5(r1^-1)     =  xxyxyXy
        concatenate      =  YYYYxyyyXXxxyxyXy
        cancel inverses  =  YYYYxyyyyxyXy
        reduce cyclically=  YYYxyyyyxyX
        invert           =  xYXYYYYXyyy
        rotate by 8      =  YYYYXyyyxYX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYXyyyxYX)
    change of variables: x -> Yx, y -> y
      r1 = YXYXXYx
           substitute      ->  YXXyXYx
                               = r1
      r2 = YYYYXyyyxYX
           substitute      ->  YYYYXyyyxYXy
           reduce          ->  YYYXyyyxYX
                               = r2
    => (YXXyXYx, YYYXyyyxYX)

    AC move:  r1 <- rot_3(r1) . rot_5(r2^-1)
        rot_3(r1)        =  XYxYXXy
        rot_5(r2^-1)     =  YxyyyxyXYY
        concatenate      =  XYxYXXyYxyyyxyXYY
        cancel inverses  =  XYxYXyyyxyXYY
        invert           =  yyxYXYYYxyXyx
        rotate by 8      =  YYYxyXyxyyxYX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYXyyyxYX, YYYxyXyxyyxYX)
    change of variables: x -> xxy, y -> X
      r1 = YYYXyyyxYX
           substitute      ->  xxxYXXXyxYXX
           reduce          ->  xYXXXyxY
           rotate by 7     ->  YXXXyxYx
                               = r1
      r2 = YYYxyXyxyyxYX
           substitute      ->  xxxxxyXYXyyxYXX
           reduce          ->  xxxyXYXyyxY
           invert          ->  yXYYxyxYXXX
           rotate by 9     ->  YYxyxYXXXyX
                               = r2
    => (YXXXyxYx, YYxyxYXXXyX)
  right — 15_12
    start: (YYXyyxx, YXXXyxYx)
    change of variables: x -> y, y -> x
      r1 = YYXyyxx
           substitute      ->  XXYxxyy
           invert          ->  YYXXyxx
                               = r1
      r2 = YXXXyxYx
           substitute      ->  XYYYxyXy
           rotate by 7     ->  YYYxyXyX
                               = r2
    => (YYXXyxx, YYYxyXyX)

    AC move:  r1 <- rot_0(r1) . rot_3(r2)
        rot_0(r1)        =  YYXXyxx
        rot_3(r2)        =  XyXYYYxy
        concatenate      =  YYXXyxxXyXYYYxy
        cancel inverses  =  YYXXyxyXYYYxy
        reduce cyclically=  YXXyxyXYYYx
        rotate by 4      =  YYYxYXXyxyX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYxyXyX, YYYxYXXyxyX)
    change of variables: x -> y, y -> x
      r1 = YYYxyXyX
           substitute      ->  XXXyxYxY
           rotate by 1     ->  YXXXyxYx
                               = r1
      r2 = YYYxYXXyxyX
           substitute      ->  XXXyXYYxyxY
           rotate by 6     ->  YYxyxYXXXyX
                               = r2
    => (YXXXyxYx, YYxyxYXXXyX)
    both meet at (YXXXyxYx, YYxyxYXXXyX)
```

---

## Class 003

**5 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 183 | 19_37 | `YYXXyx` | `YXyXyXyxxYxYx` |
| 187 | 19_38 | `YYXyxx` | `YXYXYxYxxxxxx` |
| 198 | 17_41 | `YYXYXyx` | `YXYxxxyXXX` |
| 203 | 17_42 | `YYXyxYx` | `YXXXyXyxxx` |
| 212 | 20_12 | `YYXyxyx` | `YYYXXyyXyxYXX` |

### Why they are the same problem — 4 edges

**183 (19_37)  ≡  198 (17_41)** — *change of variables only*

Substitute `x -> xy, y -> y` into **19_37** (`YYXXyx`, `YXyXyXyxxYxYx`), then normalise:

```
  r1 = YYXXyx
       substitute      ->  YYYXYXyxy
       reduce          ->  YYXYXyx
                           = r1 of 17_41   [MATCH]
  r2 = YXyXyXyxxYxYx
       substitute      ->  YYXXXyxyxxxy
       reduce          ->  YXXXyxyxxx
       invert          ->  XXXYXYxxxy
       rotate by 7     ->  YXYxxxyXXX
                           = r2 of 17_41   [MATCH]
```

which is exactly **17_41** = (`YYXYXyx`, `YXYxxxyXXX`). No AC move was used.

**183 (19_37)  ≡  203 (17_42)** — *change of variables only*

Substitute `x -> xY, y -> Y` into **19_37** (`YYXXyx`, `YXyXyXyxxYxYx`), then normalise:

```
  r1 = YYXXyx
       substitute      ->  yyyXyXYxY
       reduce          ->  yyXyXYx
       invert          ->  XyxYxYY
       rotate by 2     ->  YYXyxYx
                           = r1 of 17_42   [MATCH]
  r2 = YXyXyXyxxYxYx
       substitute      ->  yyXXXYxYxxxY
       reduce          ->  yXXXYxYxxx
       invert          ->  XXXyXyxxxY
       rotate by 1     ->  YXXXyXyxxx
                           = r2 of 17_42   [MATCH]
```

which is exactly **17_42** = (`YYXyxYx`, `YXXXyXyxxx`). No AC move was used.

**187 (19_38)  ≡  212 (20_12)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 19_38
    start: (YYXyxx, YXYXYxYxxxxxx)
    change of variables: x -> x, y -> Y
      r1 = YYXyxx
           substitute      ->  yyXYxx
           invert          ->  XXyxYY
           rotate by 2     ->  YYXXyx
                               = r1
      r2 = YXYXYxYxxxxxx
           substitute      ->  yXyXyxyxxxxxx
           invert          ->  XXXXXXYXYxYxY
           rotate by 7     ->  YXYxYxYXXXXXX
                               = r2
    => (YYXXyx, YXYxYxYXXXXXX)

    AC move:  r2 <- rot_9(r2) . rot_3(r1)
        rot_9(r2)        =  YxYXXXXXXYXYx
        rot_3(r1)        =  XyxYYX
        concatenate      =  YxYXXXXXXYXYxXyxYYX
        cancel inverses  =  YxYXXXXXXYYYX
        rotate by 4      =  YYYXYxYXXXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYYXYxYXXXXXX)

    AC move:  r2 <- rot_1(r2) . rot_4(r1^-1)
        rot_1(r2)        =  XYYYXYxYXXXXX
        rot_4(r1^-1)     =  xxyyXY
        concatenate      =  XYYYXYxYXXXXXxxyyXY
        cancel inverses  =  XYYYXYxYXXXyyXY
        rotate by 14     =  YYYXYxYXXXyyXYX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYYXYxYXXXyyXYX)
  right — 20_12
    start: (YYXyxyx, YYYXXyyXyxYXX)
    change of variables: x -> Y, y -> x
      r1 = YYXyxyx
           substitute      ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYXXyyXyxYXX
           substitute      ->  XXXyyxxyxYXyy
           invert          ->  YYxyXYXXYYxxx
                               = r2
    => (YXXyxYx, YYxyXYXXYYxxx)

    AC move:  r2 <- rot_10(r2) . rot_5(r1)
        rot_10(r2)       =  yXYXXYYxxxYYx
        rot_5(r1)        =  XyxYxYX
        concatenate      =  yXYXXYYxxxYYxXyxYxYX
        cancel inverses  =  yXYXXYYxxxYxYxYX
        rotate by 11     =  YYxxxYxYxYXyXYXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyxYx, YYxxxYxYxYXyXYXX)
    change of variables: x -> Y, y -> XY
      r1 = YXXyxYx
           substitute      ->  yxyyXYxY
           reduce          ->  xyyXYx
           invert          ->  XyxYYX
           rotate by 3     ->  YYXXyx
                               = r1
      r2 = YYxxxYxYxYXyXYXX
           substitute      ->  yxyxYYxxxyXyxyy
           invert          ->  YYXYxYXXXyyXYXY
           rotate by 1     ->  YYYXYxYXXXyyXYX
                               = r2
    => (YYXXyx, YYYXYxYXXXyyXYX)
    both meet at (YYXXyx, YYYXYxYXXXyyXYX)
```

**183 (19_37)  ≡  187 (19_38)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 19_37
    start: (YYXXyx, YXyXyXyxxYxYx)
    change of variables: x -> X, y -> yX
      r1 = YYXXyx
           substitute      ->  xYxYxxyXX
           reduce          ->  YxYxxyX
           invert          ->  xYXXyXy
           rotate by 6     ->  YXXyXyx
                               = r1
      r2 = YXyXyXyxxYxYx
           substitute      ->  xYxyyyXXYYX
           reduce          ->  YxyyyXXYY
           invert          ->  yyxxYYYXy
           rotate by 5     ->  YYYXyyyxx
                               = r2
    => (YXXyXyx, YYYXyyyxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYXyyyxx
        rot_0(r1^-1)     =  XYxYxxy
        concatenate      =  YYYXyyyxxXYxYxxy
        cancel inverses  =  YYYXyyyxYxYxxy
        reduce cyclically=  YYXyyyxYxYxx
        invert           =  XXyXyXYYYxyy
        rotate by 6      =  YYYxyyXXyXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXyx, YYYxyyXXyXyX)
    change of variables: x -> Xy, y -> y
      r1 = YXXyXyx
           substitute      ->  YYxYxxyXy
           reduce          ->  YxYxxyX
           invert          ->  xYXXyXy
           rotate by 6     ->  YXXyXyx
                               = r1
      r2 = YYYxyyXXyXyX
           substitute      ->  YYYXyyxYxxx
                               = r2
    => (YXXyXyx, YYYXyyxYxxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYXyyxYxxx
        rot_0(r1^-1)     =  XYxYxxy
        concatenate      =  YYYXyyxYxxxXYxYxxy
        cancel inverses  =  YYYXyyxYxxYxYxxy
        reduce cyclically=  YYXyyxYxxYxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXyx, YYXyyxYxxYxYxx)
    change of variables: x -> y, y -> Xy
      r1 = YXXyXyx
           substitute      ->  YxYYXXyy
           reduce          ->  xYYXXy
           rotate by 5     ->  YYXXyx
                               = r1
      r2 = YYXyyxYxxYxYxx
           substitute      ->  YxYxYXyXyxyxxyy
           reduce          ->  xYxYXyXyxyxxy
           invert          ->  YXXYXYxYxyXyX
           rotate by 10    ->  YXYxYxyXyXYXX
                               = r2
    => (YYXXyx, YXYxYxyXyXYXX)
  right — 19_38
    start: (YYXyxx, YXYXYxYxxxxxx)
    change of variables: x -> x, y -> Y
      r1 = YYXyxx
           substitute      ->  yyXYxx
           invert          ->  XXyxYY
           rotate by 2     ->  YYXXyx
                               = r1
      r2 = YXYXYxYxxxxxx
           substitute      ->  yXyXyxyxxxxxx
           invert          ->  XXXXXXYXYxYxY
           rotate by 7     ->  YXYxYxYXXXXXX
                               = r2
    => (YYXXyx, YXYxYxYXXXXXX)

    AC move:  r2 <- rot_4(r2) . rot_4(r1^-1)
        rot_4(r2)        =  XXXXYXYxYxYXX
        rot_4(r1^-1)     =  xxyyXY
        concatenate      =  XXXXYXYxYxYXXxxyyXY
        cancel inverses  =  XXXXYXYxYxyXY
        rotate by 9      =  YXYxYxyXYXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YXYxYxyXYXXXX)
    change of variables: x -> x, y -> Xy
      r1 = YYXXyx
           substitute      ->  YxYXXyx
           rotate by 5     ->  YXXyxYx
                               = r1
      r2 = YXYxYxyXYXXXX
           substitute      ->  YYxxYxyXYXXX
                               = r2
    => (YXXyxYx, YYxxYxyXYXXX)

    AC move:  r2 <- rot_1(r2) . rot_3(r1^-1)
        rot_1(r2)        =  XYYxxYxyXYXX
        rot_3(r1^-1)     =  xxyXyXY
        concatenate      =  XYYxxYxyXYXXxxyXyXY
        cancel inverses  =  XYYxxYxyXXyXY
        rotate by 12     =  YYxxYxyXXyXYX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyxYx, YYxxYxyXXyXYX)
    change of variables: x -> x, y -> yx
      r1 = YXXyxYx
           substitute      ->  XYXXyxYx
           reduce          ->  YXXyxY
           rotate by 1     ->  YYXXyx
                               = r1
      r2 = YYxxYxyXXyXYX
           substitute      ->  XYXYxYxyXyXYX
           rotate by 12    ->  YXYxYxyXyXYXX
                               = r2
    => (YYXXyx, YXYxYxyXyXYXX)
    both meet at (YYXXyx, YXYxYxyXyXYXX)
```

---

## Class 004

**4 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 3 | 17_1 | `YXYXyxx` | `YYYYYxyXyX` |
| 123 | 20_8 | `YXYxx` | `YYYYYYYXyyyyyyx` |
| 124 | 20_9 | `YXXYx` | `YYYYYYYXyyyyyyx` |
| 129 | 17_35 | `YYXyxyx` | `YXyXYxxxxx` |

### Why they are the same problem — 3 edges

**123 (20_8)  ≡  124 (20_9)** — *change of variables only*

Substitute `x -> x, y -> Y` into **20_8** (`YXYxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXYxx
       substitute      ->  yXyxx
       invert          ->  XXYxY
       rotate by 1     ->  YXXYx
                           = r1 of 20_9   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 20_9   [MATCH]
```

which is exactly **20_9** = (`YXXYx`, `YYYYYYYXyyyyyyx`). No AC move was used.

**3 (17_1)  ≡  129 (17_35)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 17_1
    start: (YXYXyxx, YYYYYxyXyX)
    change of variables: x -> x, y -> Y
      r1 = YXYXyxx
           substitute      ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYxyXyX
           substitute      ->  yyyyyxYXYX
           invert          ->  xyxyXYYYYY
           rotate by 5     ->  YYYYYxyxyX
                               = r2
    => (YXXyxYx, YYYYYxyxyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYYYxyxyX
        rot_1(r1)        =  xYXXyxY
        concatenate      =  YYYYYxyxyXxYXXyxY
        cancel inverses  =  YYYYYxyXyxY
        rotate by 1      =  YYYYYYxyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyxYx, YYYYYYxyXyx)
    change of variables: x -> xY, y -> Y
      r1 = YXXyxYx
           substitute      ->  yyXyXYxxY
           reduce          ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYYxyXyx
           substitute      ->  yyyyyyxYXYxY
           reduce          ->  yyyyyxYXYx
           invert          ->  XyxyXYYYYY
           rotate by 5     ->  YYYYYXyxyX
                               = r2
    => (YXXyxYx, YYYYYXyxyX)
  right — 17_35
    start: (YYXyxyx, YXyXYxxxxx)
    change of variables: x -> Y, y -> x
      r1 = YYXyxyx
           substitute      ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YXyXYxxxxx
           substitute      ->  XyxyXYYYYY
           rotate by 5     ->  YYYYYXyxyX
                               = r2
    => (YXXyxYx, YYYYYXyxyX)
    both meet at (YXXyxYx, YYYYYXyxyX)
```

**123 (20_8)  ≡  3 (17_1)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 20_8
    start: (YXYxx, YYYYYYYXyyyyyyx)
    change of variables: x -> x, y -> Y
      r1 = YXYxx
           substitute      ->  yXyxx
           invert          ->  XXYxY
           rotate by 1     ->  YXXYx
                               = r1
      r2 = YYYYYYYXyyyyyyx
           substitute      ->  yyyyyyyXYYYYYYx
           invert          ->  XyyyyyyxYYYYYYY
           rotate by 7     ->  YYYYYYYXyyyyyyx
                               = r2
    => (YXXYx, YYYYYYYXyyyyyyx)

    AC move:  r2 <- rot_0(r2) . rot_3(r1)
        rot_0(r2)        =  YYYYYYYXyyyyyyx
        rot_3(r1)        =  XYxYX
        concatenate      =  YYYYYYYXyyyyyyxXYxYX
        cancel inverses  =  YYYYYYYXyyyyyxYX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYx, YYYYYYYXyyyyyxYX)
    change of variables: x -> xxxxxxy, y -> X
      r2 = YYYYYYYXyyyyyxYX
           substitute      ->  xxxxxxxYXXXXXyxYXXXXXX
           reduce          ->  xYXXXXXyxY
           rotate by 9     ->  YXXXXXyxYx
                               = r1
      r1 = YXXYx
           substitute      ->  xYXXXXXXYxy
           invert          ->  YXyxxxxxxyX
                               = r2
    => (YXXXXXyxYx, YXyxxxxxxyX)
  right — 17_1
    start: (YXYXyxx, YYYYYxyXyX)
    change of variables: x -> x, y -> Y
      r1 = YXYXyxx
           substitute      ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYYYxyXyX
           substitute      ->  yyyyyxYXYX
           invert          ->  xyxyXYYYYY
           rotate by 5     ->  YYYYYxyxyX
                               = r2
    => (YXXyxYx, YYYYYxyxyX)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YXXyxYx
        rot_1(r2)        =  XYYYYYxyxy
        concatenate      =  YXXyxYxXYYYYYxyxy
        cancel inverses  =  YXXyxYYYYYYxyxy
        reduce cyclically=  XyxYYYYYYxy
        rotate by 8      =  YYYYYYxyXyx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYYxyxyX, YYYYYYxyXyx)
    change of variables: x -> y, y -> X
      r1 = YYYYYxyxyX
           substitute      ->  xxxxxyXyXY
           invert          ->  yxYxYXXXXX
           rotate by 6     ->  YXXXXXyxYx
                               = r1
      r2 = YYYYYYxyXyx
           substitute      ->  xxxxxxyXYXy
           rotate by 3     ->  YXyxxxxxxyX
                               = r2
    => (YXXXXXyxYx, YXyxxxxxxyX)
    both meet at (YXXXXXyxYx, YXyxxxxxxyX)
```

---

## Class 005

**4 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 184 | 23_22 | `YYxxYX` | `YYYYYxyXyXYXyyyxx` |
| 190 | 23_23 | `YYxYXX` | `YYYYYYYYXyyyyyxYX` |
| 231 | 19_43 | `YYXyyxxYX` | `YYYYYxyXyX` |
| 238 | 19_48 | `YYxYXXyyx` | `YYYYYxyxyX` |

### Why they are the same problem — 3 edges

**231 (19_43)  ≡  238 (19_48)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_43** (`YYXyyxxYX`, `YYYYYxyXyX`), then normalise:

```
  r1 = YYXyyxxYX
       substitute      ->  yyXYYxxyX
       invert          ->  xYXXyyxYY
       rotate by 2     ->  YYxYXXyyx
                           = r1 of 19_48   [MATCH]
  r2 = YYYYYxyXyX
       substitute      ->  yyyyyxYXYX
       invert          ->  xyxyXYYYYY
       rotate by 5     ->  YYYYYxyxyX
                           = r2 of 19_48   [MATCH]
```

which is exactly **19_48** = (`YYxYXXyyx`, `YYYYYxyxyX`). No AC move was used.

**190 (23_23)  ≡  231 (19_43)** — *pure AC path*, 1 + 0 AC moves

```
  left  — 23_23
    start: (YYxYXX, YYYYYYYYXyyyyyxYX)
    change of variables: x -> xxxxxxxy, y -> X
      r2 = YYYYYYYYXyyyyyxYX
           substitute      ->  xxxxxxxxYXXXXXyxYXXXXXXX
           reduce          ->  xYXXXXXyxY
           rotate by 9     ->  YXXXXXyxYx
                               = r1
      r1 = YYxYXX
           substitute      ->  xxxxxxxxxyxYXXXXXXXYXXXXXXX
           reduce          ->  xxyxYXXXXXXXY
           invert          ->  yxxxxxxxyXYXX
           rotate by 3     ->  YXXyxxxxxxxyX
                               = r2
    => (YXXXXXyxYx, YXXyxxxxxxxyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YXXyxxxxxxxyX
        rot_1(r1)        =  xYXXXXXyxY
        concatenate      =  YXXyxxxxxxxyXxYXXXXXyxY
        cancel inverses  =  YXXyxxyxY
        rotate by 1      =  YYXXyxxyx
                            ^ the new r1
        r1 is untouched by the move (it becomes r2: the two relators sort into the other order)
    => (YYXXyxxyx, YXXXXXyxYx)
  right — 19_43
    start: (YYXyyxxYX, YYYYYxyXyX)
    change of variables: x -> y, y -> x
      r1 = YYXyyxxYX
           substitute      ->  XXYxxyyXY
           invert          ->  yxYYXXyxx
           rotate by 7     ->  YYXXyxxyx
                               = r1
      r2 = YYYYYxyXyX
           substitute      ->  XXXXXyxYxY
           rotate by 1     ->  YXXXXXyxYx
                               = r2
    => (YYXXyxxyx, YXXXXXyxYx)
    both meet at (YYXXyxxyx, YXXXXXyxYx)
```

Every step is an AC move — no change of variables inside the path. So `23_23 ~AC psi(19_43)` with `psi: x -> yyyyyyyx, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `19_43`, not to `19_43` itself.

**184 (23_22)  ≡  190 (23_23)** — *AC moves + change of variables*, 10 + 3 AC moves

```
  left  — 23_22
    start: (YYxxYX, YYYYYxyXyXYXyyyxx)
    change of variables: x -> X, y -> y
      r1 = YYxxYX
           substitute      ->  YYXXYx
                               = r1
      r2 = YYYYYxyXyXYXyyyxx
           substitute      ->  YYYYYXyxyxYxyyyXX
                               = r2
    => (YYXXYx, YYYYYXyxyxYxyyyXX)

    AC move:  r2 <- rot_1(r2) . rot_1(r1)
        rot_1(r2)        =  XYYYYYXyxyxYxyyyX
        rot_1(r1)        =  xYYXXY
        concatenate      =  XYYYYYXyxyxYxyyyXxYYXXY
        cancel inverses  =  XYYYYYXyxyxYxyXXY
        rotate by 16     =  YYYYYXyxyxYxyXXYX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXYx, YYYYYXyxyxYxyXXYX)
    change of variables: x -> xY, y -> X
      r1 = YYXXYx
           substitute      ->  xxyXyxY
           invert          ->  yXYxYXX
           rotate by 3     ->  YXXyXYx
                               = r1
      r2 = YYYYYXyxyxYxyXXYX
           substitute      ->  xxxxxyXYYxxYXyXyyX
           reduce          ->  xxxxyXYYxxYXyXyy
           invert          ->  YYxYxyXXyyxYXXXX
                               = r2
    => (YXXyXYx, YYxYxyXXyyxYXXXX)

    AC move:  r2 <- rot_2(r2) . rot_3(r1^-1)
        rot_2(r2)        =  XXYYxYxyXXyyxYXX
        rot_3(r1^-1)     =  xxyXyxY
        concatenate      =  XXYYxYxyXXyyxYXXxxyXyxY
        cancel inverses  =  XXYYxYxyXXyyyxY
        invert           =  yXYYYxxYXyXyyxx
        rotate by 13     =  YYYxxYXyXyyxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYxxYXyXyyxxyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYxxYXyXyyxxyX
        rot_1(r1)        =  xYXXyXY
        concatenate      =  YYYxxYXyXyyxxyXxYXXyXY
        cancel inverses  =  YYYxxYXyXyyyXY
        rotate by 1      =  YYYYxxYXyXyyyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYYxxYXyXyyyX)
    change of variables: x -> xy, y -> y
      r1 = YXXyXYx
           substitute      ->  YYXYXXYxy
           reduce          ->  YXYXXYx
                               = r1
      r2 = YYYYxxYXyXyyyX
           substitute      ->  YYYYxyxYXXyyX
                               = r2
    => (YXYXXYx, YYYYxyxYXXyyX)

    AC move:  r2 <- rot_4(r2) . rot_2(r1^-1)
        rot_4(r2)        =  XyyXYYYYxyxYX
        rot_2(r1^-1)     =  xyXyxxy
        concatenate      =  XyyXYYYYxyxYXxyXyxxy
        cancel inverses  =  XyyXYYYYxyyxxy
        rotate by 10     =  YYYYxyyxxyXyyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYxyyxxyXyyX)

    AC move:  r2 <- rot_2(r2) . rot_2(r1)
        rot_2(r2)        =  yXYYYYxyyxxyXy
        rot_2(r1)        =  YxYXYXX
        concatenate      =  yXYYYYxyyxxyXyYxYXYXX
        cancel inverses  =  yXYYYYxyyxYXX
        rotate by 11     =  YYYYxyyxYXXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYxyyxYXXyX)

    AC move:  r2 <- rot_3(r2) . rot_2(r1^-1)
        rot_3(r2)        =  XyXYYYYxyyxYX
        rot_2(r1^-1)     =  xyXyxxy
        concatenate      =  XyXYYYYxyyxYXxyXyxxy
        cancel inverses  =  XyXYYYYxyyyxxy
        rotate by 11     =  YYYYxyyyxxyXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYxyyyxxyXyX)

    AC move:  r2 <- rot_1(r2) . rot_2(r1)
        rot_1(r2)        =  XYYYYxyyyxxyXy
        rot_2(r1)        =  YxYXYXX
        concatenate      =  XYYYYxyyyxxyXyYxYXYXX
        cancel inverses  =  XYYYYxyyyxYXX
        rotate by 12     =  YYYYxyyyxYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYxyyyxYXXX)

    AC move:  r2 <- rot_0(r2) . rot_5(r1^-1)
        rot_0(r2)        =  YYYYxyyyxYXXX
        rot_5(r1^-1)     =  xxyxyXy
        concatenate      =  YYYYxyyyxYXXXxxyxyXy
        cancel inverses  =  YYYYxyyyxYXyxyXy
        reduce cyclically=  YYYxyyyxYXyxyX
        invert           =  xYXYxyXYYYXyyy
        rotate by 7      =  YYYXyyyxYXYxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYXyyyxYXYxyX)
    change of variables: x -> Yx, y -> y
      r1 = YXYXXYx
           substitute      ->  YXXyXYx
                               = r1
      r2 = YYYXyyyxYXYxyX
           substitute      ->  YYYXyyyxYXYxyXy
           reduce          ->  YYXyyyxYXYxyX
           invert          ->  xYXyxyXYYYxyy
           rotate by 6     ->  YYYxyyxYXyxyX
                               = r2
    => (YXXyXYx, YYYxyyxYXyxyX)

    AC move:  r2 <- rot_0(r2) . rot_5(r1^-1)
        rot_0(r2)        =  YYYxyyxYXyxyX
        rot_5(r1^-1)     =  xYxxyXy
        concatenate      =  YYYxyyxYXyxyXxYxxyXy
        cancel inverses  =  YYYxyyxYXyxxxyXy
        reduce cyclically=  YYxyyxYXyxxxyX
        invert           =  xYXXXYxyXYYXyy
        rotate by 5      =  YYXyyxYXXXYxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYXyyxYXXXYxyX)

    AC move:  r2 <- rot_7(r2) . rot_4(r1)
        rot_7(r2)        =  XXXYxyXYYXyyxY
        rot_4(r1)        =  yXYxYXX
        concatenate      =  XXXYxyXYYXyyxYyXYxYXX
        cancel inverses  =  XXXYxyXYYXyxYXX
        rotate by 8      =  YYXyxYXXXXXYxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYXyxYXXXXXYxyX)
  right — 23_23
    start: (YYxYXX, YYYYYYYYXyyyyyxYX)
    change of variables: x -> xxxxxxxy, y -> X
      r2 = YYYYYYYYXyyyyyxYX
           substitute      ->  xxxxxxxxYXXXXXyxYXXXXXXX
           reduce          ->  xYXXXXXyxY
           rotate by 9     ->  YXXXXXyxYx
                               = r1
      r1 = YYxYXX
           substitute      ->  xxxxxxxxxyxYXXXXXXXYXXXXXXX
           reduce          ->  xxyxYXXXXXXXY
           invert          ->  yxxxxxxxyXYXX
           rotate by 3     ->  YXXyxxxxxxxyX
                               = r2
    => (YXXXXXyxYx, YXXyxxxxxxxyX)

    AC move:  r1 <- rot_2(r1) . rot_5(r2^-1)
        rot_2(r1)        =  YxYXXXXXyx
        rot_5(r2^-1)     =  XYxxyxYXXXXXX
        concatenate      =  YxYXXXXXyxXYxxyxYXXXXXX
        cancel inverses  =  YxYXXXyxYXXXXXX
        rotate by 13     =  YXXXyxYXXXXXXYx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YXXyxxxxxxxyX, YXXXyxYXXXXXXYx)
    change of variables: x -> X, y -> xxxxxxy
      r1 = YXXyxxxxxxxyX
           substitute      ->  YxxyXyx
           invert          ->  XYxYXXy
           rotate by 4     ->  YXXyXYx
                               = r1
      r2 = YXXXyxYXXXXXXYx
           substitute      ->  YxxxyXYYXXXXXXX
           rotate by 9     ->  YYXXXXXXXYxxxyX
                               = r2
    => (YXXyXYx, YYXXXXXXXYxxxyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYXXXXXXXYxxxyX
        rot_1(r1)        =  xYXXyXY
        concatenate      =  YYXXXXXXXYxxxyXxYXXyXY
        cancel inverses  =  YYXXXXXXXYxyXY
        rotate by 1      =  YYYXXXXXXXYxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYXXXXXXXYxyX)

    AC move:  r2 <- rot_9(r2) . rot_3(r1^-1)
        rot_9(r2)        =  XXXXXYxyXYYYXX
        rot_3(r1^-1)     =  xxyXyxY
        concatenate      =  XXXXXYxyXYYYXXxxyXyxY
        cancel inverses  =  XXXXXYxyXYYXyxY
        rotate by 6      =  YYXyxYXXXXXYxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYXyxYXXXXXYxyX)
    both meet at (YXXyXYx, YYXyxYXXXXXYxyX)
```

---

## Class 006

**4 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 201 | 19_40 | `YYYxxYX` | `YXyxxxyXyXyX` |
| 211 | 19_42 | `YYYxYXX` | `YXYXYXyXYxxx` |
| 236 | 19_47 | `YYYYxyxyX` | `YYxYXXYxyx` |
| 259 | 19_51 | `YYYYxyXX` | `YXyxxyXyXYx` |

### Why they are the same problem — 3 edges

**201 (19_40)  ≡  211 (19_42)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_40** (`YYYxxYX`, `YXyxxxyXyXyX`), then normalise:

```
  r1 = YYYxxYX
       substitute      ->  yyyxxyX
       invert          ->  xYXXYYY
       rotate by 3     ->  YYYxYXX
                           = r1 of 19_42   [MATCH]
  r2 = YXyxxxyXyXyX
       substitute      ->  yXYxxxYXYXYX
       rotate by 6     ->  YXYXYXyXYxxx
                           = r2 of 19_42   [MATCH]
```

which is exactly **19_42** = (`YYYxYXX`, `YXYXYXyXYxxx`). No AC move was used.

**236 (19_47)  ≡  259 (19_51)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 19_47
    start: (YYYYxyxyX, YYxYXXYxyx)
    change of variables: x -> y, y -> X
      r1 = YYYYxyxyX
           substitute      ->  xxxxyXyXY
           invert          ->  yxYxYXXXX
           rotate by 5     ->  YXXXXyxYx
                               = r1
      r2 = YYxYXXYxyx
           substitute      ->  xxyxYYxyXy
           rotate by 6     ->  YYxyXyxxyx
                               = r2
    => (YXXXXyxYx, YYxyXyxxyx)

    AC move:  r2 <- rot_1(r2) . rot_0(r1)
        rot_1(r2)        =  xYYxyXyxxy
        rot_0(r1)        =  YXXXXyxYx
        concatenate      =  xYYxyXyxxyYXXXXyxYx
        cancel inverses  =  xYYxyXyXXyxYx
        rotate by 12     =  YYxyXyXXyxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXXyxYx, YYxyXyXXyxYxx)
    change of variables: x -> x, y -> yx
      r1 = YXXXXyxYx
           substitute      ->  XYXXXXyxYx
           reduce          ->  YXXXXyxY
           rotate by 1     ->  YYXXXXyx
                               = r1
      r2 = YYxyXyXXyxYxx
           substitute      ->  XYXYxyyXyxYxx
           reduce          ->  YXYxyyXyxYx
           invert          ->  XyXYxYYXyxy
           rotate by 6     ->  YYXyxyXyXYx
                               = r2
    => (YYXXXXyx, YYXyxyXyXYx)

    AC move:  r2 <- rot_7(r2) . rot_7(r1)
        rot_7(r2)        =  xyXyXYxYYXy
        rot_7(r1)        =  YXXXXyxY
        concatenate      =  xyXyXYxYYXyYXXXXyxY
        cancel inverses  =  xyXyXYxYYXXXXXyxY
        rotate by 10     =  YYXXXXXyxYxyXyXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyx, YYXXXXXyxYxyXyXYx)
    change of variables: x -> X, y -> yX
      r1 = YYXXXXyx
           substitute      ->  xYxYxxxxyXX
           reduce          ->  YxYxxxxyX
           invert          ->  xYXXXXyXy
           rotate by 8     ->  YXXXXyXyx
                               = r1
      r2 = YYXXXXXyxYxyXyXYx
           substitute      ->  xYxYxxxxxyXYXyyxYX
           reduce          ->  YxYxxxxxyXYXyyxY
           rotate by 1     ->  YYxYxxxxxyXYXyyx
                               = r2
    => (YXXXXyXyx, YYxYxxxxxyXYXyyx)
  right — 19_51
    start: (YYYYxyXX, YXyxxyXyXYx)
    change of variables: x -> y, y -> x
      r1 = YYYYxyXX
           substitute      ->  XXXXyxYY
           rotate by 2     ->  YYXXXXyx
                               = r1
      r2 = YXyxxyXyXYx
           substitute      ->  XYxyyxYxYXy
           invert          ->  YxyXyXYYXyx
           rotate by 5     ->  YYXyxYxyXyX
                               = r2
    => (YYXXXXyx, YYXyxYxyXyX)

    AC move:  r2 <- rot_9(r2) . rot_2(r1)
        rot_9(r2)        =  XyxYxyXyXYY
        rot_2(r1)        =  yxYYXXXX
        concatenate      =  XyxYxyXyXYYyxYYXXXX
        cancel inverses  =  XyxYxyXyXYxYYXXXX
        rotate by 6      =  YYXXXXXyxYxyXyXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyx, YYXXXXXyxYxyXyXYx)
    change of variables: x -> X, y -> yX
      r1 = YYXXXXyx
           substitute      ->  xYxYxxxxyXX
           reduce          ->  YxYxxxxyX
           invert          ->  xYXXXXyXy
           rotate by 8     ->  YXXXXyXyx
                               = r1
      r2 = YYXXXXXyxYxyXyXYx
           substitute      ->  xYxYxxxxxyXYXyyxYX
           reduce          ->  YxYxxxxxyXYXyyxY
           rotate by 1     ->  YYxYxxxxxyXYXyyx
                               = r2
    => (YXXXXyXyx, YYxYxxxxxyXYXyyx)
    both meet at (YXXXXyXyx, YYxYxxxxxyXYXyyx)
```

**236 (19_47)  ≡  201 (19_40)** — *AC moves + change of variables*, 2 + 5 AC moves

```
  left  — 19_47
    start: (YYYYxyxyX, YYxYXXYxyx)
    change of variables: x -> y, y -> X
      r1 = YYYYxyxyX
           substitute      ->  xxxxyXyXY
           invert          ->  yxYxYXXXX
           rotate by 5     ->  YXXXXyxYx
                               = r1
      r2 = YYxYXXYxyx
           substitute      ->  xxyxYYxyXy
           rotate by 6     ->  YYxyXyxxyx
                               = r2
    => (YXXXXyxYx, YYxyXyxxyx)

    AC move:  r2 <- rot_0(r2) . rot_7(r1^-1)
        rot_0(r2)        =  YYxyXyxxyx
        rot_7(r1^-1)     =  XYxxxxyXy
        concatenate      =  YYxyXyxxyxXYxxxxyXy
        cancel inverses  =  YYxyXyxxxxxxyXy
        reduce cyclically=  YxyXyxxxxxxyX
        invert           =  xYXXXXXXYxYXy
        rotate by 3      =  YXyxYXXXXXXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXXyxYx, YXyxYXXXXXXYx)
    change of variables: x -> x, y -> yx
      r1 = YXXXXyxYx
           substitute      ->  XYXXXXyxYx
           reduce          ->  YXXXXyxY
           rotate by 1     ->  YYXXXXyx
                               = r1
      r2 = YXyxYXXXXXXYx
           substitute      ->  XYXyxYXXXXXXXYx
           reduce          ->  YXyxYXXXXXXXY
           rotate by 1     ->  YYXyxYXXXXXXX
                               = r2
    => (YYXXXXyx, YYXyxYXXXXXXX)

    AC move:  r1 <- rot_5(r1) . rot_3(r2^-1)
        rot_5(r1)        =  XXXyxYYX
        rot_3(r2^-1)     =  xyyxxxxxxxyXY
        concatenate      =  XXXyxYYXxyyxxxxxxxyXY
        cancel inverses  =  XXXyxxxxxxxxyXY
        rotate by 1      =  YXXXyxxxxxxxxyX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYXyxYXXXXXXX, YXXXyxxxxxxxxyX)
    change of variables: x -> X, y -> xxxxxxxy
      r2 = YXXXyxxxxxxxxyX
           substitute      ->  YxxxyXyx
           invert          ->  XYxYXXXy
           rotate by 5     ->  YXXXyXYx
                               = r1
      r1 = YYXyxYXXXXXXX
           substitute      ->  YXXXXXXXYxyXY
           rotate by 1     ->  YYXXXXXXXYxyX
                               = r2
    => (YXXXyXYx, YYXXXXXXXYxyX)
  right — 19_40
    start: (YYYxxYX, YXyxxxyXyXyX)
    change of variables: x -> y, y -> X
      r1 = YYYxxYX
           substitute      ->  xxxyyxY
           invert          ->  yXYYXXX
           rotate by 5     ->  YYXXXyX
                               = r1
      r2 = YXyxxxyXyXyX
           substitute      ->  xYXyyyXYXYXY
           invert          ->  yxyxyxYYYxyX
           rotate by 6     ->  YYYxyXyxyxyx
                               = r2
    => (YYXXXyX, YYYxyXyxyxyx)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYxyXyxyxyx
        rot_1(r1)        =  XYYXXXy
        concatenate      =  YYYxyXyxyxyxXYYXXXy
        cancel inverses  =  YYYxyXyxyxYXXXy
        reduce cyclically=  YYxyXyxyxYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyX, YYxyXyxyxYXXX)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYxyXyxyxYXXX
        rot_0(r1^-1)     =  xYxxxyy
        concatenate      =  YYxyXyxyxYXXXxYxxxyy
        cancel inverses  =  YYxyXyxyxYXXYxxxyy
        reduce cyclically=  xyXyxyxYXXYxxx
        invert           =  XXXyxxyXYXYxYX
        rotate by 6      =  YXYxYXXXXyxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyX, YXYxYXXXXyxxyX)
    change of variables: x -> x, y -> Xy
      r1 = YYXXXyX
           substitute      ->  YxYXXXyX
           rotate by 6     ->  YXXXyXYx
                               = r1
      r2 = YXYxYXXXXyxxyX
           substitute      ->  YYxxYXXXXyxyX
                               = r2
    => (YXXXyXYx, YYxxYXXXXyxyX)

    AC move:  r2 <- rot_5(r2) . rot_4(r1^-1)
        rot_5(r2)        =  XyxyXYYxxYXXX
        rot_4(r1^-1)     =  xxxyXyxY
        concatenate      =  XyxyXYYxxYXXXxxxyXyxY
        cancel inverses  =  XyxyXYYxyxY
        rotate by 6      =  YYxyxYXyxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyXYx, YYxyxYXyxyX)

    AC move:  r2 <- rot_0(r2) . rot_6(r1^-1)
        rot_0(r2)        =  YYxyxYXyxyX
        rot_6(r1^-1)     =  xYxxxyXy
        concatenate      =  YYxyxYXyxyXxYxxxyXy
        cancel inverses  =  YYxyxYXyxxxxyXy
        reduce cyclically=  YxyxYXyxxxxyX
        invert           =  xYXXXXYxyXYXy
        rotate by 3      =  YXyxYXXXXYxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyXYx, YXyxYXXXXYxyX)
    change of variables: x -> X, y -> xxy
      r1 = YXXXyXYx
           substitute      ->  YxxxyxYXXX
           rotate by 4     ->  YXXXYxxxyx
                               = r1
      r2 = YXyxYXXXXYxyX
           substitute      ->  YxyXYxxYXyx
           invert          ->  XYxyXXyxYXy
           rotate by 3     ->  YXyXYxyXXyx
                               = r2
    => (YXXXYxxxyx, YXyXYxyXXyx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YXyXYxyXXyx
        rot_0(r1^-1)     =  XYXXXyxxxy
        concatenate      =  YXyXYxyXXyxXYXXXyxxxy
        cancel inverses  =  YXyXYxyXXXXXyxxxy
        reduce cyclically=  yXYxyXXXXXyxx
        invert           =  XXYxxxxxYXyxY
        rotate by 5      =  YXyxYXXYxxxxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXYxxxyx, YXyxYXXYxxxxx)
    change of variables: x -> X, y -> xxy
      r1 = YXXXYxxxyx
           substitute      ->  YxYXXXyX
           rotate by 6     ->  YXXXyXYx
                               = r1
      r2 = YXyxYXXYxxxxx
           substitute      ->  YxyXYYXXXXXXX
           rotate by 9     ->  YYXXXXXXXYxyX
                               = r2
    => (YXXXyXYx, YYXXXXXXXYxyX)
    both meet at (YXXXyXYx, YYXXXXXXXYxyX)
```

---

## Class 007

**4 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 202 | 18_9 | `YYYxxyX` | `YXYXyXyxxYx` |
| 210 | 18_11 | `YYYxyXX` | `YXYXXyxyxYx` |
| 235 | 19_46 | `YYYYxxYX` | `YYYxyxYxYXX` |
| 260 | 19_52 | `YYYYxYXX` | `YXYXyxyXyxx` |

### Why they are the same problem — 3 edges

**202 (18_9)  ≡  210 (18_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into **18_9** (`YYYxxyX`, `YXYXyXyxxYx`), then normalise:

```
  r1 = YYYxxyX
       substitute      ->  yyyxxYX
       invert          ->  xyXXYYY
       rotate by 3     ->  YYYxyXX
                           = r1 of 18_11   [MATCH]
  r2 = YXYXyXyxxYx
       substitute      ->  yXyXYXYxxyx
       invert          ->  XYXXyxyxYxY
       rotate by 1     ->  YXYXXyxyxYx
                           = r2 of 18_11   [MATCH]
```

which is exactly **18_11** = (`YYYxyXX`, `YXYXXyxyxYx`). No AC move was used.

**235 (19_46)  ≡  260 (19_52)** — *pure AC path*, 1 + 0 AC moves

```
  left  — 19_46
    start: (YYYYxxYX, YYYxyxYxYXX)
    change of variables: x -> y, y -> X
      r1 = YYYYxxYX
           substitute      ->  xxxxyyxY
           invert          ->  yXYYXXXX
           rotate by 6     ->  YYXXXXyX
                               = r1
      r2 = YYYxyxYxYXX
           substitute      ->  xxxyXyxyxYY
           rotate by 2     ->  YYxxxyXyxyx
                               = r2
    => (YYXXXXyX, YYxxxyXyxyx)

    AC move:  r2 <- rot_5(r2) . rot_7(r1)
        rot_5(r2)        =  XyxyxYYxxxy
        rot_7(r1)        =  YXXXXyXY
        concatenate      =  XyxyxYYxxxyYXXXXyXY
        cancel inverses  =  XyxyxYYXyXY
        rotate by 6      =  YYXyXYXyxyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyX, YYXyXYXyxyx)
  right — 19_52
    start: (YYYYxYXX, YXYXyxyXyxx)
    change of variables: x -> y, y -> x
      r1 = YYYYxYXX
           substitute      ->  XXXXyXYY
           rotate by 2     ->  YYXXXXyX
                               = r1
      r2 = YXYXyxyXyxx
           substitute      ->  XYXYxyxYxyy
           invert          ->  YYXyXYXyxyx
                               = r2
    => (YYXXXXyX, YYXyXYXyxyx)
    both meet at (YYXXXXyX, YYXyXYXyxyx)
```

Every step is an AC move — no change of variables inside the path. So `19_46 ~AC psi(19_52)` with `psi: x -> x, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `19_52`, not to `19_52` itself.

**202 (18_9)  ≡  235 (19_46)** — *AC moves + change of variables*, 3 + 2 AC moves

```
  left  — 18_9
    start: (YYYxxyX, YXYXyXyxxYx)
    change of variables: x -> y, y -> X
      r1 = YYYxxyX
           substitute      ->  xxxyyXY
           invert          ->  yxYYXXX
           rotate by 5     ->  YYXXXyx
                               = r1
      r2 = YXYXyXyxxYx
           substitute      ->  xYxYXYXyyxy
           invert          ->  YXYYxyxyXyX
           rotate by 9     ->  YYxyxyXyXYX
                               = r2
    => (YYXXXyx, YYxyxyXyXYX)

    AC move:  r2 <- rot_1(r2) . rot_2(r1)
        rot_1(r2)        =  XYYxyxyXyXY
        rot_2(r1)        =  yxYYXXX
        concatenate      =  XYYxyxyXyXYyxYYXXX
        cancel inverses  =  XYYxyxyXYXXX
        rotate by 11     =  YYxyxyXYXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyx, YYxyxyXYXXXX)
    change of variables: x -> x, y -> Xy
      r1 = YYXXXyx
           substitute      ->  YxYXXXyx
           rotate by 6     ->  YXXXyxYx
                               = r1
      r2 = YYxyxyXYXXXX
           substitute      ->  YxYxyyXYXXX
           invert          ->  xxxyxYYXyXy
           rotate by 6     ->  YYXyXyxxxyx
                               = r2
    => (YXXXyxYx, YYXyXyxxxyx)

    AC move:  r2 <- rot_0(r2) . rot_6(r1^-1)
        rot_0(r2)        =  YYXyXyxxxyx
        rot_6(r1^-1)     =  XYxxxyXy
        concatenate      =  YYXyXyxxxyxXYxxxyXy
        cancel inverses  =  YYXyXyxxxxxxyXy
        reduce cyclically=  YXyXyxxxxxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxYx, YXyXyxxxxxxyX)
    change of variables: x -> x, y -> yx
      r1 = YXXXyxYx
           substitute      ->  XYXXXyxYx
           reduce          ->  YXXXyxY
           rotate by 1     ->  YYXXXyx
                               = r1
      r2 = YXyXyxxxxxxyX
           substitute      ->  XYXyyxxxxxxxy
           invert          ->  YXXXXXXXYYxyx
           rotate by 5     ->  YYxyxYXXXXXXX
                               = r2
    => (YYXXXyx, YYxyxYXXXXXXX)

    AC move:  r2 <- rot_11(r2) . rot_2(r1^-1)
        rot_11(r2)       =  xyxYXXXXXXXYY
        rot_2(r1^-1)     =  yyXYxxx
        concatenate      =  xyxYXXXXXXXYYyyXYxxx
        cancel inverses  =  xyxYXXXXXXXXYxxx
        invert           =  XXXyxxxxxxxxyXYX
        rotate by 2      =  YXXXXyxxxxxxxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyx, YXXXXyxxxxxxxxyX)
    change of variables: x -> X, y -> xxxxxxxy
      r2 = YXXXXyxxxxxxxxyX
           substitute      ->  YxxxxyXyx
           invert          ->  XYxYXXXXy
           rotate by 6     ->  YXXXXyXYx
                               = r1
      r1 = YYXXXyx
           substitute      ->  YXXXXXXXYxxxyX
           invert          ->  xYXXXyxxxxxxxy
           rotate by 13    ->  YXXXyxxxxxxxyx
                               = r2
    => (YXXXXyXYx, YXXXyxxxxxxxyx)
  right — 19_46
    start: (YYYYxxYX, YYYxyxYxYXX)
    change of variables: x -> y, y -> X
      r1 = YYYYxxYX
           substitute      ->  xxxxyyxY
           invert          ->  yXYYXXXX
           rotate by 6     ->  YYXXXXyX
                               = r1
      r2 = YYYxyxYxYXX
           substitute      ->  xxxyXyxyxYY
           rotate by 2     ->  YYxxxyXyxyx
                               = r2
    => (YYXXXXyX, YYxxxyXyxyx)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYxxxyXyxyx
        rot_1(r1)        =  XYYXXXXy
        concatenate      =  YYxxxyXyxyxXYYXXXXy
        cancel inverses  =  YYxxxyXyxYXXXXy
        reduce cyclically=  YxxxyXyxYXXXX
        invert           =  xxxxyXYxYXXXy
        rotate by 5      =  YXXXyxxxxyXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyX, YXXXyxxxxyXYx)

    AC move:  r2 <- rot_1(r2) . rot_1(r1^-1)
        rot_1(r2)        =  xYXXXyxxxxyXY
        rot_1(r1^-1)     =  yxYxxxxy
        concatenate      =  xYXXXyxxxxyXYyxYxxxxy
        cancel inverses  =  xYXXXyxxxxxxxxy
        rotate by 14     =  YXXXyxxxxxxxxyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyX, YXXXyxxxxxxxxyx)
    change of variables: x -> x, y -> Xy
      r1 = YYXXXXyX
           substitute      ->  YxYXXXXyX
           rotate by 7     ->  YXXXXyXYx
                               = r1
      r2 = YXXXyxxxxxxxxyx
           substitute      ->  YXXXyxxxxxxxyx
                               = r2
    => (YXXXXyXYx, YXXXyxxxxxxxyx)
    both meet at (YXXXXyXYx, YXXXyxxxxxxxyx)
```

---

## Class 008

**3 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 127 | 16_6 | `YYxyxYX` | `YXyXXyxxx` |
| 133 | 16_9 | `YYXyXYX` | `YYXXXXyxx` |
| 161 | 16_10 | `YYxxyXX` | `YYYYXYxYx` |

### Why they are the same problem — 2 edges

**127 (16_6)  ≡  133 (16_9)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 16_6
    start: (YYxyxYX, YXyXXyxxx)
    change of variables: x -> y, y -> X
      r1 = YYxyxYX
           substitute      ->  xxyXyxY
           invert          ->  yXYxYXX
           rotate by 3     ->  YXXyXYx
                               = r1
      r2 = YXyXXyxxx
           substitute      ->  xYXYYXyyy
           invert          ->  YYYxyyxyX
                               = r2
    => (YXXyXYx, YYYxyyxyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYxyyxyX
        rot_1(r1)        =  xYXXyXY
        concatenate      =  YYYxyyxyXxYXXyXY
        cancel inverses  =  YYYxyyXyXY
        rotate by 1      =  YYYYxyyXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYYxyyXyX)
    change of variables: x -> xy, y -> y
      r1 = YXXyXYx
           substitute      ->  YYXYXXYxy
           reduce          ->  YXYXXYx
                               = r1
      r2 = YYYYxyyXyX
           substitute      ->  YYYYxyyXX
                               = r2
    => (YXYXXYx, YYYYxyyXX)
  right — 16_9
    start: (YYXyXYX, YYXXXXyxx)
    change of variables: x -> y, y -> x
      r1 = YYXyXYX
           substitute      ->  XXYxYXY
           rotate by 3     ->  YXYXXYx
                               = r1
      r2 = YYXXXXyxx
           substitute      ->  XXYYYYxyy
           rotate by 7     ->  YYYYxyyXX
                               = r2
    => (YXYXXYx, YYYYxyyXX)
    both meet at (YXYXXYx, YYYYxyyXX)
```

**161 (16_10)  ≡  127 (16_6)** — *AC moves + change of variables*, 5 + 4 AC moves

```
  left  — 16_10
    start: (YYxxyXX, YYYYXYxYx)
    change of variables: x -> X, y -> y
      r1 = YYxxyXX
           substitute      ->  YYXXyxx
                               = r1
      r2 = YYYYXYxYx
           substitute      ->  YYYYxYXYX
                               = r2
    => (YYXXyxx, YYYYxYXYX)

    AC move:  r1 <- rot_0(r1) . rot_5(r2^-1)
        rot_0(r1)        =  YYXXyxx
        rot_5(r2^-1)     =  Xyyyyxyxy
        concatenate      =  YYXXyxxXyyyyxyxy
        cancel inverses  =  YYXXyxyyyyxyxy
        reduce cyclically=  YXXyxyyyyxyx
        invert           =  XYXYYYYXYxxy
        rotate by 9      =  YYYYXYxxyXYX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYxYXYX, YYYYXYxxyXYX)
    change of variables: x -> Xy, y -> x
      r1 = YYYYxYXYX
           substitute      ->  XXXXXyXYYx
           reduce          ->  XXXXyXYY
           rotate by 2     ->  YYXXXXyX
                               = r1
      r2 = YYYYXYxxyXYX
           substitute      ->  XXXXYXyXyxYYx
           reduce          ->  XXXYXyXyxYY
           rotate by 2     ->  YYXXXYXyXyx
                               = r2
    => (YYXXXXyX, YYXXXYXyXyx)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYXXXYXyXyx
        rot_1(r1)        =  XYYXXXXy
        concatenate      =  YYXXXYXyXyxXYYXXXXy
        cancel inverses  =  YYXXXYXyXYXXXXy
        reduce cyclically=  YXXXYXyXYXXXX
        rotate by 9      =  YXyXYXXXXYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyX, YXyXYXXXXYXXX)
    change of variables: x -> y, y -> YYYx
      r2 = YXyXYXXXXYXXX
           substitute      ->  XYxYXYX
           rotate by 4     ->  YXYXXYx
                               = r1
      r1 = YYXXXXyX
           substitute      ->  XyyyXYYYYxY
           rotate by 6     ->  YYYYxYXyyyX
                               = r2
    => (YXYXXYx, YYYYxYXyyyX)

    AC move:  r2 <- rot_4(r2) . rot_2(r1^-1)
        rot_4(r2)        =  yyyXYYYYxYX
        rot_2(r1^-1)     =  xyXyxxy
        concatenate      =  yyyXYYYYxYXxyXyxxy
        cancel inverses  =  yyyXYYYxxy
        invert           =  YXXyyyxYYY
        rotate by 3      =  YYYYXXyyyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYXXyyyx)

    AC move:  r2 <- rot_0(r2) . rot_3(r1)
        rot_0(r2)        =  YYYYXXyyyx
        rot_3(r1)        =  XYxYXYX
        concatenate      =  YYYYXXyyyxXYxYXYX
        cancel inverses  =  YYYYXXyyxYXYX
                            ^ the new r2
        r1 is untouched by the move
    => (YXYXXYx, YYYYXXyyxYXYX)
    change of variables: x -> Yx, y -> y
      r1 = YXYXXYx
           substitute      ->  YXXyXYx
                               = r1
      r2 = YYYYXXyyxYXYX
           substitute      ->  YYYYXyXyyxYXXy
           reduce          ->  YYYXyXyyxYXX
                               = r2
    => (YXXyXYx, YYYXyXyyxYXX)

    AC move:  r2 <- rot_2(r2) . rot_4(r1)
        rot_2(r2)        =  XXYYYXyXyyxY
        rot_4(r1)        =  yXYxYXX
        concatenate      =  XXYYYXyXyyxYyXYxYXX
        cancel inverses  =  XXYYYXyXyxYXX
        rotate by 11     =  YYYXyXyxYXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYXyXyxYXXXX)
  right — 16_6
    start: (YYxyxYX, YXyXXyxxx)
    change of variables: x -> y, y -> X
      r1 = YYxyxYX
           substitute      ->  xxyXyxY
           invert          ->  yXYxYXX
           rotate by 3     ->  YXXyXYx
                               = r1
      r2 = YXyXXyxxx
           substitute      ->  xYXYYXyyy
           invert          ->  YYYxyyxyX
                               = r2
    => (YXXyXYx, YYYxyyxyX)

    AC move:  r2 <- rot_0(r2) . rot_5(r1^-1)
        rot_0(r2)        =  YYYxyyxyX
        rot_5(r1^-1)     =  xYxxyXy
        concatenate      =  YYYxyyxyXxYxxyXy
        cancel inverses  =  YYYxyyxxxyXy
        reduce cyclically=  YYxyyxxxyX
        invert           =  xYXXXYYXyy
        rotate by 5      =  YYXyyxYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYXyyxYXXX)

    AC move:  r2 <- rot_3(r2) . rot_4(r1)
        rot_3(r2)        =  XXXYYXyyxY
        rot_4(r1)        =  yXYxYXX
        concatenate      =  XXXYYXyyxYyXYxYXX
        cancel inverses  =  XXXYYXyxYXX
        rotate by 8      =  YYXyxYXXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYXyxYXXXXX)

    AC move:  r2 <- rot_5(r2) . rot_4(r1)
        rot_5(r2)        =  XXXXXYYXyxY
        rot_4(r1)        =  yXYxYXX
        concatenate      =  XXXXXYYXyxYyXYxYXX
        cancel inverses  =  XXXXXYYYXX
        rotate by 5      =  YYYXXXXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYXXXXXXX)

    AC move:  r2 <- rot_4(r2) . rot_3(r1^-1)
        rot_4(r2)        =  XXXXYYYXXX
        rot_3(r1^-1)     =  xxyXyxY
        concatenate      =  XXXXYYYXXXxxyXyxY
        cancel inverses  =  XXXXYYYXyXyxY
        rotate by 9      =  YYYXyXyxYXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXYx, YYYXyXyxYXXXX)
    both meet at (YXXyXYx, YYYXyXyxYXXXX)
```

---

## Class 009

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 7 | 15_2 | `YXXXyxx` | `YYYXXyyX` |
| 11 | 15_6 | `YXXyxxx` | `YYYXyXyX` |

### Why they are the same problem — 1 edge

**7 (15_2)  ≡  11 (15_6)** — *AC moves + change of variables*, 3 + 5 AC moves

```
  left  — 15_2
    start: (YXXXyxx, YYYXXyyX)
    => (YXXXyxx, YYYXXyyX)   [already Aut-minimal]

    AC move:  r2 <- rot_3(r2) . rot_3(r1^-1)
        rot_3(r2)        =  yyXYYYXX
        rot_3(r1^-1)     =  xxyXXYx
        concatenate      =  yyXYYYXXxxyXXYx
        cancel inverses  =  yyXYYXXYx
        invert           =  XyxxyyxYY
        rotate by 2      =  YYXyxxyyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXyxxyyx)

    AC move:  r2 <- rot_0(r2) . rot_6(r1^-1)
        rot_0(r2)        =  YYXyxxyyx
        rot_6(r1^-1)     =  XYxxxyX
        concatenate      =  YYXyxxyyxXYxxxyX
        cancel inverses  =  YYXyxxyxxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXyxxyxxxyX)
    change of variables: x -> X, y -> xxy
      r1 = YXXXyxx
           substitute      ->  YxxxyXX
           invert          ->  xxYXXXy
           rotate by 5     ->  YXXXyxx
                               = r1
      r2 = YYXyxxyxxxyX
           substitute      ->  YXXYxyyXyx
           invert          ->  XYxYYXyxxy
           rotate by 7     ->  YYXyxxyXYx
                               = r2
    => (YXXXyxx, YYXyxxyXYx)

    AC move:  r2 <- rot_8(r2) . rot_3(r1)
        rot_8(r2)        =  XyxxyXYxYY
        rot_3(r1)        =  yxxYXXX
        concatenate      =  XyxxyXYxYYyxxYXXX
        cancel inverses  =  XyxxyXYxYxxYXXX
        invert           =  xxxyXXyXyxYXXYx
        rotate by 5      =  YXXYxxxxyXXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YXXYxxxxyXXyXyx)
    change of variables: x -> X, y -> yX
      r1 = YXXXyxx
           substitute      ->  xYxxxyXXX
           reduce          ->  YxxxyXX
           invert          ->  xxYXXXy
           rotate by 5     ->  YXXXyxx
                               = r1
      r2 = YXXYxxxxyXXyXyx
           substitute      ->  xYxxxYXXXXyxyyXX
           reduce          ->  YxxxYXXXXyxyyX
           invert          ->  xYYXYxxxxyXXXy
           rotate by 13    ->  YYXYxxxxyXXXyx
                               = r2
    => (YXXXyxx, YYXYxxxxyXXXyx)
  right — 15_6
    start: (YXXyxxx, YYYXyXyX)
    change of variables: x -> X, y -> Y
      r1 = YXXyxxx
           substitute      ->  yxxYXXX
           rotate by 4     ->  YXXXyxx
                               = r1
      r2 = YYYXyXyX
           substitute      ->  yyyxYxYx
           invert          ->  XyXyXYYY
           rotate by 3     ->  YYYXyXyX
                               = r2
    => (YXXXyxx, YYYXyXyX)

    AC move:  r2 <- rot_0(r2) . rot_2(r1)
        rot_0(r2)        =  YYYXyXyX
        rot_2(r1)        =  xxYXXXy
        concatenate      =  YYYXyXyXxxYXXXy
        cancel inverses  =  YYYXyXyxYXXXy
        reduce cyclically=  YYXyXyxYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXyXyxYXXX)

    AC move:  r2 <- rot_4(r2) . rot_6(r1^-1)
        rot_4(r2)        =  YXXXYYXyXyx
        rot_6(r1^-1)     =  XYxxxyX
        concatenate      =  YXXXYYXyXyxXYxxxyX
        cancel inverses  =  YXXXYYXyxxyX
        rotate by 8      =  YYXyxxyXYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXyxxyXYXXX)
    change of variables: x -> X, y -> xxy
      r1 = YXXXyxx
           substitute      ->  YxxxyXX
           invert          ->  xxYXXXy
           rotate by 5     ->  YXXXyxx
                               = r1
      r2 = YYXyxxyXYXXX
           substitute      ->  YXXYxyyxYx
           invert          ->  XyXYYXyxxy
           rotate by 7     ->  YYXyxxyXyX
                               = r2
    => (YXXXyxx, YYXyxxyXyX)

    AC move:  r2 <- rot_4(r2) . rot_0(r1^-1)
        rot_4(r2)        =  yXyXYYXyxx
        rot_0(r1^-1)     =  XXYxxxy
        concatenate      =  yXyXYYXyxxXXYxxxy
        cancel inverses  =  yXyXYYxxy
        invert           =  YXXyyxYxY
        rotate by 1      =  YYXXyyxYx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXXyyxYx)

    AC move:  r2 <- rot_4(r2) . rot_5(r1^-1)
        rot_4(r2)        =  yxYxYYXXy
        rot_5(r1^-1)     =  YxxxyXX
        concatenate      =  yxYxYYXXyYxxxyXX
        cancel inverses  =  yxYxYYxyXX
        rotate by 6      =  YYxyXXyxYx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYxyXXyxYx)
    change of variables: x -> x, y -> yx
      r1 = YXXXyxx
           substitute      ->  XYXXXyxxx
           reduce          ->  YXXXyxx
                               = r1
      r2 = YYxyXXyxYx
           substitute      ->  XYXYxyXyxYx
           reduce          ->  YXYxyXyxY
           rotate by 1     ->  YYXYxyXyx
                               = r2
    => (YXXXyxx, YYXYxyXyx)

    AC move:  r2 <- rot_3(r2) . rot_5(r1^-1)
        rot_3(r2)        =  XyxYYXYxy
        rot_5(r1^-1)     =  YxxxyXX
        concatenate      =  XyxYYXYxyYxxxyXX
        cancel inverses  =  XyxYYXYxxxxyXX
        rotate by 11     =  YYXYxxxxyXXXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXYxxxxyXXXyx)
    both meet at (YXXXyxx, YYXYxxxxyXXXyx)
```

---

## Class 010

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 8 | 15_3 | `YYYXyyx` | `YXXYxxYx` |
| 14 | 15_9 | `YXXXyxx` | `YYYxxyyX` |

### Why they are the same problem — 1 edge

**8 (15_3)  ≡  14 (15_9)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 15_3
    start: (YYYXyyx, YXXYxxYx)
    change of variables: x -> Y, y -> x
      r1 = YYYXyyx
           substitute      ->  XXXyxxY
           rotate by 1     ->  YXXXyxx
                               = r1
      r2 = YXXYxxYx
           substitute      ->  XyyXYYXY
           rotate by 4     ->  YYXYXyyX
                               = r2
    => (YXXXyxx, YYXYXyyX)

    AC move:  r2 <- rot_0(r2) . rot_2(r1)
        rot_0(r2)        =  YYXYXyyX
        rot_2(r1)        =  xxYXXXy
        concatenate      =  YYXYXyyXxxYXXXy
        cancel inverses  =  YYXYXyyxYXXXy
        reduce cyclically=  YXYXyyxYXXX
        invert           =  xxxyXYYxyxy
        rotate by 6      =  YYxyxyxxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYxyxyxxxyX)
    change of variables: x -> x, y -> Xy
      r1 = YXXXyxx
           substitute      ->  YXXXyxx
                               = r1
      r2 = YYxyxyxxxyX
           substitute      ->  YxYxyyxxyX
           invert          ->  xYXXYYXyXy
           rotate by 6     ->  YYXyXyxYXX
                               = r2
    => (YXXXyxx, YYXyXyxYXX)

    AC move:  r2 <- rot_3(r2) . rot_6(r1^-1)
        rot_3(r2)        =  YXXYYXyXyx
        rot_6(r1^-1)     =  XYxxxyX
        concatenate      =  YXXYYXyXyxXYxxxyX
        cancel inverses  =  YXXYYXyxxyX
        rotate by 8      =  YYXyxxyXYXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXyxxyXYXX)
    change of variables: x -> X, y -> xxy
      r1 = YXXXyxx
           substitute      ->  YxxxyXX
           invert          ->  xxYXXXy
           rotate by 5     ->  YXXXyxx
                               = r1
      r2 = YYXyxxyXYXX
           substitute      ->  YXXYxyyxY
           invert          ->  yXYYXyxxy
           rotate by 7     ->  YYXyxxyyX
                               = r2
    => (YXXXyxx, YYXyxxyyX)
  right — 15_9
    start: (YXXXyxx, YYYxxyyX)
    change of variables: x -> X, y -> y
      r1 = YXXXyxx
           substitute      ->  YxxxyXX
           invert          ->  xxYXXXy
           rotate by 5     ->  YXXXyxx
                               = r1
      r2 = YYYxxyyX
           substitute      ->  YYYXXyyx
                               = r2
    => (YXXXyxx, YYYXXyyx)

    AC move:  r2 <- rot_3(r2) . rot_3(r1^-1)
        rot_3(r2)        =  yyxYYYXX
        rot_3(r1^-1)     =  xxyXXYx
        concatenate      =  yyxYYYXXxxyXXYx
        cancel inverses  =  yyxYYXXYx
        invert           =  XyxxyyXYY
        rotate by 2      =  YYXyxxyyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxx, YYXyxxyyX)
    both meet at (YXXXyxx, YYXyxxyyX)
```

---

## Class 011

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 9 | 15_4 | `YYYXyyx` | `YXyXyxxx` |
| 12 | 15_7 | `YYYXyyx` | `YXYxxxyX` |

### Why they are the same problem — 1 edge

**9 (15_4)  ≡  12 (15_7)** — *change of variables only*

Substitute `x -> x, y -> Y` into **15_4** (`YYYXyyx`, `YXyXyxxx`), then normalise:

```
  r1 = YYYXyyx
       substitute      ->  yyyXYYx
       invert          ->  XyyxYYY
       rotate by 3     ->  YYYXyyx
                           = r1 of 15_7   [MATCH]
  r2 = YXyXyxxx
       substitute      ->  yXYXYxxx
       rotate by 6     ->  YXYxxxyX
                           = r2 of 15_7   [MATCH]
```

which is exactly **15_7** = (`YYYXyyx`, `YXYxxxyX`). No AC move was used.

---

## Class 012

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 10 | 15_5 | `YYYXyyx` | `YXyXXyxx` |
| 13 | 15_8 | `YYYXyyx` | `YXXYxxyX` |

### Why they are the same problem — 1 edge

**10 (15_5)  ≡  13 (15_8)** — *change of variables only*

Substitute `x -> x, y -> Y` into **15_5** (`YYYXyyx`, `YXyXXyxx`), then normalise:

```
  r1 = YYYXyyx
       substitute      ->  yyyXYYx
       invert          ->  XyyxYYY
       rotate by 3     ->  YYYXyyx
                           = r1 of 15_8   [MATCH]
  r2 = YXyXXyxx
       substitute      ->  yXYXXYxx
       rotate by 6     ->  YXXYxxyX
                           = r2 of 15_8   [MATCH]
```

which is exactly **15_8** = (`YYYXyyx`, `YXXYxxyX`). No AC move was used.

---

## Class 013

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 17 | 17_2 | `YYXXYxxx` | `YYYXYxYxx` |
| 36 | 17_21 | `YYXXXYxx` | `YYYXXYXYx` |

### Why they are the same problem — 1 edge

**17 (17_2)  ≡  36 (17_21)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_2** (`YYXXYxxx`, `YYYXYxYxx`), then normalise:

```
  r1 = YYXXYxxx
       substitute      ->  yyXXyxxx
       invert          ->  XXXYxxYY
       rotate by 2     ->  YYXXXYxx
                           = r1 of 17_21   [MATCH]
  r2 = YYYXYxYxx
       substitute      ->  yyyXyxyxx
       invert          ->  XXYXYxYYY
       rotate by 3     ->  YYYXXYXYx
                           = r2 of 17_21   [MATCH]
```

which is exactly **17_21** = (`YYXXXYxx`, `YYYXXYXYx`). No AC move was used.

---

## Class 014

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 18 | 17_3 | `YXXYxxYx` | `YYYYXyyyx` |
| 42 | 17_27 | `YXYXXYxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**18 (17_3)  ≡  42 (17_27)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_3** (`YXXYxxYx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXXYxxYx
       substitute      ->  yXXyxxyx
       invert          ->  XYXXYxxY
       rotate by 1     ->  YXYXXYxx
                           = r1 of 17_27   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_27   [MATCH]
```

which is exactly **17_27** = (`YXYXXYxx`, `YYYYXyyyx`). No AC move was used.

---

## Class 015

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 19 | 17_4 | `YXXYxYxx` | `YYYYXyyyx` |
| 44 | 17_29 | `YXYxxYXX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**19 (17_4)  ≡  44 (17_29)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_4** (`YXXYxYxx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXXYxYxx
       substitute      ->  yXXyxyxx
       invert          ->  XXYXYxxY
       rotate by 6     ->  YXYxxYXX
                           = r1 of 17_29   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_29   [MATCH]
```

which is exactly **17_29** = (`YXYxxYXX`, `YYYYXyyyx`). No AC move was used.

---

## Class 016

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 20 | 17_5 | `YYxxyXXX` | `YYYYXyyyx` |
| 32 | 17_17 | `YXXyXYxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**32 (17_17)  ≡  20 (17_5)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 17_17
    start: (YXXyXYxx, YYYYXyyyx)
    change of variables: x -> X, y -> y
      r1 = YXXyXYxx
           substitute      ->  YxxyxYXX
           rotate by 3     ->  YXXYxxyx
                               = r1
      r2 = YYYYXyyyx
           substitute      ->  YYYYxyyyX
                               = r2
    => (YXXYxxyx, YYYYxyyyX)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YXXYxxyx
        rot_1(r2)        =  XYYYYxyyy
        concatenate      =  YXXYxxyxXYYYYxyyy
        cancel inverses  =  YXXYxxYYYxyyy
        reduce cyclically=  XXYxxYYYxyy
        rotate by 6      =  YYYxyyXXYxx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYxyyyX, YYYxyyXXYxx)
    change of variables: x -> y, y -> x
      r1 = YYYYxyyyX
           substitute      ->  XXXXyxxxY
           rotate by 1     ->  YXXXXyxxx
                               = r1
      r2 = YYYxyyXXYxx
           substitute      ->  XXXyxxYYXyy
           rotate by 5     ->  YYXyyXXXyxx
                               = r2
    => (YXXXXyxxx, YYXyyXXXyxx)

    AC move:  r2 <- rot_9(r2) . rot_4(r1)
        rot_9(r2)        =  XyyXXXyxxYY
        rot_4(r1)        =  yxxxYXXXX
        concatenate      =  XyyXXXyxxYYyxxxYXXXX
        cancel inverses  =  XyyXXXyxxYxxxYXXXX
        invert           =  xxxxyXXXyXXYxxxYYx
        rotate by 3      =  YYxxxxxyXXXyXXYxxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXXyxxx, YYxxxxxyXXXyXXYxxx)
    change of variables: x -> x, y -> yxxx
      r1 = YXXXXyxxx
           substitute      ->  XXXYXXXXyxxxxxx
           reduce          ->  YXXXXyxxx
                               = r1
      r2 = YYxxxxxyXXXyXXYxxx
           substitute      ->  XXXYXXXYxxxxxyyXXYxxx
           reduce          ->  YXXXYxxxxxyyXXY
           rotate by 1     ->  YYXXXYxxxxxyyXX
                               = r2
    => (YXXXXyxxx, YYXXXYxxxxxyyXX)
  right — 17_5
    start: (YYxxyXXX, YYYYXyyyx)
    change of variables: x -> X, y -> Y
      r1 = YYxxyXXX
           substitute      ->  yyXXYxxx
           invert          ->  XXXyxxYY
           rotate by 2     ->  YYXXXyxx
                               = r1
      r2 = YYYYXyyyx
           substitute      ->  yyyyxYYYX
           invert          ->  xyyyXYYYY
           rotate by 4     ->  YYYYxyyyX
                               = r2
    => (YYXXXyxx, YYYYxyyyX)

    AC move:  r1 <- rot_3(r1) . rot_0(r2^-1)
        rot_3(r1)        =  yxxYYXXX
        rot_0(r2^-1)     =  xYYYXyyyy
        concatenate      =  yxxYYXXXxYYYXyyyy
        cancel inverses  =  yxxYYXXYYYXyyyy
        invert           =  YYYYxyyyxxyyXXY
        rotate by 1      =  YYYYYxyyyxxyyXX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYxyyyX, YYYYYxyyyxxyyXX)
    change of variables: x -> y, y -> x
      r1 = YYYYxyyyX
           substitute      ->  XXXXyxxxY
           rotate by 1     ->  YXXXXyxxx
                               = r1
      r2 = YYYYYxyyyxxyyXX
           substitute      ->  XXXXXyxxxyyxxYY
           invert          ->  yyXXYYXXXYxxxxx
           rotate by 11    ->  YYXXXYxxxxxyyXX
                               = r2
    => (YXXXXyxxx, YYXXXYxxxxxyyXX)
    both meet at (YXXXXyxxx, YYXXXYxxxxxyyXX)
```

---

## Class 017

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 21 | 17_6 | `YXXYxxyx` | `YYYYXyyyx` |
| 34 | 17_19 | `YXyXXYxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**21 (17_6)  ≡  34 (17_19)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_6** (`YXXYxxyx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXXYxxyx
       substitute      ->  yXXyxxYx
       invert          ->  XyXXYxxY
       rotate by 1     ->  YXyXXYxx
                           = r1 of 17_19   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_19   [MATCH]
```

which is exactly **17_19** = (`YXyXXYxx`, `YYYYXyyyx`). No AC move was used.

---

## Class 018

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 22 | 17_7 | `YXyXXyxx` | `YYYYXyyyx` |
| 41 | 17_26 | `YXXYxxyX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**22 (17_7)  ≡  41 (17_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_7** (`YXyXXyxx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXyXXyxx
       substitute      ->  yXYXXYxx
       rotate by 6     ->  YXXYxxyX
                           = r1 of 17_26   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_26   [MATCH]
```

which is exactly **17_26** = (`YXXYxxyX`, `YYYYXyyyx`). No AC move was used.

---

## Class 019

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 23 | 17_8 | `YXXyXyxx` | `YYYYXyyyx` |
| 43 | 17_28 | `YXYxxyXX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**23 (17_8)  ≡  43 (17_28)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_8** (`YXXyXyxx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXXyXyxx
       substitute      ->  yXXYXYxx
       rotate by 5     ->  YXYxxyXX
                           = r1 of 17_28   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_28   [MATCH]
```

which is exactly **17_28** = (`YXYxxyXX`, `YYYYXyyyx`). No AC move was used.

---

## Class 020

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 24 | 17_9 | `YXyxxYXX` | `YYYYXyyyx` |
| 31 | 17_16 | `YXXyxYxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**24 (17_9)  ≡  31 (17_16)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_9** (`YXyxxYXX`, `YYYYXyyyx`), then normalise:

```
  r1 = YXyxxYXX
       substitute      ->  yXYxxyXX
       invert          ->  xxYXXyxY
       rotate by 6     ->  YXXyxYxx
                           = r1 of 17_16   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_16   [MATCH]
```

which is exactly **17_16** = (`YXXyxYxx`, `YYYYXyyyx`). No AC move was used.

---

## Class 021

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 25 | 17_10 | `YXYXXyxx` | `YYYYXyyyx` |
| 33 | 17_18 | `YXXyxxYx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**25 (17_10)  ≡  33 (17_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_10** (`YXYXXyxx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXYXXyxx
       substitute      ->  yXyXXYxx
       invert          ->  XXyxxYxY
       rotate by 1     ->  YXXyxxYx
                           = r1 of 17_18   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_18   [MATCH]
```

which is exactly **17_18** = (`YXXyxxYx`, `YYYYXyyyx`). No AC move was used.

---

## Class 022

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 26 | 17_11 | `YYXXXyxx` | `YXyxxyXYx` |
| 35 | 17_20 | `YYXXyxxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**26 (17_11)  ≡  35 (17_20)** — *pure AC path*, 2 + 1 AC moves

```
  left  — 17_11
    start: (YYXXXyxx, YXyxxyXYx)
    => (YYXXXyxx, YXyxxyXYx)   [already Aut-minimal]

    AC move:  r2 <- rot_4(r2) . rot_0(r1^-1)
        rot_4(r2)        =  yXYxYXyxx
        rot_0(r1^-1)     =  XXYxxxyy
        concatenate      =  yXYxYXyxxXXYxxxyy
        cancel inverses  =  yXYxYxxyy
        invert           =  YYXXyXyxY
        rotate by 1      =  YYYXXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYXXyXyx)

    AC move:  r2 <- rot_0(r2) . rot_7(r1^-1)
        rot_0(r2)        =  YYYXXyXyx
        rot_7(r1^-1)     =  XYxxxyyX
        concatenate      =  YYYXXyXyxXYxxxyyX
        cancel inverses  =  YYYXXyxxyyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYXXyxxyyX)
  right — 17_20
    start: (YYXXyxxx, YYYYXyyyx)
    change of variables: x -> x, y -> Y
      r1 = YYXXyxxx
           substitute      ->  yyXXYxxx
           invert          ->  XXXyxxYY
           rotate by 2     ->  YYXXXyxx
                               = r1
      r2 = YYYYXyyyx
           substitute      ->  yyyyXYYYx
           invert          ->  XyyyxYYYY
           rotate by 4     ->  YYYYXyyyx
                               = r2
    => (YYXXXyxx, YYYYXyyyx)

    AC move:  r2 <- rot_4(r2) . rot_3(r1^-1)
        rot_4(r2)        =  yyyxYYYYX
        rot_3(r1^-1)     =  xyyXXYxx
        concatenate      =  yyyxYYYYXxyyXXYxx
        cancel inverses  =  yyyxYYXXYxx
        invert           =  XXyxxyyXYYY
        rotate by 3      =  YYYXXyxxyyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYXXyxxyyX)
    both meet at (YYXXXyxx, YYYXXyxxyyX)
```

Every step is an AC move — no change of variables inside the path. So `17_11 ~AC psi(17_20)` with `psi: x -> x, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `17_20`, not to `17_20` itself.

---

## Class 023

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 27 | 17_12 | `YXYXYxxx` | `YYYYXyyyx` |
| 40 | 17_25 | `YXXXYxYx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**27 (17_12)  ≡  40 (17_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_12** (`YXYXYxxx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXYXYxxx
       substitute      ->  yXyXyxxx
       invert          ->  XXXYxYxY
       rotate by 1     ->  YXXXYxYx
                           = r1 of 17_25   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_25   [MATCH]
```

which is exactly **17_25** = (`YXXXYxYx`, `YYYYXyyyx`). No AC move was used.

---

## Class 024

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 28 | 17_13 | `YXYxxxyX` | `YYYYXyyyx` |
| 39 | 17_24 | `YXyXyxxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**28 (17_13)  ≡  39 (17_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_13** (`YXYxxxyX`, `YYYYXyyyx`), then normalise:

```
  r1 = YXYxxxyX
       substitute      ->  yXyxxxYX
       rotate by 2     ->  YXyXyxxx
                           = r1 of 17_24   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_24   [MATCH]
```

which is exactly **17_24** = (`YXyXyxxx`, `YYYYXyyyx`). No AC move was used.

---

## Class 025

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 29 | 17_14 | `YXyXYxxx` | `YYYYXyyyx` |
| 38 | 17_23 | `YXyxxxyX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**29 (17_14)  ≡  38 (17_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_14** (`YXyXYxxx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXyXYxxx
       substitute      ->  yXYXyxxx
       rotate by 6     ->  YXyxxxyX
                           = r1 of 17_23   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_23   [MATCH]
```

which is exactly **17_23** = (`YXyxxxyX`, `YYYYXyyyx`). No AC move was used.

---

## Class 026

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 30 | 17_15 | `YXXXyxYx` | `YYYYXyyyx` |
| 37 | 17_22 | `YXYXyxxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**30 (17_15)  ≡  37 (17_22)** — *change of variables only*

Substitute `x -> x, y -> Y` into **17_15** (`YXXXyxYx`, `YYYYXyyyx`), then normalise:

```
  r1 = YXXXyxYx
       substitute      ->  yXXXYxyx
       invert          ->  XYXyxxxY
       rotate by 1     ->  YXYXyxxx
                           = r1 of 17_22   [MATCH]
  r2 = YYYYXyyyx
       substitute      ->  yyyyXYYYx
       invert          ->  XyyyxYYYY
       rotate by 4     ->  YYYYXyyyx
                           = r2 of 17_22   [MATCH]
```

which is exactly **17_22** = (`YXYXyxxx`, `YYYYXyyyx`). No AC move was used.

---

## Class 027

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 45 | 15_10 | `YXyxxyX` | `YYXyyxYx` |
| 46 | 15_11 | `YYYXyxx` | `YYYxxyyX` |

### Why they are the same problem — 1 edge

**46 (15_11)  ≡  45 (15_10)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 15_11
    start: (YYYXyxx, YYYxxyyX)
    change of variables: x -> Y, y -> x
      r1 = YYYXyxx
           substitute      ->  XXXyxYY
           rotate by 2     ->  YYXXXyx
                               = r1
      r2 = YYYxxyyX
           substitute      ->  XXXYYxxy
           rotate by 5     ->  YYxxyXXX
                               = r2
    => (YYXXXyx, YYxxyXXX)

    AC move:  r2 <- rot_3(r2) . rot_6(r1)
        rot_3(r2)        =  XXXYYxxy
        rot_6(r1)        =  YXXXyxY
        concatenate      =  XXXYYxxyYXXXyxY
        cancel inverses  =  XXXYYXyxY
        rotate by 6      =  YYXyxYXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyx, YYXyxYXXX)

    AC move:  r2 <- rot_0(r2) . rot_5(r1^-1)
        rot_0(r2)        =  YYXyxYXXX
        rot_5(r1^-1)     =  xxxyyXY
        concatenate      =  YYXyxYXXXxxxyyXY
        cancel inverses  =  YYXyxyXY
        rotate by 1      =  YYYXyxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyx, YYYXyxyX)
  right — 15_10
    start: (YXyxxyX, YYXyyxYx)
    change of variables: x -> x, y -> Y
      r1 = YXyxxyX
           substitute      ->  yXYxxYX
           rotate by 2     ->  YXyXYxx
                               = r1
      r2 = YYXyyxYx
           substitute      ->  yyXYYxyx
           invert          ->  XYXyyxYY
           rotate by 2     ->  YYXYXyyx
                               = r2
    => (YXyXYxx, YYXYXyyx)

    AC move:  r2 <- rot_0(r2) . rot_4(r1)
        rot_0(r2)        =  YYXYXyyx
        rot_4(r1)        =  XYxxYXy
        concatenate      =  YYXYXyyxXYxxYXy
        cancel inverses  =  YYXYXyxxYXy
        reduce cyclically=  YXYXyxxYX
        rotate by 2      =  YXYXYXyxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXyXYxx, YXYXYXyxx)
    change of variables: x -> Y, y -> yx
      r2 = YXYXYXyxx
           substitute      ->  XXXyxYY
           rotate by 2     ->  YYXXXyx
                               = r1
      r1 = YXyXYxx
           substitute      ->  XyxyXYYY
           rotate by 3     ->  YYYXyxyX
                               = r2
    => (YYXXXyx, YYYXyxyX)
    both meet at (YYXXXyx, YYYXyxyX)
```

---

## Class 028

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 47 | 18_1 | `YXXYxxx` | `YYYYYXyyyyx` |
| 49 | 18_3 | `YXXXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**47 (18_1)  ≡  49 (18_3)** — *change of variables only*

Substitute `x -> x, y -> Y` into **18_1** (`YXXYxxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXXYxxx
       substitute      ->  yXXyxxx
       invert          ->  XXXYxxY
       rotate by 1     ->  YXXXYxx
                           = r1 of 18_3   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 18_3   [MATCH]
```

which is exactly **18_3** = (`YXXXYxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 029

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 50 | 19_1 | `YYXXYxxx` | `YYYYYXyyyyx` |
| 71 | 19_22 | `YYXXXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**50 (19_1)  ≡  71 (19_22)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_1** (`YYXXYxxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YYXXYxxx
       substitute      ->  yyXXyxxx
       invert          ->  XXXYxxYY
       rotate by 2     ->  YYXXXYxx
                           = r1 of 19_22   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_22   [MATCH]
```

which is exactly **19_22** = (`YYXXXYxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 030

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 51 | 19_2 | `YXyxxxYXX` | `YYYYXXXyxx` |
| 79 | 19_30 | `YXYXXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**79 (19_30)  ≡  51 (19_2)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 19_30
    start: (YXYXXYxx, YYYYYXyyyyx)
    change of variables: x -> X, y -> y
      r1 = YXYXXYxx
           substitute      ->  YxYxxYXX
           rotate by 3     ->  YXXYxYxx
                               = r1
      r2 = YYYYYXyyyyx
           substitute      ->  YYYYYxyyyyX
                               = r2
    => (YXXYxYxx, YYYYYxyyyyX)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YXXYxYxx
        rot_1(r2)        =  XYYYYYxyyyy
        concatenate      =  YXXYxYxxXYYYYYxyyyy
        cancel inverses  =  YXXYxYxYYYYYxyyyy
        reduce cyclically=  XXYxYxYYYYYxyyy
        rotate by 9      =  YYYYYxyyyXXYxYx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYYxyyyyX, YYYYYxyyyXXYxYx)
    change of variables: x -> yX, y -> X
      r1 = YYYYYxyyyyX
           substitute      ->  xxxxxyXXXXY
           invert          ->  yxxxxYXXXXX
           rotate by 6     ->  YXXXXXyxxxx
                               = r1
      r2 = YYYYYxyyyXXYxYx
           substitute      ->  xxxxxyXXXYxYxyyX
           reduce          ->  xxxxyXXXYxYxyy
           invert          ->  YYXyXyxxxYXXXX
                               = r2
    => (YXXXXXyxxxx, YYXyXyxxxYXXXX)

    AC move:  r2 <- rot_5(r2) . rot_10(r1^-1)
        rot_5(r2)        =  YXXXXYYXyXyxxx
        rot_10(r1^-1)    =  XXXYxxxxxyX
        concatenate      =  YXXXXYYXyXyxxxXXXYxxxxxyX
        cancel inverses  =  YXXXXYYXyxxxxyX
        rotate by 10     =  YYXyxxxxyXYXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXXXyxxxx, YYXyxxxxyXYXXXX)
    change of variables: x -> X, y -> xxxxy
      r2 = YYXyxxxxyXYXXXX
           substitute      ->  YXXXXYxyyxY
           invert          ->  yXYYXyxxxxy
           rotate by 9     ->  YYXyxxxxyyX
                               = r1
      r1 = YXXXXXyxxxx
           substitute      ->  YxxxxxyXXXX
           invert          ->  xxxxYXXXXXy
           rotate by 7     ->  YXXXXXyxxxx
                               = r2
    => (YYXyxxxxyyX, YXXXXXyxxxx)
  right — 19_2
    start: (YXyxxxYXX, YYYYXXXyxx)
    change of variables: x -> x, y -> Y
      r1 = YXyxxxYXX
           substitute      ->  yXYxxxyXX
           invert          ->  xxYXXXyxY
           rotate by 7     ->  YXXXyxYxx
                               = r1
      r2 = YYYYXXXyxx
           substitute      ->  yyyyXXXYxx
           invert          ->  XXyxxxYYYY
           rotate by 4     ->  YYYYXXyxxx
                               = r2
    => (YXXXyxYxx, YYYYXXyxxx)

    AC move:  r1 <- rot_3(r1) . rot_8(r2^-1)
        rot_3(r1)        =  YxxYXXXyx
        rot_8(r2^-1)     =  XYxxyyyyXX
        concatenate      =  YxxYXXXyxXYxxyyyyXX
        cancel inverses  =  YxxYXyyyyXX
        invert           =  xxYYYYxyXXy
        rotate by 9      =  YYYYxyXXyxx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYXXyxxx, YYYYxyXXyxx)
    change of variables: x -> Y, y -> x
      r1 = YYYYXXyxxx
           substitute      ->  XXXXyyxYYY
           rotate by 3     ->  YYYXXXXyyx
                               = r1
      r2 = YYYYxyXXyxx
           substitute      ->  XXXXYxyyxYY
           invert          ->  yyXYYXyxxxx
           rotate by 8     ->  YYXyxxxxyyX
                               = r2
    => (YYYXXXXyyx, YYXyxxxxyyX)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YYYXXXXyyx
        rot_1(r2)        =  XYYXyxxxxyy
        concatenate      =  YYYXXXXyyxXYYXyxxxxyy
        cancel inverses  =  YYYXXXXXyxxxxyy
        reduce cyclically=  YXXXXXyxxxx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYXyxxxxyyX, YXXXXXyxxxx)
    both meet at (YYXyxxxxyyX, YXXXXXyxxxx)
```

---

## Class 031

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 52 | 19_3 | `YXXYxYxx` | `YYYYYXyyyyx` |
| 81 | 19_32 | `YXYxxYXX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**52 (19_3)  ≡  81 (19_32)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_3** (`YXXYxYxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXXYxYxx
       substitute      ->  yXXyxyxx
       invert          ->  XXYXYxxY
       rotate by 6     ->  YXYxxYXX
                           = r1 of 19_32   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_32   [MATCH]
```

which is exactly **19_32** = (`YXYxxYXX`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 032

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 53 | 19_4 | `YXyxxyXX` | `YYYYYXyyyyx` |
| 69 | 19_20 | `YXXyXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**53 (19_4)  ≡  69 (19_20)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_4** (`YXyxxyXX`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXyxxyXX
       substitute      ->  yXYxxYXX
       rotate by 3     ->  YXXyXYxx
                           = r1 of 19_20   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_20   [MATCH]
```

which is exactly **19_20** = (`YXXyXYxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 033

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 54 | 19_5 | `YXXYxxyx` | `YYYYYXyyyyx` |
| 67 | 19_18 | `YXyXXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**54 (19_5)  ≡  67 (19_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_5** (`YXXYxxyx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXXYxxyx
       substitute      ->  yXXyxxYx
       invert          ->  XyXXYxxY
       rotate by 1     ->  YXyXXYxx
                           = r1 of 19_18   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_18   [MATCH]
```

which is exactly **19_18** = (`YXyXXYxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 034

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 55 | 19_6 | `YXyXXyxx` | `YYYYYXyyyyx` |
| 78 | 19_29 | `YXXYxxyX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**55 (19_6)  ≡  78 (19_29)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_6** (`YXyXXyxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXyXXyxx
       substitute      ->  yXYXXYxx
       rotate by 6     ->  YXXYxxyX
                           = r1 of 19_29   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_29   [MATCH]
```

which is exactly **19_29** = (`YXXYxxyX`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 035

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 56 | 19_7 | `YXXyXyxx` | `YYYYYXyyyyx` |
| 80 | 19_31 | `YXYxxyXX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**56 (19_7)  ≡  80 (19_31)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_7** (`YXXyXyxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXXyXyxx
       substitute      ->  yXXYXYxx
       rotate by 5     ->  YXYxxyXX
                           = r1 of 19_31   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_31   [MATCH]
```

which is exactly **19_31** = (`YXYxxyXX`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 036

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 57 | 19_8 | `YXyxxYXX` | `YYYYYXyyyyx` |
| 68 | 19_19 | `YXXyxYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**57 (19_8)  ≡  68 (19_19)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_8** (`YXyxxYXX`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXyxxYXX
       substitute      ->  yXYxxyXX
       invert          ->  xxYXXyxY
       rotate by 6     ->  YXXyxYxx
                           = r1 of 19_19   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_19   [MATCH]
```

which is exactly **19_19** = (`YXXyxYxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 037

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 58 | 19_9 | `YXYXXyxx` | `YYYYYXyyyyx` |
| 66 | 19_17 | `YXXyXYxxx` | `YYYYXXXYxx` |

### Why they are the same problem — 1 edge

**58 (19_9)  ≡  66 (19_17)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 19_9
    start: (YXYXXyxx, YYYYYXyyyyx)
    change of variables: x -> X, y -> y
      r1 = YXYXXyxx
           substitute      ->  YxYxxyXX
           invert          ->  xxYXXyXy
           rotate by 6     ->  YXXyXyxx
                               = r1
      r2 = YYYYYXyyyyx
           substitute      ->  YYYYYxyyyyX
                               = r2
    => (YXXyXyxx, YYYYYxyyyyX)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YXXyXyxx
        rot_1(r2)        =  XYYYYYxyyyy
        concatenate      =  YXXyXyxxXYYYYYxyyyy
        cancel inverses  =  YXXyXyxYYYYYxyyyy
        reduce cyclically=  XXyXyxYYYYYxyyy
        rotate by 9      =  YYYYYxyyyXXyXyx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYYxyyyyX, YYYYYxyyyXXyXyx)
    change of variables: x -> yX, y -> X
      r1 = YYYYYxyyyyX
           substitute      ->  xxxxxyXXXXY
           invert          ->  yxxxxYXXXXX
           rotate by 6     ->  YXXXXXyxxxx
                               = r1
      r2 = YYYYYxyyyXXyXyx
           substitute      ->  xxxxxyXXXYxYYXyX
           reduce          ->  xxxxyXXXYxYYXy
           rotate by 4     ->  YYXyxxxxyXXXYx
                               = r2
    => (YXXXXXyxxxx, YYXyxxxxyXXXYx)

    AC move:  r2 <- rot_0(r2) . rot_6(r1)
        rot_0(r2)        =  YYXyxxxxyXXXYx
        rot_6(r1)        =  XyxxxxYXXXX
        concatenate      =  YYXyxxxxyXXXYxXyxxxxYXXXX
        cancel inverses  =  YYXyxxxxyxYXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXXXyxxxx, YYXyxxxxyxYXXXX)
    change of variables: x -> X, y -> xxxxy
      r2 = YYXyxxxxyxYXXXX
           substitute      ->  YXXXXYxyyXY
           invert          ->  yxYYXyxxxxy
           rotate by 9     ->  YYXyxxxxyyx
                               = r1
      r1 = YXXXXXyxxxx
           substitute      ->  YxxxxxyXXXX
           invert          ->  xxxxYXXXXXy
           rotate by 7     ->  YXXXXXyxxxx
                               = r2
    => (YYXyxxxxyyx, YXXXXXyxxxx)
  right — 19_17
    start: (YXXyXYxxx, YYYYXXXYxx)
    => (YXXyXYxxx, YYYYXXXYxx)   [already Aut-minimal]

    AC move:  r1 <- rot_1(r1) . rot_0(r2^-1)
        rot_1(r1)        =  xYXXyXYxx
        rot_0(r2^-1)     =  XXyxxxyyyy
        concatenate      =  xYXXyXYxxXXyxxxyyyy
        cancel inverses  =  xYXXyxxyyyy
        invert           =  YYYYXXYxxyX
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYYYXXXYxx, YYYYXXYxxyX)
    change of variables: x -> Y, y -> X
      r1 = YYYYXXXYxx
           substitute      ->  xxxxyyyxYY
           invert          ->  yyXYYYXXXX
           rotate by 7     ->  YYYXXXXyyX
                               = r1
      r2 = YYYYXXYxxyX
           substitute      ->  xxxxyyxYYXy
           rotate by 4     ->  YYXyxxxxyyx
                               = r2
    => (YYYXXXXyyX, YYXyxxxxyyx)

    AC move:  r1 <- rot_0(r1) . rot_1(r2)
        rot_0(r1)        =  YYYXXXXyyX
        rot_1(r2)        =  xYYXyxxxxyy
        concatenate      =  YYYXXXXyyXxYYXyxxxxyy
        cancel inverses  =  YYYXXXXXyxxxxyy
        reduce cyclically=  YXXXXXyxxxx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYXyxxxxyyx, YXXXXXyxxxx)
    both meet at (YYXyxxxxyyx, YXXXXXyxxxx)
```

---

## Class 038

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 59 | 19_10 | `YYXXXyxx` | `YYYYYXyyyyx` |
| 70 | 19_21 | `YYXXyxxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**59 (19_10)  ≡  70 (19_21)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_10** (`YYXXXyxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YYXXXyxx
       substitute      ->  yyXXXYxx
       invert          ->  XXyxxxYY
       rotate by 2     ->  YYXXyxxx
                           = r1 of 19_21   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_21   [MATCH]
```

which is exactly **19_21** = (`YYXXyxxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 039

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 60 | 19_11 | `YXYXYxxx` | `YYYYYXyyyyx` |
| 75 | 19_26 | `YXXXYxYx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**60 (19_11)  ≡  75 (19_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_11** (`YXYXYxxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXYXYxxx
       substitute      ->  yXyXyxxx
       invert          ->  XXXYxYxY
       rotate by 1     ->  YXXXYxYx
                           = r1 of 19_26   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_26   [MATCH]
```

which is exactly **19_26** = (`YXXXYxYx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 040

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 61 | 19_12 | `YXYxxxyX` | `YYYYYXyyyyx` |
| 74 | 19_25 | `YXyXyxxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**61 (19_12)  ≡  74 (19_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_12** (`YXYxxxyX`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXYxxxyX
       substitute      ->  yXyxxxYX
       rotate by 2     ->  YXyXyxxx
                           = r1 of 19_25   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_25   [MATCH]
```

which is exactly **19_25** = (`YXyXyxxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 041

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 62 | 19_13 | `YXyXYxxx` | `YYYYYXyyyyx` |
| 73 | 19_24 | `YXyxxxyX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**62 (19_13)  ≡  73 (19_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_13** (`YXyXYxxx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXyXYxxx
       substitute      ->  yXYXyxxx
       rotate by 6     ->  YXyxxxyX
                           = r1 of 19_24   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_24   [MATCH]
```

which is exactly **19_24** = (`YXyxxxyX`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 042

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 63 | 19_14 | `YXXXyxYx` | `YYYYYXyyyyx` |
| 72 | 19_23 | `YXYXyxxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**63 (19_14)  ≡  72 (19_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_14** (`YXXXyxYx`, `YYYYYXyyyyx`), then normalise:

```
  r1 = YXXXyxYx
       substitute      ->  yXXXYxyx
       invert          ->  XYXyxxxY
       rotate by 1     ->  YXYXyxxx
                           = r1 of 19_23   [MATCH]
  r2 = YYYYYXyyyyx
       substitute      ->  yyyyyXYYYYx
       invert          ->  XyyyyxYYYYY
       rotate by 5     ->  YYYYYXyyyyx
                           = r2 of 19_23   [MATCH]
```

which is exactly **19_23** = (`YXYXyxxx`, `YYYYYXyyyyx`). No AC move was used.

---

## Class 043

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 64 | 19_15 | `YYxxxYXX` | `YXYxxyXyXYx` |
| 77 | 19_28 | `YYxxYXXX` | `YYYYYxYXYXX` |

### Why they are the same problem — 1 edge

**77 (19_28)  ≡  64 (19_15)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 19_28
    start: (YYxxYXXX, YYYYYxYXYXX)
    change of variables: x -> X, y -> Y
      r1 = YYxxYXXX
           substitute      ->  yyXXyxxx
           invert          ->  XXXYxxYY
           rotate by 2     ->  YYXXXYxx
                               = r1
      r2 = YYYYYxYXYXX
           substitute      ->  yyyyyXyxyxx
           invert          ->  XXYXYxYYYYY
           rotate by 5     ->  YYYYYXXYXYx
                               = r2
    => (YYXXXYxx, YYYYYXXYXYx)

    AC move:  r2 <- rot_4(r2) . rot_4(r1^-1)
        rot_4(r2)        =  YXYxYYYYYXX
        rot_4(r1^-1)     =  xxyyXXyx
        concatenate      =  YXYxYYYYYXXxxyyXXyx
        cancel inverses  =  YXYxYYYXXyx
        rotate by 7      =  YYYXXyxYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYXXyxYXYx)
  right — 19_15
    start: (YYxxxYXX, YXYxxyXyXYx)
    change of variables: x -> x, y -> Yx
      r1 = YYxxxYXX
           substitute      ->  XyXyxxyXX
           invert          ->  xxYXXYxYx
           rotate by 7     ->  YXXYxYxxx
                               = r1
      r2 = YXYxxyXyXYx
           substitute      ->  XyXXyxxYYXyx
           reduce          ->  yXXyxxYYXy
           rotate by 4     ->  YYXyyXXyxx
                               = r2
    => (YXXYxYxxx, YYXyyXXyxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYXyyXXyxx
        rot_0(r1^-1)     =  XXXyXyxxy
        concatenate      =  YYXyyXXyxxXXXyXyxxy
        cancel inverses  =  YYXyyXXyXyXyxxy
        reduce cyclically=  YXyyXXyXyXyxx
        invert           =  XXYxYxYxxYYxy
        rotate by 4      =  YYxyXXYxYxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYxYxxx, YYxyXXYxYxYxx)
    change of variables: x -> X, y -> YX
      r1 = YXXYxYxxx
           substitute      ->  xyxxxyyXXX
           reduce          ->  yxxxyyXX
           invert          ->  xxYYXXXY
           rotate by 6     ->  YYXXXYxx
                               = r1
      r2 = YYxyXXYxYxYxx
           substitute      ->  xyxyXYxxyyyXX
           reduce          ->  yxyXYxxyyyX
           invert          ->  xYYYXXyxYXY
           rotate by 10    ->  YYYXXyxYXYx
                               = r2
    => (YYXXXYxx, YYYXXyxYXYx)
    both meet at (YYXXXYxx, YYYXXyxYXYx)
```

---

## Class 044

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 65 | 19_16 | `YYxxxyXX` | `YYYYYxxyxyX` |
| 76 | 19_27 | `YYxxyXXX` | `YXyxxyXyXYx` |

### Why they are the same problem — 1 edge

**76 (19_27)  ≡  65 (19_16)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 19_27
    start: (YYxxyXXX, YXyxxyXyXYx)
    change of variables: x -> x, y -> Yx
      r1 = YYxxyXXX
           substitute      ->  XyXyxxYXX
           rotate by 3     ->  YXXXyXyxx
                               = r1
      r2 = YXyxxyXyXYx
           substitute      ->  XyXYxxxYYXyx
           reduce          ->  yXYxxxYYXy
           rotate by 4     ->  YYXyyXYxxx
                               = r2
    => (YXXXyXyxx, YYXyyXYxxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYXyyXYxxx
        rot_0(r1^-1)     =  XXYxYxxxy
        concatenate      =  YYXyyXYxxxXXYxYxxxy
        cancel inverses  =  YYXyyXYxYxYxxxy
        reduce cyclically=  YXyyXYxYxYxxx
        invert           =  XXXyXyXyxYYxy
        rotate by 4      =  YYxyXXXyXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyXyxx, YYxyXXXyXyXyx)
    change of variables: x -> X, y -> yX
      r1 = YXXXyXyxx
           substitute      ->  xYxxxyyXXX
           reduce          ->  YxxxyyXX
           invert          ->  xxYYXXXy
           rotate by 6     ->  YYXXXyxx
                               = r1
      r2 = YYxyXXXyXyXyx
           substitute      ->  xYxYXyxxyyyXX
           reduce          ->  YxYXyxxyyyX
           invert          ->  xYYYXXYxyXy
           rotate by 10    ->  YYYXXYxyXyx
                               = r2
    => (YYXXXyxx, YYYXXYxyXyx)
  right — 19_16
    start: (YYxxxyXX, YYYYYxxyxyX)
    change of variables: x -> X, y -> y
      r1 = YYxxxyXX
           substitute      ->  YYXXXyxx
                               = r1
      r2 = YYYYYxxyxyX
           substitute      ->  YYYYYXXyXyx
                               = r2
    => (YYXXXyxx, YYYYYXXyXyx)

    AC move:  r2 <- rot_4(r2) . rot_4(r1^-1)
        rot_4(r2)        =  yXyxYYYYYXX
        rot_4(r1^-1)     =  xxyyXXYx
        concatenate      =  yXyxYYYYYXXxxyyXXYx
        cancel inverses  =  yXyxYYYXXYx
        rotate by 7      =  YYYXXYxyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYXXYxyXyx)
    both meet at (YYXXXyxx, YYYXXYxyXyx)
```

---

## Class 045

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 82 | 17_30 | `YYYxyXX` | `YYxxyXyXYX` |
| 85 | 17_33 | `YYYxyxyX` | `YXyxxyXyX` |

### Why they are the same problem — 1 edge

**85 (17_33)  ≡  82 (17_30)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 17_33
    start: (YYYxyxyX, YXyxxyXyX)
    change of variables: x -> y, y -> X
      r1 = YYYxyxyX
           substitute      ->  xxxyXyXY
           invert          ->  yxYxYXXX
           rotate by 4     ->  YXXXyxYx
                               = r1
      r2 = YXyxxyXyX
           substitute      ->  xYXyyXYXY
           invert          ->  yxyxYYxyX
           rotate by 5     ->  YYxyXyxyx
                               = r2
    => (YXXXyxYx, YYxyXyxyx)

    AC move:  r2 <- rot_1(r2) . rot_0(r1)
        rot_1(r2)        =  xYYxyXyxy
        rot_0(r1)        =  YXXXyxYx
        concatenate      =  xYYxyXyxyYXXXyxYx
        cancel inverses  =  xYYxyXyXXyxYx
        rotate by 12     =  YYxyXyXXyxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyxYx, YYxyXyXXyxYxx)
    change of variables: x -> x, y -> yx
      r1 = YXXXyxYx
           substitute      ->  XYXXXyxYx
           reduce          ->  YXXXyxY
           rotate by 1     ->  YYXXXyx
                               = r1
      r2 = YYxyXyXXyxYxx
           substitute      ->  XYXYxyyXyxYxx
           reduce          ->  YXYxyyXyxYx
           invert          ->  XyXYxYYXyxy
           rotate by 6     ->  YYXyxyXyXYx
                               = r2
    => (YYXXXyx, YYXyxyXyXYx)
  right — 17_30
    start: (YYYxyXX, YYxxyXyXYX)
    change of variables: x -> y, y -> x
      r1 = YYYxyXX
           substitute      ->  XXXyxYY
           rotate by 2     ->  YYXXXyx
                               = r1
      r2 = YYxxyXyXYX
           substitute      ->  XXyyxYxYXY
           invert          ->  yxyXyXYYxx
           rotate by 4     ->  YYxxyxyXyX
                               = r2
    => (YYXXXyx, YYxxyxyXyX)

    AC move:  r2 <- rot_6(r2) . rot_4(r1)
        rot_6(r2)        =  yxyXyXYYxx
        rot_4(r1)        =  XXyxYYX
        concatenate      =  yxyXyXYYxxXXyxYYX
        cancel inverses  =  yxyXyXYxYYX
        rotate by 3      =  YYXyxyXyXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyx, YYXyxyXyXYx)
    both meet at (YYXXXyx, YYXyxyXyXYx)
```

---

## Class 046

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 83 | 17_31 | `YYxxyX` | `YYYYYXyxxyx` |
| 84 | 17_32 | `YYxyXX` | `YYYXXyxyxYX` |

### Why they are the same problem — 1 edge

**83 (17_31)  ≡  84 (17_32)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 17_31
    start: (YYxxyX, YYYYYXyxxyx)
    change of variables: x -> X, y -> y
      r1 = YYxxyX
           substitute      ->  YYXXyx
                               = r1
      r2 = YYYYYXyxxyx
           substitute      ->  YYYYYxyXXyX
                               = r2
    => (YYXXyx, YYYYYxyXXyX)

    AC move:  r2 <- rot_1(r2) . rot_5(r1^-1)
        rot_1(r2)        =  XYYYYYxyXXy
        rot_5(r1^-1)     =  YxxyyX
        concatenate      =  XYYYYYxyXXyYxxyyX
        cancel inverses  =  XYYYYYxyyyX
        rotate by 10     =  YYYYYxyyyXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYYYYxyyyXX)

    AC move:  r2 <- rot_3(r2) . rot_0(r1)
        rot_3(r2)        =  yXXYYYYYxyy
        rot_0(r1)        =  YYXXyx
        concatenate      =  yXXYYYYYxyyYYXXyx
        cancel inverses  =  yXXYYYYYXyx
        rotate by 8      =  YYYYYXyxyXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYYYYXyxyXX)
  right — 17_32
    start: (YYxyXX, YYYXXyxyxYX)
    change of variables: x -> Xy, y -> x
      r1 = YYxyXX
           substitute      ->  XXXyxYxYx
           reduce          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYYXXyxyxYX
           substitute      ->  XXXYxYxyyXYx
           reduce          ->  XXYxYxyyXY
           invert          ->  yxYYXyXyxx
           rotate by 8     ->  YYXyXyxxyx
                               = r2
    => (YXXyxYx, YYXyXyxxyx)

    AC move:  r2 <- rot_0(r2) . rot_5(r1^-1)
        rot_0(r2)        =  YYXyXyxxyx
        rot_5(r1^-1)     =  XYxxyXy
        concatenate      =  YYXyXyxxyxXYxxyXy
        cancel inverses  =  YYXyXyxxxxyXy
        reduce cyclically=  YXyXyxxxxyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyxYx, YXyXyxxxxyX)
    change of variables: x -> Y, y -> XY
      r1 = YXXyxYx
           substitute      ->  yxyyXYxY
           reduce          ->  xyyXYx
           invert          ->  XyxYYX
           rotate by 3     ->  YYXXyx
                               = r1
      r2 = YXyXyxxxxyX
           substitute      ->  yxyXXYYYYYX
           rotate by 6     ->  YYYYYXyxyXX
                               = r2
    => (YYXXyx, YYYYYXyxyXX)
    both meet at (YYXXyx, YYYYYXyxyXX)
```

---

## Class 047

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 86 | 20_1 | `YYYxyyx` | `YXXXXXyxxxxxx` |
| 89 | 20_3 | `YXXXYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**86 (20_1)  ≡  89 (20_3)** — *change of variables only*

Substitute `x -> Y, y -> x` into **20_1** (`YYYxyyx`, `YXXXXXyxxxxxx`), then normalise:

```
  r1 = YYYxyyx
       substitute      ->  XXXYxxY
       rotate by 1     ->  YXXXYxx
                           = r1 of 20_3   [MATCH]
  r2 = YXXXXXyxxxxxx
       substitute      ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 20_3   [MATCH]
```

which is exactly **20_3** = (`YXXXYxx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 048

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 88 | 16_4 | `YYXXyXX` | `YYYxyyXyX` |
| 90 | 16_5 | `YYxxyxx` | `YYYxyyxyX` |

### Why they are the same problem — 1 edge

**90 (16_5)  ≡  88 (16_4)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 16_5
    start: (YYxxyxx, YYYxyyxyX)
    change of variables: x -> y, y -> X
      r1 = YYxxyxx
           substitute      ->  xxyyXyy
           invert          ->  YYxYYXX
           rotate by 4     ->  YYXXYYx
                               = r1
      r2 = YYYxyyxyX
           substitute      ->  xxxyXXyXY
           invert          ->  yxYxxYXXX
           rotate by 4     ->  YXXXyxYxx
                               = r2
    => (YYXXYYx, YXXXyxYxx)

    AC move:  r2 <- rot_4(r2) . rot_2(r1)
        rot_4(r2)        =  xYxxYXXXy
        rot_2(r1)        =  YxYYXXY
        concatenate      =  xYxxYXXXyYxYYXXY
        cancel inverses  =  xYxxYXXYYXXY
        rotate by 5      =  YYXXYxYxxYXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXYYx, YYXXYxYxxYXX)
  right — 16_4
    start: (YYXXyXX, YYYxyyXyX)
    change of variables: x -> y, y -> x
      r1 = YYXXyXX
           substitute      ->  XXYYxYY
           rotate by 2     ->  YYXXYYx
                               = r1
      r2 = YYYxyyXyX
           substitute      ->  XXXyxxYxY
           rotate by 1     ->  YXXXyxxYx
                               = r2
    => (YYXXYYx, YXXXyxxYx)

    AC move:  r2 <- rot_4(r2) . rot_2(r1)
        rot_4(r2)        =  xxYxYXXXy
        rot_2(r1)        =  YxYYXXY
        concatenate      =  xxYxYXXXyYxYYXXY
        cancel inverses  =  xxYxYXXYYXXY
        rotate by 5      =  YYXXYxxYxYXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXYYx, YYXXYxxYxYXX)
    change of variables: x -> X, y -> Y
      r1 = YYXXYYx
           substitute      ->  yyxxyyX
           invert          ->  xYYXXYY
           rotate by 6     ->  YYXXYYx
                               = r1
      r2 = YYXXYxxYxYXX
           substitute      ->  yyxxyXXyXyxx
           invert          ->  XXYxYxxYXXYY
           rotate by 2     ->  YYXXYxYxxYXX
                               = r2
    => (YYXXYYx, YYXXYxYxxYXX)
    both meet at (YYXXYYx, YYXXYxYxxYXX)
```

---

## Class 049

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 91 | 21_2 | `YYXXYxxx` | `YYYYYYXyyyyyx` |
| 112 | 21_20 | `YYXXXYxx` | `YXYXYxYXXyxyx` |

### Why they are the same problem — 1 edge

**91 (21_2)  ≡  112 (21_20)** — *AC moves + change of variables*, 3 + 2 AC moves

```
  left  — 21_2
    start: (YYXXYxxx, YYYYYYXyyyyyx)
    change of variables: x -> x, y -> Y
      r1 = YYXXYxxx
           substitute      ->  yyXXyxxx
           invert          ->  XXXYxxYY
           rotate by 2     ->  YYXXXYxx
                               = r1
      r2 = YYYYYYXyyyyyx
           substitute      ->  yyyyyyXYYYYYx
           invert          ->  XyyyyyxYYYYYY
           rotate by 6     ->  YYYYYYXyyyyyx
                               = r2
    => (YYXXXYxx, YYYYYYXyyyyyx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYYYYXyyyyyx
        rot_0(r1^-1)     =  XXyxxxyy
        concatenate      =  YYYYYYXyyyyyxXXyxxxyy
        cancel inverses  =  YYYYYYXyyyyyXyxxxyy
        reduce cyclically=  YYYYXyyyyyXyxxx
        invert           =  XXXYxYYYYYxyyyy
        rotate by 10     =  YYYYYxyyyyXXXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYxyyyyXXXYx)

    AC move:  r2 <- rot_3(r2) . rot_2(r1)
        rot_3(r2)        =  XYxYYYYYxyyyyXX
        rot_2(r1)        =  xxYYXXXY
        concatenate      =  XYxYYYYYxyyyyXXxxYYXXXY
        cancel inverses  =  XYxYYYYYxyyXXXY
        rotate by 12     =  YYYYYxyyXXXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYxyyXXXYXYx)

    AC move:  r2 <- rot_5(r2) . rot_2(r1)
        rot_5(r2)        =  XYXYxYYYYYxyyXX
        rot_2(r1)        =  xxYYXXXY
        concatenate      =  XYXYxYYYYYxyyXXxxYYXXXY
        cancel inverses  =  XYXYxYYYYYXXY
        rotate by 8      =  YYYYYXXYXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYXXYXYXYx)
  right — 21_20
    start: (YYXXXYxx, YXYXYxYXXyxyx)
    change of variables: x -> X, y -> xY
      r1 = YYXXXYxx
           substitute      ->  yXyxxyXXX
           invert          ->  xxxYXXYxY
           rotate by 6     ->  YXXYxYxxx
                               = r1
      r2 = YXYXYxYXXyxyx
           substitute      ->  yyyXXyxxYYX
           invert          ->  xyyXXYxxYYY
           rotate by 3     ->  YYYxyyXXYxx
                               = r2
    => (YXXYxYxxx, YYYxyyXXYxx)

    AC move:  r2 <- rot_3(r2) . rot_2(r1)
        rot_3(r2)        =  YxxYYYxyyXX
        rot_2(r1)        =  xxYXXYxYx
        concatenate      =  YxxYYYxyyXXxxYXXYxYx
        cancel inverses  =  YxxYYYxyXXYxYx
        rotate by 11     =  YYYxyXXYxYxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYxYxxx, YYYxyXXYxYxYxx)
    change of variables: x -> X, y -> YX
      r1 = YXXYxYxxx
           substitute      ->  xyxxxyyXXX
           reduce          ->  yxxxyyXX
           invert          ->  xxYYXXXY
           rotate by 6     ->  YYXXXYxx
                               = r1
      r2 = YYYxyXXYxYxYxx
           substitute      ->  xyxyxyXYxxyyyXX
           reduce          ->  yxyxyXYxxyyyX
           invert          ->  xYYYXXyxYXYXY
           rotate by 12    ->  YYYXXyxYXYXYx
                               = r2
    => (YYXXXYxx, YYYXXyxYXYXYx)

    AC move:  r2 <- rot_6(r2) . rot_4(r1)
        rot_6(r2)        =  YXYXYxYYYXXyx
        rot_4(r1)        =  XYxxYYXX
        concatenate      =  YXYXYxYYYXXyxXYxxYYXX
        cancel inverses  =  YXYXYxYYYYYXX
        rotate by 7      =  YYYYYXXYXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYXXYXYXYx)
    both meet at (YYXXXYxx, YYYYYXXYXYXYx)
```

---

## Class 050

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 92 | 20_4 | `YXyxxxYXX` | `YYYYYXXXyxx` |
| 120 | 20_7 | `YXXXyxYxx` | `YYYYYXXyxxx` |

### Why they are the same problem — 1 edge

**92 (20_4)  ≡  120 (20_7)** — *change of variables only*

Substitute `x -> x, y -> Y` into **20_4** (`YXyxxxYXX`, `YYYYYXXXyxx`), then normalise:

```
  r1 = YXyxxxYXX
       substitute      ->  yXYxxxyXX
       invert          ->  xxYXXXyxY
       rotate by 7     ->  YXXXyxYxx
                           = r1 of 20_7   [MATCH]
  r2 = YYYYYXXXyxx
       substitute      ->  yyyyyXXXYxx
       invert          ->  XXyxxxYYYYY
       rotate by 5     ->  YYYYYXXyxxx
                           = r2 of 20_7   [MATCH]
```

which is exactly **20_7** = (`YXXXyxYxx`, `YYYYYXXyxxx`). No AC move was used.

---

## Class 051

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 94 | 21_4 | `YXyxxyXX` | `YYYYYYXyyyyyx` |
| 110 | 21_18 | `YXXyXYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**94 (21_4)  ≡  110 (21_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_4** (`YXyxxyXX`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXyxxyXX
       substitute      ->  yXYxxYXX
       rotate by 3     ->  YXXyXYxx
                           = r1 of 21_18   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_18   [MATCH]
```

which is exactly **21_18** = (`YXXyXYxx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 052

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 95 | 21_5 | `YXXYxxyx` | `YYYYYYXyyyyyx` |
| 108 | 21_16 | `YXyXXYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**95 (21_5)  ≡  108 (21_16)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_5** (`YXXYxxyx`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXXYxxyx
       substitute      ->  yXXyxxYx
       invert          ->  XyXXYxxY
       rotate by 1     ->  YXyXXYxx
                           = r1 of 21_16   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_16   [MATCH]
```

which is exactly **21_16** = (`YXyXXYxx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 053

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 96 | 21_6 | `YXyXXyxx` | `YYYYYYXyyyyyx` |
| 119 | 21_27 | `YXXYxxyX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**96 (21_6)  ≡  119 (21_27)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_6** (`YXyXXyxx`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXyXXyxx
       substitute      ->  yXYXXYxx
       rotate by 6     ->  YXXYxxyX
                           = r1 of 21_27   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_27   [MATCH]
```

which is exactly **21_27** = (`YXXYxxyX`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 054

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 98 | 21_8 | `YXyxxYXX` | `YYYYYYXyyyyyx` |
| 109 | 21_17 | `YXXyxYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**98 (21_8)  ≡  109 (21_17)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_8** (`YXyxxYXX`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXyxxYXX
       substitute      ->  yXYxxyXX
       invert          ->  xxYXXyxY
       rotate by 6     ->  YXXyxYxx
                           = r1 of 21_17   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_17   [MATCH]
```

which is exactly **21_17** = (`YXXyxYxx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 055

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 99 | 20_5 | `YXyxxxyXX` | `YYYYYXXYxxx` |
| 107 | 20_6 | `YXXyXYxxx` | `YYYYYXXXYxx` |

### Why they are the same problem — 1 edge

**99 (20_5)  ≡  107 (20_6)** — *change of variables only*

Substitute `x -> x, y -> Y` into **20_5** (`YXyxxxyXX`, `YYYYYXXYxxx`), then normalise:

```
  r1 = YXyxxxyXX
       substitute      ->  yXYxxxYXX
       rotate by 3     ->  YXXyXYxxx
                           = r1 of 20_6   [MATCH]
  r2 = YYYYYXXYxxx
       substitute      ->  yyyyyXXyxxx
       invert          ->  XXXYxxYYYYY
       rotate by 5     ->  YYYYYXXXYxx
                           = r2 of 20_6   [MATCH]
```

which is exactly **20_6** = (`YXXyXYxxx`, `YYYYYXXXYxx`). No AC move was used.

---

## Class 056

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 100 | 21_9 | `YYXXXyxx` | `YYYXXYxyXyXyx` |
| 111 | 21_19 | `YYXXyxxx` | `YXYXYxyXXyxyx` |

### Why they are the same problem — 1 edge

**100 (21_9)  ≡  111 (21_19)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 21_9
    start: (YYXXXyxx, YYYXXYxyXyXyx)
    => (YYXXXyxx, YYYXXYxyXyXyx)   [already Aut-minimal]

    AC move:  r2 <- rot_8(r2) . rot_4(r1^-1)
        rot_8(r2)        =  YxyXyXyxYYYXX
        rot_4(r1^-1)     =  xxyyXXYx
        concatenate      =  YxyXyXyxYYYXXxxyyXXYx
        cancel inverses  =  YxyXyXyxYXXYx
        invert           =  XyxxyXYxYxYXy
        rotate by 3      =  YXyXyxxyXYxYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YXyXyxxyXYxYx)
    change of variables: x -> X, y -> yX
      r1 = YYXXXyxx
           substitute      ->  xYxYxxxyXXX
           reduce          ->  YxYxxxyXX
           invert          ->  xxYXXXyXy
           rotate by 7     ->  YXXXyXyxx
                               = r1
      r2 = YXyXyxxyXYxYx
           substitute      ->  xYxyyXXXyxYYX
           reduce          ->  YxyyXXXyxYY
           rotate by 2     ->  YYYxyyXXXyx
                               = r2
    => (YXXXyXyxx, YYYxyyXXXyx)
  right — 21_19
    start: (YYXXyxxx, YXYXYxyXXyxyx)
    change of variables: x -> X, y -> xY
      r1 = YYXXyxxx
           substitute      ->  yXyxxYXXX
           rotate by 4     ->  YXXXyXyxx
                               = r1
      r2 = YXYXYxyXXyxyx
           substitute      ->  yyyXYxxxYYX
           invert          ->  xyyXXXyxYYY
           rotate by 3     ->  YYYxyyXXXyx
                               = r2
    => (YXXXyXyxx, YYYxyyXXXyx)
    both meet at (YXXXyXyxx, YYYxyyXXXyx)
```

---

## Class 057

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 101 | 21_10 | `YXYXYxxx` | `YYYYYYXyyyyyx` |
| 116 | 21_24 | `YXXXYxYx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**101 (21_10)  ≡  116 (21_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_10** (`YXYXYxxx`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXYXYxxx
       substitute      ->  yXyXyxxx
       invert          ->  XXXYxYxY
       rotate by 1     ->  YXXXYxYx
                           = r1 of 21_24   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_24   [MATCH]
```

which is exactly **21_24** = (`YXXXYxYx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 058

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 102 | 21_11 | `YXYxxxyX` | `YYYYYYXyyyyyx` |
| 115 | 21_23 | `YXyXyxxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**102 (21_11)  ≡  115 (21_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_11** (`YXYxxxyX`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXYxxxyX
       substitute      ->  yXyxxxYX
       rotate by 2     ->  YXyXyxxx
                           = r1 of 21_23   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_23   [MATCH]
```

which is exactly **21_23** = (`YXyXyxxx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 059

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 103 | 21_12 | `YXyXYxxx` | `YYYYYYXyyyyyx` |
| 114 | 21_22 | `YXyxxxyX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**103 (21_12)  ≡  114 (21_22)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_12** (`YXyXYxxx`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXyXYxxx
       substitute      ->  yXYXyxxx
       rotate by 6     ->  YXyxxxyX
                           = r1 of 21_22   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_22   [MATCH]
```

which is exactly **21_22** = (`YXyxxxyX`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 060

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 104 | 21_13 | `YXXXyxYx` | `YYYYYYXyyyyyx` |
| 113 | 21_21 | `YXYXyxxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**104 (21_13)  ≡  113 (21_21)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_13** (`YXXXyxYx`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YXXXyxYx
       substitute      ->  yXXXYxyx
       invert          ->  XYXyxxxY
       rotate by 1     ->  YXYXyxxx
                           = r1 of 21_21   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_21   [MATCH]
```

which is exactly **21_21** = (`YXYXyxxx`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 061

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 105 | 21_14 | `YYxxxYXX` | `YYYYYYXyyyyyx` |
| 118 | 21_26 | `YYxxYXXX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**105 (21_14)  ≡  118 (21_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_14** (`YYxxxYXX`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YYxxxYXX
       substitute      ->  yyxxxyXX
       invert          ->  xxYXXXYY
       rotate by 2     ->  YYxxYXXX
                           = r1 of 21_26   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_26   [MATCH]
```

which is exactly **21_26** = (`YYxxYXXX`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 062

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 106 | 21_15 | `YYxxxyXX` | `YYYYYYXyyyyyx` |
| 117 | 21_25 | `YYxxyXXX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**106 (21_15)  ≡  117 (21_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_15** (`YYxxxyXX`, `YYYYYYXyyyyyx`), then normalise:

```
  r1 = YYxxxyXX
       substitute      ->  yyxxxYXX
       invert          ->  xxyXXXYY
       rotate by 2     ->  YYxxyXXX
                           = r1 of 21_25   [MATCH]
  r2 = YYYYYYXyyyyyx
       substitute      ->  yyyyyyXYYYYYx
       invert          ->  XyyyyyxYYYYYY
       rotate by 6     ->  YYYYYYXyyyyyx
                           = r2 of 21_25   [MATCH]
```

which is exactly **21_25** = (`YYxxyXXX`, `YYYYYYXyyyyyx`). No AC move was used.

---

## Class 063

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 125 | 17_34 | `YYXXyxx` | `YYYYYXyXyx` |
| 131 | 17_36 | `YYXXyxx` | `YYxyxyxYXX` |

### Why they are the same problem — 1 edge

**131 (17_36)  ≡  125 (17_34)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 17_36
    start: (YYXXyxx, YYxyxyxYXX)
    change of variables: x -> X, y -> xY
      r1 = YYXXyxx
           substitute      ->  yXyxxYXX
           rotate by 3     ->  YXXyXyxx
                               = r1
      r2 = YYxyxyxYXX
           substitute      ->  yXyXYYXyx
           rotate by 5     ->  YYXyxyXyX
                               = r2
    => (YXXyXyxx, YYXyxyXyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYXyxyXyX
        rot_1(r1)        =  xYXXyXyx
        concatenate      =  YYXyxyXyXxYXXyXyx
        cancel inverses  =  YYXyxyXXXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXyXyxx, YYXyxyXXXyXyx)
    change of variables: x -> X, y -> yX
      r1 = YXXyXyxx
           substitute      ->  xYxxyyXXX
           reduce          ->  YxxyyXX
           invert          ->  xxYYXXy
           rotate by 5     ->  YYXXyxx
                               = r1
      r2 = YYXyxyXXXyXyx
           substitute      ->  xYxYxyXXyxxyyXX
           reduce          ->  YxYxyXXyxxyyX
           invert          ->  xYYXXYxxYXyXy
           rotate by 12    ->  YYXXYxxYXyXyx
                               = r2
    => (YYXXyxx, YYXXYxxYXyXyx)
  right — 17_34
    start: (YYXXyxx, YYYYYXyXyx)
    => (YYXXyxx, YYYYYXyXyx)   [already Aut-minimal]

    AC move:  r2 <- rot_6(r2) . rot_2(r1^-1)
        rot_6(r2)        =  YXyXyxYYYY
        rot_2(r1^-1)     =  yyXXYxx
        concatenate      =  YXyXyxYYYYyyXXYxx
        cancel inverses  =  YXyXyxYYXXYxx
        rotate by 7      =  YYXXYxxYXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyxx, YYXXYxxYXyXyx)
    both meet at (YYXXyxx, YYXXYxxYXyXyx)
```

---

## Class 064

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 126 | 19_33 | `YYXXyx` | `YYYXYxyxyXXyX` |
| 130 | 19_34 | `YYXyxx` | `YYxxYxxyXyXYx` |

### Why they are the same problem — 1 edge

**126 (19_33)  ≡  130 (19_34)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 19_33
    start: (YYXXyx, YYYXYxyxyXXyX)
    => (YYXXyx, YYYXYxyxyXXyX)   [already Aut-minimal]

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYXYxyxyXXyX
        rot_1(r1)        =  xYYXXy
        concatenate      =  YYYXYxyxyXXyXxYYXXy
        cancel inverses  =  YYYXYxyxyXXYXXy
        reduce cyclically=  YYXYxyxyXXYXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYXYxyxyXXYXX)
    change of variables: x -> x, y -> Xy
      r1 = YYXXyx
           substitute      ->  YxYXXyx
           rotate by 5     ->  YXXyxYx
                               = r1
      r2 = YYXYxyxyXXYXX
           substitute      ->  YxYYxyyXXYX
           invert          ->  xyxxYYXyyXy
           rotate by 7     ->  YYXyyXyxyxx
                               = r2
    => (YXXyxYx, YYXyyXyxyxx)
  right — 19_34
    start: (YYXyxx, YYxxYxxyXyXYx)
    change of variables: x -> x, y -> Yx
      r1 = YYXyxx
           substitute      ->  XyXyXYxxx
           reduce          ->  yXyXYxx
           invert          ->  XXyxYxY
           rotate by 1     ->  YXXyxYx
                               = r1
      r2 = YYxxYxxyXyXYx
           substitute      ->  XyXyxyxxYYXyx
           reduce          ->  yXyxyxxYYXy
           rotate by 4     ->  YYXyyXyxyxx
                               = r2
    => (YXXyxYx, YYXyyXyxyxx)
    both meet at (YXXyxYx, YYXyyXyxyxx)
```

---

## Class 065

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 128 | 16_7 | `YYxYxyX` | `YXXXyxxYx` |
| 132 | 16_8 | `YYxyXYX` | `YXYXXyxxx` |

### Why they are the same problem — 1 edge

**128 (16_7)  ≡  132 (16_8)** — *change of variables only*

Substitute `x -> x, y -> Y` into **16_7** (`YYxYxyX`, `YXXXyxxYx`), then normalise:

```
  r1 = YYxYxyX
       substitute      ->  yyxyxYX
       invert          ->  xyXYXYY
       rotate by 2     ->  YYxyXYX
                           = r1 of 16_8   [MATCH]
  r2 = YXXXyxxYx
       substitute      ->  yXXXYxxyx
       invert          ->  XYXXyxxxY
       rotate by 1     ->  YXYXXyxxx
                           = r2 of 16_8   [MATCH]
```

which is exactly **16_8** = (`YYxyXYX`, `YXYXXyxxx`). No AC move was used.

---

## Class 066

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 134 | 22_1 | `YXXYxxx` | `YYYYYYYXyyyyyyx` |
| 140 | 22_4 | `YXXXYxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**134 (22_1)  ≡  140 (22_4)** — *change of variables only*

Substitute `x -> x, y -> Y` into **22_1** (`YXXYxxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXXYxxx
       substitute      ->  yXXyxxx
       invert          ->  XXXYxxY
       rotate by 1     ->  YXXXYxx
                           = r1 of 22_4   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 22_4   [MATCH]
```

which is exactly **22_4** = (`YXXXYxx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 067

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 135 | 22_2 | `YYYxyyX` | `YXXXXXXXyxxxxxx` |
| 139 | 22_3 | `YYYxyyX` | `YXXXXXXyxxxxxxx` |

### Why they are the same problem — 1 edge

**135 (22_2)  ≡  139 (22_3)** — *change of variables only*

Substitute `x -> x, y -> Y` into **22_2** (`YYYxyyX`, `YXXXXXXXyxxxxxx`), then normalise:

```
  r1 = YYYxyyX
       substitute      ->  yyyxYYX
       invert          ->  xyyXYYY
       rotate by 3     ->  YYYxyyX
                           = r1 of 22_3   [MATCH]
  r2 = YXXXXXXXyxxxxxx
       substitute      ->  yXXXXXXXYxxxxxx
       invert          ->  XXXXXXyxxxxxxxY
       rotate by 1     ->  YXXXXXXyxxxxxxx
                           = r2 of 22_3   [MATCH]
```

which is exactly **22_3** = (`YYYxyyX`, `YXXXXXXyxxxxxxx`). No AC move was used.

---

## Class 068

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 136 | 17_37 | `YXyXXYxx` | `YYYYXyXyx` |
| 142 | 17_40 | `YXXYxxyx` | `YYYXyXyxx` |

### Why they are the same problem — 1 edge

**136 (17_37)  ≡  142 (17_40)** — *pure AC path*, 1 + 0 AC moves

```
  left  — 17_37
    start: (YXyXXYxx, YYYYXyXyx)
    change of variables: x -> x, y -> Y
      r1 = YXyXXYxx
           substitute      ->  yXYXXyxx
           invert          ->  XXYxxyxY
           rotate by 1     ->  YXXYxxyx
                               = r1
      r2 = YYYYXyXyx
           substitute      ->  yyyyXYXYx
           invert          ->  XyxyxYYYY
           rotate by 4     ->  YYYYXyxyx
                               = r2
    => (YXXYxxyx, YYYYXyxyx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYYXyxyx
        rot_0(r1^-1)     =  XYXXyxxy
        concatenate      =  YYYYXyxyxXYXXyxxy
        cancel inverses  =  YYYYXyXyxxy
        reduce cyclically=  YYYXyXyxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYxxyx, YYYXyXyxx)
  right — 17_40
    start: (YXXYxxyx, YYYXyXyxx)
    => (YXXYxxyx, YYYXyXyxx)   [already Aut-minimal]
    both meet at (YXXYxxyx, YYYXyXyxx)
```

Every step is an AC move — no change of variables inside the path. So `17_37 ~AC psi(17_40)` with `psi: x -> x, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `17_40`, not to `17_40` itself.

---

## Class 069

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 137 | 17_38 | `YYYXXyx` | `YYXYxyxyXX` |
| 141 | 17_39 | `YYYXyxyx` | `YXYXyXyxx` |

### Why they are the same problem — 1 edge

**137 (17_38)  ≡  141 (17_39)** — *change of variables only*

Substitute `x -> yx, y -> Y` into **17_38** (`YYYXXyx`, `YYXYxyxyXX`), then normalise:

```
  r1 = YYYXXyx
       substitute      ->  yyyXYXYx
       invert          ->  XyxyxYYY
       rotate by 3     ->  YYYXyxyx
                           = r1 of 17_39   [MATCH]
  r2 = YYXYxyxyXX
       substitute      ->  yyXyxxYXYXY
       reduce          ->  yXyxxYXYX
       rotate by 4     ->  YXYXyXyxx
                           = r2 of 17_39   [MATCH]
```

which is exactly **17_39** = (`YYYXyxyx`, `YXYXyXyxx`). No AC move was used.

---

## Class 070

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 138 | 19_35 | `YYYYXXyyx` | `YYYYYxyyXX` |
| 143 | 19_36 | `YYXyyXYYx` | `YYYYYYYXXX` |

### Why they are the same problem — 1 edge

**143 (19_36)  ≡  138 (19_35)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 19_36
    start: (YYXyyXYYx, YYYYYYYXXX)
    change of variables: x -> y, y -> X
      r1 = YYXyyXYYx
           substitute      ->  xxYXXYxxy
           rotate by 7     ->  YXXYxxyxx
                               = r1
      r2 = YYYYYYYXXX
           substitute      ->  xxxxxxxYYY
           rotate by 3     ->  YYYxxxxxxx
                               = r2
    => (YXXYxxyxx, YYYxxxxxxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYxxxxxxx
        rot_0(r1^-1)     =  XXYXXyxxy
        concatenate      =  YYYxxxxxxxXXYXXyxxy
        cancel inverses  =  YYYxxxxxYXXyxxy
        reduce cyclically=  YYxxxxxYXXyxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYxxyxx, YYxxxxxYXXyxx)

    AC move:  r1 <- rot_0(r1) . rot_0(r2^-1)
        rot_0(r1)        =  YXXYxxyxx
        rot_0(r2^-1)     =  XXYxxyXXXXXyy
        concatenate      =  YXXYxxyxxXXYxxyXXXXXyy
        cancel inverses  =  YXXYxxxxyXXXXXyy
        reduce cyclically=  XXYxxxxyXXXXXy
        invert           =  YxxxxxYXXXXyxx
        rotate by 8      =  YXXXXyxxYxxxxx
                            ^ the new r2
        r2 is untouched by the move (it becomes r1: the two relators sort into the other order)
    => (YYxxxxxYXXyxx, YXXXXyxxYxxxxx)
    change of variables: x -> x, y -> yxxxxx
      r2 = YXXXXyxxYxxxxx
           substitute      ->  XXXXXYXXXXyxxYxxxxx
           reduce          ->  YXXXXyxxY
           rotate by 1     ->  YYXXXXyxx
                               = r1
      r1 = YYxxxxxYXXyxx
           substitute      ->  XXXXXYXXXXXYYXXyxxxxxxx
           reduce          ->  YXXXXXYYXXyxx
           rotate by 7     ->  YYXXyxxYXXXXX
                               = r2
    => (YYXXXXyxx, YYXXyxxYXXXXX)
  right — 19_35
    start: (YYYYXXyyx, YYYYYxyyXX)
    change of variables: x -> Y, y -> X
      r1 = YYYYXXyyx
           substitute      ->  xxxxyyXXY
           invert          ->  yxxYYXXXX
           rotate by 6     ->  YYXXXXyxx
                               = r1
      r2 = YYYYYxyyXX
           substitute      ->  xxxxxYXXyy
           invert          ->  YYxxyXXXXX
                               = r2
    => (YYXXXXyxx, YYxxyXXXXX)

    AC move:  r2 <- rot_5(r2) . rot_8(r1)
        rot_5(r2)        =  XXXXXYYxxy
        rot_8(r1)        =  YXXXXyxxY
        concatenate      =  XXXXXYYxxyYXXXXyxxY
        cancel inverses  =  XXXXXYYXXyxxY
        rotate by 8      =  YYXXyxxYXXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyxx, YYXXyxxYXXXXX)
    both meet at (YYXXXXyxx, YYXXyxxYXXXXX)
```

---

## Class 071

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 144 | 23_1 | `YYXXYxxx` | `YYYYYYYXyyyyyyx` |
| 167 | 23_13 | `YYXXXYxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**144 (23_1)  ≡  167 (23_13)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_1** (`YYXXYxxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YYXXYxxx
       substitute      ->  yyXXyxxx
       invert          ->  XXXYxxYY
       rotate by 2     ->  YYXXXYxx
                           = r1 of 23_13   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_13   [MATCH]
```

which is exactly **23_13** = (`YYXXXYxx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 072

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 145 | 21_30 | `YXyxxxYXX` | `YYYYYYXXXyxx` |
| 175 | 21_33 | `YXXXyxYxx` | `YYYYYYXXyxxx` |

### Why they are the same problem — 1 edge

**145 (21_30)  ≡  175 (21_33)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_30** (`YXyxxxYXX`, `YYYYYYXXXyxx`), then normalise:

```
  r1 = YXyxxxYXX
       substitute      ->  yXYxxxyXX
       invert          ->  xxYXXXyxY
       rotate by 7     ->  YXXXyxYxx
                           = r1 of 21_33   [MATCH]
  r2 = YYYYYYXXXyxx
       substitute      ->  yyyyyyXXXYxx
       invert          ->  XXyxxxYYYYYY
       rotate by 6     ->  YYYYYYXXyxxx
                           = r2 of 21_33   [MATCH]
```

which is exactly **21_33** = (`YXXXyxYxx`, `YYYYYYXXyxxx`). No AC move was used.

---

## Class 073

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 146 | 22_5 | `YXXYxxxyX` | `YYYYYYYxxxYXX` |
| 177 | 22_12 | `YXyXXyxxx` | `YYYYYYYxxYXXX` |

### Why they are the same problem — 1 edge

**146 (22_5)  ≡  177 (22_12)** — *change of variables only*

Substitute `x -> x, y -> Y` into **22_5** (`YXXYxxxyX`, `YYYYYYYxxxYXX`), then normalise:

```
  r1 = YXXYxxxyX
       substitute      ->  yXXyxxxYX
       rotate by 2     ->  YXyXXyxxx
                           = r1 of 22_12   [MATCH]
  r2 = YYYYYYYxxxYXX
       substitute      ->  yyyyyyyxxxyXX
       invert          ->  xxYXXXYYYYYYY
       rotate by 7     ->  YYYYYYYxxYXXX
                           = r2 of 22_12   [MATCH]
```

which is exactly **22_12** = (`YXyXXyxxx`, `YYYYYYYxxYXXX`). No AC move was used.

---

## Class 074

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 147 | 22_6 | `YYYYYxxyXXX` | `YYXyxxyxYXX` |
| 165 | 22_10 | `YYYYYxxxyXX` | `YYxxYXyXXyx` |

### Why they are the same problem — 1 edge

**147 (22_6)  ≡  165 (22_10)** — *change of variables only*

Substitute `x -> x, y -> Y` into **22_6** (`YYYYYxxyXXX`, `YYXyxxyxYXX`), then normalise:

```
  r1 = YYYYYxxyXXX
       substitute      ->  yyyyyxxYXXX
       invert          ->  xxxyXXYYYYY
       rotate by 5     ->  YYYYYxxxyXX
                           = r1 of 22_10   [MATCH]
  r2 = YYXyxxyxYXX
       substitute      ->  yyXYxxYxyXX
       invert          ->  xxYXyXXyxYY
       rotate by 2     ->  YYxxYXyXXyx
                           = r2 of 22_10   [MATCH]
```

which is exactly **22_10** = (`YYYYYxxxyXX`, `YYxxYXyXXyx`). No AC move was used.

---

## Class 075

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 148 | 23_2 | `YXXYxxyx` | `YYYYYYYXyyyyyyx` |
| 163 | 23_11 | `YXyXXYxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**148 (23_2)  ≡  163 (23_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_2** (`YXXYxxyx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXXYxxyx
       substitute      ->  yXXyxxYx
       invert          ->  XyXXYxxY
       rotate by 1     ->  YXyXXYxx
                           = r1 of 23_11   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_11   [MATCH]
```

which is exactly **23_11** = (`YXyXXYxx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 076

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 149 | 23_3 | `YXyXXyxx` | `YYYYYYYXyyyyyyx` |
| 174 | 23_20 | `YXXYxxyX` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**149 (23_3)  ≡  174 (23_20)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_3** (`YXyXXyxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXyXXyxx
       substitute      ->  yXYXXYxx
       rotate by 6     ->  YXXYxxyX
                           = r1 of 23_20   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_20   [MATCH]
```

which is exactly **23_20** = (`YXXYxxyX`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 077

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 150 | 22_7 | `YXyXXYxxx` | `YYYYYYYxxxyXX` |
| 176 | 22_11 | `YXXyxxxyX` | `YYYYYYYxxyXXX` |

### Why they are the same problem — 1 edge

**150 (22_7)  ≡  176 (22_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into **22_7** (`YXyXXYxxx`, `YYYYYYYxxxyXX`), then normalise:

```
  r1 = YXyXXYxxx
       substitute      ->  yXYXXyxxx
       rotate by 7     ->  YXXyxxxyX
                           = r1 of 22_11   [MATCH]
  r2 = YYYYYYYxxxyXX
       substitute      ->  yyyyyyyxxxYXX
       invert          ->  xxyXXXYYYYYYY
       rotate by 7     ->  YYYYYYYxxyXXX
                           = r2 of 22_11   [MATCH]
```

which is exactly **22_11** = (`YXXyxxxyX`, `YYYYYYYxxyXXX`). No AC move was used.

---

## Class 078

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 151 | 22_8 | `YYYYYxxYXXX` | `YYXyxxYxyXX` |
| 164 | 22_9 | `YYYYYxxxYXX` | `YYxxyXYXXyx` |

### Why they are the same problem — 1 edge

**151 (22_8)  ≡  164 (22_9)** — *change of variables only*

Substitute `x -> x, y -> Y` into **22_8** (`YYYYYxxYXXX`, `YYXyxxYxyXX`), then normalise:

```
  r1 = YYYYYxxYXXX
       substitute      ->  yyyyyxxyXXX
       invert          ->  xxxYXXYYYYY
       rotate by 5     ->  YYYYYxxxYXX
                           = r1 of 22_9   [MATCH]
  r2 = YYXyxxYxyXX
       substitute      ->  yyXYxxyxYXX
       invert          ->  xxyXYXXyxYY
       rotate by 2     ->  YYxxyXYXXyx
                           = r2 of 22_9   [MATCH]
```

which is exactly **22_9** = (`YYYYYxxxYXX`, `YYxxyXYXXyx`). No AC move was used.

---

## Class 079

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 152 | 21_31 | `YXyxxxyXX` | `YYYYYYXXYxxx` |
| 162 | 21_32 | `YXXyXYxxx` | `YYYYYYXXXYxx` |

### Why they are the same problem — 1 edge

**152 (21_31)  ≡  162 (21_32)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_31** (`YXyxxxyXX`, `YYYYYYXXYxxx`), then normalise:

```
  r1 = YXyxxxyXX
       substitute      ->  yXYxxxYXX
       rotate by 3     ->  YXXyXYxxx
                           = r1 of 21_32   [MATCH]
  r2 = YYYYYYXXYxxx
       substitute      ->  yyyyyyXXyxxx
       invert          ->  XXXYxxYYYYYY
       rotate by 6     ->  YYYYYYXXXYxx
                           = r2 of 21_32   [MATCH]
```

which is exactly **21_32** = (`YXXyXYxxx`, `YYYYYYXXXYxx`). No AC move was used.

---

## Class 080

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 153 | 23_4 | `YYXXXyxx` | `YYYYYYYXyyyyyyx` |
| 166 | 23_12 | `YYXXyxxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**153 (23_4)  ≡  166 (23_12)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_4** (`YYXXXyxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YYXXXyxx
       substitute      ->  yyXXXYxx
       invert          ->  XXyxxxYY
       rotate by 2     ->  YYXXyxxx
                           = r1 of 23_12   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_12   [MATCH]
```

which is exactly **23_12** = (`YYXXyxxx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 081

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 154 | 23_5 | `YXYXYxxx` | `YYYYYYYXyyyyyyx` |
| 171 | 23_17 | `YXXXYxYx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**154 (23_5)  ≡  171 (23_17)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_5** (`YXYXYxxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXYXYxxx
       substitute      ->  yXyXyxxx
       invert          ->  XXXYxYxY
       rotate by 1     ->  YXXXYxYx
                           = r1 of 23_17   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_17   [MATCH]
```

which is exactly **23_17** = (`YXXXYxYx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 082

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 155 | 23_6 | `YXYxxxyX` | `YYYYYYYXyyyyyyx` |
| 170 | 23_16 | `YXyXyxxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**155 (23_6)  ≡  170 (23_16)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_6** (`YXYxxxyX`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXYxxxyX
       substitute      ->  yXyxxxYX
       rotate by 2     ->  YXyXyxxx
                           = r1 of 23_16   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_16   [MATCH]
```

which is exactly **23_16** = (`YXyXyxxx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 083

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 156 | 23_7 | `YXyXYxxx` | `YYYYYYYXyyyyyyx` |
| 169 | 23_15 | `YXyxxxyX` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**156 (23_7)  ≡  169 (23_15)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_7** (`YXyXYxxx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXyXYxxx
       substitute      ->  yXYXyxxx
       rotate by 6     ->  YXyxxxyX
                           = r1 of 23_15   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_15   [MATCH]
```

which is exactly **23_15** = (`YXyxxxyX`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 084

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 157 | 23_8 | `YXXXyxYx` | `YYYYYYYXyyyyyyx` |
| 168 | 23_14 | `YXYXyxxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**157 (23_8)  ≡  168 (23_14)** — *change of variables only*

Substitute `x -> x, y -> Y` into **23_8** (`YXXXyxYx`, `YYYYYYYXyyyyyyx`), then normalise:

```
  r1 = YXXXyxYx
       substitute      ->  yXXXYxyx
       invert          ->  XYXyxxxY
       rotate by 1     ->  YXYXyxxx
                           = r1 of 23_14   [MATCH]
  r2 = YYYYYYYXyyyyyyx
       substitute      ->  yyyyyyyXYYYYYYx
       invert          ->  XyyyyyyxYYYYYYY
       rotate by 7     ->  YYYYYYYXyyyyyyx
                           = r2 of 23_14   [MATCH]
```

which is exactly **23_14** = (`YXYXyxxx`, `YYYYYYYXyyyyyyx`). No AC move was used.

---

## Class 085

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 158 | 23_9 | `YYxxxYXX` | `YXYxxyXyXyXYxYx` |
| 173 | 23_19 | `YYxxYXXX` | `YYYYYxYXYXYxyXX` |

### Why they are the same problem — 1 edge

**173 (23_19)  ≡  158 (23_9)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 23_19
    start: (YYxxYXXX, YYYYYxYXYXYxyXX)
    change of variables: x -> X, y -> Y
      r1 = YYxxYXXX
           substitute      ->  yyXXyxxx
           invert          ->  XXXYxxYY
           rotate by 2     ->  YYXXXYxx
                               = r1
      r2 = YYYYYxYXYXYxyXX
           substitute      ->  yyyyyXyxyxyXYxx
           invert          ->  XXyxYXYXYxYYYYY
           rotate by 5     ->  YYYYYXXyxYXYXYx
                               = r2
    => (YYXXXYxx, YYYYYXXyxYXYXYx)

    AC move:  r2 <- rot_8(r2) . rot_4(r1^-1)
        rot_8(r2)        =  yxYXYXYxYYYYYXX
        rot_4(r1^-1)     =  xxyyXXyx
        concatenate      =  yxYXYXYxYYYYYXXxxyyXXyx
        cancel inverses  =  yxYXYXYxYYYXXyx
        rotate by 7      =  YYYXXyxyxYXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYXXyxyxYXYXYx)
  right — 23_9
    start: (YYxxxYXX, YXYxxyXyXyXYxYx)
    change of variables: x -> x, y -> Yx
      r1 = YYxxxYXX
           substitute      ->  XyXyxxyXX
           invert          ->  xxYXXYxYx
           rotate by 7     ->  YXXYxYxxx
                               = r1
      r2 = YXYxxyXyXyXYxYx
           substitute      ->  XyXXyxxYYYXyyx
           reduce          ->  yXXyxxYYYXyy
           rotate by 6     ->  YYYXyyyXXyxx
                               = r2
    => (YXXYxYxxx, YYYXyyyXXyxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYXyyyXXyxx
        rot_0(r1^-1)     =  XXXyXyxxy
        concatenate      =  YYYXyyyXXyxxXXXyXyxxy
        cancel inverses  =  YYYXyyyXXyXyXyxxy
        reduce cyclically=  YYXyyyXXyXyXyxx
        invert           =  XXYxYxYxxYYYxyy
        rotate by 6      =  YYYxyyXXYxYxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYxYxxx, YYYxyyXXYxYxYxx)
    change of variables: x -> X, y -> YX
      r1 = YXXYxYxxx
           substitute      ->  xyxxxyyXXX
           reduce          ->  yxxxyyXX
           invert          ->  xxYYXXXY
           rotate by 6     ->  YYXXXYxx
                               = r1
      r2 = YYYxyyXXYxYxYxx
           substitute      ->  xyxyxyXYXYxxyyyXX
           reduce          ->  yxyxyXYXYxxyyyX
           invert          ->  xYYYXXyxyxYXYXY
           rotate by 14    ->  YYYXXyxyxYXYXYx
                               = r2
    => (YYXXXYxx, YYYXXyxyxYXYXYx)
    both meet at (YYXXXYxx, YYYXXyxyxYXYXYx)
```

---

## Class 086

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 159 | 23_10 | `YYxxxyXX` | `YYYYYxxYXyxyxyX` |
| 172 | 23_18 | `YYxxyXXX` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**172 (23_18)  ≡  159 (23_10)** — *pure AC path*, 2 + 2 AC moves

```
  left  — 23_18
    start: (YYxxyXXX, YYYYYYYXyyyyyyx)
    change of variables: x -> X, y -> Y
      r1 = YYxxyXXX
           substitute      ->  yyXXYxxx
           invert          ->  XXXyxxYY
           rotate by 2     ->  YYXXXyxx
                               = r1
      r2 = YYYYYYYXyyyyyyx
           substitute      ->  yyyyyyyxYYYYYYX
           invert          ->  xyyyyyyXYYYYYYY
           rotate by 7     ->  YYYYYYYxyyyyyyX
                               = r2
    => (YYXXXyxx, YYYYYYYxyyyyyyX)

    AC move:  r2 <- rot_0(r2) . rot_1(r1)
        rot_0(r2)        =  YYYYYYYxyyyyyyX
        rot_1(r1)        =  xYYXXXyx
        concatenate      =  YYYYYYYxyyyyyyXxYYXXXyx
        cancel inverses  =  YYYYYYYxyyyyXXXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYYYYYxyyyyXXXyx)

    AC move:  r2 <- rot_3(r2) . rot_2(r1)
        rot_3(r2)        =  XyxYYYYYYYxyyyyXX
        rot_2(r1)        =  xxYYXXXy
        concatenate      =  XyxYYYYYYYxyyyyXXxxYYXXXy
        cancel inverses  =  XyxYYYYYYYxyyXXXy
        rotate by 14     =  YYYYYYYxyyXXXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYYYYYxyyXXXyXyx)
  right — 23_10
    start: (YYxxxyXX, YYYYYxxYXyxyxyX)
    change of variables: x -> X, y -> y
      r1 = YYxxxyXX
           substitute      ->  YYXXXyxx
                               = r1
      r2 = YYYYYxxYXyxyxyX
           substitute      ->  YYYYYXXYxyXyXyx
                               = r2
    => (YYXXXyxx, YYYYYXXYxyXyXyx)

    AC move:  r2 <- rot_6(r2) . rot_4(r1)
        rot_6(r2)        =  yXyXyxYYYYYXXYx
        rot_4(r1)        =  XyxxYYXX
        concatenate      =  yXyXyxYYYYYXXYxXyxxYYXX
        cancel inverses  =  yXyXyxYYYYYYYXX
        rotate by 9      =  YYYYYYYXXyXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYYYYYXXyXyXyx)

    AC move:  r2 <- rot_5(r2) . rot_6(r1^-1)
        rot_5(r2)        =  XyXyxYYYYYYYXXy
        rot_6(r1^-1)     =  YxxxyyXX
        concatenate      =  XyXyxYYYYYYYXXyYxxxyyXX
        cancel inverses  =  XyXyxYYYYYYYxyyXX
        rotate by 12     =  YYYYYYYxyyXXXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYYYYYxyyXXXyXyx)
    both meet at (YYXXXyxx, YYYYYYYxyyXXXyXyx)
```

Every step is an AC move — no change of variables inside the path. So `23_18 ~AC psi(23_10)` with `psi: x -> x, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `23_10`, not to `23_10` itself.

---

## Class 087

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 160 | 18_4 | `YYYXXYxyX` | `YYxYXXYXX` |
| 178 | 18_5 | `YYYxyXYxx` | `YYxxYxxYX` |

### Why they are the same problem — 1 edge

**160 (18_4)  ≡  178 (18_5)** — *change of variables only*

Substitute `x -> x, y -> Y` into **18_4** (`YYYXXYxyX`, `YYxYXXYXX`), then normalise:

```
  r1 = YYYXXYxyX
       substitute      ->  yyyXXyxYX
       invert          ->  xyXYxxYYY
       rotate by 3     ->  YYYxyXYxx
                           = r1 of 18_5   [MATCH]
  r2 = YYxYXXYXX
       substitute      ->  yyxyXXyXX
       invert          ->  xxYxxYXYY
       rotate by 2     ->  YYxxYxxYX
                           = r2 of 18_5   [MATCH]
```

which is exactly **18_5** = (`YYYxyXYxx`, `YYxxYxxYX`). No AC move was used.

---

## Class 088

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 185 | 21_35 | `YYxxyX` | `YYYYYYYxyxyXyxx` |
| 189 | 21_38 | `YYxyXX` | `YYYYYYYXyXXyxyX` |

### Why they are the same problem — 1 edge

**189 (21_38)  ≡  185 (21_35)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 21_38
    start: (YYxyXX, YYYYYYYXyXXyxyX)
    change of variables: x -> X, y -> Y
      r1 = YYxyXX
           substitute      ->  yyXYxx
           invert          ->  XXyxYY
           rotate by 2     ->  YYXXyx
                               = r1
      r2 = YYYYYYYXyXXyxyX
           substitute      ->  yyyyyyyxYxxYXYx
           invert          ->  XyxyXXyXYYYYYYY
           rotate by 7     ->  YYYYYYYXyxyXXyX
                               = r2
    => (YYXXyx, YYYYYYYXyxyXXyX)

    AC move:  r2 <- rot_4(r2) . rot_5(r1)
        rot_4(r2)        =  XXyXYYYYYYYXyxy
        rot_5(r1)        =  YXXyxY
        concatenate      =  XXyXYYYYYYYXyxyYXXyxY
        cancel inverses  =  XXyXYYYYYYYXyXyxY
        rotate by 13     =  YYYYYYYXyXyxYXXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYYYYYYXyXyxYXXyX)
    change of variables: x -> Y, y -> X
      r1 = YYXXyx
           substitute      ->  xxyyXY
           invert          ->  yxYYXX
           rotate by 4     ->  YYXXyx
                               = r1
      r2 = YYYYYYYXyXyxYXXyX
           substitute      ->  xxxxxxxyXyXYxyyXy
           invert          ->  YxYYXyxYxYXXXXXXX
           rotate by 15    ->  YYXyxYxYXXXXXXXYx
                               = r2
    => (YYXXyx, YYXyxYxYXXXXXXXYx)
  right — 21_35
    start: (YYxxyX, YYYYYYYxyxyXyxx)
    change of variables: x -> X, y -> y
      r1 = YYxxyX
           substitute      ->  YYXXyx
                               = r1
      r2 = YYYYYYYxyxyXyxx
           substitute      ->  YYYYYYYXyXyxyXX
                               = r2
    => (YYXXyx, YYYYYYYXyXyxyXX)

    AC move:  r2 <- rot_1(r2) . rot_1(r1)
        rot_1(r2)        =  XYYYYYYYXyXyxyX
        rot_1(r1)        =  xYYXXy
        concatenate      =  XYYYYYYYXyXyxyXxYYXXy
        cancel inverses  =  XYYYYYYYXyXyxYXXy
        rotate by 16     =  YYYYYYYXyXyxYXXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXyx, YYYYYYYXyXyxYXXyX)
    change of variables: x -> Y, y -> X
      r1 = YYXXyx
           substitute      ->  xxyyXY
           invert          ->  yxYYXX
           rotate by 4     ->  YYXXyx
                               = r1
      r2 = YYYYYYYXyXyxYXXyX
           substitute      ->  xxxxxxxyXyXYxyyXy
           invert          ->  YxYYXyxYxYXXXXXXX
           rotate by 15    ->  YYXyxYxYXXXXXXXYx
                               = r2
    => (YYXXyx, YYXyxYxYXXXXXXXYx)
    both meet at (YYXXyx, YYXyxYxYXXXXXXXYx)
```

---

## Class 089

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 192 | 24_1 | `YXXYxxx` | `YYYYYYYYXyyyyyyyx` |
| 206 | 24_4 | `YXXXYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**192 (24_1)  ≡  206 (24_4)** — *change of variables only*

Substitute `x -> x, y -> Y` into **24_1** (`YXXYxxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXXYxxx
       substitute      ->  yXXyxxx
       invert          ->  XXXYxxY
       rotate by 1     ->  YXXXYxx
                           = r1 of 24_4   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 24_4   [MATCH]
```

which is exactly **24_4** = (`YXXXYxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 090

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 193 | 24_2 | `YYYXyyx` | `YXXXXXXXyxxxxxxxx` |
| 205 | 24_3 | `YXXyxxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**193 (24_2)  ≡  205 (24_3)** — *change of variables only*

Substitute `x -> y, y -> x` into **24_2** (`YYYXyyx`, `YXXXXXXXyxxxxxxxx`), then normalise:

```
  r1 = YYYXyyx
       substitute      ->  XXXYxxy
       invert          ->  YXXyxxx
                           = r1 of 24_3   [MATCH]
  r2 = YXXXXXXXyxxxxxxxx
       substitute      ->  XYYYYYYYxyyyyyyyy
       invert          ->  YYYYYYYYXyyyyyyyx
                           = r2 of 24_3   [MATCH]
```

which is exactly **24_3** = (`YXXyxxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 091

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 194 | 19_39 | `YYYXYxyx` | `YYXXYxxyXyx` |
| 208 | 19_41 | `YYYXyXYx` | `YXXYxYXXyxx` |

### Why they are the same problem — 1 edge

**194 (19_39)  ≡  208 (19_41)** — *pure AC path*, 1 + 0 AC moves

```
  left  — 19_39
    start: (YYYXYxyx, YYXXYxxyXyx)
    change of variables: x -> Y, y -> x
      r1 = YYYXYxyx
           substitute      ->  XXXyXYxY
           rotate by 1     ->  YXXXyXYx
                               = r1
      r2 = YYXXYxxyXyx
           substitute      ->  XXyyXYYxyxY
           rotate by 6     ->  YYxyxYXXyyX
                               = r2
    => (YXXXyXYx, YYxyxYXXyyX)

    AC move:  r2 <- rot_3(r2) . rot_3(r1^-1)
        rot_3(r2)        =  yyXYYxyxYXX
        rot_3(r1^-1)     =  xxyXyxYx
        concatenate      =  yyXYYxyxYXXxxyXyxYx
        cancel inverses  =  yyXYYxyyxYx
        invert           =  XyXYYXyyxYY
        rotate by 8      =  YYXyyxYYXyX
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyXYx, YYXyyxYYXyX)
  right — 19_41
    start: (YYYXyXYx, YXXYxYXXyxx)
    change of variables: x -> Y, y -> X
      r1 = YYYXyXYx
           substitute      ->  xxxyXyxY
           invert          ->  yXYxYXXX
           rotate by 4     ->  YXXXyXYx
                               = r1
      r2 = YXXYxYXXyxx
           substitute      ->  xyyxYxyyXYY
           invert          ->  yyxYYXyXYYX
           rotate by 3     ->  YYXyyxYYXyX
                               = r2
    => (YXXXyXYx, YYXyyxYYXyX)
    both meet at (YXXXyXYx, YYXyyxYYXyX)
```

Every step is an AC move — no change of variables inside the path. So `19_39 ~AC psi(19_41)` with `psi: x -> x, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `19_41`, not to `19_41` itself.

---

## Class 092

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 199 | 18_8 | `YYYXXyx` | `YYXYXyXyxxx` |
| 207 | 18_10 | `YYYXyxx` | `YYXXXyxyxYx` |

### Why they are the same problem — 1 edge

**199 (18_8)  ≡  207 (18_10)** — *change of variables only*

Substitute `x -> x, y -> Y` into **18_8** (`YYYXXyx`, `YYXYXyXyxxx`), then normalise:

```
  r1 = YYYXXyx
       substitute      ->  yyyXXYx
       invert          ->  XyxxYYY
       rotate by 3     ->  YYYXyxx
                           = r1 of 18_10   [MATCH]
  r2 = YYXYXyXyxxx
       substitute      ->  yyXyXYXYxxx
       invert          ->  XXXyxyxYxYY
       rotate by 2     ->  YYXXXyxyxYx
                           = r2 of 18_10   [MATCH]
```

which is exactly **18_10** = (`YYYXyxx`, `YYXXXyxyxYx`). No AC move was used.

---

## Class 093

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 200 | 20_10 | `YYXYYxyyx` | `YYYYYYYxxxx` |
| 209 | 20_11 | `YYXyyXYYx` | `YYYYYYYXXXX` |

### Why they are the same problem — 1 edge

**200 (20_10)  ≡  209 (20_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into **20_10** (`YYXYYxyyx`, `YYYYYYYxxxx`), then normalise:

```
  r1 = YYXYYxyyx
       substitute      ->  yyXyyxYYx
       invert          ->  XyyXYYxYY
       rotate by 2     ->  YYXyyXYYx
                           = r1 of 20_11   [MATCH]
  r2 = YYYYYYYxxxx
       substitute      ->  yyyyyyyxxxx
       invert          ->  XXXXYYYYYYY
       rotate by 7     ->  YYYYYYYXXXX
                           = r2 of 20_11   [MATCH]
```

which is exactly **20_11** = (`YYXyyXYYx`, `YYYYYYYXXXX`). No AC move was used.

---

## Class 094

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 213 | 25_1 | `YYXXYxxx` | `YYYYYYYYXyyyyyyyx` |
| 244 | 25_22 | `YYXXXYxx` | `YYYXXyxyxYXYXYXYx` |

### Why they are the same problem — 1 edge

**213 (25_1)  ≡  244 (25_22)** — *AC moves + change of variables*, 4 + 2 AC moves

```
  left  — 25_1
    start: (YYXXYxxx, YYYYYYYYXyyyyyyyx)
    change of variables: x -> x, y -> Y
      r1 = YYXXYxxx
           substitute      ->  yyXXyxxx
           invert          ->  XXXYxxYY
           rotate by 2     ->  YYXXXYxx
                               = r1
      r2 = YYYYYYYYXyyyyyyyx
           substitute      ->  yyyyyyyyXYYYYYYYx
           invert          ->  XyyyyyyyxYYYYYYYY
           rotate by 8     ->  YYYYYYYYXyyyyyyyx
                               = r2
    => (YYXXXYxx, YYYYYYYYXyyyyyyyx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYYYYYYYXyyyyyyyx
        rot_0(r1^-1)     =  XXyxxxyy
        concatenate      =  YYYYYYYYXyyyyyyyxXXyxxxyy
        cancel inverses  =  YYYYYYYYXyyyyyyyXyxxxyy
        reduce cyclically=  YYYYYYXyyyyyyyXyxxx
        invert           =  XXXYxYYYYYYYxyyyyyy
        rotate by 14     =  YYYYYYYxyyyyyyXXXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYYYxyyyyyyXXXYx)

    AC move:  r2 <- rot_3(r2) . rot_2(r1)
        rot_3(r2)        =  XYxYYYYYYYxyyyyyyXX
        rot_2(r1)        =  xxYYXXXY
        concatenate      =  XYxYYYYYYYxyyyyyyXXxxYYXXXY
        cancel inverses  =  XYxYYYYYYYxyyyyXXXY
        rotate by 16     =  YYYYYYYxyyyyXXXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYYYxyyyyXXXYXYx)

    AC move:  r2 <- rot_5(r2) . rot_2(r1)
        rot_5(r2)        =  XYXYxYYYYYYYxyyyyXX
        rot_2(r1)        =  xxYYXXXY
        concatenate      =  XYXYxYYYYYYYxyyyyXXxxYYXXXY
        cancel inverses  =  XYXYxYYYYYYYxyyXXXY
        rotate by 14     =  YYYYYYYxyyXXXYXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYYYxyyXXXYXYXYx)

    AC move:  r2 <- rot_7(r2) . rot_2(r1)
        rot_7(r2)        =  XYXYXYxYYYYYYYxyyXX
        rot_2(r1)        =  xxYYXXXY
        concatenate      =  XYXYXYxYYYYYYYxyyXXxxYYXXXY
        cancel inverses  =  XYXYXYxYYYYYYYXXY
        rotate by 10     =  YYYYYYYXXYXYXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYYYXXYXYXYXYx)
  right — 25_22
    start: (YYXXXYxx, YYYXXyxyxYXYXYXYx)
    change of variables: x -> X, y -> xY
      r1 = YYXXXYxx
           substitute      ->  yXyxxyXXX
           invert          ->  xxxYXXYxY
           rotate by 6     ->  YXXYxYxxx
                               = r1
      r2 = YYYXXyxyxYXYXYXYx
           substitute      ->  yXyXyxxYYXyyyyXX
           invert          ->  xxYYYYxyyXXYxYxY
           rotate by 14    ->  YYYYxyyXXYxYxYxx
                               = r2
    => (YXXYxYxxx, YYYYxyyXXYxYxYxx)

    AC move:  r2 <- rot_7(r2) . rot_2(r1)
        rot_7(r2)        =  YxYxYxxYYYYxyyXX
        rot_2(r1)        =  xxYXXYxYx
        concatenate      =  YxYxYxxYYYYxyyXXxxYXXYxYx
        cancel inverses  =  YxYxYxxYYYYxyXXYxYx
        rotate by 12     =  YYYYxyXXYxYxYxYxYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXYxYxxx, YYYYxyXXYxYxYxYxYxx)
    change of variables: x -> X, y -> YX
      r1 = YXXYxYxxx
           substitute      ->  xyxxxyyXXX
           reduce          ->  yxxxyyXX
           invert          ->  xxYYXXXY
           rotate by 6     ->  YYXXXYxx
                               = r1
      r2 = YYYYxyXXYxYxYxYxYxx
           substitute      ->  xyxyxyxyXYxxyyyyyXX
           reduce          ->  yxyxyxyXYxxyyyyyX
           invert          ->  xYYYYYXXyxYXYXYXY
           rotate by 16    ->  YYYYYXXyxYXYXYXYx
                               = r2
    => (YYXXXYxx, YYYYYXXyxYXYXYXYx)

    AC move:  r2 <- rot_8(r2) . rot_4(r1)
        rot_8(r2)        =  YXYXYXYxYYYYYXXyx
        rot_4(r1)        =  XYxxYYXX
        concatenate      =  YXYXYXYxYYYYYXXyxXYxxYYXX
        cancel inverses  =  YXYXYXYxYYYYYYYXX
        rotate by 9      =  YYYYYYYXXYXYXYXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXYxx, YYYYYYYXXYXYXYXYx)
    both meet at (YYXXXYxx, YYYYYYYXXYXYXYXYx)
```

---

## Class 095

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 214 | 25_2 | `YXXYxxYx` | `YYYYYYYYXyyyyyyyx` |
| 252 | 25_30 | `YXYXXYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**214 (25_2)  ≡  252 (25_30)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_2** (`YXXYxxYx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXXYxxYx
       substitute      ->  yXXyxxyx
       invert          ->  XYXXYxxY
       rotate by 1     ->  YXYXXYxx
                           = r1 of 25_30   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_30   [MATCH]
```

which is exactly **25_30** = (`YXYXXYxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 096

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 215 | 25_3 | `YXXYxYxx` | `YYYYYYYYXyyyyyyyx` |
| 254 | 25_32 | `YXYxxYXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**215 (25_3)  ≡  254 (25_32)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_3** (`YXXYxYxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXXYxYxx
       substitute      ->  yXXyxyxx
       invert          ->  XXYXYxxY
       rotate by 6     ->  YXYxxYXX
                           = r1 of 25_32   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_32   [MATCH]
```

which is exactly **25_32** = (`YXYxxYXX`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 097

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 216 | 25_4 | `YXyxxyXX` | `YYYYYYYYXyyyyyyyx` |
| 242 | 25_20 | `YXXyXYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**216 (25_4)  ≡  242 (25_20)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_4** (`YXyxxyXX`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXyxxyXX
       substitute      ->  yXYxxYXX
       rotate by 3     ->  YXXyXYxx
                           = r1 of 25_20   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_20   [MATCH]
```

which is exactly **25_20** = (`YXXyXYxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 098

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 217 | 25_5 | `YXXYxxyx` | `YYYYYYYYXyyyyyyyx` |
| 240 | 25_18 | `YXyXXYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**217 (25_5)  ≡  240 (25_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_5** (`YXXYxxyx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXXYxxyx
       substitute      ->  yXXyxxYx
       invert          ->  XyXXYxxY
       rotate by 1     ->  YXyXXYxx
                           = r1 of 25_18   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_18   [MATCH]
```

which is exactly **25_18** = (`YXyXXYxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 099

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 218 | 25_6 | `YXyXXyxx` | `YYYYYYYYXyyyyyyyx` |
| 251 | 25_29 | `YXXYxxyX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**218 (25_6)  ≡  251 (25_29)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_6** (`YXyXXyxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXyXXyxx
       substitute      ->  yXYXXYxx
       rotate by 6     ->  YXXYxxyX
                           = r1 of 25_29   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_29   [MATCH]
```

which is exactly **25_29** = (`YXXYxxyX`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 100

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 219 | 25_7 | `YXXyXyxx` | `YYYYYYYYXyyyyyyyx` |
| 253 | 25_31 | `YXYxxyXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**219 (25_7)  ≡  253 (25_31)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_7** (`YXXyXyxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXXyXyxx
       substitute      ->  yXXYXYxx
       rotate by 5     ->  YXYxxyXX
                           = r1 of 25_31   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_31   [MATCH]
```

which is exactly **25_31** = (`YXYxxyXX`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 101

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 220 | 25_8 | `YXyxxYXX` | `YYYYYYYYXyyyyyyyx` |
| 241 | 25_19 | `YXXyxYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**220 (25_8)  ≡  241 (25_19)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_8** (`YXyxxYXX`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXyxxYXX
       substitute      ->  yXYxxyXX
       invert          ->  xxYXXyxY
       rotate by 6     ->  YXXyxYxx
                           = r1 of 25_19   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_19   [MATCH]
```

which is exactly **25_19** = (`YXXyxYxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 102

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 221 | 25_9 | `YXYXXyxx` | `YYYYYYYYXyyyyyyyx` |
| 239 | 25_17 | `YXXyxxYx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**221 (25_9)  ≡  239 (25_17)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_9** (`YXYXXyxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXYXXyxx
       substitute      ->  yXyXXYxx
       invert          ->  XXyxxYxY
       rotate by 1     ->  YXXyxxYx
                           = r1 of 25_17   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_17   [MATCH]
```

which is exactly **25_17** = (`YXXyxxYx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 103

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 222 | 25_10 | `YYXXXyxx` | `YYYYYYYXXyXyXyXyx` |
| 243 | 25_21 | `YYXXyxxx` | `YYYXyxyxyxyXYXYxx` |

### Why they are the same problem — 1 edge

**243 (25_21)  ≡  222 (25_10)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 25_21
    start: (YYXXyxxx, YYYXyxyxyxyXYXYxx)
    change of variables: x -> X, y -> xY
      r1 = YYXXyxxx
           substitute      ->  yXyxxYXXX
           rotate by 4     ->  YXXXyXyxx
                               = r1
      r2 = YYYXyxyxyxyXYXYxx
           substitute      ->  yXyXyxYYYYxyyXXX
           rotate by 10    ->  YYYYxyyXXXyXyXyx
                               = r2
    => (YXXXyXyxx, YYYYxyyXXXyXyXyx)

    AC move:  r2 <- rot_7(r2) . rot_2(r1)
        rot_7(r2)        =  XyXyXyxYYYYxyyXX
        rot_2(r1)        =  xxYXXXyXy
        concatenate      =  XyXyXyxYYYYxyyXXxxYXXXyXy
        cancel inverses  =  XyXyXyxYYYYxyXXXyXy
        rotate by 12     =  YYYYxyXXXyXyXyXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXyXyxx, YYYYxyXXXyXyXyXyXyx)
    change of variables: x -> X, y -> yX
      r1 = YXXXyXyxx
           substitute      ->  xYxxxyyXXX
           reduce          ->  YxxxyyXX
           invert          ->  xxYYXXXy
           rotate by 6     ->  YYXXXyxx
                               = r1
      r2 = YYYYxyXXXyXyXyXyXyx
           substitute      ->  xYxYxYxYXyxxyyyyyXX
           reduce          ->  YxYxYxYXyxxyyyyyX
           invert          ->  xYYYYYXXYxyXyXyXy
           rotate by 16    ->  YYYYYXXYxyXyXyXyx
                               = r2
    => (YYXXXyxx, YYYYYXXYxyXyXyXyx)
  right — 25_10
    start: (YYXXXyxx, YYYYYYYXXyXyXyXyx)
    => (YYXXXyxx, YYYYYYYXXyXyXyXyx)   [already Aut-minimal]

    AC move:  r2 <- rot_8(r2) . rot_4(r1^-1)
        rot_8(r2)        =  yXyXyXyxYYYYYYYXX
        rot_4(r1^-1)     =  xxyyXXYx
        concatenate      =  yXyXyXyxYYYYYYYXXxxyyXXYx
        cancel inverses  =  yXyXyXyxYYYYYXXYx
        rotate by 9      =  YYYYYXXYxyXyXyXyx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXyxx, YYYYYXXYxyXyXyXyx)
    both meet at (YYXXXyxx, YYYYYXXYxyXyXyXyx)
```

---

## Class 104

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 223 | 25_11 | `YXYXYxxx` | `YYYYYYYYXyyyyyyyx` |
| 248 | 25_26 | `YXXXYxYx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**223 (25_11)  ≡  248 (25_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_11** (`YXYXYxxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXYXYxxx
       substitute      ->  yXyXyxxx
       invert          ->  XXXYxYxY
       rotate by 1     ->  YXXXYxYx
                           = r1 of 25_26   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_26   [MATCH]
```

which is exactly **25_26** = (`YXXXYxYx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 105

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 224 | 25_12 | `YXYxxxyX` | `YYYYYYYYXyyyyyyyx` |
| 247 | 25_25 | `YXyXyxxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**224 (25_12)  ≡  247 (25_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_12** (`YXYxxxyX`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXYxxxyX
       substitute      ->  yXyxxxYX
       rotate by 2     ->  YXyXyxxx
                           = r1 of 25_25   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_25   [MATCH]
```

which is exactly **25_25** = (`YXyXyxxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 106

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 226 | 25_13 | `YXyXYxxx` | `YYYYYYYYXyyyyyyyx` |
| 246 | 25_24 | `YXyxxxyX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**226 (25_13)  ≡  246 (25_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_13** (`YXyXYxxx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXyXYxxx
       substitute      ->  yXYXyxxx
       rotate by 6     ->  YXyxxxyX
                           = r1 of 25_24   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_24   [MATCH]
```

which is exactly **25_24** = (`YXyxxxyX`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 107

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 227 | 25_14 | `YXXXyxYx` | `YYYYYYYYXyyyyyyyx` |
| 245 | 25_23 | `YXYXyxxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**227 (25_14)  ≡  245 (25_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_14** (`YXXXyxYx`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YXXXyxYx
       substitute      ->  yXXXYxyx
       invert          ->  XYXyxxxY
       rotate by 1     ->  YXYXyxxx
                           = r1 of 25_23   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_23   [MATCH]
```

which is exactly **25_23** = (`YXYXyxxx`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 108

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 228 | 25_15 | `YYxxxYXX` | `YYYYYYYYXyyyyyyyx` |
| 250 | 25_28 | `YYxxYXXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**228 (25_15)  ≡  250 (25_28)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_15** (`YYxxxYXX`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YYxxxYXX
       substitute      ->  yyxxxyXX
       invert          ->  xxYXXXYY
       rotate by 2     ->  YYxxYXXX
                           = r1 of 25_28   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_28   [MATCH]
```

which is exactly **25_28** = (`YYxxYXXX`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 109

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 229 | 25_16 | `YYxxxyXX` | `YYYYYYYYXyyyyyyyx` |
| 249 | 25_27 | `YYxxyXXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**229 (25_16)  ≡  249 (25_27)** — *change of variables only*

Substitute `x -> x, y -> Y` into **25_16** (`YYxxxyXX`, `YYYYYYYYXyyyyyyyx`), then normalise:

```
  r1 = YYxxxyXX
       substitute      ->  yyxxxYXX
       invert          ->  xxyXXXYY
       rotate by 2     ->  YYxxyXXX
                           = r1 of 25_27   [MATCH]
  r2 = YYYYYYYYXyyyyyyyx
       substitute      ->  yyyyyyyyXYYYYYYYx
       invert          ->  XyyyyyyyxYYYYYYYY
       rotate by 8     ->  YYYYYYYYXyyyyyyyx
                           = r2 of 25_27   [MATCH]
```

which is exactly **25_27** = (`YYxxyXXX`, `YYYYYYYYXyyyyyyyx`). No AC move was used.

---

## Class 110

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 230 | 21_39 | `YYYXXyyxx` | `YYYYYXyyXyyx` |
| 256 | 21_41 | `YYYXXyyxx` | `YYYYYXyyxyyx` |

### Why they are the same problem — 1 edge

**230 (21_39)  ≡  256 (21_41)** — *change of variables only*

Substitute `x -> x, y -> Y` into **21_39** (`YYYXXyyxx`, `YYYYYXyyXyyx`), then normalise:

```
  r1 = YYYXXyyxx
       substitute      ->  yyyXXYYxx
       invert          ->  XXyyxxYYY
       rotate by 3     ->  YYYXXyyxx
                           = r1 of 21_41   [MATCH]
  r2 = YYYYYXyyXyyx
       substitute      ->  yyyyyXYYXYYx
       invert          ->  XyyxyyxYYYYY
       rotate by 5     ->  YYYYYXyyxyyx
                           = r2 of 21_41   [MATCH]
```

which is exactly **21_41** = (`YYYXXyyxx`, `YYYYYXyyxyyx`). No AC move was used.

---

## Class 111

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 232 | 19_44 | `YYYXXyyx` | `YYYxyyXXYXX` |
| 255 | 19_49 | `YYYXyyxx` | `YYYxxYxxyyX` |

### Why they are the same problem — 1 edge

**232 (19_44)  ≡  255 (19_49)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_44** (`YYYXXyyx`, `YYYxyyXXYXX`), then normalise:

```
  r1 = YYYXXyyx
       substitute      ->  yyyXXYYx
       invert          ->  XyyxxYYY
       rotate by 3     ->  YYYXyyxx
                           = r1 of 19_49   [MATCH]
  r2 = YYYxyyXXYXX
       substitute      ->  yyyxYYXXyXX
       invert          ->  xxYxxyyXYYY
       rotate by 3     ->  YYYxxYxxyyX
                           = r2 of 19_49   [MATCH]
```

which is exactly **19_49** = (`YYYXyyxx`, `YYYxxYxxyyX`). No AC move was used.

---

## Class 112

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 233 | 21_40 | `YYYYxyyXyX` | `YYXYXyXYxyx` |
| 258 | 21_42 | `YYYYxxyyX` | `YYYYXYxxYYxx` |

### Why they are the same problem — 1 edge

**233 (21_40)  ≡  258 (21_42)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 21_40
    start: (YYYYxyyXyX, YYXYXyXYxyx)
    change of variables: x -> y, y -> x
      r1 = YYYYxyyXyX
           substitute      ->  XXXXyxxYxY
           rotate by 1     ->  YXXXXyxxYx
                               = r1
      r2 = YYXYXyXYxyx
           substitute      ->  XXYXYxYXyxy
           rotate by 9     ->  YXYxYXyxyXX
                               = r2
    => (YXXXXyxxYx, YXYxYXyxyXX)

    AC move:  r2 <- rot_0(r2) . rot_4(r1)
        rot_0(r2)        =  YXYxYXyxyXX
        rot_4(r1)        =  xxYxYXXXXy
        concatenate      =  YXYxYXyxyXXxxYxYXXXXy
        cancel inverses  =  YXYxYXyxxYXXXXy
        reduce cyclically=  XYxYXyxxYXXXX
        rotate by 10     =  YXyxxYXXXXXYx
                            ^ the new r2
        r1 is untouched by the move
    => (YXXXXyxxYx, YXyxxYXXXXXYx)
    change of variables: x -> x, y -> yx
      r1 = YXXXXyxxYx
           substitute      ->  XYXXXXyxxYx
           reduce          ->  YXXXXyxxY
           rotate by 1     ->  YYXXXXyxx
                               = r1
      r2 = YXyxxYXXXXXYx
           substitute      ->  XYXyxxYXXXXXXYx
           reduce          ->  YXyxxYXXXXXXY
           rotate by 1     ->  YYXyxxYXXXXXX
                               = r2
    => (YYXXXXyxx, YYXyxxYXXXXXX)

    AC move:  r2 <- rot_6(r2) . rot_1(r1^-1)
        rot_6(r2)        =  XXXXXXYYXyxxY
        rot_1(r1^-1)     =  yXXYxxxxy
        concatenate      =  XXXXXXYYXyxxYyXXYxxxxy
        cancel inverses  =  XXXXXXYYxxxy
        rotate by 6      =  YYxxxyXXXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyxx, YYxxxyXXXXXX)
  right — 21_42
    start: (YYYYxxyyX, YYYYXYxxYYxx)
    change of variables: x -> y, y -> X
      r1 = YYYYxxyyX
           substitute      ->  xxxxyyXXY
           invert          ->  yxxYYXXXX
           rotate by 6     ->  YYXXXXyxx
                               = r1
      r2 = YYYYXYxxYYxx
           substitute      ->  xxxxYxyyxxyy
           invert          ->  YYXXYYXyXXXX
           rotate by 8     ->  YYXyXXXXYYXX
                               = r2
    => (YYXXXXyxx, YYXyXXXXYYXX)

    AC move:  r2 <- rot_0(r2) . rot_4(r1^-1)
        rot_0(r2)        =  YYXyXXXXYYXX
        rot_4(r1^-1)     =  xxyyXXYxx
        concatenate      =  YYXyXXXXYYXXxxyyXXYxx
        cancel inverses  =  YYXyXXXXXXYxx
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyxx, YYXyXXXXXXYxx)

    AC move:  r2 <- rot_0(r2) . rot_0(r1^-1)
        rot_0(r2)        =  YYXyXXXXXXYxx
        rot_0(r1^-1)     =  XXYxxxxyy
        concatenate      =  YYXyXXXXXXYxxXXYxxxxyy
        cancel inverses  =  YYXyXXXXXXYYxxxxyy
        reduce cyclically=  yXXXXXXYYxxx
        rotate by 5      =  YYxxxyXXXXXX
                            ^ the new r2
        r1 is untouched by the move
    => (YYXXXXyxx, YYxxxyXXXXXX)
    both meet at (YYXXXXyxx, YYxxxyXXXXXX)
```

---

## Class 113

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 234 | 19_45 | `YYYxxyyX` | `YYYYXyxxYxx` |
| 257 | 19_50 | `YYYxyyXX` | `YYYYXXYXXyx` |

### Why they are the same problem — 1 edge

**234 (19_45)  ≡  257 (19_50)** — *change of variables only*

Substitute `x -> x, y -> Y` into **19_45** (`YYYxxyyX`, `YYYYXyxxYxx`), then normalise:

```
  r1 = YYYxxyyX
       substitute      ->  yyyxxYYX
       invert          ->  xyyXXYYY
       rotate by 3     ->  YYYxyyXX
                           = r1 of 19_50   [MATCH]
  r2 = YYYYXyxxYxx
       substitute      ->  yyyyXYxxyxx
       invert          ->  XXYXXyxYYYY
       rotate by 4     ->  YYYYXXYXXyx
                           = r2 of 19_50   [MATCH]
```

which is exactly **19_50** = (`YYYxyyXX`, `YYYYXXYXXyx`). No AC move was used.

---

## Class 114

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 0 | 13_1 | `YXyXYx` | `YYYXXXX` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 115

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 1 | 15_1 | `YYXyXyx` | `YYxxxxyX` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 116

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 2 | 16_1 | `YYXyXyx` | `YYxxxxxyX` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 117

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 5 | 14_1 | `YYYXyyx` | `YXXYxxx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 118

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 6 | 14_2 | `YYYxyyX` | `YXXyxxx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 119

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 15 | 16_2 | `YYYXyyX` | `YXXXXyxxx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 120

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 16 | 16_3 | `YYYXyyx` | `YXXXXyxxx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 121

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 48 | 18_2 | `YXXXyxx` | `YYYYYXyyyyx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 122

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 87 | 20_2 | `YXXyxxx` | `YYYYYYxyyyyyX` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 123

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 93 | 21_3 | `YXXYxYxx` | `YYYYYYXyyyyyx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 124

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 97 | 21_7 | `YXyXXYxxx` | `YYYYYYxxxyXX` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 125

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 121 | 21_28 | `YXYxxyXX` | `YYYYYYXyyyyyx` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

## Class 126

**1 presentation**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 122 | 21_29 | `YXyXXyxxx` | `YYYYYYxxYXXX` |

No other presentation of the 261 is known to be equivalent to it: neither a change of variables nor any AC move the sweep reached connects it to another class.

---

