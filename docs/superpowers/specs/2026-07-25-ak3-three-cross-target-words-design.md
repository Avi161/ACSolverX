# AK(3) three-cross target-word classification design

Date: 2026-07-25

## Objective

Classify all length-three target words over the two non-\(R\) slots
\(\{B,D\}\). Combine the existing one-way theorem, the strict alternating
three-cross theorem, and new one-switch arguments to identify every
closed branch and every surviving killer equation.

## Classification

There are eight target words:

| target word | mechanism |
|---|---|
| `BBB`, `DDD` | existing one-way theorem |
| `BBD` | original-\(D\) HNN quotient if the third target is deleted; one-way absorption if its source is deleted |
| `BDD` | third target has even \(z\)-exponent; deleting its source reduces to the first one-way event |
| `DDB` | third source has even \(z\)-exponent; quotient by original \(B\) identifies the survivor with \(D_p^{\pm1}\) |
| `DBB` | six-row killer frontier |
| `BDB` | closed by the strict alternating theorem |
| `DBD` | six-row killer frontier from the strict alternating theorem |

Here the letters record the target slot at each event.

## New closed cases

For `BBD`, quotient by the original \(D\). The first two events vanish,
the final target is a conjugate of \(B^\theta\), HNN conjugacy gives

\[
[e]_G=t^{-n}(xt)x^n,
\qquad
n=\epsilon+\eta+\theta,
\]

and evaluation makes the survivor a conjugate of
\(D(e)^{-\theta}\), hence of \(D_p^{\pm1}\).

For `BDD`, the third target has exponent
\(-\eta-\theta\in\{0,\pm2\}\). If the source is deleted, both later
source factors evaluate to one and the first one-way event remains.

For `DDB`, the twice-modified source has even exponent and cannot be
deleted. If the final target is deleted, quotient by the original \(B\)
sets \(z=p\), erases the first two events, and makes
\(p^{-1}e\) a conjugate of \(D_p^{\theta\delta}\). Evaluation of the final
target then makes the actual survivor a conjugate of \(D_p^\delta\).

## The `DBB` killer corridor

Write the source signs as \(\epsilon,\eta,\theta\). The target exponent is

\[
\sigma_z(B_2)=-1-\epsilon(\eta+\theta).
\]

The all-positive and all-negative rows have absolute exponent \(3\); the
other six have absolute exponent \(1\). Torus weight again forces
\(\operatorname{wt}(e)\in\{5,7,9\}\), and the evaluated survivor
\(D_1[e]\) has weight \(\pm1\). It is a killer because the endpoint
presentation is trivial.

The literal untwisted signed-seam replay has the same exact counts as the
strict `DBD` corridor:

\[
16,\quad416,\quad522,\quad69,
\]

and one evaluated survivor class \(D_p^{\pm1}\).

## Result boundary

Together with the earlier theorems, this classifies every length-three
target word. It does not close the arbitrary bridge/twist geometry in the
two killer words `DBB` and `DBD`. It also does not cover four or more
events, restoration failure, changed \(R\), or a multi-\(z\) eliminator.

AK(3) remains open.
