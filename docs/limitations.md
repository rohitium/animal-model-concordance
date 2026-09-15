# Declared limitations

Maintained continuously, not written at the end. Each entry states the limitation, its
direction of effect where known, and what (if anything) mitigates it.

## Retrieval

**L1 — Anchor-set overfitting.** Query recall (82.8%) was measured on an anchor set I
assembled from prior knowledge and then used to guide five rounds of query revision. It
is optimistic by construction. Citation recall (79.3%) is measured leave-one-out and is
independent of the tuned vocabulary, so it is the more trustworthy figure. A held-out
check against reference lists of published reviews is required before Phase 2 closes.

**L2 — PMC deposition bias in citation chasing.** NCBI forward-citation links derive from
PMC-deposited reference lists. Six anchors were citation-unreachable, concentrated in
*Regul Toxicol Pharmacol*, *ATLA*, and *Vet Sci*. **Direction: against Arms 3 and 4**
(toxicology, veterinary) — precisely where SQ7 is answered. Mitigated by retaining the
query mechanism at equal standing, not by anything internal to citation chasing.

**L3 — Single database.** PubMed only, pending confirmation of Stanford/Lane licensing for
Embase, Web of Science, Scopus, and CAB Abstracts. Embase absence matters most for European
pharmacology and toxicology; CAB Abstracts absence matters most for Arm 4.

**L4 — No vocabulary for the target concept.** No MeSH descriptor means "measures
animal-to-human concordance", so retrieval cannot be anchored on controlled vocabulary and
depends on author phrasing that varies widely.

## Analysis (carried from PLAN.md §13, restated as they become operative)

**L5 — Heterogeneous concordance definitions** inherited from Track A sources; recoding onto
D1/D2/D3 is partial and flagged per record by `definition_recoverable`.

**L6 — Specificity and NPV only partially estimable.** Compounds failing in animals rarely
reach humans, so true and false negatives are structurally under-observed (PLAN §6.3, §7.5).

**L7 — Preclinical publication bias** is severe and only partly correctable; raw and
bias-adjusted estimates are both reported and the gap is itself a finding (SQ5).

**L8 — Endpoint non-equivalence** between species forces judgment calls, made auditable by
the `endpoint_match` field.

**L9 — Non-random selection into clinical trials** with respect to preclinical strength.

**L10 — Rodent-dominated coverage.** Horse, chicken, cat, and great-ape estimates will rest
on small n and are reported as such, never absorbed into a headline number.

**L11 — Veterinary trials are smaller and often single-arm.** SQ7 must not conflate "better
model" with "weaker comparator"; Arm 4 comparisons are matched on `readout` and
`therapeutic_area` and reported with this caveat attached.

## Pilot slice (2026-08-20)

**L12 — Abstract-only extraction.** Full texts require subscription access we do not have.
2×2 tables, per-species breakdowns, and endpoint detail are usually in full text, so those
fields are frequently `not stated in abstract`. This is missing data, not absent evidence.

**L13 — Screening not human-verified.** Screening was LLM-assisted (gemini-2.5-flash-lite,
rubric 2026-08-20.r2), validated on a 27-record gold set at 100% sensitivity (95% CI
74.1–100%) and 62.5% specificity (95% CI 38.6–81.5%). The sensitivity CI is wide; n=27
cannot exclude a true sensitivity near 75%. Gold labels are the author's own and unverified
by a second reader.

**L14 — Arm 4 is near-empty, and this is a finding.** A targeted veterinary-patient search
returned 174 records; 1 met the inclusion rule. Well-cited comparative-oncology papers
(e.g. Vail & MacEwen 2000, 213 citations) were excluded for advocating the model rather
than measuring concordance. SQ7 is therefore not answerable from Track A, and the review
reports the gap rather than filling it (user decision, 2026-08-20).

**L15 — Slice is not a random sample.** Studies were selected by a recorded score
(0.5×log-citations + 0.5×recency + source bonus) under per-strand diversity quotas.
It is deliberately weighted toward authoritative and recent work and must not be treated
as representative of the underlying literature.

**L16 — Review is unregistered.** PROSPERO excludes preclinical and meta-research reviews;
no registration was sought. Pre-specification rests on dated, version-controlled protocol
files and `protocol/amendments.md`.

## Full-text pass (2026-08-20)

**L17 — No study in the slice publishes an explicit 2×2 table.** Of 46 full texts
extracted, 0 report the underlying TP/FP/FN/TN cell counts; papers give derived
statistics (concordance rates, PPV) instead. This is an independent route to the same
constraint as the denominator problem (PLAN §6.3): sensitivity and specificity cannot be
recomputed from published data, so §7.2's diagnostic framing depends on the handful of
studies that report those statistics directly (2 of 46 here).

