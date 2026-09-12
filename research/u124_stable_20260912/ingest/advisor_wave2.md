# Wave 2 stable-AC legality audit

## BLOCKERS

1. **Neither theorem supplies a U124 solution.** C11 gives one elementary
   multiplication, but no legal operation restores the required
   `u x^{kδ} v` form for another peel. The tested second multiplication does
   not do so. C12 has no hit among the 248 displayed best-table relators.
   Therefore neither an \(n\)-fold peel nor a U124 solve certificate exists in
   these artifacts.
2. **C12 cannot presently be advertised as an unconditional, effective
   campaign theorem.** Its simultaneous application of
   \(\phi\in\operatorname{Aut}(F_2)\) is C1, not an ordinary AC move. C1 is
   inherited, its cited `PROOFS.tex` is absent, and its Lemma-11 realization
   has unbounded, unmaterialized normal-closure cost. Conditional stable
   equivalence is legal if C1 is accepted; an elementary replay, ordinary-AC
   conclusion, or move bound is not.
3. **Deleting \(x\) from \(s'\) must not be treated as a free substitution or
   Tietze deletion.** It is legal, but only after expanding each deletion into
   AC moves. If \(s'=p x^\epsilon q\), temporarily change the first relator
   \(x\) by AC1/AC3 to \(q^{-1}x^{-\epsilon}q\), apply
   \(s'\leftarrow s'(q^{-1}x^{-\epsilon}q)=pq\) by AC2, and restore the first
   relator. Repeating this finite construction removes all displayed
   \(x^{\pm1}\). Without that expansion, step 4 would be a silent Tietze move.

## WARNINGS

- **Signs and orientations.** C11 uses the displayed donor sign \(-1\):
  \((uv)(gv)^{-1}=ug^{-1}\). Inverted relators require AC1, and a cyclic
  orientation requires an actual AC3 before multiplication. A cyclic
  representative is not a freely equal spelling.
- **Free versus cyclic reduction.** The cancellation of the common suffix is
  free cancellation in the displayed product. The orientation census is over
  cyclic rotations/inversions; its shorter representatives therefore include
  the corresponding AC1/AC3 preconditioning and must not be presented as the
  same literal product.
- **Raw length versus \(\mu\).** The displayed Q peel has
  `q_length_drops = 0` and raises raw pair length in every checked case. Some
  orientation-peels shorten the already inflated post-peel pair, but the
  audited \(Q_{2,\pm1}\) remainder `YXyxYYXyx` raises
  \(\mu:14\to18\). Neither that raw shortening nor a longest-\(x\)-run drop is
  a well-founded descent.
- **Round trips.** The orientation output contains undo/return cases as well
  as new spellings. A second multiplication must be checked against the
  original pair and its full Aut orbit before it is called progress.
- **Aut versus ordinary AC.** Whitehead reduction and `aut_min_len` are
  calculations in an ambient automorphism orbit. They are not ordinary
  Andrews--Curtis paths. C1 licenses simultaneous ambient automorphisms only
  stably and only under its trivial-presentation hypothesis; the unstable
  pairwise ambient principle is unavailable.
- **C1 is non-effective.** Even when cited legally, it proves existence rather
  than the bounded or replayable move sequence claimed by an elementary
  certificate.
- **Step 4's abelianization argument is sound.** After normalizing the first
  row to \((1,0)\), determinant \(\pm1\) forces the companion's \(y\)-exponent
  to be \(\pm1\). Deleting \(x\)'s multiplies by conjugates of \(x^{\pm1}\), so
  that exponent is unchanged. A freely reduced word in the one-generator
  free group \(\langle y\rangle\) is therefore exactly \(y^{\pm1}\), not an
  arbitrary residual power.
- **The primitive census is narrower than the pair problem.** It checks the
  248 displayed relators and two products from each stored orientation.
  `elementary_ac2_scan.json` enumerates independently rotated depth-1 AC2
  children but does not test them for primitivity. Thus a primitive relator
  elsewhere in the pair-\(\mu\) orbit, or even in that larger depth-1 set, is
  not excluded.
- **The reported 0/248 products is only a recognizer report.** The code
  serializes the two cyclically reduced stored-orientation products per row,
  but `primitive_hits` counts only direct relators; there is no separate
  product-hit aggregate or assertion in the summary. The report is not an
  obstruction and should be given a dedicated guarded aggregate before being
  treated as independently replayed census evidence.

## ALLOWED CLAIMS

- For freely reduced \(R_1=gv\), \(R_2=uv\), the replacement
  \(R_2\leftarrow R_2R_1^{-1}\) freely reduces to \(ug^{-1}\). This is an
  ordinary elementary AC1--AC3 construction once any chosen signs and cyclic
  orientations are displayed.
- For the Q spelling,
  \(R_1=g x^\delta v\), \(R_2=u x^{n\delta}v\), the same multiplication gives
  \(u x^{(n-1)\delta}g^{-1}
   =u x^{(n-1)\delta}v[y^{-1},x^{-1}]\).
  The implementation checks this for \(n=2,\ldots,8\) and both signs, 14/14.
- Repeating the same unconjugated multiplication does not restore the Q
  family, and the displayed first peel never lowers raw total length in those
  14 cases.
- Conditional on C1, a primitive relator in a balanced trivial-group pair
  with determinant \(\pm1\) is a stable-AC finish line. After the conditional
  ambient automorphism, the remaining generator deletion is a finite
  elementary AC1+AC2+AC3 procedure and abelianization leaves \(y^{\pm1}\).
- The implemented Whitehead recognizer reports no primitive word among the
  248 displayed best-table relators; the minimum-length histogram starts at
  5. A Whitehead minimum of 5 is a negative result for the length-1
  primitivity criterion, not a partial C12 hit.
- The depth-1 scan proves only its stated bounded fact: 44,016 enumerated
  children have no strict cyclic-total-length drop and no new
  one-occurrence/two-block hit.

## FORBIDDEN CLAIMS

- U124 is solved, removed, or supplied with a stable-AC certificate.
- An \(n\)-fold Q peel is available, or the displayed peel inducts on \(n\).
- A longest-\(x\)-run drop or post-inflation raw-length drop is well-founded
  progress, or is a drop in \(\mu\).
- Whitehead minimum 5 is “almost primitive,” is a C12 hit, or can be rounded
  down to length 1.
- The 0/248 direct-relator or stored-product report obstructs primitive
  relators after other AC/stable-AC moves.
- The depth-1 miss obstructs a longer ordinary or stable route.
- Any ambient automorphism of a balanced pair is an ordinary AC operation, or
  the unstable ambient automorphism principle may be used.
- C1 currently provides a bounded, expanded, independently replayable
  realization.
- Cyclic reduction, an Aut-orbit identification, or deletion of a displayed
  generator may be used as an unrecorded free move.

## VERDICT ON C11

**APPROVE.** The general common-suffix identity and the Q specialization have
the correct donor sign and are elementary AC2 after any explicitly recorded
AC1/AC3 orientation. The commutator factorization
\(g^{-1}=v[y^{-1},x^{-1}]\) is correct. The catalogue also correctly states
that the first peel does not shorten the checked Q pairs, that the same
unconjugated multiplication does not iterate, and that the \(n\)-fold finish
is counterfactual only. It is an identity theorem, not a descent theorem or a
U124 solution.

## VERDICT ON C12

**REVISE.** The mathematical finish is valid conditional on C1, and
abelianization really does force the final freely reduced one-generator word
to be \(y^{\pm1}\). Step 4 is elementary AC1+AC2+AC3, but the catalogue should
display the conjugated-donor sequence above and reorder steps 1--2 so that C1
first transports the pair to \((\phi(r),\phi(s))\), after which AC1/AC3
normalizes \(\phi(r)\) to \(x\). Keep “conditional on C1” and
“non-effective” in the theorem statement, and describe 0/248 only as the
implemented recognizer report; the missing guarded product aggregate and
unscanned oriented AC2 children prevent any broader negative conclusion.

## NEXT LEGAL EXPERIMENTS

1. Reconstruct and independently audit the C1 Nielsen-generator realization
   from the cited source, recording every Lemma-11 use as non-effective unless
   its normal-closure witness is materialized.
2. Add a symbolic AC1+AC2+AC3 replay for C12 step 4, with both
   \(x\)-occurrence signs and a terminal check of \((x,y^{\pm1})\).
3. Run primitivity on every relator produced by the already enumerated 44,016
   oriented depth-1 AC2 children and emit a Whitehead witness for any hit; a
   miss remains only a bounded report.
4. Add separate guarded totals and witness replay for the 248 stored-product
   primitivity checks.
5. Pursue Q continuations only when they provide a displayed conjugator
   identity that restores the peelable family or directly reaches a positive
   finish line (primitive relator, legal \(\mu\le12\) endpoint, or explicit
   cyclic-complement witness); reject mere run-length heuristics and
   round trips.
