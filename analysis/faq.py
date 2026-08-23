"""FAQ content. Kept as data so numbers stay bound to the database rather than
being retyped into prose that then drifts."""
def build(ctx):
    k=ctx
    return [
 ("How were the supports / partly supports / does not support verdicts decided? What were the thresholds?",
  ["<p><strong>There are no numeric thresholds.</strong> The verdicts are judgements about "
   "each study's data, applied against a fixed rubric, not the output of a cut-off.</p>",
   "<p>A cut-off is not possible here because the underlying statistics are not commensurable. "
   "Olson 2000 reports 63% concordance of human toxicities in non-rodents; Seok 2013 reports a "
   "Pearson R&sup2; of 0.09 between mouse and human gene expression; Marshall 2023 reports that "
   "over 92% of drugs fail to translate. No single number can separate these, because a high "
   "value means success in the first two and failure in the third. Any numeric rule would have "
   "to be written per statistic, and most statistics appear in only one or two studies &mdash; "
   "the threshold would be fitted to the study it judged.</p>",
   "<p>What is applied instead: each paper is read from its full-text PDF and judged on whether "
   "the animal results corresponded to the human results (<em>supports</em>), corresponded for "
   "some species, endpoints or conditions but not others (<em>partly supports</em>), or did not "
   "correspond (<em>does not support</em>). Three rules bind the judgement: read results, tables "
   "and figures rather than how the authors characterise their own work; cite the specific "
   "numbers, with no adjectives; and exclude negative controls, which are designed to score low.</p>"]),

 ("How reliable are the verdicts?",
  [f"<p>Moderately. Every study was independently re-judged by a second rater &mdash; a different "
   f"model family, the same PDFs, the same rubric. The two agree on "
   f"<strong>{k['agree']:.0%}</strong> of {k['n_pairs']} studies, Cohen&rsquo;s "
   f"&kappa; = <strong>{k['kappa']:.2f}</strong>.</p>",
   "<p>Almost every disagreement is one step (partly supports &harr; supports, or does not "
   "support &harr; partly supports); the second rater is systematically more generous. "
   "Read a verdict as indicative, and the numbers beneath it as the evidence. Where the raters "
   "disagree, the study page says so &mdash; a disagreement usually means the evidence is "
   "genuinely mixed, not that one rater erred.</p>"]),

 ("Can I compare organisms against each other using this table?",
  ["<p><strong>Not across assessments, and that is the most common way to misread this table.</strong></p>",
   "<p>Dog evidence in this corpus comes mostly from regulatory toxicology, where studies report "
   "predictive values, sensitivity and specificity. Mouse evidence comes mostly from disease "
   "biology and efficacy, where studies report correlations, survival differences and translation "
   "rates. Efficacy translation fails often in every species; toxicology prediction succeeds more "
   "often. So comparing the dog rows with the mouse rows without holding the assessment fixed "
   "largely measures which assessment each organism happens to have been studied under.</p>",
   "<p>Comparisons within a single assessment are meaningful. Comparisons across the whole table "
   "are not.</p>"]),

 ("A row shows a wide range, such as 31&ndash;85%. What does that mean?",
  ["<p>It means several sub-analyses in one or more studies reported different values, and the "
   "row shows the span. It is <em>not</em> an uncertainty interval, and the midpoint is not an "
   "estimate. Each row&rsquo;s summary says what varies across the range.</p>",
   "<p>One case is worth stating plainly. In Daluwatumulle et al. 2026, dog cancer models score "
   "31&ndash;85%, but the bottom of that range is a <strong>negative control</strong>: the authors "
   "deliberately included leukaemia (LAML, 40%) and adrenocortical carcinoma (ACC, 31%) as "
   "cancers expected to be poor dog models, to check the metric flags them as weak. It does. "
   "Reading 31% as dog performance inverts the paper&rsquo;s meaning. The genuine cancer types "
   "score 62&ndash;85%, led by bladder cancer at 85%.</p>"]),

 ("Does this show that companion-animal (dog) models translate worse than mouse models?",
  ["<p>No, and the data cannot support that comparison in either direction.</p>",
   "<p>By raw counts the verdicts are similar &mdash; dog 36% do-not-support, mouse 33%, "
   "rodent 50% &mdash; but as above, the organisms are assessed on different things, so those "
   "figures are not comparable. No study in this corpus benchmarks dog against mouse on the same "
   "endpoint. The Daluwatumulle paper, which is the largest source of dog data here, mentions "
   "mice once, in its introduction, and argues that dogs complement mouse work.</p>",
   "<p>The finding that <em>is</em> supported concerns the evidence base rather than the animals: "
   "only a small minority of dog records come from veterinary clinical studies. The "
   "comparative-oncology literature argues that naturally occurring disease in companion animals "
   "is a good model far more often than it measures whether it predicts human outcomes. "
   "A targeted search for veterinary-patient studies returned 174 records of which one met the "
   "inclusion rule. That is a gap in the published evidence, not a verdict against the model.</p>"]),

 ("What counts as a study here?",
  ["<p>A study is included only if it reports a quantitative comparison in which one side is a "
   "result in a live non-human animal and the other a human clinical result. Papers arguing that "
   "animals do or do not predict human outcomes, without measuring it, are excluded &mdash; "
   "including several well-cited reviews.</p>",
   "<p>Also excluded: predictors that are not whole animals (cell lines, organoids, "
   "organ-on-chip, isolated ion-channel assays, QSAR and PBPK models), and comparisons within a "
   "single species, such as diseased versus healthy animals. Patient-derived xenografts are "
   "reported separately, because they grow the patient&rsquo;s own human tumour in a mouse host "
   "and so answer whether a patient&rsquo;s tumour predicts that patient, not whether another "
   "species predicts humans.</p>"]),

 ("Is this a systematic review?",
  [f"<p>No. It is a structured, citation-anchored reading of {k['n_studies']} studies. They were "
   "selected from a screened candidate pool by a recorded score combining citation count and "
   "recency, deliberately weighted toward authoritative and recent work. That is not a random "
   "sample of the literature.</p>",
   f"<p>So the verdict tally &mdash; {k['supports']} support, {k['partly']} partly support, "
   f"{k['not']} do not &mdash; describes this corpus and nothing wider. It is a count of studies, "
   "not a measure of how well animal models work. The protocol, search strings, PRISMA counts and "
   "a running limitations list are in the repository.</p>"]),

 ("Has any of this been checked by a person?",
  ["<p>Not systematically. Screening, classification and extraction are model-assisted. Every "
   "figure carries the sentence it came from and the table or figure it appeared in, so any "
   "number can be checked against the source, but only a small fraction have been checked so "
   "far. Spot-checks have found real defects, and each is recorded in the limitations file "
   "rather than quietly corrected.</p>",
   "<p>Treat the site as a structured index into the literature that makes checking cheap, not "
   "as a verified dataset.</p>"]),
]
