# Spot-check: 40 results to verify by hand

Built 2026-09-15 from 1520 final results in 419 studies. Sample A seed 20260914, sample B seed 20260915; both redrawable by re-running `t1_part1_outputs.py`.

## What you are checking, and why it matters

Every result on the site was extracted by a model, checked by a second model, then decided by an
adjudicator. For 769 of the 1,494 final results that adjudicator was the same agent that built the
pipeline, working by hand and not blind (limitation L87). **This spot-check is the only independent
check on that.** If it passes, the corpus has been checked by someone who did not build it. If it
fails, we learn where, and re-adjudicate that class of result rather than patching single rows.

Two samples below, drawn by fixed seeds so they can be redrawn and audited:

- **Sample A — 30 random final results** (seed 20260914), an unbiased read of the whole corpus.
- **Sample B — 10 results from hand-adjudicated studies** (seed 20260915), aimed squarely at the
  weakest link. These are the ones to do first if you only have an hour.

## How to check one (about 5 minutes)

1. Open the paper — the PubMed/OpenAlex link, or the DOI. The local PDF path is given too; the PDF
   page number is where the extractor located the quote.
2. Find the quoted sentence. Searching a distinctive phrase from it is faster than reading the page.
3. Then check these four things **in order**, and stop at the first one that fails:

| # | Question | Fails if |
|---|---|---|
| a | Is the quote really in this paper, and is it this paper's own result? | the sentence isn't there, or it is a figure the authors quote from someone else's study |
| b | Does the statement say what the quote says? | the statement asserts more, less, or something different |
| c | Do the value, unit and n match the quote? | a number differs, or a rate is inverted (43% vs 57%) |
| d | Is this an animal-vs-human comparison, with the right species and level? | it is an animal-only result, an animal-vs-animal result, an in-vitro result, or the species/level is wrong |

**Not failures:** paraphrase that preserves the meaning; rounding (71% vs 70.6%); a page number one
off from where you find the quote; a value repeated elsewhere in the paper.

**Failures worth flagging loudly:** (a) and (d). Those mean the result should never have been kept,
and they tend to come in classes rather than singly.

## How to record it

Mark each item ✓ or ✗ below, and for a ✗ write **which letter failed** (a/b/c/d) plus one line of
what you saw. The letter matters more than the prose — it tells me whether to re-run extraction,
re-adjudicate a category, or fix one row.

**Then tell me the count.** Rough reading: 0–1 failures across the 40 is consistent with the error
rate the model-adjudicated portion already showed. Two or more failures on (a) or (d) is a
systematic problem, not bad luck, and I will re-adjudicate that whole class before the site stands.

## Sample A — 30 random final results

