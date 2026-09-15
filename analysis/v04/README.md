# v0.4 pipeline

Implements `PLAN.md` v0.4 (tag `protocol-v0.4`). Writes only to `data/v04/`; the live site still
builds from `data/db/` and is untouched until v0.4 outputs replace it.

## Step 1 — verification workflow on the existing corpus

| Stage | Script | Output | What it does |
|---|---|---|---|
| 1 | `s1_scope.py` | `s1_scope.json` | Two models classify each study's index tests; include / provisional / exclude / PDX |
| 2 | `s2_extract.py` | `s2_extract.json` | Two models extract animal-vs-human comparisons from the PDF, blind to the review's aims |
| 3 | `s3_locate_align.py` | `s3_items.json` | No model: finds each value and quote in the PDF text layer; pairs A's and B's records |
| 4 | `s4_verify.py` | `s4_verify.json` | The other model family checks each record against the located page (9-item checklist) |
| 5 | `s5_decide.py` | `s5_decisions.json`, `review_queue.json`, `audit_sample.json`, `canary_report.json`, `step1_report.md` | Accept / exclude / flag; canaries; seeded audit sample |
| 6 | `s6_review_page.py` | `review/index.html` | Review page; decisions are stored in the published artifact's database |
| 7 | `s7_import_review.py` | `s7_final.json`, `audit_result.json` | Applies exported decisions; audit false-accept rate with exact 95% CI |

Export decisions before stage 7: Artifact `read_db` on collections `resolutions` and `audit` with
`out_dir: data/v04/review/db`.

## Step 1b — drug-pair pilot (dogs and cats)

| Script | Output | What it does |
|---|---|---|
| `f1_cotc_frame.py` | `frames/cotc.json` | Every NCI COTC trial (open and completed) |
| `f2_pubmed_frame.py` | `frames/pubmed_companion.json` | Systematic PubMed frame; query logged in `protocol/search_strings.md` |
| `p1_pilot_screen.py` | `pilot/screen.json` | Seeded random order; two-model screen until 25 qualify |
| `p2_pilot_pairs.py` | `pilot/pairs.json`, `pilot/pilot_report.md` | Pilot 1 (superseded, kept as record): human evidence from PubMed search; failed its gate, see `pilot/pilot_findings.md` |

### Pilot 2 — human side from reference-data snapshots (amendment A5)

| Script | Output | What it does |
|---|---|---|
| `f3_snapshots.py` | `data/raw/snapshots/` (gitignored), `frames/snapshots_manifest.json` | Downloads Drugs@FDA, openFDA NDC and labels, AACT ClinicalTrials.gov export; records URL, size, SHA-256 |
| `f4_human_index.py` | `frames/human_index.json` (gitignored, regenerable) | Ingredients in US human medicine, with FDA applications and label indications; `lookup(name)` |
| `f5_aact_sqlite.py` | `data/raw/snapshots/aact/aact_subset.sqlite` | ClinicalTrials.gov tables needed for classification, plus trial-to-ingredient links by name matching |
| `p3_pilot2.py` | `pilot2/pairs.json`, `pilot2/pilot2_report.md` | Test-agent roles (two models) → lookup → exhaustive local retrieval → condition correspondence (two models, choosing from retrieved lists) → evidence hierarchy → §7.4 in code |

Build order after a new snapshot: `f3 → f4 → f5 → p3`.

## Conventions

- Model tier per stage: `AMC_TIER` or `AMC_TIER_<STAGE>` (default 1). Ladder in `common.py`.
  Escalate only on a trigger in PLAN §8.2, re-running the whole stage.
- Every LLM response is cached in `data/v04/cache/` (gitignored), keyed on model, prompt, schema
  and PDF hash. Re-running a stage costs nothing unless an input changed.
- Output that cannot be parsed is not retried (at temperature 0 it repeats); the item is recorded
  as an error and flagged, never dropped.
