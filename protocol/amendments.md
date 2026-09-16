# Protocol amendments

Dated deviations from PLAN.md, with justification. Required by PRISMA 2020.

## A1 — 2026-08-20 — Retrieval redesigned as dual-mechanism

**PLAN.md §5 as written** treated the Boolean query as the retrieval mechanism and
citation chasing as "supplementary retrieval" (§5.3).

**Empirical finding (Phase 1).** No single PubMed query achieved both adequate
sensitivity and a screenable yield. Five query generations were built and measured
against 29 PMID-verified anchors:

| Version | Design | Union hits | Anchor recall |
|---|---|---|---|
| v1 | `[tiab]` blocks only | 132,092 | 53.3% |
| v2 | + MeSH rescue terms | 1,671,757 | 93.1% |
| v3 | phrase core + narrow MeSH | 530,902 | 69.0% |
| v4 | 7-strand union | 204,998 | 69.0% |
| v5 | v4 with `s3` leak fixed | see `scoping_run_v5.json` | — |

The cause is not query craft. This literature has no shared vocabulary and no MeSH
descriptor meaning "measures animal-to-human concordance"; landmark papers are titled
"Are animal models as good as we think?", "Lost in translation", "Believe it or not…".
Term-level measurement confirmed the volume drivers are semantically wrong rather than
merely broad: `Predictive Value of Tests`[Mesh] (245,644) indexes diagnostic-test accuracy,
`concordan*`[tiab] (108,835) is dominated by genetic/twin concordance, and `translat*`[tiab]
(546,492) largely matches protein translation.

**Amendment.** Retrieval is now two mechanisms of equal standing:
1. **Query union (discovery)** — a multi-strand union, screened in full.
2. **Citation chasing (recall guarantee)** — forward and backward expansion via NCBI
   elink, seeded from verified includes, iterated to closure.

Recall is reported for each mechanism separately and for their union. Neither is
claimed to be sufficient alone; measured on the anchor set, they miss **different**
records, and their union covers 29/29.

**Consequence for §12.** Phase 2 gains an explicit citation-closure step. Phase 1's
gate is restated: not "≥90% recall from one query" but "≥90% recall from the union of
both mechanisms, with each mechanism's contribution reported."

## A2 — 2026-08-20 — Anchor-set overfitting declared, second recall estimate added

Query recall was measured on an anchor set assembled from prior knowledge and then used
to guide query revision; it is optimistic by construction. Citation-network recall is
measured leave-one-out and does not depend on the vocabulary that was tuned, so it is
reported alongside as the less-contaminated estimate. Both are declared in
`docs/limitations.md`. A held-out check against reference lists of published reviews
remains required before Phase 2 closes.

## A3 — 2026-08-20 — Known bias in the citation mechanism

NCBI forward-citation links derive from PMC-deposited reference lists, so coverage is
uneven across journals. Six anchors were unreachable by citation alone, concentrated in
titles with weaker PMC deposition (*Regul Toxicol Pharmacol*, *ATLA*, *Vet Sci*). This is
a non-random gap that runs against toxicology and veterinary sources — precisely Arms 3
and 4 — and is the reason the query mechanism is retained at equal standing rather than
demoted to a supplement.

## A4 — 2026-09-14 — Question-first redesign (protocol v0.4)

**As written (v0.3 and the pipeline built on it).** Track A only: extract every animal-vs-human
number from a 100-study slice chosen by citations and recency, summarise per arm × organism, and
assign verdicts by model raters and a 0–1 median score.

**Why it changed.** A review of the pipeline and a spot-check against source PDFs found:
- in-vitro studies in the eligible set despite the L28 rule (tenocytes, Liver-Chip,
  GI microtissue);
- central studies absent or excluded for lack of a PDF (Ineichen 2024 not retrieved; Hackam 2006
  excluded with no full text; van der Worp 2010 screened but not selected);
- extractions that miss a paper's headline result (Perel 2007's 3 of 6) and record treatment
  effects as concordance;
- 355 of 925 stored "verbatim" quotes not locatable in the PDF text, many being constructed
  table-cell strings, so the quote check could not detect errors;
- rows mostly n = 1–2 and "mixed", built from incommensurable statistics; three verdict methods
  agreeing at κ 0.17–0.58.
