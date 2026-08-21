# Full texts still needed

**14** eligible studies lack full text.
(61 eligible of 100 screened; 47 eligible already held.)

14 further records without full text were **excluded** under rubric r3 (in silico only, in vitro only, human only, or reporting no animal-to-human agreement statistic) and are deliberately omitted below &mdash; they are not needed.

Save each as `data/raw/fulltext/<PMID>.pdf` (or `.xml`), then run:

```bash
python3 analysis/14_extract_fulltext.py
python3 analysis/20_measurements.py
python3 analysis/19_reclassify.py
python3 analysis/21_wanted_list.py
python3 analysis/15_build_site.py
```

Files are gitignored and never published; only extracted data reaches the site.

| PMID | Cites | Year | Arm | Journal | Title | DOI |
|---|---|---|---|---|---|---|
| [17032985](https://pubmed.ncbi.nlm.nih.gov/17032985/) | 312 | 2006 | methods-and-bias | JAMA | Translation of research evidence from animals to humans. | [10.1001/jama.296.14.1731](https://doi.org/10.1001/jama.296.14.1731) |
| [15246820](https://pubmed.ncbi.nlm.nih.gov/15246820/) | 27 | 2004 | efficacy | Exp Neurol | Lost in translation: taking neuroprotection from animal models to clinical trials. | [10.1016/j.expneurol.2004.05.008](https://doi.org/10.1016/j.expneurol.2004.05.008) |
| [26753942](https://pubmed.ncbi.nlm.nih.gov/26753942/) | 21 | 2015 | toxicology | Altern Lab Anim | Predicting human drug toxicity and safety via animal tests: can any one species predict drug toxicity in any other, and do monkeys help? | [10.1177/026119291504300607](https://doi.org/10.1177/026119291504300607) |
| [28903488](https://pubmed.ncbi.nlm.nih.gov/28903488/) | 15 | 2017 | safety-pharmacology | Toxicol Sci | An Analysis of the Relationship Between Preclinical and Clinical QT Interval-Related Data. | [10.1093/toxsci/kfx125](https://doi.org/10.1093/toxsci/kfx125) |
| [26856335](https://pubmed.ncbi.nlm.nih.gov/26856335/) | 12 | 2016 | toxicology | Eur J Appl Physiol | The rat closely mimics oxidative stress and inflammation in humans after exercise but not after exercise combined with vitamin C administration. | [10.1007/s00421-016-3336-8](https://doi.org/10.1007/s00421-016-3336-8) |
| [35616311](https://pubmed.ncbi.nlm.nih.gov/35616311/) | 7 | 2022 | methods-and-bias | J R Soc Med | The role of systematic reviews in identifying the limitations of preclinical animal research, 2000-2022: part 2. | [10.1177/01410768221100970](https://doi.org/10.1177/01410768221100970) |
| [32413492](https://pubmed.ncbi.nlm.nih.gov/32413492/) | 7 | 2021 | efficacy | Drug Discov Today | Rodent models of diabetic kidney disease: human translatability and preclinical validity. | [10.1016/j.drudis.2020.05.004](https://doi.org/10.1016/j.drudis.2020.05.004) |
| [35781406](https://pubmed.ncbi.nlm.nih.gov/35781406/) | 4 | 2023 | efficacy | Clin Oncol (R Coll Radiol) | A Multicentre Clinical Study of Sarcoma Personalised Treatment Using Patient-Derived Tumour Xenografts. | [10.1016/j.clon.2022.06.002](https://doi.org/10.1016/j.clon.2022.06.002) |
| [38852684](https://pubmed.ncbi.nlm.nih.gov/38852684/) | 3 | 2024 | safety-pharmacology | J Pharmacol Toxicol Methods | A simple accurate method for concentration-QTc analysis in preclinical animal models. | [10.1016/j.vascn.2024.107528](https://doi.org/10.1016/j.vascn.2024.107528) |
| [38676802](https://pubmed.ncbi.nlm.nih.gov/38676802/) | 3 | 2024 | efficacy | Methods Mol Biol | Patient-Derived Xenograft Models for Translational Prostate Cancer Research and Drug Development. | [10.1007/978-1-0716-3858-3_12](https://doi.org/10.1007/978-1-0716-3858-3_12) |
| [33813006](https://pubmed.ncbi.nlm.nih.gov/33813006/) | 3 | 2021 | safety-pharmacology | J Pharmacol Toxicol Methods | Core battery safety pharmacology testing - An assessment of its utility in early drug development. | [10.1016/j.vascn.2021.107055](https://doi.org/10.1016/j.vascn.2021.107055) |
| [30726989](https://pubmed.ncbi.nlm.nih.gov/30726989/) | 3 | 2019 | safety-pharmacology | Toxicol Sci | Preclinical to Clinical Translation of Hemodynamic Effects in Cardiovascular Safety Pharmacology Studies. | [10.1093/toxsci/kfz035](https://doi.org/10.1093/toxsci/kfz035) |
| [26563791](https://pubmed.ncbi.nlm.nih.gov/26563791/) | 1 | 2015 | toxicology | Handb Clin Neurol | Extrapyramidal system neurotoxicity: animal models. | [10.1016/B978-0-444-62627-1.00012-3](https://doi.org/10.1016/B978-0-444-62627-1.00012-3) |
| [42245789](https://pubmed.ncbi.nlm.nih.gov/42245789/) | 0 | 2026 | veterinary | Res Sq | Leveraging Dog Models to Uncover Human Cancer Insights. | [10.21203/rs.3.rs-9783746/v1](https://doi.org/10.21203/rs.3.rs-9783746/v1) |