**L18 — Open-access coverage is 46/100 and non-random.** Retrieval used only openly
licensed sources (Europe PMC XML, PMC, Unpaywall); no paywall was circumvented. Coverage
skews to recent and to OA-friendly journals, so older toxicology and veterinary titles are
under-represented — the same direction as the PMC-deposition bias in L2. Abstract-only
records therefore under-report exactly the fields (2×2, per-species, endpoint detail) that
Arms 3 and 4 most need.

**L19 — Metrics are not comparable across studies.** Extracted values include agreement-type
metrics (concordance, PPV, replication rate) and disagreement-type metrics (failure rate,
effect-size overestimation). They point in opposite directions and are grouped, never
co-ranked, on the site. Even within a group, definitions differ; recoding onto the D1/D2/D3
scale (PLAN §6.1) is a prerequisite to any pooling. 42 of 46 full texts state their own
concordance definition, which is the raw material for that recoding.

**L20 — Extraction is LLM-derived and only spot-checked.** Models were instructed to return
null rather than infer. Checks against known values passed (Olson 2000 → 71%, n=150;
Monticello 2017 → PPV 43%/sens 48%/spec 84%/NPV 86%, n=182; Perel 2007 → 6 pairs; Clark 2018
→ correctly null). No systematic accuracy audit has been run.

## User-supplied full texts (2026-08-21)

**L21 — Five full texts were supplied from the user's institutional access.** Recorded in
`fulltext_status.json` with `route: user_supplied` and licence
`not open access - user supplied, do not redistribute`. They sit in the gitignored
`data/raw/fulltext/` and must never be committed or published; only extracted structured
data enters the site. This raises full-text coverage from 47 to 52 of 100 and adds
per-species results for Olson 2000 (rodent 43%, non-rodent 63%) and Seok 2013 (R²=0.09
across 23 comparisons) — figures that no abstract states.

**L22 — Non-proportional quantities must not be stored in proportion fields.** Redfern 2003
reports a 30-fold hERG safety margin; extraction placed `30` in `concordance_value`, which
the site would have rendered as "3000%". The audit now fails on any value outside 0–1, and
such quantities render as a labelled reported quantity rather than a percentage. One
occurrence found and corrected in 52 extractions.

## 2026-08-21 (continued)

**L23 — Non-proportional values are relocated, not deleted.** `analysis/18_sanitize.py` moves
any value outside 0–1 from a proportion field into `reported_quantity` with its unit, so the
figure survives with its meaning intact and the audit is not permanently red. One occurrence
(Redfern 2003, 30-fold hERG margin) across 53 full texts.

**L24 — The Seok/Takao disagreement is a methods difference, not a data difference.** Both
papers analyse the same datasets. Seok 2013 reports Pearson R² ≈ 0.09 across orthologous
genes; Takao 2015 reports Spearman ρ 0.43–0.68 restricted to genes significantly changed in
*both* species, with 77–93% changing in the same direction. The site presents both with their
statistic and gene-selection rule side by side and offers no adjudication. This is the clearest
demonstration in the slice of why concordance values cannot be pooled across studies without
first recoding onto a common definition (PLAN §6.1).

## Reclassification (2026-08-21)

**L25 — "Unclear/unspecified" buckets were missing categories, not unknowable studies.**
Re-classification (`analysis/19_reclassify.py`) uses closed vocabularies with no escape
hatch, adding the categories that were absent: `methods-and-bias` as an arm (reproducibility,
publication bias, attrition), `cross-cutting` as a therapeutic area (real for toxicology and
safety pharmacology, which are not disease-specific), and `multiple-aggregated` for species
where a study reports pooled groups such as "rodent vs non-rodent". `not-species-specific`
remains only for studies about research methodology that analyse no species. Every
classification carries a verbatim supporting quote so it is auditable; forcing a choice
without evidence would convert honest gaps into confident-looking fabrications.

**L26 — Classification now uses full text where available.** 53 of 100 studies were classified
from full text, 39 from abstract, 6 from title only. Species coverage rose from 10 to 16
categories and therapeutic areas from 14 to 18 once methods sections were readable — the
earlier gaps were abstract omissions, not missing information.

**L27 — A protocol violation was introduced and caught.** The first re-screening pass excluded
6 records on title alone, contradicting the auto-advance rule (L13): Hackam 2006 (312 cites,
original data on 76 animal studies), Prinz 2011, Perrin 2014, Bracken 2009, Contopoulos 2008,
and one other. All are abstract-less. The rule is now enforced in code — a title-only record
cannot be excluded, and the model's title-only reading is retained alongside the forced
advance. Re-screening from full text moved includes from 100 to 90 of 98; the 8 genuine
exclusions are methods papers (ARRIVE guidelines, litter effects, a histopathology pipeline)
that report no agreement statistic.

## Scope correction (2026-08-21)

