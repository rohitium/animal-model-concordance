"""Operationalized search blocks from PLAN.md 5.2. Single source of truth.
Any edit here must be mirrored into protocol/search_strings.md with a new run date."""
B1_ANIMAL = """("Models, Animal"[Mesh] OR "Disease Models, Animal"[Mesh] OR "animal model"[tiab]
 OR "animal models"[tiab] OR "animal experiment"[tiab] OR "animal experiments"[tiab]
 OR "animal studies"[tiab] OR "animal study"[tiab] OR "animal research"[tiab]
 OR "animal data"[tiab] OR "animal test"[tiab] OR "animal tests"[tiab] OR "animal testing"[tiab]
 OR preclinical[tiab] OR "pre-clinical"[tiab] OR nonclinical[tiab] OR "non-clinical"[tiab]
 OR mouse[tiab] OR mice[tiab] OR murine[tiab] OR rat[tiab] OR rats[tiab] OR rodent*[tiab]
 OR canine[tiab] OR dog[tiab] OR dogs[tiab] OR feline[tiab] OR cat[tiab] OR cats[tiab]
 OR porcine[tiab] OR pig[tiab] OR pigs[tiab] OR swine[tiab] OR minipig*[tiab]
 OR equine[tiab] OR horse[tiab] OR horses[tiab] OR bovine[tiab] OR cattle[tiab]
 OR ovine[tiab] OR sheep[tiab] OR caprine[tiab] OR goat[tiab] OR goats[tiab]
 OR chicken*[tiab] OR hen[tiab] OR hens[tiab] OR avian[tiab] OR rabbit*[tiab]
 OR ferret*[tiab] OR "guinea pig"[tiab] OR "guinea pigs"[tiab]
 OR primate*[tiab] OR macaque*[tiab] OR rhesus[tiab] OR cynomolgus[tiab]
 OR marmoset*[tiab] OR baboon*[tiab] OR chimpanzee*[tiab] OR zebrafish[tiab]
 OR "Animals"[Mesh] OR "Animal Experimentation"[Mesh] OR "Drug Evaluation, Preclinical"[Mesh]
 OR "Toxicity Tests"[Mesh] OR "Species Specificity"[Mesh])"""

B2_CONCORD = """(concordan*[tiab] OR discordan*[tiab] OR predict*[tiab] OR translat*[tiab] OR "bench to bedside"[tiab]
 OR extrapolat*[tiab] OR replicat*[tiab] OR reproducib*[tiab] OR agreement[tiab]
 OR "cross-species"[tiab] OR interspecies[tiab] OR "species differences"[tiab]
 OR "species difference"[tiab] OR correlat*[tiab]
 OR "Translational Research, Biomedical"[Mesh] OR "Reproducibility of Results"[Mesh]
 OR "Predictive Value of Tests"[Mesh] OR "Treatment Failure"[Mesh] OR "Publication Bias"[Mesh])"""

B3_HUMAN = """("Clinical Trials as Topic"[Mesh] OR "randomized controlled trial"[pt]
 OR "clinical trial"[tiab] OR "clinical trials"[tiab] OR human[tiab] OR humans[tiab]
 OR "phase II"[tiab] OR "phase III"[tiab] OR "first-in-human"[tiab] OR patient[tiab]
 OR patients[tiab] OR clinical[tiab] OR "Humans"[Mesh])"""

B4_META = """("systematic review"[tiab] OR "systematic review"[pt] OR meta-analy*[tiab]
 OR "meta analysis"[pt] OR "cross-sectional"[tiab] OR "retrospective analysis"[tiab]
 OR "success rate"[tiab] OR "success rates"[tiab] OR attrition[tiab]
 OR "failure rate"[tiab] OR "failure rates"[tiab] OR "predictive value"[tiab]
 OR sensitivity[tiab] OR specificity[tiab] OR "scoping review"[tiab] OR review[pt]
 OR "Biomedical Research"[Mesh] OR "Research Design"[Mesh] OR "Evaluation Studies"[pt])"""

