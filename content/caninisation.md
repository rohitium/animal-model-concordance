::: dek
Programme selection
:::

# Licensing human molecules for dogs and cats

::: lede
Companion-animal medicine mostly adopts drugs that already work in people, and adopts them late.
This page asks which human molecules are the best candidates to license and develop for dogs and
cats, using the review's own evidence on where dog biology corresponds to human.
:::

{{cand_figures}}

## The pattern this rests on {#pattern}

Of {{n_pairs}} classified drug pairs, {{n_human_first}} run human approval first and the veterinary
evidence later. {{n_vet_first}} run the other way. Among pairs where both dates are known the median
gap is **{{median_lag}} years**.

{{cand_lag}}

::: note What the lag does and does not mean
A long lag says veterinary medicine adopts human drugs slowly. It does not say those drugs were
predictable from animal evidence — the direction of travel is human first, so the two sides are not
independent tests of each other. The opportunity here is adoption, not prediction.
:::

## How candidates are selected {#selection}

A molecule is a candidate when it has **both** legs of human evidence — safety and efficacy — and
either has no companion-animal programme against its target, or was stopped for a reason unrelated
to how it performed clinically.

An approved drug carries both legs by definition: the approval is the evidence. A discontinued drug
carries them only if it got far enough to show efficacy and was dropped for some other reason —
supply, portfolio, partnership, or the company itself. A drug that failed on efficacy is not a
starting point, because demonstrated efficacy is the premise of the whole approach.

{{cand_routes}}

::: note Route 1 is not all open ground
{{n_formulary}} of the {{n_route1}} route-1 molecules are already in routine veterinary use as
generics — furosemide, tadalafil, losartan, triamcinolone and betamethasone among them. They appear
here because no *company programme* in the supplied list targets them, which is not the same as no
dog being given them. Each is flagged in the table below. Treat route 1 as "no branded programme
found", never as "untried in dogs".
:::

## What "no companion-animal programme" actually means {#presence}

A route says whether a *company programme* holds the molecule's mechanism. It does not say whether
dogs and cats already receive the drug, nor whether the disease is already served by something else.
Those are different questions, and answering only the first overstates how open a space is.

Every molecule is therefore checked against four sources, and the table reports what each one found:
the mechanism it works, the corresponding condition in dogs or cats, the veterinary literature under
its own name, and this review's own drug-pair records.

{{cand_presence}}

Only **{{n_nothing_found}}** of the {{n_candidates}} candidates return nothing on any check.
{{n_occupied}} have a companion-animal programme working the same mechanism. {{n_mech_open}} have an
unoccupied mechanism inside a condition that is already contested — an anti-IL-4Rα antibody faces no
IL-4Rα competitor in dogs, but canine atopic dermatitis is held by Apoquel, Cytopoint, Zenrelia,
Befrena and five cyclosporine products. That is the distinction worth acting on: an open mechanism
is not an open market.

::: note What is not checked
No register of approved veterinary medicines is in the loop. The FDA Green Book publishes no
machine-readable export, openFDA's animal endpoint returns adverse events rather than approved
products, and the EMA veterinary dataset has moved behind a portal with no download. A molecule
approved for dogs or cats outside the supplied list would show here as "not found". Absence of a
finding is never evidence of absence, and adding a veterinary registry is the single most valuable
fix available to this analysis.
:::

::: note Why route 3 is so small
Most discontinuations are clinical. Reading each source link rather than pattern-matching its
headline leaves very few assets that were genuinely shelved for non-clinical reasons, and only one
that is both approved and cleanly documented. Assets whose stated reason could not be established
are held back rather than counted, because a headline verb is not a reason: one programme's source
reads "pulls the plug", which sounds commercial, while the programme itself carried a clinical hold,
an FDA-halted trial and a monitoring committee's dose halt.
:::

## Where the evidence is {#areas}

The review answers one question the market cannot: does this disease's biology correspond between
dog and human? Areas are ranked on how often findings agreed, weighted by evidence level, together
with how much of that evidence is intervention outcomes rather than biological similarity.

{{cand_areas}}

