# A double-transposition quotient closes the known eleven-direction span

## Status

An eleventh exact homogeneous direction lies outside the previous
ten-dimensional span and defeats all thirteen Result 156 bits.  A new
four-point action supplies two further covectors.  The resulting fifteen
functionals obstruct every integer coefficient class in the known
eleven-direction affine family.  The full syzygy module and the original
Andrews--Curtis problems remain open.

## 1. Exact direction

With $T=t^{-1}$, start the $L_0$ component with

\[
m_0=e_{TTcttt}+e_{cTcTct}.
\tag{1}
\]

In the forest basis $A=t,B=X,G=U^{-1}t^{-1}$, exact Stallings-cover
rewriting gives

\[
\begin{aligned}
ctcTTTctcTct&\xrightarrow{\ gAB\ }ctcTTct,\\
cTTcttcTTcttt&\xrightarrow{\ BgAbgaaGaG\ }ctcTcTTct,\\
ctcTTTcttcTTcttt&\xrightarrow{\ gAB\ }ctcTctcTTcttt,\\
ctcTTTTcttcTTcttt&\xrightarrow{\ gABgAbgaaBgAgAgaB\ }ctcTcTctcTTcttt,\\
cTTctcTct&\xrightarrow{\ BgAbGb\ }cTct,\\
ctcTTTTctcTct&\xrightarrow{\ gABgAbAgABaGbA\ }tcTTcttt.
\end{aligned}
\tag{2}
\]

Their signed edge flow reconstructs a 44-entry syzygy $m$ with
\(\ell^1(m)=55\) and

\[
\sum_{i=0}^4L_i m_i=0.
\tag{3}
\]

The component-image statistics are

\[
(12,12),(0,0),(22,30),(30,36),(30,36).
\tag{4}
\]

The known direction rank rises from ten to eleven modulo two.  Adding $m$
to the canonical lift gives residual length 1696, kernel length 228, wedge
support 515, and wedge coefficient norm 956.  All thirteen Result 156 bits
vanish.

## 2. New four-point quotient

On four points take

\[
c=(1\ 2),\qquad t=(0\ 1)(2\ 3).
\tag{5}
\]

In wedge basis $(01,02,03,12,13,23)$, the operator image over
\(\mathbb F_2\) has rank four.  Its annihilator has basis

\[
\eta_0=(0,0,1,1,0,0),\qquad
\eta_1=(1,1,0,0,1,1).
\tag{6}
\]

The eleventh residual maps to

\[
(-29,-6,-3,20,-14,19).
\tag{7}
\]

The two covector values are $(1,0)$ modulo two, and adjoining (7) raises
the rank from four to five.

## 3. Complete coefficient closure

The fifteen obstruction coordinates are integer-valued quadratic functions
of eleven coefficients and have period dividing four modulo two.  The exact
certificate determines them from

\[
1+2\cdot11+\binom{11}{2}=78
\tag{8}
\]

replays and validates them at 66 independent points.  Evaluation on all

\[
4^{11}=4194304
\tag{9}
\]

classes finds no zero row.  The table hash is

\[
\texttt{297fcafd277a752eff9b26b2de69f5de4540eebad8c76c31356cd8d478651912}.
\tag{10}
\]

Thus every integer combination in the known eleven-dimensional affine
family is degree-two obstructed.

## 4. Frontier and certificate

Balanced two-source $L_0$ flows continue to produce new independent
directions at depth six.  The next target remains a global syndrome
automaton, or a twelfth zero-syndrome direction demonstrating another
missing quotient.

The checker

\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_eleven\_direction\_obstruction\_certificate.py}
\]

reconstructs (1)--(3), verifies rank eleven and (5)--(7), validates the
quadratic model, and exhausts (9) with hash (10).
