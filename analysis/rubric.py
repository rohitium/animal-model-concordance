"""Screening rubric and output schema. Single source of truth for 06 and 08.
Any change here invalidates prior screening decisions; bump RUBRIC_VERSION."""

RUBRIC_VERSION = "2026-08-21.r3"

RUBRIC = """You are screening titles/abstracts for a systematic review.

INCLUDE only if the record reports a QUANTITATIVE measure of agreement between
non-human animal results and human clinical results - e.g. a concordance rate,
translation/success rate, positive predictive value, sensitivity/specificity of
animal models, or a systematic comparison of animal vs human effect sizes -
across one or more intervention-indication pairs. Regulatory-dataset analyses
and veterinary comparative-oncology concordance analyses count.

THE INDEX TEST MUST BE A WHOLE, LIVE NON-HUMAN ANIMAL (in vivo). This review is
about ANIMAL model concordance. EXCLUDE any study whose predictor of human outcome
is only a non-animal method:
- in vitro assays: cell lines, primary cells, organoids, organ-on-chip / microphysiological
  systems, isolated ion-channel or hERG assays, microtissues, 3D cultures
- in silico / computational: QSAR, PBPK or other pharmacokinetic modelling, AI/ML
  predictors, mathematical or statistical models, structure-activity relationships
- "new approach methodologies" (NAMs) and other explicitly non-animal test batteries
Note: isolated tissue or organ preparations taken from an animal are still in vitro.

If a study evaluates BOTH whole-animal in vivo results AND non-animal methods against
human outcomes, INCLUDE it — the animal arm is what we need. If the animal appears only
as a source of cells or tissue, EXCLUDE.

EXCLUDE:
- primary animal or human research reporting only its own results
- individual clinical trial reports
- methods/tools/guidelines/reporting checklists
- opinion, editorial, commentary or narrative essay with NO original data and no
  systematic re-analysis
- in vitro / in silico only comparisons
- records with no extractable numerator and denominator

Being an influential paper ABOUT the translation problem is NOT sufficient. The
record must itself report an agreement statistic. A review that only argues that
animal models translate poorly, without measuring it, is EXCLUDE.

When uncertain, INCLUDE (screening favours sensitivity over precision).

Answer with JSON only."""
SCHEMA = {"type":"object","additionalProperties":False,
 "properties":{"decision":{"type":"string","enum":["include","exclude"]},
  "confidence":{"type":"number"},"reason":{"type":"string"}},
 "required":["decision","confidence","reason"]}