Numbers that were captured were generally transcribed correctly (Olson 2000, Monticello 2017,
Atkins 2020, Bailey 2016 checked).

**Amendment.** v0.4 replaces the arm × organism table with four pre-specified questions: a
disease-area × species evidence map with evidence levels A–D; within-cell pooling only at k ≥ 3
independent datasets; a drug-pair table for dogs and cats with spontaneous disease, built from
complete sampling frames; and a within-drug comparison of lab model vs companion animal vs human.
Falsifiers are stated before data collection. Every headline number passes double extraction,
mechanical location in the PDF, a checklist verifier, and human review of flags, with a published
audit false-accept rate. Models start at the cheapest tier and escalate only on measured failure
(user decision). Scope of the drug-pair table is dogs and cats only (user decision). The live site
is unchanged until a replacement exists (user decision).

**Revisions before sign-off (user review, 2026-09-14).** The draft falsifiers were changed:
(1) if companion-animal concordance is not higher than lab-model concordance, this is stated
plainly as no difference, with its CI; (2) a small number of drug pairs is reported with an exact
CI rather than declared unanswerable, so no evidence is withheld; (3) the prediction-vs-agreement
distinction was removed — the object of measurement is concordance, and dates are descriptive
only; (4) "discordant" is reserved for cases where all available evidence points the opposite
way, with "mixed" and "indeterminate" otherwise. ORR ≥ 20% is kept as the primary single-arm
threshold, with lower thresholds as sensitivity analyses. Disease areas may be added as needed.

**Motivation declared.** The review supports the Nori white paper. v0.4 §1 and §3 exist to offset
that motivation, not to disguise it.

## A5 — 2026-09-14 — Drug-pair table rebuilt on reference-data snapshots (after pilot 1)

**As written (v0.4 §7).** Human counterparts found by searching PubMed for the agent and condition
and classifying the retrieved abstracts; sampling frames drawn without regard to whether the agent
exists in human medicine.

**Why it changed.** Pilot 1 (`data/v04/pilot/pilot_findings.md`) did not pass its gate: the
pilot set came out indeterminate 6, mixed 3, discordant 1, and inspection showed the labels
reflected design defects. The trial, not the tested agent, was the unit, so comparators were
paired. Every retrieved abstract was pooled. Human drug names were taken from model memory
(lotilaner mapped to fluralaner; lokivetmab to a garbled name). Relevance-ranked top-12 retrieval
could not show absence. The random PubMed frame was dominated by agents with no human form.

**Amendment (user decisions 2026-09-14).**
1. The human side is classified from frozen local snapshots of authoritative US sources, not
   live searches: Drugs@FDA (approvals and application history), the openFDA drug label and NDC
   files, and the AACT export of ClinicalTrials.gov. Each file is recorded with URL, date, size
   and SHA-256 (`data/v04/frames/snapshots_manifest.json`). Models read matched records; they do
   not find them.
2. Sampling frames are restricted to agents present in US human medicine, determined by lookup in
   those snapshots, not by a model. The unrestricted count is reported alongside.
3. US sources only. An agent approved for humans only outside the US is treated as absent from
   human medicine; declared as a limitation.
4. Carried from the pilot findings as defaults, open to user veto: one pair per tested agent
   (comparators and background therapy recorded, not paired); a fixed human evidence hierarchy
   (US approval for the indication, then registered phase 3, then phase 2, then earlier, classified
   from the highest level present); non-inferiority met = positive, superiority against an active
   comparator not shown = indeterminate; separate statuses for no human form of the disease, agent
   absent from human medicine, and no human record found.

A second 10-pair pilot under these rules precedes the full table.

## A6 — 2026-09-14 — Simplified execution; expanded search for concordance evidence

**As written (v0.4 §5, §6, §7, §8 and A5).** Two models enumerate every animal-vs-human comparison in
each study, followed by a nine-item verifier, a model-tier ladder and item-level human review. Drug
pairs are drawn from random veterinary-trial frames, with human evidence taken from registry
snapshots. The corpus is the v0.3 100-study slice, selected by citations and recency.

