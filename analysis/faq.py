"""FAQ content, kept as data so the numbers stay bound to the database."""
def build(k):
    return [
 ("How is the concordance verdict decided? Is there a numeric threshold?",
  ["<p>Yes — there is now a deterministic rule, and it is the primary summary. Every extracted "
   "figure that carries concordance information is put on a common 0–1 scale where 1 means the "
   "animal result tracked the human result. Figures that point the other way are inverted: a 92% "
   "failure rate becomes 0.08. Correlations use |r| or R². The study's score is the median of its "
   "figures, and the cut-offs are <strong>≥0.70 supports, 0.40–0.70 partly supports, "
   "&lt;0.40 does not support</strong>.</p>",
   "<p>An earlier version of this page argued that no threshold was possible because a "
   "concordance rate, a correlation and a failure rate cannot share a cut-off. That was wrong: "
   "direction is trivially normalisable, and the argument was an excuse for not doing the work. "
   f"The rule now scores <strong>{k['n_scored']} of {k['n_studies']}</strong> studies.</p>",
   "<p>Which statistics count, how each is oriented and where the cut-offs sit are all written "
   "out in <code>analysis/37_objective_verdict.py</code>; anyone can recompute the verdicts or "
   "change the cut-offs. Moving them from 0.70/0.40 to 0.65/0.35 shifts four studies from "
   "partly-supports to supports and leaves does-not-support unchanged.</p>"]),

 ("Why do some studies have no numeric verdict?",
  [f"<p>Because <strong>{k['n_unscored']} of {k['n_studies']}</strong> studies report nothing "
   "reducible to a concordance scale. Their figures are p-values, regression slopes, Mahalanobis "
   "distances, fold-changes, likelihood ratios and odds ratios — real results, but not "
   "expressible as “how often did the animal result match the human one”.</p>",
   "<p>That is itself a finding about the field: roughly half of the studies that measure "
   "animal-to-human correspondence do not report it as a rate of agreement, which is a large part "
   "of why concordance figures are hard to compare across papers.</p>"]),

 ("The verdicts disagree with each other. How much should I trust them?",
  [f"<p>Treat the numbers as primary and the labels as contested. Three independent verdicts exist "
   f"for each study and they agree only moderately:</p>",
   "<table><tr><th>Comparison</th><th>Agreement</th><th>Cohen's κ</th></tr>"
   f"<tr><td>Model rater 1 vs model rater 2</td><td>{k['r1r2_a']:.0%}</td><td>{k['r1r2_k']:.2f}</td></tr>"
   f"<tr><td>Numeric rule vs rater 1</td><td>{k['rule_r1_a']:.0%}</td><td>{k['rule_r1_k']:.2f}</td></tr>"
   f"<tr><td>Numeric rule vs rater 2</td><td>{k['rule_r2_a']:.0%}</td><td>{k['rule_r2_k']:.2f}</td></tr></table>",
   "<p>The two model raters agree moderately with each other and poorly with the rule. Both have "
   "known weaknesses. The rule takes a median across statistics that mean different things within "
   "one paper, so a high negative predictive value — which is usually high simply because most "
   "findings are negative — can pull a study upward. The model raters weigh which figure matters "
   "but are only moderately reproducible.</p>",
   "<p>Neither is treated as authoritative. Each study page shows all three, and where they "
   "disagree that is displayed rather than resolved. A disagreement is a reliable signal that the "
   "evidence in that paper is genuinely mixed.</p>"]),

 ("Can I compare organisms against each other using this table?",
  ["<p><strong>Not across assessments.</strong> Dog evidence here is mostly regulatory toxicology, "
   "which reports predictive values and sensitivity. Mouse evidence is mostly disease biology and "
   "efficacy, which report correlations and translation rates. Efficacy translation fails often in "
   "every species; toxicology prediction succeeds more often. Comparing dog rows with mouse rows "
   "without holding the assessment fixed largely measures the assessment.</p>",
   "<p>Comparisons within one assessment are meaningful.</p>"]),

 ("A row shows a wide range, such as 31–85%. What does that mean?",
  ["<p>It is the span of several sub-analyses, not an uncertainty interval, and the midpoint is "
   "not an estimate. Each row states what varies across the range.</p>",
   "<p>One case matters. In Daluwatumulle et al. 2026 the dog cancer scores run 31–85%, but the "
   "bottom is a <strong>negative control</strong>: leukaemia (40%) and adrenocortical carcinoma "
   "(31%) were deliberately included as cancers expected to be poor dog models, to check the "
   "metric flags them. It does. Real cancer types score 62–85%, led by bladder cancer at 85%. "
   "Reading 31% as dog performance inverts the paper's meaning.</p>"]),

 ("Does this show that companion-animal (dog) models translate worse than mouse models?",
  ["<p>No, and the data cannot support that comparison in either direction. No study here "
   "benchmarks dog against mouse on the same endpoint, and the two organisms are assessed on "
   "different things.</p>",
   "<p>What the corpus does show is a gap in the evidence: a targeted search for veterinary-patient "
   "studies returned 174 records, of which one met the inclusion rule. The comparative-oncology "
   "literature argues that naturally occurring disease in companion animals is a good model far "
   "more often than it measures whether it predicts human outcomes.</p>",
   "<p>The clearest negative result for companion animals in this corpus is specific and worth "
   "stating: Petersen-Jones et al. 2015 found dog RPE65 gene therapy did not track human outcomes "
   "— dogs recovered near-normal vision and electroretinogram responses, while patients showed no "
   "ERG change and remained visually impaired.</p>"]),

 ("What counts as a study here?",
  ["<p>It must report a quantitative comparison with a live non-human animal on one side and a "
   "human clinical result on the other. Papers that argue animals do or do not predict human "
   "outcomes without measuring it are excluded, including several well-cited reviews.</p>",
   "<p>Also excluded: predictors that are not whole animals (cell lines, organoids, organ-on-chip, "
   "isolated ion-channel assays, QSAR and PBPK models), and comparisons within one species. "
   "Patient-derived xenografts are reported separately, because they grow a patient's own tumour "
   "in a mouse host and so test whether a patient's tumour predicts that patient.</p>"]),

 ("Is this a systematic review?",
  [f"<p>No. It is a structured reading of {k['n_studies']} studies selected from a screened pool "
   "by a score combining citations and recency — deliberately weighted toward authoritative and "
   "recent work, and not a random sample. Verdict counts describe this corpus and nothing "
   "wider.</p>"]),

 ("Has any of this been checked by a person?",
  ["<p>Not systematically. Screening, classification and extraction are model-assisted. Every "
   "figure carries the sentence it came from and the table or figure it appeared in, so any number "
   "can be checked against its source, but only a small fraction have been. Spot-checks have found "
   "real defects, each recorded in the limitations file rather than quietly corrected.</p>",
   "<p>Treat this as a structured index into the literature that makes checking cheap, not as a "
   "verified dataset.</p>"]),
]
