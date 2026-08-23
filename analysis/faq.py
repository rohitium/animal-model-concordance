"""FAQ content, kept as data so the numbers stay bound to the database."""
def build(k):
    return [
 ("How is the concordance verdict decided? Is there a numeric threshold?",
  ["<p>Yes. Every figure carrying concordance information is put on a 0–1 scale where 1 means "
   "the animal result tracked the human result. Figures pointing the other way are inverted, so a "
   "92% failure rate becomes 0.08; correlations use |r| or R². A study's score is the median of "
   "its figures, with cut-offs at <strong>≥0.70 supports</strong>, "
   "<strong>0.40–0.70 partly supports</strong>, <strong>&lt;0.40 does not support</strong>.</p>",
   "<p>Which statistics count, how each is oriented and where the cut-offs sit are written out in "
   "<code>analysis/37_objective_verdict.py</code>. Moving the cut-offs to 0.65/0.35 shifts four "
   "studies from partly-supports to supports and leaves does-not-support unchanged.</p>"]),

 ("Why do some studies have no numeric verdict?",
  [f"<p><strong>{k['n_unscored']} of {k['n_studies']}</strong> studies report nothing reducible to "
   "a concordance scale — their figures are p-values, regression slopes, Mahalanobis distances, "
   "fold-changes and odds ratios. Real results, but not rates of agreement.</p>",
   "<p>That roughly half the field does not express animal-to-human correspondence as agreement is "
   "a large part of why concordance figures rarely compare across papers.</p>"]),

 ("How much should I trust the verdicts?",
  ["<p>Treat the figures as the evidence and the labels as contested. Three independent verdicts "
   "exist per study and they agree only moderately:</p>",
   "<table><tr><th>Comparison</th><th>Agreement</th><th>Cohen's κ</th></tr>"
   f"<tr><td>model rater 1 vs model rater 2</td><td>{k['r1r2_a']:.0%}</td><td>{k['r1r2_k']:.2f}</td></tr>"
   f"<tr><td>numeric rule vs rater 1</td><td>{k['rule_r1_a']:.0%}</td><td>{k['rule_r1_k']:.2f}</td></tr>"
   f"<tr><td>numeric rule vs rater 2</td><td>{k['rule_r2_a']:.0%}</td><td>{k['rule_r2_k']:.2f}</td></tr></table>",
   "<p>Each has a known weakness. The rule takes a median across statistics that mean different "
   "things within one paper, so a negative predictive value — usually high because most findings "
   "are negative — can pull a study upward. The model raters weigh which figure matters but "
   "reproduce only moderately. All three appear on each study page; disagreement is displayed, not "
   "resolved, and reliably marks a paper whose evidence is genuinely mixed.</p>"]),

 ("Which figures count as a study's evidence?",
  [f"<p>Only figures the study produced itself, or produced by pooling others' published data. "
   f"Papers frequently quote numbers from earlier work while setting up a problem — "
   f"<strong>{k['pct_cited']:.0f}%</strong> of all extracted figures are quoted from another "
   "study. Those do not count toward the quoting paper's verdict or toward any row of the main "
   "table, because the conditions that produced them belong to the original work and counting "
   "them twice would inflate the corpus.</p>",
   "<p>They remain visible on each study page under “figures this paper quotes from other work”, "
   "credited where the source is named.</p>"]),

 ("How is a figure assigned to a model organism?",
  ["<p>A figure naming its own species is assigned to that species. A figure with no species is "
   "assigned only when the study examines exactly one organism, so the attribution is "
   "unambiguous.</p>",
   "<p>This matters for reviews spanning many species: a general statement about animal research "
   "in a paper that mentions rodents, dogs and primates is evidence about none of them "
   "specifically, and is not shown as evidence about any.</p>"]),

 ("Can I compare organisms against each other using this table?",
  ["<p><strong>Not across assessments.</strong> Dog evidence here is mostly regulatory toxicology, "
   "which reports predictive values and sensitivity. Mouse evidence is mostly disease biology and "
   "efficacy, which report correlations and translation rates. Efficacy translation fails often in "
   "every species; toxicology prediction succeeds more often. Comparing dog rows with mouse rows "
   "without holding the assessment fixed largely measures the assessment.</p>",
   "<p>Comparisons within one assessment are meaningful.</p>"]),

 ("A row shows a wide range, such as 31–85%. What does that mean?",
  ["<p>It is the span of several sub-analyses, not an uncertainty interval, and the midpoint is not "
   "an estimate. Each row states what varies across the range.</p>",
   "<p>One case matters. In Daluwatumulle et al. 2026 the dog cancer scores run 31–85%, but the "
   "bottom is a <strong>negative control</strong>: leukaemia (40%) and adrenocortical carcinoma "
   "(31%) were deliberately included as cancers expected to be poor dog models, to check the metric "
   "flags them. It does. Real cancer types score 62–85%, led by bladder cancer at 85%.</p>"]),

 ("Does this show that companion-animal (dog) models translate worse than mouse models?",
  ["<p>No, and the data cannot support that comparison in either direction. No study here "
   "benchmarks dog against mouse on the same endpoint, and the two are assessed on different "
   "things.</p>",
   "<p>What the corpus does show is a gap: a targeted search for veterinary-patient studies "
   "returned 174 records, of which one met the inclusion rule. The comparative-oncology literature "
   "argues that naturally occurring disease in companion animals is a good model far more often "
   "than it measures whether it predicts human outcomes.</p>",
   "<p>The clearest negative result for companion animals here is specific: Petersen-Jones et al. "
   "2015 found dog RPE65 gene therapy did not track human outcomes — dogs recovered near-normal "
   "vision and electroretinogram responses, while patients showed no ERG change and remained "
   "visually impaired.</p>"]),

 ("What counts as a study here?",
  ["<p>It must report a quantitative comparison with a live non-human animal on one side and a "
   "human clinical result on the other. Papers that argue animals do or do not predict human "
   "outcomes without measuring it are excluded, including several well-cited reviews.</p>",
   "<p>Also excluded: predictors that are not whole animals (cell lines, organoids, organ-on-chip, "
   "isolated ion-channel assays, QSAR and PBPK models), and comparisons within one species. "
   "Patient-derived xenografts are reported separately, since they grow a patient's own tumour in "
   "a mouse host and so test whether a patient's tumour predicts that patient.</p>"]),

 ("Is this a systematic review?",
  [f"<p>No. It is a structured reading of {k['n_studies']} studies selected from a screened pool by "
   "a score combining citations and recency — weighted toward authoritative and recent work, and "
   "not a random sample. Verdict counts describe this corpus and nothing wider.</p>"]),

 ("Has any of this been checked by a person?",
  ["<p>Not systematically. Screening, classification and extraction are model-assisted. Every figure "
   "carries the sentence it came from and the table or figure it appeared in, so any number can be "
   "checked against its source, but only a small fraction have been. Spot-checks have found real "
   "defects, each recorded in the limitations file.</p>",
   "<p>Treat this as a structured index into the literature that makes checking cheap, not as a "
   "verified dataset.</p>"]),
]