B5_ARM2 = """("safety pharmacology"[tiab] OR "ICH S7"[tiab] OR hERG[tiab] OR "QT interval"[tiab]
 OR "QT prolongation"[tiab] OR torsade*[tiab] OR "adverse event"[tiab] OR "adverse events"[tiab]
 OR "adverse drug reaction*"[tiab] OR "drug withdrawal"[tiab] OR "market withdrawal"[tiab]
 OR "black box warning"[tiab] OR "boxed warning"[tiab])"""

B5_ARM3 = """(toxicolog*[tiab] OR toxicity[tiab] OR "repeat-dose"[tiab] OR "repeat dose"[tiab]
 OR carcinogenic*[tiab] OR genotoxic*[tiab] OR teratogen*[tiab] OR hepatotoxic*[tiab]
 OR nephrotoxic*[tiab] OR "target organ toxicity"[tiab] OR "no observed adverse effect"[tiab]
 OR "drug-induced liver injury"[tiab] OR "safety assessment"[tiab])"""

B6_VET = """("comparative oncology"[tiab] OR "naturally occurring"[tiab] OR "naturally-occurring"[tiab]
 OR spontaneous[tiab] OR "companion animal"[tiab] OR "companion animals"[tiab]
 OR "client-owned"[tiab] OR "client owned"[tiab] OR "veterinary clinical trial"[tiab]
 OR "veterinary clinical trials"[tiab] OR "pet dog"[tiab] OR "pet dogs"[tiab]
 OR "pet cat"[tiab] OR "pet cats"[tiab] OR "One Health"[tiab] OR "veterinary patients"[tiab])"""

AUX_BIAS = """(("Publication Bias"[Mesh] OR "Reproducibility of Results"[Mesh]
 OR "publication bias"[tiab] OR reproducib*[tiab] OR replicat*[tiab] OR irreproducib*[tiab]
 OR "research waste"[tiab] OR "questionable research practices"[tiab] OR "risk of bias"[tiab])
 AND (preclinical[tiab] OR "pre-clinical"[tiab] OR nonclinical[tiab] OR animal*[tiab]
 OR laborator*[tiab] OR "Drug Evaluation, Preclinical"[Mesh] OR "Animal Experimentation"[Mesh]
 OR "Disease Models, Animal"[Mesh] OR "Biomedical Research"[Mesh] OR "Drug Industry"[Mesh]))"""

AUX_ATTRITION = """(("success rate"[tiab] OR "success rates"[tiab] OR attrition[tiab]
 OR "failure rate"[tiab] OR "failure rates"[tiab] OR pipeline[tiab] OR "probability of success"[tiab]
 OR "approval rate"[tiab] OR "approval rates"[tiab] OR "clinical development"[tiab]
 OR "drug development"[tiab] OR "development success"[tiab])
 AND ("Drug Development"[Mesh] OR "Drug Discovery"[Mesh] OR "Drug Industry"[Mesh]
 OR "Clinical Trials as Topic"[Mesh] OR "Drug Approval"[Mesh] OR investigational[tiab]
 OR "new drug"[tiab] OR "phase II"[tiab] OR "phase III"[tiab] OR "clinical trial"[tiab]
 OR "clinical trials"[tiab]))"""

DATE = ' AND ("1980"[dp] : "3000"[dp])'
def j(*b): return " AND ".join("(" + x.replace("\n", " ") + ")" for x in b)

QUERIES = {
 "arm1_efficacy":  j(B1_ANIMAL, B2_CONCORD, B3_HUMAN, B4_META) + DATE,
 "arm2_safety":    j(B1_ANIMAL, B3_HUMAN, B5_ARM2, "(" + B2_CONCORD + " OR " + B4_META + ")") + DATE,
 "arm3_tox":       j(B1_ANIMAL, B3_HUMAN, B5_ARM3, "(" + B2_CONCORD + " OR " + B4_META + ")") + DATE,
 "arm4_vet":       j(B6_VET, B3_HUMAN, "(" + B2_CONCORD + " OR " + B4_META + ")", B1_ANIMAL) + DATE,
 "aux_bias":       AUX_BIAS.replace("\n", " ") + DATE,
 "aux_attrition":  AUX_ATTRITION.replace("\n", " ") + DATE,
}



