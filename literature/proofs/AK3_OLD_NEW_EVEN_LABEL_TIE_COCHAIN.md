# Even transported-label fibers and the old--new tie cochain

## Status and scope

This note proves that every transported-label fiber of the full
collision-aggregated 84-token mask \(T=b_{n,d}\) has even cardinality.
Consequently every strict transported-label contribution to the global
\(<_\rho\)-rank vanishes.  The remaining rank is exactly an
equal-label chronology prefix.  It admits a canonical normal form using
42 same-label chronology chords and is supported on at most 252 edges of
the two-component module forest.

Together with the forest-overlap theorem, this removes all strict shortlex
comparisons from the two surviving \(P\)-rays, the six-family \(C\)-chain,
and the three paired \(Q\)-rectangles.  It does not evaluate the remaining
equal-label chord incidences or the boundary-distance parities.  Thus it
does not prove the endpoint identities, positive-chamber covariance, the
period-two lift, AK(3), stable Andrews--Curtis, or Andrews--Curtis.

## 1. Collision-first label pushforward

Let \(\mathscr P\) be the fixed decorated-token universe for the literal
residual AST.  It consists of:

1. the fixed-literal core events, with their literal AST positions and
   final Schreier labels; and
2. correction coordinates \((o,v)\), where \(o\) is a correction
   occurrence and \(v\in X=Q/\langle c\rangle\) is canonical.

For a correction coordinate put

\[
 \tau_o(v)=\operatorname{cvert}(q_ov).
 \tag{1.1}
\]

Here \(q_o\) is the literal raw occurrence prefix.  A terminal \(c\) is
retained until the displayed \(\operatorname{cvert}\) operation.

Let \(C=B+D\) be a complete current, with \(D\) an integral homogeneous
correction direction.  First canonicalize every raw module word in \(X\)
and sum all integral coefficients at each \((s,v)\).  Only then define the
correction activity

\[
 a_C(o,v)=C_{s_o}(v)\pmod2.
 \tag{1.2}
\]

Equal canonical module fibers have the same transported label at a fixed
occurrence by the bound source semantics, so (1.1)--(1.2) define a genuine
pushforward.  For a canonical label \(\ell\), put

\[
 P_C(\ell)
 :=\sum_{\substack{o,v\\\tau_o(v)=\ell}}a_C(o,v)
 \in\mathbb F_2.
 \tag{1.3}
\]

This sum ranges over the collision-aggregated coordinates.  It does not
range over virtual provenance rows.

Let

\[
 F(\ell)
 :=\#\{\text{fixed-literal core events of label }\ell\}\pmod2.
 \tag{1.4}
\]

The fixed value \(F\) depends only on the literal residual AST, not on
\(C\).

## 2. The complete endpoint label equation

**Lemma 2.1 (fixed plus correction parity).** If the residual
\(\mathcal R(C)\) has zero integral linear Schreier coordinate, then

\[
 \boxed{F(\ell)+P_C(\ell)=0}
 \qquad\text{for every label }\ell.
 \tag{2.1}
\]

### Proof

Expand every transported correction atom by the exact raw bridge.  Its
event-label word is

\[
 (\alpha_1,\ldots,\alpha_m,\tau_o(v),
   \alpha_m,\ldots,\alpha_1).
 \tag{2.2}
\]

The same statement holds for a negative atom after reversal and sign
inversion.  Reducing the integral linear Schreier coordinate modulo two
removes signs.  Every mirror label \(\alpha_h\) occurs twice and therefore
vanishes, leaving exactly the central label \(\tau_o(v)\) for each
coefficient copy.  Integral copies at a common canonical coordinate reduce
to the activity (1.2).  The fixed literal events contribute (1.4).

Thus the coefficient of \(e_\ell\) in the mod-two reduction of the linear
Schreier coordinate is precisely \(F(\ell)+P_C(\ell)\).  The integral
coordinate is zero, so every displayed coefficient is zero.  \(\square\)

The fixed term in (2.1) is essential.  Zero linear coordinate does not
assert \(P_C(\ell)=0\) for one endpoint.

## 3. Even fibers of the actual \(b\)-mask

