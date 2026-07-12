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

### `cv` — change of variables only

A single substitution `psi` in `Aut(F₂)` with `canon(psi(A)) == canon(B)`. **B is A with new words substituted for the generators**, full stop — no AC move is involved. Check it by hand: substitute and compare canonical forms.

### `ac` — AC moves were needed

Both presentations are driven by Definition 2.1 moves

```
r_i  <-  rot_k1(r_i) . rot_k2(r_j^±1)          (the move inverts the OTHER relator)
```

to a common `Aut(F₂)`-class. This proves **A and B are the same problem** — A is AC-trivial ⟺ B is. It does **not** exhibit an AC path from A to B, because a change of variables is applied between the moves.

On **6 of the 42** the change of variables at every step is the identity, so the path is Definition 2.1 moves and nothing else. Those are flagged `pure AC path` and do give an AC path — from `A` to `psi(B)`, where `psi` is the relabelling that carried the two roots to their `Aut`-minimal forms. **Not** from A to B; no edge here proves that.

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

Substitute `x -> X, y -> y` into `22_13`:

```
    (YXYxx, YYYYYYYYxyyyyyyyX)
      ==>  (YXXYx, YYYYYYYYXyyyyyyyx)   = the canonical form of 22_14   [MATCH]
```

**179 (22_13)  ≡  182 (23_21)** — *change of variables only*

Substitute `x -> xY, y -> y` into `22_13`:

```
    (YXYxx, YYYYYYYYxyyyyyyyX)
      ==>  (YXYxYx, YYYYYYYYxyyyyyyyX)   = the canonical form of 23_21   [MATCH]
```

**4 (21_1)  ≡  186 (21_36)** — *change of variables only*

Substitute `x -> Y, y -> x` into `21_1`:

```
    (YXYxyx, YYYYYYYYxxxxxxx)
      ==>  (YXyXYx, YYYYYYYXXXXXXXX)   = the canonical form of 21_36   [MATCH]
```

**179 (22_13)  ≡  191 (23_24)** — *change of variables only*

Substitute `x -> XY, y -> y` into `22_13`:

```
    (YXYxx, YYYYYYYYxyyyyyyyX)
      ==>  (YXYXYx, YYYYYYYYXyyyyyyyx)   = the canonical form of 23_24   [MATCH]
```

**196 (18_6)  ≡  179 (22_13)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 18_6
    P                                  = (YXYXyxx, YYYYYYxyXyx)
    x -> x, y -> Y                     = (YXXyxYx, YYYYYYXyxyX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYYYYYXyxyX, YYYYYYYXyXyx)   [AC move]
    x -> yyyyyyx, y -> Y               = (YXXYx, YYYYYYYXYxyyyyyyyX)   [change of variables]
  right — 22_13
    P                                  = (YXYxx, YYYYYYYYxyyyyyyyX)
    x -> X, y -> y                     = (YXXYx, YYYYYYYYXyyyyyyyx)   [to the Aut-minimal form]
    r2 <- rot_8(r2) . rot_2(r1^-1)     = (YXXYx, YYYYYYYXYxyyyyyyyX)   [AC move]
    both meet at (YXXYx, YYYYYYYXYxyyyyyyyX)
```

**196 (18_6)  ≡  197 (18_7)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 18_6
    P                                  = (YXYXyxx, YYYYYYxyXyx)
    x -> x, y -> Y                     = (YXXyxYx, YYYYYYXyxyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YXXyxYx, YYYYYYYXyXyx)   [AC move]
    x -> xY, y -> Y                    = (YXXyxYx, YYYYYYYXyxx)   [change of variables]
  right — 18_7
    P                                  = (YXYXyxx, YYYYYYYXXyx)
    x -> x, y -> Y                     = (YXXyxYx, YYYYYYYXyxx)   [to the Aut-minimal form]
    both meet at (YXXyxYx, YYYYYYYXyxx)
```

**4 (21_1)  ≡  196 (18_6)** — *AC moves + change of variables*, 6 + 1 AC moves

```
  left  — 21_1
    P                                  = (YXYxyx, YYYYYYYYxxxxxxx)
    x -> x, y -> y                     = (YXYxyx, YYYYYYYYxxxxxxx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXYxyx, YYYYYYYxxxxxxYXyx)   [AC move]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXYxyx, YYYYYYxxxxxxYXXyx)   [AC move]
    r2 <- rot_3(r2) . rot_2(r1^-1)     = (YXYxyx, YYYYYYxxxxxYXyXyx)   [AC move]
    r2 <- rot_4(r2) . rot_2(r1^-1)     = (YXYxyx, YYYYYYxxxxYXyyXyx)   [AC move]
    r2 <- rot_5(r2) . rot_2(r1^-1)     = (YXYxyx, YYYYYYxxxYXyyyXyx)   [AC move]
    r2 <- rot_6(r2) . rot_2(r1^-1)     = (YXYxyx, YYYYYYxxYXyyyyXyx)   [AC move]
  right — 18_6
    P                                  = (YXYXyxx, YYYYYYxyXyx)
    x -> x, y -> Y                     = (YXXyxYx, YYYYYYXyxyX)   [to the Aut-minimal form]
    r1 <- rot_5(r1) . rot_7(r2^-1)     = (YYYYYYXyxyX, YYYYYXyXYxyxyX)   [AC move]
    x -> YYYYYx, y -> y                = (YXYxyx, YYYYYYxxYXyyyyXyx)   [change of variables]
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

Substitute `x -> x, y -> Y` into `15_12`:

```
    (YYXyyxx, YXXXyxYx)
      ==>  (YYXXyyx, YXYXyxxx)   = the canonical form of 15_13   [MATCH]
```

**195 (15_12)  ≡  225 (15_14)** — *change of variables only*

Substitute `x -> y, y -> x` into `15_12`:

```
    (YYXyyxx, YXXXyxYx)
      ==>  (YYXXyxx, YYYxyXyX)   = the canonical form of 15_14   [MATCH]
```

**195 (15_12)  ≡  237 (15_15)** — *change of variables only*

Substitute `x -> Y, y -> x` into `15_12`:

```
    (YYXyyxx, YXXXyxYx)
      ==>  (YYXXyxx, YYYxyxyX)   = the canonical form of 15_15   [MATCH]
```

**181 (21_34)  ≡  188 (21_37)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 21_34
    P                                  = (YYXYxx, YYYYYYxYxYxYXyx)
    x -> Yx, y -> x                    = (YXXyXYx, YYYXyxYXXXXX)   [to the Aut-minimal form]
    r2 <- rot_3(r2) . rot_3(r1^-1)     = (YXXyXYx, YYYXyyxYXXX)   [AC move]
    r2 <- rot_0(r2) . rot_2(r1^-1)     = (YXXyXYx, YYYXyyxYXXyXyxYx)   [AC move]
    x -> xy, y -> y                    = (YXYXXYx, YYYXyyxYXYXXyxx)   [change of variables]
  right — 21_37
    P                                  = (YYXXYx, YYxYxyxyXYXYXYX)
    x -> xY, y -> X                    = (YXXyXYx, YYYYxyyXXyXX)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_5(r1^-1)     = (YXXyXYx, YYYYxyyyXyX)   [AC move]
    x -> xy, y -> y                    = (YXYXXYx, YYYYxyyyXX)   [change of variables]
    r2 <- rot_8(r2) . rot_6(r1^-1)     = (YXYXXYx, YYYXyyxYXYXXyxx)   [AC move]
    both meet at (YXYXXYx, YYYXyyxYXYXXyxx)
```

**188 (21_37)  ≡  195 (15_12)** — *AC moves + change of variables*, 3 + 1 AC moves

```
  left  — 21_37
    P                                  = (YYXXYx, YYxYxyxyXYXYXYX)
    x -> xY, y -> X                    = (YXXyXYx, YYYYxyyXXyXX)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_5(r1^-1)     = (YXXyXYx, YYYYxyyyXyX)   [AC move]
    x -> xy, y -> y                    = (YXYXXYx, YYYYxyyyXX)   [change of variables]
    r2 <- rot_0(r2) . rot_5(r1^-1)     = (YXYXXYx, YYYYXyyyxYX)   [AC move]
    x -> Yx, y -> y                    = (YXXyXYx, YYYXyyyxYX)   [change of variables]
    r1 <- rot_3(r1) . rot_5(r2^-1)     = (YYYXyyyxYX, YYYxyXyxyyxYX)   [AC move]
    x -> xxy, y -> X                   = (YXXXyxYx, YYxyxYXXXyX)   [change of variables]
  right — 15_12
    P                                  = (YYXyyxx, YXXXyxYx)
    x -> y, y -> x                     = (YYXXyxx, YYYxyXyX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_3(r2)        = (YYYxyXyX, YYYxYXXyxyX)   [AC move]
    x -> y, y -> x                     = (YXXXyxYx, YYxyxYXXXyX)   [change of variables]
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

Substitute `x -> xy, y -> y` into `19_37`:

```
    (YYXXyx, YXyXyXyxxYxYx)
      ==>  (YYXYXyx, YXYxxxyXXX)   = the canonical form of 17_41   [MATCH]
```

**183 (19_37)  ≡  203 (17_42)** — *change of variables only*

Substitute `x -> xY, y -> Y` into `19_37`:

```
    (YYXXyx, YXyXyXyxxYxYx)
      ==>  (YYXyxYx, YXXXyXyxxx)   = the canonical form of 17_42   [MATCH]
```

**187 (19_38)  ≡  212 (20_12)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 19_38
    P                                  = (YYXyxx, YXYXYxYxxxxxx)
    x -> x, y -> Y                     = (YYXXyx, YXYxYxYXXXXXX)   [to the Aut-minimal form]
    r2 <- rot_9(r2) . rot_3(r1)        = (YYXXyx, YYYXYxYXXXXXX)   [AC move]
    r2 <- rot_1(r2) . rot_4(r1^-1)     = (YYXXyx, YYYXYxYXXXyyXYX)   [AC move]
  right — 20_12
    P                                  = (YYXyxyx, YYYXXyyXyxYXX)
    x -> Y, y -> x                     = (YXXyxYx, YYxyXYXXYYxxx)   [to the Aut-minimal form]
    r2 <- rot_10(r2) . rot_5(r1)       = (YXXyxYx, YYxxxYxYxYXyXYXX)   [AC move]
    x -> Y, y -> XY                    = (YYXXyx, YYYXYxYXXXyyXYX)   [change of variables]
    both meet at (YYXXyx, YYYXYxYXXXyyXYX)
```

