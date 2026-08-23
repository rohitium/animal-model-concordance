# How verdicts are assigned

A question collaborators ask first, and it deserves a direct answer: **there are no numeric
thresholds.**

## Why not

The three verdicts are applied to studies whose statistics are not commensurable. Olson 2000
reports 63% concordance of human toxicities in non-rodents; Seok 2013 reports a Pearson R² of
0.09 between mouse and human gene expression; Marshall 2023 reports that over 92% of drugs
fail to translate. No cut-off can span a concordance rate, a correlation coefficient and a
failure rate, because a high value means success in the first two and failure in the third.
A numeric rule would have to be defined per statistic, and most statistics appear in only one
or two studies — the threshold would be fitted to the study it judged.

## What is applied instead

Each study is read from its full-text PDF and judged against a fixed rubric:

| Verdict | Criterion |
|---|---|
| supports | the animal results corresponded well to the human results |
| partly-supports | mixed — good for some species, endpoints or conditions and not others |
| does-not-support | the animal results did not correspond |
| no-data | no animal-to-human comparison is reported (study is then excluded) |

with three binding rules:

1. **Judge the data, not the prose.** The rubric directs the reader to results, tables and
   figures and to ignore how authors characterise their own findings. Abstracts editorialise
   in both directions.
2. **`verdict_basis` must cite specific numbers** and contain no adjectives. Every verdict on
   the site shows this text, so a reader can check the judgement against the figures.
3. **Negative controls are not failures.** Where a paper deliberately includes comparisons
   expected to score low in order to validate its metric, those are excluded from the verdict.

## The limitation this leaves

Consistency is not guaranteed by a rule, so it must be measured rather than assumed. An
independent second rater (a different model family, same PDFs, same rubric) re-judges every
study; agreement between the two is reported as a percentage and Cohen's κ, and every
disagreement is listed. Where the two raters disagree, the study is flagged on its page: a
disagreement is a signal that the evidence is genuinely ambiguous, not something to average
away.

## Reading a verdict correctly

A verdict is a judgement **about one study's data**, not a score for an organism or a model
class. Two things follow:

- **Verdict tallies count studies, not predictive performance.** The corpus is not a random
  sample of the literature.
- **Do not compare organisms across assessments.** Dog evidence in this corpus comes mostly
  from regulatory toxicology (PPV, NPV, sensitivity, specificity); mouse evidence comes mostly
  from disease biology and efficacy (correlations, survival change, success rates). Comparing
  the organism rows without holding the assessment fixed measures the assessment, not the
  organism.
