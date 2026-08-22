# Site revamp plan

Two page types only: a landing page, and one page per study.

## 1. Landing page

### The main table

Three columns: **Assessment · Model organism · Evidence**

One row per (assessment × model organism) pair. A study appears in as many rows as it
has organisms reported separately.

| Assessment | Model organism | Evidence |
|---|---|---|
| Toxicology | dog | 63% of human toxicities also seen in dog studies (Olson 2000, n=150 compounds) · PPV 43%, NPV 92% for dog toxicology vs human adverse events (Monticello 2017, n=182 molecules) |

**Assessment** replaces "arm": efficacy · safety pharmacology · toxicology · disease
biology · veterinary.

**Model organism** is the species as the study reports it. Grouped labels stay grouped
and get their own rows — `rodent (as grouped)` and `non-rodent (as grouped)` are never
expanded into member species, because a paper reporting "43% of rodent studies" did not
measure mice separately.

### Aggregation rules

The instruction is to aggregate as far as possible *without destroying the meaning of the
original statistics*. That constrains what may be combined:

1. **Never average across studies.** Studies define concordance differently; a mean of
   incompatible definitions is not a quantity.
2. **A range may be shown only within one statistic, one assessment and one organism** —
   e.g. "concordance 43–63%" across two studies both reporting concordance of human
   toxicities. Different statistics are listed separately, never merged into a range.
3. **Every figure keeps its n and its citation.** No number appears without what it counts
   and who reported it.
4. **Direction is explicit.** A high failure rate and a high concordance rate point
   opposite ways; each cell states what the number means, not just its value.
5. **Base-rate caveats are attached to the figure, not hidden.** NPV of 92–99% is usually
   high because most findings are negative; where a study's own caveat says so, it is
   shown with the figure.

### Verdict summary

Above the table, a compact tally per assessment: how many studies support, partly support,
or do not support concordance, from the data rather than the authors' framing.

Current: supports 8 · partly-supports 22 · does-not-support 4 (34 of 57 processed).

### Also on the landing page
- One-paragraph statement of what the review asks and what counts as evidence.
- Counts: studies, organisms, assessments, comparisons.
- Method note in a few sentences, with a link to the protocol in the repository.
- Excluded studies as a collapsed list with reasons (kept for auditability).

## 2. Study page

One page per study, in this order:

1. **Citation** — Author et al. Year, journal, PMID/DOI/PMC links.
2. **What was compared** — animal side (species or grouped label, strain, how the disease
   arose, n) against human side (population, disease, stage, trial phase, n), and whether
   the endpoints are identical, analogous or non-analogous.
3. **Verdict** — supports / partly supports / does not support, with the numbers that
   justify it.
4. **Figures reported** — every animal↔human comparison: value in the unit as printed,
   statistic, what was compared, n and what n counts, **where it came from** (Table 3,
   Figure 2, Results p4), and the verbatim sentence.
5. **Caveats** — base-rate or design caveats that would make a figure misleading alone.
6. **Abstract, MeSH terms, provenance** — last, for reference.

## 3. Removed

- Findings, Species, Areas, Arms, Methods and Excluded as separate pages; their content
  either folds into the landing page or is dropped.
- The metric leaderboard: ranking sensitivity, specificity, NPV and concordance against
  each other implied comparisons that do not exist.
- Subcategory explosions: a study reporting NPV per organ system per species contributes
  its overall figure and its per-species figures, not every cell.

## 4. Open questions

1. **Row ordering** — by assessment then organism (stable, easy to scan), or by weight of
   evidence (more informative, less predictable)? Default: assessment, then organism by
   number of studies.
2. **Organisms with one study** — show inline, or group into a "single-study organisms"
   row to keep the table short? Default: show inline; the table is expected to be roughly
   30–40 rows.
3. **Cell length** — some cells will carry several figures. Show all, or the strongest two
   with the rest on the study page? Default: show all, since omitting figures is what
   made earlier pages misleading.
