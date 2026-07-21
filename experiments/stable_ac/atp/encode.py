"""Encode Andrews-Curtis triviality search as Prover9 problems.

Faithful transcription of Alexei Lisitsa's IG ("implicational, ground")
encoding, on the REDUCED term rewriting system ``rACT2``, dimension n = 2.

PRIMARY SOURCE (read in full before touching this file):
  literature/txt/lisitsa_parametric_ac_aitp2023.txt              (AITP 2023 abstract)
  literature/txt/lisitsa_parametric_ac_simplifications_ii.txt    (extended version -- has the encoding, section 1)

Why IG, not EG/EN/IN
---------------------
The paper offers four translations of the same rewrite system into first-order
logic -- EG ("equational ground"), EN ("equational non-ground"), IG
("implicational ground"), IN ("implicational non-ground") -- and reports
results for all four (simplifications_ii.txt lines 156-236). IG is the one
used for the headline result:

    "These trivializations were found by automated theorem proving using IG
    encoding and Prover9 prover." (simplifications_ii.txt line 177, backing
    Proposition 5 / Table 1: M S_n(w*) trivialized for n = 3, 4, 5, 6, the
    paper's primary reported table, with times from 0.05s (n=2) to 10637s
    (n=6).)

IG is also the encoding that produces a DIRECT proof object Prover9 can dump
and inspect step-by-step (the R(f(...)) chain is exactly the trace of AC-moves
applied) -- EN's proof for n=7 needed 892 hand-delemmatized macrosteps before
any move sequence could even be read off (line 217-221), and IN was reported
as an *alternative*/optimization angle explored after IG, for a restricted
target (line 222-236), not as the paper's strongest result. IG only failed
once, at n=7 (line 204), where EN and IN were used as fallbacks -- out of
scope here; this module implements IG only, per ESCAPE_PLAN.md T6's
"implement the ONE the paper reports strongest results with."

The rewrite system, transcribed verbatim (simplifications_ii.txt lines 88-100,
115-125; x, y range over presentation-slot terms, a_i over the alphabet A):

    ACT2 (full system):
      R1L  f(x, y) -> f(r(x), y))
      R1R  f(x, y) -> f(x, r(y))
      R2L  f(x, y) -> f(x . y, y)
      R2R  f(x, y) -> f(x, y . x)
      R3Li f(x, y) -> f((a_i . x) . r(a_i), y)   for a_i in A, i = 1, 2
      R3Ri f(x, y) -> f(x, (a_i . y) . r(a_i))   for a_i in A, i = 1, 2

    rACT2 (reduced system -- Proposition 1: rACT2 and ACT2 have the SAME
    transitive closure modulo the group axioms, so dropping R1R/R3Ri loses no
    reachability):
      R1L  f(x, y) -> f(r(x), y))
      R2L  f(x, y) -> f(x . y, y)
      R2R  f(x, y) -> f(x, y . x)
      R3Li f(x, y) -> f((a_i . x) . r(a_i), y)   for a_i in A, i = 1, 2

The IG translation (section 1.3, lines 145-152) marks reachability with a unary
predicate R and turns each rewrite rule into a Prover9 implication:

      I-R1L   R(f(x,y)) -> R(f(r(x),y)))
      I-R2L   R(f(x,y)) -> R(f(x . y, y))
      I-R2R   R(f(x,y)) -> R(f(x, y . x))
      I-R3Li  R(f(x,y)) -> R(f((a_i . x) . r(a_i), y))   for a_i in A, i = 1, 2

    Proposition 4: for ground t1, t2: t1 ->*ACT2/G t2  iff  IACT2 |- R(t1) -> R(t2).

We set t1 = the input presentation, t2 = f(a, b) (the trivial presentation
<a,b | a,b>), assert R(t1) as a fact, and ask Prover9 to prove R(t2) as the
goal -- Prover9 internally negates the goal and searches for a refutation, so
what actually gets searched is exactly the forward chain of R3Li/R2L/R2R/R1L
applications from t1 to t2, i.e. an AC-move sequence.

Symbol scheme (verified against the installed Prover9 2009-11A binary, see
experiments/stable_ac/atp/README.md "Prover9 syntax notes")
------------------------------------------------------------
Prover9's default parser convention: identifiers starting with one of
``u,v,w,x,y,z`` (lowercase) are VARIABLES; everything else is a
constant/function/predicate symbol. The paper's own rule schema uses ``x,y``
as the meta-variables ranging over presentation slots -- that convention is
free, so we keep ``x`` and ``y`` as Prover9 variables (matching the paper's
notation exactly) and rename the *generators themselves* to ``a`` and ``b``
(the paper's own letters for its worked M_n(w) = <a,b|...> family) to avoid
colliding with Prover9's reserved variable-letter set. The repo's alphabet is
{x, y, X, Y} (lowercase = generator, uppercase = its inverse); this module
maps repo-``x`` -> Prover9-``a``, repo-``y`` -> Prover9-``b`` and their
uppercase inverses to ``i(a)``/``i(b)``. This mapping is internal bookkeeping
only -- it changes no semantics, and is documented so a proof trace can be
read back against the original presentation.

Group theory (TG) is axiomatized with the standard 5-axiom equational
presentation (associativity + two-sided identity + two-sided inverse); this
is the same axiom set used across Lisitsa's published Prover9 group-theory
encodings and lets Prover9's paramodulation freely reduce words.
"""

