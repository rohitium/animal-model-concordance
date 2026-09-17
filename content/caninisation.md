::: dek
Programme selection
:::

# Licensing human molecules for dogs and cats

::: lede
Which human molecules are the best candidates to license and develop for companion animals, judged
against this review's evidence on where dog biology corresponds to human.
:::

## The pattern this rests on {#pattern}

{{n_human_first}} of {{n_pairs}} drug pairs run human approval first and the veterinary evidence
later; {{n_vet_first}} run the other way. Median gap: **{{median_lag}} years**.

{{cand_lag}}

::: note What the lag does and does not mean
A long lag says veterinary medicine adopts human drugs slowly. It does not say those drugs were
predictable from animal evidence: the direction of travel is human first, so the two sides are not
independent tests of each other. The opportunity is adoption, not prediction.
:::

## How candidates are selected {#selection}

A candidate needs **both** legs of human evidence — safety and efficacy — and either no
companion-animal programme on its mechanism, or a stop unrelated to clinical performance. An
approval carries both legs by definition. An efficacy failure is disqualifying, because demonstrated
efficacy is the premise.

{{cand_routes}}

::: note Route 1 is not open ground
{{n_formulary}} of the {{n_route1}} route-1 molecules are already routine veterinary generics —
furosemide, tadalafil, losartan, triamcinolone, betamethasone. They qualify because no *company
programme* targets them, which is not the same as no dog receiving them. Each is flagged in the table.
:::

::: note Why route 3 is so small
Most discontinuations are clinical. One programme's source reads "pulls the plug", which sounds
commercial, while the programme carried a clinical hold, an FDA-halted trial and a monitoring
committee's dose halt. Assets whose reason could not be established are held back, not counted.
:::

## What "no companion-animal programme" means {#presence}

A route says whether a *marketed product* works the molecule's mechanism. It does not say whether
dogs already receive the drug, whether the condition is already served by something else, or whether
competitors hold patents and simply have not launched.

Anti-IL-4Rα is the case in point. No IL-4R product is marketed for dogs — yet Merck Animal Health
holds a granted patent on anti-canine IL-4Rα with 2015 priority, Vetoquinol and Kindred Biosciences
have their own filings, and Elanco wrote off its IL-4R pet asset in 2024 for commercial reasons. A
mechanism can be thick with intellectual property and abandoned assets while the marketed-product
column stays empty.

Every molecule is therefore checked against the mechanism, patents and halted programmes recorded
against it, the corresponding companion condition, the veterinary literature, and this review's own
pair records.

{{cand_presence}}

Only **{{n_nothing_found}}** of {{n_candidates}} candidates return nothing on any check.
{{n_mech_open}} have an open mechanism inside a contested condition — an anti-IL-4Rα antibody faces
no IL-4Rα competitor in dogs, but canine atopic dermatitis is held by Apoquel, Cytopoint, Zenrelia,
Befrena and five cyclosporine products. **An open mechanism is not an open market.**

::: note What is not checked
**No register of approved veterinary medicines.** The FDA Green Book publishes no machine-readable
export, openFDA's animal endpoint returns adverse events, and the EMA veterinary dataset has no
download. A drug approved for dogs outside the supplied list shows here as "not found".

**The patent and halted-programme search is not systematic.** Both are recorded only for mechanisms
where someone looked: Google Patents blocks automated querying and the APIs that would replace it
need credentials. **A mechanism with no patent entry has not been searched, and must not be read as
free of intellectual property.** Anti-IL-4Rα read as open until someone looked, and four companies
had filed on it.

A veterinary drug registry and a patent API credential are the two highest-value additions to this
work.
:::

## Where the evidence is {#areas}

Areas ranked on how often dog and human findings agreed, weighted by evidence level and by how much
of that evidence is treatment outcomes rather than biological similarity.

{{cand_areas}}

::: note Read the kind of evidence, not only the rate
Oncology has the most evidence and the weakest kind — tumours look alike transcriptomically, which
is a claim about biology, not treatment. Immunology has the highest agreement rate and no treatment
outcomes at all. Cardiovascular has the least volume and the best kind.
:::

## A claimed target is not a closed door {#crowding}

Crowding is market validation: the indications with the most companion-animal programmes are the
ones worth entering, and companies already enter them against incumbents.

{{cand_crowding}}

## BTK: evidence without a programme {#btk}

Three BTK inhibitors reached dogs at or before their human approval and no companion-animal BTK
programme exists in the supplied list. The review's own records explain why it has stayed open.

| Molecule | Canine evidence | What that evidence is | Human |
|---|---|---|---|
| Ibrutinib | Spontaneous canine B-cell non-Hodgkin lymphoma | A single dose-finding study | Approved 2013 |
| Acalabrutinib | Canine B-cell lymphoma, 25% response (5 of 20) | Single-arm, n=20, median progression-free survival **22.5 days** | Approved 2017 |
| Rilzabrutinib | Canine pemphigus | A sentence in a review; no trial design or outcome | Phase 3 **missed** its endpoint |

Thin, uncontrolled and short-lived: three weeks of progression-free survival is not a product. Not a
proven opportunity overlooked, then, but early signals nobody has taken to a registrational trial.
Canine lymphoma is held by Laverdia-CA1 (verdinexor), whose conditional approval rests on similarly
limited data.

## Every candidate {#browse}

All {{n_candidates}} candidates plus the {{n_watch}} pipeline assets held back for want of an
approval. Filter by route to separate them; click any row for the evidence behind it.

{{cand_table}}

## How the list was cut {#funnel}

{{cand_funnel}}

::: small
The largest exclusion is programmes dropped because the review holds no dog evidence for their
condition area — a statement about where this review is thin, not about those molecules.
:::

## What this cannot tell you {#limits}

- **No canine or feline prevalence, market size or willingness to pay.** Probably the largest single
  determinant of programme value, and absent. The veterinary literature's attention is deliberately
  not substituted for it: that measures what researchers study, not what animals get.
- **"Not found" is a statement about the checks that were run**, listed above. The supplied list is
  branded company programmes, not the formulary.
- **Patent status is recorded only where it was searched.** Where none is shown, the mechanism has
  not been searched rather than found clear.
- **Target-animal safety is not systematically checked.** An absent flag means not checked, never safe.
- **Molecules within an area are not ranked.** They inherit the same evidence, so a score would order
  them by how old they are while appearing to order them by evidence.
- **Formulation, route, palatability and dosing** are not assessed.

::: small
Built by crossing the two supplied programme lists against this review's adjudicated results, plus
Drugs@FDA for ingredients and approval dates, a condition-area mapping, a companion-animal target
index and a species-safety exclusion list. An analysis for programme selection, not a valuation.
:::
