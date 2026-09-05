# Reviews of the frozen AK(3) Aut(F2) manifest

Date: 2026-07-29

## Mathematical contract review

**VERDICT: APPROVE — zero load-bearing findings.**

The hostile reviewer checked the exact seven-edge inverse-closed Nielsen
alphabet, `child = phi o nu`, identity-first FIFO first discovery, the frozen
1,000-map prefix, inverse edge words and both inverse compositions, all three
dictionary-derived spelling tracks, exact cyclic reconstruction, the cellular
symmetry group and raw ASCII order, all 3,000 bucket memberships, canonical
serialization, and the manifest-only source-hash boundary.  The artifact
contains no verdict, topology decision, AC claim, stable-AC claim, or negative
transport.

The bounded meaning is only this: the manifest replayably records 1,000
explicit automorphisms, their two-sided inverses, and three separately
word-realized AK(3) complexes per map, grouped by proved exact-cellular
homeomorphisms.  It proves no thickenability or nonthickenability result and no
Aut-orbit, AC, or stable-AC obstruction.

## Code-quality and integrity review

The initial review found one Important common-mode test gap: the builder and
verifier shared the spelling/key logic, so payload tampering tests alone could
not expose a systematic defect in both.  The fix added a test-local oracle with
its own edge fixtures, inverse, substitution, free reduction, cyclic peeling,
signed-generator orbit, and raw-ASCII key.  It compares all three tracks and
keys for every map and independently rebuilds the ordered 3,000-member bucket
partition.  A temporary production mutation that replaced a nontrivial free
track by the source relators made this test fail, and restoring the exact
production bytes made it pass.

**SCOPED REREVIEW: all Important findings addressed; no new Critical or
Important breakage.**

Two nonblocking Minor observations remain for the final branch review:

1. malformed non-UTF-8 manifest bytes raise `UnicodeDecodeError` rather than a
   normalized verifier assertion/CLI message; and
2. one bucket-shape `type: ignore[index]` could be replaced by a more explicit
   local type.

Fresh controller verification subsequently found three mechanical Ruff 0.16.0
findings: two import-order findings and one preference for
`itertools.pairwise`.  Those were repaired without logic changes, requiring a
deterministic JSON regeneration only because the manifest embeds the module
hash.  Scoped mathematical and quality rereviews both returned **APPROVE — no
drift**.  The independent oracle and all prior review conclusions remain in
force.

## Reviewed bytes

```text
manifest module  75a57e969800e9cb299a52885143d48fdff6ad012f9d56934d4c35697ef64076
test module      04afb9f428d17ee4bb8df3dd5f9d4a086b1910745ade20413b5e925023d933c8
manifest JSON    96b710a0fd53e56c53c42e8bcd203286d98a982a735ec2d42fa9b4b856fd816a
```