**L28 — Non-animal studies had entered the slice, and the vocabulary encouraged it.**
PLAN §6.3 excludes in vitro-only and in silico-only comparisons, but rubric r2 restated this
too weakly, and the classification vocabulary offered `in-vitro-or-in-silico-comparator` as
a *model type* — turning a protocol violation into a supported category (17 studies).
Rubric r3 requires the index test to be a whole, live non-human animal, and names the
excluded methods explicitly (cell lines, organoids, organ-on-chip, isolated ion-channel
assays, 3D cultures, QSAR, PBPK, AI/ML, mathematical models, NAMs). Isolated tissue taken
from an animal counts as in vitro. Studies evaluating both whole-animal and non-animal
predictors are retained, since the animal arm is in scope.

Re-screening all 100 with `index_test` recorded and quoted: 29 excluded — 8 in-silico-only,
7 in-vitro-only, 3 human-only, 5 unclear, 6 whole-animal studies reporting no agreement
statistic (ARRIVE guidelines, litter effects, welfare/rigor methodology). **71 remain
eligible.** Excluded records stay in the database with their reason and evidence quote
rather than being deleted, so the exclusion is auditable.

Hay 2014 (drug attrition) was excluded as `human-only`: it supplies the base rate for the
PPV curve (PLAN §7.2) and belongs to the auxiliary set, not to an arm.

## Measurement scoping (2026-08-21)

**L29 — Rubric r4: the comparison must have an animal on one side and a human on the other.**
r3 required the index test to be a live animal but not what it was compared with, so
within-species work qualified: a paper computing sensitivity/specificity for diagnosing
osteoarthritis *in dogs* satisfied "reports a quantitative measure of agreement" with no
human data at all. r4 judges each study against its own extracted measurements. 10 studies
excluded (within-animal, within-human, or no comparison found), leaving 61 eligible.

**L30 — A judging step read a gap in our data as a finding about the literature.** The first
r4 run excluded Redfern 2003, Bracken 2009 and two others because the `species` field on
their measurements was empty — an extraction gap, not evidence of no cross-species
comparison. Redfern 2003 is an Arm 2 anchor and one of only three studies reporting
sensitivity/specificity. The prompt now states explicitly that an empty species field is a
gap in our data and directs judgment to the comparison text. Failures fell from 15 to 10.

**L31 — Study-level scoping was the wrong granularity.** An included study reports many
figures and most are not animal-to-human. Of 1,344 extracted figures, only **379 (28%)**
compare an animal with a human; 336 are within-animal (including cross-species animal
comparisons such as zebrafish vs mammal), 269 within-human, 147 about research conduct
(e.g. inter-rater agreement between data extractors), 147 animal vs non-animal method, and
66 bare counts. Aggregate pages show only the animal-vs-human figures; the rest remain on
each study page, labelled, for completeness.

**L32 — Values are ranked only within comparable units.** A count of 4,418 genes is not
"larger" than 94%. Sorting groups percentages and proportions together, correlations next,
and counts last.

## Extraction integrity (2026-08-21)

**L33 — 12.1% of numeric values are not supported by the sentence they are attributed to.**
`analysis/26_audit_measurements.py` checks every measurement carrying a value against its
own verbatim quote (number words such as "fivefold" and "a third" count as stated). 144 of
1,187 fail. Some are inferences the model made rather than figures the paper reported — an
ALS review saying "eight of these compounds ultimately failed" was stored as
`failure rate = 100%`; a narrative claim that a phenomenon was "first discovered in rats
and later demonstrated in smokers" was stored as `concordance = 100%`. Others have the
right number attached to the wrong sentence. Since we cannot show them as sourced, the
value is withheld on study pages (shown as "not stated") and the measurement is excluded
from all aggregate pages. The statement and its quote remain visible.

**L34 — Patient-derived xenografts are reported separately.** A PDX grows the patient's own
human tumour tissue in a mouse host, so a PDX concordance study asks whether a patient's
tumour predicts that patient's response — not whether another species' biology predicts
human outcomes. The 4 PDX studies report very high agreement (100%, on 17 regimens) on small
samples; pooling them with animal-model concordance would inflate it. They appear in their
own section, excluded from every aggregate.

**L35 — Two parser defects corrupted displayed text.** (a) Journals such as *Dialogues in
Clinical Neuroscience* publish Spanish and French translations in `<OtherAbstract>`; matching
`<AbstractText>` anywhere concatenated all three languages into one abstract. Parsing is now
scoped to the primary `<Abstract>`. (b) Markup was stripped without unescaping, so numeric
character entities (`&#xf3;`) reached the page as literal text and were copied into extracted
quotes — 108 occurrences, now unescaped at source and in stored data.

## Comparison detail (2026-08-21)

