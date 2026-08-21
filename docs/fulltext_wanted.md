# Full texts still needed

**34 of 100** studies lack full text (66 held).

Save each as `data/raw/fulltext/<PMID>.pdf` (or `.xml`), then run:

```bash
python3 analysis/14_extract_fulltext.py
python3 analysis/20_measurements.py
python3 analysis/19_reclassify.py
python3 analysis/21_wanted_list.py
python3 analysis/15_build_site.py
```

Files are gitignored and never published; only extracted data reaches the site.

| PMID | Cites | Year | Journal | Title | DOI |
|---|---|---|---|---|---|
| [17032985](https://pubmed.ncbi.nlm.nih.gov/17032985/) | 312 | 2006 | JAMA | Translation of research evidence from animals to humans. | [10.1001/jama.296.14.1731](https://doi.org/10.1001/jama.296.14.1731) |
| [28893587](https://pubmed.ncbi.nlm.nih.gov/28893587/) | 60 | 2017 | Toxicol Appl Pharmacol | Current nonclinical testing paradigm enables safe entry to First-In-Human clinical trials: The IQ consortium nonclinical to clinical translational database. | [10.1016/j.taap.2017.09.006](https://doi.org/10.1016/j.taap.2017.09.006) |
| [17988725](https://pubmed.ncbi.nlm.nih.gov/17988725/) | 46 | 2008 | Theriogenology | Are animal models as good as we think? | [10.1016/j.theriogenology.2007.09.030](https://doi.org/10.1016/j.theriogenology.2007.09.030) |
| [29730448](https://pubmed.ncbi.nlm.nih.gov/29730448/) | 43 | 2018 | Regul Toxicol Pharmacol | A big data approach to the concordance of the toxicity of pharmaceuticals in animals and humans. | [10.1016/j.yrtph.2018.04.018](https://doi.org/10.1016/j.yrtph.2018.04.018) |
| [25814248](https://pubmed.ncbi.nlm.nih.gov/25814248/) | 42 | 2015 | Eur J Pharmacol | Translational value of animal models of kidney failure. | [10.1016/j.ejphar.2015.03.026](https://doi.org/10.1016/j.ejphar.2015.03.026) |
| [25671556](https://pubmed.ncbi.nlm.nih.gov/25671556/) | 39 | 2015 | Hum Gene Ther Clin Dev | Dog models for blinding inherited retinal dystrophies. | [10.1089/humc.2014.155](https://doi.org/10.1089/humc.2014.155) |
| [22303754](https://pubmed.ncbi.nlm.nih.gov/22303754/) | 30 | 2011 | J Knee Surg | Using animal models in osteoarthritis biomarker research. | [10.1055/s-0031-1297361](https://doi.org/10.1055/s-0031-1297361) |
| [29143114](https://pubmed.ncbi.nlm.nih.gov/29143114/) | 27 | 2018 | Cancer Immunol Immunother | Cancer vaccine strategies: translation from mice to human clinical trials. | [10.1007/s00262-017-2084-x](https://doi.org/10.1007/s00262-017-2084-x) |
| [15246820](https://pubmed.ncbi.nlm.nih.gov/15246820/) | 27 | 2004 | Exp Neurol | Lost in translation: taking neuroprotection from animal models to clinical trials. | [10.1016/j.expneurol.2004.05.008](https://doi.org/10.1016/j.expneurol.2004.05.008) |
| [26753942](https://pubmed.ncbi.nlm.nih.gov/26753942/) | 21 | 2015 | Altern Lab Anim | Predicting human drug toxicity and safety via animal tests: can any one species predict drug toxicity in any other, and do monkeys help? | [10.1177/026119291504300607](https://doi.org/10.1177/026119291504300607) |
| [28903488](https://pubmed.ncbi.nlm.nih.gov/28903488/) | 15 | 2017 | Toxicol Sci | An Analysis of the Relationship Between Preclinical and Clinical QT Interval-Related Data. | [10.1093/toxsci/kfx125](https://doi.org/10.1093/toxsci/kfx125) |
| [28543848](https://pubmed.ncbi.nlm.nih.gov/28543848/) | 12 | 2018 | J Appl Toxicol | Non-animal assessment of skin sensitization hazard: Is an integrated testing strategy needed, and if so what should be integrated? | [10.1002/jat.3479](https://doi.org/10.1002/jat.3479) |
| [26856335](https://pubmed.ncbi.nlm.nih.gov/26856335/) | 12 | 2016 | Eur J Appl Physiol | The rat closely mimics oxidative stress and inflammation in humans after exercise but not after exercise combined with vitamin C administration. | [10.1007/s00421-016-3336-8](https://doi.org/10.1007/s00421-016-3336-8) |
| [32152206](https://pubmed.ncbi.nlm.nih.gov/32152206/) | 9 | 2020 | Diabetes | Connecting Rodent and Human Pharmacokinetic Models for the Design and Translation of Glucose-Responsive Insulin. | [10.2337/db19-0879](https://doi.org/10.2337/db19-0879) |
| [35616311](https://pubmed.ncbi.nlm.nih.gov/35616311/) | 7 | 2022 | J R Soc Med | The role of systematic reviews in identifying the limitations of preclinical animal research, 2000-2022: part 2. | [10.1177/01410768221100970](https://doi.org/10.1177/01410768221100970) |
| [32413492](https://pubmed.ncbi.nlm.nih.gov/32413492/) | 7 | 2021 | Drug Discov Today | Rodent models of diabetic kidney disease: human translatability and preclinical validity. | [10.1016/j.drudis.2020.05.004](https://doi.org/10.1016/j.drudis.2020.05.004) |
| [35781406](https://pubmed.ncbi.nlm.nih.gov/35781406/) | 4 | 2023 | Clin Oncol (R Coll Radiol) | A Multicentre Clinical Study of Sarcoma Personalised Treatment Using Patient-Derived Tumour Xenografts. | [10.1016/j.clon.2022.06.002](https://doi.org/10.1016/j.clon.2022.06.002) |
| [34968630](https://pubmed.ncbi.nlm.nih.gov/34968630/) | 4 | 2022 | Regul Toxicol Pharmacol | Evaluation of the predictivity of Acute Oral Toxicity (AOT) structure-activity relationship models. | [10.1016/j.yrtph.2021.105109](https://doi.org/10.1016/j.yrtph.2021.105109) |
| [38852684](https://pubmed.ncbi.nlm.nih.gov/38852684/) | 3 | 2024 | J Pharmacol Toxicol Methods | A simple accurate method for concentration-QTc analysis in preclinical animal models. | [10.1016/j.vascn.2024.107528](https://doi.org/10.1016/j.vascn.2024.107528) |
| [38676802](https://pubmed.ncbi.nlm.nih.gov/38676802/) | 3 | 2024 | Methods Mol Biol | Patient-Derived Xenograft Models for Translational Prostate Cancer Research and Drug Development. | [10.1007/978-1-0716-3858-3_12](https://doi.org/10.1007/978-1-0716-3858-3_12) |
| [33813006](https://pubmed.ncbi.nlm.nih.gov/33813006/) | 3 | 2021 | J Pharmacol Toxicol Methods | Core battery safety pharmacology testing - An assessment of its utility in early drug development. | [10.1016/j.vascn.2021.107055](https://doi.org/10.1016/j.vascn.2021.107055) |
| [33085125](https://pubmed.ncbi.nlm.nih.gov/33085125/) | 3 | 2021 | J Appl Toxicol | Prediction of acute inhalation toxicity using cytotoxicity data from human lung epithelial cell lines. | [10.1002/jat.4090](https://doi.org/10.1002/jat.4090) |
| [32735877](https://pubmed.ncbi.nlm.nih.gov/32735877/) | 3 | 2020 | J Pharmacol Toxicol Methods | A Bayesian approach to toxicological testing. | [10.1016/j.vascn.2020.106898](https://doi.org/10.1016/j.vascn.2020.106898) |
| [30726989](https://pubmed.ncbi.nlm.nih.gov/30726989/) | 3 | 2019 | Toxicol Sci | Preclinical to Clinical Translation of Hemodynamic Effects in Cardiovascular Safety Pharmacology Studies. | [10.1093/toxsci/kfz035](https://doi.org/10.1093/toxsci/kfz035) |
| [40418625](https://pubmed.ncbi.nlm.nih.gov/40418625/) | 2 | 2025 | Clin Pharmacol Ther | An Integrated AI-PBPK Platform for Predicting Drug In Vivo Fate and Tissue Distribution in Human and Inter-Species Extrapolation. | [10.1002/cpt.3732](https://doi.org/10.1002/cpt.3732) |
| [40054526](https://pubmed.ncbi.nlm.nih.gov/40054526/) | 2 | 2025 | J Pharm Sci | Physiologically-based modeling of methylprednisolone pharmacokinetics across species with extrapolations to humans. | [10.1016/j.xphs.2025.103719](https://doi.org/10.1016/j.xphs.2025.103719) |
| [38910363](https://pubmed.ncbi.nlm.nih.gov/38910363/) | 2 | 2024 | Altern Lab Anim | In Silico Phototoxicity Prediction of Drugs and Chemicals by using Derek Nexus and QSAR Toolbox. | [10.1177/02611929241256040](https://doi.org/10.1177/02611929241256040) |
| [39093553](https://pubmed.ncbi.nlm.nih.gov/39093553/) | 1 | 2024 | Crit Rev Toxicol | Evaluation of rat and rabbit embryofetal development studies with pharmaceuticals: the added value of a second species. | [10.1080/10408444.2024.2374281](https://doi.org/10.1080/10408444.2024.2374281) |
| [38688826](https://pubmed.ncbi.nlm.nih.gov/38688826/) | 1 | 2024 | Int J Cancer | Human-mouse comparison of the multistage nature of radiation carcinogenesis in a mathematical model. | [10.1002/ijc.34987](https://doi.org/10.1002/ijc.34987) |
| [38642821](https://pubmed.ncbi.nlm.nih.gov/38642821/) | 1 | 2024 | Toxicology | Sex, age, and species differences of perfluorooctanoic acid modeled by flow- versus permeability-limited physiologically-based pharmacokinetic models. | [10.1016/j.tox.2024.153806](https://doi.org/10.1016/j.tox.2024.153806) |
| [26563791](https://pubmed.ncbi.nlm.nih.gov/26563791/) | 1 | 2015 | Handb Clin Neurol | Extrapyramidal system neurotoxicity: animal models. | [10.1016/B978-0-444-62627-1.00012-3](https://doi.org/10.1016/B978-0-444-62627-1.00012-3) |
| [42245789](https://pubmed.ncbi.nlm.nih.gov/42245789/) | 0 | 2026 | Res Sq | Leveraging Dog Models to Uncover Human Cancer Insights. | [10.21203/rs.3.rs-9783746/v1](https://doi.org/10.21203/rs.3.rs-9783746/v1) |
| [26803853](https://pubmed.ncbi.nlm.nih.gov/26803853/) | 0 | 2015 | National Academies Press (US) | The Role of Clinical Studies for Pets with Naturally Occurring Tumors in Translational Cancer Research: Workshop Summary | [10.17226/21830](https://doi.org/10.17226/21830) |
| [20806453](https://pubmed.ncbi.nlm.nih.gov/20806453/) | 0 | 2007 | The Publishing House of the Romanian Academy | Comparative Oncology | — |
