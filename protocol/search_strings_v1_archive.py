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
 OR marmoset*[tiab] OR baboon*[tiab] OR chimpanzee*[tiab] OR zebrafish[tiab])"""

B2_CONCORD = """(concordan*[tiab] OR discordan*[tiab] OR predictiv*[tiab] OR predict[tiab]
 OR predicting[tiab] OR prediction[tiab] OR translat*[tiab] OR "bench to bedside"[tiab]
 OR extrapolat*[tiab] OR replicat*[tiab] OR reproducib*[tiab] OR agreement[tiab]
 OR "cross-species"[tiab] OR interspecies[tiab] OR "species differences"[tiab]
 OR "species difference"[tiab] OR correlat*[tiab])"""

B3_HUMAN = """("Clinical Trials as Topic"[Mesh] OR "randomized controlled trial"[pt]
 OR "clinical trial"[tiab] OR "clinical trials"[tiab] OR human[tiab] OR humans[tiab]
 OR "phase II"[tiab] OR "phase III"[tiab] OR "first-in-human"[tiab] OR patient[tiab]
 OR patients[tiab] OR clinical[tiab])"""

B4_META = """("systematic review"[tiab] OR "systematic review"[pt] OR meta-analy*[tiab]
 OR "meta analysis"[pt] OR "cross-sectional"[tiab] OR "retrospective analysis"[tiab]
 OR "success rate"[tiab] OR "success rates"[tiab] OR attrition[tiab]
 OR "failure rate"[tiab] OR "failure rates"[tiab] OR "predictive value"[tiab]
 OR sensitivity[tiab] OR specificity[tiab] OR "scoping review"[tiab] OR review[pt])"""

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

DATE = ' AND ("1980"[dp] : "3000"[dp])'
def j(*b): return " AND ".join("(" + x.replace("\n", " ") + ")" for x in b)

QUERIES = {
 "arm1_efficacy":  j(B1_ANIMAL, B2_CONCORD, B3_HUMAN, B4_META) + DATE,
 "arm2_safety":    j(B1_ANIMAL, B3_HUMAN, B5_ARM2, "(" + B2_CONCORD + " OR " + B4_META + ")") + DATE,
 "arm3_tox":       j(B1_ANIMAL, B3_HUMAN, B5_ARM3, "(" + B2_CONCORD + " OR " + B4_META + ")") + DATE,
 "arm4_vet":       j(B6_VET, B3_HUMAN, "(" + B2_CONCORD + " OR " + B4_META + ")", B1_ANIMAL) + DATE,
}