**L36 — A cache keyed only on PMID kept abstract-derived data after full text arrived.**
`20_measurements.py` skipped any study already cached, with no record of which source text
produced the entry, so **85 of 100** studies retained measurements extracted from their
abstracts even after full text was supplied. Re-extraction raised the total from 1,349 to
2,079 figures. The dog pan-cancer preprint had zero measurements despite having full text,
which is why Arm 4 appeared empty; it now yields 26. Caches are source-aware.

**L37 — Figures are filtered for relevance, not just for mentioning both species.**
The scope pass marked anything touching preclinical and clinical work as animal-vs-human,
including "$330,000 to characterise a single drug" — a budget figure. Each figure is now
tested for whether it quantifies correspondence; 84 of 655 were dropped as costs,
timelines, publication counts, or bare tallies, each with a stated reason.

**L38 — A missing category, not a missing paper: `animal-result-by-human-outcome`.**
O'Collins 2006 (1,026 experimental treatments in acute stroke, 643 citations) was excluded
three times because its central comparison — 31.3% average neuroprotection in drugs that
reached the clinic versus 24.4% in drugs never taken forward — has animals on both sides.
But the groups are defined by human clinical fate, which makes it concordance evidence of a
direct kind. The taxonomy now carries this category; 23 figures across the corpus fall into
it, and the study is included.

**L39 — Both sides of each comparison are now characterised.** Species is recorded
specifically (never "animal"), with strain or model where named, how the disease arose,
n and what n counts, and the endpoint; the human side records population, disease, n,
endpoint and trial phase. `endpoint_match` records whether the two endpoints are identical
(404), analogous (139), non-analogous (27) or unstated (1) — without which a concordance
figure cannot be interpreted, and PLAN §6.1's D1/D2/D3 recoding cannot be done. Coarse but
genuine groupings such as Olson's "rodent" and "non-rodent" are kept as grouped labels
rather than discarded: rodent 43% vs non-rodent 63% is that paper's headline result.

## Presentation and taxonomy (2026-08-21, later)

**L40 — `methods-and-bias` removed; `disease-biology` added.** Every other arm classifies by
what is being predicted; that one classified by what kind of study it is, mixing two axes.
Its contents split: cross-species comparisons of gene expression, immune signatures and
pathology became `disease-biology` (does the model's biology resemble the human disease —
a prediction target with no intervention involved), and translation-rate studies moved to
the arm whose findings they count. Arms: disease-biology 21, efficacy 16, toxicology 13,
safety-pharmacology 4, veterinary 2.

**L41 — Arm 4 needs precedence, not competition.** Veterinary describes the *model*
(spontaneous disease in client-owned animals) while the other arms describe the readout, so
under a single-choice enum the dog pan-cancer study was classified `disease-biology` and the
veterinary arm emptied. Per PLAN v0.3, spontaneous-veterinary models take Arm 4 whatever the
readout, with the readout retained in a `readout` field.

**L42 — Figures are shown as self-contained statements.** 730 of 759 concordance figures were
rewritten to state the denominator, the species and disease, and the human counterpart where
the source gives one; 709 carry an explicit denominator and 141 a counterpart value. Figures
that could not be stated precisely are dropped rather than displayed as fragments. Text is
never truncated mid-word.

**L43 — Duplicate figures are collapsed.** The same result is often extracted from two
sentences ("93%" and "93.2%" for genes changing in the same direction). Two figures collapse
only when unit and value agree closely AND descriptions overlap heavily; the copy retaining a
refined statement and a denominator survives. An earlier, looser rule would have dropped 748
figures including distinct correlations for different diseases in Takao 2015; the current rule
drops 675 and preserves Olson's two separate 63% results.

**L44 — Studies are cited as Author et al. Year**, not by truncated title.

## Question-driven extraction (2026-08-21, final)

**L45 — Extraction is now question-driven and reads the PDF.** Bottom-up harvesting of every
printed number produced twelve NPV rows for organ subcategories and a leaderboard of
incommensurable statistics. Each of the 57 studies was instead read from its full-text PDF
(native file parsing, so tables and figures are visible) and asked one fixed question set.
925 comparisons, each with its unit as printed and its table/figure location. Verdicts are
judged from results, tables and figures, with the prompt explicitly directing the model to
ignore how authors characterise their own findings.

**L46 — Verdict tallies count studies, not predictive performance.** supports 10,
partly-supports 29, does-not-support 18. The studies are not a random sample of the
literature, so this distribution describes our corpus and nothing wider. The tally also moved
sharply as the corpus filled (does-not-support was 12% at 34 studies and 32% at 57), which is
a warning against reading partial results.

**L47 — Ranges are formed only across figures measuring the same thing.** Same statistic, same
unit, and closely matching descriptions of what was compared. Grouping on statistic name alone
merged neuroprotective efficacy with translation success into a single "3–83%" range.

