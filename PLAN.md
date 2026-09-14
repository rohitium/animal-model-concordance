# Animal Model Concordance with Human Clinical Outcomes
## Protocol — v0.4 (draft for sign-off)

**Date:** 2026-09-14
**Status:** Draft. Step 0 of §11. No v0.4 data collected. Once signed off, this file is frozen
in a tagged commit; every later change goes in `protocol/amendments.md` with a date and reason.
**Changes from v0.3:** see amendment A4. In short: the unit of analysis moves from "every number
a concordance paper prints" to four pre-specified questions; a disease-area × species evidence
map replaces the arm × organism table; a drug-by-drug companion-animal table (dogs and cats) is
added; every headline number passes a staged verification workflow with a measured error rate.
**Archived:** `protocol/v0.1_archive.md`, `v0.2_archive.md`, `v0.3_archive.md`.

---

## 1. Purpose and stance

This review is the evidence base behind the Nori white paper's claims about animal-model
concordance (currently the table on p15). It is therefore **not neutral in motivation**, and the
design has to compensate for that. We are the people most likely to be fooled by this analysis,
because we already know which answer we would like.

Commitments that follow from that:

1. **Rules before results.** Questions, eligibility, classification criteria and analysis code
   are fixed here before outcomes are extracted. Changes are dated amendments, never silent edits.
2. **Stated falsifiers** (§3). If the data say the thesis is wrong, the p15 replacement says so.
3. **Blind extraction.** Extraction prompts never mention Nori, companion animals as a thesis, or
   a hoped-for direction. Extraction records; interpretation is a separate, later step.
4. **Deliberate search for disconfirming evidence** (§6.4), with its yield reported.
5. **Adversarial reading.** Every headline row is given to a separate agent instructed to argue
   the opposite conclusion from the same evidence; its strongest objection is published beside
   the row.
6. **Measured, published error rate** for the extraction itself (§8).
7. **Everything is reported in both directions.** Negative, null and indeterminate results stay
   in the denominator.

## 2. Questions

| # | Question | Output |
|---|---|---|
| **Q1** | For each disease area and species, what kind and strength of evidence exists that the animal corresponds to humans? | Evidence map (§4) |
| **Q2** | Where studies in the same cell report the same metric, what is the pooled estimate? | Pooled estimates with CI and prediction interval (§9) |
| **Q3** | When a drug was tested in dogs or cats with **spontaneous** disease and in humans, did the results agree? | Drug-pair table and 2×2 tables (§7) |
| **Q4** | For the same drug, do spontaneous-disease dogs/cats agree with humans more often than induced laboratory models do? | Within-drug paired comparison (§7.6) |

Q3 and Q4 are the questions the white paper's thesis depends on. Q1 and Q2 provide context and
guard against over-reading Q3.

## 3. Pre-specified falsifiers and reporting rules

Written before any v0.4 data are seen. Each result is reported whichever way it falls. The
object of measurement is **concordance** between animal results and human outcomes.

- **F1 (Q4).** If, across drugs with results in all three (lab model, spontaneous companion
  animal, human), companion-animal concordance with human outcomes is not higher than lab-model
  concordance, the p15 replacement states plainly that concordance did not differ between
  companion animals and laboratory models, with the difference and its 95% CI.
- **F2 (Q3).** Every drug pair meeting §7 criteria is reported, however few. If fewer than 10
  meet criteria, that is stated plainly, alongside the concordance proportion with an exact
  (Clopper–Pearson) 95% CI. No evidence is withheld for being sparse.
- **F3 (Q1).** If spontaneous-disease dog/cat cells contain only level C/D evidence (§4.3), the
  map shows that, and no claim of demonstrated clinical concordance is made for them.
- **F4 (terms).** A pair or cell is called **discordant** only when all available evidence
  points in the opposite direction. Where evidence points both ways it is **mixed**; where it
  cannot be classified it is **indeterminate**. Efficacy and safety are classified separately,
  each with these terms.

## 4. Evidence map (Q1)

### 4.1 Disease areas (rows)
Assigned by the **human** condition being compared. A study comparing several areas contributes
to each, per comparison, never per study. The list below is a starting set, not a closed
vocabulary: when a comparison fits no row, a new row is created (never forced into the nearest
one) and logged in `protocol/amendments.md` with the comparison that prompted it.

