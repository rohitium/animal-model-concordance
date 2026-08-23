"""FAQ content, kept as data so the numbers stay bound to the database."""
def build(k):
    return [
 ("How is the concordance verdict decided? Is there a numeric threshold?",
  ["<p>Yes. Every figure carrying concordance information is put on a 0–1 scale where 1 means "
   "the animal result tracked the human result. Figures pointing the other way are inverted, so a "
   "92% failure rate becomes 0.08; correlations use |r| or R². A study's score is the median of "
   "its figures, with cut-offs at <strong>≥0.70 supports</strong>, "
   "<strong>0.40–0.70 partly supports</strong>, <strong>&lt;0.40 does not support</strong>.</p>",
   f"<p>The score covers agreement and concordance rates, discordance rates (inverted), "
   f"correlations, and differences between quantities that are themselves on a 0–1 scale. "
   f"It applies to <strong>{k['n_scored']} of {k['n_studies']}</strong> studies. Moving the "
   f"cut-offs to 0.65/0.35 shifts a few studies from partly-supports to supports and leaves "
   f"does-not-support unchanged, so the negative end of the scale is the more stable one.</p>",
   "<p><strong>A worked example.</strong> Daluwatumulle et al. 2026 computed a model-robustness "
   "score for dog models of each human cancer type — a composite of how closely the dog tumour "
   "transcriptome matches its human counterpart. That distribution is the concordance measure, so "
   "the score is simply its median. The 20 reported values run from 31.10% (adult adrenocortical "
   "carcinoma) to 85.05% (adult bladder cancer), with a median of 61.7%, placing the study in "
   "<em>partly supports</em>. Nothing is removed from the distribution: the authors included some "
   "cancers they expected to score low in order to check the metric behaves, and those belong in "
   "it. Ancillary statistics from the same paper — the mean gap between within-species and "
   "cross-species correlations, for instance — are steps in the analysis rather than measures of "
   "match, and do not enter the score.</p>"]),

 ("Why aren't odds ratios, fold-changes and p-values included in the score?",
  ["<p>Odds ratios, likelihood ratios, fold-changes and slopes <em>can</em> be put on the same "
   "0–1 scale — an odds ratio by x/(1+x), so no association maps to 0.50; a fold-change by "
   "1/max(x, 1/x), so a two-fold difference maps to 0.50. Those conversions are applied and shown "
   "on each study page.</p>",
   "<p>They are kept out of the score because pooling them makes it less meaningful rather than "
   "more. A 0.5 meaning “a two-fold difference” is not the same claim as a 0.5 meaning “agreed "
   "half the time”. Measured against independent readers, adding them moves the rule from modest "
   "agreement to chance, while buying only three extra studies.</p>",
   "<p>Two kinds genuinely cannot be converted. p-values and false discovery rates measure "
   "evidence against a null hypothesis, not how closely two things agree — a very small p is "
   "compatible with a trivial difference or an enormous one. Mahalanobis distances and slope "
   "differences reported in unstated units are monotone in agreement but have no common scale, so "
   "they rank species within one study and cannot be compared across studies.</p>"]),

 ("Why do some studies have no numeric verdict?",
  [f"<p><strong>{k['n_unscored']} of {k['n_studies']}</strong> studies report nothing that enters "
   "the score. Their figures are p-values, regression slopes, Mahalanobis distances, and ratio-type "
   "measures that are convertible but not poolable (see above). Real results, but not rates of "
   "agreement.</p>",
   "<p>That roughly half the field does not express animal-to-human correspondence as a rate of "
   "agreement is a large part of why concordance figures rarely compare across papers.</p>"]),

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
   f"<strong>{k['cited']}</strong> of {k['n_figures']} extracted figures "
   f"({k['pct_cited']:.0f}%) are quoted from another "
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
  ["<p>It is the span of a distribution, not an uncertainty interval. Where a paper scores many "
   "conditions — one value per cancer type, per organ system, per compound — the row shows the "
   "span and the summary gives the median. Each row states what varies across it.</p>",
   "<p>In Daluwatumulle et al. 2026, the 31–85% span is 20 dog cancer models scored against their "
   "human counterparts: 31.10% for adult adrenocortical carcinoma at one end, 85.05% for adult "
   "bladder cancer at the other, median 61.7%. The spread is the finding — dogs model some human "
   "cancers closely and others poorly — not noise around a central value.</p>"]),

 ("Can dog models be compared with mouse models here?",
  ["<p>Within a single study that measured both, yes. Several toxicology studies report the "
   "same statistic per species. Atkins et al. 2020 gives a median positive predictive value of "
   "0.38 for dog, 0.43 for mouse, 0.41 for rat and 0.60 for non-human primate, with negative "
   "predictive values of 0.71, 0.81, 0.72 and 0.73. Bailey et al. 2015 and the IQ consortium "
   "database (Monticello et al. 2017) report comparable per-species breakdowns. In total "
   "<strong>18 of the studies here report one statistic for more than one organism</strong>, and "
   "those are legitimate comparisons: same design, same endpoint, same cohort of compounds.</p>",
   "<p>What is not legitimate is reading the organism rows of the main table against each other. "
   "Dog evidence in this corpus comes mostly from regulatory toxicology and mouse evidence mostly "
   "from disease biology and efficacy. Efficacy translation fails often in every species and "
   "toxicology prediction succeeds more often, so a cross-row comparison largely measures which "
   "assessment each organism happens to have been studied under.</p>",
   "<p>Where studies do compare species directly, no organism stands out as clearly better: the "
   "predictive values above sit within a narrow band, and the study reporting them concludes that "
   "pre-clinical models in general predict human toxicity poorly.</p>"]),

 ("What counts as a study here?",
  ["<p>It must report a quantitative comparison with a live non-human animal on one side and a "
   "human clinical result on the other. Papers that argue animals do or do not predict human "
   "outcomes without measuring it are excluded, including several well-cited reviews.</p>",
   "<p>Also excluded: predictors that are not whole animals (cell lines, organoids, organ-on-chip, "
   "isolated ion-channel assays, QSAR and PBPK models), and comparisons within one species. "
   "Patient-derived xenografts are reported separately, since they grow a patient's own tumour in "
   "a mouse host and so test whether a patient's tumour predicts that patient.</p>"]),

 ("Is this a systematic review?",
  [f"<p>No. It is a structured reading of {k['n_studies']} studies — {k['in_rows']} of which "
   f"contribute organism-specific evidence — selected from a screened pool by "
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