### A1. Zebrafish toxicological screening could aid Leishmaniosis drug discovery
2021 · Laboratory Animal Research · record 34530926 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/34530926/) · [DOI](https://doi.org/10.1186/s42826-021-00104-1) · local PDF `data/raw/fulltext/34530926.pdf` · **go to PDF page 7**
- **Statement:** The zebrafish model did not predict the side effects of carbamazepine and benznidazole, which are common in humans.
- **Value:** — · species `zebrafish` · level B · direction animal-did-not-correspond · cross-cutting-toxicology
- **Quote:** “Thus, the proposed platform was sensible to perform an effective screening for approval of new compounds, however, it did not predict the side effects of the drugs.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A2. Patient-derived xenografts effectively capture responses to oncology therapy in a heterogeneous cohort of pati
2017 · Annals of Oncology · record 28945830 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/28945830/) · [DOI](https://doi.org/10.1093/annonc/mdx416) · local PDF `data/raw/fulltext/28945830.pdf` · **go to PDF page 7**
- **Statement:** The sensitivity for the PDX drug screens was 96% (80/83).
- **Value:** 96 percent (n 80/83) · species `mouse` · level A · direction animal-corresponded · oncology
- **Quote:** “Our analysis revealed a sensitivity for the PDX drug screens of 96%, with a lower 95% confidence interval (CI) of 89% (which meets the acceptance criteria of 80%), and specificity of 70%, with a lower 95% CI of 54% (Table 1, top panel).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A3. Plasma-to-tumour tissue integrated proteomics using nano-omics for biomarker discovery in glioblastoma
2025 · Nature Communications · record 40210624 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/40210624/) · [DOI](https://doi.org/10.1038/s41467-025-58252-0) · local PDF `data/raw/fulltext/40210624.pdf` · **go to PDF page 1**
- **Statement:** 48 potential glioblastoma biomarker candidates were identified through cross-species correlation.
- **Value:** 48 count · species `grouped-label` · level C · direction animal-corresponded · oncology
- **Quote:** “Cross-species correlation identified 48 potential GB biomarker candidates involved in actin cytoskeleton organisation, focal adhesion, platelet activation, leukocyte migration, amino acid biosynthesis, carbon metabolism, and phagosome pathways.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A4. Cntnap2-dependent molecular networks in autism spectrum disorder revealed through an integrative multi-omics a
2022 · Molecular Psychiatry · record 36253443 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/36253443/) · [DOI](https://doi.org/10.1038/s41380-022-01822-1) · local PDF `data/raw/fulltext/36253443.pdf` · **go to PDF page 3**
- **Statement:** Out of 7413 common genes between mouse proteomic data and human transcriptome data, 48 genes showed the same expression trend.
- **Value:** 48 count (n 48/7413) · species `grouped-label` · level C · direction animal-corresponded · neurology
- **Quote:** “Of the 7413 genes found to be common to both datasets (Fig. 4a), 48 genes (12 upregulated and 36 downregulated DEGs) showed the same trend as the DEPs in our proteomic data (Fig. 4b).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A5. Identification of conserved canonical marker genes in human and mouse adrenal glands using Visium spatial tran
2025 · Histochemistry and Cell Biology · record 41442035 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/41442035/) · [DOI](https://doi.org/10.1007/s00418-025-02446-6) · local PDF `data/raw/fulltext/41442035.pdf` · **go to PDF page 14**
- **Statement:** The Spearman correlation of log2FC values between human ZR and mouse ZF across 18 signature genes was 0.4.
- **Value:** 0.4 correlation · species `grouped-label` · level C · direction animal-corresponded · new
- **Quote:** “The correlations for other clusters were considerably lower (ρ=0.4 for ZF, ZG, and medulla; ρ=−0.8 for CT/WAT), yielding a specificity margin Δρ=0.4 (Fig. 7c).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A6. Know Thy Model: Charting Molecular Homology in Stromal Reprogramming Between Canine and Human Mammary Tumors
2019 · Frontiers in Cell and Developmental Biology · record 31921858 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/31921858/) · [DOI](https://doi.org/10.3389/fcell.2019.00348) · local PDF `data/raw/fulltext/31921858.pdf` · **go to PDF page 7**
- **Statement:** The paper found strong molecular homology in stromal reprogramming between canine and human mammary carcinomas.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · oncology
- **Quote:** “In conclusion, these results clearly demonstrated that stromal reprogramming in canine and human mCA shares significant molecular homology.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A7. Cross-species single-cell landscapes identify the pathogenic gene characteristics of inherited retinal disease
2024 · Frontiers in Genetics · record 39055259 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/39055259/) · [DOI](https://doi.org/10.3389/fgene.2024.1409016) · local PDF `data/raw/fulltext/39055259.pdf` · **go to PDF page 12**
- **Statement:** The IRDs GNAT2, PDEFG, and CSPG4 displayed highly consistent expression in humans and mice.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · ophthalmology
- **Quote:** “The IRDs (GNAT2, PDEFG, and CSPG4) displayed highly consistent expression in humans and mice (Supplementary Figure 5F).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A8. Concordance of the Toxicity of Pharmaceuticals in Humans and in Animals
2000 · Regulatory Toxicology and Pharmacology · record 11029269 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/11029269/) · [DOI](https://doi.org/10.1006/rtph.2000.1399) · local PDF `data/raw/fulltext/11029269.pdf` · **go to PDF page 5**
- **Statement:** The true positive human toxicity concordance rate for nonrodent species was 63% for human toxicity events.
- **Value:** 63 percent (n None/221) · species `grouped-label` · level B · direction animal-corresponded · cross-cutting-toxicology
- **Quote:** “Concordance was seen in 63% of nonrodent studies (primarily the dog) and 43% of rodent studies (primarily the rat).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A9. Clonogenic assay with established human tumour xenografts
2004 · European Journal of Cancer · record 15120036 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/15120036/) · [DOI](https://doi.org/10.1016/j.ejca.2004.01.009) · local PDF `data/raw/fulltext/15120036.pdf` · **go to PDF page 1**
- **Statement:** 97% of 80 comparisons between clinical response of tumors and their explants established in nude mice and treated in vivo showed correct prediction for tumor resistance.
- **Value:** 97 percent (n None/80) · species `mouse` · level A · direction animal-corresponded · oncology
- **Quote:** “Of 80 comparisons performed, we observed a correct prediction for tumour resistance in 97% and for tumour sensitivity in 90%.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A10. Tripartite factors leading to molecular divergence between human and murine smooth muscle
2020 · PLoS ONE · record 31945134 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/31945134/) · [DOI](https://doi.org/10.1371/journal.pone.0227672) · local PDF `data/raw/fulltext/31945134.pdf` · **go to PDF page 10**
- **Statement:** 19% of EC non-uniformly conserved proteins were absent in mouse.
- **Value:** 19.0 percent · species `mouse` · level C · direction animal-did-not-correspond · cardiovascular
- **Quote:** “Non-uniformly conserved VSMC proteins were much more likely to be absent in mouse than EC or VSMC/EC non-conserved molecules (84.6% for VSMC, compared with 19% for EC proteins and 42.1% for VSMC/EC proteins).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A11. Patient-derived xenografts effectively capture responses to oncology therapy in a heterogeneous cohort of pati
2017 · Annals of Oncology · record 28945830 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/28945830/) · [DOI](https://doi.org/10.1093/annonc/mdx416) · local PDF `data/raw/fulltext/28945830.pdf` · **go to PDF page 8**
- **Statement:** When the first systemic therapy was received after tumor collection, the sensitivity of PDX drug screens was 97% (29/30).
- **Value:** 97 percent (n 29/30) · species `mouse` · level A · direction animal-corresponded · oncology
- **Quote:** “Table 1. Values and confidence intervals for parameters of analytical and clinical accuracy for PDX model drug screening ... Treatment is first therapy received after tumor collection ... Sensitivity 97% (29/30) 81%-99%”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A12. Translating medication effects for alcohol use disorder across preclinical, human laboratory, and clinical tri
2025 · Translational Psychiatry · record 40691154 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/40691154/) · [DOI](https://doi.org/10.1038/s41398-025-03473-6) · local PDF `data/raw/fulltext/40691154.pdf` · **go to PDF page 5**
- **Statement:** Medications that reduced alcohol preference in preclinical 2-BC studies were associated with lower return to drinking in human clinical trials, with a linear slope of 0.04.
- **Value:** 0.04 none · species `grouped-label` · level A · direction animal-corresponded · psychiatry-addiction
- **Quote:** “For the preclinical 2-BC preference endpoint, the linear slope is statistically significant for return to any drinking in RCTs (β = 0.04, SE = 0.02, p=0.004; Fig. 2B), such that medications that reduced alcohol preference in preclinical 2-BC studies were associated with lower return to drinking in R”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A13. An integrated analysis of genes and functional pathways for aggression in human and rodent models
2018 · Molecular Psychiatry · record 29858598 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/29858598/) · [DOI](https://doi.org/10.1038/s41380-018-0068-7) · local PDF `data/raw/fulltext/29858598.pdf` · **go to PDF page 7**
- **Statement:** The pathway overlap between human GWAS and rodent transcriptome genes was not significant, with 27 pathways in common.
- **Value:** 27 count · species `grouped-label` · level C · direction animal-did-not-correspond · psychiatry-addiction
- **Quote:** “In contrast, the pathway overlap between the human GWAS and rodent transcriptome genes was not significant (N = 27, p = 0.20).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A14. Expression profiles of the autism-related SHANK proteins in the human brain
2023 · BMC Biology · record 37953224 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/37953224/) · [DOI](https://doi.org/10.1186/s12915-023-01712-0) · local PDF `data/raw/fulltext/37953224.pdf` · **go to PDF page 12**
- **Statement:** SHANK2 puncta density and sum intensity in the amygdala were considerably higher in mice compared to humans.
- **Value:** — · species `grouped-label` · level C · direction animal-did-not-correspond · neurology
- **Quote:** “In contrast, puncta density and sum intensity in the AMY were considerably higher in mice compared to humans.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A15. Complement response to burn injury: systematic review and meta-analysis of patient and animal studies
2026 · Frontiers in Immunology · record 41822479 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/41822479/) · [DOI](https://doi.org/10.3389/fimmu.2026.1793945) · local PDF `data/raw/fulltext/41822479.pdf` · **go to PDF page 8**
- **Statement:** Human studies showed markedly higher levels of C3a compared with animal studies, with a standardized mean difference of 2.18 in humans.
- **Value:** 2.18 none (n None/9) · species `non-human-primate` · level A · direction mixed · immunology-inflammation
- **Quote:** “Compared with animal studies, human studies showed markedly higher levels of C3a (animals: SMD = -1.34; CI95% = -1.78, -0.89; n = 1 study versus humans: SMD = 2.18; CI95% = 1.79, 2.56; n = 9 studies; P< 0.0001)”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A16. Transcriptomic evidence for immaturity of the prefrontal cortex in patients with schizophrenia
2014 · Molecular Brain · record 24886351 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/24886351/) · [DOI](https://doi.org/10.1186/1756-6606-7-41) · local PDF `data/raw/fulltext/24886351.pdf` · **go to PDF page 8**
- **Statement:** 110 genes overlapped between human developing MFC and Shn-2 KO mice MFC, indicating significant similarities in the pattern of transcriptome changes between the two groups (P = 0.0063).
- **Value:** 0.0063 none · species `mouse` · level C · direction animal-corresponded · psychiatry-addiction
- **Quote:** “One hundred and 10 genes overlapped between human developing MFC and Shn-2 KO mice MFC, indicating significant similarities in the pattern of transcriptome changes between the two groups (P = 0.0063, Figure 4a, Additional file 1: Table S22).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A17. Amphetamine increases motivation of humans and mice as measured by breakpoint, but does not affect an Electroe
2024 · Cognitive Affective & Behavioral Neuroscience · record 38168850 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/38168850/) · [DOI](https://doi.org/10.3758/s13415-023-01150-z) · local PDF `data/raw/fulltext/38168850.pdf` · **go to PDF page 1**
- **Statement:** Amphetamine increased breakpoint in mice (cohort 2, without EEG tethering) at 0.3 mg/kg.
- **Value:** — · species `mouse` · level A · direction animal-corresponded · neurology
- **Quote:** “In cohort 2, however, 0.3 mg/kg of amphetamine increased breakpoint consistent with human findings.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A18. A multimodal cross-species comparison of pancreas development
2025 · Nature Communications · record 41125606 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/41125606/) · [DOI](https://doi.org/10.1038/s41467-025-64774-4) · local PDF `data/raw/fulltext/41125606.pdf` · **go to PDF page 1**
- **Statement:** Transcription factors regulated by NEUROG3 were over 50% conserved between pig and human.
- **Value:** 0.5 percent · species `grouped-label` · level C · direction animal-corresponded · metabolic-endocrine
- **Quote:** “Transcription factors regulated by NEUROG3, the endocrine master regulator, are over 50% conserved between pig and human, many being validated in human stem cell models.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A19. The dog as an animal model for bladder and urethral urothelial carcinoma: Comparative epidemiology and histolo
2018 · Oncology Letters · record 30008848 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/30008848/) · [DOI](https://doi.org/10.3892/ol.2018.8837) · local PDF `data/raw/fulltext/30008848.pdf` · **go to PDF page 6**
- **Statement:** Urothelial carcinoma is the most common type of bladder cancer in both people and dogs with comparable frequencies.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · oncology
- **Quote:** “UC is the most common type of bladder cancer in both people and dogs with comparable frequencies.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A20. Transcriptomic Cross‐Species Analysis of Chronic Liver Disease Reveals Consistent Regulation Between Humans an
2021 · Hepatology Communications · record 34558834 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/34558834/) · [DOI](https://doi.org/10.1002/hep4.1797) · local PDF `data/raw/fulltext/34558834.pdf` · **go to PDF page 15**
- **Statement:** The highest precision for human NAFLD was 0.33 in the Western-type diet mouse model.
- **Value:** 0.33 none · species `mouse` · level C · direction animal-corresponded · liver-gi
- **Quote:** “Among the 12 mouse models analyzed, the WTD presented with the highest precision (0.33) for human NAFLD.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A21. Bridging the Gap Between Fluid Biomarkers for Alzheimer’s Disease, Model Systems, and Patients
2020 · Frontiers in Aging Neuroscience · record 32982716 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/32982716/) · [DOI](https://doi.org/10.3389/fnagi.2020.00272) · local PDF `data/raw/fulltext/32982716.pdf` · **go to PDF page 1**
- **Statement:** The core Alzheimer's disease biomarkers have been found to translate well across species.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · neurology
- **Quote:** “The core AD biomarkers have been found to translate well across species, whereas biomarkers of neuroinflammation translate to a lesser extent.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A22. Acquired resistance to the RAS(ON) multi-selective inhibitor daraxonrasib guides rational combination therapy 
2026 · Nature Medicine · record 42581230 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/42581230/) · [DOI](https://doi.org/10.1038/s41591-026-04537-w) · local PDF `data/raw/fulltext/42581230.pdf` · **go to PDF page 5**
- **Statement:** The majority of key acquired resistance mechanisms identified in human patient ctDNA samples were recapitulated in daraxonrasib-resistant preclinical models.
- **Value:** — · species `grouped-label` · level A · direction animal-corresponded · oncology
- **Quote:** “The majority of key acquired resistance mechanisms identified in the EOT ctDNA samples (for example, mutant KRASamp, RTK alterations and MYCamp) were recapitulated in daraxonrasib-resistant preclinical models derived following prolonged RAS(ON) inhibition.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A23. Transcriptomic classification of genetically engineered mouse models of breast cancer identifies human subtype
2013 · Genome biology · record 24220145 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/24220145/) · [DOI](https://doi.org/10.1186/gb-2013-14-11-r125) · local PDF `data/raw/fulltext/24220145.pdf` · **go to PDF page 7**
- **Statement:** The murine NeuEx class associated with the human luminal A subtype based on gene set analysis.
- **Value:** — · species `mouse` · level C · direction animal-corresponded · oncology
- **Quote:** “Previously defined as a 'luminal' model [31], the Neu Ex murine class associated with the human luminal A sub-type in this newest analysis; this correlation was somewhat surprising given the lack of ERa and ERa-regulated gene expression in the murine NeuEx class, but does suggest that human luminal ”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A24. Phosphoproteomics reveals conserved exercise‐stimulated signaling and AMPK regulation of store‐operated calciu
2019 · The EMBO Journal · record 31381180 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/31381180/) · [DOI](https://doi.org/10.15252/embj.2019102578) · local PDF `data/raw/fulltext/31381180.pdf` · **go to PDF page 4**
- **Statement:** 190 phosphosites were regulated in the same region of the protein across human, rat, and mouse datasets.
- **Value:** 190 count · species `grouped-label` · level C · direction animal-corresponded · cross-cutting-toxicology
- **Quote:** “Mapping potential orthologs by sequence window resulted in the identification of 190 phosphosites regulated in all three models (114 up- and 76 down-regulated phosphosites), representing 80 proteins (Table EV2).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A25. Plasma Chemokines in Patients with Alcohol Use Disorders: Association of CCL11 (Eotaxin-1) with Psychiatric Co
2017 · Frontiers in Psychiatry · record 28149283 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/28149283/) · [DOI](https://doi.org/10.3389/fpsyt.2016.00214) · local PDF `data/raw/fulltext/28149283.pdf` · **go to PDF page 13**
- **Statement:** The paper found that changes in plasma CXCL12 concentrations in male rats exposed to repeated ethanol were similar to those observed in humans during abstinence.
- **Value:** — · species `grouped-label` · level A · direction animal-corresponded · psychiatry-addiction
- **Quote:** “studies conducted in male rats exposed to repeated ethanol revealed similar changes in plasma CXCL12 concentra- tions than those observed in humans during abstinence during abstinence and acute ethanol exposure also induced a decrease in CXCL12”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A26. Comparative HPLC-MSn analysis of canine and human meibomian lipidomes: many similarities, a few differences
2011 · Scientific Reports · record 22355543 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/22355543/) · [DOI](https://doi.org/10.1038/srep00024) · local PDF `data/raw/fulltext/22355543.pdf` · **go to PDF page 11**
- **Statement:** Canine meibum had a relatively larger proportion of (O-acyl)-omega-hydroxy fatty acids (OAHFA) than human meibum.
- **Value:** — · species `laboratory-dog` · level C · direction animal-did-not-correspond · ophthalmology
- **Quote:** “Canine meibum has a relatively larger proportion of OAHFA (minor HPLC with RT 4–6 min, Fig.1A) than human meibum.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A27. A comparative encyclopedia of DNA elements in the mouse genome
2014 · Nature · record 25409824 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/25409824/) · [DOI](https://doi.org/10.1038/nature13992) · local PDF `data/raw/fulltext/25409824.pdf` · **go to PDF page 4**
- **Statement:** 79.6% of chromatin-based promoter predictions in the mouse genome have homologues in the human genome with at least 10% overlapping nucleotides.
- **Value:** 79.6 percent · species `mouse` · level C · direction animal-corresponded · cross-cutting-toxicology
- **Quote:** “This analysis showed that 79.3% of chromatin-based enhancer predictions, 79.6% of chromatin-based promoter predictions, 67.1% of the DHS, and 66.7% of the transcription factor binding sites in the mouse genome have homologues in the human genome with at least 10% overlapping nucleotides, while by ra”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A28. Comparative developmental genomics of sex-biased gene expression in early embryogenesis across mammals
2023 · Biology of Sex Differences · record 37208698 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/37208698/) · [DOI](https://doi.org/10.1186/s13293-023-00520-z) · local PDF `data/raw/fulltext/37208698.pdf` · **go to PDF page 5**
- **Statement:** The orthologs of 17 transcription factors expressed in mouse were detected in human embryos.
- **Value:** 17 count · species `grouped-label` · level C · direction mixed · new
- **Quote:** “Surprisingly, the orthologs of only 17 TFs and 6 EEs expressed in the mouse were detected in human embryos.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A29. Know Thy Model: Charting Molecular Homology in Stromal Reprogramming Between Canine and Human Mammary Tumors
2019 · Frontiers in Cell and Developmental Biology · record 31921858 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/31921858/) · [DOI](https://doi.org/10.3389/fcell.2019.00348) · local PDF `data/raw/fulltext/31921858.pdf` · **go to PDF page 7**
- **Statement:** Upregulated genes in canine normal stroma were highly enriched among favorably prognostic genes in humans.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · oncology
- **Quote:** “And finally, we demonstrated that the high level of molecular homology between canine and human stromal reprogramming manifested in a prognostic value of the canine CAS signature, with upregulated genes in canine CAS highly enriched among adversely prognostic genes in humans, and upregulated genes i”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### A30. Concordant and discordant gene expression patterns in mouse strains identify best-fit animal model for human t
2017 · Scientific Reports · record 28935874 · adjudicated by **model**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/28935874/) · [DOI](https://doi.org/10.1038/s41598-017-11812-x) · local PDF `data/raw/fulltext/28935874.pdf` · **go to PDF page 7**
- **Statement:** There were no enriched discordant modules in the comparison of human and murine macrophages.
- **Value:** 0 count · species `grouped-label` · level C · direction animal-corresponded · infectious-disease
- **Quote:** “Unlike in the case of WB comparisons, there were no enriched discordant modules in this comparison.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

## Sample B — 10 results from hand-adjudicated studies

### B1. Association between early arterial pH, base excess and lactate and 24-h mortality and neurological outcomes af
2026 · Resuscitation Plus · record 41648068 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/41648068/) · [DOI](https://doi.org/10.1016/j.resplu.2026.101228) · local PDF `data/raw/fulltext/41648068.pdf` · **go to PDF page 1**
- **Statement:** The area under the curve for lactate to predict 24-h mortality in rats was 0.959.
- **Value:** 0.959 auc · species `rat` · level A · direction animal-corresponded · cardiovascular
- **Quote:** “In a multivariate regression analysis area under the curve, considering pH, base excess and lactate, for prediction of mortality were respectively: 0.796 (95%CI: 0.635-0.956), 0.980 (95%CI: 0.946-1.000), 0.959 (95%CI: 0.896-1.000) in rats”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B2. Translating metabolomic evidence gathered from an animal model to a real human scenario: the post-mortem inter
2025 · Metabolomics · record 40839180 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/40839180/) · [DOI](https://doi.org/10.1007/s11306-025-02321-4) · local PDF `data/raw/fulltext/40839180.pdf` · **go to PDF page 7**
- **Statement:** Taurine and Hypoxanthine concentrations showed no differences between animal and human samples.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · cross-cutting-toxicology
- **Quote:** “Interestingly, no differences in Taurine and Hypoxanthine concentrations can be seen between animal and humans as shown by Fig. 6.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B3. Transcriptional programs diverge in aging mouse and human skeletal muscle
2026 · Aging · record 42172440 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/42172440/) · [DOI](https://doi.org/10.18632/aging.206382) · local PDF `data/raw/fulltext/42172440.pdf` · **go to PDF page 1**
- **Statement:** Neurogenesis demonstrated opposing or non-significant trends between mouse and human skeletal muscle with aging.
- **Value:** — · species `grouped-label` · level C · direction mixed · pain-musculoskeletal
- **Quote:** “Hypoxia signaling, VEGFA, and inflammatory pathways showed concordant downregulation with aging in both species; however, angiogenesis, neurogenesis, and myogenesis demonstrated opposing or non-significant trends.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B4. Transfer learning between preclinical models and human tumors identifies a conserved NK cell activation signat
2021 · Genome Medicine · record 34376232 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/34376232/) · [DOI](https://doi.org/10.1186/s13073-021-00944-5) · local PDF `data/raw/fulltext/34376232.pdf` · **go to PDF page 10**
- **Statement:** The NK cell activation signature was significantly higher in anti-CTLA-4 responsive human tumors than non-responsive tumors.
- **Value:** 1e-15 none · species `mouse` · level C · direction animal-corresponded · oncology
- **Quote:** “In pre-treatment biopsies, the NK cell activation signature was significantly higher in anti-CTLA-4 responsive tumors than non-responsive tumors (p < 1 × 10-15, Additional file 1: Fig. S2A).”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B5. From signal to significance: characterizing anthracycline-related hypercoagulable adverse events via pharmacov
2026 · Frontiers in Pharmacology · record 42602169 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/42602169/) · [DOI](https://doi.org/10.3389/fphar.2026.1856410) · local PDF `data/raw/fulltext/42602169.pdf` · **go to PDF page 1**
- **Statement:** The paper found that pathways related to cyclic adenosine monophosphate (cAMP) signaling and heparan sulfate biosynthesis were directionally consistent between experimental models and clinical samples.
- **Value:** — · species `grouped-label` · level C · direction animal-corresponded · oncology
- **Quote:** “Exploratory analyses suggested potential involvement of pathways related to cyclic adenosine monophosphate (cAMP) signaling and heparan sulfate biosynthesis, which were directionally consistent with observed alterations in coagulation-related parameters in clinical samples and experimental models.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B6. Single-cell multimodal analysis identifies common regulatory programs in synovial fibroblasts of rheumatoid ar
2022 · Genome Medicine · record 35879783 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/35879783/) · [DOI](https://doi.org/10.1186/s13073-022-01081-3) · local PDF `data/raw/fulltext/35879783.pdf` · **go to PDF page 20**
- **Statement:** 17 shared regulons were identified between hTNFtg mice and human RA patients.
- **Value:** 17 count · species `grouped-label` · level C · direction animal-corresponded · immunology-inflammation
- **Quote:** “A Regulatory network analysis in mouse and human datasets reveals 17 shared regulons.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B7. Activin-A impedes the establishment of CD4+ T cell exhaustion and enhances anti-tumor immunity in the lung
2021 · Journal of Experimental & Clinical Cancer Research · record 34548096 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/34548096/) · [DOI](https://doi.org/10.1186/s13046-021-02092-5) · local PDF `data/raw/fulltext/34548096.pdf` · **go to PDF page 1**
- **Statement:** Treatment of activin-A on tumor-infiltrating CD4+ T cells from lung cancer patients augmented their immunostimulatory capacity towards autologous CD4+ and CD8+ T cells, mimicking its anti-tumorigenic effects observed in the mouse lung cancer models.
- **Value:** — · species `mouse` · level C · direction animal-corresponded · oncology
- **Quote:** “Of translational importance, treatment of activin-A on tumor-infiltrating CD4+ T cells from lung cancer patients augmented their immunostimulatory capacity towards autologous CD4+ and CD8+ T cells.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B8. Pan-glioma analyses reveal species- and tumor-specific regulation of neuron-glioma synapse genes by lncRNAs
2023 · Frontiers in Genetics · record 37693314 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/37693314/) · [DOI](https://doi.org/10.3389/fgene.2023.1218408) · local PDF `data/raw/fulltext/37693314.pdf` · **go to PDF page 8**
- **Statement:** NGS genes in mouse PDX models showed similar expression levels to NGS genes in human MB.
- **Value:** — · species `grouped-label` · level A · direction animal-corresponded · oncology
- **Quote:** “Fourth, NGS genes in mouse MB PDX showed similar expression levels to NGS genes in human MB”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B9. Nanomedicine in 2026: Illustrative Quantitative Analyses of EPR Heterogeneity, Clinical Trial Attrition, and E
2026 · International Journal of Nanomedicine · record 42311422 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/42311422/) · [DOI](https://doi.org/10.2147/ijn.s618407) · local PDF `data/raw/fulltext/42311422.pdf` · **go to PDF page 6**
- **Statement:** Median nanoparticle tumour-to-blood ratio was 8.5 in murine models versus 1.8 in human tumours from the same publications (23 studies, 412 patients).
- **Value:** 8.5 ratio · species `mouse` · level C · direction animal-did-not-correspond · oncology
- **Quote:** “compared to a median of 8.5 (IQR: 5.1-14.2) in murine models from the same publications.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

### B10. Translatability of preclinical to early clinical tolerable and pharmacologically active dose ranges for centra
2023 · Translational Psychiatry · record 36859342 · adjudicated by **hand**

- **Open:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/36859342/) · [DOI](https://doi.org/10.1038/s41398-023-02353-1) · local PDF `data/raw/fulltext/36859342.pdf` · **go to PDF page 8**
- **Statement:** The preclinical data predicted the pharmacologically active range in humans to a high degree, with 18 out of 25 interventions showing an overlap of 80% or more for HED.
- **Value:** 72 percent (n 18/25) · species `grouped-label` · level A · direction animal-corresponded · neurology
- **Quote:** “Overall, the preclinical data predicted the pharmacologically active range in humans to a high degree, as indicated by an overlap of ≥ 80% in 18 out of 25 (72%) for HED, 15 out of 25 (60%) for Cmax and 19 out of 23 (83%) for AUC.”
- **Check:** ☐ ✓   ☐ ✗ → failed (a / b / c / d): ______  note: ______