# ---------------------------------------------------------------------------
# v3. v2 passed the recall gate (93.1%) but returned 1.67M records: the
# "Animals"[Mesh] / "Humans"[Mesh] rescue terms made blocks 1-3 near-universal.
# v3 keeps the MeSH rescue but requires it to CO-OCCUR with a translation
# concept, and adds a high-specificity phrase core. Recall is re-tested, not
# assumed: any precision gain that costs anchors is rejected.
# ---------------------------------------------------------------------------

CORE_PHRASE = """("animal to human"[tiab] OR "animals to humans"[tiab] OR "animal-to-human"[tiab]
 OR "preclinical to clinical"[tiab] OR "bench to bedside"[tiab] OR "bench-to-bedside"[tiab]
 OR "translational success"[tiab] OR "translational failure"[tiab] OR "translational value"[tiab]
 OR "translatability"[tiab] OR "translational gap"[tiab] OR "failure to translate"[tiab]
 OR concordan*[tiab] OR discordan*[tiab] OR "predictive value"[tiab] OR "predictive validity"[tiab]
 OR "predict human"[tiab] OR "predict humans"[tiab] OR "predict clinical"[tiab]
 OR "predict the clinical"[tiab] OR "predicting human"[tiab] OR "predicting clinical"[tiab]
 OR "poor predictor"[tiab] OR "poor predictors"[tiab] OR "good predictor"[tiab]
 OR "predictivity"[tiab] OR "predictiveness"[tiab]
 OR "cross-species"[tiab] OR interspecies[tiab] OR "species differences"[tiab]
 OR "species difference"[tiab] OR "species specificity"[tiab] OR "species-specific"[tiab]
 OR "extrapolation"[tiab] OR "external validity"[tiab] OR "construct validity"[tiab]
 OR "face validity"[tiab] OR "reverse translation"[tiab] OR "clinical relevance of animal"[tiab]
 OR "how well do animal"[tiab] OR "do animal models"[tiab])"""

MESH_TRANSLATION = """("Translational Research, Biomedical"[Mesh] OR "Drug Evaluation, Preclinical"[Mesh]
 OR "Predictive Value of Tests"[Mesh] OR "Species Specificity"[Mesh] OR "Treatment Failure"[Mesh])"""

MESH_ANIMAL_MODEL = """("Disease Models, Animal"[Mesh] OR "Models, Animal"[Mesh]
 OR "Animal Experimentation"[Mesh] OR "Animal Testing Alternatives"[Mesh] OR "Toxicity Tests"[Mesh])"""

def _f(x): return "(" + x.replace("\n", " ") + ")"

# Two routes into each arm, unioned: a phrase core, and a MeSH route that still
# demands an explicit translation concept.
_ROUTE_CORE = _f(CORE_PHRASE) + " AND " + _f(B1_ANIMAL) + " AND " + _f(B3_HUMAN)
_ROUTE_MESH = _f(MESH_TRANSLATION) + " AND " + _f(MESH_ANIMAL_MODEL) + " AND " + _f(B3_HUMAN) \
              + " AND " + _f("""predict*[tiab] OR concordan*[tiab] OR translat*[tiab]
 OR reproducib*[tiab] OR replicat*[tiab] OR extrapolat*[tiab] OR "Reproducibility of Results"[Mesh]""")
_BASE_V3 = "((" + _ROUTE_CORE + ") OR (" + _ROUTE_MESH + "))"

QUERIES_V3 = {
 "arm1_efficacy": _BASE_V3 + DATE,
 "arm2_safety":   _BASE_V3 + " AND " + _f(B5_ARM2) + DATE,
 "arm3_tox":      _BASE_V3 + " AND " + _f(B5_ARM3) + DATE,
 "arm4_vet":      _f(B6_VET) + " AND " + _f(B1_ANIMAL) + " AND " + _f(B3_HUMAN) + " AND "
                  + _f(CORE_PHRASE + " OR " + MESH_TRANSLATION) + DATE,
 "aux_bias":      AUX_BIAS.replace("\n", " ") + DATE,
 "aux_attrition": AUX_ATTRITION.replace("\n", " ") + DATE,
}