::: note Read the kind of evidence, not only the rate
Oncology has the most evidence and the weakest kind: dog and human tumours look alike
transcriptomically, which is a claim about biology rather than about whether treating them works.
Immunology has the highest agreement rate and no intervention outcomes at all. Cardiovascular has
the smallest volume and the best kind — most of its results are level A.
:::

## A claimed target is not a closed door {#crowding}

Crowding is market validation. The indications with the most companion-animal programmes are the
indications worth entering, and companies already enter them against incumbents.

{{cand_crowding}}

## Brutinib inhibitors: evidence without a programme {#btk}

Three BTK inhibitors reached dogs at or before their human approval, and no companion-animal BTK
programme exists in the supplied list of {{n_pet_programs}} programmes. That looks like an opening,
and the review's own records explain why it has stayed open.

| Molecule | Canine evidence | What that evidence is | Human |
|---|---|---|---|
| Ibrutinib | Spontaneous canine B-cell non-Hodgkin lymphoma | A single dose-finding study reporting objective responses | Approved 2013 |
| Acalabrutinib | Canine B-cell lymphoma, 25% response rate (5 of 20) | Single-arm, n=20, median progression-free survival **22.5 days** | Approved 2017 |
| Rilzabrutinib | Canine pemphigus | A sentence in a review saying early studies showed effectiveness; no trial design or outcome | Phase 3 **failed** its primary endpoint |

The canine data is thin, uncontrolled and short-lived. A 25% response rate clears the threshold this
review uses to call a single-arm cancer study positive, but three weeks of progression-free survival
is not a product. No pivotal veterinary trial has been run by anyone, and the one BTK molecule that
reached a human Phase 3 in the autoimmune indication missed its endpoint.

So the honest reading is not that a proven opportunity has been overlooked. It is that the class has
promising, published, early canine signals that nobody has taken to a registrational trial — which
is a reason to run one, and a reason to expect it to be a real trial rather than a formality. Canine
lymphoma is currently held by Laverdia-CA1 (verdinexor, an XPO1 inhibitor), whose own conditional
approval rests on similarly limited data.

## Every candidate {#browse}

All {{n_candidates}} candidates, plus the {{n_watch}} pipeline assets held back for want of an
approval. Filter by route to separate them. Click any row for the dog evidence behind its condition
area, the companion-animal programmes on its target, and the programme source.

{{cand_table}}

## How the list was cut {#funnel}

{{cand_funnel}}

::: small
The largest exclusion is programmes dropped because the review holds no dog evidence for their
condition area at all. That is a statement about where this review is thin — renal, respiratory,
dermatology and metabolic disease among them — not a judgement on those molecules. It doubles as a
retrieval to-do list.
:::

## What this cannot tell you {#limits}

- **No canine or feline prevalence, market size, or willingness to pay.** No epidemiological source
  is held here. This is probably the largest single determinant of programme value and it is
  absent. The veterinary literature's attention is deliberately not substituted for prevalence: it
  measures what researchers study, not what animals get.
- **"No companion-animal programme" means absent from the supplied {{n_pet_programs}}-programme
  list, not absent from veterinary practice.** That list is branded company programmes, not the
  formulary. Molecules in routine generic veterinary use are flagged separately, but that flag is
  hand-written and incomplete.
- **Patent and exclusivity status is unknown.** Years since first approval is a crude proxy for
  whether a molecule can be licensed cheaply, and says nothing about who controls it now.
- **Target-animal safety is not systematically checked.** The species exclusion list is
  reviewer-supplied and incomplete. An absent flag means not checked, never safe.
- **Molecules within an area are not ranked.** Every candidate in an area inherits the same
  evidence, so a blended score would order them by the only things that vary — mostly how old they
  are — while appearing to order them by evidence.
- **Formulation, route, palatability and dosing interval** in the target species are not assessed.

::: small
Built by crossing two supplied programme lists — {{n_human_programs}} human and
{{n_pet_programs}} companion-animal — against the review's {{n_results}} adjudicated results in
{{n_studies}} studies, plus Drugs@FDA for brand-to-ingredient and approval dates, a condition-area
mapping, a companion-animal target index, and a species-safety exclusion list. Discontinuation
reasons are read from each programme's own source. This is an analysis for programme selection, not
a valuation.
:::