**183 (19_37)  ≡  187 (19_38)** — *AC moves + change of variables*, 2 + 2 AC moves

```
  left  — 19_37
    P                                  = (YYXXyx, YXyXyXyxxYxYx)
    x -> X, y -> yX                    = (YXXyXyx, YYYXyyyxx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXyXyx, YYYxyyXXyXyX)   [AC move]
    x -> Xy, y -> y                    = (YXXyXyx, YYYXyyxYxxx)   [change of variables]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXyXyx, YYXyyxYxxYxYxx)   [AC move]
    x -> y, y -> Xy                    = (YYXXyx, YXYxYxyXyXYXX)   [change of variables]
  right — 19_38
    P                                  = (YYXyxx, YXYXYxYxxxxxx)
    x -> x, y -> Y                     = (YYXXyx, YXYxYxYXXXXXX)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_4(r1^-1)     = (YYXXyx, YXYxYxyXYXXXX)   [AC move]
    x -> x, y -> Xy                    = (YXXyxYx, YYxxYxyXYXXX)   [change of variables]
    r2 <- rot_1(r2) . rot_3(r1^-1)     = (YXXyxYx, YYxxYxyXXyXYX)   [AC move]
    x -> x, y -> yx                    = (YYXXyx, YXYxYxyXyXYXX)   [change of variables]
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

Substitute `x -> x, y -> Y` into `20_8`:

```
    (YXYxx, YYYYYYYXyyyyyyx)
      ==>  (YXXYx, YYYYYYYXyyyyyyx)   = the canonical form of 20_9   [MATCH]
```

**3 (17_1)  ≡  129 (17_35)** — *AC moves + change of variables*, 1 + 0 AC moves

```
  left  — 17_1
    P                                  = (YXYXyxx, YYYYYxyXyX)
    x -> x, y -> Y                     = (YXXyxYx, YYYYYxyxyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YXXyxYx, YYYYYYxyXyx)   [AC move]
    x -> xY, y -> Y                    = (YXXyxYx, YYYYYXyxyX)   [change of variables]
  right — 17_35
    P                                  = (YYXyxyx, YXyXYxxxxx)
    x -> Y, y -> x                     = (YXXyxYx, YYYYYXyxyX)   [to the Aut-minimal form]
    both meet at (YXXyxYx, YYYYYXyxyX)