**L48 — A study reporting no quantitative animal-human comparison was excluded** (`26563791`,
extrapyramidal neurotoxicity). The extraction returned a verdict of "supports" resting on the
qualitative statement that "a variety of veterinary species also develop extrapyramidal signs".
Both the inclusion rule and the verdict rule require data; the verdict step can drift to prose
when a paper contains no figures, so zero-comparison studies are now excluded automatically.

**L49 — An organism earns a table row only where a figure is attributable to it.** Reviews
often name every species they mention while reporting figures for a few; those namings are
listed in a note rather than becoming empty rows.

## Deployment (2026-08-22)

**L50 — Published at https://rohitium.github.io/animal-model-concordance/.** Public repository,
built in CI from the committed data on every push, so the published pages always regenerate
from `data/db/`. Full-text PDFs and XML are gitignored and never published; only extracted
structured data reaches the site. The site states on every page that it is not peer reviewed.

**L51 — The first two deploys published the wrong thing, and both reported success.** The CI
workflow referenced `analysis/11_build_site.py`, three builders out of date, so a stale 9 KB
page was served instead of the 98 KB current site. The fix then failed to deploy itself,
because the workflow's `paths:` filter did not include the workflow file. Both times the run
was reported as successful; success meant the job executed, not that the intended content was
live. Verification is now by fetching the page and comparing its size and heading against the
local build, not by reading a green check.

## Objective verdict (2026-08-22)

**L52 — The argument against numeric thresholds was wrong, and has been withdrawn.** The site
previously claimed no cut-off could span a concordance rate, a correlation and a failure rate
"because a high value means success in the first two and failure in the third". Direction is
trivially normalisable — a 92% failure rate is an 8% success rate — and the claim served as an
excuse for not building a rule. `analysis/37_objective_verdict.py` now maps every figure that
carries concordance information onto a 0–1 scale where 1 means the animal result tracked the
human result, inverting discordance-type statistics and taking |r| for correlations. A study's
score is the median of its figures; cut-offs are ≥0.70 supports, 0.40–0.70 partly supports,
<0.40 does not support. Which statistics count, their orientation and the cut-offs are all
explicit in the script and can be recomputed or changed by anyone.

**L53 — Only 31 of 56 studies report anything reducible to a concordance scale.** The rest
report p-values, regression slopes, Mahalanobis distances, fold-changes, likelihood ratios and
odds ratios. These are real results but not rates of agreement. That roughly half of the
studies measuring animal-to-human correspondence do not express it as agreement is itself a
finding, and much of why concordance is hard to compare across papers.

**L54 — The three verdicts agree poorly, and none is treated as authoritative.** Model rater 1
vs rater 2: 73% agreement, κ = 0.58. Numeric rule vs rater 1: 52%, κ = 0.24. Rule vs rater 2:
48%, κ = 0.17. Each has a known weakness: the rule takes a median across statistics that mean
different things within one paper, so a base-rate-inflated negative predictive value can pull a
study upward; the model raters weigh which figure matters but are only moderately reproducible.
All three are shown on every study page and disagreement is displayed rather than resolved.
Consequence for readers: **the figures are the evidence; the labels are contested.**

**L55 — Verdict cut-offs are sensitive but not arbitrary.** Moving from 0.70/0.40 to 0.65/0.35
shifts four studies from partly-supports to supports; does-not-support is unchanged across all
tested cut-offs (0.60/0.30 through 0.75/0.45). The negative end of the scale is therefore more
stable than the positive end.

**L56 — Excluded-study reasons rewritten in plain language.** They had been machine strings such
as "r4: none-found — …" truncated mid-sentence.

## Attribution and provenance (2026-08-22)

**L57 — A figure with no species of its own was attributed to every organism the study named.**
41% of extracted figures (377/925) carry no species. The old rule gave those to each organism
the study mentioned, duplicating one result across up to eight rows: Martić-Kehl 2012's "3 of
494 stroke interventions" appeared as evidence about dogs, rodents and primates alike, from a
paper about none of them specifically. A species-less figure is now attributed only when the
study examines exactly one organism. Table rows fell from 38 to 27.

**L58 — Figures quoted from other papers were counted as the quoting paper's evidence.**
206 of 925 figures (22%) are numbers taken from earlier work, usually while setting up a
problem. All three of Martić-Kehl 2012's figures are of this kind, including the 3/494
explicitly credited to Sena and colleagues. Counting them is wrong twice: the conditions
belong to the original study, and where the original is also in this corpus the same number is
counted twice. Provenance is now classified per figure — own result (556), re-analysis of
others' data (162, which does count, since pooling published results is the reviewer's own
work), cited from another study (206, which does not). Rows fell from 27 to 24.

A keyword detector had found only 4% of the cited figures; the classification pass found 22%.
Pattern-matching on phrases like "reported" and "et al." is not adequate for this.