**Why it changed.** See `docs/retrospective_v04.md`.
- **Step 1** failed at tier 1 and tier 2 (99% and 95% flag rates; canary C1 missed both times).
  The cause was task definition: open enumeration has no single right answer, so the agreement checks
  flagged differences in how papers were carved, not errors.
- **Drug-pair pilot 2** produced 6 indeterminate pairs. Registry results are sparse and random frames
  are dominated by veterinary-only drugs.
- **The corpus is not comprehensive (user assessment).** Key studies are missing: Ineichen 2024,
  Hackam 2006, van der Worp 2010, Clark 2018.

**Amendment (user decision 2026-09-14).**
1. **Expanded retrieval** for studies reporting animal-to-human concordance evidence:
   - backward and forward citation chasing (OpenAlex, NCBI) from every included study and a named
     anchor set, including the reviews included in Ineichen 2024;
   - targeted PubMed queries per theme (efficacy translation, toxicology/safety concordance,
     cross-species disease biology, companion-animal translation);
   - title/abstract screening by two models, where either model's "include" advances a record;
   - full-text eligibility per §4.4.

   Search strings, dates, counts and anchor recall are logged in `protocol/search_strings.md`.
2. **Extraction asks one fixed question per study**: its headline animal-vs-human results, overall and
   per species or disease area, at most ~8 numbers, each with sentence and page.
   - Each number is checked mechanically against the PDF page.
   - A second model answers independently.
   - Differences are adjudicated by the reviewing agent and recorded.
   - The user spot-checks a random sample; the error rate is published.
3. **Drug pairs start from drugs**: candidate drugs come from COTC, comparative-oncology reviews,
   FDA-CVM approvals with a US human counterpart, and targeted searches, with known failures included
   deliberately. Human evidence comes from PubMed (pivotal trials, approval), with FDA data as a
   cross-check.
4. **Dropped:** item-level enumeration, the verifier ladder, the item review queue and web page,
   registry-first human evidence, and random veterinary-trial frames. Questions, falsifiers (§3) and
   classification rules (§7.4, A5 §4) are unchanged.
5. **Routine method decisions** are made by the reviewing agent and logged here or in
   `docs/limitations.md`. The user is consulted at milestones.

### A6 execution notes (reviewing agent, 2026-09-14): routine decisions, logged per the working agreement

- **Headline extraction:** one extractor (`gemini-2.5-flash`), not two. On five test studies,
  two-extractor agreement was 6 of 57 results while the values were largely correct. Agreement
  measured selection differences, not errors.
- **Per-result verifier:** `gpt-5-mini`. On the same test it rejected 8 of 10 known-bad results,
  against 0 of 10 for `gpt-4.1-mini` and 3 of 10 for `claude-haiku-4.5`.
- **Adjudication:** by `claude-sonnet-5`, once per study with all of that study's results, so that
  like results are decided alike. A seeded 10% of studies with verified results are re-checked blind
  to estimate the verifier's false-accept rate before the human spot-check.
- **Abstract screening:** `gemini-2.5-flash-lite` and `gpt-4.1-nano`. Either model's include or
  uncertain advances a record. A title-only exclusion by both models is accepted, a departure from
  L27 given ~26,000 candidates; see limitations.
- **Forward citation chasing** excludes attrition and reproducibility seeds (Hay 2014, Begley 2012,
  Prinz 2011, Wong 2019, Cummings 2014, Freedman 2015). Their citing works are not about
  animal-to-human comparison; they remain backward seeds.
- **Held-out recall check** was built from memory and proved weak: 6 of 14 titles unresolved, 2
  resolved to out-of-scope papers. To be rebuilt from exact titles in published reviews' reference
  lists.
- **Drug pairs, by relation to the human drug.** The primary table includes a pair when the dog or cat
  drug is:
  - **the same molecule** as a human drug, or
  - **a species-specific biologic** against the same target as a human product (e.g. bedinvetmab vs
    tanezumab).

  **Class analogues** (a different molecule, same mechanism: toceranib vs sunitinib, verdinexor vs
  selinexor, oclacitinib vs human JAK inhibitors) form a separate stratum. **Hand-added exemplars** are
  searched by name and reported separately from systematically found candidates.
- **Large PDFs** (over 14 MB) are sent to the model as their text layer with page markers, because of
  provider request limits.
