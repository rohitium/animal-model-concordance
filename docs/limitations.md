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
