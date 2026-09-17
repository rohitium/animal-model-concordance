::: dek
Systematic review
:::

# Brief survey of animal-to-human concordance in the biomedical literature

::: lede
Studies that compared a finding in live animals against the corresponding finding in humans, and what they found.
:::

## Summary {#summary}

Each row is one comparison a paper drew between an animal and a human, classified by what was
compared: **A** treatment outcomes, **B** toxicity and safety, **C** disease biology.

{{level_table}}

::: note Caveats
Most of the evidence is level C — how similar the biology looks, not what happened when a disease
was treated. The quantities differ (concordance rates, sensitivities, correlations, gene overlaps)
and are never pooled. Publishing favours positive findings, so this reflects what authors chose to
report.
:::

## Choosing the next programme {#selection|Programme selection}

{{n_human_first}} of {{n_pairs}} drug pairs run human approval first and the veterinary evidence
later; {{n_vet_first}} run the other way. Median gap: **{{median_lag}} years**. Companion-animal
medicine adopts human drugs, late.

Crossing {{n_human_programs}} human programmes against {{n_pet_programs}} companion-animal ones,
filtered on where this review finds dog biology corresponds, leaves **{{n_candidates}} candidates**.

[**Programme selection: licensing human molecules for dogs and cats →**](caninisation.html)

## Evidence map {#map}

Distinct studies per disease area and species; the superscript is the highest evidence level in the
cell. Companion dogs and cats are kept separate from laboratory ones throughout.

{{heatmap}}

::: note
{{n_unresolved}} results name their animals only as "animals", "both species" or "rodents", so every
species total is a lower bound.
:::

## The results {#results}

Filter by level, species, disease area or direction. Each row links to its study, the quote and the
page it came from.

[**Browse all {{n_results}} results →**](results.html)

## Drug pairs {#pairs}

Agents used both in companion animals with naturally occurring disease and in people: does the
veterinary evidence point the same way as the human evidence?

{{pairs_strata}}

::: note How to read this
Most are human medicines adopted into veterinary practice later, so agreement records adoption, not
prediction. "Discordant" is used only where all available evidence points the opposite way.
:::

[**Browse all pairs →**](pairs.html)

## Companion animals vs laboratory models {#q4|Companion vs laboratory}

For the same agent and condition, did each match what happened in people?

{{q4_tables}}

::: note What this cannot tell you
104 of 108 pairs have a positive human result and the laboratory literature is almost uniformly
positive, so agreement is close to automatic. Only 4 pairs have a negative human result — the case
where predictive value would show — and there laboratory models matched 0, companion animals 1.
:::

## Methods {#methods}

A study is eligible if it reports a finding in live non-human animals alongside the corresponding
human finding. Animal-only results, in-vitro work and figures quoted from another paper are not.

Retrieval by citation chasing and PubMed queries, run as two independent mechanisms so coverage can
be estimated; two screening stages; extraction from open-access full text, every result carrying its
sentence and page; verification by a second model; then adjudication of every result, including the
ones verification rejected, so the checking step cannot quietly remove evidence. Models screen,
extract and verify. Nothing here is summarised by one — the counts are computed from the records.

{{recall}}

Of the results verification accepted, **34% were later dropped or corrected**; of those it rejected,
**10% were reinstated**. {{n_single_reviewer}} of {{n_results}} were adjudicated by a single
unblinded reviewer — the ones the [spot-check](spotcheck.html) oversamples.

## Limitations {#limits}

- **A sample, not a census.** Capture–recapture estimates 33% coverage (95% CI 26–46%), itself an
  upper bound.
- **Open-access full text only**, and the veterinary side of the pairs is largely read from abstracts.
- **Rows are not independent.** A paper reporting one comparison gene by gene yields many rows from
  a single sentence.
- **Not commensurable.** Different quantities, grouped only where metric and unit match, never pooled.
- **The literature is selective**, which inflates apparent agreement — most visibly in the
  companion-versus-laboratory comparison.
- **Agreement is not prediction.** Most pairs are human medicines adopted later in veterinary practice.
- **Part of the adjudication was single-reviewer and unblinded**, across different studies, so
  agreement between adjudicators cannot be measured.
- **{{n_unresolved}} results could not be resolved to one species.**

::: small
All {{n_limitations}} limitations, the protocol, the data and the code that built this site are in
the [project repository](https://github.com/rohitium/animal-model-concordance).
:::

## Verify this work {#verify}

A fixed, seeded sample of the review's own results, each with its source, its page and the sentence
it came from. Forty items, about five minutes each.

[**Open the spot-check →**](spotcheck.html)
