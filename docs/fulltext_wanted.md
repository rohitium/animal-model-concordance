# Full texts still needed

**2** eligible studies lack full text.
(61 eligible of 100 screened; 59 eligible already held.)

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
| [42245789](https://pubmed.ncbi.nlm.nih.gov/42245789/) | 0 | 2026 | veterinary | Res Sq | Leveraging Dog Models to Uncover Human Cancer Insights. | [10.21203/rs.3.rs-9783746/v1](https://doi.org/10.21203/rs.3.rs-9783746/v1) |
