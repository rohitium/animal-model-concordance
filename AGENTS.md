# Working on this project

A structured reading of the published literature that **measures** how well animal results
correspond to human clinical outcomes. Live at
<https://rohitium.github.io/animal-model-concordance/>, built in CI from the committed data
on every push to `main`.

**Redesign in progress (2026-09-14):** `PLAN.md` is now protocol v0.4 (question-first; evidence
map, dog/cat drug-pair table, verification workflow; see amendment A4). The state and pipeline
described below are v0.3 and still drive the live site, which stays unchanged until v0.4 outputs
replace it.

Read `PLAN.md` (protocol, v0.4), `protocol/amendments.md` (dated deviations) and
`docs/limitations.md` (68 numbered limitations) before changing anything. The limitations
file is the honest record of what is wrong and why; add to it rather than quietly fixing.

## State as of 2026-08-22

| | |
|---|---|
| Screened | 100 candidate studies |
| Eligible | 56 |
| Read from full-text PDF | 56 (70 PDFs held, incl. excluded studies) |
| Figures extracted | 925 |
| …quoted from other papers, so not that study's evidence | 206 |
| Studies with a numeric score | 27 |
| Table rows (assessment × organism) | 26 |
| Verdicts (model rater 1) | 9 supports · 29 partly · 18 does not |
| Rater 1 vs rater 2 | 73% agreement, κ 0.58 |
| Numeric rule vs rater 1 | 44%, κ 0.17 |

## Pipeline

Numbered scripts in `analysis/`, each writing to `data/db/`. Re-run in order after adding
full texts; all cache by PMID and skip completed work.

```
12,16,31  fetch open-access full text (Europe PMC, Unpaywall, OpenAlex, PMC)
13        PubMed metadata: MeSH, DOI, abstract, funding
19        classification: assessment, species, model type, endpoint class
22,23     eligibility: index test must be a live animal; comparison must be animal vs human
32        question-driven extraction from the PDF  ← the core pass
38        figure provenance: own result / re-analysis / quoted from elsewhere
37        deterministic 0-1 verdict from the figures
35        independent second verdict (different model family)
36        two-sentence synthesis per table row
33        build the site        34 + build_docx.js  build the Word export
21        regenerate docs/fulltext_wanted.md
```

After adding a PDF to `data/raw/fulltext/<PMID>.pdf`:
`32 → 38 → 37 → 36 → 33 → 34 → build_docx.js`, then commit; CI redeploys.

## Rules that took real work to get right

Each of these was wrong at some point and was corrected after a reader caught it. Do not
regress them.

1. **A figure with no species is attributed only when the study examines one organism.**
   Attributing it to every organism a paper mentions duplicated one result across eight rows.
2. **Figures quoted from other papers are not that paper's evidence** (206 of 925). Counting
   them double-counts when the original is also in the corpus. Re-analysis of others' data
   does count — pooling published results is the reviewer's own work.
3. **Qualitative comparisons are evidence.** Dropping unquantified findings preferentially
   drops negative ones, because failures are often reported without a number. This silently
   deleted the clearest negative dog result and flipped a row to favourable.
4. **A composite score's distribution is the concordance measure.** Report span, median and
   named endpoints. Do not exclude conditions the authors expected to score low; they belong
   to the distribution.
5. **Never name a merged span after one of its members.** A row read "78.2–85.05% for adult
   bladder cancer" when bladder was 85.05% and 78.2% was head and neck.
6. **Ratios, odds ratios and fold-changes are convertible but are not pooled.** Adding them to
   the score moves agreement with independent readers to chance. p-values and unbounded
   distances cannot be converted at all.
7. **Do not compare organisms across assessments.** Dog evidence is mostly toxicology, mouse
   mostly efficacy and disease biology; the apparent organism effect is largely an assessment
   effect.
8. **Never cite a script or a page number on the site.** Readers should not open source code
   to learn what a number means, and page numbers read off a PDF may not be the journal's.

## What this project is for

It supports a decision about whether companion-animal clinical trials are a viable basis for a
biotech platform. Report what the studies show, in both directions, and let the reader draw the
conclusion.

Two points of fact that took work to establish and are easy to get wrong:

- **Organism comparisons are valid within a study, not across the table.** 18 studies report one
  statistic for more than one organism — Atkins et al. 2020 gives median positive predictive
  values of 0.38 (dog), 0.43 (mouse), 0.41 (rat), 0.60 (non-human primate); Bailey et al. 2015
  and Monticello et al. 2017 give comparable per-species breakdowns. Those are legitimate
  comparisons. Reading the main table's organism rows against each other is not, because dog
  evidence sits mostly in toxicology and mouse evidence mostly in efficacy and disease biology.
- **Arm 4 is thin in this corpus.** A targeted search for veterinary-patient studies returned 174
  records and one met the inclusion rule, which requires a quantitative animal-to-human agreement
  statistic in the same paper. Most comparative-oncology work is either a canine trial without a
  paired human comparison, or a review. That is a statement about what this rubric retrieves, not
  a verdict on the field.

## Known weaknesses, in priority order

1. **Nothing is human-verified.** Roughly 1% of the 925 figures have been checked. Every
   defect found so far was found by a person reading one paper against the site, not by
   internal checks. A stratified verification sample of ~50 figures, with the measured error
   rate published, is the highest-value next step.
2. **The three verdicts agree poorly** (κ 0.17–0.58). The figures are the evidence; the labels
   are contested. The site says so; keep it that way.
3. **The corpus is not a random sample** — selected by citations and recency from a screened
   pool. Verdict tallies describe this corpus only.
4. **Arm 4 (veterinary) rests on two studies.** SQ7 in `PLAN.md` is unanswered.
5. `data/db/measurements.json` and several `*_scope`/`*_refined` files are from the superseded
   bottom-up extraction. The site no longer reads them; they are kept for provenance and could
   be removed.

## Conventions

- `.env` holds `OPENROUTER_API_KEY`; gitignored, never commit it or read it into output.
- `data/raw/fulltext/` holds copyrighted PDFs; gitignored, never publish them. Only extracted
  data reaches the site.
- Parallelise API passes (8 workers is fine); sequential runs waste ~8×.
- Check `max_tokens` against the model's real ceiling before assuming truncation is a content
  problem.
- Verify by fetching the deployed page and comparing with the local build. A green CI run
  means the job executed, not that the intended content is live — that mistake published a
  stale build twice.