**L59 — Both defects were found by a reader checking one paper against the site.** Neither
would have surfaced from internal consistency checks: the numbers were extracted correctly,
carried correct verbatims and correct source locations, and simply meant something other than
what the table asserted.

## Which statistics can be thresholded (2026-08-22)

**L60 — Odds ratios, fold-changes and slopes CAN be converted; converting them makes the
composite worse.** Standard transforms exist: an odds or likelihood ratio maps by x/(1+x)
(Yule's Q rescaled, so 1 → 0.50), and a fold-change or ratio maps by 1/max(x, 1/x) (1 → 1.00,
2 → 0.50). Claiming they were unconvertible was wrong. But folding them into one median is
not an improvement: a 0.5 meaning "a two-fold difference" is not the same claim as a 0.5
meaning "agreed half the time". Measured against independent readers, each family added makes
the rule worse — agreement/discordance/correlation alone gives κ = +0.17 against rater 1;
adding association gives +0.13; adding ratio-like gives **−0.01**, i.e. chance. The score is
therefore restricted to agreement, discordance, correlation and bounded differences. The other
families are still converted and shown per figure on study pages, labelled and excluded from
the score, so the information is not lost.

**L61 — Two families genuinely cannot be thresholded.** p-values and FDRs measure evidence
against a null, not how closely two things agree: a tiny p can accompany a trivial or a large
divergence. Mahalanobis distances and slope differences in unstated units are monotone in
agreement but have no common scale, so they rank species within a study and cannot be compared
across studies.

**L62 — Headline numbers restated after the attribution and provenance fixes.** 56 studies
included; 33 have organism-specific evidence; 577 of 925 extracted figures appear in the table
(206 are quoted from other work, the rest are not attributable to a specific organism);
24 evidence rows; 27 studies carry a numeric score.

## Distributions, qualitative evidence, worked example (2026-08-22)

**L63 — A purpose-built composite score is the concordance measure; its distribution is the
finding.** Daluwatumulle et al. 2026 scores dog models of each human cancer type. The row now
reports that distribution — 20 comparisons, span 31–85.05%, median 61.73%, with the lowest and
highest named — rather than splitting it into pairs or picking out individual cancers.
Conditions the authors expected to score low are part of the distribution and are not removed;
the earlier special-casing of "negative controls" was an unnecessary editorial layer.

**L64 — Ancillary statistics are not concordance measures.** The mean gap between within-species
and cross-species correlations is a step in an analysis, not a measure of how well the model
matched. Such figures no longer appear in table rows (they remain on study pages) and do not
enter the score.

**L65 — A merged span must not be named after one of its members.** A row read "78.2–85.05% —
model robustness score for adult bladder cancer" when bladder is 85.05% and 78.2% is head and
neck. Spans covering several comparisons now state the count, the median, and the identity of
the lowest and highest.

**L66 — Qualitative comparisons are evidence and were being deleted.** Petersen-Jones et al.
2015 compares dog and human RPE65 gene therapy entirely in words — dogs showed "remarkable
improvement in the ERG", patients "no change", and the degree of rescue in humans was "nowhere
near" that in dogs. Every figure had a null value, and the provenance filter treated a review's
synthesis as quoted material, so the study vanished from the veterinary/dog row and the row's
direction flipped from mixed to *favours the model*. Qualitative animal-to-human comparisons
are now retained, marked, and excluded only from the numeric score. **A rule that drops
unquantified findings will preferentially drop negative ones**, since failures are often
reported without a number.

## Locators and qualitative rendering (2026-08-22)

**L67 — Page numbers are no longer published as locators.** 392 of 925 figures carried a
locator of the form "Results, p5". These were read off a PDF, so a page number may be the PDF's
rather than the journal's, and pointing a reader at a page we cannot vouch for is worse than
giving the section alone. Page numbers are stripped; section names are kept. Table and figure
references (501 figures) are verifiable in the published article and are kept verbatim.

**L68 — Qualitative comparisons are shown as statements, not as empty table rows.** A comparison
made in words was being rendered in the numeric table as a dash for the value and the phrase
"remarkable improvement" in the statistic column, with "not named" under credit. It is now shown
as the quoted sentence with its section, under a heading that says the paper compared animal and
human results in words rather than figures and that these cannot enter a numeric score.

## v0.4 step 1 — tier-1 extraction failed its gate (2026-09-14)

