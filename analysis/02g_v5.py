"""v5: single diagnosed fix to v4. s3 was 123,391 records because concordan*[tiab]
(108,835 alone) is dominated by genetic/twin concordance and diagnostic-test
concordance -- the wrong sense. Require it to co-occur with a strong animal-model
term rather than the permissive B1 block."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, queries
H = "(" + queries.B3_HUMAN.replace("\n", " ") + ")"
STRONG_ANIMAL = ('("Disease Models, Animal"[Mesh] OR "Models, Animal"[Mesh] OR "Animal Experimentation"[Mesh] '
                 'OR "animal model"[tiab] OR "animal models"[tiab] OR "animal study"[tiab] '
                 'OR "animal studies"[tiab] OR "animal experiment"[tiab] OR "animal experiments"[tiab] '
                 'OR "animal data"[tiab] OR "animal testing"[tiab] OR preclinical[tiab] '
                 'OR "pre-clinical"[tiab] OR nonclinical[tiab])')
v4 = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "scoping_run_v4.json")))
s3_old = v4["strands"]["s3_concordance"]
s3_new = ('((concordan*[tiab] OR discordan*[tiab] OR "predictive validity"[tiab] OR predictivity[tiab] '
          'OR translatability[tiab] OR "external validity"[tiab]) AND ' + STRONG_ANIMAL + ' AND ' + H + ')'
          + queries.DATE)
strands = dict(v4["strands"]); strands["s3_concordance"] = s3_new
union_new = "(" + " OR ".join("(" + v + ")" for v in strands.values()) + ")"
print(f"s3 old: {pubmed.esearch(s3_old)[0]:,}")
print(f"s3 new: {pubmed.esearch(s3_new)[0]:,}")
n = pubmed.esearch(union_new)[0]
print(f"v5 union: {n:,}   (v4 was {v4['union_size']:,})")
ANCH = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "scoping_run.json")))["anchors"]
hit, miss = [], []
for a in ANCH:
    if not a["recall_test"]: continue
    (hit if pubmed.esearch(f"({union_new}) AND {a['pmid']}[uid]")[0] else miss).append(a["key"])
print(f"v5 recall: {len(hit)}/{len(hit)+len(miss)} = {len(hit)/(len(hit)+len(miss)):.1%}")
print("missed:", miss)
json.dump({"strands": strands, "union": union_new, "union_size": n,
           "recall": len(hit)/(len(hit)+len(miss)), "missed": miss},
          open(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "scoping_run_v5.json"), "w"), indent=1)