ENCODING = "IG"  # implicational, ground (Lisitsa, rACT2) -- see module docstring

# repo convention: lowercase = generator, uppercase = its inverse (envs/ac_moves.py
# style). Prover9 reserves u,v,w,x,y,z as variables by default, and the paper's own
# rewrite-rule meta-variables ARE x,y -- so generators are renamed a,b (the paper's
# own M_n(w) generator names) rather than kept as x,y.
_GEN_TO_PROVER9 = {"x": "a", "y": "b"}

TG_AXIOMS = (
    "(x * y) * z = x * (y * z).",   # associativity
    "e * x = x.",                    # left identity
    "x * e = x.",                    # right identity
    "i(x) * x = e.",                 # left inverse
    "x * i(x) = e.",                 # right inverse
)

# rACT2 as IG implications (I-R1L, I-R2L, I-R2R, I-R3Li for i=1,2), transcribed
# from simplifications_ii.txt lines 148-151. Each entry is
# (paper_rule_label, prover9_clause_text) -- the label is emitted as a Prover9
# ``# label(...)`` annotation so a proof trace can be read back against the
# paper's own rule names (Prover9 threads the label onto the clausified axiom
# and onto any hyper-resolution step that fires it directly; see README.md
# "Reading a proof trace").
RULES = (
    ("AC_I_R1L", "R(f(x,y)) -> R(f(i(x),y))"),
    ("AC_I_R2L", "R(f(x,y)) -> R(f(x*y,y))"),
    ("AC_I_R2R", "R(f(x,y)) -> R(f(x,y*x))"),
    ("AC_I_R3L_a", "R(f(x,y)) -> R(f((a*x)*i(a),y))"),
    ("AC_I_R3L_b", "R(f(x,y)) -> R(f((b*x)*i(b),y))"),
)


def word_to_term(word):
    """repo-convention word (chars in x, X, y, Z... i.e. x/y/X/Y) -> Prover9 term.

    Empty word -> the identity constant ``e``. Letters multiply left-to-right in
    the order they appear in ``word`` (the word IS the product); the term is
    built as a right-fold, which the associativity axiom makes equal in
    Prover9's eyes to any other bracketing of the same left-to-right product.
    """
    if not word:
        return "e"
    parts = []
    for ch in word:
        gen = _GEN_TO_PROVER9.get(ch.lower())
        if gen is None:
            raise ValueError(f"unsupported letter {ch!r} in word {word!r}; "
                              f"only x, X, y, Y are supported (2-generator alphabet)")
        parts.append(f"i({gen})" if ch.isupper() else gen)
    term = parts[-1]
    for p in reversed(parts[:-1]):
        term = f"{p}*({term})"
    return term


def build_ig_problem(name, r1, r2, timeout_s=600):
    """Return Prover9 input text for "presentation (r1, r2) is AC-trivializable".

    Fact: R(f(term(r1), term(r2))).  Goal: R(f(a,b))  (the trivial presentation
    <a,b|a,b> -- the paper's own chosen normal form, simplifications_ii.txt
    line 60: "<x1,...,xn ; x1,...,xn>"). ``timeout_s`` is written into the file
    as ``assign(max_seconds, ...)`` so Prover9 exits cleanly and reports
    ``SEARCH FAILED`` / exit code 4 on its own account if it can't prove the
    goal in time; ``run_prover9.py`` additionally wraps the process in a
    subprocess-level timeout as a backstop.
    """
    t1 = word_to_term(r1)
    t2 = word_to_term(r2)
    lines = [
        "% Prover9 IG (implicational, ground) encoding of AC-triviality.",
        f"% presentation: {name}  r1={r1!r}  r2={r2!r}",
        "% Lisitsa rACT2 rules I-R1L / I-R2L / I-R2R / I-R3La / I-R3Lb "
        "(lisitsa_parametric_ac_simplifications_ii.txt sec 1.1/1.3).",
        "% repo generator x -> Prover9 constant a, repo generator y -> Prover9 "
        "constant b (Prover9 reserves x,y,z,u,v,w as variables by default; "
        "the paper's own f(x,y) rule schema keeps x,y as those variables).",
        "% goal: reach the trivial presentation <a,b|a,b>, i.e. R(f(a,b)).",
        "",
        f"assign(max_seconds, {int(timeout_s)}).",
        "",
        "formulas(assumptions).",
        "",
    ]
    for ax in TG_AXIOMS:
        lines.append(f"  {ax}")
    lines.append("")
    for label, rule in RULES:
        lines.append(f"  {rule} # label({label}).")
    lines.append("")
    lines.append(f"  R(f({t1}, {t2})).")
    lines.append("")
    lines.append("end_of_list.")
    lines.append("")
    lines.append("formulas(goals).")
    lines.append("  R(f(a,b)).")
    lines.append("end_of_list.")
    lines.append("")
    return "\n".join(lines)