**L69 — The cheapest models could not tell a comparison from an animal-only result.** Run on the
56-study v0.3 corpus with `gemini-2.5-flash-lite` and `gpt-5-nano`, extraction was told explicitly
that a treatment effect measured in animals alone is not an animal-vs-human comparison. Both models
extracted such effects anyway: for Perel et al. 2007 they recorded infarct-volume reductions and
odds ratios, and neither recorded the paper's headline result (3 of 6 interventions concordant).
Gemini failed outright on 15 of 52 studies and repeated results within the rest; only 156 of 1,138
extracted items matched between the two models. Of all items, 7 passed every check, a 99% flag
rate, and canary C1 was missed — two escalation triggers under PLAN §8.2. The run is archived
in `data/v04/runs/tier1/` and extraction was re-run at tier 2. The verifier stage, which did
catch many of these errors (123 "not animal-vs-human"), stayed at tier 1.

**L70 — Stalled and silently hung jobs.** OpenRouter keep-alive bytes reset per-read socket
timeouts, so hung generations blocked jobs for over ten minutes while reporting nothing. All calls
now have a wall-clock deadline and runs are watched for stalls; the pilot step had also been
written sequentially and was rewritten to run in parallel.

## v0.4 drug-pair table on reference-data snapshots (2026-09-14)

**L71 — US sources only.** "Exists in human medicine" and human approval are read from Drugs@FDA
and openFDA labels. A drug approved for humans only elsewhere (pimobendan: human heart failure in
Japan) counts as absent from human medicine and is not paired. **Direction:** it removes pairs,
most likely for older drugs and agents developed outside the US. User decision (amendment A5).

**L72 — Label coverage is partial.** Of 262,842 openFDA labels in the 2026-09-11 export, 76,803
carry a human product type in the harmonised `openfda` block; the rest cannot be attributed to an
ingredient, so their indications are not seen. Drugs@FDA still lists every approved application,
so approval status is not lost; only label indication text may be missing for some products.

**L73 — Trial-to-ingredient links are made by name matching.** Intervention names and other names
are split into word n-grams and matched to salt-stripped ingredient names. This reliably links
branded or dose-qualified names ("Nab-paclitaxel", "Lotilaner ophthalmic solution, 0.25%"). It also
links generic words that are FDA ingredients ("water", "oxygen", "iron") to hundreds of trials.
Such agents are not veterinary test agents in any pair so far; every pair records how its link was
made (name or other name; exact or salt-stripped) so a wrong link can be audited.

**L74 — Veterinary side read from abstracts in pilot 2.** The test agent's result is extracted from
the PubMed abstract. Full texts would give response rates and endpoints the abstract omits. For
pairs entering the final table, the veterinary full text is to be obtained (user-supplied where
paywalled) and re-extracted.

## v0.4 A6 execution (2026-09-14)

**L75 — Title-only records can be excluded at screening.** About 7,300 of 26,343 expanded-retrieval
candidates have no abstract in OpenAlex or PubMed. Excluding them on title when both screening models say
exclude departs from L27 and may lose studies whose titles do not signal an animal–human comparison.
**Direction:** against older studies and journals without deposited abstracts, the same direction as L2
and L18.

**L76 — Held-out recall is not yet established for the expanded search.** The first held-out check was
built from memory and proved unusable as a certificate (see retrieval report). Recall claims wait on a
held-out set taken from published reviews' reference lists.

**L77 — Headline extraction selects, by design, at most 8 results per paper.** Papers reporting many
comparable breakdowns (per organ system, per cancer type) contribute their overall and main
per-species or per-disease results, not every breakdown. Per-breakdown values remain in the paper and
are cited by page.

**L78 — Narrative reviews that restate translation rates are excluded.** The criterion requires the
paper's own data or its own systematic or pooled analysis. Reviews that quote others' concordance
figures ("Lost in translation", "Are animal models as good as we think?") are excluded, even though
they are widely cited. Their figures enter only through the original studies, if those are retrieved.
This prevents double counting, but a figure whose original source is not retrieved is lost.

**L79 — The strict screen was calibrated on a small anchor set.** 20 anchors, 18 passing on
abstract. A 90% sensitivity on 20 papers has a wide confidence interval (exact 95% CI 68–99% for
18/20). The capture–recapture recall estimate (L76) is the fuller check.

## v0.4 A6: dog and cat drug pairs (2026-09-14)

**L80 — Most drug pairs are human medicines later used in pets.** Of 586 primary pairs, 440 involve a
drug with US human approval before the veterinary evidence. Concordance in those pairs (83%, exact 95% CI
76–89%) shows that established human drugs tend to work in dogs and cats with the corresponding disease.
It does not show that dog or cat results anticipate human results. Pairs where the veterinary evidence
came first are few: 19 with later US approval (7 concordant, 0 discordant; CI 59–100%) and 127 never
US-approved (72%, CI 53–87%). Reported as separate strata; the headline must not blur them. **Direction:**
the pooled primary figure overstates concordance for novel drugs.

**L81 — Veterinary sides are classified from abstracts.** About 58% of primary pairs (339 of 586) are
indeterminate. Many abstracts of veterinary studies report no response rate or primary-endpoint result.
Full texts would reclassify some; which way is unknown.