Let \(C\) and \(C'\) be the two complete endpoint currents whose activity
difference is \(b=b_{n,d}\).  Both have the form \(B+D\) with integral
homogeneous \(D\), so both residuals have zero linear coordinate.  They use
the same literal residual AST and hence the same fixed function \(F\).

Let \(T\) be the actual active decorated-coordinate support of their
difference.  Activity is added only after integral collision aggregation:

\[
 T(o,v)=a_{C'}(o,v)+a_C(o,v).
 \tag{3.1}
\]

The fixed coordinates cancel and do not occur in \(T\).  In the present
period-two mask, \(T\) consists of twelve slot-zero tokens and two
occurrence copies of each of the 36 odd path fibers, hence

\[
 |T|=84.
 \tag{3.2}
\]

For a label \(\ell\), define its active decorated-token multiplicity

\[
 m_T(\ell)
 :=\#\{t\in T:\lambda(t)=\ell\}\pmod2.
 \tag{3.3}
\]

Equations (2.1) and (3.1) give

\[
\begin{aligned}
 m_T(\ell)
 &=P_{C'}(\ell)+P_C(\ell)\\
 &=F(\ell)+F(\ell)=0.
\end{aligned}
\tag{3.4}
\]

Therefore:

**Theorem 3.1 (even transported-label fibers).**

\[
 \boxed{m_T(\ell)=0\quad\text{for every canonical label }\ell.}
 \tag{3.5}
\]

This is parity of active decorated token coordinates.  It is not a claim
about the number of virtual rows or an unaggregated integral provenance
sum.

If

\[
 \Lambda(T)=\{\lambda(t):t\in T\},
 \tag{3.6}
\]

then every nonempty fiber has size at least two.  Hence

\[
 \boxed{|\Lambda(T)|\le 42.}
 \tag{3.7}
\]

## 4. Elimination of every strict-label rank

Recall that \(<_\rho\) is decreasing transported-label shortlex, with
literal chronology \(<_\chi\) as its tie-breaker.  For any decorated
coordinate \(x\),

\[
\begin{aligned}
 R_T^\rho(x)
 &=\#\{t\in T:t<_\rho x\}\pmod2\\
 &=\sum_{\ell>_{\rm sl}\lambda(x)}m_T(\ell)
   +\#\{t\in T:\lambda(t)=\lambda(x),\ t<_\chi x\}\pmod2.
\end{aligned}
\tag{4.1}
\]

Theorem 3.1 kills the first term label fiber by label fiber.  Define

\[
 H_T(x)
 :=\#\{t\in T:\lambda(t)=\lambda(x),\ t<_\chi x\}\pmod2.
 \tag{4.2}
\]

Then

\[
 \boxed{R_T^\rho(x)=H_T(x).}
 \tag{4.3}
\]

Both orders in (4.1) are strict.  If \(x\in T\), its diagonal token is
not earlier than itself, so (4.3) requires no extra membership correction.
The complete membership correction remains in the separate
\(\beta_E\)-term of the forest-overlap theorem.

Equation (4.3) eliminates every strict transported-label comparison.
Only exact equality of final canonical labels and literal chronology within
that equality fiber remain.

## 5. The 42-chord normal form

For each \(\ell\in\Lambda(T)\), list its token fiber in chronology order:

\[
 t_{\ell,1}<_\chi t_{\ell,2}<_\chi\cdots<_\chi
 t_{\ell,2m_\ell}.
 \tag{5.1}
\]

The length is even by Theorem 3.1.  Pair consecutive tokens

\[
 (t_{\ell,1},t_{\ell,2}),\ldots,
 (t_{\ell,2m_\ell-1},t_{\ell,2m_\ell}).
 \tag{5.2}
\]

There are exactly

\[
 \sum_\ell m_\ell=\frac{|T|}{2}=42
 \tag{5.3}
\]

such same-label pairs.  For any decorated coordinate \(x\),

\[
 \boxed{
 H_T(x)=
 \sum_{\ell}\sum_{j=1}^{m_\ell}
 [\lambda(x)=\ell]\,
 [t_{\ell,2j-1}<_\chi x\le_\chi t_{\ell,2j}].}
 \tag{5.4}
\]

Indeed, inside one label fiber the parity of the strict chronology prefix
toggles at the first token of each pair and toggles back immediately after
the second.  The half-open convention in (5.4) excludes the first endpoint
and includes the second, exactly matching the strict diagonal rule.

Thus the former global rank is a 42-chord same-label incidence function.
No shortlex inequality survives in (5.4).

## 6. Exact forest endpoint prefixes

Use the stored oriented edges

\[
\begin{aligned}
 E_2(v)&:Bv\longrightarrow v,\\
 E_3(v)&:tv\longrightarrow U^{-1}v,\\
 E_4(v)&:v\longrightarrow tv.
\end{aligned}
\tag{6.1}
\]

The two occurrences of each forest slot have the following literal raw
prefixes:

\[
\begin{array}{c|c|c|c|c}
 s&o_s^+&q_{o_s^+}&o_s^-&q_{o_s^-}\\ \hline
 2&1&1&6&B=\texttt{ctcTcTctc}\\
 3&9&U^{-1}=Gt=\texttt{ctcTTctt}&14&t\\
 4&15&t&16&1.
\end{array}
\tag{6.2}
\]

Consequently the positive and negative transported labels are exactly the
head and tail vertices of the stored edge:

\[
\begin{array}{c|c|c}
 s&\lambda(\iota_{o_s^+}(v))
   &\lambda(\iota_{o_s^-}(v))\\ \hline
 2&\operatorname{cvert}(v)&\operatorname{cvert}(Bv)\\
 3&\operatorname{cvert}(U^{-1}v)&\operatorname{cvert}(tv)\\
 4&\operatorname{cvert}(tv)&\operatorname{cvert}(v).
\end{array}
\tag{6.3}
\]

This endpoint statement concerns transported labels.  The decorated
coordinates and their positive/decreasing occurrence chronologies remain
distinct and are retained by \(H_T\).

## 7. The finite tie cochain

Define the edge tie cochain

\[
 \tau_T(E_s(v))
 :=H_T(\iota_{o_s^+}(v))
  +H_T(\iota_{o_s^-}(v)).
 \tag{7.1}
\]

The old global rank cochain was

\[
 r_T(E_s(v))
 =\sum_{o:s_o=s}R_T^\rho(\iota_o(v)).
 \tag{7.2}
\]

Equations (4.3) and (7.1) prove the exact collapse

\[
 \boxed{r_T=\tau_T.}
 \tag{7.3}
\]

If \(\tau_T(E_s(v))\ne0\), at least one endpoint label in (6.3) belongs
to \(\Lambda(T)\).  Since the free labelled \(K\)-orbit graph is a
six-regular Cayley tree, this gives

\[
 \boxed{
 \operatorname{supp}(\tau_T)
 \subseteq
 \bigcup_{\ell\in\Lambda(T)}\operatorname{Star}(\ell).}
 \tag{7.4}
\]

Each star has six edges.  Combining (7.4) with (3.7) yields the uniform
bound

\[
 \boxed{|\operatorname{supp}(\tau_T)|\le
        6|\Lambda(T)|\le252.}
 \tag{7.5}
\]

Duplicate stars or parity cancellation can only lower this number.  The
bound is not an evaluation of the surviving cochain.

Substituting (5.4) into (7.1) gives a fully explicit description: for each
stored edge, test its two decorated occurrence coordinates against the
42 same-label half-open chronology chords.  There are no order comparisons
between unequal labels.

## 8. Consequence for the exact AK3 endpoint target

Let \(\beta_E\) be the de-occurrenced, collision-first parity edge current
of \(b\).  The forest-overlap theorem gave

\[
 \omega_T(e)=\beta_E(e)+r_T(e).
 \tag{8.1}
\]

Equation (7.3) sharpens this to

\[
 \boxed{\omega_T(e)=\beta_E(e)+\tau_T(e).}
 \tag{8.2}
\]

For the two surviving \(P\)-ray chain \(C_P(h)\) and the three paired
\(Q\)-rectangle chains \(C_Q^{\nu,\nu'}(h)\), one therefore has

\[
 \boxed{
 E_P(h)=
 \langle C_P(h),\beta_E\rangle_E+
 \langle C_P(h),\tau_T\rangle,}
 \tag{8.3}
\]

and

\[
 \boxed{
 E_Q(h)=
 \sum_{(\nu,\nu')\in\{(1,5),(2,3),(4,6)\}}
 \left(
 \langle C_Q^{\nu,\nu'}(h),\beta_E\rangle_E+
 \langle C_Q^{\nu,\nu'}(h),\tau_T\rangle
 \right).}
\tag{8.4}
\]

For the six-family \(C\)-chain, put

\[
 C_C:=\sum_{\nu=1}^6
 [x^C_{\nu,0},x^C_{\nu,1}].
 \tag{8.5}
\]

Then the same identity gives

\[
 \boxed{
 E_C=\langle C_C,\beta_E\rangle_E
     +\langle C_C,\tau_T\rangle.}
 \tag{8.6}
\]

The first terms are the mod-four boundary-distance pairings already proved.
The second terms are supported on the finite star neighborhood (7.4) and
are decided solely by canonical-label equality and chronology incidence in
(5.4).  Strict transported-label shortlex comparison has disappeared from
the AK3 old--new endpoint problem.

The remaining exact theorem obligation is to evaluate these
boundary-distance and same-label chord incidences for all admissible
powered \(P,C,Q\) endpoints.  The separate finite old terms still require

\[
 E_{\rm fixed}=0,\qquad E_{\rm base}=0,\qquad
 E_{\rm singleton}=1.
 \tag{8.7}
\]

Neither tree geometry nor even label fibers alone force any of these
parities to vanish.