oncology · immunology/inflammation · infectious disease · cardiovascular · metabolic/endocrine ·
renal · liver/GI · neurology (stroke, neurodegeneration, epilepsy) · psychiatry/addiction ·
pain/musculoskeletal · respiratory · ophthalmology · haematology · dermatology ·
reproductive/developmental · **cross-cutting toxicology/safety** (not disease-specific)

### 4.2 Species (columns)
mouse · rat · other rodent · rabbit · pig/minipig · sheep/goat · non-human primate ·
**laboratory dog** · **companion dog (spontaneous disease)** · laboratory cat ·
**companion cat (spontaneous disease)** · horse · zebrafish · *Drosophila* · *C. elegans* ·
grouped label (e.g. "rodent", "non-rodent" — kept as the paper reports it, never expanded).

Laboratory and companion dogs/cats are separate columns. A healthy or induced-disease beagle and
a client-owned dog with naturally occurring disease are different models.

Each cell also records `model_type ∈ {induced, engineered, spontaneous-lab, spontaneous-companion,
healthy}`.

### 4.3 Evidence levels (what a cell contains)
| Level | Definition | Typical metric |
|---|---|---|
| **A — Outcome concordance** | Intervention results in the animal compared with intervention results in humans | concordance proportion, translation rate, effect-size ratio |
| **B — Safety/toxicity concordance** | Animal toxicity or safety findings compared with human adverse events | sensitivity, specificity, PPV, NPV, LR+, iNLR |
| **C — Biological similarity** | Molecular, pathological or physiological resemblance measured against human data, no intervention outcome | correlation, overlap, similarity score |
| **D — Asserted only** | Resemblance claimed without an animal-vs-human measurement | count of records only |

A cell shows, per level: number of studies, number of independent datasets, direction, and (where
§9 allows) a pooled estimate. **Levels are never combined into one number**, and cells are
compared only at the same level and metric.

### 4.4 Eligibility for Q1/Q2
Include: a whole, live non-human animal (or a spontaneous-disease animal population) compared
quantitatively with human data, as the study's own result or its own re-analysis of others' data.

Exclude from levels A–C: in vitro or ex vivo systems, including cells or tissue taken from animals
(organoids, organ-chips, cultured tenocytes); in silico methods; within-species comparisons;
figures quoted from other studies. Patient-derived xenografts are recorded in a separate stratum
and never pooled with animal-model concordance.

Level D records are counted from screened records and not extracted further.

Preprints are eligible, flagged `peer_reviewed: false`, and shown as such wherever they appear.

## 5. Unit of extraction

One **comparison**: `{study, disease_area, human_condition, species, model_type, level, metric,
value, CI, n, n_unit, denominator, dataset_id, provenance, locator}`.

`dataset_id` identifies the underlying data source (e.g. a regulatory database, a consortium
dataset) so that two papers analysing the same data are not counted as independent.

Only comparisons that answer §2 are extracted. Descriptive numbers a paper prints for other
purposes are not.

## 6. Retrieval

### 6.1 Seeds
- The 56 currently eligible studies, re-screened under §4.4.
- The systematic reviews included in Ineichen et al. 2024 (PLOS Biol, umbrella review of
  animal-to-human translation), as level A seeds by disease area.
- Known anchors not yet held: Hackam & Redelmeier 2006, van der Worp 2010, Clark &
  Steger-Hartmann 2018, and level B/C anchors identified during the work.

### 6.2 Searches per disease area
PubMed search per disease area × level, logged in `protocol/search_strings.md` with the exact
string, date and hit count. Screening by the §8 model ladder, with a human-checked sample
reporting sensitivity.

### 6.3 Citation chasing
Backward and forward from every included study, one generation, then to closure if yield is
over 5%.

### 6.4 Disconfirming-evidence searches
Dedicated searches for (a) companion-animal results that did not translate to humans,
(b) companion-animal safety problems, (c) critiques of comparative oncology. Yield reported
separately.

### 6.5 Full text
Open-access routes first. Anything unavailable is listed in `docs/fulltext_wanted.md` for the
user to supply through institutional access. No study is excluded for lack of a PDF; it is held
as `awaiting_fulltext`.

## 7. Drug-pair table — dogs and cats (Q3, Q4)

### 7.1 Unit
One **drug (or biologic, or defined target) × indication**, with at least one result in dogs or
cats with **spontaneous, naturally occurring** disease and a corresponding human result.

