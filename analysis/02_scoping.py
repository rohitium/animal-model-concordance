"""Phase 1: operationalize the PLAN.md §5.2 query blocks, record hit counts,
and test recall against the resolved anchor set."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pubmed
from queries import *
ROOT = os.path.join(os.path.dirname(__file__), "..")

# Anchors. Each is assigned to the query family expected to retrieve it.
# recall_test=False for records that our own eligibility criteria (PLAN 6.3) would
# exclude at screening anyway -- opinion pieces with no original data, method/tool
# papers, and individual trial reports. Holding the search to a standard the protocol
# does not require would inflate apparent sensitivity.
ANCHORS = [
 ("hackam2006","17032985","efficacy",True),   ("perel2007","17175568","efficacy",True),
 ("contopoulos2008","18772421","efficacy",True),("vanderworp2010","20361020","efficacy",True),
 ("pound2018","30404629","efficacy",True),    ("leenaars2019","31307492","efficacy",True),
 ("bracken2009","19297654","efficacy",True),  ("wall2008","17988725","efficacy",True),
 ("mak2014","24489990","efficacy",True),      ("macleod2010","21097827","context-editorial",False),
 ("howells2010","20485296","efficacy",True),  ("marshall2023","36883244","efficacy",True),
 ("sena2010","20361022","bias",True),         ("begley2012","22460880","bias",True),
 ("prinz2011","21892149","bias",True),        ("freedman2015","25670378","bias",True),
 ("olson2000","11029269","tox",True),         ("monticello2017","28893587","tox",True),
 ("clark2018","29730448","tox",True),         ("bailey2015","26753942","tox",True),
 ("redfern2003","12667944","tox",True),
 ("hay2014","24406927","attrition",True),     ("wong2019","29394327","attrition",True),
 ("cummings2014","25024750","attrition",True),
 ("seok2013","23401516","contested",True),    ("takao2015","25092317","contested",True),
 ("perrin2014","24678540","contested",True),
 ("paoloni_khanna2008","18202698","vet",True),("kol2015","26446953","vet",True),
 ("fan_khanna2015","29061942","vet",True),
 ("lees2006_saint1","16467546","context",False),("shuaib2007_saint2","17687131","context",False),
 ("nguyen2015_recistvet","23534501","context",False),("vcog_ctcae_v2","33427378","context",False),
 ("arrive2020","34095516","context",False),
]

QUERIES = QUERIES_V3 if os.environ.get("QV")=="3" else QUERIES
VER = os.environ.get("QV","2")
print(f"=== HIT COUNTS (queries v{VER}) ===")
counts = {}
for k, q in QUERIES.items():
    n, _, _ = pubmed.esearch(q)
    counts[k] = n
    print(f"  {k:16s} {n:>8,}")
n_any, _, _ = pubmed.esearch("(" + ") OR (".join(QUERIES.values()) + ")")
counts["union_all_arms"] = n_any
print(f"  {'UNION':16s} {n_any:>8,}")

print("\n=== ANCHOR RECALL ===")
res = []
for key, pmid, cat, test in ANCHORS:
    hits = {}
    for qk, q in QUERIES.items():
        n, _, _ = pubmed.esearch(f"({q}) AND {pmid}[uid]")
        hits[qk] = bool(n)
    any_hit = any(hits.values())
    res.append({"key": key, "pmid": pmid, "category": cat, "recall_test": test,
                "retrieved_by": [k for k, v in hits.items() if v], "retrieved": any_hit})
    mark = "OK " if any_hit else "MISS"
    if not test: mark = "ok*" if any_hit else "  -"
    print(f"  {mark} {key:22s} {pmid:9s} {cat:9s} {','.join(k for k,v in hits.items() if v) or '(none)'}")

tested = [r for r in res if r["recall_test"]]
got = [r for r in tested if r["retrieved"]]
recall = len(got) / len(tested)
print(f"\nRecall on {len(tested)} testable anchors: {len(got)}/{len(tested)} = {recall:.1%}  (gate: >=90%)")
print("Missed:", [r["key"] for r in tested if not r["retrieved"]] or "none")

json.dump({"run_date": "2026-08-20", "query_version": VER, "queries": QUERIES, "counts": counts,
           "anchors": res, "recall": recall},
          open(os.path.join(ROOT, "data", "raw", f"scoping_run_v{VER}.json"), "w"), indent=1)
