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