**L82 — Pair labels come from one judge model, with measured reliability.** A blind second judge
(`gemini-2.5-pro`) on 40 random primary pairs agreed on 88% (Cohen's κ 0.76). All disagreements were
between a determinate and an indeterminate or mixed label; none reversed concordant and discordant.

**L83 — Non-drug treatments were matched by name and removed from the primary table.** 201 pairs involved
supplements, minerals, devices or materials, multi-drug regimens, or names that are not treatments
(e.g. "copper" for hepatic copper accumulation). A treatment-type classification took them out; they are
reported separately (73%, CI 59–84%).

**L84 — SUPERSEDED (2026-09-14, same day): the first Q4 run below was invalid and is being re-run.** Inspection showed the laboratory-side reader credited studies of other compounds that used the drug only as a benchmark or comparator, counted adverse effects as efficacy failures, and aggregated 25–30 studies with an any-disagreement-is-mixed rule (195 of 343 sides mixed). The figures that follow are kept as the record of that run and must not be cited.

**L84 (first run, invalid) — Q4 (companion animals vs laboratory models, within drug) is underpowered.** Of 343 primary pairs with a
classifiable human side, only 47 had companion-animal, laboratory and human sides all positive or negative.
Result:
- companion animals matched humans in 39 of 47 (83%);
- laboratory models of the same drug and condition matched in 39 of 47 (83%);
- of the 10 pairs where only one matched, 5 favoured companion animals (exact 95% CI 19–81%).

Stated per F1: concordance did not differ detectably. The comparison cannot rule out a moderate
difference in either direction.

Caveats:
- Laboratory sides were read from abstracts and were mostly mixed (195 of 343).
- Laboratory literature is biased towards positive results.
- Most of the 47 pairs are drugs already approved in humans (L80).

**L85 — Q4 laboratory sides depend on an abstract reader whose accuracy is audited.** The first reader
(gemini-2.5-flash-lite) was correct on 46% of 56 audited reads, mostly by including abstracts that were
not efficacy studies of the drug in that condition. Q4 results are reported only from a reader that passes
the same audit, and the audited accuracy is stated beside the result.

**L86 — Q4 result (reader escalated to gemini-2.5-flash, audited 79% correct) cannot answer which model predicts
human outcomes.** On 108 drug × condition pairs where companion-animal, laboratory and human sides were all positive
or negative (laboratory side by the 75% rule):
- companion animals matched humans in 90 (83%) and laboratory models in 100 (93%);
- where only one matched, laboratory models were the one in 14 of 18 (companion share 22%, exact 95% CI 6–48%).

Stated per F1: in this set, laboratory models agreed with human outcomes more often than companion animals. The
unanimous-rule sensitivity analysis (65 pairs) found no detectable difference.

The agreement is not evidence of better prediction:
- 104 of the 108 pairs have a positive human result;
- the laboratory literature is almost uniformly positive (205 of 214 determinate laboratory sides);
- a side that nearly always reads "works" agrees with a mostly positive human side automatically.

Only 4 pairs have a negative human result, where predictive value would show. Laboratory models matched 0 of 4 and
companion animals 1 of 4. 90 of the 108 pairs concern drugs already approved in humans before the veterinary
evidence; only 2 concern drugs approved later. The first two Q4 runs (L84) were invalid and are not cited.

**L87 — The final result set has two different adjudicators, and half of it rests on one that was not
independently checked.** 309 of the 572 study-level adjudication calls were made by `claude-sonnet-5`;
the remaining 263 studies were adjudicated by the reviewing agent by hand after API credit ran out
(amendment note "Anthropic credit also ran out"). Of the 1,494 final results, **769 (51%) come from the
manually adjudicated studies**.
- The two adjudicators cover disjoint sets of studies, so no inter-rater agreement between them can be
  computed from this data, and none is reported.
- The manual pass was not blind: the same agent built the pipeline and had seen the verifier's reasons for
  each result. It is therefore the least independent step in the review.
- The human spot-check (`spotcheck.md`, 20 results, seed 20260914) is the only external check on it. The
  spot-check sample is drawn from all final results, so roughly half of it falls on manual decisions; the
  check should be read as a test of this step in particular.
- The manual pass dropped a larger share of results than the model adjudicator did (878 of 1,647 decisions,
  53%). Whether that reflects a stricter reading of the same criteria or a different one is not measured.

**L88 — Species labels in the final set are imperfect.** 879 of the 1,494 final results carry the extractor's
`grouped-label` (the paper reported several species together and the result was not resolvable to one), and
15 carry `human`, which is an extraction error that survived both adjudication passes — these are results
whose animal side is named only in the surrounding text. The evidence map therefore shows a `human` column,
which should be read as "species not correctly assigned", not as a finding.
