"""Assemble a ~100-study pilot slice: diverse (arm/species/area), authoritative
(citation count), recent (weighted, but landmarks retained).

Candidates come from three sources so the slice is not an artefact of one:
  1. citation neighbourhood records linked to >=3 verified anchors
  2. per-strand samples (guarantees every arm is represented)
  3. the verified anchors themselves
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(__file__))
import pubmed, queries
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda *p: os.path.join(ROOT, "data", *p)

cite = json.load(open(J("raw", "citation_chase.json")))
v5 = json.load(open(J("raw", "scoping_run_v5.json")))
anchors = [a["pmid"] for a in json.load(open(J("raw", "scoping_run.json")))["anchors"]]

cand = collections.defaultdict(set)
for p in cite["multi_linked"]:
    cand[p].add("citation_hub")
for p in anchors:
    cand[p].add("anchor")

# Per-strand sample, most recent first, so every arm is represented.
for name, q in v5["strands"].items():
    n, ids, _ = pubmed.esearch(q + " AND hasabstract", retmax=120, sort="relevance")
    for p in ids:
        cand[p].add(name)
    print(f"  {name:18s} pool={n:>8,} sampled={len(ids)}")

pmids = list(cand)
print(f"\ncandidates: {len(pmids)}")
summ = pubmed.esummary(pmids)

# Authority proxy: how many PubMed records cite this one.
cited = pubmed.elink(pmids, "pubmed_pubmed_citedin")
recs = {}
for p in pmids:
    s = summ.get(p)
    if not s: continue
    try: yr = int(s.get("year") or 0)
    except ValueError: yr = 0
    recs[p] = {"pmid": p, "title": s["title"], "journal": s["journal"], "year": yr,
               "authors": s.get("authors", []), "sources": sorted(cand[p]),
               "cited_by": len(cited.get(p, []))}
json.dump(recs, open(J("screening", "slice_candidates.json"), "w"), indent=1)
print(f"with metadata: {len(recs)}")
yrs = [r["year"] for r in recs.values() if r["year"]]
print(f"year range {min(yrs)}-{max(yrs)}, median {sorted(yrs)[len(yrs)//2]}")
print(f"cited_by: max {max(r['cited_by'] for r in recs.values())}, "
      f"median {sorted(r['cited_by'] for r in recs.values())[len(recs)//2]}")
