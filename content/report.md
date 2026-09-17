::: dek
Systematic review
:::

# Brief survey of animal-to-human concordance in the biomedical literature

::: lede
Studies comparing a finding in live animals against the same finding in humans, and what they found.
:::

## Summary {#summary}

Each row is one comparison a paper drew between an animal and a human. **A** treatment outcomes,
**B** toxicity, **C** disease biology.

{{level_table}}

::: note Caveats
Mostly level C — how similar the biology looks, not what happened when a disease was treated. The
quantities differ and are never pooled. Publishing favours positive findings.
:::

## Choosing the next programme {#selection|Programme selection}

{{n_human_first}} of {{n_pairs}} drug pairs run human approval first, {{n_vet_first}} the reverse,
median gap **{{median_lag}} years**. Filtering {{n_human_programs}} human programmes on where dog
biology corresponds leaves **{{n_candidates}} candidates**.

[**Programme selection →**](caninisation.html)

## Evidence map {#map}

Studies per disease area and species; the superscript is the highest level in that cell. Companion
and laboratory dogs and cats are counted separately. {{n_unresolved}} results name their animals
only as "animals" or "rodents", so totals are lower bounds.

{{heatmap}}

## The results {#results}

[**Browse all {{n_results}} results →**](results.html)

## Drug pairs {#pairs}

Agents used in both companion animals and people: does the veterinary evidence agree?

{{pairs_strata}}

::: note How to read this
Most are human medicines adopted later in veterinary practice, so agreement records adoption, not
prediction. "Discordant" means all evidence points the opposite way.
:::

[**Browse all pairs →**](pairs.html)

## Companion animals vs laboratory models {#q4|Companion vs laboratory}

{{q4_tables}}

::: note What this cannot tell you
104 of 108 pairs have a positive human result and the laboratory literature is almost uniformly
positive, so agreement is near-automatic. On the 4 negative-human pairs, laboratory models matched
0 and companion animals 1.
:::

## Methods {#methods}

Eligible: a finding in live animals reported alongside the human one. Two independent retrieval
mechanisms, two screening stages, extraction from open-access full text with sentence and page,
verification by a second model, then adjudication of every result — including those verification
rejected. Counts are computed from the records, not summarised by a model.

{{recall}}

Of results verification accepted, 34% were later dropped or corrected; of those it rejected, 10%
were reinstated. {{n_single_reviewer}} of {{n_results}} had a single unblinded adjudicator,
oversampled by the [spot-check](spotcheck.html).

## Limitations {#limits}

- ~33% coverage (CI 26–46%), itself an upper bound.
- Open-access full text only; veterinary side largely from abstracts.
- Rows sharing a sentence are not independent evidence.
- Quantities grouped only where metric and unit match.
- Selective publishing inflates apparent agreement.
- Agreement is not prediction.
- Adjudication partly single-reviewer and unblinded.
- {{n_unresolved}} results unresolved to one species.

::: small
All {{n_limitations}} limitations, the protocol, data and code:
[repository](https://github.com/rohitium/animal-model-concordance).
:::

## Verify this work {#verify}

Forty seeded results, each with its source, page and sentence.
[**Open the spot-check →**](spotcheck.html)
