# Full texts still needed

**0** eligible studies lack full text.
(57 eligible of 100 screened; 57 eligible already held.)

15 further records without full text were **excluded** under rubric r3 (in silico only, in vitro only, human only, or reporting no animal-to-human agreement statistic) and are deliberately omitted below &mdash; they are not needed.

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

## PDFs wanted (full text already held as XML)

These **6** studies are included and we have their text, but only as
XML. Extraction now reads the PDF so the model can see tables and figures, which is
where most concordance numbers live. A PDF would improve these records; they are not
blocked without one.

Save as `data/raw/fulltext/<PMID>.pdf` (it will replace nothing — the XML stays).

| PMID | Cites | Year | Arm | Journal | Title | DOI |
|---|---|---|---|---|---|---|
| [27261415](https://pubmed.ncbi.nlm.nih.gov/27261415/) | 300 | 2016 | disease-biology | J Hepatol | A diet-induced animal model of non-alcoholic fatty liver disease and hepatocellular cancer. | [10.1016/j.jhep.2016.05.005](https://doi.org/10.1016/j.jhep.2016.05.005) |
| [32868897](https://pubmed.ncbi.nlm.nih.gov/32868897/) | 51 | 2020 | toxicology | Br J Cancer | Pre-clinical animal models are poor predictors of human toxicities in phase 1 oncology clinical trials. | [10.1038/s41416-020-01033-x](https://doi.org/10.1038/s41416-020-01033-x) |
| [22790876](https://pubmed.ncbi.nlm.nih.gov/22790876/) | 49 | 2012 | efficacy | Eur J Nucl Med Mol Imaging | Can animal data predict human outcome? Problems and pitfalls of translational animal research. | [10.1007/s00259-012-2175-z](https://doi.org/10.1007/s00259-012-2175-z) |
| [28731442](https://pubmed.ncbi.nlm.nih.gov/28731442/) | 16 | 2017 | disease-biology | J Alzheimers Dis | Of Mice and Men: Comparative Analysis of Neuro-Inflammatory Mechanisms in Human and Mouse Using Cause-and-Effect Models. | [10.3233/JAD-170255](https://doi.org/10.3233/JAD-170255) |
| [39255793](https://pubmed.ncbi.nlm.nih.gov/39255793/) | 5 | 2024 | disease-biology | Cell Rep Methods | PTMoreR-enabled cross-species PTM mapping and comparative phosphoproteomics across mammals. | [10.1016/j.crmeth.2024.100859](https://doi.org/10.1016/j.crmeth.2024.100859) |
| [36730203](https://pubmed.ncbi.nlm.nih.gov/36730203/) | 3 | 2023 | disease-biology | Proc Natl Acad Sci U S A | Transcriptomic congruence analysis for evaluating model organisms. | [10.1073/pnas.2202584120](https://doi.org/10.1073/pnas.2202584120) |
