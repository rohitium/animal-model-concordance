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