### 7.2 Sampling frames (the denominator comes first)
To avoid building the table from well-known successes, candidates come from complete lists:
1. All trials run by the NCI Comparative Oncology Trials Consortium.
2. All FDA CVM approvals for dogs and cats (Green Book), cross-referenced to human drugs via
   DrugCentral.
3. The AVMA Animal Health Studies Database (registered veterinary clinical studies).
4. A systematic PubMed search for client-owned / naturally occurring disease trials in dogs and
   cats.

Every candidate is recorded, including those with no human counterpart (reported as a count).
Named exemplars (RPE65, toceranib, anti-NGF, oclacitinib/lokivetmab) are checked for presence in
the frames, not added by hand. If an exemplar is missing from all frames, that is reported as a
frame gap.

### 7.3 Fields
Per side (companion animal, human; lab model where available): population, spontaneous vs
induced, design (RCT / single-arm / observational), n, primary endpoint, effect with CI, safety
findings, source identifiers (PMID / NCT / regulatory document), and **date of first public
result**.

### 7.4 Classification (pre-specified; confirmed in the pilot, then frozen)
Efficacy, per side:
- **positive:** RCT meeting its primary efficacy endpoint; or regulatory approval for the
  indication; or, for single-arm trials only, objective response rate by VCOG/RECIST criteria
  ≥ 20% (oncology) or a pre-specified validated outcome measure improved (non-oncology);
- **negative:** RCT failing its primary efficacy endpoint; or development stopped for lack of
  efficacy;
- **indeterminate:** anything else. Kept and reported, never dropped.

Safety, per side: **signal** (dose-limiting or label-relevant toxicity in the same organ system)
/ **no signal** / **indeterminate**.

Results are tabulated as 2×2 (animal ± × human ±) for efficacy and for safety separately, with
indeterminate counts shown alongside. Each pair is then labelled, per F4: **concordant** (all
available animal and human evidence in the same direction), **discordant** (all in opposite
directions), **mixed** (both), or **indeterminate**. Concordance proportions are reported with
exact 95% CIs.

**Threshold sensitivity.** ORR ≥ 20% is the primary threshold and deliberately a high bar, so the
most clearly concordant single-arm cases are identified first. The table is then re-classified at
lower pre-specified thresholds (ORR ≥ 10%; any objective response), and each result is reported
alongside the primary one, never in place of it.

The criteria above are frozen at sign-off. The 10-pair pilot (§11) tests whether they can be
applied consistently; any change is made and logged **before** the full set is classified.

### 7.5 Dates
The date of each side's first public result is recorded for provenance. It is descriptive only
and does not change how a pair is classified.

### 7.6 Within-drug comparison (Q4)
For each pair, locate the induced or engineered laboratory-model efficacy result for the same
drug and indication, classified by the same rules. Concordance with human outcomes is compared
between lab model and companion animal **within drugs**, so drug-level confounders cancel.
Reported as the difference in concordance proportions with a paired 95% CI.

### 7.7 Declared biases
Veterinary trials are smaller and more often single-arm (a weaker design can look like better
concordance); publication bias on both sides; drugs reach dog trials because they already looked
promising (selection on the outcome); human-first pairs dominate repurposing. Each is reported
with its expected direction.

## 8. Verification workflow

### 8.1 Stages, per comparison
1. **Double extraction** by two different model families, independently, from the PDF.
2. **Mechanical location.** The value is searched for in the PDF text layer and extracted tables;
   page and character span recorded. Found only in a figure image → flagged.
3. **Verifier.** A model receives the comparison and the located page (text, plus page image if
   needed) and answers a fixed checklist: value present; same species; same metric; same
   denominator; own result vs quoted; animal-vs-human; in scope under §4.4; correct level.
4. **Decision.** Auto-accepted only if both extractions agree, the value is located, and every
   checklist item passes. Otherwise it goes to the review queue with the failing item, the quote
   and the page reference.
5. **Human review.** The user resolves flagged items. Resolutions are stored as data, with the
   reviewer and date.

Drug-pair records (§7) pass the same stages, per field.

### 8.2 Model ladder
Start with the cheapest models and move up only on measured failure.

