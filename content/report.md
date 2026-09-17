::: dek
Systematic review
:::

# Brief survey of animal-to-human concordance in the biomedical literature

::: lede
We reviewed studies directly comparing a finding in live animals against the same finding in humans,
then collected the evidence.
:::

## Summary {#summary}

Each row is one comparison a paper drew between an animal and a human. 
**A**: treatment outcomes,
**B**: toxicity and safety, 
**C**: disease biology.

{{level_table}}

::: note Caveats
Dominated by evidence level C — how similar the biology looks, not what happened when a disease was treated. 

Quantities reported across multiple studies are not pooled, in general. 

Publications generally biased toward positive findings.
:::

## Evidence map {#map}

Studies per disease area and species; the superscript is the highest level in that cell. Companion
and laboratory dogs and cats are counted separately. The grid holds the {{n_species_results}}
results that name a species. The other {{n_no_species}} are not on it: they state a finding about
animal models as a class rather than about a named species, so there is no species to place.

{{heatmap}}

[**Browse all {{n_results}} results →**](results.html)

## Choosing Nori's first program {#selection|Program selection}

How can this collection of concordance evidence help us select our first candidate? We collected pairs
of drugs with similar mechanisms targeted toward both human and companion animals, then asked whether
the clinical outcomes pointed in the same direction.

{{pairs_strata}}

::: note How to read this
Most are human medicines adopted later in veterinary practice, so agreement records adoption, not
prediction. 

"Discordant" means all evidence points the opposite way.
:::

[**Browse all pairs →**](pairs.html)

We found that {{n_human_first}} of {{n_pairs}} drug pairs were approved for humans first, {{n_vet_first}} the reverse,
and a median gap **{{median_lag}} years** between human drug approval and vet drug approval. 

Filtering {{n_human_programs}} human programs on where dog biology corresponds leaves **{{n_candidates}} candidates**.

[**Program selection →**](caninisation.html)

## Companion animals vs laboratory models {#q4|Companion vs laboratory}

{{q4_tables}}

::: note Extreme class imbalance
104 of 108 pairs have a positive human result and the laboratory literature is almost uniformly
positive, so agreement is near-automatic. 

On the 4 negative-human pairs, laboratory models matched 0 and companion animals 1.
:::

## Methods {#methods}

Eligible: a finding in live animals reported alongside the human one. Two independent retrieval
mechanisms, two screening stages, extraction from open-access full text with sentence and page,
verification by a second model, then adjudication of every result — including those verification
rejected. Counts are computed from the records, not summarized by a model.

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
- {{n_no_species}} results are kept off the evidence map: nearly all carry a grouped label
  ("animals", "rodents") rather than a species. A minority record the human side of the
  comparison in the animal field. Results naming several species now count toward each.

::: small
All {{n_limitations}} limitations, the protocol, data and code:
[repository](https://github.com/rohitium/animal-model-concordance).
:::

## Verify this work {#verify}

Forty seeded results, each with its source, page and sentence.
[**Open the spot-check →**](spotcheck.html)