- **"Exists in humans" includes investigational drugs.** For drug pairs, a veterinary drug has a human
  counterpart if it is in the US human-medicine index (approved or labelled) **or** is an intervention in
  at least one registered interventional trial in the ClinicalTrials.gov snapshot. Matches are by name or
  registered other name, so development codes resolve (PCI-32765 → ibrutinib).
  - **Why:** the approval-only rule dropped tanezumab and fasinumab (the anti-NGF antibodies, never
    FDA-approved, with a well-known human safety failure), plus masitinib and rabacfosadine. Removing
    unapproved drugs removes exactly the cases where human development failed, which biases the table
    towards concordance.
  - Resolution is deterministic (`analysis/v04/f7_resolve.py`) and records whether a counterpart is
    approved or investigational.
- **Name matching no longer accepts "anti-X" as ingredient X.** "Anti-nerve growth factor antibodies" had
  been matched to nerve growth factor.
- **Drug-pair records must report an efficacy result to form a pair.** Pharmacokinetic, dose-finding and
  biomarker-only records are counted but not paired.
- **Indications are merged into canonical conditions per drug.** Species words are dropped, subtypes are
  merged into the parent disease when the human counterpart is the same, and non-specific tumour mixtures
  are not paired.
- **An uncontrolled or below-threshold veterinary study is indeterminate, never negative.** The first
  exemplar run called a 4-dog pilot with no responses "discordant".
- **A second, strict screening pass was added before full text.** The first pass advanced a record if
  either fast model said include or uncertain, which advanced 15,439 of 26,335 records. That included
  4,886 records the first model had itself labelled not relevant, too many to take to full text.
  - **The strict pass** (`gemini-2.5-flash`) asks whether the paper's *own* data or pooled analysis
    compares live animals with humans, and names the common false positives.
  - **Calibration set:** 20 anchors that genuinely measure concordance. The v0.3 stage-1 includes were
    not used, because many are narrative reviews or in vitro studies the criterion correctly excludes.
    Two first-draft anchors were removed as not measuring concordance: van der Worp 2010 (an essay) and
    Sena 2010 (animal-only publication bias).
  - **Calibration result:** 18 of 20 passed on their abstracts. The other two (Hackam 2006, Perrin
    2014) have no abstract, and records without an abstract advance whenever the first pass's Gemini
    model said include or uncertain.
- **Q4 laboratory side, corrected.** The first run was invalid, found by inspecting a sample before
  reporting:
  - the reader credited studies of other compounds that used the drug only as a benchmark or comparator;
  - it counted adverse effects as efficacy failures;
  - it aggregated 25–30 studies per drug with an any-disagreement-is-mixed rule.

  The reader now requires the drug to be the treatment under test for that condition's main efficacy
  outcome. The laboratory side is positive or negative when at least 75% of its classifiable studies
  agree. The unanimous rule is reported as a sensitivity analysis. Veterinary and human sides keep their
  rules; they rest on few records.
- **The Q4 laboratory reader was escalated from `gemini-2.5-flash-lite` to `gemini-2.5-flash` on
  measured failure.**
  - **Audit:** a blind audit by `gemini-2.5-pro` of 56 random Flash-Lite reads found both inclusion and
    result correct in 26 (46%).
  - **Main error:** 27 abstracts counted as laboratory efficacy studies of the drug when they were not.
    Examples: propylthiouracil used to *induce* hypothyroidism; post-laparotomy pain models under a
    cataract-surgery pair; comparator studies of other drugs.
  - **Status of that run:** its within-drug result (companion 80% vs laboratory 87% on 101 pairs) is not
    reported. It is kept as `lab_models_flashlite.json` / `q4_report_flashlite.md`.
  - **Next:** the escalated reader is audited the same way before its result is used.
- **All verifier-excluded results are adjudicated, per a rule set before the audit.** A blind audit of
  59 random verifier exclusions (`claude-sonnet-5`, `e4_audit_excluded.py`) found 15 the adjudicator
  kept: 25%, exact 95% CI 15–38%. The pre-set rule was to adjudicate every exclusion if the upper bound
  exceeded 10%, and it was followed.
  - Several of the adjudicator's keeps look lenient: an animal-only percentage of macaque studies, a
    forensic human prediction error, gene-sequence similarity. The true false-exclusion rate is probably
    lower than 25%.
  - Adjudicator leniency is therefore a named target of the human spot-check, and it is reported in the
    quality file.
  - Implementation: studies already adjudicated on their non-excluded results get one extra call for
    their excluded results; the rest get one call covering all results.