| Tier | Models (two families) |
|---|---|
| 1 | `google/gemini-2.5-flash-lite`, `openai/gpt-5-nano` |
| 2 | `google/gemini-2.5-flash`, `openai/gpt-5-mini` |
| 3 | chosen at the time, on evidence |

A stage moves up one tier if **any** of: a canary (§8.3) is missed; the audit false-accept rate
(§8.4) exceeds 5%; the flag rate exceeds 30%, making the review queue unworkable; or the model
cannot read the input (e.g. tables in PDFs). On escalation the stage is re-run for all items, so
each stage's outputs come from one model. Tier, model and date are recorded per output.

### 8.3 Canaries
Known errors from the v0.3 data, seeded into the first run. The workflow must catch each:
- Perel 2007 (17175568): odds ratio 4.2 attached to a quote reporting 12.5; headline result
  (3 of 6 interventions concordant) not extracted; animal treatment effects recorded as
  concordance.
- Tenocyte study (34127759): cultured cells, out of scope.
- Liver-Chip (31694927) and 3D GI microtissue (30364994): in vitro, out of scope.
- Bailey 2016 (26753942): Table 4 condenses the authors' earlier papers; not solely own result.
- Daluwatumulle 2026 (42245789): preprint; transcriptomic similarity is level C, not A.
- Leenaars 2019 (31307492): toxicology figures placed in an efficacy row.

### 8.4 Audit
A random sample of 30 auto-accepted comparisons per stage is checked by the user. The
false-accept rate and its 95% CI are published. The sample is drawn by a seeded script, not
chosen.

## 9. Synthesis

- Pooling only within one cell, one level, one metric, and only with **k ≥ 3 independent
  datasets**; otherwise descriptive (values listed with n).
- Proportions: random effects, REML, logit or Freeman–Tukey transform; report τ², I² and a 95%
  prediction interval. Sensitivity/specificity: bivariate model where 2×2 cells are available.
- Overlapping datasets: one estimate per `dataset_id` (the most complete report).
- Certainty per cell and per drug-pair summary: high / moderate / low / very low, from number of
  independent datasets, consistency, directness (level), and risk of bias.
- Ratios, odds ratios and fold-changes are not pooled with proportions. p-values are not
  concordance measures.

## 10. Outputs

1. **p15 replacement:** 4–6 rows. Each row: a plain claim, the number with CI, the number of
   studies and independent datasets, certainty, and the adversarial objection.
2. **Evidence map** (§4) as a heatmap coloured by highest level, with per-cell drill-down.
3. **Drug-pair table** (§7) with 2×2 summaries and the within-drug comparison.
4. **Site** as the audit trail: every number links to its source and verification status. The
   current site stays as it is until a replacement is ready.
5. Published error rate (§8.4) and the list of flagged items with their resolutions.

## 11. Order of work and gates

| Step | Work | Gate |
|---|---|---|
| 0 | This protocol; amendment A4 | User sign-off; tagged commit |
| 1 | Build the §8 workflow; run on the 56 existing studies with canaries | All canaries caught; audit done; error rate published |
| 1b | Pilot 10 drug pairs sampled from §7.2 frames (not hand-picked) | Fields fillable; §7.4 criteria applicable; any changes logged |
| 2 | Retrieval (§6) and extraction per disease area | Search log complete; screening sensitivity reported |
| 3 | Full drug-pair table | Every frame exhausted; indeterminate counts reported |
| 4 | Synthesis (§9); adversarial review; outputs (§10) | Every headline number verified; falsifiers evaluated and reported |

Steps 1 and 1b run first and in parallel: they test the two biggest unknowns (whether the checker
can be trusted, whether drug pairs can be built).

## 12. Rules carried forward
From `AGENTS.md` and `docs/limitations.md`, unchanged: grouped labels are never expanded to
species; quoted figures are not the quoting paper's evidence; qualitative comparisons are
evidence (recorded, not pooled); a span is never named after one member; organisms are not
compared across levels or assessments; no page numbers or script names are cited on the site;
full-text PDFs are never published.

## 13. Open questions
None at sign-off. Horses and other spontaneous-disease species are deferred (user decision,
2026-09-14); they may be added later by amendment.

Resolved before sign-off (2026-09-14): disease-area list accepted as a flexible starting set;
ORR ≥ 20% accepted as primary single-arm threshold with lower thresholds as sensitivity analyses;
falsifiers revised (see amendment A4).
