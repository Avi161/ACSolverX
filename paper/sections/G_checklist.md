# NeurIPS Paper Checklist {#app:checklist}

1. **Claims.** Do the main claims made in the abstract and introduction accurately reflect the paper's contributions and scope?
   \answerYes{} The abstract and introduction's claims — the re-verified misprint and rescission, the stabilization negatives at stated budgets, the cap-not-binding control, and the two-representative floor structure — are each backed by a dedicated results subsection and by machine-checkable certificates (\ref{app:certs}).

2. **Limitations.** Does the paper discuss the limitations of the work performed?
   \answerYes{} A dedicated limitations section lists seven explicit items: the budget-boundedness of every negative, the length-ordered-search restriction, the RL lane's out-of-distribution scope, the two-scale reporting convention, partial certificate coverage, floor non-uniformity, and the AK(3)-specific word bank.

3. **Theory assumptions and proofs.** For all theoretical results, does the paper state the full set of assumptions and include a complete proof?
   \answerYes{} The paper proves no new theorems. Every stable-AC-equivalence or triviality claim is instead a machine-checked certificate against the acx-cert-v1 schema (\ref{app:certs}), independently verified by two separately authored programs, in place of a hand proof.

4. **Experimental result reproducibility.** Does the paper fully disclose all the information needed to reproduce the main experimental results?
   \answerYes{} \ref{app:repro} gives, per campaign, the entry point, parameters, output stream, and resume semantics; every accelerated hot path is gated against a reference implementation.

5. **Open access to data and code.** Does the paper provide open access to the data and code, with sufficient instructions to reproduce the main results?
   \answerYes{} Code, the consolidated result archives, and all certificates will be released on acceptance (withheld only during anonymized review); \ref{app:repro} documents the recipe needed to regenerate every reported number from them.

6. **Experimental setting/details.** Does the paper specify all the training/evaluation details needed to understand the results?
   \answerYes{} Node budgets, caps, worker counts, and beam-search widths and temperatures are given per campaign in \ref{sec:methods} and \ref{app:repro}.

7. **Experiment statistical significance.** Does the paper report error bars or other appropriate measures of statistical significance?
   \answerNA{} Every reported outcome is a deterministic search over a fixed, exactly enumerated set of presentations or candidates (solved counts, floor histograms, certificate check counts); there is no sampling variance to report error bars over.

8. **Experiments compute resources.** Does the paper disclose the compute used for the experiments?
   \answerYes{} \ref{app:repro} states the hardware (a 16 GB laptop; cloud CPU boxes up to 8 vCPU / 50 GB), per-attempt node budgets, and total wall-clock (about one week).

9. **Code of ethics.** Does the research conform to the NeurIPS Code of Ethics?
   \answerYes{} The work is a pure-mathematics search over group presentations; it involves no human subjects, personal data, or dual-use models.

10. **Broader impacts.** Does the paper discuss both potential positive societal impacts and negative societal impacts?
    \answerYes{} This is a pure-mathematics search on the Andrews–Curtis conjecture, with no foreseeable negative societal impact identified. The practical benefit is methodological: a rigorously verified negative and a released, deduplicated candidate archive let future attempts skip already-searched regions rather than re-spend the compute this campaign already spent.

11. **Safeguards.** Does the paper describe safeguards for the responsible release of data or models with a high risk for misuse?
    \answerNA{} The released artifacts are group-presentation data, search logs, and machine-checkable certificates; none carries a misuse risk that would require a release safeguard.

12. **Licenses.** Are the creators or original owners of assets used in the paper properly credited, and are the license and terms of use explicitly mentioned?
    \answerYes{} The Miller–Schupp benchmark presentations and related dataset infrastructure are drawn from prior work \cite{fagan2026twohump}, credited at first use and released under a CC BY 4.0 data license; the classical AC/AK/MS literature results are cited throughout.

13. **New assets.** Are new assets introduced in the paper well documented, and is the documentation provided alongside the assets?
    \answerYes{} The acx-cert-v1 certificate schema (\ref{app:certs}), the 97-word literature-grounded word bank (\ref{app:tables}), and the consolidated candidate/trial archives (\ref{app:repro}) are each documented with their schema, provenance, and generation recipe, and released alongside the code on acceptance.

14. **Crowdsourcing and research with human subjects.** For crowdsourcing experiments or research with human subjects, does the paper include the full text of instructions and screenshots, if applicable?
    \answerNA{} This work involves no crowdsourcing and no human subjects.

15. **IRB approvals.** Does the paper describe potential risks and confirm that the research received Institutional Review Board (IRB) approvals, if applicable?
    \answerNA{} No human subjects are involved in this research.
