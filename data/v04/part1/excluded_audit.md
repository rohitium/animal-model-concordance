# Audit of verifier exclusions

Run 2026-09-14 by `analysis/v04/e4_audit_excluded.py`, adjudicator anthropic/claude-sonnet-5, seed 20260915.

- excluded results: 1811; audited: 59 in 56 studies
- adjudicator decisions: {'keep': 7, 'drop': 44, 'keep-with-correction': 8}
- false-exclusion rate: 15/59 = 25% (exact 95% CI 15%–38%)
- decision rule (set before the run): upper bound above 10%: adjudicate every excluded result

## Wrongly excluded (kept by the adjudicator)

- 22164278-5: miR-152 is down regulated in both mouse and human neuroblastoma. | verifier said: own_result: no — The human finding is cited from other studies and the statement reflects overlap between the authors' mouse data and published human datasets.
- 24748377-7: Long-term treatment with olaparib significantly suppressed tumor development in Brca1-deficient but not in Brca1-wild type tumors, similar t | verifier said: is_correspondence: no — The text makes a qualitative comparison to patient PFS but gives no concordance/translation metric or rate.
- 25814248-0: Therapeutic interventions reported to reduce albuminuria and improve renal pathology in animal models of diabetic kidney disease have shown  | verifier said: own_result: no — The statement cites Deb et al., 2010, so it is reporting results from other studies, not the paper's own original data.
- 16493187-5: Nifedipine, a negative compound, produced an 11% increase in QTcF interval in conscious dogs. | verifier said: is_correspondence: no — The 11% is an animal treatment effect in dogs, not a concordance/translation metric between animal and human findings.; level_correct: n
- 26959227-4: Humanized mice showed selective CD3 downmodulation on T cells upon OKT3 injection, a typical effect of OKT3. | verifier said: is_correspondence: no — The text reports the animal treatment effect and notes it is a typical human effect but provides no concordance/translation metric.
- 28668095-1: The human sequence of CSPG4 had 88% similarity with the canine counterpart. | verifier said: is_correspondence: no — This percentage reports sequence similarity, not a concordance/translation rate of animal vs human findings.
- 32211332-1: Nine dogs co-clustered with 97 human samples in group 2, suggesting an ABC phenotype. | verifier said: is_correspondence: no — This is a count of co-clustering (sample membership), not a quantitative concordance or translation metric between species.
- 40534873-2: The study found clear differences in the directionality of pathways that are potentially impacted between mice and humans. | verifier said: is_correspondence: no — The text reports a qualitative difference, not a numeric concordance/translation rate or other correspondence metric.
- W2938335835-4: There was no correlation between what the genes and responses did in mice versus what they did in humans for inflammatory processes such as  | verifier said: own_result: no — This is a citation of Seok et al. (2013), not an original result or pooled analysis by the book authors.
- 41952231-5: The proportion of homologous DEGs associated with 'disease progression' in ICR mice was 9.26%. | verifier said: is_correspondence: no — This is a within-animal proportion of homologous DEGs, not a measure of animal–human correspondence.
- 38717901-5: Human voxels with connectivity profiles most similar to mouse M1 showed higher values on three myelin markers compared to human voxels most  | verifier said: is_correspondence: no — The t-statistic is from a comparison between two human voxel groups, not a concordance/translation rate between animal and human finding
- 42399261-6: Mouse PC2 explained 5.71% of variance in human entorhinal cortex microglia. | verifier said: is_correspondence: no — The 5.71% is variance explained, not a measure of cross-species concordance or translation rate.; species_correct: no — The text refers 
- 40839180-0: The standard deviation of the error in prediction (SDEP) for human samples was 300 minutes across the entire PMI window. | verifier said: is_correspondence: no — SDEP is an error in prediction for human samples, not a concordance or translation rate between animal and human findings.; species_corr
- 40808951-4: SOCS3 was significantly upregulated in both mouse models of septic liver injury. | verifier said: is_correspondence: no — This is an animal finding; the text gives no concordance/translation metric between animals and humans.; level_correct: no — The reporte
- 28182759-5: For disease-modifying interventions, 84% of macaque studies showed an improved outcome. | verifier said: is_correspondence: no — This percent reports macaque improved outcomes, not a measure of animal-human correspondence.

Cost (uncached): $6.39
