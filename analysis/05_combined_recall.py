"""Measure coverage of the full retrieval design: query union (v5 + auxiliary
families) OR one-generation citation neighbourhood. Reports each mechanism's
contribution separately and the union, rather than asserting it across logs."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, queries
ROOT = os.path.join(os.path.dirname(__file__), "..")
v5 = json.load(open(os.path.join(ROOT, "data", "raw", "scoping_run_v5.json")))
AUX = {"aux_bias": queries.AUX_BIAS.replace("\n"," ") + queries.DATE,
       "aux_attrition": queries.AUX_ATTRITION.replace("\n"," ") + queries.DATE}
QUERY_UNION = "((" + v5["union"] + ") OR (" + ") OR (".join(AUX.values()) + "))"

ANCH = {a["key"]: a["pmid"] for a in
        json.load(open(os.path.join(ROOT, "data", "raw", "scoping_run.json")))["anchors"]
        if a["recall_test"]}
pm = list(ANCH.values())
fwd = pubmed.elink(pm, "pubmed_pubmed_citedin")
bwd = pubmed.elink(pm, "pubmed_pubmed_refs")
reach = {}
for src in pm:
    for t in fwd.get(src, []) + bwd.get(src, []):
        reach.setdefault(t, set()).add(src)

rows = []
for k, p in ANCH.items():
    q = bool(pubmed.esearch(f"({QUERY_UNION}) AND {p}[uid]")[0])
    c = len(reach.get(p, set()) - {p}) > 0
    rows.append((k, p, q, c))

nq = sum(r[2] for r in rows); nc = sum(r[3] for r in rows)
nb = sum(r[2] or r[3] for r in rows); n = len(rows)
print(f"{'anchor':22s} {'query':>6s} {'cite':>6s}")
for k, p, q, c in rows:
    print(f"{k:22s} {'OK' if q else '-':>6s} {'OK' if c else '-':>6s}")
print(f"\nQuery union alone     : {nq}/{n} = {nq/n:.1%}")
print(f"Citation alone        : {nc}/{n} = {nc/n:.1%}")
print(f"UNION of mechanisms   : {nb}/{n} = {nb/n:.1%}")
print("Missed by both        :", [r[0] for r in rows if not (r[2] or r[3])] or "none")
print(f"\nQuery-union pool size : {pubmed.esearch(QUERY_UNION)[0]:,}")
json.dump({"query_only": nq/n, "citation_only": nc/n, "combined": nb/n,
           "rows": [{"key":k,"pmid":p,"query":q,"citation":c} for k,p,q,c in rows]},
          open(os.path.join(ROOT, "data", "raw", "combined_recall.json"), "w"), indent=1)
