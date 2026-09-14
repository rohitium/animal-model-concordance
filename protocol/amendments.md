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
