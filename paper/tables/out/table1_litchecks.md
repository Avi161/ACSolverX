| Check | Method | Result |
|---|---|---|
| Self-test: hom-counter | CSP hom-counter vs. brute-force cross-check on 4 synthetic triple-relator systems (n≤4 generators) | PASS (4/4 match) |
| Check 1: corrected-W, all 14 deletions | SNF abelianization + Felsch coset enumeration on each single-relator deletion of corrected W | PASS (14/14 present Z) |
| Check 2: misprinted-W is broken | S3 hom-counting gate: misprinted W' deletions {7,14} disagree (B3 vs Z) while corrected-W deletions {7,12,14} all agree (Z) | PASS (gate satisfied) |
| Check 3: AK(3) is trivial | Felsch coset enumeration of the trivial subgroup (index = group order) | PASS (order 1) |
| Check 4: M3 (Wirtinger) = P25 | Reduced-word match of the Wirtinger-derived M3 transcription against P25 under commutator convention B | PASS (convention B matches) |
| Check 5: corrected-W, 3-gen reduction | SNF + S3 hom-count + coset collapse of corrected-W's (x,y,z) 3-generator reduction | PASS (presents Z) |
| Check 6: Remark 17 conjugation convention | Conjugation-convention match (g t g^-1) of r1/r2 against Remark 17 | PASS (r1, r2 both match) |
| Appendix-F 53-move replay [cert] | Replay of the printed AC' h-move sequence (Appendix F, arXiv:2408.15332v2), forward order/forward moves, from P25 | Lands exactly on AK(3) (53 steps, 54 states; cert appendixF_P25_to_AK3.json) |
| Lisitsa S2 external replay [log] | Independent replay of Zenodo 14567743's 159-transition AC path P25→AK(3) | PASS — genuine bridge; 2 data defects found in the published artifact (line 91 corrupt relator, line 81 CONJ label swapped) |

*Note: Rows 1-7 are read verbatim from results/stable_ac/ak3_stable_proof/literature_checks.json (7 entries, all pass:true). Raw JSON key names differ in spelling/case from this table's human-readable labels; see the run report for the exact key list.*

*Note: Rows 8-9 are additional re-verifications NOT drawn from literature_checks.json: row 8 is sourced from the certificate results/stable_ac/ak3_stable_proof/certs/appendixF_P25_to_AK3.json (steps count read live from the cert); row 9 is sourced from the campaign log experiments/stable_ac/ak3_stable_proof/RESULTS.md, section 'PL(partial) -- Lisitsa S2 independently validated'.*

*Note: Key-name check: this table's originally-expected key spellings ['check3_ak3_trivial', 'check4_M3_lemma11_P25', 'check5_corrected_family_Z'] do not appear verbatim in literature_checks.json; the actual keys (used above) are ['check3_AK3_trivial', 'check4_M3_to_P25', 'check5_correctedW_3gen'].*