```

**123 (20_8)  ≡  3 (17_1)** — *AC moves + change of variables*, 1 + 1 AC moves

```
  left  — 20_8
    P                                  = (YXYxx, YYYYYYYXyyyyyyx)
    x -> x, y -> Y                     = (YXXYx, YYYYYYYXyyyyyyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_3(r1)        = (YXXYx, YYYYYYYXyyyyyxYX)   [AC move]
    x -> xxxxxxy, y -> X               = (YXXXXXyxYx, YXyxxxxxxyX)   [change of variables]
  right — 17_1
    P                                  = (YXYXyxx, YYYYYxyXyX)
    x -> x, y -> Y                     = (YXXyxYx, YYYYYxyxyX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYYYYxyxyX, YYYYYYxyXyx)   [AC move]
    x -> y, y -> X                     = (YXXXXXyxYx, YXyxxxxxxyX)   [change of variables]
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

Substitute `x -> x, y -> Y` into `19_43`:

```
    (YYXyyxxYX, YYYYYxyXyX)
      ==>  (YYxYXXyyx, YYYYYxyxyX)   = the canonical form of 19_48   [MATCH]
```

**190 (23_23)  ≡  231 (19_43)** — *pure AC path*, 1 + 0 AC moves

```
  left  — 23_23
    P                                  = (YYxYXX, YYYYYYYYXyyyyyxYX)
    x -> xxxxxxxy, y -> X              = (YXXXXXyxYx, YXXyxxxxxxxyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YYXXyxxyx, YXXXXXyxYx)   [AC move]
  right — 19_43
    P                                  = (YYXyyxxYX, YYYYYxyXyX)
    x -> y, y -> x                     = (YYXXyxxyx, YXXXXXyxYx)   [to the Aut-minimal form]
    both meet at (YYXXyxxyx, YXXXXXyxYx)
```

Every step is an AC move — no change of variables inside the path. So `23_23 ~AC psi(19_43)` with `psi: x -> yyyyyyyx, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `19_43`, not to `19_43` itself.

**184 (23_22)  ≡  190 (23_23)** — *AC moves + change of variables*, 10 + 3 AC moves

```
  left  — 23_22
    P                                  = (YYxxYX, YYYYYxyXyXYXyyyxx)
    x -> X, y -> y                     = (YYXXYx, YYYYYXyxyxYxyyyXX)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_1(r1)        = (YYXXYx, YYYYYXyxyxYxyXXYX)   [AC move]
    x -> xY, y -> X                    = (YXXyXYx, YYxYxyXXyyxYXXXX)   [change of variables]
    r2 <- rot_2(r2) . rot_3(r1^-1)     = (YXXyXYx, YYYxxYXyXyyxxyX)   [AC move]
    r2 <- rot_0(r2) . rot_1(r1)        = (YXXyXYx, YYYYxxYXyXyyyX)   [AC move]
    x -> xy, y -> y                    = (YXYXXYx, YYYYxyxYXXyyX)   [change of variables]
    r2 <- rot_4(r2) . rot_2(r1^-1)     = (YXYXXYx, YYYYxyyxxyXyyX)   [AC move]
    r2 <- rot_2(r2) . rot_2(r1)        = (YXYXXYx, YYYYxyyxYXXyX)   [AC move]
    r2 <- rot_3(r2) . rot_2(r1^-1)     = (YXYXXYx, YYYYxyyyxxyXyX)   [AC move]
    r2 <- rot_1(r2) . rot_2(r1)        = (YXYXXYx, YYYYxyyyxYXXX)   [AC move]
    r2 <- rot_0(r2) . rot_5(r1^-1)     = (YXYXXYx, YYYXyyyxYXYxyX)   [AC move]
    x -> Yx, y -> y                    = (YXXyXYx, YYYxyyxYXyxyX)   [change of variables]
    r2 <- rot_0(r2) . rot_5(r1^-1)     = (YXXyXYx, YYXyyxYXXXYxyX)   [AC move]
    r2 <- rot_7(r2) . rot_4(r1)        = (YXXyXYx, YYXyxYXXXXXYxyX)   [AC move]
  right — 23_23
    P                                  = (YYxYXX, YYYYYYYYXyyyyyxYX)
    x -> xxxxxxxy, y -> X              = (YXXXXXyxYx, YXXyxxxxxxxyX)   [to the Aut-minimal form]
    r1 <- rot_2(r1) . rot_5(r2^-1)     = (YXXyxxxxxxxyX, YXXXyxYXXXXXXYx)   [AC move]
    x -> X, y -> xxxxxxy               = (YXXyXYx, YYXXXXXXXYxxxyX)   [change of variables]
    r2 <- rot_0(r2) . rot_1(r1)        = (YXXyXYx, YYYXXXXXXXYxyX)   [AC move]
    r2 <- rot_9(r2) . rot_3(r1^-1)     = (YXXyXYx, YYXyxYXXXXXYxyX)   [AC move]
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

Substitute `x -> x, y -> Y` into `19_40`:

```
    (YYYxxYX, YXyxxxyXyXyX)
      ==>  (YYYxYXX, YXYXYXyXYxxx)   = the canonical form of 19_42   [MATCH]
```

**236 (19_47)  ≡  259 (19_51)** — *AC moves + change of variables*, 2 + 1 AC moves

```
  left  — 19_47
    P                                  = (YYYYxyxyX, YYxYXXYxyx)
    x -> y, y -> X                     = (YXXXXyxYx, YYxyXyxxyx)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_0(r1)        = (YXXXXyxYx, YYxyXyXXyxYxx)   [AC move]
    x -> x, y -> yx                    = (YYXXXXyx, YYXyxyXyXYx)   [change of variables]
    r2 <- rot_7(r2) . rot_7(r1)        = (YYXXXXyx, YYXXXXXyxYxyXyXYx)   [AC move]
    x -> X, y -> yX                    = (YXXXXyXyx, YYxYxxxxxyXYXyyx)   [change of variables]
  right — 19_51
    P                                  = (YYYYxyXX, YXyxxyXyXYx)
    x -> y, y -> x                     = (YYXXXXyx, YYXyxYxyXyX)   [to the Aut-minimal form]
    r2 <- rot_9(r2) . rot_2(r1)        = (YYXXXXyx, YYXXXXXyxYxyXyXYx)   [AC move]
    x -> X, y -> yX                    = (YXXXXyXyx, YYxYxxxxxyXYXyyx)   [change of variables]
    both meet at (YXXXXyXyx, YYxYxxxxxyXYXyyx)
```

**236 (19_47)  ≡  201 (19_40)** — *AC moves + change of variables*, 2 + 5 AC moves

```
  left  — 19_47
    P                                  = (YYYYxyxyX, YYxYXXYxyx)
    x -> y, y -> X                     = (YXXXXyxYx, YYxyXyxxyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_7(r1^-1)     = (YXXXXyxYx, YXyxYXXXXXXYx)   [AC move]
    x -> x, y -> yx                    = (YYXXXXyx, YYXyxYXXXXXXX)   [change of variables]
    r1 <- rot_5(r1) . rot_3(r2^-1)     = (YYXyxYXXXXXXX, YXXXyxxxxxxxxyX)   [AC move]
    x -> X, y -> xxxxxxxy              = (YXXXyXYx, YYXXXXXXXYxyX)   [change of variables]
  right — 19_40
    P                                  = (YYYxxYX, YXyxxxyXyXyX)
    x -> y, y -> X                     = (YYXXXyX, YYYxyXyxyxyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YYXXXyX, YYxyXyxyxYXXX)   [AC move]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YYXXXyX, YXYxYXXXXyxxyX)   [AC move]
    x -> x, y -> Xy                    = (YXXXyXYx, YYxxYXXXXyxyX)   [change of variables]
    r2 <- rot_5(r2) . rot_4(r1^-1)     = (YXXXyXYx, YYxyxYXyxyX)   [AC move]
    r2 <- rot_0(r2) . rot_6(r1^-1)     = (YXXXyXYx, YXyxYXXXXYxyX)   [AC move]
    x -> X, y -> xxy                   = (YXXXYxxxyx, YXyXYxyXXyx)   [change of variables]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXXYxxxyx, YXyxYXXYxxxxx)   [AC move]
    x -> X, y -> xxy                   = (YXXXyXYx, YYXXXXXXXYxyX)   [change of variables]
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

Substitute `x -> x, y -> Y` into `18_9`:

```
    (YYYxxyX, YXYXyXyxxYx)
      ==>  (YYYxyXX, YXYXXyxyxYx)   = the canonical form of 18_11   [MATCH]
```

**235 (19_46)  ≡  260 (19_52)** — *pure AC path*, 1 + 0 AC moves

```
  left  — 19_46
    P                                  = (YYYYxxYX, YYYxyxYxYXX)
    x -> y, y -> X                     = (YYXXXXyX, YYxxxyXyxyx)   [to the Aut-minimal form]
    r2 <- rot_5(r2) . rot_7(r1)        = (YYXXXXyX, YYXyXYXyxyx)   [AC move]
  right — 19_52
    P                                  = (YYYYxYXX, YXYXyxyXyxx)
    x -> y, y -> x                     = (YYXXXXyX, YYXyXYXyxyx)   [to the Aut-minimal form]
    both meet at (YYXXXXyX, YYXyXYXyxyx)
```

Every step is an AC move — no change of variables inside the path. So `19_46 ~AC psi(19_52)` with `psi: x -> x, y -> Y` (the relabelling to the Aut-minimal forms). This is an AC path to a *relabelled* `19_52`, not to `19_52` itself.

**202 (18_9)  ≡  235 (19_46)** — *AC moves + change of variables*, 3 + 2 AC moves

```
  left  — 18_9
    P                                  = (YYYxxyX, YXYXyXyxxYx)
    x -> y, y -> X                     = (YYXXXyx, YYxyxyXyXYX)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_2(r1)        = (YYXXXyx, YYxyxyXYXXXX)   [AC move]
    x -> x, y -> Xy                    = (YXXXyxYx, YYXyXyxxxyx)   [change of variables]
    r2 <- rot_0(r2) . rot_6(r1^-1)     = (YXXXyxYx, YXyXyxxxxxxyX)   [AC move]
    x -> x, y -> yx                    = (YYXXXyx, YYxyxYXXXXXXX)   [change of variables]
    r2 <- rot_11(r2) . rot_2(r1^-1)    = (YYXXXyx, YXXXXyxxxxxxxxyX)   [AC move]
    x -> X, y -> xxxxxxxy              = (YXXXXyXYx, YXXXyxxxxxxxyx)   [change of variables]
  right — 19_46
    P                                  = (YYYYxxYX, YYYxyxYxYXX)
    x -> y, y -> X                     = (YYXXXXyX, YYxxxyXyxyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YYXXXXyX, YXXXyxxxxyXYx)   [AC move]
    r2 <- rot_1(r2) . rot_1(r1^-1)     = (YYXXXXyX, YXXXyxxxxxxxxyx)   [AC move]
    x -> x, y -> Xy                    = (YXXXXyXYx, YXXXyxxxxxxxyx)   [change of variables]
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
    P                                  = (YYxyxYX, YXyXXyxxx)
    x -> y, y -> X                     = (YXXyXYx, YYYxyyxyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YXXyXYx, YYYYxyyXyX)   [AC move]
    x -> xy, y -> y                    = (YXYXXYx, YYYYxyyXX)   [change of variables]
  right — 16_9
    P                                  = (YYXyXYX, YYXXXXyxx)
    x -> y, y -> x                     = (YXYXXYx, YYYYxyyXX)   [to the Aut-minimal form]
    both meet at (YXYXXYx, YYYYxyyXX)
```

**161 (16_10)  ≡  127 (16_6)** — *AC moves + change of variables*, 5 + 4 AC moves

```
  left  — 16_10
    P                                  = (YYxxyXX, YYYYXYxYx)
    x -> X, y -> y                     = (YYXXyxx, YYYYxYXYX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_5(r2^-1)     = (YYYYxYXYX, YYYYXYxxyXYX)   [AC move]
    x -> Xy, y -> x                    = (YYXXXXyX, YYXXXYXyXyx)   [change of variables]
    r2 <- rot_0(r2) . rot_1(r1)        = (YYXXXXyX, YXyXYXXXXYXXX)   [AC move]
    x -> y, y -> YYYx                  = (YXYXXYx, YYYYxYXyyyX)   [change of variables]
    r2 <- rot_4(r2) . rot_2(r1^-1)     = (YXYXXYx, YYYYXXyyyx)   [AC move]
    r2 <- rot_0(r2) . rot_3(r1)        = (YXYXXYx, YYYYXXyyxYXYX)   [AC move]
    x -> Yx, y -> y                    = (YXXyXYx, YYYXyXyyxYXX)   [change of variables]
    r2 <- rot_2(r2) . rot_4(r1)        = (YXXyXYx, YYYXyXyxYXXXX)   [AC move]
  right — 16_6
    P                                  = (YYxyxYX, YXyXXyxxx)
    x -> y, y -> X                     = (YXXyXYx, YYYxyyxyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_5(r1^-1)     = (YXXyXYx, YYXyyxYXXX)   [AC move]
    r2 <- rot_3(r2) . rot_4(r1)        = (YXXyXYx, YYXyxYXXXXX)   [AC move]
    r2 <- rot_5(r2) . rot_4(r1)        = (YXXyXYx, YYYXXXXXXX)   [AC move]
    r2 <- rot_4(r2) . rot_3(r1^-1)     = (YXXyXYx, YYYXyXyxYXXXX)   [AC move]
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
    P                                  = (YXXXyxx, YYYXXyyX)
    x -> x, y -> y                     = (YXXXyxx, YYYXXyyX)   [to the Aut-minimal form]
    r2 <- rot_3(r2) . rot_3(r1^-1)     = (YXXXyxx, YYXyxxyyx)   [AC move]
    r2 <- rot_0(r2) . rot_6(r1^-1)     = (YXXXyxx, YYXyxxyxxxyX)   [AC move]
    x -> X, y -> xxy                   = (YXXXyxx, YYXyxxyXYx)   [change of variables]
    r2 <- rot_8(r2) . rot_3(r1)        = (YXXXyxx, YXXYxxxxyXXyXyx)   [AC move]
    x -> X, y -> yX                    = (YXXXyxx, YYXYxxxxyXXXyx)   [change of variables]
  right — 15_6
    P                                  = (YXXyxxx, YYYXyXyX)
    x -> X, y -> Y                     = (YXXXyxx, YYYXyXyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_2(r1)        = (YXXXyxx, YYXyXyxYXXX)   [AC move]
    r2 <- rot_4(r2) . rot_6(r1^-1)     = (YXXXyxx, YYXyxxyXYXXX)   [AC move]
    x -> X, y -> xxy                   = (YXXXyxx, YYXyxxyXyX)   [change of variables]
    r2 <- rot_4(r2) . rot_0(r1^-1)     = (YXXXyxx, YYXXyyxYx)   [AC move]
    r2 <- rot_4(r2) . rot_5(r1^-1)     = (YXXXyxx, YYxyXXyxYx)   [AC move]
    x -> x, y -> yx                    = (YXXXyxx, YYXYxyXyx)   [change of variables]
    r2 <- rot_3(r2) . rot_5(r1^-1)     = (YXXXyxx, YYXYxxxxyXXXyx)   [AC move]
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
    P                                  = (YYYXyyx, YXXYxxYx)
    x -> Y, y -> x                     = (YXXXyxx, YYXYXyyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_2(r1)        = (YXXXyxx, YYxyxyxxxyX)   [AC move]
    x -> x, y -> Xy                    = (YXXXyxx, YYXyXyxYXX)   [change of variables]
    r2 <- rot_3(r2) . rot_6(r1^-1)     = (YXXXyxx, YYXyxxyXYXX)   [AC move]
    x -> X, y -> xxy                   = (YXXXyxx, YYXyxxyyX)   [change of variables]
  right — 15_9
    P                                  = (YXXXyxx, YYYxxyyX)
    x -> X, y -> y                     = (YXXXyxx, YYYXXyyx)   [to the Aut-minimal form]
    r2 <- rot_3(r2) . rot_3(r1^-1)     = (YXXXyxx, YYXyxxyyX)   [AC move]
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

Substitute `x -> x, y -> Y` into `15_4`:

```
    (YYYXyyx, YXyXyxxx)
      ==>  (YYYXyyx, YXYxxxyX)   = the canonical form of 15_7   [MATCH]
```

---

## Class 012

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 10 | 15_5 | `YYYXyyx` | `YXyXXyxx` |
| 13 | 15_8 | `YYYXyyx` | `YXXYxxyX` |

### Why they are the same problem — 1 edge

**10 (15_5)  ≡  13 (15_8)** — *change of variables only*

Substitute `x -> x, y -> Y` into `15_5`:

```
    (YYYXyyx, YXyXXyxx)
      ==>  (YYYXyyx, YXXYxxyX)   = the canonical form of 15_8   [MATCH]
```

---

## Class 013

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 17 | 17_2 | `YYXXYxxx` | `YYYXYxYxx` |
| 36 | 17_21 | `YYXXXYxx` | `YYYXXYXYx` |

### Why they are the same problem — 1 edge

**17 (17_2)  ≡  36 (17_21)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_2`:

```
    (YYXXYxxx, YYYXYxYxx)
      ==>  (YYXXXYxx, YYYXXYXYx)   = the canonical form of 17_21   [MATCH]
```

---

## Class 014

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 18 | 17_3 | `YXXYxxYx` | `YYYYXyyyx` |
| 42 | 17_27 | `YXYXXYxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**18 (17_3)  ≡  42 (17_27)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_3`:

```
    (YXXYxxYx, YYYYXyyyx)
      ==>  (YXYXXYxx, YYYYXyyyx)   = the canonical form of 17_27   [MATCH]
```

---

## Class 015

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 19 | 17_4 | `YXXYxYxx` | `YYYYXyyyx` |
| 44 | 17_29 | `YXYxxYXX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**19 (17_4)  ≡  44 (17_29)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_4`:

```
    (YXXYxYxx, YYYYXyyyx)
      ==>  (YXYxxYXX, YYYYXyyyx)   = the canonical form of 17_29   [MATCH]
```

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
    P                                  = (YXXyXYxx, YYYYXyyyx)
    x -> X, y -> y                     = (YXXYxxyx, YYYYxyyyX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYYYxyyyX, YYYxyyXXYxx)   [AC move]
    x -> y, y -> x                     = (YXXXXyxxx, YYXyyXXXyxx)   [change of variables]
    r2 <- rot_9(r2) . rot_4(r1)        = (YXXXXyxxx, YYxxxxxyXXXyXXYxxx)   [AC move]
    x -> x, y -> yxxx                  = (YXXXXyxxx, YYXXXYxxxxxyyXX)   [change of variables]
  right — 17_5
    P                                  = (YYxxyXXX, YYYYXyyyx)
    x -> X, y -> Y                     = (YYXXXyxx, YYYYxyyyX)   [to the Aut-minimal form]
    r1 <- rot_3(r1) . rot_0(r2^-1)     = (YYYYxyyyX, YYYYYxyyyxxyyXX)   [AC move]
    x -> y, y -> x                     = (YXXXXyxxx, YYXXXYxxxxxyyXX)   [change of variables]
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

Substitute `x -> x, y -> Y` into `17_6`:

```
    (YXXYxxyx, YYYYXyyyx)
      ==>  (YXyXXYxx, YYYYXyyyx)   = the canonical form of 17_19   [MATCH]
```

---

## Class 018

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 22 | 17_7 | `YXyXXyxx` | `YYYYXyyyx` |
| 41 | 17_26 | `YXXYxxyX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**22 (17_7)  ≡  41 (17_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_7`:

```
    (YXyXXyxx, YYYYXyyyx)
      ==>  (YXXYxxyX, YYYYXyyyx)   = the canonical form of 17_26   [MATCH]
```

---

## Class 019

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 23 | 17_8 | `YXXyXyxx` | `YYYYXyyyx` |
| 43 | 17_28 | `YXYxxyXX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**23 (17_8)  ≡  43 (17_28)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_8`:

```
    (YXXyXyxx, YYYYXyyyx)
      ==>  (YXYxxyXX, YYYYXyyyx)   = the canonical form of 17_28   [MATCH]
```

---

## Class 020

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 24 | 17_9 | `YXyxxYXX` | `YYYYXyyyx` |
| 31 | 17_16 | `YXXyxYxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**24 (17_9)  ≡  31 (17_16)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_9`:

```
    (YXyxxYXX, YYYYXyyyx)
      ==>  (YXXyxYxx, YYYYXyyyx)   = the canonical form of 17_16   [MATCH]
```

---

## Class 021

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 25 | 17_10 | `YXYXXyxx` | `YYYYXyyyx` |
| 33 | 17_18 | `YXXyxxYx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**25 (17_10)  ≡  33 (17_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_10`:

```
    (YXYXXyxx, YYYYXyyyx)
      ==>  (YXXyxxYx, YYYYXyyyx)   = the canonical form of 17_18   [MATCH]
```

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
    P                                  = (YYXXXyxx, YXyxxyXYx)
    x -> x, y -> y                     = (YYXXXyxx, YXyxxyXYx)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_0(r1^-1)     = (YYXXXyxx, YYYXXyXyx)   [AC move]
    r2 <- rot_0(r2) . rot_7(r1^-1)     = (YYXXXyxx, YYYXXyxxyyX)   [AC move]
  right — 17_20
    P                                  = (YYXXyxxx, YYYYXyyyx)
    x -> x, y -> Y                     = (YYXXXyxx, YYYYXyyyx)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_3(r1^-1)     = (YYXXXyxx, YYYXXyxxyyX)   [AC move]
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

Substitute `x -> x, y -> Y` into `17_12`:

```
    (YXYXYxxx, YYYYXyyyx)
      ==>  (YXXXYxYx, YYYYXyyyx)   = the canonical form of 17_25   [MATCH]
```

---

## Class 024

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 28 | 17_13 | `YXYxxxyX` | `YYYYXyyyx` |
| 39 | 17_24 | `YXyXyxxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**28 (17_13)  ≡  39 (17_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_13`:

```
    (YXYxxxyX, YYYYXyyyx)
      ==>  (YXyXyxxx, YYYYXyyyx)   = the canonical form of 17_24   [MATCH]
```

---

## Class 025

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 29 | 17_14 | `YXyXYxxx` | `YYYYXyyyx` |
| 38 | 17_23 | `YXyxxxyX` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**29 (17_14)  ≡  38 (17_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_14`:

```
    (YXyXYxxx, YYYYXyyyx)
      ==>  (YXyxxxyX, YYYYXyyyx)   = the canonical form of 17_23   [MATCH]
```

---

## Class 026

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 30 | 17_15 | `YXXXyxYx` | `YYYYXyyyx` |
| 37 | 17_22 | `YXYXyxxx` | `YYYYXyyyx` |

### Why they are the same problem — 1 edge

**30 (17_15)  ≡  37 (17_22)** — *change of variables only*

Substitute `x -> x, y -> Y` into `17_15`:

```
    (YXXXyxYx, YYYYXyyyx)
      ==>  (YXYXyxxx, YYYYXyyyx)   = the canonical form of 17_22   [MATCH]
```

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
    P                                  = (YYYXyxx, YYYxxyyX)
    x -> Y, y -> x                     = (YYXXXyx, YYxxyXXX)   [to the Aut-minimal form]
    r2 <- rot_3(r2) . rot_6(r1)        = (YYXXXyx, YYXyxYXXX)   [AC move]
    r2 <- rot_0(r2) . rot_5(r1^-1)     = (YYXXXyx, YYYXyxyX)   [AC move]
  right — 15_10
    P                                  = (YXyxxyX, YYXyyxYx)
    x -> x, y -> Y                     = (YXyXYxx, YYXYXyyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_4(r1)        = (YXyXYxx, YXYXYXyxx)   [AC move]
    x -> Y, y -> yx                    = (YYXXXyx, YYYXyxyX)   [change of variables]
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

Substitute `x -> x, y -> Y` into `18_1`:

```
    (YXXYxxx, YYYYYXyyyyx)
      ==>  (YXXXYxx, YYYYYXyyyyx)   = the canonical form of 18_3   [MATCH]
```

---

## Class 029

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 50 | 19_1 | `YYXXYxxx` | `YYYYYXyyyyx` |
| 71 | 19_22 | `YYXXXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**50 (19_1)  ≡  71 (19_22)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_1`:

```
    (YYXXYxxx, YYYYYXyyyyx)
      ==>  (YYXXXYxx, YYYYYXyyyyx)   = the canonical form of 19_22   [MATCH]
```

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
    P                                  = (YXYXXYxx, YYYYYXyyyyx)
    x -> X, y -> y                     = (YXXYxYxx, YYYYYxyyyyX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYYYYxyyyyX, YYYYYxyyyXXYxYx)   [AC move]
    x -> yX, y -> X                    = (YXXXXXyxxxx, YYXyXyxxxYXXXX)   [change of variables]
    r2 <- rot_5(r2) . rot_10(r1^-1)    = (YXXXXXyxxxx, YYXyxxxxyXYXXXX)   [AC move]
    x -> X, y -> xxxxy                 = (YYXyxxxxyyX, YXXXXXyxxxx)   [change of variables]
  right — 19_2
    P                                  = (YXyxxxYXX, YYYYXXXyxx)
    x -> x, y -> Y                     = (YXXXyxYxx, YYYYXXyxxx)   [to the Aut-minimal form]
    r1 <- rot_3(r1) . rot_8(r2^-1)     = (YYYYXXyxxx, YYYYxyXXyxx)   [AC move]
    x -> Y, y -> x                     = (YYYXXXXyyx, YYXyxxxxyyX)   [change of variables]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYXyxxxxyyX, YXXXXXyxxxx)   [AC move]
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

Substitute `x -> x, y -> Y` into `19_3`:

```
    (YXXYxYxx, YYYYYXyyyyx)
      ==>  (YXYxxYXX, YYYYYXyyyyx)   = the canonical form of 19_32   [MATCH]
```

---

## Class 032

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 53 | 19_4 | `YXyxxyXX` | `YYYYYXyyyyx` |
| 69 | 19_20 | `YXXyXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**53 (19_4)  ≡  69 (19_20)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_4`:

```
    (YXyxxyXX, YYYYYXyyyyx)
      ==>  (YXXyXYxx, YYYYYXyyyyx)   = the canonical form of 19_20   [MATCH]
```

---

## Class 033

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 54 | 19_5 | `YXXYxxyx` | `YYYYYXyyyyx` |
| 67 | 19_18 | `YXyXXYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**54 (19_5)  ≡  67 (19_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_5`:

```
    (YXXYxxyx, YYYYYXyyyyx)
      ==>  (YXyXXYxx, YYYYYXyyyyx)   = the canonical form of 19_18   [MATCH]
```

---

## Class 034

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 55 | 19_6 | `YXyXXyxx` | `YYYYYXyyyyx` |
| 78 | 19_29 | `YXXYxxyX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**55 (19_6)  ≡  78 (19_29)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_6`:

```
    (YXyXXyxx, YYYYYXyyyyx)
      ==>  (YXXYxxyX, YYYYYXyyyyx)   = the canonical form of 19_29   [MATCH]
```

---

## Class 035

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 56 | 19_7 | `YXXyXyxx` | `YYYYYXyyyyx` |
| 80 | 19_31 | `YXYxxyXX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**56 (19_7)  ≡  80 (19_31)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_7`:

```
    (YXXyXyxx, YYYYYXyyyyx)
      ==>  (YXYxxyXX, YYYYYXyyyyx)   = the canonical form of 19_31   [MATCH]
```

---

## Class 036

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 57 | 19_8 | `YXyxxYXX` | `YYYYYXyyyyx` |
| 68 | 19_19 | `YXXyxYxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**57 (19_8)  ≡  68 (19_19)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_8`:

```
    (YXyxxYXX, YYYYYXyyyyx)
      ==>  (YXXyxYxx, YYYYYXyyyyx)   = the canonical form of 19_19   [MATCH]
```

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
    P                                  = (YXYXXyxx, YYYYYXyyyyx)
    x -> X, y -> y                     = (YXXyXyxx, YYYYYxyyyyX)   [to the Aut-minimal form]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYYYYxyyyyX, YYYYYxyyyXXyXyx)   [AC move]
    x -> yX, y -> X                    = (YXXXXXyxxxx, YYXyxxxxyXXXYx)   [change of variables]
    r2 <- rot_0(r2) . rot_6(r1)        = (YXXXXXyxxxx, YYXyxxxxyxYXXXX)   [AC move]
    x -> X, y -> xxxxy                 = (YYXyxxxxyyx, YXXXXXyxxxx)   [change of variables]
  right — 19_17
    P                                  = (YXXyXYxxx, YYYYXXXYxx)
    x -> x, y -> y                     = (YXXyXYxxx, YYYYXXXYxx)   [to the Aut-minimal form]
    r1 <- rot_1(r1) . rot_0(r2^-1)     = (YYYYXXXYxx, YYYYXXYxxyX)   [AC move]
    x -> Y, y -> X                     = (YYYXXXXyyX, YYXyxxxxyyx)   [change of variables]
    r1 <- rot_0(r1) . rot_1(r2)        = (YYXyxxxxyyx, YXXXXXyxxxx)   [AC move]
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

Substitute `x -> x, y -> Y` into `19_10`:

```
    (YYXXXyxx, YYYYYXyyyyx)
      ==>  (YYXXyxxx, YYYYYXyyyyx)   = the canonical form of 19_21   [MATCH]
```

---

## Class 039

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 60 | 19_11 | `YXYXYxxx` | `YYYYYXyyyyx` |
| 75 | 19_26 | `YXXXYxYx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**60 (19_11)  ≡  75 (19_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_11`:

```
    (YXYXYxxx, YYYYYXyyyyx)
      ==>  (YXXXYxYx, YYYYYXyyyyx)   = the canonical form of 19_26   [MATCH]
```

---

## Class 040

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 61 | 19_12 | `YXYxxxyX` | `YYYYYXyyyyx` |
| 74 | 19_25 | `YXyXyxxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**61 (19_12)  ≡  74 (19_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_12`:

```
    (YXYxxxyX, YYYYYXyyyyx)
      ==>  (YXyXyxxx, YYYYYXyyyyx)   = the canonical form of 19_25   [MATCH]
```

---

## Class 041

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 62 | 19_13 | `YXyXYxxx` | `YYYYYXyyyyx` |
| 73 | 19_24 | `YXyxxxyX` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**62 (19_13)  ≡  73 (19_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_13`:

```
    (YXyXYxxx, YYYYYXyyyyx)
      ==>  (YXyxxxyX, YYYYYXyyyyx)   = the canonical form of 19_24   [MATCH]
```

---

## Class 042

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 63 | 19_14 | `YXXXyxYx` | `YYYYYXyyyyx` |
| 72 | 19_23 | `YXYXyxxx` | `YYYYYXyyyyx` |

### Why they are the same problem — 1 edge

**63 (19_14)  ≡  72 (19_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_14`:

```
    (YXXXyxYx, YYYYYXyyyyx)
      ==>  (YXYXyxxx, YYYYYXyyyyx)   = the canonical form of 19_23   [MATCH]
```

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
    P                                  = (YYxxYXXX, YYYYYxYXYXX)
    x -> X, y -> Y                     = (YYXXXYxx, YYYYYXXYXYx)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_4(r1^-1)     = (YYXXXYxx, YYYXXyxYXYx)   [AC move]
  right — 19_15
    P                                  = (YYxxxYXX, YXYxxyXyXYx)
    x -> x, y -> Yx                    = (YXXYxYxxx, YYXyyXXyxx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXYxYxxx, YYxyXXYxYxYxx)   [AC move]
    x -> X, y -> YX                    = (YYXXXYxx, YYYXXyxYXYx)   [change of variables]
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
    P                                  = (YYxxyXXX, YXyxxyXyXYx)
    x -> x, y -> Yx                    = (YXXXyXyxx, YYXyyXYxxx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXXyXyxx, YYxyXXXyXyXyx)   [AC move]
    x -> X, y -> yX                    = (YYXXXyxx, YYYXXYxyXyx)   [change of variables]
  right — 19_16
    P                                  = (YYxxxyXX, YYYYYxxyxyX)
    x -> X, y -> y                     = (YYXXXyxx, YYYYYXXyXyx)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_4(r1^-1)     = (YYXXXyxx, YYYXXYxyXyx)   [AC move]
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
    P                                  = (YYYxyxyX, YXyxxyXyX)
    x -> y, y -> X                     = (YXXXyxYx, YYxyXyxyx)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_0(r1)        = (YXXXyxYx, YYxyXyXXyxYxx)   [AC move]
    x -> x, y -> yx                    = (YYXXXyx, YYXyxyXyXYx)   [change of variables]
  right — 17_30
    P                                  = (YYYxyXX, YYxxyXyXYX)
    x -> y, y -> x                     = (YYXXXyx, YYxxyxyXyX)   [to the Aut-minimal form]
    r2 <- rot_6(r2) . rot_4(r1)        = (YYXXXyx, YYXyxyXyXYx)   [AC move]
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
    P                                  = (YYxxyX, YYYYYXyxxyx)
    x -> X, y -> y                     = (YYXXyx, YYYYYxyXXyX)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_5(r1^-1)     = (YYXXyx, YYYYYxyyyXX)   [AC move]
    r2 <- rot_3(r2) . rot_0(r1)        = (YYXXyx, YYYYYXyxyXX)   [AC move]
  right — 17_32
    P                                  = (YYxyXX, YYYXXyxyxYX)
    x -> Xy, y -> x                    = (YXXyxYx, YYXyXyxxyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_5(r1^-1)     = (YXXyxYx, YXyXyxxxxyX)   [AC move]
    x -> Y, y -> XY                    = (YYXXyx, YYYYYXyxyXX)   [change of variables]
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

Substitute `x -> Y, y -> x` into `20_1`:

```
    (YYYxyyx, YXXXXXyxxxxxx)
      ==>  (YXXXYxx, YYYYYYXyyyyyx)   = the canonical form of 20_3   [MATCH]
```

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
    P                                  = (YYxxyxx, YYYxyyxyX)
    x -> y, y -> X                     = (YYXXYYx, YXXXyxYxx)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_2(r1)        = (YYXXYYx, YYXXYxYxxYXX)   [AC move]
  right — 16_4
    P                                  = (YYXXyXX, YYYxyyXyX)
    x -> y, y -> x                     = (YYXXYYx, YXXXyxxYx)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_2(r1)        = (YYXXYYx, YYXXYxxYxYXX)   [AC move]
    x -> X, y -> Y                     = (YYXXYYx, YYXXYxYxxYXX)   [change of variables]
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
    P                                  = (YYXXYxxx, YYYYYYXyyyyyx)
    x -> x, y -> Y                     = (YYXXXYxx, YYYYYYXyyyyyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YYXXXYxx, YYYYYxyyyyXXXYx)   [AC move]
    r2 <- rot_3(r2) . rot_2(r1)        = (YYXXXYxx, YYYYYxyyXXXYXYx)   [AC move]
    r2 <- rot_5(r2) . rot_2(r1)        = (YYXXXYxx, YYYYYXXYXYXYx)   [AC move]
  right — 21_20
    P                                  = (YYXXXYxx, YXYXYxYXXyxyx)
    x -> X, y -> xY                    = (YXXYxYxxx, YYYxyyXXYxx)   [to the Aut-minimal form]
    r2 <- rot_3(r2) . rot_2(r1)        = (YXXYxYxxx, YYYxyXXYxYxYxx)   [AC move]
    x -> X, y -> YX                    = (YYXXXYxx, YYYXXyxYXYXYx)   [change of variables]
    r2 <- rot_6(r2) . rot_4(r1)        = (YYXXXYxx, YYYYYXXYXYXYx)   [AC move]
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

Substitute `x -> x, y -> Y` into `20_4`:

```
    (YXyxxxYXX, YYYYYXXXyxx)
      ==>  (YXXXyxYxx, YYYYYXXyxxx)   = the canonical form of 20_7   [MATCH]
```

---

## Class 051

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 94 | 21_4 | `YXyxxyXX` | `YYYYYYXyyyyyx` |
| 110 | 21_18 | `YXXyXYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**94 (21_4)  ≡  110 (21_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_4`:

```
    (YXyxxyXX, YYYYYYXyyyyyx)
      ==>  (YXXyXYxx, YYYYYYXyyyyyx)   = the canonical form of 21_18   [MATCH]
```

---

## Class 052

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 95 | 21_5 | `YXXYxxyx` | `YYYYYYXyyyyyx` |
| 108 | 21_16 | `YXyXXYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**95 (21_5)  ≡  108 (21_16)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_5`:

```
    (YXXYxxyx, YYYYYYXyyyyyx)
      ==>  (YXyXXYxx, YYYYYYXyyyyyx)   = the canonical form of 21_16   [MATCH]
```

---

## Class 053

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 96 | 21_6 | `YXyXXyxx` | `YYYYYYXyyyyyx` |
| 119 | 21_27 | `YXXYxxyX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**96 (21_6)  ≡  119 (21_27)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_6`:

```
    (YXyXXyxx, YYYYYYXyyyyyx)
      ==>  (YXXYxxyX, YYYYYYXyyyyyx)   = the canonical form of 21_27   [MATCH]
```

---

## Class 054

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 98 | 21_8 | `YXyxxYXX` | `YYYYYYXyyyyyx` |
| 109 | 21_17 | `YXXyxYxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**98 (21_8)  ≡  109 (21_17)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_8`:

```
    (YXyxxYXX, YYYYYYXyyyyyx)
      ==>  (YXXyxYxx, YYYYYYXyyyyyx)   = the canonical form of 21_17   [MATCH]
```

---

## Class 055

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 99 | 20_5 | `YXyxxxyXX` | `YYYYYXXYxxx` |
| 107 | 20_6 | `YXXyXYxxx` | `YYYYYXXXYxx` |

### Why they are the same problem — 1 edge

**99 (20_5)  ≡  107 (20_6)** — *change of variables only*

Substitute `x -> x, y -> Y` into `20_5`:

```
    (YXyxxxyXX, YYYYYXXYxxx)
      ==>  (YXXyXYxxx, YYYYYXXXYxx)   = the canonical form of 20_6   [MATCH]
```

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
    P                                  = (YYXXXyxx, YYYXXYxyXyXyx)
    x -> x, y -> y                     = (YYXXXyxx, YYYXXYxyXyXyx)   [to the Aut-minimal form]
    r2 <- rot_8(r2) . rot_4(r1^-1)     = (YYXXXyxx, YXyXyxxyXYxYx)   [AC move]
    x -> X, y -> yX                    = (YXXXyXyxx, YYYxyyXXXyx)   [change of variables]
  right — 21_19
    P                                  = (YYXXyxxx, YXYXYxyXXyxyx)
    x -> X, y -> xY                    = (YXXXyXyxx, YYYxyyXXXyx)   [to the Aut-minimal form]
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

Substitute `x -> x, y -> Y` into `21_10`:

```
    (YXYXYxxx, YYYYYYXyyyyyx)
      ==>  (YXXXYxYx, YYYYYYXyyyyyx)   = the canonical form of 21_24   [MATCH]
```

---

## Class 058

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 102 | 21_11 | `YXYxxxyX` | `YYYYYYXyyyyyx` |
| 115 | 21_23 | `YXyXyxxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**102 (21_11)  ≡  115 (21_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_11`:

```
    (YXYxxxyX, YYYYYYXyyyyyx)
      ==>  (YXyXyxxx, YYYYYYXyyyyyx)   = the canonical form of 21_23   [MATCH]
```

---

## Class 059

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 103 | 21_12 | `YXyXYxxx` | `YYYYYYXyyyyyx` |
| 114 | 21_22 | `YXyxxxyX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**103 (21_12)  ≡  114 (21_22)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_12`:

```
    (YXyXYxxx, YYYYYYXyyyyyx)
      ==>  (YXyxxxyX, YYYYYYXyyyyyx)   = the canonical form of 21_22   [MATCH]
```

---

## Class 060

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 104 | 21_13 | `YXXXyxYx` | `YYYYYYXyyyyyx` |
| 113 | 21_21 | `YXYXyxxx` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**104 (21_13)  ≡  113 (21_21)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_13`:

```
    (YXXXyxYx, YYYYYYXyyyyyx)
      ==>  (YXYXyxxx, YYYYYYXyyyyyx)   = the canonical form of 21_21   [MATCH]
```

---

## Class 061

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 105 | 21_14 | `YYxxxYXX` | `YYYYYYXyyyyyx` |
| 118 | 21_26 | `YYxxYXXX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**105 (21_14)  ≡  118 (21_26)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_14`:

```
    (YYxxxYXX, YYYYYYXyyyyyx)
      ==>  (YYxxYXXX, YYYYYYXyyyyyx)   = the canonical form of 21_26   [MATCH]
```

---

## Class 062

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 106 | 21_15 | `YYxxxyXX` | `YYYYYYXyyyyyx` |
| 117 | 21_25 | `YYxxyXXX` | `YYYYYYXyyyyyx` |

### Why they are the same problem — 1 edge

**106 (21_15)  ≡  117 (21_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_15`:

```
    (YYxxxyXX, YYYYYYXyyyyyx)
      ==>  (YYxxyXXX, YYYYYYXyyyyyx)   = the canonical form of 21_25   [MATCH]
```

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
    P                                  = (YYXXyxx, YYxyxyxYXX)
    x -> X, y -> xY                    = (YXXyXyxx, YYXyxyXyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YXXyXyxx, YYXyxyXXXyXyx)   [AC move]
    x -> X, y -> yX                    = (YYXXyxx, YYXXYxxYXyXyx)   [change of variables]
  right — 17_34
    P                                  = (YYXXyxx, YYYYYXyXyx)
    x -> x, y -> y                     = (YYXXyxx, YYYYYXyXyx)   [to the Aut-minimal form]
    r2 <- rot_6(r2) . rot_2(r1^-1)     = (YYXXyxx, YYXXYxxYXyXyx)   [AC move]
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
    P                                  = (YYXXyx, YYYXYxyxyXXyX)
    x -> x, y -> y                     = (YYXXyx, YYYXYxyxyXXyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YYXXyx, YYXYxyxyXXYXX)   [AC move]
    x -> x, y -> Xy                    = (YXXyxYx, YYXyyXyxyxx)   [change of variables]
  right — 19_34
    P                                  = (YYXyxx, YYxxYxxyXyXYx)
    x -> x, y -> Yx                    = (YXXyxYx, YYXyyXyxyxx)   [to the Aut-minimal form]
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

Substitute `x -> x, y -> Y` into `16_7`:

```
    (YYxYxyX, YXXXyxxYx)
      ==>  (YYxyXYX, YXYXXyxxx)   = the canonical form of 16_8   [MATCH]
```

---

## Class 066

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 134 | 22_1 | `YXXYxxx` | `YYYYYYYXyyyyyyx` |
| 140 | 22_4 | `YXXXYxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**134 (22_1)  ≡  140 (22_4)** — *change of variables only*

Substitute `x -> x, y -> Y` into `22_1`:

```
    (YXXYxxx, YYYYYYYXyyyyyyx)
      ==>  (YXXXYxx, YYYYYYYXyyyyyyx)   = the canonical form of 22_4   [MATCH]
```

---

## Class 067

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 135 | 22_2 | `YYYxyyX` | `YXXXXXXXyxxxxxx` |
| 139 | 22_3 | `YYYxyyX` | `YXXXXXXyxxxxxxx` |

### Why they are the same problem — 1 edge

**135 (22_2)  ≡  139 (22_3)** — *change of variables only*

Substitute `x -> x, y -> Y` into `22_2`:

```
    (YYYxyyX, YXXXXXXXyxxxxxx)
      ==>  (YYYxyyX, YXXXXXXyxxxxxxx)   = the canonical form of 22_3   [MATCH]
```

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
    P                                  = (YXyXXYxx, YYYYXyXyx)
    x -> x, y -> Y                     = (YXXYxxyx, YYYYXyxyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXYxxyx, YYYXyXyxx)   [AC move]
  right — 17_40
    P                                  = (YXXYxxyx, YYYXyXyxx)
    x -> x, y -> y                     = (YXXYxxyx, YYYXyXyxx)   [to the Aut-minimal form]
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

Substitute `x -> yx, y -> Y` into `17_38`:

```
    (YYYXXyx, YYXYxyxyXX)
      ==>  (YYYXyxyx, YXYXyXyxx)   = the canonical form of 17_39   [MATCH]
```

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
    P                                  = (YYXyyXYYx, YYYYYYYXXX)
    x -> y, y -> X                     = (YXXYxxyxx, YYYxxxxxxx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXYxxyxx, YYxxxxxYXXyxx)   [AC move]
    r1 <- rot_0(r1) . rot_0(r2^-1)     = (YYxxxxxYXXyxx, YXXXXyxxYxxxxx)   [AC move]
    x -> x, y -> yxxxxx                = (YYXXXXyxx, YYXXyxxYXXXXX)   [change of variables]
  right — 19_35
    P                                  = (YYYYXXyyx, YYYYYxyyXX)
    x -> Y, y -> X                     = (YYXXXXyxx, YYxxyXXXXX)   [to the Aut-minimal form]
    r2 <- rot_5(r2) . rot_8(r1)        = (YYXXXXyxx, YYXXyxxYXXXXX)   [AC move]
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

Substitute `x -> x, y -> Y` into `23_1`:

```
    (YYXXYxxx, YYYYYYYXyyyyyyx)
      ==>  (YYXXXYxx, YYYYYYYXyyyyyyx)   = the canonical form of 23_13   [MATCH]
```

---

## Class 072

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 145 | 21_30 | `YXyxxxYXX` | `YYYYYYXXXyxx` |
| 175 | 21_33 | `YXXXyxYxx` | `YYYYYYXXyxxx` |

### Why they are the same problem — 1 edge

**145 (21_30)  ≡  175 (21_33)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_30`:

```
    (YXyxxxYXX, YYYYYYXXXyxx)
      ==>  (YXXXyxYxx, YYYYYYXXyxxx)   = the canonical form of 21_33   [MATCH]
```

---

## Class 073

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 146 | 22_5 | `YXXYxxxyX` | `YYYYYYYxxxYXX` |
| 177 | 22_12 | `YXyXXyxxx` | `YYYYYYYxxYXXX` |

### Why they are the same problem — 1 edge

**146 (22_5)  ≡  177 (22_12)** — *change of variables only*

Substitute `x -> x, y -> Y` into `22_5`:

```
    (YXXYxxxyX, YYYYYYYxxxYXX)
      ==>  (YXyXXyxxx, YYYYYYYxxYXXX)   = the canonical form of 22_12   [MATCH]
```

---

## Class 074

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 147 | 22_6 | `YYYYYxxyXXX` | `YYXyxxyxYXX` |
| 165 | 22_10 | `YYYYYxxxyXX` | `YYxxYXyXXyx` |

### Why they are the same problem — 1 edge

**147 (22_6)  ≡  165 (22_10)** — *change of variables only*

Substitute `x -> x, y -> Y` into `22_6`:

```
    (YYYYYxxyXXX, YYXyxxyxYXX)
      ==>  (YYYYYxxxyXX, YYxxYXyXXyx)   = the canonical form of 22_10   [MATCH]
```

---

## Class 075

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 148 | 23_2 | `YXXYxxyx` | `YYYYYYYXyyyyyyx` |
| 163 | 23_11 | `YXyXXYxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**148 (23_2)  ≡  163 (23_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_2`:

```
    (YXXYxxyx, YYYYYYYXyyyyyyx)
      ==>  (YXyXXYxx, YYYYYYYXyyyyyyx)   = the canonical form of 23_11   [MATCH]
```

---

## Class 076

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 149 | 23_3 | `YXyXXyxx` | `YYYYYYYXyyyyyyx` |
| 174 | 23_20 | `YXXYxxyX` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**149 (23_3)  ≡  174 (23_20)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_3`:

```
    (YXyXXyxx, YYYYYYYXyyyyyyx)
      ==>  (YXXYxxyX, YYYYYYYXyyyyyyx)   = the canonical form of 23_20   [MATCH]
```

---

## Class 077

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 150 | 22_7 | `YXyXXYxxx` | `YYYYYYYxxxyXX` |
| 176 | 22_11 | `YXXyxxxyX` | `YYYYYYYxxyXXX` |

### Why they are the same problem — 1 edge

**150 (22_7)  ≡  176 (22_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into `22_7`:

```
    (YXyXXYxxx, YYYYYYYxxxyXX)
      ==>  (YXXyxxxyX, YYYYYYYxxyXXX)   = the canonical form of 22_11   [MATCH]
```

---

## Class 078

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 151 | 22_8 | `YYYYYxxYXXX` | `YYXyxxYxyXX` |
| 164 | 22_9 | `YYYYYxxxYXX` | `YYxxyXYXXyx` |

### Why they are the same problem — 1 edge

**151 (22_8)  ≡  164 (22_9)** — *change of variables only*

Substitute `x -> x, y -> Y` into `22_8`:

```
    (YYYYYxxYXXX, YYXyxxYxyXX)
      ==>  (YYYYYxxxYXX, YYxxyXYXXyx)   = the canonical form of 22_9   [MATCH]
```

---

## Class 079

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 152 | 21_31 | `YXyxxxyXX` | `YYYYYYXXYxxx` |
| 162 | 21_32 | `YXXyXYxxx` | `YYYYYYXXXYxx` |

### Why they are the same problem — 1 edge

**152 (21_31)  ≡  162 (21_32)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_31`:

```
    (YXyxxxyXX, YYYYYYXXYxxx)
      ==>  (YXXyXYxxx, YYYYYYXXXYxx)   = the canonical form of 21_32   [MATCH]
```

---

## Class 080

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 153 | 23_4 | `YYXXXyxx` | `YYYYYYYXyyyyyyx` |
| 166 | 23_12 | `YYXXyxxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**153 (23_4)  ≡  166 (23_12)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_4`:

```
    (YYXXXyxx, YYYYYYYXyyyyyyx)
      ==>  (YYXXyxxx, YYYYYYYXyyyyyyx)   = the canonical form of 23_12   [MATCH]
```

---

## Class 081

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 154 | 23_5 | `YXYXYxxx` | `YYYYYYYXyyyyyyx` |
| 171 | 23_17 | `YXXXYxYx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**154 (23_5)  ≡  171 (23_17)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_5`:

```
    (YXYXYxxx, YYYYYYYXyyyyyyx)
      ==>  (YXXXYxYx, YYYYYYYXyyyyyyx)   = the canonical form of 23_17   [MATCH]
```

---

## Class 082

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 155 | 23_6 | `YXYxxxyX` | `YYYYYYYXyyyyyyx` |
| 170 | 23_16 | `YXyXyxxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**155 (23_6)  ≡  170 (23_16)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_6`:

```
    (YXYxxxyX, YYYYYYYXyyyyyyx)
      ==>  (YXyXyxxx, YYYYYYYXyyyyyyx)   = the canonical form of 23_16   [MATCH]
```

---

## Class 083

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 156 | 23_7 | `YXyXYxxx` | `YYYYYYYXyyyyyyx` |
| 169 | 23_15 | `YXyxxxyX` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**156 (23_7)  ≡  169 (23_15)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_7`:

```
    (YXyXYxxx, YYYYYYYXyyyyyyx)
      ==>  (YXyxxxyX, YYYYYYYXyyyyyyx)   = the canonical form of 23_15   [MATCH]
```

---

## Class 084

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 157 | 23_8 | `YXXXyxYx` | `YYYYYYYXyyyyyyx` |
| 168 | 23_14 | `YXYXyxxx` | `YYYYYYYXyyyyyyx` |

### Why they are the same problem — 1 edge

**157 (23_8)  ≡  168 (23_14)** — *change of variables only*

Substitute `x -> x, y -> Y` into `23_8`:

```
    (YXXXyxYx, YYYYYYYXyyyyyyx)
      ==>  (YXYXyxxx, YYYYYYYXyyyyyyx)   = the canonical form of 23_14   [MATCH]
```

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
    P                                  = (YYxxYXXX, YYYYYxYXYXYxyXX)
    x -> X, y -> Y                     = (YYXXXYxx, YYYYYXXyxYXYXYx)   [to the Aut-minimal form]
    r2 <- rot_8(r2) . rot_4(r1^-1)     = (YYXXXYxx, YYYXXyxyxYXYXYx)   [AC move]
  right — 23_9
    P                                  = (YYxxxYXX, YXYxxyXyXyXYxYx)
    x -> x, y -> Yx                    = (YXXYxYxxx, YYYXyyyXXyxx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YXXYxYxxx, YYYxyyXXYxYxYxx)   [AC move]
    x -> X, y -> YX                    = (YYXXXYxx, YYYXXyxyxYXYXYx)   [change of variables]
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
    P                                  = (YYxxyXXX, YYYYYYYXyyyyyyx)
    x -> X, y -> Y                     = (YYXXXyxx, YYYYYYYxyyyyyyX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_1(r1)        = (YYXXXyxx, YYYYYYYxyyyyXXXyx)   [AC move]
    r2 <- rot_3(r2) . rot_2(r1)        = (YYXXXyxx, YYYYYYYxyyXXXyXyx)   [AC move]
  right — 23_10
    P                                  = (YYxxxyXX, YYYYYxxYXyxyxyX)
    x -> X, y -> y                     = (YYXXXyxx, YYYYYXXYxyXyXyx)   [to the Aut-minimal form]
    r2 <- rot_6(r2) . rot_4(r1)        = (YYXXXyxx, YYYYYYYXXyXyXyx)   [AC move]
    r2 <- rot_5(r2) . rot_6(r1^-1)     = (YYXXXyxx, YYYYYYYxyyXXXyXyx)   [AC move]
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

Substitute `x -> x, y -> Y` into `18_4`:

```
    (YYYXXYxyX, YYxYXXYXX)
      ==>  (YYYxyXYxx, YYxxYxxYX)   = the canonical form of 18_5   [MATCH]
```

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
    P                                  = (YYxyXX, YYYYYYYXyXXyxyX)
    x -> X, y -> Y                     = (YYXXyx, YYYYYYYXyxyXXyX)   [to the Aut-minimal form]
    r2 <- rot_4(r2) . rot_5(r1)        = (YYXXyx, YYYYYYYXyXyxYXXyX)   [AC move]
    x -> Y, y -> X                     = (YYXXyx, YYXyxYxYXXXXXXXYx)   [change of variables]
  right — 21_35
    P                                  = (YYxxyX, YYYYYYYxyxyXyxx)
    x -> X, y -> y                     = (YYXXyx, YYYYYYYXyXyxyXX)   [to the Aut-minimal form]
    r2 <- rot_1(r2) . rot_1(r1)        = (YYXXyx, YYYYYYYXyXyxYXXyX)   [AC move]
    x -> Y, y -> X                     = (YYXXyx, YYXyxYxYXXXXXXXYx)   [change of variables]
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

Substitute `x -> x, y -> Y` into `24_1`:

```
    (YXXYxxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXXXYxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 24_4   [MATCH]
```

---

## Class 090

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 193 | 24_2 | `YYYXyyx` | `YXXXXXXXyxxxxxxxx` |
| 205 | 24_3 | `YXXyxxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**193 (24_2)  ≡  205 (24_3)** — *change of variables only*

Substitute `x -> y, y -> x` into `24_2`:

```
    (YYYXyyx, YXXXXXXXyxxxxxxxx)
      ==>  (YXXyxxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 24_3   [MATCH]
```

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
    P                                  = (YYYXYxyx, YYXXYxxyXyx)
    x -> Y, y -> x                     = (YXXXyXYx, YYxyxYXXyyX)   [to the Aut-minimal form]
    r2 <- rot_3(r2) . rot_3(r1^-1)     = (YXXXyXYx, YYXyyxYYXyX)   [AC move]
  right — 19_41
    P                                  = (YYYXyXYx, YXXYxYXXyxx)
    x -> Y, y -> X                     = (YXXXyXYx, YYXyyxYYXyX)   [to the Aut-minimal form]
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

Substitute `x -> x, y -> Y` into `18_8`:

```
    (YYYXXyx, YYXYXyXyxxx)
      ==>  (YYYXyxx, YYXXXyxyxYx)   = the canonical form of 18_10   [MATCH]
```

---

## Class 093

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 200 | 20_10 | `YYXYYxyyx` | `YYYYYYYxxxx` |
| 209 | 20_11 | `YYXyyXYYx` | `YYYYYYYXXXX` |

### Why they are the same problem — 1 edge

**200 (20_10)  ≡  209 (20_11)** — *change of variables only*

Substitute `x -> x, y -> Y` into `20_10`:

```
    (YYXYYxyyx, YYYYYYYxxxx)
      ==>  (YYXyyXYYx, YYYYYYYXXXX)   = the canonical form of 20_11   [MATCH]
```

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
    P                                  = (YYXXYxxx, YYYYYYYYXyyyyyyyx)
    x -> x, y -> Y                     = (YYXXXYxx, YYYYYYYYXyyyyyyyx)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YYXXXYxx, YYYYYYYxyyyyyyXXXYx)   [AC move]
    r2 <- rot_3(r2) . rot_2(r1)        = (YYXXXYxx, YYYYYYYxyyyyXXXYXYx)   [AC move]
    r2 <- rot_5(r2) . rot_2(r1)        = (YYXXXYxx, YYYYYYYxyyXXXYXYXYx)   [AC move]
    r2 <- rot_7(r2) . rot_2(r1)        = (YYXXXYxx, YYYYYYYXXYXYXYXYx)   [AC move]
  right — 25_22
    P                                  = (YYXXXYxx, YYYXXyxyxYXYXYXYx)
    x -> X, y -> xY                    = (YXXYxYxxx, YYYYxyyXXYxYxYxx)   [to the Aut-minimal form]
    r2 <- rot_7(r2) . rot_2(r1)        = (YXXYxYxxx, YYYYxyXXYxYxYxYxYxx)   [AC move]
    x -> X, y -> YX                    = (YYXXXYxx, YYYYYXXyxYXYXYXYx)   [change of variables]
    r2 <- rot_8(r2) . rot_4(r1)        = (YYXXXYxx, YYYYYYYXXYXYXYXYx)   [AC move]
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

Substitute `x -> x, y -> Y` into `25_2`:

```
    (YXXYxxYx, YYYYYYYYXyyyyyyyx)
      ==>  (YXYXXYxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_30   [MATCH]
```

---

## Class 096

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 215 | 25_3 | `YXXYxYxx` | `YYYYYYYYXyyyyyyyx` |
| 254 | 25_32 | `YXYxxYXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**215 (25_3)  ≡  254 (25_32)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_3`:

```
    (YXXYxYxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXYxxYXX, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_32   [MATCH]
```

---

## Class 097

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 216 | 25_4 | `YXyxxyXX` | `YYYYYYYYXyyyyyyyx` |
| 242 | 25_20 | `YXXyXYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**216 (25_4)  ≡  242 (25_20)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_4`:

```
    (YXyxxyXX, YYYYYYYYXyyyyyyyx)
      ==>  (YXXyXYxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_20   [MATCH]
```

---

## Class 098

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 217 | 25_5 | `YXXYxxyx` | `YYYYYYYYXyyyyyyyx` |
| 240 | 25_18 | `YXyXXYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**217 (25_5)  ≡  240 (25_18)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_5`:

```
    (YXXYxxyx, YYYYYYYYXyyyyyyyx)
      ==>  (YXyXXYxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_18   [MATCH]
```

---

## Class 099

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 218 | 25_6 | `YXyXXyxx` | `YYYYYYYYXyyyyyyyx` |
| 251 | 25_29 | `YXXYxxyX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**218 (25_6)  ≡  251 (25_29)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_6`:

```
    (YXyXXyxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXXYxxyX, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_29   [MATCH]
```

---

## Class 100

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 219 | 25_7 | `YXXyXyxx` | `YYYYYYYYXyyyyyyyx` |
| 253 | 25_31 | `YXYxxyXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**219 (25_7)  ≡  253 (25_31)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_7`:

```
    (YXXyXyxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXYxxyXX, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_31   [MATCH]
```

---

## Class 101

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 220 | 25_8 | `YXyxxYXX` | `YYYYYYYYXyyyyyyyx` |
| 241 | 25_19 | `YXXyxYxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**220 (25_8)  ≡  241 (25_19)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_8`:

```
    (YXyxxYXX, YYYYYYYYXyyyyyyyx)
      ==>  (YXXyxYxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_19   [MATCH]
```

---

## Class 102

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 221 | 25_9 | `YXYXXyxx` | `YYYYYYYYXyyyyyyyx` |
| 239 | 25_17 | `YXXyxxYx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**221 (25_9)  ≡  239 (25_17)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_9`:

```
    (YXYXXyxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXXyxxYx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_17   [MATCH]
```

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
    P                                  = (YYXXyxxx, YYYXyxyxyxyXYXYxx)
    x -> X, y -> xY                    = (YXXXyXyxx, YYYYxyyXXXyXyXyx)   [to the Aut-minimal form]
    r2 <- rot_7(r2) . rot_2(r1)        = (YXXXyXyxx, YYYYxyXXXyXyXyXyXyx)   [AC move]
    x -> X, y -> yX                    = (YYXXXyxx, YYYYYXXYxyXyXyXyx)   [change of variables]
  right — 25_10
    P                                  = (YYXXXyxx, YYYYYYYXXyXyXyXyx)
    x -> x, y -> y                     = (YYXXXyxx, YYYYYYYXXyXyXyXyx)   [to the Aut-minimal form]
    r2 <- rot_8(r2) . rot_4(r1^-1)     = (YYXXXyxx, YYYYYXXYxyXyXyXyx)   [AC move]
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

Substitute `x -> x, y -> Y` into `25_11`:

```
    (YXYXYxxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXXXYxYx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_26   [MATCH]
```

---

## Class 105

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 224 | 25_12 | `YXYxxxyX` | `YYYYYYYYXyyyyyyyx` |
| 247 | 25_25 | `YXyXyxxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**224 (25_12)  ≡  247 (25_25)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_12`:

```
    (YXYxxxyX, YYYYYYYYXyyyyyyyx)
      ==>  (YXyXyxxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_25   [MATCH]
```

---

## Class 106

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 226 | 25_13 | `YXyXYxxx` | `YYYYYYYYXyyyyyyyx` |
| 246 | 25_24 | `YXyxxxyX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**226 (25_13)  ≡  246 (25_24)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_13`:

```
    (YXyXYxxx, YYYYYYYYXyyyyyyyx)
      ==>  (YXyxxxyX, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_24   [MATCH]
```

---

## Class 107

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 227 | 25_14 | `YXXXyxYx` | `YYYYYYYYXyyyyyyyx` |
| 245 | 25_23 | `YXYXyxxx` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**227 (25_14)  ≡  245 (25_23)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_14`:

```
    (YXXXyxYx, YYYYYYYYXyyyyyyyx)
      ==>  (YXYXyxxx, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_23   [MATCH]
```

---

## Class 108

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 228 | 25_15 | `YYxxxYXX` | `YYYYYYYYXyyyyyyyx` |
| 250 | 25_28 | `YYxxYXXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**228 (25_15)  ≡  250 (25_28)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_15`:

```
    (YYxxxYXX, YYYYYYYYXyyyyyyyx)
      ==>  (YYxxYXXX, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_28   [MATCH]
```

---

## Class 109

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 229 | 25_16 | `YYxxxyXX` | `YYYYYYYYXyyyyyyyx` |
| 249 | 25_27 | `YYxxyXXX` | `YYYYYYYYXyyyyyyyx` |

### Why they are the same problem — 1 edge

**229 (25_16)  ≡  249 (25_27)** — *change of variables only*

Substitute `x -> x, y -> Y` into `25_16`:

```
    (YYxxxyXX, YYYYYYYYXyyyyyyyx)
      ==>  (YYxxyXXX, YYYYYYYYXyyyyyyyx)   = the canonical form of 25_27   [MATCH]
```

---

## Class 110

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 230 | 21_39 | `YYYXXyyxx` | `YYYYYXyyXyyx` |
| 256 | 21_41 | `YYYXXyyxx` | `YYYYYXyyxyyx` |

### Why they are the same problem — 1 edge

**230 (21_39)  ≡  256 (21_41)** — *change of variables only*

Substitute `x -> x, y -> Y` into `21_39`:

```
    (YYYXXyyxx, YYYYYXyyXyyx)
      ==>  (YYYXXyyxx, YYYYYXyyxyyx)   = the canonical form of 21_41   [MATCH]
```

---

## Class 111

**2 presentations**, `|det| = 1`

| pres_id | name | r1 | r2 |
|---|---|---|---|
| 232 | 19_44 | `YYYXXyyx` | `YYYxyyXXYXX` |
| 255 | 19_49 | `YYYXyyxx` | `YYYxxYxxyyX` |

### Why they are the same problem — 1 edge

**232 (19_44)  ≡  255 (19_49)** — *change of variables only*

Substitute `x -> x, y -> Y` into `19_44`:

```
    (YYYXXyyx, YYYxyyXXYXX)
      ==>  (YYYXyyxx, YYYxxYxxyyX)   = the canonical form of 19_49   [MATCH]
```

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
    P                                  = (YYYYxyyXyX, YYXYXyXYxyx)
    x -> y, y -> x                     = (YXXXXyxxYx, YXYxYXyxyXX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_4(r1)        = (YXXXXyxxYx, YXyxxYXXXXXYx)   [AC move]
    x -> x, y -> yx                    = (YYXXXXyxx, YYXyxxYXXXXXX)   [change of variables]
    r2 <- rot_6(r2) . rot_1(r1^-1)     = (YYXXXXyxx, YYxxxyXXXXXX)   [AC move]
  right — 21_42
    P                                  = (YYYYxxyyX, YYYYXYxxYYxx)
    x -> y, y -> X                     = (YYXXXXyxx, YYXyXXXXYYXX)   [to the Aut-minimal form]
    r2 <- rot_0(r2) . rot_4(r1^-1)     = (YYXXXXyxx, YYXyXXXXXXYxx)   [AC move]
    r2 <- rot_0(r2) . rot_0(r1^-1)     = (YYXXXXyxx, YYxxxyXXXXXX)   [AC move]
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

Substitute `x -> x, y -> Y` into `19_45`:

```
    (YYYxxyyX, YYYYXyxxYxx)
      ==>  (YYYxyyXX, YYYYXXYXXyx)   = the canonical form of 19_50   [MATCH]
```

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

