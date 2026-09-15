# Archive: the v0.3 site

The site published at <https://rohitium.github.io/animal-model-concordance/> was replaced on
2026-09-14 by the v0.4 build (`analysis/v04/s1_build_site.py` → `site/v04_build/`). The v0.3 site
is retired, not deleted.

**What it was.** 100 screened studies, 56 eligible, a figure-level extraction, and a table of
assessment × organism rows. Its numbers are superseded: v0.4 re-ran retrieval, screening,
extraction, verification and adjudication under a protocol frozen before data collection
(`PLAN.md`, tag `protocol-v0.4`), and covers 1,494 results in 406 studies.

**How to get it back.**

```bash
git checkout site-v0.3
python3 analysis/33_build_site.py
python3 -m http.server 8811 --directory site/_build
```

The tag `site-v0.3` marks the last commit whose CI build produced the old live site. Its builder
(`analysis/33_build_site.py`) and its data (`data/db/*.json`) are still in the repository on `main`
and still run; nothing but the deploy target changed.

**Why it was replaced rather than kept alongside.** The two builds answer the same question with
different corpora and different methods. Serving both would invite reading one as a check on the
other, which it is not.
