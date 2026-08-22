# Full texts still needed

**0** eligible studies lack full text.
(56 eligible of 100 screened; 56 eligible already held.)

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
