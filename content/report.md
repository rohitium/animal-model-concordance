::: dek
Systematic review
:::

# Brief survey of animal-to-human concordance in the biomedical literature

::: lede
We reviewed studies that reported direct comparisons between live non-human animals and humans, then recorded what they found.
:::

{{figures}}

## Summary {#summary}

Across every result we kept, the animal finding matched the human finding **{{n_corresponded}}**
times, failed to match **{{n_not_corresponded}}** times, and was mixed **{{n_mixed}}** times.

Those {{n_results}} results represent about **{{n_distinct_findings}} distinct findings**: where a
paper reports one comparison gene by gene or tissue by tissue, each row quotes the same sentence, so
rows are not independent evidence.

{{level_table}}

::: note Caveats
Most of the evidence is level C: how similar the biology looks, rather than what happened when a
disease was treated.

Different studies report concordance rates, sensitivities, correlation coefficients, gene-overlap
counts and qualitative similarity claims, across different diseases and species. Pooling all these
together is not necessarily kosher.

The literature is also selective about what gets published and about which comparisons get made at
all, so the balance above reflects what authors chose to report. Values are grouped only where
metric and unit match, and spreads are shown rather than averages.
:::

## Evidence map {#map}

Where the evidence actually is. Each cell counts the distinct studies with a kept result for that
disease area and species; the superscript is the highest evidence level present. Companion dogs and
cats — client-owned animals with naturally occurring disease — are kept separate from laboratory
dogs and cats throughout.

{{heatmap}}

::: note Note
{{n_unresolved}} of {{n_results}} results sit in the *not resolved* column, because the paper named
its animals only as "animals", "both species" or "rodents". That column means the species could not
be pinned down, not that something was found, so every species total is a lower bound. The grid is
sparse by nature — most disease-area and species combinations have never been studied this way.
:::

## What the results say {#results}

Every kept result is browsable: filter by evidence level, species, disease area or direction, or
search the findings themselves. Each row links to its study page, which carries the quote and the
page number the value came from.

[**Browse all {{n_results}} results →**](results.html)

## Companion animal vs Human drug pairs {#pairs}

For agents used both in companion animals with naturally occurring disease and in people: does the
veterinary evidence point the same way as the human evidence?

{{pairs_strata}}

::: note How to read this
Most of these are human medicines later adopted in veterinary practice. The agreement therefore
mostly shows that veterinary medicine adopts drugs that already work — not that animal evidence
predicted the human result. "Discordant" is used only where all the available evidence points the
opposite way.
:::

[**Browse all classified pairs →**](pairs.html)

Most of these pairs are human medicines adopted into veterinary practice decades later. Read the
other way, that lag is a question about which human molecules to develop for dogs and cats next.

[**Licensing human molecules for dogs and cats →**](caninisation.html)

## Companion animals vs laboratory models {#q4|Companion vs laboratory}

For the same agent and condition, did the companion-animal evidence and the laboratory-model
evidence each match what happened in people?

{{q4_tables}}

::: note What this cannot tell you
104 of the 108 pairs have a positive human result, and the laboratory literature is almost uniformly
positive (205 of 214 determinate laboratory sides). A body of evidence that nearly always reads "it
works" will agree with a mostly positive human record automatically.

Only 4 pairs have a negative human result — the case where predictive value would actually show —
and there laboratory models matched 0 of 4 and companion animals 1 of 4. This compares *agreement*,
as the protocol asked. It says nothing about prediction.
:::

::: small
The laboratory side of each pair is read from abstracts by a language model. Audited against a
stronger judge on a random sample, 79% of those reads were fully correct (42 of 53), with errors
dominated by including studies that should have been excluded.
:::

## Methods {#methods}

### Eligibility

A study is eligible if it reports a finding in live non-human animals alongside the corresponding
finding in humans, so that the two can be compared. Results are classified by what is being
compared: **A**, what happened when a disease was treated; **B**, toxicity and safety; **C**,
disease biology without an intervention outcome. Animal-only results, animal-to-animal comparisons,
in-vitro work, and figures a paper quotes from another paper are not eligible, whatever they report.

### From search to result

1. **Retrieval.** Citation chasing from known reviews plus themed PubMed queries, run as two
   independent mechanisms so that coverage can be estimated.
2. **Screening** in two stages, the second calibrated against hand-checked anchor papers.
3. **Extraction** from open-access full text. Every result is recorded with the sentence it came
   from and the page that sentence is on; both are published with it.
4. **Verification.** A second model checks each extracted result against the located page.
5. **Adjudication.** Every result is then decided against the eligibility rule above — including the
   results verification rejected, so that the checking step cannot quietly remove evidence.

Extraction, screening and verification are performed by language models under fixed prompts;
adjudication decides what appears here. Nothing on this site is summarised by a model: the counts,
rates and intervals are computed from the adjudicated records.

### Coverage of the literature

{{recall}}

### How accurate is the checking?

{{n_extracted}} candidate results were extracted from the full text of {{n_extraction_studies}}
studies, of which {{n_results}} results in {{n_studies}} studies survived adjudication. The two checking stages
disagree often enough to be worth reporting: of the results verification accepted, **34% were later
dropped or corrected**; of those it rejected, **10% were reinstated**. That is why every result is
adjudicated rather than trusted to verification alone.

Roughly half the final results ({{n_single_reviewer}} of {{n_results}}) were adjudicated by a single
reviewer who was not blinded to the provisional labels. Those are the results the
[spot-check](spotcheck.html) deliberately oversamples.

## Limitations {#limits}

The ones that bear on how these results should be read:

- **This is a large sample of the field, not a census.** Capture–recapture across the two search
  mechanisms estimates 33% coverage of the reachable eligible literature (95% CI 26–46%), and
  because the mechanisms are not fully independent that is an upper bound.
- **Open-access full text only.** Paywalled studies are absent, and the veterinary side of the
  drug-pair analysis is largely read from abstracts.
- **The results are not commensurable.** Concordance rates, sensitivities, correlations and
  gene-overlap counts are different quantities; they are grouped only where metric and unit match,
  and never pooled.
- **The literature is selective.** Preclinical publishing favours positive findings, and which
  comparisons get made at all is not random. This inflates apparent agreement — most visibly in the
  companion-versus-laboratory comparison.
- **Agreement is not prediction.** Most drug pairs are human medicines later adopted in veterinary
  practice, so the two sides are not independent tests of each other.
- **Part of the adjudication was single-reviewer and unblinded**, and the two adjudicators covered
  different studies, so agreement between them cannot be measured.
- **Species labels are imperfect.** {{n_unresolved}} of {{n_results}} results could not be resolved
  to one species, and a handful carry a label that is simply wrong. In the evidence map, treat that
  column as unassigned rather than as a finding.
- **Regulatory status is read from US sources**, and the review is unregistered — PROSPERO does not
  accept preclinical or meta-research reviews.

::: small
A dated register of all {{n_limitations}} limitations recorded during the work, including those
superseded by later corrections, is kept in the
[project repository](https://github.com/rohitium/animal-model-concordance) along with the protocol,
the data and the code that built this site.
:::

## Verify this work {#verify}

Because part of the adjudication was single-reviewer and unblinded, the review publishes a fixed,
seeded sample of its own results — each with its source, its page and the sentence it came from — so
that anyone can check it rather than take it on trust. Forty items, about five minutes each.

[**Open the spot-check →**](spotcheck.html)
