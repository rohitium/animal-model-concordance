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
