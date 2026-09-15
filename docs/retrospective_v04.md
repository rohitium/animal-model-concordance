# Retrospective on v0.4 (2026-09-14) and a simpler plan

## What happened

A day of building produced a lot of machinery and no usable answer:
- two-model extraction of every comparison;
- a nine-item verifier;
- canaries and a model-tier ladder;
- a 1,202-item decision stage;
- a review web page;
- 4.4 GB of FDA and ClinicalTrials.gov snapshots in a SQLite database;
- two drug-pair pilots.

Both gates failed:
- **Step 1:** 95% flag rate, and canary C1 (Perel's "3 of 6") missed at tier 2.
- **Pilot 2:** 6 pairs, all indeterminate.

LLM spend was about $6. The real cost was time and complexity.

## Why

1. **Infrastructure came before the answer.** Every failure prompted another layer of checks instead
   of asking whether the task was well posed.
2. **The tasks were ill-defined, then policed.**
   - "Extract every animal-vs-human comparison" has no single right answer. Two good readers carve a
     paper differently: 253 of 483 single-extractor flags had no counterpart at all.
   - The verifier and agreement checks then flagged the disagreement, not errors.
   - Changing model tier changed little (99% → 95%).
3. **The frames were too generic.**
   - A random draw of 3,000 pet-animal trials is mostly flea, worm and anaesthesia studies.
   - The whole of ClinicalTrials.gov is exhaustive but thin: most matched trials posted no analysable
     results.
   - The drug-pair question is about a few dozen drugs, not about registries.
4. **Too many small questions went to the user.** Routine design and debugging decisions belong in the
   amendment log, not the conversation.
5. **Process errors** (sequential steps, hung calls, self-matching kill commands) cost hours. Fixed, and
   recorded in memory.

## What the deliverable actually needs

The page-15 replacement makes a few claims, each resting on a small number of key studies:

| Claim | Evidence it needs | Size |
|---|---|---|
| Lab-animal efficacy translates poorly | Headline numbers from the key meta-research: Ineichen 2024 umbrella review, Hackam 2006, Perel 2007, O'Collins 2006, van der Worp 2010, and similar | ~10–15 papers |
| Toxicology concordance is partial and species-dependent | Headline PPV/NPV/sensitivity/LR per species: Olson 2000, Monticello 2017, Clark 2018, Atkins 2020, Bailey 2014/2016 | ~6–10 papers |
| Model biology resembles human disease to varying degrees (by disease area) | Headline similarity results: Seok/Takao and similar, for the evidence map | ~15–20 papers |
| Pet dogs/cats with spontaneous disease: how concordant are they with humans, drug by drug? | A table of drugs tested in both, found by targeted PubMed search | ~30–50 pairs |

That is roughly 40 papers read for their **headline** results, plus a drug-pair table. It is
small enough to do carefully, and small enough for a person to spot-check.

## The simpler plan

### Part 1: evidence table and map (reuse the corpus; about a day)

1. **Fix the study list.** Keep the v0.3 corpus studies that pass the live-animal scope screen (already
   done, stage 1). Add the missing anchors: Ineichen 2024, Hackam 2006, van der Worp 2010, Clark 2018.
   PDFs for any paywalled ones go on the full-text request list.
2. **One targeted question per study, not open enumeration:** "What are this paper's headline
   animal-vs-human concordance results, overall and per species or disease area?" At most about 8
   numbers per paper, each with the exact sentence and page.
3. **Check each number mechanically.** Code confirms it appears on the cited page. A second model
   answers the same question independently; where the two headline sets differ, I read the paper and
   decide, and record the decision.
4. **Human spot-check** of a random 20 numbers, with the error rate published.
5. **Outputs:**
   - the page-15 replacement table: a few rows, each a plain claim with number, CI, n studies and
     certainty;
   - an evidence map: disease area × species, coloured by evidence level.

   Pool only where the same metric recurs (toxicology PPV/NPV by species).

### Part 2: dog/cat drug pairs (start from drugs; PubMed; about 1–2 days)

1. **Candidate drugs** from documented, repeatable sources:
   - the COTC trial list;
   - comparative-oncology reviews (reference lists);
   - FDA-CVM dog/cat approvals whose ingredient is also a human drug (the human index already built
     answers this in seconds);
   - PubMed searches of "client-owned" / "naturally occurring" combined with drug classes.

   Deliberately include known failures (anti-NGF antibodies, others), not just successes. Log every
   candidate found.
2. **For each drug × indication**, search PubMed for the pet-animal efficacy study and the human trial
   evidence in the corresponding indication (pivotal/phase 3 publication, or approval). Read abstracts,
   and full text where the result needs it.
3. **Classify with the existing §7.4 rules** (concordant / discordant / mixed / indeterminate), with a
   short rationale and citations per pair. FDA approval data is a cross-check, not the source.
4. **Output:** a pair table with the 2×2 summary and exact CI, and the plain statements F1–F4 require.

### What is dropped

- Enumerating every comparison.
- The 1,200-item decision stage and review web app.
- Registry-first human evidence.
- Random vet-trial sampling.

The downloaded snapshots stay on disk for the approval cross-check only. Protocol v0.4's questions,
falsifiers and classification rules stay; the machinery changes. Logged as amendment A6.

### Working agreement

- I resolve bugs and routine method decisions myself, and record them in `protocol/amendments.md` and
  `docs/limitations.md`.
- Check-ins with the user happen at three milestones only:
  1. Part 1 table and map drafted, with the spot-check sample;
  2. drug-pair table drafted;
  3. final page-15 replacement.
