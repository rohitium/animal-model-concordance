# Animal Model Concordance with Human Clinical Outcomes

A systematic review quantifying how predictive animal models are of human clinical outcomes.

**Status:** pilot slice complete; full review not run. No conclusions drawn.
Protocol: [PLAN.md](PLAN.md) (v0.3). Deviations: [protocol/amendments.md](protocol/amendments.md).

## Four evidence arms

Analysed separately, never pooled — they are different prediction problems with
different base rates and regulatory histories.

| Arm | Index test | Reference standard |
|---|---|---|
| 1 — Efficacy | Induced/engineered laboratory disease model | Human trial efficacy |
| 2 — Safety pharmacology & adverse events | ICH S7A/S7B acute functional effects | Human AEs, QT, withdrawals |
| 3 — Toxicology | GLP repeat-dose, genotox, carcinogenicity, reprotox | Human target-organ toxicity |
| 4 — Veterinary / spontaneous disease | Naturally occurring disease in client-owned animals | Corresponding human result |

## What has been established

**Retrieval must be dual-mechanism.** No single PubMed query achieves both adequate
sensitivity and a screenable yield. Five query generations were measured against 29
PMID-verified anchors:

| Version | Union hits | Anchor recall |
|---|---|---|
| v1 `[tiab]` blocks | 132,092 | 53.3% |
| v2 + MeSH rescue | 1,671,757 | 93.1% |
| v3 phrase core | 530,902 | 69.0% |
| v4 7-strand union | 204,998 | 69.0% |
| v5 (current) | 88,405 | 69.0% |

The cause is not query craft: the literature has no shared vocabulary, and the
high-volume terms carry the wrong sense (`Predictive Value of Tests`[Mesh] = 245,644
records about diagnostic-test accuracy; `concordan*` = 108,835 mostly twin studies;
`translat*` = 546,492 largely protein translation).

Query union recovers 82.8% of anchors, citation chasing 79.3% — on **disjoint** failure
sets. Their union recovers 29/29.

**Arm 4 is near-empty, and that is a finding.** A targeted veterinary-patient search
returned 174 records; 1 met the inclusion rule. Well-cited comparative-oncology papers
argue that companion animals are good models without measuring concordance. SQ7 is
therefore not answerable from Track A.

## Pilot slice

100 studies: retrieved → LLM-screened (14.0% include rate) → selected by a recorded
score → extracted → rendered as a static site. Total API cost $0.13.

Extraction runs in two tiers, always labelled: open-access full text where retrievable
(46/100), abstract-only otherwise. Spot-checked against known values — Olson 2000 → 71%,
n=150; Monticello 2017 → PPV 43%, sensitivity 48%, specificity 84%, NPV 86%, n=182.

## Build the site

```bash
python3 analysis/15_build_site.py
python3 -m http.server 8811 --directory site/_build
```

## Layout

| Path | Contents |
|---|---|
| `PLAN.md` | protocol v0.3 |
| `protocol/` | search strings with hit counts, PRISMA flow, amendments, archived versions |
| `analysis/` | numbered, re-runnable pipeline (`pubmed.py`, `openrouter.py`, `rubric.py`, `normalize.py`) |
| `data/raw/` | cached API responses, scoping runs, full-text status |
| `data/screening/` | candidates, decisions, gold set, pilot results |
| `data/db/` | `studies.json`, `metadata.json`, `fulltext_extract.json` |
| `site/` | static generator output |
| `docs/` | limitations |

`data/raw/fulltext/` holds retrieved articles and is **gitignored** — full texts are
copyrighted and must never be committed or published. `.env` is likewise gitignored.

## Standing constraints

- Every quantitative claim carries n, an estimate, an interval where applicable, and a PMID.
- Evidence and opinion are separate fields, separate files, separate rendering.
- No pooled estimates until source definitions are recoded onto a common scale.
- Contested questions cite both sides together (e.g. Seok 2013 with Takao 2015).
- Absence of data is reported as absence of data.