- **OpenRouter credit ran out during adjudication.** 373 of 573 per-study calls failed with credit
  errors: 372 HTTP 402 "requires more credits", plus one timeout.
  - The failed studies are re-run on the **same model** (`claude-sonnet-5`) through the Anthropic API,
    using the user's key provided for fallback. The rule that a stage never switches models is kept.
  - The direct route attaches PDFs natively. Documents over 100 pages go as text with page markers
    (Anthropic's PDF limit), as oversized files already did.
  - Structured output is forced through a tool schema.
  - Each output records its route (`openrouter`, `anthropic-direct`).
  - Outputs built from the partial adjudication (1,074 final results in 345 studies; recall estimate 35%)
    are provisional and are rebuilt after the rerun.
- **Anthropic credit also ran out; the remaining studies were adjudicated by the reviewing agent, by hand,
  in session.** No further API spend was authorised, so the 263 studies left unadjudicated (262 credit
  errors, one KeyError, one OpenRouter error) were decided by the reviewing agent reading each extracted
  result against the paper's own text.
  - Tooling (no network, no model calls): `m1_dossier.py` prints, per pending study, every extracted result
    with its verifier status, quote, located PDF page and a ±450-character context window from the PDF text
    layer; `m2_record.py` records the decisions under `"{pmid}|manual"` in `adjudicated.json`, in the same
    shape as model decisions, with the model field naming the reviewing agent.
  - The criteria are the ones in `e3_adjudicate.SYSTEM`, unchanged: keep / keep-with-correction / drop, the
    same definition of a correspondence result, and the same "treat like results alike" rule.
  - Result: 1,647 decisions over 263 studies — 646 keep, 123 keep-with-correction, 878 drop.
  - Two recurring calls made consistently and recorded in each rationale: (a) where a paper reported the
    animal and the human arm as separate single-species results, the pair was recast as one comparison and
    the other half dropped, rather than counting each arm as a correspondence result; (b) duplicate reports
    of one analysis (preprint and published version) were kept once and the duplicate dropped, with the
    retained record named in the rationale.
  - `t1_part1_outputs.py` merges `"|manual"` alongside `"|all"` and `"|excl"`.
  - Final set after the merge: **1,494 results in 406 studies**; 309 study-calls were adjudicated by
    `claude-sonnet-5` and 263 by the reviewing agent, covering disjoint sets of studies.

## A7 — Species recovered from the reported label, for display (2026-09-15)

**What was wrong.** 879 of 1,494 final results carried `species: grouped-label`, and 15 carried
`species: human`. Inspecting `species_as_reported` on those records shows why: labels such as
"canine and human", "dog and human" and "human and canine" name two things, so the extractor
recorded them as grouped. But one of those two is always the comparator. Every result in this
review compares an animal with a human; "canine and human" is a dog result, not a grouped one.

The effect was not cosmetic. The evidence map's species axis was 60% "unknown", and cells that
hold real evidence looked empty — the question "what do we have for dogs in eye disease?" returned
one study when the corpus holds four, including a paper on RPE65 gene therapy in dog models of
inherited retinal dystrophy whose whole subject is the dog-to-human comparison.

**The rule.** Where a result's species is `grouped-label` or `human`, and `species_as_reported`
names exactly one animal from the frozen vocabulary, the species column shows that animal. Where
the label names several ("both species", "rodents", "animals", "preclinical") or none, it stays in
the *not resolved* column. The rule cannot invent a species: it fires only on an unambiguous match,
and human-only words are never animal matches.

**Effect.** 499 of the 894 unresolved results resolve: mouse 366, dog 67 (45 laboratory, 22
companion), rat 23, pig-minipig 14, non-human-primate 13, zebrafish 11, other-rodent 4,
c-elegans 1. 395 remain unresolved and are still shown as such. `model_type` is untouched, so
recovered dogs and cats still separate into companion and laboratory columns by the existing rule.

**Scope.** Display only. The stored records keep what the extractor recorded, exactly as with the
spelling normalisations (`guinea pig` → other-rodent, `Macaca fascicularis` → non-human-primate).
The mapping is applied in the site builder and is reproducible from the committed data.

**Found by.** A reader asking why a paper we hold in full text was not in the ophthalmology dog
cell — the kind of check limitation L87 exists to invite.

## A8 — Species recovery extended to the title and the result's own text (2026-09-15)

A7 recovered a species where `species_as_reported` named exactly one animal. 399 results still had
none. Two further sources were tested against each other before either was used: the study title,
and the result's own statement and quote.

Where both name exactly one animal they agree in **74 of 74 cases, with no disagreements**, so the
two are treated as one rule: if the reported label is non-specific, take the single animal named in
the title or in the result's own text, and if either source names more than one animal, or they
would disagree, leave the result unresolved. This recovers a further 139 results; 260 remain
unresolved and are still displayed as such.

The order matters: `species_as_reported` first (A7), then title or text (A8). The reported label is
the extractor's own answer to "which species", while the title and statement are evidence about the
paper, not about the result. The weaker source is used only where the stronger one is silent.

`GEMM`/`GEMMs` (genetically engineered mouse models) was added to the animal vocabulary, having
appeared as an unrecognised label.

## A9 — Drug-pair names and treatment types corrected (2026-09-15)

The `not-a-treatment` type held 16 pairs and should not have existed. Inspecting each against its
own `veterinary_basis` showed the problem was in the ingredient name, not the evidence: the
automated name-extraction step had captured the wrong entity. `CHICKEN` was the allergen a
hydrolysed-diet trial challenged with; `THYROID` was recombinant human TSH; `RED BLOOD CELLS` was
transfusion; `HL036`, `M032` and `RAAV2TYF GRK1 HRPGRCO` were tanfanercept, an oncolytic herpes
virus and an AAV gene therapy; `PARTS A B ADRABETADEX` was adrabetadex (HPBCD) with a label string
wrapped around it. Truncations were also present outside that type: `BORIC`, `BUTYL`, `ETHYL`,
`CORN`, `WHEY`, `I 131`, `PRGF`.

Corrections are recorded one pair at a time in `pair_overrides.json`, each carrying the sentence
from its own record that justifies it, and applied at build time; the judgements themselves are
untouched. Four pairs are dropped rather than renamed, because their records do not support a
drug-and-indication comparison at all: ammonia (a diagnostic biomarker study), a prescribing-pattern
fragment that duplicated the whey-diet trial, and two drug classes (`NSAID`, `ACE INHIBITOR`) whose
records were about something else. Classified pairs fall from 803 to 799, and `not-a-treatment`
falls to zero.

The pairs table now also defaults to alphabetical order by drug rather than grouping by verdict,
and every row can be opened to show the veterinary and human evidence behind its verdict, with
links to each cited study on PubMed and each cited US label on DailyMed.

## A10 — model_type resolved from the full texts for dog and cat studies (2026-09-15)

`model_type` decides whether a result appears in the companion or the laboratory column, and the
extractor left it as `mixed-or-not-stated` on 51 dog and cat results across 20 studies. The species
rule (A7/A8) routes those to the laboratory column, so studies of naturally occurring disease in
client-owned animals were being counted as laboratory evidence — a misclassification running in one
direction, and directly against the review's central comparison (L90).

No text rule could fix it: none of the 51 results contains "spontaneous" or "client-owned" language
in its own statement, quote or title. The full texts were held for all 20 studies, so each was read
and decided from its own methods and framing, with the deciding phrase recorded in
`model_type_overrides.json`.

Outcome: 16 studies are companion-animal work ("recruited at the RVC", "with informed consent from
their owners", "naturally occurring canine invasive urothelial carcinoma"), and 4 are laboratory:
three are regulatory-database analyses of preclinical toxicity studies (26753942, 29730448,
30823899, 30364994 — animal tests required by regulators, not patients), and one is the RPE65
gene-therapy work in maintained colonies of affected dogs (25671556), which is a purpose-maintained
research population rather than client-owned patients even though the mutation arose spontaneously.

Applied at build time per study; the stored records keep what the extractor recorded. This corrects
the companion/laboratory split in the evidence map, which is the comparison the review exists to
make, so it is recorded here rather than treated as a display detail.

## A11 — Thirteen supplied full texts incorporated (2026-09-15)

The author supplied full texts for ranks 1-13 of the wanted list, all previously unreachable by
open-access routes. They were registered in `studies.json`, marked user-supplied in the full-text
status record, extracted (66 candidate results, all 13 studies judged eligible; $0.06), verified
($0.21), and adjudicated by hand by the reviewing agent under the same criteria as the earlier
manual pass.

24 results were kept from 12 studies; 42 were dropped. The drops are dominated by two patterns the
extractor repeats on parallel-design papers: single-arm values with no cross-species comparison in
the statement (vitamin C, lithium, hyperventilation, C. novyi-NT), and in vitro assays, which fail
eligibility whatever they predict (four cell-line rows in 14519650, six clonogenic-assay rows in
15120036). Where a paper reported the animal arm and the human arm separately but stated the
correspondence in its own words, the arms were recast into one comparison, as in the earlier pass.

One study contributed nothing. 17300945 ("Lost in translation: treatment trials in the SOD1 mouse
and in human ALS") is precisely the kind of paper this review exists to capture, but every extracted
result was a mouse-side pooled effect size, and no extracted quote contained the human trial
outcome. Rather than attach a translation claim to a quote that does not support it, all eight were
dropped. The paper is a candidate for re-extraction with a question aimed at the comparison.

23 of the 24 kept results are level A (intervention outcomes), against 28% level A in the corpus as
a whole - supplied full texts are disproportionately the evidence the review is thinnest on, which
is an argument for supplying more.

Corpus after incorporation: 1,518 results in 418 studies.

## A12 — Manual extraction where the automated pass missed the comparison (2026-09-15)

17300945 ("Lost in translation: treatment trials in the SOD1 mouse and in human ALS") was dropped
entirely under A11 because all eight extracted results were mouse-side pooled effect sizes and no
extracted quote carried a human outcome. That was a failure of the extraction, not of the paper:
it is a random-effects meta-analysis of treatment trials in the most-used ALS model, and its subject
is precisely the animal-to-human question this review exists to measure.

Two results were therefore extracted by hand from the held full text and recorded with their
verbatim sentences and pages: the abstract's finding that therapeutic success in the SOD1 mouse has
not translated into effective therapy for human ALS (page 1), and the translation of the pooled
mouse survival-interval gain onto the human scale - a 10% prolongation of disease duration, or 3-4
months, the same order of magnitude as riluzole achieves in sporadic ALS (page 11). Mechanical
location against the PDF text layer scores 0.90 and 0.78 respectively, so the quotes are where they
are said to be. Items carry `extracted_by: manual`.

A third candidate on page 10, that the benefits of riluzole in the SOD1 mouse are comparable to
those seen in humans, was not taken: the paper attributes it to Gurney 1997 and immediately notes
there are no direct data supporting comparisons of that sort, so it is a quoted figure, not this
paper's own result.

**The rule this establishes.** Where the automated extraction captured only single-species values
from a paper whose subject is the comparison, the reviewing agent may extract directly from the held
full text, recording the verbatim quote and page and marking the item as manually extracted. This is
narrower than it sounds and more dangerous than adjudication: it lets the reviewer add evidence
rather than only remove it. It is used only on studies already screened in, only from full texts we
hold, and every such item is marked so it can be audited or removed as a class.

**What it implies.** The same failure mode - parallel-design papers split into single-arm values
with the comparison left unextracted - was visible across the supplied batch (vitamin C, lithium,
hyperventilation, C. novyi-NT) and was handled there by recasting. A systematic re-check of studies
that contributed zero kept results is warranted; there may be other papers dropped for the
extractor's reasons rather than their own.

## A13 — Condition areas for the drug-pair browser (2026-09-15)

The pairs table could be filtered by verdict, species, type and timing, but not by what the drug was
for — and the obvious filter was unusable: 339 distinct veterinary indications across 799 pairs, 206
of them appearing exactly once. Indications are therefore grouped into 21 condition areas by ordered
regex rules in `indication_areas.json`, first match winning, with the indication itself still
reachable by search. 797 of 799 pairs are assigned (99.7%); `radiography` and `systemic illness`
remain in `other`.

Order encodes the judgements that matter: oncology precedes reproductive so a mammary carcinoma is
cancer rather than a reproductive condition, and musculoskeletal precedes anaesthesia-analgesia so
"orthopaedic surgery" is not swallowed by the generic surgery and pain terms.

**A spelling bug worth recording.** The first version of these rules used `[ae]` for the ae digraph —
`an[ae]sthe`, `an[ae]mia`, `h[ae]morrhag`, `orthop[ae]dic`. A character class matches exactly one
character, so every one of those matched the American spelling and missed the British one:
"anesthesia" matched, "anaesthesia" did not. British spellings fell silently into `other`, which is
how a mapping can look 92% complete while being systematically wrong about a whole class of terms.
Spelled `ana?e?sthe` and so on, coverage went from 92% to 99.7%. The failure was invisible in the
output - `other` is a plausible-looking bucket - and was only caught by reading the unmatched list
rather than the summary.

The browser also now shows what the human side of each verdict rests on, as a badge in the evidence
panel and as a filter: US label indication (169 pairs), phase 3 or meta-analysis (283), phase 2
(31), earlier-phase or observational (40), none retrieved (276). Where the badge reads "US label
indication" the panel adds that a label means the FDA reviewed adequate and well-controlled trials,
and that such pairs can only disagree in one direction, since a label exists because the drug
worked (L91).

All of it is display-only: the pair records are unchanged, and both the area rules and every label
are editable without touching Python.

## A14 — Caninisation candidates: areas ranked, molecules not (2026-09-16)

A separate question from the review itself: which human-approved molecules are the best candidates
to license and develop for dogs or cats. The review answers one input to it — whether a disease
area's biology corresponds between dog and human — and the corpus supports the premise, since 477
of 799 classified pairs run human-approval-then-veterinary-evidence against 22 the other way, at a
median lag of 30 years.

`x1_caninisation_candidates.py` crosses two supplied programme lists (1,949 human, 328 companion
animal) against the review, the condition-area rules (A13), a species-safety exclusion list and
Drugs@FDA. Of 561 approved human programmes, 83 molecules survive: target not already claimed in
companion animals, disease one dogs actually get, an area where the review has dog evidence that
corresponds, not a diagnostic agent, and no known species toxicity.

**No molecule-level score is emitted, and that is the substantive decision.** Every candidate in an
area inherits identical evidence — all nine cardiovascular assets carry the same 13/19 corresponded,
16 of 19 results being intervention outcomes. The only attributes that vary between molecules in an
area are approval age, precedent and safety flags. A blended score would therefore have ordered
molecules by how old they are while appearing to order them by evidence: an early version ranked
Cozaar above ivabradine purely on a 1995 approval date. Areas are ranked on the review's evidence,
which is real; within an area candidates are an unranked set carrying the attributes that differ.

Evidence rank weights direction and depth equally, so an area that agrees often on weak evidence
does not beat one that agrees less often on strong evidence. Cardiovascular (13/19 corresponded, 16
intervention outcomes) ranks above oncology (93/107 corresponded, but only 5 of 111 results are
intervention outcomes).

**Declared missing.** No canine or feline prevalence, market size or willingness to pay is held
here, and the veterinary literature's attention is deliberately not substituted for prevalence — it
measures what researchers study. Patent status is proxied only by years since approval. The safety
exclusions are reviewer-supplied and incomplete: an absent flag means not checked, never safe.

**Correction to A13 found while doing this.** The musculoskeletal rule's `myopath` fired before
cardiovascular's `cardiomyopath`, so every cardiomyopathy was filed under musculoskeletal — 11
classified pairs on the live site, including feline hypertrophic cardiomyopathy, plus the cardiac
myosin and transthyretin candidates here. Spelled `(?<!cardio)myopath`. Third pattern bug in this
mapping after the `[ae]` digraph and the `\bthall\b` stem: a regex that looks right and silently
routes a whole class of terms to the wrong bucket is the characteristic failure of this approach,
and is only ever caught by reading what landed where, never by the summary.
